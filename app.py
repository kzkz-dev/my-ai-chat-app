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
# 🔹 Flux AI (Ultimate Fix - Build 27.1.0) 🧠
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "27.1.0"
ADMIN_PASSWORD = "7rx9x2c0" 

# Links (Restored)
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
    print("⚠️ WARNING: No Groq keys found. Please add them in Render Environment Variables.")

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
    return {
        "time_local": now_dhaka.strftime("%I:%M %p"),
        "date": now_dhaka.strftime("%d %B, %Y")
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
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics simply"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Plan a trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Creative business ideas"},
    {"icon": "fas fa-laptop-code", "text": "Write a Python calculator"},
    {"icon": "fas fa-paint-brush", "text": "Generate a cyberpunk city image"},
    {"icon": "fas fa-calculator", "text": "Solve this puzzle: 50 * 3 + 20"}
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
            :root {{
                /* 🎨 DEFAULT DARK THEME */
                --bg: #050a14;
                --sidebar: #0f172a;
                --text: #e2e8f0;
                --text-secondary: #94a3b8;
                --input-bg: rgba(30, 41, 59, 0.7);
                --border: rgba(148, 163, 184, 0.1);
                --accent: #3b82f6;
                /* 🔥 LOGO GRADIENT (Purple to Blue) */
                --bolt-grad: linear-gradient(135deg, #d946ef 0%, #3b82f6 100%);
                --user-msg: #1e293b;
                --bot-msg: transparent;
            }}

            body.light {{
                /* ☀️ LIGHT THEME */
                --bg: #ffffff;
                --sidebar: #f8fafc;
                --text: #0f172a;
                --text-secondary: #475569;
                --input-bg: #f1f5f9;
                --border: #e2e8f0;
                --accent: #2563eb;
                --user-msg: #eff6ff;
                --bot-msg: transparent;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.3s, color 0.3s;
            }}

            /* 🌌 NEURAL BACKGROUND (The Brain Network) */
            #neuro-bg {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: 0; pointer-events: none; opacity: 0.4;
            }}

            /* SIDEBAR */
            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border);
                background: var(--sidebar); /* 🔥 Dynamic Color */
                position: absolute; z-index: 200; left: 0; top: 0; 
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 5px 0 25px rgba(0,0,0,0.3);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ 
                font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; 
                display: flex; align-items: center; gap: 12px; color: var(--text);
                letter-spacing: -0.5px;
            }}
            /* 🔥 LOGO GRADIENT MATCHING YOUR IMAGE */
            .brand i {{ background: var(--bolt-grad); -webkit-background-clip: text; color: transparent; font-size: 1.8rem; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--input-bg); 
                color: var(--accent); border: 1px solid var(--border);
                border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 10px;
                margin-bottom: 20px; transition: 0.2s;
            }}
            .new-chat-btn:active {{ transform: scale(0.98); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }}
            .history-item {{
                padding: 12px; border-radius: 10px; cursor: pointer; color: var(--text-secondary); 
                font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                transition: 0.2s; display: flex; align-items: center; gap: 10px;
            }}
            .history-item:active, .history-item:hover {{ background: var(--input-bg); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px; }}
            
            /* ABOUT SECTION (Restored Links) */
            .about-section {{ 
                display: none; background: var(--input-bg); padding: 15px; border-radius: 12px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--border);
            }}
            .about-section.show {{ display: block; animation: fadeIn 0.3s; }}
            .social-links {{ margin: 10px 0; display: flex; justify-content: center; gap: 15px; }}
            .social-links a {{ color: var(--text); font-size: 1.3rem; transition: 0.2s; }}
            .social-links a:hover {{ color: var(--accent); transform: scale(1.1); }}

            /* HEADER */
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 18px;
                background: rgba(5, 10, 20, 0.8); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.8); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 18px 140px 18px; display: flex; flex-direction: column; gap: 24px; position: relative; z-index: 1; }}

            /* WELCOME SCREEN */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding-top: 60px; padding-bottom: 100px;
            }}
            .icon-wrapper {{ 
                width: 90px; height: 90px; background: rgba(255,255,255,0.05); 
                border-radius: 24px; display: flex; align-items: center; justify-content: center; 
                font-size: 3.5rem; margin-bottom: 20px; border: 1px solid var(--border);
                box-shadow: 0 0 40px rgba(59, 130, 246, 0.2);
            }}
            .icon-wrapper i {{ background: var(--bolt-grad); -webkit-background-clip: text; color: transparent; }}
            
            .welcome-title {{ font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 30px; font-size: 1rem; max-width: 80%; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; width: 100%; max-width: 700px; }}
            .chip {{
                padding: 14px; background: var(--input-bg); border: 1px solid var(--border); border-radius: 12px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: 0.2s;
                font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 10px;
            }}
            .chip:hover {{ border-color: var(--accent); color: var(--text); transform: translateY(-2px); }}
            .chip i {{ color: var(--accent); opacity: 0.8; }}

            /* MESSAGES */
            .message-wrapper {{ display: flex; gap: 12px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.3s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.1rem; }}
            .bot-avatar {{ background: var(--bolt-grad); color: white; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }}
            .user-avatar {{ background: var(--input-bg); border: 1px solid var(--border); color: var(--text); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 85%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            
            .bubble {{ 
                padding: 12px 16px; border-radius: 18px; font-size: 1rem; line-height: 1.6; 
                word-wrap: break-word; overflow-wrap: break-word;
            }}
            .bot .bubble {{ background: var(--bot-msg); padding-left: 0; width: 100%; color: var(--text); }}
            .user .bubble {{ background: var(--user-msg); border: 1px solid var(--border); color: var(--text); border-radius: 18px 4px 18px 18px; }}

            /* CODE BLOCKS & COPY */
            pre {{ background: #0d1117 !important; padding: 15px; border-radius: 12px; overflow-x: auto; border: 1px solid var(--border); position: relative; margin-top: 10px; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; }}
            .copy-btn {{
                position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.1); color: #fff;
                border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.75rem;
            }}

            /* RUN BUTTON */
            .run-code-btn {{
                display: inline-flex; align-items: center; gap: 8px; margin-top: 10px;
                padding: 8px 14px; background: var(--input-bg); color: var(--accent);
                border: 1px solid var(--accent); border-radius: 8px; font-weight: 600; cursor: pointer;
            }}

            /* INPUT AREA */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 85%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 24px; padding: 10px 10px 10px 20px;
                border: 1px solid var(--border); box-shadow: 0 5px 20px rgba(0,0,0,0.1); backdrop-filter: blur(10px);
            }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 140px; resize: none; padding: 10px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 42px; height: 42px;
                border-radius: 50%; cursor: pointer; margin-left: 10px;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
            }}

            /* 🔥 ENERGY TRAIL (BOLT) */
            .energy-ball {{
                position: fixed; width: 15px; height: 15px; background: var(--accent);
                border-radius: 50%; pointer-events: none; z-index: 9999;
                box-shadow: 0 0 20px var(--accent);
                animation: shootUp 0.5s ease-in-out forwards;
            }}

            /* ANIMATIONS */
            @keyframes popIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes shootUp {{ 0% {{ bottom: 80px; left: 50%; opacity: 1; transform: scale(1); }} 100% {{ bottom: 70%; left: 50%; opacity: 0; transform: scale(0.2); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

            /* PREVIEW MODAL */
            #preview-modal {{
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center;
            }}
            .preview-box {{
                width: 95%; height: 85%; background: white; border-radius: 12px; overflow: hidden;
                display: flex; flex-direction: column;
            }}
            .preview-header {{
                padding: 10px; background: #1e293b; color: white; display: flex; justify-content: space-between; align-items: center;
            }}
            iframe {{ flex: 1; border: none; }}

            /* OVERLAY & MODALS */
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 150; display: none; backdrop-filter: blur(2px); }}
            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; }}
            .modal-box {{ background: var(--sidebar); border: 1px solid var(--border); padding: 25px; border-radius: 16px; width: 90%; max-width: 320px; text-align: center; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 4px; border-radius: 8px; margin-bottom: 10px; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 6px; }}
            .theme-btn.active {{ background: var(--bg); color: var(--accent); box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span>Live Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:4px;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>

        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--text)">Clear History?</h3>
                <div style="display:flex; gap:10px; margin-top:20px;">
                    <button onclick="closeModal('delete-modal')" style="flex:1; padding:10px; background:var(--input-bg); color:var(--text); border:none; border-radius:8px;">Cancel</button>
                    <button onclick="confirmDelete()" style="flex:1; padding:10px; background:var(--danger); color:white; border:none; border-radius:8px;">Delete</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--accent)">Admin Access</h3>
                <input type="password" id="admin-pass" style="width:100%; padding:10px; margin:15px 0; background:var(--input-bg); border:1px solid var(--border); color:var(--text); text-align:center; border-radius:8px;" placeholder="Password">
                <button onclick="verifyAdmin()" style="width:100%; padding:10px; background:var(--accent); color:white; border:none; border-radius:8px;">Login</button>
                <button onclick="closeModal('admin-auth-modal')" style="margin-top:10px; background:transparent; border:none; color:var(--text-secondary);">Cancel</button>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box">
                <h3>Dashboard</h3>
                <div style="margin:15px 0;">
                    <div>Msgs: <span id="stat-msgs" style="color:var(--accent)">0</span></div>
                    <div>Uptime: <span id="stat-uptime" style="color:var(--accent)">0s</span></div>
                </div>
                <button onclick="toggleSystem()" id="btn-toggle-sys" style="width:100%; padding:10px; background:var(--success); color:white; border:none; border-radius:8px;">System Online</button>
                <button onclick="closeModal('admin-panel-modal')" style="margin-top:10px; background:transparent; border:none; color:var(--text-secondary);">Close</button>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i></button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i></button>
                </div>
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> About</div>
                <div id="about-info" class="about-section">
                    <strong>{APP_NAME} v{VERSION}</strong><br>
                    <small>Dev: {OWNER_NAME}</small>
                    <div class="social-links">
                        <a href="{FACEBOOK_URL}" target="_blank"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank"><i class="fas fa-globe"></i></a>
                    </div>
                    <small>&copy; 2026 All Rights Reserved</small>
                </div>
                <div class="history-item" onclick="openDeleteModal('delete-modal')" style="color:#ef4444;"><i class="fas fa-trash"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:700; font-size:1.2rem;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Flux AI</div>
                    <div class="welcome-subtitle">Your intelligent companion.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Type here..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v27_1_history')) || [];
            let userName = localStorage.getItem('flux_user_name'); 
            let awaitingName = false; 
            let currentChatId = null;
            
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            // 🧠 NEURAL BG SCRIPT
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();
            class Particle {{
                constructor() {{ this.x = Math.random()*canvas.width; this.y = Math.random()*canvas.height; this.vx = (Math.random()-.5)*0.5; this.vy = (Math.random()-.5)*0.5; }}
                update() {{ this.x+=this.vx; this.y+=this.vy; if(this.x<0||this.x>canvas.width) this.vx*=-1; if(this.y<0||this.y>canvas.height) this.vy*=-1; }}
                draw() {{ ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent'); ctx.beginPath(); ctx.arc(this.x, this.y, 2, 0, Math.PI*2); ctx.fill(); }}
            }}
            for(let i=0; i<50; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach((p,i)=>{{
                    p.update(); p.draw();
                    particles.slice(i+1).forEach(p2=>{{
                        let d = Math.hypot(p.x-p2.x, p.y-p2.y);
                        if(d<100) {{
                            ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent').replace('rgb','rgba').replace(')',', '+ (1-d/100)*0.2 +')');
                            ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(p2.x,p2.y); ctx.stroke();
                        }}
                    }});
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            // INIT
            renderHistory(); renderSuggestions();
            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}
            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}
            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; toggleSidebar(); }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            
            // 🔥 CLEAR HISTORY FIX
            function confirmDelete() {{ localStorage.removeItem('flux_v27_1_history'); location.reload(); }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{ html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>'; }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Chat", messages: [] }});
                saveData(); renderHistory(); renderSuggestions();
                // 🔥 SHOW WELCOME SCREEN
                chatBox.innerHTML = ''; chatBox.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed'); overlay.style.display = 'none';
                msgInput.value = '';
            }}

            function saveData() {{ localStorage.setItem('flux_v27_1_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment"></i> ' + (chat.title || 'Chat').substring(0, 20);
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id);
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false));
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}

            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if(pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button'); btn.className='copy-btn'; btn.innerHTML='Copy';
                    btn.onclick = () => {{ navigator.clipboard.writeText(pre.querySelector('code').innerText); btn.innerHTML='Copied!'; setTimeout(()=>btn.innerHTML='Copy',2000); }};
                    pre.appendChild(btn);
                }});
            }}

            function checkForCode(text, bubble) {{
                if(text.includes('```html')) {{
                    const btn = document.createElement('button'); btn.className='run-code-btn'; btn.innerHTML='▶ Run Code';
                    btn.onclick = () => {{
                        document.getElementById('preview-modal').style.display='flex';
                        document.getElementById('code-frame').srcdoc = text.match(/```html([\\s\\S]*?)```/)[1];
                    }};
                    bubble.appendChild(btn);
                }}
            }}
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const div = document.createElement('div'); div.className = `message-wrapper ${{isUser?'user':'bot'}}`;
                div.innerHTML = `<div class="avatar ${{isUser?'user-avatar':'bot-avatar'}}">${{isUser?'<i class="fas fa-user"></i>':'<i class="fas fa-bolt"></i>'}}</div><div class="bubble-container"><div class="bubble">${{marked.parse(text)}}</div></div>`;
                chatBox.appendChild(div);
                if(!isUser) {{ hljs.highlightAll(); addCopyButtons(); checkForCode(text, div.querySelector('.bubble')); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                
                if(text==='!admin') {{ msgInput.value=''; document.getElementById('admin-auth-modal').style.display='flex'; return; }}
                
                const ball = document.createElement('div'); ball.className='energy-ball'; ball.style.left='50%'; 
                document.body.appendChild(ball); setTimeout(()=>ball.remove(),500);

                if(!currentChatId) startNewChat();
                const chat = chats.find(c=>c.id===currentChatId);
                chat.messages.push({{role:'user', text:text}});
                if(chat.messages.length===1) {{ chat.title = text.substring(0,18); renderHistory(); }}
                saveData(); msgInput.value=''; appendBubble(text, true);

                if(!userName && !awaitingName) {{ awaitingName=true; setTimeout(()=>appendBubble("Hello! What is your name?", false),600); return; }}
                if(awaitingName) {{ userName=text; localStorage.setItem('flux_user_name',userName); awaitingName=false; setTimeout(()=>appendBubble(`Nice to meet you, ${{userName}}!`, false),600); return; }}

                const context = chat.messages.map(m=>({{role:m.role, content:m.text}}));
                try {{
                    const res = await fetch('/chat', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{messages:context, user_name:userName}}) }});
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp='';
                    const div = document.createElement('div'); div.className='message-wrapper bot';
                    div.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="bubble"></div></div>`;
                    chatBox.appendChild(div); const bubble = div.querySelector('.bubble');
                    while(true) {{
                        const {{done, value}} = await reader.read(); if(done) break;
                        botResp += decoder.decode(value); bubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight }});
                    }}
                    chat.messages.push({{role:'assistant', text:botResp}}); saveData();
                    hljs.highlightAll(); addCopyButtons(); checkForCode(botResp, bubble);
                }} catch(e) {{ appendBubble("⚠️ Connection Error", false); }}
            }}

            async function verifyAdmin() {{
                if(document.getElementById('admin-pass').value === '{ADMIN_PASSWORD}') {{
                    closeModal('admin-auth-modal'); document.getElementById('admin-panel-modal').style.display='flex';
                    const res = await fetch('/admin/stats'); const data = await res.json();
                    document.getElementById('stat-msgs').innerText = data.total_messages;
                    document.getElementById('stat-uptime').innerText = data.uptime;
                }}
            }}
            async function toggleSystem() {{
                const res = await fetch('/admin/toggle_system', {{method:'POST'}}); const data = await res.json();
                const btn = document.getElementById('btn-toggle-sys');
                btn.innerText = data.active ? "System Online" : "System Offline";
                btn.style.background = data.active ? "var(--success)" : "var(--danger)";
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

    if messages and messages[-1]['role'] == 'user':
        math_result = solve_math_problem(messages[-1]['content'])
        if math_result:
            messages.insert(-1, {"role": "system", "content": f"⚡ FLUX MATH: Answer is {math_result}. Use this."})

    ctx = get_current_context()
    
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, an expert AI assistant.
        
        IDENTITY:
        - Created by {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
        
        CONTEXT:
        - Time: {ctx['time_local']}
        
        RULES:
        1. **NO SCRIPTS**: Reply naturally.
        2. **CODE**: Use ```html for web code.
        3. **IMAGE**: Output ONLY: ![Flux Image](https://image.pollinations.ai/prompt/{{english_prompt}})
        """
    }

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
                    messages=[sys_prompt] + messages,
                    stream=True,
                    temperature=0.7, 
                    max_tokens=1024
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content: yield chunk.choices[0].delta.content
                return
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ System overloaded."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
