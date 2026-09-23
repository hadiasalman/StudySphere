import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import os
from anthropic import Anthropic
import google.generativeai as genai

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with all tables including academic structures."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    
    # Existing tables...
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS institutions (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        code TEXT UNIQUE,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # ===== NEW TABLES FOR STEP 6: ACADEMIC STRUCTURES =====
    
    # Programs (e.g., BS Artificial Intelligence, BS Computer Science)
    c.execute('''CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY,
        institution_id INTEGER,
        name TEXT,
        code TEXT,
        description TEXT,
        duration_years INTEGER,
        total_credits INTEGER,
        level TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(institution_id) REFERENCES institutions(id),
        UNIQUE(institution_id, code)
    )''')
    
    # Degrees (subdivisions of programs, e.g., General, Honors)
    c.execute('''CREATE TABLE IF NOT EXISTS degrees (
        id INTEGER PRIMARY KEY,
        program_id INTEGER,
        name TEXT,
        code TEXT,
        description TEXT,
        min_gpa REAL,
        total_credits INTEGER,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(program_id) REFERENCES programs(id),
        UNIQUE(program_id, code)
    )''')
    
    # Semesters (e.g., Fall 2024, Spring 2025)
    c.execute('''CREATE TABLE IF NOT EXISTS semesters (
        id INTEGER PRIMARY KEY,
        institution_id INTEGER,
        name TEXT,
        code TEXT,
        season TEXT,
        year INTEGER,
        start_date DATE,
        end_date DATE,
        registration_deadline DATE,
        status TEXT DEFAULT 'planning',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(institution_id) REFERENCES institutions(id),
        UNIQUE(institution_id, code)
    )''')
    
    # Sections (course sections offered in a semester)
    c.execute('''CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY,
        course_id INTEGER,
        semester_id INTEGER,
        section_code TEXT,
        faculty_id INTEGER,
        capacity INTEGER,
        enrolled_count INTEGER DEFAULT 0,
        schedule TEXT,
        location TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(semester_id) REFERENCES semesters(id),
        FOREIGN KEY(faculty_id) REFERENCES users(id),
        UNIQUE(course_id, semester_id, section_code)
    )''')
    
    # Student Enrollments
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        section_id INTEGER,
        semester_id INTEGER,
        status TEXT DEFAULT 'enrolled',
        grade TEXT,
        gpa_points REAL,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(section_id) REFERENCES sections(id),
        FOREIGN KEY(semester_id) REFERENCES semesters(id),
        UNIQUE(student_id, section_id)
    )''')
    
    # Faculty Course Assignments
    c.execute('''CREATE TABLE IF NOT EXISTS faculty_assignments (
        id INTEGER PRIMARY KEY,
        faculty_id INTEGER,
        course_id INTEGER,
        program_id INTEGER,
        role TEXT DEFAULT 'instructor',
        status TEXT DEFAULT 'active',
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(faculty_id) REFERENCES users(id),
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(program_id) REFERENCES programs(id),
        UNIQUE(faculty_id, course_id, program_id)
    )''')
    
    # Program Requirements (which courses required for degree)
    c.execute('''CREATE TABLE IF NOT EXISTS program_requirements (
        id INTEGER PRIMARY KEY,
        degree_id INTEGER,
        course_id INTEGER,
        semester_order INTEGER,
        is_mandatory BOOLEAN DEFAULT 1,
        credits INTEGER,
        prerequisites TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(degree_id) REFERENCES degrees(id),
        FOREIGN KEY(course_id) REFERENCES courses(id),
        UNIQUE(degree_id, course_id)
    )''')
    
    # Student Program Enrollment (which program/degree is student in)
    c.execute('''CREATE TABLE IF NOT EXISTS student_programs (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        program_id INTEGER,
        degree_id INTEGER,
        enrollment_semester_id INTEGER,
        status TEXT DEFAULT 'enrolled',
        expected_graduation_date DATE,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(program_id) REFERENCES programs(id),
        FOREIGN KEY(degree_id) REFERENCES degrees(id),
        FOREIGN KEY(enrollment_semester_id) REFERENCES semesters(id),
        UNIQUE(student_id, program_id, degree_id)
    )''')
    
    # Existing course and other tables
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        institution_id INTEGER,
        code TEXT,
        name TEXT,
        description TEXT,
        credits INTEGER,
        level TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(institution_id) REFERENCES institutions(id),
        UNIQUE(institution_id, code)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        institution_id INTEGER,
        name TEXT,
        code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(institution_id) REFERENCES institutions(id),
        UNIQUE(institution_id, code)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS course_materials (
        id INTEGER PRIMARY KEY,
        course_id INTEGER,
        title TEXT,
        file_path TEXT,
        file_type TEXT,
        uploaded_by INTEGER,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(uploaded_by) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY,
        course_id INTEGER,
        title TEXT,
        description TEXT,
        due_date DATE,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(created_by) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS faculty_ai_history (
        id INTEGER PRIMARY KEY,
        faculty_id INTEGER,
        course_id INTEGER,
        generation_type TEXT,
        prompt TEXT,
        output TEXT,
        sources TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(faculty_id) REFERENCES users(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )''')
    
    conn.commit()
    conn.close()

