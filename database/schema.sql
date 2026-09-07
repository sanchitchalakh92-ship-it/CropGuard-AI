-- CropGuard AI Database Schema
-- SQLite schema for crops, diseases, multilingual translations, and user scan logs

CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    scientific_name TEXT,
    category TEXT DEFAULT 'Vegetable',
    icon TEXT DEFAULT '🌱'
);

CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    pathogen_type TEXT DEFAULT 'Fungal', -- Fungal, Bacterial, Viral, Pest, Physiological
    description TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    prevention_tips TEXT NOT NULL,
    organic_control TEXT,
    chemical_control TEXT,
    urgency TEXT DEFAULT 'Act within 3 days',
    severity_notes TEXT,
    FOREIGN KEY (crop_id) REFERENCES crops(id),
    UNIQUE (crop_id, name)
);

CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id INTEGER NOT NULL,
    lang_code TEXT NOT NULL, -- 'en', 'hi', 'mr', 'es', 'te'
    name TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    prevention_tips TEXT NOT NULL,
    organic_control TEXT,
    chemical_control TEXT,
    urgency TEXT,
    FOREIGN KEY (disease_id) REFERENCES diseases(id),
    UNIQUE (disease_id, lang_code)
);

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT DEFAULT 'default_user',
    crop TEXT NOT NULL,
    disease TEXT NOT NULL,
    confidence REAL NOT NULL,
    severity TEXT NOT NULL, -- Low, Medium, High, Healthy
    affected_area_pct REAL DEFAULT 0.0,
    recommendation TEXT NOT NULL,
    urgency TEXT,
    lang TEXT DEFAULT 'en',
    image_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_diseases_crop_id ON diseases(crop_id);
CREATE INDEX IF NOT EXISTS idx_translations_disease_lang ON translations(disease_id, lang_code);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
