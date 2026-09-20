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

cursor.execute("SELECT name, code, instructor FROM subjects ORDER BY id DESC")
all_subjects = cursor.fetchall()

cursor.execute("SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5")
upcoming_assignments = cursor.fetchall()

cursor.execute("SELECT title, exam_date, notes FROM exams ORDER BY exam_date LIMIT 5")
upcoming_exams = cursor.fetchall()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("👋 Welcome back!")

st.write("Your personal student dashboard is ready.")

st.divider()

st.header("📊 Your Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Subjects", subject_count)
col2.metric("📝 Assignments", assignment_count)
col3.metric("📅 Exams", exam_count)
col4.metric("✅ Study Tasks", task_count)

st.divider()

st.header("📝 Upcoming Assignments")

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

st.header("📅 Upcoming Exams")

st.dataframe(
upcoming_exams,
column_config={
"title": "Exam",
"exam_date": "Exam Date",
"notes": "Notes"
},
hide_index=True
)

st.divider()

st.header("📚 Your Subjects")

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

st.header("🧭 StudySphere Modules")

st.info("📚 Subjects — Manage your university subjects.")
st.info("📝 Assignments — Track assignments and deadlines.")
st.info("📅 Exams — Organize your exams and syllabus.")
st.info("✅ Study Planner — Plan your daily study tasks.")

st.success("🎉 Your StudySphere dashboard is working!")

conn.close()
