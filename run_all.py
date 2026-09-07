"""
CropGuard AI - Single-Command Monorepo Launcher
Starts both the ML Microservice (port 5001) and Backend Gateway (port 5000).
"""

import sys
import time
import subprocess
import threading
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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


import socket
import argparse


def get_local_ip():
    """Retrieve host machine's primary local IP address for LAN access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_tunnel():
    """Optional public HTTPS tunnel for remote/cellular mobile access."""
    print("[Launcher] Starting public HTTPS tunnel...")
    # Attempt localtunnel via npx or ssh pinggy
    cmd = 'cmd.exe /c "npx --yes localtunnel --port 5000"'
    try:
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"[Launcher] Tunnel error: {e}")


def main():
    parser = argparse.ArgumentParser(description="CropGuard AI Platform Monorepo Launcher")
    parser.add_argument("--tunnel", action="store_true", help="Launch a public HTTPS tunnel for remote phone access")
    args = parser.parse_args()

    print("=" * 65)
    print("🌿  CROPGUARD AI — FULL-STACK PLATFORM LAUNCHER")
    print("=" * 65)

    local_ip = get_local_ip()

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

    if args.tunnel:
        tunnel_thread = threading.Thread(target=run_tunnel, daemon=True)
        tunnel_thread.start()
        time.sleep(2.0)

    print("\n✅ CropGuard AI Services Ready:")
    print(f"  💻 Local Web App:       http://localhost:5000")
    print(f"  📱 Mobile (Same Wi-Fi): http://{local_ip}:5000")
    print(f"  🧠 ML Microservice:     http://localhost:5001")
    print(f"  🗄️ Database:            SQLite (cropguard.db)")
    if args.tunnel:
        print(f"  🌐 Remote Tunnel:       Check terminal above for public URL")
    print("\nTip: On your phone or another device, open the Mobile link above.")
    print("Press Ctrl+C to terminate all services.\n")

    # 3. Start Backend Gateway in main thread
    run_backend()


if __name__ == "__main__":
    main()
