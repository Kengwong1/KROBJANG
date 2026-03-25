"""
fix_all_pages.py — แก้ไฟล์ HTML ทุกหน้าให้ใช้ style.css ที่สะอาด
วิธีใช้: วางไฟล์นี้ไว้ในโฟลเดอร์เดียวกับไฟล์ HTML แล้วรัน:
    python fix_all_pages.py
"""

import os
import re
import glob

# ======================================================
# 1) ลิสต์ไฟล์ HTML ทุกไฟล์ในโฟลเดอร์ปัจจุบัน
# ======================================================
html_files = glob.glob("*.html")
if not html_files:
    print("❌ ไม่พบไฟล์ .html ในโฟลเดอร์นี้ กรุณาวางสคริปต์ไว้ในโฟลเดอร์เดียวกับไฟล์เว็บครับ")
    exit()

print(f"พบ {len(html_files)} ไฟล์ HTML: {html_files}\n")

fixed = []
skipped = []

for filename in html_files:
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    original = content

    # --------------------------------------------------
    # 2) ลบ style inline ที่ซ้ำซ้อนใน <head>
    #    (style block ที่ AI เก่าสร้างทิ้งไว้ในแต่ละหน้า)
    # --------------------------------------------------
    # ลบ <style>...</style> blocks ที่อยู่ใน <head> ออกทั้งหมด
    # แต่เก็บ style ที่อยู่ใน <body> ไว้ (เช่น inline style="...")
    # วิธีนี้ safe กว่าเพราะเราพึ่ง style.css กลางอยู่แล้ว
    content = re.sub(
        r'<style[^>]*>.*?</style>',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------
    # 3) ตรวจว่ามี link ไปยัง style.css อยู่แล้วหรือไม่
    # --------------------------------------------------
    has_link = bool(re.search(r'<link[^>]+href=["\']style\.css["\']', content, re.IGNORECASE))

    if not has_link:
        # เพิ่ม link ก่อน </head>
        content = content.replace(
            '</head>',
            '  <link rel="stylesheet" href="style.css">\n</head>',
            1
        )
        print(f"  ✅ เพิ่ม link style.css ใน {filename}")
    else:
        print(f"  ✔️  {filename} มี style.css อยู่แล้ว")

    # --------------------------------------------------
    # 4) บันทึกไฟล์ถ้ามีการเปลี่ยนแปลง
    # --------------------------------------------------
    if content != original:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        fixed.append(filename)
    else:
        skipped.append(filename)

# ======================================================
# สรุปผล
# ======================================================
print("\n" + "="*50)
print(f"✅ แก้ไขแล้ว ({len(fixed)} ไฟล์):")
for f in fixed:
    print(f"   - {f}")

if skipped:
    print(f"\n⏭️  ไม่มีการเปลี่ยนแปลง ({len(skipped)} ไฟล์):")
    for f in skipped:
        print(f"   - {f}")

print("\n🎉 เสร็จแล้วครับ! เปิดเว็บดูได้เลย")
print("   (อย่าลืมวางไฟล์ style.css ที่แก้แล้วไว้ในโฟลเดอร์เดียวกันด้วยครับ)")
