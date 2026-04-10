"""
╔══════════════════════════════════════════════════════════════════════╗
║  agent_fix_v5.py  — Full Layout + Theme + Multi-Layout Edition      ║
║                                                                      ║
║  python agent_fix_v5.py                → ซ่อมทุกส่วน + push         ║
║  python agent_fix_v5.py --fix          → ซ่อมอย่างเดียว             ║
║  python agent_fix_v5.py --audit        → ตรวจอย่างเดียว             ║
║  python agent_fix_v5.py --publish      → sitemap + push              ║
║  python agent_fix_v5.py --dry-run      → ดูอย่างเดียว               ║
║  python agent_fix_v5.py --dedup        → ลบซ้ำ + rebuild             ║
║  python agent_fix_v5.py --chat         → คุยกับ AI โดยตรง            ║
║                                                                      ║
║  Layout (--layout):                                                  ║
║    grid     → การ์ดตาราง N คอลัมน์ (default)                        ║
║    list     → รูปซ้าย ข้อความขวา (แนวตั้ง)                          ║
║    magazine → ใหญ่ 1 + เล็กๆ (2fr 1fr 1fr)                          ║
║    compact  → กริดเล็ก 4 คอลัมน์                                     ║
║    compact5 → กริดเล็กมาก 5 คอลัมน์                                  ║
║    compact6 → กริดจิ๋ว 6 คอลัมน์                                     ║
║    hero3    → 3 การ์ดใหญ่แบบเว็บข่าว (Sanook/Kapook)                ║
║    sidebar  → ใหญ่ซ้าย + list ขวา (BBC style)                        ║
║    tiles    → รูปเต็ม title ทับล่าง (Pinterest style)               ║
║    masonry  → สูงไม่เท่ากัน (CSS columns)                           ║
║    zigzag   → สลับรูปซ้าย-ขวา (feature style)                       ║
║    featured → 1 ใหญ่ข้างบน + grid เล็กข้างล่าง                      ║
║    row      → scroll แนวนอน (horizontal scroll)                      ║
║                                                                      ║
║  python agent_fix_v5.py --layout hero3 --cols 3                     ║
║  python agent_fix_v5.py --layout tiles --cols 4                     ║
║  python agent_fix_v5.py --layout compact6 --cols 6                  ║
║  python agent_fix_v5.py --layout zigzag                             ║
║  python agent_fix_v5.py --layout featured --cols 3                  ║
║                                                                      ║
║  Theme (--theme):                                                    ║
║    blue(default) dark  green  red  purple  orange  teal  slate      ║
║    rose  indigo  amber  cyan  lime  sky  violet                      ║
║  python agent_fix_v5.py --theme dark --layout hero3                 ║
║                                                                      ║
║  Extra:                                                              ║
║  python agent_fix_v5.py --check-overlap → ตรวจซ้ำ                  ║
║  python agent_fix_v5.py --fix-css       → rebuild style.css         ║
║  python agent_fix_v5.py --fix-footer    → แก้ footer ทุกหน้า         ║
║  python agent_fix_v5.py --fix-hero      → แก้ hero ทุกหน้า          ║
║  python agent_fix_v5.py --stats         → สถิติเว็บไซต์             ║
╚══════════════════════════════════════════════════════════════════════╝

แก้จาก v4:
  ✅ [BUG-COLOR] hero gradient ≠ footer bg → ใช้ _theme() เดียวกัน 100%
  ✅ [BUG-COLOR] category page footer สีต่างจาก index → fixed
  ✅ [BUG-LAYOUT] article pages ไม่มี hero/footer uniform → แก้
  ✅ [NEW] layout zigzag  — รูปสลับซ้าย-ขวาเหมือนเว็บ feature
  ✅ [NEW] layout featured — 1 ใหญ่ข้างบน + grid เล็กข้างล่าง
  ✅ [NEW] layout row      — horizontal scroll card
  ✅ [NEW] layout compact5/compact6 — 5-6 คอลัมน์
  ✅ [NEW] theme เพิ่ม: rose, indigo, amber, cyan, lime, sky, violet
  ✅ [NEW] --fix-css  → สร้าง style.css ใหม่ทั้งหมดที่มี CSS variables
  ✅ [NEW] --fix-footer → แก้ footer ทุกหน้าให้ใช้สีเดียวกัน
  ✅ [NEW] --fix-hero   → แก้ hero ทุกหน้าให้ใช้ gradient เดียวกัน
  ✅ [NEW] --stats → สถิติเว็บไซต์ (จำนวนบทความ, หมวด, ขนาด)
  ✅ [NEW] กรอบการ์ดสวยขึ้น: shadow, hover กว้างขึ้น
  ✅ [NEW] badge หมวดหมู่บนการ์ด
  ✅ [NEW] อ่านเพิ่มเติม button บนการ์ด
  ✅ [NEW] index hero ปรับสวยขึ้น: counter ล่วงหน้า, stats row
  ✅ [NEW] footer ปรับสวยขึ้น: social icons, credit line
  ✅ [IMPROVED] search ทำงานเร็วขึ้น + แสดงผลสวยขึ้น
  ✅ [IMPROVED] responsive breakpoint ครอบคลุมขึ้น
"""
import os, sys, re, json, datetime, hashlib, subprocess, time
from pathlib import Path
from collections import Counter, defaultdict

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️  ติดตั้ง: pip install beautifulsoup4")
    sys.exit(1)

from config import (
    BASE_PATH, SITE_URL, SITE_NAME, CATEGORIES,
    CATEGORY_PAGE_MAP, CAT_COLORS, หมวด_ไทย, DRY_RUN,
    log, log_ok, log_warn, log_err, log_info, log_section,
    สร้าง_thumbnail_svg, เรียก_ollama,
)

# ══════════════════════════════════════════════════════════════
# ⚙️  Constants
# ══════════════════════════════════════════════════════════════
_SKIP_DIRS    = {"node_modules",".git",".vercel",".github","__pycache__","dist","build",".next","venv",".venv"}
_INDEX_FILES  = {"index.html","404.html","contact.html","sitemap.html","privacy.html"}
_CAT_FILES    = {"ai.html","booking.html","finance.html","food.html","games.html",
                 "health.html","horoscope.html","lifestyle.html","news.html","sport.html",
                 "technology.html","entertainment.html"}
_FEAT_FILES   = {"video.html","shopping.html","lotto.html"}
_STATIC_FILES = {"style.css","nav.js","robots.txt","sitemap.xml","search-index.json","thumbnails.json"}
_NON_ARTICLE  = _INDEX_FILES | _CAT_FILES | _STATIC_FILES | _FEAT_FILES

_INTERACTIVE  = "--interactive" in sys.argv or "--ask" in sys.argv

ART_S = "<!-- ARTICLE_LIST_START -->"
ART_E = "<!-- ARTICLE_LIST_END -->"
REL_S = "<!-- related-articles-block -->"
REL_E = "<!-- /related-articles-block -->"
IDX_S = "<!-- INDEX_ARTICLES_START -->"
IDX_E = "<!-- INDEX_ARTICLES_END -->"

# ══════════════════════════════════════════════════════════════
# 🎨  PARSE FLAGS
# ══════════════════════════════════════════════════════════════
_args = sys.argv[1:]

def _get_arg(flag: str, default: str) -> str:
    try:
        i = _args.index(flag)
        return _args[i+1] if i+1 < len(_args) else default
    except ValueError:
        return default

LAYOUT_MODE  = _get_arg("--layout",  "grid")
COLS         = int(_get_arg("--cols",  "3"))
THEME_NAME   = _get_arg("--theme",   "blue")

# ══════════════════════════════════════════════════════════════
# 🎨  THEME SYSTEM — ขยาย 15 ธีม  (primary, dark, grad_end, accent, badge_txt)
# ══════════════════════════════════════════════════════════════
THEME_DEFS = {
    "blue":   ("#1e40af", "#0f172a", "#1e3a8a", "#3b82f6", "#fff"),
    "dark":   ("#0f172a", "#020617", "#1e293b", "#475569", "#e2e8f0"),
    "green":  ("#065f46", "#022c22", "#047857", "#10b981", "#fff"),
    "red":    ("#991b1b", "#450a0a", "#b91c1c", "#ef4444", "#fff"),
    "purple": ("#581c87", "#2e1065", "#6b21a8", "#a855f7", "#fff"),
    "orange": ("#9a3412", "#431407", "#c2410c", "#f97316", "#fff"),
    "teal":   ("#0f766e", "#042f2e", "#0d9488", "#14b8a6", "#fff"),
    "slate":  ("#334155", "#0f172a", "#475569", "#64748b", "#f8fafc"),
    # ── v5 ใหม่ ──
    "rose":   ("#9f1239", "#4c0519", "#be123c", "#fb7185", "#fff"),
    "indigo": ("#3730a3", "#1e1b4b", "#4338ca", "#818cf8", "#fff"),
    "amber":  ("#92400e", "#451a03", "#b45309", "#fbbf24", "#fff"),
    "cyan":   ("#155e75", "#083344", "#0e7490", "#22d3ee", "#fff"),
    "lime":   ("#3f6212", "#1a2e05", "#4d7c0f", "#a3e635", "#1a2e05"),
    "sky":    ("#075985", "#082f49", "#0369a1", "#38bdf8", "#fff"),
    "violet": ("#4c1d95", "#2e1065", "#5b21b6", "#c084fc", "#fff"),
}

def _theme() -> dict:
    t = THEME_DEFS.get(THEME_NAME, THEME_DEFS["blue"])
    return {"primary": t[0], "dark": t[1], "grad_end": t[2], "accent": t[3], "badge_txt": t[4]}

def _hero_gradient() -> str:
    t = _theme()
    # ใช้ primary → dark เหมือนกันทั้ง hero และ footer
    return f"linear-gradient(135deg,{t['primary']},{t['dark']})"

def _footer_bg() -> str:
    # ✅ BUG-COLOR FIX: footer ใช้สี dark เดียวกับ hero gradient
    return _theme()["dark"]

def _footer_gradient() -> str:
    # footer gradient เหมือน hero แต่กลับทิศ (dark → primary)
    t = _theme()
    return f"linear-gradient(135deg,{t['dark']},{t['primary']})"

