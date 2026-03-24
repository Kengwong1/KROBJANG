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

BASE_PATH = Path(r"D:\\Projects\\krubjang-site full")
ARTICLES_PATH = BASE_PATH
LOG_PATH = BASE_PATH / "agent_logs"
LOG_PATH.mkdir(exist_ok=True)

# โหลด .env จากโฟลเดอร์โปรเจกต์
load_dotenv(BASE_PATH / ".env")

MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest"

DAILY_ARTICLE_LIMIT = 20
MAX_INTERNAL_LINKS = 3

# ดึงค่าจาก .env ทั้งหมด
SITE_URL          = os.getenv("WEBSITE_URL", "https://krobjang.vercel.app").rstrip("/")
SITEMAP_URL       = f"{SITE_URL}/sitemap.xml"
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID           = os.getenv("FB_PAGE_ID")
UNSPLASH_KEY         = os.getenv("UNSPLASH_KEY")

# =====================================================

CATEGORIES = [
    "health",
    "finance",
    "technology",
    "lifestyle",
    "comedy",
    "horoscope"
]

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
        "health": [
            "สมุนไพรไทยยอดนิยม",
            "อาหารเสริมที่คนไทยนิยม",
            "วิธีนอนหลับให้สนิท"
        ],
        "finance": [
            "วิธีเก็บเงินให้ได้ผล",
            "รายได้เสริมออนไลน์",
            "การลงทุนสำหรับมือใหม่"
        ],
        "technology": [
            "AI ทำอะไรได้บ้าง",
            "มือถือรุ่นใหม่ล่าสุด",
            "เทคโนโลยีอนาคต"
        ],
        "lifestyle": [
            "นิสัยคนสำเร็จ",
            "วิธีจัดบ้านให้น่าอยู่",
            "การพัฒนาตัวเอง"
        ],
        "comedy": [
            "เรื่องตลกยอดฮิต",
            "ประโยคฮาๆ",
            "เรื่องขำประจำวัน"
        ],
        "horoscope": [
            "ดวงความรัก",
            "ดวงการเงิน",
            "ดวงการงาน"
        ]
    }

    return random.choice(topics.get(category, ["เรื่องน่ารู้ล่าสุด"]))

# =====================================================
# IMAGE AUTO
# =====================================================

def add_auto_image(title: str, category: str) -> str:
    try:
        words = title.replace("ล่าสุด", "").split()
        keyword = words[0]
    except:
        keyword = category

    return f'<img src="https://source.unsplash.com/800x400/?{keyword}" alt="{keyword}">\n'


def get_image_url(title: str, category: str) -> str:
    """คืน URL รูปภาพจาก Unsplash API สำหรับโพสต์ Facebook"""
    try:
        words = title.replace("ล่าสุด", "").split()
        keyword = words[0]
    except:
        keyword = category

    # ถ้ามี Unsplash key ใช้ API จริง (ได้รูปแน่นอน ไม่ redirect)
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

    # fallback ถ้าไม่มี key
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
1. บทนำ
2. ประวัติ / ความเป็นมา
3. ประโยชน์
4. วิธีใช้
5. ข้อควรระวัง
6. สรุป

เงื่อนไข:
- ยาว 1200-2000 คำ
- มีหัวข้อย่อย h2 h3
- ใช้ HTML เท่านั้น
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

        image_html = add_auto_image(title, category)

        return image_html + content

    except Exception as e:
        log(f"Generate error: {e}")
        return "<p>Generate failed</p>"

# =====================================================
# INTERNAL LINKS
# =====================================================

def add_internal_links(content: str, category: str) -> str:
    try:
        files = [
            f.name for f in ARTICLES_PATH.glob(f"{category}_*.html")
        ]

        if not files:
            return content

        selected = random.sample(
            files,
            min(MAX_INTERNAL_LINKS, len(files))
        )

        html = "\n<hr>\n<h3>บทความที่เกี่ยวข้อง</h3>\n<ul>\n"

        for f in selected:
            title = f.replace(".html", "").replace("_", " ")
            html += f'<li><a href="{f}">{title}</a></li>\n'

        html += "</ul>\n"

        return content + html

    except Exception as e:
        log(f"Internal links error: {e}")
        return content

# =====================================================
# PING GOOGLE
# =====================================================

