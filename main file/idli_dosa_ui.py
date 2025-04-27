import sys
import cv2
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QMessageBox, QComboBox, QDateEdit, QDialog,
                            QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import face_recognition
import numpy as np
from idli_dosa_cam import register_face, delete_face, add_log, known_face_encodings, known_face_names, known_face_rolls

class UpdateStudentDialog(QDialog):
    def __init__(self, parent=None, name="", roll_no=""):
        super().__init__(parent)
        self.setWindowTitle("Update Student Details")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(name)
        self.roll_input = QLineEdit(roll_no)
        
        layout.addRow("Name:", self.name_input)
        layout.addRow("Roll Number:", self.roll_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Idli Dosa Cam - Facial Recognition System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize database connections
        self.conn_faces = sqlite3.connect("faces.db")
        self.cursor_faces = self.conn_faces.cursor()
        self.conn_logs = sqlite3.connect("logs.db")
        self.cursor_logs = self.conn_logs.cursor()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_home_tab()
        self.create_register_tab()
        self.create_attendance_tab()
        self.create_admin_tab()
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Load initial data
        self.load_students()
        
    def create_home_tab(self):
        home_tab = QWidget()
        layout = QVBoxLayout()
        
        # Camera display
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        layout.addWidget(self.camera_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.take_attendance_button = QPushButton("Take Attendance")
        self.take_attendance_button.clicked.connect(self.take_attendance)
        button_layout.addWidget(self.take_attendance_button)
        
        layout.addLayout(button_layout)
        home_tab.setLayout(layout)
        self.tabs.addTab(home_tab, "Home")
        
    def create_register_tab(self):
        register_tab = QWidget()
        layout = QVBoxLayout()
        
        # Registration form
        form_layout = QVBoxLayout()
        
        # User type selection
        self.user_type = QComboBox()
        self.user_type.addItems(["Student", "Teacher"])
        form_layout.addWidget(QLabel("User Type:"))
        form_layout.addWidget(self.user_type)
        
        # Name input
        self.name_input = QLineEdit()
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)
        
        # Roll number input
        self.roll_input = QLineEdit()
        form_layout.addWidget(QLabel("Roll Number:"))
        form_layout.addWidget(self.roll_input)
        
        # Camera preview
        self.register_camera_label = QLabel()
        self.register_camera_label.setAlignment(Qt.AlignCenter)
        self.register_camera_label.setMinimumSize(640, 480)
        form_layout.addWidget(self.register_camera_label)
        
        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)
        form_layout.addWidget(self.register_button)
        
        layout.addLayout(form_layout)
        register_tab.setLayout(layout)
        self.tabs.addTab(register_tab, "Register")
        
    def create_attendance_tab(self):
        attendance_tab = QWidget()
        layout = QVBoxLayout()
        
        # Search filters
        filter_layout = QHBoxLayout()
        
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.date_filter)
        
        self.name_filter = QLineEdit()
        filter_layout.addWidget(QLabel("Name:"))
        filter_layout.addWidget(self.name_filter)
        
        self.roll_filter = QLineEdit()
        filter_layout.addWidget(QLabel("Roll Number:"))
        filter_layout.addWidget(self.roll_filter)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_attendance)
        filter_layout.addWidget(self.search_button)
        
        layout.addLayout(filter_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(3)
        self.attendance_table.setHorizontalHeaderLabels(["Name", "Roll Number", "Timestamp"])
        layout.addWidget(self.attendance_table)
        
        attendance_tab.setLayout(layout)
        self.tabs.addTab(attendance_tab, "Attendance")
        
    def create_admin_tab(self):
        admin_tab = QWidget()
        layout = QVBoxLayout()
        
        # Student management
        student_layout = QVBoxLayout()
        
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(3)
        self.student_table.setHorizontalHeaderLabels(["Name", "Roll Number", "Date Added"])
        student_layout.addWidget(self.student_table)
        
        # Update student button
        self.update_student_button = QPushButton("Update Student Details")
        self.update_student_button.clicked.connect(self.update_student)
        student_layout.addWidget(self.update_student_button)
        
        # Delete student button
        self.delete_student_button = QPushButton("Delete Student")
        self.delete_student_button.clicked.connect(self.delete_student)
        student_layout.addWidget(self.delete_student_button)
        
        layout.addLayout(student_layout)
        admin_tab.setLayout(layout)
        self.tabs.addTab(admin_tab, "Admin")
        
    def start_camera(self):
        if not self.timer.isActive():
            self.timer.start(30)
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
    def stop_camera(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Display frame
            if self.tabs.currentIndex() == 0:  # Home tab
                self.camera_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                    self.camera_label.size(), Qt.KeepAspectRatio))
            elif self.tabs.currentIndex() == 1:  # Register tab
                self.register_camera_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                    self.register_camera_label.size(), Qt.KeepAspectRatio))
                    
    def take_attendance(self):
        ret, frame = self.camera.read()
        if ret:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    roll_no = known_face_rolls[first_match_index]
                    add_log(name, roll_no)
                    QMessageBox.information(self, "Success", f"Attendance marked for {name}")
                    
    def register_user(self):
        name = self.name_input.text()
        roll_no = self.roll_input.text()
        user_type = self.user_type.currentText()
        
        if not name or not roll_no:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        try:
            register_face(name, roll_no)
            QMessageBox.information(self, "Success", f"{user_type} registered successfully!")
            self.name_input.clear()
            self.roll_input.clear()
            self.load_students()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def search_attendance(self):
        date = self.date_filter.date().toString("yyyy-MM-dd")
        name = self.name_filter.text()
        roll_no = self.roll_filter.text()
        
        query = "SELECT name, roll_no, timestamp FROM attendance WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if roll_no:
            query += " AND roll_no LIKE ?"
            params.append(f"%{roll_no}%")
        if date:
            query += " AND date(timestamp) = ?"
            params.append(date)
            
        self.cursor_logs.execute(query, params)
        rows = self.cursor_logs.fetchall()
        
        self.attendance_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.attendance_table.setItem(i, j, QTableWidgetItem(str(value)))
                
    def update_student(self):
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            name = self.student_table.item(selected_row, 0).text()
            roll_no = self.student_table.item(selected_row, 1).text()
            
            dialog = UpdateStudentDialog(self, name, roll_no)
            if dialog.exec_() == QDialog.Accepted:
                new_name = dialog.name_input.text()
                new_roll_no = dialog.roll_input.text()
                
                if not new_name or not new_roll_no:
                    QMessageBox.warning(self, "Error", "Please fill in all fields")
                    return
                    
                try:
                    # Update in database
                    self.cursor_faces.execute(
                        "UPDATE students SET name = ?, roll_no = ? WHERE roll_no = ?",
                        (new_name, new_roll_no, roll_no)
                    )
                    self.conn_faces.commit()
                    
                    # Update in memory
                    index = known_face_rolls.index(roll_no)
                    known_face_names[index] = new_name
                    known_face_rolls[index] = new_roll_no
                    
                    QMessageBox.information(self, "Success", "Student details updated successfully!")
                    self.load_students()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
            
    def delete_student(self):
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            roll_no = self.student_table.item(selected_row, 1).text()
            try:
                delete_face(roll_no)
                QMessageBox.information(self, "Success", "Student deleted successfully!")
                self.load_students()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def load_students(self):
        self.cursor_faces.execute("SELECT name, roll_no, date_added FROM students")
        rows = self.cursor_faces.fetchall()
        
        self.student_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.student_table.setItem(i, j, QTableWidgetItem(str(value)))
                
    def closeEvent(self, event):
        self.camera.release()
        self.conn_faces.close()
        self.conn_logs.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 