import openai
import gradio as gr
import datetime

openai.api_key = "ใส่ API KEY ของคุณตรงนี้"

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

# 🖥️ สร้างหน้าเว็บด้วย Gradio
demo = gr.Interface(
    fn=get_daily_horoscope,
    inputs=[
        gr.Textbox(label="ชื่อของคุณ"),
        gr.Textbox(label="วันเกิด (เช่น 1990-05-21)")
    ],
    outputs="text",
    title="🔮 ดูดวงรายวันกับครบจัง",
    description="กรอกชื่อและวันเกิดของคุณเพื่อรับคำทำนายรายวัน"
)

demo.launch()
