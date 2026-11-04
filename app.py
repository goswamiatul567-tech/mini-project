import os
import cv2
import numpy as np
import sqlite3
from flask import Flask, render_template, request, jsonify
from utils.detector import process_frame
from database.db import init_db, verify_and_save, get_records, sync_to_cloud, DB_PATH

app = Flask(__name__)
init_db()
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    records = get_records()
    return render_template("index.html", records=records)

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    class_name = request.form.get("class_name", "Unknown")
    section = request.form.get("section", "Unknown")
    attendance = int(request.form.get("attendance", 0))
    
    file = request.files["image"]
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    if image is None:
        return jsonify({"error": "Invalid image format"}), 400

    counts, annotated_img = process_frame(image, is_live=False)
    
    out_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    cv2.imwrite(out_path, annotated_img)
    
    status = verify_and_save(class_name, section, counts["students"], counts["plates"], attendance)
    
    return jsonify({
        "success": True,
        "students": counts["students"],
        "plates": counts["plates"],
        "status": status,
        "image_url": "/static/uploads/latest.jpg"
    })

@app.route("/live_frame", methods=["POST"])
def live_frame():
    if "frame" not in request.files:
        return jsonify({"error": "No frame"}), 400
    
    file = request.files["frame"]
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    counts, annotated_img = process_frame(image, is_live=True)
    
    out_path = os.path.join(UPLOAD_FOLDER, "live.jpg")
    cv2.imwrite(out_path, annotated_img)
    
    return jsonify({
        "success": True,
        "students": counts["students"],
        "plates": counts["plates"],
        "image_url": "/static/uploads/live.jpg"
    })

@app.route("/finish_live", methods=["POST"])
def finish_live():
    data = request.json
    students = data.get("students", 0)
    plates = data.get("plates", 0)
    class_name = data.get("class_name", "Unknown")
    section = data.get("section", "Unknown")
    attendance = data.get("attendance", 0)
    
    status = verify_and_save(class_name, section, students, plates, attendance)
    
    from utils.tracker import tracker
    tracker.tracks.clear()
    tracker.next_id = 1
    
    return jsonify({"success": True, "status": status})

@app.route("/api/reset", methods=["POST"])
def reset_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM records")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
