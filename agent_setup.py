"""
╔══════════════════════════════════════════════════════════════════════╗
║  agent_setup.py v2 — สร้างเว็บไซต์ใหม่ตั้งแต่ศูนย์               ║
║                                                                      ║
║  python agent_setup.py             → Wizard ถามตอบ (แนะนำ)         ║
║  python agent_setup.py --auto      → AI ออกแบบให้ทุกส่วนเลย        ║
║  python agent_setup.py --manual    → เลือกเองทุกขั้นตอน            ║
║  python agent_setup.py --dry-run   → ดูโครงสร้าง ไม่สร้างไฟล์     ║
║                                                                      ║
║  ประเภทเว็บที่รองรับ:                                               ║
║  blog / news / food / health / tech / lifestyle / ecommerce          ║
║  portfolio / restaurant / clinic / school / landing / custom         ║
╚══════════════════════════════════════════════════════════════════════╝

สิ่งที่สร้าง:
  style.css, nav.js, index.html, หน้าหมวดทุกหน้า,
  contact.html, privacy.html, robots.txt, .gitignore, config.py (ใหม่)
"""
import os, sys, re, json, datetime, random
from pathlib import Path

try:
    from config import (
        BASE_PATH, SITE_URL, SITE_NAME, CATEGORIES, CATEGORY_PAGE_MAP,
        หมวด_ไทย, DRY_RUN, log, log_ok, log_warn, log_err, log_info, log_section,
        เรียก_ollama, เรียก_ollama_เร็ว,
        สร้าง_sidebar_html,   # ← sidebar กลาง ใช้ร่วมกับ agent_writer
    )
except ImportError:
    BASE_PATH = Path(__file__).parent.resolve()
    DRY_RUN   = "--dry-run" in sys.argv
    SITE_NAME = "เว็บไซต์ใหม่"
    SITE_URL  = "https://example.vercel.app"
    CATEGORIES = []
    CATEGORY_PAGE_MAP = {}
    หมวด_ไทย = {}
    def _ts(): return datetime.datetime.now().strftime("%H:%M:%S")
    def log(m):         print(f"[{_ts()}] {m}")
    def log_ok(m):      print(f"[{_ts()}] ✅ {m}")
    def log_warn(m):    print(f"[{_ts()}] ⚠️  {m}")
    def log_err(m):     print(f"[{_ts()}] ❌ {m}")
    def log_info(m):    print(f"[{_ts()}] ℹ️  {m}")
    def log_section(m): print(f"\n{'='*60}\n  {m}\n{'='*60}")
    def เรียก_ollama(p, **kw): return ""
    def เรียก_ollama_เร็ว(p, **kw): return ""
    def สร้าง_sidebar_html(**kw): return ""  # ← fallback ป้องกัน NameError


# ══════════════════════════════════════════════════════════════
# 🎨 ชุดสีสำเร็จรูป (10 ธีม)
# ══════════════════════════════════════════════════════════════
COLOR_THEMES = {
    "slate_indigo": {"label":"Slate Indigo — บล็อกทั่วไป (แนะนำ)","primary":"#1e40af","secondary":"#3b82f6","bg":"#f1f5f9","dark":"#0f172a","accent":"#dbeafe"},
    "navy_gold":    {"label":"Navy + Gold — หรูหรา เป็นทางการ","primary":"#1e3a5f","secondary":"#c9a227","bg":"#f8f9fa","dark":"#1a2535","accent":"#e8d5a3"},
    "forest_green": {"label":"Forest Green — ธรรมชาติ สุขภาพ","primary":"#2d6a4f","secondary":"#40916c","bg":"#f0fdf4","dark":"#1b4332","accent":"#b7e4c7"},
    "royal_purple": {"label":"Royal Purple — ดูดวง ลึกลับ","primary":"#6d28d9","secondary":"#8b5cf6","bg":"#faf5ff","dark":"#3b0764","accent":"#ede9fe"},
    "sunset_red":   {"label":"Sunset Red — ข่าว บันเทิง","primary":"#dc2626","secondary":"#ef4444","bg":"#fff5f5","dark":"#7f1d1d","accent":"#fecaca"},
    "ocean_blue":   {"label":"Ocean Blue — เทคโนโลยี AI","primary":"#1d4ed8","secondary":"#3b82f6","bg":"#eff6ff","dark":"#1e3a8a","accent":"#bfdbfe"},
    "warm_orange":  {"label":"Warm Orange — อาหาร ท่องเที่ยว","primary":"#ea580c","secondary":"#fb923c","bg":"#fff7ed","dark":"#7c2d12","accent":"#fed7aa"},
    "midnight":     {"label":"Midnight Dark — Modern Dark Mode","primary":"#6366f1","secondary":"#818cf8","bg":"#0f172a","dark":"#020617","accent":"#312e81"},
    "sakura_pink":  {"label":"Sakura Pink — ความงาม แฟชั่น","primary":"#db2777","secondary":"#ec4899","bg":"#fdf2f8","dark":"#831843","accent":"#fbcfe8"},
    "teal_cyan":    {"label":"Teal Cyan — กีฬา ไลฟ์สไตล์","primary":"#0d9488","secondary":"#14b8a6","bg":"#f0fdfa","dark":"#134e4a","accent":"#99f6e4"},
    "charcoal":     {"label":"Charcoal — Portfolio ดูดี","primary":"#374151","secondary":"#6b7280","bg":"#f9fafb","dark":"#111827","accent":"#e5e7eb"},
    "emerald_shop": {"label":"Emerald — ร้านค้า Ecommerce","primary":"#059669","secondary":"#10b981","bg":"#ecfdf5","dark":"#064e3b","accent":"#a7f3d0"},
}

NAV_STYLES = {
    "top_full":   "นาวบาร์เต็มความกว้าง พื้นสีเข้ม ลิงก์สีขาว (แนะนำ)",
    "top_glass":  "นาวบาร์กระจก/โปร่งแสง backdrop-blur สวยงาม",
    "sidebar":    "เมนูด้านข้าง (sidebar) เหมาะกับเว็บที่มีหมวดมาก",
    "minimal":    "นาวบาร์เรียบ เน้นข้อความ สีขาว ไม่มีเงา",
    "centered":   "นาวบาร์กึ่งกลาง Logo ตรงกลาง เมนูด้านล่าง",
}

FONT_PAIRS = {
    "sarabun":   {"label":"Sarabun — อ่านง่าย ทันสมัย (แนะนำ)","url":"https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap","body":"'Sarabun', sans-serif"},
    "noto_sans": {"label":"Noto Sans Thai — เป็นทางการ","url":"https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap","body":"'Noto Sans Thai', sans-serif"},
    "kanit":     {"label":"Kanit — Bold โดดเด่น","url":"https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap","body":"'Kanit', sans-serif"},
    "prompt":    {"label":"Prompt — เทคโนโลยี Modern","url":"https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap","body":"'Prompt', sans-serif"},
    "mitr":      {"label":"Mitr — เป็นกันเอง น่ารัก","url":"https://fonts.googleapis.com/css2?family=Mitr:wght@300;400;500;600;700&display=swap","body":"'Mitr', sans-serif"},
}

LAYOUT_OPTIONS = {
    "grid":     {"label":"Grid — การ์ดตาราง 3 คอลัมน์ (แนะนำ)","css":"display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.25rem;","img_h":"180px"},
    "list":     {"label":"List — เรียงแนวตั้ง รูปซ้าย ข้อความขวา","css":"display:flex;flex-direction:column;gap:.75rem;","img_h":"88px","img_w":"130px"},
    "magazine": {"label":"Magazine — ใหญ่ 1 + เล็ก 4 แบบนิตยสาร","css":"display:grid;grid-template-columns:1fr 1fr;gap:1rem;","img_h":"220px"},
    "masonry":  {"label":"Masonry — ไม่เท่ากัน สวยงาม (CSS columns)","css":"column-count:3;column-gap:1rem;","img_h":"auto"},
}

DARK_MODE_OPTIONS = {
    "none":   "ไม่มี Dark Mode",
    "toggle": "มีปุ่มสลับ Dark/Light (แนะนำ)",
    "auto":   "ตามระบบ OS อัตโนมัติ (prefers-color-scheme)",
}

# ── ประเภทเว็บ (Web Types) ──────────────────────────────────────
WEB_TYPES = {
    "blog":       {"label":"📝 บล็อก / สาระความรู้ทั่วไป","cats":["news","lifestyle","health","food","finance","technology","entertainment"],"rss":True},
    "news":       {"label":"📰 เว็บข่าว / สำนักข่าว","cats":["news","politics","business","sport","entertainment","technology","health"],"rss":True},
    "food":       {"label":"🍜 เว็บอาหาร / สูตรอาหาร","cats":["food","health","lifestyle","travel","beauty","diy"],"rss":False},
    "health":     {"label":"💚 สุขภาพ / wellness","cats":["health","food","sport","beauty","lifestyle","education"],"rss":False},
    "tech":       {"label":"💻 เทคโนโลยี / AI / Gaming","cats":["technology","ai","gaming","education","business","finance"],"rss":True},
    "lifestyle":  {"label":"✨ ไลฟ์สไตล์ / แฟชั่น","cats":["lifestyle","beauty","food","travel","health","finance","pet"],"rss":False},
    "education":  {"label":"📚 ความรู้ / การศึกษา","cats":["education","health","finance","technology","lifestyle","law"],"rss":False},
    "ecommerce":  {"label":"🛒 ร้านค้าออนไลน์ / รีวิวสินค้า","cats":["shopping","beauty","health","food","diy","technology","pet","car"],"rss":False},
    "portfolio":  {"label":"🎨 Portfolio / แสดงผลงาน","cats":["portfolio","design","photography","art","technology"],"rss":False},
    "restaurant": {"label":"🍽️ ร้านอาหาร / คาเฟ่","cats":["menu","promotion","event","review","about"],"rss":False},
    "clinic":     {"label":"🏥 คลินิก / โรงพยาบาล","cats":["service","health","beauty","faq","doctor","news"],"rss":False},
    "school":     {"label":"🏫 โรงเรียน / สถาบัน","cats":["news","course","event","teacher","faq","gallery"],"rss":False},
    "landing":    {"label":"🚀 Landing Page / สินค้า/บริการเดียว","cats":["feature","pricing","review","faq","contact"],"rss":False},
    "travel":     {"label":"✈️ ท่องเที่ยว / รีวิวที่เที่ยว","cats":["travel","food","hotel","tip","review","gallery"],"rss":True},
    "custom":     {"label":"⚙️ กำหนดเอง (เลือกหมวดเอง)","cats":[],"rss":True},
}

