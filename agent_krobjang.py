# agent_krobjang.py — COMPLETE VERSION WITH AUTO AUTO_ARTICLES INSERTION
# วางไฟล์นี้แทนของเดิมได้เลย
# ทำหน้าที่:
# 1) สแกนไฟล์ HTML ทุกไฟล์ในโปรเจค
# 2) ตรวจและซ่อม HTML เบื้องต้น
# 3) ใส่ <!-- AUTO_ARTICLES --> อัตโนมัติถ้ายังไม่มี

from pathlib import Path
from bs4 import BeautifulSoup
import logging
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# โฟลเดอร์โปรเจค (ค่าเริ่มต้น = โฟลเดอร์ที่ไฟล์นี้อยู่)
KROBJANG_PATH = Path(__file__).resolve().parent

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

log = logging.getLogger("KrobjangAgent")


# ─────────────────────────────────────────────
# GET ALL HTML FILES
# ─────────────────────────────────────────────

def get_all_html_files() -> list[Path]:
    """ค้นหาไฟล์ .html ทั้งหมดในโปรเจค"""

    files: list[Path] = []

    for f in KROBJANG_PATH.rglob("*.html"):
        path_str = str(f).lower()

        # ข้ามโฟลเดอร์ที่ไม่จำเป็น
        if any(skip in path_str for skip in [
            "node_modules",
            "__pycache__",
            "agent_logs",
            "venv",
            ".git",
        ]):
            continue

        files.append(f)

    return files


# ─────────────────────────────────────────────
# BASIC HTML CHECK / FIX
# ─────────────────────────────────────────────

def check_and_fix_html(filepath: Path) -> dict:
    """
    ตรวจ HTML ว่าอ่านได้หรือไม่
    (ไม่แก้ logic ใหญ่ — แค่ตรวจ parse ได้)
    """

    result = {
        "file": filepath.name,
        "fixed": False,
    }

    try:
        html = filepath.read_text(encoding="utf-8", errors="ignore")

        # parse เพื่อเช็กว่า HTML ไม่พัง
        BeautifulSoup(html, "lxml")

    except Exception as e:
        log.error(f"HTML parse error: {filepath} | {e}")
        result["fixed"] = False

    return result


# ─────────────────────────────────────────────
# AUTO INSERT MARKER
# ─────────────────────────────────────────────

def ensure_auto_articles_marker(filepath: Path):
    """
    ถ้าไฟล์ HTML ไม่มี <!-- AUTO_ARTICLES -->
    ให้ใส่เข้าไปอัตโนมัติใน content-area
    """

    try:
        html = filepath.read_text(encoding="utf-8", errors="ignore")

        # ถ้ามี marker อยู่แล้ว
        if "<!-- AUTO_ARTICLES -->" in html:
            return

        soup = BeautifulSoup(html, "lxml")

        # หา content-area
        content = soup.find("div", class_="content-area")

        if not content:
            log.info(f"[SKIP] No content-area in: {filepath.name}")
            return

        marker = soup.new_string("\n<!-- AUTO_ARTICLES -->\n")

        content.append(marker)

        filepath.write_text(str(soup), encoding="utf-8")

        log.info(f"[AUTO] Inserted AUTO_ARTICLES in: {filepath.name}")

    except Exception as e:
        log.error(f"[ERROR] {filepath.name}: {e}")


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

def run_html_fixer():
    """วนตรวจและใส่ marker ทุกไฟล์"""

    log.info("=" * 50)
    log.info("HTML FIXER START")
    log.info("=" * 50)

    files = get_all_html_files()

    log.info(f"Found HTML files: {len(files)}")

    results = []

    for f in files:
        result = check_and_fix_html(f)

        # ใส่ marker อัตโนมัติ
        ensure_auto_articles_marker(f)

        results.append(result)

    fixed_count = sum(1 for r in results if r.get("fixed"))

    log.info(
        f"Completed. Checked: {len(files)} files | Fixed: {fixed_count}"
    )


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_html_fixer()
