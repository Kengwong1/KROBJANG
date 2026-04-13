"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  agent_video.py v3.1 — AI Image + Ken Burns + TTS + Multi-Format           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ติดตั้ง (ครั้งแรกครั้งเดียว):                                              ║
║    pip install gtts moviepy==1.0.3 pillow requests beautifulsoup4 numpy     ║
║    pip install python-dotenv                                                 ║
║    (แนะนำ) ติดตั้ง ffmpeg แล้วเพิ่มใน PATH → เสียงจะเร็วขึ้น 15%         ║
║                                                                              ║
║  ไฟล์ .env (วางไว้ในโฟลเดอร์เดียวกัน):                                     ║
║    PEXELS_KEY=your_key        → https://www.pexels.com/api/                 ║
║    UNSPLASH_KEY=your_key      → https://unsplash.com/developers             ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  คำสั่งทั้งหมด                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ── พื้นฐาน ──────────────────────────────────────────────────────────────  ║
║  python agent_video.py                       สร้างจากบทความล่าสุด 1 ไฟล์   ║
║  python agent_video.py --count 5             สร้าง 5 วิดีโอรวดเดียว        ║
║  python agent_video.py --file sport_123.html ระบุไฟล์ HTML เอง             ║
║  python agent_video.py --cat ghost           เฉพาะหมวด ghost               ║
║  python agent_video.py --cat sport --count 3 หมวด sport 3 วิดีโอ           ║
║                                                                              ║
║  ── รูปแบบวิดีโอ (เลือกได้ 3 แบบ) ────────────────────────────────────── ║
║  python agent_video.py --format vertical     9:16  1080×1920 (default)      ║
║                                              → TikTok / YouTube Shorts /    ║
║                                                 Instagram Reels             ║
║  python agent_video.py --format square       1:1   1080×1080                ║
║                                              → Instagram Feed / Facebook    ║
║  python agent_video.py --format landscape    16:9  1920×1080                ║
║                                              → YouTube / Facebook Video     ║
║                                                                              ║
║  ── ตัวเลือกเสริม ────────────────────────────────────────────────────── ║
║  python agent_video.py --no-ai-img           ข้ามการสร้างรูป AI            ║
║                                              (ใช้รูปจากบทความ + Pexels)    ║
║  python agent_video.py --dry-run             ทดสอบโดยไม่สร้างจริง          ║
║                                              (ดู prompt + ชื่อไฟล์)        ║
║                                                                              ║
║  ── ตัวอย่างคำสั่งผสม ─────────────────────────────────────────────────── ║
║  python agent_video.py --cat sport --format landscape --count 2             ║
║  python agent_video.py --file health_999.html --format square               ║
║  python agent_video.py --count 10 --no-ai-img                               ║
║  python agent_video.py --cat ghost --dry-run                                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ลำดับการหารูป (อัตโนมัติ ไม่ต้องตั้งค่า)                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  1. รูปจากบทความ HTML       เร็วสุด ตรงเนื้อหาสุด                          ║
║  2. Fooocus local API       ถ้าเปิดอยู่ port 7865 คุณภาพสูงสุด (GPU)       ║
║     เปิด Fooocus: python launch.py --listen --port 7865                     ║
║  3. Pollinations AI         ฟรี cloud ไม่ต้อง key (อาจช้า/429)             ║
║  4. Pexels                  ต้อง PEXELS_KEY ใน .env                         ║
║  5. Unsplash                ต้อง UNSPLASH_KEY ใน .env                       ║
║  6. Picsum random           fallback สุดท้าย ไม่ตรงเนื้อหา                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  หมวดที่รองรับ (ใช้กับ --cat)                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ghost  health  food  sport  technology  travel  beauty  finance             ║
║  lifestyle  education  gaming  car  pet  diy  law  anime  horoscope          ║
║  story  cartoon  news                                                        ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ฟีเจอร์ที่มีในไฟล์นี้                                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ✅ Smart Prompt Builder   แปลงหัวข้อไทย → prompt EN อัตโนมัติ             ║
║     (regex safe — ไม่เอา "ยา" ใน "กีฬา" แล้ว)                              ║
║  ✅ Ken Burns Effect       zoom_in / zoom_out / pan_right / pan_left / up   ║
║  ✅ TTS ภาษาไทย            Google TTS + ffmpeg เร่งความเร็ว 15%            ║
║  ✅ ตัดคำไทย               ไม่ตัดกลางคำ รองรับทั้งมีช่องว่างและไม่มี      ║
║  ✅ Subtitle box dynamic   วัด pixel จริง ไม่ล้นกรอบ auto-shrink font      ║
║  ✅ Font scale อัตโนมัติ   ปรับตาม format vertical/square/landscape        ║
║  ✅ Gradient overlay       สวยขึ้นอ่านง่ายขึ้นทุก clip                      ║
║  ✅ Intro + Outro card     badge หมวด + ชื่อเว็บ + CTA กด Like/Follow      ║
║  ✅ fadein/fadeout          ทุก clip มี transition 0.4s / 0.3s              ║
║  ✅ Skip ถ้ามีแล้ว         ไม่สร้างซ้ำถ้า .mp4 มีอยู่แล้ว                  ║
║  ✅ config.py / .env        ใช้ค่าจาก project config ถ้ามี                 ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  output: videos/ชื่อไฟล์.mp4   temp: videos/_tmp/ (ลบอัตโนมัติ)           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, re, json, datetime, hashlib, textwrap, time, math, urllib.parse
from pathlib import Path

# ── ตรวจสอบ dependencies ─────────────────────────────────────────────
def _check_deps():
    missing = []
    try: from gtts import gTTS
    except ImportError: missing.append("gtts")
    try: import moviepy.editor
    except ImportError: missing.append("moviepy==1.0.3")
    try: from PIL import Image, ImageDraw, ImageFont
    except ImportError: missing.append("pillow")
    try: from bs4 import BeautifulSoup
    except ImportError: missing.append("beautifulsoup4")
    if missing:
        print(f"❌ ติดตั้ง library ก่อน:\n   pip install {' '.join(missing)}")
        sys.exit(1)

_check_deps()

from gtts import gTTS
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, VideoClip
)
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from bs4 import BeautifulSoup
import requests
import numpy as np

# ── Config ────────────────────────────────────────────────────────────
try:
    from config import (
        BASE_PATH, SITE_URL, SITE_NAME, CATEGORIES, หมวด_ไทย,
        log, log_ok, log_warn, log_err, log_info, log_section,
    )
