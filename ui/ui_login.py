"""
ui_login.py — Login window for Brain Tumour Diagnostics.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core import database


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brain Tumor Diagnostics — Login")
        self.setMinimumSize(500, 600)
        self.resize(520, 650)
        self.setObjectName("appRoot")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("card")
        card.setFixedSize(380, 460)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(8)

        icon = QLabel("🧠")
        icon.setFont(QFont("Segoe UI", 38))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(icon)

        title = QLabel("Diagnostics Portal")
        title.setObjectName("heading")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("Sign in to continue")
        sub.setObjectName("subtext")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(sub)
        cl.addSpacing(20)

        ul = QLabel("Username")
        ul.setObjectName("formLabel")
        cl.addWidget(ul)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setMinimumHeight(44)
        cl.addWidget(self.username)
        cl.addSpacing(6)

        pl = QLabel("Password")
        pl.setObjectName("formLabel")
        cl.addWidget(pl)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(44)
        cl.addWidget(self.password)
        cl.addSpacing(16)

        btn = QPushButton("  Secure Login")
        btn.setObjectName("accentBtn")
        btn.setMinimumHeight(46)
        btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn.clicked.connect(self._login)
        cl.addWidget(btn)

        self.password.returnPressed.connect(self._login)
        self.username.returnPressed.connect(lambda: self.password.setFocus())

        cl.addStretch()
        outer.addWidget(card)

    def _login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        
        from core import audit_logger
        
        if database.needs_password_setup(u):
            if not p:
                QMessageBox.information(self, "Password Setup", "This is your first login. Please enter a secure password to set it.")
                return
            database.setup_password(u, p)
            QMessageBox.information(self, "Password Setup", "Your password has been successfully set. You will now be logged in.")
            
        eid = database.authenticate(u, p)
        if eid:
            # Log Successful Login
            try:
                audit_logger.log_action(eid, "Portal Login Success", "Examiner successfully authenticated into local clinical session.")
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            from ui.ui_main import MainWindow
            self.main = MainWindow(eid)
            self.main.show()
            self.close()
        else:
            # Log Failed Login Attempt
            try:
                audit_logger.log_action(None, "Portal Login Failed", f"Unauthorized credentials attempted for username: '{u}'")
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
