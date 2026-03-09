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
# 🔹 Flux AI (Ultimate Intelligence - Build 29.2.2) 🧠
# 🔥 FIXED: MOBILE OVERFLOW, RESTORED ADMIN & DEEP-BRAIN, AUTO-ANIMATION 🔥
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"  
OWNER_NAME_BN = "কাওছুর" 
VERSION = "29.2.2"
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
    {"icon": "fas fa-gamepad", "text": "Make a Tic-Tac-Toe game"},
    {"icon": "fas fa-calculator", "text": "Create a Neon Calculator"},
    {"icon": "fas fa-code", "text": "Create a login page in HTML"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Physics"},
    {"icon": "fas fa-dumbbell", "text": "30-minute home workout"},
    {"icon": "fas fa-utensils", "text": "Healthy dinner recipe"},
    {"icon": "fas fa-plane", "text": "Trip plan for Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Business ideas for students"},
    {"icon": "fas fa-calculator", "text": "Solve: 50 * 3 + 20"}
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
            body {{ 
                margin: 0; background: var(--bg-gradient); color: var(--text); 
                font-family: 'Outfit', 'Noto Sans Bengali', sans-serif; 
                height: 100vh; display: flex; overflow: hidden; 
                transition: background 0.4s ease;
            }}

            /* 🌌 NEURAL BRAIN BACKGROUND */
            #neuro-bg {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; opacity: 0.3; }}
            .glass {{ background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); }}

            /* SIDEBAR FIXED FOR DARK/LIGHT */
            #sidebar {{ width: 280px; height: 100%; display: flex; flex-direction: column; padding: 20px; border-right: 1px solid var(--glass-border); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background 0.4s ease; position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 10px 0 30px rgba(0,0,0,0.3); background: var(--sidebar-bg); }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.6rem; font-weight: 800; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); text-shadow: var(--accent-glow); }}
            .brand i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            
            .new-chat-btn {{ width: 100%; padding: 14px; background: rgba(125, 125, 125, 0.1); color: var(--text); border: 1px solid var(--glass-border); border-radius: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; margin-bottom: 20px; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}
            .new-chat-btn:active {{ transform: scale(0.97); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; padding-right: 5px; }}
            .history-item {{ padding: 12px 14px; border-radius: 12px; cursor: pointer; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.9rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; gap: 10px; font-weight: 500; }}
            .history-item:hover {{ background: rgba(125, 125, 125, 0.1); color: var(--text); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--glass-border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .about-section {{ display: none; background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 16px; margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--glass-border); animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}
            .about-section.show {{ display: block; }}
            .about-link {{ color: var(--text); font-size: 1.4rem; margin: 0 10px; transition: 0.3s; display: inline-block; }}
            .about-link:hover {{ color: var(--accent); }}

            .theme-toggles {{ display: flex; background: rgba(125,125,125,0.1); padding: 4px; border-radius: 10px; margin-bottom: 10px; transition: all 0.4s ease; }}
            .theme-btn {{ flex: 1; padding: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; border-radius: 8px; transition: all 0.3s ease; }}
            .theme-btn.active {{ background: rgba(125,125,125,0.2); color: var(--text); }}

            header {{ height: 65px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: rgba(15, 15, 30, 0.0); backdrop-filter: blur(10px); border-bottom: 1px solid var(--glass-border); position: absolute; top: 0; left: 0; right: 0; z-index: 100; transition: background 0.4s ease; }}
            body.light header {{ background: rgba(255, 255, 255, 0.5); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            #chat-box {{ flex: 1; overflow-y: auto; padding: 90px 20px 150px 20px; display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth; overflow-x: hidden; }}

            /* WELCOME SCREEN */
            .welcome-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding-top: 100px; padding-bottom: 60px; }}
            .icon-wrapper {{ width: 80px; height: 80px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 25px; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: white; margin-bottom: 25px; box-shadow: 0 0 30px rgba(0, 243, 255, 0.15); animation: levitate 4s ease-in-out infinite; }}
            .icon-wrapper i {{ background: var(--bot-grad); -webkit-background-clip: text; color: transparent; }}
            .welcome-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 30px; letter-spacing: -0.5px; }}

            .suggestions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; width: 100%; max-width: 750px; padding: 0 10px; }}
            .chip {{ padding: 14px 16px; background: rgba(125, 125, 125, 0.05); border: 1px solid var(--glass-border); border-radius: 16px; cursor: pointer; text-align: left; color: var(--text-secondary); transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); font-weight: 500; font-size: 0.9rem; display: flex; align-items: center; gap: 14px; }}
            .chip:hover {{ transform: translateY(-3px); border-color: var(--accent); color: var(--text); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .chip i {{ color: var(--accent); font-size: 1.1rem; opacity: 0.9; }}

            /* MESSAGE BUBBLES */
            .message-wrapper {{ display: flex; gap: 14px; width: 100%; max-width: 850px; margin: 0 auto; animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1rem; transition: all 0.3s ease; }}
            .bot-avatar {{ background: var(--bot-grad); color: white; }}
            .user-avatar {{ background: rgba(125,125,125,0.1); color: var(--text); border: 1px solid var(--glass-border); }}
            
            .bubble-container {{ display: flex; flex-direction: column; flex: 1; min-width: 0; }}
            .message-wrapper.user .bubble-container {{ align-items: flex-end; flex: none; max-width: 85%; }}
            
            .sender-name {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 5px; font-weight: 600; padding-left: 2px; text-transform: uppercase; }}
            .message-wrapper.user .sender-name {{ display: none; }}

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

            /* 🔥 FIXED: FLUX ARTIFACTS MOBILE RESPONSIVE 🔥 */
            .artifact-container {{ 
                width: 100%; 
                max-width: 100%; 
                background: var(--glass-bg); 
                border: 1px solid var(--glass-border); 
                border-radius: 16px; 
                overflow: hidden; 
                margin-top: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                box-sizing: border-box; 
            }}
            .artifact-header {{ background: rgba(125,125,125,0.1); padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--glass-border); flex-wrap: wrap; gap: 10px; }}
            .artifact-title {{ display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; color: var(--text); }}
            .artifact-actions button {{ background: var(--accent); border: none; color: black; font-weight: 600; padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: 0.3s; display: inline-flex; align-items: center; gap: 6px; }}
            
            .artifact-content {{ 
                width: 100%; 
                height: 380px; 
                position: relative; 
                background: #fff; 
                overflow: hidden;
            }}
            .artifact-content iframe {{ 
                width: 100%; 
                height: 100%; 
                border: none; 
                background: #fff; 
                display: block;
            }}

            pre {{ background: #0d1117 !important; padding: 18px; border-radius: 14px; overflow-x: auto; border: 1px solid var(--glass-border); position: relative; margin-top: 15px; box-sizing: border-box; max-width: 100%; }}
            code {{ font-family: 'Fira Code', monospace; font-size: 0.85rem; color: #e6edf3; }}
            .copy-btn {{ position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.15); color: white; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; transition: 0.3s; }}

            /* FIXED TEXT BOX LAYOUT */
            #input-area {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, var(--sidebar-bg) 0%, transparent 100%); display: flex; justify-content: center; z-index: 50; transition: all 0.4s ease; }}
            .input-box {{ width: 100%; max-width: 850px; display: flex; align-items: flex-end; background: var(--sidebar-bg); border-radius: 28px; padding: 10px 10px 10px 20px; border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.1); backdrop-filter: blur(20px); transition: all 0.3s ease; }}
            textarea {{ flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 1.05rem; max-height: 150px; resize: none; padding: 10px 0; margin-bottom: 2px; font-family: inherit; line-height: 1.4; }}
            .send-btn {{ background: var(--text); color: var(--sidebar-bg); border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; margin-left: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; transition: 0.3s; flex-shrink: 0; }}

            /* FULLSCREEN PREVIEW MODAL */
            #preview-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; backdrop-filter: blur(8px); }}
            .preview-box {{ width: 95%; height: 90%; background: white; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; animation: popIn 0.3s; }}
            .preview-header {{ padding: 12px 20px; background: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }}

            /* MODALS */
            .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 9999; backdrop-filter: blur(8px); }}
            .modal-box {{ background: var(--sidebar-bg); border: 1px solid var(--glass-border); padding: 30px; border-radius: 20px; width: 90%; max-width: 350px; text-align: center; color: var(--text); animation: popIn 0.3s; box-sizing: border-box; }}
            .btn-modal {{ padding: 12px; border-radius: 12px; border: none; font-weight: 600; cursor: pointer; flex: 1; margin: 0 6px; font-size: 0.9rem; }}

            @keyframes levitate {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-15px); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.9); }} to {{ opacity: 1; transform: scale(1); }} }}
            
            .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 150; display: none; }}
        </style>
    </head>
    <body class="dark">
        <canvas id="neuro-bg"></canvas>

        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title" style="font-size:1.4rem; font-weight:700; margin-bottom:10px;">Clear History?</div>
                <div class="modal-desc" style="color:var(--text-secondary); margin-bottom:25px;">This will permanently delete all your conversations.</div>
                <div style="display:flex;">
                    <button class="btn-modal" style="background:rgba(125,125,125,0.15); color:var(--text);" onclick="closeModal('delete-modal')">Cancel</button>
                    <button class="btn-modal" style="background:var(--danger); color:white;" onclick="confirmDelete()">Delete All</button>
                </div>
            </div>
        </div>

        <div id="admin-auth-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title"><i class="fas fa-shield-alt" style="color:var(--accent)"></i> Admin Access</div>
                <input type="password" id="admin-pass" style="width:100%; padding:14px; border-radius:12px; border:1px solid var(--glass-border); background:rgba(125,125,125,0.1); color:var(--text); margin:20px 0; outline:none; text-align:center;" placeholder="••••••••">
                <div id="admin-error-msg" style="color:var(--danger); font-size:0.9rem; margin-bottom:20px; display:none;">Invalid Password</div>
                <div style="display:flex;">
                    <button class="btn-modal" style="background:rgba(125,125,125,0.15); color:var(--text);" onclick="closeModal('admin-auth-modal')">Cancel</button>
                    <button class="btn-modal" style="background:var(--success); color:black;" onclick="verifyAdmin()">Login</button>
                </div>
            </div>
        </div>

        <div id="admin-panel-modal" class="modal-overlay">
            <div class="modal-box" style="max-width: 450px;">
                <div class="modal-title" style="margin-bottom:20px;">Admin Dashboard</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:25px;">
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-msgs" style="font-size:1.6rem; font-weight:700; color:var(--accent);">0</div><div style="font-size:0.8rem; opacity:0.7">TOTAL MSGS</div></div>
                    <div style="background:rgba(125,125,125,0.1); padding:15px; border-radius:14px;"><div id="stat-uptime" style="font-size:1.1rem; font-weight:700; color:var(--accent);">0s</div><div style="font-size:0.8rem; opacity:0.7">UPTIME</div></div>
                </div>
                <button class="btn-modal" id="btn-toggle-sys" onclick="toggleSystem()" style="width:100%; margin:0; padding:16px; background:var(--danger); color:white;">Turn System OFF</button>
                <button class="btn-modal" onclick="closeModal('admin-panel-modal')" style="width:100%; margin:15px 0 0 0; background:rgba(125,125,125,0.1); color:var(--text);">Close</button>
            </div>
        </div>

        <div id="preview-modal">
            <div class="preview-box">
                <div class="preview-header">
                    <span style="font-weight:700; color:#111;">Live App Preview</span>
                    <button onclick="closePreview()" style="background:#ef4444; color:white; border:none; padding:6px 14px; border-radius:6px; cursor:pointer;">Close</button>
                </div>
                <iframe id="fullscreen-frame" style="flex:1; border:none; width:100%; height:100%;"></iframe>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-plus"></i> New Chat
            </button>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i></button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i></button>
                </div>

                <div class="history-item" onclick="toggleAbout()"><i class="fas fa-info-circle"></i> App Info</div>
                <div id="about-info" class="about-section">
                    <strong>{APP_NAME} v{VERSION}</strong><br>
                    <small>Created by {OWNER_NAME}</small><br>
                    <div style="margin:10px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                </div>
                <div class="history-item" onclick="openModal('delete-modal')" style="color:#ff0f7b;"><i class="fas fa-trash-alt"></i> Delete History</div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.4rem; cursor:pointer;"><i class="fas fa-bars"></i></button>
                <span style="font-weight:800; font-size:1.4rem;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--accent); font-size:1.4rem; cursor:pointer;"><i class="fas fa-pen-to-square"></i></button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="suggestions" id="suggestion-box"></div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Ask Flux Anything..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            marked.use({{ breaks: true, gfm: true }});
            const allSuggestions = {suggestions_json};
            let chats = JSON.parse(localStorage.getItem('flux_v29_2_history')) || [];
            let currentChatId = null;

            // 🧠 NEURAL BACKGROUND
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
            for(let i=0; i<50; i++) particles.push(new Particle());
            function animateBg() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                particles.forEach((p, index) => {{
                    p.update(); p.draw();
                    for(let j=index; j<particles.length; j++) {{
                        const dx = p.x - particles[j].x; const dy = p.y - particles[j].y; const dist = Math.sqrt(dx*dx + dy*dy);
                        if(dist < 100) {{
                            ctx.strokeStyle = `rgba(0, 243, 255, ${{0.2 * (1 - dist/100)}})`;
                            ctx.lineWidth = 0.5; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(particles[j].x, particles[j].y); ctx.stroke();
                        }}
                    }}
                }});
                requestAnimationFrame(animateBg);
            }}
            animateBg();

            function setTheme(mode) {{ document.body.className = mode; }}
            function toggleAbout() {{ document.getElementById('about-info').classList.toggle('show'); }}
            function resizeInput(el) {{ el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 200) + 'px'; }}
            function toggleSidebar() {{ document.getElementById('sidebar').classList.toggle('closed'); document.querySelector('.overlay').style.display = document.getElementById('sidebar').classList.contains('closed') ? 'none' : 'block'; }}
            
            function renderSuggestions() {{
                const shuffled = allSuggestions.sort(() => 0.5 - Math.random()).slice(0, 4);
                let html = '';
                shuffled.forEach(s => {{ html += `<div class="chip" onclick="sendSuggestion('${{s.text}}')"><i class="${{s.icon}}"></i> ${{s.text}}</div>`; }});
                document.getElementById('suggestion-box').innerHTML = html;
            }}
            renderSuggestions();

            function startNewChat() {{
                currentChatId = Date.now();
                chats.unshift({{ id: currentChatId, title: "New Conversation", messages: [] }});
                saveData(); renderHistory();
                document.getElementById('chat-box').innerHTML = ''; document.getElementById('chat-box').appendChild(document.getElementById('welcome'));
                document.getElementById('welcome').style.display = 'flex';
                toggleSidebar();
            }}
            function saveData() {{ localStorage.setItem('flux_v29_2_history', JSON.stringify(chats)); }}
            function renderHistory() {{
                const list = document.getElementById('history-list'); list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div'); div.className = 'history-item';
                    div.innerHTML = `<i class="far fa-comment-alt"></i> <span>${{chat.title}}</span>`;
                    div.onclick = () => loadChat(chat.id); list.appendChild(div);
                }});
            }}
            renderHistory();

            function loadChat(id) {{
                currentChatId = id; const chat = chats.find(c => c.id === id); if(!chat) return;
                const box = document.getElementById('chat-box'); box.innerHTML = '';
                document.getElementById('welcome').style.display = 'none';
                chat.messages.forEach(msg => appendBubble(msg.text, msg.role === 'user', false));
                toggleSidebar();
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
                                    <button onclick="openFullscreenPreview(this)" data-code="${{encodeURIComponent(code)}}">
                                        <i class="fas fa-play"></i> Fullscreen
                                    </button>
                                </div>
                            </div>
                            <div class="artifact-content">
                                <iframe srcdoc="${{code.replace(/"/g, '&quot;')}}"></iframe>
                            </div>`;
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

            function appendBubble(text, isUser, animate=true) {{
                document.getElementById('welcome').style.display = 'none';
                const wrapper = document.createElement('div'); wrapper.className = `message-wrapper ${{isUser ? 'user' : 'bot'}}`;
                const avatar = `<div class="avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}"><i class="fas ${{isUser ? 'fa-user' : 'fa-bolt'}}"></i></div>`;
                wrapper.innerHTML = `${{avatar}}<div class="bubble-container"><div class="sender-name">${{isUser ? 'You' : '{APP_NAME}'}}</div><div class="bubble">${{marked.parse(text)}}</div></div>`;
                document.getElementById('chat-box').appendChild(wrapper);
                
                if(!isUser) {{
                    hljs.highlightAll();
                    checkForArtifacts(text, wrapper.querySelector('.bubble'));
                }}
                document.getElementById('chat-box').scrollTo({{ top: document.getElementById('chat-box').scrollHeight, behavior: 'smooth' }});
            }}

            function showDeepBrainThinking() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `
                    <div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div>
                    <div class="bubble-container">
                        <div class="sender-name">{APP_NAME}</div>
                        <div class="bubble" style="background:transparent; padding:0; width:100%;">
                            <div class="brain-container">
                                <div class="brain-header"><i class="fas fa-microchip brain-icon"></i><span class="brain-title">Deep-Brain Processor</span></div>
                                <div class="brain-logs" id="brain-logs"></div>
                            </div>
                        </div>
                    </div>`;
                document.getElementById('chat-box').appendChild(wrapper);
                document.getElementById('chat-box').scrollTo({{ top: document.getElementById('chat-box').scrollHeight, behavior: 'smooth' }});

                const logs = ["Analyzing query...", "Neural compiling...", "Generating response..."];
                const container = document.getElementById('brain-logs');
                let i = 0;
                window.brainInterval = setInterval(() => {{
                    if(i < logs.length) {{
                        const line = document.createElement('div'); line.className = 'log-line'; line.style.opacity = '1'; line.innerText = logs[i];
                        container.appendChild(line); i++;
                    }} else clearInterval(window.brainInterval);
                }}, 800);
            }}

            function removeTyping() {{ 
                if(window.brainInterval) clearInterval(window.brainInterval);
                document.getElementById('typing-indicator')?.remove(); 
            }}

            function sendSuggestion(text) {{ document.getElementById('msg').value = text; sendMessage(); }}

            async function sendMessage() {{
                const msgInput = document.getElementById('msg');
                const text = msgInput.value.trim();
                if(!text) return;

                if(text === '!admin') {{ msgInput.value = ''; openModal('admin-auth-modal'); return; }}

                if(!currentChatId) {{
                    currentChatId = Date.now();
                    chats.unshift({{ id: currentChatId, title: text.substring(0, 20), messages: [] }});
                }}
                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                saveData(); renderHistory();
                msgInput.value = ''; appendBubble(text, true);

                showDeepBrainThinking();
                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: chat.messages.slice(-10).map(m => ({{role: m.role, content: m.text}})) }})
                    }});
                    removeTyping();
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrap = document.createElement('div'); wrap.className = 'message-wrapper bot';
                    wrap.innerHTML = `<div class="avatar bot-avatar"><i class="fas fa-bolt"></i></div><div class="bubble-container"><div class="sender-name">{APP_NAME}</div><div class="bubble"></div></div>`;
                    document.getElementById('chat-box').appendChild(wrap);
                    const bubble = wrap.querySelector('.bubble');

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubble.innerHTML = marked.parse(botResp);
                        document.getElementById('chat-box').scrollTo({{ top: document.getElementById('chat-box').scrollHeight, behavior: 'auto' }});
                    }}
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData(); hljs.highlightAll(); checkForArtifacts(botResp, bubble);
                }} catch(e) {{ removeTyping(); appendBubble("System Error.", false); }}
            }}

            function openModal(id) {{ document.getElementById(id).style.display = 'flex'; }}
            function closeModal(id) {{ document.getElementById(id).style.display = 'none'; }}
            function confirmDelete() {{ localStorage.removeItem('flux_v29_2_history'); location.reload(); }}
            async function verifyAdmin() {{
                if(document.getElementById('admin-pass').value === '{ADMIN_PASSWORD}') {{
                    closeModal('admin-auth-modal'); openModal('admin-panel-modal');
                    const res = await fetch('/admin/stats'); const data = await res.json();
                    document.getElementById('stat-uptime').innerText = data.uptime;
                    document.getElementById('stat-msgs').innerText = data.total_messages;
                }} else document.getElementById('admin-error-msg').style.display = 'block';
            }}
            async function toggleSystem() {{ await fetch('/admin/toggle_system', {{method:'POST'}}); location.reload(); }}
        </script>
    </body>
    </html>
    """

# 🛡️ ADMIN API ROUTES
@app.route("/admin/stats")
def admin_stats():
    return jsonify({"uptime": get_uptime(), "total_messages": TOTAL_MESSAGES, "active": SYSTEM_ACTIVE})

@app.route("/admin/toggle_system", methods=["POST"])
def toggle_system():
    global SYSTEM_ACTIVE
    SYSTEM_ACTIVE = not SYSTEM_ACTIVE
    return jsonify({"active": SYSTEM_ACTIVE})

@app.route("/chat", methods=["POST"])
def chat():
    global TOTAL_MESSAGES
    if not SYSTEM_ACTIVE: return Response("System maintenance.", status=503)
    TOTAL_MESSAGES += 1
    data = request.json
    messages = data.get("messages", [])
    ctx = get_current_context()
    
    # 🔥 ENHANCED SYSTEM PROMPT (ANIMATIONS + MOBILE FIX) 🔥
    sys_prompt = f"""
    You are {APP_NAME}, an Elite AI created by {OWNER_NAME}.
    
    RULES:
    1. If building an App/Game, ALWAYS use:
       - <meta name="viewport" content="width=device-width, initial-scale=1.0">
       - Animate.css: <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
       - Use classes like 'animate__animated animate__fadeInUp' for entrance.
       - Use modern CSS (Glassmorphism, Flexbox, Gradients).
    2. Ensure EVERYTHING is inside a container with `box-sizing: border-box; max-width: 100%;` to prevent mobile overflow.
    3. Generate the FULL code in ONE ```html block.
    """

    def generate():
        client = get_groq_client()
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}] + messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
