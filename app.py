from flask import Flask, request, Response, session
from groq import Groq
import os
from datetime import datetime, timedelta

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
            return Groq(api_key=key)
        except Exception as e:
            print(f"Key {current_key_index} failed: {e}")
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)

    raise ValueError("সব Groq key invalid!")

def get_bd_time():
    utc_now = datetime.utcnow()
    bd_time = utc_now + timedelta(hours=6)
    return bd_time.strftime("%A, %d %B %Y, %I:%M %p")

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
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            :root {
                --bg-color: #ffffff;
                --chat-bg: #ffffff;
                --input-area-bg: #f0f2f5;
                --user-msg-bg: #0084ff;
                --user-text: #ffffff;
                --bot-msg-bg: #e4e6eb;
                --bot-text: #050505;
                --text-color: #050505;
            }
            body.dark {
                --bg-color: #18191a;
                --chat-bg: #18191a;
                --input-area-bg: #242526;
                --user-msg-bg: #0084ff;
                --user-text: #ffffff;
                --bot-msg-bg: #3a3b3c;
                --bot-text: #e4e6eb;
                --text-color: #e4e6eb;
            }
            body { margin: 0; background: var(--bg-color); color: var(--text-color); font-family: 'Roboto', sans-serif; height: 100vh; display: flex; flex-direction: column; }
            
            header {
                position: fixed; top: 0; left: 0; right: 0; height: 60px;
                background: var(--chat-bg); box-shadow: 0 1px 2px rgba(0,0,0,0.1); z-index: 100;
                display: flex; justify-content: space-between; align-items: center; padding: 0 20px;
            }
            
            #chat-container {
                margin-top: 60px; /* Header height */
                margin-bottom: 70px; /* Input area height */
                padding: 20px;
                overflow-y: auto;
                height: calc(100vh - 130px);
            }
            
            .message-wrapper { display: flex; width: 100%; margin-bottom: 10px; }
            .message-wrapper.user { justify-content: flex-end; }
            .message-wrapper.bot { justify-content: flex-start; }

            .message {
                max-width: 75%; padding: 10px 15px; border-radius: 18px;
                font-size: 0.95rem; line-height: 1.5; word-wrap: break-word;
            }
            .user .message { background: var(--user-msg-bg); color: var(--user-text); border-bottom-right-radius: 4px; }
            .bot .message { background: var(--bot-msg-bg); color: var(--bot-text); border-bottom-left-radius: 4px; }
            
            #input-area {
                position: fixed; bottom: 0; left: 0; right: 0;
                height: 70px;
                background: var(--input-area-bg);
                display: flex; align-items: center; gap: 10px; padding: 0 10px;
                z-index: 100; border-top: 1px solid rgba(0,0,0,0.1);
            }
            
            input {
                flex: 1; padding: 12px 15px; border-radius: 20px; border: none; outline: none;
                background: var(--chat-bg); color: var(--text-color); font-size: 1rem;
            }
            
            button.send-btn {
                background: #0084ff; color: white; border: none; padding: 10px;
                border-radius: 50%; cursor: pointer; height: 40px; width: 40px;
                display: flex; align-items: center; justify-content: center;
            }
            
            .theme-btn { background: none; border: none; font-size: 1.2rem; color: var(--text-color); cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <div style="width: 24px;"></div>
            <h3>Smart AI Buddy</h3>
            <button class="theme-btn" onclick="toggleTheme()"><i class="fas fa-moon"></i></button>
        </header>

        <div id="chat-container">
            <div class="message-wrapper bot">
                <div class="message">
                    হ্যালো! আমি তৈরি। এখন আমাকে মেসেজ পাঠাতে পারবেন! 👇
                </div>
            </div>
        </div>

        <div id="input-area">
            <input id="msg" placeholder="মেসেজ লিখুন..." autocomplete="off">
            <button class="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const input = document.getElementById('msg');

            function toggleTheme() {
                document.body.classList.toggle('dark');
                const btn = document.querySelector('.theme-btn i');
                btn.className = document.body.classList.contains('dark') ? 'fas fa-sun' : 'fas fa-moon';
            }

            function appendMessage(text, isUser) {
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${isUser ? 'user' : 'bot'}`;
                wrapper.innerHTML = `<div class="message">${marked.parse(text)}</div>`;
                chat.appendChild(wrapper);
                chat.scrollTop = chat.scrollHeight;
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;
                appendMessage(text, true);
                input.value = '';
                
                try {
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let fullResponse = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'message';
                    wrapper.appendChild(msgDiv);
                    chat.appendChild(wrapper);

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        fullResponse += decoder.decode(value);
                        msgDiv.innerHTML = marked.parse(fullResponse);
                        chat.scrollTop = chat.scrollHeight;
                    }
                } catch (e) {
                    appendMessage("⚠️ সমস্যা হয়েছে!", false);
                }
            }
            
            input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    if not prompt: return "No prompt", 400
    
    bd_time_str = get_bd_time()
    
    if 'chat_history' not in session: session['chat_history'] = []
    
    system_prompt = {
        "role": "system",
        "content": f"You are Smart AI Buddy. Current time in Bangladesh: {bd_time_str}. Owner: KAWCHUR (Reveal owner ONLY if asked). Reply in user's language (Bangla/English). Be friendly."
    }
    
    history = [msg for msg in session['chat_history'] if msg['role'] != 'system']
    history.append({"role": "user", "content": prompt})
    session['chat_history'] = history[-10:]
    session.modified = True
    
    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[system_prompt] + history,
                stream=True
            )
            resp = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    c = chunk.choices[0].delta.content
                    resp += c
                    yield c
            session['chat_history'].append({"role": "assistant", "content": resp})
            session.modified = True
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
