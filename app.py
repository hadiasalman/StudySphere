import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, task_date TEXT, duration INTEGER, priority TEXT, completed INTEGER DEFAULT 0, subject_id INTEGER)")
conn.commit()

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio(
"Navigation",
[1, 2, 3, 4, 5],
format_func=lambda x: {
1: "🏠 Dashboard",
2: "📚 Subjects",
3: "📝 Assignments",
4: "📅 Exams",
5: "✅ Study Planner"
}[x]
)

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM exams")
exam_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 0")
pending_task_count = cursor.fetchone()[0]

dashboard_header = st.header("🏠 Dashboard") if page == 1 else None

dashboard_col1, dashboard_col2, dashboard_col3, dashboard_col4 = st.columns(4) if page == 1 else (None, None, None, None)

dashboard_metric1 = dashboard_col1.metric("📚 Subjects", subject_count) if page == 1 else None
dashboard_metric2 = dashboard_col2.metric("📝 Assignments", assignment_count) if page == 1 else None
dashboard_metric3 = dashboard_col3.metric("📅 Exams", exam_count) if page == 1 else None
dashboard_metric4 = dashboard_col4.metric("✅ Pending Tasks", pending_task_count) if page == 1 else None

dashboard_text = st.write("Welcome to your StudySphere dashboard!") if page == 1 else None

subjects_header = st.header("📚 Subjects") if page == 2 else None

subject_name = st.text_input("Subject Name") if page == 2 else ""
subject_code = st.text_input("Subject Code") if page == 2 else ""
subject_instructor = st.text_input("Instructor") if page == 2 else ""

add_subject = st.button("➕ Add Subject") if page == 2 else False

valid_subject = bool(subject_name.strip())

insert_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name.strip(), subject_code.strip(), subject_instructor.strip())
) if page == 2 and add_subject and valid_subject else None

commit_subject = conn.commit() if page == 2 and add_subject and valid_subject else None

subject_success = st.success("Subject added successfully!") if page == 2 and add_subject and valid_subject else None

subject_error = st.error("Please enter a subject name.") if page == 2 and add_subject and not valid_subject else None

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
subject_list = cursor.fetchall()

subject_table = st.dataframe(
subject_list,
use_container_width=True,
hide_index=True
) if page == 2 else None

assignments_header = st.header("📝 Assignments") if page == 3 else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
assignment_subject_rows = cursor.fetchall()

assignment_subject_names = [row[1] for row in assignment_subject_rows]
assignment_subject_ids = [row[0] for row in assignment_subject_rows]

assignment_title = st.text_input("Assignment Title") if page == 3 else ""
assignment_description = st.text_area("Description") if page == 3 else ""
assignment_deadline = st.date_input("Deadline") if page == 3 else None

assignment_priority = st.selectbox(
"Priority",
["Low", "Medium", "High"]
) if page == 3 else "Medium"

assignment_status = st.selectbox(
"Status",
["Pending", "In Progress", "Completed"]
) if page == 3 else "Pending"

assignment_subject = st.selectbox(
"Subject",
assignment_subject_names
) if page == 3 and assignment_subject_names else ""

assignment_subject_id = assignment_subject_ids[assignment_subject_names.index(assignment_subject)] if page == 3 and assignment_subject_names and assignment_subject else None

add_assignment = st.button("➕ Add Assignment") if page == 3 else False

valid_assignment = bool(assignment_title.strip()) and bool(assignment_subject_names)

insert_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
assignment_title.strip(),
assignment_description.strip(),
str(assignment_deadline),
assignment_priority,
assignment_status,
assignment_subject_id
)
) if page == 3 and add_assignment and valid_assignment else None

commit_assignment = conn.commit() if page == 3 and add_assignment and valid_assignment else None

assignment_success = st.success("Assignment added successfully!") if page == 3 and add_assignment and valid_assignment else None

assignment_error = st.error("Enter an assignment title and make sure you have at least one subject.") if page == 3 and add_assignment and not valid_assignment else None

