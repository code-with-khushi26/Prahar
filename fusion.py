"""
fusion.py
Combines detection outputs from PRAHAR's individual modules
(image/YOLO, audio, video/deepfake, text/misinfo) into a single
threat assessment.

Expected input format per module (adjust keys to match what your
modules actually return):

    image_result   = {"class": "truck", "confidence": 0.78}
    audio_result    = {"label": "gunshot", "confidence": 0.65}
    video_result    = {"is_deepfake": True, "confidence": 0.82}
    text_result     = {"is_misinfo": True, "confidence": 0.55}

Any module can be None if that input wasn't provided for this request.
"""

# Classes from YOLO that are considered defense-relevant proxies
# (since COCO has no tank/weapon/uniform classes)
RELEVANT_IMAGE_CLASSES = {"truck", "car", "airplane", "boat", "person"}

# Weights for each module in the final fused score (tune as needed)
WEIGHTS = {
    "image": 0.4,
    "audio": 0.2,
    "video": 0.2,
    "text": 0.2,
}

THREAT_THRESHOLDS = {
    "high": 0.7,
    "medium": 0.4,
}


def score_image(image_result):
    if not image_result:
        return 0.0
    cls = image_result.get("class")
    conf = image_result.get("confidence", 0.0)
    if cls in RELEVANT_IMAGE_CLASSES:
        return conf
    return 0.0


def score_audio(audio_result):
    if not audio_result:
        return 0.0
    return audio_result.get("confidence", 0.0)


def score_video(video_result):
    if not video_result:
        return 0.0
    if video_result.get("is_deepfake"):
        return video_result.get("confidence", 0.0)
    return 0.0


def score_text(text_result):
    if not text_result:
        return 0.0
    if text_result.get("is_misinfo"):
        return text_result.get("confidence", 0.0)
    return 0.0


def fuse_results(image_result=None, audio_result=None, video_result=None, text_result=None):
    """
    Combines individual module outputs into one weighted threat score.
    Returns a dict with the fused score, threat level, and per-module breakdown.
    """
    scores = {
        "image": score_image(image_result),
        "audio": score_audio(audio_result),
        "video": score_video(video_result),
        "text": score_text(text_result),
    }

    fused_score = sum(scores[k] * WEIGHTS[k] for k in scores)

    if fused_score >= THREAT_THRESHOLDS["high"]:
        threat_level = "HIGH"
    elif fused_score >= THREAT_THRESHOLDS["medium"]:
        threat_level = "MEDIUM"
    else:
        threat_level = "LOW"

    return {
        "fused_score": round(fused_score, 3),
        "threat_level": threat_level,
        "module_scores": scores,
        "inputs_used": {
            "image": image_result is not None,
            "audio": audio_result is not None,
            "video": video_result is not None,
            "text": text_result is not None,
        },
    }