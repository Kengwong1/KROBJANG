"""
╔══════════════════════════════════════════════════════════════════════╗
║  agent_chat.py — WebBot AI ผู้ช่วยดูแลเว็บ (ใช้ Claude API)        ║
║                                                                      ║
║  python agent_chat.py          → เปิด chat                          ║
║  python agent_chat.py --setup  → ตั้งค่า API key                   ║
║                                                                      ║
║  คุยได้เลย เช่น:                                                   ║
║    "ซ่อมเว็บให้หน่อย"                                               ║
║    "มีบทความกี่ชิ้น"                                                ║
║    "เพิ่มบทความ 5 ชิ้นหมวดอาหาร"                                   ║
║    "push ขึ้น github"                                               ║
║    "search ใช้ได้ไหม"                                               ║
║    "บทความซ้ำไหม"                                                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import os, sys, re, json, subprocess, datetime
from pathlib import Path

# ── โหลด config ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import (
        BASE_PATH, SITE_NAME, SITE_URL,
        CATEGORIES, CATEGORY_PAGE_MAP, หมวด_ไทย,
        log, log_ok, log_warn, log_err, log_info, log_section,
    )
except ImportError as e:
    print(f"⚠️  โหลด config.py ไม่ได้: {e}")
    BASE_PATH = Path(__file__).parent
    SITE_NAME = "เว็บของฉัน"
    SITE_URL  = ""
    CATEGORIES = []
    CATEGORY_PAGE_MAP = {}
    หมวด_ไทย = {}
    def log(m):         print(f"  {m}")
    def log_ok(m):      print(f"  ✅ {m}")
    def log_warn(m):    print(f"  ⚠️  {m}")
    def log_err(m):     print(f"  ❌ {m}")
    def log_info(m):    print(f"  ℹ️  {m}")
    def log_section(m): print(f"\n{'─'*50}\n  {m}\n{'─'*50}")

# ── โหลด .env ────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# ── ตรวจ/โหลด requests ───────────────────────────────────────────────
try:
    import requests as _req
    _has_requests = True
except ImportError:
    _has_requests = False

# ══════════════════════════════════════════════════════════════════════
# 🔑 API KEY SETUP
# ══════════════════════════════════════════════════════════════════════
_KEY_FILE = Path(__file__).parent / ".claude_key"

def _load_api_key() -> str:
    # 1) env var
    k = os.environ.get("ANTHROPIC_API_KEY","")
    if k: return k
    # 2) .env file
    env_f = Path(__file__).parent / ".env"
    if env_f.exists():
        for line in env_f.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                k = line.split("=",1)[1].strip().strip('"').strip("'")
                if k: return k
    # 3) .claude_key file
    if _KEY_FILE.exists():
        k = _KEY_FILE.read_text(encoding="utf-8").strip()
        if k: return k
    return ""

def _save_api_key(key: str):
    _KEY_FILE.write_text(key.strip(), encoding="utf-8")
    log_ok(f"บันทึก API key ที่ {_KEY_FILE.name} แล้ว")

def setup_api_key():
    print("\n╔══ ตั้งค่า Claude API Key ═══════════════════════╗")
    print("║  รับ key ฟรีได้ที่: https://console.anthropic.com  ║")
    print("╚═════════════════════════════════════════════════════╝")
    key = input("\nวาง API key ที่นี่: ").strip()
    if key.startswith("sk-ant-") and len(key) > 20:
        _save_api_key(key)
        return key
    else:
        print("❌ Key ไม่ถูกต้อง (ต้องขึ้นต้นด้วย sk-ant- และมีความยาวพอสมควร)")
        return ""

# ══════════════════════════════════════════════════════════════════════
# 🔍 WEB SEARCH — DuckDuckGo (ฟรี) + Tavily fallback
# ══════════════════════════════════════════════════════════════════════
_TAVILY_KEY_FILE = Path(__file__).parent / ".tavily_key"

def _load_tavily_key() -> str:
    k = os.environ.get("TAVILY_API_KEY", "")
    if k: return k
    env_f = Path(__file__).parent / ".env"
    if env_f.exists():
        for line in env_f.read_text(encoding="utf-8").splitlines():
            if line.startswith("TAVILY_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                if k: return k
    if _TAVILY_KEY_FILE.exists():
        k = _TAVILY_KEY_FILE.read_text(encoding="utf-8").strip()
        if k: return k
    return ""

def search_duckduckgo(query: str) -> str:
    """ค้นหาฟรีผ่าน DuckDuckGo Instant Answer API"""
    if not _has_requests:
        return ""
    try:
        r = _req.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=10,
            headers={"User-Agent": "WebBot/1.0"}
        )
        data = r.json()
        parts = []
        if data.get("AbstractText"):
            parts.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:4]:
            if isinstance(topic, dict) and topic.get("Text"):
                parts.append(f"• {topic['Text'][:200]}")
        return "\n".join(parts) if parts else ""
    except Exception:
        return ""

def search_tavily(query: str) -> str:
    """ค้นหาผ่าน Tavily API (ต้องมี key)"""
    if not _has_requests:
        return ""
    key = _load_tavily_key()
    if not key:
        return ""
    try:
        r = _req.post(
            "https://api.tavily.com/search",
            json={
                "api_key": key,
                "query": query,
                "max_results": 4,
                "search_depth": "basic",
            },
            timeout=15,
        )
        results = r.json().get("results", [])
        if not results:
            return ""
        return "\n\n".join([
            f"📰 {x.get('title','')}\n{x.get('content','')[:300]}"
            for x in results
        ])
    except Exception:
        return ""

def web_search(query: str) -> tuple:
    """ลอง DuckDuckGo ก่อน ถ้าไม่ได้ผลค่อยใช้ Tavily คืน (engine_name, result)"""
    result = search_duckduckgo(query)
    if result and len(result) > 50:
        return "🦆 DuckDuckGo", result
    result = search_tavily(query)
    if result:
        return "🔵 Tavily", result
    return "", ""

# คำที่บ่งบอกว่าต้องการข้อมูลปัจจุบัน
_SEARCH_TRIGGERS = [
    "ข่าว", "กระแส", "ไวรัล", "ดัง", "โซเชียล", "เทรนด์", "trend",
    "ล่าสุด", "ตอนนี้", "วันนี้", "เมื่อกี้", "เพิ่งเกิด", "ใหม่ล่าสุด",
    "ดารา", "ซีรีส์", "อัลบั้ม", "เพลง", "หนัง", "บันเทิง",
    "รู้ไหม", "เคยได้ยิน", "เล่าให้ฟัง", "คืออะไร", "เป็นใคร",
]

def needs_search(text: str) -> bool:
    """ตรวจว่าคำถามนี้ต้องการค้นหาข้อมูลจริงไหม"""
    tl = text.lower()
    return any(t in tl for t in _SEARCH_TRIGGERS)

def extract_search_query(text: str) -> str:
    """ดึง query ที่ดีที่สุดจากข้อความ"""
    # ตัดคำสุภาพออก
    clean = re.sub(r'(ครับ|ค่ะ|นะ|หน่อย|ได้ไหม|รู้ไหม|เล่าให้ฟัง)', '', text).strip()
    return clean[:100]

# ══════════════════════════════════════════════════════════════════════
# 📊 WEB STATUS — ดึงข้อมูลสถานะเว็บ
# ══════════════════════════════════════════════════════════════════════
_NON_ARTICLE = {
    "index.html","404.html","contact.html","sitemap.html","privacy.html",
    "style.css","nav.js","robots.txt","sitemap.xml","search-index.json",
    "thumbnails.json","manifest.json","sw.js",
}
_NON_ARTICLE.update(set(CATEGORY_PAGE_MAP.values()) if CATEGORY_PAGE_MAP else set())

def scan_articles():
    result = []
    for fp in sorted(BASE_PATH.glob("*.html")):
        if fp.name in _NON_ARTICLE: continue
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if "<html" in txt.lower() and len(txt) > 200:
                result.append(fp)
        except Exception: pass
    return result

def get_web_status() -> dict:
    """รวบรวมสถานะเว็บทั้งหมดเพื่อส่งให้ AI รู้บริบท"""
    articles = scan_articles()
    by_cat   = {}
    for fp in articles:
        cat = fp.stem.split("_")[0] if "_" in fp.stem else fp.stem
        by_cat.setdefault(cat, []).append(fp.name)

    issues = []
    for fp in articles[:30]:  # ตรวจแค่ 30 บทความล่าสุด
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if "nav.js" not in txt:           issues.append(f"{fp.name}: ไม่มี nav.js")
            if "<h1" not in txt.lower():       issues.append(f"{fp.name}: ไม่มี h1")
            if len(txt) < 500:                 issues.append(f"{fp.name}: เนื้อหาสั้นมาก")
        except Exception: pass

    search_ok = (BASE_PATH / "search-index.json").exists()
    sitemap_ok = (BASE_PATH / "sitemap.xml").exists()
    nav_ok     = (BASE_PATH / "nav.js").exists()

    newest = sorted(articles, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
    newest_names = [f.name for f in newest]

    return {
        "site_name":    SITE_NAME,
        "site_url":     SITE_URL,
        "base_path":    str(BASE_PATH),
        "total_articles": len(articles),
        "categories":   {cat: len(fps) for cat, fps in by_cat.items()},
        "newest_5":     newest_names,
        "issues_found": issues[:10],
        "files_ok": {
            "nav.js":           nav_ok,
            "search-index.json": search_ok,
            "sitemap.xml":      sitemap_ok,
            "style.css":        (BASE_PATH / "style.css").exists(),
        },
    }

# ══════════════════════════════════════════════════════════════════════
# ⚡ RUN AGENT COMMANDS
# ══════════════════════════════════════════════════════════════════════
_AGENT_FIX    = Path(__file__).parent / "agent_fix_v5.py"
_AGENT_WRITER = Path(__file__).parent / "agent_writer.py"
_FIX_NOW      = Path(__file__).parent / "fix_now.py"

def run_command(cmd: list, label: str) -> str:
    """รันคำสั่ง python และคืนผลลัพธ์"""
    print(f"\n  🔄 กำลังรัน: {label} ...")
    try:
        r = subprocess.run(
            [sys.executable] + cmd,
            capture_output=True, text=True,
            encoding="utf-8", errors="ignore",
            timeout=300, cwd=str(BASE_PATH)
        )
        out = (r.stdout + r.stderr)[-2000:]  # เอาแค่ 2000 ตัวสุดท้าย
        return out
    except subprocess.TimeoutExpired:
        return "⏱️ หมดเวลา (> 5 นาที)"
    except Exception as e:
        return f"❌ รันไม่ได้: {e}"

# mapping คำพูดไทย → คำสั่ง
_CMD_MAP = {
    # fix
    "ซ่อม":           lambda: run_command([str(_AGENT_FIX), "--fix"],     "agent_fix_v5 --fix"),
    "แก้เว็บ":         lambda: run_command([str(_AGENT_FIX), "--fix"],     "agent_fix_v5 --fix"),
    "fix":            lambda: run_command([str(_AGENT_FIX), "--fix"],     "agent_fix_v5 --fix"),
    "ซ่อมทั้งหมด":    lambda: run_command([str(_AGENT_FIX)],              "agent_fix_v5 (full)"),
    # search
    "แก้ search":     lambda: run_command([str(_AGENT_FIX), "--fix-search"], "fix-search"),
    "ซ่อม search":    lambda: run_command([str(_AGENT_FIX), "--fix-search"], "fix-search"),
    "fix search":     lambda: run_command([str(_AGENT_FIX), "--fix-search"], "fix-search"),
    "แก้ค้นหา":       lambda: run_command([str(_AGENT_FIX), "--fix-search"], "fix-search"),
    "ค้นหาไม่ได้":    lambda: run_command([str(_AGENT_FIX), "--fix-search"], "fix-search"),
    "fix_now":        lambda: run_command([str(_FIX_NOW)],                "fix_now.py"),
    # publish
    "push":           lambda: run_command([str(_AGENT_FIX), "--publish"], "publish"),
    "deploy":         lambda: run_command([str(_AGENT_FIX), "--publish"], "publish"),
    "อัปโหลด":        lambda: run_command([str(_AGENT_FIX), "--publish"], "publish"),
    # audit
    "ตรวจ":           lambda: run_command([str(_AGENT_FIX), "--audit"],   "audit"),
    "audit":          lambda: run_command([str(_AGENT_FIX), "--audit"],   "audit"),
    # stats
    "สถิติ":          lambda: run_command([str(_AGENT_FIX), "--stats"],   "stats"),
    "stats":          lambda: run_command([str(_AGENT_FIX), "--stats"],   "stats"),
    # dedup
    "ลบซ้ำ":          lambda: run_command([str(_AGENT_FIX), "--dedup"],   "dedup"),
    "dedup":          lambda: run_command([str(_AGENT_FIX), "--dedup"],   "dedup"),
    # css
    "rebuild css":    lambda: run_command([str(_AGENT_FIX), "--fix-css"], "fix-css"),
    "แก้ css":        lambda: run_command([str(_AGENT_FIX), "--fix-css"], "fix-css"),
    # footer/hero
    "แก้ footer":     lambda: run_command([str(_AGENT_FIX), "--fix-footer"], "fix-footer"),
    "แก้ hero":       lambda: run_command([str(_AGENT_FIX), "--fix-hero"],   "fix-hero"),
    # meta/alt/404
    "แก้ meta":       lambda: run_command([str(_AGENT_FIX), "--fix-meta"],   "fix-meta"),
    "เติม alt":       lambda: run_command([str(_AGENT_FIX), "--fix-alt"],    "fix-alt"),
    "แก้ 404":        lambda: run_command([str(_AGENT_FIX), "--fix-404"],    "fix-404"),
    "ตรวจซ้ำ":        lambda: run_command([str(_AGENT_FIX), "--check-dup"],  "check-dup"),
}

def detect_command(msg: str):
    """ตรวจว่าข้อความต้องการรันคำสั่งอะไร คืน (key, fn) หรือ None"""
    ml = msg.lower()
    for key, fn in _CMD_MAP.items():
        if key in ml:
            return key, fn

    # ── layout / theme / style ────────────────────────────────
    _LAYOUTS = ["grid","list","magazine","compact","compact5","compact6",
                "hero3","sidebar","tiles","masonry","zigzag","featured","row"]
    _THEMES  = ["blue","dark","green","red","purple","orange","teal","slate",
                "rose","indigo","amber","cyan","lime","sky","violet"]

    m_lay   = re.search(r'layout\s+([a-z0-9]+)', ml) or \
              re.search(r'(?:เปลี่ยน|ใช้|เป็น)\s*(?:layout|หน้า|รูปแบบ|การจัดวาง)?\s*(?:เป็น|แบบ)?\s*([a-z0-9]+)', ml)
    m_theme = re.search(r'(?:theme|ธีม|สีธีม)\s+([a-z]+)', ml) or \
              re.search(r'(?:สี|ธีม)\s*(?:เป็น|แบบ)?\s*([a-z]+)', ml)
    m_cols  = re.search(r'(\d+)\s*(?:คอลัมน์|cols?|column)', ml)

    lay_val   = m_lay.group(1)   if m_lay   and m_lay.group(1)   in _LAYOUTS else None
    theme_val = m_theme.group(1) if m_theme and m_theme.group(1) in _THEMES  else None
    cols_val  = m_cols.group(1)  if m_cols else None

    # ตรวจชื่อ layout/theme ตรงๆ ในข้อความ (fallback)
    if not lay_val:
        for lay in _LAYOUTS:
            if lay in ml: lay_val = lay; break
    if not theme_val:
        for th in _THEMES:
            # ป้องกัน false positive กับคำสั้น เช่น "red" ใน "redo"
            if re.search(r'\b' + th + r'\b', ml): theme_val = th; break

    if lay_val or theme_val or cols_val:
        cmd = [str(_AGENT_FIX), "--fix"]
        if lay_val:   cmd += ["--layout", lay_val]
        if theme_val: cmd += ["--theme",  theme_val]
        if cols_val:  cmd += ["--cols",   cols_val]
        label = f"fix layout={lay_val or '-'} theme={theme_val or '-'} cols={cols_val or '-'}"
        return "style", lambda c=list(cmd), l=label: run_command(c, l)

    # เพิ่มบทความ
    m = re.search(r'(?:เพิ่ม|สร้าง|เขียน).*?(\d+).*?บทความ', ml)
    if m:
        count = m.group(1)
        cat_arg = []
        # ค้นหาหมวดจาก "หมวด X" ก่อน ถ้าไม่มีค่อยลองแปลงจากภาษาไทย
        cat_match = re.search(r'หมวด\s*(\w+)', ml)
        if cat_match:
            cat = cat_match.group(1)
            rev = {v: k for k, v in หมวด_ไทย.items()}
            cat_en = rev.get(cat, cat)
            if cat_en in CATEGORIES:
                cat_arg = ["--cat", cat_en]
        else:
            # ลองจับชื่อหมวดภาษาไทยโดยตรง เช่น "เพิ่มบทความ 5 ชิ้นหมวดอาหาร"
            rev = {v: k for k, v in หมวด_ไทย.items()}
            for th_name, en_name in rev.items():
                if th_name and th_name in ml and en_name in CATEGORIES:
                    cat_arg = ["--cat", en_name]
                    break
        cmd = [str(_AGENT_WRITER), "--count", count] + cat_arg
        return "writer", lambda c=list(cmd), n=count: run_command(c, f"agent_writer --count {n}")

    return None

# ══════════════════════════════════════════════════════════════════════
# 🤖 CLAUDE API CALL
# ══════════════════════════════════════════════════════════════════════
def call_claude(messages: list, api_key: str, status: dict) -> str:
    if not _has_requests:
        return "❌ ติดตั้ง requests ก่อน: pip install requests"

    # System prompt รู้จักเว็บนี้จริงๆ
    system = f"""คุณคือ WebBot — ผู้ช่วย AI อัจฉริยะที่ดูแลเว็บไซต์ "{status['site_name']}" ({status['site_url']}) แบบครบวงจร

