from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import math

# ==========================================
# 🔹 Flux AI (Groq Stability Edition - Build 23.2.0) 🛡️
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"
VERSION = "23.2.0"
ADMIN_PASSWORD = "7rx9x2c0"

# Links
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=100024467246473" 
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"      

# Stats
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True 

app = Flask(__name__)
app.secret_key = os.urandom(24)

# CONFIGURATION: GROQ ONLY
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_groq_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found. Please add them in Render Environment Variables.")

def get_groq_client():
    global current_groq_index
    if not GROQ_KEYS: return None
    # Rotate keys for load balancing
    key = GROQ_KEYS[current_groq_index % len(GROQ_KEYS)]
    current_groq_index += 1
    return Groq(api_key=key)

def get_uptime():
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return str(timedelta(seconds=uptime_seconds))

def get_current_context(): 
    tz_dhaka = pytz.timezone('Asia/Dhaka')
    now_dhaka = datetime.now(tz_dhaka)
    return {
        "time_local": now_dhaka.strftime("%I:%M %p")
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
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics simply"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Plan a 3-day trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Creative business ideas"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML & CSS basics"},
    {"icon": "fas fa-guitar", "text": "Write a song lyric about rain"},
    {"icon": "fas fa-camera", "text": "Photography tips for beginners"},
    {"icon": "fas fa-paint-brush", "text": "Generate a futuristic city image"},
    {"icon": "fas fa-calculator", "text": "Solve this puzzle: 2 + 2 * 4"}
]

