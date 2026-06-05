# =============================================================
# Travel_Monthly.py
# Goal: Fetch Google Trends data for all 77 Thai provinces
#       for the PREVIOUS MONTH and save it to MongoDB.
#
# REGION: Thailand (TH)
# =============================================================

import os
import time
import random
import pathlib
import tomllib  # สำหรับ Python 3.11 ขึ้นไป
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from pymongo import MongoClient

# ── STEP 1 : Load secrets.toml ──────────────────────────────
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

# แก้ไขให้ชี้เข้าไปในโฟลเดอร์ .streamlit เรียบร้อยแล้ว
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml" 

MONGO_URI = None

# อ่านค่าจากไฟล์ secrets.toml (ถ้ามีไฟล์)
if SECRETS_FILE.exists():
    with open(SECRETS_FILE, "rb") as f:
        secrets = tomllib.load(f)
        MONGO_URI = secrets.get("MONGO_URI")

# กรณีหาไม่เจอในไฟล์ ให้ลองหาจาก Environment Variable
if not MONGO_URI:
    MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise SystemExit(
        "Missing MongoDB configuration. Create a secrets.toml file in the .streamlit folder with:\n"
        'MONGO_URI = "<your_mongo_connection_string>"\n'
        "or set the environment variable MONGO_URI before running the script."
    )

# ── STEP 2 : Connect to MongoDB ──────────────────────────────
print("🔌 Connecting to MongoDB...")
client      = MongoClient(MONGO_URI)
db          = client["thailand_trends_db"]
collection  = db["travel_trends_monthly"] 
print("✅ Connected!\n")

# ── STEP 3 : Setup Google Trends API ─────────────────────────
pytrends = TrendReq(hl="th-TH", tz=-420)

# ── STEP 4 : All 77 Thai provinces ───────────────────────────
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

# ── STEP 5 : Dynamic Settings ─────────
today = datetime.now()
first_day_this_month = today.replace(day=1)
last_day_prev_month = first_day_this_month - timedelta(days=1)
first_day_prev_month = last_day_prev_month.replace(day=1)

TIMEFRAME = f"{first_day_prev_month.strftime('%Y-%m-%d')} {last_day_prev_month.strftime('%Y-%m-%d')}"
GEO       = "TH"
SLEEP_MIN = 5
SLEEP_MAX = 10
RETRY_WAIT = 60

# ── STEP 6 : Helper function to fetch ONE keyword ─────────────
def fetch_trends(keyword, geo=GEO, timeframe=TIMEFRAME):
    for attempt in range(3):
        try:
            pytrends.build_payload(kw_list=[keyword], cat=0, timeframe=timeframe, geo=geo, gprop="")
            df = pytrends.interest_over_time()
            if df.empty:
                print(f"    ⚠️  No data returned for: {keyword}")
                return []
            
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
    return None

# ── STEP 7 : Main loop ────────────────────────────────────────
print("=" * 60)
print(f"📅 Timeframe: {TIMEFRAME} (Previous Month)")
print(f"📍 Region   : {GEO} (Thailand)")
print(f"🏙️  Provinces: {len(PROVINCES)}")
print("=" * 60)

existing = set()
print("🔍 Checking existing data in MongoDB for this timeframe...")
for doc in collection.find({"timeframe": TIMEFRAME}, {"keyword": 1, "_id": 0}):
    existing.add(doc["keyword"])
print(f"   Already collected: {len(existing)} keywords for {TIMEFRAME}\n")

total_inserted = 0

for idx, (eng_name, thai_name) in enumerate(PROVINCES, start=1):
    print(f"\n[{idx:02d}/{len(PROVINCES)}] Province: {eng_name} / {thai_name}")
    
    kw_english = f"Travel {eng_name}"
    kw_thai    = f"เที่ยว {thai_name}"
    
    for keyword, lang in [(kw_english, "EN"), (kw_thai, "TH")]:
        if keyword in existing:
            print(f"  ⏭️  [{lang}] Already collected this month, skipping: {keyword}")
            continue
            
        print(f"  🔍 [{lang}] Fetching: {keyword}")
        data = fetch_trends(keyword)
        
        if data is None:
            print(f"  ⛔ Skipped after 3 failed attempts.")
            continue
            
        if len(data) == 0:
            print(f"  ⚠️  No trend data available.")
        else:
            document = {
                "province_en":  eng_name,
                "province_th":  thai_name,
                "keyword":      keyword,
                "language":     lang,
                "timeframe":    TIMEFRAME,
                "geo":          GEO,
                "fetched_at":   datetime.utcnow().isoformat(),
                "data_points":  data
            }
            result = collection.insert_one(document)
            print(f"  ✅ Saved {len(data)} data points → MongoDB _id: {result.inserted_id}")
            total_inserted += 1
            
        sleep_sec = random.uniform(SLEEP_MIN, SLEEP_MAX)
        print(f"  ⏳ Sleeping {sleep_sec:.1f}s...")
        time.sleep(sleep_sec)

# ── STEP 8 : Done! ────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"🎉 Finished! Total documents inserted: {total_inserted}")
print(f"📦 Database : thailand_trends_db")
print(f"📂 Collection: travel_trends_monthly")
client.close()