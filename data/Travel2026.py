# =============================================================
# Travel2026.py (Sustainable, Automated & Bulletproof Version)
# Goal: Fetch Google Trends data for all 77 Thai provinces
#       for Jan-May 2026 and save it to MongoDB (travel_trends_2026).
# =============================================================

import os
import time
import random
import pathlib
import tomllib
import logging
from datetime import datetime, timezone
from pytrends.request import TrendReq
from pymongo import MongoClient

# ── STEP 1 : Setup Logging ───────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ── STEP 2 : Bulletproof Config Loader ───────────────────────
SECRETS_FILE = pathlib.Path("/workspaces/gemma-data-driven-tourism-project/.streamlit/secrets.toml")
MONGO_URI = os.getenv("MONGO_URI") 

if not MONGO_URI and SECRETS_FILE.exists():
    with open(SECRETS_FILE, "rb") as f:
        try:
            secrets = tomllib.load(f)
            MONGO_URI = secrets.get("MONGO_URI")
            if not MONGO_URI:
                for section_name, section_content in secrets.items():
                    if isinstance(section_content, dict) and "MONGO_URI" in section_content:
                        MONGO_URI = section_content.get("MONGO_URI")
                        logging.info(f"🔍 Found MONGO_URI hiding inside the [{section_name}] section!")
                        break
        except Exception as e:
            raise SystemExit(f"❌ โครงสร้างไฟล์ secrets.toml ผิดพลาดจนอ่านไม่ได้: {e}")

if not MONGO_URI:
    raise SystemExit(
        f"❌ FATAL ERROR: ไม่พบ MONGO_URI ทั้งใน Environment Variable และในไฟล์\n"
        f"ระบบพยายามค้นหาไฟล์จาก: {SECRETS_FILE}\n"
    )

# ── STEP 3 : Connect to MongoDB ──────────────────────────────
logging.info("🔌 Connecting to MongoDB...")
client      = MongoClient(MONGO_URI)
db          = client["thailand_trends_db"]
collection  = db["travel_trends_2026"] 

# ⚠️ ล้างข้อมูลเก่าทิ้งทั้งหมดเพื่อป้องกันปัญหา DuplicateKeyError จากข้อมูลที่ซ้อนทับกัน
logging.info("🧹 Dropping old collection to prevent index build failures...")
collection.drop()

# สร้าง Index ป้องกันข้อมูลซ้ำ (ใช้ unique=True)
collection.create_index([("keyword", 1), ("timeframe", 1)], unique=True)
logging.info("✅ Connected & Index Verified!")

# ── STEP 4 : Setup Google Trends API ─────────────────────────
pytrends = TrendReq(hl="th-TH", tz=-420)

# ── STEP 5 : All 77 Thai provinces ───────────────────────────
PROVINCES = [
    ("Bangkok",            "กรุงเทพมหานคร"), ("Samut Prakan",       "สมุทรปราการ"),
    ("Nonthaburi",         "นนทบุรี"), ("Pathum Thani",       "ปทุมธานี"),
    ("Phra Nakhon Si Ayutthaya", "พระนครศรีอยุธยา"), ("Ang Thong",          "อ่างทอง"),
    ("Lop Buri",           "ลพบุรี"), ("Sing Buri",          "สิงห์บุรี"),
    ("Chai Nat",           "ชัยนาท"), ("Saraburi",           "สระบุรี"),
    ("Chon Buri",          "ชลบุรี"), ("Rayong",             "ระยอง"),
    ("Chanthaburi",        "จันทบุรี"), ("Trat",               "ตราด"),
    ("Chachoengsao",       "ฉะเชิงเทรา"), ("Prachin Buri",       "ปราจีนบุรี"),
    ("Nakhon Nayok",       "นครนายก"), ("Sa Kaeo",            "สระแก้ว"),
    ("Nakhon Ratchasima",  "นครราชสีมา"), ("Buri Ram",           "บุรีรัมย์"),
    ("Surin",              "สุรินทร์"), ("Si Sa Ket",          "ศรีสะเกษ"),
    ("Ubon Ratchathani",   "อุบลราชธานี"), ("Yasothon",           "ยโสธร"),
    ("Chaiyaphum",         "ชัยภูมิ"), ("Amnat Charoen",      "อำนาจเจริญ"),
    ("Bueng Kan",          "บึงกาฬ"), ("Nong Bua Lam Phu",   "หนองบัวลำภู"),
    ("Khon Kaen",          "ขอนแก่น"), ("Udon Thani",         "อุดรธานี"),
    ("Loei",               "เลย"), ("Nong Khai",          "หนองคาย"),
    ("Maha Sarakham",      "มหาสารคาม"), ("Roi Et",             "ร้อยเอ็ด"),
    ("Kalasin",            "กาฬสินธุ์"), ("Sakon Nakhon",       "สกลนคร"),
    ("Nakhon Phanom",      "นครพนม"), ("Mukdahan",           "มุกดาหาร"),
    ("Chiang Mai",         "เชียงใหม่"), ("Lamphun",            "ลำพูน"),
    ("Lampang",            "ลำปาง"), ("Uttaradit",          "อุตรดิตถ์"),
    ("Phrae",              "แพร่"), ("Nan",                "น่าน"),
    ("Phayao",             "พะเยา"), ("Chiang Rai",         "เชียงราย"),
    ("Mae Hong Son",       "แม่ฮ่องสอน"), ("Nakhon Sawan",       "นครสวรรค์"),
    ("Uthai Thani",        "อุทัยธานี"), ("Kamphaeng Phet",     "กำแพงเพชร"),
    ("Tak",                "ตาก"), ("Sukhothai",          "สุโขทัย"),
    ("Phitsanulok",        "พิษณุโลก"), ("Phichit",            "พิจิตร"),
    ("Phetchabun",         "เพชรบูรณ์"), ("Ratchaburi",         "ราชบุรี"),
    ("Kanchanaburi",       "กาญจนบุรี"), ("Suphan Buri",        "สุพรรณบุรี"),
    ("Nakhon Pathom",      "นครปฐม"), ("Samut Sakhon",       "สมุทรสาคร"),
    ("Samut Songkhram",    "สมุทรสงคราม"), ("Phetchaburi",        "เพชรบุรี"),
    ("Prachuap Khiri Khan","ประจวบคีรีขันธ์"), ("Nakhon Si Thammarat","นครศรีธรรมราช"),
    ("Krabi",              "กระบี่"), ("Phangnga",           "พังงา"),
    ("Phuket",             "ภูเก็ต"), ("Surat Thani",        "สุราษฎร์ธานี"),
    ("Ranong",             "ระนอง"), ("Chumphon",           "ชุมพร"),
    ("Songkhla",           "สงขลา"), ("Satun",              "สตูล"),
    ("Trang",              "ตรัง"), ("Phatthalung",        "พัทลุง"),
    ("Pattani",            "ปัตตานี"), ("Yala",               "ยะลา"),
    ("Narathiwat",         "นราธิวาส")
]