🧠 บุคลิก:
- พูดภาษาไทยเป็นธรรมชาติ กระชับ ตรงประเด็น เหมือนเพื่อนที่เชี่ยวชาญด้านเว็บมานั่งช่วย
- ไม่พูดอ้อมค้อม ถ้าทำได้บอกว่าทำ ถ้าทำไม่ได้บอกตรงๆ พร้อมเสนอทางออก
- ตอบสั้นพอดีกับคำถาม อย่าพูดยาวเกินไปถ้าไม่จำเป็น
- ถ้าผู้ใช้ถามเรื่องที่ไม่เกี่ยวกับเว็บ ตอบได้ปกติ อย่าปฏิเสธ

📊 สถานะเว็บตอนนี้:
- ชื่อเว็บ: {status['site_name']} | URL: {status['site_url']}
- บทความทั้งหมด: {status['total_articles']} ชิ้น
- หมวดหมู่และจำนวน: {json.dumps(status['categories'], ensure_ascii=False)}
- บทความล่าสุด 3 ชิ้น: {', '.join(status['newest_5'][:3])}
- ไฟล์ระบบ: {json.dumps(status['files_ok'], ensure_ascii=False)}
- ปัญหาที่พบ: {len(status['issues_found'])} รายการ {('— ' + ', '.join(status['issues_found'][:2])) if status['issues_found'] else '(ไม่มี ✅)'}
- โฟลเดอร์: {status['base_path']}

