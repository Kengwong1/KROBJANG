# auto_content_krobjang.py — ADVANCED VERSION (SEO + 20 POSTS PER RUN)
# เพิ่มแล้ว:
# - โมเดลภาษาไทยที่เหมาะสม
# - SEO keyword + meta description
# - สร้างบทความ 20 บทต่อรอบอัตโนมัติ

import requests
from datetime import datetime
from pathlib import Path
import random

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

MODEL_NAME = "scb10x/llama3.1-typhoon2-8b-instruct:latest"
OUTPUT_DIR = Path(__file__).resolve().parent

# จำนวนบทความต่อการรัน 1 ครั้ง
POSTS_PER_RUN = 20

# หมวดและหัวข้อ
CATEGORIES = {
    "comedy": [
        "5 ประโยคที่คนไทยพูดแล้วฝรั่งงง",
        "เรื่องฮาในออฟฟิศ",
        "นิสัยคนไทยที่ทำให้ต่างชาติขำ",
        "เรื่องตลกในชีวิตประจำวัน"
    ],
    "health": [
        "สมุนไพรไทยที่ช่วยเสริมภูมิคุ้มกัน",
        "อาหารที่ช่วยให้นอนหลับดีขึ้น",
        "วิธีดูแลสุขภาพง่ายๆ",
        "อาหารที่ควรกินทุกวัน"
    ],
    "horoscope": [
        "ดวงความรักราศีต่างๆ",
        "ราศีไหนการเงินดี",
        "เคล็ดลับเสริมดวง",
        "ดวงวันนี้"
    ]
}

# ─────────────────────────────────────────────
# SEO KEYWORDS
# ─────────────────────────────────────────────

def build_keywords(topic: str):

    words = topic.split()

    keywords = [
        topic,
        f"{topic} ล่าสุด",
        f"{topic} 2569",
        f"{topic} วันนี้",
        f"{topic} วิธี",
    ]

    return ", ".join(keywords[:5])


# ─────────────────────────────────────────────
# PROMPT TEMPLATE
# ─────────────────────────────────────────────

def build_prompt(category: str, topic: str) -> str:

    base = f"""
เขียนบทความภาษาไทยคุณภาพสูง

หัวข้อ: {topic}

ข้อกำหนด:
- เขียนให้อ่านง่าย
- ใช้ภาษาธรรมชาติ
- มีหัวข้อย่อย
- มีบทสรุปท้ายบทความ
- ความยาวประมาณ 800 คำ

SEO:
- ใช้ keyword ซ้ำอย่างเป็นธรรมชาติ
- เหมาะสำหรับเว็บไซต์
"""

    if category == "comedy":
        base += "\nโทน: สนุก อ่านเพลิน มีตัวอย่างสถานการณ์จริง"

    if category == "health":
        base += "\nโทน: ให้ความรู้ ใช้ได้จริง"

    if category == "horoscope":
        base += "\nโทน: ดูดวง อ่านง่าย"

    return base


# ─────────────────────────────────────────────
# CALL OLLAMA
# ─────────────────────────────────────────────

def generate_content(prompt: str) -> str:

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=600
    )

    data = response.json()

    return data.get("response", "")


# ─────────────────────────────────────────────
# SAVE HTML WITH SEO
# ─────────────────────────────────────────────

def save_html(category: str, topic: str, content: str):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{category}_{timestamp}_{random.randint(1000,9999)}.html"

    filepath = OUTPUT_DIR / filename

    keywords = build_keywords(topic)

    description = topic

    html = f"""
<html>
<head>
<meta charset=\"utf-8\">
<title>{topic}</title>

<meta name=\"description\" content=\"{description}\">
<meta name=\"keywords\" content=\"{keywords}\">
<meta name=\"robots\" content=\"index, follow\">

</head>
<body>

<h1>{topic}</h1>

{content}

</body>
</html>
"""

    filepath.write_text(html, encoding="utf-8")

    print(f"Saved: {filename}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run():

    print("=" * 50)
    print("Auto Content Generator -", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Model:", MODEL_NAME)
    print("Posts per run:", POSTS_PER_RUN)
    print("=" * 50)

    for i in range(POSTS_PER_RUN):

        category = random.choice(list(CATEGORIES.keys()))

        topic = random.choice(CATEGORIES[category])

        print(f"Generating ({i+1}/{POSTS_PER_RUN}): [{category}] {topic}")

        prompt = build_prompt(category, topic)

        content = generate_content(prompt)

        save_html(category, topic, content)


if __name__ == "__main__":
    run()