# ============================================================================
# DATABASE HELPER FUNCTIONS - ACADEMIC MANAGEMENT
# ============================================================================

def create_program(institution_id, name, code, description, duration_years, total_credits, level):
    """Create a new academic program."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO programs 
                     (institution_id, name, code, description, duration_years, total_credits, level)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (institution_id, name, code, description, duration_years, total_credits, level))
        conn.commit()
        program_id = c.lastrowid
        conn.close()
        return program_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def create_degree(program_id, name, code, description, min_gpa, total_credits):
    """Create a degree within a program."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO degrees 
                     (program_id, name, code, description, min_gpa, total_credits)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (program_id, name, code, description, min_gpa, total_credits))
        conn.commit()
        degree_id = c.lastrowid
        conn.close()
        return degree_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def create_semester(institution_id, name, code, season, year, start_date, end_date, reg_deadline):
    """Create a new semester."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO semesters 
                     (institution_id, name, code, season, year, start_date, end_date, registration_deadline)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (institution_id, name, code, season, year, start_date, end_date, reg_deadline))
        conn.commit()
        semester_id = c.lastrowid
        conn.close()
        return semester_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def create_section(course_id, semester_id, section_code, faculty_id, capacity, schedule, location):
    """Create a course section for a semester."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO sections 
                     (course_id, semester_id, section_code, faculty_id, capacity, schedule, location)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (course_id, semester_id, section_code, faculty_id, capacity, schedule, location))
        conn.commit()
        section_id = c.lastrowid
        conn.close()
        return section_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def enroll_student(student_id, section_id, semester_id):
    """Enroll a student in a section."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO enrollments 
                     (student_id, section_id, semester_id)
                     VALUES (?, ?, ?)''',
                  (student_id, section_id, semester_id))
        
        c.execute('UPDATE sections SET enrolled_count = enrolled_count + 1 WHERE id = ?', (section_id,))
        
        conn.commit()
        enrollment_id = c.lastrowid
        conn.close()
        return enrollment_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def enroll_student_in_program(student_id, program_id, degree_id, enrollment_semester_id):
    """Enroll a student in a degree program."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO student_programs 
                     (student_id, program_id, degree_id, enrollment_semester_id)
                     VALUES (?, ?, ?, ?)''',
                  (student_id, program_id, degree_id, enrollment_semester_id))
        conn.commit()
        enrollment_id = c.lastrowid
        conn.close()
        return enrollment_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def assign_faculty_to_course(faculty_id, course_id, program_id, role='instructor'):
    """Assign faculty to a course."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO faculty_assignments 
                     (faculty_id, course_id, program_id, role)
                     VALUES (?, ?, ?, ?)''',
                  (faculty_id, course_id, program_id, role))
        conn.commit()
        assignment_id = c.lastrowid
        conn.close()
        return assignment_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_programs(institution_id):
    """Get all programs for an institution."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('SELECT * FROM programs WHERE institution_id = ?', (institution_id,))
    programs = c.fetchall()
    conn.close()
    return programs

def get_degrees(program_id):
    """Get all degrees for a program."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('SELECT * FROM degrees WHERE program_id = ?', (program_id,))
    degrees = c.fetchall()
    conn.close()
    return degrees

