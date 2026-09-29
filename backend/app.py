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
import hashlib
import hmac
import smtplib
import sqlite3
import math
from email.message import EmailMessage

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    send_file,
    session,
    redirect
)
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
    from db import (
        init_db,
        save_scan,
        get_scan_history,
        get_scan_progress,
        get_all_crops,
        get_all_diseases
    )
    from recommendations import get_farmer_advisory, get_available_languages
    from crop_doctor_rag import ask_crop_doctor
    from weather_risk import calculate_disease_risks
except ImportError as e:
    print(f"[Backend WARN] Database imports failed: {e}")

# Farmer authentication database
try:
    from auth_db import (
        init_auth_db,
        register_farmer,
        login_farmer,
        get_farmer,
        create_pending_registration,
        get_pending_registration,
        update_pending_otp_request,
        can_resend_pending_otp,
        increment_pending_attempt,
        delete_pending_registration,
        finalize_pending_registration,
        registration_exists,
        find_farmer_by_email,
        create_password_reset_otp,
        get_password_reset_otp,
        can_resend_password_reset_otp,
        update_password_reset_otp,
        increment_password_reset_attempt,
        delete_password_reset_otp,
        update_farmer_password,
        delete_farmer_account,
        OTP_MAX_ATTEMPTS
    )
except ImportError as e:
    print(f"[Backend WARN] Authentication imports failed: {e}")
    init_auth_db = None
    register_farmer = None
    login_farmer = None
    get_farmer = None
    create_pending_registration = None
    get_pending_registration = None
    update_pending_otp_request = None
    can_resend_pending_otp = None
    increment_pending_attempt = None
    delete_pending_registration = None
    finalize_pending_registration = None
    registration_exists = None
    find_farmer_by_email = None
    create_password_reset_otp = None
    get_password_reset_otp = None
    can_resend_password_reset_otp = None
    update_password_reset_otp = None
    increment_password_reset_attempt = None
    delete_password_reset_otp = None
    update_farmer_password = None
    delete_farmer_account = None
    OTP_MAX_ATTEMPTS = 5

try:
    from predict import predict_image as direct_predict_image
except ImportError:
    direct_predict_image = None

# Initialize Flask app
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

# Secure Flask session for farmer authentication.
# For production, set CROPGUARD_SECRET_KEY in the environment.
app.config["SECRET_KEY"] = os.environ.get(
    "CROPGUARD_SECRET_KEY"
) or secrets.token_hex(32)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Local development uses HTTP. Set True when deployed behind HTTPS.
app.config["SESSION_COOKIE_SECURE"] = False

# Keep an authenticated farmer logged in for 30 days.
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)

CORS(app, supports_credentials=True)

# -------------------------------------------------------------
# Disease Outbreak Alert System
# -------------------------------------------------------------
# Uses a separate SQLite database so the existing auth/scan database
# structure does not need to be changed. Farmer identity always comes
# from the existing Flask session. Exact GPS coordinates are never
# returned to other farmers; they are used only for distance calculations.
OUTBREAK_DB_PATH = DATABASE_DIR / "outbreak_alerts.db"
OUTBREAK_RADIUS_KM = 10.0
OUTBREAK_WINDOW_DAYS = 7
OUTBREAK_MIN_REPORTS = 3
OUTBREAK_MIN_CONFIDENCE = 60.0


