"""Patient selection, settings, and add examiner pages."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import database

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


class PatientSelectionPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        lay = QHBoxLayout(self)
        lay.setContentsMargins(50, 50, 50, 50)
        lay.setSpacing(30)

        # Left card — existing patients
        left = _card()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(30, 30, 30, 30)
        ll.setSpacing(12)

        t = QLabel("Select Existing Patient")
        t.setObjectName("subheading")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(t)
        ll.addWidget(_sep())
        ll.addSpacing(8)

        self.patients = database.get_all_patients()
        self.pdict = {f"[{p[0]}] {p[1]}": p[0] for p in self.patients}

        self.combo = QComboBox()
        self.combo.setMinimumHeight(44)
        if self.pdict:
            self.combo.addItems(list(self.pdict.keys()))
        else:
            self.combo.addItem("No patients found")
        ll.addWidget(self.combo)
        ll.addSpacing(8)

        eb = QPushButton("▶  New Examination")
        eb.setObjectName("successBtn")
        eb.setMinimumHeight(44)
        eb.clicked.connect(self._new_exam)
        ll.addWidget(eb)

        vb = QPushButton("📊  View Past Results")
        vb.setMinimumHeight(44)
        vb.clicked.connect(self._view_results)
        ll.addWidget(vb)
        ll.addStretch()
        lay.addWidget(left)

        # Right card — add patient
        right = _card()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(30, 30, 30, 30)
        rl.setSpacing(12)

        t2 = QLabel("Add New Patient")
        t2.setObjectName("subheading")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(t2)
        rl.addWidget(_sep())
        rl.addSpacing(8)

        self.pname = QLineEdit(); self.pname.setPlaceholderText("Patient Name"); self.pname.setMinimumHeight(44)
        self.page = QLineEdit(); self.page.setPlaceholderText("Age"); self.page.setMinimumHeight(44)
        self.pgender = QLineEdit(); self.pgender.setPlaceholderText("Gender"); self.pgender.setMinimumHeight(44)
        self.pcontact = QLineEdit(); self.pcontact.setPlaceholderText("Contact Info"); self.pcontact.setMinimumHeight(44)
        for w in [self.pname, self.page, self.pgender, self.pcontact]:
            rl.addWidget(w)
        rl.addSpacing(8)

        ab = QPushButton("Add & Select")
        ab.setObjectName("accentBtn")
        ab.setMinimumHeight(44)
        ab.clicked.connect(self._add)
        rl.addWidget(ab)
        rl.addStretch()
        lay.addWidget(right)

    def _get_pid(self):
        s = self.combo.currentText()
        return self.pdict.get(s)

    def _new_exam(self):
        pid = self._get_pid()
        if not pid:
            QMessageBox.warning(self, "Warning", "Please select a valid patient.")
            return
        from ui_analysis import AnalysisPage
        self.mw.push_page(AnalysisPage(self.mw, pid))

    def _view_results(self):
        pid = self._get_pid()
        if not pid:
            QMessageBox.warning(self, "Warning", "Please select a valid patient.")
            return
        from ui_history import PatientHistoryPage
        self.mw.push_page(PatientHistoryPage(self.mw, pid))

    def _add(self):
        n = self.pname.text().strip()
        if not n:
            QMessageBox.warning(self, "Warning", "Patient Name is required.")
            return
        age = None
        try: age = int(self.page.text().strip())
        except: pass
        pid = database.add_patient(n, age, self.pgender.text().strip(), self.pcontact.text().strip())
        QMessageBox.information(self, "Success", "Patient added.")
        from ui_analysis import AnalysisPage
        self.mw.push_page(AnalysisPage(self.mw, pid))


class SettingsPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = _card()
        card.setFixedWidth(420)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(10)

        t = QLabel("⚙️  Profile Settings")
        t.setObjectName("heading")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(t)
        cl.addWidget(_sep())
        cl.addSpacing(12)

        info = database.get_examiner_info(self.mw.examiner_id)
        cur = info[1] if info else ""

        cl.addWidget(self._fl("Update Name"))
        self.name_e = QLineEdit()
        self.name_e.setText(cur)
        self.name_e.setMinimumHeight(44)
        cl.addWidget(self.name_e)

        nb = QPushButton("Save Name")
        nb.setObjectName("accentBtn")
        nb.setMinimumHeight(44)
        nb.clicked.connect(self._save_name)
        cl.addWidget(nb)
        cl.addSpacing(16)

        cl.addWidget(self._fl("Update Password"))
        self.pw_e = QLineEdit()
        self.pw_e.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_e.setMinimumHeight(44)
        cl.addWidget(self.pw_e)

        pb = QPushButton("Save Password")
        pb.setObjectName("warnBtn")
        pb.setMinimumHeight(44)
        pb.clicked.connect(self._save_pw)
        cl.addWidget(pb)
        cl.addStretch()
        outer.addWidget(card)

    def _fl(self, t):
        l = QLabel(t)
        l.setObjectName("formLabel")
        return l

    def _save_name(self):
        n = self.name_e.text().strip()
        if n:
            database.update_examiner_name(self.mw.examiner_id, n)
            QMessageBox.information(self, "Success", "Name updated.")
        else:
            QMessageBox.warning(self, "Warning", "Name cannot be empty.")

    def _save_pw(self):
        p = self.pw_e.text().strip()
        if p:
            database.update_examiner_password(self.mw.examiner_id, p)
            QMessageBox.information(self, "Success", "Password updated.")
            self.pw_e.clear()
        else:
            QMessageBox.warning(self, "Warning", "Password cannot be empty.")


class AddExaminerPage(QWidget):
    def __init__(self, main_win):
        super().__init__()
        self.mw = main_win
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = _card()
        card.setFixedWidth(420)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(10)

        t = QLabel("👤  Add New Examiner")
        t.setObjectName("heading")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(t)
        cl.addWidget(_sep())
        cl.addSpacing(12)

        self.uname = QLineEdit(); self.uname.setPlaceholderText("Username"); self.uname.setMinimumHeight(44)
        self.pw = QLineEdit(); self.pw.setPlaceholderText("Password"); self.pw.setEchoMode(QLineEdit.EchoMode.Password); self.pw.setMinimumHeight(44)
        self.fname = QLineEdit(); self.fname.setPlaceholderText("Full Name"); self.fname.setMinimumHeight(44)

        for w in [self.uname, self.pw, self.fname]:
            cl.addWidget(w)

        cl.addSpacing(4)
        cl.addWidget(self._fl("Role"))
        self.role_cb = QComboBox()
        self.role_cb.addItems(ROLES)
        self.role_cb.setMinimumHeight(44)
        cl.addWidget(self.role_cb)

        cl.addSpacing(4)
        cl.addWidget(self._fl("Department"))
        self.dept_cb = QComboBox()
        self.dept_cb.addItems(DEPARTMENTS)
        self.dept_cb.setMinimumHeight(44)
        cl.addWidget(self.dept_cb)

        cl.addSpacing(12)
        sb = QPushButton("Save Examiner")
        sb.setObjectName("successBtn")
        sb.setMinimumHeight(44)
        sb.clicked.connect(self._save)
        cl.addWidget(sb)
        cl.addStretch()
        outer.addWidget(card)

    def _fl(self, t):
        l = QLabel(t)
        l.setObjectName("formLabel")
        return l

    def _save(self):
        u, p, n = self.uname.text().strip(), self.pw.text().strip(), self.fname.text().strip()
        if not all([u, p, n]):
            QMessageBox.warning(self, "Warning", "Username, Password, and Name are required.")
            return
        ok = database.add_examiner(u, p, n, self.role_cb.currentText(), self.dept_cb.currentText())
        if ok:
            QMessageBox.information(self, "Success", f"Examiner '{u}' added!")
            self.uname.clear(); self.pw.clear(); self.fname.clear()
        else:
            QMessageBox.critical(self, "Error", "Username already exists.")
