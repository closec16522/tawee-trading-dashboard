import urllib.request
import json
import time

BOT_TOKEN = "8796299419:AAF5eY4Z_bH1kCdj2bQ_g3N0urdwPGEkHfY"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

print("========================================")
print("🔍 กำลังค้นหา Chat ID ของห้องประชุมบอท...")
print("========================================")
print("รบกวนบอสลากบอทเข้ากลุ่ม 'ห้องประชุมบอท'")
print("แล้วพิมพ์ข้อความอะไรก็ได้ในกลุ่ม เช่น 'hello'")
print("รอสักครู่ ระบบกำลังสแกนหา Chat ID...\n")

while True:
    try:
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if data.get("ok") and len(data.get("result", [])) > 0:
                for result in data["result"]:
                    if "message" in result:
                        chat = result["message"]["chat"]
                        chat_id = chat["id"]
                        chat_title = chat.get("title", chat.get("first_name", "Private Chat"))
                        
                        print("✅ เจอแล้วครับบอส!")
                        print(f"ชื่อกลุ่ม/แชท: {chat_title}")
                        print(f"👉 Chat ID: {chat_id}")
                        print("\nให้นำตัวเลข Chat ID นี้ไปใส่ในไฟล์ config.json")
                        print("ตรงบรรทัด: \"agent_telegram_chat_id\": \"ตัวเลขที่ได้\"")
                        print("========================================")
                        exit(0)
    except Exception as e:
        print("Error connecting to Telegram:", e)
        
    time.sleep(3)
