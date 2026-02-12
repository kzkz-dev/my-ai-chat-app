from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json
import random

# ==========================================
# 🔹 Flux AI (Fixed & Polished - Build 12.0.0) 🛠️
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
VERSION = "12.0.0"

# ⚠️ আপনার লিঙ্কগুলো (ফাঁকা থাকলে সমস্যা নেই)
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

SUGGESTION_POOL = [
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute workout plan"},
    {"icon": "fas fa-utensils", "text": "Healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Plan a trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Creative business ideas"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML to a beginner"}
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
                --border: #374151;
                --accent: #3b82f6;
                --chat-accent: #3b82f6; /* Dynamic Color */
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
                --danger: #ef4444;
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
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            /* SIDEBAR */
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s ease;
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 5px 0 25px rgba(0,0,0,0.5);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; color: var(--text); }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: transparent; color: var(--text); border: 1px solid var(--border);
                border-radius: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 10px;
                margin-bottom: 20px; transition: 0.2s;
            }}
            .new-chat-btn:active {{ background: var(--input-bg); transform: scale(0.98); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }}
            .history-item {{
                padding: 12px; border-radius: 10px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.95rem;
            }}
            .history-item:active {{ background: var(--input-bg); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 5px; border-radius: 10px; }}
            .theme-btn {{ flex: 1; padding: 8px; border-radius: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}

            /* ABOUT SECTION (Restored) */
            .about-section {{ 
                display: none; background: var(--input-bg); padding: 15px; border-radius: 12px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--border);
            }}
            .about-section.show {{ display: block; animation: fadeIn 0.3s; }}
            .about-link {{ color: var(--text); font-size: 1.2rem; margin: 0 10px; }}

            /* HEADER */
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 15px;
                background: rgba(11, 15, 25, 0.8); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(255,255,255,0.05); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.9); border-bottom: 1px solid rgba(0,0,0,0.1); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 15px 140px 15px; display: flex; flex-direction: column; gap: 20px; }}

            /* WELCOME SCREEN (Restored) */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 80%; text-align: center; padding-top: 50px;
            }}
            .icon-wrapper {{ 
                width: 80px; height: 80px; background: var(--bot-icon); border-radius: 25px; 
                display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: white; 
                margin-bottom: 20px; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
            }}
            .welcome-title {{ font-size: 2rem; font-weight: 700; margin-bottom: 10px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; }}

            .suggestions {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; }}
            .chip {{
                padding: 15px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 15px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: 0.2s;
            }}
            body.light .chip {{ background: rgba(0,0,0,0.03); }}
            .chip:active {{ transform: scale(0.98); background: var(--input-bg); }}
            .chip i {{ color: var(--text); font-size: 1.2rem; margin-bottom: 8px; display: block; }}

            /* MESSAGES (Fixed Alignment) */
            .message-wrapper {{ display: flex; gap: 12px; width: 100%; max-width: 800px; margin: 0 auto; }}
            
            /* USER ON RIGHT */
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
            .bot-avatar {{ background: var(--bot-icon); color: white; }}
            .user-avatar {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 80%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            
            .sender-name {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 4px; }}
            .message-wrapper.user .sender-name {{ display: none; }}

            .bubble {{ 
                padding: 12px 16px; border-radius: 18px; font-size: 1rem; line-height: 1.5; word-wrap: break-word;
            }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; }}
            .user .bubble {{ background: var(--input-bg); border-radius: 18px 4px 18px 18px; color: var(--text); }}
            
            /* Dynamic Highlights */
            .bubble strong {{ color: var(--chat-accent); font-weight: 700; }}

            .bubble img {{ max-width: 100%; border-radius: 12px; margin-top: 10px; cursor: pointer; }}

            /* INPUT AREA */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 15px;
                background: linear-gradient(to top, var(--bg) 80%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 800px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 25px; padding: 8px 8px 8px 20px;
                border: 1px solid var(--border); box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px; resize: none; padding: 10px 0;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 40px; height: 40px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; margin-bottom: 2px;
                display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
            }}

            /* Delete Modal */
            .modal-overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7); display: none; justify-content: center; align-items: center; z-index: 9999;
            }}
            .modal-box {{
                background: var(--sidebar); border: 1px solid var(--border); padding: 25px; border-radius: 15px; width: 90%; max-width: 320px; text-align: center;
            }}
            .btn-modal {{ padding: 10px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; flex: 1; margin: 0 5px; }}
            .btn-cancel {{ background: var(--input-bg); color: var(--text); }}
            .btn-delete {{ background: var(--danger); color: white; }}

            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            .typing {{ display: flex; gap: 5px; padding: 10px 0; }}
            .dot {{ width: 7px; height: 7px; background: var(--text-secondary); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            
            /* Markdown Styles */
            pre {{ background: #111; padding: 15px; border-radius: 10px; overflow-x: auto; border: 1px solid var(--border); }}
            code {{ font-family: monospace; }}
        </style>
    </head>
    <body class="dark">
        
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <h3 style="margin-top:0; color:var(--text)">Clear History?</h3>
                <p style="color:var(--text-secondary)">Irreversible action.</p>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal()">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete</button>
                </div>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()" style="position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:150; display:none;"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-pen-to-square"></i> New Chat
            </button>
            <div style="font-size:0.75rem; font-weight:600; color:var(--text-secondary); margin-bottom:10px;">RECENT</div>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>
                
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                
                <div id="about-info" class="about-section">
                    <strong>{APP_NAME} v{VERSION}</strong><br>
                    <small style="color:var(--text-secondary)">Dev: {OWNER_NAME}</small><br>
                    <div style="margin:10px 0;">
                        <a href="{FACEBOOK_URL}" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small>&copy; 2026 {OWNER_NAME}</small>
                </div>

                <div class="history-item" onclick="openDeleteModal()" style="color:#ef4444;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.2rem; cursor:pointer;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:700; font-size:1.2rem;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.2rem; cursor:pointer;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your smart AI companion.</div>
                    
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[0]['text']}')"><i class="{random_suggestions[0]['icon']}"></i> {random_suggestions[0]['text']}</div>
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[1]['text']}')"><i class="{random_suggestions[1]['icon']}"></i> {random_suggestions[1]['text']}</div>
                        <div class="chip" onclick="sendSuggestion('Generate a futuristic city image')"><i class="fas fa-paint-brush"></i> Generate Image</div>
                        <div class="chip" onclick="sendSuggestion('Solve: 5 + 5 * 10')"><i class="fas fa-calculator"></i> Solve Math</div>
                    </div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            let chats = JSON.parse(localStorage.getItem('flux_v12_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');

            // 🌈 Dynamic Accent Colors
            const accentColors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'];

            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
            renderHistory();

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function toggleAbout() {{
                document.getElementById('about-info').classList.toggle('show');
            }}

            function resizeInput(el) {{
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 120) + 'px';
            }}

            function toggleSidebar() {{
                sidebar.classList.toggle('closed');
                overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block';
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                const randomColor = accentColors[Math.floor(Math.random() * accentColors.length)];
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [], accent: randomColor }});
                saveData();
                renderHistory();
                
                // SHOW WELCOME SCREEN LOGIC FIXED
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                msgInput.value = '';
            }}

            function saveData() {{ localStorage.setItem('flux_v12_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerText = chat.title || 'New Conversation';
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;

                // Set Accent Color
                document.documentElement.style.setProperty('--chat-accent', chat.accent || 'var(--accent)');

                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none'; // Hide welcome on load

                if (chat.messages.length === 0) {{
                     // If empty chat, show welcome
                     chatBox.appendChild(welcomeScreen);
                     welcomeScreen.style.display = 'flex';
                }} else {{
                    chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                }}
                
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                
                // HTML structure for alignment
                wrapper.innerHTML = `
                    ${{avatar}}
                    <div class="bubble-container">
                        ${{name}}
                        <div class="bubble">${{marked.parse(text)}}</div>
                    </div>
                `;
                
                chatBox.appendChild(wrapper);
                if(!isUser) hljs.highlightAll();
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
                    
                    // Streaming Bubble
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

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Error connecting to server.", false);
                }}
            }}

            function openDeleteModal() {{ deleteModal.style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal() {{ deleteModal.style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v12_history'); location.reload(); }}
            
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
    
    # 🧠 BRAIN RESTORED TO "CONCISE & SMART" 🧠
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a smart, friendly, and concise AI assistant created by {OWNER_NAME}.
        
        RULES:
        1. BE CONCISE: Keep answers short (1-3 sentences) unless asked for details. Don't write essays for "Hi".
        2. TONE: Warm, human-like, helpful.
        3. FORMATTING: Use bolding and lists where helpful.
        4. IMAGES: If user asks for image, start with "🎨 Generating image..." then blank line then: ![Img](https://image.pollinations.ai/prompt/{{english_prompt}})
        
        Current Time: {ctx['time_local']}
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