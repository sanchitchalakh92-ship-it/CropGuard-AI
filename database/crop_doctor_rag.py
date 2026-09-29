"""
CropGuard AI - Farmer Crop Doctor (RAG & Rule-Based Assistant)

Answers farmer questions about crop diseases, remedies, dosages,
and pest management using the database knowledge base as context.

Supported response languages:
English, Hindi, Marathi.
"""

from typing import Dict, Any, List

try:
    from .db import get_all_diseases, get_recommendation, get_all_crops
except ImportError:
    from db import get_all_diseases, get_recommendation, get_all_crops


# ============================================================
# LANGUAGE HELPERS
# ============================================================

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}


def normalize_language(lang: str) -> str:
    """Convert language names/codes to en, hi, or mr."""

    if not lang:
        return "en"

    value = str(lang).strip().lower()

    aliases = {
        "english": "en",
        "en-us": "en",
        "en-in": "en",

        "hindi": "hi",
        "hi-in": "hi",

        "marathi": "mr",
        "mr-in": "mr",
    }

    value = aliases.get(value, value)

    # Spanish/Telugu are deliberately removed.
    # If an old frontend sends them, safely fall back to English.
    if value not in LANG_NAMES:
        return "en"

    return value


# ============================================================
# TRANSLATED RESPONSE TEXT
# ============================================================