except ImportError:
    BASE_PATH = Path(__file__).parent.resolve()
    SITE_URL  = "https://example.vercel.app"
    SITE_NAME = "เว็บไซต์ของฉัน"
    CATEGORIES = []
    หมวด_ไทย  = {}
    def _ts(): return datetime.datetime.now().strftime("%H:%M:%S")
    def log(m):         print(f"[{_ts()}] {m}")
    def log_ok(m):      print(f"[{_ts()}] ✅ {m}")
    def log_warn(m):    print(f"[{_ts()}] ⚠️  {m}")
    def log_err(m):     print(f"[{_ts()}] ❌ {m}")
    def log_info(m):    print(f"[{_ts()}] ℹ️  {m}")
    def log_section(m): print(f"\n{'='*55}\n  {m}\n{'='*55}")

# ── โหลด .env ──────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_PATH / ".env")
except ImportError:
    pass  # ถ้าไม่มี python-dotenv ก็ข้าม

PEXELS_KEY   = os.environ.get("PEXELS_KEY", "")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")

DRY_RUN   = "--dry-run"   in sys.argv
NO_AI_IMG = "--no-ai-img" in sys.argv

# ── ขนาดวิดีโอ ────────────────────────────────────────────────────────
# รองรับ: vertical (TikTok/Shorts/Reels), square (Instagram), landscape (YouTube)
_FORMAT_PRESETS = {
    "vertical":  (1080, 1920),   # 9:16  TikTok / YouTube Shorts / Reels
    "square":    (1080, 1080),   # 1:1   Instagram / Facebook
    "landscape": (1920, 1080),   # 16:9  YouTube / Facebook
}

# อ่าน --format จาก args (default = vertical)
_FORMAT_ARG = "vertical"
for _i, _a in enumerate(sys.argv):
    if _a == "--format" and _i + 1 < len(sys.argv):
        _FORMAT_ARG = sys.argv[_i + 1].lower()

VID_W, VID_H = _FORMAT_PRESETS.get(_FORMAT_ARG, _FORMAT_PRESETS["vertical"])
FPS = 30

# ── โฟลเดอร์ ──────────────────────────────────────────────────────────
VIDEO_DIR = BASE_PATH / "videos"
TMP_DIR   = BASE_PATH / "videos" / "_tmp"
VIDEO_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)

# ── สีตาม category ────────────────────────────────────────────────────
CAT_COLORS = {
    "health":     ("#10b981", "#064e3b"),
    "food":       ("#ef4444", "#7f1d1d"),
    "finance":    ("#059669", "#064e3b"),
    "technology": ("#3b82f6", "#1e3a8a"),
    "lifestyle":  ("#8b5cf6", "#3b0764"),
    "beauty":     ("#ec4899", "#831843"),
    "news":       ("#4b5563", "#111827"),
    "gaming":     ("#7c3aed", "#2e1065"),
    "travel":     ("#0ea5e9", "#0c4a6e"),
    "education":  ("#0891b2", "#164e63"),
    "horoscope":  ("#8b5cf6", "#1e1b4b"),
    "ghost":      ("#9333ea", "#0a0a0a"),
    "story":      ("#f59e0b", "#451a03"),
    "cartoon":    ("#ec4899", "#500724"),
    "sport":      ("#f97316", "#431407"),
    "car":        ("#6366f1", "#1e1b4b"),
    "pet":        ("#84cc16", "#1a2e05"),
    "diy":        ("#f59e0b", "#451a03"),
    "law":        ("#6b7280", "#111827"),
    "anime":      ("#a855f7", "#2e1065"),
    "default":    ("#1e40af", "#0f172a"),
}


# ══════════════════════════════════════════════════════════════
# 🧠 Smart Prompt Builder
# แปลงหัวข้อ+เนื้อหาภาษาไทย → prompt ภาษาอังกฤษ
# ══════════════════════════════════════════════════════════════

# คำไทย → keyword อังกฤษ
_THAI_KEYWORDS = {
    # ── ผี / สยองขวัญ ──
    "ผี":           "ghost spirit",
    "วิญญาณ":      "spirit soul ethereal",
    "ตานี":         "banana tree ghost spirit woman",
    "กล้วย":       "banana tree plantation",
    "ต้นกล้วย":    "banana tree dark forest",
    "สิง":          "possessed haunted",
    "หลอน":        "haunted eerie supernatural",
    "น่ากลัว":     "scary frightening horror",
    "มืด":          "dark darkness shadow",
    "กลางคืน":     "night midnight moonlight",
    "ป่า":          "forest jungle dark trees",
    "นาง":          "woman female spirit",
    "แม่":          "mother woman",
    "ร้องไห้":     "crying weeping sorrowful",
    "เลือด":       "blood dark red",
    "ตาย":          "death dead skull",
    "ศพ":           "corpse body dead",
    "สุสาน":       "graveyard cemetery tombstone",
    "วัด":          "Thai temple ancient",
    "พระ":          "Buddhist monk temple",
    "ไสยศาสตร์":   "black magic occult mystical",
    "คาถา":        "spell incantation magic",
    "พราย":        "water spirit sprite",
    "กุมาร":       "child spirit ghost baby",
    "ปอบ":          "evil spirit demon Thai",
    "กระสือ":      "floating head ghost horror",
    "โขมด":        "will-o-wisp ghost light",
    "แม่นาค":      "Mae Nak Thai ghost woman",
    "ความมืด":     "darkness shadows horror",
    "หมอผี":       "shaman witch doctor occult",
    # ── สุขภาพ ──
    "สุขภาพ":      "healthcare medical wellness",
    "โรค":          "disease illness medical",
    "ยา":           "medicine medication pills",
    "หมอ":          "doctor physician medical",
    "โรงพยาบาล":   "hospital medical center",
    "ออกกำลัง":    "exercise workout fitness gym",
    # ── อาหาร ──
    "อาหาร":       "food dish cuisine",
    "ทำอาหาร":     "cooking kitchen chef",
    "อร่อย":       "delicious tasty food",
    "ร้านอาหาร":   "restaurant dining table",
    "ครัว":        "kitchen cooking",
    # ── กีฬา ──
    "ฟุตบอล":      "football soccer match",
    "นักกีฬา":     "athlete sports player",
    "แข่งขัน":     "competition match sports",
    "ทีม":          "team players sports",
    "ชนะ":          "victory winning champion",
    "สนามกีฬา":    "stadium sports arena crowd",
    # ── เทคโนโลยี ──
    "เทคโนโลยี":   "technology digital futuristic",
    "AI":           "artificial intelligence AI robot",
    "คอมพิวเตอร์": "computer technology digital",
    "มือถือ":      "smartphone mobile device",
    # ── ท่องเที่ยว ──
    "ท่องเที่ยว":  "travel tourism adventure",
    "ทะเล":        "sea ocean beach waves",
    "ภูเขา":       "mountain landscape nature",
    "วัฒนธรรม":    "culture traditional heritage",
    # ── รถ ──
    "รถ":           "car automobile vehicle",
    "รถยนต์":      "car vehicle automotive",
    "ขับ":          "driving road highway",
    # ── ความงาม ──
    "ความงาม":     "beauty skincare cosmetics",
    "เครื่องสำอาง": "cosmetics makeup beauty",
    "ผิว":          "skin skincare glow",
    "ผม":           "hair styling beauty",
    # ── การเงิน ──
    "เงิน":         "money finance wealth",
    "ลงทุน":       "investment finance stock",
    "หุ้น":         "stock market finance",
    # ── การศึกษา ──
    "เรียน":        "studying education learning",
    "โรงเรียน":    "school education classroom",
    "มหาวิทยาลัย": "university campus education",
}

