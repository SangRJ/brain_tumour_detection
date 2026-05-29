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


def overlay_heatmap(original_img, heatmap, alpha=0.5, model_input_size=(224, 224)):
    """
    Overlay Grad-CAM heatmap on the original MRI image.

    A low activation threshold removes background noise, while a fixed
    alpha blend in the active region keeps highlights clearly visible.

    Args:
        original_img (PIL.Image or np.ndarray): Original MRI image
        heatmap (np.ndarray): 2D Grad-CAM heatmap with values in [0, 1]
        alpha (float): Blend factor for the colored overlay
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

        # --- Resize heatmap directly to original image dimensions ---
        heatmap_resized = cv2.resize(
            heatmap.astype(np.float32), (orig_w, orig_h),
            interpolation=cv2.INTER_CUBIC
        )

        # Smooth the upscaled heatmap to remove blocky artifacts
        ksize = max(3, min(orig_w, orig_h) // 14) | 1  # ensure odd kernel
        heatmap_resized = cv2.GaussianBlur(heatmap_resized, (ksize, ksize), 0)

        # Re-normalize after blur
        hmax = heatmap_resized.max()
        if hmax > 0:
            heatmap_resized = heatmap_resized / hmax

        # --- Suppress weak activations (bottom 15%) to cut edge noise ---
        threshold = 0.15
        heatmap_resized[heatmap_resized < threshold] = 0.0

        # --- Build foreground mask so heatmap only covers brain tissue ---
        gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
        _, fg_mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask_f = (fg_mask / 255.0).astype(np.float32)

        # Zero out heatmap outside the brain region
        heatmap_resized = heatmap_resized * fg_mask_f

        # Normalize to [0, 255] and apply color map
        heatmap_uint8 = np.uint8(255 * np.clip(heatmap_resized, 0, 1))
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # --- Blend: full alpha where active, original where not ---
        # Build a binary mask of where heatmap has any activation
        active = (heatmap_resized > 0).astype(np.float32)
        active_3ch = np.stack([active] * 3, axis=-1)

        blended = cv2.addWeighted(original_img, 1 - alpha, heatmap_colored, alpha, 0)
        overlay = np.where(active_3ch > 0, blended, original_img)

        return overlay

    except Exception as e:
        raise ValueError(f"Error overlaying heatmap: {str(e)}")

