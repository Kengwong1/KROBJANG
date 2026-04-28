"""
╔══════════════════════════════════════════════════════════════════╗
║  image_sources.py  v13.0 — [FIX B] keyword priority fix         ║
╠══════════════════════════════════════════════════════════════════╣
║  แก้ไข v13.0:                                                     ║
║  [B] เพิ่ม keyword ผม/ทรงผม/ตัดผม/เส้นผม ก่อนคำกว้าง (บ้าน)    ║
║      เพราะ sorted(key=len, reverse=True) จะดักคำยาวก่อนแต่        ║
║      "ทำผมสวยที่บ้าน" มีทั้ง "บ้าน" กับ "ผม" → ต้องมีทั้งคู่     ║
║  [B] เพิ่ม mapping หลายหมวดที่ขาด: ผิวหนัง, นอน, สัตว์เลี้ยง ฯลฯ ║
║  Fallback Chain:                                                  ║
║  1. Fooocus  → generate รูปตรงเนื้อหา 100% (local AI, port 7865) ║
║  2. Pexels   → stock photo คุณภาพดี                               ║
║  3. Pixabay  → stock photo สำรอง 1                                ║
║  4. Unsplash → stock photo สำรอง 2                                ║
║  5. Picsum   → random (รับประกันมีรูปเสมอ)                        ║
╚══════════════════════════════════════════════════════════════════╝
"""
import os, re, hashlib, time, json, urllib.request, urllib.parse, urllib.error
from pathlib import Path

# ── API Keys ──────────────────────────────────────────────────────
PEXELS_KEY   = os.getenv("PEXELS_KEY", "")
PIXABAY_KEY  = os.getenv("PIXABAY_KEY", "")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY", "")
FOOOCUS_HOST = os.getenv("FOOOCUS_HOST", "http://127.0.0.1:7865")

# ── Fooocus Config ────────────────────────────────────────────────
FOOOCUS_PERFORMANCE  = "Speed"
FOOOCUS_ASPECT_RATIO = "1152*896"
FOOOCUS_STYLE = [
    "Fooocus V2",
    "Fooocus Enhance",
    "Fooocus Sharp",
    "Fooocus Masterpiece",
]
FOOOCUS_NEGATIVE = (
    "text, watermark, logo, signature, blurry, low quality, "
    "ugly, deformed, nsfw, violence, cartoon, anime style"
)
FOOOCUS_TIMEOUT  = 120
FOOOCUS_FN_INDEX = 67

