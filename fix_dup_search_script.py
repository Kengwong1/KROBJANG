"""
fix_dup_search_script.py
========================
ลบ search script block ที่ซ้ำออกจากทุกไฟล์ HTML
(เก็บไว้แค่ block แรก ลบ block ที่ 2 ทิ้ง)
"""
import re
from pathlib import Path

BASE = Path(".")
SKIP = {"node_modules", ".git", ".vercel", "__pycache__", "dist", "build"}

# pattern จับ search script block (มี SEARCH_DATA อยู่ข้างใน)
SEARCH_BLOCK_RE = re.compile(
    r'<script[^>]*>\s*\(function\(\)\{[^<]*?var SEARCH_DATA\s*=.*?\}\)\(\);?\s*</script>',
    re.DOTALL
)

fixed = 0
for fp in sorted(BASE.glob("*.html")):
    if any(s in fp.parts for s in SKIP):
        continue
    try:
        orig = fp.read_text(encoding="utf-8", errors="ignore")
        blocks = SEARCH_BLOCK_RE.findall(orig)
        if len(blocks) < 2:
            continue  # ไม่ซ้ำ ข้าม

        # ลบ block ที่ 2 ขึ้นไป เก็บแค่ block แรก
        count = [0]
        def replace_fn(m):
            count[0] += 1
            if count[0] == 1:
                return m.group(0)  # เก็บ block แรก
            return ""              # ลบ block ที่ 2+

        new_html = SEARCH_BLOCK_RE.sub(replace_fn, orig)
        if new_html != orig:
            fp.write_text(new_html, encoding="utf-8")
            print(f"✅ {fp.name}: ลบ {len(blocks)-1} block ซ้ำ")
            fixed += 1
    except Exception as e:
        print(f"❌ {fp.name}: {e}")

print(f"\n✅ แก้แล้ว {fixed} ไฟล์")
print("\nถัดไป:")
print("  python agent_fix_v6.py --publish")
