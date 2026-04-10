"""
╔══════════════════════════════════════════════════════════╗
║       ครบจังดอทคอม — agent_writer.py v5 (UNIFIED)      ║
║       สร้างบทความยาว+ลึก+มีคุณภาพ (Chunked Writing)    ║
║                                                          ║
║  python agent_writer.py                → สร้าง 1 บทความ ║
║  python agent_writer.py --count 5      → สร้าง 5 บทความ ║
║  python agent_writer.py --count 10 --cat food → หมวดเดียว║
║  python agent_writer.py --topic "X"    → ระบุหัวข้อเอง  ║
║  python agent_writer.py --cluster      → cluster 4 บทความ║
║  python agent_writer.py --cluster --count 10 → cluster 10║
║  python agent_writer.py --batch 20     → 20 บท ต่างหมวด ║
║  python agent_writer.py --batch 10 --cat health → 10 บท  ║
║  python agent_writer.py --dry-run      → ทดสอบไม่ push   ║
╚══════════════════════════════════════════════════════════╝

หลักการ Chunked Writing:
  - วาง Outline ก่อน (AI ครั้งเดียว)
  - เขียนทีละ section (AI ทีละ call, num_predict สูง)
  - รวมทุก section เป็นบทความเดียว
  - ผลลัพธ์: บทความ 2,000-4,000 คำ คุณภาพสูง

สนับสนุนเรา (sidebar):
  - PromptPay QR + ปุ่มคัดลอกเบอร์
  - Facebook / YouTube / TikTok
  - AdSense (แสดงด้านล่างปุ่ม social)
"""
import os, sys, re, time, json, datetime, random, hashlib
import requests
import feedparser
from pathlib import Path
from bs4 import BeautifulSoup
from config import (
    BASE_PATH, SITE_URL, SITE_NAME, SITE_DESC,
    CATEGORIES, CATEGORY_PAGE_MAP, หมวด_ไทย,
    UNSPLASH_KEY, FB_PAGE_ID, FB_ACCESS_TOKEN,
    LINE_NOTIFY_TOKEN, ADSENSE_PUB, ADSENSE_SLOT, GA4_ID,
    LAZADA_AFFILIATE, SHOPEE_AFFILIATE, AGODA_AFFILIATE,
    DRY_RUN, log, log_ok, log_warn, log_err, log_info, log_ai, log_section,
    เรียก_ollama, เรียก_ollama_เร็ว, สร้าง_thumbnail_svg,
    ดึงรูป_unsplash, ดึงรูป_ตรงเนื้อหา,
    สร้าง_sidebar_html,   # ← ใช้ sidebar จาก config แทน hardcode
)

# ... ต่อจากส่วน import และ config ที่พี่เก่งส่งมา ...

# ══════════════════════════════════════════════════════════════
# 🌐 ส่วนที่ 2: ระบบดึงเนื้อหาจาก URL และแปลงโฉม (Rewrite)
# ══════════════════════════════════════════════════════════════

def ดึงเนื้อหาและ_Rewrite(url: str):
    """
    ดึงข้อมูลจาก URL ที่กำหนด แล้วให้ AI สรุปเนื้อหาเพื่อเตรียมเขียนใหม่
    """
    try:
        log_info(f"🌐 กำลังเข้าถึง URL: {url}")
        
        # ดึงหน้าเว็บ
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, timeout=15, headers=headers)
        res.encoding = 'utf-8'
        
        if res.status_code != 200:
            log_err(f"ไม่สามารถดึงข้อมูลได้ (Status: {res.status_code})")
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # ลบส่วนที่ไม่ใช่นื้อหาออก (เมนู, โฆษณา, สคริปต์)
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'ads']):
            tag.decompose()
        
        # ดึงข้อความและทำความสะอาด
        เนื้อหาดิบ = soup.get_text(separator='\n', strip=True)
        # ตัดเอาเฉพาะช่วงต้นถึงกลาง (ป้องกัน Token เกินถ้าหน้าเว็บยาวมาก)
        เนื้อหาสำหรับ_AI = เนื้อหาดิบ[:5000] 

        log_ai("🤖 กำลังวิเคราะห์และสรุปเนื้อหาจากแหล่งข้อมูล...")
        
        prompt = f"""
        คุณคือบรรณาธิการข่าวอาวุโส 
        จงสรุปเนื้อหาสำคัญจากข้อมูลด้านล่างนี้ เพื่อนำไปใช้เป็นข้อมูลอ้างอิงในการเขียนบทความใหม่
        โดยให้สรุปเป็นประเด็นสำคัญ 5-8 ข้อ และคงใจความสำคัญไว้ทั้งหมด (ห้ามก๊อปปี้ประโยคเดิม)
        
        ข้อมูลจาก URL: {url}
        เนื้อหา:
        {เนื้อหาสำหรับ_AI}
        """
        
        สรุป = เรียก_ollama(prompt)
        return สรุป

    except Exception as e:
        log_err(f"เกิดข้อผิดพลาดในระบบดึงข้อมูล: {e}")
        return None

# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# 🖼️ รูปภาพ — ค้นหาหลายวิธี (5 fallback)
# ══════════════════════════════════════════════════════════════
def ดึงรูป_robust(หัวข้อ: str, หมวด: str, filename: str = "", บริบท: str = "") -> str:
    """
    FIX: ดึงรูปตรงเนื้อหา โดยให้ AI คิด keyword เฉพาะเจาะจงก่อน
    แล้วส่งให้ ดึงรูป_ตรงเนื้อหา ใน config จัดการ
    """
    # ให้ AI แปลง keyword เป็นภาษาอังกฤษที่ตรงเนื้อหาก่อน (ไม่ใช้ชื่อบุคคล)
    try:
        keyword_prompt = (
            f'จากหัวข้อ: "{หัวข้อ}"\n'
            f'คิด keyword ภาษาอังกฤษ 2-3 คำ สำหรับค้นรูปภาพ\n'
            f'ห้ามใช้ชื่อบุคคล ให้ใช้คำกว้างๆ เช่น "trade war economy", "military diplomacy", "stock market"\n'
            f'ตอบแค่ keyword ไม่ต้องอธิบาย'
        )
        keyword_en = เรียก_ollama_เร็ว(keyword_prompt).strip().split('\n')[0][:80]
        log_info(f"🔍 keyword รูป: {keyword_en}")
        img = ดึงรูป_ตรงเนื้อหา(keyword_en, หมวด, keyword_en)
    except Exception:
        img = ดึงรูป_ตรงเนื้อหา(หัวข้อ, หมวด, บริบท)

    if img and img.startswith("http"):
        return img

    # Fallback: SVG local
    if filename:
        svg_path = สร้าง_thumbnail_svg(หัวข้อ, หมวด, filename)
        if svg_path:
            log_ok(f"สร้าง SVG thumbnail local: {svg_path}")
            return svg_path

    seed = hashlib.md5((หัวข้อ + หมวด).encode()).hexdigest()[:12]
    return f"https://picsum.photos/seed/{seed}/800/450"


def สร้างรูป_inline(หัวข้อ_section: str, หมวด: str, หัวข้อ_บทความ: str = "", filename: str = "") -> str:
    """FIX: รูปแทรกในเนื้อหา — ส่ง context ทั้งหัวข้อ section และบทความให้ keyword แม่น"""
    บริบท = f"บทความ: {หัวข้อ_บทความ}, ส่วน: {หัวข้อ_section}" if หัวข้อ_บทความ else หัวข้อ_section
    url = ดึงรูป_robust(หัวข้อ_section, หมวด, filename=filename, บริบท=บริบท)  # แก้บั๊ก 3: ส่ง filename ด้วย
    seed = hashlib.md5(หัวข้อ_section.encode()).hexdigest()[:8]
    fallback = f"https://picsum.photos/seed/{seed}/800/350"
    return (
        f'<figure style="margin:1.5rem 0;border-radius:12px;overflow:hidden;'
        f'box-shadow:0 2px 12px rgba(0,0,0,0.1);">'
        f'<img src="{url}" alt="{หัวข้อ_section}" loading="lazy" '
        f'onerror="this.onerror=null;this.src=\'{fallback}\'" '
        f'style="width:100%;max-height:350px;object-fit:cover;">'
        f'<figcaption style="text-align:center;font-size:0.85rem;color:#64748b;'
        f'padding:0.5rem;">{หัวข้อ_section}</figcaption></figure>'
    )


