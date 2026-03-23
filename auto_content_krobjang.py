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
SITE_URL = "https://krobjang.vercel.app"

# ==========================================
# ตั้งค่าหลายเพจ
# ==========================================
PAGES = [
    {
        "name": "มาชมคลิป",
        "token_env": "FB_PAGE_TOKEN",
        "page_id_env": "FB_PAGE_ID",
        "style": "funny",
        "categories": ["lifestyle", "health", "ai", "finance"],
        "post_tone": "สนุกสนาน ตลก ผ่อนคลาย",
    },
    {
        "name": "แสงธรรมส่องทาง",
        "token_env": "FB_PAGE_TOKEN_2",
        "page_id_env": "FB_PAGE_ID_2",
        "style": "dharma",
        "categories": ["horoscope", "lifestyle", "health"],
        "post_tone": "สงบ ธรรมะ สร้างแรงบันดาลใจ",
    },
]

# หมวดและ keyword
CATEGORY_KEYWORDS = {
    "ai": ["AI", "ChatGPT", "Gemini", "Claude", "ปัญญาประดิษฐ์", "machine learning"],
    "finance": ["หุ้น", "ลงทุน", "เงิน", "กองทุน", "บิทคอยน์", "เศรษฐกิจ"],
    "horoscope": ["ดูดวง", "ราศี", "ฮวงจุ้ย", "เลขเด็ด", "หวย", "ดวงชะตา", "ธรรมะ", "บุญ", "กรรม"],
    "health": ["สุขภาพ", "โรค", "ออกกำลังกาย", "อาหาร", "วิตามิน"],
    "lifestyle": ["ท่องเที่ยว", "แฟชั่น", "บ้าน", "มือถือ", "เกม", "ตลก", "ขำ"],
}

# หัวข้อ backup แยกตามสไตล์
TOPICS_BY_STYLE = {
    "funny": {
        "lifestyle": ["10 เรื่องฮาที่คนไทยเจอทุกวันแต่ไม่รู้ตัว", "5 นิสัยคนไทยที่ฝรั่งงงมากที่สุด", "เมื่อเทคโนโลยีทำให้ชีวิตฮามากขึ้น"],
        "health": ["5 วิธีออกกำลังกายที่คนขี้เกียจทำได้จริง", "อาหารไทยที่กินแล้วอ้วนไม่รู้ตัว"],
        "ai": ["AI ทำอะไรได้บ้างที่มนุษย์ยังทำไม่ได้", "5 เครื่องมือ AI ฟรีที่คนไทยควรลองใช้"],
        "finance": ["วิธีเก็บเงินแบบง่ายๆ สำหรับคนใช้เงินไม่เป็น", "5 ความเชื่อผิดๆ เรื่องเงินที่คนไทยยังเชื่ออยู่"],
    },
    "dharma": {
        "horoscope": ["กรรมดีกรรมชั่ว ทำอย่างไรให้ชีวิตดีขึ้น", "บทสวดมนต์ก่อนนอน นำความสงบมาสู่จิตใจ", "ตายแล้วไปไหน มุมมองจากพระพุทธศาสนา", "สิ่งลี้ลับที่วิทยาศาสตร์ยังอธิบายไม่ได้"],
        "lifestyle": ["หลักธรรมที่ช่วยให้ชีวิตมีความสุขมากขึ้น", "วิธีปล่อยวางความทุกข์ตามแบบพุทธศาสนา"],
        "health": ["การทำสมาธิกับสุขภาพจิต ผลที่พิสูจน์แล้ว"],
    },
}

CATEGORY_IMAGES = {
    "ai": "artificial+intelligence+technology",
    "finance": "money+finance+investment",
    "horoscope": "stars+astrology+temple",
    "health": "healthy+lifestyle+wellness",
    "lifestyle": "thailand+lifestyle+happy",
}

# หน้าหมวดที่ต้องอัปเดต
CATEGORY_PAGES = {
    "ai": "ai.html",
    "finance": "finance.html",
    "horoscope": "horoscope.html",
    "health": "health.html",
    "lifestyle": "lifestyle.html",
}

THAI_NEWS_RSS = [
    "https://www.matichon.co.th/feed",
    "https://mgronline.com/rss/all.aspx",
]


def get_thai_news_topics():
    topics = []
    for rss_url in THAI_NEWS_RSS:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:8]:
                topics.append(entry.title)
        except:
            pass
    print(f"  Thai News RSS: ดึงได้ {len(topics)} หัวข้อ")
    return topics[:20]


