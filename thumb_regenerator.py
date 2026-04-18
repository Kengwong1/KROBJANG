"""
thumb_regenerator.py — สร้าง SVG thumbnail ใหม่ที่ใช้รูปจริงจาก Pexels

วิธีใช้:
  python thumb_regenerator.py            แก้ทุกไฟล์
  python thumb_regenerator.py --dry-run  ทดสอบไม่เขียนไฟล์
  python thumb_regenerator.py --file beauty_1776347150.html
"""

import sys, re, hashlib
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from config import (
        BASE_PATH, CATEGORY_PAGE_MAP,
        log, log_ok, log_warn, log_err, log_info, log_section,
    )
    DRY_RUN = "--dry-run" in sys.argv
except ImportError as e:
    print(f"❌ import config ไม่ได้: {e}")
    sys.exit(1)

# ── copy KEYWORD_MAP และ PEXELS_POOL จาก image_replacer_v4 ──────────────────
KEYWORD_MAP = [
    ("สวนสมุนไพร",    "herb garden medicinal plants"),
    ("สมุนไพร",       "herbs medicinal plants garden"),
    ("กระเพรา",       "holy basil thai herbs"),
    ("ตะไคร้",        "lemongrass thai herb"),
    ("ใบเตย",         "pandan leaf thai herb"),
    ("มะกรูด",        "kaffir lime thai herb"),
    ("ส้มตำ",         "papaya salad thai food"),
    ("ต้มยำกุ้ง",     "tom yum shrimp soup"),
    ("ต้มยำ",         "tom yum thai soup"),
    ("ต้มข่า",        "coconut soup thai food"),
    ("ผัดกะเพรา",     "basil stir fry thai"),
    ("ผัดไทย",        "pad thai noodle"),
    ("ข้าวผัด",       "fried rice thai food"),
    ("แกงเขียวหวาน",  "thai green curry"),
    ("แกงแดง",        "thai red curry"),
    ("แกงกะหรี่",     "curry food"),
    ("แกง",           "thai curry coconut"),
    ("ลาบ",           "thai minced salad"),
    ("น้ำพริก",       "thai chili dip"),
    ("ยำ",            "thai spicy salad"),
    ("หมูกระทะ",      "korean bbq pork"),
    ("ไก่ทอด",        "fried chicken crispy"),
    ("ไก่ย่าง",       "grilled chicken bbq"),
    ("ปลาทอด",        "fried fish golden"),
    ("กุ้งทอด",       "fried shrimp"),
    ("สเต็ก",         "beef steak grilled"),
    ("พิซซ่า",        "pizza italian food"),
    ("สปาเกตตี้",     "spaghetti pasta"),
    ("พาสต้า",        "pasta italian food"),
    ("ราเมง",         "ramen japanese noodle"),
    ("ซูชิ",          "sushi japanese food"),
    ("เบอร์เกอร์",    "burger fast food"),
    ("ก๋วยเตี๋ยว",    "noodle soup bowl"),
    ("บะหมี่",        "egg noodle chinese"),
    ("ขนมไทย",        "thai dessert sweets"),
    ("เค้ก",          "cake bakery dessert"),
    ("คุกกี้",        "cookie bakery"),
    ("ไอศกรีม",       "ice cream dessert"),
    ("กาแฟ",          "coffee cafe drink"),
    ("ชา",            "tea cup beverage"),
    ("น้ำผลไม้",      "fruit juice fresh"),
    ("สมูทตี้",       "smoothie healthy drink"),
    ("ไก่",           "chicken food cooking"),
    ("หมู",           "pork food cooking"),
    ("เนื้อ",         "beef meat grilled"),
    ("ปลา",           "fish seafood cooking"),
    ("กุ้ง",          "shrimp seafood"),
    ("ปู",            "crab seafood"),
    ("ผัก",           "vegetables fresh"),
    ("ผลไม้",         "fresh fruit"),
    ("ทำอาหาร",       "cooking kitchen food"),
    ("สูตรอาหาร",     "recipe cooking"),
    ("วิธีทำ",        "cooking recipe"),
    ("ออกกำลังกาย",   "exercise fitness workout gym"),
    ("วิ่ง",          "running jogging fitness"),
    ("โยคะ",          "yoga meditation wellness"),
    ("นอนหลับ",       "sleep rest bed"),
    ("ลดน้ำหนัก",     "weight loss diet fitness"),
    ("เบาหวาน",       "diabetes health medical"),
    ("ความดัน",       "blood pressure health"),
    ("หัวใจ",         "heart health medical"),
    ("มะเร็ง",        "cancer medical health"),
    ("ผิวหนัง",       "skin dermatology"),
    ("ฟัน",           "dental teeth smile"),
    ("สายตา",         "eye vision health"),
    ("ภูมิแพ้",       "allergy medical"),
    ("วิตามิน",       "vitamins supplements"),
    ("โภชนาการ",      "nutrition healthy food"),
    ("สุขภาพจิต",     "mental health wellness"),
    ("ความเครียด",    "stress relief calm"),
    ("นวด",           "massage therapy"),
    ("สปา",           "spa wellness"),
    ("ลิปสติก",       "lipstick makeup cosmetics"),
    ("อายแชโดว์",     "eyeshadow eye makeup"),
    ("มาสคาร่า",      "mascara eyelash makeup"),
    ("ไลเนอร์",       "eyeliner eye makeup"),
    ("เซรั่ม",        "serum skincare bottle"),
    ("ครีมกันแดด",    "sunscreen skincare"),
    ("มอยเจอร์ไรเซอร์","moisturizer face cream"),
    ("ครีม",          "face cream skincare"),
    ("มาสก์หน้า",     "face mask skincare"),
    ("สกินแคร์",      "skincare beauty routine"),
    ("ทรงผม",         "hairstyle hair woman"),
    ("ย้อมผม",        "hair color dye"),
    ("เล็บ",          "nail art manicure"),
    ("แต่งหน้า",      "makeup beauty woman"),
    ("ผม",            "hair beauty woman"),
    ("น้ำหอม",        "perfume fragrance"),
    ("เชียงใหม่",     "chiang mai thailand temple mountain"),
    ("เชียงราย",      "chiang rai thailand"),
    ("ภูเก็ต",        "phuket thailand beach"),
    ("กระบี่",        "krabi thailand sea cliff"),
    ("พัทยา",         "pattaya thailand beach"),
    ("กรุงเทพ",       "bangkok thailand city"),
    ("เกาะสมุย",      "koh samui thailand island"),
    ("เกาะ",          "island tropical beach"),
    ("ดอยอินทนนท์",   "doi inthanon mountain"),
    ("ปาย",           "pai thailand mountain"),
    ("ญี่ปุ่น",       "japan tokyo travel"),
    ("โตเกียว",       "tokyo japan city"),
    ("เกาหลี",        "south korea seoul"),
    ("ยุโรป",         "europe travel city"),
    ("น้ำตก",         "waterfall nature"),
    ("ภูเขา",         "mountain landscape"),
    ("วัด",           "buddhist temple thailand"),
    ("โรงแรม",        "hotel resort luxury"),
    ("คาเฟ่",         "cafe coffee shop"),
    ("ตลาดน้ำ",       "floating market thailand"),
    ("ท่องเที่ยว",    "travel adventure landscape"),
    ("ไอโฟน",         "iphone apple smartphone"),
    ("ซัมซุง",        "samsung galaxy smartphone"),
    ("มือถือ",        "smartphone mobile phone"),
    ("แล็ปท็อป",      "laptop computer"),
    ("คอมพิวเตอร์",   "computer desk tech"),
    ("AI",            "artificial intelligence tech"),
    ("หุ่นยนต์",      "robot automation technology"),
    ("โดรน",          "drone flying technology"),
    ("เกม",           "gaming esports computer"),
    ("หุ้น",          "stock market trading"),
    ("กองทุน",        "mutual fund investment"),
    ("คริปโต",        "cryptocurrency bitcoin"),
    ("บิตคอยน์",      "bitcoin crypto"),
    ("ธนาคาร",        "bank finance building"),
    ("เงินออม",       "savings money bank"),
    ("ลงทุน",         "investment money growth"),
    ("ประกัน",        "insurance finance"),
    ("ภาษี",          "tax document finance"),
    ("ฟุตบอล",        "football soccer"),
    ("บาสเกตบอล",     "basketball sport"),
    ("เทนนิส",        "tennis sport"),
    ("มวยไทย",        "muay thai boxing"),
    ("มวย",           "boxing martial arts"),
    ("ว่ายน้ำ",       "swimming pool sport"),
    ("จักรยาน",       "cycling bicycle"),
    ("ตกแต่งบ้าน",    "home interior design"),
    ("ห้องนอน",       "bedroom interior"),
    ("ห้องครัว",      "kitchen interior"),
    ("ห้องน้ำ",       "bathroom interior"),
    ("คอนโด",         "apartment condominium"),
    ("บ้านสวน",       "garden house green"),
    ("สุนัข",         "dog pet cute"),
    ("แมว",           "cat pet cute"),
    ("สัตว์เลี้ยง",   "pet animal"),
    ("รถยนต์",        "car automobile road"),
    ("แฟชั่น",        "fashion clothing style"),
    ("หนังสือ",       "book reading"),
    ("ดนตรี",         "music instrument"),
    ("ภาพยนตร์",      "movie cinema film"),
    ("ซีรีส์เกาหลี",  "korean drama series"),
    ("ซีรีส์",        "drama series show"),
    ("อนิเมะ",        "anime japan illustration"),
    ("การ์ตูน",       "cartoon animation"),
    ("คอนเสิร์ต",     "concert music show"),
    ("โหราศาสตร์",    "astrology zodiac stars"),
    ("ดูดวง",         "astrology stars cosmos"),
    ("ราศี",          "zodiac horoscope"),
    ("ไพ่ทาโร่",      "tarot card mystical"),
    ("กฎหมาย",        "law justice courthouse"),
    ("บ้านจัดสรร",    "house residential"),
    ("อสังหา",        "real estate house"),
    ("ภาษาอังกฤษ",    "english learning study"),
    ("สอบ",           "exam test study"),
    ("มหาวิทยาลัย",   "university campus"),
]

