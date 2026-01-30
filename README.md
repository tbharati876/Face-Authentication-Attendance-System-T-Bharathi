# Video Demo Link:
https://drive.google.com/file/d/1xOwnvqnZ9QOQzdYhFlMiZfWV_lAODozw/view?usp=sharing

# Colab Code Notebook Link:
https://colab.research.google.com/drive/1ndrasLc91DKnk4Qal0wrUNrWtWWyRTVc?usp=sharing

# Face Authentication Attendance System

A real-time face recognition application built with Python, Flask, and Dlib. This system allows for user registration, identification, and attendance logging (Punch-In/Punch-Out) with automated PDF report generation.

## 🚀 Features
* **Real time Registration:** Capture and encode new faces via the browser.
* **Dual Action Logging:** Support for 'Punch-In' and 'Punch-Out' events.
* **Automated Reporting:** Generates a downloadable PDF report with timestamps and verification photos.
* **Adaptive UI:** Supports Light/Dark modes for better user experience.
* **Cloud Tunneling:** Integrated with `ngrok` for easy remote demoing.

---

## Model & Approach

### Underlying Technology
The system utilizes the **`face_recognition`** library, which is built on top of **dlib's** state of the art face recognition model. 

1.  **Face Detection:** Uses a HOG (Histogram of Oriented Gradients) based linear classifier to locate faces in the frame.
2.  **Face Landmarks:** Identifies specific points (eyes, nose, mouth) to normalize the face pose.
3.  **Encoding:** The system uses a **Deep Residual Network ** to transform the face image into a **dimension vector** (embedding).
4.  **Verification:** Attendance is marked by calculating the **Euclidean Distance** between the live encoding and the stored encodings. A tolerance threshold of `0.5` is used for strict matching.



### Spoof Prevention 
The current implementation includes a **Tolerance-based filtering**. By setting `tolerance=0.5`, the system ensures a high degree of similarity is required, preventing some low quality printed photo spoofs. 

---

## Accuracy & Expectations
* **Accuracy:** The dlib model has a reported accuracy of **99.38%** on the Labeled Faces in the Wild (LFW) dataset.
* **Performance:** Recognition occurs in near real-time (<200ms) once the face is detected.
* **Lighting:** Works best in front-lit conditions; performance may degrade in heavy backlight or extreme low light.

---

## ⚠️ Known Failure Cases & Limitations
1.  **Occlusions:** Heavy face masks or large sunglasses may prevent the landmark predictor from identifying the face.
2.  **Extreme Angles:** The HOG-based detector is optimized for frontal or near-frontal views; profile shots may fail.
3.  **Advanced Spoofing:** While simple photo spoofs are mitigated by distance thresholds, the system does not currently utilize 3D depth sensing or liveness detection (e.g. blink detection).
4.  **Environment:** Varying lighting conditions can shift the Euclidean distance of the same user.

---

## Installation & Setup
1.  **Clone the repository**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Ngrok:**
    Replace the `NGROK_TOKEN` in the script with your personal token from the ngrok dashboard.
4.  **Run the App:**
    ```bash
    python app.py
    ```

---

## 📂 Project Structure
* `app.py`: Main Flask application and ML logic.
* `known_faces/`: Stores registered user images and encodings.
* `attendance_photos/`: Storage for verification snapshots.
* `requirements.txt`: Python dependencies.
