from glob import glob
import re

html_files = glob("*.html")
success = []
failed = []

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # ลบ <style>...</style> ออก
    new_content = re.sub(r'\s*<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

    # เพิ่ม link ไปหา style.css ใน <head> (ถ้ายังไม่มี)
    if 'style.css' not in new_content:
        new_content = new_content.replace(
            '</head>',
            '  <link rel="stylesheet" href="style.css">\n</head>'
        )

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    success.append(html_file)

print(f"✅ แก้ไขเสร็จแล้ว {len(success)} ไฟล์")