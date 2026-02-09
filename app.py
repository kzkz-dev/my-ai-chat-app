from flask import Flask, request, Response, session
from groq import Groq
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Render-এর GROQ_KEYS থেকে কি (Key) লোড করা
GROQ_KEYS = os.environ.get("GROQ_KEYS", "").split(",")
current_key_index = 0

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS or GROQ_KEYS == ['']:
        raise ValueError("কোনো Groq key পাওয়া যায়নি! Render-এ GROQ_KEYS সেট করো।")

    # ৩ বার চেষ্টা করবে ভিন্ন ভিন্ন কি দিয়ে
    for _ in range(len(GROQ_KEYS)):
        key = GROQ_KEYS[current_key_index].strip()
        if not key:
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
            continue
            
        try:
            client = Groq(api_key=key)
            # টেস্ট কল (ছোট্ট করে চেক করি key কাজ করে কি না)
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return client
        except Exception as e:
            print(f"Key {current_key_index} failed: {e}")
            current_key_index = (current_key_index + 1) % len(GROQ_KEYS)

    raise ValueError("সব Groq key invalid বা rate-limited!")

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
            :root { --primary: #0d6efd; --bg: #f8f9fa; --text: #212529; --bot: #ffffff; --user: #0d6efd; }
            body.dark { --bg: #0d1117; --text: #c9d1d9; --bot: #161b22; --user: #238636; }
            body { margin: 0; background: var(--bg); color: var(--text); font-family: system-ui; height: 100vh; display: flex; flex-direction: column; }
            header { background: var(--bot); padding: 12px; display: flex; justify-content: space-between; border-bottom: 1px solid #30363d; }
            #chat { flex: 1; overflow-y: auto; padding: 16px; }
            .message { margin: 12px 0; padding: 14px; border-radius: 18px; max-width: 85%; line-height: 1.6; }
            .user { background: var(--user); color: white; margin-left: auto; }
            .bot { background: var(--bot); border: 1px solid #30363d; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
            .typing { color: #8b949e; font-style: italic; }
            #input-area { background: var(--bot); padding: 12px; position: sticky; bottom: 0; border-top: 1px solid #30363d; }
            #input-form { display: flex; gap: 8px; max-width: 900px; margin: auto; }
            #msg { flex: 1; padding: 12px; border-radius: 24px; border: 1px solid #30363d; background: #0d1117; color: var(--text); }
            button { padding: 12px 20px; background: var(--primary); color: white; border: none; border-radius: 24px; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <h1>Smart AI Buddy</h1>
            <button onclick="toggleTheme()">🌙</button>
        </header>
        <div id="chat"></div>
        <div id="input-area">
            <form id="input-form">
                <input id="msg" placeholder="মেসেজ লিখুন..." autocomplete="off" autofocus>
                <button type="submit">পাঠান</button>
            </form>
        </div>

        <script>
            const chat = document.getElementById('chat');
            const form = document.getElementById('input-form');
            const input = document.getElementById('msg');

            function toggleTheme() {
                document.body.classList.toggle('dark');
                localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
            }
            if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark');

            function addMessage(text, isUser = false) {
                const div = document.createElement('div');
                div.className = `message ${isUser ? 'user' : 'bot'}`;
                div.innerHTML = marked.parse(text);
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
                hljs.highlightAll();
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
                    const res = await fetch(`/chat?prompt=${encodeURIComponent(text)}`);
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
                        hljs.highlightAll();
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
    if not prompt:
        return "No prompt", 400

    # ১. চ্যাট হিস্ট্রি সেশন তৈরি বা লোড করা (রিকোয়েস্ট কন্টেক্সটের ভেতরে)
    if 'chat_history' not in session:
        session['chat_history'] = [
            {
                "role": "system",
                "content": """
                তুমি Smart AI Buddy — একটা অত্যন্ত স্মার্ট, দ্রুত, আপডেটেড এবং হেল্পফুল AI।
                তোমার মালিকের নাম KAWCHUR (বাংলায় কাওছুর)।
                যদি কেউ তোমার মালিক কে জিজ্ঞেস করে, বলো: "আমার মালিক KAWCHUR (কাওছুর)"।
                
                স্টাইল:
                - বাংলা/বাংলিশ/ইংরেজি — ইউজারের স্টাইলে মিশিয়ে কথা বলো।
                - সত্যি, নিরপেক্ষ, সর্বশেষ তথ্য দিয়ে উত্তর।
                - জটিল প্রশ্নে step-by-step চিন্তা করে উত্তর দাও।
                - মজার প্রশ্নে হিউমার, সিরিয়াসে সিরিয়াস।
                - সংক্ষিপ্ত কিন্তু পূর্ণাঙ্গ উত্তর।
                - না জানলে বলো "আমি নিশ্চিত না"।
                """
            }
        ]

    # ২. ইউজারের মেসেজ সেশনে যোগ করা
    session['chat_history'].append({"role": "user", "content": prompt})
    session.modified = True
    
    # ৩. জেনারেটরের জন্য মেসেজ লিস্ট কপি করে নেওয়া
    # (এটিই আপনার 'Working outside of request context' সমস্যার সমাধান)
    messages_for_groq = list(session['chat_history'])

    def generate():
        try:
            # এখানে সরাসরি session ভেরিয়েবল ব্যবহার করবেন না, messages_for_groq ব্যবহার করুন
            client = get_groq_client()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_groq,
                temperature=0.7,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield content

            # নোট: স্ট্রিমিং চলাকালীন বা শেষে session আপডেট করা যায় না, 
            # কারণ রেসপন্স হেডার আগেই পাঠানো হয়ে যায়।

        except Exception as e:
            print(f"Error in generate: {e}")
            yield f"⚠️ সমস্যা: {str(e)} (Key rotation check logs)"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
