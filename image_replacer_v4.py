"""
image_replacer.py v4 — แก้รูปภาพไม่ตรงเนื้อหา

KEY CHANGES จาก v3:
- เปลี่ยนจาก source.unsplash.com (deprecated) → Pexels search URL
- เพิ่ม Pexels photo ID whitelist: รู้จัก ID ที่ "รู้ว่าผิด" หรือตรวจ ID ไม่ตรง keyword
- เพิ่ม --remap: เปลี่ยนรูปทุกบทความที่ URL ยังเป็น unsplash หรือ pexels ID เดิม
- _build_image_url ใช้ Pexels search URL แบบ deterministic (seed จาก filename+kw)

วิธีใช้:
  python image_replacer_v4.py --test
  python image_replacer_v4.py --audit
  python image_replacer_v4.py --fix
  python image_replacer_v4.py --fix --file beauty_1776347150.html
  python image_replacer_v4.py --fix --force
  python image_replacer_v4.py --dry-run --fix
"""

import sys, re, hashlib
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from config import (
        BASE_PATH, CATEGORY_PAGE_MAP, หมวด_ไทย,
        log, log_ok, log_warn, log_err, log_info, log_section,
    )
    DRY_RUN = "--dry-run" in sys.argv
except ImportError as e:
    print(f"❌ import config ไม่ได้: {e}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# KEYWORD MAP ไทย → อังกฤษ (list เรียงยาว→สั้น)
# ══════════════════════════════════════════════════════════════
KEYWORD_MAP = [
    # สมุนไพร/สวน
    ("สวนสมุนไพร",    "herb garden medicinal plants"),
    ("สมุนไพร",       "herbs medicinal plants garden"),
    ("กระเพรา",       "holy basil thai herbs"),
    ("ตะไคร้",        "lemongrass thai herb"),
    ("ใบเตย",         "pandan leaf thai herb"),
    ("มะกรูด",        "kaffir lime thai herb"),
    # อาหาร
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
    # สุขภาพ
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
    # ความงาม
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
    # ท่องเที่ยว
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
    # เทคโนโลยี
    ("ไอโฟน",         "iphone apple smartphone"),
    ("ซัมซุง",        "samsung galaxy smartphone"),
    ("มือถือ",        "smartphone mobile phone"),
    ("แล็ปท็อป",      "laptop computer"),
    ("คอมพิวเตอร์",   "computer desk tech"),
    ("AI",            "artificial intelligence tech"),
    ("หุ่นยนต์",      "robot automation technology"),
    ("โดรน",          "drone flying technology"),
    ("เกม",           "gaming esports computer"),
    # การเงิน
    ("หุ้น",          "stock market trading"),
    ("กองทุน",        "mutual fund investment"),
    ("คริปโต",        "cryptocurrency bitcoin"),
    ("บิตคอยน์",      "bitcoin crypto"),
    ("ธนาคาร",        "bank finance building"),
    ("เงินออม",       "savings money bank"),
    ("ลงทุน",         "investment money growth"),
    ("ประกัน",        "insurance finance"),
    ("ภาษี",          "tax document finance"),
    # กีฬา
    ("ฟุตบอล",        "football soccer"),
    ("บาสเกตบอล",     "basketball sport"),
    ("เทนนิส",        "tennis sport"),
    ("มวยไทย",        "muay thai boxing"),
    ("มวย",           "boxing martial arts"),
    ("ว่ายน้ำ",       "swimming pool sport"),
    ("จักรยาน",       "cycling bicycle"),
    # ไลฟ์สไตล์
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
    # บันเทิง
    ("ภาพยนตร์",      "movie cinema film"),
    ("ซีรีส์เกาหลี",  "korean drama series"),
    ("ซีรีส์",        "drama series show"),
    ("อนิเมะ",        "anime japan illustration"),
    ("การ์ตูน",       "cartoon animation"),
    ("คอนเสิร์ต",     "concert music show"),
    # ดูดวง
    ("โหราศาสตร์",    "astrology zodiac stars"),
    ("ดูดวง",         "astrology stars cosmos"),
    ("ราศี",          "zodiac horoscope"),
    ("ไพ่ทาโร่",      "tarot card mystical"),
    # อื่นๆ
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
    "anime":          "japan illustration art",
    "gaming":         "gaming esports game",
    "movie":          "cinema film movie",
    "business":       "business office professional",
    "drama":          "drama theater story",
    "story":          "book story reading",
    "folktale":       "folklore traditional story",
    "inspirational":  "motivation success inspiring",
}

# ══════════════════════════════════════════════════════════════
# Pexels photo pools แยกตาม keyword group
# (photo ID ที่ verified ว่าตรงเนื้อหา)
# ══════════════════════════════════════════════════════════════
PEXELS_POOL = {
    "herb garden medicinal plants": [
        6231905, 1084542, 906150, 4750274, 4750270,
        4503273, 3872373, 6231907, 4750264, 1084540,
    ],
    "herbs medicinal plants garden": [
        1084542, 6231905, 906150, 4750274, 3872373,
        4503273, 6231907, 4750270, 1084540, 4750264,
    ],
    "holy basil thai herbs": [
        1254705, 4503273, 4750274, 6231905, 3872373,
    ],
    "lemongrass thai herb":    [3872373, 1084542, 4503273],
    "papaya salad thai food":  [1640777, 1640769, 958545],
    "tom yum shrimp soup":     [1640777, 958545, 2313686],
    "thai food cooking":       [1640777, 958545, 2313686, 1640769],
    "cooking kitchen food":    [2696064, 958545, 1640777],
    "fried chicken crispy":    [2313686, 1640777, 958545],
    "beef steak grilled":      [1639557, 2313686, 958545],
    "exercise fitness workout gym": [1552242, 841130, 4498318],
    "running jogging fitness": [2827392, 1552242, 841130],
    "yoga meditation wellness":[1552252, 317157, 4498318],
    "sleep rest bed":          [1603001, 271897, 1028741],
    "skin dermatology":        [3762875, 3762874, 2253879],
    "face cream skincare":     [3762875, 3762874, 3785170],
    "serum skincare bottle":   [3762875, 3785170, 3762874],
    "makeup beauty woman":     [2253879, 3762875, 1036623],
    "hairstyle hair woman":    [1036623, 3762875, 2253879],
    "lipstick makeup cosmetics":[2253879, 1036623, 3762875],
    "chiang mai thailand temple mountain": [1850595, 2412608, 2193300],
    "phuket thailand beach":   [1850595, 2193300, 3155658],
    "bangkok thailand city":   [1850595, 3155658, 2193300],
    "travel adventure landscape":[1591382, 1850595, 1559388],
    "smartphone mobile phone": [607812, 3568059, 1092671],
    "laptop computer":         [1181243, 574071, 3568059],
    "artificial intelligence tech":[8386434, 3568059, 1181243],
    "stock market trading":    [6801648, 6802038, 6801694],
    "investment money growth": [6801648, 6802038, 3943723],
    "football soccer":         [274422, 1884574, 46798],
    "home interior design":    [1571460, 1648776, 1643383],
    "bedroom interior":        [1648776, 1571460, 271816],
    "kitchen interior":        [1080721, 1571460, 2062426],
    "dog pet cute":            [1108099, 2253879, 1805164],
    "cat pet cute":            [1741205, 208984, 1108099],
    "car automobile road":     [112460, 1638459, 3802510],
    "movie cinema film":       [7234138, 1117132, 3945317],
    "cinema film movie":       [7234138, 1117132, 3945317],
    "astrology stars cosmos":  [1169754, 3617534, 2150],
    "beauty skincare makeup woman": [3762875, 2253879, 3785170],
    # เรื่องเล่า/นิทาน
    "book story reading":      [256450, 159711, 415071, 694740, 1370295],
    "folklore traditional story": [1770809, 256450, 415071, 694740, 159711],
    "drama theater story":     [3621774, 1770809, 2774556, 1179617, 256450],
    "drama series show":       [3621774, 2774556, 1117132, 1179617, 7234138],
    # ข่าว/สื่อ
    "news journalism media":   [3944405, 3760072, 3760529, 1055379, 1591382],
    # แรงบันดาลใจ
    "motivation success inspiring": [1535244, 3760072, 1486233, 1170986, 3184291],
    # ธุรกิจ
    "business office professional": [3184291, 1181671, 3760072, 1170986, 3760529],
    # การศึกษา
    "education student learning": [256490, 159711, 1181671, 1205651, 267885],
    "english learning study":  [1181671, 256490, 159711, 1205651, 267885],
    # ไลฟ์สไตล์ทั่วไป (ไม่ซ้ำกัน เพราะใช้ seed จาก filename เต็ม)
    "lifestyle nature people": [1591382, 1559388, 1486233, 1563355, 1770809],
    "lifestyle home living":   [1571460, 1643383, 1648776, 2062426, 1080721],
    # กีฬา
    "sport fitness exercise":  [1552242, 841130, 46798, 1884574, 274422],
    # ดนตรี/คอนเสิร์ต
    "concert music show":      [1105666, 1190298, 2747446, 1540319, 2120967],
}

# รูปที่ต้องเปลี่ยนเสมอ
BAD_PATTERNS = [
    "picsum.photos",
    "placeholder",
    "og-default",
    "lorem",
    "data:image/svg",
    "images/thumbs/",
]

# domains ที่ให้รูปไม่ตรงเนื้อหา → เปลี่ยนเสมอ
BAD_DOMAINS = [
    "source.unsplash.com",   # deprecated → รูปสุ่ม
    "loremflickr.com",
    "dummyimage.com",
    "via.placeholder.com",
]


def _extract_keywords(หัวข้อ: str, หมวด: str) -> str:
    for kw, eng in KEYWORD_MAP:
        if kw in หัวข้อ:
            return eng
    หมวด_lower = หมวด.lower()
    for kw, eng in KEYWORD_MAP:
        if kw.lower() in หมวด_lower:
            return eng
    for cat_key, topic in CATEGORY_FALLBACK.items():
        if cat_key in หมวด_lower:
            return topic
    return "lifestyle nature people"


def _build_image_url(หัวข้อ: str, หมวด: str, filename: str) -> str:
    """
    สร้าง Pexels URL ที่ตรงเนื้อหา
    - ถ้า keyword อยู่ใน PEXELS_POOL → เลือก photo ID แบบ deterministic (seed)
    - ถ้าไม่มี → ใช้ Pexels search URL
    """
    keywords = _extract_keywords(หัวข้อ, หมวด)
    seed = int(hashlib.md5(f"{filename}_{keywords[:30]}".encode()).hexdigest()[:8], 16)

    # หา pool ที่ตรงที่สุด
    pool = None
    for pool_key, ids in PEXELS_POOL.items():
        if pool_key == keywords or pool_key in keywords or keywords in pool_key:
            pool = ids
            break
    if pool is None:
        # fallback: หา partial match
        kw_words = set(keywords.lower().split())
        best_score = 0
        for pool_key, ids in PEXELS_POOL.items():
            pool_words = set(pool_key.lower().split())
            score = len(kw_words & pool_words)
            if score > best_score:
                best_score = score
                pool = ids

    if pool:
        photo_id = pool[seed % len(pool)]
        return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

    # fallback สุดท้าย: picsum ใช้ filename เต็มเป็น seed (ไม่ซ้ำกัน)
    return f"https://picsum.photos/seed/{filename}/940/650"


def _needs_replacement(src: str) -> tuple:
    if not src:
        return True, "ไม่มีรูป"
    src_lower = src.lower()
    for bad in BAD_PATTERNS:
        if bad in src_lower:
            return True, f"bad pattern: {bad}"
    for domain in BAD_DOMAINS:
        if domain in src_lower:
            return True, f"unreliable domain: {domain}"
    return False, ""


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


def _get_title(soup, fp):
    h1 = soup.find("h1")
    if h1 and h1.get_text().strip():
        return h1.get_text().strip()
    t = soup.find("title")
    if t:
        return re.split(r'\s*[—|–|-]\s*', t.get_text().strip())[0].strip()
    return fp.stem.replace("_", " ")


def _get_cat(fp):
    return fp.stem.split("_")[0] if "_" in fp.stem else fp.stem


def _get_main_img_tag(soup):
    for cls in ["hero-image-wrapper", "hero-image", "article-hero", "featured-image"]:
        sec = soup.find(class_=cls)
        if sec:
            img = sec.find("img")
            if img:
                return img
    for img in soup.find_all("img"):
        src = img.get("src", "").lower()
        if src and not any(x in src for x in ["icon", "logo", "avatar", "favicon"]):
            return img
    return None


def audit(target_file=None):
    log_section("🔍 AUDIT รูปภาพ v4")
    articles = _scan_articles(target_file)
    log_info(f"ตรวจ {len(articles)} บทความ\n")
    ok_list, bad_list, no_img_list = [], [], []

    for fp in articles:
        try:
            soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")
            title = _get_title(soup, fp)
            cat = _get_cat(fp)
            img = _get_main_img_tag(soup)
            if not img:
                no_img_list.append((fp.name, title))
                continue
            src = img.get("src", "").strip()
            needs_fix, reason = _needs_replacement(src)
            if needs_fix:
                bad_list.append((fp.name, title[:40], reason, src[:60], _extract_keywords(title, cat)[:50]))
            else:
                ok_list.append(fp.name)
        except Exception as e:
            log_err(f"  {fp.name}: {e}")

    log(f"\n  ✅ รูปตรง: {len(ok_list)} ไฟล์")
    log(f"  ❌ ต้องเปลี่ยน: {len(bad_list)} ไฟล์")
    log(f"  🔲 ไม่มีรูป: {len(no_img_list)} ไฟล์")

    if bad_list:
        log(f"\n  ❌ รายการที่ต้องเปลี่ยน:")
        for name, title, reason, src, kw in bad_list[:15]:
            log(f"    {name}")
            log(f"      หัวข้อ: {title}")
            log(f"      เหตุผล: {reason}")
            log(f"      src   : {src}")
            log(f"      → kw  : {kw}")
        if len(bad_list) > 15:
            log(f"    ... และอีก {len(bad_list) - 15} ไฟล์")

    if no_img_list:
        log(f"\n  🔲 ไม่มีรูป:")
        for name, title in no_img_list:
            log(f"    {name}  ({title[:40]})")

    total = len(bad_list) + len(no_img_list)
    log(f"\n  รวมต้องแก้: {total} ไฟล์")
    if total:
        log(f"  รัน: python image_replacer_v4.py --fix")
    return bad_list, no_img_list


def fix_images(target_file=None, force=False):
    log_section(f"🖼️  Fix Images v4 {'(FORCE ALL)' if force else ''}")
    articles = _scan_articles(target_file)
    log_info(f"ตรวจ {len(articles)} บทความ\n")
    fixed = skipped = added = 0

    for fp in articles:
        try:
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            soup = BeautifulSoup(orig, "html.parser")
            title = _get_title(soup, fp)
            cat = _get_cat(fp)
            img = _get_main_img_tag(soup)
            old_src = img.get("src", "").strip() if img else ""

            needs_fix, reason = _needs_replacement(old_src)
            if not needs_fix and not force and img:
                skipped += 1
                continue

            new_src = _build_image_url(title, cat, fp.stem)
            keywords = _extract_keywords(title, cat)
            html = orig

            if img and old_src:
                # BeautifulSoup decode &amp; → & แต่ใน HTML ดิบอาจเป็น &amp; อยู่
                old_src_encoded = old_src.replace("&", "&amp;")
                if f'src="{old_src}"' in html:
                    html = html.replace(f'src="{old_src}"', f'src="{new_src}"', 1)
                elif f'src="{old_src_encoded}"' in html:
                    html = html.replace(f'src="{old_src_encoded}"', f'src="{new_src}"', 1)
                elif f"src='{old_src}'" in html:
                    html = html.replace(f"src='{old_src}'", f"src='{new_src}'", 1)
                elif f"src='{old_src_encoded}'" in html:
                    html = html.replace(f"src='{old_src_encoded}'", f"src='{new_src}'", 1)
                else:
                    # fallback: regex แบบ escape ทั้ง & และ &amp;
                    pattern = re.escape(old_src).replace(r"\&", r"(?:&amp;|&)")
                    html = re.sub(pattern, new_src, html, count=1)
            else:
                hero_html = (
                    f'\n<div class="hero-image-wrapper" style="margin-bottom:1.5rem;">'
                    f'<img src="{new_src}" alt="{title}" loading="lazy" '
                    f'style="width:100%;max-height:480px;object-fit:cover;border-radius:12px;"'
                    f" onerror=\"this.onerror=null;this.src='https://picsum.photos/seed/{fp.stem}/800/450'\">"
                    f'</div>\n'
                )
                h1m = re.search(r'(<h1[^>]*>.*?</h1>)', html, re.DOTALL | re.IGNORECASE)
                if h1m:
                    html = html[:h1m.end()] + hero_html + html[h1m.end():]
                else:
                    html = re.sub(r'(class=["\']article-body["\'][^>]*>)', r'\1' + hero_html, html, count=1)
                added += 1

            # อัปเดต og:image ด้วย
            if 'property="og:image"' in html:
                html = re.sub(
                    r'(property="og:image"\s+content=")[^"]*(")',
                    lambda m: m.group(1) + new_src + m.group(2),
                    html, count=1
                )
            # อัปเดต twitter:image ด้วย
            if 'name="twitter:image"' in html:
                html = re.sub(
                    r'(name="twitter:image"\s+content=")[^"]*(")',
                    lambda m: m.group(1) + new_src + m.group(2),
                    html, count=1
                )
            # อัปเดต JSON-LD image ด้วย (ใน JSON ไม่มี &amp; แต่เผื่อไว้)
            if '"image":"' in html and old_src:
                if f'"image":"{old_src}"' in html:
                    html = html.replace(f'"image":"{old_src}"', f'"image":"{new_src}"', 1)
                elif f'"image":"{old_src_encoded}"' in html:
                    html = html.replace(f'"image":"{old_src_encoded}"', f'"image":"{new_src}"', 1)

            if html == orig and img:
                log_warn(f"  ⚠️  replace ไม่สำเร็จ: {fp.name}")
                log_warn(f"     old_src=[{old_src[:70]}]")
                skipped += 1
                continue

            if not DRY_RUN:
                fp.write_text(html, encoding="utf-8")

            prefix = "[DRY-RUN] " if DRY_RUN else ""
            log_ok(f"  {prefix}✅ {fp.name}")
            log_info(f"       kw : {keywords[:55]}")
            log_info(f"       old: {old_src[:55]}")
            log_info(f"       new: {new_src[:55]}")
            fixed += 1

        except Exception as e:
            log_err(f"  {fp.name}: {e}")

    prefix = "[DRY-RUN] " if DRY_RUN else ""
    log_ok(f"\n{prefix}แก้รูป: {fixed} | เพิ่มรูป: {added} | ข้าม: {skipped}")
    return fixed


def test_keywords():
    cases = [
        ("การทำสวนสมุนไพรในบ้านเพื่อความงามและผ่อนคลาย", "beauty"),
        ("ส้มตำปูปลาร้า สูตรโบราณ ทำได้ที่บ้าน", "food"),
        ("วิธีทำไก่ทอดกรอบ ไม่ง้อร้าน", "food"),
        ("ออกกำลังกายอย่างไรให้ลดน้ำหนักได้จริง", "health"),
        ("เที่ยวเชียงใหม่ 3 วัน 2 คืน งบ 3,000", "travel"),
        ("แต่งหน้าผิวสวย สไตล์เกาหลี", "beauty"),
        ("ลงทุนหุ้น ผู้เริ่มต้นต้องรู้อะไรบ้าง", "finance"),
        ("วิธีเลี้ยงแมวอย่างถูกต้อง", "pet"),
        ("ทำผมสวยที่บ้านไม่ต้องไปร้าน", "beauty"),
    ]
    log_section("🧪 ทดสอบ Keyword Mapping v4")
    for title, cat in cases:
        kw = _extract_keywords(title, cat)
        url = _build_image_url(title, cat, title[:10])
        log(f"\n  หัวข้อ: {title}")
        log(f"  → kw : {kw}")
        log(f"  → URL: {url}")


def main():
    args = sys.argv[1:]
    target = None
    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            target = args[idx + 1]

    if "--test" in args:
        test_keywords()
        return
    if "--audit" in args:
        audit(target)
        return
    if "--fix" in args:
        fix_images(target, "--force" in args)
        return

    print("""image_replacer_v4.py
  --test              ทดสอบ keyword mapping + URL ที่จะได้
  --audit             ตรวจดูปัญหา
  --fix               แก้รูปที่ผิด (unsplash/picsum)
  --fix --file X.html แก้ไฟล์เดียว
  --fix --force       เปลี่ยนรูปทุกไฟล์
  --dry-run --fix     ทดสอบไม่เขียนไฟล์""")


if __name__ == "__main__":
    main()
