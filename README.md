Attendance System Using Facial Recognition
This project is an automated attendance system developed in Python, where attendance is marked by recognizing faces from an image. It uses image processing and facial recognition techniques to detect students and record their presence.

Features
Student Registration: Add student details and capture their facial images.

Model Training: Train the system on the collected student images.

Attendance Marking: Upload a group photo or capture an image to mark attendance automatically.

Attendance Records: Store and view attendance records subject-wise.

User Roles:

Admin: Manage users and students.

Teacher: Register students, mark attendance, and view attendance reports.

Tech Stack
Frontend: Tkinter (for desktop application) / HTML, CSS (for web application - optional)

Backend: Python

Libraries/Frameworks:

OpenCV (cv2) – for image capturing and face detection

face_recognition – for face encoding and matching

NumPy

Pandas – for managing CSV attendance records

Tkinter – for GUI (if desktop app)

Flask (optional) – for web-based version

How It Works
Student Registration:

Teacher/Admin captures multiple images of each student.

These images are stored in a dataset folder.

Model Training:

The system generates face encodings for each student based on the dataset.

Attendance Marking:

Upload or capture a classroom/group photo.

The system detects faces, compares them with trained encodings, and marks attendance.

Attendance Storage:

Attendance is saved in CSV files, with date, subject, and present/absent status.
