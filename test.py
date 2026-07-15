import base64
from modules.m2_deepfake import predict_deepfake

result = predict_deepfake(r"C:\Users\itzkh\OneDrive\Pictures\Screenshots\Screenshot 2026-07-15 181246.png")
print("Label:", result["label"], "| Fake score:", result["fake_score"])

if result["heatmap"]:
    with open("heatmap_output.jpg", "wb") as f:
        f.write(base64.b64decode(result["heatmap"]))
    print("Saved heatmap_output.jpg — open it to view")
else:
    print("No heatmap generated")