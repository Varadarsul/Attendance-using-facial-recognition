let mainCameraStream = null;
let registerCameraStream = null;
let faceDetectionInterval = null;

// Camera controls
let videoStream = null;
// Registration camera controls
let registerStream = null;
let registerCanvas = document.createElement('canvas');
let registerCtx = registerCanvas.getContext('2d');

// Camera functions
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        const video = document.getElementById('video');
        video.srcObject = stream;
        videoStream = stream;
        await video.play();
        
        // Update button states
        document.getElementById('startCamera').disabled = true;
        document.getElementById('stopCamera').disabled = false;
        document.getElementById('takeAttendance').disabled = false;
        
        // Clear any previous results
        document.getElementById('attendanceResults').innerHTML = '';
        
        return true;
    } catch (err) {
        console.error('Camera Error:', err);
        showNotification('error', 'Failed to access camera. Please check permissions.');
        return false;
    }
}

// Registration camera functions
async function startRegisterCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById('registerVideo');
        registerCanvas.width = video.videoWidth || 640;
        registerCanvas.height = video.videoHeight || 480;
        video.srcObject = stream;
        registerStream = stream;
        await video.play();
        document.getElementById('startRegisterCamera').disabled = true;
        document.getElementById('stopRegisterCamera').disabled = false;
        document.getElementById('captureRegisterPhoto').disabled = false;
    } catch (err) {
        console.error('Registration camera error:', err);
        showNotification('error', 'Cannot access registration camera');
    }
}

function stopRegisterCamera() {
    if (registerStream) {
        registerStream.getTracks().forEach(t => t.stop());
        registerStream = null;
        const video = document.getElementById('registerVideo');
        video.srcObject = null;
        document.getElementById('startRegisterCamera').disabled = false;
        document.getElementById('stopRegisterCamera').disabled = true;
        document.getElementById('captureRegisterPhoto').disabled = true;
    }
}

function captureRegisterPhoto() {
    const video = document.getElementById('registerVideo');
    const canvasOverlay = document.getElementById('registerOverlay');
    registerCanvas.width = video.videoWidth;
    registerCanvas.height = video.videoHeight;
    registerCtx.drawImage(video, 0, 0, registerCanvas.width, registerCanvas.height);
    const dataURL = registerCanvas.toDataURL('image/jpeg');
    document.getElementById('registerFrame').value = dataURL.split(',')[1];
    // show preview
    const ctx = canvasOverlay.getContext('2d');
    canvasOverlay.width = registerCanvas.width;
    canvasOverlay.height = registerCanvas.height;
    ctx.drawImage(video, 0, 0, canvasOverlay.width, canvasOverlay.height);
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        const video = document.getElementById('video');
        video.srcObject = null;
        videoStream = null;
        
        // Update button states
        document.getElementById('startCamera').disabled = false;
        document.getElementById('stopCamera').disabled = true;
        document.getElementById('takeAttendance').disabled = true;
        
        // Clear overlay
        const overlay = document.getElementById('overlay');
        const ctx = overlay.getContext('2d');
        ctx.clearRect(0, 0, overlay.width, overlay.height);
    }
}

function drawFaceBox(canvas, x, y, width, height, name = '') {
    const ctx = canvas.getContext('2d');
    
    // Update canvas size to match video
    const video = canvas.previousElementSibling;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw face box
    ctx.strokeStyle = '#2ecc71';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
    
    // Draw name label with modern style
    if (name && name !== 'Unknown') {
        const padding = 8;
        const fontSize = 14;
        ctx.font = `${fontSize}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`;
        const textWidth = ctx.measureText(name).width;
        const labelHeight = fontSize + (padding * 2);
        
        // Background for text
        ctx.fillStyle = 'rgba(46, 204, 113, 0.9)';
        ctx.beginPath();
        ctx.roundRect(x, y - labelHeight - 5, textWidth + (padding * 2), labelHeight, 4);
        ctx.fill();
        
        // Text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(name, x + padding, y - padding - 5);
    }
}

// Update face detection interval timing for smoother performance
const FACE_DETECTION_INTERVAL = 50; // 50ms for more frequent updates

// Home tab camera
document.getElementById('startCamera').addEventListener('click', startCamera);

