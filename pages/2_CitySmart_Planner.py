import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io
import re
import math
import os
import urllib.request

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CitySmart Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif !important;
    color: #1a1a2e;
}
.stApp {
    background: linear-gradient(150deg, #eef6fb 0%, #e8f2f8 40%, #f2f4fb 100%);
    background-attachment: fixed;
}
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 1360px;
}
.element-container { margin-bottom: 0rem !important; }

/* ── Hero ── */
.hero { padding: 0.4rem 0 0.2rem 0 !important; }
.hero-title {
    font-family: 'Prompt', sans-serif;
    font-size: clamp(1.8rem, 3.5vw, 2.4rem);
    font-weight: 800;
    color: #12111a;
    line-height: 1.2;
    margin: 0 !important;
}
.hero-title span {
    background: #0077B6;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #6c6c6c;
    margin-top: 0.15rem !important;
    margin-bottom: 0 !important;
    max-width: 720px;
}

/* ── Language radio ── */
div[data-testid="stHorizontalBlock"] > div:has(.stRadio) {
    display: flex; justify-content: flex-end;
    align-items: flex-start; padding-top: 0.35rem;
}
.stRadio {
    background: rgba(255,255,255,0.85); border-radius: 100px; padding: 0.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08); display: inline-flex;
    backdrop-filter: blur(8px);
}
.stRadio > div { display: flex !important; flex-direction: row !important; gap: 0 !important; }
.stRadio > div > label {
    border-radius: 100px !important; padding: 0.48rem 1rem !important;
    margin: 0 !important; font-size: 0.86rem; font-weight: 500;
    color: #666; background: transparent !important; border: none !important;
}
.stRadio > div > label[data-baseweb="radio"] > div:first-child { display: none !important; }
.stRadio > div > label:has(input:checked) {
    background: #AED6F1 !important;
    color: #1E3D59 !important;
    box-shadow: 0 2px 8px rgba(174,214,241,0.5);
}

