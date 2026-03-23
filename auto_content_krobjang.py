import requests
import os
import random
import subprocess
import feedparser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# ตั้งค่าตรงนี้ครับ
# ==========================================
OLLAMA_MODEL = "PhromAI:latest"
KROBJANG_PATH = r"D:\Projects\krubjang-site full"
OLLAMA_URL = "http://localhost:11434/api/generate"
SITE_URL = "https://krobjang.com"  # เปลี่ยนเป็น URL จริง

# Facebook Config (อ่านจาก .env)
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# หมวดของเว็บ และ keyword ที่เกี่ยวข้อง
CATEGORY_KEYWORDS = {
    "ai": ["AI", "ChatGPT", "Gemini", "Claude", "ปัญญาประดิษฐ์", "machine learning", "โมเดล AI"],
    "finance": ["หุ้น", "ลงทุน", "เงิน", "กองทุน", "ค่าเงิน", "บิทคอยน์", "crypto", "ดอกเบี้ย", "เศรษฐกิจ"],
    "horoscope": ["ดูดวง", "ราศี", "ฮวงจุ้ย", "เลขเด็ด", "หวย", "โชคลาภ", "ดาว", "ดวงชะตา"],
    "health": ["สุขภาพ", "โรค", "ออกกำลังกาย", "อาหาร", "วิตามิน", "ยา", "โรงพยาบาล", "ฟิตเนส"],
    "lifestyle": ["ท่องเที่ยว", "อาหาร", "แฟชั่น", "บ้าน", "รถ", "มือถือ", "แอป", "เกม", "ภาพยนตร์"],
}

# RSS feeds ข่าวไทย
THAI_NEWS_RSS = [
    "https://feeds.thairath.co.th/tr/home.xml",
    "https://www.sanook.com/feed/",
    "https://feeds.kapook.com/kapook/news.xml",
]

