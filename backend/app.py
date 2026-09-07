"""
CropGuard AI - Backend Gateway Application
Orchestrates ML Microservice, Database Layer, Crop Doctor RAG, and Frontend Delivery.
"""

import os
import sys
import time
import datetime
from pathlib import Path
from io import BytesIO
from collections import defaultdict
from threading import Lock
import re
import secrets

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import requests

from config import (
    PORT,
    ML_SERVICE_URL,
    ML_SERVICE_TIMEOUT_SEC,
    FRONTEND_DIR,
    DATABASE_DIR,
    ML_MODEL_DIR,
    UPLOAD_DIR,
    ALLOWED_EXTENSIONS
)

# Add database and ml-model to sys.path for direct access & fallback
sys.path.insert(0, str(DATABASE_DIR))
sys.path.insert(0, str(ML_MODEL_DIR))

try:
    from db import init_db, save_scan, get_scan_history, get_all_crops, get_all_diseases
    from recommendations import get_farmer_advisory, get_available_languages
    from crop_doctor_rag import ask_crop_doctor
    from weather_risk import calculate_disease_risks
except ImportError as e:
    print(f"[Backend WARN] Database imports failed: {e}")

try:
    from predict import predict_image as direct_predict_image
except ImportError:
    direct_predict_image = None

# Initialize Flask app
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

# -------------------------------------------------------------
# Security Configuration
# -------------------------------------------------------------
# Reject HTTP requests larger than 25 MB before they reach the upload handler.
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

# Simple in-memory rate limiter for the public POST APIs.
# This requires no extra package and is suitable for the current MVP/local deployment.
_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX_REQUESTS = 30
_rate_limit_store = defaultdict(list)
_rate_limit_lock = Lock()


def _client_ip():
    """Return the direct client address. Do not trust X-Forwarded-For by default."""
    return request.remote_addr or "unknown"


def _rate_limited():
    """Return True when a client exceeds the small MVP API request limit."""
    now = time.time()
    key = f"{_client_ip()}:{request.path}"
    with _rate_limit_lock:
        timestamps = [t for t in _rate_limit_store[key] if now - t < _RATE_LIMIT_WINDOW]
        if len(timestamps) >= _RATE_LIMIT_MAX_REQUESTS:
            _rate_limit_store[key] = timestamps
            return True
        timestamps.append(now)
        _rate_limit_store[key] = timestamps
    return False


@app.before_request
def security_before_request():
    # Rate-limit endpoints that can consume ML/LLM resources.
    if request.method == "POST" and request.path in {"/api/upload", "/api/chat"}:
        if _rate_limited():
            return jsonify({
                "status": "error",
                "message": "Too many requests. Please try again later."
            }), 429


@app.after_request
def security_headers(response):
    # Browser-side security headers; these do not change the application's API data.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(self), microphone=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "connect-src 'self' http: https:; "
        "font-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    )
    return response


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({
        "status": "error",
        "message": "File/request is too large. Maximum allowed size is 5 MB."
    }), 413


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_uploaded_image(filename: str, image_bytes: bytes) -> bool:
    """Validate extension and actual image contents before saving/processing."""
    if not filename or not is_allowed_file(filename):
        return False
    if not image_bytes or len(image_bytes) > app.config["MAX_CONTENT_LENGTH"]:
        return False
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
        return True
    except (UnidentifiedImageError, OSError, ValueError):
        return False


def make_safe_upload_name(original_filename: str, session_id: str) -> str:
    """Create a random server-side filename; never trust the user's filename."""
    extension = Path(secure_filename(original_filename)).suffix.lower()
    if extension not in {f".{ext.lower().lstrip('.') }" for ext in ALLOWED_EXTENSIONS}:
        extension = ".jpg"
    safe_session = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id))[:8] or "session"
    return f"scan_{int(time.time())}_{safe_session}_{secrets.token_hex(8)}{extension}"


