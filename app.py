import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
conn.commit()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("📚 Add a Subject")

subject_name = st.text_input("Subject Name")
subject_code = st.text_input("Subject Code")
subject_instructor = st.text_input("Instructor")

st.write("Enter the information above and click the button below.")

add_subject = st.button("➕ Add Subject")

st.divider()

st.header("📖 Subjects")

cursor.execute("SELECT name, code, instructor FROM subjects ORDER BY id DESC")
subjects = cursor.fetchall()

st.write("Subjects currently saved:", len(subjects))

st.dataframe(
subjects,
column_config={
"name": "Subject",
"code": "Code",
"instructor": "Instructor"
},
hide_index=True
)

conn.close()
