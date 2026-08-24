with open('index.html', 'rb') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if b'const eqGrowthEl = document.getElementById("kpi-equity-growth");' in line:
        pass
    if b"const meetingLog = document.getElementById('ai-meeting-log');" in line and 8100 < i < 8300:
        start_idx = i
        for j in range(start_idx, len(lines)):
            if b'eqGrowthEl.innerText =' in lines[j]:
                # find the closing bracket before eqGrowthEl
                end_idx = j - 1
                while b'}' not in lines[end_idx]:
                    end_idx -= 1
                end_idx += 1 # keep the closing brace? No, the corrupted block ends with } but eqGrowthEl belongs to the outer block
                # Wait, looking at the code:
                # const meetingLog = ...
                # if (meetingLog) { ... }
                # eqGrowthEl.innerText = ...
                # So we want to delete from start_idx to the line before eqGrowthEl.innerText
                end_idx = j
                break
        break

if start_idx != -1 and end_idx != -1:
    print(f"Found bad block at {start_idx} to {end_idx}")
    new_lines = lines[:start_idx] + lines[end_idx:]
    with open('index.html', 'wb') as f:
        f.writelines(new_lines)
    print("Deleted successfully.")
else:
    print("Not found.")

