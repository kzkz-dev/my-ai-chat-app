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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            :root {
                --primary: #0d6efd;
                --primary-dark: #0b5ed7;
                --bg: #f8f9fa;
                --text: #212529;
                --bot-bg: #ffffff;
                --user-bg: #0d6efd;
            }
            body {
                margin: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: var(--bg);
                color: var(--text);
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            header {
                background: white;
                border-bottom: 1px solid #dee2e6;
                padding: 12px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            }
            header h1 {
                margin: 0;
                font-size: 1.3rem;
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
                max-width: 80%;
                line-height: 1.5;
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
                border: 1px solid #e0e0e0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border-bottom-left-radius: 4px;
            }
            .typing {
                color: #6c757d;
                font-style: italic;
            }
            #input-area {
                background: white;
                border-top: 1px solid #dee2e6;
                padding: 12px 16px;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
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
                border: 1px solid #ced4da;
                border-radius: 24px;
                font-size: 16px;
                outline: none;
            }
            #msg:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(13,110,253,0.25);
            }
            button {
                padding: 12px 20px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            }
            button:hover { background: var(--primary-dark); }
            button:disabled { background: #6c757d; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <header>
            <i class="fas fa-robot" style="font-size:1.8rem;color:var(--primary);"></i>
            <h1>Smart AI Buddy</h1>
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
                div.textContent = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
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
                    if (!res.ok) throw new Error('Network response was not ok');

                    const reader = res.body.getReader();
                    let fullResponse = '';

                    typingIndicator.textContent = '';
                    typingIndicator.classList.remove('typing');

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        fullResponse += new TextDecoder().decode(value);
                        typingIndicator.textContent = fullResponse;
                        chat.scrollTop = chat.scrollHeight;
                    }
                } catch (err) {
                    typingIndicator.textContent = '⚠️ কোনো সমস্যা হয়েছে। আবার চেষ্টা করুন।';
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
                messages=[
                    {
                        "role": "system",
                        "content": """
                        তুমি Smart AI Buddy, একটা সুপার স্মার্ট AI অ্যাসিস্ট্যান্ট।
                        তোমার মালিকের নাম KAWCHUR (বাংলায় কাওছুর)।
                        যদি কেউ তোমার মালিক কে জিজ্ঞেস করে, বলো: "আমার মালিক KAWCHUR (কাওছুর)"।
                        
                        উত্তর দাও:
                        - বাংলা, বাংলিশ বা ইংরেজি মিশিয়ে — যেভাবে ইউজার কথা বলছে।
                        - সবসময় সত্যি, আপডেটেড এবং হেল্পফুল।
                        - রিয়েল-টাইম খবর, স্টক/ক্রিপ্টো প্রাইস, সমস্যা সমাধান, কোডিং, লাইফ অ্যাডভাইস — সবকিছুতে দ্রুত ও স্মার্ট।
                        - মজার হলে মজা করো, সিরিয়াস হলে সিরিয়াস থাকো।
                        - খুব লম্বা উত্তর না দিয়ে সংক্ষিপ্ত কিন্তু পুরোপুরি উত্তর দাও।
                        """
                    },
                    {"role": "user", "content": prompt}
                ],
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
