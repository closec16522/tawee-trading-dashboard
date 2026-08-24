import os
import re

path = 'mt5_backend/mt5_gateway.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace everything between the end of api_export_research_data and tf_map
new_content = re.sub(
    r'return FileResponse\(csv_file, media_type=\'text/csv\', filename="research_signals_export\.csv"\).*?tf_map = {',
    '''return FileResponse(csv_file, media_type='text/csv', filename="research_signals_export.csv")

class LongtermRequest(BaseModel):
    ticker: str
    tg_chat_id: str = ""

class JournalUpdate(BaseModel):
    entries: list

@app.post("/api/journal_update")
async def api_journal_update(update: JournalUpdate):
    update_heartbeat()
    global journal_entries
    journal_entries = update.entries
    
    payload = {
        "type": "JOURNAL_UPDATE",
        "entries": update.entries,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.get("/api/signal_history")
def api_get_signal_history():
    import os
    import json
    history_path = os.path.join(os.path.dirname(__file__), "signal_history.json")
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.post("/api/longterm_analyze")
def api_longterm_analyze(req: LongtermRequest):
    req_path = os.path.join(os.path.dirname(__file__), "longterm_request.json")
    try:
        import json
        with open(req_path, "w", encoding="utf-8") as f:
            json.dump({"ticker": req.ticker, "tg_chat_id": req.tg_chat_id}, f)
        return {"ok": True, "msg": f"Requested analysis for {req.ticker}. Please wait a moment."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/api/history")
def api_history(symbol: str = "XAUUSD", timeframe: str = "60", count: int = 500):
    tf_map = {''',
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Fixed successfully using regex!')
