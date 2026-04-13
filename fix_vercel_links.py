"""
fix_vercel_links.py
===================
แก้ปัญหา Vercel: เปลี่ยน href="index.html" → href="/"
ในทุกไฟล์ HTML ของเว็บไซต์

รัน:
  python fix_vercel_links.py
"""
import re
from pathlib import Path

BASE = Path(".")
SKIP = {"node_modules", ".git", ".vercel", ".github", "__pycache__",
        "dist", "build", ".next", "venv", ".venv"}

fixed_files = 0
fixed_count = 0

html_files = [
    fp for fp in BASE.rglob("*.html")
    if not any(s in fp.parts for s in SKIP)
    and fp.parent == BASE  # เฉพาะ root
]

print(f"สแกน {len(html_files)} ไฟล์...")

for fp in sorted(html_files):
    try:
        orig = fp.read_text(encoding="utf-8", errors="ignore")
        html = orig

        # เปลี่ยน href="index.html" → href="/"
        html = re.sub(r'href=["\']index\.html["\']', 'href="/"', html)

        # เปลี่ยน action="index.html" (form) → action="/"
        html = re.sub(r'action=["\']index\.html["\']', 'action="/"', html)

        # เปลี่ยน window.location = 'index.html' ใน JS
        html = re.sub(r"(window\.location(?:\.href)?\s*=\s*)['\"]index\.html['\"]",
                      r"\1'/'", html)

        # เปลี่ยน src="index.html" (กรณีหายาก)
        html = re.sub(r"src=['\"]index\.html['\"]", 'src="/"', html)

        n = orig.count('index.html') - html.count('index.html')
        if html != orig:
            fp.write_text(html, encoding="utf-8")
            fixed_files += 1
            fixed_count += n
            print(f"  ✅ {fp.name}: แก้ {n} จุด")
    except Exception as e:
        print(f"  ❌ {fp.name}: {e}")

print()
print(f"✅ แก้แล้ว {fixed_files} ไฟล์ รวม {fixed_count} จุด")
print()
print("ขั้นตอนถัดไป:")
print("  python agent_fix_v6.py --publish")
