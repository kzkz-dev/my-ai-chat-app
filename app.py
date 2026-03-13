from flask import Flask, request, Response, jsonify, session, stream_with_context
from groq import Groq
import os
import time
import json
import re
import sqlite3
import requests
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock
import pytz

APP_NAME = "Flux"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"
VERSION = "41.0.0"

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
GROQ_KEYS = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
MODEL_PRIMARY = os.getenv("MODEL_PRIMARY", "llama-3.3-70b-versatile")
MODEL_FAST = os.getenv("MODEL_FAST", "llama-3.1-8b-instant")
DB_PATH = os.getenv("DB_PATH", "flux_ai.db")
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "").lower()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "12"))
MAX_USER_TEXT = int(os.getenv("MAX_USER_TEXT", "5000"))
AUTO_APPLY_LOW_RISK = os.getenv("AUTO_APPLY_LOW_RISK", "false").lower() == "true"

SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True
TOTAL_MESSAGES_LOCK = Lock()
KEY_LOCK = Lock()

CURRENT_INFO_TRUSTED_DOMAINS = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "aljazeera.com",
    "pbs.org",
    "parliament.gov.bd",
    "cabinet.gov.bd",
    "pmo.gov.bd",
    "bangladesh.gov.bd",
]

BAD_SOURCE_DOMAINS = [
    "wikipedia.org",
    "m.wikipedia.org",
    "wikidata.org",
    "facebook.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "tiktok.com",
]

HOME_CARDS = [
    {"title": "Study Help", "prompt": "Explain this topic step by step for a student", "icon": "fas fa-graduation-cap"},
    {"title": "Build App", "prompt": "Create a modern mobile-friendly app in HTML", "icon": "fas fa-code"},
    {"title": "Smart Answer", "prompt": "Give me a smart clear answer", "icon": "fas fa-brain"},
    {"title": "Search Web", "prompt": "latest news today", "icon": "fas fa-globe"},
]

SUGGESTION_POOL = [
    {"icon": "fas fa-book", "text": "Explain photosynthesis simply"},
    {"icon": "fas fa-lightbulb", "text": "Business ideas for students"},
    {"icon": "fas fa-calculator", "text": "Solve: 50 * 3 + 20"},
    {"icon": "fas fa-language", "text": "Translate this into English"},
    {"icon": "fas fa-atom", "text": "Explain quantum physics simply"},
    {"icon": "fas fa-laptop-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-globe", "text": "latest tech news today"},
    {"icon": "fas fa-pen", "text": "Write a short paragraph in Bangla"},
]

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE

KEY_STATES = [{"key": key, "failures": 0, "cooldown_until": 0.0} for key in GROQ_KEYS]


