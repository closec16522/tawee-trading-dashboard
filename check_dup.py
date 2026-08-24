import re
with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "function getSettingsHTML" in line:
        print(f"getSettingsHTML at line {i+1}")
    if "function initSettingsLogic" in line:
        print(f"initSettingsLogic at line {i+1}")