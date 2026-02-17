from flask import Flask, request, Response, jsonify
from groq import Groq
from duckduckgo_search import DDGS
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import re
import math
import base64

# ==========================================
# 🔹 Flux AI (Brain Upgrade - Build 31.0.0) 🧠
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "31.0.0"
ADMIN_PASSWORD = "7rx9x2c0" 

# Stats
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True 

app = Flask(__name__)
app.secret_key = os.urandom(24)

GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS: return None
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_current_context(): 
    tz_dhaka = pytz.timezone('Asia/Dhaka')
    now_dhaka = datetime.now(tz_dhaka)
    return {
        "time_local": now_dhaka.strftime("%I:%M %p"),
        "date": now_dhaka.strftime("%d %B, %Y"),
        "day": now_dhaka.strftime("%A")
    }

# 🌐 WEB SEARCH ENGINE
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return summary
        return None
    except:
        return None

# 🧮 MATH ENGINE
def solve_math_problem(text):
    try:
        clean_text = text.replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
        allowed_chars = set("0123456789.+-*/()xX÷^")
        if not set(clean_text).issubset(allowed_chars): return None
        if len(clean_text) < 3 or not any(op in clean_text for op in ['+', '-', '*', '/', 'x', '÷', '^']): return None
        expression = clean_text.replace("x", "*").replace("X", "*").replace("÷", "/").replace("^", "**")
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if result == int(result): return f"{int(result):,}" 
        return f"{result:,.4f}" 
    except: return None

