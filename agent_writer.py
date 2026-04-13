"""
╔══════════════════════════════════════════════════════════╗
║       ครบจังดอทคอม — agent_writer.py v5 (UNIFIED)      ║
║       สร้างบทความยาว+ลึก+มีคุณภาพ (Chunked Writing)    ║
║                                                          ║
║  python agent_writer.py                → สร้าง 1 บทความ ║
║  python agent_writer.py --count 5      → สร้าง 5 บทความ ║
║  python agent_writer.py --count 10 --cat food → หมวดเดียว║
║  python agent_writer.py --topic "X"    → ระบุหัวข้อเอง  ║
║  python agent_writer.py --cluster      → cluster 4 บทความ║
║  python agent_writer.py --cluster --count 10 → cluster 10║
║  python agent_writer.py --batch 20     → 20 บท ต่างหมวด ║
║  python agent_writer.py --batch 10 --cat health → 10 บท  ║
║  python agent_writer.py --dry-run      → ทดสอบไม่ push 
║
║  python agent_writer.py --cat folktale
║  python agent_writer.py --cat cartoon
║  python agent_writer.py --cat drama --count 3
║  python agent_writer.py --cat inspirational --topic "จากศูนย์สู่ดาว"  ║
╚══════════════════════════════════════════════════════════╝

หลักการ Chunked Writing:
  - วาง Outline ก่อน (AI ครั้งเดียว)
  - เขียนทีละ section (AI ทีละ call, num_predict สูง)
  - รวมทุก section เป็นบทความเดียว
  - ผลลัพธ์: บทความ 2,000-4,000 คำ คุณภาพสูง

สนับสนุนเรา (sidebar):
  - PromptPay QR + ปุ่มคัดลอกเบอร์
  - Facebook / YouTube / TikTok
  - AdSense (แสดงด้านล่างปุ่ม social)
"""
import os, sys, re, time, json, datetime, random, hashlib
import requests
import feedparser
from pathlib import Path
from bs4 import BeautifulSoup
from config import (
    BASE_PATH, SITE_URL, SITE_NAME, SITE_DESC,
    CATEGORIES, CATEGORY_PAGE_MAP, หมวด_ไทย,
    UNSPLASH_KEY, FB_PAGE_ID, FB_ACCESS_TOKEN,
    LINE_NOTIFY_TOKEN, ADSENSE_PUB, ADSENSE_SLOT, GA4_ID,
    LAZADA_AFFILIATE, SHOPEE_AFFILIATE, AGODA_AFFILIATE,
    DRY_RUN, log, log_ok, log_warn, log_err, log_info, log_ai, log_section,
    เรียก_ollama, เรียก_ollama_เร็ว, สร้าง_thumbnail_svg,
    ดึงรูป_unsplash, ดึงรูป_ตรงเนื้อหา,
    สร้าง_sidebar_html,   # ← ใช้ sidebar จาก config แทน hardcode
)

# โหลด .env เพิ่มเติม (Pexels, Unsplash fallback กรณี config ไม่มี)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_PATH / ".env")
except ImportError:
    pass
PEXELS_KEY   = os.environ.get("PEXELS_KEY", "")
# UNSPLASH_KEY อ่านจาก config แล้ว แต่ fallback จาก .env ด้วย
if not UNSPLASH_KEY:
    UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")

# ... ต่อจากส่วน import และ config ที่พี่เก่งส่งมา ...

# ══════════════════════════════════════════════════════════════
# 🖼️  Global image dedup — ป้องกันรูปซ้ำข้ามบทความใน session เดียวกัน
# ══════════════════════════════════════════════════════════════
_USED_IMG_URLS: set = set()   # เก็บ photo-ID ของ Unsplash/Pexels ที่ใช้แล้ว

def _extract_photo_id(url: str) -> str:
    """ดึง photo ID จาก Unsplash/Pexels URL"""
    m = re.search(r'photo-([a-f0-9-]{10,})', url)
    if m:
        return m.group(1)
    m = re.search(r'photos/(\d+)/', url)
    if m:
        return m.group(1)
    return url  # fallback: ใช้ URL เต็ม

def _is_img_used(url: str) -> bool:
    return _extract_photo_id(url) in _USED_IMG_URLS

def _mark_img_used(url: str):
    _USED_IMG_URLS.add(_extract_photo_id(url))


# ══════════════════════════════════════════════════════════════
# 🌐 ส่วนที่ 2: ระบบดึงเนื้อหาจาก URL และแปลงโฉม (Rewrite)
# ══════════════════════════════════════════════════════════════

def ดึงเนื้อหาและ_Rewrite(url: str):
    """
    ดึงข้อมูลจาก URL ที่กำหนด แล้วให้ AI สรุปเนื้อหาเพื่อเตรียมเขียนใหม่
    """
    try:
        log_info(f"🌐 กำลังเข้าถึง URL: {url}")
        
        # ดึงหน้าเว็บ
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, timeout=15, headers=headers)
        res.encoding = 'utf-8'
        
        if res.status_code != 200:
            log_err(f"ไม่สามารถดึงข้อมูลได้ (Status: {res.status_code})")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ลบส่วนที่ไม่ใช่นื้อหาออก (เมนู, โฆษณา, สคริปต์)
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'ads']):
            tag.decompose()
        
        # ดึงข้อความและทำความสะอาด
        เนื้อหาดิบ = soup.get_text(separator='\n', strip=True)
        # ตัดเอาเฉพาะช่วงต้นถึงกลาง (ป้องกัน Token เกินถ้าหน้าเว็บยาวมาก)
        เนื้อหาสำหรับ_AI = เนื้อหาดิบ[:5000] 

        log_ai("🤖 กำลังวิเคราะห์และสรุปเนื้อหาจากแหล่งข้อมูล...")
        
        prompt = f"""
        คุณคือบรรณาธิการข่าวอาวุโส 
        จงสรุปเนื้อหาสำคัญจากข้อมูลด้านล่างนี้ เพื่อนำไปใช้เป็นข้อมูลอ้างอิงในการเขียนบทความใหม่
        โดยให้สรุปเป็นประเด็นสำคัญ 5-8 ข้อ และคงใจความสำคัญไว้ทั้งหมด (ห้ามก๊อปปี้ประโยคเดิม)
        
        ข้อมูลจาก URL: {url}
        เนื้อหา:
        {เนื้อหาสำหรับ_AI}
        """
        
        สรุป = เรียก_ollama(prompt)
        return สรุป

    except Exception as e:
        log_err(f"เกิดข้อผิดพลาดในระบบดึงข้อมูล: {e}")
        return None

# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# 🖼️ รูปภาพ — ค้นหาหลายวิธี (5 fallback)
# ══════════════════════════════════════════════════════════════
def ดึงรูป_robust(หัวข้อ: str, หมวด: str, filename: str = "", บริบท: str = "") -> str:
    """
    FIX: ดึงรูปตรงเนื้อหา โดยให้ AI คิด keyword เฉพาะเจาะจงก่อน
    แล้วส่งให้ ดึงรูป_ตรงเนื้อหา ใน config จัดการ
    """
    # ให้ AI แปลง keyword เป็นภาษาอังกฤษที่ตรงเนื้อหาก่อน (ไม่ใช้ชื่อบุคคล)
    try:
        keyword_prompt = (
            f'จากหัวข้อ: "{หัวข้อ}"\n'
            f'คิด keyword ภาษาอังกฤษ 2-3 คำ สำหรับค้นรูปภาพ\n'
            f'ห้ามใช้ชื่อบุคคล ให้ใช้คำกว้างๆ เช่น "trade war economy", "military diplomacy", "stock market"\n'
            f'ตอบแค่ keyword ไม่ต้องอธิบาย'
        )
        keyword_en = เรียก_ollama_เร็ว(keyword_prompt).strip().split('\n')[0][:80]
        log_info(f"🔍 keyword รูป: {keyword_en}")
        img = ดึงรูป_ตรงเนื้อหา(keyword_en, หมวด, keyword_en)
    except Exception:
        img = ดึงรูป_ตรงเนื้อหา(หัวข้อ, หมวด, บริบท)

    if img and img.startswith("http"):
        return img

    # Fallback: Pexels (keyword ตรงเนื้อหา)
    if PEXELS_KEY:
        try:
            kw = keyword_en if "keyword_en" in dir() else หัวข้อ[:40]
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": kw, "per_page": 3, "orientation": "landscape"},
                timeout=12,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    pex_url = photos[0]["src"]["large2x"]
                    log_ok(f"Pexels รูป: {pex_url[:60]}...")
                    return pex_url
        except Exception as e:
            log_warn(f"Pexels ล้มเหลว: {e}")

    # Fallback: SVG local
    if filename:
        svg_path = สร้าง_thumbnail_svg(หัวข้อ, หมวด, filename)
        if svg_path:
            log_ok(f"สร้าง SVG thumbnail local: {svg_path}")
            return svg_path

    seed = hashlib.md5((หัวข้อ + หมวด).encode()).hexdigest()[:12]
    return f"https://picsum.photos/seed/{seed}/800/450"


def _ดึงรูป_ไม่ซ้ำ(หัวข้อ: str, หมวด: str, filename: str = "", บริบท: str = "") -> str:
    """
    wrapper ของ ดึงรูป_robust — ถ้าได้รูปที่ใช้แล้วให้ลองใหม่อีก 2 รอบ
    """
    for attempt in range(3):
        suffix = ("" if attempt == 0 else f" มุมมองที่ {attempt+1}")
        url = ดึงรูป_robust(หัวข้อ + suffix, หมวด, filename, บริบท)
        if not _is_img_used(url):
            _mark_img_used(url)
            return url
        log_warn(f"  รูปซ้ำ (attempt {attempt+1}): {url[30:70]}...")
    # ถ้าซ้ำทุกรอบ ใช้ picsum seed ต่างออกไป
    seed = hashlib.md5((หัวข้อ + หมวด + str(len(_USED_IMG_URLS))).encode()).hexdigest()[:12]
    fallback = f"https://picsum.photos/seed/{seed}/800/450"
    _mark_img_used(fallback)
    return fallback


def สร้างรูป_inline(หัวข้อ_section: str, หมวด: str, หัวข้อ_บทความ: str = "", filename: str = "") -> str:
    """FIX: รูปแทรกในเนื้อหา — ส่ง context ทั้งหัวข้อ section และบทความให้ keyword แม่น"""
    บริบท = f"บทความ: {หัวข้อ_บทความ}, ส่วน: {หัวข้อ_section}" if หัวข้อ_บทความ else หัวข้อ_section
    url = ดึงรูป_robust(หัวข้อ_section, หมวด, filename=filename, บริบท=บริบท)  # แก้บั๊ก 3: ส่ง filename ด้วย
    seed = hashlib.md5(หัวข้อ_section.encode()).hexdigest()[:8]
    fallback = f"https://picsum.photos/seed/{seed}/800/350"
    return (
        f'<figure style="margin:1.5rem 0;border-radius:12px;overflow:hidden;'
        f'box-shadow:0 2px 12px rgba(0,0,0,0.1);">'
        f'<img src="{url}" alt="{หัวข้อ_section}" loading="lazy" '
        f'onerror="this.onerror=null;this.src=\'{fallback}\'" '
        f'style="width:100%;max-height:350px;object-fit:cover;">'
        f'<figcaption style="text-align:center;font-size:0.85rem;color:#64748b;'
        f'padding:0.5rem;">{หัวข้อ_section}</figcaption></figure>'
    )


