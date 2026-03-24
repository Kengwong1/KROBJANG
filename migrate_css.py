"""
migrate_css.py
──────────────────────────────────────────────────
รันครั้งเดียว แปลง HTML เก่าทุกไฟล์ให้ใช้ style.css ร่วมกัน

สิ่งที่ทำ:
  1. ลบ <style>...</style> ที่ฝังอยู่ข้างในออก
  2. ใส่ <link rel="stylesheet" href="/style.css"> ใน <head>
  3. ใส่ <header> nav ที่ตรงกันทุกไฟล์
  4. ใส่ <footer> มาตรฐาน (ถ้ายังไม่มี)
  5. backup ไฟล์เดิมไว้ที่ _backup/ ก่อนแก้ทุกครั้ง

วิธีใช้:
  python migrate_css.py
  python migrate_css.py --dry-run   ← ดูว่าจะแก้ไฟล์ไหนบ้าง ยังไม่แก้จริง
  python migrate_css.py --no-backup ← แก้เลยไม่ backup (ไม่แนะนำ)
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIG — แก้ path ให้ตรงกับเครื่องคุณ
# =====================================================

KROBJANG_PATH = Path(r"D:\Projects\krubjang-site full")
BACKUP_PATH   = KROBJANG_PATH / "_backup"

# =====================================================
# NAV HTML — เหมือนกับที่ใช้ใน auto_content_krobjang.py
# =====================================================

NAV_HTML = """\
  <header>
    <nav>
      <a class="brand" href="/">ครบจัง</a>
      <a href="/ai">🤖 AI</a>
      <a href="/finance">💰 การเงิน</a>
      <a href="/health">💚 สุขภาพ</a>
      <a href="/lifestyle">🌟 ไลฟ์สไตล์</a>
      <a href="/horoscope">⭐ ดวง</a>
    </nav>
  </header>"""

FOOTER_HTML = """\
  <footer>
    <p>© {year} ครบจัง · อ่านครบ รู้จริง ใช้ได้เลย</p>
  </footer>"""

CSS_LINK = '  <link rel="stylesheet" href="/style.css">'
ADSENSE_SCRIPT = '  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2068902667667616" crossorigin="anonymous"></script>'

# =====================================================
# HELPERS
# =====================================================

def backup_file(path: Path):
    """สำเนาไฟล์เดิมไปไว้ที่ _backup/ ก่อนแก้"""
    BACKUP_PATH.mkdir(exist_ok=True)
    dest = BACKUP_PATH / path.name
    # ถ้า backup ซ้ำชื่อ ให้ต่อท้ายด้วย timestamp
    if dest.exists():
        ts   = datetime.now().strftime("%H%M%S")
        dest = BACKUP_PATH / f"{path.stem}_{ts}{path.suffix}"
    shutil.copy2(path, dest)


def strip_inline_style(html: str) -> str:
    """ลบ <style>...</style> ทุกบล็อกออก"""
    return re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.IGNORECASE)


def ensure_css_link(html: str) -> str:
    """ใส่ <link stylesheet> ถ้ายังไม่มี"""
    if "style.css" in html:
        return html  # มีแล้ว ไม่ต้องใส่ซ้ำ
    # ใส่ก่อน </head>
    return re.sub(
        r"(</head>)",
        f"{CSS_LINK}\n\\1",
        html,
        flags=re.IGNORECASE,
    )


def ensure_adsense(html: str) -> str:
    """ใส่ AdSense script ถ้ายังไม่มี"""
    if "adsbygoogle.js" in html:
        return html
    return re.sub(
        r"(</head>)",
        f"{ADSENSE_SCRIPT}\n\\1",
        html,
        flags=re.IGNORECASE,
    )


def ensure_nav(html: str) -> str:
    """ใส่ <header> nav หลัง <body> ถ้ายังไม่มี"""
    if "<header>" in html.lower():
        # มี header แล้ว — แทนที่ด้วย nav ใหม่เพื่อให้เมนูครบ
        html = re.sub(
            r"<header[\s\S]*?</header>",
            NAV_HTML,
            html,
            flags=re.IGNORECASE,
        )
        return html
    # ไม่มี header เลย — ใส่หลัง <body>
    return re.sub(
        r"(<body[^>]*>)",
        f"\\1\n{NAV_HTML}",
        html,
        flags=re.IGNORECASE,
    )


def ensure_footer(html: str) -> str:
    """ใส่ <footer> ก่อน </body> ถ้ายังไม่มี"""
    if "<footer>" in html.lower():
        return html  # มีแล้ว
    year    = datetime.now().year
    footer  = FOOTER_HTML.format(year=year)
    return re.sub(
        r"(</body>)",
        f"{footer}\n\\1",
        html,
        flags=re.IGNORECASE,
    )


def migrate_file(path: Path, dry_run: bool = False, do_backup: bool = True) -> dict:
    """
    แปลง 1 ไฟล์ HTML — คืนค่า dict บอกว่าเปลี่ยนอะไรบ้าง
    """
    original = path.read_text(encoding="utf-8", errors="ignore")
    html     = original

    changes = []

    # 1. ลบ inline <style>
    stripped = strip_inline_style(html)
    if stripped != html:
        changes.append("ลบ <style> inline")
        html = stripped

    # 2. เพิ่ม CSS link
    linked = ensure_css_link(html)
    if linked != html:
        changes.append("เพิ่ม <link style.css>")
        html = linked

    # 3. เพิ่ม / อัปเดต AdSense
    with_ads = ensure_adsense(html)
    if with_ads != html:
        changes.append("เพิ่ม AdSense script")
        html = with_ads

    # 4. เพิ่ม / อัปเดต nav
    with_nav = ensure_nav(html)
    if with_nav != html:
        changes.append("อัปเดต <header> nav")
        html = with_nav

    # 5. เพิ่ม footer ถ้าไม่มี
    with_footer = ensure_footer(html)
    if with_footer != html:
        changes.append("เพิ่ม <footer>")
        html = with_footer

    result = {
        "file":    path.name,
        "changes": changes,
        "changed": html != original,
    }

    if not dry_run and html != original:
        if do_backup:
            backup_file(path)
        path.write_text(html, encoding="utf-8")

    return result

# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="Migrate HTML files to shared CSS")
    parser.add_argument("--dry-run",   action="store_true", help="ดูผลโดยไม่แก้ไฟล์จริง")
    parser.add_argument("--no-backup", action="store_true", help="ไม่ backup ก่อนแก้")
    args = parser.parse_args()

    dry_run   = args.dry_run
    do_backup = not args.no_backup

    if dry_run:
        print("\n🔍 DRY RUN — ดูผลเท่านั้น ไม่แก้ไฟล์จริง\n")
    else:
        print(f"\n🚀 MIGRATE START — {'พร้อม backup' if do_backup else 'ไม่ backup'}\n")

    html_files = sorted(KROBJANG_PATH.glob("*.html"))

    # ข้ามไฟล์ที่ไม่ใช่บทความ (เช่น index.html ถ้ามี)
    skip_files = {"index.html", "404.html"}
    html_files = [f for f in html_files if f.name not in skip_files]

    print(f"พบ HTML {len(html_files)} ไฟล์\n")

    total_changed = 0
    total_skip    = 0

    for path in html_files:
        result = migrate_file(path, dry_run=dry_run, do_backup=do_backup)

        if result["changed"]:
            total_changed += 1
            status = "✏️ " if not dry_run else "📋"
            print(f"  {status} {result['file']}")
            for c in result["changes"]:
                print(f"      · {c}")
        else:
            total_skip += 1

    print(f"\n{'─'*50}")
    if dry_run:
        print(f"📋 จะแก้ไข: {total_changed} ไฟล์  |  ข้าม: {total_skip} ไฟล์ (ไม่มีอะไรเปลี่ยน)")
        print(f"\n   รัน python migrate_css.py เพื่อแก้จริง")
    else:
        print(f"✅ แก้ไขสำเร็จ: {total_changed} ไฟล์  |  ข้าม: {total_skip} ไฟล์")
        if do_backup:
            print(f"   backup เก็บไว้ที่: {BACKUP_PATH}")
        print(f"\n   git add . && git commit -m 'migrate: shared CSS + nav' && git push")
    print()


if __name__ == "__main__":
    main()
