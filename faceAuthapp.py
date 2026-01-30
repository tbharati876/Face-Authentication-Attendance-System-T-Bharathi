# 1. Install Libraries
!pip install flask-cors pyngrok face_recognition opencv-python-headless pytz

import os
import cv2
import face_recognition
import numpy as np
import datetime
import base64
import pytz
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pyngrok import ngrok

# 2. Attendance Configuration
KNOWN_FACES_DIR = "known_faces"
LOG_DIR = "attendance_photos"
IST = pytz.timezone('Asia/Kolkata')

os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

NGROK_TOKEN = "36mSHpSl4DWk4VZO6zTudKO3Piz_2ReYvKNYAz8zPKgUJRMxH"
ngrok.set_auth_token(NGROK_TOKEN)

app = Flask(__name__)
CORS(app)

known_face_encodings = []
known_face_names = []

def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings, known_face_names = [], []
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            img = face_recognition.load_image_file(f"{KNOWN_FACES_DIR}/{filename}")
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])

# 3. Web UI Interface
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Face Authentication Attendance System App</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.25/jspdf.plugin.autotable.min.js"></script>
    <style>
        :root { --bg: #f8f9fa; --card: #ffffff; --text: #212529; --primary: #0d6efd; }
        [data-theme="dark"] { --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --primary: #03dac6; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 20px; transition: 0.3s; }
        .card { background: var(--card); padding: 2rem; border-radius: 1rem; display: inline-block; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 90%; max-width: 600px; }
        video { width: 100%; max-width: 400px; border-radius: 10px; border: 3px solid var(--primary); transform: scaleX(-1); }
        .hidden { display: none; }
        button { padding: 12px 24px; margin: 8px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
        .btn-reg { background: #198754; color: white; }
        .btn-in { background: #0d6efd; color: white; }
        .btn-out { background: #dc3545; color: white; }
        .btn-pdf { background: #6c757d; color: white; width: 100%; margin-top: 20px; }
        table { width: 100%; margin-top: 2rem; border-collapse: collapse; background: var(--card); }
        th, td { border: 1px solid #444; padding: 12px; text-align: center; }
        .log-img { width: 50px; height: 50px; object-fit: cover; border-radius: 4px; }
    </style>
</head>
<body data-theme="dark">
    <button onclick="document.body.getAttribute('data-theme')=='dark'?document.body.setAttribute('data-theme','light'):document.body.setAttribute('data-theme','dark')" style="position:fixed; top:10px; right:10px;">🌓 Theme</button>

    <div class="card">
        <h2>Face Authentication Attendance</h2>
        <video id="video" autoplay muted playsinline></video>

        <div id="reg-section">
            <input type="text" id="username" placeholder="Enter Name" style="padding:10px; border-radius:5px;">
            <button class="btn-reg" onclick="process('register')">Register</button>
        </div>

        <div id="auth-section" class="hidden">
            <h3 id="welcome-msg"></h3>
            <button class="btn-in" onclick="process('Punch-In')">Punch-In</button>
            <button class="btn-out" onclick="process('Punch-Out')">Punch-Out</button>
        </div>

        <div id="status" style="margin: 15px;"></div>

        <table id="attendanceTable">
            <thead>
                <tr><th>Photo</th><th>Name</th><th>Action</th><th>Date</th><th>Time</th></tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
        <button class="btn-pdf" onclick="downloadPDF()">Download PDF Report</button>
    </div>

    <script>
        const { jsPDF } = window.jspdf;
        let logRecords = [];

        async function startCamera() {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            document.getElementById('video').srcObject = stream;
        }

        async function process(action) {
            const video = document.getElementById('video');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth; canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const imgData = canvas.toDataURL('image/jpeg');

            const res = await fetch(action === 'register' ? '/register' : '/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action, name: document.getElementById('username').value, image: imgData })
            });

            const data = await res.json();
            document.getElementById('status').innerText = data.message || "";

            if(data.status === "success") {
                if(action === 'register') {
                    document.getElementById('reg-section').classList.add('hidden');
                    document.getElementById('auth-section').classList.remove('hidden');
                    document.getElementById('welcome-msg').innerText = "Hello, " + data.user;
                } else {
                    addTableRow(data.img, data.user, action, data.date, data.time);
                }
            }
        }

        function addTableRow(imgBase64, name, action, date, time) {
            logRecords.push({ imgBase64, name, action, date, time });
            const row = `<tr>
                <td><img src="${imgBase64}" class="log-img"></td>
                <td>${name}</td><td>${action}</td><td>${date}</td><td>${time}</td>
            </tr>`;
            document.getElementById('tableBody').innerHTML += row;
        }

        function downloadPDF() {
            const doc = new jsPDF();
            doc.setFontSize(18);
            doc.text("Attendance Report - IST", 14, 20);

            const tableData = logRecords.map(r => ["", r.name, r.action, r.date, r.time]);

            doc.autoTable({
                head: [['Photo', 'Name', 'Action', 'Date', 'Time']],
                body: tableData,
                startY: 30,
                didDrawCell: (data) => {
                    if (data.section === 'body' && data.column.index === 0) {
                        const base64Img = logRecords[data.row.index].imgBase64;
                        doc.addImage(base64Img, 'JPEG', data.cell.x + 2, data.cell.y + 2, 10, 10);
                    }
                },
                styles: { minCellHeight: 15 }
            });
            doc.save("Attendance_Report.pdf");
        }
        startCamera();
    </script>
</body>
</html>
"""
# 4. Connecting Backend Server
@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data['name'].strip()
    image_data = base64.b64decode(data['image'].split(',')[1])
    with open(f"{KNOWN_FACES_DIR}/{name}.jpg", "wb") as f: f.write(image_data)
    load_known_faces()
    return jsonify({"status": "success", "user": name})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    action = data['action']
    img_b64_full = data['image']
    image_bytes = base64.b64decode(img_b64_full.split(',')[1])

    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    if face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0], tolerance=0.5)
        if True in matches:
            name = known_face_names[matches.index(True)]
            now_ist = datetime.datetime.now(IST)

            return jsonify({
                "status": "success",
                "user": name,
                "date": now_ist.strftime("%Y-%m-%d"),
                "time": now_ist.strftime("%I:%M:%S %p"),
                "img": img_b64_full
            })

    return jsonify({"status": "failed", "message": "Face Not Recognized"})

if __name__ == '__main__':
    load_known_faces()
    try:
        url = ngrok.connect(5000)
        print(f"\n Face Auth Attendance App: {url}")
    except: pass
    app.run(port=5000)
