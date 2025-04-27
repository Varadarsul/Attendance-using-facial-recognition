import sqlite3
from datetime import datetime

# Initialize databases (faces + logs)
def init_databases():
    # Faces database
    conn_faces = sqlite3.connect("faces.db")
    cursor_faces = conn_faces.cursor()
    cursor_faces.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            face_encoding TEXT NOT NULL,
            date_added TEXT NOT NULL
        )
    """)
    conn_faces.commit()
    conn_faces.close()

    # Logs database
    conn_logs = sqlite3.connect("logs.db")
    cursor_logs = conn_logs.cursor()
    cursor_logs.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_no TEXT,
            action TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn_logs.commit()
    conn_logs.close()

init_databases()