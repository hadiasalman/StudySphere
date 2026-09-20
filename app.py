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

subject_name = st.text_input("Subject Name")
subject_code = st.text_input("Subject Code")
subject_instructor = st.text_input("Instructor")

add_subject = st.button("➕ Add Subject")

save_subject = cursor.execute("INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)", (subject_name, subject_code, subject_instructor)) if add_subject and subject_name.strip() else None

conn.commit()

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
subject_rows = cursor.fetchall()

subject_names = [row[1] for row in subject_rows]
subject_ids = [row[0] for row in subject_rows]

st.divider()

st.header("📅 Add Exam")

exam_title = st.text_input("Exam Title")
exam_date = st.date_input("Exam Date", value=date.today())
exam_syllabus = st.text_area("Syllabus")
exam_notes = st.text_area("Exam Notes")

selected_exam_subject = st.selectbox("Exam Subject", ["No Subject"] + subject_names)

exam_subject_id = subject_ids[subject_names.index(selected_exam_subject)] if selected_exam_subject in subject_names else None

add_exam = st.button("➕ Add Exam")

save_exam = cursor.execute(
"INSERT INTO exams (title, exam_date, syllabus, notes, subject_id) VALUES (?, ?, ?, ?, ?)",
(exam_title, str(exam_date), exam_syllabus, exam_notes, exam_subject_id)
) if add_exam and exam_title.strip() else None

conn.commit()

st.divider()

st.header("📋 Upcoming Exams")

cursor.execute(
"SELECT exams.id, exams.title, exams.exam_date, exams.syllabus, exams.notes, subjects.name "
"FROM exams LEFT JOIN subjects ON exams.subject_id = subjects.id "
"ORDER BY exams.exam_date"
)

exams = cursor.fetchall()

st.write("Total Exams:", len(exams))

st.dataframe(
exams,
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

st.info("💡 Add an exam with its date, syllabus and subject to keep your exam schedule organized.")

conn.close()
