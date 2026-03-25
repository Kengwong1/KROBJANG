import requests
import os
import random
from datetime import datetime
from dotenv import load_dotenv

# โหลดค่าจาก .env (ถ้ามี)
load_dotenv()

# ================= CONFIG =================
# ตรวจสอบชื่อโมเดลในเครื่องคุณ (เช่น qwen2.5-coder:latest หรือ PhromAI:latest)
OLLAMA_MODEL = "PhromAI:latest" 
OLLAMA_URL   = "http://localhost:11434/api/generate"

# พาธโปรเจกต์ของคุณ
KROBJANG_PATH = r"D:\Projects\krubjang-site full"

# ================= HTML TEMPLATE (ปรับปรุง Layout ให้เหมือนหน้าแรก) =================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | ครบจังดอทคอม</title>
  <meta name="description" content="{description}">

  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <div class="logo">ครบจังดอทคอม</div>
  </header>

  <nav class="main-nav">
    <div class="nav-wrap">
      <a href="index.html"><i class="fas fa-home" style="color: #45B7D1;"></i> หน้าแรก</a>
      <a href="news.html"><i class="fas fa-bolt" style="color: #FF6B6B;"></i> ข่าว</a>
      <a href="ai.html"><i class="fas fa-robot" style="color: #2EC4B6;"></i> AI</a>
      <a href="finance.html"><i class="fas fa-coins" style="color: #F59E0B;"></i> การเงิน</a>
      <a href="horoscope.html"><i class="fas fa-star" style="color: #6A4C93;"></i> ดูดวง</a>
    </div>
  </nav>

  <div class="container">
    <div class="content-area">
      <div class="section" style="background: white; border-radius: 18px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        
        <main class="article-container">
          <article>
            <h1 style="color: #1e40af; font-size: 2rem; margin-bottom: 15px; line-height: 1.4;">{title}</h1>
            
            <div class="meta" style="color: #64748b; font-size: 0.9rem; margin-bottom: 25px; border-bottom: 1px solid #f1f5f9; padding-bottom: 15px;">
              <i class="far fa-calendar-alt"></i> วันที่: {date} | <i class="fas fa-tag"></i> หมวดหมู่: {category}
            </div>

            <div class="hero-image-wrapper" style="text-align: center; margin-bottom: 30px;">
              {hero_image}
            </div>

            <div class="content" style="line-height: 1.8; font-size: 1.1rem; color: #334155;">
              {content}
            </div>

            <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 40px 0;">

            <section class="related">
              <h3 style="color: #1e40af; margin-bottom: 20px;"><i class="fas fa-fire" style="color: #FF6B6B;"></i> บทความที่น่าสนใจ</h3>
              <ul style="list-style: none; padding-left: 0; display: grid; gap: 10px;">
                <li><a href="index.html" style="text-decoration: none; color: #475569;"><i class="fas fa-chevron-right" style="color: #45B7D1; font-size: 0.8rem;"></i> กลับไปหน้าหลัก</a></li>
              </ul>
            </section>
          </article>
        </main>

      </div>
    </div>

    <aside class="sidebar">
      <div class="ad-section" style="background: white; padding: 20px; border-radius: 18px; margin-bottom: 20px;">
        <h2 style="font-size: 1.1rem; margin-bottom: 15px; color: #1e40af;">
          <i class="fas fa-ad"></i> สนับสนุนเว็บไซต์
        </h2>
        <div style="background: #f8fafc; min-height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 12px; border: 2px dashed #e2e8f0;">
          <p style="color: #94a3b8;">พื้นที่โฆษณา</p>
        </div>
      </div>

      <div class="ad-section" style="background: white; padding: 20px; border-radius: 18px;">
        <h2 style="font-size: 1.1rem; margin-bottom: 15px; color: #1e40af;">
          <i class="fas fa-heart" style="color: #FF6B6B;"></i> สนับสนุนเรา
        </h2>
        <div style="text-align: center;">
          <p style="font-size: 0.9rem; margin-bottom: 10px;">ขอบคุณทุกการสนับสนุนค่ะ</p>
          <img src="https://krobjang.vercel.app/images/promptpay.png" alt="QR PromptPay" style="max-width: 100%; border-radius: 12px;">
        </div>
      </div>
    </aside>
  </div>

  <footer style="background: #1e40af; color: white; padding: 30px; text-align: center; margin-top: 50px;">
    <p>© 2026 ครบจังดอทคอม | เว็บเดียวครบทุกเรื่อง</p>
  </footer>
</body>
</html>
"""

# ================= FUNCTIONS =================

def generate_content_with_ollama(title):
    prompt = f"""
    เขียนบทความภาษาไทยเชิงสาระเรื่อง "{title}" 
    ให้เน้นเนื้อหาที่เป็นประโยชน์ อ่านง่าย 
    จัดรูปแบบโดยใช้เฉพาะแท็ก HTML ต่อไปนี้: <h2>, <p>, <ul>, <li>
    ความยาวประมาณ 500 คำ
    """
    try:
        print(f"กำลังติดต่อ Ollama (Model: {OLLAMA_MODEL})...")
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=180 # เพิ่มเวลา Timeout เผื่อ AI ตอบช้า
        )
        if response.status_code == 200:
            return response.json().get("response", "")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ Ollama: {e}")
    
    return "<p>ขออภัยค่ะ เนื้อหาส่วนนี้กำลังปรับปรุง</p>"

def get_image():
    # สุ่มรูปภาพจาก Unsplash ให้ดูสวยงาม
    return '<img class="hero-image" src="https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=800&q=80" style="width: 100%; border-radius: 15px;" />'

def save_article(title, content):
    # สร้างชื่อไฟล์จาก Timestamp
    filename = f"article_{int(datetime.now().timestamp())}.html"
    path = os.path.join(KROBJANG_PATH, filename)

    full_html = HTML_TEMPLATE.format(
        title=title,
        description=f"อ่านเรื่อง {title} ได้ที่ครบจังดอทคอม",
        date=datetime.now().strftime("%d/%m/%Y"),
        category="บทความพิเศษ",
        hero_image=get_image(),
        content=content,
        year=datetime.now().year
    )

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"✅ บันทึกไฟล์สำเร็จ: {path}")
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกไฟล์ได้: {e}")

# ================= MAIN EXECUTION =================

if __name__ == "__main__":
    print("\n" + "="*30)
    print("  KROBJANG AUTO CONTENT START")
    print("="*30)

    # ทดสอบสร้างบทความ
    topic = "เทรนด์ AI ปี 2026 ที่จะเปลี่ยนชีวิตคุณ"
    print(f"หัวข้อ: {topic}")

    article_content = generate_content_with_ollama(topic)
    
    if article_content:
        save_article(topic, article_content)
    
    print("\n" + "="*30)
    print("  การทำงานเสร็จสิ้นค่ะ")
    print("="*30)