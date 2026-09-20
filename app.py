import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
conn.commit()

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

st.sidebar.title("StudySphere")
page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "📚 Subjects"])

st.header("🏠 Dashboard") if page == "🏠 Dashboard" else None

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

st.metric("📚 Subjects", subject_count) if page == "🏠 Dashboard" else None

st.write("Welcome to your StudySphere dashboard!") if page == "🏠 Dashboard" else None

st.header("📚 Subjects") if page == "📚 Subjects" else None

subject_name = st.text_input("Subject Name") if page == "📚 Subjects" else ""
subject_code = st.text_input("Subject Code") if page == "📚 Subjects" else ""
subject_instructor = st.text_input("Instructor") if page == "📚 Subjects" else ""

add_subject = st.button("➕ Add Subject") if page == "📚 Subjects" else False

valid_subject = bool(subject_name.strip())

cursor.execute(
"INSERT INTO subjects (name, code, instructor) VALUES (?, ?, ?)",
(subject_name.strip(), subject_code.strip(), subject_instructor.strip())
) if page == "📚 Subjects" and add_subject and valid_subject else None

conn.commit() if page == "📚 Subjects" and add_subject and valid_subject else None

st.success("Subject added successfully!") if page == "📚 Subjects" and add_subject and valid_subject else None

st.error("Please enter a subject name.") if page == "📚 Subjects" and add_subject and not valid_subject else None

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
subject_list = cursor.fetchall()

st.subheader("Your Subjects") if page == "📚 Subjects" else None

st.dataframe(
subject_list,
column_config={
"id": "ID",
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
use_container_width=True,
hide_index=True
) if page == "📚 Subjects" else None

conn.close()