# ══════════════════════════════════════════════════════════════
# 📚 Scrape ข้อมูลอ้างอิง — หลายแหล่ง
# ══════════════════════════════════════════════════════════════
def scrape_อ้างอิง(หัวข้อ: str) -> str:
    import urllib.parse
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    }
    เนื้อหา = []
    _BAD_WORDS = ["คุกกี้","Cookie","ลงทะเบียน","subscribe","copyright","advertisement",
                  "ดาวน์โหลดแอป","Privacy Policy","Terms of","นโยบายความ"]

    def _ดึงหน้าเว็บ(url: str, max_chars: int = 6000) -> list:
        """ดึง paragraph จากหน้าเว็บจริง กรองขยะออก"""
        try:
            r2 = requests.get(url, headers=headers, timeout=12)
            r2.encoding = "utf-8"
            if r2.status_code != 200:
                return []
            s2 = BeautifulSoup(r2.text, "html.parser")
            # ลบ nav/footer/script/style/ads
            for tag in s2(["script","style","nav","footer","header","aside","iframe",
                            "noscript","form","button"]):
                tag.decompose()
            ps = []
            total = 0
            for p in s2.find_all(["p","li","h2","h3"]):
                t = p.get_text(" ", strip=True)
                if len(t) < 60:
                    continue
                if any(w in t for w in _BAD_WORDS):
                    continue
                ps.append(t)
                total += len(t)
                if total >= max_chars:
                    break
            return ps
        except Exception:
            return []

    log_info("ค้นหาข้อมูลอ้างอิง...")

    # ── แหล่งที่ 1: DuckDuckGo — ดึง snippet + เข้าหน้าจริง ──
    all_links = []
    try:
        ddg = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(หัวข้อ + ' ภาษาไทย')}"
        r = requests.get(ddg, headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")

        # snippet (ใช้ backup ถ้าหน้าจริงดึงไม่ได้)
        snippets = [s.get_text().strip() for s in soup.select(".result__snippet")
                    if len(s.get_text().strip()) > 50]
        เนื้อหา.extend(snippets[:5])

        # รวบรวม link ทั้งหมด — ไม่จำกัดแค่ข่าว
        _PREFER = ["sanook","kapook","thairath","khaosod","mthai","manager",
                   "wongnai","cookpad.th","allrecipes.in.th","healthline",
                   "rama.mahidol","pobpad","dmh.go.th","bangkokpost","nationthailand",
                   "posttoday","prachachat","thaipbs"]
        for a in soup.select(".result__title a, .result__a"):
            href = a.get("href", "")
            if "uddg=" in href:
                try:
                    href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                except Exception:
                    pass
            if href.startswith("http"):
                # ให้ priority แก่เว็บที่รู้จัก
                priority = 0 if any(d in href for d in _PREFER) else 1
                all_links.append((priority, href))

        # เรียง priority ก่อน แล้วดึงหน้าจริง
        all_links.sort(key=lambda x: x[0])
        visited = 0
        for _, url in all_links[:6]:
            ps = _ดึงหน้าเว็บ(url)
            if ps:
                เนื้อหา.extend(ps)
                log_ok(f"อ่านหน้าจริง: {url[8:55]}... ({len(ps)} ย่อหน้า)")
                visited += 1
            if visited >= 4:
                break
    except Exception as e:
        log_warn(f"DuckDuckGo ล้มเหลว: {e}")

    # ── แหล่งที่ 2: เว็บเฉพาะทางตามหมวด (ถ้ายังน้อย) ──────────
    if len(เนื้อหา) < 10:
        log_info("Fallback: ค้นเว็บเฉพาะทาง...")
        q = urllib.parse.quote(หัวข้อ)
        fallback_sources = [
            f"https://www.wongnai.com/search?q={q}",
            f"https://www.sanook.com/search/?q={q}",
            f"https://www.kapook.com/search.php?q={q}",
            f"https://www.thairath.co.th/search/{q}",
            f"https://www.khaosod.co.th/?s={q}",
            f"https://www.pobpad.com/?s={q}",
        ]
        for url in fallback_sources:
            ps = _ดึงหน้าเว็บ(url, max_chars=4000)
            เนื้อหา.extend(ps[:8])
            if len(เนื้อหา) >= 25:
                break

    # ── กรองซ้ำ + เรียงตาม length ─────────────────────────────
    seen, กรอง = set(), []
    for t in เนื้อหา:
        k = t[:60]
        if k not in seen and len(t) > 60:
            seen.add(k)
            กรอง.append(t)
    กรอง.sort(key=len, reverse=True)

    log_info(f"ข้อมูลอ้างอิง: {len(กรอง)} ย่อหน้า ({sum(len(x) for x in กรอง):,} ตัวอักษร)")
    return "\n\n".join(กรอง[:35])


# ══════════════════════════════════════════════════════════════
# ✍️ Markdown → HTML converter
# ══════════════════════════════════════════════════════════════
def _กรอง_instruction(ข้อความ: str) -> str:
    """ลบบรรทัดที่เป็น instruction หลุดออกมาจาก AI ไม่ให้ติดในบทความ"""
    PATTERNS = [
        r'^[⚠️✨🔴🔥💡📌]+\s*(สำคัญ|กฎ|ห้าม|ต้อง|หมายเหตุ)',
        r'^\d+\.\s*(เริ่มด้วย|ห้าม|เขียน Markdown|ความยาว|ตอบเฉพาะ)',
        r'^(กฎ|กฎสำคัญ|สำคัญมาก|หมายเหตุ)\s*:',
        r'^ความยาว\s+\d+',
        r'^เขียน Markdown',
        r'^ห้าม HTML',
        r'^ตอบเป็น Markdown',
        r'^สลับระหว่างย่อหน้า',
        r'^รายการ bullet',
        # ── เพิ่ม: pattern ที่พบบ่อยจริงจากโมเดลไทย ──────────────
        r'^สไตล์บังคับ',
        r'^สไตล์สำหรับ',
        r'^สไตล์:',
        r'^ตัวอย่าง.*section',
        r'^ประเด็นหลัก\s*:',
        r'^หมวด\s*:',
        r'^ขอเนื้อหาส่วน',
        r'^ขึ้นต้นด้วย ##',
        r'^\*\s*(เขียน|ย่อหน้า|ห้าม|ใส่|สลับ|ตอบ)',
        r'^-\s*(เขียน|ย่อหน้า|ห้าม|ใส่|สลับ|ตอบ)',
        r'^กฎ\s*$',
        r'^กฎ:',
        r'^(\d+\.\s*)?(เริ่ม|ห้าม|ต้อง|ใช้|ตอบ|เขียน|สลับ|ใส่|ครอบคลุม|ระบุ|รวม|ทำ|แต่ละ).*[Mm]arkdown',
        r'^\*\*สไตล์',
        r'^\*\*กฎ',
        r'^\*\*ห้าม',
        r'^\*\*ต้อง',
        r'^(step|STEP)\s*\d+',
    ]
    สะอาด = []
    for line in ข้อความ.split('\n'):
        if any(re.match(p, line.strip()) for p in PATTERNS):
            continue
        สะอาด.append(line)
    return '\n'.join(สะอาด)



# ══════════════════════════════════════════════════════════════
# 🔗 Auto External Links — ลิงก์คำสำคัญไปแหล่งทางการ
# ══════════════════════════════════════════════════════════════

# คำสำคัญ → URL ทางการ (เพิ่มได้เรื่อยๆ)
_EXTERNAL_LINKS = {
    # ── Social Media ──────────────────────────────────────────
    "Facebook":     "https://www.facebook.com",
    "Instagram":    "https://www.instagram.com",
    "YouTube":      "https://www.youtube.com",
    "TikTok":       "https://www.tiktok.com",
    "Twitter":      "https://twitter.com",
    "X (Twitter)":  "https://twitter.com",
    "LINE":         "https://line.me",
    "WhatsApp":     "https://www.whatsapp.com",
    "Telegram":     "https://telegram.org",
    "Pinterest":    "https://www.pinterest.com",
    "LinkedIn":     "https://www.linkedin.com",
    "Threads":      "https://www.threads.net",
    # ── Tech / Platform ───────────────────────────────────────
    "Google":       "https://www.google.com",
    "Google Maps":  "https://maps.google.com",
    "Google Play":  "https://play.google.com",
    "App Store":    "https://www.apple.com/app-store",
    "ChatGPT":      "https://chat.openai.com",
    "OpenAI":       "https://openai.com",
    "Gemini":       "https://gemini.google.com",
    "Claude":       "https://claude.ai",
    "Microsoft":    "https://www.microsoft.com",
    "Apple":        "https://www.apple.com",
    "Amazon":       "https://www.amazon.com",
    "Netflix":      "https://www.netflix.com",
    "Spotify":      "https://www.spotify.com",
    "Wikipedia":    "https://th.wikipedia.org",
    "GitHub":       "https://github.com",
    "Vercel":       "https://vercel.com",
    # ── E-commerce ────────────────────────────────────────────
    "Shopee":       "https://shopee.co.th",
    "Lazada":       "https://www.lazada.co.th",
    "JD Central":   "https://www.jd.co.th",
    "Grab":         "https://www.grab.com/th",
    "Agoda":        "https://www.agoda.com",
    "Booking.com":  "https://www.booking.com",
    "Airbnb":       "https://www.airbnb.com",
    # ── สื่อไทย ───────────────────────────────────────────────
    "ไทยรัฐ":       "https://www.thairath.co.th",
    "เดลินิวส์":    "https://www.dailynews.co.th",
    "มติชน":        "https://www.matichon.co.th",
    "Sanook":       "https://www.sanook.com",
    "Kapook":       "https://www.kapook.com",
    # ── สุขภาพ ────────────────────────────────────────────────
    "WHO":          "https://www.who.int",
    "กรมอนามัย":    "https://www.anamai.moph.go.th",
    "สาธารณสุข":    "https://www.moph.go.th",
    # ── การเงิน ───────────────────────────────────────────────
    "ตลาดหลักทรัพย์": "https://www.set.or.th",
    "กรมสรรพากร":   "https://www.rd.go.th",
    "ธนาคารแห่งประเทศไทย": "https://www.bot.or.th",
    "SCB":          "https://www.scb.co.th",
    "กสิกรไทย":     "https://www.kasikornbank.com",
    "กรุงไทย":      "https://krungthai.com",
    "Bangkok Bank": "https://www.bangkokbank.com",
    # ── รัฐบาล/หน่วยงาน ──────────────────────────────────────
    "ราชกิจจานุเบกษา": "https://ratchakitchanubeksa.soc.go.th",
    "กรมที่ดิน":    "https://www.dol.go.th",
}

def _ใส่_external_links(html: str) -> str:
    """
    ใส่ลิงก์ external ให้คำสำคัญในบทความ
    - แต่ละคำลิงก์ได้แค่ครั้งแรกที่เจอ (ไม่ซ้ำ)
    - ข้าม tag HTML (ไม่ลิงก์ใน src/href/attribute)
    - เปิด target="_blank" ผู้อ่านไม่หายจากเว็บ
    """
    import re as _re

    used = set()  # คำที่ลิงก์แล้ว

    # เรียงจากยาวไปสั้น เพื่อจับ "Google Maps" ก่อน "Google"
    sorted_links = sorted(_EXTERNAL_LINKS.items(), key=lambda x: len(x[0]), reverse=True)

    for word, url in sorted_links:
        if word in used:
            continue

        # สร้าง regex จับคำ (case-sensitive สำหรับภาษาไทย/แบรนด์)
        escaped = _re.escape(word)
        # จับคำตรงๆ — การกรอง HTML tag ทำใน _replace แทน lookbehind
        pattern = _re.compile(
            r'(' + escaped + r')',
            _re.UNICODE
        )

        def _replace(m, _url=url, _word=word):
            # ตรวจว่าอยู่ใน HTML tag หรือเปล่า (นับ < > รอบๆ)
            start = m.start()
            before = html[:start]
            # ถ้ามี < ที่ยังไม่ปิดด้วย > = อยู่ใน tag
            last_lt = before.rfind('<')
            last_gt = before.rfind('>')
            if last_lt > last_gt:
                return m.group(0)  # อยู่ใน tag ข้าม
            # ตรวจว่าอยู่ใน attribute (ตามหลัง " หรือ ')
            if before and before[-1] in ('"', "'"):
                return m.group(0)
            used.add(_word)
            style = "color:var(--primary,#1e40af);text-decoration:underline;text-underline-offset:2px;"
            return (f'<a href="{_url}" target="_blank" rel="noopener noreferrer" '
                    f'style="{style}">{m.group(0)}</a>')

        # ลิงก์แค่ครั้งแรก (count=1)
        new_html, n = pattern.subn(_replace, html, count=1)
        if n > 0:
            html = new_html
            used.add(word)

    return html


def แปลง_md_html(ข้อความ: str) -> str:
    """แปลง Markdown/raw text → HTML สะอาด"""
    # ลบ <think> tags จาก deepseek-r1
    ข้อความ = re.sub(r'<think>.*?</think>', '', ข้อความ, flags=re.DOTALL).strip()
    # ลบ ``` code blocks
    ข้อความ = re.sub(r'```.*?```', '', ข้อความ, flags=re.DOTALL)
    # ลบ #### Q3: / A: ที่ AI เขียนใน FAQ แบบดิบ (ไม่ถูก render)
    ข้อความ = re.sub(r'^#{2,5}\s*Q\d+[:\s]', 'Q: ', ข้อความ, flags=re.MULTILINE)
    ข้อความ = re.sub(r'^#{2,5}\s*A\s*:', 'A:', ข้อความ, flags=re.MULTILINE)
    # ลบ instruction หลุด
    ข้อความ = _กรอง_instruction(ข้อความ)

    บรรทัด = ข้อความ.split("\n")
    ผล, in_list, in_ol = [], False, False
    ol_counter = 0  # นับเลขลำดับเองป้องกัน AI ส่ง "1. 1. 1."

    for line in บรรทัด:
        stripped = line.strip()

        # ── ข้าม heading ที่ขึ้นต้นด้วย "ย่อหน้า N" "ตอน N" ──
        _h_text = re.sub(r'^#{1,6}\s*', '', stripped)
        if re.match(r'^(ย่อหน้า|ตอน|ฉาก)(ที่)?\s*\d+', _h_text) and re.match(r'^#{1,6}\s+', stripped):
            continue

        if re.match(r'^#{4,6}\s+', stripped):
            # h4-h6 → แปลงเป็น <p><strong> แทน เพราะ AI มักใช้ #### สำหรับ Q&A
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            h = re.sub(r'^#{4,6}\s+', '', stripped)
            h = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
            ผล.append(f'<p><strong style="color:var(--dark,#1e293b);">{h}</strong></p>')

        elif re.match(r'^#{3}\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            h = re.sub(r'^#{3}\s+', '', stripped)
            h = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
            ผล.append(f'<h3 style="color:var(--dark,#1e293b);margin-top:1.5rem;margin-bottom:0.5rem;font-size:1.1rem;">{h}</h3>')

        elif re.match(r'^#{1,2}\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            h = re.sub(r'^#{1,2}\s+', '', stripped)
            h = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
            ผล.append(f'<h2 style="color:var(--primary,#1e40af);margin-top:2rem;margin-bottom:0.75rem;font-size:1.3rem;border-left:4px solid var(--primary,#1e40af);padding-left:0.75rem;">{h}</h2>')

        elif re.match(r'^\d+\.\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if not in_ol:
                ผล.append('<ol style="padding-left:1.5rem;margin:1rem 0;">')
                in_ol = True
                ol_counter = 0
            ol_counter += 1
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            # ใช้ value= บังคับให้ browser แสดงเลขถูก แม้ AI ส่ง 1. ทุกบรรทัด
            ผล.append(f'<li value="{ol_counter}" style="margin-bottom:0.5rem;line-height:1.7;">{item}</li>')

        elif re.match(r'^[-*•]\s+', stripped):
            if in_ol: ผล.append("</ol>"); in_ol = False; ol_counter = 0
            if not in_list: ผล.append('<ul style="padding-left:1.5rem;margin:1rem 0;">'); in_list = True
            item = re.sub(r'^[-*•]\s+', '', stripped)
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            ผล.append(f'<li style="margin-bottom:0.5rem;line-height:1.7;">{item}</li>')

        elif stripped == "":
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0

        else:
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            if stripped:
                s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
                if s.startswith('<h') or s.startswith('<ul') or s.startswith('<ol') or s.startswith('<li'):
                    ผล.append(s)
                else:
                    ผล.append(f"<p>{s}</p>")

    if in_list: ผล.append("</ul>")
    if in_ol:   ผล.append("</ol>")
    return "\n".join(ผล)


def ทำความสะอาด_html(html: str) -> str:
    """ลบ tag ซ้ำซ้อน, ลบ h1 ที่ AI สร้างขึ้นมา, กรอง instruction หลุด"""
    html = re.sub(r'<h1[^>]*>.*?</h1>', '', html, flags=re.DOTALL)
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[23][^>]*>)', r'\1', html)
    html = re.sub(r'(</h[23]>)</p>', r'\1', html)
    # ลบ instruction หลุดในรูปแบบ HTML
    html = re.sub(
        r'<p>[⚠️✨🔴🔥💡📌]*\s*(สำคัญมาก|กฎสำคัญ|หมายเหตุ)[^<]{0,400}</p>', '', html)
    html = re.sub(
        r'<p>\d+\.\s*(เริ่มด้วย|ห้าม|เขียน Markdown|ความยาว)[^<]{0,400}</p>', '', html)
    html = re.sub(
        r'<p>(เขียน Markdown|ห้าม HTML|สลับระหว่างย่อหน้า|รายการ bullet)[^<]{0,400}</p>', '', html)
    # ── เพิ่ม: กรอง instruction หลุดแบบอื่นๆ ─────────────────
    html = re.sub(
        r'<p>\s*(สไตล์บังคับ|สไตล์สำหรับ|สไตล์:|ประเด็นหลัก|กฎ:|กฎ\s*$|step\s*\d|ขอเนื้อหาส่วน|ขึ้นต้นด้วย)[^<]{0,500}</p>',
        '', html, flags=re.IGNORECASE)
    html = re.sub(
        r'<p>[\*\-]\s*(เขียน|ย่อหน้า|ห้าม|ใส่|สลับ|ตอบ|ต้อง)[^<]{0,400}</p>', '', html)
    html = re.sub(r'<li[^>]*>\s*ห้าม[^<]{0,200}</li>', '', html)
    html = re.sub(r'<li[^>]*>\s*\d+\.\s*(เขียน|ห้าม|ต้อง)[^<]{0,200}</li>', '', html)
    # ── ลบ h2/h3 ที่ขึ้นต้นด้วย "ย่อหน้า N" "ตอน N" "ฉาก N" ไม่ว่าจะมีชื่อตามหรือไม่ ──
    html = re.sub(r'<h[23][^>]*>\s*ย่อหน้า(ที่)?\s*\d+[^<]*</h[23]>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<h[23][^>]*>\s*ตอน(ที่)?\s*\d+[^<]*</h[23]>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<h[23][^>]*>\s*ฉาก(ที่)?\s*\d+[^<]*</h[23]>', '', html, flags=re.IGNORECASE)
    # ── แปลง #### Q3: ... ที่หลุดออกมาเป็น <p> แทน h4 ──
    html = re.sub(r'<h[34][^>]*>\s*#{2,4}\s*Q\d+[^<]*</h[34]>', '', html, flags=re.IGNORECASE)
    # ── ลบ #### markdown ดิบที่ไม่ถูก render (หลุดออกมาเป็น <p>) ──
    html = re.sub(r'<p>\s*#{2,5}\s*Q\d+[:\s][^<]{0,400}</p>', '', html)
    html = re.sub(r'<p>\s*#{2,5}\s*A\s*:[^<]{0,400}</p>', '', html)
    # ── เพิ่ม external links อัตโนมัติ ──────────────────────
    html = _ใส่_external_links(html)
    return html.strip()


# ══════════════════════════════════════════════════════════════
# 🎲 สร้าง Outline แบบสุ่มสไตล์ — แยกออกมาเป็นฟังก์ชันอิสระ
# ══════════════════════════════════════════════════════════════
def สร้าง_outline_แบบสุ่มสไตล์(หัวข้อ: str, หมวด: str, ctx: str = "") -> list:
    """
    สุ่มรูปแบบการวางโครงสร้างบทความ เพื่อไม่ให้ได้ outline ซ้ำเดิมทุกครั้ง
    คืนค่าเป็น list ของ dict {"h": หัวข้อย่อย, "desc": รายละเอียด}
    """
    สไตล์ทั้งหมด = [
        "สไตล์เล่าเรื่องแบบ Storytelling (เปิดด้วยปมปัญหา ชวนคิด มีบทสรุปสร้างแรงบันดาลใจ)",
        "สไตล์ Guidebook / How-to (ลำดับขั้นตอน 1, 2, 3 ปฏิบัติได้จริง มีทริคเสริม)",
        "สไตล์แชร์ประสบการณ์และรีวิว (เป็นกันเอง เหมือนเพื่อนเล่าให้ฟัง มีข้อดีข้อเสีย)",
        "สไตล์เจาะลึกแบบ Case Study (วิเคราะห์เหตุและผล มีข้อมูลสนับสนุน)",
        "สไตล์ Q&A (ตั้งคำถามที่คนมักสงสัย แล้วตอบให้กระจ่างเป็นข้อๆ)",
    ]
    สไตล์ที่เลือก = random.choice(สไตล์ทั้งหมด)
    log_info(f"🎲 สุ่มสไตล์บทความ: {สไตล์ที่เลือก[:40]}...")

    # คำแนะนำพิเศษตามหมวด
    OUTLINE_GUIDE = {
        "food": (
            "บทความอาหาร/สูตรอาหาร ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- วัตถุดิบที่ต้องใช้ (ระบุปริมาณ)\n"
            "- ขั้นตอนการทำทีละขั้น (Step-by-step)\n"
            "- เคล็ดลับให้อร่อย\n"
            "- การจัดจาน/เสิร์ฟ\n"
            "ห้ามเขียนเรื่องที่ไม่เกี่ยวกับอาหารนี้โดยตรง"
        ),
        "health": (
            "บทความสุขภาพ ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- อาการ/สัญญาณที่ควรรู้\n"
            "- สาเหตุและปัจจัยเสี่ยง\n"
            "- วิธีป้องกัน/รักษาเบื้องต้น\n"
            "- เมื่อไรควรพบแพทย์\n"
            "ห้ามแนะนำยาหรือการรักษาโดยไม่มีหมอ"
        ),
        "finance": (
            "บทความการเงิน ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- หลักการ/แนวคิดที่สำคัญ\n"
            "- ตัวเลข/ตัวอย่างจริงประกอบ\n"
            "- ขั้นตอนที่ทำได้จริง\n"
            "- ข้อควรระวัง/ความเสี่ยง"
        ),
        "lifestyle": (
            "บทความไลฟ์สไตล์ ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- เหตุผลว่าทำไมถึงสำคัญ\n"
            "- วิธีปฏิบัติจริงทีละขั้น\n"
            "- ตัวอย่างในชีวิตจริง\n"
            "- เคล็ดลับที่ใช้ได้ทันที"
        ),
        "sport": (
            "บทความกีฬา ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- กฎ/วิธีเล่น/ประเภท\n"
            "- เทคนิค/ท่าทาง\n"
            "- การฝึกซ้อม/พัฒนา\n"
            "- ประโยชน์ต่อสุขภาพ"
        ),
        "beauty": (
            "บทความความงาม ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- ผลิตภัณฑ์/วัตถุดิบที่ใช้\n"
            "- ขั้นตอนวิธีทำทีละขั้น\n"
            "- เคล็ดลับให้ได้ผลดี\n"
            "- ข้อควรระวัง"
        ),
        "diy": (
            "บทความ DIY ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- อุปกรณ์/วัสดุที่ต้องใช้\n"
            "- ขั้นตอนการทำทีละขั้น\n"
            "- เคล็ดลับ/วิธีแก้ปัญหา\n"
            "- ตัวอย่างผลงาน"
        ),
        "cooking": (
            "บทความสูตรอาหาร/ทำครัว ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- วัตถุดิบและเครื่องปรุงครบถ้วน พร้อมปริมาณเป็นตัวเลข\n"
            "- ขั้นตอนการทำทีละขั้น Step-by-step จริงๆ ไม่ใช่แค่สรุป\n"
            "- เคล็ดลับให้อร่อยกว่าปกติ ข้อผิดพลาดที่พบบ่อย\n"
            "- วิธีจัดจาน/เสิร์ฟ\n"
            "ห้ามบอกแบบเกริ่นๆ ต้องระบุรายละเอียดจริง"
        ),
        "tips": (
            "บทความเคล็ดลับ/How-to ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- สิ่งที่ต้องเตรียม (วัตถุดิบ อุปกรณ์) พร้อมปริมาณ/รายละเอียดจริง\n"
            "- ขั้นตอนทีละขั้น Step-by-step จริงๆ ไม่ใช่แค่บอกว่า 'ทำให้เสร็จ'\n"
            "- ข้อผิดพลาดที่พบบ่อยและวิธีแก้\n"
            "- เคล็ดลับขั้นสูง/ทริคที่ทำให้ได้ผลดีขึ้น\n"
            "ถ้ามีหลายรายการ แยกแต่ละรายการให้ชัดเจน ไม่รวมกัน"
        ),
        "story": (
            "นิทาน/เรื่องเล่า ต้องมีโครงสร้างเรื่อง:\n"
            "- บทนำ: แนะนำตัวละคร ฉาก บรรยากาศ\n"
            "- ปม: เหตุการณ์ที่ทำให้เรื่องเริ่มต้น\n"
            "- การต่อสู้/ความขัดแย้ง\n"
            "- จุดสูงสุด: ช่วงตึงเครียดที่สุด\n"
            "- การคลี่คลาย\n"
            "- บทสรุปและบทเรียน"
        ),
        "folktale": (
            "นิทานพื้นบ้าน ต้องมีโครงสร้าง:\n"
            "- ที่มาของตำนาน/เรื่องเล่า\n"
            "- ตัวละครหลักและโลกในเรื่อง\n"
            "- ภารกิจหรือปัญหาที่ต้องแก้\n"
            "- การผจญภัยและอุปสรรค\n"
            "- ชัยชนะและรางวัล\n"
            "- คติสอนใจสำหรับคนอ่าน"
        ),
        "cartoon": (
            "การ์ตูน ต้องมีโครงสร้าง:\n"
            "- แนะนำตัวละคร น่ารัก มีเอกลักษณ์\n"
            "- สถานการณ์ตลก/น่าสนุก\n"
            "- ความผิดพลาดหรือปัญหาที่เกิด\n"
            "- การแก้ปัญหาแบบสร้างสรรค์\n"
            "- บทเรียนสนุกๆ สำหรับเด็ก"
        ),
        "drama": (
            "ละคร/ดราม่า ต้องมีโครงสร้าง:\n"
            "- แนะนำตัวละครและปัญหาชีวิต\n"
            "- ความขัดแย้งกับคนรอบข้าง\n"
            "- จุดพลิกผันของชีวิต\n"
            "- การต่อสู้กับอุปสรรค\n"
            "- บทสรุปที่กินใจ"
        ),
        "inspirational": (
            "เรื่องสร้างแรงบันดาลใจ ต้องมีโครงสร้าง:\n"
            "- จุดเริ่มต้นที่ยากลำบาก\n"
            "- ช่วงเวลาที่แทบยอมแพ้\n"
            "- สิ่งที่เปลี่ยนทุกอย่าง\n"
            "- ก้าวสู่ความสำเร็จ\n"
            "- บทเรียนที่นำไปใช้ได้"
        ),
    }
    outline_guide = OUTLINE_GUIDE.get(หมวด, "")
    if outline_guide:
        outline_guide = f"\n⚠️ คำแนะนำพิเศษสำหรับหมวด {หมวด_ไทย.get(หมวด, หมวด)}:\n{outline_guide}\n"

    def _parse_any_list(raw: str) -> list:
        """Parse outline — รองรับทุก format ที่โมเดลตอบมา"""
        import re as _re
        SKIP = ["หัวข้อย่อย","สิ่งที่ต้อง","---","===","รูปแบบ","ตอบแค่","กฎ:","ห้าม","ใช้:"]
        # pattern หัวข้อที่ขึ้นต้นด้วย "ย่อหน้า N" หรือ "ตอน N" ไม่ว่าจะมีชื่อตามหรือไม่
        SKIP_RE = [
            _re.compile(r'^ย่อหน้า(ที่)?\s*\d+'),   # ย่อหน้า 1, ย่อหน้า 1: ชื่อ
            _re.compile(r'^ตอน(ที่)?\s*\d+'),        # ตอน 1, ตอน 1: ชื่อ
            _re.compile(r'^ฉาก(ที่)?\s*\d+'),        # ฉาก 1, ฉาก 1: ชื่อ
            _re.compile(r'^chapter\s*\d+', _re.IGNORECASE),
            _re.compile(r'^part\s*\d+', _re.IGNORECASE),
        ]
        result = []
        for line in raw.split("\n"):
            line = _re.sub(r'<think>.*?</think>', '', line).strip()
            if not line or any(s in line for s in SKIP):
                continue
            _h_check = line.lstrip("0123456789.-) ").strip('"\' *#')
            if any(p.match(_h_check) for p in SKIP_RE):
                continue
            if "|" in line:
                parts = line.split("|", 1)
                h = parts[0].strip().lstrip("0123456789.-) ").strip('"\' *#')
                desc = parts[1].strip() if len(parts)>1 else "อธิบายรายละเอียดและยกตัวอย่าง"
            else:
                h = line.lstrip("0123456789.-) ").strip('"\' *#')
                desc = "อธิบายรายละเอียดและยกตัวอย่างจากชีวิตจริง"
            if 4 <= len(h) <= 80 and any('\u0e00' <= c <= '\u0e7f' for c in h):
                result.append({"h": h, "desc": desc})
            if len(result) >= 7:
                break
        return result

    # รอบแรก: prompt กระชับ ให้ตอบง่าย
    outline_raw = เรียก_ollama(
        f"บทความเรื่อง \"{หัวข้อ}\" จะแบ่งเป็นหัวข้อย่อยอะไรบ้าง\n"
        f"(หมวด: {หมวด_ไทย.get(หมวด, หมวด)} | สไตล์: {สไตล์ที่เลือก})\n"
        f"{ctx}"
        f"{outline_guide}\n"
        f"ตอบ 7 หัวข้อที่เกี่ยวกับ \"{หัวข้อ}\" โดยตรง แต่ละหัวข้อต่างกัน\n"
        f"ห้ามตอบว่า 'ย่อหน้าที่ 1' 'ตอนที่ 1' 'ฉากที่ 1' ให้ตอบเป็นชื่อหัวข้อจริงๆ\n"
        f"รูปแบบ: ชื่อหัวข้อ | สิ่งที่จะพูดถึง\n"
        f"ตอบแค่ 7 บรรทัด",
        timeout=90, num_predict=700
    )
    sections = _parse_any_list(outline_raw)

    # รอบสอง: prompt ง่ายกว่า ถ้าได้น้อยกว่า 4
    if len(sections) < 4:
        log_warn(f"Outline รอบแรกได้ {len(sections)} → ลองแบบง่าย...")
        outline_raw2 = เรียก_ollama(
            f"บทความเรื่อง \"{หัวข้อ}\" ควรพูดถึงอะไรบ้าง\n"
            f"ตอบเป็นรายการ 7 ข้อ บรรทัดละ 1 ข้อ ภาษาไทย",
            timeout=60, num_predict=500
        )
        sections2 = _parse_any_list(outline_raw2)
        if len(sections2) > len(sections):
            sections = sections2

    # รอบสาม: ถ้ายังไม่พอ → ให้ AI สร้างแบบอิสระ
    if len(sections) < 4:
        log_warn(f"Outline รอบสองได้ {len(sections)} → ขอแบบอิสระ...")
        outline_raw3 = เรียก_ollama(
            f"ถ้าจะสอนเรื่อง \"{หัวข้อ}\" ให้ครบ ต้องมีหัวข้ออะไรบ้าง\n"
            f"ตอบ 7 ข้อ",
            timeout=60, num_predict=400
        )
        sections3 = _parse_any_list(outline_raw3)
        if len(sections3) > len(sections):
            sections = sections3

    # Fallback outline แยกตามหมวด — ถ้า AI ไม่ตอบ
    FALLBACK_OUTLINE = {
        "food": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "ความหมาย ที่มา ประวัติ ทำไมถึงนิยม"},
            {"h": "วัตถุดิบที่ต้องเตรียม", "desc": "รายการวัตถุดิบครบถ้วนพร้อมปริมาณที่ชัดเจน"},
            {"h": "อุปกรณ์ที่ใช้ในการทำ", "desc": "หม้อ กระทะ เครื่องมือที่ต้องใช้"},
            {"h": "ขั้นตอนการทำทีละขั้น", "desc": "Step-by-step วิธีทำตั้งแต่ต้นจนเสร็จ"},
            {"h": "เคล็ดลับให้อร่อย", "desc": "เทคนิคเฉพาะ สิ่งที่ควรทำและไม่ควรทำ"},
            {"h": "การจัดจานและเสิร์ฟ", "desc": "วิธีตกแต่ง เครื่องเคียง การนำเสนอ"},
            {"h": "คุณค่าทางโภชนาการ", "desc": "แคลอรี่ สารอาหาร ประโยชน์ต่อร่างกาย"},
        ],
        "health": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "นิยาม ความหมาย ภาพรวม"},
            {"h": "อาการและสัญญาณ", "desc": "อาการที่พบบ่อย วิธีสังเกต"},
            {"h": "สาเหตุและปัจจัยเสี่ยง", "desc": "ต้นเหตุ กลุ่มเสี่ยง ปัจจัยที่เกี่ยวข้อง"},
            {"h": "วิธีป้องกัน", "desc": "การป้องกันก่อนเกิด ปรับพฤติกรรม"},
            {"h": "วิธีรักษาเบื้องต้น", "desc": "สิ่งที่ทำได้เอง ยาสามัญ การดูแลตนเอง"},
            {"h": "เมื่อไรควรพบแพทย์", "desc": "สัญญาณอันตราย อาการที่ต้องรีบรักษา"},
            {"h": "เคล็ดลับดูแลตนเอง", "desc": "วิถีชีวิต อาหาร การออกกำลังกาย"},
        ],
        "finance": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "นิยาม ความสำคัญ ภาพรวม"},
            {"h": "หลักการสำคัญที่ควรรู้", "desc": "แนวคิดพื้นฐาน กฎที่ต้องจำ"},
            {"h": "วิธีเริ่มต้นสำหรับมือใหม่", "desc": "ขั้นตอนแรกที่ต้องทำ เตรียมตัวอย่างไร"},
            {"h": "ตัวอย่างจริงและตัวเลข", "desc": "กรณีศึกษา ตัวเลขจริง การคำนวณ"},
            {"h": "ความผิดพลาดที่พบบ่อย", "desc": "ข้อผิดพลาดที่คนมักทำ วิธีหลีกเลี่ยง"},
            {"h": "เครื่องมือและทรัพยากร", "desc": "แอป เว็บไซต์ สิ่งที่ช่วยได้"},
            {"h": "เคล็ดลับจากผู้เชี่ยวชาญ", "desc": "คำแนะนำระดับสูง กลยุทธ์ที่ได้ผล"},
        ],
        # Story modes — ใช้ชื่อฉากจริง ไม่ใช่ "ย่อหน้าที่ 1"
        "cartoon": [
            {"h": "แนะนำตัวละครหลัก", "desc": "แนะนำตัวเอก บุคลิก ความน่ารัก เอกลักษณ์"},
            {"h": "สถานการณ์ตลกเกิดขึ้น", "desc": "ปัญหาหรือสถานการณ์ที่ทำให้เรื่องเริ่ม"},
            {"h": "ความพยายามแก้ปัญหา", "desc": "ตัวละครพยายาม ผิดพลาด ตลก"},
            {"h": "พบเพื่อนใหม่ช่วยเหลือ", "desc": "ตัวละครใหม่มาช่วยหรือร่วมผจญภัย"},
            {"h": "จุดพลิกผันสนุกๆ", "desc": "เหตุการณ์เปลี่ยนทิศทางเรื่อง"},
            {"h": "แก้ปัญหาสำเร็จ", "desc": "วิธีแก้ปัญหาแบบสร้างสรรค์"},
            {"h": "บทเรียนสนุกๆ", "desc": "สิ่งที่ตัวละครเรียนรู้ คติสอนใจสำหรับเด็ก"},
        ],
        "folktale": [
            {"h": "ที่มาของตำนาน", "desc": "กาลครั้งหนึ่ง ฉาก ยุคสมัย"},
            {"h": "ตัวละครและโลกในเรื่อง", "desc": "แนะนำตัวเอก ตัวร้าย สิ่งแวดล้อม"},
            {"h": "ภารกิจที่ต้องทำ", "desc": "ปัญหาหรือภารกิจที่ตัวเอกต้องเผชิญ"},
            {"h": "การผจญภัยและอุปสรรค", "desc": "เส้นทาง อุปสรรค ศัตรูที่พบ"},
            {"h": "ชัยชนะและรางวัล", "desc": "วิธีเอาชนะ ผลลัพธ์ของภารกิจ"},
            {"h": "คติสอนใจ", "desc": "บทเรียน ความหมายที่ซ่อนอยู่ในเรื่อง"},
            {"h": "ตำนานที่สืบทอดมา", "desc": "สิ่งที่เรื่องนี้ส่งผลต่อคนในปัจจุบัน"},
        ],
        "story": [
            {"h": "บทนำ — ตัวละครและฉาก", "desc": "แนะนำตัวละครหลัก สถานที่ บรรยากาศ"},
            {"h": "จุดเริ่มต้นของปม", "desc": "เหตุการณ์ที่ทำให้เรื่องเริ่มต้น"},
            {"h": "ความขัดแย้งหลัก", "desc": "ปัญหาหลักที่ตัวเอกต้องเผชิญ"},
            {"h": "การต่อสู้กับอุปสรรค", "desc": "ตัวเอกพยายาม ล้มเหลว ลุกขึ้น"},
            {"h": "จุดสูงสุดของเรื่อง", "desc": "ช่วงตึงเครียดที่สุด การตัดสินใจสำคัญ"},
            {"h": "การคลี่คลาย", "desc": "ปัญหาถูกแก้ไข ผลลัพธ์ปรากฏ"},
            {"h": "บทสรุปและบทเรียน", "desc": "ตอนจบ สิ่งที่ตัวละครเรียนรู้"},
        ],
        "drama": [
            {"h": "แนะนำตัวละครและชีวิต", "desc": "ตัวละครหลัก บทบาท ปัญหาชีวิต"},
            {"h": "ความขัดแย้งเริ่มต้น", "desc": "ความขัดแย้งกับคนรอบข้าง จุดชนวน"},
            {"h": "จุดพลิกผันชีวิต", "desc": "เหตุการณ์ที่เปลี่ยนทุกอย่าง"},
            {"h": "การต่อสู้กับอุปสรรค", "desc": "ความยากลำบาก การพยายามอดทน"},
            {"h": "จุดสูงสุดของดราม่า", "desc": "ฉากอารมณ์สูงสุด ความตึงเครียดสุด"},
            {"h": "การคลี่คลาย", "desc": "ความขัดแย้งถูกแก้ไข"},
            {"h": "บทสรุปที่กินใจ", "desc": "ตอนจบ บทเรียนชีวิต"},
        ],
        "inspirational": [
            {"h": "จุดเริ่มต้นที่ยากลำบาก", "desc": "ชีวิตก่อนเปลี่ยน ความยากจน อุปสรรค"},
            {"h": "ช่วงเวลาที่แทบยอมแพ้", "desc": "วันที่มืดที่สุด ความท้อแท้"},
            {"h": "แรงบันดาลใจที่เจอ", "desc": "คน เหตุการณ์ หรือสิ่งที่เปลี่ยนใจ"},
            {"h": "ก้าวแรกที่เปลี่ยนชีวิต", "desc": "การตัดสินใจสำคัญ การลงมือทำ"},
            {"h": "เส้นทางสู่ความสำเร็จ", "desc": "ความพยายาม การเรียนรู้ การเติบโต"},
            {"h": "ผลลัพธ์ที่ได้", "desc": "ความสำเร็จ การเปลี่ยนแปลง"},
            {"h": "บทเรียนที่นำไปใช้ได้", "desc": "คติ คำแนะนำ แรงบันดาลใจให้ผู้อ่าน"},
        ],
        "cooking": [
            {"h": f"{หัวข้อ} — ที่มาและความน่าสนใจ", "desc": "ประวัติ เหตุผลที่นิยม คุณค่า"},
            {"h": "วัตถุดิบและเครื่องปรุงทั้งหมด", "desc": "รายการวัตถุดิบครบถ้วนพร้อมปริมาณที่ชัดเจน"},
            {"h": "อุปกรณ์ที่ใช้ในการทำ", "desc": "หม้อ กระทะ เครื่องมือที่ต้องเตรียม"},
            {"h": "ขั้นตอนการทำทีละขั้น", "desc": "Step-by-step วิธีทำตั้งแต่ต้นจนเสร็จ ระบุเวลาแต่ละขั้น"},
            {"h": "เคล็ดลับให้อร่อยกว่าร้าน", "desc": "เทคนิค ข้อผิดพลาดที่พบบ่อย ปรับรสให้ถูกจุด"},
            {"h": "การจัดจานและเสิร์ฟ", "desc": "วิธีตกแต่ง เครื่องเคียง การนำเสนอให้น่ากิน"},
            {"h": "คุณค่าทางโภชนาการ", "desc": "แคลอรี่ สารอาหาร ประโยชน์ต่อร่างกาย"},
        ],
        "tips": [
            {"h": "ทำไมเรื่องนี้ถึงสำคัญ", "desc": "เหตุผล ปัญหาที่แก้ได้ ประโยชน์ที่จะได้รับ"},
            {"h": "สิ่งที่ต้องเตรียม", "desc": "วัตถุดิบ อุปกรณ์ ทรัพยากร พร้อมรายละเอียดและปริมาณจริง"},
            {"h": "ขั้นตอนทำได้เลยทีละขั้น", "desc": "Step-by-step วิธีทำตั้งแต่ต้นจนจบ ระบุรายละเอียดทุกขั้น"},
            {"h": "ข้อผิดพลาดที่พบบ่อยและวิธีแก้", "desc": "ปัญหาที่คนมักเจอ สาเหตุ วิธีหลีกเลี่ยงหรือแก้ไข"},
            {"h": "เคล็ดลับและเทคนิคขั้นสูง", "desc": "วิธีทำให้ดียิ่งขึ้น ลัดขั้นตอน ประหยัดเวลา"},
            {"h": "ตัวอย่างจริงที่ได้ผล", "desc": "กรณีศึกษา ตัวเลขจริง ประสบการณ์ที่ทำแล้วได้ผล"},
            {"h": "สรุปและขั้นตอนถัดไป", "desc": "สรุปสาระสำคัญ สิ่งที่ทำต่อได้ทันที"},
        ],
        "ghost": [
            {"h": "บรรยากาศและฉาก", "desc": "สถานที่ลึกลับ บรรยากาศน่ากลัว"},
            {"h": "เหตุการณ์แรกที่ประหลาด", "desc": "สัญญาณแรกที่มีบางอย่างผิดปกติ"},
            {"h": "ความลึกลับทวีความน่ากลัว", "desc": "เรื่องค่อยๆ ตึงเครียดขึ้น"},
            {"h": "การสืบสาวหาความจริง", "desc": "ตัวละครพยายามหาคำตอบ"},
            {"h": "จุดสยองที่สุด", "desc": "ฉากที่น่ากลัวที่สุด หักมุม"},
            {"h": "การคลี่คลายความลึกลับ", "desc": "ความจริงที่ซ่อนอยู่ถูกเปิดเผย"},
            {"h": "บทสรุปและข้อคิด", "desc": "ตอนจบ สิ่งที่เรียนรู้จากเรื่อง"},
        ],
    }

    if len(sections) < 4:
        log_warn(f"Outline ไม่ครบ (ได้ {len(sections)}) → ใช้โครงสร้างสำรองตามหมวด '{หมวด}'")
        # ตรวจหัวข้อเป็น recipe/how-to หลายรายการ
        _is_recipe_topic = any(kw in หัวข้อ for kw in [
            "เมนู", "สูตร", "วิธีทำ", "ขั้นตอน", "ทำอาหาร",
            "ผัด", "ต้ม", "ทอด", "อบ", "นึ่ง", "ย่าง",
        ])
        if หมวด in FALLBACK_OUTLINE:
            sections = FALLBACK_OUTLINE[หมวด]
        elif _is_recipe_topic and หมวด in ("food", "cooking", "tips", "diy"):
            sections = [
                {"h": "ทำไมต้องลองเมนูนี้", "desc": "เหตุผล ประโยชน์ ความน่าสนใจ"},
                {"h": "วัตถุดิบและเครื่องปรุงทั้งหมด", "desc": "รายการวัตถุดิบแต่ละเมนูครบถ้วน พร้อมปริมาณ"},
                {"h": "ขั้นตอนการทำทีละเมนู", "desc": "Step-by-step วิธีทำแต่ละเมนูตั้งแต่ต้นจนเสร็จ"},
                {"h": "เคล็ดลับให้อร่อยกว่าเดิม", "desc": "เทคนิค ข้อผิดพลาดที่ควรหลีกเลี่ยง การปรุงรสให้ถูกจุด"},
                {"h": "การจัดจานและเสิร์ฟ", "desc": "วิธีตกแต่ง เครื่องเคียง การนำเสนอให้น่ากิน"},
                {"h": "ปรับเปลี่ยนตามสไตล์ตัวเอง", "desc": "วิธีดัดแปลง ทดแทนวัตถุดิบ ทำให้เหมาะกับความชอบ"},
                {"h": "เก็บรักษาและอุ่นซ้ำ", "desc": "วิธีเก็บ อายุอาหาร การอุ่นให้อร่อยเหมือนเดิม"},
            ]
        else:
            sections = [
                {"h": f"{หัวข้อ} คืออะไร", "desc": "ความหมาย นิยาม ภาพรวม ทำไมถึงสำคัญ"},
                {"h": f"ประเภทของ{หัวข้อ}", "desc": "แบ่งประเภท เปรียบเทียบแต่ละแบบ"},
                {"h": "วิธีการและขั้นตอน", "desc": "คำแนะนำทีละขั้นตอน เทคนิค เคล็ดลับ"},
                {"h": "ประโยชน์ที่ได้รับ", "desc": "ข้อดี ผลลัพธ์จริง กรณีศึกษา"},
                {"h": "ข้อควรระวัง", "desc": "ความเสี่ยง ข้อเสีย วิธีป้องกัน"},
                {"h": "ตัวอย่างจริง", "desc": "กรณีศึกษา ตัวอย่างในชีวิตประจำวัน"},
                {"h": "เคล็ดลับจากผู้เชี่ยวชาญ", "desc": "Tips เทคนิคขั้นสูง คำแนะนำมืออาชีพ"},
            ]

    return sections