# ══════════════════════════════════════════════════════════════
# 📚 Scrape ข้อมูลอ้างอิง — หลายแหล่ง
# ══════════════════════════════════════════════════════════════
def scrape_อ้างอิง(หัวข้อ: str) -> str:
    import urllib.parse
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
    }
    เนื้อหา = []

    log_info("ค้นหาข้อมูลอ้างอิง...")

    # แหล่งที่ 1: DuckDuckGo
    try:
        ddg = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(หัวข้อ + ' ภาษาไทย')}"
        r = requests.get(ddg, headers=headers, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        snippets = [s.get_text().strip() for s in soup.select(".result__snippet")
                    if len(s.get_text().strip()) > 50]
        เนื้อหา.extend(snippets[:10])

        # ดึงเนื้อหาจากเว็บข่าวไทยที่เจอใน DuckDuckGo
        links = []
        for a in soup.select(".result__title a, .result__a"):
            href = a.get("href", "")
            if "uddg=" in href:
                try:
                    href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                except Exception:
                    pass
            if href.startswith("http") and any(d in href for d in
                    ["sanook", "kapook", "thairath", "khaosod", "mthai",
                     "manager", "bangkokpost", "nationthailand"]):
                links.append(href)

        for url in links[:3]:
            try:
                r2 = requests.get(url, headers=headers, timeout=10)
                s2 = BeautifulSoup(r2.text, "html.parser")
                ps = [p.get_text().strip() for p in s2.find_all("p")
                      if len(p.get_text().strip()) > 80
                      and not any(w in p.get_text() for w in
                                  ["คุกกี้","Cookie","ลงทะเบียน","subscribe","copyright"])]
                เนื้อหา.extend(ps[:8])
                log_ok(f"อ่านเว็บ: {url[8:50]}...")
            except Exception:
                pass
    except Exception as e:
        log_warn(f"DuckDuckGo ล้มเหลว: {e}")

    # แหล่งที่ 2: เว็บไทยโดยตรง (ถ้ายังน้อย)
    if len(เนื้อหา) < 8:
        log_info("Fallback: ค้นเว็บไทยโดยตรง...")
        thai_sources = [
            f"https://www.sanook.com/search/?q={urllib.parse.quote(หัวข้อ)}",
            f"https://www.kapook.com/search.php?q={urllib.parse.quote(หัวข้อ)}",
            f"https://www.thairath.co.th/search/{urllib.parse.quote(หัวข้อ)}",
            f"https://www.khaosod.co.th/?s={urllib.parse.quote(หัวข้อ)}",
        ]
        for url in thai_sources:
            try:
                r = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                ps = [p.get_text().strip() for p in soup.find_all("p")
                      if len(p.get_text().strip()) > 80]
                เนื้อหา.extend(ps[:6])
                if len(เนื้อหา) >= 20:
                    break
            except Exception:
                pass

    # กรองซ้ำ + เรียงตาม length (เนื้อหายาวกว่า = มีประโยชน์มากกว่า)
    seen, กรอง = set(), []
    for t in เนื้อหา:
        k = t[:50]
        if k not in seen and len(t) > 60:
            seen.add(k)
            กรอง.append(t)
    กรอง.sort(key=len, reverse=True)

    log_info(f"ข้อมูลอ้างอิง: {len(กรอง)} ย่อหน้า ({sum(len(x) for x in กรอง)} ตัวอักษร)")
    return "\n".join(กรอง[:30])


# ══════════════════════════════════════════════════════════════
# ✍️ Markdown → HTML converter
# ══════════════════════════════════════════════════════════════
def _กรอง_instruction(ข้อความ: str) -> str:
    """ลบบรรทัดที่เป็น instruction หลุดออกมาจาก AI ไม่ให้ติดในบทความ"""
    PATTERNS = [
        r'^[⚠️✨🔴🔥💡📌]+\s*(สำคัญ|กฎ|ห้าม|ต้อง|หมายเหตุ)',
        r'^\d+\.\s*(เริ่มด้วย|ห้าม|เขียน Markdown|ความยาว|ตอบเฉพาะ)',
        r'^(กฎ|กฎสำคัญ|สำคัญมาก|หมายเหตุ)\s*:',
        r'^ความยาว\s+\d+',
        r'^เขียน Markdown',
        r'^ห้าม HTML',
        r'^ตอบเป็น Markdown',
        r'^สลับระหว่างย่อหน้า',
        r'^รายการ bullet',
    ]
    สะอาด = []
    for line in ข้อความ.split('\n'):
        if any(re.match(p, line.strip()) for p in PATTERNS):
            continue
        สะอาด.append(line)
    return '\n'.join(สะอาด)


def แปลง_md_html(ข้อความ: str) -> str:
    """แปลง Markdown/raw text → HTML สะอาด"""
    # ลบ <think> tags จาก deepseek-r1
    ข้อความ = re.sub(r'<think>.*?</think>', '', ข้อความ, flags=re.DOTALL).strip()
    # ลบ ``` code blocks
    ข้อความ = re.sub(r'```.*?```', '', ข้อความ, flags=re.DOTALL)
    # ลบ instruction หลุด
    ข้อความ = _กรอง_instruction(ข้อความ)

    บรรทัด = ข้อความ.split("\n")
    ผล, in_list, in_ol = [], False, False
    ol_counter = 0  # นับเลขลำดับเองป้องกัน AI ส่ง "1. 1. 1."

    for line in บรรทัด:
        stripped = line.strip()

        if re.match(r'^#{3}\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            h = re.sub(r'^#{3}\s+', '', stripped)
            h = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
            ผล.append(f'<h3 style="color:var(--dark,#1e293b);margin-top:1.5rem;margin-bottom:0.5rem;font-size:1.1rem;">{h}</h3>')

        elif re.match(r'^#{1,2}\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            h = re.sub(r'^#{1,2}\s+', '', stripped)
            h = re.sub(r'\*\*(.+?)\*\*', r'\1', h)
            ผล.append(f'<h2 style="color:var(--primary,#1e40af);margin-top:2rem;margin-bottom:0.75rem;font-size:1.3rem;border-left:4px solid var(--primary,#1e40af);padding-left:0.75rem;">{h}</h2>')

        elif re.match(r'^\d+\.\s+', stripped):
            if in_list: ผล.append("</ul>"); in_list = False
            if not in_ol:
                ผล.append('<ol style="padding-left:1.5rem;margin:1rem 0;">')
                in_ol = True
                ol_counter = 0
            ol_counter += 1
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            # ใช้ value= บังคับให้ browser แสดงเลขถูก แม้ AI ส่ง 1. ทุกบรรทัด
            ผล.append(f'<li value="{ol_counter}" style="margin-bottom:0.5rem;line-height:1.7;">{item}</li>')

        elif re.match(r'^[-*•]\s+', stripped):
            if in_ol: ผล.append("</ol>"); in_ol = False; ol_counter = 0
            if not in_list: ผล.append('<ul style="padding-left:1.5rem;margin:1rem 0;">'); in_list = True
            item = re.sub(r'^[-*•]\s+', '', stripped)
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            ผล.append(f'<li style="margin-bottom:0.5rem;line-height:1.7;">{item}</li>')

        elif stripped == "":
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0

        else:
            if in_list: ผล.append("</ul>"); in_list = False
            if in_ol:   ผล.append("</ol>"); in_ol = False; ol_counter = 0
            if stripped:
                s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
                if s.startswith('<h') or s.startswith('<ul') or s.startswith('<ol') or s.startswith('<li'):
                    ผล.append(s)
                else:
                    ผล.append(f"<p>{s}</p>")

    if in_list: ผล.append("</ul>")
    if in_ol:   ผล.append("</ol>")
    return "\n".join(ผล)


def ทำความสะอาด_html(html: str) -> str:
    """ลบ tag ซ้ำซ้อน, ลบ h1 ที่ AI สร้างขึ้นมา, กรอง instruction หลุด"""
    html = re.sub(r'<h1[^>]*>.*?</h1>', '', html, flags=re.DOTALL)
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[23][^>]*>)', r'\1', html)
    html = re.sub(r'(</h[23]>)</p>', r'\1', html)
    # ลบ instruction หลุดในรูปแบบ HTML
    html = re.sub(
        r'<p>[⚠️✨🔴🔥💡📌]*\s*(สำคัญมาก|กฎสำคัญ|หมายเหตุ)[^<]{0,400}</p>', '', html)
    html = re.sub(
        r'<p>\d+\.\s*(เริ่มด้วย|ห้าม|เขียน Markdown|ความยาว)[^<]{0,400}</p>', '', html)
    html = re.sub(
        r'<p>(เขียน Markdown|ห้าม HTML|สลับระหว่างย่อหน้า|รายการ bullet)[^<]{0,400}</p>', '', html)
    return html.strip()


# ══════════════════════════════════════════════════════════════
# 🎲 สร้าง Outline แบบสุ่มสไตล์ — แยกออกมาเป็นฟังก์ชันอิสระ
# ══════════════════════════════════════════════════════════════
def สร้าง_outline_แบบสุ่มสไตล์(หัวข้อ: str, หมวด: str, ctx: str = "") -> list:
    """
    สุ่มรูปแบบการวางโครงสร้างบทความ เพื่อไม่ให้ได้ outline ซ้ำเดิมทุกครั้ง
    คืนค่าเป็น list ของ dict {"h": หัวข้อย่อย, "desc": รายละเอียด}
    """
    สไตล์ทั้งหมด = [
        "สไตล์เล่าเรื่องแบบ Storytelling (เปิดด้วยปมปัญหา ชวนคิด มีบทสรุปสร้างแรงบันดาลใจ)",
        "สไตล์ Guidebook / How-to (ลำดับขั้นตอน 1, 2, 3 ปฏิบัติได้จริง มีทริคเสริม)",
        "สไตล์แชร์ประสบการณ์และรีวิว (เป็นกันเอง เหมือนเพื่อนเล่าให้ฟัง มีข้อดีข้อเสีย)",
        "สไตล์เจาะลึกแบบ Case Study (วิเคราะห์เหตุและผล มีข้อมูลสนับสนุน)",
        "สไตล์ Q&A (ตั้งคำถามที่คนมักสงสัย แล้วตอบให้กระจ่างเป็นข้อๆ)",
    ]
    สไตล์ที่เลือก = random.choice(สไตล์ทั้งหมด)
    log_info(f"🎲 สุ่มสไตล์บทความ: {สไตล์ที่เลือก[:40]}...")

    # คำแนะนำพิเศษตามหมวด
    OUTLINE_GUIDE = {
        "food": (
            "บทความอาหาร/สูตรอาหาร ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- วัตถุดิบที่ต้องใช้ (ระบุปริมาณ)\n"
            "- ขั้นตอนการทำทีละขั้น (Step-by-step)\n"
            "- เคล็ดลับให้อร่อย\n"
            "- การจัดจาน/เสิร์ฟ\n"
            "ห้ามเขียนเรื่องที่ไม่เกี่ยวกับอาหารนี้โดยตรง"
        ),
        "health": (
            "บทความสุขภาพ ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- อาการ/สัญญาณที่ควรรู้\n"
            "- สาเหตุและปัจจัยเสี่ยง\n"
            "- วิธีป้องกัน/รักษาเบื้องต้น\n"
            "- เมื่อไรควรพบแพทย์\n"
            "ห้ามแนะนำยาหรือการรักษาโดยไม่มีหมอ"
        ),
        "finance": (
            "บทความการเงิน ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- หลักการ/แนวคิดที่สำคัญ\n"
            "- ตัวเลข/ตัวอย่างจริงประกอบ\n"
            "- ขั้นตอนที่ทำได้จริง\n"
            "- ข้อควรระวัง/ความเสี่ยง"
        ),
        "lifestyle": (
            "บทความไลฟ์สไตล์ ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- เหตุผลว่าทำไมถึงสำคัญ\n"
            "- วิธีปฏิบัติจริงทีละขั้น\n"
            "- ตัวอย่างในชีวิตจริง\n"
            "- เคล็ดลับที่ใช้ได้ทันที"
        ),
        "sport": (
            "บทความกีฬา ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- กฎ/วิธีเล่น/ประเภท\n"
            "- เทคนิค/ท่าทาง\n"
            "- การฝึกซ้อม/พัฒนา\n"
            "- ประโยชน์ต่อสุขภาพ"
        ),
        "beauty": (
            "บทความความงาม ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- ผลิตภัณฑ์/วัตถุดิบที่ใช้\n"
            "- ขั้นตอนวิธีทำทีละขั้น\n"
            "- เคล็ดลับให้ได้ผลดี\n"
            "- ข้อควรระวัง"
        ),
        "diy": (
            "บทความ DIY ต้องมีหัวข้อที่ครอบคลุม:\n"
            "- อุปกรณ์/วัสดุที่ต้องใช้\n"
            "- ขั้นตอนการทำทีละขั้น\n"
            "- เคล็ดลับ/วิธีแก้ปัญหา\n"
            "- ตัวอย่างผลงาน"
        ),
    }
    outline_guide = OUTLINE_GUIDE.get(หมวด, "")
    if outline_guide:
        outline_guide = f"\n⚠️ คำแนะนำพิเศษสำหรับหมวด {หมวด_ไทย.get(หมวด, หมวด)}:\n{outline_guide}\n"

    def _parse_any_list(raw: str) -> list:
        """Parse outline — รองรับทุก format ที่โมเดลตอบมา"""
        import re as _re
        SKIP = ["หัวข้อย่อย","สิ่งที่ต้อง","---","===","รูปแบบ","ตอบแค่","กฎ:","ห้าม","ใช้:"]
        result = []
        for line in raw.split("\n"):
            line = _re.sub(r'<think>.*?</think>', '', line).strip()
            if not line or any(s in line for s in SKIP):
                continue
            if "|" in line:
                parts = line.split("|", 1)
                h = parts[0].strip().lstrip("0123456789.-) ").strip('"\' *#')
                desc = parts[1].strip() if len(parts)>1 else "อธิบายรายละเอียดและยกตัวอย่าง"
            else:
                h = line.lstrip("0123456789.-) ").strip('"\' *#')
                desc = "อธิบายรายละเอียดและยกตัวอย่างจากชีวิตจริง"
            if 4 <= len(h) <= 80 and any('\u0e00' <= c <= '\u0e7f' for c in h):
                result.append({"h": h, "desc": desc})
            if len(result) >= 7:
                break
        return result

    # รอบแรก: prompt กระชับ ให้ตอบง่าย
    outline_raw = เรียก_ollama(
        f"บทความเรื่อง \"{หัวข้อ}\" จะแบ่งเป็นหัวข้อย่อยอะไรบ้าง\n"
        f"(หมวด: {หมวด_ไทย.get(หมวด, หมวด)} | สไตล์: {สไตล์ที่เลือก})\n"
        f"{ctx}"
        f"{outline_guide}\n"
        f"ตอบ 7 หัวข้อที่เกี่ยวกับ \"{หัวข้อ}\" โดยตรง แต่ละหัวข้อต่างกัน\n"
        f"รูปแบบ: ชื่อหัวข้อ | สิ่งที่จะพูดถึง\n"
        f"ตอบแค่ 7 บรรทัด",
        timeout=90, num_predict=700
    )
    sections = _parse_any_list(outline_raw)

    # รอบสอง: prompt ง่ายกว่า ถ้าได้น้อยกว่า 4
    if len(sections) < 4:
        log_warn(f"Outline รอบแรกได้ {len(sections)} → ลองแบบง่าย...")
        outline_raw2 = เรียก_ollama(
            f"บทความเรื่อง \"{หัวข้อ}\" ควรพูดถึงอะไรบ้าง\n"
            f"ตอบเป็นรายการ 7 ข้อ บรรทัดละ 1 ข้อ ภาษาไทย",
            timeout=60, num_predict=500
        )
        sections2 = _parse_any_list(outline_raw2)
        if len(sections2) > len(sections):
            sections = sections2

    # รอบสาม: ถ้ายังไม่พอ → ให้ AI สร้างแบบอิสระ
    if len(sections) < 4:
        log_warn(f"Outline รอบสองได้ {len(sections)} → ขอแบบอิสระ...")
        outline_raw3 = เรียก_ollama(
            f"ถ้าจะสอนเรื่อง \"{หัวข้อ}\" ให้ครบ ต้องมีหัวข้ออะไรบ้าง\n"
            f"ตอบ 7 ข้อ",
            timeout=60, num_predict=400
        )
        sections3 = _parse_any_list(outline_raw3)
        if len(sections3) > len(sections):
            sections = sections3

    # Fallback outline แยกตามหมวด — ถ้า AI ไม่ตอบ
    FALLBACK_OUTLINE = {
        "food": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "ความหมาย ที่มา ประวัติ ทำไมถึงนิยม"},
            {"h": "วัตถุดิบที่ต้องเตรียม", "desc": "รายการวัตถุดิบครบถ้วนพร้อมปริมาณที่ชัดเจน"},
            {"h": "อุปกรณ์ที่ใช้ในการทำ", "desc": "หม้อ กระทะ เครื่องมือที่ต้องใช้"},
            {"h": "ขั้นตอนการทำทีละขั้น", "desc": "Step-by-step วิธีทำตั้งแต่ต้นจนเสร็จ"},
            {"h": "เคล็ดลับให้อร่อย", "desc": "เทคนิคเฉพาะ สิ่งที่ควรทำและไม่ควรทำ"},
            {"h": "การจัดจานและเสิร์ฟ", "desc": "วิธีตกแต่ง เครื่องเคียง การนำเสนอ"},
            {"h": "คุณค่าทางโภชนาการ", "desc": "แคลอรี่ สารอาหาร ประโยชน์ต่อร่างกาย"},
        ],
        "health": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "นิยาม ความหมาย ภาพรวม"},
            {"h": "อาการและสัญญาณ", "desc": "อาการที่พบบ่อย วิธีสังเกต"},
            {"h": "สาเหตุและปัจจัยเสี่ยง", "desc": "ต้นเหตุ กลุ่มเสี่ยง ปัจจัยที่เกี่ยวข้อง"},
            {"h": "วิธีป้องกัน", "desc": "การป้องกันก่อนเกิด ปรับพฤติกรรม"},
            {"h": "วิธีรักษาเบื้องต้น", "desc": "สิ่งที่ทำได้เอง ยาสามัญ การดูแลตนเอง"},
            {"h": "เมื่อไรควรพบแพทย์", "desc": "สัญญาณอันตราย อาการที่ต้องรีบรักษา"},
            {"h": "เคล็ดลับดูแลตนเอง", "desc": "วิถีชีวิต อาหาร การออกกำลังกาย"},
        ],
        "finance": [
            {"h": f"{หัวข้อ} คืออะไร", "desc": "นิยาม ความสำคัญ ภาพรวม"},
            {"h": "หลักการสำคัญที่ควรรู้", "desc": "แนวคิดพื้นฐาน กฎที่ต้องจำ"},
            {"h": "วิธีเริ่มต้นสำหรับมือใหม่", "desc": "ขั้นตอนแรกที่ต้องทำ เตรียมตัวอย่างไร"},
            {"h": "ตัวอย่างจริงและตัวเลข", "desc": "กรณีศึกษา ตัวเลขจริง การคำนวณ"},
            {"h": "ความผิดพลาดที่พบบ่อย", "desc": "ข้อผิดพลาดที่คนมักทำ วิธีหลีกเลี่ยง"},
            {"h": "เครื่องมือและทรัพยากร", "desc": "แอป เว็บไซต์ สิ่งที่ช่วยได้"},
            {"h": "เคล็ดลับจากผู้เชี่ยวชาญ", "desc": "คำแนะนำระดับสูง กลยุทธ์ที่ได้ผล"},
        ],
    }

    if len(sections) < 4:
        log_warn(f"Outline ไม่ครบ (ได้ {len(sections)}) → ใช้โครงสร้างสำรองตามหมวด '{หมวด}'")
        if หมวด in FALLBACK_OUTLINE:
            sections = FALLBACK_OUTLINE[หมวด]
        else:
            sections = [
                {"h": f"{หัวข้อ} คืออะไร", "desc": "ความหมาย นิยาม ภาพรวม ทำไมถึงสำคัญ"},
                {"h": f"ประเภทของ{หัวข้อ}", "desc": "แบ่งประเภท เปรียบเทียบแต่ละแบบ"},
                {"h": "วิธีการและขั้นตอน", "desc": "คำแนะนำทีละขั้นตอน เทคนิค เคล็ดลับ"},
                {"h": "ประโยชน์ที่ได้รับ", "desc": "ข้อดี ผลลัพธ์จริง กรณีศึกษา"},
                {"h": "ข้อควรระวัง", "desc": "ความเสี่ยง ข้อเสีย วิธีป้องกัน"},
                {"h": "ตัวอย่างจริง", "desc": "กรณีศึกษา ตัวอย่างในชีวิตประจำวัน"},
                {"h": "เคล็ดลับจากผู้เชี่ยวชาญ", "desc": "Tips เทคนิคขั้นสูง คำแนะนำมืออาชีพ"},
            ]

    return sections


