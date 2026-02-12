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
# 🔹 Flux AI (Ultra Pro UI - Build 20.0) 🚀
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "Kawchur"
OWNER_NAME_BN = "কাওছুর"
VERSION = "20.0.0"
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

# 🧮 INTELLIGENT MATH ENGINE (STABLE)
def solve_math_problem(text):
    try:
        clean_text = text.replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
        allowed_chars = set("0123456789.+-*/()xX÷^")
        if not set(clean_text).issubset(allowed_chars): return None
        if len(clean_text) < 3 or not any(op in clean_text for op in ['+', '-', '*', '/', 'x', '÷', '^']): return None
        expression = clean_text.replace("x", "*").replace("X", "*").replace("÷", "/").replace("^", "**")
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if isinstance(result, (int, float)):
            if result == int(result): return f"{int(result):,}"
            return f"{result:,.4f}"
        return None
    except: return None

SUGGESTION_POOL = [
    {"icon": "fa-solid fa-wand-magic-sparkles", "text": "Write a creative story"},
    {"icon": "fa-brands fa-python", "text": "Python code for a bot"},
    {"icon": "fa-solid fa-atom", "text": "Explain Black Holes"},
    {"icon": "fa-solid fa-utensils", "text": "Easy pasta recipe"},
    {"icon": "fa-solid fa-envelope", "text": "Write a formal email"},
    {"icon": "fa-solid fa-calculator", "text": "Solve 8292 * 8296"},
    {"icon": "fa-solid fa-image", "text": "Generate an AI image"},
    {"icon": "fa-solid fa-lightbulb", "text": "Business ideas for students"}
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
        <title>{APP_NAME} | Cyberpunk Pro</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Outfit:wght@300;400;500;600&family=Noto+Sans+Bengali:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg-dark: #050510;
                --bg-gradient: linear-gradient(135deg, #050510 0%, #1a1a2e 50%, #0f0c29 100%);
                --neon-blue: #00f3ff;
                --neon-purple: #bc13fe;
                --neon-pink: #ff0055;
                
                /* Glassmorphism Variables */
                --glass-bg: rgba(20, 20, 35, 0.7);
                --glass-border: rgba(255, 255, 255, 0.1);
                --glass-blur: blur(25px);
                
                --text-main: #e0e0e0;
                --text-muted: #94a3b8;
                --font-tech: 'Orbitron', sans-serif;
                --font-main: 'Outfit', 'Noto Sans Bengali', sans-serif;
            }}

            * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
            
            body {{
                margin: 0; 
                background: var(--bg-gradient);
                background-attachment: fixed;
                color: var(--text-main);
                font-family: var(--font-main);
                height: 100vh; 
                display: flex; 
                overflow: hidden;
            }}

            /* --- SIDEBAR --- */
            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                background: var(--glass-bg); 
                backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
                border-right: 1px solid var(--glass-border); padding: 20px;
                position: fixed; top: 0; left: 0; z-index: 100; 
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 10px 0 40px rgba(0,0,0,0.6);
            }}
            
            /* Sidebar hidden logic */
            #sidebar.closed {{ transform: translateX(-105%); }}
            
            /* Desktop Override: Always show unless explicitly toggled (optional, but sticking to mobile-first logic here) */
            @media (min-width: 769px) {{
                #sidebar {{ position: relative; transform: translateX(0); box-shadow: none; background: rgba(5, 5, 16, 0.4); }}
                #sidebar.closed {{ transform: translateX(-105%); margin-right: -280px; }}
            }}

            .brand-logo {{
                font-family: var(--font-tech);
                font-size: 1.8rem; font-weight: 700; margin-bottom: 25px;
                color: white; text-transform: uppercase; letter-spacing: 2px;
                display: flex; align-items: center; gap: 12px;
            }}
            
            /* Gradient Lightning Icon */
            .logo-icon {{
                background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                filter: drop-shadow(0 0 10px var(--neon-purple));
                font-size: 2rem;
            }}

            .new-chat-btn {{
                width: 100%; padding: 14px; border-radius: 8px; 
                border: 1px solid var(--neon-blue);
                background: rgba(0, 243, 255, 0.08);
                color: var(--neon-blue); font-family: var(--font-tech);
                font-weight: 600; cursor: pointer; margin-bottom: 25px;
                display: flex; align-items: center; justify-content: center; gap: 10px;
                transition: 0.3s; box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
            }}
            .new-chat-btn:hover {{ 
                background: var(--neon-blue); color: #000; 
                box-shadow: 0 0 25px var(--neon-blue); transform: translateY(-2px);
            }}

            .section-title {{
                font-size: 0.7rem; font-weight: 700; color: var(--text-muted);
                margin: 15px 0 8px 0; letter-spacing: 1.5px; font-family: var(--font-tech);
                border-bottom: 1px solid var(--glass-border); padding-bottom: 5px;
            }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; margin-bottom: 10px; }}
            .menu-item {{
                padding: 10px 12px; border-radius: 6px; color: #cbd5e1; cursor: pointer;
                font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                transition: 0.2s; display: flex; align-items: center; gap: 10px;
            }}
            .menu-item:hover {{ background: rgba(255,255,255,0.08); color: white; padding-left: 15px; }}
            .menu-item i {{ width: 20px; text-align: center; color: var(--neon-purple); }}

            .menu-item.danger {{ color: var(--neon-pink); margin-top: 10px; border: 1px solid rgba(255, 0, 85, 0.2); }}
            .menu-item.danger:hover {{ background: rgba(255, 0, 85, 0.1); border-color: var(--neon-pink); }}
            .menu-item.danger i {{ color: var(--neon-pink); }}

            .version-tag {{
                font-size: 0.75rem; color: var(--text-muted); padding: 5px 12px; 
                background: rgba(0,0,0,0.2); border-radius: 4px; margin-bottom: 5px;
                display: inline-block; font-family: monospace;
            }}

            /* --- MAIN AREA --- */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; transition: margin 0.3s; }}
            
            header {{
                height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(5, 5, 16, 0.6); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--glass-border); z-index: 50;
            }}
            
            #chat-box {{ flex: 1; overflow-y: auto; padding: 20px 20px 140px 20px; scroll-behavior: smooth; }}

            /* --- WELCOME --- */
            .welcome-container {{
                height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
                text-align: center; padding-bottom: 60px;
            }}
            .logo-big {{
                font-size: 5rem; margin-bottom: 10px;
                background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
                -webkit-background-clip: text; color: transparent;
                filter: drop-shadow(0 0 20px rgba(188, 19, 254, 0.6));
                animation: pulseGlow 3s infinite alternate;
            }}
            .welcome-title {{ 
                font-family: var(--font-tech); font-size: 2.5rem; font-weight: 700; margin: 0; 
                color: white; letter-spacing: 1px;
            }}
            
            .suggestions-grid {{
                display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px;
                width: 100%; max-width: 800px; margin-top: 40px;
                animation: fadeInUp 0.8s ease-out backwards;
            }}
            .suggestion-card {{
                background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); padding: 15px;
                border-radius: 12px; cursor: pointer; text-align: left; transition: 0.3s;
                display: flex; flex-direction: column; gap: 10px;
            }}
            .suggestion-card:hover {{ 
                background: rgba(255,255,255,0.08); border-color: var(--neon-blue);
                transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.4);
            }}
            .suggestion-card i {{ color: var(--neon-blue); }}

            /* --- MESSAGES --- */
            .message-wrapper {{ display: flex; gap: 16px; max-width: 850px; margin: 0 auto 24px auto; animation: popIn 0.3s ease; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{
                width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
                flex-shrink: 0; font-size: 1.1rem; border: 1px solid var(--glass-border);
            }}
            .bot-avatar {{ background: rgba(0, 243, 255, 0.1); color: var(--neon-blue); box-shadow: 0 0 10px rgba(0,243,255,0.2); }}
            .user-avatar {{ background: rgba(188, 19, 254, 0.1); color: var(--neon-purple); }}

            .bubble {{
                padding: 14px 20px; border-radius: 12px; font-size: 1rem; line-height: 1.6;
                color: #e2e8f0; max-width: 100%; overflow-wrap: break-word;
                background: rgba(30, 30, 50, 0.6); border: 1px solid var(--glass-border);
                backdrop-filter: blur(5px);
            }}
            .user .bubble {{ 
                background: rgba(188, 19, 254, 0.15); border-color: rgba(188, 19, 254, 0.3);
                border-radius: 12px 2px 12px 12px;
            }}
            .bot .bubble {{ 
                background: rgba(0, 243, 255, 0.05); border-color: rgba(0, 243, 255, 0.2);
                border-radius: 2px 12px 12px 12px;
            }}
            pre {{ background: #0b0b14 !important; padding: 15px; border-radius: 8px; border: 1px solid #333; }}

            /* --- INPUT --- */
            #input-container {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, #050510 85%, transparent);
                display: flex; justify-content: center; z-index: 60;
            }}
            .input-box {{
                width: 100%; max-width: 850px; background: rgba(20, 20, 40, 0.8);
                backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px; padding: 8px 8px 8px 20px; display: flex; align-items: flex-end;
                box-shadow: 0 0 30px rgba(0,0,0,0.5); transition: 0.3s;
            }}
            .input-box:focus-within {{ border-color: var(--neon-blue); box-shadow: 0 0 20px rgba(0, 243, 255, 0.1); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; color: white;
                font-size: 1rem; font-family: inherit; resize: none; max-height: 150px;
                padding: 12px 0; outline: none;
            }}
            .send-btn {{
                width: 42px; height: 42px; border-radius: 10px; border: none;
                background: var(--neon-blue); color: #000; font-size: 1.2rem; cursor: pointer; margin-left: 10px;
                transition: 0.3s; display: flex; align-items: center; justify-content: center;
            }}
            .send-btn:hover {{ background: white; box-shadow: 0 0 15px white; }}

            /* Animations */
            @keyframes pulseGlow {{ 0% {{ filter: drop-shadow(0 0 10px var(--neon-purple)); }} 100% {{ filter: drop-shadow(0 0 25px var(--neon-blue)); }} }}
            @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
            
            .typing span {{
                width: 6px; height: 6px; background: var(--text-muted); border-radius: 50%;
                display: inline-block; animation: bounce 1.4s infinite; margin: 0 2px;
            }}
            .typing span:nth-child(2) {{ animation-delay: 0.2s; }}
            .typing span:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}

            /* Mobile Specific */
            @media (max-width: 768px) {{
                #sidebar {{ transform: translateX(-105%); width: 85%; max-width: 320px; }}
                #sidebar.closed {{ transform: translateX(-105%); }} /* Default closed */
                #sidebar.open {{ transform: translateX(0); }} /* Class to open */
                .welcome-title {{ font-size: 2rem; }}
                .suggestions-grid {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
    </head>
    <body>
        
        <div class="overlay" onclick="toggleSidebar()" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); backdrop-filter:blur(3px); z-index:90;"></div>

        <div id="sidebar" class="closed">
            <div class="brand-logo">
                <i class="fa-solid fa-bolt logo-icon"></i> 
                {APP_NAME}
            </div>
            
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fa-solid fa-plus"></i> New Mission
            </button>
            
            <div class="section-title">MEMORY LOGS</div>
            <div class="history-list" id="history-list"></div>
            
            <div style="margin-top:auto;">
                <div class="section-title">ABOUT</div>
                <div class="version-tag">Version: {VERSION}</div>
                <div class="menu-item" onclick="window.open('{WEBSITE_URL}', '_blank')">
                    <i class="fa-solid fa-globe"></i> Website
                </div>
                <div class="menu-item" onclick="window.open('{FACEBOOK_URL}', '_blank')">
                    <i class="fa-brands fa-facebook"></i> Developer
                </div>
                
                <div style="height:1px; background:var(--glass-border); margin:10px 0;"></div>

                <div class="menu-item danger" onclick="confirmDelete()">
                    <i class="fa-solid fa-trash-can"></i> Purge Data
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:white; font-size:1.4rem; cursor:pointer;"><i class="fa-solid fa-bars-staggered"></i></button>
                <div style="font-weight:700; font-size:1.2rem; letter-spacing:1px; font-family:var(--font-tech); color:white;">{APP_NAME}</div>
                <button onclick="startNewChat()" style="background:none; border:none; color:white; font-size:1.3rem; cursor:pointer;"><i class="fa-regular fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="logo-big"><i class="fa-solid fa-bolt"></i></div>
                    <h1 class="welcome-title">SYSTEM ONLINE</h1>
                    <p style="color:var(--text-muted); margin-top:10px;">Awaiting command, {OWNER_NAME}.</p>
                    
                    <div class="suggestions-grid" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-container">
                <div class="input-box">
                    <textarea id="msg" placeholder="Enter command..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fa-solid fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v20_history')) || [];
            let currentChatId = null;
            
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            renderHistory();
            renderSuggestions();

            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            
            // Fixed Toggle Logic
            function toggleSidebar() {{
                const isMobile = window.innerWidth <= 768;
                if (isMobile) {{
                    sidebar.classList.toggle('open');
                    const isOpen = sidebar.classList.contains('open');
                    overlay.style.display = isOpen ? 'block' : 'none';
                }} else {{
                    sidebar.classList.toggle('closed');
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
                chats.unshift({{ id: currentChatId, title: "New Session", messages: [] }});
                saveData();
                renderHistory();
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                // Close sidebar on mobile when starting new chat
                if(window.innerWidth <= 768) {{ sidebar.classList.remove('open'); overlay.style.display = 'none'; }}
                msgInput.value = '';
            }}

            function saveData() {{ localStorage.setItem('flux_v20_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'menu-item';
                    div.innerHTML = `<i class="fa-regular fa-comment-dots"></i> ${{chat.title.substring(0, 20)}}`;
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
                if(window.innerWidth <= 768) {{ sidebar.classList.remove('open'); overlay.style.display = 'none'; }}
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}"><i class="${{isUser ? 'fa-solid fa-user-astronaut' : 'fa-solid fa-bolt'}}"></i></div>`;
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
                if(confirm("Confirm system purge? This cannot be undone.")) {{
                    localStorage.removeItem('flux_v20_history');
                    location.reload();
                }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

# 🛡️ SYSTEM ROUTES
@app.route("/admin/stats")
def admin_stats(): return jsonify({"uptime": get_uptime(), "total_messages": TOTAL_MESSAGES, "active": SYSTEM_ACTIVE})

@app.route("/admin/toggle_system", methods=["POST"])
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    return jsonify({"active": SYSTEM_ACTIVE})

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
        "content": f"""You are {APP_NAME}, a helpful AI assistant created by {OWNER_NAME}.
        Time: {ctx['time_local']}.
        Identity: Be friendly, professional, and concise.
        Rules: No markdown in math answers unless necessary."""
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