# ══════════════════════════════════════════════════════════════════
# 📖  ตารางแปลคำไทย → อังกฤษ
# [FIX B] เพิ่ม keyword เฉพาะทางมากขึ้น เรียงจากเฉพาะ→กว้าง
#         sorted(key=len, reverse=True) จะดักคำยาวก่อนอยู่แล้ว
#         แต่ต้องให้ครบทั้งหมวดหมู่
# ══════════════════════════════════════════════════════════════════
_TH_MAP = {
    # ── ผม / ทรงผม (เพิ่มใหม่ [FIX B]) ──────────────────────────
    "ทำผมสวย":    "hair styling beautiful woman",
    "ทำผมเอง":    "DIY hair styling home",
    "ทำผมที่บ้าน": "home hair styling self",
    "ทรงผม":      "hairstyle haircut",
    "ตัดผม":      "haircut barber salon",
    "เส้นผม":     "hair care treatment",
    "ผมยาว":      "long hair woman",
    "ผมสั้น":     "short hair woman",
    "ผมหยิก":     "curly hair",
    "ผมตรง":      "straight hair woman",
    "ย้อมผม":     "hair dye color",
    "ดูแลผม":     "hair care treatment",
    "ผมเสีย":     "damaged hair treatment",
    "ผม":         "hair grooming",

    # ── ผิว / สกิน (เพิ่มใหม่) ────────────────────────────────
    "ผิวหน้า":    "skincare face woman",
    "ดูแลผิว":    "skincare routine",
    "ผิวสวย":     "beautiful skin glowing",
    "ลดสิว":      "acne skincare treatment",
    "กันแดด":     "sunscreen skincare",

    # ── ธุรกิจ / การเงิน ─────────────────────────────────────────
    "ธุรกิจ":    "business professional",
    "การเงิน":   "finance money",
    "หุ้น":      "stock market trading",
    "ประกัน":    "insurance protection",
    "การตลาด":   "marketing strategy",
    "ลงทุน":     "investment finance",
    "บัญชี":     "accounting finance",
    "ภาษี":      "tax finance documents",
    "เงินเดือน": "salary paycheck",
    "ธนาคาร":    "bank banking",

    # ── เทคโนโลยี ─────────────────────────────────────────────────
    "เทคโนโลยี": "technology digital",
    "คอมพิวเตอร์":"laptop computer",
    "มือถือ":    "smartphone mobile",
    "ซ่อม":      "repair technician",
    "โปรแกรม":   "software coding",
    "แอป":       "mobile app smartphone",
    "อินเทอร์เน็ต":"internet wifi",
    "ไซเบอร์":   "cybersecurity digital",
    "เอไอ":      "artificial intelligence",
    "เกม":       "gaming computer",

    # ── สุขภาพ ────────────────────────────────────────────────────
    "ออกกำลังกาย":"fitness gym workout",
    "โภชนาการ":  "nutrition healthy food",
    "นอนหลับ":   "sleep rest bedroom",
    "สุขภาพ":    "healthcare wellness",
    "แพทย์":     "doctor medical",
    "โรงพยาบาล": "hospital medical",
    "ยา":        "medicine pharmacy",
    "จิตใจ":     "mental health wellness",

    # ── อาหาร ─────────────────────────────────────────────────────
    "ทำอาหาร":   "cooking kitchen",
    "เบเกอรี่":  "bakery pastry",
    "ร้านอาหาร": "restaurant dining",
    "อาหาร":     "food cooking meal",
    "ขนม":       "dessert pastry",
    "เครื่องดื่ม":"drinks beverage",

    # ── ท่องเที่ยว ────────────────────────────────────────────────
    "เที่ยวทะเล": "beach vacation travel",
    "ท่องเที่ยว": "travel destination",
    "ต่างประเทศ": "travel abroad international",
    "กระเป๋าเดินทาง": "travel luggage suitcase packing",
    "แพ็คกระเป๋า": "packing suitcase travel",
    "กระเป๋า":   "bag luggage travel",
    "แพ็ค":      "packing travel checklist",
    "เดินทาง":   "travel journey trip",
    "ชายหาด":    "beach sand tropical",
    "ทะเล":      "beach ocean sea",
    "ภูเขา":     "mountain nature",
    "กรุงเทพ":   "Bangkok Thailand city",
    "โรงแรม":    "hotel accommodation",
    "checklist": "travel checklist packing",
    "trip":      "travel trip vacation",

    # ── บ้าน ──────────────────────────────────────────────────────
    "ตกแต่ง":    "home decoration interior",
    "เฟอร์นิเจอร์":"furniture interior design",
    "ครัว":      "kitchen cooking modern",
    "สวน":       "garden plants outdoor",
    "บ้าน":      "home interior",

    # ── การศึกษา ──────────────────────────────────────────────────
    "การศึกษา":  "education learning",
    "เรียน":     "student studying",
    "หนังสือ":   "books reading library",
    "ทักษะ":     "skills professional",
    "อาชีพ":     "career profession office",

    # ── ความงาม ───────────────────────────────────────────────────
    "เครื่องสำอาง":"makeup cosmetics beauty",
    "ความงาม":   "beauty skincare cosmetics",
    "แฟชั่น":    "fashion style clothing",
    "เสื้อผ้า":  "clothing fashion model",

    # ── ยานพาหนะ ──────────────────────────────────────────────────
    "มอเตอร์ไซค์":"motorcycle road",
    "รถยนต์":    "car automotive",
    "รถ":        "car vehicle road",

    # ── บันเทิง ───────────────────────────────────────────────────
    "อนิเมะ":    "colorful illustration entertainment",
    "หนัง":      "cinema movie entertainment",
    "ดนตรี":     "music concert performance",
    "กีฬา":      "sports athletic action",
    "ศิลปะ":     "art creative colorful",

    # ── สัตว์เลี้ยง (เพิ่มใหม่) ────────────────────────────────
    "สัตว์เลี้ยง": "pets animals cute",
    "แมว":       "cat kitten cute",
    "สุนัข":     "dog puppy cute",
    "สัตว์":     "animals pets cute",

    # ── อื่นๆ ──────────────────────────────────────────────────────
    "ครอบครัว":  "family together happy",
    "เด็ก":      "children kids playing",
    "ผู้สูงอายุ": "elderly senior lifestyle",
    "สิ่งแวดล้อม":"environment nature green",
    "พลังงาน":   "energy solar renewable",
}

