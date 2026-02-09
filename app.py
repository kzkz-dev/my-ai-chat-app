from flask import Flask, request, Response
from groq import Groq
import os

app = Flask(__name__)

# API key Render-এ Environment Variable থেকে নেবে
GROQ_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set! Please set it in Render dashboard.")

def groq_client():
    return Groq(api_key=GROQ_KEY)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart AI Buddy</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
            #chat { max-width: 800px; margin: auto; height: 80vh; overflow-y: auto; padding-bottom: 80px; }
            .message { margin: 12px 0; padding: 14px; border-radius: 18px; max-width: 85%; word-wrap: break-word; }
            .user { background: #0084ff; color: white; margin-left: auto; }
            .bot { background: white; border: 1px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            #input-area { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 12px; border-top: 1px solid #ddd; }
            #input { display: flex; max-width: 800px; margin: auto; }
            input { flex: 1; padding: 12px 16px; border-radius: 24px; border: 1px solid #ccc; font-size: 16px; }
            button { margin-left: 10px; padding: 12px 24px; background: #0084ff; color: white; border: none; border-radius: 24px; font-weight: bold; cursor: pointer; }
            button:hover { background: #006fd1; }
        </style>
    </head>
    <body>
        <div id="chat"></div>
        <div id="input-area">
            <div id="input">
                <input id="msg" placeholder="মেসেজ লিখুন..." autocomplete="off">
                <button onclick="send()">পাঠান</button>
            </div>
        </div>
        <script>
            const chat = document.getElementById('chat');
            const input = document.getElementById('msg');

            function addMsg(text, isUser = false) {
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

                try {
                    const res = await fetch('/chat?prompt=' + encodeURIComponent(text));
                    if (!res.ok) throw new Error('Network error');
                    const reader = res.body.getReader();
                    let full = '';
                    while (true) {
                        const {done, value} = await reader.read();
                        if (done) break;
                        full += new TextDecoder().decode(value);
                        botMsg.textContent = full;
                        chat.scrollTop = chat.scrollHeight;
                    }
                } catch (err) {
                    botMsg.textContent = '⚠️ সমস্যা হয়েছে: ' + err.message;
                }
            }

            input.addEventListener('keypress', e => {
                if (e.key === 'Enter') send();
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

    def generate():
        try:
            stream = groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stream=True
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)