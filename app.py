import streamlit as st
import sqlite3

st.set_page_config(
page_title="StudySphere",
page_icon="🎓",
layout="wide"
)

# ============================================================

# DATABASE

# ============================================================

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")

cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER)")

cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER, subject_id INTEGER)")

conn.commit()

# ============================================================

# GET SUBJECTS

# ============================================================

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

# ============================================================

# COUNTS

# ============================================================

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM tasks")
task_count = cursor.fetchone()[0]

# ============================================================

# SIDEBAR

# ============================================================

st.sidebar.title("🎓 StudySphere")
st.sidebar.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio(
"Navigation",
[
"🏠 Dashboard",
"📚 Subjects",
"📝 Assignments",
"📅 Exams",
"✅ Study Planner"
]
)

st.sidebar.divider()

st.sidebar.write("📊 Quick Stats")
st.sidebar.write("📚 Subjects:", subject_count)
st.sidebar.write("📝 Assignments:", assignment_count)
st.sidebar.write("📅 Exams:", exam_count)
st.sidebar.write("✅ Study Tasks:", task_count)

# ============================================================

# HEADER

# ============================================================

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")
st.divider()

# ============================================================

# DASHBOARD

# ============================================================

st.header("🏠 Dashboard") if page == "🏠 Dashboard" else None

st.write("Welcome to your StudySphere dashboard.") if page == "🏠 Dashboard" else None

col1, col2, col3, col4 = st.columns(4) if page == "🏠 Dashboard" else (None, None, None, None)

col1.metric("📚 Subjects", subject_count) if page == "🏠 Dashboard" else None
col2.metric("📝 Assignments", assignment_count) if page == "🏠 Dashboard" else None
col3.metric("📅 Exams", exam_count) if page == "🏠 Dashboard" else None
col4.metric("✅ Study Tasks", task_count) if page == "🏠 Dashboard" else None

st.subheader("📝 Upcoming Assignments") if page == "🏠 Dashboard" else None

cursor.execute(
"SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5"
) if page == "🏠 Dashboard" else None

dashboard_assignments = cursor.fetchall() if page == "🏠 Dashboard" else []

st.dataframe(
dashboard_assignments,
column_config={
"title": "Assignment",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status"
},
hide_index=True
) if page == "🏠 Dashboard" and dashboard_assignments else None

st.info("No assignments added yet.") if page == "🏠 Dashboard" and not dashboard_assignments else None

# ============================================================

# SUBJECTS

# ============================================================

st.header("📚 Subjects") if page == "📚 Subjects" else None

st.write("Add and manage your university subjects.") if page == "📚 Subjects" else None

subject_name_input = st.text_input("Subject Name") if page == "📚 Subjects" else ""
subject_code_input = st.text_input("Subject Code") if page == "📚 Subjects" else ""
subject_instructor_input = st.text_input("Instructor") if page == "📚 Subjects" else ""

add_subject = st.button("➕ Add Subject") if page == "📚 Subjects" else False

subject_insert = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(
subject_name_input.strip(),
subject_code_input.strip(),
subject_instructor_input.strip()
)
) if add_subject and subject_name_input.strip() else None

conn.commit() if add_subject and subject_name_input.strip() else None

st.success("Subject added successfully!") if add_subject and subject_name_input.strip() else None

st.warning("Please enter a subject name.") if add_subject and not subject_name_input.strip() else None

cursor.execute(
"SELECT id, name, code, instructor FROM subjects ORDER BY name"
) if page == "📚 Subjects" else None

subjects_table = cursor.fetchall() if page == "📚 Subjects" else []

st.subheader("Your Subjects") if page == "📚 Subjects" else None

st.dataframe(
subjects_table,
column_config={
"id": "ID",
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
hide_index=True
) if page == "📚 Subjects" and subjects_table else None

st.info("No subjects added yet.") if page == "📚 Subjects" and not subjects_table else None

# ============================================================

# ASSIGNMENTS

# ============================================================

st.header("📝 Assignments") if page == "📝 Assignments" else None

st.write("Track your assignments and deadlines.") if page == "📝 Assignments" else None

assignment_title_input = st.text_input("Assignment Title") if page == "📝 Assignments" else ""

assignment_description_input = st.text_area("Description") if page == "📝 Assignments" else ""

assignment_deadline_input = st.date_input("Deadline") if page == "📝 Assignments" else None

assignment_priority_input = st.selectbox(
"Priority",
["Low", "Medium", "High"]
) if page == "📝 Assignments" else ""

assignment_status_input = st.selectbox(
"Status",
["Pending", "In Progress", "Completed"]
) if page == "📝 Assignments" else ""

assignment_subject_name = st.selectbox(
"Subject",
subject_names
) if page == "📝 Assignments" and subject_names else ""

assignment_subject_id = subject_ids[subject_names.index(assignment_subject_name)] if page == "📝 Assignments" and subject_names else None

st.warning("Please add a subject first from the Subjects page.") if page == "📝 Assignments" and not subject_names else None

add_assignment = st.button("➕ Add Assignment") if page == "📝 Assignments" else False

assignment_insert = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
assignment_title_input.strip(),
assignment_description_input.strip(),
str(assignment_deadline_input),
assignment_priority_input,
assignment_status_input,
assignment_subject_id
)
) if add_assignment and assignment_title_input.strip() and assignment_subject_id else None