⚡ สิ่งที่ทำได้เมื่อผู้ใช้สั่ง (บอกผู้ใช้ก่อนว่ากำลังทำอะไร):
- "ซ่อม / fix / แก้เว็บ / มีปัญหา" → รัน agent_fix_v5.py --fix (ซ่อมทุกอย่าง + rebuild)
- "เพิ่มบทความ N ชิ้น [หมวด]" → รัน agent_writer.py --count N [--cat หมวด]
- "push / deploy / อัปโหลด / ขึ้น vercel" → รัน --publish (sitemap + git push)
- "ตรวจ / audit / ดูปัญหา" → รัน --audit (แสดงปัญหาทั้งหมด)
- "สถิติ / stats / มีบทความกี่ชิ้น" → รัน --stats
- "แก้ search / ค้นหาไม่ได้ / แก้ค้นหา" → รัน --fix-search
- "ลบซ้ำ / dedup" → รัน --dedup
- "rebuild css / แก้ style / แก้ css" → รัน --fix-css
- "แก้ footer" → รัน --fix-footer | "แก้ hero" → รัน --fix-hero
- "แก้ meta / เติม alt / แก้ 404 / ตรวจซ้ำ" → รัน flag ตรงๆ
- 🎨 STYLE — เปลี่ยนธีม/layout/คอลัมน์ (พูดธรรมชาติได้เลย):
  · Layout: grid, list, magazine, compact, compact5, compact6, hero3, sidebar, tiles, masonry, zigzag, featured, row
  · Theme: blue, dark, green, red, purple, orange, teal, slate, rose, indigo, amber, cyan, lime, sky, violet
  · ตัวอย่าง: "เปลี่ยนเป็น layout hero3", "ธีม dark", "ใช้ 4 คอลัมน์", "layout tiles สีม่วง"

