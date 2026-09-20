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

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("🏠 Dashboard")
st.write("Welcome to your StudySphere dashboard.")

st.metric("📚 Subjects", subject_count)
st.metric("📝 Assignments", assignment_count)
st.metric("📅 Exams", exam_count)
st.metric("✅ Study Tasks", task_count)

cursor.execute("SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5")
dashboard_assignments = cursor.fetchall()

st.subheader("📝 Upcoming Assignments")

st.dataframe(
dashboard_assignments,
column_config={
"title": "Assignment",
"deadline": "Deadline",
"priority": "Priority",
"status": "Status"
},
hide_index=True
)

st.stop() if page != "🏠 Dashboard" else None
