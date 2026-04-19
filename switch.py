"""
switch.py — เปลี่ยนธีม/layout ทั้งเว็บเร็วๆ ไม่รัน pipeline
ใช้: python switch.py
"""
import re, sys
from pathlib import Path

BASE = Path(r"D:\Projects\krubjang-site full")

THEMES = {
    "1":  ("blue",      "น้ำเงิน (default)",     "#1e40af", "#0f172a", "#1e3a8a", "#3b82f6"),
    "2":  ("dark",      "Dark Mode",              "#0f172a", "#020617", "#1e293b", "#475569"),
    "3":  ("green",     "เขียวเข้ม",               "#065f46", "#022c22", "#047857", "#10b981"),
    "4":  ("red",       "แดง — ข่าว บันเทิง",     "#991b1b", "#450a0a", "#b91c1c", "#ef4444"),
    "5":  ("purple",    "ม่วง — สร้างสรรค์",      "#581c87", "#2e1065", "#6b21a8", "#a855f7"),
    "6":  ("orange",    "ส้ม — อาหาร",            "#9a3412", "#431407", "#c2410c", "#f97316"),
    "7":  ("teal",      "เขียวน้ำ — เทคโนโลยี",  "#0f766e", "#042f2e", "#0d9488", "#14b8a6"),
    "8":  ("rose",      "กุหลาบ — ความงาม",       "#9f1239", "#4c0519", "#be123c", "#fb7185"),
    "9":  ("indigo",    "คราม — การเงิน",         "#3730a3", "#1e1b4b", "#4338ca", "#818cf8"),
    "10": ("amber",     "อำพัน — อบอุ่น",         "#92400e", "#451a03", "#b45309", "#fbbf24"),
    "11": ("cyan",      "ฟ้าน้ำ — สดใส",          "#155e75", "#083344", "#0e7490", "#22d3ee"),
    "12": ("sky",       "ท้องฟ้า — สดชื่น",       "#075985", "#082f49", "#0369a1", "#38bdf8"),
    "13": ("reliable",  "Navy น่าเชื่อถือ",        "#1a365d", "#0d1f3c", "#2a4a7f", "#4299e1"),
    "14": ("corporate", "Corporate มืออาชีพ",     "#1e3a5f", "#0f2340", "#2d5a9e", "#63b3ed"),
    "15": ("charcoal",  "Charcoal โมเดิร์น",      "#374151", "#111827", "#4b5563", "#9ca3af"),
    "16": ("minimal",   "Minimal สะอาด",          "#334155", "#1e293b", "#475569", "#94a3b8"),
    "17": ("calm",      "Calm สบายตา",            "#2d6a7a", "#0f3642", "#3d8fa3", "#67c8d8"),
    "18": ("zen",       "Zen ผ่อนคลาย",          "#4a7c59", "#1a3328", "#5a9c6e", "#88d4a8"),
    "19": ("sweet",     "Sweet หวาน ชมพู",        "#be185d", "#6b0f3a", "#db2777", "#f9a8d4"),
    "20": ("sakura",    "Sakura ซากุระ",          "#ad1457", "#4a0726", "#c2185b", "#f8bbd0"),
    "21": ("lavender",  "Lavender นุ่มนวล",       "#5b21b6", "#2e1065", "#7c3aed", "#ddd6fe"),
    "22": ("dharma",    "Dharma ธรรมะ ทองวัด",   "#92400e", "#3b1a06", "#b45309", "#fcd34d"),
    "23": ("monk",      "Monk จีวร พระ",          "#c05621", "#7b341e", "#dd6b20", "#f6ad55"),
    "24": ("lotus",     "Lotus บัว สมาธิ",        "#702459", "#4a044e", "#9b2c8c", "#d6a8e0"),
    "25": ("gold",      "Gold ทองคำ มงคล",        "#78350f", "#3b1a03", "#92400e", "#fbbf24"),
    "26": ("mystic",    "Mystic ลึกลับ จักรวาล", "#1e1b4b", "#0f0c2e", "#312e81", "#818cf8"),
    "27": ("horoscope", "Horoscope ดูดวง",        "#4c1d95", "#1e0a3c", "#5b21b6", "#a78bfa"),
    "28": ("cosmic",    "Cosmic ดาว อวกาศ",       "#0f172a", "#020617", "#1e1b4b", "#6366f1"),
    "29": ("midnight",  "Midnight เที่ยงคืน",     "#1e3a8a", "#0a0f2e", "#1e40af", "#60a5fa"),
    "30": ("forest",    "Forest ป่า ธรรมชาติ",   "#14532d", "#052e16", "#166534", "#4ade80"),
    "31": ("ocean",     "Ocean ทะเลลึก",          "#075985", "#0c1a35", "#0369a1", "#38bdf8"),
    "32": ("earth",     "Earth ดิน อบอุ่น",       "#713f12", "#3b1f07", "#92400e", "#d97706"),
    "33": ("spring",    "Spring ฤดูใบไม้ผลิ",    "#15803d", "#052e16", "#16a34a", "#86efac"),
    "34": ("retro",     "Retro วินเทจ ม่วง",     "#7c3aed", "#1e0a3c", "#6d28d9", "#c4b5fd"),
    "35": ("neon",      "Neon Dark นีออน",        "#0f172a", "#020617", "#1e293b", "#22d3ee"),
}

