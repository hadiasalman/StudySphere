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

dark_mode = st.sidebar.toggle("Dark mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

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
.block-container {{ max-width:1450px; padding-top:1.4rem; padding-bottom:3rem; }}

h1,h2,h3,h4,h5,h6,p,label,.stMarkdown,.stCaption {{
    color:{text} !important;
}}

[data-testid="stSidebar"] {{
    background:{sidebar_bg};
    border-right:1px solid {border};
}}
[data-testid="stSidebar"] * {{ color:{text} !important; }}

.brand {{
    padding:8px 4px 22px;
}}
.logo-row {{
    display:flex;
    align-items:center;
    gap:10px;
}}
.logo {{
    width:42px;
    height:42px;
    border-radius:13px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:linear-gradient(135deg,#14B8A6,#0F766E);
    color:white !important;
    font-size:22px;
    box-shadow:0 8px 20px rgba(20,184,166,.25);
}}
.brand-name {{
    font-size:23px;
    font-weight:850;
    letter-spacing:-.7px;
}}
.brand-tag {{
    margin:7px 0 0 52px;
    color:{muted} !important;
    font-size:11px;
}}

.sidebar-label {{
    color:{muted} !important;
    text-transform:uppercase;
    letter-spacing:1.2px;
    font-size:10px;
    font-weight:800;
    margin:15px 0 7px;
}}

.hero {{
    position:relative;
    overflow:hidden;
    padding:34px 36px;
    border-radius:25px;
    margin-bottom:22px;
    background:
        radial-gradient(circle at 85% 15%, rgba(45,212,191,.30), transparent 28%),
        radial-gradient(circle at 10% 100%, rgba(59,130,246,.20), transparent 30%),
        linear-gradient(135deg,#0F766E,#115E59 52%,#0F172A);
    box-shadow:0 18px 45px rgba(15,118,110,.20);
}}
.hero-kicker {{
    color:#99F6E4 !important;
    font-size:12px;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:1.5px;
}}
.hero-title {{
    color:white !important;
    font-size:35px;
    line-height:1.1;
    font-weight:850;
    letter-spacing:-1.2px;
    margin:8px 0;
}}
.hero-text {{
    color:rgba(255,255,255,.82) !important;
    font-size:14px;
    max-width:680px;
    line-height:1.6;
}}
.hero-pill {{
    display:inline-block;
    margin-top:18px;
    padding:7px 12px;
    border-radius:999px;
    background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.18);
    color:white !important;
    font-size:11px;
}}

.stat-card {{
    background:{card};
    border:1px solid {border};
    border-radius:19px;
    padding:20px;
    min-height:130px;
    box-shadow:{shadow};
    transition:transform .2s ease, border-color .2s ease;
}}
.stat-card:hover {{
    transform:translateY(-3px);
    border-color:#5EEAD4;
}}
.stat-top {{
    display:flex;
    justify-content:space-between;
    align-items:center;
}}
.stat-icon {{
    width:39px;
    height:39px;
    border-radius:12px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#CCFBF1;
    font-size:19px;
}}
.dark .stat-icon {{ background:#134E4A; }}
.stat-number {{
    font-size:30px;
    font-weight:850;
    color:{text} !important;
    margin-top:13px;
}}
.stat-label {{
    font-size:12px;
    color:{muted} !important;
    margin-top:2px;
}}

.panel {{
    background:{card};
    border:1px solid {border};
    border-radius:20px;
    padding:22px;
    margin-top:22px;
    box-shadow:{shadow};
}}
.panel-head {{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:15px;
}}
.panel-title {{
    color:{text} !important;
    font-size:18px;
    font-weight:800;
}}
.panel-sub {{
    color:{muted} !important;
    font-size:12px;
    margin-top:4px;
}}

.ai-panel {{
    border-radius:22px;
    padding:25px;
    margin-top:22px;
    background:
        radial-gradient(circle at 90% 20%,rgba(45,212,191,.18),transparent 30%),
        linear-gradient(135deg,#102A43,#123B4A);
    border:1px solid #1E5963;
    box-shadow:0 14px 35px rgba(2,132,140,.12);
}}
.ai-badge {{
    display:inline-block;
    padding:5px 9px;
    border-radius:999px;
    background:rgba(45,212,191,.12);
    color:#5EEAD4 !important;
    font-size:10px;
    font-weight:800;
    letter-spacing:.8px;
    text-transform:uppercase;
}}
.ai-title {{
    color:white !important;
    font-size:22px;
    font-weight:850;
    margin-top:10px;
}}
.ai-text {{
    color:#CBD5E1 !important;
    font-size:13px;
    line-height:1.6;
    max-width:850px;
}}

.page-banner {{
    padding:22px 24px;
    border-radius:19px;
    background:{card};
    border:1px solid {border};
    box-shadow:{shadow};
    margin-bottom:20px;
}}
.page-title {{
    font-size:27px;
    font-weight:850;
    letter-spacing:-.7px;
}}
.page-sub {{
    color:{muted} !important;
    font-size:13px;
    margin-top:4px;
}}

div.stButton > button {{
    background:#14B8A6 !important;
    color:white !important;
    border:1px solid #0F766E !important;
    border-radius:11px !important;
    min-height:42px;
    font-weight:750;
    box-shadow:0 6px 14px rgba(20,184,166,.14);
    transition:.2s ease;
}}
div.stButton > button:hover {{
    background:#0F766E !important;
    border-color:#0F766E !important;
    transform:translateY(-1px);
}}
div.stButton > button p, div.stButton > button span {{
    color:white !important;
}}

input, textarea {{
    background:{card2} !important;
    color:{text} !important;
    caret-color:{text} !important;
}}
input::placeholder, textarea::placeholder {{
    color:{muted} !important;
}}
div[data-baseweb="select"] > div {{
    background:{card2} !important;
    color:{text} !important;
    border-color:{border} !important;
}}
div[data-baseweb="select"] span {{ color:{text} !important; }}
div[data-baseweb="popover"], ul {{ background:{card} !important; }}
li {{ color:{text} !important; }}

[data-testid="stDataFrame"] {{
    border:1px solid {border};
    border-radius:14px;
    overflow:hidden;
}}
[data-testid="stDataFrame"] * {{ color:{text} !important; }}

[data-testid="stMetric"] {{
    background:{card};
    border:1px solid {border};
    border-radius:15px;
    padding:10px;
}}

hr {{ border-color:{border}; }}

@media (max-width: 900px) {{
    .hero {{ padding:25px; }}
    .hero-title {{ font-size:28px; }}
    .panel {{ padding:17px; }}
}}
</style>
""",
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
<div class="brand">
<div class="logo-row">
<div class="logo">🎓</div>
<div class="brand-name">StudySphere</div>
</div>
<div class="brand-tag">Learn smarter. Plan better. Achieve more.</div>
</div>
""",
    unsafe_allow_html=True
)

st.sidebar.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    [1, 2, 3, 4, 5],
    format_func=lambda x: {
        1: "🏠  Dashboard",
        2: "📚  Subjects",
        3: "📝  Assignments",
        4: "📅  Exams",
        5: "✅  Study Planner"
    }[x],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-label">Intelligence</div>', unsafe_allow_html=True)
st.sidebar.markdown("### 🤖 AI Agent")
st.sidebar.caption("Your personal academic AI agent is coming next.")

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0")
pending_task_count = cursor.fetchone()[0]

if page == 1:
    st.markdown(
        """
<div class="hero">
<div class="hero-kicker">Student command center</div>
<div class="hero-title">Welcome back to StudySphere 👋</div>
<div class="hero-text">
Everything you need to organize your academic life — subjects, deadlines,
exams and daily study tasks — in one focused workspace.
</div>
<div class="hero-pill">✦ Stay organized • Study consistently • Make progress</div>
</div>
""",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">📚</div></div><div class="stat-number">{subject_count}</div><div class="stat-label">Total Subjects</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">📝</div></div><div class="stat-number">{assignment_count}</div><div class="stat-label">Assignments</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">🎯</div></div><div class="stat-number">{exam_count}</div><div class="stat-label">Upcoming Exams</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-top"><div class="stat-icon">✓</div></div><div class="stat-number">{pending_task_count}</div><div class="stat-label">Pending Tasks</div></div>', unsafe_allow_html=True)

    cursor.execute("SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5")
    upcoming_assignments = cursor.fetchall()

    cursor.execute("SELECT title, exam_date FROM exams ORDER BY exam_date LIMIT 5")
    upcoming_exams = cursor.fetchall()

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="panel"><div class="panel-head"><div><div class="panel-title">📝 Upcoming Assignments</div><div class="panel-sub">Stay ahead of your deadlines.</div></div></div></div>', unsafe_allow_html=True)
        st.dataframe(upcoming_assignments, use_container_width=True, hide_index=True, column_config={"title":"Assignment","deadline":"Deadline","priority":"Priority","status":"Status"})

    with right:
        st.markdown('<div class="panel"><div class="panel-head"><div><div class="panel-title">📅 Upcoming Exams</div><div class="panel-sub">Keep your exam schedule under control.</div></div></div></div>', unsafe_allow_html=True)
        st.dataframe(upcoming_exams, use_container_width=True, hide_index=True, column_config={"title":"Exam","exam_date":"Exam Date"})

    st.markdown(
        """
<div class="ai-panel">
<div class="ai-badge">AI • Coming next</div>
<div class="ai-title">🤖 StudySphere AI Agent</div>
<div class="ai-text">
Your future academic agent will connect your subjects, tasks and exams to help
you understand what needs attention and organize your study time more intelligently.
</div>
</div>
""",
        unsafe_allow_html=True
    )

elif page == 2:
    st.markdown('<div class="page-banner"><div class="page-title">📚 Subjects</div><div class="page-sub">Build your academic workspace by adding your university subjects.</div></div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    subject_name = a.text_input("Subject Name")
    subject_code = b.text_input("Subject Code")
    subject_instructor = c.text_input("Instructor")

    add_subject = st.button("➕ Add Subject", use_container_width=True)
    valid_subject = bool(subject_name.strip())

    if add_subject and valid_subject:
        cursor.execute("INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)", (subject_name.strip(), subject_code.strip(), subject_instructor.strip()))
        conn.commit()
        st.success("Subject added successfully.")

    if add_subject and not valid_subject:
        st.error("Please enter a subject name.")

    cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
    subject_list = cursor.fetchall()

    st.markdown('<div class="panel"><div class="panel-title">Your Subjects</div><div class="panel-sub">All subjects currently saved in StudySphere.</div></div>', unsafe_allow_html=True)
    st.dataframe(subject_list, use_container_width=True, hide_index=True, column_config={"id":"ID","name":"Subject","code":"Code","instructor":"Instructor"})

elif page == 3:
    st.markdown('<div class="page-banner"><div class="page-title">📝 Assignments</div><div class="page-sub">Track deadlines, priorities and completion status in one place.</div></div>', unsafe_allow_html=True)

    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    assignment_subject_rows = cursor.fetchall()
    assignment_subject_names = [row[1] for row in assignment_subject_rows]
    assignment_subject_ids = [row[0] for row in assignment_subject_rows]

    a, b = st.columns(2)
    assignment_title = a.text_input("Assignment Title")
    assignment_deadline = b.date_input("Deadline")
    assignment_description = st.text_area("Description")

    c1, c2 = st.columns(2)
    assignment_priority = c1.selectbox("Priority", ["Low", "Medium", "High"])
    assignment_status = c2.selectbox("Status", ["Pending", "In Progress", "Completed"])

    assignment_subject = st.selectbox("Subject", assignment_subject_names) if assignment_subject_names else ""
    assignment_subject_id = assignment_subject_ids[assignment_subject_names.index(assignment_subject)] if assignment_subject_names and assignment_subject else None

    add_assignment = st.button("➕ Add Assignment", use_container_width=True)
    valid_assignment = bool(assignment_title.strip()) and bool(assignment_subject_names)

    if add_assignment and valid_assignment:
        cursor.execute("INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)", (assignment_title.strip(), assignment_description.strip(), str(assignment_deadline), assignment_priority, assignment_status, assignment_subject_id))
        conn.commit()
        st.success("Assignment added successfully.")

    if add_assignment and not valid_assignment:
        st.error("Enter an assignment title and make sure you have at least one subject.")

    cursor.execute("SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline")
    assignment_list = cursor.fetchall()

    st.markdown('<div class="panel"><div class="panel-title">Assignment List</div><div class="panel-sub">Your saved assignments and their current status.</div></div>', unsafe_allow_html=True)
    st.dataframe(assignment_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Assignment","description":"Description","deadline":"Deadline","priority":"Priority","status":"Status","name":"Subject"})

elif page == 4:
    st.markdown('<div class="page-banner"><div class="page-title">📅 Exams</div><div class="page-sub">Keep your exam dates, syllabus and notes organized.</div></div>', unsafe_allow_html=True)

    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    exam_subject_rows = cursor.fetchall()
    exam_subject_names = [row[1] for row in exam_subject_rows]
    exam_subject_ids = [row[0] for row in exam_subject_rows]

    a, b = st.columns(2)
    exam_title = a.text_input("Exam Title")
    exam_date = b.date_input("Exam Date")
    exam_syllabus = st.text_area("Syllabus")
    exam_notes = st.text_area("Notes")

    exam_subject = st.selectbox("Subject", exam_subject_names) if exam_subject_names else ""
    exam_subject_id = exam_subject_ids[exam_subject_names.index(exam_subject)] if exam_subject_names and exam_subject else None

    add_exam = st.button("➕ Add Exam", use_container_width=True)
    valid_exam = bool(exam_title.strip()) and bool(exam_subject_names)

    if add_exam and valid_exam:
        cursor.execute("INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)", (exam_title.strip(), str(exam_date), exam_syllabus.strip(), exam_notes.strip(), exam_subject_id))
        conn.commit()
        st.success("Exam added successfully.")

    if add_exam and not valid_exam:
        st.error("Enter an exam title and make sure you have at least one subject.")

    cursor.execute("SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date")
    exam_list = cursor.fetchall()

    st.markdown('<div class="panel"><div class="panel-title">Exam Schedule</div><div class="panel-sub">Your saved exams in date order.</div></div>', unsafe_allow_html=True)
    st.dataframe(exam_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Exam","exam_date":"Exam Date","syllabus":"Syllabus","notes":"Notes","name":"Subject"})

elif page == 5:
    st.markdown('<div class="page-banner"><div class="page-title">✅ Study Planner</div><div class="page-sub">Turn your study goals into clear, manageable daily tasks.</div></div>', unsafe_allow_html=True)

    cursor.execute("SELECT id, name FROM subjects ORDER BY name")
    task_subject_rows = cursor.fetchall()
    task_subject_names = [row[1] for row in task_subject_rows]
    task_subject_ids = [row[0] for row in task_subject_rows]

    a, b = st.columns(2)
    task_title = a.text_input("Study Task")
    task_date = b.date_input("Study Date")

    c1, c2 = st.columns(2)
    task_duration = c1.number_input("Duration (minutes)", min_value=15, max_value=600, value=60, step=15)
    task_priority = c2.selectbox("Priority", ["Low", "Medium", "High"])

    task_subject = st.selectbox("Subject", task_subject_names) if task_subject_names else ""
    task_subject_id = task_subject_ids[task_subject_names.index(task_subject)] if task_subject_names and task_subject else None

    add_task = st.button("➕ Add Study Task", use_container_width=True)
    valid_task = bool(task_title.strip()) and bool(task_subject_names)

    if add_task and valid_task:
        cursor.execute("INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)", (task_title.strip(), str(task_date), int(task_duration), task_priority, 0, task_subject_id))
        conn.commit()
        st.success("Study task added successfully.")

    if add_task and not valid_task:
        st.error("Enter a study task and make sure you have at least one subject.")

    cursor.execute("SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date")
    task_list = cursor.fetchall()

    st.markdown('<div class="panel"><div class="panel-title">Study Tasks</div><div class="panel-sub">Your daily study activities.</div></div>', unsafe_allow_html=True)
    st.dataframe(task_list, use_container_width=True, hide_index=True, column_config={"id":"ID","title":"Task","task_date":"Date","duration":"Minutes","priority":"Priority","completed":"Completed","name":"Subject"})

conn.close()
