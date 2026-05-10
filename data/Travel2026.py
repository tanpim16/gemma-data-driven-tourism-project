# =============================================================
# Travel2026.py
# Goal: Fetch Google Trends data for all 77 Thai provinces
#       and save it into a MongoDB database.
#
# KEYWORDS searched:
#   - English : "Travel <province>"   e.g. "Travel Bangkok"
#   - Thai    : "เที่ยว <province>"   e.g. "เที่ยว กรุงเทพ"
#
# DATE RANGE: 1 Jan 2026 – 30 Apr 2026
# REGION: Thailand (TH)
#
# HOW IT AVOIDS GOOGLE RATE LIMITS:
#   - We fetch one province at a time (not all 77 at once)
#   - We add a random sleep of 3-8 seconds between each request
#   - If Google blocks us (429 error), we wait 60 seconds and retry
# =============================================================

# ── STEP 0 : Import libraries ────────────────────────────────
import os
import time
import random
from datetime import datetime

import pathlib
from pytrends.request import TrendReq
from pymongo import MongoClient

# ── STEP 1 : Load .env file (contains your MongoDB password) ─
# Read .env manually (avoids issues with special chars like &)
ENV_FILE = pathlib.Path("/workspaces/gemma-data-driven-tourism-project/.env")
for _line in ENV_FILE.read_text().splitlines():
    if _line.startswith("MONGO_URI="):
        os.environ["MONGO_URI"] = _line[len("MONGO_URI="):]
        break
MONGO_URI = os.getenv("MONGO_URI")

# ── STEP 2 : Connect to MongoDB ──────────────────────────────
print("🔌 Connecting to MongoDB...")
client = MongoClient(MONGO_URI)
db          = client["thailand_trends_db"]
collection  = db["travel_trends_2026"]
print("✅ Connected!\n")

# ── STEP 3 : Setup Google Trends API ─────────────────────────
# hl='th-TH'  → use Thai language interface
# tz=-420     → Thailand timezone (UTC+7, pytrends uses -420)
pytrends = TrendReq(hl="th-TH", tz=-420)

# ── STEP 4 : All 77 Thai provinces ───────────────────────────
# Format: (English name, Thai name)
PROVINCES = [
    ("Bangkok",            "กรุงเทพมหานคร"),
    ("Samut Prakan",       "สมุทรปราการ"),
    ("Nonthaburi",         "นนทบุรี"),
    ("Pathum Thani",       "ปทุมธานี"),
    ("Phra Nakhon Si Ayutthaya", "พระนครศรีอยุธยา"),
    ("Ang Thong",          "อ่างทอง"),
    ("Lop Buri",           "ลพบุรี"),
    ("Sing Buri",          "สิงห์บุรี"),
    ("Chai Nat",           "ชัยนาท"),
    ("Saraburi",           "สระบุรี"),
    ("Chon Buri",          "ชลบุรี"),
    ("Rayong",             "ระยอง"),
    ("Chanthaburi",        "จันทบุรี"),
    ("Trat",               "ตราด"),
    ("Chachoengsao",       "ฉะเชิงเทรา"),
    ("Prachin Buri",       "ปราจีนบุรี"),
    ("Nakhon Nayok",       "นครนายก"),
    ("Sa Kaeo",            "สระแก้ว"),
    ("Nakhon Ratchasima",  "นครราชสีมา"),
    ("Buri Ram",           "บุรีรัมย์"),
    ("Surin",              "สุรินทร์"),
    ("Si Sa Ket",          "ศรีสะเกษ"),
    ("Ubon Ratchathani",   "อุบลราชธานี"),
    ("Yasothon",           "ยโสธร"),
    ("Chaiyaphum",         "ชัยภูมิ"),
    ("Amnat Charoen",      "อำนาจเจริญ"),
    ("Bueng Kan",          "บึงกาฬ"),
    ("Nong Bua Lam Phu",   "หนองบัวลำภู"),
    ("Khon Kaen",          "ขอนแก่น"),
    ("Udon Thani",         "อุดรธานี"),
    ("Loei",               "เลย"),
    ("Nong Khai",          "หนองคาย"),
    ("Maha Sarakham",      "มหาสารคาม"),
    ("Roi Et",             "ร้อยเอ็ด"),
    ("Kalasin",            "กาฬสินธุ์"),
    ("Sakon Nakhon",       "สกลนคร"),
    ("Nakhon Phanom",      "นครพนม"),
    ("Mukdahan",           "มุกดาหาร"),
    ("Chiang Mai",         "เชียงใหม่"),
    ("Lamphun",            "ลำพูน"),
    ("Lampang",            "ลำปาง"),
    ("Uttaradit",          "อุตรดิตถ์"),
    ("Phrae",              "แพร่"),
    ("Nan",                "น่าน"),
    ("Phayao",             "พะเยา"),
    ("Chiang Rai",         "เชียงราย"),
    ("Mae Hong Son",       "แม่ฮ่องสอน"),
    ("Nakhon Sawan",       "นครสวรรค์"),
    ("Uthai Thani",        "อุทัยธานี"),
    ("Kamphaeng Phet",     "กำแพงเพชร"),
    ("Tak",                "ตาก"),
    ("Sukhothai",          "สุโขทัย"),
    ("Phitsanulok",        "พิษณุโลก"),
    ("Phichit",            "พิจิตร"),
    ("Phetchabun",         "เพชรบูรณ์"),
    ("Ratchaburi",         "ราชบุรี"),
    ("Kanchanaburi",       "กาญจนบุรี"),
    ("Suphan Buri",        "สุพรรณบุรี"),
    ("Nakhon Pathom",      "นครปฐม"),
    ("Samut Sakhon",       "สมุทรสาคร"),
    ("Samut Songkhram",    "สมุทรสงคราม"),
    ("Phetchaburi",        "เพชรบุรี"),
    ("Prachuap Khiri Khan","ประจวบคีรีขันธ์"),
    ("Nakhon Si Thammarat","นครศรีธรรมราช"),
    ("Krabi",              "กระบี่"),
    ("Phangnga",           "พังงา"),
    ("Phuket",             "ภูเก็ต"),
    ("Surat Thani",        "สุราษฎร์ธานี"),
    ("Ranong",             "ระนอง"),
    ("Chumphon",           "ชุมพร"),
    ("Songkhla",           "สงขลา"),
    ("Satun",              "สตูล"),
    ("Trang",              "ตรัง"),
    ("Phatthalung",        "พัทลุง"),
    ("Pattani",            "ปัตตานี"),
    ("Yala",               "ยะลา"),
    ("Narathiwat",         "นราธิวาส"),
]

