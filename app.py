from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime, timedelta
import pytz
import json
import random
import re      # ➕ Math: Regex এর জন্য
import math    # ➕ Math: অংকের লাইব্রেরি

# ==========================================
# 🔹 Flux AI (Ultimate Fix - Build 18.2.3) 🛡️
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  # Fixed capitalization for better display
OWNER_NAME_BN = "কাওছুর" # Fixed Bangla spelling
VERSION = "18.2.3"
ADMIN_PASSWORD = "7rx9x2c0" 

# ⚠️ Links Restored
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
        "date": now_dhaka.strftime("%d %B, %Y (%A)"),
        "year": now_dhaka.year
    }

# 🧮 FLUX INSTRUMENTS (MATH ENGINE) - INTELLIGENT MODE 🚀
def solve_math_problem(text):
    try:
        # ১. চিহ্ন রিপ্লেস করা (যাতে × এবং ÷ চিনতে পারে)
        # এখানে আমরা × কে * এবং ÷ কে / বানিয়ে দিচ্ছি
        normalized_text = text.replace("×", "*").replace("÷", "/")
        
        # ২. টেক্সট থেকে শুধু অংক বের করা (Regex ব্যবহার করে)
        # এটি "Please solve" বা "অংক করো" বাদ দিয়ে শুধু সংখ্যা ও চিহ্ন নেবে
        # আমরা খুঁজছি: সংখ্যা, দশমিক, এবং অপারেটর এর একটি সিকোয়েন্স
        match = re.search(r'[\d][\d\.\+\-\*\/\(\)\s\^]*[\d]', normalized_text)
        
        if not match:
            return None
            
        expression = match.group(0).strip()
        
        # ৩. যদি খুব ছোট কিছু হয় বা কোনো অপারেটর না থাকে, তবে ইগনোর করো
        # যেমন শুধু "2026" বা ফোন নম্বর যাতে অংক না ভাবে
        if len(expression) < 3 or not any(op in expression for op in ['+', '-', '*', '/']):
            return None

        # ৪. ক্যালকুলেশন (নিরাপদভাবে)
        result = eval(expression, {"__builtins__": None}, {"math": math})
        
        # ৫. উত্তর সাজানো
        if result == int(result):
            return f"{int(result):,}" 
        return f"{result:,.2f}" # দশমিকের পর ২ ঘর পর্যন্ত দেখাবে
    except:
        return None