# หมวดทั้งหมดที่มี
ALL_CATS = {
    "news":"ข่าวสาร","politics":"การเมือง","business":"ธุรกิจ","sport":"กีฬา",
    "entertainment":"บันเทิง","technology":"เทคโนโลยี","health":"สุขภาพ",
    "food":"อาหาร","lifestyle":"ไลฟ์สไตล์","finance":"การเงิน",
    "travel":"ท่องเที่ยว","beauty":"ความงาม","ai":"AI","gaming":"เกม",
    "education":"การศึกษา","pet":"สัตว์เลี้ยง","diy":"DIY","car":"รถยนต์",
    "horoscope":"ดูดวง","law":"กฎหมาย","anime":"อนิเมะ","music":"ดนตรี",
    "movie":"ภาพยนตร์","mystery":"ปริศนา","ghost":"เรื่องลี้ลับ",
    "shopping":"ช้อปปิ้ง","review":"รีวิว","portfolio":"ผลงาน",
    "design":"ดีไซน์","photography":"ถ่ายภาพ","art":"ศิลปะ",
    "menu":"เมนูอาหาร","promotion":"โปรโมชั่น","event":"กิจกรรม",
    "service":"บริการ","doctor":"แพทย์","faq":"คำถามที่พบบ่อย",
    "course":"หลักสูตร","teacher":"อาจารย์","gallery":"แกลเลอรี่",
    "feature":"คุณสมบัติ","pricing":"ราคา","hotel":"โรงแรม","tip":"เคล็ดลับ",
    "about":"เกี่ยวกับเรา","contact":"ติดต่อ",
}

# RSS feeds สำหรับ auto-select topic
RSS_PRESETS = {
    "th_news": [
        ("ไทยรัฐ",   "https://www.thairath.co.th/rss/news.xml"),
        ("BBC Thai", "https://feeds.bbci.co.uk/thai/rss.xml"),
        ("ข่าวสด",   "https://www.khaosod.co.th/feed"),
    ],
    "tech": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge",  "https://www.theverge.com/rss/index.xml"),
    ],
    "none": [],
}


