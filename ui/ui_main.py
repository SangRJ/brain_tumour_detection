"""
ui_main.py — Main window with sidebar navigation.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core import database


class MainWindow(QMainWindow):
    def __init__(self, examiner_id):
        super().__init__()
        self.examiner_id = examiner_id
        self.setWindowTitle("Brain Tumor Diagnostics Management System")
        self.setMinimumSize(1100, 700)
        self.resize(1420, 870)

        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Brand
        brand_w = QWidget()
        bl = QVBoxLayout(brand_w)
        bl.setContentsMargins(24, 28, 24, 24)
        brand = QLabel("🧠  MedDiagnostics")
        brand.setObjectName("brand")
        bl.addWidget(brand)
        sb_layout.addWidget(brand_w)

        # User card
        info = database.get_examiner_info(examiner_id)
        name = info[1] if info and info[1] else "Examiner"

        uc = QFrame()
        uc.setObjectName("userCard")
        ucl = QVBoxLayout(uc)
        ucl.setContentsMargins(16, 14, 16, 14)
        un = QLabel(f"👤  {name}")
        un.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        ucl.addWidget(un)
        if info and info[2]:
            role_lbl = QLabel(info[2])
            role_lbl.setObjectName("subtext")
            ucl.addWidget(role_lbl)

        uc_wrap = QWidget()
        uc_wrap_l = QVBoxLayout(uc_wrap)
        uc_wrap_l.setContentsMargins(20, 0, 20, 20)
        uc_wrap_l.addWidget(uc)
        sb_layout.addWidget(uc_wrap)

        # Nav buttons
        self.nav_btns = []
        nav_w = QWidget()
        self.nav_layout = QVBoxLayout(nav_w)
        self.nav_layout.setContentsMargins(12, 0, 12, 0)
        self.nav_layout.setSpacing(4)

        # Admin privilege check
        is_admin = False
        if info:
            username = info[0]
            role = info[2]
            if username == "admin" or (role and role.lower() == "admin"):
                is_admin = True

        self._add_nav("🔍  Patient Selection", 0)
        self._add_nav("📊  Hospital Analytics", 1)
        self._add_nav("⚙️  Settings", 2)
        if is_admin:
            self._add_nav("👤  Add Examiner", 3)

        sb_layout.addWidget(nav_w)
        sb_layout.addStretch()

        # Logout
        logout_w = QWidget()
        lo_l = QVBoxLayout(logout_w)
        lo_l.setContentsMargins(12, 0, 12, 20)
        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setMinimumHeight(44)
        logout_btn.clicked.connect(self._logout)
        lo_l.addWidget(logout_btn)
        sb_layout.addWidget(logout_w)

        main_layout.addWidget(sidebar)

        # Content area
        content = QWidget()
        content.setObjectName("contentArea")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        cl.addWidget(self.stack)
        main_layout.addWidget(content)

        # Pages - lazy import to avoid circular imports
        from ui.ui_pages import PatientSelectionPage, SettingsPage, AddExaminerPage, HospitalAnalyticsPage
        self.pages = {
            0: PatientSelectionPage(self),
            1: HospitalAnalyticsPage(self),
            2: SettingsPage(self),
        }
        if is_admin:
            self.pages[3] = AddExaminerPage(self)

        for idx in sorted(self.pages.keys()):
            self.stack.addWidget(self.pages[idx])

        self._switch(0)

    def _add_nav(self, text, idx):
        btn = QPushButton(text)
        btn.setObjectName("navBtn")
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda _, i=idx: self._switch(i))
        self.nav_layout.addWidget(btn)
        self.nav_btns.append(btn)

    def _switch(self, idx):
        for i, b in enumerate(self.nav_btns):
            b.setObjectName("navBtnActive" if i == idx else "navBtn")
            b.style().unpolish(b)
            b.style().polish(b)
        self.stack.setCurrentIndex(idx)

    def push_page(self, page):
        """Push a dynamic page (history/analysis) onto the stack."""
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)
        # Deselect nav buttons
        for b in self.nav_btns:
            b.setObjectName("navBtn")
            b.style().unpolish(b)
            b.style().polish(b)

    def pop_page(self, page):
        """Remove a dynamic page and go back to patient selection."""
        self.stack.removeWidget(page)
        page.deleteLater()
        self._switch(0)

    def _logout(self):
        try:
            from core import audit_logger
            audit_logger.log_action(self.examiner_id, "Portal Session Logged Out", "Examiner safely terminated clinical session.")
        except Exception as le:
            print(f"[Audit Log Error] Failed logging event: {le}")

        from ui.ui_login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()
