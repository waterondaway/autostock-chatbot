from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, warnings, datetime
from dotenv import load_dotenv
warnings.filterwarnings("ignore")

load_dotenv()

app = Flask(__name__)

user_ids = [uid.strip() for uid in os.getenv('LINE_USER_IDS').split(',')]
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature. Please check your channel access token/channel secret.', 400

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('Message From: ', event.source.user_id)

# Example JSON data to send to the /alert-pickup-part and /alert-add-part endpoint
# {
#     'employee': 'ชื่อพนักงาน',
#     'stock': {
#         'ชื่ออะไหล่': จำนวนที่เบิก,
#         'ชื่ออะไหล่': จำนวนที่เบิก,
#         'ชื่ออะไหล่': จำนวนที่เบิก,
#     }
# }

@app.route("/alert-pickup-part", methods=['POST'])
def alert_pickup():
    data = request.get_json()
    if not data or 'employee' not in data or 'stock' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    employee = data['employee']
    stock = data['stock']
    text = f'💬 เรียนแจ้งมีการดำเนินการเบิกอะไหล่ออกจากคลัง 🔴 รายละเอียดดังนี้:\n\n📦 รายการเบิกดังนี้:'
    for item_name, quantity in stock.items():
        text += f'\n- {item_name} เป็นจำนวน {quantity} ชิ้น'
    text += f'\n\n📅 เวลา: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nรับผิดชอบโดย: {employee}'
    for user_id in user_ids:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    
    return jsonify({'status': 'success'}), 200

@app.route("/alert-add-part", methods=['POST'])
def alert_add():
    data = request.get_json()
    if not data or 'employee' not in data or 'stock' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    employee = data['employee']
    stock = data['stock']
    text = f'💬 เรียนแจ้งมีการดำเนินการเพิ่มอะไหล่เข้าคลัง 🟢 รายละเอียดดังนี้:\n\n📦 รายการเพิ่มดังนี้:'
    for item_name, quantity in stock.items():
        text += f'\n- {item_name} เป็นจำนวน {quantity} ชิ้น'
    text += f'\n\n📅 เวลา: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nปฏิบัติงานโดย: {employee}'
    for user_id in user_ids:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    
    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)