# ══════════════════════════════════════════════════════════════
# 🎬 YouTube Embed — ค้นหาวิดีโอตรงหัวข้อ
# ══════════════════════════════════════════════════════════════
def _yt_can_embed(video_id: str) -> bool:
    """ตรวจสอบว่าวิดีโอนี้ embed ได้หรือเปล่า
    วิธี: ดึง oembed endpoint — ถ้า embeddable=True แสดงว่าใช้ได้"""
    try:
        import urllib.parse
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return True          # oembed ตอบ → embed ได้
        if r.status_code == 401: # Unauthorized = ปิด embed
            return False
        if r.status_code == 403: # Forbidden = ปิด embed
            return False
        return True              # status อื่น → ลองดูก่อน
    except Exception:
        return True              # ถ้า timeout → ลองดูก่อน


def ดึง_youtube_embed(หัวข้อ: str, หมวด: str) -> str:
    """
    ค้นหา YouTube วิดีโอตรงหัวข้อ
    - ตรวจสอบ embed ได้ก่อนเสมอ (ข้ามวิดีโอที่ Error 153)
    - Lite embed: แสดง thumbnail + กดเล่น (ไม่โหลด iframe ตาบอด)
    """
    try:
        from config import YOUTUBE_API_KEY
    except ImportError:
        YOUTUBE_API_KEY = ""

    import urllib.parse

    candidates = []

    # วิธี 1: YouTube Data API (ถ้ามี key)
    if YOUTUBE_API_KEY:
        try:
            q = urllib.parse.quote(f"{หัวข้อ} ภาษาไทย")
            api_url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&q={q}&type=video&maxResults=5"
                f"&relevanceLanguage=th&key={YOUTUBE_API_KEY}"
            )
            r = requests.get(api_url, timeout=10)
            data = r.json()
            for item in data.get("items", []):
                vid = item["id"].get("videoId", "")
                if vid:
                    candidates.append(vid)
        except Exception as e:
            log_warn(f"YouTube API ล้มเหลว: {e}")

    # วิธี 2: scrape YouTube search (ถ้ายังไม่มี)
    if not candidates:
        try:
            q = urllib.parse.quote(f"{หัวข้อ} ภาษาไทย")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = requests.get(
                f"https://www.youtube.com/results?search_query={q}",
                headers=headers, timeout=10
            )
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
            # dedup รักษาลำดับ
            seen = set()
            for m in matches:
                if m not in seen:
                    seen.add(m)
                    candidates.append(m)
                if len(candidates) >= 8:
                    break
        except Exception as e:
            log_warn(f"YouTube scrape ล้มเหลว: {e}")

    if not candidates:
        log_warn("ไม่พบวิดีโอ YouTube — ข้าม")
        return ""

    # ── หาวิดีโอแรกที่ embed ได้ ─────────────────────────────
    video_id = ""
    for vid in candidates[:5]:
        if _yt_can_embed(vid):
            video_id = vid
            log_ok(f"YouTube embed ได้: {vid}")
            break
        else:
            log_warn(f"YouTube {vid} ปิด embed — ข้าม")

    # ถ้าทุกอันปิด embed → ใช้อันแรกแต่แสดงเป็นลิงก์เท่านั้น
    fallback_only = False
    if not video_id:
        video_id = candidates[0]
        fallback_only = True
        log_warn(f"ทุกวิดีโอปิด embed — ใช้ลิงก์ YouTube แทน: {video_id}")

    # ── สร้าง HTML ──────────────────────────────────────────
    thumb_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    yt_url    = f"https://www.youtube.com/watch?v={video_id}"
    uid       = f"yt_{video_id}"

    if fallback_only:
        # แสดงแค่ thumbnail + ปุ่มดูบน YouTube (ไม่มี onclick embed)
        return (
            f'\n<div style="margin:2rem 0;">'
            f'<h2 style="color:var(--primary,#1e40af);font-size:1.1rem;margin-bottom:0.75rem;">'
            f'<i class="fab fa-youtube" style="color:#ff0000;"></i> วิดีโอที่เกี่ยวข้อง</h2>'
            f'<a href="{yt_url}" target="_blank" rel="noopener" style="display:block;text-decoration:none;">'
            f'<div style="position:relative;border-radius:12px;overflow:hidden;'
            f'box-shadow:0 4px 16px rgba(0,0,0,0.12);">'
            f'<img src="{thumb_url}" alt="{หัวข้อ}" loading="lazy" '
            f'onerror="this.onerror=null;this.style.display=\'none\'" '
            f'style="width:100%;display:block;">'
            f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;'
            f'align-items:center;justify-content:center;background:rgba(0,0,0,0.45);">'
            f'<div style="width:68px;height:48px;background:#ff0000;border-radius:12px;'
            f'display:flex;align-items:center;justify-content:center;">'
            f'<svg viewBox="0 0 68 48" width="68" height="48">'
            f'<path d="M66.52 7.74C65.7 4.62 63.27 2.19 60.15 1.37 54.9 0 33.75 0 33.75 '
            f'0S12.6 0 7.35 1.32C4.27 2.14 1.8 4.62.98 7.74 0 13 0 24 0 24s0 11 .98 16.26'
            f'c.82 3.12 3.25 5.55 6.37 6.37C12.6 48 33.75 48 33.75 48s21.15 0 26.4-1.32'
            f'c3.12-.82 5.55-3.25 6.37-6.37C68 35 68 24 68 24s-.03-11-.48-16.26z" fill="#f00"/>'
            f'<path d="M27 34l18-10-18-10v20z" fill="#fff"/></svg></div>'
            f'<p style="color:#fff;font-size:0.85rem;margin-top:0.5rem;'
            f'text-shadow:0 1px 3px rgba(0,0,0,0.8);">▶ ดูวิดีโอบน YouTube</p>'
            f'</div></div></a></div>'
        )

    # Lite embed: thumbnail + กดแล้วโหลด iframe (ใช้ nocookie domain ลด Error 153)
    onclick = (
        f"(function(el){{"
        f"var ifr=document.createElement('iframe');"
        f"ifr.src='https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&rel=0';"
        f"ifr.allow='autoplay;encrypted-media;fullscreen';"
        f"ifr.allowFullscreen=true;"
        f"ifr.style='position:absolute;top:0;left:0;width:100%;height:100%;border:none;';"
        f"el.innerHTML='';el.appendChild(ifr);"
        f"}})(this)"
    )
    return (
        f'\n<div style="margin:2rem 0;">'
        f'<h2 style="color:var(--primary,#1e40af);font-size:1.1rem;margin-bottom:0.75rem;">'
        f'<i class="fab fa-youtube" style="color:#ff0000;"></i> วิดีโอที่เกี่ยวข้อง</h2>'
        f'<div id="{uid}" '
        f'style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;'
        f'border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12);cursor:pointer;background:#000;" '
        f'onclick="{onclick}">'
        f'<img src="{thumb_url}" alt="{หัวข้อ}" loading="lazy" '
        f'onerror="this.onerror=null;this.style.display=\'none\'" '
        f'style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;">'
        f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'
        f'width:68px;height:48px;background:#ff0000;border-radius:12px;display:flex;'
        f'align-items:center;justify-content:center;pointer-events:none;">'
        f'<svg viewBox="0 0 68 48" width="68" height="48">'
        f'<path d="M66.52 7.74C65.7 4.62 63.27 2.19 60.15 1.37 54.9 0 33.75 0 33.75 '
        f'0S12.6 0 7.35 1.32C4.27 2.14 1.8 4.62.98 7.74 0 13 0 24 0 24s0 11 .98 16.26'
        f'c.82 3.12 3.25 5.55 6.37 6.37C12.6 48 33.75 48 33.75 48s21.15 0 26.4-1.32'
        f'c3.12-.82 5.55-3.25 6.37-6.37C68 35 68 24 68 24s-.03-11-.48-16.26z" fill="#f00"/>'
        f'<path d="M27 34l18-10-18-10v20z" fill="#fff"/></svg></div>'
        f'<p style="position:absolute;bottom:8px;left:50%;transform:translateX(-50%);'
        f'color:rgba(255,255,255,0.9);font-size:0.82rem;white-space:nowrap;'
        f'text-shadow:0 1px 4px rgba(0,0,0,0.9);">▶ คลิกเพื่อเล่น | '
        f'<a href="{yt_url}" target="_blank" rel="noopener" '
        f'style="color:#ffdd57;text-decoration:underline;font-weight:700;">เปิดใน YouTube ↗</a></p>'
        f'</div></div>'
    )




