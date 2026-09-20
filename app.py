import streamlit as st
import sqlite3

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

st.sidebar.title("🎓 StudySphere")
st.sidebar.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "📚 Subjects", "📝 Assignments", "📅 Exams", "✅ Study Planner"])

st.sidebar.divider()
st.sidebar.write("📊 Quick Stats")
st.sidebar.write("📚 Subjects:", subject_count)
st.sidebar.write("📝 Assignments:", assignment_count)
st.sidebar.write("📅 Exams:", exam_count)
st.sidebar.write("✅ Study Tasks:", task_count)

dashboard_title = "🎓 StudySphere"
subjects_title = "📚 Subjects"
assignments_title = "📝 Assignments"
exams_title = "📅 Exams"
planner_title = "✅ Study Planner"

st.title(dashboard_title if page == "🏠 Dashboard" else subjects_title if page == "📚 Subjects" else assignments_title if page == "📝 Assignments" else exams_title if page == "📅 Exams" else planner_title)

st.caption("Learn smarter. Plan better. Achieve more.")

st.divider()
st.write("You selected:", page)

subject_name = st.selectbox(
"Subject",
subject_names
) if page == "📝 Assignments" and subject_names else ""

assignment_title = st.text_input("Assignment Title") if page == "📝 Assignments" else ""
assignment_description = st.text_area("Description") if page == "📝 Assignments" else ""
assignment_deadline = st.date_input("Deadline") if page == "📝 Assignments" else None
assignment_priority = st.selectbox("Priority", ["Low", "Medium", "High"]) if page == "📝 Assignments" else ""
assignment_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"]) if page == "📝 Assignments" else ""

selected_subject_id = subject_ids[subject_names.index(subject_name)] if page == "📝 Assignments" and subject_name else None

add_assignment = st.button("➕ Add Assignment") if page == "📝 Assignments" else False

assignment_saved = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
assignment_title,
assignment_description,
str(assignment_deadline),
assignment_priority,
assignment_status,
selected_subject_id
)
) if add_assignment and assignment_title.strip() and selected_subject_id else None

conn.commit() if add_assignment and assignment_title.strip() and selected_subject_id else None

st.success("Assignment added successfully!") if add_assignment and assignment_title.strip() and selected_subject_id else None

st.warning("Please add a Subject first.") if page == "📝 Assignments" and not subject_names else None

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
) if page == "📝 Assignments" else None

conn.close()
