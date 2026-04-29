import streamlit as st
from google import genai
import pandas as pd
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
import io
import re
import math

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CitySmart | AI Trip Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1a1a2e;
}
.stApp {
    background: linear-gradient(135deg, #f5f3ef 0%, #faf9f7 100%);
}
.block-container {
    padding-top: 1.5rem !important; /* Added space to prevent top overflow */
    padding-bottom: 0.5rem !important;
    max-width: 1360px;
}
.element-container {
    margin-bottom: 0rem !important;
}

/* Hero */
.hero {
    padding: 0.4rem 0 0.2rem 0 !important;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(1.8rem, 3.5vw, 2.5rem);
    font-weight: 800;
    color: #12111a;
    line-height: 1.15;
    margin: 0 !important;
    word-break: break-word;
}
.hero-title span {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #6c6c6c;
    margin-top: 0.15rem !important;
    margin-bottom: 0 !important;
    max-width: 720px;
}

/* Language selector */
div[data-testid="stHorizontalBlock"] > div:has(.stRadio) {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    padding-top: 0.35rem;
}
.stRadio {
    background: white;
    border-radius: 100px;
    padding: 0.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    display: inline-flex;
}
.stRadio > div {
    display: flex !important;
    flex-direction: row !important;
    gap: 0 !important;
}
.stRadio > div > label {
    border-radius: 100px !important;
    padding: 0.48rem 1rem !important;
    margin: 0 !important;
    font-size: 0.86rem;
    font-weight: 500;
    color: #666;
    background: transparent !important;
    border: none !important;
}
.stRadio > div > label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
.stRadio > div > label:has(input:checked) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.28);
}

/* Form */
.form-container {
    padding: 0.25rem 0 0.15rem 0 !important;
}
.stSelectbox, .stMultiSelect, .stDateInput, .stSlider {
    margin-bottom: 0.4rem !important;
    margin-top: 0.1rem !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div {
    background: rgba(255,255,255,0.94) !important;
    border-radius: 12px !important;
    border: 1px solid #e9e9ef !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
label {
    font-weight: 600 !important;
    color: #1a1a2e !important;
    font-size: 0.92rem !important;
    margin-bottom: 0.12rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.8rem 2.2rem !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.30) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.82rem 2rem !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* Combined section */
.combo-card {
    background: white;
    border-radius: 24px;
    padding: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    margin-top: 0.8rem;
    margin-bottom: 1rem;
}
.combo-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.08rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.75rem;
}
.map-panel {
    background: #f8f9ff;
    border-radius: 18px;
    padding: 0.7rem;
    border: 1px solid #ecefff;
    height: 100%;
}
.weather-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 18px;
    padding: 1rem;
    color: white;
    height: 100%;
}
.weather-panel-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.04rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.75rem;
}
.weather-city-card {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    padding: 0.8rem 0.95rem;
    margin-bottom: 0.65rem;
}
.weather-city-card:last-child {
    margin-bottom: 0;
}
.weather-city-name {
    font-weight: 700;
    font-size: 0.98rem;
    margin-bottom: 0.25rem;
}
.weather-line {
    font-size: 0.91rem;
    line-height: 1.55;
}

/* Result cards */
.result-card {
    background: white;
    border-radius: 20px; /* Adjusted border-radius */
    padding: 1.3rem 1.5rem; /* Compacted padding */
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    height: 100%; /* Enforce equal height in columns */
    border-top: 6px solid #667eea;
    display: flex; /* Use flexbox for robust height */
    flex-direction: column;
}
.gem-card {
    border-top: 6px solid #ff9933;
}
.card-label {
    color: #667eea;
    font-weight: 700;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.35rem !important;
}
.gem-card .card-label {
    color: #ff9933;
}

/* Reset Streamlit's default markdown margins for consistency */
.result-card > div[data-testid="stMarkdown"] > div > * {
    margin: 0;
    padding: 0;
}

/* Consistent Typography & Spacing */
.result-card h1, .result-card h2, .result-card h3, .result-card h4, .result-card p, .result-card li {
    font-family: 'Syne', sans-serif !important;
    color: #1a1a2e !important;
    line-height: 1.6 !important; /* Standardized line-height */
}
.result-card h2 {
    font-size: 1.22rem !important;
    color: #667eea !important;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 0.2rem !important;
    margin: 1.1rem 0 0.6rem 0 !important; /* Consistent heading margins */
}
.result-card h3 {
    font-size: 1.08rem !important;
    margin: 1rem 0 0.4rem 0 !important;
}
.result-card p, .result-card li {
    font-size: 0.95rem !important;
    color: #2a2a3e !important;
    margin-bottom: 0.5rem !important;
}
.result-card ul {
    padding-left: 1.2rem !important; /* Aligned list items */
    margin-bottom: 0.5rem !important;
}
.result-card strong {
    display: inline-block; /* Keeps background as a single block */
    background-color: #f0f2ff;
    padding: 0.15rem 0.6rem; /* Adjusted padding */
    border-radius: 7px;
    color: #667eea !important;
    line-height: 1.6 !important; /* Matched line-height for alignment */
}

