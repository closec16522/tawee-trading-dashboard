import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_code = """            if (data.signal_history) {
                if (window.renderSignalsTable) window.renderSignalsTable(data.signal_history);"""

new_code = """            if (data.signal_history) {
                window.signalsHistory = data.signal_history;
                if (window.renderSignalsTable) window.renderSignalsTable(data.signal_history);"""

content = content.replace(old_code, new_code)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed signalsHistory bug.")
