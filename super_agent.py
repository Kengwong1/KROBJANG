import os
import time
import datetime
import requests
import feedparser
from pathlib import Path
from bs4 import BeautifulSoup

# --- ⚙️ การตั้งค่าพื้นฐาน ---
BASE_PATH = Path(r"D:\Projects\krubjang-site full")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest" 

CATEGORIES = ["health", "finance", "technology", "lifestyle", "comedy", "horoscope"]

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# --- 1. ฟังก์ชันดึงเทรนด์ (The Eye) ---
def get_live_trends():
    all_trends = []
    log("🔍 กำลังค้นหาเทรนด์ล่าสุดจากโลกออนไลน์...")

    # ดึงจาก Google Trends (ผ่าน RSS)
    try:
        feed = feedparser.parse("https://trends.google.com/trends/trendingsearches/daily/rss?geo=TH")
        for entry in feed.entries[:10]:
            all_trends.append(entry.title)
    except Exception as e:
        log(f"❌ Google Trends Error: {e}")

    # ดึงจาก Pantip (หัวข้อกระทู้ฮิต)
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://pantip.com/forum/featured", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.find_all('h2', limit=5):
            all_trends.append(tag.get_text().strip())
    except Exception as e:
        log(f"❌ Pantip Error: {e}")

    return list(set(all_trends))

# --- 2. ฟังก์ชันวางแผนบทความ (The Brain - ปรับปรุงใหม่) ---
def ask_ollama_to_plan(trend_list):
    log("🧠 กำลังส่งเทรนด์ให้ AI ช่วยวิเคราะห์และเลือกหัวข้อ...")
    
    prompt = f"""
    จากรายการหัวข้อดังต่อไปนี้: {", ".join(trend_list)}
    
    คำสั่ง:
    1. เลือกหัวข้อที่น่าสนใจและมีประโยชน์ที่สุดมา 1 หัวข้อ
    2. **ข้อห้ามเด็ดขาด**: ห้ามเลือกหัวข้อที่เป็นข้อความ Error, หน้าเว็บล่ม, หรือข้อความระบบ (เช่น 'หน้านี้ไม่พร้อมใช้งาน', '404', 'Error')
    3. จัดหมวดหมู่ที่เหมาะสมจากรายการนี้เท่านั้น: {", ".join(CATEGORIES)}
    4. ระบุตำแหน่งความสำคัญบนหน้าเว็บ (Top, Middle, Bottom)
    
    ตอบกลับในรูปแบบนี้เท่านั้น (ห้ามมีคำอื่น): หัวข้อ | หมวดหมู่ | ตำแหน่ง
    """
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME, 
            "prompt": prompt, 
            "stream": False
        }, timeout=120)
        
        result = response.json().get("response", "").strip()
        log(f"🤖 AI วางแผนมาให้ว่า: {result}")
        return result
    except Exception as e:
        log(f"❌ Ollama Planning Error: {e}")
        return "สรุปสาระน่ารู้ประจำวัน | lifestyle | Middle"

# --- 3. ฟังก์ชันเขียนเนื้อหา (The Hand - ปรับปรุง SEO) ---
def generate_article_content(title, category):
    log(f"✍️ กำลังเขียนบทความหัวข้อ: {title}...")
    
    prompt = f"""
    คุณคือผู้เชี่ยวชาญด้านการเขียนบทความ SEO ภาษาไทย
    จงเขียนบทความเรื่อง: "{title}" หมวดหมู่: {category}
    
    ข้อกำหนด:
    - เขียนเนื้อหาที่เจาะลึก น่าสนใจ และให้สาระแก่ผู้อ่าน
    - ใช้ HTML Tag: <h2> สำหรับหัวข้อหลัก, <h3> สำหรับหัวข้อย่อย และ <p> สำหรับเนื้อหา
    - ห้ามใส่ Tag <html>, <body> หรือ <head> มาในคำตอบ
    - ความยาวบทความอย่างน้อย 500 คำ
    """
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME, "prompt": prompt, "stream": False
        }, timeout=300)
        return response.json().get("response", "")
    except Exception as e:
        log(f"❌ Generate Content Error: {e}")
        return "<p>ขออภัยค่ะ เนื้อหาส่วนนี้กำลังปรับปรุง โปรดรอสักครู่</p>"

def get_image_url(title, category):
    keyword = title.split()[0] if title else category
    return f"https://source.unsplash.com/800x400/?{keyword}"

# --- 4. ระบบจัดการไฟล์และ HTML Template ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ครบจังดอทคอม</title>
    <style>
        body {{ font-family: 'Tahoma', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f4f4f4; }}
        .container {{ max-width: 800px; margin: 20px auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        header {{ background: #333; color: #fff; padding: 10px 0; text-align: center; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .content img {{ max-width: 100%; height: auto; border-radius: 10px; margin: 20px 0; }}
        footer {{ text-align: center; padding: 20px; font-size: 0.8em; color: #777; }}
    </style>
</head>
<body>
    <header><h1>ครบจังดอทคอม</h1></header>
    <main class="container">
        <article>
            <h1>{title}</h1>
            <p class="meta">📅 {date} | 📂 หมวดหมู่: {category}</p>
            <div class="hero-image">{hero_image}</div>
            <div class="content">{content}</div>
        </article>
    </main>
    <footer><p>© {year} ครบจังดอทคอม - ระบบ Super Agent อัตโนมัติ</p></footer>
</body>
</html>
"""

def save_article(title, category, content, image_url):
    filename = f"{category}_{int(time.time())}.html"
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")
    
    full_html = HTML_TEMPLATE.format(
        title=title,
        date=date_str,
        category=category,
        hero_image=f'<img src="{image_url}" alt="{title}">',
        content=content,
        year=datetime.datetime.now().year
    )
    
    path = BASE_PATH / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    log(f"💾 บันทึกไฟล์สำเร็จ: {filename}")
    return filename

# --- 5. ระบบอัปเดตออนไลน์ (Git) ---
def update_online():
    log("⚙️ กำลังส่งไฟล์ขึ้น GitHub...")
    try:
        import subprocess
        os.chdir(BASE_PATH)
        subprocess.run("git add .", shell=True)
        subprocess.run('git commit -m "Auto update by Super Agent"', shell=True)
        subprocess.run("git push", shell=True)
        log("🚀 อัปโหลดไฟล์ขึ้น GitHub สำเร็จแล้วค่ะ")
    except Exception as e:
        log(f"❌ ระบบ Git ขัดข้อง: {e}")

# --- 6. Master Workflow ---
def main():
    log("🌟 เริ่มต้นระบบ Super Agent อัจฉริยะ...")
    
    trends = get_live_trends()
    if not trends:
        log("⚠️ ไม่พบเทรนด์ใหม่ในขณะนี้")
        return

    plan = ask_ollama_to_plan(trends)
    
    if "|" in plan:
        try:
            parts = [x.strip() for x in plan.split("|")]
            if len(parts) >= 2:
                title, category = parts[0], parts[1]
                
                content = generate_article_content(title, category)
                image_url = get_image_url(title, category)
                save_article(title, category, content, image_url)
                update_online()
                
                log(f"🎊 ทำงานเสร็จสมบูรณ์! สร้างบทความเรื่อง: {title}")
        except Exception as e:
            log(f"❌ เกิดข้อผิดพลาดในขั้นตอนรวมงาน: {e}")
    else:
        log("⚠️ AI ตอบกลับในรูปแบบที่ไม่ถูกต้อง ขอยกเลิกงานรอบนี้ค่ะ")

if __name__ == "__main__":
    main()