# ══════════════════════════════════════════════════════════════
# 📐  LAYOUT SYSTEM — 13 แบบ (v5)
# ══════════════════════════════════════════════════════════════
LAYOUT_DEFS = {
    # ── grid: การ์ดตาราง N คอลัมน์ (default) ──────────────────
    "grid": {
        "label":    "Grid — การ์ดตาราง",
        "img_h":    "200px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.06);"
        ),
        "wrapper": lambda cols: f"display:grid;grid-template-columns:repeat({cols},1fr);gap:1.4rem;",
        "responsive": lambda cols: (
            f"@media(max-width:1024px){{.art-grid{{grid-template-columns:repeat({min(cols,3)},1fr)!important;}}}}"
            f"@media(max-width:768px){{.art-grid{{grid-template-columns:repeat({min(cols,2)},1fr)!important;}}}}"
            f"@media(max-width:480px){{.art-grid{{grid-template-columns:1fr!important;}}}}"
        ),
    },
    # ── list: รูปซ้าย ข้อความขวา (แนวตั้ง) ───────────────────
    "list": {
        "label":    "List — รูปซ้าย ข้อความขวา",
        "img_h":    "90px",
        "img_w":    "140px",
        "card_css": (
            "display:flex;flex-direction:row;align-items:center;gap:.85rem;"
            "background:var(--card,#fff);"
            "border-radius:12px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;padding:.6rem;"
            "transition:box-shadow .2s,background .2s;"
            "box-shadow:0 1px 4px rgba(0,0,0,.05);"
        ),
        "wrapper": lambda cols: "display:flex;flex-direction:column;gap:.7rem;",
        "responsive": lambda cols: "",
    },
    # ── magazine: ใหญ่ 1 + เล็กๆ ──────────────────────────────
    "magazine": {
        "label":    "Magazine — featured + grid",
        "img_h":    "220px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.07);"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:2fr 1fr 1fr;gap:1.25rem;",
        "responsive": lambda cols: (
            "@media(max-width:900px){.art-grid{grid-template-columns:1fr 1fr!important;}}"
            "@media(max-width:560px){.art-grid{grid-template-columns:1fr!important;}}"
        ),
    },
    # ── compact: กริดเล็ก 4 คอลัมน์ ───────────────────────────
    "compact": {
        "label":    "Compact — กริด 4 คอลัมน์",
        "img_h":    "140px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:10px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .15s,box-shadow .15s;"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;",
        "responsive": lambda cols: (
            "@media(max-width:1100px){.art-grid{grid-template-columns:repeat(3,1fr)!important;}}"
            "@media(max-width:700px){.art-grid{grid-template-columns:repeat(2,1fr)!important;}}"
            "@media(max-width:420px){.art-grid{grid-template-columns:1fr!important;}}"
        ),
    },
    # ── compact5: 5 คอลัมน์ [NEW v5] ─────────────────────────
    "compact5": {
        "label":    "Compact5 — กริด 5 คอลัมน์",
        "img_h":    "120px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:10px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .15s,box-shadow .15s;"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:repeat(5,1fr);gap:.85rem;",
        "responsive": lambda cols: (
            "@media(max-width:1100px){.art-grid{grid-template-columns:repeat(4,1fr)!important;}}"
            "@media(max-width:800px){.art-grid{grid-template-columns:repeat(3,1fr)!important;}}"
            "@media(max-width:560px){.art-grid{grid-template-columns:repeat(2,1fr)!important;}}"
            "@media(max-width:360px){.art-grid{grid-template-columns:1fr!important;}}"
        ),
    },
    # ── compact6: 6 คอลัมน์ [NEW v5] ─────────────────────────
    "compact6": {
        "label":    "Compact6 — กริด 6 คอลัมน์",
        "img_h":    "100px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:8px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .15s,box-shadow .15s;"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:repeat(6,1fr);gap:.7rem;",
        "responsive": lambda cols: (
            "@media(max-width:1200px){.art-grid{grid-template-columns:repeat(5,1fr)!important;}}"
            "@media(max-width:1000px){.art-grid{grid-template-columns:repeat(4,1fr)!important;}}"
            "@media(max-width:700px){.art-grid{grid-template-columns:repeat(3,1fr)!important;}}"
            "@media(max-width:480px){.art-grid{grid-template-columns:repeat(2,1fr)!important;}}"
        ),
    },
    # ── hero3: 3 การ์ดใหญ่เต็มความกว้าง ───────────────────────
    "hero3": {
        "label":    "Hero3 — 3 การ์ดใหญ่แบบเว็บข่าว",
        "img_h":    "260px",
        "card_css": (
            "display:flex;flex-direction:column;position:relative;"
            "background:var(--card,#fff);"
            "border-radius:16px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 4px 12px rgba(0,0,0,.09);"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;",
        "responsive": lambda cols: (
            "@media(max-width:900px){.art-grid{grid-template-columns:repeat(2,1fr)!important;}}"
            "@media(max-width:560px){.art-grid{grid-template-columns:1fr!important;}}"
        ),
    },
    # ── sidebar: ใหญ่ซ้าย + list ขวา ─────────────────────────
    "sidebar": {
        "label":    "Sidebar — ใหญ่ซ้าย + list ขวา",
        "img_h":    "200px",
        "img_h_side": "72px",
        "img_w_side": "110px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .2s,box-shadow .2s;"
        ),
        "wrapper": lambda cols: "display:grid;grid-template-columns:1.8fr 1fr;gap:1.5rem;",
        "responsive": lambda cols: "@media(max-width:700px){.art-grid{grid-template-columns:1fr!important;}}",
    },
    # ── tiles: รูปเต็ม title ทับล่าง ──────────────────────────
    "tiles": {
        "label":    "Tiles — รูปเต็ม title ทับล่าง",
        "img_h":    "240px",
        "card_css": (
            "display:block;position:relative;"
            "border-radius:16px;overflow:hidden;"
            "text-decoration:none;color:#fff;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 6px 20px rgba(0,0,0,.18);"
        ),
        "wrapper": lambda cols: f"display:grid;grid-template-columns:repeat({cols},1fr);gap:1.1rem;",
        "responsive": lambda cols: (
            f"@media(max-width:900px){{.art-grid{{grid-template-columns:repeat({min(cols,2)},1fr)!important;}}}}"
            f"@media(max-width:560px){{.art-grid{{grid-template-columns:1fr!important;}}}}"
        ),
    },
    # ── masonry: สูงไม่เท่ากัน ─────────────────────────────────
    "masonry": {
        "label":    "Masonry — สูงไม่เท่ากัน",
        "img_h":    "auto",
        "card_css": (
            "display:flex;flex-direction:column;break-inside:avoid;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;margin-bottom:1.25rem;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.06);"
        ),
        "wrapper": lambda cols: f"columns:{cols};column-gap:1.25rem;",
        "responsive": lambda cols: (
            f"@media(max-width:900px){{.art-grid{{columns:{min(cols,2)}!important;}}}}"
            f"@media(max-width:560px){{.art-grid{{columns:1!important;}}}}"
        ),
    },
    # ── zigzag: สลับรูปซ้าย-ขวา [NEW v5] ─────────────────────
    "zigzag": {
        "label":    "Zigzag — รูปสลับซ้าย-ขวา",
        "img_h":    "220px",
        "img_w":    "45%",
        "card_css": (
            "display:flex;flex-direction:row;align-items:stretch;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;margin-bottom:1.25rem;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.06);min-height:180px;"
        ),
        "wrapper": lambda cols: "display:flex;flex-direction:column;gap:0;",
        "responsive": lambda cols: (
            "@media(max-width:600px){.art-grid .zigzag-card{flex-direction:column!important;}}"
            "@media(max-width:600px){.art-grid .zigzag-card img{width:100%!important;height:180px!important;}}"
        ),
    },
    # ── featured: 1 ใหญ่ข้างบน + grid เล็ก [NEW v5] ──────────
    "featured": {
        "label":    "Featured — 1 ใหญ่บน + grid ล่าง",
        "img_h":    "320px",
        "card_css": (
            "display:flex;flex-direction:column;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.06);"
        ),
        "wrapper": lambda cols: f"display:grid;grid-template-columns:repeat({cols},1fr);gap:1.25rem;",
        "responsive": lambda cols: (
            f"@media(max-width:900px){{.art-grid{{grid-template-columns:repeat({min(cols,2)},1fr)!important;}}}}"
            f"@media(max-width:560px){{.art-grid{{grid-template-columns:1fr!important;}}}}"
        ),
    },
    # ── row: horizontal scroll [NEW v5] ───────────────────────
    "row": {
        "label":    "Row — แนวนอน scroll",
        "img_h":    "180px",
        "card_w":   "260px",
        "card_css": (
            "display:flex;flex-direction:column;flex-shrink:0;"
            "background:var(--card,#fff);"
            "border-radius:14px;overflow:hidden;"
            "border:1px solid var(--border,#e2e8f0);"
            "text-decoration:none;color:inherit;"
            "transition:transform .22s,box-shadow .22s;"
            "box-shadow:0 2px 8px rgba(0,0,0,.06);width:260px;"
        ),
        "wrapper": lambda cols: (
            "display:flex;flex-direction:row;gap:1.1rem;"
            "overflow-x:auto;padding-bottom:.75rem;"
            "scrollbar-width:thin;scrollbar-color:rgba(0,0,0,.2) transparent;"
        ),
        "responsive": lambda cols: "",
    },
}

def _layout() -> dict:
    return LAYOUT_DEFS.get(LAYOUT_MODE, LAYOUT_DEFS["grid"])


# ══════════════════════════════════════════════════════════════
# 🔧 Utility helpers
# ══════════════════════════════════════════════════════════════
def สแกน_html() -> list:
    result = []
    for fp in sorted(BASE_PATH.rglob("*")):
        if any(s in fp.parts for s in _SKIP_DIRS): continue
        if fp.suffix.lower() == ".html" and fp.is_file() and fp.parent == BASE_PATH:
            result.append(fp)
    return result

def สแกน_บทความ() -> list:
    result = []
    for fp in สแกน_html():
        if fp.name in _NON_ARTICLE: continue
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if "<html" in txt.lower() and len(txt) > 100:
                result.append(fp)
        except Exception: pass
    return result

def ชื่อหมวด(fp: Path) -> str:
    return fp.stem.split("_")[0] if "_" in fp.stem else fp.stem

def ดึงหัวข้อ(soup, fp: Path) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text().strip(): return h1.get_text().strip()
    title = soup.find("title")
    if title:
        t = re.split(r'\s*[—|–|-]\s*', title.get_text().strip())[0].strip()
        if t: return t
    return fp.stem.replace("_"," ").replace("-"," ").title()

def ดึงรูปหลัก(soup, fp: Path) -> str:
    for cls in ["hero-image-wrapper","hero-image","article-hero","featured-image"]:
        sec = soup.find(class_=cls)
        if sec:
            img = sec.find("img")
            if img:
                s = img.get("src","").strip()
                if s and "picsum" not in s: return s
    for cls in ["article-body","article-content","post-content","content"]:
        sec = soup.find(class_=cls)
        if sec:
            for img in sec.find_all("img"):
                s = img.get("src","").strip()
                if s and "picsum" not in s: return s
    og = soup.find("meta", property="og:image")
    if og and og.get("content"): return og["content"].strip()
    svg_local = BASE_PATH / "images" / "thumbs" / (fp.stem + ".svg")
    if svg_local.exists(): return f"images/thumbs/{fp.stem}.svg"
    for img in soup.find_all("img"):
        s = img.get("src","").strip()
        if s and "icon" not in s.lower() and "logo" not in s.lower(): return s
    return ""

def _fallback_img(stem: str) -> str:
    svg_fb = f"images/thumbs/{stem}.svg"
    seed   = hashlib.md5(stem.encode()).hexdigest()[:8]
    p2     = f"https://picsum.photos/seed/{seed}/400/225"
    grey   = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
              "width='400' height='225'%3E%3Crect width='400' height='225' fill='%23e2e8f0'/%3E"
              "%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' "
              "fill='%2394a3b8' font-size='14'%3Eไม่มีรูปภาพ%3C/text%3E%3C/svg%3E")
    return (f"this.onerror=null;this.src='{svg_fb}';"
            f"this.onerror=function(){{this.onerror=null;this.src='{p2}';"
            f"this.onerror=function(){{this.src='{grey}'}}}}")