SUGGESTION_POOL = [
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics simply"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Plan a 3-day trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Creative business ideas"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML & CSS basics"},
    {"icon": "fas fa-guitar", "text": "Write a song lyric about rain"},
    {"icon": "fas fa-camera", "text": "Photography tips for beginners"},
    {"icon": "fas fa-paint-brush", "text": "Generate a futuristic city image"},
    {"icon": "fas fa-calculator", "text": "Solve this puzzle: 2 + 2 * 4"}
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

        <style>
            :root {{
                --bg: #0b0f19;
                --sidebar: #111827;
                --text: #f3f4f6;
                --text-secondary: #9ca3af;
                --input-bg: #1f2937;
                --border: #374151;
                --accent: #3b82f6;
                --chat-accent: #3b82f6;
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
                --danger: #ef4444;
                --success: #10b981;
                --shadow-soft: 0 10px 40px -10px rgba(0,0,0,0.5);
                --shadow-input: 0 5px 20px rgba(0,0,0,0.3);
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f9fafb;
                --text: #111827;
                --text-secondary: #6b7280;
                --input-bg: #f3f4f6;
                --border: #e5e7eb;
                --accent: #2563eb;
                --chat-accent: #2563eb;
                --bot-icon: linear-gradient(135deg, #2563eb, #7c3aed);
                --shadow-soft: 0 10px 40px -10px rgba(0,0,0,0.1);
                --shadow-input: 0 5px 20px rgba(0,0,0,0.05);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 5px 0 25px rgba(0,0,0,0.3);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 10px; color: var(--text); letter-spacing: -0.5px; }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: var(--input-bg); color: var(--text); border: 1px solid var(--border);
                border-radius: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px;
                margin-bottom: 20px; transition: all 0.2s ease; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .new-chat-btn:active {{ transform: scale(0.98); border-color: var(--accent); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{
                padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); 
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.95rem;
                transition: background 0.2s; display: flex; align-items: center; gap: 10px; font-weight: 500;
            }}
            .history-item:active {{ background: var(--input-bg); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 10px; }}
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 5px; border-radius: 12px; border: 1px solid var(--border); }}
            .theme-btn {{ flex: 1; padding: 10px; border-radius: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-weight: 600; transition: 0.3s; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}

            .about-section {{ 
                display: none; background: var(--input-bg); padding: 20px; border-radius: 16px;
                margin-top: 5px; font-size: 0.9rem; text-align: center; border: 1px solid var(--border);
                box-shadow: var(--shadow-soft); animation: fadeIn 0.3s;
            }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.3rem; margin: 0 12px; transition: 0.2s; display: inline-block; }}
            .about-link:hover {{ color: var(--accent); transform: scale(1.1); }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 18px;
                background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid var(--border); position: absolute; top: 0; left: 0; right: 0; z-index: 100;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.9); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 80px 18px 140px 18px; display: flex; flex-direction: column; gap: 24px; }}

            /* WELCOME SCREEN */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 100%; text-align: center; 
                padding-top: 80px; padding-bottom: 100px;
            }}
            .icon-wrapper {{ 
                width: 80px; height: 80px; background: var(--bot-icon); border-radius: 26px; 
                display: flex; align-items: center; justify-content: center; font-size: 2.6rem; color: white; 
                margin-bottom: 25px; box-shadow: 0 10px 40px rgba(59, 130, 246, 0.4);
                animation: floatPulse 4s ease-in-out infinite;
            }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); margin-bottom: 40px; font-size: 1.05rem; max-width: 80%; }}

            /* SUGGESTIONS */
            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; width: 100%; max-width: 700px; }}
            .chip {{
                padding: 16px 20px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 18px;
                cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
                font-weight: 500; font-size: 0.92rem; display: flex; align-items: center; gap: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            body.light .chip {{ background: rgba(0,0,0,0.02); }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: var(--shadow-soft); }}
            .chip:active {{ transform: scale(0.96); background: var(--input-bg); }}
            .chip i {{ color: var(--text); font-size: 1.1rem; opacity: 0.8; }}

            /* MESSAGES */
            .message-wrapper {{ display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.3s ease; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            .avatar {{ width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .bot-avatar {{ background: var(--bot-icon); color: white; }}
            .user-avatar {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; max-width: 85%; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; }}
            .sender-name {{ font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 5px; font-weight: 600; padding-left: 2px; }}
            .message-wrapper.user .sender-name {{ display: none; }}

            /* 🔥 CSS FIX FOR OVERFLOW 🔥 */
            .bubble {{ 
                padding: 12px 18px; border-radius: 22px; font-size: 1.02rem; line-height: 1.6; 
                word-wrap: break-word;          /* Old standard */
                word-break: break-word;         /* Important for long numbers */
                overflow-wrap: break-word;      /* Modern standard */
                white-space: pre-wrap;          /* Preserves spaces but wraps */
            }}
            .bot .bubble {{ background: transparent; padding: 0; width: 100%; }}
            .user .bubble {{ background: var(--input-bg); border-radius: 22px 6px 22px 22px; color: var(--text); box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid var(--border); }}
            
            .bubble strong {{ color: var(--chat-accent); font-weight: 700; }}
            .bubble img {{ max-width: 100%; border-radius: 16px; margin-top: 10px; cursor: pointer; box-shadow: var(--shadow-soft); border: 1px solid var(--border); }}
            .img-brand {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 8px; display: flex; align-items: center; gap: 6px; font-weight: 600; opacity: 0.8; }}

            /* INPUT AREA */
            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 20px;
                background: linear-gradient(to top, var(--bg) 85%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 850px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 28px; padding: 10px 10px 10px 24px;
                border: 1px solid var(--border); box-shadow: var(--shadow-input); transition: all 0.3s ease;
            }}
            .input-box:focus-within {{ border-color: var(--accent); transform: translateY(-3px); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }}
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1.05rem; max-height: 160px; resize: none; padding: 12px 0; font-family: inherit;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 46px; height: 46px;
                border-radius: 50%; cursor: pointer; margin-left: 12px; margin-bottom: 2px;
                display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s;
            }}
            .send-btn:hover {{ transform: rotate(-10deg) scale(1.05); background: var(--accent); color: white; }}
            .send-btn:active {{ transform: scale(0.9); }}

            /* MODAL STYLES */
            .modal-overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.75); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(6px);
            }}
            .modal-box {{
                background: var(--sidebar); border: 1px solid var(--border); padding: 30px; border-radius: 24px; width: 90%; max-width: 350px; text-align: center; box-shadow: var(--shadow-soft);
            }}
            .modal-title {{ font-size: 1.4rem; margin-bottom: 10px; font-weight: 700; color: var(--text); }}
            .modal-desc {{ color: var(--text-secondary); margin-bottom: 25px; line-height: 1.5; }}
            
            .btn-modal {{ padding: 14px; border-radius: 14px; border: none; font-weight: 700; cursor: pointer; flex: 1; margin: 0 6px; font-size: 0.95rem; transition: 0.2s; }}
            .btn-cancel {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            .btn-delete {{ background: var(--danger); color: white; box-shadow: 0 5px 20px rgba(239, 68, 68, 0.3); }}
            .btn-confirm {{ background: var(--success); color: white; box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3); }}
            .btn-modal:hover {{ transform: translateY(-2px); }}

            /* ADMIN PANEL */
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
            .stat-box {{ background: var(--input-bg); padding: 15px; border-radius: 12px; border: 1px solid var(--border); }}
            .stat-val {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); }}
            .stat-label {{ font-size: 0.8rem; color: var(--text-secondary); }}

            @keyframes floatPulse {{
                0%, 100% {{ transform: translateY(0); box-shadow: 0 10px 40px rgba(59, 130, 246, 0.4); }}
                50% {{ transform: translateY(-12px); box-shadow: 0 20px 60px rgba(59, 130, 246, 0.7); }}
            }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
            
            .typing {{ display: flex; gap: 6px; padding: 12px 0; }}
            .dot {{ width: 8px; height: 8px; background: var(--text-secondary); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            
            pre {{ background: #0d1117 !important; padding: 20px; border-radius: 16px; overflow-x: auto; border: 1px solid var(--border); box-shadow: var(--shadow-soft); }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.9rem; }}
        </style>
    </head>
    <body class="dark">
        
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title">Clear History?</div>
                <div class="modal-desc">This will permanently delete all your conversations.</div>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal('delete-modal')">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete All</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title"><i class="fas fa-shield-alt"></i> Admin Access</div>
                <div class="modal-desc">Enter authorization code</div>
                <input type="password" id="admin-pass" style="width:100%; padding:12px; border-radius:10px; border:1px solid var(--border); background:var(--bg); color:var(--text); margin-bottom:10px; outline:none;" placeholder="Password">
                <div id="admin-error-msg" style="color:var(--danger); font-size:0.9rem; margin-bottom:15px; display:none; font-weight:600;"><i class="fas fa-exclamation-circle"></i> Invalid Password</div>
                <div style="display:flex;">
                    <button class="btn-modal btn-cancel" onclick="closeModal('admin-auth-modal')">Cancel</button>
                    <button class="btn-modal btn-confirm" onclick="verifyAdmin()">Login</button>
                </div>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box" style="max-width: 400px;">
                <div class="modal-title">Admin Panel</div>
                <div class="stats-grid">
                    <div class="stat-box"><div class="stat-val" id="stat-msgs">0</div><div class="stat-label">Total Messages</div></div>
                    <div class="stat-box"><div class="stat-val" id="stat-uptime">0s</div><div class="stat-label">Server Uptime</div></div>
                    <div class="stat-box"><div class="stat-val" style="font-size:1rem;">{VERSION}</div><div class="stat-label">App Version</div></div>
                    <div class="stat-box"><div class="stat-val" style="font-size:1rem; color:var(--text);">{OWNER_NAME}</div><div class="stat-label">Developer</div></div>
                </div>
                <div class="modal-desc" id="system-status-text" style="font-weight:600;">System is currently ONLINE</div>
                <button class="btn-modal btn-delete" id="btn-toggle-sys" onclick="toggleSystem()" style="width:100%; margin:0;">Turn System OFF</button>
                <button class="btn-modal btn-cancel" onclick="closeModal('admin-panel-modal')" style="width:100%; margin:10px 0 0 0;">Close Panel</button>
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
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>
                
                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                
                <div id="about-info" class="about-section">
                    <strong style="font-size:1.1rem; display:block; margin-bottom:5px;">{APP_NAME} v{VERSION}</strong>
                    <small style="color:var(--text-secondary)">Dev: {OWNER_NAME}</small><br>
                    <div style="margin:15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="display:block; margin-top:5px; font-weight:600; opacity:0.7;">All rights reserved by {OWNER_NAME} &copy; 2026</small>
                </div>
                <div class="history-item" onclick="openDeleteModal('delete-modal')" style="color:#ef4444;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 8px;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.3rem; letter-spacing: -0.5px;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 8px;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your intelligent AI companion.</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message {APP_NAME}..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            
            const allSuggestions = {suggestions_json};
            
            let chats = JSON.parse(localStorage.getItem('flux_v18_history')) || [];
            let userName = localStorage.getItem('flux_user_name'); 
            let awaitingName = false; 

            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const welcomeScreen = document.getElementById('welcome');
            const msgInput = document.getElementById('msg');
            const deleteModal = document.getElementById('delete-modal');
            const overlay = document.querySelector('.overlay');

            const accentColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
            renderHistory();
            renderSuggestions(); 

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ sidebar.classList.toggle('closed'); overlay.style.display = sidebar.classList.contains('closed') ? 'none' : 'block'; }}

            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random());
                const selected = shuffled.slice(0, 4);
                let html = '';
                selected.forEach(s => {{
                    // NOTE: Escaped braces properly here
                    html += '<div class="chip" onclick="sendSuggestion(\\'' + s.text + '\\')"><i class="' + s.icon + '"></i> ' + s.text + '</div>';
                }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                const randomColor = accentColors[Math.floor(Math.random() * accentColors.length)];
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [], accent: randomColor }});
                saveData();
                renderHistory();
                renderSuggestions();
                
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                msgInput.value = '';
                resizeInput(msgInput);
            }}

            function saveData() {{ localStorage.setItem('flux_v18_history', JSON.stringify(chats)); }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = '<i class="far fa-comment-alt"></i> <span>' + (chat.title || 'New Conversation').substring(0, 22) + '</span>';
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;
                document.documentElement.style.setProperty('--chat-accent', chat.accent || 'var(--accent)');
                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none'; 
                if (chat.messages.length === 0) {{
                     chatBox.appendChild(welcomeScreen);
                     welcomeScreen.style.display = 'flex';
                }} else {{
                    chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user'));
                }}
                sidebar.classList.add('closed');
                overlay.style.display = 'none';
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function addBrandingToImages() {{
                document.querySelectorAll('.bubble img').forEach(img => {{
                    if(img.closest('.img-container')) return; 
                    const container = document.createElement('div');
                    container.className = 'img-container';
                    img.parentNode.insertBefore(container, img);
                    container.appendChild(img);
                    const branding = document.createElement('div');
                    branding.className = 'img-brand';
                    branding.innerHTML = '<i class="fas fa-bolt" style="color:var(--chat-accent)"></i> Flux AI';
                    container.appendChild(branding);
                }});
            }}

            function appendBubble(text, isUser) {{
                welcomeScreen.style.display = 'none';
                const wrapper = document.createElement('div');
                wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}">${{isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>'}}</div>`;
                const name = `<div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container">${{name}}<div class="bubble">${{marked.parse(text)}}</div></div>`;
                chatBox.appendChild(wrapper);
                if(!isUser) {{ hljs.highlightAll(); addBrandingToImages(); }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble" style="background:transparent; padding-left:0;"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div></div>`;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{ document.getElementById('typing-indicator')?.remove(); }}
            function sendSuggestion(text) {{ msgInput.value = text; sendMessage(); }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(text === '!admin') {{
                    msgInput.value = '';
                    openModal('admin-auth-modal');
                    // Reset Error Msg
                    document.getElementById('admin-error-msg').style.display = 'none';
                    return;
                }}

                if(!currentChatId) startNewChat();
                const chat = chats.find(c => c.id === currentChatId);
                
                chat.messages.push({{ role: 'user', text: text }});
                if(chat.messages.length === 1) {{ chat.title = text.substring(0, 20); renderHistory(); }}
                saveData();
                msgInput.value = '';
                appendBubble(text, true);

                if(!userName && !awaitingName) {{
                    awaitingName = true;
                    setTimeout(() => {{
                        appendBubble("Hello! Before we start, may I know your name?", false);
                    }}, 600);
                    return;
                }}
                if(awaitingName) {{
                    userName = text;
                    localStorage.setItem('flux_user_name', userName);
                    awaitingName = false;
                    setTimeout(() => {{
                        appendBubble(`Nice to meet you, ${{userName}}! How can I help you today?`, false);
                    }}, 600);
                    return;
                }}

                showTyping();
                const context = chat.messages.slice(-10).map(m => ({{ role: m.role, content: m.text }}));
                if(userName) context.unshift({{role: "system", content: "User's name is " + userName}});

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    removeTyping();
                    if(!res.ok) throw new Error("System Offline");
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
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
                    saveData();
                    hljs.highlightAll();
                    addBrandingToImages();

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ System is currently offline by Admin or connection failed.", false);
                }}
            }}

            // ADMIN & MODAL LOGIC
            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; sidebar.classList.add('closed'); overlay.style.display = 'none'; }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function openDeleteModal(id) {{ openModal(id); }}
            
            function confirmDelete() {{ localStorage.removeItem('flux_v18_history'); location.reload(); }}

            async function verifyAdmin() {{
                const pass = document.getElementById('admin-pass').value;
                const errorMsg = document.getElementById('admin-error-msg');
                
                if(pass === '{ADMIN_PASSWORD}') {{
                    errorMsg.style.display = 'none';
                    closeModal('admin-auth-modal');
                    openModal('admin-panel-modal');
                    document.getElementById('admin-pass').value = '';
                    try {{
                        const res = await fetch('/admin/stats');
                        const data = await res.json();
                        document.getElementById('stat-uptime').innerText = data.uptime;
                        document.getElementById('stat-msgs').innerText = data.total_messages;
                        updateSysBtn(data.active);
                    }} catch(e) {{ alert('Error fetching stats'); }}
                }} else {{
                    // 🔒 SECURE ERROR: No alert box, just red text
                    errorMsg.style.display = 'block';
                    // Optional: Shake animation
                    const box = document.querySelector('#admin-auth-modal .modal-box');
                    box.style.transform = 'translateX(5px)';
                    setTimeout(() => box.style.transform = 'translateX(0)', 100);
                }}
            }}

            async function toggleSystem() {{
                try {{
                    const res = await fetch('/admin/toggle_system', {{ method: 'POST' }});
                    const data = await res.json();
                    updateSysBtn(data.active);
                }} catch(e) {{ alert('Error toggling system'); }}
            }}

            function updateSysBtn(isActive) {{
                const btn = document.getElementById('btn-toggle-sys');
                const txt = document.getElementById('system-status-text');
                if(isActive) {{
                    btn.innerText = "Turn System OFF";
                    btn.style.background = "var(--danger)";
                    txt.innerText = "System is ONLINE";
                    txt.style.color = "var(--success)";
                }} else {{
                    btn.innerText = "Turn System ON";
                    btn.style.background = "var(--success)";
                    txt.innerText = "System is OFFLINE";
                    txt.style.color = "var(--danger)";
                }}
            }}

            msgInput.addEventListener('keypress', e => {{ if(e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); sendMessage(); }} }});
        </script>
    </body>
    </html>
