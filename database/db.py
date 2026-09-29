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
    Safe agronomic recommendation lookup.

    Only an exact crop + disease record is accepted.
    We intentionally do NOT fall back to:
      - another disease with a similar keyword,
      - another disease of the same crop,
      - the first disease in a crop.

    This prevents an AI prediction from receiving advice for a different
    disease when the exact database record is unavailable.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_crop = str(crop or "").strip()
    clean_disease = str(disease or "").strip()
    clean_lang = str(lang or "en").strip().lower()

    query = """
        SELECT
            d.*,
            c.name AS crop_name,
            c.icon AS crop_icon,
            t.name AS trans_name,
            t.recommended_action AS trans_action,
            t.prevention_tips AS trans_prev,
            t.organic_control AS trans_org,
            t.chemical_control AS trans_chem,
            t.urgency AS trans_urgency
        FROM diseases d
        JOIN crops c ON d.crop_id = c.id
        LEFT JOIN translations t
          ON d.id = t.disease_id AND LOWER(t.lang_code) = LOWER(?)
        WHERE LOWER(TRIM(c.name)) = LOWER(TRIM(?))
          AND LOWER(TRIM(d.name)) = LOWER(TRIM(?))
        LIMIT 1
    """

    cursor.execute(
        query,
        (clean_lang, clean_crop, clean_disease)
    )
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
            "description": (
                f"No exact advisory is stored for "
                f"{clean_crop} - {clean_disease}."
            ),
            "recommended_action": "",
            "prevention_tips": "",
            "organic_control": "",
            "chemical_control": "",
            "urgency": "Confirm diagnosis",
            "severity_notes": (
                "Do not use a different disease's treatment. "
                "Confirm the diagnosis with a qualified agricultural "
                "expert or a validated disease reference."
            ),
            "language": clean_lang,
        }

    use_trans = bool(
        clean_lang != "en" and row["trans_action"]
    )

    return {
        "found": True,
        "crop": row["crop_name"],
        "crop_icon": row["crop_icon"],
        "disease": (
            row["trans_name"]
            if use_trans and row["trans_name"]
            else row["name"]
        ),
        "original_disease": row["name"],
        "pathogen_type": row["pathogen_type"],
        "description": row["description"],
        "recommended_action": (
            row["trans_action"]
            if use_trans
            else row["recommended_action"]
        ),
        "prevention_tips": (
            row["trans_prev"]
            if use_trans
            else row["prevention_tips"]
        ),
        "organic_control": (
            row["trans_org"]
            if use_trans
            else row["organic_control"]
        ),
        "chemical_control": (
            row["trans_chem"]
            if use_trans
            else row["chemical_control"]
        ),
        "urgency": (
            row["trans_urgency"]
            if use_trans and row["trans_urgency"]
            else row["urgency"]
        ),
        "severity_notes": row["severity_notes"],
        "language": clean_lang,
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



def _severity_rank(severity: str) -> int:
    levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return levels.get(str(severity or "").strip().lower(), 0)


def _calculate_progress(previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    prev_area = float(previous.get("affected_area_pct") or 0)
    curr_area = float(current.get("affected_area_pct") or 0)
    area_change = round(curr_area - prev_area, 2)
    severity_change = _severity_rank(current.get("severity")) - _severity_rank(previous.get("severity"))
    if area_change <= -5:
        status, label, reason = "improving", "🟢 Improving", f"Affected area decreased by {abs(area_change):.1f}%."
    elif area_change >= 5:
        status, label, reason = "worsening", "🔴 Worsening", f"Affected area increased by {area_change:.1f}%."
    elif severity_change < 0:
        status, label, reason = "improving", "🟢 Improving", "Disease severity has decreased."
    elif severity_change > 0:
        status, label, reason = "worsening", "🔴 Worsening", "Disease severity has increased."
    else:
        status, label, reason = "stable", "🟡 Stable", "No significant change was detected."
    return {"status": status, "label": label, "reason": reason, "previous_affected_area_pct": round(prev_area,2), "current_affected_area_pct": round(curr_area,2), "area_change_pct": area_change, "previous_severity": previous.get("severity"), "current_severity": current.get("severity"), "severity_change": severity_change}


def get_scan_progress(scan_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)); row = cursor.fetchone()
    if not row:
        conn.close(); return {"found": False, "status": "not_found", "message": "Scan not found."}
    current = dict(row)
    if session_id and current.get("session_id") != session_id:
        conn.close(); return {"found": False, "status": "not_found", "message": "Scan does not belong to this session."}
    cursor.execute("""SELECT * FROM scans WHERE session_id = ? AND LOWER(TRIM(crop)) = LOWER(TRIM(?)) AND LOWER(TRIM(disease)) = LOWER(TRIM(?)) AND id <> ? ORDER BY datetime(created_at) DESC, id DESC LIMIT 1""", (current.get("session_id"), current.get("crop",""), current.get("disease",""), scan_id))
    prev = cursor.fetchone(); conn.close()
    if not prev:
        return {"found": True, "status": "first_scan", "label": "🔵 First scan", "reason": "No previous scan of the same crop and disease is available for comparison.", "current": current, "previous": None}
    result = _calculate_progress(dict(prev), current)
    result.update({"found": True, "current_scan_id": current.get("id"), "previous_scan_id": prev["id"], "current_timestamp": current.get("created_at"), "previous_timestamp": prev["created_at"]})
    return result


def get_crop_disease_progress(crop: str, disease: str, session_id: str = "default_user", limit: int = 20) -> Dict[str, Any]:
    conn = get_db_connection()
    rows = conn.execute("""SELECT * FROM scans WHERE session_id = ? AND LOWER(TRIM(crop)) = LOWER(TRIM(?)) AND LOWER(TRIM(disease)) = LOWER(TRIM(?)) ORDER BY datetime(created_at) ASC, id ASC LIMIT ?""", (session_id, crop, disease, int(limit))).fetchall()
    conn.close()
    scans = [dict(r) for r in rows]; timeline = []
    for i, current in enumerate(scans):
        item = {"scan_id": current.get("id"), "created_at": current.get("created_at"), "crop": current.get("crop"), "disease": current.get("disease"), "confidence": current.get("confidence"), "severity": current.get("severity"), "affected_area_pct": current.get("affected_area_pct"), "image_name": current.get("image_name")}
        item["progress"] = {"status":"first_scan","label":"🔵 First scan","reason":"Baseline scan."} if i == 0 else _calculate_progress(scans[i-1], current)
        timeline.append(item)
    return {"found": bool(scans), "crop": crop, "disease": disease, "count": len(scans), "timeline": timeline}

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
