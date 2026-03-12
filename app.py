from flask import Flask, request, jsonify, session
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
VERSION = "42.0.0"

FACEBOOK_URL = "https://www.facebook.com/share/1CBWMUaou9/"
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
GROQ_KEYS = [k.strip() for k in os.getenv("GROQ_KEYS", "").split(",") if k.strip()]
MODEL_PRIMARY = os.getenv("MODEL_PRIMARY", "llama-3.3-70b-versatile")
MODEL_FAST = os.getenv("MODEL_FAST", "llama-3.1-8b-instant")
DB_PATH = os.getenv("DB_PATH", "flux_ai.db")
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "12"))
MAX_USER_TEXT = int(os.getenv("MAX_USER_TEXT", "5000"))
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"

SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "").lower()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True
TOTAL_MESSAGES_LOCK = Lock()
KEY_LOCK = Lock()

CURRENT_INFO_TRUSTED_DOMAINS = [
    "reuters.com",
    "apnews.com",
    "pbs.org",
    "bbc.com",
    "bbc.co.uk",
    "aljazeera.com",
    "parliament.gov.bd",
    "pmo.gov.bd",
    "cabinet.gov.bd",
    "ecs.gov.bd",
]

BAD_SOURCE_DOMAINS = [
    "wikipedia.org",
    "wikidata.org",
    "facebook.com",
    "youtube.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "tiktok.com",
    "blogspot.com",
]

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE


def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS memory (
            key_name TEXT PRIMARY KEY,
            value_text TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

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


def analytics_count():
    try:
        conn = db_connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM analytics").fetchone()
        conn.close()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


def clear_analytics():
    try:
        conn = db_connect()
        conn.execute("DELETE FROM analytics")
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


def memory_count():
    try:
        conn = db_connect()
        row = conn.execute("SELECT COUNT(*) AS c FROM memory").fetchone()
        conn.close()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


init_db()
save_memory("app_name", APP_NAME)
save_memory("owner_name", OWNER_NAME)

KEY_STATES = [{"key": key, "failures": 0, "cooldown_until": 0.0} for key in GROQ_KEYS]


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper


def get_uptime():
    return str(timedelta(seconds=int(time.time() - SERVER_START_TIME)))


def get_current_context():
    tz_dhaka = pytz.timezone("Asia/Dhaka")
    now_dhaka = datetime.now(tz_dhaka)
    now_utc = datetime.now(pytz.utc)
    return {
        "time_utc": now_utc.strftime("%I:%M %p"),
        "time_local": now_dhaka.strftime("%I:%M %p"),
        "date": now_dhaka.strftime("%d %B, %Y"),
        "weekday": now_dhaka.strftime("%A"),
    }


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
        "gold price", "bitcoin price", "stock price", "headline",
        "আজ", "সর্বশেষ", "আজকের", "এখন", "দাম", "নিউজ", "আপডেট", "আবহাওয়া",
        "বর্তমান", "প্রধানমন্ত্রী", "রাষ্ট্রপতি", "কে"
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


def pick_search_topic(query):
    q = (query or "").lower()
    news_words = ["news", "headline", "breaking", "latest news", "খবর", "সর্বশেষ", "আপডেট"]
    price_weather_words = [
        "price", "rate", "gold", "silver", "bitcoin", "crypto", "stock",
        "weather", "temperature", "forecast", "দাম", "রেট", "আবহাওয়া"
    ]

    if any(w in q for w in news_words):
        return "news"
    if any(w in q for w in price_weather_words):
        return "general"
    return "general"


def is_bad_source(url):
    url_l = (url or "").lower()
    return any(domain in url_l for domain in BAD_SOURCE_DOMAINS)


def is_trusted_current_source(url):
    url_l = (url or "").lower()
    return any(domain in url_l for domain in CURRENT_INFO_TRUSTED_DOMAINS)


def normalize_result(item):
    return {
        "title": sanitize_text(item.get("title", "Untitled"), 200),
        "url": sanitize_text(item.get("url", ""), 400),
        "content": sanitize_text(item.get("content", ""), 700),
        "score": float(item.get("score", 0) or 0),
    }


def filter_general_results(results):
    cleaned = []
    for item in results:
        norm = normalize_result(item)
        if is_bad_source(norm["url"]):
            continue
        if not norm["url"]:
            continue
        cleaned.append(norm)
    cleaned.sort(key=lambda x: x["score"], reverse=True)
    return cleaned[:5]


def filter_current_info_results(results):
    filtered = []
    for item in results:
        norm = normalize_result(item)
        url_l = norm["url"].lower()
        content_l = norm["content"].lower()
        title_l = norm["title"].lower()

        if is_bad_source(norm["url"]):
            continue
        if not is_trusted_current_source(norm["url"]):
            continue

        stale_patterns = [
            "sheikh hasina",
            "2019",
            "2020",
            "2021",
            "2022",
            "2023",
        ]
        if ("prime minister" in title_l or "প্রধানমন্ত্রী" in title_l or "prime minister" in content_l) and any(p in content_l for p in stale_patterns):
            if "tarique rahman" not in content_l and "তারেক রহমান" not in content_l:
                continue

        filtered.append(norm)

    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered[:3]


def tavily_search_once(query, topic="general", max_results=8):
    if SEARCH_PROVIDER != "tavily" or not TAVILY_API_KEY:
        return []

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TAVILY_API_KEY}"
        }
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "topic": topic,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False
        }
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload,
            timeout=25
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not isinstance(results, list):
            return []
        return results
    except Exception as e:
        log_event("tavily_error", {"error": str(e), "query": query, "topic": topic})
        return []


def tavily_search(query, max_results=8, current_only=False):
    primary_topic = pick_search_topic(query)
    results = tavily_search_once(query, topic=primary_topic, max_results=max_results)
    if not results:
        fallback_topic = "news" if primary_topic == "general" else "general"
        results = tavily_search_once(query, topic=fallback_topic, max_results=max_results)

    if current_only:
        return filter_current_info_results(results)
    return filter_general_results(results)[:3]


def build_live_fallback(query):
    if detect_language(query) == "bn":
        return "আমি এই প্রশ্নের বর্তমান তথ্য নির্ভরযোগ্য live source থেকে যাচাই করতে পারিনি, তাই guess করছি না।"
    return "I could not verify this current information from trusted live sources, so I am not guessing."


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


def format_sources_structured(results):
    return [{"title": item["title"], "url": item["url"]} for item in results[:3]]


def update_preferences(user_name, preferences, latest_user):
    if user_name:
        save_memory("user_name", user_name)

    if str(preferences.get("memory_enabled", "true")).lower() == "true":
        for key, value in preferences.items():
            save_memory(f"pref_{key}", str(value))

    save_memory("preferred_language", detect_language(latest_user))


