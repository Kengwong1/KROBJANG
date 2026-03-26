import re
from glob import glob

html_files = glob("*.html")
css_per_file = {}

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    found = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    if found:
        css_per_file[html_file] = found.group(1).strip()

# เอา index.html เป็น base แล้วเช็คว่าหน้าอื่นต่างกันแค่ไหน
base = css_per_file.get("index.html", "")
base_lines = set(base.splitlines())

print(f"index.html มี CSS {len(base_lines)} บรรทัด\n")
print("หน้าที่มี CSS ต่างจาก index.html:")

for html_file, css in css_per_file.items():
    if html_file == "index.html":
        continue
    lines = set(css.splitlines())
    extra = lines - base_lines
    missing = base_lines - lines
    if extra or missing:
        print(f"\n📄 {html_file}")
        print(f"   เพิ่มมา {len(extra)} บรรทัด | ขาดไป {len(missing)} บรรทัด")