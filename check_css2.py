from glob import glob
import re

html_files = glob("*.html")

css_names = {}
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    found = re.findall(r'href=["\']([^"\']*\.css)["\']', content)
    for css in found:
        css_names.setdefault(css, []).append(html_file)

print("CSS ที่ถูกใช้อยู่ในโปรเจกต์:\n")
for css, files in sorted(css_names.items()):
    print(f"{css} → ใช้ใน {len(files)} ไฟล์")