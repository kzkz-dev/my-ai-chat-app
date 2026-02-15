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
# 🔹 Flux AI (Python Engine - Build 28.0.0) 🐍
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "28.0.0"
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
                --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 10, 25) 0%, rgb(5, 5, 10) 90%);
                --glass-bg: rgba(20, 20, 35, 0.65);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text: #e0e6ed;
                --text-secondary: #94a3b8;
                --accent: #00f3ff;
                --accent-glow: 0 0 10px rgba(0, 243, 255, 0.5);
                --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%);
                --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
                --danger: #ff0f7b;
                --success: #00ff87;
                --sidebar-bg: rgba(15, 15, 30, 0.95);
            }}

            body.light {{
                --bg-gradient: #f8fafc;
                --glass-bg: #ffffff;
                --sidebar-bg: #ffffff;
                --text: #1e293b;
                --text-secondary: #64748b;
                --glass-border: #e2e8f0;
                --accent: #2563eb;
                --bot-grad: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
                --user-grad: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg-gradient); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.3s ease;
            }}

            /* NEURAL BG */
            #neuro-bg {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: -1; pointer-events: none; opacity: 0.3;
            }}

            .glass {{ background: var(--glass-bg); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); }}

            /* SIDEBAR */
            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--glass-border);
                transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), background 0.3s ease;
                position: absolute; z-index: 200; left: 0; top: 0; 
                box-shadow: 10px 0 30px rgba(0,0,0,0.3); background: var(--sidebar-bg);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{
                width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); 
                color: var(--text); border: 1px solid var(--glass-border);
                border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px;
                margin-bottom: 20px; transition: all 0.3s ease;
            }}
            .new-chat-btn:active {{ transform: scale(0.97); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }}
            .history-item {{
                padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem;
                transition: all 0.2s; display: flex; align-items: center; gap: 10px; font-weight: 500;
            }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .about-section {{ 
                display: none; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 16px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--glass-border);
            }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.4rem; margin: 0 10px; transition: 0.3s; display: inline-block; }}
            
            .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 8px; }}
            .theme-btn.active {{ background: rgba(125,125,125,0.2); color: var(--text); }}

            header {{
                height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(15, 15, 30, 0.0); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.5); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; }}

            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 60px; padding-bottom: 100px; }}
            .icon-wrapper {{ 
                width: 90px; height: 90px; background: rgba(255,255,255,0.03);
                border: 1px solid var(--glass-border); border-radius: 25px; 
                display: flex; align-items: center; justify-content: center; font-size: 3.5rem; color: white; 
                margin-bottom: 20px; box-shadow: 0 0 30px rgba(0, 243, 255, 0.15);
                animation: levitate 4s ease-in-out infinite;
            }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 1rem; max-width: 80%; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; }}
            .chip {{
                padding: 16px 20px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 18px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.3s;
                font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 14px;
            }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .chip i {{ color: var(--accent); font-size: 1.1rem; }}

            .message-wrapper {{ display: flex; gap: 16px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1rem; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 88%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            .sender-name {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 5px; font-weight: 600; padding-left: 2px; text-transform: uppercase; }}
            
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; color: var(--text); }}
            .user .bubble {{ background: var(--user-grad); border-radius: 20px 4px 20px 20px; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .bubble strong {{ color: var(--accent); font-weight: 700; }}
            body.light .bubble strong {{ color: #2563eb; }}
            .bubble img {{ max-width: 100%; border-radius: 16px; margin-top: 12px; }}

            /* CODE & RUN BUTTON */
            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            .copy-btn {{
                position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.15); color: white; border: none;
                padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem;
            }}
            
            .run-code-btn {{
                display: inline-flex; align-items: center; gap: 8px; margin-top: 12px;
                padding: 8px 14px; background: rgba(125,125,125,0.1); color: var(--accent);
                border: 1px solid var(--accent); border-radius: 8px; font-weight: 600; cursor: pointer;
                transition: 0.3s; font-size: 0.9rem;
            }}
            .run-code-btn:hover {{ background: var(--accent); color: black; }}

            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); 
                display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--sidebar-bg); border-radius: 26px; padding: 8px 8px 8px 20px;
                border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(20px); transition: all 0.3s ease;
            }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 243, 255, 0.1); }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 12px 0; font-family: inherit; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 10px; margin-bottom: 2px; font-size: 1.2rem; }}

            .energy-ball {{
                position: fixed; width: 18px; height: 18px; background: var(--accent);
                border-radius: 50%; pointer-events: none; z-index: 9999;
                box-shadow: 0 0 15px var(--accent), 0 0 30px white;
                animation: shootUp 0.6s ease-in-out forwards;
            }}

            #preview-modal {{
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center;
                backdrop-filter: blur(8px);
            }}
            .preview-box {{ width: 95%; max-width: 600px; height: 85%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; }}
            .preview-header {{ padding: 12px 20px; background: #111; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; color: white; }}
            iframe {{ flex: 1; border: none; width: 100%; height: 100%; }}

            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(8px); }}
            .modal-box {{ background: var(--sidebar-bg); border: 1px solid var(--glass-border); padding: 30px; border-radius: 20px; width: 90%; max-width: 350px; text-align: center; color: var(--text); }}
            .btn-modal {{ padding: 12px; border-radius: 12px; border: none; font-weight: 600; cursor: pointer; flex: 1; margin: 0 6px; }}
            .btn-delete {{ background: var(--danger); color: white; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes shootUp {{ 0% {{ bottom: 80px; left: 50%; opacity: 1; transform: scale(1); }} 100% {{ bottom: 70%; left: 50%; opacity: 0; transform: scale(0.2); }} }}
            .typing {{ display: flex; gap: 6px; padding: 12px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="margin-bottom:10px;">Clear History?</h3>
                <div style="display:flex; margin-top:20px;">
                    <button class="btn-modal" onclick="closeModal('delete-modal')" style="background:rgba(125,125,125,0.15); color:var(--text);">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete All</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="margin-bottom:15px;">Admin Access</h3>
                <input type="password" id="admin-pass" style="width:100%; padding:14px; border-radius:12px; border:1px solid var(--glass-border); background:rgba(125,125,125,0.1); color:var(--text); margin-bottom:10px; outline:none; text-align:center;" placeholder="••••••••">
                <div id="admin-error-msg" style="color:var(--danger); font-size:0.9rem; margin-bottom:20px; display:none; font-weight:600;">Invalid Password</div>
                <div style="display:flex;">
                    <button class="btn-modal" onclick="closeModal('admin-auth-modal')" style="background:transparent; color:var(--text);">Cancel</button>
                    <button class="btn-modal" onclick="verifyAdmin()" style="background:var(--success); color:black;">Login</button>
                </div>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="margin-bottom:20px;">Dashboard</h3>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:25px;">
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-msgs" style="font-size:1.6rem; font-weight:700; color:var(--accent);">0</div><div>MSGS</div></div>
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-uptime" style="font-size:1.2rem; font-weight:700; color:var(--accent);">0s</div><div>UPTIME</div></div>
                </div>
                <button class="btn-modal btn-delete" id="btn-toggle-sys" onclick="toggleSystem()">Turn System OFF</button>
                <button class="btn-modal" onclick="closeModal('admin-panel-modal')" style="margin-top:15px; background:transparent; color:var(--text-secondary);">Close</button>
            </div>
        </div>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span>Live Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:5px 12px; border-radius:6px; cursor:pointer;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>

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
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                <div id="about-info" class="about-section">
                    <strong style="font-size:1.2rem; display:block; margin-bottom:5px; color:var(--text);">{APP_NAME}</strong>
                    <span style="font-size:0.8rem; opacity:0.7; color:var(--text);">v{VERSION}</span><br>
                    <small style="color:var(--text-secondary)">Created by <span style="color:var(--accent)">{OWNER_NAME}</span></small><br>
                    <div style="margin:15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="display:block; margin-top:5px; font-weight:500; opacity:0.5; color:var(--text);">&copy; 2026</small>
                </div>
                <div class="history-item" onclick="openDeleteModal('delete-modal')" style="color:#ff0f7b;"><i class="fas fa-trash-alt"></i> Delete History</div>
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
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your intelligent AI companion.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask Flux..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v28_history')) || [];
            let userName = localStorage.getItem('flux_user_name_v2'); 
            let awaitingName = false; 
            let currentChatId = null;
            
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            // 🧠 NEURAL BG
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas); resizeCanvas();
            class Particle {{
                constructor() {{ this.x=Math.random()*canvas.width; this.y=Math.random()*canvas.height; this.vx=(Math.random()-.5)*0.5; this.vy=(Math.random()-.5)*0.5; }}
                update() {{ this.x+=this.vx; this.y+=this.vy; if(this.x<0||this.x>canvas.width)this.vx*=-1; if(this.y<0||this.y>canvas.height)this.vy*=-1; }}
                draw() {{ ctx.fillStyle=getComputedStyle(document.body).getPropertyValue('--accent'); ctx.beginPath(); ctx.arc(this.x,this.y,2,0,Math.PI*2); ctx.fill(); }}
            }}
            for(let i=0; i<60; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach((p,i)=>{{
                    p.update(); p.draw();
                    particles.slice(i+1).forEach(p2=>{{
                        let d=Math.hypot(p.x-p2.x, p.y-p2.y);
                        if(d<100) {{ ctx.strokeStyle=getComputedStyle(document.body).getPropertyValue('--accent').replace('rgb','rgba').replace(')',', '+(1-d/100)*0.2+')'); ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(p2.x,p2.y); ctx.stroke(); }}
                    }});
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}

            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{ html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>'; }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData(); renderHistory(); renderSuggestions();
                chatBox.innerHTML = ''; chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed'); overlay.style.display = 'none';
                msgInput.value = ''; resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v28_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Conversation').substring(0, 22) + '</span>';
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false));
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}

            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if (pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button'); btn.className = 'copy-btn'; btn.innerHTML = '<i class="fas fa-copy"></i>';
                    btn.onclick = () => {{ navigator.clipboard.writeText(pre.querySelector('code').innerText); btn.innerHTML = '<i class="fas fa-check"></i>'; setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i>', 2000); }};
                    pre.appendChild(btn);
                }});
            }}

            function checkForCode(text, bubble) {{
                // HTML/JS PREVIEW
                if(text.includes('```html')) {{
                    const btn = document.createElement('button'); btn.className = 'run-code-btn'; btn.innerHTML = '<i class="fas fa-play"></i> Preview';
                    btn.onclick = () => {{ 
                        document.getElementById('preview-modal').style.display = 'flex'; 
                        document.getElementById('code-frame').srcdoc = text.match(/```html([\\s\\S]*?)```/)[1]; 
                    }};
                    bubble.appendChild(btn);
                }}
                // PYTHON RUNNER (Client-side via Pyodide logic simulation or Server if safe - here we use simulation for HTML preview for now, but text implies full python)
                if(text.includes('```python')) {{
                    const btn = document.createElement('button'); btn.className = 'run-code-btn'; btn.innerHTML = '<i class="fas fa-play"></i> Run Code';
                    btn.onclick = () => {{
                        const code = text.match(/```python([\\s\\S]*?)```/)[1];
                        // Inject Pyodide runner into iframe
                        const html = `<html><head><script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"><\/script><style>body{background:#111;color:#0f0;font-family:monospace;padding:20px;}</style></head><body><div id="out">Initializing Python...</div><script>async function main(){let pyodide=await loadPyodide();document.getElementById("out").innerText=">> Python Ready\\n";pyodide.setStdout({batched:(m)=>{document.getElementById("out").innerText+=m+"\\n"}});try{await pyodide.runPythonAsync(\`${{code.replace(/`/g, '\\`').replace(/\$/g, '\\$')}}\`)}catch(e){document.getElementById("out").innerText+="Error: "+e}}main()<\/script></body></html>`;
                        document.getElementById('preview-modal').style.display = 'flex'; 
                        document.getElementById('code-frame').srcdoc = html;
                    }};
                    bubble.appendChild(btn);
                }}
            }}
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            function playSentAnimation() {{
                const ball = document.createElement('div'); ball.className = 'energy-ball'; ball.style.left = '50%';
                document.body.appendChild(ball); setTimeout(() => ball.remove(), 500);
            }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div><div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                const bubble = wrapper.querySelector('.bubble');
                bubble.innerHTML = marked.parse(text);
                if(!isUser) {{ hljs.highlightAll(); addCopyButtons(); checkForCode(text, bubble); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div'); wrapper.id = 'typing-indicator'; wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble" style="background:transparent; padding-left:0;"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div></div>`;
                chatBox.appendChild(wrapper); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}
            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                if(text === '!admin') {{ msgInput.value = ''; openModal('admin-auth-modal'); document.getElementById('admin-error-msg').style.display='none'; return; }}

                playSentAnimation();
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData(); msgInput.value = ''; appendBubble(text, true);

                if(!userName && !awaitingName) {{
                    awaitingName = true; setTimeout(() => appendBubble("Hello! I am Flux AI. What should I call you?", false), 600); return;
                }}
                if(awaitingName) {{
                    userName = text; localStorage.setItem('flux_user_name_v2', userName); awaitingName = false;
                    setTimeout(() => appendBubble(`Nice to meet you, ${{userName}}! I'll remember that.`, false), 600); return;
                }}

                showTyping();
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context, user_name: userName }}) }});
                    removeTyping();
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp = '';
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper); const bubble = wrapper.querySelector('.bubble');
                    while(true) {{
                        const {{ done, value }} = await reader.read(); if(done) break;
                        botResp += decoder.decode(value); bubble.innerHTML = marked.parse(botResp); chatBox.scrollTo({{ top: chatBox.scrollHeight }});
                    }}
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData(); hljs.highlightAll(); addCopyButtons(); checkForCode(botResp, bubble);
                }} catch(e) {{ removeTyping(); appendBubble("⚠️ Connection Error.", false); }}
            }}

            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function openDeleteModal(id) {{ openModal(id); }}
            function confirmDelete() {{ localStorage.removeItem('flux_v28_history'); location.reload(); }}
            async function verifyAdmin() {{ if(document.getElementById('admin-pass').value==='{ADMIN_PASSWORD}'){{ closeModal('admin-auth-modal'); openModal('admin-panel-modal'); }} else {{ document.getElementById('admin-error-msg').style.display='block'; }} }}
            async function toggleSystem() {{ const res = await fetch('/admin/toggle_system', {{ method: 'POST' }}); const data = await res.json(); document.getElementById('btn-toggle-sys').innerText = data.active?"Turn System OFF":"Turn System ON"; }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
            renderHistory(); renderSuggestions();
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
    user_name = data.get("user_name", "User") 

    if messages and messages[-1]['role'] == 'user':
        math_result = solve_math_problem(messages[-1]['content'])
        if math_result:
            messages.insert(-1, {{"role": "system", "content": f"⚡ MATH TOOL: Answer is {{math_result}}. State it clearly."}})

    ctx = get_current_context()
    
    sys_prompt_content = f"""
    You are {APP_NAME}, a smart and concise AI assistant for students.
    
    IDENTITY:
    - Name: {APP_NAME}
    - Created by: {OWNER_NAME} (Bangla: {OWNER_NAME_BN}). Only mention if asked.
    - User Name: {user_name}. Use this name.
    
    CONTEXT:
    - Time: {ctx['time_utc']} (UTC). Only give Local Time ({ctx['time_local']}) if explicitly asked.
    
    RULES:
    1. **CONCISE**: Be direct and helpful. No fluff.
    2. **CODING**: Always use markdown blocks (```python, ```html) so the 'Run Code' button works.
    3. **IMAGE**: Output ONLY: ![Flux Image](https://image.pollinations.ai/prompt/{{english_prompt}})
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
