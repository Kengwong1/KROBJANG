"""
patch_home_link.py
==================
แพทช์ agent_fix_v6.py ให้ใช้ href="/" แทน href="index.html" ตลอด
เพื่อให้ทำงานได้บน Vercel

รัน:
  python patch_home_link.py
"""
import re
from pathlib import Path

fp = Path("agent_fix_v6.py")
if not fp.exists():
    print("❌ ไม่พบ agent_fix_v6.py")
    exit()

src = fp.read_text(encoding="utf-8")
orig = src

# แก้ทุก href="index.html" และ href='index.html' ใน string literals
src = src.replace('href="index.html"', 'href="/"')
src = src.replace("href='index.html'", "href='/'")

# แก้ใน f-string ที่อาจมี {VAR}/index.html (breadcrumb, cat_page fallback)
# เช่น f'href="index.html"' ใน Python code
src = re.sub(r"(href=\\?['\"])index\.html(\\?['\"])", r"\1/\2", src)

# แก้ window.location patterns ใน JS ที่ generate ใน Python
src = src.replace("'index.html'", "'/'")
src = src.replace('"index.html"', '"/"')

n = sum(1 for a, b in zip(orig.splitlines(), src.splitlines()) if a != b)

if src != orig:
    fp.write_text(src, encoding="utf-8")
    print(f"✅ แพทช์ agent_fix_v6.py สำเร็จ — แก้ {n} บรรทัด")
else:
    print("✅ agent_fix_v6.py ไม่มี index.html link แล้ว")

print()
print("ถัดไป:")
print("  python fix_vercel_links.py      # แก้ไฟล์ HTML ที่มีอยู่")
print("  python agent_fix_v6.py --publish  # push ขึ้น Vercel")
