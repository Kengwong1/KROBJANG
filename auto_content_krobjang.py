import requests
import os
import re
import random
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# CONFIG
# =====================================================

OLLAMA_MODEL  = "PhromAI:latest"
KROBJANG_PATH = Path(r"D:\Projects\krubjang-site full")
OLLAMA_URL    = "http://localhost:11434/api/generate"
WEBSITE_URL   = os.getenv("WEBSITE_URL", "https://krobjang.vercel.app")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID    = os.getenv("FB_PAGE_ID", "126444234360863")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
UNSPLASH_KEY    = os.getenv("UNSPLASH_KEY", "")

# =====================================================
# CONSTANTS
# =====================================================

CATEGORY_TO_EMOJI = {
    "ai": "🤖", "finance": "💰", "horoscope": "⭐",
    "health": "💚", "lifestyle": "🌟", "news": "📰",
}

CATEGORY_IMAGES = {
    "ai":        "artificial+intelligence+technology",
    "finance":   "money+finance+investment",
    "horoscope": "stars+astrology+sky",
    "health":    "healthy+lifestyle+wellness",
    "lifestyle": "lifestyle+modern+living",
    "news":      "thailand+news+newspaper",
}

# fallback topics ถ้า trending ดึงไม่ได้
FALLBACK_TOPICS = {
    "ai": [
        "5 เครื่องมือ AI ฟรีที่คนไทยควรใช้ในปี 2026",
        "วิธีใช้ AI ช่วยทำงานประจำวันให้เสร็จเร็วขึ้น",
        "AI กับอาชีพไทย อะไรจะหายไปอะไรจะเกิดใหม่",
        "ChatGPT vs Gemini vs Claude ใช้อะไรดีสำหรับคนไทย",
        "สร้างรายได้ออนไลน์ด้วย AI ทำได้จริงไหม",
    ],
    "finance": [
        "วิธีเก็บเงินแบบง่ายๆ สำหรับมนุษย์เงินเดือน",
        "กองทุน RMF กับ SSF ต่างกันยังไง เลือกอะไรดี",
        "เริ่มลงทุนหุ้นครั้งแรก ต้องรู้อะไรบ้าง",
        "บัตรเครดิตไหนคุ้มสุดสำหรับคนไทยปี 2026",
        "ทำบัญชีรายรับรายจ่ายแบบง่ายๆ ด้วยมือถือ",
    ],
    "horoscope": [
        "ดูดวงประจำสัปดาห์ ราศีใดโชคดีเรื่องการเงิน",
        "ฤกษ์ดีประจำเดือนนี้ เหมาะทำอะไรบ้าง",
        "เลขมงคลประจำวันนี้ แต่ละราศีควรใช้เลขอะไร",
        "ดวงความรักราศีต่างๆ ใครจะเจอคนพิเศษ",
        "ดูดวงอาชีพและการงาน ราศีไหนได้เลื่อนตำแหน่ง",
    ],
    "health": [
        "5 วิธีออกกำลังกายในบ้านโดยไม่ต้องซื้ออุปกรณ์",
        "อาหารไทยที่ดีต่อสุขภาพ ทานได้ทุกวันไม่อ้วน",
        "วิธีนอนหลับให้ดีขึ้น แก้ปัญหานอนไม่หลับ",
        "โรคออฟฟิศซินโดรม รักษาและป้องกันอย่างไร",
        "สมุนไพรไทยที่ช่วยเสริมภูมิคุ้มกัน",
    ],
    "lifestyle": [
        "10 แอปมือถือที่คนไทยควรมีติดเครื่องไว้",
        "ไอเดียแต่งบ้านสวยงามด้วยงบน้อย",
        "เที่ยวในไทยสุดคุ้ม จังหวัดไหนน่าไปเดือนนี้",
        "ทำอาหารง่ายๆ สำหรับคนทำงาน ใช้เวลาไม่เกิน 20 นาที",
        "วิธีลดความเครียดในชีวิตประจำวัน",
    ],
}

# =====================================================
# HTML TEMPLATE  ← ไม่มี <style> แล้ว ใช้ style.css แทน
# =====================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ครบจัง</title>
  <meta name="description" content="{description}">
  <!-- Google Fonts + Shared CSS (แก้ style.css ที่เดียว ทุกหน้าเปลี่ยน) -->
  <link rel="stylesheet" href="/style.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2068902667667616" crossorigin="anonymous"></script>
