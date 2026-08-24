import os

file_path = os.path.join('mt5_backend', 'mt5_gateway.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_endpoint = """
@app.get("/api/news_status")
def api_news_status():
    status_file = "news_status.json"
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"summary_text": "ยังไม่มีข้อมูลข่าวสารล่าสุด", "summary_risk": "รอข้อมูล", "pairs": []}
"""

if "/api/news_status" not in content:
    # insert before @app.post("/api/news_update")
    target = '@app.post("/api/news_update")'
    if target in content:
        content = content.replace(target, new_endpoint + "\n" + target)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched mt5_gateway.py")
else:
    print("Already patched")
