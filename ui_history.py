"""Patient history page with PDF report generation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from fpdf import FPDF
import os, subprocess
import database


class PatientHistoryPage(QWidget):
    def __init__(self, main_win, patient_id):
        super().__init__()
        self.mw = main_win
        self.pid = patient_id

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 30)
        lay.setSpacing(16)

        # Header row
        hdr = QHBoxLayout()
        back = QPushButton("⬅  Back to Selection")
        back.setObjectName("backBtn")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda: self.mw.pop_page(self))
        hdr.addWidget(back)
        hdr.addStretch()

        pdf_btn = QPushButton("🖨️  Generate PDF Report")
        pdf_btn.setObjectName("accentBtn")
        pdf_btn.setMinimumHeight(40)
        pdf_btn.clicked.connect(self._gen_pdf)
        hdr.addWidget(pdf_btn)
        lay.addLayout(hdr)

        title = QLabel("📊  Patient History")
        title.setObjectName("heading")
        lay.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setObjectName("card")
        self.cl = QVBoxLayout(container)
        self.cl.setContentsMargins(20, 20, 20, 20)
        self.cl.setSpacing(12)

        self.history = database.get_patient_history(patient_id)
        if not self.history:
            e = QLabel("No past examinations found.")
            e.setObjectName("subtext")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cl.addWidget(e)
        else:
            for exam in self.history:
                self._add_card(exam)

        self.cl.addStretch()
        scroll.setWidget(container)
        lay.addWidget(scroll)

    def _add_card(self, exam):
        card = QFrame()
        card.setObjectName("innerCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(6)

        date_str = str(exam[4]).split(".")[0]
        examiner = exam[5] if exam[5] else "Unknown"

        top = QLabel(f"📅 {date_str}   |   📁 {exam[1]}")
        top.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        cl.addWidget(top)

        row = QHBoxLayout()
        color = "#ef4444" if exam[2] == "Tumor" else "#10b981"
        res = QLabel(f"Result: {exam[2]} ({exam[3]*100:.1f}%)")
        res.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 14px;")
        row.addWidget(res)
        row.addStretch()
        ex_lbl = QLabel(f"Examiner: {examiner}")
        ex_lbl.setObjectName("subtext")
        row.addWidget(ex_lbl)
        cl.addLayout(row)

        self.cl.addWidget(card)

    def _gen_pdf(self):
        info = database.get_patient_info(self.pid)
        if not info:
            QMessageBox.critical(self, "Error", "Patient info not found.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, "Brain Tumor Diagnostic Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Patient Details:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, f"Name: {info[1]}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Age: {info[2] or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Gender: {info[3] or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Contact: {info[4] or 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Examination History:", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        for exam in self.history:
            date_str = str(exam[4]).split(".")[0]
            examiner = exam[5] if exam[5] else "Unknown"
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"Date: {date_str}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 8, f"Image File: {exam[1]}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"Examiner: {examiner}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"Diagnosis: {exam[2]} ({exam[3]*100:.1f}%)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

        fn = f"report_{info[1].replace(' ', '_')}.pdf"
        try:
            pdf.output(fn)
            QMessageBox.information(self, "Success", f"Report saved as {fn}")
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate PDF: {e}")