LAYOUTS = {
    "1": "grid",
    "2": "magazine", 
    "3": "list",
    "4": "masonry",
    "5": "sidebar",
    "6": "tiles",
}

def apply_theme(primary, dark, grad_end, accent):
    files = list(BASE.glob("*.html"))
    fixed = 0
    for fp in files:
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            changed = False
            # เปลี่ยน CSS variables
            if "--primary:" in txt:
                txt = re.sub(r'(--primary:\s*)#[0-9a-fA-F]{3,8}', f'\\g<1>{primary}', txt)
                changed = True
            if "--dark:" in txt:
                txt = re.sub(r'(--dark:\s*)#[0-9a-fA-F]{3,8}', f'\\g<1>{dark}', txt)
                changed = True
            if "--accent:" in txt:
                txt = re.sub(r'(--accent:\s*)#[0-9a-fA-F]{3,8}', f'\\g<1>{accent}', txt)
                changed = True
            # เปลี่ยนสี nav, hero gradient, footer
            txt = re.sub(r'(background:\s*)(#1e40af|#0f172a|#065f46|#991b1b|#581c87|#9a3412|#0f766e|#9f1239|#3730a3|#92400e|#155e75|#075985|#1a365d|#1e3a5f|#374151|#334155|#2d6a7a|#4a7c59|#be185d|#ad1457|#5b21b6|#702459|#78350f|#1e1b4b|#4c1d95|#0f172a|#1e3a8a|#14532d|#713f12|#15803d|#7c3aed|#c05621)', f'\\g<1>{primary}', txt)
            if changed or True:
                fp.write_text(txt, encoding="utf-8")
                fixed += 1
        except:
            pass
    return fixed

def main():
    print("\n" + "="*50)
    print("  🎨  SWITCH — เปลี่ยนธีม/Layout ทั้งเว็บ")
    print("="*50)
    
    print("\n📐 Layout ที่มี:")
    for k, v in LAYOUTS.items():
        print(f"  {k}. {v}")
    
    layout_choice = input("\nเลือก Layout (Enter=ข้าม): ").strip()
    
    print("\n🎨 ธีมที่มี:")
    for k, v in THEMES.items():
        print(f"  {k:2}. {v[0]:12} — {v[1]}")
    
    theme_choice = input("\nเลือกธีม (Enter=ข้าม): ").strip()
    
    if not layout_choice and not theme_choice:
        print("ไม่ได้เลือกอะไร ออกจากโปรแกรม")
        return

    if theme_choice and theme_choice in THEMES:
        t = THEMES[theme_choice]
        print(f"\n⏳ กำลังเปลี่ยนธีม: {t[0]} ({t[1]})...")
        # แก้ config ใน agent โดยตรง
        cfg = BASE / "config.py"
        if cfg.exists():
            c = cfg.read_text(encoding="utf-8", errors="ignore")
            c = re.sub(r'(THEME\s*=\s*["\'])[^"\']*(["\'])', f'\\g<1>{t[0]}\\g<2>', c)
            c = re.sub(r'(PRIMARY\s*=\s*["\'])[^"\']*(["\'])', f'\\g<1>{t[2]}\\g<2>', c)
            c = re.sub(r'(DARK\s*=\s*["\'])[^"\']*(["\'])', f'\\g<1>{t[3]}\\g<2>', c)
            cfg.write_text(c, encoding="utf-8")
        print(f"✅ เปลี่ยนธีมเป็น: {t[0]}")
        print("⚠️  รัน: python agent_fix_v6.py --fix-css เพื่อ apply สีใหม่")

    if layout_choice and layout_choice in LAYOUTS:
        layout = LAYOUTS[layout_choice]
        cfg = BASE / "config.py"
        if cfg.exists():
            c = cfg.read_text(encoding="utf-8", errors="ignore")
            c = re.sub(r'(LAYOUT\s*=\s*["\'])[^"\']*(["\'])', f'\\g<1>{layout}\\g<2>', c)
            cfg.write_text(c, encoding="utf-8")
        print(f"✅ เปลี่ยน Layout เป็น: {layout}")
        print("⚠️  รัน: python agent_fix_v6.py --fix อีกครั้งเพื่อ rebuild")

if __name__ == "__main__":
    main()
