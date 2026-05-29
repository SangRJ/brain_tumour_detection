"""MRI Analysis page with model loading in background thread."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage
from PIL import Image
import numpy as np
import os

from engine.inference import BrainTumorPredictor
from engine.gradcam import GradCAM
from engine.utils import preprocess_image, validate_image_file, overlay_heatmap
from core import database

IMG_SIZE = (600, 600)


class _ModelLoader(QThread):
    done = pyqtSignal(object, object)
    error = pyqtSignal(str)

    def run(self):
        try:
            from core import config_registry
            cfg = config_registry.load_config()
            thresh = cfg.get("confidence_threshold", 0.50)
            
            p = BrainTumorPredictor(threshold=thresh)
            p.load_model()
            g = GradCAM(p.get_model(), layer_name="top_conv")
            self.done.emit(p, g)
        except Exception as e:
            self.error.emit(str(e))


class _AnalysisWorker(QThread):
    result = pyqtSignal(str, float, object)  # label, conf, overlay_pil_or_None
    error = pyqtSignal(str)

    def __init__(self, predictor, gradcam, path, orig_img):
        super().__init__()
        self.predictor = predictor
        self.gradcam = gradcam
        self.path = path
        self.orig_img = orig_img

    def run(self):
        try:
            preprocessed, _ = preprocess_image(self.path)
            label, confidence = self.predictor.predict(preprocessed)
            overlay_pil = None
            try:
                hm = self.gradcam.generate_heatmap(preprocessed, predicted_label=label)
                ov = overlay_heatmap(self.orig_img, hm)
                overlay_pil = Image.fromarray(ov.astype("uint8"))
            except:
                pass
            self.result.emit(label, float(confidence), overlay_pil)
        except Exception as e:
            self.error.emit(str(e))


def _pil_to_pixmap(pil_img, max_size=IMG_SIZE):
    img = pil_img.copy()
    img.thumbnail(max_size, Image.LANCZOS)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    data = img.tobytes("raw", "RGBA")
    qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimg)


class AnalysisPage(QWidget):
    def __init__(self, main_win, patient_id):
        super().__init__()
        self.mw = main_win
        self.pid = patient_id
        self.eid = main_win.examiner_id
        self.predictor = None
        self.gradcam = None
        self.current_path = None
        self.orig_img = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        inner = QHBoxLayout()

        txt_w = QWidget()
        tl = QVBoxLayout(txt_w)
        tl.setContentsMargins(10, 0, 0, 0)
        tl.setSpacing(2)
        t1 = QLabel("MRI Analysis Studio")
        t1.setObjectName("heading")
        tl.addWidget(t1)
        t2 = QLabel("AI-Powered Brain Tumor Detection")
        t2.setObjectName("subtext")
        tl.addWidget(t2)
        inner.addWidget(txt_w)
        hdr.addLayout(inner)
        hdr.addStretch()

        back = QPushButton("Back")
        back.setObjectName("backBtn")
        back.clicked.connect(lambda: self.mw.pop_page(self))
        hdr.addWidget(back)

        warn = QLabel("FOR INVESTIGATIONAL USE ONLY")
        warn.setObjectName("warningBadge")
        hdr.addWidget(warn)
        lay.addLayout(hdr)

        # Top section - Controls & Results
        top_card = self._card("Results & Controls")
        tl_layout = QHBoxLayout()
        tl_layout.setSpacing(30)
        
        # Controls
        ctrl_layout = QVBoxLayout()
        self.load_btn = QPushButton("Load MRI")
        self.load_btn.setMinimumHeight(44)
        self.load_btn.clicked.connect(self._load_image)
        
        self.analyze_btn = QPushButton("Analyze Image")
        self.analyze_btn.setObjectName("accentBtn")
        self.analyze_btn.setMinimumHeight(44)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._analyze)
        
        self.print_btn = QPushButton("Print Report")
        self.print_btn.setMinimumHeight(44)
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self._print_report)
        
        ctrl_layout.addWidget(self.load_btn)
        ctrl_layout.addWidget(self.analyze_btn)
        ctrl_layout.addWidget(self.print_btn)
        ctrl_layout.addStretch()
        tl_layout.addLayout(ctrl_layout, 1)

        # Vertical Separator
        v_sep = QFrame()
        v_sep.setFrameShape(QFrame.Shape.VLine)
        v_sep.setFrameShadow(QFrame.Shadow.Sunken)
        v_sep.setStyleSheet("color: #334155;")
        tl_layout.addWidget(v_sep)

        # Results
        res_layout = QVBoxLayout()
        
        self.res_title = QLabel("Awaiting Scan")
        self.res_title.setObjectName("resultTitle")
        self.res_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.res_title.setStyleSheet("color: #94a3b8;")
        res_layout.addWidget(self.res_title)

        conf_hbox = QHBoxLayout()
        self.conf_label = QLabel("")
        self.conf_label.setObjectName("subtext")
        conf_hbox.addWidget(self.conf_label)
        
        self.conf_pct = QLabel("")
        self.conf_pct.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        conf_hbox.addStretch()
        conf_hbox.addWidget(self.conf_pct)
        res_layout.addLayout(conf_hbox)

        self.conf_bar = QProgressBar()
        self.conf_bar.setMinimumHeight(14)
        self.conf_bar.setRange(0, 1000)
        self.conf_bar.setValue(0)
        res_layout.addWidget(self.conf_bar)

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setObjectName("statusLabel")
        res_layout.addWidget(self.status_lbl)
        
        res_layout.addStretch()
        tl_layout.addLayout(res_layout, 2)
        
        top_card.layout().addLayout(tl_layout)
        lay.addWidget(top_card)

        # Images section
        img_cols = QHBoxLayout()
        img_cols.setSpacing(12)

        # Left - original scan
        left = self._card("Original Scan")
        self.orig_lbl = QLabel("No image loaded")
        self.orig_lbl.setObjectName("imagePlaceholder")
        self.orig_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orig_lbl.setMinimumSize(400, 400)
        
        # Give the image label stretching preference
        left.layout().addWidget(self.orig_lbl, 1)
        img_cols.addWidget(left, 1)

        # Right - heatmap
        right = self._card("Grad-CAM Heatmap")
        self.hm_lbl = QLabel("No heatmap generated")
        self.hm_lbl.setObjectName("imagePlaceholder")
        self.hm_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hm_lbl.setMinimumSize(400, 400)
        right.layout().addWidget(self.hm_lbl, 1)
        img_cols.addWidget(right, 1)

        lay.addLayout(img_cols, 1)

        # Load model in background
        self._set_status("Loading AI model...", "#f59e0b")
        self._loader = _ModelLoader()
        self._loader.done.connect(self._on_model_loaded)
        self._loader.error.connect(self._on_model_error)
        self._loader.start()

    def _card(self, title):
        f = QFrame()
        f.setObjectName("card")
        vl = QVBoxLayout(f)
        vl.setContentsMargins(20, 16, 20, 20)
        vl.setSpacing(10)
        t = QLabel(title)
        t.setObjectName("sectionTitle")
        vl.addWidget(t)
        vl.addWidget(self._sep())
        return f

    def _sep(self):
        s = QFrame()
        s.setObjectName("separator")
        s.setFixedHeight(1)
        return s

    def _set_status(self, msg, color="#94a3b8"):
        self.status_lbl.setText(msg)
        self.status_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    def _on_model_loaded(self, p, g):
        self.predictor = p
        self.gradcam = g
        self._set_status("Model loaded - ready", "#10b981")

    def _on_model_error(self, e):
        QMessageBox.critical(self, "Model Error", f"Failed to load model:\n\n{e}")
        self._set_status("Model loading failed", "#ef4444")

    def _load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select MRI Image", "", "Image Files (*.png *.jpg *.jpeg);;All Files (*)")
        if not path:
            return
        if not validate_image_file(path):
            QMessageBox.critical(self, "Invalid File", "Please select a valid image (PNG/JPG/JPEG).")
            return
        try:
            self.current_path = path
            self.orig_img = Image.open(path).convert("RGB")
            pm = _pil_to_pixmap(self.orig_img)
            self.orig_lbl.setPixmap(pm)

            self.analyze_btn.setEnabled(True)
            self.print_btn.setEnabled(False)
            self.res_title.setText("Ready")
            self.res_title.setStyleSheet("color: #6366f1;")
            self.conf_label.setText("")
            self.conf_pct.setText("")
            self.conf_bar.setValue(0)
            self.hm_lbl.setPixmap(QPixmap())
            self.hm_lbl.setText("No heatmap generated")

            fn = os.path.basename(path)
            if len(fn) > 30: fn = fn[:27] + "..."
            self._set_status(f"Loaded: {fn}", "#10b981")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load image:\n\n{e}")

    def _analyze(self):
        if not self.current_path or not self.predictor:
            return

        self.analyze_btn.setEnabled(False)
        self.res_title.setText("Processing...")
        self.res_title.setStyleSheet("color: #94a3b8;")
        self._set_status("Running AI inference...", "#f59e0b")

        self._worker = _AnalysisWorker(self.predictor, self.gradcam, self.current_path, self.orig_img)
        self._worker.result.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, label, confidence, overlay_pil):
        if label == "Tumor":
            self.res_title.setText("TUMOR DETECTED")
            self.res_title.setStyleSheet("color: #ef4444; font-size: 20px; font-weight: 700;")
            self.conf_bar.setObjectName("dangerBar")
        else:
            self.res_title.setText("NO TUMOR DETECTED")
            self.res_title.setStyleSheet("color: #10b981; font-size: 20px; font-weight: 700;")
            self.conf_bar.setObjectName("successBar")
        self.conf_bar.style().unpolish(self.conf_bar)
        self.conf_bar.style().polish(self.conf_bar)

        self.conf_label.setText("Confidence Score")
        self.conf_bar.setValue(int(confidence * 1000))
        self.conf_pct.setText(f"{confidence * 100:.1f}%")

        # SECURE FILE STORAGE & INTEGRATION
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 1. Save Grad-CAM Heatmap
        self.hm_save_path = "heatmap_error"
        if overlay_pil:
            pm = _pil_to_pixmap(overlay_pil)
            self.hm_lbl.setPixmap(pm)
            self.hm_lbl.setText("")
            
            try:
                heatmaps_dir = os.path.join(base_dir, "images", "patient", "heatmaps")
                os.makedirs(heatmaps_dir, exist_ok=True)
                import time
                hm_filename = f"heatmap_p{self.pid}_{int(time.time())}.png"
                self.hm_save_path = os.path.join(heatmaps_dir, hm_filename)
                overlay_pil.save(self.hm_save_path)
            except Exception as e:
                print(f"[Analysis Error] Failed to save Grad-CAM heatmap overlay: {e}")
        else:
            self.hm_lbl.setText("Grad-CAM Error")

        # 2. Copy Original Scan to Local Storage Repository
        self.mri_save_path = self.current_path
        if self.current_path and os.path.exists(self.current_path):
            try:
                scans_dir = os.path.join(base_dir, "images", "patient", "scans")
                os.makedirs(scans_dir, exist_ok=True)
                import shutil
                import time
                scan_ext = os.path.splitext(self.current_path)[1] or ".png"
                scan_filename = f"scan_p{self.pid}_{int(time.time())}{scan_ext}"
                self.mri_save_path = os.path.join(scans_dir, scan_filename)
                shutil.copy2(self.current_path, self.mri_save_path)
            except Exception as e:
                print(f"[Analysis Error] Failed to copy original scan to repository: {e}")

        # 3. Save Examination to Database
        self.last_pred = label
        self.last_conf = confidence
        self.last_exam_id = database.save_examination(
            patient_id=self.pid,
            examiner_id=self.eid,
            image_name=self.mri_save_path,
            prediction=label,
            confidence_score=confidence,
            heatmap_path=self.hm_save_path
        )

        # Enable direct clinical printing
        if self.last_exam_id:
            self.print_btn.setEnabled(True)

        # 4. Write to Medical Audit Trail Log
        try:
            from core import audit_logger
            fn = os.path.basename(self.current_path)
            audit_logger.log_action(
                examiner_id=self.eid,
                action="MRI Diagnosis Completed",
                details=f"Patient ID: {self.pid}, Result: {label}, Confidence: {confidence*100:.1f}%, File: {fn}"
            )
        except Exception as le:
            print(f"[Audit Log Error] Failed logging event: {le}")

        if confidence < 0.65:
            self._set_status("Done - low confidence", "#f59e0b")
        else:
            self._set_status("Analysis complete", "#10b981")
        self.analyze_btn.setEnabled(True)

    def _on_error(self, e):
        QMessageBox.critical(self, "Analysis Error", f"Error during analysis:\n\n{e}")
        self._set_status("Analysis failed", "#ef4444")
        self.res_title.setText("Failed")
        self.res_title.setStyleSheet("color: #ef4444;")
        self.analyze_btn.setEnabled(True)

    def _print_report(self):
        if not hasattr(self, "last_exam_id") or not self.last_exam_id:
            return
            
        from reporting.reporting import ClinicalReportGenerator
        import subprocess
        import datetime
        
        info = database.get_patient_info(self.pid)
        if not info:
            QMessageBox.critical(self, "Error", "Patient info not found.")
            return
            
        p_name = info[1].replace(' ', '_')
        date_clean = datetime.date.today().strftime("%Y-%m-%d")
        
        # Ensure reports folder exists inside workspace
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        fn = os.path.join(reports_dir, f"diagnostic_report_{p_name}_{date_clean}_exam_{self.last_exam_id}.pdf")
        
        try:
            generator = ClinicalReportGenerator(self.pid, self.eid)
            
            exam_data = {
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "image_name": os.path.basename(self.mri_save_path),
                "original_path": self.mri_save_path,
                "heatmap_path": self.hm_save_path,
                "prediction": self.last_pred,
                "confidence": self.last_conf
            }
            
            generator.generate_pdf(exam_data, fn)
            
            # Log print action
            try:
                from core import audit_logger
                audit_logger.log_action(
                    examiner_id=self.eid,
                    action="Diagnostic Report Exported",
                    details=f"Exported diagnostic report from Analysis Studio for Patient ID: {self.pid}, Exam ID: {self.last_exam_id} to: {fn}"
                )
            except Exception as le:
                print(f"[Audit Log Error] Failed logging event: {le}")

            QMessageBox.information(self, "Success", f"Diagnostic report saved in reports folder:\n{os.path.basename(fn)}")
            
            # Auto-open
            if os.name == 'nt':
                os.startfile(fn)
            elif os.uname().sysname == 'Darwin':
                subprocess.call(['open', fn])
            else:
                subprocess.call(['xdg-open', fn])
                
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Could not generate diagnostic report:\n{ex}")
