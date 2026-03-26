from glob import glob
import re

# ดึง CSS จาก index.html เป็น base
with open("index.html", 'r', encoding='utf-8') as f:
    index_content = f.read()

base_css = re.search(r'<style[^>]*>(.*?)</style>', index_content, re.DOTALL)
if base_css:
    with open("style.css", 'w', encoding='utf-8') as f:
        f.write(base_css.group(1).strip())
    print("✅ บันทึก CSS จาก index.html → style.css แล้ว")

# ลบ <style> inline และเพิ่ม link ในทุกไฟล์ HTML
html_files = glob("*.html")
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # ลบ <style>...</style>
    new_content = re.sub(r'\s*<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

    # เพิ่ม link ถ้ายังไม่มี
    if 'style.css' not in new_content:
        new_content = new_content.replace(
            '</head>',
            '  <link rel="stylesheet" href="style.css">\n</head>'
        )

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

print(f"✅ แก้ไขเสร็จ {len(html_files)} ไฟล์")
print("⚠️  เช็คหน้าเว็บดูก่อนนะครับ หน้าไหนพังแจ้งมาได้เลย")