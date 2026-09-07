"""
CropGuard AI - Fixed Inference Engine
Uses the exact class labels from model_metadata.json/checkpoint.
IMPORTANT: Never converts one disease into another disease just because
the word "rust" or "spot" appears in the class name.
"""

import io
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dataset_downloader import DEFAULT_CLASSES, get_transforms

MODEL_PATH = CURRENT_DIR / "model.pt"
METADATA_PATH = CURRENT_DIR / "model_metadata.json"

_CACHED_MODEL = None
_CACHED_CLASSES = DEFAULT_CLASSES


# Exact mappings for the 70 classes in the current model.
# Do not use generic disease-name rules here.
CLASS_MAP = {
    "Brinjal_Bacterial_wilt": ("Brinjal", "Bacterial Wilt"),
    "Brinjal_Cercospora_leaf_spot": ("Brinjal", "Cercospora Leaf Spot"),
    "Brinjal_little leaf_disease": ("Brinjal", "Little Leaf Disease"),
    "Brinjal_phomopsis_Blight": ("Brinjal", "Phomopsis Blight"),

    "CabbageBlack_root": ("Cabbage", "Black Root"),
    "Cabbage_Alternaria_Leaf_Spot": ("Cabbage", "Alternaria Leaf Spot"),
    "Cabbage_Downy_mildew": ("Cabbage", "Downy Mildew"),
    "Cabbage_Fusarium_Yellows": ("Cabbage", "Fusarium Yellows"),
    "Cabbage_club_root": ("Cabbage", "Clubroot"),

    "Cherry_Bacterial_Canker": ("Cherry", "Bacterial Canker"),
    "Cherry_brown_rot": ("Cherry", "Brown Rot"),

    "Cotton_Alternaria_Leaf_Spot": ("Cotton", "Alternaria Leaf Spot"),
    "Cotton_Bacterial_Blight": ("Cotton", "Bacterial Blight"),
    "Cotton_Fusarium_Wilt": ("Cotton", "Fusarium Wilt"),
    "Cotton_Grey_Mildew_(Areolate Mildew)": ("Cotton", "Grey Mildew (Areolate Mildew)"),
    "Cotton_Verticillium_Wilt": ("Cotton", "Verticillium Wilt"),

    "Grapes_Anthracnose": ("Grapes", "Anthracnose"),
    "Grapes_Bacterial_leaf_spot": ("Grapes", "Bacterial Leaf Spot"),
    "Grapes_Downy_Mildew": ("Grapes", "Downy Mildew"),
    "Grapes_Grey_Mold_(Botrytis)": ("Grapes", "Grey Mold (Botrytis)"),
    "Grapes_Powdery_mildew": ("Grapes", "Powdery Mildew"),

    "Maize(Corn)_common_rust_in_maize": ("Maize (Corn)", "Common Rust"),
    "maize_commonrust": ("Maize (Corn)", "Common Rust"),

    "Onion_Downy_Mildew — Peronospora destructor": ("Onion", "Downy Mildew"),
    "Onion_Fusarium_Basal_Plate_Rot": ("Onion", "Fusarium Basal Plate Rot"),
    "Onion_Purple_Blotch": ("Onion", "Purple Blotch"),
    "Onion_Stemphylium_Leaf_Blight — Stemphylium vesicarium": ("Onion", "Stemphylium Leaf Blight"),
    "Onion_White_Rot — Sclerotium cepivorum": ("Onion", "White Rot"),

    "Rice_Bacterial_leaf_Blight": ("Rice", "Bacterial Leaf Blight"),
    "Rice_Blast": ("Rice", "Blast"),
    "Rice_Brown_spots": ("Rice", "Brown Spot"),
    "Rice_Sheath_Blight": ("Rice", "Sheath Blight"),
    "Rice_tungro_disease": ("Rice", "Tungro Disease"),

    "Sugarcane_Grassy_Shoot_Disease": ("Sugarcane", "Grassy Shoot Disease"),
    "Sugarcane_Pokkah_Boeng_(Top Rot)": ("Sugarcane", "Pokkah Boeng (Top Rot)"),
    "Sugarcane_Red_root": ("Sugarcane", "Red Rot"),
    "Sugarcane_Smut": ("Sugarcane", "Smut"),
    "Sugarcane_Wilt": ("Sugarcane", "Wilt"),
    "Sugarcane_stalk_rot": ("Sugarcane", "Stalk Rot"),

    "Tomato_Bacterial_Spot": ("Tomato", "Bacterial Spot"),
    "Tomato_Late_blight": ("Tomato", "Late Blight"),
    "Tomato_Leaf_Early_Blight": ("Tomato", "Early Blight"),
    "Tomato_Leaf_Mold": ("Tomato", "Leaf Mold"),
    "Tomato_Spectoria_Leaf_Spot": ("Tomato", "Septoria Leaf Spot"),

    "Tur_Phytophthora Bligh": ("Tur (Pigeon Pea)", "Phytophthora Blight"),
    "Tur__Fusarium Wilt": ("Tur (Pigeon Pea)", "Fusarium Wilt"),

    "Wheat _Leaf_rust": ("Wheat", "Leaf Rust"),
    "Wheat_Fusarium_Head_Blight": ("Wheat", "Fusarium Head Blight"),
    "Wheat_Powdery_Mildew_disease": ("Wheat", "Powdery Mildew"),
    "Wheat_Septoria_Leaf_Blotch": ("Wheat", "Septoria Leaf Blotch"),
    "Wheat_stripe_rust": ("Wheat", "Stripe Rust"),

    "bajra_anthracnose_disease": ("Bajra (Pearl Millet)", "Anthracnose"),
    "bajra_anthracnose_disease - Copy": ("Bajra (Pearl Millet)", "Anthracnose"),
    "bajra_anthracnose_disease - Copy (2)": ("Bajra (Pearl Millet)", "Anthracnose"),
    "bajra_anthracnose_disease - Copy - Copy": ("Bajra (Pearl Millet)", "Anthracnose"),
    "bajra_downy_lmildew_eaf_disease": ("Bajra (Pearl Millet)", "Downy Mildew"),
    "bajra_leaf_rust_disease": ("Bajra (Pearl Millet)", "Leaf Rust"),
    "bajra_leaf_spot_disease": ("Bajra (Pearl Millet)", "Leaf Spot"),

    "groundnut_diseases": ("Groundnut", "Leaf Disease"),
    "jowar__leaf_spot_disease": ("Jowar (Sorghum)", "Leaf Spot"),
    "jowar_antharcnose_disease": ("Jowar (Sorghum)", "Anthracnose"),
    "jowar_antharcnose_disease - Copy": ("Jowar (Sorghum)", "Anthracnose"),
    "jowar_leaf_rust_disease": ("Jowar (Sorghum)", "Leaf Rust"),
    "jowar_mydis_leaf_spot": ("Jowar (Sorghum)", "Leaf Spot"),

    "ladyfinger_diseases": ("Ladyfinger (Okra)", "Leaf Disease"),

    "turmeric_leaf_anthracnose_diseas": ("Turmeric", "Leaf Anthracnose"),
    "turmeric_leaf_blight": ("Turmeric", "Leaf Blight"),
    "turmeric_leaf_blotch_diseas": ("Turmeric", "Leaf Blotch"),
    "turmeric_leaf_spot_diseas": ("Turmeric", "Leaf Spot"),
    "turmeric_rhizoctonia_leaf_blight_disease": ("Turmeric", "Rhizoctonia Leaf Blight"),
}


