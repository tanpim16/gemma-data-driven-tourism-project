# =============================================================
# Export2026.py (Updated to use secrets.toml)
# Exports all MongoDB travel_trends_2026 data to a fixed CSV.
# Every run OVERWRITES the same file: Travel_search2026.csv
# =============================================================

import os
import csv
import pathlib
import tomllib
from datetime import datetime
from pymongo import MongoClient

# -- STEP 1: Load MongoDB URI from secrets.toml ---------------
BASE_DIR = pathlib.Path("/workspaces/gemma-data-driven-tourism-project")
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"

MONGO_URI = os.getenv("MONGO_URI") 

if not MONGO_URI and SECRETS_FILE.exists():
    with open(SECRETS_FILE, "rb") as f:
        try:
            secrets = tomllib.load(f)
            # ค้นหาในระดับหลัก
            MONGO_URI = secrets.get("MONGO_URI")
            
            # ถ้าไม่เจอ ค้นหาในหมวดหมู่ย่อย
            if not MONGO_URI:
                for section_name, section_content in secrets.items():
                    if isinstance(section_content, dict) and "MONGO_URI" in section_content:
                        MONGO_URI = section_content.get("MONGO_URI")
                        break
        except Exception as e:
            raise SystemExit(f"❌ Error reading secrets.toml: {e}")

if not MONGO_URI:
    raise SystemExit("❌ FATAL ERROR: MONGO_URI not found in secrets.toml or Environment Variables.")

# -- STEP 2: Connect to MongoDB -------------------------------
print("🔌 Connecting to MongoDB...")
client     = MongoClient(MONGO_URI)
db         = client["thailand_trends_db"]
collection = db["travel_trends_2026"]
print("✅ Connected!")

# -- STEP 3: Fixed output file (always the same name) ---------
OUTPUT_FILE = BASE_DIR / "data" / "Travel_search2026.csv"

# -- STEP 4: Fetch all documents ------------------------------
print("📥 Fetching documents from MongoDB...")
documents = list(collection.find({}))
print(f"   Found {len(documents)} documents")

if len(documents) == 0:
    print("⚠️ No documents found. Is Travel2026.py still running?")
    client.close()
    exit()

# -- STEP 5: Overwrite CSV with latest data -------------------
CSV_HEADERS = [
    "province_en", "province_th", "keyword", "language",
    "timeframe", "geo", "fetched_at", "date", "interest",
]

total_rows = 0
print(f"📝 Writing to: {OUTPUT_FILE.name}")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
    writer.writeheader()
    for doc in documents:
        for point in doc.get("data_points", []):
            writer.writerow({
                "province_en": doc.get("province_en", ""),
                "province_th": doc.get("province_th", ""),
                "keyword":     doc.get("keyword", ""),
                "language":    doc.get("language", ""),
                "timeframe":   doc.get("timeframe", ""),
                "geo":         doc.get("geo", ""),
                "fetched_at":  doc.get("fetched_at", ""),
                "date":        point.get("date", ""),
                "interest":    point.get("interest", 0),
            })
            total_rows += 1

client.close()
file_size_kb = OUTPUT_FILE.stat().st_size / 1024
print("")
print(f"🎉 Updated: {OUTPUT_FILE.name}")
print(f"   Rows  : {total_rows:,}  ({len(documents)} MongoDB documents)")
print(f"   Size  : {file_size_kb:.1f} KB")
print(f"   Time  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")