TEXT = {
    "en": {
        "hello":
            "Hello farmer friend! Ask me any question about crop symptoms, "
            "leaf spots, organic neem sprays, fungicide dosages, or fertilizer management.",

        "organic_title":
            "🌿 **Organic Management for {crop} ({disease}):**",

        "bio":
            "**Bio-Control:** {value}",

        "cultural":
            "**Cultural Practice:** {value}",

        "prophylactic":
            "**Prophylactic Spray:** Apply fermented cow urine (5%) or sour buttermilk "
            "spray (50ml/L) weekly in early mornings to boost leaf immunity.",

        "general_organic":
            "🌿 **General Organic Crop Protection Guidelines:**",

        "neem":
            "**Neem Oil Spray:** Mix 5ml pure neem oil (1500-3000 ppm) + 2ml liquid soap "
            "per 1 liter water. Spray early morning every 7-10 days.",

        "biofungicide":
            "**Bio-Fungicides:** Apply *Trichoderma harzianum* (5g/L) for soil-borne "
            "pathogens or *Pseudomonas fluorescens* for foliar blights.",

        "airflow":
            "**Airflow & Mulch:** Maintain 2-3 feet spacing and apply straw mulch "
            "to prevent soil-splash pathogens.",

        "chemical_title":
            "🧪 **Recommended Chemical Spray for {crop} ({disease}):**",

        "active":
            "**Active Spray:** {value}",

        "timing":
            "**Application Timing:** Spray during calm mornings or late afternoons "
            "(avoid direct midday sun). Ensure uniform coverage under leaf surfaces.",

        "safety":
            "**Safety:** Wear mask and gloves. Observe 7-10 days pre-harvest interval (PHI).",

        "urgency":
            "**Urgency:** {value}.",

        "general_chemical":
            "🧪 **Standard Fungicide Guidelines:**",

        "contact":
            "**Contact Fungicides (Preventive):** Mancozeb 75% WP @ 2.5g/L or "
            "Copper Oxychloride 50% WP @ 2.5g/L.",

        "systemic":
            "**Systemic Fungicides (Curative):** Azoxystrobin + Difenoconazole @ 1ml/L "
            "or Ridomil Gold @ 2.5g/L for blights.",

        "mixing":
            "Always check crop-specific labels and avoid mixing incompatible chemicals.",

        "diagnosis":
            "🔍 **Crop Doctor Diagnosis for {crop} — {disease}:**",

        "symptoms":
            "**Symptoms:** {value}",

        "action":
            "**Recommended Action:** {value}",

        "prevention":
            "**Prevention:** {value}",

        "general_title":
            "🌱 **Crop Doctor Advice:**",

        "general_body":
            "To give you the most accurate solution, you can upload a photo of your leaf "
            "in the scanner, or mention your specific crop (Tomato, Potato, Corn, Apple, "
            "Rice, Grape) and observed symptoms (yellow spots, white powder, wilting, "
            "curling leaves).",

        "q1":
            "What is the dosage of Mancozeb for early blight?",

        "q2":
            "How to prepare organic neem oil spray?",

        "q3":
            "How to cure leaf curl virus in tomatoes?",

        "q4":
            "What causes white fuzz on the underside of leaves?",
    },

    # ========================================================
    # HINDI
    # ========================================================

    "hi": {
        "hello":
            "नमस्ते किसान मित्र! फसल के लक्षण, पत्तियों के धब्बे, "
            "जैविक नीम स्प्रे, फफूंदनाशक की मात्रा या उर्वरक प्रबंधन के बारे में पूछें।",

        "organic_title":
            "🌿 **{crop} ({disease}) के लिए जैविक प्रबंधन:**",

        "bio":
            "**जैव नियंत्रण:** {value}",

        "cultural":
            "**कृषि प्रबंधन:** {value}",

        "prophylactic":
            "**रोकथाम स्प्रे:** पौधों की प्रतिरोधक क्षमता बनाए रखने के लिए "
            "सुबह के समय 5% किण्वित गोमूत्र या 50ml/L छाछ का छिड़काव करें।",

        "general_organic":
            "🌿 **सामान्य जैविक फसल सुरक्षा दिशानिर्देश:**",

        "neem":
            "**नीम तेल स्प्रे:** 1 लीटर पानी में 5ml शुद्ध नीम तेल "
            "(1500-3000 ppm) और 2ml लिक्विड साबुन मिलाएं। "
            "हर 7-10 दिन में सुबह छिड़काव करें।",

        "biofungicide":
            "**जैव-फफूंदनाशक:** मिट्टी से होने वाले रोगों के लिए "
            "*Trichoderma harzianum* (5g/L) या पत्तियों के फफूंद रोगों के लिए "
            "*Pseudomonas fluorescens* का उपयोग करें।",

        "airflow":
            "**हवा का प्रवाह और मल्च:** पौधों के बीच 2-3 फीट दूरी रखें और "
            "मिट्टी से रोग फैलने से रोकने के लिए पुआल मल्च का उपयोग करें।",

        "chemical_title":
            "🧪 **{crop} ({disease}) के लिए अनुशंसित रासायनिक स्प्रे:**",

        "active":
            "**सक्रिय स्प्रे:** {value}",

        "timing":
            "**छिड़काव का समय:** शांत मौसम में सुबह या देर दोपहर छिड़काव करें। "
            "दोपहर की तेज धूप से बचें और पत्तियों की निचली सतह पर भी समान रूप से "
            "छिड़काव करें।",

        "safety":
            "**सुरक्षा:** मास्क और दस्ताने पहनें। फसल कटाई से पहले निर्धारित "
            "7-10 दिनों के अंतराल (PHI) का पालन करें।",

        "urgency":
            "**तात्कालिकता:** {value}.",

        "general_chemical":
            "🧪 **सामान्य फफूंदनाशक दिशानिर्देश:**",

        "contact":
            "**संपर्क फफूंदनाशक (रोकथाम):** Mancozeb 75% WP @ 2.5g/L या "
            "Copper Oxychloride 50% WP @ 2.5g/L।",

        "systemic":
            "**सिस्टमिक फफूंदनाशक (उपचार):** Azoxystrobin + Difenoconazole @ 1ml/L "
            "या ब्लाइट के लिए Ridomil Gold @ 2.5g/L।",

        "mixing":
            "हमेशा फसल-विशिष्ट लेबल की जांच करें और असंगत रसायनों को मिलाने से बचें।",

        "diagnosis":
            "🔍 **{crop} — {disease} के लिए Crop Doctor निदान:**",

        "symptoms":
            "**लक्षण:** {value}",

        "action":
            "**अनुशंसित उपाय:** {value}",

        "prevention":
            "**रोकथाम:** {value}",

        "general_title":
            "🌱 **Crop Doctor की सलाह:**",

        "general_body":
            "सबसे सटीक समाधान के लिए अपनी पत्ती की फोटो स्कैनर में अपलोड करें "
            "या अपनी फसल (Tomato, Potato, Corn, Apple, Rice, Grape) और दिखाई देने "
            "वाले लक्षण जैसे पीले धब्बे, सफेद पाउडर, मुरझाना या पत्तियों का मुड़ना बताएं।",

        "q1":
            "Early Blight के लिए Mancozeb की मात्रा कितनी है?",

        "q2":
            "जैविक नीम तेल स्प्रे कैसे तैयार करें?",

        "q3":
            "टमाटर में Leaf Curl Virus का उपचार कैसे करें?",

        "q4":
            "पत्तियों के नीचे सफेद फफूंद क्यों दिखाई देती है?",
    },

    # ========================================================
    # MARATHI
    # ========================================================

    "mr": {
        "hello":
            "नमस्कार शेतकरी मित्रा! पिकांची लक्षणे, पानांवरील डाग, "
            "सेंद्रिय कडुनिंब फवारणी, बुरशीनाशकांचे प्रमाण किंवा खत व्यवस्थापनाबद्दल विचारा.",

        "organic_title":
            "🌿 **{crop} ({disease}) साठी सेंद्रिय व्यवस्थापन:**",

        "bio":
            "**जैविक नियंत्रण:** {value}",

        "cultural":
            "**पीक व्यवस्थापन:** {value}",

        "prophylactic":
            "**प्रतिबंधात्मक फवारणी:** पिकाची प्रतिकारशक्ती वाढवण्यासाठी "
            "सकाळच्या वेळी 5% आंबवलेले गोमूत्र किंवा 50ml/L ताकाची फवारणी करा.",

        "general_organic":
            "🌿 **सामान्य सेंद्रिय पीक संरक्षण मार्गदर्शक:**",

        "neem":
            "**कडुनिंब तेलाची फवारणी:** 1 लिटर पाण्यात 5ml शुद्ध कडुनिंब तेल "
            "(1500-3000 ppm) आणि 2ml द्रव साबण मिसळा. "
            "दर 7-10 दिवसांनी सकाळी फवारणी करा.",

        "biofungicide":
            "**जैविक बुरशीनाशके:** मातीजन्य रोगांसाठी "
            "*Trichoderma harzianum* (5g/L) किंवा पानांवरील बुरशीजन्य रोगांसाठी "
            "*Pseudomonas fluorescens* वापरा.",

        "airflow":
            "**हवेचा प्रवाह आणि आच्छादन:** झाडांमध्ये 2-3 फूट अंतर ठेवा "
            "आणि मातीमधून रोग पसरणे टाळण्यासाठी पेंढ्याचे आच्छादन वापरा.",

        "chemical_title":
            "🧪 **{crop} ({disease}) साठी शिफारस केलेली रासायनिक फवारणी:**",

        "active":
            "**सक्रिय फवारणी:** {value}",

        "timing":
            "**फवारणीची वेळ:** शांत हवामानात सकाळी किंवा उशिरा दुपारी फवारणी करा. "
            "दुपारच्या तीव्र उन्हात फवारणी टाळा आणि पानांच्या खालच्या बाजूसही "
            "समान फवारणी करा.",

        "safety":
            "**सुरक्षितता:** मास्क आणि हातमोजे वापरा. काढणीपूर्वीचा "
            "7-10 दिवसांचा कालावधी (PHI) पाळा.",

        "urgency":
            "**तातडी:** {value}.",

        "general_chemical":
            "🧪 **सामान्य बुरशीनाशक मार्गदर्शक:**",

        "contact":
            "**संपर्क बुरशीनाशके (प्रतिबंधात्मक):** Mancozeb 75% WP @ 2.5g/L किंवा "
            "Copper Oxychloride 50% WP @ 2.5g/L.",

        "systemic":
            "**सिस्टमिक बुरशीनाशके (उपचारात्मक):** Azoxystrobin + Difenoconazole @ 1ml/L "
            "किंवा ब्लाइटसाठी Ridomil Gold @ 2.5g/L.",

        "mixing":
            "नेहमी पिकासाठी दिलेले अधिकृत लेबल तपासा आणि एकमेकांशी विसंगत "
            "रसायने मिसळणे टाळा.",

        "diagnosis":
            "🔍 **{crop} — {disease} साठी Crop Doctor निदान:**",

        "symptoms":
            "**लक्षणे:** {value}",

        "action":
            "**शिफारस केलेली कृती:** {value}",

        "prevention":
            "**प्रतिबंध:** {value}",

        "general_title":
            "🌱 **Crop Doctor चा सल्ला:**",

        "general_body":
            "अधिक अचूक उपायासाठी आपल्या पानाचा फोटो स्कॅनरमध्ये अपलोड करा "
            "किंवा आपले पीक (Tomato, Potato, Corn, Apple, Rice, Grape) आणि "
            "दिसणारी लक्षणे जसे पिवळे डाग, पांढरी पावडर, पाने कोमेजणे किंवा "
            "पाने वाकणे याबद्दल माहिती द्या.",

        "q1":
            "Early Blight साठी Mancozeb चे प्रमाण किती आहे?",

        "q2":
            "सेंद्रिय कडुनिंब तेलाची फवारणी कशी तयार करावी?",

        "q3":
            "टोमॅटोमधील Leaf Curl Virus वर उपचार कसा करावा?",

        "q4":
            "पानांच्या खाली पांढरी बुरशी का दिसते?",
    },
}


