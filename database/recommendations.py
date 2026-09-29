"""
CropGuard AI - Multilingual Recommendation & Advisory Engine
Provides farmer-friendly actionable steps, urgency grading, and localized advisory.
"""

from typing import Dict, Any, List
try:
    from .db import get_recommendation as db_get_recommendation
except ImportError:
    from db import get_recommendation as db_get_recommendation

try:
    from .disease_knowledge import DISEASE_KNOWLEDGE, get_disease_info, get_disease_info_by_key
except ImportError:
    from disease_knowledge import DISEASE_KNOWLEDGE, get_disease_info, get_disease_info_by_key

# Alias for test suite and external imports
DISEASE_ADVISORIES = DISEASE_KNOWLEDGE

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "flag": "🌐"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"}
}

SEVERITY_LEVELS = {
    "Healthy": {"color": "#10b981", "badge": "success", "description": "No infection detected", "risk": "Low"},
    "Low": {"color": "#3b82f6", "badge": "info", "description": "Mild spot/lesion (<15% leaf area)", "risk": "Minor"},
    "Medium": {"color": "#f59e0b", "badge": "warning", "description": "Noticeable spread (15-40% leaf area)", "risk": "Moderate"},
    "High": {"color": "#ef4444", "badge": "danger", "description": "Severe infestation (>40% leaf area)", "risk": "Critical"}
}


def get_farmer_advisory(crop: str, disease: str, severity: str = "Medium", lang: str = "en") -> Dict[str, Any]:
    """
    Produce a complete structured advisory response tailored to the farmer.
    Integrates DB localized records and comprehensive scientific knowledge base.
    """
    rec_data = db_get_recommendation(crop, disease, lang=lang)
    sev_info = SEVERITY_LEVELS.get(severity, SEVERITY_LEVELS["Medium"])
    d_info = get_disease_info(crop, disease) or get_disease_info_by_key(f"{crop}|{disease}")

    # Fallback to disease knowledge base if DB record is generic or missing
    if d_info and (not rec_data.get("found") or len(rec_data.get("description", "")) < 30):
        desc = d_info.get("description", rec_data["description"])
        urgency = d_info.get("urgency", rec_data["urgency"])
        mgmt = d_info.get("management", [])
        prev = d_info.get("prevention", [])

        rec_data["description"] = desc
        rec_data["urgency"] = urgency
        if mgmt:
            rec_data["recommended_action"] = mgmt[0]
            if len(mgmt) > 1:
                rec_data["organic_control"] = mgmt[1]
            if len(mgmt) > 2:
                rec_data["chemical_control"] = mgmt[2]
        if prev:
            rec_data["prevention_tips"] = "; ".join(prev)

    # Enhance with step-by-step action plan
    actions = [
        {"step": 1, "title": "Immediate Action", "text": rec_data["recommended_action"], "type": "critical"},
        {"step": 2, "title": "Organic / Bio Solution", "text": rec_data["organic_control"] or "Spray neem oil 5ml/L preventively.", "type": "organic"},
        {"step": 3, "title": "Recommended Spray", "text": rec_data["chemical_control"] or "Consult local agronomist.", "type": "chemical"},
        {"step": 4, "title": "Long-term Prevention", "text": rec_data["prevention_tips"], "type": "prevention"}
    ]

    result = {
        "crop": rec_data["crop"],
        "crop_icon": rec_data.get("crop_icon", "🌱"),
        "disease": rec_data["disease"],
        "original_disease": rec_data["original_disease"],
        "pathogen_type": rec_data["pathogen_type"],
        "description": rec_data["description"],
        "severity": severity,
        "severity_badge": sev_info["badge"],
        "severity_color": sev_info["color"],
        "urgency": rec_data["urgency"],
        "summary": rec_data["recommended_action"],
        "action_steps": actions,
        "organic_control": rec_data["organic_control"],
        "chemical_control": rec_data["chemical_control"],
        "prevention_tips": rec_data["prevention_tips"],
        "language": lang,
        "language_name": SUPPORTED_LANGUAGES.get(lang, {}).get("name", "English")
    }

    if d_info:
        result.update({
            "cause": d_info.get("cause", ""),
            "symptoms": d_info.get("symptoms", []),
            "spread": d_info.get("spread", []),
            "management": d_info.get("management", []),
            "prevention": d_info.get("prevention", []),
            "detailed_knowledge": d_info
        })

    return result


def get_available_languages() -> List[Dict[str, str]]:
    """Return list of supported languages for the frontend."""
    return [
        {"code": code, "name": meta["name"], "native": meta["native"], "flag": meta["flag"]}
        for code, meta in SUPPORTED_LANGUAGES.items()
    ]
