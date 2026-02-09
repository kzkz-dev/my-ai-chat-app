from flask import Flask, request, Response
from groq import Groq
import os

app = Flask(__name__)

# Key টা env var থেকে নেবে (Render-এ সেট করবা)
GROQ_KEY = os.environ.get("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")
if not GROQ_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set!")

def groq_client():
    return Groq(api_key=GROQ_KEY)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <title>Smart AI Buddy</title>
        <style>
            body { font-family: Arial; margin: 0; padding: 20px; background: #f0f2f5; }
            #chat { max-width: 800px; margin: auto; height: 80vh; overflow-y: auto; }
            .message { margin: 10px; padding: 12px; border-radius: 12px; max-width: 80%; }
            .user { background: #0084ff; color: white; margin-left: auto; }
            .bot { background: white; border: 1px solid #ddd; }
            #input { position: fixed; bottom: 10px; width: 90%; max-width: 800px; display: flex; }
            input { flex: 1; padding: 12px; border-radius: 20px; border: 1px solid #ddd; }
            button { margin-left: 10px; padding: 12px 20px; background: #0084ff; color: white; border: none; border-radius: 20px; }
        </style>
    </head>
    <body>
        <div id="chat"></div>
        <div id="input">
            <input id="msg" placeholder="মেসেজ লিখুন...">
            <button onclick="send()">পাঠান</button>
        </div>
        <script>
            const chat = document.getElementById('chat');
            const input = document.getElementById('msg');

            function addMsg(text, isUser=false) {
                const div = document.createElement('div');
                div.className = 'message ' + (isUser ? 'user' : 'bot');
                div.textContent = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }

            async function send() {
                const text = input.value.trim();
                if (!text) return;
                addMsg(text, true);
                input.value = '';

                addMsg('টাইপ করছি...');
                const botMsg = chat.lastChild;

                const res = await fetch('/chat?prompt=' + encodeURIComponent(text));
                const reader = res.body.getReader();
                let full = '';
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    full += new TextDecoder().decode(value);
                    botMsg.textContent = full;
                    chat.scrollTop = chat.scrollHeight;
                }
            }

            input.addEventListener('keypress', e => { if (e.key === 'Enter') send(); });
        </script>
    </body>
    </html>
    """

@app.route("/chat")
def chat():
    prompt = request.args.get("prompt")
    if not prompt:
        return "No prompt"

    def generate():
        try:
            stream = groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)