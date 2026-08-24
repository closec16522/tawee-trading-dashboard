import os
import re

KEY_TO_REMOVE = ""
REPLACEMENT = ""

cleaned_files = []

for root, dirs, files in os.walk("."):
    # Skip .git directory and mingit directory
    if ".git" in root or "mingit" in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if KEY_TO_REMOVE in content:
                content = content.replace(KEY_TO_REMOVE, REPLACEMENT)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                cleaned_files.append(filepath)
        except Exception as e:
            pass

print(f"Cleaned key from {len(cleaned_files)} files: {cleaned_files}")
