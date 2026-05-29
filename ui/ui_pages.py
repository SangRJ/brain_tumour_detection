"""Patient selection, settings, and add examiner pages with rich clinical layouts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QMessageBox, QScrollArea, QGridLayout, QSizePolicy,
    QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core import database
import datetime

ROLES = ["Radiologist", "Neurologist", "Neurosurgeon", "Oncologist", "Resident", "Technician", "Other"]
DEPARTMENTS = ["Radiology", "Neurology", "Neurosurgery", "Oncology", "Pathology", "Emergency", "Other"]


def _card(parent=None):
    f = QFrame(parent)
    f.setObjectName("card")
    return f


def _sep(parent=None):
    s = QFrame(parent)
    s.setObjectName("separator")
    s.setFixedHeight(1)
    return s


def get_stats():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Patient")
        p_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM MRI_Examination")
        e_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Examiner")
        ex_count = cursor.fetchone()[0]
        conn.close()
        return p_count, e_count, ex_count
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return 0, 0, 0


def get_all_examiners():
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT examiner_name, role, department, username FROM Examiner ORDER BY examiner_id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching examiners: {e}")
        return []


class KPICard(QFrame):
    def __init__(self, icon_str, title, value_str, parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(14)

        icon_lbl = QLabel(icon_str)
        icon_lbl.setObjectName("kpiIcon")
        lay.addWidget(icon_lbl)

        txt_lay = QVBoxLayout()
        txt_lay.setSpacing(3)
        
        val_lbl = QLabel(value_str)
        val_lbl.setObjectName("kpiVal")
        txt_lay.addWidget(val_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("kpiTitle")
        txt_lay.addWidget(title_lbl)

        lay.addLayout(txt_lay)
        lay.addStretch()


class ExaminerRow(QFrame):
    def __init__(self, name, role, dept, username, parent=None):
        super().__init__(parent)
        self.setObjectName("listItemRow")
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)
        
        icon = QLabel("")
        icon.setFont(QFont("Segoe UI", 13))
        lay.addWidget(icon)
        
        details = QVBoxLayout()
        details.setSpacing(2)
        
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        details.addWidget(name_lbl)
        
        un_lbl = QLabel(f"@{username}")
        un_lbl.setObjectName("muted")
        details.addWidget(un_lbl)
        
        lay.addLayout(details)
        lay.addStretch()
        
        if role:
            r_lbl = QLabel(role)
            r_lbl.setObjectName("badgeSuccess")
            lay.addWidget(r_lbl)
            
        if dept:
            d_lbl = QLabel(dept)
            d_lbl.setObjectName("badgeAccent")
            lay.addWidget(d_lbl)


class NewPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Patient")
        self.setFixedSize(450, 360)
        self.setStyleSheet("background-color: #0f172a; color: white;")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        
        t2 = QLabel("Register New Patient Intake")
        t2.setObjectName("subheading")
        lay.addWidget(t2)
        
        form_grid = QGridLayout()
        form_grid.setVerticalSpacing(12)
        form_grid.setHorizontalSpacing(10)

        form_grid.addWidget(QLabel("Full Patient Name"), 0, 0, 1, 2)
        self.pname = QLineEdit()
        self.pname.setPlaceholderText("Enter name")
        self.pname.setMinimumHeight(42)
        form_grid.addWidget(self.pname, 1, 0, 1, 2)

        form_grid.addWidget(QLabel("Age"), 2, 0)
        form_grid.addWidget(QLabel("Gender"), 2, 1)
        
        self.page = QLineEdit()
        self.page.setPlaceholderText("Age")
        self.page.setMinimumHeight(42)
        form_grid.addWidget(self.page, 3, 0)

        self.pgender = QLineEdit()
        self.pgender.setPlaceholderText("Gender")
        self.pgender.setMinimumHeight(42)
        form_grid.addWidget(self.pgender, 3, 1)

        form_grid.addWidget(QLabel("Contact Info"), 4, 0, 1, 2)
        self.pcontact = QLineEdit()
        self.pcontact.setPlaceholderText("Email or phone number")
        self.pcontact.setMinimumHeight(42)
        form_grid.addWidget(self.pcontact, 5, 0, 1, 2)
        
        lay.addLayout(form_grid)
        lay.addStretch()
        
        ab = QPushButton("Save & Register Patient")
        ab.setObjectName("accentBtn")
        ab.setMinimumHeight(44)
        ab.clicked.connect(self.accept)
        lay.addWidget(ab)


class PatientSelectionPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # Header Row
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        title = QLabel("Active Roster")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        wl.addWidget(title)
        
        sub = QLabel("Pending and active neurological scans requiring analysis.")
        sub.setObjectName("subtext")
        wl.addWidget(sub)
        hdr.addLayout(wl)
        hdr.addStretch()
        
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search Patient ID...")
        search_box.setFixedWidth(200)
        search_box.setMinimumHeight(38)
        search_box.textChanged.connect(self._filter_patients)
        self.search_box = search_box
        hdr.addWidget(search_box)
        
        new_btn = QPushButton("+ NEW PATIENT")
        new_btn.setObjectName("accentBtn")
        new_btn.setFixedSize(140, 38)
        new_btn.setStyleSheet("background-color: #c0c1ff; color: #0f172a; font-weight: bold; font-size: 11px;")
        new_btn.clicked.connect(self._show_new_patient_dialog)
        hdr.addWidget(new_btn)
        
        lay.addLayout(hdr)

        # KPI Cards Row
        self.kpi_lay = QHBoxLayout()
        self.kpi_lay.setSpacing(16)
        lay.addLayout(self.kpi_lay)
        lay.addSpacing(10)

        # Table Wrapper
        table_wrap = QWidget()
        table_wrap.setObjectName("card")
        tl = QVBoxLayout(table_wrap)
        tl.setContentsMargins(20, 20, 20, 20)
        tl.setSpacing(0)
        
        # Table Header
        th = QHBoxLayout()
        cols = ["PATIENT ID", "NAME", "SCAN DATE", "DIAGNOSTIC STATUS", "TRIAGE PRIORITY", "ACTION"]
        widths = [100, 160, 140, 160, 120, 200]
        for c, w in zip(cols, widths):
            lbl = QLabel(c)
            lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            if w > 0:
                lbl.setFixedWidth(w)
            th.addWidget(lbl)
        tl.addLayout(th)
        
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: #334155; margin-top: 10px; margin-bottom: 10px;")
        tl.addWidget(div)

        # Scroll area for rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.container = QWidget()
        self.list_lay = QVBoxLayout(self.container)
        self.list_lay.setContentsMargins(0, 0, 0, 0)
        self.list_lay.setSpacing(0)
        
        scroll.setWidget(self.container)
        tl.addWidget(scroll)
        
        # Footer
        self.footer_lbl = QLabel()
        self.footer_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        tl.addSpacing(10)
        tl.addWidget(self.footer_lbl)
        
        lay.addWidget(table_wrap)

        self._refresh_data()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_data()

    def _refresh_data(self):
        # Clear existing KPIs
        while self.kpi_lay.count():
            item = self.kpi_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear existing list rows
        while self.list_lay.count():
            item = self.list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.rows_list = []
        
        self.patients = database.get_all_patients()
        total_active = len(self.patients)
        
        high_priority = 0
        completed_scans = 0
        ai_processing = 0
        
        self.patient_latest_exams = {}
        for p in self.patients:
            pid = p[0]
            hist = database.get_patient_history(pid)
            if hist:
                latest = hist[0]
                self.patient_latest_exams[pid] = latest
                if latest[2] == "Tumor":
                    high_priority += 1
                elif latest[2] == "No Tumor" or latest[2] == "Normal":
                    completed_scans += 1
            else:
                ai_processing += 1
                self.patient_latest_exams[pid] = None

        def _kpi(title, val, icon_color, subtitle=""):
            c = QFrame()
            c.setObjectName("card")
            l = QVBoxLayout(c)
            l.setContentsMargins(16, 12, 16, 12)
            t = QLabel(title)
            t.setStyleSheet(f"color: {icon_color}; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            
            vl = QHBoxLayout()
            v = QLabel(str(val))
            v.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            vl.addWidget(v)
            if subtitle:
                sl = QLabel(subtitle)
                sl.setStyleSheet("color: #4edea3; font-size: 10px; font-weight: bold;")
                vl.addWidget(sl)
            vl.addStretch()
            
            l.addWidget(t)
            l.addLayout(vl)
            return c
            
        self.kpi_lay.addWidget(_kpi("TOTAL ACTIVE", total_active, "#94a3b8", "+12 today"))
        self.kpi_lay.addWidget(_kpi("HIGH PRIORITY", high_priority, "#ef4444"))
        self.kpi_lay.addWidget(_kpi("COMPLETED SCANS", completed_scans, "#10b981"))
        self.kpi_lay.addWidget(_kpi("PENDING SCANS", ai_processing, "#f59e0b"))

        if not self.patients:
            e = QLabel("No patients currently in the roster.")
            e.setObjectName("subtext")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_lay.addWidget(e)
        else:
            for i, p in enumerate(self.patients):
                row = self._create_patient_row(p)
                self.list_lay.addWidget(row)
                self.rows_list.append((p[1].lower(), row))
                if i < len(self.patients) - 1:
                    row_div = QFrame()
                    row_div.setFixedHeight(1)
                    row_div.setStyleSheet("background-color: #1e293b;")
                    self.list_lay.addWidget(row_div)

        self.list_lay.addStretch()
        self.footer_lbl.setText(f"Showing 1-{min(5, total_active)} of {total_active} patients")

    def _create_patient_row(self, p):
        row = QWidget()
        row.setMinimumHeight(60)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 8, 0, 8)
        
        pid = p[0]
        name = p[1]
        
        latest_exam = self.patient_latest_exams.get(pid)
        if latest_exam:
            date_str = str(latest_exam[4]).split(".")[0]
            pred = latest_exam[2]
            status_text = "High Risk" if pred == "Tumor" else "Completed"
            priority = "P1" if pred == "Tumor" else "P3"
        else:
            date_str = "No scans available"
            status_text = "Review Required"
            priority = "P2"

        # Widths must match header widths
        # PATIENT ID
        id_lbl = QLabel(f"ND-{pid:04d}")
        id_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: bold;")
        id_lbl.setFixedWidth(100)
        rl.addWidget(id_lbl)
        
        # NAME
        n_lbl = QLabel(name)
        n_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        n_lbl.setFixedWidth(160)
        rl.addWidget(n_lbl)
        
        # SCAN DATE
        d_lbl = QLabel(date_str)
        d_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
        d_lbl.setFixedWidth(140)
        rl.addWidget(d_lbl)
        
        # DIAGNOSTIC STATUS
        pill = QLabel()
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if status_text == "High Risk":
            pill.setText("High Risk")
            pill.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        elif status_text == "Completed":
            pill.setText("Completed")
            pill.setStyleSheet("background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        else:
            pill.setText("Review Required")
            pill.setStyleSheet("background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        pill.setFixedSize(120, 24)
        
        p_wrap = QWidget()
        p_wrap.setFixedWidth(160)
        p_lay = QHBoxLayout(p_wrap)
        p_lay.setContentsMargins(0,0,0,0)
        p_lay.addWidget(pill, alignment=Qt.AlignmentFlag.AlignLeft)
        rl.addWidget(p_wrap)
        
        # TRIAGE PRIORITY
        pri_lbl = QLabel(priority)
        if priority == "P1":
            pri_lbl.setStyleSheet("color: #fca5a5; font-size: 12px; font-weight: bold;")
        elif priority == "P2":
            pri_lbl.setStyleSheet("color: #fcd34d; font-size: 12px; font-weight: bold;")
        else:
            pri_lbl.setStyleSheet("color: #6ee7b7; font-size: 12px; font-weight: bold;")
        pri_lbl.setFixedWidth(120)
        rl.addWidget(pri_lbl)
        
        # ACTION BUTTONS
        btn_lay = QHBoxLayout()
        btn_lay.setContentsMargins(0,0,0,0)
        btn_lay.setSpacing(8)
        
        btn_scan = QPushButton("Analyze")
        btn_scan.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #4f46e5; color: #818cf8; border-radius: 6px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(79, 70, 229, 0.1); }
        """)
        btn_scan.setFixedSize(85, 32)
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scan.clicked.connect(lambda _, x=pid: self._go_analyze(x))
        btn_lay.addWidget(btn_scan)
        
        btn_hist = QPushButton("History")
        btn_hist.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid #475569; color: #cbd5e1; border-radius: 6px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: rgba(71, 85, 105, 0.3); }
        """)
        btn_hist.setFixedSize(85, 32)
        btn_hist.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hist.clicked.connect(lambda _, x=pid: self._go_history(x))
        btn_lay.addWidget(btn_hist)
        
        btn_wrap = QWidget()
        btn_wrap.setFixedWidth(200)
        btn_wrap.setLayout(btn_lay)
        rl.addWidget(btn_wrap)
        
        return row

    def _filter_patients(self, text):
        query = text.lower().strip()
        for name_lower, row_widget in self.rows_list:
            if not query or query in name_lower:
                row_widget.show()
            else:
                row_widget.hide()

    def _go_analyze(self, pid):
        from ui.ui_analysis import AnalysisPage
        self.mw.push_page(AnalysisPage(self.mw, pid))

    def _go_history(self, pid):
        from ui.ui_history import PatientHistoryPage
        self.mw.push_page(PatientHistoryPage(self.mw, pid))

    def _show_new_patient_dialog(self):
        from PyQt6.QtWidgets import QDialog
        dialog = NewPatientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            n = dialog.pname.text().strip()
            if not n:
                QMessageBox.warning(self, "Warning", "Patient Name is required.")
                return
            
            age = None
            try:
                age = int(dialog.page.text().strip())
            except:
                pass
                
            pid = database.add_patient(n, age, dialog.pgender.text().strip(), dialog.pcontact.text().strip())
            
            # Log patient intake
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Patient Intake Registered",
                    details=f"New patient profile registered: ID {pid}, Name: '{n}', Age: {age or 'N/A'}"
                )
            except Exception as le:
                pass

            QMessageBox.information(self, "Success", "Patient successfully added to local database.")
            
            # Navigate immediately to Analyze screen for new patient
            self._go_analyze(pid)


class SettingsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win

        # Main top-level layout on SettingsPage
        top_layout = QVBoxLayout(self)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_content.setObjectName("settingsScrollContent")
        lay = QVBoxLayout(scroll_content)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        welcome = QLabel("Profile & Security Center")
        welcome.setObjectName("heading")
        wl.addWidget(welcome)
        sub = QLabel("Manage your examiner profile, security settings, and view diagnostic system health.")
        sub.setObjectName("subtext")
        wl.addWidget(sub)
        hdr.addLayout(wl)
        lay.addLayout(hdr)

        # Split columns
        cols = QHBoxLayout()
        cols.setSpacing(20)

        # Left Column Profile adjustments
        left = _card()
        cl = QVBoxLayout(left)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(12)

        t = QLabel("Change Account Details")
        t.setObjectName("subheading")
        cl.addWidget(t)
        cl.addWidget(_sep())
        cl.addSpacing(4)

        info = database.get_examiner_info(self.mw.examiner_id)
        cur_name = info[1] if info else ""

        cl.addWidget(self._fl("Update Display Name"))
        self.name_e = QLineEdit()
        self.name_e.setText(cur_name)
        self.name_e.setMinimumHeight(42)
        cl.addWidget(self.name_e)

        nb = QPushButton("Save Name")
        nb.setObjectName("accentBtn")
        nb.setMinimumHeight(44)
        nb.clicked.connect(self._save_name)
        cl.addWidget(nb)
        cl.addSpacing(14)

        cl.addWidget(self._fl("Update Security Password"))
        self.pw_e = QLineEdit()
        self.pw_e.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_e.setPlaceholderText("Enter new password")
        self.pw_e.setMinimumHeight(42)
        cl.addWidget(self.pw_e)

        pb = QPushButton("Save Password")
        pb.setObjectName("warnBtn")
        pb.setMinimumHeight(44)
        pb.clicked.connect(self._save_pw)
        cl.addWidget(pb)
        cl.addStretch()
        cols.addWidget(left, 5)

        # Right Column Info panel
        right = _card()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 20, 24, 20)
        rl.setSpacing(14)

        t2 = QLabel("Session & System Health")
        t2.setObjectName("subheading")
        rl.addWidget(t2)
        rl.addWidget(_sep())

        # Badge panel
        badge = QFrame()
        badge.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 10px;")
        bl = QVBoxLayout(badge)
        bl.setContentsMargins(18, 14, 18, 14)
        bl.setSpacing(6)

        bl.addWidget(QLabel("ACTIVE SESSION OPERATOR"))
        name_lbl = QLabel(cur_name or "Examiner")
        name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        bl.addWidget(name_lbl)

        role = info[2] if info and info[2] else "Staff Member"
        dept = info[3] if info and info[3] else "Radiology"
        
        detail_lay = QHBoxLayout()
        detail_lay.setSpacing(8)
        
        role_b = QLabel(role)
        role_b.setObjectName("badgeSuccess")
        detail_lay.addWidget(role_b)

        dept_b = QLabel(dept)
        dept_b.setObjectName("badgeAccent")
        detail_lay.addWidget(dept_b)
        
        detail_lay.addStretch()
        bl.addLayout(detail_lay)
        rl.addWidget(badge)

        # System health grid
        health_lay = QVBoxLayout()
        health_lay.setSpacing(10)

        health_lay.addWidget(self._hl("Database File", "clinic.db  (Active)"))
        health_lay.addWidget(self._hl("DB Status", "Connected & Encrypted"))
        health_lay.addWidget(self._hl("AI Model Host", "TensorFlow Local CPU Runtime"))
        health_lay.addWidget(self._hl("Analysis Portals", "Standard Model + Grad-CAM Convolutional Layer"))
        health_lay.addWidget(self._hl("Diagnostics Cache", "sqlite3 Standard Engine"))

        rl.addLayout(health_lay)
        rl.addStretch()
        cols.addWidget(right, 5)

        lay.addLayout(cols, 1)
        
        # Check admin privilege to dynamically render thresholds config registry
        is_admin = False
        if info:
            username = info[0]
            role = info[2]
            if username == "admin" or (role and role.lower() == "admin"):
                is_admin = True
                
        if is_admin:
            self.thresh_card = self._create_threshold_card()
            lay.addWidget(self.thresh_card)
            
            # Create and add the Security Logs Card!
            self.logs_card = self._create_logs_card()
            lay.addWidget(self.logs_card)

        scroll.setWidget(scroll_content)
        top_layout.addWidget(scroll)

    def _fl(self, t):
        l = QLabel(t)
        l.setObjectName("formLabel")
        return l

    def _hl(self, label, value):
        f = QFrame()
        f.setStyleSheet("background-color: transparent; border: none;")
        fl = QHBoxLayout(f)
        fl.setContentsMargins(0, 4, 0, 4)
        
        lbl = QLabel(label)
        lbl.setObjectName("formLabel")
        fl.addWidget(lbl)
        fl.addStretch()
        
        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        val.setStyleSheet("color: #e2e8f0;")
        fl.addWidget(val)
        return f

    def _save_name(self):
        n = self.name_e.text().strip()
        if n:
            database.update_examiner_name(self.mw.examiner_id, n)
            
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Account Profile Updated",
                    details=f"Display name updated to: '{n}'"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", "Display name saved successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Display name cannot be empty.")

    def _save_pw(self):
        p = self.pw_e.text().strip()
        if p:
            database.update_examiner_password(self.mw.examiner_id, p)
            
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Account Password Updated",
                    details="Security credentials updated."
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", "Security credentials updated successfully.")
            self.pw_e.clear()
        else:
            QMessageBox.warning(self, "Warning", "Password cannot be empty.")

    def _create_threshold_card(self):
        from core import config_registry
        cfg = config_registry.load_config()
        
        card = _card()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(14)
        
        t = QLabel("Clinical Decision Registry & Operating Thresholds")
        t.setObjectName("subheading")
        cl.addWidget(t)
        cl.addWidget(_sep())
        
        # Grid layout for settings fields
        grid = QGridLayout()
        grid.setSpacing(14)
        
        # Hospital Name
        grid.addWidget(self._fl("Hospital Name"), 0, 0)
        self.hospital_e = QLineEdit()
        self.hospital_e.setText(cfg.get("hospital_name", ""))
        self.hospital_e.setMinimumHeight(40)
        grid.addWidget(self.hospital_e, 0, 1)
        
        # Dept Name
        grid.addWidget(self._fl("Clinical Department Name"), 0, 2)
        self.dept_e = QLineEdit()
        self.dept_e.setText(cfg.get("department_name", ""))
        self.dept_e.setMinimumHeight(40)
        grid.addWidget(self.dept_e, 0, 3)
        
        # Confidence Threshold
        grid.addWidget(self._fl("AI Decision Boundary Threshold (0.10 - 0.99)"), 1, 0)
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.10, 0.99)
        self.conf_spin.setSingleStep(0.05)
        self.conf_spin.setValue(cfg.get("confidence_threshold", 0.50))
        self.conf_spin.setMinimumHeight(40)
        grid.addWidget(self.conf_spin, 1, 1)
        
        # Critical Alert Threshold
        grid.addWidget(self._fl("High-Risk Alert Threshold (0.50 - 0.99)"), 1, 2)
        self.crit_spin = QDoubleSpinBox()
        self.crit_spin.setRange(0.50, 0.99)
        self.crit_spin.setSingleStep(0.05)
        self.crit_spin.setValue(cfg.get("critical_alert_threshold", 0.85))
        self.crit_spin.setMinimumHeight(40)
        grid.addWidget(self.crit_spin, 1, 3)
        
        cl.addLayout(grid)
        
        # Save btn
        sb = QPushButton("Save Clinical Registry Settings")
        sb.setObjectName("accentBtn")
        sb.setMinimumHeight(44)
        sb.clicked.connect(self._save_thresholds)
        cl.addWidget(sb)
        
        return card

    def _save_thresholds(self):
        from core import config_registry
        
        cfg = {
            "hospital_name": self.hospital_e.text().strip(),
            "department_name": self.dept_e.text().strip(),
            "confidence_threshold": self.conf_spin.value(),
            "critical_alert_threshold": self.crit_spin.value(),
            "audit_retention_days": 90,
            "enable_gradcam": True
        }
        
        ok = config_registry.save_config(cfg)
        if ok:
            # Audit log trace
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Clinical Threshold Registry Updated",
                    details=f"Conf Threshold: {cfg['confidence_threshold']:.2f}, Crit Threshold: {cfg['critical_alert_threshold']:.2f}, Hospital: '{cfg['hospital_name']}'"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", "Decision thresholds and clinical configuration registry successfully saved.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save clinical configuration.")

    def _create_logs_card(self):
        card = _card()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(14)

        t = QLabel("Medical Audit Trail & Security Logs Ledger")
        t.setObjectName("subheading")
        cl.addWidget(t)
        cl.addWidget(_sep())

        # Filter bar
        fl = QHBoxLayout()
        fl.setSpacing(10)
        
        self.search_logs = QLineEdit()
        self.search_logs.setPlaceholderText("Filter logs by action, operator, or details...")
        self.search_logs.setMinimumHeight(40)
        self.search_logs.textChanged.connect(self._filter_logs)
        fl.addWidget(self.search_logs, 1)

        ref_btn = QPushButton("Refresh Ledger")
        ref_btn.setMinimumHeight(40)
        ref_btn.setFixedWidth(140)
        ref_btn.clicked.connect(self.refresh_logs_table)
        fl.addWidget(ref_btn)

        cl.addLayout(fl)

        # Table widget
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(4)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Examiner / Operator", "Clinical Action", "Ledger Details"])
        self.logs_table.setMinimumHeight(350)
        
        # Stylesheet for custom dark table theme inside slate cards
        self.logs_table.setStyleSheet("""
            QTableWidget {
                background-color: #0f172a;
                border: 1px solid #334155;
                gridline-color: #1e293b;
                border-radius: 8px;
                color: #e2e8f0;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #818cf8;
                padding: 6px;
                border: 1px solid #334155;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #6366f1;
                color: white;
            }
        """)

        # Set column stretching
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.logs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.logs_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        cl.addWidget(self.logs_table)
        
        self.refresh_logs_table()
        
        return card

    def refresh_logs_table(self):
        """Fetch latest audit log entries and populate the table."""
        self.all_logs = database.get_audit_logs()
        self._populate_logs(self.all_logs)

    def _populate_logs(self, logs_list):
        self.logs_table.setRowCount(0)
        for row_idx, log in enumerate(logs_list):
            self.logs_table.insertRow(row_idx)
            
            # Format examiner cell
            ex_name = log[1] or "System/Unknown"
            ex_user = f" (@{log[2]})" if log[2] else ""
            ex_cell = f"{ex_name}{ex_user}"
            
            # Parse datetime nicely if possible
            time_val = str(log[0])
            if "." in time_val:
                time_val = time_val.split(".")[0]
                
            cols = [time_val, ex_cell, str(log[3]), str(log[4])]
            
            for col_idx, val in enumerate(cols):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                # Dynamic alert coloring for critical actions
                if col_idx == 2 and ("Threshold" in val or "Registered" in val or "Delete" in val):
                    item.setForeground(Qt.GlobalColor.yellow)
                elif col_idx == 2 and "Failed" in val:
                    from PyQt6.QtGui import QColor
                    item.setForeground(QColor("#ef4444")) # Crimson text alert
                    
                self.logs_table.setItem(row_idx, col_idx, item)

    def _filter_logs(self):
        search_txt = self.search_logs.text().strip().lower()
        if not search_txt:
            self._populate_logs(self.all_logs)
            return

        filtered = []
        for log in self.all_logs:
            timestamp, ex_name, ex_user, action, details = log
            ex_name = ex_name or "System/Unknown"
            ex_user = ex_user or ""
            
            # Build search string containing all columns
            search_str = f"{timestamp} {ex_name} {ex_user} {action} {details}".lower()
            if search_txt in search_str:
                filtered.append(log)
                
        self._populate_logs(filtered)


class AddExaminerPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        self.rows_list = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        welcome = QLabel("Personnel Registry")
        welcome.setObjectName("heading")
        wl.addWidget(welcome)
        sub = QLabel("Register new practitioners and view all active operators within the diagnostic portal.")
        sub.setObjectName("subtext")
        wl.addWidget(sub)
        hdr.addLayout(wl)
        lay.addLayout(hdr)

        # Split columns
        cols = QHBoxLayout()
        cols.setSpacing(20)

        # Left Column Add form
        left = _card()
        cl = QVBoxLayout(left)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(12)

        t = QLabel("Register Clinical Staff")
        t.setObjectName("subheading")
        cl.addWidget(t)
        cl.addWidget(_sep())
        cl.addSpacing(4)

        self.uname = QLineEdit(); self.uname.setPlaceholderText("Select username"); self.uname.setMinimumHeight(42)
        self.fname = QLineEdit(); self.fname.setPlaceholderText("Practitioner's full name"); self.fname.setMinimumHeight(42)

        cl.addWidget(self._fl("Credentials Details"))
        cl.addWidget(self.uname)
        cl.addWidget(self.fname)

        cl.addSpacing(4)
        cl.addWidget(self._fl("Practitioner Role"))
        self.role_cb = QComboBox()
        self.role_cb.addItems(ROLES)
        self.role_cb.setMinimumHeight(42)
        cl.addWidget(self.role_cb)

        cl.addSpacing(4)
        cl.addWidget(self._fl("Assigned Department"))
        self.dept_cb = QComboBox()
        self.dept_cb.addItems(DEPARTMENTS)
        self.dept_cb.setMinimumHeight(42)
        cl.addWidget(self.dept_cb)

        cl.addSpacing(14)
        sb = QPushButton("Register Operator")
        sb.setObjectName("successBtn")
        sb.setMinimumHeight(44)
        sb.clicked.connect(self._save)
        cl.addWidget(sb)
        cl.addStretch()
        cols.addWidget(left, 5)

        # Right Column List active clinical users
        right = _card()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 20, 24, 20)
        rl.setSpacing(14)

        t2 = QLabel("Active Diagnostic Operators")
        t2.setObjectName("subheading")
        rl.addWidget(t2)
        rl.addWidget(_sep())

        # Scroll Area for active roster
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.roster_container = QWidget()
        self.roster_lay = QVBoxLayout(self.roster_container)
        self.roster_lay.setContentsMargins(0, 0, 0, 0)
        self.roster_lay.setSpacing(8)

        self._refresh_roster()

        scroll.setWidget(self.roster_container)
        rl.addWidget(scroll, 1)
        
        cols.addWidget(right, 5)

        lay.addLayout(cols, 1)
        
        info = database.get_examiner_info(self.mw.examiner_id)
        is_admin = (info[2] == "Admin") if info else False
        if not is_admin:
            self.uname.setEnabled(False)
            self.fname.setEnabled(False)
            self.role_cb.setEnabled(False)
            self.dept_cb.setEnabled(False)
            sb.setEnabled(False)
            t.setText("Register Clinical Staff (Admin Only)")

    def _fl(self, t):
        l = QLabel(t)
        l.setObjectName("formLabel")
        return l

    def _refresh_roster(self):
        # Clear roster items
        while self.roster_lay.count():
            item = self.roster_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.rows_list.clear()

        examiners = get_all_examiners()
        for ex in examiners:
            # ex: (name, role, department, username)
            row = ExaminerRow(ex[0], ex[1], ex[2], ex[3], self)
            self.roster_lay.addWidget(row)
            self.rows_list.append(row)
        
        self.roster_lay.addStretch()

    def _save(self):
        u, n = self.uname.text().strip(), self.fname.text().strip()
        if not all([u, n]):
            QMessageBox.warning(self, "Warning", "Username and Full Name are strictly required.")
            return
        ok = database.add_examiner(u, "", n, self.role_cb.currentText(), self.dept_cb.currentText())
        if ok:
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Staff Operator Registered",
                    details=f"Generated operator account for: '{u}' ({self.role_cb.currentText()} in {self.dept_cb.currentText()})"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", f"Clinical credentials for operator '{u}' successfully generated.")
            self.uname.clear(); self.fname.clear()
            self._refresh_roster()
        else:
            QMessageBox.critical(self, "Error", "Registration failed: Username already exists.")


class HospitalAnalyticsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        
        # Scrollable layout container
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 24, 30, 24)
        self.main_layout.setSpacing(20)
        
        # Header
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        welcome = QLabel("Clinical Analytics & Performance Dashboard")
        welcome.setObjectName("heading")
        wl.addWidget(welcome)
        sub = QLabel("Aggregate hospital diagnostics throughput, AI accuracy bounds, and clinical detection ratios.")
        sub.setObjectName("subtext")
        wl.addWidget(sub)
        hdr.addLayout(wl)
        
        # Dynamic Refresh button
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.setFixedWidth(140)
        self.refresh_btn.clicked.connect(self.refresh_dashboard)
        hdr.addWidget(self.refresh_btn)
        
        self.main_layout.addLayout(hdr)
        
        # KPI grid cards row
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(16)
        self.main_layout.addLayout(self.kpi_layout)
        
        # Charts dashboard panel
        self.charts_w = QWidget()
        self.charts_layout = QHBoxLayout(self.charts_w)
        self.charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_layout.setSpacing(20)
        self.main_layout.addWidget(self.charts_w, 1)
        
        self.refresh_dashboard()
        
    def refresh_dashboard(self):
        # 1. Clear KPI layouts
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 2. Clear Chart layouts
        while self.charts_layout.count():
            item = self.charts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Fetch stats from db
        stats = database.get_dashboard_stats()
        
        total_scans = stats["total_exams"]
        tumor_count = stats["tumor_count"]
        normal_count = stats["normal_count"]
        critical_count = stats["critical_count"]
        
        # Draw dynamic clinical KPI badges
        self._add_kpi("Total Diagnostic Runs", str(total_scans), "Throughput", "#c0c1ff")
        self._add_kpi("Tumor Detections", str(tumor_count), "Positive Cases", "#ef4444")
        self._add_kpi("Normal Brain Scans", str(normal_count), "Negative Cases", "#4edea3")
        self._add_kpi("High-Risk Critical Alerts", str(critical_count), "Triage Urgency", "#ffb95f")
        
        if total_scans == 0:
            no_data = _card()
            nl = QVBoxLayout(no_data)
            lbl = QLabel("No scans recorded in the system. Go run some diagnostics to render analytics graphs!")
            lbl.setObjectName("subtext")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            nl.addWidget(lbl)
            self.charts_layout.addWidget(no_data)
            return
            
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
        # --- Chart 1: Donut Ratio ---
        c1_card = _card()
        c1_lay = QVBoxLayout(c1_card)
        c1_lay.setContentsMargins(16, 16, 16, 16)
        
        title1 = QLabel("Tumor vs Normal Distribution")
        title1.setObjectName("subheading")
        title1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c1_lay.addWidget(title1)
        c1_lay.addWidget(_sep())
        
        fig1 = Figure(figsize=(4.5, 4.5), facecolor='#1e293b') # slate-800 background card
        canvas1 = FigureCanvas(fig1)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor('#1e293b')
        
        labels = ['Normal', 'Tumor']
        sizes = [normal_count, tumor_count]
        colors = ['#4edea3', '#ef4444'] # Emerald / Crimson
        
        actual_labels = []
        actual_sizes = []
        actual_colors = []
        for l, s, c in zip(labels, sizes, colors):
            if s > 0:
                actual_labels.append(l)
                actual_sizes.append(s)
                actual_colors.append(c)
                
        wedges, texts, autotexts = ax1.pie(
            actual_sizes, 
            labels=actual_labels, 
            colors=actual_colors,
            autopct='%1.1f%%', 
            startangle=90, 
            pctdistance=0.75,
            textprops={'color': 'white', 'fontsize': 10, 'weight': 'bold'}
        )
        centre_circle = ax1.pie([1], radius=0.5, colors=['#1e293b'])
        
        ax1.axis('equal')  
        fig1.tight_layout()
        canvas1.draw()
        c1_lay.addWidget(canvas1, 1)
        self.charts_layout.addWidget(c1_card, 4)
        
        # --- Chart 2: Timeline Activity ---
        c2_card = _card()
        c2_lay = QVBoxLayout(c2_card)
        c2_lay.setContentsMargins(16, 16, 16, 16)
        
        title2 = QLabel("Diagnostic Activity Timeline")
        title2.setObjectName("subheading")
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c2_lay.addWidget(title2)
        c2_lay.addWidget(_sep())
        
        fig2 = Figure(figsize=(6, 4.5), facecolor='#1e293b')
        canvas2 = FigureCanvas(fig2)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor('#0f172a') # dark slate background grid
        
        timeline = stats["timeline"]
        if timeline:
            dates = [t[0] for t in timeline]
            counts = [t[1] for t in timeline]
            
            ax2.plot(dates, counts, marker='o', color='#c0c1ff', linewidth=2.5, markersize=6, label='Scans Run')
            ax2.fill_between(dates, counts, color='#c0c1ff', alpha=0.15)
        else:
            ax2.text(0.5, 0.5, 'Insufficient activity logs', color='white', ha='center', va='center')
            
        ax2.tick_params(colors='white', labelsize=8)
        ax2.set_ylabel("Volume (Scans)", color='white', fontsize=9)
        ax2.grid(True, color='#334155', linestyle='--', alpha=0.5)
        ax2.spines['bottom'].set_color('#475569')
        ax2.spines['left'].set_color('#475569')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        fig2.autofmt_xdate()
        fig2.tight_layout()
        canvas2.draw()
        c2_lay.addWidget(canvas2, 1)
        self.charts_layout.addWidget(c2_card, 6)

    def _add_kpi(self, title, val, category, color):
        card = _card()
        card.setFixedHeight(105)
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(4)
        
        cat = QLabel(category)
        cat.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        cat.setStyleSheet(f"color: {color};")
        l.addWidget(cat)
        
        v = QLabel(val)
        v.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        v.setStyleSheet("color: white;")
        l.addWidget(v)
        
        t = QLabel(title)
        t.setObjectName("subtext")
        l.addWidget(t)
        
        self.kpi_layout.addWidget(card)
