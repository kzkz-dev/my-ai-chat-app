from flask import Flask, request, Response, jsonify
from groq import Groq
import os
import time
from datetime import datetime
import pytz
import json
import random  # 🆕 Added for random suggestions

# ==========================================
# 🔹 Flux AI (Picasso Update - Build 13.0.0) 🎨
# ==========================================
APP_NAME = "Flux AI"
OWNER_NAME = "KAWCHUR"
OWNER_NAME_BN = "কাওছুর"
VERSION = "13.0.0"

# ⚠️ আপনার আসল ফেসবুক এবং ওয়েবসাইটের লিঙ্ক দিন ⚠️
FACEBOOK_URL = "Not available right now" 
WEBSITE_URL = "https://sites.google.com/view/flux-ai-app/home"      

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

# 🆕 DYNAMIC SUGGESTION POOL (উপরের ২টা এখান থেকে আসবে)
SUGGESTION_POOL = [
    {"icon": "fas fa-envelope-open-text", "text": "Draft a professional email"},
    {"icon": "fas fa-code", "text": "Write a Python script for web scraping"},
    {"icon": "fas fa-brain", "text": "Explain Quantum Computing simply"},
    {"icon": "fas fa-dumbbell", "text": "Give me a 30-minute home workout plan"},
    {"icon": "fas fa-utensils", "text": "Suggest a healthy dinner recipe"},
    {"icon": "fas fa-book-open", "text": "Summarize the book 'Atomic Habits'"},
    {"icon": "fas fa-plane", "text": "Plan a 3-day trip to Cox's Bazar"},
    {"icon": "fas fa-lightbulb", "text": "Give me 5 creative business ideas"},
    {"icon": "fas fa-guitar", "text": "Write a short song lyric about rain"},
    {"icon": "fas fa-laptop-code", "text": "Explain HTML and CSS to a beginner"}
]