</head>
<body>
  <header>
    <nav>
      <a class="brand" href="/">ครบจัง</a>
      <a href="/ai">🤖 AI</a>
      <a href="/finance">💰 การเงิน</a>
      <a href="/health">💚 สุขภาพ</a>
      <a href="/lifestyle">🌟 ไลฟ์สไตล์</a>
      <a href="/horoscope">⭐ ดวง</a>
    </nav>
  </header>

  <main class="article-container">
    <!-- Ad Top -->
    <div class="ad-slot">
      <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
           data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>

    <article>
      {source_badge}
      <h1>{title}</h1>
      <div class="meta">
        <span>📅 {date}</span>
        <span class="category-badge">{category}</span>
      </div>
      {hero_image}
      {content}
    </article>

    <!-- Ad Bottom -->
    <div class="ad-slot">
      <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
           data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>
  </main>

  <footer>
    <p>© {year} ครบจัง · อ่านครบ รู้จริง ใช้ได้เลย</p>
  </footer>
</body>
</html>"""

# =====================================================
# ── TRENDING SOURCE 1: RSS ข่าวไทย ──────────────────
# =====================================================

RSS_FEEDS = {
    "thairath": {
        "url":   "https://www.thairath.co.th/rss/news.xml",
        "label": "ไทยรัฐ",
    },
    "sanook": {
        "url":   "https://www.sanook.com/news/rss/",
        "label": "Sanook",
    },
    "kapook": {
        "url":   "https://hilight.kapook.com/rss/kapook_all.xml",
        "label": "Kapook",
    },
    "tnn": {
        "url":   "https://www.tnnthailand.com/feed/",
        "label": "TNN",
    },
    "pptvhd": {
        "url":   "https://www.pptvhd36.com/feed",
        "label": "PPTV",
    },
}

def fetch_rss_topics(max_items: int = 10) -> list[dict]:
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; KrobjangBot/1.0)"}

    for key, feed in RSS_FEEDS.items():
        try:
            resp = requests.get(feed["url"], headers=headers, timeout=10)
            resp.encoding = "utf-8"
            root = ET.fromstring(resp.content)

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//item") or root.findall(".//atom:entry", ns)

            count = 0
            for item in items:
                title_el = item.find("title")
                if title_el is None:
                    title_el = item.find("atom:title", ns)
                if title_el is None or not title_el.text:
                    continue

                title = title_el.text.strip()
                if len(title) < 10:
                    continue

                results.append({
                    "title":    title,
                    "source":   feed["label"],
                    "category": _classify_news(title),
                })
                count += 1
                if count >= 3:
                    break

            print(f"  RSS [{feed['label']}]: {count} items")

        except Exception as e:
            print(f"  RSS [{key}] error: {e}")

    random.shuffle(results)
    return results[:max_items]


def _classify_news(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["หุ้น", "เงิน", "ลงทุน", "ธนาคาร", "บาท", "เศรษฐกิจ", "ดอกเบี้ย", "ราคา", "ค่าเงิน"]):
        return "finance"
    if any(w in t for w in ["ดวง", "ราศี", "หวย", "เลข", "โชค", "ฤกษ์"]):
        return "horoscope"
    if any(w in t for w in ["ai", "เทคโนโลยี", "แอป", "iphone", "samsung", "ดิจิทัล", "ซอฟต์แวร์", "อินเทอร์เน็ต"]):
        return "ai"
    if any(w in t for w in ["สุขภาพ", "โรค", "ยา", "หมอ", "ออกกำลัง", "อาหาร", "โภชนาการ", "พยาบาล"]):
        return "health"
    return "news"

# =====================================================
# ── TRENDING SOURCE 2: YouTube Thailand ─────────────
# =====================================================

def fetch_youtube_trending(max_items: int = 5) -> list[dict]:
    results = []
    if not YOUTUBE_API_KEY:
        print("  YouTube: ไม่มี API key ข้ามครับ")
        return results
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part":       "snippet",
            "chart":      "mostPopular",
            "regionCode": "TH",
            "maxResults": max_items,
            "key":        YOUTUBE_API_KEY,
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        for item in data.get("items", []):
            title = item["snippet"]["title"]
            results.append({
                "title":    title,
                "source":   "YouTube TH",
                "category": _classify_news(title),
            })
        print(f"  YouTube TH: {len(results)} items")
    except Exception as e:
        print(f"  YouTube error: {e}")
    return results

# =====================================================
# ── TRENDING SOURCE 3: TikTok Discover ──────────────
# =====================================================

def fetch_tiktok_trending(max_items: int = 5) -> list[dict]:
    results = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; KrobjangBot/1.0)",
            "Accept-Language": "th-TH,th;q=0.9",
        }
        r = requests.get("https://www.tiktok.com/discover", headers=headers, timeout=15)
        seen = set()

        pattern = re.compile(r'(?:"title"|"challengeName"|"hashtag")\s*:\s*"([^"]{3,40})"')
        for m in pattern.finditer(r.text):
            tag = m.group(1).strip("#").strip()
            if tag and tag not in seen:
                seen.add(tag)
                if len(seen) >= max_items:
                    break

        for tag in seen:
            results.append({
                "title":    f"เทรนด์ #{tag} กำลังมาแรงบน TikTok",
                "source":   "TikTok Discover",
                "category": _classify_news(tag),
            })
        print(f"  TikTok Discover: {len(results)} hashtags")

    except Exception as e:
        print(f"  TikTok Discover error: {e}")

    return results[:max_items]

# =====================================================
# ── AGGREGATE TOPICS ─────────────────────────────────
# =====================================================

def get_smart_topics(articles_per_run: int = 5) -> list[dict]:
    """รวม topics จากทุก source: RSS 40% | YouTube 30% | TikTok 20% | Fallback 10%"""
    print("\n📡 Fetching trending topics from all sources...")

    rss_topics     = fetch_rss_topics(max_items=10)
    youtube_topics = fetch_youtube_trending(max_items=5)
    tiktok_topics  = fetch_tiktok_trending(max_items=5)

    print(f"\n  Total: RSS={len(rss_topics)}, YouTube={len(youtube_topics)}, TikTok={len(tiktok_topics)}")

    pool = []
    rss_quota     = max(1, int(articles_per_run * 0.40))
    youtube_quota = max(1, int(articles_per_run * 0.30))
    tiktok_quota  = max(1, int(articles_per_run * 0.20))

    pool += rss_topics[:rss_quota]
    pool += youtube_topics[:youtube_quota]
    pool += tiktok_topics[:tiktok_quota]

    remaining = articles_per_run - len(pool)
    if remaining > 0:
        categories = list(FALLBACK_TOPICS.keys())
        random.shuffle(categories)
        for cat in categories[:remaining]:
            topic = random.choice(FALLBACK_TOPICS[cat])
            pool.append({"title": topic, "source": "internal", "category": cat})

    random.shuffle(pool)
    selected = pool[:articles_per_run]

    print(f"\n✅ Selected {len(selected)} topics:")
    for i, t in enumerate(selected, 1):
        print(f"  {i}. [{t['category']}] {t['title'][:60]} ({t['source']})")

    return selected

# =====================================================
# OLLAMA HELPERS
# =====================================================

def generate_content_with_ollama(title: str, category: str) -> str:
    prompt = f"""เขียนบทความภาษาไทยเรื่อง "{title}"