def build_system_prompt(user_name, preferences, latest_user, live_results_found):
    ctx = get_current_context()
    task_type = detect_task_type(latest_user)

    answer_length = preferences.get("answer_length", "balanced")
    tone = preferences.get("tone", "normal")
    bangla_first = str(preferences.get("bangla_first", "false")).lower() == "true"
    response_mode = preferences.get("response_mode", "smart")

    base = (
        f"You are {APP_NAME}, a smart and helpful AI assistant. "
        f"Your creator and owner is fixed as {OWNER_NAME} (Bangla: {OWNER_NAME_BN}). "
        f"Never contradict this identity. "
        f"Current user name: {user_name}. "
        f"Current UTC time: {ctx['time_utc']}. "
        f"Dhaka local time: {ctx['time_local']}. "
        f"Date: {ctx['date']}. Day: {ctx['weekday']}. "
        f"Bangla-first: {bangla_first}. "
        f"Primary mode: {response_mode}. "
        f"Answer length: {answer_length}. "
        f"Tone: {tone}."
    )

    rules = """
Core rules:
1. Be accurate, clear, and concise.
2. Keep answers mobile-friendly and easy to read.
3. Do not invent current facts.
4. If current information is requested, only answer from trusted recent sources provided in the prompt.
5. If trusted recent sources are unavailable, say verification was unavailable and do not guess.
6. Give the answer first. Do not paste raw URLs in the answer body.
7. Use very short paragraphs.
8. If asked who created or owns you, the answer is always KAWCHUR.
9. For study mode, explain step by step.
10. For code mode, be practical and stable.
11. If sources are provided, keep the answer factual and limited to those sources.
""".strip()

    task_text = "Task type: general chat."
    if task_type == "code":
        task_text = (
            "Task type: code. "
            "If the user asks to build an app or UI, return a single full HTML file inside one ```html code block. "
            "Put CSS in <style> and JS in <script>. Keep it mobile-friendly."
        )
    elif task_type == "math":
        task_text = "Task type: math. Give the exact answer directly."
    elif task_type == "current_info":
        task_text = (
            "Task type: current info. "
            "Use only the trusted recent sources provided below. "
            "Ignore stale pages, generic profile pages, and untrusted domains."
            if live_results_found else
            "Task type: current info. Trusted live results are unavailable. Do not guess."
        )
    elif task_type == "transform":
        task_text = "Task type: transform. Summarize, rewrite, translate, or simplify directly."

    return "\n\n".join([base, rules, task_text])


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


def generate_answer(messages, user_name, preferences):
    latest_user = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            latest_user = msg["content"]
            break

    update_preferences(user_name, preferences, latest_user)
    task_type = detect_task_type(latest_user)

    if task_type == "math":
        math_result = safe_math_eval(latest_user)
        if math_result is not None:
            if detect_language(latest_user) == "bn":
                return {"answer": f"উত্তর: {math_result}", "sources": []}
            return {"answer": f"Answer: {math_result}", "sources": []}

    search_results = []
    if preferences.get("response_mode") == "search" or task_type == "current_info":
        search_results = tavily_search(latest_user, max_results=8, current_only=(task_type == "current_info"))

    if task_type == "current_info" and not search_results:
        return {"answer": build_live_fallback(latest_user), "sources": []}

    final_messages = [
        {"role": "system", "content": build_system_prompt(user_name, preferences, latest_user, bool(search_results))},
        {"role": "system", "content": f"Fixed identity facts: app name is {APP_NAME}. Owner and creator is {OWNER_NAME}."}
    ]

    if search_results:
        final_messages.append({
            "role": "system",
            "content": (
                "Trusted search results are available below. "
                "Answer cleanly in 1-3 short paragraphs. "
                "Do not output raw URLs in the answer body.\n\n" + format_search_results_for_prompt(search_results)
            )
        })

    final_messages.extend(messages)

    api_key = get_available_key()
    if not api_key:
        return {"answer": "System busy right now. Please try again.", "sources": []}

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=pick_model(messages),
            messages=final_messages,
            temperature=0.15 if search_results else 0.55,
            max_tokens=1400,
            stream=False,
        )
        answer = (completion.choices[0].message.content or "").strip()
        mark_key_success(api_key)
        return {"answer": answer, "sources": format_sources_structured(search_results)}
    except Exception as e:
        mark_key_failure(api_key)
        log_event("groq_error", {"error": str(e)})
        if task_type == "current_info":
            return {"answer": build_live_fallback(latest_user), "sources": []}
        return {"answer": "System busy. Please try again in a moment.", "sources": []}


