# config.py — ไอหมอก
# สร้างโดย agent_setup.py v2 เมื่อ 2026-04-09 22:16
import os, sys, re, datetime
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ══════════════════════════════════════════════════════════════
# 🌐 ตั้งค่าเว็บไซต์
# ══════════════════════════════════════════════════════════════
BASE_PATH         = Path(r"D:\Projects\krubjang-site full")
SITE_URL          = "https://krobjang.vercel.app/"
SITE_NAME         = "ไอหมอก"
SITE_DESC         = "ไอหมอก — แหล่งความรู้ครบครัน"
CATEGORIES        = ['news', 'lifestyle', 'health', 'food', 'finance', 'technology', 'entertainment']
CATEGORY_PAGE_MAP = {'news': 'news.html', 'lifestyle': 'lifestyle.html', 'health': 'health.html', 'food': 'food.html', 'finance': 'finance.html', 'technology': 'technology.html', 'entertainment': 'entertainment.html'}
CAT_PAGE_MAP      = CATEGORY_PAGE_MAP
FILE_TYPES        = [".html"]
ART_PATTERN       = "*_*.html"
LANG              = "th"

RSS_FEEDS = [('ไทยรัฐ', 'https://www.thairath.co.th/rss/news.xml'), ('BBC Thai', 'https://feeds.bbci.co.uk/thai/rss.xml'), ('ข่าวสด', 'https://www.khaosod.co.th/feed')]

# ══════════════════════════════════════════════════════════════
# 🤖 Ollama
# ══════════════════════════════════════════════════════════════
OLLAMA_HOST    = "http://localhost:11434"
OLLAMA_MODEL   = os.getenv("OLLAMA_MODEL", "scb10x/llama3.1-typhoon2-8b-instruct:latest")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))

# ══════════════════════════════════════════════════════════════
# 🔑 API Keys — ใส่ใน .env หรือแก้โดยตรง
# ══════════════════════════════════════════════════════════════
UNSPLASH_KEY      = os.getenv("UNSPLASH_KEY", "")
PEXELS_KEY        = os.getenv("PEXELS_KEY", "")
YOUTUBE_API_KEY   = os.getenv("YOUTUBE_API_KEY", "")
FB_PAGE_ID        = os.getenv("FB_PAGE_ID", "")
FB_ACCESS_TOKEN   = os.getenv("FB_ACCESS_TOKEN", "")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN", "")
ADSENSE_PUB       = os.getenv("ADSENSE_PUB", "")
ADSENSE_SLOT      = os.getenv("ADSENSE_SLOT", "")
GA4_ID            = os.getenv("GA4_ID", "")
LAZADA_AFFILIATE  = os.getenv("LAZADA_AFFILIATE", "")
SHOPEE_AFFILIATE  = os.getenv("SHOPEE_AFFILIATE", "")
AGODA_AFFILIATE   = os.getenv("AGODA_AFFILIATE", "")

# ══════════════════════════════════════════════════════════════
# 📝 Logging
# ══════════════════════════════════════════════════════════════
DRY_RUN = "--dry-run" in sys.argv

def _ts(): return datetime.datetime.now().strftime("%H:%M:%S")
def log(m):        print(f"[{_ts()}] {m}")
def log_ok(m):     print(f"[{_ts()}] ✅ {m}")
def log_warn(m):   print(f"[{_ts()}] ⚠️  {m}")
def log_err(m):    print(f"[{_ts()}] ❌ {m}")
def log_info(m):   print(f"[{_ts()}] ℹ️  {m}")
def log_ai(m):     print(f"[{_ts()}] 🤖 {m}")
def log_section(m):print(f"\n{'='*55}\n  {m}\n{'='*55}")

