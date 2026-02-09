from flask import Flask, request, Response, session, redirect, url_for, jsonify, send_file
from groq import Groq
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
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
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Groq keys rotation (Render-এ GROQ_KEYS = key1,key2,key3)
GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS:
        raise ValueError("কোনো Groq key নেই! Render-এ GROQ_KEYS সেট করো।")

    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        try:
            client = Groq(api_key=key)
            client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": "hi"}], max_tokens=1)
            return client
        except:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
    raise ValueError("সব key invalid!")

# ডাটাবেস মডেল
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    chats = db.relationship('Chat', backref='user', lazy=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200), default="New Chat")
    messages = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    # ডিফল্ট এডমিন (প্রথমবার চালালে)
    if not User.query.filter_by(email="your_email@gmail.com").first():
        admin = User(email="your_email@gmail.com", name="KAWCHUR", is_admin=True)
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Gmail OAuth (Google Console থেকে Client ID/Secret দাও)
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'}
)

# রিয়েল-টাইম ডেটা
def get_latest_news():
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn")
        return "\n".join([f"📰 {e.title}" for e in feed.entries[:4]])
    except:
        return "খবর লোড করতে সমস্যা।"

def get_crypto_price(coin="bitcoin"):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd")
        return f"💰 {coin.title()}: ${r.json()[coin]['usd']} USD"
    except:
        return "প্রাইস লোড করতে সমস্যা।"

@app.route("/")
@login_required
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
            body { margin: 0; font-family: system-ui; height: 100vh; display: flex; flex-direction: column; background: #f0f2f5; }
            header { background: #fff; padding: 12px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; }
            #chat { flex: 1; overflow-y: auto; padding: 16px; }
            .message { margin: 12px 0; padding: 14px; border-radius: 18px; max-width: 85%; }
            .user { background: #0d6efd; color: white; margin-left: auto; }
            .bot { background: white; border: 1px solid #ddd; }
            #input-area { background: white; padding: 12px; border-top: 1px solid #ddd; position: sticky; bottom: 0; }
            #input-form { display: flex; gap: 8px; }
            #msg { flex: 1; padding: 12px; border-radius: 24px; border: 1px solid #ccc; }
            button, .mic { padding: 12px; background: #0d6efd; color: white; border: none; border-radius: 50%; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h1>Smart AI Buddy</h1>
            <div>
                <button onclick="toggleTheme()">🌙</button>
                <button class="mic" onclick="startVoice()"><i class="fas fa-microphone"></i></button>
                <a href="/logout">লগআউট</a>
            </div>
        </header>
        <div id="chat"></div>
        <div id="input-area">
            <form id="input-form">
                <input id="msg" placeholder="লিখুন বা বলুন..." autocomplete="off">
                <button type="submit">পাঠান</button>
            </form>
        </div>

        <script>
            const chat = document.getElementById('chat');
            const input = document.getElementById('msg');
            let recognition;
            let synth = window.speechSynthesis;

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

            function speak(text) {
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'bn-BD';
                synth.speak(utter);
            }

            // বাকি JS (sendMessage, addMessage ইত্যাদি) আগের মতো রাখো
        </script>
    </body>
    </html>
    """

# চ্যাট (উন্নত)
@app.route("/chat")
@login_required
def chat():
    prompt = request.args.get("prompt")
    if not prompt:
        return "No prompt", 400

    # ডাটাবেসে চ্যাট সেভ (উদাহরণ)
    chat_entry = Chat.query.filter_by(user_id=current_user.id).first()
    if not chat_entry:
        chat_entry = Chat(user_id=current_user.id, messages=json.dumps([]))
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

            # ভয়েস রিপ্লাই
            tts = gTTS(full, lang='bn')
            audio = io.BytesIO()
            tts.write_to_fp(audio)
            audio.seek(0)
            # এখানে audio পাঠানো যাবে, কিন্তু ওয়েবে JS দিয়ে প্লে করতে হবে

        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

# Gmail লগইন (Google Console থেকে Client ID দাও)
@app.route("/login")
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/authorized")
def authorized():
    token = google.authorize_access_token()
    userinfo = google.get('userinfo').json()
    email = userinfo['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=userinfo['name'])
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('home'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# এডমিন প্যানেল
@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        return "তুমি এডমিন না!", 403
    users = User.query.all()
    return f"এডমিন প্যানেল<br>ইউজার: {len(users)}<br>" + "<br>".join([u.email for u in users])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)