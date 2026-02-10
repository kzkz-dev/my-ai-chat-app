from flask import Flask, request, Response, session, jsonify
from groq import Groq
import os
import uuid
from datetime import datetime
import pytz
import json

# ==========================================
# 🔹 Flux v4.0 (Final Professional)
APP_NAME = "Flux"
# ==========================================

app = Flask(__name__)
app.secret_key = os.urandom(24)

# মেমোরি স্টোরেজ (প্রোডাকশনে ডাটাবেস ব্যবহার করা উচিত)
user_chats = {} 

GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS or GROQ_KEYS == ['']: raise ValueError("No Groq keys found!")
    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        if not key:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
            continue
        try: return Groq(api_key=key)
        except Exception: current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    raise ValueError("All keys invalid!")

def get_time(): return datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%I:%M %p")

@app.route("/")
def home():
    if 'user_id' not in session: session['user_id'] = str(uuid.uuid4())
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME} AI</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #ffffff;
                --sidebar-bg: #f9f9f9;
                --text: #374151;
                --border: #e5e7eb;
                --input-bg: #f3f4f6;
                --user-msg: #f3f4f6;
                --bot-msg: transparent;
                --accent: #10a37f;
            }}
            
            body.dark {{
                --bg: #343541;
                --sidebar-bg: #202123;
                --text: #ececf1;
                --border: #4d4d4f;
                --input-bg: #40414f;
                --user-msg: #444654;
                --bot-msg: transparent;
                --accent: #19c37d;
            }}

            * {{ box-sizing: border-box; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: 'Inter', sans-serif; height: 100vh; display: flex; 
                flex-direction: column; overflow: hidden; transition: 0.3s;
            }}

            /* Header */
            header {{
                height: 50px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 15px; border-bottom: 1px solid var(--border);
                background: var(--bg); z-index: 50;
            }}
            .header-btn {{ background: none; border: none; color: var(--text); font-size: 1.2rem; cursor: pointer; padding: 5px; }}
            .model-name {{ font-weight: 600; font-size: 1rem; cursor: pointer; display: flex; align-items: center; gap: 5px; }}
            
            /* Sidebar */
            #sidebar {{
                position: fixed; top: 0; left: -280px; width: 280px; height: 100%;
                background: var(--sidebar-bg); z-index: 1000; transition: 0.3s;
                border-right: 1px solid var(--border); display: flex; flex-direction: column;
                padding: 10px;
            }}
            #sidebar.open {{ left: 0; }}
            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 900; display: none; }}
            .overlay.open {{ display: block; }}
            
            .new-chat-btn {{
                padding: 10px; border: 1px solid var(--border); border-radius: 5px;
                background: transparent; color: var(--text); cursor: pointer;
                display: flex; align-items: center; gap: 10px; margin-bottom: 20px;
                transition: 0.2s;
            }}
            .new-chat-btn:hover {{ background: rgba(0,0,0,0.05); }}
            body.dark .new-chat-btn:hover {{ background: rgba(255,255,255,0.05); }}

            .sidebar-item {{
                padding: 10px; cursor: pointer; border-radius: 5px; display: flex; align-items: center; gap: 10px;
                color: var(--text); margin-bottom: 5px;
            }}
            .sidebar-item:hover {{ background: rgba(0,0,0,0.05); }}
            body.dark .sidebar-item:hover {{ background: rgba(255,255,255,0.05); }}

            /* Chat Area */
            #chat-container {{
                flex: 1; overflow-y: auto; padding: 0 0 120px 0;
                display: flex; flex-direction: column; align-items: center;
                scroll-behavior: smooth;
            }}
            
            .message-row {{
                width: 100%; padding: 20px; display: flex; justify-content: center;
                border-bottom: 1px solid rgba(0,0,0,0.05);
            }}
            body.dark .message-row {{ border-bottom: 1px solid rgba(255,255,255,0.05); }}
            
            .message-row.user {{ background: var(--bg); }}
            .message-row.bot {{ background: var(--bot-msg); }}
            body.dark .message-row.bot {{ background: #444654; }} /* ChatGPT style bot bg */

            .message-content {{
                width: 100%; max-width: 800px; display: flex; gap: 20px;
            }}
            
            .avatar {{
                width: 30px; height: 30px; border-radius: 2px; flex-shrink: 0;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
            }}
            .user-av {{ background: #5436DA; border-radius: 5px; color: white; font-size: 0.9rem; }}
            .bot-av {{ background: #10a37f; border-radius: 5px; color: white; font-size: 0.9rem; }}
            
            .text-content {{
                flex: 1; font-size: 1rem; line-height: 1.6; overflow-x: hidden;
                word-wrap: break-word; /* Fix text overflow */
            }}
            .text-content p {{ margin-top: 0; }}
            
            /* Typing Animation */
            .typing-indicator {{ display: flex; gap: 5px; padding: 10px 0; }}
            .dot {{ width: 6px; height: 6px; background: var(--text); border-radius: 50%; opacity: 0.6; animation: bounce 1.4s infinite ease-in-out both; }}
            .dot:nth-child(1) {{ animation-delay: -0.32s; }}
            .dot:nth-child(2) {{ animation-delay: -0.16s; }}
            @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}

            /* Input Area */
            #input-area {{
                position: fixed; bottom: 0; left: 0; right: 0;
                background: linear-gradient(180deg, rgba(255,255,255,0) 0%, var(--bg) 20%);
                padding: 20px; display: flex; justify-content: center; z-index: 40;
            }}
            body.dark #input-area {{ background: linear-gradient(180deg, rgba(52,53,65,0) 0%, var(--bg) 20%); }}

            .input-wrapper {{
                width: 100%; max-width: 800px; position: relative;
                background: var(--input-bg); border-radius: 12px;
                border: 1px solid var(--border);
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
                display: flex; align-items: flex-end; padding: 10px;
            }}
            
            textarea {{
                width: 100%; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; resize: none; max-height: 200px;
                padding: 4px; font-family: inherit; line-height: 1.5;
            }}
            
            .send-btn {{
                background: transparent; border: none; color: var(--text);
                padding: 5px 10px; cursor: pointer; transition: 0.2s;
                border-radius: 5px;
            }}
            .send-btn:hover {{ background: rgba(0,0,0,0.1); }}
            .send-btn.active {{ background: var(--accent); color: white; }}

            /* Actions */
            .msg-actions {{ margin-top: 10px; display: flex; gap: 10px; opacity: 0.7; font-size: 0.9rem; }}
            .action-icon {{ cursor: pointer; transition: 0.2s; }}
            .action-icon:hover {{ color: var(--text); opacity: 1; }}

        </style>
    </head>
    <body class="dark"> <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar">
            <button class="new-chat-btn" onclick="location.reload()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div style="flex: 1; overflow-y: auto;">
                <div style="font-size: 0.8rem; font-weight: 500; color: #666; margin-bottom: 10px; padding-left: 10px;">Preferences</div>
                <div class="sidebar-item" onclick="toggleTheme()"><i class="fas fa-sun"></i> Toggle Theme</div>
                <div class="sidebar-item" onclick="toggleLang()"><i class="fas fa-globe"></i> Language: <span id="lang-display">EN</span></div>
            </div>
            <div class="sidebar-item" style="margin-top: auto;">
                <i class="fas fa-user"></i> {APP_NAME} User
            </div>
        </div>

        <header>
            <button class="header-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
            <div class="model-name" onclick="location.reload()">
                {APP_NAME} <span style="font-size: 0.8rem; opacity: 0.5; font-weight: 400;">v4.0</span>
            </div>
            <button class="header-btn" onclick="location.reload()"><i class="fas fa-plus"></i></button>
        </header>

        <div id="chat-container">
            <div id="welcome-msg" style="margin-top: 30vh; text-align: center; opacity: 0.8;">
                <h2 style="font-size: 2rem;">{APP_NAME}</h2>
                <p>Advanced AI Assistant</p>
            </div>
        </div>

        <div id="input-area">
            <div class="input-wrapper">
                <textarea id="msg" placeholder="Send a message..." rows="1" oninput="autoResize(this)"></textarea>
                <button class="send-btn" id="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const input = document.getElementById('msg');
            const sendBtn = document.getElementById('send-btn');
            const welcome = document.getElementById('welcome-msg');
            let currentLang = 'en';

            // Auto Resize Textarea
            function autoResize(el) {{
                el.style.height = 'auto';
                el.style.height = el.scrollHeight + 'px';
                if(el.value.trim().length > 0) {{
                    sendBtn.classList.add('active');
                }} else {{
                    sendBtn.classList.remove('active');
                }}
            }}

            // Sidebar
            function toggleSidebar() {{
                document.getElementById('sidebar').classList.toggle('open');
                document.querySelector('.overlay').classList.toggle('open');
            }}

            // Theme
            function toggleTheme() {{
                document.body.classList.toggle('dark');
            }}
            
            // Language Toggle
            function toggleLang() {{
                currentLang = currentLang === 'en' ? 'bn' : 'en';
                document.getElementById('lang-display').innerText = currentLang.toUpperCase();
                alert("Language switched to " + (currentLang === 'en' ? "English" : "Bangla"));
            }}

            // TTS (Voice Output)
            function speakText(text) {{
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                // Try to match language
                if(text.match(/[\u0980-\u09FF]/)) {{
                    utterance.lang = 'bn-BD';
                }} else {{
                    utterance.lang = 'en-US';
                }}
                window.speechSynthesis.speak(utterance);
            }}

            function appendMessage(text, isUser) {{
                if(welcome) welcome.style.display = 'none';

                const row = document.createElement('div');
                row.className = `message-row ${{isUser ? 'user' : 'bot'}}`;
                
                const avatar = isUser ? '<div class="avatar user-av">U</div>' : '<div class="avatar bot-av"><i class="fas fa-bolt"></i></div>';
                
                let content = isUser ? text : marked.parse(text);
                
                // Bot Actions (Voice Icon)
                let actions = '';
                if(!isUser) {{
                    actions = `
                    <div class="msg-actions">
                        <i class="fas fa-volume-up action-icon" title="Listen" onclick="speakText(this.parentElement.previousElementSibling.innerText)"></i>
                        <i class="fas fa-copy action-icon" title="Copy" onclick="navigator.clipboard.writeText(this.parentElement.previousElementSibling.innerText)"></i>
                    </div>`;
                }}

                row.innerHTML = `
                    <div class="message-content">
                        ${{avatar}}
                        <div class="text-content">
                            ${{content}}
                            ${{actions}}
                        </div>
                    </div>
                `;
                chat.appendChild(row);
                
                if(!isUser) hljs.highlightAll();
                window.scrollTo(0, document.body.scrollHeight);
            }}

            function showTyping() {{
                const row = document.createElement('div');
                row.id = 'typing-indicator';
                row.className = 'message-row bot';
                row.innerHTML = `
                    <div class="message-content">
                        <div class="avatar bot-av"><i class="fas fa-bolt"></i></div>
                        <div class="text-content">
                            <div class="typing-indicator">
                                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                            </div>
                        </div>
                    </div>
                `;
                chat.appendChild(row);
                window.scrollTo(0, document.body.scrollHeight);
            }}

            async function sendMessage() {{
                const text = input.value.trim();
                if (!text) return;
                
                input.value = '';
                input.style.height = 'auto';
                sendBtn.classList.remove('active');
                
                appendMessage(text, true);
                showTyping();

                try {{
                    const res = await fetch(`/chat?prompt=${{encodeURIComponent(text)}}&lang=${{currentLang}}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let full = '';
                    
                    // Remove typing indicator
                    document.getElementById('typing-indicator').remove();
                    
                    // Create bot message container
                    const row = document.createElement('div');
                    row.className = 'message-row bot';
                    row.innerHTML = `
                        <div class="message-content">
                            <div class="avatar bot-av"><i class="fas fa-bolt"></i></div>
                            <div class="text-content"></div>
                        </div>
                    `;
                    chat.appendChild(row);
                    const contentDiv = row.querySelector('.text-content');

                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        full += decoder.decode(value);
                        contentDiv.innerHTML = marked.parse(full) + `
                            <div class="msg-actions">
                                <i class="fas fa-volume-up action-icon" onclick="speakText(this.parentElement.previousElementSibling.innerText)"></i>
                                <i class="fas fa-copy action-icon" onclick="navigator.clipboard.writeText(this.parentElement.previousElementSibling.innerText)"></i>
                            </div>`;
                        window.scrollTo(0, document.body.scrollHeight);
                    }}
                    hljs.highlightAll();
                    
                }} catch (e) {{
                    document.getElementById('typing-indicator').remove();
                    appendMessage("⚠️ Network Error. Please try again.", false);
                }}
            }}
            
            input.addEventListener('keydown', e => {{
                if(e.key === 'Enter' && !e.shiftKey) {{
                    e.preventDefault();
                    sendMessage();
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    lang = request.args.get("lang", "en")
    
    if not prompt: return "No prompt", 400
    
    if 'user_id' not in session: session['user_id'] = str(uuid.uuid4())
    uid = session['user_id']
    if uid not in user_chats: user_chats[uid] = []
    
    # System Instruction
    lang_instr = "Reply in fluent English." if lang == 'en' else "Reply in natural Bangla."
    
    sys = {
        "role": "system", 
        "content": f"""
        You are {APP_NAME}.
        Time: {get_time()}.
        
        INSTRUCTIONS:
        1. {lang_instr}
        2. Be smart, professional, and concise.
        3. Use Markdown for formatting.
        4. No images. No extra talk.
        """
    }
    
    user_chats[uid].append({"role": "user", "content": prompt})
    user_chats[uid] = user_chats[uid][-15:] 
    
    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[sys] + user_chats[uid],
                stream=True,
                temperature=0.7
            )
            resp = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    c = chunk.choices[0].delta.content
                    resp += c
                    yield c
            user_chats[uid].append({"role": "assistant", "content": resp})
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)