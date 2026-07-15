"""
camobreak.py
Detects camouflaged people/objects that plain YOLO misses, by combining:
  1. Standard YOLO detection (color/texture based)
  2. MiDaS depth estimation -> edge detection (shape based, ignores color)
The depth-edge branch finds object boundaries even when color/texture
blend into the background (i.e. camouflage), since depth doesn't care
what color something is.
"""

import cv2
import torch
import numpy as np
import base64
from ultralytics import YOLO

torch.hub._validate_not_a_forked_repo = lambda a, b, c: True

yolo_model = YOLO("models/m4/yolov8n.pt")

# MiDaS small model - free, pretrained, downloaded automatically on first run
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
midas.eval()
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.small_transform


def get_depth_map(image_bgr):
    """Runs MiDaS on the image and returns a normalized depth map (H, W)."""
    img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    input_batch = transform(img_rgb)

    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth_map = prediction.cpu().numpy()
    depth_norm = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return depth_norm


def find_depth_edge_regions(depth_map, min_area=800):
    """
    Finds candidate object regions from the depth map using edge detection.
    These are shape-based boundaries, independent of color/texture, which is
    what lets this catch camouflaged objects that blend into the background.
    Confidence is based on edge density within the region — a tighter,
    denser edge boundary means a more clearly defined object shape.
    """
    edges = cv2.Canny(depth_map, 50, 150)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for c in contours:
        area = cv2.contourArea(c)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(c)
            bbox_edge_pixels = edges[y:y+h, x:x+w]
            edge_density = float(np.count_nonzero(bbox_edge_pixels)) / (w * h) if w * h > 0 else 0
            # scale edge density into a 0-100 confidence score, capped
            confidence = round(min(edge_density * 400, 98.0), 2)
            regions.append({"bbox": [x, y, x + w, y + h], "area": int(area), "confidence": confidence})

    return regions


def encode_depth_map_b64(depth_map_gray):
    """Encodes the raw depth map as a base64 JPEG (colorized) for side-by-side display."""
    colored = cv2.applyColorMap(depth_map_gray, cv2.COLORMAP_INFERNO)
    success, buffer = cv2.imencode(".jpg", colored)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


def boxes_overlap(box1, box2, iou_thresh=0.2):
    """Simple IoU check to see if a depth-region overlaps an existing YOLO detection."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    if inter_area == 0:
        return False

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    iou = inter_area / union_area if union_area > 0 else 0
    return iou > iou_thresh


def detect_camouflaged(image_path):
    """
    Runs both YOLO and the depth-edge branch, then fuses results:
    - YOLO detections are returned as normal, labeled detections
    - Depth-edge regions that DON'T overlap any YOLO box are flagged as
      "possible camouflaged object" — these are shapes YOLO missed entirely
    """
    img = cv2.imread(image_path)

    # Branch 1: standard YOLO
    yolo_results = yolo_model(image_path)
    r = yolo_results[0]
    yolo_detections = [{
        "class": yolo_model.names[int(box.cls[0])],
        "confidence": float(box.conf[0]),
        "bbox": box.xyxy[0].tolist(),
        "source": "yolo"
    } for box in r.boxes]

    # Branch 2: depth-based edge regions
    depth_map = get_depth_map(img)
    depth_regions = find_depth_edge_regions(depth_map)
    depth_map_b64 = encode_depth_map_b64(depth_map)

    # Fusion: keep depth regions that YOLO completely missed
    yolo_boxes = [d["bbox"] for d in yolo_detections]
    camo_candidates = []
    for region in depth_regions:
        overlaps_existing = any(boxes_overlap(region["bbox"], yb) for yb in yolo_boxes)
        if not overlaps_existing:
            camo_candidates.append({
                "class": "possible_camouflaged_object",
                "bbox": region["bbox"],
                "area": region["area"],
                "confidence": region["confidence"],
                "source": "depth_edge"
            })

    return {
        "yolo_detections": yolo_detections,
        "camo_candidates": camo_candidates,
        "total_objects": len(yolo_detections) + len(camo_candidates),
        "depth_map": depth_map_b64
    }