import streamlit as st
import sqlite3
import os
from datetime import datetime, date

st.set_page_config(
page_title="StudySphere",
page_icon="🎓",
layout="wide"
)

DB_NAME = "studysphere.db"

# ============================================================

# DATABASE

# ============================================================

def get_connection():
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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

# DATABASE FUNCTIONS

# ============================================================

def execute_query(query, params=(), fetch=False):
conn = get_connection()
cursor = conn.cursor()
cursor.execute(query, params)

```
if fetch:
    data = cursor.fetchall()
    conn.close()
    return data

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

def save_profile(name, email, university, degree, semester, target_gpa):
profile = get_profile()

```
if profile:
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
            profile["id"]
        )
    )
else:
    execute_query(
        """
        INSERT INTO profile
        (name, email, university, degree, semester, target_gpa, created_at)
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
(name, code, instructor, description, created_at)
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
SELECT assignments.*, subjects.name AS subject_name
FROM assignments
LEFT JOIN subjects
ON assignments.subject_id = subjects.id
ORDER BY deadline
""",
fetch=True
)

def add_assignment(title, description, deadline, priority, subject_id):
execute_query(
"""
INSERT INTO assignments
(title, description, deadline, priority, status, subject_id, created_at)
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
"UPDATE assignments SET status = ? WHERE id = ?",
(status, assignment_id)
)

def delete_assignment(assignment_id):
execute_query(
"DELETE FROM assignments WHERE id = ?",
(assignment_id,)
)

def get_exams():
return execute_query(
"""
SELECT exams.*, subjects.name AS subject_name
FROM exams
LEFT JOIN subjects
ON exams.subject_id = subjects.id
ORDER BY exam_date
""",
fetch=True
)

def add_exam(title, exam_date, syllabus, notes, subject_id):
execute_query(
"""
INSERT INTO exams
(title, exam_date, syllabus, notes, subject_id, created_at)
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
SELECT tasks.*, subjects.name AS subject_name
FROM tasks
LEFT JOIN subjects
ON tasks.subject_id = subjects.id
ORDER BY task_date
""",
fetch=True
)

def add_task(title, task_date, duration, priority, subject_id):
execute_query(
"""
INSERT INTO tasks
(title, task_date, duration, priority, completed, subject_id, created_at)
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
"UPDATE tasks SET completed = ? WHERE id = ?",
(int(completed), task_id)
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
(title, content, created_at)
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
api_key = None

try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None
```

except Exception:
gemini_client = None

def ask_gemini(prompt):
if gemini_client is None:
return "Gemini API is not configured. Add GEMINI_API_KEY to Streamlit Secrets."

```
try:
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

except Exception as error:
    return f"Gemini error: {error}"
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

# THEME

# ============================================================

def apply_theme(dark):
if dark:
background = "#0f172a"
card = "#1e293b"
text = "#ffffff"
border = "#475569"
else:
background = "#f8fafc"
card = "#ffffff"
text = "#000000"
border = "#cbd5e1"

```
st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {background};
    }}

    .stApp * {{
        color: {text} !important;
    }}

    body {{
        background-color: {background};
        color: {text};
    }}

    h1, h2, h3, h4, h5, h6,
    p, span, label, div, li,
    td, th, small, strong {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {card} !important;
        border-right: 1px solid {border};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    input,
    textarea {{
        background-color: {card} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: {text} !important;
        opacity: 0.6 !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {card} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    div[data-baseweb="select"] * {{
        color: {text} !important;
    }}

    div[data-testid="stMetric"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
        border-radius: 15px;
        padding: 15px;
    }}

    div[data-testid="stMetric"] * {{
        color: {text} !important;
    }}

    div[data-testid="stExpander"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
    }}

    div[data-testid="stExpander"] * {{
        color: {text} !important;
    }}

    .stButton > button,
    .stFormSubmitButton > button {{
        background-color: {card} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 10px;
    }}

    .study-card {{
        background-color: {card};
        border: 1px solid {border};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }}

    .welcome-card {{
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 25px;
    }}

    .welcome-card h1,
    .welcome-card p {{
        color: white !important;
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
    "<h1>🎓 StudySphere</h1>",
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

st.session_state.page = st.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page)
)

st.divider()

st.session_state.dark_mode = st.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

profile = get_profile()

if profile:
    st.divider()
    st.write("👤", profile["name"] or "Student")
    st.caption(profile["degree"] or "")
```

apply_theme(st.session_state.dark_mode)

# ============================================================

# DASHBOARD

# ============================================================

if st.session_state.page == "Dashboard":

```
profile = get_profile()

name = "Student"

if profile and profile["name"]:
    name = profile["name"]

st.markdown(
    f"""
    <div class="welcome-card">
        <h1>Welcome back, {name}! 👋</h1>
        <p>Learn smarter. Plan better. Achieve more.</p>
    </div>
    """,
    unsafe_allow_html=True
)

subjects = get_subjects()
assignments = get_assignments()
exams = get_exams()
tasks = get_tasks()

pending = [
    item for item in assignments
    if item["status"] != "Completed"
]

completed_tasks = [
    item for item in tasks
    if item["completed"] == 1
]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📚 Subjects", len(subjects))

with c2:
    st.metric("📝 Assignments", len(pending))

with c3:
    st.metric("📖 Exams", len(exams))

with c4:
    st.metric("✅ Completed Tasks", len(completed_tasks))

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("📅 Today's Tasks")

    today = date.today().isoformat()

    today_tasks = [
        item for item in tasks
        if item["task_date"] == today
    ]

    if not today_tasks:
        st.info("No tasks planned for today.")

    for task in today_tasks:

        status = "Completed" if task["completed"] else "Pending"

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{task['title']}</h3>
                <p>Subject: {task['subject_name'] or 'General'}</p>
                <p>Duration: {task['duration']} minutes</p>
                <p>Priority: {task['priority']}</p>
                <p>Status: {status}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

with right:

    st.subheader("📝 Upcoming Assignments")

    if not pending:
        st.info("No pending assignments.")

    for assignment in pending[:5]:

        st.markdown(
            f"""
            <div class="study-card">
                <h3>{assignment['title']}</h3>
                <p>Subject: {assignment['subject_name'] or 'General'}</p>
                <p>Deadline: {assignment['deadline']}</p>
                <p>Priority: {assignment['priority']}</p>
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

with st.form("subject_form"):

    name = st.text_input("Subject Name")
    code = st.text_input("Subject Code")
    instructor = st.text_input("Instructor")
    description = st.text_area("Description")

    submit = st.form_submit_button("➕ Add Subject")

    if submit:

        if name.strip():

            add_subject(
                name.strip(),
                code.strip(),
                instructor.strip(),
                description.strip()
            )

            st.success("Subject added!")
            st.rerun()

        else:
            st.warning("Enter a subject name.")

st.divider()

subjects = get_subjects()

for subject in subjects:

    with st.container(border=True):

        st.subheader(
            f"📘 {subject['name']}"
        )

        st.write(
            f"**Code:** {subject['code'] or 'N/A'}"
        )

        st.write(
            f"**Instructor:** {subject['instructor'] or 'N/A'}"
        )

        if subject["description"]:
            st.write(subject["description"])

        if st.button(
            "🗑️ Delete",
            key=f"subject_delete_{subject['id']}"
        ):

            delete_subject(subject["id"])
            st.rerun()
```

# ============================================================

# ASSIGNMENTS

# ============================================================

elif st.session_state.page == "Assignments":

```
st.title("📝 Assignments")

subjects = get_subjects()

subject_map = {"General": None}

for subject in subjects:
    subject_map[subject["name"]] = subject["id"]

with st.form("assignment_form"):

    title = st.text_input("Assignment Title")
    description = st.text_area("Description")

    deadline = st.date_input(
        "Deadline",
        value=date.today()
    )

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    subject = st.selectbox(
        "Subject",
        list(subject_map.keys())
    )

    submit = st.form_submit_button(
        "➕ Add Assignment"
    )

    if submit:

        if title.strip():

            add_assignment(
                title.strip(),
                description.strip(),
                deadline.isoformat(),
                priority,
                subject_map[subject]
            )

            st.success("Assignment added!")
            st.rerun()

        else:
            st.warning("Enter an assignment title.")

st.divider()

assignments = get_assignments()

for assignment in assignments:

    with st.container(border=True):

        st.subheader(
            f"📝 {assignment['title']}"
        )

        st.write(
            f"Subject: {assignment['subject_name'] or 'General'}"
        )

        st.write(
            f"Deadline: {assignment['deadline']}"
        )

        st.write(
            f"Priority: {assignment['priority']}"
        )

        status_options = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        current_status = assignment["status"]

        if current_status not in status_options:
            current_status = "Pending"

        new_status = st.selectbox(
            "Status",
            status_options,
            index=status_options.index(current_status),
            key=f"assignment_status_{assignment['id']}"
        )

        if new_status != assignment["status"]:

            update_assignment_status(
                assignment["id"],
                new_status
            )

            st.rerun()

        if st.button(
            "🗑️ Delete",
            key=f"assignment_delete_{assignment['id']}"
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

subjects = get_subjects()

subject_map = {"General": None}

for subject in subjects:
    subject_map[subject["name"]] = subject["id"]

with st.form("exam_form"):

    title = st.text_input("Exam Title")

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

    subject = st.selectbox(
        "Subject",
        list(subject_map.keys())
    )

    submit = st.form_submit_button(
        "➕ Add Exam"
    )

    if submit:

        if title.strip():

            add_exam(
                title.strip(),
                exam_date.isoformat(),
                syllabus.strip(),
                notes.strip(),
                subject_map[subject]
            )

            st.success("Exam added!")
            st.rerun()

        else:
            st.warning("Enter an exam title.")

st.divider()

exams = get_exams()

for exam in exams:

    with st.container(border=True):

        st.subheader(
            f"📚 {exam['title']}"
        )

        st.write(
            f"Subject: {exam['subject_name'] or 'General'}"
        )

        st.write(
            f"Exam Date: {exam['exam_date']}"
        )

        if exam["syllabus"]:
            st.write(
                f"Syllabus: {exam['syllabus']}"
            )

        if exam["notes"]:
            st.write(
                f"Notes: {exam['notes']}"
            )

        if st.button(
            "🗑️ Delete",
            key=f"exam_delete_{exam['id']}"
        ):

            delete_exam(exam["id"])
            st.rerun()
```

# ============================================================

# STUDY PLANNER

# ============================================================

elif st.session_state.page == "Study Planner":

```
st.title("📅 Study Planner")

subjects = get_subjects()

subject_map = {"General": None}

for subject in subjects:
    subject_map[subject["name"]] = subject["id"]

with st.form("task_form"):

    title = st.text_input(
        "Task Title"
    )

    task_date = st.date_input(
        "Date",
        value=date.today()
    )

    duration = st.number_input(
        "Duration in minutes",
        min_value=5,
        max_value=600,
        value=60,
        step=5
    )

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    subject = st.selectbox(
        "Subject",
        list(subject_map.keys())
    )

    submit = st.form_submit_button(
        "➕ Add Task"
    )

    if submit:

        if title.strip():

            add_task(
                title.strip(),
                task_date.isoformat(),
                duration,
                priority,
                subject_map[subject]
            )

            st.success("Task added!")
            st.rerun()

        else:
            st.warning("Enter a task title.")

st.divider()

tasks = get_tasks()

for task in tasks:

    with st.container(border=True):

        completed = st.checkbox(
            "Completed",
            value=bool(task["completed"]),
            key=f"task_complete_{task['id']}"
        )

        if completed != bool(task["completed"]):

            update_task_completion(
                task["id"],
                completed
            )

            st.rerun()

        st.subheader(
            task["title"]
        )

        st.write(
            f"📅 {task['task_date']}"
        )

        st.write(
            f"⏱️ {task['duration']} minutes"
        )

        st.write(
            f"🎯 {task['priority']}"
        )

        st.write(
            f"📚 {task['subject_name'] or 'General'}"
        )

        if st.button(
            "🗑️ Delete",
            key=f"task_delete_{task['id']}"
        ):

            delete_task(task["id"])
            st.rerun()
```

# =====
