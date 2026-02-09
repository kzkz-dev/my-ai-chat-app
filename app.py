from flask import Flask, request, Response, session, redirect, url_for, jsonify, send_file
from groq import Groq
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import feedparser
from gtts import gTTS
import io
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_ai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ডাটাবেস মডেল
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50))  # সেশন ID দিয়ে আলাদা করা
    title = db.Column(db.String(200), default="New Chat")
    messages = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# Groq keys rotation
GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS:
        raise ValueError("কোনো Groq key নেই!")

    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        try:
            client = Groq(api_key=key)
            client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": "hi"}], max_tokens=1)
            return client
        except:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    raise ValueError("সব key invalid!")

# রিয়েল-টাইম ডেটা
def get_latest_news():
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn")
        return "\n".join([f"📰 {e.title}" for e in feed.entries[:5]])
    except:
        return "খবর লোড করতে সমস্যা।"

def get_crypto_price(coin="bitcoin"):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd")
        return f"💰 {coin.title()}: ${r.json()[coin]['usd']} USD"
    except:
        return "প্রাইস লোড করতে সমস্যা।"

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
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
        <style>
            :root { --bg: #f8f9fa; --text: #212529; --bot: #ffffff; --user: #0d6efd; }
            body.dark { --bg: #0d1117; --text: #c9d1d9; --bot: #161b22; --user: #238636; }
            body { margin: 0; background: var(--bg); color: var(--text); font-family: system-ui; height: 100vh; display: flex; flex-direction: column; }
            header { background: var(--bot); padding: 12px; display: flex; justify-content: space-between; }
            #chat-list { padding: 10px; background: var(--bot); border-bottom: 1px solid #333; overflow-x: auto; white-space: nowrap; }
            .chat-item { padding: 8px 16px; background: #333; color: white; border-radius: 20px; margin-right: 8px; cursor: pointer; display: inline-block; }
            #chat { flex: 1; overflow-y: auto; padding: 16px; }
            .message { margin: 12px 0; padding: 14px; border-radius: 18px; max-width: 85%; }
            .user { background: var(--user); color: white; margin-left: auto; }
            .bot { background: var(--bot); border: 1px solid #333; }
            #input-area { background: var(--bot); padding: 12px; position: sticky; bottom: 0; border-top: 1px solid #333; }
            #input-form { display: flex; gap: 8px; }
            #msg { flex: 1; padding: 12px; border-radius: 24px; border: 1px solid #333; background: #0d1117; color: var(--text); }
            button, .mic { padding: 12px; background: #0d6efd; color: white; border: none; border-radius: 50%; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h1>Smart AI Buddy</h1>
            <button onclick="toggleTheme()">🌙</button>
        </header>
        <div id="chat-list"></div>
        <div id="chat"></div>
        <div id="input-area">
            <form id="input-form">
                <button type="button" class="mic" onclick="startVoice()"><i class="fas fa-microphone"></i></button>
                <input id="msg" placeholder="লিখুন বা বলুন..." autocomplete="off">
                <button type="submit">পাঠান</button>
            </form>
        </div>

        <script>
            const chat = document.getElementById('chat');
            const chatList = document.getElementById('chat-list');
            const input = document.getElementById('msg');
            let currentChatId = 'new';
            let recognition;

            function toggleTheme() {
                document.body.classList.toggle('dark');
            }

            function startVoice() {
                recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'bn-BD';
                recognition.onresult = e => {
                    input.value = e.results[0][0].transcript;
                    sendMessage();
                };
                recognition.start();
            }

            function addMessage(text, isUser = false) {
                const div = document.createElement('div');
                div.className = `message ${isUser ? 'user' : 'bot'}`;
                div.innerHTML = marked.parse(text);
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }

            function showTyping() {
                const typing = document.createElement('div');
                typing.className = 'message bot typing';
                typing.innerHTML = '<i class="fas fa-ellipsis-h fa-beat"></i> টাইপ করছি...';
                chat.appendChild(typing);
                chat.scrollTop = chat.scrollHeight;
                return typing;
            }

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;

                addMessage(text, true);
                input.value = '';

                const typing = showTyping();

                try {
                    const res = await fetch(`/chat?prompt=\( {encodeURIComponent(text)}&chat_id= \){currentChatId}`);
                    const reader = res.body.getReader();
                    let full = '';

                    typing.innerHTML = '';
                    typing.classList.remove('typing');

                    while (true) {
                        const {done, value} = await reader.read();
                        if (done) break;
                        full += new TextDecoder().decode(value);
                        typing.innerHTML = marked.parse(full);
                        chat.scrollTop = chat.scrollHeight;
                    }
                } catch (e) {
                    typing.innerHTML = '⚠️ সমস্যা: ' + e.message;
                }
            }

            form.addEventListener('submit', e => { e.preventDefault(); sendMessage(); });
            input.addEventListener('keypress', e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    chat_id = request.args.get("chat_id", "new")

    if not prompt:
        return "No prompt", 400

    # চ্যাট হিস্ট্রি ডাটাবেস থেকে লোড
    chat_entry = Chat.query.filter_by(session_id=session.sid if chat_id == "new" else chat_id).first()
    if not chat_entry:
        chat_entry = Chat(session_id=session.sid, messages=json.dumps([]))
        db.session.add(chat_entry)
        db.session.commit()

    history = json.loads(chat_entry.messages)
    history.append({"role": "user", "content": prompt})

    def generate():
        try:
            stream = get_groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                temperature=0.7,
                stream=True
            )
            full = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full += content
                    yield content

            history.append({"role": "assistant", "content": full})
            chat_entry.messages = json.dumps(history)
            db.session.commit()
        except Exception as e:
            yield f"⚠️ সমস্যা: {str(e)}"

    return Response(generate(), mimetype="text/plain")

@app.route("/admin")
def admin():
    password = request.args.get("password")
    if password == "kawchur123":  # এটা পরিবর্তন করে স্ট্রং করো
        session["is_admin"] = True
        return "এডমিন প্যানেলে স্বাগতম! (এখানে ইউজার লিস্ট, লগ ইত্যাদি যোগ করা যাবে)"
    return """
    <form>
        <input type="password" name="password" placeholder="এডমিন পাসওয়ার্ড">
        <button type="submit">লগইন</button>
    </form>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)