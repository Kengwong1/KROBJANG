from glob import glob
import re

html_files = glob("*.html")
all_vars = {}

# ดึง :root variables จากทุกหน้า
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    root = re.search(r':root\s*\{([^}]+)\}', content)
    if root:
        for line in root.group(1).splitlines():
            line = line.strip()
            if line.startswith('--'):
                key = line.split(':')[0].strip()
                all_vars[key] = line

# เขียน style.css
with open("style.css", 'w', encoding='utf-8') as f:
    f.write(":root {\n")
    for var in sorted(all_vars.values()):
        f.write(f"  {var}\n")
    f.write("}\n")

print(f"✅ พบ CSS Variables {len(all_vars)} ตัว → บันทึกใน style.css แล้ว")

# ลบ :root ออกจากทุกหน้า แล้วเพิ่ม link style.css
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # ลบ :root {...} ออกจาก <style>
    new_content = re.sub(r'\s*:root\s*\{[^}]+\}', '', content)

    # เพิ่ม link style.css ถ้ายังไม่มี
    if 'style.css' not in new_content:
        new_content = new_content.replace(
            '</head>',
            '  <link rel="stylesheet" href="style.css">\n</head>'
        )

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"✅ อัปเดต {len(html_files)} ไฟล์เรียบร้อย")
print("ทดสอบเปิดหน้าเว็บดูได้เลยครับ!")