"""
config_registry.py — Central Clinical Configuration & Decision Threshold Registry.
Handles JSON persistence for confidence limits, clinic names, and diagnostic constraints.
"""
import os
import json

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "confidence_threshold": 0.50,
    "critical_alert_threshold": 0.85,
    "hospital_name": "Neural Diagnostics Center",
    "department_name": "Neurology & Neurosurgery",
    "audit_retention_days": 90,
    "enable_gradcam": True
}


def load_config():
    """Load configuration from JSON file. Creates with defaults if not present."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, CONFIG_FILE)
    
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
        
    try:
        with open(path, "r") as f:
            cfg = json.load(f)
            # Guarantee all default keys are present
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
    except Exception as e:
        print(f"[Config Registry Error] Failed to read configuration: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config_dict):
    """Save the clinical configuration to config.json."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, CONFIG_FILE)
    
    try:
        # Validate data types
        validated = {}
        validated["confidence_threshold"] = max(0.1, min(0.99, float(config_dict.get("confidence_threshold", 0.50))))
        validated["critical_alert_threshold"] = max(0.5, min(0.99, float(config_dict.get("critical_alert_threshold", 0.85))))
        validated["hospital_name"] = str(config_dict.get("hospital_name", DEFAULT_CONFIG["hospital_name"])).strip() or DEFAULT_CONFIG["hospital_name"]
        validated["department_name"] = str(config_dict.get("department_name", DEFAULT_CONFIG["department_name"])).strip() or DEFAULT_CONFIG["department_name"]
        validated["audit_retention_days"] = int(config_dict.get("audit_retention_days", 90))
        validated["enable_gradcam"] = bool(config_dict.get("enable_gradcam", True))
        
        with open(path, "w") as f:
            json.dump(validated, f, indent=4)
        return True
    except Exception as e:
        print(f"[Config Registry Error] Failed to write configuration: {e}")
        return False


def get_value(key):
    """Safely fetch a specific configuration value."""
    cfg = load_config()
    return cfg.get(key, DEFAULT_CONFIG.get(key))