# Style prompt ตามหมวด
_CAT_STYLE = {
    "ghost":      "Thai horror atmosphere, dark cinematic lighting, purple mist fog, dramatic shadows, eerie supernatural, photorealistic, 8k ultra detailed",
    "story":      "cinematic storytelling, warm dramatic lighting, emotional atmosphere, photorealistic, film grain",
    "health":     "clean medical professional, bright lighting, healthcare wellness, photorealistic, 8k",
    "food":       "food photography, appetizing, bright natural lighting, macro close-up, delicious vibrant colors",
    "sport":      "dynamic action photography, motion blur, stadium lighting, energetic crowd, photorealistic",
    "technology": "futuristic technology, blue neon lighting, digital hologram, sleek modern design, 8k",
    "travel":     "travel photography, golden hour sunset, beautiful landscape, vibrant vivid colors",
    "beauty":     "beauty portrait photography, soft studio lighting, glamour, professional editorial",
    "finance":    "professional business, modern glass office, clean minimalist, corporate",
    "lifestyle":  "lifestyle photography, warm natural light, authentic candid, modern living",
    "education":  "educational setting, bright classroom, learning environment, inspiring",
    "gaming":     "gaming setup RGB, neon cyberpunk lights, dramatic dark atmosphere",
    "car":        "automotive photography, dramatic studio lighting, sleek luxury design, showroom",
    "pet":        "cute animal portrait, soft natural bokeh light, adorable furry",
    "anime":      "anime illustration style, vibrant saturated colors, Japanese animation quality",
    "horoscope":  "mystical cosmic universe, stars galaxy nebula, purple golden ethereal glow",
    "default":    "cinematic photography, professional dramatic lighting, high quality, 8k photorealistic",
}

_NEGATIVE_PROMPT = (
    "ugly, blurry, low quality, watermark, text overlay, logo, "
    "deformed, bad anatomy, extra limbs, duplicate, out of frame"
)


def _build_image_prompt(heading: str, body: str, cat: str) -> str:
    """
    แปลงหัวข้อ+เนื้อหาไทย → prompt ภาษาอังกฤษ
    ใช้ regex word-boundary เพื่อป้องกัน partial match (เช่น "ยา" ใน "กีฬา")
    """
    full_text = heading + " " + body[:200]

    found = []
    for thai_word, eng_word in _THAI_KEYWORDS.items():
        # ตรวจสอบว่า keyword ปรากฏเป็นคำอิสระ ไม่ใช่ส่วนหนึ่งของคำอื่น
        # ใช้ lookbehind/lookahead เพราะภาษาไทยไม่มี whitespace ระหว่างคำ
        # แต่เราจะเช็ค "ไม่ตามด้วยตัวอักษรไทย" เพื่อหลีกเลี่ยง partial match
        pattern = thai_word + r'(?![ก-๙])'
        if re.search(pattern, full_text):
            found.append(eng_word)

    # ไม่เจอ keyword → ใช้ style ของหมวดแทน
    if not found:
        found = [cat]

    # รวม unique สูงสุด 5 คำ (ลดจาก 6 เพื่อให้ style มีน้ำหนักมากขึ้น)
    unique_kw = list(dict.fromkeys(found))[:5]
    style = _CAT_STYLE.get(cat, _CAT_STYLE["default"])
    return ", ".join(unique_kw) + ", " + style


# ══════════════════════════════════════════════════════════════
# 🎨 AI Image Generation
# ══════════════════════════════════════════════════════════════

def _check_fooocus_running() -> bool:
    """เช็คว่า Fooocus เปิดอยู่ที่ localhost:7865 ไหม"""
    try:
        r = requests.get("http://127.0.0.1:7865/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _generate_img_fooocus(prompt: str, save_path: Path) -> bool:
    """
    สร้างรูปด้วย Fooocus local API
    เปิด Fooocus ด้วย: python launch.py --listen --port 7865
    """
    try:
        url = "http://127.0.0.1:7865/v1/generation/text-to-image"
        payload = {
            "prompt": prompt,
            "negative_prompt": _NEGATIVE_PROMPT,
            "style_selections": ["Fooocus V2", "Fooocus Masterpiece"],
            "performance_selection": "Speed",
            "aspect_ratios_selection": "576*1024",
            "image_number": 1,
            "image_seed": -1,
            "sharpness": 2.0,
            "guidance_scale": 4.0,
            "save_meta": False,
        }
        r = requests.post(url, json=payload, timeout=120)
        if r.status_code != 200:
            return False
        data = r.json()
        if isinstance(data, list) and data:
            item = data[0]
            if "url" in item:
                img_url = item["url"]
                if img_url.startswith("http"):
                    return _download_img(img_url, save_path)
                src = Path(img_url.lstrip("/"))
                if src.exists():
                    import shutil
                    shutil.copy(src, save_path)
                    return True
            elif "base64" in item:
                import base64
                save_path.write_bytes(base64.b64decode(item["base64"]))
                return _resize_to_vertical(save_path)
        return False
    except Exception as e:
        log_warn(f"Fooocus error: {e}")
        return False


def _generate_img_pollinations(prompt: str, save_path: Path,
                                seed: str = "") -> bool:
    """
    สร้างรูปด้วย Pollinations AI
    ฟรี 100% ไม่ต้องสมัคร ไม่ต้อง API key ไม่หักเงิน
    เรียก URL → ได้รูปเลย
    """
    try:
        encoded = urllib.parse.quote(prompt)
        if not seed:
            seed = hashlib.md5(prompt.encode()).hexdigest()[:8]
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=576&height=1024"
            f"&seed={seed}"
            f"&nologo=true"
            f"&enhance=true"
            f"&model=flux"
        )
        log_info(f"  🎨 Pollinations AI กำลังสร้างรูป...")
        r = requests.get(url, timeout=60, stream=True)
        if r.status_code != 200:
            log_warn(f"  Pollinations ตอบกลับ: {r.status_code}")
            return False
        if "image" not in r.headers.get("content-type", ""):
            return False
        save_path.write_bytes(r.content)
        return _resize_to_vertical(save_path)
    except Exception as e:
        log_warn(f"  Pollinations error: {e}")
        return False


