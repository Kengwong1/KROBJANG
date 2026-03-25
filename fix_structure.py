"""
fix_structure.py — แก้ structure header/nav ทุกหน้าให้เหมือนหน้าข่าว
วิธีใช้: วางไว้ในโฟลเดอร์เดียวกับไฟล์ HTML แล้วรัน:
    python fix_structure.py

สิ่งที่แก้:
  1. ลบ <header><nav> เก่าที่มี class="brand" / href="/ai" ออก
  2. เพิ่ม <header> โลโก้ ครบจังดอทคอม ก่อน .main-nav (ถ้ายังไม่มี)
  3. ห่อ <nav class="main-nav"> ที่ links ลอยอยู่นอก nav-wrap ให้เข้า div.nav-wrap
  4. แก้ <div class="mobile-nav"> ที่มี nav-wrap ซ้อนอยู่ข้างใน (contact.html)
     ให้เป็น mobile-nav ตรงๆ โดยไม่มี nav-wrap
"""

import os, re, glob

# ── โลโก้ header มาตรฐาน (เหมือน news.html) ──────────────────────────────
HEADER_HTML = '''<header>
  <div class="logo">ครบจังดอทคอม</div>
</header>\n'''

html_files = glob.glob("*.html")
if not html_files:
    print("❌ ไม่พบไฟล์ .html  กรุณาวางสคริปต์ไว้ในโฟลเดอร์เดียวกับไฟล์เว็บ")
    exit()

print(f"พบ {len(html_files)} ไฟล์\n")
fixed = []

for filename in html_files:
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        src = f.read()
    out = src

    # ── 1) ลบ header เก่า (มี brand/nav เก่า) ──────────────────────────────
    # จับ <header>...</header> ที่มี class="brand" หรือ href="/ai" อยู่ข้างใน
    out = re.sub(
        r'<header>\s*<nav>[\s\S]*?class=["\']brand["\'][\s\S]*?</nav>\s*</header>',
        '',
        out,
        flags=re.IGNORECASE
    )

    # ── 2) เพิ่ม header โลโก้ถ้ายังไม่มี ────────────────────────────────────
    has_logo_header = bool(re.search(r'<header>[\s\S]*?class=["\']logo["\'][\s\S]*?</header>', out, re.IGNORECASE))
    has_main_nav    = bool(re.search(r'<nav\s[^>]*class=["\'][^"\']*main-nav', out, re.IGNORECASE))

    if not has_logo_header and has_main_nav:
        # แทรก header ก่อน <nav class="main-nav">
        out = re.sub(
            r'(<nav\s[^>]*class=["\'][^"\']*main-nav)',
            HEADER_HTML + r'\1',
            out,
            count=1,
            flags=re.IGNORECASE
        )

    # ── 3) ห่อ links ใน <nav class="main-nav"> ที่ยังลอยอยู่นอก nav-wrap ──
    # ตรวจว่า nav block มี div.nav-wrap หรือเปล่า
    def fix_nav_wrap(m):
        nav_open  = m.group(1)   # เช่น <nav class="main-nav">
        nav_body  = m.group(2)   # เนื้อหาข้างใน
        nav_close = m.group(3)   # </nav>
        # ถ้ามี nav-wrap แล้วไม่ต้องแก้
        if re.search(r'class=["\'][^"\']*nav-wrap', nav_body, re.IGNORECASE):
            return m.group(0)
        # ไม่มี → ห่อด้วย div.nav-wrap
        wrapped_body = f'\n  <div class="nav-wrap">\n{nav_body.strip()}\n  </div>\n'
        return nav_open + wrapped_body + nav_close

    out = re.sub(
        r'(<nav\b[^>]*class=["\'][^"\']*main-nav[^>]*>)([\s\S]*?)(</nav>)',
        fix_nav_wrap,
        out,
        flags=re.IGNORECASE
    )

    # ── 4) แก้ mobile-nav ที่มี nav-wrap ซ้อน (contact.html pattern) ────────
    # <div class="mobile-nav"><div class="nav-wrap">links</div></div>
    # → <div class="mobile-nav">links</div>
    def unwrap_mobile_nav(m):
        outer_open  = m.group(1)  # <div class="mobile-nav" ...>
        inner_wrap  = m.group(2)  # เนื้อหาใน nav-wrap
        outer_close = m.group(3)  # </div> ปิด mobile-nav
        # ตรวจว่า inner มี nav-wrap ไหม
        inner_match = re.search(
            r'<div\s[^>]*class=["\'][^"\']*nav-wrap[^"\']*["\'][^>]*>([\s\S]*?)</div>',
            inner_wrap, re.IGNORECASE
        )
        if inner_match:
            links = inner_match.group(1)
            return outer_open + '\n' + links.strip() + '\n' + outer_close
        return m.group(0)

    out = re.sub(
        r'(<div\b[^>]*class=["\'][^"\']*mobile-nav[^"\']*["\'][^>]*>)'
        r'([\s\S]*?)'
        r'(</div>\s*(?=\s*<div|\s*<aside|\s*<footer|\s*</body))',
        unwrap_mobile_nav,
        out,
        flags=re.IGNORECASE
    )

    # ── 5) ลบ link /style.css ซ้ำที่ absolute path (/style.css) ─────────────
    out = re.sub(
        r'\s*<link\s+rel=["\']stylesheet["\']\s+href=["\']\/style\.css["\']\s*/?>',
        '',
        out,
        flags=re.IGNORECASE
    )

    # ── บันทึกถ้ามีการเปลี่ยนแปลง ───────────────────────────────────────────
    if out != src:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(out)
        fixed.append(filename)
        print(f"  ✅ {filename}")
    else:
        print(f"  ⏭️  {filename}  (ไม่มีการเปลี่ยนแปลง)")

print(f"\n{'='*50}")
print(f"✅ แก้ไขแล้ว {len(fixed)} ไฟล์")
if fixed:
    for f in fixed:
        print(f"   - {f}")
print("\n🎉 เสร็จแล้ว! รีเฟรชเบราว์เซอร์แล้วดูได้เลยครับ")
