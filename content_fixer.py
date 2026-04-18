"""
content_fixer.py — แก้ปัญหา 3 จุดหลักของเว็บ krubjang
1. รูปภาพไม่ตรงเนื้อหา (เลข 1, เลข 2, picsum มั่ว)
2. เนื้อหาบทความตื้น / มั่ว / คำสั่ง AI หลุด
3. บทความพูดนอกเรื่อง

วิธีใช้:
  python content_fixer.py --fix-content   # แก้เนื้อหาทุกบทความ
  python content_fixer.py --fix-images    # แก้รูปทุกบทความ
  python content_fixer.py --audit         # ตรวจดูปัญหาก่อนแก้
  python content_fixer.py                 # รันทุกอย่าง
"""

import sys, re, os, json, hashlib, time
from pathlib import Path
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════
# ⚙️  IMPORT จาก project เดิม
# ══════════════════════════════════════════════════════════════
try:
    from config import (
        BASE_PATH, SITE_NAME, CATEGORIES,
        CATEGORY_PAGE_MAP, หมวด_ไทย, DRY_RUN,
        log, log_ok, log_warn, log_err, log_info, log_section,
        เรียก_ollama,
    )
except ImportError as e:
    print(f"❌ import config ไม่ได้: {e}")
    print("วางไฟล์นี้ในโฟลเดอร์เดียวกับ config.py")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# 🗺️  TOPIC MAP สำหรับดึงรูปตามเนื้อหาจริง
# ══════════════════════════════════════════════════════════════
UNSPLASH_TOPICS = {
    "food":         "thai food,cooking,meal,recipe,cuisine",
    "อาหาร":        "thai food,cooking,meal",
    "health":       "healthcare,wellness,medical,doctor",
    "สุขภาพ":       "healthcare,wellness,fitness",
    "travel":       "travel,thailand,landscape,temple",
    "ท่องเที่ยว":   "travel,landscape,destination",
    "beauty":       "beauty,makeup,skincare,cosmetics",
    "ความงาม":      "beauty,makeup,skincare",
    "lifestyle":    "lifestyle,living,home,family",
    "ไลฟ์สไตล์":   "lifestyle,living,people",
    "technology":   "technology,computer,smartphone,digital",
    "เทคโนโลยี":    "technology,computer,gadget",
    "finance":      "finance,business,money,investment",
    "การเงิน":      "finance,money,banking",
    "sport":        "sport,fitness,exercise,stadium",
    "กีฬา":         "sport,fitness,athlete",
    "news":         "news,newspaper,journalism",
    "ข่าวสาร":      "news,media,journalism",
    "education":    "education,study,school,student",
    "การศึกษา":     "education,student,learning",
    "horoscope":    "stars,astrology,zodiac,moon",
    "ดูดวง":        "stars,galaxy,astrology",
    "law":          "law,justice,legal,courthouse",
    "กฎหมาย":       "courthouse,legal,justice",
    "pet":          "pet,dog,cat,animal",
    "สัตว์เลี้ยง":  "pet,dog,cat",
    "car":          "car,automobile,road,vehicle",
    "รถยนต์":       "car,automobile,vehicle",
    "real_estate":  "house,architecture,building,interior",
    "อสังหา":       "house,building,interior",
    "entertainment": "entertainment,concert,show,festival",
    "บันเทิง":      "entertainment,concert,festival",
    "gaming":       "gaming,game,esports,controller",
    "เกมมิ่ง":      "gaming,esports,game",
    "anime":        "japan,tokyo,anime,illustration",
    "cartoon":      "colorful,animation,creative",
    "movie":        "cinema,film,popcorn,movie",
    "ภาพยนตร์":     "cinema,film,movie",
}

