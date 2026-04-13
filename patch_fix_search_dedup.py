"""
patch_fix_search_dedup.py
=========================
แพทช์ agent_fix_v6.py ให้ตรวจและลบ search script ซ้ำ
ก่อน inject search block ใหม่เสมอ
"""
import re
from pathlib import Path

fp = Path("agent_fix_v6.py")
src = fp.read_text(encoding="utf-8")
orig = src

# ── หาฟังก์ชัน แก้_search ──────────────────────────────────
# เพิ่ม dedup logic ก่อนที่จะ inject search script
OLD_SEARCH = 'def แก้_search() -> int:'

NEW_SEARCH_PREFIX = '''def _ลบ_search_script_ซ้ำ(html: str) -> str:
    """ลบ search script block ที่ซ้ำ เก็บไว้แค่ block แรก"""
    pattern = re.compile(
        r\'<script[^>]*>\\s*\\(function\\(\\)\\{[^<]*?var SEARCH_DATA\\s*=.*?\\}\\)\\(\\);?\\s*</script>\',
        re.DOTALL
    )
    count = [0]
    def _keep_first(m):
        count[0] += 1
        return m.group(0) if count[0] == 1 else ""
    return pattern.sub(_keep_first, html)


def แก้_search() -> int:'''

if "_ลบ_search_script_ซ้ำ" in src:
    print("✅ _ลบ_search_script_ซ้ำ มีแล้ว")
elif OLD_SEARCH in src:
    src = src.replace(OLD_SEARCH, NEW_SEARCH_PREFIX, 1)
    print("✅ เพิ่ม _ลบ_search_script_ซ้ำ สำเร็จ")
else:
    print("⚠️  ไม่พบ def แก้_search — ข้าม")

# ── หาใน rebuild_index_page ให้เรียก dedup ก่อน write ──────
OLD_WRITE = '''    if เขียน(fp, html, orig):
        log_ok(f"rebuild index: {len(บทความ)} บทความ [{LAYOUT_MODE}]")
        return 1
    log_info("index ไม่มีการเปลี่ยนแปลง")
    return 0'''

NEW_WRITE = '''    html = _ลบ_search_script_ซ้ำ(html)   # ✅ กัน search script ซ้ำ
    if เขียน(fp, html, orig):
        log_ok(f"rebuild index: {len(บทความ)} บทความ [{LAYOUT_MODE}]")
        return 1
    log_info("index ไม่มีการเปลี่ยนแปลง")
    return 0'''

if "_ลบ_search_script_ซ้ำ(html)" in src and "rebuild index" in src:
    print("✅ dedup ใน rebuild_index_page มีแล้ว")
elif OLD_WRITE in src:
    src = src.replace(OLD_WRITE, NEW_WRITE, 1)
    print("✅ เพิ่ม dedup ใน rebuild_index_page")
else:
    print("⚠️  ไม่พบ pattern ใน rebuild_index_page — ข้าม")

if src != orig:
    fp.write_text(src, encoding="utf-8")
    print("💾 บันทึก agent_fix_v6.py เรียบร้อย")
else:
    print("ℹ️  ไม่มีการเปลี่ยนแปลง")
