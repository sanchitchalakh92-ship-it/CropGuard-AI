# 🌿 CropGuard AI — ML & Computer Vision Microservice

This module handles **leaf disease classification** via PyTorch deep learning and **infection severity estimation** using OpenCV HSV color segmentation.

---

## 🎯 Architecture & Components

1. **`dataset_downloader.py`**: PlantVillage dataset loading, train/validation split, and data augmentation pipeline (rotation, flips, color jitter, normalization).
2. **`train.py`**: Fine-tuning script with MobileNetV2 / ResNet18 transfer learning backbone, AdamW optimizer, cosine annealing scheduler, and checkpoint exporter.
3. **`predict.py`**: Inference engine and OpenCV HSV segmentation algorithm:
   - Segments total leaf boundary.
   - Extracts chlorotic (yellowed) and necrotic (brown/black) lesion masks.
   - Computes exact `affected_area_pct` and classifies severity into `Healthy`, `Low`, `Medium`, `High`.
4. **`ml_service.py`**: Microservice exposing HTTP `POST /predict` on port `5001`.
5. **`generate_sample_leaves.py`**: Pre-generates realistic synthetic leaf images for instant demo testing.

---

## 🚀 Running the ML Microservice

```bash
# Install dependencies
pip install -r requirements.txt

# Start the ML Microservice
python ml_service.py
```

The service runs at `http://localhost:5001`.

### 📡 API Contract

#### `POST /predict`
**Request**:
- `multipart/form-data` with key `image` or `file` containing the leaf image file.

**Response**:
```json
{
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 0.93,
  "severity": "Medium",
  "affected_area_pct": 28.5,
  "status": "success"
}
```

---

## 🧠 Training Custom Models

To train on your own PlantVillage dataset:
1. Place dataset folders in `./data/plantvillage/<Class_Name>/<images...>`
2. Run:
```bash
python train.py --epochs 10 --backbone mobilenet_v2
```
This saves `model.pt` and `model_metadata.json`.
