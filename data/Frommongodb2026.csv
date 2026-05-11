# =============================================================
# Export2026.py
# Exports all MongoDB travel_trends_2026 data to a fixed CSV.
# Every run OVERWRITES the same file: Travel_search2026.csv
# (no new files created each time)
# =============================================================

import csv
import pathlib
from datetime import datetime
from pymongo import MongoClient

# -- STEP 1: Load MongoDB URI from .env -----------------------
ENV_FILE = pathlib.Path("/workspaces/gemma-data-driven-tourism-project/.env")
MONGO_URI = None
for line in ENV_FILE.read_text().splitlines():
    line = line.strip()
    if line.startswith("MONGO_URI="):
        MONGO_URI = line[len("MONGO_URI="):]
        break

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file!")

# -- STEP 2: Connect to MongoDB -------------------------------
print("Connecting to MongoDB...")
client     = MongoClient(MONGO_URI)
db         = client["thailand_trends_db"]
collection = db["travel_trends_2026"]
print("Connected!")

# -- STEP 3: Fixed output file (always the same name) ---------
OUTPUT_FILE = pathlib.Path("/workspaces/gemma-data-driven-tourism-project/data/Travel_search2026.csv")

# -- STEP 4: Fetch all documents ------------------------------
print("Fetching documents from MongoDB...")
documents = list(collection.find({}))
print(f"   Found {len(documents)} documents")

if len(documents) == 0:
    print("No documents found. Is Travel2026.py still running?")
    client.close()
    exit()

# -- STEP 5: Overwrite CSV with latest data -------------------
CSV_HEADERS = [
    "province_en", "province_th", "keyword", "language",
    "timeframe", "geo", "fetched_at", "date", "interest",
]

total_rows = 0
print(f"Writing to: {OUTPUT_FILE.name}")

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
print(f"")
print(f"Updated: {OUTPUT_FILE.name}")
print(f"   Rows  : {total_rows:,}  ({len(documents)} MongoDB documents)")
print(f"   Size  : {file_size_kb:.1f} KB")
print(f"   Time  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
