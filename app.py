import os
import cv2
import numpy as np
import sqlite3
import csv
import io
from flask import Flask, render_template, request, jsonify, Response
from utils.detector import process_frame
from database.db import init_db, verify_and_save, get_records, sync_to_cloud, DB_PATH

app = Flask(__name__)
init_db()
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/dashboard")
def dashboard():
    records = get_records()
    conn = sqlite3.connect(DB_PATH)
    total_meals = conn.execute("SELECT SUM(students) FROM records").fetchone()[0] or 0
    total_errors = conn.execute("SELECT COUNT(*) FROM records WHERE status LIKE '%ERROR%'").fetchone()[0] or 0
    conn.close()
    stats = {"total_meals": total_meals, "total_errors": total_errors}
    return render_template("dashboard.html", records=records, stats=stats)

@app.route("/alerts")
def alerts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM records WHERE status LIKE '%ERROR%' ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("alerts.html", alerts=[dict(row) for row in rows])

@app.route("/records")
def records_page():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("records.html", all_records=[dict(row) for row in rows])

@app.route("/export_csv")
def export_csv():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date/Time", "Class", "Section", "Attendance", "Students Detected", "Plates Detected", "Status"])
    for row in rows:
        writer.writerow([row["id"], row["timestamp"], row["class_name"], row["section"], row["attendance"], row["students"], row["plates"], row["status"]])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=MealTrack_Audit_Records.csv"})

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files: return jsonify({"error": "No image uploaded"}), 400
    file = request.files["image"]
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if image is None: return jsonify({"error": "Invalid image format"}), 400
    counts, annotated_img = process_frame(image, is_live=False)
    out_path = os.path.join(UPLOAD_FOLDER, "latest.jpg")
    cv2.imwrite(out_path, annotated_img)
    return jsonify({"success": True, "students": counts["students"], "plates": counts["plates"], "image_url": "/static/uploads/latest.jpg"})

@app.route("/save_record", methods=["POST"])
def save_record():
    data = request.json
    status = verify_and_save(data.get("class_name"), data.get("section"), int(data.get("students", 0)), int(data.get("plates", 0)), int(data.get("attendance", 0)))
    return jsonify({"success": True, "status": status})

@app.route("/live_frame", methods=["POST"])
def live_frame():
    if "frame" not in request.files: return jsonify({"error": "No frame"}), 400
    file = request.files["frame"]
    npimg = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    counts, annotated_img = process_frame(image, is_live=True)
    out_path = os.path.join(UPLOAD_FOLDER, "live.jpg")
    cv2.imwrite(out_path, annotated_img)
    return jsonify({"success": True, "students": counts["students"], "plates": counts["plates"], "image_url": "/static/uploads/live.jpg"})

@app.route("/finish_live", methods=["POST"])
def finish_live():
    data = request.json
    status = verify_and_save(data.get("class_name"), data.get("section"), data.get("students"), data.get("plates"), data.get("attendance"))
    from utils.tracker import tracker
    tracker.tracks.clear()
    tracker.next_id = 1
    return jsonify({"success": True, "status": status})

@app.route("/api/all_records")
def api_all_records():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/reset", methods=["POST"])
def reset_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM records")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