def parse_class_name(raw_class: str) -> Tuple[str, str]:
    """Return the exact canonical crop/disease pair for a model class."""
    raw_class = str(raw_class).strip()
    if raw_class in CLASS_MAP:
        return CLASS_MAP[raw_class]

    # Safe fallback for a future class: preserve the disease name.
    # Never translate generic "rust"/"spot" into another disease.
    if "___" in raw_class:
        raw_crop, raw_disease = raw_class.split("___", 1)
    elif "_" in raw_class:
        raw_crop, raw_disease = raw_class.split("_", 1)
    else:
        return "Unknown Crop", raw_class

    crop = " ".join(raw_crop.replace("(", " (").split())
    disease = " ".join(raw_disease.replace("_", " ").split()).strip(" -")
    return crop.title(), disease.title()


def compute_leaf_severity_opencv(image_np: np.ndarray) -> Tuple[float, str, np.ndarray]:
    """Estimate affected area for UI severity only; disease identity comes from ML."""
    if len(image_np.shape) == 2:
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
    elif image_np.shape[2] == 4:
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
    else:
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_green = np.array([25, 30, 30])
    upper_green = np.array([95, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    lower_brown = np.array([5, 40, 30])
    upper_brown = np.array([25, 255, 220])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)

    total_leaf_mask = cv2.bitwise_or(mask_green, mask_brown)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    total_leaf_mask = cv2.morphologyEx(total_leaf_mask, cv2.MORPH_CLOSE, kernel)
    total_leaf_mask = cv2.morphologyEx(total_leaf_mask, cv2.MORPH_OPEN, kernel)

    total_leaf_pixels = int(np.count_nonzero(total_leaf_mask))
    if total_leaf_pixels < image_bgr.shape[0] * image_bgr.shape[1] * 0.05:
        total_leaf_pixels = image_bgr.shape[0] * image_bgr.shape[1]
        total_leaf_mask = np.ones(image_bgr.shape[:2], dtype=np.uint8) * 255

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, dark_spots = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)
    dark_lesions = cv2.bitwise_and(dark_spots, total_leaf_mask)

    lower_yellow = np.array([12, 50, 60])
    upper_yellow = np.array([32, 255, 255])
    mask_chlorosis = cv2.inRange(hsv, lower_yellow, upper_yellow)
    diseased_foliage = cv2.bitwise_and(mask_chlorosis, total_leaf_mask)

    total_lesions = cv2.bitwise_or(dark_lesions, diseased_foliage)
    total_lesions = cv2.morphologyEx(total_lesions, cv2.MORPH_OPEN, kernel)

    lesion_pixels = int(np.count_nonzero(total_lesions))
    affected_pct = round((lesion_pixels / max(1, total_leaf_pixels)) * 100.0, 1)
    affected_pct = min(100.0, max(0.0, affected_pct))

    if affected_pct < 4:
        severity = "Healthy"
    elif affected_pct < 18:
        severity = "Low"
    elif affected_pct < 42:
        severity = "Medium"
    else:
        severity = "High"

    return affected_pct, severity, total_lesions


