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
# 🔹 Flux AI (Ultimate Intelligence - Build 29.2.1) 🧠
# 🔥 FIXED: MOBILE PREVIEW, AUTO-ANIMATION, RESPONSIVE UI 🔥
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "29.2.1"
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
    {"icon": "fas fa-gamepad", "text": "Make a Tic-Tac-Toe game"},
    {"icon": "fas fa-calculator", "text": "Create a Neon Calculator"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"},
    {"icon": "fas fa-utensils", "text": "Healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Trip plan for Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Business ideas for students"},
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
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
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
            body {{ 
                margin: 0; background: var(--bg-gradient); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.4s ease;
            }}

            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }}
            .glass {{ background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); }}

            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid var(--glass-border); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.4s ease; position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 10px 0 30px rgba(0,0,0,0.3); background: var(--sidebar-bg); }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid var(--glass-border); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{ padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; gap: 10px; font-weight: 500; }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; transition: all 0.4s ease; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 8px; transition: all 0.3s ease; }}
            .theme-btn.active {{ background: rgba(125,125,125,0.2); color: var(--text); }}

            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: rgba(15, 15, 30, 0.0); backdrop-filter: blur(10px); border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100; }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; overflow-x: hidden; }}

            /* WELCOME SCREEN */
            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }}
            .icon-wrapper {{ width: 80px; height: 80px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 25px; animation: levitate 4s ease-in-out infinite; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 30px; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; width: 100%; max-width: 750px; }}
            .chip {{ padding: 14px 16px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 16px; cursor: pointer; color: var(--text-secondary); transition: 0.4s; display: flex; align-items: center; gap: 14px; font-size: 0.9rem; }}

            /* MESSAGE BUBBLES */
            .message-wrapper {{ display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: fadeIn 0.4s ease; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; flex: 1; min-width: 0; }}
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; }}
            .user .bubble {{ background: var(--user-grad); color: white; border-radius: 20px 4px 20px 20px; width: fit-content; align-self: flex-end; }}

            /* 🔥 FIXED: MOBILE-FRIENDLY ARTIFACTS 🔥 */
            .artifact-container {{ 
                width: 100%; 
                background: var(--glass-bg); 
                border: 1px solid var(--glass-border); 
                border-radius: 16px; 
                overflow: hidden; 
                margin-top: 15px; 
                box-sizing: border-box; /* Crucial for mobile */
            }}
            .artifact-header {{ background: rgba(125,125,125,0.1); padding: 12px; display: flex; justify-content: space-between; align-items: center; }}
            .artifact-content {{ 
                width: 100%; 
                height: 350px; 
                background: #fff; 
                position: relative;
                overflow: hidden;
            }}
            .artifact-content iframe {{ 
                width: 100%; 
                height: 100%; 
                border: none; 
                display: block;
            }}

            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; margin-top: 15px; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; }}

            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 10%, transparent); display: flex; justify-content: center; z-index: 50; }}
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 28px; padding: 10px; border: 1px solid var(--glass-border); }}
            textarea {{ flex: 1; background: transparent; border: none; color: var(--text); font-size: 1.05rem; max-height: 150px; resize: none; padding: 10px; font-family: inherit; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            /* PREVIEW MODAL */
            #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; }}
            .preview-box {{ width: 95%; height: 90%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; }}
            .preview-header {{ padding: 12px; background: #f3f4f6; display: flex; justify-content: space-between; }}
            
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700; color:#111;">Live App Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:6px 14px; border-radius:6px; cursor:pointer;">Close</button>
                </div>
                <iframe id="fullscreen-frame" style="flex:1; border:none;"></iframe>
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
                <div class="history-item" onclick="location.reload()" style="color:#ff0f7b;"><i class="fas fa-trash-alt"></i> Clear All</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.3rem;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Flux AI Elite</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask Flux Anything..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            let chats = JSON.parse(localStorage.getItem('flux_v29_history')) || [];
            let currentChatId = null;
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');

            function setTheme(mode) {{ document.body.className = mode; }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 150) + 'px'; }}
            function toggleSidebar() {{ document.getElementById('sidebar').classList.toggle('closed'); document.querySelector('.overlay').style.display = document.getElementById('sidebar').classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const selected = {suggestions_json}.slice(0, 4);
                let html = '';
                selected.forEach(s => {{ html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>'; }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}
            renderSuggestions();

            function appendBubble(text, isUser) {{
                document.getElementById('welcome').style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                wrapper.innerHTML = `
                    <div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">
                        <i class="fas ${{isUser ? 'fa-user' : 'fa-bolt'}}"></i>
                    </div>
                    <div class="bubble-container">
                        <div class="bubble">${{marked.parse(text)}}</div>
                    </div>`;
                chatBox.appendChild(wrapper);
                
                if(!isUser) {{
                    hljs.highlightAll();
                    checkForArtifacts(text, wrapper.querySelector('.bubble'));
                }}
                chatBox.scrollTop = chatBox.scrollHeight;
            }}

            function checkForArtifacts(text, bubble) {{
                const codeMatch = text.match(/```html([\\s\\S]*?)```/);
                if(codeMatch) {{
                    const code = codeMatch[1];
                    const artifactDiv = document.createElement('div');
                    artifactDiv.className = 'artifact-container';
                    artifactDiv.innerHTML = `
                        <div class="artifact-header">
                            <span style="font-size:0.8rem; font-weight:600;"><i class="fas fa-code"></i> Live Preview</span>
                            <button onclick="openFullscreenPreview(this)" data-code="${{encodeURIComponent(code)}}" style="background:var(--accent); border:none; padding:4px 10px; border-radius:4px; font-size:0.7rem; cursor:pointer;">Fullscreen</button>
                        </div>
                        <div class="artifact-content">
                            <iframe srcdoc="${{code.replace(/"/g, '&quot;')}}"></iframe>
                        </div>`;
                    bubble.appendChild(artifactDiv);
                }}
            }}

            window.openFullscreenPreview = function(btn) {{
                const code = decodeURIComponent(btn.getAttribute('data-code'));
                document.getElementById('preview-modal').style.display = 'flex';
                document.getElementById('fullscreen-frame').srcdoc = code;
            }};
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;
                msgInput.value = '';
                appendBubble(text, true);

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: [{{role:'user', content:text}}], user_name: 'User' }})
                    }});
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = '<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="bubble"></div></div>';
                    chatBox.appendChild(wrapper);
                    const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }}
                    hljs.highlightAll();
                    checkForArtifacts(botResp, bubbleDiv);
                }} catch(e) {{ appendBubble("Error connecting to server.", false); }}
            }}

            // Background Animation
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth; canvas.height = window.innerHeight;
            function animate() {{
                ctx.clearRect(0,0,canvas.width, canvas.height);
                requestAnimationFrame(animate);
            }}
            animate();
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    user_name = data.get("user_name", "User")
    ctx = get_current_context()

    # 🔥 SYSTEM PROMPT ENHANCED FOR ANIMATIONS & MOBILE FIX 🔥
    sys_prompt = f"""
    You are {APP_NAME}, an Elite AI Developer created by {OWNER_NAME}.
    Current User: {user_name}. Time: {ctx['time_local']}.
    
    CRITICAL INSTRUCTIONS:
    1. If asked to build an app/UI/Game, ALWAYS include:
       - <meta name="viewport" content="width=device-width, initial-scale=1.0"> inside the HTML.
       - A link to Animate.css: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
       - Beautiful Google Fonts (Outfit or Poppins).
       - Glassmorphism effects and smooth transitions.
    2. Ensure all UI elements are inside a container with `max-width: 100%` and `box-sizing: border-box` so they never overflow on mobile.
    3. Make everything look "Premium" and "Dynamic" with hover effects and entrance animations.
    4. Write the ENTIRE code in ONE ```html block.
    """

    def generate():
        client = get_groq_client()
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
