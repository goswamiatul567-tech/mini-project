
# 🍲 Smart Mid-Day Meal Monitoring System

An AI-powered, offline-first web application designed to bring transparency, accountability, and efficiency to school Mid-Day Meal distribution. 

## 🎯 The Problem
Traditional meal monitoring relies on manual counting and paper records, leading to:
- Fake attendance records.
- Food wastage and corruption.
- Inability to verify if meals actually reached the students.

## 💡 Our Solution
We use Computer Vision (YOLOv8) and Web Technologies to automate the monitoring process. The system:
1. **Detects Students & Plates:** Uses a dual-model approach to count heads and meal plates simultaneously.
2. **ByteTrack Integration:** Ensures students are not double-counted while walking through the line.
3. **Human-in-the-Loop:** The AI detects the counts, but a human operator must review and click "Confirm & Save" to prevent false data.
4. **Verification Logic:** Cross-checks AI detections against official attendance to flag errors (e.g., "3 students missing meals").
5. **Cloud Dashboard:** A real-time, dark-themed dashboard built with Flask and SQLite to view telemetry and audit logs.

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Computer Vision:** YOLOv8 (ONNX format), OpenCV, ONNX Runtime
- **Tracking:** Custom ByteTrack-style distance tracker
- **Database:** SQLite (Offline-first storage)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Deployment:** Render (Cloud hosting)

## 🚀 How to Run Locally
1. Clone the repository:
   `git clone https://github.com/goswamiatul567-tech/mini-project.git`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the Flask app:
   `python app.py`
4. Open `http://127.0.0.1:5000` in your browser.

## 📸 Screenshots
*(Add screenshots of your dashboard here later)*

## 👨‍💻 Developed By
- Atul Goswami
