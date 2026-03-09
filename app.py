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
# 🔹 Flux AI (Ultimate Intelligence - Build 29.2.3) 🧠
# 🔥 FIXED: INTERNAL SERVER ERROR & MOBILE OVERFLOW 🔥
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "29.2.3"
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
    
    # Using a standard string and .replace() to avoid f-string curly brace errors
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>[[APP_NAME]]</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {
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
            }

            body.light {
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
            }

            * { box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }
            body { 
                margin: 0; background: var(--bg-gradient); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.4s ease;
            }

            #neuro-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }
            
            #sidebar { width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid var(--glass-border); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.4s ease; position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 10px 0 30px rgba(0,0,0,0.3); background: var(--sidebar-bg); }
            #sidebar.closed { transform: translateX(-105%); box-shadow: none; }
            
            .brand { font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }
            .brand i { background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }
            
            .new-chat-btn { width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid var(--glass-border); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; transition: all 0.4s ease; }
            .history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
            .history-item { padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; transition: all 0.3s ease; display: flex; align-items: center; gap: 10px; font-weight: 500; }
            .history-item:hover { background: rgba(125, 125, 125, 0.1); color: var(--text); }

            header { height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100; backdrop-filter: blur(10px); }
            
            #main { flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }
            #chat-box { flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; overflow-x: hidden; }

            .welcome-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }
            .icon-wrapper { width: 80px; height: 80px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 3rem; margin-bottom: 25px; animation: levitate 4s ease-in-out infinite; }
            .icon-wrapper i { background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }

            .suggestions { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; width: 100%; max-width: 750px; }
            .chip { padding: 14px 16px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 16px; cursor: pointer; color: var(--text-secondary); transition: 0.4s; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; }
            .chip:hover { border-color: var(--accent); color: var(--text); transform: translateY(-3px); }

            .message-wrapper { display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: fadeIn 0.4s ease; }
            .message-wrapper.user { flex-direction: row-reverse; }
            .avatar { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
            .bot-avatar { background: var(--bot-grad); color: white; }
            .user-avatar { background: rgba(125,125,125,0.1); border: 1px solid var(--glass-border); }

            .bubble { padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; position: relative; max-width: 100%; }
            .user .bubble { background: var(--user-grad); color: white; border-radius: 20px 4px 20px 20px; }
            
            /* DEEP-BRAIN PROCESSOR */
            .brain-container { width: 100%; background: #000; border: 1px solid var(--glass-border); border-radius: 16px; padding: 20px; font-family: 'Fira Code', monospace; margin-bottom: 15px; box-sizing: border-box; }
            .brain-header { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 10px; }
            .brain-title { color: var(--terminal-green); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; }
            .brain-logs { font-size: 0.8rem; color: #a3a3a3; min-height: 60px; }
            .log-line::before { content: "> "; color: var(--terminal-green); }

            /* MOBILE FIXED ARTIFACTS */
            .artifact-container { width: 100%; max-width: 100%; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 16px; overflow: hidden; margin-top: 15px; box-sizing: border-box; }
            .artifact-header { background: rgba(125,125,125,0.1); padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
            .artifact-content { width: 100%; height: 350px; background: #fff; }
            .artifact-content iframe { width: 100%; height: 100%; border: none; }

            pre { background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); margin-top: 15px; max-width: 100%; position: relative; }
            .copy-btn { position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.1); border: none; color: white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.7rem; }

            #input-area { position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; }
            .input-box { width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 28px; padding: 10px 10px 10px 20px; border: 1px solid var(--glass-border); }
            textarea { flex: 1; background: transparent; border: none; color: var(--text); font-size: 1.05rem; max-height: 150px; resize: none; padding: 10px 0; font-family: inherit; }
            .send-btn { background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 12px; display: flex; align-items: center; justify-content: center; }

            .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(8px); }
            .modal-box { background: var(--sidebar-bg); border: 1px solid var(--glass-border); padding: 30px; border-radius: 20px; width: 90%; max-width: 350px; text-align: center; }

            #preview-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; }
            .preview-box { width: 95%; height: 90%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; }

            @keyframes levitate { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <h3>Admin Access</h3>
                <input type="password" id="admin-pass" style="width:100%; padding:12px; margin:15px 0; background:rgba(0,0,0,0.2); color:white; border:1px solid var(--glass-border); border-radius:10px;">
                <button onclick="verifyAdmin()" style="width:100%; padding:10px; background:var(--accent); border:none; border-radius:10px; font-weight:700;">Login</button>
                <button onclick="closeModal('admin-auth-modal')" style="margin-top:10px; background:none; border:none; color:var(--text-secondary);">Cancel</button>
            </div>
        </div>

        <div id="preview-modal">
            <div class="preview-box">
                <div style="padding:10px; background:#f0f0f0; display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#000; font-weight:700;">App Preview</span>
                    <button onclick="closePreview()" style="background:red; color:white; border:none; padding:5px 15px; border-radius:5px;">Close</button>
                </div>
                <iframe id="fullscreen-frame" style="flex:1; border:none;"></iframe>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> [[APP_NAME]]</div>
            <button class="new-chat-btn" onclick="startNewChat()"><i class="fas fa-plus"></i> New Chat</button>
            <div class="history-list" id="history-list"></div>
            <div style="margin-top:auto; padding-top:20px;">
                <div class="history-item" onclick="openModal('admin-auth-modal')"><i class="fas fa-shield-alt"></i> Admin Panel</div>
                <div class="history-item" onclick="clearLocalHistory()" style="color:var(--danger);"><i class="fas fa-trash"></i> Clear History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800;">[[APP_NAME]]</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem;"><i class="fas fa-edit"></i></button>
            </header>
            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <h2 style="margin-bottom:30px;">How can I help you today?</h2>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>
            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Type a message..." rows="1" oninput="this.style.height='auto';this.style.height=this.scrollHeight+'px'"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({ breaks: true, gfm: true });
            const allSuggestions = [[SUGGESTIONS_JSON]];
            let chats = JSON.parse(localStorage.getItem('flux_history_v29')) || [];
            let currentChatId = null;

            // Neuro BG
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
            window.onresize = resize; resize();
            class P {
                constructor() { this.x=Math.random()*canvas.width; this.y=Math.random()*canvas.height; this.vx=(Math.random()-0.5)*0.5; this.vy=(Math.random()-0.5)*0.5; }
                draw() { 
                    ctx.fillStyle = '#00f3ff22'; ctx.beginPath(); ctx.arc(this.x,this.y,2,0,Math.PI*2); ctx.fill(); 
                }
            }
            for(let i=0; i<40; i++) particles.push(new P());
            function anim() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                particles.forEach(p => {
                    p.x+=p.vx; p.y+=p.vy;
                    if(p.x<0||p.x>canvas.width) p.vx*=-1;
                    if(p.y<0||p.y>canvas.height) p.vy*=-1;
                    p.draw();
                });
                requestAnimationFrame(anim);
            }
            anim();

            function toggleSidebar() { 
                document.getElementById('sidebar').classList.toggle('closed');
                document.querySelector('.overlay').style.display = document.getElementById('sidebar').classList.contains('closed') ? 'none' : 'block';
            }

            function renderSuggestions() {
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {
                    html += `<div class="chip" onclick="sendSug('${s.text}')"><i class="${s.icon}"></i> ${s.text}</div>`;
                });
                document.getElementById('suggestion-box').innerHTML = html;
            }
            renderSuggestions();

            function sendSug(txt) { document.getElementById('msg').value = txt; sendMessage(); }

            function appendBubble(text, isUser) {
                document.getElementById('welcome').style.display = 'none';
                const wrap = document.createElement('div');
                wrap.className = `message-wrapper ${isUser ? 'user' : 'bot'}`;
                wrap.innerHTML = `
                    <div class="avatar ${isUser ? 'user-avatar' : 'bot-avatar'}"><i class="fas ${isUser ? 'fa-user' : 'fa-bolt'}"></i></div>
                    <div class="bubble">${isUser ? text : marked.parse(text)}</div>
                `;
                document.getElementById('chat-box').appendChild(wrap);
                if(!isUser) { hljs.highlightAll(); checkArtifacts(text, wrap.querySelector('.bubble')); }
                document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
            }

            function checkArtifacts(text, el) {
                const match = text.match(/```html([\\s\\S]*?)```/);
                if(match) {
                    const code = match[1];
                    const div = document.createElement('div');
                    div.className = 'artifact-container';
                    div.innerHTML = `
                        <div class="artifact-header">
                            <span><i class="fas fa-code"></i> Live Preview</span>
                            <button onclick="openFull('${encodeURIComponent(code)}')" style="background:var(--accent); border:none; padding:4px 10px; border-radius:5px; font-size:0.8rem;">Fullscreen</button>
                        </div>
                        <div class="artifact-content"><iframe srcdoc="${code.replace(/"/g, '&quot;')}"></iframe></div>
                    `;
                    el.appendChild(div);
                }
            }

            window.openFull = (c) => {
                document.getElementById('preview-modal').style.display = 'flex';
                document.getElementById('fullscreen-frame').srcdoc = decodeURIComponent(c);
            };
            window.closePreview = () => { document.getElementById('preview-modal').style.display = 'none'; };

            function showThinking() {
                const div = document.createElement('div');
                div.id = 'thinker';
                div.className = 'message-wrapper bot';
                div.innerHTML = `
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="bubble" style="width:100%">
                        <div class="brain-container">
                            <div class="brain-header"><i class="fas fa-microchip" style="color:#0f0"></i> <span class="brain-title">Deep-Brain Processor</span></div>
                            <div class="brain-logs" id="logs"></div>
                        </div>
                    </div>
                `;
                document.getElementById('chat-box').appendChild(div);
                const logs = ["Analyzing input...", "Compiling neural nodes...", "Optimizing response..."];
                let i=0;
                window.thinkInt = setInterval(() => {
                    if(i<logs.length) {
                        const l = document.createElement('div'); l.className='log-line'; l.innerText=logs[i];
                        document.getElementById('logs').appendChild(l); i++;
                    } else clearInterval(window.thinkInt);
                }, 600);
            }

            async function sendMessage() {
                const input = document.getElementById('msg');
                const text = input.value.trim();
                if(!text) return;
                input.value = ''; input.style.height = 'auto';
                appendBubble(text, true);
                showThinking();

                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ messages: [{role:'user', content:text}] })
                    });
                    document.getElementById('thinker').remove();
                    clearInterval(window.thinkInt);
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botTxt = '';
                    const wrap = document.createElement('div'); wrap.className='message-wrapper bot';
                    wrap.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble"></div>`;
                    document.getElementById('chat-box').appendChild(wrap);
                    const b = wrap.querySelector('.bubble');

                    while(true) {
                        const {done, value} = await reader.read();
                        if(done) break;
                        botTxt += decoder.decode(value);
                        b.innerHTML = marked.parse(botTxt);
                        document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
                    }
                    hljs.highlightAll();
                    checkArtifacts(botTxt, b);
                } catch(e) { appendBubble("Connection Error.", false); }
            }

            function startNewChat() { location.reload(); }
            function openModal(id) { document.getElementById(id).style.display='flex'; }
            function closeModal(id) { document.getElementById(id).style.display='none'; }
            function clearLocalHistory() { localStorage.removeItem('flux_history_v29'); location.reload(); }
            function verifyAdmin() {
                if(document.getElementById('admin-pass').value === '[[ADMIN_PASS]]') {
                    alert("Welcome Admin. Stats feature coming soon.");
                    closeModal('admin-auth-modal');
                } else { alert("Wrong Password!"); }
            }
        </script>
    </body>
    </html>
    """
    
    # Replacing placeholders safely
    resp = html_template.replace("[[APP_NAME]]", APP_NAME)
    resp = resp.replace("[[SUGGESTIONS_JSON]]", suggestions_json)
    resp = resp.replace("[[ADMIN_PASS]]", ADMIN_PASSWORD)
    
    return resp

@app.route("/chat", methods=["POST"])
def chat():
    if not SYSTEM_ACTIVE: return Response("System offline.", status=503)
    data = request.json
    messages = data.get("messages", [])
    
    sys_prompt = f"You are {APP_NAME}, an Elite AI. When building apps, always use Animate.css and meta viewport for mobile. Ensure max-width: 100% on all containers."

    def generate():
        client = get_groq_client()
        if not client: yield "API Key Missing!"; return
        
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
