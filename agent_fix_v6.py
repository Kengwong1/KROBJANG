"""
╔══════════════════════════════════════════════════════════════════════╗
║  agent_fix_v6.py  — Full Layout + Theme + Auto-Create Edition       ║
║                                                                      ║
║  python agent_fix_v6.py                → ซ่อมทุกส่วน + push         ║
║  python agent_fix_v6.py --fix          → ซ่อมอย่างเดียว             ║
║  python agent_fix_v6.py --audit        → ตรวจอย่างเดียว             ║
║  python agent_fix_v6.py --publish      → sitemap + push              ║
║  python agent_fix_v6.py --dry-run      → ดูอย่างเดียว               ║
║  python agent_fix_v6.py --dedup        → ลบซ้ำ + rebuild             ║
║  python agent_fix_v6.py --chat         → คุยกับ AI โดยตรง            ║
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
║  python agent_fix_v6.py --layout hero3 --cols 3                     ║
║  python agent_fix_v6.py --layout tiles --cols 4                     ║
║  python agent_fix_v6.py --layout compact6 --cols 6                  ║
║  python agent_fix_v6.py --layout zigzag                             ║
║  python agent_fix_v6.py --layout featured --cols 3                  ║
║                                                                      ║
║  Theme (--theme) — 40 ธีม:                                          ║
║  พื้นฐาน: blue dark green red purple orange teal slate rose         ║
║            indigo amber cyan lime sky violet                         ║
║  มืออาชีพ: reliable corporate charcoal                              ║
║  เรียบง่าย: minimal calm zen paper                                  ║
║  หวานน่ารัก: sweet candy sakura lavender peach                      ║
║  ธรรมมะ: dharma monk lotus gold                                     ║
║  ดูดวง/ลึกลับ: mystic horoscope cosmic midnight                     ║
║  ธรรมชาติ: forest ocean earth spring                                ║
║  วินเทจ: retro vintage neon                                         ║
║  python agent_fix_v6.py --theme dharma --layout grid               ║
║  python agent_fix_v6.py --theme mystic --layout tiles              ║
║  python agent_fix_v6.py --list-themes  → แสดงธีมทั้งหมด            ║
║                                                                      ║
║  Extra:                                                              ║
║  python agent_fix_v6.py --check-overlap → ตรวจซ้ำ                  ║
║  python agent_fix_v6.py --fix-css       → rebuild style.css         ║
║  python agent_fix_v6.py --fix-footer    → แก้ footer ทุกหน้า        ║
║  python agent_fix_v6.py --fix-hero      → แก้ hero ทุกหน้า          ║
║  python agent_fix_v6.py --fix-search    → แก้ช่องค้นหา              ║
║  python agent_fix_v6.py --fix-meta      → แก้ meta description      ║
║  python agent_fix_v6.py --fix-404       → สร้างหน้า 404 สวย         ║
║  python agent_fix_v6.py --fix-alt       → เติม img alt SEO           ║
║  python agent_fix_v6.py --check-dup     → ตรวจเนื้อหาซ้ำ            ║
║  python agent_fix_v6.py --stats         → สถิติเว็บไซต์             ║
║  python agent_fix_v6.py --create-cats   → สร้างหน้าหมวดที่หายไป     ║ ← [NEW v6]
║  python agent_fix_v6.py --fix-nav       → rebuild nav.js ครบทุกหมวด ║ ← [NEW v6]
║  python agent_fix_v6.py --breadcrumb    → เพิ่ม breadcrumb ทุกหน้า  ║ ← [NEW v6]
║  python agent_fix_v6.py --fix-og        → แก้ og:image ทุกบทความ    ║ ← [NEW v6]
║  python agent_fix_v6.py --reading-time  → เพิ่มเวลาอ่านบทความ       ║ ← [NEW v6]
║  python agent_fix_v6.py --robots        → สร้าง robots.txt          ║ ← [NEW v6]
╚══════════════════════════════════════════════════════════════════════╝

แก้จาก v5:
  ✅ [BUG-FIX] rebuild_category_pages() → ไม่ข้ามถ้าไม่มีไฟล์ → สร้างใหม่ทันที
  ✅ [BUG-FIX] nav ทุกหน้าแสดงหมวดหมู่ครบ 26 หมวด (rebuild nav.js อัตโนมัติ)
  ✅ [BUG-FIX] _CAT_TITLE ครบทุกหมวดที่อยู่ใน CATEGORIES (ไม่มีแสดง stem แล้ว)
  ✅ [NEW] --create-cats → สร้างหน้าหมวดที่หายไปทั้งหมดทันที
  ✅ [NEW] --fix-nav → rebuild nav.js ใหม่ให้ครบทุกหมวดหมู่
  ✅ [NEW] --breadcrumb → เพิ่ม breadcrumb navigation ทุกหน้าบทความ
  ✅ [NEW] --fix-og → เติม og:image ทุกบทความที่ยังขาดอยู่
  ✅ [NEW] --reading-time → คำนวณ + แสดงเวลาอ่านโดยประมาณ
  ✅ [NEW] --robots → สร้าง robots.txt ที่ถูกต้อง
  ✅ [NEW] หน้าหมวด tag pills ครบทุกหมวดหมู่เหมือนหน้าแรก
  ✅ [NEW] สร้าง nav.js อัตโนมัติถ้ายังไม่มี
  ✅ [IMPROVED] สถิติแสดงจำนวนหน้าหมวดที่หายไปด้วย
  ✅ [IMPROVED] log แสดงรายการหมวดที่ถูกสร้างใหม่ชัดเจน
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
_INDEX_FILES  = {"/","404.html","contact.html","sitemap.html","privacy.html"}
_CAT_FILES    = set(CATEGORY_PAGE_MAP.values())   # ✅ v6: ดึงจาก config ตรงๆ ไม่ hard-code
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
# 🎨  THEME SYSTEM — 40 ธีม
# format: (primary, dark, grad_end, accent, badge_txt)
# ══════════════════════════════════════════════════════════════
THEME_DEFS = {
    # ── ธีมพื้นฐาน (เดิม) ──────────────────────────────────────
    "blue":     ("#1e40af", "#0f172a", "#1e3a8a", "#3b82f6", "#fff"),
    "dark":     ("#0f172a", "#020617", "#1e293b", "#475569", "#e2e8f0"),
    "green":    ("#065f46", "#022c22", "#047857", "#10b981", "#fff"),
    "red":      ("#991b1b", "#450a0a", "#b91c1c", "#ef4444", "#fff"),
    "purple":   ("#581c87", "#2e1065", "#6b21a8", "#a855f7", "#fff"),
    "orange":   ("#9a3412", "#431407", "#c2410c", "#f97316", "#fff"),
    "teal":     ("#0f766e", "#042f2e", "#0d9488", "#14b8a6", "#fff"),
    "slate":    ("#334155", "#0f172a", "#475569", "#64748b", "#f8fafc"),
    "rose":     ("#9f1239", "#4c0519", "#be123c", "#fb7185", "#fff"),
    "indigo":   ("#3730a3", "#1e1b4b", "#4338ca", "#818cf8", "#fff"),
    "amber":    ("#92400e", "#451a03", "#b45309", "#fbbf24", "#fff"),
    "cyan":     ("#155e75", "#083344", "#0e7490", "#22d3ee", "#fff"),
    "lime":     ("#3f6212", "#1a2e05", "#4d7c0f", "#a3e635", "#1a2e05"),
    "sky":      ("#075985", "#082f49", "#0369a1", "#38bdf8", "#fff"),
    "violet":   ("#4c1d95", "#2e1065", "#5b21b6", "#c084fc", "#fff"),

    # ── น่าเชื่อถือ / มืออาชีพ ───────────────────────────────────
    "reliable": ("#1a365d", "#0d1f3c", "#2a4a7f", "#4299e1", "#fff"),   # navy น่าเชื่อถือ
    "corporate":("#1e3a5f", "#0f2340", "#2d5a9e", "#63b3ed", "#fff"),   # บริษัท เป็นทางการ
    "charcoal": ("#374151", "#111827", "#4b5563", "#9ca3af", "#fff"),   # ถ่าน โมเดิร์น

    # ── เรียบง่าย / สบายตา ──────────────────────────────────────
    "minimal":  ("#334155", "#1e293b", "#475569", "#94a3b8", "#fff"),   # minimal สะอาด
    "calm":     ("#2d6a7a", "#0f3642", "#3d8fa3", "#67c8d8", "#fff"),   # สบายตา ฟ้าเทา
    "zen":      ("#4a7c59", "#1a3328", "#5a9c6e", "#88d4a8", "#fff"),   # เขียวอ่อน ผ่อนคลาย
    "paper":    ("#5c4a32", "#2c2218", "#7a6248", "#c8a97a", "#fff"),   # น้ำตาลกระดาษ อบอุ่น

    # ── หวาน / น่ารัก ───────────────────────────────────────────
    "sweet":    ("#be185d", "#6b0f3a", "#db2777", "#f9a8d4", "#fff"),   # ชมพูหวาน
    "candy":    ("#9d174d", "#5a0f2e", "#c2185b", "#f48fb1", "#fff"),   # ลูกอม
    "sakura":   ("#ad1457", "#4a0726", "#c2185b", "#f8bbd0", "#fff"),   # ซากุระ ญี่ปุ่น
    "lavender": ("#5b21b6", "#2e1065", "#7c3aed", "#ddd6fe", "#fff"),   # ลาเวนเดอร์
    "peach":    ("#c2410c", "#7c2d12", "#ea580c", "#fdba74", "#fff"),   # พีช ส้มอ่อน

    # ── ธรรมมะ / จิตใจ ──────────────────────────────────────────
    "dharma":   ("#92400e", "#3b1a06", "#b45309", "#fcd34d", "#fff"),   # ทองธรรมะ วัด
    "monk":     ("#c05621", "#7b341e", "#dd6b20", "#f6ad55", "#fff"),   # สีจีวร พระ
    "lotus":    ("#702459", "#4a044e", "#9b2c8c", "#d6a8e0", "#fff"),   # บัว ม่วงเข้ม
    "gold":     ("#78350f", "#3b1a03", "#92400e", "#fbbf24", "#fff"),   # ทองคำ มงคล

    # ── ดูดวง / ลึกลับ ──────────────────────────────────────────
    "mystic":   ("#1e1b4b", "#0f0c2e", "#312e81", "#818cf8", "#e0e7ff"), # ลึกลับ จักรวาล
    "horoscope":("#4c1d95", "#1e0a3c", "#5b21b6", "#a78bfa", "#fff"),   # ดูดวง ม่วง
    "cosmic":   ("#0f172a", "#020617", "#1e1b4b", "#6366f1", "#c7d2fe"), # จักรวาล ดาว
    "midnight": ("#1e3a8a", "#0a0f2e", "#1e40af", "#60a5fa", "#dbeafe"), # เที่ยงคืน navy

    # ── ธรรมชาติ / ป่า / ทะเล ────────────────────────────────────
    "forest":   ("#14532d", "#052e16", "#166534", "#4ade80", "#fff"),   # ป่าเขา
    "ocean":    ("#075985", "#0c1a35", "#0369a1", "#38bdf8", "#fff"),   # ทะเลลึก
    "earth":    ("#713f12", "#3b1f07", "#92400e", "#d97706", "#fff"),   # ดินแดน
    "spring":   ("#15803d", "#052e16", "#16a34a", "#86efac", "#fff"),   # ฤดูใบไม้ผลิ

    # ── Retro / วินเทจ ──────────────────────────────────────────
    "retro":    ("#7c3aed", "#1e0a3c", "#6d28d9", "#c4b5fd", "#fff"),   # retro ม่วง
    "vintage":  ("#92400e", "#3b1a06", "#a16207", "#fde68a", "#1a0e00"), # วินเทจ ซีเปีย
    "neon":     ("#0f172a", "#020617", "#1e293b", "#22d3ee", "#fff"),   # นีออน dark
}

# คำอธิบายธีม (ใช้ใน --list-themes)
THEME_LABELS = {
    "blue":      "น้ำเงิน (default) — เว็บทั่วไป",
    "dark":      "Dark Mode — โมเดิร์น",
    "green":     "เขียวเข้ม — สุขภาพ ธรรมชาติ",
    "red":       "แดง — ข่าว บันเทิง",
    "purple":    "ม่วง — สร้างสรรค์",
    "orange":    "ส้ม — อาหาร ท่องเที่ยว",
    "teal":      "เขียวน้ำ — เทคโนโลยี",
    "slate":     "เทา — เรียบ มินิมอล",
    "rose":      "กุหลาบ — ความงาม",
    "indigo":    "คราม — การเงิน",
    "amber":     "อำพัน — อบอุ่น",
    "cyan":      "ฟ้าน้ำ — สดใส",
    "lime":      "เขียวสด — พลังงาน",
    "sky":       "ท้องฟ้า — สดชื่น",
    "violet":    "ไวโอเล็ต — สร้างสรรค์",
    "reliable":  "🏛️  Navy น่าเชื่อถือ — ข่าว รัฐ บริษัท",
    "corporate": "💼 Corporate — เป็นทางการ มืออาชีพ",
    "charcoal":  "🪨 Charcoal — โมเดิร์น เรียบ",
    "minimal":   "✨ Minimal — สะอาด เรียบง่าย",
    "calm":      "🌊 Calm — สบายตา ฟ้าเทา",
    "zen":       "🍃 Zen — ผ่อนคลาย เขียวอ่อน",
    "paper":     "📄 Paper — อบอุ่น กระดาษน้ำตาล",
    "sweet":     "🍭 Sweet — หวาน ชมพู น่ารัก",
    "candy":     "🍬 Candy — ลูกอม สดใส",
    "sakura":    "🌸 Sakura — ซากุระ ญี่ปุ่น",
    "lavender":  "💜 Lavender — ลาเวนเดอร์ นุ่มนวล",
    "peach":     "🍑 Peach — พีช ส้มอ่อน",
    "dharma":    "🙏 Dharma — ธรรมมะ ทองวัด",
    "monk":      "🟠 Monk — จีวร พระ พุทธศาสนา",
    "lotus":     "🪷 Lotus — บัว จิตใจ สมาธิ",
    "gold":      "✨ Gold — ทองคำ มงคล ความสำเร็จ",
    "mystic":    "🔮 Mystic — ลึกลับ จักรวาล",
    "horoscope": "⭐ Horoscope — ดูดวง โหราศาสตร์",
    "cosmic":    "🌌 Cosmic — ดาว อวกาศ",
    "midnight":  "🌙 Midnight — เที่ยงคืน navy dark",
    "forest":    "🌲 Forest — ป่า ธรรมชาติ",
    "ocean":     "🌊 Ocean — ทะเลลึก สีฟ้า",
    "earth":     "🌍 Earth — ดิน อบอุ่น",
    "spring":    "🌱 Spring — ฤดูใบไม้ผลิ สดใส",
    "retro":     "📺 Retro — วินเทจ ม่วง",
    "vintage":   "🕰️  Vintage — ซีเปีย คลาสสิก",
    "neon":      "💡 Neon — นีออน dark สว่าง",
}

def _theme() -> dict:
    t = THEME_DEFS.get(THEME_NAME, THEME_DEFS["blue"])
    return {"primary": t[0], "dark": t[1], "grad_end": t[2], "accent": t[3], "badge_txt": t[4]}

def _hero_gradient() -> str:
    t = _theme()
    return f"linear-gradient(135deg,{t['primary']},{t['dark']})"

def _footer_bg() -> str:
    return _theme()["dark"]

def _footer_gradient() -> str:
    t = _theme()
    return f"linear-gradient(135deg,{t['dark']},{t['primary']})"

# ══════════════════════════════════════════════════════════════
# 📐  LAYOUT SYSTEM — 13 แบบ
# ══════════════════════════════════════════════════════════════
LAYOUT_DEFS = {
    "grid": {
        "label": "Grid — การ์ดตาราง",
        "img_h": "200px",
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
    "list": {
        "label": "List — รูปซ้าย ข้อความขวา",
        "img_h": "90px",
        "img_w": "140px",
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
    "magazine": {
        "label": "Magazine — featured + grid",
        "img_h": "220px",
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
    "compact": {
        "label": "Compact — กริด 4 คอลัมน์",
        "img_h": "140px",
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
    "compact5": {
        "label": "Compact5 — กริด 5 คอลัมน์",
        "img_h": "120px",
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
    "compact6": {
        "label": "Compact6 — กริด 6 คอลัมน์",
        "img_h": "100px",
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
    "hero3": {
        "label": "Hero3 — 3 การ์ดใหญ่แบบเว็บข่าว",
        "img_h": "260px",
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
    "sidebar": {
        "label": "Sidebar — ใหญ่ซ้าย + list ขวา",
        "img_h": "200px",
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
    "tiles": {
        "label": "Tiles — รูปเต็ม title ทับล่าง",
        "img_h": "240px",
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
    "masonry": {
        "label": "Masonry — สูงไม่เท่ากัน",
        "img_h": "auto",
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
    "zigzag": {
        "label": "Zigzag — รูปสลับซ้าย-ขวา",
        "img_h": "220px",
        "img_w": "45%",
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
    "featured": {
        "label": "Featured — 1 ใหญ่บน + grid ล่าง",
        "img_h": "320px",
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
    "row": {
        "label": "Row — แนวนอน scroll",
        "img_h": "180px",
        "card_w": "260px",
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
    color = CAT_COLORS.get(หมวด, "#6366f1")
    label = หมวด_ไทย.get(หมวด, หมวด)
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

    # ── sidebar ──────────────────────────────────────────────
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

    # ── featured ─────────────────────────────────────────────
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

    # ── zigzag ───────────────────────────────────────────────
    if LAYOUT_MODE == "zigzag":
        cards = ""
        for i, af in enumerate(ไฟล์บทความ):
            d   = _parse_article(af)
            oe  = _fallback_img(af.stem).replace('"','&quot;')
            badge = _badge_html(d["หมวด"])
            row_dir = "row" if i % 2 == 0 else "row-reverse"
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

    # ── row ──────────────────────────────────────────────────
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

    # ── ทุก layout อื่น ───────────────────────────────────────
    การ์ด = ""
    for af in ไฟล์บทความ:
        d   = _parse_article(af)
        oe  = _fallback_img(af.stem).replace('"','&quot;')
        badge = _badge_html(d["หมวด"])
        วันที่_html = (f'<p style="font-size:.72rem;color:#94a3b8;margin:0 0 .3rem;">'
                      f'<i class="fas fa-clock"></i> {d["วันที่"]}</p>' if d["วันที่"] else "")
        excerpt_part = (f'<p style="font-size:.81rem;color:#64748b;margin:.3rem 0 0;'
                        f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">'
                        f'{d["excerpt"]}</p>' if d["excerpt"] and LAYOUT_MODE not in ("compact","compact5","compact6") else "")
        if LAYOUT_MODE == "list":
            oe_esc = oe.replace('"','&quot;')
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe_esc}"'
                f' style="width:{lay.get("img_w","140px")};height:{img_h};object-fit:cover;'
                f'border-radius:8px;flex-shrink:0;">'
                f'<div style="padding:.9rem;flex:1;display:flex;flex-direction:column;">'
                f'{badge}'
                f'{วันที่_html}'
                f'<h3 style="font-size:.92rem;font-weight:700;margin:0;line-height:1.45;flex:1;'
                f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{d["หัวข้อ"]}</h3>'
                f'{excerpt_part}'
                f'</div></a>'
            )
        elif LAYOUT_MODE == "tiles":
            seed_c = CAT_COLORS.get(d["หมวด"], "#1e40af")
            การ์ด += (
                f'<a href="{af.name}" style="{lay["card_css"]}"{hover}>'
                f'<img src="{d["img"]}" alt="{d["หัวข้อ"]}" loading="lazy" onerror="{oe}"'
                f' style="width:100%;height:{img_h};object-fit:cover;display:block;">'
                f'<div style="position:absolute;bottom:0;left:0;right:0;'
                f'background:linear-gradient(transparent,rgba(0,0,0,.78));padding:.75rem .9rem .85rem;">'
                f'{badge}'
                f'<h3 style="font-size:.9rem;font-weight:700;line-height:1.35;color:#fff;margin:0;">{d["หัวข้อ"]}</h3>'
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
                f'{excerpt_part}'
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

    # ✅ v6: ตรวจหน้าหมวดที่ยังไม่มีไฟล์
    หน้าหมวดหาย = []
    for cat, page in CATEGORY_PAGE_MAP.items():
        fp = BASE_PATH / page
        if not fp.exists():
            หน้าหมวดหาย.append(page)
    if หน้าหมวดหาย:
        log_warn(f"⚠️  หน้าหมวดที่ยังไม่มีไฟล์ ({len(หน้าหมวดหาย)} หน้า):")
        for p in หน้าหมวดหาย:
            log(f"     ❌ {p}")
        log_warn("   → รัน: python agent_fix_v6.py --create-cats  เพื่อสร้างทั้งหมด")

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
        "หน้าหมวดไม่มีไฟล์":    หน้าหมวดหาย,
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
        if fp.name not in (_CAT_FILES | {"/"}): continue
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if txt.count(ART_S) > 1:        ปัญหา["block ซ้ำ"].append(f"{fp.name} ({txt.count(ART_S)}x)")
            if fp.name in _CAT_FILES and ART_S not in txt:
                ปัญหา["หน้าหมวดไม่มี block"].append(fp.name)
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
# 📊 STATS
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
    log(f"  📁 หมวดหมู่ที่มีบทความ: {len(by_cat)} หมวด")

    # ✅ v6: แสดงหมวดที่ยังไม่มีไฟล์ HTML
    หน้าหาย = [(c, CATEGORY_PAGE_MAP[c]) for c in CATEGORIES
                if not (BASE_PATH / CATEGORY_PAGE_MAP.get(c, c+".html")).exists()]
    if หน้าหาย:
        log(f"\n  ❌ หน้าหมวดที่ยังไม่มีไฟล์ ({len(หน้าหาย)} หน้า):")
        for c, p in หน้าหาย:
            log(f"     • {p}  ({หมวด_ไทย.get(c,c)})")
        log(f"  → รัน --create-cats เพื่อสร้าง")

    log(f"")
    for cat, fps in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        th_name = หมวด_ไทย.get(cat, cat)
        avg_sz  = sum(f.stat().st_size for f in fps) / len(fps) / 1024
        log(f"  {'▪' if len(fps) >= 5 else '·'} {th_name:<14} {len(fps):>4} บทความ  avg {avg_sz:.1f} KB")

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
    # ✅ v6: สร้าง nav.js ก่อนถ้ายังไม่มี
    สร้าง_nav_js()
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
# 🔧 [NEW v6] สร้าง nav.js อัตโนมัติ ครบทุกหมวด
# ══════════════════════════════════════════════════════════════
def สร้าง_nav_js() -> int:
    log_section("🧭 Rebuild nav.js — ครบทุกหมวด")
    th = _theme()

    # สร้าง nav items จาก CATEGORY_PAGE_MAP ครบทุกหมวด
    nav_items = []
    # หมวดหลักที่แสดงใน navbar
    main_cats = ['news', 'lifestyle', 'health', 'food', 'finance', 'technology', 'entertainment', 'travel']
    # หมวดที่เหลือใส่ใน dropdown "เพิ่มเติม"
    extra_cats = [c for c in CATEGORIES if c not in main_cats]

    main_links = ""
    for cat in main_cats:
        page  = CATEGORY_PAGE_MAP.get(cat, cat + ".html")
        label = หมวด_ไทย.get(cat, cat)
        main_links += f'    {{ label: "{label}", href: "{page}" }},\n'

    extra_links = ""
    for cat in extra_cats:
        page  = CATEGORY_PAGE_MAP.get(cat, cat + ".html")
        label = หมวด_ไทย.get(cat, cat)
        extra_links += f'    {{ label: "{label}", href: "{page}" }},\n'

    js = f"""// nav.js — ไอหมอก v6 — auto-generated {datetime.datetime.now().strftime("%Y-%m-%d")}
