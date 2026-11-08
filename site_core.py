import os
import json
import re
import sys
import datetime
import urllib.parse
import requests
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
SITE_URL = "https://krobjang.vercel.app"
SITE_NAME = "ครบจัง"
SITE_DESC = "บทความไทยคุณภาพ ครบทุกหมวด"

# โหลดค่า Environment
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_PATH / ".env")
except:
    pass

UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_KEY", "")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")
LINE_NOTIFY_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN", "")
ADSENSE_PUB = os.environ.get("ADSENSE_PUB", "")
ADSENSE_SLOT = os.environ.get("ADSENSE_SLOT", "")
GA4_ID = os.environ.get("GA4_ID", "")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", "llava")
DRY_RUN = "--dry-run" in sys.argv

# หมวดหมู่
CATEGORIES = [
    'food', 'health', 'travel', 'finance', 'technology', 'sport', 
    'cartoon', 'drama', 'anime', 'gaming', 'lifestyle', 'news', 
    'beauty', 'business', 'comedy', 'education', 'ghost', 'inspirational', 
    'music', 'tips'
]
CATEGORY_PAGE_MAP = {c: f"{c}.html" for c in CATEGORIES}
หมวด_ไทย = {
    'food': 'อาหาร', 'health': 'สุขภาพ', 'travel': 'ท่องเที่ยว', 
    'finance': 'การเงิน', 'technology': 'เทคโนโลยี', 'sport': 'กีฬา', 
    'cartoon': 'การ์ตูน', 'drama': 'ดราม่า', 'anime': 'อนิเมะ', 
    'gaming': 'เกม', 'lifestyle': 'ไลฟ์สไตล์', 'news': 'ข่าว', 
    'beauty': 'ความงาม', 'business': 'ธุรกิจ', 'comedy': 'ตลก', 
    'education': 'การศึกษา', 'ghost': 'ผีสาง', 'inspirational': 'แรงบันดาลใจ', 
    'music': 'เพลง', 'tips': 'เคล็ดลับ'
}

# Logging
def log(msg): print(msg)
def log_ok(msg): print(f"✅ {msg}")
def log_warn(msg): print(f"⚠️ {msg}")
def log_err(msg): print(f"❌ {msg}")
def log_info(msg): print(f"ℹ️ {msg}")
def log_ai(msg): print(f"🤖 {msg}")
def log_section(msg): print(f"\n{'='*50}\n{msg}\n{'='*50}")

# Utils
def url_join(base, path):
    return f"{base.rstrip('/')}/{path.lstrip('/')}"

def สร้างชื่อไฟล์(หมวด, หัวข้อ):
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    import hashlib
    h = hashlib.md5(หัวข้อ.encode()).hexdigest()[:4]
    return f"article_{หมวด}_{now}_{h}.html"

def สร้าง_thumbnail_svg(หัวข้อ, หมวด):
    return ""

# State Management
STATE_FILE = BASE_PATH / "site_state.json"
def อ่าน_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {}
def เขียน_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

def state_เพิ่ม_pending_publish(filename):
    state = อ่าน_state()
    if "pending_publish" not in state: state["pending_publish"] = []
    state["pending_publish"].append(filename)
    เขียน_state(state)

def state_เพิ่ม_pending_doctor(filename): pass
def state_บันทึก_error(err): pass

INDEX_FILE = BASE_PATH / "articles_index.json"
def index_เพิ่มบทความ(title, cat, filename, og_img):
    index = []
    if INDEX_FILE.exists():
        try: index = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
        except: pass
    index.append({"title": title, "cat": cat, "filename": filename, "image": og_img})
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')

def ดึงหัวข้อที่มี():
    if INDEX_FILE.exists():
        try:
            index = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
            return [i["title"] for i in index]
        except: pass
    return []

def index_ดึงตามหมวด(หมวด, limit=10):
    if INDEX_FILE.exists():
        try:
            index = json.loads(INDEX_FILE.read_text(encoding='utf-8'))
            return [i for i in index if i["cat"] == หมวด][:limit]
        except: pass
    return []

def เช็คซ้ำ(filename):
    return (BASE_PATH / filename).exists()

# Ollama Functions
def เรียก_ollama(prompt, timeout=180, num_predict=1500):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": num_predict}
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        return r.json().get("response", "")
    except Exception as e:
        log_warn(f"Ollama error: {e}")
        return ""

def เรียก_ollama_เร็ว(prompt, timeout=60, num_predict=100):
    return เรียก_ollama(prompt, timeout, num_predict)

def เช็ค_ollama():
    try:
        requests.get(OLLAMA_URL.replace("/api/generate", ""), timeout=2)
        return True
    except:
        return False

def ดึงรูป_local(หมวด, หัวข้อ=""):
    return ""