📝 วิธีรายงานผล:
- สรุป log ให้เข้าใจง่าย ไม่ต้องก็อปทั้งหมด
- บอกว่าทำสำเร็จกี่ไฟล์ มีปัญหาอะไร และขั้นตอนต่อไปคืออะไร
- ถ้า log แสดง error ให้วิเคราะห์และบอกสาเหตุ + วิธีแก้

💡 ถ้าผู้ใช้ถามคำถามทั่วไปเกี่ยวกับเว็บ SEO เนื้อหา หรือการตลาด ตอบจากความรู้ได้เลย ไม่ต้องรัน agent

🔍 ข้อมูลจากการค้นหา:
- ถ้ามี [ผลการค้นหา] แนบมาใน message ให้ใช้ข้อมูลนั้นตอบได้เลย
- ถ้าข้อมูลไม่ครบหรือไม่ตรง ให้บอกตรงๆ อย่าแต่งเรื่องเพิ่ม
- ห้ามประดิษฐ์ข้อมูลข่าว/เหตุการณ์ขึ้นมาเอง ถ้าไม่รู้ให้บอกว่าไม่มีข้อมูล"""

    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "system": system,
        "messages": messages,
    }

    try:
        resp = _req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["content"][0]["text"]
        elif resp.status_code == 401:
            return "❌ API key ไม่ถูกต้อง — รัน: python agent_chat.py --setup"
        elif resp.status_code == 429:
            return "⏱️ ใช้งานเยอะเกินไป รอแป๊บแล้วลองใหม่ครับ"
        else:
            return f"❌ Claude API error {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return f"❌ เชื่อมต่อไม่ได้: {e}"

def call_ollama_chat(messages: list, status: dict) -> str:
    """Fallback: ใช้ Ollama แทน Claude API เมื่อไม่มี key"""
    try:
        from config import เรียก_ollama, OLLAMA_HOST
        import requests as _r
        # ตรวจว่า Ollama พร้อมไหม
        try:
            _r.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        except Exception:
            return "❌ Ollama ไม่ได้รัน — รัน: ollama serve\nหรือตั้งค่า Claude API key: python agent_chat.py --setup"

        # สร้าง prompt จาก history
        history_text = "\n".join([
            f"{'ผู้ใช้' if m['role']=='user' else 'WebBot'}: {m['content'][:2000]}"
            for m in messages[-6:]
        ])
        system_brief = (f"คุณคือ WebBot ดูแลเว็บ {status['site_name']} "
                       f"มี {status['total_articles']} บทความ "
                       f"ตอบภาษาไทยสั้นกระชับ "
                       f"ถ้ามี [ผลการค้นหา] ใน message ให้ใช้ข้อมูลนั้นตอบเท่านั้น ห้ามแต่งข้อมูลขึ้นมาเอง")
        reply = เรียก_ollama(
            f"{system_brief}\n\n{history_text}\nWebBot:",
            num_predict=800, timeout=60
        )
        # ตัด prefix ที่อาจติดมา
        reply = re.sub(r'^(WebBot\s*:\s*)', '', reply.strip())
        return reply if reply else "⏱️ Ollama ตอบช้า ลองใหม่อีกครั้ง"
    except Exception as e:
        return f"❌ Ollama error: {e}"



def chat():
    api_key = _load_api_key()
    if not api_key:
        print("""