# ══════════════════════════════════════════════════════════════
# 🖼️  ดึงรูปจริงตามหมวดหมู่และหัวข้อ
# ══════════════════════════════════════════════════════════════
def _get_relevant_image(หัวข้อ: str, หมวด: str, filename: str) -> str:
    """
    หารูปที่ตรงกับเนื้อหาจริงๆ โดยใช้ Unsplash ตาม topic
    ไม่ใช้ picsum.photos เด็ดขาด
    """
    # สร้าง seed จาก filename เพื่อให้รูปต่างกันในแต่ละบทความ
    seed = hashlib.md5(f"{filename}{หัวข้อ}".encode()).hexdigest()[:8]

    # หา topic ตามหมวด
    topic = "lifestyle,nature"
    หมวด_lower = หมวด.lower()
    หัวข้อ_lower = หัวข้อ.lower()

    for kw, t in UNSPLASH_TOPICS.items():
        if kw in หมวด_lower or kw in หัวข้อ_lower:
            topic = t
            break

    # เพิ่ม keyword จากหัวข้อให้ตรงขึ้น
    # ตัวอย่าง: "ส้มตำปูปลาร้า" → เพิ่ม "papaya salad,thai food"
    _FOOD_KW = {
        "ส้มตำ": "papaya salad,thai food",
        "ต้มยำ": "thai soup,tom yum",
        "ผัดไทย": "pad thai,noodle",
        "ข้าวผัด": "fried rice,thai food",
        "แกง": "thai curry,coconut",
        "สเต็ก": "steak,beef",
        "พิซซ่า": "pizza,italian",
        "ซูชิ": "sushi,japanese food",
        "ไก่": "chicken,grilled chicken",
        "หมู": "pork,bbq",
        "ปลา": "fish,seafood",
        "กุ้ง": "shrimp,seafood",
        "ลาบ": "thai salad,minced meat",
        "เส้น": "noodle,pasta",
        "สปาเกตตี้": "spaghetti,pasta,italian",
    }
    for kw, extra_topic in _FOOD_KW.items():
        if kw in หัวข้อ:
            topic = extra_topic
            break

    # Unsplash source URL พร้อม seed สุ่มเฉพาะบทความ
    return f"https://source.unsplash.com/featured/800x450/?{topic}&sig={seed}"


# ══════════════════════════════════════════════════════════════
# 🚫  BAD IMAGE PATTERNS — รูปที่ต้องเปลี่ยนแน่ๆ
# ══════════════════════════════════════════════════════════════
BAD_IMAGE_PATTERNS = [
    "picsum.photos",
    "placeholder",
    "og-default",
    "lorem",
    "data:image/svg",
    "/seed/",                # picsum seed pattern
    "images/thumbs/",        # SVG thumbnail
    # รูปตัวเลข / abstract ที่ไม่ตรงเนื้อหา (ตรวจจาก filename)
    "photo-1461897104016",   # รูปเลข "1" ที่โผล่บ่อย
    "photo-1542621334",      # รูป abstract มั่ว
]

def _is_bad_image(src: str) -> bool:
    if not src:
        return True
    src_lower = src.lower()
    for bad in BAD_IMAGE_PATTERNS:
        if bad in src_lower:
            return True
    # ตรวจว่าเป็น local path ที่ไม่มีไฟล์จริง
    if src.startswith("images/") and not src.startswith("http"):
        return True
    return False


# ══════════════════════════════════════════════════════════════
# 📝  PROMPT TEMPLATES — สร้างเนื้อหาบทความที่ดี
# ══════════════════════════════════════════════════════════════

