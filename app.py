import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
conn.commit()

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "📚 Subjects"])

show_dashboard_header = st.header("🏠 Dashboard") if page == "🏠 Dashboard" else None

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

show_metric = st.metric("📚 Subjects", subject_count) if page == "🏠 Dashboard" else None

show_welcome = st.write("Welcome to your StudySphere dashboard!") if page == "🏠 Dashboard" else None

show_subject_header = st.header("📚 Subjects") if page == "📚 Subjects" else None

subject_name = st.text_input("Subject Name") if page == "📚 Subjects" else ""
subject_code = st.text_input("Subject Code") if page == "📚 Subjects" else ""
subject_instructor = st.text_input("Instructor") if page == "📚 Subjects" else ""

add_subject = st.button("➕ Add Subject") if page == "📚 Subjects" else False

valid_subject = bool(subject_name.strip())

insert_subject = cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name.strip(), subject_code.strip(), subject_instructor.strip())
) if page == "📚 Subjects" and add_subject and valid_subject else None

commit_subject = conn.commit() if page == "📚 Subjects" and add_subject and valid_subject else None

show_success = st.success("Subject added successfully!") if page == "📚 Subjects" and add_subject and valid_subject else None

show_error = st.error("Please enter a subject name.") if page == "📚 Subjects" and add_subject and not valid_subject else None

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
subject_list = cursor.fetchall()

show_subjects = st.dataframe(
subject_list,
use_container_width=True,
hide_index=True
) if page == "📚 Subjects" else None

conn.close()
