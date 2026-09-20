import streamlit as st
import sqlite3
import os
from datetime import datetime, date

# ============================================================

# STUDYSPHERE — AI STUDENT COMPANION

# ============================================================

st.set_page_config(
page_title="StudySphere",
page_icon="🎓",
layout="wide",
initial_sidebar_state="expanded"
)

# ============================================================

# DATABASE

# ============================================================

DB_NAME = "studysphere.db"

def get_connection():
conn = sqlite3.connect(
DB_NAME,
check_same_thread=False
)
conn.row_factory = sqlite3.Row
return conn

def init_database():
conn = get_connection()
cursor = conn.cursor()

```
cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        university TEXT,
        degree TEXT,
        semester TEXT,
        target_gpa REAL,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT,
        instructor TEXT,
        description TEXT,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        deadline TEXT,
        priority TEXT,
        status TEXT,
        subject_id INTEGER,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        exam_date TEXT,
        syllabus TEXT,
        notes TEXT,
        subject_id INTEGER,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        task_date TEXT,
        duration INTEGER,
        priority TEXT,
        completed INTEGER DEFAULT 0,
        subject_id INTEGER,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at TEXT
    )
""")

conn.commit()
conn.close()
```

init_database()

# ============================================================

# DATABASE HELPERS

# ============================================================

def execute_query(query, params=(), fetch=False):
conn = get_connection()
cursor = conn.cursor()

```
cursor.execute(query, params)

if fetch:
    result = cursor.fetchall()
    conn.close()
    return result

conn.commit()
last_id = cursor.lastrowid
conn.close()

return last_id
```

# ============================================================

# PROFILE

# ============================================================

def get_profile():
rows = execute_query(
"SELECT * FROM profile LIMIT 1",
fetch=True
)

```
return rows[0] if rows else None
```

def save_profile(
name,
email,
university,
degree,
semester,
target_gpa
):
existing = get_profile()

```
if existing:
    execute_query(
        """
        UPDATE profile
        SET name=?,
            email=?,
            university=?,
            degree=?,
            semester=?,
            target_gpa=?
        WHERE id=?
        """,
        (
            name,
            email,
            university,
            degree,
            semester,
            target_gpa,
            existing["id"]
        )
    )
else:
    execute_query(
        """
        INSERT INTO profile
        (
            name,
            email,
            university,
            degree,
            semester,
            target_gpa,
            created_at
        )
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            name,
            email,
            university,
            degree,
            semester,
            target_gpa,
            datetime.now().isoformat()
        )
    )
```

# ============================================================

# SUBJECTS

# ============================================================

def get_subjects():
return execute_query(
"SELECT * FROM subjects ORDER BY name",
fetch=True
)

def add_subject(
name,
code,
instructor,
description
):
execute_query(
"""
INSERT INTO subjects
(
name,
code,
instructor,
description,
created_at
)
VALUES (?,?,?,?,?)
""",
(
name,
code,
instructor,
description,
datetime.now().isoformat()
)
)

def delete_subject(subject_id):
execute_query(
"DELETE FROM subjects WHERE id=?",
(subject_id,)
)

# ============================================================

# ASSIGNMENTS

# ============================================================

def get_assignments():
return execute_query(
"""
SELECT
assignments.*,
subjects.name AS subject_name
FROM assignments
LEFT JOIN subjects
ON assignments.subject_id = subjects.id
ORDER BY deadline ASC
""",
fetch=True
)

def add_assignment(
title,
description,
deadline,
priority,
subject_id
):
execute_query(
"""
INSERT INTO assignments
(
title,
description,
deadline,
priority,
status,
subject_id,
created_at
)
VALUES (?,?,?,?,?,?,?)
""",
(
title,
description,
deadline,
priority,
"Pending",
subject_id,
datetime.now().isoformat()
)
)

def update_assignment_status(
assignment_id,
status
):
execute_query(
"""
UPDATE assignments
SET status=?
WHERE id=?
""",
(
status,
assignment_id
)
)

def delete_assignment(assignment_id):
execute_query(
"DELETE FROM assignments WHERE id=?",
(assignment_id,)
)

# ============================================================

# EXAMS

# ============================================================

def get_exams():
return execute_query(
"""
SELECT
exams.*,
subjects.name AS subject_name
FROM exams
LEFT JOIN subjects
ON exams.subject_id = subjects.id
ORDER BY exam_date ASC
""",
fetch=True
)

def add_exam(
title,
exam_date,
syllabus,
notes,
subject_id
):
execute_query(
"""
INSERT INTO exams
(
title,
exam_date,
syllabus,
notes,
subject_id,
created_at
)
VALUES (?,?,?,?,?,?)
""",
(
title,
exam_date,
syllabus,
notes,
subject_id,
datetime.now().isoformat()
)
)

