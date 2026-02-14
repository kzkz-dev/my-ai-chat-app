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
# 🔹 Flux AI (Ultimate Complete - Build 26.0.0) ⚡
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "26.0.0"
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
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Inter:wght@300;400;600&family=Noto+Sans+Bengali:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --hue: 200; /* Flux Blue */
                --bg: #0b0f19;
                --sidebar: #111827;
                --text: #f3f4f6;
                --text-secondary: #9ca3af;
                --input-bg: #1f2937;
                --border: #374151;
                --accent: #3b82f6;
                --glow: 0 0 15px rgba(59, 130, 246, 0.5);
                --danger: #ef4444;
                --success: #10b981;
                --font-main: 'Inter', sans-serif;
                --font-header: 'Orbitron', sans-serif;
            }}
            
            body.light {{
                --bg: #ffffff;
                --sidebar: #f3f4f6;
                --text: #1f2937;
                --text-secondary: #4b5563;
                --input-bg: #e5e7eb;
                --border: #d1d5db;
                --accent: #2563eb;
                --glow: 0 0 10px rgba(37, 99, 235, 0.2);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: var(--font-main); height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.3s ease, color 0.3s ease;
            }}

            /* 🌌 NEURAL BACKGROUND */
            #neuro-bg {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: -1; pointer-events: none; opacity: 0.4;
            }}

            /* SIDEBAR */
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); 
                position: absolute; z-index: 200; left: 0; top: 0; 
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 10px 0 30px rgba(0,0,0,0.5);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ 
                font-family: var(--font-header); font-size: 1.6rem; font-weight: 800; 
                margin-bottom: 25px; display: flex; align-items: center; gap: 10px; 
                color: var(--text); letter-spacing: 1px; text-shadow: var(--glow);
            }}
            .brand i {{ color: var(--accent); }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--input-bg); 
                color: var(--accent); border: 1px solid var(--border);
                border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 10px;
                margin-bottom: 20px; transition: 0.3s;
            }}
            .new-chat-btn:active {{ transform: scale(0.98); border-color: var(--accent); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{
                padding: 12px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); 
                font-size: 0.95rem; transition: background 0.2s; display: flex; align-items: center; gap: 10px;
            }}
            .history-item:hover, .history-item:active {{ background: var(--input-bg); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px; }}
            
            /* DARK/LIGHT TOGGLE */
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 4px; border-radius: 8px; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 6px; }}
            .theme-btn.active {{ background: var(--bg); color: var(--accent); font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}

            /* ABOUT SECTION */
            .about-section {{ 
                display: none; background: var(--input-bg); padding: 15px; border-radius: 12px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--border);
                animation: fadeIn 0.3s;
            }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.2rem; margin: 0 10px; }}
            .about-link:hover {{ color: var(--accent); }}

            /* MAIN AREA */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 18px;
                background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.8); }}

            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 18px 140px 18px; display: flex; flex-direction: column; gap: 24px; }}

            /* 🧠 JARVIS ORB (STYLED FOR FLUX) */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding-top: 60px;
            }}
            .orb-container {{
                width: 100px; height: 100px; position: relative; margin-bottom: 25px;
                display: flex; justify-content: center; align-items: center;
            }}
            .orb {{
                position: absolute; width: 100%; height: 100%; border-radius: 50%;
                border: 3px solid var(--accent); border-top-color: transparent; border-bottom-color: transparent;
                animation: spin 3s linear infinite; box-shadow: var(--glow);
            }}
            .orb-core {{
                width: 40px; height: 40px; background: var(--accent); border-radius: 50%;
                box-shadow: 0 0 20px var(--accent); animation: pulse 2s ease-in-out infinite;
            }}
            
            .welcome-title {{ font-family: var(--font-header); font-size: 2rem; font-weight: 700; margin-bottom: 10px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 30px; font-size: 1rem; }}

            /* SUGGESTIONS */
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; width: 100%; max-width: 700px; }}
            .chip {{
                padding: 14px; background: var(--input-bg); border: 1px solid var(--border); border-radius: 12px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: 0.3s;
                font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 10px;
            }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); }}
            .chip i {{ color: var(--accent); }}

            /* MESSAGES & COPY BUTTON */
            .message-wrapper {{ display: flex; gap: 12px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.3s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
            .bot-avatar {{ background: var(--accent); color: white; }}
            .user-avatar {{ background: var(--input-bg); border: 1px solid var(--border); color: var(--text); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 88%; min-width: 0; }} /* min-width: 0 prevents overflow */
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            
            .bubble {{ 
                padding: 12px 16px; border-radius: 16px; font-size: 1rem; line-height: 1.6; 
                word-wrap: break-word; overflow-wrap: break-word;
            }}
            .bot .bubble {{ background: transparent; padding-left: 0; width: 100%; }}
            .user .bubble {{ background: var(--input-bg); border: 1px solid var(--border); color: var(--text); border-radius: 16px 4px 16px 16px; }}

            /* 🔥 CODE BLOCK & COPY BUTTON FIX */
            pre {{ 
                background: #0d1117 !important; padding: 15px; border-radius: 10px; 
                overflow-x: auto; border: 1px solid var(--border); position: relative;
                margin-top: 10px; max-width: 100%;
            }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            
            .copy-btn {{
                position: absolute; top: 8px; right: 8px;
                background: rgba(255, 255, 255, 0.1); color: #fff;
                border: none; padding: 5px 10px; border-radius: 5px;
                cursor: pointer; font-size: 0.8rem; transition: 0.2s;
            }}
            .copy-btn:hover {{ background: var(--accent); }}

            /* 🔥 RUN CODE BUTTON */
            .run-code-btn {{
                display: inline-flex; align-items: center; gap: 8px; margin-top: 10px;
                padding: 8px 14px; background: var(--input-bg); color: var(--accent);
                border: 1px solid var(--accent); border-radius: 8px; font-weight: 600; cursor: pointer;
                transition: 0.3s; font-size: 0.85rem;
            }}
            .run-code-btn:hover {{ background: var(--accent); color: white; }}

            /* INPUT AREA */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 90%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border: 1px solid var(--border);
                border-radius: 20px; padding: 10px 10px 10px 20px; backdrop-filter: blur(10px);
                box-shadow: var(--shadow-input); transition: 0.3s;
            }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: var(--glow); }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 10px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 42px; height: 42px;
                border-radius: 12px; cursor: pointer; margin-left: 10px;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s;
            }}
            .send-btn:hover {{ background: var(--accent); color: white; }}

            /* 🔥 ENERGY TRAIL (BRANDED) */
            .energy-ball {{
                position: fixed; width: 15px; height: 15px; background: var(--accent);
                border-radius: 50%; pointer-events: none; z-index: 9999;
                box-shadow: 0 0 20px var(--accent);
                animation: shootUp 0.5s ease-in-out forwards;
            }}

            /* PREVIEW MODAL */
            #preview-modal {{
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center;
                backdrop-filter: blur(5px);
            }}
            .preview-box {{
                width: 95%; max-width: 500px; height: 80%; background: white; border-radius: 12px; overflow: hidden;
                display: flex; flex-direction: column; box-shadow: 0 0 50px rgba(0,0,0,0.5); border: 2px solid var(--accent);
            }}
            .preview-header {{
                padding: 10px 15px; background: #111; color: white; display: flex; justify-content: space-between; align-items: center;
            }}
            iframe {{ flex: 1; border: none; width: 100%; height: 100%; }}

            /* ANIMATIONS */
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            @keyframes pulse {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(0.8); opacity: 0.7; }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes shootUp {{ 0% {{ bottom: 80px; left: 50%; opacity: 1; transform: scale(1); }} 100% {{ bottom: 70%; left: 50%; opacity: 0; transform: scale(0.2); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}

            .typing {{ display: flex; gap: 6px; padding: 10px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            
            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; }}
            .modal-box {{ background: var(--sidebar); border: 1px solid var(--border); padding: 25px; border-radius: 16px; width: 90%; max-width: 350px; text-align: center; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700;">Live Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:5px 12px; border-radius:5px; cursor:pointer;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>

        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--text); margin-bottom:10px;">Delete History?</h3>
                <div style="display:flex; gap:10px; margin-top:20px;">
                    <button onclick="closeModal('delete-modal')" style="flex:1; padding:10px; background:var(--input-bg); color:var(--text); border:none; border-radius:6px;">Cancel</button>
                    <button onclick="confirmDelete()" style="flex:1; padding:10px; background:var(--danger); color:white; border:none; border-radius:6px;">Delete</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--accent);">Admin Access</h3>
                <input type="password" id="admin-pass" style="width:100%; padding:10px; margin:15px 0; background:rgba(0,0,0,0.3); border:1px solid var(--border); color:var(--text); text-align:center; border-radius:6px;" placeholder="Password">
                <button onclick="verifyAdmin()" style="width:100%; padding:10px; background:var(--accent); color:white; border:none; border-radius:6px; font-weight:bold;">Login</button>
                <button onclick="closeModal('admin-auth-modal')" style="margin-top:10px; background:transparent; border:none; color:var(--text-secondary);">Cancel</button>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box">
                <h3>Dashboard</h3>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0;">
                    <div style="background:var(--input-bg); padding:10px; border-radius:8px;"><div id="stat-msgs" style="font-size:1.5rem; font-weight:bold; color:var(--accent);">0</div><small>Messages</small></div>
                    <div style="background:var(--input-bg); padding:10px; border-radius:8px;"><div id="stat-uptime" style="font-size:1.2rem; font-weight:bold; color:var(--accent);">0s</div><small>Uptime</small></div>
                </div>
                <button id="btn-toggle-sys" onclick="toggleSystem()" style="width:100%; padding:12px; background:var(--success); color:white; border:none; border-radius:6px;">System Online</button>
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
                    <small>Created by {OWNER_NAME}</small><br>
                    <small style="opacity:0.7">All rights reserved by {OWNER_NAME} &copy; 2026</small>
                </div>
                <div class="history-item" style="color:var(--danger);" onclick="openDeleteModal('delete-modal')"><i class="fas fa-trash"></i> Clear Data</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-family:var(--font-header); font-weight:700;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="orb-container"><div class="orb"></div><div class="orb-core"></div></div>
                    <div class="welcome-title">Flux AI</div>
                    <div class="welcome-subtitle">Your intelligent companion.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message Flux AI..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v26_history')) || [];
            let userName = localStorage.getItem('flux_user_name'); 
            let awaitingName = false; 
            let currentChatId = null;
            
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            // 1. NEURAL BG SETUP (Blue/Cyan)
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();
            class Particle {{
                constructor() {{
                    this.x = Math.random()*canvas.width; this.y = Math.random()*canvas.height;
                    this.vx = (Math.random()-.5)*0.5; this.vy = (Math.random()-.5)*0.5;
                }}
                update() {{
                    this.x+=this.vx; this.y+=this.vy;
                    if(this.x<0||this.x>canvas.width) this.vx*=-1;
                    if(this.y<0||this.y>canvas.height) this.vy*=-1;
                }}
                draw() {{
                    ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent');
                    ctx.beginPath(); ctx.arc(this.x, this.y, 2, 0, Math.PI*2); ctx.fill();
                }}
            }}
            for(let i=0; i<50; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach((p,i)=>{{
                    p.update(); p.draw();
                    particles.slice(i+1).forEach(p2=>{{
                        let d = Math.hypot(p.x-p2.x, p.y-p2.y);
                        if(d<100) {{
                            ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent').replace(')', ', ' + (1-d/100) + ')').replace('rgb', 'rgba');
                            ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(p2.x,p2.y); ctx.stroke();
                        }}
                    }});
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            // 2. COPY BUTTON LOGIC
            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if (pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button');
                    btn.className = 'copy-btn';
                    btn.innerHTML = '<i class="fas fa-copy"></i>';
                    btn.onclick = () => {{
                        const code = pre.querySelector('code').innerText;
                        navigator.clipboard.writeText(code);
                        btn.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i>', 2000);
                    }};
                    pre.appendChild(btn);
                }});
            }}

            // 3. THEME TOGGLE
            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}

            renderHistory(); renderSuggestions();

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
                welcomeScreen.style.display = 'flex'; sidebar.classList.add('closed');
                overlay.style.display = 'none';
            }}

            function saveData() {{ localStorage.setItem('flux_v26_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment"></i> <span>' + (chat.title || 'New Conversation').substring(0, 20) + '</span>';
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id);
                if(!chat) return;
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false));
                addCopyButtons();
                sidebar.classList.add('closed'); overlay.style.display = 'none';
            }}

            function checkForCode(text, bubble) {{
                if(text.includes('```html')) {{
                    const btn = document.createElement('button');
                    btn.className = 'run-code-btn';
                    btn.innerHTML = '<i class="fas fa-play"></i> Run Code';
                    btn.onclick = () => {{
                        const code = text.match(/```html([\\s\\S]*?)```/)[1];
                        document.getElementById('preview-modal').style.display = 'flex';
                        document.getElementById('code-frame').srcdoc = code;
                    }};
                    bubble.appendChild(btn);
                }}
            }}
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div><div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                const bubble = wrapper.querySelector('.bubble');
                bubble.innerHTML = marked.parse(text);
                
                if(!isUser) {{
                    hljs.highlightAll();
                    addCopyButtons();
                    checkForCode(text, bubble);
                }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div'); wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble" style="padding:10px;"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div></div>`;
                chatBox.appendChild(wrapper); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}
            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                
                if(text === '!admin') {{ msgInput.value=''; document.getElementById('admin-auth-modal').style.display='flex'; return; }}

                // Energy Trail
                const ball = document.createElement('div'); ball.className='energy-ball'; ball.style.left='50%';
                document.body.appendChild(ball); setTimeout(()=>ball.remove(), 500);

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData(); msgInput.value = ''; appendBubble(text, true);

                if(!userName && !awaitingName) {{
                    awaitingName = true; setTimeout(()=>appendBubble("Hello! May I know your name?", false), 600); return;
                }}
                if(awaitingName) {{
                    userName = text; localStorage.setItem('flux_user_name', userName); awaitingName = false;
                    setTimeout(()=>appendBubble(`Nice to meet you, ${{userName}}!`, false), 600); return;
                }}

                showTyping();
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context }}) }});
                    removeTyping();
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp = '';
                    
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper); const bubble = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read(); if(done) break;
                        botResp += decoder.decode(value);
                        bubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight }});
                    }}
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData(); hljs.highlightAll(); addCopyButtons(); checkForCode(botResp, bubble);
                }} catch(e) {{ removeTyping(); appendBubble("⚠️ Connection Error.", false); }}
            }}

            // ADMIN LOGIC
            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v26_history'); location.reload(); }}
            async function verifyAdmin() {{
                if(document.getElementById('admin-pass').value === '{ADMIN_PASSWORD}') {{
                    closeModal('admin-auth-modal'); openModal('admin-panel-modal');
                    const res = await fetch('/admin/stats'); const data = await res.json();
                    document.getElementById('stat-msgs').innerText = data.total_messages;
                    document.getElementById('stat-uptime').innerText = data.uptime;
                }}
            }}
            async function toggleSystem() {{
                const res = await fetch('/admin/toggle_system', {{ method: 'POST' }}); const data = await res.json();
                const btn = document.getElementById('btn-toggle-sys');
                btn.innerText = data.active ? "Turn System OFF" : "Turn System ON";
                btn.style.background = data.active ? "var(--danger)" : "var(--success)";
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
    
    if messages and messages[-1]['role'] == 'user':
        math_result = solve_math_problem(messages[-1]['content'])
        if math_result:
            messages.insert(-1, {{"role": "system", "content": f"⚡ MATH TOOL: Answer is {{math_result}}."}})

    ctx = get_current_context()
    
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a friendly and expert AI.
        
        IDENTITY:
        - Created by {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
        
        CONTEXT:
        - Time: {ctx['time_local']}
        
        RULES:
        1. **CODING**: Provide complete code snippets.
        2. **HTML**: Use ```html blocks for web code.
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