CATEGORY_FALLBACK = {
    "food":           "thai food cooking meal",
    "beauty":         "beauty skincare makeup woman",
    "health":         "health wellness fitness",
    "travel":         "travel landscape destination",
    "technology":     "technology smartphone computer",
    "finance":        "finance money investment",
    "sport":          "sport fitness exercise",
    "lifestyle":      "lifestyle home living",
    "news":           "news journalism media",
    "education":      "education student learning",
    "entertainment":  "entertainment concert show",
    "horoscope":      "astrology stars cosmos",
    "law":            "law justice legal",
    "pet":            "pet dog cat animal",
    "car":            "car automobile road",
    "real_estate":    "house architecture property",
    "cartoon":        "illustration colorful creative",
    "anime":          "anime japan illustration",
    "gaming":         "gaming esports game",
    "movie":          "cinema film movie",
    "business":       "business office professional",
    "drama":          "drama theater story",
    "story":          "book story reading",
    "folktale":       "folklore traditional story",
    "inspirational":  "motivation success inspiring",
}

PEXELS_POOL = {
    "herb garden medicinal plants": [6231905, 1084542, 906150, 4750274, 4750270],
    "herbs medicinal plants garden": [1084542, 6231905, 906150, 4750274, 3872373],
    "holy basil thai herbs":        [1254705, 4503273, 4750274, 6231905, 3872373],
    "papaya salad thai food":       [1640777, 1640769, 958545],
    "tom yum shrimp soup":          [1640777, 958545, 2313686],
    "tom yum thai soup":            [2313686, 1640777, 958545],
    "thai food cooking meal":       [1640777, 958545, 2313686, 1640769],
    "cooking kitchen food":         [2696064, 958545, 1640777],
    "fried chicken crispy":         [2313686, 1640777, 958545],
    "pork food cooking":            [1640769, 958545, 2313686],
    "noodle soup bowl":             [958545, 2313686, 1640777],
    "beef steak grilled":           [1639557, 2313686, 958545],
    "exercise fitness workout gym": [1552242, 841130, 4498318],
    "running jogging fitness":      [2827392, 1552242, 841130],
    "yoga meditation wellness":     [1552252, 317157, 4498318],
    "health wellness fitness":      [1552242, 841130, 4498318],
    "weight loss diet fitness":     [4498318, 1552242, 841130],
    "sleep rest bed":               [1603001, 271897, 1028741],
    "skin dermatology":             [3762875, 3762874, 2253879],
    "face cream skincare":          [3762875, 3762874, 3785170],
    "serum skincare bottle":        [3762875, 3785170, 3762874],
    "skincare beauty routine":      [3785170, 3762875, 2253879],
    "makeup beauty woman":          [2253879, 3762875, 1036623],
    "hairstyle hair woman":         [1036623, 3762875, 2253879],
    "hair beauty woman":            [1036623, 2253879, 3762875],
    "lipstick makeup cosmetics":    [2253879, 1036623, 3762875],
    "beauty skincare makeup woman": [3762875, 2253879, 3785170],
    "chiang mai thailand temple mountain": [1850595, 2412608, 2193300],
    "phuket thailand beach":        [1850595, 2193300, 3155658],
    "bangkok thailand city":        [1850595, 3155658, 2193300],
    "travel adventure landscape":   [1591382, 1850595, 1559388],
    "travel landscape destination": [1559388, 1591382, 1850595],
    "japan tokyo travel":           [1591382, 1850595, 1559388],
    "smartphone mobile phone":      [607812, 3568059, 1092671],
    "laptop computer":              [1181243, 574071, 3568059],
    "technology smartphone computer": [3568059, 607812, 1092671],
    "artificial intelligence tech": [8386434, 3568059, 1181243],
    "stock market trading":         [6801648, 6802038, 6801694],
    "investment money growth":      [6801648, 6802038, 3943723],
    "finance money investment":     [6802038, 6801648, 3943723],
    "football soccer":              [274422, 1884574, 46798],
    "home interior design":         [1571460, 1648776, 1643383],
    "bedroom interior":             [1648776, 1571460, 271816],
    "kitchen interior":             [1080721, 1571460, 2062426],
    "lifestyle home living":        [1571460, 1643383, 1648776],
    "dog pet cute":                 [1108099, 2253879, 1805164],
    "cat pet cute":                 [1741205, 208984, 1108099],
    "car automobile road":          [112460, 1638459, 3802510],
    "movie cinema film":            [7234138, 1117132, 3945317],
    "cinema film movie":            [7234138, 1117132, 3945317],
    "astrology stars cosmos":       [1169754, 3617534, 2150],
    # เรื่องเล่า/นิทาน
    "book story reading":           [256450, 159711, 415071, 694740, 1370295],
    "folklore traditional story":   [1770809, 256450, 415071, 694740, 159711],
    "drama theater story":          [3621774, 1770809, 2774556, 1179617, 256450],
    "drama series show":            [3621774, 2774556, 1117132, 1179617, 7234138],
    # ข่าว/สื่อ
    "news journalism media":        [3944405, 3760072, 3760529, 1055379, 1591382],
    # แรงบันดาลใจ
    "motivation success inspiring": [1535244, 3760072, 1486233, 1170986, 3184291],
    # ธุรกิจ
    "business office professional": [3184291, 1181671, 3760072, 1170986, 3760529],
    # การศึกษา
    "education student learning":   [256490, 159711, 1181671, 1205651, 267885],
    "english learning study":       [1181671, 256490, 159711, 1205651, 267885],
    # ไลฟ์สไตล์ทั่วไป
    "lifestyle nature people":      [1591382, 1559388, 1486233, 1563355, 1770809],
    # กีฬา
    "sport fitness exercise":       [1552242, 841130, 46798, 1884574, 274422],
    # ดนตรี/คอนเสิร์ต
    "concert music show":           [1105666, 1190298, 2747446, 1540319, 2120967],
}