def _build_content_prompt(หัวข้อ: str, หมวด: str) -> str:
    """
    สร้าง prompt ที่ดีสำหรับแต่ละประเภทเนื้อหา
    ป้องกัน AI เบี่ยงหัวข้อ / instruction หลุด
    """
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)

    # Template ตามประเภทหมวด
    if หมวด in ("food", "อาหาร", "cooking"):
        return f"""เขียนบทความสอนทำอาหารภาษาไทย เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. แนะนำเมนู (2-3 ประโยค) — บอกว่าเมนูนี้คืออะไร มาจากไหน รสชาติแบบไหน
2. วัตถุดิบ (บอกให้ครบ ระบุปริมาณชัดเจน เช่น 200 กรัม 2 ช้อนโต๊ะ)
3. วิธีทำทีละขั้นตอน (อย่างน้อย 5-7 ขั้นตอน อธิบายละเอียดทุกขั้น)
4. เคล็ดลับและข้อควรระวัง (2-3 ข้อ)
5. การเสิร์ฟและตกแต่งจาน

กฎ: เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น ห้ามพูดถึงเมนูอื่น
ตอบเป็น HTML paragraphs (<p>...</p>) และ lists (<ul><li>...</li></ul>) เท่านั้น
ห้ามมี markdown ห้ามมีหัวข้อนำ ห้ามอธิบาย meta-information"""

    elif หมวด in ("health", "สุขภาพ"):
        return f"""เขียนบทความสุขภาพภาษาไทย เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. ความสำคัญ/ปัญหา (อธิบายให้ผู้อ่านเข้าใจว่าทำไมเรื่องนี้ถึงสำคัญ)
2. สาเหตุหรือปัจจัยที่เกี่ยวข้อง (3-5 ข้อ พร้อมอธิบายแต่ละข้อ)
3. วิธีแก้ไขหรือปฏิบัติ (อย่างน้อย 5 ข้อ อธิบายละเอียด)
4. ข้อควรระวัง/เมื่อไหรควรพบแพทย์
5. สรุป

กฎ: เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น อ้างอิงข้อมูลที่เชื่อถือได้
ตอบเป็น HTML paragraphs และ lists เท่านั้น ห้ามมี markdown"""

    elif หมวด in ("travel", "ท่องเที่ยว"):
        return f"""เขียนบทความท่องเที่ยวภาษาไทย เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. แนะนำสถานที่/เส้นทาง (ตำแหน่ง ระยะทาง การเดินทาง)
2. สถานที่น่าสนใจในละแวก (3-5 ที่ พร้อมรายละเอียด)
3. ที่พักแนะนำ (ระดับราคาต่างๆ)
4. ร้านอาหาร/ของกิน (แบบ local)
5. เคล็ดลับเที่ยว (ช่วงเวลา งบประมาณ ข้อควรระวัง)
6. การเดินทางและเส้นทาง

กฎ: เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น
ตอบเป็น HTML paragraphs และ lists เท่านั้น ห้ามมี markdown"""

    elif หมวด in ("beauty", "ความงาม"):
        return f"""เขียนบทความความงามภาษาไทย เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. แนะนำและความสำคัญ
2. วิธีปฏิบัติทีละขั้นตอน (อย่างน้อย 5 ขั้น อธิบายละเอียด)
3. ผลิตภัณฑ์/อุปกรณ์ที่แนะนำ (บอก type ไม่ต้องระบุยี่ห้อ)
4. ข้อผิดพลาดที่ควรหลีกเลี่ยง
5. เคล็ดลับจากผู้เชี่ยวชาญ

กฎ: เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น
ตอบเป็น HTML paragraphs และ lists เท่านั้น ห้ามมี markdown"""

    elif หมวด in ("finance", "การเงิน"):
        return f"""เขียนบทความการเงินภาษาไทย เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. อธิบายแนวคิดหลัก (ให้เข้าใจง่าย)
2. ทำไมถึงสำคัญ / ประโยชน์ที่ได้รับ
3. วิธีเริ่มต้นหรือปฏิบัติ (step by step อย่างน้อย 5 ข้อ)
4. ข้อควรระวัง / ความเสี่ยง
5. ตัวอย่างจริงหรือกรณีศึกษา
6. สรุปและคำแนะนำ

กฎ: เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น ให้ข้อมูลที่ถูกต้อง ไม่ชี้นำลงทุน
ตอบเป็น HTML paragraphs และ lists เท่านั้น ห้ามมี markdown"""

    else:
        # Generic template สำหรับทุกหมวดที่เหลือ
        return f"""เขียนบทความภาษาไทย หมวด {หมวด_th} เรื่อง "{หัวข้อ}"

โครงสร้างที่ต้องมี:
1. บทนำ — แนะนำเรื่องให้น่าสนใจ อธิบายว่าบทความนี้พูดถึงอะไร (2-3 ประโยค)
2. เนื้อหาหลัก — อธิบายรายละเอียด ข้อมูลสำคัญ ข้อเท็จจริง (3-4 ย่อหน้า)
3. ขั้นตอนหรือวิธีปฏิบัติ (ถ้ามี) — อย่างน้อย 5 ข้อ อธิบายทุกข้อ
4. ข้อควรรู้เพิ่มเติม — เคล็ดลับหรือข้อมูลที่มักถูกมองข้าม
5. สรุป — ประเด็นสำคัญและข้อแนะนำ

กฎสำคัญ:
- เขียนเฉพาะเรื่อง "{หัวข้อ}" เท่านั้น ห้ามพูดเรื่องอื่น
- ความยาวอย่างน้อย 600 คำ
- ให้ข้อมูลจริง ละเอียด เหมือนผู้เชี่ยวชาญเขียน
- ตอบเป็น HTML paragraphs (<p>) และ lists (<ul><li>) เท่านั้น
- ห้ามมี: markdown, ##, **, คำว่า "บทนำ:", "เนื้อหา:", "สรุป:" นำหน้า
- ห้ามใส่ HTML อื่นนอกจาก p, ul, ol, li, strong, em, h2, h3"""