# ══════════════════════════════════════════════════════════════
# 💰 Affiliate + Download Links — สร้างรายได้จากเนื้อหา
# ══════════════════════════════════════════════════════════════

# Platform ดาวน์โหลดเกมฟรี (ใช้กับหมวด gaming, anime, entertainment)
GAME_PLATFORMS = [
    {"name": "Steam", "icon": "fab fa-steam", "color": "#1b2838",
     "url": "https://store.steampowered.com/search/?term={kw}&tags=493",
     "label": "ค้นหาบน Steam"},
    {"name": "Epic Games", "icon": "fas fa-gamepad", "color": "#2d2d2d",
     "url": "https://store.epicgames.com/browse?q={kw}&sortBy=relevancy",
     "label": "ค้นหาบน Epic Games"},
    {"name": "GOG", "icon": "fas fa-compact-disc", "color": "#86329f",
     "url": "https://www.gog.com/games?search={kw}",
     "label": "ค้นหาบน GOG"},
]

# Map หมวด → config affiliate
AFFILIATE_CONFIG = {
    "gaming": {
        "type": "game_download",
        "shopee_cat": "gaming",
        "lazada_cat": "gaming",
        "platforms": GAME_PLATFORMS,
    },
    "anime": {
        "type": "game_download",
        "shopee_cat": "anime",
        "lazada_cat": "anime",
        "platforms": GAME_PLATFORMS,
    },
    "food": {
        "type": "product",
        "shopee_cat": "food",
        "lazada_cat": "grocery",
        "platforms": [],
    },
    "health": {
        "type": "product",
        "shopee_cat": "health",
        "lazada_cat": "health",
        "platforms": [],
    },
    "beauty": {
        "type": "product",
        "shopee_cat": "beauty",
        "lazada_cat": "beauty",
        "platforms": [],
    },
    "travel": {
        "type": "booking",
        "shopee_cat": "travel",
        "lazada_cat": "travel",
        "platforms": [],
    },
    "finance": {
        "type": "product",
        "shopee_cat": "finance",
        "lazada_cat": "finance",
        "platforms": [],
    },
    "diy": {
        "type": "product",
        "shopee_cat": "diy",
        "lazada_cat": "tools",
        "platforms": [],
    },
    "pet": {
        "type": "product",
        "shopee_cat": "pet",
        "lazada_cat": "pet",
        "platforms": [],
    },
    "car": {
        "type": "product",
        "shopee_cat": "automotive",
        "lazada_cat": "automotive",
        "platforms": [],
    },
}


def สร้าง_affiliate_block(หัวข้อ: str, หมวด: str) -> str:
    """
    สร้างบล็อก affiliate/download ที่ตรงกับเนื้อหาบทความ
    - gaming/anime  → ปุ่มดาวน์โหลดแพลตฟอร์มเกม + Shopee/Lazada
    - travel        → Agoda + Shopee/Lazada
    - อื่นๆ          → Shopee + Lazada (keyword จากหัวข้อ)
    """
    import urllib.parse

    cfg = AFFILIATE_CONFIG.get(หมวด, {"type": "product", "shopee_cat": "", "lazada_cat": "", "platforms": []})

    # AI คิด keyword สินค้าจากหัวข้อ (สั้น กระชับ ค้นหาได้)
    try:
        kw_raw = เรียก_ollama_เร็ว(
            f'จากหัวข้อบทความ: "{หัวข้อ}"\n'
            f'คิด keyword ภาษาไทย 1-3 คำ สำหรับค้นหาสินค้าที่เกี่ยวข้องใน Shopee/Lazada\n'
            f'ตอบแค่ keyword เดียว ไม่ต้องอธิบาย'
        ).strip().split("\n")[0].strip('"\'- ')[:40]
        kw = kw_raw if len(kw_raw) > 2 else หัวข้อ[:20]
    except Exception:
        kw = หัวข้อ[:20]

    kw_enc  = urllib.parse.quote(kw)
    parts   = []

    # ── ① ปุ่มดาวน์โหลด (gaming/anime) ──────────────────────
    if cfg.get("platforms"):
        platform_btns = "".join(
            f'''<a href="{p["url"].replace("{kw}", kw_enc)}" target="_blank" rel="noopener sponsored"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.1rem;
                      background:{p["color"]};color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;transition:opacity 0.2s;"
               onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
              <i class="{p["icon"]}"></i> {p["label"]}</a>'''
            for p in cfg["platforms"]
        )
        parts.append(
            f'''<div style="background:linear-gradient(135deg,#1b2838,#2d2d2d);border-radius:12px;
                    padding:1.25rem;margin:1.5rem 0;">
              <h3 style="color:#fff;margin:0 0 0.85rem;font-size:1rem;">
                <i class="fas fa-download" style="color:#66c0f4;"></i> ดาวน์โหลด / ค้นหาเกมที่เกี่ยวข้อง
              </h3>
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">{platform_btns}</div>
            </div>'''
        )

    # ── ② Agoda (travel) ──────────────────────────────────────
    if หมวด == "travel" and AGODA_AFFILIATE:
        agoda_url = f"https://www.agoda.com/th-th/search?city={kw_enc}&tag={AGODA_AFFILIATE}"
        parts.append(
            f'''<div style="background:linear-gradient(135deg,#e53935,#b71c1c);border-radius:12px;
                    padding:1.25rem;margin:1.5rem 0;">
              <h3 style="color:#fff;margin:0 0 0.5rem;font-size:1rem;">
                <i class="fas fa-hotel"></i> ค้นหาที่พักราคาดี — {kw}
              </h3>
              <p style="color:rgba(255,255,255,0.85);margin:0 0 0.75rem;font-size:0.88rem;">
                เปรียบเทียบราคาโรงแรม รีสอร์ท หลายร้อยแห่ง จองได้ทันที
              </p>
              <a href="{agoda_url}" target="_blank" rel="noopener sponsored"
                 style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.6rem 1.4rem;
                        background:#fff;color:#b71c1c;border-radius:8px;text-decoration:none;
                        font-size:0.9rem;font-weight:700;">
                <i class="fas fa-search"></i> ค้นหาที่พักบน Agoda</a>
            </div>'''
        )

    # ── ③ Shopee ──────────────────────────────────────────────
    if SHOPEE_AFFILIATE:
        shopee_url = f"https://s.shopee.co.th/AKd8bPBUeB?keyword={kw_enc}"
        shopee_btn = (
            f'''<a href="{shopee_url}" target="_blank" rel="noopener sponsored"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                      background:#ee4d2d;color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;">
              <i class="fas fa-shopping-bag"></i> ค้นหาบน Shopee</a>'''
        )
    else:
        shopee_url  = f"https://shopee.co.th/search?keyword={kw_enc}"
        shopee_btn  = (
            f'''<a href="{shopee_url}" target="_blank" rel="noopener"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                      background:#ee4d2d;color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;">
              <i class="fas fa-shopping-bag"></i> ดูใน Shopee</a>'''
        )

    # ── ④ Lazada ─────────────────────────────────────────────
    if LAZADA_AFFILIATE:
        lazada_url = f"https://www.lazada.co.th/tag/{kw_enc}/?laz_trackid={LAZADA_AFFILIATE}"
    else:
        lazada_url = f"https://www.lazada.co.th/catalog/?q={kw_enc}"
    lazada_btn = (
        f'''<a href="{lazada_url}" target="_blank" rel="noopener sponsored"
           style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                  background:#f57224;color:#fff;border-radius:8px;text-decoration:none;
                  font-size:0.88rem;font-weight:600;">
          <i class="fas fa-tag"></i> ดูใน Lazada</a>'''
    )

    # รวม Shopee + Lazada เป็นบล็อกเดียว
    parts.append(
        f'''<div style="background:var(--soft,#f1f5f9);border-radius:12px;
                padding:1.25rem;margin:1.5rem 0;border:1px solid var(--border,#e2e8f0);">
          <h3 style="color:var(--dark,#1e293b);margin:0 0 0.6rem;font-size:0.95rem;">
            <i class="fas fa-shopping-cart" style="color:#ee4d2d;"></i>
            สินค้าที่เกี่ยวข้องกับ <em>{kw}</em>
          </h3>
          <p style="margin:0 0 0.75rem;font-size:0.85rem;color:var(--muted,#64748b);">
            เปรียบเทียบราคา หาของดีราคาถูกได้ที่นี่
          </p>
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
            {shopee_btn}
            {lazada_btn}
          </div>
          <p style="margin:0.6rem 0 0;font-size:0.75rem;color:var(--muted,#94a3b8);">
            * ลิงก์บางส่วนเป็น Affiliate Link — เราได้รับค่าคอมมิชชันเล็กน้อยโดยไม่มีค่าใช้จ่ายเพิ่มสำหรับคุณ
          </p>
        </div>'''
    )

    if not parts:
        return ""

    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════
