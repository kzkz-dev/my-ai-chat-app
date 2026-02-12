from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json
import random

# ==========================================
# 🔹 Flux AI (Compact & Colorful - Build 11.0.0) 🌈
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
VERSION = "11.0.0"

# ⚠️ আপনার আসল ফেসবুক এবং ওয়েবসাইটের লিঙ্ক দিন ⚠️
FACEBOOK_URL = "Not available right now" 
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"      

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

# 🔄 DYNAMIC SUGGESTIONS POOL
SUGGESTION_POOL = [
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script for web scraping"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Computing simply"},
    {"icon": "fas fa-dumbbell", "text": "Give me a 30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-book-open", "text": "Summarize the book 'Atomic Habits'"},
    {"icon": "fas fa-plane", "text": "Plan a 3-day trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Give me 5 creative business ideas"},
    {"icon": "fas fa-guitar", "text": "Write a short song lyric about rain"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML and CSS to a beginner"}
]

@app.route("/")
def home():
    random_suggestions = random.sample(SUGGESTION_POOL, 2)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME}</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #0b0f19;
                --sidebar: #111827;
                --text: #f3f4f6;
                --text-secondary: #9ca3af;
                --input-bg: #1f2937;
                --user-bubble: #2563eb;
                --border: #1f2937;
                --accent: #3b82f6; /* Default accent */
                --chat-accent: #3b82f6; /* Dynamic accent per chat */
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
                --danger: #ef4444;
                --font-size-base: 14.5px; /* COMPACT FONT SIZE */
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f9fafb;
                --text: #111827;
                --text-secondary: #6b7280;
                --input-bg: #f3f4f6;
                --user-bubble: #2563eb;
                --border: #e5e7eb;
                --accent: #2563eb;
                --chat-accent: #2563eb;
                --bot-icon: linear-gradient(135deg, #2563eb, #7c3aed);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; font-size: var(--font-size-base); }}

            ::-webkit-scrollbar {{ width: 4px; height: 4px; }} /* Thinner scrollbar */
            ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}
            
            /* COMPACT SIDEBAR */
            #sidebar {{
                width: 260px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 16px; border-right: 1px solid var(--border); transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 5px 0 25px rgba(0,0,0,0.3);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; color: var(--text); letter-spacing: -0.5px; user-select: none; }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; font-size: 1.4rem; }}
            
            .new-chat-btn {{
                width: 100%; padding: 10px; background: transparent; color: var(--text); border: 1px solid var(--border);
                border-radius: 10px; font-weight: 500; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 8px;
                transition: all 0.2s ease; margin-bottom: 15px;
            }}
            .new-chat-btn:active {{ transform: scale(0.95); background: var(--input-bg); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; padding-right: 5px; margin-bottom: 10px; }}
            .history-item {{
                padding: 8px 10px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 10px;
                font-size: 0.85rem; transition: background 0.2s; user-select: none;
            }}
            .history-item:active {{ background: var(--input-bg); color: var(--text); transform: scale(0.98); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 12px; display: flex; flex-direction: column; gap: 6px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 4px; border-radius: 8px; }}
            .theme-btn {{ flex: 1; padding: 6px; border-radius: 6px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-size: 0.8rem; font-weight: 500; transition: 0.3s; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: 0 2px 5px rgba(0,0,0,0.15); }}

            /* COMPACT HEADER */
            header {{
                height: 50px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 12px; z-index: 100; background: rgba(11, 15, 25, 0.7); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
                border-bottom: 1px solid rgba(255,255,255,0.05); position: absolute; top: 0; left: 0; right: 0;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.8); border-bottom: 1px solid rgba(0,0,0,0.05); }}
            header button {{ font-size: 1.1rem !important; }}
            header span {{ font-size: 1.1rem !important; }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            #chat-box {{ 
                flex: 1; overflow-y: auto; padding: 65px 15px 130px 15px; 
                display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth;
            }}

            /* COMPACT WELCOME SCREEN */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                min-height: 80%; text-align: center; animation: popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                padding-top: 40px; padding-bottom: 30px;
            }}
            .icon-wrapper {{ 
                width: 60px; height: 60px; background: var(--bot-icon); border-radius: 18px; 
                display: flex; align-items: center; justify-content: center; font-size: 2rem; color: white; 
                margin-bottom: 15px; box-shadow: 0 0 25px rgba(59, 130, 246, 0.4);
                animation: float 3s ease-in-out infinite; flex-shrink: 0;
            }}
            .welcome-title {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 30px; font-weight: 400; }}
            
            .suggestions {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; width: 100%; max-width: 500px; }}
            .chip {{
                padding: 12px; background: transparent; border-radius: 14px; cursor: pointer; text-align: left;
                border: 1px solid var(--border); transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); font-size: 0.85rem; color: var(--text-secondary);
                background-color: rgba(255,255,255,0.02);
            }}
            .chip i {{ color: var(--text); margin-bottom: 8px; display: block; font-size: 1.1rem; opacity: 0.9; }}
            
            /* COMPACT MESSAGES */
            .message-wrapper {{ display: flex; gap: 10px; width: 100%; max-width: 800px; margin: 0 auto; }}
            .avatar {{ width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; }}
            .bubble-container {{ display: flex; flex-direction: column; width: calc(100% - 40px); }}
            .sender-name {{ font-size: 0.7rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 2px; margin-top: 2px; }}
            
            .bubble {{ font-size: 0.92rem; line-height: 1.5; color: var(--text); word-break: break-word; overflow-wrap: break-word; }}
            .bubble p {{ margin-bottom: 10px; }}
            
            /* DYNAMIC COLORED HIGHLIGHTS */
            .bubble strong {{ font-weight: 600; color: var(--chat-accent); }}
            
            /* CLEAN IMAGES (No download button) */
            .bubble img {{
                max-width: 100%; border-radius: 10px; margin-top: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2); display: block; cursor: pointer;
            }}

            .bot .bubble {{ padding: 0; margin-top: 4px; }}
            .user .bubble {{ background: var(--input-bg); padding: 10px 14px; border-radius: 18px 4px 18px 18px; }}

            /* COMPACT INPUT AREA */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 10px 15px 15px 15px;
                background: linear-gradient(to top, var(--bg) 80%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 750px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 20px; padding: 5px 5px 5px 15px;
                border: 1px solid var(--border); transition: 0.3s; box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 0.95rem; max-height: 130px; resize: none;
                padding: 10px 0; font-family: inherit; line-height: 1.4;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 38px; height: 38px;
                border-radius: 50%; cursor: pointer; margin-left: 8px; display: flex; align-items: center; justify-content: center;
                font-size: 0.9rem; flex-shrink: 0; margin-bottom: 2px;
            }}

            /* Keyframes & Other styles remain similar but compacted where applicable */
            @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-6px); box-shadow: 0 12px 25px rgba(59, 130, 246, 0.5); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            .typing {{ display: flex; gap: 4px; align-items: center; padding: 8px 0; }}
            .dot {{ width: 6px; height: 6px; background: var(--text-secondary); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            pre {{ border-radius: 12px; padding: 35px 12px 12px 12px; margin: 12px 0; font-size: 0.8em; }}
            pre::before {{ top: 12px; left: 12px; width: 10px; height: 10px; }}
            .copy-btn {{ top: 6px; right: 8px; padding: 4px 10px; font-size: 0.7rem; }}
        </style>
    </head>
    <body class="dark">
        <div id="delete-modal" class="modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); z-index:9999; justify-content:center; align-items:center;">
            <div class="modal-box" style="background:var(--sidebar); border:1px solid var(--border); padding:20px; border-radius:16px; width:85%; max-width:300px; text-align:center;">
                <div class="modal-title" style="font-size:1rem; font-weight:600; margin-bottom:8px; color:var(--text);"><i class="fas fa-trash-alt" style="color:var(--danger)"></i> Clear History?</div>
                <div class="modal-desc" style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:20px;">All conversations will be deleted.</div>
                <div class="modal-buttons" style="display:flex; gap:8px;">
                    <button class="btn-modal" onclick="closeModal()" style="padding:8px 16px; border-radius:8px; border:none; font-weight:600; cursor:pointer; flex:1; background:var(--input-bg); color:var(--text);">Cancel</button>
                    <button class="btn-modal" onclick="confirmDelete()" style="padding:8px 16px; border-radius:8px; border:none; font-weight:600; cursor:pointer; flex:1; background:var(--danger); color:white;">Delete</button>
                </div>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()" style="position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:150; display:none;"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-pen-to-square"></i> New chat
            </button>
            <div style="font-size:0.7rem; font-weight:600; color:var(--text-secondary); margin-bottom:8px; padding-left:4px; text-transform: uppercase; letter-spacing: 0.5px;">Recent</div>
            <div class="history-list" id="history-list"></div>
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>
                <div class="history-item" onclick="openDeleteModal()" style="color: #ef4444; justify-content: flex-start; margin-top:4px;">
                    <i class="fas fa-trash-alt"></i> Delete history
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.1rem; cursor:pointer; padding: 4px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:600; font-size:1.1rem; letter-spacing: -0.5px;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.1rem; cursor:pointer; padding: 4px;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your brilliant AI assistant is ready.</div>
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[0]['text']}')"><i class="{random_suggestions[0]['icon']}"></i> {random_suggestions[0]['text']}</div>
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[1]['text']}')"><i class="{random_suggestions[1]['icon']}"></i> {random_suggestions[1]['text']}</div>
                        <div class="chip" onclick="sendSuggestion('Generate a futuristic cyberpunk city image')"><i class="fas fa-paint-brush"></i> Generate Image</div>
                        <div class="chip" onclick="sendSuggestion('Solve this math puzzle: 2 + 2 * 4')"><i class="fas fa-calculator"></i> Solve Math</div>
                    </div>
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
            let chats = JSON.parse(localStorage.getItem('flux_v11_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');
            const welcomeScreen = document.getElementById('welcome');
            const sendBtn = document.getElementById('send-btn-icon');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');

            // 🎨 DYNAMIC ACCENT COLORS 🎨
            const accentColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
            renderHistory();

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function resizeInput(el) {{
                el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 120) + 'px';
                sendBtn.classList.toggle('active-typing', el.value.trim() !== "");
            }}

            function toggleSidebar() {{
                sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block';
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                // Pick random color for new chat
                const randomColor = accentColors[Math.floor(Math.random() * accentColors.length)];
                chats.unshift({{ id: currentChatId, title: "New conversation", messages: [], accent: randomColor }});
                saveData(); renderHistory(); loadChat(currentChatId);
            }}

            function saveData() {{ localStorage.setItem('flux_v11_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = `<span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{(chat.title || 'New conversation').substring(0, 25)}}</span>`;
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                // Set dynamic accent color
                document.documentElement.style.setProperty('--chat-accent', chat.accent || 'var(--accent)');
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                sidebar.classList.add('closed'); overlay.style.display = 'none';
                msgInput.value = ''; resizeInput(msgInput);
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if(pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button'); btn.className = 'copy-btn'; btn.innerHTML = '<i class="far fa-copy"></i>';
                    btn.onclick = () => {{ navigator.clipboard.writeText(pre.querySelector('code').innerText); btn.innerHTML = '<i class="fas fa-check"></i>'; setTimeout(() => btn.innerHTML = '<i class="far fa-copy"></i>', 2000); }};
                    pre.appendChild(btn);
                }});
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                wrapper.innerHTML = `
                    <div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>
                    <div class="bubble-container">
                        <div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>
                        <div class="bubble">${{marked.parse(text)}}</div>
                    </div>`;
                chatBox.appendChild(wrapper);
                if(!isUser) {{ hljs.highlightAll(); addCopyButtons(); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div'); wrapper.id = 'typing-indicator'; wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar thinking"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}...</div><div class="bubble"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div></div>`;
                chatBox.appendChild(wrapper); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}
            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim(); if(!text) return;
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 30); renderHistory(); }}
                saveData(); msgInput.value = ''; resizeInput(msgInput);
                appendBubble(text, true); showTyping();

                const context = chat.messages.slice(-15).map(m => ({{ role: m.role, content: m.text }}));
                try {{
                    const res = await fetch('/chat', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ messages: context }}) }});
                    removeTyping(); if(!res.ok) throw new Error("API Error");
                    const reader = res.body.getReader(); const decoder = new TextDecoder(); let botResp = '';
                    
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar thinking"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper); const bubble = wrapper.querySelector('.bubble'); const avatar = wrapper.querySelector('.avatar');

                    while(true) {{ const {{ done, value }} = await reader.read(); if(done) break; botResp += decoder.decode(value); bubble.innerHTML = marked.parse(botResp); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }}); }}
                    avatar.classList.remove('thinking'); chat.messages.push({{ role: 'assistant', text: botResp }}); saveData(); hljs.highlightAll(); addCopyButtons();
                }} catch(e) {{ removeTyping(); appendBubble("⚠️ Connection Error.", false); }}
            }}

            function openDeleteModal() {{ deleteModal.style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal() {{ deleteModal.style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v11_history'); location.reload(); }}
            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    ctx = get_current_context()
    
    # 🧠 SUPERCHARGED BRAIN PROMPT 🧠
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a highly intelligent, expert-level AI assistant created by {OWNER_NAME}.
        Your responses must be accurate, insightful, and comprehensively detailed when necessary.
        
        🎨 IMAGE GENERATION RULE:
        If user wants an image, start reply with "🎨 Generating image..." then a blank line, then: ![Flux Image](https://image.pollinations.ai/prompt/{{detailed_prompt_here}})
        
        🧠 TONE & FORMAT:
        - Expert, confident, empathetic.
        - Use extensive Markdown (bold for key terms, lists, tables, code blocks).
        - No real-time news access.
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
                    temperature=0.6, # Lower temperature for smarter, more focused answers
                    max_tokens=2048
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