import streamlit as st
import sqlite3
import os
from datetime import datetime, date

# ============================================================

# PAGE CONFIG

# ============================================================

st.set_page_config(
page_title="StudySphere — AI Student Companion",
page_icon="🎓",
layout="wide",
initial_sidebar_state="expanded"
)

# ============================================================

# CONSTANTS

# ============================================================

DB_NAME = "studysphere.db"

# ============================================================

# DATABASE

# ============================================================
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
conn.close()
return None
```

def get_profile():
result = execute_query(
"SELECT * FROM profile LIMIT 1",
fetch=True
)

```
if result:
    return result[0]

return None
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
        SET name = ?,
            email = ?,
            university = ?,
            degree = ?,
            semester = ?,
            target_gpa = ?
        WHERE id = ?
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
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

def get_subjects():
return execute_query(
"SELECT * FROM subjects ORDER BY name",
fetch=True
)

def add_subject(name, code, instructor, description):
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
VALUES (?, ?, ?, ?, ?)
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
"DELETE FROM subjects WHERE id = ?",
(subject_id,)
)

def get_assignments():
return execute_query(
"""
SELECT
assignments.*,
subjects.name AS subject_name
FROM assignments
LEFT JOIN subjects
ON assignments.subject_id = subjects.id
ORDER BY deadline
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
VALUES (?, ?, ?, ?, ?, ?, ?)
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

def update_assignment_status(assignment_id, status):
execute_query(
"""
UPDATE assignments
SET status = ?
WHERE id = ?
""",
(
status,
assignment_id
)
)

def delete_assignment(assignment_id):
execute_query(
"DELETE FROM assignments WHERE id = ?",
(assignment_id,)
)

def get_exams():
return execute_query(
"""
SELECT
exams.*,
subjects.name AS subject_name
FROM exams
LEFT JOIN subjects
ON exams.subject_id = subjects.id
ORDER BY exam_date
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
VALUES (?, ?, ?, ?, ?, ?)
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
"DELETE FROM exams WHERE id = ?",
(exam_id,)
)

