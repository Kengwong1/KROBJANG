"""
safe_patch.py  — แทนที่ฟังก์ชัน --dedup และ --fix-content แบบ Safe Interactive

วิธีใช้:
  import safe_patch ใน agent_fix_v6.py
  หรือ copy โค้ดทั้งก้อนไปแทนที่ฟังก์ชันเดิม 2 ตัว

แนวคิด:
  1. SCAN ก่อนเสมอ — ไม่แตะไฟล์จนกว่าผู้ใช้จะยืนยัน
  2. BACKUP อัตโนมัติก่อนเขียนทับ
  3. REVIEW mode — แสดงปัญหาแต่ละไฟล์ให้เลือก: แก้ / ข้าม / ดูก่อน / หยุด
  4. RESTORE คืนได้ทุกเมื่อถ้าผลออกมาแย่

─────────────────────────────────────────────────────────────────────────
ติดตั้ง: แทนที่ 2 ฟังก์ชันเดิมในไฟล์ agent_fix_v6.py ด้วยโค้ดนี้
  def แก้_duplicate_blocks_hard()   → บรรทัด 2234
  def แก้_เนื้อหาเพี้ยน()          → บรรทัด 3186
─────────────────────────────────────────────────────────────────────────
"""

import os, re, shutil, datetime
from pathlib import Path
from bs4 import BeautifulSoup

# ── ดึงจาก context ของ agent_fix_v6.py ──────────────────────────────────
# (ถ้า copy ไปแปะในไฟล์หลัก ตัวแปรพวกนี้มีอยู่แล้ว)
# BASE_PATH, DRY_RUN, log, log_ok, log_warn, log_err, log_info, log_section
# สแกน_html, สแกน_บทความ, ดึงหัวข้อ, เขียน, เรียก_ollama
# ART_S, ART_E, IDX_S, IDX_E, wipe_all_blocks

# ══════════════════════════════════════════════════════════════════════════
# 🔒  BACKUP HELPERS
# ══════════════════════════════════════════════════════════════════════════

def _backup_dir() -> Path:
    """สร้าง folder backup แยกตาม timestamp"""
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bk  = BASE_PATH / ".backups" / ts
    bk.mkdir(parents=True, exist_ok=True)
    return bk


def _backup_file(fp: Path, bk_dir: Path) -> Path:
    """copy ไฟล์เดิมเข้า backup dir และ return path"""
    dest = bk_dir / fp.name
    shutil.copy2(fp, dest)
    return dest


def _restore_backup(bk_dir: Path):
    """คืนทุกไฟล์จาก backup dir กลับไปที่เดิม"""
    restored = 0
    for fp in bk_dir.iterdir():
        if fp.suffix.lower() == ".html":
            dest = BASE_PATH / fp.name
            shutil.copy2(fp, dest)
            restored += 1
    log_ok(f"  ↩️  restore {restored} ไฟล์จาก {bk_dir.name}")


# ══════════════════════════════════════════════════════════════════════════
# 🎛️  INTERACTIVE PROMPT HELPER
# ══════════════════════════════════════════════════════════════════════════

def _ask(prompt: str, choices: str = "y/n/s/q") -> str:
    """
    ถามผู้ใช้และ return ตัวเลือกที่ได้รับ
    choices: y=แก้  n=ข้าม  s=ข้ามทั้งหมด  q=หยุดทั้งหมด
    """
    while True:
        try:
            ans = input(f"\n  {prompt} [{choices}]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  (ยกเลิก)")
            return "q"
        if ans in choices.split("/"):
            return ans
        valid = ", ".join(choices.split("/"))
        print(f"  กรุณากด: {valid}")


def _preview_file(fp: Path):
    """เปิดไฟล์ใน less / cat เพื่อดูเนื้อหา"""
    print(f"\n  📄 เปิดดู: {fp}")
    pager = "less" if shutil.which("less") else "cat"
    try:
        os.system(f'{pager} "{fp}"')
    except Exception:
        print("  (เปิดไม่ได้ — ดูเองที่ path ด้านบน)")


# ══════════════════════════════════════════════════════════════════════════
# 🗑️  SAFE --dedup  (แทนที่ แก้_duplicate_blocks_hard)
# ══════════════════════════════════════════════════════════════════════════