/* ── Form inputs ── */
.form-container { padding: 0.25rem 0 0.15rem 0 !important; }
.stSelectbox, .stMultiSelect, .stDateInput, .stSlider {
    margin-bottom: 0.4rem !important; margin-top: 0.1rem !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stDateInput > div > div {
    background: rgba(255,255,255,0.82) !important; border-radius: 12px !important;
    border: 1px solid rgba(0,119,182,0.14) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    backdrop-filter: blur(8px) !important;
}
label {
    font-weight: 600 !important; color: #1a1a2e !important;
    font-size: 0.92rem !important; margin-bottom: 0.12rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #AED6F1 !important;
    color: #1E3D59 !important; border: none !important;
    padding: 0.8rem 2.2rem !important; border-radius: 14px !important;
    font-weight: 700 !important; font-size: 1rem !important;
    font-family: 'Prompt', sans-serif !important;
    box-shadow: 0 4px 16px rgba(174,214,241,0.5) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(174,214,241,0.7) !important;
}
.stDownloadButton > button {
    background: #AED6F1 !important;
    color: #1E3D59 !important; border: none !important;
    padding: 0.75rem 1.5rem !important; border-radius: 14px !important;
    font-weight: 700 !important; width: 100% !important;
    font-family: 'Prompt', sans-serif !important;
}

/* ── Twin Cities Banner ── */
.twin-banner {
    background: rgba(0,119,182,0.07);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(0,119,182,0.18);
    border-radius: 14px;
    padding: 0.6rem 1.2rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #0077B6;
    flex-wrap: wrap;
}
.twin-arrow { color: #0077B6; font-size: 1.05rem; font-weight: 700; }
.twin-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 20px;
    letter-spacing: 0.4px;
}
.twin-badge.main { background: #0077B6; color: white; }
.twin-badge.sec  { background: linear-gradient(135deg,#FF6E40,#FF9A70); color: white; }

/* ── Vertical Timeline ── */
.timeline-wrap {
    position: relative;
    padding-left: 2.8rem;
}
.timeline-wrap::before {
    content: '';
    position: absolute;
    left: 1.05rem;
    top: 1.6rem;
    bottom: 1.6rem;
    width: 2px;
    background: #0077B6;
    border-radius: 2px;
}
.timeline-wrap.gem-wrap::before {
    background: linear-gradient(180deg, #FF6E40 0%, #FF9A70 60%, #FFD0BF 100%);
}
.timeline-item { position: relative; margin-bottom: 1rem; }
.timeline-dot {
    position: absolute;
    left: -2.2rem;
    top: 0.95rem;
    width: 2rem;
    height: 2rem;
    background: #0077B6;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    color: white;
    font-weight: 700;
    box-shadow: 0 2px 10px rgba(0,119,182,0.35);
    z-index: 1;
    border: 2.5px solid white;
}
.timeline-dot.gem-dot {
    background: linear-gradient(135deg, #FF6E40, #FF9A70);
    box-shadow: 0 2px 10px rgba(255,110,64,0.35);
}

/* Glassmorphism card */
.timeline-glass {
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 18px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 4px 24px rgba(0,119,182,0.07), 0 1px 4px rgba(0,0,0,0.04);
}
.timeline-glass.gem-glass {
    box-shadow: 0 4px 24px rgba(255,110,64,0.07), 0 1px 4px rgba(0,0,0,0.04);
}
.timeline-glass.budget-glass {
    background: linear-gradient(135deg, rgba(0,119,182,0.06), rgba(0,180,216,0.05));
    border-color: rgba(0,119,182,0.13);
}

.timeline-day-title {
    font-family: 'Prompt', sans-serif;
    font-size: 0.97rem;
    font-weight: 700;
    color: #1E3D59;
    margin: 0 0 0.5rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid rgba(0,119,182,0.1);
}
.timeline-glass.gem-glass .timeline-day-title {
    color: #FF6E40;
    border-bottom-color: rgba(255,110,64,0.1);
}

.timeline-slot {
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
    margin-bottom: 0.38rem;
    font-size: 0.89rem;
    line-height: 1.52;
}
.slot-icon { min-width: 1.4rem; text-align: center; flex-shrink: 0; }
.slot-content { flex: 1; color: #2a2a3e; }
.slot-badges { display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.22rem; }
.badge-tag {
    font-size: 0.68rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    background: #0077B6;
    color: white;
    letter-spacing: 0.3px;
    white-space: nowrap;
}
.badge-tag.gem-tag { background: linear-gradient(135deg, #FF6E40, #FF9A70); }

/* ── Budget rows ── */
.budget-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.25rem 0;
    border-bottom: 1px solid rgba(0,119,182,0.07);
    font-size: 0.87rem;
    color: #444;
}
.budget-row:last-child { border-bottom: none; }
.budget-row strong { color: #1a1a2e; font-weight: 600; }
.budget-total {
    padding-top: 0.4rem !important;
    font-weight: 700;
    font-size: 0.94rem !important;
    color: #0077B6 !important;
    border-bottom: none !important;
}
.budget-total strong { color: #0077B6 !important; font-weight: 800 !important; }

/* ── Map ── */
div[data-testid="stMap"] iframe,
div[data-testid="stMap"] > div {
    height: 380px !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

/* ── Alerts ── */
.stSuccess {
    background-color: #d4edda !important;
    border-left: 4px solid #28a745 !important;
    border-radius: 10px !important;
}
.stError {
    background-color: #f8d7da !important;
    border-left: 4px solid #dc3545 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── PDF Generation ───────────────────────────────────────────────────────────
_FONT_CACHE = os.path.join(os.path.expanduser('~'), '.cache', 'citysmart_fonts')
_SARABUN_REG  = os.path.join(_FONT_CACHE, 'Sarabun-Regular.ttf')
_SARABUN_BOLD = os.path.join(_FONT_CACHE, 'Sarabun-Bold.ttf')

def _ensure_fonts():
    os.makedirs(_FONT_CACHE, exist_ok=True)
    css_url = 'https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700'
    needed = {
        'Sarabun-Regular.ttf': (400, _SARABUN_REG),
        'Sarabun-Bold.ttf':    (700, _SARABUN_BOLD),
    }
    if all(os.path.exists(p) for _, p in needed.values()):
        return True
    try:
        req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            css = r.read().decode()
        for weight, dest in needed.values():
            if os.path.exists(dest):
                continue
            m = re.search(rf"font-weight: {weight}.*?url\(([^)]+)\)", css, re.DOTALL)
            if m:
                urllib.request.urlretrieve(m.group(1), dest)
        return all(os.path.exists(p) for _, p in needed.values())
    except Exception:
        return False

def _clean_text(text):
    """Strip emojis/non-printable; keep Thai, Latin, digits, punctuation."""
    cleaned = re.sub(r'[^ -~฀-๿ -ÿ]', '', str(text))
    return re.sub(r'\s+', ' ', cleaned).strip()

class _ThaiFPDF(FPDF):
    """FPDF subclass with Sarabun font and convenience helpers."""
    _fonts_added = False

    def setup_fonts(self):
        if not _ThaiFPDF._fonts_added:
            if os.path.exists(_SARABUN_REG):
                self.add_font('Sarabun', '',  _SARABUN_REG)
            if os.path.exists(_SARABUN_BOLD):
                self.add_font('Sarabun', 'B', _SARABUN_BOLD)
            _ThaiFPDF._fonts_added = True
        self._use_sarabun = os.path.exists(_SARABUN_REG)

    def font_reg(self, size):
        self.set_font('Sarabun' if self._use_sarabun else 'Helvetica', size=size)

    def font_bold(self, size):
        self.set_font('Sarabun' if self._use_sarabun else 'Helvetica', style='B', size=size)

    def header(self):
        pass  # no auto-header

    def section_heading(self, text, color=(0, 119, 182)):
        self.set_text_color(*color)
        self.font_bold(13)
        self.ln(4)
        self.multi_cell(0, 8, _clean_text(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(26, 26, 46)
        self.ln(1)

    def body_line(self, text, indent=0, bold=False):
        if bold:
            self.font_bold(10)
        else:
            self.font_reg(10)
        if indent:
            self.set_x(self.get_x() + indent)
        self.multi_cell(0, 6.5, _clean_text(text),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def render_markdown(self, content):
        for raw in str(content).split('\n'):
            line = raw.strip()
            if not line:
                self.ln(2)
                continue
            if line.startswith('## ') or line.startswith('# '):
                t = re.sub(r'\*+', '', line.lstrip('#')).strip()
                self.section_heading(t, color=(0, 119, 182))
            elif line.startswith('- ') or line.startswith('* '):
                t = re.sub(r'\*+', '', line[2:]).strip()
                self.body_line('  •  ' + t, indent=4)
            else:
                t = re.sub(r'\*+', '', line.replace('#', '')).strip()
                if t:
                    self.body_line(t)

def create_pdf(content_dict, province, lang='TH'):
    _ensure_fonts()
    _ThaiFPDF._fonts_added = False  # reset so fonts are re-added per buffer

    pdf = _ThaiFPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.setup_fonts()

    # ── Title block ──
    pdf.set_fill_color(0, 119, 182)
    pdf.rect(0, 0, 210, 32, style='F')
    pdf.set_text_color(255, 255, 255)
    pdf.font_bold(18)
    title_text = f'แผนการเดินทาง: {province}' if lang == 'TH' else f'Travel Plan: {province}'
    pdf.set_xy(20, 8)
    pdf.cell(0, 10, _clean_text(title_text),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.font_reg(9)
    pdf.set_x(20)
    pdf.cell(0, 6, f"สร้างเมื่อ: {datetime.now().strftime('%d %B %Y')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(26, 26, 46)
    pdf.ln(6)

    # ── Weather ──
    if content_dict.get('weather'):
        lbl = 'สภาพอากาศ' if lang == 'TH' else 'Weather Forecast'
        pdf.section_heading(lbl)
        pdf.render_markdown(content_dict['weather'])
        pdf.ln(3)

    # ── Main itinerary ──
    main_lbl = f'แผนเที่ยว: {province}' if lang == 'TH' else f'Main Destination: {province}'
    pdf.section_heading(main_lbl)
    if content_dict.get('main'):
        pdf.render_markdown(content_dict['main'])

    # ── Gem city ──
    if content_dict.get('gem') and content_dict.get('gem_city'):
        pdf.add_page()
        gem_lbl = f"ทางเลือกใกล้เคียง: {content_dict['gem_city']}" if lang == 'TH' \
                  else f"Nearby Alternative: {content_dict['gem_city']}"
        pdf.section_heading(gem_lbl)
        if content_dict.get('travel_info'):
            pdf.body_line(content_dict['travel_info'])
            pdf.ln(2)
        pdf.render_markdown(content_dict['gem'])

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# ─── AI Setup ─────────────────────────────────────────────────────────────────
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    gemma_model = genai.GenerativeModel('gemma-4-31b-it')
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ AI ได้: {e}")
    st.stop()

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df_t = pd.read_csv('data/master_tourism_analysis.csv')
        df_f = pd.read_excel('data/Thailand_Festival_Master.xlsx')
        df_fe = pd.read_csv('data/Thailand_Festival_With_Events.csv')
        df_t['ProvinceEN'] = df_t['ProvinceEN'].astype(str).str.strip()
        df_t['Region_EN'] = df_t['Region_EN'].astype(str).str.strip()
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
        return df_t, df_f, df_fe
    except FileNotFoundError as e:
        st.error(f"ไม่พบไฟล์ข้อมูล: {e}")
        st.stop()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
        st.stop()

# ─── Province Coordinates ─────────────────────────────────────────────────────
PROVINCE_COORDS = {
    # Bangkok Metropolitan
    'Bangkok': (13.7563, 100.5018),
    'Nonthaburi': (13.8621, 100.5144),
    'Pathum Thani': (14.0208, 100.5232),
    'Samut Prakan': (13.5991, 100.5998),
    'Samut Sakhon': (13.5477, 100.2739),
    'Samut Songkhram': (13.4098, 100.0023),
    # Southern
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
    # Northern
    'Chiang Mai': (18.7883, 98.9853),
    'Chiang Rai': (19.9105, 99.8406),
    'Lampang': (18.2888, 99.4908),
    'Lamphun': (18.5746, 99.0087),
    'Mae Hong Son': (19.3013, 97.9654),
    'Nan': (18.7756, 100.7730),
    'Phrae': (18.1459, 100.1410),
    'Phayao': (19.1665, 99.9018),
    'Kamphaeng Phet': (16.4823, 99.5220),
    'Phetchabun': (16.4189, 101.1552),
    'Phichit': (16.4418, 100.3494),
    'Phitsanulok': (16.8219, 100.2659),
    'Sukhothai': (17.0056, 99.8264),
    'Tak': (16.8847, 99.1258),
    'Uttaradit': (17.6255, 100.0996),
    # Northeastern
    'Loei': (17.4860, 101.7223),
    'Khon Kaen': (16.4419, 102.8350),
    'Udon Thani': (17.4138, 102.7870),
    'Ubon Ratchathani': (15.2447, 104.8472),
    'Nakhon Ratchasima': (14.9799, 102.0977),
    'Amnat Charoen': (15.8656, 104.6257),
    'Bueng Kan': (18.3609, 103.6461),
    'Buri Ram': (14.9933, 103.1029),
    'Chaiyaphum': (15.8068, 102.0314),
    'Kalasin': (16.4315, 103.5060),
    'Maha Sarakham': (16.1851, 103.3001),
    'Mukdahan': (16.5432, 104.7238),
    'Nakhon Phanom': (17.3924, 104.7738),
    'Nong Bua Lam Phu': (17.2042, 102.4260),
    'Nong Khai': (17.8782, 102.7410),
    'Roi Et': (16.0538, 103.6520),
    'Sakon Nakhon': (17.1551, 104.1348),
    'Si Sa Ket': (15.1186, 104.3220),
    'Surin': (14.8824, 103.4932),
    'Yasothon': (15.7925, 104.1447),
    # Eastern
    'Chon Buri': (13.3611, 100.9847),
    'Rayong': (12.6814, 101.2816),
    'Chanthaburi': (12.6112, 102.1038),
    'Trat': (12.2428, 102.5175),
    'Chachoengsao': (13.6905, 101.0779),
    'Nakhon Nayok': (14.2042, 101.2135),
    'Prachin Buri': (14.0579, 101.3706),
    'Sa Kaeo': (13.8241, 102.0642),
    # Central & Western
    'Prachuap Khiri Khan': (11.8124, 99.7973),
    'Kanchanaburi': (14.0228, 99.5328),
    'Ratchaburi': (13.5283, 99.8134),
    'Phetchaburi': (13.1112, 99.9447),
    'Phra Nakhon Si Ayutthaya': (14.3532, 100.5689),
    'Ang Thong': (14.5896, 100.4554),
    'Chai Nat': (15.1856, 100.1251),
    'Lop Buri': (14.7995, 100.6534),
    'Nakhon Pathom': (13.8199, 100.0643),
    'Nakhon Sawan': (15.6780, 100.1167),
    'Saraburi': (14.5289, 100.9107),
    'Sing Buri': (14.8918, 100.3965),
    'Suphan Buri': (14.4744, 100.1177),
    'Uthai Thani': (15.3800, 100.0247),
}

REGION_NEARBY_FALLBACK = {
    'Southern': ['Phang Nga', 'Krabi', 'Ranong', 'Trang', 'Satun', 'Phatthalung', 'Nakhon Si Thammarat', 'Surat Thani', 'Chumphon'],
    'Northern': ['Lamphun', 'Lampang', 'Phrae', 'Nan', 'Phayao', 'Mae Hong Son', 'Chiang Rai', 'Uttaradit', 'Tak', 'Sukhothai'],
    'Northeastern': ['Loei', 'Roi Et', 'Kalasin', 'Chaiyaphum', 'Bueng Kan', 'Nakhon Phanom', 'Mukdahan', 'Sakon Nakhon', 'Nong Khai', 'Yasothon', 'Amnat Charoen', 'Si Sa Ket', 'Surin', 'Buri Ram', 'Maha Sarakham'],
    'Central': ['Kanchanaburi', 'Ratchaburi', 'Phetchaburi', 'Prachuap Khiri Khan', 'Nakhon Pathom', 'Ang Thong', 'Sing Buri', 'Chai Nat', 'Lop Buri', 'Saraburi', 'Suphan Buri', 'Uthai Thani', 'Nakhon Sawan'],
    'Western': ['Kanchanaburi', 'Uthai Thani', 'Tak', 'Ratchaburi'],
    'Eastern': ['Chanthaburi', 'Trat', 'Nakhon Nayok', 'Prachin Buri', 'Sa Kaeo', 'Chachoengsao'],
    'Bangkok Metropolitan': ['Nonthaburi', 'Pathum Thani', 'Samut Prakan', 'Samut Sakhon', 'Samut Songkhram'],
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

def get_twin_city_stats(main_prov, gem_prov, df_tour):
    """Return distance (km), drive time (hr, min), and revenue data for both cities."""
    stats = {}
    main_coord = PROVINCE_COORDS.get(main_prov)
    gem_coord  = PROVINCE_COORDS.get(gem_prov)
    if main_coord and gem_coord:
        dist_km = haversine_km(main_coord[0], main_coord[1], gem_coord[0], gem_coord[1])
        drive_min = int(dist_km / 90 * 60)        # assume 90 km/h highway avg
        stats['dist_km']   = round(dist_km)
        stats['drive_hr']  = drive_min // 60
        stats['drive_min'] = drive_min % 60

    for key, prov in [('main', main_prov), ('gem', gem_prov)]:
        rows = df_tour[df_tour['ProvinceEN'] == prov]
        if not rows.empty:
            stats[f'{key}_revenue']  = rows['total_revenue'].mean()
            stats[f'{key}_visitors'] = rows['total_visitors'].mean()
            stats[f'{key}_type']     = rows['City_type_EN'].iloc[0]
    return stats

# ─── Feature A: When to Go ────────────────────────────────────────────────────
_MONTH_ORDER = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
_MONTH_TH    = {'Jan':'ม.ค.','Feb':'ก.พ.','Mar':'มี.ค.','Apr':'เม.ย.','May':'พ.ค.',
                'Jun':'มิ.ย.','Jul':'ก.ค.','Aug':'ส.ค.','Sep':'ก.ย.','Oct':'ต.ค.',
                'Nov':'พ.ย.','Dec':'ธ.ค.'}
_MONTH_FULL_TH = {'Jan':'มกราคม','Feb':'กุมภาพันธ์','Mar':'มีนาคม','Apr':'เมษายน',
                  'May':'พฤษภาคม','Jun':'มิถุนายน','Jul':'กรกฎาคม','Aug':'สิงหาคม',
                  'Sep':'กันยายน','Oct':'ตุลาคม','Nov':'พฤศจิกายน','Dec':'ธันวาคม'}

def get_seasonal_stats(province, df):
    sub = df[df['ProvinceEN'] == province].copy()
    if sub.empty:
        return None
    monthly = sub.groupby('Month').agg(
        visitors=('total_visitors', 'mean'),
        revenue=('total_revenue', 'mean'),
        occupancy=('occupancy_rate', 'mean')
    ).reset_index()
    monthly['month_idx'] = monthly['Month'].map({m: i for i, m in enumerate(_MONTH_ORDER)})
    return monthly.sort_values('month_idx').reset_index(drop=True)

def render_when_to_go(province, sel_month_abbr, df, lang='TH'):
    import plotly.graph_objects as go
    stats = get_seasonal_stats(province, df)
    if stats is None or stats.empty:
        return None, None

    month_labels = [_MONTH_TH.get(m, m) if lang == 'TH' else m for m in stats['Month']]
    visitors = stats['visitors'].values
    max_v = visitors.max()

    # Rank-based classification: top 4 = busy, mid 4 = moderate, bottom 4 = quiet
    # Guarantees every province always has all three categories
    import numpy as np
    n = len(visitors)
    ranks = np.argsort(np.argsort(visitors))   # rank 0 = lowest
    top_cut    = n - 4      # ranks >= top_cut → busy
    bottom_cut = 4          # ranks < bottom_cut → quiet

    colors, season_labels = [], []
    for rank in ranks:
        if rank >= top_cut:
            colors.append('#e74c3c'); season_labels.append('คนแน่น' if lang == 'TH' else 'Busy')
        elif rank < bottom_cut:
            colors.append('#27ae60'); season_labels.append('คนน้อย' if lang == 'TH' else 'Quiet')
        else:
            colors.append('#f39c12'); season_labels.append('พอดี' if lang == 'TH' else 'Moderate')

    sel_th = _MONTH_TH.get(sel_month_abbr, sel_month_abbr) if lang == 'TH' else sel_month_abbr
    try:
        sel_idx = month_labels.index(sel_th)
    except ValueError:
        sel_idx = -1

    # Keep original color; dim non-selected bars to 35% opacity
    bar_colors = colors[:]
    bar_opacity = [1.0 if i == sel_idx else 0.35 for i in range(len(colors))]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_labels, y=visitors,
        marker_color=bar_colors,
        marker_opacity=bar_opacity,
        marker_line_width=0,
        customdata=list(zip(season_labels, stats['occupancy'].values)),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'นักท่องเที่ยว: %{y:,.0f} คน<br>'
            'สถานะ: %{customdata[0]}<br>'
            'Occupancy: %{customdata[1]:.1f}%<extra></extra>'
        ) if lang == 'TH' else (
            '<b>%{x}</b><br>'
            'Visitors: %{y:,.0f}<br>'
            'Season: %{customdata[0]}<br>'
            'Occupancy: %{customdata[1]:.1f}%<extra></extra>'
        )
    ))

    # Arrow annotation pointing at selected bar
    if sel_idx >= 0:
        ann_lbl = '📅 เดือนของคุณ' if lang == 'TH' else '📅 Your month'
        fig.add_annotation(
            x=month_labels[sel_idx],
            y=visitors[sel_idx],
            text=ann_lbl,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='#333',
            ax=0, ay=-32,
            font=dict(size=10, color='#333'),
            bgcolor='rgba(255,255,255,0.85)',
            borderpad=3,
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=28, b=0),
        height=170,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', showticklabels=False),
        showlegend=False,
        bargap=0.18,
    )

    sel_visitors = int(visitors[sel_idx]) if sel_idx >= 0 else None
    sel_season   = season_labels[sel_idx] if sel_idx >= 0 else ''
    low_months   = [month_labels[i] for i, r in enumerate(ranks) if r < bottom_cut]
    peak_months  = [month_labels[i] for i, r in enumerate(ranks) if r >= top_cut]

    return fig, {
        'sel_visitors': sel_visitors, 'sel_season': sel_season,
        'sel_month': sel_th, 'low': low_months, 'peak': peak_months,
        'sel_idx': sel_idx,
    }

# ─── Feature B: Budget Reality ────────────────────────────────────────────────
def get_spend_per_visitor(province, df):
    sub = df[df['ProvinceEN'] == province]
    if sub.empty:
        return None
    avg_rev = sub['total_revenue'].mean()   # unit: million baht
    avg_vis = sub['total_visitors'].mean()
    if avg_vis > 0:
        return round((avg_rev * 1_000_000) / avg_vis)
    return None

# ─── Feature D: Loop Route Builder ────────────────────────────────────────────
def find_loop_stops(main_province, df, n=2, max_km=350):
    base = PROVINCE_COORDS.get(main_province)
    if not base:
        return []
    cands = df[
        (df['City_type_EN'] == 'Secondary City') &
        (df['ProvinceEN'] != main_province)
    ][['ProvinceEN', 'ProvinceTH']].drop_duplicates()

    scored = []
    for _, row in cands.iterrows():
        c = row['ProvinceEN']
        crd = PROVINCE_COORDS.get(c)
        if not crd:
            continue
        d = haversine_km(base[0], base[1], crd[0], crd[1])
        if d <= max_km:
            scored.append({'en': c, 'th': str(row['ProvinceTH']), 'dist_from_main': round(d)})
    scored.sort(key=lambda x: x['dist_from_main'])
    # Add distance from stop to stop for the loop
    result = scored[:n]
    for i, stop in enumerate(result):
        crd = PROVINCE_COORDS[stop['en']]
        if i == 0:
            prev_crd = base
        else:
            prev_crd = PROVINCE_COORDS[result[i-1]['en']]
        stop['dist_from_prev'] = round(haversine_km(prev_crd[0], prev_crd[1], crd[0], crd[1]))
    # last leg back
    if result:
        last_crd = PROVINCE_COORDS[result[-1]['en']]
        result[-1]['dist_back'] = round(haversine_km(last_crd[0], last_crd[1], base[0], base[1]))
    return result

def extract_budget_total(text):
    """Parse the '- รวมโดยประมาณ' or '- Total estimate' bullet line → (lo_thb, hi_thb).

    Anchors to line-start with a dash so sub-item notes in parentheses
    (e.g. 'ค่าเดินทาง ... (รวมโดยประมาณต่อวัน: 666 - 1,333 บาท)')
    are never mistakenly matched instead of the actual total line.
    Returns (None, None) when not found or unparseable.
    """
    if not isinstance(text, str):
        return None, None

    # Range: - รวมโดยประมาณ: 8,000 - 15,500 บาท
    m = re.search(
        r'^\s*-\s*(?:รวมโดยประมาณ|Total estimate)[^\d]*?([\d,]+)\s*[-–]\s*([\d,]+)',
        text, re.IGNORECASE | re.MULTILINE
    )
    if m:
        lo = int(m.group(1).replace(',', ''))
        hi = int(m.group(2).replace(',', ''))
        return lo, hi

    # Single value: - รวมโดยประมาณ: 12,000 บาท
    m2 = re.search(
        r'^\s*-\s*(?:รวมโดยประมาณ|Total estimate)[^\d]*([\d,]+)',
        text, re.IGNORECASE | re.MULTILINE
    )
    if m2:
        v = int(m2.group(1).replace(',', ''))
        return v, v

    return None, None

# ─── Cleaning & Parsing ───────────────────────────────────────────────────────
WEATHER_TEMPLATE_MARKERS = [
    # with brackets — any bracketed placeholder
    '[City Name]', '[City]', '[Temperature]', '[Temp', '[Weather]',
    '[Short weather condition]', '[Short travel advice]', '[Travel tip]',
    '[actual city', '[actual temp', '[actual weather', '[actual travel',
    # without brackets (AI echoing the format example literally)
    'City Name', 'Temperature', 'Short weather condition',
    'Short weather', 'Short travel tip', 'Short travel advice',
    'actual city name', 'actual temperature', 'actual weather description',
    'actual travel tip',
]

# Template city names to reject at block-parse level
_WEATHER_TEMPLATE_CITIES = {
    'city name', 'ชื่อเมือง', '[city name]',
    'city', '[city]', 'your city', 'province name',
    'actual city name', 'actual city',
}

AI_META_PATTERNS = [
    # ── Format / structure meta ──
    r'^Date:', r'^City 1:', r'^City 2:', r'^Temp:', r'^Condition:', r'^Tip:',
    r'^Constraints:', r'^Check', r'^No English\?', r'^No parentheses\?',
    r'^Thai only[\.\?]', r'^Format followed\?', r'^Ready to output',
    r'^Final verification', r'^Self-Correction', r'^Writing Style:',
    r'^CRITICAL', r'^STRUCTURE:', r'^FORMAT:', r'^Example:',
    # ── Echoed system-prompt / persona declaration ──
    r'^Professional\s+Tourism',
    r'^Tourism\s+Business\s+Consultant',
    r'^Do not explain',
    r'^Thai only\.',
    r'^Targeting\s+(foreign|domestic|local)',
    r'^Collaboration\s+with',
    r'^Visual\s+marketing',
    r'^Early\s+bird\s+(breakfast|brunch|discount)',
    r'themes\.\s*$',
    r'^".*"\s+for\s+(Chinese|foreign|Thai)',
    # ── English chain-of-thought ──
    r'^Wait[,\s—]', r'^Wait\.',
    r'^Hmm[,\s—]', r'^Hmm\.',
    r'^Let me ', r"^Let's ",
    r'^Actually[,\s—]', r'^Actually\.',
    r'^I think', r'^I need', r'^I should', r"^I'll ", r'^I am going',
    r'^Okay[,\s—]', r'^OK[,\s—]', r'^Alright[,\s—]',
    r'^Now[,\s—]', r'^Now let', r'^Now I',
    r'^So[,\s—]', r'^So the', r'^So I',
    r'^First[,\s—]', r'^First let', r'^First I',
    r'^Note:', r'^Note that', r'^Note —',
    r'^Remember[:\s—]', r'^Important[:\s—]',
    r'^Re-reading', r'^Re-check', r'^Rechecking',
    r'^Looking at', r'^Based on the prompt',
    r'^The prompt says', r'^The instructions',
    r'^Correction:', r'^Revised:', r'^Updated:',
    r'^Self-correction', r'^Double.check',
    # ── Thai chain-of-thought ──
    r'^รอก่อน', r'^ขอคิด', r'^ลองคิด', r'^คิดดู',
    r'^ตรวจสอบ', r'^ทบทวน', r'^แก้ไข', r'^ขอแก้',
    r'^อ่าน prompt', r'^prompt บอก', r'^คำสั่งบอก',
    r'^ตอนนี้', r'^เริ่มต้น', r'^สรุปแล้ว',
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

def strip_coords_for_display(text):
    """Remove (Lat:…,Lon:…) and the entire ## 🗺️ พิกัด section before rendering."""
    if not isinstance(text, str):
        return text
    text = re.sub(r'\n?##\s*🗺️\s*พิกัด.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\s*\(Lat:\s*-?\d+\.?\d*,\s*Lon:\s*-?\d+\.?\d*\)', '', text)
    return text.strip()

def _md_inline(text):
    """Convert **bold** and *italic* markdown to HTML inline tags."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', str(text))
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    return text

def build_day_cards_html(raw_text, gem=False):
    """Parse markdown itinerary into styled HTML day-cards, budget card, and hotel card."""
    text = strip_coords_for_display(raw_text)
    if not text:
        return ''

    accent = '#FF6E40' if gem else '#1E3D59'
    card_cls = 'day-card gem' if gem else 'day-card'
    sections = re.split(r'\n(?=##\s)', text.strip())
    parts = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.split('\n')
        header = lines[0].strip()
        body = [l.strip() for l in lines[1:] if l.strip()]

        # ── วันที่ X ──
        if re.match(r'^##\s*🌟', header):
            day_label = re.sub(r'^##\s*🌟\s*', '', header).strip()
            html = f'<div class="{card_cls}"><div class="day-title">🌟 {_md_inline(day_label)}</div>'
            for bl in body:
                m = re.match(r'^-\s*(🌅|🍜|🌆)\s*([^:：]*[：:]?)\s*(.*)', bl)
                if m:
                    icon, label, desc = m.group(1), m.group(2).strip().rstrip(':：'), m.group(3).strip()
                    label_html = f'<span class="meal-label">{label}:</span> ' if label else ''
                    html += (f'<div class="meal-row">'
                             f'<span class="meal-icon">{icon}</span>'
                             f'<div class="meal-content">{label_html}{_md_inline(desc)}</div>'
                             f'</div>')
                elif bl.startswith('- ') or bl.startswith('* '):
                    html += (f'<div class="meal-row"><span class="meal-icon" style="color:#aaa;">•</span>'
                             f'<div class="meal-content">{_md_inline(bl[2:])}</div></div>')
                else:
                    html += f'<p style="font-size:0.87rem;color:#666;margin:0.15rem 0;">{_md_inline(bl)}</p>'
            html += '</div>'
            parts.append(html)

        # ── สรุปงบประมาณ ──
        elif re.match(r'^##\s*💰', header):
            html = '<div class="budget-card"><div class="budget-title">💰 สรุปงบประมาณ</div>'
            for bl in body:
                content = bl[2:].strip() if (bl.startswith('- ') or bl.startswith('* ')) else bl
                idx = content.find(':')
                if idx > 0:
                    label = content[:idx].strip()
                    value = _md_inline(content[idx+1:].strip())
                    is_total = any(k in label for k in ['รวม', 'total', 'Total'])
                    cls = ' budget-total' if is_total else ''
                    html += (f'<div class="budget-row{cls}">'
                             f'<span>{label}</span><strong>{value}</strong></div>')
                elif content:
                    html += f'<div class="budget-row">{_md_inline(content)}</div>'
            html += '</div>'
            parts.append(html)

        # ── ที่พักแนะนำ ──
        elif re.match(r'^##\s*🏨', header):
            html = f'<div class="hotel-card"><div class="budget-title" style="color:{accent};">🏨 ที่พักแนะนำ</div>'
            for bl in body:
                content = bl[2:].strip() if (bl.startswith('- ') or bl.startswith('* ')) else bl
                if content:
                    html += (f'<div class="meal-row">'
                             f'<span class="meal-icon">🏠</span>'
                             f'<div class="meal-content">{_md_inline(content)}</div></div>')
            html += '</div>'
            parts.append(html)

    return ''.join(parts)

# ─── Activity Badge Detection ─────────────────────────────────────────────────
BADGE_RULES = [
    (['คาเฟ่', 'กาแฟ', 'coffee', 'cafe'],                   '#Cafe'),
    (['วัด', 'โบสถ์', 'วิหาร', 'พระ', 'เจดีย์'],            '#วัด'),
    (['ตลาด', 'ไนท์', 'night market', 'ถนนคนเดิน'],         '#ตลาด'),
    (['ทะเล', 'ชายหาด', 'หาด', 'beach', 'อ่าว', 'เกาะ'],    '#ทะเล'),
    (['ภูเขา', 'น้ำตก', 'ป่า', 'ดอย', 'ธรรมชาติ'],          '#ธรรมชาติ'),
    (['ร้านอาหาร', 'อาหาร', 'กิน', 'ซีฟู้ด', 'สตรีทฟู้ด'], '#Food'),
    (['ช้อปปิ้ง', 'ห้าง', 'ของที่ระลึก', 'ตลาดน้ำ'],        '#Shopping'),
    (['พักผ่อน', 'ผ่อนคลาย', 'สปา', 'นวด', 'ชิล'],          '#Chilled'),
    (['กิจกรรม', 'ผจญภัย', 'ดำน้ำ', 'พาย', 'ไต่'],          '#Adventure'),
    (['พิพิธภัณฑ์', 'ศิลปะ', 'ประวัติ', 'วัฒนธรรม'],        '#Culture'),
    (['พระอาทิตย์', 'วิว', 'ชมวิว', 'จุดชม', 'วิวทะเล'],    '#Scenic'),
]

def detect_badges(text, gem=False):
    text_lower = str(text).lower()
    found = []
    for keywords, badge in BADGE_RULES:
        if any(kw in text_lower for kw in keywords) and badge not in found:
            found.append(badge)
        if len(found) == 3:
            break
    return found

def build_timeline_html(raw_text, gem=False):
    """Render itinerary as a vertical glassmorphism timeline with activity badge tags."""
    text = strip_coords_for_display(raw_text)
    if not text:
        return ''

    accent   = '#FF6E40' if gem else '#1E3D59'
    wrap_cls = 'timeline-wrap gem-wrap' if gem else 'timeline-wrap'
    dot_cls  = 'timeline-dot gem-dot'   if gem else 'timeline-dot'
    glass_cls = 'timeline-glass gem-glass' if gem else 'timeline-glass'
    tag_cls  = 'badge-tag gem-tag'      if gem else 'badge-tag'

    sections = re.split(r'\n(?=##\s)', text.strip())
    parts = [f'<div class="{wrap_cls}">']

    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines  = section.split('\n')
        header = lines[0].strip()
        body   = [l.strip() for l in lines[1:] if l.strip()]

        # ── Day card ──────────────────────────────────────────────────────────
        if re.match(r'^##\s*🌟', header):
            day_label = re.sub(r'^##\s*🌟\s*', '', header).strip()
            m_num = re.search(r'(\d+)', day_label)
            dot_content = m_num.group(1) if m_num else '●'

            parts.append('<div class="timeline-item">')
            parts.append(f'<div class="{dot_cls}">{dot_content}</div>')
            parts.append(f'<div class="{glass_cls}">')
            parts.append(f'<div class="timeline-day-title">🌟 {_md_inline(day_label)}</div>')

            for bl in body:
                m = re.match(r'^-\s*(🌅|🍜|🌆)\s*([^:：]*[：:]?)\s*(.*)', bl)
                if m:
                    icon  = m.group(1)
                    label = m.group(2).strip().rstrip(':：')
                    desc  = m.group(3).strip()
                    badges = detect_badges(desc, gem)
                    b_html = ''.join(f'<span class="{tag_cls}">{b}</span>' for b in badges)
                    b_wrap = f'<div class="slot-badges">{b_html}</div>' if b_html else ''
                    if label:
                        _t = re.match(r'^(.*?)\s+(\d{1,2}:\d{2}.*)', label)
                        if _t:
                            _period = _t.group(1).strip()
                            _time   = _t.group(2).strip()
                            l_part  = (f'<strong style="color:#1E3D59;">{_period}:</strong> '
                                       f'<span style="color:#444;font-weight:400;">{_time}</span> ')
                        else:
                            l_part = f'<strong style="color:#1E3D59;">{label}:</strong> '
                    else:
                        l_part = ''
                    parts.append(
                        f'<div class="timeline-slot">'
                        f'<span class="slot-icon">{icon}</span>'
                        f'<div class="slot-content">{l_part}{_md_inline(desc)}{b_wrap}</div>'
                        f'</div>'
                    )
                elif bl.startswith('- ') or bl.startswith('* '):
                    content = bl[2:].strip()
                    badges  = detect_badges(content, gem)
                    b_html  = ''.join(f'<span class="{tag_cls}">{b}</span>' for b in badges)
                    b_wrap  = f'<div class="slot-badges">{b_html}</div>' if b_html else ''
                    parts.append(
                        f'<div class="timeline-slot">'
                        f'<span class="slot-icon" style="color:#aaa;">•</span>'
                        f'<div class="slot-content">{_md_inline(content)}{b_wrap}</div>'
                        f'</div>'
                    )
                else:
                    parts.append(
                        f'<p style="font-size:0.86rem;color:#666;margin:0.1rem 0;">'
                        f'{_md_inline(bl)}</p>'
                    )
            parts.append('</div></div>')

        # ── Budget ────────────────────────────────────────────────────────────
        elif re.match(r'^##\s*💰', header):
            parts.append('<div class="timeline-item">')
            parts.append(f'<div class="{dot_cls}" style="font-size:0.72rem;">💰</div>')
            parts.append(f'<div class="{glass_cls} budget-glass">')
            parts.append('<div class="timeline-day-title">💰 สรุปงบประมาณ</div>')
            for bl in body:
                content = bl[2:].strip() if (bl.startswith('- ') or bl.startswith('* ')) else bl
                idx = content.find(':')
                if idx > 0:
                    label = content[:idx].strip()
                    value = _md_inline(content[idx+1:].strip())
                    is_total = any(k in label for k in ['รวม', 'total', 'Total'])
                    row_cls  = ' budget-total' if is_total else ''
                    parts.append(
                        f'<div class="budget-row{row_cls}">'
                        f'<span>{label}</span><strong>{value}</strong></div>'
                    )
                elif content:
                    parts.append(f'<div class="budget-row">{_md_inline(content)}</div>')
            parts.append('</div></div>')

        # ── Hotel ─────────────────────────────────────────────────────────────
        elif re.match(r'^##\s*🏨', header):
            parts.append('<div class="timeline-item">')
            parts.append(f'<div class="{dot_cls}" style="font-size:0.72rem;">🏨</div>')
            parts.append(f'<div class="{glass_cls}">')
            parts.append(
                f'<div class="timeline-day-title" style="color:{accent};">🏨 ที่พักแนะนำ</div>'
            )
            for bl in body:
                content = bl[2:].strip() if (bl.startswith('- ') or bl.startswith('* ')) else bl
                if content:
                    parts.append(
                        f'<div class="timeline-slot">'
                        f'<span class="slot-icon">🏠</span>'
                        f'<div class="slot-content">{_md_inline(content)}</div>'
                        f'</div>'
                    )
            parts.append('</div></div>')

    parts.append('</div>')
    return ''.join(parts)

def normalize_spaces(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

_COT_KEYWORDS = [
    'wait', 'hmm', 'let me', "let's", 'actually', 'i think', 'i need',
    'i should', 'okay', 'alright', 'now let', 'so the', 'first let',
    'the prompt', 'double-check', 'rechecking', 'looking at', 'based on',
    'correction', 'revised', 'รอก่อน', 'ขอคิด', 'ลองคิด', 'ตรวจสอบ',
    'ทบทวน', 'อ่าน prompt', 'prompt บอก',
]

def strip_ai_meta_lines(text):
    if not isinstance(text, str):
        return ""

    text = normalize_spaces(text)

    # Strip everything before the first ## heading unconditionally —
    # a valid response always starts with ## so any preamble is leaked reasoning.
    first_heading = re.search(r'(?:^|\n)(##\s)', text)
    if first_heading:
        start = first_heading.start(1) if first_heading.start(1) > 0 else first_heading.start()
        if start > 0:
            text = text[start:].strip()

    cleaned = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            cleaned.append("")
            continue
        if any(marker in raw for marker in WEATHER_TEMPLATE_MARKERS):
            continue
        if any(re.search(p, raw, flags=re.IGNORECASE) for p in AI_META_PATTERNS):
            continue
        if re.match(r'^\*\s+', raw):
            continue
        if re.match(r'^\d+\.\s+', raw) and any(kw in raw.lower() for kw in [
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
            # Reject template placeholder blocks
            if city_name.lower() in _WEATHER_TEMPLATE_CITIES:
                continue
            # Reject any block where city name or any line contains bracket placeholders
            if re.search(r'\[.*?\]', city_name):
                continue
            if any(re.search(r'\[.*?\]', ln) for ln in [temp_line, cond_line, tip_line]):
                continue
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
        "- **โรงแรมใจกลางเมือง**: ทำเลดี ใกล้แหล่งท่องเที่ยวสำคัญ เดินทางสะดวก\n"
        "- **รีสอร์ทธรรมชาติ**: บรรยากาศร่มรื่น เหมาะกับการพักผ่อน"
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

        if re.match(r'^##\s*(🌟|💰|🏨|🗺️)', stripped):
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
            response = gemma_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
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
    'generated': False, 'persona_mode': 'tourist',
    'biz_res': '', 'gov_res': '', 'loop_res': '',
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Sanitize: remove unsupported lang codes (e.g. old 'CN')
if st.session_state.lang not in ('TH', 'EN'):
    st.session_state.lang = 'TH'

df_tour, df_fest, df_fest_events = load_data()

# Pre-build province list (reused by all persona modes)
_province_df = df_tour[['ProvinceEN', 'ProvinceTH']].drop_duplicates().dropna(subset=['ProvinceEN', 'ProvinceTH'])
_province_df = _province_df.sort_values(by='ProvinceTH')
province_options = _province_df['ProvinceEN'].tolist()


def format_province(p_en):
    row = df_tour[df_tour['ProvinceEN'] == p_en]
    if not row.empty:
        val = row['ProvinceTH'].iloc[0]
        return str(val) if pd.notna(val) else p_en
    return str(p_en)

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
        'gem_label': "เมืองรองแนะนำ",
        'map_header': "แผนที่สถานที่ในทริป",
        'no_map': "ยังไม่มีข้อมูลพิกัดสำหรับแสดงแผนที่",
        'no_weather': "ยังไม่มีข้อมูลสภาพอากาศ",
        'twin_km': "ห่างกัน", 'twin_drive': "ขับรถประมาณ",
        'twin_revenue': "รายได้เฉลี่ย/เดือน", 'twin_visitors': "นักท่องเที่ยว/เดือน",
        'twin_impact': "การเที่ยวเมืองรองช่วยกระจายรายได้สู่ชุมชนท้องถิ่นโดยตรง",
        'persona_tourist': "✈️ นักท่องเที่ยว",
        'persona_biz': "🏪 ผู้ประกอบการ",
        'persona_gov': "🏛️ ภาครัฐ",
        'lang_instruction': "ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้คำภาษาอังกฤษในเนื้อหาโดยเด็ดขาด",
        'weather_instruction': "ตอบเป็นภาษาไทยเท่านั้น",
        'day_label': "วันที่",
        'morning': "เช้า", 'lunch': "กลางวัน", 'evening': "เย็น-ค่ำ",
        'budget_section': "## 💰 สรุปงบประมาณ",
        'hotel_section': "## 🏨 ที่พักแนะนำ",
        'hotel_hint': "**ชื่อที่พักจริง**: คำอธิบายสั้นๆ",
        'budget_items': "- ค่าที่พัก:\n- ค่าอาหาร:\n- ค่าเดินทาง:\n- ค่าเข้าสถานที่และกิจกรรม:\n- รวมโดยประมาณ:",
    },
    'EN': {
        'title': "Plan Your Trip", 'accent': "The Smart Way",
        'sub': "Festival & weather insights for your perfect Thai adventure",
        'btn': "🚀 Generate Itinerary", 'dest': "Select Province",
        'days': "How many days", 'style': "Travel Style",
        'weather_head': "Weather Forecast",
        'styles': ["Café & Photography 📸", "Nature & Mountains ⛰️", "Culture & Temples 🛕",
                   "Street Food Tour 🍜", "Relax & Chill 🧖", "Bar & Nightlife 🍸"],
        'budget': "Budget Level",
        'budget_styles': ['💰 Budget', '💵 Comfortable', '💎 Luxury'],
        'download_btn': "Download PDF Plan",
        'spinner': "🤖 Generating itinerary...",
        'date_label': "Travel Date",
        'main_label': "Main Destination",
        'gem_label': "Recommended Secondary City",
        'map_header': "Trip Map",
        'no_map': "No location data available for map",
        'no_weather': "No weather data available",
        'twin_km': "Distance", 'twin_drive': "Drive approx.",
        'twin_revenue': "Avg. revenue/month", 'twin_visitors': "Visitors/month",
        'twin_impact': "Visiting secondary cities distributes income directly to local communities",
        'persona_tourist': "✈️ Tourist",
        'persona_biz': "🏪 Entrepreneur",
        'persona_gov': "🏛️ Government",
        'lang_instruction': "Answer in English only. Do not use Thai language in the content.",
        'weather_instruction': "Answer in English only.",
        'day_label': "Day",
        'morning': "Morning", 'lunch': "Lunch", 'evening': "Evening",
        'budget_section': "## 💰 Budget Summary",
        'hotel_section': "## 🏨 Recommended Hotels",
        'hotel_hint': "**Real Hotel Name**: short description",
        'budget_items': "- Accommodation:\n- Food:\n- Transport:\n- Entrance fees & activities:\n- Total estimate:",
    },
}
t = ui.get(st.session_state.lang, ui['TH'])

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
    _lang_opts   = ['TH', 'EN']
    _lang_labels = ['🇹🇭 ไทย', '🇬🇧 English']
    _lang_idx    = _lang_opts.index(st.session_state.lang) if st.session_state.lang in _lang_opts else 0

    _new_label = st.radio(
        "Language",
        options=_lang_labels,
        index=_lang_idx,
        horizontal=True,
        label_visibility="collapsed",
        key="lang_selector"
    )
    _new_code = _lang_opts[_lang_labels.index(_new_label)]
    if _new_code != st.session_state.lang:
        st.session_state.lang = _new_code
        st.rerun()

# ─── Persona Selector ─────────────────────────────────────────────────────────
persona_mode = st.session_state.persona_mode
st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

p_col1, p_col2, p_col3 = st.columns(3, gap="small")
with p_col1:
    if st.button(t['persona_tourist'], use_container_width=True,
                 type="primary" if persona_mode == 'tourist' else "secondary",
                 key="btn_tourist"):
        st.session_state.persona_mode = 'tourist'
        st.session_state.generated = False
        st.rerun()
with p_col2:
    if st.button(t['persona_biz'], use_container_width=True,
                 type="primary" if persona_mode == 'entrepreneur' else "secondary",
                 key="btn_entrepreneur"):
        st.session_state.persona_mode = 'entrepreneur'
        st.session_state.generated = False
        st.rerun()
with p_col3:
    if st.button(t['persona_gov'], use_container_width=True,
                 type="primary" if persona_mode == 'government' else "secondary",
                 key="btn_government"):
        st.session_state.persona_mode = 'government'
        st.session_state.generated = False
        st.rerun()

st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

# ─── Entrepreneur Mode ────────────────────────────────────────────────────────
if persona_mode == 'entrepreneur':
    st.markdown("### 🏪 ที่ปรึกษาธุรกิจท่องเที่ยว")
    st.write("รับกลยุทธ์การตลาดและไอเดียโปรโมชั่นที่สอดคล้องกับข้อมูลตลาดจริงของจังหวัดคุณ")

    bz1, bz2, bz3 = st.columns([2, 1.5, 1.5], gap="small")
    with bz1:
        biz_province = st.selectbox("📍 จังหวัดที่ประกอบธุรกิจ",
                                    options=province_options, format_func=format_province,
                                    key="biz_province")
    with bz2:
        biz_type = st.selectbox("🏬 ประเภทธุรกิจ", [
            "ร้านอาหาร / คาเฟ่", "ที่พัก / โรงแรม",
            "บริษัทนำเที่ยว / กิจกรรม", "ร้านค้าของที่ระลึก",
            "ธุรกิจ SPA / นวด", "ธุรกิจขนส่ง",
        ], key="biz_type")
    with bz3:
        month_names = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
                       'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
        biz_month = st.selectbox("📅 เดือนที่จะวางแผน", month_names, key="biz_month")

    _, bz_btn, _ = st.columns([2, 2, 2])
    with bz_btn:
        biz_clicked = st.button("🚀 วิเคราะห์และสร้างกลยุทธ์",
                                use_container_width=True, type="primary")

    if biz_clicked:
        biz_info = df_tour[df_tour['ProvinceEN'] == biz_province]
        biz_revenue = biz_info['total_revenue'].mean() if not biz_info.empty else 0
        biz_visitors = biz_info['total_visitors'].mean() if not biz_info.empty else 0
        biz_city_type = biz_info['City_type_EN'].iloc[0] if not biz_info.empty else 'ไม่ทราบ'
        biz_city_th = "เมืองรอง" if biz_city_type == 'Secondary City' else "เมืองหลัก"
        biz_province_th = format_province(biz_province)

        biz_festivals = df_fest_events[
            df_fest_events['Province_ID'] == biz_province
        ]['Festival_Name_TH'].tolist()
        festivals_str = ', '.join(biz_festivals[:5]) if biz_festivals else "ไม่พบข้อมูลเทศกาล"

        biz_prompt = f"""คุณเป็นที่ปรึกษาธุรกิจท่องเที่ยวมืออาชีพ ตอบเป็นภาษาไทยเท่านั้น ห้ามอธิบายวิธีคิด

วิเคราะห์และแนะนำกลยุทธ์การตลาดสำหรับ:
- จังหวัด: {biz_province_th} (ประเภท: {biz_city_th})
- ประเภทธุรกิจ: {biz_type}
- เดือน: {biz_month}
- เทศกาลที่เกี่ยวข้อง: {festivals_str}
- รายได้ตลาดเฉลี่ย: {biz_revenue:,.0f} ล้านบาท/เดือน
- นักท่องเที่ยวเฉลี่ย: {biz_visitors:,.0f} คน/เดือน

ตอบในรูปแบบนี้:

## 🎯 วิเคราะห์ตลาด {biz_province_th} เดือน{biz_month}

## 📢 กลยุทธ์การตลาดสำหรับ {biz_type}
(แนะนำ 3-5 กลยุทธ์ที่สอดคล้องกับเทศกาลและฤดูกาล)

## 🎁 ไอเดียโปรโมชั่น
(2-3 ไอเดียที่ทำได้จริงและเชื่อมโยงกับเทศกาล)

## 💡 คำแนะนำเฉพาะสำหรับ{biz_city_th}
(วิธีดึงดูดนักท่องเที่ยวให้มาใช้บริการมากขึ้น)

## 📊 ตัวชี้วัดที่ควรติดตาม (KPI)"""

        with st.spinner("🤖 กำลังวิเคราะห์และสร้างกลยุทธ์..."):
            st.session_state.biz_res = call_ai_strict(biz_prompt, mode="general")
        st.success("✅ สร้างกลยุทธ์เรียบร้อย!")

    if st.session_state.biz_res:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.biz_res)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ─── Government Mode ──────────────────────────────────────────────────────────
if persona_mode == 'government':
    st.markdown("### 🏛️ ที่ปรึกษานโยบายการท่องเที่ยว")
    st.write("วิเคราะห์ช่องว่างรายได้ High-Low Season และรับข้อเสนอนโยบาย Event กระตุ้นเศรษฐกิจ")

    gv1, gv2 = st.columns([2, 1.5], gap="small")
    with gv1:
        gov_province = st.selectbox("📍 เลือกจังหวัด",
                                    options=province_options, format_func=format_province,
                                    key="gov_province")
    with gv2:
        gov_focus = st.selectbox("🎯 โฟกัสการวิเคราะห์", [
            "Low Season กระตุ้นรายได้",
            "ลดช่องว่างเมืองหลัก-เมืองรอง",
            "แผนจัด Event ประจำปี",
            "พัฒนาโครงสร้างพื้นฐานท่องเที่ยว",
        ], key="gov_focus")

    _, gv_btn, _ = st.columns([2, 2, 2])
    with gv_btn:
        gov_clicked = st.button("🚀 วิเคราะห์และสร้างนโยบาย",
                                use_container_width=True, type="primary")

    if gov_clicked:
        gov_info = df_tour[df_tour['ProvinceEN'] == gov_province]
        gov_city_type = gov_info['City_type_EN'].iloc[0] if not gov_info.empty else 'ไม่ทราบ'
        gov_region = str(gov_info['Region_EN'].iloc[0]).strip() if not gov_info.empty else 'ไม่ทราบ'

        monthly_avg = gov_info.groupby('Month')['total_revenue'].mean().reset_index()
        if not monthly_avg.empty:
            high_month = monthly_avg.loc[monthly_avg['total_revenue'].idxmax(), 'Month']
            low_month = monthly_avg.loc[monthly_avg['total_revenue'].idxmin(), 'Month']
            high_rev = monthly_avg['total_revenue'].max()
            low_rev = monthly_avg['total_revenue'].min()
            gap_ratio = (high_rev / low_rev) if low_rev > 0 else 0
        else:
            high_month = low_month = '-'
            high_rev = low_rev = gap_ratio = 0

        gov_festivals = df_fest_events[
            df_fest_events['Province_ID'] == gov_province
        ]['Festival_Name_TH'].tolist()
        festivals_str = ', '.join(gov_festivals[:5]) if gov_festivals else "ยังไม่มีข้อมูลเทศกาล"

        gov_prompt = f"""คุณเป็นที่ปรึกษาด้านนโยบายการท่องเที่ยวของภาครัฐ ตอบเป็นภาษาไทยเท่านั้น ห้ามอธิบายวิธีคิด

วิเคราะห์ข้อมูลและเสนอแนะนโยบายสำหรับ:
- จังหวัด: {gov_province} (ประเภท: {gov_city_type}, ภูมิภาค: {gov_region})
- เดือน High Season: {high_month} (รายได้เฉลี่ย {high_rev:,.1f} ล้านบาท)
- เดือน Low Season: {low_month} (รายได้เฉลี่ย {low_rev:,.1f} ล้านบาท)
- ช่องว่าง High-Low: {gap_ratio:.1f} เท่า
- เทศกาลที่มีอยู่แล้ว: {festivals_str}
- โฟกัส: {gov_focus}

ตอบในรูปแบบนี้:

## 📊 วิเคราะห์สถานการณ์การท่องเที่ยว {gov_province}

## 🚨 ปัญหาและความท้าทายหลัก

## 🗓️ โอกาสและช่องว่างที่ควรเร่งพัฒนา
(โดยเฉพาะช่วง Low Season เดือน {low_month})

## 🎪 ข้อเสนอ Event / กิจกรรมใหม่ (3-5 ข้อ)
(ระบุเดือนที่เหมาะสม งบประมาณโดยประมาณ และเป้าหมายนักท่องเที่ยว)

## 💡 นโยบายเชิงกลยุทธ์
- ระยะสั้น (3-6 เดือน):
- ระยะกลาง (1-2 ปี):
- ระยะยาว (3-5 ปี):

## 🤝 แนวทางการประสานงานภาครัฐ-เอกชน"""

        with st.spinner("🤖 กำลังวิเคราะห์และสร้างรายงานนโยบาย..."):
            st.session_state.gov_res = call_ai_strict(gov_prompt, mode="general")
        st.success("✅ สร้างรายงานนโยบายเรียบร้อย!")

    if st.session_state.gov_res:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.gov_res)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ─── Tourist Mode (default) ───────────────────────────────────────────────────
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

# ─── Feature A: When to Go Card ───────────────────────────────────────────────
_sel_month_abbr = t_date.strftime('%b')   # 'Jan' … 'Dec'
_wtg_fig, _wtg_info = render_when_to_go(province, _sel_month_abbr, df_tour, lang=st.session_state.lang)
if _wtg_fig and _wtg_info:
    _lang = st.session_state.lang
    _prov_th_wtg = format_province(province)
    # insight sentence
    if _wtg_info['sel_visitors']:
        _sv = f"{_wtg_info['sel_visitors']:,}"
        _sm = _wtg_info['sel_month']
        _ss = _wtg_info['sel_season']
        if _lang == 'TH':
            _season_color = {'คนแน่น': '#e74c3c', 'พอดี': '#f39c12', 'คนน้อย': '#27ae60'}.get(_ss, '#888')
            _insight_line = (
                f"เดือน <strong>{_sm}</strong> ที่คุณเลือก: "
                f"<span style='color:{_season_color};font-weight:700'>{_ss} season</span> "
                f"— นักท่องเที่ยวเฉลี่ย <strong>{_sv}</strong> คน/เดือน"
            )
            if _wtg_info['low']:
                _insight_line += f" · ช่วงคนน้อยที่สุด: <strong>{', '.join(_wtg_info['low'])}</strong>"
        else:
            _season_color = {'Busy': '#e74c3c', 'Moderate': '#f39c12', 'Quiet': '#27ae60'}.get(_ss, '#888')
            _insight_line = (
                f"<strong>{_sm}</strong> (selected): "
                f"<span style='color:{_season_color};font-weight:700'>{_ss} season</span> "
                f"— avg <strong>{_sv}</strong> visitors/month"
            )
            if _wtg_info['low']:
                _insight_line += f" · Quietest: <strong>{', '.join(_wtg_info['low'])}</strong>"
    else:
        _insight_line = ''

    # legend chips (no selected chip — bar dimming + annotation handles it)
    _legend_html = (
        "<span style='display:inline-flex;gap:0.5rem;font-size:0.75rem;'>"
        "<span style='background:#e74c3c22;color:#c0392b;padding:2px 8px;border-radius:20px;'>🔴 คนแน่น</span>"
        "<span style='background:#f39c1222;color:#b7770d;padding:2px 8px;border-radius:20px;'>🟡 พอดี</span>"
        "<span style='background:#27ae6022;color:#1e8449;padding:2px 8px;border-radius:20px;'>🟢 คนน้อย</span>"
        "</span>"
    ) if _lang == 'TH' else (
        "<span style='display:inline-flex;gap:0.5rem;font-size:0.75rem;'>"
        "<span style='background:#e74c3c22;color:#c0392b;padding:2px 8px;border-radius:20px;'>🔴 Busy</span>"
        "<span style='background:#f39c1222;color:#b7770d;padding:2px 8px;border-radius:20px;'>🟡 Moderate</span>"
        "<span style='background:#27ae6022;color:#1e8449;padding:2px 8px;border-radius:20px;'>🟢 Quiet</span>"
        "</span>"
    )

    st.markdown(
        f'<div style="background:white;border-radius:16px;padding:1rem 1.3rem 0.5rem;'
        f'box-shadow:0 2px 14px rgba(0,0,0,0.07);margin-bottom:0.8rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.4rem;">'
        f'<p style="font-weight:700;color:#1E3D59;margin:0;font-size:0.95rem;">'
        f'📅 {"ไปเมื่อไหรดี?" if _lang == "TH" else "Best Time to Visit?"} · {_prov_th_wtg}</p>'
        f'{_legend_html}</div>'
        f'<p style="font-size:0.82rem;color:#555;margin:0.35rem 0 0;">{_insight_line}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.plotly_chart(_wtg_fig, use_container_width=True, config={'displayModeBar': False})

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
        _spend_avg = get_spend_per_visitor(province, df_tour)
        _budget_data_hint = ""
        if _spend_avg:
            if st.session_state.lang == 'TH':
                _budget_data_hint = (
                    f"\n\nข้อมูลจริงจากสถิติ: นักท่องเที่ยวที่ {format_province(province)} "
                    f"ใช้จ่ายเฉลี่ย {_spend_avg:,} บาท/คน/ทริป "
                    f"ให้วางแผนงบให้สอดคล้องกับระดับ {budget_clean} โดยอ้างอิงตัวเลขจริงนี้"
                )
            else:
                _budget_data_hint = (
                    f"\n\nReal data: tourists at {province} spend avg {_spend_avg:,} THB/person/trip. "
                    f"Align budget plan with {budget_clean} level, anchored to this real figure."
                )

        weather_locations = province
        if st.session_state.gem_city:
            weather_locations += f", {st.session_state.gem_city}"

        weather_fallback = fallback_weather_from_locations(weather_locations)

        _lang_instr = t['lang_instruction']
        _w_instr    = t['weather_instruction']
        _day_lbl    = t['day_label']
        _morning    = t['morning']
        _lunch      = t['lunch']
        _evening    = t['evening']

        day_headers = "\n\n".join(
            f"## 🌟 {_day_lbl} {d}\n"
            f"- 🌅 {_morning} 07:00-10:00: \n"
            f"- 🍜 {_lunch} 12:00-13:30: \n"
            f"- 🌆 {_evening} 17:00-20:00: "
            for d in range(1, days + 1)
        )

        w_prompt = f"""
{_w_instr}
No internal reasoning. No placeholders. No duplicate cities. One block per city.
Do NOT repeat or copy the format description — output only real data.

Create a weather forecast for {start_date_str} to {end_date_str} for: {weather_locations}

Output format (replace every field with real values, no labels or examples):
📍 [actual city name]
🌡️ [actual temperature range]
☁️ [actual weather description]
💡 [actual travel tip]
"""
        st.session_state.weather_res = call_ai_strict(
            w_prompt,
            mode="weather",
            fallback_text=weather_fallback
        )

        main_fallback = ensure_itinerary_sections("", days)

        main_prompt = f"""
{_lang_instr}
No internal reasoning. No prompt text. No checklists.
No placeholders like [X] or [specify] — fill every field with real information.
Do NOT put Lat/Lon coordinates in the daily plan. Only put them in the ## 🗺️ Coordinates section at the end.
Use only real place names that exist in the province.
Each slot: include place name + main activity + time range.
All budget numbers MUST use comma formatting, e.g. 1,500 บาท — never write without commas like 1500 บาท.

Create a {days}-day itinerary for {format_province(province)}, {start_date_str} to {end_date_str}
Style: {style_str}
Budget: {budget_clean}{_budget_data_hint}

Use this exact structure:
{day_headers}

{t['budget_section']}
{t['budget_items']}

{t['hotel_section']}
- {t['hotel_hint']}
- {t['hotel_hint']}

## 🗺️ Coordinates
(List every place mentioned. Format: **Place Name (Lat: XX.XXXX, Lon: YY.YYYY)**)
"""
        st.session_state.main_res = call_ai_strict(
            main_prompt,
            mode="itinerary",
            fallback_text=main_fallback
        )
        st.session_state.main_res = clean_itinerary_response(st.session_state.main_res, days)

        if st.session_state.gem_city:
            gem_fallback = ensure_itinerary_sections("", days)
            gem_day_headers = "\n\n".join(
                f"## 🌟 {_day_lbl} {d}\n"
                f"- 🌅 {_morning} 07:00-10:00: \n"
                f"- 🍜 {_lunch} 12:00-13:30: \n"
                f"- 🌆 {_evening} 17:00-20:00: "
                for d in range(1, days + 1)
            )
            gem_prov_th = format_province(st.session_state.gem_city)
            _num_instr = (
                "ในส่วนสรุปงบประมาณ ให้ใช้ตัวเลขอารบิคเท่านั้น เช่น 3,000 บาท "
                "ห้ามเขียนเป็นตัวอักษรไทย เช่น สามพันบาท หรือ สองพันห้าร้อยบาท โดยเด็ดขาด"
                if st.session_state.lang == 'TH' else
                "In the budget section, use Arabic numerals only, e.g. 3,000 THB. "
                "Never write amounts as words."
            )
            gem_prompt = f"""
{_lang_instr}
{_num_instr}
No internal reasoning. No prompt text. No checklists.
No placeholders — fill every field with real information.
Do NOT put Lat/Lon in the daily plan. Only in ## 🗺️ Coordinates at the end.
Use only real place names.

Create a {days}-day itinerary for {gem_prov_th}, {start_date_str} to {end_date_str}
Style: {style_str}
Budget: {budget_clean}

Use this exact structure:
{gem_day_headers}

{t['budget_section']}
{t['budget_items']}

{t['hotel_section']}
- {t['hotel_hint']}
- {t['hotel_hint']}

## 🗺️ Coordinates
(List every place mentioned. Format: **Place Name (Lat: XX.XXXX, Lon: YY.YYYY)**)
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
        st.markdown(f"#### 🗺️ {t['map_header']}")
        left_col, right_col = st.columns([1.65, 1], gap="medium")

        with left_col:
            if not all_locations_df.empty:
                st.map(all_locations_df)
            else:
                st.info(t["no_map"])

        with right_col:
            if weather_blocks:
                import html as _html
                parts = [
                    '<div style="background:#0077B6;'
                    'border-radius:18px;padding:1rem;">'
                    f'<p style="font-weight:700;font-size:1rem;color:white;margin:0 0 0.75rem 0;">'
                    f'☁️ {t["weather_head"]}</p>'
                ]
                for w in weather_blocks:
                    city = _html.escape(str(w.get('city', '')))
                    temp = _html.escape(str(w.get('temp', '')))
                    cond = _html.escape(str(w.get('cond', '')))
                    tip  = _html.escape(str(w.get('tip', '')))
                    parts.append(
                        '<div style="background:rgba(255,255,255,0.13);border:1px solid rgba(255,255,255,0.2);'
                        'border-radius:12px;padding:0.75rem 1rem;margin-bottom:0.55rem;">'
                        f'<p style="font-weight:700;color:white;font-size:0.95rem;margin:0 0 0.25rem 0;">📍 {city}</p>'
                        f'<p style="color:rgba(255,255,255,0.92);font-size:0.88rem;margin:0 0 0.18rem 0;">🌡️ {temp}</p>'
                        f'<p style="color:rgba(255,255,255,0.92);font-size:0.88rem;margin:0 0 0.18rem 0;">☁️ {cond}</p>'
                        f'<p style="color:rgba(255,255,255,0.85);font-size:0.85rem;margin:0;">💡 {tip}</p>'
                        '</div>'
                    )
                parts.append('</div>')
                st.markdown(''.join(parts), unsafe_allow_html=True)
            else:
                st.info(t["no_weather"])

# ─── Result Cards ─────────────────────────────────────────────────────────────
_badge_main = (
    f'<span style="background:#0077B6;color:white;font-size:0.68rem;font-weight:700;'
    f'padding:3px 12px;border-radius:20px;letter-spacing:1.5px;text-transform:uppercase;">'
    f'{t["main_label"]}</span>'
)
_badge_gem = (
    f'<span style="background:#FF6E40;color:white;font-size:0.68rem;font-weight:700;'
    f'padding:3px 12px;border-radius:20px;letter-spacing:1.5px;text-transform:uppercase;">'
    f'{t["gem_label"]}</span>'
)

def _plan_header(badge_html, province_label, accent):
    return (
        f'<div style="display:flex;align-items:center;gap:8px;'
        f'border-left:4px solid {accent};padding-left:0.65rem;margin-bottom:0.6rem;">'
        f'{badge_html}'
        f'<span style="font-weight:700;font-size:0.95rem;color:#1a1a2e;">📍 {province_label}</span>'
        f'</div>'
    )

if st.session_state.main_res:
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    if st.session_state.gem_res:
        # ── Twin Cities Banner + Stats ────────────────────────────────────────
        prov_th_disp = format_province(province)
        gem_th_disp  = format_province(st.session_state.gem_city)
        twin_stats   = get_twin_city_stats(province, st.session_state.gem_city, df_tour)

        # Distance / drive time line
        if 'dist_km' in twin_stats:
            hr, mn = twin_stats['drive_hr'], twin_stats['drive_min']
            drive_txt = f"{hr} ชม. {mn} นาที" if hr > 0 else f"{mn} นาที"
            if st.session_state.lang == 'EN':
                drive_txt = f"{hr} hr {mn} min" if hr > 0 else f"{mn} min"
            dist_line = (
                f'<span style="font-size:0.85rem;color:#0077B6;font-weight:500;">'
                f'📏 {twin_stats["dist_km"]} km &nbsp;|&nbsp; 🚗 {drive_txt}</span>'
            )
        else:
            dist_line = ''

        # Revenue comparison
        rev_html = ''
        if 'main_revenue' in twin_stats and 'gem_revenue' in twin_stats:
            main_rev = twin_stats['main_revenue']
            gem_rev  = twin_stats['gem_revenue']
            ratio    = main_rev / gem_rev if gem_rev > 0 else 0
            rev_lbl  = t['twin_revenue']
            vis_lbl  = t['twin_visitors']
            main_vis = twin_stats.get('main_visitors', 0)
            gem_vis  = twin_stats.get('gem_visitors', 0)
            unit     = "ล้านบาท" if st.session_state.lang == 'TH' else "M THB"
            rev_html = (
                f'<div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:0.5rem;'
                f'padding-top:0.5rem;border-top:1px solid rgba(0,119,182,0.1);">'
                f'<div style="flex:1;min-width:140px;">'
                f'<div style="font-size:0.72rem;color:#888;margin-bottom:0.15rem;">🏙️ {prov_th_disp}</div>'
                f'<div style="font-size:0.82rem;font-weight:600;color:#0077B6;">'
                f'{rev_lbl}: <strong>{main_rev:,.1f} {unit}</strong></div>'
                f'<div style="font-size:0.78rem;color:#555;">'
                f'{vis_lbl}: {main_vis:,.0f}</div>'
                f'</div>'
                f'<div style="display:flex;align-items:center;color:#0077B6;font-size:1rem;font-weight:700;">⟷</div>'
                f'<div style="flex:1;min-width:140px;">'
                f'<div style="font-size:0.72rem;color:#888;margin-bottom:0.15rem;">🌟 {gem_th_disp}</div>'
                f'<div style="font-size:0.82rem;font-weight:600;color:#FF6E40;">'
                f'{rev_lbl}: <strong>{gem_rev:,.1f} {unit}</strong></div>'
                f'<div style="font-size:0.78rem;color:#555;">'
                f'{vis_lbl}: {gem_vis:,.0f}</div>'
                f'</div>'
                f'<div style="flex:2;min-width:180px;display:flex;align-items:center;">'
                f'<div style="background:rgba(255,110,64,0.08);border-radius:10px;'
                f'padding:0.4rem 0.7rem;font-size:0.8rem;color:#555;">'
                f'💡 {t["twin_impact"]}'
                f'{"" if ratio == 0 else f" (รายได้ต่างกัน <strong>{ratio:.1f}x</strong>)" if st.session_state.lang == "TH" else f" (revenue gap <strong>{ratio:.1f}x</strong>)"}'
                f'</div></div>'
                f'</div>'
            )

        st.markdown(
            f'<div class="twin-banner" style="flex-direction:column;align-items:flex-start;gap:0.4rem;">'
            f'<div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">'
            f'<span class="twin-badge main">{"เมืองหลัก" if st.session_state.lang == "TH" else "Main City"}</span>'
            f'🏙️ <strong>{prov_th_disp}</strong>'
            f'<span class="twin-arrow">⟷</span>'
            f'🌟 <strong>{gem_th_disp}</strong>'
            f'<span class="twin-badge sec">{"เมืองรอง" if st.session_state.lang == "TH" else "Secondary"}</span>'
            f'{dist_line}'
            f'</div>'
            f'{rev_html}'
            f'</div>',
            unsafe_allow_html=True
        )

        col_l, col_r = st.columns(2, gap="medium")

        with col_l:
            st.markdown(_plan_header(_badge_main, prov_th_disp, '#0077B6'),
                        unsafe_allow_html=True)
            tl_html = build_timeline_html(st.session_state.main_res, gem=False)
            st.markdown(tl_html if tl_html else strip_coords_for_display(st.session_state.main_res),
                        unsafe_allow_html=True)

        with col_r:
            st.markdown(_plan_header(_badge_gem, gem_th_disp, '#FF6E40'),
                        unsafe_allow_html=True)
            if st.session_state.travel_info:
                st.markdown(
                    f'<div style="font-size:0.87rem;color:#555;'
                    f'background:rgba(255,110,64,0.07);'
                    f'padding:0.45rem 0.75rem;border-radius:10px;margin-bottom:0.5rem;'
                    f'border-left:3px solid #FF6E40;">🚗 {st.session_state.travel_info}</div>',
                    unsafe_allow_html=True
                )
            gem_html = build_timeline_html(st.session_state.gem_res, gem=True)
            st.markdown(gem_html if gem_html else strip_coords_for_display(st.session_state.gem_res),
                        unsafe_allow_html=True)

            # ── Savings Comparison Card ───────────────────────────────────────
            main_lo, main_hi = extract_budget_total(st.session_state.main_res)
            gem_lo,  gem_hi  = extract_budget_total(st.session_state.gem_res)
            if main_lo and gem_lo:
                # Use lo (lower bound) for conservative, display-consistent comparison
                savings = main_lo - gem_lo
                # Sanity: skip if savings is implausibly large (> either budget's lower bound)
                max_plausible = max(main_lo, gem_lo)
                if savings > 0 and savings <= max_plausible:
                    if st.session_state.lang == 'TH':
                        savings_msg = (
                            f'หากเลือกเที่ยว <strong>{gem_th_disp}</strong> '
                            f'แทน <strong>{prov_th_disp}</strong> '
                            f'คุณสามารถประหยัดได้ประมาณ '
                            f'<strong style="color:#27ae60;">{savings:,.0f} บาท</strong> ต่อคน '
                            f'<span style="font-size:0.78rem;color:#888;">(ประมาณการจาก AI)</span>'
                        )
                    else:
                        savings_msg = (
                            f'Choosing <strong>{gem_th_disp}</strong> '
                            f'over <strong>{prov_th_disp}</strong> '
                            f'saves you approximately '
                            f'<strong style="color:#27ae60;">{savings:,.0f} THB</strong> per person '
                            f'<span style="font-size:0.78rem;color:#888;">(AI estimate)</span>'
                        )
                    st.markdown(
                        f'<div style="margin-top:0.6rem;padding:0.7rem 1rem;'
                        f'background:linear-gradient(135deg,rgba(39,174,96,0.08),rgba(46,204,113,0.06));'
                        f'border:1px solid rgba(39,174,96,0.2);border-radius:14px;'
                        f'font-size:0.88rem;color:#2d4a3e;line-height:1.55;">'
                        f'💚 {savings_msg}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                elif savings < 0:
                    # Gem is pricier — show transparent note instead of hiding
                    diff = abs(savings)
                    if st.session_state.lang == 'TH':
                        cost_msg = (
                            f'{gem_th_disp} มีค่าใช้จ่ายสูงกว่า {prov_th_disp} '
                            f'ประมาณ <strong>{diff:,.0f} บาท</strong> ต่อคน '
                            f'<span style="font-size:0.78rem;color:#888;">(ประมาณการจาก AI)</span>'
                        )
                    else:
                        cost_msg = (
                            f'{gem_th_disp} costs approximately '
                            f'<strong>{diff:,.0f} THB</strong> more per person than {prov_th_disp} '
                            f'<span style="font-size:0.78rem;color:#888;">(AI estimate)</span>'
                        )
                    st.markdown(
                        f'<div style="margin-top:0.6rem;padding:0.7rem 1rem;'
                        f'background:rgba(255,110,64,0.06);'
                        f'border:1px solid rgba(255,110,64,0.18);border-radius:14px;'
                        f'font-size:0.88rem;color:#5a3020;line-height:1.55;">'
                        f'💡 {cost_msg}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
    else:
        st.markdown(_plan_header(_badge_main, format_province(province), '#0077B6'),
                    unsafe_allow_html=True)
        tl_html = build_timeline_html(st.session_state.main_res, gem=False)
        st.markdown(tl_html if tl_html else strip_coords_for_display(st.session_state.main_res),
                    unsafe_allow_html=True)

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

# ─── Feature D: Hidden Gem Loop Route Builder ─────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
st.divider()
st.markdown(
    '<div style="margin-bottom:0.6rem;">'
    '<p style="font-weight:800;font-size:1.1rem;color:#0077B6;margin:0 0 4px;">🗺️ สร้างเส้นทาง Loop Trip · Hidden Gem Route</p>'
    '<p style="font-size:0.85rem;color:#576574;margin:0;">'
    'เส้นทางที่ Google Maps ไม่เคยแนะนำ — เมืองหลัก → เมืองรอง → กลับบ้าน '
    'พร้อมระยะทาง เวลาขับรถ และ AI สรุปไฮไลต์แต่ละจุด</p>'
    '</div>',
    unsafe_allow_html=True
)

_loop_lang = st.session_state.lang
_loop_stops = find_loop_stops(province, df_tour, n=2, max_km=350)

if not _loop_stops:
    st.info("ไม่พบเมืองรองในรัศมี 350 กม. สำหรับสร้าง Loop Trip" if _loop_lang == 'TH'
            else "No secondary cities within 350 km for a loop route.")
else:
    _prov_th_loop = format_province(province)
    _main_coord   = PROVINCE_COORDS.get(province)

    # ── Route visual card ──
    _total_km = sum(s['dist_from_prev'] for s in _loop_stops) + _loop_stops[-1].get('dist_back', 0)
    _total_drive_min = int(_total_km / 80 * 60)
    _total_hr  = _total_drive_min // 60
    _total_min = _total_drive_min % 60

    _route_nodes = [_prov_th_loop] + [s['th'] for s in _loop_stops] + [_prov_th_loop]
    _route_html = ""
    for i, node in enumerate(_route_nodes):
        is_main = (node == _prov_th_loop)
        is_last = (i == len(_route_nodes) - 1)
        bg = '#0077B6' if is_main else '#FF6E40'
        _route_html += (
            f'<div style="display:flex;align-items:center;gap:0.5rem;">'
            f'<div style="background:{bg};color:white;border-radius:12px;'
            f'padding:0.45rem 0.9rem;font-weight:700;font-size:0.88rem;white-space:nowrap;">'
            f'{"🏙️" if is_main else "🌟"} {node}</div>'
        )
        if not is_last:
            _leg_km = _loop_stops[i]['dist_from_prev'] if i < len(_loop_stops) else _loop_stops[-1].get('dist_back', 0)
            if i == len(_route_nodes) - 2:
                _leg_km = _loop_stops[-1].get('dist_back', 0)
            _leg_min = int(_leg_km / 80 * 60)
            _leg_lbl = f"{_leg_km} กม. · {_leg_min} นาที" if _loop_lang == 'TH' else f"{_leg_km} km · {_leg_min} min"
            _route_html += (
                f'<div style="display:flex;flex-direction:column;align-items:center;color:#888;font-size:0.73rem;">'
                f'<span>→</span><span style="white-space:nowrap">{_leg_lbl}</span></div>'
            )
        _route_html += '</div>'

    st.markdown(
        f'<div style="background:white;border-radius:16px;padding:1.1rem 1.3rem;'
        f'box-shadow:0 2px 14px rgba(0,0,0,0.07);margin-bottom:1rem;">'
        f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0.3rem;">{_route_html}</div>'
        f'<p style="margin:0.7rem 0 0;font-size:0.82rem;color:#555;">'
        f'📏 {"รวมระยะทางทั้งหมด" if _loop_lang == "TH" else "Total distance"}: '
        f'<strong>{_total_km} {"กม." if _loop_lang == "TH" else "km"}</strong> · '
        f'⏱️ {"เวลาขับรถรวม" if _loop_lang == "TH" else "Total drive time"}: '
        f'<strong>{_total_hr} {"ชม." if _loop_lang == "TH" else "hr"} {_total_min} {"นาที" if _loop_lang == "TH" else "min"}</strong></p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── AI generate loop route description ──
    _loop_btn_lbl = "🤖 ให้ AI สรุปไฮไลต์แต่ละจุดหยุด" if _loop_lang == 'TH' else "🤖 Generate AI highlights for each stop"
    _loop_col1, _loop_col2, _loop_col3 = st.columns([2, 3, 2])
    with _loop_col2:
        if st.button(_loop_btn_lbl, use_container_width=True, key="btn_loop_gen"):
            _stops_th = [s['th'] for s in _loop_stops]
            _stops_str = ', '.join(_stops_th)
            _loop_prompt = f"""
You are a Thai travel expert. {"ตอบเป็นภาษาไทยเท่านั้น" if _loop_lang == "TH" else "Answer in English."} No internal reasoning. No prompt text.

Create a Hidden Gem Loop Trip highlight for this route:
{_prov_th_loop} → {" → ".join(_stops_th)} → {_prov_th_loop}
Travel days: {days} days total, starting {t_date.strftime('%d %B %Y')}

For each stop (including {_prov_th_loop}), write:
## 📍 [City name]
- 🌟 ไฮไลต์หลัก: [1-2 สิ่งที่ห้ามพลาด]
- 🍜 อาหารต้องลอง: [ชื่ออาหารท้องถิ่น]
- 🎯 เหมาะกับ: [ประเภทนักท่องเที่ยว]
- ⏱️ เวลาที่แนะนำ: [X วัน/ชั่วโมง]

End with:
## 💡 ทำไม Loop นี้ถึงพิเศษ
[2-3 ประโยค อธิบายว่าทำไม combo นี้ถึงดีกว่าไปจังหวัดเดียว]
"""
            with st.spinner("🤖 กำลังสร้างไฮไลต์ Loop Trip..." if _loop_lang == 'TH' else "🤖 Generating loop highlights..."):
                st.session_state.loop_res = call_ai_strict(_loop_prompt, mode="general")

    if st.session_state.loop_res:
        st.markdown(
            '<div style="background:white;border-radius:16px;padding:1.2rem 1.5rem;'
            'box-shadow:0 2px 14px rgba(0,0,0,0.07);border-top:4px solid #0077B6;">',
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.loop_res)
        st.markdown('</div>', unsafe_allow_html=True)

        