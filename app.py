import hashlib
import json
import urllib.error
import urllib.request
import hmac
import re
import secrets
import sqlite3
import uuid
from datetime import date, datetime

import streamlit as st

st.set_page_config(
    page_title="StudySphere",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "page" not in st.session_state:
    st.session_state.page = 1

if "show_login" not in st.session_state:
    st.session_state.show_login = "Sign in"

if "auth_id" not in st.session_state:
    st.session_state.auth_id = None

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "ai_api_key" not in st.session_state:
    st.session_state.ai_api_key = ""

if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "signup_recovery_code" not in st.session_state:
    st.session_state.signup_recovery_code = ""

if "reset_recovery_code" not in st.session_state:
    st.session_state.reset_recovery_code = ""

# ============================================================
# SQLITE DATABASE
# ============================================================

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (auth_id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, university TEXT, degree TEXT, semester TEXT, career_goal TEXT, skills TEXT, study_preferences TEXT, password_hash TEXT, password_salt TEXT, recovery_hash TEXT, recovery_salt TEXT, gemini_api_key TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS app_settings (setting_key TEXT PRIMARY KEY, setting_value TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS chat_sessions (id TEXT PRIMARY KEY, user_id TEXT NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, gemini_interaction_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS chat_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL, user_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)")
cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER DEFAULT 0, subject_id INTEGER, user_id TEXT)")

for table_name in ["subjects", "assignments", "exams", "tasks"]:
    existing_columns = [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if "user_id" not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id TEXT")

chat_session_columns = [row[1] for row in cursor.execute("PRAGMA table_info(chat_sessions)").fetchall()]
if "gemini_interaction_id" not in chat_session_columns:
    cursor.execute("ALTER TABLE chat_sessions ADD COLUMN gemini_interaction_id TEXT")

user_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
if "password_hash" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
if "password_salt" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN password_salt TEXT")
if "recovery_hash" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN recovery_hash TEXT")
if "recovery_salt" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN recovery_salt TEXT")
if "gemini_api_key" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN gemini_api_key TEXT")

# ============================================================
# GLOBAL GEMINI KEY MIGRATION
# ============================================================
# StudySphere uses one Gemini API key for the whole application.
# Migrate the key already stored on any existing account into a
# dedicated global settings row. New accounts never need their
# own copy and never see API-key controls.
global_key_row = cursor.execute(
    "SELECT setting_value FROM app_settings WHERE setting_key = ?",
    ("gemini_api_key",),
).fetchone()
if not global_key_row or not str(global_key_row[0] or "").strip():
    legacy_key_row = cursor.execute(
        "SELECT gemini_api_key FROM users WHERE gemini_api_key IS NOT NULL AND trim(gemini_api_key) != '' ORDER BY rowid LIMIT 1"
    ).fetchone()
    if legacy_key_row and str(legacy_key_row[0] or "").strip():
        cursor.execute(
            "INSERT OR REPLACE INTO app_settings (setting_key, setting_value) VALUES (?, ?)",
            ("gemini_api_key", str(legacy_key_row[0]).strip()),
        )

conn.commit()

# Load the global Gemini key silently from the database.
global_gemini_row = cursor.execute(
    "SELECT setting_value FROM app_settings WHERE setting_key = ?",
    ("gemini_api_key",),
).fetchone()
GLOBAL_GEMINI_API_KEY = str(global_gemini_row[0] or "").strip() if global_gemini_row else ""

# ============================================================
# THEME
# ============================================================
# ============================================================

dark_mode = st.session_state.dark_mode

if dark_mode:
    bg = "#07111F"
    card = "#0F1B2D"
    card2 = "#132238"
    text = "#F8FAFC"
    muted = "#94A3B8"
    border = "#24344D"
    sidebar_bg = "#091524"
    shadow = "0 10px 30px rgba(0,0,0,.22)"
else:
    bg = "#F4F7FB"
    card = "#FFFFFF"
    card2 = "#F8FAFC"
    text = "#0F172A"
    muted = "#64748B"
    border = "#E2E8F0"
    sidebar_bg = "#FFFFFF"
    shadow = "0 10px 30px rgba(15,23,42,.06)"

st.markdown(
    f"""
<style>
.stApp {{ --ss-bg:{bg}; --ss-card:{card}; --ss-chat-assistant:{card}; background:{bg}; color:{text}; }}
[data-testid="stAppViewContainer"] {{ background:{bg}; }}
[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ max-width:1450px; padding-top:1.4rem; padding-bottom:3rem; animation:floatIn .45s ease-out; }}

h1,h2,h3,h4,h5,h6,p,label,.stMarkdown,.stCaption {{ color:{text} !important; }}
[data-testid="stSidebar"] {{ background:{sidebar_bg}; border-right:1px solid {border}; }}
[data-testid="stSidebar"] * {{ color:{text} !important; }}

@keyframes floatIn {{
    from {{ opacity:0; transform:translateY(12px); }}
    to {{ opacity:1; transform:translateY(0); }}
}}
@keyframes shimmer {{
    0% {{ background-position:-500px 0; }}
    100% {{ background-position:500px 0; }}
}}
@keyframes softPulse {{
    0%,100% {{ box-shadow:0 0 0 0 rgba(20,184,166,.16); }}
    50% {{ box-shadow:0 0 0 9px rgba(20,184,166,0); }}
}}

.brand {{ padding:8px 4px 22px; }}
.logo-row {{ display:flex; align-items:center; gap:10px; }}
.logo {{ width:42px; height:42px; border-radius:13px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#14B8A6,#0F766E); color:white !important; font-size:22px; box-shadow:0 8px 20px rgba(20,184,166,.25); }}
.brand-name {{ font-size:23px; font-weight:850; letter-spacing:-.7px; }}
.brand-tag {{ margin:7px 0 0 52px; color:{muted} !important; font-size:11px; }}
.sidebar-label {{ color:{muted} !important; text-transform:uppercase; letter-spacing:1.2px; font-size:10px; font-weight:800; margin:15px 0 7px; }}

.hero {{ position:relative; overflow:hidden; padding:34px 36px; border-radius:25px; margin-bottom:22px; background:radial-gradient(circle at 85% 15%,rgba(45,212,191,.30),transparent 28%),radial-gradient(circle at 10% 100%,rgba(59,130,246,.20),transparent 30%),linear-gradient(135deg,#0F766E,#115E59 52%,#0F172A); box-shadow:0 18px 45px rgba(15,118,110,.20); }}
.hero::after {{ content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(110deg,transparent 35%,rgba(255,255,255,.08) 50%,transparent 65%); background-size:500px 100%; animation:shimmer 7s linear infinite; }}
.hero > * {{ position:relative; z-index:1; }}
.hero-kicker {{ color:#99F6E4 !important; font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:1.5px; }}
.hero-title {{ color:white !important; font-size:35px; line-height:1.1; font-weight:850; letter-spacing:-1.2px; margin:8px 0; }}
.hero-text {{ color:rgba(255,255,255,.82) !important; font-size:14px; max-width:680px; line-height:1.6; }}
.hero-pill {{ display:inline-block; margin-top:18px; padding:7px 12px; border-radius:999px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18); color:white !important; font-size:11px; }}

.stat-card {{ background:{card}; border:1px solid {border}; border-radius:19px; padding:20px; min-height:130px; box-shadow:{shadow}; transition:transform .2s ease,border-color .2s ease; }}
.stat-card:hover {{ transform:translateY(-4px); border-color:#5EEAD4; }}
.stat-top {{ display:flex; justify-content:space-between; align-items:center; }}
.stat-icon {{ width:39px; height:39px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:#CCFBF1; font-size:19px; }}
.stat-number {{ font-size:30px; font-weight:850; color:{text} !important; margin-top:13px; }}
.stat-label {{ font-size:12px; color:{muted} !important; margin-top:2px; }}

.panel {{ background:{card}; border:1px solid {border}; border-radius:20px; padding:22px; margin-top:22px; box-shadow:{shadow}; transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }}
.panel:hover {{ transform:translateY(-2px); }}
.panel-title {{ color:{text} !important; font-size:18px; font-weight:800; }}
.panel-sub {{ color:{muted} !important; font-size:12px; margin-top:4px; }}

.ai-panel {{ position:relative; overflow:hidden; border-radius:22px; padding:25px; margin-top:22px; background:radial-gradient(circle at 90% 20%,rgba(45,212,191,.18),transparent 30%),linear-gradient(135deg,#102A43,#123B4A); border:1px solid #1E5963; box-shadow:0 14px 35px rgba(2,132,140,.12); }}
.ai-badge {{ display:inline-block; padding:5px 9px; border-radius:999px; background:rgba(45,212,191,.12); color:#5EEAD4 !important; font-size:10px; font-weight:800; letter-spacing:.8px; text-transform:uppercase; }}
.ai-title {{ color:white !important; font-size:22px; font-weight:850; margin-top:10px; }}
.ai-text {{ color:#CBD5E1 !important; font-size:13px; line-height:1.6; max-width:850px; }}
.ai-panel::before {{ content:""; position:absolute; width:170px; height:170px; right:-60px; top:-70px; border-radius:50%; background:rgba(45,212,191,.10); filter:blur(3px); }}

.page-banner {{ padding:22px 24px; border-radius:19px; background:{card}; border:1px solid {border}; box-shadow:{shadow}; margin-bottom:20px; }}
.page-title {{ font-size:27px; font-weight:850; letter-spacing:-.7px; }}
.page-sub {{ color:{muted} !important; font-size:13px; margin-top:4px; }}

.quick-card {{ background:linear-gradient(145deg,{card},{card2}); border:1px solid {border}; border-radius:18px; padding:18px; min-height:105px; transition:transform .2s ease,border-color .2s ease; }}
.quick-card:hover {{ transform:translateY(-3px); border-color:#5EEAD4; }}
.quick-icon {{ font-size:22px; margin-bottom:8px; }}
.quick-title {{ color:{text} !important; font-weight:800; font-size:14px; }}
.quick-sub {{ color:{muted} !important; font-size:11px; margin-top:3px; }}
.progress-shell {{ height:9px; border-radius:999px; background:{border}; overflow:hidden; margin-top:9px; }}
.progress-bar {{ height:100%; border-radius:999px; background:linear-gradient(90deg,#14B8A6,#2DD4BF); }}
.section-kicker {{ color:#0F766E !important; font-size:10px; font-weight:850; letter-spacing:1.3px; text-transform:uppercase; }}

.auth-wrap {{ max-width:980px; margin:45px auto; padding:12px; }}
.auth-card {{ background:{card}; border:1px solid {border}; border-radius:28px; box-shadow:0 20px 60px rgba(15,23,42,.10); overflow:hidden; }}
.auth-brand {{ padding:34px 34px 24px; background:radial-gradient(circle at 100% 0%,rgba(45,212,191,.16),transparent 35%),linear-gradient(135deg,#0F766E,#115E59); color:white; }}
.auth-brand * {{ color:white !important; }}
.auth-logo {{ width:50px; height:50px; display:flex; align-items:center; justify-content:center; border-radius:16px; background:rgba(255,255,255,.14); font-size:26px; margin-bottom:14px; }}
.auth-title {{ font-size:30px; font-weight:850; letter-spacing:-.9px; }}
.auth-sub {{ margin-top:7px; font-size:13px; color:rgba(255,255,255,.78) !important; line-height:1.6; }}
.auth-note {{ background:{card2}; border:1px solid {border}; border-radius:14px; padding:12px 14px; color:{muted} !important; font-size:12px; margin-top:14px; }}
.chat-shell {{ max-width:980px; margin:0 auto; padding-bottom:120px; }}
.chat-header {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:4px 0 16px; border-bottom:1px solid {border}; margin-bottom:18px; }}
.chat-brand {{ font-size:24px; font-weight:850; letter-spacing:-.7px; }}
.chat-model {{ display:inline-flex; align-items:center; gap:6px; padding:6px 10px; border-radius:999px; background:{card2}; border:1px solid {border}; color:{muted} !important; font-size:11px; font-weight:750; }}
.chat-welcome {{ text-align:center; padding:76px 20px 38px; }}
.chat-welcome-icon {{ width:68px; height:68px; margin:0 auto 16px; border-radius:20px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#14B8A6,#0F766E); color:white !important; font-size:32px; box-shadow:0 14px 30px rgba(20,184,166,.22); }}
.chat-welcome-title {{ color:{text} !important; font-size:30px; font-weight:850; letter-spacing:-1px; }}
.chat-welcome-sub {{ color:{muted} !important; font-size:13px; line-height:1.6; max-width:620px; margin:8px auto 22px; }}
.prompt-card {{ background:{card}; border:1px solid {border}; border-radius:15px; padding:14px; text-align:left; min-height:88px; transition:transform .18s ease,border-color .18s ease; }}
.prompt-card:hover {{ transform:translateY(-2px); border-color:#5EEAD4; }}
.prompt-icon {{ font-size:20px; margin-bottom:7px; }}
.prompt-title {{ color:{text} !important; font-size:12px; font-weight:800; }}
.prompt-sub {{ color:{muted} !important; font-size:10px; margin-top:3px; }}
.chat-history-title {{ color:{muted} !important; font-size:10px; font-weight:850; text-transform:uppercase; letter-spacing:1.1px; margin:14px 0 7px; }}
.chat-history-button {{ font-size:11px !important; }}
[data-testid="stChatMessage"] {{ border-radius:18px; padding:8px 14px; }}
.user-box {{ padding:11px 10px; border:1px solid {border}; border-radius:14px; background:{card2}; margin:8px 0 10px; }}
.user-name {{ font-size:13px; font-weight:800; }}
.user-email {{ font-size:10px; color:{muted} !important; overflow-wrap:anywhere; margin-top:2px; }}
.avatar {{ width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:#14B8A6; color:white !important; font-weight:850; margin-right:10px; flex-shrink:0; }}
.user-row {{ display:flex; align-items:center; }}

input, textarea {{ background:{card2} !important; color:{text} !important; caret-color:{text} !important; }}
input::placeholder, textarea::placeholder {{ color:{muted} !important; }}
div[data-baseweb="select"] > div {{ background:{card2} !important; color:{text} !important; border-color:{border} !important; }}
div[data-baseweb="select"] span {{ color:{text} !important; }}
div[data-baseweb="popover"],ul {{ background:{card} !important; }}
li {{ color:{text} !important; }}

[data-testid="stDataFrame"] {{ border:1px solid {border}; border-radius:14px; overflow:hidden; }}
[data-testid="stDataFrame"] * {{ color:{text} !important; }}
[data-testid="stMetric"] {{ background:{card}; border:1px solid {border}; border-radius:15px; padding:10px; }}
hr {{ border-color:{border}; }}

div.stButton > button {{ background:#14B8A6 !important; color:white !important; border:1px solid #0F766E !important; border-radius:11px !important; min-height:42px; font-weight:750; box-shadow:0 6px 14px rgba(20,184,166,.14); transition:.2s ease; }}
div.stButton > button:hover {{ background:#0F766E !important; border-color:#0F766E !important; transform:translateY(-1px); }}
div.stButton > button p,div.stButton > button span {{ color:white !important; }}

@media (max-width:900px) {{ .hero {{ padding:25px; }} .hero-title {{ font-size:28px; }} .panel {{ padding:17px; }} .auth-wrap {{ margin:20px auto; }} }}

/* ============================================================
   STUDIO-GRADE VISUAL SYSTEM
   ============================================================ */
:root {{
  --ss-teal:#14B8A6;
  --ss-teal-deep:#0F766E;
  --ss-teal-soft:#CCFBF1;
}}

/* App shell */
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(circle at 15% 8%, rgba(20,184,166,.055), transparent 22%),
    radial-gradient(circle at 92% 18%, rgba(59,130,246,.045), transparent 24%),
    var(--ss-bg, #F4F7FB) !important;
}}
.main .block-container {{
  max-width: 1480px;
  padding-left: 2.1rem;
  padding-right: 2.1rem;
}}

/* Premium scrollbar */
* {{
  scrollbar-width: thin;
  scrollbar-color: rgba(20,184,166,.38) transparent;
}}
*::-webkit-scrollbar {{ width:8px; height:8px; }}
*::-webkit-scrollbar-track {{ background:transparent; }}
*::-webkit-scrollbar-thumb {{ background:rgba(20,184,166,.35); border-radius:999px; }}
*::-webkit-scrollbar-thumb:hover {{ background:rgba(20,184,166,.55); }}

/* Sidebar */
[data-testid="stSidebar"] {{
  box-shadow: 12px 0 40px rgba(15,23,42,.04);
}}
[data-testid="stSidebarContent"] {{
  padding: 1.05rem .85rem 1rem;
}}
[data-testid="stSidebar"] .brand {{
  padding: .6rem .45rem 1.25rem;
}}
[data-testid="stSidebar"] .brand-name {{
  font-size: 24px;
  letter-spacing: -1px;
}}
[data-testid="stSidebar"] .logo {{
  position:relative;
  overflow:hidden;
  box-shadow:0 10px 28px rgba(20,184,166,.24);
}}
[data-testid="stSidebar"] .logo::after {{
  content:"";
  position:absolute;
  width:70px;
  height:70px;
  top:-45px;
  right:-25px;
  border-radius:50%;
  background:rgba(255,255,255,.18);
}}

/* Sidebar navigation polished as pill items */
[data-testid="stSidebar"] div[role="radiogroup"] {{
  gap: .28rem;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label {{
  border-radius: 13px;
  padding: .55rem .72rem;
  margin: 0;
  border: 1px solid transparent;
  transition: background .18s ease, transform .18s ease, border-color .18s ease;
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
  background: rgba(20,184,166,.07);
  border-color: rgba(20,184,166,.14);
  transform: translateX(2px);
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {{
  background: linear-gradient(90deg, rgba(20,184,166,.14), rgba(20,184,166,.05));
  border-color: rgba(20,184,166,.24);
  box-shadow: inset 3px 0 0 #14B8A6, 0 8px 18px rgba(20,184,166,.06);
}}
[data-testid="stSidebar"] div[role="radiogroup"] > label p {{
  font-size: .86rem;
  font-weight: 720;
}}

/* User account card */
.user-box {{
  box-shadow:0 10px 26px rgba(15,23,42,.045);
  backdrop-filter:blur(10px);
}}
.avatar {{
  box-shadow:0 7px 16px rgba(20,184,166,.22);
}}

/* Global controls */
div.stButton > button,
button[kind="primary"],
button[kind="secondary"] {{
  min-height: 43px;
  border-radius: 12px !important;
  font-weight: 760 !important;
  letter-spacing: -.1px;
}}
div.stButton > button:hover {{
  box-shadow: 0 10px 24px rgba(20,184,166,.18) !important;
}}

/* Inputs */
div[data-baseweb="input"], div[data-baseweb="textarea"] {{
  border-radius: 12px !important;
}}
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {{
  border-radius: 12px !important;
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {{
  border-color:#2DD4BF !important;
  box-shadow:0 0 0 3px rgba(20,184,166,.10) !important;
}}

/* Selects */
div[data-baseweb="select"] > div {{
  border-radius:12px !important;
  min-height:43px;
}}

/* Cards */
.stat-card {{
  position:relative;
  overflow:hidden;
  backdrop-filter:blur(12px);
}}
.stat-card::after {{
  content:"";
  position:absolute;
  width:120px;
  height:120px;
  right:-55px;
  bottom:-65px;
  border-radius:50%;
  background:rgba(20,184,166,.06);
  pointer-events:none;
}}
.quick-card,
.panel,
.page-banner,
.auth-card {{
  backdrop-filter: blur(12px);
}}
.panel,
.page-banner {{
  box-shadow: 0 14px 34px rgba(15,23,42,.055);
}}
.panel:hover,
.stat-card:hover,
.quick-card:hover {{
  box-shadow: 0 18px 40px rgba(15,23,42,.085);
}}

/* Hero polish */
.hero {{
  min-height: 210px;
  display:flex;
  flex-direction:column;
  justify-content:center;
}}
.hero::before {{
  content:"";
  position:absolute;
  width:280px;
  height:280px;
  right:-90px;
  bottom:-130px;
  border:1px solid rgba(255,255,255,.10);
  border-radius:50%;
  box-shadow:0 0 0 38px rgba(255,255,255,.025), 0 0 0 76px rgba(255,255,255,.018);
}}
.hero-title {{ text-shadow:0 2px 18px rgba(0,0,0,.10); }}
.hero-pill {{ backdrop-filter: blur(8px); }}

/* Progress */
.progress-shell {{
  box-shadow: inset 0 1px 2px rgba(15,23,42,.08);
}}
.progress-bar {{
  position:relative;
  box-shadow:0 4px 12px rgba(20,184,166,.22);
}}
.progress-bar::after {{
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(90deg, transparent, rgba(255,255,255,.28), transparent);
  transform:translateX(-100%);
  animation:ssProgressShimmer 2.8s ease-in-out infinite;
}}
@keyframes ssProgressShimmer {{
  0% {{ transform:translateX(-100%); }}
  70%,100% {{ transform:translateX(100%); }}
}}

/* Empty/info states */
[data-testid="stAlert"] {{
  border-radius:14px !important;
  border-width:1px !important;
  box-shadow:0 8px 22px rgba(15,23,42,.04);
}}

/* Dataframes */
[data-testid="stDataFrame"] {{
  box-shadow:0 8px 22px rgba(15,23,42,.04);
}}

/* Chat interface */
.chat-shell {{
  max-width: 1000px;
  margin: 0 auto;
}}
.chat-header {{
  position:sticky;
  top:0;
  z-index:20;
  background:color-mix(in srgb, var(--ss-card, #fff) 86%, transparent);
  backdrop-filter:blur(16px);
  padding: .65rem 0 .85rem;
}}
.chat-brand {{
  font-size:26px;
}}
.chat-model {{
  box-shadow:0 7px 18px rgba(15,23,42,.045);
}}
.chat-welcome {{
  padding-top:68px;
}}
.chat-welcome-icon {{
  position:relative;
  animation:ssFloat 3.6s ease-in-out infinite;
}}
.chat-welcome-icon::after {{
  content:"";
  position:absolute;
  inset:-7px;
  border-radius:23px;
  border:1px solid rgba(20,184,166,.20);
  animation:ssRing 2.8s ease-out infinite;
}}
@keyframes ssFloat {{
  0%,100% {{ transform:translateY(0); }}
  50% {{ transform:translateY(-5px); }}
}}
@keyframes ssRing {{
  0% {{ opacity:.55; transform:scale(1); }}
  100% {{ opacity:0; transform:scale(1.17); }}
}}
.prompt-card {{
  box-shadow:0 10px 24px rgba(15,23,42,.045);
}}

/* Native Streamlit chat bubbles */
[data-testid="stChatMessage"] {{
  border:1px solid rgba(148,163,184,.12);
  box-shadow:0 8px 26px rgba(15,23,42,.035);
  margin-bottom:14px;
}}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
  line-height:1.72;
}}
/* User bubble gets a subtle tinted surface */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
  background:linear-gradient(145deg, rgba(20,184,166,.07), rgba(20,184,166,.025));
}}
/* Assistant bubble stays crisp */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
  background:var(--ss-chat-assistant, rgba(255,255,255,.86));
}}

/* Chat input */
[data-testid="stChatInput"] {{
  max-width:1000px;
  margin-left:auto;
  margin-right:auto;
}}
[data-testid="stChatInput"] > div {{
  border-radius:18px !important;
  border:1px solid rgba(148,163,184,.24) !important;
  box-shadow:0 12px 32px rgba(15,23,42,.09) !important;
  transition:border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}}
[data-testid="stChatInput"] > div:focus-within {{
  border-color:#5EEAD4 !important;
  box-shadow:0 16px 38px rgba(20,184,166,.14), 0 0 0 3px rgba(20,184,166,.07) !important;
  transform:translateY(-1px);
}}
[data-testid="stChatInput"] textarea {{
  min-height:54px !important;
}}

/* Metrics */
[data-testid="stMetric"] {{
  border-radius:16px !important;
  box-shadow:0 9px 22px rgba(15,23,42,.045);
}}

/* Auth screen */
.auth-wrap {{ max-width:1040px; }}
.auth-card {{
  box-shadow:0 26px 80px rgba(15,23,42,.12);
}}
.auth-brand {{
  position:relative;
  overflow:hidden;
}}
.auth-brand::after {{
  content:"";
  position:absolute;
  width:310px;
  height:310px;
  right:-130px;
  top:-180px;
  border-radius:50%;
  border:1px solid rgba(255,255,255,.10);
  box-shadow:0 0 0 35px rgba(255,255,255,.025),0 0 0 70px rgba(255,255,255,.018);
}}
.auth-logo {{
  position:relative;
  z-index:1;
  box-shadow:0 10px 24px rgba(0,0,0,.10);
}}

/* Footer */
footer {{ visibility:hidden; }}

/* Reduced-motion accessibility */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration:.01ms !important;
    animation-iteration-count:1 !important;
    transition-duration:.01ms !important;
    scroll-behavior:auto !important;
  }}
}}

@media (max-width: 900px) {{
  .main .block-container {{ padding-left:1rem; padding-right:1rem; }}
  .hero {{ min-height:180px; }}
  .chat-welcome {{ padding-top:44px; }}
  .chat-brand {{ font-size:21px; }}
}}


/* ============================================================
   EXECUTIVE DASHBOARD / UX POLISH
   ============================================================ */
.dashboard-wrap {{ animation:floatIn .48s ease-out; }}
.dashboard-hero {{
  position:relative; overflow:hidden; display:grid;
  grid-template-columns:minmax(0,1.7fr) minmax(250px,.75fr); gap:24px; align-items:stretch;
  min-height:255px; padding:32px; border-radius:28px; margin-bottom:20px;
  background:radial-gradient(circle at 78% 18%,rgba(45,212,191,.30),transparent 20%),radial-gradient(circle at 96% 72%,rgba(59,130,246,.20),transparent 24%),linear-gradient(135deg,#0B5F59 0%,#0F766E 46%,#10233A 100%);
  box-shadow:0 24px 55px rgba(15,118,110,.20);
}}
.dashboard-hero::before {{
  content:""; position:absolute; width:420px; height:420px; right:-175px; top:-235px; border-radius:50%;
  border:1px solid rgba(255,255,255,.10); box-shadow:0 0 0 34px rgba(255,255,255,.025),0 0 0 68px rgba(255,255,255,.018);
}}
.dashboard-hero-copy {{ position:relative; z-index:2; align-self:center; }}
.dashboard-hero-kicker {{ color:#99F6E4 !important; font-size:10px; font-weight:850; letter-spacing:1.6px; text-transform:uppercase; }}
.dashboard-hero-title {{ color:white !important; font-size:38px; font-weight:880; line-height:1.08; letter-spacing:-1.35px; margin-top:8px; max-width:760px; }}
.dashboard-hero-sub {{ color:rgba(255,255,255,.80) !important; font-size:13px; line-height:1.7; max-width:720px; margin-top:10px; }}
.dashboard-hero-meta {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:17px; }}
.dashboard-pill {{ display:inline-flex; align-items:center; gap:6px; padding:7px 10px; border-radius:999px; background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.15); color:white !important; font-size:10px; font-weight:700; backdrop-filter:blur(10px); }}
.dashboard-orbit {{ position:relative; min-height:190px; display:flex; align-items:center; justify-content:center; z-index:2; }}
.orbit-ring {{ position:absolute; width:178px; height:178px; border-radius:50%; border:1px solid rgba(255,255,255,.11); box-shadow:0 0 0 20px rgba(255,255,255,.02),inset 0 0 25px rgba(45,212,191,.04); }}
.orbit-ring-small {{ width:124px; height:124px; border-color:rgba(45,212,191,.21); }}
.orbit-core {{ width:78px; height:78px; border-radius:24px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#2DD4BF,#14B8A6); color:white !important; font-size:34px; box-shadow:0 16px 34px rgba(0,0,0,.20); animation:ssFloat 3.8s ease-in-out infinite; }}
.orbit-dot {{ position:absolute; width:9px; height:9px; border-radius:50%; background:#99F6E4; box-shadow:0 0 0 7px rgba(153,246,228,.08),0 0 18px rgba(153,246,228,.35); }}
.orbit-dot-one {{ top:12%; right:25%; }}
.orbit-dot-two {{ bottom:15%; left:18%; width:7px; height:7px; background:#93C5FD; box-shadow:0 0 0 7px rgba(147,197,253,.08),0 0 18px rgba(147,197,253,.28); }}
.dashboard-stat-grid {{ margin-bottom:8px; }}
.dashboard-stat {{ position:relative; overflow:hidden; min-height:146px; padding:20px; border-radius:20px; background:{card}; border:1px solid {border}; box-shadow:0 12px 28px rgba(15,23,42,.045); transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease; }}
.dashboard-stat:hover {{ transform:translateY(-4px); border-color:rgba(20,184,166,.36); box-shadow:0 18px 34px rgba(15,23,42,.075); }}
.dashboard-stat::after {{ content:""; position:absolute; width:100px; height:100px; right:-46px; bottom:-55px; border-radius:50%; background:rgba(20,184,166,.07); }}
.dashboard-stat-label {{ color:{muted} !important; font-size:11px; font-weight:750; }}
.dashboard-stat-value {{ color:{text} !important; font-size:31px; font-weight:880; letter-spacing:-1px; margin-top:15px; }}
.dashboard-stat-foot {{ color:{muted} !important; font-size:10px; margin-top:3px; }}
.dashboard-stat-icon {{ width:41px; height:41px; border-radius:13px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#D9FBF6,#C6F6F0); font-size:20px; box-shadow:inset 0 0 0 1px rgba(20,184,166,.10); }}
.dashboard-section {{ margin-top:23px; }}
.dashboard-section-head {{ display:flex; justify-content:space-between; align-items:flex-end; gap:15px; margin-bottom:11px; }}
.dashboard-section-title {{ color:{text} !important; font-size:18px; font-weight:850; letter-spacing:-.4px; }}
.dashboard-section-sub {{ color:{muted} !important; font-size:11px; margin-top:3px; }}
.dashboard-action-panel {{ padding:8px; border-radius:22px; background:{card}; border:1px solid {border}; box-shadow:0 14px 34px rgba(15,23,42,.05); }}
.dashboard-action-panel .stButton {{ margin:0 !important; }}
.dashboard-action-panel div.stButton > button {{ min-height:104px !important; text-align:left !important; padding:17px 18px !important; border-radius:16px !important; border:1px solid transparent !important; background:linear-gradient(145deg,{card},{card2}) !important; color:{text} !important; box-shadow:none !important; }}
.dashboard-action-panel div.stButton > button:hover {{ background:linear-gradient(145deg,{card2},{card}) !important; border-color:rgba(20,184,166,.28) !important; transform:translateY(-2px); box-shadow:0 12px 22px rgba(15,23,42,.07) !important; }}
.dashboard-action-panel div.stButton > button p, .dashboard-action-panel div.stButton > button span {{ color:{text} !important; font-size:13px !important; font-weight:820 !important; }}
.dashboard-focus {{ position:relative; overflow:hidden; padding:23px; border-radius:22px; background:linear-gradient(145deg,{card},{card2}); border:1px solid {border}; box-shadow:0 14px 34px rgba(15,23,42,.05); }}
.dashboard-focus::after {{ content:""; position:absolute; width:180px; height:180px; right:-100px; top:-90px; border-radius:50%; background:rgba(20,184,166,.07); }}
.focus-row {{ display:flex; align-items:center; gap:12px; padding:11px 0; border-bottom:1px solid {border}; }}
.focus-row:last-child {{ border-bottom:0; }}
.focus-icon {{ width:34px; height:34px; border-radius:11px; display:flex; align-items:center; justify-content:center; background:{card2}; border:1px solid {border}; flex-shrink:0; }}
.focus-main {{ min-width:0; flex:1; }}
.focus-name {{ color:{text} !important; font-size:12px; font-weight:780; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.focus-detail {{ color:{muted} !important; font-size:10px; margin-top:2px; }}
.focus-badge {{ padding:5px 8px; border-radius:999px; font-size:9px; font-weight:800; background:rgba(20,184,166,.09); color:#0F766E !important; border:1px solid rgba(20,184,166,.15); white-space:nowrap; }}
.dashboard-progress {{ padding:23px; border-radius:22px; background:{card}; border:1px solid {border}; box-shadow:0 14px 34px rgba(15,23,42,.05); }}
.progress-ring {{ width:116px; height:116px; border-radius:50%; margin:2px auto 0; display:flex; align-items:center; justify-content:center; background:conic-gradient(#14B8A6 calc(var(--progress) * 1%), {border} 0); position:relative; }}
.progress-ring::before {{ content:""; width:88px; height:88px; border-radius:50%; background:{card}; position:absolute; }}
.progress-ring-value {{ position:relative; z-index:1; color:{text} !important; font-size:24px; font-weight:880; }}
.progress-detail {{ text-align:center; color:{muted} !important; font-size:10px; margin-top:8px; }}
.dashboard-empty {{ padding:20px; border:1px dashed {border}; border-radius:16px; color:{muted} !important; font-size:11px; background:{card2}; }}
.dashboard-ai-banner {{ display:flex; align-items:center; justify-content:space-between; gap:18px; padding:21px 23px; border-radius:20px; margin-top:22px; background:linear-gradient(135deg,#0F766E,#115E59 54%,#123047); border:1px solid rgba(94,234,212,.18); box-shadow:0 18px 36px rgba(15,118,110,.16); }}
.dashboard-ai-copy {{ min-width:0; }}
.dashboard-ai-title {{ color:white !important; font-size:16px; font-weight:850; }}
.dashboard-ai-sub {{ color:rgba(255,255,255,.72) !important; font-size:11px; line-height:1.55; margin-top:4px; }}
.dashboard-ai-badge {{ flex-shrink:0; padding:8px 11px; border-radius:999px; background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.14); color:#CCFBF1 !important; font-size:10px; font-weight:800; }}
@media (max-width:900px) {{ .dashboard-hero {{ grid-template-columns:1fr; padding:25px; }} .dashboard-orbit {{ min-height:145px; }} .dashboard-hero-title {{ font-size:29px; }} .dashboard-ai-banner {{ align-items:flex-start; flex-direction:column; }} }}


/* ============================================================
   STUDYSPHERE ELITE UI — FINAL DESIGN OVERRIDES
   ============================================================ */
body {{ scroll-behavior:smooth; }}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display:none !important; }}
.main .block-container {{ max-width:1540px !important; padding:1.15rem 2.4rem 3.5rem !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,{sidebar_bg},{bg}) !important;
  box-shadow:16px 0 48px rgba(15,23,42,.05) !important;
}}
[data-testid="stSidebarContent"] {{ padding:1rem .72rem 1rem !important; }}
[data-testid="stSidebar"] .brand {{ padding:.55rem .42rem 1.18rem !important; }}
[data-testid="stSidebar"] .brand-name {{ font-size:24px; letter-spacing:-1px; }}
[data-testid="stSidebar"] .logo {{
  position:relative; overflow:hidden;
  box-shadow:0 11px 28px rgba(20,184,166,.24) !important;
}}
[data-testid="stSidebar"] .logo::after {{
  content:""; position:absolute; width:70px; height:70px; top:-44px; right:-28px;
  border-radius:50%; background:rgba(255,255,255,.18);
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label {{
  border-radius:12px !important; padding:7px 9px !important; transition:.18s ease !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {{
  background:rgba(20,184,166,.08) !important; transform:translateX(2px);
}}

/* Global controls */
div.stButton > button {{
  min-height:44px !important; border-radius:13px !important;
  background:linear-gradient(135deg,#14B8A6,#0F766E) !important;
  border:1px solid rgba(20,184,166,.22) !important;
  box-shadow:0 8px 18px rgba(20,184,166,.13) !important;
  transition:transform .18s ease, box-shadow .18s ease !important;
}}
div.stButton > button:hover {{
  background:linear-gradient(135deg,#2DD4BF,#0F766E) !important;
  transform:translateY(-2px) !important;
  box-shadow:0 13px 25px rgba(20,184,166,.21) !important;
}}

/* Hero */
.elite-page {{ animation:floatIn .42s ease-out; }}
.elite-hero {{
  position:relative; overflow:hidden; display:grid;
  grid-template-columns:minmax(0,1.5fr) minmax(260px,.75fr); gap:14px;
  min-height:275px; padding:34px; border-radius:30px;
  background:
    radial-gradient(circle at 80% 20%,rgba(45,212,191,.24),transparent 22%),
    radial-gradient(circle at 20% 115%,rgba(96,165,250,.15),transparent 27%),
    linear-gradient(135deg,#082C39,#0F766E 57%,#123047);
  box-shadow:0 26px 62px rgba(15,118,110,.19);
}}
.elite-hero:before {{
  content:""; position:absolute; width:390px; height:390px; right:-155px; top:-195px;
  border-radius:50%; border:1px solid rgba(255,255,255,.10);
  box-shadow:0 0 0 30px rgba(255,255,255,.02),0 0 0 60px rgba(255,255,255,.014);
}}
.elite-copy {{ position:relative; z-index:2; align-self:center; }}
.elite-kicker {{ color:#99F6E4 !important; font-size:10px; font-weight:900; letter-spacing:1.75px; text-transform:uppercase; }}
.elite-title {{ color:white !important; font-size:43px; line-height:1.04; letter-spacing:-1.7px; font-weight:900; margin-top:9px; }}
.elite-title span {{ color:#5EEAD4 !important; }}
.elite-sub {{ color:rgba(255,255,255,.77) !important; font-size:13px; line-height:1.75; margin-top:12px; max-width:710px; }}
.elite-pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
.elite-pill {{ padding:8px 11px; border-radius:999px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.08); color:white !important; font-size:10px; font-weight:750; }}
.elite-orbit {{ position:relative; min-height:215px; display:flex; align-items:center; justify-content:center; z-index:2; }}
.elite-orbit-ring {{ position:absolute; width:184px; height:184px; border-radius:50%; border:1px solid rgba(255,255,255,.12); box-shadow:0 0 0 26px rgba(255,255,255,.02); }}
.elite-orbit-ring.small {{ width:128px; height:128px; border-color:rgba(94,234,212,.20); box-shadow:none; }}
.elite-orbit-core {{ width:92px; height:92px; border-radius:28px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#5EEAD4,#14B8A6); color:#063B3A !important; font-size:38px; box-shadow:0 19px 36px rgba(0,0,0,.22); animation:ssFloat 4s ease-in-out infinite; }}
.elite-orbit-dot {{ position:absolute; width:9px; height:9px; border-radius:50%; background:#99F6E4; box-shadow:0 0 0 7px rgba(153,246,228,.08),0 0 22px rgba(153,246,228,.42); }}
.elite-orbit-dot.one {{ top:18%; right:25%; }}
.elite-orbit-dot.two {{ bottom:17%; left:17%; width:7px; height:7px; background:#93C5FD; box-shadow:0 0 0 7px rgba(147,197,253,.08),0 0 20px rgba(147,197,253,.32); }}

/* KPI cards */
.elite-kpi-grid {{ margin-top:18px; }}
.elite-kpi {{ position:relative; overflow:hidden; min-height:146px; padding:20px; border-radius:22px; background:{card}; border:1px solid {border}; box-shadow:0 14px 32px rgba(15,23,42,.05); transition:.2s ease; }}
.elite-kpi:hover {{ transform:translateY(-4px); border-color:rgba(20,184,166,.34); box-shadow:0 20px 42px rgba(15,23,42,.08); }}
.elite-kpi:after {{ content:""; position:absolute; width:112px; height:112px; right:-58px; bottom:-63px; border-radius:50%; background:rgba(20,184,166,.07); }}
.elite-kpi-top {{ display:flex; align-items:center; justify-content:space-between; }}
.elite-kpi-icon {{ width:43px; height:43px; border-radius:14px; display:flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#DDFBF7,#C8F7F1); font-size:20px; }}
.elite-kpi-label {{ color:{muted} !important; font-size:10px; font-weight:850; letter-spacing:.6px; margin-top:15px; }}
.elite-kpi-value {{ color:{text} !important; font-size:33px; line-height:1; font-weight:900; letter-spacing:-1.3px; margin-top:8px; }}
.elite-kpi-foot {{ color:{muted} !important; font-size:10px; margin-top:6px; }}

/* Sections and actions */
.elite-section {{ margin-top:25px; }}
.elite-section-head {{ display:flex; justify-content:space-between; align-items:flex-end; gap:15px; margin-bottom:11px; }}
.elite-section-title {{ color:{text} !important; font-size:18px; font-weight:900; letter-spacing:-.45px; }}
.elite-section-sub {{ color:{muted} !important; font-size:11px; margin-top:3px; }}
.elite-action-shell {{ padding:8px; border-radius:24px; background:{card}; border:1px solid {border}; box-shadow:0 15px 35px rgba(15,23,42,.045); }}
.elite-action-shell [data-testid="column"] {{ padding:4px; }}
.elite-action-shell div.stButton > button {{ min-height:112px !important; text-align:left !important; justify-content:flex-start !important; align-items:flex-start !important; padding:18px !important; border-radius:17px !important; background:{card2} !important; border:1px solid {border} !important; color:{text} !important; box-shadow:none !important; }}
.elite-action-shell div.stButton > button:hover {{ background:linear-gradient(145deg,{card2},{card}) !important; border-color:rgba(20,184,166,.35) !important; box-shadow:0 12px 24px rgba(15,23,42,.07) !important; }}
.elite-action-shell div.stButton > button p, .elite-action-shell div.stButton > button span {{ color:{text} !important; font-size:13px !important; font-weight:850 !important; }}

/* Panels */
.elite-panel {{ background:{card}; border:1px solid {border}; border-radius:23px; padding:21px; box-shadow:0 15px 36px rgba(15,23,42,.05); }}
.elite-panel-title {{ color:{text} !important; font-size:16px; font-weight:900; }}
.elite-panel-sub {{ color:{muted} !important; font-size:10px; margin-top:4px; }}
.elite-focus-row {{ display:flex; align-items:center; gap:11px; padding:12px 0; border-bottom:1px solid {border}; }}
.elite-focus-row:last-child {{ border-bottom:0; }}
.elite-focus-icon {{ width:35px; height:35px; border-radius:11px; display:flex; align-items:center; justify-content:center; background:{card2}; border:1px solid {border}; flex-shrink:0; }}
.elite-focus-main {{ flex:1; min-width:0; }}
.elite-focus-name {{ color:{text} !important; font-size:12px; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.elite-focus-detail {{ color:{muted} !important; font-size:10px; margin-top:2px; }}
.elite-focus-badge {{ flex-shrink:0; padding:5px 8px; border-radius:999px; background:rgba(20,184,166,.08); color:#0F766E !important; border:1px solid rgba(20,184,166,.14); font-size:9px; font-weight:900; }}

/* Progress */
.elite-progress {{ display:grid; grid-template-columns:145px 1fr; gap:22px; align-items:center; }}
.elite-ring {{ width:126px; height:126px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:conic-gradient(#14B8A6 calc(var(--progress) * 1%), {border} 0); position:relative; }}
.elite-ring:before {{ content:""; width:94px; height:94px; border-radius:50%; background:{card}; position:absolute; }}
.elite-ring-text {{ position:relative; z-index:1; color:{text} !important; font-size:25px; font-weight:900; }}
.elite-progress-copy h4 {{ color:{text} !important; font-size:14px; font-weight:900; margin:0; }}
.elite-progress-copy p {{ color:{muted} !important; font-size:10px; line-height:1.6; margin-top:5px; }}
.elite-mini-bar {{ height:8px; margin-top:10px; border-radius:999px; background:{border}; overflow:hidden; }}
.elite-mini-fill {{ height:100%; border-radius:999px; background:linear-gradient(90deg,#14B8A6,#5EEAD4); }}

/* AI banner */
.elite-ai {{ position:relative; overflow:hidden; display:flex; align-items:center; justify-content:space-between; gap:20px; margin-top:24px; padding:23px 25px; border-radius:22px; background:linear-gradient(135deg,#082E3A,#0F766E 56%,#123047); border:1px solid rgba(94,234,212,.18); box-shadow:0 21px 44px rgba(15,118,110,.16); }}
.elite-ai:after {{ content:""; position:absolute; right:-75px; top:-90px; width:220px; height:220px; border-radius:50%; border:1px solid rgba(255,255,255,.08); box-shadow:0 0 0 25px rgba(255,255,255,.018),0 0 0 50px rgba(255,255,255,.012); }}
.elite-ai-copy {{ position:relative; z-index:2; }}
.elite-ai-title {{ color:white !important; font-size:17px; font-weight:900; }}
.elite-ai-sub {{ color:rgba(255,255,255,.72) !important; font-size:11px; line-height:1.6; margin-top:4px; }}
.elite-ai-badge {{ position:relative; z-index:2; flex-shrink:0; padding:8px 11px; border-radius:999px; color:#CCFBF1 !important; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); font-size:10px; font-weight:850; }}

/* Better Streamlit data tables */
[data-testid="stDataFrame"] {{ border-radius:15px !important; overflow:hidden !important; border:1px solid {border} !important; box-shadow:0 8px 20px rgba(15,23,42,.035); }}

@media (max-width:950px) {{
  .elite-hero {{ grid-template-columns:1fr; padding:25px; }}
  .elite-orbit {{ min-height:155px; }}
  .elite-title {{ font-size:31px; }}
  .elite-progress {{ grid-template-columns:1fr; justify-items:center; text-align:center; }}
  .elite-ai {{ align-items:flex-start; flex-direction:column; }}
  .main .block-container {{ padding-left:1rem !important; padding-right:1rem !important; }}
}}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# LOCAL AUTHENTICATION HELPERS
# ============================================================

PBKDF2_ITERATIONS = 260000
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def hash_secret(secret_value, salt_hex=None):
    if salt_hex:
        salt = bytes.fromhex(salt_hex)
    else:
        salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        secret_value.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return salt.hex(), derived.hex()


def verify_secret(secret_value, salt_hex, expected_hash):
    if not salt_hex or not expected_hash:
        return False
    _, derived_hex = hash_secret(secret_value, salt_hex)
    return hmac.compare_digest(derived_hex, expected_hash)


def generate_recovery_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))


def clean_name(value):
    return " ".join(str(value or "").strip().split())


def clean_email(value):
    return str(value or "").strip().lower()


def valid_email(value):
    return bool(EMAIL_PATTERN.fullmatch(clean_email(value)))


def set_authenticated_user(auth_id, name, email):
    st.session_state.auth_id = str(auth_id)
    st.session_state.display_name = clean_name(name) or clean_email(email).split("@")[0].title()
    st.session_state.email = clean_email(email)
    # One application-wide Gemini key is reused for every authenticated user.
    st.session_state.ai_api_key = GLOBAL_GEMINI_API_KEY
    st.session_state.ai_messages = []
    st.session_state.page = 1
    st.session_state.show_login = "Sign in"


def call_gemini_agent(api_key, prompt, model="gemini-3.1-flash-lite"):
    api_key = str(api_key or "").strip()
    if not api_key:
        return "The AI service is temporarily unavailable. Please try again later."

    models_to_try = []
    for candidate in [model, "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-2.5-flash-lite"]:
        if candidate not in models_to_try:
            models_to_try.append(candidate)

    last_message = "Gemini could not generate a response."
    last_code = None

    for current_model in models_to_try:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": "You are StudySphere AI Agent, an academic assistant for a university student. Use the student's stored StudySphere data as the primary context. Do not invent deadlines, exams, subjects, or scores. Be practical and concise. Explain educational concepts clearly instead of blindly giving answers. When prioritizing, consider exam dates, assignment deadlines, unfinished study tasks, and stated priorities. If the data is insufficient, say exactly what is missing."
                    }
                ]
            },
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1800,
            },
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read().decode("utf-8")
            data = json.loads(raw)
            candidates = data.get("candidates") or []
            if not candidates:
                feedback = data.get("promptFeedback") or {}
                block_reason = feedback.get("blockReason")
                if block_reason:
                    return f"Gemini blocked this request. Reason: {block_reason}."
                last_message = "Gemini returned an empty response."
                continue

            parts = ((candidates[0].get("content") or {}).get("parts") or [])
            text_parts = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
            answer = "".join(text_parts).strip()
            if answer:
                return answer
            last_message = "Gemini returned an empty response."

        except urllib.error.HTTPError as exc:
            last_code = exc.code
            try:
                detail = exc.read().decode("utf-8")
                parsed = json.loads(detail)
                error_info = parsed.get("error") or {}
                message = error_info.get("message", "Gemini request failed.")
                status = error_info.get("status", "")
            except Exception:
                message = "Gemini request failed."
                status = ""

            last_message = f"{message}"

            # A model-specific 404 can happen when a newly created API key/project
            # does not currently have access to that model. Try the next model.
            if exc.code == 404:
                continue

            if exc.code == 400:
                return f"Gemini rejected the request: {message}"
            if exc.code in (401, 403):
                return "The AI service could not authenticate this request. Please try again later."
            if exc.code == 429:
                return "Gemini rate limit reached. Please wait a little and try again."
            if status:
                return f"Gemini service error ({status}): {message}"
            return f"Gemini service error: {message}"
        except urllib.error.URLError as exc:
            return f"Could not reach Gemini. Check your internet connection. Details: {exc.reason}"
        except Exception as exc:
            return f"Unexpected Gemini error: {type(exc).__name__}: {exc}"

    if last_code == 404:
        return "The AI service is currently unavailable. Please try again later."
    return last_message


def make_chat_title(message):
    text_value = " ".join(str(message or "").strip().split())
    if not text_value:
        return "New chat"
    return text_value[:42] + ("…" if len(text_value) > 42 else "")


def create_chat_session(user_id, title="New chat"):
    chat_id = uuid.uuid4().hex
    now = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_id, title, now, now),
    )
    conn.commit()
    return chat_id


def ensure_active_chat(user_id):
    active_id = st.session_state.get("active_chat_id")
    if active_id:
        exists = cursor.execute(
            "SELECT 1 FROM chat_sessions WHERE id = ? AND user_id = ?",
            (active_id, user_id),
        ).fetchone()
        if exists:
            return active_id

    latest = cursor.execute(
        "SELECT id FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    if latest:
        st.session_state.active_chat_id = latest[0]
        return latest[0]

    new_id = create_chat_session(user_id)
    st.session_state.active_chat_id = new_id
    return new_id


def list_chat_sessions(user_id):
    return cursor.execute(
        "SELECT id, title, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 30",
        (user_id,),
    ).fetchall()


def load_chat_messages(chat_id, user_id):
    return cursor.execute(
        "SELECT role, content, created_at FROM chat_messages WHERE chat_id = ? AND user_id = ? ORDER BY id",
        (chat_id, user_id),
    ).fetchall()


def save_chat_message(chat_id, user_id, role, content):
    now = datetime.now().isoformat(timespec="seconds")
    cursor.execute(
        "INSERT INTO chat_messages (chat_id, user_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (chat_id, user_id, role, content, now),
    )
    cursor.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ? AND user_id = ?",
        (now, chat_id, user_id),
    )
    conn.commit()


def update_chat_title(chat_id, user_id, title):
    cursor.execute(
        "UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ? AND user_id = ?",
        (make_chat_title(title), datetime.now().isoformat(timespec="seconds"), chat_id, user_id),
    )
    conn.commit()


def delete_chat_session(chat_id, user_id):
    cursor.execute(
        "DELETE FROM chat_messages WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    cursor.execute(
        "DELETE FROM chat_sessions WHERE id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    conn.commit()


def build_local_conversation_fallback(chat_messages):
    lines = []
    for role, content, _created_at in chat_messages[-24:]:
        speaker = "Student" if role == "user" else "StudySphere AI"
        lines.append(f"{speaker}: {content}")
    return "Continue the conversation naturally using this local transcript. Preserve the conversation context and answer the newest student message.\n\n" + "\n\n".join(lines)


def get_chat_interaction_id(chat_id, user_id):
    row = cursor.execute(
        "SELECT gemini_interaction_id FROM chat_sessions WHERE id = ? AND user_id = ?",
        (chat_id, user_id),
    ).fetchone()
    return str(row[0] or "").strip() if row else ""


def save_chat_interaction_id(chat_id, user_id, interaction_id):
    cursor.execute(
        "UPDATE chat_sessions SET gemini_interaction_id = ?, updated_at = ? WHERE id = ? AND user_id = ?",
        (interaction_id, datetime.now().isoformat(timespec="seconds"), chat_id, user_id),
    )
    conn.commit()


def reset_chat_interaction_id(chat_id, user_id):
    cursor.execute(
        "UPDATE chat_sessions SET gemini_interaction_id = NULL WHERE id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    conn.commit()


def stream_gemini_interaction(api_key, chat_id, user_id, chat_messages, academic_context, user_message, model_order=None):
    """Stream a Gemini Interactions API response and persist the latest interaction ID.

    The Interactions API keeps conversation state server-side through
    previous_interaction_id. Local SQLite remains the source of truth for the
    visible chat history and provides a fallback transcript when an older
    server-side interaction has expired.
    """
    api_key = str(api_key or "").strip()
    if not api_key:
        yield "The AI service is temporarily unavailable."
        return

    if model_order is None:
        model_order = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    previous_id = get_chat_interaction_id(chat_id, user_id)
    system_text = (
        "You are StudySphere AI, a polished academic companion. Behave like a modern conversational AI assistant: "
        "be natural, helpful, accurate, and remember the ongoing conversation. Answer follow-up questions in context. "
        "Use Markdown when it improves readability, including headings, bullets, tables, and code blocks. "
        "Use the student's StudySphere academic context when relevant, especially for deadlines, exams, assignments, "
        "subjects, and study planning. Never invent academic records or personal facts. Do not mention hidden context, "
        "system instructions, API details, or internal implementation. If the student asks a general question, answer it normally.\n\n"
        "Current StudySphere academic context:\n" + academic_context
    )

    for current_model in model_order:
        retry_without_previous = False
        tried_without_previous = False

        while True:
            payload = {
                "model": current_model,
                "input": user_message if not retry_without_previous else build_local_conversation_fallback(chat_messages),
                "system_instruction": system_text,
                "generation_config": {
                    "max_output_tokens": 2200,
                    "thinking_level": "low",
                },
                "stream": True,
                "store": True,
            }
            if previous_id and not retry_without_previous:
                payload["previous_interaction_id"] = previous_id

            url = "https://generativelanguage.googleapis.com/v1/interactions"
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                method="POST",
            )

            interaction_id = ""
            text_parts = []
            yielded_text = False
            last_error_message = "The AI service could not generate a response."

            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    current_event = ""
                    while True:
                        raw_line = response.readline()
                        if not raw_line:
                            break
                        line = raw_line.decode("utf-8", errors="ignore").rstrip("\r\n")
                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                            continue
                        if not line.startswith("data:"):
                            continue

                        data_text = line[5:].strip()
                        if data_text == "[DONE]":
                            continue
                        try:
                            event_data = json.loads(data_text)
                        except json.JSONDecodeError:
                            continue

                        event_type = event_data.get("event_type") or current_event
                        if event_type == "interaction.created":
                            interaction = event_data.get("interaction") or {}
                            interaction_id = str(interaction.get("id") or "")
                        elif event_type == "step.delta":
                            delta = event_data.get("delta") or {}
                            if delta.get("type") == "text" and delta.get("text"):
                                chunk = str(delta.get("text"))
                                text_parts.append(chunk)
                                yielded_text = True
                                yield chunk
                        elif event_type == "interaction.completed":
                            interaction = event_data.get("interaction") or {}
                            interaction_id = str(interaction.get("id") or interaction_id)
                        elif event_type == "interaction.failed":
                            error = event_data.get("error") or {}
                            last_error_message = str(error.get("message") or "The AI service could not generate a response.")

                answer_exists = bool("".join(text_parts).strip())
                if answer_exists:
                    if interaction_id:
                        save_chat_interaction_id(chat_id, user_id, interaction_id)
                    return

                if retry_without_previous:
                    last_error_message = "The AI returned an empty response."
                else:
                    last_error_message = "The AI returned an empty response."

            except urllib.error.HTTPError as exc:
                try:
                    detail = exc.read().decode("utf-8", errors="ignore")
                    parsed = json.loads(detail)
                    error_info = parsed.get("error") or {}
                    api_message = str(error_info.get("message") or "Gemini request failed.")
                except Exception:
                    api_message = "Gemini request failed."

                if exc.code == 404 and previous_id and not tried_without_previous:
                    # A free-tier Interactions object may have expired, while our
                    # local SQLite chat still exists. Rebuild context from local history.
                    tried_without_previous = True
                    retry_without_previous = True
                    continue

                if exc.code == 404:
                    last_error_message = "The selected Gemini model is currently unavailable."
                    break
                if exc.code in (401, 403):
                    yield "The AI service could not authenticate the request. Please check the Gemini API key configured for StudySphere."
                    return
                if exc.code == 429:
                    yield "Gemini rate limit reached. Please wait a little and try again."
                    return
                if exc.code == 400:
                    yield f"Gemini rejected the request: {api_message}"
                    return
                yield "The AI service encountered an error. Please try again."
                return
            except urllib.error.URLError:
                yield "Could not reach Gemini. Please check the app's internet connection and try again."
                return
            except Exception:
                yield "The AI service encountered an unexpected error. Please try again."
                return

            # If this model produced no useful output, move to the next compatible model.
            if not yielded_text:
                break
            return

        # Try the next model after a model-level 404.
        previous_id = ""

    yield "The AI service is currently unavailable. Please try again later."


def academic_context_for_chat(auth_id):
    return format_agent_context(build_agent_context(auth_id))


def render_chat_history_sidebar(user_id):
    st.sidebar.markdown('<div class="chat-history-title">Your conversations</div>', unsafe_allow_html=True)
    sessions = list_chat_sessions(user_id)
    for session_id, title, _updated_at in sessions:
        label = f"💬 {title or 'New chat'}"
        is_active = session_id == st.session_state.active_chat_id
        button_label = ("● " if is_active else "  ") + label
        if st.sidebar.button(button_label, key=f"chat_history_{session_id}", use_container_width=True):
            st.session_state.active_chat_id = session_id
            st.session_state.page = 7
            st.rerun()

def build_agent_context(auth_id):
    subjects = cursor.execute(
        "SELECT name, code, instructor FROM subjects WHERE user_id = ? ORDER BY name",
        (auth_id,),
    ).fetchall()
    assignments = cursor.execute(
        "SELECT title, deadline, priority, status, description FROM assignments WHERE user_id = ? ORDER BY deadline LIMIT 12",
        (auth_id,),
    ).fetchall()
    exams = cursor.execute(
        "SELECT title, exam_date, syllabus, notes FROM exams WHERE user_id = ? AND exam_date >= ? ORDER BY exam_date LIMIT 12",
        (auth_id, str(date.today())),
    ).fetchall()
    tasks = cursor.execute(
        "SELECT title, task_date, duration, priority, completed FROM tasks WHERE user_id = ? ORDER BY task_date LIMIT 20",
        (auth_id,),
    ).fetchall()
    return {
        "today": str(date.today()),
        "subjects": subjects,
        "assignments": assignments,
        "upcoming_exams": exams,
        "study_tasks": tasks,
    }


def format_agent_context(context):
    return json.dumps(context, ensure_ascii=False, indent=2, default=str)


def clear_authenticated_user():
    st.session_state.auth_id = None
    st.session_state.display_name = ""
    st.session_state.email = ""
    st.session_state.ai_api_key = ""
    st.session_state.ai_messages = []
    st.session_state.active_chat_id = None
    st.session_state.page = 1


def current_user_from_session():
    auth_id = st.session_state.get("auth_id")
    if not auth_id:
        return None
    row = cursor.execute(
        "SELECT auth_id, name, email FROM users WHERE auth_id = ?",
        (auth_id,),
    ).fetchone()
    return row


def migrate_legacy_rows_to_first_local_account(auth_id):
    # The previous StudySphere version could already contain rows without local authentication.
    # Keep that data available to the first local account instead of deleting or resetting it.
    local_account_count = cursor.execute(
        "SELECT COUNT(*) FROM users WHERE password_hash IS NOT NULL"
    ).fetchone()[0]
    if local_account_count == 1:
        for table_name in ["subjects", "assignments", "exams", "tasks"]:
            cursor.execute(
                f"UPDATE {table_name} SET user_id = ? WHERE user_id IS NULL OR user_id = ''",
                (auth_id,),
            )
        conn.commit()


def render_auth_screen():
    st.markdown('<div class="auth-wrap"><div class="auth-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-brand"><div class="auth-logo">🎓</div><div class="auth-title">Welcome to StudySphere</div><div class="auth-sub">Your focused academic workspace for subjects, assignments, exams and study planning.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="padding:26px 30px 30px;">', unsafe_allow_html=True)

    tabs = ["Sign in", "Create account", "Forgot password"]
    tab = st.radio(
        "Account",
        tabs,
        index=tabs.index(st.session_state.show_login) if st.session_state.show_login in tabs else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.show_login = tab

    if tab == "Sign in":
        st.markdown("### Sign in")
        email = st.text_input("Email address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        sign_in = st.button("🔐 Sign in", use_container_width=True)

        if sign_in:
            email = clean_email(email)
            if not email or not password:
                st.error("Enter both your email and password.")
            elif not valid_email(email):
                st.error("Enter a valid email address.")
            else:
                account = cursor.execute(
                    "SELECT auth_id, name, email, password_hash, password_salt FROM users WHERE lower(email) = ?",
                    (email,),
                ).fetchone()
                if not account:
                    st.error("No StudySphere account was found for that email.")
                elif not account[3] or not account[4]:
                    st.error("This account needs to be created again in the new local authentication system.")
                elif not verify_secret(password, account[4], account[3]):
                    st.error("Incorrect email or password.")
                else:
                    set_authenticated_user(account[0], account[1], account[2])
                    st.success("Signed in successfully.")
                    st.rerun()

        st.markdown(
            '<div class="auth-note">Your password is stored locally using a salted PBKDF2-SHA256 hash. StudySphere does not store your plain-text password.</div>',
            unsafe_allow_html=True,
        )

    elif tab == "Create account":
        st.markdown("### Create your account")
        name = st.text_input("Full name", key="signup_name")
        email = st.text_input("Email address", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
        create_account = st.button("✨ Create account", use_container_width=True)

        if create_account:
            name = clean_name(name)
            email = clean_email(email)
            if not name or not email or not password or not confirm:
                st.error("Please complete all fields.")
            elif not valid_email(email):
                st.error("Enter a valid email address.")
            elif len(password) < 8:
                st.error("Use a password with at least 8 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                existing = cursor.execute(
                    "SELECT auth_id, name, password_hash FROM users WHERE lower(email) = ?",
                    (email,),
                ).fetchone()
                if existing and existing[2]:
                    st.error("An account with this email already exists. Please sign in instead.")
                else:
                    auth_id = existing[0] if existing else f"local-{uuid.uuid4().hex}"
                    password_salt, password_hash = hash_secret(password)
                    recovery_code = generate_recovery_code()
                    recovery_salt, recovery_hash = hash_secret(recovery_code)
                    try:
                        if existing:
                            cursor.execute(
                                "UPDATE users SET name = ?, email = ?, password_hash = ?, password_salt = ?, recovery_hash = ?, recovery_salt = ? WHERE auth_id = ?",
                                (name, email, password_hash, password_salt, recovery_hash, recovery_salt, auth_id),
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO users (auth_id, name, email, password_hash, password_salt, recovery_hash, recovery_salt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (auth_id, name, email, password_hash, password_salt, recovery_hash, recovery_salt),
                            )
                        conn.commit()
                        migrate_legacy_rows_to_first_local_account(auth_id)
                        st.session_state.signup_recovery_code = recovery_code
                        set_authenticated_user(auth_id, name, email)
                        st.success("Account created successfully.")
                        st.info("Save your recovery code somewhere safe. You will need it if you forget your password.")
                        st.code(recovery_code)
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("That email is already registered. Try signing in instead.")
                    except Exception as exc:
                        st.error(f"Account creation failed: {str(exc)}")

    else:
        st.markdown("### Reset your password")
        st.caption("No email service is required. Use the recovery code shown when your account was created.")
        email = st.text_input("Account email", key="reset_email")
        recovery_code = st.text_input("Recovery code", key="reset_code")
        new_password = st.text_input("New password", type="password", key="reset_password")
        confirm_password = st.text_input("Confirm new password", type="password", key="reset_confirm")
        reset = st.button("🔑 Reset password", use_container_width=True)

        if reset:
            email = clean_email(email)
            recovery_code = recovery_code.strip().upper()
            account = cursor.execute(
                "SELECT auth_id, name, email, recovery_hash, recovery_salt FROM users WHERE lower(email) = ?",
                (email,),
            ).fetchone()
            if not email or not recovery_code or not new_password or not confirm_password:
                st.error("Please complete all fields.")
            elif not valid_email(email):
                st.error("Enter a valid email address.")
            elif len(new_password) < 8:
                st.error("Use a password with at least 8 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not account or not verify_secret(recovery_code, account[4], account[3]):
                st.error("The email or recovery code is incorrect.")
            else:
                password_salt, password_hash = hash_secret(new_password)
                new_recovery_code = generate_recovery_code()
                recovery_salt, recovery_hash = hash_secret(new_recovery_code)
                cursor.execute(
                    "UPDATE users SET password_hash = ?, password_salt = ?, recovery_hash = ?, recovery_salt = ? WHERE auth_id = ?",
                    (password_hash, password_salt, recovery_hash, recovery_salt, account[0]),
                )
                conn.commit()
                set_authenticated_user(account[0], account[1], account[2])
                st.session_state.reset_recovery_code = new_recovery_code
                st.success("Password reset successfully.")
                st.info("Your recovery code has been rotated. Save the new code safely.")
                st.code(new_recovery_code)
                st.rerun()

    st.markdown('</div></div></div>', unsafe_allow_html=True)


current_user = current_user_from_session()

if not current_user:
    render_auth_screen()
    conn.close()
    st.stop()

AUTH_ID = str(current_user[0])
DISPLAY_NAME = str(current_user[1] or "Student")
EMAIL = str(current_user[2] or "")

# Load the single application-wide Gemini key silently.
# It is never displayed and is not tied to the currently signed-in account.
st.session_state.ai_api_key = GLOBAL_GEMINI_API_KEY

# Keep the name/email in session synchronized with the database.
st.session_state.display_name = DISPLAY_NAME
st.session_state.email = EMAIL
ensure_active_chat(AUTH_ID)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
<div class="brand">
<div class="logo-row"><div class="logo">🎓</div><div class="brand-name">StudySphere</div></div>
<div class="brand-tag">Learn smarter. Plan better. Achieve more.</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="sidebar-label">Account</div>', unsafe_allow_html=True)
initial = DISPLAY_NAME[:1].upper() if DISPLAY_NAME else "S"
st.sidebar.markdown(
    f'<div class="user-box"><div class="user-row"><div class="avatar">{initial}</div><div><div class="user-name">{DISPLAY_NAME}</div><div class="user-email">{EMAIL}</div></div></div></div>',
    unsafe_allow_html=True,
)

logout = st.sidebar.button("🚪 Sign out", use_container_width=True)
if logout:
    clear_authenticated_user()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)

nav_options = [
    (1, "🏠  Dashboard"),
    (2, "📚  Subjects"),
    (3, "📝  Assignments"),
    (4, "📅  Exams"),
    (5, "✅  Study Planner"),
    (6, "👤  Profile"),
    (7, "🤖  AI Agent"),
]
nav_labels = [item[1] for item in nav_options]
selected_label = st.sidebar.radio("Navigation", nav_labels, index=[x[0] for x in nav_options].index(st.session_state.page), label_visibility="collapsed")
st.session_state.page = dict((label, page_id) for page_id, label in nav_options)[selected_label]

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-label">Intelligence</div>', unsafe_allow_html=True)
st.sidebar.markdown("### 🤖 StudySphere AI")
st.sidebar.caption("A conversational academic assistant that remembers your chats.")
if st.sidebar.button("＋ New chat", key="new_chat_sidebar", use_container_width=True):
    st.session_state.active_chat_id = create_chat_session(AUTH_ID)
    st.session_state.ai_messages = []
    st.session_state.page = 7
    st.rerun()
render_chat_history_sidebar(AUTH_ID)

dark_mode_toggle = st.sidebar.toggle("Dark mode", value=st.session_state.dark_mode)
if dark_mode_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode_toggle
    st.rerun()

# ============================================================
# DASHBOARD DATA
# ============================================================

cursor.execute("SELECT COUNT(*) FROM subjects WHERE user_id = ?", (AUTH_ID,))
subject_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM assignments WHERE user_id = ?", (AUTH_ID,))
assignment_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM exams WHERE user_id = ? AND exam_date >= ?", (AUTH_ID, str(date.today()),))
exam_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 0", (AUTH_ID,))
pending_task_count = cursor.fetchone()[0]

# ============================================================
# PAGES
# ============================================================


if st.session_state.page == 1:
    st.markdown('<div class="elite-page">', unsafe_allow_html=True)
    first_name = DISPLAY_NAME.split()[0] if DISPLAY_NAME.strip() else "Student"
    today_text = str(date.today())
    upcoming_assignments = cursor.execute(
        "SELECT title, deadline, priority, status FROM assignments WHERE user_id = ? ORDER BY deadline LIMIT 6",
        (AUTH_ID,),
    ).fetchall()
    upcoming_exams = cursor.execute(
        "SELECT title, exam_date, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id WHERE exams.user_id = ? AND exams.exam_date >= ? ORDER BY exams.exam_date LIMIT 6",
        (AUTH_ID, today_text),
    ).fetchall()
    focus_tasks = cursor.execute(
        "SELECT tasks.title, tasks.task_date, tasks.duration, tasks.priority, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id WHERE tasks.user_id = ? AND tasks.completed = 0 ORDER BY CASE tasks.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, tasks.task_date LIMIT 5",
        (AUTH_ID,),
    ).fetchall()
    completed_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 1", (AUTH_ID,)).fetchone()[0]
    total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (AUTH_ID,)).fetchone()[0]
    task_progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    st.markdown(
        f'''<div class="elite-hero">
  <div class="elite-copy">
    <div class="elite-kicker">Personal academic command center</div>
    <div class="elite-title">Good morning, <span>{first_name}</span> 👋</div>
    <div class="elite-sub">A calm, focused workspace for your subjects, deadlines, exams and daily study goals. Everything important is visible without the clutter.</div>
    <div class="elite-pills"><span class="elite-pill">✦ {today_text}</span><span class="elite-pill">🎓 Student workspace</span><span class="elite-pill">⚡ {pending_task_count} open tasks</span></div>
  </div>
  <div class="elite-orbit" aria-hidden="true"><div class="elite-orbit-ring"></div><div class="elite-orbit-ring small"></div><div class="elite-orbit-core">🎓</div><span class="elite-orbit-dot one"></span><span class="elite-orbit-dot two"></span></div>
</div>''', unsafe_allow_html=True)

    st.markdown('<div class="elite-kpi-grid">', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="elite-kpi"><div class="elite-kpi-top"><div class="elite-kpi-icon">📚</div></div><div class="elite-kpi-label">YOUR SUBJECTS</div><div class="elite-kpi-value">{subject_count}</div><div class="elite-kpi-foot">Courses currently organized</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="elite-kpi"><div class="elite-kpi-top"><div class="elite-kpi-icon">📝</div></div><div class="elite-kpi-label">ASSIGNMENTS</div><div class="elite-kpi-value">{assignment_count}</div><div class="elite-kpi-foot">Deadlines in your workspace</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="elite-kpi"><div class="elite-kpi-top"><div class="elite-kpi-icon">🎯</div></div><div class="elite-kpi-label">UPCOMING EXAMS</div><div class="elite-kpi-value">{exam_count}</div><div class="elite-kpi-foot">Future exam dates</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="elite-kpi"><div class="elite-kpi-top"><div class="elite-kpi-icon">✓</div></div><div class="elite-kpi-label">PENDING TASKS</div><div class="elite-kpi-value">{pending_task_count}</div><div class="elite-kpi-foot">Study actions still open</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="elite-section"><div class="elite-section-head"><div><div class="elite-section-title">Quick actions</div><div class="elite-section-sub">Your most-used StudySphere destinations, one click away.</div></div></div><div class="elite-action-shell">', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    go_ai = a1.button("🤖  Ask AI Tutor\nGet help with difficult topics", key="elite_dash_ai", use_container_width=True)
    go_subjects = a2.button("📚  Manage Subjects\nOrganize your courses", key="elite_dash_subjects", use_container_width=True)
    go_exams = a3.button("🎯  Exam Focus\nView upcoming exams", key="elite_dash_exams", use_container_width=True)
    go_planner = a4.button("⚡  Study Planner\nBuild today's focus", key="elite_dash_planner", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if go_ai:
        st.session_state.page = 7
        st.rerun()
    if go_subjects:
        st.session_state.page = 2
        st.rerun()
    if go_exams:
        st.session_state.page = 4
        st.rerun()
    if go_planner:
        st.session_state.page = 5
        st.rerun()

    st.markdown('<div class="elite-section"><div class="elite-section-head"><div><div class="elite-section-title">Today at a glance</div><div class="elite-section-sub">See what needs your attention and how far you have progressed.</div></div></div>', unsafe_allow_html=True)
    focus_col, progress_col = st.columns([1.55, 1])
    with focus_col:
        st.markdown('<div class="elite-panel"><div class="elite-panel-title">🔥 Priority queue</div><div class="elite-panel-sub">Unfinished tasks are ordered by priority first.</div>', unsafe_allow_html=True)
        if focus_tasks:
            for task_title_value, task_day, task_minutes, task_priority_value, task_subject_value in focus_tasks:
                st.markdown(f'<div class="elite-focus-row"><div class="elite-focus-icon">📖</div><div class="elite-focus-main"><div class="elite-focus-name">{task_title_value}</div><div class="elite-focus-detail">{task_subject_value or "General"} • {task_day} • {task_minutes} min</div></div><div class="elite-focus-badge">{task_priority_value or "Medium"}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="dashboard-empty" style="margin-top:14px;">🎉 You are all caught up. Add a study task whenever you are ready.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with progress_col:
        st.markdown('<div class="elite-panel"><div class="elite-panel-title">📈 Study progress</div><div class="elite-panel-sub">Your current task completion pace.</div><div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="elite-progress"><div class="elite-ring" style="--progress:{task_progress};"><div class="elite-ring-text">{task_progress}%</div></div><div class="elite-progress-copy"><h4>{completed_tasks} of {total_tasks} tasks complete</h4><p>Small, consistent progress compounds. Finish your next task and keep your momentum going.</p><div class="elite-mini-bar"><div class="elite-mini-fill" style="width:{task_progress}%;"></div></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="elite-section"><div class="elite-section-head"><div><div class="elite-section-title">Deadlines & exam radar</div><div class="elite-section-sub">The next academic items saved to your account.</div></div></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        st.markdown('<div class="elite-panel"><div class="elite-panel-title">📝 Upcoming assignments</div><div class="elite-panel-sub">Your nearest assignment deadlines.</div>', unsafe_allow_html=True)
        if upcoming_assignments:
            st.dataframe(upcoming_assignments, use_container_width=True, hide_index=True, column_config={"title":"Assignment","deadline":"Deadline","priority":"Priority","status":"Status"})
        else:
            st.markdown('<div class="dashboard-empty" style="margin-top:14px;">No assignments yet. Add your first one to start tracking deadlines.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="elite-panel"><div class="elite-panel-title">🎯 Upcoming exams</div><div class="elite-panel-sub">Your next exam dates and subjects.</div>', unsafe_allow_html=True)
        if upcoming_exams:
            exam_rows = [(row[0], row[1], row[2] or "General") for row in upcoming_exams]
            st.dataframe(exam_rows, use_container_width=True, hide_index=True, column_config={"title":"Exam","exam_date":"Exam Date","name":"Subject"})
        else:
            st.markdown('<div class="dashboard-empty" style="margin-top:14px;">No upcoming exams have been added yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="elite-ai"><div class="elite-ai-copy"><div class="elite-ai-title">🤖 Your StudySphere AI is ready</div><div class="elite-ai-sub">Ask questions, analyze your workload, or build a focused plan using the academic data already inside your account.</div></div><div class="elite-ai-badge">Connected • Gemini</div></div>', unsafe_allow_html=True)
    open_ai = st.button("Open AI Agent", key="elite_dash_open_ai", use_container_width=True)
    if open_ai:
        st.session_state.page = 7
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 2:
    st.markdown('<div class="page-banner"><div class="page-title">📚 Subjects</div><div class="page-sub">Build your academic workspace by adding your university subjects.</div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    subject_name = a.text_input("Subject Name")
    subject_code = b.text_input("Subject Code")
    subject_instructor = c.text_input("Instructor")
    add_subject = st.button("➕ Add Subject", use_container_width=True)

    if add_subject:
        if not subject_name.strip():
            st.error("Please enter a subject name.")
        else:
            cursor.execute("INSERT INTO subjects (name, code, instructor, user_id) VALUES (?, ?, ?, ?)", (subject_name.strip(), subject_code.strip(), subject_instructor.strip(), AUTH_ID))
            conn.commit()
            st.success("Subject added successfully.")
            st.rerun()

    subject_list = cursor.execute("SELECT id, name, code, instructor FROM subjects WHERE user_id = ? ORDER BY name", (AUTH_ID,)).fetchall()
    st.markdown('<div class="panel"><div class="panel-title">Your Subjects</div><div class="panel-sub">Only your own subjects are shown here.</div></div>', unsafe_allow_html=True)
    st.dataframe(subject_list, use_container_width=True, hide_index=True, column_config={"id":"ID","name":"Subject","code":"Code","instructor":"Instructor"})

elif st.session_state.page == 3:
    st.markdown('<div class="page-banner"><div class="page-title">📝 Assignments</div><div class="page-sub">Track deadlines, priorities and completion status in one place.</div></div>', unsafe_allow_html=True)
    assignment_subject_rows = cursor.execute("SELECT id, name FROM subjects WHERE user_id = ? ORDER BY name", (AUTH_ID,)).fetchall()
    assignment_subject_names = [row[1] for row in assignment_subject_rows]
    assignment_subject_ids = [row[0] for row in assignment_subject_rows]

    a, b = st.columns(2)
    assignment_title = a.text_input("Assignment Title")
    assignment_deadline = b.date_input("Deadline")
    assignment_description = st.text_area("Description")
    c1, c2 = st.columns(2)
    assignment_priority = c1.selectbox("Priority", ["Low", "Medium", "High"])
    assignment_status = c2.selectbox("Status", ["Pending", "In Progress", "Completed"])

    if assignment_subject_names:
        assignment_subject = st.selectbox("Subject", assignment_subject_names)
        assignment_subject_id = assignment_subject_ids[assignment_subject_names.index(assignment_subject)]
    else:
        assignment_subject_id = None
        st.warning("Add a subject first before creating an assignment.")

    add_assignment = st.button("➕ Add Assignment", use_container_width=True)
    if add_assignment:
        if not assignment_title.strip() or assignment_subject_id is None:
            st.error("Enter an assignment title and select a subject.")
        else:
            cursor.execute("INSERT INTO assignments (title, description, deadline, priority, status, subject_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (assignment_title.strip(), assignment_description.strip(), str(assignment_deadline), assignment_priority, assignment_status, assignment_subject_id, AUTH_ID))
            conn.commit()
            st.success("Assignment added successfully.")
            st.rerun()

    assignment_list = cursor.execute("SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id WHERE assignments.user_id = ? ORDER BY assignments.deadline", (AUTH_ID,)).fetchall()
    st.markdown('<div class="panel"><div class="panel-title">Assignment List</div><div class="panel-sub">Your saved assignments and their current status.</div></div>', unsafe_allow_html=True)
    st.dataframe(assignment_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Assignment","description":"Description","deadline":"Deadline","priority":"Priority","status":"Status","name":"Subject"})

elif st.session_state.page == 4:
    st.markdown('<div class="page-banner"><div class="page-title">📅 Exams</div><div class="page-sub">Keep your exam dates, syllabus and notes organized.</div></div>', unsafe_allow_html=True)
    exam_subject_rows = cursor.execute("SELECT id, name FROM subjects WHERE user_id = ? ORDER BY name", (AUTH_ID,)).fetchall()
    exam_subject_names = [row[1] for row in exam_subject_rows]
    exam_subject_ids = [row[0] for row in exam_subject_rows]

    a, b = st.columns(2)
    exam_title = a.text_input("Exam Title")
    exam_date = b.date_input("Exam Date")
    exam_syllabus = st.text_area("Syllabus")
    exam_notes = st.text_area("Notes")

    if exam_subject_names:
        exam_subject = st.selectbox("Subject", exam_subject_names)
        exam_subject_id = exam_subject_ids[exam_subject_names.index(exam_subject)]
    else:
        exam_subject_id = None
        st.warning("Add a subject first before creating an exam.")

    add_exam = st.button("➕ Add Exam", use_container_width=True)
    if add_exam:
        if not exam_title.strip() or exam_subject_id is None:
            st.error("Enter an exam title and select a subject.")
        else:
            cursor.execute("INSERT INTO exams (title, exam_date, syllabus, notes, subject_id, user_id) VALUES (?, ?, ?, ?, ?, ?)", (exam_title.strip(), str(exam_date), exam_syllabus.strip(), exam_notes.strip(), exam_subject_id, AUTH_ID))
            conn.commit()
            st.success("Exam added successfully.")
            st.rerun()

    exam_list = cursor.execute("SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id WHERE exams.user_id = ? ORDER BY exams.exam_date", (AUTH_ID,)).fetchall()
    st.markdown('<div class="panel"><div class="panel-title">Exam Schedule</div><div class="panel-sub">Your saved exams in date order.</div></div>', unsafe_allow_html=True)
    st.dataframe(exam_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Exam","exam_date":"Exam Date","syllabus":"Syllabus","notes":"Notes","name":"Subject"})

    upcoming = []
    today = date.today()
    for row in exam_list:
        try:
            days_left = (datetime.strptime(row[2], "%Y-%m-%d").date() - today).days
            if days_left >= 0:
                upcoming.append((row[1], days_left))
        except Exception:
            pass
    if upcoming:
        st.markdown('<div class="section-kicker" style="margin-top:20px;">Exam countdown</div>', unsafe_allow_html=True)
        cols = st.columns(min(3, len(upcoming)))
        for idx, item in enumerate(upcoming[:3]):
            cols[idx % len(cols)].metric(item[0], f"{item[1]} days")

elif st.session_state.page == 5:
    st.markdown('<div class="page-banner"><div class="page-title">✅ Study Planner</div><div class="page-sub">Turn your study goals into clear, manageable daily tasks.</div></div>', unsafe_allow_html=True)
    task_subject_rows = cursor.execute("SELECT id, name FROM subjects WHERE user_id = ? ORDER BY name", (AUTH_ID,)).fetchall()
    task_subject_names = [row[1] for row in task_subject_rows]
    task_subject_ids = [row[0] for row in task_subject_rows]

    a, b = st.columns(2)
    task_title = a.text_input("Study Task")
    task_date = b.date_input("Study Date")
    c1, c2 = st.columns(2)
    task_duration = c1.number_input("Duration (minutes)", min_value=15, max_value=600, value=60, step=15)
    task_priority = c2.selectbox("Priority", ["Low", "Medium", "High"])

    if task_subject_names:
        task_subject = st.selectbox("Subject", task_subject_names)
        task_subject_id = task_subject_ids[task_subject_names.index(task_subject)]
    else:
        task_subject_id = None
        st.warning("Add a subject first before creating a study task.")

    add_task = st.button("➕ Add Study Task", use_container_width=True)
    if add_task:
        if not task_title.strip() or task_subject_id is None:
            st.error("Enter a study task and select a subject.")
        else:
            cursor.execute("INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (task_title.strip(), str(task_date), int(task_duration), task_priority, 0, task_subject_id, AUTH_ID))
            conn.commit()
            st.success("Study task added successfully.")
            st.rerun()

    task_list = cursor.execute("SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id WHERE tasks.user_id = ? ORDER BY tasks.task_date", (AUTH_ID,)).fetchall()
    st.markdown('<div class="panel"><div class="panel-title">Study Tasks</div><div class="panel-sub">Your daily study activities.</div></div>', unsafe_allow_html=True)
    st.dataframe(task_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Task","task_date":"Date","duration":"Minutes","priority":"Priority","completed":"Completed","name":"Subject"})

    if task_list:
        st.markdown('<div class="section-kicker" style="margin-top:20px;">Update completion</div>', unsafe_allow_html=True)
        task_options = {f"#{row[0]} • {row[1]}": row[0] for row in task_list}
        selected_task_label = st.selectbox("Task", list(task_options.keys()))
        completion = st.checkbox("Mark as completed")
        update_task = st.button("✓ Update task", use_container_width=True)
        if update_task:
            selected_task_id = task_options[selected_task_label]
            cursor.execute("UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?", (1 if completion else 0, selected_task_id, AUTH_ID))
            conn.commit()
            st.success("Task updated.")
            st.rerun()

elif st.session_state.page == 6:
    st.markdown('<div class="page-banner"><div class="page-title">👤 Profile</div><div class="page-sub">Keep your student profile and study preferences up to date.</div></div>', unsafe_allow_html=True)
    profile = cursor.execute("SELECT name, email, university, degree, semester, career_goal, skills, study_preferences FROM users WHERE auth_id = ?", (AUTH_ID,)).fetchone()
    profile = profile or (DISPLAY_NAME, EMAIL, "", "", "", "", "", "")

    p1, p2 = st.columns(2)
    profile_name = p1.text_input("Name", value=profile[0] or DISPLAY_NAME)
    profile_email = p2.text_input("Email", value=profile[1] or EMAIL, disabled=True)
    p3, p4 = st.columns(2)
    profile_university = p3.text_input("University / College", value=profile[2] or "")
    profile_degree = p4.text_input("Degree / Program", value=profile[3] or "")
    p5, p6 = st.columns(2)
    profile_semester = p5.text_input("Current Semester", value=profile[4] or "")
    profile_career = p6.text_input("Career Goal", value=profile[5] or "")
    profile_skills = st.text_area("Skills", value=profile[6] or "")
    profile_preferences = st.text_area("Study Preferences", value=profile[7] or "")

    save_profile = st.button("💾 Save profile", use_container_width=True)
    if save_profile:
        cursor.execute("UPDATE users SET name = ?, university = ?, degree = ?, semester = ?, career_goal = ?, skills = ?, study_preferences = ? WHERE auth_id = ?", (profile_name.strip(), profile_university.strip(), profile_degree.strip(), profile_semester.strip(), profile_career.strip(), profile_skills.strip(), profile_preferences.strip(), AUTH_ID))
        conn.commit()
        st.success("Profile saved successfully.")

    st.markdown('<div class="panel"><div class="panel-title">🔐 Change password</div><div class="panel-sub">Update your StudySphere password securely.</div></div>', unsafe_allow_html=True)
    current_password = st.text_input("Current password", type="password")
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")
    change_password = st.button("🔑 Update password", use_container_width=True)
    if change_password:
        account = cursor.execute("SELECT password_hash, password_salt FROM users WHERE auth_id = ?", (AUTH_ID,)).fetchone()
        if not current_password or not new_password or not confirm_password:
            st.error("Please complete all password fields.")
        elif not account or not verify_secret(current_password, account[1], account[0]):
            st.error("Your current password is incorrect.")
        elif len(new_password) < 8:
            st.error("Use a password with at least 8 characters.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            password_salt, password_hash = hash_secret(new_password)
            recovery_code = generate_recovery_code()
            recovery_salt, recovery_hash = hash_secret(recovery_code)
            cursor.execute("UPDATE users SET password_hash = ?, password_salt = ?, recovery_hash = ?, recovery_salt = ? WHERE auth_id = ?", (password_hash, password_salt, recovery_hash, recovery_salt, AUTH_ID))
            conn.commit()
            st.success("Password updated successfully.")
            st.info("Your recovery code has been rotated. Save the new code safely.")
            st.code(recovery_code)

    st.markdown('<div class="ai-panel"><div class="ai-badge">Account security</div><div class="ai-title">🛡️ Your login is built directly into StudySphere</div><div class="ai-text">StudySphere keeps authentication and academic records in the local SQLite database. Passwords are never stored as plain text.</div></div>', unsafe_allow_html=True)

elif st.session_state.page == 7:
    active_chat_id = ensure_active_chat(AUTH_ID)
    chat_rows = load_chat_messages(active_chat_id, AUTH_ID)

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chat-header"><div class="chat-brand">🤖 StudySphere AI</div><div class="chat-model">✦ Gemini • Stateful AI</div></div>',
        unsafe_allow_html=True,
    )

    if not chat_rows:
        st.markdown(
            '<div class="chat-welcome"><div class="chat-welcome-icon">✦</div><div class="chat-welcome-title">How can I help you study?</div><div class="chat-welcome-sub">Have a natural conversation with your academic AI. Ask questions, follow up, plan your week, or use your StudySphere data when you need it.</div></div>',
            unsafe_allow_html=True,
        )
        p1, p2, p3, p4 = st.columns(4)
        p1.markdown('<div class="prompt-card"><div class="prompt-icon">🧠</div><div class="prompt-title">Explain a topic</div><div class="prompt-sub">Make a difficult concept simple</div></div>', unsafe_allow_html=True)
        p2.markdown('<div class="prompt-card"><div class="prompt-icon">📅</div><div class="prompt-title">Plan my week</div><div class="prompt-sub">Use my real deadlines and exams</div></div>', unsafe_allow_html=True)
        p3.markdown('<div class="prompt-card"><div class="prompt-icon">📝</div><div class="prompt-title">Review my work</div><div class="prompt-sub">Help me find what needs attention</div></div>', unsafe_allow_html=True)
        p4.markdown('<div class="prompt-card"><div class="prompt-icon">🎯</div><div class="prompt-title">Quiz me</div><div class="prompt-sub">Practice before an exam</div></div>', unsafe_allow_html=True)

    for role, content, _created_at in chat_rows:
        avatar = "🧑‍🎓" if role == "user" else "🤖"
        with st.chat_message("user" if role == "user" else "assistant", avatar=avatar):
            st.markdown(content)

    chat_prompt = st.chat_input("Message StudySphere AI…")
    if chat_prompt:
        prompt_text = chat_prompt.strip()
        if prompt_text:
            save_chat_message(active_chat_id, AUTH_ID, "user", prompt_text)
            if not chat_rows:
                update_chat_title(active_chat_id, AUTH_ID, prompt_text)

            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(prompt_text)

            refreshed_rows = load_chat_messages(active_chat_id, AUTH_ID)
            academic_context = academic_context_for_chat(AUTH_ID)
            with st.chat_message("assistant", avatar="🤖"):
                streamed_answer = st.write_stream(
                    stream_gemini_interaction(
                        GLOBAL_GEMINI_API_KEY,
                        active_chat_id,
                        AUTH_ID,
                        refreshed_rows,
                        academic_context,
                        prompt_text,
                    )
                )

            answer_text = streamed_answer if isinstance(streamed_answer, str) else str(streamed_answer)
            answer_text = answer_text.strip()
            if not answer_text:
                answer_text = "I could not generate a response. Please try again."
            save_chat_message(active_chat_id, AUTH_ID, "assistant", answer_text)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;padding:24px 0 4px;color:#64748B;font-size:11px;">StudySphere • Learn smarter. Plan better. Achieve more.</div>', unsafe_allow_html=True)

conn.close()