SUGGESTION_POOL = [
    {"icon": "fas fa-globe", "text": "Who is the current Prime Minister of Bangladesh?"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"},
    {"icon": "fas fa-plane", "text": "Trip plan for Cox's Bazar"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-cloud-sun", "text": "Weather in Dhaka today"},
    {"icon": "fas fa-laptop-code", "text": "Write a Python calculator"},
    {"icon": "fas fa-calculator", "text": "Solve: 50 * 3 + 20"}
]

@app.route("/")
def home():
    suggestions_json = json.dumps(SUGGESTION_POOL)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME}</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <style>
            :root {{ --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 10, 25) 0%, rgb(5, 5, 10) 90%); --sidebar-bg: rgba(15, 15, 30, 0.95); --text: #e0e6ed; --accent: #00f3ff; --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%); --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%); }}
            body.light {{ --bg-gradient: #f8fafc; --sidebar-bg: #ffffff; --text: #1e293b; --accent: #2563eb; --bot-grad: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%); --user-grad: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); }}
            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg-gradient); color: var(--text); font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; }}
            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid rgba(255,255,255,0.1); position: absolute; z-index: 200; left: 0; top: 0; background: var(--sidebar-bg); transition: transform 0.3s; }}
            #sidebar.closed {{ transform: translateX(-105%); }}
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }}
            .history-item {{ padding: 12px; border-radius: 12px; cursor: pointer; color: var(--text); font-size: 0.9rem; opacity: 0.8; display: flex; gap: 10px; }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); opacity: 1; }}
            .menu-section {{ margin-top: auto; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); }}
            .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text); opacity: 0.5; cursor: pointer; border-radius: 8px; }}
            .theme-btn.active {{ background: rgba(125,125,125,0.2); opacity: 1; }}
            
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; position: absolute; top: 0; left: 0; right: 0; z-index: 100; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; }}
            
            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 60px; }}
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; margin-top: 40px; }}
            .chip {{ padding: 16px 20px; background: rgba(125, 125, 125, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 18px; cursor: pointer; text-align: left; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; transition: 0.3s; }}
            .chip:hover {{ border-color: var(--accent); transform: translateY(-3px); }}
            .chip i {{ color: var(--accent); }}

            .message-wrapper {{ display: flex; gap: 16px; width: 100%; max-width: 850px; margin: 0 auto; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid rgba(255,255,255,0.1); }}
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; }}
            .user .bubble {{ background: var(--user-grad); color: white; border-radius: 20px 4px 20px 20px; }}
            
            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; gap: 8px; }}
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 26px; padding: 8px 8px 8px 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 12px 0; font-family: inherit; }}
            .action-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 5px; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; }}
            
            /* Speak Button */
            .speak-btn {{ background: rgba(125,125,125,0.15); color: var(--accent); border: 1px solid rgba(255,255,255,0.1); width: 30px; height: 30px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; margin-top: 5px; }}
            
            pre {{ background: #111 !important; padding: 15px; border-radius: 10px; overflow-x: auto; }}
            code {{ font-family: monospace; font-size: 0.9rem; color: #0f0; }}
            
            /* SEARCH BADGE */
            .search-badge {{ font-size: 0.75rem; background: rgba(0, 243, 255, 0.1); color: var(--accent); padding: 4px 8px; border-radius: 6px; margin-bottom: 8px; display: inline-block; font-weight: 600; border: 1px solid var(--accent); }}

            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
        </style>
    </head>
    <body class="dark">
        <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()"><i class="fas fa-plus"></i> New Chat</button>
            <div class="history-list" id="history-list"></div>
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i></button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i></button>
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.4rem; letter-spacing: -0.5px; background: linear-gradient(to right, var(--text), var(--text-secondary)); -webkit-background-clip: text; color: transparent;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div style="font-size:3.5rem; color:var(--accent); margin-bottom:20px;"><i class="fas fa-brain"></i></div>
                    <div style="font-size:2rem; font-weight:800; margin-bottom:10px;">Flux AI Brain 2.0</div>
                    <div style="color:gray;">Connected to the Internet. Smarter than ever.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask anything (e.g. Current news)..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                    <button class="action-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v31_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{
                    // 🔥 FIX: Escaping quotes for suggestions
                    const safeText = s.text.replace(/'/g, "\\'");
                    html += `<div class="chip" onclick="sendSuggestion('${{safeText}}')"><i class="${{s.icon}}"></i> ${{s.text}}</div>`;
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Chat", messages: [] }});
                saveData(); renderHistory(); renderSuggestions();
                chatBox.innerHTML = ''; chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}
            function saveData() {{ localStorage.setItem('flux_v31_history', JSON.stringify(chats)); }}
            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Chat').substring(0, 20) + '</span>';
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}
            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', msg.isSearch));
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            function speak(text) {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(text.replace(/[*`]/g, ''));
                u.lang = 'en-US'; window.speechSynthesis.speak(u);
            }}

            function appendBubble(text, isUser, isSearch=false) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                
                let contentHTML = `<div class="bubble-container">`;
                if(isSearch) contentHTML += `<div class="search-badge"><i class="fas fa-globe"></i> Searched Web</div>`;
                contentHTML += `<div class="bubble"></div>`;
                if(!isUser) contentHTML += `<button class="speak-btn" onclick="speak(\`${{text.replace(/"/g, '&quot;').replace(/`/g, '')}}\`)"><i class="fas fa-volume-up"></i></button>`;
                contentHTML += `</div>`;

                wrapper.innerHTML = `${{avatar}}${{contentHTML}}`;
                chatBox.appendChild(wrapper);
                wrapper.querySelector('.bubble').innerHTML = marked.parse(text);
                if(!isUser) hljs.highlightAll();
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData(); msgInput.value = ''; appendBubble(text, true);

                const context = chat.messages.slice(-6).map(m => ({{ role: m.role, content: m.text }}));
                
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context, user_name: localStorage.getItem('flux_user_name_v2') }}) }});
                    const data = await res.json();
                    appendBubble(data.reply, false, data.searched);
                    chat.messages.push({{ role: 'assistant', text: data.reply, isSearch: data.searched }});
                    saveData();
                }} catch(e) {{ appendBubble("⚠️ Network Error", false); }}
            }}
            
            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
            renderHistory(); renderSuggestions();
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    user_name = data.get("user_name", "User")
    last_msg = messages[-1]['content'] if messages else ""

    # 1. MATH CHECK
    math_res = solve_math_problem(last_msg)
    if math_res:
        return jsonify({"reply": f"The answer is: **{math_res}**", "searched": False})

    # 2. INTERNET SEARCH CHECK (Smart Detection)
    # If question asks about current events, news, weather, or specific people
    search_keywords = ["current", "latest", "news", "weather", "today", "price", "who is", "what is", "prime minister", "president", "score"]
    searched = False
    search_context = ""
    
    if any(k in last_msg.lower() for k in search_keywords) or "?" in last_msg:
        print(f"🔎 Searching for: {last_msg}")
        web_result = search_web(last_msg)
        if web_result:
            searched = True
            search_context = f"\n\n[REAL-TIME WEB SEARCH RESULTS]:\n{web_result}\n(Use this info to answer)"

    ctx = get_current_context()
    sys_prompt = f"""
    You are {APP_NAME}, a smart AI assistant.
    - Owner: {OWNER_NAME}
    - User: {user_name}
    - Time: {ctx['time_local']}, {ctx['date']} ({ctx['day']})
    {search_context}
    
    Rules:
    1. If search results are provided, USE THEM.
    2. Be concise and helpful.
    """

    try:
        client = get_groq_client()
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            temperature=0.7
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply, "searched": searched})
    except Exception as e:
        return jsonify({"reply": "⚠️ Brain Overload. Try again.", "searched": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
