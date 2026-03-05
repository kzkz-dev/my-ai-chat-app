from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import re
import math

# ==========================================
# 🔹 Flux AI (Ultimate Intelligence - Build 32.0.0) 🧠
# 🔥 NEW: FLUX VISION (IMAGE) & PDF DOC READER 📎📸
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "32.0.0"
ADMIN_PASSWORD = "7rx9x2c0" 

# Links
FACEBOOK_URL = "https://www.facebook.com/share/1CBWMUaou9/"
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"      

# Stats
SERVER_START_TIME = time.time()
TOTAL_MESSAGES = 0
SYSTEM_ACTIVE = True 

app = Flask(__name__)
app.secret_key = os.urandom(24)

GROQ_KEYS = [k.strip() for k in os.environ.get("GROQ_KEYS", "").split(",") if k.strip()]
current_key_index = 0

if not GROQ_KEYS:
    print("⚠️ WARNING: No Groq keys found. Please add them in Render Environment Variables.")

def get_groq_client():
    global current_key_index
    if not GROQ_KEYS: return None
    key = GROQ_KEYS[current_key_index % len(GROQ_KEYS)]
    return Groq(api_key=key)

def get_uptime():
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return str(timedelta(seconds=uptime_seconds))

def get_current_context(): 
    tz_dhaka = pytz.timezone('Asia/Dhaka')
    now_dhaka = datetime.now(tz_dhaka)
    now_utc = datetime.now(pytz.utc)
    return {
        "time_utc": now_utc.strftime("%I:%M %p"),
        "time_local": now_dhaka.strftime("%I:%M %p"),
        "date": now_dhaka.strftime("%d %B, %Y")
    }

# 🧮 MATH ENGINE
def solve_math_problem(text):
    try:
        clean_text = text.replace(" ", "").replace("=", "").replace("?", "").replace(",", "")
        allowed_chars = set("0123456789.+-*/()xX÷^")
        if not set(clean_text).issubset(allowed_chars): return None
        if len(clean_text) < 3 or not any(op in clean_text for op in ['+', '-', '*', '/', 'x', '÷', '^']): return None
        expression = clean_text.replace("x", "*").replace("X", "*").replace("÷", "/").replace("^", "**")
        result = eval(expression, {"__builtins__": None}, {"math": math})
        if result == int(result): return f"{int(result):,}" 
        return f"{result:,.4f}" 
    except: return None