หมวด_ไทย = {
    "health":"สุขภาพ","lifestyle":"ไลฟ์สไตล์","finance":"การเงิน",
    "ai":"ปัญญาประดิษฐ์","food":"อาหาร","sport":"กีฬา",
    "horoscope":"ดูดวง","booking":"จองที่พัก","news":"ข่าวสาร",
    "ghost":"เรื่องลี้ลับ","technology":"เทคโนโลยี","comedy":"ตลก",
    "entertainment":"บันเทิง","politics":"การเมือง","mystery":"ปริศนา",
    "anime":"อนิเมะ","movie":"ภาพยนตร์","music":"ดนตรี",
    "beauty":"ความงาม","pet":"สัตว์เลี้ยง","education":"การศึกษา",
    "business":"ธุรกิจ","diy":"ดีไอวาย","car":"รถยนต์",
    "gaming":"เกมมิ่ง","law":"กฎหมาย","shopping":"ช้อปปิ้ง",
    "review":"รีวิว","portfolio":"ผลงาน","design":"ดีไซน์",
    "photography":"ถ่ายภาพ","art":"ศิลปะ","menu":"เมนู",
    "promotion":"โปรโมชั่น","event":"กิจกรรม","service":"บริการ",
    "doctor":"แพทย์","faq":"คำถาม","course":"หลักสูตร",
    "teacher":"อาจารย์","gallery":"แกลเลอรี่","feature":"คุณสมบัติ",
    "pricing":"ราคา","hotel":"โรงแรม","tip":"เคล็ดลับ","about":"เกี่ยวกับ",
}

CAT_COLORS = {
    "health":"#10b981","lifestyle":"#6366f1","finance":"#059669",
    "ai":"#3b82f6","food":"#ef4444","sport":"#f59e0b",
    "horoscope":"#8b5cf6","news":"#4b5563","ghost":"#1e293b",
    "technology":"#2563eb","beauty":"#ec4899","gaming":"#7c3aed",
    "travel":"#0ea5e9","education":"#0891b2","business":"#059669",
}

AI_SYSTEM_PROMPT = """คุณคือนักเขียนบทความบล็อกภาษาไทยที่เขียนได้เป็นธรรมชาติ อ่านสนุก เหมือนเพื่อนที่รู้เรื่องนั้นดีมาเล่าให้ฟัง
ห้าม: เขียน instruction/คำสั่ง/หมายเหตุลงในบทความ, เริ่มทุกย่อหน้าด้วย "การ...", ใช้ภาษาแข็ง
ต้อง: ตอบด้วยเนื้อหาบทความเท่านั้น, เขียนเหมือนคนไทยจริงๆ มีอารมณ์"""

def เรียก_ollama(prompt: str, timeout: int = None, num_predict: int = 2048, temperature: float = None) -> str:
    if timeout is None: timeout = OLLAMA_TIMEOUT
    if temperature is None: temperature = 0.85
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL, "system": AI_SYSTEM_PROMPT, "prompt": prompt,
        "stream": False, "options": {"num_predict": num_predict, "temperature": temperature, "repeat_penalty": 1.15, "top_p": 0.92}
    }
    for attempt in range(1, 3):
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            log_warn(f"Ollama timeout (ครั้งที่ {attempt})")
        except Exception as e:
            log_err(f"Ollama error: {e}")
            break
    return ""

def เรียก_ollama_เร็ว(prompt: str, timeout: int = 30, num_predict: int = 200) -> str:
    return เรียก_ollama(prompt, timeout=timeout, num_predict=num_predict, temperature=0.4)

def _แปลง_keyword_อังกฤษ(หัวข้อ: str, บริบท: str = "") -> str:
    prompt = f'Thai topic: "{หัวข้อ}"\nWrite 3-4 English keywords for a stock photo. Reply keywords only.'
    raw = เรียก_ollama(prompt, timeout=20, num_predict=40, temperature=0.15)
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    raw = re.sub(r'["\'\n]', ' ', raw).strip()
    return raw[:80] if raw else ""

