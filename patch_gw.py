import re

with open('mt5_backend/mt5_gateway.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add JournalUpdate model
model_str = """class LongtermRequest(BaseModel):
    ticker: str
    tg_chat_id: str = ""
"""
new_model_str = """class LongtermRequest(BaseModel):
    ticker: str
    tg_chat_id: str = ""

class JournalUpdate(BaseModel):
    entries: list
"""
content = content.replace(model_str, new_model_str)

# Add global journal_entries
global_str = """recent_activity = []
signal_history = []
active_connections: List[WebSocket] = []"""
new_global_str = """recent_activity = []
signal_history = []
journal_entries = []
active_connections: List[WebSocket] = []"""
content = content.replace(global_str, new_global_str)

# Inject into payload
payload_str = """                "recent_activity": recent_activity,
                "signal_history": signal_history,
                "recent_trades": recent_trades
            }"""
new_payload_str = """                "recent_activity": recent_activity,
                "signal_history": signal_history,
                "recent_trades": recent_trades,
                "journal_entries": journal_entries
            }"""
content = content.replace(payload_str, new_payload_str)

# Add endpoint
endpoint_str = """@app.post("/api/longterm_analyze")"""
new_endpoint_str = """@app.post("/api/journal_update")
async def api_journal_update(update: JournalUpdate):
    update_heartbeat()
    global journal_entries
    journal_entries = update.entries
    
    payload = {
        "type": "JOURNAL_UPDATE",
        "entries": update.entries,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    await broadcast_payload(payload)
    return {"ok": True}

@app.post("/api/longterm_analyze")"""
content = content.replace(endpoint_str, new_endpoint_str)

# We also need to save/load journal history if we want persistence across gateway restarts.
# But agent_orchestrator maintains journal.json, so it will push it anyway.

with open('mt5_backend/mt5_gateway.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("mt5_gateway.py patched")
