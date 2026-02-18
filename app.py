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
import base64

# ==========================================
# 🔹 Flux AI (Ultimate Proposal Edition - Build 34.0.0) 🧠💘
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "34.0.0"

# Stats & Storage (In-Memory for Render)
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True 
PROPOSAL_DB = {} # Stores status: { 'Sadia': {'pin': '1234', 'accepted': False} }

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
        return {"time_local": "Unknown", "date": "Unknown", "day": "Unknown"}

# 🌐 WEB SEARCH ENGINE (Safe Mode)
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                return summary
        return None
    except Exception as e:
        print(f"Search Error: {e}")
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

# 💘 PROPOSE PAGE HTML (Updated with Stickers & Notification Logic)
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
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
            font-family: 'Poppins', sans-serif;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; margin: 0; overflow: hidden; touch-action: none; position: relative;
        }
        .sticker { position: absolute; width: 60px; opacity: 0.6; animation: float 6s infinite ease-in-out; pointer-events: none; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }

        .container { text-align: center; position: relative; z-index: 10; width: 100%; }
        
        .gif-container {
            width: 220px; height: 220px; margin: 0 auto 20px auto;
            border-radius: 20px; overflow: hidden; background: transparent;
            box-shadow: 0 10px 30px rgba(255, 77, 109, 0.3);
        }
        .gif-container img { width: 100%; height: 100%; object-fit: cover; }
        
        h1 { color: #ff4d6d; font-size: 1.8rem; margin-bottom: 30px; padding: 0 15px; line-height: 1.4; text-shadow: 2px 2px 0px white; }
        
        .buttons { 
            display: flex; gap: 20px; justify-content: center; align-items: center; 
            position: relative; height: 80px; width: 100%;
        }
        
        button {
            padding: 14px 40px; font-size: 1.2rem; border: none; border-radius: 50px;
            cursor: pointer; font-family: inherit; font-weight: 700; transition: 0.2s;
            -webkit-tap-highlight-color: transparent; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .yes-btn { background: #ff4d6d; color: white; z-index: 20; animation: pulse 2s infinite; }
        .yes-btn:active { transform: scale(0.95); }
        @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 77, 109, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(255, 77, 109, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 77, 109, 0); } }
        
        .no-btn { background: white; color: #ff4d6d; border: 2px solid #ff4d6d; position: absolute; transition: all 0.1s ease; }
    </style>
</head>
<body>
    <img src="https://cdn-icons-png.flaticon.com/512/2904/2904973.png" class="sticker" style="top:10%; left:10%;">
    <img src="https://cdn-icons-png.flaticon.com/512/742/742751.png" class="sticker" style="top:20%; right:15%; animation-delay: 1s;">
    <img src="https://cdn-icons-png.flaticon.com/512/1077/1077035.png" class="sticker" style="bottom:15%; left:15%; animation-delay: 2s;">
    <img src="https://cdn-icons-png.flaticon.com/512/833/833472.png" class="sticker" style="bottom:10%; right:10%; animation-delay: 1.5s;">

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
        <h1 style="font-size: 2rem; color:#d63384;">Yayyy! I knew it! 😘</h1>
    </div>

    <script>
        const noBtn = document.getElementById('noBtn');
        const name = "{{ name }}";

        noBtn.addEventListener('mouseover', moveButton);
        noBtn.addEventListener('touchstart', (e) => { e.preventDefault(); moveButton(); });
        noBtn.addEventListener('click', (e) => { e.preventDefault(); moveButton(); });

        function moveButton() {
            if (noBtn.style.position !== 'absolute') noBtn.style.position = 'fixed'; 
            const maxWidth = window.innerWidth - noBtn.offsetWidth - 20;
            const maxHeight = window.innerHeight - noBtn.offsetHeight - 20;
            noBtn.style.left = Math.max(20, Math.random() * maxWidth) + 'px';
            noBtn.style.top = Math.max(20, Math.random() * maxHeight) + 'px';
        }

        function acceptLove() {
            // Notify Server
            fetch('/accept_love/' + encodeURIComponent(name))
                .catch(err => console.log('Network error, but love accepted!'));

            document.getElementById('main-content').style.display = 'none';
            document.getElementById('success-msg').style.display = 'block';
            for(let i=0; i<60; i++) setTimeout(createConfetti, i * 20);
        }

        function createConfetti() {
            const confetti = document.createElement('div');
            confetti.innerText = ['❤️', '💖', '🌸', '💘'][Math.floor(Math.random() * 4)];
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

SUGGESTION_POOL = [
    {"icon": "fas fa-heart", "text": "Create a propose link for Sadia"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"}
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
            
            /* LINK COPY BUTTON STYLE */
            .link-box {{ background: rgba(0, 243, 255, 0.1); border: 1px solid var(--accent); padding: 10px; border-radius: 12px; margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }}
            .link-text {{ font-family: monospace; font-size: 0.85rem; color: var(--accent); word-break: break-all; display: none; }} /* Hidden URL */
            .link-btn {{ background: var(--accent); color: black; border: none; padding: 8px; border-radius: 8px; cursor: pointer; font-weight: 700; width: 100%; text-align: center; }}
            
            /* ... (Rest of existing styles kept exactly as they were) ... */
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; }} .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }} .history-item {{ padding: 12px; border-radius: 12px; cursor: pointer; color: var(--text); font-size: 0.9rem; opacity: 0.8; display: flex; gap: 10px; }} .history-item:hover {{ background: rgba(125, 125, 125, 0.1); opacity: 1; }}
            .menu-section {{ margin-top: auto; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); }} .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; }} .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text); opacity: 0.5; cursor: pointer; border-radius: 8px; }} .theme-btn.active {{ background: rgba(125,125,125,0.2); opacity: 1; }}
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }} header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; position: absolute; top: 0; left: 0; right: 0; z-index: 100; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; }} .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 60px; }}
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; margin-top: 40px; }} .chip {{ padding: 16px 20px; background: rgba(125, 125, 125, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 18px; cursor: pointer; text-align: left; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; transition: 0.3s; }} .chip:hover {{ border-color: var(--accent); transform: translateY(-3px); }} .chip i {{ color: var(--accent); }}
            .message-wrapper {{ display: flex; gap: 16px; width: 100%; max-width: 850px; margin: 0 auto; }} .message-wrapper.user {{ flex-direction: row-reverse; }} .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }} .bot-avatar {{ background: var(--bot-grad); color: white; }} .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid rgba(255,255,255,0.1); }}
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; }} .bot .bubble {{ background: transparent; padding: 0; width: 100%; }} .user .bubble {{ background: var(--user-grad); color: white; border-radius: 20px 4px 20px 20px; }}
            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; gap: 8px; }} .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 26px; padding: 8px 8px 8px 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); }} textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 12px 0; font-family: inherit; }} .action-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 5px; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; }}
            pre {{ background: #111 !important; padding: 15px; border-radius: 10px; overflow-x: auto; }} code {{ font-family: monospace; font-size: 0.9rem; color: #0f0; }}
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
                <div class="theme-toggles"><button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i></button><button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i></button></div>
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
                    <div style="font-size:2rem; font-weight:800; margin-bottom:10px;">Flux AI Brain</div>
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

            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{ html += `<div class="chip" onclick="sendSuggestion('${{s.text}}')"><i class="${{s.icon}}"></i> ${{s.text}}</div>`; }});
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
            
            // COPY LINK FUNCTION
            window.copyLink = function(url) {{
                navigator.clipboard.writeText(url).then(() => {{ alert("Link Copied! 💘"); }});
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                
                // LINK PARSER & BUTTON ADDER
                if (text.includes("###LINK###")) {{
                    const parts = text.split("###LINK###");
                    const message = parts[0];
                    const url = parts[1];
                    text = message + `
                        <div class="link-box">
                            <div style="font-size:0.9rem; font-weight:600; color:var(--text);">💘 Magic Link Created!</div>
                            <button class="link-btn" onclick="copyLink('${{url}}')"><i class="fas fa-copy"></i> Copy Link</button>
                        </div>
                    `;
                }}
                
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                wrapper.querySelector('.bubble').innerHTML = marked.parse(text);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                saveData(); msgInput.value = ''; appendBubble(text, true);

                const context = chat.messages.slice(-6).map(m => ({{ role: m.role, content: m.text }}));
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context }}) }});
                    const data = await res.json();
                    appendBubble(data.reply, false);
                    chat.messages.push({{ role: 'assistant', text: data.reply }});
                    saveData();
                }} catch(e) {{ appendBubble("⚠️ Network Error. Check connection.", false); }}
            }}
            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
            renderHistory(); renderSuggestions();
        </script>
    </body>
    </html>
    """

# 💘 PROPOSE LINK GENERATOR
@app.route("/love/<name>")
def love_page(name):
    # If name has ID format (Name_1234), extract clean name
    clean_name = name.split('_')[0]
    return render_template_string(PROPOSE_HTML, name=clean_name)

# 💘 ACCEPT ENDPOINT (Called when "Yes" is clicked)
@app.route("/accept_love/<name>")
def accept_love(name):
    clean_name = name.strip()
    if clean_name in PROPOSAL_DB:
        PROPOSAL_DB[clean_name]['accepted'] = True
    else:
        # Create entry if doesn't exist (fallback)
        PROPOSAL_DB[clean_name] = {'pin': '0000', 'accepted': True}
    return jsonify({"status": "success"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        last_msg = messages[-1]['content'] if messages else ""

        # 1. GENERATE LINK + PASSWORD LOGIC
        if "propose link" in last_msg.lower() or "love link" in last_msg.lower() or "create link" in last_msg.lower():
            match = re.search(r"for\s+(.*)", last_msg, re.IGNORECASE)
            target_name = match.group(1).strip() if match else "Someone"
            
            # Generate 4-digit PIN
            pin = str(random.randint(1000, 9999))
            
            # Save to DB
            unique_key = target_name 
            PROPOSAL_DB[unique_key] = {'pin': pin, 'accepted': False}
            
            # Create Link
            base_url = request.host_url.rstrip('/')
            link = f"{base_url}/love/{unique_key.replace(' ', '%20')}"
            
            # Return Special Format for Frontend to render Button
            return jsonify({
                "reply": f"💘 Link created for **{target_name}**!\n\n🔑 **Secret PIN:** `{pin}`\n*(Use this PIN to check if they clicked Yes)*\n\n###LINK###{link}"
            })

        # 2. CHECK STATUS LOGIC
        if "check status" in last_msg.lower() or "check proposal" in last_msg.lower():
            # Try to find Name and PIN in message
            found = False
            for name, data in PROPOSAL_DB.items():
                if name.lower() in last_msg.lower() and data['pin'] in last_msg:
                    status = "✅ **ACCEPTED!** They clicked YES! 🎉" if data['accepted'] else "⏳ **Pending...** They haven't clicked YES yet."
                    return jsonify({"reply": f"📊 **Status for {name}:**\n\n{status}"})
                    found = True
                    break
            
            if not found:
                 return jsonify({"reply": "⚠️ Could not find that proposal. Please provide the correct **Name** and **PIN** (e.g., 'Check status for Sadia 1234')."})

        # 3. NORMAL CHAT (Safe Mode)
        client = get_groq_client()
        if not client:
            return jsonify({"reply": "⚠️ API Keys Missing in Render."})

        # Search Check (Wrapped in Try-Except to prevent crash)
        search_context = ""
        if "?" in last_msg:
            try:
                web_result = search_web(last_msg)
                if web_result:
                    search_context = f"\n[SEARCH INFO]: {web_result}"
            except:
                pass

        sys_prompt = f"You are Flux AI. Helpful & Concise.{search_context}"
        
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            temperature=0.7
        )
        return jsonify({"reply": resp.choices[0].message.content})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"reply": "⚠️ System connection error. Please try again later."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
