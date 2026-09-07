# 🌿 CropGuard AI

> **Early Crop Disease Detection, Severity Quantification & Local Farmer Advisory**

An end-to-end full-stack web application designed for farmers to detect crop diseases and pest infestations early from a photo of a leaf, quantify severity using computer vision, and receive actionable, farmer-friendly recommendations in their local language.

---

## ✨ Key Features

- 📸 **Mobile-First Leaf Scanner**: Drag & drop or direct camera capture (`capture="environment"`).
- 🧠 **AI Disease Classification**: Predicts crop type, disease name, and confidence score.
- 🔬 **OpenCV Severity Estimation**: Calculates exact `% affected leaf area` via HSV segmentation (Low, Medium, High).
- 🌐 **5 Regional Languages**: English, हिन्दी (Hindi), मराठी (Marathi), Español (Spanish), తెలుగు (Telugu).
- 🔊 **Voice Read-Aloud**: Text-to-speech audio assistant so farmers can listen to advice in their language.
- 👨‍🌾 **Crop Doctor AI Chat (Kisan Sahayak)**: RAG chatbot answering fertilizer, pesticide, and organic remedy questions.
- 🌦️ **Weather Risk Radar**: Real-time fungal and pest risk predictor based on humidity and temperature.
- 📜 **Scan History**: Full history logging in SQLite.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install flask flask-cors pillow numpy opencv-python-headless requests torch torchvision

# 2. Run the application
python run_all.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📁 Repository Structure

```
├── database/          # SQLite schema, seed data, multilingual recommendations, RAG chatbot, weather risk
├── ml-model/          # Dataset pipeline, MobileNetV2/ResNet model, predict.py, OpenCV severity, ml_service.py
├── backend/           # Flask API gateway (/api/upload, /api/history, /api/chat, /api/weather-risk)
├── frontend/          # HTML5, CSS3, Vanilla JS, SpeechSynthesis, Camera handling
├── run_all.py         # Monorepo one-command runner
└── PROJECT_DOCUMENTATION.md # Detailed architecture and analytics report
```
