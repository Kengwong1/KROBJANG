# 📚 Agent System — ไอหมอก

วางไฟล์ทั้งหมดใน `D:\Projects\krubjang-site full\` (โฟลเดอร์เดียวกับ config.py)

---

## 🗂️ Agent แต่ละตัว

| ไฟล์ | หน้าที่ | คำสั่งด่วน |
|------|--------|------------|
| `agent_nav.py` | Nav 2 แถว + Footer | `python agent_nav.py --all` |
| `agent_content.py` | เนื้อหา/instruction/ซ้ำ | `python agent_content.py --all` |
| `agent_links.py` | dead/empty links | `python agent_links.py --all` |
| `agent_image.py` | รูปทุกอย่าง | `python agent_image.py --all` |
| `agent_seo.py` | meta/og/alt/sitemap | `python agent_seo.py --all` |
| `agent_health.py` | ตรวจสุขภาพ + audit | `python agent_health.py` |
| `agent_theme.py` | ธีม 42 แบบ + layout | `python agent_theme.py` |
| `agent_publish.py` | sitemap + push GitHub | `python agent_publish.py --all` |
| `run_all.py` | **รวมพล ทุก agent** | `python run_all.py` |

---

## 🚀 คำสั่งที่ใช้บ่อย

```cmd
cd /d "D:\Projects\krubjang-site full"

# รันทุกอย่างเต็ม pipeline
python run_all.py

# รันเร็ว (ข้าม AI/vision)
python run_all.py --quick

# แค่ตรวจ ไม่แก้
python run_all.py --check

# แค่แก้ไข
python run_all.py --fix-only

# Push GitHub
python run_all.py --publish
```

---

## 🎨 เปลี่ยนธีม (42 แบบ)

```cmd
# เมนูเลือก interactive
python agent_theme.py

# เปลี่ยนทันที
python agent_theme.py --theme mystic
python agent_theme.py --theme sakura
python agent_theme.py --theme cosmic
python agent_theme.py --theme dharma

# ดูธีมทั้งหมด
python agent_theme.py --list
```

---

## 🖼️ จัดการรูป

```cmd
python agent_image.py --check    # ตรวจรูป (ใช้ vision AI)
python agent_image.py --fix      # แก้รูปไม่ตรงเนื้อหา
python agent_image.py --dedup    # แก้รูปซ้ำ
python agent_image.py --cards    # แก้รูปการ์ดหน้าหมวด
python agent_image.py --hero     # แก้รูป hero บทความ
python agent_image.py --index    # อัปเดต search index
python agent_image.py --all      # ทำทุกอย่าง
```

---

## ✍️ จัดการเนื้อหา

```cmd
python agent_content.py --check        # ตรวจเนื้อหาเพี้ยน
python agent_content.py --fix          # แก้เนื้อหาเพี้ยน
python agent_content.py --instruction  # ลบ instruction หลุด
python agent_content.py --dup          # ตรวจบทความซ้ำ
python agent_content.py --rewrite      # เขียนใหม่ด้วย AI
```

---

## ⚠️ หมายเหตุสำคัญ

- **ต้อง cd เข้าโฟลเดอร์ก่อนทุกครั้ง**: `cd /d "D:\Projects\krubjang-site full"`
- `run_all.py` จะ rebuild nav+footer ก่อนเสมอ → ไม่มีปัญหาถูกทับอีก
- `agent_theme.py` รันแยกต่างหาก ไม่รันใน run_all เพราะต้องเลือกเอง
- ไฟล์ `agent_fix_v6.py` เดิมยังใช้ได้ แต่แนะนำใช้ agent ใหม่แทน
