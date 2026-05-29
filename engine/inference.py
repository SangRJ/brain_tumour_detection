# inference.py
"""
Model loading and inference logic for brain tumor detection
using EfficientNet-B0 (binary classification).
"""

import os
import numpy as np
from tensorflow import keras


class BrainTumorPredictor:
    """
    Brain tumor detection predictor using EfficientNet-B0.
    """

    def __init__(
        self,
        model_path="models/efficientnet_b0_brain_tumor_model/efficientnet_b0_brain_tumor_model.keras",
        threshold=0.5
    ):
        """
        Initialize the predictor.

        Args:
            model_path (str): Relative path to the saved model
            threshold (float): Decision threshold for tumor detection
        """
        self.model_path = model_path
        self.threshold = threshold
        self.model = None

    def load_model(self):
        """
        Load the trained TensorFlow model.
        """
        # Resolve relative to the project root (parent directory of engine package)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_model_path = os.path.join(base_dir, self.model_path)

        if not os.path.exists(full_model_path):
            raise FileNotFoundError(f"Model not found at: {full_model_path}")

        self.model = keras.models.load_model(full_model_path)
        print(f"[INFO] Model loaded from: {full_model_path}")

    def predict(self, preprocessed_image):
        """
        Run inference on a preprocessed MRI image.

        Args:
            preprocessed_image (np.ndarray):
                Shape (1, 224, 224, 3), normalized

        Returns:
            tuple:
                prediction_label (str): "Tumor" or "No Tumor"
                confidence (float): Confidence of the predicted class
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        if not isinstance(preprocessed_image, np.ndarray):
            raise TypeError("preprocessed_image must be a NumPy array")

        if preprocessed_image.shape != (1, 224, 224, 3):
            raise ValueError(
                f"Invalid input shape {preprocessed_image.shape}, "
                "expected (1, 224, 224, 3)"
            )

        # Model outputs P(Tumor) due to sigmoid activation
        prediction = self.model.predict(preprocessed_image, verbose=0)
        p_tumor = float(prediction[0][0])

        if p_tumor >= self.threshold:
            return "Tumor", p_tumor
        else:
            return "No Tumor", 1.0 - p_tumor

    def get_model(self):
        """
        Return the loaded Keras model (for Grad-CAM).
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        return self.model
