# test_agent.py — ทดสอบทุกฟังก์ชันของ agent_krobjang.py
# รัน: python test_agent.py

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_PATH = Path(r"D:\Projects\krubjang-site full")
load_dotenv(BASE_PATH / ".env")

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_TOKEN")
FB_PAGE_ID           = os.getenv("FB_PAGE_ID")
SITE_URL             = os.getenv("WEBSITE_URL", "").rstrip("/")
UNSPLASH_KEY         = os.getenv("UNSPLASH_KEY")

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []

def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    msg = f"{status}  {name}"
    if detail:
        msg += f"\n        → {detail}"
    print(msg)
    results.append(ok)

print("=" * 55)
print("  TEST: agent_krobjang")
print("=" * 55)

# ─────────────────────────────────────────
# 1. .env โหลดได้ครบไหม
# ─────────────────────────────────────────
print("\n[1] .env")

check(".env — FB_PAGE_TOKEN",  bool(FB_PAGE_ACCESS_TOKEN), FB_PAGE_ACCESS_TOKEN[:10] + "..." if FB_PAGE_ACCESS_TOKEN else "ไม่พบ")
check(".env — FB_PAGE_ID",     bool(FB_PAGE_ID),           FB_PAGE_ID or "ไม่พบ")
check(".env — WEBSITE_URL",    bool(SITE_URL),             SITE_URL or "ไม่พบ")
check(".env — UNSPLASH_KEY",   bool(UNSPLASH_KEY),         UNSPLASH_KEY[:10] + "..." if UNSPLASH_KEY else "ไม่พบ")

# ─────────────────────────────────────────
# 2. เชื่อมต่อเว็บไซต์ได้ไหม
# ─────────────────────────────────────────
print("\n[2] เว็บไซต์")

try:
    r = requests.get(SITE_URL, timeout=10)
    check("เว็บไซต์ online", r.status_code == 200, f"HTTP {r.status_code}")
except Exception as e:
    check("เว็บไซต์ online", False, str(e))

try:
    r = requests.get(f"{SITE_URL}/sitemap.xml", timeout=10)
    check("sitemap.xml", r.status_code == 200, f"HTTP {r.status_code}")
except Exception as e:
    check("sitemap.xml", False, str(e))

# ─────────────────────────────────────────
# 3. Unsplash API
# ─────────────────────────────────────────
print("\n[3] Unsplash")

if UNSPLASH_KEY:
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": "health", "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
            timeout=10
        )
        data = r.json()
        img_url = data.get("urls", {}).get("regular", "")
        check("Unsplash API", bool(img_url), img_url[:60] + "..." if img_url else "ไม่ได้รูป")
    except Exception as e:
        check("Unsplash API", False, str(e))
else:
    check("Unsplash API", False, "ไม่มี UNSPLASH_KEY ใน .env")

# ─────────────────────────────────────────
# 4. Facebook Graph API — ตรวจ token
# ─────────────────────────────────────────
print("\n[4] Facebook")

if FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID:
    try:
        r = requests.get(
            f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}",
            params={"access_token": FB_PAGE_ACCESS_TOKEN, "fields": "name,id"},
            timeout=10
        )
        data = r.json()
        page_name = data.get("name", "")
        error     = data.get("error", {}).get("message", "")
        check("Facebook token ใช้ได้", bool(page_name), f"Page: {page_name}" if page_name else error)
    except Exception as e:
        check("Facebook token ใช้ได้", False, str(e))

    # ทดสอบโพสต์จริง (text only ไม่มีรูป) — ลบทีหลังได้
    try:
        test_msg = "🔧 ทดสอบระบบ auto post — ลบโพสต์นี้ได้เลยครับ"
        r = requests.post(
            f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed",
            data={
                "message":      test_msg,
                "access_token": FB_PAGE_ACCESS_TOKEN,
            },
            timeout=15
        )
        data = r.json()
        post_id = data.get("id", "")
        error   = data.get("error", {}).get("message", "")
        check("Facebook โพสต์ข้อความได้", bool(post_id), f"post_id: {post_id}" if post_id else error)
    except Exception as e:
        check("Facebook โพสต์ข้อความได้", False, str(e))

else:
    check("Facebook token ใช้ได้",    False, "ไม่มี FB_PAGE_TOKEN หรือ FB_PAGE_ID ใน .env")
    check("Facebook โพสต์ข้อความได้", False, "ข้ามเพราะไม่มี token")

# ─────────────────────────────────────────
# 5. Ollama รันอยู่ไหม
# ─────────────────────────────────────────
print("\n[5] Ollama")

try:
    r = requests.get("http://localhost:11434", timeout=5)
    check("Ollama server", True, "กำลังรันอยู่")
except Exception:
    check("Ollama server", False, "ไม่ได้รัน — เปิด Ollama ก่อนนะครับ")

# ─────────────────────────────────────────
# 6. โฟลเดอร์โปรเจกต์
# ─────────────────────────────────────────
print("\n[6] โฟลเดอร์")

check("BASE_PATH มีอยู่",    BASE_PATH.exists(),            str(BASE_PATH))
check("agent_logs มีอยู่",  (BASE_PATH / "agent_logs").exists(), str(BASE_PATH / "agent_logs"))
check(".env มีอยู่",         (BASE_PATH / ".env").exists(), str(BASE_PATH / ".env"))

# ─────────────────────────────────────────
# สรุป
# ─────────────────────────────────────────
passed = sum(results)
total  = len(results)
print("\n" + "=" * 55)
print(f"  สรุป: {passed}/{total} ผ่าน")
if passed == total:
    print("  🎉 พร้อมรันเต็มระบบแล้วครับ!")
else:
    print("  ⚠️  แก้รายการที่ FAIL ก่อนนะครับ")
print("=" * 55)