/* map */
div[data-testid="stMap"] iframe,
div[data-testid="stMap"] > div {
    height: 390px !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

/* alerts */
.stSuccess {
    background-color: #d4edda !important;
    border-left: 4px solid #28a745 !important;
    padding: 0.7rem !important;
    border-radius: 10px !important;
    margin: 0.4rem 0 !important;
}
.stError {
    background-color: #f8d7da !important;
    border-left: 4px solid #dc3545 !important;
    padding: 0.7rem !important;
    border-radius: 10px !important;
    margin: 0.4rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── PDF Generation ───────────────────────────────────────────────────────────
def create_pdf(content_dict, province, lang='TH'):
    buffer = io.BytesIO()

    try:
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        base_font = 'HeiseiMin-W3'
    except:
        base_font = 'Helvetica'

    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=base_font,
        fontSize=22,
        textColor='#1a1a2e',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=base_font,
        fontSize=15,
        textColor='#667eea',
        spaceAfter=8,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=base_font,
        fontSize=10.5,
        leading=15,
        textColor='#1a1a2e'
    )

    title_text = {
        'TH': f'แผนการเดินทาง: {province}',
        'EN': f'Travel Plan: {province}',
        'CN': f'旅行计划: {province}'
    }.get(lang, f'Travel Plan: {province}')

    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y')}", body_style))
    story.append(Spacer(1, 0.2*inch))

    section_map = [
        ('weather', {'TH': 'สภาพอากาศ', 'EN': 'Weather', 'CN': '天气'}),
        ('main', {'TH': f'จุดหมายหลัก: {province}', 'EN': f'Main Destination: {province}', 'CN': f'主要目的地: {province}'}),
        ('gem', {'TH': f'ทางเลือกใกล้เคียง: {content_dict.get("gem_city","")}', 'EN': f'Nearby Alternative: {content_dict.get("gem_city","")}', 'CN': f'附近推荐: {content_dict.get("gem_city","")}'})
    ]

    for key, title_dict in section_map:
        content = content_dict.get(key, '')
        if not content:
            continue
        if key == 'gem':
            story.append(PageBreak())

        story.append(Paragraph(title_dict.get(lang, title_dict['EN']), heading_style))

        if key == 'gem' and content_dict.get('travel_info'):
            story.append(Paragraph(content_dict['travel_info'], body_style))
            story.append(Spacer(1, 0.08*inch))

        clean = content.replace('**', '').replace('#', '')
        for para in clean.split('\n\n'):
            para = para.strip()
            if para:
                story.append(Paragraph(para.replace('\n', ''), body_style))
                story.append(Spacer(1, 0.08*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ─── AI Setup ─────────────────────────────────────────────────────────────────
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ AI ได้: {e}")
    st.stop()

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df_t = pd.read_csv('data/master_tourism_analysis.csv')
        df_f = pd.read_excel('data/Thailand_Festival_Master.xlsx')
        df_t['ProvinceEN'] = df_t['ProvinceEN'].astype(str).str.strip()
        df_t.dropna(subset=['ProvinceEN', 'Region_EN'], inplace=True)

        province_th_map = {
            'Amnat Charoen': 'อำนาจเจริญ', 'Ang Thong': 'อ่างทอง', 'Bangkok': 'กรุงเทพมหานคร',
            'Bueng Kan': 'บึงกาฬ', 'Buri Ram': 'บุรีรัมย์', 'Chachoengsao': 'ฉะเชิงเทรา',
            'Chai Nat': 'ชัยนาท', 'Chaiyaphum': 'ชัยภูมิ', 'Chanthaburi': 'จันทบุรี',
            'Chiang Mai': 'เชียงใหม่', 'Chiang Rai': 'เชียงราย', 'Chon Buri': 'ชลบุรี',
            'Chumphon': 'ชุมพร', 'Kalasin': 'กาฬสินธุ์', 'Kamphaeng Phet': 'กำแพงเพชร',
            'Kanchanaburi': 'กาญจนบุรี', 'Khon Kaen': 'ขอนแก่น', 'Krabi': 'กระบี่',
            'Lampang': 'ลำปาง', 'Lamphun': 'ลำพูน', 'Loei': 'เลย', 'Lop Buri': 'ลพบุรี',
            'Mae Hong Son': 'แม่ฮ่องสอน', 'Maha Sarakham': 'มหาสารคาม', 'Mukdahan': 'มุกดาหาร',
            'Nakhon Nayok': 'นครนายก', 'Nakhon Pathom': 'นครปฐม', 'Nakhon Phanom': 'นครพนม',
            'Nakhon Ratchasima': 'นครราชสีมา', 'Nakhon Sawan': 'นครสวรรค์',
            'Nakhon Si Thammarat': 'นครศรีธรรมราช', 'Nan': 'น่าน', 'Narathiwat': 'นราธิวาส',
            'Nong Bua Lam Phu': 'หนองบัวลำภู', 'Nong Khai': 'หนองคาย', 'Nonthaburi': 'นนทบุรี',
            'Pathum Thani': 'ปทุมธานี', 'Pattani': 'ปัตตานี', 'Phang Nga': 'พังงา',
            'Phangnga': 'พังงา', 'Phatthalung': 'พัทลุง', 'Phayao': 'พะเยา', 'Phetchabun': 'เพชรบูรณ์',
            'Phetchaburi': 'เพชรบุรี', 'Phichit': 'พิจิตร', 'Phitsanulok': 'พิษณุโลก',
            'Phra Nakhon Si Ayutthaya': 'พระนครศรีอยุธยา', 'Phrae': 'แพร่', 'Phuket': 'ภูเก็ต',
            'Prachin Buri': 'ปราจีนบุรี', 'Prachuap Khiri Khan': 'ประจวบคีรีขันธ์',
            'Ranong': 'ระนอง', 'Ratchaburi': 'ราชบุรี', 'Rayong': 'ระยอง', 'Roi Et': 'ร้อยเอ็ด',
            'Sa Kaeo': 'สระแก้ว', 'Sakon Nakhon': 'สกลนคร', 'Samut Prakan': 'สมุทรปราการ',
            'Samut Sakhon': 'สมุทรสาคร', 'Samut Songkhram': 'สมุทรสงคราม', 'Saraburi': 'สระบุรี',
            'Satun': 'สตูล', 'Si Sa Ket': 'ศรีสะเกษ', 'Sing Buri': 'สิงห์บุรี',
            'Songkhla': 'สงขลา', 'Sukhothai': 'สุโขทัย', 'Suphan Buri': 'สุพรรณบุรี',
            'Surat Thani': 'สุราษฎร์ธานี', 'Surin': 'สุรินทร์', 'Tak': 'ตาก', 'Trang': 'ตรัง',
            'Trat': 'ตราด', 'Ubon Ratchathani': 'อุบลราชธานี', 'Udon Thani': 'อุดรธานี',
            'Uthai Thani': 'อุทัยธานี', 'Uttaradit': 'อุตรดิตถ์', 'Yala': 'ยะลา', 'Yasothon': 'ยโสธร'
        }
        df_t['ProvinceTH'] = df_t['ProvinceEN'].map(province_th_map).fillna(df_t['ProvinceEN'])
        return df_t, df_f
    except FileNotFoundError as e:
        st.error(f"ไม่พบไฟล์ข้อมูล: {e}")
        st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.stop()

# ─── Province Coordinates ─────────────────────────────────────────────────────
PROVINCE_COORDS = {
    'Bangkok': (13.7563, 100.5018),
    'Krabi': (8.0863, 98.9063),
    'Phuket': (7.8804, 98.3923),
    'Phang Nga': (8.4509, 98.5255),
    'Phangnga': (8.4509, 98.5255),
    'Ranong': (9.9529, 98.6085),
    'Trang': (7.5563, 99.6114),
    'Phatthalung': (7.6179, 100.0779),
    'Satun': (6.6238, 100.0674),
    'Surat Thani': (9.1382, 99.3215),
    'Chumphon': (10.4930, 99.1800),
    'Nakhon Si Thammarat': (8.4304, 99.9631),
    'Songkhla': (7.1897, 100.5951),
    'Pattani': (6.8695, 101.2505),
    'Yala': (6.5411, 101.2804),
    'Narathiwat': (6.4254, 101.8253),
    'Chiang Mai': (18.7883, 98.9853),
    'Chiang Rai': (19.9105, 99.8406),
    'Lampang': (18.2888, 99.4908),
    'Lamphun': (18.5746, 99.0087),
    'Mae Hong Son': (19.3013, 97.9654),
    'Nan': (18.7756, 100.7730),
    'Phrae': (18.1459, 100.1410),
    'Phayao': (19.1665, 99.9018),
    'Loei': (17.4860, 101.7223),
    'Khon Kaen': (16.4419, 102.8350),
    'Udon Thani': (17.4138, 102.7870),
    'Ubon Ratchathani': (15.2447, 104.8472),
    'Nakhon Ratchasima': (14.9799, 102.0977),
    'Rayong': (12.6814, 101.2816),
    'Chanthaburi': (12.6112, 102.1038),
    'Trat': (12.2428, 102.5175),
    'Prachuap Khiri Khan': (11.8124, 99.7973),
    'Kanchanaburi': (14.0228, 99.5328),
    'Ratchaburi': (13.5283, 99.8134),
    'Phetchaburi': (13.1112, 99.9447),
    'Phra Nakhon Si Ayutthaya': (14.3532, 100.5689),
    'Sukhothai': (17.0056, 99.8264)
}

REGION_NEARBY_FALLBACK = {
    'South': ['Phang Nga', 'Krabi', 'Ranong', 'Trang', 'Satun', 'Phatthalung', 'Nakhon Si Thammarat', 'Surat Thani'],
    'North': ['Lamphun', 'Lampang', 'Phrae', 'Nan', 'Phayao', 'Mae Hong Son', 'Chiang Rai'],
    'Northeast': ['Khon Kaen', 'Udon Thani', 'Loei', 'Roi Et', 'Ubon Ratchathani'],
    'Central': ['Kanchanaburi', 'Ratchaburi', 'Phetchaburi', 'Prachuap Khiri Khan', 'Nakhon Pathom'],
    'East': ['Rayong', 'Chanthaburi', 'Trat', 'Chon Buri']
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))

def find_nearest_secondary_city(selected_province, city_info, df_tour):
    base_coord = PROVINCE_COORDS.get(selected_province)

    candidates = df_tour[
        (df_tour['City_type_EN'] == 'Secondary City') &
        (df_tour['Region_EN'] == city_info['Region_EN']) &
        (df_tour['ProvinceEN'] != selected_province)
    ][['ProvinceEN', 'ProvinceTH']].drop_duplicates()

    if not candidates.empty and base_coord:
        scored = []
        for _, row in candidates.iterrows():
            candidate = row['ProvinceEN']
            cand_coord = PROVINCE_COORDS.get(candidate)
            if not cand_coord:
                continue
            dist = haversine_km(base_coord[0], base_coord[1], cand_coord[0], cand_coord[1])
            scored.append((candidate, dist))

        if scored:
            scored.sort(key=lambda x: x[1])
            return scored[0][0]

    # fallback by region
    fallback_candidates = REGION_NEARBY_FALLBACK.get(city_info['Region_EN'], [])
    for p in fallback_candidates:
        if p != selected_province and p in df_tour['ProvinceEN'].values:
            return p

    return None

# ─── Cleaning & Parsing ───────────────────────────────────────────────────────
WEATHER_TEMPLATE_MARKERS = [
    '[City Name]', '[Temperature]', '[Short weather condition]', '[Short travel advice]'
]

AI_META_PATTERNS = [
    r'^Date:',
    r'^City 1:',
    r'^City 2:',
    r'^Temp:',
    r'^Condition:',
    r'^Tip:',
    r'^Constraints:',
    r'^Check',
    r'^No English\?',
    r'^No parentheses\?',
    r'^Thai only\?',
    r'^Format followed\?',
    r'^Ready to output',
    r'^Final verification',
    r'^Self-Correction',
    r'^Writing Style:',
    r'^CRITICAL',
    r'^STRUCTURE:',
    r'^FORMAT:',
    r'^Example:',
]

@st.cache_data
def parse_locations_from_markdown(markdown_text):
    if not isinstance(markdown_text, str):
        return pd.DataFrame(columns=['name', 'lat', 'lon'])

    pattern = re.compile(r'\*\*(.*?)\s*\(Lat:\s*(-?\d+\.?\d*),\s*Lon:\s*(-?\d+\.?\d*)\)\*\*')
    locations = []
    matches = pattern.findall(markdown_text)

    for match in matches:
        try:
            name = str(match[0]).strip()
            lat = float(match[1])
            lon = float(match[2])
            locations.append({'name': name, 'lat': lat, 'lon': lon})
        except:
            continue

    if not locations:
        return pd.DataFrame(columns=['name', 'lat', 'lon'])

    return pd.DataFrame(locations).drop_duplicates(subset=['name', 'lat', 'lon'])

def normalize_spaces(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def strip_ai_meta_lines(text):
    if not isinstance(text, str):
        return ""

    text = normalize_spaces(text)
    cleaned = []

    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            cleaned.append("")
            continue

        if any(marker in raw for marker in WEATHER_TEMPLATE_MARKERS):
            continue

        if any(re.search(pattern, raw, flags=re.IGNORECASE) for pattern in AI_META_PATTERNS):
            continue

        if re.match(r'^\*\s+', raw):
            continue

        if re.match(r'^\d+\.\s+', raw) and any(keyword in raw.lower() for keyword in [
            'use', 'start', 'at the end', 'heading', 'format', 'structure'
        ]):
            continue

        cleaned.append(raw)

    return normalize_spaces("\n".join(cleaned))

def dedupe_weather_blocks(text):
    if not isinstance(text, str):
        return ""

    text = strip_ai_meta_lines(text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    blocks = []
    current = []

    for line in lines:
        if any(marker in line for marker in WEATHER_TEMPLATE_MARKERS):
            continue

        if line.startswith("📍 "):
            if current:
                blocks.append(current)
            current = [line]
        elif current and (line.startswith("🌡️ ") or line.startswith("☁️ ") or line.startswith("💡 ")):
            current.append(line)

    if current:
        blocks.append(current)

    unique = {}
    for block in blocks:
        city_line = next((x for x in block if x.startswith("📍 ")), None)
        temp_line = next((x for x in block if x.startswith("🌡️ ")), None)
        cond_line = next((x for x in block if x.startswith("☁️ ")), None)
        tip_line = next((x for x in block if x.startswith("💡 ")), None)

        if city_line and temp_line and cond_line and tip_line:
            city_name = city_line.replace("📍 ", "").strip()
            if city_name not in unique:
                unique[city_name] = [city_line, temp_line, cond_line, tip_line]

    final_blocks = ["\n".join(block) for block in unique.values()]
    return normalize_spaces("\n\n".join(final_blocks))

def fallback_weather_from_locations(locations_text):
    cities = []
    for part in str(locations_text).split(','):
        city = part.strip()
        if city and city not in cities:
            cities.append(city)

    default_temp = "26-34 องศาเซลเซียส"
    default_cond = "อากาศร้อน มีแดดสลับเมฆบางช่วง"
    default_tip = "พกน้ำดื่ม ครีมกันแดด และร่มติดตัว"

    blocks = []
    for city in cities[:2]:
        blocks.append(f"📍 {city}\n🌡️ {default_temp}\n☁️ {default_cond}\n💡 {default_tip}")
    return "\n\n".join(blocks)

def parse_weather_blocks(text):
    cleaned = dedupe_weather_blocks(text)
    if not cleaned:
        return []

    blocks = cleaned.split("\n\n")
    parsed = []

    for block in blocks:
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        city = temp = cond = tip = ""
        for line in lines:
            if line.startswith("📍 "):
                city = line.replace("📍 ", "").strip()
            elif line.startswith("🌡️ "):
                temp = line.replace("🌡️ ", "").strip()
            elif line.startswith("☁️ "):
                cond = line.replace("☁️ ", "").strip()
            elif line.startswith("💡 "):
                tip = line.replace("💡 ", "").strip()

        if city and temp and cond and tip:
            parsed.append({
                "city": city,
                "temp": temp,
                "cond": cond,
                "tip": tip
            })

    return parsed

def ensure_itinerary_sections(text, days):
    if not isinstance(text, str):
        return ""

    text = strip_ai_meta_lines(text)
    if not text.strip():
        return ""

    # ถ้ามีหัวข้ออยู่แล้ว ใช้เลย
    if re.search(r'^##\s*🌟\s*วันที่', text, flags=re.MULTILINE):
        return normalize_spaces(text)

    # fallback: ถ้า AI ตอบเป็นก้อนเดียว
    sections = []
    for day in range(1, days + 1):
        sections.append(
            f"## 🌟 วันที่ {day}\n"
            f"- 🌅 เช้า: วางแผนเที่ยวในเมืองและแวะจุดเด่นของพื้นที่\n"
            f"- 🍜 กลางวัน: แวะร้านอาหารหรือคาเฟ่ยอดนิยมของจังหวัด\n"
            f"- 🌆 เย็น: เดินเล่นจุดชมวิวหรือย่านบรรยากาศดีเพื่อปิดท้ายวัน"
        )

    sections.append(
        "## 💰 สรุปงบประมาณ\n"
        "- ค่าที่พัก: ประมาณ 2,000 - 4,500 บาท\n"
        "- ค่าอาหาร: ประมาณ 800 - 1,500 บาท\n"
        "- ค่าเดินทาง: ประมาณ 800 - 2,000 บาท\n"
        "- ค่าเข้าสถานที่และกิจกรรม: ประมาณ 500 - 1,500 บาท\n"
        "- รวมโดยประมาณ: 4,100 - 9,500 บาทต่อคน\n\n"
        "## 🏨 ที่พักแนะนำ\n"
        "- **ที่พักแนะนำ 1 (Lat: 13.0000, Lon: 100.0000)** : ทำเลดี เดินทางสะดวก\n"
        "- **ที่พักแนะนำ 2 (Lat: 13.0100, Lon: 100.0100)** : บรรยากาศดี เหมาะกับการพักผ่อน"
    )

    return "\n\n".join(sections)

def clean_itinerary_response(text, days=3):
    if not isinstance(text, str):
        return ""

    text = strip_ai_meta_lines(text)
    lines = text.splitlines()
    cleaned_lines = []
    started = False

    for line in lines:
        stripped = line.strip()

        if re.match(r'^##\s*(🌟|💰|🏨)', stripped):
            started = True
            cleaned_lines.append(stripped)
            continue

        if not started:
            continue

        if any(marker in stripped for marker in WEATHER_TEMPLATE_MARKERS):
            continue

        cleaned_lines.append(stripped)

    result = normalize_spaces("\n".join(cleaned_lines))
    result = ensure_itinerary_sections(result, days)
    return result

def call_ai_strict(prompt, mode="general", max_retries=2, fallback_text=""):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model="gemma-4-31b-it", contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.35,
                    top_p=0.85,
                    top_k=30,
                    max_output_tokens=2200,
                )
            )
            text = getattr(response, "text", "")

            if not isinstance(text, str) or not text.strip():
                if attempt < max_retries - 1:
                    continue
                return fallback_text or "ไม่สามารถรับข้อมูลจาก AI ได้ในขณะนี้"

            if mode == "weather":
                cleaned = dedupe_weather_blocks(text)
            elif mode == "itinerary":
                cleaned = clean_itinerary_response(text)
            else:
                cleaned = strip_ai_meta_lines(text)

            if cleaned and cleaned.strip():
                return cleaned

        except Exception:
            if attempt < max_retries - 1:
                continue

    return fallback_text or "ไม่สามารถสร้างข้อมูลได้ในขณะนี้"

# ─── Session State ────────────────────────────────────────────────────────────
for key, default in {
    'main_res': '', 'gem_res': '', 'weather_res': '',
    'travel_info': '', 'gem_city': '', 'lang': 'TH',
    'generated': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

df_tour, df_fest = load_data()

# ─── UI Text ──────────────────────────────────────────────────────────────────
ui = {
    'TH': {
        'title': "วางแผนทริป", 'accent': "แบบสมาร์ท",
        'sub': "คัดกรองข้อมูลเทศกาลและอากาศเพื่อทริปที่สมบูรณ์แบบ",
        'btn': "🚀 สร้างแผนเดินทาง", 'dest': "เลือกจังหวัด",
        'days': "ไปกี่วัน", 'style': "สไตล์การเที่ยว",
        'weather_head': "พยากรณ์อากาศ",
        'styles': ["คาเฟ่และถ่ายรูป 📸", "ธรรมชาติและภูเขา ⛰️", "วัฒนธรรมและวัด 🛕",
                   "ตะลอนกินสตรีทฟู้ด 🍜", "พักผ่อนชิลล์ๆ 🧖", "สายบาร์และกลางคืน 🍸"],
        'budget': "ระดับงบประมาณ",
        'budget_styles': ['💰 สุดประหยัด', '💵 เที่ยวสบาย', '💎 เต็มที่ลักชู'],
        'download_btn': "ดาวน์โหลดแผน PDF",
        'spinner': "🤖 กำลังสร้างแผนเดินทาง...",
        'date_label': "วันเดินทาง",
        'main_label': "จุดหมายหลัก",
        'gem_label': "ทางเลือกใกล้เคียง",
        'map_header': "แผนที่สถานที่ในทริป",
        'no_map': "ยังไม่มีข้อมูลพิกัดสำหรับแสดงแผนที่",
        'no_weather': "ยังไม่มีข้อมูลสภาพอากาศ"
    }
}
t = ui['TH']

# ─── Hero ─────────────────────────────────────────────────────────────────────
col_title, col_lang = st.columns([3.2, 1])

with col_title:
    st.markdown(
        f'<div class="hero">'
        f'<h1 class="hero-title">{t["title"]} <span>{t["accent"]}</span></h1>'
        f'<p class="hero-subtitle">{t["sub"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_lang:
    st.write("")
    lang_options = ['TH', 'EN', 'CN']
    lang_labels = ['🇹🇭 ไทย', '🇬🇧 English', '🇨🇳 中文']
    selected_lang_index = lang_options.index(st.session_state.lang)

    new_lang_label = st.radio(
        "Language",
        options=lang_labels,
        index=selected_lang_index,
        horizontal=True,
        label_visibility="collapsed",
        key="lang_selector"
    )
    new_lang_code = lang_options[lang_labels.index(new_lang_label)]
    if new_lang_code != st.session_state.lang:
        st.session_state.lang = new_lang_code
        st.rerun()

# ─── Form ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="form-container">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2.5, 1.4, 2.6], gap="small")

with c1:
    province_df = df_tour[['ProvinceEN', 'ProvinceTH']].drop_duplicates().dropna(subset=['ProvinceEN', 'ProvinceTH'])
    province_df = province_df.sort_values(by='ProvinceTH')
    province_options = province_df['ProvinceEN'].tolist()

    def format_province(p_en):
        row = df_tour[df_tour['ProvinceEN'] == p_en]
        if not row.empty:
            val = row['ProvinceTH'].iloc[0]
            return str(val) if pd.notna(val) else p_en
        return str(p_en)

    province = st.selectbox(f"📍 {t['dest']}", options=province_options, format_func=format_province)
    t_date = st.date_input(f"📅 {t['date_label']}", datetime.now())

with c2:
    days = st.slider(f"☀️ {t['days']}", 1, 7, 3)

with c3:
    selected_style = st.multiselect(
        f"🎨 {t['style']}",
        options=t['styles'],
        default=[t['styles'][0]]
    )
    if not selected_style:
        selected_style = [t['styles'][0]]

    budget_level = st.selectbox(f"💰 {t['budget']}", options=t['budget_styles'], index=1)

st.markdown('</div>', unsafe_allow_html=True)

# ─── Generate Button ──────────────────────────────────────────────────────────
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])
with col_btn2:
    generate_clicked = st.button(t['btn'], use_container_width=True, type="primary")

if generate_clicked:
    city_info = df_tour[df_tour['ProvinceEN'] == province].iloc[0]
    start_date_str = t_date.strftime('%d %B %Y')
    end_date_str = (t_date + timedelta(days=days - 1)).strftime('%d %B %Y')

    st.session_state.main_res = ""
    st.session_state.gem_res = ""
    st.session_state.weather_res = ""
    st.session_state.travel_info = ""
    st.session_state.gem_city = ""
    st.session_state.generated = False

    if city_info['City_type_EN'] == 'Major City':
        nearest_secondary = find_nearest_secondary_city(province, city_info, df_tour)
        if nearest_secondary:
            st.session_state.gem_city = nearest_secondary

    with st.spinner(t['spinner']):
        style_str = ', '.join([
            s.split('📸')[0].split('⛰️')[0].split('🛕')[0].split('🍜')[0].split('🧖')[0].split('🍸')[0].strip()
            for s in selected_style
        ])
        budget_clean = budget_level.split()[1] if ' ' in budget_level else budget_level

        weather_locations = province
        if st.session_state.gem_city:
            weather_locations += f", {st.session_state.gem_city}"

        weather_fallback = fallback_weather_from_locations(weather_locations)

        w_prompt = f"""
ตอบเป็นภาษาไทยเท่านั้น
ห้ามอธิบายวิธีคิด
ห้ามมี placeholder
ห้ามซ้ำเมืองเดิม
ให้แต่ละเมืองมี 1 block เท่านั้น

สร้างพยากรณ์อากาศช่วงวันที่ {start_date_str} ถึง {end_date_str} สำหรับ {weather_locations}

ตอบเฉพาะรูปแบบนี้เท่านั้น:
📍 ชื่อเมือง
🌡️ อุณหภูมิ
☁️ สภาพอากาศสั้นๆ
💡 คำแนะนำการเดินทางสั้นๆ
"""
        st.session_state.weather_res = call_ai_strict(
            w_prompt,
            mode="weather",
            fallback_text=weather_fallback
        )

        main_fallback = ensure_itinerary_sections("", days)

        main_prompt = f"""
ตอบเป็นภาษาไทยเท่านั้น
ห้ามอธิบายวิธีคิด
ห้ามเขียน prompt หรือ checklist
เขียนให้อ่านง่าย กระชับ เป็นหัวข้อสรุป
เริ่มต้นทันที

สร้างแผนเที่ยว {days} วัน สำหรับ {province}
ช่วงวันที่ {start_date_str} ถึง {end_date_str}
สไตล์: {style_str}
งบประมาณ: {budget_clean}

ใช้รูปแบบนี้:
## 🌟 วันที่ 1
- 🌅 เช้า:
- 🍜 กลางวัน:
- 🌆 เย็น:

ทำต่อจนครบทุกวัน

ทุกสถานที่ต้องมีพิกัดแบบนี้:
**ชื่อสถานที่ (Lat: XX.XXXX, Lon: YY.YYYY)**

ตอนท้ายต้องมี:
## 💰 สรุปงบประมาณ
- ค่าที่พัก:
- ค่าอาหาร:
- ค่าเดินทาง:
- ค่าเข้าสถานที่และกิจกรรม:
- รวมโดยประมาณ:

## 🏨 ที่พักแนะนำ
- **ชื่อที่พัก (Lat: XX.XXXX, Lon: YY.YYYY)** : คำอธิบายสั้นๆ
- **ชื่อที่พัก (Lat: XX.XXXX, Lon: YY.YYYY)** : คำอธิบายสั้นๆ
"""
        st.session_state.main_res = call_ai_strict(
            main_prompt,
            mode="itinerary",
            fallback_text=main_fallback
        )
        st.session_state.main_res = clean_itinerary_response(st.session_state.main_res, days)

        if st.session_state.gem_city:
            gem_fallback = ensure_itinerary_sections("", days)
            gem_prompt = f"""
ตอบเป็นภาษาไทยเท่านั้น
ห้ามอธิบายวิธีคิด
ใช้ format เดียวกับจุดหมายหลักทุกอย่าง
เขียนให้อ่านง่าย กระชับ เป็นหัวข้อสรุป
บรรทัดแรกให้บอกเวลาและระยะทางการเดินทางจาก {province} ไป {st.session_state.gem_city} แบบสั้นๆ

จากนั้นสร้างแผนเที่ยว {days} วัน สำหรับ {st.session_state.gem_city}
ช่วงวันที่ {start_date_str} ถึง {end_date_str}
สไตล์: {style_str}
งบประมาณ: {budget_clean}

ใช้รูปแบบนี้:
## 🌟 วันที่ 1
- 🌅 เช้า:
- 🍜 กลางวัน:
- 🌆 เย็น:

ทำต่อจนครบทุกวัน

ทุกสถานที่ต้องมีพิกัดแบบนี้:
**ชื่อสถานที่ (Lat: XX.XXXX, Lon: YY.YYYY)**

ตอนท้ายต้องมี:
## 💰 สรุปงบประมาณ
- ค่าที่พัก:
- ค่าอาหาร:
- ค่าเดินทาง:
- ค่าเข้าสถานที่และกิจกรรม:
- รวมโดยประมาณ:

## 🏨 ที่พักแนะนำ
- **ชื่อที่พัก (Lat: XX.XXXX, Lon: YY.YYYY)** : คำอธิบายสั้นๆ
- **ชื่อที่พัก (Lat: XX.XXXX, Lon: YY.YYYY)** : คำอธิบายสั้นๆ
"""
            raw_gem = call_ai_strict(
                gem_prompt,
                mode="general",
                fallback_text=gem_fallback
            )

            if isinstance(raw_gem, str) and raw_gem.strip():
                raw_gem = normalize_spaces(raw_gem)
                lines = raw_gem.split('\n')
                first = lines[0] if lines else ''
                if any(kw in first.lower() for kw in ['ขับรถ', 'ระยะทาง', 'กิโลเมตร', 'ชั่วโมง', 'นาที']):
                    st.session_state.travel_info = first
                    st.session_state.gem_res = clean_itinerary_response('\n'.join(lines[1:]).strip(), days)
                else:
                    st.session_state.gem_res = clean_itinerary_response(raw_gem, days)

        st.session_state.generated = True
        st.success("✅ สร้างแผนเรียบร้อย!")

# ─── Combined Map + Weather ───────────────────────────────────────────────────
if st.session_state.generated:
    main_locations_df = parse_locations_from_markdown(st.session_state.main_res)
    gem_locations_df = parse_locations_from_markdown(st.session_state.gem_res)
    all_locations_df = pd.concat([main_locations_df, gem_locations_df], ignore_index=True).drop_duplicates()
    weather_blocks = parse_weather_blocks(st.session_state.weather_res)

    if (not all_locations_df.empty) or weather_blocks:
        st.markdown('<div class="combo-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="combo-title">🗺️ {t["map_header"]}</div>', unsafe_allow_html=True)

        left_col, right_col = st.columns([1.65, 1], gap="medium")

        with left_col:
            st.markdown('<div class="map-panel">', unsafe_allow_html=True)
            if not all_locations_df.empty:
                st.map(all_locations_df)
            else:
                st.info(t["no_map"])
            st.markdown('</div>', unsafe_allow_html=True)

        with right_col:
            # Build the entire HTML string first to ensure correct nesting
            weather_html_parts = ['<div class="weather-panel">']
            weather_html_parts.append(f'<div class="weather-panel-title">☁️ {t["weather_head"]}</div>')

            if weather_blocks:
                for w in weather_blocks:
                    weather_html_parts.append(f"""
                        <div class="weather-city-card">
                            <div class="weather-city-name">📍 {w['city']}</div>
                            <div class="weather-line">🌡️ {w['temp']}</div>
                            <div class="weather-line">☁️ {w['cond']}</div>
                            <div class="weather-line">💡 {w['tip']}</div>
                        </div>
                        """)
            else:
                weather_html_parts.append(f'<div class="weather-city-card"><div class="weather-line">{t["no_weather"]}</div></div>')

            weather_html_parts.append('</div>')
            st.markdown("".join(weather_html_parts), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ─── Result Cards ─────────────────────────────────────────────────────────────
if st.session_state.main_res:
    if st.session_state.gem_res:
        col_l, col_r = st.columns(2, gap="medium")

        with col_l:
            st.markdown(
                f'<div class="result-card">'
                f'<div class="card-label">{t["main_label"]}</div>'
                f'<h3>📍 {province}</h3>',
                unsafe_allow_html=True
            )
            st.markdown(st.session_state.main_res)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown(
                f'<div class="result-card gem-card">'
                f'<div class="card-label">{t["gem_label"]}</div>'
                f'<h3>📍 {st.session_state.gem_city}</h3>',
                unsafe_allow_html=True
            )
            if st.session_state.travel_info:
                st.markdown(
                    f'<p style="font-size:0.9rem;color:#666;background:#fff8f0;padding:0.7rem 1rem;'
                    f'border-radius:10px;margin-bottom:1rem;border-left:4px solid #ff9933;">'
                    f'🚗 {st.session_state.travel_info}</p>',
                    unsafe_allow_html=True
                )
            st.markdown(st.session_state.gem_res)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="result-card">'
            f'<div class="card-label">{t["main_label"]}</div>'
            f'<h3>📍 {province}</h3>',
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.main_res)
        st.markdown('</div>', unsafe_allow_html=True)

    content_dict = {
        'weather': st.session_state.weather_res,
        'main': st.session_state.main_res,
        'gem': st.session_state.gem_res,
        'gem_city': st.session_state.gem_city,
        'travel_info': st.session_state.travel_info
    }

    pdf_buffer = create_pdf(content_dict, province, st.session_state.lang)
    province_filename = province.replace(" ", "_")
    date_str = t_date.strftime('%Y%m%d')

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_dl1, col_dl2, col_dl3 = st.columns([2, 2, 2])
    with col_dl2:
        st.download_button(
            label=f"📥 {t['download_btn']}",
            data=pdf_buffer,
            file_name=f"trip_{province_filename}_{date_str}.pdf",
            mime="application/pdf",
            use_container_width=True
        )