CATEGORY_IMAGES = {
    "ai": "artificial+intelligence+technology",
    "finance": "money+finance+investment",
    "horoscope": "stars+astrology+sky",
    "health": "healthy+lifestyle+wellness",
    "lifestyle": "lifestyle+modern+living",
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ครบจังดอทคอม</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="style.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2068902667667616" crossorigin="anonymous"></script>
  <style>
    .hero-image {{ width:100%; max-height:400px; object-fit:cover; border-radius:12px; margin-bottom:24px; }}
    .article-container {{ max-width:800px; margin:0 auto; padding:20px; }}
    .meta {{ color:#888; font-size:14px; margin-bottom:20px; }}
    .trending-badge {{ background:#ff4444; color:white; padding:4px 10px; border-radius:20px; font-size:12px; margin-left:8px; }}
  </style>
</head>
<body>
  <header>
    <nav>
      <a href="index.html">หน้าแรก</a>
      <a href="ai.html">AI</a>
      <a href="finance.html">การเงิน</a>
      <a href="horoscope.html">ดูดวง</a>
      <a href="health.html">สุขภาพ</a>
    </nav>
  </header>

  <main class="article-container">
    <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>

    <article>
      <h1>{title} {trending_badge}</h1>
      <p class="meta">อัปเดต: {date} | หมวด: {category} | {source_label}</p>
      {hero_image}
      {content}
    </article>

    <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </main>

  <footer>
    <p>© 2026 ครบจังดอทคอม - ครบทุกเรื่อง ใช้งานง่ายทุกวัย</p>
  </footer>
</body>
</html>"""


def get_google_trends():
    """ดึง trending topics จาก Google Trends Thailand ผ่าน RSS"""
    try:
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=TH"
        feed = feedparser.parse(url)
        topics = [entry.title for entry in feed.entries][:20]
        print(f"  Google Trends (RSS): ดึงได้ {len(topics)} หัวข้อ")
        return topics
    except Exception as e:
        print(f"  Google Trends error: {e}")
        return []


def get_thai_news_topics():
    """ดึงหัวข้อข่าวจาก RSS feeds ไทย"""
    topics = []
    for rss_url in THAI_NEWS_RSS:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:10]:
                topics.append(entry.title)
        except Exception as e:
            print(f"  RSS error ({rss_url}): {e}")
    print(f"  Thai News RSS: ดึงได้ {len(topics)} หัวข้อ")
    return topics[:20]


def match_topic_to_category(topic: str) -> str:
    """จับคู่หัวข้อ trending กับหมวดของเว็บ"""
    topic_lower = topic.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in topic_lower)
        scores[category] = score
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return random.choice(list(CATEGORY_KEYWORDS.keys()))


def get_trending_topics_for_site() -> list:
    """รวม trending topics และจับคู่กับหมวดเว็บ"""
    all_topics = []

    trends = get_google_trends()
    for t in trends:
        category = match_topic_to_category(t)
        all_topics.append({"title": t, "category": category, "source": "trending"})

    news = get_thai_news_topics()
    for n in news:
        category = match_topic_to_category(n)
        all_topics.append({"title": n, "category": category, "source": "news"})

    if not all_topics:
        print("  ใช้หัวข้อ backup...")
        all_topics = [
            {"title": "5 เครื่องมือ AI ฟรีที่คนไทยควรใช้ในปี 2026", "category": "ai", "source": "backup"},
            {"title": "วิธีเก็บเงินแบบง่ายๆ สำหรับมนุษย์เงินเดือน", "category": "finance", "source": "backup"},
            {"title": "ดูดวงประจำสัปดาห์ ราศีใดโชคดีเรื่องการเงิน", "category": "horoscope", "source": "backup"},
            {"title": "5 วิธีออกกำลังกายในบ้านโดยไม่ต้องซื้ออุปกรณ์", "category": "health", "source": "backup"},
            {"title": "10 แอปมือถือที่คนไทยควรมีติดเครื่องไว้", "category": "lifestyle", "source": "backup"},
        ]

    random.shuffle(all_topics)
    return all_topics


def get_unsplash_image(category: str) -> str:
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    return f'<img class="hero-image" src="https://source.unsplash.com/800x400/?{keyword}" alt="{category}" loading="lazy">'


def generate_content_with_ollama(title: str, category: str, is_trending: bool = False) -> str:
    trending_note = "เป็นเรื่องที่กำลังเป็นกระแสในไทยตอนนี้ " if is_trending else ""
    prompt = f"""เขียนบทความภาษาไทยเรื่อง "{title}"
หมวด: {category}
{trending_note}ความยาว: 500-800 คำ
รูปแบบ: HTML ใช้แท็ก <h2> <p> <ul> <li>
ห้ามใส่: DOCTYPE html head body
ตอบเป็น HTML ล้วนๆ เท่านั้น ไม่ต้องมีคำอธิบาย"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1500},
            },
            timeout=300,
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return "<p>เนื้อหากำลังอัปเดต</p>"
    except Exception as e:
        print(f"  Ollama error: {e}")
        return "<p>เนื้อหากำลังอัปเดต</p>"


def create_safe_filename(category: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{category}_{date_str}_{rand}.html"


def post_to_facebook(title: str, filename: str, category: str, source: str):
    """โพสลิงค์บทความไปยัง Facebook Page"""
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print("  Facebook: ไม่พบ Token หรือ Page ID ใน .env (ข้ามการโพสต์)")
        return

    article_url = f"{SITE_URL}/{filename}"
    trending_tag = "🔥 กำลังเป็นกระแส! " if source == "trending" else ""
    message = f"{trending_tag}📖 {title}\n\n🔗 อ่านเพิ่มเติมที่: {article_url}\n\n#ครบจัง #{category}"

    try:
        response = requests.post(
            f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed",
            data={
                "message": message,
                "link": article_url,
                "access_token": FB_PAGE_TOKEN,
            },
            timeout=30,
        )
        result = response.json()
        if "id" in result:
            print(f"  Facebook: โพสสำเร็จ! Post ID: {result['id']}")
        else:
            print(f"  Facebook Error: {result.get('error', {}).get('message', 'Unknown error')}")
    except Exception as e:
        print(f"  Facebook Error: {e}")


def generate_daily_content(articles_per_run: int = 5):
    print(f"\n{'='*50}")
    print(f"Auto Content Generator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Model: {OLLAMA_MODEL}")
    print(f"{'='*50}\n")

    print("กำลังดึง Trending Topics...")
    trending_pool = get_trending_topics_for_site()
    
    # ดึงหัวข้อตามจำนวนที่กำหนด (ป้องกัน error กรณีดึงหัวข้อมาได้น้อยกว่าที่กำหนด)
    selected = trending_pool[:min(articles_per_run, len(trending_pool))]
    generated_files = []

    for item in selected:
        title = item["title"]
        category = item["category"]
        source = item["source"]
        is_trending = source == "trending"

        source_label = "🔥 Trending" if source == "trending" else "📰 ข่าววันนี้" if source == "news" else "📝 บทความ"
        trending_badge = '<span class="trending-badge">🔥 Trending</span>' if is_trending else ""

        print(f"\nGenerating: [{category}] {title} ({source_label})")

        content = generate_content_with_ollama(title, category, is_trending)
        hero_image = get_unsplash_image(category)

        html = HTML_TEMPLATE.format(
            title=title,
            description=title[:150],
            date=datetime.now().strftime("%d/%m/%Y"),
            category=category,
            hero_image=hero_image,
            content=content,
            trending_badge=trending_badge,
            source_label=source_label,
        )

        filename = create_safe_filename(category)
        filepath = os.path.join(KROBJANG_PATH, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        generated_files.append(filename)
        print(f"  Saved: {filename}")

        post_to_facebook(title, filename, category, source)

    return generated_files


def git_push(files: list):
    try:
        os.chdir(KROBJANG_PATH)
        date_str = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(["git", "add"] + files, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"auto: add {len(files)} trending articles {date_str}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print(f"\nPushed {len(files)} files to GitHub → Vercel deploying...")
    except Exception as e:
        print(f"Git error: {e}")


if __name__ == "__main__":
    # ตอนนี้ตั้งไว้ให้สร้างทีละ 5 บทความนะครับ
    files = generate_daily_content(articles_per_run=5)
    
    if files:
        # ระบบจะทำการ Push เข้า Github ให้อัตโนมัติถ้ามีไฟล์เกิดใหม่
        git_push(files)
        print(f"\nDone! {len(files)} trending articles generated today")