import os
import random
import argparse
import datetime
import time
import subprocess
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

BASE_PATH = Path(r"D:\\Projects\\krubjang-site full")
ARTICLES_PATH = BASE_PATH
LOG_PATH = BASE_PATH / "agent_logs"
LOG_PATH.mkdir(exist_ok=True)

MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest"

DAILY_ARTICLE_LIMIT = 20
MAX_INTERNAL_LINKS = 3

CATEGORIES = [
    "health",
    "finance",
    "technology",
    "lifestyle",
    "comedy",
    "horoscope"
]

# =====================================================
# UTIL
# =====================================================

def log(msg: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line)

    logfile = LOG_PATH / "agent.log"
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# =====================================================
# TRENDING TOPICS (REALISTIC SIMULATION)
# =====================================================

def get_trending_topics(category: str):
    topics = {
        "health": [
            "อาหารเสริมที่คนไทยนิยม",
            "วิธีนอนหลับให้สนิท",
            "สมุนไพรไทยยอดนิยม"
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
# IMAGE AUTO (UNSPLASH STYLE)
# =====================================================

def add_auto_image(category: str) -> str:
    keywords = {
        "health": "health",
        "finance": "money",
        "technology": "technology",
        "lifestyle": "lifestyle",
        "comedy": "funny",
        "horoscope": "zodiac"
    }

    key = keywords.get(category, "news")

    return f'<img src="https://source.unsplash.com/800x400/?{key}" alt="{key}">\n'


# =====================================================
# GENERATE CONTENT
# =====================================================

def generate_article(title: str, category: str) -> str:
    prompt = f"""
เขียนบทความ SEO ภาษาไทย
หัวข้อ: {title}
หมวด: {category}

เงื่อนไข:
- ยาวประมาณ 800-1200 คำ
- อ่านง่าย
- มีหัวข้อย่อย
- ใช้ HTML
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

        image_html = add_auto_image(category)

        return image_html + content

    except Exception as e:
        log(f"Generate error: {e}")
        return "<p>Generate failed</p>"


# =====================================================
# INTERNAL LINKS BY CATEGORY
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
        import requests

        sitemap_url = "https://krobjang.vercel.app/sitemap.xml"

        ping_url = (
            "https://www.google.com/ping?"
            f"sitemap={sitemap_url}"
        )

        r = requests.get(ping_url, timeout=10)

        if r.status_code == 200:
            log("Google ping success")
        else:
            log("Google ping failed")

    except Exception as e:
        log(f"Ping error: {e}")


# =====================================================
# SITEMAP AUTO
# =====================================================

def generate_sitemap():
    try:
        sitemap_path = BASE_PATH / "sitemap.xml"

        urls = []

        for file in ARTICLES_PATH.glob("*.html"):
            url = f"https://example.com/{file.name}"
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
# SAVE FILE
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
# FACEBOOK POST (SAFE)
# =====================================================

def post_to_facebook(filename: str):
    log(f"Facebook: Post simulated for {filename}")


# =====================================================
# GIT PUSH
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
# CONTENT WORKFLOW (20 ARTICLES / DAY)
# =====================================================

def run_content():
    log("Generating content batch...")

    for _ in range(DAILY_ARTICLE_LIMIT):
        category = random.choice(CATEGORIES)

        topic = get_trending_topics(category)

        title = f"{topic} ล่าสุด"

        content = generate_article(title, category)

        content = add_internal_links(content, category)

        filename = make_filename(category)

        save_article(filename, content)

        post_to_facebook(filename)

    generate_sitemap()

    git_push()


# =====================================================
# FB CHECK
# =====================================================

def check_facebook_posts():
    log("Checking Facebook posts...")

    for file in ARTICLES_PATH.glob("*.html"):
        post_to_facebook(file.name)


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

# =====================================================
# RUN ALL WORKFLOW (FULL AUTO)
# =====================================================

def run_all():
    log("FULL AUTO START")

    fix_html_files()

    run_content()

    generate_sitemap()

    ping_google()

    git_push()

    log("FULL AUTO COMPLETE")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--content", action="store_true")
    parser.add_argument("--fb-check", action="store_true")
    parser.add_argument("--schedule", action="store_true")

    args = parser.parse_args()

    if args.fix:
        fix_html_files()

    elif args.content:
        run_content()

    elif args.fb_check:
        check_facebook_posts()

    elif args.schedule:
        scheduler()

    else:
        run_all()


if __name__ == "__main__":
    main()
