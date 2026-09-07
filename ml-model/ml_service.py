"""
CropGuard AI - ML Microservice
Standalone Flask microservice exposing POST /predict for the AI & Image Detection team.
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from flask import Flask, request, jsonify
from flask_cors import CORS

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from predict import predict_image

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for the ML microservice."""
    return jsonify({
        "service": "CropGuard AI ML Service",
        "status": "healthy",
        "port": 5001,
        "engine": "PyTorch + OpenCV HSV Segmentation"
    })


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """
    ML Inference Endpoint:
    Accepts multipart/form-data with 'image' or 'file' key, or raw octet-stream.
    Returns:
    {
      "crop": "Tomato",
      "disease": "Early Blight",
      "confidence": 0.92,
      "severity": "Medium",
      "affected_area_pct": 34.5
    }
    """
    image_bytes = None

    if "image" in request.files:
        image_bytes = request.files["image"].read()
    elif "file" in request.files:
        image_bytes = request.files["file"].read()
    elif request.data:
        image_bytes = request.data

    if not image_bytes:
        return jsonify({
            "error": "No image provided. Please upload an image under key 'image' or 'file'."
        }), 400

    result = predict_image(image_bytes)
    return jsonify(result)


if __name__ == "__main__":
    print("[ML Service] Starting CropGuard ML Microservice on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=False)
