import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓", layout="wide")

DB_NAME = "studysphere.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, name TEXT, email TEXT, university TEXT, degree TEXT, semester TEXT, target_gpa REAL)")
conn.commit()

st.title("🎓 StudySphere")
st.subheader("Learn smarter. Plan better. Achieve more.")

st.divider()

st.metric("📚 Subjects", "0")
st.metric("📝 Assignments", "0")
st.metric("📅 Exams", "0")
st.metric("🎯 Target GPA", "3.8")

st.divider()

st.header("👋 Welcome to StudySphere!")
st.write("Your personal AI-powered student companion.")
st.write("Manage your subjects, assignments, exams and study plans in one place.")

st.success("✅ StudySphere is running successfully!")

conn.close()
