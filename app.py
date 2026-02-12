from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json
import random

# ==========================================
# 🔹 Flux AI (UI Polish & Full Dynamic - Build 16.0.0) ✨
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
VERSION = "16.0.0"

# ⚠️ আপনার লিঙ্কসমূহ
FACEBOOK_URL = "https://facebook.com" 
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

# 🆕 EXPANDED SUGGESTION POOL (All options are here now)
SUGGESTION_POOL = [
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics simply"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Plan a 3-day trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Creative business ideas for startups"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML & CSS to a beginner"},
    {"icon": "fas fa-guitar", "text": "Write a song lyric about rain"},
    {"icon": "fas fa-camera", "text": "Photography tips for beginners"},
    {"icon": "fas fa-paint-brush", "text": "Generate a futuristic city image"},
    {"icon": "fas fa-calculator", "text": "Solve this math puzzle: 2 + 2 * 4"}
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
                --border: #374151;
                --accent: #3b82f6;
                --chat-accent: #3b82f6;
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
                --danger: #ef4444;
                --shadow-sm: 0 4px 12px rgba(0,0,0,0.1);
                --shadow-md: 0 8px 24px rgba(0,0,0,0.2);
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f9fafb;
                --text: #111827;
                --text-secondary: #6b7280;
                --input-bg: #f3f4f6;
                --border: #e5e7eb;
                --accent: #2563eb;
                --chat-accent: #2563eb;
                --bot-icon: linear-gradient(135deg, #2563eb, #7c3aed);
                --shadow-sm: 0 4px 12px rgba(0,0,0,0.05);
                --shadow-md: 0 8px 24px rgba(0,0,0,0.1);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            /* ✨ SIDEBAR POLISH ✨ */
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s ease;
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: var(--shadow-md);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; color: var(--text); letter-spacing: -0.5px; }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--input-bg); color: var(--text); border: 1px solid var(--border);
                border-radius: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px;
                margin-bottom: 20px; transition: all 0.2s ease; box-shadow: var(--shadow-sm);
            }}
            .new-chat-btn:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
            .new-chat-btn:active {{ transform: scale(0.98); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; padding-right: 5px; }}
            .history-item {{
                padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.95rem;
                transition: all 0.2s ease; display: flex; align-items: center; gap: 10px; font-weight: 500;
            }}
            .history-item:hover {{ background: var(--input-bg); color: var(--text); }}
            .history-item:active {{ transform: scale(0.98); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 5px; border-radius: 12px; border: 1px solid var(--border); }}
            .theme-btn {{ flex: 1; padding: 10px; border-radius: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-weight: 600; transition: 0.3s; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: var(--shadow-sm); }}

            .about-section {{ 
                display: none; background: var(--input-bg); padding: 20px; border-radius: 16px;
                margin-top: 5px; font-size: 0.9rem; text-align: center; border: 1px solid var(--border);
                box-shadow: var(--shadow-md); animation: fadeIn 0.3s ease;
            }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.3rem; margin: 0 12px; transition: 0.2s; display: inline-block; }}
            .about-link:hover {{ color: var(--accent); transform: scale(1.1); }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
                background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
                border-bottom: 1px solid var(--border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.9); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 20px 140px 20px; display: flex; flex-direction: column; gap: 25px; }}

            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding-top: 40px; padding-bottom: 80px;
            }}
            .icon-wrapper {{ 
                width: 85px; height: 85px; background: var(--bot-icon); border-radius: 28px; 
                display: flex; align-items: center; justify-content: center; font-size: 2.8rem; color: white; 
                margin-bottom: 25px; box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
                animation: float 4s ease-in-out infinite;
            }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 1.05rem; font-weight: 500; }}

            /* ✨ SUGGESTIONS POLISH ✨ */
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; width: 100%; max-width: 650px; }}
            .chip {{
                padding: 16px 20px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 18px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
                font-weight: 500; font-size: 0.95rem; display: flex; align-items: center; gap: 12px;
                box-shadow: var(--shadow-sm);
            }}
            body.light .chip {{ background: rgba(0,0,0,0.03); }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: var(--shadow-md); }}
            .chip:active {{ transform: scale(0.98); background: var(--input-bg); }}
            .chip i {{ color: var(--text); font-size: 1.2rem; opacity: 0.8; }}

            /* MESSAGES */
            .message-wrapper {{ display: flex; gap: 15px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.3s ease; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: var(--shadow-sm); }}
            .bot-avatar {{ background: var(--bot-icon); color: white; }}
            .user-avatar {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 85%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            .sender-name {{ font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px; font-weight: 600; }}
            .message-wrapper.user .sender-name {{ display: none; }}

            .bubble {{ 
                padding: 14px 18px; border-radius: 20px; font-size: 1.02rem; line-height: 1.6;
            }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; }}
            .user .bubble {{ background: var(--input-bg); border-radius: 20px 4px 20px 20px; color: var(--text); box-shadow: var(--shadow-sm); border: 1px solid var(--border); }}
            
            .bubble strong {{ color: var(--chat-accent); font-weight: 700; }}
            .bubble img {{ max-width: 100%; border-radius: 16px; margin-top: 12px; cursor: pointer; box-shadow: var(--shadow-md); border: 1px solid var(--border); }}
            .img-brand {{ font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px; display: flex; align-items: center; gap: 6px; font-weight: 600; opacity: 0.9; }}

            /* ✨ INPUT AREA POLISH ✨ */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 80%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 28px; padding: 10px 10px 10px 24px;
                border: 1px solid var(--border); box-shadow: var(--shadow-md); transition: all 0.3s ease;
            }}
            .input-box:focus-within {{ border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 15px 35px rgba(0,0,0,0.2); }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1.05rem; max-height: 180px; resize: none; padding: 12px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 45px; height: 45px;
                border-radius: 50%; cursor: pointer; margin-left: 12px; margin-bottom: 2px;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s;
            }}
            .send-btn:hover {{ transform: rotate(-10deg) scale(1.05); background: var(--accent); color: white; }}
            .send-btn:active {{ transform: scale(0.95); }}

            .modal-overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(5px);
            }}
            .modal-box {{
                background: var(--sidebar); border: 1px solid var(--border); padding: 30px; border-radius: 20px; width: 90%; max-width: 350px; text-align: center; box-shadow: var(--shadow-md);
            }}
            .btn-modal {{ padding: 12px; border-radius: 12px; border: none; font-weight: 700; cursor: pointer; flex: 1; margin: 0 8px; font-size: 0.95rem; transition: 0.2s; }}
            .btn-cancel {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            .btn-delete {{ background: var(--danger); color: white; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }}
            .btn-modal:hover {{ transform: translateY(-2px); }}

            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-12px); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
            .typing {{ display: flex; gap: 6px; padding: 10px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--text-secondary); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            
            pre {{ background: #0d1117 !important; padding: 20px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--border); box-shadow: var(--shadow-sm); }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.9rem; }}
        </style>
    </head>
    <body class="dark">
        
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="margin-top:0; color:var(--text); font-size: 1.3rem;">Clear History?</h3>
                <p style="color:var(--text-secondary); margin-bottom: 25px;">This action is irreversible. All conversations will be lost.</p>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal()">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete All</button>
                </div>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()" style="position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:150; display:none;"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div style="font-size:0.8rem; font-weight: 700; color:var(--text-secondary); margin-bottom:12px; letter-spacing: 1px;">RECENT</div>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>
                
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                
                <div id="about-info" class="about-section">
                    <strong style="font-size: 1.1rem;">{APP_NAME} v{VERSION}</strong><br>
                    <small style="color:var(--text-secondary)">Dev: {OWNER_NAME}</small><br>
                    <div style="margin:15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="display:block; margin-top:5px; font-weight:600;">All rights reserved by {OWNER_NAME} &copy; 2026</small>
                </div>
                <div class="history-item" onclick="openDeleteModal()" style="color:#ef4444;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.3rem; letter-spacing: -0.5px;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your intelligent AI companion.</div>
                    
                    <div class="suggestions" id="suggestion-box">
                        </div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message {APP_NAME}..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            
            let chats = JSON.parse(localStorage.getItem('flux_v16_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');

            const accentColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
            renderHistory();
            renderSuggestions(); 

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            // 🆕 FULLY DYNAMIC SUGGESTIONS (Pick 4 random from all)
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
                const selected = shuffled.slice(0, 4); // Pick 4 random
                let html = '';
                selected.forEach(s => {{
                    // FIX: Using icon directly in innerHTML to avoid f-string conflict
                    html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>';
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                const randomColor = accentColors[Math.floor(Math.random() * accentColors.length)];
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [], accent: randomColor }});
                saveData();
                renderHistory();
                renderSuggestions(); // Re-roll suggestions
                
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                msgInput.value = '';
                resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v16_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Conversation').substring(0, 22) + '</span>';
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;

                document.documentElement.style.setProperty('--chat-accent', chat.accent || 'var(--accent)');

                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none'; 

                if (chat.messages.length === 0) {{
                     chatBox.appendChild(welcomeScreen);
                     welcomeScreen.style.display = 'flex';
                }} else {{
                    chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                }}
                
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function addBrandingToImages() {{
                document.querySelectorAll('.bubble img').forEach(img => {{
                    if(img.closest('.img-container')) return; 
                    const container = document.createElement('div');
                    container.className = 'img-container';
                    img.parentNode.insertBefore(container, img);
                    container.appendChild(img);
                    const branding = document.createElement('div');
                    branding.className = 'img-brand';
                    branding.innerHTML = '<i class="fas fa-bolt" style="color:var(--chat-accent)"></i> Flux AI';
                    container.appendChild(branding);
                }});
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                
                wrapper.innerHTML = `
                    ${{avatar}}
                    <div class="bubble-container">
                        ${{name}}
                        <div class="bubble">${{marked.parse(text)}}</div>
                    </div>
                `;
                
                chatBox.appendChild(wrapper);
                if(!isUser) {{
                    hljs.highlightAll();
                    addBrandingToImages();
                }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="bubble-container">
                        <div class="sender-name">{APP_NAME}</div>
                        <div class="bubble" style="background:transparent; padding-left:0;"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>
                    </div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;
                
                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData();
                
                msgInput.value = '';
                resizeInput(msgInput);
                appendBubble(text, true);
                showTyping();

                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    removeTyping();
                    if(!res.ok) throw new Error("API Error");
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `
                        <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                        <div class="bubble-container">
                            <div class="sender-name">{APP_NAME}</div>
                            <div class="bubble"></div>
                        </div>`;
                    chatBox.appendChild(wrapper);
                    const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    hljs.highlightAll();
                    addBrandingToImages();

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Error connecting to server.", false);
                }}
            }}

            function openDeleteModal() {{ deleteModal.style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal() {{ deleteModal.style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v16_history'); location.reload(); }}
            
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
    
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, an advanced, expert-level AI assistant created by {OWNER_NAME}.
        
        CORE IDENTITY:
        - Name: {APP_NAME}
        - Developer: {OWNER_NAME}
        - Version: {VERSION}
        
        REAL-TIME CONTEXT:
        - Current Date: {ctx['date']}
        - Local Time (Dhaka): {ctx['time_local']}
        - UTC Time: {ctx['time_utc']}
        
        RULES:
        1. IMAGE GENERATION: If user asks for an image, output strictly: ![Flux Image](https://image.pollinations.ai/prompt/{{english_prompt}})
        2. INTELLIGENCE: Be precise, logical, and helpful.
        3. CONCISENESS: Keep casual conversation short.
        4. FORMATTING: Use **bold** for highlights.
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