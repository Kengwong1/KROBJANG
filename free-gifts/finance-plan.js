// finance-plan.js
function planFinance() {
  const income = parseFloat(document.getElementById('incomeInput').value) || 0;
  const expense = parseFloat(document.getElementById('expenseInput').value) || 0;
  const goal = parseFloat(document.getElementById('goalInput').value) || 0;

  if (income === 0) {
    alert("กรุณาใส่รายได้");
    return;
  }

  const savings = income - expense;
  const monthsToGoal = goal > 0 ? Math.ceil(goal / savings) : 0;

  let result = `<h3>📊 แผนการเงินของคุณ</h3>
                <p><strong>รายได้:</strong> ${income.toLocaleString()} บาท</p>
                <p><strong>รายจ่าย:</strong> ${expense.toLocaleString()} บาท</p>
                <p><strong>ออมต่อเดือน:</strong> ${savings.toLocaleString()} บาท</p>`;

  if (goal > 0) {
    result += `<p><strong>เป้าหมาย:</strong> ${goal.toLocaleString()} บาท</p>
               <p><strong>เวลาที่ต้องใช้:</strong> ${monthsToGoal} เดือน</p>`;
  }

  document.getElementById('financeResult').innerHTML = result;
}