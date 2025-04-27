---

# Attendance System Using Facial Recognition

This project is an automated attendance system developed in **Python**, where attendance is marked by recognizing faces from an image. It uses image processing and facial recognition techniques to detect students and record their presence.

## Features

- **Student Registration**: Add student details and capture their facial images.
- **Model Training**: Train the system on the collected student images.
- **Attendance Marking**: Upload a group photo or capture an image to mark attendance automatically.
- **Attendance Records**: Store and view attendance records subject-wise.
- **User Roles**:  
  - **Admin**: Manage users and students.  
  - **Teacher**: Register students, mark attendance, and view attendance reports.

## Tech Stack

- **Frontend**: Tkinter (for desktop application) / HTML, CSS (for web application - optional)
- **Backend**: Python
- **Libraries/Frameworks**:
  - OpenCV (`cv2`) – for image capturing and face detection
  - face_recognition – for face encoding and matching
  - NumPy
  - Pandas – for managing CSV attendance records
  - Tkinter – for GUI (if desktop app)
  - Flask (optional) – for web-based version

## How It Works

1. **Student Registration**:
   - Teacher/Admin captures multiple images of each student.
   - These images are stored in a dataset folder.

2. **Model Training**:
   - The system generates face encodings for each student based on the dataset.

3. **Attendance Marking**:
   - Upload or capture a classroom/group photo.
   - The system detects faces, compares them with trained encodings, and marks attendance.

4. **Attendance Storage**:
   - Attendance is saved in CSV files, with date, subject, and present/absent status.

```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Varadarsul/Attendance-using-facial-recognition.git
   cd Attendance-using-facial-recognition
   ```

2. **Install required libraries**
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not available, install manually:
   ```bash
   pip install opencv-python face_recognition numpy pandas
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```

## Requirements

- Python 3.7+
- OpenCV
- face_recognition library
- NumPy
- Pandas
- Tkinter (usually pre-installed with Python)

## Screenshots

### Registration Page
## Screenshots

### User Management
![User Management](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/user%20management.png?raw=true)

### Admin Panel
![Admin Panel](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/admin%20panel.png?raw=true)

### Attendance Report
![Attendance Report](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/attendance%20report.png?raw=true)

### Input Image
![Input Image](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/input%20image.png?raw=true)

### Login Page
![Login Page](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/login.png?raw=true)

### Marked Attendance
![Marked Attendance](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/marked%20attendance%20of%20input%20image.png?raw=true)

### Register Student
![Register Student](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/register%20student.png?raw=true)

### Take Attendance
![Take Attendance](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/take%20attendance.png?raw=true)

### Upload Image for Marking Attendance
![Upload Image](https://github.com/Varadarsul/Attendance-using-facial-recognition/blob/main/upload%20image%20for%20marking%20attendance.png?raw=true)


## Future Improvements

- Add email/SMS notifications for attendance updates.
- Improve face detection accuracy with advanced models like MTCNN or RetinaFace.
- Support real-time camera-based attendance.
- Add database integration (e.g., Firebase, MySQL) for storing student and attendance data.

## Acknowledgments

- [face_recognition library](https://github.com/ageitgey/face_recognition)
- [OpenCV documentation](https://docs.opencv.org/)