# ══════════════════════════════════════════════════════════════════
# 🔑  Keyword & Prompt Builder
# ══════════════════════════════════════════════════════════════════

def _extract_title_keywords(title: str, หมวด: str = "") -> str:
    """
    สกัด keyword ภาษาอังกฤษจากหัวข้อไทย
    [FIX B] sorted(key=len, reverse=True) ให้ดักคำยาว (เฉพาะ) ก่อน
    เช่น "ทำผมสวยที่บ้าน" → ดัก "ทำผมสวย" → "hair styling beautiful woman"
         แล้วค่อยดัก "บ้าน" → "home interior" ด้วย (ไม่ overwrite)
    """
    title_lower = title.lower()
    keywords = []

    # 1. คำอังกฤษในหัวข้อ
    keywords.extend(w.lower() for w in re.findall(r'[a-zA-Z]{3,}', title))

    # 2. mapping ไทย (คำยาวก่อน = เฉพาะเจาะจงก่อน)
    for th in sorted(_TH_MAP, key=len, reverse=True):
        if th in title_lower:
            keywords.extend(_TH_MAP[th].split())

    # 3. หมวดหมู่
    if หมวด:
        หมวด_l = หมวด.lower()
        if หมวด_l in _TH_MAP:
            keywords.extend(_TH_MAP[หมวด_l].split())
        else:
            keywords.extend(w.lower() for w in re.findall(r'[a-zA-Z]{3,}', หมวด))

    # กรอง stop words
    stop = {"the","and","for","are","this","that","with","from","have"}
    keywords = [k for k in keywords if k not in stop and len(k) >= 3]

    if not keywords:
        keywords = ["lifestyle", "professional"]

    # dedup + จำกัด 5 คำ
    seen, unique = set(), []
    for k in keywords:
        if k not in seen:
            seen.add(k); unique.append(k)
        if len(unique) >= 5:
            break
    return " ".join(unique)


def _build_fooocus_prompt(title: str, หมวด: str = "") -> str:
    """สร้าง prompt สำหรับ Fooocus จาก title"""
    kw = _extract_title_keywords(title, หมวด)
    return (
        f"professional editorial photo, {kw}, "
        "photorealistic, high quality, sharp focus, "
        "well-lit, modern, clean composition, "
        "suitable for blog article header, wide angle"
    )

# ══════════════════════════════════════════════════════════════════
# 🌱  Seed Helpers
# ══════════════════════════════════════════════════════════════════

def _make_seed_index(identifier: str) -> int:
    return int(hashlib.md5(identifier.encode()).hexdigest(), 16)

def _make_fooocus_seed(identifier: str) -> int:
    return int(hashlib.md5(identifier.encode()).hexdigest()[:8], 16)

def _make_picsum_seed(identifier: str) -> str:
    return hashlib.md5(identifier.encode()).hexdigest()[:12]

# ══════════════════════════════════════════════════════════════════
# 🤖  [PRIMARY] Fooocus — Generate รูปตรงเนื้อหา
# ══════════════════════════════════════════════════════════════════