# ══════════════════════════════════════════════════════════════
# 🎬 YouTube Embed — ค้นหาวิดีโอตรงหัวข้อ
# ══════════════════════════════════════════════════════════════
def ดึง_youtube_embed(หัวข้อ: str, หมวด: str) -> str:
    """
    ค้นหา YouTube วิดีโอตรงหัวข้อบทความผ่าน YouTube Data API
    ถ้าไม่มี API key → ใช้ iframe search embed แทน (ไม่ต้อง key)
    """
    try:
        from config import YOUTUBE_API_KEY
    except ImportError:
        YOUTUBE_API_KEY = ""

    video_id = ""

    # วิธี 1: YouTube Data API (ถ้ามี key)
    if YOUTUBE_API_KEY:
        try:
            import urllib.parse
            q = urllib.parse.quote(f"{หัวข้อ} ภาษาไทย")
            api_url = (
                f"https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&q={q}&type=video&maxResults=1"
                f"&relevanceLanguage=th&key={YOUTUBE_API_KEY}"
            )
            r = requests.get(api_url, timeout=10)
            data = r.json()
            items = data.get("items", [])
            if items:
                video_id = items[0]["id"]["videoId"]
                log_ok(f"YouTube API: {video_id}")
        except Exception as e:
            log_warn(f"YouTube API ล้มเหลว: {e}")

    # วิธี 2: ถ้าไม่มี video_id → scrape YouTube search หน้าแรก
    if not video_id:
        try:
            import urllib.parse
            q = urllib.parse.quote(f"{หัวข้อ} ภาษาไทย")
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(
                f"https://www.youtube.com/results?search_query={q}",
                headers=headers, timeout=10
            )
            # หา videoId จาก JSON ใน source
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
            if matches:
                video_id = matches[0]
                log_ok(f"YouTube scrape: {video_id}")
        except Exception as e:
            log_warn(f"YouTube scrape ล้มเหลว: {e}")

    if not video_id:
        log_warn("ไม่พบวิดีโอ YouTube — ข้าม")
        return ""

    return (
        f'\n<div style="margin:2rem 0;">'
        f'<h2 style="color:var(--primary,#1e40af);font-size:1.1rem;margin-bottom:0.75rem;">'
        f'<i class="fab fa-youtube" style="color:#ff0000;"></i> วิดีโอที่เกี่ยวข้อง</h2>'
        f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;'
        f'border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.12);">'
        f'<iframe src="https://www.youtube.com/embed/{video_id}"'
        f' style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"'
        f' loading="lazy" allowfullscreen'
        f' title="{หัวข้อ}"></iframe>'
        f'</div></div>'
    )



# ══════════════════════════════════════════════════════════════
# 💰 Affiliate + Download Links — สร้างรายได้จากเนื้อหา
# ══════════════════════════════════════════════════════════════

# Platform ดาวน์โหลดเกมฟรี (ใช้กับหมวด gaming, anime, entertainment)
GAME_PLATFORMS = [
    {"name": "Steam", "icon": "fab fa-steam", "color": "#1b2838",
     "url": "https://store.steampowered.com/search/?term={kw}&tags=493",
     "label": "ค้นหาบน Steam"},
    {"name": "Epic Games", "icon": "fas fa-gamepad", "color": "#2d2d2d",
     "url": "https://store.epicgames.com/browse?q={kw}&sortBy=relevancy",
     "label": "ค้นหาบน Epic Games"},
    {"name": "GOG", "icon": "fas fa-compact-disc", "color": "#86329f",
     "url": "https://www.gog.com/games?search={kw}",
     "label": "ค้นหาบน GOG"},
]

# Map หมวด → config affiliate
AFFILIATE_CONFIG = {
    "gaming": {
        "type": "game_download",
        "shopee_cat": "gaming",
        "lazada_cat": "gaming",
        "platforms": GAME_PLATFORMS,
    },
    "anime": {
        "type": "game_download",
        "shopee_cat": "anime",
        "lazada_cat": "anime",
        "platforms": GAME_PLATFORMS,
    },
    "food": {
        "type": "product",
        "shopee_cat": "food",
        "lazada_cat": "grocery",
        "platforms": [],
    },
    "health": {
        "type": "product",
        "shopee_cat": "health",
        "lazada_cat": "health",
        "platforms": [],
    },
    "beauty": {
        "type": "product",
        "shopee_cat": "beauty",
        "lazada_cat": "beauty",
        "platforms": [],
    },
    "travel": {
        "type": "booking",
        "shopee_cat": "travel",
        "lazada_cat": "travel",
        "platforms": [],
    },
    "finance": {
        "type": "product",
        "shopee_cat": "finance",
        "lazada_cat": "finance",
        "platforms": [],
    },
    "diy": {
        "type": "product",
        "shopee_cat": "diy",
        "lazada_cat": "tools",
        "platforms": [],
    },
    "pet": {
        "type": "product",
        "shopee_cat": "pet",
        "lazada_cat": "pet",
        "platforms": [],
    },
    "car": {
        "type": "product",
        "shopee_cat": "automotive",
        "lazada_cat": "automotive",
        "platforms": [],
    },
}


def สร้าง_affiliate_block(หัวข้อ: str, หมวด: str) -> str:
    """
    สร้างบล็อก affiliate/download ที่ตรงกับเนื้อหาบทความ
    - gaming/anime  → ปุ่มดาวน์โหลดแพลตฟอร์มเกม + Shopee/Lazada
    - travel        → Agoda + Shopee/Lazada
    - อื่นๆ          → Shopee + Lazada (keyword จากหัวข้อ)
    """
    import urllib.parse

    cfg = AFFILIATE_CONFIG.get(หมวด, {"type": "product", "shopee_cat": "", "lazada_cat": "", "platforms": []})

    # AI คิด keyword สินค้าจากหัวข้อ (สั้น กระชับ ค้นหาได้)
    try:
        kw_raw = เรียก_ollama_เร็ว(
            f'จากหัวข้อบทความ: "{หัวข้อ}"\n'
            f'คิด keyword ภาษาไทย 1-3 คำ สำหรับค้นหาสินค้าที่เกี่ยวข้องใน Shopee/Lazada\n'
            f'ตอบแค่ keyword เดียว ไม่ต้องอธิบาย'
        ).strip().split("\n")[0].strip('"\'- ')[:40]
        kw = kw_raw if len(kw_raw) > 2 else หัวข้อ[:20]
    except Exception:
        kw = หัวข้อ[:20]

    kw_enc  = urllib.parse.quote(kw)
    parts   = []

    # ── ① ปุ่มดาวน์โหลด (gaming/anime) ──────────────────────
    if cfg.get("platforms"):
        platform_btns = "".join(
            f'''<a href="{p["url"].replace("{kw}", kw_enc)}" target="_blank" rel="noopener sponsored"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.1rem;
                      background:{p["color"]};color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;transition:opacity 0.2s;"
               onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
              <i class="{p["icon"]}"></i> {p["label"]}</a>'''
            for p in cfg["platforms"]
        )
        parts.append(
            f'''<div style="background:linear-gradient(135deg,#1b2838,#2d2d2d);border-radius:12px;
                    padding:1.25rem;margin:1.5rem 0;">
              <h3 style="color:#fff;margin:0 0 0.85rem;font-size:1rem;">
                <i class="fas fa-download" style="color:#66c0f4;"></i> ดาวน์โหลด / ค้นหาเกมที่เกี่ยวข้อง
              </h3>
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">{platform_btns}</div>
            </div>'''
        )

    # ── ② Agoda (travel) ──────────────────────────────────────
    if หมวด == "travel" and AGODA_AFFILIATE:
        agoda_url = f"https://www.agoda.com/th-th/search?city={kw_enc}&tag={AGODA_AFFILIATE}"
        parts.append(
            f'''<div style="background:linear-gradient(135deg,#e53935,#b71c1c);border-radius:12px;
                    padding:1.25rem;margin:1.5rem 0;">
              <h3 style="color:#fff;margin:0 0 0.5rem;font-size:1rem;">
                <i class="fas fa-hotel"></i> ค้นหาที่พักราคาดี — {kw}
              </h3>
              <p style="color:rgba(255,255,255,0.85);margin:0 0 0.75rem;font-size:0.88rem;">
                เปรียบเทียบราคาโรงแรม รีสอร์ท หลายร้อยแห่ง จองได้ทันที
              </p>
              <a href="{agoda_url}" target="_blank" rel="noopener sponsored"
                 style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.6rem 1.4rem;
                        background:#fff;color:#b71c1c;border-radius:8px;text-decoration:none;
                        font-size:0.9rem;font-weight:700;">
                <i class="fas fa-search"></i> ค้นหาที่พักบน Agoda</a>
            </div>'''
        )

    # ── ③ Shopee ──────────────────────────────────────────────
    if SHOPEE_AFFILIATE:
        shopee_url = f"https://s.shopee.co.th/AKd8bPBUeB?keyword={kw_enc}"
        shopee_btn = (
            f'''<a href="{shopee_url}" target="_blank" rel="noopener sponsored"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                      background:#ee4d2d;color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;">
              <i class="fas fa-shopping-bag"></i> ค้นหาบน Shopee</a>'''
        )
    else:
        shopee_url  = f"https://shopee.co.th/search?keyword={kw_enc}"
        shopee_btn  = (
            f'''<a href="{shopee_url}" target="_blank" rel="noopener"
               style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                      background:#ee4d2d;color:#fff;border-radius:8px;text-decoration:none;
                      font-size:0.88rem;font-weight:600;">
              <i class="fas fa-shopping-bag"></i> ดูใน Shopee</a>'''
        )

    # ── ④ Lazada ─────────────────────────────────────────────
    if LAZADA_AFFILIATE:
        lazada_url = f"https://www.lazada.co.th/tag/{kw_enc}/?laz_trackid={LAZADA_AFFILIATE}"
    else:
        lazada_url = f"https://www.lazada.co.th/catalog/?q={kw_enc}"
    lazada_btn = (
        f'''<a href="{lazada_url}" target="_blank" rel="noopener sponsored"
           style="display:inline-flex;align-items:center;gap:0.5rem;padding:0.55rem 1.2rem;
                  background:#f57224;color:#fff;border-radius:8px;text-decoration:none;
                  font-size:0.88rem;font-weight:600;">
          <i class="fas fa-tag"></i> ดูใน Lazada</a>'''
    )

    # รวม Shopee + Lazada เป็นบล็อกเดียว
    parts.append(
        f'''<div style="background:var(--soft,#f1f5f9);border-radius:12px;
                padding:1.25rem;margin:1.5rem 0;border:1px solid var(--border,#e2e8f0);">
          <h3 style="color:var(--dark,#1e293b);margin:0 0 0.6rem;font-size:0.95rem;">
            <i class="fas fa-shopping-cart" style="color:#ee4d2d;"></i>
            สินค้าที่เกี่ยวข้องกับ <em>{kw}</em>
          </h3>
          <p style="margin:0 0 0.75rem;font-size:0.85rem;color:var(--muted,#64748b);">
            เปรียบเทียบราคา หาของดีราคาถูกได้ที่นี่
          </p>
          <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
            {shopee_btn}
            {lazada_btn}
          </div>
          <p style="margin:0.6rem 0 0;font-size:0.75rem;color:var(--muted,#94a3b8);">
            * ลิงก์บางส่วนเป็น Affiliate Link — เราได้รับค่าคอมมิชชันเล็กน้อยโดยไม่มีค่าใช้จ่ายเพิ่มสำหรับคุณ
          </p>
        </div>'''
    )

    if not parts:
        return ""

    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════
