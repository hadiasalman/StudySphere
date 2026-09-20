import streamlit as st
import sqlite3

st.set_page_config(page_title="StudySphere", page_icon="🎓")

st.title("🎓 StudySphere")
st.write("StudySphere is running successfully!")

conn = sqlite3.connect("studysphere.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, code TEXT, instructor TEXT)")
conn.commit()

cursor.execute("SELECT id, name, code, instructor FROM subjects ORDER BY name")
subjects = cursor.fetchall()

st.subheader("📚 Your Subjects")

st.dataframe(subjects, use_container_width=True, hide_index=True)

st.success("Database connected successfully!")
