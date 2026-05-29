import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from core import database
from core import audit_logger
from theme import QSS
from ui.ui_login import LoginWindow


def main():
    database.init_db()
    audit_logger.init_audit_db()
    
    # Log system startup event
    audit_logger.log_action(examiner_id=None, action="System Startup", details="MedDiagnostics Core Application Engine Booted.")

    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setFont(QFont("Segoe UI", 10))

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