หมวด: {category}
ความยาว: 500-800 คำ
รูปแบบ: HTML ใช้แท็ก <h2> <p> <ul> <li>
ห้ามใส่: DOCTYPE html head body style
ตอบเป็น HTML ล้วนๆ เท่านั้น ไม่ต้องมีคำอธิบาย"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.7, "num_predict": 1500}},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return "<p>เนื้อหากำลังอัปเดต</p>"
    except Exception as e:
        print(f"  Ollama error: {e}")
        return "<p>เนื้อหากำลังอัปเดต</p>"


def generate_caption_with_ollama(title: str, category: str, article_url: str) -> str:
    """
    สร้าง caption Facebook ที่น่าหยุดอ่าน:
    - บรรทัด 1: hook/คำถาม/ข้อเท็จจริงน่าตกใจ
    - บรรทัด 2-3: เนื้อหาสั้นๆ ที่น่าสนใจ ทำให้อยากอ่านต่อ
    - บรรทัด 4: CTA + ลิงก์
    - hashtag ท้าย
    """
    emoji = CATEGORY_TO_EMOJI.get(category, "📌")
    prompt = f"""เขียน caption Facebook ภาษาไทยสำหรับบทความเรื่อง "{title}"
สไตล์: กระชับ น่าหยุดอ่าน ทำให้คนอยากคลิก
โครงสร้าง 4 ส่วน:
1. hook 1 บรรทัด: คำถามหรือข้อเท็จจริงน่าตกใจ ไม่เกิน 15 คำ
2. เนื้อหา 2 บรรทัด: บอกประโยชน์สั้นๆ ว่าอ่านแล้วได้อะไร
3. CTA: "👉 อ่านฟรีได้เลยที่ลิงก์นี้ครับ"
4. hashtag 3-4 ตัวที่เกี่ยวข้อง

ใช้ emoji บ้าง ไม่เกิน 4 ตัวทั้ง caption
ตอบแค่ caption เท่านั้น ห้ามอธิบาย"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.85, "num_predict": 250}},
            timeout=120,
        )
        if response.status_code == 200:
            ai_caption = response.json().get("response", "").strip()
            # ต่อ URL ท้ายเสมอ
            return f"{emoji} {ai_caption}\n\n🔗 {article_url}"
    except Exception:
        pass

    # fallback
    return (
        f"{emoji} {title}\n\n"
        f"บทความนี้มีคำตอบที่คุณต้องรู้ อ่านจบแล้วนำไปใช้ได้ทันที\n"
        f"👉 อ่านฟรีได้เลยที่ลิงก์นี้ครับ\n\n"
        f"🔗 {article_url}"
    )

# =====================================================
# IMAGE HELPER
# =====================================================

def get_unsplash_image_url(category: str) -> str:
    """คืน URL รูป Unsplash สำหรับ Facebook post"""
    keyword = CATEGORY_IMAGES.get(category, "thailand")

    if UNSPLASH_KEY:
        try:
            r = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": keyword, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
                timeout=10,
            )
            data = r.json()
            return data["urls"]["regular"]
        except Exception as e:
            print(f"  Unsplash API error: {e}")

    # fallback (redirect-based ไม่รับประกัน แต่ใช้ได้กรณีไม่มี key)
    return f"https://source.unsplash.com/1200x630/?{keyword}"


def get_hero_image_tag(category: str) -> str:
    """สร้าง <img> tag สำหรับ hero ในหน้าเว็บ"""
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    return (
        f'<img class="hero-image" '
        f'src="https://source.unsplash.com/800x420/?{keyword}" '
        f'alt="{category}" loading="lazy">'
    )

# =====================================================
# FACEBOOK  ← โพสต์รูป + caption AI ที่น่าหยุดอ่าน
# =====================================================

def post_to_facebook(title: str, category: str, filename: str) -> bool:
    """
    โพสต์บทความไปยัง Facebook Page พร้อมรูปภาพ
    ใช้ /photos endpoint เพื่อแนบรูปได้จริง
    """
    if not FB_PAGE_TOKEN:
        print("  Facebook: ไม่มี token ข้ามไปครับ")
        return False

    try:
        article_url = f"{WEBSITE_URL}/{filename}"
        image_url   = get_unsplash_image_url(category)
        caption     = generate_caption_with_ollama(title, category, article_url)

        # ใช้ /photos endpoint — โพสต์รูปพร้อม caption ในโพสต์เดียว
        api_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
        payload = {
            "url":          image_url,
            "caption":      caption,
            "access_token": FB_PAGE_TOKEN,
        }

        resp   = requests.post(api_url, data=payload, timeout=30)
        result = resp.json()

        if "id" in result:
            print(f"  ✅ Facebook โพสต์สำเร็จ! ID: {result['id']}")
            return True
        else:
            error_msg = result.get("error", {}).get("message", str(result))
            print(f"  ❌ Facebook error: {error_msg}")
            return False

    except Exception as e:
        print(f"  Facebook exception: {e}")
        return False

# =====================================================
# UTILITIES
# =====================================================

def create_safe_filename(category: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand     = random.randint(1000, 9999)
    return f"{category}_{date_str}_{rand}.html"

# =====================================================
# MAIN WORKFLOW
# =====================================================

def generate_daily_content(articles_per_run: int = 5):
    print(f"\n{'='*55}")
    print(f"  Auto Content Generator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Model: {OLLAMA_MODEL}")
    print(f"{'='*55}\n")

    selected = get_smart_topics(articles_per_run)
    generated_files = []

    for topic in selected:
        title    = topic["title"]
        category = topic["category"]
        source   = topic.get("source", "internal")

        print(f"\n✍️  Generating: [{category}] {title[:55]}")

        content    = generate_content_with_ollama(title, category)
        hero_image = get_hero_image_tag(category)

        source_badge = ""
        if source != "internal":
            source_badge = f'<span class="source-badge">📡 {source}</span>'

        html = HTML_TEMPLATE.format(
            title        = title,
            description  = title[:150],
            date         = datetime.now().strftime("%d/%m/%Y"),
            category     = category,
            hero_image   = hero_image,
            content      = content,
            source_badge = source_badge,
            year         = datetime.now().year,
        )

        filename = create_safe_filename(category)
        filepath = os.path.join(KROBJANG_PATH, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        generated_files.append(filename)
        print(f"  💾 Saved: {filename}")

        post_to_facebook(title, category, filename)

    return generated_files


def git_push(files: list):
    try:
        os.chdir(KROBJANG_PATH)
        # push style.css ด้วยถ้ายังไม่เคย push
        subprocess.run(["git", "add", "style.css"] + files, check=False)
        date_str = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(["git", "commit", "-m", f"auto: {len(files)} articles {date_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"\n🚀 Pushed {len(files)} files → Vercel deploying...")
    except Exception as e:
        print(f"Git error: {e}")


if __name__ == "__main__":
    files = generate_daily_content(articles_per_run=5)
    if files:
        git_push(files)
        print(f"\n✅ Done! {len(files)} smart articles generated today")
