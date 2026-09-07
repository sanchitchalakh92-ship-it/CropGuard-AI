"""
CropGuard AI - Farmer Crop Doctor (RAG & Rule-Based Assistant)
Answers farmer questions about crop diseases, remedies, dosages, and pest management
using the database knowledge base as context.
"""

import re
from typing import Dict, Any, List
try:
    from .db import get_all_diseases, get_recommendation, get_all_crops
except ImportError:
    from db import get_all_diseases, get_recommendation, get_all_crops


def retrieve_disease_context(query: str) -> List[Dict[str, Any]]:
    """Search the database for diseases relevant to the user query."""
    query_lower = query.lower()
    all_diseases = get_all_diseases()
    matched = []

    for d in all_diseases:
        score = 0
        crop_name = d.get("crop_name", "").lower()
        d_name = d.get("name", "").lower()
        desc = d.get("description", "").lower()

        if crop_name in query_lower:
            score += 3
        if d_name in query_lower or any(word in d_name for word in query_lower.split() if len(word) > 3):
            score += 4
        if any(term in desc for term in ["fungal", "bacterial", "blight", "rust", "spot", "yellow", "curl"] if term in query_lower):
            score += 2

        if score > 0:
            matched.append((score, d))

    # Sort by relevance score
    matched.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in matched[:3]]


def ask_crop_doctor(query: str, crop_hint: str = None, disease_hint: str = None, lang: str = "en") -> Dict[str, Any]:
    """
    Generate an intelligent, practical, farmer-friendly response to queries.
    Uses RAG retrieval over verified agronomy seed data.
    """
    query_clean = query.strip()
    if not query_clean:
        return {
            "answer": "Hello farmer friend! Ask me any question about crop symptoms, leaf spots, organic neem sprays, fungicide dosages, or fertilizer management.",
            "sources": [],
            "suggested_questions": [
                "How to treat Tomato Early Blight organically?",
                "What is the best fungicide dosage for Potato Late Blight?",
                "How do I protect rice from blast disease?",
                "How does high humidity cause fungal leaf diseases?"
            ]
        }

    # Context retrieval
    contexts = retrieve_disease_context(query_clean)
    
    # Check for direct disease lookup if hint provided
    if crop_hint and disease_hint:
        direct = get_recommendation(crop_hint, disease_hint, lang=lang)
        if direct.get("found"):
            contexts.insert(0, direct)

    # Intelligent intent matching & synthesis
    q_low = query_clean.lower()
    sources = []

    # 1. Organic remedy query
    if any(k in q_low for k in ["organic", "natural", "neem", "home remedy", "biocontrol", "bio"]):
        if contexts:
            top = contexts[0]
            crop_n = top.get("crop_name") or top.get("crop", "your crop")
            d_n = top.get("name") or top.get("disease", "disease")
            org = top.get("organic_control") or "Spray neem oil (5ml/L) or Trichoderma bio-fungicide."
            prev = top.get("prevention_tips") or "Ensure good drainage and air circulation."
            sources.append(f"{crop_n} - {d_n}")

            answer = (
                f"🌿 **Organic Management for {crop_n} ({d_n}):**\n\n"
                f"1. **Bio-Control:** {org}\n"
                f"2. **Cultural Practice:** {prev}\n"
                f"3. **Prophylactic Spray:** Apply fermented cow urine (5%) or sour buttermilk spray (50ml/L) weekly in early mornings to boost leaf immunity."
            )
        else:
            answer = (
                "🌿 **General Organic Crop Protection Guidelines:**\n\n"
                "1. **Neem Oil Spray:** Mix 5ml pure neem oil (1500-3000 ppm) + 2ml liquid soap per 1 liter water. Spray early morning every 7-10 days.\n"
                "2. **Bio-Fungicides:** Apply *Trichoderma harzianum* (5g/L) for soil-borne pathogens or *Pseudomonas fluorescens* for foliar blights.\n"
                "3. **Airflow & Mulch:** Maintain 2-3 feet spacing and apply straw mulch to prevent soil-splash pathogens."
            )

    # 2. Chemical spray / dosage query
    elif any(k in q_low for k in ["chemical", "spray", "dose", "dosage", "fungicide", "pesticide", "medicine", "mancozeb"]):
        if contexts:
            top = contexts[0]
            crop_n = top.get("crop_name") or top.get("crop", "crop")
            d_n = top.get("name") or top.get("disease", "disease")
            chem = top.get("chemical_control") or "Apply standard Mancozeb 75% WP @ 2.5g/L."
            urg = top.get("urgency", "Act within 3 days")
            sources.append(f"{crop_n} - {d_n}")

            answer = (
                f"🧪 **Recommended Chemical Spray for {crop_n} ({d_n}):**\n\n"
                f"- **Active Spray:** {chem}\n"
                f"- **Application Timing:** Spray during calm mornings or late afternoons (avoid direct midday sun). Ensure uniform coverage under leaf surfaces.\n"
                f"- **Safety:** Wear mask and gloves. Observe 7-10 days pre-harvest interval (PHI).\n"
                f"- **Urgency:** {urg}."
            )
        else:
            answer = (
                "🧪 **Standard Fungicide Guidelines:**\n\n"
                "1. **Contact Fungicides (Preventive):** Mancozeb 75% WP @ 2.5g/L or Copper Oxychloride 50% WP @ 2.5g/L.\n"
                "2. **Systemic Fungicides (Curative):** Azoxystrobin + Difenoconazole @ 1ml/L or Ridomil Gold @ 2.5g/L for blights.\n"
                "3. Always check crop-specific labels and avoid mixing incompatible chemicals."
            )

    # 3. Specific disease / symptom inquiry
    elif contexts:
        top = contexts[0]
        crop_n = top.get("crop_name") or top.get("crop", "Crop")
        d_n = top.get("name") or top.get("disease", "Disease")
        desc = top.get("description", "")
        action = top.get("recommended_action", "")
        prev = top.get("prevention_tips", "")
        sources.append(f"{crop_n} - {d_n}")

        answer = (
            f"🔍 **Crop Doctor Diagnosis for {crop_n} — {d_n}:**\n\n"
            f"**Symptoms:** {desc}\n\n"
            f"**Recommended Action:** {action}\n\n"
            f"**Prevention:** {prev}"
        )

    # 4. General agriculture / farming advice
    else:
        answer = (
            "🌱 **Crop Doctor Advice:**\n\n"
            "To give you the most accurate solution, you can upload a photo of your leaf in the scanner, or mention your specific crop (Tomato, Potato, Corn, Apple, Rice, Grape) and observed symptoms (yellow spots, white powder, wilting, curling leaves)."
        )

    suggested = [
        "What is the dosage of Mancozeb for early blight?",
        "How to prepare organic neem oil spray?",
        "How to cure leaf curl virus in tomatoes?",
        "What causes white fuzz on the underside of leaves?"
    ]

    return {
        "query": query_clean,
        "answer": answer,
        "sources": sources,
        "suggested_questions": suggested
    }