SUGGESTION_POOL = [
    {"icon": "fas fa-image", "text": "Upload an image to analyze"},
    {"icon": "fas fa-file-pdf", "text": "Upload a PDF to summarize"},
    {"icon": "fas fa-gamepad", "text": "Make a Tic-Tac-Toe game"},
    {"icon": "fas fa-calculator", "text": "Create a Neon Calculator"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-lightbulb", "text": "Business ideas for students"}
]

@app.route("/")
def home():
    suggestions_json = json.dumps(SUGGESTION_POOL)
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{APP_NAME}</title>
        
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark-reasonable.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>

        <style>
            :root {{
                --bg-gradient: radial-gradient(circle at 10% 20%, rgb(10, 10, 25) 0%, rgb(5, 5, 10) 90%);
                --glass-bg: rgba(20, 20, 35, 0.65);
                --sidebar-bg: rgba(15, 15, 30, 0.95);
                --glass-border: rgba(255, 255, 255, 0.08);
                --text: #e0e6ed;
                --text-secondary: #94a3b8;
                --accent: #00f3ff;
                --accent-glow: 0 0 10px rgba(0, 243, 255, 0.5);
                --bot-grad: linear-gradient(135deg, #00f3ff 0%, #bc13fe 100%);
                --user-grad: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
                --danger: #ff0f7b;
                --success: #00ff87;
                --terminal-green: #0f0;
            }}

            body.light {{
                --bg-gradient: #f8fafc;
                --glass-bg: #ffffff;
                --sidebar-bg: #ffffff;
                --text: #1e293b;
                --text-secondary: #64748b;
                --glass-border: #e2e8f0;
                --accent: #2563eb;
                --bot-grad: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
                --user-grad: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
                --terminal-green: #00a000;
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg-gradient); color: var(--text); font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; transition: background 0.4s ease; }}

            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }}
            
            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid var(--glass-border); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.4s ease; position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 10px 0 30px rgba(0,0,0,0.3); background: var(--sidebar-bg); }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid var(--glass-border); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; transition: all 0.4s; }}
            .new-chat-btn:active {{ transform: scale(0.97); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{ padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; transition: all 0.3s; display: flex; align-items: center; gap: 10px; font-weight: 500; }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; transition: all 0.4s ease; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 8px; transition: all 0.3s ease; }}
            .theme-btn.active {{ background: rgba(125,125,125,0.2); color: var(--text); }}

            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: rgba(15, 15, 30, 0.0); backdrop-filter: blur(10px); border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100; transition: background 0.4s ease; }}
            body.light header {{ background: rgba(255, 255, 255, 0.5); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; overflow-x: hidden; }}

            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 100px; padding-bottom: 60px; }}
            .icon-wrapper {{ width: 80px; height: 80px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: white; margin-bottom: 25px; box-shadow: 0 0 30px rgba(0, 243, 255, 0.15); animation: levitate 4s ease-in-out infinite; }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 30px; letter-spacing: -0.5px; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; width: 100%; max-width: 750px; padding: 0 10px; }}
            .chip {{ padding: 14px 16px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 16px; cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.4s; font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .chip i {{ color: var(--accent); font-size: 1.1rem; opacity: 0.9; }}

            .message-wrapper {{ display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1rem; transition: all 0.3s ease; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; flex: 1; min-width: 0; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; flex: none; max-width: 85%; }}
            
            .bubble {{ padding: 12px 18px; border-radius: 20px; font-size: 1rem; line-height: 1.6; word-wrap: break-word; overflow-wrap: break-word; position: relative; max-width: 100%; box-sizing: border-box; }}
            .bot .bubble {{ background: transparent; padding: 0; color: var(--text); overflow-x: auto; }}
            .user .bubble {{ background: var(--user-grad); border-radius: 20px 4px 20px 20px; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); display: inline-block; width: fit-content; }}
            
            .bubble strong {{ color: var(--accent); font-weight: 700; }}
            body.light .bubble strong {{ color: #2563eb; }}
            .bubble img {{ max-width: 100%; border-radius: 16px; margin-top: 12px; cursor: pointer; border: 1px solid var(--glass-border); }}

            /* DEEP-BRAIN PROCESSOR CSS */
            .brain-container {{ width: 100%; background: #000; border: 1px solid var(--glass-border); border-radius: 16px; padding: 20px; font-family: 'Fira Code', monospace; position: relative; overflow: hidden; margin-bottom: 15px; box-shadow: inset 0 0 20px rgba(0,255,0,0.05); box-sizing: border-box; }}
            .brain-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 15px; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 10px; }}
            .brain-icon {{ color: var(--terminal-green); font-size: 1.2rem; animation: pulse 1.5s infinite; }}
            .brain-title {{ color: var(--terminal-green); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }}
            .brain-logs {{ font-size: 0.8rem; color: #a3a3a3; line-height: 1.8; min-height: 60px; }}
            .log-line {{ animation: typeText 0.1s linear forwards; opacity: 0; }}
            .log-line::before {{ content: "> "; color: var(--terminal-green); }}

            /* FLUX ARTIFACTS CSS */
            .artifact-container {{ width: 100%; background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 16px; overflow: hidden; margin-top: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); box-sizing: border-box; }}
            .artifact-header {{ background: rgba(125,125,125,0.1); padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--glass-border); flex-wrap: wrap; gap: 10px; }}
            .artifact-title {{ display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; color: var(--text); }}
            .artifact-title i {{ color: #facc15; }}
            .artifact-actions button {{ background: var(--accent); border: none; color: black; font-weight: 600; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 0 10px rgba(0, 243, 255, 0.3); }}
            .artifact-actions button:hover {{ transform: scale(1.05); box-shadow: 0 0 15px rgba(0, 243, 255, 0.6); }}
            .artifact-content {{ width: 100%; height: 400px; position: relative; background: #fff; }}
            .artifact-content iframe {{ width: 100%; height: 100%; border: none; background: #fff; }}

            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; margin-top: 15px; box-sizing: border-box; max-width: 100%; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            .copy-btn {{ position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.15); color: white; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; transition: 0.3s; }}
            .copy-btn:hover {{ background: var(--accent); color: black; }}

            /* 🔥 INPUT AREA & ATTACHMENT UI 🔥 */
            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; transition: all 0.4s ease; flex-direction: column; align-items: center; }}
            
            #attachment-preview {{ display: none; width: 100%; max-width: 850px; margin-bottom: 10px; padding: 10px; background: rgba(0, 243, 255, 0.1); border: 1px solid var(--accent); border-radius: 12px; font-size: 0.85rem; color: var(--text); align-items: center; justify-content: space-between; box-sizing: border-box; animation: fadeIn 0.3s; }}
            .preview-close {{ cursor: pointer; color: var(--danger); font-size: 1.2rem; }}
            
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 28px; padding: 10px 10px 10px 15px; border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); transition: all 0.3s ease; }}
            .input-box:focus-within {{ border-color: var(--accent); box-shadow: 0 0 20px rgba(0, 243, 255, 0.1); }}
            
            .attach-btn {{ background: transparent; border: none; color: var(--text-secondary); font-size: 1.3rem; padding: 10px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; justify-content: center; margin-bottom: 2px; }}
            .attach-btn:hover {{ color: var(--accent); transform: scale(1.1); }}
            
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1.05rem; max-height: 150px; resize: none; padding: 10px 10px; margin-bottom: 2px; font-family: inherit; line-height: 1.4; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 8px; margin-bottom: 0px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; flex-shrink: 0; }}
            .send-btn:hover {{ transform: scale(1.1); background: var(--accent); color: black; }}

            .energy-ball {{ position: fixed; width: 18px; height: 18px; background: var(--accent); border-radius: 50%; pointer-events: none; z-index: 9999; box-shadow: 0 0 15px var(--accent), 0 0 30px white; animation: shootUp 0.6s cubic-bezier(0.25, 1, 0.5, 1) forwards; }}

            #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; backdrop-filter: blur(8px); }}
            .preview-box {{ width: 95%; height: 90%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0,0,0,0.5); animation: popIn 0.3s; }}
            .preview-header {{ padding: 12px 20px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}
            iframe.fullscreen-iframe {{ flex: 1; border: none; width: 100%; height: 100%; box-sizing: border-box; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.9); }} to {{ opacity: 1; transform: scale(1); }} }}
            @keyframes shootUp {{ 0% {{ bottom: 80px; left: 50%; opacity: 1; transform: scale(1); }} 100% {{ bottom: 80%; left: 50%; opacity: 0; transform: scale(0.2); }} }}
            
            .typing {{ display: flex; gap: 6px; padding: 12px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; transition: all 0.4s ease; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700; color:#111;">Live App Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:6px 14px; border-radius:6px; cursor:pointer; font-weight:600;">Close</button>
                </div>
                <iframe id="fullscreen-frame" class="fullscreen-iframe"></iframe>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div style="font-size:0.75rem; font-weight: 700; color:var(--text-secondary); margin-bottom:12px; letter-spacing: 1px; opacity:0.8;">RECENT</div>
            <div class="history-list" id="history-list"></div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer; padding: 8px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.4rem; letter-spacing: -0.5px; background: linear-gradient(to right, var(--text), var(--text-secondary)); -webkit-background-clip: text; color: transparent;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem; cursor:pointer; padding: 8px;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div id="attachment-preview">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <i id="attach-icon" class="fas fa-file"></i>
                        <span id="attach-name" style="font-weight:600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;">file.pdf</span>
                    </div>
                    <i class="fas fa-times-circle preview-close" onclick="clearAttachment()"></i>
                </div>

                <div class="input-box">
                    <input type="file" id="file-upload" accept="image/*, application/pdf" style="display: none;">
                    <label for="file-upload" class="attach-btn"><i class="fas fa-paperclip"></i></label>

                    <textarea id="msg" placeholder="Ask Flux or upload a file..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            // Ensure PDF.js worker is set up
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v32_history')) || [];
            let userName = localStorage.getItem('flux_user_name_fixed'); 
            let awaitingName = false; 

            // 📎 Attachment Variables
            let attachedImageBase64 = null;
            let attachedPdfText = null;

            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const overlay = document.querySelector('.overlay');

            renderHistory();
            renderSuggestions(); 

            // 🌌 Background Canvas
            const canvas = document.getElementById('neuro-bg');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function resizeCanvas() {{ canvas.width = window.innerWidth; canvas.height = window.innerHeight; }}
            window.addEventListener('resize', resizeCanvas); resizeCanvas();

            class Particle {{
                constructor() {{ this.x = Math.random() * canvas.width; this.y = Math.random() * canvas.height; this.vx = (Math.random() - 0.5) * 0.5; this.vy = (Math.random() - 0.5) * 0.5; this.size = Math.random() * 2; }}
                update() {{ this.x += this.vx; this.y += this.vy; if(this.x < 0 || this.x > canvas.width) this.vx *= -1; if(this.y < 0 || this.y > canvas.height) this.vy *= -1; }}
                draw() {{ ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--accent'); ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }}
            }}
            for(let i=0; i<60; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach((p, index) => {{
                    p.update(); p.draw();
                    for(let j=index; j<particles.length; j++) {{
                        const dx = p.x - particles[j].x; const dy = p.y - particles[j].y; const dist = Math.sqrt(dx*dx + dy*dy);
                        if(dist < 100) {{
                            const accentColor = getComputedStyle(document.body).getPropertyValue('--accent');
                            ctx.strokeStyle = accentColor.replace('rgb', 'rgba').replace(')', ', ' + (1 - dist/100) * 0.2 + ')');
                            ctx.lineWidth = 0.5; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(particles[j].x, particles[j].y); ctx.stroke();
                        }}
                    }}
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}
            
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
                const selected = shuffled.slice(0, 4);
                let html = '';
                selected.forEach(s => {{ html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>'; }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData(); renderHistory(); renderSuggestions(); clearAttachment();
                chatBox.innerHTML = ''; chatBox.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed'); overlay.style.display = 'none'; msgInput.value = ''; resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v32_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Conversation').substring(0, 22) + '</span>';
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                chatBox.innerHTML = ''; welcomeScreen.style.display = 'none'; clearAttachment();
                if (chat.messages.length === 0) {{ chatBox.appendChild(welcomeScreen); welcomeScreen.style.display = 'flex'; }} 
                else {{ chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false)); }}
                sidebar.classList.add('closed'); overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if (pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button'); btn.className = 'copy-btn'; btn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    btn.onclick = () => {{ navigator.clipboard.writeText(pre.querySelector('code').innerText); btn.innerHTML = '<i class="fas fa-check"></i> Copied'; setTimeout(() => btn.innerHTML = '<i class="fas fa-copy"></i> Copy', 2000); }};
                    pre.appendChild(btn);
                }});
            }}

            function checkForArtifacts(text, bubble) {{
                const codeMatch = text.match(/```html([\\s\\S]*?)```/);
                if(codeMatch) {{
                    const code = codeMatch[1];
                    if (!bubble.querySelector('.artifact-container')) {{
                        const artifactDiv = document.createElement('div');
                        artifactDiv.className = 'artifact-container';
                        artifactDiv.innerHTML = `
                            <div class="artifact-header">
                                <div class="artifact-title"><i class="fas fa-layer-group"></i> Live App Preview</div>
                                <div class="artifact-actions">
                                    <button onclick="openFullscreenPreview(this)" data-code="${{encodeURIComponent(code)}}"><i class="fas fa-play"></i> Fullscreen</button>
                                </div>
                            </div>
                            <div class="artifact-content"><iframe srcdoc="${{code.replace(/"/g, '&quot;')}}"></iframe></div>
                        `;
                        bubble.appendChild(artifactDiv);
                    }}
                }}
            }}

            window.openFullscreenPreview = function(btn) {{
                const code = decodeURIComponent(btn.getAttribute('data-code'));
                document.getElementById('preview-modal').style.display = 'flex';
                document.getElementById('fullscreen-frame').srcdoc = code;
            }};
            function closePreview() {{ document.getElementById('preview-modal').style.display = 'none'; }}

            function playSentAnimation() {{
                const ball = document.createElement('div'); ball.className = 'energy-ball'; ball.style.left = '50%';
                document.body.appendChild(ball); setTimeout(() => ball.remove(), 600);
            }}

            // 📎 FILE UPLOAD LOGIC 📎
            document.getElementById('file-upload').addEventListener('change', async function(e) {
                const file = e.target.files[0];
                if(!file) return;

                const preview = document.getElementById('attachment-preview');
                const nameSpan = document.getElementById('attach-name');
                const icon = document.getElementById('attach-icon');
                
                nameSpan.innerText = "Processing " + file.name + "...";
                preview.style.display = 'flex';
                attachedImageBase64 = null;
                attachedPdfText = null;

                if(file.type.startsWith('image/')) {
                    icon.className = 'fas fa-image';
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        attachedImageBase64 = event.target.result.split(',')[1];
                        nameSpan.innerText = file.name;
                    };
                    reader.readAsDataURL(file);
                } 
                else if(file.type === 'application/pdf') {
                    icon.className = 'fas fa-file-pdf';
                    try {
                        const arrayBuffer = await file.arrayBuffer();
                        const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;
                        let fullText = '';
                        for (let i = 1; i <= pdf.numPages; i++) {
                            const page = await pdf.getPage(i);
                            const textContent = await page.getTextContent();
                            fullText += textContent.items.map(item => item.str).join(' ') + '\n';
                        }
                        attachedPdfText = fullText;
                        nameSpan.innerText = file.name + " (Ready)";
                    } catch (err) {
                        nameSpan.innerText = "Error reading PDF";
                    }
                } else {
                    nameSpan.innerText = "Unsupported Format";
                }
                e.target.value = ''; // clear input
            });

            function clearAttachment() {
                attachedImageBase64 = null;
                attachedPdfText = null;
                document.getElementById('attachment-preview').style.display = 'none';
            }

            function appendBubble(text, isUser, animate=true) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container">${{name}}<div class="bubble"></div></div>`;
                chatBox.appendChild(wrapper);
                
                const bubble = wrapper.querySelector('.bubble');
                bubble.innerHTML = marked.parse(text);
                
                if(!isUser) {{ hljs.highlightAll(); addCopyButtons(); checkForArtifacts(text, bubble); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showDeepBrainThinking(isVision=false) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.id = 'typing-indicator'; wrapper.className = 'message-wrapper bot';
                
                let title = isVision ? "Vision Core Active (Analyzing Image)" : "Deep-Brain Processor Active";
                
                wrapper.innerHTML = `
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="bubble-container">
                        <div class="sender-name">{APP_NAME}</div>
                        <div class="bubble" style="background:transparent; padding:0; width:100%;">
                            <div class="brain-container">
                                <div class="brain-header">
                                    <i class="fas fa-microchip brain-icon"></i>
                                    <span class="brain-title">${{title}}</span>
                                </div>
                                <div class="brain-logs" id="brain-logs"></div>
                            </div>
                        </div>
                    </div>`;
                chatBox.appendChild(wrapper); chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});

                const logs = isVision ? ["Scanning pixels...", "Extracting text...", "Processing visuals..."] : ["Analyzing query context...", "Accessing global neural network...", "Compiling logic matrix..."];
                const logContainer = document.getElementById('brain-logs');
                let i = 0;
                window.brainInterval = setInterval(() => {{
                    if(i < logs.length) {{
                        const line = document.createElement('div'); line.className = 'log-line'; line.innerText = logs[i]; logContainer.appendChild(line); i++;
                    }} else {{ clearInterval(window.brainInterval); }}
                }}, 800);
            }}

            function removeTyping() {{ if(window.brainInterval) clearInterval(window.brainInterval); document.getElementById('typing-indicator')?.remove(); }}

            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                
                // Must have text or an attachment
                if(!text && !attachedImageBase64 && !attachedPdfText) return;

                let displayMessage = text || "Sent an attachment.";
                if(attachedImageBase64) displayMessage += "\n\n*(Image attached)*";
                if(attachedPdfText) displayMessage += "\n\n*(PDF Document attached)*";

                playSentAnimation(); 

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                // Only save text to history to prevent breaking future loads
                chat.messages.push({{ role: 'user', text: displayMessage }});
                if(chat.messages.length === 1) {{ chat.title = (text || "Attachment").substring(0, 20); renderHistory(); }}
                saveData();
                msgInput.value = '';
                appendBubble(displayMessage, true);

                if(!userName && !awaitingName) {{ awaitingName = true; setTimeout(() => {{ appendBubble("Hello! I am Flux AI. What should I call you?", false); }}, 600); return; }}
                if(awaitingName) {{ userName = text; localStorage.setItem('flux_user_name_fixed', userName); awaitingName = false; setTimeout(() => {{ appendBubble(`Nice to meet you, ${{userName}}! How can I help you today?`, false); }}, 600); return; }}

                showDeepBrainThinking(!!attachedImageBase64); 
                
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                
                // Prepare Payload with Attachments
                const payload = {{
                    messages: context,
                    user_name: userName,
                    image_base64: attachedImageBase64,
                    pdf_text: attachedPdfText
                }};

                clearAttachment(); // Clear UI after sending

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }});
                    
                    removeTyping();
                    if(!res.ok) throw new Error("System Offline");
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div'); wrapper.className = 'message-wrapper bot';
                    wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    chatBox.appendChild(wrapper);
                    const bubbleDiv = wrapper.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubbleDiv.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData(); hljs.highlightAll(); addCopyButtons(); checkForArtifacts(botResp, bubbleDiv);

                }} catch(e) {{
                    removeTyping(); appendBubble("⚠️ System connection error. Please try again.", false);
                }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES
    if not SYSTEM_ACTIVE: return Response("System is currently under maintenance.", status=503)

    TOTAL_MESSAGES += 1
    data = request.json
    messages = data.get("messages", [])
    user_name = data.get("user_name", "User")
    
    # 📎 Catch attachments from Frontend
    image_base64 = data.get("image_base64")
    pdf_text = data.get("pdf_text")

    ctx = get_current_context()
    
    sys_prompt_content = f"""
    You are {APP_NAME}, a highly intelligent, creative, and elite AI assistant created by {OWNER_NAME} (Bangla: {OWNER_NAME_BN}).
    Current User Name: {user_name}.
    Current Time: {ctx['time_utc']} (UTC). Local Dhaka time is {ctx['time_local']}, Date: {ctx['date']}.
    
    RULES:
    1. CONCISE & SMART: Be highly accurate and direct.
    2. APP CREATION: Write ENTIRE HTML, CSS, and JS inside a SINGLE ```html block. 
    """

    sys_message = {"role": "system", "content": sys_prompt_content}

    # 📎 Process PDF Text Injection
    if pdf_text and messages:
        messages[-1]['content'] = f"Here is the content of an uploaded PDF document:\n\n---\n{pdf_text[:15000]}\n---\n\nUser Question/Command regarding this PDF: {messages[-1]['content']}"

    # 📎 Process Vision (Image) Logic
    use_vision_model = False
    if image_base64 and messages:
        use_vision_model = True
        user_text = messages[-1]['content']
        # Groq specific format for images
        messages[-1]['content'] = [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]

    # Switch Model based on Attachment
    target_model = "llama-3.2-11b-vision-preview" if use_vision_model else "llama-3.3-70b-versatile"

    def generate():
        global current_key_index
        attempts = 0
        max_retries = len(GROQ_KEYS) + 1 if GROQ_KEYS else 1
        
        while attempts < max_retries:
            try:
                client = get_groq_client()
                if not client: yield "⚠️ Config Error."; return
                
                stream = client.chat.completions.create(
                    model=target_model,
                    messages=[sys_message] + messages,
                    stream=True,
                    temperature=0.7, 
                    max_tokens=2048
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                current_key_index = (current_key_index + 1) % len(GROQ_KEYS)
                attempts += 1
                time.sleep(1)
        yield "⚠️ API Rate Limit or Error."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
