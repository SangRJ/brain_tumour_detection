"""
reporting.py — Clinical Diagnostic Report Generator (PDF).
Produces professional hospital reports containing patient history, practitioner signatures,
and displays the original MRI scan side-by-side with the AI-generated Grad-CAM heatmap.
"""
from fpdf import FPDF
import os
from core import database


class ClinicalReportGenerator:
    def __init__(self, patient_id, examiner_id):
        self.patient_id = patient_id
        self.examiner_id = examiner_id
        
        # Load details
        self.patient_info = database.get_patient_info(patient_id)
        self.examiner_info = database.get_examiner_info(examiner_id)

    def generate_pdf(self, exam_data, output_path):
        """
        Generate a detailed diagnostic report in PDF format.
        exam_data must contain:
            - date: datetime/string
            - image_name: filename string
            - original_path: path to original MRI image (if available)
            - heatmap_path: path to generated Grad-CAM heatmap image (if available)
            - prediction: 'Tumor' or 'No Tumor'
            - confidence: float (0.0 to 1.0)
        """
        if not self.patient_info:
            raise ValueError("Patient record not found.")

        # Instantiate PDF
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
        
        from core import config_registry
        cfg = config_registry.load_config()
        hospital_name = cfg.get("hospital_name", "Neural Diagnostics Center")

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, hospital_name.upper(), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 5, "AI-Powered Neurological Image Analysis & Diagnostic Portal", new_x="LMARGIN", new_y="NEXT", align="C")
        
        pdf.ln(20)

        # ─── DOCUMENT TITLE ───
        pdf.set_text_color(*primary_color)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "CLINICAL DIAGNOSTIC REPORT", new_x="LMARGIN", new_y="NEXT", align="L")
        
        # Thin Divider
        pdf.set_draw_color(*accent_color)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        # ─── META-DATA GRID (Patient & Examiner Details) ───
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "B", 11)
        
        # Left side - Patient details
        x_left = 10
        y_grid = pdf.get_y()
        pdf.set_xy(x_left, y_grid)
        pdf.cell(90, 6, "PATIENT INFORMATION", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 10)
        p_name = self.patient_info[1]
        p_age = self.patient_info[2] or "N/A"
        p_gender = self.patient_info[3] or "N/A"
        p_contact = self.patient_info[4] or "N/A"
        
        pdf.cell(90, 5, f"Name: {p_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(90, 5, f"Age / Gender: {p_age} yrs / {p_gender}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(90, 5, f"Contact: {p_contact}", new_x="LMARGIN", new_y="NEXT")
        
        # Right side - Examiner Details
        pdf.set_xy(110, y_grid)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(90, 6, "PRACTITIONER INTAKE", new_x="RMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 10)
        ex_name = self.examiner_info[1] if self.examiner_info else "System Operator"
        ex_role = self.examiner_info[2] if self.examiner_info else "Radiologist"
        ex_dept = self.examiner_info[3] if self.examiner_info else "Neurology"
        
        pdf.set_x(110)
        pdf.cell(90, 5, f"Name: Dr. {ex_name}", new_x="RMARGIN", new_y="NEXT")
        pdf.set_x(110)
        pdf.cell(90, 5, f"Role / Department: {ex_role} / {ex_dept}", new_x="RMARGIN", new_y="NEXT")
        pdf.set_x(110)
        pdf.cell(90, 5, f"Date of Intake: {exam_data.get('date')}", new_x="RMARGIN", new_y="NEXT")

        pdf.ln(12)

        # ─── DIAGNOSTIC RESULTS SUMMARY ───
        pdf.set_draw_color(*border_color)
        pdf.set_line_width(0.3)
        pdf.set_fill_color(248, 250, 252) # Slate-50 background
        
        res_y = pdf.get_y()
        pdf.rect(10, res_y, 190, 24, "FD")
        
        # Left Column — Diagnostic Criteria
        pdf.set_xy(15, res_y + 3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*text_muted)
        pdf.cell(90, 5, "DIAGNOSTIC CRITERIA", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        img_name = exam_data.get("image_name") or "Unknown"
        # Truncate to prevent overflowing columns
        if len(img_name) > 40:
            img_name = img_name[:37] + "..."
            
        pdf.cell(90, 5, f"MRI Scan Slice: {img_name}", new_x="LMARGIN", new_y="NEXT")
        
        # Right Column — AI Diagnostics
        pred = exam_data.get("prediction", "Unknown")
        conf = exam_data.get("confidence", 0.0) * 100
        
        pdf.set_xy(110, res_y + 3)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*text_muted)
        pdf.cell(85, 5, "AI PREDICTION RESULT", align="R", new_x="RMARGIN", new_y="NEXT")
        
        pdf.set_xy(110, res_y + 8)
        if pred == "Tumor":
            pdf.set_text_color(239, 68, 68) # Red (#ef4444)
            pred_text = f"TUMOR DETECTED | Confidence: {conf:.1f}%"
        else:
            pdf.set_text_color(16, 185, 129) # Emerald (#10b981)
            pred_text = f"NO TUMOR DETECTED (Normal) | Confidence: {conf:.1f}%"
            
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(85, 5, pred_text, align="R", new_x="RMARGIN", new_y="NEXT")
        
        pdf.ln(12)

        # ─── IMAGING SECTION (SIDE-BY-SIDE MRI & GRAD-CAM HEATMAP) ───
        pdf.set_text_color(*primary_color)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 6, "NEUROLOGICAL SCAN IMAGING & ACTIVATION ATTENTION", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        orig_img = exam_data.get("original_path")
        hm_img = exam_data.get("heatmap_path")
        
        # Robust Path Fallbacks
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if orig_img and not os.path.exists(orig_img):
            # Check 1: new dedicated folder
            fallback = os.path.join(base_dir, "images", "patient", "scans", os.path.basename(orig_img))
            if os.path.exists(fallback):
                orig_img = fallback
            else:
                # Check 2: old assets folder
                fallback_old = os.path.join(base_dir, "assets", "scans", os.path.basename(orig_img))
                if os.path.exists(fallback_old):
                    orig_img = fallback_old
                
        if hm_img and not os.path.exists(hm_img):
            # Check 1: new dedicated folder
            fallback = os.path.join(base_dir, "images", "patient", "heatmaps", os.path.basename(hm_img))
            if os.path.exists(fallback):
                hm_img = fallback
            else:
                # Check 2: old assets folder
                fallback_old = os.path.join(base_dir, "assets", "heatmaps", os.path.basename(hm_img))
                if os.path.exists(fallback_old):
                    hm_img = fallback_old
        
        img_y = pdf.get_y()
        img_width = 85
        img_height = 85
        
        # Render side-by-side images
        rendered_images = False
        
        # 1. Original scan image on the left
        if orig_img and os.path.exists(orig_img):
            try:
                pdf.image(orig_img, x=15, y=img_y, w=img_width, h=img_height)
                # Label
                pdf.set_xy(15, img_y + img_height + 2)
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(*text_muted)
                pdf.cell(img_width, 5, "Figure A: Original T2-Weighted MRI Scan Slice", align="C")
                rendered_images = True
            except Exception as e:
                print(f"[Report Error] Failed to embed original image: {e}")
        else:
            # Placeholder box
            pdf.set_draw_color(*border_color)
            pdf.rect(15, img_y, img_width, img_height)
            pdf.set_xy(15, img_y + (img_height/2) - 5)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(img_width, 5, "[ Original Scan Image Unavailable ]", align="C")

        # 2. Grad-CAM heatmap on the right
        if hm_img and os.path.exists(hm_img):
            try:
                pdf.image(hm_img, x=110, y=img_y, w=img_width, h=img_height)
                # Label
                pdf.set_xy(110, img_y + img_height + 2)
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(*text_muted)
                pdf.cell(img_width, 5, "Figure B: AI Grad-CAM Class Feature Activations", align="C")
                rendered_images = True
            except Exception as e:
                print(f"[Report Error] Failed to embed heatmap image: {e}")
        else:
            # Placeholder box
            pdf.set_draw_color(*border_color)
            pdf.rect(110, img_y, img_width, img_height)
            pdf.set_xy(110, img_y + (img_height/2) - 5)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(img_width, 5, "[ Grad-CAM Attention Map Unavailable ]", align="C")

        pdf.set_xy(10, img_y + img_height + 12)

        # ─── MEDICAL DISCLAIMER & SIGNATURE BLOCK ───
        pdf.set_line_width(0.3)
        pdf.set_draw_color(*border_color)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)
        
        disc_y = pdf.get_y()
        
        # Medical disclaimer on the left
        pdf.set_xy(10, disc_y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*text_muted)
        pdf.cell(100, 5, "DIAGNOSTIC DISCLAIMER", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", "", 8)
        disc_text = (
            "This report is generated using an advanced Convolutional Neural Network (CNN) "
            "model alongside Grad-CAM convolutional layer overlays. It is designed for clinical "
            "investigational assistance and research purposes only. The neural network's predictions "
            "do not constitute a definitive medical diagnosis and must be reviewed alongside "
            "independent physiological analysis by an authorized clinical professional before executing "
            "patient care."
        )
        pdf.multi_cell(110, 4, disc_text)
        
        # Signature block on the right
        pdf.set_xy(135, disc_y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*primary_color)
        pdf.cell(60, 5, "CLINICAL ATTESTATION", align="R", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(12)
        pdf.set_x(135)
        pdf.line(135, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)
        
        pdf.set_x(135)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*text_muted)
        pdf.cell(60, 5, f"Authorized Sign-Off: Dr. {ex_name}", align="R")

        # Save Report
        pdf.output(output_path)
