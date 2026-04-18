"""
sync_category_images.py — อัปเดต URL รูปใน category page ให้ตรงกับ article HTML

category page (เช่น beauty.html) มี <img src="..."> ของแต่ละบทความฝังตรงๆ
script นี้จะ:
1. สแกน article HTML แต่ละไฟล์ → อ่าน hero image URL (og:image)
2. แก้ URL ใน category page ให้ตรงกัน

วิธีใช้:
  python sync_category_images.py            แก้ทุก category page
  python sync_category_images.py --dry-run  ทดสอบไม่เขียนไฟล์
  python sync_category_images.py --file beauty.html
"""

import sys, re
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from config import (
        BASE_PATH, CATEGORY_PAGE_MAP,
        log, log_ok, log_warn, log_err, log_info, log_section,
    )
    DRY_RUN = "--dry-run" in sys.argv
except ImportError as e:
    print(f"❌ import config ไม่ได้: {e}")
    sys.exit(1)


def _get_article_hero_url(article_fp: Path) -> str | None:
    """อ่าน og:image จาก article HTML → คือ URL รูปที่ถูกต้อง"""
    try:
        txt = article_fp.read_text(encoding="utf-8", errors="ignore")
        # og:image เป็น source of truth หลังจาก image_replacer_v4 แก้แล้ว
        m = re.search(r'property="og:image"\s+content="([^"]+)"', txt)
        if m:
            return m.group(1)
        # fallback: hero-image-wrapper img src
        soup = BeautifulSoup(txt, "html.parser")
        hero = soup.find(class_="hero-image-wrapper")
        if hero:
            img = hero.find("img")
            if img:
                src = img.get("src", "")
                if src and "pexels.com" in src or "picsum.photos" in src:
                    return src
    except Exception:
        pass
    return None


def _get_category_pages(target_file=None):
    """หา category page ทั้งหมด"""
    pages = []
    if target_file:
        fp = BASE_PATH / target_file
        if fp.exists():
            pages.append(fp)
        return pages

    # CATEGORY_PAGE_MAP มี values เป็น filename ของ category pages
    cat_filenames = set(CATEGORY_PAGE_MAP.values())
    # เพิ่มหน้าที่รู้จักอยู่แล้ว
    known = {
        "beauty.html", "food.html", "health.html", "travel.html",
        "technology.html", "finance.html", "sport.html", "lifestyle.html",
        "news.html", "education.html", "entertainment.html", "horoscope.html",
        "law.html", "pet.html", "car.html", "business.html", "gaming.html",
        "anime.html", "cartoon.html", "drama.html", "movie.html",
        "cooking.html", "tips.html", "diy.html", "story.html",
        "folktale.html", "inspirational.html", "ghost.html", "lottery.html",
        "comedy.html",
    }
    all_cats = cat_filenames | known
    for name in all_cats:
        fp = BASE_PATH / name
        if fp.exists():
            pages.append(fp)
    return pages


def sync_category_images(target_file=None):
    log_section("🔄 Sync Category Page Images")

    # สร้าง map: article_stem → correct_url
    log_info("กำลังอ่าน og:image จาก article files...")
    url_map = {}
    skip_dirs = {"node_modules", ".git", ".vercel", "__pycache__", "dist", "build", ".next"}
    non_article = {"index.html", "404.html", "contact.html", "sitemap.html",
                   "privacy.html", "video.html", "shopping.html", "lotto.html"}
    non_article |= set(CATEGORY_PAGE_MAP.values())

    for fp in sorted(BASE_PATH.rglob("*.html")):
        if any(s in fp.parts for s in skip_dirs):
            continue
        if fp.parent != BASE_PATH:
            continue
        if fp.name in non_article:
            continue
        # skip category pages ด้วย
        if not re.search(r'_\d+\.html$', fp.name):
            continue
        url = _get_article_hero_url(fp)
        if url:
            url_map[fp.stem] = url

    log_info(f"อ่านได้ {len(url_map)} บทความ\n")

    # แก้ category pages
    cat_pages = _get_category_pages(target_file)
    log_info(f"พบ category page {len(cat_pages)} ไฟล์\n")

    total_fixed = 0
    total_replacements = 0

    for cat_fp in sorted(cat_pages):
        try:
            orig = cat_fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            replacements = 0

            for stem, correct_url in url_map.items():
                # หา <img ... src="OLD_URL" ... href="STEM.html">
                # หรือ href="STEM.html" อยู่ใกล้ๆ กับ img src ที่ผิด

                # Pattern: ค้นหา card ที่ link ไปยัง article นี้
                # แล้วเปลี่ยน src ของ img ใน card นั้น
                # ใช้ regex ที่ match: href="STEM.html"...src="WRONG"
                # หรือ src="WRONG"...href="STEM.html" (ภายใน ~2000 chars)

                # วิธีที่แม่นที่สุด: split เป็น card sections แล้วแก้ทีละ card
                card_pattern = re.compile(
                    r'(<a\s[^>]*href=["\']' + re.escape(stem) + r'\.html["\'][^>]*>.*?</a>)',
                    re.DOTALL | re.IGNORECASE
                )

                def fix_card(m):
                    card = m.group(1)
                    # หา img src ใน card นี้
                    img_pattern = re.compile(r'(<img\s[^>]*\bsrc=")([^"]+)(")', re.IGNORECASE)
                    new_card = img_pattern.sub(
                        lambda im: im.group(1) + correct_url + im.group(3),
                        card, count=1
                    )
                    return new_card

                new_html = card_pattern.sub(fix_card, html)
                if new_html != html:
                    replacements += 1
                    html = new_html

            if html != orig:
                if not DRY_RUN:
                    cat_fp.write_text(html, encoding="utf-8")
                prefix = "[DRY-RUN] " if DRY_RUN else ""
                log_ok(f"  {prefix}✅ {cat_fp.name} — แก้ {replacements} รูป")
                total_fixed += 1
                total_replacements += replacements
            else:
                log_info(f"  ⏭️  {cat_fp.name} — ไม่มีอะไรต้องแก้")

        except Exception as e:
            log_err(f"  ❌ {cat_fp.name}: {e}")

    prefix = "[DRY-RUN] " if DRY_RUN else ""
    log_ok(f"\n{prefix}แก้ไฟล์: {total_fixed} | รวมรูปที่เปลี่ยน: {total_replacements}")


def main():
    args = sys.argv[1:]
    target = None
    if "--file" in args:
        idx = args.index("--file")
        if idx + 1 < len(args):
            target = args[idx + 1]

    sync_category_images(target)


if __name__ == "__main__":
    main()
