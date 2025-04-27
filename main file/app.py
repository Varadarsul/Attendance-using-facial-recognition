from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import cv2
import face_recognition
import numpy as np
import sqlite3
from datetime import datetime
import os
import base64
from io import BytesIO
import json
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Initialize databases
def get_db_connection():
    conn = sqlite3.connect('faces.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_logs_connection():
    conn = sqlite3.connect('logs.db')
    conn.row_factory = sqlite3.Row
    return conn

# Global variables
known_face_encodings = []
known_face_names = []
known_face_rolls = []

def load_registered_faces():
    global known_face_encodings, known_face_names, known_face_rolls
    conn = get_db_connection()
    rows = conn.execute('SELECT name, roll_no, face_encoding FROM students').fetchall()
    for row in rows:
        name = row['name']
        roll_no = row['roll_no']
        encoding = json.loads(row['face_encoding'])
        known_face_encodings.append(np.array(encoding))
        known_face_names.append(name)
        known_face_rolls.append(roll_no)
    conn.close()

load_registered_faces()

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Drop existing users table
    c.execute("DROP TABLE IF EXISTS users")
    
    # Create new users table with additional fields
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL)''')
    
    # Add default admin user
    c.execute("""
        INSERT INTO users (username, password, role, name, email)
        VALUES (?, ?, ?, ?, ?)
    """, ('admin', 'admin123', 'admin', 'Administrator', 'admin@mgm.edu'))
    
    # Add default teacher
    c.execute("""
        INSERT INTO users (username, password, role, name, email)
        VALUES (?, ?, ?, ?, ?)
    """, ('teacher', 'teacher123', 'teacher', 'Default Teacher', 'teacher@mgm.edu'))
    
    conn.commit()
    conn.close()

init_db()

# Initialize logs database
from sqlite3 import connect as _sqlite3_connect  # local alias for logs initialization

def init_logs_db():
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    # Create attendance table if it doesn't exist, preserving existing records
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  roll_no TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  subject TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_logs_db()

def add_log(name, roll_no, subject):
    conn = get_logs_connection()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO attendance (name, roll_no, timestamp, subject) VALUES (?, ?, ?, ?)",
        (name, roll_no, timestamp, subject)
    )
    conn.commit()
    conn.close()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def login():
    if 'user' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('teacher_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?",
             (username, password, role))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = username
        session['role'] = role
        return jsonify({
            'success': True,
            'redirect': url_for('admin_dashboard' if role == 'admin' else 'teacher_dashboard')
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if session['role'] != 'admin':
        return redirect(url_for('teacher_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if session['role'] not in ['teacher', 'admin']:
        return redirect(url_for('index'))
    return render_template('teacher_dashboard.html')

# Face detection endpoint
@app.route('/detect_faces', methods=['POST'])
@login_required
def detect_faces():
    try:
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({'success': False, 'message': 'No image data received'})

        # Decode base64 image
        image_data = base64.b64decode(data['frame'])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        faces = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces from database
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            
            faces.append({
                'top': top,
                'right': right,
                'bottom': bottom,
                'left': left,
                'name': name
            })
        
        return jsonify({
            'success': True,
            'faces': faces
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Take attendance endpoint
@app.route('/take_attendance', methods=['POST'])
@login_required
def take_attendance():
    try:
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({'success': False, 'message': 'No image data received'})

        # Decode base64 image
        image_data = base64.b64decode(data['frame'])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'success': False, 'message': 'Invalid image data'})

        # Convert to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return jsonify({'success': False, 'message': 'No face detected'})
            
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        attendance_recorded = False
        recognized_faces = []
        subject = data.get('subject', 'Unknown')
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                roll_no = known_face_rolls[first_match_index]
                
                # Record attendance
                add_log(name, roll_no, subject)
                attendance_recorded = True
                recognized_faces.append({
                    'name': name,
                    'roll_no': roll_no
                })
        
        if attendance_recorded:
            return jsonify({
                'success': True,
                'message': 'Attendance recorded successfully',
                'recognized_faces': recognized_faces
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No registered faces were recognized'
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error recording attendance'
        })

# Register endpoint
@app.route('/register', methods=['POST'])
@login_required
def register():
    # Allow both admin and teacher to register students
    if session['role'] not in ['admin', 'teacher']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        data = request.get_json()
        name = data.get('name')
        roll_no = data.get('roll_no')
        frame_b64 = data.get('frame')

        if not name or not roll_no:
            return jsonify({'success': False, 'message': 'Name and roll number are required'})

        # Decode base64 image from client
        if not frame_b64:
            return jsonify({'success': False, 'message': 'No image data provided'})
        image_data = base64.b64decode(frame_b64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify({'success': False, 'message': 'Invalid image data'})
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return jsonify({'success': False, 'message': 'No face detected. Please try again.'})
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        # Use first face encoding
        encoding = face_encodings[0]

        # Save to database
        encoding_str = json.dumps(encoding.tolist())
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO students (name, roll_no, face_encoding, date_added) VALUES (?, ?, ?, ?)',
            (name, roll_no, encoding_str, datetime.now().strftime('%Y-%m-%d'))
        )
        conn.commit()
        conn.close()

        # Update global variables
        known_face_encodings.append(encoding)
        known_face_names.append(name)
        known_face_rolls.append(roll_no)
        # Add initial attendance log
        add_log(name, roll_no, 'Unknown')
        return jsonify({'success': True, 'message': f'Successfully registered {name}'})
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/search_attendance', methods=['POST'])
def search_attendance():
    data = request.json
    date = data.get('date')
    name = data.get('name')
    roll_no = data.get('roll_no')
    
    conn = get_logs_connection()
    query = 'SELECT name, roll_no, timestamp FROM attendance WHERE 1=1'
    params = []
    
    if date:
        query += ' AND date(timestamp) = ?'
        params.append(date)
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if roll_no:
        query += ' AND roll_no LIKE ?'
        params.append(f'%{roll_no}%')
    
    rows = conn.execute(query, params).fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    
    return jsonify({'success': True, 'results': results})

@app.route('/get_students')
def get_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT name, roll_no, date_added FROM students').fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return jsonify({'success': True, 'results': results})

@app.route('/update_student', methods=['POST'])
def update_student():
    data = request.json
    old_roll_no = data['old_roll_no']
    new_name = data['name']
    new_roll_no = data['roll_no']
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name = ?, roll_no = ? WHERE roll_no = ?',
        (new_name, new_roll_no, old_roll_no)
    )
    conn.commit()
    conn.close()
    
    # Update global variables
    index = known_face_rolls.index(old_roll_no)
    known_face_names[index] = new_name
    known_face_rolls[index] = new_roll_no
    
    return jsonify({'success': True, 'message': 'Student details updated successfully'})

@app.route('/delete_student', methods=['POST'])
def delete_student():
    roll_no = request.json['roll_no']
    
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE roll_no = ?', (roll_no,))
    conn.commit()
    conn.close()
    
    # Update global variables
    index = known_face_rolls.index(roll_no)
    known_face_encodings.pop(index)
    known_face_names.pop(index)
    known_face_rolls.pop(index)
    
    return jsonify({'success': True, 'message': 'Student deleted successfully'})

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if not all([name, email, username, password, role]):
            return jsonify({'success': False, 'message': 'All fields are required'})

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if username already exists
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists'})

        # Add new user
        c.execute("""
            INSERT INTO users (username, password, role, name, email)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, role, name, email))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_users')
@login_required
def get_users():
    if session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM users")
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    if session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        username = data.get('username')
        
        if username == session['user']:
            return jsonify({'success': False, 'message': 'Cannot delete your own account'})
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_activity')
@login_required
def get_activity():
    try:
        date = request.args.get('date')
        conn = get_logs_connection()
        query = 'SELECT name, roll_no, timestamp FROM attendance WHERE date(timestamp) = ?'
        rows = conn.execute(query, (date,)).fetchall()
        activity = [dict(row) for row in rows]
        conn.close()
        return jsonify({'success': True, 'activity': activity})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_percentage')
@login_required
def get_percentage():
    try:
        month = request.args.get('month')
        year = request.args.get('year')
        
        conn = get_logs_connection()
        # Get all students from faces database
        students_conn = get_db_connection()
        students = students_conn.execute('SELECT name, roll_no FROM students').fetchall()
        
        percentage_data = []
        for student in students:
            # Count total working days (excluding weekends)
            total_days_query = """
                SELECT COUNT(DISTINCT date(timestamp)) as total_days 
                FROM attendance 
                WHERE strftime('%m', timestamp) = ? 
                AND strftime('%Y', timestamp) = ?
            """
            total_days = conn.execute(total_days_query, (month.zfill(2), year)).fetchone()['total_days']
            
            # Count days present for this student
            present_days_query = """
                SELECT COUNT(DISTINCT date(timestamp)) as present_days 
                FROM attendance 
                WHERE roll_no = ? 
                AND strftime('%m', timestamp) = ? 
                AND strftime('%Y', timestamp) = ?
            """
            present_days = conn.execute(present_days_query, 
                                     (student['roll_no'], month.zfill(2), year)).fetchone()['present_days']
            
            # Calculate percentage
            percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            percentage_data.append({
                'name': student['name'],
                'roll_no': student['roll_no'],
                'total_days': total_days,
                'present_days': present_days,
                'percentage': percentage
            })
        
        conn.close()
        students_conn.close()
        return jsonify({'success': True, 'percentage': percentage_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_today_attendance')
@login_required
def get_today_attendance():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_logs_connection()
        query = 'SELECT name, roll_no, timestamp FROM attendance WHERE date(timestamp) = ?'
        rows = conn.execute(query, (today,)).fetchall()
        attendance = [dict(row) for row in rows]
        conn.close()
        return jsonify({'success': True, 'attendance': attendance})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_subject_log')
@login_required
def get_subject_log():
    date = request.args.get('date')
    subject = request.args.get('subject')
    conn = get_logs_connection()
    # Use strftime to ensure proper date comparison
    query = "SELECT subject, roll_no, timestamp FROM attendance WHERE strftime('%Y-%m-%d', timestamp) = ? AND subject = ?"
    rows = conn.execute(query, (date, subject)).fetchall()
    results = [dict(row) for row in rows]
    print(f"get_subject_log: date={date}, subject={subject}, count={len(results)}")
    conn.close()
    return jsonify({'success': True, 'subject_logs': results})

@app.route('/upload_attendance', methods=['POST'])
@login_required
def upload_attendance():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    subject = request.form.get('subject', '')
    
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Read the image file
    img = face_recognition.load_image_file(file)
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)
    
    recognized_students = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            roll_no = known_face_rolls[first_match_index]
            recognized_students.append({'name': name, 'roll_no': roll_no})
            add_log(name, roll_no, subject)
    
    return jsonify({
        'success': True,
        'recognized_students': recognized_students,
        'total_faces': len(face_locations),
        'recognized_faces': len(recognized_students)
    })

if __name__ == '__main__':
    app.run(debug=True) 