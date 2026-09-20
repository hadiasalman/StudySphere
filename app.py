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

subject_name = st.text_input("Subject Name") if page == "📚 Subjects" else ""
subject_code = st.text_input("Subject Code") if page == "📚 Subjects" else ""
subject_instructor = st.text_input("Instructor") if page == "📚 Subjects" else ""

add_subject = st.button("➕ Add Subject") if page == "📚 Subjects" else False

save_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name, subject_code, subject_instructor)
) if add_subject and subject_name.strip() else None

conn.commit() if add_subject and subject_name.strip() else None

st.success("Subject added successfully!") if add_subject and subject_name.strip() else None

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name") if page == "📚 Subjects" else None

subject_list = cursor.fetchall() if page == "📚 Subjects" else []

st.subheader("Your Subjects") if page == "📚 Subjects" else None

st.dataframe(
subject_list,
column_config={
"id": "ID",
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
hide_index=True
) if page == "📚 Subjects" else None

conn.close()
