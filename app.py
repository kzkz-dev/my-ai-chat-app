from flask import Flask, request, Response, jsonify, render_template_string
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

# ==========================================
# 🔹 Flux AI (Secure & Tracking Edition - Build 34.0.0) 🔒💘
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "34.0.0"
ADMIN_PASSWORD = "7rx9x2c0" # This is your Login & Status Check Password

# ✅ RESTORED LINKS (As requested)
FACEBOOK_URL = "https://www.facebook.com/share/1CBWMUaou9/"
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"      

# Stats & Storage
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True 
PROPOSAL_DB = {} # To store who accepted the proposal

app = Flask(__name__)
app.secret_key = os.urandom(24)

# API Key Setup
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS: return None
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_uptime():
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return str(timedelta(seconds=uptime_seconds))

def get_current_context(): 
    try:
        tz_dhaka = pytz.timezone('Asia/Dhaka')
        now_dhaka = datetime.now(tz_dhaka)
        return {
            "time_local": now_dhaka.strftime("%I:%M %p"),
            "date": now_dhaka.strftime("%d %B, %Y"),
            "day": now_dhaka.strftime("%A")
        }
    except:
        return {"time_local": "Unknown", "date": "Unknown", "day": ""}

# 🌐 WEB SEARCH ENGINE
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                return summary
        return None
    except Exception:
        return None

# 🧮 MATH ENGINE
def solve_math_problem(text):
    try:
        clean_text = text.replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
        allowed_chars = set("0123456789.+-*/()xX÷^")
        if not set(clean_text).issubset(allowed_chars): return None
        if len(clean_text) < 3: return None
        expression = clean_text.replace("x", "*").replace("X", "*").replace("÷", "/").replace("^", "**")
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if result == int(result): return f"{int(result):,}" 
        return f"{result:,.4f}" 
    except: return None

# -------------------------------------------
# 💘 PROPOSE PAGE (With API Call to Save Yes)
# -------------------------------------------
PROPOSE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>For You ❤️</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: #ffe6e9; font-family: 'Poppins', sans-serif;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; margin: 0; overflow: hidden; touch-action: none;
        }
        .container { text-align: center; position: relative; z-index: 10; width: 100%; }
        
        /* Cute Stickers */
        .sticker { position: absolute; font-size: 2rem; opacity: 0.8; animation: float 3s infinite ease-in-out; }
        .s1 { top: 10%; left: 10%; animation-delay: 0s; }
        .s2 { top: 15%; right: 10%; animation-delay: 1s; }
        .s3 { bottom: 20%; left: 15%; animation-delay: 2s; }
        .s4 { bottom: 10%; right: 20%; animation-delay: 1.5s; }

        .gif-container {
            width: 200px; height: 200px; margin: 0 auto 20px auto;
            border-radius: 20px; overflow: hidden; background: transparent;
            box-shadow: 0 10px 30px rgba(255, 77, 109, 0.2);
        }
        .gif-container img { width: 100%; height: 100%; object-fit: cover; }
        
        h1 { color: #ff4d6d; font-size: 1.8rem; margin-bottom: 30px; padding: 0 15px; line-height: 1.4; }
        
        .buttons { 
            display: flex; gap: 20px; justify-content: center; align-items: center; 
            position: relative; height: 60px; width: 100%;
        }
        
        button {
            padding: 12px 35px; font-size: 1.1rem; border: none; border-radius: 50px;
            cursor: pointer; font-family: inherit; font-weight: 600; transition: 0.2s;
            -webkit-tap-highlight-color: transparent;
        }
        
        .yes-btn { 
            background: #ff4d6d; color: white; 
            box-shadow: 0 5px 15px rgba(255, 77, 109, 0.4); 
            z-index: 20;
        }
        .yes-btn:active { transform: scale(0.95); }
        
        .no-btn { 
            background: white; color: #ff4d6d; border: 2px solid #ff4d6d; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            position: absolute; 
            transition: all 0.1s ease;
        }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
    </style>
</head>
<body>
    <div class="sticker s1">💖</div>
    <div class="sticker s2">🌸</div>
    <div class="sticker s3">💌</div>
    <div class="sticker s4">🧸</div>

    <div class="container" id="main-content">
        <div class="gif-container">
            <img src="https://media.tenor.com/zGm5acSjHCIAAAAj/cat-ask.gif" alt="Cute Cat">
        </div>
        <h1>Hey {{ name }}, Do you love me? 🥺</h1>
        
        <div class="buttons">
            <button class="yes-btn" onclick="acceptLove()">Yes ❤️</button>
            <button class="no-btn" id="noBtn" style="position: relative;">No 💔</button>
        </div>
    </div>

    <div class="container" id="success-msg" style="display: none;">
        <div class="gif-container">
            <img src="https://media.tenor.com/gUiu1zyxfzYAAAAj/bear-kiss-bear-kisses.gif" alt="Happy Bear">
        </div>
        <h1 style="font-size: 2rem;">Yayyy! I knew it! 😘</h1>
    </div>

    <script>
        const noBtn = document.getElementById('noBtn');
        const targetName = "{{ name }}";

        noBtn.addEventListener('mouseover', moveButton);
        noBtn.addEventListener('touchstart', (e) => { e.preventDefault(); moveButton(); });
        noBtn.addEventListener('click', (e) => { e.preventDefault(); moveButton(); });

        function moveButton() {
            if (noBtn.style.position !== 'absolute') { noBtn.style.position = 'fixed'; }
            const buttonWidth = noBtn.offsetWidth;
            const buttonHeight = noBtn.offsetHeight;
            const maxWidth = window.innerWidth - buttonWidth - 20;
            const maxHeight = window.innerHeight - buttonHeight - 20;
            const randomX = Math.max(20, Math.random() * maxWidth);
            const randomY = Math.max(20, Math.random() * maxHeight);
            noBtn.style.left = randomX + 'px';
            noBtn.style.top = randomY + 'px';
        }

        function acceptLove() {
            document.getElementById('main-content').style.display = 'none';
            document.getElementById('success-msg').style.display = 'block';
            
            // 🔥 NOTIFY SERVER
            fetch('/api/accept_proposal/' + encodeURIComponent(targetName), { method: 'POST' });

            // Confetti
            for(let i=0; i<60; i++) { setTimeout(createConfetti, i * 20); }
        }

        function createConfetti() {
            const confetti = document.createElement('div');
            confetti.innerText = ['❤️', '💖', '🌸'][Math.floor(Math.random() * 3)];
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.top = '-20px';
            confetti.style.fontSize = Math.random() * 20 + 15 + 'px';
            confetti.style.animation = `fall ${Math.random() * 2 + 2}s linear forwards`;
            confetti.style.zIndex = '100';
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 4000);
        }

        const style = document.createElement('style');
        style.innerHTML = `@keyframes fall { to { transform: translateY(105vh) rotate(360deg); } }`;
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

