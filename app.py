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
# 🔹 Flux AI (Ultimate Intelligence - Build 34.0.0) 🧠
# 🔥 FIXED: PRO UI/UX, ANIMATIONS & MOBILE RESPONSIVE PREVIEW 🔥
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "34.0.0"
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
    now_utc = datetime.now(pytz.utc)
    return {
        "time_utc": now_utc.strftime("%I:%M %p"),
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
    {"icon": "fas fa-image", "text": "Upload an image to analyze"},
    {"icon": "fas fa-gamepad", "text": "Make a responsive Snake Game"},
    {"icon": "fas fa-calculator", "text": "Create a Neon Calculator"},
    {"icon": "fas fa-paint-brush", "text": "Design an animated Login Page"}
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
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>

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
                --terminal-green: #0f0;
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
                --terminal-green: #00a000;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg-gradient); color: var(--text); font-family: 'Outfit', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }}
            
            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid var(--glass-border); transition: transform 0.4s; position: absolute; z-index: 200; left: 0; top: 0; background: var(--sidebar-bg); }}
            #sidebar.closed {{ transform: translateX(-105%); }}
            
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid var(--glass-border); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }}
            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }}
            .history-item {{ padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; font-weight: 500; }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); color: var(--text); }}

            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: transparent; backdrop-filter: blur(10px); border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100; }}
            
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; overflow-x: hidden; }}

            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 100px; padding-bottom: 60px; }}
            .icon-wrapper {{ width: 80px; height: 80px; border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 25px; animation: levitate 4s infinite; }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 30px; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; width: 100%; max-width: 750px; padding: 0 10px; }}
            .chip {{ padding: 14px 16px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 16px; cursor: pointer; color: var(--text-secondary); font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; transition: 0.3s; }}
            .chip:hover {{ border-color: var(--accent); color: var(--text); }}
            .chip i {{ color: var(--accent); }}

            .message-wrapper {{ display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1rem; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; flex: 1; min-width: 0; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; flex: none; max-width: 85%; }}
            
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; overflow-wrap: break-word; max-width: 100%; }}
            .bot .bubble {{ background: transparent; padding: 0; color: var(--text); overflow-x: auto; }}
            .user .bubble {{ background: var(--user-grad); border-radius: 20px 4px 20px 20px; color: white; }}
            .bubble img {{ max-width: 100%; border-radius: 16px; margin-top: 12px; border: 1px solid var(--glass-border); }}

            .brain-container {{ width: 100%; background: #000; border: 1px solid var(--glass-border); border-radius: 16px; padding: 20px; font-family: 'Fira Code', monospace; margin-bottom: 15px; box-shadow: inset 0 0 20px rgba(0,255,0,0.05); }}
            .brain-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 15px; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 10px; }}
            .brain-title {{ color: var(--terminal-green); font-size: 0.85rem; font-weight: 600; letter-spacing: 2px; }}
            .brain-logs {{ font-size: 0.8rem; color: #a3a3a3; line-height: 1.8; min-height: 60px; }}
            .log-line {{ animation: typeText 0.1s linear forwards; opacity: 0; }}
            .log-line::before {{ content: "> "; color: var(--terminal-green); }}

            /* 🔥 IMPROVED ARTIFACT CONTAINER FOR MOBILE 🔥 */
            .artifact-container {{ width: 100%; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 16px; overflow: hidden; margin-top: 15px; display: flex; flex-direction: column; }}
            .artifact-header {{ background: rgba(125,125,125,0.1); padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--glass-border); }}
            .artifact-title {{ display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; color: var(--text); }}
            .artifact-title i {{ color: #facc15; }}
            .artifact-actions button {{ background: var(--accent); border: none; color: black; font-weight: 600; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px; }}
            .artifact-content {{ width: 100%; height: 400px; position: relative; background: #fff; overflow: hidden; }}
            .artifact-content iframe {{ width: 100%; height: 100%; border: none; background: #fff; display: block; }}

            /* 🔥 FIXED MOBILE PREVIEW MODAL 🔥 */
            #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; backdrop-filter: blur(8px); padding: 10px; box-sizing: border-box; }}
            .preview-box {{ width: 100%; max-width: 500px; height: 100%; max-height: 90vh; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; animation: popIn 0.3s; }}
            .preview-header {{ padding: 12px 20px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
            iframe.fullscreen-iframe {{ flex: 1; border: none; width: 100%; height: 100%; display: block; }}

            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; margin-top: 15px; box-sizing: border-box; max-width: 100%; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            .copy-btn {{ position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.15); color: white; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; }}

            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; flex-direction: column; align-items: center; }}
            #attachment-preview {{ display: none; width: 100%; max-width: 850px; margin-bottom: 10px; padding: 10px 15px; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--accent); border-radius: 16px; font-size: 0.9rem; align-items: center; justify-content: space-between; }}
            .preview-close {{ cursor: pointer; color: #ff0f7b; font-size: 1.2rem; }}
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 28px; padding: 10px 10px 10px 15px; border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); }}
            .attach-btn {{ background: transparent; border: none; color: var(--text-secondary); font-size: 1.3rem; padding: 10px; cursor: pointer; }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1.05rem; max-height: 150px; resize: none; padding: 10px 10px; line-height: 1.4; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.9); }} to {{ opacity: 1; transform: scale(1); }} }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700; color:#111;">Live App Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-weight:600;">Close</button>
                </div>
                <iframe id="fullscreen-frame" class="fullscreen-iframe"></iframe>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()"><i class="fas fa-plus"></i> New Chat</button>
            <div style="font-size:0.75rem; font-weight: 700; color:var(--text-secondary); margin-bottom:12px; letter-spacing: 1px;">RECENT</div>
            <div class="history-list" id="history-list"></div>
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
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div id="attachment-preview">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <i id="attach-icon" class="fas fa-file"></i>
                        <span id="attach-name" style="font-weight:600;">file.pdf</span>
                    </div>
                    <i class="fas fa-times-circle preview-close" onclick="clearAttachment()"></i>
                </div>

                <div class="input-box">
                    <input type="file" id="file-upload" accept="image/*, application/pdf" style="display: none;">
                    <label for="file-upload" class="attach-btn"><i class="fas fa-paperclip"></i></label>
                    <textarea id="msg" placeholder="Ask Flux or upload a file..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v34_history')) || [];
            let userName = localStorage.getItem('flux_user_name_fixed'); 
            let awaitingName = false; 

            let attachedImageBase64 = null;
            let attachedPdfText = null;
            let currentChatId = null;

            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            renderHistory(); renderSuggestions(); 

            // Dynamic Background
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas); resizeCanvas();

            class Particle {{
                constructor() {{ this.x = Math.random() * canvas.width; this.y = Math.random() * canvas.height; this.vx = (Math.random() - 0.5) * 0.5; this.vy = (Math.random() - 0.5) * 0.5; this.size = Math.random() * 2; }}
                update() {{ this.x += this.vx; this.y += this.vy; if(this.x < 0 || this.x > canvas.width) this.vx *= -1; if(this.y < 0 || this.y > canvas.height) this.vy *= -1; }}
                draw() {{ ctx.fillStyle = '#00f3ff'; ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }}
            }}
            for(let i=0; i<60; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach((p, index) => {{ p.update(); p.draw(); }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                document.getElementById('suggestion-box').innerHTML = shuffled.map(s => `<div class="chip" onclick="sendSuggestion('${{s.text}}')"><i class="${{s.icon}}"></i> ${{s.text}}</div>`).join('');
            }}

            function startNewChat() {{
                currentChatId = Date.now(); chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData(); renderHistory(); renderSuggestions(); clearAttachment();
                chatBox.innerHTML = ''; chatBox.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed'); overlay.style.display = 'none'; msgInput.value = ''; resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v34_history', JSON.stringify(chats)); }}
            function renderHistory() {{
                document.getElementById('history-list').innerHTML = chats.map(chat => `<div class="history-item" onclick="loadChat(${{chat.id}})"><i class="far fa-comment-alt"></i> <span>${{(chat.title || 'New Conversation').substring(0, 22)}}</span></div>`).join('');
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none'; clearAttachment();
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

            // 🔥 FIX: FORCE INJECT VIEWPORT META TAG FOR MOBILE RESPONSIVENESS 🔥
            function checkForArtifacts(text, bubble) {{
                const codeMatch = text.match(/```html([\\s\\S]*?)```/);
                if(codeMatch) {{
                    let code = codeMatch[1];
                    // If AI forgot the viewport tag, we force it!
                    if (!code.includes('viewport')) {{
                        code = code.replace('<head>', '<head>\\n<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">\\n');
                    }}
                    
                    if (!bubble.querySelector('.artifact-container')) {{
                        const artifactDiv = document.createElement('div'); artifactDiv.className = 'artifact-container';
                        artifactDiv.innerHTML = `<div class="artifact-header"><div class="artifact-title"><i class="fas fa-layer-group"></i> Live App Preview</div><div class="artifact-actions"><button onclick="openFullscreenPreview(this)" data-code="${{encodeURIComponent(code)}}"><i class="fas fa-play"></i> Fullscreen</button></div></div><div class="artifact-content"><iframe srcdoc="${{code.replace(/"/g, '&quot;')}}"></iframe></div>`;
                        bubble.appendChild(artifactDiv);
                    }}
                }}
            }}

            window.openFullscreenPreview = function(btn) {{
                document.getElementById('preview-modal').style.display = 'flex';
                document.getElementById('fullscreen-frame').srcdoc = decodeURIComponent(btn.getAttribute('data-code'));
            }};
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            document.getElementById('file-upload').addEventListener('change', async function(e) {{
                const file = e.target.files[0]; if(!file) return;
                const preview = document.getElementById('attachment-preview'); const nameSpan = document.getElementById('attach-name'); const icon = document.getElementById('attach-icon');
                
                nameSpan.innerText = "Processing " + file.name + "..."; preview.style.display = 'flex';
                attachedImageBase64 = null; attachedPdfText = null;

                if(file.type.startsWith('image/')) {{
                    icon.className = 'fas fa-image'; const reader = new FileReader();
                    reader.onload = function(event) {{ attachedImageBase64 = event.target.result.split(',')[1]; nameSpan.innerText = file.name; }};
                    reader.readAsDataURL(file);
                }} 
                else if(file.type === 'application/pdf') {{
                    icon.className = 'fas fa-file-pdf';
                    try {{
                        const arrayBuffer = await file.arrayBuffer(); const pdf = await pdfjsLib.getDocument({{data: arrayBuffer}}).promise; let fullText = '';
                        for (let i = 1; i <= pdf.numPages; i++) {{ const page = await pdf.getPage(i); const textContent = await page.getTextContent(); fullText += textContent.items.map(item => item.str).join(' ') + '\\n'; }}
                        attachedPdfText = fullText; nameSpan.innerText = file.name + " (Ready)";
                    }} catch (err) {{ nameSpan.innerText = "Error reading PDF"; }}
                }} else {{ nameSpan.innerText = "Unsupported Format"; }}
                e.target.value = '';
            }});

            function clearAttachment() {{ attachedImageBase64 = null; attachedPdfText = null; document.getElementById('attachment-preview').style.display = 'none'; }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                wrapper.innerHTML = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div><div class="bubble-container"><div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div><div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                const bubble = wrapper.querySelector('.bubble'); bubble.innerHTML = marked.parse(text);
                if(!isUser) {{ hljs.highlightAll(); addCopyButtons(); checkForArtifacts(text, bubble); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showDeepBrainThinking(isVision=false) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.id = 'typing-indicator'; wrapper.className = 'message-wrapper bot';
                let title = isVision ? "Vision Core Active (Analyzing Image)" : "Deep-Brain Processor Active";
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble" style="background:transparent; padding:0; width:100%;"><div class="brain-container"><div class="brain-header"><i class="fas fa-microchip brain-icon" style="color:#0f0;"></i><span class="brain-title">${{title}}</span></div><div class="brain-logs" id="brain-logs"></div></div></div></div>`;
                chatBox.appendChild(wrapper); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});

                const logs = isVision ? ["Scanning pixels...", "Extracting text...", "Processing visual data..."] : ["Analyzing query context...", "Injecting UI/UX elements...", "Compiling logic matrix..."];
                const logContainer = document.getElementById('brain-logs'); let i = 0;
                window.brainInterval = setInterval(() => {{ if(i < logs.length) {{ const line = document.createElement('div'); line.className = 'log-line'; line.innerText = logs[i]; logContainer.appendChild(line); i++; }} else {{ clearInterval(window.brainInterval); }} }}, 800);
            }}

            function removeTyping() {{ if(window.brainInterval) clearInterval(window.brainInterval); document.getElementById('typing-indicator')?.remove(); }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text && !attachedImageBase64 && !attachedPdfText) return;

                let uiMessage = text;
                if(!text && attachedImageBase64) uiMessage = "📸 *Uploaded an image*";
                if(!text && attachedPdfText) uiMessage = "📄 *Uploaded a PDF document*";

                let apiMessage = text;
                if(!text && attachedImageBase64) apiMessage = "Describe this image in detail.";
                if(!text && attachedPdfText) apiMessage = "Summarize this document.";

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: uiMessage }});
                if(chat.messages.length === 1) {{ chat.title = (text || "File Upload").substring(0, 20); renderHistory(); }}
                saveData(); msgInput.value = ''; appendBubble(uiMessage, true);

                if(!userName && !awaitingName) {{ awaitingName = true; setTimeout(() => {{ appendBubble("Hello! I am Flux AI. What should I call you?", false); }}, 600); return; }}
                if(awaitingName) {{ userName = text; localStorage.setItem('flux_user_name_fixed', userName); awaitingName = false; setTimeout(() => {{ appendBubble(`Nice to meet you, ${{userName}}! How can I help you today?`, false); }}, 600); return; }}

                showDeepBrainThinking(!!attachedImageBase64); 
                
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                context[context.length - 1].content = apiMessage;

                const payload = {{ messages: context, user_name: userName, image_base64: attachedImageBase64, pdf_text: attachedPdfText }};
                clearAttachment();

                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(payload) }});
                    removeTyping();
                    if(!res.ok) throw new Error("System Offline");
                    
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp = '';
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper); const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read(); if(done) break;
                        botResp += decoder.decode(value); bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData(); hljs.highlightAll(); addCopyButtons(); checkForArtifacts(botResp, bubbleDiv);

                }} catch(e) {{ removeTyping(); appendBubble("⚠️ System connection error. Please try again.", false); }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES
    if not SYSTEM_ACTIVE: return Response("System is currently under maintenance.", status=503)

    TOTAL_MESSAGES += 1
    data = request.json
    messages = data.get("messages", [])
    user_name = data.get("user_name", "User")
    
    image_base64 = data.get("image_base64")
    pdf_text = data.get("pdf_text")

    ctx = get_current_context()
    
    if image_base64:
        # VISION MODE
        target_model = "llama-3.2-90b-vision-preview"
        sys_prompt_content = f"""
        You are {APP_NAME}, a Visual Expert AI created by {OWNER_NAME}.
        RULES: Analyze the image accurately. DO NOT WRITE CODE unless specifically asked to build an app from the image.
        """
        user_text = messages[-1]['content']
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }]
    else:
        # 🧠 THE MASTER FIX FOR ELITE CODING AND RESPONSIVENESS 🧠
        target_model = "llama-3.3-70b-versatile"
        sys_prompt_content = f"""
        You are {APP_NAME}, an Elite AI Developer and Creative Assistant created by {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
        Current User Name: {user_name}.
        
        CRITICAL RULES FOR CODING & APP CREATION:
        1. SINGLE FILE: Write ENTIRE HTML, CSS, and JS inside a SINGLE ```html block. Do not split them.
        2. NEXT-LEVEL DESIGN (UI/UX): Always include stunning CSS animations, modern UI (Glassmorphism, Neon, Gradients), hover effects, and polished styling. NEVER provide boring/plain designs.
        3. 100% MOBILE RESPONSIVE (CRITICAL): 
           - The app will run inside a mobile iframe. 
           - NEVER use fixed sizes like `width: 800px;` or `<canvas width="800">`. 
           - Use percentages (`100%`), `vw`, `vh`, and flexbox/grid. 
           - For Canvas games (like Snake), write JS to dynamically resize the canvas to fit the screen (`window.innerWidth`, `window.innerHeight`).
           - Always add `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">` to the `<head>`.
        4. BE SMART: Do not write explanations if you provide an app, let the app speak for itself.
        """
        
        if pdf_text and messages:
            messages[-1]['content'] = f"Here is the content of an uploaded PDF document:\n\n---\n{pdf_text[:15000]}\n---\n\nUser Command: {messages[-1]['content']}"

        if messages and isinstance(messages[-1]['content'], str):
            math_result = solve_math_problem(messages[-1]['content'])
            if math_result:
                messages.insert(-1, {"role": "system", "content": f"⚡ MATH TOOL: The calculated answer is {math_result}."})

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
                    model=target_model,
                    messages=[sys_message] + messages,
                    stream=True,
                    temperature=0.7, 
                    max_tokens=3000
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ API Rate Limit or Server Error. Try again in a few seconds."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
