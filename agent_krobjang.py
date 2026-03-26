import os
import random
import argparse
import datetime
import time
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv

# =====================================================
# CONFIG
# =====================================================
BASE_PATH = Path(r"D:\Projects\krubjang-site full")
ARTICLES_PATH = BASE_PATH
LOG_PATH = BASE_PATH / "agent_logs"
LOG_PATH.mkdir(exist_ok=True)

load_dotenv(BASE_PATH / ".env")

MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest"
DAILY_ARTICLE_LIMIT = 20
MAX_INTERNAL_LINKS = 3

SITE_URL = os.getenv("WEBSITE_URL", "https://krobjang.vercel.app").rstrip("/")
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY")

CATEGORIES = [
    "health", "finance", "technology", "lifestyle", "comedy", "horoscope"
]

# =====================================================
# ⭐ HTML TEMPLATE แบบสมบูรณ์ (เหมือนหน้าแรก)
# =====================================================
FULL_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ครบจังดอทคอม</title>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="nav.css">
</head>
<body>
    <header>
        <div class="logo">ครบจังดอทคอม</div>
        <nav>
            <a href="index.html">🏠 หน้าแรก</a>
            <a href="news.html">📰 ข่าว</a>
            <a href="lotto.html">🎲 ตรวจหวย</a>
            <a href="horoscope.html">🔮 ดูดวง</a>
            <a href="sport.html">⚽ กีฬา</a>
            <a href="video.html">📺 วีดีโอ</a>
            <a href="ai.html">🤖 AI</a>
            <a href="games.html">🎮 เกมส์</a>
            <a href="shopping.html">🛍️ ร้านค้า</a>
            <a href="booking.html">✈️ ท่องเที่ยว</a>
            <a href="contact.html">📞 ติดต่อเรา</a>
        </nav>
    </header>

    <div class="main-layout">
        <main class="container">
            <article class="article-card">
                <h1>{title}</h1>
                <div class="meta">📅 {date} | หมวดหมู่: {category}</div>
                <div class="hero-image">
                    {hero_image}
                </div>
                <div class="content">
                    {content}
                </div>
                
                <div class="related-posts">
                    <h3>🔥 บทความที่เกี่ยวข้อง</h3>
                    {internal_links}
                </div>
            </article>
        </main>

        <aside class="sidebar">
            <div class="ad-box">
                <h4>📢 สนับสนุนเว็บไซต์</h4>
                <a href="images/promptpay.png">พร้อมเพย์</a>
                <a href="https://www.facebook.com/phongphun.phommanee">Facebook</a>
                <a href="https://youtube.com/@phongphunphommanee8045">YouTube</a>
            </div>
        </aside>
    </div>

    <footer>
        <div class="support">
            <p>สนับสนุนเว็บไซต์</p>
            <a href="images/promptpay.png">พร้อมเพย์</a>
            <a href="https://www.facebook.com/phongphun.phommanee">Facebook</a>
            <a href="https://youtube.com/@phongphunphommanee8045">YouTube</a>
        </div>
        <p>© {year} ครบจังดอทคอม</p>
    </footer>
</body>
</html>
"""

# =====================================================
# LOG
# =====================================================
def log(msg: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)
    logfile = LOG_PATH / "agent.log"
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# =====================================================
# TRENDING TOPICS
# =====================================================
def get_trending_topics(category: str):
    topics = {
        "health": ["สมุนไพรไทยยอดนิยม", "อาหารเสริมที่คนไทยนิยม", "วิธีนอนหลับให้สนิท"],
        "finance": ["วิธีเก็บเงินให้ได้ผล", "รายได้เสริมออนไลน์", "การลงทุนสำหรับมือใหม่"],
        "technology": ["AI ทำอะไรได้บ้าง", "มือถือรุ่นใหม่ล่าสุด", "เทคโนโลยีอนาคต"],
        "lifestyle": ["นิสัยคนสำเร็จ", "วิธีจัดบ้านให้น่าอยู่", "การพัฒนาตัวเอง"],
        "comedy": ["เรื่องตลกยอดฮิต", "ประโยคฮาๆ", "เรื่องขำประจำวัน"],
        "horoscope": ["ดวงความรัก", "ดวงการเงิน", "ดวงการงาน"]
    }
    return random.choice(topics.get(category, ["เรื่องน่ารู้ล่าสุด"]))

# =====================================================
# IMAGE AUTO
# =====================================================
def get_image_url(title: str, category: str) -> str:
    try:
        words = title.replace("ล่าสุด", "").split()
        keyword = words[0]
    except:
        keyword = category
    
    if UNSPLASH_KEY:
        try:
            r = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": keyword, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
                timeout=10
            )
            data = r.json()
            return data["urls"]["regular"]
        except Exception as e:
            log(f"Unsplash API error: {e}")
    
    return f"https://source.unsplash.com/800x400/?{keyword}"

# =====================================================
# GENERATE CONTENT
# =====================================================
def generate_article(title: str, category: str) -> str:
    log(f"Generating article: {title} ({category})")
    prompt = f"""