def get_tasks():
return execute_query(
"""
SELECT
tasks.*,
subjects.name AS subject_name
FROM tasks
LEFT JOIN subjects
ON tasks.subject_id = subjects.id
ORDER BY task_date
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
VALUES (?, ?, ?, ?, ?, ?, ?)
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

def update_task_completion(task_id, completed):
execute_query(
"""
UPDATE tasks
SET completed = ?
WHERE id = ?
""",
(
int(completed),
task_id
)
)

def delete_task(task_id):
execute_query(
"DELETE FROM tasks WHERE id = ?",
(task_id,)
)

def save_study_plan(title, content):
execute_query(
"""
INSERT INTO study_plans
(
title,
content,
created_at
)
VALUES (?, ?, ?)
""",
(
title,
content,
datetime.now().isoformat()
)
)

# ============================================================

# GEMINI

# ============================================================

try:
from google import genai

```
GEMINI_API_KEY = None

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )
else:
    gemini_client = None
```

except Exception:
gemini_client = None

def ask_gemini(prompt):
if gemini_client is None:
return (
"Gemini is not configured yet.\n\n"
"Please add GEMINI_API_KEY to your "
"Streamlit secrets."
)

```
try:
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

except Exception as e:
    return f"Gemini error: {e}"
```

# ============================================================

# SESSION STATE

# ============================================================

if "page" not in st.session_state:
st.session_state.page = "Dashboard"

if "dark_mode" not in st.session_state:
st.session_state.dark_mode = False

if "chat_history" not in st.session_state:
st.session_state.chat_history = []

# ============================================================

# CSS

# ============================================================

def apply_css(dark_mode):
if dark_mode:
background = "#0f172a"
card = "#1e293b"
input_bg = "#1e293b"
text = "#ffffff"
border = "#475569"
accent = "#8b5cf6"
else:
background = "#f8fafc"
card = "#ffffff"
input_bg = "#ffffff"
text = "#000000"
border = "#cbd5e1"
accent = "#7c3aed"

```
st.markdown(
    f"""
    <style>

    /* ================================
       GLOBAL
    ================================= */

    .stApp {{
        background-color: {background};
    }}

    .stApp * {{
        color: {text} !important;
    }}

    body,
    p,
    span,
    div,
    label,
    small,
    strong,
    b,
    li,
    td,
    th {{
        color: {text} !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text} !important;
    }}

    /* ================================
       SIDEBAR
    ================================= */

    section[data-testid="stSidebar"] {{
        background-color: {card} !important;
        border-right: 1px solid {border};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* ================================
       INPUTS
    ================================= */

    input,
    textarea,
    select {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: {text} !important;
        opacity: 0.65 !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    div[data-baseweb="select"] * {{
        color: {text} !important;
    }}

    ul[role="listbox"],
    li[role="option"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}

    /* ================================
       BUTTONS
    ================================= */

    .stButton > button,
    .stFormSubmitButton > button {{
        background-color: {card} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        border-color: {accent} !important;
        color: {text} !important;
    }}

    /* ================================
       CARDS
    ================================= */

    div[data-testid="stContainer"] {{
        color: {text} !important;
    }}

    .study-card {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }}

    .study-card h3,
    .study-card p,
    .study-card span {{
        color: {text} !important;
    }}

    /* ================================
       METRICS
    ================================= */

    div[data-testid="stMetric"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }}

    div[data-testid="stMetric"] * {{
        color: {text} !important;
    }}

    /* ================================
       EXPANDERS
    ================================= */

    div[data-testid="stExpander"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    div[data-testid="stExpander"] * {{
        color: {text} !important;
    }}

    /* ================================
       ALERTS
    ================================= */

    div[data-testid="stAlert"] * {{
        color: {text} !important;
    }}

    /* ================================
       CHECKBOX / RADIO / TOGGLE
    ================================= */

    div[data-testid="stCheckbox"] *,
    div[data-testid="stRadio"] *,
    div[data-testid="stToggle"] * {{
        color: {text} !important;
    }}

    /* ================================
       CHAT
    ================================= */

    div[data-testid="stChatMessage"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    div[data-testid="stChatMessage"] * {{
        color: {text} !important;
    }}

    /* ================================
       DATAFRAME
    ================================= */

    div[data-testid="stDataFrame"] * {{
        color: {text} !important;
    }}

    /* ================================
       WELCOME CARD
    ================================= */

    .welcome-card {{
        background: linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
    }}

    .welcome-card h1,
    .welcome-card h2,
    .welcome-card p {{
        color: white !important;
    }}

    /* ================================
       NAVIGATION
    ================================= */

    .nav-title {{
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 5px;
    }}

    .muted {{
        opacity: 0.8;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
```

# ============================================================

# SIDEBAR

# ============================================================

with st.sidebar:

```
st.markdown(
    """
    <div style="
        font-size:28px;
        font-weight:800;
        margin-bottom:5px;
    ">
        🎓 StudySphere
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Learn smarter. Plan better. Achieve more.")

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

selected_page = st.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = selected_page

st.divider()

st.session_state.dark_mode = st.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

profile = get_profile()

if profile:
    st.divider()
    st.markdown("### 👤 Profile")
    st.write(profile["name"] or "Student")
    st.caption(profile["degree"] or "BS Artificial Intelligence")
```

# ============================================================

# APPLY THEME

# ============================================================

apply_css(st.session_state.dark_mode)

# ============================================================

# DASHBOARD

# ============================================================

if st.session_state.page == "Dashboard":

```
profile = get_profile()

student_name = (
    profile["name"]
    if profile and profile["name"]
    else "Student"
)

st.markdown(
    f"""
    <div class="welcome-card">
        <h1>Welcome back, {student_name}! 👋</h1>
        <p>
            Stay organized, study smarter, and keep moving
            toward your academic goals.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

subjects = get_subjects()
assignments = get_assignments()
exams = get_exams()
tasks = get_tasks()

pending_assignments = [
    a for a in assignments
    if a["status"] != "Completed"
]

upcoming_exams = [
    e for e in exams
    if e["exam_date"]
]

completed_tasks = [
    t for t in tasks
    if t["completed"] == 1
]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📚 Subjects",
        len(subjects)
    )

with col2:
    st.metric(
        "📝 Pending Assignments",
        len(pending_assignments)
    )

with col3:
    st.metric(
        "📖 Upcoming Exams",
        len(upcoming_exams)
    )

with col4:
    st.metric(
        "✅ Completed Tasks",
        len(completed_tasks)
    )

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("📌 Today's Tasks")

    today_string = date.today().isoformat()

    today_tasks = [
        task for task in tasks
        if task["task_date"] == today_string
    ]

    if not today_tasks:
        st.info("No tasks planned for today.")

    for task in today_tasks:

        status = "Completed" if task["completed"] else "Pending"

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{task["title"]}</h3>
                <p>
                    Subject:
                    {task["subject_name"] or "General"}
                </p>
                <p>
                    Duration:
                    {task["duration"]} minutes
                </p>
                <p>
                    Priority:
                    {task["priority"]}
                </p>
                <p>
                    Status:
                    {status}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

with right:

    st.subheader("⏰ Upcoming Assignments")

    if not pending_assignments:
        st.info("No pending assignments.")

    for assignment in pending_assignments[:5]:

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{assignment["title"]}</h3>
                <p>
                    Subject:
                    {assignment["subject_name"] or "General"}
                </p>
                <p>
                    Deadline:
                    {assignment["deadline"]}
                </p>
                <p>
                    Priority:
                    {assignment["priority"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
```

# ============================================================

# SUBJECTS

# ============================================================

elif st.session_state.page == "Subjects":

```
st.title("📚 Subjects")
st.write("Manage your university subjects.")

with st.form("add_subject_form"):

    st.subheader("Add New Subject")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Subject Name"
        )

    with col2:
        code = st.text_input(
            "Subject Code"
        )

    instructor = st.text_input(
        "Instructor"
    )

    description = st.text_area(
        "Description"
    )

    submitted = st.form_submit_button(
        "➕ Add Subject"
    )

    if submitted:

        if name.strip():

            add_subject(
                name.strip(),
                code.strip(),
                instructor.strip(),
                description.strip()
            )

            st.success(
                "Subject added successfully!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter a subject name."
            )

st.divider()

subjects = get_subjects()

st.subheader("Your Subjects")

if not subjects:
    st.info("No subjects added yet.")

for subject in subjects:

    with st.container(border=True):

        col1, col2 = st.columns([5, 1])

        with col1:

            st.markdown(
                f"### 📘 {subject['name']}"
            )

            if subject["code"]:
                st.write(
                    f"**Code:** {subject['code']}"
                )

            if subject["instructor"]:
                st.write(
                    f"**Instructor:** "
                    f"{subject['instructor']}"
                )

            if subject["description"]:
                st.write(
                    subject["description"]
                )

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_subject_{subject['id']}"
            ):

                delete_subject(
                    subject["id"]
                )

                st.rerun()
```

# ============================================================

# ASSIGNMENTS

# ============================================================

elif st.session_state.page == "Assignments":

```
st.title("📝 Assignments")
st.write(
    "Track assignments and deadlines."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_assignment_form"):

    st.subheader("Add Assignment")

    title = st.text_input(
        "Assignment Title"
    )

    description = st.text_area(
        "Description"
    )

    col1, col2 = st.columns(2)

    with col1:

        deadline = st.date_input(
            "Deadline",
            value=date.today()
        )

    with col2:

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High"
            ]
        )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Assignment"
    )

    if submitted:

        if title.strip():

            add_assignment(
                title.strip(),
                description.strip(),
                deadline.isoformat(),
                priority,
                subject_options[subject_name]
            )

            st.success(
                "Assignment added!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter an assignment title."
            )

st.divider()

assignments = get_assignments()

if not assignments:
    st.info(
        "No assignments available."
    )

for assignment in assignments:

    with st.container(border=True):

        st.subheader(
            f"📝 {assignment['title']}"
        )

        st.write(
            f"**Subject:** "
            f"{assignment['subject_name'] or 'General'}"
        )

        st.write(
            f"**Deadline:** "
            f"{assignment['deadline']}"
        )

        st.write(
            f"**Priority:** "
            f"{assignment['priority']}"
        )

        if assignment["description"]:
            st.write(
                assignment["description"]
            )

        current_status = assignment["status"]

        col1, col2 = st.columns([3, 1])

        with col1:

            new_status = st.selectbox(
                "Status",
                [
                    "Pending",
                    "In Progress",
                    "Completed"
                ],
                index=[
                    "Pending",
                    "In Progress",
                    "Completed"
                ].index(current_status),
                key=f"status_{assignment['id']}"
            )

            if new_status != current_status:

                update_assignment_status(
                    assignment["id"],
                    new_status
                )

                st.rerun()

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_assignment_{assignment['id']}"
            ):

                delete_assignment(
                    assignment["id"]
                )

                st.rerun()
```

# ============================================================

# EXAMS

# ============================================================

elif st.session_state.page == "Exams":

```
st.title("📖 Exams")
st.write(
    "Keep track of your upcoming exams."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_exam_form"):

    st.subheader("Add Exam")

    title = st.text_input(
        "Exam Title"
    )

    exam_date = st.date_input(
        "Exam Date",
        value=date.today()
    )

    syllabus = st.text_area(
        "Syllabus"
    )

    notes = st.text_area(
        "Notes"
    )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Exam"
    )

    if submitted:

        if title.strip():

            add_exam(
                title.strip(),
                exam_date.isoformat(),
                syllabus.strip(),
                notes.strip(),
                subject_options[subject_name]
            )

            st.success(
                "Exam added successfully!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter an exam title."
            )

st.divider()

exams = get_exams()

if not exams:
    st.info(
        "No exams added yet."
    )

for exam in exams:

    with st.container(border=True):

        st.subheader(
            f"📚 {exam['title']}"
        )

        st.write(
            f"**Subject:** "
            f"{exam['subject_name'] or 'General'}"
        )

        st.write(
            f"**Exam Date:** "
            f"{exam['exam_date']}"
        )

        if exam["syllabus"]:
            st.write(
                f"**Syllabus:** {exam['syllabus']}"
            )

        if exam["notes"]:
            st.write(
                f"**Notes:** {exam['notes']}"
            )

        if st.button(
            "🗑️ Delete",
            key=f"delete_exam_{exam['id']}"
        ):

            delete_exam(
                exam["id"]
            )

            st.rerun()
```

# ============================================================

# STUDY PLANNER

# ============================================================

elif st.session_state.page == "Study Planner":

```
st.title("📅 Study Planner")
st.write(
    "Plan your daily study sessions."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_task_form"):

    st.subheader("Add Study Task")

    title = st.text_input(
        "Task Title"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        task_date = st.date_input(
            "Date",
            value=date.today()
        )

    with col2:

        duration = st.number_input(
            "Duration (minutes)",
            min_value=5,
            max_value=600,
            value=60,
            step=5
        )

    with col3:

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High"
            ]
        )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Task"
    )

    if submitted:

        if title.strip():

            add_task(
                title.strip(),
                task_date.isoformat(),
                duration,
                priority,
                subject_options[subject_name]
            )

            st.success(
                "Study task added!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter a task title."
            )

st.divider()

tasks = get_tasks()

if not tasks:
    st.info(
        "No study tasks yet."
    )

for task in tasks:

    with st.container(border=True):

        col1, col2, col3 = st.columns(
            [1, 5, 1]
        )

        with col1:

            completed = st.checkbox(
                "Done",
                value=bool(task["completed"]),
                key=f"task_{task['id']}"
            )

            if completed != bool(task["completed"]):

                update_task_completion(
                    task["id"],
                    completed
                )

                st.rerun()

        with col2:

            if task["completed"]:
                st.markdown(
                    f"### ~~{task['title']}~~"
                )
            else:
                st.markdown(
                    f"### {task['title']}"
                )

            st.write(
                f"📅 {task['task_date']}  |  "
                f"⏱️ {task['duration']} minutes  |  "
                f"🎯 {task['priority']}"
            )

            st.write(
                f"📚 Subject: "
                f"{task['subject_name'] or 'General'}"
            )

        with col3:

            if st.button(
                "🗑️",
                key=f"delete_task_{task['id']}"
            ):

                delete_task(
                    task["id"]
                )

                st.rerun()
```

# ============================================================

# AI TUTOR

# ============================================================

elif st.session_state.page == "AI Tutor":

```
st.title("🤖 AI Tutor")

st.write(
    "Ask questions about programming, AI, "
    "databases, mathematics, or any subject."
)

for message in st.session_state.chat_history:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

user_prompt = st.chat_input(
    "Ask your AI Tutor something..."
)

if user_prompt:

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    tutor_prompt = f"""
```

You are StudySphere AI Tutor.

The student is a university student studying
Artificial Intelligence.

Explain concepts in a beginner-friendly way.

Use simple language and examples.

If the student asks about programming,
explain the logic step by step.

Student question:

{user_prompt}
"""

```
    answer = ask_gemini(
        tutor_prompt
    )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
```

# ============================================================

# AI STUDY PLAN

# ============================================================

elif st.session_state.page == "AI Study Plan":

```
st.title("🧠 AI Study Plan Generator")

st.write(
    "Let AI create a personalized study plan "
    "based on your workload."
)

col1, col2 = st.columns(2)

with col1:

    study_goal = st.text_input(
        "What do you want to study?",
        placeholder="Example: Python for AI"
    )

    available_hours = st.number_input(
        "Hours available per week",
        min_value=1,
        max_value=60,
        value=10
    )

with col2:

    duration = st.selectbox(
        "Plan Duration",
        [
            "1 week",
            "2 weeks",
            "1 month",
            "3 months",
            "6 months"
        ]
    )

    level = st.selectbox(
        "Your Skill Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

if st.button(
    "✨ Generate Study Plan"
):

    if not study_goal.strip():

        st.warning(
            "Please enter what you want to study."
        )

    else:

        with st.spinner(
            "Creating your personalized study plan..."
        ):

            plan_prompt = f"""
```

Create a practical study plan for a university student.

Topic:
{study_goal}

Skill level:
{level}

Available study time:
{available_hours} hours per week

Duration:
{duration}

Create:

1. Weekly goals
2. Topics to study
3. Daily study activities
4. Practice tasks
5. Projects
6. Revision strategy
7. Recommended milestones

Keep the plan realistic and beginner-friendly.

Use clear headings and bullet points.
"""

```
            plan = ask_gemini(
                plan_prompt
            )

        st.success(
            "Your study plan is ready!"
        )

        st.markdown(plan)

        if st.button(
            "💾 Save Study Plan"
        ):

            save_study_plan(
                study_goal,
                plan
            )

            st.success(
                "Study plan saved successfully!"
            )
```

# ============================================================

# PROFILE

# ============================================================

elif st.session_state.page == "Profile":

```
st.title("👤 Profile")

st.write(
    "Manage your student information."
)

profile = get_profile()

default_name = ""
default_email = ""
default_university = ""
default_degree = "BS Artificial Intelligence"
default_semester = "2nd Semester"
default_gpa = 3.8

if profile:

    default_name = profile["name"] or ""
    default_email = profile["email"] or ""
    default_university = profile["university"] or ""

    if profile["degree"]:
        default_degree = profile["degree"]

    if profile["semester"]:
        default_semester = profile["semester"]

    if profile["target_gpa"] is not None:
        default_gpa = profile["target_gpa"]

with st.form("profile_form"):

    name = st.text_input(
        "Full Name",
        value=default_name
    )

    email = st.text_input(
        "Email",
        value=default_email
    )

    university = st.text_input(
        "University",
        value=default_university
    )

    degree = st.text_input(
        "Degree",
        value=default_degree
    )

    semester = st.text_input(
        "Semester",
        value=default_semester
    )

    target_gpa = st.number_input(
        "Target GPA",
        min_value=0.0,
        max_value=4.0,
        value=float(default_gpa),
        step=0.1
    )

    submitted = st.form_submit_button(
        "💾 Save Profile"
    )

    if submitted:

        save_profile(
            name.strip(),
            email.strip(),
            university.strip(),
            degree.strip(),
            semester.strip(),
            target_gpa
        )

        st.success(
            "Profile saved successfully!"
        )

        st.rerun()
```

# ============================================================

# FOOTER

# ============================================================

st.divider()

st.markdown(
""" <div style="
     text-align:center;
     padding:15px;
     opacity:0.8;
 ">
🎓 StudySphere — AI Student Companion <br>
Learn smarter. Plan better. Achieve more. </div>
""",
unsafe_allow_html=True
)
import streamlit as st
import sqlite3
import os
from datetime import datetime, date

# ============================================================

# PAGE CONFIG

# ============================================================

st.set_page_config(
page_title="StudySphere — AI Student Companion",
page_icon="🎓",
layout="wide",
initial_sidebar_state="expanded"
)

# ============================================================

# CONSTANTS

# ============================================================

DB_NAME = "studysphere.db"

# ============================================================

# DATABASE

# ============================================================

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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
        created_at TEXT,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
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
conn.close()
return None
```

def get_profile():
result = execute_query(
"SELECT * FROM profile LIMIT 1",
fetch=True
)

```
if result:
    return result[0]

return None
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
        SET name = ?,
            email = ?,
            university = ?,
            degree = ?,
            semester = ?,
            target_gpa = ?
        WHERE id = ?
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
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

def get_subjects():
return execute_query(
"SELECT * FROM subjects ORDER BY name",
fetch=True
)

def add_subject(name, code, instructor, description):
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
VALUES (?, ?, ?, ?, ?)
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
"DELETE FROM subjects WHERE id = ?",
(subject_id,)
)

def get_assignments():
return execute_query(
"""
SELECT
assignments.*,
subjects.name AS subject_name
FROM assignments
LEFT JOIN subjects
ON assignments.subject_id = subjects.id
ORDER BY deadline
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
VALUES (?, ?, ?, ?, ?, ?, ?)
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

def update_assignment_status(assignment_id, status):
execute_query(
"""
UPDATE assignments
SET status = ?
WHERE id = ?
""",
(
status,
assignment_id
)
)

def delete_assignment(assignment_id):
execute_query(
"DELETE FROM assignments WHERE id = ?",
(assignment_id,)
)

def get_exams():
return execute_query(
"""
SELECT
exams.*,
subjects.name AS subject_name
FROM exams
LEFT JOIN subjects
ON exams.subject_id = subjects.id
ORDER BY exam_date
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
VALUES (?, ?, ?, ?, ?, ?)
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
"DELETE FROM exams WHERE id = ?",
(exam_id,)
)

def get_tasks():
return execute_query(
"""
SELECT
tasks.*,
subjects.name AS subject_name
FROM tasks
LEFT JOIN subjects
ON tasks.subject_id = subjects.id
ORDER BY task_date
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
VALUES (?, ?, ?, ?, ?, ?, ?)
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

def update_task_completion(task_id, completed):
execute_query(
"""
UPDATE tasks
SET completed = ?
WHERE id = ?
""",
(
int(completed),
task_id
)
)

def delete_task(task_id):
execute_query(
"DELETE FROM tasks WHERE id = ?",
(task_id,)
)

def save_study_plan(title, content):
execute_query(
"""
INSERT INTO study_plans
(
title,
content,
created_at
)
VALUES (?, ?, ?)
""",
(
title,
content,
datetime.now().isoformat()
)
)

# ============================================================

# GEMINI

# ============================================================

try:
from google import genai

```
GEMINI_API_KEY = None

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )
else:
    gemini_client = None
```

except Exception:
gemini_client = None

def ask_gemini(prompt):
if gemini_client is None:
return (
"Gemini is not configured yet.\n\n"
"Please add GEMINI_API_KEY to your "
"Streamlit secrets."
)

```
try:
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

except Exception as e:
    return f"Gemini error: {e}"
```

# ============================================================

# SESSION STATE

# ============================================================

if "page" not in st.session_state:
st.session_state.page = "Dashboard"

if "dark_mode" not in st.session_state:
st.session_state.dark_mode = False

if "chat_history" not in st.session_state:
st.session_state.chat_history = []

# ============================================================

# CSS

# ============================================================

def apply_css(dark_mode):
if dark_mode:
background = "#0f172a"
card = "#1e293b"
input_bg = "#1e293b"
text = "#ffffff"
border = "#475569"
accent = "#8b5cf6"
else:
background = "#f8fafc"
card = "#ffffff"
input_bg = "#ffffff"
text = "#000000"
border = "#cbd5e1"
accent = "#7c3aed"

```
st.markdown(
    f"""
    <style>

    /* ================================
       GLOBAL
    ================================= */

    .stApp {{
        background-color: {background};
    }}

    .stApp * {{
        color: {text} !important;
    }}

    body,
    p,
    span,
    div,
    label,
    small,
    strong,
    b,
    li,
    td,
    th {{
        color: {text} !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text} !important;
    }}

    /* ================================
       SIDEBAR
    ================================= */

    section[data-testid="stSidebar"] {{
        background-color: {card} !important;
        border-right: 1px solid {border};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* ================================
       INPUTS
    ================================= */

    input,
    textarea,
    select {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: {text} !important;
        opacity: 0.65 !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    div[data-baseweb="select"] * {{
        color: {text} !important;
    }}

    ul[role="listbox"],
    li[role="option"] {{
        background-color: {card} !important;
        color: {text} !important;
    }}

    /* ================================
       BUTTONS
    ================================= */

    .stButton > button,
    .stFormSubmitButton > button {{
        background-color: {card} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        border-color: {accent} !important;
        color: {text} !important;
    }}

    /* ================================
       CARDS
    ================================= */

    div[data-testid="stContainer"] {{
        color: {text} !important;
    }}

    .study-card {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }}

    .study-card h3,
    .study-card p,
    .study-card span {{
        color: {text} !important;
    }}

    /* ================================
       METRICS
    ================================= */

    div[data-testid="stMetric"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }}

    div[data-testid="stMetric"] * {{
        color: {text} !important;
    }}

    /* ================================
       EXPANDERS
    ================================= */

    div[data-testid="stExpander"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    div[data-testid="stExpander"] * {{
        color: {text} !important;
    }}

    /* ================================
       ALERTS
    ================================= */

    div[data-testid="stAlert"] * {{
        color: {text} !important;
    }}

    /* ================================
       CHECKBOX / RADIO / TOGGLE
    ================================= */

    div[data-testid="stCheckbox"] *,
    div[data-testid="stRadio"] *,
    div[data-testid="stToggle"] * {{
        color: {text} !important;
    }}

    /* ================================
       CHAT
    ================================= */

    div[data-testid="stChatMessage"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    div[data-testid="stChatMessage"] * {{
        color: {text} !important;
    }}

    /* ================================
       DATAFRAME
    ================================= */

    div[data-testid="stDataFrame"] * {{
        color: {text} !important;
    }}

    /* ================================
       WELCOME CARD
    ================================= */

    .welcome-card {{
        background: linear-gradient(
            135deg,
            #7c3aed,
            #4f46e5
        );
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
    }}

    .welcome-card h1,
    .welcome-card h2,
    .welcome-card p {{
        color: white !important;
    }}

    /* ================================
       NAVIGATION
    ================================= */

    .nav-title {{
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 5px;
    }}

    .muted {{
        opacity: 0.8;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
```

# ============================================================

# SIDEBAR

# ============================================================

with st.sidebar:

```
st.markdown(
    """
    <div style="
        font-size:28px;
        font-weight:800;
        margin-bottom:5px;
    ">
        🎓 StudySphere
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Learn smarter. Plan better. Achieve more.")

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

selected_page = st.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = selected_page

st.divider()

st.session_state.dark_mode = st.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

profile = get_profile()

if profile:
    st.divider()
    st.markdown("### 👤 Profile")
    st.write(profile["name"] or "Student")
    st.caption(profile["degree"] or "BS Artificial Intelligence")
```

# ============================================================

# APPLY THEME

# ============================================================

apply_css(st.session_state.dark_mode)

# ============================================================

# DASHBOARD

# ============================================================

if st.session_state.page == "Dashboard":

```
profile = get_profile()

student_name = (
    profile["name"]
    if profile and profile["name"]
    else "Student"
)

st.markdown(
    f"""
    <div class="welcome-card">
        <h1>Welcome back, {student_name}! 👋</h1>
        <p>
            Stay organized, study smarter, and keep moving
            toward your academic goals.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

subjects = get_subjects()
assignments = get_assignments()
exams = get_exams()
tasks = get_tasks()

pending_assignments = [
    a for a in assignments
    if a["status"] != "Completed"
]

upcoming_exams = [
    e for e in exams
    if e["exam_date"]
]

completed_tasks = [
    t for t in tasks
    if t["completed"] == 1
]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📚 Subjects",
        len(subjects)
    )

with col2:
    st.metric(
        "📝 Pending Assignments",
        len(pending_assignments)
    )

with col3:
    st.metric(
        "📖 Upcoming Exams",
        len(upcoming_exams)
    )

with col4:
    st.metric(
        "✅ Completed Tasks",
        len(completed_tasks)
    )

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("📌 Today's Tasks")

    today_string = date.today().isoformat()

    today_tasks = [
        task for task in tasks
        if task["task_date"] == today_string
    ]

    if not today_tasks:
        st.info("No tasks planned for today.")

    for task in today_tasks:

        status = "Completed" if task["completed"] else "Pending"

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{task["title"]}</h3>
                <p>
                    Subject:
                    {task["subject_name"] or "General"}
                </p>
                <p>
                    Duration:
                    {task["duration"]} minutes
                </p>
                <p>
                    Priority:
                    {task["priority"]}
                </p>
                <p>
                    Status:
                    {status}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

with right:

    st.subheader("⏰ Upcoming Assignments")

    if not pending_assignments:
        st.info("No pending assignments.")

    for assignment in pending_assignments[:5]:

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{assignment["title"]}</h3>
                <p>
                    Subject:
                    {assignment["subject_name"] or "General"}
                </p>
                <p>
                    Deadline:
                    {assignment["deadline"]}
                </p>
                <p>
                    Priority:
                    {assignment["priority"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
```

# ============================================================

# SUBJECTS

# ============================================================

elif st.session_state.page == "Subjects":

```
st.title("📚 Subjects")
st.write("Manage your university subjects.")

with st.form("add_subject_form"):

    st.subheader("Add New Subject")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Subject Name"
        )

    with col2:
        code = st.text_input(
            "Subject Code"
        )

    instructor = st.text_input(
        "Instructor"
    )

    description = st.text_area(
        "Description"
    )

    submitted = st.form_submit_button(
        "➕ Add Subject"
    )

    if submitted:

        if name.strip():

            add_subject(
                name.strip(),
                code.strip(),
                instructor.strip(),
                description.strip()
            )

            st.success(
                "Subject added successfully!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter a subject name."
            )

st.divider()

subjects = get_subjects()

st.subheader("Your Subjects")

if not subjects:
    st.info("No subjects added yet.")

for subject in subjects:

    with st.container(border=True):

        col1, col2 = st.columns([5, 1])

        with col1:

            st.markdown(
                f"### 📘 {subject['name']}"
            )

            if subject["code"]:
                st.write(
                    f"**Code:** {subject['code']}"
                )

            if subject["instructor"]:
                st.write(
                    f"**Instructor:** "
                    f"{subject['instructor']}"
                )

            if subject["description"]:
                st.write(
                    subject["description"]
                )

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_subject_{subject['id']}"
            ):

                delete_subject(
                    subject["id"]
                )

                st.rerun()
```

# ============================================================

# ASSIGNMENTS

# ============================================================

elif st.session_state.page == "Assignments":

```
st.title("📝 Assignments")
st.write(
    "Track assignments and deadlines."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_assignment_form"):

    st.subheader("Add Assignment")

    title = st.text_input(
        "Assignment Title"
    )

    description = st.text_area(
        "Description"
    )

    col1, col2 = st.columns(2)

    with col1:

        deadline = st.date_input(
            "Deadline",
            value=date.today()
        )

    with col2:

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High"
            ]
        )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Assignment"
    )

    if submitted:

        if title.strip():

            add_assignment(
                title.strip(),
                description.strip(),
                deadline.isoformat(),
                priority,
                subject_options[subject_name]
            )

            st.success(
                "Assignment added!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter an assignment title."
            )

st.divider()

assignments = get_assignments()

if not assignments:
    st.info(
        "No assignments available."
    )

for assignment in assignments:

    with st.container(border=True):

        st.subheader(
            f"📝 {assignment['title']}"
        )

        st.write(
            f"**Subject:** "
            f"{assignment['subject_name'] or 'General'}"
        )

        st.write(
            f"**Deadline:** "
            f"{assignment['deadline']}"
        )

        st.write(
            f"**Priority:** "
            f"{assignment['priority']}"
        )

        if assignment["description"]:
            st.write(
                assignment["description"]
            )

        current_status = assignment["status"]

        col1, col2 = st.columns([3, 1])

        with col1:

            new_status = st.selectbox(
                "Status",
                [
                    "Pending",
                    "In Progress",
                    "Completed"
                ],
                index=[
                    "Pending",
                    "In Progress",
                    "Completed"
                ].index(current_status),
                key=f"status_{assignment['id']}"
            )

            if new_status != current_status:

                update_assignment_status(
                    assignment["id"],
                    new_status
                )

                st.rerun()

        with col2:

            if st.button(
                "🗑️ Delete",
                key=f"delete_assignment_{assignment['id']}"
            ):

                delete_assignment(
                    assignment["id"]
                )

                st.rerun()
```

# ============================================================

# EXAMS

# ============================================================

elif st.session_state.page == "Exams":

```
st.title("📖 Exams")
st.write(
    "Keep track of your upcoming exams."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_exam_form"):

    st.subheader("Add Exam")

    title = st.text_input(
        "Exam Title"
    )

    exam_date = st.date_input(
        "Exam Date",
        value=date.today()
    )

    syllabus = st.text_area(
        "Syllabus"
    )

    notes = st.text_area(
        "Notes"
    )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Exam"
    )

    if submitted:

        if title.strip():

            add_exam(
                title.strip(),
                exam_date.isoformat(),
                syllabus.strip(),
                notes.strip(),
                subject_options[subject_name]
            )

            st.success(
                "Exam added successfully!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter an exam title."
            )

st.divider()

exams = get_exams()

if not exams:
    st.info(
        "No exams added yet."
    )

for exam in exams:

    with st.container(border=True):

        st.subheader(
            f"📚 {exam['title']}"
        )

        st.write(
            f"**Subject:** "
            f"{exam['subject_name'] or 'General'}"
        )

        st.write(
            f"**Exam Date:** "
            f"{exam['exam_date']}"
        )

        if exam["syllabus"]:
            st.write(
                f"**Syllabus:** {exam['syllabus']}"
            )

        if exam["notes"]:
            st.write(
                f"**Notes:** {exam['notes']}"
            )

        if st.button(
            "🗑️ Delete",
            key=f"delete_exam_{exam['id']}"
        ):

            delete_exam(
                exam["id"]
            )

            st.rerun()
```

# ============================================================

# STUDY PLANNER

# ============================================================

elif st.session_state.page == "Study Planner":

```
st.title("📅 Study Planner")
st.write(
    "Plan your daily study sessions."
)

subjects = get_subjects()

subject_options = {
    "General": None
}

for subject in subjects:
    subject_options[
        f"{subject['name']} ({subject['code']})"
    ] = subject["id"]

with st.form("add_task_form"):

    st.subheader("Add Study Task")

    title = st.text_input(
        "Task Title"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        task_date = st.date_input(
            "Date",
            value=date.today()
        )

    with col2:

        duration = st.number_input(
            "Duration (minutes)",
            min_value=5,
            max_value=600,
            value=60,
            step=5
        )

    with col3:

        priority = st.selectbox(
            "Priority",
            [
                "Low",
                "Medium",
                "High"
            ]
        )

    subject_name = st.selectbox(
        "Subject",
        list(subject_options.keys())
    )

    submitted = st.form_submit_button(
        "➕ Add Task"
    )

    if submitted:

        if title.strip():

            add_task(
                title.strip(),
                task_date.isoformat(),
                duration,
                priority,
                subject_options[subject_name]
            )

            st.success(
                "Study task added!"
            )

            st.rerun()

        else:
            st.warning(
                "Please enter a task title."
            )

st.divider()

tasks = get_tasks()

if not tasks:
    st.info(
        "No study tasks yet."
    )

for task in tasks:

    with st.container(border=True):

        col1, col2, col3 = st.columns(
            [1, 5, 1]
        )

        with col1:

            completed = st.checkbox(
                "Done",
                value=bool(task["completed"]),
                key=f"task_{task['id']}"
            )

            if completed != bool(task["completed"]):

                update_task_completion(
                    task["id"],
                    completed
                )

                st.rerun()

        with col2:

            if task["completed"]:
                st.markdown(
                    f"### ~~{task['title']}~~"
                )
            else:
                st.markdown(
                    f"### {task['title']}"
                )

            st.write(
                f"📅 {task['task_date']}  |  "
                f"⏱️ {task['duration']} minutes  |  "
                f"🎯 {task['priority']}"
            )

            st.write(
                f"📚 Subject: "
                f"{task['subject_name'] or 'General'}"
            )

        with col3:

            if st.button(
                "🗑️",
                key=f"delete_task_{task['id']}"
            ):

                delete_task(
                    task["id"]
                )

                st.rerun()
```

# ============================================================

# AI TUTOR

# ============================================================

elif st.session_state.page == "AI Tutor":

```
st.title("🤖 AI Tutor")

st.write(
    "Ask questions about programming, AI, "
    "databases, mathematics, or any subject."
)

for message in st.session_state.chat_history:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

user_prompt = st.chat_input(
    "Ask your AI Tutor something..."
)

if user_prompt:

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    tutor_prompt = f"""
```

You are StudySphere AI Tutor.

The student is a university student studying
Artificial Intelligence.

Explain concepts in a beginner-friendly way.

Use simple language and examples.

If the student asks about programming,
explain the logic step by step.

Student question:

{user_prompt}
"""

```
    answer = ask_gemini(
        tutor_prompt
    )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
```

# ============================================================

# AI STUDY PLAN

# ============================================================

elif st.session_state.page == "AI Study Plan":

```
st.title("🧠 AI Study Plan Generator")

st.write(
    "Let AI create a personalized study plan "
    "based on your workload."
)

col1, col2 = st.columns(2)

with col1:

    study_goal = st.text_input(
        "What do you want to study?",
        placeholder="Example: Python for AI"
    )

    available_hours = st.number_input(
        "Hours available per week",
        min_value=1,
        max_value=60,
        value=10
    )

with col2:

    duration = st.selectbox(
        "Plan Duration",
        [
            "1 week",
            "2 weeks",
            "1 month",
            "3 months",
            "6 months"
        ]
    )

    level = st.selectbox(
        "Your Skill Level",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )

if st.button(
    "✨ Generate Study Plan"
):

    if not study_goal.strip():

        st.warning(
            "Please enter what you want to study."
        )

    else:

        with st.spinner(
            "Creating your personalized study plan..."
        ):

            plan_prompt = f"""
```

Create a practical study plan for a university student.

Topic:
{study_goal}

Skill level:
{level}

Available study time:
{available_hours} hours per week

Duration:
{duration}

Create:

1. Weekly goals
2. Topics to study
3. Daily study activities
4. Practice tasks
5. Projects
6. Revision strategy
7. Recommended milestones

Keep the plan realistic and beginner-friendly.

Use clear headings and bullet points.
"""

```
            plan = ask_gemini(
                plan_prompt
            )

        st.success(
            "Your study plan is ready!"
        )

        st.markdown(plan)

        if st.button(
            "💾 Save Study Plan"
        ):

            save_study_plan(
                study_goal,
                plan
            )

            st.success(
                "Study plan saved successfully!"
            )
```

# ============================================================

# PROFILE

# ============================================================

elif st.session_state.page == "Profile":

```
st.title("👤 Profile")

st.write(
    "Manage your student information."
)

profile = get_profile()

default_name = ""
default_email = ""
default_university = ""
default_degree = "BS Artificial Intelligence"
default_semester = "2nd Semester"
default_gpa = 3.8

if profile:

    default_name = profile["name"] or ""
    default_email = profile["email"] or ""
    default_university = profile["university"] or ""

    if profile["degree"]:
        default_degree = profile["degree"]

    if profile["semester"]:
        default_semester = profile["semester"]

    if profile["target_gpa"] is not None:
        default_gpa = profile["target_gpa"]

with st.form("profile_form"):

    name = st.text_input(
        "Full Name",
        value=default_name
    )

    email = st.text_input(
        "Email",
        value=default_email
    )

    university = st.text_input(
        "University",
        value=default_university
    )

    degree = st.text_input(
        "Degree",
        value=default_degree
    )

    semester = st.text_input(
        "Semester",
        value=default_semester
    )

    target_gpa = st.number_input(
        "Target GPA",
        min_value=0.0,
        max_value=4.0,
        value=float(default_gpa),
        step=0.1
    )

    submitted = st.form_submit_button(
        "💾 Save Profile"
    )

    if submitted:

        save_profile(
            name.strip(),
            email.strip(),
            university.strip(),
            degree.strip(),
            semester.strip(),
            target_gpa
        )

        st.success(
            "Profile saved successfully!"
        )

        st.rerun()
```

# ============================================================

# FOOTER

# ============================================================

st.divider()

st.markdown(
""" <div style="
     text-align:center;
     padding:15px;
     opacity:0.8;
 ">
🎓 StudySphere — AI Student Companion <br>
Learn smarter. Plan better. Achieve more. </div>
""",
unsafe_allow_html=True
)