def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key_name TEXT PRIMARY KEY,
            value_text TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_type TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patch_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patch_name TEXT NOT NULL,
            problem_summary TEXT NOT NULL,
            files_change TEXT NOT NULL,
            exact_change TEXT NOT NULL,
            expected_benefit TEXT NOT NULL,
            possible_risk TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            rollback_method TEXT NOT NULL,
            test_prompts TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            approved_at TEXT,
            rejected_at TEXT,
            applied_at TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_event(event_type, payload=None):
    try:
        conn = db_connect()
        conn.execute(
            "INSERT INTO analytics (event_type, payload, created_at) VALUES (?, ?, ?)",
            (event_type, json.dumps(payload or {}, ensure_ascii=False), datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def clear_analytics():
    try:
        conn = db_connect()
        conn.execute("DELETE FROM analytics")
        conn.execute("DELETE FROM feedback")
        conn.commit()
        conn.close()
    except Exception:
        pass


def clear_all_memory():
    try:
        conn = db_connect()
        conn.execute("DELETE FROM memory")
        conn.commit()
        conn.close()
    except Exception:
        pass


def save_memory(key_name, value_text):
    try:
        conn = db_connect()
        conn.execute(
            """
            INSERT INTO memory (key_name, value_text, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key_name) DO UPDATE SET
                value_text = excluded.value_text,
                updated_at = excluded.updated_at
            """,
            (key_name, value_text, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def load_memory(key_name, default_value=""):
    try:
        conn = db_connect()
        row = conn.execute("SELECT value_text FROM memory WHERE key_name = ?", (key_name,)).fetchone()
        conn.close()
        if row:
            return row["value_text"]
    except Exception:
        pass
    return default_value


def analytics_count():
    try:
        conn = db_connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM analytics").fetchone()
        conn.close()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


def feedback_count():
    try:
        conn = db_connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM feedback").fetchone()
        conn.close()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


def memory_count():
    try:
        conn = db_connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM memory").fetchone()
        conn.close()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


def sanitize_text(text, max_len=MAX_USER_TEXT):
    if text is None:
        return ""
    return str(text).replace("\x00", " ").strip()[:max_len]


def sanitize_messages(messages):
    if not isinstance(messages, list):
        return []
    safe = []
    for item in messages[-MAX_HISTORY_TURNS:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role", "")
        content = sanitize_text(item.get("content", ""))
        if role in {"user", "assistant", "system"} and content:
            safe.append({"role": role, "content": content})
    return safe


def detect_language(text):
    if re.search(r"[\u0980-\u09FF]", text or ""):
        return "bn"
    return "en"


def looks_like_math_expression(text):
    clean_text = (text or "").replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
    allowed_chars = set("0123456789.+-*/()xX÷^")
    if len(clean_text) < 3:
        return False
    if not set(clean_text).issubset(allowed_chars):
        return False
    return any(op in clean_text for op in ["+", "-", "*", "/", "x", "÷", "^"])


def safe_math_eval(text):
    try:
        clean_text = (text or "").replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
        if not looks_like_math_expression(clean_text):
            return None
        expression = clean_text.replace("x", "*").replace("X", "*").replace("÷", "/").replace("^", "**")
        if re.search(r"[^0-9\.\+\-\*/\(\)]", expression):
            return None
        result = eval(expression, {"__builtins__": None}, {})
        if isinstance(result, (int, float)):
            if float(result).is_integer():
                return f"{int(result):,}"
            return f"{float(result):,.4f}"
        return None
    except Exception:
        return None


def is_current_info_query(text):
    t = (text or "").lower()
    keywords = [
        "today", "latest", "news", "current", "price", "recent", "update", "weather",
        "crypto", "president", "prime minister", "pm", "ceo", "score", "live",
        "gold price", "bitcoin price", "stock price", "breaking", "headline",
        "আজ", "সর্বশেষ", "আজকের", "এখন", "দাম", "নিউজ", "আপডেট", "আবহাওয়া",
        "বর্তমান", "কে প্রধানমন্ত্রী", "কে প্রেসিডেন্ট", "who is the current"
    ]
    return any(k in t for k in keywords)


def is_office_holder_query(text):
    t = (text or "").lower()
    keywords = [
        "prime minister", "president", "chief minister", "ceo", "governor", "minister",
        "প্রধানমন্ত্রী", "প্রেসিডেন্ট", "রাষ্ট্রপতি", "মন্ত্রী", "কে এখন"
    ]
    return any(k in t for k in keywords)


def detect_task_type(text):
    t = (text or "").lower()
    if any(k in t for k in ["html", "css", "javascript", "js", "app", "game", "website", "calculator", "ui"]):
        return "code"
    if looks_like_math_expression(text):
        return "math"
    if is_current_info_query(text):
        return "current_info"
    if any(k in t for k in ["translate", "rewrite", "summarize", "summary", "explain", "simplify", "অনুবাদ", "সারাংশ", "সহজ", "ব্যাখ্যা"]):
        return "transform"
    return "chat"


def get_uptime():
    return str(timedelta(seconds=int(time.time() - SERVER_START_TIME)))


def is_bad_source(url):
    if not url:
        return True
    u = url.lower()
    return any(domain in u for domain in BAD_SOURCE_DOMAINS)


def is_trusted_current_source(url):
    u = (url or "").lower()
    return any(domain in u for domain in CURRENT_INFO_TRUSTED_DOMAINS)


def clean_search_results(results):
    cleaned = []
    for item in results:
        url = sanitize_text(item.get("url", ""), 500)
        if is_bad_source(url):
            continue
        title = sanitize_text(item.get("title", "Untitled"), 220)
        content = sanitize_text(item.get("content", ""), 900)
        score = float(item.get("score", 0) or 0)
        cleaned.append({
            "title": title,
            "url": url,
            "content": content,
            "score": score,
        })
    cleaned.sort(key=lambda x: x["score"], reverse=True)
    return cleaned[:8]


def filter_current_info_results(results):
    filtered = []
    seen_domains = set()

    for item in results:
        url = item.get("url", "")
        title_l = item.get("title", "").lower()
        content_l = item.get("content", "").lower()
        domain_key = url.split("/")[2] if "://" in url else url

        if not is_trusted_current_source(url):
            continue
        if domain_key in seen_domains:
            continue
        if "prime minister" not in title_l and "prime minister" not in content_l and "প্রধানমন্ত্রী" not in content_l:
            continue

        stale_patterns = [
            "sheikh hasina",
            "new cabinet under sheikh hasina",
            "2024 interim",
            "2024 protest",
        ]
        if any(p in content_l for p in stale_patterns) and ("current" in content_l or "বর্তমান" in content_l):
            continue

        seen_domains.add(domain_key)
        filtered.append(item)

    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered[:3]


def tavily_search_once(query, topic="general", max_results=8):
    if SEARCH_PROVIDER != "tavily" or not TAVILY_API_KEY:
        return []

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TAVILY_API_KEY}",
        }
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "topic": topic,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
        }
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not isinstance(results, list):
            return []
        return clean_search_results(results)
    except Exception as e:
        log_event("tavily_error", {"error": str(e), "query": query, "topic": topic})
        return []


def tavily_search(query, max_results=8):
    q = (query or "").lower()
    topic = "news" if "news" in q or "খবর" in q else "general"
    results = tavily_search_once(query, topic=topic, max_results=max_results)
    if results:
        return results
    fallback_topic = "general" if topic == "news" else "news"
    return tavily_search_once(query, topic=fallback_topic, max_results=max_results)


def format_sources_structured(results):
    return [{"title": item["title"], "url": item["url"]} for item in results[:3]]


def format_search_results_for_prompt(results):
    if not results:
        return ""
    lines = []
    for idx, item in enumerate(results[:3], start=1):
        lines.append(
            f"Source {idx}:\n"
            f"Title: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Summary: {item['content']}"
        )
    return "\n\n".join(lines)


def build_live_fallback(query):
    q = (query or "").lower()
    if detect_language(query) == "bn":
        if "news" in q or "খবর" in q:
            return "আমি এই মুহূর্তে নির্ভরযোগ্য live news source থেকে ফল পাইনি। একটু পরে আবার চেষ্টা করো।"
        return "আমি এই প্রশ্নের বর্তমান তথ্য trusted live source দিয়ে verify করতে পারিনি, তাই guess করব না।"
    if "news" in q:
        return "I couldn't fetch reliable live news results right now. Please try again in a moment."
    return "I couldn't verify this current information from trusted live sources, so I won't guess."


def update_preferences(user_name, latest_user):
    if user_name:
        save_memory("user_name", user_name)
    save_memory("preferred_language", detect_language(latest_user))


def build_system_prompt(user_name, preferences, latest_user, live_results_found):
    answer_length = preferences.get("answer_length", "balanced")
    tone = preferences.get("tone", "normal")
    response_mode = preferences.get("response_mode", "smart")
    preferred_language = load_memory("preferred_language", "auto")
    task_type = detect_task_type(latest_user)

    base = (
        f"You are {APP_NAME}, a smart and helpful AI assistant. "
        f"Your creator and owner is fixed as {OWNER_NAME} (Bangla: {OWNER_NAME_BN}). "
        f"Never contradict this identity. "
        f"Current user name: {user_name}. "
        f"Preferred language memory: {preferred_language}. "
        f"Answer length preference: {answer_length}. "
        f"Tone preference: {tone}. "
        f"Primary mode: {response_mode}."
    )

    rules = """
Core rules:
1. Be accurate, helpful, and clear.
2. Keep answers mobile-friendly and clean.
3. Prefer short paragraphs.
4. Never invent facts, current news, prices, office-holders, or live information.
5. If current information is requested and trusted live results are unavailable, clearly say you cannot verify it.
6. If live results are provided, answer only from those results.
7. Give a clean answer first, then sources separately.
8. Do not dump raw URLs inside the main answer.
9. If the question asks for a current office-holder, prefer trusted recent sources and ignore stale pages.
10. Use strict trusted-source filtering only for current office-holder or role questions.
11. For general latest news queries, summarize from recent reliable live sources.
12. If asked who owns or created you, answer consistently: KAWCHUR.
13. For study tasks, explain step by step.
14. For code tasks, be practical and stable.
15. Avoid clutter and repetition.
""".strip()

    task_rule = "Task type: general chat."
    if task_type == "math":
        task_rule = "Task type: math. Give the exact answer directly."
    elif task_type == "current_info":
        task_rule = "Task type: current info. Use only provided live results."
    elif task_type == "code":
        task_rule = (
            "Task type: code. If the user asks to build an app or UI, "
            "return one full HTML file inside a single ```html code block."
        )

    return "\n\n".join([base, rules, task_rule])


def build_messages_for_model(messages, user_name, preferences):
    latest_user = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            latest_user = msg["content"]
            break

    update_preferences(user_name, latest_user)

    search_results = []
    response_mode = preferences.get("response_mode", "smart")
    task_type = detect_task_type(latest_user)

    if response_mode == "search" or task_type == "current_info":
        search_results = tavily_search(latest_user, max_results=8)
        if task_type == "current_info" and is_office_holder_query(latest_user):
            search_results = filter_current_info_results(search_results)
        else:
            search_results = search_results[:3]

    final_messages = [
        {"role": "system", "content": build_system_prompt(user_name, preferences, latest_user, bool(search_results))},
        {"role": "system", "content": f"Fixed identity facts: app name is {APP_NAME}. Owner and creator is {OWNER_NAME}."},
    ]

    math_result = safe_math_eval(latest_user)
    if math_result is not None:
        final_messages.append({
            "role": "system",
            "content": f"MATH TOOL RESULT: The exact answer is {math_result}. Use it correctly."
        })

    if search_results:
        final_messages.append({
            "role": "system",
            "content": "Verified trusted live results are below. Answer from these only.\n\n" + format_search_results_for_prompt(search_results)
        })

    final_messages.extend(messages)
    return final_messages, search_results


def pick_model(messages):
    latest_user = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            latest_user = msg["content"]
            break
    if detect_task_type(latest_user) == "math":
        return MODEL_FAST
    if len(latest_user) < 120:
        return MODEL_FAST
    return MODEL_PRIMARY


def mark_key_failure(api_key):
    with KEY_LOCK:
        for item in KEY_STATES:
            if item["key"] == api_key:
                item["failures"] += 1
                cooldown = min(60, 5 * item["failures"])
                item["cooldown_until"] = time.time() + cooldown
                break


def mark_key_success(api_key):
    with KEY_LOCK:
        for item in KEY_STATES:
            if item["key"] == api_key:
                item["failures"] = max(0, item["failures"] - 1)
                item["cooldown_until"] = 0.0
                break


def get_available_key():
    if not KEY_STATES:
        return None
    now = time.time()
    with KEY_LOCK:
        available = [item for item in KEY_STATES if item["cooldown_until"] <= now]
        if not available:
            available = KEY_STATES
        best = min(available, key=lambda x: x["failures"])
        return best["key"]


def generate_groq_stream(messages, user_name, preferences):
    latest_user = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            latest_user = msg["content"]
            break

    task_type = detect_task_type(latest_user)
    if task_type == "current_info":
        live_results = tavily_search(latest_user, max_results=8)
        if is_office_holder_query(latest_user):
            live_results = filter_current_info_results(live_results)
        else:
            live_results = live_results[:3]
        if not live_results:
            yield json.dumps({"answer": build_live_fallback(latest_user), "sources": []}, ensure_ascii=False)
            return

    final_messages, search_results = build_messages_for_model(messages, user_name, preferences)
    model_name = pick_model(messages)

    if not GROQ_KEYS:
        yield json.dumps({"answer": "Config error: No Groq API keys found.", "sources": []}, ensure_ascii=False)
        return

    attempts = 0
    max_retries = max(1, len(GROQ_KEYS))

    while attempts < max_retries:
        api_key = get_available_key()
        if not api_key:
            yield json.dumps({"answer": "System busy: No API key available right now.", "sources": []}, ensure_ascii=False)
            return

        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                model=model_name,
                messages=final_messages,
                stream=True,
                temperature=0.12 if search_results else 0.5,
                max_tokens=2048,
            )

            collected = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    collected += chunk.choices[0].delta.content

            mark_key_success(api_key)
            yield json.dumps({
                "answer": collected.strip(),
                "sources": format_sources_structured(search_results)
            }, ensure_ascii=False)
            return

        except Exception as e:
            mark_key_failure(api_key)
            log_event("groq_error", {"error": str(e), "model": model_name})
            attempts += 1
            time.sleep(0.7)

    yield json.dumps({"answer": "System busy. Please try again in a moment.", "sources": []}, ensure_ascii=False)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper


def build_patch_suggestion(problem_text):
    text = (problem_text or "").lower()

    if "theme" in text:
        return {
            "patch_name": "Theme State Refresh Fix",
            "problem_summary": "Visual theme change immediately reflects না।",
            "files_change": ["app.py"],
            "exact_change": "theme state update + active button refresh + surface color refresh",
            "expected_benefit": "theme click করার সাথে সাথে UI update হবে",
            "possible_risk": "low visual regression",
            "risk_level": "low",
            "rollback_method": "theme-related JS revert",
            "test_prompts": ["Neon theme", "Matrix theme", "Galaxy theme"],
        }

    if "prime minister" in text or "প্রধানমন্ত্রী" in text or "current info" in text:
        return {
            "patch_name": "Trusted Current Info Filter",
            "problem_summary": "Current office-holder query তে stale source mix হচ্ছে।",
            "files_change": ["app.py"],
            "exact_change": "strict trusted-domain filter for office-holder queries only",
            "expected_benefit": "current role question-এ ভুল কমবে",
            "possible_risk": "fallback কিছু query-তে বেশি আসতে পারে",
            "risk_level": "medium",
            "rollback_method": "current-info filter block revert",
            "test_prompts": [
                "who is the current prime minister of bangladesh",
                "বাংলাদেশের বর্তমান প্রধানমন্ত্রীর নাম কি",
                "latest news today"
            ],
        }

    if "+" in problem_text or "sheet" in text:
        return {
            "patch_name": "Tools Sheet Toggle Fix",
            "problem_summary": "Plus tools sheet open হওয়ার পর close হচ্ছে না।",
            "files_change": ["app.py"],
            "exact_change": "toggle sheet + overlay close logic",
            "expected_benefit": "same button and outside tap দিয়ে close হবে",
            "possible_risk": "low",
            "risk_level": "low",
            "rollback_method": "sheet toggle JS revert",
            "test_prompts": ["tap plus", "tap plus again", "tap outside overlay"],
        }

    return {
        "patch_name": "General Stability Patch",
        "problem_summary": problem_text or "General issue detected",
        "files_change": ["app.py"],
        "exact_change": "reviewed low-risk logic cleanup",
        "expected_benefit": "better stability",
        "possible_risk": "unknown minor regression",
        "risk_level": "medium",
        "rollback_method": "restore previous stable file",
        "test_prompts": ["latest news today", "2+2", "create html login page"],
    }


def create_patch_queue_item(suggestion, notes=""):
    conn = db_connect()
    conn.execute(
        """
        INSERT INTO patch_queue (
            patch_name, problem_summary, files_change, exact_change,
            expected_benefit, possible_risk, risk_level, rollback_method,
            test_prompts, status, created_at, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            suggestion["patch_name"],
            suggestion["problem_summary"],
            json.dumps(suggestion["files_change"], ensure_ascii=False),
            suggestion["exact_change"],
            suggestion["expected_benefit"],
            suggestion["possible_risk"],
            suggestion["risk_level"],
            suggestion["rollback_method"],
            json.dumps(suggestion["test_prompts"], ensure_ascii=False),
            "pending",
            datetime.utcnow().isoformat(),
            notes,
        )
    )
    conn.commit()
    row = conn.execute("SELECT * FROM patch_queue ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def list_patch_queue(status=None):
    conn = db_connect()
    if status:
        rows = conn.execute("SELECT * FROM patch_queue WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM patch_queue ORDER BY id DESC").fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["files_change"] = json.loads(item["files_change"])
        item["test_prompts"] = json.loads(item["test_prompts"])
        result.append(item)
    return result


def get_patch_item(patch_id):
    conn = db_connect()
    row = conn.execute("SELECT * FROM patch_queue WHERE id = ?", (patch_id,)).fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    item["files_change"] = json.loads(item["files_change"])
    item["test_prompts"] = json.loads(item["test_prompts"])
    return item


def update_patch_status(patch_id, status):
    conn = db_connect()
    time_field = {"approved": "approved_at", "rejected": "rejected_at", "applied": "applied_at"}.get(status)

    if time_field:
        conn.execute(
            f"UPDATE patch_queue SET status = ?, {time_field} = ? WHERE id = ?",
            (status, datetime.utcnow().isoformat(), patch_id)
        )
    else:
        conn.execute("UPDATE patch_queue SET status = ? WHERE id = ?", (status, patch_id))
    conn.commit()
    conn.close()


def apply_low_risk_patch(item):
    if item["risk_level"] != "low":
        return {"ok": False, "message": "Only low-risk patch auto apply is allowed."}

    save_memory(f"applied_patch_{item['id']}", item["patch_name"])
    update_patch_status(item["id"], "applied")
    return {"ok": True, "message": "Low-risk patch marked as applied to stable memory layer."}


@app.route("/")
def home():
    cards_json = json.dumps(HOME_CARDS, ensure_ascii=False)
    suggestions_json = json.dumps(SUGGESTION_POOL, ensure_ascii=False)

    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>__APP_NAME__</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{
  --bg:#050816;--bg2:#0a1130;--text:#eef2ff;--muted:#9aa8c7;--accent:#8b5cf6;--accent2:#60a5fa;--border:rgba(255,255,255,.08);--danger:#ef4444;--success:#22c55e;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:radial-gradient(circle at top,var(--bg2) 0%,var(--bg) 58%,#02040c 100%);color:var(--text);font-family:'Outfit','Noto Sans Bengali',sans-serif}
.app{width:100%;height:100%;position:relative;overflow:hidden;background:radial-gradient(circle at top,rgba(139,92,246,.1) 0%,transparent 45%)}
#bg-canvas{position:fixed;inset:0;width:100%;height:100%;opacity:.3;pointer-events:none;z-index:0}
.shell{position:relative;z-index:1;width:100%;height:100%;display:flex;flex-direction:column}
.topbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:1px solid rgba(255,255,255,.05);background:rgba(5,8,22,.54);backdrop-filter:blur(12px)}
.top-left{display:flex;align-items:center;gap:10px}
.top-title{font-size:22px;font-weight:800;background:linear-gradient(135deg,#fff 0%,#d7ccff 55%,#b7d9ff 100%);-webkit-background-clip:text;color:transparent}
.top-orb{width:46px;height:46px;border-radius:16px;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,rgba(22,22,56,.98),rgba(7,7,28,.98));color:var(--accent);box-shadow:0 0 18px rgba(139,92,246,.22);animation:topOrbPulse 3.2s infinite ease-in-out;cursor:pointer}
.chat-box{flex:1;overflow-y:auto;padding:16px 12px 108px}
.welcome{max-width:900px;margin:0 auto;text-align:center}
.hero-orb{width:90px;height:90px;border-radius:24px;display:flex;align-items:center;justify-content:center;margin:20px auto;background:linear-gradient(180deg,rgba(22,22,56,.95),rgba(7,7,28,.95));box-shadow:0 0 42px rgba(139,92,246,.22);color:var(--accent);font-size:34px}
.cards-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-top:16px}
.home-card{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:20px;padding:18px;display:flex;gap:14px;align-items:center;cursor:pointer}
.home-card-icon{width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:rgba(139,92,246,.12);color:var(--accent)}
.chips-row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:16px}
.quick-chip{border:1px solid var(--border);background:rgba(255,255,255,.03);color:var(--text);border-radius:999px;padding:10px 14px;font-size:13px;display:inline-flex;align-items:center;gap:8px;cursor:pointer}
.message{max-width:900px;margin:0 auto 18px;display:flex;gap:10px}
.message.user{flex-direction:row-reverse}
.avatar{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.avatar.bot{background:linear-gradient(135deg,#a855f7 0%,#60a5fa 100%)}
.avatar.user{background:rgba(255,255,255,.08)}
.bubble-wrap{min-width:0;flex:1}
.message.user .bubble-wrap{display:flex;flex-direction:column;align-items:flex-end}
.name{font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:700}
.message.user .name{display:none}
.bubble{width:100%;word-wrap:break-word;overflow-wrap:anywhere;line-height:1.7;font-size:16px}
.message.user .bubble{width:auto;max-width:min(82vw,560px);padding:14px 16px;border-radius:18px;background:linear-gradient(135deg,#312e81 0%,#2563eb 100%);color:#fff}
.message.bot .bubble{padding:14px 16px;border-radius:18px;background:linear-gradient(180deg,rgba(139,92,246,.06),rgba(96,165,250,.05));border:1px solid rgba(139,92,246,.22)}
.source-cards{display:grid;gap:10px;margin-top:12px}
.source-card{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:14px;padding:12px 14px}
.source-card a{color:#dbe4ff;text-decoration:none;font-weight:600;word-break:break-word}
.source-label{color:var(--muted);font-size:12px;margin-bottom:6px}
.input-area{position:fixed;left:0;right:0;bottom:0;padding:12px;background:linear-gradient(to top,rgba(2,4,12,1) 0%,rgba(2,4,12,.2) 100%)}
.input-wrap{max-width:900px;margin:0 auto}
.input-box{display:flex;gap:10px;align-items:flex-end;background:rgba(13,19,38,.96);border:1px solid var(--border);border-radius:24px;padding:10px 10px 10px 12px}
textarea{flex:1;min-width:0;background:transparent;border:none;outline:none;color:var(--text);font-size:16px;resize:none;max-height:180px;font-family:inherit;line-height:1.5;padding:9px 2px}
.send-btn{width:44px;height:44px;border:none;border-radius:50%;background:var(--text);color:#111827;cursor:pointer}
.typing{max-width:900px;margin:0 auto 18px;color:var(--muted)}
.typing-card{display:flex;align-items:center;gap:12px;padding:14px 16px;border-radius:18px;border:1px solid var(--border);background:rgba(255,255,255,.03);width:fit-content}
.voice-wave{display:flex;gap:4px;align-items:center;height:24px}
.voice-wave span{width:4px;border-radius:999px;background:linear-gradient(180deg,var(--accent),var(--accent2));animation:wave 1.1s infinite ease-in-out}
.voice-wave span:nth-child(1){height:10px}.voice-wave span:nth-child(2){height:18px}.voice-wave span:nth-child(3){height:24px}.voice-wave span:nth-child(4){height:16px}.voice-wave span:nth-child(5){height:12px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.72);display:none;align-items:center;justify-content:center;z-index:200;padding:16px}
.modal-card{width:100%;max-width:460px;background:linear-gradient(180deg,rgba(18,27,52,.98),rgba(8,12,28,.98));border:1px solid var(--border);border-radius:22px;padding:22px;position:relative;box-shadow:0 20px 55px rgba(0,0,0,.36);max-height:90vh;overflow:auto}
.close-small{position:absolute;top:12px;right:12px;background:transparent;border:none;color:var(--muted);font-size:20px;cursor:pointer}
.modal-card input,.modal-card textarea{width:100%;margin:12px 0;padding:12px;border-radius:12px;border:1px solid var(--border);background:rgba(255,255,255,.05);color:var(--text);outline:none}
.modal-row{display:flex;gap:10px;margin-top:12px}
.modal-row button{flex:1;border:none;border-radius:14px;padding:13px;cursor:pointer;font-size:15px}
.btn-cancel{background:rgba(255,255,255,.08);color:#fff}
.btn-confirm{background:var(--success);color:#000}
.btn-danger{background:var(--danger);color:#fff}
.stats-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}
.stat-card{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:16px;padding:12px}
.stat-value{font-size:22px;font-weight:800;margin-bottom:4px}
.stat-label{color:var(--muted);font-size:12px}
.patch-item{border:1px solid var(--border);background:rgba(255,255,255,.03);border-radius:14px;padding:12px;margin-top:10px}
.patch-title{font-weight:700;margin-bottom:6px}
.patch-meta{font-size:12px;color:var(--muted);margin-bottom:8px}
.patch-tests{font-size:13px;color:#dbe4ff}
@keyframes wave{0%,100%{transform:scaleY(.55);opacity:.6}50%{transform:scaleY(1);opacity:1}}
@keyframes topOrbPulse{0%{transform:scale(1)}50%{transform:scale(1.08)}100%{transform:scale(1)}}
@media (max-width:520px){.stats-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="app shell">
  <div class="topbar">
    <div class="top-left">
      <div class="top-title">__APP_NAME__</div>
    </div>
    <div class="top-orb" onclick="openAdminModal()"><i class="fas fa-bolt"></i></div>
  </div>

  <div id="chat-box" class="chat-box">
    <div id="welcome" class="welcome">
      <div class="hero-orb"><i class="fas fa-bolt"></i></div>
      <h1>How can __APP_NAME__ help today?</h1>
      <div id="home-cards" class="cards-grid"></div>
      <div id="quick-chips" class="chips-row"></div>
    </div>
  </div>

  <div class="input-area">
    <div class="input-wrap">
      <div class="input-box">
        <textarea id="msg" rows="1" placeholder="Ask __APP_NAME__..."></textarea>
        <button id="send-btn" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
      </div>
    </div>
  </div>
</div>

<div id="admin-modal" class="modal-overlay">
  <div class="modal-card">
    <button class="close-small" onclick="closeAdminModal()"><i class="fas fa-times"></i></button>
    <div style="font-size:28px;font-weight:800;margin-bottom:6px;">Admin Access</div>
    <div style="color:var(--muted);margin-bottom:10px;">Enter authorization code</div>
    <input type="password" id="admin-pass" placeholder="Password">
    <div id="admin-error" style="display:none;color:#fca5a5;margin-bottom:10px;">Invalid password</div>
    <div class="modal-row">
      <button class="btn-cancel" onclick="closeAdminModal()">Cancel</button>
      <button class="btn-confirm" onclick="verifyAdmin()">Login</button>
    </div>
  </div>
</div>

<div id="admin-panel-modal" class="modal-overlay">
  <div class="modal-card">
    <button class="close-small" onclick="closeAdminPanel()"><i class="fas fa-times"></i></button>
    <div style="font-size:30px;font-weight:800;margin-bottom:6px;">Admin Panel</div>
    <div style="color:var(--muted);margin-bottom:8px;">System overview + AutoPatch</div>

    <div class="stats-grid">
      <div class="stat-card"><div id="stat-messages" class="stat-value">0</div><div class="stat-label">Total Messages</div></div>
      <div class="stat-card"><div id="stat-uptime" class="stat-value">0</div><div class="stat-label">Uptime</div></div>
      <div class="stat-card"><div id="stat-system" class="stat-value">ON</div><div class="stat-label">System</div></div>
      <div class="stat-card"><div id="stat-keys" class="stat-value">0</div><div class="stat-label">Loaded Keys</div></div>
      <div class="stat-card"><div id="stat-pending" class="stat-value">0</div><div class="stat-label">Pending Patches</div></div>
      <div class="stat-card"><div id="stat-search" class="stat-value">OFF</div><div class="stat-label">Web Search</div></div>
    </div>

    <div style="margin-top:18px;font-size:18px;font-weight:700;">Create AutoPatch Suggestion</div>
    <textarea id="patch-problem" rows="4" placeholder="Describe the problem..."></textarea>
    <textarea id="patch-notes" rows="2" placeholder="Optional notes..."></textarea>
    <div class="modal-row">
      <button class="btn-confirm" onclick="createPatchSuggestion()">Create Suggestion</button>
    </div>

    <div style="margin-top:18px;font-size:18px;font-weight:700;">Patch Queue</div>
    <div id="patch-list"></div>

    <div class="modal-row">
      <button class="btn-danger" onclick="toggleSystemAdmin()">Toggle System</button>
      <button class="btn-cancel" onclick="closeAdminPanel()">Close</button>
    </div>
  </div>
</div>

<script>
marked.setOptions({breaks:true,gfm:true});
const HOME_CARDS = __HOME_CARDS__;
const SUGGESTION_POOL = __SUGGESTIONS__;
let chats = JSON.parse(localStorage.getItem("flux_v41_history") || "[]");
let currentChatId = null;
let userName = localStorage.getItem("flux_user_name_fixed") || "";
let awaitingName = false;
let responseMode = localStorage.getItem("flux_response_mode") || "smart";
const chatBox = document.getElementById("chat-box");
const welcome = document.getElementById("welcome");
const msgInput = document.getElementById("msg");

function shuffleArray(arr){
  const a=[...arr];
  for(let i=a.length-1;i>0;i--){
    const j=Math.floor(Math.random()*(i+1));
    [a[i],a[j]]=[a[j],a[i]];
  }
  return a;
}

function resizeInput(el){
  el.style.height="auto";
  el.style.height=Math.min(el.scrollHeight,180)+"px";
}

function renderHomeCards(){
  const box=document.getElementById("home-cards");
  box.innerHTML="";
  HOME_CARDS.forEach(card=>{
    const el=document.createElement("div");
    el.className="home-card";
    el.innerHTML='<div class="home-card-icon"><i class="'+card.icon+'"></i></div><div><div style="font-size:18px;font-weight:700">'+card.title+'</div></div>';
    el.onclick=()=>{
      msgInput.value=card.prompt;
      resizeInput(msgInput);
      sendMessage();
    };
    box.appendChild(el);
  });
}

function renderQuickChips(){
  const box=document.getElementById("quick-chips");
  box.innerHTML="";
  shuffleArray(SUGGESTION_POOL).slice(0,4).forEach(item=>{
    const btn=document.createElement("button");
    btn.className="quick-chip";
    btn.innerHTML='<i class="'+item.icon+'"></i><span>'+item.text+'</span>';
    btn.onclick=()=>{
      msgInput.value=item.text;
      resizeInput(msgInput);
      sendMessage();
    };
    box.appendChild(btn);
  });
}

setInterval(()=>{ if(welcome.style.display!=="none") renderQuickChips(); }, 10000);

function createMessage(role,text,sources=[]){
  return {id:Date.now()+Math.random().toString(16).slice(2),role,text,sources,created_at:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})};
}

function appendBubble(msg){
  welcome.style.display="none";
  const isUser=msg.role==="user";
  const wrapper=document.createElement("div");
  wrapper.className=isUser?"message user":"message bot";
  const avatar=document.createElement("div");
  avatar.className=isUser?"avatar user":"avatar bot";
  avatar.innerHTML=isUser?'<i class="fas fa-user"></i>':'<i class="fas fa-bolt"></i>';

  const bubbleWrap=document.createElement("div");
  bubbleWrap.className="bubble-wrap";
  const name=document.createElement("div");
  name.className="name";
  name.textContent=isUser?"You":"__APP_NAME__";

  const bubble=document.createElement("div");
  bubble.className="bubble";
  bubble.innerHTML=marked.parse(msg.text || "");

  if(!isUser && msg.sources && msg.sources.length){
    const src=document.createElement("div");
    src.className="source-cards";
    msg.sources.forEach((s,i)=>{
      const card=document.createElement("div");
      card.className="source-card";
      card.innerHTML='<div class="source-label">Source '+(i+1)+'</div><a href="'+s.url+'" target="_blank" rel="noopener noreferrer">'+s.title+'</a>';
      src.appendChild(card);
    });
    bubble.appendChild(src);
  }

  bubbleWrap.appendChild(name);
  bubbleWrap.appendChild(bubble);
  wrapper.appendChild(avatar);
  wrapper.appendChild(bubbleWrap);
  chatBox.appendChild(wrapper);
  chatBox.scrollTop=chatBox.scrollHeight;
}

function showTyping(label){
  const div=document.createElement("div");
  div.id="typing";
  div.className="typing";
  div.innerHTML='<div class="typing-card"><div class="voice-wave"><span></span><span></span><span></span><span></span><span></span></div><div>'+label+'</div></div>';
  chatBox.appendChild(div);
  chatBox.scrollTop=chatBox.scrollHeight;
}

function removeTyping(){
  document.getElementById("typing")?.remove();
}

async function sendMessage(){
  const text=msgInput.value.trim();
  if(!text) return;

  if(!currentChatId){
    currentChatId=Date.now();
    chats.unshift({id:currentChatId,title:"New Conversation",messages:[]});
  }
  const chat=chats.find(c=>c.id===currentChatId);
  const userMsg=createMessage("user",text);
  chat.messages.push(userMsg);
  if(chat.messages.length===1) chat.title=text.substring(0,28);

  localStorage.setItem("flux_v41_history", JSON.stringify(chats));
  msgInput.value="";
  resizeInput(msgInput);
  appendBubble(userMsg);

  if(!userName && !awaitingName){
    awaitingName=true;
    const botMsg=createMessage("assistant","Hello! I am __APP_NAME__. What should I call you?");
    chat.messages.push(botMsg);
    localStorage.setItem("flux_v41_history", JSON.stringify(chats));
    setTimeout(()=>appendBubble(botMsg),300);
    return;
  }

  if(awaitingName){
    userName=text;
    localStorage.setItem("flux_user_name_fixed", userName);
    awaitingName=false;
    const botMsg=createMessage("assistant","Nice to meet you, "+userName+"! How can I help you today?");
    chat.messages.push(botMsg);
    localStorage.setItem("flux_v41_history", JSON.stringify(chats));
    setTimeout(()=>appendBubble(botMsg),300);
    return;
  }

  showTyping("__APP_NAME__ is thinking...");

  const context = chat.messages.slice(-12).map(m=>({
    role: m.role === "assistant" ? "assistant" : "user",
    content: m.text
  }));

  try{
    const res=await fetch("/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        messages:context,
        user_name:userName || "User",
        preferences:{response_mode:responseMode,answer_length:"balanced",tone:"normal",bangla_first:"false",memory_enabled:"true"}
      })
    });

    removeTyping();

    if(!res.ok){
      const txt=await res.text();
      throw new Error(txt || "Request failed");
    }

    const raw=await res.text();
    let parsed={answer:"System error.",sources:[]};
    try{ parsed=JSON.parse(raw); }catch(e){}

    const botMsg=createMessage("assistant",parsed.answer || "System error.", parsed.sources || []);
    chat.messages.push(botMsg);
    localStorage.setItem("flux_v41_history", JSON.stringify(chats));
    appendBubble(botMsg);
  }catch(e){
    removeTyping();
    const errMsg=createMessage("assistant","System connection error. Please try again.");
    chat.messages.push(errMsg);
    localStorage.setItem("flux_v41_history", JSON.stringify(chats));
    appendBubble(errMsg);
  }
}

function openAdminModal(){
  document.getElementById("admin-error").style.display="none";
  document.getElementById("admin-pass").value="";
  document.getElementById("admin-modal").style.display="flex";
}
function closeAdminModal(){ document.getElementById("admin-modal").style.display="none"; }
function openAdminPanel(){ document.getElementById("admin-panel-modal").style.display="flex"; }
function closeAdminPanel(){ document.getElementById("admin-panel-modal").style.display="none"; }

async function verifyAdmin(){
  const pass=document.getElementById("admin-pass").value;
  try{
    const res=await fetch("/admin/login",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({password:pass})
    });
    if(!res.ok) throw new Error("Invalid");
    closeAdminModal();
    await refreshAdminPanel();
    openAdminPanel();
  }catch(e){
    document.getElementById("admin-error").style.display="block";
  }
}

async function refreshAdminPanel(){
  try{
    const statsRes = await fetch("/admin/stats");
    const stats = await statsRes.json();
    document.getElementById("stat-messages").textContent = stats.total_messages;
    document.getElementById("stat-uptime").textContent = stats.uptime;
    document.getElementById("stat-system").textContent = stats.active ? "ON" : "OFF";
    document.getElementById("stat-keys").textContent = stats.loaded_keys;
    document.getElementById("stat-pending").textContent = stats.pending_patches;
    document.getElementById("stat-search").textContent = stats.tavily_enabled ? "ON" : "OFF";

    const listRes = await fetch("/autopatch/list");
    const listData = await listRes.json();
    renderPatchList(listData.patches || []);
  }catch(e){
    alert("Failed to load admin panel");
  }
}

function renderPatchList(patches){
  const box=document.getElementById("patch-list");
  box.innerHTML="";
  if(!patches.length){
    box.innerHTML='<div style="color:var(--muted);margin-top:10px;">No patches yet.</div>';
    return;
  }

  patches.forEach(p=>{
    const el=document.createElement("div");
    el.className="patch-item";
    const tests=(p.test_prompts || []).map(t=>'<div>• '+t+'</div>').join('');
    el.innerHTML=
      '<div class="patch-title">'+p.patch_name+'</div>'+
      '<div class="patch-meta">Risk: '+p.risk_level+' | Status: '+p.status+'</div>'+
      '<div><strong>Problem:</strong> '+p.problem_summary+'</div>'+
      '<div style="margin-top:6px;"><strong>Change:</strong> '+p.exact_change+'</div>'+
      '<div style="margin-top:6px;"><strong>Benefit:</strong> '+p.expected_benefit+'</div>'+
      '<div style="margin-top:6px;"><strong>Risk:</strong> '+p.possible_risk+'</div>'+
      '<div style="margin-top:6px;"><strong>Rollback:</strong> '+p.rollback_method+'</div>'+
      '<div class="patch-tests" style="margin-top:8px;"><strong>Tests:</strong>'+tests+'</div>';

    const row=document.createElement("div");
    row.className="modal-row";
    row.style.marginTop="10px";

    const approve=document.createElement("button");
    approve.className="btn-confirm";
    approve.textContent="Approve";
    approve.onclick=()=>approvePatch(p.id);

    const reject=document.createElement("button");
    reject.className="btn-danger";
    reject.textContent="Reject";
    reject.onclick=()=>rejectPatch(p.id);

    const apply=document.createElement("button");
    apply.className="btn-cancel";
    apply.textContent="Apply";
    apply.onclick=()=>applyPatch(p.id);

    row.appendChild(approve);
    row.appendChild(reject);
    row.appendChild(apply);
    el.appendChild(row);
    box.appendChild(el);
  });
}

async function createPatchSuggestion(){
  const problem=document.getElementById("patch-problem").value.trim();
  const notes=document.getElementById("patch-notes").value.trim();
  if(!problem){
    alert("Problem লিখো");
    return;
  }
  try{
    const res=await fetch("/autopatch/suggest",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({problem,notes})
    });
    const data=await res.json();
    if(!res.ok || !data.ok) throw new Error(data.error || "Failed");
    document.getElementById("patch-problem").value="";
    document.getElementById("patch-notes").value="";
    await refreshAdminPanel();
  }catch(e){
    alert("Patch suggestion failed");
  }
}

async function approvePatch(id){
  try{
    const res=await fetch("/autopatch/approve/"+id,{method:"POST"});
    const data=await res.json();
    if(!res.ok || !data.ok) throw new Error("Failed");
    await refreshAdminPanel();
  }catch(e){
    alert("Approve failed");
  }
}

async function rejectPatch(id){
  try{
    const res=await fetch("/autopatch/reject/"+id,{method:"POST"});
    const data=await res.json();
    if(!res.ok || !data.ok) throw new Error("Failed");
    await refreshAdminPanel();
  }catch(e){
    alert("Reject failed");
  }
}

async function applyPatch(id){
  try{
    const res=await fetch("/autopatch/apply/"+id,{method:"POST"});
    const data=await res.json();
    if(!res.ok || !data.ok) throw new Error(data.message || "Failed");
    alert(data.message || "Applied");
    await refreshAdminPanel();
  }catch(e){
    alert("Apply failed");
  }
}

async function toggleSystemAdmin(){
  try{
    const res=await fetch("/admin/toggle_system",{method:"POST"});
    if(!res.ok) throw new Error("Failed");
    await refreshAdminPanel();
  }catch(e){
    alert("Toggle failed");
  }
}

msgInput.addEventListener("keypress", function(e){
  if(e.key==="Enter" && !e.shiftKey){
    e.preventDefault();
    sendMessage();
  }
});
msgInput.addEventListener("input", function(){ resizeInput(this); });

(function initBg(){
  const canvas=document.getElementById("bg-canvas");
  const ctx=canvas.getContext("2d");
  let particles=[];
  function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
  function makeParticles(){
    particles=[];
    const count=Math.max(14, Math.floor(window.innerWidth/90));
    for(let i=0;i<count;i++){
      particles.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()-0.5)*0.08,vy:(Math.random()-0.5)*0.08,r:Math.random()*1.8+0.5});
    }
  }
  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    for(let i=0;i<particles.length;i++){
      const p=particles[i];
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0 || p.x>canvas.width) p.vx*=-1;
      if(p.y<0 || p.y>canvas.height) p.vy*=-1;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle="rgba(96,165,250,0.70)";
      ctx.fill();
      for(let j=i+1;j<particles.length;j++){
        const q=particles[j];
        const dx=p.x-q.x, dy=p.y-q.y, d=Math.sqrt(dx*dx+dy*dy);
        if(d<90){
          ctx.beginPath();
          ctx.moveTo(p.x,p.y);
          ctx.lineTo(q.x,q.y);
          ctx.strokeStyle="rgba(59,130,246,"+((1-d/90)*0.12).toFixed(3)+")";
          ctx.lineWidth=1;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  window.addEventListener("resize", ()=>{ resize(); makeParticles(); });
  resize(); makeParticles(); draw();
})();

renderHomeCards();
renderQuickChips();
</script>
</body>
</html>
"""
    html = html.replace("__APP_NAME__", APP_NAME)
    html = html.replace("__OWNER_NAME__", OWNER_NAME)
    html = html.replace("__VERSION__", VERSION)
    html = html.replace("__HOME_CARDS__", cards_json)
    html = html.replace("__SUGGESTIONS__", suggestions_json)
    return html


@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES, SYSTEM_ACTIVE

    if not SYSTEM_ACTIVE:
        return Response(
            json.dumps({"answer": "System is currently under maintenance.", "sources": []}, ensure_ascii=False),
            status=503,
            mimetype="application/json"
        )

    data = request.get_json(silent=True) or {}
    messages = sanitize_messages(data.get("messages", []))
    user_name = sanitize_text(data.get("user_name", "User"), 80) or "User"
    preferences = data.get("preferences", {}) if isinstance(data.get("preferences", {}), dict) else {}

    if not messages:
        return Response(
            json.dumps({"answer": "No valid messages received.", "sources": []}, ensure_ascii=False),
            status=400,
            mimetype="application/json"
        )

    with TOTAL_MESSAGES_LOCK:
        TOTAL_MESSAGES += 1

    @stream_with_context
    def generate():
        for chunk in generate_groq_stream(messages, user_name, preferences):
            yield chunk

    return Response(generate(), mimetype="application/json")


@app.route("/admin/login", methods=["POST"])
def admin_login():
    if not ADMIN_PASSWORD:
        return jsonify({"ok": False, "error": "Admin password not configured"}), 503

    data = request.get_json(silent=True) or {}
    password = sanitize_text(data.get("password", ""), 128)

    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        log_event("admin_login_success")
        return jsonify({"ok": True})

    log_event("admin_login_failed")
    return jsonify({"ok": False, "error": "Invalid password"}), 401


@app.route("/admin/stats")
@admin_required
def admin_stats():
    return jsonify({
        "uptime": get_uptime(),
        "total_messages": TOTAL_MESSAGES,
        "active": SYSTEM_ACTIVE,
        "version": VERSION,
        "analytics_count": analytics_count(),
        "feedback_count": feedback_count(),
        "memory_count": memory_count(),
        "loaded_keys": len(GROQ_KEYS),
        "search_provider": SEARCH_PROVIDER,
        "tavily_enabled": bool(TAVILY_API_KEY),
        "pending_patches": len(list_patch_queue("pending")),
    })


@app.route("/admin/toggle_system", methods=["POST"])
@admin_required
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    log_event("toggle_system", {"active": SYSTEM_ACTIVE})
    return jsonify({"ok": True, "active": SYSTEM_ACTIVE})


@app.route("/admin/reset_memory", methods=["POST"])
@admin_required
def reset_memory():
    clear_all_memory()
    save_memory("app_name", APP_NAME)
    save_memory("owner_name", OWNER_NAME)
    return jsonify({"ok": True})


@app.route("/admin/clear_analytics", methods=["POST"])
@admin_required
def admin_clear_analytics():
    clear_analytics()
    return jsonify({"ok": True})


@app.route("/autopatch/suggest", methods=["POST"])
@admin_required
def autopatch_suggest():
    data = request.get_json(silent=True) or {}
    problem_text = sanitize_text(data.get("problem", ""), 1000)
    notes = sanitize_text(data.get("notes", ""), 1000)

    if not problem_text:
        return jsonify({"ok": False, "error": "problem is required"}), 400

    suggestion = build_patch_suggestion(problem_text)
    row = create_patch_queue_item(suggestion, notes=notes)
    log_event("autopatch_suggest", {"problem": problem_text, "patch_name": suggestion["patch_name"]})
    return jsonify({"ok": True, "patch": row})


@app.route("/autopatch/list")
@admin_required
def autopatch_list():
    status = request.args.get("status")
    return jsonify({"ok": True, "patches": list_patch_queue(status)})


@app.route("/autopatch/approve/<int:patch_id>", methods=["POST"])
@admin_required
def autopatch_approve(patch_id):
    item = get_patch_item(patch_id)
    if not item:
        return jsonify({"ok": False, "error": "Patch not found"}), 404

    update_patch_status(patch_id, "approved")
    result = {"ok": True, "status": "approved_only"}

    if AUTO_APPLY_LOW_RISK and item["risk_level"] == "low":
        result["auto_apply"] = apply_low_risk_patch(item)

    log_event("autopatch_approve", {"patch_id": patch_id, "patch_name": item["patch_name"]})
    return jsonify(result)


@app.route("/autopatch/reject/<int:patch_id>", methods=["POST"])
@admin_required
def autopatch_reject(patch_id):
    item = get_patch_item(patch_id)
    if not item:
        return jsonify({"ok": False, "error": "Patch not found"}), 404

    update_patch_status(patch_id, "rejected")
    log_event("autopatch_reject", {"patch_id": patch_id, "patch_name": item["patch_name"]})
    return jsonify({"ok": True, "status": "rejected"})


@app.route("/autopatch/apply/<int:patch_id>", methods=["POST"])
@admin_required
def autopatch_apply(patch_id):
    item = get_patch_item(patch_id)
    if not item:
        return jsonify({"ok": False, "error": "Patch not found"}), 404

    result = apply_low_risk_patch(item)
    log_event("autopatch_apply", {"patch_id": patch_id, "patch_name": item["patch_name"], "result": result})
    return jsonify(result)


@app.route("/memory")
def memory_info():
    return jsonify({
        "app_name": load_memory("app_name", APP_NAME),
        "owner_name": load_memory("owner_name", OWNER_NAME),
        "preferred_language": load_memory("preferred_language", "auto"),
        "saved_user_name": load_memory("user_name", ""),
        "memory_count": memory_count(),
    })


@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "version": VERSION,
        "groq_keys_loaded": len(GROQ_KEYS),
        "system_active": SYSTEM_ACTIVE,
        "uptime": get_uptime(),
        "search_provider": SEARCH_PROVIDER,
        "tavily_enabled": bool(TAVILY_API_KEY),
    })


@app.route("/debug/tavily")
def debug_tavily():
    query = request.args.get("q", "current prime minister of bangladesh")
    results = tavily_search(query, max_results=8)
    filtered = filter_current_info_results(results) if is_office_holder_query(query) else results[:3]
    return jsonify({
        "query": query,
        "search_provider": SEARCH_PROVIDER,
        "tavily_enabled": bool(TAVILY_API_KEY),
        "results_count": len(results),
        "filtered_count": len(filtered),
        "results": results,
        "filtered_results": filtered,
    })


if __name__ == "__main__":
    init_db()
    save_memory("app_name", APP_NAME)
    save_memory("owner_name", OWNER_NAME)
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)