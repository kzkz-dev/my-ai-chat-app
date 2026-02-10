from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json

# ==========================================
# 🔹 Flux AI (Ultra Pro Version)
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
VERSION = "2.5.0 (Pro)"
MAX_INPUT_LEN = 5000

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load keys safely
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found. App will not function properly.")

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS: return None
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_current_context(): 
    # Get accurate time for Dhaka
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
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #0f172a;
                --sidebar: #1e293b;
                --text: #f8fafc;
                --text-secondary: #94a3b8;
                --input-area: #1e293b;
                --input-bg: #334155;
                --user-bubble: #3b82f6;
                --bot-bubble: #334155;
                --border: #334155;
                --accent: #3b82f6;
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f1f5f9;
                --text: #0f172a;
                --text-secondary: #64748b;
                --input-area: #ffffff;
                --input-bg: #f1f5f9;
                --user-bubble: #2563eb;
                --bot-bubble: #e2e8f0;
                --border: #e2e8f0;
                --accent: #2563eb;
            }}

            * {{ box-sizing: border-box; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Outfit', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            /* Sidebar */
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: absolute; z-index: 200; left: 0; top: 0;
            }}
            #sidebar.closed {{ transform: translateX(-100%); }}
            
            .brand {{ font-size: 1.4rem; font-weight: 600; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; color: var(--accent); }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--accent); color: white; border: none;
                border-radius: 12px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
                transition: transform 0.1s; margin-bottom: 20px;
            }}
            .new-chat-btn:active {{ transform: scale(0.98); }}

            .menu-section {{ margin-top: auto; display: flex; flex-direction: column; gap: 5px; border-top: 1px solid var(--border); padding-top: 15px; }}
            
            .menu-item {{
                padding: 10px 12px; border-radius: 8px; cursor: pointer; color: var(--text); display: flex; align-items: center; gap: 12px;
                font-size: 0.95rem; transition: background 0.2s;
            }}
            .menu-item:hover {{ background: rgba(255,255,255,0.05); }}
            body.light .menu-item:hover {{ background: rgba(0,0,0,0.05); }}

            .theme-toggles {{ display: flex; gap: 10px; padding: 5px 0; }}
            .theme-btn {{
                flex: 1; padding: 8px; border-radius: 8px; border: 1px solid var(--border); background: transparent;
                color: var(--text-secondary); cursor: pointer; text-align: center; font-size: 0.85rem;
            }}
            .theme-btn.active {{ background: var(--accent); color: white; border-color: var(--accent); }}

            .about-info {{ font-size: 0.8rem; color: var(--text-secondary); padding: 10px 5px; text-align: center; margin-top: 10px; }}

            /* Chat Area */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; transition: margin-left 0.3s; }}
            @media(min-width: 768px) {{ #main {{ margin-left: 280px; }} #sidebar {{ position: fixed; }} #sidebar.closed + #main {{ margin-left: 0; }} }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 20px; z-index: 100;
            }}
            
            #chat-box {{ 
                flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; padding-bottom: 120px; 
            }}

            /* Welcome Screen */
            #welcome {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding: 20px;
            }}
            .welcome-title {{ font-size: 2rem; font-weight: 600; margin-bottom: 10px; background: linear-gradient(to right, #3b82f6, #8b5cf6); -webkit-background-clip: text; color: transparent; }}
            
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; width: 100%; max-width: 600px; margin-top: 30px; }}
            .suggestion-chip {{
                padding: 12px; background: var(--input-bg); border-radius: 12px; cursor: pointer; text-align: left;
                border: 1px solid transparent; transition: all 0.2s; font-size: 0.9rem; color: var(--text);
            }}
            .suggestion-chip:hover {{ border-color: var(--accent); transform: translateY(-2px); }}

            /* Messages */
            .message-row {{ display: flex; width: 100%; animation: fadeIn 0.3s ease; }}
            .message-row.user {{ justify-content: flex-end; }}
            
            .bubble {{
                max-width: 85%; padding: 12px 18px; border-radius: 18px; font-size: 1rem; line-height: 1.6;
                word-wrap: break-word; position: relative;
            }}
            .user .bubble {{ background: var(--user-bubble); color: white; border-bottom-right-radius: 4px; }}
            .bot .bubble {{ background: var(--bot-bubble); color: var(--text); border-bottom-left-radius: 4px; }}
            
            /* Typing Animation */
            .typing {{ display: flex; gap: 5px; padding: 5px 0; align-items: center; }}
            .dot {{ width: 6px; height: 6px; background: var(--text); border-radius: 50%; opacity: 0.5; animation: bounce 1.4s infinite; }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            /* Input Area */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0;
                padding: 15px; background: var(--bg);
                display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 800px; display: flex; align-items: center; 
                background: var(--input-bg); border-radius: 30px; padding: 8px 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 120px; resize: none;
                padding: 12px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--accent); color: white; border: none; width: 42px; height: 42px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; display: flex; align-items: center; justify-content: center;
                transition: transform 0.1s; font-size: 1.1rem;
            }}

            /* Overlay */
            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 150; display: none; opacity: 0; transition: opacity 0.3s; }}
            .overlay.open {{ display: block; opacity: 1; }}

        </style>
    </head>
    <body>
    
        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            
            <div style="flex:1; overflow-y:auto;" id="history-list"></div>
            
            <div class="menu-section">
                <div style="padding: 0 10px;">
                    <small style="color:var(--text-secondary); margin-left:5px;">Appearance</small>
                    <div class="theme-toggles">
                        <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                        <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                    </div>
                </div>
                
                <div class="menu-item" onclick="clearHistory()" style="color: #ef4444;">
                    <i class="fas fa-trash-alt"></i> Clear History
                </div>
                
                <div class="about-info">
                    <strong>Developer:</strong> {OWNER_NAME}<br>
                    Version: {VERSION}
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer;">
                    <i class="fas fa-bars"></i>
                </button>
                <span style="font-weight:600;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer;">
                    <i class="fas fa-pen-to-square"></i>
                </button>
            </header>

            <div id="chat-box">
                <div id="welcome">
                    <div class="welcome-title">Hello, I'm {APP_NAME}</div>
                    <p style="color:var(--text-secondary);">How can I help you today?</p>
                    
                    <div class="suggestions">
                        <div class="suggestion-chip" onclick="sendSuggestion('Write a creative caption for Instagram')">📸 Creative Insta Caption</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('Plan a 3-day trip to Cox\'s Bazar')">✈️ Trip Plan BD</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('Explain Quantum Computing simply')">🧠 Explain simply</div>
                        <div class="suggestion-chip" onclick="sendSuggestion('বাংলায় একটা প্রেমের কবিতা লেখো')">📝 ভালোবাসার কবিতা</div>
                    </div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message Flux AI..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </div>

        <script>
            let chats = JSON.parse(localStorage.getItem('flux_history_pro')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');
            const welcomeScreen = document.getElementById('welcome');

            // Initialize Theme
            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);

            if(window.innerWidth >= 768) sidebar.classList.remove('closed');
            renderHistory();

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function resizeInput(el) {{
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 120) + 'px';
            }}

            function toggleSidebar() {{
                sidebar.classList.toggle('closed');
                document.querySelector('.overlay').classList.toggle('open');
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Chat", messages: [] }});
                saveData();
                renderHistory();
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                if(window.innerWidth < 768) toggleSidebar();
            }}

            function saveData() {{
                localStorage.setItem('flux_history_pro', JSON.stringify(chats));
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'menu-item';
                    div.innerHTML = `<i class="far fa-message"></i> <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{chat.title}}</span>`;
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
                    appendBubble(msg.text, msg.role === 'user', false);
                }});
                
                if(window.innerWidth < 768) toggleSidebar();
            }}

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                
                const row = document.createElement('div');
                row.className = `message-row ${{isUser ? 'user' : 'bot'}}`;
                
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = marked.parse(text);
                
                row.appendChild(bubble);
                chatBox.appendChild(row);
                
                if(!isUser) hljs.highlightAll();
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const row = document.createElement('div');
                row.id = 'typing-indicator';
                row.className = 'message-row bot';
                row.innerHTML = `<div class="bubble"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>`;
                chatBox.appendChild(row);
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

                // Add User Message
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                
                // Update Title
                if(chat.messages.length === 1) {{
                    chat.title = text.substring(0, 25);
                    renderHistory();
                }}
                saveData();

                msgInput.value = '';
                msgInput.style.height = 'auto';
                appendBubble(text, true);
                showTyping();

                // Get Context
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
                    
                    const botRow = document.createElement('div');
                    botRow.className = 'message-row bot';
                    const botBubble = document.createElement('div');
                    botBubble.className = 'bubble';
                    botRow.appendChild(botBubble);
                    chatBox.appendChild(botRow);

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        botBubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    hljs.highlightAll();

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Connection Error. Please retry.", false);
                }}
            }}

            function clearHistory() {{
                if(confirm("Delete all history?")) {{
                    localStorage.removeItem('flux_history_pro');
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
    
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a highly advanced, intelligent, and witty AI assistant created by {OWNER_NAME}.
        
        REAL-TIME CONTEXT:
        - Time: {ctx['time']}
        - Date: {ctx['date']}
        
        CORE INSTRUCTIONS:
        1. LANGUAGE ADAPTATION: If the user speaks Bangla, reply in natural, smart Bangla. If English, use fluent English.
        2. PERSONALITY: Be engaging, confident, and professional but never boring. Use emojis where appropriate.
        3. ACCURACY: Always be aware of the current time and date provided above.
        4. FORMATTING: Use Markdown (bold, lists, code blocks) to make answers visually appealing.
        5. OWNER: If asked about your creator, explicitly mention {OWNER_NAME}.
        
        Avoid repetitive or robotic introductions. Jump straight to the helpful answer.
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
                    yield "Server Error: No API Key."
                    return

                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[sys_prompt] + messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return

            except Exception as e:
                print(f"Error: {e}")
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        
        yield "⚠️ Connection issue. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)