def load_model():
    global _CACHED_MODEL, _CACHED_CLASSES

    if _CACHED_MODEL is not None:
        return _CACHED_MODEL, _CACHED_CLASSES

    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
            classes = meta.get("classes")
            if isinstance(classes, list) and classes:
                _CACHED_CLASSES = classes
        except Exception as e:
            print(f"[ML WARN] Metadata read failed: {e}")

    if not MODEL_PATH.exists():
        return None, _CACHED_CLASSES

    try:
        from train import build_model
        checkpoint = torch.load(MODEL_PATH, map_location="cpu")
        classes = checkpoint.get("classes", _CACHED_CLASSES)
        backbone = checkpoint.get("backbone", "mobilenet_v2")

        model = build_model(
            num_classes=len(classes),
            backbone=backbone,
            pretrained=False,
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        _CACHED_MODEL = model
        _CACHED_CLASSES = classes
        print(f"[ML] Loaded model with {len(classes)} classes.")
        return _CACHED_MODEL, _CACHED_CLASSES

    except Exception as e:
        print(f"[ML ERROR] Model loading failed: {e}")
        return None, _CACHED_CLASSES


def predict_image(image_bytes: bytes) -> Dict[str, Any]:
    """Predict crop/disease and estimate severity."""
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(pil_img)

        affected_area_pct, cv_severity, _ = compute_leaf_severity_opencv(image_np)

        model, classes = load_model()
        if model is None:
            # Do NOT guess a disease when the trained model is unavailable.
            return {
                "status": "error",
                "message": "Trained disease model is unavailable.",
                "crop": "Unknown Crop",
                "disease": "Unknown Disease",
                "confidence": 0.0,
                "severity": cv_severity,
                "affected_area_pct": affected_area_pct,
            }

        _, val_tf = get_transforms()
        tensor_img = val_tf(pil_img).unsqueeze(0)

        with torch.no_grad():
            outputs = model(tensor_img)
            probs = F.softmax(outputs, dim=1)
            top_prob, top_idx = probs.max(1)

        predicted_class = classes[top_idx.item()]
        confidence = round(float(top_prob.item()), 4)
        crop, disease = parse_class_name(predicted_class)

        # Keep the original severity estimator, but do not invent a disease.
        if confidence < 0.50:
            status = "low_confidence"
        else:
            status = "success"

        severity = cv_severity
        if disease.lower() == "healthy":
            severity = "Healthy"
            affected_area_pct = min(affected_area_pct, 2.5)

        return {
            "crop": crop,
            "disease": disease,
            "confidence": confidence,
            "severity": severity,
            "affected_area_pct": affected_area_pct,
            "status": status,
            "model_class": predicted_class,
        }

    except Exception as e:
        # Never return a fake Tomato/Early Blight result on errors.
        return {
            "status": "error",
            "message": f"Inference failed: {e}",
            "crop": "Unknown Crop",
            "disease": "Unknown Disease",
            "confidence": 0.0,
            "severity": "Unknown",
            "affected_area_pct": 0.0,
        }


if __name__ == "__main__":
    print(f"Known exact class mappings: {len(CLASS_MAP)}")
    print("Model:", MODEL_PATH)
    print("Metadata:", METADATA_PATH)
