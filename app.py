from flask import Flask, request, Response, session
from groq import Groq
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Render-এর GROQ_KEYS থেকে কি (Key) লোড করা
GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS or GROQ_KEYS == ['']:
        raise ValueError("কোনো Groq key পাওয়া যায়নি! Render-এ GROQ_KEYS সেট করো।")

    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        if not key:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
            continue
            
        try:
            client = Groq(api_key=key)
            return client
        except Exception as e:
            print(f"Key {current_key_index} failed: {e}")
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)

    raise ValueError("সব Groq key invalid!")

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Smart AI Buddy</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <style>
            :root {
                --bg-color: #ffffff;
                --sidebar-color: #f9f9f9;
                --text-color: #374151;
                --input-bg: #f3f4f6;
                --border-color: #e5e7eb;
                --user-msg-bg: #f3f4f6;
                --bot-msg-bg: transparent;
                --accent-color: #10a37f; /* ChatGPT Greenish */
            }
            body.dark {
                --bg-color: #343541;
                --sidebar-color: #202123;
                --text-color: #ececf1;
                --input-bg: #40414f;
                --border-color: #565869;
                --user-msg-bg: #444654;
                --bot-msg-bg: transparent;
                --accent-color: #19c37d;
            }
            body { margin: 0; background: var(--bg-color); color: var(--text-color); font-family: 'Inter', sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; transition: background 0.3s; }
            
            /* Header */
            header {
                padding: 10px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
                background: var(--bg-color);
                z-index: 10;
            }
            h1 { font-size: 1.1rem; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 8px; }
            .theme-toggle { background: none; border: none; color: var(--text-color); cursor: pointer; font-size: 1.2rem; padding: 5px; border-radius: 5px; }
            .theme-toggle:hover { background: var(--input-bg); }

            /* Chat Area */
            #chat-container { flex: 1; overflow-y: auto; display: flex; flex-direction: column; align-items: center; scroll-behavior: smooth; }
            #chat-content { width: 100%; max-width: 800px; padding: 20px; padding-bottom: 120px; }
            
            .message { display: flex; gap: 16px; padding: 20px 0; border-bottom: 1px solid rgba(0,0,0,0.05); animation: fadeIn 0.3s ease; }
            body.dark .message { border-bottom: 1px solid rgba(255,255,255,0.05); }
            
            .avatar { width: 30px; height: 30px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
            .user-avatar { background: #5b48d9; color: white; border-radius: 50%; }
            .bot-avatar { background: #10a37f; color: white; }
            
            .msg-text { flex: 1; line-height: 1.7; font-size: 0.95rem; overflow-x: hidden; }
            .msg-text p { margin-top: 0; }
            .msg-text pre { background: #000; padding: 15px; border-radius: 8px; overflow-x: auto; color: #fff; }
            
            /* Typing Indicator */
            .typing-indicator span { display: inline-block; width: 6px; height: 6px; background-color: var(--text-color); border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; margin: 0 2px; opacity: 0.6; }
            .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
            .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

            /* Input Area */
            #input-area {
                position: fixed; bottom: 0; left: 0; right: 0;
                background: linear-gradient(180deg, rgba(255,255,255,0) 0%, var(--bg-color) 20%);
                padding: 20px;
                display: flex; justify-content: center;
            }
            body.dark #input-area { background: linear-gradient(180deg, rgba(52,53,65,0) 0%, var(--bg-color) 20%); }

            form {
                width: 100%; max-width: 768px; position: relative;
                background: var(--input-bg);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
                display: flex; align-items: flex-end;
                padding: 10px 10px 10px 16px;
            }
            form:focus-within { border-color: var(--text-color); box-shadow: 0 0 20px rgba(0,0,0,0.15); }
            
            textarea {
                flex: 1; background: transparent; border: none; color: var(--text-color);
                font-family: inherit; font-size: 1rem; resize: none; max-height: 200px;
                padding: 4px 0; outline: none; line-height: 1.5;
            }
            
            button {
                background: var(--accent-color); color: white; border: none;
                padding: 8px 12px; border-radius: 8px; cursor: pointer;
                transition: opacity 0.2s; display: flex; align-items: center; justify-content: center;
                margin-left: 10px; height: 35px; width: 35px;
            }
            button:disabled { background: var(--border-color); cursor: not-allowed; }
            button:hover:not(:disabled) { opacity: 0.9; }

        </style>
    </head>
    <body>
        <header>
            <h1><i class="fas fa-robot"></i> Smart AI Buddy</h1>
            <button class="theme-toggle" onclick="toggleTheme()"><i class="fas fa-moon"></i></button>
        </header>

        <div id="chat-container">
            <div id="chat-content">
                <div class="message">
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="msg-text">
                        হ্যালো! আমি তৈরি। তোমার কি সাহায্য লাগবে? <br>
                        <span style="font-size: 0.85em; opacity: 0.7;">(Ask me anything in Bangla or English)</span>
                    </div>
                </div>
            </div>
        </div>

        <div id="input-area">
            <form id="input-form">
                <textarea id="msg" rows="1" placeholder="মেসেজ লিখুন..." autofocus></textarea>
                <button type="submit" id="send-btn"><i class="fas fa-paper-plane"></i></button>
            </form>
        </div>

        <script>
            const chatContent = document.getElementById('chat-content');
            const form = document.getElementById('input-form');
            const input = document.getElementById('msg');
            const sendBtn = document.getElementById('send-btn');

            // Theme Management
            function toggleTheme() {
                document.body.classList.toggle('dark');
                const isDark = document.body.classList.contains('dark');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
                document.querySelector('.theme-toggle i').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
            }
            if (localStorage.getItem('theme') === 'dark') toggleTheme();

            // Auto-resize textarea
            input.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
                if(this.value === '') this.style.height = 'auto';
            });

            // Handle Enter key
            input.addEventListener('keydown', e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            function appendMessage(role, text) {
                const div = document.createElement('div');
                div.className = 'message';
                const icon = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';
                const avatarClass = role === 'user' ? 'user-avatar' : 'bot-avatar';
                
                div.innerHTML = `
                    <div class="avatar ${avatarClass}">${icon}</div>
                    <div class="msg-text">${marked.parse(text)}</div>
                `;
                chatContent.appendChild(div);
                window.scrollTo(0, document.body.scrollHeight);
                hljs.highlightAll();
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;

                appendMessage('user', text);
                input.value = '';
                input.style.height = 'auto';
                sendBtn.disabled = true;

                // Typing indicator
                const typingDiv = document.createElement('div');
                typingDiv.className = 'message typing';
                typingDiv.innerHTML = `
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="msg-text typing-indicator"><span></span><span></span><span></span></div>
                `;
                chatContent.appendChild(typingDiv);
                window.scrollTo(0, document.body.scrollHeight);

                try {
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let fullResponse = '';
                    
                    // Remove typing indicator before streaming
                    typingDiv.remove();
                    
                    // Create Bot Message container
                    const botDiv = document.createElement('div');
                    botDiv.className = 'message';
                    botDiv.innerHTML = `
                        <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                        <div class="msg-text"></div>
                    `;
                    chatContent.appendChild(botDiv);
                    const msgTextDiv = botDiv.querySelector('.msg-text');

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        const chunk = decoder.decode(value);
                        fullResponse += chunk;
                        msgTextDiv.innerHTML = marked.parse(fullResponse);
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                    hljs.highlightAll();

                } catch (e) {
                    typingDiv.innerHTML = `<div class="msg-text" style="color:red">⚠️ সমস্যা হয়েছে: ${e.message}</div>`;
                }
                sendBtn.disabled = false;
            }

            form.addEventListener('submit', e => { e.preventDefault(); sendMessage(); });
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    if not prompt:
        return "No prompt", 400

    # ১. স্মার্ট এবং মডার্ন সিস্টেম প্রম্পট (মালিকের নাম লুকানো থাকবে)
    if 'chat_history' not in session:
        session['chat_history'] = [
            {
                "role": "system",
                "content": """
                You are 'Smart AI Buddy', a highly advanced, empathetic, and witty AI assistant.
                
                **CORE RULES:**
                1. **IDENTITY:** Your owner/creator is **KAWCHUR** (কাওছুর). 
                   - **IMPORTANT:** NEVER mention your owner KAWCHUR unless the user *specifically* asks "Who created you?" or "Who is your owner?". 
                   - If not asked, keep it secret. Focus purely on helping the user.
                
                2. **LANGUAGE & TONE:** - Detect the user's language (Bangla or English).
                   - If user writes in Bangla -> Reply in **natural, smart, modern Bangla** (avoid robotic/bookish language). Use words like 'ঠিক আছে', 'বুঝতে পেরেছি', 'অবশ্যই'.
                   - If user writes in English -> Reply in smart, concise English.
                   - Be conversational, friendly, and helpful. Use emojis occasionally (🙂, 🚀, 💡) to make it feel fresh.
                
                3. **BEHAVIOR:**
                   - Don't repeat "How can I help" in every line.
                   - If the question is simple ("Hi"), reply simply ("হ্যালো! কেমন আছেন?").
                   - If the question is complex, give a structured, clear answer.
                """
            }
        ]

    session['chat_history'].append({"role": "user", "content": prompt})
    session.modified = True
    
    # কপি তৈরি করা (জেনারেটরের জন্য)
    messages_for_groq = list(session['chat_history'])

    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_groq,
                temperature=0.7, # সৃজনশীলতা বাড়ানো হয়েছে
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"⚠️ দুঃখিত, একটু সমস্যা হচ্ছে: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
