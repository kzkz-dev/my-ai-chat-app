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
# 🔹 Flux AI (Repair Edition - Build 24.1.0) 🛠️
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "24.1.0"
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

# CONFIGURATION
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

# Check keys silently to prevent startup crash
if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found in environment variables.")

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
    
    # ⚠️ FIXED: Backslashes escaped (\\) and braces doubled ({{ }})
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
                --hue: 190;
                --bg: #050a14;
                --sidebar: rgba(10, 20, 30, 0.95);
                --text: #e0f2ff;
                --text-secondary: #8ba2b5;
                --accent: hsl(var(--hue), 100%, 50%);
                --glow: 0 0 15px hsl(var(--hue), 100%, 50%, 0.6);
                --input-bg: rgba(20, 30, 50, 0.8);
                --border: rgba(100, 200, 255, 0.15);
                --font-main: 'Rajdhani', sans-serif;
                --font-header: 'Orbitron', sans-serif;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: var(--font-main); height: 100vh; display: flex; overflow: hidden; 
            }}

            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}

            #sidebar {{
                width: 280px; height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); 
                position: absolute; z-index: 200; left: 0; top: 0; 
                background: var(--sidebar); backdrop-filter: blur(15px);
                transition: transform 0.3s ease; box-shadow: 10px 0 30px rgba(0,0,0,0.5);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ 
                font-family: var(--font-header); font-size: 1.8rem; font-weight: 900; 
                margin-bottom: 25px; display: flex; align-items: center; gap: 10px; 
                color: var(--text); text-shadow: var(--glow);
            }}
            
            .new-chat-btn {{
                width: 100%; padding: 14px; background: rgba(255,255,255,0.05); 
                color: var(--accent); border: 1px solid var(--accent);
                border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 10px;
                margin-bottom: 20px; transition: 0.3s; font-family: var(--font-header);
                box-shadow: var(--glow);
            }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }}
            .history-item {{
                padding: 12px; border-radius: 6px; cursor: pointer; color: var(--text-secondary); 
                font-size: 1rem; transition: 0.2s; display: flex; align-items: center; gap: 10px;
            }}
            .history-item:hover {{ background: rgba(255,255,255,0.05); color: var(--text); }}

            .theme-colors {{ display: flex; gap: 10px; justify-content: center; margin-top: auto; padding-top: 15px; border-top: 1px solid var(--border); }}
            .color-dot {{ width: 25px; height: 25px; border-radius: 50%; cursor: pointer; transition: 0.3s; }}
            .color-dot:hover {{ transform: scale(1.2); box-shadow: 0 0 10px currentColor; }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(5, 10, 20, 0.8); backdrop-filter: blur(10px);
                border-bottom: 1px solid var(--border);
            }}

            #chat-box {{ flex: 1; overflow-y: auto; padding: 20px 20px 100px 20px; display: flex; flex-direction: column; gap: 20px; }}

            /* ORB */
            .orb-container {{ width: 100px; height: 100px; position: relative; margin: 0 auto 20px auto; }}
            .orb {{
                position: absolute; width: 100%; height: 100%; border-radius: 50%;
                border: 2px solid var(--accent); border-top-color: transparent; border-bottom-color: transparent;
                animation: spin 3s linear infinite; box-shadow: var(--glow);
            }}
            .orb-core {{
                width: 30px; height: 30px; background: var(--accent); border-radius: 50%;
                position: absolute; top: 35px; left: 35px;
                box-shadow: 0 0 30px var(--accent); animation: pulse 2s infinite;
            }}

            .message-wrapper {{ display: flex; gap: 12px; width: 100%; max-width: 800px; margin: 0 auto; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ 
                width: 35px; height: 35px; border-radius: 6px; display: flex; align-items: center; justify-content: center; 
                background: rgba(255,255,255,0.05); border: 1px solid var(--border);
            }}
            .bubble {{ 
                padding: 12px 18px; border-radius: 10px; font-size: 1rem; line-height: 1.5; 
                background: rgba(10, 20, 35, 0.8); border: 1px solid var(--border); max-width: 90%;
            }}
            .user .bubble {{ border-color: var(--accent); background: rgba(0, 200, 255, 0.05); }}
            
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 15px;
                background: linear-gradient(to top, var(--bg) 90%, transparent); display: flex; justify-content: center;
            }}
            .input-box {{
                width: 100%; max-width: 800px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border: 1px solid var(--border); border-radius: 12px; padding: 8px;
            }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 120px; resize: none; padding: 10px; font-family: inherit;
            }}
            .send-btn {{
                background: var(--accent); color: #000; border: none; width: 40px; height: 40px;
                border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
            }}

            .energy-ball {{
                position: fixed; width: 20px; height: 20px; background: var(--accent); border-radius: 50%; 
                pointer-events: none; z-index: 9999; box-shadow: 0 0 20px var(--accent);
                animation: shootUp 0.6s ease-in-out forwards;
            }}

            #preview-modal {{
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.9); z-index: 300; justify-content: center; align-items: center;
            }}
            .preview-box {{ width: 95%; height: 90%; background: #fff; border-radius: 8px; display: flex; flex-direction: column; }}
            iframe {{ flex: 1; border: none; }}

            @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
            @keyframes pulse {{ 50% {{ transform: scale(0.8); opacity: 0.7; }} }}
            @keyframes shootUp {{ 0% {{ bottom: 60px; left: 50%; opacity: 1; }} 100% {{ bottom: 60%; left: 50%; opacity: 0; }} }}
        </style>
    </head>
    <body>
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div style="padding:10px; background:#222; display:flex; justify-content:space-between;">
                    <span style="color:white">Live Preview</span>
                    <button onclick="document.getElementById('preview-modal').style.display='none'" style="cursor:pointer;">Close</button>
                </div>
                <iframe id="code-frame"></iframe>
            </div>
        </div>

        <div class="overlay" onclick="document.getElementById('sidebar').classList.add('closed')"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">NEW CHAT</button>
            <div class="history-list" id="history-list"></div>
            <div class="theme-colors">
                <div class="color-dot" style="background:#00f3ff;" onclick="setTheme(190)"></div>
                <div class="color-dot" style="background:#a200ff;" onclick="setTheme(270)"></div>
                <div class="color-dot" style="background:#00ff88;" onclick="setTheme(150)"></div>
                <div class="color-dot" style="background:#ff0055;" onclick="setTheme(340)"></div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="document.getElementById('sidebar').classList.toggle('closed')" style="background:none; border:none; color:white; font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-family:var(--font-header);">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; text-align:center;">
                    <div class="orb-container"><div class="orb"></div><div class="orb-core"></div></div>
                    <div style="font-family:var(--font-header); font-size:1.8rem;">SYSTEM ONLINE</div>
                    <div class="suggestions" id="suggestion-box" style="margin-top:20px; display:grid; gap:10px;"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Enter command..." rows="1" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px'"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-location-arrow"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v24_1_history')) || [];
            let currentChatId = null;
            let currentHue = localStorage.getItem('flux_hue') || 190;
            
            document.documentElement.style.setProperty('--hue', currentHue);

            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth; canvas.height = window.innerHeight;
            
            let particles = [];
            for(let i=0; i<50; i++) particles.push({{x:Math.random()*canvas.width, y:Math.random()*canvas.height, vx:(Math.random()-.5), vy:(Math.random()-.5)}});
            
            function animateBg() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = `hsl(${{currentHue}}, 100%, 70%)`;
                particles.forEach((p, i) => {{
                    p.x+=p.vx; p.y+=p.vy;
                    if(p.x<0||p.x>canvas.width) p.vx*=-1;
                    if(p.y<0||p.y>canvas.height) p.vy*=-1;
                    ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, Math.PI*2); ctx.fill();
                    particles.slice(i+1).forEach(p2 => {{
                        let d = Math.hypot(p.x-p2.x, p.y-p2.y);
                        if(d<100) {{
                            ctx.strokeStyle = `hsla(${{currentHue}}, 100%, 70%, ${{1-d/100}})`;
                            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
                        }}
                    }});
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            function setTheme(hue) {{
                currentHue = hue; localStorage.setItem('flux_hue', hue);
                document.documentElement.style.setProperty('--hue', hue);
            }}

            function renderSuggestions() {{
                const box = document.getElementById('suggestion-box');
                box.innerHTML = '';
                allSuggestions.slice(0,4).forEach(s => {{
                    box.innerHTML += '<div class="bubble" style="cursor:pointer;" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>';
                }});
            }}
            renderSuggestions();
            renderHistory();

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "Mission " + new Date().toLocaleTimeString(), messages: [] }});
                localStorage.setItem('flux_v24_1_history', JSON.stringify(chats));
                renderHistory();
                document.getElementById('chat-box').innerHTML = '';
                document.getElementById('welcome').style.display = 'flex';
                document.getElementById('sidebar').classList.add('closed');
            }}

            function renderHistory() {{
                document.getElementById('history-list').innerHTML = chats.map(c => 
                    '<div class="history-item" onclick="loadChat(' + c.id + ')"><i class="far fa-comment"></i> ' + c.title.substring(0,20) + '</div>'
                ).join('');
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                document.getElementById('chat-box').innerHTML = '';
                document.getElementById('welcome').style.display = 'none';
                chat.messages.forEach(m => appendBubble(m.text, m.role === 'user', false));
                document.getElementById('sidebar').classList.add('closed');
            }}

            function appendBubble(text, isUser, animate=true) {{
                document.getElementById('welcome').style.display = 'none';
                const div = document.createElement('div');
                div.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                div.innerHTML = `<div class="avatar ${{isUser?'':'bot-avatar'}}">${{isUser?'<i class="fas fa-user"></i>':'<i class="fas fa-bolt"></i>'}}</div><div class="bubble">${{marked.parse(text)}}</div>`;
                document.getElementById('chat-box').appendChild(div);
                
                // Live Preview Button Logic
                if(!isUser && text.includes('```html')) {{
                    const codeMatch = text.match(/```html([\\s\\S]*?)```/);
                    if(codeMatch) {{
                        const btn = document.createElement('button');
                        btn.innerText = '▶ Run Code';
                        btn.style.marginTop = '10px'; btn.style.cursor = 'pointer';
                        btn.onclick = () => {{
                            document.getElementById('preview-modal').style.display='flex';
                            document.getElementById('code-frame').srcdoc = codeMatch[1];
                        }};
                        div.querySelector('.bubble').appendChild(btn);
                    }}
                }}
                
                div.scrollIntoView({{behavior:'smooth'}});
            }}

            function sendSuggestion(text) {{ document.getElementById('msg').value = text; sendMessage(); }}

            async function sendMessage() {{
                const input = document.getElementById('msg');
                const text = input.value.trim();
                if(!text) return;
                
                // Energy Trail
                const ball = document.createElement('div'); ball.className='energy-ball';
                document.body.appendChild(ball); setTimeout(()=>ball.remove(), 600);

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{role:'user', text:text}});
                appendBubble(text, true);
                input.value = '';

                const context = chat.messages.map(m => ({{role:m.role, content:m.text}}));
                try {{
                    const res = await fetch('/chat', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{messages:context}}) }});
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    const div = document.createElement('div');
                    div.className = 'message-wrapper bot';
                    div.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble"></div>`;
                    document.getElementById('chat-box').appendChild(div);
                    const bubble = div.querySelector('.bubble');

                    while(true) {{
                        const {{done, value}} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubble.innerHTML = marked.parse(botResp);
                        div.scrollIntoView({{behavior:'smooth'}});
                    }}
                    chat.messages.push({{role:'assistant', text:botResp}});
                    localStorage.setItem('flux_v24_1_history', JSON.stringify(chats));
                    
                    if(botResp.includes('```html')) {{
                         const codeMatch = botResp.match(/```html([\\s\\S]*?)```/);
                         if(codeMatch) {{
                             const btn = document.createElement('button');
                             btn.innerText = '▶ Run Code';
                             btn.style.marginTop = '10px'; btn.style.cursor = 'pointer';
                             btn.onclick = () => {{
                                 document.getElementById('preview-modal').style.display='flex';
                                 document.getElementById('code-frame').srcdoc = codeMatch[1];
                             }};
                             bubble.appendChild(btn);
                         }}
                    }}

                }} catch(e) {{
                    appendBubble("⚠️ System Offline. Check API Keys.", false);
                }}
            }}
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
        You are {APP_NAME}, a highly intelligent AI assistant from the future.
        
        IDENTITY:
        - Created by: {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
        - Tone: Smart, Futuristic but friendly.
        
        CONTEXT:
        - Time: {ctx['time_local']} (Dhaka)
        
        RULES:
        1. **NO SCRIPT FORMAT**: Reply directly.
        2. **CODING**: If asked for HTML, provide a complete snippet with ```html ... ``` so the user can preview it.
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
                if not client: yield "⚠️ API Key Missing."; return
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
                # Rotate key if error
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ System overloaded or Invalid API Key."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)