def _outbreak_db():
    conn = sqlite3.connect(str(OUTBREAK_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init_outbreak_db():
    OUTBREAK_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _outbreak_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS farmer_locations (
                farmer_id INTEGER PRIMARY KEY,
                village TEXT,
                taluka TEXT,
                district TEXT,
                state TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS disease_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER NOT NULL,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL DEFAULT 0,
                village TEXT,
                district TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                reported_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_disease_reports_lookup
            ON disease_reports (disease, crop, reported_at);

            CREATE INDEX IF NOT EXISTS idx_disease_reports_farmer
            ON disease_reports (farmer_id);
        """)
        conn.commit()
    finally:
        conn.close()


def _haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in kilometres."""
    radius = 6371.0
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def _valid_coordinates(latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (TypeError, ValueError):
        return False


def _reverse_geocode(latitude, longitude):
    """Convert GPS coordinates into village/taluka/district/state.

    Uses OpenStreetMap Nominatim reverse geocoding.  The exact GPS
    coordinates stay on the backend; only area-level names are returned
    to the logged-in farmer.
    """
    headers = {
        "User-Agent": "CropGuardAI/1.0 (agriculture project; contact administrator)",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "application/json",
    }

    response = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={
            "lat": float(latitude),
            "lon": float(longitude),
            "format": "jsonv2",
            "addressdetails": 1,
            "zoom": 18,
        },
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()

    payload = response.json()
    address = payload.get("address") or {}

    # Nominatim can use different keys for Indian administrative areas.
    village = (
        address.get("village")
        or address.get("hamlet")
        or address.get("town")
        or address.get("municipality")
        or address.get("city")
        or address.get("suburb")
        or ""
    )

    taluka = (
        address.get("subdistrict")
        or address.get("subdistrict_name")
        or address.get("tehsil")
        or address.get("taluk")
        or address.get("taluka")
        or address.get("county")
        or ""
    )

    district = (
        address.get("state_district")
        or address.get("district")
        or address.get("district_name")
        or ""
    )

    state = address.get("state") or ""

    return {
        "village": str(village).strip(),
        "taluka": str(taluka).strip(),
        "district": str(district).strip(),
        "state": str(state).strip(),
    }



def _save_farmer_location(farmer_id, latitude, longitude, village="", taluka="", district="", state=""):
    conn = _outbreak_db()
    try:
        conn.execute("""
            INSERT INTO farmer_locations
                (farmer_id, village, taluka, district, state, latitude, longitude, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(farmer_id) DO UPDATE SET
                village=excluded.village, taluka=excluded.taluka,
                district=excluded.district, state=excluded.state,
                latitude=excluded.latitude, longitude=excluded.longitude,
                updated_at=excluded.updated_at
        """, (
            int(farmer_id), village, taluka, district, state,
            float(latitude), float(longitude), datetime.datetime.utcnow().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()


def _get_farmer_location(farmer_id):
    conn = _outbreak_db()
    try:
        row = conn.execute(
            "SELECT * FROM farmer_locations WHERE farmer_id = ?",
            (int(farmer_id),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _record_disease_report(farmer_id, crop, disease, confidence):
    location = _get_farmer_location(farmer_id)
    if not location or not _valid_coordinates(location.get("latitude"), location.get("longitude")):
        return {"recorded": False, "reason": "Farmer location is not saved yet."}

    conn = _outbreak_db()
    try:
        conn.execute("""
            INSERT INTO disease_reports
                (farmer_id, crop, disease, confidence, village, district, latitude, longitude, reported_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(farmer_id), str(crop), str(disease), float(confidence or 0),
            location.get("village", ""), location.get("district", ""),
            float(location["latitude"]), float(location["longitude"]),
            datetime.datetime.utcnow().isoformat()
        ))
        conn.commit()
    finally:
        conn.close()
    return {"recorded": True, "location": location}


def _check_outbreak(farmer_id, crop, disease):
    """Check recent nearby reports for the same crop+disease."""
    location = _get_farmer_location(farmer_id)
    if not location:
        return {"outbreak_detected": False, "nearby_cases": 0, "reason": "Location not saved."}

    try:
        current_lat = float(location["latitude"])
        current_lon = float(location["longitude"])
    except (KeyError, TypeError, ValueError):
        return {"outbreak_detected": False, "nearby_cases": 0, "reason": "Invalid location."}

    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=OUTBREAK_WINDOW_DAYS)).isoformat()
    conn = _outbreak_db()
    try:
        rows = conn.execute("""
            SELECT farmer_id, crop, disease, confidence, village, district, latitude, longitude, reported_at
            FROM disease_reports
            WHERE lower(crop) = lower(?)
              AND lower(disease) = lower(?)
              AND reported_at >= ?
              AND confidence >= ?
        """, (crop, disease, cutoff, OUTBREAK_MIN_CONFIDENCE)).fetchall()
    finally:
        conn.close()

    nearby = []
    seen_farmers = set()
    for row in rows:
        if row["farmer_id"] in seen_farmers:
            continue
        distance = _haversine_km(current_lat, current_lon, row["latitude"], row["longitude"])
        if distance <= OUTBREAK_RADIUS_KM:
            seen_farmers.add(row["farmer_id"])
            nearby.append({
                "village": row["village"] or "nearby area",
                "district": row["district"] or "",
                "distance_km": round(distance, 2)
            })

    count = len(nearby)
    outbreak = count >= OUTBREAK_MIN_REPORTS
    return {
        "outbreak_detected": outbreak,
        "nearby_cases": count,
        "radius_km": OUTBREAK_RADIUS_KM,
        "window_days": OUTBREAK_WINDOW_DAYS,
        "minimum_reports": OUTBREAK_MIN_REPORTS,
        "areas": nearby[:10],
        "message": (
            f"Potential {disease} outbreak detected: {count} recent cases within {OUTBREAK_RADIUS_KM:g} km."
            if outbreak else
            f"No outbreak threshold reached. {count} recent nearby case(s) found."
        )
    }


def _init_outbreak_system():
    try:
        _init_outbreak_db()
        print(f"[Outbreak] Database ready: {OUTBREAK_DB_PATH}")
    except Exception as e:
        print(f"[Backend WARN] Outbreak database initialization failed: {e}")


_init_outbreak_system()

# -------------------------------------------------------------
# EMAIL OTP Registration Configuration (Gmail SMTP)
# -------------------------------------------------------------
# Keep the Gmail App Password in an environment variable.
# Never hard-code the password in this source file.
EMAIL_SMTP_HOST = os.environ.get("EMAIL_SMTP_HOST", "smtp.gmail.com").strip()
EMAIL_SMTP_PORT = int(os.environ.get("EMAIL_SMTP_PORT", "587").strip() or "587")
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "pratikdhote999@gmail.com").strip().lower()
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "").strip().replace(" ", "")
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "CropGuard AI").strip()

OTP_EXPIRY_SECONDS = 5 * 60
OTP_RESEND_COOLDOWN_SECONDS = 60

# Simple in-memory OTP request limiter in addition to the database cooldown.
_OTP_REQUEST_WINDOW = 60
_OTP_REQUEST_MAX = 3
_otp_request_store = defaultdict(list)
_otp_request_lock = Lock()


def _normalize_indian_mobile(mobile):
    """Accept common Indian formats and return 12 digits: 91XXXXXXXXXX."""
    value = re.sub(r"\D", "", str(mobile or ""))

    if value.startswith("91") and len(value) == 12:
        number = value[2:]
    elif len(value) == 10:
        number = value
    else:
        return None

    if not number.isdigit() or len(number) != 10 or number[0] not in "6789":
        return None

    return f"91{number}"


def _normalize_email(email):
    email = str(email or "").strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return None
    return email


def _mask_email(email):
    email = email or ""
    local, _, domain = email.partition("@")
    if not local or not domain:
        return "your email address"
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * min(5, len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(otp):
    # HMAC makes the stored value useless without the server secret.
    secret = app.config["SECRET_KEY"].encode("utf-8")
    return hmac.new(secret, otp.encode("utf-8"), hashlib.sha256).hexdigest()


def _otp_request_rate_limited():
    now = time.time()
    key = f"{_client_ip()}:/api/register/otp"

    with _otp_request_lock:
        timestamps = [
            t for t in _otp_request_store[key]
            if now - t < _OTP_REQUEST_WINDOW
        ]

        if len(timestamps) >= _OTP_REQUEST_MAX:
            _otp_request_store[key] = timestamps
            return True

        timestamps.append(now)
        _otp_request_store[key] = timestamps

    return False


def _password_reset_rate_limited():
    """Rate-limit password-reset OTP requests separately from registration OTPs."""
    now = time.time()
    key = f"{_client_ip()}:/api/forgot-password/otp"

    with _otp_request_lock:
        timestamps = [
            t for t in _otp_request_store[key]
            if now - t < _OTP_REQUEST_WINDOW
        ]

        if len(timestamps) >= _OTP_REQUEST_MAX:
            _otp_request_store[key] = timestamps
            return True

        timestamps.append(now)
        _otp_request_store[key] = timestamps

    return False


def _send_password_reset_otp(email, otp):
    """Send a six-digit password-reset OTP using the same Gmail SMTP configuration."""
    if not EMAIL_USERNAME or not EMAIL_APP_PASSWORD:
        return {
            "success": False,
            "message": "Email OTP is not configured on the server."
        }

    msg = EmailMessage()
    msg["Subject"] = "CropGuard AI - Password Reset OTP"
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USERNAME}>"
    msg["To"] = email

    msg.set_content(
        f"""Hello,

"
        f"Your CropGuard AI password reset OTP is: {otp}\n\n"
        f"This code is valid for 5 minutes.\n"
        f"Do not share this OTP with anyone.\n\n"
        f"If you did not request a password reset, you can ignore this email.\n\n"
        f"Regards,\n{EMAIL_FROM_NAME}"
        """
    )

    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USERNAME, EMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}

    except (smtplib.SMTPException, OSError) as exc:
        print(f"[PASSWORD RESET] Email send failed: {type(exc).__name__}: {exc}")
        return {
            "success": False,
            "message": "Could not send the password reset email. Check the Gmail SMTP configuration."
        }


def _send_email_otp(email, otp):
    """Send the six-digit registration OTP using Gmail SMTP."""
    if not EMAIL_USERNAME or not EMAIL_APP_PASSWORD:
        return {
            "success": False,
            "message": "Email OTP is not configured on the server."
        }

    msg = EmailMessage()
    msg["Subject"] = "CropGuard AI - Your Registration OTP"
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_USERNAME}>"
    msg["To"] = email

    msg.set_content(
        f"""Hello,\n\n"
        f"Your CropGuard AI registration OTP is: {otp}\n\n"
        f"This code is valid for 5 minutes.\n"
        f"Do not share this OTP with anyone.\n\n"
        f"If you did not request this registration, you can ignore this email.\n\n"
        f"Regards,\n{EMAIL_FROM_NAME}"
        """
    )

    try:
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USERNAME, EMAIL_APP_PASSWORD)
            server.send_message(msg)

        return {"success": True}

    except (smtplib.SMTPException, OSError) as exc:
        print(f"[OTP] Email send failed: {type(exc).__name__}: {exc}")
        return {
            "success": False,
            "message": "Could not send the email OTP. Check the Gmail SMTP configuration."
        }


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
    response.headers["Permissions-Policy"] = "camera=(self), microphone=(self)"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: blob: https://server.arcgisonline.com; "
        "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com; "
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
        "message": "File/request is too large. Maximum allowed size is 25 MB."
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
    # Unauthenticated visitors start at the farmer login page.
    # Authenticated farmers go directly to the main CropGuard application.
    if session.get("user_id"):
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    return send_from_directory(str(FRONTEND_DIR), "login.html")


@app.route("/forgot-password.html")
def serve_forgot_password():
    """Serve the farmer password-reset page."""
    return send_from_directory(str(FRONTEND_DIR), "forgot-password.html")


@app.route("/<path:path>")
def serve_static(path):
    # If the farmer is already logged in, do not show login.html again.
    if path == "login.html" and session.get("user_id"):
        return redirect("/")

    # Protect the main application and farmer dashboard even when a user
    # opens these HTML files directly instead of going through "/".
    protected_pages = {"index.html", "dashboard.html"}

    if path in protected_pages and not session.get("user_id"):
        return send_from_directory(str(FRONTEND_DIR), "login.html")

    file_path = FRONTEND_DIR / path
    if file_path.exists():
        return send_from_directory(str(FRONTEND_DIR), path)
    return send_from_directory(str(FRONTEND_DIR), "index.html")


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
# -------------------------------------------------------------
# Farmer Location + Disease Outbreak Alert APIs
# -------------------------------------------------------------

@app.route("/api/location", methods=["POST"])
def save_farmer_location():
    """Save the logged-in farmer's GPS location and village information."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Please login first."}), 401

    data = request.get_json(silent=True) or {}
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not _valid_coordinates(latitude, longitude):
        return jsonify({
            "status": "error",
            "message": "Valid latitude and longitude are required."
        }), 400

    try:
        location = _reverse_geocode(float(latitude), float(longitude))
    except Exception as e:
        print(f"[Location] Reverse geocoding failed: {e}")
        # Allow manual village/taluka/district fallback if geocoding is unavailable.
        location = {
            "village": str(data.get("village", "")).strip(),
            "taluka": str(data.get("taluka", "")).strip(),
            "district": str(data.get("district", "")).strip(),
            "state": str(data.get("state", "")).strip()
        }

    _save_farmer_location(
        user_id,
        float(latitude),
        float(longitude),
        location["village"],
        location["taluka"],
        location["district"],
        location["state"]
    )

    return jsonify({
        "status": "success",
        "message": "Farmer location saved successfully.",
        "location": {
            "village": location["village"],
            "taluka": location["taluka"],
            "district": location["district"],
            "state": location["state"]
        }
    })


@app.route("/api/location", methods=["GET"])
def get_farmer_location():
    """Return the logged-in farmer's area-level location, not exact GPS."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Please login first."}), 401

    location = _get_farmer_location(user_id)
    if not location:
        return jsonify({
            "status": "success",
            "location_saved": False,
            "message": "No farmer location saved yet."
        })

    return jsonify({
        "status": "success",
        "location_saved": True,
        "location": {
            "village": location.get("village", ""),
            "taluka": location.get("taluka", ""),
            "district": location.get("district", ""),
            "state": location.get("state", ""),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude")
        }
    })


@app.route("/api/outbreak/check", methods=["GET"])
def outbreak_check():
    """Return outbreak status for the logged-in farmer's current area."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Please login first."}), 401

    crop = request.args.get("crop", "").strip()
    disease = request.args.get("disease", "").strip()
    if not crop or not disease:
        return jsonify({
            "status": "error",
            "message": "crop and disease are required."
        }), 400

    result = _check_outbreak(user_id, crop, disease)
    return jsonify({"status": "success", **result})


@app.route("/api/outbreak/alerts", methods=["GET"])
def outbreak_alerts():
    """Return recent potential outbreak alerts for diseases already reported nearby."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Please login first."}), 401

    location = _get_farmer_location(user_id)
    if not location:
        return jsonify({"status": "success", "alerts": []})

    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=OUTBREAK_WINDOW_DAYS)).isoformat()
    conn = _outbreak_db()
    try:
        rows = conn.execute("""
            SELECT DISTINCT crop, disease
            FROM disease_reports
            WHERE reported_at >= ? AND farmer_id != ?
        """, (cutoff, int(user_id))).fetchall()
    finally:
        conn.close()

    alerts = []
    for row in rows:
        result = _check_outbreak(user_id, row["crop"], row["disease"])
        if result.get("outbreak_detected"):
            alerts.append({
                "crop": row["crop"],
                "disease": row["disease"],
                **result
            })

    return jsonify({
        "status": "success",
        "alerts": alerts
    })


# -------------------------------------------------------------
# Village-Level Disease Heatmap API
# -------------------------------------------------------------
# Aggregates recent disease reports by village/area. Individual
# farmer coordinates are never returned to the frontend.
HEATMAP_DEFAULT_DAYS = OUTBREAK_WINDOW_DAYS
HEATMAP_MIN_REPORTS = OUTBREAK_MIN_REPORTS


def _heatmap_risk(report_count):
    """Return a UI-friendly risk level and score from distinct farmer reports."""
    count = int(report_count or 0)

    if count >= 7:
        return "HIGH", 85, "red"
    if count >= 4:
        return "MODERATE", 60, "orange"
    if count >= HEATMAP_MIN_REPORTS:
        return "LOW", 35, "green"

    return "NONE", 0, "gray"


@app.route("/api/disease-heatmap", methods=["GET"])
def disease_heatmap():
    """
    Return privacy-safe village/area disease clusters.

    The frontend receives an aggregated zone centroid only when the
    zone has enough distinct farmer reports. Individual farmer pins,
    farmer IDs, and exact report coordinates are never returned.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Please login first."
        }), 401

    try:
        days = max(1, min(int(request.args.get("days", HEATMAP_DEFAULT_DAYS)), 30))
        min_reports = max(
            HEATMAP_MIN_REPORTS,
            int(request.args.get("min_reports", HEATMAP_MIN_REPORTS))
        )
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "days and min_reports must be valid numbers."
        }), 400

    crop_filter = request.args.get("crop", "").strip()
    disease_filter = request.args.get("disease", "").strip()
    village_filter = request.args.get("village", "").strip()

    cutoff = (
        datetime.datetime.utcnow() -
        datetime.timedelta(days=days)
    ).isoformat()

    query = """
        SELECT
            COALESCE(NULLIF(TRIM(village), ''), 'Monitoring Zone') AS village,
            COALESCE(NULLIF(TRIM(district), ''), '') AS district,
            crop,
            disease,
            COUNT(DISTINCT farmer_id) AS reports,
            COUNT(*) AS total_reports,
            AVG(latitude) AS center_latitude,
            AVG(longitude) AS center_longitude,
            MAX(reported_at) AS latest_report
        FROM disease_reports
        WHERE reported_at >= ?
          AND confidence >= ?
          AND lower(trim(disease)) NOT IN (
              'healthy',
              'healthy leaf',
              'no disease',
              'normal'
          )
    """

    params = [cutoff, OUTBREAK_MIN_CONFIDENCE]

    if crop_filter:
        query += " AND lower(trim(crop)) = lower(trim(?))"
        params.append(crop_filter)

    if disease_filter:
        query += " AND lower(trim(disease)) = lower(trim(?))"
        params.append(disease_filter)

    if village_filter:
        query += " AND lower(trim(village)) = lower(trim(?))"
        params.append(village_filter)

    query += """
        GROUP BY
            COALESCE(NULLIF(TRIM(village), ''), 'Monitoring Zone'),
            COALESCE(NULLIF(TRIM(district), ''), ''),
            crop,
            disease
        HAVING COUNT(DISTINCT farmer_id) >= ?
        ORDER BY reports DESC, latest_report DESC
    """
    params.append(min_reports)

    conn = _outbreak_db()

    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    zones = []

    for row in rows:
        risk, risk_score, color = _heatmap_risk(row["reports"])

        # Rounded aggregated centroid: it is intentionally not an
        # individual farmer's exact GPS location.
        center_lat = round(float(row["center_latitude"]), 3)
        center_lon = round(float(row["center_longitude"]), 3)

        zones.append({
            "village": row["village"],
            "district": row["district"],
            "crop": row["crop"],
            "disease": row["disease"],
            "reports": int(row["reports"]),
            "total_reports": int(row["total_reports"]),
            "risk": risk,
            "risk_score": risk_score,
            "color": color,
            "latitude": center_lat,
            "longitude": center_lon,
            "monitoring_radius_km": OUTBREAK_RADIUS_KM,
            "window_days": days,
            "latest_report": row["latest_report"]
        })

    return jsonify({
        "status": "success",
        "count": len(zones),
        "window_days": days,
        "minimum_reports": min_reports,
        "privacy": {
            "individual_farmer_pins": False,
            "exact_farmer_coordinates": False,
            "aggregation": "village/crop/disease"
        },
        "zones": zones
    })


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



# -------------------------------------------------------------
# Farmer Authentication API
# -------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Start farmer registration.

    The farmer is NOT created yet.
    This endpoint validates the details and sends an EMAIL OTP.
    """
    return api_register_request_otp()


@app.route("/api/register/request-otp", methods=["POST"])
def api_register_request_otp():
    """Validate registration details and send a real email OTP."""
    if create_pending_registration is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    if _otp_request_rate_limited():
        return jsonify({
            "status": "error",
            "message": "Too many OTP requests. Please wait before trying again."
        }), 429

    try:
        data = request.get_json(silent=True) or {}

        name = str(data.get("name", "")).strip()
        mobile_input = str(data.get("mobile", "")).strip()
        email = _normalize_email(data.get("email", ""))
        password = str(data.get("password", ""))

        if not name:
            return jsonify({
                "status": "error",
                "message": "Farmer name is required."
            }), 400

        mobile = _normalize_indian_mobile(mobile_input)
        if not mobile:
            return jsonify({
                "status": "error",
                "message": "Enter a valid 10-digit Indian mobile number."
            }), 400

        if not email:
            return jsonify({
                "status": "error",
                "message": "Enter a valid email address."
            }), 400

        if len(password) < 6:
            return jsonify({
                "status": "error",
                "message": "Password must contain at least 6 characters."
            }), 400

        if registration_exists(mobile=mobile, email=email):
            return jsonify({
                "status": "error",
                "message": "Mobile number or email is already registered."
            }), 409

        allowed, remaining = can_resend_pending_otp(email)
        if not allowed and remaining > 0:
            return jsonify({
                "status": "error",
                "message": f"Please wait {remaining} seconds before requesting another OTP."
            }), 429

        otp = _generate_otp()
        email_result = _send_email_otp(email, otp)

        if not email_result.get("success"):
            return jsonify({
                "status": "error",
                "message": email_result.get("message", "Could not send OTP.")
            }), 502

        result = create_pending_registration(
            name=name,
            mobile=mobile,
            email=email,
            password=password,
            otp_hash=_hash_otp(otp)
        )

        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get("message", "Could not start registration.")
            }), 400

        return jsonify({
            "status": "success",
            "message": "OTP sent successfully to your email address.",
            "email": _mask_email(email),
            "expires_in": OTP_EXPIRY_SECONDS,
            "resend_after": OTP_RESEND_COOLDOWN_SECONDS
        }), 200

    except Exception as e:
        print(f"[AUTH] Email OTP registration request error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not start farmer registration."
        }), 500


@app.route("/api/register/resend-otp", methods=["POST"])
def api_register_resend_otp():
    """Resend an OTP for an existing pending registration."""
    if get_pending_registration is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    if _otp_request_rate_limited():
        return jsonify({
            "status": "error",
            "message": "Too many OTP requests. Please wait before trying again."
        }), 429

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))

        if not email:
            return jsonify({
                "status": "error",
                "message": "Invalid email address."
            }), 400

        pending = get_pending_registration(email)
        if not pending:
            return jsonify({
                "status": "error",
                "message": "Registration request expired. Please register again."
            }), 404

        allowed, remaining = can_resend_pending_otp(email)
        if not allowed:
            return jsonify({
                "status": "error",
                "message": f"Please wait {remaining} seconds before requesting another OTP."
            }), 429

        otp = _generate_otp()
        email_result = _send_email_otp(email, otp)

        if not email_result.get("success"):
            return jsonify({
                "status": "error",
                "message": email_result.get("message", "Could not resend OTP.")
            }), 502

        update_pending_otp_request(email, _hash_otp(otp))

        return jsonify({
            "status": "success",
            "message": "A new OTP has been sent to your email.",
            "email": _mask_email(email),
            "expires_in": OTP_EXPIRY_SECONDS,
            "resend_after": OTP_RESEND_COOLDOWN_SECONDS
        })

    except Exception as e:
        print(f"[AUTH] Email OTP resend error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not resend OTP."
        }), 500


@app.route("/api/register/verify-otp", methods=["POST"])
def api_register_verify_otp():
    """Verify the locally stored email OTP and create the farmer account."""
    if get_pending_registration is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))
        otp = re.sub(r"\D", "", str(data.get("otp", "")))

        if not email or len(otp) != 6:
            return jsonify({
                "status": "error",
                "message": "Enter the 6-digit OTP."
            }), 400

        pending = get_pending_registration(email)
        if not pending:
            return jsonify({
                "status": "error",
                "message": "Registration request expired. Please register again."
            }), 404

        if int(pending["attempts"]) >= OTP_MAX_ATTEMPTS:
            delete_pending_registration(email)
            return jsonify({
                "status": "error",
                "message": "Too many incorrect OTP attempts. Please register again."
            }), 429

        stored_hash = pending.get("otp_hash")
        if not stored_hash or not hmac.compare_digest(_hash_otp(otp), stored_hash):
            attempts = increment_pending_attempt(email)

            if attempts >= OTP_MAX_ATTEMPTS:
                delete_pending_registration(email)
                return jsonify({
                    "status": "error",
                    "message": "Too many incorrect OTP attempts. Please register again."
                }), 429

            return jsonify({
                "status": "error",
                "message": "Invalid OTP. Please check the code and try again.",
                "attempts_remaining": OTP_MAX_ATTEMPTS - attempts
            }), 400

        result = finalize_pending_registration(email)
        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get("message", "Could not complete registration.")
            }), 400

        return jsonify({
            "status": "success",
            "message": "Email verified. Account created successfully.",
            "user": result.get("user")
        }), 201

    except Exception as e:
        print(f"[AUTH] Email OTP verification error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not verify OTP."
        }), 500


@app.route("/api/forgot-password/request-otp", methods=["POST"])
def api_forgot_password_request_otp():
    """Send a password-reset OTP to a registered farmer email address."""
    if find_farmer_by_email is None or create_password_reset_otp is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    if _password_reset_rate_limited():
        return jsonify({
            "status": "error",
            "message": "Too many OTP requests. Please wait before trying again."
        }), 429

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))

        if not email:
            return jsonify({
                "status": "error",
                "message": "Enter a valid email address."
            }), 400

        farmer = find_farmer_by_email(email)

        # Do not reveal whether an email address is registered.
        generic_response = {
            "status": "success",
            "message": "If an account exists for this email, a password reset OTP has been sent.",
            "email": _mask_email(email),
            "expires_in": OTP_EXPIRY_SECONDS,
            "resend_after": OTP_RESEND_COOLDOWN_SECONDS
        }

        if not farmer:
            return jsonify(generic_response), 200

        allowed, remaining = can_resend_password_reset_otp(email)
        if not allowed and remaining > 0:
            return jsonify({
                "status": "error",
                "message": f"Please wait {remaining} seconds before requesting another OTP."
            }), 429

        otp = _generate_otp()
        email_result = _send_password_reset_otp(email, otp)

        if not email_result.get("success"):
            return jsonify({
                "status": "error",
                "message": email_result.get(
                    "message",
                    "Could not send the password reset OTP."
                )
            }), 502

        result = create_password_reset_otp(email, _hash_otp(otp))
        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get("message", "Could not create password reset request.")
            }), 400

        return jsonify(generic_response), 200

    except Exception as e:
        print(f"[AUTH] Password reset OTP request error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not start password reset."
        }), 500


@app.route("/api/forgot-password/resend-otp", methods=["POST"])
def api_forgot_password_resend_otp():
    """Resend a password-reset OTP for a registered farmer."""
    if get_password_reset_otp is None or find_farmer_by_email is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    if _password_reset_rate_limited():
        return jsonify({
            "status": "error",
            "message": "Too many OTP requests. Please wait before trying again."
        }), 429

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))

        if not email:
            return jsonify({
                "status": "error",
                "message": "Invalid email address."
            }), 400

        if not find_farmer_by_email(email):
            return jsonify({
                "status": "success",
                "message": "If an account exists for this email, a new OTP has been sent.",
                "expires_in": OTP_EXPIRY_SECONDS,
                "resend_after": OTP_RESEND_COOLDOWN_SECONDS
            }), 200

        allowed, remaining = can_resend_password_reset_otp(email)
        if not allowed:
            return jsonify({
                "status": "error",
                "message": f"Please wait {remaining} seconds before requesting another OTP."
            }), 429

        otp = _generate_otp()
        email_result = _send_password_reset_otp(email, otp)

        if not email_result.get("success"):
            return jsonify({
                "status": "error",
                "message": email_result.get("message", "Could not resend OTP.")
            }), 502

        result = update_password_reset_otp(email, _hash_otp(otp))
        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get("message", "Could not update the reset OTP.")
            }), 400

        return jsonify({
            "status": "success",
            "message": "A new password reset OTP has been sent to your email.",
            "email": _mask_email(email),
            "expires_in": OTP_EXPIRY_SECONDS,
            "resend_after": OTP_RESEND_COOLDOWN_SECONDS
        }), 200

    except Exception as e:
        print(f"[AUTH] Password reset OTP resend error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not resend password reset OTP."
        }), 500


@app.route("/api/forgot-password/verify-otp", methods=["POST"])
def api_forgot_password_verify_otp():
    """Verify the password-reset OTP and issue a short-lived reset authorization token."""
    if get_password_reset_otp is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))
        otp = re.sub(r"\D", "", str(data.get("otp", "")))

        if not email or len(otp) != 6:
            return jsonify({
                "status": "error",
                "message": "Enter the 6-digit OTP."
            }), 400

        reset = get_password_reset_otp(email)
        if not reset:
            return jsonify({
                "status": "error",
                "message": "OTP expired or reset request not found. Please request a new OTP."
            }), 404

        if int(reset["attempts"]) >= OTP_MAX_ATTEMPTS:
            delete_password_reset_otp(email)
            return jsonify({
                "status": "error",
                "message": "Too many incorrect OTP attempts. Please request a new OTP."
            }), 429

        stored_hash = reset.get("otp_hash")
        if not stored_hash or not hmac.compare_digest(_hash_otp(otp), stored_hash):
            attempts = increment_password_reset_attempt(email)
            if attempts >= OTP_MAX_ATTEMPTS:
                delete_password_reset_otp(email)
                return jsonify({
                    "status": "error",
                    "message": "Too many incorrect OTP attempts. Please request a new OTP."
                }), 429

            return jsonify({
                "status": "error",
                "message": "Invalid OTP. Please check the code and try again.",
                "attempts_remaining": OTP_MAX_ATTEMPTS - attempts
            }), 400

        # The browser receives only a random, one-time reset token.
        reset_token = secrets.token_urlsafe(32)
        result = update_password_reset_otp(
            email,
            stored_hash,
            reset_token=reset_token,
            verified=True
        )

        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": "Could not verify the reset request."
            }), 400

        return jsonify({
            "status": "success",
            "message": "OTP verified. You can now create a new password.",
            "reset_token": reset_token
        }), 200

    except Exception as e:
        print(f"[AUTH] Password reset OTP verification error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not verify password reset OTP."
        }), 500


@app.route("/api/forgot-password/reset", methods=["POST"])
def api_forgot_password_reset():
    """Set a new password after successful email OTP verification."""
    if update_farmer_password is None or get_password_reset_otp is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    try:
        data = request.get_json(silent=True) or {}
        email = _normalize_email(data.get("email", ""))
        reset_token = str(data.get("reset_token", "")).strip()
        password = str(data.get("password") or data.get("new_password") or "")
        confirm_password = str(data.get("confirm_password") or "")

        if not email or not reset_token:
            return jsonify({
                "status": "error",
                "message": "Password reset verification is missing. Please verify the OTP again."
            }), 400

        if len(password) < 6:
            return jsonify({
                "status": "error",
                "message": "Password must contain at least 6 characters."
            }), 400

        if password != confirm_password:
            return jsonify({
                "status": "error",
                "message": "Passwords do not match."
            }), 400

        reset = get_password_reset_otp(email)
        if not reset or not reset.get("verified"):
            return jsonify({
                "status": "error",
                "message": "OTP verification expired. Please request a new OTP."
            }), 400

        stored_token = reset.get("reset_token") or ""
        if not hmac.compare_digest(reset_token, stored_token):
            return jsonify({
                "status": "error",
                "message": "Invalid password reset authorization. Please verify the OTP again."
            }), 403

        result = update_farmer_password(email, password)
        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get("message", "Could not update password.")
            }), 400

        delete_password_reset_otp(email)
        session.clear()

        return jsonify({
            "status": "success",
            "message": "Password reset successfully. Please login with your new password."
        }), 200

    except Exception as e:
        print(f"[AUTH] Password reset error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not reset password."
        }), 500


@app.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate a farmer and create a secure Flask session."""
    if login_farmer is None:
        return jsonify({
            "status": "error",
            "message": "Authentication system is unavailable."
        }), 503

    try:
        data = request.get_json(silent=True) or {}

        identifier = str(
            data.get("identifier")
            or data.get("mobile")
            or data.get("email")
            or ""
        ).strip()

        password = str(data.get("password", ""))

        if not identifier or not password:
            return jsonify({
                "status": "error",
                "message": "Mobile/email and password are required."
            }), 400

        result = login_farmer(
            identifier=identifier,
            password=password
        )

        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get(
                    "message",
                    "Invalid mobile/email or password."
                )
            }), 401

        user = result.get("user")

        if not user or not user.get("id"):
            return jsonify({
                "status": "error",
                "message": "Invalid farmer account."
            }), 401

        session.clear()
        session["user_id"] = int(user["id"])

        # Keep the farmer authenticated across browser restarts.
        session.permanent = True

        return jsonify({
            "status": "success",
            "message": "Login successful.",
            "user": user
        })

    except Exception as e:
        print(f"[AUTH] Login error: {e}")
        return jsonify({
            "status": "error",
            "message": "Login failed."
        }), 500


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Logout the current farmer."""
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Logged out successfully."
    })


@app.route("/api/delete-account", methods=["POST"])
def api_delete_account():
    """
    Permanently delete the currently authenticated farmer.

    Required JSON:
      {
        "current_password": "...",
        "confirmation": "DELETE"
      }

    The farmer identity always comes from the Flask session.
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Please login first."
        }), 401

    data = request.get_json(silent=True) or {}
    current_password = str(data.get("current_password") or "")
    confirmation = str(data.get("confirmation") or "").strip()

    if confirmation != "DELETE":
        return jsonify({
            "status": "error",
            "message": 'Type DELETE exactly to confirm account deletion.'
        }), 400

    if not current_password:
        return jsonify({
            "status": "error",
            "message": "Current password is required."
        }), 400

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        session.clear()
        return jsonify({
            "status": "error",
            "message": "Invalid farmer session. Please login again."
        }), 401

    if delete_farmer_account is None:
        return jsonify({
            "status": "error",
            "message": "Account deletion is not available on this server."
        }), 500

    try:
        result = delete_farmer_account(
            user_id=user_id,
            current_password=current_password
        )

        if not result.get("success"):
            return jsonify({
                "status": "error",
                "message": result.get(
                    "message",
                    "Account deletion failed."
                )
            }), 400

        # Database deletion is complete. Now remove this farmer's uploaded
        # leaf images. Filenames were generated by the backend, but still
        # enforce that every path stays inside UPLOAD_DIR.
        deleted_files = 0
        failed_files = 0

        upload_root = UPLOAD_DIR.resolve()

        for image_name in result.get("image_names", []):
            try:
                candidate = (UPLOAD_DIR / Path(str(image_name)).name).resolve()
                candidate.relative_to(upload_root)

                if candidate.is_file():
                    candidate.unlink()
                    deleted_files += 1
            except Exception as file_error:
                failed_files += 1
                print(
                    f"[AUTH] Could not delete uploaded scan image "
                    f"{image_name!r}: {file_error}"
                )

        # Invalidate the authenticated browser session.
        session.clear()

        return jsonify({
            "status": "success",
            "message": "Your CropGuard AI account and associated scan data have been permanently deleted.",
            "deleted_files": deleted_files,
            "failed_files": failed_files
        })

    except Exception as e:
        print(f"[AUTH] /api/delete-account error: {e}")
        return jsonify({
            "status": "error",
            "message": "Account deletion failed. Please try again."
        }), 500


@app.route("/api/me", methods=["GET"])
def api_me():
    """Return the currently authenticated farmer."""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Not logged in."
        }), 401

    try:
        farmer = get_farmer(int(user_id))

        if not farmer:
            session.clear()
            return jsonify({
                "status": "error",
                "message": "Farmer account not found."
            }), 401

        return jsonify({
            "status": "success",
            "user": farmer
        })

    except Exception as e:
        print(f"[AUTH] /api/me error: {e}")
        return jsonify({
            "status": "error",
            "message": "Could not load farmer account."
        }), 500


