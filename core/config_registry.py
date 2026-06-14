"""
config_registry.py — Central Clinical Configuration & Decision Threshold Registry.
Handles persistence for confidence limits, clinic names, and diagnostic constraints in the DB.
"""
import os
import json
from core import database

DEFAULT_CONFIG = {
    "confidence_threshold": 0.50,
    "critical_alert_threshold": 0.85,
    "hospital_name": "Neural Diagnostics Center",
    "department_name": "Neurology & Neurosurgery",
    "audit_retention_days": 90,
    "enable_gradcam": True
}

def _init_config_table():
    """Ensure the SystemConfig table exists in the database."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SystemConfig (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_config():
    """Load configuration from database. Creates with defaults if not present."""
    _init_config_table()
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM SystemConfig')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
        
    cfg = {}
    for k, v in rows:
        try:
            cfg[k] = json.loads(v)
        except Exception:
            cfg[k] = v
            
    # Guarantee all default keys are present
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg:
            cfg[k] = v
            
    return cfg

def save_config(config_dict):
    """Save the clinical configuration to the database."""
    _init_config_table()
    
    try:
        # Validate data types
        validated = {}
        validated["confidence_threshold"] = max(0.1, min(0.99, float(config_dict.get("confidence_threshold", 0.50))))
        validated["critical_alert_threshold"] = max(0.5, min(0.99, float(config_dict.get("critical_alert_threshold", 0.85))))
        validated["hospital_name"] = str(config_dict.get("hospital_name", DEFAULT_CONFIG["hospital_name"])).strip() or DEFAULT_CONFIG["hospital_name"]
        validated["department_name"] = str(config_dict.get("department_name", DEFAULT_CONFIG["department_name"])).strip() or DEFAULT_CONFIG["department_name"]
        validated["audit_retention_days"] = int(config_dict.get("audit_retention_days", 90))
        validated["enable_gradcam"] = bool(config_dict.get("enable_gradcam", True))
        
        conn = database.get_connection()
        cursor = conn.cursor()
        for k, v in validated.items():
            cursor.execute('''
                INSERT INTO SystemConfig (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            ''', (k, json.dumps(v)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Config Registry Error] Failed to write configuration to DB: {e}")
        return False

def get_value(key):
    """Safely fetch a specific configuration value."""
    cfg = load_config()
    return cfg.get(key, DEFAULT_CONFIG.get(key))