def _resize_to_vertical(img_path: Path, size=(VID_W, VID_H)) -> bool:
    """Resize/crop รูปให้เป็น vertical 1080x1920"""
    try:
        img = Image.open(img_path).convert("RGB")
        iw, ih = img.size
        target_ratio = size[0] / size[1]
        current_ratio = iw / ih
        if current_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            left = (iw - new_w) // 2
            img = img.crop((left, 0, left + new_w, ih))
        else:
            new_h = int(iw / target_ratio)
            top = (ih - new_h) // 2
            img = img.crop((0, top, iw, top + new_h))
        img = img.resize(size, Image.LANCZOS)
        img.save(img_path, quality=95)
        return True
    except Exception as e:
        log_warn(f"resize ล้มเหลว: {e}")
        return False


def _get_best_image(prompt: str, article_img_url: str,
                    save_path: Path, seed: str = "",
                    use_ai: bool = True) -> bool:
    """
    ลำดับการหารูป:
    1. รูปจากบทความ HTML
    2. Fooocus local (ถ้าเปิดอยู่)
    3. Pollinations AI (cloud ฟรี)
    4. Picsum random (fallback)
    """
    # 1. รูปจากบทความ
    if article_img_url:
        log_info(f"  📷 ใช้รูปจากบทความ...")
        if _download_img(article_img_url, save_path):
            return True

    if not use_ai or NO_AI_IMG:
        return _fallback_picsum(
            seed or hashlib.md5(prompt.encode()).hexdigest()[:8], save_path
        )

    # 2. Fooocus local
    if _check_fooocus_running():
        log_info(f"  🖥️  Fooocus local กำลังวาดรูป...")
        if _generate_img_fooocus(prompt, save_path):
            log_ok(f"  Fooocus สำเร็จ!")
            return True
        log_warn(f"  Fooocus ล้มเหลว → ลอง Pollinations...")

    # 3. Pollinations AI
    if _generate_img_pollinations(prompt, save_path, seed):
        log_ok(f"  Pollinations สำเร็จ!")
        return True
    log_warn(f"  Pollinations ล้มเหลว → Pexels...")

    # 4. Pexels
    if _generate_img_pexels(prompt, save_path):
        log_ok(f"  Pexels สำเร็จ!")
        return True
    log_warn(f"  Pexels ล้มเหลว → Unsplash...")

    # 5. Unsplash
    if _generate_img_unsplash(prompt, save_path):
        log_ok(f"  Unsplash สำเร็จ!")
        return True
    log_warn(f"  Unsplash ล้มเหลว → Picsum...")

    # 6. Picsum fallback (สุดท้าย)
    return _fallback_picsum(
        seed or hashlib.md5(prompt.encode()).hexdigest()[:8], save_path
    )


def _generate_img_pexels(prompt: str, save_path: Path) -> bool:
    """ค้นหารูปจาก Pexels ด้วย keyword จาก prompt"""
    if not PEXELS_KEY:
        return False
    try:
        # ใช้ 3 คำแรกของ prompt เป็น keyword
        keyword = " ".join(prompt.split(",")[:2]).strip()
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": keyword, "per_page": 5, "orientation": "portrait"},
            timeout=15,
        )
        if r.status_code != 200:
            log_warn(f"  Pexels ตอบกลับ: {r.status_code}")
            return False
        photos = r.json().get("photos", [])
        if not photos:
            return False
        # เลือกรูปแรกที่ได้
        img_url = photos[0]["src"]["large2x"]
        return _download_img(img_url, save_path)
    except Exception as e:
        log_warn(f"  Pexels error: {e}")
        return False


def _generate_img_unsplash(prompt: str, save_path: Path) -> bool:
    """ค้นหารูปจาก Unsplash ด้วย keyword จาก prompt"""
    if not UNSPLASH_KEY:
        return False
    try:
        keyword = " ".join(prompt.split(",")[:2]).strip()
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            params={"query": keyword, "per_page": 5, "orientation": "portrait"},
            timeout=15,
        )
        if r.status_code != 200:
            log_warn(f"  Unsplash ตอบกลับ: {r.status_code}")
            return False
        results = r.json().get("results", [])
        if not results:
            return False
        img_url = results[0]["urls"]["regular"]
        return _download_img(img_url, save_path)
    except Exception as e:
        log_warn(f"  Unsplash error: {e}")
        return False


def _fallback_picsum(seed: str, save_path: Path) -> bool:
    try:
        url = f"https://picsum.photos/seed/{seed}/1080/1920"
        r = requests.get(url, timeout=15, stream=True)
        if r.status_code == 200:
            save_path.write_bytes(r.content)
            return True
    except Exception:
        pass
    return False


