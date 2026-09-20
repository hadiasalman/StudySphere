import streamlit as st
import sqlite3
from datetime import date

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER, subject_id INTEGER)")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM tasks")
task_count = cursor.fetchone()[0]

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

st.sidebar.title("🎓 StudySphere")
st.sidebar.write("Learn smarter. Plan better. Achieve more.")

st.sidebar.divider()

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

st.sidebar.divider()

st.sidebar.caption("StudySphere • AI Student Companion")

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("🏠 Dashboard")

dashboard_selected = page == "🏠 Dashboard"

st.write("Welcome to your personal student dashboard.")

st.metric("📚 Subjects", subject_count)
st.metric("📝 Assignments", assignment_count)
st.metric("📅 Exams", exam_count)
st.metric("✅ Study Tasks", task_count)

st.divider()

st.header("📝 Upcoming Assignments")

cursor.execute("SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5")
upcoming_assignments = cursor.fetchall()

st.dataframe(
upcoming_assignments,
column_config={
"title": "Assignment",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status"
},
hide_index=True
)

st.divider()

st.header("📚 Subjects")

cursor.execute("SELECT name, code, instructor FROM subjects ORDER BY id DESC")
all_subjects = cursor.fetchall()

st.dataframe(
all_subjects,
column_config={
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
hide_index=True
)

st.divider()

st.header("📝 Assignments")

assignment_title = st.text_input("Assignment Title")
assignment_description = st.text_area("Assignment Description")
assignment_deadline = st.date_input("Assignment Deadline", value=date.today())
assignment_priority = st.selectbox("Assignment Priority", ["Low", "Medium", "High"])

assignment_subject = st.selectbox(
"Assignment Subject",
["No Subject"] + subject_names
)

assignment_subject_id = subject_ids[subject_names.index(assignment_subject)] if assignment_subject in subject_names else None

add_assignment = st.button("➕ Add Assignment")

save_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(assignment_title, assignment_description, str(assignment_deadline), assignment_priority, "Pending", assignment_subject_id)
) if add_assignment and assignment_title.strip() else None

conn.commit()

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline"
)

assignment_rows = cursor.fetchall()

st.dataframe(
assignment_rows,
column_config={
"id": "ID",
"title": "Assignment",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status",
"name": "Subject"
},
hide_index=True
)

st.divider()

st.header("📅 Exams")

exam_title = st.text_input("Exam Title")
exam_date = st.date_input("Exam Date", value=date.today())
exam_syllabus = st.text_area("Exam Syllabus")
exam_notes = st.text_area("Exam Notes")

exam_subject = st.selectbox(
"Exam Subject",
["No Subject"] + subject_names
)

exam_subject_id = subject_ids[subject_names.index(exam_subject)] if exam_subject in subject_names else None

add_exam = st.button("➕ Add Exam")

save_exam = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(exam_title, str(exam_date), exam_syllabus, exam_notes, exam_subject_id)
) if add_exam and exam_title.strip() else None

conn.commit()

cursor.execute(
"SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date"
)

exam_rows = cursor.fetchall()

st.dataframe(
exam_rows,
column_config={
"id": "ID",
"title": "Exam",
"exam_date": "Date",
"syllabus": "Syllabus",
"notes": "Notes",
"name": "Subject"
},
hide_index=True
)

st.divider()

st.header("✅ Study Planner")

task_title = st.text_input("Task Title")
task_date = st.date_input("Task Date", value=date.today())
task_duration = st.number_input("Duration (minutes)", min_value=15, max_value=600, value=60, step=15)
task_priority = st.selectbox("Task Priority", ["Low", "Medium", "High"])

task_subject = st.selectbox(
"Task Subject",
["No Subject"] + subject_names
)

task_subject_id = subject_ids[subject_names.index(task_subject)] if task_subject in subject_names else None

add_task = st.button("➕ Add Study Task")

save_task = cursor.execute(
"INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(task_title, str(task_date), task_duration, task_priority, 0, task_subject_id)
) if add_task and task_title.strip() else None

conn.commit()

cursor.execute(
"SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date"
)

task_rows = cursor.fetchall()

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
)

st.divider()

st.success("🎉 StudySphere navigation is ready!")

conn.close()
