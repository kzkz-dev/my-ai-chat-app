from flask import Flask, request, Response, session
from groq import Groq
import os
import requests
import feedparser
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # চ্যাট হিস্ট্রির জন্য দরকার

# API key Render-এ Environment Variable থেকে
GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set!")

def groq_client():
    return Groq(api_key=GROQ_KEY)

# রিয়েল-টাইম ডেটা ফাংশন
def get_latest_news():
    try:
        url = "https://news.google.com/rss/search?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn"
        feed = feedparser.parse(url)
        if feed.entries:
            return "\n".join([f"📰 {entry.title}" for entry in feed.entries[:4]])
        return "কোনো নতুন খবর পাওয়া যায়নি।"
    except:
        return "খবর লোড করতে সমস্যা হয়েছে।"

def get_crypto_price(coin="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        r = requests.get(url).json()
        price = r.get(coin, {}).get("usd", "N/A")
        return f"💰 {coin.title()} এর বর্তমান দাম: ${price} USD"
    except:
        return "প্রাইস লোড করতে সমস্যা হয়েছে।"

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart AI Buddy</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            :root {
                --primary: #0d6efd;
                --primary-dark: #0b5ed7;
                --bg: #f8f9fa;
                --text: #212529;
                --bot-bg: #ffffff;
                --user-bg: #0d6efd;
            }
            body.dark {
                --bg: #0d1117;
                --text: #c9d1d9;
                --bot-bg: #161b22;
                --user-bg: #238636;
            }
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: var(--bg);
                color: var(--text);
                height: 100vh;
                display: flex;
                flex-direction: column;
                transition: all 0.3s;
            }
            header {
                background: var(--bot-bg);
                border-bottom: 1px solid #30363d;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 1px 4px rgba(0,0,0,0.2);
            }
            header h1 {
                margin: 0;
                font-size: 1.4rem;
                font-weight: 600;
            }
            #chat {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                max-width: 900px;
                margin: 0 auto;
                width: 100%;
            }
            .message {
                margin: 12px 0;
                padding: 14px 18px;
                border-radius: 18px;
                max-width: 85%;
                line-height: 1.6;
                word-wrap: break-word;
            }
            .user {
                background: var(--user-bg);
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 4px;
            }
            .bot {
                background: var(--bot-bg);
                border: 1px solid #30363d;
                box-shadow: 0 1px 4px rgba(0,0,0,0.15);
                border-bottom-left-radius: 4px;
            }
            .message pre {
                background: #161b22;
                padding: 12px;
                border-radius: 8px;
                overflow-x: auto;
            }
            .message code {
                background: #161b22;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .typing {
                color: #8b949e;
                font-style: italic;
            }
            #input-area {
                background: var(--bot-bg);
                border-top: 1px solid #30363d;
                padding: 12px 16px;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
            }
            #input-form {
                display: flex;
                gap: 8px;
                max-width: 900px;
                margin: 0 auto;
            }
            #msg {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #30363d;
                border-radius: 24px;
                font-size: 16px;
                background: #0d1117;
                color: var(--text);
                outline: none;
            }
            #msg:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(13,110,253,0.3);
            }
            button {
                padding: 12px 20px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: 600;
                cursor: pointer;
            }
            button:hover { background: var(--primary-dark); }
            button:disabled { background: #30363d; }
        </style>
    </head>
    <body>
        <header>
            <div style="display:flex;align-items:center;gap:12px;">
                <i class="fas fa-robot" style="font-size:1.8rem;color:var(--primary);"></i>
                <h1>Smart AI Buddy</h1>
            </div>
            <button onclick="toggleDarkMode()" style="background:none;border:none;cursor:pointer;font-size:1.2rem;">
                <i class="fas fa-moon"></i>
            </button>
        </header>

        <div id="chat"></div>

        <div id="input-area">
            <form id="input-form">
                <input id="msg" placeholder="আপনার মেসেজ লিখুন..." autocomplete="off" autofocus>
                <button type="submit" id="send-btn"><i class="fas fa-paper-plane"></i></button>
            </form>
        </div>

        <script>
            const chat = document.getElementById('chat');
            const form = document.getElementById('input-form');
            const input = document.getElementById('msg');
            const sendBtn = document.getElementById('send-btn');

            function addMessage(text, isUser = false) {
                const div = document.createElement('div');
                div.className = `message ${isUser ? 'user' : 'bot'}`;
                div.innerHTML = marked.parse(text);  // Markdown রেন্ডার
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
                hljs.highlightAll();  // কোড হাইলাইট
                return div;
            }

            function showTyping() {
                const typing = addMessage('টাইপ করছি...', false);
                typing.classList.add('typing');
                return typing;
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;

                addMessage(text, true);
                input.value = '';
                sendBtn.disabled = true;

                const typingIndicator = showTyping();

                try {
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}`);
                    if (!res.ok) throw new Error('Network error');

                    const reader = res.body.getReader();
                    let fullResponse = '';

                    typingIndicator.innerHTML = '';
                    typingIndicator.classList.remove('typing');

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        fullResponse += new TextDecoder().decode(value);
                        typingIndicator.innerHTML = marked.parse(fullResponse);
                        chat.scrollTop = chat.scrollHeight;
                        hljs.highlightAll();
                    }
                } catch (err) {
                    typingIndicator.textContent = '⚠️ সমস্যা: ' + err.message;
                } finally {
                    sendBtn.disabled = false;
                    input.focus();
                }
            }

            form.addEventListener('submit', e => {
                e.preventDefault();
                sendMessage();
            });

            input.addEventListener('keypress', e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            function toggleDarkMode() {
                document.body.classList.toggle('dark');
                localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
            }

            // থিম লোড
            if (localStorage.getItem('theme') === 'dark') {
                document.body.classList.add('dark');
            }
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    if not prompt:
        return "No prompt", 400

    # চ্যাট হিস্ট্রি সেশনে রাখা
    if 'chat_history' not in session:
        session['chat_history'] = [
            {
                "role": "system",
                "content": """
                তুমি Smart AI Buddy — একটা অত্যন্ত স্মার্ট, দ্রুত, আপডেটেড এবং হেল্পফুল AI।
                তোমার মালিকের নাম KAWCHUR (বাংলায় কাওছুর)।
                যদি কেউ তোমার মালিক কে জিজ্ঞেস করে, সরাসরি বলো: "আমার মালিক KAWCHUR (কাওছুর)"।

                তোমার স্টাইল:
                • বাংলা, বাংলিশ, ইংরেজি — ইউজার যেভাবে কথা বলছে সেভাবে রিপ্লাই দাও।
                • সবসময় সত্যি, নিরপেক্ষ এবং সর্বশেষ তথ্য দিয়ে উত্তর দাও।
                • চিন্তা করে উত্তর দাও: step-by-step রিজনিং করো যখন জটিল প্রশ্ন।
                • মজার প্রশ্নে হিউমার, সিরিয়াসে সিরিয়াস।
                • খুব লম্বা উত্তর এড়িয়ে চলো — সংক্ষিপ্ত কিন্তু পূর্ণাঙ্গ।
                • রিয়েল-টাইম খবর, ক্রিপ্টো প্রাইস, সময়, আবহাওয়া ইত্যাদি দিতে পারো।
                • কোডিং, ম্যাথ, লজিক, লাইফ অ্যাডভাইস — সবকিছুতে এক্সপার্ট।
                • কখনো হলুসিনেট করো না — না জানলে বলো "আমি নিশ্চিত না"।
                """
            }
        ]

    session['chat_history'].append({"role": "user", "content": prompt})

    def generate():
        try:
            stream = groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=session['chat_history'],
                temperature=0.7,
                stream=True
            )
            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # হিস্ট্রিতে অ্যাসিস্ট্যান্টের উত্তর যোগ করো
            session['chat_history'].append({"role": "assistant", "content": full_response})
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)