def _download_img(url: str, save_path: Path, size=(VID_W, VID_H)) -> bool:
    try:
        if url.startswith("http"):
            r = requests.get(url, timeout=15, stream=True)
            if r.status_code != 200:
                return False
            save_path.write_bytes(r.content)
        else:
            src = BASE_PATH / url.lstrip("/")
            if not src.exists():
                return False
            import shutil
            shutil.copy(src, save_path)
        return _resize_to_vertical(save_path, size)
    except Exception as e:
        log_warn(f"ดาวน์โหลดรูปล้มเหลว: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# 🔤 ตัดคำภาษาไทยถูกต้อง
# ══════════════════════════════════════════════════════════════
def _wrap_thai(text: str, max_chars: int = 20) -> list:
    if not text:
        return []
    if ' ' in text:
        words = text.split()
        lines, current = [], ""
        for w in words:
            if len(current) + len(w) + 1 <= max_chars:
                current = (current + " " + w).strip()
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines
    good_breaks = set('ยรลงนมกดบปวะาีูเแโใไ็่้๊๋์')
    lines, i = [], 0
    while i < len(text):
        end = min(i + max_chars, len(text))
        if end >= len(text):
            lines.append(text[i:])
            break
        cut = end
        for j in range(end, max(i + max_chars - 5, i), -1):
            if text[j-1] in good_breaks:
                cut = j
                break
        lines.append(text[i:cut])
        i = cut
    return [l for l in lines if l]


def _thai_subtitle_lines(heading: str, body: str, max_chars: int = 22) -> list:
    heading = heading.strip()
    body_clean = re.sub(r'\s+', ' ', body.strip())
    # เพิ่ม max_chars สำหรับ landscape mode
    effective_chars = max_chars if VID_H > VID_W else int(max_chars * VID_W / 1080)
    h_lines = _wrap_thai(heading, effective_chars + 2)[:1]
    first_sentence = re.split(r'[।\.\!\?]', body_clean)[0].strip()
    if not first_sentence:
        first_sentence = body_clean
    b_lines = _wrap_thai(first_sentence[:80], effective_chars)[:3]
    return h_lines + b_lines


# ══════════════════════════════════════════════════════════════
# 🎥 Ken Burns Effect
# ══════════════════════════════════════════════════════════════
_KB_DIRECTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "pan_up"]

def _make_ken_burns_clip(img_path: Path, duration: float,
                          direction: str = "zoom_in") -> VideoClip:
    img = Image.open(str(img_path)).convert("RGB")
    img_np = np.array(img)
    H, W = img_np.shape[:2]
    ZOOM = 1.08

    def make_frame(t):
        p = t / duration
        if direction == "zoom_in":
            scale = 1.0 + (ZOOM - 1.0) * p
            cx, cy = W / 2, H / 2
        elif direction == "zoom_out":
            scale = ZOOM - (ZOOM - 1.0) * p
            cx, cy = W / 2, H / 2
        elif direction == "pan_right":
            scale = ZOOM
            cx = W / 2 - W * 0.04 + W * 0.08 * p
            cy = H / 2
        elif direction == "pan_left":
            scale = ZOOM
            cx = W / 2 + W * 0.04 - W * 0.08 * p
            cy = H / 2
        else:
            scale = ZOOM
            cx = W / 2
            cy = H / 2 + H * 0.04 - H * 0.08 * p

        crop_w = int(W / scale)
        crop_h = int(H / scale)
        x1 = max(0, int(cx - crop_w / 2))
        y1 = max(0, int(cy - crop_h / 2))
        x2 = min(W, x1 + crop_w)
        y2 = min(H, y1 + crop_h)
        if x2 > W: x1 = W - crop_w; x2 = W
        if y2 > H: y1 = H - crop_h; y2 = H
        x1, y1 = max(0, x1), max(0, y1)
        cropped = img_np[y1:y2, x1:x2]
        return np.array(
            Image.fromarray(cropped).resize((VID_W, VID_H), Image.BILINEAR)
        )

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ══════════════════════════════════════════════════════════════
# 🎨 Overlay PNG
# ══════════════════════════════════════════════════════════════
def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _load_fonts():
    font_paths = [
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "Fonts/sarabun.ttf",
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "Fonts/SarabunNew.ttf",
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "Fonts/NotoSansThai-Regular.ttf",
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "Fonts/THSarabunNew.ttf",
        Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "Fonts/tahoma.ttf",
        Path("/usr/share/fonts/truetype/thai/Sarabun-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf"),
    ]
    font_file = next((str(p) for p in font_paths if p.exists()), None)

    # ปรับขนาด font ตาม aspect ratio
    scale = min(VID_W, VID_H) / 1080
    sz_title   = max(40, int(80  * scale))
    sz_sub     = max(30, int(58  * scale))
    sz_badge   = max(28, int(46  * scale))
    sz_heading = max(34, int(64  * scale))

    try:
        if font_file:
            return (
                ImageFont.truetype(font_file, sz_title),
                ImageFont.truetype(font_file, sz_sub),
                ImageFont.truetype(font_file, sz_badge),
                ImageFont.truetype(font_file, sz_heading),
            )
    except Exception:
        pass
    d = ImageFont.load_default()
    return d, d, d, d


def _draw_text_shadow(draw, text, x, y, font,
                       color=(255, 255, 255), shadow=(0, 0, 0), offset=3):
    draw.text((x + offset, y + offset), text, font=font, fill=(*shadow, 200))
    draw.text((x, y), text, font=font, fill=color)


