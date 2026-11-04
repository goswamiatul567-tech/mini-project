import sqlite3
import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sih.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # Added class_name and section columns
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            class_name TEXT,
            section TEXT,
            students INTEGER,
            plates INTEGER,
            attendance INTEGER,
            status TEXT,
            sync_status INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def verify_and_save(class_name, section, students, plates, attendance):
    """Compares Students, Plates, and Attendance, then saves with Class info."""
    if plates < students:
        status = f"ERROR: {students - plates} missing meals"
    elif plates > students:
        status = f"WARNING: {plates - students} extra plates"
    elif students < attendance:
        status = "WARNING: Absent students"
    else:
        status = "VERIFIED: All accounted for"
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT INTO records 
                 (timestamp, class_name, section, students, plates, attendance, status, sync_status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                 (timestamp, class_name, section, students, plates, attendance, status))
    conn.commit()
    conn.close()
    return status

def get_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM records ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows

def sync_to_cloud():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE records SET sync_status = 1 WHERE sync_status = 0")
    conn.commit()
    conn.close()
    return True