def T(lang: str, key: str, **kwargs) -> str:
    """Return translated response text."""
    lang = normalize_language(lang)

    template = TEXT.get(lang, TEXT["en"]).get(
        key,
        TEXT["en"].get(key, "")
    )

    return template.format(**kwargs)


# ============================================================
# DATABASE CONTEXT
# ============================================================

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

        if (
            d_name in query_lower
            or any(
                word in d_name
                for word in query_lower.split()
                if len(word) > 3
            )
        ):
            score += 4

        if any(
            term in desc
            for term in [
                "fungal",
                "bacterial",
                "blight",
                "rust",
                "spot",
                "yellow",
                "curl",
            ]
            if term in query_lower
        ):
            score += 2

        if score > 0:
            matched.append((score, d))

    matched.sort(key=lambda x: x[0], reverse=True)

    return [item[1] for item in matched[:3]]


def get_localized_context(
    context: Dict[str, Any],
    lang: str
) -> Dict[str, Any]:
    """
    Try to obtain translated database recommendation data.

    If a translation is unavailable, retain the original
    database context.
    """

    lang = normalize_language(lang)

    if lang == "en":
        return context

    crop = (
        context.get("crop_name")
        or context.get("crop")
        or ""
    )

    disease = (
        context.get("name")
        or context.get("disease")
        or ""
    )

    if not crop or not disease:
        return context

    try:
        translated = get_recommendation(
            crop,
            disease,
            lang=lang
        )

        if translated and translated.get("found"):
            merged = dict(context)

            if translated.get("disease"):
                merged["name"] = translated["disease"]

            if translated.get("crop"):
                merged["crop_name"] = translated["crop"]

            if translated.get("recommended_action"):
                merged["recommended_action"] = translated[
                    "recommended_action"
                ]

            if translated.get("prevention_tips"):
                merged["prevention_tips"] = translated[
                    "prevention_tips"
                ]

            if translated.get("organic_control"):
                merged["organic_control"] = translated[
                    "organic_control"
                ]

            if translated.get("chemical_control"):
                merged["chemical_control"] = translated[
                    "chemical_control"
                ]

            if translated.get("urgency"):
                merged["urgency"] = translated["urgency"]

            return merged

    except Exception as e:
        print(
            f"[Crop Doctor] Translation lookup warning: {e}"
        )

    return context



