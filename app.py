import streamlit as st
import sqlite3
from datetime import date

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, exam_date TEXT, syllabus TEXT, notes TEXT, subject_id INTEGER)")
conn.commit()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("📚 Subjects")

subject_name = st.text_input("Subject Name", key="subject_name")
subject_code = st.text_input("Subject Code", key="subject_code")
subject_instructor = st.text_input("Instructor", key="subject_instructor")

add_subject = st.button("➕ Add Subject")

save_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name, subject_code, subject_instructor)
) if add_subject and subject_name.strip() else None

conn.commit()

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

st.write("Total Subjects:", len(subject_rows))

st.dataframe(
cursor.execute("SELECT name, code, instructor FROM subjects ORDER BY id DESC").fetchall(),
column_config={
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
hide_index=True
)

st.divider()

st.header("📝 Assignments")

assignment_title = st.text_input("Assignment Title", key="assignment_title")
assignment_description = st.text_area("Assignment Description", key="assignment_description")
assignment_deadline = st.date_input("Assignment Deadline", value=date.today(), key="assignment_deadline")
assignment_priority = st.selectbox("Assignment Priority", ["Low", "Medium", "High"], key="assignment_priority")

assignment_subject = st.selectbox(
"Assignment Subject",
["No Subject"] + subject_names,
key="assignment_subject"
)

assignment_subject_id = subject_ids[subject_names.index(assignment_subject)] if assignment_subject in subject_names else None

add_assignment = st.button("➕ Add Assignment")

save_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
assignment_title,
assignment_description,
str(assignment_deadline),
assignment_priority,
"Pending",
assignment_subject_id
)
) if add_assignment and assignment_title.strip() else None

conn.commit()

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.deadline, assignments.priority, assignments.status, subjects.name "
"FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id "
"ORDER BY assignments.deadline"
)

assignment_rows = cursor.fetchall()

st.write("Total Assignments:", len(assignment_rows))

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

exam_title = st.text_input("Exam Title", key="exam_title")
exam_date = st.date_input("Exam Date", value=date.today(), key="exam_date")
exam_syllabus = st.text_area("Exam Syllabus", key="exam_syllabus")
exam_notes = st.text_area("Exam Notes", key="exam_notes")

exam_subject = st.selectbox(
"Exam Subject",
["No Subject"] + subject_names,
key="exam_subject"
)

exam_subject_id = subject_ids[subject_names.index(exam_subject)] if exam_subject in subject_names else None

add_exam = st.button("➕ Add Exam")

save_exam = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(
exam_title,
str(exam_date),
exam_syllabus,
exam_notes,
exam_subject_id
)
) if add_exam and exam_title.strip() else None

conn.commit()

cursor.execute(
"SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name "
"FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id "
"ORDER BY exams.exam_date"
)

exam_rows = cursor.fetchall()

st.write("Total Exams:", len(exam_rows))

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

st.success("🎉 Subjects, Assignments and Exams are all included in this version.")

conn.close()
