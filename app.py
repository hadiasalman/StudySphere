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

if "signup_recovery_code" not in st.session_state:
    st.session_state.signup_recovery_code = ""

if "reset_recovery_code" not in st.session_state:
    st.session_state.reset_recovery_code = ""

# ============================================================
# SQLITE DATABASE
# ============================================================

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (auth_id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE, university TEXT, degree TEXT, semester TEXT, career_goal TEXT, skills TEXT, study_preferences TEXT, password_hash TEXT, password_salt TEXT, recovery_hash TEXT, recovery_salt TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER, user_id TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER DEFAULT 0, subject_id INTEGER, user_id TEXT)")

for table_name in ["subjects", "assignments", "exams", "tasks"]:
    existing_columns = [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if "user_id" not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN user_id TEXT")

user_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
if "password_hash" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
if "password_salt" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN password_salt TEXT")
if "recovery_hash" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN recovery_hash TEXT")
if "recovery_salt" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN recovery_salt TEXT")

conn.commit()

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
.stApp {{ background:{bg}; color:{text}; }}
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
    st.session_state.page = 1
    st.session_state.show_login = "Sign in"


def call_groq_agent(api_key, messages, model="openai/gpt-oss-20b"):
    api_key = str(api_key or "").strip()
    if not api_key:
        return "Please enter your Groq API key in the AI Agent page before using the agent."
    payload = {"model": model, "messages": messages, "temperature": 0.3, "max_tokens": 1800}
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read().decode("utf-8")
        data = json.loads(raw)
        choices = data.get("choices") or []
        if not choices:
            return "The AI service returned an empty response. Please try again."
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        content = str(content or "").strip()
        return content or "The AI service returned an empty response. Please try again."
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message", "AI request failed.")
        except Exception:
            message = "AI request failed."
        return f"AI service error: {message}"
    except urllib.error.URLError:
        return "Could not reach the AI service. Check your internet connection and try again."
    except Exception:
        return "Something went wrong while contacting the AI service. Please try again."


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

# Keep the name/email in session synchronized with the database.
st.session_state.display_name = DISPLAY_NAME
st.session_state.email = EMAIL

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
st.sidebar.markdown("### 🤖 AI Agent")
st.sidebar.caption("Context-aware academic help powered by an AI model.")

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
    st.markdown(
        f"""
<div class="hero">
<div class="hero-kicker">Student command center</div>
<div class="hero-title">Good morning, {DISPLAY_NAME.split()[0]} 👋</div>
<div class="hero-text">Everything you need to organize your academic life — subjects, deadlines, exams and daily study tasks — in one focused workspace.</div>
<div class="hero-pill">✦ Stay organized • Study consistently • Make progress</div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">📚</div></div><div class="stat-number">{subject_count}</div><div class="stat-label">Your Subjects</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">📝</div></div><div class="stat-number">{assignment_count}</div><div class="stat-label">Assignments</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">🎯</div></div><div class="stat-number">{exam_count}</div><div class="stat-label">Upcoming Exams</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">✓</div></div><div class="stat-number">{pending_task_count}</div><div class="stat-label">Pending Tasks</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:6px"></div><div class="section-kicker">Quick actions</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    q1.markdown('<div class="quick-card"><div class="quick-icon">🤖</div><div class="quick-title">Ask AI Tutor</div><div class="quick-sub">Coming with the AI module</div></div>', unsafe_allow_html=True)
    q2.markdown('<div class="quick-card"><div class="quick-icon">📚</div><div class="quick-title">Manage Subjects</div><div class="quick-sub">Keep courses organized</div></div>', unsafe_allow_html=True)
    q3.markdown('<div class="quick-card"><div class="quick-icon">🎯</div><div class="quick-title">Exam Focus</div><div class="quick-sub">Stay ahead of important dates</div></div>', unsafe_allow_html=True)
    q4.markdown('<div class="quick-card"><div class="quick-icon">⚡</div><div class="quick-title">Study Planner</div><div class="quick-sub">Turn goals into daily tasks</div></div>', unsafe_allow_html=True)

    cursor.execute("SELECT title, deadline, priority, status FROM assignments WHERE user_id = ? ORDER BY deadline LIMIT 5", (AUTH_ID,))
    upcoming_assignments = cursor.fetchall()
    cursor.execute("SELECT title, exam_date FROM exams WHERE user_id = ? AND exam_date >= ? ORDER BY exam_date LIMIT 5", (AUTH_ID, str(date.today())))
    upcoming_exams = cursor.fetchall()

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel"><div class="panel-title">📝 Upcoming Assignments</div><div class="panel-sub">Stay ahead of your deadlines.</div></div>', unsafe_allow_html=True)
        if upcoming_assignments:
            st.dataframe(upcoming_assignments, use_container_width=True, hide_index=True, column_config={"title":"Assignment","deadline":"Deadline","priority":"Priority","status":"Status"})
        else:
            st.info("🎉 No assignments yet. Add your first assignment to start tracking your work.")

    with right:
        st.markdown('<div class="panel"><div class="panel-title">📅 Upcoming Exams</div><div class="panel-sub">Keep your exam schedule under control.</div></div>', unsafe_allow_html=True)
        if upcoming_exams:
            st.dataframe(upcoming_exams, use_container_width=True, hide_index=True, column_config={"title":"Exam","exam_date":"Exam Date"})
        else:
            st.info("🎯 No upcoming exams have been added yet.")

    completed_tasks = cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND completed = 1", (AUTH_ID,)).fetchone()[0]
    total_tasks = completed_tasks + pending_task_count
    task_progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    st.markdown(
        f"""
<div class="panel">
<div class="panel-title">📈 Your Study Overview</div>
<div class="panel-sub">A quick snapshot of your current academic workspace.</div>
<div style="margin-top:18px;">
<div style="display:flex;justify-content:space-between;font-size:12px;color:{muted};"><span>Study tasks completed</span><strong style="color:{text};">{task_progress}%</strong></div>
<div class="progress-shell"><div class="progress-bar" style="width:{task_progress}%;"></div></div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="ai-panel">
<div class="ai-badge">AI • Next module</div>
<div class="ai-title">🤖 StudySphere AI Agent</div>
<div class="ai-text">Your future academic agent will connect your subjects, tasks and exams to help you understand what needs attention and organize your study time more intelligently.</div>
</div>
""",
        unsafe_allow_html=True,
    )

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
    st.markdown('<div class="page-banner"><div class="page-title">🤖 AI Agent</div><div class="page-sub">Ask questions, analyze your academic workload, and turn your stored study data into a focused action plan.</div></div>', unsafe_allow_html=True)

    agent_left, agent_right = st.columns([1.35, 1])
    with agent_left:
        st.markdown('<div class="panel"><div class="panel-title">Connect your AI</div><div class="panel-sub">Your API key is kept only in this browser session and is never written to the SQLite database.</div></div>', unsafe_allow_html=True)
        agent_key = st.text_input("Groq API key", value=st.session_state.ai_api_key, type="password", key="agent_api_key_input")
        st.session_state.ai_api_key = agent_key.strip()
        st.caption("StudySphere uses Groq's OpenAI-compatible chat endpoint with the current openai/gpt-oss-20b model.")

    with agent_right:
        context = build_agent_context(AUTH_ID)
        st.metric("Subjects in context", len(context["subjects"]))
        st.metric("Upcoming exams", len(context["upcoming_exams"]))
        st.metric("Active assignments", sum(1 for row in context["assignments"] if str(row[3]).lower() != "completed"))

    agent_mode = st.selectbox("Agent mode", ["Ask my AI Tutor", "Analyze my academics", "Build my focus plan"])
    agent_question = st.text_area("What should the agent work on?", placeholder="Example: I have a database exam soon. What should I study first?", height=120)

    run_agent = st.button("🚀 Run AI Agent", use_container_width=True)
    if run_agent:
        agent_context_text = format_agent_context(context)
        base_system = """You are StudySphere AI Agent, an academic assistant for a university student. Use the student's stored StudySphere data as the primary context. Do not invent deadlines, exams, subjects, or scores. Be practical and concise. Explain educational concepts clearly instead of blindly giving answers. When prioritizing, consider exam dates, assignment deadlines, unfinished study tasks, and stated priorities. If the data is insufficient, say exactly what is missing."""

        if agent_mode == "Ask my AI Tutor":
            user_prompt = "Answer the student's question using the StudySphere context below. Give a simple explanation first, then examples or steps where useful.\n\nStudent question:\n" + (agent_question.strip() or "Give me one useful academic recommendation based on my current data.") + "\n\nStudySphere context:\n" + agent_context_text
        elif agent_mode == "Analyze my academics":
            user_prompt = "Analyze the student's current academic workload from the context below. Identify the most time-sensitive items, possible overloads or gaps, and 3 concrete actions for the next 7 days. Do not invent facts.\n\nStudent request:\n" + (agent_question.strip() or "Analyze my current academic situation.") + "\n\nStudySphere context:\n" + agent_context_text
        else:
            user_prompt = "Build a focused study plan from the student's actual stored data. Start with today's highest-priority actions, then give a 7-day plan with realistic sessions. Prefer urgent exams and deadlines, then weak or unfinished areas that are visible in the data. Clearly separate what is known from what is a suggested assumption.\n\nStudent request:\n" + (agent_question.strip() or "Build my focus plan for the next 7 days.") + "\n\nStudySphere context:\n" + agent_context_text

        with st.spinner("🤖 StudySphere AI Agent is thinking..."):
            answer = call_groq_agent(st.session_state.ai_api_key, [{"role": "system", "content": base_system}, {"role": "user", "content": user_prompt}])
        st.session_state.ai_messages.append({"mode": agent_mode, "question": agent_question.strip(), "answer": answer})

    if st.session_state.ai_messages:
        latest = st.session_state.ai_messages[-1]
        st.markdown(f'<div class="ai-panel"><div class="ai-badge">{latest["mode"]}</div><div class="ai-title">StudySphere response</div></div>', unsafe_allow_html=True)
        st.markdown(latest["answer"])

    st.markdown('<div class="panel"><div class="panel-title">🧠 What the agent can see</div><div class="panel-sub">Only the academic data belonging to your signed-in StudySphere account is added to the AI prompt.</div></div>', unsafe_allow_html=True)
    st.write(f"Subjects: {len(context['subjects'])} • Assignments: {len(context['assignments'])} • Upcoming exams: {len(context['upcoming_exams'])} • Study tasks: {len(context['study_tasks'])}")

    if st.button("🧹 Clear AI session", use_container_width=True):
        st.session_state.ai_messages = []
        st.rerun()

st.markdown('<div style="text-align:center;padding:24px 0 4px;color:#64748B;font-size:11px;">StudySphere • Learn smarter. Plan better. Achieve more.</div>', unsafe_allow_html=True)

conn.close()
