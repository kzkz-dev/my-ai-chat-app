from flask import Flask, request, Response, session
from groq import Groq
import os
import uuid
from datetime import datetime
import pytz

# ==========================================
# 🔹 Flux v3.0 Ultimate Configuration
APP_NAME = "Flux"
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
        <title>{APP_NAME} Ultimate</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --primary: #6366f1;
                --gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                --bg: #ffffff;
                --sidebar: #f8fafc;
                --text: #0f172a;
                --msg-bot: #f1f5f9;
                --msg-user: #6366f1;
                --text-user: #ffffff;
                --border: #e2e8f0;
            }}
            body.dark {{
                --bg: #0f172a; --sidebar: #1e293b; --text: #f8fafc;
                --msg-bot: #1e293b; --msg-user: #6366f1; --border: #334155;
            }}
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Outfit', sans-serif; height: 100vh; display: flex; flex-direction: column; overflow: hidden; transition: 0.3s; }}
            
            /* Header */
            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 15px; border-bottom: 1px solid var(--border); background: var(--bg); z-index: 50;
            }}
            .brand {{ font-size: 1.4rem; font-weight: 700; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 8px; }}

            /* Chat Area */
            #chat-container {{ flex: 1; overflow-y: auto; padding: 20px; padding-bottom: 110px; display: flex; flex-direction: column; gap: 20px; }}
            
            /* Welcome Screen */
            #welcome-screen {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80%; text-align: center; gap: 20px; }}
            .flux-logo {{ font-size: 4rem; background: var(--gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: float 3s infinite ease-in-out; }}
            @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
            
            .chips {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }}
            .chip {{ padding: 10px 18px; border: 1px solid var(--border); border-radius: 25px; font-size: 0.9rem; cursor: pointer; background: var(--bg); color: var(--text); transition: 0.2s; }}
            .chip:hover {{ border-color: var(--primary); color: var(--primary); transform: translateY(-3px); box-shadow: 0 5px 15px rgba(99, 102, 241, 0.2); }}

            /* Messages */
            .msg-row {{ display: flex; gap: 12px; width: 100%; animation: fadeUp 0.3s ease; }}
            @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .msg-row.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; }}
            .bot-av {{ background: var(--gradient); color: white; box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3); }}
            .user-av {{ background: var(--text); color: var(--bg); }}
            
            .msg-bubble {{ max-width: 85%; padding: 12px 18px; border-radius: 18px; font-size: 0.95rem; line-height: 1.6; position: relative; }}
            .bot .msg-bubble {{ background: var(--msg-bot); border-bottom-left-radius: 4px; }}
            .user .msg-bubble {{ background: var(--msg-user); color: var(--text-user); border-bottom-right-radius: 4px; background: var(--gradient); }}

            /* Image Generation Style */
            .generated-image {{ max-width: 100%; border-radius: 12px; margin-top: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); border: 2px solid var(--border); }}
            
            /* Code Block & Copy Button */
            pre {{ position: relative; background: #282c34; padding: 15px; border-radius: 10px; overflow-x: auto; color: #fff; margin: 10px 0; }}
            .copy-btn {{ position: absolute; top: 5px; right: 5px; background: rgba(255,255,255,0.1); border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }}
            .copy-btn:hover {{ background: rgba(255,255,255,0.2); }}

            /* Input Area */
            #input-area {{ position: fixed; bottom: 0; left: 0; right: 0; padding: 15px; background: var(--bg); border-top: 1px solid var(--border); display: flex; justify-content: center; }}
            .input-box {{ width: 100%; max-width: 800px; display: flex; align-items: center; background: var(--msg-bot); border-radius: 25px; padding: 8px 10px; border: 1px solid var(--border); box-shadow: 0 5px 20px rgba(0,0,0,0.05); }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); padding: 10px; font-size: 1rem; resize: none; rows: 1; height: 24px; font-family: inherit; }}
            
            .action-btn {{ width: 40px; height: 40px; border-radius: 50%; border: none; background: transparent; color: #64748b; cursor: pointer; font-size: 1.1rem; transition: 0.2s; display: flex; align-items: center; justify-content: center; }}
            .action-btn:hover {{ color: var(--primary); background: rgba(99, 102, 241, 0.1); }}
            .send-btn {{ background: var(--gradient); color: white; margin-left: 5px; }}
            .send-btn:hover {{ opacity: 0.9; color: white; }}
            
            /* Speak Button */
            .speak-btn {{ margin-left: 8px; font-size: 0.9rem; color: #64748b; cursor: pointer; opacity: 0.7; }}
            .speak-btn:hover {{ opacity: 1; color: var(--primary); }}

            /* Recording Animation */
            .recording {{ color: #ef4444 !important; animation: pulse-red 1s infinite; }}
            @keyframes pulse-red {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.1); }} 100% {{ transform: scale(1); }} }}

        </style>
    </head>
    <body>
    
        <header>
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME} <span style="font-size:0.7rem; opacity:0.6; margin-top:5px;">ULTRA</span></div>
            <button class="action-btn" onclick="toggleTheme()"><i class="fas fa-adjust"></i></button>
        </header>

        <div id="chat-container">
            <div id="welcome-screen">
                <div class="flux-logo"><i class="fas fa-bolt"></i></div>
                <h2 style="margin:0;">Flux Ultimate</h2>
                <p style="opacity: 0.7;">Image Generation • Voice • Coding</p>
                <div class="chips">
                    <div class="chip" onclick="sendChip('Draw a futuristic city')">🎨 Draw Image</div>
                    <div class="chip" onclick="sendChip('Write Python code for Snake game')">🐍 Write Code</div>
                    <div class="chip" onclick="sendChip('Tell me a mystery story')">📖 Story</div>
                </div>
            </div>
        </div>

        <div id="input-area">
            <div class="input-box">
                <button class="action-btn" id="mic-btn" onclick="startDictation()"><i class="fas fa-microphone"></i></button>
                <textarea id="msg" placeholder="Message Flux..." oninput="autoResize(this)"></textarea>
                <button class="action-btn send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const welcome = document.getElementById('welcome-screen');
            const input = document.getElementById('msg');
            let isDark = false;

            function toggleTheme() {{
                isDark = !isDark;
                document.body.classList.toggle('dark');
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

            // 🎤 Voice Recognition (Speech to Text)
            function startDictation() {{
                if (window.hasOwnProperty('webkitSpeechRecognition')) {{
                    var recognition = new webkitSpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.lang = "bn-BD"; // Default Bangla, auto-detects English too mostly
                    
                    const micBtn = document.getElementById('mic-btn');
                    micBtn.classList.add('recording');
                    
                    recognition.start();
                    recognition.onresult = function(e) {{
                        document.getElementById('msg').value = e.results[0][0].transcript;
                        recognition.stop();
                        micBtn.classList.remove('recording');
                        autoResize(input);
                    }};
                    recognition.onerror = function(e) {{
                        recognition.stop();
                        micBtn.classList.remove('recording');
                    }};
                }} else {{
                    alert("Voice input not supported in this browser.");
                }}
            }}

            // 🔊 Text to Speech
            function speakText(text) {{
                const utterance = new SpeechSynthesisUtterance(text);
                window.speechSynthesis.speak(utterance);
            }}

            // 📋 Copy Code Function
            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach((block) => {{
                    if (block.querySelector('.copy-btn')) return;
                    const button = document.createElement('button');
                    button.innerText = 'Copy';
                    button.className = 'copy-btn';
                    button.onclick = () => {{
                        const code = block.querySelector('code').innerText;
                        navigator.clipboard.writeText(code);
                        button.innerText = 'Copied!';
                        setTimeout(() => {{ button.innerText = 'Copy'; }}, 2000);
                    }};
                    block.appendChild(button);
                }});
            }}

            function appendMessage(text, isUser) {{
                if(welcome) welcome.style.display = 'none';

                const row = document.createElement('div');
                row.className = `msg-row ${{isUser ? 'user' : 'bot'}}`;
                
                const av = isUser ? 'user-av' : 'bot-av';
                const icon = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';
                
                let content = isUser ? text : marked.parse(text);
                
                // Speak button for bot
                let actionHTML = '';
                if (!isUser) {{
                    actionHTML = `<i class="fas fa-volume-up speak-btn" onclick="speakText(this.parentElement.innerText)"></i>`;
                }}

                row.innerHTML = `
                    <div class="avatar ${{av}}">${{icon}}</div>
                    <div class="msg-bubble">
                        ${{content}}
                        ${{actionHTML}}
                    </div>
                `;
                chat.appendChild(row);
                chat.scrollTop = chat.scrollHeight;
                
                if(!isUser) {{
                    hljs.highlightAll();
                    addCopyButtons();
                }}
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
                        <div class="msg-bubble"><i class="fas fa-circle-notch fa-spin"></i> Generating...</div>
                    `;
                    chat.appendChild(row);
                    const bubble = row.querySelector('.msg-bubble');

                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;
                        full += decoder.decode(value);
                        bubble.innerHTML = marked.parse(full) + `<i class="fas fa-volume-up speak-btn" onclick="speakText(this.parentElement.innerText)"></i>`;
                        chat.scrollTop = chat.scrollHeight;
                    }}
                    hljs.highlightAll();
                    addCopyButtons();
                }} catch (e) {{
                    // Error
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
    
    # 🧠 SUPER SYSTEM PROMPT (Image Gen Logic)
    sys = {
        "role": "system", 
        "content": f"""
        You are {APP_NAME} Ultimate.
        Time: {get_time()}. Owner: {OWNER_NAME}.
        
        **CAPABILITIES:**
        1. **IMAGE GENERATION:** If user asks to "draw", "create image", or "paint" something, you MUST return ONLY this markdown format:
           ![Generated Image](https://image.pollinations.ai/prompt/DESCRIPTION?width=800&height=600&nologo=true)
           (Replace 'DESCRIPTION' with the user's request in English). Do not add any other text.
           
        2. **CODING:** Use Markdown code blocks.
        3. **GENERAL:** Smart, witty, short answers.
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
                temperature=0.8
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