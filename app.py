import streamlit as st
import sqlite3

st.set_page_config(
    page_title="StudySphere",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER DEFAULT 0, subject_id INTEGER)")
conn.commit()

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=st.session_state.dark_mode
)

st.session_state.dark_mode = dark_mode

bg = "#0F172A" if dark_mode else "#F8FAFC"
card = "#1E293B" if dark_mode else "#FFFFFF"
text = "#F8FAFC" if dark_mode else "#0F172A"
muted = "#CBD5E1" if dark_mode else "#64748B"
border = "#334155" if dark_mode else "#E2E8F0"

st.markdown(
f"""
<style>

.stApp {{
    background: {bg};
}}

[data-testid="stSidebar"] {{
    background: {"#111827" if dark_mode else "#FFFFFF"};
    border-right: 1px solid {border};
}}

[data-testid="stSidebar"] * {{
    color: {text} !important;
}}

.block-container {{
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {text} !important;
}}

p, label, span {{
    color: {text};
}}

.brand-box {{
    padding: 10px 5px 22px 5px;
}}

.brand-title {{
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.8px;
}}

.brand-subtitle {{
    color: {muted};
    font-size: 12px;
    margin-top: 4px;
}}

.hero {{
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    padding: 30px;
    border-radius: 22px;
    margin-bottom: 25px;
    box-shadow: 0 12px 35px rgba(79,70,229,0.22);
}}

.hero-title {{
    color: white !important;
    font-size: 31px;
    font-weight: 800;
    margin: 0;
}}

.hero-text {{
    color: rgba(255,255,255,0.88) !important;
    font-size: 15px;
    margin-top: 8px;
}}

.stat-card {{
    background: {card};
    border: 1px solid {border};
    border-radius: 18px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 5px 18px rgba(15,23,42,0.06);
}}

.stat-icon {{
    font-size: 25px;
}}

.stat-number {{
    font-size: 29px;
    font-weight: 800;
    margin-top: 6px;
}}

.stat-label {{
    color: {muted} !important;
    font-size: 13px;
    margin-top: 3px;
}}

.section-card {{
    background: {card};
    border: 1px solid {border};
    border-radius: 18px;
    padding: 22px;
    margin-top: 22px;
    box-shadow: 0 5px 18px rgba(15,23,42,0.04);
}}

.section-title {{
    font-size: 19px;
    font-weight: 750;
}}

.section-subtitle {{
    color: {muted} !important;
    font-size: 13px;
    margin-top: 4px;
    margin-bottom: 15px;
}}

.ai-card {{
    background: linear-gradient(135deg, #312E81, #581C87);
    border: 1px solid #4C1D95;
    border-radius: 20px;
    padding: 25px;
    margin-top: 24px;
}}

.ai-title {{
    color: white !important;
    font-size: 21px;
    font-weight: 800;
}}

.ai-text {{
    color: #E9D5FF !important;
    font-size: 14px;
    margin-top: 6px;
}}


/* ============================= */
/* TEAL BUTTON DESIGN */
/* ============================= */

div.stButton > button {{
    background: #14B8A6 !important;
    color: white !important;
    border: 1px solid #0F766E !important;
    border-radius: 11px;
    min-height: 42px;
    font-weight: 700;
    transition: all 0.2s ease;
}}

div.stButton > button:hover {{
    background: #0F766E !important;
    color: white !important;
    border-color: #0F766E !important;
    transform: translateY(-1px);
}}

div.stButton > button:active {{
    background: #115E59 !important;
    color: white !important;
}}

</style>
""",
unsafe_allow_html=True
)

