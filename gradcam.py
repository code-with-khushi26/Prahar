"""
gradcam.py
Generates a Grad-CAM heatmap showing which regions of a face image
contributed most to the deepfake model's "FAKE" prediction.
Works with the EfficientNet-B0 model used in m2_deepfake.py.
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx):
        """
        input_tensor: preprocessed face tensor, shape (1, 3, 224, 224)
        class_idx: which class to explain (0 = FAKE in your setup)
        Returns a normalized heatmap (H, W) with values 0-1.
        """
        self.model.zero_grad()
        output = self.model(input_tensor)
        score = output[0, class_idx]
        score.backward()

        # Global-average-pool the gradients -> channel importance weights
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)

        cam = cam.squeeze().cpu().numpy()
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam


def overlay_heatmap_on_face(face_img_rgb, cam, alpha=0.45):
    """
    face_img_rgb: numpy array (H, W, 3) RGB, the original face crop
    cam: normalized Grad-CAM output (smaller H, W), values 0-1
    Returns: numpy array (H, W, 3) RGB with heatmap overlaid
    """
    h, w = face_img_rgb.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    overlay = (heatmap * alpha + face_img_rgb * (1 - alpha)).astype(np.uint8)
    return overlay


def encode_image_to_base64(img_rgb):
    """Encodes a numpy RGB image as a base64 JPEG string for JSON responses."""
    import base64
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    success, buffer = cv2.imencode(".jpg", img_bgr)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")