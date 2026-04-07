# 🤖 Universal Web Agent

ใช้ได้ทุกเว็บ ทุกโครงสร้าง ทุกปัญหา

## โครงสร้างไฟล์
```
universal_agent/
├── config.py              ← ตั้งค่าทุกอย่างที่นี่
├── master.py              ← รันตัวนี้ตัวเดียว
├── core/
│   ├── detector.py        ← สแกนเว็บ เรียนรู้โครงสร้างเอง
│   ├── ai_engine.py       ← Ollama + fallback chain
│   ├── image.py           ← ดึงรูป 6 แหล่ง fallback
│   └── scraper.py         ← ดึงข้อมูล 8 แหล่ง fallback
└── agents/
    ├── writer.py           ← เขียนบทความ AI
    ├── repair.py           ← ซ่อมทุกปัญหา
    └── publisher.py        ← push GitHub + sitemap
```

## วิธีใช้

### ติดตั้ง
```bash
pip install requests feedparser beautifulsoup4 python-dotenv
```

### คำสั่งหลัก
```powershell
# เขียนบทความใหม่อัตโนมัติ
python master.py --write

# ระบุหัวข้อเอง
python master.py --write --topic "สูตรต้มยำกุ้ง" --cat "food"

# ซ่อมทุกปัญหาในเว็บ
python master.py --repair

# รายงานปัญหา (ไม่แก้)
python master.py --audit

# push ขึ้น GitHub/Vercel
python master.py --publish

# ทำทุกอย่างในครั้งเดียว
python master.py --all

# ทดสอบ ไม่บันทึกจริง
python master.py --all --dry-run
```

### ใช้กับหลายเว็บ
```powershell
# เว็บ A
python master.py --profile siteA --write

# เว็บ B
python master.py --profile siteB --repair
```

### เพิ่มเว็บใหม่
แก้ไขใน `config.py` ส่วน `WEB_PROFILES`:
```python
WEB_PROFILES = {
    "เว็บใหม่": {
        "name":      "ชื่อเว็บ",
        "base_path": Path(r"C:\Sites\เว็บใหม่"),
        "site_url":  "https://เว็บใหม่.com",
        "file_types": [".html"],
        "article_pattern": "*_*.html",
        "categories": ["food","travel","tech"],
        "category_page_map": {"food":"food.html","travel":"travel.html"},
        "rss_feeds": [],
        "lang": "th",
    },
}
```

## Fallback Chain

| ระบบ | Plan 1 | Plan 2 | Plan 3 | Plan 4+ |
|------|--------|--------|--------|---------|
| **รูปภาพ** | Unsplash | Pexels | Pixabay | Picsum → SVG |
| **ข้อมูลอ้างอิง** | DuckDuckGo | เว็บไทย | Wikipedia ไทย | Bing → Wikipedia EN |
| **AI เขียน** | Ollama model หลัก | Ollama model สำรอง | Template fallback |
| **หาไฟล์บทความ** | Pattern จาก config | วิเคราะห์ pattern เอง | เช็ค h1 tag |
| **Content area** | Class จาก config | Semantic tags | Div ใหญ่สุด → body |

## ตัวแปรสภาพแวดล้อม (.env)
```env
# เว็บ
BASE_PATH=D:\Projects\mysite
SITE_URL=https://mysite.com
SITE_NAME=ชื่อเว็บ

# AI
OLLAMA_MODEL=scb10x/llama3.1-typhoon2-8b-instruct:latest
OLLAMA_TIMEOUT=300

# รูปภาพ
UNSPLASH_KEY=your_key
PEXELS_KEY=your_key
PIXABAY_KEY=your_key

# Analytics
GA4_ID=G-XXXXXXXX
ADSENSE_PUB=ca-pub-XXXXXXXX
```