def ดึงรูป_unsplash(หมวด: str, คีย์เวิร์ด: str = "") -> str:
    import hashlib
    if not UNSPLASH_KEY:
        seed = hashlib.md5((คีย์เวิร์ด+หมวด).encode()).hexdigest()[:12]
        return f"https://picsum.photos/seed/{seed}/800/450"
    query = คีย์เวิร์ด or หมวด
    try:
        import urllib.parse
        r = requests.get(f"https://api.unsplash.com/photos/random?query={urllib.parse.quote(query)}&orientation=landscape&client_id={UNSPLASH_KEY}", timeout=10)
        if r.status_code == 200:
            return r.json().get("urls",{}).get("regular","")
    except Exception: pass
    import hashlib
    seed = hashlib.md5(query.encode()).hexdigest()[:12]
    return f"https://picsum.photos/seed/{seed}/800/450"

def ดึงรูป_pexels(keyword: str) -> str:
    if not PEXELS_KEY: return ""
    import urllib.parse
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={urllib.parse.quote(keyword)}&per_page=5&orientation=landscape",
                         headers={"Authorization": PEXELS_KEY}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos",[])
            if photos:
                import random as _r
                return _r.choice(photos[:3])["src"]["large"]
    except Exception: pass
    return ""

def ดึงรูป_ตรงเนื้อหา(หัวข้อ: str, หมวด: str, บริบท: str = "") -> str:
    import hashlib, urllib.parse
    seed = hashlib.md5((หัวข้อ+หมวด).encode()).hexdigest()[:12]
    keyword = _แปลง_keyword_อังกฤษ(หัวข้อ, บริบท)
    if PEXELS_KEY and keyword:
        img = ดึงรูป_pexels(keyword)
        if img: return img
    if not UNSPLASH_KEY:
        return f"https://picsum.photos/seed/{seed}/800/450"
    for q in [keyword, หัวข้อ[:20], หมวด]:
        if not q: continue
        try:
            r = requests.get(f"https://api.unsplash.com/photos/random?query={urllib.parse.quote(q)}&orientation=landscape&client_id={UNSPLASH_KEY}", timeout=10)
            if r.status_code == 200:
                img = r.json().get("urls",{}).get("regular","")
                if img: return img
            elif r.status_code == 429: break
        except Exception: pass
    return f"https://picsum.photos/seed/{seed}/800/450"

def สร้าง_thumbnail_svg(หัวข้อ: str, หมวด: str, filename: str) -> str:
    import hashlib, re as _re
    svg_dir = BASE_PATH / "images" / "thumbs"
    svg_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = Path(filename).stem + ".svg"
    svg_path = svg_dir / safe_filename
    color = CAT_COLORS.get(หมวด, "#6366f1")
    h_display = _re.sub(r'[^\u0000-\u04FF\u0E00-\u0E7F ]', '', หัวข้อ[:30]).strip()
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">'
           f'<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">'
           f'<stop offset="0%" stop-color="{color}"/>'
           f'<stop offset="100%" stop-color="#1e293b"/></linearGradient></defs>'
           f'<rect width="800" height="450" fill="url(#g)"/>'
           f'<rect x="40" y="40" width="720" height="370" rx="15" fill="#fff" opacity="0.07"/>'
           f'<text x="400" y="210" fill="#fff" font-family="Sarabun,sans-serif" font-size="28" font-weight="bold" text-anchor="middle">{h_display}</text>'
           f'<text x="400" y="265" fill="#cbd5e1" font-family="sans-serif" font-size="18" text-anchor="middle">{หมวด_th}</text>'
           f'<text x="400" y="390" fill="#94a3b8" font-family="sans-serif" font-size="15" text-anchor="middle">{SITE_NAME}</text>'
           f'</svg>')
    try:
        svg_path.write_text(svg, encoding="utf-8")
        return f"images/thumbs/{safe_filename}"
    except Exception: return ""

def สร้าง_sidebar_html():
    return "" # หรือใส่โค้ดสำหรับสร้าง Sidebar ที่คุณต้องการ

