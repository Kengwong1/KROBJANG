import os
from glob import glob

# กำหนดไฟล์ CSS ใหม่ที่ต้องการใช้งาน
new_css_file = "style.css"

# รวบรวมไฟล์ HTML ทั้งหมดในโฟลเดอร์
html_files = glob("*.html")

# อ่านเนื้อหา CSS จากไฟล์ new_css_file
with open(new_css_file, 'r', encoding='utf-8') as file:
    new_css_content = file.read()

# ลบ CSS เก่าจากทุกไฟล์ HTML
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as file:  # เพิ่ม encoding ตรงนี้
        file_content = file.read()
        
    # แทนที่ CSS เก่าด้วย CSS ใหม่
    file_content = file_content.replace("style.css", new_css_file)
    
    # เขียนไฟล์ HTML กลับไปพร้อมกับ CSS ใหม่
    with open(html_file, 'w', encoding='utf-8') as file:  # เพิ่ม encoding ตรงนี้
        file.write(file_content)

print("ลบ CSS เก่าและใช้ CSS ใหม่ร่วมกันทุกหน้าเรียบร้อยแล้วค่ะ")