HOME_CARDS = [
    {"title": "Study Help", "prompt": "Explain this topic step by step for a student", "icon": "fas fa-graduation-cap"},
    {"title": "Build App", "prompt": "Create a modern mobile-friendly app in HTML", "icon": "fas fa-code"},
    {"title": "Smart Answer", "prompt": "Give me a smart clear answer", "icon": "fas fa-brain"},
    {"title": "Search Web", "prompt": "latest news today", "icon": "fas fa-globe"}
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
    {"icon": "fas fa-brain", "text": "What is the difference between RAM and ROM"},
    {"icon": "fas fa-school", "text": "Make a study routine for class 9"},
    {"icon": "fas fa-microscope", "text": "Explain the cell structure"},
    {"icon": "fas fa-cloud-sun", "text": "today weather in Dhaka"}
]


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
        :root {
            --bg: #050816;
            --bg2: #0a1130;
            --text: #eef2ff;
            --muted: #9aa8c7;
            --accent: #8b5cf6;
            --accent2: #60a5fa;
            --border: rgba(255,255,255,0.08);
            --danger: #ef4444;
            --success: #22c55e;
        }

        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: radial-gradient(circle at top, var(--bg2) 0%, var(--bg) 58%, #02040c 100%);
            color: var(--text);
            font-family: 'Outfit', 'Noto Sans Bengali', sans-serif;
        }

        .app {
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
            background: radial-gradient(circle at top, rgba(139,92,246,0.10) 0%, transparent 45%);
        }

        #bg-canvas {
            position: fixed;
            inset: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.28;
            pointer-events: none;
        }

        .shell { position: relative; z-index: 1; width: 100%; height: 100%; overflow: hidden; }

        .sidebar-overlay, .sheet-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.48);
            display: none;
            z-index: 90;
        }
        .sidebar-overlay.show, .sheet-overlay.show { display: block; }

        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: min(84vw, 320px);
            height: 100dvh;
            background: linear-gradient(180deg, rgba(18,27,52,0.98), rgba(8,12,28,0.98));
            border-right: 1px solid var(--border);
            transform: translateX(-100%);
            transition: transform 0.22s ease;
            z-index: 100;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 16px;
            box-shadow: 20px 0 50px rgba(0,0,0,0.32);
        }
        .sidebar.open { transform: translateX(0); }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 16px;
        }

        .brand-mark, .top-orb {
            width: 48px;
            height: 48px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(180deg, rgba(22,22,56,0.98), rgba(7,7,28,0.98));
            color: var(--accent);
            position: relative;
            box-shadow: 0 0 18px rgba(139,92,246,0.22);
        }

        .top-orb {
            animation: topOrbPulse 3.2s infinite ease-in-out;
        }

        .top-orb::before {
            content: "";
            position: absolute;
            inset: -8px;
            border-radius: 22px;
            background: radial-gradient(circle, rgba(139,92,246,0.28) 0%, rgba(96,165,250,0.16) 45%, transparent 72%);
            opacity: 0.55;
            z-index: -1;
        }

        .side-btn {
            width: 100%;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text);
            border-radius: 15px;
            padding: 13px 14px;
            cursor: pointer;
            text-align: left;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .side-label {
            font-size: 12px;
            color: var(--muted);
            margin: 16px 0 8px;
            letter-spacing: 1px;
            font-weight: 700;
        }

        .search-input {
            width: 100%;
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            color: var(--text);
            outline: none;
            margin-bottom: 10px;
        }

        .history-item {
            width: 100%;
            padding: 11px 12px;
            border-radius: 14px;
            margin-bottom: 8px;
            color: var(--muted);
            background: rgba(255,255,255,0.02);
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .history-title {
            flex: 1;
            min-width: 0;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .history-mini {
            border: none;
            background: transparent;
            color: var(--muted);
            cursor: pointer;
            width: 28px;
            height: 28px;
            border-radius: 8px;
        }

        .main {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .topbar {
            height: 66px;
            min-height: 66px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 14px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            background: rgba(5, 8, 22, 0.54);
            backdrop-filter: blur(12px);
        }

        .top-left {
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 0;
        }

        .menu-btn {
            width: 42px;
            height: 42px;
            border: none;
            border-radius: 13px;
            background: rgba(255,255,255,0.06);
            color: var(--text);
            cursor: pointer;
            flex-shrink: 0;
            font-size: 18px;
        }

        .top-title {
            font-size: 22px;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #d7ccff 55%, #b7d9ff 100%);
            -webkit-background-clip: text;
            color: transparent;
        }

        .chat-box {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 8px 12px 108px;
            scroll-behavior: smooth;
        }

        .welcome {
            width: 100%;
            max-width: 920px;
            margin: 0 auto;
        }

        .hero {
            text-align: center;
            padding: 38px 0 20px;
        }

        .hero-orb-wrap {
            position: relative;
            width: 84px;
            height: 84px;
            margin: 0 auto 16px;
        }

        .hero-orb-ring {
            position: absolute;
            inset: 0;
            border-radius: 50%;
            border: 1px solid rgba(139,92,246,0.25);
            animation: pulseRing 2.4s infinite;
        }

        .hero-orb-ring.r2 { animation-delay: 0.8s; }
        .hero-orb-ring.r3 { animation-delay: 1.6s; }

        .hero-orb {
            position: absolute;
            inset: 10px;
            border-radius: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(180deg, rgba(22,22,56,0.95), rgba(7,7,28,0.95));
            box-shadow: 0 0 42px rgba(139,92,246,0.22);
            color: var(--accent);
            font-size: 30px;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(30px, 7vw, 44px);
            letter-spacing: -0.5px;
        }

        .hero-sub {
            margin: 10px auto 0;
            max-width: 540px;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.7;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin-top: 18px;
        }

        .home-card {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            padding: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .home-card-icon {
            width: 46px;
            height: 46px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(139,92,246,0.12);
            color: var(--accent);
            flex-shrink: 0;
            font-size: 18px;
        }

        .home-card-title {
            font-size: 18px;
            font-weight: 700;
        }

        .chips-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 16px;
            justify-content: center;
        }

        .quick-chip {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            color: var(--text);
            border-radius: 999px;
            padding: 10px 14px;
            cursor: pointer;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .quick-chip i { color: var(--accent); }

        .message {
            width: 100%;
            max-width: 900px;
            margin: 0 auto 18px;
            display: flex;
            gap: 10px;
            align-items: flex-start;
        }

        .message.user { flex-direction: row-reverse; }

        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .avatar.bot {
            background: linear-gradient(135deg, #a855f7 0%, #60a5fa 100%);
            color: white;
        }

        .avatar.user {
            background: rgba(255,255,255,0.08);
            color: white;
        }

        .bubble-wrap {
            min-width: 0;
            flex: 1;
            max-width: calc(100% - 50px);
        }

        .message.user .bubble-wrap {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }

        .name {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 6px;
            font-weight: 700;
        }

        .message.user .name { display: none; }

        .bubble {
            width: 100%;
            word-wrap: break-word;
            overflow-wrap: anywhere;
            line-height: 1.7;
            font-size: 16px;
        }

        .message.user .bubble {
            width: auto;
            max-width: min(82vw, 560px);
            padding: 14px 16px;
            border-radius: 18px;
            background: linear-gradient(135deg, #312e81 0%, #2563eb 100%);
            color: white;
            box-shadow: 0 10px 26px rgba(37,99,235,0.14);
        }

        .message.bot .bubble { padding: 0; background: transparent; }

        .answer-card {
            border-radius: 18px;
            padding: 14px 16px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.04);
        }

        .msg-time {
            font-size: 11px;
            color: var(--muted);
            margin-top: 6px;
        }

        .msg-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .act-btn {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            color: var(--text);
            border-radius: 999px;
            padding: 7px 11px;
            cursor: pointer;
            font-size: 12px;
        }

        .source-cards {
            display: grid;
            gap: 10px;
            margin-top: 12px;
        }

        .source-card {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            border-radius: 14px;
            padding: 12px 14px;
        }

        .source-card a {
            color: #dbe4ff;
            text-decoration: none;
            font-weight: 600;
            word-break: break-word;
        }

        .source-label {
            color: var(--muted);
            font-size: 12px;
            margin-bottom: 6px;
        }

        .typing {
            width: 100%;
            max-width: 900px;
            margin: 0 auto 18px;
            color: var(--muted);
        }

        .typing-card {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            border-radius: 18px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.03);
            width: fit-content;
            max-width: 100%;
        }

        .voice-wave {
            display: flex;
            gap: 4px;
            align-items: center;
            height: 24px;
        }

        .voice-wave span {
            width: 4px;
            border-radius: 999px;
            background: linear-gradient(180deg, var(--accent), var(--accent2));
            animation: wave 1.1s infinite ease-in-out;
        }

        .voice-wave span:nth-child(1) { height: 10px; animation-delay: 0s; }
        .voice-wave span:nth-child(2) { height: 18px; animation-delay: 0.12s; }
        .voice-wave span:nth-child(3) { height: 24px; animation-delay: 0.24s; }
        .voice-wave span:nth-child(4) { height: 16px; animation-delay: 0.36s; }
        .voice-wave span:nth-child(5) { height: 12px; animation-delay: 0.48s; }

        .typing-beam {
            width: 52px;
            height: 2px;
            border-radius: 999px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            background-size: 200% 100%;
            animation: beam 1.4s linear infinite;
        }

        .input-area {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            padding: 12px;
            background: linear-gradient(to top, rgba(2,4,12,1) 0%, rgba(2,4,12,0.2) 100%);
        }

        .input-wrap {
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
        }

        .input-box {
            display: flex;
            gap: 10px;
            align-items: flex-end;
            width: 100%;
            background: rgba(13,19,38,0.96);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 10px 10px 10px 12px;
            box-shadow: 0 12px 34px rgba(0,0,0,0.20);
            position: relative;
            overflow: hidden;
        }

        .tool-btn, .send-btn {
            width: 44px;
            height: 44px;
            border: none;
            cursor: pointer;
            flex-shrink: 0;
            position: relative;
            z-index: 1;
        }

        .tool-btn {
            border-radius: 14px;
            background: rgba(255,255,255,0.06);
            color: var(--text);
            font-size: 18px;
        }

        .send-btn {
            border-radius: 50%;
            background: var(--text);
            color: #111827;
            font-size: 18px;
        }

        textarea {
            flex: 1;
            min-width: 0;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text);
            font-size: 16px;
            resize: none;
            max-height: 180px;
            font-family: inherit;
            line-height: 1.5;
            padding: 9px 2px;
        }

        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.72);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 200;
            padding: 16px;
        }

        .modal-card {
            width: 100%;
            max-width: 420px;
            background: linear-gradient(180deg, rgba(18,27,52,0.98), rgba(8,12,28,0.98));
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 22px;
            position: relative;
        }

        .sheet {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(18,27,52,0.99), rgba(8,12,28,0.99));
            border-top: 1px solid var(--border);
            border-top-left-radius: 22px;
            border-top-right-radius: 22px;
            padding: 18px;
            z-index: 220;
            transform: translateY(110%);
            transition: transform 0.22s ease;
        }

        .sheet.open { transform: translateY(0); }

        .sheet-grid { display: grid; gap: 12px; }
        .sheet-row-title {
            font-size: 13px;
            color: var(--muted);
            letter-spacing: 0.6px;
            font-weight: 700;
            margin-top: 2px;
        }
        .sheet-pills {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .sheet-pill {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            color: var(--text);
            border-radius: 999px;
            padding: 10px 14px;
            cursor: pointer;
            font-size: 13px;
        }
        .sheet-pill.active {
            background: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%);
            border-color: transparent;
        }

        .sheet-toggle {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.04);
            border-radius: 14px;
            padding: 10px 12px;
            color: var(--text);
            font-size: 13px;
        }

        .modal-card input, .modal-card textarea {
            width: 100%;
            margin: 12px 0;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.05);
            color: var(--text);
            outline: none;
        }

        .modal-row {
            display: flex;
            gap: 10px;
            margin-top: 12px;
        }

        .modal-row button {
            flex: 1;
            border: none;
            border-radius: 14px;
            padding: 13px;
            cursor: pointer;
            font-size: 15px;
        }

        .btn-cancel { background: rgba(255,255,255,0.08); color: white; }
        .btn-confirm { background: var(--success); color: black; }
        .btn-danger { background: var(--danger); color: white; }

        .close-small {
            position: absolute;
            top: 12px;
            right: 12px;
            background: transparent;
            border: none;
            color: var(--muted);
            font-size: 20px;
            cursor: pointer;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 14px;
        }

        .stat-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px;
        }

        .stat-value {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .stat-label {
            color: var(--muted);
            font-size: 12px;
        }

        @keyframes wave {
            0%, 100% { transform: scaleY(0.55); opacity: 0.6; }
            50% { transform: scaleY(1); opacity: 1; }
        }

        @keyframes beam {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }

        @keyframes pulseRing {
            0% { transform: scale(0.72); opacity: 0.45; }
            100% { transform: scale(1.25); opacity: 0; }
        }

        @keyframes topOrbPulse {
            0% { transform: scale(1); box-shadow: 0 0 18px rgba(139,92,246,0.22); }
            50% {
                transform: scale(1.08);
                box-shadow:
                    0 0 22px rgba(139,92,246,0.38),
                    0 0 42px rgba(96,165,250,0.28),
                    0 0 64px rgba(139,92,246,0.18);
            }
            100% { transform: scale(1); box-shadow: 0 0 18px rgba(139,92,246,0.22); }
        }

        .thinking .top-orb, .thinking .hero-orb {
            animation: topOrbPulse 1.1s infinite ease-in-out;
        }

        @media (min-width: 980px) {
            .sidebar {
                transform: translateX(0);
                width: 320px;
            }
            .sidebar-overlay { display: none !important; }
            .main { padding-left: 320px; }
            .menu-btn { display: none; }
            .input-area { left: 320px; }
            .cards-grid { grid-template-columns: 1fr 1fr; }
        }

        @media (max-width: 520px) {
            .topbar { padding: 0 10px; }
            .top-title { font-size: 18px; }
            .chat-box { padding: 8px 10px 104px; }
            .avatar { width: 36px; height: 36px; }
            .bubble-wrap { max-width: calc(100% - 44px); }
            .message.user .bubble { max-width: calc(100vw - 72px); }
            .input-area { padding: 10px; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <canvas id="bg-canvas"></canvas>

    <div class="app shell">
        <div id="sidebar-overlay" class="sidebar-overlay" onclick="closeSidebar()"></div>
        <div id="sheet-overlay" class="sheet-overlay" onclick="closeToolsSheet()"></div>

        <aside id="sidebar" class="sidebar">
            <div class="brand">
                <div class="brand-mark"><i class="fas fa-bolt"></i></div>
                <div>__APP_NAME__</div>
            </div>

            <button class="side-btn" onclick="startNewChat(); closeSidebar();"><i class="fas fa-plus"></i> New Chat</button>
            <button class="side-btn" onclick="exportCurrentChat(); closeSidebar();"><i class="fas fa-file-export"></i> Export Chat</button>

            <div class="side-label">Search Chats</div>
            <input id="chat-search" class="search-input" placeholder="Search history..." oninput="renderHistory()">

            <div class="side-label">Recent</div>
            <div id="history-list"></div>

            <div class="side-label">About</div>
            <div style="padding:14px;border-radius:18px;background:rgba(255,255,255,0.03);border:1px solid var(--border);line-height:1.7;">
                <div style="font-size:18px;font-weight:800;margin-bottom:6px;">__APP_NAME__</div>
                <div style="color:var(--muted);margin-bottom:8px;">Version __VERSION__</div>
                <div>Created by <span style="color:var(--accent);">__OWNER_NAME__</span></div>
                <div style="margin-top:12px;font-size:12px;color:var(--muted);">© 2026 __APP_NAME__ — Copyright by __OWNER_NAME__</div>
            </div>

            <button class="side-btn" onclick="clearChats()"><i class="fas fa-trash"></i> Delete All Chats</button>
        </aside>

        <main class="main">
            <div class="topbar">
                <div class="top-left">
                    <button class="menu-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
                    <div class="top-title">__APP_NAME__</div>
                </div>
                <div class="top-orb"><i class="fas fa-bolt"></i></div>
            </div>

            <div id="chat-box" class="chat-box">
                <div id="welcome" class="welcome">
                    <div class="hero">
                        <div class="hero-orb-wrap">
                            <div class="hero-orb-ring"></div>
                            <div class="hero-orb-ring r2"></div>
                            <div class="hero-orb-ring r3"></div>
                            <div class="hero-orb"><i class="fas fa-bolt"></i></div>
                        </div>
                        <h1>How can __APP_NAME__ help today?</h1>
                        <div class="hero-sub">Ask questions, study better, build simple apps, and verify current information from trusted sources.</div>
                    </div>

                    <div id="home-cards" class="cards-grid"></div>
                    <div id="quick-chips" class="chips-row"></div>
                </div>
            </div>

            <div class="input-area">
                <div class="input-wrap">
                    <div id="input-box" class="input-box">
                        <button id="tool-btn" class="tool-btn" onclick="toggleToolsSheet()"><i class="fas fa-plus"></i></button>
                        <textarea id="msg" rows="1" placeholder="Ask __APP_NAME__..." oninput="resizeInput(this)"></textarea>
                        <button id="send-btn" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <div id="tools-sheet" class="sheet">
        <div class="sheet-grid">
            <div class="sheet-row-title">Mode</div>
            <div class="sheet-pills">
                <button id="mode-smart" class="sheet-pill active" onclick="setMode('smart')">Smart</button>
                <button id="mode-study" class="sheet-pill" onclick="setMode('study')">Study</button>
                <button id="mode-code" class="sheet-pill" onclick="setMode('code')">Code</button>
                <button id="mode-search" class="sheet-pill" onclick="setMode('search')">Search</button>
            </div>

            <div class="sheet-row-title">Answer length</div>
            <div class="sheet-pills">
                <button id="len-short" class="sheet-pill" onclick="setAnswerLength('short')">Short</button>
                <button id="len-balanced" class="sheet-pill active" onclick="setAnswerLength('balanced')">Balanced</button>
                <button id="len-detailed" class="sheet-pill" onclick="setAnswerLength('detailed')">Detailed</button>
            </div>

            <div class="sheet-row-title">Tone</div>
            <div class="sheet-pills">
                <button id="tone-normal" class="sheet-pill active" onclick="setTone('normal')">Normal</button>
                <button id="tone-friendly" class="sheet-pill" onclick="setTone('friendly')">Friendly</button>
                <button id="tone-teacher" class="sheet-pill" onclick="setTone('teacher')">Teacher</button>
                <button id="tone-coder" class="sheet-pill" onclick="setTone('coder')">Coder</button>
            </div>

            <div class="sheet-row-title">Visual theme</div>
            <div class="sheet-pills">
                <button class="sheet-pill theme-pick" data-theme="matrix" onclick="setVisualTheme('matrix')">Matrix</button>
                <button class="sheet-pill theme-pick" data-theme="neon" onclick="setVisualTheme('neon')">Neon</button>
                <button class="sheet-pill theme-pick" data-theme="galaxy" onclick="setVisualTheme('galaxy')">Galaxy</button>
            </div>

            <div class="sheet-row-title">Options</div>
            <div class="sheet-pills">
                <label class="sheet-toggle"><input id="bangla-first" type="checkbox" onchange="saveBehaviorPrefs()"> Bangla First</label>
                <label class="sheet-toggle"><input id="memory-enabled" type="checkbox" checked onchange="saveBehaviorPrefs()"> Memory</label>
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
            <div style="color:var(--muted);margin-bottom:8px;">System overview</div>

            <div class="stats-grid">
                <div class="stat-card"><div id="stat-messages" class="stat-value">0</div><div class="stat-label">Total Messages</div></div>
                <div class="stat-card"><div id="stat-uptime" class="stat-value">0</div><div class="stat-label">Uptime</div></div>
                <div class="stat-card"><div id="stat-system" class="stat-value">ON</div><div class="stat-label">System</div></div>
                <div class="stat-card"><div id="stat-keys" class="stat-value">0</div><div class="stat-label">Loaded Keys</div></div>
                <div class="stat-card"><div id="stat-analytics" class="stat-value">0</div><div class="stat-label">Analytics</div></div>
                <div class="stat-card"><div id="stat-memory" class="stat-value">0</div><div class="stat-label">Memory</div></div>
            </div>

            <div class="modal-row">
                <button class="btn-danger" onclick="toggleSystemAdmin()">Toggle System</button>
                <button class="btn-cancel" onclick="resetMemoryAdmin()">Reset Memory</button>
            </div>
            <div class="modal-row">
                <button class="btn-danger" onclick="clearAnalyticsAdmin()">Clear Analytics</button>
                <button class="btn-cancel" onclick="closeAdminPanel()">Close</button>
            </div>
        </div>
    </div>

    <div id="rename-modal" class="modal-overlay">
        <div class="modal-card">
            <button class="close-small" onclick="closeRenameModal()"><i class="fas fa-times"></i></button>
            <div style="font-size:24px;font-weight:800;margin-bottom:6px;">Rename Chat</div>
            <input type="text" id="rename-input" placeholder="New title">
            <div class="modal-row">
                <button class="btn-cancel" onclick="closeRenameModal()">Cancel</button>
                <button class="btn-confirm" onclick="confirmRenameChat()">Save</button>
            </div>
        </div>
    </div>

    <div id="edit-message-modal" class="modal-overlay">
        <div class="modal-card">
            <button class="close-small" onclick="closeEditMessageModal()"><i class="fas fa-times"></i></button>
            <div style="font-size:24px;font-weight:800;margin-bottom:6px;">Edit Message</div>
            <textarea id="edit-message-input" rows="6" placeholder="Edit text"></textarea>
            <div class="modal-row">
                <button class="btn-cancel" onclick="closeEditMessageModal()">Cancel</button>
                <button class="btn-confirm" onclick="confirmEditMessage()">Save</button>
            </div>
        </div>
    </div>

    <script>
        marked.setOptions({ breaks: true, gfm: true });

        const HOME_CARDS = __HOME_CARDS__;
        const SUGGESTION_POOL = __SUGGESTIONS__;

        let chats = JSON.parse(localStorage.getItem("flux_v42_history") || "[]");
        let currentChatId = null;
        let userName = localStorage.getItem("flux_user_name_fixed") || "";
        let awaitingName = false;
        let responseMode = localStorage.getItem("flux_response_mode") || "smart";
        let lastUserPrompt = "";
        let renameChatId = null;
        let editingMessageMeta = null;
        let currentVisualTheme = localStorage.getItem("flux_visual_theme") || "neon";
        let suggestionTimer = null;

        const chatBox = document.getElementById("chat-box");
        const welcome = document.getElementById("welcome");
        const msgInput = document.getElementById("msg");
        const historyList = document.getElementById("history-list");
        const sidebar = document.getElementById("sidebar");
        const sidebarOverlay = document.getElementById("sidebar-overlay");
        const sheetOverlay = document.getElementById("sheet-overlay");
        const toolsSheet = document.getElementById("tools-sheet");
        const inputBox = document.getElementById("input-box");

        function shuffleArray(arr) {
            const a = [...arr];
            for (let i = a.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [a[i], a[j]] = [a[j], a[i]];
            }
            return a;
        }

        function updateThemeButtons() {
            document.querySelectorAll(".theme-pick").forEach(function(btn) {
                const isActive = btn.getAttribute("data-theme") === currentVisualTheme;
                btn.classList.toggle("active", isActive);
            });
        }

        function applyVisualThemeSurface() {
            if (currentVisualTheme === "matrix") {
                document.documentElement.style.setProperty("--accent", "#22c55e");
                document.documentElement.style.setProperty("--accent2", "#4ade80");
            } else if (currentVisualTheme === "galaxy") {
                document.documentElement.style.setProperty("--accent", "#f472b6");
                document.documentElement.style.setProperty("--accent2", "#8b5cf6");
            } else {
                document.documentElement.style.setProperty("--accent", "#8b5cf6");
                document.documentElement.style.setProperty("--accent2", "#60a5fa");
            }
        }

        function setVisualTheme(name) {
            currentVisualTheme = name;
            localStorage.setItem("flux_visual_theme", name);
            updateThemeButtons();
            applyVisualThemeSurface();
        }

        function initBackground() {
            const canvas = document.getElementById("bg-canvas");
            const ctx = canvas.getContext("2d");
            let particles = [];

            function themeColorSet() {
                if (currentVisualTheme === "matrix") {
                    return { p: "rgba(34,197,94,0.70)", l: "rgba(34,197,94,0.16)" };
                }
                if (currentVisualTheme === "galaxy") {
                    return { p: "rgba(244,114,182,0.72)", l: "rgba(168,85,247,0.15)" };
                }
                return { p: "rgba(96,165,250,0.70)", l: "rgba(59,130,246,0.16)" };
            }

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }

            function makeParticles() {
                particles = [];
                const count = Math.max(14, Math.floor(window.innerWidth / 90));
                for (let i = 0; i < count; i++) {
                    particles.push({
                        x: Math.random() * canvas.width,
                        y: Math.random() * canvas.height,
                        vx: (Math.random() - 0.5) * 0.08,
                        vy: (Math.random() - 0.5) * 0.08,
                        r: Math.random() * 1.8 + 0.5
                    });
                }
            }

            function drawMatrixRain() {
                const cols = Math.floor(canvas.width / 24);
                const t = Date.now() * 0.0016;
                ctx.save();
                ctx.globalAlpha = 0.05;
                ctx.fillStyle = "#22c55e";
                for (let i = 0; i < cols; i++) {
                    const x = i * 24;
                    const y = ((t * 120 + i * 57) % (canvas.height + 90)) - 90;
                    ctx.fillRect(x, y, 2, 20);
                }
                ctx.restore();
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                if (currentVisualTheme === "matrix") {
                    drawMatrixRain();
                }

                const colors = themeColorSet();

                for (let i = 0; i < particles.length; i++) {
                    const p = particles[i];
                    p.x += p.vx;
                    p.y += p.vy;

                    if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                    if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                    ctx.fillStyle = colors.p;
                    ctx.fill();

                    for (let j = i + 1; j < particles.length; j++) {
                        const q = particles[j];
                        const dx = p.x - q.x;
                        const dy = p.y - q.y;
                        const d = Math.sqrt(dx * dx + dy * dy);
                        if (d < 90) {
                            ctx.beginPath();
                            ctx.moveTo(p.x, p.y);
                            ctx.lineTo(q.x, q.y);
                            const alpha = ((1 - d / 90) * 0.12).toFixed(3);
                            let color = colors.l;
                            color = color.replace("0.16", alpha).replace("0.15", alpha);
                            ctx.strokeStyle = color;
                            ctx.lineWidth = 1;
                            ctx.stroke();
                        }
                    }
                }

                requestAnimationFrame(draw);
            }

            window.addEventListener("resize", function() {
                resize();
                makeParticles();
            });

            resize();
            makeParticles();
            draw();
        }

        function renderHomeCards() {
            const box = document.getElementById("home-cards");
            box.innerHTML = "";
            HOME_CARDS.forEach(function(card) {
                const el = document.createElement("div");
                el.className = "home-card";
                el.innerHTML =
                    '<div class="home-card-icon"><i class="' + card.icon + '"></i></div>' +
                    '<div><div class="home-card-title">' + card.title + '</div></div>';
                el.onclick = function() {
                    msgInput.value = card.prompt;
                    resizeInput(msgInput);
                    sendMessage();
                };
                box.appendChild(el);
            });
        }

        function renderQuickChips() {
            const box = document.getElementById("quick-chips");
            box.innerHTML = "";
            const picks = shuffleArray(SUGGESTION_POOL).slice(0, 4);
            picks.forEach(function(item) {
                const btn = document.createElement("button");
                btn.className = "quick-chip";
                btn.innerHTML = '<i class="' + item.icon + '"></i><span>' + item.text + '</span>';
                btn.onclick = function() {
                    msgInput.value = item.text;
                    resizeInput(msgInput);
                    sendMessage();
                };
                box.appendChild(btn);
            });
        }

        function startSuggestionRotation() {
            if (suggestionTimer) clearInterval(suggestionTimer);
            suggestionTimer = setInterval(function() {
                if (welcome.style.display !== "none") {
                    renderQuickChips();
                }
            }, 12000);
        }

        function saveChats() {
            localStorage.setItem("flux_v42_history", JSON.stringify(chats));
        }

        function filteredChats() {
            const q = (document.getElementById("chat-search").value || "").toLowerCase().trim();
            let list = [...chats];

            list.sort(function(a, b) {
                if ((b.pinned ? 1 : 0) !== (a.pinned ? 1 : 0)) return (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0);
                if ((b.favorite ? 1 : 0) !== (a.favorite ? 1 : 0)) return (b.favorite ? 1 : 0) - (a.favorite ? 1 : 0);
                return (b.id || 0) - (a.id || 0);
            });

            if (!q) return list;

            return list.filter(function(chat) {
                if ((chat.title || "").toLowerCase().includes(q)) return true;
                return (chat.messages || []).some(function(m) {
                    return (m.text || "").toLowerCase().includes(q);
                });
            });
        }

        function renderHistory() {
            historyList.innerHTML = "";
            filteredChats().forEach(function(chat) {
                const row = document.createElement("div");
                row.className = "history-item";

                const title = document.createElement("div");
                title.className = "history-title";
                title.textContent = (chat.pinned ? "📌 " : "") + (chat.favorite ? "⭐ " : "") + (chat.title || "New Conversation");
                title.onclick = function() {
                    loadChat(chat.id);
                    closeSidebar();
                };

                const pinBtn = document.createElement("button");
                pinBtn.className = "history-mini";
                pinBtn.innerHTML = '<i class="fas fa-thumbtack"></i>';
                pinBtn.onclick = function(e) {
                    e.stopPropagation();
                    chat.pinned = !chat.pinned;
                    saveChats();
                    renderHistory();
                };

                const favBtn = document.createElement("button");
                favBtn.className = "history-mini";
                favBtn.innerHTML = '<i class="fas fa-star"></i>';
                favBtn.onclick = function(e) {
                    e.stopPropagation();
                    chat.favorite = !chat.favorite;
                    saveChats();
                    renderHistory();
                };

                const renameBtn = document.createElement("button");
                renameBtn.className = "history-mini";
                renameBtn.innerHTML = '<i class="fas fa-pen"></i>';
                renameBtn.onclick = function(e) {
                    e.stopPropagation();
                    openRenameModal(chat.id, chat.title || "New Conversation");
                };

                const delBtn = document.createElement("button");
                delBtn.className = "history-mini";
                delBtn.innerHTML = '<i class="fas fa-trash"></i>';
                delBtn.onclick = function(e) {
                    e.stopPropagation();
                    deleteChat(chat.id);
                };

                row.appendChild(title);
                row.appendChild(pinBtn);
                row.appendChild(favBtn);
                row.appendChild(renameBtn);
                row.appendChild(delBtn);
                historyList.appendChild(row);
            });
        }

        function createMessage(role, text, sources) {
            return {
                id: Date.now() + Math.random().toString(16).slice(2),
                role: role,
                text: text,
                sources: sources || [],
                created_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
            };
        }

        function startNewChat() {
            currentChatId = Date.now();
            chats.unshift({ id: currentChatId, title: "New Conversation", pinned: false, favorite: false, messages: [] });
            saveChats();
            renderHistory();
            chatBox.innerHTML = "";
            chatBox.appendChild(welcome);
            welcome.style.display = "block";
            renderQuickChips();
            msgInput.value = "";
            resizeInput(msgInput);
        }

        function deleteChat(id) {
            chats = chats.filter(function(c) { return c.id !== id; });
            if (currentChatId === id) {
                currentChatId = null;
                chatBox.innerHTML = "";
                chatBox.appendChild(welcome);
                welcome.style.display = "block";
                renderQuickChips();
            }
            saveChats();
            renderHistory();
        }

        function openRenameModal(chatId, currentTitle) {
            renameChatId = chatId;
            document.getElementById("rename-input").value = currentTitle || "";
            document.getElementById("rename-modal").style.display = "flex";
        }

        function closeRenameModal() {
            renameChatId = null;
            document.getElementById("rename-modal").style.display = "none";
        }

        function confirmRenameChat() {
            if (!renameChatId) return;
            const chat = chats.find(function(c) { return c.id === renameChatId; });
            if (!chat) return;
            const newName = document.getElementById("rename-input").value.trim();
            if (!newName) {
                closeRenameModal();
                return;
            }
            chat.title = newName.slice(0, 50);
            saveChats();
            renderHistory();
            closeRenameModal();
        }

        function openEditMessageModal(chatId, messageId, currentText) {
            editingMessageMeta = { chatId: chatId, messageId: messageId };
            document.getElementById("edit-message-input").value = currentText || "";
            document.getElementById("edit-message-modal").style.display = "flex";
        }

        function closeEditMessageModal() {
            editingMessageMeta = null;
            document.getElementById("edit-message-modal").style.display = "none";
        }

        function confirmEditMessage() {
            if (!editingMessageMeta) return;
            const chat = chats.find(function(c) { return c.id === editingMessageMeta.chatId; });
            if (!chat) return;
            const msg = chat.messages.find(function(m) { return m.id === editingMessageMeta.messageId; });
            if (!msg) return;

            const newText = document.getElementById("edit-message-input").value.trim();
            if (!newText) {
                closeEditMessageModal();
                return;
            }

            msg.text = newText;
            saveChats();
            loadChat(chat.id);
            closeEditMessageModal();
        }

        function clearChats() {
            localStorage.removeItem("flux_v42_history");
            location.reload();
        }

        function exportCurrentChat() {
            const chat = chats.find(function(c) { return c.id === currentChatId; });
            if (!chat || !chat.messages.length) return;

            let txt = "";
            chat.messages.forEach(function(m) {
                const label = m.role === "user" ? "You" : "__APP_NAME__";
                txt += label + " [" + (m.created_at || "") + "]\\n" + m.text + "\\n";
                if (m.sources && m.sources.length) {
                    txt += "Sources:\\n";
                    m.sources.forEach(function(s) {
                        txt += "- " + s.title + " — " + s.url + "\\n";
                    });
                }
                txt += "\\n";
            });

            const blob = new Blob([txt], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "flux_chat.txt";
            a.click();
            URL.revokeObjectURL(url);
        }

        function loadChat(id) {
            currentChatId = id;
            const chat = chats.find(function(c) { return c.id === id; });
            if (!chat) return;

            chatBox.innerHTML = "";
            if (!chat.messages.length) {
                chatBox.appendChild(welcome);
                welcome.style.display = "block";
                renderQuickChips();
            } else {
                welcome.style.display = "none";
                chat.messages.forEach(function(m) {
                    appendBubble(m, chat.id);
                });
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function deleteMessage(chatId, messageId) {
            const chat = chats.find(function(c) { return c.id === chatId; });
            if (!chat) return;
            chat.messages = chat.messages.filter(function(m) { return m.id !== messageId; });
            saveChats();
            loadChat(chatId);
        }

        function makeActionButton(label, onClickFn) {
            const btn = document.createElement("button");
            btn.className = "act-btn";
            btn.textContent = label;
            btn.onclick = onClickFn;
            return btn;
        }

        function createSourceCards(sources) {
            if (!sources || !sources.length) return "";
            let html = '<div class="source-cards">';
            sources.forEach(function(s, i) {
                html += '<div class="source-card">';
                html += '<div class="source-label">Source ' + (i + 1) + '</div>';
                html += '<a href="' + s.url + '" target="_blank" rel="noopener noreferrer">' + s.title + '</a>';
                html += '</div>';
            });
            html += '</div>';
            return html;
        }

        function appendBubble(msg, chatId) {
            welcome.style.display = "none";
            const isUser = msg.role === "user";

            const wrapper = document.createElement("div");
            wrapper.className = isUser ? "message user" : "message bot";

            const avatar = document.createElement("div");
            avatar.className = isUser ? "avatar user" : "avatar bot";
            avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';

            const bubbleWrap = document.createElement("div");
            bubbleWrap.className = "bubble-wrap";

            const name = document.createElement("div");
            name.className = "name";
            name.textContent = isUser ? "You" : "__APP_NAME__";

            const bubble = document.createElement("div");
            bubble.className = "bubble";

            if (isUser) {
                bubble.innerHTML = marked.parse(msg.text || "");
            } else {
                bubble.innerHTML = '<div class="answer-card">' + marked.parse(msg.text || "") + createSourceCards(msg.sources || []) + '</div>';
            }

            const timeDiv = document.createElement("div");
            timeDiv.className = "msg-time";
            timeDiv.textContent = msg.created_at || "";

            bubbleWrap.appendChild(name);
            bubbleWrap.appendChild(bubble);
            bubbleWrap.appendChild(timeDiv);

            const actions = document.createElement("div");
            actions.className = "msg-actions";

            if (isUser) {
                actions.appendChild(makeActionButton("Copy", function() {
                    navigator.clipboard.writeText(msg.text || "");
                }));
                actions.appendChild(makeActionButton("Edit", function() {
                    openEditMessageModal(chatId, msg.id, msg.text || "");
                }));
                actions.appendChild(makeActionButton("Delete", function() {
                    deleteMessage(chatId, msg.id);
                }));
            } else {
                actions.appendChild(makeActionButton("Copy", function() {
                    navigator.clipboard.writeText(msg.text || "");
                }));
                actions.appendChild(makeActionButton("Retry", function() {
                    msgInput.value = lastUserPrompt || "";
                    resizeInput(msgInput);
                }));
                actions.appendChild(makeActionButton("Delete", function() {
                    deleteMessage(chatId, msg.id);
                }));
            }

            bubbleWrap.appendChild(actions);
            wrapper.appendChild(avatar);
            wrapper.appendChild(bubbleWrap);
            chatBox.appendChild(wrapper);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showTyping(label) {
            const div = document.createElement("div");
            div.id = "typing";
            div.className = "typing";
            div.innerHTML =
                '<div class="typing-card">' +
                '<div class="voice-wave"><span></span><span></span><span></span><span></span><span></span></div>' +
                '<div>' + label + '</div>' +
                '<div class="typing-beam"></div>' +
                '</div>';
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function removeTyping() {
            const el = document.getElementById("typing");
            if (el) el.remove();
        }

        function resizeInput(el) {
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight, 180) + "px";
        }

        function saveBehaviorPrefs() {
            localStorage.setItem("flux_bangla_first", String(document.getElementById("bangla-first").checked));
            localStorage.setItem("flux_memory_enabled", String(document.getElementById("memory-enabled").checked));
        }

        function loadBehaviorPrefs() {
            const answerLength = localStorage.getItem("flux_answer_length") || "balanced";
            const tone = localStorage.getItem("flux_tone") || "normal";
            document.getElementById("bangla-first").checked = (localStorage.getItem("flux_bangla_first") || "false") === "true";
            document.getElementById("memory-enabled").checked = (localStorage.getItem("flux_memory_enabled") || "true") === "true";
            updatePillGroup("len", answerLength);
            updatePillGroup("tone", tone);
        }

        function setAnswerLength(value) {
            localStorage.setItem("flux_answer_length", value);
            updatePillGroup("len", value);
        }

        function setTone(value) {
            localStorage.setItem("flux_tone", value);
            updatePillGroup("tone", value);
        }

        function updatePillGroup(prefix, activeValue) {
            const values = {
                len: ["short", "balanced", "detailed"],
                tone: ["normal", "friendly", "teacher", "coder"]
            };
            (values[prefix] || []).forEach(function(v) {
                const el = document.getElementById(prefix + "-" + v);
                if (!el) return;
                el.classList.toggle("active", v === activeValue);
            });
        }

        function setMode(mode) {
            responseMode = mode;
            localStorage.setItem("flux_response_mode", mode);
            ["smart", "study", "code", "search"].forEach(function(m) {
                const el = document.getElementById("mode-" + m);
                if (!el) return;
                el.classList.toggle("active", m === mode);
            });
        }

        function getBehaviorPrefs() {
            return {
                response_mode: responseMode,
                answer_length: localStorage.getItem("flux_answer_length") || "balanced",
                tone: localStorage.getItem("flux_tone") || "normal",
                bangla_first: String(document.getElementById("bangla-first").checked),
                memory_enabled: String(document.getElementById("memory-enabled").checked)
            };
        }

        function toggleSidebar() {
            sidebar.classList.toggle("open");
            sidebarOverlay.classList.toggle("show");
        }

        function closeSidebar() {
            sidebar.classList.remove("open");
            sidebarOverlay.classList.remove("show");
        }

        function toggleToolsSheet() {
            const isOpen = toolsSheet.classList.contains("open");
            if (isOpen) {
                closeToolsSheet();
            } else {
                toolsSheet.classList.add("open");
                sheetOverlay.classList.add("show");
            }
        }

        function closeToolsSheet() {
            toolsSheet.classList.remove("open");
            sheetOverlay.classList.remove("show");
        }

        function closeAdminModal() {
            document.getElementById("admin-modal").style.display = "none";
        }

        function closeAdminPanel() {
            document.getElementById("admin-panel-modal").style.display = "none";
        }

        async function verifyAdmin() {
            const pass = document.getElementById("admin-pass").value;
            try {
                const res = await fetch("/admin/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ password: pass })
                });
                if (!res.ok) throw new Error("Invalid");
                closeAdminModal();
                await refreshAdminPanel();
                document.getElementById("admin-panel-modal").style.display = "flex";
            } catch (e) {
                document.getElementById("admin-error").style.display = "block";
            }
        }

        async function refreshAdminPanel() {
            const statsRes = await fetch("/admin/stats");
            const stats = await statsRes.json();
            document.getElementById("stat-messages").textContent = stats.total_messages;
            document.getElementById("stat-uptime").textContent = stats.uptime;
            document.getElementById("stat-system").textContent = stats.active ? "ON" : "OFF";
            document.getElementById("stat-keys").textContent = stats.loaded_keys;
            document.getElementById("stat-analytics").textContent = stats.analytics_count;
            document.getElementById("stat-memory").textContent = stats.memory_count;
        }

        async function toggleSystemAdmin() {
            await fetch("/admin/toggle_system", { method: "POST" });
            await refreshAdminPanel();
        }

        async function resetMemoryAdmin() {
            await fetch("/admin/reset_memory", { method: "POST" });
            await refreshAdminPanel();
        }

        async function clearAnalyticsAdmin() {
            await fetch("/admin/clear_analytics", { method: "POST" });
            await refreshAdminPanel();
        }

        async function sendMessage() {
            const text = msgInput.value.trim();
            if (!text) return;

            if (text === "!admin") {
                msgInput.value = "";
                resizeInput(msgInput);
                document.getElementById("admin-modal").style.display = "flex";
                return;
            }

            closeSidebar();
            closeToolsSheet();

            if (!currentChatId) startNewChat();
            const chat = chats.find(function(c) { return c.id === currentChatId; });
            if (!chat) return;

            const userMsg = createMessage("user", text, []);
            chat.messages.push(userMsg);

            if (chat.messages.length === 1) {
                chat.title = text.substring(0, 28);
            }

            saveChats();
            renderHistory();

            lastUserPrompt = text;
            msgInput.value = "";
            resizeInput(msgInput);
            appendBubble(userMsg, chat.id);

            if (!userName && !awaitingName) {
                awaitingName = true;
                const botMsg = createMessage("assistant", "Hello! I am __APP_NAME__. What should I call you?", []);
                setTimeout(function() {
                    chat.messages.push(botMsg);
                    saveChats();
                    appendBubble(botMsg, chat.id);
                }, 300);
                return;
            }

            if (awaitingName) {
                userName = text;
                localStorage.setItem("flux_user_name_fixed", userName);
                awaitingName = false;
                const botMsg = createMessage("assistant", "Nice to meet you, " + userName + "! How can I help you today?", []);
                setTimeout(function() {
                    chat.messages.push(botMsg);
                    saveChats();
                    appendBubble(botMsg, chat.id);
                }, 300);
                return;
            }

            let typingText = "__APP_NAME__ is thinking...";
            if (responseMode === "study") typingText = "__APP_NAME__ is explaining step by step...";
            if (responseMode === "code") typingText = "__APP_NAME__ is building code...";
            if (responseMode === "search") typingText = "__APP_NAME__ is verifying trusted sources...";

            showTyping(typingText);
            document.body.classList.add("thinking");

            const context = chat.messages.slice(-12).map(function(m) {
                return { role: m.role === "assistant" ? "assistant" : "user", content: m.text };
            });

            try {
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        messages: context,
                        user_name: userName || "User",
                        preferences: getBehaviorPrefs()
                    })
                });

                removeTyping();
                document.body.classList.remove("thinking");

                const data = await res.json();
                const botMsg = createMessage("assistant", data.answer || "System error.", data.sources || []);
                chat.messages.push(botMsg);
                saveChats();
                appendBubble(botMsg, chat.id);
                renderHistory();
            } catch (e) {
                removeTyping();
                document.body.classList.remove("thinking");
                const errMsg = createMessage("assistant", "System connection error. Please try again.", []);
                chat.messages.push(errMsg);
                saveChats();
                appendBubble(errMsg, chat.id);
            }
        }

        msgInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        msgInput.addEventListener("focus", function() {
            inputBox.classList.add("focused");
        });

        msgInput.addEventListener("blur", function() {
            inputBox.classList.remove("focused");
        });

        initBackground();
        loadBehaviorPrefs();
        setMode(responseMode);
        applyVisualThemeSurface();
        updateThemeButtons();
        renderHomeCards();
        renderQuickChips();
        renderHistory();
        startSuggestionRotation();
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
    global TOTAL_MESSAGES

    if not SYSTEM_ACTIVE:
        return jsonify({"answer": "System is currently under maintenance.", "sources": []}), 503

    data = request.get_json(silent=True) or {}
    messages = sanitize_messages(data.get("messages", []))
    user_name = sanitize_text(data.get("user_name", "User"), 80) or "User"
    preferences = data.get("preferences", {}) if isinstance(data.get("preferences", {}), dict) else {}

    safe_preferences = {
        "response_mode": sanitize_text(preferences.get("response_mode", "smart"), 20).lower(),
        "answer_length": sanitize_text(preferences.get("answer_length", "balanced"), 20).lower(),
        "tone": sanitize_text(preferences.get("tone", "normal"), 20).lower(),
        "bangla_first": sanitize_text(preferences.get("bangla_first", "false"), 10).lower(),
        "memory_enabled": sanitize_text(preferences.get("memory_enabled", "true"), 10).lower()
    }

    if not messages:
        return jsonify({"answer": "No valid messages received.", "sources": []}), 400

    with TOTAL_MESSAGES_LOCK:
        TOTAL_MESSAGES += 1

    log_event("chat_request", {
        "user_name": user_name,
        "turns": len(messages),
        "latest_task_type": detect_task_type(messages[-1]["content"]) if messages else "unknown"
    })

    result = generate_answer(messages, user_name, safe_preferences)
    return jsonify(result)


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
        "memory_count": memory_count(),
        "loaded_keys": len(GROQ_KEYS),
    })


@app.route("/admin/toggle_system", methods=["POST"])
@admin_required
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    return jsonify({"ok": True, "active": SYSTEM_ACTIVE})


@app.route("/admin/reset_memory", methods=["POST"])
@admin_required
def reset_memory():
    conn = db_connect()
    conn.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    save_memory("app_name", APP_NAME)
    save_memory("owner_name", OWNER_NAME)
    return jsonify({"ok": True})


@app.route("/admin/clear_analytics", methods=["POST"])
@admin_required
def clear_admin_analytics():
    clear_analytics()
    return jsonify({"ok": True})


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
        "tavily_enabled": bool(TAVILY_API_KEY)
    })


@app.route("/debug/tavily")
def debug_tavily():
    query = request.args.get("q", "current prime minister of bangladesh")
    results = tavily_search(query, max_results=8, current_only=True)
    return jsonify({
        "query": query,
        "results_count": len(results),
        "results": results
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)