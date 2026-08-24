import requests
import xml.etree.ElementTree as ET

try:
    print("Fetching...")
    r = requests.get("https://nfs.faireconomy.media/ff_calendar_thisweek.xml", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
    print("Status:", r.status_code)
    print("Text preview:", r.text[:200])
    root = ET.fromstring(r.content)
    print("Parsed OK")
except Exception as e:
    print("Error:", e)