@app.route("/api/my-dashboard", methods=["GET"])
def api_my_dashboard():
    """Return dashboard data belonging only to the logged-in farmer."""
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Please login first."
        }), 401

    try:
        farmer = get_farmer(int(user_id))

        if not farmer:
            session.clear()
            return jsonify({
                "status": "error",
                "message": "Farmer account not found."
            }), 401

        # Never trust a frontend-provided session_id.
        farmer_session_id = f"farmer_{int(user_id)}"

        history = get_scan_history(
            limit=100,
            session_id=farmer_session_id
        )

        improving = 0
        stable = 0
        worsening = 0

        dashboard_scans = []

        for scan in history:
            scan_data = dict(scan)

            try:
                progress = get_scan_progress(
                    int(scan["id"]),
                    session_id=farmer_session_id
                )
            except Exception:
                progress = {
                    "status": "first_scan",
                    "label": "🔵 First scan",
                    "reason": "Baseline scan."
                }

            status = progress.get("status", "first_scan")

            if status == "improving":
                improving += 1
            elif status == "stable":
                stable += 1
            elif status == "worsening":
                worsening += 1

            scan_data["progress"] = progress
            dashboard_scans.append(scan_data)

        crops = sorted({
            str(scan.get("crop"))
            for scan in history
            if scan.get("crop")
        })

        return jsonify({
            "status": "success",
            "farmer": farmer,
            "stats": {
                "total_scans": len(history),
                "improving": improving,
                "stable": stable,
                "worsening": worsening
            },
            "crops": crops,
            "scans": dashboard_scans
        })

    except Exception as e:
        print(f"[Dashboard ERROR] {e}")
        return jsonify({
            "status": "error",
            "message": "Could not load farmer dashboard."
        }), 500