def _picsum(stem: str) -> str:
    seed = hashlib.md5(stem.encode()).hexdigest()[:8]
    return f"https://picsum.photos/seed/{seed}/400/225"

def เขียน(fp: Path, html: str, orig: str) -> bool:
    if html == orig: return False
    if DRY_RUN:
        log_info(f"  [DRY-RUN] {fp.name}")
        return True
    fp.write_text(html, encoding="utf-8")
    return True

def wipe_all_blocks(html: str, start: str, end: str) -> str:
    while start in html and end in html:
        s = html.find(start)
        e = html.find(end, s)
        if s == -1 or e == -1: break
        html = html[:s] + html[e+len(end):]
    return html


# ══════════════════════════════════════════════════════════════
# 🃏  BUILD CARDS — รองรับทุก layout
# ══════════════════════════════════════════════════════════════
def _parse_article(fp: Path) -> dict:
    try:
        soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")
        หัวข้อ = ดึงหัวข้อ(soup, fp)
        img    = ดึงรูปหลัก(soup, fp) or _picsum(fp.stem)
        dt_tag = soup.find("time") or soup.find(class_=re.compile(r'date|time|publish', re.I))
        วันที่ = dt_tag.get_text().strip() if dt_tag else ""
        body   = soup.find(class_="article-body") or soup.find("article") or soup.find("main")
        excerpt = ""
        if body:
            for p in body.find_all("p"):
                t = p.get_text().strip()
                if len(t) > 40:
                    excerpt = t[:110] + "…" if len(t) > 110 else t
                    break
        หมวด = ชื่อหมวด(fp)
        return {"หัวข้อ": หัวข้อ, "img": img, "วันที่": วันที่, "excerpt": excerpt, "หมวด": หมวด}
    except Exception:
        return {"หัวข้อ": fp.stem, "img": _picsum(fp.stem), "วันที่": "", "excerpt": "", "หมวด": ""}


def _badge_html(หมวด: str) -> str:
    """สร้าง badge หมวดหมู่"""
    color  = CAT_COLORS.get(หมวด, "#6366f1")
    label  = หมวด_ไทย.get(หมวด, หมวด)
    th     = _theme()
    return (f'<span style="display:inline-block;padding:.18rem .55rem;border-radius:999px;'
            f'background:{color};color:#fff;font-size:.68rem;font-weight:700;'
            f'margin-bottom:.35rem;">{label}</span>')


def _build_cards(ไฟล์บทความ: list) -> str:
    if not ไฟล์บทความ: return ""
    lay    = _layout()
    th     = _theme()
    img_h  = lay.get("img_h", "200px")
    primary = th["primary"]
    hover  = (' onmouseover="this.style.transform=\'translateY(-4px)\';'
              'this.style.boxShadow=\'0 8px 24px rgba(0,0,0,.14)\'"'
              ' onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'"')

    # ── sidebar: สร้าง layout พิเศษ ──────────────────────────
    if LAYOUT_MODE == "sidebar":
        if not ไฟล์บทความ: return ""
        oe0 = _fallback_img(ไฟล์บทความ[0].stem).replace('"','&quot;')
        d0  = _parse_article(ไฟล์บทความ[0])
        badge0 = _badge_html(d0["หมวด"])
        big = (
            f'<a href="{ไฟล์บทความ[0].name}" style="{lay["card_css"]}"{hover}>'
            f'<img src="{d0["img"]}" alt="{d0["หัวข้อ"]}" loading="lazy" onerror="{oe0}"'
            f' style="width:100%;height:360px;object-fit:cover;">'
            f'<div style="padding:1rem;">'
            f'{badge0}'
            f'<h3 style="font-size:1.05rem;font-weight:700;margin:.3rem 0 .5rem;line-height:1.4;">{d0["หัวข้อ"]}</h3>'
            f'<p style="font-size:.82rem;color:#64748b;margin:0;">{d0["excerpt"]}</p>'
            f'</div></a>'
        )
        smalls = ""
        for af in ไฟล์บทความ[1:8]:
            d   = _parse_article(af)
            oe  = _fallback_img(af.stem).replace('"','&quot;')
            smalls += (
                f'<a href="{af.name}" style="display:flex;gap:.65rem;align-items:flex-start;'
                f'padding:.6rem;border-radius:8px;text-decoration:none;color:inherit;'
                f'border-bottom:1px solid var(--border,#e2e8f0);transition:background .15s;"'
                f' onmouseover="this.style.background=\'var(--soft,#f8fafc)\'"'
                f' onmouseout="this.style.background=\'\'">'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:90px;height:64px;object-fit:cover;border-radius:6px;flex-shrink:0;">'
                f'<div style="flex:1;min-width:0;">'
                f'<h3 style="font-size:.87rem;font-weight:600;margin:0;line-height:1.4;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'</div></a>'
            )
        right = (
            f'<div style="display:flex;flex-direction:column;background:var(--card,#fff);'
            f'border-radius:12px;border:1px solid var(--border,#e2e8f0);overflow:hidden;">'
            f'<div style="padding:.75rem 1rem;border-bottom:2px solid {primary};font-weight:700;font-size:.9rem;color:{primary};">'
            f'<i class="fas fa-list-ul"></i> บทความอื่นๆ</div>'
            f'{smalls}</div>'
        )
        return f'<div style="{lay["wrapper"](COLS)}">{big}{right}</div>'

    # ── featured: 1 ใหญ่ข้างบน + grid เล็กข้างล่าง [NEW v5] ──
    if LAYOUT_MODE == "featured":
        if not ไฟล์บทความ: return ""
        oe0   = _fallback_img(ไฟล์บทความ[0].stem).replace('"','&quot;')
        d0    = _parse_article(ไฟล์บทความ[0])
        badge0 = _badge_html(d0["หมวด"])
        featured_card = (
            f'<a href="{ไฟล์บทความ[0].name}" style="display:flex;flex-direction:column;'
            f'background:var(--card,#fff);border-radius:16px;overflow:hidden;'
            f'border:1px solid var(--border,#e2e8f0);text-decoration:none;color:inherit;'
            f'box-shadow:0 4px 16px rgba(0,0,0,.1);margin-bottom:1.5rem;"{hover}>'
            f'<img src="{d0["img"]}" alt="{d0["หัวข้อ"]}" loading="lazy" onerror="{oe0}"'
            f' style="width:100%;height:{img_h};object-fit:cover;">'
            f'<div style="padding:1.25rem;">'
            f'{badge0}'
            f'<h2 style="font-size:1.3rem;font-weight:800;margin:.25rem 0 .5rem;line-height:1.35;">{d0["หัวข้อ"]}</h2>'
            f'<p style="font-size:.88rem;color:#64748b;margin:0;">{d0["excerpt"]}</p>'
            f'<span style="display:inline-block;margin-top:.75rem;padding:.35rem .9rem;'
            f'background:{primary};color:#fff;border-radius:6px;font-size:.8rem;font-weight:600;">'
            f'<i class="fas fa-arrow-right"></i> อ่านต่อ</span>'
            f'</div></a>'
        )
        grid_cards = ""
        cols = COLS if COLS > 0 else 3
        for af in ไฟล์บทความ[1:1+cols*2]:
            d  = _parse_article(af)
            oe = _fallback_img(af.stem).replace('"','&quot;')
            badge = _badge_html(d["หมวด"])
            grid_cards += (
                f'<a href="{af.name}" style="display:flex;flex-direction:column;'
                f'background:var(--card,#fff);border-radius:12px;overflow:hidden;'
                f'border:1px solid var(--border,#e2e8f0);text-decoration:none;color:inherit;'
                f'box-shadow:0 2px 6px rgba(0,0,0,.06);"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:100%;height:170px;object-fit:cover;">'
                f'<div style="padding:.85rem;">'
                f'{badge}'
                f'<h3 style="font-size:.9rem;font-weight:700;margin:.2rem 0;line-height:1.4;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'</div></a>'
            )
        grid_wrap = f'<div class="art-grid" style="{lay["wrapper"](cols)}">{grid_cards}</div>'
        return featured_card + grid_wrap

    # ── zigzag: สลับรูปซ้าย-ขวา [NEW v5] ─────────────────────
    if LAYOUT_MODE == "zigzag":
        cards = ""
        for i, af in enumerate(ไฟล์บทความ):
            d   = _parse_article(af)
            oe  = _fallback_img(af.stem).replace('"','&quot;')
            badge = _badge_html(d["หมวด"])
            img_side  = "left" if i % 2 == 0 else "right"
            row_dir   = "row" if i % 2 == 0 else "row-reverse"
            cards += (
                f'<a href="{af.name}" class="zigzag-card" '
                f'style="display:flex;flex-direction:{row_dir};align-items:stretch;'
                f'background:var(--card,#fff);border-radius:14px;overflow:hidden;'
                f'border:1px solid var(--border,#e2e8f0);text-decoration:none;color:inherit;'
                f'margin-bottom:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,.06);min-height:180px;"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:45%;min-width:200px;object-fit:cover;flex-shrink:0;">'
                f'<div style="flex:1;padding:1.1rem;display:flex;flex-direction:column;justify-content:center;">'
                f'{badge}'
                f'<h3 style="font-size:1rem;font-weight:700;margin:.25rem 0 .5rem;line-height:1.4;">{d["หัวข้อ"]}</h3>'
                f'<p style="font-size:.82rem;color:#64748b;margin:0;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{d["excerpt"]}</p>'
                f'<span style="display:inline-block;margin-top:.75rem;padding:.28rem .75rem;'
                f'border:1.5px solid {primary};color:{primary};border-radius:6px;font-size:.78rem;font-weight:600;">อ่านต่อ →</span>'
                f'</div></a>'
            )
        return cards

    # ── row: horizontal scroll [NEW v5] ───────────────────────
    if LAYOUT_MODE == "row":
        cards = ""
        for af in ไฟล์บทความ:
            d   = _parse_article(af)
            oe  = _fallback_img(af.stem).replace('"','&quot;')
            badge = _badge_html(d["หมวด"])
            cards += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:100%;height:{img_h};object-fit:cover;flex-shrink:0;">'
                f'<div style="padding:.85rem;flex:1;">'
                f'{badge}'
                f'<h3 style="font-size:.9rem;font-weight:700;margin:.2rem 0;line-height:1.4;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'</div></a>'
            )
        return cards

    # ── ทุก layout อื่น: loop การ์ดปกติ ───────────────────────
    การ์ด = ""
    for af in ไฟล์บทความ:
        d   = _parse_article(af)
        oe  = _fallback_img(af.stem).replace('"','&quot;')
        badge = _badge_html(d["หมวด"])
        วันที่_html = (
            f'<div style="font-size:.71rem;color:var(--muted,#94a3b8);margin-bottom:.2rem;">'
            f'{d["วันที่"]}</div>'
        ) if d["วันที่"] else ""
        excerpt_html = (
            f'<p style="margin:.3rem 0 0;font-size:.81rem;color:var(--muted,#64748b);'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;'
            f'-webkit-box-orient:vertical;">{d["excerpt"]}</p>'
        ) if d["excerpt"] else ""

        if LAYOUT_MODE == "list":
            img_w = lay.get("img_w","140px")
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"'
                f' onmouseover="this.style.boxShadow=\'0 4px 16px rgba(0,0,0,.1)\';this.style.background=\'var(--soft,#f8fafc)\'"'
                f' onmouseout="this.style.boxShadow=\'\';this.style.background=\'\'">'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:{img_w};height:{img_h};object-fit:cover;border-radius:8px;flex-shrink:0;">'
                f'<div style="flex:1;min-width:0;">'
                f'{badge}'
                f'{วันที่_html}'
                f'<h3 style="font-size:.93rem;font-weight:700;margin:0;line-height:1.4;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'{excerpt_html}</div></a>'
            )

        elif LAYOUT_MODE == "tiles":
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="position:absolute;inset:0;width:100%;height:{img_h};object-fit:cover;">'
                f'<div style="position:relative;height:{img_h};display:flex;flex-direction:column;justify-content:flex-end;">'
                f'<div style="background:linear-gradient(transparent 15%,rgba(0,0,0,.8));padding:.85rem .9rem .75rem;">'
                f'{badge}'
                f'<h3 style="color:#fff;font-size:.93rem;font-weight:700;margin:.2rem 0 0;line-height:1.4;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'</div></div></a>'
            )

        elif LAYOUT_MODE in ("grid","hero3","magazine","compact","compact5","compact6","masonry"):
            show_excerpt = LAYOUT_MODE not in ("compact5","compact6")
            excerpt_part = excerpt_html if show_excerpt else ""
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:100%;height:{img_h};object-fit:cover;">'
                f'<div style="padding:.9rem;flex:1;display:flex;flex-direction:column;">'
                f'{badge}'
                f'{วันที่_html}'
                f'<h3 style="font-size:.92rem;font-weight:700;margin:0;line-height:1.45;flex:1;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'{excerpt_part}'
                f'</div></a>'
            )
        else:
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:100%;height:{img_h};object-fit:cover;">'
                f'<div style="padding:.9rem;flex:1;">'
                f'{badge}{วันที่_html}'
                f'<h3 style="font-size:.92rem;font-weight:700;margin:0;line-height:1.45;">{d["หัวข้อ"]}</h3>'
                f'</div></a>'
            )

    return การ์ด