# ✍️ เขียนบทความแบบ Chunked — ยาว ลึก มีคุณภาพ
# ══════════════════════════════════════════════════════════════
def เขียนบทความ(หัวข้อ: str, หมวด: str) -> str:
    """
    Chunked Writing — เขียนทีละ section แล้วรวม:
    0. Scrape ข้อมูลอ้างอิง
    1. วาง Outline (6-8 section)
    2. เขียน Intro (3-4 ย่อหน้า)
    3. เขียนทีละ section (แต่ละ section 400-600 คำ)
    4. แทรกรูปทุก 2 section
    5. เขียน Conclusion + FAQ
    6. รวมทุกส่วน → บทความ 2,500-4,000 คำ

    Story Mode (หมวด story/ghost): ปรับ prompt ให้เล่าเรื่องแบบนิทาน/ตำนาน
    รูปจะเป็นแนวการ์ตูน/ลึกลับตามประเภท
    """
    log_ai(f"เขียนบทความ (Chunked): {หัวข้อ}")
    log_info(f"หมวด: {หมวด} | หมวดไทย: {หมวด_ไทย.get(หมวด, หมวด)}")

    # ── ตรวจ Story Mode ───────────────────────────────────
    is_story  = หมวด in ("story", "ghost", "comedy", "folktale", "cartoon", "drama", "inspirational")
    # keyword สำหรับรูปภาพตามประเภท
    _STORY_IMG = {
        "story": "cute cartoon animals illustrated children storybook colorful",
        "ghost": "dark mysterious thai temple night fog spirit atmospheric",
        "comedy": "funny cartoon illustration colorful cheerful",
        "folktale": "thai traditional folklore illustration ancient colorful painting",
        "cartoon": "cute cartoon character colorful illustration children comic",
        "drama": "dramatic emotional scene thai people story illustration",
        "inspirational": "inspiring sunrise mountain journey hope colorful",
    }
    story_img_kw = _STORY_IMG.get(หมวด, "")
    # Story mode: แทรกรูปทุก 2 section (บทความเรื่องเล่าต้องการภาพมากกว่า)
    _story_img_every = 2 if is_story else 999

    # ── STEP 0: Scrape อ้างอิง ────────────────────────────
    อ้างอิง = scrape_อ้างอิง(หัวข้อ)
    ctx = f"\nข้อมูลอ้างอิง (นำมาใช้ประกอบ):\n{อ้างอิง[:3000]}\n" if อ้างอิง else ""

    # ── STEP 1: Outline ───────────────────────────────────
    log_info("STEP 1/6 — วาง Outline...")
    sections = สร้าง_outline_แบบสุ่มสไตล์(หัวข้อ, หมวด, ctx)

    if not sections:
        log_err("ไม่ได้ Outline — หยุดการเขียน")
        return ""

    log_ok(f"Outline: {len(sections)} หัวข้อย่อย")
    for i, s in enumerate(sections, 1):
        log(f"  {i}. {s['h']}")

    parts_html = []

    # ── STEP 2: เขียน Intro ───────────────────────────────
    log_info("STEP 2/6 — เขียน Intro...")
    if is_story:
        # Story Mode: เปิดแบบนิทาน/เรื่องเล่า
        _story_open = {
            "story": "เขียนเหมือนนักเล่านิทานไทยโบราณที่เล่าให้เด็กๆ ฟังก่อนนอน มีเสน่ห์ ชวนติดตาม",
            "ghost": "เขียนเหมือนรุ่นพี่เล่าเรื่องผีให้ฟังยามดึก บรรยากาศขนลุก ลึกลับ น่ากลัวแต่น่าอ่าน",
            "comedy": "เขียนเหมือนนักเล่าเรื่องตลก ภาษาพูด มีมุกแทรก ทำให้อยากอ่านต่อ",
            "folktale": "เขียนเหมือนนิทานพื้นบ้านไทย มีตัวละครชัดเจน บรรยากาศไทยโบราณ สอนใจ",
            "cartoon": "เขียนเหมือนการ์ตูนแอนิเมชัน สนุกสนาน ตัวละครน่ารัก เหมาะสำหรับทุกวัย",
            "drama": "เขียนเหมือนละครไทยที่ดึงอารมณ์ผู้อ่าน มีความขัดแย้ง ความรัก การต่อสู้ชีวิต",
            "inspirational": "เขียนเหมือนนักพูดสร้างแรงบันดาลใจ อบอุ่น ให้กำลังใจ ทำให้รู้สึกอยากลุกขึ้นสู้",
        }
        intro_style = _story_open.get(หมวด, _story_open["story"])
        intro_raw = เรียก_ollama(
            f"เขียนย่อหน้าเปิดเรื่อง \"{หัวข้อ}\" สำหรับหน้าเว็บภาษาไทย\n"
            f"สไตล์: {intro_style}\n"
            f"กฎ:\n"
            f"- เขียน 3-4 ย่อหน้า รวม 300-500 คำ\n"
            f"- ย่อหน้าแรกต้องดึงดูดทันที เหมือนเริ่มเล่าเรื่องเลย\n"
            f"- แทรกบรรยากาศ สถานที่ เวลา ให้เห็นภาพ\n"
            f"- ห้ามขึ้นต้นด้วย 'บทความนี้' 'วันนี้'\n"
            f"- เขียน Markdown เท่านั้น ห้าม HTML",
            timeout=180, num_predict=1500
        )
    else:
        intro_raw = เรียก_ollama(
            f"เขียนย่อหน้าเปิดบทความภาษาไทยเรื่อง \"{หัวข้อ}\" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n"
            f"{ctx}\n"
            f"สไตล์: บล็อกเกอร์ไทยที่รู้จริงเรื่องนี้ พูดกับเพื่อนสนิท ไม่ต้องทางการ\n"
            f"กฎสำคัญ:\n"
            f"- เขียน 3-4 ย่อหน้า รวม 300-500 คำ\n"
            f"- ประโยคแรก ห้ามขึ้นต้นด้วย 'บทความนี้' 'วันนี้' 'ในปัจจุบัน'\n"
            f"  ให้ใช้แทนด้วย: ตั้งคำถามน่าสงสัย / ตัวเลขสะดุดตา / เหตุการณ์จริงสั้นๆ\n"
            f"- ย่อหน้า 2-3: อธิบายว่าทำไมเรื่องนี้สำคัญกับชีวิตของผู้อ่านโดยตรง\n"
            f"- ย่อหน้าสุดท้าย: บอกว่าในบทความนี้จะได้อะไรบ้าง (ไม่ต้องใช้คำว่า 'บทความนี้')\n"
            f"- ใช้คำว่า 'นะ' 'ครับ/ค่ะ' 'จริงๆ' 'อย่างนี้' ได้บ้างเพื่อความเป็นกันเอง\n"
            f"- เขียน Markdown เท่านั้น ห้าม HTML",
            timeout=180, num_predict=1500
        )
    intro_html = ทำความสะอาด_html(แปลง_md_html(intro_raw))
    if len(intro_html) > 100:
        parts_html.append(intro_html)
        log_ok(f"Intro เสร็จ: {len(intro_html)} ตัว")
    else:
        log_warn("Intro สั้นมาก — ใช้ fallback")
        parts_html.append(f"<p>{หัวข้อ} เป็นเรื่องที่น่าสนใจและมีความสำคัญในชีวิตประจำวัน บทความนี้จะพาคุณไปทำความรู้จักกับทุกแง่มุมของเรื่องนี้อย่างละเอียด</p>")

    # ── STEP 3: เขียนทีละ Section ─────────────────────────
    log_info("STEP 3/6 — เขียนทีละ Section...")
    written_headings: list = []  # track หัวข้อที่เขียนแล้ว เพื่อ coherence

    for i, sec in enumerate(sections):
        log_info(f"  Section {i+1}/{len(sections)}: {sec['h']}")

        # ── กรอง paragraph อ้างอิงที่ตรงกับ section นี้ ──────
        # เลือกเฉพาะย่อหน้าที่มี keyword ของ section นี้ก่อน แล้ว fallback ทั้งหมด
        _sec_keywords = set(sec['h'].replace('และ','').replace('ของ','').split())
        _relevant = [p for p in อ้างอิง.split('\n\n')
                     if any(kw in p for kw in _sec_keywords) and len(p) > 60]
        _ctx_para = '\n\n'.join(_relevant[:5]) if _relevant else อ้างอิง[:2000]
        ctx_sec = f"\nข้อมูลอ้างอิงสำหรับ section นี้:\n{_ctx_para}\n" if _ctx_para else ""

        # ── เพิ่ม written_so_far context ─────────────────────
        written_so_far = ""
        if written_headings:
            written_so_far = (
                f"\n⚠️ section ที่เขียนไปแล้ว (ห้ามซ้ำ): {', '.join(written_headings)}\n"
                f"section ปัจจุบันต้องต่อเนื่องและไม่ทับซ้อนกับที่เขียนไปแล้ว\n"
            )

        # สุ่มสไตล์ย่อยเพื่อให้แต่ละ section ไม่ซ้ำกัน
        _micro_styles = [
            "เล่าเรื่องจากประสบการณ์จริง มีอารมณ์ขันเล็กน้อย ภาษาพูด",
            "ให้ข้อมูลเชิงลึก ตัวเลข สถิติ เปรียบเทียบ ก่อน-หลัง",
            "ตั้งคำถามนำ แล้วตอบทีละประเด็น เหมือน Q&A สั้นๆ",
            "เล่าเป็น story arc: ปัญหา → ลองแก้ → ผลที่ได้ → บทเรียน",
            "ให้ step-by-step ที่ทำได้จริงวันนี้เลย พร้อมเตือนข้อผิดพลาดที่พบบ่อย",
        ]

        if is_story:
            # Story mode: เล่าต่อเนื่องเหมือนนิทานจริง ไม่มี heading คั่น
            # ใช้ข้อมูลอ้างอิงจาก scrape เพื่อให้เรื่องมีรากฐานจริง ไม่คิดเอง
            _story_sec_styles = {
                "story":         "นักเล่านิทานไทยที่เล่าให้เด็กฟัง สนุก มีชีวิตชีวา ลื่นไหล",
                "ghost":         "นักเล่าเรื่องผีค่ำคืน บรรยายละเอียด บรรยากาศขนลุก ค่อยๆ เพิ่มความน่ากลัว",
                "comedy":        "นักเล่าเรื่องตลกมืออาชีพ มีมุกแทรก จังหวะดี อ่านแล้วยิ้มได้",
                "folktale":      "ผู้เฒ่าผู้แก่เล่านิทานพื้นบ้านให้หลานฟัง สำเนียงอบอุ่น มีคติสอนใจ",
                "cartoon":       "นักเขียนการ์ตูนเล่าเรื่องน่ารัก ตัวละครมีชีวิตชีวา เหมาะสำหรับเด็กทุกวัย",
                "drama":         "นักเขียนละครไทยที่ดึงอารมณ์ได้ดี อารมณ์เข้มข้น สะเทือนใจ",
                "inspirational": "โค้ชชีวิตที่อบอุ่น เล่าเรื่องจริงจากชีวิต ให้กำลังใจ ทำให้อยากลุกขึ้นสู้",
            }
            _style = _story_sec_styles.get(หมวด, "นักเล่าเรื่องมืออาชีพ ภาษาไทยสวย อ่านลื่น")
            section_raw = เรียก_ollama(
                f"เรื่อง: {หัวข้อ}\n"
                f"เล่าต่อจากส่วนที่แล้ว — ฉาก/ตอน: {sec['h']} ({sec['desc']})\n"
                f"{ctx_sec}"
                f"{written_so_far}"
                f"สไตล์: {_style}\n"
                f"เขียน 4-5 ย่อหน้าต่อเนื่อง ไม่ต้องมีหัวข้อ ไม่ต้องมี ## นำหน้า\n"
                f"มีบทสนทนา บรรยายฉาก อารมณ์ตัวละครให้เห็นภาพ\n"
                f"เขียนเป็น Markdown ย่อหน้าธรรมดา ไม่มี heading",
                timeout=250, num_predict=2500
            )
            # story mode: ลบ ## heading ออกเพื่อให้เป็นย่อหน้าต่อเนื่อง
            section_raw = re.sub(r'^#{1,6}\s+.+$', '', section_raw, flags=re.MULTILINE)
        else:
            _style = _micro_styles[i % len(_micro_styles)]
            # FIX: แยก instruction ออกจากเนื้อหาอย่างชัดเจน
            # ไม่ใส่ "## heading" + "กฎ:" ในก้อนเดียวกัน เพราะโมเดลจะ copy กฎออกมาในเนื้อหาด้วย

            # ── บังคับโครงสร้างสำหรับ section วัตถุดิบ/ขั้นตอน ──
            _force_ingredients = any(kw in sec['h'] for kw in [
                "วัตถุดิบ", "เครื่องปรุง", "ส่วนผสม", "สิ่งที่ต้องเตรียม", "อุปกรณ์",
            ])
            _force_steps = any(kw in sec['h'] for kw in [
                "ขั้นตอน", "วิธีทำ", "วิธีการ", "การทำ", "ทีละขั้น",
            ])
            _is_howto_cat = หมวด in ("food", "cooking", "tips", "diy", "beauty")

            if _force_ingredients and _is_howto_cat:
                section_raw = เรียก_ollama(
                    f"บทความเรื่อง \"{หัวข้อ}\" หมวด {หมวด_ไทย.get(หมวด, หมวด)}\n"
                    f"ขอเนื้อหาส่วน \"{sec['h']}\" ครอบคลุมประเด็น: {sec['desc']}\n"
                    f"{ctx_sec}"
                    f"{written_so_far}"
                    f"กฎสำคัญ — ต้องระบุรายละเอียดจริง ห้ามบอกแบบเกริ่นๆ:\n"
                    f"- ถ้ามีหลายเมนู/รายการ: แยกแต่ละรายการด้วย ### ชื่อเมนู\n"
                    f"- ระบุปริมาณเป็นตัวเลขชัดเจน เช่น 2 ช้อนโต๊ะ, 100 กรัม, 3 กลีบ\n"
                    f"- เครื่องปรุงหลักห้ามบอกว่า 'ตามชอบ' ต้องบอกปริมาณเริ่มต้น\n"
                    f"- ขึ้นต้นด้วย ## {sec['h']} แล้วเขียนเนื้อหาต่อเลย ห้าม copy คำสั่งนี้\n"
                    f"เขียน Markdown ห้ามใช้ HTML",
                    timeout=250, num_predict=2500
                )
            elif _force_steps and _is_howto_cat:
                section_raw = เรียก_ollama(
                    f"บทความเรื่อง \"{หัวข้อ}\" หมวด {หมวด_ไทย.get(หมวด, หมวด)}\n"
                    f"ขอเนื้อหาส่วน \"{sec['h']}\" ครอบคลุมประเด็น: {sec['desc']}\n"
                    f"{ctx_sec}"
                    f"{written_so_far}"
                    f"กฎสำคัญ — เขียน step-by-step จริงๆ ไม่ใช่แค่บอกว่า 'ทำให้เสร็จ':\n"
                    f"- ถ้ามีหลายเมนู: แยกแต่ละเมนูด้วย ### ชื่อเมนู แล้วบอก step 1, 2, 3...\n"
                    f"- แต่ละ step ระบุ: ทำอะไร, ใช้อะไร, ใช้เวลากี่นาที/ความร้อนเท่าไร\n"
                    f"- บอกสัญญาณที่รู้ว่าสุก/เสร็จ เช่น 'จนเหลืองกรอบ' 'จนซอสข้น'\n"
                    f"- ขึ้นต้นด้วย ## {sec['h']} แล้วเขียนเนื้อหาต่อเลย ห้าม copy คำสั่งนี้\n"
                    f"เขียน Markdown ห้ามใช้ HTML",
                    timeout=250, num_predict=2500
                )
            else:
                section_raw = เรียก_ollama(
                    f"บทความเรื่อง \"{หัวข้อ}\" หมวด {หมวด_ไทย.get(หมวด, หมวด)}\n"
                    f"ขอเนื้อหาส่วน \"{sec['h']}\" ครอบคลุมประเด็น: {sec['desc']}\n"
                    f"{ctx_sec}"
                    f"{written_so_far}"
                    f"เขียนเนื้อหา 4-6 ย่อหน้า ภาษาไทย สไตล์: {_style}\n"
                    f"ขึ้นต้นด้วย ## {sec['h']} แล้วเขียนเนื้อหาต่อเลย ห้าม copy คำสั่งนี้\n"
                    f"เขียน Markdown ห้ามใช้ HTML",
                    timeout=250, num_predict=2500
                )

        section_html = ทำความสะอาด_html(แปลง_md_html(section_raw))

        # ตรวจสอบคุณภาพ — ถ้าสั้นเกินไป ลองใหม่อีกครั้ง
        if len(section_html) < 300:
            log_warn(f"  Section {i+1} สั้นเกิน ({len(section_html)} ตัว) — ลองใหม่...")
            section_raw2 = เรียก_ollama(
                f"เขียนเนื้อหาเรื่อง \"{sec['h']}\" ให้ยาวและละเอียด\n"
                f"หัวข้อหลัก: {หัวข้อ} (หมวด{หมวด_ไทย.get(หมวด,หมวด)})\n"
                f"ครอบคลุม: {sec['desc']}\n\n"
                f"ต้องมี: ย่อหน้าอย่างน้อย 4 ย่อหน้า, ตัวอย่างจริง, รายการ bullet\n"
                f"ตอบเป็น Markdown ใช้ ## และ - เท่านั้น ห้ามใช้ HTML",
                timeout=220, num_predict=2200
            )
            section_html = ทำความสะอาด_html(แปลง_md_html(section_raw2))

        # แทรกรูป: ทุกประเภทใช้ keyword ตรงกับ section นั้นๆ (แก้บัครูปซ้ำ)
        # story mode: ทุก 2 section | บทความปกติ: ทุก 3 section (ข้าม section แรก)
        should_insert_img = (
            (is_story and i > 0 and i % 2 == 0) or
            (not is_story and i > 0 and i % 3 == 0)
        )
        if should_insert_img:
            import hashlib as _hlib
            seed = _hlib.md5((หัวข้อ + sec['h']).encode()).hexdigest()[:12]
            fallback = f"https://picsum.photos/seed/{seed}/800/350"
            # keyword ตรงกับ section นี้เสมอ — ทั้ง story และ บทความปกติ
            try:
                if is_story:
                    _eg = (
                        'Examples:\n'
                        '  "บรรยากาศและฉาก" (ghost) → "dark thai temple night fog mysterious"\n'
                        '  "ตัวละครและโลกในเรื่อง" (folktale) → "thai traditional costume colorful ancient"\n'
                        '  "จุดสูงสุดของเรื่อง" (drama) → "dramatic emotional thai people conflict scene"'
                    )
                else:
                    _eg = (
                        'Examples:\n'
                        f'  "วัตถุดิบและเครื่องปรุง" (food) → "{หัวข้อ[:15]} ingredients spices bowl close-up"\n'
                        f'  "ขั้นตอนการทำ" (cooking) → "chef cooking wok flame thai kitchen process"\n'
                        f'  "คุณค่าทางโภชนาการ" (health) → "nutrition facts vegetables fruits healthy colorful"\n'
                        f'  "เคล็ดลับการดูแลผิว" (beauty) → "skincare serum woman applying face glow"'
                    )
                _scene_kw_prompt = (
                    f'Article: "{หัวข้อ}" (category: {หมวด})\n'
                    f'Section: "{sec["h"]}"\n'
                    f'Section description: {sec["desc"]}\n'
                    f'Write 4-5 specific English keywords for a stock photo that matches THIS section.\n'
                    f'The photo should show exactly what this section is about — not just the general topic.\n'
                    f'{_eg}\n'
                    f'Reply with keywords ONLY.'
                )
                from config import เรียก_ollama_เร็ว as _ollama_fast
                _scene_kw = _ollama_fast(_scene_kw_prompt).strip().split('\n')[0][:100]
                # กรอง → ออก ถ้า AI ยังใส่มา
                _scene_kw = _scene_kw.split('→')[-1].strip().strip('"\'')
                if not _scene_kw or len(_scene_kw) < 5:
                    raise ValueError("empty")
            except Exception:
                _scene_kw = story_img_kw if is_story else f"{หัวข้อ[:20]} {sec['h'][:20]}"
            img_url = ดึงรูป_ตรงเนื้อหา(_scene_kw, หมวด, _scene_kw)
            img_html = (
                f'<figure style="margin:1.5rem 0;border-radius:12px;overflow:hidden;'
                f'box-shadow:0 2px 12px rgba(0,0,0,0.15);">'
                f'<img src="{img_url}" alt="{sec["h"]}" loading="lazy" '
                f'onerror="this.onerror=null;this.src=\'{fallback}\'" '
                f'style="width:100%;max-height:400px;object-fit:cover;">'
                f'<figcaption style="text-align:center;font-size:0.85rem;color:#64748b;'
                f'padding:0.5rem;">{sec["h"]}</figcaption></figure>'
            )
            parts_html.append(img_html)
            log_info(f"  แทรกรูป section {i+1}/{len(sections)}: {_scene_kw}")

        parts_html.append(section_html)
        written_headings.append(sec['h'])  # track สำหรับ section ถัดไป
        log_ok(f"  Section {i+1} เสร็จ: {len(section_html)} ตัว")
        time.sleep(0.3)  # ป้องกัน Ollama overload

    # ── STEP 4: YouTube Embed ─────────────────────────────
    log_info("STEP 4/7 — ค้นหา YouTube embed...")
    youtube_html = ดึง_youtube_embed(หัวข้อ, หมวด)
    if youtube_html:
        parts_html.append(youtube_html)
        log_ok("เพิ่ม YouTube embed แล้ว")

    # ── STEP 5: FAQ ───────────────────────────────────────
    log_info("STEP 5/7 — เขียน FAQ...")
    faq_raw = เรียก_ollama(
        f"เขียน FAQ (คำถามที่พบบ่อย) สำหรับบทความเรื่อง \"{หัวข้อ}\"\n"
        f"กฎ: 5 คำถาม แต่ละคำถามมีคำตอบ 2-3 ประโยค\n"
        f"รูปแบบ Markdown: ใช้ ### คำถาม และขึ้นบรรทัดใหม่ตอบคำถาม ห้ามใช้ HTML",
        timeout=180, num_predict=1500
    )
    faq_html = ทำความสะอาด_html(แปลง_md_html(faq_raw))
    if len(faq_html) > 100:
        # สร้าง FAQPage schema จาก faq_raw
        import re as _re
        faq_pairs = []
        qs = _re.split(r'(?:^|\n)#{2,3}\s+', faq_raw.strip())
        for block in qs:
            block = block.strip()
            if not block: continue
            lines = block.split("\n", 1)
            q = lines[0].strip().lstrip("0123456789.) ").strip("?")
            a = lines[1].strip() if len(lines) > 1 else ""
            a = _re.sub(r'[\n\r]+', " ", a).strip()
            if q and a and any("\u0e00" <= c <= "\u0e7f" for c in q):
                q_esc = q.replace('"', '\"')
                a_esc = a[:300].replace('"', '\"')
                faq_pairs.append(f'{{"@type":"Question","name":"{q_esc}","acceptedAnswer":{{"@type":"Answer","text":"{a_esc}"}}}}'
                )
        if faq_pairs:
            _joined = ",".join(faq_pairs[:5])
            faq_ld = (
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@type":"FAQPage",'
                '"mainEntity":[' + _joined + ']}'
                '</script>'
            )
            parts_html.append(faq_ld)
        parts_html.append(
            f'\n<div style="background:var(--soft,#f1f5f9);border-radius:12px;padding:1.5rem;margin-top:2rem;">'
            f'\n<h2 style="color:var(--primary,#1e40af);margin-top:0;">❓ คำถามที่พบบ่อย</h2>'
            f'\n{faq_html}\n</div>'
        )
        log_ok(f"FAQ เสร็จ: {len(faq_html)} ตัว + FAQPage schema")

    # ── STEP 6: Conclusion ────────────────────────────────
    log_info("STEP 6/7 — เขียน Conclusion...")
    conclusion_raw = เรียก_ollama(
        f"เขียนบทสรุปของบทความเรื่อง \"{หัวข้อ}\" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n"
        f"## สรุป\n\n"
        f"กฎ:\n"
        f"- ย่อหน้า 1: สรุป insight สำคัญที่สุด 1-2 ข้อ\n"
        f"- ย่อหน้า 2: บอกว่าถ้าจะเริ่มทำ ควรเริ่มตรงไหนก่อน (CTA ชัดเจน)\n"
        f"- ย่อหน้า 3: ปิดด้วยประโยคสร้างแรงบันดาลใจ ไม่ใช่แค่ 'หวังว่าจะเป็นประโยชน์'\n"
        f"- ห้ามใช้ประโยคปิดแบบ AI ทั่วไป เช่น 'หวังว่าบทความนี้จะเป็นประโยชน์'\n"
        f"- เขียน Markdown ห้ามใช้ HTML",
        timeout=150, num_predict=1000
    )
    conclusion_html = ทำความสะอาด_html(แปลง_md_html(conclusion_raw))
    if len(conclusion_html) > 80:
        parts_html.append(conclusion_html)
        log_ok(f"Conclusion เสร็จ: {len(conclusion_html)} ตัว")

    # ── STEP 7: Affiliate / Download links ──────────────
    log_info("STEP 7/7 — สร้าง Affiliate block...")
    aff_html = สร้าง_affiliate_block(หัวข้อ, หมวด)
    if aff_html:
        parts_html.append(aff_html)
        log_ok("เพิ่ม Affiliate block แล้ว")

    # ── STEP 8: รวมทุกส่วน ───────────────────────────────
    log_info("STEP 8/8 — รวมบทความ...")
    result = "\n\n".join(parts_html)
    total_len = len(result)
    total_words = len(result.split())

    log_ok(f"บทความสมบูรณ์: {total_len:,} ตัวอักษร | ~{total_words:,} คำ")

    if total_len < 1000:
        log_warn("บทความสั้นเกินไป! ตรวจสอบ Ollama ว่าทำงานอยู่")

    return result


# ══════════════════════════════════════════════════════════════
# 🏗️ Topic Cluster — สร้างหลายบทความเชื่อมกัน
# ══════════════════════════════════════════════════════════════
def ai_คิดหัวข้อย่อย(หัวข้อหลัก: str, หมวด: str) -> list:
    log_ai(f"คิดหัวข้อย่อย: {หัวข้อหลัก}")
    raw = เรียก_ollama(
        f'หัวข้อหลัก: "{หัวข้อหลัก}" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n'
        f'คิดหัวข้อบทความที่เกี่ยวข้อง 4 หัวข้อ\n'
        f'กฎ:\n'
        f'- แต่ละหัวข้อต้องต่างกันอย่างชัดเจน\n'
        f'- ครอบคลุมคนละมุม: เช่น วิธีทำ / ประวัติ / เปรียบเทียบ / แก้ปัญหา\n'
        f'- ตอบแค่รายการ บรรทัดละ 1 หัวข้อ ไม่ต้องใส่หมายเลข',
        timeout=90
    )
    result = []
    for line in raw.split("\n"):
        line = line.strip().lstrip("0123456789.-) ").strip()
        # กรอง <think> tags จาก deepseek
        line = re.sub(r'<think>.*?</think>', '', line, flags=re.DOTALL).strip()
        if len(line) > 5 and any('\u0e00' <= c <= '\u0e7f' for c in line):
            result.append(line)
    return result[:4] if len(result) >= 2 else [
        f"ประโยชน์ของ{หัวข้อหลัก}",
        f"วิธีเริ่มต้น{หัวข้อหลัก}สำหรับมือใหม่",
        f"ข้อผิดพลาดที่ควรหลีกเลี่ยงใน{หัวข้อหลัก}",
    ]


def สร้าง_topic_cluster(หัวข้อหลัก: str, หมวด: str) -> list:
    log_section(f"🏗️ Topic Cluster: {หัวข้อหลัก}")
    บทความทั้งหมด = []

    # บทความหลัก
    log_info("เขียนบทความหลัก...")
    เนื้อหา = เขียนบทความ(หัวข้อหลัก, หมวด)
    if เนื้อหา:
        ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อหลัก, หมวด, เนื้อหา)
        บทความทั้งหมด.append((หัวข้อหลัก, ชื่อไฟล์, รูป))
        log_ok(f"บทความหลัก: {ชื่อไฟล์}")

    # บทความย่อย (3 บทความ)
    หัวข้อย่อย = ai_คิดหัวข้อย่อย(หัวข้อหลัก, หมวด)
    for i, หัวข้อ_ย่อย in enumerate(หัวข้อย่อย[:3]):
        log_info(f"เขียนบทความย่อย {i+1}/{min(len(หัวข้อย่อย),3)}: {หัวข้อ_ย่อย}")
        เนื้อหา = เขียนบทความ(หัวข้อ_ย่อย, หมวด)
        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ย่อย, หมวด, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_ย่อย, ชื่อไฟล์, รูป))
            log_ok(f"บทความย่อย {i+1}: {ชื่อไฟล์}")

    return บทความทั้งหมด