# -------------------------------------------------------------
# My Farm + Reports & Analytics
# -------------------------------------------------------------
def _analytics_health_score(scan):
    try:
        area=float(scan.get("affected_area_pct"))
        if math.isfinite(area): return max(0.0,min(100.0,100.0-area))
    except (TypeError,ValueError): pass
    sev=str(scan.get("severity") or "").lower()
    return 10.0 if "critical" in sev else 30.0 if "high" in sev else 60.0 if ("medium" in sev or "moderate" in sev) else 90.0

@app.route("/api/reports-analytics", methods=["GET"])
def reports_analytics():
    user_id=session.get("user_id")
    if not user_id: return jsonify({"status":"error","message":"Please login first."}),401
    try: farmer=get_farmer(int(user_id))
    except Exception: farmer=None
    if not farmer:
        session.clear(); return jsonify({"status":"error","message":"Farmer account not found."}),401
    try: days=int(request.args.get("days",30))
    except (TypeError,ValueError): days=30
    days=max(1,min(days,365)); sid=f"farmer_{int(user_id)}"
    history=get_scan_history(limit=500,session_id=sid)
    cutoff=datetime.datetime.utcnow()-datetime.timedelta(days=days); scans=[]
    for raw in history:
        item=dict(raw); include=True; created=item.get("created_at")
        if created:
            try:
                dt=datetime.datetime.fromisoformat(str(created).replace("Z","+00:00"))
                if dt.tzinfo: dt=dt.replace(tzinfo=None)
                include=dt>=cutoff
            except (TypeError,ValueError): pass
        if include:
            try: item["progress"]=get_scan_progress(int(item["id"]),session_id=sid)
            except Exception: item["progress"]={"status":"first_scan","label":"🔵 First scan","reason":"Baseline scan."}
            item["health_score"]=round(_analytics_health_score(item),2)
            item["risk_score"]=round(100-item["health_score"],2)
            scans.append(item)
    scans.sort(key=lambda x:(str(x.get("created_at") or ""),int(x.get("id") or 0)),reverse=True)

    grouped={}
    for s in scans: grouped.setdefault(str(s.get("crop") or "Unknown").strip() or "Unknown",[]).append(s)
    crops=[]
    for crop,items in sorted(grouped.items(),key=lambda x:x[0].lower()):
        latest=items[0]
        icon="🍅" if crop.lower()=="tomato" else "🌶️" if crop.lower() in {"chilli","chili","pepper"} else "🌱"
        crops.append({"crop":crop,"icon":icon,"health_score":latest["health_score"],"risk_score":latest["risk_score"],"latest_disease":latest.get("disease") or "Healthy","last_scan":latest.get("created_at"),"scan_count":len(items)})

    counts={}
    for s in scans:
        d=str(s.get("disease") or "Healthy").strip() or "Healthy"; counts[d]=counts.get(d,0)+1
    distribution=[{"disease":d,"count":n} for d,n in sorted(counts.items(),key=lambda x:(-x[1],x[0].lower()))]
    trend=[{"created_at":s.get("created_at"),"crop":s.get("crop"),"health_score":s["health_score"]} for s in reversed(scans)]
    improving=sum(1 for s in scans if s.get("progress",{}).get("status")=="improving")
    stable=sum(1 for s in scans if s.get("progress",{}).get("status")=="stable")
    worsening=sum(1 for s in scans if s.get("progress",{}).get("status")=="worsening")
    loc=_get_farmer_location(int(user_id)) or {}
    return jsonify({
        "status":"success","period_days":days,"farmer":farmer,
        "location":{"village":loc.get("village",""),"taluka":loc.get("taluka",""),"district":loc.get("district",""),"state":loc.get("state","")},
        "total_scans":len(scans),
        "average_health":round(sum(s["health_score"] for s in scans)/len(scans),2) if scans else None,
        "current_risk":scans[0]["risk_score"] if scans else None,
        "disease_count":len([d for d in distribution if d["disease"].lower()!="healthy"]),
        "stats":{"improving":improving,"stable":stable,"worsening":worsening},
        "crops":crops,"disease_distribution":distribution,"trend":trend,"scans":scans[:50]
    })


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

    # Authenticated farmer identity is controlled by the backend.
    # Do not trust a session_id sent by the browser.
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Please login before scanning a leaf."
        }), 401

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        session.clear()
        return jsonify({
            "status": "error",
            "message": "Invalid farmer session. Please login again."
        }), 401

    session_id = f"farmer_{user_id}"

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

        crop = ml_result.get("crop")
        disease = ml_result.get("disease")
        confidence = float(ml_result.get("confidence", 0))
        severity = ml_result.get("severity", "Unknown")
        affected_area_pct = float(
            ml_result.get("affected_area_pct", 0)
        )

        # Never silently convert an ML failure into Tomato / Early Blight.
        if not crop or not disease:
            return jsonify({
                "status": "error",
                "message": "AI could not identify a valid crop and disease."
            }), 422

        # 2. Record a disease report for the outbreak-alert engine.
        # Healthy scans are intentionally excluded from outbreak detection.
        outbreak_result = {
            "outbreak_detected": False,
            "nearby_cases": 0,
            "message": "No outbreak check performed."
        }
        if str(disease).strip().lower() not in {"healthy", "healthy leaf", "no disease", "normal"}:
            report_result = _record_disease_report(
                user_id, crop, disease, confidence
            )
            if report_result.get("recorded"):
                outbreak_result = _check_outbreak(user_id, crop, disease)
            else:
                outbreak_result["message"] = report_result.get("reason", "Farmer location is not saved yet.")

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
            "cause": advisory.get("cause", ""),
            "symptoms": advisory.get("symptoms", []),
            "spread": advisory.get("spread", []),
            "management": advisory.get("management", []),
            "prevention": advisory.get("prevention", []),
            "detailed_knowledge": advisory.get("detailed_knowledge", {}),
            "language": lang,
            "outbreak_detected": outbreak_result.get("outbreak_detected", False),
            "nearby_cases": outbreak_result.get("nearby_cases", 0),
            "outbreak_message": outbreak_result.get("message", ""),
            "outbreak_radius_km": outbreak_result.get("radius_km", OUTBREAK_RADIUS_KM),
            "outbreak_window_days": outbreak_result.get("window_days", OUTBREAK_WINDOW_DAYS),
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
    """Return scan history belonging to the current farmer."""
    try:
        limit = int(request.args.get("limit", 50))
        limit = max(1, min(limit, 100))

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "status": "error",
                "message": "Please login first."
            }), 401

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            session.clear()
            return jsonify({
                "status": "error",
                "message": "Invalid farmer session. Please login again."
            }), 401

        # Backend-controlled farmer identity.
        session_id = f"farmer_{user_id}"

        history = get_scan_history(
            limit=limit,
            session_id=session_id
        )

        for scan in history:
            try:
                scan["progress"] = get_scan_progress(
                    int(scan["id"]),
                    session_id=session_id
                )
            except Exception:
                scan["progress"] = {
                    "status": "first_scan",
                    "label": "🔵 First scan",
                    "reason": "Baseline scan."
                }

        return jsonify({
            "status": "success",
            "count": len(history),
            "scans": history
        })

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid history limit."
        }), 400

    except Exception as e:
        print(f"[History ERROR] {e}")
        return jsonify({
            "status": "error",
            "message": "Could not load scan history."
        }), 500


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
    if not session.get("user_id"):
        return jsonify({
            "status": "error",
            "message": "Please login first."
        }), 401

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


# Initialize databases when the application module is loaded as well as
# when it is executed directly. This keeps authentication available under
# Flask/WGI servers too.
try:
    init_db()
except Exception as e:
    print(f"[Backend WARN] Database initialization failed: {e}")

if init_auth_db:
    try:
        init_auth_db()
    except Exception as e:
        print(f"[Backend WARN] Authentication DB initialization failed: {e}")


if __name__ == "__main__":
    print(f"[Backend] Starting CropGuard Gateway on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)
