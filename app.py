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
st.sidebar.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio(
"Navigation",
["🏠 Dashboard", "📚 Subjects", "📝 Assignments", "📅 Exams", "✅ Study Planner"]
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

st.divider()

dashboard = page == "🏠 Dashboard"

st.header("🏠 Dashboard")
st.write("Welcome to your personal student dashboard.")

st.metric("📚 Subjects", subject_count)
st.metric("📝 Assignments", assignment_count)
st.metric("📅 Exams", exam_count)
st.metric("✅ Study Tasks", task_count)

st.divider()

cursor.execute("SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5")
upcoming_assignments = cursor.fetchall()

st.subheader("📝 Upcoming Assignments")

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

subjects_page = page == "📚 Subjects"

st.header("📚 Subjects")
st.write("Manage your university subjects here.")

new_subject_name = st.text_input("Subject Name", key="new_subject_name")
new_subject_code = st.text_input("Subject Code", key="new_subject_code")
new_subject_instructor = st.text_input("Instructor", key="new_subject_instructor")

add_subject = st.button("➕ Add Subject", key="add_subject")

save_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(new_subject_name, new_subject_code, new_subject_instructor)
) if add_subject and new_subject_name.strip() else None

conn.commit()

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

assignments_page = page == "📝 Assignments"

st.header("📝 Assignments")
st.write("Track your assignments and deadlines.")

new_assignment_title = st.text_input("Assignment Title", key="new_assignment_title")
new_assignment_description = st.text_area("Description", key="new_assignment_description")
new_assignment_deadline = st.date_input("Deadline", value=date.today(), key="new_assignment_deadline")
new_assignment_priority = st.selectbox("Priority", ["Low", "Medium", "High"], key="new_assignment_priority")

new_assignment_subject = st.selectbox(
"Subject",
["No Subject"] + subject_names,
key="new_assignment_subject"
)

new_assignment_subject_id = subject_ids[subject_names.index(new_assignment_subject)] if new_assignment_subject in subject_names else None

add_assignment = st.button("➕ Add Assignment", key="add_assignment")

save_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
new_assignment_title,
new_assignment_description,
str(new_assignment_deadline),
new_assignment_priority,
"Pending",
new_assignment_subject_id
)
) if add_assignment and new_assignment_title.strip() else None

conn.commit()

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline"
)

all_assignments = cursor.fetchall()

st.dataframe(
all_assignments,
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

exams_page = page == "📅 Exams"

st.header("📅 Exams")
st.write("Organize your upcoming exams.")

new_exam_title = st.text_input("Exam Title", key="new_exam_title")
new_exam_date = st.date_input("Exam Date", value=date.today(), key="new_exam_date")
new_exam_syllabus = st.text_area("Syllabus", key="new_exam_syllabus")
new_exam_notes = st.text_area("Notes", key="new_exam_notes")

new_exam_subject = st.selectbox(
"Subject",
["No Subject"] + subject_names,
key="new_exam_subject"
)

new_exam_subject_id = subject_ids[subject_names.index(new_exam_subject)] if new_exam_subject in subject_names else None

add_exam = st.button("➕ Add Exam", key="add_exam")

save_exam = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(
new_exam_title,
str(new_exam_date),
new_exam_syllabus,
new_exam_notes,
new_exam_subject_id
)
) if add_exam and new_exam_title.strip() else None

conn.commit()

cursor.execute(
"SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date"
)

all_exams = cursor.fetchall()

st.dataframe(
all_exams,
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

planner_page = page == "✅ Study Planner"

st.header("✅ Study Planner")
st.write("Plan your daily study sessions.")

new_task_title = st.text_input("Task Title", key="new_task_title")
new_task_date = st.date_input("Task Date", value=date.today(), key="new_task_date")
new_task_duration = st.number_input("Duration (minutes)", min_value=15, max_value=600, value=60, step=15, key="new_task_duration")
new_task_priority = st.selectbox("Priority", ["Low", "Medium", "High"], key="new_task_priority")

new_task_subject = st.selectbox(
"Subject",
["No Subject"] + subject_names,
key="new_task_subject"
)

new_task_subject_id = subject_ids[subject_names.index(new_task_subject)] if new_task_subject in subject_names else None

add_task = st.button("➕ Add Study Task", key="add_task")

save_task = cursor.execute(
"INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
new_task_title,
str(new_task_date),
new_task_duration,
new_task_priority,
0,
new_task_subject_id
)
) if add_task and new_task_title.strip() else None

conn.commit()

cursor.execute(
"SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date"
)

all_tasks = cursor.fetchall()

st.dataframe(
all_tasks,
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

st.success("🎉 StudySphere navigation is working!")

conn.close()
