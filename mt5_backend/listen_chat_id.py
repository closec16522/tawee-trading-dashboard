import requests
import time

TOKEN = "8899582441:AAFVy4Ab23ilqcO1BBue5zo18RbmmJAVAAI"

print("Listening for messages...")
last_update_id = 0

while True:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id}"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if data.get("ok") and data["result"]:
            for res in data["result"]:
                last_update_id = res["update_id"] + 1
                if "message" in res:
                    chat_id = res["message"]["chat"]["id"]
                    text = res["message"].get("text", "")
                    print(f"✅ RECEIVED: '{text}' from Chat ID: {chat_id}")
                    
                    # Send confirmation
                    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                    requests.post(send_url, json={"chat_id": chat_id, "text": "✅ ระบบบอทจับ Chat ID ของคุณได้แล้วครับ!"})
                    
                    # Save to a file so we know it
                    with open("chat_id.txt", "w") as f:
                        f.write(str(chat_id))
                    
                    print("Done. Exiting.")
                    exit(0)
    except Exception as e:
        print(f"Error: {e}")
        
    time.sleep(2)
