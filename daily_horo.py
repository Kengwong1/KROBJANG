import openai
import datetime

# 🔑 ใส่ API Key ของคุณตรงนี้
openai.api_key = "ใส่ API KEY ของคุณ"

# 🎯 ฟังก์ชันดูดวง
def get_daily_horoscope(name, birthdate):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
    คุณคือหมอดูผู้เชี่ยวชาญด้านโหราศาสตร์ไทยและสากล
    วันนี้คือ {today}
    ผู้ใช้ชื่อ {name} เกิดวันที่ {birthdate}
    กรุณาทำนายดวงรายวันแบบกระชับ มีทั้งด้านความรัก การเงิน สุขภาพ และโชคลาภ
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']

# 🧪 ทดสอบระบบ
if __name__ == "__main__":
    name = input("กรุณากรอกชื่อของคุณ: ")
    birthdate = input("กรุณากรอกวันเกิด (เช่น 1990-05-21): ")
    result = get_daily_horoscope(name, birthdate)
    print("\n🔮 คำทำนายวันนี้:\n")
    print(result)
