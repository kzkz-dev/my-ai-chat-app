from flask import Flask, request, Response, session
from groq import Groq
import os
import uuid
from datetime import datetime
import pytz

# ==========================================
# 🔹 অ্যাপের কনফিগারেশন
APP_NAME = "Flux"
OWNER_NAME = "KAWCHUR"
# ==========================================

app = Flask(__name__)
app.secret_key = os.urandom(24)

# মেমোরি স্টোরেজ
user_chats = {}

# Groq Keys লোড করা
GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS or GROQ_KEYS == ['']:
        raise ValueError("No Groq keys found!")
    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        if not key:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
            continue
        try:
            return Groq(api_key=key)
        except Exception:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    raise ValueError("All keys invalid!")

def get_time():
    return datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%I:%M %p")

def get_date():
    return datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%d %B, %Y")

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
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --primary: #6366f1;
                --primary-dark: #4f46e5;
                --gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                --bg: #ffffff;
                --sidebar: #f8fafc;
                --text: #0f172a;
                --msg-bot: #f1f5f9;
                --msg-user: #6366f1;
                --text-user: #ffffff;
                --border: #e2e8f0;
            }}
            
            body.dark {{
                --bg: #0f172a;
                --sidebar: #1e293b;
                --text: #f8fafc;
                --msg-bot: #1e293b;
                --msg-user: #6366f1;
                --border: #334155;
            }}

            * {{ box-sizing: border-box; }}
            body {{ 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: 'Outfit', sans-serif; height: 100vh; display: flex; 
                flex-direction: column; overflow: hidden; transition: 0.3s;
            }}
            
            /* Header */
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 15px; border-bottom: 1px solid var(--border);
                background: var(--bg); z-index: 50;
            }}
            
            .brand {{ 
                font-size: 1.4rem; font-weight: 700; 
                background: var(--gradient); -webkit-background-clip: text;
                -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 8px;
            }}
            
            /* Sidebar */
            #sidebar {{
                position: fixed; left: -260px; top: 0; bottom: 0; width: 260px;
                background: var(--sidebar); z-index: 1000; transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border-right: 1px solid var(--border); padding: 25px;
                box-shadow: 5px 0 15px rgba(0,0,0,0.1);
                display: flex; flex-direction: column; gap: 15px;
            }}
            #sidebar.open {{ left: 0; }}
            .overlay {{
                position: fixed; inset: 0; background: rgba(0,0,0,0.6); 
                z-index: 900; display: none; backdrop-filter: blur(2px);
            }}
            .overlay.open {{ display: block; }}
            
            .menu-btn {{
                padding: 12px; border-radius: 12px; cursor: pointer; display: flex; 
                align-items: center; gap: 12px; color: var(--text); font-weight: 500;
                transition: 0.2s;
            }}
            .menu-btn:hover {{ background: rgba(99, 102, 241, 0.1); color: var(--primary); }}
            
            /* Chat Area */
            #chat-container {{
                flex: 1; overflow-y: auto; padding: 20px; padding-bottom: 100px;
                display: flex; flex-direction: column; gap: 18px;
            }}
            
            /* Welcome Screen */
            #welcome-screen {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 80%; text-align: center; gap: 20px;
            }}
            .flux-logo {{
                font-size: 3.5rem; background: var(--gradient); -webkit-background-clip: text;
                -webkit-text-fill-color: transparent; animation: pulse 2s infinite;
            }}
            @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
            
            .suggestions {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; padding: 0 20px; }}
            .chip {{
                padding: 10px 18px; border: 1px solid var(--border); border-radius: 25px;
                font-size: 0.9rem; cursor: pointer; background: var(--bg); color: var(--text);
                transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .chip:hover {{ border-color: var(--primary); color: var(--primary); transform: translateY(-2px); }}

            /* Messages */
            .msg-row {{ display: flex; gap: 12px; width: 100%; animation: fadeUp 0.3s ease; }}
            @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            .msg-row.user {{ flex-direction: row-reverse; }}
            
            .avatar {{
                width: 38px; height: 38px; border-radius: 12px; display: flex; 
                align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0;
            }}
            .bot-av {{ background: var(--gradient); color: white; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3); }}
            .user-av {{ background: var(--text); color: var(--bg); }}
            
            .msg-bubble {{
                max-width: 85%; padding: 12px 18px; border-radius: 18px;
                font-size: 0.95rem; line-height: 1.6; position: relative;
                box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            }}
            .bot .msg-bubble {{ background: var(--msg-bot); border-bottom-left-radius: 4px; }}
            .user .msg-bubble {{ background: var(--msg-user); color: var(--text-user); border-bottom-right-radius: 4px; background: var(--gradient); }}
            
            /* Code Styling */
            pre {{ background: #282c34; padding: 15px; border-radius: 10px; overflow-x: auto; color: #fff; margin: 10px 0; }}
            code {{ font-family: 'Consolas', monospace; font-size: 0.9em; }}
            p {{ margin: 0 0 8px 0; }}
            p:last-child {{ margin: 0; }}

            /* Input Area */
            #input-area {{
                position: fixed; bottom: 0; left: 0; right: 0; padding: 15px;
                background: var(--bg); border-top: 1px solid var(--border);
                display: flex; justify-content: center;
            }}
            .input-box {{
                width: 100%; max-width: 800px;
                display: flex; align-items: center; background: var(--msg-bot);
                border-radius: 25px; padding: 8px 15px; border: 1px solid var(--border);
                box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); padding: 10px 5px; font-size: 1rem; resize: none; rows: 1; height: 24px; font-family: inherit;
            }}
            .send-btn {{
                width: 42px; height: 42px; background: var(--gradient); color: white;
                border-radius: 50%; border: none; cursor: pointer; display: flex;
                align-items: center; justify-content: center; margin-left: 10px;
                transition: transform 0.2s;
            }}
            .send-btn:active {{ transform: scale(0.9); }}

        </style>
    </head>
    <body>
    
        <div class="overlay" onclick="toggleMenu()"></div>
        <div id="sidebar">
            <h2 style="margin: 0 0 20px 0; font-weight: 700;">Menu</h2>
            <div class="menu-btn" onclick="clearChat()"><i class="fas fa-broom"></i> Clear History</div>
            <div class="menu-btn" onclick="toggleTheme()"><i class="fas fa-adjust"></i> Change Theme</div>
            <div class="menu-btn"><i class="fas fa-info-circle"></i> About Flux</div>
            <div style="margin-top: auto; font-size: 0.8rem; opacity: 0.6;">v2.0 Pro</div>
        </div>

        <header>
            <i class="fas fa-bars" style="font-size: 1.3rem; cursor: pointer;" onclick="toggleMenu()"></i>
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <div style="width: 24px;"></div>
        </header>

        <div id="chat-container">
            <div id="welcome-screen">
                <div class="flux-logo"><i class="fas fa-bolt"></i></div>
                <h2 style="margin:0;">I am {APP_NAME}</h2>
                <p style="opacity: 0.7;">Capable. Dynamic. Intelligent.</p>
                
                <div class="suggestions">
                    <div class="chip" onclick="sendChip('Write python code for a calculator')">💻 Write Code</div>
                    <div class="chip" onclick="sendChip('Give me a creative caption for FB')">📸 Social Caption</div>
                    <div class="chip" onclick="sendChip('Solve this math: 2x + 5 = 15')">🧮 Solve Math</div>
                    <div class="chip" onclick="sendChip('Explain Quantum Physics simply')">🔬 Explain Science</div>
                </div>
            </div>
        </div>

        <div id="input-area">
            <div class="input-box">
                <textarea id="msg" placeholder="Ask Flux anything..." oninput="autoResize(this)"></textarea>
                <button class="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const welcome = document.getElementById('welcome-screen');
            const input = document.getElementById('msg');
            let isDark = false;

            // Theme Toggle
            function toggleTheme() {{
                isDark = !isDark;
                document.body.classList.toggle('dark');
                toggleMenu();
            }}

            // Sidebar Toggle
            function toggleMenu() {{
                document.getElementById('sidebar').classList.toggle('open');
                document.querySelector('.overlay').classList.toggle('open');
            }}
            
            // Clear Chat
            function clearChat() {{
                if(confirm("Start a new conversation?")) {{
                    location.reload();
                }}
            }}

            function autoResize(el) {{
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 150) + 'px';
                if(el.value === '') el.style.height = '24px';
            }}

            function sendChip(text) {{
                input.value = text;
                sendMessage();
            }}

            function appendMessage(text, isUser) {{
                if(welcome) welcome.style.display = 'none';

                const row = document.createElement('div');
                row.className = `msg-row ${{isUser ? 'user' : 'bot'}}`;
                
                const av = isUser ? 'user-av' : 'bot-av';
                const icon = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';
                
                // Markdown parse with highlight
                const content = isUser ? text : marked.parse(text);
                
                row.innerHTML = `
                    <div class="avatar ${{av}}">${{icon}}</div>
                    <div class="msg-bubble">${{content}}</div>
                `;
                chat.appendChild(row);
                chat.scrollTop = chat.scrollHeight;
                
                // Apply syntax highlighting
                if(!isUser) hljs.highlightAll();
            }}

            async function sendMessage() {{
                const text = input.value.trim();
                if (!text) return;
                
                input.value = '';
                input.style.height = '24px';
                appendMessage(text, true);

                try {{
                    const res = await fetch(`/chat?prompt=${{encodeURIComponent(text)}}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let full = '';
                    
                    if(welcome) welcome.style.display = 'none';
                    const row = document.createElement('div');
                    row.className = 'msg-row bot';
                    row.innerHTML = `
                        <div class="avatar bot-av"><i class="fas fa-bolt"></i></div>
                        <div class="msg-bubble"><i class="fas fa-circle-notch fa-spin"></i> Thinking...</div>
                    `;
                    chat.appendChild(row);
                    const bubble = row.querySelector('.msg-bubble');

                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        full += decoder.decode(value);
                        bubble.innerHTML = marked.parse(full);
                        chat.scrollTop = chat.scrollHeight;
                    }}
                    hljs.highlightAll();
                }} catch (e) {{
                    appendMessage("⚠️ Flux is offline. Check internet.", false);
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
    if not prompt: return "No prompt", 400
    
    if 'user_id' not in session: session['user_id'] = str(uuid.uuid4())
    uid = session['user_id']
    
    if uid not in user_chats: user_chats[uid] = []
    
    # 🧠 Flux Brain (উন্নত ব্রেইন)
    # এখানে তাকে বলা হয়েছে রিপিট না করতে এবং সব ধরনের কাজ করতে।
    sys = {
        "role": "system", 
        "content": f"""
        You are {APP_NAME} (ফ্লাক্স).
        Current Time: {get_time()}.
        Owner: {OWNER_NAME} (Do not mention unless asked).
        
        **YOUR CORE DIRECTIVES:**
        1. **NO REPETITION:** Never start answers with robotic phrases like "I can help with that" or "Here is the answer". Just answer directly.
        2. **UNIVERSAL SOLVER:** You are an expert in Coding, Math, Science, Creative Writing, and Life Advice. Never say "I cannot do that" for safe queries.
        3. **TONE:** Be smart, witty, and confident. Use emojis sparingly but effectively.
        4. **LANGUAGE:** Detect user language. If Bangla, use natural Bangla. If English, use fluent English.
        5. **FORMAT:** Use Markdown. Use Code Blocks for code. Use Bold for emphasis.
        """
    }
    
    user_chats[uid].append({"role": "user", "content": prompt})
    user_chats[uid] = user_chats[uid][-12:] # মেমোরি একটু বাড়ালাম
    
    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[sys] + user_chats[uid],
                stream=True,
                temperature=0.8 # সৃজনশীলতা বাড়ানো হয়েছে
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