# ============================================================
# DETAILED RESPONSE HELPERS
# ============================================================

def _value(data: Dict[str, Any], *keys: str, default: str = "") -> str:
    """Return the first non-empty value from a context dictionary."""
    for key in keys:
        value = data.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _detailed_disease_response(top: Dict[str, Any], lang: str) -> str:
    """
    Build a detailed farmer-friendly answer whenever a relevant
    disease/crop record is available.

    The response stays grounded in the database fields. Missing
    fields are not invented; the farmer is directed to provide
    additional crop/symptom information when necessary.
    """
    crop = _value(top, "crop_name", "crop", default="Crop")
    disease = _value(top, "name", "disease", default="Disease")

    symptoms = _value(
        top,
        "description",
        "symptoms",
        default="The available knowledge base does not contain a detailed symptom description."
    )

    action = _value(
        top,
        "recommended_action",
        "action",
        default="Follow the crop-specific management guidance available in the knowledge base."
    )

    prevention = _value(
        top,
        "prevention_tips",
        "prevention",
        default="Maintain good field hygiene, monitor the crop regularly, and follow crop-specific preventive practices."
    )

    organic = _value(
        top,
        "organic_control",
        "organic_remedy",
        default="No specific organic treatment is available in the current knowledge-base record."
    )

    chemical = _value(
        top,
        "chemical_control",
        "chemical_remedy",
        default="No specific chemical recommendation is available in the current knowledge-base record."
    )

    urgency = _value(
        top,
        "urgency",
        default="Monitor the crop closely and act according to the crop-specific recommendation."
    )

    return (
        T(lang, "diagnosis", crop=crop, disease=disease)
        + "\n\n"
        + "📌 **1. " + (
            "Disease / Problem" if lang == "en"
            else "रोग / समस्या" if lang == "hi"
            else "रोग / समस्या"
        ) + ":** "
        + disease

        + "\n\n"
        + "🔎 **2. " + (
            "Symptoms & Identification" if lang == "en"
            else "लक्षण आणि ओळख" if lang == "mr"
            else "लक्षण और पहचान"
        ) + ":** "
        + symptoms

        + "\n\n"
        + "🩺 **3. " + (
            "What to do now" if lang == "en"
            else "आता काय करावे" if lang == "mr"
            else "अभी क्या करें"
        ) + ":** "
        + action

        + "\n\n"
        + "🌿 **4. " + (
            "Organic / Bio Management" if lang == "en"
            else "सेंद्रिय / जैविक व्यवस्थापन" if lang == "mr"
            else "जैविक / प्राकृतिक प्रबंधन"
        ) + ":** "
        + organic

        + "\n\n"
        + "🧪 **5. " + (
            "Chemical Management" if lang == "en"
            else "रासायनिक व्यवस्थापन" if lang == "mr"
            else "रासायनिक प्रबंधन"
        ) + ":** "
        + chemical

        + "\n\n"
        + "🛡️ **6. " + (
            "Prevention" if lang == "en"
            else "प्रतिबंध" if lang == "mr"
            else "रोकथाम"
        ) + ":** "
        + prevention

        + "\n\n"
        + "⚠️ **7. " + (
            "Urgency / Monitoring" if lang == "en"
            else "तातडी / निरीक्षण" if lang == "mr"
            else "तात्कालिकता / निगरानी"
        ) + ":** "
        + urgency

        + "\n\n"
        + "📷 **8. " + (
            "Next step" if lang == "en"
            else "पुढील पाऊल" if lang == "mr"
            else "अगला कदम"
        ) + ":** "
        + (
            "If symptoms are changing or spreading, upload a fresh leaf photo for another AI diagnosis and compare it with the previous scan."
            if lang == "en"
            else
            "लक्षणे बदलत असतील किंवा पसरत असतील तर नवीन पानाचा फोटो अपलोड करून पुन्हा AI निदान करा आणि मागील स्कॅनशी तुलना करा."
            if lang == "mr"
            else
            "यदि लक्षण बदल रहे हैं या फैल रहे हैं, तो पत्ती की नई फोटो अपलोड करके दोबारा AI निदान करें और पिछले स्कैन से तुलना करें।"
        )
    )