// Stop camera
document.getElementById('stopCamera').addEventListener('click', stopCamera);

// Registration camera event listeners
document.getElementById('startRegisterCamera').addEventListener('click', startRegisterCamera);
document.getElementById('stopRegisterCamera').addEventListener('click', stopRegisterCamera);
document.getElementById('captureRegisterPhoto').addEventListener('click', captureRegisterPhoto);

// Take attendance
document.getElementById('takeAttendance').addEventListener('click', async () => {
    if (!videoStream) {
        showNotification('error', 'Please start the camera first');
        return;
    }
    
    try {
        const video = document.getElementById('video');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        showNotification('info', 'Processing attendance...');
        
        const subject = document.getElementById('subjectSelect').value;
        const response = await fetch('/take_attendance', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                frame: canvas.toDataURL('image/jpeg').split(',')[1],
                subject: subject
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('success', 'Attendance recorded successfully');
            // Display recognized faces if any
            if (data.recognized_faces && data.recognized_faces.length > 0) {
                const names = data.recognized_faces.map(face => `${face.name} (${face.roll_no})`).join(', ');
                document.getElementById('attendanceResults').innerHTML = `
                    <div class="alert alert-success">
                        <i class="bi bi-check-circle-fill"></i> 
                        Attendance recorded for: ${names}
                    </div>
                `;
            }
            // Refresh subject log for current date/subject
            if (typeof loadSubjectData === 'function') loadSubjectData();
        } else {
            showNotification('error', data.message);
            document.getElementById('attendanceResults').innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle-fill"></i> 
                    ${data.message}
                </div>
            `;
        }
        
        // After successful attendance, refresh lists if available
        if (document.getElementById('attendanceList') && typeof updateAttendanceList === 'function') {
            updateAttendanceList();
        }
        if (document.getElementById('activity-list') && typeof loadActivityData === 'function') {
            loadActivityData();
        }
        // Automatically stop the camera after successful attendance
        document.getElementById('stopCamera').click();
    } catch (error) {
        console.error('Error:', error);
        showNotification('error', 'Failed to record attendance');
    }
});

// Handle tab switching
document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(tab => {
    tab.addEventListener('show.bs.tab', (event) => {
        // Stop camera when switching tabs
        if (videoStream) {
            document.getElementById('stopCamera').click();
        }
    });
});

// Register tab camera controls
document.getElementById('startRegisterCamera').addEventListener('click', async () => {
    const video = document.getElementById('registerCamera');
    registerCameraStream = await startCamera(video);
    
    if (registerCameraStream) {
        document.getElementById('startRegisterCamera').disabled = true;
        document.getElementById('stopRegisterCamera').disabled = false;
        document.getElementById('registerButton').disabled = false;
    }
});

document.getElementById('stopRegisterCamera').addEventListener('click', () => {
    const video = document.getElementById('registerCamera');
    stopCamera(registerCameraStream, video);
    registerCameraStream = null;
    document.getElementById('startRegisterCamera').disabled = false;
    document.getElementById('stopRegisterCamera').disabled = true;
    document.getElementById('registerButton').disabled = true;
});

function getVideoFrame(videoElement) {
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0);
    return canvas.toDataURL('image/jpeg').split(',')[1];
}

// Register form submission
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('studentName').value;
    const rollNo = document.getElementById('rollNo').value;
    const frame = document.getElementById('registerFrame').value;
    if (!frame) {
        showNotification('error', 'Please capture a photo before registering');
        return;
    }

    if (!name || !rollNo) {
        showNotification('error', 'Please fill in all fields');
        return;
    }
    
    try {
        showNotification('info', 'Starting registration process...');
        
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, roll_no: rollNo, frame: frame })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification('success', data.message);
            document.getElementById('registerModal').querySelector('.btn-close').click();
            loadStudents();
        } else {
            showNotification('error', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('error', 'Failed to register student');
    }
});

// Search attendance
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
        const response = await fetch('/search_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                date: document.getElementById('searchDate').value,
                name: document.getElementById('searchName').value,
                roll_no: document.getElementById('searchRollNo').value
            })
        });

        const data = await response.json();
        if (data.success) {
            const tbody = document.getElementById('attendanceTableBody');
            tbody.innerHTML = '';
            if (data.results.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center">No records found</td>
                    </tr>
                `;
            } else {
                data.results.forEach(result => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${result.name}</td>
                            <td>${result.roll_no}</td>
                            <td>${result.timestamp}</td>
                        </tr>
                    `;
                });
            }
        }
    } catch (error) {
        console.error('Error searching attendance:', error);
        alert('Error searching attendance. Please try again.');
    }
});

// Load students list
function loadStudents() {
    fetch('/get_students')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.getElementById('studentsList');
                tbody.innerHTML = '';
                data.results.forEach(student => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${student.name}</td>
                            <td>${student.roll_no}</td>
                            <td>${student.date_added}</td>
                            <td>
                                <button class="btn btn-sm btn-danger" onclick="deleteStudent('${student.roll_no}')">
                                    <i class="bi bi-trash-fill"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                });
                // Update student count badge
                const countEl = document.getElementById('studentCount');
                if (countEl) countEl.innerText = data.results.length;
            }
        })
        .catch(error => {
            console.error('Error loading students:', error);
            showNotification('error', 'Failed to load students list');
        });
}

// Update student
document.getElementById('updateStudent').addEventListener('click', async () => {
    try {
        const response = await fetch('/update_student', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                old_roll_no: document.getElementById('oldRollNo').value,
                name: document.getElementById('updateName').value,
                roll_no: document.getElementById('updateRollNo').value
            })
        });

        const data = await response.json();
        if (data.success) {
            alert(data.message);
            bootstrap.Modal.getInstance(document.getElementById('updateModal')).hide();
            loadStudents();
        }
    } catch (error) {
        console.error('Error updating student:', error);
        alert('Error updating student. Please try again.');
    }
});

function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-circle'}-fill"></i>
        <div>${message}</div>
    `;
    document.querySelector('.notification-container').appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Activity panel functionality
function loadActivityData() {
    const date = document.getElementById('activity-date').value;
    
    fetch(`/get_activity?date=${date}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('activity-list');
            tbody.innerHTML = '';
            
            if (data.success && data.activity) {
                data.activity.forEach(record => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${record.name}</td>
                            <td>${record.roll_no}</td>
                            <td>${new Date(record.timestamp).toLocaleTimeString()}</td>
                            <td><span class="badge bg-success">Present</span></td>
                        </tr>
                    `;
                });
                
                if (data.activity.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center">No activity recorded for this date</td>
                        </tr>
                    `;
                }
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-danger">Error loading activity data</td>
                    </tr>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('error', 'Failed to load activity data');
        });
}

// Initialize activity data on tab show (admin anchor)
const activityAnchor = document.querySelector('a[href="#activity"]');
if (activityAnchor) {
    activityAnchor.addEventListener('shown.bs.tab', () => {
        loadActivityData();
    });
}

// Teacher panel: bind Activity pill to refresh activity log
const activityPillBtn = document.querySelector('button[data-bs-target="#activity"]');
if (activityPillBtn) {
    activityPillBtn.addEventListener('shown.bs.tab', loadActivityData);
    activityPillBtn.addEventListener('click', loadActivityData);
}

// Bind teacher pill show event for Activity tab
const teacherActivityPills = document.querySelectorAll('[data-bs-toggle="pill"][data-bs-target="#activity"]');
teacherActivityPills.forEach(pill => {
    pill.addEventListener('shown.bs.tab', loadActivityData);
});

// Also load activity if teacher panel is present
if (document.getElementById('activity-list')) {
    loadActivityData();
}

// On page load, if teacher panel has activity table, load it
if (document.getElementById('activity-list')) {
    loadActivityData();
}

// Initialize date input with today's date
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('activity-date').value = today;
    
    // Load initial data
    loadStudents();
    loadActivityData();
    
    // Handle tab changes
    document.querySelectorAll('[data-bs-toggle="pill"]').forEach(pill => {
        pill.addEventListener('shown.bs.tab', () => {
            // Stop camera when switching tabs
            if (videoStream) {
                stopCamera();
            }
            // Refresh activity on teacher panel
            if (pill.getAttribute('data-bs-target') === '#activity') {
                loadActivityData();
            }
        });
    });
});

// On page load, if teacher panel has student table, load students
if (document.getElementById('studentsList')) {
    loadStudents();
}

// Bind student tab show event to reload students
const studentTabBtns = document.querySelectorAll('button[data-bs-toggle="pill"][data-bs-target="#students"]');
studentTabBtns.forEach(btn => btn.addEventListener('shown.bs.tab', loadStudents));

// Unified tab change handler for Students and Activity
document.querySelectorAll('[data-bs-toggle="pill"]').forEach(pill => {
    pill.addEventListener('shown.bs.tab', () => {
        const target = pill.getAttribute('data-bs-target');
        if (target === '#students') loadStudents();
        if (target === '#activity') loadActivityData();
    });
});

// After DOM content loaded, bind UI interactions
document.addEventListener('DOMContentLoaded', () => {
    // Subject dropdown interactions (works for any dropdown)
    const subjectItems = document.querySelectorAll('.subject-item');
    subjectItems.forEach(item => {
        item.addEventListener('click', event => {
            event.preventDefault();
            const subj = item.getAttribute('data-subject');
            // Update hidden select
            const selectEl = document.getElementById('subjectSelect');
            if (selectEl) selectEl.value = subj;
            // Update the corresponding dropdown button text
            const dropdown = item.closest('.dropdown');
            if (dropdown) {
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) toggle.textContent = `Subject: ${subj}`;
            }
            loadSubjectData();
        });
    });

    // Subject date picker change
    const datePicker = document.getElementById('subject-date');
    if (datePicker) {
        datePicker.addEventListener('change', loadSubjectData);
    }
});

// Bind subject date picker if present
const subjectDatePicker = document.getElementById('subject-date');
if (subjectDatePicker) {
    subjectDatePicker.addEventListener('change', loadSubjectData);
}

// Bind Subjects tab activation to refresh log
const subjectsTabBtn = document.querySelector('[data-bs-target="#subjects"]');
if (subjectsTabBtn) {
    subjectsTabBtn.addEventListener('shown.bs.tab', () => {
        // Initialize date picker value same as activity
        const today = new Date().toISOString().split('T')[0];
        if (subjectDatePicker) subjectDatePicker.value = today;
        loadSubjectData();
    });
}

// Delete Student
function deleteStudent(rollNo) {
    if (confirm('Are you sure you want to delete this student?')) {
        fetch('/delete_student', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ roll_no: rollNo })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('success', 'Student deleted successfully');
                loadStudents();
            } else {
                showNotification('error', data.message || 'Failed to delete student');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('error', 'Failed to delete student');
        });
    }
}

// Subject log functionality
function loadSubjectData() {
    // Use selected date or default to today
    let date = document.getElementById('subject-date').value;
    if (!date) date = new Date().toISOString().split('T')[0];
    const subject = document.getElementById('subjectSelect').value;
    console.log(`Loading subject logs for ${date}, ${subject}`);
    fetch(`/get_subject_log?date=${date}&subject=${subject}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('subject-list');
            tbody.innerHTML = '';
            if (data.success && data.subject_logs) {
                data.subject_logs.forEach(rec => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${rec.subject}</td>
                            <td>${rec.roll_no}</td>
                            <td>${new Date(rec.timestamp).toLocaleTimeString()}</td>
                            <td><span class="badge bg-success">Present</span></td>
                        </tr>
                    `;
                });
                if (data.subject_logs.length === 0) {
                    tbody.innerHTML = `
                        <tr><td colspan="4" class="text-center">No records for this date/subject</td></tr>
                    `;
                }
            } else {
                tbody.innerHTML = `
                    <tr><td colspan="4" class="text-center text-danger">Error loading subject logs</td></tr>
                `;
            }
        })
        .catch(err => {
            console.error('Error loading subject logs:', err);
            showNotification('error', 'Failed to load subject logs');
        });
}

// Subject button click handlers
const subjectButtons = document.querySelectorAll('.subject-btn');
if (subjectButtons.length) {
    subjectButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const subj = btn.getAttribute('data-subject');
            // Update hidden select and display
            const select = document.getElementById('subjectSelect');
            const display = document.getElementById('subjectDisplay');
            if (select) select.value = subj;
            if (display) display.textContent = `Subject: ${subj}`;
            // Toggle active state
            subjectButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
    // Initialize first button as active
    subjectButtons[0].classList.add('active');
}