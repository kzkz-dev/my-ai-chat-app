from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json

# ==========================================
# 🔹 Flux AI (Ultimate Brain & Premium UI) 🧠💎
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"
VERSION = "5.0.0 (Ultimate Edition)"

# ⚠️ আপনার আসল ফেসবুক এবং ওয়েবসাইটের লিঙ্ক দিন ⚠️
FACEBOOK_URL = "https://www.facebook.com/your.profile" 
WEBSITE_URL = "https://your-website.com"      

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
    tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(tz)
    return {
        "time": now.strftime("%I:%M %p"),
        "date": now.strftime("%d %B, %Y (%A)"),
        "year": now.year
    }

@app.route("/")
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME}</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
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
                --accent: #3b82f6;
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
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
                --bot-icon: linear-gradient(135deg, #2563eb, #7c3aed);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            ::-webkit-scrollbar {{ width: 5px; }}
            ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}
            
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 5px 0 15px rgba(0,0,0,0.2);
            }}
            #sidebar.closed {{ transform: translateX(-105%); }}
            
            .brand {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); letter-spacing: -0.5px; user-select: none; }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; font-size: 1.6rem; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: transparent; color: var(--text); border: 1px solid var(--border);
                border-radius: 10px; font-weight: 500; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 10px;
                transition: 0.2s; margin-bottom: 20px;
            }}
            .new-chat-btn:active {{ transform: scale(0.97); background: var(--input-bg); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; padding-right: 5px; margin-bottom: 10px; }}
            .history-item {{
                padding: 10px 12px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 12px;
                font-size: 0.9rem; transition: 0.2s; user-select: none;
            }}
            .history-item:active {{ background: var(--input-bg); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 4px; border-radius: 8px; }}
            .theme-btn {{ flex: 1; padding: 6px; border-radius: 6px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: 0.2s; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}

            .about-section {{ 
                display: none; background: var(--input-bg); padding: 15px; border-radius: 12px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--border);
            }}
            .about-section.show {{ display: block; animation: fadeIn 0.3s; }}
            .about-link {{ color: var(--text); font-size: 1.2rem; text-decoration: none; margin: 0 10px; transition: color 0.2s; }}
            .about-link:hover {{ color: var(--accent); }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 15px; z-index: 100; background: rgba(11, 15, 25, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid rgba(255,255,255,0.05); position: absolute; top: 0; left: 0; right: 0;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.8); border-bottom: 1px solid rgba(0,0,0,0.05); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            #chat-box {{ 
                flex: 1; overflow-y: auto; padding: 80px 20px 140px 20px; 
                display: flex; flex-direction: column; gap: 25px; scroll-behavior: smooth;
            }}

            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 80%; text-align: center; animation: fadeIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
            }}
            .icon-wrapper {{ width: 60px; height: 60px; background: var(--bot-icon); border-radius: 18px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; color: white; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3); }}
            
            .welcome-title {{ font-size: 2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.5px; }}
            
            .suggestions {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; width: 100%; max-width: 500px; margin-top: 35px; }}
            .chip {{
                padding: 14px 16px; background: transparent; border-radius: 14px; cursor: pointer; text-align: left;
                border: 1px solid var(--border); transition: all 0.2s; font-size: 0.9rem; color: var(--text-secondary);
            }}
            .chip:active {{ background: var(--input-bg); border-color: var(--accent); }}
            .chip i {{ color: var(--text); margin-bottom: 8px; display: block; font-size: 1.1rem; opacity: 0.8; }}

            .message-wrapper {{ display: flex; gap: 15px; width: 100%; animation: slideUp 0.3s ease; max-width: 800px; margin: 0 auto; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }}
            .bot-avatar {{ background: var(--bot-icon); color: white; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2); }}
            .user-avatar {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 85%; }}
            .sender-name {{ font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; margin-top: 2px; }}
            .user .sender-name {{ text-align: right; display: none; }} 
            
            .bubble {{ font-size: 1rem; line-height: 1.6; word-wrap: break-word; }}
            .bot .bubble {{ color: var(--text); padding: 0; margin-top: 5px; }}
            .user .bubble {{ background: var(--input-bg); color: var(--text); padding: 12px 16px; border-radius: 18px 4px 18px 18px; }}

            .typing {{ display: flex; gap: 5px; align-items: center; padding: 10px 0; }}
            .dot {{ width: 6px; height: 6px; background: var(--text-secondary); border-radius: 50%; animation: pulse 1.4s infinite; }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}

            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 10px 20px 20px 20px;
                background: linear-gradient(to top, var(--bg) 70%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 750px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 20px; padding: 6px 6px 6px 16px;
                border: 1px solid var(--border); transition: 0.3s; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .input-box:focus-within {{ border-color: rgba(59, 130, 246, 0.5); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px; resize: none;
                padding: 12px 0; font-family: inherit; line-height: 1.5;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 38px; height: 38px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; display: flex; align-items: center; justify-content: center;
                transition: transform 0.1s; font-size: 1rem; flex-shrink: 0; margin-bottom: 4px;
            }}
            .send-btn:active {{ transform: scale(0.9); }}
            .send-btn.active-typing {{ background: var(--accent); color: white; }}

            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 150; display: none; backdrop-filter: blur(3px); -webkit-backdrop-filter: blur(3px); }}
            .overlay.open {{ display: block; animation: fadeIn 0.2s; }}

            pre {{ border-radius: 12px; padding: 15px; background: #161b22 !important; border: 1px solid rgba(255,255,255,0.1); margin: 12px 0; font-size: 0.9em; overflow-x: auto; }}
            p {{ margin-top: 0; margin-bottom: 12px; }}
            p:last-child {{ margin-bottom: 0; }}

            @keyframes pulse {{ 0%, 100% {{ transform: scale(0.8); opacity: 0.5; }} 50% {{ transform: scale(1.2); opacity: 1; }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
    </head>
    <body class="dark">
    
        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-pen-to-square"></i> New chat
            </button>
            
            <div style="font-size:0.75rem; font-weight:600; color:var(--text-secondary); margin-bottom:10px; padding-left:5px;">Recent</div>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>

                <div class="history-item" onclick="toggleAbout()" style="color: var(--text); justify-content: flex-start; margin-top:5px;">
                    <i class="fas fa-info-circle"></i> App Info
                </div>
                
                <div id="about-info" class="about-section">
                    <strong style="color:var(--text); font-size: 1.1rem;">{APP_NAME}</strong><br>
                    <small style="color: var(--accent);">Version {VERSION}</small><br>
                    <div style="margin: 12px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="color:var(--text-secondary);">Developer: {OWNER_NAME}</small><br>
                </div>

                <div class="history-item" onclick="clearHistory()" style="color: #ef4444; justify-content: flex-start; margin-top:5px;">
                    <i class="fas fa-trash-alt"></i> Delete history
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px;">
                    <i class="fas fa-bars"></i>
                </button>
                <span style="font-weight:600; font-size:1.1rem; letter-spacing: -0.3px;">{APP_NAME} <sup style="font-size:0.6rem; color:var(--accent);">PRO</sup></span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px;">
                    <i class="fas fa-pen-to-square"></i>
                </button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">How can I help you today?</div>
                    
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('Tell me a very funny tech joke')"><i class="fas fa-laugh-squint"></i> Tell a Joke</div>
                        <div class="chip" onclick="sendSuggestion('Give me a creative caption for my new DP')"><i class="fas fa-camera-retro"></i> Creative Caption</div>
                        <div class="chip" onclick="sendSuggestion('Explain Quantum Physics like I am 5')"><i class="fas fa-brain"></i> Explain Simply</div>
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
            let chats = JSON.parse(localStorage.getItem('flux_ultimate_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');
            const welcomeScreen = document.getElementById('welcome');
            const sendBtn = document.getElementById('send-btn-icon');

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
                if(el.value.trim() !== "") {{
                    sendBtn.classList.add('active-typing');
                }} else {{
                    sendBtn.classList.remove('active-typing');
                }}
            }}

            function toggleSidebar() {{
                sidebar.classList.toggle('closed');
                document.querySelector('.overlay').classList.toggle('open');
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New conversation", messages: [] }});
                saveData();
                renderHistory();
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                msgInput.value = '';
                resizeInput(msgInput);
                sidebar.classList.add('closed');
                document.querySelector('.overlay').classList.remove('open');
            }}

            function saveData() {{
                localStorage.setItem('flux_ultimate_history', JSON.stringify(chats));
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{(chat.title || 'New conversation').substring(0, 25)}}</span>`;
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;

                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none';
                
                chat.messages.forEach(msg => {{
                    appendBubble(msg.text, msg.role === 'user');
                }});
                
                sidebar.classList.add('closed');
                document.querySelector('.overlay').classList.remove('open');
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                
                const avatar = document.createElement('div');
                avatar.className = `avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}`;
                avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';
                
                const bubbleContainer = document.createElement('div');
                bubbleContainer.className = 'bubble-container';
                
                const senderName = document.createElement('div');
                senderName.className = 'sender-name';
                senderName.innerText = isUser ? 'You' : '{APP_NAME}';
                
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = marked.parse(text);
                
                bubbleContainer.appendChild(senderName);
                bubbleContainer.appendChild(bubble);
                
                wrapper.appendChild(avatar);
                wrapper.appendChild(bubbleContainer);
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
                        <div class="bubble"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>
                    </div>
                `;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{
                const el = document.getElementById('typing-indicator');
                if(el) el.remove();
            }}

            function sendSuggestion(text) {{
                msgInput.value = text;
                sendMessage();
            }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(!currentChatId) startNewChat();

                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                
                if(chat.messages.length === 1) {{
                    chat.title = text.substring(0, 30);
                    renderHistory();
                }}
                saveData();

                msgInput.value = '';
                resizeInput(msgInput);
                appendBubble(text, true);
                showTyping();

                const context = chat.messages.slice(-15).map(m => ({{ role: m.role, content: m.text }}));

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
                    
                    const avatar = document.createElement('div');
                    avatar.className = 'avatar bot-avatar';
                    avatar.innerHTML = '<i class="fas fa-bolt"></i>';
                    
                    const bubbleContainer = document.createElement('div');
                    bubbleContainer.className = 'bubble-container';
                    
                    const senderName = document.createElement('div');
                    senderName.className = 'sender-name';
                    senderName.innerText = '{APP_NAME}';
                    
                    const bubble = document.createElement('div');
                    bubble.className = 'bubble';
                    
                    bubbleContainer.appendChild(senderName);
                    bubbleContainer.appendChild(bubble);
                    wrapper.appendChild(avatar);
                    wrapper.appendChild(bubbleContainer);
                    chatBox.appendChild(wrapper);

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    hljs.highlightAll();

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Internet connection unstable or API Error.", false);
                }}
            }}

            function clearHistory() {{
                if(confirm("Clear all conversations?")) {{
                    localStorage.removeItem('flux_ultimate_history');
                    location.reload();
                }}
            }}

            msgInput.addEventListener('keypress', e => {{
                if(e.key === 'Enter' && !e.shiftKey) {{
                    e.preventDefault();
                    sendMessage();
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    ctx = get_current_context()
    
    # 🧠 THE ULTIMATE BRAIN: Optimized for Accuracy, Wit, and Engagement 🧠
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a brilliant, witty, and highly engaging AI assistant created by {OWNER_NAME} (কাওছুর).
        
        📅 LIVE CONTEXT:
        - Date: {ctx['date']} | Time: {ctx['time']} (Bangladesh Time)
        
        🧠 CORE DIRECTIVES (Follow Strictly):
        1. SUPER INTELLIGENCE & ACCURACY: You are extremely smart. For math, coding, or complex logic, always think step-by-step internally before providing the final answer to ensure absolutely zero mistakes. 
        2. FUN & ENGAGING PERSONA: Never be boring. Talk like a highly intelligent, empathetic, and witty human. Use a conversational, lively tone. Sprinkle in relevant emojis to make the text visually appealing and fun to read.
        3. PERFECT LANGUAGE MIRRORING: If the user speaks casual Bangla (e.g., 'kemon aso'), reply in natural, friendly, and smart Bangla. If formal English, reply in highly professional English. Adapt perfectly to their vibe.
        4. NO ROBOTIC CLICHÉS: Never say "As an AI..." or "I am a large language model." You are simply {APP_NAME}, the ultimate assistant. If someone asks who made you, proudly say you were created by {OWNER_NAME}.
        5. CONCISENESS WITH IMPACT: Keep answers crisp, punchy, and direct. Don't write long boring essays unless explicitly asked for details. Use bullet points and bold text for easy reading.
        """
    }

    def generate():
        global current_key_index
        attempts = 0
        max_retries = len(GROQ_KEYS) + 1 if GROQ_KEYS else 1
        
        while attempts < max_retries:
            try:
                client = get_groq_client()
                if not client:
                    yield "⚠️ Server Configuration Error."
                    return

                # Using llama-3.3-70b for maximum reasoning and creativity
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[sys_prompt] + messages,
                    stream=True,
                    temperature=0.7, # Perfect balance of creativity and accuracy
                    max_tokens=2048
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ System overloaded. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
