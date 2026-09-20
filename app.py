import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

DB_NAME = "studysphere.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, name TEXT, email TEXT, university TEXT, degree TEXT, semester TEXT, target_gpa REAL)")

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, code TEXT, instructor TEXT, description TEXT)")

conn.commit()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.header("📚 Subjects")

subject_name = st.text_input("Subject Name")
subject_code = st.text_input("Subject Code")
subject_instructor = st.text_input("Instructor")
subject_description = st.text_area("Description")

add_subject = st.button("➕ Add Subject")

if add_subject:
if subject_name.strip() == "":
st.error("Please enter a subject name.")
else:
cursor.execute(
"INSERT INTO subjects (name, code, instructor, description) VALUES (?, ?, ?, ?)",
(subject_name, subject_code, subject_instructor, subject_description)
)
conn.commit()
st.success("✅ Subject added successfully!")

st.divider()

st.header("📖 Your Subjects")

cursor.execute("SELECT id, name, code, instructor, description FROM subjects ORDER BY id DESC")
subjects = cursor.fetchall()

st.write("Total Subjects:", len(subjects))

for subject in subjects:
st.subheader("📘 " + subject[1])
st.write("Code:", subject[2])
st.write("Instructor:", subject[3])
st.write("Description:", subject[4])

```
delete_subject = st.button("🗑️ Delete " + str(subject[0]))

if delete_subject:
    cursor.execute("DELETE FROM subjects WHERE id = ?", (subject[0],))
    conn.commit()
    st.rerun()

st.divider()
```

conn.close()
