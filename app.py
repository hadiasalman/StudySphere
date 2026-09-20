import streamlit as st
import sqlite3
from datetime import date

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")

cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")

conn.commit()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("📚 Add Subject")

subject_name = st.text_input("Subject Name")
subject_code = st.text_input("Subject Code")
subject_instructor = st.text_input("Instructor")

add_subject = st.button("➕ Add Subject")

save_subject = cursor.execute("INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)", (subject_name, subject_code, subject_instructor)) if add_subject and subject_name.strip() else None
conn.commit()

st.divider()

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

st.header("📝 Add Assignment")

assignment_title = st.text_input("Assignment Title")
assignment_description = st.text_area("Assignment Description")
assignment_deadline = st.date_input("Deadline", value=date.today())
assignment_priority = st.selectbox("Priority", ["Low", "Medium", "High"])

selected_subject = st.selectbox("Subject", ["No Subject"] + subject_names)

selected_subject_id = subject_ids[subject_names.index(selected_subject)] if selected_subject in subject_names else None

add_assignment = st.button("➕ Add Assignment")

save_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(assignment_title, assignment_description, str(assignment_deadline), assignment_priority, "Pending", selected_subject_id)
) if add_assignment and assignment_title.strip() else None

conn.commit()

st.divider()

st.header("📋 Your Assignments")

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.deadline, assignments.priority, assignments.status, subjects.name "
"FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id "
"ORDER BY assignments.deadline"
)

assignments = cursor.fetchall()

st.write("Total Assignments:", len(assignments))

st.dataframe(
assignments,
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

st.info("💡 Add your subjects first, then select a subject when creating an assignment.")

conn.close()
