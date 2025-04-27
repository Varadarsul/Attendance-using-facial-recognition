import cv2
import face_recognition
import numpy as np
import sqlite3
from datetime import datetime
import os
import time

# Initialize databases
conn_faces = sqlite3.connect("faces.db")
cursor_faces = conn_faces.cursor()
conn_logs = sqlite3.connect("logs.db")
cursor_logs = conn_logs.cursor()

# Drop existing attendance table and create new one without action column
cursor_logs.execute("DROP TABLE IF EXISTS attendance")
cursor_logs.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
""")
conn_logs.commit()

# Global variables
known_face_encodings = []
known_face_names = []
known_face_rolls = []

# Load registered faces from database
def load_registered_faces():
    global known_face_encodings, known_face_names, known_face_rolls
    cursor_faces.execute("SELECT name, roll_no, face_encoding FROM students")
    rows = cursor_faces.fetchall()
    for row in rows:
        name, roll_no, encoding = row
        face_encoding = np.array(eval(encoding))
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
        known_face_rolls.append(roll_no)

load_registered_faces()

# Add log entry
def add_log(name, roll_no):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor_logs.execute(
        "INSERT INTO attendance (name, roll_no, timestamp) VALUES (?, ?, ?)",
        (name, roll_no, timestamp)
    )
    conn_logs.commit()

# Register a new face
def register_face(name, roll_no):
    cap = cv2.VideoCapture(0)
    face_encodings = []
    
    print("Capturing samples... (Move slightly for better accuracy)")
    print("Progress: ", end="")
    for i in range(25):  # Capture 25 samples
        ret, frame = cap.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            face_encodings.append(face_encoding)
            print(".", end="", flush=True)
            time.sleep(0.3)
        else:
            print("x", end="", flush=True)
    
    print("\n")
    cap.release()
    
    if not face_encodings:
        print("No face detected. Try again.")
        return
    
    avg_encoding = np.mean(face_encodings, axis=0)
    encoding_str = str(avg_encoding.tolist())
    
    cursor_faces.execute(
        "INSERT INTO students (name, roll_no, face_encoding, date_added) VALUES (?, ?, ?, ?)",
        (name, roll_no, encoding_str, datetime.now().strftime("%Y-%m-%d"))
    )
    conn_faces.commit()
    
    known_face_encodings.append(avg_encoding)
    known_face_names.append(name)
    known_face_rolls.append(roll_no)
    
    add_log(name, roll_no)
    print(f"✅ {name} (Roll: {roll_no}) registered successfully!")

# Delete a registered face
def delete_face(roll_no):
    cursor_faces.execute("SELECT name FROM students WHERE roll_no = ?", (roll_no,))
    row = cursor_faces.fetchone()
    if row:
        name = row[0]
        cursor_faces.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn_faces.commit()
        
        index = known_face_rolls.index(roll_no)
        known_face_encodings.pop(index)
        known_face_names.pop(index)
        known_face_rolls.pop(index)
        
        print(f"❌ {name} (Roll: {roll_no}) deleted successfully!")
    else:
        print("❌ Student not found!")

# Main face detection loop
def run_recognition():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize for faster face processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            roll_no = "N/A"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                roll_no = known_face_rolls[first_match_index]
                add_log(name, roll_no)
            
            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} (Roll: {roll_no})", (left, top - 10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Display UI buttons and instructions
        cv2.putText(frame, "Press 'R' to Register | 'D' to Delete | 'Q' to Quit", (10, 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Idli Dosa Cam - Facial Recognition", frame)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('r'):
            name = input("Enter student name: ")
            roll_no = input("Enter roll number: ")
            register_face(name, roll_no)
        elif key == ord('d'):
            roll_no = input("Enter roll number to delete: ")
            delete_face(roll_no)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🚀 Idli Dosa Cam - Facial Recognition System")
    run_recognition()
    conn_faces.close()
    conn_logs.close()