# utils.py
"""
Utility functions for image preprocessing and visualization.
Used for EfficientNet-B0 brain tumor detection and Grad-CAM overlay.
"""

import numpy as np
from PIL import Image
import cv2


def preprocess_image(image_path, target_size=(224, 224)):
    """
    Load and preprocess an MRI image for model inference.

    Args:
        image_path (str): Path to the image file
        target_size (tuple): Target image size (width, height)

    Returns:
        tuple:
            np.ndarray: Preprocessed image of shape (1, 224, 224, 3)
            PIL.Image: Original image (RGB)
    """
    try:
        # Load image
        img = Image.open(image_path)

        # Convert to RGB explicitly
        if img.mode != "RGB":
            img = img.convert("RGB")

        original_img = img.copy()

        # Resize
        img = img.resize(target_size, Image.LANCZOS)

        # Convert to NumPy
        img_array = np.asarray(img, dtype=np.float32)

        # Normalize (matches your training setup)
        img_array /= 255.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array, original_img

    except Exception as e:
        raise ValueError(f"Error preprocessing image: {str(e)}")


def validate_image_file(file_path):
    """
    Validate if the file is a supported image format.

    Args:
        file_path (str): Path to the file

    Returns:
        bool: True if valid image file
    """
    valid_extensions = (".png", ".jpg", ".jpeg")
    return file_path.lower().endswith(valid_extensions)


def overlay_heatmap(original_img, heatmap, alpha=0.4, model_input_size=(224, 224)):
    """
    Overlay Grad-CAM heatmap on the original MRI image.

    The heatmap is computed in model-input space (e.g. 224×224). To avoid
    spatial offset when the original image has a different aspect ratio,
    we composite in model-input space first and then resize back to the
    original dimensions.

    Args:
        original_img (PIL.Image or np.ndarray): Original MRI image
        heatmap (np.ndarray): 2D Grad-CAM heatmap with values in [0, 1]
        alpha (float): Transparency factor for overlay
        model_input_size (tuple): (width, height) the model was fed

    Returns:
        np.ndarray: RGB image with heatmap overlay (original dimensions)
    """
    try:
        # --- Convert to RGB numpy array ---
        if isinstance(original_img, Image.Image):
            original_img = np.array(original_img.convert("RGB"))

        if original_img.ndim == 2:
            original_img = cv2.cvtColor(original_img, cv2.COLOR_GRAY2RGB)
        elif original_img.shape[2] == 4:
            original_img = cv2.cvtColor(original_img, cv2.COLOR_RGBA2RGB)

        if heatmap.ndim != 2:
            raise ValueError("Heatmap must be a 2D array")

        orig_h, orig_w = original_img.shape[:2]
        mw, mh = model_input_size  # width, height

        # --- Work in model-input space for perfect alignment ---
        aligned_img = cv2.resize(
            original_img, (mw, mh), interpolation=cv2.INTER_LINEAR
        )

        heatmap_resized = cv2.resize(
            heatmap.astype(np.float32), (mw, mh),
            interpolation=cv2.INTER_CUBIC
        )

        # Smooth the low-res heatmap to remove blocky upscale artifacts
        ksize = max(3, mw // 14) | 1  # ensure odd kernel
        heatmap_resized = cv2.GaussianBlur(heatmap_resized, (ksize, ksize), 0)

        # Re-normalize after blur
        hmax = heatmap_resized.max()
        if hmax > 0:
            heatmap_resized = heatmap_resized / hmax

        # --- Build foreground mask so heatmap only covers brain tissue ---
        gray = cv2.cvtColor(aligned_img, cv2.COLOR_RGB2GRAY)
        # Threshold: pixels brighter than ~5% of max are "foreground"
        _, fg_mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
        # Light morphological close to fill small holes in the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask_f = (fg_mask / 255.0).astype(np.float32)

        # Zero out heatmap outside the brain region
        heatmap_resized = heatmap_resized * fg_mask_f

        # Normalize to [0, 255] and apply color map
        heatmap_uint8 = np.uint8(255 * np.clip(heatmap_resized, 0, 1))
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # Blend only where foreground exists; keep original elsewhere
        fg_mask_3ch = np.stack([fg_mask_f] * 3, axis=-1)
        blended = cv2.addWeighted(aligned_img, 1 - alpha, heatmap_colored, alpha, 0)
        overlay = np.where(fg_mask_3ch > 0, blended, aligned_img)

        # --- Resize back to original dimensions for display ---
        if (orig_w, orig_h) != (mw, mh):
            overlay = cv2.resize(
                overlay, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR
            )

        return overlay

    except Exception as e:
        raise ValueError(f"Error overlaying heatmap: {str(e)}")