// ✅ ครบทุกหมวด {len(CATEGORIES)} หมวด
(function() {{
  var SITE_NAME = "{SITE_NAME}";
  var PRIMARY   = "{th['primary']}";
  var DARK      = "{th['dark']}";

  var MAIN_CATS = [
{main_links}  ];

  var EXTRA_CATS = [
{extra_links}  ];

  function renderNav() {{
    var nav = document.querySelector('nav');
    if (!nav) return;

    var currentPage = location.pathname.split('/').pop() || '/';

    // สร้าง main links
    var mainHTML = MAIN_CATS.map(function(item) {{
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="color:#fff;text-decoration:none;'
        + 'padding:.4rem .65rem;border-radius:6px;font-size:.88rem;font-weight:600;white-space:nowrap;'
        + (active ? 'background:rgba(255,255,255,.22);' : 'opacity:.88;')
        + 'transition:background .18s;" '
        + 'onmouseover="this.style.background=\'rgba(255,255,255,.18)\'" '
        + 'onmouseout="this.style.background=\'' + (active ? 'rgba(255,255,255,.22)' : '') + '\'">'
        + item.label + '</a>';
    }}).join('');

    // สร้าง dropdown "เพิ่มเติม"
    var dropHTML = EXTRA_CATS.map(function(item) {{
      var active = currentPage === item.href;
      return '<a href="' + item.href + '" style="display:block;padding:.45rem .85rem;'
        + 'color:#1e293b;text-decoration:none;font-size:.85rem;font-weight:' + (active ? '700' : '500') + ';'
        + 'background:' + (active ? '#e0f2fe' : 'transparent') + ';'
        + 'transition:background .15s;" '
        + 'onmouseover="this.style.background=\'#f1f5f9\'" '
        + 'onmouseout="this.style.background=\'' + (active ? '#e0f2fe' : 'transparent') + '\'">'
        + item.label + '</a>';
    }}).join('');

    nav.style.cssText = 'position:sticky;top:0;z-index:999;background:' + PRIMARY
      + ';box-shadow:0 2px 10px rgba(0,0,0,.22);font-family:Sarabun,sans-serif;';

    nav.innerHTML = [
      '<div style="max-width:1140px;margin:0 auto;padding:0 1rem;display:flex;align-items:center;gap:.25rem;height:52px;">',
      // Logo
      '<a href="/" style="color:#fff;text-decoration:none;font-size:1.15rem;font-weight:800;',
      'letter-spacing:.02em;margin-right:.75rem;flex-shrink:0;white-space:nowrap;">' + SITE_NAME + '</a>',
      // Main links (desktop)
      '<div class="nav-main" style="display:flex;align-items:center;gap:.15rem;flex:1;overflow:hidden;flex-wrap:nowrap;">',
      mainHTML,
      '</div>',
      // Dropdown เพิ่มเติม
      '<div class="nav-more" style="position:relative;flex-shrink:0;">',
      '<button id="nav-more-btn" style="background:rgba(255,255,255,.15);border:none;color:#fff;',
      'padding:.38rem .75rem;border-radius:6px;cursor:pointer;font-family:inherit;font-size:.85rem;',
      'font-weight:600;display:flex;align-items:center;gap:.35rem;" ',
      'onclick="(function(){{var d=document.getElementById(\'nav-more-drop\');',
      'd.style.display=d.style.display===\'block\'?\'none\':\'block\';}})()" >',
      'เพิ่มเติม <span style="font-size:.65rem;">▼</span></button>',
      '<div id="nav-more-drop" style="display:none;position:absolute;top:calc(100% + 6px);right:0;',
      'background:#fff;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.18);',
      'min-width:160px;max-height:70vh;overflow-y:auto;z-index:9999;padding:.35rem 0;">',
      dropHTML,
      '</div></div>',
      // Hamburger (mobile)
      '<button id="nav-ham" style="display:none;background:none;border:none;color:#fff;',
      'font-size:1.3rem;cursor:pointer;padding:.3rem .5rem;margin-left:.5rem;" ',
      'onclick="(function(){{var m=document.getElementById(\'nav-mobile\');',
      'm.style.display=m.style.display===\'flex\'?\'none\':\'flex\';}})()" >☰</button>',
      '</div>',
      // Mobile menu
      '<div id="nav-mobile" style="display:none;flex-direction:column;background:' + DARK + ';',
      'padding:.6rem 1rem 1rem;gap:.2rem;flex-wrap:wrap;">',
      MAIN_CATS.concat(EXTRA_CATS).map(function(item) {{
        return '<a href="' + item.href + '" style="color:rgba(255,255,255,.88);text-decoration:none;',
          'padding:.4rem .6rem;border-radius:6px;font-size:.9rem;font-weight:500;">' + item.label + '</a>';
      }}).join(''),
      '</div>',
      // Responsive CSS
      '<style>@media(max-width:760px){{.nav-main{{display:none!important;}}.nav-more{{display:none!important;}}#nav-ham{{display:block!important;}}}}</style>',
    ].join('');

    // ปิด dropdown เมื่อคลิกข้างนอก
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
}})();
"""
    nav_path = BASE_PATH / "nav.js"
    orig = nav_path.read_text(encoding="utf-8", errors="ignore") if nav_path.exists() else ""
    if not DRY_RUN:
        nav_path.write_text(js, encoding="utf-8")
    log_ok(f"สร้าง nav.js — {len(CATEGORIES)} หมวด (main: {len(main_cats)}, dropdown: {len(extra_cats)})")
    return 1


# ══════════════════════════════════════════════════════════════
# 🔧 FIX DEAD LINKS
# ══════════════════════════════════════════════════════════════
def แก้_dead_links() -> int:
    log_section("🔗 แก้ Dead/Empty Links")
    ชื่อไฟล์ = {fp.name for fp in สแกน_html()}
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            changed = False
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href in ("", "javascript:void(0)"):
                    del a["href"]
                    a["href"] = "/"
                    changed = True
                elif (href.endswith(".html") and not href.startswith("http")
                      and not href.startswith("#") and href not in ชื่อไฟล์):
                    # ลิงก์ชี้ไปหน้าที่ไม่มี → ชี้ไปหน้าแรกแทน
                    a["href"] = "/"
                    changed = True
            if changed and เขียน(fp, str(soup), orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  dead-link {fp.name}: {e}")
    log_ok(f"แก้ dead links: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX IMAGES
# ══════════════════════════════════════════════════════════════
def แก้_รูปภาพ() -> int:
    log_section("🖼️  แก้รูปภาพ + onerror")
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            changed = False
            for img in soup.find_all("img"):
                if not img.get("onerror"):
                    stem = fp.stem
                    img["onerror"] = _fallback_img(stem)
                    changed = True
                if not img.get("loading"):
                    img["loading"] = "lazy"
                    changed = True
            if changed and เขียน(fp, str(soup), orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  img {fp.name}: {e}")
    log_ok(f"แก้รูปภาพ: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX SVG EMOJI
# ══════════════════════════════════════════════════════════════
def แก้_svg_emoji() -> int:
    log_section("✨ แก้ SVG Emoji")
    แก้แล้ว = 0
    _SVG_RE = re.compile(r'<svg[^>]*>\s*<text[^>]*>[^<]*</text>\s*</svg>', re.I)
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            changed = False
            for svg in soup.find_all("svg"):
                txt = svg.find("text")
                if txt and len(txt.get_text().strip()) <= 2:
                    emoji = txt.get_text().strip()
                    svg.replace_with(BeautifulSoup(emoji, "html.parser"))
                    changed = True
            if changed and เขียน(fp, str(soup), orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  svg {fp.name}: {e}")
    log_ok(f"แก้ SVG emoji: {แก้แล้ว} ไฟล์")
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
# 🎨 BUILD FOOTER HTML [SHARED]
# ══════════════════════════════════════════════════════════════
def _build_footer_html() -> str:
    th = _theme()
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
      <a href="/"   style="color:rgba(255,255,255,.75);text-decoration:none;">🏠 หน้าแรก</a>
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
    return f'''<!-- HERO SECTION -->
<div style="background:{_hero_gradient()};color:#fff;padding:3.75rem 1.5rem 2.75rem;text-align:center;position:relative;overflow:hidden;">
  <div style="position:absolute;inset:0;background:url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2220%22 cy=%2220%22 r=%2260%22 fill=%22rgba(255,255,255,.04)%22/><circle cx=%2280%22 cy=%2280%22 r=%2240%22 fill=%22rgba(255,255,255,.03)%22/></svg>') no-repeat center;background-size:cover;"></div>
  <div style="position:relative;z-index:1;">
    <h1 style="font-size:clamp(1.9rem,5vw,3rem);font-weight:800;margin-bottom:.75rem;line-height:1.18;letter-spacing:-.01em;">{SITE_NAME}</h1>
    <p style="font-size:1.02rem;opacity:.88;max-width:580px;margin:0 auto 1.5rem;">แหล่งรวมบทความคุณภาพสูง อัปเดตทุกวัน</p>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.4rem .5rem;margin-bottom:1.6rem;max-height:7rem;overflow-y:auto;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.3) transparent;">{cat_pills}</div>
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
            # ✅ v6: เพิ่ม tag pills ทุกหมวดเหมือนหน้าแรก
            f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.35rem .45rem;margin-top:1rem;">'
            + "".join(
                f'<a href="{CATEGORY_PAGE_MAP.get(c, c+".html")}" '
                f'style="display:inline-flex;align-items:center;gap:.3rem;'
                f'padding:.3rem .75rem;background:rgba(255,255,255,.15);color:#fff;'
                f'border-radius:999px;text-decoration:none;font-size:.78rem;font-weight:600;'
                f'transition:background .2s;" '
                f'onmouseover="this.style.background=\'rgba(255,255,255,.28)\'" '
                f'onmouseout="this.style.background=\'rgba(255,255,255,.15)\'">'
                f'{หมวด_ไทย.get(c, c)}</a>'
                for c in CATEGORIES
            )
            + f'</div>'
            f'</div>')


# ══════════════════════════════════════════════════════════════
# 🔧 --fix-footer
# ══════════════════════════════════════════════════════════════
def แก้_footer_ทุกหน้า() -> int:
    log_section("🎨 แก้ Footer สีทุกหน้า")
    footer_html = _build_footer_html()
    แก้แล้ว = 0
    for fp in สแกน_html():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if "<footer" not in orig.lower(): continue
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
# 🔧 --fix-hero
# ══════════════════════════════════════════════════════════════
def แก้_hero_ทุกหน้า() -> int:
    log_section("🎨 แก้ Hero Gradient ทุกหน้า")
    แก้แล้ว = 0
    th = _theme()
    for fp in สแกน_html():
        if fp.name not in _CAT_FILES: continue
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            def _fix_bg(m):
                tag = m.group(0)
                tag = re.sub(r'linear-gradient\([^)]+\)', _hero_gradient(), tag)
                return tag
            new_html = re.sub(
                r'<div[^>]*(?:hero|banner|jumbotron)[^>]*>',
                _fix_bg, orig, flags=re.IGNORECASE
            )
            new_html = re.sub(r'(--primary:\s*)#[0-9a-fA-F]{3,6}', r'\g<1>' + th['primary'], new_html)
            new_html = re.sub(r'(--dark:\s*)#[0-9a-fA-F]{3,6}',    r'\g<1>' + th['dark'],    new_html)
            if เขียน(fp, new_html, orig):
                แก้แล้ว += 1
                log_ok(f"  แก้ hero: {fp.name}")
        except Exception as e:
            log_err(f"  hero {fp.name}: {e}")
    log_ok(f"แก้ hero: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 --fix-css: สร้าง style.css ใหม่
# ══════════════════════════════════════════════════════════════
def rebuild_style_css() -> int:
    log_section("🎨 Rebuild style.css")
    th = _theme()
    css = f"""/* style.css — {SITE_NAME} v6 — auto-generated {datetime.datetime.now().strftime("%Y-%m-%d")} */
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
@media (prefers-color-scheme: dark) {{
  :root {{
    --card:   #1e293b; --bg: #0f172a; --soft: #1e293b;
    --border: #334155; --muted: #94a3b8; --text: #e2e8f0;
  }}
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.6; -webkit-font-smoothing: antialiased; }}
img {{ max-width: 100%; height: auto; display: block; }}
a   {{ color: var(--primary); }}
.page-main  {{ max-width: 1140px; margin: 0 auto; padding: 1rem 1.25rem 2.5rem; }}
.container  {{ max-width: 1140px; margin: 0 auto; padding: 0 1.25rem; }}
.art-grid a:hover {{ transform: translateY(-4px); box-shadow: var(--shadow); }}
.art-grid::-webkit-scrollbar {{ height: 5px; }}
.art-grid::-webkit-scrollbar-thumb {{ background: rgba(0,0,0,.18); border-radius: 999px; }}
.card {{ background: var(--card); border-radius: var(--radius); border: 1px solid var(--border);
         box-shadow: var(--shadow-sm); overflow: hidden; transition: transform .22s, box-shadow .22s; }}
.card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow); }}
nav {{ position: sticky; top: 0; z-index: 100; background: var(--primary); color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.18); }}
.badge {{ display: inline-block; padding: .2rem .6rem; border-radius: 999px; font-size: .68rem; font-weight: 700; background: var(--accent); color: #fff; }}
.btn {{ display: inline-flex; align-items: center; gap: .4rem; padding: .45rem 1rem; border: none; border-radius: 8px; cursor: pointer; font-family: var(--font); font-size: .88rem; font-weight: 600; text-decoration: none; transition: opacity .2s, transform .15s; }}
.btn:hover {{ opacity: .88; transform: translateY(-1px); }}
.btn-primary {{ background: var(--primary); color: #fff; }}
.btn-outline  {{ background: transparent; border: 1.5px solid var(--primary); color: var(--primary); }}
.article-body {{ max-width: 760px; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }}
.article-body h2 {{ font-size: 1.25rem; margin: 1.5rem 0 .6rem; color: var(--primary); }}
.article-body h3 {{ font-size: 1.05rem; margin: 1.2rem 0 .5rem; }}
.article-body p  {{ margin-bottom: 1rem; line-height: 1.8; }}
.article-body ul, .article-body ol {{ margin: .75rem 0 1rem 1.5rem; }}
.article-body li {{ margin-bottom: .4rem; line-height: 1.7; }}
.article-body blockquote {{ border-left: 4px solid var(--accent); padding: .75rem 1.25rem; margin: 1rem 0; background: var(--soft); border-radius: 0 8px 8px 0; font-style: italic; }}
.article-body img {{ border-radius: 10px; margin: 1rem auto; box-shadow: var(--shadow-sm); }}
.hero-image-wrapper img {{ width: 100%; max-height: 480px; object-fit: cover; border-radius: 12px; margin-bottom: 1.25rem; }}
.sidebar {{ min-width: 240px; }}
.sidebar-box {{ background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); padding: 1.1rem; box-shadow: var(--shadow-sm); margin-bottom: 1rem; }}
#search-results a {{ display: flex; gap: .6rem; align-items: center; padding: .55rem .85rem; border-bottom: 1px solid var(--border); text-decoration: none; color: var(--text); font-size: .88rem; transition: background .15s; }}
#search-results a:hover {{ background: var(--soft); }}
#search-results a:last-child {{ border-bottom: none; }}
/* Breadcrumb */
.breadcrumb {{ display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; font-size: .82rem; color: var(--muted); padding: .6rem 0; }}
.breadcrumb a {{ color: var(--primary); text-decoration: none; }}
.breadcrumb a:hover {{ text-decoration: underline; }}
.breadcrumb span {{ opacity: .5; }}
/* Reading time */
.reading-time {{ display: inline-flex; align-items: center; gap: .35rem; font-size: .78rem; color: var(--muted); margin-bottom: .75rem; }}
/* Back to top */
#back-to-top {{ position: fixed; bottom: 1.5rem; right: 1.5rem; background: var(--primary); color: #fff; border: none; border-radius: 999px; width: 42px; height: 42px; display: none; align-items: center; justify-content: center; cursor: pointer; box-shadow: var(--shadow); font-size: 1.1rem; z-index: 500; transition: opacity .2s; }}
#back-to-top.show {{ display: flex; }}
#back-to-top:hover {{ opacity: .85; }}
@media(max-width:768px) {{ .page-main {{ padding: .75rem .85rem 2rem; }} }}
"""
    out = BASE_PATH / "style.css"
    orig = out.read_text(encoding="utf-8", errors="ignore") if out.exists() else ""
    if not DRY_RUN:
        out.write_text(css, encoding="utf-8")
    log_ok(f"rebuild style.css: {len(css)} chars")
    return 1


# ══════════════════════════════════════════════════════════════
# 🔧 [NEW v6] CREATE MISSING CATEGORY PAGES
# ══════════════════════════════════════════════════════════════
# ✅ v6 BUG-FIX: ครบทุกหมวดที่อยู่ใน CATEGORIES
_CAT_TITLE = {cat: (หมวด_ไทย.get(cat, cat), f"รวมบทความ{หมวด_ไทย.get(cat, cat)}คุณภาพสูง อัปเดตทุกวัน")
              for cat in CATEGORIES}


def สร้างหน้าหมวดที่หายไป() -> int:
    """✅ v6: สร้างไฟล์ HTML เปล่าสำหรับหมวดที่ยังไม่มีไฟล์"""
    log_section("📁 สร้างหน้าหมวดที่หายไป [NEW v6]")
    สร้างแล้ว = 0
    for cat in CATEGORIES:
        หน้า = CATEGORY_PAGE_MAP.get(cat, cat + ".html")
        fp   = BASE_PATH / หน้า
        if fp.exists():
            continue  # มีแล้ว ข้าม
        th_name, desc = _CAT_TITLE.get(cat, (cat, f"รวมบทความ{cat}"))
        # สร้างไฟล์เปล่าพื้นฐานก่อน (rebuild_category_pages จะ rebuild ให้ครบ)
        placeholder = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{th_name} — {SITE_NAME}</title>
  <meta name="description" content="{desc}">
  <link rel="stylesheet" href="style.css">
</head>
<body>
<script src="nav.js"></script>
<nav></nav>
<div class="page-main">
  <h1>{th_name}</h1>
  <p>{desc}</p>
</div>
</body></html>"""
        if not DRY_RUN:
            fp.write_text(placeholder, encoding="utf-8")
        log_ok(f"  สร้าง: {หน้า}  ({th_name})")
        สร้างแล้ว += 1
    if สร้างแล้ว == 0:
        log_ok("ทุกหน้าหมวดมีอยู่แล้ว ✅")
    else:
        log_ok(f"สร้างหน้าหมวดใหม่: {สร้างแล้ว} หน้า — กำลัง rebuild เนื้อหา...")
    return สร้างแล้ว


# ══════════════════════════════════════════════════════════════
# 🎨 BUILD CATEGORY PAGE HTML
# ══════════════════════════════════════════════════════════════
def _สร้างหน้าหมวด_ครบ(หน้า: str, content_block: str) -> str:
    stem = หน้า.replace(".html","")
    th_name, desc = _CAT_TITLE.get(stem, (หมวด_ไทย.get(stem, stem), f"รวมบทความ{stem} อัปเดตทุกวัน"))
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
<!-- Back to top -->
<button id="back-to-top" title="กลับด้านบน">↑</button>
<script>
// Search System v6
(function(){{
  var SEARCH_DATA = /*SEARCH_JSON_PLACEHOLDER*/[];
  var inp = document.getElementById('search-input');
  var box = document.getElementById('search-results');
  if(!inp || !box) return;
  box.style.cssText = 'position:absolute;top:115%;left:0;right:0;background:#fff;border-radius:14px;box-shadow:0 12px 32px rgba(0,0,0,.28);z-index:9999;overflow:hidden;max-height:380px;overflow-y:auto;display:none;';
  var timer;
  inp.addEventListener('input', function(){{
    clearTimeout(timer);
    timer = setTimeout(function(){{
      var q = inp.value.trim().toLowerCase();
      box.innerHTML = '';
      if(!q || q.length < 1){{ box.style.display='none'; return; }}
      var hits = SEARCH_DATA.filter(function(a){{
        return (a.t||'').toLowerCase().indexOf(q)>=0 || (a.cat||'').toLowerCase().indexOf(q)>=0;
      }}).slice(0,10);
      if(!hits.length){{
        box.innerHTML='<div style="padding:.75rem 1rem;color:#94a3b8;font-size:.85rem;">ไม่พบบทความ</div>';
        box.style.display='block'; return;
      }}
      hits.forEach(function(a){{
        var el=document.createElement('a');
        el.href=a.u;
        el.style.cssText='display:flex;gap:.6rem;align-items:center;padding:.6rem .9rem;border-bottom:1px solid #f1f5f9;text-decoration:none;color:#1e293b;transition:background .15s;';
        el.onmouseover=function(){{this.style.background='#f8fafc';}};
        el.onmouseout=function(){{this.style.background='';}};
        el.innerHTML='<img src="'+(a.img||'')+'" loading="lazy" style="width:52px;height:38px;object-fit:cover;border-radius:5px;flex-shrink:0;" onerror="this.style.display=\'none\'"><div><div style="font-weight:600;font-size:.88rem;line-height:1.3;">'+(a.t||'')+'</div><div style="font-size:.72rem;color:#94a3b8;margin-top:.1rem;">'+(a.cat||'')+'</div></div>';
        box.appendChild(el);
      }});
      box.style.display='block';
    }}, 180);
  }});
  document.addEventListener('click',function(e){{
    if(!box.contains(e.target)&&e.target!==inp)box.style.display='none';
  }});
  inp.addEventListener('keydown',function(e){{
    if(e.key==='Escape'){{box.style.display='none';inp.value='';}};
  }});
}})();
// Back to top
(function(){{
  var btn = document.getElementById('back-to-top');
  if(!btn) return;
  window.addEventListener('scroll', function(){{
    btn.classList.toggle('show', window.scrollY > 400);
  }});
  btn.addEventListener('click', function(){{ window.scrollTo({{top:0,behavior:'smooth'}}); }});
}})();
try {{
  if('serviceWorker' in navigator && location.protocol !== 'file:')
    navigator.serviceWorker.register('sw.js');
}} catch(e) {{}}
</script>
</body></html>"""


def rebuild_category_pages() -> int:
    log_section(f"📂 Rebuild Category Pages [{LAYOUT_MODE} {COLS}col | {THEME_NAME}]")

    # ✅ v6 BUG-FIX: สร้างหน้าที่หายไปก่อน ไม่ข้าม
    สร้างหน้าหมวดที่หายไป()

    แก้แล้ว = 0
    บทความ  = สแกน_บทความ()
    หน้าที่ทำ = set()
    for หมวด in CATEGORIES:
        หน้า = CATEGORY_PAGE_MAP.get(หมวด, "news.html")
        if หน้า in หน้าที่ทำ: continue
        หน้าที่ทำ.add(หน้า)
        fp = BASE_PATH / หน้า

        # ✅ v6: ถ้าไม่มีไฟล์ยังไม่ออก → สร้างใหม่เลย (กรณี DRY_RUN ข้ามได้)
        if not fp.exists():
            if DRY_RUN:
                log_warn(f"  [DRY-RUN] จะสร้าง: {หน้า}")
                continue
            fp.write_text("", encoding="utf-8")

        ไฟล์หมวด = [f for f in บทความ
                    if CATEGORY_PAGE_MAP.get(ชื่อหมวด(f), "news.html") == หน้า]
        ไฟล์หมวด.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        if not ไฟล์หมวด:
            # ✅ v6: แม้ไม่มีบทความก็ยัง rebuild หน้าหมวด (แสดงว่ากำลังอัปเดต)
            th_name, desc = _CAT_TITLE.get(หมวด, (หมวด_ไทย.get(หมวด, หมวด), f"รวมบทความ{หมวด}"))
            empty_block = (
                f'\n{ART_S}\n'
                f'<div style="text-align:center;padding:3rem 1rem;color:var(--muted,#64748b);">'
                f'<div style="font-size:3rem;margin-bottom:1rem;">📝</div>'
                f'<h2 style="font-size:1.1rem;margin-bottom:.5rem;">กำลังเพิ่มบทความ{th_name}</h2>'
                f'<p style="font-size:.9rem;">ติดตามอัปเดตได้เร็วๆ นี้</p>'
                f'<a href="/" style="display:inline-block;margin-top:1rem;padding:.5rem 1.25rem;'
                f'background:var(--primary,#1e40af);color:#fff;border-radius:8px;text-decoration:none;font-weight:600;">'
                f'← กลับหน้าแรก</a></div>'
                f'\n{ART_E}\n'
            )
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = _สร้างหน้าหมวด_ครบ(หน้า, empty_block)
            # inject search JSON
            try:
                _all_arts = บทความ
                _json_str = json.dumps(
                    [{"t": _parse_article(f)["หัวข้อ"], "u": f.name,
                      "img": _parse_article(f)["img"],
                      "cat": หมวด_ไทย.get(ชื่อหมวด(f), ชื่อหมวด(f))} for f in _all_arts],
                    ensure_ascii=False, separators=(',', ':')
                )
                html = html.replace("/*SEARCH_JSON_PLACEHOLDER*/[]", f"/*SEARCH_JSON_PLACEHOLDER*/{_json_str}", 1)
            except Exception: pass
            if เขียน(fp, html, orig):
                log_ok(f"  {หน้า} — ยังไม่มีบทความ (สร้าง placeholder)")
                แก้แล้ว += 1
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

        # inject inline search JSON
        try:
            _all_arts = สแกน_บทความ()
            _json_str = json.dumps(
                [{"t": _parse_article(f)["หัวข้อ"], "u": f.name,
                  "img": _parse_article(f)["img"],
                  "cat": หมวด_ไทย.get(ชื่อหมวด(f), ชื่อหมวด(f))} for f in _all_arts],
                ensure_ascii=False, separators=(',', ':')
            )
            html = html.replace("/*SEARCH_JSON_PLACEHOLDER*/[]",
                                f"/*SEARCH_JSON_PLACEHOLDER*/{_json_str}", 1)
        except Exception: pass

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
        for c in CATEGORIES
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
<!-- Back to top -->
<button id="back-to-top" title="กลับด้านบน">↑</button>
<script>
// Search System v6
(function(){{
  var SEARCH_DATA = /*SEARCH_JSON_PLACEHOLDER*/[];
  var inp = document.getElementById('search-input');
  var box = document.getElementById('search-results');
  if(!inp || !box) return;
  box.style.cssText = 'position:absolute;top:115%;left:0;right:0;background:#fff;border-radius:14px;box-shadow:0 12px 32px rgba(0,0,0,.28);z-index:9999;overflow:hidden;max-height:380px;overflow-y:auto;display:none;';
  var timer;
  inp.addEventListener('input', function(){{
    clearTimeout(timer);
    timer = setTimeout(function(){{
      var q = inp.value.trim().toLowerCase();
      box.innerHTML = '';
      if(!q || q.length < 1){{ box.style.display='none'; return; }}
      var hits = SEARCH_DATA.filter(function(a){{
        return (a.t||'').toLowerCase().indexOf(q)>=0||(a.cat||'').toLowerCase().indexOf(q)>=0;
      }}).slice(0,10);
      if(!hits.length){{
        box.innerHTML='<div style="padding:.75rem 1rem;color:#94a3b8;font-size:.85rem;">ไม่พบบทความ</div>';
        box.style.display='block'; return;
      }}
      hits.forEach(function(a){{
        var el=document.createElement('a');
        el.href=a.u;
        el.style.cssText='display:flex;gap:.6rem;align-items:center;padding:.6rem .9rem;border-bottom:1px solid #f1f5f9;text-decoration:none;color:#1e293b;transition:background .15s;';
        el.onmouseover=function(){{this.style.background='#f8fafc';}};
        el.onmouseout=function(){{this.style.background='';}};
        el.innerHTML='<img src="'+(a.img||'')+'" loading="lazy" style="width:52px;height:38px;object-fit:cover;border-radius:5px;flex-shrink:0;" onerror="this.style.display=\'none\'"><div><div style="font-weight:600;font-size:.88rem;line-height:1.3;">'+(a.t||'')+'</div><div style="font-size:.72rem;color:#94a3b8;margin-top:.1rem;">'+(a.cat||'')+'</div></div>';
        box.appendChild(el);
      }});
      box.style.display='block';
    }}, 180);
  }});
  document.addEventListener('click',function(e){{
    if(!box.contains(e.target)&&e.target!==inp)box.style.display='none';
  }});
  inp.addEventListener('keydown',function(e){{
    if(e.key==='Escape'){{box.style.display='none';inp.value='';}};
  }});
}})();
// Back to top
(function(){{
  var btn = document.getElementById('back-to-top');
  if(!btn) return;
  window.addEventListener('scroll', function(){{ btn.classList.toggle('show', window.scrollY > 400); }});
  btn.addEventListener('click', function(){{ window.scrollTo({{top:0,behavior:'smooth'}}); }});
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

    seen, unique = set(), []
    for f in บทความ:
        if f.stem not in seen: seen.add(f.stem); unique.append(f)
    บทความ = unique

    การ์ด = _build_cards(บทความ[:30])

    orig = fp.read_text(encoding="utf-8", errors="ignore") if fp.exists() else ""
    html = _สร้างหน้า_index_ครบ(การ์ด, len(บทความ))
    json_str = json.dumps(
        [{"t": _parse_article(f)["หัวข้อ"], "u": f.name,
          "img": _parse_article(f)["img"],
          "cat": หมวด_ไทย.get(ชื่อหมวด(f), ชื่อหมวด(f))} for f in บทความ],
        ensure_ascii=False, separators=(',', ':')
    )
    html = html.replace("/*SEARCH_JSON_PLACEHOLDER*/[]",
                        f"/*SEARCH_JSON_PLACEHOLDER*/{json_str}", 1)
    html = _ลบ_search_script_ซ้ำ(html)   # ✅ กัน search script ซ้ำ
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
        pri = "1.0" if fp.name in ("/", "index.html") else ("0.8" if fp.name in _CAT_FILES else "0.6")
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
# 🔧 [NEW v6] ROBOTS.TXT
# ══════════════════════════════════════════════════════════════
def สร้าง_robots_txt() -> int:
    log_section("🤖 สร้าง robots.txt")
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /*.py
Disallow: /*.json

Sitemap: {SITE_URL}/sitemap.xml

# Generated by agent_fix_v6.py — {datetime.datetime.now().strftime("%Y-%m-%d")}
"""
    fp = BASE_PATH / "robots.txt"
    orig = fp.read_text(encoding="utf-8", errors="ignore") if fp.exists() else ""
    if not DRY_RUN:
        fp.write_text(content, encoding="utf-8")
    log_ok("สร้าง robots.txt")
    return 1


# ══════════════════════════════════════════════════════════════
# 🔧 PUSH GITHUB
# ══════════════════════════════════════════════════════════════
def push_github():
    log_section("🚀 Push GitHub")
    try:
        subprocess.run(["git","-C",str(BASE_PATH),"add","-A"], check=True)
        msg = f"fix: v6 rebuild {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} [{LAYOUT_MODE}|{THEME_NAME}]"
        try:
            subprocess.run(["git","-C",str(BASE_PATH),"commit","-m",msg], check=True)
        except subprocess.CalledProcessError:
            log_info("ไม่มีอะไรต้อง commit")

        # ── pull --rebase ก่อน push เสมอ เพื่อไม่ให้ fetch first error ──
        log_info("git pull --rebase ก่อน push...")
        try:
            subprocess.run(
                ["git","-C",str(BASE_PATH),"pull","--rebase","origin","main"],
                check=True
            )
        except subprocess.CalledProcessError:
            log_warn("pull --rebase ล้มเหลว — ลอง push ต่อ")

        subprocess.run(["git","-C",str(BASE_PATH),"push","origin","main"], check=True)
        log_ok("Push สำเร็จ")
    except subprocess.CalledProcessError as e:
        log_err(f"Push ล้มเหลว: {e}")


# ══════════════════════════════════════════════════════════════
# 🔍 FIX SEARCH
# ══════════════════════════════════════════════════════════════
_SEARCH_JS = """
(function(){
  var SEARCH_DATA = /*SEARCH_JSON_PLACEHOLDER*/[];
  var inp = document.getElementById('search-input');
  var box = document.getElementById('search-results');
  if(!inp || !box) return;
  box.style.cssText = ['position:absolute','top:115%','left:0','right:0','background:#fff','border-radius:14px','box-shadow:0 12px 32px rgba(0,0,0,.28)','z-index:9999','overflow:hidden','max-height:380px','overflow-y:auto','display:none'].join(';');
  var timer;
  inp.addEventListener('input', function(){
    clearTimeout(timer);
    timer = setTimeout(function(){
      var q = inp.value.trim().toLowerCase();
      box.innerHTML = '';
      if(!q){ box.style.display='none'; return; }
      var hits = SEARCH_DATA.filter(function(a){
        return (a.t||'').toLowerCase().indexOf(q)>=0||(a.cat||'').toLowerCase().indexOf(q)>=0;
      }).slice(0,10);
      if(!hits.length){
        box.innerHTML='<div style="padding:.75rem 1rem;color:#94a3b8;font-size:.85rem;">ไม่พบบทความ</div>';
        box.style.display='block'; return;
      }
      hits.forEach(function(a){
        var el=document.createElement('a');
        el.href=a.u;
        el.style.cssText='display:flex;gap:.6rem;align-items:center;padding:.6rem .9rem;border-bottom:1px solid #f1f5f9;text-decoration:none;color:#1e293b;transition:background .15s;';
        el.onmouseover=function(){this.style.background='#f8fafc';};
        el.onmouseout=function(){this.style.background='';};
        el.innerHTML='<img src="'+(a.img||'')+'" loading="lazy" style="width:52px;height:38px;object-fit:cover;border-radius:5px;flex-shrink:0;" onerror="this.style.display=\'none\'"><div><div style="font-weight:600;font-size:.88rem;line-height:1.3;">'+(a.t||'')+'</div><div style="font-size:.72rem;color:#94a3b8;margin-top:.1rem;">'+(a.cat||'')+'</div></div>';
        box.appendChild(el);
      });
      box.style.display='block';
    }, 180);
  });
  document.addEventListener('click',function(e){
    if(!box.contains(e.target)&&e.target!==inp)box.style.display='none';
  });
  inp.addEventListener('keydown',function(e){
    if(e.key==='Escape'){box.style.display='none';inp.value='';}
  });
})();
"""

_SEARCH_CSS = """<style id="search-fix-css">
#search-input::placeholder{color:rgba(255,255,255,.65);}
#search-input:focus{background:rgba(255,255,255,.25)!important;}
#search-results a:last-child{border-bottom:none!important;}
#search-results{scrollbar-width:thin;scrollbar-color:#cbd5e1 transparent;}
</style>"""

def _ลบ_search_script_ซ้ำ(html: str) -> str:
    """ลบ search script block ที่ซ้ำ เก็บไว้แค่ block แรก"""
    pattern = re.compile(
        r'<script[^>]*>\s*\(function\(\)\{[^<]*?var SEARCH_DATA\s*=.*?\}\)\(\);?\s*</script>',
        re.DOTALL
    )
    count = [0]
    def _keep_first(m):
        count[0] += 1
        return m.group(0) if count[0] == 1 else ""
    return pattern.sub(_keep_first, html)


def แก้_search() -> int:
    log_section("🔍 Fix Search — v6")
    บทความ  = สแกน_บทความ()
    entries = []
    for fp in บทความ:
        try:
            soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            t    = ดึงหัวข้อ(soup, fp)
            img  = ดึงรูปหลัก(soup, fp) or _picsum(fp.stem)
            cat  = หมวด_ไทย.get(ชื่อหมวด(fp), ชื่อหมวด(fp))
            entries.append({"t": t, "u": fp.name, "img": img, "cat": cat})
        except Exception as e:
            log_warn(f"  skip {fp.name}: {e}")

    json_str = json.dumps(entries, ensure_ascii=False, separators=(',', ':'))
    idx_json = BASE_PATH / "search-index.json"
    if not DRY_RUN:
        idx_json.write_text(json_str, encoding="utf-8")
    log_ok(f"  search-index.json: {len(entries)} รายการ")

    inline_script = _SEARCH_JS.replace("/*SEARCH_JSON_PLACEHOLDER*/[]",
                                        f"/*SEARCH_JSON_PLACEHOLDER*/{json_str}")
    แก้แล้ว = 0
    ไฟล์เป้า = [BASE_PATH / "index.html"] + [BASE_PATH / p for p in CATEGORY_PAGE_MAP.values()]
    _OLD_RE  = re.compile(r'//\s*Search\s*(?:functionality|index|System)[^\n]*\n\s*\(function\(\)\{.*?\}\)\(\);', re.DOTALL|re.IGNORECASE)
    _OLD_RE2 = re.compile(r'fetch\([\'"]search-index\.json[\'"]\).*?\}\)\(\);', re.DOTALL)

    for fp in ไฟล์เป้า:
        if not fp.exists(): continue
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if 'id="search-input"' not in orig and "id='search-input'" not in orig: continue
            html = orig
            html = _OLD_RE.sub("", html)
            html = _OLD_RE2.sub("", html)
            html = re.sub(r'<style id="search-fix-css">.*?</style>', "", html, flags=re.DOTALL)
            if _SEARCH_CSS.strip() not in html:
                if "</head>" in html:
                    html = html.replace("</head>", _SEARCH_CSS + "</head>", 1)
            script_tag = f"<script>\n{inline_script}\n</script>"
            html = re.sub(r'<script>\s*//\s*Search.*?</script>', "", html, flags=re.DOTALL|re.IGNORECASE)
            html = re.sub(r'<script>\s*\(function\(\)\{[^<]*fetch\([\'"]search-index[^<]*</script>', "", html, flags=re.DOTALL)
            if "</body>" in html:
                html = html.replace("</body>", script_tag + "\n</body>", 1)
            else:
                html += "\n" + script_tag
            if เขียน(fp, html, orig):
                log_ok(f"  ✅ แก้ search: {fp.name}")
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  search {fp.name}: {e}")

    log_ok(f"แก้ search: {แก้แล้ว} ไฟล์ | {len(entries)} บทความ")
    return แก้แล้ว


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
    inner_m = re.search(r'<aside[^>]*>(.*?)</aside>', sidebar_content, re.DOTALL)
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
            new_html = re.sub(
                r'(<aside[^>]*class=["\'][^"\']*sidebar[^"\']*["\'][^>]*>)(.*?)(</aside>)',
                _inject, orig, flags=re.DOTALL)
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
    log_section("💬 Chat Mode — WebBot v6")
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
# 🔧 FIX META DESCRIPTION
# ══════════════════════════════════════════════════════════════
def แก้_meta_description() -> int:
    log_section("📝 แก้ Meta Description ว่าง")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            meta = soup.find("meta", {"name": "description"})
            content = (meta.get("content","") if meta else "").strip()
            if content and len(content) > 30: continue

            body = soup.find(class_="article-body") or soup.find("article") or soup.find("main")
            excerpt = ""
            if body:
                for p in body.find_all("p"):
                    t = p.get_text().strip()
                    if len(t) > 40:
                        excerpt = t[:155].rstrip() + "…"
                        break
            if not excerpt:
                h1 = soup.find("h1")
                excerpt = (h1.get_text().strip() + " — " + SITE_NAME) if h1 else SITE_NAME

            html = orig
            if meta:
                html = re.sub(
                    r'(<meta\s+name=["\']description["\']\s+content=["\'])[^"\']*(["\'])',
                    r'\g<1>' + excerpt.replace("\\","\\\\") + r'\g<2>',
                    html, flags=re.IGNORECASE
                )
            else:
                html = re.sub(
                    r'(</title>)',
                    r'\1\n  <meta name="description" content="' + excerpt + '">',
                    html, count=1, flags=re.IGNORECASE
                )
            og = soup.find("meta", {"property": "og:description"})
            og_content = (og.get("content","") if og else "").strip()
            if not og_content or len(og_content) < 30:
                html = re.sub(
                    r'(<meta\s+property=["\']og:description["\']\s+content=["\'])[^"\']*(["\'])',
                    r'\g<1>' + excerpt.replace("\\","\\\\") + r'\g<2>',
                    html, flags=re.IGNORECASE
                )
            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  meta {fp.name}: {e}")
    log_ok(f"แก้ meta description: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX 404 PAGE
# ══════════════════════════════════════════════════════════════
def แก้_หน้า_404() -> int:
    log_section("🚫 แก้หน้า 404")
    fp = BASE_PATH / "404.html"
    th = _theme()
    html_404 = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>404 — ไม่พบหน้านี้ | {SITE_NAME}</title>
  <meta name="robots" content="noindex">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700;800&display=swap" rel="stylesheet">
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Sarabun',sans-serif;background:{th['dark']};
          display:flex;align-items:center;justify-content:center;
          min-height:100vh;text-align:center;padding:2rem;}}
    .box{{color:#fff;max-width:480px;}}
    .code{{font-size:clamp(5rem,20vw,9rem);font-weight:800;
           background:linear-gradient(135deg,{th['accent']},{th['primary']});
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           line-height:1;margin-bottom:.5rem;}}
    h1{{font-size:1.5rem;margin-bottom:.75rem;opacity:.9;}}
    p{{opacity:.65;font-size:.95rem;margin-bottom:1.75rem;line-height:1.6;}}
    .btn{{display:inline-block;padding:.75rem 2rem;border-radius:999px;
          background:{th['primary']};color:#fff;text-decoration:none;
          font-weight:700;font-size:1rem;transition:opacity .2s;}}
    .btn:hover{{opacity:.85;}}
    .search{{margin-top:1.5rem;}}
    .search input{{width:100%;padding:.65rem 1.1rem;border-radius:999px;border:none;
                   font-family:inherit;font-size:.95rem;outline:none;}}
    #countdown{{font-size:.85rem;opacity:.5;margin-top:1rem;}}
  </style>
</head>
<body>
  <div class="box">
    <div class="code">404</div>
    <h1>ไม่พบหน้าที่คุณต้องการ</h1>
    <p>หน้านี้อาจถูกลบ ย้าย หรือไม่มีอยู่จริง<br>ลองค้นหาหรือกลับหน้าแรกได้เลยครับ</p>
    <a href="/" class="btn">🏠 กลับหน้าแรก</a>
    <div class="search">
      <input type="text" placeholder="🔍 ค้นหาบทความ..."
        onkeydown="if(event.key==='Enter')location.href='index.html#s='+encodeURIComponent(this.value)">
    </div>
    <p id="countdown"></p>
  </div>
  <script>
    var t = 15;
    var cd = document.getElementById('countdown');
    var i = setInterval(function(){{
      t--;
      if(cd) cd.textContent = 'กลับหน้าแรกอัตโนมัติใน ' + t + ' วินาที...';
      if(t <= 0){{ clearInterval(i); location.href='/'; }}
    }}, 1000);
    if(cd) cd.textContent = 'กลับหน้าแรกอัตโนมัติใน ' + t + ' วินาที...';
  </script>
</body>
</html>"""
    orig = fp.read_text(encoding="utf-8", errors="ignore") if fp.exists() else ""
    if เขียน(fp, html_404, orig):
        log_ok("สร้าง/อัปเดต 404.html")
        return 1
    log_info("404.html ไม่มีการเปลี่ยนแปลง")
    return 0


# ══════════════════════════════════════════════════════════════
# 🔧 FIX SELF LINKS
# ══════════════════════════════════════════════════════════════
def แก้_self_links() -> int:
    log_section("🔄 แก้ลิงก์วนซ้ำตัวเอง (Self Links)")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            changed = False
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href == fp.name or href == "./" + fp.name or href.endswith("/" + fp.name):
                    a.unwrap()
                    changed = True
                    log_warn(f"  ลบ self-link: {fp.name} → {href}")
            if changed and เขียน(fp, str(soup), orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  self-link {fp.name}: {e}")
    log_ok(f"แก้ self-links: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 FIX IMG ALT
# ══════════════════════════════════════════════════════════════
def แก้_img_alt() -> int:
    log_section("🖼️  เติม Alt Text รูปภาพ (SEO)")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            h1   = soup.find("h1")
            title = h1.get_text().strip() if h1 else fp.stem.replace("_"," ")
            changed = False
            for i, img in enumerate(soup.find_all("img")):
                alt = img.get("alt","").strip()
                if not alt:
                    img["alt"] = title if i == 0 else f"{title} รูปที่ {i+1}"
                    changed = True
            if changed and เขียน(fp, str(soup), orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  alt {fp.name}: {e}")
    log_ok(f"เติม alt: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 CHECK DUPLICATE CONTENT
# ══════════════════════════════════════════════════════════════
def ตรวจ_บทความซ้ำเนื้อหา() -> int:
    log_section("🔁 ตรวจบทความเนื้อหาซ้ำ")
    บทความ = สแกน_บทความ()
    hashes = {}
    ซ้ำ    = []
    for fp in บทความ:
        try:
            txt  = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(txt, "html.parser")
            body = soup.find(class_="article-body") or soup.find("article") or soup.find("main")
            text = body.get_text().strip() if body else ""
            if len(text) < 100: continue
            fingerprint = hashlib.md5(text[:500].encode()).hexdigest()
            if fingerprint in hashes:
                ซ้ำ.append((fp.name, hashes[fingerprint]))
                log_warn(f"  ซ้ำ: {fp.name} ≈ {hashes[fingerprint]}")
            else:
                hashes[fingerprint] = fp.name
        except Exception as e:
            log_err(f"  dup-check {fp.name}: {e}")

    if ซ้ำ:
        log_warn(f"พบซ้ำ: {len(ซ้ำ)} คู่")
        for a, b in ซ้ำ[:5]:
            log(f"  • {a}  ≈  {b}")
    else:
        log_ok("ไม่พบบทความเนื้อหาซ้ำ 🎉")
    return len(ซ้ำ)


# ══════════════════════════════════════════════════════════════
# 🖼️  [NEW] ตรวจและแก้รูปซ้ำข้ามบทความ
# ══════════════════════════════════════════════════════════════
def _extract_photo_id_fix(url: str) -> str:
    m = re.search(r'photo-([a-f0-9-]{10,})', url)
    if m: return m.group(1)
    m = re.search(r'photos/(\d+)/', url)
    if m: return m.group(1)
    return url

def ตรวจและแก้_รูปซ้ำ() -> int:
    """สแกนทุกบทความ หารูป URL ที่ซ้ำกัน แล้วแก้ไม่ให้ซ้ำ"""
    log_section("🖼️  ตรวจและแก้รูปซ้ำข้ามบทความ [AUTO-FIX]")
    บทความ = สแกน_บทความ()
    seen: dict = {}
    ซ้ำ_list: list = []

    for fp_art in บทความ:
        try:
            soup = BeautifulSoup(fp_art.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            hero_sec = (soup.find(class_="hero-image-wrapper") or
                        soup.find(class_="hero-image") or
                        soup.find(class_="article-hero"))
            img_tag = hero_sec.find("img") if hero_sec else None
            if not img_tag:
                img_tag = soup.find("img")
            if not img_tag:
                continue
            src = img_tag.get("src", "").strip()
            if not src or src.startswith("data:"):
                continue
            pid = _extract_photo_id_fix(src)
            if pid in seen:
                ซ้ำ_list.append((fp_art, src, pid, seen[pid]))
                log_warn(f"  รูปซ้ำ: {fp_art.name} == {seen[pid].name}")
            else:
                seen[pid] = fp_art
        except Exception as e:
            log_err(f"  img-scan {fp_art.name}: {e}")

    if not ซ้ำ_list:
        log_ok("ไม่พบรูปซ้ำข้ามบทความ 🎉")
        return 0

    log_warn(f"พบรูปซ้ำ {len(ซ้ำ_list)} ไฟล์ — กำลังแก้...")
    แก้แล้ว = 0
    for fp_art, old_src, pid, first_fp in ซ้ำ_list:
        try:
            seed = hashlib.md5((fp_art.stem + "_dedup").encode()).hexdigest()[:12]
            new_src = f"https://picsum.photos/seed/{seed}/800/450"
            orig = fp_art.read_text(encoding="utf-8", errors="ignore")
            new_html = orig.replace(old_src, new_src)
            if เขียน(fp_art, new_html, orig):
                log_ok(f"  แก้ {fp_art.name}: เปลี่ยนรูปซ้ำกับ {first_fp.name}")
                แก้แล้ว += 1
            else:
                log_warn(f"  {fp_art.name}: URL ไม่ตรง — ข้าม")
        except Exception as e:
            log_err(f"  แก้รูปซ้ำ {fp_art.name}: {e}")

    log_ok(f"แก้รูปซ้ำ: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 [NEW v6] BREADCRUMB — เพิ่ม breadcrumb ทุกหน้าบทความ
# ══════════════════════════════════════════════════════════════
def เพิ่ม_breadcrumb() -> int:
    log_section("🍞 เพิ่ม Breadcrumb Navigation [NEW v6]")
    th = _theme()
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if 'class="breadcrumb"' in orig or "breadcrumb" in orig: continue
            soup = BeautifulSoup(orig, "html.parser")
            หัวข้อ = ดึงหัวข้อ(soup, fp)
            หมวด  = ชื่อหมวด(fp)
            หมวด_th = หมวด_ไทย.get(หมวด, หมวด)
            หน้าหมวด = CATEGORY_PAGE_MAP.get(หมวด, "/")

            breadcrumb_html = (
                f'<nav class="breadcrumb" aria-label="breadcrumb" '
                f'style="max-width:760px;margin:.75rem auto 0;padding:.5rem 1.25rem;font-size:.82rem;color:#64748b;">'
                f'<a href="/" style="color:{th["primary"]};text-decoration:none;">🏠 หน้าแรก</a>'
                f'<span style="margin:0 .4rem;opacity:.4;">/</span>'
                f'<a href="{หน้าหมวด}" style="color:{th["primary"]};text-decoration:none;">{หมวด_th}</a>'
                f'<span style="margin:0 .4rem;opacity:.4;">/</span>'
                f'<span style="color:#94a3b8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
                f'max-width:200px;display:inline-block;vertical-align:middle;">{หัวข้อ[:50]}</span>'
                f'</nav>'
            )

            html = orig
            # เพิ่มหลัง <body> หรือหลัง <nav>
            if "</nav>" in html:
                idx = html.find("</nav>") + len("</nav>")
                html = html[:idx] + "\n" + breadcrumb_html + html[idx:]
            elif "<body" in html:
                html = re.sub(r'(<body[^>]*>)', r'\1\n' + breadcrumb_html, html, count=1, flags=re.IGNORECASE)

            if เขียน(fp, html, orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  breadcrumb {fp.name}: {e}")
    log_ok(f"เพิ่ม breadcrumb: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 [NEW v6] FIX OG:IMAGE — เติม og:image ทุกบทความ
# ══════════════════════════════════════════════════════════════
def แก้_og_image() -> int:
    log_section("🖼️  เติม og:image ทุกบทความ [NEW v6]")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            og_img = soup.find("meta", {"property": "og:image"})
            og_content = (og_img.get("content","") if og_img else "").strip()

            # มีอยู่แล้วและไม่ใช่ default → ข้าม
            if og_content and "og-default" not in og_content: continue

            # หารูปจากบทความ
            img_src = ดึงรูปหลัก(soup, fp)
            if not img_src: img_src = f"{SITE_URL}/images/og-default.png"
            elif not img_src.startswith("http"):
                img_src = f"{SITE_URL}/{img_src}"

            html = orig
            if og_img:
                html = re.sub(
                    r'(<meta\s+property=["\']og:image["\']\s+content=["\'])[^"\']*(["\'])',
                    r'\g<1>' + img_src + r'\g<2>',
                    html, flags=re.IGNORECASE
                )
            else:
                # เพิ่มใหม่หลัง og:description หรือหลัง </title>
                tag = f'<meta property="og:image" content="{img_src}">'
                if 'og:description' in html:
                    html = re.sub(r'(<meta[^>]+og:description[^>]+>)', r'\1\n  ' + tag, html, count=1)
                else:
                    html = html.replace("</title>", f"</title>\n  {tag}", 1)

            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  og:image {fp.name}: {e}")
    log_ok(f"เติม og:image: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 [NEW v6] READING TIME — เพิ่มเวลาอ่านบทความ
# ══════════════════════════════════════════════════════════════
def เพิ่ม_reading_time() -> int:
    log_section("⏱️  เพิ่มเวลาอ่านบทความ [NEW v6]")
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if "reading-time" in orig: continue
            soup = BeautifulSoup(orig, "html.parser")
            body = soup.find(class_="article-body") or soup.find("article")
            if not body: continue
            word_count = len(body.get_text().split())
            minutes    = max(1, round(word_count / 250))  # ~250 คำ/นาที ภาษาไทย
            time_html  = (
                f'<span class="reading-time" style="display:inline-flex;align-items:center;'
                f'gap:.35rem;font-size:.78rem;color:#94a3b8;margin-bottom:.75rem;">'
                f'<i class="fas fa-clock"></i> อ่าน {minutes} นาที · {word_count} คำ</span>'
            )
            # เพิ่มก่อน h1 หรือหลัง h1
            h1 = body.find("h1") or soup.find("h1")
            html = orig
            if h1:
                html = html.replace(str(h1), str(h1) + "\n" + time_html, 1)
            else:
                # เพิ่มต้น body
                html = re.sub(r'(class=["\']article-body["\'][^>]*>)', r'\1\n' + time_html, html, count=1)

            if เขียน(fp, html, orig): แก้แล้ว += 1
        except Exception as e:
            log_err(f"  reading-time {fp.name}: {e}")
    log_ok(f"เพิ่ม reading time: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🔧 [NEW] แก้ Share Buttons — JS Quote Bug
# ══════════════════════════════════════════════════════════════
def แก้_share_buttons() -> int:
    """
    แก้ bug JS syntax error ใน share button ของบทความเก่าทั้งหมด
    ปัญหา: btn.innerHTML='<i class='fas fa-check'></i>...'
           single quote ใน class= ไปปิด JS string → ปุ่มแชร์ทุกอันหายหมด
    แก้:   เปลี่ยนเป็น double quote ใน HTML attribute ข้างใน JS string
    """
    log_section("🔧 แก้ Share Buttons JS Bug [NEW]")
    แก้แล้ว = 0

    # pattern เก่าที่ผิด (single quote ใน class attribute)
    OLD_PATTERNS = [
        # escaped single quote version
        (
            r"btn\.innerHTML='<i class=\\'fas fa-check\\'></i> คัดลอกแล้ว!'",
            "btn.innerHTML='<i class=\"fas fa-check\"></i> คัดลอกแล้ว!'"
        ),
        (
            r"btn\.innerHTML='<i class=\\'fas fa-link\\'></i> คัดลอกลิงก์'",
            "btn.innerHTML='<i class=\"fas fa-link\"></i> คัดลอกลิงก์'"
        ),
        # unescaped single quote version (ที่ทำให้พัง)
        (
            "btn.innerHTML='<i class='fas fa-check'></i> คัดลอกแล้ว!'",
            "btn.innerHTML='<i class=\"fas fa-check\"></i> คัดลอกแล้ว!'"
        ),
        (
            "btn.innerHTML='<i class='fas fa-link'></i> คัดลอกลิงก์'",
            "btn.innerHTML='<i class=\"fas fa-link\"></i> คัดลอกลิงก์'"
        ),
    ]

    for fp in list(สแกน_บทความ()) + [BASE_PATH / f for f in ["index.html","news.html","lifestyle.html","health.html","food.html"]]:
        if not fp.exists():
            continue
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            if "share-btns" not in orig:
                continue
            html = orig
            for old, new in OLD_PATTERNS:
                html = html.replace(old, new)
            if เขียน(fp, html, orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  share-btn {fp.name}: {e}")

    log_ok(f"แก้ share buttons: {แก้แล้ว} ไฟล์")
    return แก้แล้ว



def ลบ_instruction_หลุด() -> int:
    """
    ลบบรรทัด/ย่อหน้าที่เป็น instruction ของ AI หลุดมาอยู่ในเนื้อหาบทความ
    เช่น 'สไตล์บังคับสำหรับ section นี้:', 'กฎ:', 'ขึ้นต้นด้วย ##' ฯลฯ
    """
    log_section("🧹 ลบ Instruction หลุดจากบทความ [NEW]")
    # pattern ที่ต้องลบออก (เป็น <p> tag ใน HTML)
    REMOVE_P = [
        r'<p>\s*สไตล์บังคับ[^<]{0,500}</p>',
        r'<p>\s*สไตล์สำหรับ[^<]{0,500}</p>',
        r'<p>\s*สไตล์:[^<]{0,500}</p>',
        r'<p>\s*กฎ\s*:[^<]{0,500}</p>',
        r'<p>\s*กฎ\s*</p>',
        r'<p>\s*ประเด็นหลัก\s*:[^<]{0,500}</p>',
        r'<p>\s*ขอเนื้อหาส่วน[^<]{0,500}</p>',
        r'<p>\s*ขึ้นต้นด้วย ##[^<]{0,500}</p>',
        r'<p>\s*เขียน Markdown[^<]{0,500}</p>',
        r'<p>\s*ห้าม HTML[^<]{0,500}</p>',
        r'<p>\s*ตอบเป็น Markdown[^<]{0,500}</p>',
        r'<p>[⚠️✨🔴🔥💡📌]*\s*(สำคัญมาก|กฎสำคัญ|หมายเหตุ)[^<]{0,400}</p>',
        r'<p>\d+\.\s*(เริ่มด้วย|ห้าม|เขียน Markdown|ความยาว)[^<]{0,400}</p>',
        r'<li[^>]*>\s*ห้าม[^<]{0,200}</li>',
        r'<p>\s*-\s*(เขียน|ห้าม|ใส่|สลับ|ตอบ)[^<]{0,300}</p>',
        # ── ลบ h2/h3 ที่ขึ้นต้นด้วย "ย่อหน้า N" ไม่ว่าจะมีชื่อตามหรือไม่ ──
        r'<h[23][^>]*>\s*ย่อหน้า(ที่)?\s*\d+[^<]*</h[23]>',
        r'<h[23][^>]*>\s*ตอน(ที่)?\s*\d+[^<]*</h[23]>',
        r'<h[23][^>]*>\s*ฉาก(ที่)?\s*\d+[^<]*</h[23]>',
        # ── ลบ #### Q3: markdown ดิบที่หลุดมาเป็น <p> ──
        r'<p>\s*#{2,5}\s*Q\d+[:\s][^<]{0,400}</p>',
        r'<p>\s*#{2,5}\s*A\s*:[^<]{0,400}</p>',
        r'<h[34][^>]*>\s*#{2,5}\s*Q\d+[^<]*</h[34]>',
    ]
    แก้แล้ว = 0
    for fp in สแกน_บทความ():
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            for pattern in REMOVE_P:
                html = re.sub(pattern, '', html, flags=re.IGNORECASE | re.DOTALL)
            if เขียน(fp, html, orig):
                แก้แล้ว += 1
        except Exception as e:
            log_err(f"  instruction {fp.name}: {e}")
    log_ok(f"ลบ instruction หลุด: {แก้แล้ว} ไฟล์")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════
# 🚀 รัน_fix_ทั้งหมด
# ══════════════════════════════════════════════════════════════
def รัน_fix_ทั้งหมด():
    log_section(f"🛠️  Fix v6 — Layout: {LAYOUT_MODE} | Cols: {COLS} | Theme: {THEME_NAME}")
    log(f"📁 {BASE_PATH}")
    if DRY_RUN: log_warn("DRY-RUN mode")

    audit_ทั้งหมด()

    steps = [
        ("สร้าง nav.js ครบทุกหมวด",  สร้าง_nav_js),          # ✅ v6: ก่อนเลย
        ("สร้างหน้าหมวดที่หายไป",     สร้างหน้าหมวดที่หายไป), # ✅ v6: BUG-FIX
        ("ลบ instruction หลุด",       ลบ_instruction_หลุด),   # ✅ NEW: ล้างบทความเก่า
        ("แก้ share buttons JS bug",  แก้_share_buttons),      # ✅ NEW: แก้ปุ่มแชร์หาย
        ("แก้ nav bar",               แก้_nav),
        ("แก้ dead/empty links",       แก้_dead_links),
        ("แก้รูปภาพ + onerror",        แก้_รูปภาพ),
        ("แก้ SVG emoji",              แก้_svg_emoji),
        ("แก้ h1",                     แก้_h1),
        ("แก้เนื้อหาว่าง",             แก้_เนื้อหาว่าง),
        ("rebuild category pages",    rebuild_category_pages),
        ("rebuild index page",        rebuild_index_page),
        ("แก้ footer สี",              แก้_footer_ทุกหน้า),
        ("ใส่ sidebar สนับสนุนเรา",    แก้_support_sidebar),
        ("related articles",          แก้_related_articles),
        ("fix search ค้นหา",          แก้_search),
        ("แก้ meta description",      แก้_meta_description),
        ("แก้ og:image",              แก้_og_image),           # ✅ v6
        ("แก้ self links",            แก้_self_links),
        ("เติม img alt",              แก้_img_alt),
        ("เพิ่ม breadcrumb",           เพิ่ม_breadcrumb),       # ✅ v6
        ("เพิ่ม reading time",         เพิ่ม_reading_time),     # ✅ v6
        ("แก้หน้า 404",               แก้_หน้า_404),
        ("ตรวจซ้ำเนื้อหา",            ตรวจ_บทความซ้ำเนื้อหา),
        ("ตรวจ+แก้รูปซ้ำ",            ตรวจและแก้_รูปซ้ำ),        # ✅ NEW: รูปซ้ำข้ามบทความ
        ("สร้าง robots.txt",          สร้าง_robots_txt),        # ✅ v6
        ("rebuild style.css",         rebuild_style_css),       # ✅ v6: rebuild ด้วย
        ("sitemap",                   สร้าง_sitemap),
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

    if "--list-themes"   in args:
        log_section(f"🎨 ธีมทั้งหมด ({len(THEME_DEFS)} ธีม)")
        for name, label in THEME_LABELS.items():
            active = " ← (ใช้อยู่)" if name == THEME_NAME else ""
            t = THEME_DEFS[name]
            log(f"  --theme {name:<12}  {label}{active}")
        log(f"\n  ตัวอย่าง: python agent_fix_v6.py --theme dharma --layout grid")
        return
    if "--chat"          in args: รัน_chat(); return
    if "--audit"         in args: audit_ทั้งหมด(); return
    if "--stats"         in args: แสดง_สถิติ(); return
    if "--check-overlap" in args:
        log_section("🔁 ตรวจการทำงานซ้ำ — v6")
        log("  ลำดับ: agent_writer → agent_fix_v6 → agent_fix_v6 --publish")
        return
    if "--dedup" in args:
        แก้_duplicate_blocks_hard()
        rebuild_category_pages()
        rebuild_index_page()
        return
    if "--create-cats"  in args:                                  # ✅ v6 NEW
        n = สร้างหน้าหมวดที่หายไป()
        if n > 0:
            rebuild_category_pages()
        return
    if "--fix-nav"      in args: สร้าง_nav_js(); return           # ✅ v6 NEW
    if "--breadcrumb"   in args: เพิ่ม_breadcrumb(); return       # ✅ v6 NEW
    if "--fix-og"       in args: แก้_og_image(); return           # ✅ v6 NEW
    if "--reading-time" in args: เพิ่ม_reading_time(); return     # ✅ v6 NEW
    if "--robots"       in args: สร้าง_robots_txt(); return       # ✅ v6 NEW
    if "--fix-share"       in args: แก้_share_buttons(); return   # ✅ NEW
    if "--fix-instruction" in args: ลบ_instruction_หลุด(); return  # ✅ NEW
    if "--fix-css"      in args: rebuild_style_css(); return
    if "--fix-footer"   in args: แก้_footer_ทุกหน้า(); return
    if "--fix-hero"     in args: แก้_hero_ทุกหน้า(); return
    if "--fix-search"   in args: แก้_search(); return
    if "--fix-meta"     in args: แก้_meta_description(); return
    if "--fix-404"      in args: แก้_หน้า_404(); return
    if "--fix-alt"      in args: แก้_img_alt(); return
    if "--check-dup"    in args: ตรวจ_บทความซ้ำเนื้อหา(); return
    if "--check-img-dup" in args: ตรวจและแก้_รูปซ้ำ(); return   # ✅ NEW
    if "--publish"      in args:
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