เขียนบทความ SEO ภาษาไทยแบบละเอียดมาก
หัวข้อ: {title}
หมวด: {category}
โครงสร้าง:
บทนำ
ประวัติ / ความเป็นมา
ประโยชน์
วิธีใช้
ข้อควรระวัง
สรุป
เงื่อนไข:
ยาว 1200-2000 คำ
มีหัวข้อย่อย h2 h3
ใช้ HTML Tag เฉพาะเนื้อหา (ไม่ต้องมี html, head, body)
"""
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        content = result.stdout
        return content
    except Exception as e:
        log(f"Generate error: {e}")
        return "<p>Generate failed</p>"

# =====================================================
# INTERNAL LINKS
# =====================================================
def add_internal_links(category: str) -> str:
    try:
        files = [f.name for f in ARTICLES_PATH.glob(f"{category}_*.html")]
        if not files:
            return ""

        selected = random.sample(files, min(MAX_INTERNAL_LINKS, len(files)))
        html = "<ul>\n"
        for f in selected:
            title = f.replace(".html", "").replace("_", "  ")
            html += f'<li><a href="{f}">{title}</a></li>\n'
        html += "</ul>\n"
        return html
    except Exception as e:
        log(f"Internal links error: {e}")
        return ""

# =====================================================
# ⭐ SAVE ARTICLE (รับ 5 พารามิเตอร์ + ใช้ Template)
# =====================================================
def make_filename(category: str) -> str:
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{category}_{now}_{rand}.html"

def save_article(filename: str, title: str, category: str, content: str, image_url: str):
    try:
        internal_links = add_internal_links(category)
        date_now = datetime.datetime.now().strftime("%d/%m/%Y")
        year_now = datetime.datetime.now().strftime("%Y")
        
        full_html = FULL_HTML_TEMPLATE.format(
            title=title,
            date=date_now,
            category=category,
            hero_image=f'<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;">',
            content=content,
            internal_links=internal_links,
            year=year_now
        )

        path = ARTICLES_PATH / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_html)

        log(f"Saved: {filename}")
        return filename
    except Exception as e:
        log(f"Save error: {e}")
        return None

# =====================================================
# FACEBOOK POST
# =====================================================
def post_to_facebook(filename: str, title: str, category: str):
    try:
        article_url = f"{SITE_URL}/{filename}"
        image_url = get_image_url(title, category)
        caption = f"📖 {title}\n\nอ่านบทความเพิ่มเติม 👉 {article_url}\n\n#krobjang #{category} #บทความไทย"
        
        api_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
        payload = {
            "url": image_url,
            "caption": caption,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }

        response = requests.post(api_url, data=payload, timeout=30)
        result = response.json()

        if "id" in result:
            log(f"Facebook posted OK — post id: {result['id']} ({filename})")
        else:
            error_msg = result.get("error", {}).get("message", str(result))
            log(f"Facebook post FAILED: {error_msg} ({filename})")
    except Exception as e:
        log(f"Facebook error: {e}")

# =====================================================
# SITEMAP & PING
# =====================================================
def generate_sitemap():
    try:
        sitemap_path = BASE_PATH / "sitemap.xml"
        urls = []
        for file in ARTICLES_PATH.glob("*.html"):
            url = f"{SITE_URL}/{file.name}"
            urls.append(url)

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for url in urls:
            xml += f"  <url>\n    <loc>{url}</loc>\n  </url>\n"
        xml += '</urlset>'

        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml)
        log("Sitemap generated")
    except Exception as e:
        log(f"Sitemap error: {e}")

def ping_google():
    try:
        ping_url = f"https://www.google.com/ping?sitemap={SITEMAP_URL}"
        r = requests.get(ping_url, timeout=10)
        if r.status_code == 200:
            log("Google ping success")
        else:
            log("Google ping failed")
    except Exception as e:
        log(f"Ping error: {e}")

def git_push():
    try:
        subprocess.run("git add .", shell=True)
        subprocess.run('git commit -m "auto content"', shell=True)
        subprocess.run("git push", shell=True)
        log("Git pushed")
    except Exception as e:
        log(f"Git error: {e}")

# =====================================================
# ⭐ CONTENT WORKFLOW (ส่งพารามิเตอร์ครบ)
# =====================================================
def run_content():
    log("Generating content batch...")
    for i in range(DAILY_ARTICLE_LIMIT):
        log(f"--- Article {i+1}/{DAILY_ARTICLE_LIMIT} ---")

        category = random.choice(CATEGORIES)
        topic = get_trending_topics(category)
        title = f"{topic} ล่าสุด"

        content = generate_article(title, category)
        image_url = get_image_url(title, category)
        filename = make_filename(category)

        save_article(filename, title, category, content, image_url)
        post_to_facebook(filename, title, category)

    generate_sitemap()
    ping_google()
    git_push()

# =====================================================
# SCHEDULER
# =====================================================
def scheduler():
    log("Scheduler started")
    times = ["08:00", "14:00", "20:00"]
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now in times:
            run_content()
            time.sleep(60)
        time.sleep(30)

# =====================================================
# MAIN
# =====================================================
def run_all():
    log("FULL AUTO START")
    run_content()
    log("FULL AUTO COMPLETE")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", action="store_true")
    parser.add_argument("--schedule", action="store_true")
    args = parser.parse_args()

    if args.content:
        run_content()
    elif args.schedule:
        scheduler()
    else:
        run_all()

if __name__ == "__main__":
    main()