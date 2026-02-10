from flask import Flask, request, Response, session
from groq import Groq
import os
import uuid
from datetime import datetime
import pytz

# ==========================================
# 🔹 Flux Professional (ChatGPT Clone Style)
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
# ==========================================

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        <title>{APP_NAME}</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Söhne:wght@300;400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #ffffff;
                --sidebar: #f9f9f9;
                --text: #0d0d0d;
                --text-secondary: #8e8ea0;
                --border: #e5e5e5;
                --input-bg: #f4f4f4;
                --user-msg-bg: #f4f4f4;
                --bot-icon: #10a37f;
            }}
            
            body.dark {{
                --bg: #343541;
                --sidebar: #202123;
                --text: #ececf1;
                --text-secondary: #c5c5d2;
                --border: #4d4d4f;
                --input-bg: #40414f;
                --user-msg-bg: #444654;
                --bot-icon: #19c37d;
            }}

            * {{ box-sizing: border-box; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: 'Söhne', 'Inter', sans-serif; height: 100vh; display: flex; 
                flex-direction: column; overflow: hidden; transition: background 0.3s;
            }}

            /* Header */
            header {{
                height: 50px; display: flex; align-items: center; justify-content: center;
                border-bottom: 1px solid var(--border); background: var(--bg); 
                position: relative; z-index: 50; font-weight: 600;
            }}
            .menu-btn {{ position: absolute; left: 15px; background: none; border: none; color: var(--text); font-size: 1.2rem; cursor: pointer; }}
            .new-chat-btn {{ position: absolute; right: 15px; background: none; border: none; color: var(--text); font-size: 1.2rem; cursor: pointer; }}

            /* Sidebar */
            #sidebar {{
                position: fixed; top: 0; left: -300px; width: 300px; height: 100%;
                background: var(--sidebar); z-index: 1000; transition: 0.3s;
                border-right: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column;
            }}
            #sidebar.open {{ left: 0; }}
            .overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 900; display: none; }}
            .overlay.open {{ display: block; }}
            
            .sidebar-link {{
                padding: 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 12px;
                color: var(--text); margin-bottom: 5px; font-size: 0.95rem; transition: 0.2s;
            }}
            .sidebar-link:hover {{ background: rgba(0,0,0,0.05); }}
            body.dark .sidebar-link:hover {{ background: rgba(255,255,255,0.05); }}

            /* Chat Area */
            #chat-container {{
                flex: 1; overflow-y: auto; padding: 20px 0 100px 0;
                display: flex; flex-direction: column; scroll-behavior: smooth;
            }}
            
            .message-row {{
                width: 100%; padding: 24px 20px; display: flex; justify-content: center;
                border-bottom: 1px solid rgba(0,0,0,0.05);
            }}
            body.dark .message-row {{ border-bottom: 1px solid rgba(0,0,0,0.1); }}
            
            .message-row.user {{ background: var(--bg); }}
            .message-row.bot {{ background: var(--bg); }} /* Clean look, no colored blocks */
            body.dark .message-row.bot {{ background: #444654; }} /* Slight contrast in dark mode */

            .content-wrapper {{
                width: 100%; max-width: 800px; display: flex; gap: 18px;
            }}
            
            .avatar {{
                width: 30px; height: 30px; border-radius: 4px; flex-shrink: 0;
                display: flex; align-items: center; justify-content: center; font-size: 1rem;
            }}
            .user-av {{ background: #7C3AED; color: white; }}
            .bot-av {{ background: var(--bot-icon); color: white; }}
            
            .text-content {{
                flex: 1; font-size: 1rem; line-height: 1.6; overflow-x: hidden;
                word-wrap: break-word; white-space: pre-wrap;
            }}
            .text-content p {{ margin-top: 0; margin-bottom: 10px; }}
            
            /* Code Blocks */
            pre {{ background: #000 !important; padding: 15px; border-radius: 6px; overflow-x: auto; color: #fff; }}
            code {{ font-family: monospace; }}

            /* Typing Indicator */
            .typing {{ display: flex; gap: 5px; align-items: center; padding-top: 5px; }}
            .dot {{ width: 8px; height: 8px; background: #9ca3af; border-radius: 50%; animation: pulse 1.5s infinite; }}
            .dot:nth-child(2) {{ animation-delay: 0.2s; }}
            .dot:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 0.5; transform: scale(0.9); }} 50% {{ opacity: 1; transform: scale(1.1); }} }}

            /* Input Area (Floating Capsule) */
            #input-area {{
                position: fixed; bottom: 0; left: 0; right: 0;
                padding: 20px; background: linear-gradient(180deg, rgba(255,255,255,0), var(--bg) 15%);
                display: flex; justify-content: center; z-index: 100;
            }}
            body.dark #input-area {{ background: linear-gradient(180deg, rgba(52,53,65,0), var(--bg) 15%); }}

            .input-box {{
                width: 100%; max-width: 800px; background: var(--input-bg);
                border: 1px solid var(--border); border-radius: 24px;
                padding: 8px 12px 8px 20px; display: flex; align-items: flex-end;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px;
                resize: none; padding: 8px 0; line-height: 1.5; font-family: inherit;
            }}
            
            .send-btn {{
                width: 32px; height: 32px; background: var(--bot-icon); color: white;
                border-radius: 50%; border: none; cursor: pointer; margin-left: 10px; margin-bottom: 4px;
                display: flex; align-items: center; justify-content: center; transition: 0.2s;
            }}
            .send-btn:disabled {{ opacity: 0.5; cursor: default; background: #ccc; }}

            /* Language Toggle in Header */
            .lang-switch {{
                font-size: 0.8rem; padding: 4px 8px; background: var(--input-bg);
                border-radius: 4px; margin-left: 10px; cursor: pointer;
            }}

        </style>
    </head>
    <body class="dark"> <div class="overlay" onclick="toggleSidebar()"></div>
        <div id="sidebar">
            <h3 style="margin-top: 0; color: var(--text-secondary); font-size: 0.8rem;">HISTORY</h3>
            <div class="sidebar-link" onclick="location.reload()"><i class="fas fa-plus"></i> New Chat</div>
            <div class="sidebar-link" onclick="toggleTheme()"><i class="fas fa-adjust"></i> Toggle Theme</div>
            <div style="margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px;">
                <div class="sidebar-link"><i class="fas fa-user-circle"></i> {APP_NAME} Pro</div>
            </div>
        </div>

        <header>
            <button class="menu-btn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
            <span>{APP_NAME} <span class="lang-switch" onclick="toggleLang()" id="lang-btn">EN</span></span>
            <button class="new-chat-btn" onclick="location.reload()"><i class="fas fa-pen-to-square"></i></button>
        </header>

        <div id="chat-container">
            <div id="empty-state" style="margin-top: 35vh; text-align: center; opacity: 0.8;">
                <div style="font-size: 3rem; margin-bottom: 10px;">⚡</div>
                <h3>How can I help you today?</h3>
            </div>
        </div>

        <div id="input-area">
            <div class="input-box">
                <textarea id="msg" placeholder="Message Flux..." rows="1" oninput="autoResize(this)"></textarea>
                <button class="send-btn" id="sendBtn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const input = document.getElementById('msg');
            const emptyState = document.getElementById('empty-state');
            let currentLang = 'en';

            function toggleSidebar() {{
                document.getElementById('sidebar').classList.toggle('open');
                document.querySelector('.overlay').classList.toggle('open');
            }}

            function toggleTheme() {{
                document.body.classList.toggle('dark');
            }}

            function toggleLang() {{
                currentLang = currentLang === 'en' ? 'bn' : 'en';
                document.getElementById('lang-btn').innerText = currentLang.toUpperCase();
            }}

            function autoResize(el) {{
                el.style.height = 'auto';
                el.style.height = el.scrollHeight + 'px';
            }}

            function appendMessage(text, isUser) {{
                if(emptyState) emptyState.style.display = 'none';

                const row = document.createElement('div');
                row.className = `message-row ${{isUser ? 'user' : 'bot'}}`;
                
                const av = isUser ? '<div class="avatar user-av"><i class="fas fa-user"></i></div>' : '<div class="avatar bot-av"><i class="fas fa-bolt"></i></div>';
                const content = isUser ? text : marked.parse(text);

                row.innerHTML = `
                    <div class="content-wrapper">
                        ${{av}}
                        <div class="text-content">${{content}}</div>
                    </div>
                `;
                chat.appendChild(row);
                window.scrollTo(0, document.body.scrollHeight);
                if(!isUser) hljs.highlightAll();
            }}

            function showTyping() {{
                const row = document.createElement('div');
                row.id = 'typing';
                row.className = 'message-row bot';
                row.innerHTML = `
                    <div class="content-wrapper">
                        <div class="avatar bot-av"><i class="fas fa-bolt"></i></div>
                        <div class="text-content typing">
                            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
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
                appendMessage(text, true);
                showTyping();

                try {{
                    const res = await fetch(`/chat?prompt=${{encodeURIComponent(text)}}&lang=${{currentLang}}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let full = '';

                    document.getElementById('typing').remove();
                    
                    const row = document.createElement('div');
                    row.className = 'message-row bot';
                    row.innerHTML = `
                        <div class="content-wrapper">
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
                        contentDiv.innerHTML = marked.parse(full);
                        window.scrollTo(0, document.body.scrollHeight);
                    }}
                    hljs.highlightAll();

                }} catch (e) {{
                    document.getElementById('typing').remove();
                    appendMessage("⚠️ Network error. Please try again.", false);
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
    
    # 🔴 OWNER LOGIC FIX
    # আমি সিস্টেম প্রম্পটটি কড়াভাবে ঠিক করেছি যাতে সে মালিকের নাম স্বীকার করে।
    sys_content = f"""
    You are {APP_NAME}. 
    Your Owner/Creator is: {OWNER_NAME}.
    
    RULES:
    1. If user asks "Who is your owner?" or "Who created you?", you MUST answer: "My owner is {OWNER_NAME}."
    2. If user speaks Bangla, reply in Bangla. If English, reply in English.
    3. Do not be robotic. Be helpful, direct, and professional like ChatGPT.
    4. Current Time: {get_time()}.
    """
    
    sys = {"role": "system", "content": sys_content}
    user_chats[uid].append({"role": "user", "content": prompt})
    user_chats[uid] = user_chats[uid][-12:] 
    
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