def แก้_duplicate_blocks_hard() -> int:
    """
    Safe Hard Dedup — scan ก่อน, แจ้งผู้ใช้, backup, แล้วค่อยลบ

    ขั้นตอน:
      1. สแกนหาไฟล์ที่มี block ซ้ำ
      2. แสดงรายการให้เห็น
      3. ถาม: แก้ทีละไฟล์ / แก้ทั้งหมด / ยกเลิก
      4. backup ก่อนเสมอ
      5. rebuild หลังเสร็จ
    """
    log_section("🔍 Safe Dedup — สแกนก่อน")

    _BLOCK_PAIRS = [
        (ART_S, ART_E),
        ("<!-- article-list -->", "<!-- /article-list -->"),
        (IDX_S, IDX_E),
    ]

    # ── Phase 1: สแกน ────────────────────────────────────────────────────
    ปัญหา: list[tuple[Path, list[str]]] = []

    for fp in สแกน_html():
        try:
            html = fp.read_text(encoding="utf-8", errors="ignore")
            found_pairs = []
            for s, e in _BLOCK_PAIRS:
                count = html.count(s)
                if count > 1:
                    found_pairs.append(f"  block '{s[:30]}...' ซ้ำ {count} ครั้ง")
                elif count == 1:
                    # block เดียว — อาจ ok แต่รายงานไว้
                    pass
            if found_pairs:
                ปัญหา.append((fp, found_pairs))
        except Exception as e:
            log_err(f"  scan {fp.name}: {e}")

    # ── Phase 2: รายงาน ──────────────────────────────────────────────────
    if not ปัญหา:
        log_ok("✅ ไม่พบ block ซ้ำ — ไม่ต้องทำอะไร")
        return 0

    log_warn(f"\n⚠️  พบ block ซ้ำใน {len(ปัญหา)} ไฟล์:")
    print()
    for i, (fp, details) in enumerate(ปัญหา, 1):
        print(f"  [{i:2d}] {fp.name}")
        for d in details:
            print(f"       {d}")
    print()

    # ── Phase 3: ถามผู้ใช้ ───────────────────────────────────────────────
    print("  ตัวเลือก:")
    print("    a = แก้ทั้งหมดเลย (backup อัตโนมัติก่อน)")
    print("    r = ดูทีละไฟล์แล้วเลือกเอง")
    print("    q = ยกเลิก ไม่ทำอะไร")
    print()

    mode = _ask("เลือก", "a/r/q")
    if mode == "q":
        log_info("ยกเลิก dedup")
        return 0

    # ── Phase 4: backup + แก้ ────────────────────────────────────────────
    bk_dir   = _backup_dir()
    แก้แล้ว  = 0
    skip_all = False

    log_info(f"  💾 backup → {bk_dir}")

    for fp, details in ปัญหา:
        if skip_all:
            break

        if mode == "r":
            # ── review ทีละไฟล์ ──────────────────────────────────────────
            print(f"\n  ━━ {fp.name} ━━")
            for d in details:
                print(f"  {d}")

            act = _ask("จัดการไฟล์นี้ว่าไง", "y=แก้/v=ดูก่อน/n=ข้าม/q=หยุด")

            if act == "v":
                _preview_file(fp)
                act = _ask("หลังดูแล้ว จัดการยังไง", "y=แก้/n=ข้าม/q=หยุด")

            if act == "q":
                log_info("  หยุดกลางคัน — ไฟล์ที่ยังไม่ได้แก้ไม่ถูกแตะ")
                break
            if act == "n":
                log_info(f"  ข้าม {fp.name}")
                continue

        # ── ลงมือแก้ ─────────────────────────────────────────────────────
        try:
            _backup_file(fp, bk_dir)
            orig = fp.read_text(encoding="utf-8", errors="ignore")
            html = orig
            for s, e in _BLOCK_PAIRS:
                html = wipe_all_blocks(html, s, e)

            if เขียน(fp, html, orig):
                แก้แล้ว += 1
                log_ok(f"  ✅ dedup: {fp.name}")
        except Exception as e:
            log_err(f"  dedup {fp.name}: {e}")

    # ── Phase 5: rebuild + สรุป ──────────────────────────────────────────
    if แก้แล้ว > 0 and not DRY_RUN:
        log_section("🔄 Rebuild หลัง dedup")
        rebuild_category_pages()
        rebuild_index_page()

    log_ok(f"\n✅ dedup เสร็จ: {แก้แล้ว}/{len(ปัญหา)} ไฟล์")
    log_info(f"  💾 backup อยู่ที่: {bk_dir}")
    log_info(f"  ↩️  ถ้าผิดพลาด: python agent_fix_v6.py --restore {bk_dir.name}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════════════════
# 🔧  SAFE --fix-content  (แทนที่ แก้_เนื้อหาเพี้ยน)
# ══════════════════════════════════════════════════════════════════════════

_AI_LEAKAGE_RE = [
    r'<p>\s*สไตล์บังคับ[^<]{0,500}</p>',
    r'<p>\s*สไตล์สำหรับ[^<]{0,500}</p>',
    r'<p>\s*สไตล์:[^<]{0,500}</p>',
    r'<p>\s*กฎ\s*:[^<]{0,500}</p>',
    r'<p>\s*กฎ\s*</p>',
    r'<p>\s*ประเด็นหลัก\s*:[^<]{0,500}</p>',
    r'<p>\s*ขอเนื้อหาส่วน[^<]{0,500}</p>',
    r'<p>\s*เขียน Markdown[^<]{0,500}</p>',
    r'<p>\s*ห้าม HTML[^<]{0,500}</p>',
    r'<p>\s*num_predict[^<]{0,300}</p>',
    r'<p>\s*temperature[^<]{0,300}</p>',
    r'<p>[⚠️✨🔴🔥💡📌]*\s*(สำคัญมาก|กฎสำคัญ|หมายเหตุ)[^<]{0,400}</p>',
    r'<p>\s*-\s*(เขียน|ห้าม|ใส่|สลับ|ตอบ)[^<]{0,300}</p>',
    r'<h[23][^>]*>\s*ย่อหน้า(ที่)?\s*\d+[^<]*</h[23]>',
]

_AI_LEAKAGE_TEXT = [
    "สไตล์บังคับ", "สไตล์สำหรับ section", "ประเด็นหลัก:",
    "ขอเนื้อหาส่วน", "เขียน Markdown", "ห้าม HTML",
    "num_predict", "temperature", "กฎ:", "กฎสำคัญ:",
]


def _scan_content_issues(fp: Path) -> dict:
    """
    สแกนปัญหาในไฟล์เดียว — return dict:
      {
        "instruction": ["ข้อความที่หลุด", ...],
        "dup_para":    ["ย่อหน้าซ้ำ", ...],
        "short":       จำนวนตัวอักษร หรือ None,
        "text_len":    ความยาวจริง,
        "title":       หัวข้อ,
      }
    """
    html = fp.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    หัวข้อ = ดึงหัวข้อ(soup, fp)
    body = (soup.find(class_="article-body") or
            soup.find("article") or soup.find("main"))

    result = {"instruction": [], "dup_para": [], "short": None,
              "text_len": 0, "title": หัวข้อ, "html": html}

    if not body:
        return result

    text = body.get_text("\n", strip=True)
    result["text_len"] = len(text)

    # 1. instruction หลุด
    for kw in _AI_LEAKAGE_TEXT:
        if kw in text:
            result["instruction"].append(kw)

    # 2. ย่อหน้าซ้ำ
    paras = [p.strip() for p in text.split("\n") if len(p.strip()) > 60]
    seen: set = set()
    for p in paras:
        key = p[:80]
        if key in seen:
            result["dup_para"].append(p[:60] + "…")
            break
        seen.add(key)

    # 3. เนื้อหาสั้น
    if len(text) < 300:
        result["short"] = len(text)

    return result


def แก้_เนื้อหาเพี้ยน() -> int:
    """
    Safe Fix Content — 3 phase:
      Phase 1: สแกนทุกบทความ สร้าง report
      Phase 2: แสดงผล แบ่งตามความรุนแรง
      Phase 3: ให้ผู้ใช้เลือกทีละไฟล์หรือ bulk

    แต่ละไฟล์มี 3 action ที่ทำได้:
      instruction + dup_para → ลบ regex (ปลอดภัย มาก)
      short                  → AI เขียนเพิ่ม (ต้องยืนยันแต่ละไฟล์เสมอ)
    """
    log_section("🔬 Safe Fix Content — สแกนก่อน")

    บทความ = สแกน_บทความ()
    รายงาน: list[tuple[Path, dict]] = []

    # ── Phase 1: สแกน ────────────────────────────────────────────────────
    log_info(f"  กำลังสแกน {len(บทความ)} บทความ…")
    for fp in บทความ:
        try:
            info = _scan_content_issues(fp)
            has_issue = (info["instruction"] or
                         info["dup_para"] or
                         info["short"] is not None)
            if has_issue:
                รายงาน.append((fp, info))
        except Exception as e:
            log_err(f"  scan {fp.name}: {e}")

    # ── Phase 2: รายงาน ──────────────────────────────────────────────────
    if not รายงาน:
        log_ok("✅ ไม่พบเนื้อหาเพี้ยน — ทุกบทความปกติดี")
        return 0

    # แบ่งกลุ่ม
    safe_fixes:  list[tuple[Path, dict]] = []  # instruction/dup เท่านั้น → ลบ regex ปลอดภัย
    ai_fixes:    list[tuple[Path, dict]] = []  # short → AI เขียนเพิ่ม อันตราย
    mixed_fixes: list[tuple[Path, dict]] = []  # ทั้งคู่

    for fp, info in รายงาน:
        has_safe = bool(info["instruction"] or info["dup_para"])
        has_ai   = info["short"] is not None
        if has_safe and has_ai:
            mixed_fixes.append((fp, info))
        elif has_safe:
            safe_fixes.append((fp, info))
        else:
            ai_fixes.append((fp, info))

    print()
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  พบปัญหาทั้งหมด {len(รายงาน)} ไฟล์                                    │")
    print("  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  🟢 ปลอดภัย  (ลบ instruction/ซ้ำ) : {len(safe_fixes):3d} ไฟล์             │")
    print(f"  │  🔴 ระวัง    (AI เขียนทับ)        : {len(ai_fixes):3d} ไฟล์             │")
    print(f"  │  🟡 ผสม      (ทั้งสองแบบ)         : {len(mixed_fixes):3d} ไฟล์             │")
    print("  └─────────────────────────────────────────────────────────────┘")
    print()

    # ── แสดง detail ──────────────────────────────────────────────────────
    all_groups = [
        ("🟢 ปลอดภัย — ลบ instruction/ย่อหน้าซ้ำ", safe_fixes),
        ("🔴 ระวัง — เนื้อหาสั้น ต้องให้ AI เขียนเพิ่ม", ai_fixes),
        ("🟡 ผสม — มีทั้งสองปัญหา", mixed_fixes),
    ]

    for group_label, group in all_groups:
        if not group:
            continue
        print(f"  {group_label}")
        for i, (fp, info) in enumerate(group, 1):
            tags = []
            if info["instruction"]:
                tags.append(f"instruction({len(info['instruction'])})")
            if info["dup_para"]:
                tags.append("ย่อหน้าซ้ำ")
            if info["short"] is not None:
                tags.append(f"สั้น {info['short']} ตัว")
            print(f"    [{i:2d}] {fp.name:<35} {', '.join(tags)}")
            print(f"         หัวข้อ: {info['title'][:55]}")
        print()

    # ── Phase 3: เลือกวิธีจัดการ ─────────────────────────────────────────
    print("  ─── ตัวเลือก ───────────────────────────────────────────────")
    print("    1 = แก้เฉพาะ 🟢 ปลอดภัย ทั้งหมดเลย (แนะนำ)")
    print("    2 = ดูทีละไฟล์แล้วเลือกเอง (ทุกกลุ่ม)")
    print("    3 = แก้ทุกไฟล์ทั้งหมด รวม AI เขียนทับ (อันตราย)")
    print("    q = ออก ไม่ทำอะไร")
    print()

    mode = _ask("เลือก", "1/2/3/q")
    if mode == "q":
        log_info("ยกเลิก fix-content")
        return 0

    # ── เริ่มแก้ ─────────────────────────────────────────────────────────
    bk_dir  = _backup_dir()
    แก้แล้ว = 0
    log_info(f"  💾 backup → {bk_dir}")
    print()

    to_process: list[tuple[Path, dict, bool]] = []  # (fp, info, allow_ai)

    if mode == "1":
        # เฉพาะ safe + mixed แต่ทำแค่ส่วน safe ของ mixed
        for fp, info in safe_fixes:
            to_process.append((fp, info, False))
        for fp, info in mixed_fixes:
            to_process.append((fp, info, False))  # allow_ai=False → ข้ามส่วน short

    elif mode == "2":
        # review ทีละไฟล์
        for fp, info in รายงาน:
            print(f"\n  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"  ไฟล์  : {fp.name}")
            print(f"  หัวข้อ: {info['title'][:60]}")
            print(f"  ขนาด  : {info['text_len']} ตัวอักษร")
            if info["instruction"]:
                print(f"  ⚠️  instruction หลุด: {', '.join(info['instruction'][:3])}")
            if info["dup_para"]:
                print(f"  ⚠️  ย่อหน้าซ้ำ: {info['dup_para'][0]}")
            if info["short"] is not None:
                print(f"  ⚠️  เนื้อหาสั้น ({info['short']} ตัว) → AI จะเขียนเพิ่ม")
            print()

            act = _ask("จัดการไฟล์นี้", "y=แก้/v=ดูก่อน/n=ข้าม/q=หยุด")
            if act == "v":
                _preview_file(fp)
                act = _ask("หลังดูแล้ว", "y=แก้/n=ข้าม/q=หยุด")

            if act == "q":
                log_info("  หยุดกลางคัน")
                break
            if act == "n":
                continue

            # ถ้าไฟล์มี short → ถามแยกว่ายอม AI เขียนทับไหม
            allow_ai = False
            if info["short"] is not None:
                ai_ans = _ask(
                    f"  เนื้อหาสั้น {info['short']} ตัว — ให้ AI เขียนเพิ่มด้วยไหม",
                    "y/n"
                )
                allow_ai = (ai_ans == "y")

            to_process.append((fp, info, allow_ai))

    elif mode == "3":
        for fp, info in รายงาน:
            to_process.append((fp, info, True))

    # ── ลงมือแก้จริง ─────────────────────────────────────────────────────
    for fp, info, allow_ai in to_process:
        try:
            _backup_file(fp, bk_dir)
            orig = html = info["html"]  # ใช้ html ที่ scan มาแล้ว
            changed = False

            # ขั้น 1: ลบ instruction
            if info["instruction"]:
                for pat in _AI_LEAKAGE_RE:
                    new_html = re.sub(pat, '', html,
                                      flags=re.IGNORECASE | re.DOTALL)
                    if new_html != html:
                        html = new_html
                        changed = True
                log_ok(f"  🧹 ลบ instruction: {fp.name}")

            # ขั้น 2: ลบย่อหน้าซ้ำ
            if info["dup_para"]:
                seen_p: set = set()

                def _dedup_p(m: re.Match) -> str:
                    txt = m.group(1).strip()
                    key = txt[:100]
                    if len(txt) > 60 and key in seen_p:
                        return ""
                    seen_p.add(key)
                    return m.group(0)

                new_html = re.sub(r'<p[^>]*>(.*?)</p>', _dedup_p,
                                  html, flags=re.DOTALL | re.IGNORECASE)
                if new_html != html:
                    html = new_html
                    changed = True
                log_ok(f"  🔁 ลบย่อหน้าซ้ำ: {fp.name}")

            # ขั้น 3: AI เขียนเพิ่ม (เฉพาะเมื่อ allow_ai=True)
            if allow_ai and info["short"] is not None:
                log_info(f"  ✍️  AI เขียนเพิ่ม ({info['short']} ตัว → เป้า 500+): {fp.name}")
                try:
                    extra = เรียก_ollama(
                        f"เขียนเนื้อหาบทความภาษาไทยเพิ่มเติมเกี่ยวกับ "
                        f"'{info['title']}' ความยาว 3-5 ย่อหน้า "
                        f"ไม่มี HTML tag ไม่มี markdown",
                        num_predict=600
                    )
                    if extra and len(extra.strip()) > 100:
                        extra_html = "\n".join(
                            f"<p>{line.strip()}</p>"
                            for line in extra.strip().split("\n")
                            if line.strip()
                        )
                        html = re.sub(
                            r'(</article>|</main>)',
                            f"\n{extra_html}\n\\1",
                            html, count=1, flags=re.IGNORECASE
                        )
                        changed = True
                        log_ok(f"  เพิ่ม {len(extra)} ตัว")
                    else:
                        log_warn(f"  AI ตอบสั้นเกินไป — ข้ามการเขียนเพิ่ม")
                except Exception as e:
                    log_warn(f"  AI error: {e}")

            if changed and เขียน(fp, html, orig):
                แก้แล้ว += 1

        except Exception as e:
            log_err(f"  fix-content {fp.name}: {e}")

    # ── สรุป ─────────────────────────────────────────────────────────────
    print()
    log_ok(f"✅ fix-content เสร็จ: {แก้แล้ว}/{len(to_process)} ไฟล์")
    log_info(f"  💾 backup อยู่ที่: {bk_dir}")
    log_info(f"  ↩️  ถ้าผิดพลาด: python agent_fix_v6.py --restore {bk_dir.name}")
    return แก้แล้ว


# ══════════════════════════════════════════════════════════════════════════
# ↩️  --restore  (เพิ่มใน main() ของ agent_fix_v6.py)
# ══════════════════════════════════════════════════════════════════════════

def restore_backup(backup_name: str):
    """
    คืนไฟล์จาก backup กลับสู่สถานะก่อนแก้
    ใช้: python agent_fix_v6.py --restore 20250414_153022
    """
    log_section(f"↩️  Restore: {backup_name}")
    bk_dir = BASE_PATH / ".backups" / backup_name
    if not bk_dir.exists():
        # แสดง backup ที่มีอยู่
        bk_root = BASE_PATH / ".backups"
        if bk_root.exists():
            available = sorted(bk_root.iterdir(), reverse=True)
            log_warn(f"ไม่พบ backup '{backup_name}'")
            log_info("  backup ที่มี:")
            for b in available[:10]:
                count = len(list(b.glob("*.html")))
                print(f"    {b.name}  ({count} ไฟล์)")
        else:
            log_warn("ยังไม่มี backup เลย")
        return

    html_files = list(bk_dir.glob("*.html"))
    if not html_files:
        log_warn(f"ไม่มีไฟล์ HTML ใน backup นี้")
        return

    print(f"\n  จะ restore {len(html_files)} ไฟล์:")
    for f in html_files:
        print(f"    {f.name}")

    confirm = _ask("ยืนยัน restore ทั้งหมด", "y/n")
    if confirm != "y":
        log_info("ยกเลิก restore")
        return

    _restore_backup(bk_dir)


# ══════════════════════════════════════════════════════════════════════════
# 📋  วิธีติดตั้งในไฟล์ agent_fix_v6.py
# ══════════════════════════════════════════════════════════════════════════
"""
STEP 1: แทนที่ฟังก์ชัน แก้_duplicate_blocks_hard() (บรรทัด 2234–2249)
        ด้วย safe version จากไฟล์นี้

STEP 2: แทนที่ฟังก์ชัน แก้_เนื้อหาเพี้ยน() (บรรทัด 3186–3290)
        ด้วย safe version จากไฟล์นี้
        และ copy _AI_LEAKAGE_RE, _AI_LEAKAGE_TEXT, _scan_content_issues ด้วย

STEP 3: เพิ่ม helper functions ด้านบน:
        _backup_dir, _backup_file, _restore_backup, _ask, _preview_file

STEP 4: เพิ่มใน main() ของไฟล์หลัก:
        if "--restore" in args:
            backup_name = _get_arg("--restore", "")
            if backup_name:
                restore_backup(backup_name)
            return

STEP 5: เพิ่มใน banner comment ด้านบน:
        python agent_fix_v6.py --restore <timestamp>  → คืนไฟล์จาก backup
"""