@app.route("/")
def home():
    # 🆕 Pick 2 random suggestions for the top slots
    random_suggestions = random.sample(SUGGESTION_POOL, 2)

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
                --user-bubble: #2563eb;
                --border: #1f2937;
                --accent: #3b82f6;
                --chat-accent: #3b82f6; /* 🆕 DYNAMIC ACCENT COLOR VARIABLE */
                --bot-icon: linear-gradient(135deg, #3b82f6, #8b5cf6);
                --danger: #ef4444;
            }}
            body.light {{
                --bg: #ffffff;
                --sidebar: #f9fafb;
                --text: #111827;
                --text-secondary: #6b7280;
                --input-bg: #f3f4f6;
                --user-bubble: #2563eb;
                --border: #e5e7eb;
                --accent: #2563eb;
                --chat-accent: #2563eb;
                --bot-icon: linear-gradient(135deg, #2563eb, #7c3aed);
            }}

            * {{ box-sizing: border-box; outline: none; -webkit-tap-highlight-color: transparent; }}
            body {{ margin: 0; background: var(--bg); color: var(--text); font-family: 'Inter', 'Noto Sans Bengali', sans-serif; height: 100vh; display: flex; overflow: hidden; }}

            ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
            ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}
            
            #sidebar {{
                width: 280px; background: var(--sidebar); height: 100%; display: flex; flex-direction: column;
                padding: 20px; border-right: 1px solid var(--border); transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
                position: absolute; z-index: 200; left: 0; top: 0; box-shadow: 5px 0 25px rgba(0,0,0,0.3);
            }}
            #sidebar.closed {{ transform: translateX(-105%); box-shadow: none; }}
            
            .brand {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 25px; display: flex; align-items: center; gap: 12px; color: var(--text); letter-spacing: -0.5px; user-select: none; }}
            .brand i {{ background: var(--bot-icon); -webkit-background-clip: text; color: transparent; font-size: 1.6rem; }}
            
            .new-chat-btn {{
                width: 100%; padding: 12px; background: transparent; color: var(--text); border: 1px solid var(--border);
                border-radius: 12px; font-weight: 500; font-size: 0.95rem; cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 10px;
                transition: all 0.2s ease; margin-bottom: 20px;
            }}
            .new-chat-btn:active {{ transform: scale(0.95); background: var(--input-bg); }}

            .history-list {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; padding-right: 5px; margin-bottom: 10px; }}
            .history-item {{
                padding: 10px 12px; border-radius: 10px; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 12px;
                font-size: 0.9rem; transition: background 0.2s; user-select: none;
            }}
            .history-item:active {{ background: var(--input-bg); color: var(--text); transform: scale(0.98); }}

            .menu-section {{ margin-top: auto; border-top: 1px solid var(--border); padding-top: 15px; display: flex; flex-direction: column; gap: 8px; }}
            
            .theme-toggles {{ display: flex; background: var(--input-bg); padding: 5px; border-radius: 10px; }}
            .theme-btn {{ flex: 1; padding: 8px; border-radius: 8px; border: none; background: transparent; color: var(--text-secondary); cursor: pointer; font-size: 0.85rem; font-weight: 500; transition: 0.3s; }}
            .theme-btn.active {{ background: var(--bg); color: var(--text); box-shadow: 0 2px 5px rgba(0,0,0,0.15); }}

            .about-section {{ 
                display: none; background: var(--input-bg); padding: 15px; border-radius: 12px;
                margin-top: 5px; font-size: 0.85rem; text-align: center; border: 1px solid var(--border);
            }}
            .about-section.show {{ display: block; animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
            .about-link {{ color: var(--text); font-size: 1.2rem; text-decoration: none; margin: 0 10px; transition: color 0.2s; }}
            .about-link:hover {{ color: var(--accent); transform: scale(1.1); display: inline-block; }}

            header {{
                height: 60px; display: flex; align-items: center; justify-content: space-between;
                padding: 0 15px; z-index: 100; background: rgba(11, 15, 25, 0.7); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
                border-bottom: 1px solid rgba(255,255,255,0.05); position: absolute; top: 0; left: 0; right: 0;
            }}
            body.light header {{ background: rgba(255, 255, 255, 0.8); border-bottom: 1px solid rgba(0,0,0,0.05); }}

            #main {{ flex: 1; display: flex; flex-direction: column; position: relative; width: 100%; height: 100vh; }}
            
            #chat-box {{ 
                flex: 1; overflow-y: auto; padding: 80px 20px 140px 20px; 
                display: flex; flex-direction: column; gap: 28px; scroll-behavior: smooth;
            }}

            /* Welcome Screen Animations */
            .welcome-container {{
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                height: 80%; text-align: center; animation: popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }}
            .icon-wrapper {{ 
                width: 70px; height: 70px; background: var(--bot-icon); border-radius: 22px; 
                display: flex; align-items: center; justify-content: center; font-size: 2.2rem; color: white; 
                margin-bottom: 20px; box-shadow: 0 0 25px rgba(59, 130, 246, 0.4);
                animation: float 3s ease-in-out infinite;
            }}
            
            .welcome-title {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 8px; letter-spacing: -0.5px; }}
            .welcome-subtitle {{ color: var(--text-secondary); font-size: 1.05rem; margin-bottom: 40px; font-weight: 400; }}
            
            .suggestions {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; width: 100%; max-width: 550px; }}
            .chip {{
                padding: 16px; background: transparent; border-radius: 18px; cursor: pointer; text-align: left;
                border: 1px solid var(--border); transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); font-size: 0.95rem; color: var(--text-secondary);
                background-color: rgba(255,255,255,0.02);
                animation: slideUpFade 0.6s ease forwards; opacity: 0;
            }}
            body.light .chip {{ background-color: rgba(0,0,0,0.02); }}
            .chip:active {{ background: var(--input-bg); border-color: var(--accent); transform: scale(0.95); }}
            .chip i {{ color: var(--text); margin-bottom: 10px; display: block; font-size: 1.3rem; opacity: 0.9; transition: transform 0.3s; }}
            .chip:hover i {{ transform: scale(1.1); }}
            
            .chip:nth-child(1) {{ animation-delay: 0.1s; }}
            .chip:nth-child(2) {{ animation-delay: 0.2s; }}
            .chip:nth-child(3) {{ animation-delay: 0.3s; }}
            .chip:nth-child(4) {{ animation-delay: 0.4s; }}

            /* 🌟 Message Wrapper & Text Wrap Fixes 🌟 */
            .message-wrapper {{ display: flex; gap: 15px; width: 100%; animation: popInChat 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; max-width: 800px; margin: 0 auto; }}
            .message-wrapper.user {{ flex-direction: row-reverse; }}
            
            .avatar {{ width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; transition: transform 0.3s; }}
            .bot-avatar {{ background: var(--bot-icon); color: white; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }}
            .bot-avatar.thinking {{ animation: pulseGlow 1.5s infinite; }}
            .user-avatar {{ background: var(--input-bg); color: var(--text); border: 1px solid var(--border); }}
            
            /* The FIX for Horizontal Scroll! */
            .bubble-container {{ display: flex; flex-direction: column; width: calc(100% - 50px); }}
            
            .sender-name {{ font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; margin-top: 2px; }}
            .user .sender-name {{ display: none; }} 
            
            .bubble {{ font-size: 0.98rem; line-height: 1.6; color: var(--text); word-break: break-word; overflow-wrap: break-word; white-space: normal; width: 100%; }}
            .bubble * {{ max-width: 100%; }} /* Ensure children don't overflow */
            .bubble p {{ white-space: pre-wrap; margin-top: 0; margin-bottom: 12px; }}
            .bubble p:last-child {{ margin-bottom: 0; }}
            
            .bot .bubble {{ padding: 0; margin-top: 5px; }}
            .user .bubble {{ background: var(--input-bg); padding: 12px 16px; border-radius: 20px 4px 20px 20px; display: inline-block; max-width: max-content; align-self: flex-end; }}

            /* Beautiful Lists */
            .bubble ul, .bubble ol {{ margin: 8px 0 12px 0; padding-left: 20px; color: var(--text); }}
            .bubble li {{ margin-bottom: 6px; line-height: 1.5; }}
            
            /* 🆕 DYNAMIC COLOR HIGHLIGHTS */
            .bubble strong {{ font-weight: 600; color: var(--chat-accent); }}
            body.light .bubble strong {{ color: var(--chat-accent); }}

            /* 🆕 IMAGE BRANDING STYLE */
            .img-container {{ margin-top:10px; display: inline-block; position: relative; }}
            .bubble img {{ border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); max-width: 100%; display: block; }}
            .img-brand {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 6px; display: flex; align-items: center; gap: 5px; font-weight: 500; opacity: 0.8; }}

            .typing {{ display: flex; gap: 5px; align-items: center; padding: 10px 0; }}
            .dot {{ width: 7px; height: 7px; background: var(--text-secondary); border-radius: 50%; animation: typingBounce 1.4s infinite ease-in-out both; }}
            .dot:nth-child(1) {{ animation-delay: -0.32s; }}
            .dot:nth-child(2) {{ animation-delay: -0.16s; }}

            #input-area {{
                position: absolute; bottom: 0; left: 0; right: 0; padding: 10px 20px 20px 20px;
                background: linear-gradient(to top, var(--bg) 80%, transparent); display: flex; justify-content: center; z-index: 50;
            }}
            .input-box {{
                width: 100%; max-width: 750px; display: flex; align-items: flex-end; 
                background: var(--input-bg); border-radius: 24px; padding: 6px 6px 6px 18px;
                border: 1px solid var(--border); transition: 0.3s; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .input-box:focus-within {{ border-color: rgba(59, 130, 246, 0.5); transform: translateY(-2px); box-shadow: 0 15px 35px rgba(0,0,0,0.3); }}
            
            textarea {{
                flex: 1; background: transparent; border: none; outline: none;
                color: var(--text); font-size: 1rem; max-height: 150px; resize: none;
                padding: 12px 0; font-family: inherit; line-height: 1.5;
            }}
            .send-btn {{
                background: var(--text); color: var(--bg); border: none; width: 42px; height: 42px;
                border-radius: 50%; cursor: pointer; margin-left: 10px; display: flex; align-items: center; justify-content: center;
                transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); font-size: 1rem; flex-shrink: 0; margin-bottom: 3px;
            }}
            .send-btn:active {{ transform: scale(0.85); }}
            .send-btn.active-typing {{ background: var(--accent); color: white; transform: rotate(-10deg) scale(1.05); }}

            /* CUSTOM MODAL FOR DELETE */
            .modal-overlay {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7); display: none; justify-content: center; align-items: center;
                z-index: 9999; backdrop-filter: blur(5px); animation: fadeIn 0.2s;
            }}
            .modal-box {{
                background: var(--sidebar); border: 1px solid var(--border);
                padding: 25px; border-radius: 18px; width: 90%; max-width: 320px;
                text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                transform: scale(0.9); animation: popIn 0.3s forwards;
            }}
            .modal-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 10px; color: var(--text); }}
            .modal-desc {{ font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 25px; }}
            .modal-buttons {{ display: flex; gap: 10px; justify-content: center; }}
            .btn-modal {{
                padding: 10px 20px; border-radius: 10px; border: none; font-weight: 600; cursor: pointer; flex: 1; transition: 0.2s;
            }}
            .btn-cancel {{ background: var(--input-bg); color: var(--text); }}
            .btn-delete {{ background: var(--danger); color: white; }}
            .btn-modal:active {{ transform: scale(0.95); }}

            /* Code Block Fixes */
            pre {{ 
                border-radius: 14px; 
                padding: 40px 15px 15px 15px;
                background: #0d1117 !important; 
                border: 1px solid rgba(255,255,255,0.08); 
                margin: 15px 0; 
                font-size: 0.85em; 
                overflow-x: auto; /* Scroll only inside code */
                max-width: 100%;
                position: relative;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }}
            pre::before {{
                content: ''; position: absolute; top: 15px; left: 15px; width: 12px; height: 12px; border-radius: 50%;
                background: #ff5f56; box-shadow: 20px 0 0 #ffbd2e, 40px 0 0 #27c93f;
            }}
            .copy-btn {{
                position: absolute; top: 8px; right: 10px; background: rgba(255,255,255,0.1); color: #fff; border: none;
                padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; cursor: pointer; transition: 0.2s; font-family: 'Inter', sans-serif; font-weight: 500;
            }}
            .copy-btn:hover {{ background: rgba(255,255,255,0.25); transform: translateY(-1px); }}
            
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 0.9em; border-radius: 8px; overflow: hidden; }}
            th, td {{ border: 1px solid var(--border); padding: 12px; text-align: left; }}
            th {{ background: var(--input-bg); font-weight: 600; color: var(--accent); }}
            
            blockquote {{ border-left: 4px solid var(--accent); margin: 10px 0; padding-left: 15px; color: var(--text-secondary); font-style: italic; background: rgba(59, 130, 246, 0.05); padding: 12px 15px; border-radius: 0 10px 10px 0; }}

            /* Keyframes */
            @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-8px); box-shadow: 0 15px 30px rgba(59, 130, 246, 0.5); }} }}
            @keyframes pulseGlow {{ 0%, 100% {{ box-shadow: 0 0 10px rgba(59, 130, 246, 0.3); transform: scale(1); }} 50% {{ box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); transform: scale(1.05); }} }}
            @keyframes typingBounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            @keyframes popIn {{ 0% {{ opacity: 0; transform: scale(0.9); }} 100% {{ opacity: 1; transform: scale(1); }} }}
            @keyframes popInChat {{ 0% {{ opacity: 0; transform: translateY(20px) scale(0.95); }} 100% {{ opacity: 1; transform: translateY(0) scale(1); }} }}
            @keyframes scaleIn {{ 0% {{ opacity: 0; transform: translateY(-10px) scale(0.95); }} 100% {{ opacity: 1; transform: translateY(0) scale(1); }} }}
            @keyframes slideUpFade {{ 0% {{ opacity: 0; transform: translateY(20px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
        </style>
    </head>
    <body class="dark">
    
        <div id="delete-modal" class="modal-overlay">
            <div class="modal-box">
                <div class="modal-title"><i class="fas fa-trash-alt" style="color:var(--danger)"></i> Clear History?</div>
                <div class="modal-desc">All your conversations will be permanently deleted. This action cannot be undone.</div>
                <div class="modal-buttons">
                    <button class="btn-modal btn-cancel" onclick="closeModal()">Cancel</button>
                    <button class="btn-modal btn-delete" onclick="confirmDelete()">Delete</button>
                </div>
            </div>
        </div>

        <div class="overlay" onclick="toggleSidebar()"></div>
        
        <div id="sidebar" class="closed">
            <div class="brand"><i class="fas fa-bolt"></i> {APP_NAME}</div>
            <button class="new-chat-btn" onclick="startNewChat()">
                <i class="fas fa-pen-to-square"></i> New chat
            </button>
            
            <div style="font-size:0.75rem; font-weight:600; color:var(--text-secondary); margin-bottom:10px; padding-left:5px; text-transform: uppercase; letter-spacing: 1px;">Recent</div>
            <div class="history-list" id="history-list"></div>
            
            <div class="menu-section">
                <div class="theme-toggles">
                    <button class="theme-btn active" id="btn-dark" onclick="setTheme('dark')"><i class="fas fa-moon"></i> Dark</button>
                    <button class="theme-btn" id="btn-light" onclick="setTheme('light')"><i class="fas fa-sun"></i> Light</button>
                </div>

                <div class="history-item" onclick="toggleAbout()" style="color: var(--text); justify-content: flex-start; margin-top:5px;">
                    <i class="fas fa-info-circle"></i> App Info
                </div>
                
                <div id="about-info" class="about-section">
                    <strong style="color:var(--text); font-size: 1.1rem;">{APP_NAME}</strong><br>
                    <small style="color: var(--text-secondary);">Version {VERSION}</small><br>
                    <div style="margin: 15px 0;">
                        <a href="{FACEBOOK_URL}" target="_blank" class="about-link"><i class="fab fa-facebook"></i></a>
                        <a href="{WEBSITE_URL}" target="_blank" class="about-link"><i class="fas fa-globe"></i></a>
                    </div>
                    <small style="color:var(--text-secondary);">Developer: {OWNER_NAME}</small><br>
                    <small style="color:var(--text-secondary); font-size: 0.75rem; opacity: 0.8; display: block; margin-top: 5px;">&copy; {datetime.now().year} {OWNER_NAME}. All rights reserved.</small>
                </div>

                <div class="history-item" onclick="openDeleteModal()" style="color: #ef4444; justify-content: flex-start; margin-top:5px;">
                    <i class="fas fa-trash-alt"></i> Delete history
                </div>
            </div>
        </div>

        <div id="main">
            <header>
                <button onclick="toggleSidebar()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px; transition: transform 0.2s;">
                    <i class="fas fa-bars"></i>
                </button>
                <span style="font-weight:600; font-size:1.2rem; letter-spacing: -0.5px;">{APP_NAME}</span>
                <button onclick="startNewChat()" style="background:none; border:none; color:var(--text); font-size:1.3rem; cursor:pointer; padding: 5px; transition: transform 0.2s;">
                    <i class="fas fa-pen-to-square"></i>
                </button>
            </header>

            <div id="chat-box">
                <div id="welcome" class="welcome-container">
                    <div class="icon-wrapper"><i class="fas fa-bolt"></i></div>
                    <div class="welcome-title">Welcome to {APP_NAME}</div>
                    <div class="welcome-subtitle">Your brilliant AI assistant is ready to help.</div>
                    
                    <div class="suggestions">
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[0]['text']}')"><i class="{random_suggestions[0]['icon']}"></i> {random_suggestions[0]['text']}</div>
                        <div class="chip" onclick="sendSuggestion('{random_suggestions[1]['text']}')"><i class="{random_suggestions[1]['icon']}"></i> {random_suggestions[1]['text']}</div>
                        
                        <div class="chip" onclick="sendSuggestion('Generate a futuristic cyberpunk city image')"><i class="fas fa-paint-brush"></i> Generate Image</div>
                        <div class="chip" onclick="sendSuggestion('Solve this math puzzle: 2 + 2 * 4')"><i class="fas fa-calculator"></i> Solve Math</div>
                    </div>
                </div>
            </div>

            <div id="input-area">
                <div class="input-box">
                    <textarea id="msg" placeholder="Message Flux AI..." rows="1" oninput="resizeInput(this)"></textarea>
                    <button id="send-btn-icon" class="send-btn" onclick="sendMessage()"><i class="fas fa-arrow-up"></i></button>
                </div>
            </div>
        </div>

        <script>
            // Enable marked breaks for proper markdown newlines
            marked.use({{ breaks: true, gfm: true }});

            let chats = JSON.parse(localStorage.getItem('flux_v6_history')) || [];
            let currentChatId = null;
            const sidebar = document.getElementById('sidebar');
            const chatBox = document.getElementById('chat-box');
            const msgInput = document.getElementById('msg');
            const welcomeScreen = document.getElementById('welcome');
            const sendBtn = document.getElementById('send-btn-icon');
            const deleteModal = document.getElementById('delete-modal');

            // 🆕 DYNAMIC COLOR PALETTE
            const accentColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
            renderHistory();

            function setTheme(mode) {{
                document.body.className = mode;
                localStorage.setItem('theme', mode);
                document.getElementById('btn-dark').className = mode === 'dark' ? 'theme-btn active' : 'theme-btn';
                document.getElementById('btn-light').className = mode === 'light' ? 'theme-btn active' : 'theme-btn';
            }}

            function toggleAbout() {{
                document.getElementById('about-info').classList.toggle('show');
            }}

            function resizeInput(el) {{
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 120) + 'px';
                if(el.value.trim() !== "") {{
                    sendBtn.classList.add('active-typing');
                }} else {{
                    sendBtn.classList.remove('active-typing');
                }}
            }}

            function toggleSidebar() {{
                sidebar.classList.toggle('closed');
                document.querySelector('.overlay').classList.toggle('open');
            }}

            function startNewChat() {{
                currentChatId = Date.now();
                // 🆕 PICK RANDOM ACCENT COLOR
                const randomColor = accentColors[Math.floor(Math.random() * accentColors.length)];
                chats.unshift({{ id: currentChatId, title: "New conversation", messages: [], accent: randomColor }});
                
                saveData();
                renderHistory();
                
                // 🆕 FORCE RELOAD TO UPDATE DYNAMIC SUGGESTIONS
                // (Optionally, we could just clear DOM, but reloading ensures python picks new suggestions)
                chatBox.innerHTML = '';
                chatBox.appendChild(welcomeScreen);
                welcomeScreen.style.display = 'flex';
                
                msgInput.value = '';
                resizeInput(msgInput);
                sidebar.classList.add('closed');
                document.querySelector('.overlay').classList.remove('open');
            }}

            function saveData() {{
                localStorage.setItem('flux_v6_history', JSON.stringify(chats));
            }}

            function renderHistory() {{
                const list = document.getElementById('history-list');
                list.innerHTML = '';
                chats.forEach(chat => {{
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${{(chat.title || 'New conversation').substring(0, 25)}}</span>`;
                    div.onclick = () => loadChat(chat.id);
                    list.appendChild(div);
                }});
            }}

            function loadChat(id) {{
                currentChatId = id;
                const chat = chats.find(c => c.id === id);
                if(!chat) return;

                // 🆕 APPLY CHAT'S ACCENT COLOR
                document.documentElement.style.setProperty('--chat-accent', chat.accent || '#3b82f6');

                chatBox.innerHTML = '';
                welcomeScreen.style.display = 'none';
                
                chat.messages.forEach(msg => {{
                    appendBubble(msg.text, msg.role === 'user');
                }});
                
                sidebar.classList.add('closed');
                document.querySelector('.overlay').classList.remove('open');
                setTimeout(() => chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }}), 100);
            }}

            function addCopyButtons() {{
                document.querySelectorAll('pre').forEach(pre => {{
                    if(pre.querySelector('.copy-btn')) return;
                    const btn = document.createElement('button');
                    btn.className = 'copy-btn';
                    btn.innerHTML = '<i class="far fa-copy"></i> Copy';
                    btn.onclick = () => {{
                        const code = pre.querySelector('code').innerText;
                        navigator.clipboard.writeText(code);
                        btn.innerHTML = '<i class="fas fa-check"></i> Copied';
                        setTimeout(() => btn.innerHTML = '<i class="far fa-copy"></i> Copy', 2000);
                    }};
                    pre.appendChild(btn);
                }});
            }}

            // 🆕 ADD BRANDING TO IMAGES
            function addBrandingToImages() {{
                document.querySelectorAll('.bubble img').forEach(img => {{
                    if(img.closest('.img-container')) return; // Already processed

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
                
                const avatar = document.createElement('div');
                avatar.className = `avatar ${{isUser ? 'user-avatar' : 'bot-avatar'}}`;
                avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-bolt"></i>';
                
                const bubbleContainer = document.createElement('div');
                bubbleContainer.className = 'bubble-container';
                
                const senderName = document.createElement('div');
                senderName.className = 'sender-name';
                senderName.innerText = isUser ? 'You' : '{APP_NAME}';
                
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = marked.parse(text);
                
                bubbleContainer.appendChild(senderName);
                bubbleContainer.appendChild(bubble);
                
                wrapper.appendChild(avatar);
                wrapper.appendChild(bubbleContainer);
                chatBox.appendChild(wrapper);
                
                if(!isUser) {{
                    hljs.highlightAll();
                    addCopyButtons();
                    addBrandingToImages(); // 🆕 Check for images
                }}
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function showTyping() {{
                const wrapper = document.createElement('div');
                wrapper.id = 'typing-indicator';
                wrapper.className = 'message-wrapper bot';
                wrapper.innerHTML = `
                    <div class="avatar bot-avatar thinking"><i class="fas fa-bolt"></i></div>
                    <div class="bubble-container">
                        <div class="sender-name">{APP_NAME} is typing...</div>
                        <div class="bubble"><div class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>
                    </div>
                `;
                chatBox.appendChild(wrapper);
                chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'smooth' }});
            }}

            function removeTyping() {{
                const el = document.getElementById('typing-indicator');
                if(el) el.remove();
            }}

            function sendSuggestion(text) {{
                msgInput.value = text;
                sendMessage();
            }}

            async function sendMessage() {{
                const text = msgInput.value.trim();
                if(!text) return;

                if(!currentChatId) startNewChat();

                const chat = chats.find(c => c.id === currentChatId);
                chat.messages.push({{ role: 'user', text: text }});
                
                if(chat.messages.length === 1) {{
                    chat.title = text.substring(0, 30);
                    renderHistory();
                }}
                saveData();

                msgInput.value = '';
                resizeInput(msgInput);
                appendBubble(text, true);
                showTyping();

                const context = chat.messages.slice(-15).map(m => ({{ role: m.role, content: m.text }}));

                try {{
                    const res = await fetch('/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ messages: context }})
                    }});
                    
                    removeTyping();

                    if(!res.ok) throw new Error("API Error");

                    const reader = res.body.getReader();
                    const decoder = new TextDecoder();
                    let botResp = '';
                    
                    const wrapper = document.createElement('div');
                    wrapper.className = 'message-wrapper bot';
                    
                    const avatar = document.createElement('div');
                    avatar.className = 'avatar bot-avatar thinking';
                    avatar.innerHTML = '<i class="fas fa-bolt"></i>';
                    
                    const bubbleContainer = document.createElement('div');
                    bubbleContainer.className = 'bubble-container';
                    
                    const senderName = document.createElement('div');
                    senderName.className = 'sender-name';
                    senderName.innerText = '{APP_NAME}';
                    
                    const bubble = document.createElement('div');
                    bubble.className = 'bubble';
                    
                    bubbleContainer.appendChild(senderName);
                    bubbleContainer.appendChild(bubble);
                    wrapper.appendChild(avatar);
                    wrapper.appendChild(bubbleContainer);
                    chatBox.appendChild(wrapper);

                    while(true) {{
                        const {{ done, value }} = await reader.read();
                        if(done) break;
                        botResp += decoder.decode(value);
                        bubble.innerHTML = marked.parse(botResp);
                        chatBox.scrollTo({{ top: chatBox.scrollHeight, behavior: 'auto' }});
                    }}
                    
                    avatar.classList.remove('thinking');
                    chat.messages.push({{ role: 'assistant', text: botResp }});
                    saveData();
                    hljs.highlightAll();
                    addCopyButtons();
                    addBrandingToImages(); // 🆕 Add branding after stream completes

                }} catch(e) {{
                    removeTyping();
                    appendBubble("⚠️ Internet connection unstable or API Error.", false);
                }}
            }}

            // 🛑 MODAL LOGIC (New) 🛑
            function openDeleteModal() {{
                deleteModal.style.display = 'flex';
                sidebar.classList.add('closed');
            }}

            function closeModal() {{
                deleteModal.style.display = 'none';
            }}

            function confirmDelete() {{
                localStorage.removeItem('flux_v6_history');
                location.reload();
            }}

            msgInput.addEventListener('keypress', e => {{
                if(e.key === 'Enter' && !e.shiftKey) {{
                    e.preventDefault();
                    sendMessage();
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    ctx = get_current_context()
    
    # 🧠 THE ULTIMATE SUPER BRAIN (UPDATED FOR NEWS & IMAGES) 🧠
    sys_prompt = {
        "role": "system",
        "content": f"""
        You are {APP_NAME}, a brilliant, highly engaging, and empathetic premium AI assistant.
        
        👑 CREATOR & IDENTITY:
        - Created strictly by: {OWNER_NAME}
        - Copyright: © {ctx['year']} {OWNER_NAME}.
        - Never mention OpenAI, Google, Anthropic, or any other company.
        
        📅 TIME AWARENESS:
        - Date: {ctx['date']}
        - Time: Always provide UTC Time first ({ctx['time_utc']}), followed by Bangladesh Local Time ({ctx['time_local']}) if asked.
        
        🎨 IMAGE GENERATION RULE (VERY IMPORTANT):
        If the user wants an image:
        1. First line MUST be: "🎨 Generating image for you..." (or similar helpful text).
        2. Then add a blank line.
        3. Then provide the image link: ![Flux Image](https://image.pollinations.ai/prompt/{{detailed_prompt_here}})
        
        🚫 LIMITATIONS (Crucial):
        - You DO NOT have real-time internet access.
        - If asked about live events (news, elections, weather, sports) happening today or yesterday, politely apologize. Say: "I don't have real-time internet access to check live news, but I can help you with..."
        - Do NOT hallucinate or make up fake news.
        
        🧠 BEHAVIORAL MASTERY:
        1. NO WALLS OF TEXT: Use short, readable paragraphs.
        2. PERFECT EMPATHY & TONE: Be warm, fun, and human-like.
        3. FLAWLESS FORMATTING: Use Markdown properly.
        4. LANGUAGE: Perfectly mirror the user's language (Bangla/English).
        """
    }

    def generate():
        global current_key_index
        attempts = 0
        max_retries = len(GROQ_KEYS) + 1 if GROQ_KEYS else 1
        
        while attempts < max_retries:
            try:
                client = get_groq_client()
                if not client:
                    yield "⚠️ Server Configuration Error."
                    return

                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[sys_prompt] + messages,
                    stream=True,
                    temperature=0.75, 
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
        yield "⚠️ System overloaded. Please try again."

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)