SIDEBAR_CONFIG = {
    "show_recent":    True,
    "show_categories": True,
    "show_tags":      True,
    "max_recent_posts": 5,
    # ─── Social / Support ───────────────────────────────
    "facebook_url":   os.getenv("FACEBOOK_URL",  "https://www.facebook.com/phongphun.phommanee"),
    "youtube_url":    os.getenv("YOUTUBE_URL",   "https://youtube.com/@phongphunphommanee8045"),
    "tiktok_url":     os.getenv("TIKTOK_URL",    "https://www.tiktok.com/@kengwong007"),
    "instagram_url":  os.getenv("INSTAGRAM_URL", ""),
    "promptpay_img":  os.getenv("PROMPTPAY_IMG", "images/promptpay.png"),
    "promptpay_href": os.getenv("PROMPTPAY_HREF","images/promptpay.png"),
}

def สร้าง_sidebar_html() -> str:
    """Sidebar 'สนับสนุนเรา' — ใส่ทุกหน้าผ่านฟังก์ชันนี้จุดเดียว
    แก้ข้อมูล Social/PromptPay ที่ SIDEBAR_CONFIG หรือ .env ด้านบน"""
    cfg = SIDEBAR_CONFIG
    qr  = cfg["promptpay_img"]
    qr_href = cfg["promptpay_href"]

    def _btn(href, bg, icon, label, extra=""):
        return (f'<a href="{href}" target="_blank" rel="noopener" '
                f'style="display:inline-flex;align-items:center;gap:.4rem;'
                f'padding:.42rem .9rem;background:{bg};color:#fff;border-radius:6px;'
                f'text-decoration:none;font-size:.83rem;font-weight:600;{extra}">'
                f'<i class="{icon}"></i> {label}</a>')

    social_btns = []
    if cfg.get("facebook_url"):
        social_btns.append(_btn(cfg["facebook_url"], "#1877f2", "fab fa-facebook-f", "Facebook"))
    if cfg.get("youtube_url"):
        social_btns.append(_btn(cfg["youtube_url"],  "#ff0000", "fab fa-youtube",    "YouTube"))
    if cfg.get("tiktok_url"):
        social_btns.append(_btn(cfg["tiktok_url"],   "#010101", "fab fa-tiktok",     "TikTok"))
    if cfg.get("instagram_url"):
        social_btns.append(_btn(cfg["instagram_url"],"#e1306c", "fab fa-instagram",  "Instagram"))

    social_html = "\n        ".join(social_btns)

    # PromptPay QR — ใช้ external URL เป็น fallback ถ้าไม่มีไฟล์ local
    qr_html = (
        f'<a href="{qr_href}" target="_blank" rel="noopener" style="display:block;margin:.75rem 0;text-align:center;">'
        f'<img src="{qr}" alt="QR PromptPay" loading="lazy" '
        f'style="width:100%;max-width:160px;border-radius:8px;display:block;margin:0 auto;" '
        f'onerror="this.onerror=null;this.style.display=\'none\'">'
        f'</a>'
        f'<p style="font-size:.8rem;color:#475569;text-align:center;margin:.25rem 0 .5rem;">'
        f'<i class="fas fa-mobile-alt"></i> พร้อมเพย์: <strong>0922098134</strong></p>'
    )

    return (
        f'<aside class="sidebar">\n'
        f'  <div style="background:#fff;border-radius:12px;border:1px solid #e2e8f0;'
        f'padding:1.1rem;box-shadow:0 2px 8px rgba(0,0,0,.06);">\n'
        f'    <h2 style="color:#1e40af;font-size:1rem;margin:0 0 .75rem;display:flex;'
        f'align-items:center;gap:.4rem;">'
        f'<i class="fas fa-heart" style="color:#ef4444;"></i> สนับสนุนเรา</h2>\n'
        f'    <p style="font-size:.83rem;color:#64748b;margin:0 0 .6rem;">'
        f'<i class="fas fa-hand-holding-heart" style="color:#fb8c00;"></i> ขอบคุณทุกการสนับสนุน!</p>\n'
        f'    {qr_html}\n'
        f'    <div style="display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center;margin-top:.6rem;">\n'
        f'      {_btn(qr_href, "#0f766e", "fas fa-money-bill-wave", "พร้อมเพย์")}\n'
        f'      {social_html}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</aside>'
    )