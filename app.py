import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os
import threading
import subprocess
from fpdf import FPDF

from inference import BrainTumorPredictor
from gradcam import GradCAM
from utils import preprocess_image, validate_image_file, overlay_heatmap
import database

# ── Appearance ──────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colour constants (Modern Slate/Indigo) ───────────────────────
_C = {
    "sidebar_bg":  "#0f172a",
    "header_bg":   "#0f172a",
    "card_bg":     "#1e293b",
    "surface":     "#334155",
    "background":  "#020617",
    "accent":      "#6366f1",  # Indigo
    "accent_hover":"#4f46e5",
    "success":     "#10b981",  # Emerald
    "success_dk":  "#059669",
    "danger":      "#ef4444",  # Red
    "danger_dk":   "#dc2626",
    "warn":        "#f59e0b",
    "text":        "#f8fafc",
    "text2":       "#94a3b8",
    "border":      "#334155",
}

IMAGE_DISPLAY_SIZE = (380, 380)

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Brain Tumor Diagnostics Management System")
        self.geometry("1420x870")
        self.minsize(1100, 700)
        self.configure(fg_color=_C["background"])
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # State
        self.examiner_id = None
        self.current_frame = None
        
        # Initialize with Login
        self.switch_frame(LoginFrame)

    def set_examiner(self, examiner_id):
        self.examiner_id = examiner_id

    def switch_frame(self, frame_class, *args, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self, *args, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

class LoginFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=0, column=0)
        
        frame = ctk.CTkFrame(wrap, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        frame.pack(padx=40, pady=40, ipadx=40, ipady=40)
        
        ctk.CTkLabel(frame, text="🧠\nDiagnostics Portal", font=("Helvetica", 28, "bold"), text_color=_C["text"]).pack(pady=(10, 30))
        
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=280, height=45, corner_radius=8)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=280, height=45, corner_radius=8)
        self.password_entry.pack(pady=10)
        
        self.login_btn = ctk.CTkButton(frame, text="Secure Login", command=self._login, width=280, height=45, corner_radius=8, fg_color=_C["accent"], hover_color=_C["accent_hover"], font=("Helvetica", 15, "bold"))
        self.login_btn.pack(pady=(20, 10))

        self.bind('<Return>', lambda event: self._login())
        
    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        examiner_id = database.authenticate(username, password)
        if examiner_id:
            self.app.set_examiner(examiner_id)
            self.app.switch_frame(MainViewFrame)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class MainViewFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color="transparent")
        self.app = app
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=_C["sidebar_bg"], border_width=1, border_color=_C["border"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) # Spacer
        
        ctk.CTkLabel(self.sidebar, text="🧠 MedDiagnostics", font=("Helvetica", 22, "bold"), text_color=_C["text"]).pack(pady=(30, 40), padx=20)
        
        info = database.get_examiner_info(self.app.examiner_id)
        name = info[1] if info and info[1] else "Examiner"
        
        user_card = ctk.CTkFrame(self.sidebar, fg_color=_C["surface"], corner_radius=8)
        user_card.pack(fill="x", padx=20, pady=(0, 30))
        ctk.CTkLabel(user_card, text=f"👤 {name}", font=("Helvetica", 14, "bold")).pack(pady=12)

        # Nav Buttons
        self.nav_btns = []
        self._add_nav_button("🔍 Patient Selection", PatientSelectionFrame)
        self._add_nav_button("⚙️ Settings", SettingsFrame)
        self._add_nav_button("👤 Add Examiner", AddExaminerFrame)
        
        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        # Logout
        logout_btn = ctk.CTkButton(self.sidebar, text="🚪 Logout", command=self._logout, 
                                   fg_color="transparent", hover_color=_C["danger"], text_color=_C["danger"], font=("Helvetica", 15, "bold"), height=45, anchor="w")
        logout_btn.pack(fill="x", padx=20, pady=20)
        
        # --- Content Area ---
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.current_content_frame = None
        
        # Default view
        self.switch_content(PatientSelectionFrame)

    def _add_nav_button(self, text, target_class):
        btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.switch_content(target_class),
                            fg_color="transparent", hover_color=_C["surface"], text_color=_C["text2"], font=("Helvetica", 15, "bold"), height=45, anchor="w")
        btn.pack(fill="x", padx=20, pady=5)
        self.nav_btns.append((btn, target_class))
        
    def switch_content(self, frame_class, *args, **kwargs):
        if self.current_content_frame is not None:
            self.current_content_frame.destroy()
            
        # Update nav buttons styling
        for btn, cls in self.nav_btns:
            if cls == frame_class or (cls == PatientSelectionFrame and frame_class in (PatientHistoryFrame, BrainTumorFrame)):
                btn.configure(fg_color=_C["accent"], text_color=_C["text"])
            else:
                btn.configure(fg_color="transparent", text_color=_C["text2"])

        self.current_content_frame = frame_class(self.content_area, self, *args, **kwargs)
        self.current_content_frame.grid(row=0, column=0, sticky="nsew")
        
    def _logout(self):
        self.app.examiner_id = None
        self.app.switch_frame(LoginFrame)

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, main_view):
        super().__init__(parent, fg_color="transparent")
        self.main_view = main_view
        self.app = main_view.app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=0, column=0)
        
        frame = ctk.CTkFrame(wrap, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        frame.pack(padx=20, pady=20, ipadx=40, ipady=40)
        
        ctk.CTkLabel(frame, text="⚙️ Profile Settings", font=("Helvetica", 24, "bold"), text_color=_C["text"]).pack(pady=(0, 25))
        
        info = database.get_examiner_info(self.app.examiner_id)
        current_name = info[1] if info else ""
        
        ctk.CTkLabel(frame, text="Update Name:", font=("Helvetica", 14)).pack(anchor="w", pady=(10, 5))
        self.name_entry = ctk.CTkEntry(frame, width=300, height=45, corner_radius=8)
        self.name_entry.insert(0, current_name)
        self.name_entry.pack()
        
        self.update_name_btn = ctk.CTkButton(frame, text="Save Name", command=self._update_name, width=300, height=45, fg_color=_C["accent"], corner_radius=8)
        self.update_name_btn.pack(pady=15)
        
        ctk.CTkLabel(frame, text="Update Password:", font=("Helvetica", 14)).pack(anchor="w", pady=(25, 5))
        self.password_entry = ctk.CTkEntry(frame, show="*", width=300, height=45, corner_radius=8)
        self.password_entry.pack()
        
        self.update_pw_btn = ctk.CTkButton(frame, text="Save Password", command=self._update_password, width=300, height=45, fg_color=_C["warn"], hover_color="#d97706", corner_radius=8)
        self.update_pw_btn.pack(pady=15)
        
    def _update_name(self):
        new_name = self.name_entry.get().strip()
        if new_name:
            database.update_examiner_name(self.app.examiner_id, new_name)
            messagebox.showinfo("Success", "Name updated successfully.")
        else:
            messagebox.showwarning("Warning", "Name cannot be empty.")
            
    def _update_password(self):
        new_pw = self.password_entry.get().strip()
        if new_pw:
            database.update_examiner_password(self.app.examiner_id, new_pw)
            messagebox.showinfo("Success", "Password updated successfully.")
            self.password_entry.delete(0, "end")
        else:
            messagebox.showwarning("Warning", "Password cannot be empty.")

class AddExaminerFrame(ctk.CTkFrame):
    def __init__(self, parent, main_view):
        super().__init__(parent, fg_color="transparent")
        self.main_view = main_view
        self.app = main_view.app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=0, column=0)
        
        frame = ctk.CTkFrame(wrap, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        frame.pack(padx=20, pady=20, ipadx=40, ipady=40)
        
        ctk.CTkLabel(frame, text="👤 Add New Examiner", font=("Helvetica", 24, "bold"), text_color=_C["text"]).pack(pady=(0, 25))
        
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=300, height=45, corner_radius=8)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=300, height=45, corner_radius=8)
        self.password_entry.pack(pady=10)
        
        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", width=300, height=45, corner_radius=8)
        self.name_entry.pack(pady=10)
        
        self.role_entry = ctk.CTkEntry(frame, placeholder_text="Role (e.g. Radiologist)", width=300, height=45, corner_radius=8)
        self.role_entry.pack(pady=10)
        
        self.save_btn = ctk.CTkButton(frame, text="Save Examiner", command=self._save, width=300, height=45, fg_color=_C["success"], hover_color=_C["success_dk"], corner_radius=8)
        self.save_btn.pack(pady=20)
        
    def _save(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        name = self.name_entry.get()
        role = self.role_entry.get()
        
        if not all([username, password, name]):
            messagebox.showwarning("Warning", "Username, Password, and Name are required.")
            return
            
        success = database.add_examiner(username, password, name, role)
        if success:
            messagebox.showinfo("Success", f"Examiner '{username}' added successfully!")
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            self.role_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Username already exists. Please choose another.")

class PatientSelectionFrame(ctk.CTkFrame):
    def __init__(self, parent, main_view):
        super().__init__(parent, fg_color="transparent")
        self.main_view = main_view
        self.app = main_view.app
        
        self.grid_columnconfigure((0,1), weight=1, uniform="col")
        self.grid_rowconfigure(0, weight=1)
        
        # Existing Patients
        exist_wrap = ctk.CTkFrame(self, fg_color="transparent")
        exist_wrap.grid(row=0, column=0, sticky="nsew", padx=(60, 20), pady=60)
        
        exist_frame = ctk.CTkFrame(exist_wrap, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        exist_frame.pack(fill="both", expand=True, ipadx=20, ipady=30)
        
        ctk.CTkLabel(exist_frame, text="Select Existing Patient", font=("Helvetica", 22, "bold")).pack(pady=(10, 25))
        
        self.patients = database.get_all_patients()
        self.patient_dict = {f"[{p[0]}] {p[1]}": p[0] for p in self.patients}
        
        self.patient_combo = ctk.CTkComboBox(exist_frame, values=list(self.patient_dict.keys()) if self.patient_dict else ["No patients found"], width=300, height=45, corner_radius=8)
        self.patient_combo.pack(pady=15)
        
        ctk.CTkButton(exist_frame, text="▶ New Examination", command=self._new_exam, width=300, height=45, fg_color=_C["success"], hover_color=_C["success_dk"], corner_radius=8, font=("Helvetica", 14, "bold")).pack(pady=15)
        ctk.CTkButton(exist_frame, text="📊 View Past Results", command=self._view_results, width=300, height=45, fg_color=_C["surface"], corner_radius=8, font=("Helvetica", 14, "bold")).pack(pady=10)
        
        # Add New Patient
        add_wrap = ctk.CTkFrame(self, fg_color="transparent")
        add_wrap.grid(row=0, column=1, sticky="nsew", padx=(20, 60), pady=60)
        
        add_frame = ctk.CTkFrame(add_wrap, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        add_frame.pack(fill="both", expand=True, ipadx=20, ipady=30)
        
        ctk.CTkLabel(add_frame, text="Or Add New Patient", font=("Helvetica", 22, "bold")).pack(pady=(10, 25))
        
        self.new_name = ctk.CTkEntry(add_frame, placeholder_text="Patient Name", width=300, height=45, corner_radius=8)
        self.new_name.pack(pady=10)
        
        self.new_age = ctk.CTkEntry(add_frame, placeholder_text="Age", width=300, height=45, corner_radius=8)
        self.new_age.pack(pady=10)
        
        self.new_gender = ctk.CTkEntry(add_frame, placeholder_text="Gender", width=300, height=45, corner_radius=8)
        self.new_gender.pack(pady=10)
        
        self.new_contact = ctk.CTkEntry(add_frame, placeholder_text="Contact Info", width=300, height=45, corner_radius=8)
        self.new_contact.pack(pady=10)
        
        ctk.CTkButton(add_frame, text="Add & Select", command=self._add_patient, width=300, height=45, fg_color=_C["accent"], corner_radius=8, font=("Helvetica", 14, "bold")).pack(pady=25)
        
    def _new_exam(self):
        selection = self.patient_combo.get()
        if selection in self.patient_dict:
            patient_id = self.patient_dict[selection]
            self.main_view.switch_content(BrainTumorFrame, patient_id)
        else:
            messagebox.showwarning("Warning", "Please select a valid patient.")

    def _view_results(self):
        selection = self.patient_combo.get()
        if selection in self.patient_dict:
            patient_id = self.patient_dict[selection]
            self.main_view.switch_content(PatientHistoryFrame, patient_id)
        else:
            messagebox.showwarning("Warning", "Please select a valid patient.")
            
    def _add_patient(self):
        name = self.new_name.get().strip()
        age_str = self.new_age.get().strip()
        gender = self.new_gender.get().strip()
        contact = self.new_contact.get().strip()
        
        if not name:
            messagebox.showwarning("Warning", "Patient Name is required.")
            return
            
        age = None
        if age_str:
            try:
                age = int(age_str)
            except ValueError:
                pass
                
        patient_id = database.add_patient(name, age, gender, contact)
        messagebox.showinfo("Success", "Patient added.")
        self.main_view.switch_content(BrainTumorFrame, patient_id)

class PatientHistoryFrame(ctk.CTkFrame):
    def __init__(self, parent, main_view, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.main_view = main_view
        self.app = main_view.app
        self.patient_id = patient_id
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkButton(header_frame, text="⬅ Back to Selection", command=lambda: self.main_view.switch_content(PatientSelectionFrame),
                      fg_color="transparent", hover_color=_C["surface"], text_color=_C["text2"], font=("Helvetica", 14, "bold")).pack(side="left")
                      
        self.print_btn = ctk.CTkButton(header_frame, text="🖨️ Generate PDF Report", command=self._generate_pdf,
                                       fg_color=_C["accent"], hover_color=_C["accent_hover"], font=("Helvetica", 14, "bold"), height=40, corner_radius=8)
        self.print_btn.pack(side="right")
        
        ctk.CTkLabel(self, text="Patient History", font=("Helvetica", 28, "bold")).pack(pady=(0, 20))
        
        frame = ctk.CTkScrollableFrame(self, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.history = database.get_patient_history(patient_id)
        if not self.history:
            ctk.CTkLabel(frame, text="No past examinations found.", text_color=_C["text2"]).pack(pady=40)
            return
            
        for exam in self.history:
            card = ctk.CTkFrame(frame, fg_color=_C["surface"], corner_radius=12)
            card.pack(fill="x", pady=12, padx=20)
            
            date_str = exam[4].split(".")[0]
            examiner = exam[5] if exam[5] else "Unknown"
            
            lbl_title = ctk.CTkLabel(card, text=f"📅 {date_str}   |   📁 {exam[1]}", font=("Helvetica", 16, "bold"))
            lbl_title.pack(anchor="w", padx=20, pady=(15, 5))
            
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            color = _C["danger"] if exam[2] == "Tumor" else _C["success"]
            lbl_res = ctk.CTkLabel(info_frame, text=f"Result: {exam[2]} ({exam[3]*100:.1f}%)", text_color=color, font=("Helvetica", 14, "bold"))
            lbl_res.pack(side="left")
            
            lbl_examiner = ctk.CTkLabel(info_frame, text=f"Examiner: {examiner}", text_color=_C["text2"], font=("Helvetica", 13))
            lbl_examiner.pack(side="right")

    def _generate_pdf(self):
        info = database.get_patient_info(self.patient_id)
        if not info:
            messagebox.showerror("Error", "Patient info not found.")
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
        pdf.cell(0, 8, f"Age: {info[2] if info[2] else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Gender: {info[3] if info[3] else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Contact: {info[4] if info[4] else 'N/A'}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Examination History:", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        for exam in self.history:
            date_str = exam[4].split(".")[0]
            examiner = exam[5] if exam[5] else "Unknown"
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, f"Date: {date_str}", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 8, f"Image File: {exam[1]}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"Examiner: {examiner}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, f"Diagnosis: {exam[2]} ({exam[3]*100:.1f}%)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
        filename = f"report_{info[1].replace(' ', '_')}.pdf"
        try:
            pdf.output(filename)
            messagebox.showinfo("Success", f"Report saved as {filename}")
            if os.name == 'nt':
                os.startfile(filename)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', filename])
            else:
                subprocess.call(['xdg-open', filename])
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate PDF: {e}")


class BrainTumorFrame(ctk.CTkFrame):
    def __init__(self, parent, main_view, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.main_view = main_view
        self.app = main_view.app
        self.examiner_id = self.app.examiner_id
        self.patient_id = patient_id

        self.current_image_path = None
        self.original_image = None
        self.predictor = None
        self.gradcam = None

        self._build_ui()
        self.after(300, self._load_model)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()       # row 0
        self._build_content()      # row 1

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(side="left")

        ctk.CTkLabel(inner, text="🧠", font=("", 38)).pack(side="left", padx=(0, 14))

        txt = ctk.CTkFrame(inner, fg_color="transparent")
        txt.pack(side="left")
        ctk.CTkLabel(txt, text="MRI Analysis Studio", font=("Helvetica", 24, "bold"), text_color=_C["text"]).pack(anchor="w")
        ctk.CTkLabel(txt, text="AI-Powered Brain Tumor Detection", font=("Helvetica", 13), text_color=_C["text2"]).pack(anchor="w")

        # Warning
        ctk.CTkLabel(header, text="FOR INVESTIGATIONAL USE ONLY", font=("Helvetica", 11, "bold"), text_color="#fca5a5", fg_color="#7f1d1d", corner_radius=6, padx=14, pady=6).pack(side="right", pady=10)

    def _build_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure((0, 1, 2), weight=1, uniform="col")
        content.grid_rowconfigure(0, weight=1)

        left = self._make_card(content, "📸  Original Scan")
        left.grid(row=0, column=0, sticky="nsew", padx=8)
        self.orig_img_lbl = self._make_image_placeholder(left, "No image loaded")

        centre = self._make_card(content, "📊  Results & Controls")
        centre.grid(row=0, column=1, sticky="nsew", padx=8)
        self._build_results_panel(centre)

        right = self._make_card(content, "🔥  Grad-CAM Heatmap")
        right.grid(row=0, column=2, sticky="nsew", padx=8)
        self.hm_img_lbl = self._make_image_placeholder(right, "No heatmap generated")

    def _make_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=_C["card_bg"], corner_radius=16, border_width=1, border_color=_C["border"])
        ctk.CTkLabel(card, text=title, font=("Helvetica", 16, "bold"), text_color=_C["text"]).pack(anchor="w", padx=20, pady=(16, 10))
        ctk.CTkFrame(card, fg_color=_C["border"], height=1, corner_radius=0).pack(fill="x", padx=20)
        return card

    def _make_image_placeholder(self, parent, text):
        container = ctk.CTkFrame(parent, fg_color=_C["surface"], corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=(16, 20))
        lbl = ctk.CTkLabel(container, text=text, font=("Helvetica", 13), text_color=_C["text2"])
        lbl.pack(expand=True)
        return lbl

    def _build_results_panel(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=(16, 20))

        # Controls at top of center card
        self.load_btn = ctk.CTkButton(wrap, text="📁 Load MRI", command=self._load_image, font=("Helvetica", 14, "bold"), height=45, fg_color=_C["surface"], hover_color=_C["border"], corner_radius=8)
        self.load_btn.pack(fill="x", pady=(0, 10))

        self.analyze_btn = ctk.CTkButton(wrap, text="🔍 Analyze Image", command=self._analyze_image, font=("Helvetica", 14, "bold"), height=45, fg_color=_C["accent"], hover_color=_C["accent_hover"], corner_radius=8, state="disabled")
        self.analyze_btn.pack(fill="x", pady=(0, 20))

        ctk.CTkFrame(wrap, fg_color=_C["border"], height=1, corner_radius=0).pack(fill="x", pady=(0, 20))

        self.res_icon = ctk.CTkLabel(wrap, text="⏳", font=("", 48))
        self.res_icon.pack(pady=(10, 10))

        self.res_title = ctk.CTkLabel(wrap, text="Awaiting Scan", font=("Helvetica", 20, "bold"), text_color=_C["text2"])
        self.res_title.pack(pady=6)

        conf_frame = ctk.CTkFrame(wrap, fg_color="transparent")
        conf_frame.pack(pady=16, fill="x")

        self.conf_label = ctk.CTkLabel(conf_frame, text="", font=("Helvetica", 14, "bold"), text_color=_C["text2"])
        self.conf_label.pack()

        self.conf_bar = ctk.CTkProgressBar(conf_frame, height=16, corner_radius=8, fg_color=_C["surface"], progress_color=_C["accent"])
        self.conf_bar.pack(pady=10, fill="x", padx=20)
        self.conf_bar.set(0)

        self.conf_pct = ctk.CTkLabel(conf_frame, text="", font=("Helvetica", 13, "bold"), text_color=_C["text"])
        self.conf_pct.pack()

        self.status_lbl = ctk.CTkLabel(wrap, text="● Ready", font=("Helvetica", 12), text_color=_C["text2"])
        self.status_lbl.pack(side="bottom", pady=10)

    def _set_status(self, msg, kind="info"):
        icons = {"info": "●", "success": "✓", "warn": "⚠", "error": "✗", "loading": "⟳"}
        colours = {"info": _C["accent"], "success": _C["success"], "warn": _C["warn"], "error": _C["danger"], "loading": _C["warn"]}
        icon = icons.get(kind, "●")
        colour = colours.get(kind, _C["text2"])
        self.status_lbl.configure(text=f"{icon}  {msg}", text_color=colour)

    def _load_model(self):
        try:
            self._set_status("Loading AI model…", "loading")
            self.update()
            self.predictor = BrainTumorPredictor()
            self.predictor.load_model()
            self.gradcam = GradCAM(self.predictor.get_model(), layer_name="top_conv")
            self._set_status("Model loaded — ready", "success")
        except Exception as e:
            messagebox.showerror("Model Error", f"Failed to load model:\n\n{e}")
            self._set_status("Model loading failed", "error")

    def _load_image(self):
        path = filedialog.askopenfilename(title="Select MRI Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg"), ("All Files", "*.*")])
        if not path:
            return
        if not validate_image_file(path):
            messagebox.showerror("Invalid File", "Please select a valid image (PNG / JPG / JPEG).")
            return

        try:
            self.current_image_path = path
            self.original_image = Image.open(path).convert("RGB")

            self._display_image(self.orig_img_lbl, self.original_image)
            self.analyze_btn.configure(state="normal")

            self.res_icon.configure(text="🔍")
            self.res_title.configure(text="Ready", text_color=_C["accent"])
            self.conf_label.configure(text="")
            self.conf_pct.configure(text="")
            self.conf_bar.set(0)
            self.hm_img_lbl.configure(image=None, text="No heatmap generated")

            fname = os.path.basename(path)
            if len(fname) > 30:
                fname = fname[:27] + "…"
            self._set_status(f"Loaded: {fname}", "success")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n\n{e}")
            self._set_status("Image loading failed", "error")

    def _analyze_image(self):
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please load an MRI image first.")
            return

        try:
            self._set_status("Preprocessing…", "loading")
            self.analyze_btn.configure(state="disabled")
            self.res_icon.configure(text="⏳")
            self.res_title.configure(text="Processing…", text_color=_C["text2"])
            self.update()

            preprocessed, _ = preprocess_image(self.current_image_path)
            
            self._set_status("Running AI inference…", "loading")
            self.update()
            label, confidence = self.predictor.predict(preprocessed)

            if label == "Tumor":
                self.res_icon.configure(text="⚠️")
                self.res_title.configure(text="TUMOR DETECTED", text_color=_C["danger"])
                bar_colour = _C["danger"]
            else:
                self.res_icon.configure(text="✅")
                self.res_title.configure(text="NO TUMOR DETECTED", text_color=_C["success"])
                bar_colour = _C["success"]

            self.conf_label.configure(text="Confidence Score", text_color=_C["text"])
            self.conf_bar.configure(progress_color=bar_colour)
            self.conf_bar.set(confidence)
            self.conf_pct.configure(text=f"{confidence * 100:.1f}%")

            if confidence < 0.65:
                self._set_status("Done — low confidence", "warn")
            else:
                self._set_status("Analysis complete", "success")

            self._set_status("Generating Grad-CAM…", "loading")
            self.update()
            try:
                heatmap = self.gradcam.generate_heatmap(preprocessed)
                overlay = overlay_heatmap(self.original_image, heatmap)
                overlay_pil = Image.fromarray(overlay.astype("uint8"))
                self._display_image(self.hm_img_lbl, overlay_pil)
                heatmap_path = "heatmap_generated"
            except Exception as ge:
                self.hm_img_lbl.configure(image=None, text=f"❌ Grad-CAM Error\n\n{str(ge)[:120]}", text_color=_C["danger"])
                heatmap_path = "error"

            self._set_status("Saving to database…", "loading")
            self.update()
            database.save_examination(
                patient_id=self.patient_id,
                examiner_id=self.examiner_id,
                image_name=os.path.basename(self.current_image_path),
                prediction=label,
                confidence_score=float(confidence),
                heatmap_path=heatmap_path
            )

            self._set_status("Analysis complete", "success")

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis:\n\n{e}")
            self._set_status("Analysis failed", "error")
            self.res_icon.configure(text="❌")
            self.res_title.configure(text="Failed", text_color=_C["danger"])

        finally:
            self.analyze_btn.configure(state="normal")

    def _display_image(self, label: ctk.CTkLabel, pil_img: Image.Image):
        img = pil_img.copy()
        img.thumbnail(IMAGE_DISPLAY_SIZE, Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        label.configure(image=ctk_img, text="")
        label._ctk_img = ctk_img

def main():
    database.init_db()
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    main()
