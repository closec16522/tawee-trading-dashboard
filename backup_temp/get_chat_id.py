import requests
import time

TOKEN = "8899582441:AAFvY4Ab23ilqc01BBue5zo18RbmmJAVAAI"

print("=======================================")
print("Telegram Chat ID Finder")
print("=======================================")
print(f"1. Open Telegram and search for @Tawee_Cy_bot (or click t.me/Tawee_Cy_bot)")
print("2. Click 'Start' or send a message like 'Hello' to the bot.")
print("Waiting for your message...\n")

last_update_id = 0

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("ok") and len(data["result"]) > 0:
            for result in data["result"]:
                last_update_id = result["update_id"] + 1
                if "message" in result:
                    chat_id = result["message"]["chat"]["id"]
                    text = result["message"].get("text", "")
                    sender = result["message"]["from"].get("first_name", "User")
                    print(f"✅ Success! Received message from {sender}: '{text}'")
                    print(f"👉 YOUR CHAT ID IS: {chat_id}")
                    print("\nKeep this Chat ID safe. We will use it in the trading bot.")
                    
                    # Send a confirmation message back to the user
                    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ระบบบอทเชื่อมต่อกับ Telegram ของคุณเรียบร้อยแล้ว!"})
                    
                    exit(0)
    except Exception as e:
        print(f"Error: {e}")
        
    time.sleep(3)