def delete_exam(exam_id):
execute_query(
"DELETE FROM exams WHERE id=?",
(exam_id,)
)

# ============================================================

# TASKS

# ============================================================

def get_tasks():
return execute_query(
"""
SELECT
tasks.*,
subjects.name AS subject_name
FROM tasks
LEFT JOIN subjects
ON tasks.subject_id = subjects.id
ORDER BY task_date ASC
""",
fetch=True
)

def add_task(
title,
task_date,
duration,
priority,
subject_id
):
execute_query(
"""
INSERT INTO tasks
(
title,
task_date,
duration,
priority,
completed,
subject_id,
created_at
)
VALUES (?,?,?,?,?,?,?)
""",
(
title,
task_date,
duration,
priority,
0,
subject_id,
datetime.now().isoformat()
)
)

def update_task(
task_id,
completed
):
execute_query(
"""
UPDATE tasks
SET completed=?
WHERE id=?
""",
(
int(completed),
task_id
)
)

def delete_task(task_id):
execute_query(
"DELETE FROM tasks WHERE id=?",
(task_id,)
)

# ============================================================

# GEMINI AI

# ============================================================

def get_gemini_client():
try:
from google import genai

```
    api_key = None

    try:
        api_key = st.secrets.get(
            "GEMINI_API_KEY"
        )
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

    if not api_key:
        return None

    return genai.Client(
        api_key=api_key
    )

except Exception:
    return None
```

def ask_gemini(prompt):
client = get_gemini_client()

```
if not client:
    return (
        "Gemini is not configured yet.\n\n"
        "Add your GEMINI_API_KEY to "
        "Streamlit Secrets to activate "
        "the AI features."
    )

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

except Exception as e:
    return f"AI error: {str(e)}"
```

# ============================================================

# LIGHT / DARK MODE CSS

# ============================================================

def apply_css(dark_mode=False):

