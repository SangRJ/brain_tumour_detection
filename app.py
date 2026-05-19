"""
app.py — Entry point for Brain Tumour Diagnostics (PyQt6).
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import database
from theme import QSS
from ui_login import LoginWindow


def main():
    database.init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setFont(QFont("Segoe UI", 10))

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
