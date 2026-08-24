import urllib.request
import json
import time
import os
import ctypes

BOT_TOKEN = "8796299419:AAF5eY4Z_bH1kCdj2bQ_g3N0urdwPGEkHfY"
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
CONFIG_FILE = "config.json"

print("Waiting for user to send a message in the Bot Meeting Room...")

while True:
    try:
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            if data.get("ok") and len(data.get("result", [])) > 0:
                for result in data["result"]:
                    if "message" in result:
                        chat = result["message"]["chat"]
                        chat_id = str(chat["id"])
                        chat_title = chat.get("title", chat.get("first_name", "Private Chat"))
                        
                        print(f"Found chat: {chat_title} ({chat_id})")
                        
                        # Update config.json
                        if os.path.exists(CONFIG_FILE):
                            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                        else:
                            config = {}
                            
                        config["agent_telegram_chat_id"] = chat_id
                        
                        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=4)
                        
                        print("Updated config.json successfully!")
                        
                        # Show Windows Popup
                        msg = f"เซ็ตอัปสำเร็จแล้วครับบอส!\n\nดึง Chat ID ของกลุ่ม '{chat_title}' ได้เรียบร้อยและบันทึกลง config.json แล้วครับ\n\nบอสสามารถปิดหน้าต่างบอทอันเก่า แล้วรัน start_all_systems.bat ใหม่ได้เลยครับ!"
                        ctypes.windll.user32.MessageBoxW(0, msg, "✅ Tawee Agent Setup Complete", 0x40 | 0x0)
                        
                        exit(0)
    except Exception as e:
        print("Error connecting to Telegram:", e)
        
    time.sleep(3)
