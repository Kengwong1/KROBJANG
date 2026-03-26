import os
import time
import datetime
import requests
import feedparser
from pathlib import Path
from bs4 import BeautifulSoup

# --- ตั้งค่าพื้นฐาน (ดึงมาจากไฟล์เก่าของคุณ) ---
BASE_PATH = Path(r"D:\Projects\krubjang-site full")
OLLAMA_URL = "http://localhost:11434/api/generate"
# เลือกชื่อโมเดลที่คุณใช้บ่อยที่สุด (เช่น Typhoon หรือ PhromAI)
MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest" 

# หมวดหมู่ที่มีในเว็บของคุณ
CATEGORIES = ["health", "finance", "technology", "lifestyle", "comedy", "horoscope"]

print("✅ สเต็ป 2 สำเร็จ: ตั้งค่าเรียบร้อยแล้วค่ะ")

# --- ฟังก์ชันบันทึก Log (เอามาจากไฟล์เก่า) ---
def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# --- 1. ฟังก์ชัน "ตา" (ไปดึงเทรนด์จริงจาก Google และ Pantip) ---
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

    return list(set(all_trends)) # ลบหัวข้อที่ซ้ำออก

print("✅ สเต็ป 3 สำเร็จ: ระบบดึงเทรนด์พร้อมทำงานแล้วค่ะ")

# --- 2. ฟังก์ชัน "สมอง" (ให้ Ollama เลือกหัวข้อและวางแผน) ---
def ask_ollama_to_plan(trend_list):
    log("🧠 กำลังส่งเทรนด์ให้ AI ช่วยวิเคราะห์และเลือกหัวข้อ...")
    
    prompt = f"""
    จากรายการหัวข้อที่กำลังดังต่อไปนี้: {", ".join(trend_list)}
    
    คำสั่ง:
    1. เลือกหัวข้อที่น่าสนใจที่สุดมา 1 หัวข้อเพื่อเขียนบทความลงเว็บ
    2. จัดหมวดหมู่ที่เหมาะสมจากรายการนี้เท่านั้น: {", ".join(CATEGORIES)}
    3. ระบุตำแหน่งความสำคัญบนหน้าเว็บ (Top, Middle, Bottom)
    
    ตอบกลับในรูปแบบนี้เท่านั้น (ห้ามมีคำอื่น): หัวข้อ | หมวดหมู่ | ตำแหน่ง
    """
    
    try:
        # ใช้ requests ติดต่อ Ollama เหมือนในไฟล์ auto_content_krobjang.py ของคุณค่ะ
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
        return "สรุปข่าวเด่นวันนี้ | lifestyle | Middle"

print("✅ สเต็ป 4 สำเร็จ: สมอง AI พร้อมสั่งการแล้วค่ะ")

# --- 3. ฟังก์ชัน "มือ" (สั่งเขียนเนื้อหาและหาภาพ) ---
def generate_article_content(title, category):
    log(f"✍️ กำลังเขียนบทความหัวข้อ: {title}...")
    prompt = f"เขียนบทความ SEO ภาษาไทยเรื่อง {title} หมวด {category} ให้ละเอียด มีหัวข้อ h2, h3 และใช้ HTML Tag เฉพาะเนื้อหา (ไม่ต้องมี <html> หรือ <body>)"
    
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME, "prompt": prompt, "stream": False
        }, timeout=300) # ให้เวลา AI คิด 5 นาที
        return response.json().get("response", "")
    except Exception as e:
        log(f"❌ Generate Content Error: {e}")
        return "<p>ขออภัยค่ะ เนื้อหาส่วนนี้กำลังปรับปรุง</p>"

def get_image_url(title, category):
    # ใช้รูปภาพจาก Unsplash ตามหัวข้อที่ AI เลือก
    keyword = title.split()[0] if title else category
    return f"https://source.unsplash.com/800x400/?{keyword}"

print("✅ สเต็ป 5 สำเร็จ: ระบบเขียนบทความพร้อมแล้วค่ะ")

# --- HTML Template สำหรับหน้าบทความ (ปรับปรุงจากต้นฉบับของคุณ) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | ครบจังดอทคอม</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header><div class="logo">ครบจังดอทคอม</div></header>
    <main class="container">
        <article>
            <h1>{title}</h1>
            <div class="meta">📅 {date} | หมวดหมู่: {category}</div>
            <div class="hero-image">{hero_image}</div>
            <div class="content">{content}</div>
        </article>
    </main>
    <footer><p>© {year} ครบจังดอทคอม</p></footer>
</body>
</html>
"""

def save_article(title, category, content, image_url):
    # สร้างชื่อไฟล์อัตโนมัติ
    filename = f"{category}_{int(time.time())}.html"
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")
    
    # นำข้อมูลไปหยอดใส่ Template
    full_html = HTML_TEMPLATE.format(
        title=title,
        date=date_str,
        category=category,
        hero_image=f'<img src="{image_url}" style="width:100%; border-radius:15px;">',
        content=content,
        year=datetime.datetime.now().year
    )
    
    path = BASE_PATH / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(full_html)
    
    log(f"💾 บันทึกไฟล์สำเร็จ: {filename}")
    return filename

print("✅ สเต็ป 6 สำเร็จ: ระบบ Template และการบันทึกไฟล์พร้อมแล้วค่ะ")

# --- 4. ฟังก์ชันอัตโนมัติ (อัปเดตระบบออนไลน์) ---
def update_online():
    log("⚙️ กำลังอัปเดตระบบ Sitemap และส่งไฟล์ขึ้น GitHub...")
    try:
        # ระบบจัดการ Git อัตโนมัติที่คุณเคยทำไว้
        import subprocess
        os.chdir(BASE_PATH)
        subprocess.run("git add .", shell=True)
        subprocess.run('git commit -m "Auto update by Super Agent"', shell=True)
        subprocess.run("git push", shell=True)
        log("🚀 อัปโหลดไฟล์ขึ้น GitHub สำเร็จแล้วค่ะ")
    except Exception as e:
        log(f"❌ ระบบ Git ขัดข้อง: {e}")

# --- 5. ตัวควบคุมหลัก (Master Workflow) ---
def main():
    log("🌟 เริ่มต้นระบบ Super Agent อัจฉริยะ...")
    
    # 1. ค้นหาเทรนด์ล่าสุด
    trends = get_live_trends()
    
    # 2. ให้ AI วิเคราะห์และเลือกหัวข้อที่ดีที่สุด
    plan = ask_ollama_to_plan(trends)
    
    # 3. ตรวจสอบข้อมูลและเริ่มงาน
    if "|" in plan:
        try:
            title, category, position = [x.strip() for x in plan.split("|")]
            
            # 4. AI เขียนเนื้อหาบทความ
            content = generate_article_content(title, category)
            
            # 5. ค้นหาภาพประกอบ
            image_url = get_image_url(title, category)
            
            # 6. บันทึกเป็นหน้าเว็บ HTML
            save_article(title, category, content, image_url)
            
            # 7. ดันขึ้นเว็บออนไลน์ทันที
            update_online()
            
            log(f"🎊 ทำงานเสร็จสมบูรณ์! สร้างบทความเรื่อง: {title}")
        except Exception as e:
            log(f"❌ เกิดข้อผิดพลาดในขั้นตอนรวมงาน: {e}")
    else:
        log("⚠️ AI วางแผนไม่สำเร็จ (รูปแบบข้อมูลผิด) ขอยกเลิกงานรอบนี้ค่ะ")

if __name__ == "__main__":
    main()