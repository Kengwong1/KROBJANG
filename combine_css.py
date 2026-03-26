from glob import glob
import re

html_files = glob("*.html")
all_css = []

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    found = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    if found:
        all_css.append(f"/* === {html_file} === */\n{found.group(1).strip()}")

# รวมทั้งหมดเขียนลง style.css
with open("style_combined.css", 'w', encoding='utf-8') as f:
    f.write("\n\n".join(all_css))

print(f"✅ รวม CSS จาก {len(all_css)} ไฟล์ → style_combined.css")