# ══════════════════════════════════════════════════════════════
# 💾 บันทึกบทความ + HTML Template
# ══════════════════════════════════════════════════════════════
def _head_html(title, desc, filename, og_img="", cat="", cat_th="", date_iso=""):
    og_img  = og_img or f"{SITE_URL}/images/og-default.png"
    _gsc    = os.getenv("GSC_VERIFY", "")   # Google Search Console verify tag
    _gsc_tag = f'\n  <meta name="google-site-verification" content="{_gsc}">' if _gsc else ""
    ga4 = (
        f'\n  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
        f'\n  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
        f'gtag("js",new Date());gtag("config","{GA4_ID}");</script>'
    ) if GA4_ID else ""
    # Breadcrumb JSON-LD
    _cat_url = f"{SITE_URL}/{cat}.html" if cat else f"{SITE_URL}/"
    _cat_label = cat_th or cat or "หน้าแรก"
    _breadcrumb = f"""
  <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"BreadcrumbList",
    "itemListElement":[
      {{"@type":"ListItem","position":1,"name":"หน้าแรก","item":"{SITE_URL}/"}},
      {{"@type":"ListItem","position":2,"name":"{_cat_label}","item":"{_cat_url}"}},
      {{"@type":"ListItem","position":3,"name":"{title.split(" | ")[0]}","item":"{SITE_URL}/{filename}"}}
    ]
  }}</script>"""
    # WebPage + Article combined JSON-LD
    _article_ld = f"""
  <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"Article",
    "headline":"{title.split(" | ")[0]}",
    "description":"{desc}",
    "image":"{og_img}",
    "datePublished":"{date_iso}",
    "dateModified":"{date_iso}",
    "inLanguage":"th",
    "author":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},
    "publisher":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}","logo":{{"@type":"ImageObject","url":"{SITE_URL}/images/icon-192.png"}}}},
    "mainEntityOfPage":{{"@type":"WebPage","@id":"{SITE_URL}/{filename}"}}
  }}</script>"""
    return f"""  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#1e40af">{_gsc_tag}
  <link rel="canonical" href="{SITE_URL}/{filename}">
  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="images/icon-192.png">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_img}">
  <meta property="og:url" content="{SITE_URL}/{filename}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="th_TH">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_img}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v6.5.0/css/all.css" media="print" onload="this.media='all';this.onload=null">
  <link rel="stylesheet" href="style.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB}" crossorigin="anonymous"></script>{ga4}{_breadcrumb}{_article_ld}"""


ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
{head}
</head>
<body>
<script src="nav.js"></script>
<div class="container">
  <article class="article-card content-area">
    <h1>{title}</h1>
    <div class="article-meta">
      <i class="far fa-calendar-alt"></i> วันที่: {date_th} |
      <i class="fas fa-tag"></i> หมวด: <a href="{cat_page}">{category_th}</a>
    </div>
    <div class="hero-image-wrapper">
      <img src="{img_url}" alt="{title}" loading="eager"
           onerror="this.onerror=null;this.src='{img_fallback}'">
    </div>
    <div class="article-body">
      {content}
    </div>
    <div class="share-buttons" style="margin:2rem 0 1rem;padding:1rem 1.25rem;background:var(--soft,#f1f5f9);border-radius:12px;">
      <p style="margin:0 0 0.75rem;font-size:0.9rem;font-weight:600;color:var(--dark,#1e293b);">
        <i class="fas fa-share-alt"></i> แชร์บทความนี้
      </p>
      <div id="share-btns" style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">
        <!-- สร้างโดย JS เพื่อ encode title อย่างถูกต้อง -->
      </div>
      <script>
      (function(){{
        var u=encodeURIComponent(location.href);
        var t=encodeURIComponent(document.title.split(' | ')[0]);
        var BTN='display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;';
        var X_SVG='<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.253 5.622L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>';
        var T_SVG='<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 192 192" fill="white"><path d="M141.537 88.988a66.667 66.667 0 0 0-2.518-1.143c-1.482-27.307-16.403-42.94-41.457-43.1h-.34c-14.986 0-27.449 6.396-35.12 18.036l13.779 9.452c5.73-8.695 14.724-10.548 21.348-10.548h.229c8.249.053 14.474 2.452 18.503 7.129 2.932 3.405 4.893 8.111 5.864 14.05-7.314-1.243-15.224-1.626-23.68-1.14-23.82 1.371-39.134 15.264-38.105 34.568.522 9.792 5.4 18.216 13.735 23.719 7.047 4.652 16.124 6.927 25.557 6.412 12.458-.683 22.231-5.436 29.049-14.127 5.178-6.6 8.453-15.153 9.899-25.93 5.937 3.583 10.337 8.298 12.767 13.966 4.132 9.635 4.373 25.468-8.546 38.376-11.319 11.308-24.925 16.2-45.488 16.351-22.809-.169-40.06-7.484-51.275-21.742C35.236 139.966 29.808 120.682 29.605 96c.203-24.682 5.63-43.966 16.133-57.317C56.954 24.425 74.204 17.11 97.013 16.94c22.975.17 40.526 7.52 52.171 21.847 5.71 7.026 10.015 15.86 12.853 26.162l16.147-4.308c-3.44-12.68-8.853-23.606-16.219-32.668C147.036 10.606 125.202 1.195 97.07 1L96.94 1C68.806 1.195 47.218 10.606 32.725 27.973 19.712 43.508 13.01 65.468 12.804 96v.027c.206 30.531 6.908 52.49 19.921 68.025C47.218 181.394 68.806 190.805 96.94 191h.129c24.765-.176 42.248-6.672 56.637-21.048 18.919-18.905 18.351-42.573 12.12-57.114-4.452-10.383-13.059-18.798-24.29-23.85ZM98.44 129.507c-10.44.588-21.286-4.098-21.82-14.135-.397-7.442 5.296-15.746 22.461-16.735 1.966-.113 3.895-.169 5.79-.169 6.235 0 12.068.606 17.37 1.765-1.978 24.702-13.754 28.713-23.8 29.274Z"/></svg>';
        var btns=[
          ['https://www.facebook.com/sharer/sharer.php?u='+u,'#1877f2','<i class="fab fa-facebook-f"></i> Facebook'],
          ['https://twitter.com/intent/tweet?url='+u+'&text='+t,'#000',X_SVG+' X'],
          ['https://line.me/R/msg/text/?'+t+'%0A'+u,'#06c755','<i class="fab fa-line"></i> LINE'],
          ['https://wa.me/?text='+t+'%20'+u,'#25d366','<i class="fab fa-whatsapp"></i> WhatsApp'],
          ['https://t.me/share/url?url='+u+'&text='+t,'#229ed9','<i class="fab fa-telegram-plane"></i> Telegram'],
          ['https://www.tiktok.com/share?url='+u,'#010101','<i class="fab fa-tiktok"></i> TikTok'],
          ['https://threads.net/intent/post?text='+t+'%20'+u,'#101010',T_SVG+' Threads'],
          ['{youtube_channel_url}','#ff0000','<i class="fab fa-youtube"></i> YouTube'],
        ];
        var c=document.getElementById('share-btns');
        btns.forEach(function(b){{
          var a=document.createElement('a');
          a.href=b[0];a.target='_blank';a.rel='noopener';
          a.style=BTN+'background:'+b[1]+';';
          a.innerHTML=b[2];c.appendChild(a);
        }});
        var btn=document.createElement('button');
        btn.style=BTN+'background:var(--primary,#1e40af);border:none;cursor:pointer;font-family:inherit;';
        btn.innerHTML='<i class="fas fa-link"></i> คัดลอกลิงก์';
        btn.onclick=function(){{navigator.clipboard.writeText(location.href).then(function(){{btn.innerHTML='<i class="fas fa-check"></i> คัดลอกแล้ว!';setTimeout(function(){{btn.innerHTML='<i class="fas fa-link"></i> คัดลอกลิงก์'}},2000)}});}};
        c.appendChild(btn);
      }})();
      </script>
    </div>
        <script type="application/ld+json">
    {{
      "@context":"https://schema.org",
      "@type":"Article",
      "headline":"{title}",
      "image":"{img_url}",
      "datePublished":"{date_iso}",
      "dateModified":"{date_iso}",
      "author":{{"@type":"Organization","name":"{site_name}"}},
      "publisher":{{"@type":"Organization","name":"{site_name}","url":"{site_url}"}}
    }}
    </script>
  </article>
  {sidebar}
</div>
{footer_html}
</body>
</html>"""


def _footer_html(year: int, site_name: str, site_url: str) -> str:
    """Footer ที่อ่านค่า social links และสีจาก SIDEBAR_CONFIG + THEME ใน config.py"""
    from config import SIDEBAR_CONFIG
    cfg = SIDEBAR_CONFIG
    # ── สีตรงกับ nav/hero (ดึงจาก CSS variable หรือ default) ──
    footer_bg = "#0f172a"   # ตรง theme dark ของ blue theme (default)
    link_style = "color:rgba(255,255,255,0.75);text-decoration:none;"
    social_items = []
    if cfg.get("facebook_url"):
        social_items.append(f'<a href="{cfg["facebook_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-facebook-f"></i> Facebook</a>')
    if cfg.get("youtube_url"):
        social_items.append(f'<a href="{cfg["youtube_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-youtube"></i> YouTube</a>')
    if cfg.get("tiktok_url"):
        social_items.append(f'<a href="{cfg["tiktok_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-tiktok"></i> TikTok</a>')
    if cfg.get("instagram_url"):
        social_items.append(f'<a href="{cfg["instagram_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-instagram"></i> Instagram</a>')
    social_html = "\n      ".join(social_items)
    return f"""<footer style="background:{footer_bg};color:rgba(255,255,255,0.85);text-align:center;padding:2rem 1rem 1.5rem;font-size:0.88rem;margin-top:2rem;">
  <div style="max-width:800px;margin:0 auto;">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0.5rem 1.2rem;margin-bottom:1rem;">
      <a href="index.html" style="{link_style}">🏠 หน้าแรก</a>
      <a href="contact.html" style="{link_style}">📬 ติดต่อเรา</a>
      <a href="privacy.html" style="{link_style}">🔒 นโยบายความเป็นส่วนตัว</a>
      <a href="sitemap.xml" style="{link_style}">🗺️ Sitemap</a>
      {social_html}
    </div>
    <p style="margin:0;color:rgba(255,255,255,0.5);font-size:0.82rem;">
      © {year} {site_name} · เว็บไซต์นี้ใช้ Google AdSense และลิงก์พันธมิตร (Affiliate) เพื่อสนับสนุนการดูแลเว็บไซต์
    </p>
  </div>
