# 🐞 BUG REPORT — `krubjang-site full`

> ตรวจเมื่อ **2026-11-03** · แทนที่รายงานฉบับก่อน (`BUG-REPORT.md` เดิม) ซึ่งมีบางข้อคลาดเคลื่อน — ดู §"แก้ข้อมูลรายงานเดิม"
>
> **ขอบเขต:** 653 ไฟล์ HTML (บทความ 618 + หน้าอื่น 35), Python 44 ไฟล์ (~13,000 บรรทัด), JSON 60 ไฟล์, JS 3 ไฟล์, CSS, `vercel.json`, `.env*`, `sitemap.xml`, `robots.txt`, `.gitignore`, git state และเว็บ production จริง
>
> **วิธีตรวจ:** `py_compile` ทุกไฟล์, `ruff` (F/E9/B/PLE/PLW/RUF), AST, สคริปต์สแกน HTML/JSON/Link แบบเขียนเอง, `git ls-files`/`git diff`/`git config`, DNS lookup, HTTP probe ไปที่ `krobjang.vercel.app`, และอ่านโค้ดทีละโมดูล (parallel review)

---

## 📊 ตัวเลขสำคัญ (วัดจริง ไม่ใช่ประมาณ)

| ตัวชี้วัด | ค่า |
|---|---|
| บทความบนดิสก์ / ใน `articles_index.json` | **618 / 500** → หายจาก index **118** |
| URL ใน `sitemap.xml` | 531 (1 หน้าแรก + 30 หมวด + 500 บทความ) → ขาดบทความ **118** |
| canonical ชี้ `https://krubjang.com` (DNS: **NXDOMAIN**) | **315 / 618** หน้า |
| ลิงก์ภายในเสีย (ปลายทางไม่มีไฟล์) | **248 จุด / 100 เป้าหมาย / 103 ไฟล์** |
| หัวข้อซ้ำ | **62 กลุ่ม ครอบ 208 ไฟล์** (ใน index ซ้ำ 109 รายการ) |
| meta description เสียเพราะ `"` ไม่ถูก escape | **64 หน้า** (1 หน้า markup พังทั้งแท็ก) |
| `og:title` / `twitter:title` เสีย | **3 หน้า** (6 แท็ก) |
| `alt` ของ `<img>` เสียเพราะ `"` | **10 หน้า / 35 รูป** |
| บทความที่มี raw JSON หลุดในเนื้อหา | **4 หน้า** (4 หน้าที่เนื้อหายาวที่สุด) |
| หน้าโหลด `style.css` ซ้ำ 2 ครั้ง | **300 / 618** |
| หน้าไม่มี canonical (ไม่ใช่บทความ) | **35** (30 หมวด + index + 404 + privacy + contact + google) |
| บทความขาด `article:published_time` / `wordCount` | **300 / 618** |
| meta description ถูกตัดกลางคำด้วย `...` | **549 / 618** |
| หน้าหมวดว่างเปล่า (0 การ์ด) แต่ยังอยู่ในเมนู/sitemap | **8** (car, cooking, horoscope, law, lottery, music, pet, tips) |
| รูป local ที่จะ 404 บน production | **24 จุด ใน 12 บทความใหม่ (2026-08-03)** |
| `images/` | 13,884 ไฟล์ / **2.4 GB** — `git ls-files images` = **0** |
| `pending_doctor` / `pending_publish` | **805** (ไฟล์ไม่มีจริง 187) / **100** |
| Python syntax errors | **0** (ทั้ง 44 ไฟล์คอมไพล์ผ่าน) |

---

## 🔴 P0 — วิกฤต (เว็บเสียหาย/ข้อมูลหาย/รั่ว)

### 1. เว็บหยุดอัปเดตตั้งแต่ 2 ส.ค. — push ล้มแต่ pipeline รายงานสำเร็จ
**หลักฐานจริง:**
- `site_state.json`: `last_publisher_run = 2026-07-31T21:09`, `errors` มี `Authentication failed for 'https://github.com/Kengwong1/KROBJANG.git/'` (2026-08-02)
- `git status`: `main...origin/main [ahead 1]` (commit `05e0f8c0` ค้าง), บทความ 08-03 **40 ไฟล์ยัง untracked**
- production: `https://krobjang.vercel.app/article_anime_20260803_222447_441.html` → **404**
- หน้าแรก production แสดงบทความล่าสุด **2026-07-31** (ในเครื่องมีถึง 08-03)

