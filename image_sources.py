"""
╔══════════════════════════════════════════════════════════════════╗
║  image_sources.py  — ดึงรูปฟรีจากหลายแหล่ง                    ║
║                                                                  ║
║  แหล่งรูปฟรี 100% ไม่เสียเงินทุกกรณี:                         ║
║  1. Unsplash (source.unsplash.com)  — ไม่ต้องใช้ key           ║
║  2. Pexels API                      — ต้องมี PEXELS_KEY         ║
║  3. Pixabay API                     — ต้องมี PIXABAY_KEY        ║
║  4. Lorem Picsum                    — ไม่ต้องใช้ key            ║
║  5. Stable Horde (AI สร้างภาพฟรี)  — ไม่ต้องใช้ key           ║
║  6. Pollinations.ai (AI สร้างภาพ)  — ไม่ต้องใช้ key           ║
║  7. Google Custom Search Images     — ต้องมี GOOGLE_CSE_KEY     ║
║  8. Wikimedia Commons               — ไม่ต้องใช้ key           ║
║                                                                  ║
║  ใช้: from image_sources import get_image_url                   ║
║  >>> url = get_image_url("อาหารไทย", "food", "article-001")    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import re
import hashlib
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# ══════════════════════════════════════════════════════════════
# 🔧  โหลด .env อัตโนมัติ (ไม่ต้องติดตั้ง python-dotenv)
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
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:  # ไม่ทับ env จริงถ้ามีอยู่แล้ว
                os.environ[key] = val

_load_dotenv()

# ══════════════════════════════════════════════════════════════
# 🔑  API KEYS — ใส่ใน .env หรือ environment variable
# ══════════════════════════════════════════════════════════════
PEXELS_KEY      = os.environ.get("PEXELS_KEY", "")
UNSPLASH_KEY    = os.environ.get("UNSPLASH_KEY", "")   # ไม่บังคับ (source. ใช้ได้ฟรี)
PIXABAY_KEY     = os.environ.get("PIXABAY_KEY", "")
GOOGLE_CSE_KEY  = os.environ.get("GOOGLE_CSE_KEY", "")
GOOGLE_CSE_CX   = os.environ.get("GOOGLE_CSE_CX", "")

# ══════════════════════════════════════════════════════════════
# 🗂️  Topic map — หัวข้อภาษาไทย → keyword ภาษาอังกฤษ
# ══════════════════════════════════════════════════════════════
_TOPIC_MAP = {
    # หมวดหลัก
    "อาหาร":       "food,meal,cuisine,cooking",
    "food":        "food,meal,restaurant,cuisine",
    "cooking":     "cooking,kitchen,food,recipe",
    "สุขภาพ":      "healthcare,wellness,fitness,medical",
    "health":      "healthcare,wellness,medical,hospital",
    "กีฬา":        "sport,fitness,exercise,athlete",
    "sport":       "sport,fitness,exercise,stadium",
    "ท่องเที่ยว":  "travel,landscape,destination,adventure",
    "travel":      "travel,landscape,destination,adventure",
    "เทคโนโลยี":  "technology,computer,digital,innovation",
    "technology":  "technology,computer,digital,innovation",
    "gaming":      "gaming,esports,controller,game",
    "เกม":         "gaming,esports,controller,game",
    "การเงิน":     "finance,money,investment,banking",
    "finance":     "finance,money,investment,banking",
    "business":    "business,office,corporate,finance",
    "ธุรกิจ":      "business,office,corporate,finance",
    "ความงาม":     "beauty,cosmetics,skincare,makeup",
    "beauty":      "beauty,cosmetics,skincare,makeup",
    "ดูดวง":       "stars,astrology,zodiac,horoscope",
    "horoscope":   "stars,astrology,zodiac,moon",
    "บันเทิง":     "entertainment,concert,show,celebrity",
    "entertainment": "entertainment,show,concert,stage",
    "ข่าว":        "news,newspaper,journalism,media",
    "news":        "news,newspaper,journalism,media",
    "สัตว์":       "animal,pet,nature,wildlife",
    "pet":         "pet,dog,cat,animal",
    "รถ":          "car,automobile,vehicle,road",
    "car":         "car,automobile,vehicle,road",
    "กฎหมาย":      "law,justice,courthouse,legal",
    "law":         "law,justice,courthouse,legal",
    "การ์ตูน":     "animation,cartoon,colorful,creative",
    "cartoon":     "animation,cartoon,colorful,creative",
    "anime":       "japan,illustration,art,anime",
    "ไลฟ์สไตล์":  "lifestyle,living,home,relax",
    "lifestyle":   "lifestyle,living,home,relax",
    "ผี":          "mystery,horror,dark,night",
    "ghost":       "mystery,horror,dark,supernatural",
    "ลอตเตอรี":   "lucky,numbers,win,lottery",
    "lottery":     "lucky,numbers,win,lottery",
    "หนัง":        "movie,cinema,film,popcorn",
    "movie":       "movie,cinema,film,popcorn",
    "เคล็ดลับ":   "tips,advice,guide,learning",
    "tips":        "tips,advice,guide,learning",
}

_DEFAULT_TOPIC = "lifestyle,nature,people"


def _get_topic(หมวด: str, หัวข้อ: str = "") -> str:
    """แปลงหมวด/หัวข้อภาษาไทย-อังกฤษ → keyword สำหรับ API"""
    combined = (หมวด + " " + หัวข้อ).lower()
    for kw, topic in _TOPIC_MAP.items():
        if kw in combined:
            return topic
    return _DEFAULT_TOPIC


def _seed(identifier: str) -> str:
    """สร้าง seed จาก identifier เพื่อให้รูปต่างกันทุกบทความ
    ถ้า identifier ว่าง → ใช้ timestamp เพื่อป้องกันซ้ำ
    """
    key = identifier.strip() if identifier.strip() else str(time.time_ns())
    return hashlib.md5(key.encode()).hexdigest()[:10]


def _fetch_json(url: str, headers: dict = None, timeout: int = 8) -> dict:
    """HTTP GET → parse JSON"""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 1: Unsplash (ไม่ต้อง key — source.unsplash.com)
# ══════════════════════════════════════════════════════════════
def from_unsplash_source(topic: str, seed_str: str, w=800, h=450) -> str:
    """
    source.unsplash.com — ฟรี ไม่ต้อง key
    แต่ Unsplash ปิด endpoint นี้แล้วในปี 2023
    fallback → picsum
    """
    keyword = topic.split(",")[0].strip()
    url = f"https://source.unsplash.com/featured/{w}x{h}/?{urllib.parse.quote(keyword)}&sig={seed_str}"
    return url  # return URL ตรงๆ (redirect image)


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 2: Unsplash API (ต้องมี UNSPLASH_KEY)
# ══════════════════════════════════════════════════════════════
def from_unsplash_api(topic: str, seed_str: str) -> str:
    """Unsplash API — ฟรี 50 req/hr (ต้องลงทะเบียน developers.unsplash.com)"""
    if not UNSPLASH_KEY:
        return ""
    keyword = topic.split(",")[0].strip()
    page = (int(seed_str[:4], 16) % 10) + 1
    data = _fetch_json(
        f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(keyword)}&per_page=1&page={page}",
        headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    )
    try:
        return data["results"][0]["urls"]["regular"]
    except (KeyError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 3: Pexels API (ต้องมี PEXELS_KEY — ฟรีตลอด)
# ══════════════════════════════════════════════════════════════
def from_pexels(topic: str, seed_str: str) -> str:
    """
    Pexels — ฟรี ไม่จำกัด ต้องลงทะเบียน www.pexels.com/api/
    ได้รูปตรงหัวข้อ 100%
    """
    if not PEXELS_KEY:
        return ""
    # ใช้ 2 keyword แรกเพื่อให้ผลลัพธ์ตรงเนื้อหากว่าใช้คำเดียว
    keywords = [k.strip() for k in topic.split(",")[:2]]
    keyword = " ".join(keywords)
    page = (int(seed_str[:4], 16) % 20) + 1
    data = _fetch_json(
        f"https://api.pexels.com/v1/search?query={urllib.parse.quote(keyword)}&per_page=1&page={page}",
        headers={"Authorization": PEXELS_KEY}
    )
    try:
        return data["photos"][0]["src"]["large"]
    except (KeyError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 4: Pixabay API (ต้องมี PIXABAY_KEY — ฟรีตลอด)
# ══════════════════════════════════════════════════════════════
def from_pixabay(topic: str, seed_str: str) -> str:
    """
    Pixabay — ฟรี ลงทะเบียนที่ pixabay.com/api/docs/
    200 req/hr, รูป CC0 ใช้ได้เสรี
    """
    if not PIXABAY_KEY:
        return ""
    keywords = [k.strip() for k in topic.split(",")[:2]]
    keyword = " ".join(keywords)
    page = (int(seed_str[:4], 16) % 10) + 1
    data = _fetch_json(
        f"https://pixabay.com/api/?key={PIXABAY_KEY}"
        f"&q={urllib.parse.quote(keyword)}&image_type=photo"
        f"&per_page=3&page={page}&safesearch=true"
    )
    try:
        hits = data.get("hits", [])
        idx = int(seed_str[4:6], 16) % max(len(hits), 1)
        return hits[idx]["webformatURL"]
    except (KeyError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 5: Wikimedia Commons (ไม่ต้อง key — ใช้ฟรีตลอด)
# ══════════════════════════════════════════════════════════════
def from_wikimedia(topic: str, seed_str: str) -> str:
    """
    Wikimedia Commons — ไม่ต้อง key, CC license, ฟรีตลอด
    เหมาะกับหัวข้อทั่วไป/วิชาการ
    """
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


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 6: Pollinations.ai (AI สร้างภาพฟรี — ไม่ต้อง key)
# ══════════════════════════════════════════════════════════════
def from_pollinations(prompt_th: str, seed_str: str, w=800, h=450) -> str:
    """
    Pollinations.ai — AI generate รูปฟรี ไม่ต้อง key
    ส่ง prompt ภาษาไทยหรืออังกฤษก็ได้
    URL format: https://image.pollinations.ai/prompt/{prompt}?width=800&height=450&seed=123&nologo=true
    """
    prompt = urllib.parse.quote(prompt_th[:200])
    seed_num = int(seed_str[:6], 16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{prompt}"
        f"?width={w}&height={h}&seed={seed_num}&nologo=true&model=flux"
    )
    return url


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 7: Lorem Picsum (ไม่ต้อง key — fallback ดีที่สุด)
# ══════════════════════════════════════════════════════════════
def from_picsum(seed_str: str, w=800, h=450) -> str:
    """Lorem Picsum — ฟรีตลอด ไม่ต้อง key รูปสวยแต่ไม่ตรงเนื้อหา"""
    return f"https://picsum.photos/seed/{seed_str}/{w}/{h}"


# ══════════════════════════════════════════════════════════════
# 📸  SOURCE 8: Google Custom Search Images (ต้อง key + cx)
# ══════════════════════════════════════════════════════════════
def from_google_cse(topic: str, seed_str: str) -> str:
    """
    Google Custom Search Engine — ฟรี 100 req/วัน
    ต้องสร้าง CSE ที่ programmablesearchengine.google.com
    และ enable Image Search
    """
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_CX:
        return ""
    keyword = topic.split(",")[0].strip()
    start = (int(seed_str[:2], 16) % 5) * 2 + 1
    data = _fetch_json(
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={GOOGLE_CSE_KEY}&cx={GOOGLE_CSE_CX}"
        f"&q={urllib.parse.quote(keyword)}&searchType=image"
        f"&num=1&start={start}&imgSize=large&safe=active"
    )
    try:
        return data["items"][0]["link"]
    except (KeyError, IndexError):
        return ""


# ══════════════════════════════════════════════════════════════
# 🎯  MAIN FUNCTION — ลองทุก source ตามลำดับ priority
# ══════════════════════════════════════════════════════════════
def get_image_url(
    หัวข้อ: str,
    หมวด: str = "",
    identifier: str = "",
    w: int = 800,
    h: int = 450,
    prefer_ai: bool = False,
    verbose: bool = False,
) -> str:
    """
    ดึง URL รูปฟรีตรงเนื้อหา ลองทุก source ตามลำดับ

    Args:
        หัวข้อ:     หัวข้อบทความ (ภาษาไทยหรืออังกฤษ)
        หมวด:       หมวดหมู่บทความ เช่น "food", "travel"
        identifier: ชื่อไฟล์หรือ slug สำหรับสร้าง seed (ห้ามซ้ำ)
        w, h:       ขนาดรูป
        prefer_ai:  ถ้า True → ใช้ Pollinations ก่อน (AI generate)
        verbose:    แสดง log

    Returns:
        URL รูปภาพที่ใช้ได้จริง (fallback → picsum ถ้าทุกอย่างพัง)
    """
    topic  = _get_topic(หมวด, หัวข้อ)
    s = _seed(identifier or (หัวข้อ + str(time.time_ns())))
    prompt = f"{หัวข้อ}, {topic.split(',')[0]}, high quality photo, realistic"

    def _log(msg):
        if verbose:
            print(f"  [img] {msg}")

    # ── ลำดับ priority ───────────────────────────────────────
    sources = []

    if prefer_ai:
        # AI generate ก่อน → ตรงเนื้อหา 100% แต่ช้ากว่า
        sources.append(("pollinations", lambda: from_pollinations(prompt, s, w, h)))

    if PEXELS_KEY:
        sources.append(("pexels",    lambda: from_pexels(topic, s)))
    if PIXABAY_KEY:
        sources.append(("pixabay",   lambda: from_pixabay(topic, s)))
    if UNSPLASH_KEY:
        sources.append(("unsplash",  lambda: from_unsplash_api(topic, s)))
    if GOOGLE_CSE_KEY and GOOGLE_CSE_CX:
        sources.append(("google",    lambda: from_google_cse(topic, s)))

    # ไม่ต้อง key — Pollinations ก่อนเสมอ (seed ทำงานจริง ไม่ซ้ำ)
    # source.unsplash.com และ wikimedia ไม่สนใจ seed → ซ้ำได้
    if not prefer_ai:
        sources.append(("pollinations", lambda: from_pollinations(prompt, s, w, h)))

    sources.append(("wikimedia",    lambda: from_wikimedia(topic, s)))

    # picsum เป็น fallback สุดท้ายเสมอ
    sources.append(("picsum",       lambda: from_picsum(s, w, h)))

    for name, fn in sources:
        try:
            url = fn()
            if url:
                _log(f"✅ {name}: {url[:60]}...")
                return url
        except Exception as e:
            _log(f"⚠️  {name} error: {e}")
            continue

    # ป้องกัน edge case
    return from_picsum(s, w, h)


# ══════════════════════════════════════════════════════════════
# 🔄  BATCH — ดึงรูปหลายบทความพร้อมกัน (มี delay ป้องกัน rate limit)
# ══════════════════════════════════════════════════════════════
def get_image_urls_batch(
    articles: list[dict],
    delay: float = 0.3,
    verbose: bool = True,
) -> dict[str, str]:
    """
    ดึงรูปหลายบทความ

    Args:
        articles: list of {"identifier": str, "หัวข้อ": str, "หมวด": str}
        delay:    วินาทีรอระหว่าง request (ป้องกัน rate limit)

    Returns:
        dict: {identifier: url}
    """
    results = {}
    for i, art in enumerate(articles):
        ident = art.get("identifier", f"article-{i}")
        url = get_image_url(
            หัวข้อ=art.get("หัวข้อ", ""),
            หมวด=art.get("หมวด", ""),
            identifier=ident,
            verbose=verbose,
        )
        results[ident] = url
        if i < len(articles) - 1:
            time.sleep(delay)
    return results


# ══════════════════════════════════════════════════════════════
# 🔍  STATUS — ตรวจสอบว่า source ไหนใช้ได้บ้าง
# ══════════════════════════════════════════════════════════════
def check_sources_status() -> None:
    """แสดงสถานะของทุก source"""
    print("\n📸  Image Sources Status")
    print("─" * 50)

    statuses = [
        ("Pexels API",         bool(PEXELS_KEY),   "PEXELS_KEY",     "www.pexels.com/api/"),
        ("Pixabay API",        bool(PIXABAY_KEY),  "PIXABAY_KEY",    "pixabay.com/api/docs/"),
        ("Unsplash API",       bool(UNSPLASH_KEY), "UNSPLASH_KEY",   "unsplash.com/developers"),
        ("Google CSE Images",  bool(GOOGLE_CSE_KEY and GOOGLE_CSE_CX), "GOOGLE_CSE_KEY+CX", "programmablesearchengine.google.com"),
        ("Pollinations.ai",    True,               "(ไม่ต้อง key)",  "image.pollinations.ai"),
        ("Wikimedia Commons",  True,               "(ไม่ต้อง key)",  "commons.wikimedia.org"),
        ("Lorem Picsum",       True,               "(ไม่ต้อง key)",  "picsum.photos"),
    ]

    for name, ok, key_name, signup in statuses:
        status = "✅ พร้อมใช้" if ok else f"❌ ไม่มี {key_name}"
        print(f"  {status:<25} {name:<22} ({signup})")

    print()
    active = sum(1 for _, ok, _, _ in statuses if ok)
    print(f"  รวม: {active}/{len(statuses)} sources พร้อมใช้")
    if active < 3:
        print("\n  💡 แนะนำ: สมัคร Pexels API ฟรี (www.pexels.com/api/)")
        print("     ได้รูปตรงเนื้อหา ไม่จำกัด ไม่เสียเงิน")


# ══════════════════════════════════════════════════════════════
# 🧪  ทดสอบ
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    check_sources_status()

    if "--test" in sys.argv:
        print("\n🧪 ทดสอบดึงรูป...")
        test_cases = [
            ("เคล็ดลับทำอาหารให้สุขภาพดี", "food",        "test-food-001"),
            ("10 สถานที่ท่องเที่ยวในกรุงเทพ", "travel",   "test-travel-002"),
            ("เกมมือถือยอดนิยม 2025",        "gaming",     "test-game-003"),
            ("ดูดวงราศีพิจิก",               "horoscope",  "test-horo-004"),
        ]
        for หัวข้อ, หมวด, ident in test_cases:
            url = get_image_url(หัวข้อ, หมวด, ident, verbose=True)
            print(f"\n  📌 {หัวข้อ}")
            print(f"     → {url}")
