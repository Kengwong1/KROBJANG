import requests
from bs4 import BeautifulSoup
from PIL import Image
import os

def main():
    """ฟังก์ชันหลักในการตรวจสอบและแก้ไขรูปซ้ำ"""
    print("กำลังตรวจสอบรูปซ้ำในเว็บไซต์...")
    check_duplicate_images()
    print("การตรวจสอบและแก้ไขรูปซ้ำเสร็จสมบูรณ์")

def check_duplicate_images():
    """ตรวจสอบรูปซ้ำในเว็บไซต์และแก้ไข"""
    base_url = "https://www.example.com"  # เปลี่ยนเป็น URL ของเว็บไซต์ที่ต้องการตรวจสอบ
    all_images = get_all_images(base_url)
    duplicate_images = find_duplicate_images(all_images)

    if duplicate_images:
        print("พบรูปซ้ำ:")
        for image_url in duplicate_images:
            print(f"  - {image_url}")
            replace_image(image_url)
    else:
        print("ไม่พบรูปซ้ำในเว็บไซต์")

def get_all_images(url):
    """ดึง URL ของรูปภาพทั้งหมดจากเว็บไซต์"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # ตรวจสอบว่า request สำเร็จหรือไม่
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')
        image_urls = [img['src'] for img in images if 'src' in img.attrs]
        return image_urls
    except requests.exceptions.RequestException as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return []

def find_duplicate_images(image_urls):
    """ตรวจสอบว่ามีรูปภาพซ้ำกันหรือไม่"""
    seen_urls = set()
    duplicate_urls = []
    for url in image_urls:
        if url in seen_urls:
            duplicate_urls.append(url)
        else:
            seen_urls.add(url)
    return duplicate_urls

def replace_image(image_url):
    """แทนที่รูปภาพซ้ำด้วยรูปภาพจาก Unsplash"""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw)
        # สร้างชื่อไฟล์ใหม่สำหรับรูปภาพจาก Unsplash
        image_id = image_url.split("/")[-1].split("?")[0]
        unsplash_image_url = f"https://source.unsplash.com/random/{image.size[0]}x{image.size[1]}/?sig={image_id}"
        
        # ดาวน์โหลดรูปภาพจาก Unsplash
        unsplash_response = requests.get(unsplash_image_url, stream=True)
        unsplash_response.raise_for_status()
        unsplash_image = Image.open(unsplash_response.raw)

        # บันทึกรูปภาพใหม่
        filename = os.path.basename(image_url)
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_unsplash{ext}"
        unsplash_image.save(new_filename)

        # แทนที่รูปภาพเดิมด้วยรูปภาพใหม่
        print(f"ได้เปลี่ยนรูปภาพ {image_url} เป็น {new_filename}")

    except requests.exceptions.RequestException as e:
        print(f"เกิดข้อผิดพลาดในการดาวน์โหลดรูปภาพจาก Unsplash: {e}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()