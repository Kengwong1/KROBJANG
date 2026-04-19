"""
╔══════════════════════════════════════════════════════════════════╗
║  image_sources.py  v9 — ดึงรูปตรงเนื้อหา ไม่ซ้ำ ไม่ picsum    ║
║                                                                  ║
║  แก้ปัญหาหลัก (v9):                                            ║
║  ✅ _extract_title_keywords() — ดึง EN keyword จากหัวข้อไทยตรง ║
║  ✅ _get_topic() — ผสม title keyword + category topic           ║
║  ✅ Pexels/Pixabay/Unsplash ส่ง title_kw ไปด้วยทุก source      ║
║  ✅ page seed ใช้ full md5 + offset → ไม่ซ้ำข้ามบทความ         ║
║  ✅ Pollinations ย้ายหลัง Wikimedia (ช้า ไม่ควร default)       ║
║  ✅ timeout 5s (ลดจาก 8s) ป้องกัน pipeline หยุด               ║
║                                                                  ║
║  Priority: Pexels > Pixabay > Unsplash > Google >               ║
║            Wikimedia > Pollinations > Picsum(fallback)          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, re, hashlib, time, json, urllib.request, urllib.parse, urllib.error
from pathlib import Path

# ══════════════════════════════════════════════════════════════
# 🔧  โหลด .env
# ══════════════════════════════════════════════════════════════
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip(); val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

_load_dotenv()

PEXELS_KEY     = os.environ.get("PEXELS_KEY", "")
UNSPLASH_KEY   = os.environ.get("UNSPLASH_KEY", "")
PIXABAY_KEY    = os.environ.get("PIXABAY_KEY", "")
GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY", "")
GOOGLE_CSE_CX  = os.environ.get("GOOGLE_CSE_CX", "")

# ══════════════════════════════════════════════════════════════
# 🗂️  Topic map — หมวดหมู่ → EN keyword
# ══════════════════════════════════════════════════════════════
_TOPIC_MAP = {
    "อาหาร": "food meal cuisine cooking",
    "food": "food meal restaurant cuisine",
    "cooking": "cooking kitchen food recipe",
    "ทำอาหาร": "cooking kitchen recipe food",
    "เดลิเวอรี": "food delivery package courier",
    "ร้านอาหาร": "restaurant dining food menu",
    "สุขภาพ": "healthcare wellness fitness medical",
    "health": "healthcare wellness medical hospital",
    "ออกกำลังกาย": "exercise fitness workout gym",
    "โควิด": "pandemic health medical virus",
    "covid": "pandemic health medical quarantine",
    "โรค": "disease medical health treatment",
    "ธุรกิจ": "business office corporate meeting",
    "business": "business office corporate finance",
    "ออนไลน์": "online ecommerce digital shopping",
    "online": "online ecommerce digital internet",
    "การเงิน": "finance money investment banking",
    "finance": "finance money investment banking",
    "ลงทุน": "investment stock market finance",
    "เงิน": "money finance cash banking",
    "ตลาดหุ้น": "stock market trading investment",
    "อสังหาริมทรัพย์": "real estate property house building",
    "สตาร์ทอัพ": "startup business entrepreneur office",
    "การตลาด": "marketing advertising brand strategy",
    "marketing": "marketing business strategy advertising",
    "เทคโนโลยี": "technology computer digital innovation",
    "technology": "technology computer digital innovation",
    "ai": "artificial intelligence technology robot",
    "ปัญญาประดิษฐ์": "artificial intelligence robot technology",
    "โปรแกรม": "programming code software developer",
    "programming": "programming code computer developer",
    "มือถือ": "smartphone mobile phone technology",
    "smartphone": "smartphone mobile phone technology",
    "gaming": "gaming esports controller game",
    "เกม": "gaming esports controller game",
    "ท่องเที่ยว": "travel landscape destination adventure",
    "travel": "travel landscape destination adventure",
    "ทะเล": "beach sea ocean travel",
    "ภูเขา": "mountain nature landscape",
    "ญี่ปุ่น": "japan tokyo temple travel",
    "ยุโรป": "europe travel architecture city",
    "ความงาม": "beauty cosmetics skincare makeup",
    "beauty": "beauty cosmetics skincare makeup",
    "แฟชั่น": "fashion clothing style outfit",
    "fashion": "fashion clothing style outfit",
    "ไลฟ์สไตล์": "lifestyle living home relax",
    "lifestyle": "lifestyle living home relax",
    "บ้าน": "home house interior decoration",
    "กีฬา": "sport fitness exercise athlete",
    "sport": "sport fitness exercise stadium",
    "ฟุตบอล": "football soccer sport stadium",
    "มวย": "boxing martial arts fight sport",
    "การศึกษา": "education learning university student",
    "education": "education learning study school",
    "เคล็ดลับ": "tips advice guide learning",
    "tips": "tips advice guide learning",
    "ข่าว": "news newspaper journalism media",
    "news": "news newspaper journalism media",
    "บันเทิง": "entertainment concert show celebrity",
    "entertainment": "entertainment show concert stage",
    "ดารา": "celebrity entertainment people",
    "หนัง": "movie cinema film entertainment",
    "movie": "movie cinema film entertainment",
    "เพลง": "music concert singer performance",
    "music": "music concert instrument performance",
    "สัตว์": "animal pet nature wildlife",
    "pet": "pet dog cat animal",
    "หมา": "dog pet animal cute",
    "แมว": "cat pet animal cute",
    "ธรรมชาติ": "nature landscape forest mountain",
    "nature": "nature landscape forest outdoor",
    "รถ": "car automobile vehicle road",
    "car": "car automobile vehicle road",
    "ดูดวง": "astrology stars zodiac moon",
    "horoscope": "astrology stars zodiac horoscope",
    "ธรรมะ": "meditation temple buddhism calm",
    "สมาธิ": "meditation yoga calm mindfulness",
    "กฎหมาย": "law justice courthouse legal",
    "law": "law justice courthouse legal",
    "อาชีพ": "career job work profession",
    "career": "career job office work",
    "การ์ตูน": "animation cartoon colorful art",
    "cartoon": "animation cartoon colorful creative",
    "anime": "japan illustration art anime",
    "ผี": "mystery horror dark night",
    "ghost": "mystery horror dark supernatural",
    "ลอตเตอรี": "lucky numbers lottery win",
    "lottery": "lucky numbers lottery win",
}

_DEFAULT_TOPIC = "lifestyle nature people"

# ══════════════════════════════════════════════════════════════
# 🔑  [NEW v9] TH word → EN keyword map สำหรับแยกจากหัวข้อ
# ══════════════════════════════════════════════════════════════
_TH_WORD_TO_EN = {
    "อาหาร": "food", "ข้าว": "rice food", "ก๋วยเตี๋ยว": "noodle food",
    "ทำอาหาร": "cooking kitchen", "สูตร": "recipe cooking",
    "เดลิเวอรี": "food delivery", "ร้านอาหาร": "restaurant",
    "สุขภาพ": "health", "ออกกำลังกาย": "exercise fitness",
    "โยคะ": "yoga fitness", "วิ่ง": "running jogging",
    "โควิด": "covid pandemic", "วัคซีน": "vaccine medical",
    "โรค": "disease medical", "ยา": "medicine medical",
    "ลดน้ำหนัก": "weight loss fitness", "อาหารเสริม": "supplement nutrition",
    "ธุรกิจ": "business", "ออนไลน์": "online digital",
    "ขายของ": "selling ecommerce", "ตลาด": "market",
    "การตลาด": "marketing", "โฆษณา": "advertising",
    "สตาร์ทอัพ": "startup entrepreneur",
    "ลงทุน": "investment", "หุ้น": "stock investment",
    "อสังหา": "real estate property",
    "เทคโนโลยี": "technology", "มือถือ": "smartphone mobile",
    "คอมพิวเตอร์": "computer", "อินเทอร์เน็ต": "internet",
    "แอป": "app mobile", "โปรแกรม": "software programming",
    "เกม": "gaming", "ปัญญาประดิษฐ์": "artificial intelligence",
    "ท่องเที่ยว": "travel", "เที่ยว": "travel tourism",
    "ทะเล": "beach sea ocean", "ภูเขา": "mountain nature",
    "วัด": "temple buddhism", "ญี่ปุ่น": "japan",
    "ยุโรป": "europe travel", "เกาหลี": "korea travel",
    "ความงาม": "beauty", "เครื่องสำอาง": "cosmetics makeup",
    "ผิว": "skincare beauty", "ผม": "hair beauty",
    "แฟชั่น": "fashion", "เสื้อผ้า": "clothing fashion",
    "กีฬา": "sport", "ฟุตบอล": "football soccer",
    "บาสเกตบอล": "basketball sport", "มวย": "boxing",
    "ว่ายน้ำ": "swimming sport",
    "หนัง": "movie cinema", "ซีรี่ส์": "tv series",
    "เพลง": "music", "คอนเสิร์ต": "concert music",
    "ดารา": "celebrity", "นักแสดง": "actor",
    "บ้าน": "home interior", "การ์ตูน": "cartoon animation",
    "ดูดวง": "astrology", "ราศี": "zodiac astrology",
    "ธรรมะ": "meditation buddhism", "สมาธิ": "meditation",
    "สัตว์เลี้ยง": "pet animal", "หมา": "dog pet", "แมว": "cat pet",
    "รถ": "car automobile", "มอเตอร์ไซค์": "motorcycle",
    "กฎหมาย": "law legal", "ภาษี": "tax finance",
    "อาชีพ": "career job", "งาน": "work career",
    "การศึกษา": "education", "เรียน": "learning education",
    "เด็ก": "children family", "ครอบครัว": "family",
    "ผี": "horror mystery", "ลอตเตอรี": "lottery lucky",
}


def _extract_title_keywords(หัวข้อ: str) -> str:
    """
    [NEW v9] ดึง EN keyword ตรงๆ จากหัวข้อภาษาไทย/อังกฤษ
    ใช้ word-level matching — ตรงกว่า category mapping มาก

    ตัวอย่าง:
      "ธุรกิจออนไลน์ในช่วงโควิด" → "business online covid pandemic"
      "10 วิธีออกกำลังกายที่บ้าน" → "exercise fitness home"
      "เคล็ดลับทำอาหารญี่ปุ่น"   → "cooking recipe japan food"
    """
    keywords = []
    title_lower = หัวข้อ.lower()

    # EN words ในหัวข้อ (ถ้าปนอังกฤษ)
    skip_en = {"the","and","for","with","from","that","this","top",
               "best","how","tips","guide","ways","what","when","why"}
    for w in re.findall(r'[a-zA-Z]{3,}', title_lower):
        if w not in skip_en:
            keywords.append(w)

    # แปล TH → EN (เรียงตาม key ยาวก่อน เพื่อ match คำยาวก่อน)
    for th_word, en_kw in sorted(_TH_WORD_TO_EN.items(), key=lambda x: -len(x[0])):
        if th_word.lower() in title_lower:
            for kw in en_kw.split():
                if kw not in keywords:
                    keywords.append(kw)

    # กำจัดซ้ำรักษาลำดับ
    seen, unique = set(), []
    for k in keywords:
        if k not in seen:
            seen.add(k); unique.append(k)

    return " ".join(unique[:6])


def _get_topic(หมวด: str, หัวข้อ: str = "") -> str:
    """
    [IMPROVED v9] ผสม title keyword + category topic
    → query ที่ตรงเนื้อหากว่าเดิมมาก
    """
    combined = (หมวด + " " + หัวข้อ).lower()
    title_kw = _extract_title_keywords(หัวข้อ)

    # หา base topic จาก map (เรียง key ยาวก่อน)
    base_topic = _DEFAULT_TOPIC
    for kw, topic in sorted(_TOPIC_MAP.items(), key=lambda x: -len(x[0])):
        if kw in combined:
            base_topic = topic
            break

    if title_kw:
        words = list(dict.fromkeys(
            (title_kw + " " + base_topic.replace(",", " ")).split()
        ))[:6]
        return ",".join(words)

    return base_topic


def _seed(identifier: str) -> str:
    # [FIX v10] เพิ่ม nanosecond entropy ป้องกัน seed ชนเมื่อ identifier คล้ายกัน
    key = identifier.strip() if identifier.strip() else str(time.time_ns())
    # ผสม key + length + position-hash ป้องกัน "article1" vs "article10" ได้ seed เดียวกัน
    entropy_key = f"{key}|len={len(key)}|sum={sum(ord(c) for c in key)}"
    return hashlib.md5(entropy_key.encode()).hexdigest()[:12]


def _page_from_seed(seed_str: str, max_page: int, offset: int = 0) -> int:
    """[FIX v9] ใช้ full seed hex + offset → ไม่ซ้ำข้ามบทความ"""
    return (int(seed_str, 16) + offset) % max_page + 1


def _fetch_json(url: str, headers: dict = None, timeout: int = 5) -> dict:
    """HTTP GET → JSON (timeout 5s ป้องกัน pipeline หยุด)"""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════
# 📸  SOURCES
# ══════════════════════════════════════════════════════════════

def from_pexels(topic: str, seed_str: str, title_kw: str = "") -> str:
    if not PEXELS_KEY:
        return ""
    if title_kw:
        parts = title_kw.split()[:3]
        first_cat = topic.split(",")[0].strip()
        if first_cat not in title_kw:
            parts.append(first_cat)
        query = " ".join(parts)
    else:
        query = " ".join(k.strip() for k in topic.split(",")[:2])

    page = _page_from_seed(seed_str, 20)
    data = _fetch_json(
        f"https://api.pexels.com/v1/search"
        f"?query={urllib.parse.quote(query)}&per_page=3&page={page}",
        headers={"Authorization": PEXELS_KEY}
    )
    try:
        photos = data.get("photos", [])
        if not photos:
            return ""
        idx = int(seed_str[4:6], 16) % len(photos)
        return photos[idx]["src"]["large"]
    except (KeyError, IndexError):
        return ""


def from_pixabay(topic: str, seed_str: str, title_kw: str = "") -> str:
    if not PIXABAY_KEY:
        return ""
    query = " ".join(title_kw.split()[:3]) if title_kw else " ".join(k.strip() for k in topic.split(",")[:2])
    page = _page_from_seed(seed_str, 10, offset=3)
    data = _fetch_json(
        f"https://pixabay.com/api/"
        f"?key={PIXABAY_KEY}"
        f"&q={urllib.parse.quote(query)}"
        f"&image_type=photo&per_page=3&page={page}&safesearch=true"
    )
    try:
        hits = data.get("hits", [])
        if not hits:
            return ""
        idx = int(seed_str[6:8], 16) % len(hits)
        return hits[idx]["webformatURL"]
    except (KeyError, IndexError):
        return ""


def from_unsplash_api(topic: str, seed_str: str, title_kw: str = "") -> str:
    if not UNSPLASH_KEY:
        return ""
    query = title_kw.split()[0] if title_kw else topic.split(",")[0].strip()
    page = _page_from_seed(seed_str, 10, offset=1)
    data = _fetch_json(
        f"https://api.unsplash.com/search/photos"
        f"?query={urllib.parse.quote(query)}&per_page=3&page={page}",
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    )
    try:
        results = data.get("results", [])
        if not results:
            return ""
        idx = int(seed_str[4:6], 16) % len(results)
        return results[idx]["urls"]["regular"]
    except (KeyError, IndexError):
        return ""


def from_google_cse(topic: str, seed_str: str, title_kw: str = "") -> str:
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_CX:
        return ""
    query = title_kw.split()[0] if title_kw else topic.split(",")[0].strip()
    start = (int(seed_str[:2], 16) % 5) * 2 + 1
    data = _fetch_json(
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_CSE_KEY}&cx={GOOGLE_CSE_CX}"
        f"&q={urllib.parse.quote(query)}&searchType=image"
        f"&num=1&start={start}&imgSize=large&safe=active"
    )
    try:
        return data["items"][0]["link"]
    except (KeyError, IndexError):
        return ""


def from_wikimedia(topic: str, seed_str: str) -> str:
    keyword = topic.split(",")[0].strip()
    data = _fetch_json(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(keyword)}"
    )
    try:
        img = data.get("originalimage", {}).get("source", "")
        if img and any(ext in img.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            return img
    except Exception:
        pass
    return ""


def from_pollinations(prompt_en: str, seed_str: str, w: int = 800, h: int = 450) -> str:
    """AI generate — ช้า 5-10s ใช้เป็น fallback เท่านั้น"""
    prompt = urllib.parse.quote(prompt_en[:200])
    seed_num = int(seed_str[:6], 16) % 99999
    return (
        f"https://image.pollinations.ai/prompt/{prompt}"
        f"?width={w}&height={h}&seed={seed_num}&nologo=true&model=flux"
    )


def from_picsum(seed_str: str, w: int = 800, h: int = 450) -> str:
    return f"https://picsum.photos/seed/{seed_str}/{w}/{h}"


# ══════════════════════════════════════════════════════════════
# 🎯  MAIN
# ══════════════════════════════════════════════════════════════
def get_image_url(
    หัวข้อ: str,
    หมวด: str = "",
    identifier: str = "",
    w: int = 800,
    h: int = 450,
    prefer_ai: bool = False,
    verbose: bool = False,
    no_image: bool = False,
) -> str:
    """
    ดึง URL รูปฟรีตรงเนื้อหา

    Args:
        หัวข้อ:     หัวข้อบทความ (ภาษาไทยหรืออังกฤษ)
        หมวด:       หมวดหมู่ เช่น "food", "travel", "business"
        identifier: filename/slug ไม่ซ้ำกัน — สำคัญมาก!
        w, h:       ขนาดรูป
        prefer_ai:  True → Pollinations ก่อน (ตรง 100% แต่ช้า)
        verbose:    แสดง log
        no_image:   True → คืน "" ทันที ไม่ดึงรูปใดๆ
    """
    # [NEW v10] ถ้าตั้ง no_image → ไม่ดึงรูปใดๆ เลย
    if no_image:
        return ""

    topic    = _get_topic(หมวด, หัวข้อ)
    # [FIX v10] เพิ่ม time_ns ป้องกัน seed ว่างชน
    s        = _seed(identifier or (หัวข้อ + str(time.time_ns())))
    title_kw = _extract_title_keywords(หัวข้อ)

    ai_prompt = (title_kw if title_kw else topic.split(",")[0]) + ", realistic photo, natural lighting"

    def _log(msg):
        if verbose:
            print(f"  [img] {msg}")

    _log(f"'{หัวข้อ[:35]}' → kw='{title_kw}' topic='{topic[:35]}'")

    sources = []

    if prefer_ai:
        sources.append(("pollinations", lambda: from_pollinations(ai_prompt, s, w, h)))

    if PEXELS_KEY:
        sources.append(("pexels",    lambda: from_pexels(topic, s, title_kw)))
    if PIXABAY_KEY:
        sources.append(("pixabay",   lambda: from_pixabay(topic, s, title_kw)))
    if UNSPLASH_KEY:
        sources.append(("unsplash",  lambda: from_unsplash_api(topic, s, title_kw)))
    if GOOGLE_CSE_KEY and GOOGLE_CSE_CX:
        sources.append(("google",    lambda: from_google_cse(topic, s, title_kw)))

    sources.append(("wikimedia",    lambda: from_wikimedia(topic, s)))
    if not prefer_ai:
        sources.append(("pollinations", lambda: from_pollinations(ai_prompt, s, w, h)))
    sources.append(("picsum",       lambda: from_picsum(s, w, h)))

    for name, fn in sources:
        try:
            url = fn()
            if url:
                _log(f"✅ {name}: {url[:70]}")
                return url
        except Exception as e:
            _log(f"⚠️  {name}: {e}")

    return from_picsum(s, w, h)


# ══════════════════════════════════════════════════════════════
# 🔄  BATCH
# ══════════════════════════════════════════════════════════════
def get_image_urls_batch(articles: list, delay: float = 0.3, verbose: bool = True) -> dict:
    results = {}
    for i, art in enumerate(articles):
        ident = art.get("identifier", f"article-{i}")
        results[ident] = get_image_url(
            หัวข้อ=art.get("หัวข้อ", ""),
            หมวด=art.get("หมวด", ""),
            identifier=ident,
            verbose=verbose,
        )
        if i < len(articles) - 1:
            time.sleep(delay)
    return results


# ══════════════════════════════════════════════════════════════
# 🔍  STATUS
# ══════════════════════════════════════════════════════════════
def check_sources_status() -> None:
    print("\n📸  Image Sources Status (v9)")
    print("─" * 58)
    statuses = [
        ("Pexels API",        bool(PEXELS_KEY),                       "PEXELS_KEY",         "www.pexels.com/api/"),
        ("Pixabay API",       bool(PIXABAY_KEY),                      "PIXABAY_KEY",         "pixabay.com/api/docs/"),
        ("Unsplash API",      bool(UNSPLASH_KEY),                     "UNSPLASH_KEY",        "unsplash.com/developers"),
        ("Google CSE",        bool(GOOGLE_CSE_KEY and GOOGLE_CSE_CX), "GOOGLE_CSE_KEY+CX",   "programmablesearchengine.google.com"),
        ("Wikimedia Commons", True,                                   "(ไม่ต้อง key)",       "commons.wikimedia.org"),
        ("Pollinations.ai",   True,                                   "(ไม่ต้อง key, ช้า)", "image.pollinations.ai"),
        ("Lorem Picsum",      True,                                   "(fallback สุดท้าย)",  "picsum.photos"),
    ]
    for name, ok, key_name, signup in statuses:
        print(f"  {'✅' if ok else '❌'} {name:<22} {key_name:<22} {signup}")

    active = sum(1 for _, ok, _, _ in statuses if ok)
    print(f"\n  รวม: {active}/{len(statuses)} sources พร้อมใช้")

    if not PEXELS_KEY:
        print("\n  💡 แนะนำด่วน: สมัคร Pexels API ฟรี ได้รูปตรงเนื้อหาที่สุด")
        print("     www.pexels.com/api/  → ใส่ใน .env: PEXELS_KEY=your_key")

    print("\n  🧪 ทดสอบ keyword extraction:")
    tests = [
        ("ธุรกิจออนไลน์ในช่วงโควิด-19", "business"),
        ("10 วิธีออกกำลังกายที่บ้าน",   "health"),
        ("เคล็ดลับทำอาหารญี่ปุ่นง่ายๆ", "food"),
        ("ดูดวงราศีพิจิกประจำสัปดาห์",  "horoscope"),
    ]
    for title, หมวด in tests:
        kw    = _extract_title_keywords(title)
        topic = _get_topic(หมวด, title)
        print(f"    '{title}'")
        print(f"     kw='{kw}'  query='{topic}'")


if __name__ == "__main__":
    import sys
    check_sources_status()
    if "--test" in sys.argv:
        print("\n🧪 ทดสอบดึงรูป...")
        for หัวข้อ, หมวด, ident in [
            ("ธุรกิจออนไลน์ในช่วงโควิด-19", "business", "test-biz-001"),
            ("10 วิธีออกกำลังกายที่บ้าน",    "health",   "test-health-002"),
            ("เคล็ดลับทำอาหารญี่ปุ่น",        "food",     "test-food-003"),
            ("ดูดวงราศีพิจิก",               "horoscope", "test-horo-004"),
        ]:
            url = get_image_url(หัวข้อ, หมวด, ident, verbose=True)
            print(f"  → {url[:80]}\n")