def match_topic_to_category(topic: str, allowed_categories: list) -> str:
    topic_lower = topic.lower()
    scores = {}
    for category in allowed_categories:
        keywords = CATEGORY_KEYWORDS.get(category, [])
        score = sum(1 for kw in keywords if kw.lower() in topic_lower)
        scores[category] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else random.choice(allowed_categories)


def get_unsplash_image(category: str, css_class: str = "hero-image") -> str:
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    rand = random.randint(1, 9999)
    return f'<img class="{css_class}" src="https://source.unsplash.com/800x400/?{keyword}&sig={rand}" alt="{category}" loading="lazy">'


def generate_content_with_ollama(title: str, category: str, style: str) -> str:
    style_note = "เขียนในแนวสนุกสนาน ตลก ผ่อนคลาย" if style == "funny" else "เขียนในแนวธรรมะ สงบ สร้างแรงบันดาลใจ"
    prompt = f"""เขียนบทความภาษาไทยเรื่อง "{title}"
หมวด: {category}
สไตล์: {style_note}
ความยาว: 500-800 คำ
รูปแบบ: HTML ใช้แท็ก <h2> <p> <ul> <li>
ห้ามใส่: DOCTYPE html head body
ตอบเป็น HTML ล้วนๆ เท่านั้น"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.8, "num_predict": 1500}},
            timeout=300,
        )
        if response.status_code == 200:
            content = response.json().get("response", "")
            # แทรกรูปกลางบทความ
            keyword = CATEGORY_IMAGES.get(category, "thailand")
            rand = random.randint(1, 9999)
            inline_img = f'\n<img style="width:100%;border-radius:8px;margin:16px 0;" src="https://source.unsplash.com/800x300/?{keyword}&sig={rand}" alt="{category}" loading="lazy">\n'
            mid = len(content) // 2
            nearest_p = content.find("</p>", mid)
            if nearest_p > 0:
                content = content[:nearest_p+4] + inline_img + content[nearest_p+4:]
            return content
        return "<p>เนื้อหากำลังอัปเดต</p>"
    except Exception as e:
        print(f"  Ollama error: {e}")
        return "<p>เนื้อหากำลังอัปเดต</p>"


def create_article_html(title: str, category: str, content: str, hero_image: str, source_label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ครบจังดอทคอม</title>
  <meta name="description" content="{title[:150]}">
  <meta property="og:title" content="{title}">
  <meta property="og:image" content="https://source.unsplash.com/1200x630/?{CATEGORY_IMAGES.get(category,'thailand')}">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2068902667667616" crossorigin="anonymous"></script>
  <style>
    :root {{
      --primary-dark: #1e3a8a; --primary: #1e40af; --soft: #eff6ff;
      --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --radius: 18px;
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Sarabun',sans-serif; }}
    body {{ background:var(--bg); color:var(--text); line-height:1.7; }}
    header {{ background:linear-gradient(135deg,var(--primary-dark),var(--primary)); color:#fff; padding:0.75rem 1rem; display:flex; justify-content:center; align-items:center; position:sticky; top:0; z-index:1000; box-shadow:0 2px 12px rgba(30,64,175,0.3); }}
    .logo {{ font-size:1.5rem; font-weight:800; }}
    .main-nav {{ background:#fff; padding:0.5rem 0; box-shadow:0 2px 8px rgba(0,0,0,0.08); }}
    .nav-wrap {{ max-width:1200px; margin:auto; display:flex; gap:0.75rem; padding:0 1rem; overflow-x:auto; white-space:nowrap; }}
    .main-nav a {{ text-decoration:none; color:#4b5563; font-weight:600; padding:0.6rem 1rem; border-radius:12px; transition:all 0.2s; display:flex; align-items:center; gap:0.4rem; font-size:0.95rem; }}
    .main-nav a:hover {{ background:var(--soft); }}
    .article-wrap {{ max-width:860px; margin:2rem auto; padding:0 1rem; }}
    .article-card {{ background:var(--card); border-radius:var(--radius); padding:2rem; box-shadow:0 4px 20px rgba(30,64,175,0.06); }}
    .article-card h1 {{ font-size:1.7rem; color:var(--primary); margin-bottom:0.5rem; line-height:1.4; }}
    .meta {{ color:var(--muted); font-size:0.9rem; margin-bottom:1.5rem; }}
    .hero-image {{ width:100%; max-height:400px; object-fit:cover; border-radius:12px; margin-bottom:1.5rem; }}
    .article-card h2 {{ font-size:1.2rem; color:var(--primary); margin:1.5rem 0 0.75rem; }}
    .article-card p {{ margin-bottom:1rem; font-size:1rem; }}
    .article-card ul {{ padding-left:1.5rem; margin-bottom:1rem; }}
    .article-card li {{ margin-bottom:0.5rem; }}
    .back-btn {{ display:inline-block; margin-top:1.5rem; padding:0.6rem 1.2rem; background:var(--primary); color:white; border-radius:10px; text-decoration:none; font-weight:600; }}
    .back-btn:hover {{ opacity:0.9; }}
    footer {{ margin-top:2rem; background:linear-gradient(135deg,var(--primary-dark),var(--primary)); color:white; text-align:center; padding:1.25rem; font-size:0.9rem; }}
    footer a {{ color:#e0f2fe; text-decoration:none; margin:0 0.5rem; }}
  </style>
</head>
<body>
  <header><div class="logo">ครบจังดอทคอม</div></header>
  <nav class="main-nav">
    <div class="nav-wrap">
      <a href="/index.html"><i class="fas fa-home" style="color:#45B7D1;"></i> หน้าแรก</a>
      <a href="/ai.html"><i class="fas fa-robot" style="color:#2EC4B6;"></i> AI</a>
      <a href="/finance.html"><i class="fas fa-coins" style="color:#FFD166;"></i> การเงิน</a>
      <a href="/horoscope.html"><i class="fas fa-star" style="color:#6A4C93;"></i> ดูดวง</a>
      <a href="/health.html"><i class="fas fa-heart" style="color:#FF6B6B;"></i> สุขภาพ</a>
      <a href="/lifestyle.html"><i class="fas fa-smile" style="color:#45B7D1;"></i> ไลฟ์สไตล์</a>
    </div>
  </nav>
  <div class="article-wrap">
    <ins class="adsbygoogle" style="display:block;margin-bottom:1rem;" data-ad-client="ca-pub-2068902667667616" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    <div class="article-card">
      <h1>{title}</h1>
      <p class="meta">📅 {datetime.now().strftime('%d/%m/%Y %H:%M')} | หมวด: {category} | {source_label}</p>
      {hero_image}
      {content}
      <a href="/{CATEGORY_PAGES.get(category, 'index.html')}" class="back-btn">← กลับหน้าหมวด {category}</a>
    </div>
    <ins class="adsbygoogle" style="display:block;margin-top:1rem;" data-ad-client="ca-pub-2068902667667616" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>
  <footer><p>© 2026 ครบจังดอทคอม | <a href="#">นโยบายความเป็นส่วนตัว</a></p></footer>
</body>
</html>"""