</footer>"""


def _sidebar_html() -> str:
    """Sidebar สนับสนุนเรา — อ่านจาก config.py (SIDEBAR_CONFIG)
    แก้ข้อมูลที่ config.py หรือ .env ที่เดียว ทุก agent อัปเดตพร้อมกัน"""
    return สร้าง_sidebar_html()


def บันทึกบทความ(หัวข้อ: str, หมวด: str, เนื้อหา: str) -> tuple:
    หมวดสะอาด = "".join(filter(str.isalnum, หมวด))
    timestamp  = int(time.time())
    ชื่อไฟล์   = f"{หมวดสะอาด}_{timestamp}.html"
    วันที่_th  = datetime.datetime.now().strftime("%d/%m/%Y")
    วันที่_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00")
    ปีนี้      = datetime.datetime.now().year
    desc       = f"{หัวข้อ} — {SITE_NAME} เว็บเดียวครบทุกเรื่อง"
    cat_page   = CATEGORY_PAGE_MAP.get(หมวด, "news.html")

    # ดึงรูป hero — ใช้ robust function (5 fallback)
    รูป_url = _ดึงรูป_ไม่ซ้ำ(หัวข้อ, หมวด, ชื่อไฟล์)

    # สร้าง SVG เป็น fallback เสมอ
    svg_fallback = สร้าง_thumbnail_svg(หัวข้อ, หมวด, ชื่อไฟล์)

    # รูปที่ใช้ใน og: และใน <img> tag
    og_img       = รูป_url if รูป_url.startswith("http") else f"{SITE_URL}/{รูป_url}"
    รูป_ใน_หน้า = รูป_url

    head = _head_html(
        f"{หัวข้อ} | {SITE_NAME}", desc, ชื่อไฟล์, og_img,
        cat=หมวด, cat_th=หมวด_ไทย.get(หมวด, หมวด), date_iso=วันที่_iso
    )
    # ดึง YouTube channel URL จาก SIDEBAR_CONFIG
    try:
        from config import SIDEBAR_CONFIG as _SC
        _yt_channel = _SC.get("youtube_url", "https://youtube.com")
    except Exception:
        _yt_channel = "https://youtube.com"

    html = ARTICLE_TEMPLATE.format(
        head=head, title=หัวข้อ, desc=desc,
        img_url=รูป_ใน_หน้า,
        img_fallback=svg_fallback or f"https://picsum.photos/seed/{hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]}/800/450",
        date_iso=วันที่_iso, date_th=วันที่_th,
        category_th=หมวด_ไทย.get(หมวด, หมวด),
        cat_page=cat_page,
        content=เนื้อหา, filename=ชื่อไฟล์,
        year=ปีนี้, site_name=SITE_NAME, site_url=SITE_URL,
        sidebar=_sidebar_html(),
        footer_html=_footer_html(ปีนี้, SITE_NAME, SITE_URL),
        youtube_channel_url=_yt_channel,
    )

    if not DRY_RUN:
        (BASE_PATH / ชื่อไฟล์).write_text(html, encoding="utf-8")
        log_ok(f"บันทึก: {ชื่อไฟล์} ({len(html):,} ตัว)")
    else:
        log_info(f"[DRY-RUN] จะบันทึก: {ชื่อไฟล์}")

    return ชื่อไฟล์, og_img


# ══════════════════════════════════════════════════════════════
# 🔍 เลือกหัวข้อ — RSS + Evergreen
# ══════════════════════════════════════════════════════════════
def ดึงหัวข้อที่มี() -> list:
    result = []
    for f in BASE_PATH.glob("*_*.html"):
        try:
            soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
            h1 = soup.find("h1")
            if h1:
                result.append(h1.get_text().strip())
        except Exception:
            pass
    return result


def เช็คซ้ำ(หัวข้อ: str, รายการที่มี: list) -> bool:
    if หัวข้อ in รายการที่มี:
        return True
    if not รายการที่มี:
        return False
    # FIX: ใช้ เรียก_ollama_เร็ว สำหรับงานเล็กๆ ประหยัดเวลา
    ผล = เรียก_ollama_เร็ว(
        f'หัวข้อใหม่: "{หัวข้อ}"\nหัวข้อที่มีอยู่:\n' +
        "\n".join(f"- {t}" for t in รายการที่มี[-20:]) +
        '\nตอบแค่: YES หรือ NO (YES=ซ้ำหรือคล้ายมาก)',
    ).upper()
    if not ผล:  # แก้บั๊ก 4: guard กรณี timeout คืนค่าว่าง
        return False
    return "YES" in ผล


EVERGREEN_POOL = [
    # ── สุขภาพ ────────────────────────────────────────────────
    "7 วิธีดูแลสุขภาพที่ทำได้ทุกวัน | health",
    "วิธีลดน้ำหนักอย่างปลอดภัยใน 3 เดือน | health",
    "อาการเตือนโรคร้ายที่ไม่ควรมองข้าม | health",
    "อาหารบำรุงสายตาที่ควรกินทุกวัน | health",
    "วิธีออกกำลังกายที่บ้านโดยไม่ต้องใช้อุปกรณ์ | health",
    "สัญญาณเตือนความเครียดสะสมที่ต้องรีบแก้ | health",
    # ── อาหาร / ทำครัว ────────────────────────────────────────
    "สูตรต้มยำกุ้งน้ำข้นต้นตำรับ | food",
    "วิธีทำผัดกะเพราหมูสับฉบับร้านอาหาร | cooking",
    "สูตรขนมหวานไทยที่ทำเองได้ง่ายๆ | cooking",
    "เมนูอาหารเช้าด้วยไข่ 10 แบบ | cooking",
    "วิธีทำชาไทยนมสดสูตรต้นตำรับ | cooking",
    "สูตรข้าวผัดไข่ให้อร่อยเหมือนร้าน | cooking",
    "เมนูอาหารลดน้ำหนักที่ทำเองได้ | food",
    # ── การเงิน ───────────────────────────────────────────────
    "เคล็ดลับออมเงินเดือนละ 5,000 | finance",
    "วิธีเริ่มลงทุนหุ้นสำหรับมือใหม่ | finance",
    "กองทุนรวม vs หุ้น ต่างกันอย่างไร | finance",
    "วิธีเพิ่มรายได้เสริมออนไลน์ในยุค AI | finance",
    "หนี้บัตรเครดิตปิดยังไงให้หมดเร็ว | finance",
    "ลงทุน crypto ความเสี่ยงที่ต้องรู้ก่อน | finance",
    # ── ท่องเที่ยว ────────────────────────────────────────────
    "ที่เที่ยวเชียงใหม่ 3 วัน 2 คืน งบน้อย | travel",
    "ที่เที่ยวภูเก็ตแบบไม่ต้องใช้ทัวร์ | travel",
    "ที่เที่ยวใกล้กรุงเทพไปเช้าเย็นกลับ | travel",
    "ที่เที่ยวญี่ปุ่นงบหมื่นเดียวไปได้ | travel",
    "คาเฟ่น่านั่งเชียงใหม่ 2025 | travel",
    "ของกินต้องลองในเยาวราช | travel",
    "แพ็คกระเป๋าเที่ยวทะเลให้ครบใน 5 นาที | travel",
    # ── ดูดวง / โชคลาภ ───────────────────────────────────────
    "ดูดวงรายเดือนธาตุไฟ — โอกาสและความรัก | horoscope",
    "เลขเด็ดจากฝัน วิธีตีความที่แม่นที่สุด | lottery",
    "หวยงวดนี้ เลขนำโชคตามวันเกิด | lottery",
    "สัตว์นำโชคตามปีเกิด มีผลจริงไหม | horoscope",
    "ดูดวงจีนปีนี้ 12 ปีนักษัตรเป็นอย่างไร | horoscope",
    "เลขมงคลตามวันเกิดที่เชื่อกันมานาน | horoscope",
    "ฮวงจุ้ยบ้านเพื่อดึงดูดโชคลาภ | horoscope",
    # ── เรื่องผี / ลึกลับ ─────────────────────────────────────
    "เรื่องผีสุดขนลุกที่เกิดขึ้นจริงในไทย | ghost",
    "สถานที่หลอนในไทยที่คนกลัวไปเยือน | ghost",
    "ประเพณีบวงสรวงที่คนไทยยังเชื่อถึงทุกวันนี้ | ghost",
    "วิญญาณ vs ปีศาจ ต่างกันอย่างไรในความเชื่อไทย | ghost",
    "เรื่องเล่าสยองในตำนานไทยโบราณ | ghost",
    "สถานที่ผีสิงในโรงเรียนที่นักเรียนเล่าต่อกัน | ghost",
    # ── บันเทิง ───────────────────────────────────────────────
    "10 ซีรีส์เกาหลีน่าดูในปี 2025 | entertainment",
    "อนิเมะน่าดูที่ไม่ควรพลาดในปีนี้ | anime",
    "หนังไทยที่ดีที่สุดตลอดกาล | movie",
    "ซีรีส์ Netflix ที่ดูแล้วหยุดไม่ได้ | entertainment",
    "ดาราไทยที่กำลังมาแรงในปี 2025 | entertainment",
    "เพลงไทยเพราะๆ ที่ควรฟังในปีนี้ | entertainment",
    # ── เทคโนโลยี / AI ────────────────────────────────────────
    "ChatGPT vs Gemini vs Claude ต่างกันยังไง | technology",
    "วิธีใช้ AI ช่วยทำงานให้ประหยัดเวลา | technology",
    "มือถือราคาหมื่นต้นที่คุ้มที่สุดในปี 2025 | technology",
    "วิธีสร้าง Passive Income จาก AI ในปีนี้ | technology",
    "แอปฟรีที่ต้องมีติดมือถือ 2025 | technology",
    # ── ความงาม ───────────────────────────────────────────────
    "ทำผมสวยที่บ้านไม่ต้องไปร้าน | beauty",
    "สกินแคร์เบื้องต้นสำหรับมือใหม่ | beauty",
    "ครีมกันแดดราคาถูกที่ดีที่สุดในไทย | beauty",
    "รูทีนดูแลผิวหน้าก่อนนอนที่ได้ผลจริง | beauty",
    # ── กีฬา ──────────────────────────────────────────────────
    "วิธีออกกำลังกายลดพุงใน 30 นาที | sport",
    "เทคนิคเตะบอลให้แม่นยำแบบมือโปร | sport",
    "โยคะสำหรับผู้เริ่มต้นทำที่บ้านได้เลย | sport",
    # ── การศึกษา ──────────────────────────────────────────────
    "วิธีเรียนภาษาอังกฤษด้วยตัวเองให้ได้ผลใน 6 เดือน | education",
    "วิธีสอนลูกให้รักการอ่านตั้งแต่เล็ก | education",
    "เทคนิคจำเนื้อหาสอบให้ติดทนนาน | education",
    # ── ไลฟ์สไตล์ ─────────────────────────────────────────────
    "แต่งบ้านสไตล์มินิมอลงบน้อย | lifestyle",
    "วิธีจัดระเบียบบ้านแบบ KonMari | lifestyle",
    "เคล็ดลับนอนหลับหลับได้เร็วคืนนี้เลย | lifestyle",
    "วิธีเลิกโทรศัพท์ก่อนนอนให้ได้จริง | lifestyle",
    # ── เกม / อนิเมะ ─────────────────────────────────────────
    "10 เกม PC ฟรีที่ดีที่สุด | gaming",
    "เกมมือถือน่าเล่นในปี 2025 ที่ไม่ต้องจ่ายเงิน | gaming",
    "อนิเมะ isekai น่าดู 2025 | anime",
    # ── สัตว์เลี้ยง ───────────────────────────────────────────
    "วิธีเลี้ยงแมวสำหรับมือใหม่ | pet",
    "อาหารที่สุนัขห้ามกินเด็ดขาด | pet",
    # ── DIY ───────────────────────────────────────────────────
    "DIY ของแต่งบ้านจากวัสดุเหลือใช้ | diy",
    "วิธีซ่อมก๊อกน้ำรั่วด้วยตัวเองไม่ต้องรอช่าง | diy",
    # ── รถยนต์ ────────────────────────────────────────────────
    "วิธีดูแลรถยนต์ด้วยตัวเองเบื้องต้น | car",
    "รถยนต์ไฟฟ้าราคาถูกที่น่าซื้อในไทย 2025 | car",
    # ── กฎหมาย / ธุรกิจ ──────────────────────────────────────
    "กฎหมายที่คนไทยควรรู้ทุกคน | law",
    "วิธีเริ่มต้นธุรกิจออนไลน์ด้วยทุนน้อย | business",
    # ── นิทาน / เรื่องเล่า / ตลก ─────────────────────────────
    "นิทานอีสปที่สอนใจและสรุปบทเรียนชีวิต | story",
    "เรื่องตลกขำขันที่เล่าในวงสนทนา | comedy",
    "10 มุกตลกที่คนไทยชอบที่สุด | comedy",
    "นิทานพื้นบ้านไทยที่เด็กๆ ควรรู้ | story",
    "เรื่องราวสร้างแรงบันดาลใจจากคนธรรมดา | story",
    # ── นิทานอีสป (Rewrite ภาษาไทยสมัยใหม่) ─────────────────
    "กระต่ายกับเต่า บทเรียนที่ยังใช้ได้ในยุคนี้ | story",
    "สิงโตกับหนู ความช่วยเหลือที่ยิ่งใหญ่ | story",
    "มดกับตั๊กแตน ทำไมต้องวางแผนล่วงหน้า | story",
    "อีกาผู้ฉลาด เรื่องราวของการแก้ปัญหา | story",
    "เด็กเลี้ยงแกะกับหมาป่า บทเรียนเรื่องความซื่อสัตย์ | story",
    "สุนัขจิ้งจอกกับองุ่น จิตใจที่ยอมรับความจริง | story",
    # ── ผีไทย / ตำนาน ────────────────────────────────────────
    "กระสือ ผีที่คนไทยกลัวมากที่สุดคืออะไร | ghost",
    "กระหัง ตำนานความเชื่อที่สืบทอดมาพันปี | ghost",
    "แม่นาคพระโขนง เรื่องจริงหรือตำนาน | ghost",
    "นางตานี ผีกล้วยที่คนไทยกลัวมาตลอด | ghost",
    "ผีปอบ ความเชื่อพื้นบ้านอีสานที่น่าสนใจ | ghost",
    # ── เรื่องเล่าสร้างแรงบันดาลใจ ───────────────────────────
    "หมู่บ้านที่ดวงดาวพูดได้ นิทานไทยสร้างสรรค์ | story",
    "เด็กชายกับมังกรแม่น้ำโขง นิทานพื้นบ้านสร้างใหม่ | story",
    "ตลาดผีกลางคืนริมแม่น้ำ เรื่องเล่าลึกลับ | ghost",
    # ── เคล็ดลับ ──────────────────────────────────────────────
    "เคล็ดลับประหยัดไฟฟ้าในบ้านที่ทำได้ทันที | tips",
    "เทคนิคถ่ายรูปสวยด้วยมือถือ | tips",
    "วิธีต่อรองราคาให้ได้ของถูกทุกครั้ง | tips",
    "เคล็ดลับล้างจานไวและสะอาดกว่าเดิม | tips",
    # ── นิทานพื้นบ้านไทย ─────────────────────────────────────
    "สังข์ทอง ตำนานความรักที่ยิ่งใหญ่ | folktale",
    "ไกรทอง นักสู้ผู้พิชิตจระเข้ยักษ์ | folktale",
    "พระอภัยมณีกับนางผีเสื้อสมุทร | folktale",
    "กาละแมสิงโต นิทานพื้นบ้านอีสาน | folktale",
    "เจ้าชายกบ ตำนานความรักข้ามชาติ | folktale",
    "นางสิบสอง เรื่องเล่าจากวรรณคดีไทย | folktale",
    # ── การ์ตูน ───────────────────────────────────────────────
    "หนูน้อยหมวกแดงฉบับใหม่สำหรับเด็กไทย | cartoon",
    "การ์ตูนสัตว์ป่าเรียนรู้การอยู่ร่วมกัน | cartoon",
    "ผจญภัยในโลกมหัศจรรย์ของเด็กชายดวงดาว | cartoon",
    "แมวน้อยกับปลาทอง เพื่อนต่างโลก | cartoon",
    # ── ละคร/ดราม่า ───────────────────────────────────────────
    "ชีวิตแม่ค้าตลาดนัดที่สู้ไม่ถอย | drama",
    "รักข้ามชนชั้นที่ทำให้ทุกอย่างเปลี่ยน | drama",
    "หญิงสาวกับความฝันที่ถูกขโมยไป | drama",
    "พ่อลูกกับสายสัมพันธ์ที่ขาดหาย | drama",
    # ── สร้างแรงบันดาลใจ ──────────────────────────────────────
    "จากศูนย์สู่ดาว เรื่องจริงของคนธรรมดา | inspirational",
    "เมื่อล้มเหลว 10 ครั้ง แต่ลุกขึ้น 11 ครั้ง | inspirational",
    "บทเรียนชีวิตจากคนที่ผ่านวิกฤตมาได้ | inspirational",
    "ความฝันเล็กๆ ที่เปลี่ยนชีวิตได้จริง | inspirational",
]


def ai_evergreen() -> str:
    หมวด = random.choice(CATEGORIES)
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)
    raw = เรียก_ollama(
        f'คิดหัวข้อบทความภาษาไทยหมวด "{หมวด_th}" 1 หัวข้อ\n'
        f'เงื่อนไข: คนไทยค้นหาตลอดกาล เฉพาะเจาะจง ไม่ซ้ำกับหัวข้อทั่วไป\n'
        f'ตอบรูปแบบ: หัวข้อ | {หมวด}',
        timeout=60
    )
    # กรอง <think>
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    for line in raw.split("\n"):
        line = line.strip()
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and len(parts[0]) > 5:
                h = parts[0].strip('"\'')
                m = parts[1].lower().strip()
                if m not in CATEGORIES:
                    m = หมวด
                return f"{h} | {m}"
    return random.choice(EVERGREEN_POOL)


RSS_ข่าว = [
    # ── ข่าวทั่วไปไทย ─────────────────────────────────────────
    ("ไทยรัฐ",       "https://www.thairath.co.th/rss/news.xml"),
    ("BBC Thai",    "https://feeds.bbci.co.uk/thai/rss.xml"),
    ("ข่าวสด",      "https://www.khaosod.co.th/feed"),
    # ── บันเทิงไทย / ดาราไทย ──────────────────────────────────
    ("Sanook บันเทิง",  "https://www.sanook.com/entertainment/feed/"),
    ("Kapook บันเทิง",  "https://entertain.kapook.com/feed/"),
    ("Manager บันเทิง", "https://mgronline.com/entertainment/rss"),
    # ── เทคโนโลยี ─────────────────────────────────────────────
    ("TechCrunch",  "https://techcrunch.com/feed/"),
    ("The Verge",   "https://www.theverge.com/rss/index.xml"),
    # ── อาหารและสุขภาพ ────────────────────────────────────────
    ("Healthline",  "https://www.healthline.com/rss/health-news"),
    # ── ท่องเที่ยว ────────────────────────────────────────────
    ("Lonely Planet","https://www.lonelyplanet.com/news/feed/rss/"),
    # ── บันเทิง ───────────────────────────────────────────────
    ("IGN",         "https://feeds.feedburner.com/ign/games-all"),
]

# RSS แยกตามหมวด — ดึงเฉพาะหมวดที่ต้องการ
RSS_BY_CATEGORY = {
    "news":          [("ไทยรัฐ","https://www.thairath.co.th/rss/news.xml"),
                      ("BBC Thai","https://feeds.bbci.co.uk/thai/rss.xml"),
                      ("ข่าวสด","https://www.khaosod.co.th/feed")],
    "technology":    [("TechCrunch","https://techcrunch.com/feed/"),
                      ("The Verge","https://www.theverge.com/rss/index.xml"),
                      ("Wired","https://www.wired.com/feed/rss")],
    "health":        [("Healthline","https://www.healthline.com/rss/health-news"),
                      ("WebMD","https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC")],
    "finance":       [("Forbes","https://www.forbes.com/investing/feed2/"),
                      ("CNBC","https://www.cnbc.com/id/10000664/device/rss/rss.html")],
    "travel":        [("Lonely Planet","https://www.lonelyplanet.com/news/feed/rss/"),
                      ("Travel + Leisure","https://www.travelandleisure.com/feeds/all.rss.xml")],
    "entertainment": [("Entertainment Weekly","https://ew.com/feed/"),
                      ("Variety","https://variety.com/feed/"),
                      ("Sanook บันเทิง","https://www.sanook.com/entertainment/feed/"),
                      ("Kapook บันเทิง","https://entertain.kapook.com/feed/"),
                      ("Manager บันเทิง","https://mgronline.com/entertainment/rss")],
    "gaming":        [("IGN","https://feeds.feedburner.com/ign/games-all"),
                      ("Kotaku","https://kotaku.com/rss")],
    "anime":         [("Anime News Network","https://www.animenewsnetwork.com/all/rss.xml")],
    "movie":         [("Variety Movies","https://variety.com/v/film/feed/"),
                      ("Roger Ebert","https://www.rogerebert.com/feed")],
    "sport":         [("ESPN","https://www.espn.com/espn/rss/news")],
    "beauty":        [("Allure","https://www.allure.com/feed/rss")],
}


def ดึงเทรนด์_rss(หมวด_เป้า: str = "") -> list:
    """ดึง RSS ตามหมวดที่ต้องการ ถ้าไม่ระบุดึงจากทุก feed สลับกัน"""
    result = []
    # ถ้าระบุหมวดและมี RSS เฉพาะ → ดึงตรงๆ
    if หมวด_เป้า and หมวด_เป้า in RSS_BY_CATEGORY:
        feeds = RSS_BY_CATEGORY[หมวด_เป้า]
    else:
        # สุ่มเลือก feeds 3 ชุดจากหมวดต่างๆ ป้องกัน bias
        all_feeds = []
        for cat, feeds_list in RSS_BY_CATEGORY.items():
            all_feeds.extend([(cat, f) for f in feeds_list])
        random.shuffle(all_feeds)
        feeds = [f for _, f in all_feeds[:6]]

    for ชื่อ, url in feeds:
        try:
            feed = feedparser.parse(url)
            items = [e.title for e in feed.entries[:3] if e.get("title","").strip()]
            result.extend(items)
            if items:
                log_ok(f"{ชื่อ}: {len(items)} หัวข้อ")
        except Exception as e:
            log_warn(f"{ชื่อ}: {e}")
    return result


def ดึง_google_trends_ไทย() -> list:
    """
    ดึง Google Trends Thailand รายวัน — ฟรี ไม่ต้อง API
    ใช้ RSS feed ของ Google Trends ที่เปิดให้ใช้งานสาธารณะ
    """
    ผล = []
    try:
        url = "https://trends.google.com/trending/rss?geo=TH"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=12)
        r.encoding = "utf-8"
        feed = feedparser.parse(r.text)
        for entry in feed.entries[:15]:
            title = entry.get("title", "").strip()
            if title and len(title) > 2:
                ผล.append(title)
        if ผล:
            log_ok(f"Google Trends TH: {len(ผล)} หัวข้อเทรนด์ → {', '.join(ผล[:5])}")
    except Exception as e:
        log_warn(f"Google Trends: {e}")
    return ผล


def เลือกหัวข้อ(หมวด_บังคับ: str = "") -> tuple:
    """คืน (หัวข้อ, หมวด) โดยกระจายหมวดอย่างสม่ำเสมอ"""

    # ถ้าระบุหมวด → ดึง RSS เฉพาะหมวดนั้น
    หมวด_target = หมวด_บังคับ if หมวด_บังคับ in CATEGORIES else ""

    # 15% Google Trends ไทย (ไวรัลเรียลไทม์), 35% RSS, 50% Evergreen
    rng = random.random()
    use_trends = rng < 0.15 and not หมวด_target
    use_rss    = rng < 0.50

    if use_trends:
        เทรนด์ = ดึง_google_trends_ไทย()
        if เทรนด์:
            target_cat = random.choice(CATEGORIES)
            raw = เรียก_ollama(
                f'หัวข้อกำลังเป็นกระแสในไทยตอนนี้: {", ".join(เทรนด์[:8])}\n'
                f'เลือก 1 หัวข้อและดัดแปลงเป็นบทความภาษาไทยที่คนอยากอ่าน\n'
                f'หมวด: {หมวด_ไทย.get(target_cat, target_cat)}\n'
                f'ตอบรูปแบบ: หัวข้อภาษาไทย | {target_cat}',
                timeout=90
            )
            raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
            for line in raw.split("\n"):
                line = line.strip()
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2 and len(parts[0]) > 5:
                        หมวด = parts[1].lower().strip()
                        if หมวด not in CATEGORIES:
                            หมวด = target_cat
                        return parts[0], หมวด

    if use_rss:
        เทรนด์ = ดึงเทรนด์_rss(หมวด_target)
        if เทรนด์:
            # สุ่มเลือกหมวดเป้าหมายก่อน ป้องกัน bias ข่าว
            target_cat = หมวด_target or random.choice(CATEGORIES)
            raw = เรียก_ollama(
                f'จากหัวข้อเหล่านี้: {", ".join(เทรนด์[:6])}\n'
                f'เลือกหรือดัดแปลง 1 หัวข้อให้เป็นบทความภาษาไทยที่น่าสนใจ\n'
                f'หมวดที่ต้องการ: {หมวด_ไทย.get(target_cat, target_cat)}\n'
                f'ตอบรูปแบบ: หัวข้อภาษาไทย | {target_cat}',
                timeout=90
            )
            raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
            for line in raw.split("\n"):
                line = line.strip()
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2 and len(parts[0]) > 5:
                        หมวด = parts[1].lower().strip()
                        if หมวด not in CATEGORIES:
                            หมวด = target_cat or random.choice(CATEGORIES)
                        return parts[0], หมวด

    # Evergreen Pool — กระจายทุกหมวด
    # กรองตามหมวดที่ต้องการ หรือสุ่มทั้งหมด
    if หมวด_target:
        pool = [x for x in EVERGREEN_POOL if x.endswith(f"| {หมวด_target}")]
        if not pool:
            pool = EVERGREEN_POOL
    else:
        pool = EVERGREEN_POOL

    # ให้ AI สร้างหัวข้อใหม่จากหมวดที่สุ่มมา (หรือหมวดที่กำหนด)
    target_cat = หมวด_target or random.choice(CATEGORIES)
    if random.random() < 0.6:  # 60% ให้ AI คิดเอง ไม่ซ้ำ Pool
        raw = ai_evergreen_by_cat(target_cat)
        if raw:
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) >= 2 and parts[0]:
                หมวด = parts[1].lower().strip()
                if หมวด not in CATEGORIES:
                    หมวด = target_cat
                return parts[0], หมวด

    # Fallback: สุ่มจาก Pool
    raw = random.choice(pool)
    parts = [p.strip() for p in raw.split("|")]
    return parts[0], (parts[1] if len(parts) > 1 and parts[1] in CATEGORIES else target_cat)


def ai_evergreen_by_cat(หมวด: str) -> str:
    """ให้ AI คิดหัวข้อ Evergreen สำหรับหมวดที่กำหนด"""
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)

    # hint พิเศษสำหรับหมวดที่ AI มักเขียนไม่ถนัด
    HINTS = {
        "ghost":     "เรื่องผี ตำนาน ความเชื่อ สถานที่หลอน ประเพณีไทย",
        "lottery":   "หวย เลขเด็ด ฝัน ตีเลข โชคลาภ",
        "horoscope": "ดูดวง ราศี ปีนักษัตร ฮวงจุ้ย เลขมงคล",
        "cooking":   "สูตรอาหาร วิธีทำกับข้าว เมนูง่าย วัตถุดิบ เคล็ดลับทำครัว",
        "comedy":    "มุกตลก เรื่องฮา ขำขัน สถานการณ์ตลก",
        "story":     "นิทาน เรื่องเล่า ตำนาน บทเรียนชีวิต แรงบันดาลใจ",
        "tips":      "เคล็ดลับ วิธีง่ายๆ ทริค ลัดขั้นตอน ประหยัดเวลา",
        "travel":    "ที่เที่ยว ร้านอาหาร คาเฟ่ โรงแรม งบน้อย",
    }
    hint = HINTS.get(หมวด, "")
    raw = เรียก_ollama(
        f'คิดหัวข้อบทความภาษาไทยหมวด "{หมวด_th}" 1 หัวข้อ\n'
        f'{("ตัวอย่างเนื้อหาในหมวดนี้: " + hint) if hint else ""}\n'
        f'เงื่อนไข: เฉพาะเจาะจง ค้นหาได้บน Google คนไทยสนใจจริง\n'
        f'ตอบรูปแบบ: หัวข้อ | {หมวด}',
        timeout=60
    )
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    for line in raw.split("\n"):
        line = line.strip()
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and len(parts[0]) > 5:
                h = parts[0].strip('"\'')
                return f"{h} | {หมวด}"
    return ""


# ══════════════════════════════════════════════════════════════
# 🔗 Internal Links + อัปเดตหน้าหมวด
# ══════════════════════════════════════════════════════════════
def ใส่_internal_links(ชื่อไฟล์: str, หมวด: str):
    filepath = BASE_PATH / ชื่อไฟล์
    if not filepath.exists():
        return
    html = filepath.read_text(encoding="utf-8")
    MARKER_START = "<!-- related-articles-block -->"
    MARKER_END   = "<!-- /related-articles-block -->"

    # แก้บั๊ก 2: เช็คทั้ง MARKER และ keyword ป้องกันซ้ำ
    if MARKER_START in html or "บทความที่เกี่ยวข้อง" in html:
        return
    หมวดสะอาด = "".join(filter(str.isalnum, หมวด.lower()))  # FIX: ประกาศก่อนใช้
    ไฟล์ = sorted(
        BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
        key=lambda f: f.stat().st_mtime, reverse=True
    )
    related = []
    for af in ไฟล์[:8]:
        if af.name == ชื่อไฟล์:
            continue
        try:
            soup = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1   = soup.find("h1")
            if h1:
                related.append((af.name, h1.get_text().strip()))
        except Exception:
            pass
        if len(related) >= 5:
            break

    if not related:
        return

    MARKER_START = "<!-- related-articles-block -->"
    MARKER_END   = "<!-- /related-articles-block -->"
    cards = "".join(
        f'<a href="{fn}" style="display:flex;align-items:center;gap:0.75rem;'
        f'padding:0.65rem 1rem;margin-bottom:0.4rem;background:var(--soft,#f1f5f9);'
        f'border-radius:8px;color:inherit;text-decoration:none;'
        f'border-left:3px solid var(--primary,#1e40af);font-size:0.92rem;">'
        f'<i class="fas fa-arrow-right" style="color:var(--primary,#1e40af);'
        f'font-size:0.75rem;flex-shrink:0;"></i>'
        f'<span>{title}</span></a>'
        for fn, title in related
    )
    block = (
        "\n" + MARKER_START +
        '\n<div style="margin-top:2rem;padding:1.2rem;background:var(--soft,#f1f5f9);border-radius:12px;">'
        '\n<h3 style="color:var(--primary,#1e40af);margin:0 0 0.85rem;font-size:1rem;">'
        '<i class="fas fa-link"></i> บทความที่เกี่ยวข้อง</h3>'
        + cards + "\n</div>\n" + MARKER_END
    )

    if "</article>" in html:
        html = html.replace("</article>", block + "\n</article>", 1)
    elif "</main>" in html:
        html = html.replace("</main>", block + "\n</main>", 1)

    if not DRY_RUN:
        filepath.write_text(html, encoding="utf-8")
        log_ok(f"Internal links ({len(related)}) → {ชื่อไฟล์}")


def อัปเดตหน้าหลัก():
    """อัปเดต index.html ให้แสดงบทความล่าสุดจากทุกหมวด (grid 3 คอลัมน์)"""
    path = BASE_PATH / "index.html"
    if not path.exists():
        log_warn("อัปเดตหน้าหลัก: ไม่พบ index.html")
        return

    # ดึงบทความล่าสุดทุกหมวด รวมกัน max 24 บทความ
    ไฟล์ทั้งหมด = []
    for หมวด in CATEGORIES:
        หมวดสะอาด = "".join(filter(str.isalnum, หมวด.lower()))
        for af in sorted(BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
                         key=lambda f: f.stat().st_mtime, reverse=True)[:6]:
            if af.exists() and af.stat().st_size > 100:
                ไฟล์ทั้งหมด.append(af)

    # เรียงตาม mtime ล่าสุด
    ไฟล์ทั้งหมด.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    ไฟล์ทั้งหมด = ไฟล์ทั้งหมด[:24]

    if not ไฟล์ทั้งหมด:
        log_warn("อัปเดตหน้าหลัก: ยังไม่มีบทความ")
        return

    การ์ด = ""
    for af in ไฟล์ทั้งหมด:
        try:
            soup   = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1     = soup.find("h1")
            หัวข้อ = h1.get_text().strip() if h1 else af.stem
            หมวด_af = af.stem.split("_")[0]
            หมวด_th = หมวด_ไทย.get(หมวด_af, หมวด_af)

            img_src = ""
            hero_wrap = soup.find(class_="hero-image-wrapper")
            if hero_wrap:
                hero_img = hero_wrap.find("img")
                if hero_img:
                    s = hero_img.get("src", "").strip()
                    if s and "icon" not in s.lower():
                        img_src = s
            if not img_src:
                og = soup.find("meta", property="og:image")
                if og and og.get("content", "").startswith("http"):
                    img_src = og["content"].strip()
            if not img_src:
                body_el = soup.find(class_="article-body")
                for img in (body_el or soup).find_all("img"):
                    s = img.get("src", "").strip()
                    if s and not s.endswith(".gif") and "icon" not in s.lower():
                        img_src = s; break
            if not img_src:
                seed = hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]
                img_src = f"https://picsum.photos/seed/{seed}/800/450"

            svg_fb = f"images/thumbs/{af.stem}.svg"
            onerror = f'onerror="this.onerror=null;this.src=\'{svg_fb}\'"'

            meta = soup.find(class_="article-meta")
            วันที่ = ""
            if meta:
                t = meta.get_text()
                if "วันที่:" in t:
                    วันที่ = t.split("วันที่:")[-1].split("|")[0].strip()
        except Exception:
            หัวข้อ = af.stem; import hashlib as _hl; img_src = f"https://picsum.photos/seed/{_hl.md5(af.stem.encode()).hexdigest()[:8]}/800/450"
            svg_fb = ""; onerror = ""; วันที่ = ""; หมวด_th = ""

        date_html = (f'<div style="font-size:.72rem;color:var(--muted,#64748b);margin:.3rem 0;">'
                     f'<i class="far fa-calendar-alt"></i> {วันที่}</div>') if วันที่ else ""
        badge_html = (f'<div class="cat-badge" style="background:var(--primary,#1e40af);color:#fff;'
                      f'font-size:.7rem;padding:2px 8px;border-radius:999px;display:inline-block;margin-bottom:.3rem;">'
                      f'{หมวด_th}</div>') if หมวด_th else ""
        การ์ด += (
            f'<a href="{af.name}" style="display:flex;flex-direction:column;background:var(--card,#fff);'
            f'border-radius:12px;overflow:hidden;border:1px solid var(--border,#e2e8f0);'
            f'text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s;"'
            f' onmouseover="this.style.transform=\'translateY(-3px)\';this.style.boxShadow=\'0 8px 24px rgba(0,0,0,.12)\'"'
            f' onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'">'
            f'<img src="{img_src}" alt="{หัวข้อ}" loading="lazy" {onerror}'
            f' style="width:100%;height:180px;object-fit:cover;">'
            f'<div style="padding:.9rem;flex:1;">'
            f'{badge_html}{date_html}'
            f'<h3 style="margin:0;font-size:.93rem;line-height:1.45;font-weight:700;'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{หัวข้อ}</h3>'
            f'</div></a>'
        )

    IDX_S = "<!-- INDEX_ARTICLES_START -->"
    IDX_E = "<!-- INDEX_ARTICLES_END -->"
    block = (
        f'\n{IDX_S}\n'
        f'<div class="article-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem;">'
        f'\n{การ์ด}\n</div>\n{IDX_E}\n'
    )

    html = path.read_text(encoding="utf-8")

    # ลบ block เก่า (ทั้ง marker ใหม่ และ embedded-articles-list)
    for _s, _e in [
        ("<!-- INDEX_ARTICLES_START -->", "<!-- INDEX_ARTICLES_END -->"),
        ("<!-- ARTICLE_LIST_START -->", "<!-- ARTICLE_LIST_END -->"),
        ("<!-- article-list -->", "<!-- /article-list -->"),
    ]:
        for _ in range(5):
            new = re.sub(re.escape(_s)+r".*?"+re.escape(_e), "", html, flags=re.DOTALL)
            if new == html: break
            html = new

    # แทนที่ placeholder "กำลังโหลดบทความ" ถ้ายังมีอยู่
    html = re.sub(
        r'<div[^>]*id="embedded-articles-list"[^>]*>.*?</div>',
        block, html, flags=re.DOTALL
    )

    # ถ้าไม่มี placeholder → แทรกหลัง <main>
    if IDX_S not in html:
        if "<main>" in html:
            html = html.replace("<main>", f"<main>\n{block}", 1)
        elif "</main>" in html:
            # แทรกก่อน </main>
            idx = html.rfind("</main>")
            html = html[:idx] + block + html[idx:]

    if not DRY_RUN:
        path.write_text(html, encoding="utf-8")
        log_ok(f"อัปเดต index.html — {len(ไฟล์ทั้งหมด)} บทความ")

def อัปเดตหน้าหมวด(หมวด: str, ชื่อไฟล์ใหม่: str = "", หัวข้อ_ใหม่: str = ""):
    # BUG FIX: lowercase เสมอก่อน lookup
    หมวด_lower = หมวด.lower().strip()
    ไฟล์หมวด = CATEGORY_PAGE_MAP.get(หมวด_lower, "news.html")
    path = BASE_PATH / ไฟล์หมวด
    if not path.exists():
        log_warn(f"อัปเดตหน้าหมวด: ไม่พบ {ไฟล์หมวด}")
        return

    # BUG FIX: ตรวจว่าไฟล์ใหม่บันทึกแล้วจริงก่อน glob
    if ชื่อไฟล์ใหม่ and not (BASE_PATH / ชื่อไฟล์ใหม่).exists():
        log_warn(f"อัปเดตหน้าหมวด: ยังไม่พบไฟล์ใหม่ {ชื่อไฟล์ใหม่} — รอ 1 วินาที")
        time.sleep(1)

    หมวดสะอาด = "".join(filter(str.isalnum, หมวด_lower))
    ไฟล์บทความ = sorted(
        BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
        key=lambda f: f.stat().st_mtime, reverse=True
    )
    if not ไฟล์บทความ:
        log_warn(f"อัปเดตหน้าหมวด: ไม่มีบทความใน {หมวด_lower}")
        return

    # BUG FIX: กรองเฉพาะไฟล์ที่มีอยู่จริง ป้องกัน card ชี้ไปไฟล์เก่า/ค้าง
    ไฟล์บทความ = [f for f in ไฟล์บทความ if f.exists() and f.stat().st_size > 100]
    if not ไฟล์บทความ:
        log_warn(f"อัปเดตหน้าหมวด: ไม่มีบทความที่ valid ใน {หมวด_lower}")
        return

    การ์ด = ""
    for af in ไฟล์บทความ[:24]:
        try:
            soup   = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1     = soup.find("h1")
            หัวข้อ = h1.get_text().strip() if h1 else af.stem

            # ดึงรูป: hero-image-wrapper ก่อน → article-body → og:image → picsum
            img_src = ""
            hero_wrap = soup.find(class_="hero-image-wrapper")
            if hero_wrap:
                hero_img = hero_wrap.find("img")
                if hero_img:
                    s = hero_img.get("src", "").strip()
                    if s and "icon" not in s.lower():
                        img_src = s
            if not img_src:
                og = soup.find("meta", property="og:image")
                if og and og.get("content","").startswith("http"):
                    img_src = og["content"].strip()
            if not img_src:
                body_el = soup.find(class_="article-body")
                search_in = body_el if body_el else soup
                for img in search_in.find_all("img"):
                    s = img.get("src", "").strip()
                    if s and not s.endswith(".gif") and "icon" not in s.lower():
                        img_src = s
                        break
            # SVG local เป็น fallback สุดท้าย (ไม่ใช้เป็น primary)
            if not img_src:
                svg_local = f"images/thumbs/{af.stem}.svg"
                if (BASE_PATH / svg_local).exists():
                    img_src = svg_local
            if not img_src:
                seed = hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]
                img_src = f"https://picsum.photos/seed/{seed}/800/450"

            svg_fb = f"images/thumbs/{af.stem}.svg"
            meta = soup.find(class_="article-meta")
            วันที่ = ""
            if meta:
                t = meta.get_text()
                if "วันที่:" in t:
                    วันที่ = t.split("วันที่:")[-1].split("|")[0].strip()
        except Exception:
            หัวข้อ = af.stem
            import hashlib as _hl; img_src = f"https://picsum.photos/seed/{_hl.md5(af.stem.encode()).hexdigest()[:8]}/800/450"
            svg_fb = ""
            วันที่ = ""

        onerror = f'onerror="this.onerror=null;this.src=\'{svg_fb}\'"' if svg_fb else ""
        date_html = (f'<div style="font-size:0.72rem;color:var(--muted,#64748b);margin-bottom:0.3rem;">'
                     f'<i class="far fa-calendar-alt"></i> {วันที่}</div>') if วันที่ else ""
        การ์ด += f"""
  <a href="{af.name}" style="display:flex;gap:1rem;align-items:flex-start;padding:0.85rem;
     background:var(--card,#fff);border-radius:10px;margin-bottom:0.6rem;text-decoration:none;
     color:inherit;border:1px solid var(--border,#e2e8f0);transition:box-shadow 0.2s;"
     onmouseover="this.style.boxShadow='0 2px 12px rgba(0,0,0,.08)'"
     onmouseout="this.style.boxShadow='none'">
    <img src="{img_src}" alt="{หัวข้อ}"
         style="width:140px;height:95px;object-fit:cover;border-radius:8px;flex-shrink:0;"
         loading="lazy" {onerror}>
    <div style="flex:1;min-width:0;">
      {date_html}
      <h3 style="margin:0;font-size:0.95rem;line-height:1.45;font-weight:600;
         overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{หัวข้อ}</h3>
    </div>
    <i class="fas fa-chevron-right" style="color:var(--muted,#64748b);font-size:0.75rem;flex-shrink:0;margin-top:0.3rem;"></i>
  </a>"""

    # ใช้ marker เดียวกับ agent_fix_v4.py เพื่อป้องกัน block ซ้อน
    ART_S_W = "<!-- ARTICLE_LIST_START -->"
    ART_E_W = "<!-- ARTICLE_LIST_END -->"
    ส่วนบทความ = (
        f"\n{ART_S_W}\n"
        f'<div style="background:var(--card,#fff);border-radius:16px;padding:1.25rem;'
        f'box-shadow:0 4px 12px rgba(30,64,175,0.06);margin-top:1rem;">'
        f'\n<h2 style="color:var(--primary,#1e40af);font-size:1.1rem;margin:0 0 1rem;">'
        f'\n  <i class="fas fa-list-ul"></i> บทความล่าสุด ({len(ไฟล์บทความ)} บทความ)'
        f'\n</h2>'
        f'\n{การ์ด}\n</div>'
        f"\n{ART_E_W}\n"
    )

    html = path.read_text(encoding="utf-8")
    # ลบ block เก่าทุกรูปแบบก่อน (ทั้ง marker เก่าและใหม่)
    for _s, _e in [
        ("<!-- ARTICLE_LIST_START -->", "<!-- ARTICLE_LIST_END -->"),
        ("<!-- article-list -->", "<!-- /article-list -->"),
        ("<!-- ARTICLES_START -->", "<!-- ARTICLES_END -->"),
        ("<!-- posts-grid-start -->", "<!-- posts-grid-end -->"),
    ]:
        for _ in range(10):
            new_html = re.sub(re.escape(_s)+r".*?"+re.escape(_e), "", html, flags=re.DOTALL)
            if new_html == html: break
            html = new_html

    if "</main>" in html:
        html = html.replace("</main>", ส่วนบทความ + "\n</main>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", ส่วนบทความ + "\n</body>", 1)
    else:
        html += "\n" + ส่วนบทความ

    if not DRY_RUN:
        path.write_text(html, encoding="utf-8")
        log_ok(f"อัปเดตหน้าหมวด: {ไฟล์หมวด}")


# ══════════════════════════════════════════════════════════════
# 📱 Social Push
# ══════════════════════════════════════════════════════════════
def โพส_facebook(หัวข้อ: str, url: str, รูป: str, หมวด: str):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        log_warn("ไม่มี Facebook token — ข้าม")
        return
    emoji = {"food":"🍜","health":"💚","finance":"💰","travel":"✈️",
             "anime":"🎌","gaming":"🎮","beauty":"💄"}.get(หมวด,"📰")
    try:
        r = requests.post(
            f"https://graph.facebook.com/{FB_PAGE_ID}/feed",
            data={"message": f"{emoji} {หัวข้อ}\n\n{url}",
                  "link": url, "access_token": FB_ACCESS_TOKEN},
            timeout=15
        )
        if r.status_code == 200:
            log_ok("โพส Facebook สำเร็จ!")
        else:
            log_warn(f"Facebook: {r.status_code} — {r.text[:100]}")
    except Exception as e:
        log_err(f"Facebook: {e}")


def โพส_line(หัวข้อ: str, url: str, หมวด: str):
    if not LINE_NOTIFY_TOKEN:
        return
    emoji = {"food":"🍜","health":"💚","finance":"💰"}.get(หมวด,"📰")
    try:
        r = requests.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
            data={"message": f"\n{emoji} {หัวข้อ}\n🔗 {url}"},
            timeout=15
        )
        if r.status_code == 200:
            log_ok("Line Notify สำเร็จ!")
    except Exception as e:
        log_err(f"Line Notify: {e}")


# ══════════════════════════════════════════════════════════════
# 🚀 Main
# ══════════════════════════════════════════════════════════════
def _บันทึกและอัปเดต(หัวข้อ: str, หมวด: str, เนื้อหา: str) -> tuple:
    """บันทึกบทความและอัปเดต links+หน้าหมวด+หน้าหลัก — ใช้ร่วมกัน"""
    ชื่อไฟล์, รูป = บันทึกบทความ(หัวข้อ, หมวด, เนื้อหา)
    ใส่_internal_links(ชื่อไฟล์, หมวด)
    อัปเดตหน้าหมวด(หมวด, ชื่อไฟล์, หัวข้อ)
    อัปเดตหน้าหลัก()   # ← FIX: อัปเดต index.html ด้วยทุกครั้ง
    article_url = f"{SITE_URL}/{ชื่อไฟล์}"
    โพส_facebook(หัวข้อ, article_url, รูป, หมวด)
    โพส_line(หัวข้อ, article_url, หมวด)
    return ชื่อไฟล์, รูป



def _progress_bar(done: int, total: int, width: int = 10) -> str:
    """แถบ progress unicode"""
    total = max(total, 1)  # ป้องกัน ZeroDivisionError
    filled = min(int(width * done / total), width)
    bar = "█" * filled + "░" * (width - filled)
    pct = min(int(100 * done / total), 100)
    return f"[{bar}] {pct}%"


def main():
    log_section("🤖 Agent Writer v5 — เริ่ม Pipeline")

    # แสดงสถานะ API keys
    if PEXELS_KEY:
        log_ok("Pexels API พร้อม ✅")
    else:
        log_warn("ไม่พบ PEXELS_KEY ใน .env — รูปจะใช้ Unsplash/Picsum แทน")
    if UNSPLASH_KEY:
        log_ok("Unsplash API พร้อม ✅")
    else:
        log_warn("ไม่พบ UNSPLASH_KEY ใน .env")

    หัวข้อ     = ""
    หมวด_force = ""   # --cat ระบุหมวดบังคับ
    url_target = ""
    args       = sys.argv[1:]

    # ── รับ arguments ─────────────────────────────────────────
    if "--topic" in args:
        idx = args.index("--topic")
        if idx + 1 < len(args):
            หัวข้อ = args[idx + 1]

    if "--url" in args:
        idx = args.index("--url")
        if idx + 1 < len(args):
            url_target = args[idx + 1]

    if "--cat" in args:
        idx = args.index("--cat")
        if idx + 1 < len(args):
            หมวด_force = args[idx + 1].lower().strip()
            if หมวด_force not in CATEGORIES:
                log_warn(f"หมวด '{หมวด_force}' ไม่พบ — ใช้อัตโนมัติ")
                หมวด_force = ""

    # จำนวนบทความ (--count N)
    จำนวน = 1
    if "--count" in args:
        idx = args.index("--count")
        if idx + 1 < len(args):
            try:
                จำนวน = max(1, min(50, int(args[idx + 1])))
            except ValueError:
                log_warn("--count ต้องเป็นตัวเลข — ใช้ค่า 1")

    # ── Helper ─────────────────────────────────────────────────
    def _pick(hint: str = "") -> tuple:
        """เลือกหัวข้อ+หมวด พร้อม override จาก --cat"""
        if hint:
            raw = เรียก_ollama_เร็ว(
                f'หัวข้อ: "{hint}"\nหมวดจาก: {", ".join(CATEGORIES)}\nตอบแค่ชื่อหมวดภาษาอังกฤษ 1 คำ'
            ).lower().strip()
            m = raw if raw in CATEGORIES else "lifestyle"
            return hint, (หมวด_force or m)
        h, m = เลือกหัวข้อ(หมวด_force)   # ← ส่ง หมวด_force เข้าไปด้วย
        return h, m

    # ══════════════════════════════════════════════════════════
    # MODE: --cluster [--count N]
    # ══════════════════════════════════════════════════════════
    if "--cluster" in args:
        cluster_n = จำนวน if "--count" in args else 4
        log_section(f"🏗️ Cluster Mode — สร้าง {cluster_n} บทความเชื่อมกัน")

        หัวข้อ_หลัก, หมวด = _pick(หัวข้อ)
        if not หัวข้อ_หลัก:
            log_err("ไม่ได้หัวข้อ — หยุด")
            return

        log(f"📝 หัวข้อหลัก: {หัวข้อ_หลัก} | หมวด: {หมวด} | เป้า: {cluster_n} บทความ")
        บทความทั้งหมด = []
        เวลาเริ่ม = time.time()

        # บทความหลัก
        log(f"\n{_progress_bar(0, cluster_n)} [1/{cluster_n}] บทความหลัก")
        log_info(f"📄 เขียน: {หัวข้อ_หลัก}")
        เนื้อหา = เขียนบทความ(หัวข้อ_หลัก, หมวด)
        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_หลัก, หมวด, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_หลัก, ชื่อไฟล์, รูป))
            log_ok(f"✅ {ชื่อไฟล์}")

        # คิดหัวข้อย่อย
        ต้องการย่อย = cluster_n - 1
        หัวข้อย่อย = ai_คิดหัวข้อย่อย(หัวข้อ_หลัก, หมวด)
        while len(หัวข้อย่อย) < ต้องการย่อย:
            extra = ai_คิดหัวข้อย่อย(f"{หัวข้อ_หลัก} (มุมมองใหม่)", หมวด)
            existing = set(หัวข้อย่อย)
            for h in extra:
                if h not in existing:
                    หัวข้อย่อย.append(h)
                    existing.add(h)
            if not extra:
                break

        log_ok(f"หัวข้อย่อย: {หัวข้อย่อย[:ต้องการย่อย]}")

        for i, หัวข้อ_ย่อย in enumerate(หัวข้อย่อย[:ต้องการย่อย]):
            seq = i + 2
            log(f"\n{_progress_bar(seq-1, cluster_n)} [{seq}/{cluster_n}] บทความย่อย {i+1}")
            log_info(f"📄 เขียน: {หัวข้อ_ย่อย}")
            เนื้อหา = เขียนบทความ(หัวข้อ_ย่อย, หมวด)
            if เนื้อหา:
                ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ย่อย, หมวด, เนื้อหา)
                บทความทั้งหมด.append((หัวข้อ_ย่อย, ชื่อไฟล์, รูป))
                log_ok(f"✅ {ชื่อไฟล์}")
            else:
                log_warn(f"บทความย่อย {i+1} ล้มเหลว — ข้าม")
            time.sleep(1)

        ใช้เวลา = int(time.time() - เวลาเริ่ม)
        log_section(
            f"🎊 Cluster เสร็จ! {len(บทความทั้งหมด)}/{cluster_n} บทความ"
            f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
        )
        for h, f, _ in บทความทั้งหมด:
            log(f"   📄 {f} — {h}")
        if not DRY_RUN:
            log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")
        return

    # ══════════════════════════════════════════════════════════
    # MODE: --batch N  (ต่างจาก --count ตรงที่เลือกหัวข้อต่างกันทุกรอบ)
    # ══════════════════════════════════════════════════════════
    if "--batch" in args:
        bidx = args.index("--batch")
        batch_n = 5
        if bidx + 1 < len(args) and args[bidx + 1].isdigit():
            batch_n = max(1, min(50, int(args[bidx + 1])))

        log_section(f"📦 Batch Mode — สร้าง {batch_n} บทความ (หัวข้อต่างกันทุกครั้ง)")
        if หมวด_force:
            log_info(f"หมวดบังคับ: {หมวด_force} ({หมวด_ไทย.get(หมวด_force, หมวด_force)})")

        บทความทั้งหมด = []
        เวลาเริ่ม     = time.time()
        รายการที่มี   = ดึงหัวข้อที่มี()
        ล้มเหลวติดกัน = 0
        MAX_FAIL = 5   # เพิ่มจาก 3 → 5 ลด false stop
        MAX_ITER = batch_n * 4  # ป้องกัน infinite loop

        _iter = 0
        while len(บทความทั้งหมด) < batch_n and _iter < MAX_ITER:
            _iter += 1
            log(f"\n{_progress_bar(len(บทความทั้งหมด), batch_n)} [{len(บทความทั้งหมด)+1}/{batch_n}]")
            h, m = _pick()
            if not h:
                log_err("เลือกหัวข้อไม่ได้ — หยุด")
                break
            if เช็คซ้ำ(h, รายการที่มี):
                log_warn(f"ซ้ำ: {h[:45]}... — ข้าม")
                ล้มเหลวติดกัน += 1
                if ล้มเหลวติดกัน >= MAX_FAIL:
                    log_warn(f"ซ้ำ {MAX_FAIL} ครั้งติดกัน — หยุด")
                    break
                continue
            log_info(f"📄 {h} [{หมวด_ไทย.get(m, m)}]")
            เนื้อหา = เขียนบทความ(h, m)
            if เนื้อหา:
                ชื่อไฟล์, รูป = _บันทึกและอัปเดต(h, m, เนื้อหา)
                บทความทั้งหมด.append((h, ชื่อไฟล์, รูป))
                รายการที่มี.append(h)
                log_ok(f"✅ {ชื่อไฟล์}")
                ล้มเหลวติดกัน = 0
                time.sleep(2)
            else:
                log_warn(f"เขียนไม่ได้: {h[:45]}")
                ล้มเหลวติดกัน += 1
                if ล้มเหลวติดกัน >= MAX_FAIL:
                    log_err(f"ล้มเหลว {MAX_FAIL} ครั้งติดกัน — ตรวจ Ollama")
                    break

        ใช้เวลา = int(time.time() - เวลาเริ่ม)
        log_section(
            f"🎊 Batch เสร็จ! {len(บทความทั้งหมด)}/{batch_n} บทความ"
            f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
        )
        for h, f, _ in บทความทั้งหมด:
            log(f"   📄 {f} — {h}")
        if not DRY_RUN and บทความทั้งหมด:
            log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")
        return

    # ══════════════════════════════════════════════════════════
    # MODE: --url (Rewrite จาก URL)
    # ══════════════════════════════════════════════════════════
    if url_target:
        สรุปเนื้อหา = ดึงเนื้อหาและ_Rewrite(url_target)
        if สรุปเนื้อหา:
            หัวข้อ = เรียก_ollama_เร็ว(
                f'จากสรุปนี้:\n{สรุปเนื้อหา[:500]}\n\nคิดหัวข้อบทความภาษาไทย 1 หัวข้อ ตอบแค่หัวข้อเดียวไม่ต้องมีคำอธิบาย'
            ).strip().split('\n')[0]
            log_ok(f"ได้หัวข้อจาก URL: {หัวข้อ}")
        else:
            log_err("ไม่สามารถดึงข้อมูลจาก URL ได้")
            return

    # ══════════════════════════════════════════════════════════
    # MODE: ปกติ — สร้าง N บทความ (--count N, default 1)
    # ══════════════════════════════════════════════════════════
    log_section(f"📝 Normal Mode — สร้าง {จำนวน} บทความ")
    บทความทั้งหมด = []
    เวลาเริ่ม     = time.time()
    รายการที่มี   = ดึงหัวข้อที่มี()

    for i in range(จำนวน):
        if จำนวน > 1:
            log(f"\n{_progress_bar(i, จำนวน)} [{i+1}/{จำนวน}]")

        if หัวข้อ and i == 0:
            หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน = _pick(หัวข้อ)
        else:
            หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน = _pick()

        if not หัวข้อ_ปัจจุบัน:
            log_err(f"ไม่ได้หัวข้อบทความที่ {i+1} — ข้าม")
            continue

        if เช็คซ้ำ(หัวข้อ_ปัจจุบัน, รายการที่มี):
            log_warn(f"หัวข้อซ้ำ: {หัวข้อ_ปัจจุบัน[:45]}... — ข้าม")
            continue

        log(f"📝 {หัวข้อ_ปัจจุบัน[:55]}... [{หมวด_ไทย.get(หมวด_ปัจจุบัน, หมวด_ปัจจุบัน)}]")
        เนื้อหา = เขียนบทความ(หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน)

        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_ปัจจุบัน, ชื่อไฟล์))
            รายการที่มี.append(หัวข้อ_ปัจจุบัน)
            log_ok(f"✅ {ชื่อไฟล์}")
        else:
            log_err(f"เขียนบทความที่ {i+1} ล้มเหลว")

        if i < จำนวน - 1:
            time.sleep(2)

    ใช้เวลา = int(time.time() - เวลาเริ่ม)
    log_section(
        f"🎊 เสร็จ! สร้าง {len(บทความทั้งหมด)}/{จำนวน} บทความ"
        f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
    )
    for h, f in บทความทั้งหมด:
        log(f"   📄 {f} — {h}")
    if not DRY_RUN and บทความทั้งหมด:
        log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")


if __name__ == "__main__":
    main()