# ══════════════════════════════════════════════════════════════
# 🧹  ล้างผลลัพธ์จาก AI
# ══════════════════════════════════════════════════════════════
def _clean_ai_output(text: str, หัวข้อ: str) -> str:
    """
    ล้างสิ่งที่ไม่ต้องการออกจากผลลัพธ์ AI:
    - markdown (##, **, __)
    - instruction หลุด
    - ประโยคที่ไม่เกี่ยวกับหัวข้อ
    """
    if not text:
        return ""

    # ── ลบ markdown ──────────────────────────────────────────
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # ## header
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)  # **bold**
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)  # *italic*
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.+?)`', r'\1', text)  # `code`

    # ── ลบ instruction ที่หลุดมา ─────────────────────────────
    LEAK_PATTERNS = [
        r'^\s*(กฎ|กฎ:|กฎสำคัญ|สไตล์บังคับ|สไตล์สำหรับ|ประเด็นหลัก|ขอเนื้อหา)[^\n]{0,300}$',
        r'^\s*(เขียน Markdown|ห้าม HTML|num_predict|temperature)[^\n]{0,300}$',
        r'^\s*-\s*(เขียน|ห้าม|ใส่|สลับ|ตอบ|Reply)[^\n]{0,300}$',
        r'^\s*\d+\.\s*(ห้าม|เขียน Markdown|ความยาว)[^\n]{0,300}$',
        r'^\s*(โครงสร้าง|ต้องมี|template)[^\n]{0,300}$',
        r'^\s*ตอบเป็น[^\n]{0,200}$',
        r'^\s*HTML paragraph[^\n]{0,200}$',
    ]
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        is_leak = any(re.match(p, line, re.IGNORECASE) for p in LEAK_PATTERNS)
        if not is_leak:
            clean_lines.append(line)
    text = '\n'.join(clean_lines)

    # ── แปลง markdown list → HTML list ──────────────────────
    # ถ้ายังมี "- item" หลงเหลือ → แปลงเป็น HTML
    if re.search(r'^\s*[-*]\s+', text, re.MULTILINE):
        def _convert_list(text):
            lines = text.split('\n')
            result = []
            in_list = False
            for line in lines:
                m = re.match(r'^\s*[-*]\s+(.+)', line)
                if m:
                    if not in_list:
                        result.append('<ul>')
                        in_list = True
                    result.append(f'<li>{m.group(1)}</li>')
                else:
                    if in_list:
                        result.append('</ul>')
                        in_list = False
                    result.append(line)
            if in_list:
                result.append('</ul>')
            return '\n'.join(result)
        text = _convert_list(text)

    # ── แปลง numbered list → HTML ──────────────────────────
    if re.search(r'^\s*\d+\.\s+', text, re.MULTILINE):
        def _convert_ol(text):
            lines = text.split('\n')
            result = []
            in_list = False
            for line in lines:
                m = re.match(r'^\s*\d+\.\s+(.+)', line)
                if m:
                    if not in_list:
                        result.append('<ol>')
                        in_list = True
                    result.append(f'<li>{m.group(1)}</li>')
                else:
                    if in_list:
                        result.append('</ol>')
                        in_list = False
                    result.append(line)
            if in_list:
                result.append('</ol>')
            return '\n'.join(result)
        text = _convert_ol(text)

    # ── ห่อ plain text ด้วย <p> ─────────────────────────────
    # ถ้า block ไหนไม่มี HTML tag ให้ห่อด้วย <p>
    paragraphs = re.split(r'\n{2,}', text.strip())
    wrapped = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # ถ้าไม่มี HTML tag เลย → ห่อด้วย <p>
        if not re.search(r'<[a-z]', para, re.IGNORECASE):
            if len(para) > 10:
                wrapped.append(f'<p>{para}</p>')
        else:
            wrapped.append(para)
    text = '\n'.join(wrapped)

    # ── ตรวจว่าเนื้อหาตรงหัวข้อ (basic check) ─────────────
    # ถ้าหัวข้อบอกอาหาร A แต่เนื้อหาพูดถึงอาหาร B → flag
    # (ทำได้แค่ basic เพราะไม่มี vision)

    return text.strip()


# ══════════════════════════════════════════════════════════════
# 🔍  SCAN ARTICLES
# ══════════════════════════════════════════════════════════════
_SKIP_DIRS = {"node_modules",".git",".vercel","__pycache__","dist","build",".next"}
_NON_ARTICLE_NAMES = {
    "index.html","404.html","contact.html","sitemap.html",
    "privacy.html","video.html","shopping.html","lotto.html",
    "style.css","nav.js","robots.txt","sitemap.xml",
}
_NON_ARTICLE_NAMES |= set(CATEGORY_PAGE_MAP.values())

def _scan_articles():
    result = []
    for fp in sorted(BASE_PATH.rglob("*")):
        if any(s in fp.parts for s in _SKIP_DIRS):
            continue
        if (fp.suffix.lower() == ".html" and
                fp.is_file() and
                fp.parent == BASE_PATH and
                fp.name not in _NON_ARTICLE_NAMES):
            try:
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                if "<html" in txt.lower() and len(txt) > 100:
                    result.append(fp)
            except Exception:
                pass
    return result


def _get_title(soup, fp) -> str:
    h1 = soup.find("h1")
    if h1 and h1.get_text().strip():
        return h1.get_text().strip()
    t = soup.find("title")
    if t:
        return re.split(r'\s*[—|–|-]\s*', t.get_text().strip())[0].strip()
    return fp.stem.replace("_"," ").replace("-"," ").title()


def _get_cat(fp) -> str:
    return fp.stem.split("_")[0] if "_" in fp.stem else fp.stem


def _get_main_img(soup) -> str:
    for cls in ["hero-image-wrapper","hero-image","article-hero","featured-image"]:
        sec = soup.find(class_=cls)
        if sec:
            img = sec.find("img")
            if img:
                s = img.get("src","").strip()
                if s:
                    return s
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"].strip()
    img = soup.find("img")
    if img:
        return img.get("src","").strip()
    return ""


# ══════════════════════════════════════════════════════════════
# 🎯  AUDIT — ตรวจปัญหาก่อนแก้
# ══════════════════════════════════════════════════════════════
def audit():
    log_section("🔍 AUDIT — ตรวจปัญหาบทความ")
    articles = _scan_articles()
    log_info(f"บทความทั้งหมด: {len(articles)} ไฟล์")

    # Instruction patterns ที่ไม่ควรอยู่ในเนื้อหา
    LEAK_KW = [
        "สไตล์บังคับ","สไตล์สำหรับ section","ประเด็นหลัก:","ขอเนื้อหาส่วน",
        "เขียน Markdown","ห้าม HTML","num_predict","temperature",
        "กฎ:","กฎสำคัญ:","Reply with keywords","โครงสร้างที่ต้องมี",
    ]

    issues = {
        "รูปไม่ตรง/picsum":    [],
        "เนื้อหาสั้น (<400 ตัว)": [],
        "instruction หลุด":     [],
        "ย่อหน้าซ้ำ":          [],
        "ไม่มีรูปเลย":          [],
    }

    for fp in articles:
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(txt, "html.parser")

            # ตรวจรูป
            src = _get_main_img(soup)
            if not src:
                issues["ไม่มีรูปเลย"].append(fp.name)
            elif _is_bad_image(src):
                issues["รูปไม่ตรง/picsum"].append(f"{fp.name} ({src[:50]})")

            # ตรวจเนื้อหา
            body = (soup.find(class_="article-body") or
                    soup.find("article") or soup.find("main"))
            text = body.get_text("\n", strip=True) if body else ""

            if len(text) < 400:
                issues["เนื้อหาสั้น (<400 ตัว)"].append(f"{fp.name} ({len(text)} ตัว)")

            if any(kw in text for kw in LEAK_KW):
                found = [kw for kw in LEAK_KW if kw in text]
                issues["instruction หลุด"].append(f"{fp.name}: {', '.join(found[:2])}")

            # ตรวจย่อหน้าซ้ำ
            paras = [p.strip() for p in text.split("\n") if len(p.strip()) > 80]
            seen = set()
            for p in paras:
                key = p[:100]
                if key in seen:
                    issues["ย่อหน้าซ้ำ"].append(fp.name)
                    break
                seen.add(key)

        except Exception as e:
            log_err(f"  audit {fp.name}: {e}")

    # สรุปผล
    total_issues = 0
    log("\n📊 สรุปปัญหา:")
    for k, v in issues.items():
        icon = "✅" if not v else "❌"
        unique_v = list(set(v))
        log(f"  {icon} {k}: {len(unique_v)} ไฟล์")
        for x in unique_v[:5]:
            log(f"       - {x}")
        if len(unique_v) > 5:
            log(f"       ... และอีก {len(unique_v)-5} ไฟล์")
        total_issues += len(unique_v)

    log(f"\n  รวมปัญหา: {total_issues} รายการ")
    return issues


# ══════════════════════════════════════════════════════════════
# 🖼️  FIX IMAGES — แก้รูปทุกบทความ
# ══════════════════════════════════════════════════════════════
def fix_images():
    log_section("🖼️  Fix Images — เปลี่ยนรูปไม่ตรงเนื้อหา")
    articles = _scan_articles()
    fixed = 0

    for fp in articles:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")

            title = _get_title(soup, fp)
            cat = _get_cat(fp)
            src = _get_main_img(soup)

            if not _is_bad_image(src):
                continue  # รูปโอเคแล้ว

            new_src = _get_relevant_image(title, cat, fp.stem)

            # Replace ใน HTML
            html = orig
            if src:
                html = html.replace(f'src="{src}"', f'src="{new_src}"', 1)
                if src in html:
                    html = html.replace(src, new_src, 1)
            else:
                # ไม่มีรูปเลย → เพิ่ม img ใน hero section
                hero_insert = (
                    f'<div class="hero-image-wrapper" style="margin-bottom:1.5rem;">'
                    f'<img src="{new_src}" alt="{title}" loading="lazy" '
                    f'style="width:100%;max-height:480px;object-fit:cover;border-radius:12px;"'
                    f' onerror="this.onerror=null;this.src=\'https://picsum.photos/seed/{fp.stem}/800/450\'">'
                    f'</div>'
                )
                html = re.sub(
                    r'(class=["\']article-body["\'][^>]*>)',
                    r'\1\n' + hero_insert,
                    html, count=1
                )

            # อัปเดต og:image ด้วย
            html = re.sub(
                r'(property="og:image"\s+content=")[^"]*(")',
                lambda m: m.group(1) + new_src + m.group(2),
                html, count=1
            )

            if html != orig:
                if not DRY_RUN:
                    fp.write_text(html, encoding="utf-8")
                log_ok(f"  ✅ {fp.name}: รูปใหม่ → [{cat}] {title[:30]}")
                fixed += 1

        except Exception as e:
            log_err(f"  fix-img {fp.name}: {e}")

    log_ok(f"\nแก้รูป: {fixed} ไฟล์")
    return fixed


# ══════════════════════════════════════════════════════════════
# 📝  FIX CONTENT — แก้เนื้อหาทุกบทความ
# ══════════════════════════════════════════════════════════════

def _has_instruction_leak(text: str) -> bool:
    LEAK_KW = [
        "สไตล์บังคับ","สไตล์สำหรับ section","ประเด็นหลัก:","ขอเนื้อหาส่วน",
        "เขียน Markdown","ห้าม HTML","num_predict","temperature",
        "กฎ:","กฎสำคัญ:","Reply with keywords","โครงสร้างที่ต้องมี",
        "ตอบเป็น HTML","HTML paragraph","ห้ามมี markdown",
    ]
    return any(kw in text for kw in LEAK_KW)


def _is_content_offtrack(title: str, text: str) -> bool:
    """
    ตรวจว่าเนื้อหาเบี่ยงออกจากหัวข้อหรือไม่
    โดยเช็ค keyword หลักจากหัวข้อว่าปรากฏในเนื้อหาบ้างไหม
    """
    if not text or len(text) < 100:
        return True

    # ดึง keyword หลักจากหัวข้อ (คำที่ยาว > 3 ตัวอักษร)
    title_words = set(re.findall(r'[ก-๙a-zA-Z]{3,}', title.lower()))
    if not title_words:
        return False

    text_lower = text.lower()
    # ถ้าคำจากหัวข้ออย่างน้อย 1 คำอยู่ในเนื้อหา → น่าจะตรง
    matches = sum(1 for w in title_words if w in text_lower)
    return matches == 0


def fix_content(force_rewrite: bool = False):
    """
    แก้เนื้อหาบทความ:
    - ล้าง instruction หลุด
    - ลบย่อหน้าซ้ำ
    - เขียนใหม่ถ้าเนื้อหาสั้นหรือผิดหัวข้อ (เฉพาะเมื่อ force_rewrite=True)
    """
    log_section("📝 Fix Content — แก้เนื้อหาบทความ")
    articles = _scan_articles()
    fixed = 0
    skipped = 0

    for fp in articles:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            title = _get_title(soup, fp)
            cat = _get_cat(fp)

            body = (soup.find(class_="article-body") or
                    soup.find("article") or soup.find("main"))
            if not body:
                skipped += 1
                continue

            text = body.get_text("\n", strip=True)
            html = orig
            changed = False

            # ── 1. ล้าง instruction หลุด ──────────────────────
            if _has_instruction_leak(text):
                log_info(f"  🧹 ล้าง instruction: {fp.name}")
                LEAK_PATTERNS = [
                    r'<p>\s*(?:กฎ|กฎ:|กฎสำคัญ|สไตล์บังคับ|สไตล์สำหรับ|ประเด็นหลัก)[^<]{0,400}</p>',
                    r'<p>\s*(?:เขียน Markdown|ห้าม HTML|num_predict|temperature)[^<]{0,300}</p>',
                    r'<p>\s*ตอบเป็น HTML[^<]{0,300}</p>',
                    r'<p>\s*HTML paragraph[^<]{0,300}</p>',
                    r'<p>\s*โครงสร้างที่ต้องมี[^<]{0,300}</p>',
                    r'<p>\s*ห้ามมี[^<]{0,300}</p>',
                    r'<p>\s*Reply with keywords[^<]{0,300}</p>',
                    r'<li>\s*ห้าม[^<]{0,200}</li>',
                    r'<h[23][^>]*>\s*ย่อหน้า(?:ที่)?\s*\d+[^<]*</h[23]>',
                ]
                for pat in LEAK_PATTERNS:
                    new_html = re.sub(pat, '', html, flags=re.IGNORECASE | re.DOTALL)
                    if new_html != html:
                        html = new_html
                        changed = True

            # ── 2. ลบย่อหน้าซ้ำ ─────────────────────────────
            seen_p = set()
            def _dedup_p(m):
                content = m.group(1).strip()
                key = content[:120]
                if len(content) > 80 and key in seen_p:
                    return ""
                seen_p.add(key)
                return m.group(0)
            new_html = re.sub(
                r'<p[^>]*>(.*?)</p>',
                _dedup_p, html,
                flags=re.DOTALL | re.IGNORECASE
            )
            if new_html != html:
                html = new_html
                changed = True

            # ── 3. เขียนเนื้อหาใหม่ถ้าสั้นหรือผิดหัวข้อ ─────
            current_text = BeautifulSoup(html, "html.parser")
            current_body = (current_text.find(class_="article-body") or
                           current_text.find("article") or current_text.find("main"))
            current_text_content = current_body.get_text(strip=True) if current_body else ""

            needs_rewrite = (
                force_rewrite or
                len(current_text_content) < 400 or
                _is_content_offtrack(title, current_text_content)
            )

            if needs_rewrite:
                log_info(f"  ✍️  เขียนใหม่: {fp.name} — {title[:40]}")
                prompt = _build_content_prompt(title, cat)
                new_content = เรียก_ollama(
                    prompt,
                    num_predict=1200,
                    temperature=0.3,  # ต่ำ = ตรงประเด็นกว่า
                )

                if new_content and len(new_content.strip()) > 200:
                    clean_content = _clean_ai_output(new_content, title)

                    if clean_content and len(clean_content) > 200:
                        # แทนที่เนื้อหาใน body
                        if current_body:
                            # เก็บ tag เปิด/ปิดของ body ไว้
                            body_tag_open = re.search(
                                r'<(?:div[^>]+class=["\'][^"\']*article-body[^"\']*["\'][^>]*|article[^>]*|main[^>]*)>',
                                html, re.IGNORECASE
                            )
                            if body_tag_open:
                                tag_name = body_tag_open.group(0)
                                # หา closing tag
                                tag_elem_name = re.match(r'<(\w+)', tag_name).group(1)
                                # Replace content ด้วย regex
                                pattern = re.compile(
                                    rf'({re.escape(tag_name)})(.*?)(</\s*{tag_elem_name}\s*>)',
                                    re.DOTALL | re.IGNORECASE
                                )
                                html = pattern.sub(
                                    lambda m: m.group(1) + '\n' + clean_content + '\n' + m.group(3),
                                    html, count=1
                                )
                                changed = True
                                log_ok(f"  ✅ เขียนใหม่: {fp.name} ({len(clean_content)} ตัว)")
                        else:
                            log_warn(f"  ไม่พบ article-body: {fp.name}")
                    else:
                        log_warn(f"  เนื้อหาหลัง clean สั้นไป: {fp.name}")
                else:
                    log_warn(f"  AI ตอบสั้นหรือว่าง: {fp.name} (ได้ {len(new_content or '')} ตัว)")

            if changed:
                if not DRY_RUN:
                    fp.write_text(html, encoding="utf-8")
                fixed += 1
            else:
                skipped += 1

        except Exception as e:
            log_err(f"  fix-content {fp.name}: {e}")

    log_ok(f"\nแก้เนื้อหา: {fixed} ไฟล์ | ข้าม: {skipped} ไฟล์")
    return fixed


# ══════════════════════════════════════════════════════════════
# 🎯  FIX INSTRUCTION ONLY — ล้าง instruction หลุดเท่านั้น (เร็ว)
# ══════════════════════════════════════════════════════════════
def fix_instruction_leak():
    log_section("🧹 Fix Instruction Leak — ล้างคำสั่ง AI หลุด")
    articles = _scan_articles()
    fixed = 0

    LEAK_PATTERNS = [
        r'<p>\s*(?:กฎ|กฎ:|กฎสำคัญ|สไตล์บังคับ|สไตล์สำหรับ|ประเด็นหลัก)[^<]{0,500}</p>',
        r'<p>\s*(?:เขียน Markdown|ห้าม HTML|num_predict|temperature)[^<]{0,400}</p>',
        r'<p>\s*ตอบเป็น HTML[^<]{0,400}</p>',
        r'<p>\s*HTML paragraph[^<]{0,400}</p>',
        r'<p>\s*โครงสร้างที่ต้องมี[^<]{0,400}</p>',
        r'<p>\s*ห้ามมี[^<]{0,300}</p>',
        r'<p>\s*Reply with keywords[^<]{0,300}</p>',
        r'<p>\s*กฎ\s*</p>',
        r'<li>\s*ห้าม[^<]{0,200}</li>',
        r'<h[23][^>]*>\s*ย่อหน้า(?:ที่)?\s*\d+[^<]*</h[23]>',
        r'<p>\s*#{2,5}\s*[^<]{0,300}</p>',
    ]

    for fp in articles:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            for pat in LEAK_PATTERNS:
                html = re.sub(pat, '', html, flags=re.IGNORECASE | re.DOTALL)
            if html != orig:
                if not DRY_RUN:
                    fp.write_text(html, encoding="utf-8")
                log_ok(f"  ✅ {fp.name}")
                fixed += 1
        except Exception as e:
            log_err(f"  leak {fp.name}: {e}")

    log_ok(f"ล้าง instruction: {fixed} ไฟล์")
    return fixed


# ══════════════════════════════════════════════════════════════
# 🚀  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    args = sys.argv[1:]

    if "--audit" in args:
        audit()
        return

    if "--fix-images" in args:
        fix_images()
        return

    if "--fix-instruction" in args:
        fix_instruction_leak()
        return

    if "--fix-content" in args:
        force = "--force" in args
        fix_content(force_rewrite=force)
        return

    if "--fix-content-force" in args:
        fix_content(force_rewrite=True)
        return

    if "--help" in args or "-h" in args:
        print("""
content_fixer.py — แก้ปัญหาเนื้อหาและรูปภาพ

วิธีใช้:
  python content_fixer.py                     # รันทุกอย่าง (audit + fix-images + fix-instruction)
  python content_fixer.py --audit              # ตรวจดูปัญหาก่อน ไม่แก้ใดๆ
  python content_fixer.py --fix-images         # แก้รูปภาพไม่ตรง/picsum เท่านั้น
  python content_fixer.py --fix-instruction    # ล้าง instruction หลุดเท่านั้น (เร็ว)
  python content_fixer.py --fix-content        # แก้เนื้อหา (ล้าง + เขียนใหม่ถ้าสั้น)
  python content_fixer.py --fix-content --force  # เขียนทับทุกบทความใหม่หมด

หมายเหตุ:
  --force ใช้เวลานานมาก (ขึ้นกับจำนวนบทความ)
  แนะนำรัน --audit ก่อน แล้วค่อยรัน --fix-images และ --fix-instruction
""")
        return

    # DEFAULT: รันทุกอย่าง (ยกเว้น force-rewrite)
    log_section("🚀 Content Fixer — รันทุกอย่าง")
    log_info("ขั้น 1/3: Audit")
    issues = audit()

    log_info("\nขั้น 2/3: แก้รูปภาพ")
    fix_images()

    log_info("\nขั้น 3/3: ล้าง instruction หลุด + แก้เนื้อหาสั้น")
    fix_content(force_rewrite=False)

    log_section("✅ เสร็จแล้ว!")
    log_info("ถ้ายังมีบทความมั่วรัน: python content_fixer.py --fix-content --force")
    log_info("(แต่ใช้เวลานาน AI จะเขียนทับทุกบทความ)")


if __name__ == "__main__":
    main()