def _wrap_block(การ์ด: str, label: str, count: int) -> str:
    lay      = _layout()
    th       = _theme()
    resp_css = lay["responsive"](COLS)
    resp_tag = f'<style>{resp_css}</style>' if resp_css else ""

    if LAYOUT_MODE in ("sidebar","featured","zigzag"):
        inner = การ์ด
    elif LAYOUT_MODE == "row":
        wrapper = lay["wrapper"](COLS)
        inner = f'<div class="art-grid" style="{wrapper}">{การ์ด}</div>'
    else:
        wrapper = lay["wrapper"](COLS)
        inner = f'<div class="art-grid" style="{wrapper}">{การ์ด}</div>'

    return (
        f"\n{ART_S}\n"
        f'<div style="max-width:1140px;margin:0 auto;background:var(--soft,#f8fafc);'
        f'border-radius:16px;padding:1.4rem;'
        f'box-shadow:0 4px 16px rgba(30,64,175,0.06);margin-top:1rem;">'
        f'<h2 style="color:{th["primary"]};font-size:1.05rem;margin:0 0 1.1rem;'
        f'display:flex;align-items:center;gap:.5rem;">'
        f'<i class="fas fa-fire" style="color:#ef4444;"></i> {label} '
        f'<span style="font-size:.8rem;font-weight:400;color:var(--muted,#64748b);">({count} บทความ)</span></h2>'
        f'{resp_tag}'
        f'{inner}'
        f'</div>'
        f"\n{ART_E}\n"
    )