def _detailed_general_response(query: str, crop_hint: str, lang: str) -> str:
    """
    Detailed fallback for crop-related questions when no disease
    record matched. It does not invent a disease diagnosis.
    """
    crop = crop_hint or (
        "your crop" if lang == "en"
        else "आपले पीक" if lang == "mr"
        else "आपकी फसल"
    )

    if lang == "mr":
        return (
            f"🌱 **Crop Doctor — {crop} साठी मार्गदर्शन**\n\n"
            f"तुमचा प्रश्न: **{query}**\n\n"
            "मी या प्रश्नासाठी उपलब्ध रोग/शिफारस नोंदी तपासल्या, परंतु या प्रश्नाशी "
            "थेट जुळणारी विशिष्ट नोंद सापडली नाही.\n\n"
            "👨‍🌾 **अचूक सल्ल्यासाठी पुढील माहिती द्या:**\n"
            "• पिकाचे नाव आणि वाढीचा टप्पा\n"
            "• पानांवर/खोडावर/फळांवर दिसणारी लक्षणे\n"
            "• लक्षणे कधीपासून आहेत आणि किती क्षेत्रात आहेत\n"
            "• पाणी देण्याची पद्धत आणि अलीकडील हवामान\n"
            "• अलीकडे वापरलेले खत किंवा फवारणी\n\n"
            "📷 शक्य असल्यास पानाचा स्पष्ट फोटो अपलोड करा. त्यामुळे Crop Doctor "
            "लक्षणांवर आधारित अधिक विशिष्ट उत्तर देऊ शकतो."
        )

    if lang == "hi":
        return (
            f"🌱 **Crop Doctor — {crop} के लिए मार्गदर्शन**\n\n"
            f"आपका प्रश्न: **{query}**\n\n"
            "मैंने उपलब्ध रोग और सिफारिश संबंधी जानकारी देखी, लेकिन इस प्रश्न से "
            "सीधे मेल खाने वाली विशिष्ट जानकारी नहीं मिली।\n\n"
            "👨‍🌾 **सटीक सलाह के लिए बताएं:**\n"
            "• फसल का नाम और उसकी वर्तमान अवस्था\n"
            "• पत्तियों/तने/फलों पर दिखाई देने वाले लक्षण\n"
            "• लक्षण कब से हैं और कितने क्षेत्र में हैं\n"
            "• सिंचाई की पद्धति और हाल का मौसम\n"
            "• हाल में इस्तेमाल किया गया खाद या स्प्रे\n\n"
            "📷 संभव हो तो पत्ती की स्पष्ट फोटो अपलोड करें। इससे Crop Doctor "
            "लक्षणों के आधार पर अधिक विशिष्ट उत्तर दे सकेगा।"
        )

    return (
        f"🌱 **Crop Doctor — Guidance for {crop}**\n\n"
        f"Your question: **{query}**\n\n"
        "I checked the available disease and recommendation knowledge, but "
        "there is no directly matching specific record for this question.\n\n"
        "👨‍🌾 **For a more accurate answer, provide:**\n"
        "• Crop name and current growth stage\n"
        "• Symptoms on leaves, stem, flowers, or fruit\n"
        "• When the symptoms started and how much of the field is affected\n"
        "• Irrigation method and recent weather\n"
        "• Fertilizer or spray used recently\n\n"
        "📷 If possible, upload a clear leaf photo. Crop Doctor can then give "
        "more specific symptom-based guidance."
    )


