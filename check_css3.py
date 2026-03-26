from glob import glob
import re

# ดูแค่ไฟล์แรกก่อน เพื่อเช็คว่าโครงสร้างเป็นยังไง
with open("index.html", 'r', encoding='utf-8') as f:
    content = f.read()

# หา style tags
styles = re.findall(r'<style[^>]*>.*?</style>', content, re.DOTALL)
print(f"พบ <style> จำนวน {len(styles)} อัน\n")
for i, s in enumerate(styles):
    print(f"--- style #{i+1} (แสดง 200 ตัวอักษรแรก) ---")
    print(s[:200])
    print()