def _extract_keywords(title: str, cat: str) -> str:
    for kw, eng in KEYWORD_MAP:
        if kw in title:
            return eng
    cat_lower = cat.lower()
    for kw, eng in KEYWORD_MAP:
        if kw.lower() in cat_lower:
            return eng
    for cat_key, topic in CATEGORY_FALLBACK.items():
        if cat_key in cat_lower:
            return topic
    return "lifestyle nature people"


def _build_pexels_url(title: str, cat: str, stem: str) -> str:
    keywords = _extract_keywords(title, cat)
    seed = int(hashlib.md5(f"{stem}_{keywords[:30]}".encode()).hexdigest()[:8], 16)

    pool = None
    for pool_key, ids in PEXELS_POOL.items():
        if pool_key == keywords or pool_key in keywords or keywords in pool_key:
            pool = ids
            break
    if pool is None:
        kw_words = set(keywords.lower().split())
        best_score = 0
        for pool_key, ids in PEXELS_POOL.items():
            score = len(kw_words & set(pool_key.lower().split()))
            if score > best_score:
                best_score = score
                pool = ids

    if pool:
        photo_id = pool[seed % len(pool)]
        return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=800&h=450&fit=crop"

    return f"https://picsum.photos/seed/{stem}/800/450"


def _make_svg(title: str, img_url: str, cat: str) -> str:
    """สร้าง SVG ที่มีรูปจริงเป็น background + overlay ข้อความ"""
    # escape XML special chars
    safe_title = title[:40].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    safe_cat   = cat.replace("&", "&amp;")

    # ตัดชื่อยาวให้พอดี 2 บรรทัด
    words = safe_title
    line1 = words[:22]
    line2 = words[22:44] if len(words) > 22 else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 800 450">
  <defs>
    <clipPath id="cp"><rect width="800" height="450" rx="0"/></clipPath>
    <linearGradient id="ov" x1="0" y1="0" x2="0" y2="1">
      <stop offset="40%" stop-color="#000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0.72"/>
    </linearGradient>
  </defs>
  <image href="{img_url}" x="0" y="0" width="800" height="450" preserveAspectRatio="xMidYMid slice" clip-path="url(#cp)"/>
  <rect width="800" height="450" fill="url(#ov)"/>
  <text x="24" y="{390 if not line2 else 375}" fill="#fff" font-family="Sarabun,sans-serif" font-size="26" font-weight="bold">{line1}</text>
  {f'<text x="24" y="408" fill="#fff" font-family="Sarabun,sans-serif" font-size="26" font-weight="bold">{line2}</text>' if line2 else ''}
  <text x="24" y="435" fill="#94a3b8" font-family="sans-serif" font-size="16">{safe_cat}</text>