# ✍️ เขียนบทความแบบ Chunked — ยาว ลึก มีคุณภาพ
# ══════════════════════════════════════════════════════════════
def เขียนบทความ(หัวข้อ: str, หมวด: str) -> str:
    """
    Chunked Writing — เขียนทีละ section แล้วรวม:
    0. Scrape ข้อมูลอ้างอิง
    1. วาง Outline (6-8 section)
    2. เขียน Intro (3-4 ย่อหน้า)
    3. เขียนทีละ section (แต่ละ section 400-600 คำ)
    4. แทรกรูปทุก 2 section
    5. เขียน Conclusion + FAQ
    6. รวมทุกส่วน → บทความ 2,500-4,000 คำ
    """
    log_ai(f"เขียนบทความ (Chunked): {หัวข้อ}")
    log_info(f"หมวด: {หมวด} | หมวดไทย: {หมวด_ไทย.get(หมวด, หมวด)}")

    # ── STEP 0: Scrape อ้างอิง ────────────────────────────
    อ้างอิง = scrape_อ้างอิง(หัวข้อ)
    ctx = f"\nข้อมูลอ้างอิง (นำมาใช้ประกอบ):\n{อ้างอิง[:3000]}\n" if อ้างอิง else ""

    # ── STEP 1: Outline ───────────────────────────────────
    log_info("STEP 1/6 — วาง Outline...")
    sections = สร้าง_outline_แบบสุ่มสไตล์(หัวข้อ, หมวด, ctx)

    if not sections:
        log_err("ไม่ได้ Outline — หยุดการเขียน")
        return ""

    log_ok(f"Outline: {len(sections)} หัวข้อย่อย")
    for i, s in enumerate(sections, 1):
        log(f"  {i}. {s['h']}")

    parts_html = []

    # ── STEP 2: เขียน Intro ───────────────────────────────
    log_info("STEP 2/6 — เขียน Intro...")
    intro_raw = เรียก_ollama(
        f"เขียนย่อหน้าเปิดบทความภาษาไทยเรื่อง \"{หัวข้อ}\" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n"
        f"{ctx}\n"
        f"สไตล์: บล็อกเกอร์ไทยที่รู้จริงเรื่องนี้ พูดกับเพื่อนสนิท ไม่ต้องทางการ\n"
        f"กฎสำคัญ:\n"
        f"- เขียน 3-4 ย่อหน้า รวม 300-500 คำ\n"
        f"- ประโยคแรก ห้ามขึ้นต้นด้วย 'บทความนี้' 'วันนี้' 'ในปัจจุบัน'\n"
        f"  ให้ใช้แทนด้วย: ตั้งคำถามน่าสงสัย / ตัวเลขสะดุดตา / เหตุการณ์จริงสั้นๆ\n"
        f"- ย่อหน้า 2-3: อธิบายว่าทำไมเรื่องนี้สำคัญกับชีวิตของผู้อ่านโดยตรง\n"
        f"- ย่อหน้าสุดท้าย: บอกว่าในบทความนี้จะได้อะไรบ้าง (ไม่ต้องใช้คำว่า 'บทความนี้')\n"
        f"- ใช้คำว่า 'นะ' 'ครับ/ค่ะ' 'จริงๆ' 'อย่างนี้' ได้บ้างเพื่อความเป็นกันเอง\n"
        f"- เขียน Markdown เท่านั้น ห้าม HTML",
        timeout=180, num_predict=1500
    )
    intro_html = ทำความสะอาด_html(แปลง_md_html(intro_raw))
    if len(intro_html) > 100:
        parts_html.append(intro_html)
        log_ok(f"Intro เสร็จ: {len(intro_html)} ตัว")
    else:
        log_warn("Intro สั้นมาก — ใช้ fallback")
        parts_html.append(f"<p>{หัวข้อ} เป็นเรื่องที่น่าสนใจและมีความสำคัญในชีวิตประจำวัน บทความนี้จะพาคุณไปทำความรู้จักกับทุกแง่มุมของเรื่องนี้อย่างละเอียด</p>")

    # ── STEP 3: เขียนทีละ Section ─────────────────────────
    log_info("STEP 3/6 — เขียนทีละ Section...")
    for i, sec in enumerate(sections):
        log_info(f"  Section {i+1}/{len(sections)}: {sec['h']}")

        # ใช้ข้อมูลอ้างอิงที่ตรงกว่าสำหรับแต่ละ section
        ctx_sec = f"\nข้อมูลอ้างอิง:\n{อ้างอิง[:1500]}\n" if อ้างอิง else ""

        # สุ่มสไตล์ย่อยเพื่อให้แต่ละ section ไม่ซ้ำกัน
        _micro_styles = [
            "เล่าเรื่องจากประสบการณ์จริง มีอารมณ์ขันเล็กน้อย ภาษาพูด",
            "ให้ข้อมูลเชิงลึก ตัวเลข สถิติ เปรียบเทียบ ก่อน-หลัง",
            "ตั้งคำถามนำ แล้วตอบทีละประเด็น เหมือน Q&A สั้นๆ",
            "เล่าเป็น story arc: ปัญหา → ลองแก้ → ผลที่ได้ → บทเรียน",
            "ให้ step-by-step ที่ทำได้จริงวันนี้เลย พร้อมเตือนข้อผิดพลาดที่พบบ่อย",
        ]
        _style = _micro_styles[i % len(_micro_styles)]
        section_raw = เรียก_ollama(
            f"เขียนเนื้อหาส่วน \"{sec['h']}\" ของบทความเรื่อง \"{หัวข้อ}\"\n"
            f"หมวด: {หมวด_ไทย.get(หมวด, หมวด)} | ประเด็นหลัก: {sec['desc']}\n"
            f"{ctx_sec}\n"
            f"## {sec['h']}\n\n"
            f"สไตล์บังคับสำหรับ section นี้: {_style}\n"
            f"กฎ:\n"
            f"- เขียน 4-6 ย่อหน้า รวม 400-600 คำ\n"
            f"- ย่อหน้าแรกต้องดึงดูดด้วยคำถาม, ตัวเลข, หรือเหตุการณ์จริง\n"
            f"- ห้ามขึ้นต้นทุกย่อหน้าด้วย 'นอกจากนี้' 'อีกทั้ง' 'ดังนั้น'\n"
            f"- ใส่ตัวอย่างที่คนไทยเข้าใจได้ทันที (อาหาร สถานที่ บุคคล)\n"
            f"- สลับ: บางย่อหน้าเล่าเรื่อง บางย่อหน้าเป็น bullet 3-5 ข้อ\n"
            f"- เขียน Markdown เท่านั้น ห้าม HTML",
            timeout=250, num_predict=2500
        )

        section_html = ทำความสะอาด_html(แปลง_md_html(section_raw))

        # ตรวจสอบคุณภาพ — ถ้าสั้นเกินไป ลองใหม่อีกครั้ง
        if len(section_html) < 300:
            log_warn(f"  Section {i+1} สั้นเกิน ({len(section_html)} ตัว) — ลองใหม่...")
            section_raw2 = เรียก_ollama(
                f"เขียนเนื้อหาเรื่อง \"{sec['h']}\" ให้ยาวและละเอียด\n"
                f"หัวข้อหลัก: {หัวข้อ} (หมวด{หมวด_ไทย.get(หมวด,หมวด)})\n"
                f"ครอบคลุม: {sec['desc']}\n\n"
                f"ต้องมี: ย่อหน้าอย่างน้อย 4 ย่อหน้า, ตัวอย่างจริง, รายการ bullet\n"
                f"ตอบเป็น Markdown ใช้ ## และ - เท่านั้น ห้ามใช้ HTML",
                timeout=220, num_predict=2200
            )
            section_html = ทำความสะอาด_html(แปลง_md_html(section_raw2))

        # แทรกรูปตรงกลางบทความแค่ 1 รูป (section กลาง) — keyword ตรงหัวข้อบทความหลัก
        mid = len(sections) // 2
        if i == mid:
            # ใช้หัวข้อบทความหลักเป็น keyword หลัก ไม่ใช่ section ย่อย → รูปตรงกว่า
            img_html = สร้างรูป_inline(หัวข้อ, หมวด, หัวข้อ_บทความ=หัวข้อ, filename="")
            parts_html.append(img_html)
            log_info(f"  แทรกรูปกลางบทความ (section {i+1}/{len(sections)})")

        parts_html.append(section_html)
        log_ok(f"  Section {i+1} เสร็จ: {len(section_html)} ตัว")
        time.sleep(0.3)  # ป้องกัน Ollama overload

    # ── STEP 4: YouTube Embed ─────────────────────────────
    log_info("STEP 4/7 — ค้นหา YouTube embed...")
    youtube_html = ดึง_youtube_embed(หัวข้อ, หมวด)
    if youtube_html:
        parts_html.append(youtube_html)
        log_ok("เพิ่ม YouTube embed แล้ว")

    # ── STEP 5: FAQ ───────────────────────────────────────
    log_info("STEP 5/7 — เขียน FAQ...")
    faq_raw = เรียก_ollama(
        f"เขียน FAQ (คำถามที่พบบ่อย) สำหรับบทความเรื่อง \"{หัวข้อ}\"\n"
        f"กฎ: 5 คำถาม แต่ละคำถามมีคำตอบ 2-3 ประโยค\n"
        f"รูปแบบ Markdown: ใช้ ### คำถาม และขึ้นบรรทัดใหม่ตอบคำถาม ห้ามใช้ HTML",
        timeout=180, num_predict=1500
    )
    faq_html = ทำความสะอาด_html(แปลง_md_html(faq_raw))
    if len(faq_html) > 100:
        # สร้าง FAQPage schema จาก faq_raw
        import re as _re
        faq_pairs = []
        qs = _re.split(r'(?:^|\n)#{2,3}\s+', faq_raw.strip())
        for block in qs:
            block = block.strip()
            if not block: continue
            lines = block.split("\n", 1)
            q = lines[0].strip().lstrip("0123456789.) ").strip("?")
            a = lines[1].strip() if len(lines) > 1 else ""
            a = _re.sub(r'[\n\r]+', " ", a).strip()
            if q and a and any("\u0e00" <= c <= "\u0e7f" for c in q):
                q_esc = q.replace('"', '\"')
                a_esc = a[:300].replace('"', '\"')
                faq_pairs.append(f'{{"@type":"Question","name":"{q_esc}","acceptedAnswer":{{"@type":"Answer","text":"{a_esc}"}}}}'
                )
        if faq_pairs:
            _joined = ",".join(faq_pairs[:5])
            faq_ld = (
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@type":"FAQPage",'
                '"mainEntity":[' + _joined + ']}'
                '</script>'
            )
            parts_html.append(faq_ld)
        parts_html.append(
            f'\n<div style="background:var(--soft,#f1f5f9);border-radius:12px;padding:1.5rem;margin-top:2rem;">'
            f'\n<h2 style="color:var(--primary,#1e40af);margin-top:0;">❓ คำถามที่พบบ่อย</h2>'
            f'\n{faq_html}\n</div>'
        )
        log_ok(f"FAQ เสร็จ: {len(faq_html)} ตัว + FAQPage schema")

    # ── STEP 6: Conclusion ────────────────────────────────
    log_info("STEP 6/7 — เขียน Conclusion...")
    conclusion_raw = เรียก_ollama(
        f"เขียนบทสรุปของบทความเรื่อง \"{หัวข้อ}\" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n"
        f"## สรุป\n\n"
        f"กฎ:\n"
        f"- ย่อหน้า 1: สรุป insight สำคัญที่สุด 1-2 ข้อ\n"
        f"- ย่อหน้า 2: บอกว่าถ้าจะเริ่มทำ ควรเริ่มตรงไหนก่อน (CTA ชัดเจน)\n"
        f"- ย่อหน้า 3: ปิดด้วยประโยคสร้างแรงบันดาลใจ ไม่ใช่แค่ 'หวังว่าจะเป็นประโยชน์'\n"
        f"- ห้ามใช้ประโยคปิดแบบ AI ทั่วไป เช่น 'หวังว่าบทความนี้จะเป็นประโยชน์'\n"
        f"- เขียน Markdown ห้ามใช้ HTML",
        timeout=150, num_predict=1000
    )
    conclusion_html = ทำความสะอาด_html(แปลง_md_html(conclusion_raw))
    if len(conclusion_html) > 80:
        parts_html.append(conclusion_html)
        log_ok(f"Conclusion เสร็จ: {len(conclusion_html)} ตัว")

    # ── STEP 7: Affiliate / Download links ──────────────
    log_info("STEP 7/7 — สร้าง Affiliate block...")
    aff_html = สร้าง_affiliate_block(หัวข้อ, หมวด)
    if aff_html:
        parts_html.append(aff_html)
        log_ok("เพิ่ม Affiliate block แล้ว")

    # ── STEP 8: รวมทุกส่วน ───────────────────────────────
    log_info("STEP 8/8 — รวมบทความ...")
    result = "\n\n".join(parts_html)
    total_len = len(result)
    total_words = len(result.split())

    log_ok(f"บทความสมบูรณ์: {total_len:,} ตัวอักษร | ~{total_words:,} คำ")

    if total_len < 1000:
        log_warn("บทความสั้นเกินไป! ตรวจสอบ Ollama ว่าทำงานอยู่")

    return result


