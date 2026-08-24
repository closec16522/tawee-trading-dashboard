import base64

with open('base64_block.txt', 'r', encoding='utf-8') as f:
    clean_block_b64 = f.read().strip()

clean_block = base64.b64decode(clean_block_b64).decode('utf-8')

with open('index.html', 'rb') as f:
    lines = f.readlines()

target_start_idx = -1
target_end_idx = -1

for i, line in enumerate(lines):
    if b"const meetingLog = document.getElementById('ai-meeting-log');" in line and 8500 < i < 8800:
        target_start_idx = i
        for j in range(target_start_idx, len(lines)):
            if b'meetingLog.scrollTop = meetingLog.scrollHeight;' in lines[j]:
                target_end_idx = j + 1
                while b'}' not in lines[target_end_idx]:
                    target_end_idx += 1
                target_end_idx += 1
                break
        break

if target_start_idx != -1 and target_end_idx != -1:
    final_lines = lines[:target_start_idx] + [clean_block.encode('utf-8')] + lines[target_end_idx:]
    with open('index.html', 'wb') as f:
        f.writelines(final_lines)
    print("Patched completely!")
else:
    print(f"Target not found: {target_start_idx}")