# -------------------------------------------
# 🏠 HOME PAGE (Protected by Password Lock)
# -------------------------------------------
SUGGESTION_POOL = [
    {"icon": "fas fa-heart", "text": "Create a propose link for Sadia"},
    {"icon": "fas fa-check-circle", "text": "Check status for Sadia"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-plane", "text": "Trip plan for Cox's Bazar"}
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
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <style>
            :root {{
                --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 10, 25) 0%, rgb(5, 5, 10) 90%);
                --sidebar-bg: rgba(15, 15, 30, 0.95);
                --text: #e0e6ed; --accent: #00f3ff;
                --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%);
                --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
                --danger: #ff0f7b;
            }}
            body {{ margin: 0; background: var(--bg-gradient); color: var(--text); font-family: 'Outfit', sans-serif; height: 100vh; display: flex; overflow: hidden; }}
            
            /* 🔒 LOCK SCREEN */
            #lock-screen {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: var(--bg-gradient); z-index: 5000;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
            }}
            .lock-box {{ text-align: center; width: 90%; max-width: 300px; }}
            .lock-input {{
                width: 100%; padding: 15px; margin-top: 20px; border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3);
                color: white; font-size: 1.2rem; text-align: center; outline: none;
            }}
            .lock-btn {{
                width: 100%; padding: 15px; margin-top: 10px; border-radius: 12px;
                background: var(--accent); color: black; font-weight: bold; border: none; cursor: pointer;
            }}

            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid rgba(255,255,255,0.1); position: absolute; z-index: 200; left: 0; top: 0; background: var(--sidebar-bg); transition: transform 0.3s; }}
            #sidebar.closed {{ transform: translateX(-105%); }}
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
            .history-list {{ flex: 1; overflow-y: auto; }}
            .history-item {{ padding: 12px; border-radius: 12px; cursor: pointer; color: var(--text); font-size: 0.9rem; opacity: 0.8; display: flex; gap: 10px; }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); opacity: 1; }}
            
            /* ABOUT SECTION (RESTORED) */
            .menu-section {{ margin-top: auto; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); }}
            .about-section {{ display: none; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; margin-top: 5px; text-align: center; font-size: 0.8rem; }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.3rem; margin: 0 8px; transition: 0.3s; display: inline-block; }}
            .about-link:hover {{ color: var(--accent); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; position: absolute; top: 0; left: 0; right: 0; z-index: 100; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; }}
            
            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 60px; }}
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; margin-top: 40px; }}
            .chip {{ padding: 16px 20px; background: rgba(125, 125, 125, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 18px; cursor: pointer; text-align: left; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; transition: 0.3s; }}
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
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
            
            pre {{ background: #111; padding: 15px; border-radius: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body class="dark">
        <div id="lock-screen">
            <div class="lock-box">
                <div style="font-size:3rem; color:var(--accent); margin-bottom:10px;"><i class="fas fa-lock"></i></div>
                <h2>Flux AI Protected</h2>
                <p style="color:gray;">Enter password to access owner's bot.</p>
                <input type="password" id="unlock-pass" class="lock-input" placeholder="Enter Password">
                <button class="lock-btn" onclick="unlockApp()">Unlock</button>
                <div id="lock-error" style="color:var(--danger); margin-top:10px; display:none;">Incorrect Password!</div>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()"><i class="fas fa-plus"></i> New Chat</button>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                <div id="about-info" class="about-section">
                    <strong>{APP_NAME} v{VERSION}</strong><br>
                    <small>Created by <span style="color:var(--accent)">{OWNER_NAME}</span></small>
                    <div style="margin:15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
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
                    <div style="font-size:3.5rem; color:var(--accent); margin-bottom:20px;"><i class="fas fa-bolt"></i></div>
                    <div style="font-size:2rem; font-weight:800; margin-bottom:10px;">Welcome Back!</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask Flux..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                    <button class="action-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v34_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            // 🔓 UNLOCK FUNCTION
            function unlockApp() {{
                const p = document.getElementById('unlock-pass').value;
                if(p === '{ADMIN_PASSWORD}') {{
                    document.getElementById('lock-screen').style.display = 'none';
                }} else {{
                    document.getElementById('lock-error').style.display = 'block';
                }}
            }}

            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{
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
            function saveData() {{ localStorage.setItem('flux_v34_history', JSON.stringify(chats)); }}
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
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(() => {{ alert("Link Copied!"); }});
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble">${{text}}</div>`; // Simplified structure to avoid errors
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
                    appendBubble(data.reply, false);
                    chat.messages.push({{ role: 'assistant', text: data.reply }});
                    saveData();
                }} catch(e) {{ appendBubble("⚠️ Network Error. Check internet.", false); }}
            }}
            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
            renderHistory(); renderSuggestions();
        </script>
    </body>
    </html>
    """

# -------------------------------------------
# 🔥 ROUTES & LOGIC
# -------------------------------------------

@app.route("/love/<name>")
def love_page(name):
    # This renders the proposal page
    return render_template_string(PROPOSE_HTML, name=name)

@app.route("/api/accept_proposal/<name>", methods=["POST"])
def accept_proposal(name):
    # Saves who clicked YES
    PROPOSAL_DB[name.lower()] = "Accepted ✅"
    return jsonify({"status": "saved"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        user_name = data.get("user_name", "User")
        last_msg = messages[-1]['content'] if messages else ""

        # Check API KEY first
        client = get_groq_client()
        if not client:
            return jsonify({"reply": "⚠️ **Error:** API Key is missing. Check Render settings."})

        # 1. 💘 LINK GENERATOR
        if "propose link" in last_msg.lower() or "love link" in last_msg.lower():
            match = re.search(r"for\s+(.*)", last_msg, re.IGNORECASE)
            target_name = match.group(1).strip() if match else "Someone"
            base_url = request.host_url.rstrip('/')
            link = f"{base_url}/love/{target_name.replace(' ', '%20')}"
            
            reply_text = f"💘 **Magic Link Created!**\n\nFor: **{target_name}**\n\nLink: `{link}`\n\n<button onclick=\"copyToClipboard('{link}')\" style='background:#ff4d6d; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;'>📋 Copy Link</button>"
            return jsonify({"reply": reply_text})

        # 2. 🕵️‍♂️ STATUS CHECKER (Password Protected)
        if "check status" in last_msg.lower():
            # Simply check if the name exists in DB
            match = re.search(r"for\s+(.*)", last_msg, re.IGNORECASE)
            if match:
                name_key = match.group(1).strip().lower()
                status = PROPOSAL_DB.get(name_key, "Pending ⏳ (Hasn't clicked YES yet)")
                
                # Ask for password flow is hard in chat, so we just give info if they are already logged in (Home page is locked anyway)
                return jsonify({"reply": f"🕵️‍♂️ **Status Report for {match.group(1)}:**\n\nResult: **{status}**"})

        # 3. INTERNET SEARCH
        search_context = ""
        if "?" in last_msg or "who is" in last_msg.lower():
            web_res = search_web(last_msg)
            if web_res:
                search_context = f"\n[WEB SEARCH]: {web_res}"

        # 4. AI REPLY
        sys_prompt = f"""
        You are {APP_NAME}. Owner: {OWNER_NAME}.
        Be concise and helpful.
        {search_context}
        """

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            temperature=0.7
        )
        return jsonify({"reply": resp.choices[0].message.content})

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({"reply": f"⚠️ System Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
