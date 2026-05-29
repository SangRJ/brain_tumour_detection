# gradcam.py
"""
Grad-CAM (Gradient-weighted Class Activation Mapping)
Robust implementation for EfficientNet-B0 (binary classification).
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np


class GradCAM:
    def __init__(self, model, layer_name="top_conv"):
        self.model = model
        self.layer_name = layer_name
        self.grad_model = self._build_grad_model()

    def _build_grad_model(self):
        try:
            target_layer = self.model.get_layer(self.layer_name)
        except ValueError:
            raise ValueError(f"Layer '{self.layer_name}' not found in the model.")

        return keras.Model(
            inputs=self.model.inputs,
            outputs=[target_layer.output, self.model.output]
        )

    @staticmethod
    def _unwrap(x):
        """Extract tensor from list/tuple model outputs."""
        if isinstance(x, (list, tuple)):
            return x[0]
        return x

    def generate_heatmap(self, image_array, predicted_label="Tumor"):
        """Generate a Grad-CAM heatmap for the given preprocessed image.

        The heatmap highlights the regions most responsible for the model's
        actual prediction. For "Tumor" predictions the gradient targets the
        positive logit; for "No Tumor" the gradient is negated so it
        highlights what drove the healthy-tissue decision.

        Args:
            image_array: np.ndarray of shape (1, H, W, C), normalized.
            predicted_label: "Tumor" or "No Tumor" — controls gradient
                direction so the heatmap matches the prediction made.

        Returns:
            np.ndarray: 2D heatmap with values in [0, 1], shape matches
            the spatial dimensions of the target conv layer.
        """
        if image_array.ndim != 4:
            raise ValueError("Input image must have shape (1, H, W, C)")

        image_tensor = tf.cast(image_array, tf.float32)

        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.grad_model(image_tensor)
            conv_outputs = self._unwrap(conv_outputs)
            predictions = self._unwrap(predictions)

            # For binary sigmoid output, convert probability back to logit
            # so gradients aren't crushed by sigmoid saturation.
            if len(predictions.shape) > 1 and predictions.shape[-1] == 1:
                p = predictions[:, 0]
            else:
                p = predictions

            # inverse-sigmoid: logit = log(p / (1 - p))
            p_clipped = tf.clip_by_value(p, 1e-7, 1.0 - 1e-7)
            class_score = tf.math.log(p_clipped / (1.0 - p_clipped))

            # For "No Tumor", negate the score so gradients highlight
            # regions that drove the model away from tumor prediction.
            if predicted_label != "Tumor":
                class_score = -class_score

        grads = tape.gradient(class_score, conv_outputs)

        if grads is None:
            raise RuntimeError(
                "Failed to compute gradients — check that the target layer "
                "is connected to the model output."
            )

        grads = self._unwrap(grads)

        # Remove batch dimension → (H, W, C)
        conv_outputs = conv_outputs[0]
        grads = grads[0]

        # Channel-wise importance weights via global average pooling
        weights = tf.reduce_mean(grads, axis=(0, 1))

        # Vectorized weighted combination (replaces slow Python loop)
        heatmap = tf.reduce_sum(conv_outputs * weights, axis=-1)

        # ReLU — keep only positive influence
        heatmap = tf.nn.relu(heatmap)

        # Normalize to [0, 1]
        max_val = tf.reduce_max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val

        return heatmap.numpy()