# ══════════════════════════════════════════════════════════════
# 🏗️ Topic Cluster — สร้างหลายบทความเชื่อมกัน
# ══════════════════════════════════════════════════════════════
def ai_คิดหัวข้อย่อย(หัวข้อหลัก: str, หมวด: str) -> list:
    log_ai(f"คิดหัวข้อย่อย: {หัวข้อหลัก}")
    raw = เรียก_ollama(
        f'หัวข้อหลัก: "{หัวข้อหลัก}" (หมวด: {หมวด_ไทย.get(หมวด, หมวด)})\n'
        f'คิดหัวข้อบทความที่เกี่ยวข้อง 4 หัวข้อ\n'
        f'กฎ:\n'
        f'- แต่ละหัวข้อต้องต่างกันอย่างชัดเจน\n'
        f'- ครอบคลุมคนละมุม: เช่น วิธีทำ / ประวัติ / เปรียบเทียบ / แก้ปัญหา\n'
        f'- ตอบแค่รายการ บรรทัดละ 1 หัวข้อ ไม่ต้องใส่หมายเลข',
        timeout=90
    )
    result = []
    for line in raw.split("\n"):
        line = line.strip().lstrip("0123456789.-) ").strip()
        # กรอง <think> tags จาก deepseek
        line = re.sub(r'<think>.*?</think>', '', line, flags=re.DOTALL).strip()
        if len(line) > 5 and any('\u0e00' <= c <= '\u0e7f' for c in line):
            result.append(line)
    return result[:4] if len(result) >= 2 else [
        f"ประโยชน์ของ{หัวข้อหลัก}",
        f"วิธีเริ่มต้น{หัวข้อหลัก}สำหรับมือใหม่",
        f"ข้อผิดพลาดที่ควรหลีกเลี่ยงใน{หัวข้อหลัก}",
    ]


def สร้าง_topic_cluster(หัวข้อหลัก: str, หมวด: str) -> list:
    log_section(f"🏗️ Topic Cluster: {หัวข้อหลัก}")
    บทความทั้งหมด = []

    # บทความหลัก
    log_info("เขียนบทความหลัก...")
    เนื้อหา = เขียนบทความ(หัวข้อหลัก, หมวด)
    if เนื้อหา:
        ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อหลัก, หมวด, เนื้อหา)
        บทความทั้งหมด.append((หัวข้อหลัก, ชื่อไฟล์, รูป))
        log_ok(f"บทความหลัก: {ชื่อไฟล์}")

    # บทความย่อย (3 บทความ)
    หัวข้อย่อย = ai_คิดหัวข้อย่อย(หัวข้อหลัก, หมวด)
    for i, หัวข้อ_ย่อย in enumerate(หัวข้อย่อย[:3]):
        log_info(f"เขียนบทความย่อย {i+1}/{min(len(หัวข้อย่อย),3)}: {หัวข้อ_ย่อย}")
        เนื้อหา = เขียนบทความ(หัวข้อ_ย่อย, หมวด)
        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ย่อย, หมวด, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_ย่อย, ชื่อไฟล์, รูป))
            log_ok(f"บทความย่อย {i+1}: {ชื่อไฟล์}")

    return บทความทั้งหมด


# ══════════════════════════════════════════════════════════════
# 💾 บันทึกบทความ + HTML Template
# ══════════════════════════════════════════════════════════════
def _head_html(title, desc, filename, og_img="", cat="", cat_th="", date_iso=""):
    og_img  = og_img or f"{SITE_URL}/images/og-default.png"
    _gsc    = os.getenv("GSC_VERIFY", "")   # Google Search Console verify tag
    _gsc_tag = f'\n  <meta name="google-site-verification" content="{_gsc}">' if _gsc else ""
    ga4 = (
        f'\n  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
        f'\n  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
        f'gtag("js",new Date());gtag("config","{GA4_ID}");</script>'
    ) if GA4_ID else ""
    # Breadcrumb JSON-LD
    _cat_url = f"{SITE_URL}/{cat}.html" if cat else f"{SITE_URL}/"
    _cat_label = cat_th or cat or "หน้าแรก"
    _breadcrumb = f"""
  <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"BreadcrumbList",
    "itemListElement":[
      {{"@type":"ListItem","position":1,"name":"หน้าแรก","item":"{SITE_URL}/"}},
      {{"@type":"ListItem","position":2,"name":"{_cat_label}","item":"{_cat_url}"}},
      {{"@type":"ListItem","position":3,"name":"{title.split(" | ")[0]}","item":"{SITE_URL}/{filename}"}}
    ]
  }}</script>"""
    # WebPage + Article combined JSON-LD
    _article_ld = f"""
  <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"Article",
    "headline":"{title.split(" | ")[0]}",
    "description":"{desc}",
    "image":"{og_img}",
    "datePublished":"{date_iso}",
    "dateModified":"{date_iso}",
    "inLanguage":"th",
    "author":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},
    "publisher":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}","logo":{{"@type":"ImageObject","url":"{SITE_URL}/images/icon-192.png"}}}},
    "mainEntityOfPage":{{"@type":"WebPage","@id":"{SITE_URL}/{filename}"}}
  }}</script>"""
    return f"""  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="robots" content="index, follow">
  <meta name="theme-color" content="#1e40af">{_gsc_tag}
  <link rel="canonical" href="{SITE_URL}/{filename}">
  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="images/icon-192.png">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_img}">
  <meta property="og:url" content="{SITE_URL}/{filename}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="th_TH">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_img}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="stylesheet" href="style.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB}" crossorigin="anonymous"></script>{ga4}{_breadcrumb}{_article_ld}"""


ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
{head}
</head>
<body>
<script src="nav.js"></script>
<div class="container">
  <article class="article-card content-area">
    <h1>{title}</h1>
    <div class="article-meta">
      <i class="far fa-calendar-alt"></i> วันที่: {date_th} |
      <i class="fas fa-tag"></i> หมวด: <a href="{cat_page}">{category_th}</a>
    </div>
    <div class="hero-image-wrapper">
      <img src="{img_url}" alt="{title}" loading="eager"
           onerror="this.onerror=null;this.src='{img_fallback}'">
    </div>
    <div class="article-body">
      {content}
    </div>
    <div class="share-buttons" style="margin:2rem 0 1rem;padding:1rem 1.25rem;background:var(--soft,#f1f5f9);border-radius:12px;">
      <p style="margin:0 0 0.75rem;font-size:0.9rem;font-weight:600;color:var(--dark,#1e293b);">
        <i class="fas fa-share-alt"></i> แชร์บทความนี้
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">
        <a href="https://www.facebook.com/sharer/sharer.php?u={site_url}/{filename}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#1877f2;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-facebook-f"></i> Facebook</a>
        <a href="https://twitter.com/intent/tweet?url={site_url}/{filename}&text={title}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#000;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-x-twitter"></i> X</a>
        <a href="https://line.me/R/msg/text/?{title}%0A{site_url}/{filename}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#06c755;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-line"></i> LINE</a>
        <a href="https://wa.me/?text={title}%20{site_url}/{filename}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#25d366;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-whatsapp"></i> WhatsApp</a>
        <a href="https://t.me/share/url?url={site_url}/{filename}&text={title}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#229ed9;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-telegram-plane"></i> Telegram</a>
        <a href="https://www.tiktok.com/share?url={site_url}/{filename}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#010101;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-tiktok"></i> TikTok</a>
        <a href="https://threads.net/intent/post?text={title}%20{site_url}/{filename}" target="_blank" rel="noopener"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:#101010;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;font-weight:600;white-space:nowrap;">
          <i class="fab fa-square-threads"></i> Threads</a>
        <button onclick="navigator.clipboard.writeText('{site_url}/{filename}').then(()=>{{this.innerHTML='<i class=\'fas fa-check\'></i> คัดลอกแล้ว!';setTimeout(()=>this.innerHTML='<i class=\'fas fa-link\'></i> คัดลอกลิงก์',2000)}})"
           style="display:inline-flex;align-items:center;gap:0.4rem;padding:0.45rem 1rem;background:var(--primary,#1e40af);color:#fff;border-radius:6px;border:none;font-size:0.85rem;font-weight:600;cursor:pointer;white-space:nowrap;font-family:inherit;">
          <i class="fas fa-link"></i> คัดลอกลิงก์</button>
      </div>
    </div>
        <script type="application/ld+json">
    {{
      "@context":"https://schema.org",
      "@type":"Article",
      "headline":"{title}",
      "image":"{img_url}",
      "datePublished":"{date_iso}",
      "dateModified":"{date_iso}",
      "author":{{"@type":"Organization","name":"{site_name}"}},
      "publisher":{{"@type":"Organization","name":"{site_name}","url":"{site_url}"}}
    }}
    </script>
  </article>
  {sidebar}
</div>
{footer_html}
</body>
</html>"""


def _footer_html(year: int, site_name: str, site_url: str) -> str:
    """Footer ที่อ่านค่า social links และสีจาก SIDEBAR_CONFIG + THEME ใน config.py"""
    from config import SIDEBAR_CONFIG
    cfg = SIDEBAR_CONFIG
    # ── สีตรงกับ nav/hero (ดึงจาก CSS variable หรือ default) ──
    footer_bg = "#0f172a"   # ตรง theme dark ของ blue theme (default)
    link_style = "color:rgba(255,255,255,0.75);text-decoration:none;"
    social_items = []
    if cfg.get("facebook_url"):
        social_items.append(f'<a href="{cfg["facebook_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-facebook-f"></i> Facebook</a>')
    if cfg.get("youtube_url"):
        social_items.append(f'<a href="{cfg["youtube_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-youtube"></i> YouTube</a>')
    if cfg.get("tiktok_url"):
        social_items.append(f'<a href="{cfg["tiktok_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-tiktok"></i> TikTok</a>')
    if cfg.get("instagram_url"):
        social_items.append(f'<a href="{cfg["instagram_url"]}" target="_blank" rel="noopener" style="{link_style}"><i class="fab fa-instagram"></i> Instagram</a>')
    social_html = "\n      ".join(social_items)
    return f"""<footer style="background:{footer_bg};color:rgba(255,255,255,0.85);text-align:center;padding:2rem 1rem 1.5rem;font-size:0.88rem;margin-top:2rem;">
  <div style="max-width:800px;margin:0 auto;">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0.5rem 1.2rem;margin-bottom:1rem;">
      <a href="index.html" style="{link_style}">🏠 หน้าแรก</a>
      <a href="contact.html" style="{link_style}">📬 ติดต่อเรา</a>
      <a href="privacy.html" style="{link_style}">🔒 นโยบายความเป็นส่วนตัว</a>
      <a href="sitemap.xml" style="{link_style}">🗺️ Sitemap</a>
      {social_html}
    </div>
    <p style="margin:0;color:rgba(255,255,255,0.5);font-size:0.82rem;">
      © {year} {site_name} · เว็บไซต์นี้ใช้ Google AdSense และลิงก์พันธมิตร (Affiliate) เพื่อสนับสนุนการดูแลเว็บไซต์
    </p>
  </div>
