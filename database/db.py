"""
CropGuard AI - Fixed Database Engine
SQLite initialization, migrations, CRUD queries, and seed data loader.
"""

import sqlite3
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

DB_PATH = Path(__file__).resolve().parent / "cropguard.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
SEED_DATA_PATH = Path(__file__).resolve().parent / "seed_data.json"

DB_CONNECTION_TIMEOUT = 5
DB_BUSY_TIMEOUT_MS = 5000


def _restrict_database_file_permissions():
    """Best-effort local permission hardening."""
    try:
        if DB_PATH.exists() and os.name != "nt":
            DB_PATH.chmod(0o600)
    except Exception as e:
        print(f"[DB WARN] Could not restrict DB permissions: {e}")


def _harden_db_connection(conn):
    conn.enable_load_extension(False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA secure_delete = ON;")
    conn.execute("PRAGMA trusted_schema = OFF;")
    conn.execute(f"PRAGMA busy_timeout = {DB_BUSY_TIMEOUT_MS};")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=DB_CONNECTION_TIMEOUT)
    conn.row_factory = sqlite3.Row
    _harden_db_connection(conn)
    return conn


def init_db(force_reseed: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM crops")
    crop_count = cursor.fetchone()[0]

    if crop_count == 0 or force_reseed:
        seed_database(conn)

    conn.close()
    _restrict_database_file_permissions()
    print(f"[DB] Initialized database at {DB_PATH}")


def seed_database(conn):
    if not SEED_DATA_PATH.exists():
        print(f"[DB WARN] Seed data file {SEED_DATA_PATH} not found.")
        return

    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()

    for item in data:
        crop_name = item["crop"]
        sci_name = item.get("scientific_name", "")
        icon = item.get("icon", "🌱")
        category = item.get("category", "Vegetable")

        cursor.execute(
            """
            INSERT OR IGNORE INTO crops (name, scientific_name, icon, category)
            VALUES (?, ?, ?, ?)
            """,
            (crop_name, sci_name, icon, category)
        )
        cursor.execute("SELECT id FROM crops WHERE name = ?", (crop_name,))
        crop_id = cursor.fetchone()["id"]

        for disease in item.get("diseases", []):
            d_name = disease["name"]
            pathogen = disease.get("pathogen_type", "Fungal")
            desc = disease.get("description", "")
            rec = disease.get("recommended_action", "")
            prev = disease.get("prevention_tips", "")
            org = disease.get("organic_control", "")
            chem = disease.get("chemical_control", "")
            urg = disease.get("urgency", "Act within 3 days")
            sev_notes = disease.get("severity_notes", "")

            cursor.execute("SELECT id FROM diseases WHERE crop_id = ? AND name = ?", (crop_id, d_name))
            row = cursor.fetchone()
            if row:
                disease_id = row["id"]
                cursor.execute(
                    """
                    UPDATE diseases SET
                        pathogen_type = ?, description = ?, recommended_action = ?,
                        prevention_tips = ?, organic_control = ?, chemical_control = ?,
                        urgency = ?, severity_notes = ?
                    WHERE id = ?
                    """,
                    (pathogen, desc, rec, prev, org, chem, urg, sev_notes, disease_id)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO diseases
                    (crop_id, name, pathogen_type, description, recommended_action,
                     prevention_tips, organic_control, chemical_control, urgency,
                     severity_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (crop_id, d_name, pathogen, desc, rec, prev, org, chem, urg, sev_notes)
                )
                disease_id = cursor.lastrowid

            translations = disease.get("translations", {})
            for lang_code, trans in translations.items():
                t_name = trans.get("name", d_name)
                t_rec = trans.get("recommended_action", rec)
                t_prev = trans.get("prevention_tips", prev)
                t_org = trans.get("organic_control", org)
                t_chem = trans.get("chemical_control", chem)
                t_urg = trans.get("urgency", urg)

                cursor.execute(
                    "SELECT id FROM translations WHERE disease_id = ? AND lang_code = ?",
                    (disease_id, lang_code)
                )
                t_row = cursor.fetchone()
                if t_row:
                    cursor.execute(
                        """
                        UPDATE translations SET
                            name = ?, recommended_action = ?, prevention_tips = ?,
                            organic_control = ?, chemical_control = ?, urgency = ?
                        WHERE id = ?
                        """,
                        (t_name, t_rec, t_prev, t_org, t_chem, t_urg, t_row["id"])
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO translations
                        (disease_id, lang_code, name, recommended_action,
                         prevention_tips, organic_control, chemical_control, urgency)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (disease_id, lang_code, t_name, t_rec, t_prev, t_org, t_chem, t_urg)
                    )

    conn.commit()
    print("[DB] Successfully seeded crops, diseases, and translations.")


def get_recommendation(crop: str, disease: str, lang: str = "en") -> Dict[str, Any]:
    """
    Intelligent agronomic recommendation lookup:
    1. Exact crop + disease lookup
    2. Normalized & fuzzy crop + disease lookup (strips parentheses, aliases, plurals)
    3. Keyword-level disease match for the identified crop
    4. Crop fallback if specific disease name variant is uncataloged
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_crop = str(crop).strip()
    clean_disease = str(disease).strip()

    # Normalization helpers
    crop_base = re.sub(r"\(.*?\)", "", clean_crop).strip().lower()
    crop_singular = crop_base[:-1] if (crop_base.endswith("s") and not crop_base.endswith("ss")) else crop_base
    disease_base = re.sub(r"\(.*?\)", "", clean_disease).strip().lower()

    # Step 1: Exact match
    query_exact = """
        SELECT d.*, c.name AS crop_name, c.icon AS crop_icon,
               t.name AS trans_name, t.recommended_action AS trans_action,
               t.prevention_tips AS trans_prev, t.organic_control AS trans_org,
               t.chemical_control AS trans_chem, t.urgency AS trans_urgency
        FROM diseases d
        JOIN crops c ON d.crop_id = c.id
        LEFT JOIN translations t
          ON d.id = t.disease_id AND t.lang_code = ?
        WHERE LOWER(c.name) = LOWER(?)
          AND LOWER(d.name) = LOWER(?)
        LIMIT 1
    """
    cursor.execute(query_exact, (lang, clean_crop, clean_disease))
    row = cursor.fetchone()

    # Step 2: Fuzzy / alias match (handling e.g. "Sugarcane" + "Red Root" -> "Red Root (Red Rot)", "Grape" vs "Grapes")
    if not row:
        query_fuzzy = """
            SELECT d.*, c.name AS crop_name, c.icon AS crop_icon,
                   t.name AS trans_name, t.recommended_action AS trans_action,
                   t.prevention_tips AS trans_prev, t.organic_control AS trans_org,
                   t.chemical_control AS trans_chem, t.urgency AS trans_urgency
            FROM diseases d
            JOIN crops c ON d.crop_id = c.id
            LEFT JOIN translations t
              ON d.id = t.disease_id AND t.lang_code = ?
            WHERE (
                LOWER(c.name) LIKE ? OR ? LIKE '%' || LOWER(c.name) || '%'
                OR LOWER(c.name) LIKE ? OR ? LIKE '%' || LOWER(c.name) || '%'
            )
            AND (
                LOWER(d.name) LIKE ? OR ? LIKE '%' || LOWER(d.name) || '%'
                OR LOWER(d.name) LIKE ? OR ? LIKE '%' || LOWER(d.name) || '%'
            )
            LIMIT 1
        """
        cursor.execute(
            query_fuzzy,
            (
                lang,
                f"%{crop_base}%", crop_base,
                f"%{crop_singular}%", crop_singular,
                f"%{clean_disease}%", clean_disease,
                f"%{disease_base}%", disease_base,
            )
        )
        row = cursor.fetchone()

    # Step 3: Disease-keyword match on crop (e.g. "rust", "smut", "blight", "wilt", "rot")
    if not row:
        disease_words = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", clean_disease.lower()) if w not in {"leaf", "spot"}]
        for word in disease_words:
            query_word = """
                SELECT d.*, c.name AS crop_name, c.icon AS crop_icon,
                       t.name AS trans_name, t.recommended_action AS trans_action,
                       t.prevention_tips AS trans_prev, t.organic_control AS trans_org,
                       t.chemical_control AS trans_chem, t.urgency AS trans_urgency
                FROM diseases d
                JOIN crops c ON d.crop_id = c.id
                LEFT JOIN translations t
                  ON d.id = t.disease_id AND t.lang_code = ?
                WHERE (LOWER(c.name) LIKE ? OR ? LIKE '%' || LOWER(c.name) || '%')
                  AND LOWER(d.name) LIKE ?
                LIMIT 1
            """
            cursor.execute(query_word, (lang, f"%{crop_base}%", crop_base, f"%{word}%"))
            row = cursor.fetchone()
            if row:
                break

    # Step 4: Crop fallback (return first disease of this crop if disease is generic like "Leaf Disease")
    if not row:
        query_crop_fallback = """
            SELECT d.*, c.name AS crop_name, c.icon AS crop_icon,
                   t.name AS trans_name, t.recommended_action AS trans_action,
                   t.prevention_tips AS trans_prev, t.organic_control AS trans_org,
                   t.chemical_control AS trans_chem, t.urgency AS trans_urgency
            FROM diseases d
            JOIN crops c ON d.crop_id = c.id
            LEFT JOIN translations t
              ON d.id = t.disease_id AND t.lang_code = ?
            WHERE LOWER(c.name) LIKE ? OR ? LIKE '%' || LOWER(c.name) || '%'
            LIMIT 1
        """
        cursor.execute(query_crop_fallback, (lang, f"%{crop_base}%", crop_base))
        row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "found": False,
            "crop": clean_crop,
            "crop_icon": "🌱",
            "disease": clean_disease,
            "original_disease": clean_disease,
            "pathogen_type": "Unknown",
            "description": f"Agronomic advisory for {clean_crop} - {clean_disease} is being cataloged by our plant pathologists.",
            "recommended_action": f"Carefully inspect {clean_crop} for lesion progression. Prune severely spotted leaves and maintain clean tools.",
            "prevention_tips": "Ensure balanced irrigation, adequate spacing between plants, and avoid overnight foliage moisture.",
            "organic_control": "Apply cold-pressed neem oil (5ml/L) with liquid soap weekly as broad preventive care.",
            "chemical_control": "Consult your regional Krishi Vigyan Kendra (KVK) or extension officer for registered chemicals.",
            "urgency": "Act within 2-3 days",
            "severity_notes": "Monitor spread daily.",
            "language": lang,
        }

    use_trans = bool(lang != "en" and row["trans_action"])

    return {
        "found": True,
        "crop": row["crop_name"],
        "crop_icon": row["crop_icon"],
        "disease": row["trans_name"] if use_trans and row["trans_name"] else row["name"],
        "original_disease": row["name"],
        "pathogen_type": row["pathogen_type"],
        "description": row["description"],
        "recommended_action": row["trans_action"] if use_trans else row["recommended_action"],
        "prevention_tips": row["trans_prev"] if use_trans else row["prevention_tips"],
        "organic_control": row["trans_org"] if use_trans else row["organic_control"],
        "chemical_control": row["trans_chem"] if use_trans else row["chemical_control"],
        "urgency": row["trans_urgency"] if use_trans and row["trans_urgency"] else row["urgency"],
        "severity_notes": row["severity_notes"],
        "language": lang,
    }


def save_scan(
    crop: str,
    disease: str,
    confidence: float,
    severity: str,
    affected_area_pct: float,
    recommendation: str,
    urgency: str = "Act within 3 days",
    lang: str = "en",
    session_id: str = "default_user",
    image_name: Optional[str] = None,
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scans
        (session_id, crop, disease, confidence, severity, affected_area_pct,
         recommendation, urgency, lang, image_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id, crop, disease, float(confidence), severity,
            float(affected_area_pct), recommendation, urgency, lang, image_name
        )
    )
    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def get_scan_history(limit: int = 50, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    if session_id:
        cursor.execute(
            "SELECT * FROM scans WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM scans ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_crops() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM crops ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_diseases(crop_name: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()

    if crop_name:
        rows = conn.execute(
            """
            SELECT d.*, c.name AS crop_name, c.icon AS crop_icon
            FROM diseases d
            JOIN crops c ON d.crop_id = c.id
            WHERE LOWER(c.name) = LOWER(?)
            ORDER BY d.name ASC
            """,
            (crop_name,)
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT d.*, c.name AS crop_name, c.icon AS crop_icon
            FROM diseases d
            JOIN crops c ON d.crop_id = c.id
            ORDER BY c.name, d.name ASC
            """
        ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db(force_reseed=True)
    print(json.dumps(
        get_recommendation("Tomato", "Early Blight", lang="en"),
        indent=2,
        ensure_ascii=False
    ))
