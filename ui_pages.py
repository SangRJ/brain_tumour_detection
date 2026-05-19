"""Patient selection, settings, and add examiner pages with rich clinical layouts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QMessageBox, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import database
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


class PatientRow(QFrame):
    clicked = pyqtSignal(int, str)  # patient_id, display_name

    def __init__(self, patient_id, name, age, gender, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.name = name
        self.display_name = f"[{patient_id}] {name}"
        self.setObjectName("listItemRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)
        
        icon = QLabel("👤")
        icon.setFont(QFont("Segoe UI", 12))
        lay.addWidget(icon)
        
        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lay.addWidget(name_lbl)
        
        lay.addStretch()
        
        if gender:
            g_lbl = QLabel(gender)
            g_lbl.setObjectName("badge")
            lay.addWidget(g_lbl)
            
        if age:
            a_lbl = QLabel(f"{age} yrs")
            a_lbl.setObjectName("badgeAccent")
            lay.addWidget(a_lbl)

    def mousePressEvent(self, event):
        self.clicked.emit(self.patient_id, self.display_name)


class ExaminerRow(QFrame):
    def __init__(self, name, role, dept, username, parent=None):
        super().__init__(parent)
        self.setObjectName("listItemRow")
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)
        
        icon = QLabel("🩺")
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


class PatientSelectionPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        self.selected_pid = None
        self.rows_list = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # ── TOP ROW: WELCOME & SYSTEM STATS OVERVIEW ────────────────
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        
        info = database.get_examiner_info(self.mw.examiner_id)
        ex_name = info[1] if info else "Examiner"
        
        welcome = QLabel(f"Welcome back, Dr. {ex_name}")
        welcome.setObjectName("heading")
        wl.addWidget(welcome)
        
        today_str = datetime.date.today().strftime("%B %d, %Y")
        sub = QLabel(f"Clinical Dashboard Overview  •  {today_str}")
        sub.setObjectName("subtext")
        wl.addWidget(sub)
        hdr.addLayout(wl)
        hdr.addStretch()
        
        status_card = QFrame()
        status_card.setStyleSheet("background-color: #064e3b; border-radius: 8px; padding: 6px 14px;")
        s_lay = QHBoxLayout(status_card)
        s_lay.setContentsMargins(6, 6, 6, 6)
        s_lbl = QLabel("●  SYSTEM ONLINE")
        s_lbl.setStyleSheet("color: #a7f3d0; font-size: 11px; font-weight: bold;")
        s_lay.addWidget(s_lbl)
        hdr.addWidget(status_card)
        lay.addLayout(hdr)

        # KPI Counter row
        kpi_lay = QHBoxLayout()
        kpi_lay.setSpacing(16)
        
        p_count, e_count, ex_count = get_stats()
        
        self.kpi_patients = KPICard("👥", "Patients Registered", str(p_count))
        self.kpi_exams = KPICard("🔬", "Diagnoses Completed", str(e_count))
        self.kpi_staff = KPICard("🩺", "Authorized Operators", str(ex_count))
        
        kpi_lay.addWidget(self.kpi_patients)
        kpi_lay.addWidget(self.kpi_exams)
        kpi_lay.addWidget(self.kpi_staff)
        lay.addLayout(kpi_lay)

        # ── MAIN LAYOUT: SPLIT CARDS ────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(20)

        # Left Column — Patient Directory
        left = _card()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(24, 20, 24, 20)
        ll.setSpacing(14)

        t = QLabel("Patient Directory")
        t.setObjectName("subheading")
        ll.addWidget(t)
        ll.addWidget(_sep())

        # Search Bar
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search patient directory by name...")
        self.search.setMinimumHeight(42)
        self.search.textChanged.connect(self._filter_patients)
        ll.addWidget(self.search)

        # Scroll Area for Patients List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.list_container = QWidget()
        self.list_lay = QVBoxLayout(self.list_container)
        self.list_lay.setContentsMargins(0, 0, 0, 0)
        self.list_lay.setSpacing(8)
        
        self.scroll.setWidget(self.list_container)
        ll.addWidget(self.scroll, 1)

        # Selected Indicator Status
        self.sel_status = QLabel("Please select a patient from the roster above")
        self.sel_status.setObjectName("subtext")
        self.sel_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sel_status.setStyleSheet("color: #64748b; font-style: italic; font-weight: 500;")
        ll.addWidget(self.sel_status)

        # Directory Action Button bar
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)
        
        self.eb = QPushButton("▶  New Examination")
        self.eb.setObjectName("successBtn")
        self.eb.setMinimumHeight(44)
        self.eb.setEnabled(False)
        self.eb.clicked.connect(self._new_exam)
        btn_bar.addWidget(self.eb, 1)

        self.vb = QPushButton("📊  View Past Results")
        self.vb.setMinimumHeight(44)
        self.vb.setEnabled(False)
        self.vb.clicked.connect(self._view_results)
        btn_bar.addWidget(self.vb, 1)
        
        ll.addLayout(btn_bar)
        
        self._refresh_patient_list()
        cols.addWidget(left, 6)

        # Right Column — Register Patient
        right = _card()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 20, 24, 20)
        rl.setSpacing(14)

        t2 = QLabel("Register New Patient")
        t2.setObjectName("subheading")
        rl.addWidget(t2)
        rl.addWidget(_sep())

        # Form Layout
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

        rl.addLayout(form_grid)
        rl.addSpacing(4)

        ab = QPushButton("Add & Initiate Scan")
        ab.setObjectName("accentBtn")
        ab.setMinimumHeight(44)
        ab.clicked.connect(self._add)
        rl.addWidget(ab)
        
        # Info Block to fill space cleanly
        rl.addStretch()
        info_block = QFrame()
        info_block.setStyleSheet("background-color: #0f172a; border-radius: 8px; border: 1px solid #334155;")
        ibl = QVBoxLayout(info_block)
        ibl.setContentsMargins(14, 12, 14, 12)
        ibl.setSpacing(4)
        
        it = QLabel("🔒  Secure Patient Intake Policy")
        it.setStyleSheet("color: #f8fafc; font-size: 11px; font-weight: bold;")
        ibl.addWidget(it)
        
        idsc = QLabel("Patient credentials, medical scan records, and Grad-CAM diagnostics are encrypted and stored locally under strict privacy protocols.")
        idsc.setObjectName("muted")
        idsc.setWordWrap(True)
        idsc.setStyleSheet("font-size: 10px; line-height: 14px;")
        ibl.addWidget(idsc)
        rl.addWidget(info_block)

        cols.addWidget(right, 4)
        lay.addLayout(cols, 1)

    def _refresh_patient_list(self):
        # Clear layout
        for r in self.rows_list:
            r.deleteLater()
        self.rows_list.clear()
        self.selected_pid = None
        self.eb.setEnabled(False)
        self.vb.setEnabled(False)
        self.sel_status.setText("Please select a patient from the roster above")
        self.sel_status.setStyleSheet("color: #64748b; font-style: italic; font-weight: 500;")

        self.patients = database.get_all_patients()
        for p in self.patients:
            # p: (patient_id, name, age, gender, contact_info)
            row = PatientRow(p[0], p[1], p[2], p[3], self)
            row.clicked.connect(self._on_patient_selected)
            self.list_lay.addWidget(row)
            self.rows_list.append(row)
        
        self.list_lay.addStretch()

    def _filter_patients(self, text):
        query = text.lower().strip()
        for row in self.rows_list:
            if not query or query in row.name.lower():
                row.show()
            else:
                row.hide()

    def _on_patient_selected(self, pid, display_name):
        self.selected_pid = pid
        self.sel_status.setText(f"Active Selection: {display_name}")
        self.sel_status.setStyleSheet("color: #6366f1; font-weight: bold; font-style: normal;")
        
        self.eb.setEnabled(True)
        self.vb.setEnabled(True)

        for row in self.rows_list:
            if row.patient_id == pid:
                row.setObjectName("listItemRowSelected")
            else:
                row.setObjectName("listItemRow")
            row.style().unpolish(row)
            row.style().polish(row)

    def _new_exam(self):
        if not self.selected_pid:
            return
        from ui_analysis import AnalysisPage
        self.mw.push_page(AnalysisPage(self.mw, self.selected_pid))

    def _view_results(self):
        if not self.selected_pid:
            return
        from ui_history import PatientHistoryPage
        self.mw.push_page(PatientHistoryPage(self.mw, self.selected_pid))

    def _add(self):
        n = self.pname.text().strip()
        if not n:
            QMessageBox.warning(self, "Warning", "Patient Name is required.")
            return
        age = None
        try:
            age = int(self.page.text().strip())
        except:
            pass
        pid = database.add_patient(n, age, self.pgender.text().strip(), self.pcontact.text().strip())
        QMessageBox.information(self, "Success", "Patient successfully added to local database.")
        
        # Reset and open scan immediately
        self.pname.clear()
        self.page.clear()
        self.pgender.clear()
        self.pcontact.clear()
        
        from ui_analysis import AnalysisPage
        self.mw.push_page(AnalysisPage(self.mw, pid))


class SettingsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 24, 30, 24)
        lay.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        wl = QVBoxLayout()
        wl.setSpacing(3)
        welcome = QLabel("⚙️  Profile & Security Center")
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

        # Left Column — Profile adjustments
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

        # Right Column — Info panel
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

        bl.addWidget(QLabel("🩺  ACTIVE SESSION OPERATOR"))
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
        health_lay.addWidget(self._hl("DB Status", "✅ Connected & Encrypted"))
        health_lay.addWidget(self._hl("AI Model Host", "TensorFlow Local CPU Runtime"))
        health_lay.addWidget(self._hl("Analysis Portals", "Standard Model + Grad-CAM Convolutional Layer"))
        health_lay.addWidget(self._hl("Diagnostics Cache", "sqlite3 Standard Engine"))

        rl.addLayout(health_lay)
        rl.addStretch()
        cols.addWidget(right, 5)

        lay.addLayout(cols, 1)

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
            QMessageBox.information(self, "Success", "Display name saved successfully.")
        else:
            QMessageBox.warning(self, "Warning", "Display name cannot be empty.")

    def _save_pw(self):
        p = self.pw_e.text().strip()
        if p:
            database.update_examiner_password(self.mw.examiner_id, p)
            QMessageBox.information(self, "Success", "Security credentials updated successfully.")
            self.pw_e.clear()
        else:
            QMessageBox.warning(self, "Warning", "Password cannot be empty.")


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
        welcome = QLabel("👤  Personnel Registry")
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

        # Left Column — Add form
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
        self.pw = QLineEdit(); self.pw.setPlaceholderText("Select secure password"); self.pw.setEchoMode(QLineEdit.EchoMode.Password); self.pw.setMinimumHeight(42)
        self.fname = QLineEdit(); self.fname.setPlaceholderText("Practitioner's full name"); self.fname.setMinimumHeight(42)

        cl.addWidget(self._fl("Credentials Details"))
        cl.addWidget(self.uname)
        cl.addWidget(self.pw)
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
        sb = QPushButton("Save & Register Operator")
        sb.setObjectName("successBtn")
        sb.setMinimumHeight(44)
        sb.clicked.connect(self._save)
        cl.addWidget(sb)
        cl.addStretch()
        cols.addWidget(left, 5)

        # Right Column — List active clinical users
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

    def _fl(self, t):
        l = QLabel(t)
        l.setObjectName("formLabel")
        return l

    def _refresh_roster(self):
        # Clear roster items
        for r in self.rows_list:
            r.deleteLater()
        self.rows_list.clear()

        examiners = get_all_examiners()
        for ex in examiners:
            # ex: (name, role, department, username)
            row = ExaminerRow(ex[0], ex[1], ex[2], ex[3], self)
            self.roster_lay.addWidget(row)
            self.rows_list.append(row)
        
        self.roster_lay.addStretch()

    def _save(self):
        u, p, n = self.uname.text().strip(), self.pw.text().strip(), self.fname.text().strip()
        if not all([u, p, n]):
            QMessageBox.warning(self, "Warning", "Username, Password, and Full Name are strictly required.")
            return
        ok = database.add_examiner(u, p, n, self.role_cb.currentText(), self.dept_cb.currentText())
        if ok:
            QMessageBox.information(self, "Success", f"Clinical credentials for operator '{u}' successfully generated.")
            self.uname.clear(); self.pw.clear(); self.fname.clear()
            self._refresh_roster()
        else:
            QMessageBox.critical(self, "Error", "Registration failed: Username already exists.")