cursor.execute("SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline")

assignment_list = cursor.fetchall()

assignment_table = st.dataframe(
assignment_list,
use_container_width=True,
hide_index=True
) if page == 3 else None

exams_header = st.header("📅 Exams") if page == 4 else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
exam_subject_rows = cursor.fetchall()

exam_subject_names = [row[1] for row in exam_subject_rows]
exam_subject_ids = [row[0] for row in exam_subject_rows]

exam_title = st.text_input("Exam Title") if page == 4 else ""
exam_date = st.date_input("Exam Date") if page == 4 else None
exam_syllabus = st.text_area("Syllabus") if page == 4 else ""
exam_notes = st.text_area("Notes") if page == 4 else ""

exam_subject = st.selectbox(
"Subject",
exam_subject_names
) if page == 4 and exam_subject_names else ""

exam_subject_id = exam_subject_ids[exam_subject_names.index(exam_subject)] if page == 4 and exam_subject_names and exam_subject else None

add_exam = st.button("➕ Add Exam") if page == 4 else False

valid_exam = bool(exam_title.strip()) and bool(exam_subject_names)

insert_exam = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(
exam_title.strip(),
str(exam_date),
exam_syllabus.strip(),
exam_notes.strip(),
exam_subject_id
)
) if page == 4 and add_exam and valid_exam else None

commit_exam = conn.commit() if page == 4 and add_exam and valid_exam else None

exam_success = st.success("Exam added successfully!") if page == 4 and add_exam and valid_exam else None

exam_error = st.error("Enter an exam title and make sure you have at least one subject.") if page == 4 and add_exam and not valid_exam else None

cursor.execute("SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id ORDER BY exams.exam_date")

exam_list = cursor.fetchall()

exam_table = st.dataframe(
exam_list,
use_container_width=True,
hide_index=True
) if page == 4 else None

planner_header = st.header("✅ Study Planner") if page == 5 else None

st.write("Create and manage your daily study tasks.") if page == 5 else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
task_subject_rows = cursor.fetchall()

task_subject_names = [row[1] for row in task_subject_rows]
task_subject_ids = [row[0] for row in task_subject_rows]

task_title = st.text_input("Study Task") if page == 5 else ""

task_date = st.date_input("Study Date") if page == 5 else None

task_duration = st.number_input(
"Duration (minutes)",
min_value=15,
max_value=600,
value=60,
step=15
) if page == 5 else 60

task_priority = st.selectbox(
"Priority",
["Low", "Medium", "High"]
) if page == 5 else "Medium"

task_subject = st.selectbox(
"Subject",
task_subject_names
) if page == 5 and task_subject_names else ""

task_subject_id = task_subject_ids[task_subject_names.index(task_subject)] if page == 5 and task_subject_names and task_subject else None

add_task = st.button("➕ Add Study Task") if page == 5 else False

valid_task = bool(task_title.strip()) and bool(task_subject_names)

insert_task = cursor.execute(
"INSERT INTO tasks (title, task_date, duration, priority, completed, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
task_title.strip(),
str(task_date),
int(task_duration),
task_priority,
0,
task_subject_id
)
) if page == 5 and add_task and valid_task else None

commit_task = conn.commit() if page == 5 and add_task and valid_task else None

task_success = st.success("Study task added successfully!") if page == 5 and add_task and valid_task else None

task_error = st.error("Enter a study task and make sure you have at least one subject.") if page == 5 and add_task and not valid_task else None

cursor.execute("SELECT tasks.id, tasks.title, tasks.task_date, tasks.duration, tasks.priority, tasks.completed, subjects.name FROM tasks LEFT JOIN subjects ON tasks.subject_id = subjects.id ORDER BY tasks.task_date")

task_list = cursor.fetchall()

task_table = st.dataframe(
task_list,
use_container_width=True,
hide_index=True
) if page == 5 else None

conn.close()
