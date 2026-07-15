import cv2
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
from PIL import Image
import numpy as np

from gradcam import GradCAM, overlay_heatmap_on_face, encode_image_to_base64

model = models.efficientnet_b0(weights="IMAGENET1K_V1")
model.classifier[1] = nn.Linear(model.classifier[1].in_features, 2)
model.load_state_dict(torch.load("models/m2_deepfake/m2_deepfake_finetuned.pt", map_location="cpu"))
model.eval()

# Grad-CAM hooks into the last convolutional block of EfficientNet-B0's feature extractor
gradcam = GradCAM(model, model.features[-1])

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def _generate_heatmap_b64(face_img_rgb_pil):
    """
    Runs Grad-CAM on a face image (PIL, RGB) and returns a base64-encoded
    JPEG string of the heatmap overlaid on the face. class_idx=0 is FAKE
    in this model's setup.
    """
    tensor = transform(face_img_rgb_pil).unsqueeze(0)
    cam = gradcam.generate(tensor, class_idx=0)

    # resize original face to match the 224x224 the model saw, so overlay lines up
    face_resized = face_img_rgb_pil.resize((224, 224))
    face_np = np.array(face_resized)

    overlay = overlay_heatmap_on_face(face_np, cam)
    return encode_image_to_base64(overlay)


def predict_deepfake(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        face_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        x, y, w, h = faces[0]
        face_img = Image.fromarray(cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2RGB))

    tensor = transform(face_img).unsqueeze(0)
    with torch.no_grad():
        output = model(tensor)
        probs = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probs, 1)
        label = "REAL" if predicted.item() == 1 else "FAKE"

    # Grad-CAM needs gradients, so this runs outside no_grad(), separately
    heatmap_b64 = _generate_heatmap_b64(face_img)

    return {
        "faces_detected": int(len(faces)),
        "label": label,
        "confidence": round(confidence.item() * 100, 2),
        "real_score": round(probs[0][1].item() * 100, 2),
        "fake_score": round(probs[0][0].item() * 100, 2),
        "heatmap": heatmap_b64
    }


def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    frame_count = 0
    frame_results = []
    sampled_faces = {}  # frame_count -> PIL face image, kept so we can re-run Grad-CAM on the worst one

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % 30 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_img = Image.fromarray(cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB))
            else:
                face_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            tensor = transform(face_img).unsqueeze(0)
            with torch.no_grad():
                output = model(tensor)
                probs = torch.softmax(output, dim=1)
                fake_score = round(probs[0][0].item() * 100, 2)
                frame_results.append({"frame": frame_count, "fake_score": fake_score})
            sampled_faces[frame_count] = face_img
        frame_count += 1

    cap.release()

    avg_fake = float(np.mean([f["fake_score"] for f in frame_results])) if frame_results else 50.0
    avg_real = 100 - avg_fake

    # Generate a heatmap for the single most-suspicious frame, so we don't
    # run Grad-CAM (which needs a backward pass) on every sampled frame
    heatmap_b64 = None
    worst_frame = None
    if frame_results:
        worst = max(frame_results, key=lambda f: f["fake_score"])
        worst_frame = worst["frame"]
        worst_face_img = sampled_faces.get(worst_frame)
        if worst_face_img is not None:
            heatmap_b64 = _generate_heatmap_b64(worst_face_img)

    return {
        "frames_processed": len(frame_results),
        "avg_real": round(avg_real, 2),
        "avg_fake": round(avg_fake, 2),
        "final_label": "FAKE" if avg_fake > 50 else "REAL",
        "frame_results": frame_results,
        "heatmap_frame": worst_frame,
        "heatmap": heatmap_b64
    }