# ══════════════════════════════════════════════════════════════
# 🤖 AI ออกแบบเว็บ
# ══════════════════════════════════════════════════════════════
def ai_ออกแบบ(ชื่อเว็บ: str, เกี่ยวกับ: str, กลุ่มเป้าหมาย: str, web_type: str = "blog") -> dict:
    """ให้ AI ออกแบบทุกส่วนจากข้อมูลเบื้องต้น"""
    log_info("AI กำลังออกแบบเว็บให้...")
    type_cats = WEB_TYPES.get(web_type, WEB_TYPES["blog"])["cats"]
    cat_hint = ", ".join(type_cats[:6]) if type_cats else ", ".join(list(ALL_CATS.keys())[:8])
    prompt = (
        f"ออกแบบเว็บไซต์ภาษาไทยชื่อ '{ชื่อเว็บ}'\n"
        f"ประเภท: {WEB_TYPES.get(web_type,{}).get('label','บล็อก')}\n"
        f"เนื้อหา: {เกี่ยวกับ}\n"
        f"กลุ่มเป้าหมาย: {กลุ่มเป้าหมาย}\n\n"
        f"ตอบ JSON เท่านั้น ไม่มีคำอธิบาย:\n"
        f'{{"color_theme":"<จาก:{list(COLOR_THEMES.keys())}>","font":"<จาก:sarabun|noto_sans|kanit|prompt|mitr>",'
        f'"nav_style":"<จาก:top_full|top_glass|sidebar|minimal|centered>",'
        f'"layout":"<จาก:grid|list|magazine|masonry>",'
        f'"dark_mode":"<จาก:none|toggle|auto>",'
        f'"categories":["<5-7 จาก:{cat_hint}>"],'
        f'"tagline":"<สโลแกนภาษาไทย 1 ประโยค>",'
        f'"desc":"<คำอธิบาย 1-2 ประโยค>",'
        f'"hero_title":"<หัวข้อใหญ่หน้าแรก>",'
        f'"hero_subtitle":"<คำอธิบายย่อย>"}}'
    )
    raw = เรียก_ollama(prompt, timeout=90, num_predict=500)
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    match = re.search(r'\{.*?\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    # Fallback
    type_def = WEB_TYPES.get(web_type, WEB_TYPES["blog"])
    return {
        "color_theme": "emerald_shop" if web_type == "ecommerce" else "charcoal" if web_type == "portfolio" else "slate_indigo",
        "font": "sarabun",
        "nav_style": "top_full",
        "layout": "grid",
        "dark_mode": "toggle",
        "categories": type_def["cats"][:6] or ["news","lifestyle","health","food","technology"],
        "tagline": f"{ชื่อเว็บ} — {เกี่ยวกับ}",
        "desc": f"เว็บไซต์รวม{เกี่ยวกับ} คุณภาพสูง อัปเดตทุกวัน",
        "hero_title": f"ยินดีต้อนรับสู่ {ชื่อเว็บ}",
        "hero_subtitle": f"แหล่งรวม{เกี่ยวกับ} ที่ดีที่สุด",
    }


# ══════════════════════════════════════════════════════════════
# 🧙 Wizard — ถาม-ตอบ (default mode)
# ══════════════════════════════════════════════════════════════
def wizard() -> dict:
    log_section("🧙 Setup Wizard — สร้างเว็บใหม่")
    print("  ตอบ 6 คำถาม แล้ว AI จะออกแบบที่เหลือให้อัตโนมัติ\n")

    def ask(q, default=""):
        try:
            val = input(f"  {q}" + (f" [{default}]" if default else "") + ": ").strip()
            return val or default
        except (EOFError, KeyboardInterrupt):
            return default

    def choose_num(title, options: dict, default_key: str = "") -> str:
        print(f"\n  {title}:")
        keys = list(options.keys())
        for i, (k, v) in enumerate(options.items(), 1):
            label = v if isinstance(v, str) else v.get("label", k)
            mark = " ◀ แนะนำ" if k == default_key else ""
            print(f"    {i:>2}. {label}{mark}")
        try:
            sel = input(f"  เลือก (1-{len(keys)}): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(keys):
                return keys[int(sel) - 1]
        except (EOFError, KeyboardInterrupt, ValueError):
            pass
        return default_key or keys[0]

    ชื่อเว็บ      = ask("ชื่อเว็บไซต์ของคุณ?", "เว็บใหม่ของฉัน")
    url_เว็บ      = ask("URL เว็บ (Vercel/GitHub Pages)?", "https://mysite.vercel.app")
    เกี่ยวกับ     = ask("เว็บนี้เกี่ยวกับอะไร? (อธิบายสั้นๆ)", "บทความความรู้ทั่วไป")
    กลุ่มเป้า    = ask("กลุ่มเป้าหมาย?", "คนไทยทั่วไป")
    base_path_str = ask("โฟลเดอร์โปรเจกต์?", str(BASE_PATH))

    # เลือกประเภทเว็บ
    web_type = choose_num("🌐 ประเภทเว็บไซต์", {k: v["label"] for k, v in WEB_TYPES.items()}, "blog")

    config = {
        "site_name": ชื่อเว็บ, "site_url": url_เว็บ, "about": เกี่ยวกับ,
        "target": กลุ่มเป้า, "base_path": base_path_str, "web_type": web_type, "mode": "wizard",
    }
    log_info("AI กำลังออกแบบ...")
    design = ai_ออกแบบ(ชื่อเว็บ, เกี่ยวกับ, กลุ่มเป้า, web_type)
    config.update(design)

    theme = COLOR_THEMES.get(config.get("color_theme","slate_indigo"), COLOR_THEMES["slate_indigo"])
    print(f"\n  {'─'*54}")
    print(f"  📋 แผนการออกแบบ (AI เลือกให้):")
    print(f"  ชื่อเว็บ     : {ชื่อเว็บ}")
    print(f"  ประเภท       : {WEB_TYPES.get(web_type,{}).get('label','')}")
    print(f"  สีโทน       : {theme['label']}")
    print(f"  ฟอนต์       : {FONT_PAIRS.get(config.get('font','sarabun'),FONT_PAIRS['sarabun'])['label']}")
    print(f"  นาวบาร์     : {NAV_STYLES.get(config.get('nav_style','top_full'))}")
    print(f"  Layout      : {LAYOUT_OPTIONS.get(config.get('layout','grid'),{}).get('label','Grid')}")
    print(f"  Dark Mode   : {DARK_MODE_OPTIONS.get(config.get('dark_mode','none'))}")
    print(f"  หมวดหมู่    : {', '.join(config.get('categories',[]))}")
    print(f"  สโลแกน     : {config.get('tagline','')}")
    print(f"  {'─'*54}\n")

    try:
        ยืนยัน = input("  เริ่มสร้างเว็บเลยไหม? (Enter=ใช่ / n=ยกเลิก): ").strip().lower()
        if ยืนยัน in ("n", "no", "ไม่"):
            log_warn("ยกเลิก"); return {}
    except (EOFError, KeyboardInterrupt):
        pass
    return config


# ══════════════════════════════════════════════════════════════
# 🎛️ Manual — เลือกเองทุกส่วน
# ══════════════════════════════════════════════════════════════
def manual() -> dict:
    log_section("🎛️  Manual Setup — เลือกเองทุกส่วน")

    def ask(q, default=""):
        try:
            val = input(f"  {q}" + (f" [{default}]" if default else "") + ": ").strip()
            return val or default
        except (EOFError, KeyboardInterrupt):
            return default

    def choose(title, options: dict, default_key: str = "") -> str:
        print(f"\n  {title}:")
        keys = list(options.keys())
        for i, (k, v) in enumerate(options.items(), 1):
            label = v if isinstance(v, str) else v.get("label", k)
            mark = " ◀ แนะนำ" if k == default_key else ""
            print(f"    {i:>2}. {label}{mark}")
        try:
            _def_idx = (list(keys).index(default_key) + 1) if default_key in keys else 1
            sel = input(f"  เลือก (1-{len(keys)}, Enter={_def_idx}): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(keys):
                return keys[int(sel) - 1]
        except (EOFError, KeyboardInterrupt, ValueError):
            pass
        return default_key or keys[0]

    # ── ข้อมูลพื้นฐาน ──────────────────────────────────────────
    ชื่อเว็บ      = ask("ชื่อเว็บไซต์", "เว็บใหม่")
    url_เว็บ      = ask("URL เว็บ", "https://mysite.vercel.app")
    สโลแกน       = ask("สโลแกน / คำอธิบายสั้น", f"{ชื่อเว็บ} — แหล่งความรู้ครบครัน")
    desc          = ask("คำอธิบายเว็บ (SEO)", f"เว็บไซต์รวมบทความคุณภาพสูง อัปเดตทุกวัน")
    hero_title    = ask("หัวข้อใหญ่หน้าแรก", f"ยินดีต้อนรับสู่ {ชื่อเว็บ}")
    hero_subtitle = ask("คำอธิบายย่อยหน้าแรก", "แหล่งความรู้ครบครันที่ดีที่สุด")
    base_path_str = ask("โฟลเดอร์โปรเจกต์", str(BASE_PATH))

    # ── ประเภทเว็บ ──────────────────────────────────────────────
    web_type = choose("🌐 ประเภทเว็บไซต์", {k: v["label"] for k, v in WEB_TYPES.items()}, "blog")

    # ── ออกแบบ ──────────────────────────────────────────────────
    color_theme = choose("🎨 โทนสี", {k: v["label"] for k, v in COLOR_THEMES.items()}, "slate_indigo")
    font        = choose("🔤 ฟอนต์", {k: v["label"] for k, v in FONT_PAIRS.items()}, "sarabun")
    nav_style   = choose("📋 สไตล์นาวบาร์", NAV_STYLES, "top_full")
    layout      = choose("📐 Layout บทความ", {k: v["label"] for k, v in LAYOUT_OPTIONS.items()}, "grid")
    dark_mode   = choose("🌙 Dark Mode", DARK_MODE_OPTIONS, "toggle")

    # ── หมวดหมู่ ─────────────────────────────────────────────────
    type_cats = WEB_TYPES.get(web_type, {}).get("cats", [])
    if type_cats:
        print(f"\n  หมวดแนะนำสำหรับ {WEB_TYPES[web_type]['label']}: {', '.join(type_cats)}")
        use_preset = ask("ใช้หมวดแนะนำเลยไหม? (Enter=ใช่ / n=เลือกเอง)", "y").lower()
        if use_preset in ("n", "no", "ไม่"):
            type_cats = []

    if not type_cats:
        print(f"\n  หมวดที่มีทั้งหมด:")
        cat_list = list(ALL_CATS.items())
        for i, (k, v) in enumerate(cat_list, 1):
            print(f"  {i:>3}. {k:<15} {v}", end="\n" if i % 3 == 0 else "  ")
        print()
        cat_input = ask("พิมพ์หมวดที่ต้องการ (คั่นด้วย comma)", "news,lifestyle,health,food,technology")
        type_cats = [c.strip() for c in cat_input.split(",") if c.strip() in ALL_CATS]
        if not type_cats:
            type_cats = ["news", "lifestyle", "health", "food"]

    print(f"\n  หมวดที่เลือก: {', '.join(type_cats)}")

    # ── RSS Feeds ────────────────────────────────────────────────
    use_rss = WEB_TYPES.get(web_type, {}).get("rss", True)
    rss_preset = "th_news" if use_rss else "none"
    if use_rss:
        rss_choice = choose("📡 RSS Feeds สำหรับดึงข่าว", {
            "th_news": "ไทยรัฐ + BBC Thai + ข่าวสด (แนะนำ)",
            "tech":    "TechCrunch + The Verge",
            "none":    "ไม่ใช้ RSS (AI เลือกหัวข้อเอง)",
        }, "th_news")
        rss_preset = rss_choice

    return {
        "site_name": ชื่อเว็บ, "site_url": url_เว็บ,
        "base_path": base_path_str, "web_type": web_type,
        "tagline": สโลแกน, "desc": desc,
        "hero_title": hero_title, "hero_subtitle": hero_subtitle,
        "color_theme": color_theme, "font": font,
        "nav_style": nav_style, "layout": layout, "dark_mode": dark_mode,
        "categories": type_cats, "rss_preset": rss_preset, "mode": "manual",
    }


# ══════════════════════════════════════════════════════════════
# 🏗️ สร้างไฟล์จริง
# ══════════════════════════════════════════════════════════════
def สร้างเว็บ(config: dict):
    site_name  = config.get("site_name", "เว็บใหม่")
    site_url   = config.get("site_url", "https://mysite.vercel.app")
    tagline    = config.get("tagline", site_name)
    desc       = config.get("desc", "เว็บไซต์คุณภาพสูง")
    hero_title = config.get("hero_title", f"ยินดีต้อนรับสู่ {site_name}")
    hero_sub   = config.get("hero_subtitle", "แหล่งความรู้ครบครัน")
    cats       = config.get("categories") or ["news","lifestyle","health","food","technology"]
    # กรองเฉพาะหมวดที่รู้จัก (ป้องกัน AI ส่งค่าแปลกมา)
    cats = [c for c in cats if c and isinstance(c, str)]
    if not cats:
        cats = WEB_TYPES.get(config.get("web_type","blog"), WEB_TYPES["blog"])["cats"][:6] or ["news","lifestyle","health","food","technology"]
    web_type   = config.get("web_type", "blog")
    layout_key = config.get("layout", "grid")
    dark_mode  = config.get("dark_mode", "toggle")
    rss_preset = config.get("rss_preset", "th_news" if WEB_TYPES.get(web_type, {}).get("rss") else "none")

    base = Path(config.get("base_path", str(BASE_PATH)))
    base.mkdir(parents=True, exist_ok=True)
    (base / "images" / "thumbs").mkdir(parents=True, exist_ok=True)

    # ── โหลด theme/colors ก่อน (ต้องอยู่ก่อน og_svg) ───────────────────────
    theme    = COLOR_THEMES.get(config.get("color_theme", "slate_indigo"), COLOR_THEMES["slate_indigo"])
    font_cfg = FONT_PAIRS.get(config.get("font", "sarabun"), FONT_PAIRS["sarabun"])
    nav_sty  = config.get("nav_style", "top_full")
    layout   = LAYOUT_OPTIONS.get(layout_key, LAYOUT_OPTIONS["grid"])

    primary   = theme["primary"]
    secondary = theme["secondary"]
    bg        = theme["bg"]
    dark      = theme["dark"]
    accent    = theme["accent"]

    # ── og-default.svg (fallback og:image เวลา share) ────────────────────────
    og_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <rect width="1200" height="630" fill="{primary}"/>
  <rect x="60" y="60" width="1080" height="510" rx="24" fill="{dark}" opacity="0.6"/>
  <text x="600" y="290" fill="#ffffff" font-family="sans-serif" font-size="72" font-weight="bold" text-anchor="middle">{site_name}</text>
  <text x="600" y="380" fill="#cbd5e1" font-family="sans-serif" font-size="32" text-anchor="middle">{tagline[:60]}</text>
  <text x="600" y="440" fill="#94a3b8" font-family="sans-serif" font-size="24" text-anchor="middle">{site_url}</text>
</svg>'''
    _write(base / "images" / "og-default.svg", og_svg)
    # ลิงก์ og:image ชี้ .png แต่สร้าง .svg ไว้ก่อน (Vercel serve SVG ได้เลย)
    # ถ้าต้องการ .png จริงให้ใช้ ImageMagick: convert og-default.svg og-default.png
    # ลอง rasterize เป็น PNG จริงด้วย Pillow (ถ้ามี)
    if not DRY_RUN:
        _og_png = base / "images" / "og-default.png"
        _og_svg_path = base / "images" / "og-default.svg"
        _converted = False
        try:
            from PIL import Image
            import io, subprocess
            # ลอง cairosvg ก่อน
            try:
                import cairosvg
                cairosvg.svg2png(url=str(_og_svg_path), write_to=str(_og_png), output_width=1200, output_height=630)
                _converted = True
            except ImportError:
                pass
            # ถ้าไม่มี cairosvg ใช้ copy SVG แทน (Vercel serve SVG ได้)
            if not _converted:
                import shutil
                shutil.copy(_og_svg_path, _og_png)
        except Exception:
            import shutil
            shutil.copy(_og_svg_path, _og_png)
    log_ok("สร้าง og-default.svg/png (og:image fallback)")
    (base / "agent_logs").mkdir(parents=True, exist_ok=True)

    is_dark_bg = bg.startswith("#0") or bg.startswith("#1")
    text_main  = "#f1f5f9" if is_dark_bg else "#1e293b"
    text_muted = "#94a3b8" if is_dark_bg else "#64748b"
    card_bg    = "#1e293b" if is_dark_bg else "#ffffff"
    border_c   = "#334155" if is_dark_bg else "#e2e8f0"
    soft_c     = "#1e293b" if is_dark_bg else "#f1f5f9"

    # ── Nav CSS ─────────────────────────────────────────────────
    nav_css = {
        "top_full":  f"background:{primary};",
        "top_glass": "background:rgba(15,23,42,0.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);",
        "sidebar":   f"background:{dark};",
        "minimal":   f"background:#fff;border-bottom:2px solid {primary};",
        "centered":  f"background:{primary};text-align:center;",
    }.get(nav_sty, f"background:{primary};")
    nav_text = "#fff" if nav_sty not in ("minimal",) else primary

    # ── Dark Mode CSS ────────────────────────────────────────────
    dark_css = ""
    dark_toggle_html = ""
    if dark_mode == "toggle":
        dark_css = f"""
/* Dark Mode Toggle */
body.dark-mode {{
  --bg: #0f172a; --card: #1e293b; --text: #f1f5f9;
  --muted: #94a3b8; --border: #334155; --soft: #1e293b;
}}
.dark-toggle {{
  cursor:pointer; background:none; border:2px solid rgba(255,255,255,.5);
  color:#fff; border-radius:999px; padding:.3rem .7rem; font-size:.82rem;
  transition:all .2s; margin-left:.5rem;
}}
.dark-toggle:hover {{ background:rgba(255,255,255,.15); }}"""
        dark_toggle_html = "<button class='dark-toggle' onclick='toggleDark()' title='สลับ Dark/Light Mode'>🌙</button>"
    elif dark_mode == "auto":
        dark_css = f"""
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0f172a; --card: #1e293b; --text: #f1f5f9;
    --muted: #94a3b8; --border: #334155; --soft: #1e293b;
  }}
}}"""

    dark_js = ""
    if dark_mode == "toggle":
        dark_js = """
function toggleDark() {
  document.body.classList.toggle('dark-mode');
  var btn = document.querySelector('.dark-toggle');
  if (btn) btn.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
  try { localStorage.setItem('darkMode', document.body.classList.contains('dark-mode') ? '1' : '0'); } catch(e) {}
}
(function(){ try { if(localStorage.getItem('darkMode')==='1') { document.body.classList.add('dark-mode'); var b=document.querySelector('.dark-toggle'); if(b) b.textContent='☀️'; } } catch(e) {} })();"""

    # ── CSS Layout ──────────────────────────────────────────────
    layout_article_css = layout["css"]
    if layout_key == "masonry":
        layout_article_css = "column-count:3;column-gap:1rem;"
        layout_article_css += "\n@media(max-width:860px){.article-grid{column-count:2;}}"
        layout_article_css += "\n@media(max-width:560px){.article-grid{column-count:1;}}"

    # ── style.css ────────────────────────────────────────────────
    css = f"""/* {site_name} — style.css — สร้างโดย agent_setup.py v2 */
@import url('{font_cfg["url"]}');

:root{{
  --primary:   {primary};
  --secondary: {secondary};
  --bg:        {bg};
  --dark:      {dark};
  --accent:    {accent};
  --card:      {card_bg};
  --border:    {border_c};
  --text:      {text_main};
  --muted:     {text_muted};
  --soft:      {soft_c};
  --font:      {font_cfg["body"]};
}}
{dark_css}

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{
  font-family:var(--font);background:var(--bg);color:var(--text);
  line-height:1.7;font-size:16px;min-height:100vh;transition:background .3s,color .3s;
}}

/* ── NAV ── */
nav{{
  {nav_css}
  padding:.75rem 1.5rem;
  position:sticky;top:0;z-index:100;
  box-shadow:0 2px 12px rgba(0,0,0,.18);
}}
.nav-inner{{
  max-width:1100px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;
}}
{"" if nav_sty != "centered" else ".nav-inner{flex-direction:column;text-align:center;}"}
.nav-brand{{
  font-size:1.25rem;font-weight:800;color:{nav_text};text-decoration:none;letter-spacing:-.5px;
}}
.nav-links{{
  display:flex;flex-wrap:wrap;gap:.2rem;list-style:none;align-items:center;
}}
.nav-links a{{
  color:{nav_text};text-decoration:none;padding:.4rem .75rem;border-radius:6px;
  font-size:.88rem;font-weight:500;transition:background .18s;opacity:.9;
}}
.nav-links a:hover,.nav-links a.active{{background:rgba(255,255,255,.2);opacity:1;}}
{"" if nav_sty != "minimal" else f".nav-links a:hover{{background:{accent};color:{primary};opacity:1;}}"}

/* ── CONTAINER ── */
.container{{max-width:1100px;margin:0 auto;padding:1.5rem 1rem;
  display:grid;grid-template-columns:1fr 320px;gap:1.5rem;}}
@media(max-width:860px){{
  .container{{grid-template-columns:1fr;}}
  .sidebar{{display:none;}}
}}

/* ── HERO ── */
.hero{{
  background:linear-gradient(135deg,{primary},{dark});
  color:#fff;padding:3rem 1.5rem;text-align:center;
}}
.hero h1{{font-size:clamp(1.6rem,4vw,2.6rem);font-weight:800;margin-bottom:.75rem;line-height:1.2;}}
.hero p{{font-size:1rem;opacity:.9;max-width:600px;margin:0 auto 1.5rem;}}
.hero-btn{{
  display:inline-block;background:#fff;color:{primary};
  padding:.7rem 1.8rem;border-radius:999px;font-weight:700;
  text-decoration:none;font-size:.95rem;transition:transform .2s,box-shadow .2s;
}}
.hero-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.2);}}

/* ── CARDS / LAYOUT ── */
.article-grid{{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:1.25rem;
}}
@media(max-width:900px){{.article-grid{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:560px){{.article-grid{{grid-template-columns:1fr;}}}}
{"/* masonry */.article-grid{display:block;column-count:3;column-gap:1rem;}@media(max-width:860px){.article-grid{column-count:2;}}@media(max-width:560px){.article-grid{column-count:1;}}" if layout_key == "masonry" else ""}
{"/* list layout */.article-grid{display:flex;flex-direction:column;gap:.75rem;}" if layout_key == "list" else ""}
{"/* magazine: first card full width */.article-grid{grid-template-columns:repeat(2,1fr);}.article-grid>a:first-child{grid-column:1/-1;}.article-grid>a:first-child img{height:300px;}" if layout_key == "magazine" else ""}
.news-card,.article-card{{
  background:var(--card);border-radius:12px;overflow:hidden;
  border:1px solid var(--border);box-shadow:0 2px 8px rgba(0,0,0,.06);
  transition:transform .2s,box-shadow .2s;
  {"break-inside:avoid;margin-bottom:1rem;" if layout_key == "masonry" else ""}
}}
.news-card:hover,.article-card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.12);}}
.article-card.content-area{{padding:1.5rem;}}
{"/* Magazine: first card full width */ .article-grid > a:first-child{{grid-column:1/-1;}} .article-grid > a:first-child img{{height:300px;}}" if layout_key == "magazine" else ""}

/* ── ARTICLE CONTENT ── */
.article-meta{{color:var(--muted);font-size:.85rem;margin:.5rem 0 1.25rem;}}
.article-meta a{{color:var(--primary);text-decoration:none;}}
.hero-image-wrapper img{{width:100%;max-height:450px;object-fit:cover;border-radius:12px;margin-bottom:1.5rem;}}
.article-body{{line-height:1.85;}}
.article-body h2{{color:var(--primary);font-size:1.25rem;margin:2rem 0 .75rem;border-left:4px solid var(--primary);padding-left:.75rem;}}
.article-body h3{{font-size:1.05rem;margin:1.5rem 0 .5rem;color:var(--dark);}}
.article-body p{{margin-bottom:1.1rem;}}
.article-body ul,.article-body ol{{padding-left:1.5rem;margin-bottom:1rem;}}
.article-body li{{margin-bottom:.4rem;}}
.article-body img{{border-radius:10px;max-width:100%;margin:1rem 0;}}
.article-body figure{{margin:1.5rem 0;}}
.article-body figcaption{{font-size:.82rem;color:var(--muted);text-align:center;}}

/* ── SIDEBAR ── */
.sidebar{{display:flex;flex-direction:column;gap:1rem;}}
.ad-section{{background:var(--card);border-radius:12px;padding:1.25rem;border:1px solid var(--border);}}
.support-us{{font-size:.9rem;font-weight:700;color:{primary};display:flex;align-items:center;gap:.5rem;margin-bottom:.75rem;}}
.support-links{{display:flex;flex-direction:column;gap:.4rem;}}
.support-btn{{display:flex;align-items:center;gap:.5rem;padding:.5rem .9rem;border-radius:8px;text-decoration:none;font-size:.88rem;font-weight:600;color:#fff;transition:opacity .2s;}}
.support-btn:hover{{opacity:.85;}}
.qr-code{{max-width:150px;border-radius:8px;}}

/* ── SEARCH ── */
.search-box{{position:relative;margin:.5rem 0 1rem;}}
.search-box input{{
  width:100%;padding:.6rem 1rem .6rem 2.4rem;
  border:1px solid var(--border);border-radius:999px;
  background:var(--soft);color:var(--text);font-family:var(--font);font-size:.9rem;
  outline:none;transition:border-color .2s;
}}
.search-box input:focus{{border-color:var(--primary);}}
.search-box i{{position:absolute;left:.85rem;top:50%;transform:translateY(-50%);color:var(--muted);}}

/* ── BADGE ── */
.cat-badge{{display:inline-block;background:var(--primary);color:#fff;font-size:.72rem;font-weight:700;padding:2px 10px;border-radius:999px;margin-bottom:.5rem;}}

/* ── FOOTER ── */
footer{{background:{dark};color:rgba(255,255,255,.85);text-align:center;padding:2rem 1rem 1.5rem;font-size:.88rem;margin-top:2rem;}}
footer a{{color:rgba(255,255,255,.7);text-decoration:none;}}
footer a:hover{{color:#fff;}}

/* ── RESPONSIVE ── */
@media(max-width:640px){{
  .hero{{padding:2rem 1rem;}}
  .hero h1{{font-size:1.5rem;}}
  nav{{padding:.6rem 1rem;}}
  .article-grid{{grid-template-columns:1fr;column-count:1;}}
  .nav-links{{
    display:none;width:100%;flex-direction:column;gap:0;
    background:rgba(0,0,0,.15);border-radius:8px;margin-top:.5rem;
  }}
  .nav-links.nav-open{{display:flex;}}
  .nav-links li a{{padding:.6rem 1rem;display:block;}}
  .nav-hamburger{{display:block;}}
}}
@media(min-width:641px){{
  .nav-hamburger{{display:none;}}
}}

/* ── HAMBURGER ── */
.nav-hamburger{{
  background:none;border:2px solid rgba(255,255,255,.6);color:#fff;
  border-radius:6px;padding:.25rem .6rem;font-size:1.1rem;cursor:pointer;
  transition:background .2s;
}}
.nav-hamburger:hover{{background:rgba(255,255,255,.15);}}

/* ── UTIL ── */
.text-muted{{color:var(--muted);}} .text-primary{{color:var(--primary);}}
.mt-1{{margin-top:.5rem;}} .mt-2{{margin-top:1rem;}} .mt-3{{margin-top:1.5rem;}}
"""
    _write(base / "style.css", css)
    log_ok("สร้าง style.css")

    # ── nav.js (v6 — sync กับ agent_fix_v6) ─────────────────────
    # สร้าง main cats (8 หมวดหลัก) และ extra cats (ที่เหลือ)
    main_cats_list = cats[:8]
    extra_cats_list = cats[8:]

    main_links_js = ""
    for c in main_cats_list:
        _href = CATEGORY_PAGE_MAP.get(c, c + ".html") if CATEGORY_PAGE_MAP else c + ".html"
        _label = ALL_CATS.get(c, c)
        main_links_js += f'    {{ label: "{_label}", href: "{_href}" }},\n'

    extra_links_js = ""
    for c in extra_cats_list:
        _href = CATEGORY_PAGE_MAP.get(c, c + ".html") if CATEGORY_PAGE_MAP else c + ".html"
        _label = ALL_CATS.get(c, c)
        extra_links_js += f'    {{ label: "{_label}", href: "{_href}" }},\n'

    nav_js = f"""// nav.js — {site_name} v6 — auto-generated
(function() {{
  var SITE_NAME = "{site_name}";
  var PRIMARY   = "{primary}";
  var DARK      = "{dark}";

  var MAIN_CATS = [
{main_links_js}  ];

  var EXTRA_CATS = [
{extra_links_js}  ];

  function renderNav() {{
    var nav = document.querySelector('nav');
    if (!nav) return;

    var currentPage = location.pathname.split('/').pop() || '/';

    var mainHTML = MAIN_CATS.map(function(item) {{
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="color:#fff;text-decoration:none;'
        + 'padding:.4rem .65rem;border-radius:6px;font-size:.88rem;font-weight:600;white-space:nowrap;'
        + (active ? 'background:rgba(255,255,255,.22);' : 'opacity:.88;')
        + 'transition:background .18s;" '
        + 'onmouseover="this.style.background=\\'rgba(255,255,255,.18)\\'" '
        + 'onmouseout="this.style.background=\\'' + (active ? 'rgba(255,255,255,.22)' : '') + '\\';">'
        + item.label + '</a>';
    }}).join('');

    var dropHTML = EXTRA_CATS.map(function(item) {{
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="display:block;padding:.45rem .85rem;'
        + 'color:#1e293b;text-decoration:none;font-size:.85rem;font-weight:' + (active ? '700' : '500') + ';'
        + 'background:' + (active ? '#e0f2fe' : 'transparent') + ';'
        + 'transition:background .15s;" '
        + 'onmouseover="this.style.background=\\'#f1f5f9\\'" '
        + 'onmouseout="this.style.background=\\'' + (active ? '#e0f2fe' : 'transparent') + '\\';">'
        + item.label + '</a>';
    }}).join('');

    nav.style.cssText = 'position:sticky;top:0;z-index:999;background:' + PRIMARY
      + ';box-shadow:0 2px 10px rgba(0,0,0,.22);font-family:Sarabun,sans-serif;';

    var mobileLinks = MAIN_CATS.concat(EXTRA_CATS).map(function(item) {{
      return '<a href="' + item.href + '" style="color:rgba(255,255,255,.88);text-decoration:none;'
        + 'padding:.4rem .6rem;border-radius:6px;font-size:.9rem;font-weight:500;">' + item.label + '</a>';
    }}).join('');

    var extraBtn = EXTRA_CATS.length > 0
      ? '<div class="nav-more" style="position:relative;flex-shrink:0;">'
        + '<button id="nav-more-btn" style="background:rgba(255,255,255,.15);border:none;color:#fff;'
        + 'padding:.38rem .75rem;border-radius:6px;cursor:pointer;font-family:inherit;font-size:.85rem;'
        + 'font-weight:600;display:flex;align-items:center;gap:.35rem;" '
        + 'onclick="(function(){{var d=document.getElementById(\\'nav-more-drop\\');'
        + 'd.style.display=d.style.display===\\'block\\'?\\'none\\':\\'block\\';}})()">เพิ่มเติม <span style="font-size:.65rem;">▼</span></button>'
        + '<div id="nav-more-drop" style="display:none;position:absolute;top:calc(100% + 6px);right:0;'
        + 'background:#fff;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.18);'
        + 'min-width:160px;max-height:70vh;overflow-y:auto;z-index:9999;padding:.35rem 0;">'
        + dropHTML + '</div></div>'
      : '';

    nav.innerHTML = [
      '<div style="max-width:1140px;margin:0 auto;padding:0 1rem;display:flex;align-items:center;gap:.25rem;height:52px;">',
      '<a href="/" style="color:#fff;text-decoration:none;font-size:1.15rem;font-weight:800;',
      'letter-spacing:.02em;margin-right:.75rem;flex-shrink:0;white-space:nowrap;">' + SITE_NAME + '</a>',
      '<div class="nav-main" style="display:flex;align-items:center;gap:.15rem;flex:1;overflow:hidden;flex-wrap:nowrap;">',
      mainHTML,
      '</div>',
      extraBtn,
      '<button id="nav-ham" style="display:none;background:none;border:none;color:#fff;',
      'font-size:1.3rem;cursor:pointer;padding:.3rem .5rem;margin-left:.5rem;" ',
      'onclick="(function(){{var m=document.getElementById(\\'nav-mobile\\');',
      'm.style.display=m.style.display===\\'flex\\'?\\'none\\':\\'flex\\';}})()">☰</button>',
      '</div>',
      '<div id="nav-mobile" style="display:none;flex-direction:column;background:' + DARK + ';',
      'padding:.6rem 1rem 1rem;gap:.2rem;flex-wrap:wrap;">',
      mobileLinks,
      '</div>',
      '<style>@media(max-width:760px){{.nav-main{{display:none!important;}}.nav-more{{display:none!important;}}#nav-ham{{display:block!important;}}}}</style>',
    ].join('');

    document.addEventListener('click', function(e) {{
      var btn  = document.getElementById('nav-more-btn');
      var drop = document.getElementById('nav-more-drop');
      if (drop && btn && !btn.contains(e.target) && !drop.contains(e.target)) {{
        drop.style.display = 'none';
      }}
    }});
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', renderNav);
  }} else {{
    renderNav();
  }}
"""
    _write(base / "nav.js", nav_js)
    log_ok("สร้าง nav.js")

    # ── index.html ────────────────────────────────────────────────
    cat_pills = "".join(
        f'<a href="{c}.html" style="display:inline-flex;align-items:center;gap:.35rem;'
        f'padding:.45rem 1rem;background:rgba(255,255,255,.15);color:#fff;border-radius:999px;'
        f'text-decoration:none;font-size:.85rem;font-weight:600;transition:background .2s;"'
        f' onmouseover="this.style.background=\'rgba(255,255,255,.3)\'" onmouseout="this.style.background=\'rgba(255,255,255,.15)\'">'
        f'<i class="fas fa-tag" style="font-size:.75rem;"></i> {ALL_CATS.get(c, c)}</a>'
        for c in cats[:8]
    )
    ga4 = os.getenv("GA4_ID", "")
    _idx_ld = json.dumps({
        "@context":"https://schema.org","@type":"WebSite",
        "name":site_name,"url":site_url,"description":desc,"inLanguage":"th",
        "potentialAction":{"@type":"SearchAction",
            "target":{"@type":"EntryPoint","urlTemplate":f"{site_url}/?s={{search_term_string}}"},
            "query-input":"required name=search_term_string"}
    }, ensure_ascii=False)
    head = _head(site_name, desc, "index.html", site_url, font_cfg["url"], ga4_id=ga4, json_ld=_idx_ld)
    index_html = f"""{head}
<body>
<script src="nav.js"></script>
<div style="background:linear-gradient(135deg,{primary},{dark});color:#fff;padding:3.5rem 1.5rem 2.5rem;text-align:center;">
  <h1 style="font-size:clamp(1.8rem,5vw,2.8rem);font-weight:800;margin-bottom:.75rem;line-height:1.2;">{hero_title}</h1>
  <p style="font-size:1rem;opacity:.9;max-width:600px;margin:0 auto 1.5rem;">{hero_sub}</p>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;margin-bottom:1.5rem;">{cat_pills}</div>
  <div style="max-width:480px;margin:0 auto;position:relative;">
    <i class="fas fa-search" style="position:absolute;left:.85rem;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.7);z-index:1;"></i>
    <input id="search-input" type="text" placeholder="ค้นหาบทความ..." autocomplete="off"
      style="width:100%;padding:.65rem 1rem .65rem 2.4rem;border:none;border-radius:999px;
             background:rgba(255,255,255,.15);color:#fff;font-family:inherit;font-size:.95rem;
             outline:none;backdrop-filter:blur(4px);">
    <div id="search-results" style="position:absolute;top:110%;left:0;right:0;background:var(--card);
         border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.25);z-index:200;overflow:hidden;max-height:360px;overflow-y:auto;"></div>
  </div>
</div>

<div class="container">
  <main>
    <h2 style="color:var(--primary);font-size:1.1rem;margin:0 0 1rem;display:flex;align-items:center;gap:.5rem;">
      <i class="fas fa-fire" style="color:#ef4444;"></i> บทความล่าสุด
    </h2>
    <div id="embedded-articles-list" class="article-grid">
      <p style="color:var(--muted);grid-column:1/-1;padding:2rem;text-align:center;">
        กำลังโหลดบทความ... <br><small>รัน <code>python agent_writer.py --count 5</code> เพื่อสร้างบทความแรก</small>
      </p>
    </div>
  </main>
  <aside class="sidebar">
    {_sidebar_html(primary, site_name)}
  </aside>
</div>

{_footer_html(site_name, site_url, cats)}
</body></html>"""
    # เพิ่ม SW registration ก่อน </body> ใน index.html
    index_html = index_html.replace("</body></html>", """<script>
  try { if ('serviceWorker' in navigator && location.protocol !== 'file:') { navigator.serviceWorker.register('sw.js'); } } catch(e) {}
</script>
</body></html>""")
    _write(base / "index.html", index_html)
    log_ok("สร้าง index.html")

    # ── หน้าหมวด ─────────────────────────────────────────────────
    for cat in cats:
        cat_th = ALL_CATS.get(cat, cat)
        _cat_ld = json.dumps({
            "@context":"https://schema.org","@type":"BreadcrumbList",
            "itemListElement":[
                {"@type":"ListItem","position":1,"name":"หน้าแรก","item":f"{site_url}/"},
                {"@type":"ListItem","position":2,"name":cat_th,"item":f"{site_url}/{cat}.html"}
            ]}, ensure_ascii=False)
        cat_head = _head(f"{cat_th} — {site_name}", f"รวมบทความ{cat_th}คุณภาพสูง อัปเดตทุกวัน", f"{cat}.html", site_url, font_cfg["url"], ga4_id=ga4, json_ld=_cat_ld)
        cat_page = f"""{cat_head}
<body>
<script src="nav.js"></script>
<div style="background:linear-gradient(135deg,{primary},{dark});color:#fff;padding:1.75rem 1.5rem;text-align:center;">
  <h1 style="font-size:1.7rem;font-weight:700;margin:0;">
    <i class="fas fa-tag"></i> {cat_th}
  </h1>
  <p style="margin:.4rem 0 0;opacity:.85;font-size:.9rem;">รวมบทความ{cat_th}คุณภาพสูง อัปเดตทุกวัน</p>
</div>
<div class="container">
  <main>
<!-- ARTICLE_LIST_START -->
<p style="color:var(--muted);padding:2rem;text-align:center;">ยังไม่มีบทความในหมวดนี้ — รัน <code>python agent_writer.py --cat {cat}</code> เพื่อสร้างบทความ</p>
<!-- ARTICLE_LIST_END -->
  </main>
  <aside class="sidebar">
    {_sidebar_html(primary, site_name)}
  </aside>
</div>
{_footer_html(site_name, site_url, cats)}
</body></html>"""
        _write(base / f"{cat}.html", cat_page)
    log_ok(f"สร้างหน้าหมวด: {len(cats)} หน้า")

    # ── contact.html ──────────────────────────────────────────────
    contact_head = _head(f"ติดต่อเรา — {site_name}", f"ติดต่อทีมงาน {site_name}", "contact.html", site_url, font_cfg["url"], ga4_id=ga4)
    contact_html = f"""{contact_head}
<body>
<script src="nav.js"></script>
<div class="container" style="max-width:700px;margin:2rem auto;padding:1.5rem;">
  <div class="article-card content-area">
    <h1 style="color:var(--primary);margin-bottom:1rem;">📬 ติดต่อเรา</h1>
    <p>ขอบคุณที่สนใจติดต่อ <strong>{site_name}</strong></p>
    <div style="margin-top:1.5rem;background:var(--soft);border-radius:12px;padding:1.5rem;">
      <h2 style="color:var(--primary);font-size:1rem;margin-bottom:1rem;">ช่องทางติดต่อ</h2>
      <p>📧 Email: contact@{site_url.replace('https://','').replace('http://','').split('/')[0]}</p>
      <p style="margin-top:.75rem;color:var(--muted);font-size:.9rem;">เราจะตอบกลับภายใน 24-48 ชั่วโมงในวันทำการ</p>
    </div>
    <div style="margin-top:1.5rem;padding:1rem;background:#ecfdf5;border-radius:12px;border-left:4px solid #10b981;">
      <p style="color:#065f46;font-size:.9rem;margin:0;">💡 สำหรับการลงโฆษณาหรือร่วมมือทางธุรกิจ กรุณาระบุในหัวข้ออีเมลว่า "Business"</p>
    </div>
  </div>
</div>
{_footer_html(site_name, site_url, cats)}
</body></html>"""
    _write(base / "contact.html", contact_html)
    log_ok("สร้าง contact.html")

    # ── privacy.html ──────────────────────────────────────────────
    privacy_head = _head(f"นโยบายความเป็นส่วนตัว — {site_name}", f"นโยบายความเป็นส่วนตัวของ {site_name}", "privacy.html", site_url, font_cfg["url"], ga4_id=ga4)
    privacy_html = f"""{privacy_head}
<body>
<script src="nav.js"></script>
<div class="container" style="max-width:700px;margin:2rem auto;padding:1.5rem;">
  <div class="article-card content-area">
    <h1 style="color:var(--primary);margin-bottom:1rem;">🔒 นโยบายความเป็นส่วนตัว</h1>
    <p style="color:var(--muted);font-size:.85rem;">อัปเดตล่าสุด: {datetime.date.today().strftime("%d/%m/%Y")}</p>
    <div class="article-body">
      <h2>การเก็บรวบรวมข้อมูล</h2>
      <p>{site_name} อาจเก็บข้อมูลการใช้งานพื้นฐานเพื่อปรับปรุงบริการ เช่น ประเภทเบราว์เซอร์ และหน้าที่เข้าชม โดยไม่ระบุตัวตนส่วนบุคคล</p>
      <h2>คุกกี้</h2>
      <p>เว็บไซต์นี้อาจใช้คุกกี้เพื่อวิเคราะห์การใช้งาน (Google Analytics) และแสดงโฆษณาที่เกี่ยวข้อง (Google AdSense)</p>
      <h2>การแชร์ข้อมูล</h2>
      <p>เราไม่ขาย แลกเปลี่ยน หรือส่งข้อมูลส่วนตัวของคุณให้บุคคลที่สาม ยกเว้นที่จำเป็นตามกฎหมาย</p>
      <h2>ลิงก์พันธมิตร (Affiliate Links)</h2>
      <p>บางลิงก์ในเว็บไซต์นี้เป็น Affiliate Link เราอาจได้รับค่าคอมมิชชันเล็กน้อยเมื่อคุณซื้อสินค้าผ่านลิงก์เหล่านี้ โดยไม่มีค่าใช้จ่ายเพิ่มสำหรับคุณ</p>
      <h2>ติดต่อเรา</h2>
      <p>หากมีคำถาม กรุณาติดต่อผ่าน <a href="contact.html">หน้าติดต่อเรา</a></p>
    </div>
  </div>
</div>
{_footer_html(site_name, site_url, cats)}
</body></html>"""
    _write(base / "privacy.html", privacy_html)
    log_ok("สร้าง privacy.html")

    # ── robots.txt ────────────────────────────────────────────────
    _write(base / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n")
    log_ok("สร้าง robots.txt")

    # ── sitemap.xml (stub — agent_fix จะ rebuild ให้ครบ) ─────────
    today = datetime.date.today().isoformat()
    sitemap_urls = "\n".join(
        f"""  <url>
    <loc>{site_url}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>{"1.0" if page == "index.html" else "0.8"}</priority>
  </url>"""
        for page in ["index.html"] + [f"{c}.html" for c in cats] + ["contact.html", "privacy.html"]
    )
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_urls}
</urlset>"""
    _write(base / "sitemap.xml", sitemap_xml)
    log_ok("สร้าง sitemap.xml (stub)")

    # ── .gitignore ────────────────────────────────────────────────
    gitignore_content = """# ════════════════════════════════════════════════════════════════
#  .gitignore — auto-generated by agent_setup.py
#  ไฟล์ที่ไม่ควรขึ้น GitHub/Vercel
# ════════════════════════════════════════════════════════════════

# ── 🤖 Python scripts ทุกตัว (agent/fix/patch/inject ฯลฯ) ───────
*.py

# ── 🔑 Secret / API Key ──────────────────────────────────────────
.env
*.env
.env.*
.env.example
secrets.py
api_keys.py

# ── 🐍 Python cache ───────────────────────────────────────────────
__pycache__/
*.py[cod]
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
pip-log.txt

# ── 📦 Node / npm ─────────────────────────────────────────────────
node_modules/
npm-debug.log*
yarn-error.log*
package-lock.json

# ── 🖥️  OS ────────────────────────────────────────────────────────
.DS_Store
.DS_Store?
._*
Thumbs.db
ehthumbs.db
desktop.ini

# ── 🗂️  Venv ──────────────────────────────────────────────────────
venv/
.venv/
env/
.env/
ENV/

# ── 📋 Log / Temp ─────────────────────────────────────────────────
*.log
*.tmp
*.bak
*.swp
*.swo
*.pid
agent_logs/
logs/
audit_report.json

# ── 🛠️  IDE & Editor ──────────────────────────────────────────────
.vscode/
.idea/
*.sublime-project
*.sublime-workspace
.cursor/

# ── 📦 Build output ───────────────────────────────────────────────
dist/
build/
.next/
out/

# ── ☁️  Vercel ─────────────────────────────────────────────────────
.vercel/

# ── 🧪 Test / Draft ───────────────────────────────────────────────
draft_*.html
test_*.html
_draft/
_test/

# ── ⚙️  Config & Secrets ──────────────────────────────────────────
config.py
.site_config.json
.agent_structure.json

# ── 🖼️  Generated files ────────────────────────────────────────────
thumbnails.json
# search-index.json  ← uncomment ถ้าไม่ต้องการ push
"""
    _write(base / ".gitignore", gitignore_content)
    log_ok("สร้าง .gitignore")
    # ── .env.example ──────────────────────────────────────────────
    env_example = f"""# .env.example — คัดลอกไปเป็น .env แล้วใส่ค่าจริง
# รัน: copy .env.example .env  (Windows) / cp .env.example .env (Mac/Linux)

BASE_PATH={str(base)}
SITE_URL={site_url}

# Ollama (AI เขียนบทความ)
OLLAMA_MODEL=scb10x/llama3.1-typhoon2-8b-instruct:latest
OLLAMA_TIMEOUT=180

# Google Analytics GA4 — https://analytics.google.com
GA4_ID=

# Google Search Console — วาง verification code ที่นี่
# หาได้จาก search.google.com/search-console → Settings → Ownership verification → HTML tag
GSC_VERIFY=

# รูปภาพ (ใช้อย่างน้อย 1 อัน)
UNSPLASH_KEY=       # https://unsplash.com/developers (ฟรี 50 req/ชม.)
PEXELS_KEY=         # https://www.pexels.com/api/ (ฟรี 200 req/ชม.)

# Social (ไม่บังคับ)
FB_PAGE_ID=
FB_ACCESS_TOKEN=
LINE_NOTIFY_TOKEN=

# AdSense / Affiliate (ไม่บังคับ)
ADSENSE_PUB=
ADSENSE_SLOT=
LAZADA_AFFILIATE=
SHOPEE_AFFILIATE=
AGODA_AFFILIATE=
YOUTUBE_API_KEY=

# ══════════════════════════════════════════════════════════════
# 🤝 Sidebar "สนับสนุนเรา" — แก้ที่นี่ที่เดียว ทุก agent ใช้ร่วมกัน
# ══════════════════════════════════════════════════════════════

# PromptPay — ใส่เบอร์มือถือหรือเลขบัตรประชาชนที่ผูก PromptPay
PROMPTPAY_NUMBER=

# Social Links — ใส่ URL จริง หรือเว้นว่างเพื่อซ่อนปุ่มนั้น
FACEBOOK_URL=       # เช่น https://www.facebook.com/yourpage
YOUTUBE_URL=        # เช่น https://www.youtube.com/@yourchannel
TIKTOK_URL=         # เช่น https://www.tiktok.com/@youraccount
INSTAGRAM_URL=      # เช่น https://www.instagram.com/yourprofile
LINE_URL=           # เช่น https://line.me/ti/p/~yourID

# ร้านค้า Shopee (หน้าร้านของคุณ)
SHOPEE_STORE_URL=   # เช่น https://shopee.co.th/yourstore
"""
    _write(base / ".env.example", env_example)
    log_ok("สร้าง .env.example")

    # ── manifest.json (PWA) ───────────────────────────────────────
    manifest = json.dumps({
        "name": site_name,
        "short_name": site_name[:12],
        "description": desc,
        "start_url": "/",
        "display": "standalone",
        "background_color": bg,
        "theme_color": primary,
        "lang": "th",
        "icons": [
            {"src": "images/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "images/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
        "categories": ["news", "blog"],
        "screenshots": []
    }, ensure_ascii=False, indent=2)
    _write(base / "manifest.json", manifest)
    log_ok("สร้าง manifest.json (PWA)")

    # ── sw.js (Service Worker — cache-first offline) ──────────────
    sw_cache_ver = datetime.datetime.now().strftime("%Y%m%d%H%M")
    sw_js = f"""// Service Worker — {site_name}
// Cache-first strategy: เปิดเว็บได้แม้ไม่มีเน็ต (อ่านบทความที่เคยเปิดไว้)
const CACHE = 'v{sw_cache_ver}';
const PRECACHE = ['/', 'index.html', 'style.css', 'nav.js', 'search-index.json'];

self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(k => k !== CACHE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(cached => {{
      const network = fetch(e.request).then(res => {{
        if (res && res.status === 200 && res.type === 'basic') {{
          caches.open(CACHE).then(c => c.put(e.request, res.clone()));
        }}
        return res;
      }}).catch(() => cached);
      return cached || network;
    }})
  );
}});
"""
    _write(base / "sw.js", sw_js)
    log_ok("สร้าง sw.js (Service Worker / PWA offline)")

    # ── 404.html ──────────────────────────────────────────────────
    head_404 = _head(f"ไม่พบหน้านี้ — {site_name}", f"ขออภัย ไม่พบหน้าที่คุณต้องการ", "404.html", site_url, font_cfg["url"], ga4_id=ga4)
    page_404 = f"""{head_404}
<body>
<script src="nav.js"></script>
<div style="min-height:70vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:3rem 1.5rem;">
  <div style="font-size:5rem;margin-bottom:1rem;">🔍</div>
  <h1 style="font-size:2rem;color:var(--primary);margin-bottom:.75rem;">404 — ไม่พบหน้านี้</h1>
  <p style="color:var(--muted);max-width:400px;margin-bottom:2rem;">ขออภัย หน้าที่คุณต้องการอาจถูกย้ายหรือลบไปแล้ว ลองค้นหาหรือกลับหน้าแรก</p>
  <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;">
    <a href="index.html" style="background:var(--primary);color:#fff;padding:.65rem 1.5rem;border-radius:8px;text-decoration:none;font-weight:600;">🏠 หน้าแรก</a>
    <a href="javascript:history.back()" style="background:var(--soft);color:var(--text);padding:.65rem 1.5rem;border-radius:8px;text-decoration:none;font-weight:600;">← ย้อนกลับ</a>
  </div>
</div>
{_footer_html(site_name, site_url, cats)}
<script>
  try {{
    if ('serviceWorker' in navigator && location.protocol !== 'file:') {{
      navigator.serviceWorker.register('sw.js');
    }}
  }} catch(e) {{}}
</script>
</body></html>"""
    _write(base / "404.html", page_404)
    log_ok("สร้าง 404.html")

    # ── config.py ใหม่ (สำคัญมาก!) ──────────────────────────────
    rss_list = RSS_PRESETS.get(rss_preset, RSS_PRESETS["th_news"])
    rss_py = repr(rss_list)
    cats_py = repr(cats)
    cat_page_map_py = repr({c: f"{c}.html" for c in cats})

    config_py_content = f'''# config.py — {site_name}
# สร้างโดย agent_setup.py v2 เมื่อ {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
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
BASE_PATH         = Path(r"{str(base)}")
SITE_URL          = "{site_url}"
SITE_NAME         = "{site_name}"
SITE_DESC         = "{tagline}"
CATEGORIES        = {cats_py}
CATEGORY_PAGE_MAP = {cat_page_map_py}
CAT_PAGE_MAP      = CATEGORY_PAGE_MAP
FILE_TYPES        = [".html"]
ART_PATTERN       = "*_*.html"
LANG              = "th"

RSS_FEEDS = {rss_py}

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
def log(m):        print(f"[{{_ts()}}] {{m}}")
def log_ok(m):     print(f"[{{_ts()}}] ✅ {{m}}")
def log_warn(m):   print(f"[{{_ts()}}] ⚠️  {{m}}")
def log_err(m):    print(f"[{{_ts()}}] ❌ {{m}}")
def log_info(m):   print(f"[{{_ts()}}] ℹ️  {{m}}")
def log_ai(m):     print(f"[{{_ts()}}] 🤖 {{m}}")
def log_section(m):print(f"\\n{{'='*55}}\\n  {{m}}\\n{{'='*55}}")

หมวด_ไทย = {{
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
}}

CAT_COLORS = {{
    "health":"#10b981","lifestyle":"#6366f1","finance":"#059669",
    "ai":"#3b82f6","food":"#ef4444","sport":"#f59e0b",
    "horoscope":"#8b5cf6","news":"#4b5563","ghost":"#1e293b",
    "technology":"#2563eb","beauty":"#ec4899","gaming":"#7c3aed",
    "travel":"#0ea5e9","education":"#0891b2","business":"#059669",
}}

AI_SYSTEM_PROMPT = """คุณคือนักเขียนบทความบล็อกภาษาไทยที่เขียนได้เป็นธรรมชาติ อ่านสนุก เหมือนเพื่อนที่รู้เรื่องนั้นดีมาเล่าให้ฟัง
ห้าม: เขียน instruction/คำสั่ง/หมายเหตุลงในบทความ, เริ่มทุกย่อหน้าด้วย "การ...", ใช้ภาษาแข็ง
ต้อง: ตอบด้วยเนื้อหาบทความเท่านั้น, เขียนเหมือนคนไทยจริงๆ มีอารมณ์"""

def เรียก_ollama(prompt: str, timeout: int = None, num_predict: int = 2048, temperature: float = None) -> str:
    if timeout is None: timeout = OLLAMA_TIMEOUT
    if temperature is None: temperature = 0.85
    url = f"{{OLLAMA_HOST}}/api/generate"
    payload = {{
        "model": OLLAMA_MODEL, "system": AI_SYSTEM_PROMPT, "prompt": prompt,
        "stream": False, "options": {{"num_predict": num_predict, "temperature": temperature, "repeat_penalty": 1.15, "top_p": 0.92}}
    }}
    for attempt in range(1, 3):
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            log_warn(f"Ollama timeout (ครั้งที่ {{attempt}})")
        except Exception as e:
            log_err(f"Ollama error: {{e}}")
            break
    return ""

def เรียก_ollama_เร็ว(prompt: str, timeout: int = 30, num_predict: int = 200) -> str:
    return เรียก_ollama(prompt, timeout=timeout, num_predict=num_predict, temperature=0.4)

def _แปลง_keyword_อังกฤษ(หัวข้อ: str, บริบท: str = "") -> str:
    prompt = f\'Thai topic: "{{หัวข้อ}}"\\nWrite 3-4 English keywords for a stock photo. Reply keywords only.\'
    raw = เรียก_ollama(prompt, timeout=20, num_predict=40, temperature=0.15)
    raw = re.sub(r\'<think>.*?</think>\', \'\', raw, flags=re.DOTALL).strip()
    raw = re.sub(r\'["\\\'\\n]\', \' \', raw).strip()
    return raw[:80] if raw else ""

def ดึงรูป_unsplash(หมวด: str, คีย์เวิร์ด: str = "") -> str:
    import hashlib
    if not UNSPLASH_KEY:
        seed = hashlib.md5((คีย์เวิร์ด+หมวด).encode()).hexdigest()[:12]
        return f"https://picsum.photos/seed/{{seed}}/800/450"
    query = คีย์เวิร์ด or หมวด
    try:
        import urllib.parse
        r = requests.get(f"https://api.unsplash.com/photos/random?query={{urllib.parse.quote(query)}}&orientation=landscape&client_id={{UNSPLASH_KEY}}", timeout=10)
        if r.status_code == 200:
            return r.json().get("urls",{{}}).get("regular","")
    except Exception: pass
    import hashlib
    seed = hashlib.md5(query.encode()).hexdigest()[:12]
    return f"https://picsum.photos/seed/{{seed}}/800/450"

def ดึงรูป_pexels(keyword: str) -> str:
    if not PEXELS_KEY: return ""
    import urllib.parse
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={{urllib.parse.quote(keyword)}}&per_page=5&orientation=landscape",
                         headers={{"Authorization": PEXELS_KEY}}, timeout=10)
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
        return f"https://picsum.photos/seed/{{seed}}/800/450"
    for q in [keyword, หัวข้อ[:20], หมวด]:
        if not q: continue
        try:
            r = requests.get(f"https://api.unsplash.com/photos/random?query={{urllib.parse.quote(q)}}&orientation=landscape&client_id={{UNSPLASH_KEY}}", timeout=10)
            if r.status_code == 200:
                img = r.json().get("urls",{{}}).get("regular","")
                if img: return img
            elif r.status_code == 429: break
        except Exception: pass
    return f"https://picsum.photos/seed/{{seed}}/800/450"

def สร้าง_thumbnail_svg(หัวข้อ: str, หมวด: str, filename: str) -> str:
    import hashlib, re as _re
    svg_dir = BASE_PATH / "images" / "thumbs"
    svg_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = Path(filename).stem + ".svg"
    svg_path = svg_dir / safe_filename
    color = CAT_COLORS.get(หมวด, "#6366f1")
    h_display = _re.sub(r\'[^\\u0000-\\u04FF\\u0E00-\\u0E7F ]\', \'\', หัวข้อ[:30]).strip()
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)
    svg = (f\'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">\'
           f\'<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">\'
           f\'<stop offset="0%" stop-color="{{color}}"/>\'
           f\'<stop offset="100%" stop-color="#1e293b"/></linearGradient></defs>\'
           f\'<rect width="800" height="450" fill="url(#g)"/>\'
           f\'<rect x="40" y="40" width="720" height="370" rx="15" fill="#fff" opacity="0.07"/>\'
           f\'<text x="400" y="210" fill="#fff" font-family="Sarabun,sans-serif" font-size="28" font-weight="bold" text-anchor="middle">{{h_display}}</text>\'
           f\'<text x="400" y="265" fill="#cbd5e1" font-family="sans-serif" font-size="18" text-anchor="middle">{{หมวด_th}}</text>\'
           f\'<text x="400" y="390" fill="#94a3b8" font-family="sans-serif" font-size="15" text-anchor="middle">{{SITE_NAME}}</text>\'
           f\'</svg>\')
    try:
        svg_path.write_text(svg, encoding="utf-8")
        return f"images/thumbs/{{safe_filename}}"
    except Exception: return ""
'''
    _write(base / "config.py", config_py_content)
    log_ok("สร้าง config.py (ใหม่สำหรับเว็บนี้)")

    # ── .site_config.json ─────────────────────────────────────────
    summary = {
        "site_name": site_name, "site_url": site_url,
        "base_path": str(base), "categories": cats,
        "color_theme": config.get("color_theme"), "font": config.get("font"),
        "nav_style": nav_sty, "layout": layout_key, "dark_mode": dark_mode,
        "web_type": web_type, "rss_preset": rss_preset,
        "created": datetime.datetime.now().isoformat(),
    }
    _write(base / ".site_config.json", json.dumps(summary, ensure_ascii=False, indent=2))

    log_section(f"🎉 สร้างเว็บ '{site_name}' เสร็จสมบูรณ์!")
    log(f"  📁 โฟลเดอร์  : {base}")
    log(f"  🌐 URL       : {site_url}")
    log(f"  🎨 ธีม       : {COLOR_THEMES.get(config.get('color_theme','slate_indigo'),{}).get('label','')}")
    log(f"  📐 Layout    : {layout.get('label','Grid')}")
    log(f"  🌙 Dark Mode : {DARK_MODE_OPTIONS.get(dark_mode,'')}")
    log(f"  📄 ไฟล์หลัก  : index.html + {len(cats)} หน้าหมวด + contact + privacy + 404 + config.py")
    log(f"  📦 PWA       : manifest.json + sw.js (offline support)")
    log(f"  🔑 .env      : คัดลอก .env.example → .env แล้วใส่ API keys")
    log(f"\n  ⚡ ขั้นตอนต่อไป:")
    log(f"  1. ตรวจสอบ config.py ที่สร้างใหม่ (BASE_PATH, SITE_URL)")
    log(f"  2. รัน: python agent_writer.py --count 10   (สร้างบทความ)")
    log(f"  3. รัน: python agent_fix_v4.py              (ซ่อม + rebuild)")
    log(f"  4. รัน: python agent_fix_v4.py --publish    (push GitHub/Vercel)")


# ══════════════════════════════════════════════════════════════
# 🔧 Helpers
# ══════════════════════════════════════════════════════════════
def _write(path: Path, content: str):
    if not DRY_RUN:
        path.write_text(content, encoding="utf-8")
    else:
        log_info(f"[DRY-RUN] จะสร้าง: {path.name}")


def _head(title: str, desc: str, filename: str, site_url: str, font_url: str,
          og_image: str = "", ga4_id: str = "", json_ld: str = "") -> str:
    _og_img = og_image or f"{site_url}/images/og-default.png"
    _gsc    = os.getenv("GSC_VERIFY", "")
    gsc_tag = f'<meta name="google-site-verification" content="{_gsc}">' if _gsc else ""
    _ga4 = (
        f'<!-- Google Analytics GA4 -->\n'
        f'  <script async src="https://www.googletagmanager.com/gtag/js?id={ga4_id}"></script>\n'
        f'  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}'
        f"gtag('js',new Date());gtag('config','{ga4_id}');</script>"
    ) if ga4_id else ""
    _jld = f'\n  <script type="application/ld+json">{json_ld}</script>' if json_ld else ""
    _site_name = title.split(" \u2014 ")[-1] if " \u2014 " in title else title
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <!-- Open Graph -->
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{site_url}/{filename}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{_og_img}">
  <meta property="og:locale" content="th_TH">
  <meta property="og:site_name" content="{_site_name}">
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{_og_img}">
  <!-- Canonical + PWA -->
  <link rel="canonical" href="{site_url}/{filename}">
  {gsc_tag}
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#1e40af">
  <link rel="apple-touch-icon" href="images/icon-192.png">
  <!-- Fonts + CSS -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{font_url}" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="style.css">
  {_ga4}{_jld}
</head>"""


def _sidebar_html(primary: str = "", site_name: str = "") -> str:
    """Sidebar สนับสนุนเรา — อ่านจาก config.py (SIDEBAR_CONFIG)
    ถ้าไม่ได้ตั้งค่า .env ไว้ จะคืน empty string (ไม่แสดงอะไร)"""
    try:
        return สร้าง_sidebar_html(primary_color=primary or "#1e40af")
    except Exception:
        return ""   # ← คืน empty แทน ไม่แสดง placeholder ให้สับสน


def _footer_html(site_name: str, site_url: str, cats: list) -> str:
    year = datetime.date.today().year
    cat_links = " · ".join(
        f'<a href="{c}.html">{ALL_CATS.get(c, c)}</a>' for c in cats[:6]
    )
    return f"""<footer>
  <div style="max-width:800px;margin:0 auto;">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem 1.2rem;margin-bottom:.75rem;">
      <a href="index.html">🏠 หน้าแรก</a>
      <a href="contact.html">📬 ติดต่อเรา</a>
      <a href="privacy.html">🔒 นโยบายฯ</a>
      <a href="sitemap.xml">🗺️ Sitemap</a>
    </div>
    <div style="margin-bottom:.75rem;font-size:.85rem;opacity:.7;">{cat_links}</div>
    <p style="margin:0;color:rgba(255,255,255,.5);font-size:.82rem;">
      © {year} {site_name} · เว็บไซต์นี้ใช้ Google AdSense และลิงก์พันธมิตร (Affiliate)
    </p>
  </div>
</footer>"""


# ══════════════════════════════════════════════════════════════
# 🚀 Main
# ══════════════════════════════════════════════════════════════
def main():
    log_section("🚀 Agent Setup v2 — สร้างเว็บไซต์ใหม่ตั้งแต่ศูนย์")
    log(f"📁 BASE_PATH: {BASE_PATH}")
    if DRY_RUN:
        log_warn("DRY-RUN: ไม่สร้างไฟล์จริง")

    args = set(sys.argv[1:])

    if "--auto" in args:
        log_info("โหมด Auto — AI ออกแบบทุกส่วนให้")
        try:
            ชื่อเว็บ  = input("  ชื่อเว็บ: ").strip() or "เว็บใหม่"
            เกี่ยวกับ = input("  เกี่ยวกับ: ").strip() or "บทความทั่วไป"
            กลุ่ม     = input("  กลุ่มเป้าหมาย: ").strip() or "คนไทยทั่วไป"
            url       = input("  URL เว็บ: ").strip() or "https://mysite.vercel.app"
            base_p    = input(f"  โฟลเดอร์ [{BASE_PATH}]: ").strip() or str(BASE_PATH)
            web_type  = input("  ประเภทเว็บ (blog/news/food/health/tech/ecommerce/portfolio/...): ").strip() or "blog"
        except (EOFError, KeyboardInterrupt):
            log_warn("ยกเลิก"); return
        design = ai_ออกแบบ(ชื่อเว็บ, เกี่ยวกับ, กลุ่ม, web_type)
        design.update({"site_name": ชื่อเว็บ, "site_url": url, "base_path": base_p, "web_type": web_type, "mode": "auto"})
        สร้างเว็บ(design)

    elif "--manual" in args:
        config = manual()
        if config:
            สร้างเว็บ(config)

    else:
        config = wizard()
        if config:
            สร้างเว็บ(config)


if __name__ == "__main__":
    main()