# ============================================================
# MAIN CROP DOCTOR
# ============================================================

def ask_crop_doctor(
    query: str,
    crop_hint: str = None,
    disease_hint: str = None,
    lang: str = "en"
) -> Dict[str, Any]:

    lang = normalize_language(lang)

    query_clean = query.strip()

    # --------------------------------------------------------
    # EMPTY QUESTION
    # --------------------------------------------------------

    if not query_clean:
        return {
            "answer": T(lang, "hello"),
            "sources": [],
            "language": lang,
            "language_name": LANG_NAMES[lang],
            "suggested_questions": [
                T(lang, "q1"),
                T(lang, "q2"),
                T(lang, "q3"),
                T(lang, "q4"),
            ],
        }

    # --------------------------------------------------------
    # CONTEXT RETRIEVAL
    # --------------------------------------------------------

    contexts = retrieve_disease_context(query_clean)

    if crop_hint and disease_hint:

        direct = get_recommendation(
            crop_hint,
            disease_hint,
            lang=lang
        )

        if direct.get("found"):
            contexts.insert(0, direct)

    if contexts:
        contexts = [
            get_localized_context(c, lang)
            for c in contexts
        ]

    q_low = query_clean.lower()
    sources = []

    # ========================================================
    # 1. ORGANIC REMEDY
    # ========================================================

    if any(
        k in q_low
        for k in [
            "organic",
            "natural",
            "neem",
            "home remedy",
            "biocontrol",
            "bio",
        ]
    ):

        if contexts:

            top = contexts[0]

            crop_n = (
                top.get("crop_name")
                or top.get("crop")
                or "your crop"
            )

            d_n = (
                top.get("name")
                or top.get("disease")
                or "disease"
            )

            org = (
                top.get("organic_control")
                or "Spray neem oil (5ml/L) or Trichoderma bio-fungicide."
            )

            prev = (
                top.get("prevention_tips")
                or "Ensure good drainage and air circulation."
            )

            sources.append(
                f"{crop_n} - {d_n}"
            )

            answer = (
                T(
                    lang,
                    "organic_title",
                    crop=crop_n,
                    disease=d_n
                )
                + "\n\n1. "
                + T(lang, "bio", value=org)
                + "\n2. "
                + T(lang, "cultural", value=prev)
                + "\n3. "
                + T(lang, "prophylactic")
            )

        else:

            answer = (
                T(lang, "general_organic")
                + "\n\n1. "
                + T(lang, "neem")
                + "\n2. "
                + T(lang, "biofungicide")
                + "\n3. "
                + T(lang, "airflow")
            )

    # ========================================================
    # 2. CHEMICAL / DOSAGE
    # ========================================================

    elif any(
        k in q_low
        for k in [
            "chemical",
            "spray",
            "dose",
            "dosage",
            "fungicide",
            "pesticide",
            "medicine",
            "mancozeb",
        ]
    ):

        if contexts:

            top = contexts[0]

            crop_n = (
                top.get("crop_name")
                or top.get("crop")
                or "crop"
            )

            d_n = (
                top.get("name")
                or top.get("disease")
                or "disease"
            )

            chem = (
                top.get("chemical_control")
                or "Apply standard Mancozeb 75% WP @ 2.5g/L."
            )

            urg = (
                top.get("urgency")
                or "Act within 3 days"
            )

            sources.append(
                f"{crop_n} - {d_n}"
            )

            answer = (
                T(
                    lang,
                    "chemical_title",
                    crop=crop_n,
                    disease=d_n
                )
                + "\n\n- "
                + T(lang, "active", value=chem)
                + "\n- "
                + T(lang, "timing")
                + "\n- "
                + T(lang, "safety")
                + "\n- "
                + T(lang, "urgency", value=urg)
            )

        else:

            answer = (
                T(lang, "general_chemical")
                + "\n\n1. "
                + T(lang, "contact")
                + "\n2. "
                + T(lang, "systemic")
                + "\n3. "
                + T(lang, "mixing")
            )

    # ========================================================
    # 3. SPECIFIC DISEASE / SYMPTOM
    # ========================================================

    elif contexts:

        top = contexts[0]

        crop_n = (
            top.get("crop_name")
            or top.get("crop")
            or "Crop"
        )

        d_n = (
            top.get("name")
            or top.get("disease")
            or "Disease"
        )

        desc = top.get(
            "description",
            ""
        )

        action = top.get(
            "recommended_action",
            ""
        )

        prev = top.get(
            "prevention_tips",
            ""
        )

        sources.append(
            f"{crop_n} - {d_n}"
        )

        answer = _detailed_disease_response(top, lang)

    # ========================================================
    # 4. GENERAL AGRICULTURE ADVICE
    # ========================================================

    else:

        answer = _detailed_general_response(
            query_clean,
            crop_hint,
            lang
        )

    suggested = [
        T(lang, "q1"),
        T(lang, "q2"),
        T(lang, "q3"),
        T(lang, "q4"),
    ]

    return {
        "query": query_clean,
        "answer": answer,
        "sources": sources,
        "language": lang,
        "language_name": LANG_NAMES[lang],
        "suggested_questions": suggested,
    }
