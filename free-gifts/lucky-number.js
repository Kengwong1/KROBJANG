// lucky-number.js
function calculateLuckyNumber() {
  const name = document.getElementById('nameInput').value.trim();
  if (!name) {
    alert("กรุณาใส่ชื่อ");
    return;
  }

  // แปลงชื่อเป็นตัวเลขตามหลักเลขศาสตร์ (ตัวอย่าง: A=1, B=2, ..., Z=26)
  let sum = 0;
  for (let i = 0; i < name.length; i++) {
    const charCode = name.charCodeAt(i);
    if (charCode >= 65 && charCode <= 90) { // A-Z
      sum += charCode - 64;
    } else if (charCode >= 97 && charCode <= 122) { // a-z
      sum += charCode - 96;
    }
  }

  // ลดเหลือเลขหลักเดียว
  while (sum > 9) {
    let tempSum = 0;
    while (sum > 0) {
      tempSum += sum % 10;
      sum = Math.floor(sum / 10);
    }
    sum = tempSum;
  }

  // แสดงผล
  const resultDiv = document.getElementById('luckyResult');
  resultDiv.innerHTML = `
    <h3>ผลลัพธ์: ชื่อ "${name}" มีเลขมงคลคือ <span style="color:#d4af37; font-size:1.5rem;">${sum}</span></h3>
    <p>ความหมาย: เลข ${sum} หมายถึง <strong>${getMeaning(sum)}</strong></p>
    <p>เคล็ดลับ: ใช้เลข ${sum} ในการเลือกเบอร์โทร, บัญชีธนาคาร, หรือวันสำคัญ</p>
  `;
}

function getMeaning(number) {
  const meanings = {
    1: "ผู้นำ, ความเป็นอิสระ, ความมั่นใจ",
    2: "ความสมดุล, ความสัมพันธ์, ความอ่อนโยน",
    3: "ความคิดสร้างสรรค์, ความสนุกสนาน, การสื่อสาร",
    4: "ความมั่นคง, ความประณีต, ความปลอดภัย",
    5: "ความเปลี่ยนแปลง, ความอิสระ, ความตื่นเต้น",
    6: "ความรัก, ความรับผิดชอบ, ความสมดุลในครอบครัว",
    7: "ความลึกลับ, ความรู้, ความสันโดษ",
    8: "ความมั่งคั่ง, อำนาจ, ความสมดุลระหว่างวัตถุและจิตวิญญาณ",
    9: "ความเมตตา, ความสมบูรณ์, การจบสิ้นเพื่อเริ่มใหม่"
  };
  return meanings[number] || "พลังแห่งการเริ่มต้นใหม่";
}