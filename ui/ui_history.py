"""Patient history page with PDF report generation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from fpdf import FPDF
import os, subprocess
from core import database


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
        back = QPushButton("Back to Selection")
        back.setObjectName("backBtn")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda: self.mw.pop_page(self))
        hdr.addWidget(back)
        hdr.addStretch()

        pdf_btn = QPushButton("Generate PDF Report")
        pdf_btn.setObjectName("accentBtn")
        pdf_btn.setMinimumHeight(40)
        pdf_btn.clicked.connect(self._gen_pdf)
        hdr.addWidget(pdf_btn)
        lay.addLayout(hdr)

        title = QLabel("Patient History")
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
        filename = os.path.basename(exam[1])

        top = QLabel(f"{date_str}   |   {filename}")
        top.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        cl.addWidget(top)

        row = QHBoxLayout()
        color = "#ef4444" if exam[2] == "Tumor" else "#10b981"
        res = QLabel(f"Result: {exam[2]} ({exam[3]*100:.1f}%)")
        res.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 13px;")
        row.addWidget(res)
        
        row.addStretch()
        
        ex_lbl = QLabel(f"Examiner: {examiner}")
        ex_lbl.setObjectName("subtext")
        row.addWidget(ex_lbl)
        
        # Spacer & Individual PDF Print button
        row.addSpacing(14)
        btn = QPushButton("Print Report")
        btn.setObjectName("accentBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(34)
        btn.clicked.connect(lambda _, e=exam: self._gen_single_report(e))
        row.addWidget(btn)
        
        cl.addLayout(row)
        self.cl.addWidget(card)

    def _gen_single_report(self, exam):
        # exam: (exam_id, image_name, prediction, confidence_score, exam_date, examiner_name, heatmap_path)
        from reporting.reporting import ClinicalReportGenerator
        
        info = database.get_patient_info(self.pid)
        if not info:
            QMessageBox.critical(self, "Error", "Patient info not found.")
            return

        p_name = info[1].replace(' ', '_')
        date_clean = str(exam[4]).split(" ")[0]
        
        # Ensure reports folder exists inside workspace
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        fn = os.path.join(reports_dir, f"diagnostic_report_{p_name}_{date_clean}_exam_{exam[0]}.pdf")
        
        try:
            generator = ClinicalReportGenerator(self.pid, self.mw.examiner_id)
            
            # Prepare exam data
            exam_data = {
                "date": str(exam[4]).split(".")[0],
                "image_name": os.path.basename(exam[1]),
                "original_path": exam[1],    # Secure copied original scan path
                "heatmap_path": exam[6],     # Secure generated heatmap path
                "prediction": exam[2],
                "confidence": exam[3]
            }
            
            generator.generate_pdf(exam_data, fn)
            
            # LOG EVENT
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Diagnostic Report Exported",
                    details=f"Exported diagnostic report for Patient ID: {self.pid}, Exam ID: {exam[0]} to: {fn}"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", f"Diagnostic report saved as:\n{fn}")
            
            # Auto-open
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
                
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Could not generate diagnostic report:\n{ex}")

    def _gen_pdf(self):
        info = database.get_patient_info(self.pid)
        if not info:
            QMessageBox.critical(self, "Error", "Patient info not found.")
            return

        from core import config_registry
        cfg = config_registry.load_config()
        hospital_name = cfg.get("hospital_name", "Neural Diagnostics Center")

        pdf = FPDF()
        pdf.add_page()
        
        # Color Theme: Deep Indigo / Slate Grey
        primary_color = (15, 23, 42)    # #0f172a
        accent_color = (99, 102, 241)   # #6366f1
        border_color = (226, 232, 240)  # #e2e8f0
        text_muted = (100, 116, 139)    # #64748b

        # ─── HEADER ───
        pdf.set_fill_color(*primary_color)
        pdf.rect(0, 0, 210, 40, "F")
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, hospital_name.upper(), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 5, "Patient Examination & Diagnostic History Log", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(20)

        # ─── DOCUMENT TITLE ───
        pdf.set_text_color(*primary_color)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "PATIENT HISTORY RECORD", new_x="LMARGIN", new_y="NEXT", align="L")
        
        # Thin Divider
        pdf.set_draw_color(*accent_color)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        # ─── PATIENT DETAILS ───
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(90, 6, "PATIENT INFORMATION", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 10)
        p_name = info[1]
        p_age = info[2] or "N/A"
        p_gender = info[3] or "N/A"
        p_contact = info[4] or "N/A"
        
        pdf.cell(90, 5, f"Name: {p_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(90, 5, f"Age / Gender: {p_age} yrs / {p_gender}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(90, 5, f"Contact: {p_contact}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # ─── EXAMINATION HISTORY TABLE ───
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*primary_color)
        pdf.cell(0, 10, "DIAGNOSTIC TIMELINE", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        for exam in self.history:
            date_str = str(exam[4]).split(".")[0]
            examiner = exam[5] if exam[5] else "System Operator"
            filename = os.path.basename(exam[1])
            pred = exam[2]
            conf = exam[3] * 100
            
            # Container box
            pdf.set_draw_color(*border_color)
            pdf.set_line_width(0.3)
            pdf.set_fill_color(248, 250, 252) # Slate-50 background
            
            y_start = pdf.get_y()
            # If box might overflow page, add new page
            if y_start > 250:
                pdf.add_page()
                y_start = pdf.get_y()
                
            pdf.rect(10, y_start, 190, 26, "FD")
            
            # Row 1: Date and Examiner
            pdf.set_xy(15, y_start + 4)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(90, 5, f"Date: {date_str}", align="L")
            
            pdf.set_xy(110, y_start + 4)
            pdf.set_text_color(*text_muted)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(85, 5, f"Attending Examiner: Dr. {examiner}", align="R", new_x="LMARGIN", new_y="NEXT")
            
            # Row 2: Scan details
            pdf.set_xy(15, y_start + 10)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*text_muted)
            
            # truncate filename if too long
            disp_file = filename if len(filename) < 40 else filename[:37] + "..."
            pdf.cell(90, 5, f"Scan File: {disp_file}", align="L")
            
            # Row 3: Results
            pdf.set_xy(15, y_start + 16)
            pdf.set_font("Helvetica", "B", 10)
            if pred == "Tumor":
                pdf.set_text_color(239, 68, 68) # Red (#ef4444)
                pred_text = f"TUMOR DETECTED | Confidence: {conf:.1f}%"
            else:
                pdf.set_text_color(16, 185, 129) # Emerald (#10b981)
                pred_text = f"NORMAL (NO TUMOR) | Confidence: {conf:.1f}%"
                
            pdf.cell(180, 5, pred_text, align="L", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_y(y_start + 30)

        # Ensure reports folder exists inside workspace
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        fn = os.path.join(reports_dir, f"history_{info[1].replace(' ', '_')}.pdf")
        try:
            pdf.output(fn)
            
            # LOG EVENT
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="History Exported",
                    details=f"Exported timeline history for Patient ID: {self.pid} to: {fn}"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", f"History log saved as {fn}")
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate PDF: {e}")
