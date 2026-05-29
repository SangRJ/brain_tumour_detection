import sqlite3
import datetime
import os
import hashlib

DB_FILE = "clinic.db"

def _hash_password(password: str) -> str:
    """Hash the password for basic security."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    """Initialize the database schema and create a default examiner if none exists."""
    conn = get_connection()
    cursor = conn.cursor()

    # Patient Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Patient (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact_info TEXT
        )
    ''')

    # Examiner Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Examiner (
            examiner_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            examiner_name TEXT,
            role TEXT,
            department TEXT
        )
    ''')

    # MRI Examination Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MRI_Examination (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            examiner_id INTEGER,
            image_name TEXT,
            prediction TEXT,
            confidence_score REAL,
            heatmap_path TEXT,
            examination_date DATETIME,
            FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
            FOREIGN KEY (examiner_id) REFERENCES Examiner(examiner_id)
        )
    ''')
    
    conn.commit()

    # Add default examiner if table is empty
    cursor.execute('SELECT COUNT(*) FROM Examiner')
    if cursor.fetchone()[0] == 0:
        add_examiner("admin", "password", "Rogers", "Admin", "Radiology")

    conn.close()

def authenticate(username, password):
    """Authenticate an examiner and return their examiner_id, or None if failed."""
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = _hash_password(password)
    
    cursor.execute('''
        SELECT examiner_id FROM Examiner WHERE username = ? AND password = ?
    ''', (username, hashed_password))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def add_examiner(username, password, examiner_name, role, department):
    """Add a new examiner to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = _hash_password(password) if password else ""
    
    try:
        cursor.execute('''
            INSERT INTO Examiner (username, password, examiner_name, role, department)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, examiner_name, role, department))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Username already exists
    
    conn.close()
    return success

def needs_password_setup(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM Examiner WHERE username = ?', (username,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0] == "":
        return True
    return False

def setup_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = _hash_password(new_password)
    cursor.execute('UPDATE Examiner SET password = ? WHERE username = ?', (hashed, username))
    conn.commit()
    conn.close()

def get_all_patients():
    """Retrieve a list of all patients."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT patient_id, patient_name, age, gender, contact_info FROM Patient')
    patients = cursor.fetchall()
    conn.close()
    return patients

def add_patient(patient_name, age, gender, contact_info):
    """Explicitly create a new patient."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Patient (patient_name, age, gender, contact_info)
        VALUES (?, ?, ?, ?)
    ''', (patient_name, age, gender, contact_info))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def get_patient_history(patient_id):
    """Retrieve past MRI results for a specific patient."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.exam_id, e.image_name, e.prediction, e.confidence_score, e.examination_date, ex.examiner_name, e.heatmap_path
        FROM MRI_Examination e
        LEFT JOIN Examiner ex ON e.examiner_id = ex.examiner_id
        WHERE e.patient_id = ?
        ORDER BY e.examination_date DESC
    ''', (patient_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def get_patient_info(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT patient_id, patient_name, age, gender, contact_info FROM Patient WHERE patient_id = ?', (patient_id,))
    info = cursor.fetchone()
    conn.close()
    return info

def update_examiner_name(examiner_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE Examiner SET examiner_name = ? WHERE examiner_id = ?', (new_name, examiner_id))
    conn.commit()
    conn.close()

def update_examiner_password(examiner_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = _hash_password(new_password)
    cursor.execute('UPDATE Examiner SET password = ? WHERE examiner_id = ?', (hashed_password, examiner_id))
    conn.commit()
    conn.close()

def get_examiner_info(examiner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, examiner_name, role, department FROM Examiner WHERE examiner_id = ?', (examiner_id,))
    info = cursor.fetchone()
    conn.close()
    return info

def ensure_patient(patient_name, age=None, gender=None, contact_info=None):
    """
    Ensure a patient exists (for MVP we'll just create a new one if we don't have a lookup, 
    or just return a dummy patient ID).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Patient (patient_name, age, gender, contact_info)
        VALUES (?, ?, ?, ?)
    ''', (patient_name or "Unknown Patient", age, gender, contact_info))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def save_examination(patient_id, examiner_id, image_name, prediction, confidence_score, heatmap_path):
    """Save the results of an MRI examination."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute('''
        INSERT INTO MRI_Examination (patient_id, examiner_id, image_name, prediction, confidence_score, heatmap_path, examination_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (patient_id, examiner_id, image_name, prediction, confidence_score, heatmap_path, now))
    
    exam_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exam_id


def get_dashboard_stats():
    """Retrieve statistical counters for the hospital dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Total patients
    cursor.execute('SELECT COUNT(*) FROM Patient')
    total_patients = cursor.fetchone()[0]
    
    # 2. Total examinations
    cursor.execute('SELECT COUNT(*) FROM MRI_Examination')
    total_exams = cursor.fetchone()[0]
    
    # 3. Tumor vs Normal counts
    cursor.execute("SELECT COUNT(*) FROM MRI_Examination WHERE prediction = 'Tumor'")
    tumor_count = cursor.fetchone()[0]
    
    # Check both standard No Tumor predictions and fallback formats
    cursor.execute("SELECT COUNT(*) FROM MRI_Examination WHERE prediction != 'Tumor'")
    normal_count = cursor.fetchone()[0]
    
    # 4. Critical cases (above critical confidence threshold)
    from core import config_registry
    cfg = config_registry.load_config()
    crit_thresh = cfg.get("critical_alert_threshold", 0.85)
    
    cursor.execute("SELECT COUNT(*) FROM MRI_Examination WHERE prediction = 'Tumor' AND confidence_score >= ?", (crit_thresh,))
    critical_count = cursor.fetchone()[0]
    
    # 5. Examinations by date (for rolling timeline chart)
    cursor.execute('''
        SELECT DATE(examination_date) as exam_date, COUNT(*) 
        FROM MRI_Examination 
        GROUP BY exam_date 
        ORDER BY exam_date ASC 
        LIMIT 14
    ''')
    timeline_data = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_patients": total_patients,
        "total_exams": total_exams,
        "tumor_count": tumor_count,
        "normal_count": normal_count,
        "critical_count": critical_count,
        "timeline": timeline_data
    }


def get_audit_logs():
    """Fetch all audit log entries, sorted by timestamp descending, with examiner details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.timestamp, e.examiner_name, e.username, a.action, a.details
        FROM AuditLog a
        LEFT JOIN Examiner e ON a.examiner_id = e.examiner_id
        ORDER BY a.timestamp DESC
        LIMIT 150
    ''')
    logs = cursor.fetchall()
    conn.close()
    return logs