def get_semesters(institution_id):
    """Get all semesters for an institution."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('SELECT * FROM semesters WHERE institution_id = ? ORDER BY year DESC, season', (institution_id,))
    semesters = c.fetchall()
    conn.close()
    return semesters

def get_sections_for_course_semester(course_id, semester_id):
    """Get all sections for a course in a semester."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT s.*, c.name, c.code, u.full_name as faculty_name
                 FROM sections s
                 JOIN courses c ON s.course_id = c.id
                 LEFT JOIN users u ON s.faculty_id = u.id
                 WHERE s.course_id = ? AND s.semester_id = ?''',
              (course_id, semester_id))
    sections = c.fetchall()
    conn.close()
    return sections

def get_student_enrollments(student_id):
    """Get all enrollments for a student."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT e.*, c.name, c.code, s.name as semester_name
                 FROM enrollments e
                 JOIN sections sec ON e.section_id = sec.id
                 JOIN courses c ON sec.course_id = c.id
                 JOIN semesters s ON e.semester_id = s.id
                 WHERE e.student_id = ?
                 ORDER BY s.year DESC, s.season''',
              (student_id,))
    enrollments = c.fetchall()
    conn.close()
    return enrollments

def get_student_program(student_id):
    """Get student's program enrollment."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT sp.*, p.name as program_name, p.code as program_code, d.name as degree_name
                 FROM student_programs sp
                 JOIN programs p ON sp.program_id = p.id
                 JOIN degrees d ON sp.degree_id = d.id
                 WHERE sp.student_id = ?''',
              (student_id,))
    program = c.fetchone()
    conn.close()
    return program

def get_faculty_assignments(faculty_id):
    """Get courses assigned to faculty."""
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT fa.*, c.name, c.code, p.name as program_name
                 FROM faculty_assignments fa
                 JOIN courses c ON fa.course_id = c.id
                 JOIN programs p ON fa.program_id = p.id
                 WHERE fa.faculty_id = ? AND fa.status = 'active' ''',
              (faculty_id,))
    assignments = c.fetchall()
    conn.close()
    return assignments

# ============================================================================
# STREAMLIT APP
# ============================================================================

st.set_page_config(page_title="StudySphere", layout="wide")

if 'user_id' not in st.session_state:
    st.session_state.user_id = 1
    st.session_state.user_role = 'admin'
    st.session_state.institution_id = 1

init_db()

st.title("📚 StudySphere Step 6: Course & Academic Management")

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

role = st.session_state.user_role
institution_id = st.session_state.institution_id

with st.sidebar:
    st.header("Navigation")
    
    if role == 'admin':
        page = st.radio("Select Page", [
            "📊 Dashboard",
            "🏫 Programs & Degrees",
            "📅 Semesters",
            "📖 Courses & Sections",
            "👥 Enrollments",
            "👨‍🏫 Faculty Assignments",
            "📋 Course Catalog"
        ])
    elif role == 'faculty':
        page = st.radio("Select Page", [
            "📊 Faculty Dashboard",
            "📖 My Courses",
            "👥 My Students",
            "📅 Semester View"
        ])
    elif role == 'student':
        page = st.radio("Select Page", [
            "📊 Student Dashboard",
            "📚 My Program",
            "📖 Current Courses",
            "📋 Course Catalog",
            "📅 Registration"
        ])

# ============================================================================
# ADMIN PAGES
# ============================================================================

if page == "📊 Dashboard":
    st.header("Academic Management Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM programs WHERE institution_id = ?', (institution_id,))
    num_programs = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM courses WHERE institution_id = ?', (institution_id,))
    num_courses = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM semesters WHERE institution_id = ?', (institution_id,))
    num_semesters = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM enrollments WHERE semester_id IN (SELECT id FROM semesters WHERE institution_id = ?)', (institution_id,))
    total_enrollments = c.fetchone()[0]
    
    conn.close()
    
    col1.metric("📚 Programs", num_programs)
    col2.metric("📖 Courses", num_courses)
    col3.metric("📅 Semesters", num_semesters)
    col4.metric("👥 Total Enrollments", total_enrollments)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Active Semesters")
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        c.execute('SELECT name, season, year, status FROM semesters WHERE institution_id = ? ORDER BY year DESC LIMIT 5', (institution_id,))
        semesters_data = c.fetchall()
        conn.close()
        
        if semesters_data:
            df = pd.DataFrame(semesters_data, columns=['Name', 'Season', 'Year', 'Status'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No semesters created yet.")
    
    with col2:
        st.subheader("Recent Programs")
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        c.execute('SELECT name, code, duration_years, total_credits FROM programs WHERE institution_id = ? LIMIT 5', (institution_id,))
        programs_data = c.fetchall()
        conn.close()
        
        if programs_data:
            df = pd.DataFrame(programs_data, columns=['Name', 'Code', 'Duration (yrs)', 'Total Credits'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No programs created yet.")

elif page == "🏫 Programs & Degrees":
    st.header("Programs & Degrees Management")
    
    tab1, tab2 = st.tabs(["Manage Programs", "Manage Degrees"])
    
    with tab1:
        st.subheader("Create New Program")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            prog_name = st.text_input("Program Name", placeholder="e.g., Bachelor of Science in AI")
        with col2:
            prog_code = st.text_input("Program Code", placeholder="e.g., BSAI")
        with col3:
            duration = st.number_input("Duration (Years)", min_value=1, max_value=6, value=4)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_credits = st.number_input("Total Credits Required", min_value=60, max_value=200, value=120)
        with col2:
            level = st.selectbox("Degree Level", ["Undergraduate", "Graduate", "Postgraduate"])
        with col3:
            prog_desc = st.text_area("Description")
        
        if st.button("Create Program", use_container_width=True):
            if prog_name and prog_code:
                program_id = create_program(institution_id, prog_name, prog_code, prog_desc, duration, total_credits, level)
                if program_id:
                    st.success(f"✅ Program '{prog_name}' created successfully!")
                else:
                    st.error("Program code already exists.")
            else:
                st.warning("Please fill in all required fields.")
        
        st.divider()
        st.subheader("Existing Programs")
        
        programs = get_programs(institution_id)
        if programs:
            df = pd.DataFrame(programs, columns=['ID', 'Inst. ID', 'Name', 'Code', 'Description', 'Duration', 'Credits', 'Level', 'Status', 'Created'])
            st.dataframe(df[['Name', 'Code', 'Duration', 'Credits', 'Level', 'Status']], use_container_width=True, hide_index=True)
        else:
            st.info("No programs found.")
    
    with tab2:
        st.subheader("Create New Degree")
        
        programs = get_programs(institution_id)
        if programs:
            program_names = {p[0]: p[3] for p in programs}
            selected_program = st.selectbox("Select Program", options=list(program_names.values()), key="degree_program")
            program_id = [k for k, v in program_names.items() if v == selected_program][0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                degree_name = st.text_input("Degree Name", placeholder="e.g., General, Honors")
            with col2:
                degree_code = st.text_input("Degree Code", placeholder="e.g., BS-AI-H")
            with col3:
                min_gpa = st.number_input("Minimum GPA", min_value=0.0, max_value=4.0, value=2.0)
            
            col1, col2 = st.columns(2)
            with col1:
                degree_credits = st.number_input("Total Credits", min_value=60, value=120)
            with col2:
                degree_desc = st.text_area("Description")
            
            if st.button("Create Degree", use_container_width=True):
                if degree_name and degree_code:
                    degree_id = create_degree(program_id, degree_name, degree_code, degree_desc, min_gpa, degree_credits)
                    if degree_id:
                        st.success(f"✅ Degree '{degree_name}' created successfully!")
                    else:
                        st.error("Degree code already exists for this program.")
                else:
                    st.warning("Please fill in all required fields.")
            
            st.divider()
            st.subheader(f"Degrees in {selected_program}")
            
            degrees = get_degrees(program_id)
            if degrees:
                df = pd.DataFrame(degrees, columns=['ID', 'Prog. ID', 'Name', 'Code', 'Description', 'Min GPA', 'Credits', 'Status', 'Created'])
                st.dataframe(df[['Name', 'Code', 'Min GPA', 'Credits', 'Status']], use_container_width=True, hide_index=True)
            else:
                st.info("No degrees created for this program yet.")
        else:
            st.warning("Create a program first before adding degrees.")

elif page == "📅 Semesters":
    st.header("Semester Management")
    
    st.subheader("Create New Semester")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sem_name = st.text_input("Semester Name", placeholder="e.g., Fall 2024")
    with col2:
        sem_code = st.text_input("Semester Code", placeholder="e.g., FA2024")
    with col3:
        season = st.selectbox("Season", ["Fall", "Spring", "Summer"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.number_input("Year", min_value=2020, max_value=2030, value=2024)
    with col2:
        start_date = st.date_input("Start Date")
    with col3:
        end_date = st.date_input("End Date")
    
    reg_deadline = st.date_input("Registration Deadline")
    
    if st.button("Create Semester", use_container_width=True):
        if sem_name and sem_code:
            semester_id = create_semester(institution_id, sem_name, sem_code, season, year, start_date, end_date, reg_deadline)
            if semester_id:
                st.success(f"✅ Semester '{sem_name}' created successfully!")
            else:
                st.error("Semester code already exists.")
        else:
            st.warning("Please fill in all required fields.")
    
    st.divider()
    st.subheader("Existing Semesters")
    
    semesters = get_semesters(institution_id)
    if semesters:
        df = pd.DataFrame(semesters, columns=['ID', 'Inst. ID', 'Name', 'Code', 'Season', 'Year', 'Start', 'End', 'Reg. Deadline', 'Status', 'Created'])
        st.dataframe(df[['Name', 'Code', 'Season', 'Year', 'Status']], use_container_width=True, hide_index=True)
    else:
        st.info("No semesters created yet.")

elif page == "📖 Courses & Sections":
    st.header("Courses & Sections Management")
    
    tab1, tab2 = st.tabs(["Manage Courses", "Create Sections"])
    
    with tab1:
        st.subheader("Create New Course")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            course_code = st.text_input("Course Code", placeholder="e.g., CS101")
        with col2:
            course_name = st.text_input("Course Name")
        with col3:
            credits = st.number_input("Credits", min_value=1, max_value=4, value=3)
        
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Course Level", ["100", "200", "300", "400", "500"])
        with col2:
            course_desc = st.text_area("Description")
        
        if st.button("Create Course", use_container_width=True):
            if course_code and course_name:
                conn = sqlite3.connect('studysphere.db')
                c = conn.cursor()
                try:
                    c.execute('''INSERT INTO courses 
                                 (institution_id, code, name, description, credits, level)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                              (institution_id, course_code, course_name, course_desc, credits, f"Level {level}"))
                    conn.commit()
                    st.success(f"✅ Course '{course_name}' created successfully!")
                except sqlite3.IntegrityError:
                    st.error("Course code already exists.")
                conn.close()
            else:
                st.warning("Please fill in all required fields.")
        
        st.divider()
        st.subheader("Existing Courses")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        c.execute('SELECT code, name, credits, level FROM courses WHERE institution_id = ?', (institution_id,))
        courses_data = c.fetchall()
        conn.close()
        
        if courses_data:
            df = pd.DataFrame(courses_data, columns=['Code', 'Name', 'Credits', 'Level'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No courses created yet.")
    
    with tab2:
        st.subheader("Create Course Section")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        
        c.execute('SELECT id, name FROM semesters WHERE institution_id = ? ORDER BY year DESC', (institution_id,))
        semesters = c.fetchall()
        
        c.execute('SELECT id, code, name FROM courses WHERE institution_id = ?', (institution_id,))
        courses = c.fetchall()
        
        c.execute('SELECT id, full_name FROM users WHERE role = "faculty"')
        faculty = c.fetchall()
        
        conn.close()
        
        if courses and semesters and faculty:
            col1, col2 = st.columns(2)
            with col1:
                semester_id = st.selectbox("Select Semester", options=[s[0] for s in semesters], format_func=lambda x: next((s[1] for s in semesters if s[0] == x), ""))
            with col2:
                course_id = st.selectbox("Select Course", options=[c[0] for c in courses], format_func=lambda x: next((f"{c[1]} - {c[2]}" for c in courses if c[0] == x), ""))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                section_code = st.text_input("Section Code", placeholder="e.g., A, B, C")
            with col2:
                faculty_id = st.selectbox("Instructor", options=[f[0] for f in faculty], format_func=lambda x: next((f[1] for f in faculty if f[0] == x), ""))
            with col3:
                capacity = st.number_input("Capacity", min_value=10, max_value=100, value=30)
            
            col1, col2 = st.columns(2)
            with col1:
                schedule = st.text_input("Schedule", placeholder="e.g., MWF 10:00-11:00")
            with col2:
                location = st.text_input("Location", placeholder="e.g., Room 101")
            
            if st.button("Create Section", use_container_width=True):
                if section_code and schedule and location:
                    section_id = create_section(course_id, semester_id, section_code, faculty_id, capacity, schedule, location)
                    if section_id:
                        st.success(f"✅ Section '{section_code}' created successfully!")
                    else:
                        st.error("Section already exists.")
                else:
                    st.warning("Please fill in all required fields.")
        else:
            st.warning("Create courses and semesters first before creating sections.")

elif page == "👥 Enrollments":
    st.header("Student Enrollments")
    
    tab1, tab2 = st.tabs(["Enroll Student", "View Enrollments"])
    
    with tab1:
        st.subheader("Enroll Student in Section")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        
        c.execute('SELECT id, full_name FROM users WHERE role = "student"')
        students = c.fetchall()
        
        c.execute('SELECT DISTINCT s.id, c.code, c.name, sm.name as semester FROM sections s JOIN courses c ON s.course_id = c.id JOIN semesters sm ON s.semester_id = sm.id WHERE s.status = "open"')
        sections = c.fetchall()
        
        conn.close()
        
        if students and sections:
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.selectbox("Select Student", options=[s[0] for s in students], format_func=lambda x: next((s[1] for s in students if s[0] == x), ""))
            with col2:
                section_id = st.selectbox("Select Section", options=[s[0] for s in sections], format_func=lambda x: next((f"{s[1]} - {s[2]} ({s[3]})" for s in sections if s[0] == x), ""))
            
            # Get semester_id for the section
            conn = sqlite3.connect('studysphere.db')
            c = conn.cursor()
            c.execute('SELECT semester_id FROM sections WHERE id = ?', (section_id,))
            semester_id = c.fetchone()[0]
            conn.close()
            
            if st.button("Enroll Student", use_container_width=True):
                enrollment_id = enroll_student(student_id, section_id, semester_id)
                if enrollment_id:
                    st.success("✅ Student enrolled successfully!")
                else:
                    st.error("Student is already enrolled in this section.")
        else:
            st.warning("Create students and open sections first.")
    
    with tab2:
        st.subheader("View All Enrollments")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        c.execute('''SELECT u.full_name, c.code, c.name, s.name as semester, e.status
                     FROM enrollments e
                     JOIN users u ON e.student_id = u.id
                     JOIN sections sec ON e.section_id = sec.id
                     JOIN courses c ON sec.course_id = c.id
                     JOIN semesters s ON e.semester_id = s.id
                     ORDER BY s.year DESC, u.full_name''')
        enrollments_data = c.fetchall()
        conn.close()
        
        if enrollments_data:
            df = pd.DataFrame(enrollments_data, columns=['Student', 'Code', 'Course', 'Semester', 'Status'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No enrollments yet.")

elif page == "👨‍🏫 Faculty Assignments":
    st.header("Faculty Course Assignments")
    
    tab1, tab2 = st.tabs(["Assign Faculty", "View Assignments"])
    
    with tab1:
        st.subheader("Assign Faculty to Course")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        
        c.execute('SELECT id, full_name FROM users WHERE role = "faculty"')
        faculty = c.fetchall()
        
        c.execute('SELECT id, code, name FROM courses WHERE institution_id = ?', (institution_id,))
        courses = c.fetchall()
        
        c.execute('SELECT id, name FROM programs WHERE institution_id = ?', (institution_id,))
        programs = c.fetchall()
        
        conn.close()
        
        if faculty and courses and programs:
            col1, col2 = st.columns(2)
            with col1:
                faculty_id = st.selectbox("Select Faculty", options=[f[0] for f in faculty], format_func=lambda x: next((f[1] for f in faculty if f[0] == x), ""))
            with col2:
                course_id = st.selectbox("Select Course", options=[c[0] for c in courses], format_func=lambda x: next((f"{c[1]} - {c[2]}" for c in courses if c[0] == x), ""))
            
            col1, col2 = st.columns(2)
            with col1:
                program_id = st.selectbox("Select Program", options=[p[0] for p in programs], format_func=lambda x: next((p[1] for p in programs if p[0] == x), ""))
            with col2:
                role = st.selectbox("Role", ["instructor", "co-instructor", "teaching_assistant"])
            
            if st.button("Assign Faculty", use_container_width=True):
                assignment_id = assign_faculty_to_course(faculty_id, course_id, program_id, role)
                if assignment_id:
                    st.success("✅ Faculty assigned successfully!")
                else:
                    st.error("Assignment already exists.")
        else:
            st.warning("Create faculty, courses, and programs first.")
    
    with tab2:
        st.subheader("View All Assignments")
        
        conn = sqlite3.connect('studysphere.db')
        c = conn.cursor()
        c.execute('''SELECT u.full_name, c.code, c.name, p.name as program, fa.role
                     FROM faculty_assignments fa
                     JOIN users u ON fa.faculty_id = u.id
                     JOIN courses c ON fa.course_id = c.id
                     JOIN programs p ON fa.program_id = p.id
                     WHERE fa.status = 'active'
                     ORDER BY u.full_name''')
        assignments_data = c.fetchall()
        conn.close()
        
        if assignments_data:
            df = pd.DataFrame(assignments_data, columns=['Faculty', 'Course Code', 'Course Name', 'Program', 'Role'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No faculty assignments yet.")

elif page == "📋 Course Catalog":
    st.header("Course Catalog")
    
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT c.code, c.name, c.credits, c.level, COUNT(DISTINCT s.id) as sections_count
                 FROM courses c
                 LEFT JOIN sections s ON c.id = s.course_id
                 WHERE c.institution_id = ?
                 GROUP BY c.id
                 ORDER BY c.code''', (institution_id,))
    catalog_data = c.fetchall()
    conn.close()
    
    if catalog_data:
        df = pd.DataFrame(catalog_data, columns=['Code', 'Name', 'Credits', 'Level', 'Sections'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No courses in catalog.")

# ============================================================================
# STUDENT PAGES
# ============================================================================

elif page == "📊 Student Dashboard":
    st.header("Student Dashboard")
    
    st.write(f"Welcome! This is your academic dashboard.")
    
    student_program = get_student_program(st.session_state.user_id)
    
    if student_program:
        col1, col2, col3 = st.columns(3)
        col1.metric("Program", student_program[5])
        col2.metric("Degree", student_program[7])
        col3.metric("Status", student_program[4])
    
    st.divider()
    
    enrollments = get_student_enrollments(st.session_state.user_id)
    if enrollments:
        st.subheader("Current Enrollments")
        df = pd.DataFrame(enrollments, columns=['ID', 'Student ID', 'Section ID', 'Semester ID', 'Status', 'Grade', 'GPA', 'Enrolled At', 'Course', 'Code', 'Semester'])
        st.dataframe(df[['Code', 'Course', 'Semester', 'Status', 'Grade']], use_container_width=True, hide_index=True)

elif page == "📚 My Program":
    st.header("My Program")
    
    student_program = get_student_program(st.session_state.user_id)
    
    if student_program:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Program", student_program[5])
        col2.metric("Degree", student_program[7])
        col3.metric("Status", student_program[4])
        col4.metric("Expected Graduation", student_program[6] if student_program[6] else "N/A")
        
        st.divider()
        st.subheader("Program Requirements")
        st.info("Your program requirements and course progression will appear here.")
    else:
        st.warning("You are not enrolled in a program yet. Contact your administrator.")

elif page == "📖 Current Courses":
    st.header("Current Courses")
    
    enrollments = get_student_enrollments(st.session_state.user_id)
    if enrollments:
        for enrollment in enrollments:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**{enrollment[9]}**")
                col2.write(f"Semester: {enrollment[11]}")
                col3.write(f"Status: {enrollment[4]}")
    else:
        st.info("You have no current enrollments.")

elif page == "📋 Course Catalog":
    st.header("Course Catalog")
    
    st.write("Browse available courses and their sections:")
    
    conn = sqlite3.connect('studysphere.db')
    c = conn.cursor()
    c.execute('''SELECT c.code, c.name, c.credits, c.level, GROUP_CONCAT(s.section_code) as sections
                 FROM courses c
                 LEFT JOIN sections s ON c.id = s.course_id
                 WHERE c.institution_id = ?
                 GROUP BY c.id
                 ORDER BY c.code''', (institution_id,))
    catalog_data = c.fetchall()
    conn.close()
    
    if catalog_data:
        for course in catalog_data:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{course[0]}: {course[1]}**")
                col2.write(f"Credits: {course[2]}")
                st.caption(f"Sections: {course[4] if course[4] else 'No sections available'}")

elif page == "📅 Registration":
    st.header("Course Registration")
    
    st.info("Registration for the next semester will open on the announced date. Check your email for updates.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("StudySphere Step 6 - Course & Academic Management System | Database-backed institutional structure with programs, degrees, semesters, sections, and faculty assignments.")
