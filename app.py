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
    records = get_records() # Returns last 10
    return render_template("index.html", records=records)

@app.route("/api/all_records")
def all_records():
    """Fetches every single record for the 'Show All' modal."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    records = [dict(row) for row in rows]
    return jsonify(records)

# ... (Keep the rest of the routes: /upload, /live_frame, /finish_live, /api/reset) ...
