from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import re      # ➕ Math: Regex এর জন্য
import math    # ➕ Math: অংকের লাইব্রেরি

# ==========================================
# 🔹 Flux AI (Sci-Fi Ultimate - Build 24.0.0) 🌌
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "24.0.0"
ADMIN_PASSWORD = "7rx9x2c0" 

# ⚠️ Links Restored
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
    except:
        return None

SUGGESTION_POOL = [
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"},
    {"icon": "fas fa-plane", "text": "Plan a trip to Cox's Bazar"},
    {"icon": "fas fa-laptop-code", "text": "Write a Python calculator"},
    {"icon": "fas fa-paint-brush", "text": "Generate a cyberpunk city image"},
    {"icon": "fas fa-calculator", "text": "Solve: 50 * 3 + 20"}
]

@app.route("/")
def home():
    suggestions_json = json.dumps(SUGGESTION_POOL)
    
    # ⚠️ CRITICAL: CSS/JS braces are double {{ }} to avoid Python errors
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME}</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;500;700&family=Noto+Sans+Bengali:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --hue: 210; /* Default Blue */
                --bg: #050a14;
                --sidebar: rgba(10, 20, 30, 0.85);
                --text: #e0f2ff;
                --text-secondary: #8ba2b5;
                --accent: hsl(var(--hue), 100%, 50%);
                --glow: 0 0 15px hsl(var(--hue), 100%, 50%, 0.6);
                --input-bg: rgba(20, 30, 50, 0.6);
                --border: rgba(100, 200, 255, 0.1);
                --font-main: 'Rajdhani', sans-serif;
                --font-header: 'Orbitron', sans-serif;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: var(--font-main); height: 100vh; display: flex; overflow: hidden; 
            }}

            /* 🌌 1. NEURAL BACKGROUND */
            #neuro-bg {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                z-index: -1; pointer-events: none;
            }}

            /* SIDEBAR (Glassmorphism) */
            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); 
                position: absolute; z-index: 200; left: 0; top: 0; 
                background: var(--sidebar); backdrop-filter: blur(15px);
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 10px 0 30px rgba(0,0,0,0.5);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ 
                font-family: var(--font-header); font-size: 1.8rem; font-weight: 900; 
                margin-bottom: 25px; display: flex; align-items: center; gap: 10px; 
                color: var(--text); letter-spacing: 2px; text-transform: uppercase;
                text-shadow: var(--glow);
            }}
            
            .new-chat-btn {{
                width: 100%; padding: 14px; background: rgba(255,255,255,0.05); 
                color: var(--accent); border: 1px solid var(--accent);
                border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 10px;
                margin-bottom: 20px; transition: 0.3s; font-family: var(--font-header);
                box-shadow: var(--glow);
            }}
            .new-chat-btn:active {{ transform: scale(0.95); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }}
            .history-item {{
                padding: 12px; border-radius: 6px; cursor: pointer; color: var(--text-secondary); 
                font-size: 1rem; transition: 0.3s; display: flex; align-items: center; gap: 10px;
                border-left: 2px solid transparent;
            }}
            .history-item:hover {{ background: rgba(255,255,255,0.05); border-left-color: var(--accent); color: var(--text); }}

            /* 🎨 2. THEME PICKER */
            .theme-section {{ margin-top: auto; padding-top: 15px; border-top: 1px solid var(--border); }}
            .theme-title {{ font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }}
            .theme-colors {{ display: flex; gap: 10px; justify-content: center; }}
            .color-dot {{ width: 25px; height: 25px; border-radius: 50%; cursor: pointer; transition: 0.3s; border: 2px solid transparent; }}
            .color-dot:hover, .color-dot.active {{ transform: scale(1.2); border-color: white; box-shadow: 0 0 10px currentColor; }}

            /* MAIN CHAT AREA */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(5, 10, 20, 0.8); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}

            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 20px 140px 20px; display: flex; flex-direction: column; gap: 25px; }}

            /* 🧠 5. JARVIS ORB */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding-top: 60px;
            }}
            .orb-container {{
                width: 120px; height: 120px; position: relative; margin-bottom: 30px;
                display: flex; justify-content: center; align-items: center;
            }}
            .orb {{
                position: absolute; width: 100%; height: 100%; border-radius: 50%;
                border: 2px solid var(--accent); border-top-color: transparent; border-bottom-color: transparent;
                animation: spin 3s linear infinite; box-shadow: var(--glow);
            }}
            .orb::before {{
                content: ''; position: absolute; inset: 10px; border-radius: 50%;
                border: 2px solid #fff; border-left-color: transparent; border-right-color: transparent;
                animation: spin-rev 5s linear infinite;
            }}
            .orb-core {{
                width: 40px; height: 40px; background: var(--accent); border-radius: 50%;
                box-shadow: 0 0 30px var(--accent), 0 0 60px var(--accent);
                animation: pulse 2s ease-in-out infinite;
            }}
            
            .welcome-title {{ font-family: var(--font-header); font-size: 2.2rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 30px; font-size: 1.1rem; max-width: 90%; }}

            /* MESSAGES & MATRIX EFFECT */
            .message-wrapper {{ display: flex; gap: 15px; width: 100%; max-width: 850px; margin: 0 auto; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ 
                width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                background: rgba(255,255,255,0.05); border: 1px solid var(--border); font-size: 1.2rem;
                box-shadow: var(--glow);
            }}
            .bot-avatar {{ color: var(--accent); }}
            
            .bubble {{ 
                padding: 15px 20px; border-radius: 12px; font-size: 1.05rem; line-height: 1.6; position: relative;
                background: rgba(10, 20, 35, 0.7); border: 1px solid var(--border);
                backdrop-filter: blur(5px); max-width: 90%;
            }}
            .user .bubble {{ border-color: var(--accent); background: rgba(0, 200, 255, 0.1); }}
            .bot .bubble {{ border-left: 3px solid var(--accent); }}

            /* 6. LIVE PREVIEW BUTTON */
            .run-code-btn {{
                display: inline-flex; align-items: center; gap: 8px; margin-top: 10px;
                padding: 8px 16px; background: var(--accent); color: #000;
                border: none; border-radius: 4px; font-weight: 700; cursor: pointer;
                font-family: var(--font-header); transition: 0.3s;
            }}
            .run-code-btn:hover {{ box-shadow: 0 0 20px var(--accent); transform: translateY(-2px); }}

            /* INPUT HUD */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 90%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border: 1px solid var(--border);
                border-radius: 12px; padding: 10px 10px 10px 20px; backdrop-filter: blur(10px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.3); transition: 0.3s; position: relative; overflow: hidden;
            }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: var(--glow); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1.1rem; max-height: 150px; resize: none; padding: 12px 0; font-family: inherit;
            }}
            
            .send-btn {{
                background: var(--accent); color: #000; border: none; width: 45px; height: 45px;
                border-radius: 8px; cursor: pointer; margin-left: 10px;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s;
            }}
            .send-btn:hover {{ box-shadow: 0 0 15px var(--accent); }}

            /* 1. ENERGY TRAIL ANIMATION */
            .energy-ball {{
                position: fixed; width: 20px; height: 20px; background: var(--accent);
                border-radius: 50%; pointer-events: none; z-index: 9999;
                box-shadow: 0 0 20px var(--accent), 0 0 40px #fff;
                animation: shootUp 0.6s ease-in-out forwards;
            }}

            /* PREVIEW MODAL */
            #preview-modal {{
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.9); z-index: 300; justify-content: center; align-items: center;
                backdrop-filter: blur(10px);
            }}
            .preview-box {{
                width: 95%; height: 90%; background: #fff; border-radius: 10px; overflow: hidden;
                display: flex; flex-direction: column; border: 2px solid var(--accent);
            }}
            .preview-header {{
                padding: 10px; background: #222; color: #fff; display: flex; justify-content: space-between; align-items: center;
            }}
            iframe {{ flex: 1; border: none; width: 100%; height: 100%; }}

            /* ANIMATIONS */
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            @keyframes spin-rev {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
            @keyframes pulse {{ 0%, 100% {{ transform: scale(1); opacity: 1; }} 50% {{ transform: scale(0.8); opacity: 0.7; }} }}
            @keyframes shootUp {{ 
                0% {{ bottom: 80px; left: 50%; transform: scale(1); opacity: 1; }} 
                100% {{ bottom: 60%; left: 50%; transform: scale(0.2); opacity: 0; }} 
            }}
            
            /* Admin & Delete Modal (Glassy) */
            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; }}
            .modal-box {{ background: rgba(15, 25, 40, 0.95); border: 1px solid var(--accent); padding: 30px; border-radius: 16px; width: 90%; max-width: 350px; text-align: center; box-shadow: var(--glow); }}
            
            pre {{ background: #0b121b !important; padding: 15px; border-radius: 8px; border: 1px solid var(--border); overflow-x: auto; }}
        </style>
    </head>
    <body>
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span>🔴 Live Preview</span>
                    <button onclick="closePreview()" style="background:red; color:white; border:none; padding:5px 10px; cursor:pointer;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>

        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--text)">Delete History?</h3>
                <div style="display:flex; gap:10px; margin-top:20px;">
                    <button onclick="closeModal('delete-modal')" style="flex:1; padding:10px; background:rgba(255,255,255,0.1); border:1px solid var(--border); color:white; border-radius:5px;">Cancel</button>
                    <button onclick="confirmDelete()" style="flex:1; padding:10px; background:var(--danger); border:none; color:white; border-radius:5px;">Delete</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="color:var(--accent)">Admin Access</h3>
                <input type="password" id="admin-pass" style="width:100%; padding:10px; margin:15px 0; background:rgba(0,0,0,0.3); border:1px solid var(--accent); color:white; text-align:center;" placeholder="Enter Code">
                <button onclick="verifyAdmin()" style="width:100%; padding:10px; background:var(--accent); border:none; font-weight:bold;">LOGIN</button>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> NEW CHAT
            </button>
            
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-title">System Color</div>
                <div class="theme-colors">
                    <div class="color-dot" style="background: #00f3ff;" onclick="setTheme(190)"></div> <div class="color-dot" style="background: #a200ff;" onclick="setTheme(270)"></div> <div class="color-dot" style="background: #00ff88;" onclick="setTheme(150)"></div> <div class="color-dot" style="background: #ff0055;" onclick="setTheme(340)"></div> </div>
                
                <div class="history-item" style="margin-top:15px;" onclick="openDeleteModal('delete-modal')"><i class="fas fa-trash"></i> Clear Memory</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:white; font-size:1.4rem; cursor:pointer;"><i class="fas fa-bars"></i></button>
                <span style="font-family:var(--font-header); font-weight:700; letter-spacing:1px;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem; cursor:pointer;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="orb-container">
                        <div class="orb"></div>
                        <div class="orb-core"></div>
                    </div>
                    <div class="welcome-title">SYSTEM ONLINE</div>
                    <div class="welcome-subtitle">Awaiting your command, User.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Enter command..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-location-arrow"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v24_history')) || [];
            let currentChatId = null;
            let currentHue = localStorage.getItem('flux_hue') || 190;
            
            // Apply Saved Theme
            document.documentElement.style.setProperty('--hue', currentHue);

            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');

            // 1. NEURAL BACKGROUND JS
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();

            class Particle {{
                constructor() {{
                    this.x = Math.random() * canvas.width;
                    this.y = Math.random() * canvas.height;
                    this.vx = (Math.random() - 0.5) * 0.5;
                    this.vy = (Math.random() - 0.5) * 0.5;
                    this.size = Math.random() * 2;
                }}
                update() {{
                    this.x += this.vx; this.y += this.vy;
                    if(this.x < 0 || this.x > canvas.width) this.vx *= -1;
                    if(this.y < 0 || this.y > canvas.height) this.vy *= -1;
                }}
                draw() {{
                    ctx.fillStyle = `hsl(${{currentHue}}, 100%, 70%)`;
                    ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
                }}
            }}

            for(let i=0; i<60; i++) particles.push(new Particle());

            function animateBg() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach((p, index) => {{
                    p.update(); p.draw();
                    for(let j=index; j<particles.length; j++) {{
                        const dx = p.x - particles[j].x;
                        const dy = p.y - particles[j].y;
                        const dist = Math.sqrt(dx*dx + dy*dy);
                        if(dist < 100) {{
                            ctx.strokeStyle = `hsla(${{currentHue}}, 100%, 70%, ${{1 - dist/100}})`;
                            ctx.lineWidth = 0.5;
                            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(particles[j].x, particles[j].y); ctx.stroke();
                        }}
                    }}
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            // 2. THEME SETTER
            function setTheme(hue) {{
                currentHue = hue;
                localStorage.setItem('flux_hue', hue);
                document.documentElement.style.setProperty('--hue', hue);
            }}

            // 3. MATRIX / TYPEWRITER EFFECT
            function typeText(element, text) {{
                let index = 0;
                element.innerHTML = '';
                const interval = setInterval(() => {{
                    element.innerHTML += text.charAt(index);
                    index++;
                    chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    if(index >= text.length) clearInterval(interval);
                }}, 5); // Fast typing
            }}

            // 4. ENERGY TRAIL
            function playSentAnimation() {{
                const ball = document.createElement('div');
                ball.className = 'energy-ball';
                document.body.appendChild(ball);
                setTimeout(() => ball.remove(), 600);
            }}

            // 5. LIVE PREVIEW LOGIC
            function checkForCode(text, bubble) {{
                if(text.includes('```html')) {{
                    const btn = document.createElement('button');
                    btn.className = 'run-code-btn';
                    btn.innerHTML = '<i class="fas fa-play"></i> Run Code';
                    btn.onclick = () => {{
                        const code = text.match(/```html([\s\S]*?)```/)[1];
                        openPreview(code);
                    }};
                    bubble.appendChild(btn);
                }}
            }}

            function openPreview(code) {{
                document.getElementById('preview-modal').style.display = 'flex';
                const frame = document.getElementById('code-frame');
                frame.srcdoc = code;
            }}
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            // INIT LOGIC
            renderHistory();
            renderSuggestions();

            function toggleSidebar() {{ sidebar.classList.toggle('closed'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            function openDeleteModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v24_history'); location.reload(); }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{
                    html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>';
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Mission", messages: [] }});
                saveData();
                renderHistory();
                renderSuggestions();
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed');
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-dots"></i> <span>' + (chat.title || 'New Mission').substring(0, 20) + '</span>';
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function saveData() {{ localStorage.setItem('flux_v24_history', JSON.stringify(chats)); }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;
                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false)); // false = no typing effect for history
                sidebar.classList.add('closed');
            }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="sender-name">${{isUser ? 'YOU' : '{APP_NAME}'}}</div><div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                const bubble = wrapper.querySelector('.bubble');
                
                if(isUser || !animate) {{
                    bubble.innerHTML = marked.parse(text);
                    checkForCode(text, bubble);
                }} else {{
                    // Matrix Typing Effect for Bot
                    let html = marked.parse(text);
                    bubble.innerHTML = html; // Direct render for stability, glitch effect is CSS
                    checkForCode(text, bubble);
                }}
                
                hljs.highlightAll();
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(text === '!admin') {{
                    msgInput.value = '';
                    document.getElementById('admin-auth-modal').style.display = 'flex';
                    return;
                }}

                playSentAnimation(); // 🚀 Energy Trail

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 18); renderHistory(); }}
                saveData();
                msgInput.value = '';
                appendBubble(text, true);

                // Loading Indicator
                const loadingWrapper = document.createElement('div');
                loadingWrapper.id = 'loading';
                loadingWrapper.className = 'message-wrapper bot';
                loadingWrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble" style="background:transparent; color:var(--accent);">Encrypting response...</div>`;
                chatBox.appendChild(loadingWrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight }});

                const context = chat.messages.slice(-6).map(m => ({{ role: m.role, content: m.text }}));

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    document.getElementById('loading').remove();
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    // Create Bot Bubble
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper);
                    const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        const chunk = decoder.decode(value);
                        botResp += chunk;
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    checkForCode(botResp, bubbleDiv);
                    hljs.highlightAll();

                }} catch(e) {{
                    document.getElementById('loading').remove();
                    appendBubble("⚠️ Connection Lost. Check Neural Link.", false);
                }}
            }}

            async function verifyAdmin() {{
                const pass = document.getElementById('admin-pass').value;
                if(pass === '{ADMIN_PASSWORD}') {{
                    document.getElementById('admin-auth-modal').style.display = 'none';
                    document.getElementById('admin-panel-modal').style.display = 'flex';
                    const res = await fetch('/admin/stats');
                    const data = await res.json();
                    document.getElementById('stat-msgs').innerText = data.total_messages;
                    document.getElementById('stat-uptime').innerText = data.uptime;
                }} else {{
                    document.getElementById('admin-error-msg').style.display = 'block';
                }}
            }}

            async function toggleSystem() {{
                const res = await fetch('/admin/toggle_system', {{ method: 'POST' }});
                const data = await res.json();
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
    
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a highly intelligent AI assistant from the future (Year 2026).
        
        IDENTITY:
        - Created by: {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
        - Tone: Smart, Professional, Futuristic but friendly.
        
        CONTEXT:
        - Time: {ctx['time_local']} (Dhaka)
        
        RULES:
        1. **NO SCRIPT FORMAT**: Never use "Flux AI:" or "User:" prefixes. Just reply directly.
        2. **CODING**: If asked for code, provide it in a code block. If asked for HTML, provide a complete HTML snippet so the user can preview it.
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