# ── STEP 6 : Dynamic Settings ─────────
# บังคับดึงข้อมูลตั้งแต่วันที่ 1 ม.ค. 2026 ถึง 31 พ.ค. 2026
TIMEFRAME = "2026-01-01 2026-05-31"
GEO       = "TH"
SLEEP_MIN = 5
SLEEP_MAX = 10
RETRY_WAIT = 60

# ── STEP 7 : Helper function to fetch ONE keyword ─────────────
def fetch_trends(keyword, geo=GEO, timeframe=TIMEFRAME):
    for attempt in range(3):
        try:
            pytrends.build_payload(kw_list=[keyword], cat=0, timeframe=timeframe, geo=geo, gprop="")
            df = pytrends.interest_over_time()
            if df.empty:
                logging.warning(f"⚠️ No data returned for: {keyword}")
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
                logging.warning(f"🚫 Rate limited! Waiting {RETRY_WAIT}s before retry {attempt+1}/3...")
                time.sleep(RETRY_WAIT)
            else:
                logging.error(f"❌ Error on attempt {attempt+1}: {err_msg}")
                time.sleep(10)
    return None

# ── STEP 8 : Main loop ────────────────────────────────────────
logging.info("=" * 60)
logging.info(f"📅 Timeframe: {TIMEFRAME}")
logging.info(f"📍 Region   : {GEO} (Thailand)")
logging.info(f"🏙️  Provinces: {len(PROVINCES)}")
logging.info("=" * 60)

existing = set()
logging.info("🔍 Checking existing data in MongoDB for this timeframe...")
for doc in collection.find({"timeframe": TIMEFRAME}, {"keyword": 1, "_id": 0}):
    existing.add(doc["keyword"])
logging.info(f"📌 Already collected: {len(existing)} keywords for {TIMEFRAME}")

total_inserted = 0

for idx, (eng_name, thai_name) in enumerate(PROVINCES, start=1):
    logging.info(f"--- [{idx:02d}/{len(PROVINCES)}] {eng_name} / {thai_name} ---")
    
    kw_english = f"Travel {eng_name}"
    kw_thai    = f"เที่ยว {thai_name}"
    
    for keyword, lang in [(kw_english, "EN"), (kw_thai, "TH")]:
        if keyword in existing:
            logging.info(f"⏭️ [{lang}] Skipping, already exists: {keyword}")
            continue
            
        logging.info(f"🔍 [{lang}] Fetching: {keyword}")
        data = fetch_trends(keyword)
        
        if data is None:
            logging.error(f"⛔ Skipped after 3 failed attempts: {keyword}")
            continue
            
        if len(data) == 0:
            logging.warning(f"⚠️ No trend data available for: {keyword}")
        else:
            document = {
                "province_en":  eng_name,
                "province_th":  thai_name,
                "keyword":      keyword,
                "language":     lang,
                "timeframe":    TIMEFRAME,
                "geo":          GEO,
                "fetched_at":   datetime.now(timezone.utc).isoformat(),
                "data_points":  data
            }
            try:
                result = collection.insert_one(document)
                logging.info(f"✅ Saved {len(data)} points -> _id: {result.inserted_id}")
                total_inserted += 1
            except Exception as e:
                logging.error(f"❌ Failed to insert {keyword} to MongoDB: {e}")
            
        sleep_sec = random.uniform(SLEEP_MIN, SLEEP_MAX)
        logging.info(f"⏳ Sleeping {sleep_sec:.1f}s...")
        time.sleep(sleep_sec)

# ── STEP 9 : Done! ────────────────────────────────────────────
logging.info("=" * 60)
logging.info(f"🎉 Finished! Total documents inserted: {total_inserted}")
client.close()