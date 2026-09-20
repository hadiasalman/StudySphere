import streamlit as st
import sqlite3

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

st.sidebar.title("🎓 StudySphere")
st.sidebar.caption("Learn smarter. Plan better. Achieve more.")

page = st.sidebar.radio(
"Navigation",
[
"🏠 Dashboard",
"📚 Subjects",
"📝 Assignments",
"📅 Exams",
"✅ Study Planner"
]
)

st.sidebar.divider()
st.sidebar.write("📊 Quick Stats")
st.sidebar.write("📚 Subjects:", subject_count)
st.sidebar.write("📝 Assignments:", assignment_count)
st.sidebar.write("📅 Exams:", exam_count)
st.sidebar.write("✅ Study Tasks:", task_count)

if page == "🏠 Dashboard":
st.title("🎓 StudySphere")
st.caption("Learn smarter. Plan better. Achieve more.")
st.divider()

```
st.header("🏠 Dashboard")
st.write("Welcome to your StudySphere dashboard.")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📚 Subjects", subject_count)
col2.metric("📝 Assignments", assignment_count)
col3.metric("📅 Exams", exam_count)
col4.metric("✅ Study Tasks", task_count)

st.subheader("📝 Upcoming Assignments")

cursor.execute(
    "SELECT title, deadline, priority, status FROM assignments ORDER BY deadline LIMIT 5"
)

dashboard_assignments = cursor.fetchall()

if dashboard_assignments:
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
else:
    st.info("No assignments added yet.")
```

elif page == "📚 Subjects":
st.title("📚 Subjects")
st.write("This is the Subjects page.")

```
st.success("Subjects page is working!")
```

elif page == "📝 Assignments":
st.title("📝 Assignments")
st.write("This is the Assignments page.")

```
st.success("Assignments page is working!")
```

elif page == "📅 Exams":
st.title("📅 Exams")
st.write("This is the Exams page.")

```
st.success("Exams page is working!")
```

elif page == "✅ Study Planner":
st.title("✅ Study Planner")
st.write("This is the Study Planner page.")

```
st.success("Study Planner page is working!")
```

conn.close()
