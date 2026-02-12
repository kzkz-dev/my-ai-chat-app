from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import re
import math

# ==========================================
# 🔹 Flux AI (Professional UI - Build 19.0) 🎨
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"
VERSION = "19.0.0"
ADMIN_PASSWORD = "7rx9x2c0"

# Links
FACEBOOK_URL = "https://www.facebook.com/share/1CBWMUaou9/"
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"

# Stats
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True

app = Flask(__name__)
app.secret_key = os.urandom(24)

GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found.")

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS: return None
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_uptime():
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return str(timedelta(seconds=uptime_seconds))

def get_current_context():
    tz_dhaka = pytz.timezone('Asia/Dhaka')
    now_dhaka = datetime.now(tz_dhaka)
    now_utc = datetime.now(pytz.utc)
    return {
        "time_utc": now_utc.strftime("%I:%M %p"),
        "time_local": now_dhaka.strftime("%I:%M %p"),
        "date": now_dhaka.strftime("%d %B, %Y (%A)"),
        "year": now_dhaka.year
    }

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
    {"icon": "fa-regular fa-envelope", "text": "Draft a professional email"},
    {"icon": "fa-brands fa-python", "text": "Write a Python script"},
    {"icon": "fa-solid fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fa-solid fa-dumbbell", "text": "30-minute workout plan"},
    {"icon": "fa-solid fa-utensils", "text": "Healthy dinner recipe"},
    {"icon": "fa-solid fa-plane-departure", "text": "Trip to Cox's Bazar"},
    {"icon": "fa-solid fa-lightbulb", "text": "Startup business ideas"},
    {"icon": "fa-solid fa-code", "text": "Explain HTML & CSS"},
    {"icon": "fa-solid fa-music", "text": "Write a song lyric"},
    {"icon": "fa-solid fa-camera", "text": "Photography tips"},
    {"icon": "fa-solid fa-palette", "text": "Generate an image"},
    {"icon": "fa-solid fa-calculator", "text": "Solve 282 * 8201"}
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
        <title>{APP_NAME} | Next Gen AI</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg-color: #020617;
                --sidebar-bg: rgba(15, 23, 42, 0.6);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
                --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
                --input-bg: rgba(30, 41, 59, 0.7);
                --msg-user-bg: #1e293b;
                --msg-bot-bg: transparent;
                --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.15);
            }}

            * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
            body {{
                margin: 0; background-color: var(--bg-color); color: var(--text-primary);
                font-family: 'Plus Jakarta Sans', 'Noto Sans Bengali', sans-serif;
                height: 100vh; display: flex; overflow: hidden;
                background-image: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
                                  radial-gradient(circle at 85% 30%, rgba(217, 70, 239, 0.08), transparent 25%);
            }}

            /* --- SIDEBAR (GLASSMORPHISM) --- */
            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                background: var(--sidebar-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                border-right: 1px solid var(--glass-border); padding: 20px;
                position: absolute; z-index: 100; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            #sidebar.closed {{ transform: translateX(-105%); }}

            .brand {{
                font-size: 1.6rem; font-weight: 800; margin-bottom: 30px; letter-spacing: -0.5px;
                background: var(--accent-gradient); -webkit-background-clip: text; color: transparent;
                display: flex; align-items: center; gap: 10px;
            }}
            
            .new-chat-btn {{
                width: 100%; padding: 14px; border-radius: 12px; border: 1px solid var(--glass-border);
                background: rgba(255,255,255,0.03); color: white; font-weight: 600; cursor: pointer;
                transition: all 0.3s; display: flex; align-items: center; gap: 10px; margin-bottom: 20px;
            }}
            .new-chat-btn:hover {{ background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }}
            .history-item {{
                padding: 10px 14px; border-radius: 8px; color: var(--text-secondary); cursor: pointer;
                font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                transition: 0.2s; display: flex; align-items: center; gap: 10px;
            }}
            .history-item:hover {{ background: rgba(255,255,255,0.05); color: var(--text-primary); }}

            /* --- MAIN CHAT AREA --- */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100%; }}
            
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(2, 6, 23, 0.8); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--glass-border); z-index: 50;
            }}
            .header-title {{ font-weight: 700; font-size: 1.1rem; opacity: 0.9; }}

            #chat-box {{ flex: 1; overflow-y: auto; padding: 20px 20px 140px 20px; scroll-behavior: smooth; }}

            /* --- WELCOME SCREEN --- */
            .welcome-container {{
                height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
                text-align: center; padding-bottom: 80px; animation: fadeIn 0.8s ease;
            }}
            .logo-large {{
                font-size: 3.5rem; margin-bottom: 10px; 
                background: var(--accent-gradient); -webkit-background-clip: text; color: transparent;
                filter: drop-shadow(0 0 30px rgba(139, 92, 246, 0.4));
            }}
            .welcome-text {{ font-size: 2.2rem; font-weight: 700; margin: 0; line-height: 1.2; }}
            .welcome-sub {{ color: var(--text-secondary); margin-top: 10px; font-size: 1.1rem; max-width: 500px; }}

            .suggestions-grid {{
                display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px;
                width: 100%; max-width: 800px; margin-top: 40px;
            }}
            .suggestion-card {{
                background: rgba(30, 41, 59, 0.4); border: 1px solid var(--glass-border); padding: 15px;
                border-radius: 16px; cursor: pointer; text-align: left; transition: all 0.3s;
                display: flex; flex-direction: column; gap: 8px;
            }}
            .suggestion-card:hover {{ transform: translateY(-5px); background: rgba(30, 41, 59, 0.8); border-color: #8b5cf6; }}
            .suggestion-card i {{ color: #a78bfa; font-size: 1.2rem; }}
            .suggestion-card span {{ font-size: 0.9rem; color: var(--text-secondary); font-weight: 500; }}

            /* --- MESSAGES --- */
            .message-wrapper {{ display: flex; gap: 16px; max-width: 850px; margin: 0 auto 24px auto; animation: slideUp 0.3s ease; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{
                width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
                flex-shrink: 0; font-size: 1.1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}
            .bot-avatar {{ background: linear-gradient(135deg, #4f46e5, #9333ea); color: white; }}
            .user-avatar {{ background: #334155; color: #e2e8f0; }}

            .bubble {{
                padding: 12px 18px; border-radius: 18px; font-size: 1rem; line-height: 1.6;
                color: var(--text-primary); max-width: 100%; overflow-wrap: break-word;
            }}
            .user .bubble {{ background: var(--msg-user-bg); border-radius: 18px 4px 18px 18px; }}
            .bot .bubble {{ background: transparent; padding: 0; margin-top: 5px; }}
            
            .bubble strong {{ color: #c4b5fd; font-weight: 700; }}
            .bubble code {{ background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-family: 'Fira Code', monospace; font-size: 0.9em; color: #f472b6; }}
            pre {{ background: #0d1117 !important; padding: 15px; border-radius: 12px; overflow-x: auto; border: 1px solid var(--glass-border); }}

            /* --- INPUT AREA --- */
            #input-container {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg-color) 70%, transparent);
                display: flex; justify-content: center;
            }}
            .input-box {{
                width: 100%; max-width: 850px; background: var(--input-bg);
                backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border); border-radius: 24px;
                padding: 10px 10px 10px 20px; display: flex; align-items: flex-end;
                box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5); transition: 0.3s;
            }}
            .input-box:focus-within {{ border-color: #8b5cf6; box-shadow: 0 10px 40px -5px rgba(139, 92, 246, 0.2); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; color: white;
                font-size: 1rem; font-family: inherit; resize: none; max-height: 150px;
                padding: 12px 0; outline: none;
            }}
            .send-btn {{
                width: 44px; height: 44px; border-radius: 50%; border: none;
                background: var(--text-primary); color: var(--bg-color);
                font-size: 1.1rem; cursor: pointer; margin-left: 10px; margin-bottom: 2px;
                transition: 0.2s; display: flex; align-items: center; justify-content: center;
            }}
            .send-btn:hover {{ transform: scale(1.05) rotate(-10deg); background: #8b5cf6; color: white; }}

            /* --- ANIMATIONS --- */
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .typing span {{
                display: inline-block; width: 6px; height: 6px; background: #94a3b8;
                border-radius: 50%; margin-right: 4px; animation: bounce 1.4s infinite;
            }}
            .typing span:nth-child(2) {{ animation-delay: 0.2s; }}
            .typing span:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}

            /* Mobile Responsive */
            @media (max-width: 768px) {{
                #sidebar {{ transform: translateX(-105%); box-shadow: none; }}
                #sidebar.closed {{ transform: translateX(0); box-shadow: 10px 0 30px rgba(0,0,0,0.5); }}
                .welcome-text {{ font-size: 1.8rem; }}
                .logo-large {{ font-size: 2.8rem; }}
                .suggestions-grid {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
    </head>
    <body>
        
        <div class="overlay" onclick="toggleSidebar()" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:90;"></div>

        <div id="sidebar" class="closed">
            <div class="brand"><i class="fa-solid fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fa-solid fa-plus"></i> New Chat
            </button>
            <div style="font-size:0.75rem; font-weight:700; color:#475569; margin-bottom:10px; letter-spacing:1px;">HISTORY</div>
            <div class="history-list" id="history-list"></div>
            
            <div style="margin-top:auto; border-top:1px solid var(--glass-border); padding-top:15px;">
                <div class="history-item" onclick="window.open('{WEBSITE_URL}', '_blank')"><i class="fa-solid fa-globe"></i> Website</div>
                <div class="history-item" onclick="window.open('{FACEBOOK_URL}', '_blank')"><i class="fa-brands fa-facebook"></i> Developer</div>
                <div class="history-item" onclick="confirmDelete()" style="color:#ef4444;"><i class="fa-solid fa-trash"></i> Clear Data</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:white; font-size:1.2rem; cursor:pointer; padding:8px;"><i class="fa-solid fa-bars"></i></button>
                <div class="header-title">{APP_NAME} <span style="font-size:0.7rem; background:#334155; padding:2px 6px; border-radius:4px; margin-left:5px;">v{VERSION}</span></div>
                <button onclick="startNewChat()" style="background:none; border:none; color:white; font-size:1.2rem; cursor:pointer; padding:8px;"><i class="fa-regular fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="logo-large"><i class="fa-solid fa-bolt-lightning"></i></div>
                    <h1 class="welcome-text">Hello, I'm {APP_NAME}</h1>
                    <p class="welcome-sub">Your intelligent companion powered by advanced AI.</p>
                    
                    <div class="suggestions-grid" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-container">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask anything..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v19_history')) || [];
            let currentChatId = null;
            
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            renderHistory();
            renderSuggestions();

            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            
            function toggleSidebar() {{
                sidebar.classList.toggle('closed');
                // Mobile overlay logic
                if (window.innerWidth <= 768) {{
                    overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block';
                }} else {{
                    overlay.style.display = 'none';
                }}
            }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{
                    html += `<div class="suggestion-card" onclick="sendSuggestion('${{s.text}}')"><i class="${{s.icon}}"></i><span>${{s.text}}</span></div>`;
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData();
                renderHistory();
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                if(window.innerWidth <= 768) {{ sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
                msgInput.value = '';
            }}

            function saveData() {{ localStorage.setItem('flux_v19_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<i class="fa-regular fa-message"></i> ${{chat.title.substring(0, 20)}}`;
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;
                chatBox.innerHTML = '';
                if(chat.messages.length === 0) {{
                    chatBox.appendChild(welcomeScreen);
                    welcomeScreen.style.display = 'flex';
                }} else {{
                    welcomeScreen.style.display = 'none';
                    chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                }}
                if(window.innerWidth <= 768) {{ sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}"><i class="${{isUser ? 'fa-regular fa-user' : 'fa-solid fa-bolt'}}"></i></div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="bubble">${{marked.parse(text)}}</div></div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
                if(!isUser) hljs.highlightAll();
            }}

            function showTyping() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fa-solid fa-bolt"></i></div><div class="bubble-container"><div class="bubble typing"><span></span><span></span><span></span></div></div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{ document.getElementById('typing')?.remove(); }}
            
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;
                
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text; renderHistory(); }}
                
                msgInput.value = '';
                resizeInput(msgInput);
                appendBubble(text, true);
                saveData();
                showTyping();

                const context = chat.messages.slice(-8).map(m => ({{ role: m.role, content: m.text }}));

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    removeTyping();
                    if(!res.ok) throw new Error("Offline");
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fa-solid fa-bolt"></i></div><div class="bubble-container"><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper);
                    const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    hljs.highlightAll();

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Connection Error. Please try again.", false);
                }}
            }}
            
            function confirmDelete() {{
                if(confirm("Delete all history?")) {{
                    localStorage.removeItem('flux_v19_history');
                    location.reload();
                }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

# 🛡️ ADMIN & CHAT ROUTES (SAME LOGIC)
@app.route("/admin/stats")
def admin_stats(): return jsonify({{ "uptime": get_uptime(), "total_messages": TOTAL_MESSAGES, "active": SYSTEM_ACTIVE }})

@app.route("/admin/toggle_system", methods=["POST"])
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    return jsonify({{"active": SYSTEM_ACTIVE}})

@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES
    if not SYSTEM_ACTIVE: return Response("Maintenance Mode", status=503)

    TOTAL_MESSAGES += 1
    data = request.json
    messages = data.get("messages", [])
    
    # Math Engine
    if messages and messages[-1]['role'] == 'user':
        math_result = solve_math_problem(messages[-1]['content'])
        if math_result:
            system_note = {
                "role": "system",
                "content": f"TOOL: Math calculated result is: {math_result}. Just say the answer directly."
            }
            messages.insert(-1, system_note)

    ctx = get_current_context()
    sys_prompt = {
        "role": "system",
        "content": f"""You are {APP_NAME}, a helpful AI assistant.
        Developer: {OWNER_NAME} ({OWNER_NAME_BN}).
        Time: {ctx['time_local']}.
        Be concise, friendly, and smart."""
    }

    def generate():
        global current_key_index
        attempts = 0
        while attempts < (len(GROQ_KEYS) + 1):
            try:
                client = get_groq_client()
                if not client: yield "Server Error"; return
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[sys_prompt] + messages,
                    stream=True, temperature=0.7, max_tokens=1024
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
                return
            except:
                current_key_index += 1
                attempts += 1
        yield "System Overloaded. Try later."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
