import requests
import json

TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"

try:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data.get("ok") and len(data["result"]) > 0:
        for result in data["result"]:
            if "message" in result:
                chat_id = result["message"]["chat"]["id"]
                text = result["message"].get("text", "")
                sender = result["message"]["from"].get("first_name", "User")
                print(f"✅ Success! Received message from {sender}: '{text}'")
                print(f"👉 YOUR CHAT ID IS: {chat_id}")
                
                # Send a confirmation message back to the user
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ระบบบอทเชื่อมต่อกับ Telegram ของคุณเรียบร้อยแล้ว!"})
                
                exit(0)
        print("No message found in updates.")
    else:
        print("No updates found.")
        print(data)
except Exception as e:
    print(f"Error: {e}")
