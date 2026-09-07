"""
CropGuard AI - Weather & Disease Risk Radar
Calculates real-time fungal, bacterial, and pest infestation risk scores
based on temperature, relative humidity, and rainfall factors.
"""

from typing import Dict, Any, List
import datetime


def calculate_disease_risks(
    temperature: float = 24.5,
    humidity: float = 82.0,
    rainfall_mm: float = 4.5,
    crop: str = "General"
) -> Dict[str, Any]:
    """
    Compute agronomic disease risk indices based on microclimate parameters.
    """
    # 1. Fungal Blight Risk (Early & Late Blight thrive at 18-26°C + >75% RH)
    fungal_score = 0.0
    if humidity > 85:
        fungal_score += 45
    elif humidity > 70:
        fungal_score += 30
    elif humidity > 55:
        fungal_score += 15

    if 18 <= temperature <= 28:
        fungal_score += 35
    elif 15 <= temperature < 18 or 28 < temperature <= 32:
        fungal_score += 20
    else:
        fungal_score += 5

    if rainfall_mm > 5.0:
        fungal_score += 20
    elif rainfall_mm > 0.0:
        fungal_score += 10

    fungal_score = min(100.0, fungal_score)

    # 2. Rust Risk (Cooler to moderate temp 15-22°C + high humidity or heavy dew)
    rust_score = 0.0
    if 15 <= temperature <= 23:
        rust_score += 40
    elif 23 < temperature <= 27:
        rust_score += 25

    if humidity > 80:
        rust_score += 40
    elif humidity > 60:
        rust_score += 25

    if rainfall_mm > 0:
        rust_score += 20

    rust_score = min(100.0, rust_score)

    # 3. Pest / Vector Risk (Whitefly, Thrips thrive in warm, dry-to-moderate conditions: 26-36°C, RH < 65%)
    pest_score = 0.0
    if 27 <= temperature <= 37:
        pest_score += 45
    elif 22 <= temperature < 27:
        pest_score += 25

    if humidity < 60:
        pest_score += 35
    elif humidity < 75:
        pest_score += 20

    if rainfall_mm == 0:
        pest_score += 20
    else:
        pest_score -= 15  # Rain washes away some nymphs

    pest_score = max(0.0, min(100.0, pest_score))

    # Helper for risk tier
    def get_risk_tier(score: float) -> Dict[str, str]:
        if score >= 75:
            return {"level": "CRITICAL", "color": "#ef4444", "badge": "danger", "action": "Immediate prophylactic spray advised"}
        elif score >= 50:
            return {"level": "MODERATE", "color": "#f59e0b", "badge": "warning", "action": "Monitor fields daily; spray if symptoms appear"}
        else:
            return {"level": "LOW", "color": "#10b981", "badge": "success", "action": "Favorable conditions; normal routine scouting"}

    fungal_tier = get_risk_tier(fungal_score)
    rust_tier = get_risk_tier(rust_score)
    pest_tier = get_risk_tier(pest_score)

    # Primary risk summary
    if fungal_score >= 75:
        headline = "High Fungal Blight Outbreak Risk Detected!"
        summary = f"High relative humidity ({humidity:.0f}%) and optimal temp ({temperature:.1f}°C) create prime conditions for Late Blight, Scab, and Downy Mildew."
        overall_level = "High Risk"
        overall_color = "#ef4444"
    elif pest_score >= 70:
        headline = "High Insect Vector & Sucking Pest Alert"
        summary = f"Warm conditions ({temperature:.1f}°C) and dry air favor rapid Whitefly, Thrip, and Spider Mite multiplication."
        overall_level = "Elevated Pest Risk"
        overall_color = "#f59e0b"
    elif fungal_score >= 50 or rust_score >= 50:
        headline = "Moderate Fungal Disease Caution"
        summary = f"Humidity levels ({humidity:.0f}%) are elevated. Keep canopy aerated and check lower leaves for brown spots."
        overall_level = "Moderate Alert"
        overall_color = "#f59e0b"
    else:
        headline = "Favorable Weather for Crop Growth"
        summary = "Current weather parameters do not favor rapid fungal sporulation or pest swarming."
        overall_level = "Low Risk"
        overall_color = "#10b981"

    # Action checklist
    advisory_checklist = []
    if fungal_score >= 50:
        advisory_checklist.append("Apply preventive copper spray or Mancozeb before expected rain.")
        advisory_checklist.append("Avoid irrigation during evening hours to keep leaves dry overnight.")
    if pest_score >= 50:
        advisory_checklist.append("Install yellow and blue sticky traps in crop rows.")
        advisory_checklist.append("Spray 2% neem oil to suppress early whitefly / aphid nymphs.")
    if not advisory_checklist:
        advisory_checklist.append("Continue balanced fertilization and routine weekly field walks.")

    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weather": {
            "temperature_c": round(temperature, 1),
            "humidity_pct": round(humidity, 1),
            "rainfall_mm": round(rainfall_mm, 1),
            "condition": "Humid / Overcast" if humidity > 75 else "Partly Sunny"
        },
        "overall_level": overall_level,
        "overall_color": overall_color,
        "headline": headline,
        "summary": summary,
        "risks": [
            {
                "category": "Fungal Blight & Spot",
                "score": round(fungal_score),
                "level": fungal_tier["level"],
                "color": fungal_tier["color"],
                "badge": fungal_tier["badge"],
                "target_diseases": ["Late Blight", "Early Blight", "Apple Scab", "Rice Blast"],
                "action": fungal_tier["action"]
            },
            {
                "category": "Rust & Powdery Mildew",
                "score": round(rust_score),
                "level": rust_tier["level"],
                "color": rust_tier["color"],
                "badge": rust_tier["badge"],
                "target_diseases": ["Corn Rust", "Cedar Apple Rust", "Wheat Rust"],
                "action": rust_tier["action"]
            },
            {
                "category": "Insect Pests & Whiteflies",
                "score": round(pest_score),
                "level": pest_tier["level"],
                "color": pest_tier["color"],
                "badge": pest_tier["badge"],
                "target_diseases": ["Tomato Yellow Leaf Curl Virus (Whitefly)", "Aphids", "Thrips"],
                "action": pest_tier["action"]
            }
        ],
        "advisory_checklist": advisory_checklist
    }
