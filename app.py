import streamlit as st
import sqlite3

st.set_page_config(
page_title="StudySphere",
page_icon="🎓",
layout="wide"
)

st.markdown("""

<style>
body {
    font-family: Arial, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: #ffffff;
}
[data-testid="stSidebar"] {
    background: #f5f7fb;
}
h1, h2, h3, h4, h5, h6, p, label, div, span {
    color: #000000;
}
</style>

""", unsafe_allow_html=True)

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
code TEXT,
instructor TEXT
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
subject_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS exams (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
exam_date TEXT,
syllabus TEXT,
notes TEXT,
subject_id INTEGER
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
subject_id INTEGER
)
""")

conn.commit()

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

subject_count = len(subject_rows)

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0")
task_count = cursor.fetchone()[0]

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
st.sidebar.info("StudySphere — AI Student Companion")

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

st.header("🏠 Dashboard") if page == "🏠 Dashboard" else None

dashboard_col1, dashboard_col2, dashboard_col3, dashboard_col4 = st.columns(4) if page == "🏠 Dashboard" else (None, None, None, None)

dashboard_col1.metric("📚 Subjects", subject_count) if page == "🏠 Dashboard" else None
dashboard_col2.metric("📝 Assignments", assignment_count) if page == "🏠 Dashboard" else None
dashboard_col3.metric("📅 Exams", exam_count) if page == "🏠 Dashboard" else None
dashboard_col4.metric("✅ Pending Tasks", task_count) if page == "🏠 Dashboard" else None

st.divider() if page == "🏠 Dashboard" else None

st.subheader("Welcome to StudySphere 👋") if page == "🏠 Dashboard" else None

st.write(
"Your personal student companion for managing subjects, assignments, exams and study tasks."
) if page == "🏠 Dashboard" else None

st.subheader("Quick Overview") if page == "🏠 Dashboard" else None

cursor.execute("""
SELECT name, code, instructor
FROM subjects
ORDER BY name
""")

dashboard_subjects = cursor.fetchall()

st.dataframe(
dashboard_subjects,
column_config={
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
use_container_width=True,
hide_index=True
) if page == "🏠 Dashboard" and dashboard_subjects else None

st.info("No subjects added yet. Go to 📚 Subjects to add your first subject.") if page == "🏠 Dashboard" and not dashboard_subjects else None

st.header("📚 Subjects") if page == "📚 Subjects" else None

st.subheader("Add New Subject") if page == "📚 Subjects" else None

subject_name = st.text_input("Subject Name", key="subject_name") if page == "📚 Subjects" else ""
subject_code = st.text_input("Subject Code", key="subject_code") if page == "📚 Subjects" else ""
subject_instructor = st.text_input("Instructor", key="subject_instructor") if page == "📚 Subjects" else ""

add_subject = st.button("➕ Add Subject", key="add_subject") if page == "📚 Subjects" else False

subject_valid = bool(subject_name.strip())

save_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name.strip(), subject_code.strip(), subject_instructor.strip())
) if page == "📚 Subjects" and add_subject and subject_valid else None

conn.commit() if page == "📚 Subjects" and add_subject and subject_valid else None

st.success("Subject added successfully! Please refresh the page to update the dropdown lists.") if page == "📚 Subjects" and add_subject and subject_valid else None

st.error("Please enter a subject name.") if page == "📚 Subjects" and add_subject and not subject_valid else None

st.subheader("Your Subjects") if page == "📚 Subjects" else None

cursor.execute("""
SELECT id, name, code, instructor
FROM subjects
ORDER BY name
""")

subject_list = cursor.fetchall()

st.dataframe(
subject_list,
column_config={
"id": "ID",
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
use_container_width=True,
hide_index=True
) if page == "📚 Subjects" and subject_list else None

st.info("No subjects found.") if page == "📚 Subjects" and not subject_list else None

st.header("📝 Assignments") if page == "📝 Assignments" else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
assignment_subject_rows = cursor.fetchall()

assignment_subject_names = [row[1] for row in assignment_subject_rows]
assignment_subject_ids = [row[0] for row in assignment_subject_rows]

st.subheader("Add Assignment") if page == "📝 Assignments" else None

assignment_title = st.text_input("Assignment Title", key="assignment_title") if page == "📝 Assignments" else ""
assignment_description = st.text_area("Description", key="assignment_description") if page == "📝 Assignments" else ""

assignment_deadline = st.date_input(
"Deadline",
key="assignment_deadline"
) if page == "📝 Assignments" else None

assignment_priority = st.selectbox(
"Priority",
["Low", "Medium", "High"],
key="assignment_priority"
) if page == "📝 Assignments" else "Medium"

assignment_status = st.selectbox(
"Status",
["Pending", "In Progress", "Completed"],
key="assignment_status"
) if page == "📝 Assignments" else "Pending"

assignment_subject_name = st.selectbox(
"Subject",
assignment_subject_names,
key="assignment_subject"
) if page == "📝 Assignments" and assignment_subject_names else ""

assignment_subject_id = assignment_subject_ids[assignment_subject_names.index(assignment_subject_name)] if page == "📝 Assignments" and assignment_subject_names and assignment_subject_name else None

add_assignment = st.button("➕ Add Assignment", key="add_assignment") if page == "📝 Assignments" else False

assignment_valid = bool(assignment_title.strip()) and bool(assignment_subject_names)

save_assignment = cursor.execute(
"""
INSERT INTO assignments
(title, description, deadline, priority, status, subject_id)
VALUES (?, ?, ?, ?, ?, ?)
""",
(
assignment_title.strip(),
assignment_description.strip(),
str(assignment_deadline),
assignment_priority,
assignment_status,
assignment_subject_id
)
) if page == "📝 Assignments" and add_assignment and assignment_valid else None

conn.commit() if page == "📝 Assignments" and add_assignment and assignment_valid else None

st.success("Assignment added successfully!") if page == "📝 Assignments" and add_assignment and assignment_valid else None

st.error("Enter an assignment title and make sure at least one subject exists.") if page == "📝 Assignments" and add_assignment and not assignment_valid else None

st.subheader("Your Assignments") if page == "📝 Assignments" else None

cursor.execute("""
SELECT
assignments.id,
assignments.title,
assignments.description,
assignments.deadline,
assignments.priority,
assignments.status,
subjects.name
FROM assignments
LEFT JOIN subjects
ON assignments.subject_id = subjects.id
ORDER BY assignments.deadline
""")

assignment_list = cursor.fetchall()

st.dataframe(
assignment_list,
column_config={
"id": "ID",
"title": "Title",
"description": "Description",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status",
"name": "Subject"
},
use_container_width=True,
hide_index=True
) if page == "📝 Assignments" and assignment_list else None

st.info("No assignments found.") if page == "📝 Assignments" and not assignment_list else None

st.header("📅 Exams") if page == "📅 Exams" else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
exam_subject_rows = cursor.fetchall()

exam_subject_names = [row[1] for row in exam_subject_rows]
exam_subject_ids = [row[0] for row in exam_subject_rows]

st.subheader("Add Exam") if page == "📅 Exams" else None

exam_title = st.text_input("Exam Title", key="exam_title") if page == "📅 Exams" else ""

exam_date = st.date_input(
"Exam Date",
key="exam_date"
) if page == "📅 Exams" else None

exam_syllabus = st.text_area(
"Syllabus",
key="exam_syllabus"
) if page == "📅 Exams" else ""

exam_notes = st.text_area(
"Notes",
key="exam_notes"
) if page == "📅 Exams" else ""

exam_subject_name = st.selectbox(
"Subject",
exam_subject_names,
key="exam_subject"
) if page == "📅 Exams" and exam_subject_names else ""

exam_subject_id = exam_subject_ids[exam_subject_names.index(exam_subject_name)] if page == "📅 Exams" and exam_subject_names and exam_subject_name else None

add_exam = st.button("➕ Add Exam", key="add_exam") if page == "📅 Exams" else False

exam_valid = bool(exam_title.strip()) and bool(exam_subject_names)

save_exam = cursor.execute(
"""
INSERT INTO exams
(title, exam_date, syllabus, notes, subject_id)
VALUES (?, ?, ?, ?, ?)
""",
(
exam_title.strip(),
str(exam_date),
exam_syllabus.strip(),
exam_notes.strip(),
exam_subject_id
)
) if page == "📅 Exams" and add_exam and exam_valid else None

conn.commit() if page == "📅 Exams" and add_exam and exam_valid else None

st.success("Exam added successfully!") if page == "📅 Exams" and add_exam and exam_valid else None

st.error("Enter an exam title and make sure at least one subject exists.") if page == "📅 Exams" and add_exam and not exam_valid else None

st.subheader("Your Exams") if page == "📅 Exams" else None

cursor.execute("""
SELECT
exams.id,
exams.title,
exams.exam_date,
exams.syllabus,
exams.notes,
subjects.name
FROM exams
LEFT JOIN subjects
ON exams.subject_id = subjects.id
ORDER BY exams.exam_date
""")

exam_list = cursor.fetchall()

st.dataframe(
exam_list,
column_config={
"id": "ID",
"title": "Exam",
"exam_date": "Date",
"syllabus": "Syllabus",
"notes": "Notes",
"name": "Subject"
},
use_container_width=True,
hide_index=True
) if page == "📅 Exams" and exam_list else None

st.info("No exams found.") if page == "📅 Exams" and not exam_list else None

st.header("✅ Study Planner") if page == "✅ Study Planner" else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
task_subject_rows = cursor.fetchall()

task_subject_names = [row[1] for row in task_subject_rows]
task_subject_ids = [row[0] for row in task_subject_rows]

st.subheader("Create Study Task") if page == "✅ Study Planner" else None

task_title = st.text_input("Task Title", key="task_title") if page == "✅ Study Planner" else ""

task_date = st.date_input(
"Study Date",
key="task_date"
) if page == "✅ Study Planner" else None

task_duration = st.number_input(
"Duration in minutes",
min_value=15,
max_value=600,
value=60,
step=15,
key="task_duration"
) if page == "✅ Study Planner" else 60

task_priority = st.selectbox(
"Priority",
["Low", "Medium", "High"],
key="task_priority"
) if page == "✅ Study Planner" else "Medium"

task_subject_name = st.selectbox(
"Subject",
task_subject_names,
key="task_subject"
) if page == "✅ Study Planner" and task_subject_names else ""

task_subject_id = task_subject_ids[task_subject_names.index(task_subject_name)] if page == "✅ Study Planner" and task_subject_names and task_subject_name else None

add_task = st.button("➕ Add Study Task", key="add_task") if page == "✅ Study Planner" else False

task_valid = bool(task_title.strip()) and bool(task_subject_names)

save_task = cursor.execute(
"""
INSERT INTO tasks
(title, task_date, duration, priority, completed, subject_id)
VALUES (?, ?, ?, ?, ?, ?)
""",
(
task_title.strip(),
str(task_date),
int(task_duration),
task_priority,
0,
task_subject_id
)
) if page == "✅ Study Planner" and add_task and task_valid else None

conn.commit() if page == "✅ Study Planner" and add_task and task_valid else None

st.success("Study task added successfully!") if page == "✅ Study Planner" and add_task and task_valid else None

st.error("Enter a task title and make sure at least one subject exists.") if page == "✅ Study Planner" and add_task and not task_valid else None

st.subheader("Your Study Tasks") if page == "✅ Study Planner" else None

cursor.execute("""
SELECT
tasks.id,
tasks.title,
tasks.task_date,
tasks.duration,
tasks.priority,
tasks.completed,
subjects.name
FROM tasks
LEFT JOIN subjects
ON tasks.subject_id = subjects.id
ORDER BY tasks.task_date
""")

task_list = cursor.fetchall()

st.dataframe(
task_list,
column_config={
"id": "ID",
"title": "Task",
"task_date": "Date",
"duration": "Minutes",
"priority": "Priority",
"completed": "Completed",
"name": "Subject"
},
use_container_width=True,
hide_index=True
) if page == "✅ Study Planner" and task_list else None

st.info("No study tasks found.") if page == "✅ Study Planner" and not task_list else None

conn.close()
