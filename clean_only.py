import os
from pathlib import Path
from bs4 import BeautifulSoup

# --- CONFIG (พาธของพี่เก่ง) ---
BASE_PATH = Path(r"D:\Projects\krubjang-site full")

def force_clean_svg_placeholders():
    """สคริปต์แยกเฉพาะกิจ: ล้าง .svg หรือ placeholder ทิ้งเพื่อให้ระบบหลักหาใหม่"""
    html_files = [f for f in os.listdir(BASE_PATH) if f.endswith(".html")]
    count = 0
    print(f"🔍 กำลังสแกนไฟล์ใน: {BASE_PATH}")
    
    for f_name in html_files:
        f_path = BASE_PATH / f_name
        try:
            # อ่านไฟล์
            content = f_path.read_text(encoding="utf-8")
            soup = BeautifulSoup(content, "html.parser")
            changed = False
            
            # ค้นหารูป
            for img in soup.find_all("img"):
                src = img.get("src", "").lower()
                # ตรวจสอบขยะ
                if any(x in src for x in [".svg", "placeholder", "picsum", "seed"]):
                    img["src"] = "" # ล้างทิ้ง
                    changed = True
            
            # ถ้ามีการเปลี่ยนแปลง ให้เขียนทับไฟล์เดิม
            if changed:
                f_path.write_text(str(soup), encoding="utf-8")
                count += 1
                print(f"  ✅ ล้างรูปขยะในไฟล์: {f_name}")
                
        except Exception as e:
            print(f"  ❌ พลาดที่ไฟล์ {f_name}: {e}")
            
    print(f"\n✨ เสร็จเรียบร้อย! ล้างไปทั้งหมด {count} ไฟล์ค่ะพี่เก่ง")

if __name__ == "__main__":
    force_clean_svg_placeholders()