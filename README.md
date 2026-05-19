# # Brain Tumor Detection Desktop Application

An offline desktop application for brain tumor detection from MRI images using EfficientNet-B0 deep learning model with Grad-CAM explainability.

## ⚠️ Disclaimer

**This system is for research and educational purposes only. It is not intended for clinical use or medical diagnosis.**

## Features

- ✅ Fully offline operation (no internet required)
- 🧠 EfficientNet-B0 model with transfer learning
- 🔍 Binary classification: Tumor / No Tumor
- 📊 Prediction confidence scores
- 🎨 Grad-CAM heatmap visualization for explainability
- 💻 CPU-only inference
- 🖥️ Simple and professional Tkinter UI

## Requirements

- Python 3.9 or higher
- TensorFlow (CPU version)
- NumPy
- OpenCV
- Pillow

## Installation

1. **Clone or download this repository**

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure model is in place**
   Make sure your trained model is located at:
   ```
   models/efficientnet_b0_brain_tumor_model/
   ```

## Usage

Run the application:

```bash
python app.py
```

### How to Use the Application:

1. Click **"Load MRI Image"** to select an MRI scan (PNG, JPG, or JPEG)
2. Click **"Run Analysis"** to perform tumor detection
3. View results:
   - **Original Image**: Your input MRI scan
   - **Prediction**: Tumor or No Tumor with confidence score
   - **Grad-CAM Heatmap**: Visual explanation showing regions of interest

## Project Structure

```
brain_tumor_app/
├── app.py                          # Main application (Tkinter UI)
├── inference.py                    # Model loading and inference
├── gradcam.py                      # Grad-CAM generation
├── utils.py                        # Image preprocessing utilities
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── models/
│   └── efficientnet_b0_brain_tumor_model/  # Trained model
└── assets/                         # Optional assets
```

## Technical Details

### Model

- **Architecture**: EfficientNet-B0
- **Framework**: TensorFlow/Keras
- **Input Size**: 224 × 224 × 3
- **Output**: Binary classification (sigmoid)
- **Transfer Learning**: Pre-trained on ImageNet

### Grad-CAM

- Generates heatmaps from the last convolutional layer
- Highlights tumor regions in the MRI scan
- Provides visual explainability for predictions

### Performance

- **Inference Time**: < 1 second per image (CPU)
- **Grad-CAM Generation**: < 2 seconds (CPU)
- **Model Loading**: Once at startup

## Code Quality

- Modular design with separation of concerns
- Comprehensive docstrings
- Exception handling
- No hardcoded absolute paths
- PEP 8 compliant

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)

## Troubleshooting

### Model Not Found Error

Ensure the model directory exists at `models/efficientnet_b0_brain_tumor_model/`

### Image Loading Error

Make sure your image is in a supported format (PNG, JPG, JPEG)

### Slow Performance

The application is optimized for CPU inference. Performance depends on your CPU speed.

## License

This project is for educational and research purposes only.

## Authors

Final Year Project - Brain Tumor Detection System

## Acknowledgments

- TensorFlow and Keras teams
- EfficientNet architecture
- Grad-CAM visualization technique
