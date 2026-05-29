# Neural Diagnostics - Clinical AI Suite

An enterprise-grade, offline desktop application for clinical brain tumor detection from MRI images. Built with PyQt6 and powered by an EfficientNet-B0 deep learning model, this suite offers real-time Grad-CAM explainability, secure clinical authentication, and comprehensive patient reporting.

## ⚠️ Disclaimer

**This system is for research and educational purposes only. It is not intended for clinical use, automated medical diagnosis, or replacing professional medical consultation.**

---

## 🌟 Key Features

- **✅ Deep Learning Diagnostics**: EfficientNet-B0 model using transfer learning for accurate binary classification (Tumor / No Tumor).
- **🔍 Explainable AI (XAI)**: Integrated Grad-CAM heatmap visualization to pinpoint diagnostic regions of interest.
- **🖥️ Premium UI Architecture**: A sleek, dark-mode clinical dashboard built on **PyQt6**, featuring responsive 50/50 split-screens and medical iconography.
- **🔐 Clinical Security & Authentication**: Secure user login, hashed passwords, and system administrator controls to revoke access.
- **📜 Comprehensive Audit Logging**: Background tracking of all staff portal logins, patient intake events, and system interactions.
- **📄 Automated Medical Reporting**: Generate professional, printable PDF clinical reports complete with MRI images, Grad-CAM overlays, and examiner signatures.
- **📊 Hospital Analytics**: Built-in KPI metrics to track active rosters, completed scans, and pending diagnostics.

---

## 🛠️ System Architecture

The application operates on a highly organized, scalable **14-module architecture** divided into 5 specialized domains:

### Root Execution
- `app.py`: The main entry point that boots the engine and initializes audit telemetry.
- `theme.py`: Global QSS stylesheet repository dictating the dark-mode aesthetic tokens.

### User Interface (`/ui`)
- `ui_login.py`: Secure entry portal with dynamically rendered MRI background.
- `ui_main.py`: Overarching dashboard framework and primary clinical navigation sidebar.
- `ui_pages.py`: Multi-page controller handling Patient Selection, Intake, Settings, System Admin, and Analytics.
- `ui_analysis.py`: Complex MRI diagnostic workspace and side-by-side inference viewer.
- `ui_history.py`: Patient record timeline, past examination viewer, and PDF generator trigger.

### Core Services (`/core`)
- `database.py`: SQLite engine handling examiner auth, access control flags, patient records, and scan history.
- `audit_logger.py`: Security tracker ensuring HIPAA-aligned action recording.
- `config_registry.py`: System state manager for environmental thresholds.

### AI Engine (`/engine`)
- `inference.py`: Model loader and real-time inference execution logic.
- `gradcam.py`: Generates the thermal heatmap diagnostic overlays.
- `utils.py`: Auxiliary image pre-processing scripts.

### Reporting (`/reporting`)
- `reporting.py`: Dedicated PDF compiler utilizing ReportLab for clinical document generation.

---

## 💻 Requirements

- Python 3.10+
- PyQt6
- TensorFlow (CPU version optimized)
- OpenCV
- Pillow
- ReportLab

## 🚀 Installation & Setup

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the ML Model**
   Ensure your trained `.keras` or `.h5` model is correctly located at:
   ```text
   models/efficientnet_b0_brain_tumor_model/
   ```

4. **Launch the Application**
   ```bash
   python app.py
   ```

*Note: On the first launch, the SQLite database (`clinic.db`) will automatically initialize and a default `admin` profile will be generated for system access.*

---

## 🧑‍⚕️ Usage Guide

1. **Secure Login**: Use authorized credentials to access the Clinical AI Suite.
2. **Register Patients**: Use the Patient Selection dashboard to intake new records.
3. **Run Diagnostics**: Navigate to an active patient profile, upload an MRI scan (PNG/JPG), and click "Initiate Neural Network Analysis".
4. **Review Results**: Examine the original scan alongside the Grad-CAM thermal overlay to determine physiological anomalies.
5. **Export Documentation**: Navigate to Patient History and generate a comprehensive PDF medical report.
6. **System Administration**: (Admins Only) Add new clinical staff, assign departments, or instantly revoke access for offboarded employees.

---

## ⚖️ License & Authors

This project was initially developed as a Final Year Project for Brain Tumor Detection. 

**Acknowledgments:**
- TensorFlow & Keras Engineering Teams
- EfficientNet Architecture
- Grad-CAM XAI Research
