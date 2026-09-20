import streamlit as st
import sqlite3

st.title("StudySphere")
conn = sqlite3.connect("studysphere.db")
st.success("StudySphere is working!")
