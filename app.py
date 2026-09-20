import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
conn.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, deadline TEXT, priority TEXT, status TEXT, subject_id INTEGER)")
conn.commit()

st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio(
"Navigation",
["🏠 Dashboard", "📚 Subjects", "📝 Assignments"]
)

cursor.execute("SELECT COUNT(*) FROM subjects")
subject_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM assignments")
assignment_count = cursor.fetchone()[0]

dashboard_header = st.header("🏠 Dashboard") if page == "🏠 Dashboard" else None
dashboard_col1, dashboard_col2 = st.columns(2) if page == "🏠 Dashboard" else (None, None)

dashboard_metric1 = dashboard_col1.metric("📚 Subjects", subject_count) if page == "🏠 Dashboard" else None
dashboard_metric2 = dashboard_col2.metric("📝 Assignments", assignment_count) if page == "🏠 Dashboard" else None

dashboard_text = st.write("Welcome to your StudySphere dashboard!") if page == "🏠 Dashboard" else None

subjects_header = st.header("📚 Subjects") if page == "📚 Subjects" else None

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

subject_success = st.success("Subject added successfully!") if page == "📚 Subjects" and add_subject and valid_subject else None

subject_error = st.error("Please enter a subject name.") if page == "📚 Subjects" and add_subject and not valid_subject else None

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
subject_list = cursor.fetchall()

subject_table = st.dataframe(
subject_list,
use_container_width=True,
hide_index=True
) if page == "📚 Subjects" else None

assignments_header = st.header("📝 Assignments") if page == "📝 Assignments" else None

cursor.execute("SELECT id, name FROM subjects ORDER BY name")
assignment_subject_rows = cursor.fetchall()

assignment_subject_names = [row[1] for row in assignment_subject_rows]
assignment_subject_ids = [row[0] for row in assignment_subject_rows]

assignment_title = st.text_input("Assignment Title") if page == "📝 Assignments" else ""

assignment_description = st.text_area("Description") if page == "📝 Assignments" else ""

assignment_deadline = st.date_input("Deadline") if page == "📝 Assignments" else None

assignment_priority = st.selectbox(
"Priority",
["Low", "Medium", "High"]
) if page == "📝 Assignments" else "Medium"

assignment_status = st.selectbox(
"Status",
["Pending", "In Progress", "Completed"]
) if page == "📝 Assignments" else "Pending"

assignment_subject = st.selectbox(
"Subject",
assignment_subject_names
) if page == "📝 Assignments" and assignment_subject_names else ""

assignment_subject_id = assignment_subject_ids[assignment_subject_names.index(assignment_subject)] if page == "📝 Assignments" and assignment_subject_names and assignment_subject else None

add_assignment = st.button("➕ Add Assignment") if page == "📝 Assignments" else False

valid_assignment = bool(assignment_title.strip()) and bool(assignment_subject_names)

insert_assignment = cursor.execute(
"INSERT INTO assignments (title, description, deadline, priority, status, subject_id) VALUES (?, ?, ?, ?, ?, ?)",
(
assignment_title.strip(),
assignment_description.strip(),
str(assignment_deadline),
assignment_priority,
assignment_status,
assignment_subject_id
)
) if page == "📝 Assignments" and add_assignment and valid_assignment else None

commit_assignment = conn.commit() if page == "📝 Assignments" and add_assignment and valid_assignment else None

assignment_success = st.success("Assignment added successfully!") if page == "📝 Assignments" and add_assignment and valid_assignment else None

assignment_error = st.error("Enter an assignment title and make sure you have at least one subject.") if page == "📝 Assignments" and add_assignment and not valid_assignment else None

cursor.execute(
"SELECT assignments.id, assignments.title, assignments.description, assignments.deadline, assignments.priority, assignments.status, subjects.name FROM assignments LEFT JOIN subjects ON assignments.subject_id = subjects.id ORDER BY assignments.deadline"
)

assignment_list = cursor.fetchall()

assignment_table = st.dataframe(
assignment_list,
use_container_width=True,
hide_index=True
) if page == "📝 Assignments" else None

conn.close()
