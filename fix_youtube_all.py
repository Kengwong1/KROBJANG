"""
fix_youtube_all.py v2 — แก้ไขทุกไฟล์ HTML ในโฟลเดอร์เว็บ
แก้ 3 ปัญหา:
  1. YouTube Error 153 → youtube.com/embed → youtube-nocookie.com/embed
  2. ปุ่มแชร์ YouTube URL ผิด → แก้เป็น channel URL จริง
  3. ปุ่มแชร์ YouTube หายไปเลย → แทรกปุ่มใหม่หลัง Threads

วิธีใช้:
  python fix_youtube_all.py              -> แก้ทุกไฟล์
  python fix_youtube_all.py --dry-run    -> ดูผลก่อน ไม่บันทึก
  python fix_youtube_all.py --dir D:/Projects/mysite
"""

import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import BASE_PATH, SIDEBAR_CONFIG
    SITE_DIR = BASE_PATH
    YT_CHANNEL = SIDEBAR_CONFIG.get("youtube_url", "https://youtube.com").rstrip("/")
    print(f"OK โหลด config.py สำเร็จ")
    print(f"   โฟลเดอร์  : {SITE_DIR}")
    print(f"   YouTube   : {YT_CHANNEL}")
except ImportError:
    SITE_DIR = Path(r"D:\Projects\krubjang-site full")
    YT_CHANNEL = "https://youtube.com/@phongphunphommanee8045"
    print(f"WARN ไม่พบ config.py ใช้ค่า default")

args = sys.argv[1:]
if "--dir" in args:
    idx = args.index("--dir")
    if idx + 1 < len(args):
        SITE_DIR = Path(args[idx + 1])

DRY_RUN = "--dry-run" in args


def fix_embed(html):
    p = re.compile(r'https?://(?:www\.)?youtube\.com/embed/', re.IGNORECASE)
    return p.subn('https://www.youtube-nocookie.com/embed/', html)


def fix_share_url(html, yt_channel):
    p = re.compile(r"'https?://(?:www\.)?youtube\.com/share\?url='(\+u)?", re.IGNORECASE)
    return p.subn(f"'{yt_channel}'", html)


def add_youtube_btn(html, yt_channel):
    # มีปุ่มอยู่แล้ว ไม่ต้องเพิ่ม
    if 'fab fa-youtube' in html:
        return html, 0
    # ไม่มี share block เลย ข้ามไป
    if 'var btns=[' not in html:
        return html, 0

    yt_btn = f"          ['{yt_channel}','#ff0000','<i class=\"fab fa-youtube\"></i> YouTube'],"

    # แทรกหลัง Threads
    p = re.compile(r"(\['https://threads\.net[^\]]+'\],)")
    if p.search(html):
        new_html = p.sub(r"\1\n" + yt_btn, html)
        return new_html, 1

    # fallback: แทรกก่อน ]]; ปิด btns
    p2 = re.compile(r"(        \];)")
    m = p2.search(html)
    if m and 'var btns=[' in html[:m.start()]:
        new_html = html[:m.start()] + yt_btn + "\n" + html[m.start():]
        return new_html, 1

    return html, 0


def fix_link_color(html):
    old = 'style="color:#fff;text-decoration:underline;">เปิดใน YouTube</a>'
    new = 'style="color:#ffdd57;text-decoration:underline;font-weight:700;">เปิดใน YouTube ↗</a>'
    n = html.count(old)
    return html.replace(old, new) if n else html, n


def main():
    if not SITE_DIR.exists():
        print(f"ERROR ไม่พบโฟลเดอร์: {SITE_DIR}")
        return

    files = sorted([f for f in SITE_DIR.glob("*.html") if "_" in f.stem and f.stem[0].isalpha()])
    print(f"\n{'='*58}")
    print(f"  แก้ YouTube ใน {len(files)} ไฟล์{'  [DRY-RUN]' if DRY_RUN else ''}")
    print(f"{'='*58}\n")

    s = dict(files_changed=0, files_skipped=0, embed=0, share=0, btn=0, color=0)

    for fp in files:
        try:
            html = fp.read_text(encoding="utf-8")
            orig = html

            html, n1 = fix_embed(html)
            html, n2 = fix_share_url(html, YT_CHANNEL)
            html, n3 = add_youtube_btn(html, YT_CHANNEL)
            html, n4 = fix_link_color(html)

            total = n1 + n2 + n3 + n4
            if total:
                s["files_changed"] += 1
                s["embed"] += n1; s["share"] += n2
                s["btn"]   += n3; s["color"] += n4
                if not DRY_RUN:
                    fp.write_text(html, encoding="utf-8")
                tag = "[DRY]" if DRY_RUN else "OK"
                d = []
                if n1: d.append(f"embed nocookie×{n1}")
                if n2: d.append(f"share url×{n2}")
                if n3: d.append(f"ปุ่มใหม่×{n3}")
                if n4: d.append(f"สี×{n4}")
                print(f"  {tag}  {fp.name:<50}  {', '.join(d)}")
            else:
                s["files_skipped"] += 1
        except Exception as e:
            print(f"  ERR  {fp.name} — {e}")

    print(f"\n{'='*58}")
    print(f"  ไฟล์แก้ไข     : {s['files_changed']}")
    print(f"  ไฟล์ข้าม      : {s['files_skipped']} (ไม่มี YouTube)")
    print(f"  embed nocookie : {s['embed']} จุด  → แก้ Error 153")
    print(f"  share url แก้  : {s['share']} จุด")
    print(f"  ปุ่มเพิ่มใหม่   : {s['btn']} ไฟล์")
    print(f"  สีลิงก์        : {s['color']} จุด")
    if DRY_RUN:
        print(f"\n  รันอีกครั้งโดยไม่ใส่ --dry-run เพื่อบันทึกจริง")
    else:
        print(f"\n  เสร็จ! Push ขึ้น GitHub/Vercel ได้เลย")
    print(f"{'='*58}")


if __name__ == "__main__":
    main()