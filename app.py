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

# বাংলাদেশের বর্তমান সময় বের করার ফাংশন
def get_bd_time():
    utc_now = datetime.utcnow()
    bd_time = utc_now + timedelta(hours=6) # UTC+6 for Bangladesh
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
            body { margin: 0; background: var(--bg-color); color: var(--text-color); font-family: 'Roboto', sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
            
            /* Header */
            header {
                padding: 15px; text-align: center; background: var(--chat-bg);
                box-shadow: 0 1px 2px rgba(0,0,0,0.1); z-index: 10;
                display: flex; justify-content: space-between; align-items: center;
            }
            h1 { font-size: 1.2rem; margin: 0; color: var(--text-color); }
            .theme-btn { background: none; border: none; font-size: 1.2rem; color: var(--text-color); cursor: pointer; }

            /* Chat Area */
            #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; scroll-behavior: smooth; }
            
            .message-wrapper { display: flex; width: 100%; }
            .message-wrapper.user { justify-content: flex-end; }
            .message-wrapper.bot { justify-content: flex-start; }

            .message {
                max-width: 75%; padding: 10px 15px; border-radius: 18px;
                font-size: 0.95rem; line-height: 1.5; position: relative; word-wrap: break-word;
            }
            .user .message { background: var(--user-msg-bg); color: var(--user-text); border-bottom-right-radius: 4px; }
            .bot .message { background: var(--bot-msg-bg); color: var(--bot-text); border-bottom-left-radius: 4px; }
            
            .message p { margin: 0; }
            .message ul, .message ol { padding-left: 20px; margin: 5px 0; }
            
            /* Typing Animation */
            .typing { font-style: italic; opacity: 0.7; font-size: 0.8rem; margin-left: 10px; margin-bottom: 10px; color: var(--text-color); display: none; }

            /* Input Area */
            #input-area { padding: 10px; background: var(--input-area-bg); display: flex; align-items: center; gap: 10px; }
            input {
                flex: 1; padding: 12px 15px; border-radius: 20px; border: none; outline: none;
                background: var(--chat-bg); color: var(--text-color); font-size: 1rem;
            }
            button {
                background: #0084ff; color: white; border: none; padding: 10px 15px;
                border-radius: 50%; cursor: pointer; font-size: 1rem; display: flex; align-items: center; justify-content: center;
                transition: transform 0.1s;
            }
            button:active { transform: scale(0.95); }

        </style>
    </head>
    <body>
        <header>
            <div style="width: 24px;"></div> <h1>Smart AI Buddy</h1>
            <button class="theme-btn" onclick="toggleTheme()"><i class="fas fa-moon"></i></button>
        </header>

        <div id="chat-container">
            <div class="message-wrapper bot">
                <div class="message">
                    হ্যালো! আমি তৈরি। আমি সবকিছু নিয়ে কথা বলতে পারি। আপনার কী সাহায্য লাগবে? 👋
                </div>
            </div>
        </div>
        <div class="typing" id="typing-indicator">AI লিখছে...</div>

        <div id="input-area">
            <input id="msg" placeholder="এখানে লিখুন..." autocomplete="off">
            <button onclick="sendMessage()"><i class="fas fa-paper-plane"></i></button>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const input = document.getElementById('msg');
            const typingInd = document.getElementById('typing-indicator');

            function toggleTheme() {
                document.body.classList.toggle('dark');
                const btn = document.querySelector('.theme-btn i');
                if (document.body.classList.contains('dark')) {
                    btn.classList.remove('fa-moon');
                    btn.classList.add('fa-sun');
                } else {
                    btn.classList.remove('fa-sun');
                    btn.classList.add('fa-moon');
                }
            }

            function appendMessage(text, isUser) {
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${isUser ? 'user' : 'bot'}`;
                
                const msgDiv = document.createElement('div');
                msgDiv.className = 'message';
                msgDiv.innerHTML = marked.parse(text);
                
                wrapper.appendChild(msgDiv);
                chat.appendChild(wrapper);
                chat.scrollTop = chat.scrollHeight;
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;

                appendMessage(text, true);
                input.value = '';
                typingInd.style.display = 'block';
                chat.scrollTop = chat.scrollHeight;

                try {
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}`);
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let fullResponse = '';
                    
                    // Create a placeholder for bot response
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'message';
                    wrapper.appendChild(msgDiv);
                    chat.appendChild(wrapper);

                    typingInd.style.display = 'none';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        fullResponse += decoder.decode(value);
                        msgDiv.innerHTML = marked.parse(fullResponse);
                        chat.scrollTop = chat.scrollHeight;
                    }
                } catch (e) {
                    typingInd.style.display = 'none';
                    appendMessage("⚠️ একটু সমস্যা হয়েছে, আবার চেষ্টা করুন।", false);
                }
            }

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    if not prompt:
        return "No prompt", 400

    # বাংলাদেশ সময় আপডেট করা
    bd_time_str = get_bd_time()

    if 'chat_history' not in session:
        session['chat_history'] = []

    # সিস্টেম প্রম্পট (প্রতিবার লেটেস্ট সময় সহ আপডেট হবে)
    # আমরা হিস্ট্রির শুরুতে সিস্টেম মেসেজ না রেখে, প্রতি রিকোয়েস্টে ইনজেক্ট করব
    # এতে সে সময় মনে রাখতে পারবে।
    
    current_system_prompt = {
        "role": "system",
        "content": f"""
        You are Smart AI Buddy, a friendly and intelligent assistant.
        
        **Your Capabilities:**
        1. **Current Time & Date:** You know that today is **{bd_time_str}** (Bangladesh Time). If asked about time, tell this.
        2. **Owner:** Your creator is **KAWCHUR**. 
           - **RULE:** NEVER mention your owner unless the user specifically asks "Who created you?". Keep it hidden otherwise.
        3. **Language:** Reply in Bangla if the user speaks Bangla. Reply in English if they speak English.
        4. **Personality:** Be natural, like a human friend. Don't sound like a robot. Use emojis.
        
        Answer short questions shortly. Answer complex questions with details.
        """
    }

    # সেশন থেকে আগের মেসেজ নেওয়া (System prompt বাদে)
    user_history = [msg for msg in session['chat_history'] if msg['role'] != 'system']
    
    # নতুন মেসেজ যোগ করা
    user_history.append({"role": "user", "content": prompt})
    
    # গ্রোক-এ পাঠানোর জন্য ফাইনাল লিস্ট (System Prompt + User History)
    messages_for_groq = [current_system_prompt] + user_history

    # সেশন আপডেট করা (ভবিষ্যতের জন্য)
    session['chat_history'] = user_history[-10:] # মেমোরি হালকা রাখতে লাস্ট ১০টা মেসেজ রাখি
    session.modified = True

    def generate():
        try:
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_groq,
                temperature=0.8, # সৃজনশীলতার জন্য একটু বাড়ালাম
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # অ্যাসিস্ট্যান্টের উত্তর হিস্ট্রিতে যোগ করা (পরের বার মনে রাখার জন্য)
            session['chat_history'].append({"role": "assistant", "content": full_response})
            session.modified = True

        except Exception as e:
            yield f"⚠️ সমস্যা: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