def _check_fooocus_alive() -> bool:
    """Ping Fooocus Gradio UI ที่ port 7865"""
    try:
        req = urllib.request.Request(
            f"{FOOOCUS_HOST}/info",
            method="GET",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status == 200
    except Exception:
        pass
    try:
        req = urllib.request.Request(
            f"{FOOOCUS_HOST}/",
            method="GET",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status < 500
    except Exception:
        return False


def _get_fooocus_session_hash() -> str:
    import random, string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def _make_fooocus_data(prompt: str, seed: int) -> list:
    """สร้าง data array ครบ 152 inputs สำหรับ Fooocus 2.5.5 fn_index=67"""
    d = [None] * 152

    d[0]  = False; d[1]  = prompt; d[2]  = FOOOCUS_NEGATIVE
    d[3]  = FOOOCUS_STYLE; d[4]  = FOOOCUS_PERFORMANCE
    d[5]  = FOOOCUS_ASPECT_RATIO; d[6]  = 1; d[7]  = "png"
    d[8]  = str(seed); d[9]  = False
    d[10] = 2.0; d[11] = 4.0
    d[12] = "juggernautXL_v8Rundiffusion.safetensors"
    d[13] = "None"; d[14] = 0.5
    d[15] = True;  d[16] = "None"; d[17] = 1.0
    d[18] = True;  d[19] = "None"; d[20] = 1.0
    d[21] = True;  d[22] = "None"; d[23] = 1.0
    d[24] = True;  d[25] = "None"; d[26] = 1.0
    d[27] = True;  d[28] = "None"; d[29] = 1.0
    d[30] = False; d[31] = ""; d[32] = "Disabled"
    d[33] = None; d[34] = []; d[35] = None; d[36] = ""; d[37] = None
    d[38] = False; d[39] = False; d[40] = False; d[41] = False
    d[42] = 1.5; d[43] = 0.8; d[44] = 0.3; d[45] = 7.0; d[46] = 2
    d[47] = "dpmpp_2m_sde_gpu"; d[48] = "karras"; d[49] = "Default (model)"
    d[50] = -1; d[51] = -1; d[52] = -1; d[53] = -1; d[54] = -1; d[55] = -1
    d[56] = False; d[57] = False; d[58] = False; d[59] = False
    d[60] = 64; d[61] = 128; d[62] = "joint"; d[63] = 0.25
    d[64] = False; d[65] = 1.01; d[66] = 1.02; d[67] = 0.99; d[68] = 0.95
    d[69] = False; d[70] = False; d[71] = "v2.6"
    d[72] = 1.0; d[73] = 0.618; d[74] = False; d[75] = False; d[76] = 0
    d[77] = False; d[78] = False; d[79] = "fooocus"

    for i in range(4):
        b = 80 + i * 4
        d[b] = None; d[b+1] = 0.5; d[b+2] = 0.6; d[b+3] = "ImagePrompt"

    d[96] = False; d[97] = 0; d[98] = False; d[99] = None
    d[100] = False; d[101] = "Disabled"
    d[102] = "Before First Enhancement"; d[103] = "Original Prompts"

    for slot in range(3):
        b = 104 + slot * 16
        d[b]    = False; d[b+1]  = ""; d[b+2]  = ""; d[b+3]  = ""
        d[b+4]  = "u2net"; d[b+5]  = "full"; d[b+6]  = "vit_b"
        d[b+7]  = 0.25; d[b+8]  = 0.3; d[b+9]  = 4
        d[b+10] = False; d[b+11] = "v2.6"; d[b+12] = 0.5
        d[b+13] = 0.618; d[b+14] = 0; d[b+15] = False

    return d


def _get_fooocus_img(title: str, หมวด: str, identifier: str) -> str:
    if not _check_fooocus_alive():
        return ""
    prompt = _build_fooocus_prompt(title, หมวด)
    seed   = _make_fooocus_seed(identifier)
    try:
        payload = json.dumps({
            "prompt":                  prompt,
            "negative_prompt":         FOOOCUS_NEGATIVE,
            "style_selections":        FOOOCUS_STYLE,
            "performance_selection":   FOOOCUS_PERFORMANCE,
            "aspect_ratios_selection": FOOOCUS_ASPECT_RATIO,
            "image_number":            1,
            "image_seed":              seed,
            "sharpness":               2.0,
            "guidance_scale":          4.0,
            "save_meta":               False,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{FOOOCUS_HOST}/v1/generation/text-to-image",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
        if not isinstance(data, list) or not data:
            return ""
        item = data[0]
        url = item.get("url", "")
        if url.startswith("http"):
            return url
        if url:
            return f"{FOOOCUS_HOST}/{url.lstrip('/')}"
    except Exception:
        pass
    return ""

# ══════════════════════════════════════════════════════════════════
# 📷  Stock API Fetchers (Fallback)
# ══════════════════════════════════════════════════════════════════

def _get_pexels_img(query: str, idx: int) -> str:
    if not PEXELS_KEY: return ""
    try:
        page = (idx // 30) + 1
        slot = idx % 30
        p = urllib.parse.urlencode({
            "query": query, "per_page": 30,
            "orientation": "landscape", "page": page,
        })
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?{p}",
            headers={"Authorization": PEXELS_KEY}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            photos = json.loads(r.read()).get("photos", [])
        if photos:
            return photos[slot % len(photos)]["src"]["large2x"]
    except Exception: pass
    return ""


def _get_pixabay_img(query: str, idx: int) -> str:
    if not PIXABAY_KEY: return ""
    try:
        page = (idx // 20) + 1
        slot = idx % 20
        p = urllib.parse.urlencode({
            "key": PIXABAY_KEY, "q": query,
            "image_type": "photo", "orientation": "horizontal",
            "per_page": 20, "safesearch": "true", "page": page,
        })
        with urllib.request.urlopen(f"https://pixabay.com/api/?{p}", timeout=6) as r:
            hits = json.loads(r.read()).get("hits", [])
        if hits:
            return hits[slot % len(hits)]["largeImageURL"]
    except Exception: pass
    return ""


def _get_unsplash_img(query: str, idx: int) -> str:
    if not UNSPLASH_KEY: return ""
    try:
        page = (idx // 20) + 1
        slot = idx % 20
        p = urllib.parse.urlencode({
            "query": query, "per_page": 20, "page": page,
            "orientation": "landscape", "client_id": UNSPLASH_KEY,
        })
        with urllib.request.urlopen(
            f"https://api.unsplash.com/search/photos?{p}", timeout=6
        ) as r:
            results = json.loads(r.read()).get("results", [])
        if results:
            return results[slot % len(results)]["urls"]["regular"]
    except Exception: pass
    return ""

# ══════════════════════════════════════════════════════════════════
# 📂  Local Library Lookup
# ══════════════════════════════════════════════════════════════════

_LOCAL_INDEX_CACHE: dict = {}

def _load_local_index(cat: str) -> list:
    if cat not in _LOCAL_INDEX_CACHE:
        try:
            from config import BASE_PATH
            idx_file = BASE_PATH / "images" / "thumbs" / cat / "_index.json"
        except ImportError:
            idx_file = Path(__file__).parent / "images" / "thumbs" / cat / "_index.json"
        if idx_file.exists():
            try:
                _LOCAL_INDEX_CACHE[cat] = json.loads(idx_file.read_text(encoding="utf-8"))
            except Exception:
                _LOCAL_INDEX_CACHE[cat] = []
        else:
            _LOCAL_INDEX_CACHE[cat] = []
    return _LOCAL_INDEX_CACHE[cat]

def _get_local_img(หมวด: str, ident: str, หัวข้อ: str = "") -> str:
    """
    คืน relative path รูปจาก local library
    - ถ้ามี description (tag แล้ว) → smart match กับหัวข้อ
    - ถ้ายังไม่ tag → สุ่มตาม hash (stable)
    """
    records = _load_local_index(หมวด)
    if not records:
        return ""

    # ── smart match ถ้ามี description ──────────────────────────
    if หัวข้อ:
        tagged = [r for r in records if r.get("description", "").strip()]
        if tagged:
            kw_en = _extract_title_keywords(หัวข้อ, หมวด).lower().split()
            best_score, best_record = -1, None
            for r in tagged:
                desc  = r.get("description", "").lower()
                score = sum(1 for kw in kw_en if kw in desc)
                if score > best_score:
                    best_score, best_record = score, r
            if best_record:
                path = best_record.get("path", "")
                return path or f"images/thumbs/{หมวด}/{best_record['file']}"

    # ── fallback: hash-stable random ────────────────────────────
    seed   = int(hashlib.md5(ident.encode()).hexdigest(), 16)
    record = records[seed % len(records)]
    path = record.get("path", "")
    return path or f"images/thumbs/{หมวด}/{record['file']}"

# ══════════════════════════════════════════════════════════════════
# 🎯  ฟังก์ชันหลัก
# ══════════════════════════════════════════════════════════════════

def get_image_url(หัวข้อ: str = "", หมวด: str = "", identifier: str = "") -> str:
    """
    เลือก/สร้างรูปภาพที่ตรงกับเนื้อหา

    Fallback chain:
        Local Library (เร็ว ตรงหมวด 100%)
            ↓
        Fooocus (AI generate)
            ↓
        Pexels → Pixabay → Unsplash  (stock photo)
            ↓
        Picsum  (guaranteed)
    """
    ident = identifier or หัวข้อ or หมวด or "default"
    idx   = _make_seed_index(ident)
    kw    = _extract_title_keywords(หัวข้อ, หมวด)

    # ── 0. Local library ก่อนเลย (smart match ถ้า tag แล้ว) ──
    if หมวด:
        img = _get_local_img(หมวด, ident, หัวข้อ)
        if img: return img

    # ── 1. Fooocus AI ──────────────────────────────────────────
    img = _get_fooocus_img(หัวข้อ, หมวด, ident)
    if img: return img

    # ── 2. Stock APIs ──────────────────────────────────────────
    img = _get_pexels_img(kw, idx)
    if img: return img

    img = _get_pixabay_img(kw, idx)
    if img: return img

    img = _get_unsplash_img(kw, idx)
    if img: return img

    return f"https://picsum.photos/seed/{_make_picsum_seed(ident)}/1200/630"


# ══════════════════════════════════════════════════════════════════
# 🏷️  Credit Helper — ดึง credit จาก _index.json
# ══════════════════════════════════════════════════════════════════

def get_image_credit(img_path: str) -> str:
    """
    ดึง credit สำหรับแสดงใต้ภาพ
    img_path: เช่น "images/thumbs/food/food_0003.jpg"
    คืน: "JohnDoe / Pexels · Pexels License"  หรือ ""
    """
    if not img_path or img_path.startswith("http"):
        return ""
    try:
        parts = Path(img_path).parts
        if len(parts) < 2:
            return ""
        cat      = parts[-2]
        filename = parts[-1]
        records  = _load_local_index(cat)
        for r in records:
            if r.get("file") == filename:
                creator = r.get("creator", "").strip()
                source  = r.get("source", "").strip()
                lic     = r.get("license", "CC").strip()
                parts_c = []
                if creator:
                    parts_c.append(creator)
                if source == "openverse":
                    parts_c.append("OpenVerse")
                elif source == "pexels":
                    parts_c.append("Pexels")
                elif source:
                    parts_c.append(source.capitalize())
                credit = " / ".join(parts_c) if parts_c else "Unknown"
                return f"{credit} · {lic}"
    except Exception:
        pass
    return ""


def wrap_image_with_credit(img_path: str, alt: str = "", caption: str = "") -> str:
    """
    สร้าง <figure> HTML พร้อม credit ใต้ภาพ
    ใช้แทน <img> ตรงๆ ใน agent_writer
    """
    credit = get_image_credit(img_path)
    seed   = hashlib.md5((img_path or alt).encode()).hexdigest()[:8]
    fallback = f"https://picsum.photos/seed/{seed}/800/350"
    credit_html = (
        f'<span style="float:right;font-size:0.72rem;color:#94a3b8;margin-left:.5rem;">'
        f'📷 {credit}</span>'
        if credit else ""
    )
    cap_text = caption or alt
    return (
        f'<figure style="margin:1.5rem 0;border-radius:12px;overflow:hidden;'
        f'box-shadow:0 2px 12px rgba(0,0,0,0.1);">'
        f'<img src="{img_path}" alt="{alt}" loading="lazy" '
        f'onerror="this.onerror=null;this.src=\'{fallback}\'" '
        f'style="width:100%;max-height:400px;object-fit:cover;">'
        f'<figcaption style="text-align:center;font-size:0.82rem;color:#64748b;padding:.4rem .8rem;">'
        f'{cap_text}{credit_html}</figcaption>'
        f'</figure>'
    )


def check_sources_status():
    """ตรวจสอบสถานะทุก source"""
    fooocus_ok = False
    gradio_ok  = False

    try:
        req = urllib.request.Request(f"{FOOOCUS_HOST}/", method="GET",
                                     headers={"User-Agent": "FoocousCheck/1.0"})
        with urllib.request.urlopen(req, timeout=3) as r:
            gradio_ok = r.status < 500
    except Exception:
        gradio_ok = False

    for path in ["/v1/generation/text-to-image", "/v1/engines/all", "/docs"]:
        try:
            req = urllib.request.Request(f"{FOOOCUS_HOST}{path}", method="GET",
                                         headers={"User-Agent": "FoocousCheck/1.0"})
            with urllib.request.urlopen(req, timeout=3) as r:
                if r.status in (200, 405, 422):
                    fooocus_ok = True; break
        except urllib.error.HTTPError as e:
            if e.code in (405, 422):
                fooocus_ok = True; break
        except Exception:
            continue

    print(f"\n📸 Image Sources Status Check (v13.0)")
    print("-" * 55)

    if fooocus_ok:
        print(f"✅ Fooocus AI    (REST API พร้อม 🚀 — generate รูปได้!)")
    elif gradio_ok:
        print(f"✅ Fooocus AI    (Gradio UI พร้อม 🚀 — generate รูปได้!)")
    else:
        print(f"❌ Fooocus AI    (ไม่ได้เปิด → ใช้ stock API แทน)")

    print(f"{'✅' if PEXELS_KEY   else '❌'} Pexels API    {'(พร้อมใช้)' if PEXELS_KEY   else '(ไม่มี Key)'}")
    print(f"{'✅' if PIXABAY_KEY  else '❌'} Pixabay API   {'(พร้อมใช้)' if PIXABAY_KEY  else '(ไม่มี Key)'}")
    print(f"{'✅' if UNSPLASH_KEY else '❌'} Unsplash API  {'(พร้อมใช้)' if UNSPLASH_KEY else '(ไม่มี Key)'}")
    print(f"⚡ Picsum Fallback  (พร้อมใช้งานเสมอ)")
    print("-" * 55)

    if not fooocus_ok and not gradio_ok:
        print(f"💡 เปิด Fooocus ก่อน: cd D:\\Fooocus_win64_2-5-0 แล้วรัน .\\run_api.bat")

    return gradio_ok


def _find_fooocus_fn_index():
    print(f"\n🔍 ค้นหา fn_index จาก {FOOOCUS_HOST}/info ...")
    try:
        req = urllib.request.Request(f"{FOOOCUS_HOST}/info",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            info = json.loads(r.read())

        named   = info.get("named_endpoints", {})
        unnamed = info.get("unnamed_endpoints", {})

        print(f"\n📋 Named endpoints ({len(named)} รายการ):")
        for name in list(named.keys())[:20]:
            print(f"  {name}")

        best_idx, best_count = -1, 0
        for idx_str, ep in unnamed.items():
            c = len(ep.get("parameters", []))
            if c > best_count:
                best_count = c; best_idx = int(idx_str)

        print(f"\n✅ fn_index แนะนำ: {best_idx} (มี {best_count} inputs)")
        print(f"   แก้ FOOOCUS_FN_INDEX = {best_idx} ใน image_sources.py")

    except Exception as e:
        print(f"❌ ไม่สามารถดึง info ได้: {e}")


if __name__ == "__main__":
    import sys
    if "--find-fn" in sys.argv:
        _find_fooocus_fn_index()
        sys.exit(0)
    check_sources_status()
    print("\n🧪 ทดสอบ Keyword Builder v13.0 [FIX B]:")
    tests = [
        ("ทำผมสวยที่บ้าน ไม่ต้องไปร้าน",       "ไลฟ์สไตล์", "lifestyle_hair"),
        ("เล็มปลายผมด้วยตัวเอง",                "ไลฟ์สไตล์", "lifestyle_trim"),
        ("อนิเมะน่าดูที่ไม่ควรพลาด",             "บันเทิง",   "anime_2025"),
        ("วิธีดูแลสุขภาพผิวหน้า",               "ความงาม",  "beauty_001"),
        ("แนะนำร้านอาหารอร่อยในกรุงเทพ",        "อาหาร",    "food_002"),
        ("เทคนิคลงทุนหุ้นสำหรับมือใหม่",         "การเงิน",  "finance_003"),
        ("กระเป๋าเดินทางแบบไหนดี",               "travel",   "travel_004"),
    ]
    for title, cat, ident in tests:
        kw = _extract_title_keywords(title, cat)
        print(f"\n  📌 '{title}'")
        print(f"     keyword : {kw}")
