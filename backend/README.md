# 🌐 CropGuard AI — Backend & Gateway Service

The Backend Gateway connects the Frontend, ML Microservice, and Database Knowledge Base into a unified application.

---

## 📡 API Endpoints

### 1. `POST /api/upload`
Uploads a crop leaf photo, queries ML service for disease + severity %, retrieves farmer recommendations from the database, records scan history, and returns full results.

- **Form Data**:
  - `image`: File (leaf photo)
  - `lang`: String (`en`, `hi`, `mr`, `es`, `te`) [default: `en`]
  - `session_id`: String [default: `default_farmer`]

- **Response**:
```json
{
  "status": "success",
  "id": 1,
  "crop": "Tomato",
  "crop_icon": "🍅",
  "disease": "Early Blight",
  "confidence": 0.93,
  "severity": "Medium",
  "severity_badge": "warning",
  "severity_color": "#f59e0b",
  "affected_area_pct": 28.5,
  "urgency": "Act within 24-48 hours",
  "summary": "Prune and dispose of infected bottom leaves immediately...",
  "action_steps": [...],
  "organic_control": "Spray neem oil solution (5ml/L)...",
  "chemical_control": "Apply Mancozeb 75% WP @ 2.5g/L...",
  "prevention_tips": "Rotate crops every 2-3 years...",
  "language": "en",
  "image_url": "/api/uploads/scan_1725200000_default_.jpg",
  "timestamp": "2026-09-01 22:15:00"
}
```

### 2. `GET /api/history`
Returns chronological past scan history.
- Query params: `limit` (default: 50), `session_id`

### 3. `GET /api/recommendation?crop=Tomato&disease=Early+Blight&lang=hi`
Direct lookup of recommended treatment.

### 4. `POST /api/chat`
Farmer Crop Doctor RAG Assistant.
- JSON Body: `{"query": "How to treat blight using organic neem?", "crop": "Tomato", "lang": "en"}`

### 5. `GET /api/weather-risk?temp=25&humidity=85&rain=5`
Computes real-time Fungal, Rust, and Pest outbreak risk indices.

### 6. `GET /api/samples`
Returns list of built-in sample leaf images for instant UI testing.

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```
The application runs at `http://localhost:5000` and automatically serves the frontend at the root URL.
