import requests
import json

tokens = [
    "8899582441:AAFvY4Ab23ilqcOlBBue5zo18RbmmJAVAAI",
    "8899582441:AAFvY4Ab23ilqcO1BBue5zo18RbmmJAVAAI",
    "8899582441:AAFvY4Ab23ilqc0lBBue5zo18RbmmJAVAAI"
]

for t in tokens:
    url = f"https://api.telegram.org/bot{t}/getMe"
    r = requests.get(url)
    if r.status_code == 200:
        print(f"VALID TOKEN: {t}")
        print(json.dumps(r.json(), indent=2))
        
        # Now get updates
        print("Getting updates...")
        r_updates = requests.get(f"https://api.telegram.org/bot{t}/getUpdates")
        print(json.dumps(r_updates.json(), indent=2))
        break
    else:
        print(f"Failed: {t}")
