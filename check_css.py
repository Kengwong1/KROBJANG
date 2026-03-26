from glob import glob

html_files = glob("*.html")
print(f"พบไฟล์ HTML ทั้งหมด {len(html_files)} ไฟล์\n")

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'style.css' in content:
        print(f"OK  {html_file}")
    else:
        print(f"NO  {html_file} → ไม่มี style.css")