# ══════════════════════════════════════════════════════════════
# 📋 STEP 1: AUDIT
# ══════════════════════════════════════════════════════════════
def audit_ทั้งหมด() -> dict:
    log_section("📋 AUDIT — ตรวจสอบทุกส่วน")
    ทุกไฟล์  = สแกน_html()
    บทความ   = สแกน_บทความ()
    ชื่อไฟล์ = {fp.name for fp in ทุกไฟล์}
    log_info(f"ไฟล์ HTML: {len(ทุกไฟล์)} | บทความ: {len(บทความ)} | Layout: {LAYOUT_MODE} {COLS}col | Theme: {THEME_NAME}")

    idx_path = BASE_PATH / "index.html"
    if idx_path.exists():
        idx_txt = idx_path.read_text(encoding="utf-8", errors="ignore")
        if IDX_S not in idx_txt:
            log_warn("⚠️  index.html ยังไม่มี INDEX_ARTICLES block")

    ปัญหา = {
        "ไม่มี nav.js":          [],
        "ไม่มี h1":              [],
        "เนื้อหาว่าง/สั้น":       [],
        "รูปหาย":                [],
        "รูปไม่มี onerror":      [],
        "dead links":            [],
        "empty links":           [],
        "block ซ้ำ":             [],
        "หน้าหมวดไม่มี block":   [],
        "layout ไม่สม่ำเสมอ":   [],
        # ✅ v5 เพิ่ม
        "footer สีผิด":          [],
        "hero gradient ผิด":     [],
    }

    th = _theme()
    for fp in sorted(บทความ, key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            txt  = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(txt, "html.parser")
            if "nav.js" not in txt:             ปัญหา["ไม่มี nav.js"].append(fp.name)
            if not soup.find("h1"):             ปัญหา["ไม่มี h1"].append(fp.name)
            body = soup.find(class_="article-body") or soup.find("main")
            if body and len(body.get_text().strip()) < 200:
                ปัญหา["เนื้อหาว่าง/สั้น"].append(fp.name)
            for img in soup.find_all("img"):
                src = img.get("src","").strip()
                if not img.get("onerror"):      ปัญหา["รูปไม่มี onerror"].append(fp.name)
                if src.startswith("images/") and not src.startswith("http"):
                    if not (BASE_PATH/src).exists():
                        ปัญหา["รูปหาย"].append(f"{fp.name} → {src}")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href in ("#","","javascript:void(0)"):
                    ปัญหา["empty links"].append(fp.name)
                elif (href.endswith(".html") and not href.startswith("http")
                      and not href.startswith("#") and href not in ชื่อไฟล์):
                    ปัญหา["dead links"].append(f"{fp.name} → {href}")
        except Exception as e:
            log_err(f"  audit {fp.name}: {e}")

    for fp in สแกน_html():
        if fp.name not in (_CAT_FILES | {"index.html"}): continue
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if txt.count(ART_S) > 1:        ปัญหา["block ซ้ำ"].append(f"{fp.name} ({txt.count(ART_S)}x)")
            if fp.name in _CAT_FILES and ART_S not in txt:
                ปัญหา["หน้าหมวดไม่มี block"].append(fp.name)
            # ✅ v5: ตรวจสีบน-ล่าง
            if "footer" in txt.lower():
                if _theme()["dark"] not in txt and _theme()["primary"] not in txt:
                    ปัญหา["footer สีผิด"].append(fp.name)
        except Exception: pass

    log("\n📊 สรุปปัญหา:")
    รวม = 0
    for k, v in ปัญหา.items():
        icon = "✅" if not v else "❌"
        unique = list(set(v))
        log(f"  {icon} {k}: {len(unique)}")
        for x in unique[:3]: log(f"       - {x}")
        รวม += len(unique)

    log("\n📋 ไฟล์ระบบ:")
    now = datetime.datetime.now()
    for fn in ["style.css","nav.js","index.html","sitemap.xml","robots.txt"]:
        p = BASE_PATH / fn
        if p.exists():
            sz  = round(p.stat().st_size/1024, 1)
            age = int((now - datetime.datetime.fromtimestamp(p.stat().st_mtime)).total_seconds()/3600)
            log(f"  ✅ {fn:<25} {sz:>6.1f} KB | {age} ชม.ที่แล้ว")
        else:
            log(f"  ❌ {fn} — ไม่พบ!")

    log(f"\n  Layout: {LAYOUT_MODE} | Cols: {COLS} | Theme: {THEME_NAME} | บทความ: {len(บทความ)} | ปัญหา: {รวม}")
    return ปัญหา


# ══════════════════════════════════════════════════════════════
# 📊 STATS (--stats) [NEW v5]
# ══════════════════════════════════════════════════════════════
def แสดง_สถิติ():
    log_section("📊 สถิติเว็บไซต์")
    บทความ = สแกน_บทความ()
    by_cat  = defaultdict(list)
    total_size = 0
    for fp in บทความ:
        by_cat[ชื่อหมวด(fp)].append(fp)
        total_size += fp.stat().st_size

    log(f"  📝 บทความทั้งหมด: {len(บทความ)} ชิ้น")
    log(f"  💾 ขนาดรวม: {total_size/1024:.1f} KB ({total_size/1024/1024:.2f} MB)")
    log(f"  📁 หมวดหมู่: {len(by_cat)} หมวด")
    log(f"")
    for cat, fps in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        th_name = หมวด_ไทย.get(cat, cat)
        avg_sz  = sum(f.stat().st_size for f in fps) / len(fps) / 1024
        log(f"  {'▪' if len(fps) >= 5 else '·'} {th_name:<14} {len(fps):>4} บทความ  avg {avg_sz:.1f} KB")

    # ใหม่สุด
    newest = sorted(บทความ, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
    log(f"\n  🕐 ใหม่ที่สุด 5 อัน:")
    for fp in newest:
        dt = datetime.datetime.fromtimestamp(fp.stat().st_mtime).strftime("%d/%m %H:%M")
        log(f"     {dt}  {fp.name}")


# ══════════════════════════════════════════════════════════════
# 🔧 FIX NAV
# ══════════════════════════════════════════════════════════════
def แก้_nav() -> int:
    log_section("🧭 แก้ Nav Bar")
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if "nav.js" in orig: continue
            if "<body>" not in orig.lower(): continue
            html = re.sub(r'(<body[^>]*>)', r'\1\n<script src="nav.js"></script>',
                          orig, count=1, flags=re.IGNORECASE)
            if เขียน(fp, html, orig):
                แก้แล้ว += 1
                log_ok(f"  เพิ่ม nav.js: {fp.name}")
        except Exception as e:
            log_err(f"  nav {fp.name}: {e}")
    log_ok(f"แก้ nav: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX DEAD LINKS
# ══════════════════════════════════════════════════════════════
def แก้_dead_links() -> int:
    log_section("🔗 แก้ Dead/Empty Links")
    ทุกไฟล์  = สแกน_html()
    ชื่อไฟล์ = {fp.name for fp in ทุกไฟล์}
    แก้แล้ว  = 0
    for fp in ทุกไฟล์:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            changed = False
            for a in list(soup.find_all("a", href=True)):
                href = a["href"].strip()
                if href in ("#","","javascript:void(0)"):
                    a.unwrap(); changed = True; continue
                if (href.endswith(".html") and not href.startswith("http")
                        and not href.startswith("#") and href not in ชื่อไฟล์):
                    card = None
                    for anc in a.parents:
                        tag = getattr(anc,'name','')
                        if tag in ('div','article','li') and anc != soup:
                            if len(anc.find_all('a', href=True)) == 1:
                                card = anc; break
                    if card and card != soup.body: card.decompose()
                    else: a.unwrap()
                    changed = True
                    log_warn(f"  ลบ dead link: {fp.name} → {href}")
            if changed and เขียน(fp, str(soup), orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  links {fp.name}: {e}")
    log_ok(f"แก้ links: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX IMAGES
# ══════════════════════════════════════════════════════════════
def แก้_รูปภาพ() -> int:
    log_section("🖼️  แก้รูปภาพ")
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            # เพิ่ม loading lazy
            html = re.sub(r'(<img\b(?![^>]*\bloading=)[^>]*?)(/?>)', r'\1 loading="lazy"\2', html)
            # แก้ src ว่าง
            html = re.sub(r'(<img\b[^>]*)\bsrc=["\'](\s*)["\']',
                          lambda m: m.group(1) + f' src="{_picsum(fp.stem)}"', html)
            # แก้ local src หาย
            def _fix_src(m):
                tag = m.group(0)
                s = re.search(r'src=["\']([^"\']+)["\']', tag)
                if not s: return tag
                src = s.group(1)
                if src.startswith("images/") and not src.startswith("http"):
                    if not (BASE_PATH/src).exists():
                        svg = BASE_PATH/"images"/"thumbs"/(fp.stem+".svg")
                        new = f"images/thumbs/{fp.stem}.svg" if svg.exists() else _picsum(fp.stem)
                        tag = tag.replace(s.group(0), f'src="{new}"')
                return tag
            html = re.sub(r'<img\b[^>]*>', _fix_src, html)
            # เพิ่ม onerror
            def _add_onerror(m):
                tag = m.group(0)
                if 'onerror=' in tag: return tag
                s = re.search(r'src=["\']([^"\']+)["\']', tag)
                stem = fp.stem
                if s:
                    sv = re.search(r'thumbs/([^/]+?)\.svg', s.group(1))
                    if sv: stem = sv.group(1)
                fb = _fallback_img(stem)
                return tag.rstrip('>').rstrip('/') + f' onerror="{fb}">'
            html = re.sub(r'<img\b[^>]*>', _add_onerror, html)
            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  รูป {fp.name}: {e}")
    log_ok(f"แก้รูป: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX SVG EMOJI
# ══════════════════════════════════════════════════════════════
def แก้_svg_emoji() -> int:
    svg_dir = BASE_PATH / "images" / "thumbs"
    แก้แล้ว = 0
    if not svg_dir.exists(): return 0
    for fp in svg_dir.glob("*.svg"):
        try:
            txt = fp.read_text(encoding="utf-8")
            if re.search(r'[\U00010000-\U0010FFFF]', txt):
                if not DRY_RUN:
                    fp.write_text(re.sub(r'[\U00010000-\U0010FFFF]', '', txt), encoding="utf-8")
                    แก้แล้ว += 1
        except Exception: pass
    log_ok(f"แก้ SVG emoji: {แก้แล้ว}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX H1
# ══════════════════════════════════════════════════════════════
def แก้_h1() -> int:
    log_section("📰 แก้ h1")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            if soup.find("h1"): continue
            หัวข้อ = ดึงหัวข้อ(soup, fp)
            html = orig
            for ins in ["<article","<main","<div class=\"article-body\""]:
                if ins in html:
                    idx = html.find(ins)
                    end = html.find(">", idx) + 1
                    html = html[:end] + f"\n<h1>{หัวข้อ}</h1>\n" + html[end:]
                    break
            else:
                html = html.replace("<body>", f"<body>\n<h1>{หัวข้อ}</h1>", 1)
            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  h1 {fp.name}: {e}")
    log_ok(f"แก้ h1: {แก้แล้ว}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX EMPTY CONTENT
# ══════════════════════════════════════════════════════════════
def _สร้างเนื้อหาพื้นฐาน(หัวข้อ: str, หมวด: str) -> str:
    try:
        content = เรียก_ollama(
            f'เขียนบทความภาษาไทยหัวข้อ "{หัวข้อ}" หมวด {หมวด_ไทย.get(หมวด,หมวด)} '
            f'ยาว 3-5 ย่อหน้า ตอบด้วยเนื้อหาเท่านั้น', num_predict=800)
        if content and len(content) > 100:
            paras = [f"<p>{p.strip()}</p>" for p in content.split("\n")
                     if p.strip() and len(p.strip()) > 20]
            return "\n".join(paras) if paras else f"<p>{content[:500]}</p>"
    except Exception: pass
    return (f"<p>{หัวข้อ} เป็นเรื่องที่น่าสนใจสำหรับผู้อ่านทุกท่าน</p>"
            f"<p>ติดตามบทความใหม่ได้ทุกวัน</p>")

def แก้_เนื้อหาว่าง() -> int:
    log_section("📝 แก้เนื้อหาว่าง")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            body = soup.find(class_="article-body")
            if not body or len(body.get_text().strip()) >= 200: continue
            log_warn(f"  สั้น: {fp.name}")
            body.clear()
            body.append(BeautifulSoup(
                _สร้างเนื้อหาพื้นฐาน(ดึงหัวข้อ(soup, fp), ชื่อหมวด(fp)),
                "html.parser"))
            if เขียน(fp, str(soup), orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  เนื้อหา {fp.name}: {e}")
    log_ok(f"แก้เนื้อหาว่าง: {แก้แล้ว}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 RELATED ARTICLES
# ══════════════════════════════════════════════════════════════
def แก้_related_articles() -> int:
    log_section("🔗 Related Articles")
    บทความทั้งหมด = สแกน_บทความ()
    by_cat = defaultdict(list)
    for f in บทความทั้งหมด: by_cat[ชื่อหมวด(f)].append(f)
    th = _theme()
    แก้แล้ว = 0
    for fp in บทความทั้งหมด:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if REL_S in orig: continue
            related = [f for f in by_cat[ชื่อหมวด(fp)] if f != fp][:4]
            if not related: continue
            soup = BeautifulSoup(orig, "html.parser")
            การ์ด = ""
            for rf in related:
                rs  = BeautifulSoup(rf.read_text(encoding="utf-8", errors="ignore"), "html.parser")
                rh  = ดึงหัวข้อ(rs, rf)
                ri  = ดึงรูปหลัก(rs, rf) or _picsum(rf.stem)
                oe  = _fallback_img(rf.stem).replace('"','&quot;')
                การ์ด += (
                    f'<a href="{rf.name}" style="display:block;border-radius:10px;overflow:hidden;'
                    f'background:#fff;border:1px solid #e2e8f0;text-decoration:none;color:inherit;'
                    f'box-shadow:0 2px 6px rgba(0,0,0,.05);">'
                    f'<img src="{ri}" alt="{rh}" loading="lazy" style="width:100%;height:130px;'
                    f'object-fit:cover;" onerror="{oe}">'
                    f'<div style="padding:.6rem;">'
                    f'<p style="margin:0;font-size:.83rem;font-weight:600;line-height:1.4;">{rh}</p>'
                    f'</div></a>')
            block = (
                f'\n{REL_S}\n'
                f'<div style="margin-top:2rem;padding:1.25rem;background:#f1f5f9;border-radius:12px;">'
                f'<h3 style="color:{th["primary"]};margin:0 0 1rem;font-size:1rem;">'
                f'<i class="fas fa-bookmark"></i> บทความที่เกี่ยวข้อง</h3>'
                f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.75rem;">'
                f'{การ์ด}</div></div>\n{REL_E}\n'
            )
            html = orig
            for tag in ["</article>","</main>","</body>"]:
                if tag in html:
                    idx = html.rfind(tag)
                    html = html[:idx] + block + html[idx:]
                    break
            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  related {fp.name}: {e}")
    log_ok(f"related: {แก้แล้ว}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🎨 BUILD FOOTER HTML [SHARED] — ✅ v5: สีเดียวกันทั้งเว็บ
# ══════════════════════════════════════════════════════════════
def _build_footer_html() -> str:
    """Footer ที่ใช้สีเดียวกับ hero gradient — แก้ BUG-COLOR"""
    th = _theme()
    # ใช้ _footer_gradient() ให้ดูสม่ำเสมอกับ hero
    cat_links = " · ".join(
        f'<a href="{CATEGORY_PAGE_MAP.get(c, c+".html")}" '
        f'style="color:rgba(255,255,255,.75);text-decoration:none;">{หมวด_ไทย.get(c, c)}</a>'
        for c in CATEGORIES
    )
    return f'''<footer style="background:{_footer_gradient()};color:rgba(255,255,255,.88);
text-align:center;padding:2.5rem 1rem 1.75rem;font-size:.88rem;margin-top:1.5rem;">
  <div style="max-width:900px;margin:0 auto;">
    <div style="font-size:1.4rem;font-weight:800;letter-spacing:.04em;margin-bottom:.4rem;opacity:.9;">
      {SITE_NAME}
    </div>
    <p style="margin:0 0 1rem;font-size:.82rem;opacity:.65;">แหล่งรวมบทความคุณภาพสูง อัปเดตทุกวัน</p>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem 1.2rem;margin-bottom:.9rem;">
      <a href="index.html"   style="color:rgba(255,255,255,.75);text-decoration:none;">🏠 หน้าแรก</a>
      <a href="contact.html" style="color:rgba(255,255,255,.75);text-decoration:none;">📬 ติดต่อเรา</a>
      <a href="privacy.html" style="color:rgba(255,255,255,.75);text-decoration:none;">🔒 นโยบายฯ</a>
      <a href="sitemap.xml"  style="color:rgba(255,255,255,.75);text-decoration:none;">🗺️ Sitemap</a>
    </div>
    <div style="margin-bottom:.9rem;font-size:.83rem;opacity:.7;">{cat_links}</div>
    <div style="border-top:1px solid rgba(255,255,255,.15);padding-top:.75rem;margin-top:.25rem;">
      <p style="margin:0;color:rgba(255,255,255,.45);font-size:.79rem;">
        © {datetime.datetime.now().year} {SITE_NAME} · เว็บไซต์นี้ใช้ Google AdSense และลิงก์พันธมิตร (Affiliate)
      </p>
    </div>
  </div>
</footer>'''


# ══════════════════════════════════════════════════════════════
# 🎨 BUILD HERO HTML [SHARED]
# ══════════════════════════════════════════════════════════════
def _build_hero_index(count: int, cat_pills: str) -> str:
    th = _theme()
    return f'''<!-- HERO SECTION -->
<div style="background:{_hero_gradient()};color:#fff;padding:3.75rem 1.5rem 2.75rem;text-align:center;position:relative;overflow:hidden;">
  <div style="position:absolute;inset:0;background:url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2220%22 cy=%2220%22 r=%2260%22 fill=%22rgba(255,255,255,.04)%22/><circle cx=%2280%22 cy=%2280%22 r=%2240%22 fill=%22rgba(255,255,255,.03)%22/></svg>') no-repeat center;background-size:cover;"></div>
  <div style="position:relative;z-index:1;">
    <h1 style="font-size:clamp(1.9rem,5vw,3rem);font-weight:800;margin-bottom:.75rem;line-height:1.18;letter-spacing:-.01em;">{SITE_NAME}</h1>
    <p style="font-size:1.02rem;opacity:.88;max-width:580px;margin:0 auto 1.5rem;">แหล่งรวมบทความคุณภาพสูง อัปเดตทุกวัน</p>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.5rem;margin-bottom:1.6rem;">{cat_pills}</div>
    <div style="max-width:500px;margin:0 auto;position:relative;">
      <i class="fas fa-search" style="position:absolute;left:.9rem;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.7);z-index:1;"></i>
      <input id="search-input" type="text" placeholder="ค้นหาบทความ..." autocomplete="off"
        style="width:100%;padding:.7rem 1rem .7rem 2.6rem;border:none;border-radius:999px;
               background:rgba(255,255,255,.16);color:#fff;font-family:inherit;font-size:.97rem;
               outline:none;backdrop-filter:blur(6px);box-sizing:border-box;"
        onfocus="this.style.background='rgba(255,255,255,.25)'"
        onblur="this.style.background='rgba(255,255,255,.16)'">
      <div id="search-results" style="position:absolute;top:115%;left:0;right:0;background:var(--card,#fff);
           border-radius:14px;box-shadow:0 12px 32px rgba(0,0,0,.28);z-index:200;overflow:hidden;
           max-height:380px;overflow-y:auto;"></div>
    </div>
    <div style="display:flex;justify-content:center;gap:2rem;margin-top:1.5rem;font-size:.85rem;opacity:.75;">
      <div><span style="font-size:1.25rem;font-weight:800;">{count}</span><br>บทความ</div>
      <div><span style="font-size:1.25rem;font-weight:800;">{len(CATEGORIES)}</span><br>หมวดหมู่</div>
      <div><span style="font-size:1.25rem;font-weight:800;">∞</span><br>อัปเดตทุกวัน</div>
    </div>
  </div>
</div>'''


def _build_hero_category(th_name: str, desc: str) -> str:
    return (f'<div style="background:{_hero_gradient()};color:#fff;padding:2rem 1.5rem 1.5rem;text-align:center;">'
            f'<h1 style="font-size:1.75rem;font-weight:700;margin:0;">'
            f'<i class="fas fa-tag"></i> {th_name}</h1>'
            f'<p style="margin:.4rem 0 0;opacity:.85;font-size:.9rem;">{desc}</p>'
            f'</div>')


# ══════════════════════════════════════════════════════════════
# 🔧 --fix-footer: แก้ footer ทุกหน้า [NEW v5]
# ══════════════════════════════════════════════════════════════
def แก้_footer_ทุกหน้า() -> int:
    """แก้ footer ทุกหน้าให้ใช้สีเดียวกัน — ✅ BUG-COLOR FIX"""
    log_section("🎨 แก้ Footer สีทุกหน้า")
    footer_html = _build_footer_html()
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if "<footer" not in orig.lower(): continue
            # แทนที่ footer เก่าทั้งหมด
            new_html = re.sub(
                r'<footer[\s\S]*?</footer>',
                footer_html, orig, flags=re.IGNORECASE
            )
            if เขียน(fp, new_html, orig):
                แก้แล้ว += 1
                log_ok(f"  แก้ footer: {fp.name}")
        except Exception as e:
            log_err(f"  footer {fp.name}: {e}")
    log_ok(f"แก้ footer: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 --fix-hero: แก้ hero ทุกหน้า [NEW v5]
# ══════════════════════════════════════════════════════════════
def แก้_hero_ทุกหน้า() -> int:
    """แก้ hero gradient ของหน้าหมวดให้ match กับ index"""
    log_section("🎨 แก้ Hero Gradient ทุกหน้า")
    แก้แล้ว = 0
    th = _theme()
    for fp in สแกน_html():
        if fp.name not in _CAT_FILES: continue
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            # แก้ background ทุก div ที่มี hero/banner gradient
            def _fix_bg(m):
                tag = m.group(0)
                # แก้ gradient เก่า
                tag = re.sub(r'linear-gradient\([^)]+\)', _hero_gradient(), tag)
                # แก้ background:#[0-9a-f]{3,6} ใน hero zone
                return tag
            new_html = re.sub(
                r'<div[^>]*(?:hero|banner|jumbotron)[^>]*>',
                _fix_bg, orig, flags=re.IGNORECASE
            )
            # แก้สี CSS variable ใน <style> header
            new_html = re.sub(
                r'(--primary:\s*)#[0-9a-fA-F]{3,6}',
                r'\g<1>' + th['primary'], new_html
            )
            new_html = re.sub(
                r'(--dark:\s*)#[0-9a-fA-F]{3,6}',
                r'\g<1>' + th['dark'], new_html
            )
            if เขียน(fp, new_html, orig):
                แก้แล้ว += 1
                log_ok(f"  แก้ hero: {fp.name}")
        except Exception as e:
            log_err(f"  hero {fp.name}: {e}")
    log_ok(f"แก้ hero: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 --fix-css: สร้าง style.css ใหม่ [NEW v5]
# ══════════════════════════════════════════════════════════════
def rebuild_style_css() -> int:
    """สร้าง style.css ใหม่ที่มี CSS variables และ utility classes ครบ"""
    log_section("🎨 Rebuild style.css")
    th = _theme()
    css = f"""/* style.css — ไอหมอก v5 — auto-generated {datetime.datetime.now().strftime("%Y-%m-%d")} */
/* Theme: {THEME_NAME} */

/* ══ CSS Variables ══════════════════════════════════════════ */
:root {{
  --primary:   {th['primary']};
  --dark:      {th['dark']};
  --accent:    {th['accent']};
  --card:      #ffffff;
  --bg:        #f8fafc;
  --soft:      #f1f5f9;
  --border:    #e2e8f0;
  --muted:     #64748b;
  --text:      #1e293b;
  --radius:    12px;
  --shadow-sm: 0 1px 4px rgba(0,0,0,.06);
  --shadow:    0 4px 16px rgba(0,0,0,.09);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.14);
  --font:      'Sarabun', sans-serif;
}}

/* Dark mode */
@media (prefers-color-scheme: dark) {{
  :root {{
    --card:   #1e293b;
    --bg:     #0f172a;
    --soft:   #1e293b;
    --border: #334155;
    --muted:  #94a3b8;
    --text:   #e2e8f0;
  }}
}}

/* ══ Reset ══════════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}

img {{ max-width: 100%; height: auto; display: block; }}
a   {{ color: var(--primary); }}

/* ══ Layout ═════════════════════════════════════════════════ */
.page-main {{
  max-width: 1140px;
  margin: 0 auto;
  padding: 1rem 1.25rem 2.5rem;
}}

.container {{
  max-width: 1140px;
  margin: 0 auto;
  padding: 0 1.25rem;
}}

/* ══ Art Grid ═══════════════════════════════════════════════ */
.art-grid a:hover {{
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}}

/* Horizontal scroll bar */
.art-grid::-webkit-scrollbar {{ height: 5px; }}
.art-grid::-webkit-scrollbar-track {{ background: transparent; }}
.art-grid::-webkit-scrollbar-thumb {{ background: rgba(0,0,0,.18); border-radius: 999px; }}

/* ══ Cards ══════════════════════════════════════════════════ */
.card {{
  background: var(--card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform .22s, box-shadow .22s;
}}
.card:hover {{
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}}

/* ══ Nav ════════════════════════════════════════════════════ */
nav {{
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--primary);
  color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,.18);
}}

/* ══ Badges ═════════════════════════════════════════════════ */
.badge {{
  display: inline-block;
  padding: .2rem .6rem;
  border-radius: 999px;
  font-size: .68rem;
  font-weight: 700;
  background: var(--accent);
  color: #fff;
}}

/* ══ Buttons ════════════════════════════════════════════════ */
.btn {{
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: .45rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: var(--font);
  font-size: .88rem;
  font-weight: 600;
  text-decoration: none;
  transition: opacity .2s, transform .15s;
}}
.btn:hover {{ opacity: .88; transform: translateY(-1px); }}
.btn-primary {{ background: var(--primary); color: #fff; }}
.btn-outline  {{ background: transparent; border: 1.5px solid var(--primary); color: var(--primary); }}

/* ══ Article Page ════════════════════════════════════════════ */
.article-body {{
  max-width: 760px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}}
.article-body h2 {{ font-size: 1.25rem; margin: 1.5rem 0 .6rem; color: var(--primary); }}
.article-body h3 {{ font-size: 1.05rem; margin: 1.2rem 0 .5rem; }}
.article-body p  {{ margin-bottom: 1rem; line-height: 1.8; }}
.article-body ul, .article-body ol {{ margin: .75rem 0 1rem 1.5rem; }}
.article-body li {{ margin-bottom: .4rem; line-height: 1.7; }}
.article-body blockquote {{
  border-left: 4px solid var(--accent);
  padding: .75rem 1.25rem;
  margin: 1rem 0;
  background: var(--soft);
  border-radius: 0 8px 8px 0;
  font-style: italic;
}}
.article-body img {{
  border-radius: 10px;
  margin: 1rem auto;
  box-shadow: var(--shadow-sm);
}}
.hero-image-wrapper img {{
  width: 100%;
  max-height: 480px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 1.25rem;
}}

/* ══ Sidebar ════════════════════════════════════════════════ */
.sidebar {{
  min-width: 240px;
}}
.sidebar-box {{
  background: var(--card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 1.1rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1rem;
}}

/* ══ Search ═════════════════════════════════════════════════ */
#search-results a {{
  display: flex;
  gap: .6rem;
  align-items: center;
  padding: .55rem .85rem;
  border-bottom: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  font-size: .88rem;
  transition: background .15s;
}}
#search-results a:hover {{ background: var(--soft); }}
#search-results a img {{
  width: 52px; height: 38px;
  object-fit: cover;
  border-radius: 5px;
  flex-shrink: 0;
}}

/* ══ Utility ════════════════════════════════════════════════ */
.text-center {{ text-align: center; }}
.text-muted  {{ color: var(--muted); }}
.mt-1 {{ margin-top: .5rem; }}
.mt-2 {{ margin-top: 1rem; }}
.mt-3 {{ margin-top: 1.5rem; }}
.mb-1 {{ margin-bottom: .5rem; }}
.mb-2 {{ margin-bottom: 1rem; }}
.mb-3 {{ margin-bottom: 1.5rem; }}

/* ══ Responsive ══════════════════════════════════════════════ */
@media (max-width: 768px) {{
  .page-main {{ padding: .75rem .9rem 2rem; }}
  .article-body {{ padding: 1rem .9rem 2.5rem; }}
  h1 {{ font-size: 1.5rem !important; }}
}}

@media (max-width: 480px) {{
  .page-main {{ padding: .6rem .7rem 1.5rem; }}
}}

/* ══ Print ══════════════════════════════════════════════════ */
@media print {{
  nav, footer, .sidebar, #search-results {{ display: none !important; }}
  .article-body {{ max-width: 100%; padding: 0; }}
}}
"""
    fp = BASE_PATH / "style.css"
    if not DRY_RUN:
        fp.write_text(css, encoding="utf-8")
        log_ok(f"เขียน style.css ใหม่: {len(css)} chars")
        return 1
    else:
        log_info(f"[DRY-RUN] จะเขียน style.css ({len(css)} chars)")
        return 0


# ══════════════════════════════════════════════════════════════
# 🔧 REBUILD CATEGORY PAGES
# ══════════════════════════════════════════════════════════════
_CAT_TITLE = {
    "finance":      ("การเงิน",      "รวมบทความการเงินและการลงทุน อัปเดตทุกวัน"),
    "lifestyle":    ("ไลฟ์สไตล์",    "รวมบทความไลฟ์สไตล์คุณภาพสูง อัปเดตทุกวัน"),
    "food":         ("อาหาร",        "รวมบทความอาหารและการกิน อัปเดตทุกวัน"),
    "health":       ("สุขภาพ",       "รวมบทความสุขภาพคุณภาพสูง อัปเดตทุกวัน"),
    "news":         ("ข่าวสาร",      "รวมบทความข่าวสารคุณภาพสูง อัปเดตทุกวัน"),
    "technology":   ("เทคโนโลยี",    "รวมบทความเทคโนโลยีคุณภาพสูง อัปเดตทุกวัน"),
    "entertainment":("บันเทิง",      "รวมบทความบันเทิงและความบันเทิง อัปเดตทุกวัน"),
    "ai":           ("AI",           "รวมบทความปัญญาประดิษฐ์ อัปเดตทุกวัน"),
    "sport":        ("กีฬา",         "รวมบทความกีฬา อัปเดตทุกวัน"),
    "horoscope":    ("ดูดวง",        "รวมบทความดูดวงโหราศาสตร์ อัปเดตทุกวัน"),
}

def _สร้างหน้าหมวด_ครบ(หน้า: str, content_block: str) -> str:
    stem = หน้า.replace(".html","")
    th_name, desc = _CAT_TITLE.get(stem, (stem, f"รวมบทความ{stem} อัปเดตทุกวัน"))
    url  = f"{SITE_URL}/{หน้า}"
    th   = _theme()
    hero = _build_hero_category(th_name, desc)
    footer = _build_footer_html()

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{th_name} — {SITE_NAME}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{th_name} — {SITE_NAME}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{SITE_URL}/images/og-default.png">
  <meta property="og:locale" content="th_TH">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{th_name} — {SITE_NAME}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{SITE_URL}/images/og-default.png">
  <link rel="canonical" href="{url}">
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="{th['primary']}">
  <link rel="apple-touch-icon" href="images/icon-192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="style.css">
  <style>
    :root{{--primary:{th['primary']};--dark:{th['dark']};--accent:{th['accent']};}}
    .page-main{{max-width:1140px;margin:0 auto;padding:1rem 1.25rem 2rem;}}
    .art-grid a:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.13);}}
  </style>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList",
    "itemListElement":[
      {{"@type":"ListItem","position":1,"name":"หน้าแรก","item":"{SITE_URL}/"}},
      {{"@type":"ListItem","position":2,"name":"{th_name}","item":"{url}"}}
    ]}}</script>
</head>
<body>
<script src="nav.js"></script>
<nav></nav>
{hero}
<div class="page-main">
{content_block}
</div>
{footer}
<script>
  // Search index (re-use from index)
  try {{
    fetch('search-index.json').then(r=>r.json()).then(idx=>{{
      const inp = document.getElementById('search-input');
      const box = document.getElementById('search-results');
      if(!inp||!box) return;
      inp.addEventListener('input',function(){{
        const q=this.value.trim().toLowerCase();
        box.innerHTML='';
        if(!q||q.length<2) return;
        const hits=idx.filter(a=>(a.t||'').toLowerCase().includes(q)).slice(0,8);
        hits.forEach(a=>{{
          const el=document.createElement('a');
          el.href=a.u;
          el.innerHTML=`<img src="${{a.img||''}}" onerror="this.style.display='none'" loading="lazy"><span>${{a.t}}</span>`;
          box.appendChild(el);
        }});
      }});
      document.addEventListener('click',e=>{{if(!box.contains(e.target)&&e.target!==inp)box.innerHTML='';}});
    }}).catch(()=>{{}});
  }} catch(e) {{}}
  try {{
    if('serviceWorker' in navigator && location.protocol !== 'file:')
      navigator.serviceWorker.register('sw.js');
  }} catch(e) {{}}
</script>
</body></html>"""


def rebuild_category_pages() -> int:
    log_section(f"📂 Rebuild Category Pages [{LAYOUT_MODE} {COLS}col | {THEME_NAME}]")
    แก้แล้ว = 0
    บทความ  = สแกน_บทความ()
    หน้าที่ทำ = set()
    for หมวด in CATEGORIES:
        หน้า = CATEGORY_PAGE_MAP.get(หมวด, "news.html")
        if หน้า in หน้าที่ทำ: continue
        หน้าที่ทำ.add(หน้า)
        fp = BASE_PATH / หน้า
        if not fp.exists(): continue
        ไฟล์หมวด = [f for f in บทความ
                    if CATEGORY_PAGE_MAP.get(ชื่อหมวด(f), "news.html") == หน้า]
        ไฟล์หมวด.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if not ไฟล์หมวด:
            log_warn(f"  {หน้า} — ยังไม่มีบทความ ข้าม")
            continue
        # deduplicate
        seen = set()
        unique = []
        for f in ไฟล์หมวด:
            if f.stem not in seen:
                seen.add(f.stem); unique.append(f)
        ไฟล์หมวด = unique
        การ์ด     = _build_cards(ไฟล์หมวด[:24])
        art_block = _wrap_block(การ์ด, "บทความล่าสุด", len(ไฟล์หมวด))
        orig = fp.read_text(encoding="utf-8", errors="ignore")
        html = _สร้างหน้าหมวด_ครบ(หน้า, art_block)
        if เขียน(fp, html, orig):
            log_ok(f"  {หน้า} — {len(ไฟล์หมวด)} บทความ [{LAYOUT_MODE}]")
            แก้แล้ว += 1
        else:
            log_info(f"  {หน้า} — ไม่มีการเปลี่ยนแปลง")
    log_ok(f"rebuild category: {แก้แล้ว} หน้า")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 REBUILD INDEX PAGE
# ══════════════════════════════════════════════════════════════
def _สร้างหน้า_index_ครบ(art_block: str, count: int) -> str:
    lay      = _layout()
    th       = _theme()
    resp_css = lay["responsive"](COLS)
    resp_tag = f'<style>{resp_css}</style>' if resp_css else ""
    footer   = _build_footer_html()

    cat_pills = "".join(
        f'<a href="{CATEGORY_PAGE_MAP.get(c, c+".html")}" '
        f'style="display:inline-flex;align-items:center;gap:.35rem;'
        f'padding:.38rem .9rem;background:rgba(255,255,255,.15);color:#fff;'
        f'border-radius:999px;text-decoration:none;font-size:.82rem;font-weight:600;'
        f'transition:background .2s;" '
        f'onmouseover="this.style.background=\'rgba(255,255,255,.28)\'" '
        f'onmouseout="this.style.background=\'rgba(255,255,255,.15)\'">'
        f'<i class="fas fa-tag" style="font-size:.7rem;"></i> {หมวด_ไทย.get(c,c)}</a>'
        for c in CATEGORIES[:8]
    )
    hero = _build_hero_index(count, cat_pills)

    if LAYOUT_MODE in ("sidebar","featured","zigzag","row"):
        art_section = f"\n{IDX_S}\n{art_block}\n{IDX_E}\n"
    else:
        wrapper = lay["wrapper"](COLS)
        art_section = (
            f"\n{IDX_S}\n"
            f'{resp_tag}'
            f'<div class="art-grid" style="{wrapper};max-width:100%;">'
            f'\n{art_block}\n</div>'
            f"\n{IDX_E}\n"
        )

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{SITE_NAME} — ทุกเรื่องที่คุณอยากรู้</title>
  <meta name="description" content="{SITE_NAME} — แหล่งรวมบทความคุณภาพสูง อัปเดตทุกวัน">
  <meta property="og:title" content="{SITE_NAME}">
  <meta property="og:description" content="แหล่งรวมบทความคุณภาพสูง อัปเดตทุกวัน">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{SITE_URL}/images/og-default.png">
  <meta property="og:locale" content="th_TH">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{SITE_URL}/">
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="{th['primary']}">
  <link rel="apple-touch-icon" href="images/icon-192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="style.css">
  <style>
    :root{{--primary:{th['primary']};--dark:{th['dark']};--accent:{th['accent']};}}
    .page-main{{max-width:1140px;margin:0 auto;padding:1rem 1.25rem 2rem;}}
    .art-grid a:hover{{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.13);}}
  </style>
</head>
<body>
<script src="nav.js"></script>
<nav></nav>
{hero}
<div class="page-main">
  <h2 style="color:{th['primary']};font-size:1.1rem;margin:1.35rem 0 1rem;
             display:flex;align-items:center;gap:.5rem;">
    <i class="fas fa-fire" style="color:#ef4444;"></i> บทความล่าสุด
    <span style="font-size:.78rem;font-weight:400;color:var(--muted,#64748b);margin-left:.3rem;">
      ({count} บทความ)</span>
  </h2>
  {art_section}
</div>
{footer}
<script>
  // Search functionality
  (function(){{
    fetch('search-index.json').then(r=>r.json()).then(idx=>{{
      const inp = document.getElementById('search-input');
      const box = document.getElementById('search-results');
      if(!inp||!box) return;
      let timer;
      inp.addEventListener('input',function(){{
        clearTimeout(timer);
        timer = setTimeout(()=>{{
          const q = this.value.trim().toLowerCase();
          box.innerHTML = '';
          if(!q || q.length < 2) return;
          const hits = idx.filter(a =>
            (a.t||'').toLowerCase().includes(q) ||
            (a.cat||'').toLowerCase().includes(q)
          ).slice(0,10);
          hits.forEach(a=>{{
            const el = document.createElement('a');
            el.href = a.u;
            el.innerHTML = `<img src="${{a.img||''}}" loading="lazy"
              onerror="this.style.display='none'">
              <div><div style="font-weight:600;">${{a.t}}</div>
              <div style="font-size:.75rem;color:#94a3b8;">${{a.cat||''}}</div></div>`;
            box.appendChild(el);
          }});
          if(!hits.length) {{
            box.innerHTML = '<div style="padding:.75rem 1rem;color:#94a3b8;font-size:.85rem;">ไม่พบบทความ</div>';
          }}
        }}, 200);
      }});
      document.addEventListener('click', e=>{{
        if(!box.contains(e.target) && e.target !== inp) box.innerHTML = '';
      }});
    }}).catch(()=>{{}});
  }})();
  try {{
    if('serviceWorker' in navigator && location.protocol !== 'file:')
      navigator.serviceWorker.register('sw.js');
  }} catch(e) {{}}
</script>
</body></html>"""


def rebuild_index_page() -> int:
    log_section(f"🏠 Rebuild Index Page [{LAYOUT_MODE} {COLS}col | {THEME_NAME}]")
    fp   = BASE_PATH / "index.html"
    บทความ = สแกน_บทความ()
    บทความ.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    if not บทความ:
        log_warn("ไม่มีบทความ ข้าม")
        return 0

    # deduplicate
    seen, unique = set(), []
    for f in บทความ:
        if f.stem not in seen: seen.add(f.stem); unique.append(f)
    บทความ = unique

    การ์ด = _build_cards(บทความ[:30])

    if LAYOUT_MODE in ("sidebar","featured","zigzag","row"):
        art_block = การ์ด
    else:
        art_block = การ์ด

    orig = fp.read_text(encoding="utf-8", errors="ignore") if fp.exists() else ""
    html = _สร้างหน้า_index_ครบ(art_block, len(บทความ))
    if เขียน(fp, html, orig):
        log_ok(f"rebuild index: {len(บทความ)} บทความ [{LAYOUT_MODE}]")
        return 1
    log_info("index ไม่มีการเปลี่ยนแปลง")
    return 0


# ══════════════════════════════════════════════════════════════
# 🔧 SEARCH INDEX
# ══════════════════════════════════════════════════════════════
def rebuild_search_index() -> int:
    log_section("🔍 Rebuild Search Index")
    บทความ = สแกน_บทความ()
    entries = []
    for fp in บทความ:
        try:
            soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            t    = ดึงหัวข้อ(soup, fp)
            img  = ดึงรูปหลัก(soup, fp) or _picsum(fp.stem)
            cat  = หมวด_ไทย.get(ชื่อหมวด(fp), ชื่อหมวด(fp))
            entries.append({"t": t, "u": fp.name, "img": img, "cat": cat})
        except Exception: pass
    out = BASE_PATH / "search-index.json"
    if not DRY_RUN:
        out.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    log_ok(f"search index: {len(entries)} รายการ")
    return len(entries)


# ══════════════════════════════════════════════════════════════
# 🔧 SITEMAP
# ══════════════════════════════════════════════════════════════
def สร้าง_sitemap() -> int:
    log_section("🗺️  Sitemap")
    บทความ = สแกน_html()
    now    = datetime.datetime.now().strftime("%Y-%m-%d")
    urls   = []
    for fp in บทความ:
        pri = "1.0" if fp.name == "index.html" else ("0.8" if fp.name in _CAT_FILES else "0.6")
        urls.append(f'  <url><loc>{SITE_URL}/{fp.name}</loc><lastmod>{now}</lastmod>'
                    f'<changefreq>daily</changefreq><priority>{pri}</priority></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(urls) + "\n</urlset>")
    out = BASE_PATH / "sitemap.xml"
    if not DRY_RUN:
        out.write_text(xml, encoding="utf-8")
    log_ok(f"sitemap: {len(urls)} URLs")
    return len(urls)


# ══════════════════════════════════════════════════════════════
# 🔧 PUSH GITHUB
# ══════════════════════════════════════════════════════════════
def push_github():
    log_section("🚀 Push GitHub")
    try:
        subprocess.run(["git","-C",str(BASE_PATH),"add","-A"], check=True)
        msg = f"fix: v5 rebuild {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} [{LAYOUT_MODE}|{THEME_NAME}]"
        subprocess.run(["git","-C",str(BASE_PATH),"commit","-m",msg], check=True)
        subprocess.run(["git","-C",str(BASE_PATH),"push"], check=True)
        log_ok("Push สำเร็จ")
    except subprocess.CalledProcessError as e:
        log_err(f"Push ล้มเหลว: {e}")


# ══════════════════════════════════════════════════════════════
# 🔧 SIDEBAR SUPPORT
# ══════════════════════════════════════════════════════════════
def แก้_support_sidebar() -> int:
    try:
        from config import สร้าง_sidebar_html as _sidebar_fn
    except ImportError:
        log_warn("ไม่พบ สร้าง_sidebar_html ใน config")
        return 0
    log_section("💛 ใส่ Sidebar สนับสนุนเรา")
    แก้แล้ว = 0
    sidebar_content = _sidebar_fn()
    import re as _re
    inner_m = _re.search(r'<aside[^>]*>(.*?)</aside>', sidebar_content, _re.DOTALL)
    sidebar_inner = inner_m.group(1).strip() if inner_m else sidebar_content
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if '<aside' not in orig: continue
            if 'สนับสนุนเรา' in orig: continue
            def _inject(m):
                tag_open  = m.group(1)
                tag_close = m.group(3)
                content   = m.group(2).strip()
                if content: return f"{tag_open}\n{content}\n{sidebar_inner}\n{tag_close}"
                return f"{tag_open}\n{sidebar_inner}\n{tag_close}"
            new_html = _re.sub(
                r'(<aside[^>]*class=["\'][^"\']*sidebar[^"\']*["\'][^>]*>)(.*?)(</aside>)',
                _inject, orig, flags=_re.DOTALL)
            if new_html != orig and เขียน(fp, new_html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  sidebar {fp.name}: {e}")
    log_ok(f"ใส่ sidebar: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔁 DEDUP
# ══════════════════════════════════════════════════════════════
def แก้_duplicate_blocks_hard() -> int:
    log_section("🗑️  Hard Dedup")
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            for _s, _e in [(ART_S, ART_E),
                           ("<!-- article-list -->","<!-- /article-list -->"),
                           (IDX_S, IDX_E)]:
                html = wipe_all_blocks(html, _s, _e)
            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  dedup {fp.name}: {e}")
    log_ok(f"dedup: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 💬 CHAT MODE
# ══════════════════════════════════════════════════════════════
def รัน_chat():
    log_section("💬 Chat Mode — WebBot v5")
    sys_p = (f"คุณคือ WebBot ผู้ช่วยดูแลเว็บไซต์ {SITE_NAME} "
             f"ตอบภาษาไทยสั้นกระชับ ใช้คำสั่ง /fix /audit /publish /status")
    history = []
    while True:
        try:
            user = input("\nคุณ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nออกจาก chat"); break
        if not user: continue
        if user.lower() in ("/exit","ออก","quit"): break
        if user.lower() in ("/fix","ซ่อม","fix"):   รัน_fix_ทั้งหมด(); continue
        if user.lower() in ("/audit","ตรวจ"):       audit_ทั้งหมด(); continue
        if user.lower() in ("/stats","สถิติ"):      แสดง_สถิติ(); continue
        if user.lower() in ("/publish","push"):
            สร้าง_sitemap(); rebuild_search_index(); push_github(); continue
        history.append({"role":"user","content":user})
        msgs = [f"{'ผู้ใช้' if m['role']=='user' else 'WebBot'}: {m['content']}"
                for m in history[-10:]]
        prompt = sys_p + "\n\n" + "\n".join(msgs) + "\nWebBot:"
        print("WebBot: ", end="", flush=True)
        res = เรียก_ollama(prompt, num_predict=600, timeout=60)
        if res:
            res = re.sub(r'^(WebBot\s*:\s*)', '', res.strip())
            print(res)
            history.append({"role":"assistant","content":res})
        else:
            print("(ไม่ได้คำตอบ — ลองใหม่ หรือตรวจ: ollama serve)")


# ══════════════════════════════════════════════════════════════
# 🚀 รัน_fix_ทั้งหมด
# ══════════════════════════════════════════════════════════════
def รัน_fix_ทั้งหมด():
    log_section(f"🛠️  Fix v5 — Layout: {LAYOUT_MODE} | Cols: {COLS} | Theme: {THEME_NAME}")
    log(f"📁 {BASE_PATH}")
    if DRY_RUN: log_warn("DRY-RUN mode")

    audit_ทั้งหมด()

    steps = [
        ("แก้ nav bar",             แก้_nav),
        ("แก้ dead/empty links",    แก้_dead_links),
        ("แก้รูปภาพ + onerror",     แก้_รูปภาพ),
        ("แก้ SVG emoji",           แก้_svg_emoji),
        ("แก้ h1",                  แก้_h1),
        ("แก้เนื้อหาว่าง",          แก้_เนื้อหาว่าง),
        ("rebuild category pages", rebuild_category_pages),
        ("rebuild index page",     rebuild_index_page),
        # ✅ v5 ใหม่: แก้ footer+hero สีทุกหน้าหลังจาก rebuild
        ("แก้ footer สี",           แก้_footer_ทุกหน้า),
        ("ใส่ sidebar สนับสนุนเรา", แก้_support_sidebar),
        ("related articles",       แก้_related_articles),
        ("rebuild search index",   rebuild_search_index),
        ("sitemap",                สร้าง_sitemap),
    ]

    results = {}
    for ชื่อ, fn in steps:
        log_section(f"▶ {ชื่อ}")
        try:
            results[ชื่อ] = fn()
        except Exception as e:
            log_err(f"  ERROR: {e}")
            results[ชื่อ] = "ERROR"

    log_section("📋 Audit หลังซ่อม")
    audit_ทั้งหมด()

    log_section("✅ สรุปผล")
    for k, v in results.items():
        icon = "✅" if str(v) != "ERROR" else "❌"
        log(f"  {icon} {k}: {v}")


# ══════════════════════════════════════════════════════════════
# 🚀 MAIN
# ══════════════════════════════════════════════════════════════
def main():
    args = set(_args)

    if "--chat"          in args: รัน_chat(); return
    if "--audit"         in args: audit_ทั้งหมด(); return
    if "--stats"         in args: แสดง_สถิติ(); return
    if "--check-overlap" in args:
        log_section("🔁 ตรวจการทำงานซ้ำ — v5")
        log("  ลำดับ: agent_writer → agent_fix_v5 → agent_fix_v5 --publish")
        return
    if "--dedup" in args:
        แก้_duplicate_blocks_hard()
        rebuild_category_pages()
        rebuild_index_page()
        return
    if "--fix-css"    in args: rebuild_style_css(); return
    if "--fix-footer" in args: แก้_footer_ทุกหน้า(); return
    if "--fix-hero"   in args: แก้_hero_ทุกหน้า(); return
    if "--publish"    in args:
        สร้าง_sitemap(); rebuild_search_index(); push_github(); return
    if "--dry-run" in args:
        import config as _cfg; _cfg.DRY_RUN = True
        รัน_fix_ทั้งหมด(); return
    if "--fix" in args:
        รัน_fix_ทั้งหมด()
        log_section("✅ Fix เสร็จ — รัน --publish เพื่อ push")
        return

    # DEFAULT
    รัน_fix_ทั้งหมด()
    if not DRY_RUN:
        try:
            ans = input("\nPush ขึ้น GitHub เลยไหม? (Enter=ใช่ / n=ไม่): ").strip().lower()
            if ans not in ("n","no","ไม่"): push_github()
        except (EOFError, KeyboardInterrupt):
            log_info("รัน --publish เพื่อ push")


if __name__ == "__main__":
    main()
