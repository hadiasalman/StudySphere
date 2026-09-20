import streamlit as st
import sqlite3
import json
import os
from datetime import datetime, date, timedelta

# ============================================================
# STUDYSPHERE — AI STUDENT COMPANION
# Single-file Streamlit MVP
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
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

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


init_database()


# ============================================================
# DATABASE HELPERS
# ============================================================

def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, params)

    if fetch:
        result = cursor.fetchall()
        conn.close()
        return result

    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


# ============================================================
# PROFILE
# ============================================================

def get_profile():
    rows = execute_query(
        "SELECT * FROM profile LIMIT 1",
        fetch=True
    )
    return rows[0] if rows else None


def save_profile(
    name,
    email,
    university,
    degree,
    semester,
    target_gpa
):
    existing = get_profile()

    if existing:
        execute_query("""
            UPDATE profile
            SET name=?,
                email=?,
                university=?,
                degree=?,
                semester=?,
                target_gpa=?
            WHERE id=?
        """, (
            name,
            email,
            university,
            degree,
            semester,
            target_gpa,
            existing["id"]
        ))
    else:
        execute_query("""
            INSERT INTO profile
            (name,email,university,degree,semester,target_gpa,created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (
            name,
            email,
            university,
            degree,
            semester,
            target_gpa,
            datetime.now().isoformat()
        ))


# ============================================================
# SUBJECTS
# ============================================================

def get_subjects():
    return execute_query(
        "SELECT * FROM subjects ORDER BY name",
        fetch=True
    )


def add_subject(name, code, instructor, description):
    execute_query("""
        INSERT INTO subjects
        (name,code,instructor,description,created_at)
        VALUES (?,?,?,?,?)
    """, (
        name,
        code,
        instructor,
        description,
        datetime.now().isoformat()
    ))


def delete_subject(subject_id):
    execute_query(
        "DELETE FROM subjects WHERE id=?",
        (subject_id,)
    )


# ============================================================
# ASSIGNMENTS
# ============================================================

def get_assignments():
    return execute_query("""
        SELECT assignments.*, subjects.name AS subject_name
        FROM assignments
        LEFT JOIN subjects
        ON assignments.subject_id = subjects.id
        ORDER BY deadline ASC
    """, fetch=True)


def add_assignment(
    title,
    description,
    deadline,
    priority,
    subject_id
):
    execute_query("""
        INSERT INTO assignments
        (title,description,deadline,priority,status,subject_id,created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (
        title,
        description,
        deadline,
        priority,
        "Pending",
        subject_id,
        datetime.now().isoformat()
    ))


def update_assignment_status(assignment_id, status):
    execute_query("""
        UPDATE assignments
        SET status=?
        WHERE id=?
    """, (status, assignment_id))


def delete_assignment(assignment_id):
    execute_query(
        "DELETE FROM assignments WHERE id=?",
        (assignment_id,)
    )


# ============================================================
# EXAMS
# ============================================================

def get_exams():
    return execute_query("""
        SELECT exams.*, subjects.name AS subject_name
        FROM exams
        LEFT JOIN subjects
        ON exams.subject_id = subjects.id
        ORDER BY exam_date ASC
    """, fetch=True)


def add_exam(
    title,
    exam_date,
    syllabus,
    notes,
    subject_id
):
    execute_query("""
        INSERT INTO exams
        (title,exam_date,syllabus,notes,subject_id,created_at)
        VALUES (?,?,?,?,?,?)
    """, (
        title,
        exam_date,
        syllabus,
        notes,
        subject_id,
        datetime.now().isoformat()
    ))


def delete_exam(exam_id):
    execute_query(
        "DELETE FROM exams WHERE id=?",
        (exam_id,)
    )


# ============================================================
# TASKS
# ============================================================

def get_tasks():
    return execute_query("""
        SELECT tasks.*, subjects.name AS subject_name
        FROM tasks
        LEFT JOIN subjects
        ON tasks.subject_id = subjects.id
        ORDER BY task_date ASC
    """, fetch=True)


def add_task(
    title,
    task_date,
    duration,
    priority,
    subject_id
):
    execute_query("""
        INSERT INTO tasks
        (title,task_date,duration,priority,completed,subject_id,created_at)
        VALUES (?,?,?,?,?,?,?)
    """, (
        title,
        task_date,
        duration,
        priority,
        0,
        subject_id,
        datetime.now().isoformat()
    ))


def update_task(task_id, completed):
    execute_query("""
        UPDATE tasks
        SET completed=?
        WHERE id=?
    """, (
        int(completed),
        task_id
    ))


def delete_task(task_id):
    execute_query(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )


# ============================================================
# AI / GEMINI
# ============================================================

def get_gemini_client():
    try:
        from google import genai

        api_key = None

        # Streamlit Cloud secrets
        if hasattr(st, "secrets"):
            try:
                api_key = st.secrets.get("GEMINI_API_KEY")
            except Exception:
                pass

        # Local environment
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return None

        return genai.Client(api_key=api_key)

    except Exception:
        return None


def ask_gemini(prompt):
    client = get_gemini_client()

    if not client:
        return (
            "Gemini is not configured yet.\n\n"
            "Add your GEMINI_API_KEY to Streamlit Secrets "
            "to activate the AI features."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI error: {str(e)}"


# ============================================================
# CUSTOM CSS
# ============================================================

def apply_css(dark_mode=False):

    if dark_mode:
        background = "#0f172a"
        card = "#1e293b"
        text = "#f8fafc"
        muted = "#94a3b8"
    else:
        background = "#f8fafc"
        card = "#ffffff"
        text = "#0f172a"
        muted = "#64748b"

    st.markdown(
        f"""
        <style>

        .stApp {{
            background: {background};
        }}

        .main-title {{
            font-size: 2.5rem;
            font-weight: 800;
            color: {text};
            margin-bottom: 0;
        }}

        .subtitle {{
            color: {muted};
            font-size: 1rem;
            margin-bottom: 25px;
        }}

        .stat-card {{
            background: {card};
            border-radius: 16px;
            padding: 22px;
            border: 1px solid rgba(128,128,128,0.15);
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: 800;
            color: {text};
        }}

        .stat-label {{
            color: {muted};
            font-size: 0.9rem;
        }}

        .section-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: {text};
            margin-top: 25px;
            margin-bottom: 15px;
        }}

        .welcome {{
            background: linear-gradient(
                135deg,
                #6366f1,
                #8b5cf6
            );
            color: white;
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 25px;
        }}

        .welcome h1 {{
            margin: 0;
            font-size: 2rem;
        }}

        .welcome p {{
            margin-top: 8px;
            opacity: 0.9;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


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

    st.markdown("## 🎓 StudySphere")

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
        st.write(profile["name"] or "Student")

        if profile["degree"]:
            st.caption(profile["degree"])


apply_css(st.session_state.dark_mode)


# ============================================================
# DASHBOARD
# ============================================================

def dashboard():

    profile = get_profile()
    subjects = get_subjects()
    assignments = get_assignments()
    exams = get_exams()
    tasks = get_tasks()

    name = profile["name"] if profile else "Student"

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

    total_assignments = len(assignments)

    pending_assignments = len([
        a for a in assignments
        if a["status"] != "Completed"
    ])

    completed_tasks = len([
        t for t in tasks
        if t["completed"]
    ])

    pending_tasks = len([
        t for t in tasks
        if not t["completed"]
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{len(subjects)}</div>
                <div class="stat-label">Subjects</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{pending_assignments}</div>
                <div class="stat-label">Pending Assignments</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{len(exams)}</div>
                <div class="stat-label">Upcoming Exams</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{completed_tasks}</div>
                <div class="stat-label">Completed Tasks</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">📚 Today\'s Tasks</div>',
        unsafe_allow_html=True
    )

    today = date.today().isoformat()

    today_tasks = [
        t for t in tasks
        if t["task_date"] == today
    ]

    if not today_tasks:
        st.info("No tasks scheduled for today.")

    for task in today_tasks:

        completed = bool(task["completed"])

        new_value = st.checkbox(
            f"{'~~' if completed else ''}"
            f"{task['title']} "
            f"({task['duration'] or 0} min)"
            f"{'~~' if completed else ''}",
            value=completed,
            key=f"dashboard_task_{task['id']}"
        )

        if new_value != completed:
            update_task(task["id"], new_value)
            st.rerun()

    st.markdown(
        '<div class="section-title">📝 Upcoming Assignments</div>',
        unsafe_allow_html=True
    )

    upcoming_assignments = [
        a for a in assignments
        if a["status"] != "Completed"
    ][:5]

    if not upcoming_assignments:
        st.success("No pending assignments! 🎉")

    for assignment in upcoming_assignments:

        st.write(
            f"**{assignment['title']}** — "
            f"{assignment['deadline']} "
            f"({assignment['priority']})"
        )

    st.markdown(
        '<div class="section-title">📅 Upcoming Exams</div>',
        unsafe_allow_html=True
    )

    upcoming_exams = exams[:5]

    if not upcoming_exams:
        st.info("No exams added yet.")

    for exam in upcoming_exams:

        subject = exam["subject_name"] or "No subject"

        st.write(
            f"**{exam['title']}** — "
            f"{subject} — {exam['exam_date']}"
        )


# ============================================================
# SUBJECTS
# ============================================================

def subjects_page():

    st.title("📚 Subjects")

    subjects = get_subjects()

    with st.expander("➕ Add New Subject"):

        with st.form("subject_form"):

            name = st.text_input("Subject Name")
            code = st.text_input("Course Code")
            instructor = st.text_input("Instructor")
            description = st.text_area("Description")

            submitted = st.form_submit_button(
                "Add Subject",
                use_container_width=True
            )

            if submitted:

                if not name.strip():
                    st.error("Subject name is required.")
                else:
                    add_subject(
                        name,
                        code,
                        instructor,
                        description
                    )
                    st.success("Subject added successfully!")
                    st.rerun()

    st.divider()

    if not subjects:
        st.info("No subjects added yet.")
        return

    for subject in subjects:

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:
                st.subheader(subject["name"])

                if subject["code"]:
                    st.caption(f"Course Code: {subject['code']}")

                if subject["instructor"]:
                    st.write(
                        f"👨‍🏫 {subject['instructor']}"
                    )

                if subject["description"]:
                    st.write(subject["description"])

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_subject_{subject['id']}"
                ):
                    delete_subject(subject["id"])
                    st.rerun()


# ============================================================
# ASSIGNMENTS
# ============================================================

def assignments_page():

    st.title("📝 Assignment Manager")

    subjects = get_subjects()

    subject_options = {
        "No Subject": None
    }

    for subject in subjects:
        subject_options[
            subject["name"]
        ] = subject["id"]

    with st.expander("➕ Add Assignment"):

        with st.form("assignment_form"):

            title = st.text_input("Assignment Title")

            description = st.text_area(
                "Description"
            )

            deadline = st.date_input(
                "Deadline",
                value=date.today()
            )

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"]
            )

            selected_subject = st.selectbox(
                "Subject",
                list(subject_options.keys())
            )

            submitted = st.form_submit_button(
                "Add Assignment",
                use_container_width=True
            )

            if submitted:

                if not title.strip():
                    st.error("Assignment title is required.")
                else:

                    add_assignment(
                        title,
                        description,
                        deadline.isoformat(),
                        priority,
                        subject_options[selected_subject]
                    )

                    st.success("Assignment added!")
                    st.rerun()

    st.divider()

    assignments = get_assignments()

    if not assignments:
        st.info("No assignments yet.")
        return

    for assignment in assignments:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [4, 2, 1]
            )

            with col1:

                st.subheader(
                    assignment["title"]
                )

                if assignment["description"]:
                    st.write(
                        assignment["description"]
                    )

                st.caption(
                    f"Subject: "
                    f"{assignment['subject_name'] or 'None'}"
                )

            with col2:

                st.write(
                    f"📅 {assignment['deadline']}"
                )

                st.write(
                    f"Priority: "
                    f"**{assignment['priority']}**"
                )

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
                    ].index(assignment["status"]),
                    key=f"status_{assignment['id']}"
                )

                if new_status != assignment["status"]:
                    update_assignment_status(
                        assignment["id"],
                        new_status
                    )
                    st.rerun()

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_assignment_{assignment['id']}"
                ):
                    delete_assignment(
                        assignment["id"]
                    )
                    st.rerun()


# ============================================================
# EXAMS
# ============================================================

def exams_page():

    st.title("📅 Exam Manager")

    subjects = get_subjects()

    subject_options = {
        "No Subject": None
    }

    for subject in subjects:
        subject_options[
            subject["name"]
        ] = subject["id"]

    with st.expander("➕ Add Exam"):

        with st.form("exam_form"):

            title = st.text_input("Exam Title")

            exam_date = st.date_input(
                "Exam Date",
                value=date.today()
            )

            selected_subject = st.selectbox(
                "Subject",
                list(subject_options.keys())
            )

            syllabus = st.text_area(
                "Syllabus / Topics"
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Add Exam",
                use_container_width=True
            )

            if submitted:

                if not title.strip():
                    st.error("Exam title is required.")
                else:

                    add_exam(
                        title,
                        exam_date.isoformat(),
                        syllabus,
                        notes,
                        subject_options[selected_subject]
                    )

                    st.success("Exam added!")
                    st.rerun()

    st.divider()

    exams = get_exams()

    if not exams:
        st.info("No exams added yet.")
        return

    for exam in exams:

        with st.container(border=True):

            col1, col2 = st.columns([4, 2])

            with col1:

                st.subheader(exam["title"])

                st.write(
                    f"📚 "
                    f"{exam['subject_name'] or 'No subject'}"
                )

                if exam["syllabus"]:
                    st.write(
                        f"**Syllabus:** "
                        f"{exam['syllabus']}"
                    )

                if exam["notes"]:
                    st.write(
                        f"**Notes:** {exam['notes']}"
                    )

            with col2:

                st.metric(
                    "Exam Date",
                    exam["exam_date"]
                )

                if st.button(
                    "Delete",
                    key=f"delete_exam_{exam['id']}"
                ):
                    delete_exam(exam["id"])
                    st.rerun()


# ============================================================
# STUDY PLANNER
# ============================================================

def planner_page():

    st.title("✅ Study Planner")

    subjects = get_subjects()

    subject_options = {
        "No Subject": None
    }

    for subject in subjects:
        subject_options[
            subject["name"]
        ] = subject["id"]

    with st.expander("➕ Add Study Task"):

        with st.form("task_form"):

            title = st.text_input(
                "Task Title"
            )

            task_date = st.date_input(
                "Date",
                value=date.today()
            )

            duration = st.number_input(
                "Duration (minutes)",
                min_value=5,
                max_value=600,
                value=60,
                step=5
            )

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"]
            )

            selected_subject = st.selectbox(
                "Subject",
                list(subject_options.keys())
            )

            submitted = st.form_submit_button(
                "Add Task",
                use_container_width=True
            )

            if submitted:

                if not title.strip():
                    st.error("Task title is required.")
                else:

                    add_task(
                        title,
                        task_date.isoformat(),
                        duration,
                        priority,
                        subject_options[selected_subject]
                    )

                    st.success("Task added!")
                    st.rerun()

    st.divider()

    tasks = get_tasks()

    if not tasks:
        st.info("No study tasks yet.")
        return

    for task in tasks:

        completed = bool(task["completed"])

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [5, 2, 1]
            )

            with col1:

                new_completed = st.checkbox(
                    task["title"],
                    value=completed,
                    key=f"task_{task['id']}"
                )

                if new_completed != completed:
                    update_task(
                        task["id"],
                        new_completed
                    )
                    st.rerun()

                st.caption(
                    f"📚 "
                    f"{task['subject_name'] or 'No subject'}"
                )

            with col2:

                st.write(
                    f"📅 {task['task_date']}"
                )

                st.write(
                    f"⏱️ {task['duration'] or 0} min"
                )

                st.write(
                    f"Priority: {task['priority']}"
                )

            with col3:

                if st.button(
                    "🗑️",
                    key=f"delete_task_{task['id']}"
                ):
                    delete_task(task["id"])
                    st.rerun()


# ============================================================
# AI TUTOR
# ============================================================

def ai_tutor_page():

    st.title("🤖 AI Tutor")

    st.write(
        "Ask StudySphere anything about your studies."
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):
            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Ask your AI Tutor..."
    )

    if prompt:

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        system_prompt = """
You are StudySphere AI Tutor.

Your job is to help university students learn.

Rules:
- Explain concepts clearly.
- Use beginner-friendly language.
- Give examples.
- Break difficult concepts into steps.
- Help students understand rather than blindly providing answers.
- For programming questions, explain the logic.
- Use headings and bullet points when useful.
"""

        full_prompt = (
            system_prompt
            + "\n\nStudent question:\n"
            + prompt
        )

        response = ask_gemini(
            full_prompt
        )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        with st.chat_message("assistant"):
            st.markdown(response)


# ============================================================
# AI STUDY PLAN
# ============================================================

def ai_study_plan_page():

    st.title("🧠 AI Study Plan Generator")

    st.write(
        "Create a personalized study plan using your academic workload."
    )

    subjects = get_subjects()
    assignments = get_assignments()
    exams = get_exams()

    with st.form("study_plan_form"):

        available_hours = st.number_input(
            "Available study hours per day",
            min_value=1,
            max_value=16,
            value=3
        )

        plan_days = st.number_input(
            "Plan duration (days)",
            min_value=1,
            max_value=30,
            value=7
        )

        priorities = st.text_area(
            "What do you want to focus on?",
            placeholder=(
                "Example: C++, Database, AI exam preparation"
            )
        )

        submitted = st.form_submit_button(
            "✨ Generate Study Plan",
            use_container_width=True
        )

    if submitted:

        subject_text = "\n".join([
            f"- {s['name']}"
            for s in subjects
        ])

        assignment_text = "\n".join([
            f"- {a['title']} | "
            f"Deadline: {a['deadline']} | "
            f"Priority: {a['priority']}"
            for a in assignments
            if a["status"] != "Completed"
        ])

        exam_text = "\n".join([
            f"- {e['title']} | "
            f"Date: {e['exam_date']} | "
            f"Subject: {e['subject_name'] or 'Unknown'}"
            for e in exams
        ])

        prompt = f"""
You are StudySphere AI Study Planner.

Create a practical personalized study plan.

Student subjects:
{subject_text or "No subjects added"}

Pending assignments:
{assignment_text or "No pending assignments"}

Upcoming exams:
{exam_text or "No exams added"}

Available study time:
{available_hours} hours per day

Plan duration:
{plan_days} days

Student priorities:
{priorities or "General academic improvement"}

Create a day-by-day study plan.

For every day include:
- Subject
- Topic/activity
- Duration
- Priority
- Revision/review activity

Make the plan realistic and avoid overloading the student.
"""

        with st.spinner(
            "Creating your personalized study plan..."
        ):

            response = ask_gemini(prompt)

        st.success(
            "Your study plan is ready!"
        )

        st.markdown(response)

        execute_query("""
            INSERT INTO study_plans
            (title,content,created_at)
            VALUES (?,?,?)
        """, (
            f"{plan_days}-Day Study Plan",
            response,
            datetime.now().isoformat()
        ))


# ============================================================
# PROFILE
# ============================================================

def profile_page():

    st.title("👤 Student Profile")

    profile = get_profile()

    with st.form("profile_form"):

        name = st.text_input(
            "Full Name",
            value=profile["name"] if profile else ""
        )

        email = st.text_input(
            "Email",
            value=profile["email"] if profile else ""
        )

        university = st.text_input(
            "University / College",
            value=profile["university"] if profile else ""
        )

        degree = st.text_input(
            "Degree / Program",
            value=profile["degree"] if profile else ""
        )

        semester = st.text_input(
            "Semester",
            value=profile["semester"] if profile else ""
        )

        target_gpa = st.number_input(
            "Target GPA",
            min_value=0.0,
            max_value=4.0,
            value=float(
                profile["target_gpa"]
                if profile and profile["target_gpa"]
                else 3.5
            ),
            step=0.1
        )

        submitted = st.form_submit_button(
            "Save Profile",
            use_container_width=True
        )

        if submitted:

            if not name.strip():
                st.error("Please enter your name.")
            else:

                save_profile(
                    name,
                    email,
                    university,
                    degree,
                    semester,
                    target_gpa
                )

                st.success(
                    "Profile saved successfully!"
                )

                st.rerun()


# ============================================================
# ROUTING
# ============================================================

page = st.session_state.page

if page == "Dashboard":
    dashboard()

elif page == "Subjects":
    subjects_page()

elif page == "Assignments":
    assignments_page()

elif page == "Exams":
    exams_page()

elif page == "Study Planner":
    planner_page()

elif page == "AI Tutor":
    ai_tutor_page()

elif page == "AI Study Plan":
    ai_study_plan_page()

elif page == "Profile":
    profile_page()
```
