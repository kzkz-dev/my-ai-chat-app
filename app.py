from flask import Flask, request, Response, session, jsonify
from groq import Groq
import os
import uuid
import time
import random
from datetime import datetime
import pytz
import json

# ==========================================
# 🔹 Flux AI (Fixed & Optimized)
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
MAX_INPUT_LEN = 5000  # Increased slightly
# ==========================================

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load keys safely
GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]

# 🛠️ FIX 1: Initialize global variable
current_key_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found. App will not function properly.")

def get_groq_client():
    """Get client using the current active key."""
    global current_key_index
    if not GROQ_KEYS: return None
    # Rotate key index ensures we don't stick to a bad key indefinitely
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_time(): 
    try:
        return datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%I:%M %p")
    except:
        return datetime.now().strftime("%I:%M %p")

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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #111827;
                --sidebar: #1f2937;
                --header: #1f2937;
                --text: #f9fafb;
                --input-area: #1f2937;
                --input-bg: #374151;
                --user-bubble: #6366f1;
                --bot-bubble: #374151;
                --border: #374151;
            }}
            body.light {{
                --bg: #f3f4f6;
                --sidebar: #ffffff;
                --header: #ffffff;
                --text: #1f2937;
                --input-area: #ffffff;
                --input-bg: #e5e7eb;
                --user-bubble: #4f46e5;
                --bot-bubble: #ffffff;
                --border: #d1d5db;
            }}

            * {{ box-sizing: border-box; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            /* Sidebar */
            #sidebar {{
                width: 260px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 15px; border-right: 1px solid var(--border); transition: transform 0.3s ease;
                position: absolute; z-index: 200; left: 0; top: 0;
            }}
            #sidebar.closed {{ transform: translateX(-100%); }}
            
            .new-chat {{
                padding: 12px; border: 1px dashed var(--border); border-radius: 8px; cursor: pointer;
                text-align: center; margin-bottom: 20px; font-weight: 600; transition: 0.2s;
            }}
            .new-chat:hover {{ background: rgba(255,255,255,0.05); border-color: var(--user-bubble); }}
            
            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }}
            .history-item {{
                padding: 10px; border-radius: 6px; cursor: pointer; white-space: nowrap; overflow: hidden;
                text-overflow: ellipsis; font-size: 0.9rem; background: rgba(255,255,255,0.03);
                transition: background 0.2s;
            }}
            .history-item:hover {{ background: rgba(255,255,255,0.1); }}

            /* Overlay for mobile */
            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
            .overlay.open {{ display: block; }}

            /* Main Layout */
            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; transition: margin-left 0.3s; }}
            @media(min-width: 768px) {{ #main {{ margin-left: 260px; }} #sidebar {{ position: fixed; }} #sidebar.closed + #main {{ margin-left: 0; }} }}

            /* Header */
            header {{
                height: 60px; background: var(--header); display: flex; align-items: center; justify-content: space-between;
                padding: 0 20px; border-bottom: 1px solid var(--border); z-index: 100;
            }}
            .menu-btn {{ background: none; border: none; color: var(--text); font-size: 1.2rem; cursor: pointer; }}

            /* Chat Area */
            #chat-box {{ 
                flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 100px; 
                scroll-behavior: smooth;
            }}
            
            .message-row {{ display: flex; width: 100%; }}
            .message-row.user {{ justify-content: flex-end; }}
            .message-row.bot {{ justify-content: flex-start; }}
            
            .bubble {{
                max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 0.95rem; line-height: 1.5;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1); word-wrap: break-word; position: relative;
            }}
            
            .user .bubble {{ background: var(--user-bubble); color: white; border-bottom-right-radius: 4px; }}
            .bot .bubble {{ background: var(--bot-bubble); color: var(--text); border-bottom-left-radius: 4px; }}
            body.light .bot .bubble {{ color: #1f2937; }}

            /* Code Blocks */
            pre {{ position: relative; background: #0d1117; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; }}
            code {{ font-family: 'Consolas', monospace; font-size: 0.9em; }}
            
            .copy-btn {{
                position: absolute; top: 5px; right: 5px; background: rgba(255,255,255,0.1);
                border: none; color: #fff; padding: 4px 8px; border-radius: 4px;
                font-size: 0.75rem; cursor: pointer; opacity: 0.7; transition: 0.2s;
            }}
            .copy-btn:hover {{ opacity: 1; background: rgba(255,255,255,0.2); }}

            /* Typing Animation */
            .typing {{ display: flex; gap: 4px; padding: 5px 0; }}
            .dot {{ width: 8px; height: 8px; background: currentColor; border-radius: 50%; opacity: 0.5; animation: bounce 1.4s infinite; }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes bounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}

            /* Input Area */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0;
                padding: 15px; background: var(--input-area); border-top: 1px solid var(--border);
                display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 800px; display: flex; align-items: center; 
                background: var(--input-bg); border-radius: 25px; padding: 5px 15px;
                border: 1px solid transparent; transition: border-color 0.2s;
            }}
            .input-box:focus-within {{ border-color: var(--user-bubble); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 120px; resize: none;
                padding: 10px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--user-bubble); color: white; border: none; width: 40px; height: 40px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; display: flex; align-items: center; justify-content: center;
                transition: transform 0.1s;
            }}
            .send-btn:active {{ transform: scale(0.95); }}
            
            .bubble p {{ margin: 0 0 10px 0; }}
            .bubble p:last-child {{ margin: 0; }}
            .bubble ul, .bubble ol {{ padding-left: 20px; margin: 5px 0; }}
        </style>
    </head>
    <body class="dark">
    
        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="new-chat" onclick="startNewChat()">+ New Chat</div>
            <div class="history-list" id="history-list"></div>
            
            <div style="margin-top: auto; border-top: 1px solid var(--border); padding-top: 10px;">
                <div style="padding: 10px; cursor: pointer; display: flex; align-items: center; gap: 10px;" onclick="document.body.classList.toggle('light')">
                    <i class="fas fa-adjust"></i> Toggle Theme
                </div>
                <div style="padding: 10px; cursor: pointer; color: #ef4444; display: flex; align-items: center; gap: 10px;" onclick="clearHistory()">
                    <i class="fas fa-trash"></i> Clear History
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button class="menu-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
                <span style="font-weight: 600; font-size: 1.1rem; display:flex; align-items:center; gap:8px;">
                    <i class="fas fa-bolt" style="color: var(--user-bubble)"></i> {APP_NAME}
                </span>
                <button class="menu-btn" onclick="startNewChat()"><i class="fas fa-edit"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" style="text-align: center; margin-top: 30vh; opacity: 0.6;">
                    <h1>Welcome to {APP_NAME}</h1>
                    <p>Powered by Advanced AI • Owner: {OWNER_NAME}</p>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Type a message..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </div>

        <script>
            let chats = JSON.parse(localStorage.getItem('flux_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');

            if(window.innerWidth >= 768) sidebar.classList.remove('closed');
            renderHistory();

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
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData();
                renderHistory();
                chatBox.innerHTML = '';
                document.getElementById('welcome').style.display = 'block';
                if(window.innerWidth < 768) toggleSidebar();
            }}

            function saveData() {{
                localStorage.setItem('flux_history', JSON.stringify(chats));
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<i class="far fa-comment-dots"></i> ${{chat.title}}`;
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;

                chatBox.innerHTML = '';
                document.getElementById('welcome').style.display = 'none';
                
                chat.messages.forEach(msg => {{
                    appendBubble(msg.text, msg.role === 'user');
                }});
                
                if(window.innerWidth < 768) toggleSidebar();
            }}

            function addCopyButtons(element) {{
                element.querySelectorAll('pre').forEach(block => {{
                    if(block.querySelector('.copy-btn')) return;
                    
                    const btn = document.createElement('button');
                    btn.className = 'copy-btn';
                    btn.innerText = 'Copy';
                    btn.onclick = () => {{
                        const code = block.querySelector('code').innerText;
                        navigator.clipboard.writeText(code);
                        btn.innerText = 'Copied!';
                        setTimeout(() => btn.innerText = 'Copy', 2000);
                    }};
                    block.appendChild(btn);
                }});
            }}

            function appendBubble(text, isUser) {{
                document.getElementById('welcome').style.display = 'none';
                const row = document.createElement('div');
                row.className = `message-row ${{isUser ? 'user' : 'bot'}}`;
                
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = marked.parse(text);
                
                row.appendChild(bubble);
                chatBox.appendChild(row);
                
                if(!isUser) {{
                    hljs.highlightAll();
                    addCopyButtons(bubble);
                }}
                
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(!currentChatId) startNewChat();

                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                
                if(chat.messages.length === 1) {{
                    chat.title = text.substring(0, 30) + (text.length > 30 ? '...' : '');
                    renderHistory();
                }}
                saveData();

                msgInput.value = '';
                msgInput.style.height = 'auto';
                appendBubble(text, true);

                const typingRow = document.createElement('div');
                typingRow.id = 'typing';
                typingRow.className = 'message-row bot';
                typingRow.innerHTML = `<div class="bubble"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>`;
                chatBox.appendChild(typingRow);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});

                const context = chat.messages.slice(-12).map(m => ({{ role: m.role, content: m.text }}));

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    if(!res.ok) throw new Error("Network response was not ok");

                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    document.getElementById('typing').remove();
                    
                    const botRow = document.createElement('div');
                    botRow.className = 'message-row bot';
                    const botBubble = document.createElement('div');
                    botBubble.className = 'bubble';
                    botRow.appendChild(botBubble);
                    chatBox.appendChild(botRow);

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        const chunk = decoder.decode(value);
                        botResp += chunk;
                        botBubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
                    }}
                    
                    hljs.highlightAll();
                    addCopyButtons(botBubble);
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();

                }} catch(e) {{
                    if(document.getElementById('typing')) document.getElementById('typing').remove();
                    appendBubble("⚠️ Connection Error. Please retry.", false);
                    console.error(e);
                }}
            }}

            function clearHistory() {{
                if(confirm("Are you sure you want to delete all chat history?")) {{
                    localStorage.removeItem('flux_history');
                    location.reload();
                }}
            }}

            // 🛠️ FIX 2: Correct Event Listener
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
    # 1. Input Validation
    data = request.json
    messages = data.get("messages", [])
    
    # 2. Enhanced System Prompt
    sys = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a helpful and intelligent AI assistant.
        Owner/Creator: {OWNER_NAME}.
        Current Time: {get_time()}.
        
        GUIDELINES:
        - If asked "Who is your owner?", reply strictly: "My owner is {OWNER_NAME}."
        - Respond in the same language as the user (Bangla/English).
        - Use Markdown for code, lists, and bold text.
        - Be concise, professional, and friendly.
        """
    }
    
    # 3. Robust Retry Logic
    def generate():
        global current_key_index
        attempts = 0
        max_retries = len(GROQ_KEYS) + 1 if GROQ_KEYS else 1
        
        while attempts < max_retries:
            try:
                client = get_groq_client()
                if not client:
                    yield "Server Configuration Error: No API Keys."
                    return

                # Check payload validity before sending
                full_messages = [sys] + messages
                
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=full_messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=2048
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return # Success

            except Exception as e:
                print(f"Key index {current_key_index} failed: {e}")
                # Rotate key
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        
        yield "⚠️ System Overload or API Error. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