def ping_google():
    try:
        ping_url = (
            "https://www.google.com/ping?"
            f"sitemap={SITEMAP_URL}"
        )

        r = requests.get(ping_url, timeout=10)

        if r.status_code == 200:
            log("Google ping success")
        else:
            log("Google ping failed")

    except Exception as e:
        log(f"Ping error: {e}")

# =====================================================
# SITEMAP
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
            xml += "  <url>\n"
            xml += f"    <loc>{url}</loc>\n"
            xml += "  </url>\n"

        xml += '</urlset>'

        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(xml)

        log("Sitemap generated")

    except Exception as e:
        log(f"Sitemap error: {e}")

# =====================================================
# SAVE
# =====================================================

def make_filename(category: str) -> str:
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{category}_{now}_{rand}.html"


def save_article(filename: str, content: str):
    path = ARTICLES_PATH / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"Saved: {filename}")

# =====================================================
# FACEBOOK  ← แก้ใหม่ทั้งหมด โพสต์จริงพร้อมรูป
# =====================================================

def post_to_facebook(filename: str, title: str, category: str):
    """
    โพสต์บทความไปยัง Facebook Page พร้อมรูปภาพ
    ใช้ Facebook Graph API endpoint: /PAGE_ID/photos
    """
    try:
        article_url = f"{SITE_URL}/{filename}"
        image_url   = get_image_url(title, category)

        # ข้อความ caption ที่จะโพสต์
        caption = (
            f"📖 {title}\n\n"
            f"อ่านบทความเพิ่มเติม 👉 {article_url}\n\n"
            f"#krobjang #{category} #บทความไทย"
        )

        # โพสต์รูป + caption ด้วย /photos endpoint
        # (Facebook จะสร้าง post พร้อมรูปให้อัตโนมัติ)
        api_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"

        payload = {
            "url":          image_url,
            "caption":      caption,
            "access_token": FB_PAGE_ACCESS_TOKEN,
        }

        response = requests.post(api_url, data=payload, timeout=30)
        result   = response.json()

        if "id" in result:
            log(f"Facebook posted OK — post id: {result['id']} ({filename})")
        else:
            # แสดง error จาก API ให้ชัดเจน
            error_msg = result.get("error", {}).get("message", str(result))
            log(f"Facebook post FAILED: {error_msg} ({filename})")

    except Exception as e:
        log(f"Facebook error: {e}")

# =====================================================
# GIT
# =====================================================

def git_push():
    try:
        subprocess.run("git add .", shell=True)
        subprocess.run("git commit -m \"auto content\"", shell=True)
        subprocess.run("git push", shell=True)
        log("Git pushed")
    except Exception as e:
        log(f"Git error: {e}")

# =====================================================
# FIX HTML
# =====================================================

def fix_html_files():
    log("Checking HTML files...")

    for file in ARTICLES_PATH.glob("*.html"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()

            if "</html>" not in content:
                content += "\n</html>"

                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)

                log(f"Fixed: {file.name}")

        except Exception as e:
            log(f"Fix error: {e}")

    git_push()

# =====================================================
# CONTENT WORKFLOW
# =====================================================

def run_content():
    log("Generating content batch...")

    for i in range(DAILY_ARTICLE_LIMIT):
        log(f"--- Article {i+1}/{DAILY_ARTICLE_LIMIT} ---")

        category = random.choice(CATEGORIES)
        topic    = get_trending_topics(category)
        title    = f"{topic} ล่าสุด"

        content  = generate_article(title, category)
        content  = add_internal_links(content, category)

        filename = make_filename(category)

        save_article(filename, content)

        # ← ส่ง title + category ด้วยเพื่อใช้สร้างรูปและ caption
        post_to_facebook(filename, title, category)

    generate_sitemap()
    ping_google()
    git_push()

# =====================================================
# SCHEDULER
# =====================================================

def scheduler():
    log("Scheduler started")

    times = [
        "08:00",
        "14:00",
        "20:00"
    ]

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

    fix_html_files()
    run_content()

    log("FULL AUTO COMPLETE")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--fix",      action="store_true")
    parser.add_argument("--content",  action="store_true")
    parser.add_argument("--schedule", action="store_true")

    args = parser.parse_args()

    if args.fix:
        fix_html_files()

    elif args.content:
        run_content()

    elif args.schedule:
        scheduler()

    else:
        run_all()


if __name__ == "__main__":
    main()
