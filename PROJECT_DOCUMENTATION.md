# 🌿 CropGuard AI — Project Documentation

**Early Crop Disease Detection, Severity Quantification & Multilingual Farmer Advisory**

---

## 📌 1. Executive Summary & Problem Statement

Crop diseases and pest infestations cause up to **40% of global agricultural yield losses annually**. In rural farming communities, the lack of timely agronomic expertise, language barriers, and inability to quantify infection severity lead to delayed interventions or excessive, inappropriate pesticide use.

**CropGuard AI** solves this by putting an AI Agronomist directly in the farmer's pocket:
1. **Instant Disease Diagnosis**: Farmer uploads or captures a leaf photo via mobile camera.
2. **Computer Vision Severity Scoring**: OpenCV HSV color segmentation isolates leaf tissue and computes the exact `% affected leaf area` (Low, Medium, High).
3. **Actionable Local-Language Remedies**: Generates simple, non-technical treatment steps, organic alternatives (e.g. neem oil, trichoderma), chemical dosages, and urgency timelines in **5 regional languages** (English, Hindi, Marathi, Spanish, Telugu).
4. **Kisan Sahayak (Crop Doctor AI Chat)**: RAG assistant for natural-language Q&A on dosages and symptoms.
5. **Weather-Driven Disease Risk Radar**: Alerts farmers ahead of fungal spore outbreaks during high humidity.

---

## 🏗️ 2. Monorepo Architecture & Team Structure

The repository is organized into four decoupled modules matching the 3 sub-teams:

```
synergy/
├── database/                 # Team 3: Database, Recommendations & Innovation
│   ├── schema.sql            # SQLite schema (crops, diseases, translations, scans)
│   ├── db.py                 # SQLite initialization, CRUD queries, scan history
│   ├── recommendations.py    # Multilingual recommendation engine (EN, HI, MR, ES, TE)
│   ├── crop_doctor_rag.py    # Farmer AI Chatbot (RAG retrieval over agronomy DB)
│   ├── weather_risk.py       # Weather-driven fungal & pest risk index calculation
│   └── seed_data.json        # 18+ comprehensive crop diseases with multilingual actions
├── ml-model/                 # Team 1: AI & Image Detection Microservice
│   ├── dataset_downloader.py # PlantVillage dataset loading & augmentation pipeline
│   ├── train.py              # Transfer learning fine-tuning script (MobileNetV2 / ResNet18)
│   ├── predict.py            # Inference engine + OpenCV HSV leaf lesion segmentation
│   ├── ml_service.py         # Standalone Flask microservice exposing POST /predict (:5001)
│   ├── sample_images/        # High-res sample leaf images for instant demo testing
│   └── requirements.txt
├── backend/                  # Team 2: Backend API & Gateway Service
│   ├── app.py                # Flask API server (:5000) orchestrating ML + DB + UI
│   ├── config.py             # Server ports, upload folders, and microservice URLs
│   ├── requirements.txt
│   └── README.md
├── frontend/                 # Team 2: Farmer-Friendly Web Application
│   ├── index.html            # Mobile-first responsive UI with high-contrast accessibility
│   ├── css/styles.css        # Modern agricultural design system (emerald/warm earth)
│   ├── js/
│   │   ├── app.js            # Main frontend state controller & scan submissions
│   │   ├── camera.js         # Mobile camera capture & drag-and-drop dropzone
│   │   ├── audio.js          # Web Speech API (reads recommendations aloud to farmers)
│   │   └── i18n.js           # Multi-language UI text dictionaries
│   └── assets/samples/       # Pre-bundled sample leaf images for 1-click testing
├── run_all.py                # One-command startup script
└── PROJECT_DOCUMENTATION.md
```

---

## 🔗 3. System Data Flow & API Contracts

```
[Farmer Mobile Browser]
       │
       ▼ (1) Upload Leaf Image + Language ('hi', 'en', 'mr', 'es', 'te')
[Backend Gateway (:5000)] ── POST /api/upload
       │
       ▼ (2) Forwards Image Bytes
[ML Microservice (:5001)] ── POST /predict
       │
       ├─► PyTorch Transfer CNN ──► {crop: "Tomato", disease: "Early Blight", confidence: 0.93}
       └─► OpenCV HSV Color Mask ─► {affected_area_pct: 28.5%, severity: "Medium"}
       │
       ▼ (3) Returns ML Payload to Backend Gateway
[Database Layer (SQLite)] ── get_farmer_advisory("Tomato", "Early Blight", severity="Medium", lang="hi")
       │
       ├─► Fetches Hindi Treatment Plan, Organic Remedy, Chemical Spray Dosage, Urgency
       └─► Logs Scan in `scans` table
       │
       ▼ (4) Unified Response to Frontend
[Farmer Results Dashboard]
       ├─► High-contrast Severity Badge (Medium / Amber Pulse)
       ├─► Dual Progress Meters (% Affected Area & Confidence)
       ├─► Step-by-Step Action Cards (Organic + Chemical + Prevention)
       └─► 🔊 Voice Read-Aloud Button in Native Language
```

---

## 📊 4. Analytics Summary (For Demo / Hackathon Pitch)

- **AI Model**: MobileNetV2 / ResNet18 fine-tuned on PlantVillage dataset (54,306 images across 38 classes).
- **Computer Vision Segmentation**: OpenCV HSV color-space masking isolating green chlorophyll vs chlorotic/necrotic lesion tissue to quantify infection percentage with sub-second latency (<85ms).
- **Knowledge Base**: 18+ high-impact crop diseases covering Tomato, Potato, Corn, Apple, Grape, Rice, Wheat, Cotton.
- **Multilingual Support**: Fully translated advice into 5 languages: English, हिन्दी (Hindi), मराठी (Marathi), Español (Spanish), తెలుగు (Telugu).
- **Farmer Accessibility**: Web Speech API audio synthesis for illiterate/rural farmers, large tap targets (>48px), and high contrast for outdoor sunlight readability.

---

## 🚀 5. Quick Start Instructions

```bash
# 1. Install dependencies
pip install flask flask-cors pillow numpy opencv-python-headless requests torch torchvision

# 2. Start the complete application
python run_all.py
```

- **Web App**: [http://localhost:5000](http://localhost:5000)
- **ML Microservice**: [http://localhost:5001](http://localhost:5001)
