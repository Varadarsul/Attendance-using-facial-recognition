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
![User Management](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/user%20management.png?token=BCRWHCABP36TDJ6L3Y6WTSLIBYG4U)

![Admin Panel](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/admin%20panel.png?token=BCRWHCBZHR2HXJHENZQVUSLIBYG4S)

![Attendance report](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/attendance%20report.png?token=BCRWHCFAFYOVE5YYJQBAVTTIBYG4S)
## Screenshots
![Input Image](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/input%20image.png?token=BCRWHCGMWGDOJBPKKBC3GV3IBYG4S)
## Screenshots
![Login Page](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/login.png?token=BCRWHCAMO4NKAYMWAQVRZJTIBYG4U)
## Screenshots
![Marked Attendance](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/marked%20attendance%20of%20input%20image.png?token=BCRWHCCTIZFB3D2NKZWMWFDIBYG4U)
## Screenshots
![Register student](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/register%20student.png?token=BCRWHCBO6JSBDUWAZ6DWTBLIBYG4U)
## Screenshots
![Take Attendance](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/take%20attendance.png?token=BCRWHCA6K7MIH6RFH3TXVO3IBYG4U)
## Screenshots
![Upload Image](https://raw.githubusercontent.com/Varadarsul/Attendance-using-facial-recognition/79eb1ae2b44373faefe56aebf0f5cbbb523b5167/upload%20image%20for%20marking%20attendance.png?token=BCRWHCF3MFPGKWWVT6ZEP7LIBYG4U)

## Future Improvements

- Add email/SMS notifications for attendance updates.
- Improve face detection accuracy with advanced models like MTCNN or RetinaFace.
- Support real-time camera-based attendance.
- Add database integration (e.g., Firebase, MySQL) for storing student and attendance data.

## Acknowledgments

- [face_recognition library](https://github.com/ageitgey/face_recognition)
- [OpenCV documentation](https://docs.opencv.org/)


