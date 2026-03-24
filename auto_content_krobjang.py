import requests
import os
import random
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()

OLLAMA_MODEL = "PhromAI:latest"
KROBJANG_PATH = r"D:\Projects\krubjang-site full"
OLLAMA_URL = "http://localhost:11434/api/generate"
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://krobjang.vercel.app")
FB_PAGE_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "126444234360863")

CATEGORY_TO_EMOJI = {
    "ai": "🤖", "finance": "💰", "horoscope": "⭐", "health": "💚", "lifestyle": "🌟",
}

CATEGORY_IMAGES = {
    "ai": "artificial+intelligence+technology",
    "finance": "money+finance+investment",
    "horoscope": "stars+astrology+sky",
    "health": "healthy+lifestyle+wellness",
    "lifestyle": "lifestyle+modern+living",
}

TOPICS = {
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


def get_trending_topics(max_topics: int = 5) -> list:
    """ดึง trending topics จาก Google Trends ประเทศไทย"""
    try:
        pytrends = TrendReq(hl='th-TH', tz=420, timeout=(10, 30))
        trending_df = pytrends.trending_searches(pn='thailand')
        topics = trending_df[0].tolist()[:max_topics]
        print(f"  Trending topics: {topics}")
        return topics
    except Exception as e:
        print(f"  Trends error: {e}")
        return []

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ครบจังดอทคอม</title>
  <meta name="description" content="{description}">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2068902667667616" crossorigin="anonymous"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: sans-serif; background: #f5f5f5; color: #333; line-height: 1.8; }}
    header {{ background: #1a73e8; padding: 12px 20px; }}
    header nav a {{ color: white; text-decoration: none; margin-right: 16px; font-size: 15px; }}
    .article-container {{ max-width: 820px; margin: 30px auto; padding: 0 16px; }}
    article {{ background: white; border-radius: 12px; padding: 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
    h1 {{ font-size: 26px; color: #1a1a1a; margin-bottom: 8px; line-height: 1.4; }}
    h2 {{ font-size: 20px; color: #1a73e8; margin: 24px 0 10px; }}
    p {{ margin-bottom: 16px; font-size: 16px; }}
    ul, ol {{ margin: 12px 0 16px 24px; }}
    li {{ margin-bottom: 8px; font-size: 16px; }}
    .meta {{ color: #888; font-size: 13px; margin-bottom: 20px; }}
    .hero-image {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 10px; margin-bottom: 24px; }}
    footer {{ text-align: center; padding: 20px; color: #888; font-size: 13px; margin-top: 30px; }}
  </style>
</head>
<body>
  <main class="article-container">
    <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    <article>
      <h1>{title}</h1>
      <p class="meta">อัปเดต: {date} | หมวด: {category}</p>
      {hero_image}
      {content}
    </article>
    <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2068902667667616"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </main>
</body>
</html>"""


def get_unsplash_image(category: str) -> str:
    keyword = CATEGORY_IMAGES.get(category, "thailand")
    return f'<img class="hero-image" src="https://source.unsplash.com/800x400/?{keyword}" alt="{category}" loading="lazy">'


def generate_content_with_ollama(title: str, category: str) -> str:
    prompt = f"""เขียนบทความภาษาไทยเรื่อง "{title}"
หมวด: {category}
ความยาว: 500-800 คำ
รูปแบบ: HTML ใช้แท็ก <h2> <p> <ul> <li>
ห้ามใส่: DOCTYPE html head body
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


def generate_caption_with_ollama(title: str, category: str) -> str:
    emoji = CATEGORY_TO_EMOJI.get(category, "📌")
    prompt = f"""เขียน caption Facebook ภาษาไทยสำหรับบทความเรื่อง "{title}"
ความยาว: 3-4 บรรทัด สไตล์: น่าสนใจ กระตุ้นให้คลิก ใช้ emoji บ้าง
ลงท้ายด้วย: อ่านต่อได้ที่ลิงก์ด้านล่างครับ
ตอบแค่ caption เท่านั้น"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.8, "num_predict": 200}},
            timeout=120,
        )
        if response.status_code == 200:
            return f"{emoji} {response.json().get('response', '')}"
        return f"{emoji} {title}\n\nอ่านต่อได้ที่ลิงก์ด้านล่างครับ"
    except Exception:
        return f"{emoji} {title}\n\nอ่านต่อได้ที่ลิงก์ด้านล่างครับ"


def post_to_facebook(title: str, category: str, filename: str) -> bool:
    if not FB_PAGE_TOKEN:
        print("  Facebook: ไม่มี token ข้ามไปครับ")
        return False
    try:
        article_url = f"{WEBSITE_URL}/{filename}"
        caption = generate_caption_with_ollama(title, category)
        message = f"{caption}\n\n🔗 {article_url}"
        resp = requests.post(
            f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed",
            data={"message": message, "access_token": FB_PAGE_TOKEN},
            timeout=30,
        )
        if resp.status_code == 200:
            print(f"  Facebook: โพสสำเร็จ! ID: {resp.json().get('id', '')}")
            return True
        else:
            print(f"  Facebook error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"  Facebook error: {e}")
        return False


def create_safe_filename(category: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = random.randint(1000, 9999)
    return f"{category}_{date_str}_{rand}.html"


def generate_daily_content(articles_per_run: int = 5):
    print(f"\n{'='*50}")
    print(f"Auto Content Generator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Model: {OLLAMA_MODEL}")
    print(f"{'='*50}\n")

    selected = []

    # ดึง trending topics ก่อน
    trending = get_trending_topics(max_topics=3)
    for trend in trending:
        # จัดหมวดหมู่ trending topic อัตโนมัติ
        if any(w in trend for w in ['หุ้น', 'เงิน', 'ลงทุน', 'ธนาคาร', 'บาท']):
            cat = 'finance'
        elif any(w in trend for w in ['ดวง', 'ราศี', 'หวย', 'เลข', 'โชค']):
            cat = 'horoscope'
        elif any(w in trend for w in ['AI', 'แอป', 'เทค', 'iPhone', 'Samsung']):
            cat = 'ai'
        elif any(w in trend for w in ['สุขภาพ', 'โรค', 'ยา', 'หมอ', 'ออกกำลัง']):
            cat = 'health'
        else:
            cat = 'lifestyle'
        selected.append((cat, f"{trend} ล่าสุด {datetime.now().year}"))

    # เติมด้วย topics ที่กำหนดไว้ให้ครบ
    categories = list(TOPICS.keys())
    random.shuffle(categories)
    remaining = articles_per_run - len(selected)
    for cat in categories[:remaining]:
        topic = random.choice(TOPICS[cat])
        selected.append((cat, topic))

    generated_files = []
    for category, title in selected:
        print(f"Generating: [{category}] {title}")
        content = generate_content_with_ollama(title, category)
        hero_image = get_unsplash_image(category)
        html = HTML_TEMPLATE.format(
            title=title, description=title[:150],
            date=datetime.now().strftime("%d/%m/%Y"),
            category=category, hero_image=hero_image, content=content,
        )
        filename = create_safe_filename(category)
        filepath = os.path.join(KROBJANG_PATH, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        generated_files.append(filename)
        print(f"  Saved: {filename}")
        post_to_facebook(title, category, filename)

    return generated_files


def git_push(files: list):
    try:
        os.chdir(KROBJANG_PATH)
        date_str = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(["git", "add"] + files, check=True)
        subprocess.run(["git", "commit", "-m", f"auto: add {len(files)} articles {date_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"\nPushed {len(files)} files → Vercel deploying...")
    except Exception as e:
        print(f"Git error: {e}")


if __name__ == "__main__":
    files = generate_daily_content(articles_per_run=5)
    if files:
        git_push(files)
        print(f"\nDone! {len(files)} articles generated today")
