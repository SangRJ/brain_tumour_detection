from ui.utils import show_custom_msg
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

        # Header Layout
        info = database.get_patient_info(patient_id)
        p_name = info[1] if info else "Unknown Patient"
        
        top_bar = QHBoxLayout()
        back = QPushButton("Back to Selection")
        back.setObjectName("backBtn")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda: self.mw.pop_page(self))
        top_bar.addWidget(back)
        top_bar.addStretch()
        
        pdf_btn = QPushButton("Generate Full History PDF")
        pdf_btn.setObjectName("accentBtn")
        pdf_btn.setMinimumHeight(38)
        pdf_btn.clicked.connect(self._gen_pdf)
        top_bar.addWidget(pdf_btn)
        lay.addLayout(top_bar)
        
        title = QLabel("Patient History Record")
        title.setStyleSheet("font-size: 28px; font-weight: 700; ")
        lay.addWidget(title)
        
        sub = QLabel(f"Past neurological scans and diagnostic timeline for {p_name}.")
        sub.setObjectName("subtext")
        lay.addWidget(sub)
        lay.addSpacing(16)

        self.history = database.get_patient_history(patient_id)

        # KPI Cards Row
        kpi_lay = QHBoxLayout()
        kpi_lay.setSpacing(16)
        
        total_scans = len(self.history)
        tumor_count = sum(1 for e in self.history if e[2] == "Tumor")
        normal_count = total_scans - tumor_count
        
        def _kpi(title, val, color):
            c = QFrame()
            c.setObjectName("card")
            l = QVBoxLayout(c)
            l.setContentsMargins(16, 12, 16, 12)
            t = QLabel(title)
            t.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            v = QLabel(str(val))
            v.setStyleSheet(" font-size: 24px; font-weight: bold;")
            l.addWidget(t)
            l.addWidget(v)
            return c
            
        kpi_lay.addWidget(_kpi("Total Scans", total_scans, "#818cf8"))
        kpi_lay.addWidget(_kpi("Tumor Detections", tumor_count, "#ef4444"))
        kpi_lay.addWidget(_kpi("Normal Scans", normal_count, "#10b981"))
        
        lay.addLayout(kpi_lay)
        lay.addSpacing(20)

        # Table Wrapper
        table_wrap = QWidget()
        table_wrap.setObjectName("card")
        tl = QVBoxLayout(table_wrap)
        tl.setContentsMargins(20, 20, 20, 20)
        tl.setSpacing(0)
        
        # Table Header
        th = QHBoxLayout()
        cols = ["SCAN DATE", "FILE NAME", "DIAGNOSTIC STATUS", "CONFIDENCE", "EXAMINER", "ACTION"]
        widths = [140, 160, 140, 100, 140, 100]
        for c, w in zip(cols, widths):
            lbl = QLabel(c)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase;")
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
        self.cl = QVBoxLayout(self.container)
        self.cl.setContentsMargins(0, 0, 0, 0)
        self.cl.setSpacing(0)

        if not self.history:
            e = QLabel("No past examinations found.")
            e.setObjectName("subtext")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cl.addWidget(e)
        else:
            for i, exam in enumerate(self.history):
                self._add_row(exam)
                if i < len(self.history) - 1:
                    row_div = QFrame()
                    row_div.setFixedHeight(1)
                    row_div.setStyleSheet("background-color: #e2e8f0;")
                    self.cl.addWidget(row_div)

        self.cl.addStretch()
        scroll.setWidget(self.container)
        tl.addWidget(scroll)
        lay.addWidget(table_wrap)

    def _add_row(self, exam):
        row = QWidget()
        row.setMinimumHeight(60)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 8, 0, 8)
        
        date_str = str(exam[4]).split(".")[0]
        filename = os.path.basename(exam[1])
        pred = exam[2]
        conf = exam[3] * 100
        examiner = exam[5] if exam[5] else "System"

        # Widths must match header widths
        d_lbl = QLabel(date_str)
        d_lbl.setStyleSheet("color: #475569; font-size: 13px;")
        d_lbl.setFixedWidth(140)
        rl.addWidget(d_lbl)
        
        f_lbl = QLabel(filename[:18] + "..." if len(filename)>20 else filename)
        f_lbl.setStyleSheet(" font-size: 13px; font-weight: bold;")
        f_lbl.setFixedWidth(160)
        rl.addWidget(f_lbl)
        
        # Diagnostic Pill
        pill = QLabel()
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if pred == "Tumor":
            pill.setText("High Risk")
            pill.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        else:
            pill.setText("Normal")
            pill.setStyleSheet("background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        pill.setFixedSize(100, 24)
        
        p_wrap = QWidget()
        p_wrap.setFixedWidth(140)
        p_lay = QHBoxLayout(p_wrap)
        p_lay.setContentsMargins(0,0,0,0)
        p_lay.addWidget(pill, alignment=Qt.AlignmentFlag.AlignLeft)
        rl.addWidget(p_wrap)
        
        c_lbl = QLabel(f"{conf:.1f}%")
        c_lbl.setStyleSheet("color: #475569; font-size: 13px;")
        c_lbl.setFixedWidth(100)
        rl.addWidget(c_lbl)
        
        e_lbl = QLabel(examiner)
        e_lbl.setStyleSheet("color: #475569; font-size: 13px;")
        e_lbl.setFixedWidth(140)
        rl.addWidget(e_lbl)
        
        btn = QPushButton("Print")
        btn.setObjectName("ghostBtn")
        btn.setFixedSize(70, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda _, e=exam: self._gen_single_report(e))
        rl.addWidget(btn)
        
        self.cl.addWidget(row)

    def _gen_single_report(self, exam):
        # exam: (exam_id, image_name, prediction, confidence_score, exam_date, examiner_name, heatmap_path)
        from reporting.reporting import ClinicalReportGenerator
        
        info = database.get_patient_info(self.pid)
        if not info:
            show_custom_msg(self,  "Error",  "Patient info not found.", is_error=True)
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
            
            import secrets
            # Secure PDF with a cryptographically secure random PIN
            doc_password = secrets.token_hex(4).upper()
            generator.generate_pdf(exam_data, fn, password=doc_password)
            
            # LOG EVENT
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Encrypted Diagnostic Report Exported",
                    details=f"Exported encrypted diagnostic report for Patient ID: {self.pid}, Exam ID: {exam[0]} to: {fn}"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            show_custom_msg(self, "Export Successful", f"Encrypted diagnostic report saved securely as:\n{fn}\n\nDocument Password: {doc_password}")
            
            # Auto-open
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
                
        except Exception as ex:
            show_custom_msg(self,  "Error",  f"Could not generate diagnostic report:\n{ex}", is_error=True)

    def _gen_pdf(self):
        info = database.get_patient_info(self.pid)
        if not info:
            show_custom_msg(self,  "Error",  "Patient info not found.", is_error=True)
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
            
            import secrets
            doc_password = secrets.token_hex(4).upper()
            
            # Apply Encryption
            try:
                from pypdf import PdfReader, PdfWriter
                reader = PdfReader(fn)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.encrypt(doc_password)
                with open(fn, "wb") as f:
                    writer.write(f)
            except Exception as e:
                print(f"Error encrypting PDF: {e}")
            
            # LOG EVENT
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.mw.examiner_id,
                    action="Encrypted History Exported",
                    details=f"Exported encrypted timeline history for Patient ID: {self.pid} to: {fn}"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            show_custom_msg(self, "Export Successful", f"Encrypted timeline report saved securely as:\n{os.path.basename(fn)}\n\nDocument Password: {doc_password}")
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
        except Exception as e:
            show_custom_msg(self,  "Error",  f"Could not generate PDF: {e}", is_error=True)
