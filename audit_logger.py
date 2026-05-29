"""
audit_logger.py — Secure HIPAA-compliant audit logging for clinical actions.
Saves log records both to a local 'audit.log' text file and an SQLite 'AuditLog' database table.
"""
import os
import datetime
import database

LOG_FILE = "audit.log"


def init_audit_db():
    """Ensure the AuditLog table exists in the system database."""
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS AuditLog (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                examiner_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (examiner_id) REFERENCES Examiner(examiner_id)
            )
        ''');
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Audit Log Error] Failed to initialize database: {e}")


def log_action(examiner_id, action, details=""):
    """
    Log a clinical or administrative event.
    Writes to both the local text audit log and the SQLite DB audit registry.
    """
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Retrieve examiner details
    ex_name = "System/Unknown"
    if examiner_id:
        info = database.get_examiner_info(examiner_id)
        if info:
            ex_name = f"{info[1]} (@{info[0]})"

    # 1. Write to secure audit.log text file
    log_entry = f"[{timestamp_str}] [OPERATOR: {ex_name}] [ACTION: {action}] Details: {details}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[Audit Log Error] Failed to write to audit.log: {e}")

    # 2. Write to SQLite database
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO AuditLog (examiner_id, action, details, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (examiner_id, action, details, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Audit Log Error] Failed to write to database: {e}")