st.sidebar.markdown(
"""
<div class="brand-box">
<div class="brand-title">🎓 StudySphere</div>
<div class="brand-subtitle">
Learn smarter. Plan better. Achieve more.
</div>
</div>
""",
unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [1, 2, 3, 4, 5],
    format_func=lambda x: {
        1: "🏠  Dashboard",
        2: "📚  Subjects",
        3: "📝  Assignments",
        4: "📅  Exams",
        5: "✅  Study Planner"
    }[x]
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🤖 AI Agent")

st.sidebar.caption(
    "Your personal academic AI agent is coming next."
)

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0")
pending_task_count = cursor.fetchone()[0]


# ==========================================
# DASHBOARD
# ==========================================

if page == 1:

    st.markdown(
    """
    <div class="hero">
    <div class="hero-title">
    Welcome back to StudySphere 👋
    </div>

    <div class="hero-text">
    Your academic command center for subjects,
    assignments, exams and daily study tasks.
    </div>
    </div>
    """,
    unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(
    f"""
    <div class="stat-card">
    <div class="stat-icon">📚</div>
    <div class="stat-number">{subject_count}</div>
    <div class="stat-label">Total Subjects</div>
    </div>
    """,
    unsafe_allow_html=True
    )

    c2.markdown(
    f"""
    <div class="stat-card">
    <div class="stat-icon">📝</div>
    <div class="stat-number">{assignment_count}</div>
    <div class="stat-label">Assignments</div>
    </div>
    """,
    unsafe_allow_html=True
    )

    c3.markdown(
    f"""
    <div class="stat-card">
    <div class="stat-icon">📅</div>
    <div class="stat-number">{exam_count}</div>
    <div class="stat-label">Exams</div>
    </div>
    """,
    unsafe_allow_html=True
    )

    c4.markdown(
    f"""
    <div class="stat-card">
    <div class="stat-icon">✅</div>
    <div class="stat-number">{pending_task_count}</div>
    <div class="stat-label">Pending Tasks</div>
    </div>
    """,
    unsafe_allow_html=True
    )

    cursor.execute(
        "SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5"
    )

    upcoming_assignments = cursor.fetchall()

    cursor.execute(
        "SELECT title, exam_date FROM exams ORDER BY exam_date LIMIT 5"
    )

    upcoming_exams = cursor.fetchall()

    left, right = st.columns(2)

    with left:

        st.markdown(
        """
        <div class="section-card">
        <div class="section-title">
        📝 Upcoming Assignments
        </div>

        <div class="section-subtitle">
        Stay ahead of your deadlines.
        </div>
        </div>
        """,
        unsafe_allow_html=True
        )

        st.dataframe(
            upcoming_assignments,
            use_container_width=True,
            hide_index=True,
            column_config={
                "title": "Assignment",
                "deadline": "Deadline",
                "priority": "Priority",
                "status": "Status"
            }
        )

    with right:

        st.markdown(
        """
        <div class="section-card">
        <div class="section-title">
        📅 Upcoming Exams
        </div>

        <div class="section-subtitle">
        Keep your exam schedule under control.
        </div>
        </div>
        """,
        unsafe_allow_html=True
        )

        st.dataframe(
            upcoming_exams,
            use_container_width=True,
            hide_index=True,
            column_config={
                "title": "Exam",
                "exam_date": "Exam Date"
            }
        )

    st.markdown(
    """
    <div class="ai-card">

    <div class="ai-title">
    🤖 StudySphere AI Agent
    </div>

    <div class="ai-text">
    Coming next — an intelligent academic agent that will
    understand your StudySphere data and help you decide
    what to study, when to study it, and what needs attention.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )


# ==========================================
# SUBJECTS
# ==========================================

elif page == 2:

    st.header("📚 Subjects")

    st.caption(
        "Manage all your university subjects in one place."
    )

    a, b, c = st.columns(3)

    subject_name = a.text_input(
        "Subject Name"
    )

    subject_code = b.text_input(
        "Subject Code"
    )

    subject_instructor = c.text_input(
        "Instructor"
    )

    add_subject = st.button(
        "➕ Add Subject",
        use_container_width=True
    )

    valid_subject = bool(
        subject_name.strip()
    )

    cursor.execute(
        "INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
        (
            subject_name.strip(),
            subject_code.strip(),
            subject_instructor.strip()
        )
    ) if add_subject and valid_subject else None

    conn.commit() if add_subject and valid_subject else None

    st.success(
        "Subject added successfully!"
    ) if add_subject and valid_subject else None

    st.error(
        "Please enter a subject name."
    ) if add_subject and not valid_subject else None

    cursor.execute(
        "SELECT id, name, code, instructor FROM subjects ORDER BY name"
    )

    subject_list = cursor.fetchall()

    st.markdown(
    """
    <div class="section-card">

    <div class="section-title">
    Your Subjects
    </div>

    <div class="section-subtitle">
    All subjects currently saved in StudySphere.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

    st.dataframe(
        subject_list,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "name": "Subject",
            "code": "Code",
            "instructor": "Instructor"
        }
    )


# ==========================================
# ASSIGNMENTS
# ==========================================

elif page == 3:

    st.header("📝 Assignments")

    st.caption(
        "Track deadlines, priorities and completion status."
    )

    cursor.execute(
        "SELECT id, name FROM subjects ORDER BY name"
    )

    assignment_subject_rows = cursor.fetchall()

    assignment_subject_names = [
        row[1]
        for row in assignment_subject_rows
    ]

    assignment_subject_ids = [
        row[0]
        for row in assignment_subject_rows
    ]

    a, b = st.columns(2)

    assignment_title = a.text_input(
        "Assignment Title"
    )

    assignment_deadline = b.date_input(
        "Deadline"
    )

    assignment_description = st.text_area(
        "Description"
    )

    c1, c2, c3 = st.columns(3)

    assignment_priority = c1.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    assignment_status = c2.selectbox(
        "Status",
        ["Pending", "In Progress", "Completed"]
    )

    assignment_subject = c3.selectbox(
        "Subject",
        assignment_subject_names
    ) if assignment_subject_names else ""

    assignment_subject_id = (
        assignment_subject_ids[
            assignment_subject_names.index(
                assignment_subject
            )
        ]
        if assignment_subject_names and assignment_subject
        else None
    )

    add_assignment = st.button(
        "➕ Add Assignment",
        use_container_width=True
    )

    valid_assignment = (
        bool(assignment_title.strip())
        and bool(assignment_subject_names)
    )

    cursor.execute(
        "INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
        (
            assignment_title.strip(),
            assignment_description.strip(),
            str(assignment_deadline),
            assignment_priority,
            assignment_status,
            assignment_subject_id
        )
    ) if add_assignment and valid_assignment else None

    conn.commit() if add_assignment and valid_assignment else None

    st.success(
        "Assignment added successfully!"
    ) if add_assignment and valid_assignment else None

    st.error(
        "Enter an assignment title and make sure you have at least one subject."
    ) if add_assignment and not valid_assignment else None

    cursor.execute(
        "SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline"
    )

    assignment_list = cursor.fetchall()

    st.markdown(
    """
    <div class="section-card">

    <div class="section-title">
    Assignment List
    </div>

    <div class="section-subtitle">
    Your saved assignments and their current status.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

    st.dataframe(
        assignment_list,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "title": "Assignment",
            "description": "Description",
            "deadline": "Deadline",
            "priority": "Priority",
            "status": "Status",
            "name": "Subject"
        }
    )


# ==========================================
# EXAMS
# ==========================================

elif page == 4:

    st.header("📅 Exams")

    st.caption(
        "Keep your exam dates, syllabus and notes organized."
    )

    cursor.execute(
        "SELECT id, name FROM subjects ORDER BY name"
    )

    exam_subject_rows = cursor.fetchall()

    exam_subject_names = [
        row[1]
        for row in exam_subject_rows
    ]

    exam_subject_ids = [
        row[0]
        for row in exam_subject_rows
    ]

    a, b = st.columns(2)

    exam_title = a.text_input(
        "Exam Title"
    )

    exam_date = b.date_input(
        "Exam Date"
    )

    exam_syllabus = st.text_area(
        "Syllabus"
    )

    exam_notes = st.text_area(
        "Notes"
    )

    exam_subject = st.selectbox(
        "Subject",
        exam_subject_names
    ) if exam_subject_names else ""

    exam_subject_id = (
        exam_subject_ids[
            exam_subject_names.index(
                exam_subject
            )
        ]
        if exam_subject_names and exam_subject
        else None
    )

    add_exam = st.button(
        "➕ Add Exam",
        use_container_width=True
    )

    valid_exam = (
        bool(exam_title.strip())
        and bool(exam_subject_names)
    )

    cursor.execute(
        "INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
        (
            exam_title.strip(),
            str(exam_date),
            exam_syllabus.strip(),
            exam_notes.strip(),
            exam_subject_id
        )
    ) if add_exam and valid_exam else None

    conn.commit() if add_exam and valid_exam else None

    st.success(
        "Exam added successfully!"
    ) if add_exam and valid_exam else None

    st.error(
        "Enter an exam title and make sure you have at least one subject."
    ) if add_exam and not valid_exam else None

    cursor.execute(
        "SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date"
    )

    exam_list = cursor.fetchall()

    st.markdown(
    """
    <div class="section-card">

    <div class="section-title">
    Exam Schedule
    </div>

    <div class="section-subtitle">
    Your saved exams in date order.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

    st.dataframe(
        exam_list,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "title": "Exam",
            "exam_date": "Exam Date",
            "syllabus": "Syllabus",
            "notes": "Notes",
            "name": "Subject"
        }
    )


# ==========================================
# STUDY PLANNER
# ==========================================

elif page == 5:

    st.header("✅ Study Planner")

    st.caption(
        "Turn your study goals into clear daily tasks."
    )

    cursor.execute(
        "SELECT id, name FROM subjects ORDER BY name"
    )

    task_subject_rows = cursor.fetchall()

    task_subject_names = [
        row[1]
        for row in task_subject_rows
    ]

    task_subject_ids = [
        row[0]
        for row in task_subject_rows
    ]

    a, b = st.columns(2)

    task_title = a.text_input(
        "Study Task"
    )

    task_date = b.date_input(
        "Study Date"
    )

    c1, c2 = st.columns(2)

    task_duration = c1.number_input(
        "Duration (minutes)",
        min_value=15,
        max_value=600,
        value=60,
        step=15
    )

    task_priority = c2.selectbox(
        "Priority",
        ["Low", "Medium", "High"]
    )

    task_subject = st.selectbox(
        "Subject",
        task_subject_names
    ) if task_subject_names else ""

    task_subject_id = (
        task_subject_ids[
            task_subject_names.index(
                task_subject
            )
        ]
        if task_subject_names and task_subject
        else None
    )

    add_task = st.button(
        "➕ Add Study Task",
        use_container_width=True
    )

    valid_task = (
        bool(task_title.strip())
        and bool(task_subject_names)
    )

    cursor.execute(
        "INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
        (
            task_title.strip(),
            str(task_date),
            int(task_duration),
            task_priority,
            0,
            task_subject_id
        )
    ) if add_task and valid_task else None

    conn.commit() if add_task and valid_task else None

    st.success(
        "Study task added successfully!"
    ) if add_task and valid_task else None

    st.error(
        "Enter a study task and make sure you have at least one subject."
    ) if add_task and not valid_task else None

    cursor.execute(
        "SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date"
    )

    task_list = cursor.fetchall()

    st.markdown(
    """
    <div class="section-card">

    <div class="section-title">
    Study Tasks
    </div>

    <div class="section-subtitle">
    Your daily study activities.
    </div>

    </div>
    """,
    unsafe_allow_html=True
    )

    st.dataframe(
        task_list,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "title": "Task",
            "task_date": "Date",
            "duration": "Minutes",
            "priority": "Priority",
            "completed": "Completed",
            "name": "Subject"
        }
    )

conn.close()
