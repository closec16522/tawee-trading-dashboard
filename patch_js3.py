with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

target = """        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "MT5_UPDATE") {"""

replacement = """        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Process signal_history from ANY event that includes it (like MT5_UPDATE or SIGNALS_UPDATE)
            if (data.signal_history) {
                if (window.renderSignalsTable) window.renderSignalsTable(data.signal_history);
                if (window.renderSignalAlerts) window.renderSignalAlerts(data.signal_history);
            }
            
            if (data.type === "MT5_UPDATE") {"""

content = content.replace(target, replacement)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Added signal_history listener to all events")