</svg>'''


_SKIP_DIRS = {"node_modules", ".git", ".vercel", "__pycache__", "dist", "build", ".next"}
_NON_ARTICLE = {
    "index.html", "404.html", "contact.html", "sitemap.html", "privacy.html",
    "video.html", "shopping.html", "lotto.html",
}
_NON_ARTICLE |= set(CATEGORY_PAGE_MAP.values())


def _scan_articles(target_file=None):
    result = []
    for fp in sorted(BASE_PATH.rglob("*")):
        if any(s in fp.parts for s in _SKIP_DIRS):
            continue
        if (fp.suffix.lower() == ".html" and fp.is_file()
                and fp.parent == BASE_PATH
                and fp.name not in _NON_ARTICLE):
            if target_file and fp.name != target_file and fp.stem != target_file:
                continue
            try:
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                if "<html" in txt.lower() and len(txt) > 100:
                    result.append(fp)
            except Exception:
                pass
    return result


def regen_thumbs(target_file=None):
    log_section("🖼️  Regenerate SVG Thumbnails")
    articles = _scan_articles(target_file)
    log_info(f"ตรวจ {len(articles)} บทความ\n")

    thumb_dir = BASE_PATH / "images" / "thumbs"
    thumb_dir.mkdir(parents=True, exist_ok=True)

    done = skipped = errors = 0

    for fp in articles:
        try:
            soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")

            # ดึง title
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else fp.stem.replace("_", " ")

            cat = fp.stem.split("_")[0] if "_" in fp.stem else fp.stem

            img_url  = _build_pexels_url(title, cat, fp.stem)
            svg_text = _make_svg(title, img_url, cat)
            svg_path = thumb_dir / f"{fp.stem}.svg"

            if not DRY_RUN:
                svg_path.write_text(svg_text, encoding="utf-8")

            prefix = "[DRY-RUN] " if DRY_RUN else ""
            log_ok(f"  {prefix}✅ {fp.stem}.svg")
            log_info(f"       img: {img_url[:70]}")
            done += 1

        except Exception as e:
            log_err(f"  ❌ {fp.name}: {e}")
            errors += 1

    prefix = "[DRY-RUN] " if DRY_RUN else ""
    log_ok(f"\n{prefix}สร้าง SVG: {done} | ข้าม: {skipped} | error: {errors}")


def main():
    args = sys.argv[1:]
    target = None
    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            target = args[idx + 1]

    regen_thumbs(target)


if __name__ == "__main__":
    main()
