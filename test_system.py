"""
CropGuard AI - End-to-End System Test Suite
Tests ML microservice, Backend Gateway, Database queries, Multilingual translations, Chatbot, and Weather Radar.
"""

import sys
import json
import requests
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_BACKEND = "http://localhost:5000"
BASE_ML = "http://localhost:5001"
SAMPLE_DIR = Path(__file__).resolve().parent / "ml-model" / "sample_images"


def test_ml_health():
    print("\n--- 1. Testing ML Microservice Health ---")
    resp = requests.get(f"{BASE_ML}/health", timeout=5)
    print(f"Status Code: {resp.status_code}")
    print("Response:", resp.json())
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_ml_predict():
    print("\n--- 2. Testing ML Microservice POST /predict Directly ---")
    test_img = SAMPLE_DIR / "tomato_early_blight.jpg"
    with open(test_img, "rb") as f:
        files = {"image": ("leaf.jpg", f.read(), "image/jpeg")}
        resp = requests.post(f"{BASE_ML}/predict", files=files, timeout=5)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print("Response:", json.dumps(data, indent=2))
    assert resp.status_code == 200
    assert "crop" in data
    assert "disease" in data
    assert "confidence" in data
    assert "affected_area_pct" in data
    assert "severity" in data


def test_backend_health():
    print("\n--- 3. Testing Backend Gateway Health ---")
    resp = requests.get(f"{BASE_BACKEND}/api/health", timeout=5)
    print(f"Status Code: {resp.status_code}")
    print("Response:", resp.json())
    assert resp.status_code == 200


def test_backend_samples():
    print("\n--- 4. Testing Backend /api/samples ---")
    resp = requests.get(f"{BASE_BACKEND}/api/samples", timeout=5)
    data = resp.json()
    print(f"Samples Count: {len(data.get('samples', []))}")
    assert resp.status_code == 200
    assert len(data.get("samples", [])) >= 5


def test_backend_upload_multilingual():
    print("\n--- 5. Testing Full Scan Pipeline (English & Hindi) ---")
    test_img = SAMPLE_DIR / "tomato_early_blight.jpg"
    
    # 5a. English scan
    with open(test_img, "rb") as f:
        files = {"image": ("leaf.jpg", f.read(), "image/jpeg")}
        data_payload = {"lang": "en", "session_id": "test_farmer"}
        resp = requests.post(f"{BASE_BACKEND}/api/upload", files=files, data=data_payload, timeout=8)
    
    print("English Scan Response Status:", resp.status_code)
    en_data = resp.json()
    print(f"Diagnosed: {en_data['crop']} - {en_data['disease']}")
    print(f"Severity: {en_data['severity']} ({en_data['affected_area_pct']}% affected leaf area)")
    print(f"Urgency: {en_data['urgency']}")
    print(f"Action Steps: {len(en_data['action_steps'])} steps")
    assert resp.status_code == 200
    assert en_data["status"] == "success"

    # 5b. Hindi scan
    with open(test_img, "rb") as f:
        files = {"image": ("leaf.jpg", f.read(), "image/jpeg")}
        data_payload = {"lang": "hi", "session_id": "test_farmer"}
        resp_hi = requests.post(f"{BASE_BACKEND}/api/upload", files=files, data=data_payload, timeout=8)
    
    hi_data = resp_hi.json()
    print("\nHindi Scan Response:")
    print("Language:", hi_data["language"])
    print("Disease (Hindi):", hi_data["disease"].encode("ascii", "replace").decode("ascii"))
    print("Urgency (Hindi):", hi_data["urgency"].encode("ascii", "replace").decode("ascii"))
    assert resp_hi.status_code == 200


def test_crop_doctor_chat():
    print("\n--- 6. Testing Crop Doctor AI (Kisan Sahayak RAG) ---")
    query_payload = {
        "query": "What is the organic remedy for tomato early blight?",
        "crop": "Tomato",
        "disease": "Early Blight",
        "lang": "en"
    }
    resp = requests.post(f"{BASE_BACKEND}/api/chat", json=query_payload, timeout=5)
    data = resp.json()
    print(f"Status: {resp.status_code}")
    ans = data["response"]["answer"]
    print("Doctor Answer Preview:", ans[:100].encode("ascii", "replace").decode("ascii"), "...")
    assert resp.status_code == 200
    assert "response" in data


def test_weather_risk_radar():
    print("\n--- 7. Testing Weather & Disease Risk Radar ---")
    resp = requests.get(f"{BASE_BACKEND}/api/weather-risk?temp=24.5&humidity=85&rain=6.0", timeout=5)
    data = resp.json()
    print(f"Overall Level: {data['risk_radar']['overall_level']}")
    print(f"Headline: {data['risk_radar']['headline']}")
    print(f"Risk Categories: {len(data['risk_radar']['risks'])}")
    assert resp.status_code == 200
    assert data["status"] == "success"


def test_history():
    print("\n--- 8. Testing Scan History Endpoint ---")
    resp = requests.get(f"{BASE_BACKEND}/api/history", timeout=5)
    data = resp.json()
    print(f"Recorded Scans in DB: {data['count']}")
    assert resp.status_code == 200
    assert data["count"] > 0


if __name__ == "__main__":
    print("==================================================")
    print("[TEST] STARTING CROPGUARD AI SYSTEM TEST SUITE")
    print("==================================================")
    
    test_ml_health()
    test_ml_predict()
    test_backend_health()
    test_backend_samples()
    test_backend_upload_multilingual()
    test_crop_doctor_chat()
    test_weather_risk_radar()
    test_history()

    print("\n==================================================")
    print("[SUCCESS] ALL CROPGUARD AI TESTS PASSED SUCCESSFULLY!")
    print("==================================================")
