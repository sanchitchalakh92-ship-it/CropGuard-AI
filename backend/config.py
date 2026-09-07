"""
CropGuard AI - Backend Configuration
"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATABASE_DIR = PROJECT_ROOT / "database"
ML_MODEL_DIR = PROJECT_ROOT / "ml-model"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Ports and Microservice URLs
PORT = int(os.environ.get("PORT", 5000))
ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL", "http://localhost:5001")
ML_SERVICE_TIMEOUT_SEC = 5

# Database Settings
DB_PATH = DATABASE_DIR / "cropguard.db"

# Max Upload Size (25MB)
MAX_CONTENT_LENGTH = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

# -------------------------------------------------------------
# Security Settings
# -------------------------------------------------------------

# Maximum number of requests allowed from one client in a time window.
# This is used by the backend security/rate-limiting code.
RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60

# Maximum size for a single uploaded image.
# Kept in line with Flask's overall MAX_CONTENT_LENGTH.
MAX_IMAGE_SIZE = 25 * 1024 * 1024

# Never expose Flask's secret key directly in source code.
# Set CROP_GUARD_SECRET_KEY as an environment variable in deployment.
SECRET_KEY = os.environ.get("CROP_GUARD_SECRET_KEY")

# Security headers can be enabled by the backend app without changing
# the existing application configuration.
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(self), microphone=(), geolocation=()",
}

# Do not trust user-supplied filenames when saving uploaded files.
# The backend should generate its own filenames.
GENERATE_SAFE_UPLOAD_NAMES = True
