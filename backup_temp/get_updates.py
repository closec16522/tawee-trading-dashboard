import requests
import json

TOKEN = "8899582441:AAFvY4Ab23ilqc01BBue5zo18RbmmJAVAAI"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
r = requests.get(url)
print(json.dumps(r.json(), indent=2))