conn.commit() if add_assignment and assignment_title_input.strip() and assignment_subject_id else None

st.success("Assignment added successfully!") if add_assignment and assignment_title_input.strip() and assignment_subject_id else None

st.warning("Please enter an assignment title.") if add_assignment and not assignment_title_input.strip() else None

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline"
) if page == "📝 Assignments" else None

assignment_rows = cursor.fetchall() if page == "📝 Assignments" else []

st.subheader("Your Assignments") if page == "📝 Assignments" else None

st.dataframe(
assignment_rows,
column_config={
"id": "ID",
"title": "Assignment",
"description": "Description",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status",
"name": "Subject"
},
hide_index=True
) if page == "📝 Assignments" and assignment_rows else None

st.info("No assignments added yet.") if page == "📝 Assignments" and not assignment_rows else None

# ============================================================

# EXAMS

# ============================================================

st.header("📅 Exams") if page == "📅 Exams" else None

st.write("Manage your upcoming exams and syllabus.") if page == "📅 Exams" else None

exam_title_input = st.text_input("Exam Title") if page == "📅 Exams" else ""

exam_date_input = st.date_input("Exam Date") if page == "📅 Exams" else None

exam_syllabus_input = st.text_area("Syllabus") if page == "📅 Exams" else ""

exam_notes_input = st.text_area("Notes") if page == "📅 Exams" else ""

exam_subject_name = st.selectbox(
"Subject",
subject_names
) if page == "📅 Exams" and subject_names else ""

exam_subject_id = subject_ids[subject_names.index(exam_subject_name)] if page == "📅 Exams" and subject_names else None

st.warning("Please add a subject first from the Subjects page.") if page == "📅 Exams" and not subject_names else None

add_exam = st.button("➕ Add Exam") if page == "📅 Exams" else False

exam_insert = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(
exam_title_input.strip(),
str(exam_date_input),
exam_syllabus_input.strip(),
exam_notes_input.strip(),
exam_subject_id
)
) if add_exam and exam_title_input.strip() and exam_subject_id else None

conn.commit() if add_exam and exam_title_input.strip() and exam_subject_id else None

st.success("Exam added successfully!") if add_exam and exam_title_input.strip() and exam_subject_id else None

st.warning("Please enter an exam title.") if add_exam and not exam_title_input.strip() else None

cursor.execute(
"SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date"
) if page == "📅 Exams" else None

exam_rows = cursor.fetchall() if page == "📅 Exams" else []

st.subheader("Your Exams") if page == "📅 Exams" else None

st.dataframe(
exam_rows,
column_config={
"id": "ID",
"title": "Exam",
"exam_date": "Exam Date",
"syllabus": "Syllabus",
"notes": "Notes",
"name": "Subject"
},
hide_index=True
) if page == "📅 Exams" and exam_rows else None

st.info("No exams added yet.") if page == "📅 Exams" and not exam_rows else None

# ============================================================

# STUDY PLANNER

# ============================================================

st.header("✅ Study Planner") if page == "✅ Study Planner" else None

st.write("Create and manage your study sessions.") if page == "✅ Study Planner" else None

task_title_input = st.text_input("Study Task") if page == "✅ Study Planner" else ""

task_date_input = st.date_input("Study Date") if page == "✅ Study Planner" else None

task_duration_input = st.number_input(
"Duration in minutes",
min_value=5,
max_value=1440,
value=60,
step=5
) if page == "✅ Study Planner" else 60

task_priority_input = st.selectbox(
"Task Priority",
["Low", "Medium", "High"]
) if page == "✅ Study Planner" else ""

task_subject_name = st.selectbox(
"Subject",
subject_names
) if page == "✅ Study Planner" and subject_names else ""

task_subject_id = subject_ids[subject_names.index(task_subject_name)] if page == "✅ Study Planner" and subject_names else None

st.warning("Please add a subject first from the Subjects page.") if page == "✅ Study Planner" and not subject_names else None

add_task = st.button("➕ Add Study Task") if page == "✅ Study Planner" else False

task_insert = cursor.execute(
"INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
task_title_input.strip(),
str(task_date_input),
task_duration_input,
task_priority_input,
0,
task_subject_id
)
) if add_task and task_title_input.strip() and task_subject_id else None

conn.commit() if add_task and task_title_input.strip() and task_subject_id else None

st.success("Study task added successfully!") if add_task and task_title_input.strip() and task_subject_id else None

st.warning("Please enter a study task.") if add_task and not task_title_input.strip() else None

cursor.execute(
"SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date"
) if page == "✅ Study Planner" else None

task_rows = cursor.fetchall() if page == "✅ Study Planner" else []

st.subheader("Your Study Tasks") if page == "✅ Study Planner" else None

st.dataframe(
task_rows,
column_config={
"id": "ID",
"title": "Task",
"task_date": "Date",
"duration": "Minutes",
"priority": "Priority",
"completed": "Completed",
"name": "Subject"
},
hide_index=True
) if page == "✅ Study Planner" and task_rows else None

st.info("No study tasks added yet.") if page == "✅ Study Planner" and not task_rows else None

# ============================================================

# CLOSE DATABASE

# ============================================================

conn.close()
