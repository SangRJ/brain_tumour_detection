"""
ui_login.py Login window for Brain Tumour Diagnostics.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QGridLayout, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QPainterPath, QPolygonF
from core import database


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Login - Neural Diagnostics")
        self.setMinimumSize(1100, 700)
        self.resize(1420, 870)
        self.setObjectName("appRoot")
        
        # Transparent background for the main window widget so paintEvent works
        self.setStyleSheet("background-color: transparent;")

        # Main horizontal layout
        main_lay = QHBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ---------------------------------------------------------
        # LEFT PANEL (Form Container)
        # ---------------------------------------------------------
        left_panel = QWidget()
        left_grid = QGridLayout(left_panel)
        left_grid.setContentsMargins(0, 0, 0, 0)
        
        form_container = QWidget()
        form_container.setFixedWidth(440)
        form_lay = QVBoxLayout(form_container)
        form_lay.setContentsMargins(20, 20, 20, 20)
        form_lay.setSpacing(8)

        # Title
        title = QLabel("Neural Diagnostics")
        title.setStyleSheet("color: white; font-family: 'Inter'; font-size: 28px; font-weight: 800;")
        form_lay.addWidget(title)

        sub = QLabel("Clinical AI Suite")
        sub.setStyleSheet("color: #cccccc; font-family: 'Inter'; font-size: 14px; font-weight: 500;")
        form_lay.addWidget(sub)
        form_lay.addSpacing(32)

        signin = QLabel("Sign in to continue")
        signin.setStyleSheet("color: #aaaaaa; font-family: 'Inter'; font-size: 15px;")
        form_lay.addWidget(signin)
        form_lay.addSpacing(24)

        # Username
        ul = QLabel("USERNAME")
        ul.setStyleSheet("color: #999999; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        form_lay.addWidget(ul)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setStyleSheet("border: 1px solid #333333; border-radius: 6px; padding: 10px; color: white; font-size: 14px; background-color: #000000;")
        self.username.setMinimumHeight(44)
        form_lay.addWidget(self.username)
        form_lay.addSpacing(16)

        # Password
        pl = QLabel("PASSWORD")
        pl.setStyleSheet("color: #999999; font-size: 11px; font-weight: bold; text-transform: uppercase;")
        form_lay.addWidget(pl)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("border: 1px solid #333333; border-radius: 6px; padding: 10px; color: white; font-size: 14px; background-color: #000000;")
        self.password.setMinimumHeight(44)
        form_lay.addWidget(self.password)
        form_lay.addSpacing(24)



        # Login Button
        btn = QPushButton("Secure Login →")
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: black; border: none; border-radius: 6px; font-weight: bold; font-size: 15px; margin: 0px; padding: 10px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:pressed { background-color: #cccccc; }
        """)
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._login)
        form_lay.addWidget(btn)

        self.password.returnPressed.connect(self._login)
        self.username.returnPressed.connect(lambda: self.password.setFocus())
        
        # Center form inside the left panel
        left_grid.addWidget(form_container, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # ---------------------------------------------------------
        # RIGHT PANEL (Overlay Title)
        # ---------------------------------------------------------
        right_panel = QWidget()
        right_grid = QGridLayout(right_panel)
        right_grid.setContentsMargins(0, 0, 0, 0)
        

        
        main_lay.addWidget(left_panel, 1)
        main_lay.addWidget(right_panel, 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Fill entire background with black (left side)
        painter.fillRect(self.rect(), QColor("#000000"))
        
        # 2. Draw the diagonal slash dark background (right side)
        w = self.width()
        h = self.height()
        
        # Custom polygon to create the diagonal split
        # Top-left starts at 55% of screen width, bottom-left starts at 45%
        poly = QPolygonF([
            QPointF(w * 0.55, 0),
            QPointF(w, 0),
            QPointF(w, h),
            QPointF(w * 0.45, h)
        ])
        
        path = QPainterPath()
        path.addPolygon(poly)
        
        painter.save()
        painter.setClipPath(path)
        
        import os
        from PyQt6.QtGui import QPixmap
        img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "login.png")
        pixmap = QPixmap(img_path)
        
        if not pixmap.isNull():
            # Target dimensions for the right half
            target_w = w * 0.55
            target_h = h
            
            # Scale and preserve aspect ratio by expanding to fill target_w x target_h
            scaled_pixmap = pixmap.scaled(
                int(target_w), int(target_h), 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Align the right edge of the image with the right edge of the window
            x_offset = int(w - scaled_pixmap.width())
            
            # Center vertically
            y_offset = int((h - scaled_pixmap.height()) // 2)
            
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            painter.fillPath(path, QColor("#111111"))  # Fallback
            
        painter.restore()

    def _show_msg(self, title, text, is_error=False):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        
        msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

        # Professional clinical styling for dialogs
        if is_error:
            msg.setStyleSheet("""
                QMessageBox { background-color: #000000; }
                QLabel { color: #fca5a5; font-size: 14px; font-weight: bold; font-family: 'Inter'; }
                QPushButton { background-color: #ffffff; color: black; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)
        else:
            msg.setStyleSheet("""
                QMessageBox { background-color: #000000; }
                QLabel { color: #ffffff; font-size: 14px; font-weight: bold; font-family: 'Inter'; }
                QPushButton { background-color: #ffffff; color: black; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)
        msg.exec()

    def _login(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        
        from core import audit_logger
        
        if database.needs_password_setup(u):
            if not p:
                self._show_msg("Password Setup Required", "This is your first login. Please enter a secure password to register your account.", is_error=False)
                return
            database.setup_password(u, p)
            self._show_msg("Account Registered", "Your password has been successfully securely stored. You will now be logged in.", is_error=False)
            
        eid = database.authenticate(u, p)
        if eid == -1:
            try:
                audit_logger.log_action(None, "Portal Login Blocked", f"Login attempted on disabled account: '{u}'")
            except Exception:
                pass
            self._show_msg("Account Suspended", "This account has been disabled by a system administrator", is_error=True)
            return
            
        if eid:
            # Log Successful Login
            try:
                audit_logger.log_action(eid, "Portal Login Success", "Examiner successfully authenticated into local clinical session.")
            except Exception as le:
                pass

            from ui.ui_main import MainWindow
            self.main = MainWindow(eid)
            self.main.show()
            self.close()
        else:
            # Log Failed Login Attempt
            try:
                audit_logger.log_action(None, "Portal Login Failed", f"Unauthorized credentials attempted for username: '{u}'")
            except Exception as le:
                pass

            self._show_msg("Authentication Failed", "The credentials provided are invalid or expired.", is_error=True)
