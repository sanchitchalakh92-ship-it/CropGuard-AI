"""
CropGuard AI - Single-Command Monorepo Launcher
Starts both the ML Microservice (port 5001) and Backend Gateway (port 5000).
"""

import sys
import time
import subprocess
import threading
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DB_DIR = ROOT_DIR / "database"
ML_DIR = ROOT_DIR / "ml-model"
BACKEND_DIR = ROOT_DIR / "backend"

# Add directories to python path
sys.path.insert(0, str(DB_DIR))
sys.path.insert(0, str(ML_DIR))
sys.path.insert(0, str(BACKEND_DIR))


def run_ml_service():
    """Start the ML Microservice on port 5001."""
    print("[Launcher] Starting ML Microservice on port 5001...")
    subprocess.run([sys.executable, str(ML_DIR / "ml_service.py")], cwd=str(ML_DIR))


def run_backend():
    """Start the Backend Gateway on port 5000."""
    print("[Launcher] Starting Backend Gateway on port 5000...")
    subprocess.run([sys.executable, str(BACKEND_DIR / "app.py")], cwd=str(BACKEND_DIR))


def main():
    print("=" * 65)
    print("🌿  CROPGUARD AI — FULL-STACK PLATFORM LAUNCHER")
    print("=" * 65)

    # 1. Initialize SQLite Database
    try:
        from db import init_db
        print("[Launcher] Checking database schema & seed data...")
        init_db()
    except Exception as e:
        print(f"[Launcher WARN] DB Init error: {e}")

    # 2. Start ML Microservice in background thread
    ml_thread = threading.Thread(target=run_ml_service, daemon=True)
    ml_thread.start()
    time.sleep(1.5)

    print("\n✅ CropGuard AI Services Ready:")
    print("  🌐 Web Application:  http://localhost:5000")
    print("  🧠 ML Microservice:  http://localhost:5001")
    print("  🗄️ Database:         SQLite (cropguard.db)")
    print("\nPress Ctrl+C to terminate all services.\n")

    # 3. Start Backend Gateway in main thread
    run_backend()


if __name__ == "__main__":
    main()