@app.route("/")
def home():
    suggestions_json = json.dumps(SUGGESTION_POOL)
    
    # ⚠️ IMPORTANT: All CSS/JS braces must be doubled {{ }}
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
            :root {{
                /* 🌌 CYBERPUNK PALETTE */
                --bg-gradient: radial-gradient(circle at 10% 20%, rgb(8, 8, 20) 0%, rgb(2, 2, 5) 90%);
                --glass-bg: rgba(20, 20, 35, 0.65);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text: #e0e6ed;
                --text-secondary: #94a3b8;
                --accent: #00f3ff;
                --accent-glow: 0 0 15px rgba(0, 243, 255, 0.6);
                --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%);
                --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
                --danger: #ff0f7b;
                --success: #00ff87;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg-gradient); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
            }}

            .glass {{
                background: var(--glass-bg); backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border);
            }}

            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--glass-border);
                transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
                position: absolute; z-index: 200; left: 0; top: 0; 
                box-shadow: 10px 0 40px rgba(0,0,0,0.6);
                background: rgba(10, 10, 25, 0.9); backdrop-filter: blur(25px);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ 
                font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; 
                display: flex; align-items: center; gap: 12px; color: white; 
                text-shadow: var(--accent-glow);
                animation: glowPulse 3s infinite alternate;
            }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{
                width: 100%; padding: 14px; background: rgba(255, 255, 255, 0.05); 
                color: var(--text); border: 1px solid var(--glass-border);
                border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px;
                margin-bottom: 20px; transition: all 0.3s ease;
            }}
            .new-chat-btn:active {{ transform: scale(0.97); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{
                padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem;
                transition: all 0.2s; display: flex; align-items: center; gap: 10px; font-weight: 500;
            }}
            .history-item:hover {{ background: rgba(255, 255, 255, 0.05); color: white; }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .about-section {{ 
                display: none; background: rgba(0, 0, 0, 0.6); padding: 20px; border-radius: 16px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--glass-border);
                animation: fadeIn 0.3s;
            }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: white; font-size: 1.4rem; margin: 0 10px; transition: 0.3s; display: inline-block; }}
            .about-link:hover {{ color: var(--accent); }}

            header {{
                height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(10, 10, 25, 0.75); backdrop-filter: blur(20px);
                border-bottom: 1px solid var(--glass-border); 
                position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; }}

            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding-top: 130px; padding-bottom: 100px;
            }}
            .icon-wrapper {{ 
                width: 100px; height: 100px; background: linear-gradient(135deg, rgba(0, 243, 255, 0.15), rgba(188, 19, 254, 0.15));
                border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 30px; 
                display: flex; align-items: center; justify-content: center; font-size: 3.5rem; color: white; 
                margin-bottom: 25px; box-shadow: 0 0 40px rgba(0, 243, 255, 0.2);
                animation: levitate 4s ease-in-out infinite;
            }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; background: linear-gradient(to right, #fff, #b3b3b3); -webkit-background-clip: text; color: transparent; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 1.1rem; max-width: 80%; line-height: 1.5; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; }}
            .chip {{
                padding: 18px 22px; background: rgba(255, 255, 255, 0.04); 
                border: 1px solid var(--glass-border); border-radius: 20px;
                cursor: pointer; text-align: left; color: var(--text-secondary); 
                transition: all 0.3s; font-weight: 500; font-size: 0.95rem; display: flex; align-items: center; gap: 14px;
            }}
            .chip:hover {{ transform: translateY(-5px); background: rgba(255, 255, 255, 0.08); border-color: var(--accent); color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }}
            .chip i {{ color: var(--accent); font-size: 1.2rem; opacity: 0.9; }}

            .message-wrapper {{ display: flex; gap: 16px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 40px; height: 40px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 5px 15px rgba(0,0,0,0.3); font-size: 1.1rem; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(255,255,255,0.1); color: white; border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 85%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            .sender-name {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 5px; font-weight: 600; padding-left: 2px; text-transform: uppercase; }}
            .message-wrapper.user .sender-name {{ display: none; }}

            .bubble {{ padding: 14px 20px; border-radius: 22px; font-size: 1.02rem; line-height: 1.65; word-wrap: break-word; position: relative; }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; color: var(--text); }}
            .user .bubble {{ background: var(--user-grad); border-radius: 22px 4px 22px 22px; color: white; box-shadow: 0 5px 20px rgba(20, 136, 204, 0.3); }}
            
            .bubble strong {{ color: var(--accent); font-weight: 700; }}
            .bubble img {{ max-width: 100%; border-radius: 18px; margin-top: 12px; cursor: pointer; box-shadow: 0 8px 30px rgba(0,0,0,0.4); border: 1px solid var(--glass-border); }}
            .img-brand {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 10px; display: flex; align-items: center; gap: 6px; font-weight: 600; opacity: 0.8; }}

            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 25px;
                background: linear-gradient(to top, rgb(2, 2, 5) 0%, transparent 100%); 
                display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: rgba(30, 30, 55, 0.7); border-radius: 30px; padding: 8px 8px 8px 24px;
                border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.4);
                backdrop-filter: blur(20px); transition: all 0.3s ease;
            }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: 0 0 30px rgba(0, 243, 255, 0.15); }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: white; font-size: 1.05rem; max-height: 160px; resize: none; padding: 14px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--text); color: black; border: none; width: 48px; height: 48px;
                border-radius: 50%; cursor: pointer; margin-left: 12px; margin-bottom: 2px;
                display: flex; align-items: center; justify-content: center; font-size: 1.3rem; transition: 0.3s;
            }}
            .send-btn:hover {{ transform: scale(1.1); background: var(--accent); color: black; box-shadow: 0 0 15px var(--accent); }}

            .modal-overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.85); display: none; justify-content: center; align-items: center; 
                z-index: 9999; backdrop-filter: blur(10px);
            }}
            .modal-box {{
                background: rgba(20, 20, 35, 0.95); border: 1px solid var(--glass-border); 
                padding: 35px; border-radius: 24px; width: 90%; max-width: 360px; 
                text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            }}
            .modal-title {{ font-size: 1.5rem; margin-bottom: 12px; font-weight: 700; color: white; }}
            .modal-desc {{ color: var(--text-secondary); margin-bottom: 25px; line-height: 1.5; }}
            
            .btn-modal {{ padding: 14px; border-radius: 14px; border: none; font-weight: 600; cursor: pointer; flex: 1; margin: 0 6px; font-size: 0.95rem; transition: 0.2s; }}
            .btn-cancel {{ background: rgba(255,255,255,0.1); color: white; }}
            .btn-delete {{ background: var(--danger); color: white; }}
            .btn-confirm {{ background: var(--success); color: black; }}

            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }}
            .stat-box {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 14px; border: 1px solid var(--glass-border); }}
            .stat-val {{ font-size: 1.6rem; font-weight: 700; color: var(--accent); }}
            .stat-label {{ font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; margin-top: 5px; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
            @keyframes glowPulse {{ 0% {{ text-shadow: 0 0 10px rgba(0,243,255,0.5); }} 100% {{ text-shadow: 0 0 20px rgba(0,243,255,0.9), 0 0 10px rgba(188,19,254,0.5); }} }}
            
            .typing {{ display: flex; gap: 6px; padding: 12px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            
            pre {{ background: #0d1117 !important; padding: 20px; border-radius: 16px; overflow-x: auto; border: 1px solid var(--glass-border); }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.9rem; }}
        </style>
    </head>
    <body class="dark">
        
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title">Clear History?</div>
                <div class="modal-desc">This will permanently delete all your conversations.</div>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal('delete-modal')">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete All</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title"><i class="fas fa-shield-alt" style="color:var(--accent)"></i> Admin Access</div>
                <div class="modal-desc">Enter authorization code</div>
                <input type="password" id="admin-pass" style="width:100%; padding:14px; border-radius:12px; border:1px solid var(--glass-border); background:rgba(0,0,0,0.3); color:white; margin-bottom:10px; outline:none; font-size:1rem; text-align:center;" placeholder="••••••••">
                <div id="admin-error-msg" style="color:var(--danger); font-size:0.9rem; margin-bottom:20px; display:none; font-weight:600;"><i class="fas fa-exclamation-circle"></i> Invalid Password</div>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal('admin-auth-modal')">Cancel</button>
                    <button class="btn-modal btn-confirm" onclick="verifyAdmin()">Login</button>
                </div>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box" style="max-width: 450px;">
                <div class="modal-title" style="margin-bottom:20px;">Admin Dashboard</div>
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-val" id="stat-msgs">0</div><div class="stat-label">Total Messages</div></div>
                    <div class="stat-box"><div class="stat-val" id="stat-uptime">0s</div><div class="stat-label">Server Uptime</div></div>
                    <div class="stat-box"><div class="stat-val" style="font-size:1.1rem;">{VERSION}</div><div class="stat-label">App Version</div></div>
                    <div class="stat-box"><div class="stat-val" style="font-size:1.1rem; color:white;">{OWNER_NAME}</div><div class="stat-label">Developer</div></div>
                </div>
                <div class="modal-desc" id="system-status-text" style="font-weight:700; font-size:1.1rem; color:var(--success);">System is ONLINE 🟢</div>
                <button class="btn-modal btn-delete" id="btn-toggle-sys" onclick="toggleSystem()" style="width:100%; margin:0; padding:16px;">Turn System OFF</button>
                <button class="btn-modal btn-cancel" onclick="closeModal('admin-panel-modal')" style="width:100%; margin:15px 0 0 0;">Close Panel</button>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="glass closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div style="font-size:0.75rem; font-weight: 700; color:var(--text-secondary); margin-bottom:12px; letter-spacing: 1px; opacity:0.8;">RECENT</div>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                <div id="about-info" class="about-section">
                    <strong style="font-size:1.2rem; display:block; margin-bottom:5px; color:white;">{APP_NAME}</strong>
                    <span style="font-size:0.8rem; opacity:0.7;">v{VERSION}</span><br>
                    <small style="color:var(--text-secondary)">Created by <span style="color:var(--accent)">{OWNER_NAME}</span></small><br>
                    <div style="margin:15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="display:block; margin-top:5px; font-weight:500; opacity:0.5;">&copy; 2026 All Rights Reserved</small>
                </div>
                <div class="history-item" onclick="openDeleteModal('delete-modal')" style="color:#ff0f7b;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:white; font-size:1.4rem; cursor:pointer; padding: 8px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.4rem; letter-spacing: -0.5px; background: linear-gradient(to right, #fff, #bbb); -webkit-background-clip: text; color: transparent;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem; cursor:pointer; padding: 8px;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your intelligent AI companion ready to explore the future.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Type a message..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            
            let chats = JSON.parse(localStorage.getItem('flux_v23_2_history')) || [];
            let userName = localStorage.getItem('flux_user_name'); 
            let awaitingName = false; 

            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');

            renderHistory();
            renderSuggestions(); 

            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
                const selected = shuffled.slice(0, 4);
                let html = '';
                selected.forEach(s => {{
                    // NOTE: Double braces for JS inside f-string
                    html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>';
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData();
                renderHistory();
                renderSuggestions();
                
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                msgInput.value = '';
                resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v23_2_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Conversation').substring(0, 22) + '</span>';
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;
                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none'; 
                if (chat.messages.length === 0) {{
                     chatBox.appendChild(welcomeScreen);
                     welcomeScreen.style.display = 'flex';
                }} else {{
                    chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                }}
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container">${{name}}<div class="bubble">${{marked.parse(text)}}</div></div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble" style="background:transparent; padding-left:0;"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div></div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(text === '!admin') {{
                    msgInput.value = '';
                    openModal('admin-auth-modal');
                    document.getElementById('admin-error-msg').style.display = 'none';
                    return;
                }}

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData();
                msgInput.value = '';
                appendBubble(text, true);

                if(!userName && !awaitingName) {{
                    awaitingName = true;
                    setTimeout(() => {{
                        appendBubble("Hello! Welcome to Flux AI. Before we start, may I know your name?", false);
                    }}, 600);
                    return;
                }}
                if(awaitingName) {{
                    userName = text;
                    localStorage.setItem('flux_user_name', userName);
                    awaitingName = false;
                    setTimeout(() => {{
                        appendBubble(`Nice to meet you, ${{userName}}! How can I help you today?`, false);
                    }}, 600);
                    return;
                }}

                showTyping();
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                // We pass name via SYSTEM PROMPT instead of user body to avoid transcript issues
                
                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context, user_name: userName }})
                    }});
                    
                    removeTyping();
                    if(!res.ok) throw new Error("API Error");
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
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

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ I'm currently experiencing high traffic. Please try again in a moment.", false);
                }}
            }}

            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function openDeleteModal(id) {{ openModal(id); }}
            
            function confirmDelete() {{ localStorage.removeItem('flux_v23_2_history'); location.reload(); }}

            async function verifyAdmin() {{
                const pass = document.getElementById('admin-pass').value;
                const errorMsg = document.getElementById('admin-error-msg');
                
                if(pass === '{ADMIN_PASSWORD}') {{
                    errorMsg.style.display = 'none';
                    closeModal('admin-auth-modal');
                    openModal('admin-panel-modal');
                    document.getElementById('admin-pass').value = '';
                    try {{
                        const res = await fetch('/admin/stats');
                        const data = await res.json();
                        document.getElementById('stat-uptime').innerText = data.uptime;
                        document.getElementById('stat-msgs').innerText = data.total_messages;
                        updateSysBtn(data.active);
                    }} catch(e) {{ alert('Error fetching stats'); }}
                }} else {{
                    errorMsg.style.display = 'block';
                }}
            }}

            async function toggleSystem() {{
                try {{
                    const res = await fetch('/admin/toggle_system', {{ method: 'POST' }});
                    const data = await res.json();
                    updateSysBtn(data.active);
                }} catch(e) {{ alert('Error toggling system'); }}
            }}

            function updateSysBtn(isActive) {{
                const btn = document.getElementById('btn-toggle-sys');
                const txt = document.getElementById('system-status-text');
                if(isActive) {{
                    btn.innerText = "Turn System OFF";
                    btn.style.background = "var(--danger)";
                    txt.innerText = "System is ONLINE 🟢";
                    txt.style.color = "var(--success)";
                }} else {{
                    btn.innerText = "Turn System ON";
                    btn.style.background = "var(--success)";
                    txt.innerText = "System is OFFLINE 🔴";
                    txt.style.color = "var(--danger)";
                }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

# 🛡️ ADMIN API ROUTES
@app.route("/admin/stats")
def admin_stats():
    return jsonify({
        "uptime": get_uptime(),
        "total_messages": TOTAL_MESSAGES,
        "active": SYSTEM_ACTIVE
    })

@app.route("/admin/toggle_system", methods=["POST"])
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    return jsonify({"active": SYSTEM_ACTIVE})

@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES
    if not SYSTEM_ACTIVE:
        return Response("System is currently under maintenance.", status=503)

    TOTAL_MESSAGES += 1
    data = request.json
    messages = data.get("messages", [])
    user_name = data.get("user_name", None)

    # MATH ENGINE
    if messages and messages[-1]['role'] == 'user':
        last_msg = messages[-1]['content']
        math_result = solve_math_problem(last_msg)
        if math_result:
            system_note = {
                "role": "system",
                "content": f"⚡ FLUX TOOL: Math detected. Answer is {math_result}. Use this exact value."
            }
            messages.insert(-1, system_note)

    ctx = get_current_context()
    
    # 🧠 BRAIN (NATURAL)
    sys_prompt_content = f"""
    You are {APP_NAME}, a super-intelligent AI assistant.
    
    IDENTITY:
    - Name: {APP_NAME}
    - Created by: {OWNER_NAME} (Bangla: {OWNER_NAME_BN})
    
    CONTEXT:
    - Time: {ctx['time_local']}
    
    RULES:
    1. **NO SCRIPT FORMAT**: Never use prefixes like "Flux AI:". Reply directly.
    2. **NATURAL**: Speak naturally. Do not repeat the owner's name unless asked.
    3. **NAME**: You know the user is {user_name if user_name else 'friend'}. Use it rarely.
    4. **IMAGE**: Output ONLY: ![Flux Image](https://image.pollinations.ai/prompt/{{english_prompt}})
    """

    sys_message = {"role": "system", "content": sys_prompt_content}

    def generate():
        global current_key_index
        attempts = 0
        max_retries = len(GROQ_KEYS) + 1 if GROQ_KEYS else 1
        
        while attempts < max_retries:
            try:
                client = get_groq_client()
                if not client: yield "⚠️ Config Error."; return
                
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[sys_message] + messages,
                    stream=True,
                    temperature=0.7, 
                    max_tokens=1024
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ System overloaded. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