```
if dark_mode:
    background = "#0f172a"
    card = "#1e293b"
    text = "#ffffff"
    muted = "#cbd5e1"
    input_background = "#1e293b"
    border = "rgba(255,255,255,0.18)"

else:
    background = "#f8fafc"
    card = "#ffffff"
    text = "#000000"
    muted = "#000000"
    input_background = "#ffffff"
    border = "rgba(0,0,0,0.18)"

st.markdown(
    f"""
    <style>

    /* ==================================================
       GLOBAL
       ================================================== */

    .stApp {{
        background-color: {background} !important;
        color: {text} !important;
    }}

    .stApp * {{
        color: {text} !important;
    }}

    body {{
        background-color: {background} !important;
    }}

    p,
    span,
    label,
    li,
    td,
    th,
    div {{
        color: {text} !important;
    }}


    /* ==================================================
       HEADINGS
       ================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {{
        color: {text} !important;
    }}


    /* ==================================================
       SIDEBAR
       ================================================== */

    section[data-testid="stSidebar"] {{
        background-color: {background} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] button {{
        color: {text} !important;
        background-color: transparent !important;
    }}

    section[data-testid="stSidebar"] button * {{
        color: {text} !important;
    }}


    /* ==================================================
       TEXT INPUTS
       ================================================== */

    input,
    textarea {{
        color: {text} !important;
        background-color: {input_background} !important;
        border-color: {border} !important;
        caret-color: {text} !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: {muted} !important;
        opacity: 0.7 !important;
    }}


    /* ==================================================
       SELECT BOX
       ================================================== */

    div[data-baseweb="select"] {{
        background-color: {input_background} !important;
    }}

    div[data-baseweb="select"] * {{
        color: {text} !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_background} !important;
        border-color: {border} !important;
    }}

    div[data-baseweb="popover"] {{
        background-color: {input_background} !important;
    }}

    div[data-baseweb="popover"] * {{
        color: {text} !important;
    }}

    ul[role="listbox"] {{
        background-color: {input_background} !important;
    }}

    ul[role="listbox"] li {{
        background-color: {input_background} !important;
        color: {text} !important;
    }}


    /* ==================================================
       DATE INPUT
       ================================================== */

    input[type="date"] {{
        color: {text} !important;
        background-color: {input_background} !important;
    }}


    /* ==================================================
       NUMBER INPUT
       ================================================== */

    [data-testid="stNumberInput"] input {{
        color: {text} !important;
        background-color: {input_background} !important;
    }}

    [data-testid="stNumberInput"] button {{
        color: {text} !important;
    }}


    /* ==================================================
       BUTTONS
       ================================================== */

    .stButton > button,
    .stFormSubmitButton > button {{
        color: {text} !important;
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    .stButton > button *,
    .stFormSubmitButton > button * {{
        color: {text} !important;
    }}


    /* ==================================================
       CHECKBOX
       ================================================== */

    [data-testid="stCheckbox"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       TOGGLE
       ================================================== */

    [data-testid="stToggle"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       RADIO
       ================================================== */

    [data-testid="stRadio"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       CAPTIONS
       ================================================== */

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {{
        color: {muted} !important;
    }}


    /* ==================================================
       METRICS
       ================================================== */

    [data-testid="stMetric"] {{
        background-color: {card} !important;
    }}

    [data-testid="stMetric"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       EXPANDERS
       ================================================== */

    [data-testid="stExpander"] {{
        background-color: {card} !important;
        border-color: {border} !important;
    }}

    [data-testid="stExpander"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       CONTAINERS / CARDS
       ================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card} !important;
        border-color: {border} !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       ALERTS
       ================================================== */

    [data-testid="stAlert"] {{
        color: {text} !important;
    }}

    [data-testid="stAlert"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       CHAT
       ================================================== */

    [data-testid="stChatMessage"] {{
        color: {text} !important;
    }}

    [data-testid="stChatMessage"] * {{
        color: {text} !important;
    }}

    [data-testid="stChatInput"] {{
        background-color: {input_background} !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {text} !important;
        background-color: {input_background} !important;
    }}


    /* ==================================================
       MARKDOWN
       ================================================== */

    [data-testid="stMarkdownContainer"] {{
        color: {text} !important;
    }}

    [data-testid="stMarkdownContainer"] * {{
        color: {text} !important;
    }}


    /* ==================================================
       LINKS
       ================================================== */

    a {{
        color: {text} !important;
    }}


    /* ==================================================
       WELCOME CARD
       ================================================== */

    .welcome {{
        background: linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );
        padding: 28px;
        border-radius: 20px;
        margin-bottom: 25px;
    }}

    .welcome h1,
    .welcome p {{
        color: #ffffff !important;
    }}

    .welcome h1 {{
        margin: 0;
        font-size: 2rem;
    }}

    .welcome p {{
        margin-top: 8px;
    }}


    /* ==================================================
       STAT CARDS
       ================================================== */

    .stat-card {{
        background-color: {card};
        border-radius: 16px;
        padding: 22px;
        border: 1px solid {border};
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }}

    .stat-number {{
        font-size: 2rem;
        font-weight: 800;
        color: {text} !important;
    }}

    .stat-label {{
        color: {text} !important;
        font-size: 0.9rem;
    }}


    /* ==================================================
       SECTION TITLES
       ================================================== */

    .section-title {{
        font-size: 1.4rem;
        font-weight: 700;
        color: {text} !important;
        margin-top: 25px;
        margin-bottom: 15px;
    }}


    /* ==================================================
       DIVIDERS
       ================================================== */

    hr {{
        border-color: {border} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
```

# ============================================================

# SESSION STATE

# ============================================================

if "page" not in st.session_state:
st.session_state.page = "Dashboard"

if "dark_mode" not in st.session_state:
st.session_state.dark_mode = False

# ============================================================

# SIDEBAR

# ============================================================

profile = get_profile()

with st.sidebar:

```
st.markdown("## 🎓 StudySphere")

st.caption(
    "Learn smarter. Plan better. Achieve more."
)

st.divider()

pages = [
    "Dashboard",
    "Subjects",
    "Assignments",
    "Exams",
    "Study Planner",
    "AI Tutor",
    "AI Study Plan",
    "Profile"
]

for page in pages:

    if st.button(
        page,
        use_container_width=True,
        key=f"nav_{page}"
    ):
        st.session_state.page = page
        st.rerun()

st.divider()

st.session_state.dark_mode = st.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

st.divider()

if profile:

    st.markdown("### 👤 Student")

    st.write(
        profile["name"] or "Student"
    )

    if profile["degree"]:
        st.caption(
            profile["degree"]
        )
```

# Apply theme

apply_css(
st.session_state.dark_mode
)

# ============================================================

# DASHBOARD

# ============================================================

def dashboard():

```
profile = get_profile()
subjects = get_subjects()
assignments = get_assignments()
exams = get_exams()
tasks = get_tasks()

name = (
    profile["name"]
    if profile
    else "Student"
)

st.markdown(
    f"""
    <div class="welcome">
        <h1>Welcome back, {name} 👋</h1>
        <p>
            Stay organized, study smarter,
            and keep moving toward your goals.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

pending_assignments = len([
    a for a in assignments
    if a["status"] != "Completed"
])

completed_tasks = len([
    t for t in tasks
    if t["completed"]
])

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                {len(subjects)}
            </div>
            <div class="stat-label">
                Subjects
            </div>
        </div>
        """,
        unsa
```
