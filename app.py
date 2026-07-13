from flask import Flask, render_template,request,jsonify
import json
import os
import sqlite3
from fusion import enrich_alert, save_alert, get_all_alerts
from modules.m1_misinfo import analyze
from modules.factcheck import fact_check
from modules.m3_acoustic import predict_audio
from modules.m2_deepfake import analyze_video
from ultralytics import YOLO
model = YOLO("models/m4/yolov8n.pt")

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html",project_name="PRAHAR")

@app.route("/status")
def status():
    return {"module": "PRAHAR", "status": "online"}


@app.route("/search")
def search():
    query = request.args.get("q", "")
    conn = sqlite3.connect("database/prahar.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM weapons 
        WHERE name LIKE ? OR type LIKE ? OR description LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()

    results = [
        {"id": r[0], "name": r[1], "type": r[2], "country": r[3], "description": r[4]}
        for r in rows
    ]
    return {"results": results}

@app.route("/api/analyze")
def api_analyze():
    text = request.args.get("text", "")
    if not text:
        return {"error": "No text provided"}, 400
    result = analyze(text)
    return result

@app.route("/api/factcheck")
def api_factcheck():
    claim = request.args.get("text", "")
    if not claim:
        return {"error": "No text provided"}, 400
    result = fact_check(claim)
    return jsonify(result)

@app.route("/api/audio", methods=["POST"])
def api_audio():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400
    file = request.files["file"]
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    result = predict_audio(temp_path)
    os.remove(temp_path)
    return result

@app.route("/api/video", methods=["POST"])
def api_video():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files["file"]
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    
    result = analyze_video(temp_path)
    os.remove(temp_path)
    
    return result

@app.route("/api/image", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files["image"]
    save_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)
    results = model(save_path)
    r = results[0]
    detections = [{
        "class": model.names[int(box.cls[0])],
        "confidence": float(box.conf[0]),
        "bbox": box.xyxy[0].tolist()
    } for box in r.boxes]
    return jsonify({"filename": file.filename, "detections": detections})

@app.route("/api/fusion", methods=["POST"])
def api_fusion():
    data = request.get_json()
    module = data.get("module")   
    alert = data.get("alert")     

    if not module or alert is None:
        return jsonify({"error": "Provide 'module' and 'alert'"}), 400

    result = enrich_alert(module, alert)
    save_alert(
        module=module,
        raw_result=alert,
        enriched_context=result,
        severity=result["severity"],
    )
    return jsonify(result)

@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    return jsonify(get_all_alerts())

if __name__ == "__main__":
    app.run(debug=True)