# ── STEP 5 : Settings ─────────────────────────────────────────
TIMEFRAME = "2026-01-01 2026-04-30"   # Jan 1 – Apr 30, 2026
GEO       = "TH"                       # Country: Thailand
SLEEP_MIN = 5     # minimum seconds between requests
SLEEP_MAX = 10    # maximum seconds between requests
RETRY_WAIT = 60   # seconds to wait if Google rate-limits us


# ── STEP 6 : Helper function to fetch ONE keyword ─────────────
def fetch_trends(keyword, geo=GEO, timeframe=TIMEFRAME):
    """
    Fetch interest-over-time data from Google Trends for ONE keyword.
    Returns a list of dicts like:
      [{"date": "2026-01-04", "interest": 45}, ...]
    Returns None if the request fails.
    """
    for attempt in range(3):   # try up to 3 times
        try:
            pytrends.build_payload(
                kw_list=[keyword],
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=""
            )
            df = pytrends.interest_over_time()

            if df.empty:
                print(f"    ⚠️  No data returned for: {keyword}")
                return []

            # Convert the pandas DataFrame rows → list of dicts
            results = []
            for date, row in df.iterrows():
                results.append({
                    "date":     str(date.date()),
                    "interest": int(row[keyword])
                })
            return results

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "Too Many Requests" in err_msg:
                print(f"    🚫 Rate limited! Waiting {RETRY_WAIT}s before retry {attempt+1}/3...")
                time.sleep(RETRY_WAIT)
            else:
                print(f"    ❌ Error on attempt {attempt+1}: {err_msg}")
                time.sleep(10)

    return None   # all 3 attempts failed


# ── STEP 7 : Main loop — fetch data for all 77 provinces ──────
print(f"📅 Timeframe: {TIMEFRAME}")
print(f"📍 Region   : {GEO} (Thailand)")
print(f"🏙️  Provinces: {len(PROVINCES)}")
print("=" * 60)

total_inserted = 0

# ── Load already-collected keywords to skip duplicates ────────
print("🔍 Checking existing data in MongoDB...")
existing = set()
for doc in collection.find({}, {"keyword": 1, "_id": 0}):
    existing.add(doc["keyword"])
print(f"   Already collected: {len(existing)} keywords — will skip these\n")

for idx, (eng_name, thai_name) in enumerate(PROVINCES, start=1):
    print(f"\n[{idx:02d}/{len(PROVINCES)}] Province: {eng_name} / {thai_name}")

    # ── Build the two keyword strings ──
    kw_english = f"Travel {eng_name}"          # e.g.  "Travel Bangkok"
    kw_thai    = f"เที่ยว {thai_name}"         # e.g.  "เที่ยว กรุงเทพมหานคร"

    for keyword, lang in [(kw_english, "EN"), (kw_thai, "TH")]:
        # ── Skip if already in MongoDB ──
        if keyword in existing:
            print(f"  ⏭️  [{lang}] Already collected, skipping: {keyword}")
            continue

        print(f"  🔍 [{lang}] Fetching: {keyword}")

        data = fetch_trends(keyword)

        if data is None:
            print(f"  ⛔ Skipped after 3 failed attempts.")
            continue

        if len(data) == 0:
            print(f"  ⚠️  No trend data available (all zeros or region not tracked).")
            continue

        # ── Build the MongoDB document ──
        document = {
            "province_en":  eng_name,
            "province_th":  thai_name,
            "keyword":      keyword,
            "language":     lang,
            "timeframe":    TIMEFRAME,
            "geo":          GEO,
            "fetched_at":   datetime.utcnow().isoformat(),
            "data_points":  data           # list of {date, interest}
        }

        # ── Insert into MongoDB ──
        result = collection.insert_one(document)
        total_inserted += 1
        print(f"  ✅ Saved {len(data)} data points → MongoDB _id: {result.inserted_id}")

        # ── Sleep between requests to avoid rate limits ──
        sleep_sec = random.uniform(SLEEP_MIN, SLEEP_MAX)
        print(f"  ⏳ Sleeping {sleep_sec:.1f}s...")
        time.sleep(sleep_sec)

# ── STEP 8 : Done! ────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"🎉 Finished! Total documents inserted: {total_inserted}")
print(f"📦 Database : thailand_trends_db")
print(f"📂 Collection: travel_trends_2026")
client.close()
