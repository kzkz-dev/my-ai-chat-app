from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json

# ==========================================
# 🔹 Flux AI (Ultimate Edition)
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"  # Bangla Name
VERSION = "3.0.0 (Pro)"
FACEBOOK_URL = "https://facebook.com/your-id" # আপনার ফেসবুক লিঙ্ক দিন
WEBSITE_URL = "https://your-website.com"      # আপনার ওয়েবসাইট লিঙ্ক দিন

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load keys safely
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found.")

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
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #0f172a;
                --sidebar: #1e293b;
                --text: #f8fafc;
                --text-secondary: #94a3b8;
                --input-bg: #334155;
                --user-bubble: #3b82f6;
                --bot-bubble: #334155;
                --border: #334155;
                --accent: #3b82f6;
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f8fafc;
                --text: #0f172a;
                --text-secondary: #64748b;
                --input-bg: #f1f5f9;
                --user-bubble: #2563eb;
                --bot-bubble: #e2e8f0;
                --border: #e2e8f0;
                --accent: #2563eb;
            }}

            * {{ box-sizing: border-box; outline: none; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Outfit', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            /* Sidebar */
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s ease;
                position: absolute; z-index: 200; left: 0; top: 0;
            }}
            #sidebar.closed {{ transform: translateX(-100%); }}
            
            .brand {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; color: var(--accent); }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--accent); color: white; border: none;
                border-radius: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;
                transition: 0.2s; margin-bottom: 20px;
            }}
            .new-chat-btn:hover {{ opacity: 0.9; }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }}
            .history-item {{
                padding: 10px 12px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 10px;
                font-size: 0.9rem; transition: 0.2s;
            }}
            .history-item:hover {{ background: rgba(125,125,125,0.1); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 4px; border-radius: 8px; }}
            .theme-btn {{
                flex: 1; padding: 6px; border-radius: 6px; border: none; background: transparent;
                color: var(--text-secondary); cursor: pointer; font-size: 0.8rem; font-weight: 500;
            }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); shadow: 0 2px 5px rgba(0,0,0,0.1); }}

            /* About Modal/Section */
            .about-section {{ 
                display: none; background: var(--bg); padding: 15px; border-radius: 12px; border: 1px solid var(--border);
                margin-top: 10px; font-size: 0.85rem; text-align: center;
            }}
            .about-section.show {{ display: block; animation: fadeIn 0.3s; }}
            .about-link {{ color: var(--accent); text-decoration: none; margin: 0 5px; }}
            
            /* Main Chat */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; transition: margin-left 0.3s; }}
            @media(min-width: 768px) {{ #main {{ margin-left: 280px; }} #sidebar {{ position: fixed; }} #sidebar.closed + #main {{ margin-left: 0; }} }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 20px; z-index: 100; backdrop-filter: blur(10px);
            }}

            #chat-box {{ flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; padding-bottom: 120px; }}

            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; padding: 20px;
            }}
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; width: 100%; max-width: 650px; margin-top: 40px; }}
            .chip {{
                padding: 15px; background: var(--input-bg); border-radius: 12px; cursor: pointer; text-align: left;
                border: 1px solid transparent; transition: all 0.2s; font-size: 0.9rem; color: var(--text);
            }}
            .chip:hover {{ border-color: var(--accent); transform: translateY(-3px); }}

            /* Messages */
            .message-row {{ display: flex; width: 100%; }}
            .message-row.user {{ justify-content: flex-end; }}
            
            .bubble {{
                max-width: 85%; padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6;
                position: relative; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .user .bubble {{ background: var(--user-bubble); color: white; border-bottom-right-radius: 4px; }}
            .bot .bubble {{ background: var(--bot-bubble); color: var(--text); border-bottom-left-radius: 4px; }}
            
            .typing {{ display: flex; gap: 5px; align-items: center; padding: 5px; }}
            .dot {{ width: 6px; height: 6px; background: var(--text); border-radius: 50%; opacity: 0.6; animation: bounce 1.4s infinite; }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

            /* Input */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 80%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 800px; display: flex; align-items: center; 
                background: var(--input-bg); border-radius: 30px; padding: 8px 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid var(--border);
            }}
            .input-box:focus-within {{ border-color: var(--accent); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px; resize: none;
                padding: 12px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--accent); color: white; border: none; width: 40px; height: 40px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; display: flex; align-items: center; justify-content: center;
                transition: transform 0.1s;
            }}
            .send-btn:active {{ transform: scale(0.9); }}

            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 150; display: none; }}
            .overlay.open {{ display: block; }}
        </style>
    </head>
    <body class="dark">
    
        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>
                
                <div class="history-item" onclick="toggleAbout()" style="color: var(--accent);">
                    <i class="fas fa-info-circle"></i> About {APP_NAME}
                </div>
                
                <div id="about-info" class="about-section">
                    <strong style="color:var(--text);">{APP_NAME}</strong><br>
                    <small>Version {VERSION}</small><br>
                    <div style="margin: 8px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="color:var(--text-secondary);">Owner: {OWNER_NAME}</small><br>
                    <small style="opacity:0.6;">&copy; 2026 {OWNER_NAME}</small>
                </div>

                <div class="history-item" onclick="clearHistory()" style="color: #ef4444; margin-top:5px;">
                    <i class="fas fa-trash-alt"></i> Clear History
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer;">
                    <i class="fas fa-bars"></i>
                </button>
                <span style="font-weight:600; font-size:1.1rem;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer;">
                    <i class="fas fa-pen-to-square"></i>
                </button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <h1 style="font-weight: 600; background: linear-gradient(to right, #3b82f6, #a855f7); -webkit-background-clip: text; color: transparent; margin-bottom: 5px;">
                        Hello, I'm {APP_NAME}
                    </h1>
                    <p style="color:var(--text-secondary);">Your intelligent & fun AI assistant. Ask me anything!</p>
                    
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('Write a romantic poem about rain')">📝 Romantic Poem</div>
                        <div class="chip" onclick="sendSuggestion('Plan a 3-day trip to Cox\'s Bazar')">✈️ Trip Plan BD</div>
                        <div class="chip" onclick="sendSuggestion('Explain Quantum Physics simply')">🧠 Explain Physics</div>
                        <div class="chip" onclick="sendSuggestion('Solve this math: 2x + 5 = 15')">➗ Solve Math</div>
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
            let chats = JSON.parse(localStorage.getItem('flux_v3_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');
            const welcomeScreen = document.getElementById('welcome');

            // Theme Init
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

            function toggleAbout() {{
                document.getElementById('about-info').classList.toggle('show');
            }}

            function resizeInput(el) {{
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 150) + 'px';
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
                localStorage.setItem('flux_v3_history', JSON.stringify(chats));
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<i class="far fa-message"></i> ${{(chat.title || 'New Chat').substring(0, 22)}}`;
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

                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                
                // Update title intelligently
                if(chat.messages.length === 1) {{
                    chat.title = text.substring(0, 25);
                    renderHistory();
                }}
                saveData();

                msgInput.value = '';
                msgInput.style.height = 'auto';
                appendBubble(text, true);
                showTyping();

                // Send last 15 messages for memory context
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
                    
                    // Live Streaming Effect
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
                    appendBubble("⚠️ Internet connection unstable.", false);
                }}
            }}

            function clearHistory() {{
                if(confirm("Delete all chat history permanently?")) {{
                    localStorage.removeItem('flux_v3_history');
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
    
    # 🧠 The Brain: Advanced System Prompt
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a smart, witty, and highly capable AI assistant.
        
        👑 OWNER INFO:
        - Owner Name (English): {OWNER_NAME}
        - Owner Name (Bangla): {OWNER_NAME_BN} (কাওছুর)
        - If asked about copyright, say: © 2026 {OWNER_NAME}.
        
        📅 REAL-TIME INFO:
        - Date: {ctx['date']}
        - Time: {ctx['time']}
        
        🧠 BEHAVIORAL INSTRUCTIONS (Strict):
        1. **Language Mirroring:** If user speaks English, reply in English. If Bangla, reply in Bangla.
        2. **Personality:** Be fun and engaging. Don't be robotic. Use emojis occasionally.
        3. **Conciseness:** Do NOT talk too much. Give direct answers. Do not give unsolicited advice.
        4. **Capabilities:** You can solve Math problems, write code, explain science, and help with daily life.
        5. **Memory:** Always remember the user's name if they mentioned it in the current conversation.
        
        🚫 RESTRICTIONS:
        - Never apologize excessively.
        - Do not mention you are an AI model trained by Google/Meta etc. You are {APP_NAME} by {OWNER_NAME}.
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
                    yield "Server Error: No API Keys configured."
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
        
        yield "⚠️ Flux AI is currently overloaded. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)