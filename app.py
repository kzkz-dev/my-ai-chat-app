from flask import Flask, request, Response, session
from groq import Groq
import os
import uuid
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = os.urandom(24)

# মেমোরিতে চ্যাট হিস্ট্রি রাখার জন্য (Error Fix)
user_chats = {}

# Render-এর GROQ_KEYS লোড করা
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
        except Exception as e:
            print(f"Key failed: {e}")
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    raise ValueError("All keys invalid!")

# ১. সময় ফিক্স (TimeZone ব্যবহার করে)
def get_bd_time():
    bd_zone = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_zone)
    # ফরম্যাট: 10:30 PM
    return bd_time.strftime("%I:%M %p") 

# ২. তারিখ ফিক্স
def get_bd_date():
    bd_zone = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_zone)
    return bd_time.strftime("%d %B, %Y (%A)")

@app.route("/")
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Smart AI</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #007AFF; /* Default Blue */
                --bg: #ffffff;
                --text: #000000;
                --gray: #f2f2f7;
                --msg-user: #007AFF;
                --msg-bot: #e9e9eb;
                --text-user: #ffffff;
                --text-bot: #000000;
            }
            
            /* থিম ভেরিয়েবল */
            body.theme-blue { --primary: #007AFF; --msg-user: #007AFF; }
            body.theme-green { --primary: #25D366; --msg-user: #25D366; } /* WhatsApp */
            body.theme-purple { --primary: #8B5CF6; --msg-user: #8B5CF6; }
            body.theme-orange { --primary: #F97316; --msg-user: #F97316; }
            body.theme-dark { 
                --bg: #111827; --text: #ffffff; --gray: #1f2937; 
                --msg-bot: #374151; --text-bot: #ffffff; 
                --primary: #3B82F6; --msg-user: #3B82F6;
            }

            body { 
                margin: 0; background: var(--bg); color: var(--text); 
                font-family: 'Inter', sans-serif; height: 100vh; display: flex; flex-direction: column; 
                transition: background 0.3s, color 0.3s;
            }
            
            /* হেডার ডিজাইন */
            header {
                position: fixed; top: 0; left: 0; right: 0; height: 60px;
                background: var(--bg); 
                border-bottom: 1px solid rgba(0,0,0,0.1);
                display: flex; justify-content: space-between; align-items: center; padding: 0 15px;
                z-index: 100;
            }
            body.theme-dark header { border-bottom: 1px solid rgba(255,255,255,0.1); }
            
            .brand { font-weight: 700; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
            
            .controls { display: flex; gap: 15px; }
            .icon-btn { background: none; border: none; font-size: 1.2rem; color: var(--text); cursor: pointer; transition: transform 0.2s; }
            .icon-btn:active { transform: scale(0.9); }
            
            /* ল্যাঙ্গুয়েজ ব্যাজ */
            #lang-badge { font-size: 0.8rem; font-weight: bold; padding: 4px 8px; border-radius: 12px; background: var(--gray); }

            /* চ্যাট এরিয়া */
            #chat-container {
                margin-top: 60px; margin-bottom: 70px; padding: 15px;
                overflow-y: auto; height: 100%; scroll-behavior: smooth;
            }
            
            .message-wrapper { display: flex; width: 100%; margin-bottom: 12px; }
            .message-wrapper.user { justify-content: flex-end; }
            
            .message {
                max-width: 80%; padding: 10px 16px; border-radius: 20px;
                font-size: 0.95rem; line-height: 1.5; word-wrap: break-word;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            .user .message { background: var(--msg-user); color: var(--text-user); border-bottom-right-radius: 4px; }
            .bot .message { background: var(--msg-bot); color: var(--text-bot); border-bottom-left-radius: 4px; }
            
            .message p { margin: 0; }
            
            /* ইনপুট এরিয়া */
            #input-area {
                position: fixed; bottom: 0; left: 0; right: 0; height: 70px;
                background: var(--bg); border-top: 1px solid rgba(0,0,0,0.05);
                display: flex; align-items: center; gap: 10px; padding: 0 15px;
                z-index: 100;
            }
            body.theme-dark #input-area { border-top: 1px solid rgba(255,255,255,0.1); }
            
            input {
                flex: 1; padding: 12px 20px; border-radius: 25px; border: none; 
                background: var(--gray); color: var(--text); font-size: 1rem; outline: none;
            }
            
            button.send-btn {
                background: var(--primary); color: white; border: none; 
                width: 45px; height: 45px; border-radius: 50%; 
                cursor: pointer; display: flex; align-items: center; justify-content: center;
                font-size: 1.1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body class="theme-blue">
        <header>
            <div class="brand"><i class="fas fa-robot" style="color: var(--primary)"></i> AI Buddy</div>
            <div class="controls">
                <span id="lang-badge" onclick="toggleLang()">BN</span>
                <button class="icon-btn" onclick="toggleTheme()"><i class="fas fa-palette"></i></button>
            </div>
        </header>

        <div id="chat-container">
            <div class="message-wrapper bot">
                <div class="message">
                    হ্যালো! আমি তৈরি। আমাকে যা খুশি জিজ্ঞেস করতে পারেন। 👇
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
            const langBadge = document.getElementById('lang-badge');
            
            // ৩. থিম এবং ভাষা সেটআপ
            const themes = ['theme-blue', 'theme-green', 'theme-purple', 'theme-orange', 'theme-dark'];
            let currentThemeIdx = 0;
            let currentLang = 'bn'; // 'bn' or 'en'

            // থিম পরিবর্তন ফাংশন
            function toggleTheme() {
                document.body.classList.remove(themes[currentThemeIdx]);
                currentThemeIdx = (currentThemeIdx + 1) % themes.length;
                document.body.classList.add(themes[currentThemeIdx]);
            }

            // ভাষা পরিবর্তন ফাংশন
            function toggleLang() {
                currentLang = currentLang === 'bn' ? 'en' : 'bn';
                langBadge.innerText = currentLang.toUpperCase();
                langBadge.style.background = currentLang === 'bn' ? '#d1fae5' : '#e0f2fe';
                langBadge.style.color = currentLang === 'bn' ? '#065f46' : '#075985';
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
                    // ল্যাঙ্গুয়েজ প্যারামিটার পাঠানো হচ্ছে
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}&lang=${currentLang}`);
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
                    appendMessage("⚠️ Connection error!", false);
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
    lang_pref = request.args.get("lang", "bn") # ফ্রন্টএন্ড থেকে ভাষা আসছে
    
    if not prompt: return "No prompt", 400
    
    # ইউজার ID (APK-তে প্রতিবার অ্যাপ ওপেন করলে নতুন সেশন হতে পারে, তাই কুকি ইউজ করছি)
    if 'user_id' not in session: session['user_id'] = str(uuid.uuid4())
    user_id = session['user_id']
    
    # বর্তমান সঠিক সময় (Render এর সার্ভার টাইম নয়, বাংলাদেশ টাইম)
    time_str = get_bd_time()
    date_str = get_bd_date()
    
    if user_id not in user_chats: user_chats[user_id] = []
    
    # ৪. স্মার্ট এবং শর্ট সিস্টেম প্রম্পট (বেশি কথা বলবে না)
    # ভাষা অনুযায়ী ইনস্ট্রাকশন সেট করা
    lang_instruction = "Reply in Bangla." if lang_pref == 'bn' else "Reply in English."
    
    system_prompt = {
        "role": "system",
        "content": f"""
        You are Smart AI Buddy. 
        Current Time: {time_str} (Bangladesh Time).
        Current Date: {date_str}.
        Owner: KAWCHUR (Say ONLY if asked).
        
        **STRICT INSTRUCTIONS:**
        1. {lang_instruction}
        2. Be CONCISE and SMART like ChatGPT. Do NOT write long essays unless asked.
        3. Be friendly and witty.
        4. If asked about time, give the exact time provided above.
        """
    }
    
    # ইউজারের মেসেজ অ্যাড
    user_chats[user_id].append({"role": "user", "content": prompt})
    user_chats[user_id] = user_chats[user_id][-8:] # মেমোরি ক্লিন রাখা
    
    messages_final = [system_prompt] + user_chats[user_id]

    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_final,
                stream=True,
                temperature=0.7 
            )
            
            full_resp = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    c = chunk.choices[0].delta.content
                    full_resp += c
                    yield c
            
            # গ্লোবাল ভেরিয়েবলে সেভ (Session error fix)
            user_chats[user_id].append({"role": "assistant", "content": full_resp})
            
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
