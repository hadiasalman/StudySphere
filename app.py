import streamlit as st
import sqlite3

st.title("StudySphere")

def get_connection():
conn = sqlite3.connect("studysphere.db")
return conn

st.success("StudySphere is working!")