**ต้นเหตุเชิงโค้ด:** [`agent_publisher.py:273-301`](agent_publisher.py#L273) `push_github()` จับ `CalledProcessError` แล้วแค่ `log_err` + `state_บันทึก_error` **ไม่คืนค่า/ไม่ raise**; [`agent_publisher.py:321-333`](agent_publisher.py#L321) `main()` ยังพิมพ์ "✅ Publisher เสร็จ!"; [`run_all.py:74-88`](run_all.py#L74) ไม่สนใจผลตอบกลับ; [`run_all.py:162-180`](run_all.py#L162) พิมพ์ "✅ Quick/Full เสร็จ!" เสมอ; เส้นทาง publish ไม่มี exit code ที่สื่อความล้มเหลว → cron/Task Scheduler มองว่าสำเร็จ

**แก้:** ให้ `push_github()` คืน `bool`; `main()`/`pipeline_publish()` `sys.exit(1)` เมื่อ push fail; อย่าล้าง `pending_publish` และอย่าอัปเดต `last_publisher_run` เมื่อ fail; ตรวจ `git push` ด้วย remote แบบ token/credential helper ที่ถูกต้อง

---

### 2. 315 บทความ + robots.txt ชี้โดเมนที่ **ไม่มีอยู่จริง**
**หลักฐาน:** `Resolve-DnsName krubjang.com` → **DNS name does not exist** ขณะที่ `krobjang.vercel.app` ตอบ 200
- canonical/og:url 315 หน้า = `https://krubjang.com/...` (303 หน้าเป็น vercel)
- [`robots.txt:3`](robots.txt#L3) → `Sitemap: https://krubjang.com/sitemap.xml` → Google ตามไปไม่เจอ sitemap
- [`privacy.html:25`](privacy.html#L25), [`contact.html:26`](contact.html#L26) เขียนลิงก์ `https://krubjang.com` (ตาย)
- `index.html` (ทั้ง HEAD และไฟล์ใหม่) ไม่มี canonical

**ต้นเหตุ:** ค่า default ผิดใน [`site_core.py:21`](site_core.py#L21) และ [`agent_config.py:22`](agent_config.py#L22) (`https://krubjang.com` — สลับ j/b) + [`agent_setup.py:98`](agent_setup.py#L98) เขียนค่านี้ลง `.env.example`; หน้าเก่าถูก generate ตอน `.env` ยังผิด (ปัจจุบัน `.env` แก้เป็น `https://krobjang.vercel.app` แล้ว แต่หน้าเก่าไม่ถูก regenerate)

**แก้:** ตั้ง default = `https://krobjang.vercel.app`, regenerate canonical/og ทุกหน้า (หรือทำ rewrite one-off 315 ไฟล์), แก้ robots/privacy/contact, เพิ่ม canonical ให้หน้าหมวด/index

---

### 3. `articles_index.json` ถูกตัดถาวรที่ 500 → บทความ 118 หายจากทุกหน้า
[`site_core.py:204-211`](site_core.py#L204):
```python
json.dumps(data[:500], ensure_ascii=False, indent=2)
```
- ไฟล์จริง 618 / index 500 → 118 บทความหายจาก index, sitemap, search-index, หน้าหมวด
- ผลข้างเคียง: 8 หน้าหมวดกลายเป็นหน้าว่าง, movie/diy แสดง 1 จาก 2 บทความ (ดู §11)
- **ยิ่งร้าย:** `อ่าน_index()` กลืน JSON error แล้วคืน `[]` ([`site_core.py:196-202`](site_core.py#L196)) และ `เขียน_index()` เขียนทับตรง ๆ ไม่ atomic → ถ้า process ตายกลาง write ไฟล์เสีย → รอบถัดไปอ่านได้ `[]` → เขียนทับด้วย 1 รายการ = **index หายทั้งหมด**

**แก้:** ลบ `[:500]` (หรือ 5000), เขียนแบบ temp + `os.replace`, backup, และ prune รายการที่ไฟล์หายก่อนบันทึก

---

### 4. ไม่มี HTML escaping → metadata พัง 64+3+10 หน้า และมี markup เพี้ยนจริง
หัวข้อ/คำอธิบาย/แคปชันถูกต่อเข้า attribute ตรง ๆ:
- [`agent_writer.py:2418-2431`](agent_writer.py#L2418) สร้าง `_desc` จากข้อความ แล้วยัด [`2444`](agent_writer.py#L2444) `content="{_desc}"` — ถ้าเนื้อหามี `"` attribute ปิดก่อนกำหนด
- [`2438-2450`](agent_writer.py#L2438) `og:title`, `twitter:title`, `og:description` ใช้ `{หัวข้อ}` ดิบ
- [`2334`](agent_writer.py#L2334) `alt="{หัวข้อ}"`, [`2025`](agent_writer.py#L2025) `alt="{caption}"`
- [`2388`](agent_writer.py#L2388) share URL `?text={หัวข้อ}` ไม่ encode; [`2392`](agent_writer.py#L2392) Telegram
- [`agent_publisher.py:63`](agent_publisher.py#L63), [`:152`](agent_publisher.py#L152) การ์ดหน้า index/หมวด: `alt="{title}"` + `{title}`

**ผลที่วัดได้:**
- `article_technology_20260717_123206_095.html` → `og:title content="ยืนยันตัวตน "บัตรคนจน 2569"..."` → OG/Twitter/share ถูกตัดที่ `ยืนยันตัวตน`
- `article_health_20260716_202701_432.html`, `article_news_20260716_233751_448.html` → เสียเหมือนกัน (รวม 3 หน้า)
- 64 หน้า meta description ถูกตัดที่ `"` ตัวแรก
- `article_diy_20260714_223727_585.html` พังทั้งแท็ก (หลัง BS4 round-trip):
  `<meta (do="" content="..." it="" name="description" yourself)="" ...>`
- `agent_writer.py:26` import `html` มาแล้ว แต่ทั้งไฟล์เรียกแค่ `html.unescape()` ครั้งเดียว ([`:242`](agent_writer.py#L242)) — ไม่มี `html.escape()` เลย

**แก้:** `from html import escape`; escape ทุกจุดที่ interpolate ชื่อเรื่อง/desc/alt (attribute ต้อง `quote=True`); URL ใช้ `urllib.parse.quote`; regenerate หน้าที่พัง (อย่างน้อย 64+3+10)

---

### 5. รูป local ที่ git ไม่ได้ track → รูปแตกบน production (24 จุดในบทความใหม่)
- `git ls-files images` = **0** (`.gitignore` มี `images/`) แต่ `vercel.json` มี cache rule ให้ `/images/(.*)`
- `images/` ในเครื่อง = 2.4 GB / 13,884 ไฟล์
- production: `GET /images/favicon-32.png` → **404**, `GET /images/thumbs/anime/anime_0093.jpg` → **404**
- 12 บทความใหม่ (2026-08-03) มี `src="images/thumbs/..."` 24 จุด เช่น [`article_anime_20260803_122413_789.html`](article_anime_20260803_122413_789.html)

**ต้นเหตุ:** [`agent_writer.py:739-773`](agent_writer.py#L739) `_local_smart()` คืน path relative; [`site_core.py:468-490`](site_core.py#L468) `get_image_url()` คืน local ก่อน; [`agent_writer.py:941-951`](agent_writer.py#L941) `_svg_thumbnail()` ชื่อ/docstring บอก data-URI แต่ branch แรกคืน path relative `images/thumbs/...`; `_CAT_STRATEGY` ([`agent_writer.py:839-861`](agent_writer.py#L839)) ไม่มีหลายหมวด (ghost, comedy, inspirational, business, …) → ตกไป default ที่เริ่มด้วย `"local"`

**แก้:** เลือกนโยบายเดียว — commit `images/` ที่ใช้จริง **หรือ** ให้ writer/publisher รับเฉพาะ `http(s)`/`data:` และ fallback เป็น SVG data-URI (ที่ทำงานจริง) แทน path local; แก้ `_svg_thumbnail` ให้คืน data-URI จริง

**บั๊กพ่วง:** [`agent_writer.py:2414`](agent_writer.py#L2414) เรียก `_validate_hero_url()` **หลัง** สร้าง `hero_html` ([:2329](agent_writer.py#L2329)) และ `og_image` ([:2302](agent_writer.py#L2302)) แล้ว → การ reject มาสายเกินไป ไม่มีผลกับรูปที่แสดงจริง

---

### 6. เนื้อหาบทความมี raw JSON หลุด 4 หน้า (รวม meta description)
ตัวอย่าง [`article_food_20260730_001758_185.html`](article_food_20260730_001758_185.html):
```html
<h2>"ห": "บทนำจี้ใจ"</h2>
<h2>"desc": "อาหารที่ดีต่อสุขภาพไม่เพียงแต่..."</h2>
...
<figcaption>"desc": "อาหารที่ดีต่อสุขภาพไม่เพียงแต่..."</figcaption>
```
- meta description เริ่มด้วย `""ห": "บทนำจี้ใจ" ...` (attribute พัง)
- หน้าอื่น: `article_health_20260718_202923_542.html`, `article_news_20260725_001903_789.html`, `article_travel_20260730_204730_106.html`
- ทั้ง 4 หน้าคือ 4 บทความที่เนื้อหายาวที่สุด (13K–28K ตัวอักษร) และมี h2 เกินปกติ (13–27)

**ต้นเหตุ:** [`agent_writer.py:1557-1571`](agent_writer.py#L1557) `_parse()` fallback สุดท้ายเอา "ทุกบรรทัด" มาเป็น section (`lines → {"h": l}`) โดยไม่กรอง JSON; [`1578-1591`](agent_writer.py#L1578) `_normalize()` ไม่ตรวจคุณภาพหัวข้อ/ไม่จำกัดจำนวน section; [`_กรอง()` 1652-1747](agent_writer.py#L1652) ไม่มีขั้นลบ `"h":`/`"desc":`/`"a":`

**แก้:** ตรวจ JSON ก่อน fallback (ถ้าพบ `"h"`/`"desc"` ให้ถือว่า parse fail), กรองหัวข้อที่ขึ้นต้นด้วย `{`/`"`/`[`, จำกัด 5–7 section, และเพิ่ม sanitizer ใน `_กรอง`

---

### 7. `index.html` (ไฟล์ใหม่ 28 KB ที่ยังไม่ commit) ใช้งานไม่ได้ + publish จะทับทิ้ง
- `git status: M index.html` — HEAD เป็น template เดิม 8.8 KB, ไฟล์ในเครื่องเป็นดีไซน์ใหม่ 28 KB (835 บรรทัด diff)
- การ์ดทั้ง 12 ใบเป็น `<article class="article-card">` **ไม่มี `<a href>`** → คลิกไม่ได้ (แต่ CSS ใส่ `cursor:pointer` ที่ [`index.html:278`](index.html#L278))
- ช่องค้นหาเป็น `<div class="navbar-search">🔍</div>` ([`540`](index.html#L540)) ไม่มี handler; **ไม่มี `<script>` ทั้งไฟล์** → ไม่โหลด `nav.js`
- ไม่มี `<meta name="description">`, ไม่มี canonical, ไม่มี `manifest`/favicon
- ถ้ารัน `run_all.py --publish` → [`agent_publisher.py:137-245`](agent_publisher.py#L137) `rebuild_index_html()` เขียนทับด้วย template เก่าทันที → ดีไซน์ใหม่หาย

**แก้:** ก่อน publish ให้ commit/save ดีไซน์ใหม่, เปลี่ยนการ์ดเป็น `<a>`, เพิ่ม search JS หรือใช้ `nav.js`, เพิ่ม meta/canonical/manifest, และแก้ `rebuild_index_html` ให้ไม่ทับถ้าเป็นหน้า custom (หรือย้ายไป template)

---

### 8. GitHub Personal Access Token ฝังใน `.git/config` แบบ plaintext
```
[remote "origin"]
    url = https://Kengwong1:ghp_****************@github.com/Kengwong1/KROBJANG.git
```
- token อยู่ในไฟล์ config (และอาจติดใน history ของ shell/backup)
- **ยังไม่พบ** token ใน `site_state.json` (รายงานเดิมกล่าวเกินจริง — state มีแค่ URL ที่ git ปิดรหัสแล้ว)

**แก้:** revoke token ทันที, เปลี่ยนเป็น `gh auth`/credential helper/SSH, ล้าง remote URL, rotate คีย์อื่นที่อาจรั่วจากเครื่องเดียวกัน

---

## 🟠 P1 — สูง (ผู้ใช้/SEO เห็นชัด)

### 9. ลิงก์ภายในเสีย 248 จุด
- 100 ปลายทางไม่มีไฟล์จริง, กระจายใน 103 ไฟล์; **ทั้ง 248 จุดอยู่ในกล่อง "บทความที่เกี่ยวข้อง"** (ตรวจแยกแล้ว)
- ต้นเหตุ: [`agent_writer.py:2035-2055`](agent_writer.py#L2035) `_related_html()` ดึงจาก index แล้ว bake ลิงก์ลง HTML โดย**ไม่เช็กว่าไฟล์ปลายทางยังมีอยู่**; [`site_core.py:204-207`](site_core.py#L204) ตัด index ทิ้งทำให้รายการเก่าหาย
- ตัวอย่าง: `article_business_20260602_213747_589.html` (7 ลิงก์), `article_anime_20260602_223447_344.html` (6)

**แก้:** ตอน doctor/publish ให้ตรวจ `related-box` ทุกลิงก์กับไฟล์จริง ลบ/แทนที่ลิงก์เสีย; และ `_related_html` ควรกรอง `Path(filename).exists()`

---

### 10. หัวข้อซ้ำ 62 กลุ่ม / 208 ไฟล์ — โค้ดกันซ้ำถูกทิ้ง
- กลุ่มใหญ่สุด: `ธุรกิจในยุคดิจิทัล` = **15 บทความ**, `เทคโนโลยีการศึกษา` = **12**, `ผีสางในประเทศไทย` = **12**
- [`agent_writer.py:51`](agent_writer.py#L51) import `เช็คซ้ำ` แต่ **ไม่เคยเรียก** (ruff F401)
- [`agent_writer.py:1357-1372`](agent_writer.py#L1357) `_คิดหัวข้อจากเว็บ()` (ตัวที่ใช้จริงใน [:1477](agent_writer.py#L1477)) ส่งรายการ "ห้ามซ้ำ" ไปใน prompt เฉย ๆ **ไม่ตรวจผลลัพธ์**
- `_คิดหัวข้อจากรูป()` (มี `_is_dup`) เป็น **dead code** — ไม่ถูกเรียกที่ไหน
- `article_beauty_20260703_161431_372.html` และ `_20260706_231746_935.html` มี meta description ซ้ำกันเป๊ะ

**แก้:** เรียก `เช็คซ้ำ()` หลังสร้างหัวข้อ (normalize ช่องว่าง/เครื่องหมาย), ถ้าซ้ำให้ retry, และตรวจซ้ำก่อน `บันทึกบทความ`

---

### 11. หน้าหมวดว่าง 8 หน้า แต่ยังอยู่ในเมนูและ sitemap
| หน้า | การ์ด | บทความบนดิสก์ |
|---|---|---|
| car, cooking, horoscope, law, lottery, music, pet, tips | **0** | 0–2 |
| movie, diy | 1 | 2 |

สาเหตุเดียวกับ §3 (index 500) + [`agent_publisher.py:58`](agent_publisher.py#L58) `articles[:50]` แต่หัวหน้าประกาศ `len(articles)` ([`:116`](agent_publisher.py#L116)) → ถ้าหมวด > 50 ตัวเลขกับรายการไม่ตรง

**แก้:** rebuild หลังแก้ index; ถ้าหมวดไม่มีบทความให้ `noindex`/ซ่อนจากเมนู/sitemap; ลบ `[:50]` หรือทำ pagination

---

### 12. CSS โหลดซ้ำ 300 หน้า + cache ผิดนโยบาย
- [`agent_writer.py:2455-2456`](agent_writer.py#L2455): ทั้ง `href="/style.css"` และ `href="style.css"` (300/618)
- [`vercel.json:33-41`](vercel.json#L33): CSS `max-age=31536000, immutable` แต่ `style.css` ไม่มี hash → ผู้ใช้เดิมติด CSS เก่า 1 ปี

**แก้:** ลบ link ซ้ำ, เปลี่ยนเป็น `max-age=300`/`must-revalidate` หรือทำ filename hash

---

### 13. ช่องว่าง SEO metadata
- **35 หน้าไม่มี canonical** (30 หมวด + index + 404 + privacy + contact + google verification)
- **300 บทความขาด** `article:published_time` และ `wordCount` (318 มีแล้วจาก doctor รอบก่อน)
- **549 หน้า** meta description ถูกตัดที่ 155 ตัวอักษรแล้วเติม `...` (ตัดกลางคำ เพราะไทยไม่มีเว้นวรรค) — [`agent_writer.py:2422`](agent_writer.py#L2422)
- **45 หน้า** `<title>` ยาวเกิน 65 ตัวอักษร (สูงสุด 76)
- 7 ไฟล์ใช้ description ซ้ำ (3 หน้า static ใช้ค่าเดียวกัน), 1 ไฟล์ description ว่าง (`article_food_20260730_001758_185.html`)
- `datePublished` **618/618** ไม่มี timezone ([`agent_writer.py:2374`](agent_writer.py#L2374) `now.isoformat()`), JSON-LD ไม่มี `dateModified`/`mainEntityOfPage`
- หน้าหมวด/index ไม่มี `og:*` เลย

**แก้:** สร้าง meta จากย่อหน้าแรกที่ตัดที่ขอบประโยค (หรือใช้ AI สรุป 150 ตัวอักษร), ใส่ timezone `+07:00`, เพิ่ม canonical ให้หน้าหมวด, จำกัด title ≤ 60

---

### 14. `agent_doctor` มีขั้นตอนที่ "ไม่ทำงานจริง" หลายจุด
- **Breadcrumb 0/618:** [`agent_doctor.py:364`](agent_doctor.py#L364) หา `<(?:main|article)>` แต่ template บทความไม่มีแท็กนี้ (วัดแล้ว 0 ไฟล์มี `<main>`/`<article>`) → ไม่เคยแทรก
- **Reading time 0/618:** [`agent_doctor.py:295`](agent_doctor.py#L295) เช็ค `"อ่าน" not in txt[:3000]` แต่ทุกหน้ามี "⏱ อ่าน ~5 นาที" อยู่แล้ว; และ `date_m` ([`:298`](agent_doctor.py#L298)) match **0 ไฟล์** (regex ต้องมีแท็กปิด แต่ `.article-meta` ถูกตามด้วย `<a>`)
- **`wordCount` ผิด ~2 เท่า:** [`agent_doctor.py:324`](agent_doctor.py#L324) `len(re.sub(r'<[^>]+>',' ',txt).split())` นับ CSS/JS ใน `<head>` (~10 KB/หน้า) และ `.split()` ไม่มีความหมายกับภาษาไทย (ไม่มีเว้นวรรค)
- **`fix_seo()` ไม่ fix:** [`agent_doctor.py:458-486`](agent_doctor.py#L458) แค่รายงาน แต่ `run_all.pipeline_fix` ประกาศขั้น "4/4 แก้ SEO meta..."

**แก้:** anchor breadcrumb ที่ `<div class="article-wrap">`, คำนวณ reading time จาก `div.content`, ตัด `<script>/<style>` ก่อนนับคำ, และอย่าประกาศว่า "แก้" ถ้าแค่รายงาน

---

### 15. `run_all.py` เรียก `fix_articles()` ซ้ำ 3 รอบ + ไม่มี exit code
[`run_all.py:56-63`](run_all.py#L56):
```python
print("  1/4 ลบ instruction artifacts...");  agent_doctor.fix_articles()
print("  2/4 แก้ nested anchor...");         agent_doctor.fix_articles()   # ฟังก์ชันเดียวกัน
print("  3/4 ตรวจ HTML bugs...");            agent_doctor.fix_articles()   # ฟังก์ชันเดียวกัน
print("  4/4 แก้ SEO meta...");              agent_doctor.fix_seo()        # แค่รายงาน
```
- งาน 3 อย่างที่ประกาศไม่มีอยู่จริง; เลขขั้นกระโดด `1/4…4/4` → `5/7` ([`:66`](run_all.py#L66)) ทั้งที่ไม่มี 6/7, 7/7
- [`run_all.py:43-48`](run_all.py#L43) กลืน exception ต่อบทความแล้วไปต่อ → ทั้งรอบอาจล้มเหลวทุกบทความแต่ exit 0
- [`run_all.py:88`](run_all.py#L88) เรียก `push_github()` ทิ้งค่าที่คืน
- `pipeline_quick`/`pipeline_full` พิมพ์สำเร็จเสมอ

**แก้:** เรียก doctor ครั้งเดียว, ทำขั้นที่ประกาศจริงหรือเปลี่ยนชื่อขั้น, รวม error แล้ว `sys.exit(1)` เมื่อมีข้อผิดพลาด/push fail

---

### 16. Facebook/LINE ปิดเงียบ และลิงก์โซเชียลเป็น handle ภาษาไทย
- [`agent_writer.py:2788`](agent_writer.py#L2788) `if not FB_PAGE_ID or not FB_ACCESS_TOKEN: return` — `.env` มี `FB_PAGE_TOKEN` (305 ตัวอักษร) แต่ `FB_ACCESS_TOKEN` **ว่าง** → return ทุกครั้ง ไม่มี log
- [`agent_writer.py:2793-2794`](agent_writer.py#L2793) ไม่เช็ค `status_code` ของ Graph API; `if รูป: data["link"] = url` — ไม่ใช้ `รูป` เลย (ควรเป็น `picture`)
- LINE token ว่าง → [`โพส_line`](agent_writer.py#L2799) return เงียบ
- [`agent_writer.py:2403-2406`](agent_writer.py#L2403): `tiktok.com/@ครบจัง`, `youtube.com/@ครบจัง`, `twitter.com/ครบจัง` → ทั้ง 3 ลิงก์เสีย (handle ไทย); `.env` มี `FACEBOOK_URL`/`YOUTUBE_URL`/`TIKTOK_URL` แต่ไม่มีโค้ดอ่าน
- `agent_setup.py:113` เขียน `FB_ACCESS_TOKEN=your_fb_token` → ค่า placeholder ไม่ว่าง → โค้ดจะยิง API ด้วย token ปลอมและล้มเงียบ

**แก้:** ใช้ `FB_PAGE_TOKEN` หรือ map ชื่อให้ตรง, ตรวจ `r.ok`/log error, ใช้ `picture`, อ่าน social URL จาก env, และตรวจ token ว่างแบบ placeholder

---

### 17. ธีมไม่ถูกบันทึก → rebuild/doctor คืนค่า blue
- [`agent_theme.py:89-133`](agent_theme.py#L89) `apply_theme()` เปลี่ยนสีแต่**ไม่เขียน state**
- [`agent_theme.py:466-473`](agent_theme.py#L466) `do_rebuild()` อ่าน `s.get("theme","blue")` → ไม่มี key นี้ใน `site_state.json` (มีแค่ `layout`)
- [`agent_doctor.py:84-89`](agent_doctor.py#L84) ก็อ่าน `theme` จาก state → คิดว่าเป็น blue แล้วเขียน nav/footer/`--primary` กลับเป็น `#1e40af`

**แก้:** หลัง apply theme สำเร็จ `s["theme"]=name; เขียน_state(s)`; doctor อ่านค่าจาก state หรือ `.site_config.json`

---

### 18. `agent_doctor --all` ทำให้ `style.css` โตขึ้นทุกครั้ง
- [`agent_doctor.py:218-227`](agent_doctor.py#L218): ถ้า `.site-footer` มี `background:#1e40af` อยู่แล้ว การ replace ด้วยค่าเดิมทำให้ `new == old` → ไปต่อ fallback ที่ **append** `/* doctor fix */ .site-footer{...!important;}` ทุกครั้ง
- [`agent_doctor.py:187-194`](agent_doctor.py#L187): append `background/color` ใน `.site-nav` และ `color:#fff;` ใน `.nav-search-btn` ทุกครั้ง
- ผล: ไฟล์โตไม่หยุด + `!important` ทำให้เปลี่ยนธีมภายหลังไม่ติด (วัดจริงจากสำเนา: 5,272 → 5,313 → 5,354 bytes ในการรัน 2 ครั้ง)

**แก้:** append เฉพาะเมื่อ declaration ยังไม่มี/ค่าต่าง; เลิก `!important`; ทำให้ idempotent

---

### 19. `agent_setup.py` — `--reset` เป็น no-op, หน้า generated มี nav ว่าง, robots ถูกเขียนทับ
- [`agent_setup.py:543-545`](agent_setup.py#L543) ตั้ง `RESET=True` แต่ `_write()` ([`:31-37`](agent_setup.py#L31)) ใช้ `force` เฉพาะ `สร้าง_robots` ([`:351`](agent_setup.py#L351)) → `--reset` ไม่เขียน style.css/index/หมวด/nav/sw/manifest ตามที่ประกาศ
- `_nav_links()` ([`:39`](agent_setup.py#L39)) ไม่ถูกเรียกเลย → `404.html`/`privacy.html`/`contact.html`/`index.html` (และหน้า setup) มีแค่ logo ไม่มีเมนูหมวด
- `สร้าง_robots` ใช้ `force=True` → รัน `agent_setup.py` ธรรมดาลบ `Disallow` ที่ผู้ใช้เพิ่ม
- `.env.example` มี `SITE_URL=https://krobjang.vercel.app/` (slash ท้าย) + โค้ดต่อ `/sitemap.xml` ตรง ๆ → ได้ `//sitemap.xml`
- `ADSENSE_PUB` import แต่ไม่ใช้ (ruff F401) → หน้า generated ไม่มีโฆษณา

**แก้:** ส่ง `force=reset` ให้ทุก builder, render `{_nav_links()}`, `SITE_URL.rstrip("/")`, และเลิก `force` ยกเว้น reset

---

### 20. Service Worker / cookie banner / favicon / manifest เป็นของค้าง
- `serviceWorker.register` = **0 หน้า** → `sw.js` ไม่ทำงาน; ถึงเปิดก็ cache-first + `CACHE='v202604232341'` (เม.ย.) → เสิร์ฟ HTML เก่า
- `cookie-consent.js` ถูกอ้าง **0 หน้า**; ไม่มี `#cookie-banner` เลย
- ไม่มีหน้าไหนมี `<link rel="icon">` (0/653) ทั้งที่ `images/favicon-16/32.png` มีอยู่ (และ 404 บน production)
- [`manifest.json`](manifest.json) name/short_name = **"ไอหมอก"** แต่เว็บชื่อ "ครบจัง"; `description` ก็ของไอหมอก
- `thumbnails.json` 52 รายการ → ไฟล์ `.svg` **ไม่มีอยู่จริงทั้ง 52** และไม่มีโค้ด/HTML อ่าน
- `site-config.json` = "OnePoint" ธีมคาเฟ่ (ไม่เกี่ยวกับเว็บ) — ไม่มีโค้ดอ่าน
- [`index.html`](index.html) ไม่มี manifest/favicon ด้วย

**แก้:** ตัดสินใจเปิดหรือลบ sw/cookie; เพิ่ม favicon link; regenerate manifest จาก `SITE_NAME`; ลบ/ซ่อม thumbnails.json + site-config.json

---

## 🟡 P2 — บั๊กในโค้ด (ทำงานผิด/ทำลายข้อมูลเมื่อรัน)

### 21. `agent_video.py` — โมดูลวิดีโอมีบั๊กทำให้ผลลัพธ์ผิด/ค้าง
- **`:1432`** `soup.find(class_="article-body")` แต่ template จริงใช้ `class="content"` (618/618) → parse h2 ไม่ทำงาน, ทุกวิดีโอได้ heading = ชื่อบทความซ้ำ 5 ครั้ง
- **`:1708-1713`** `--cat` ตรวจ `stem.startswith(cat+"_")` แต่ไฟล์ชื่อ `article_ghost_...` → `--cat ghost` คืน 0 ไฟล์ตลอด
- **`:1227-1229`** `while s < 0.5: s /= 0.5` — ถ้า `--tts-speed 0` หรือค่าลบ → **infinite loop** (0/0.5=0)
- **`:181-182`** vision check คืน `"ใช่" in ans` → คำตอบ "ไม่ใช่" มี substring "ใช่" → ผ่านตลอด; `"true" in "not true"` ก็ผ่าน
- **`:775-781`** Picsum fallback ฮาร์ดโค้ด 1080×1920 ไม่ resize → `--format square/landscape` ทำ `Image.alpha_composite` โยน `ValueError: images do not match`
- **`:539-543`** Fooocus path copy รูป 576×1024 โดยไม่ resize → ValueError เดียวกัน
- **`:1670-1674`** `_mix_bgm()` ล้มเหลวแต่ `log_ok("BGM มิกซ์เสร็จ")` + ลบไฟล์ BGM
- **`:1655-1667`** `total_dur = sum(max(5.0,1.0) ...)` = ค่าคงที่ 5×จำนวนคลิป; ถ้าไม่มี `ffprobe` จะข้าม BGM
- **`:1525-1530`** ไม่เช็กผล `_get_best_image` → ถ้ารูป fail ทั้งหมด `_make_ken_burns_clip` โยน `FileNotFoundError` (ถูกกลืนที่ `except` ทำให้วิดีโอหายทั้งเรื่อง)
- **`:435-448`** dict key `"ghost"` ซ้ำ (ruff F601) — ค่าแรกถูกทับ

> `agent_video` ไม่อยู่ใน `run_all` (รันแยก) ความรุนแรงจึงจำกัดที่ผู้ใช้สั่งทำวิดีโอ

**แก้:** ใช้ `class="content"`, `article_{cat}_`, clamp speed/format, ตรวจขนาดภาพก่อน composite, ตรวจ `r.ok`/ผลฟังก์ชัน, ใช้ `c.duration`

---

### 22. `agent_image.py` — pipeline แก้รูปเสี่ยงทำลายรูปทั้งคลัง
- **`:1029-1035` + `:870-935`** `_vision_check_image()` คืน `False` ทั้งกรณี HTTP error/timeout/คำตอบกำกวม; `แก้รูปผิด()` ตีความ `False` = รูปผิด → ไล่เปลี่ยนรูป (Phase 1–3) รวม Phase 3 ที่ไม่ vision-check → Ollama สะดุดครั้งเดียว = รูปที่ถูกถูกสลับทั้งเว็บ
- **`:1307-1319, 1321-1323, 1420-1454`** `_load_index` กลืน error → `[]`; `_save_index` เขียนทับไม่ atomic; `harvest_category` เช็กชื่อไฟล์จาก index เท่านั้น → index เสีย = โหลดทับ `cat_0001.jpg...` (URL เดิมได้ภาพคนละใบ, credit ผิด)
- **`:256-257, 314-325, 367-372`** dedupe ไม่กัน `new_src.startswith("http")` → ถ้าคลังว่าง `get_image_url` คืน `picsum.photos` แล้วเขียนลงบทความ
- **`:1145-1181`** `อัปเดต_search_index()` หา `var SEARCH_DATA` ซึ่ง **ไม่มีในเว็บเลย (0 ไฟล์)** → no-op ทุกครั้ง
- **`:945`** `title_clean` คำนวณแล้วไม่ใช้ (ruff F841) → "download ตามหัวข้อ" ค้นด้วยชื่อหมวด
- **`:73-77`** `_cat_of()` split `_` → หมวดที่มี underscore จะได้หมวดผิด (ปัจจุบันยัง latent)
- **`:1174`** ruff B023 เป็น **false positive** (re.sub เรียก lambda แบบ synchronous) — ไม่ต้องแก้
- **`:1663-1665` vs `:1752`** `--tag --status` เข้า branch `--status` ก่อน → ไม่เคยแสดง tag status

**แก้:** ใช้ 3 สถานะ (`True/False/None`) โดย `None` = เก็บรูปเดิม, atomic index, กัน `http` ก่อน assign, ใช้ `search-index.json` แทน SEARCH_DATA

---

### 23. `agent_checker.py` — QC ที่ใช้งานจริงไม่ได้
- **`:17`** `BASE_PATH = Path(".")` → รันจาก CWD อื่นไม่เจอไฟล์; **`:16`** hardcode `VISION_MODEL="qwen3-vl:2b"` ทับค่าที่ import
- **`:95-116`** `_yn()` คืน `False` เมื่อ parse ไม่ได้; `on_topic` default False → รูปดีถูกตัดสิน "ผิดหมวด" (ตอบไทย/ตอบเป็นประโยค/ถูกตัดกลาง = False) แล้วแทนด้วย Pexels สุ่ม
- **`:124`** vision error → `{"ok": True}` = false all-clear
- **`:241-253`** แทนรูปแล้วไม่อัปเดต `articles_index.json`/credit
- ไม่ถูกเรียกจาก `run_all.py` เลย → ไม่มี QC ในไปป์ไลน์จริง

**แก้:** ใช้ `BASE_PATH` จาก site_core, ใช้ `OLLAMA_VISION_MODEL`, 3 สถานะ, error = `None`/exit 2, อัปเดต index

---

### 24. `gemini_core.py` — โมดูล 262 บรรทัดที่ไม่มีใครใช้ + API key ใน URL
- ไม่มีไฟล์ไหน import `gemini_core` (grep ทั้ง repo เจอแค่ docstring ของตัวเอง) → `GEMINI_API_KEY` ใน `.env` ไม่ถูกใช้; ทุกบั๊กในไฟล์เป็น latent
- [`gemini_core.py:36`](gemini_core.py#L36) `...generateContent?key={key}` → key อยู่ใน query string (proxy/log); `:139` log `str(e)` ที่ฝัง URL เต็ม (มี key)
- `:105-119` 429 ครั้งเดียวตั้ง `_quota_exhausted=True` → mute ทั้ง process; `:107` `int(Retry-After)` ระเบิดเมื่อเป็น HTTP-date; `:155/169` บีบ timeout ของ caller เหลือ 120/60 วิ

**แก้:** ต่อสายหรือลบไฟล์; ใช้ header `x-goog-api-key`; แยก 429 รายนาที/รายวัน; parse Retry-After แบบปลอดภัย

---

### 25. `site_core.py` — เขียน state/index ไม่ atomic + helper ที่ escape ไม่ครบ
- [`site_core.py:150-155`](site_core.py#L150), [`204-211`](site_core.py#L204): `write_text` ทับตรง ๆ; ถ้า crash กลาง write → JSON เสีย → `อ่าน_state`/`อ่าน_index` คืน default/`[]` → รอบถัดไปเขียนทับ = data loss
- [`site_core.py:248-271`](site_core.py#L248) `สร้าง_thumbnail_svg()` ใส่ `หัวข้อ[:30]` ลง SVG โดย escape แค่ `"`/`'` ไม่ escape `&`/`<` → SVG invalid (เช่นชื่อมี `&`)
- [`site_core.py:273-278`](site_core.py#L273) `เช็คซ้ำ()` ใช้ substring สองทาง → over-block ("กาแฟ" กับ "กาแฟสด") และ under-block (ชื่อต่างกันแต่ความหมายเดียวกัน)
- [`site_core.py:324-342`](site_core.py#L324) `_load_local_index` ถ้า index เป็น dict จะคืน dict (ไม่ใช่ list) → `_pick_best` วน key แทน record (latent)

**แก้:** temp+`os.replace`+backup, escape XML, ใช้ normalized equality/Levenshtein สำหรับ dedupe, validate type

---

### 26. `agent_config.py` — เขียน `.env` ทับ/ค่า default ผิด/JS ที่ generate ไม่ตรงกับ nav.js จริง
- [`agent_config.py:188-248`](agent_config.py#L188) `_merge_env` เขียน `.env` ใหม่ทั้งไฟล์ → comment/format/ลำดับหาย; ค่าที่มี `#`/quote อาจเพี้ยน
- [`agent_config.py:22`](agent_config.py#L22) `SITE_URL="https://krubjang.com"` (ตาย) และ [`agent_setup.py:98`](agent_setup.py#L98) เขียนลง template
- [`agent_config.py:251-310`](agent_config.py#L251) `_generate_nav_js()` สร้าง nav ที่ `insertAdjacentHTML` ทับหน้า + ลิงก์ absolute `${SITE_URL}...`; แต่ `nav.js` จริงเป็น IIFE ค้นหา → ถ้ารัน `--apply` จะได้ nav คนละแบบและซ้ำซ้อน
- [`agent_config.py:407-411`](agent_config.py#L407) CSS ที่ generate ใช้ `.cards-grid` แต่หน้าเว็บใช้ `.article-grid` (style.css) → layout ไม่ตรง

**แก้:** ใช้ `python-dotenv` set_key หรือ merge แบบรักษา comment, default domain ให้ถูก, เลิก generate nav ถ้าไม่ใช้, รวม CSS ให้ตรง selector

---

### 27. `agent_writer.py` — บั๊กเฉพาะจุด
- [`2626`](agent_writer.py#L2626) `article_title or หัวข้อ_บทความ` — `หัวข้อ_บทความ` ไม่มีใน scope (ruff F821) → `NameError` ถ้าหัวข้อว่าง
- [`2418-2431`](agent_writer.py#L2418) บล็อกสร้าง `_desc` ซ้ำ **2 ชุด** (patch รัน 2 ครั้ง) — ทำงานซ้ำ, import ซ้ำ
- [`941-951`](agent_writer.py#L941) `_svg_thumbnail` คืน path relative ไม่ใช่ data-URI ตามชื่อ/docstring
- [`778-833`](agent_writer.py#L778) `_local_generated` ชี้ `images/generated/<cat>` ซึ่ง **ไม่มีโฟลเดอร์นี้** → คืน `""` ทุกครั้ง (dead branch)
- [`1997-2029`](agent_writer.py#L1997) `_figure_html` ไม่ escape `caption` ใน `alt`/`figcaption`/SVG
- [`2757`](agent_writer.py#L2757) ชื่อไฟล์สำรอง `article_{cat}_{YYYYmmdd_HHMMSS}.html` ไม่มี random → 2 บทความวินาทีเดียวกันเขียนทับ (cluster mode [`2867`](agent_writer.py#L2867) ก็ไม่มี `%f`)
- [`2865-2873`](agent_writer.py#L2865) `if result:` — `เขียนบทความ` คืน tuple 4 ค่าเสมอ (truthy) → เงื่อนไขไม่มีความหมาย
- [`2792`](agent_writer.py#L2792) `data["link"] = url` ไม่ได้ใช้ `รูป` (ควร `picture`)
- `prev = html_sec[-300:]` ([`2686`](agent_writer.py#L2686)) ตัดบริบทเหลือ 300 ตัวอักษรสุดท้าย (ตั้งใจหรือไม่ก็ตาม — ทำให้ model ไม่เห็นเนื้อหาก่อนหน้า)

**แก้:** ลบ `or หัวข้อ_บทความ`, ลบบล็อก desc ซ้ำ, ให้ `_svg_thumbnail` คืน data-URI, escape caption, ใช้ `สร้างชื่อไฟล์()` ที่มี random, เก็บ `prev` เป็นข้อความมากพอ

---

### 28. `patch_*.py` — สคริปต์ one-off ที่รันซ้ำแล้วทำ source พัง
- [`patch_hero_blocklist.py:10-20`](patch_hero_blocklist.py#L10): anchor คือบรรทัด `def _validate_hero_url` ที่ไม่ถูกแก้ → รันซ้ำเพิ่ม `_HERO_BLOCKLIST` ทุกครั้ง (1→2→3)
- [`patch_meta_desc.py:13-27`](patch_meta_desc.py#L13): anchor ยังอยู่หลัง patch → รันซ้ำแทรกบล็อกซ้ำ (หลักฐานจริง: `agent_writer.py:2418-2431` มี 2 บล็อก)
- [`patch_setup_index.py:26-42`](patch_setup_index.py#L26): target ไม่มีแล้ว; fallback อาจลบ `<div class="nav-links">...</div>` ทั้งบรรทัดออกจาก template
- [`patch_wiki_query.py:55-60`](patch_wiki_query.py#L55): PATCH 1/2 แยกกัน; ถ้า PATCH 1 ไม่ match แต่ 2 match → `_query` undefined (NameError ถูกกลืน)
- [`patch_youtube_fix.py:13-16`](patch_youtube_fix.py#L13): แทนฟังก์ชันทั้งก้อนทุกรอบ → ย้อน fix ที่ทำทีหลัง
- ทุกตัวใช้ path อิง CWD, ไม่มี backup/`--dry-run`/idempotency marker

**แก้:** เก็บไว้ใน `_archive/` หรือเพิ่ม guard `if already_patched: exit 0`, เขียน `.bak`, `py_compile` หลัง patch, ใช้ `Path(__file__).parent`

---

### 29. สคริปต์ตรวจ/ซ่อมที่รายงานผลหลอก
- [`check_vercel_live.py`](check_vercel_live.py), [`check_vercel_css.py`](check_vercel_css.py): ไม่มี try/except, hardcode host, exit 0 เสมอ → ใช้ gate deploy ไม่ได้
- [`fix_index_images.py:94`](fix_index_images.py#L94): `Path("articles_index.json")` อิง CWD; `json.load(index_path.open())` ไม่ปิดไฟล์; เลือกรูปตามหมวด (ไม่ใช้หัวข้อ) ขัด docstring
- [`fix_local_images.py:47`](fix_local_images.py#L47): `used=set()` mutable default (ruff B006); `Path(".").glob` → รันนอก repo รายงาน "แก้ 0 รูป" exit 0
- [`check_category_imgs.py`](check_category_imgs.py), [`check_colors.py`](check_colors.py): hardcode `lifestyle.html`/`style.css` ไฟล์เดียว
- [`clean_local_images.py:179-181`](clean_local_images.py#L179): reply ยาวแต่ไม่มี keyword → `MISMATCH` → `--move` ย้ายรูปออกทั้งหมวด และไม่ prune `_index.json` → บทความชี้ไฟล์ที่ไม่มี
- [`index_thumbs.py`](index_thumbs.py) `--force` → สร้าง record ใหม่ `description:""` ทับ tag ทั้งหมด (ต้นทุน vision หาย)
- [`check_thumbs.py:58-67`](check_thumbs.py#L58): `not_indexed` ติดลบได้ → ไม่เตือน; นับ `_mismatch` เป็นหมวด

**แก้:** ใช้ `BASE_PATH`, `with open`, `sys.exit(1)` เมื่อล้มเหลว/พบ 0 ไฟล์, เก็บ description เดิม, prune index

---

### 30. คิว/state เพี้ยนและไม่ถูกใช้
- `pending_doctor` = **805** รายการ แต่ไฟล์บนดิสก์มี 618 → **187 รายการชี้ไฟล์ที่ถูกลบแล้ว**; ไม่มีโค้ด prune
- `pending_publish` = 100; `published_today` = 722 (ไม่เคย reset รายวัน), `total_articles` = 822 (มากกว่าจำนวนไฟล์จริง 618)
- [`agent_publisher.py:294`](agent_publisher.py#L294) `published_today += len(pending_publish)` ทุกครั้งที่ push สำเร็จ (นับซ้ำ/ผิด)
- `state_ล้าง_pending_publish()` ล้างทั้งหมดแม้ push บางส่วน

**แก้:** prune คิวกับไฟล์จริงตอน start, reset `published_today` ตามวันที่, คำนวณ `total_articles` จาก index/ดิสก์

---

### 31. Repo/deploy hygiene ที่ทำให้เกิดบั๊กซ้ำ
- [`.gitignore`](.gitignore) มี byte **UTF-16LE 41 NUL** ต่อท้ายบรรทัด (ไฟล์ไบนารี) → บล็อกท้าย (`agent_*.py`, `config.py`, `run_all.py`, `.env`, `images/`) อ่านไม่ตรง; และ `*.py` ถูก ignore → **source code ไม่อยู่ใน git เลย** (แก้ bug แล้วไม่มีประวัติ/CI)
- `README.md` มีบรรทัดเดียว `# KROBJANG` — ไม่มีวิธีรัน/env
- ไฟล์ dev artifacts ถูก track/deploy: `clean_report.json`, `fix_report_20260507_212726.json`, `thumbnails.json`, `site_state.json` (46 KB), `videos/article_lifestyle_...mp4` (**7.4 MB**)
- `site_state.json` เปิดให้เข้าถึงจากสาธารณะ: `GET https://krobjang.vercel.app/site_state.json` → **200 / 43 KB** (มี error log, คิว, สถิติ)
- ไม่มี `.vercelignore`; `vercel.json` ตั้ง `outputDirectory: "."` → ถ้า deploy ด้วย Vercel CLI ทั้งโฟลเดอร์ (รวม `*.py`, `.env*`, `images/` 2.4 GB) อาจถูกอัปโหลด
  - **หมายเหตุ:** ตอนนี้ `.env`/`.env.local` บน production ตอบ **404** (ยังไม่รั่ว) — เป็นความเสี่ยงเชิงโครงสร้าง ไม่ใช่การรั่วที่เกิดแล้ว

**แก้:** เขียน `.gitignore` ใหม่เป็น UTF-8, เอา `*.py` ออก (หรือแยก private repo), เพิ่ม `.vercelignore`, ย้าย state/report ออกจาก web root, ใส่ README

---

## 🔵 P3 — ต่ำ / คุณภาพ/ความสอดคล้อง

32. **21 หน้า** มี `<h2>` ซ้ำกันในหน้าเดียว (เช่น `article_education_20260731_223922_271.html` มี "ตัวอย่างจากชีวิตจริง" 2 ครั้ง) และ 3 หน้ามี 13–27 section (เกิน 5–7 ที่ prompt กำหนด) — [`agent_writer.py:1593`](agent_writer.py#L1593) ไม่จำกัดจำนวนหลัง parse
33. `article_health_20260718_202923_542.html` (28 KB ข้อความ) และ `article_travel_20260730_204730_106.html` ผิดปกติเมื่อเทียบหน้าปกติ (~4–6 KB) — ตรวจโครงสร้างแล้วพบ JSON artifact/หัวข้อซ้ำ (ดู §6)
34. `articles_index.json` มี 1 รายการ `image` เป็น `data:` URI (634 bytes) — ใช้เป็นการ์ดได้แต่ไม่ควรอยู่ใน index
35. `contact.html` บอก "กรุณาส่งอีเมลมาที่ด้านล่าง" แต่ **ไม่มีอีเมล/ฟอร์ม** ([`contact.html:25`](contact.html#L25)); `privacy.html`/`contact.html` ใช้ description สำเร็จรูป "บทความไทยคุณภาพ ครบทุกหมวด" และ hardcode โดเมนตาย
36. `404.html` ไม่มี `noindex`; `vercel.json` rewrite `/404` → `/404.html` แต่ static 404 ใช้ `404.html` อยู่แล้ว (ไม่เสียหาย แต่ซ้ำซ้อน)
37. `nav.js` สร้างผลลัพธ์ค้นหาด้วย `innerHTML` จาก title โดยไม่ escape ([`nav.js:16`](nav.js#L16)) — ถ้าหัวข้อมี `<`/`</a>` จะ inject; ปัจจุบันมี 2 หัวข้อที่มี `"` (ไม่ทำให้ลิงก์พัง แต่แสดงผลเพี้ยน)
38. `sw.js` เป็น cache-first และ `CACHE='v202604232341'` ค้างตั้งแต่ เม.ย. → ถ้าเปิดใช้จะเสิร์ฟ HTML เก่าตลอด; `PRECACHE` ไม่มี `/404.html`
39. `manifest.json` `theme_color:#1e40af` แต่หน้าแรกใช้ `--primary:#1e3a8a`; `screenshots: []`
40. `agent_theme.py` พารามิเตอร์ `grad` ไม่ถูกใช้, `--accent` ฮาร์ดโค้ด `#dbeafe`, regex nav.js ไม่ match อะไร, และแก้แค่ `background:` ไม่แก้ `color:` → ธีมเปลี่ยนแล้วสีผสม
41. `agent_doctor.py` อ่าน/เขียนด้วย `errors="ignore"` ([`:278`](agent_doctor.py#L278), [`:371`](agent_doctor.py#L371)) → ไฟล์ cp874 จะโดนตัดไบต์ไทยถาวร; `input()` ไม่มี guard non-TTY ([`:883`](agent_doctor.py#L883)); `--check` exit 0 ตลอด
42. `agent_image`/`fix_*` เขียน HTML ผ่าน BeautifulSoup `str(soup)` → attribute order/quote ถูก normalize (เห็นได้จาก 5 บทความที่ `<link href=... rel="canonical"/>` และ `article_diy_...` ที่ meta พังหนักขึ้น)
43. `agent_video` config drift กับ `site_core`: `CAT_COLORS`/`_CAT_STYLE` ขาดหลายหมวด; `OLLAMA_VISION_MODEL` fallback คนละค่า (`llama3.2-vision:latest` vs `qwen3-vl:2b`); `--count -1` → 617 ไฟล์
44. `agent_writer._search_wikipedia` ใช้ UA `github.com/krubjang` (typo domain) และ reference ที่ได้เป็น `[Wikipedia/ชื่อ]` ไม่มี URL — [`agent_writer.py:96`](agent_writer.py#L96), [`2178-2188`](agent_writer.py#L2178)
45. `_related_html`/`_faq_html`/`_references_html` ไม่ escape title/ref (เพิ่มความเสี่ยง markup พัง) — [`agent_writer.py:2047-2050`](agent_writer.py#L2047), [`2134-2147`](agent_writer.py#L2134)

---

## ✅ ตรวจแล้ว "ไม่ใช่บั๊ก" / คำเตือนที่ต้องระวัง

- **Python syntax:** 44/44 ผ่าน `py_compile`; **JSON:** 60/60 parse ผ่าน; **sitemap.xml:** XML well-formed
- **HTML:** ไม่มี `id` ซ้ำ (0 หน้า), ทุกบทความมี `<h1>` 1 ตัว, ทุก `<img>` มี attribute `alt` (แต่ค่าอาจถูกตัดตาม §4), ทุกหน้าใน sitemap มีไฟล์จริง (531/531)
- **Thai identifier ที่ดูเหมือนพัง ไม่ใช่บั๊ก:** `run_all.py` เขียน `แก้รูปซ้ําHash` (decomposed) ขณะที่ `agent_image.py` เขียน `แก้รูปซ้ำHash` (composed) — Python normalize identifier เป็น NFKC ทำให้ `ซ้ำ` → `ซ้ํา` และทั้งสองอ้างถึงฟังก์ชันเดียวกัน **ทดสอบแล้วเรียกได้จริง** (`ast` + `getattr` = callable) → **ห้าม "แก้" ด้วยการ rename เฉย ๆ โดยไม่ทดสอบ** (ควรเปลี่ยนเป็นชื่อ ASCII เพื่อความชัดเจนก็ได้ แต่ไม่ใช่ bug)
- **ruff B023 ที่ `agent_image.py:1174`:** false positive — `re.sub` เรียก lambda แบบ synchronous ใน iteration เดียวกัน; และ repl แบบ callable ไม่ตีความ backslash
- **`.env` / `.env.local` รั่วบน production:** ไม่จริงตอนนี้ — ทั้งคู่ตอบ 404; ความเสี่ยงคืออนาคตถ้า deploy ด้วย CLI (`outputDirectory:"."`, ไม่มี `.vercelignore`)
- **token ใน `site_state.json`:** ไม่พบ — มีแค่ URL ที่ git ปิดรหัสแล้ว; token อยู่ใน `.git/config`
- **`SITE_URL` ใน `.env`:** ถูกต้อง (`https://krobjang.vercel.app`) — ปัญหา canonical ที่ผิดเป็นเพราะหน้าเก่าถูก generate ก่อนแก้ + default ในโค้ดยังผิด
- **`articles_index.json` 500 รายการ:** ไม่ใช่เพราะ prune ปกติ แต่เพราะ `[:500]` ตัดถาวร (ยืนยันจาก 118 ไฟล์ที่หายเป็นรุ่นเก่าสุด)
- **`sitemap.xml`:** ชี้ไฟล์ที่มีจริงครบ, host เดียว (krobjang), ไม่มี URL ซ้ำ — แต่ขาด 118 บทความและชี้หน้าเปล่า 8 หน้า

### แก้ข้อมูลรายงานเดิม (`BUG-REPORT.md` ฉบับก่อน)
| ข้อเดิม | ข้อเท็จจริง |
|---|---|
| token GitHub ติดไปกับ error ใน `site_state.json` | ไม่จริง — state มีแค่ URL ที่ถูก redact |
| `.env` ถูกเสิร์ฟที่ `/.env.local` | ไม่จริง (404); เป็นความเสี่ยงเชิงโครงสร้าง |
| canonical หาย 5 หน้า | บทความทั้ง 618 มี canonical; **หน้า non-article 35 หน้า** ไม่มี |
| canonical ผิด 310 หน้า | **315** หน้า (`krubjang.com`) |
| "ไม่มี artifact หลุด" | ผิด — มี 4 หน้า raw JSON และ 1 หน้า meta พังหนัก |
| `articles_index` ตัด 500 → 118 หาย | ถูกต้อง (ยืนยัน) |
| ลิงก์เสีย 248 / 100 เป้าหมาย | ถูกต้อง |
| CSS ซ้ำ 300 | ถูกต้อง |
| `article:published_time` ขาด 300 | ถูกต้อง (318 มี / 618) |

---

## 🛠️ ลำดับการแก้ที่แนะนำ

**ทำก่อน (ชั่วโมงนี้):**
1. revoke GitHub token + เปลี่ยน remote เป็น credential helper → `git push` ให้สำเร็จ (จะปลดล็อก 40 บทความ + commit ค้าง)
2. แก้ `agent_publisher.push_github()` ให้คืน bool + `sys.exit(1)`; `run_all` อย่าพิมพ์สำเร็จเมื่อ fail
3. แก้ `site_core.เขียน_index` (ลบ `[:500]`, atomic write) แล้ว rebuild index/sitemap/search/category — จะได้ 118 บทความ + 8 หมวดกลับมา
4. ตั้ง `SITE_URL` default เป็น `https://krobjang.vercel.app` + regenerate canonical/og/robots/privacy/contact (315 หน้า)
5. เพิ่ม `html.escape()` ทุกจุด (writer/publisher) + rebuild 64+3+10 หน้าที่พัง
6. ตัดสินนโยบายรูป: commit `images/` ที่ใช้ หรือบังคับ http/data เท่านั้น + แก้ `_svg_thumbnail`

**ถัดมา (วันนี้–พรุ่งนี้):**
7. ซ่อม related-box 248 ลิงก์ + เพิ่ม existence check ใน `_related_html`
8. เพิ่ม dedupe หัวข้อจริง (`เช็คซ้ำ`) + ลบ `_คิดหัวข้อจากรูป` ที่ตาย
9. ซ่อม `index.html` (การ์ดเป็นลิงก์, search, meta, canonical) **ก่อน**รัน publish ใด ๆ
10. ซ่อม doctor: breadcrumb/reading-time/wordCount/fix_seo, และ idempotent CSS
11. ซ่อม FB/LINE (ชื่อ token, ตรวจ status, ใช้ `picture`) + social URL
12. ลบ/ซ่อม dead assets: sw/cookie, thumbnails.json, site-config.json, manifest brand, favicon

**ปรับปรุงโครงสร้าง:**
13. `agent_setup --reset` ให้ทำงานจริง, `_nav_links` ใช้งาน, robots อย่า force
14. theme persistence + `agent_theme`/`agent_video` bug ตาม §17/§21
15. `.gitignore` UTF-8 ใหม่ + เอา `*.py` ออก + `.vercelignore` + README
16. เพิ่ม test/CI ขั้นต่ำ: `py_compile`, JSON valid, link check, `meta` escape check, `git push` exit code

---

## 📎 ภาคผนวก — วิธีทำซ้ำ

```powershell
# static analysis
python -m py_compile (Get-ChildItem *.py).FullName
ruff check --select F,E9,B,PLE,PLW,RUF --isolated --no-cache (Get-ChildItem *.py).FullName

# ตรวจ index vs ดิสก์
python -c "import json,pathlib; b=pathlib.Path('.'); i=json.loads((b/'articles_index.json').read_text(encoding='utf-8')); d={p.name for p in b.glob('article_*.html')}; print(len(i),len(d),len(d-{a['filename'] for a in i}))"

# ตรวจ DNS / production
Resolve-DnsName krubjang.com -Type A          # → does not exist
Invoke-WebRequest https://krobjang.vercel.app/article_anime_20260803_222447_441.html   # → 404
Invoke-WebRequest https://krobjang.vercel.app/images/favicon-32.png                    # → 404
Invoke-WebRequest https://krobjang.vercel.app/site_state.json                          # → 200
```

> **หมายเหตุ:** ผมไม่ได้แก้ไฟล์ซอร์สหรือหน้าเว็บใด ๆ — เขียนเฉพาะรายงานฉบับนี้ทับไฟล์เดิม (ไฟล์ทดสอบทั้งหมดอยู่ใน `%TEMP%`)