</footer>"""


def _sidebar_html() -> str:
    """Sidebar สนับสนุนเรา — อ่านจาก config.py (SIDEBAR_CONFIG)
    แก้ข้อมูลที่ config.py หรือ .env ที่เดียว ทุก agent อัปเดตพร้อมกัน"""
    return สร้าง_sidebar_html()


def บันทึกบทความ(หัวข้อ: str, หมวด: str, เนื้อหา: str) -> tuple:
    หมวดสะอาด = "".join(filter(str.isalnum, หมวด))
    timestamp  = int(time.time())
    ชื่อไฟล์   = f"{หมวดสะอาด}_{timestamp}.html"
    วันที่_th  = datetime.datetime.now().strftime("%d/%m/%Y")
    วันที่_iso = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00")
    ปีนี้      = datetime.datetime.now().year
    desc       = f"{หัวข้อ} — {SITE_NAME} เว็บเดียวครบทุกเรื่อง"
    cat_page   = CATEGORY_PAGE_MAP.get(หมวด, "news.html")

    # ดึงรูป hero — ใช้ robust function (5 fallback)
    รูป_url = ดึงรูป_robust(หัวข้อ, หมวด, ชื่อไฟล์)

    # สร้าง SVG เป็น fallback เสมอ
    svg_fallback = สร้าง_thumbnail_svg(หัวข้อ, หมวด, ชื่อไฟล์)

    # รูปที่ใช้ใน og: และใน <img> tag
    og_img       = รูป_url if รูป_url.startswith("http") else f"{SITE_URL}/{รูป_url}"
    รูป_ใน_หน้า = รูป_url

    head = _head_html(
        f"{หัวข้อ} | {SITE_NAME}", desc, ชื่อไฟล์, og_img,
        cat=หมวด, cat_th=หมวด_ไทย.get(หมวด, หมวด), date_iso=วันที่_iso
    )
    html = ARTICLE_TEMPLATE.format(
        head=head, title=หัวข้อ, desc=desc,
        img_url=รูป_ใน_หน้า,
        img_fallback=svg_fallback or f"https://picsum.photos/seed/{hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]}/800/450",
        date_iso=วันที่_iso, date_th=วันที่_th,
        category_th=หมวด_ไทย.get(หมวด, หมวด),
        cat_page=cat_page,
        content=เนื้อหา, filename=ชื่อไฟล์,
        year=ปีนี้, site_name=SITE_NAME, site_url=SITE_URL,
        sidebar=_sidebar_html(),
        footer_html=_footer_html(ปีนี้, SITE_NAME, SITE_URL),
    )

    if not DRY_RUN:
        (BASE_PATH / ชื่อไฟล์).write_text(html, encoding="utf-8")
        log_ok(f"บันทึก: {ชื่อไฟล์} ({len(html):,} ตัว)")
    else:
        log_info(f"[DRY-RUN] จะบันทึก: {ชื่อไฟล์}")

    return ชื่อไฟล์, og_img


# ══════════════════════════════════════════════════════════════
# 🔍 เลือกหัวข้อ — RSS + Evergreen
# ══════════════════════════════════════════════════════════════
def ดึงหัวข้อที่มี() -> list:
    result = []
    for f in BASE_PATH.glob("*_*.html"):
        try:
            soup = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
            h1 = soup.find("h1")
            if h1:
                result.append(h1.get_text().strip())
        except Exception:
            pass
    return result


def เช็คซ้ำ(หัวข้อ: str, รายการที่มี: list) -> bool:
    if หัวข้อ in รายการที่มี:
        return True
    if not รายการที่มี:
        return False
    # FIX: ใช้ เรียก_ollama_เร็ว สำหรับงานเล็กๆ ประหยัดเวลา
    ผล = เรียก_ollama_เร็ว(
        f'หัวข้อใหม่: "{หัวข้อ}"\nหัวข้อที่มีอยู่:\n' +
        "\n".join(f"- {t}" for t in รายการที่มี[-20:]) +
        '\nตอบแค่: YES หรือ NO (YES=ซ้ำหรือคล้ายมาก)',
    ).upper()
    if not ผล:  # แก้บั๊ก 4: guard กรณี timeout คืนค่าว่าง
        return False
    return "YES" in ผล


EVERGREEN_POOL = [
    "7 วิธีดูแลสุขภาพที่ทำได้ทุกวัน | health",
    "เคล็ดลับออมเงินเดือนละ 5,000 | finance",
    "สูตรต้มยำกุ้งน้ำข้นต้นตำรับ | food",
    "10 อนิเมะที่ดีที่สุดตลอดกาล | anime",
    "วิธีเลี้ยงแมวสำหรับมือใหม่ | pet",
    "กฎหมายที่คนไทยควรรู้ทุกคน | law",
    "วิธีเริ่มต้นธุรกิจออนไลน์ด้วยทุนน้อย | business",
    "ที่เที่ยวเชียงใหม่ 3 วัน 2 คืน | travel",
    "DIY ของแต่งบ้านจากวัสดุเหลือใช้ | diy",
    "10 เกม PC ฟรีที่ดีที่สุด | gaming",
    "วิธีลดน้ำหนักอย่างปลอดภัยใน 3 เดือน | health",
    "แต่งบ้านสไตล์มินิมอลงบน้อย | lifestyle",
    "วิธีดูแลรถยนต์ด้วยตัวเองเบื้องต้น | car",
    "ทำผมสวยที่บ้าน ไม่ต้องไปร้าน | beauty",
    "วิธีสอนลูกให้รักการอ่าน | education",
]


def ai_evergreen() -> str:
    หมวด = random.choice(CATEGORIES)
    หมวด_th = หมวด_ไทย.get(หมวด, หมวด)
    raw = เรียก_ollama(
        f'คิดหัวข้อบทความภาษาไทยหมวด "{หมวด_th}" 1 หัวข้อ\n'
        f'เงื่อนไข: คนไทยค้นหาตลอดกาล เฉพาะเจาะจง ไม่ซ้ำกับหัวข้อทั่วไป\n'
        f'ตอบรูปแบบ: หัวข้อ | {หมวด}',
        timeout=60
    )
    # กรอง <think>
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    for line in raw.split("\n"):
        line = line.strip()
        if "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and len(parts[0]) > 5:
                h = parts[0].strip('"\'')
                m = parts[1].lower().strip()
                if m not in CATEGORIES:
                    m = หมวด
                return f"{h} | {m}"
    return random.choice(EVERGREEN_POOL)


RSS_ข่าว = [
    ("ไทยรัฐ",   "https://www.thairath.co.th/rss/news.xml"),
    ("BBC Thai", "https://feeds.bbci.co.uk/thai/rss.xml"),
    ("ข่าวสด",   "https://www.khaosod.co.th/feed"),
]


def ดึงเทรนด์_rss() -> list:
    result = []
    for ชื่อ, url in RSS_ข่าว:
        try:
            feed = feedparser.parse(url)
            items = [e.title for e in feed.entries[:5] if e.get("title","").strip()]
            result.extend(items)
            log_ok(f"{ชื่อ}: {len(items)} หัวข้อ")
        except Exception as e:
            log_warn(f"{ชื่อ}: {e}")
    return result


def เลือกหัวข้อ() -> tuple:
    """คืน (หัวข้อ, หมวด)"""
    เทรนด์ = ดึงเทรนด์_rss()
    if เทรนด์:
        raw = เรียก_ollama(
            f'จากหัวข้อข่าว: {", ".join(เทรนด์[:8])}\n'
            f'เลือก 1 หัวข้อที่น่าสนใจสำหรับบทความบล็อก ตอบรูปแบบ: หัวข้อ | หมวด\n'
            f'หมวดเลือกจาก: {", ".join(CATEGORIES)}',
            timeout=90
        )
        raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
        for line in raw.split("\n"):
            line = line.strip()
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2 and len(parts[0]) > 5:
                    หมวด = parts[1].lower().strip()
                    if หมวด in CATEGORIES:
                        return parts[0], หมวด

    raw = ai_evergreen()
    parts = [p.strip() for p in raw.split("|")]
    return parts[0], (parts[1] if len(parts) > 1 and parts[1] in CATEGORIES else "lifestyle")


# ══════════════════════════════════════════════════════════════
# 🔗 Internal Links + อัปเดตหน้าหมวด
# ══════════════════════════════════════════════════════════════
def ใส่_internal_links(ชื่อไฟล์: str, หมวด: str):
    filepath = BASE_PATH / ชื่อไฟล์
    if not filepath.exists():
        return
    html = filepath.read_text(encoding="utf-8")
    MARKER_START = "<!-- related-articles-block -->"
    MARKER_END   = "<!-- /related-articles-block -->"

    # แก้บั๊ก 2: เช็คทั้ง MARKER และ keyword ป้องกันซ้ำ
    if MARKER_START in html or "บทความที่เกี่ยวข้อง" in html:
        return
    หมวดสะอาด = "".join(filter(str.isalnum, หมวด.lower()))  # FIX: ประกาศก่อนใช้
    ไฟล์ = sorted(
        BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
        key=lambda f: f.stat().st_mtime, reverse=True
    )
    related = []
    for af in ไฟล์[:8]:
        if af.name == ชื่อไฟล์:
            continue
        try:
            soup = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1   = soup.find("h1")
            if h1:
                related.append((af.name, h1.get_text().strip()))
        except Exception:
            pass
        if len(related) >= 5:
            break

    if not related:
        return

    MARKER_START = "<!-- related-articles-block -->"
    MARKER_END   = "<!-- /related-articles-block -->"
    cards = "".join(
        f'<a href="{fn}" style="display:flex;align-items:center;gap:0.75rem;'
        f'padding:0.65rem 1rem;margin-bottom:0.4rem;background:var(--soft,#f1f5f9);'
        f'border-radius:8px;color:inherit;text-decoration:none;'
        f'border-left:3px solid var(--primary,#1e40af);font-size:0.92rem;">'
        f'<i class="fas fa-arrow-right" style="color:var(--primary,#1e40af);'
        f'font-size:0.75rem;flex-shrink:0;"></i>'
        f'<span>{title}</span></a>'
        for fn, title in related
    )
    block = (
        "\n" + MARKER_START +
        '\n<div style="margin-top:2rem;padding:1.2rem;background:var(--soft,#f1f5f9);border-radius:12px;">'
        '\n<h3 style="color:var(--primary,#1e40af);margin:0 0 0.85rem;font-size:1rem;">'
        '<i class="fas fa-link"></i> บทความที่เกี่ยวข้อง</h3>'
        + cards + "\n</div>\n" + MARKER_END
    )

    if "</article>" in html:
        html = html.replace("</article>", block + "\n</article>", 1)
    elif "</main>" in html:
        html = html.replace("</main>", block + "\n</main>", 1)

    if not DRY_RUN:
        filepath.write_text(html, encoding="utf-8")
        log_ok(f"Internal links ({len(related)}) → {ชื่อไฟล์}")


def อัปเดตหน้าหลัก():
    """อัปเดต index.html ให้แสดงบทความล่าสุดจากทุกหมวด (grid 3 คอลัมน์)"""
    path = BASE_PATH / "index.html"
    if not path.exists():
        log_warn("อัปเดตหน้าหลัก: ไม่พบ index.html")
        return

    # ดึงบทความล่าสุดทุกหมวด รวมกัน max 24 บทความ
    ไฟล์ทั้งหมด = []
    for หมวด in CATEGORIES:
        หมวดสะอาด = "".join(filter(str.isalnum, หมวด.lower()))
        for af in sorted(BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
                         key=lambda f: f.stat().st_mtime, reverse=True)[:6]:
            if af.exists() and af.stat().st_size > 100:
                ไฟล์ทั้งหมด.append(af)

    # เรียงตาม mtime ล่าสุด
    ไฟล์ทั้งหมด.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    ไฟล์ทั้งหมด = ไฟล์ทั้งหมด[:24]

    if not ไฟล์ทั้งหมด:
        log_warn("อัปเดตหน้าหลัก: ยังไม่มีบทความ")
        return

    การ์ด = ""
    for af in ไฟล์ทั้งหมด:
        try:
            soup   = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1     = soup.find("h1")
            หัวข้อ = h1.get_text().strip() if h1 else af.stem
            หมวด_af = af.stem.split("_")[0]
            หมวด_th = หมวด_ไทย.get(หมวด_af, หมวด_af)

            img_src = ""
            hero_wrap = soup.find(class_="hero-image-wrapper")
            if hero_wrap:
                hero_img = hero_wrap.find("img")
                if hero_img:
                    s = hero_img.get("src", "").strip()
                    if s and "icon" not in s.lower():
                        img_src = s
            if not img_src:
                og = soup.find("meta", property="og:image")
                if og and og.get("content", "").startswith("http"):
                    img_src = og["content"].strip()
            if not img_src:
                body_el = soup.find(class_="article-body")
                for img in (body_el or soup).find_all("img"):
                    s = img.get("src", "").strip()
                    if s and not s.endswith(".gif") and "icon" not in s.lower():
                        img_src = s; break
            if not img_src:
                seed = hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]
                img_src = f"https://picsum.photos/seed/{seed}/800/450"

            svg_fb = f"images/thumbs/{af.stem}.svg"
            onerror = f'onerror="this.onerror=null;this.src=\'{svg_fb}\'"'

            meta = soup.find(class_="article-meta")
            วันที่ = ""
            if meta:
                t = meta.get_text()
                if "วันที่:" in t:
                    วันที่ = t.split("วันที่:")[-1].split("|")[0].strip()
        except Exception:
            หัวข้อ = af.stem; import hashlib as _hl; img_src = f"https://picsum.photos/seed/{_hl.md5(af.stem.encode()).hexdigest()[:8]}/800/450"
            svg_fb = ""; onerror = ""; วันที่ = ""; หมวด_th = ""

        date_html = (f'<div style="font-size:.72rem;color:var(--muted,#64748b);margin:.3rem 0;">'
                     f'<i class="far fa-calendar-alt"></i> {วันที่}</div>') if วันที่ else ""
        badge_html = (f'<div class="cat-badge" style="background:var(--primary,#1e40af);color:#fff;'
                      f'font-size:.7rem;padding:2px 8px;border-radius:999px;display:inline-block;margin-bottom:.3rem;">'
                      f'{หมวด_th}</div>') if หมวด_th else ""
        การ์ด += (
            f'<a href="{af.name}" style="display:flex;flex-direction:column;background:var(--card,#fff);'
            f'border-radius:12px;overflow:hidden;border:1px solid var(--border,#e2e8f0);'
            f'text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s;"'
            f' onmouseover="this.style.transform=\'translateY(-3px)\';this.style.boxShadow=\'0 8px 24px rgba(0,0,0,.12)\'"'
            f' onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'">'
            f'<img src="{img_src}" alt="{หัวข้อ}" loading="lazy" {onerror}'
            f' style="width:100%;height:180px;object-fit:cover;">'
            f'<div style="padding:.9rem;flex:1;">'
            f'{badge_html}{date_html}'
            f'<h3 style="margin:0;font-size:.93rem;line-height:1.45;font-weight:700;'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{หัวข้อ}</h3>'
            f'</div></a>'
        )

    IDX_S = "<!-- INDEX_ARTICLES_START -->"
    IDX_E = "<!-- INDEX_ARTICLES_END -->"
    block = (
        f'\n{IDX_S}\n'
        f'<div class="article-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1.25rem;">'
        f'\n{การ์ด}\n</div>\n{IDX_E}\n'
    )

    html = path.read_text(encoding="utf-8")

    # ลบ block เก่า (ทั้ง marker ใหม่ และ embedded-articles-list)
    for _s, _e in [
        ("<!-- INDEX_ARTICLES_START -->", "<!-- INDEX_ARTICLES_END -->"),
        ("<!-- ARTICLE_LIST_START -->", "<!-- ARTICLE_LIST_END -->"),
        ("<!-- article-list -->", "<!-- /article-list -->"),
    ]:
        for _ in range(5):
            new = re.sub(re.escape(_s)+r".*?"+re.escape(_e), "", html, flags=re.DOTALL)
            if new == html: break
            html = new

    # แทนที่ placeholder "กำลังโหลดบทความ" ถ้ายังมีอยู่
    html = re.sub(
        r'<div[^>]*id="embedded-articles-list"[^>]*>.*?</div>',
        block, html, flags=re.DOTALL
    )

    # ถ้าไม่มี placeholder → แทรกหลัง <main>
    if IDX_S not in html:
        if "<main>" in html:
            html = html.replace("<main>", f"<main>\n{block}", 1)
        elif "</main>" in html:
            # แทรกก่อน </main>
            idx = html.rfind("</main>")
            html = html[:idx] + block + html[idx:]

    if not DRY_RUN:
        path.write_text(html, encoding="utf-8")
        log_ok(f"อัปเดต index.html — {len(ไฟล์ทั้งหมด)} บทความ")

def อัปเดตหน้าหมวด(หมวด: str, ชื่อไฟล์ใหม่: str = "", หัวข้อ_ใหม่: str = ""):
    # BUG FIX: lowercase เสมอก่อน lookup
    หมวด_lower = หมวด.lower().strip()
    ไฟล์หมวด = CATEGORY_PAGE_MAP.get(หมวด_lower, "news.html")
    path = BASE_PATH / ไฟล์หมวด
    if not path.exists():
        log_warn(f"อัปเดตหน้าหมวด: ไม่พบ {ไฟล์หมวด}")
        return

    # BUG FIX: ตรวจว่าไฟล์ใหม่บันทึกแล้วจริงก่อน glob
    if ชื่อไฟล์ใหม่ and not (BASE_PATH / ชื่อไฟล์ใหม่).exists():
        log_warn(f"อัปเดตหน้าหมวด: ยังไม่พบไฟล์ใหม่ {ชื่อไฟล์ใหม่} — รอ 1 วินาที")
        time.sleep(1)

    หมวดสะอาด = "".join(filter(str.isalnum, หมวด_lower))
    ไฟล์บทความ = sorted(
        BASE_PATH.glob(f"{หมวดสะอาด}_*.html"),
        key=lambda f: f.stat().st_mtime, reverse=True
    )
    if not ไฟล์บทความ:
        log_warn(f"อัปเดตหน้าหมวด: ไม่มีบทความใน {หมวด_lower}")
        return

    # BUG FIX: กรองเฉพาะไฟล์ที่มีอยู่จริง ป้องกัน card ชี้ไปไฟล์เก่า/ค้าง
    ไฟล์บทความ = [f for f in ไฟล์บทความ if f.exists() and f.stat().st_size > 100]
    if not ไฟล์บทความ:
        log_warn(f"อัปเดตหน้าหมวด: ไม่มีบทความที่ valid ใน {หมวด_lower}")
        return

    การ์ด = ""
    for af in ไฟล์บทความ[:24]:
        try:
            soup   = BeautifulSoup(af.read_text(encoding="utf-8"), "html.parser")
            h1     = soup.find("h1")
            หัวข้อ = h1.get_text().strip() if h1 else af.stem

            # ดึงรูป: hero-image-wrapper ก่อน → article-body → og:image → picsum
            img_src = ""
            hero_wrap = soup.find(class_="hero-image-wrapper")
            if hero_wrap:
                hero_img = hero_wrap.find("img")
                if hero_img:
                    s = hero_img.get("src", "").strip()
                    if s and "icon" not in s.lower():
                        img_src = s
            if not img_src:
                og = soup.find("meta", property="og:image")
                if og and og.get("content","").startswith("http"):
                    img_src = og["content"].strip()
            if not img_src:
                body_el = soup.find(class_="article-body")
                search_in = body_el if body_el else soup
                for img in search_in.find_all("img"):
                    s = img.get("src", "").strip()
                    if s and not s.endswith(".gif") and "icon" not in s.lower():
                        img_src = s
                        break
            # SVG local เป็น fallback สุดท้าย (ไม่ใช้เป็น primary)
            if not img_src:
                svg_local = f"images/thumbs/{af.stem}.svg"
                if (BASE_PATH / svg_local).exists():
                    img_src = svg_local
            if not img_src:
                seed = hashlib.md5(หัวข้อ.encode()).hexdigest()[:8]
                img_src = f"https://picsum.photos/seed/{seed}/800/450"

            svg_fb = f"images/thumbs/{af.stem}.svg"
            meta = soup.find(class_="article-meta")
            วันที่ = ""
            if meta:
                t = meta.get_text()
                if "วันที่:" in t:
                    วันที่ = t.split("วันที่:")[-1].split("|")[0].strip()
        except Exception:
            หัวข้อ = af.stem
            import hashlib as _hl; img_src = f"https://picsum.photos/seed/{_hl.md5(af.stem.encode()).hexdigest()[:8]}/800/450"
            svg_fb = ""
            วันที่ = ""

        onerror = f'onerror="this.onerror=null;this.src=\'{svg_fb}\'"' if svg_fb else ""
        date_html = (f'<div style="font-size:0.72rem;color:var(--muted,#64748b);margin-bottom:0.3rem;">'
                     f'<i class="far fa-calendar-alt"></i> {วันที่}</div>') if วันที่ else ""
        การ์ด += f"""
  <a href="{af.name}" style="display:flex;gap:1rem;align-items:flex-start;padding:0.85rem;
     background:var(--card,#fff);border-radius:10px;margin-bottom:0.6rem;text-decoration:none;
     color:inherit;border:1px solid var(--border,#e2e8f0);transition:box-shadow 0.2s;"
     onmouseover="this.style.boxShadow='0 2px 12px rgba(0,0,0,.08)'"
     onmouseout="this.style.boxShadow='none'">
    <img src="{img_src}" alt="{หัวข้อ}"
         style="width:140px;height:95px;object-fit:cover;border-radius:8px;flex-shrink:0;"
         loading="lazy" {onerror}>
    <div style="flex:1;min-width:0;">
      {date_html}
      <h3 style="margin:0;font-size:0.95rem;line-height:1.45;font-weight:600;
         overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">{หัวข้อ}</h3>
    </div>
    <i class="fas fa-chevron-right" style="color:var(--muted,#64748b);font-size:0.75rem;flex-shrink:0;margin-top:0.3rem;"></i>
  </a>"""

    # ใช้ marker เดียวกับ agent_fix_v4.py เพื่อป้องกัน block ซ้อน
    ART_S_W = "<!-- ARTICLE_LIST_START -->"
    ART_E_W = "<!-- ARTICLE_LIST_END -->"
    ส่วนบทความ = (
        f"\n{ART_S_W}\n"
        f'<div style="background:var(--card,#fff);border-radius:16px;padding:1.25rem;'
        f'box-shadow:0 4px 12px rgba(30,64,175,0.06);margin-top:1rem;">'
        f'\n<h2 style="color:var(--primary,#1e40af);font-size:1.1rem;margin:0 0 1rem;">'
        f'\n  <i class="fas fa-list-ul"></i> บทความล่าสุด ({len(ไฟล์บทความ)} บทความ)'
        f'\n</h2>'
        f'\n{การ์ด}\n</div>'
        f"\n{ART_E_W}\n"
    )

    html = path.read_text(encoding="utf-8")
    # ลบ block เก่าทุกรูปแบบก่อน (ทั้ง marker เก่าและใหม่)
    for _s, _e in [
        ("<!-- ARTICLE_LIST_START -->", "<!-- ARTICLE_LIST_END -->"),
        ("<!-- article-list -->", "<!-- /article-list -->"),
        ("<!-- ARTICLES_START -->", "<!-- ARTICLES_END -->"),
        ("<!-- posts-grid-start -->", "<!-- posts-grid-end -->"),
    ]:
        for _ in range(10):
            new_html = re.sub(re.escape(_s)+r".*?"+re.escape(_e), "", html, flags=re.DOTALL)
            if new_html == html: break
            html = new_html

    if "</main>" in html:
        html = html.replace("</main>", ส่วนบทความ + "\n</main>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", ส่วนบทความ + "\n</body>", 1)
    else:
        html += "\n" + ส่วนบทความ

    if not DRY_RUN:
        path.write_text(html, encoding="utf-8")
        log_ok(f"อัปเดตหน้าหมวด: {ไฟล์หมวด}")


# ══════════════════════════════════════════════════════════════
# 📱 Social Push
# ══════════════════════════════════════════════════════════════
def โพส_facebook(หัวข้อ: str, url: str, รูป: str, หมวด: str):
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        log_warn("ไม่มี Facebook token — ข้าม")
        return
    emoji = {"food":"🍜","health":"💚","finance":"💰","travel":"✈️",
             "anime":"🎌","gaming":"🎮","beauty":"💄"}.get(หมวด,"📰")
    try:
        r = requests.post(
            f"https://graph.facebook.com/{FB_PAGE_ID}/feed",
            data={"message": f"{emoji} {หัวข้อ}\n\n{url}",
                  "link": url, "access_token": FB_ACCESS_TOKEN},
            timeout=15
        )
        if r.status_code == 200:
            log_ok("โพส Facebook สำเร็จ!")
        else:
            log_warn(f"Facebook: {r.status_code} — {r.text[:100]}")
    except Exception as e:
        log_err(f"Facebook: {e}")


def โพส_line(หัวข้อ: str, url: str, หมวด: str):
    if not LINE_NOTIFY_TOKEN:
        return
    emoji = {"food":"🍜","health":"💚","finance":"💰"}.get(หมวด,"📰")
    try:
        r = requests.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"},
            data={"message": f"\n{emoji} {หัวข้อ}\n🔗 {url}"},
            timeout=15
        )
        if r.status_code == 200:
            log_ok("Line Notify สำเร็จ!")
    except Exception as e:
        log_err(f"Line Notify: {e}")


# ══════════════════════════════════════════════════════════════
# 🚀 Main
# ══════════════════════════════════════════════════════════════
def _บันทึกและอัปเดต(หัวข้อ: str, หมวด: str, เนื้อหา: str) -> tuple:
    """บันทึกบทความและอัปเดต links+หน้าหมวด+หน้าหลัก — ใช้ร่วมกัน"""
    ชื่อไฟล์, รูป = บันทึกบทความ(หัวข้อ, หมวด, เนื้อหา)
    ใส่_internal_links(ชื่อไฟล์, หมวด)
    อัปเดตหน้าหมวด(หมวด, ชื่อไฟล์, หัวข้อ)
    อัปเดตหน้าหลัก()   # ← FIX: อัปเดต index.html ด้วยทุกครั้ง
    article_url = f"{SITE_URL}/{ชื่อไฟล์}"
    โพส_facebook(หัวข้อ, article_url, รูป, หมวด)
    โพส_line(หัวข้อ, article_url, หมวด)
    return ชื่อไฟล์, รูป



def _progress_bar(done: int, total: int, width: int = 10) -> str:
    """แถบ progress unicode"""
    filled = int(width * done / total) if total else 0
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * done / total) if total else 0
    return f"[{bar}] {pct}%"


def main():
    log_section("🤖 Agent Writer v5 — เริ่ม Pipeline")

    หัวข้อ     = ""
    หมวด_force = ""   # --cat ระบุหมวดบังคับ
    url_target = ""
    args       = sys.argv[1:]

    # ── รับ arguments ─────────────────────────────────────────
    if "--topic" in args:
        idx = args.index("--topic")
        if idx + 1 < len(args):
            หัวข้อ = args[idx + 1]

    if "--url" in args:
        idx = args.index("--url")
        if idx + 1 < len(args):
            url_target = args[idx + 1]

    if "--cat" in args:
        idx = args.index("--cat")
        if idx + 1 < len(args):
            หมวด_force = args[idx + 1].lower().strip()
            if หมวด_force not in CATEGORIES:
                log_warn(f"หมวด '{หมวด_force}' ไม่พบ — ใช้อัตโนมัติ")
                หมวด_force = ""

    # จำนวนบทความ (--count N)
    จำนวน = 1
    if "--count" in args:
        idx = args.index("--count")
        if idx + 1 < len(args):
            try:
                จำนวน = max(1, min(50, int(args[idx + 1])))
            except ValueError:
                log_warn("--count ต้องเป็นตัวเลข — ใช้ค่า 1")

    # ── Helper ─────────────────────────────────────────────────
    def _pick(hint: str = "") -> tuple:
        """เลือกหัวข้อ+หมวด พร้อม override จาก --cat"""
        if hint:
            raw = เรียก_ollama_เร็ว(
                f'หัวข้อ: "{hint}"\nหมวดจาก: {", ".join(CATEGORIES)}\nตอบแค่ชื่อหมวดภาษาอังกฤษ 1 คำ'
            ).lower().strip()
            m = raw if raw in CATEGORIES else "lifestyle"
            return hint, (หมวด_force or m)
        h, m = เลือกหัวข้อ()
        return h, (หมวด_force or m)

    # ══════════════════════════════════════════════════════════
    # MODE: --cluster [--count N]
    # ══════════════════════════════════════════════════════════
    if "--cluster" in args:
        cluster_n = จำนวน if "--count" in args else 4
        log_section(f"🏗️ Cluster Mode — สร้าง {cluster_n} บทความเชื่อมกัน")

        หัวข้อ_หลัก, หมวด = _pick(หัวข้อ)
        if not หัวข้อ_หลัก:
            log_err("ไม่ได้หัวข้อ — หยุด")
            return

        log(f"📝 หัวข้อหลัก: {หัวข้อ_หลัก} | หมวด: {หมวด} | เป้า: {cluster_n} บทความ")
        บทความทั้งหมด = []
        เวลาเริ่ม = time.time()

        # บทความหลัก
        log(f"\n{_progress_bar(0, cluster_n)} [1/{cluster_n}] บทความหลัก")
        log_info(f"📄 เขียน: {หัวข้อ_หลัก}")
        เนื้อหา = เขียนบทความ(หัวข้อ_หลัก, หมวด)
        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_หลัก, หมวด, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_หลัก, ชื่อไฟล์, รูป))
            log_ok(f"✅ {ชื่อไฟล์}")

        # คิดหัวข้อย่อย
        ต้องการย่อย = cluster_n - 1
        หัวข้อย่อย = ai_คิดหัวข้อย่อย(หัวข้อ_หลัก, หมวด)
        while len(หัวข้อย่อย) < ต้องการย่อย:
            extra = ai_คิดหัวข้อย่อย(f"{หัวข้อ_หลัก} (มุมมองใหม่)", หมวด)
            existing = set(หัวข้อย่อย)
            for h in extra:
                if h not in existing:
                    หัวข้อย่อย.append(h)
                    existing.add(h)
            if not extra:
                break

        log_ok(f"หัวข้อย่อย: {หัวข้อย่อย[:ต้องการย่อย]}")

        for i, หัวข้อ_ย่อย in enumerate(หัวข้อย่อย[:ต้องการย่อย]):
            seq = i + 2
            log(f"\n{_progress_bar(seq-1, cluster_n)} [{seq}/{cluster_n}] บทความย่อย {i+1}")
            log_info(f"📄 เขียน: {หัวข้อ_ย่อย}")
            เนื้อหา = เขียนบทความ(หัวข้อ_ย่อย, หมวด)
            if เนื้อหา:
                ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ย่อย, หมวด, เนื้อหา)
                บทความทั้งหมด.append((หัวข้อ_ย่อย, ชื่อไฟล์, รูป))
                log_ok(f"✅ {ชื่อไฟล์}")
            else:
                log_warn(f"บทความย่อย {i+1} ล้มเหลว — ข้าม")
            time.sleep(1)

        ใช้เวลา = int(time.time() - เวลาเริ่ม)
        log_section(
            f"🎊 Cluster เสร็จ! {len(บทความทั้งหมด)}/{cluster_n} บทความ"
            f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
        )
        for h, f, _ in บทความทั้งหมด:
            log(f"   📄 {f} — {h}")
        if not DRY_RUN:
            log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")
        return

    # ══════════════════════════════════════════════════════════
    # MODE: --batch N  (ต่างจาก --count ตรงที่เลือกหัวข้อต่างกันทุกรอบ)
    # ══════════════════════════════════════════════════════════
    if "--batch" in args:
        bidx = args.index("--batch")
        batch_n = 5
        if bidx + 1 < len(args) and args[bidx + 1].isdigit():
            batch_n = max(1, min(50, int(args[bidx + 1])))

        log_section(f"📦 Batch Mode — สร้าง {batch_n} บทความ (หัวข้อต่างกันทุกครั้ง)")
        if หมวด_force:
            log_info(f"หมวดบังคับ: {หมวด_force} ({หมวด_ไทย.get(หมวด_force, หมวด_force)})")

        บทความทั้งหมด = []
        เวลาเริ่ม     = time.time()
        รายการที่มี   = ดึงหัวข้อที่มี()
        ล้มเหลวติดกัน = 0
        MAX_FAIL = 3

        while len(บทความทั้งหมด) < batch_n:
            log(f"\n{_progress_bar(len(บทความทั้งหมด), batch_n)} [{len(บทความทั้งหมด)+1}/{batch_n}]")
            h, m = _pick()
            if not h:
                log_err("เลือกหัวข้อไม่ได้ — หยุด")
                break
            if เช็คซ้ำ(h, รายการที่มี):
                log_warn(f"ซ้ำ: {h[:45]}... — ข้าม")
                ล้มเหลวติดกัน += 1
                if ล้มเหลวติดกัน >= MAX_FAIL:
                    log_warn(f"ซ้ำ {MAX_FAIL} ครั้งติดกัน — หยุด")
                    break
                continue
            log_info(f"📄 {h} [{หมวด_ไทย.get(m, m)}]")
            เนื้อหา = เขียนบทความ(h, m)
            if เนื้อหา:
                ชื่อไฟล์, รูป = _บันทึกและอัปเดต(h, m, เนื้อหา)
                บทความทั้งหมด.append((h, ชื่อไฟล์, รูป))
                รายการที่มี.append(h)
                log_ok(f"✅ {ชื่อไฟล์}")
                ล้มเหลวติดกัน = 0
                time.sleep(2)
            else:
                log_warn(f"เขียนไม่ได้: {h[:45]}")
                ล้มเหลวติดกัน += 1
                if ล้มเหลวติดกัน >= MAX_FAIL:
                    log_err(f"ล้มเหลว {MAX_FAIL} ครั้งติดกัน — ตรวจ Ollama")
                    break

        ใช้เวลา = int(time.time() - เวลาเริ่ม)
        log_section(
            f"🎊 Batch เสร็จ! {len(บทความทั้งหมด)}/{batch_n} บทความ"
            f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
        )
        for h, f, _ in บทความทั้งหมด:
            log(f"   📄 {f} — {h}")
        if not DRY_RUN and บทความทั้งหมด:
            log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")
        return

    # ══════════════════════════════════════════════════════════
    # MODE: --url (Rewrite จาก URL)
    # ══════════════════════════════════════════════════════════
    if url_target:
        สรุปเนื้อหา = ดึงเนื้อหาและ_Rewrite(url_target)
        if สรุปเนื้อหา:
            หัวข้อ = เรียก_ollama_เร็ว(
                f'จากสรุปนี้:\n{สรุปเนื้อหา[:500]}\n\nคิดหัวข้อบทความภาษาไทย 1 หัวข้อ ตอบแค่หัวข้อเดียวไม่ต้องมีคำอธิบาย'
            ).strip().split('\n')[0]
            log_ok(f"ได้หัวข้อจาก URL: {หัวข้อ}")
        else:
            log_err("ไม่สามารถดึงข้อมูลจาก URL ได้")
            return

    # ══════════════════════════════════════════════════════════
    # MODE: ปกติ — สร้าง N บทความ (--count N, default 1)
    # ══════════════════════════════════════════════════════════
    log_section(f"📝 Normal Mode — สร้าง {จำนวน} บทความ")
    บทความทั้งหมด = []
    เวลาเริ่ม     = time.time()
    รายการที่มี   = ดึงหัวข้อที่มี()

    for i in range(จำนวน):
        if จำนวน > 1:
            log(f"\n{_progress_bar(i, จำนวน)} [{i+1}/{จำนวน}]")

        if หัวข้อ and i == 0:
            หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน = _pick(หัวข้อ)
        else:
            หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน = _pick()

        if not หัวข้อ_ปัจจุบัน:
            log_err(f"ไม่ได้หัวข้อบทความที่ {i+1} — ข้าม")
            continue

        if เช็คซ้ำ(หัวข้อ_ปัจจุบัน, รายการที่มี):
            log_warn(f"หัวข้อซ้ำ: {หัวข้อ_ปัจจุบัน[:45]}... — ข้าม")
            continue

        log(f"📝 {หัวข้อ_ปัจจุบัน[:55]}... [{หมวด_ไทย.get(หมวด_ปัจจุบัน, หมวด_ปัจจุบัน)}]")
        เนื้อหา = เขียนบทความ(หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน)

        if เนื้อหา:
            ชื่อไฟล์, รูป = _บันทึกและอัปเดต(หัวข้อ_ปัจจุบัน, หมวด_ปัจจุบัน, เนื้อหา)
            บทความทั้งหมด.append((หัวข้อ_ปัจจุบัน, ชื่อไฟล์))
            รายการที่มี.append(หัวข้อ_ปัจจุบัน)
            log_ok(f"✅ {ชื่อไฟล์}")
        else:
            log_err(f"เขียนบทความที่ {i+1} ล้มเหลว")

        if i < จำนวน - 1:
            time.sleep(2)

    ใช้เวลา = int(time.time() - เวลาเริ่ม)
    log_section(
        f"🎊 เสร็จ! สร้าง {len(บทความทั้งหมด)}/{จำนวน} บทความ"
        f" | ⏱ {ใช้เวลา//60} นาที {ใช้เวลา%60} วินาที"
    )
    for h, f in บทความทั้งหมด:
        log(f"   📄 {f} — {h}")
    if not DRY_RUN and บทความทั้งหมด:
        log_info("รัน python agent_publish.py เพื่อ push ขึ้น GitHub/Vercel")


if __name__ == "__main__":
    main()