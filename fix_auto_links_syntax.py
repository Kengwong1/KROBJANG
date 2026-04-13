"""
fix_auto_links_syntax.py
แก้ SyntaxError ใน _ใส่_external_links ที่ patch ไปก่อนหน้า
"""
import re
from pathlib import Path

fp = Path("agent_writer.py")
src = fp.read_text(encoding="utf-8")

# แก้บรรทัดที่มี syntax error — f-string ที่ตัดบรรทัดผิด
OLD = """            return (f\'<a href="{url}" target="_blank" rel="noopener noreferrer" \\\'
                    f\'style="color:var(--primary,#1e40af);text-decoration:underline;\\\'
                    f\'text-underline-offset:2px;">{m.group(0)}</a>\')"""

NEW = """            return (
                f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'style="color:var(--primary,#1e40af);text-decoration:underline;'
                f'text-underline-offset:2px;">{m.group(0)}</a>'
            )"""

if OLD in src:
    src = src.replace(OLD, NEW, 1)
    fp.write_text(src, encoding="utf-8")
    print("✅ แก้ syntax error สำเร็จ")
else:
    # fallback: หาด้วย regex
    pattern = re.compile(
        r"return \(f'<a href=.*?</a>'\)",
        re.DOTALL
    )
    new_return = (
        "return (\n"
        "                f'<a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\" '\n"
        "                f'style=\"color:var(--primary,#1e40af);text-decoration:underline;'\n"
        "                f'text-underline-offset:2px;\">{m.group(0)}</a>'\n"
        "            )"
    )
    src2, n = pattern.subn(new_return, src, count=1)
    if n:
        fp.write_text(src2, encoding="utf-8")
        print("✅ แก้ด้วย fallback สำเร็จ")
    else:
        # แก้ตรงๆ บรรทัด 462
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "noopener noreferrer" in line and "\\'" in line:
                # แทนที่ 3 บรรทัดนั้นด้วยโค้ดที่ถูก
                lines[i] = "            return ("
                if i+1 < len(lines): lines[i+1] = "                f'<a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\" '"
                if i+2 < len(lines): lines[i+2] = "                f'style=\"color:var(--primary,#1e40af);text-decoration:underline;text-underline-offset:2px;\">{m.group(0)}</a>'"
                lines.insert(i+3, "            )")
                fp.write_text("\n".join(lines), encoding="utf-8")
                print("✅ แก้แบบ line-by-line สำเร็จ")
                break
        else:
            print("❌ ไม่พบ pattern — แก้มือที่บรรทัด 462 ครับ")
            print("   เปลี่ยนเป็น:")
            print("""            return (
                f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'style="color:var(--primary,#1e40af);text-decoration:underline;'
                f'text-underline-offset:2px;">{m.group(0)}</a>'
            )""")