def update_category_page(category: str, title: str, filename: str):
    """แทรก card บทความใหม่ลงในหน้าหมวด"""
    category_file = CATEGORY_PAGES.get(category)
    if not category_file:
        return

    filepath = os.path.join(KROBJANG_PATH, category_file)
    if not os.path.exists(filepath):
        print(f"  ⚠️ ไม่พบไฟล์ {category_file}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # สร้าง card ใหม่
    date_str = datetime.now().strftime("%d/%m/%Y")
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    rand = random.randint(1, 9999)
    new_card = f"""
    <!-- AUTO_ARTICLE_START -->
    <div class="section" style="margin-bottom:1rem;">
      <div style="display:flex;gap:1rem;align-items:flex-start;">
        <img src="https://source.unsplash.com/120x80/?{keyword}&sig={rand}" 
             style="width:120px;height:80px;object-fit:cover;border-radius:10px;flex-shrink:0;" 
             alt="{category}" loading="lazy">
        <div>
          <a href="/{filename}" style="font-size:1rem;font-weight:700;color:#1e40af;text-decoration:none;line-height:1.4;display:block;margin-bottom:0.3rem;">{title}</a>
          <span style="font-size:0.8rem;color:#64748b;">📅 {date_str} | #{category}</span>
        </div>
      </div>
    </div>
    <!-- AUTO_ARTICLE_END -->"""

    # แทรกหลัง tag <div class="content-area">
    insert_marker = '<div class="content-area">'
    if insert_marker in html:
        html = html.replace(insert_marker, insert_marker + new_card, 1)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  📌 อัปเดตหน้า {category_file} สำเร็จ")
    else:
        print(f"  ⚠️ ไม่พบ marker ใน {category_file}")


def generate_fb_caption(title: str, category: str, style: str, article_url: str) -> str:
    if style == "funny":
        hooks = [
            f"😂 อ่านแล้วหัวเราะไม่หยุด!\n\n📖 {title}\n\n👇 กดดูเลย!\n{article_url}\n\n#ครบจัง #{category}",
            f"🤣 เรื่องนี้ต้องแชร์!\n\n✨ {title}\n\n🔗 อ่านเพิ่มเติม: {article_url}\n\n#ครบจัง #{category}",
            f"😆 รู้หรือเปล่า?\n\n📌 {title}\n\n👉 คลิกอ่านได้เลย: {article_url}\n\n#ครบจัง #{category}",
        ]
    else:
        hooks = [
            f"🙏 ข้อคิดดีๆ สำหรับวันนี้\n\n✨ {title}\n\n🌟 อ่านแล้วจิตใจสงบ:\n{article_url}\n\n#ธรรมะ #{category}",
            f"💫 สาธุ! แชร์ให้คนที่รัก\n\n🌺 {title}\n\n🔗 อ่านต่อที่: {article_url}\n\n#แสงธรรม #{category}",
        ]
    return random.choice(hooks)


def post_to_facebook_with_image(page: dict, title: str, filename: str, category: str):
    token = os.getenv(page["token_env"])
    page_id = os.getenv(page["page_id_env"])
    if not token or not page_id:
        print(f"  ⚠️ {page['name']}: ไม่พบ Token ใน .env")
        return

    article_url = f"{SITE_URL}/{filename}"
    message = generate_fb_caption(title, category, page["style"], article_url)
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    rand = random.randint(1, 9999)
    image_url = f"https://source.unsplash.com/1200x630/?{keyword}&sig={rand}"

    try:
        r = requests.post(
            f"https://graph.facebook.com/v25.0/{page_id}/photos",
            data={"message": message, "url": image_url, "access_token": token},
            timeout=30,
        )
        result = r.json()
        if "id" in result:
            print(f"  ✅ {page['name']}: โพสสำเร็จพร้อมรูป!")
        else:
            err = result.get("error", {}).get("message", "Unknown")
            print(f"  ❌ {page['name']}: {err}")
            # fallback ไม่มีรูป
            r2 = requests.post(
                f"https://graph.facebook.com/v25.0/{page_id}/feed",
                data={"message": message, "link": article_url, "access_token": token},
                timeout=30,
            )
            if "id" in r2.json():
                print(f"  ✅ {page['name']}: โพสสำเร็จ (ไม่มีรูป)")
    except Exception as e:
        print(f"  ❌ {page['name']}: {e}")


def create_safe_filename(category: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{category}_{date_str}_{rand}.html"


def generate_content_for_page(page: dict, articles_per_page: int = 3):
    print(f"\n{'='*50}")
    print(f"📄 เพจ: {page['name']} | สไตล์: {page['post_tone']}")
    print(f"{'='*50}")

    news_topics = get_thai_news_topics()
    topic_pool = []

    for news in news_topics:
        cat = match_topic_to_category(news, page["categories"])
        topic_pool.append({"title": news, "category": cat, "source": "news"})

    for cat in page["categories"]:
        for t in TOPICS_BY_STYLE.get(page["style"], {}).get(cat, []):
            topic_pool.append({"title": t, "category": cat, "source": "backup"})

    random.shuffle(topic_pool)
    selected = topic_pool[:articles_per_page]
    generated_files = []

    for item in selected:
        title = item["title"]
        category = item["category"]
        source = item["source"]
        source_label = "📰 ข่าววันนี้" if source == "news" else "📝 บทความ"

        print(f"\n  ✍️  [{category}] {title}")

        content = generate_content_with_ollama(title, category, page["style"])
        hero_image = get_unsplash_image(category)
        html = create_article_html(title, category, content, hero_image, source_label)

        filename = create_safe_filename(category)
        filepath = os.path.join(KROBJANG_PATH, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        generated_files.append(filename)
        print(f"  💾 Saved: {filename}")

        # อัปเดตหน้าหมวดอัตโนมัติ
        update_category_page(category, title, filename)

        # โพส Facebook
        post_to_facebook_with_image(page, title, filename, category)

    return generated_files


def git_push(files: list):
    try:
        os.chdir(KROBJANG_PATH)
        date_str = datetime.now().strftime("%Y-%m-%d")
        # add ทั้งไฟล์ใหม่และหน้าหมวดที่อัปเดต
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", f"auto: add {len(files)} articles + update category pages {date_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"\n✅ Pushed {len(files)} files + category pages → Vercel deploying...")
    except Exception as e:
        print(f"Git error: {e}")


if __name__ == "__main__":
    print(f"\n🚀 Auto Content Generator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Model: {OLLAMA_MODEL}\n")

    all_files = []

    for page in PAGES:
        token = os.getenv(page["token_env"])
        page_id = os.getenv(page["page_id_env"])
        if not token or not page_id:
            print(f"⚠️  ข้าม {page['name']} — ไม่พบ Token ใน .env")
            continue
        files = generate_content_for_page(page, articles_per_page=3)
        all_files.extend(files)

    if all_files:
        git_push(all_files)
        print(f"\n🎉 Done! สร้าง {len(all_files)} บทความวันนี้")
