import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "ml-model"))
sys.path.insert(0, str(ROOT / "database"))

from predict import CLASS_MAP, parse_class_name
from recommendations import DISEASE_ADVISORIES

print("Model class mappings:", len(CLASS_MAP))
print("Disease-specific advisories:", len(DISEASE_ADVISORIES))

missing = []
for raw_class, (crop, disease) in CLASS_MAP.items():
    if f"{crop}|{disease}" not in DISEASE_ADVISORIES:
        missing.append((raw_class, crop, disease))

if missing:
    print("\nMISSING ADVISORIES:")
    for item in missing:
        print(item)
    raise SystemExit(1)

print("\nPASS: every model class has a disease-specific advisory.")

for raw in [
    "Cabbage_Alternaria_Leaf_Spot",
    "Wheat_stripe_rust",
    "Tomato_Spectoria_Leaf_Spot",
    "Sugarcane_Red_root",
    "maize_commonrust",
]:
    print(f"{raw} -> {parse_class_name(raw)}")