def _draw_badge(draw, text, cx, y, color, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = 200, 50
    px, py = 40, 18
    r, g, b = _hex_to_rgb(color)
    draw.rounded_rectangle(
        [cx-tw//2-px, y-th//2-py, cx+tw//2+px, y+th//2+py],
        radius=50, fill=(r, g, b, 240)
    )
    draw.text((cx - tw // 2, y - th // 2), text, font=font, fill="#ffffff")


def _make_overlay_image(bg_img_path: Path, lines: list, heading_line: str,
                         cat: str, is_intro=False, is_outro=False,
                         save_path: Path = None) -> Path:
    primary, dark = CAT_COLORS.get(cat, CAT_COLORS["default"])
    font_title, font_sub, font_badge, font_heading = _load_fonts()

    if bg_img_path and bg_img_path.exists():
        img = Image.open(bg_img_path).convert("RGBA")
    else:
        img = Image.new("RGBA", (VID_W, VID_H), dark)

    # gradient ล่าง
    overlay = Image.new("RGBA", (VID_W, VID_H), (0, 0, 0, 0))
    ov = ImageDraw.Draw(overlay)
    grad_start = int(VID_H * 0.38)
    for y in range(grad_start, VID_H):
        t = (y - grad_start) / (VID_H - grad_start)
        alpha = int(230 * (t ** 0.6))
        ov.line([(0, y), (VID_W, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    r_p, g_p, b_p = _hex_to_rgb(primary)

    if is_intro:
        cat_th = หมวด_ไทย.get(cat, cat.upper())
        _draw_badge(draw, f"▶ {cat_th}", VID_W // 2,
                    int(VID_H * 0.52), primary, font_badge)
        ty = int(VID_H * 0.57)
        for tl in _wrap_thai(heading_line, 16)[:4]:
            try:
                bbox = draw.textbbox((0, 0), tl, font=font_title)
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = len(tl) * 40
            _draw_text_shadow(draw, tl, (VID_W - tw) // 2, ty,
                               font_title, shadow=(0, 0, 0), offset=4)
            ty += 88
        try:
            bbox = draw.textbbox((0, 0), SITE_NAME, font=font_badge)
            sw = bbox[2] - bbox[0]
        except Exception:
            sw = 300
        draw.text(((VID_W - sw) // 2, int(VID_H * 0.90)), SITE_NAME,
                   font=font_badge, fill=(255, 255, 255, 180))

    elif is_outro:
        msgs   = ["อ่านบทความเต็มได้ที่",
                  SITE_URL.replace("https://", ""),
                  "👍 กด Like และ Follow ด้วยนะครับ"]
        fonts  = [font_sub, font_badge, font_sub]
        colors = [(255,255,255), _hex_to_rgb(primary), (255,255,255)]
        ty = int(VID_H * 0.48)
        for msg, fnt, col in zip(msgs, fonts, colors):
            try:
                bbox = draw.textbbox((0, 0), msg, font=fnt)
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = 300
            _draw_text_shadow(draw, msg, (VID_W - tw) // 2, ty, fnt, color=col)
            ty += 100

    else:
        if lines:
            # วัดความกว้างจริงของทุก line ก่อนวาด
            pad_x = max(60, int(VID_W * 0.06))   # padding ซ้าย-ขวา
            pad_y = 32
            line_gap = 8
            bar_w = 18                             # แถบสีซ้าย
            text_x = pad_x + bar_w + 12            # x เริ่มต้นของข้อความ
            max_text_w = VID_W - text_x - pad_x   # ความกว้างสูงสุดที่ข้อความใช้ได้

            # วัดความสูงแต่ละบรรทัด
            line_heights = []
            for i, line in enumerate(lines):
                fnt = font_heading if i == 0 else font_sub
                try:
                    bbox = draw.textbbox((0, 0), line, font=fnt)
                    lh = bbox[3] - bbox[1]
                except Exception:
                    lh = 60
                line_heights.append(max(lh, 44))

            total_text_h = sum(line_heights) + line_gap * (len(lines) - 1)
            box_h = total_text_h + pad_y * 2
            margin_bottom = max(80, int(VID_H * 0.05))
            box_y = VID_H - box_h - margin_bottom

            # วาด background box
            sub_ov = Image.new("RGBA", (VID_W, VID_H), (0, 0, 0, 0))
            sub_draw = ImageDraw.Draw(sub_ov)
            sub_draw.rounded_rectangle(
                [pad_x // 2, box_y, VID_W - pad_x // 2, VID_H - margin_bottom],
                radius=24, fill=(0, 0, 0, 200)
            )
            img = Image.alpha_composite(img, sub_ov)
            draw = ImageDraw.Draw(img)

            # แถบสีซ้าย
            draw.rounded_rectangle(
                [pad_x // 2, box_y, pad_x // 2 + bar_w, VID_H - margin_bottom],
                radius=8, fill=(r_p, g_p, b_p, 255)
            )

            # วาดข้อความ
            text_y = box_y + pad_y
            for i, line in enumerate(lines):
                fnt = font_heading if i == 0 else font_sub
                col = (255, 255, 255) if i == 0 else (220, 220, 220)
                # ตัด line ถ้ายาวเกิน (safety check)
                try:
                    bbox = draw.textbbox((0, 0), line, font=fnt)
                    lw = bbox[2] - bbox[0]
                    if lw > max_text_w:
                        # ย่อ font size ลงถ้าเกิน
                        scale_down = max_text_w / lw
                        try:
                            font_file_path = fnt.path
                            orig_size = fnt.size
                            fnt_small = ImageFont.truetype(
                                font_file_path, max(24, int(orig_size * scale_down))
                            )
                            fnt = fnt_small
                        except Exception:
                            pass
                except Exception:
                    pass
                _draw_text_shadow(draw, line, text_x, text_y, fnt,
                                   color=col, shadow=(0, 0, 0), offset=2)
                text_y += line_heights[i] + line_gap

    result_path = save_path or (TMP_DIR / "card_tmp.png")
    img.convert("RGB").save(result_path, quality=95)
    return result_path


# ══════════════════════════════════════════════════════════════
# 🔊 TTS + ปรับความเร็ว
# ══════════════════════════════════════════════════════════════
def _text_to_speech(text: str, save_path: Path, speed: float = 1.15) -> bool:
    try:
        clean = re.sub(r'<[^>]+>', ' ', text)
        clean = re.sub(r'http\S+', '', clean)
        clean = re.sub(r'[^\u0E00-\u0E7F\s\d.,!?]', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if not clean or len(clean) < 5:
            return False
        clean = clean[:500]
        tts = gTTS(text=clean, lang='th', slow=False)
        tts.save(str(save_path))
        if speed != 1.0:
            try:
                import subprocess, shutil
                tmp_out = str(save_path) + "_fast.mp3"
                result = subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(save_path),
                    "-filter:a", f"atempo={speed}",
                    tmp_out
                ], capture_output=True, timeout=30)
                if result.returncode == 0:
                    shutil.move(tmp_out, str(save_path))
                else:
                    log_warn(f"ปรับความเร็วเสียงล้มเหลว (ffmpeg): {result.stderr.decode(errors='ignore')[-200:]}")
            except Exception as e:
                log_warn(f"ปรับความเร็วเสียงล้มเหลว: {e}")
        return save_path.exists()
    except Exception as e:
        log_warn(f"TTS ล้มเหลว: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# 🎬 สร้าง clip = Ken Burns + Overlay + Audio
# ══════════════════════════════════════════════════════════════
def _make_section_clip(bg_path: Path, overlay_path: Path,
                        audio_path, duration: float,
                        kb_index: int = 0) -> VideoClip:
    from moviepy.editor import CompositeVideoClip
    direction = _KB_DIRECTIONS[kb_index % len(_KB_DIRECTIONS)]
    kb_clip = _make_ken_burns_clip(bg_path, duration, direction)
    overlay_clip = ImageClip(str(overlay_path)).set_duration(duration)
    composite = CompositeVideoClip([kb_clip, overlay_clip])
    if audio_path and Path(str(audio_path)).exists():
        try:
            audio = AudioFileClip(str(audio_path))
            composite = composite.set_audio(audio)
        except Exception as e:
            log_warn(f"ใส่เสียงล้มเหลว: {e}")
    return composite.fadein(0.4).fadeout(0.3)


# ══════════════════════════════════════════════════════════════
# 📄 อ่านบทความ HTML
# ══════════════════════════════════════════════════════════════
def _parse_article(html_path: Path) -> dict:
    try:
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    except Exception as e:
        log_err(f"อ่านไฟล์ล้มเหลว: {e}")
        return {}

    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content", "")
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else html_path.stem

    cat = html_path.stem.split("_")[0] if "_" in html_path.stem else html_path.stem
    cat_meta = soup.find("meta", {"name": "category"})
    if cat_meta:
        cat = cat_meta.get("content", cat)

    hero_img = ""
    og_img = soup.find("meta", property="og:image")
    if og_img:
        hero_img = og_img.get("content", "")
    if not hero_img:
        hw = soup.find(class_="hero-image-wrapper")
        if hw:
            img_tag = hw.find("img")
            if img_tag:
                hero_img = img_tag.get("src", "")

    sections = []
    body = soup.find(class_="article-body")
    if body:
        current_h, current_text, current_img = "", [], ""
        for el in body.children:
            if not hasattr(el, 'name') or el.name is None:
                continue
            if el.name in ("h2", "h3"):
                if current_h and current_text:
                    sections.append({
                        "heading": current_h,
                        "text": " ".join(current_text)[:400],
                        "image": current_img,
                    })
                current_h = el.get_text(strip=True)
                current_text, current_img = [], ""
            elif el.name == "p":
                t = el.get_text(strip=True)
                if t and len(t) > 10:
                    current_text.append(t)
            elif el.name == "figure":
                img_tag = el.find("img")
                if img_tag and not current_img:
                    current_img = img_tag.get("src", "")
            elif el.name in ("ul", "ol"):
                items = [li.get_text(strip=True) for li in el.find_all("li")]
                if items:
                    current_text.append(" ".join(items[:3]))
        if current_h and current_text:
            sections.append({
                "heading": current_h,
                "text": " ".join(current_text)[:400],
                "image": current_img,
            })

    if not sections:
        paras = [p.get_text(strip=True) for p in soup.find_all("p")
                 if len(p.get_text(strip=True)) > 30]
        if paras:
            sections = [{"heading": title, "text": p, "image": ""}
                        for p in paras[:5]]

    return {
        "title": title,
        "cat": cat,
        "hero_img": hero_img,
        "sections": sections[:8],
        "file": html_path,
    }


# ══════════════════════════════════════════════════════════════
# 🎬 สร้างวิดีโอ MAIN
# ══════════════════════════════════════════════════════════════
def สร้างวิดีโอ(html_path: Path):
    log_section(f"🎬 สร้างวิดีโอ: {html_path.name}")

    article = _parse_article(html_path)
    if not article or not article.get("sections"):
        log_err("ไม่พบเนื้อหาในไฟล์")
        return None

    title    = article["title"]
    cat      = article["cat"]
    sections = article["sections"]
    output_path = VIDEO_DIR / (html_path.stem + ".mp4")

    if output_path.exists():
        log_warn(f"วิดีโอมีอยู่แล้ว: {output_path.name} — ข้าม")
        return output_path

    if DRY_RUN:
        log_info(f"[DRY-RUN] จะสร้าง: {output_path.name}")
        log_info(f"  หัวข้อ: {title} | หมวด: {cat} | sections: {len(sections)}")
        for i, sec in enumerate(sections[:3]):
            p = _build_image_prompt(sec["heading"], sec["text"], cat)
            log_info(f"  Section {i+1} prompt: {p[:80]}...")
        return None

    fooocus_ok = _check_fooocus_running()
    if fooocus_ok:
        log_ok("Fooocus local พร้อม! (คุณภาพสูงสุด)")
    else:
        log_info("Fooocus ไม่ได้เปิด → ใช้ Pollinations AI (ฟรี cloud)")

    clips, tmp_files = [], []

    try:
        # ── INTRO ──────────────────────────────────────────
        log_info("สร้าง Intro card...")
        intro_bg = TMP_DIR / f"{html_path.stem}_intro_bg.jpg"
        intro_prompt = _build_image_prompt(title, "", cat)
        log_info(f"  Prompt: {intro_prompt[:70]}...")

        _get_best_image(
            prompt=intro_prompt,
            article_img_url=article["hero_img"],
            save_path=intro_bg,
            seed=hashlib.md5(title.encode()).hexdigest()[:8],
        )
        tmp_files.append(intro_bg)

        intro_overlay = TMP_DIR / f"{html_path.stem}_intro_ov.png"
        _make_overlay_image(intro_bg, [], title, cat,
                            is_intro=True, save_path=intro_overlay)
        tmp_files.append(intro_overlay)

        intro_audio = TMP_DIR / f"{html_path.stem}_intro.mp3"
        _text_to_speech(f"{title} มาฟังกันเลยครับ", intro_audio, speed=1.1)
        tmp_files.append(intro_audio)

        intro_dur = 4.0
        if intro_audio.exists():
            try:
                ac = AudioFileClip(str(intro_audio))
                intro_dur = max(4.0, ac.duration + 0.5)
                ac.close()
            except Exception:
                pass

        clips.append(_make_section_clip(
            intro_bg, intro_overlay, intro_audio, intro_dur, kb_index=0
        ))

        # ── CONTENT SLIDES ─────────────────────────────────
        for i, sec in enumerate(sections):
            log_info(f"Section {i+1}/{len(sections)}: {sec['heading'][:35]}")

            sec_prompt = _build_image_prompt(sec["heading"], sec["text"], cat)
            log_info(f"  Prompt: {sec_prompt[:70]}...")

            sec_bg = TMP_DIR / f"{html_path.stem}_sec{i}_bg.jpg"
            seed = hashlib.md5((title + sec["heading"]).encode()).hexdigest()[:8]

            _get_best_image(
                prompt=sec_prompt,
                article_img_url=sec["image"],
                save_path=sec_bg,
                seed=seed,
            )
            tmp_files.append(sec_bg)

            sub_lines = _thai_subtitle_lines(sec["heading"], sec["text"])
            sec_overlay = TMP_DIR / f"{html_path.stem}_sec{i}_ov.png"
            _make_overlay_image(sec_bg, sub_lines, sec["heading"], cat,
                                save_path=sec_overlay)
            tmp_files.append(sec_overlay)

            sec_audio = TMP_DIR / f"{html_path.stem}_sec{i}.mp3"
            tts_ok = _text_to_speech(
                sec["heading"] + " " + sec["text"],
                sec_audio, speed=1.15
            )
            tmp_files.append(sec_audio)

            sec_dur = 6.0
            if tts_ok and sec_audio.exists():
                try:
                    ac = AudioFileClip(str(sec_audio))
                    sec_dur = max(5.0, ac.duration + 0.8)
                    ac.close()
                except Exception:
                    pass

            clips.append(_make_section_clip(
                sec_bg, sec_overlay,
                sec_audio if tts_ok else None,
                sec_dur, kb_index=i + 1
            ))
            time.sleep(0.3)

        # ── OUTRO ──────────────────────────────────────────
        log_info("สร้าง Outro card...")
        outro_overlay = TMP_DIR / f"{html_path.stem}_outro_ov.png"
        _make_overlay_image(intro_bg, [], title, cat,
                            is_outro=True, save_path=outro_overlay)
        tmp_files.append(outro_overlay)

        outro_audio = TMP_DIR / f"{html_path.stem}_outro.mp3"
        _text_to_speech(
            f"อ่านบทความเต็มได้ที่ {SITE_NAME} ครับ กด Like และ Follow ด้วยนะครับ",
            outro_audio, speed=1.1
        )
        tmp_files.append(outro_audio)

        outro_dur = 4.0
        if outro_audio.exists():
            try:
                ac = AudioFileClip(str(outro_audio))
                outro_dur = max(4.0, ac.duration + 0.5)
                ac.close()
            except Exception:
                pass

        clips.append(_make_section_clip(
            intro_bg, outro_overlay, outro_audio, outro_dur, kb_index=0
        ))

        # ── รวม → MP4 ──────────────────────────────────────
        log_info(f"รวม {len(clips)} clips → MP4...")
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(TMP_DIR / "temp_audio.aac"),
            remove_temp=True,
            logger=None,
            preset="fast",
        )
        size_mb = output_path.stat().st_size // 1024 // 1024
        log_ok(f"วิดีโอเสร็จ: {output_path.name} ({size_mb} MB)")
        return output_path

    except Exception as e:
        log_err(f"สร้างวิดีโอล้มเหลว: {e}")
        import traceback; traceback.print_exc()
        return None

    finally:
        for f in tmp_files:
            try:
                if f and Path(f).exists():
                    Path(f).unlink()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════
# 📋 เลือกไฟล์
# ══════════════════════════════════════════════════════════════
def _get_article_files(cat_filter="", count=1, specific_file="") -> list:
    if specific_file:
        fp = BASE_PATH / specific_file
        return [fp] if fp.exists() else []
    pattern = "*_[0-9]*.html"
    all_files = sorted(BASE_PATH.glob(pattern),
                       key=lambda f: f.stat().st_mtime, reverse=True)
    if cat_filter:
        all_files = [f for f in all_files
                     if f.stem.startswith(cat_filter + "_")]
    no_video = [f for f in all_files
                if not (VIDEO_DIR / (f.stem + ".mp4")).exists()]
    return no_video[:count]


# ══════════════════════════════════════════════════════════════
# 🚀 Main
# ══════════════════════════════════════════════════════════════
def main():
    log_section("🎬 agent_video.py v3 — AI Image + Ken Burns + TTS")

    args = sys.argv[1:]
    specific_file = ""
    cat_filter    = ""
    count         = 1

    for i, a in enumerate(args):
        if a == "--file"  and i+1 < len(args): specific_file = args[i+1]
        elif a == "--cat" and i+1 < len(args): cat_filter    = args[i+1]
        elif a == "--count" and i+1 < len(args):
            try: count = int(args[i+1])
            except ValueError: pass

    # แสดง format ที่เลือก
    fmt_names = {
        "vertical":  "9:16 Vertical (TikTok / YouTube Shorts / Reels)",
        "square":    "1:1 Square (Instagram / Facebook)",
        "landscape": "16:9 Landscape (YouTube / Facebook Video)",
    }
    log_info(f"📐 Format: {fmt_names.get(_FORMAT_ARG, _FORMAT_ARG)} [{VID_W}×{VID_H}]")
    log_info(f"   เปลี่ยนได้ด้วย --format vertical | square | landscape")

    # แสดงสถานะ
    if NO_AI_IMG:
        log_warn("โหมด --no-ai-img: ข้ามการสร้างรูป AI")
    else:
        if _check_fooocus_running():
            log_ok("Fooocus local พร้อม! (คุณภาพสูงสุด 🖥️)")
        else:
            log_info("Pollinations AI พร้อม (ฟรี cloud ☁️)")
            log_info("เคล็ดลับ: เปิด Fooocus ด้วย --listen --port 7865")
            log_info("         เพื่อใช้ GPU เครื่องตัวเองสร้างรูปคุณภาพสูงกว่า")
        if PEXELS_KEY:
            log_ok(f"Pexels API พร้อม ✅")
        else:
            log_warn("ไม่พบ PEXELS_KEY ใน .env")
        if UNSPLASH_KEY:
            log_ok(f"Unsplash API พร้อม ✅")
        else:
            log_warn("ไม่พบ UNSPLASH_KEY ใน .env")

    files = _get_article_files(cat_filter, count, specific_file)
    if not files:
        log_warn("ไม่พบบทความที่ยังไม่มีวิดีโอ")
        log_info("รัน: python agent_writer.py --count 5 ก่อนนะครับ")
        return

    log_info(f"พบ {len(files)} บทความ")
    success = 0
    for i, fp in enumerate(files, 1):
        log(f"\n[{i}/{len(files)}] {fp.name}")
        if สร้างวิดีโอ(fp):
            success += 1

    log_section(f"🎉 เสร็จ! {success}/{len(files)} วิดีโอ")
    log_info(f"📁 {VIDEO_DIR}")
    log_info("📱 พร้อมโพสต์ TikTok / YouTube Shorts / Reels!")


if __name__ == "__main__":
    main()