# -------------------------------------------------------------
# Frontend Static Routing
# -------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/<path:path>")
def serve_static(path):
    file_path = FRONTEND_DIR / path
    if file_path.exists():
        return send_from_directory(str(FRONTEND_DIR), path)
    return send_from_directory(str(FRONTEND_DIR), "index.html")


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "CropGuard AI Backend Gateway",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/api/languages", methods=["GET"])
def languages_endpoint():
    """Return available languages for UI and advisory translation."""
    try:
        langs = get_available_languages()
        return jsonify({"status": "success", "languages": langs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/crops", methods=["GET"])
def crops_endpoint():
    """Return list of supported crops and their registered diseases."""
    try:
        crops = get_all_crops()
        return jsonify({"status": "success", "crops": crops})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_endpoint():
    """
    Main Scan Pipeline:
    1. Receives image from frontend (<input type="file"> / camera capture).
    2. Sends image to ML microservice POST /predict (with in-process fallback).
    3. Fetches farmer-friendly recommendation from Database in requested language.
    4. Records scan history into SQLite.
    5. Returns unified response to frontend.
    """
    if "image" not in request.files and "file" not in request.files:
        return jsonify({"status": "error", "message": "No image file provided."}), 400

    file = request.files.get("image") or request.files.get("file")
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file."}), 400

    lang = request.form.get("lang", "en").lower()
    session_id = request.form.get("session_id", "default_farmer")

    # Security: validate the extension AND the actual image bytes before saving.
    if not is_allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": "Unsupported image type. Allowed: JPG, JPEG, PNG, WEBP."
        }), 400

    try:
        image_bytes = file.read()
        if not validate_uploaded_image(file.filename, image_bytes):
            return jsonify({
                "status": "error",
                "message": "Invalid or corrupted image file."
            }), 400

        # Security: generate a server-controlled filename to prevent path traversal/collisions.
        save_name = make_safe_upload_name(file.filename, session_id)
        save_path = UPLOAD_DIR / save_name

        with open(save_path, "wb") as f:
            f.write(image_bytes)

        # 1. Forward to ML Microservice (or fallback)
        ml_result = None
        try:
            files_payload = {"image": (secure_filename(file.filename) or "leaf.jpg", image_bytes, "image/jpeg")}
            resp = requests.post(f"{ML_SERVICE_URL}/predict", files=files_payload, timeout=ML_SERVICE_TIMEOUT_SEC)
            if resp.status_code == 200:
                ml_result = resp.json()
        except Exception as ml_err:
            print(f"[Backend] ML Microservice call failed ({ml_err}), falling back to direct inference.")

        if not ml_result and direct_predict_image:
            ml_result = direct_predict_image(image_bytes)

        if not ml_result:
            return jsonify({
                "status": "error",
                "message": "ML Service unavailable and local inference failed."
            }), 503

        crop = ml_result.get("crop", "Tomato")
        disease = ml_result.get("disease", "Early Blight")
        confidence = float(ml_result.get("confidence", 0.90))
        severity = ml_result.get("severity", "Medium")
        affected_area_pct = float(ml_result.get("affected_area_pct", 25.0))

        # 2. Fetch Farmer Recommendation from DB
        advisory = get_farmer_advisory(crop, disease, severity=severity, lang=lang)

        # 3. Log scan in SQLite
        scan_id = save_scan(
            crop=advisory["crop"],
            disease=advisory["disease"],
            confidence=confidence,
            severity=severity,
            affected_area_pct=affected_area_pct,
            recommendation=advisory["summary"],
            urgency=advisory["urgency"],
            lang=lang,
            session_id=session_id,
            image_name=save_name
        )

        # 4. Return combined JSON
        return jsonify({
            "status": "success",
            "id": scan_id,
            "crop": advisory["crop"],
            "crop_icon": advisory.get("crop_icon", "🌱"),
            "disease": advisory["disease"],
            "original_disease": advisory["original_disease"],
            "pathogen_type": advisory["pathogen_type"],
            "confidence": confidence,
            "severity": severity,
            "severity_badge": advisory["severity_badge"],
            "severity_color": advisory["severity_color"],
            "affected_area_pct": affected_area_pct,
            "urgency": advisory["urgency"],
            "summary": advisory["summary"],
            "action_steps": advisory["action_steps"],
            "organic_control": advisory["organic_control"],
            "chemical_control": advisory["chemical_control"],
            "prevention_tips": advisory["prevention_tips"],
            "language": lang,
            "image_url": f"/api/uploads/{save_name}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        print(f"[Backend ERROR] Upload processing error: {e}")
        return jsonify({"status": "error", "message": f"Scan processing error: {str(e)}"}), 500


@app.route("/api/uploads/<filename>")
def serve_uploaded_image(filename):
    """Serve uploaded scan images."""
    return send_from_directory(str(UPLOAD_DIR), filename)


@app.route("/api/history", methods=["GET"])
def history_endpoint():
    """Return historical crop scans from database."""
    try:
        limit = int(request.args.get("limit", 50))
        session_id = request.args.get("session_id")
        history = get_scan_history(limit=limit, session_id=session_id)
        return jsonify({"status": "success", "count": len(history), "scans": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/recommendation", methods=["GET"])
def recommendation_endpoint():
    """Standalone recommendation lookup endpoint."""
    crop = request.args.get("crop", "Tomato")
    disease = request.args.get("disease", "Early Blight")
    severity = request.args.get("severity", "Medium")
    lang = request.args.get("lang", "en")

    try:
        advisory = get_farmer_advisory(crop, disease, severity=severity, lang=lang)
        return jsonify({"status": "success", "advisory": advisory})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Farmer AI Assistant (Crop Doctor RAG):
    Accepts question and optional crop context.
    """
    data = request.get_json() or {}
    query = data.get("query") or data.get("message") or ""
    crop_hint = data.get("crop")
    disease_hint = data.get("disease")
    lang = data.get("lang", "en")

    try:
        doctor_resp = ask_crop_doctor(query, crop_hint=crop_hint, disease_hint=disease_hint, lang=lang)
        return jsonify({"status": "success", "response": doctor_resp})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/weather-risk", methods=["GET"])
def weather_risk_endpoint():
    """
    Weather & Disease Risk Radar:
    Returns real-time fungal, rust, and pest outbreak risk indices.
    """
    try:
        temp = float(request.args.get("temp", 26.0))
        humidity = float(request.args.get("humidity", 82.0))
        rain = float(request.args.get("rain", 4.0))
        crop = request.args.get("crop", "General")

        risk_data = calculate_disease_risks(temperature=temp, humidity=humidity, rainfall_mm=rain, crop=crop)
        return jsonify({"status": "success", "risk_radar": risk_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/samples", methods=["GET"])
def list_samples():
    """Return list of available sample leaf images for instant UI demo."""
    sample_dir = ML_MODEL_DIR / "sample_images"
    samples = []
    sample_meta = {
        "tomato_early_blight.jpg": {"crop": "Tomato", "disease": "Early Blight", "title": "Tomato - Early Blight (Target Spots)", "icon": "🍅"},
        "tomato_healthy.jpg": {"crop": "Tomato", "disease": "Healthy", "title": "Tomato - Healthy Leaf", "icon": "🍅"},
        "potato_late_blight.jpg": {"crop": "Potato", "disease": "Late Blight", "title": "Potato - Late Blight (Water-soaked)", "icon": "🥔"},
        "corn_common_rust.jpg": {"crop": "Corn", "disease": "Common Rust", "title": "Corn - Common Rust (Cinnamon Pustules)", "icon": "🌽"},
        "apple_scab.jpg": {"crop": "Apple", "disease": "Apple Scab", "title": "Apple - Apple Scab (Olive Lesions)", "icon": "🍎"},
        "rice_blast.jpg": {"crop": "Rice", "disease": "Rice Blast", "title": "Rice - Leaf Blast (Spindle Lesions)", "icon": "🌾"}
    }

    if sample_dir.exists():
        for f in sample_dir.glob("*.jpg"):
            info = sample_meta.get(f.name, {"crop": "Crop", "disease": "Condition", "title": f.name, "icon": "🌱"})
            samples.append({
                "filename": f.name,
                "title": info["title"],
                "crop": info["crop"],
                "disease": info["disease"],
                "icon": info["icon"],
                "url": f"/api/sample-image/{f.name}"
            })

    return jsonify({"status": "success", "samples": samples})


@app.route("/api/sample-image/<filename>")
def serve_sample_image(filename):
    """Serve sample test leaf images."""
    sample_dir = ML_MODEL_DIR / "sample_images"
    return send_from_directory(str(sample_dir), filename)


if __name__ == "__main__":
    init_db()
    print(f"[Backend] Starting CropGuard Gateway on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)