╔══════════════════════════════════════════════════════════════╗
║  ℹ️  ไม่พบ Claude API key                                    ║
║  WebBot จะใช้ Ollama แทน (ต้องรัน ollama serve ก่อน)        ║
║  หากต้องการใช้ Claude: python agent_chat.py --setup          ║
╚══════════════════════════════════════════════════════════════╝""")

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🤖 WebBot — ผู้ช่วย AI ดูแลเว็บ "{SITE_NAME}"
║  พิมพ์อะไรก็ได้เป็นภาษาไทย หรือ /exit เพื่อออก
║  ตัวอย่าง: "ซ่อมเว็บ", "เพิ่มบทความ 5 ชิ้น", "สถิติ", "push"
╚══════════════════════════════════════════════════════════════╝""")

    history  = []   # conversation history
    status   = get_web_status()
    log_ok(f"โหลดสถานะเว็บ: {status['total_articles']} บทความ | {len(status['categories'])} หมวด")
    if status["issues_found"]:
        log_warn(f"พบปัญหา {len(status['issues_found'])} รายการ (พิมพ์ 'ตรวจ' เพื่อดูรายละเอียด)")

    while True:
        print()
        try:
            user = input("คุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 บาย!")
            break

        if not user:
            continue
        if user.lower() in ("/exit", "/quit", "ออก", "บาย", "bye"):
            print("👋 บาย! แวะมาคุยใหม่ได้เสมอครับ")
            break
        if user.lower() in ("/status", "สถานะ", "สถานะเว็บ"):
            status = get_web_status()
            print(f"  📊 {status['site_name']} — {status['total_articles']} บทความ")
            for cat, n in status["categories"].items():
                print(f"     · {หมวด_ไทย.get(cat, cat)}: {n} ชิ้น")
            if status["issues_found"]:
                print(f"  ⚠️  ปัญหา: {', '.join(status['issues_found'][:3])}")
            else:
                print("  ✅ ไม่พบปัญหา")
            continue
        if user.lower() in ("/help", "ช่วย", "ช่วยด้วย", "คำสั่ง"):
            print("""  📖 คำสั่งที่ใช้ได้:
  /status     — ดูสถานะเว็บ
  /exit       — ออก
  ซ่อมเว็บ   — รัน agent_fix --fix
  push        — deploy ขึ้น Vercel
  ตรวจ        — audit ปัญหา
  สถิติ       — ดู stats
  เพิ่มบทความ 5 ชิ้น [หมวดอาหาร]
  เปลี่ยน layout grid / ธีม dark
  ลบซ้ำ / แก้ search / rebuild css""")
            continue

        # ── ตรวจว่าต้องรัน agent ไหม ─────────────────────────
        cmd_result = detect_command(user)
        agent_output = ""

        if cmd_result:
            key, fn = cmd_result
            print(f"  ⚡ ตรวจพบคำสั่ง: {key}")
            agent_output = fn()
            # refresh status หลังรัน
            try:
                status = get_web_status()
            except Exception:
                pass
            # สรุป output ให้ AI อธิบาย
            user_with_result = (
                f"{user}\n\n"
                f"[ผลการรัน agent]\n{agent_output}"
            )
        else:
            # ── ค้นหาข้อมูลจริงถ้าคำถามต้องการ ──────────────
            search_result = ""
            engine = ""
            if needs_search(user):
                print("  🔍 กำลังค้นหาข้อมูล...", end="", flush=True)
                query = extract_search_query(user)
                engine, search_result = web_search(query)
                if search_result:
                    print(f" {engine} ✅")
                else:
                    print(f" ⚠️ ไม่พบข้อมูล")

            if search_result:
                user_with_result = (
                    f"{user}\n\n"
                    f"[ผลการค้นหา: {extract_search_query(user)}]\n{search_result}"
                )
            else:
                user_with_result = user

        # ── เรียก Claude ──────────────────────────────────────
        history.append({"role": "user", "content": user_with_result})

        # จำกัด history 20 รอบ (40 messages = user+assistant)
        # เก็บ system context ไว้ 2 message แรก + 38 ล่าสุด
        if len(history) > 40:
            history = history[-40:]

        print("WebBot: ", end="", flush=True)
        if api_key:
            reply = call_claude(history, api_key, status)
        else:
            reply = call_ollama_chat(history, status)
        print(reply)

        history.append({"role": "assistant", "content": reply})

        # refresh status ทุก 5 รอบ
        if len(history) % 10 == 0:
            try:
                status = get_web_status()
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════════
# 🚀 Main
# ══════════════════════════════════════════════════════════════════════
def main():
    args = set(sys.argv[1:])
    if "--setup" in args:
        setup_api_key()
        return
    if not _has_requests:
        print("❌ ต้องติดตั้ง requests ก่อน:")
        print("   pip install requests")
        return
    chat()

if __name__ == "__main__":
    main()
