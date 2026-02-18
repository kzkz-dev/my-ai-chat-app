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
# 🔹 Flux AI (Stable + Propose Feature - Build 33.0.0) 🧠💘
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "33.0.0"
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
        "date": now_dhaka.strftime("%d %B, %Y"),
        "day": now_dhaka.strftime("%A")
    }

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

# 💘 PROPOSE PAGE HTML (Clean & Fixed)
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
        
        /* Fixed Image Container (No White Box) */
        .gif-container {
            width: 200px; height: 200px; margin: 0 auto 20px auto;
            border-radius: 20px; overflow: hidden; background: transparent;
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
    </style>
</head>
<body>
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

        // Event Listeners for Mobile & Desktop
        noBtn.addEventListener('mouseover', moveButton);
        noBtn.addEventListener('touchstart', (e) => { e.preventDefault(); moveButton(); });
        noBtn.addEventListener('click', (e) => { e.preventDefault(); moveButton(); });

        function moveButton() {
            if (noBtn.style.position !== 'absolute') {
                noBtn.style.position = 'fixed'; 
            }
            // Safe Boundary Calculation
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
            
            // Confetti
            for(let i=0; i<60; i++) {
                setTimeout(createConfetti, i * 20);
            }
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

SUGGESTION_POOL = [
    {"icon": "fas fa-heart", "text": "Create a propose link for Sadia"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"},
    {"icon": "fas fa-plane", "text": "Trip plan for Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Business ideas for students"},
    {"icon": "fas fa-laptop-code", "text": "Python calculator code"},
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
            :root {{
                --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 10, 25) 0%, rgb(5, 5, 10) 90%);
                --glass-bg: rgba(20, 20, 35, 0.65);
                --sidebar-bg: rgba(15, 15, 30, 0.95);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text: #e0e6ed;
                --text-secondary: #94a3b8;
                --accent: #00f3ff;
                --accent-glow: 0 0 10px rgba(0, 243, 255, 0.5);
                --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%);
                --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
                --danger: #ff0f7b;
                --success: #00ff87;
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
            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }}
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
            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{
                padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem;
                transition: all 0.2s; display: flex; align-items: center; gap: 10px; font-weight: 500;
            }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); color: var(--text); }}
            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            .about-section {{ display: none; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 16px; margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--glass-border); }}
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
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; }}
            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 60px; padding-bottom: 100px; }}
            .icon-wrapper {{ 
                width: 90px; height: 90px; background: rgba(255,255,255,0.03);
                border: 1px solid var(--glass-border); border-radius: 25px; 
                display: flex; align-items: center; justify-content: center; font-size: 3.5rem; color: white; 
                margin-bottom: 20px; box-shadow: 0 0 30px rgba(0, 243, 255, 0.15); animation: levitate 4s ease-in-out infinite;
            }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 1rem; max-width: 80%; line-height: 1.5; }}
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; width: 100%; max-width: 750px; }}
            .chip {{
                padding: 16px 20px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 18px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.3s;
                font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 14px;
            }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .chip i {{ color: var(--accent); font-size: 1.1rem; opacity: 0.9; }}
            .message-wrapper {{ display: flex; gap: 16px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1rem; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            .bubble-container {{ display: flex; flex-direction: column; max-width: 88%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            .sender-name {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 5px; font-weight: 600; padding-left: 2px; text-transform: uppercase; }}
            .message-wrapper.user .sender-name {{ display: none; }}
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; position: relative; }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; color: var(--text); }}
            .user .bubble {{ background: var(--user-grad); border-radius: 20px 4px 20px 20px; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .bubble strong {{ color: var(--accent); font-weight: 700; }}
            body.light .bubble strong {{ color: #2563eb; }}
            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            .copy-btn {{ position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.15); color: white; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; }}
            .run-code-btn {{ display: inline-flex; align-items: center; gap: 8px; margin-top: 12px; padding: 8px 14px; background: rgba(125,125,125,0.1); color: var(--accent); border: 1px solid var(--accent); border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.3s; font-size: 0.9rem; }}
            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; }}
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 26px; padding: 8px 8px 8px 20px; border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); transition: all 0.3s ease; }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 243, 255, 0.1); }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 12px 0; font-family: inherit; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 10px; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; }}
            .energy-ball {{ position: fixed; width: 18px; height: 18px; background: var(--accent); border-radius: 50%; pointer-events: none; z-index: 9999; box-shadow: 0 0 15px var(--accent), 0 0 30px white; animation: shootUp 0.6s ease-in-out forwards; }}
            #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; backdrop-filter: blur(8px); }}
            .preview-box {{ width: 90%; height: 85%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }}
            .preview-header {{ padding: 12px 20px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
            iframe {{ flex: 1; border: none; width: 100%; height: 100%; }}
            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(8px); }}
            .modal-box {{ background: var(--sidebar-bg); border: 1px solid var(--glass-border); padding: 30px; border-radius: 20px; width: 90%; max-width: 350px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.3); color: var(--text); }}
            .modal-title {{ font-size: 1.4rem; margin-bottom: 10px; font-weight: 700; }}
            .modal-desc {{ color: var(--text-secondary); margin-bottom: 25px; line-height: 1.5; }}
            .btn-modal {{ padding: 12px; border-radius: 12px; border: none; font-weight: 600; cursor: pointer; flex: 1; margin: 0 6px; font-size: 0.9rem; transition: 0.2s; }}
            .btn-cancel {{ background: rgba(125,125,125,0.15); color: var(--text); }}
            .btn-delete {{ background: var(--danger); color: white; }}
            .btn-confirm {{ background: var(--success); color: black; }}
            .typing {{ display: flex; gap: 6px; padding: 12px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes shootUp {{ 0% {{ bottom: 80px; left: 50%; opacity: 1; transform: scale(1); }} 100% {{ bottom: 70%; left: 50%; opacity: 0; transform: scale(0.2); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>
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
                <input type="password" id="admin-pass" style="width:100%; padding:14px; border-radius:12px; border:1px solid var(--glass-border); background:rgba(125,125,125,0.1); color:var(--text); margin-bottom:10px; outline:none; font-size:1rem; text-align:center;" placeholder="••••••••">
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
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:25px;">
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-msgs" style="font-size:1.6rem; font-weight:700; color:var(--accent);">0</div><div style="font-size:0.8rem; opacity:0.7">TOTAL MSGS</div></div>
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-uptime" style="font-size:1.2rem; font-weight:700; color:var(--accent);">0s</div><div style="font-size:0.8rem; opacity:0.7">UPTIME</div></div>
                </div>
                <button class="btn-modal btn-delete" id="btn-toggle-sys" onclick="toggleSystem()" style="width:100%; margin:0; padding:16px;">Turn System OFF</button>
                <button class="btn-modal btn-cancel" onclick="closeModal('admin-panel-modal')" style="width:100%; margin:15px 0 0 0;">Close Panel</button>
            </div>
        </div>
        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700; color:#111;">Live Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-weight:600;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>
        <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div style="font-size:0.75rem; font-weight: 700; color:var(--text-secondary); margin-bottom:12px; letter-spacing: 1px; opacity:0.8;">RECENT</div>
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
                    <small style="display:block; margin-top:5px; font-weight:500; opacity:0.5; color:var(--text);">&copy; 2026 All Rights Reserved by {OWNER_NAME}</small>
                </div>
                <div class="history-item" onclick="openDeleteModal('delete-modal')" style="color:#ff0f7b;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>
        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer; padding: 8px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.4rem; letter-spacing: -0.5px; background: linear-gradient(to right, var(--text), var(--text-secondary)); -webkit-background-clip: text; color: transparent;">{APP_NAME}</span>
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
                    <textarea id="msg" placeholder="Ask Flux..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>
        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v27_2_history')) || [];
            let userName = localStorage.getItem('flux_user_name_fixed'); 
            let awaitingName = false; 
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');
            
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas); resizeCanvas();
            class Particle {{
                constructor() {{ this.x=Math.random()*canvas.width; this.y=Math.random()*canvas.height; this.vx=(Math.random()-.5)*0.5; this.vy=(Math.random()-.5)*0.5; this.size=Math.random()*2; }}
                update() {{ this.x+=this.vx; this.y+=this.vy; if(this.x<0||this.x>canvas.width)this.vx*=-1; if(this.y<0||this.y>canvas.height)this.vy*=-1; }}
                draw() {{ ctx.fillStyle=getComputedStyle(document.body).getPropertyValue('--accent'); ctx.beginPath(); ctx.arc(this.x,this.y,this.size,0,Math.PI*2); ctx.fill(); }}
            }}
            for(let i=0; i<60; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach((p,i)=>{{ p.update(); p.draw();
                    for(let j=i; j<particles.length; j++) {{
                        const dx=p.x-particles[j].x; const dy=p.y-particles[j].y; const dist=Math.sqrt(dx*dx+dy*dy);
                        if(dist<100) {{ ctx.strokeStyle=getComputedStyle(document.body).getPropertyValue('--accent').replace('rgb','rgba').replace(')',', '+(1-dist/100)*0.2+')'); ctx.lineWidth=0.5; ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(particles[j].x,particles[j].y); ctx.stroke(); }}
                    }}
                }}); requestAnimationFrame(animateBg);
            }}
            animateBg();

            function setTheme(mode) {{
                document.body.className = mode;
                document.getElementById('btn-dark').className = mode==='dark'?'theme-btn active':'theme-btn';
                document.getElementById('btn-light').className = mode==='light'?'theme-btn active':'theme-btn';
            }}
            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
                const selected = shuffled.slice(0, 4);
                let html = '';
                selected.forEach(s => {{ html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>'; }});
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
            function saveData() {{ localStorage.setItem('flux_v27_2_history', JSON.stringify(chats)); }}
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
                if (chat.messages.length === 0) {{ chatBox.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex'; }} 
                else {{ chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false)); }}
                sidebar.classList.add('closed'); overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}
            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if (pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button'); btn.className = 'copy-btn'; btn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    btn.onclick = () => {{ navigator.clipboard.writeText(pre.querySelector('code').innerText); btn.innerHTML = '<i class="fas fa-check"></i> Copied'; setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i> Copy', 2000); }};
                    pre.appendChild(btn);
                }});
            }}
            function checkForCode(text, bubble) {{
                if(text.includes('```html')) {{
                    const btn = document.createElement('button'); btn.className = 'run-code-btn'; btn.innerHTML = '<i class="fas fa-play"></i> Run Code';
                    btn.onclick = () => {{
                        const code = text.match(/```html([\\s\\S]*?)```/)[1];
                        document.getElementById('preview-modal').style.display = 'flex';
                        document.getElementById('code-frame').srcdoc = code;
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
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container">${{name}}<div class="bubble"></div></div>`;
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
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}
            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                if(text === '!admin') {{ msgInput.value = ''; openModal('admin-auth-modal'); document.getElementById('admin-error-msg').style.display = 'none'; return; }}
                playSentAnimation(); 
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData(); msgInput.value = ''; appendBubble(text, true);
                if(!userName && !awaitingName) {{ awaitingName = true; setTimeout(() => {{ appendBubble("Hello! I am Flux AI. What should I call you?", false); }}, 600); return; }}
                if(awaitingName) {{ userName = text; localStorage.setItem('flux_user_name_fixed', userName); awaitingName = false; setTimeout(() => {{ appendBubble(`Nice to meet you, ${{userName}}! How can I help you today?`, false); }}, 600); return; }}
                showTyping();
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context, user_name: userName }}) }});
                    removeTyping(); if(!res.ok) throw new Error("System Offline");
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp = '';
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper); const bubbleDiv = wrapper.querySelector('.bubble');
                    while(true) {{
                        const {{ done, value }} = await reader.read(); if(done) break;
                        botResp += decoder.decode(value);
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    chat.messages.push({{ role: 'assistant', text: botResp }}); saveData(); hljs.highlightAll(); addCopyButtons(); checkForCode(botResp, bubbleDiv);
                }} catch(e) {{ removeTyping(); appendBubble("⚠️ System connection error. Please try again.", false); }}
            }}
            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function openDeleteModal(id) {{ openModal(id); }}
            function confirmDelete() {{ localStorage.removeItem('flux_v27_2_history'); location.reload(); }}
            async function verifyAdmin() {{
                const pass = document.getElementById('admin-pass').value; const errorMsg = document.getElementById('admin-error-msg');
                if(pass === '{ADMIN_PASSWORD}') {{ errorMsg.style.display = 'none'; closeModal('admin-auth-modal'); openModal('admin-panel-modal'); document.getElementById('admin-pass').value = ''; try {{ const res = await fetch('/admin/stats'); const data = await res.json(); document.getElementById('stat-uptime').innerText = data.uptime; document.getElementById('stat-msgs').innerText = data.total_messages; updateSysBtn(data.active); }} catch(e) {{ alert('Error fetching stats'); }} }} else {{ errorMsg.style.display = 'block'; }}
            }}
            async function toggleSystem() {{ try {{ const res = await fetch('/admin/toggle_system', {{ method: 'POST' }}); const data = await res.json(); updateSysBtn(data.active); }} catch(e) {{ alert('Error toggling system'); }} }}
            function updateSysBtn(isActive) {{ const btn = document.getElementById('btn-toggle-sys'); if(isActive) {{ btn.innerText = "Turn System OFF"; btn.style.background = "var(--danger)"; }} else {{ btn.innerText = "Turn System ON"; btn.style.background = "var(--success)"; }} }}
            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
            renderHistory(); renderSuggestions();
        </script>
    </body>
    </html>
    """

# 🔥 NEW ROUTE: LOVE PAGE (Prank)
@app.route("/love/<name>")
def love_page(name):
    # This renders the viral proposal page with the provided name
    return render_template_string(PROPOSE_HTML, name=name)

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
    user_name = data.get("user_name", "User") # Get user name from frontend
    
    # 0. ❤️ LOVE LINK GENERATOR (Specific Trigger)
    last_msg = messages[-1]['content'] if messages else ""
    if "propose link" in last_msg.lower() or "love link" in last_msg.lower() or "create link" in last_msg.lower():
        match = re.search(r"for\s+(.*)", last_msg, re.IGNORECASE)
        target_name = match.group(1).strip() if match else "Someone"
        base_url = request.host_url.rstrip('/')
        link = f"{base_url}/love/{target_name.replace(' ', '%20')}"
        
        # Generator response
        return Response(f"💘 **Here is your magic link!**\n\nSend this to **{target_name}**:\n\n[Click here to open magic link 💘]({link})", mimetype="text/plain")

    # MATH ENGINE
    if messages and messages[-1]['role'] == 'user':
        math_result = solve_math_problem(last_msg)
        if math_result:
            system_note = {
                "role": "system",
                "content": f"⚡ MATH TOOL: The calculated answer is {math_result}. Give this answer directly."
            }
            messages.insert(-1, system_note)
            
    # SEARCH ENGINE
    search_keywords = ["current", "latest", "news", "weather", "today", "price", "who is", "what is", "prime minister", "president", "score"]
    search_context = ""
    if any(k in last_msg.lower() for k in search_keywords) or "?" in last_msg:
        web_result = search_web(last_msg)
        if web_result:
            search_context = f"\n\n[REAL-TIME WEB SEARCH RESULTS]:\n{web_result}\n(Use this info to answer)"

    ctx = get_current_context()
    
    # 🧠 BRAIN UPDATE: Enhanced Logic
    sys_prompt_content = f"""
    You are {APP_NAME}, a highly intelligent, creative, and concise AI assistant designed for students and professionals.
    
    IDENTITY & CONTEXT:
    - Creator: {OWNER_NAME} (Bangla: {OWNER_NAME_BN}). IMPORTANT: Only mention the creator if explicitly asked "Who created you?" or "Who is your owner?".
    - Current User Name: {user_name}. (Address the user by this name if you know it. If the user corrects their name, accept it immediately).
    - Current Time: {ctx['time_utc']} (UTC). Only provide Local Dhaka time ({ctx['time_local']}) if specifically asked for "Local time" or "Dhaka time". Do not mention time in every response.
    {search_context}
    
    BEHAVIOR RULES:
    1. **CONCISE & SMART**: Be direct. Avoid unnecessary chatter ("I hope you are doing well", etc.). Get straight to the answer.
    2. **STUDENT FRIENDLY**: Explain complex topics simply and creatively.
    3. **CODING**: If asked for code (HTML/CSS/JS/Python), ALWAYS provide the full code inside a markdown block (```language ... ```) so the Live Preview tool works.
    4. **NO SCRIPT FORMAT**: Do not use "Flux AI:" or "User:" prefixes.
    5. **IMAGE**: Output ONLY: ![Flux Image](https://image.pollinations.ai/prompt/{{english_prompt}})
    6. **LOVE LINK**: If user asks for a love link, do not generate it yourself. The system handles it. Just encourage them to ask "Create a propose link for [Name]".
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
        yield "⚠️ System Busy."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000)) # Default to 10000 for Render
    app.run(host="0.0.0.0", port=port, debug=True)
