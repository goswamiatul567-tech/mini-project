import sqlite3
import datetime
import os

# Set up the database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "sih.db")

def init_db():
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            students INTEGER,
            plates INTEGER,
            attendance INTEGER,
            status TEXT,
            sync_status INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def verify_and_save(students, plates, attendance=50):
    """
    Compares Students, Plates, and Attendance to find errors.
    Saves the result locally (sync_status = 0 means offline).
    """
    # Verification Logic (The "Brain" of your project)
    if plates < students:
        status = f"ERROR: {students - plates} students missing meals"
    elif plates > students:
        status = f"WARNING: {plates - students} extra plates detected"
    elif students < attendance:
        status = "WARNING: Students absent from meal"
    else:
        status = "VERIFIED: All meals accounted for"
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO records (timestamp, students, plates, attendance, status, sync_status) VALUES (?, ?, ?, ?, ?, 0)",
                 (timestamp, students, plates, attendance, status))
    conn.commit()
    conn.close()
    return status

def get_records():
    """Fetches the latest 10 records for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM records ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows

def sync_to_cloud():
    """Simulates syncing offline data to the cloud when internet returns."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE records SET sync_status = 1 WHERE sync_status = 0")
    conn.commit()
    conn.close()
    return True
