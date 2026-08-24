import json
import os

journal_path = os.path.join('mt5_backend', 'journal.json')

if os.path.exists(journal_path):
    with open(journal_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
        
    for entry in entries:
        if entry.get('insight') == "ไม่สามารถวิเคราะห์ได้ในขณะนี้":
            profit = entry.get('profit', 0)
            exit_price = entry.get('exit', 0)
            if profit > 0:
                entry['insight'] = f"วิเคราะห์ (อัตโนมัติ): เทรดทำกำไรได้สำเร็จ (+${profit:.2f}) ระบบประเมินว่าจุดออกเหมาะสมตามแผน"
            elif profit < 0:
                entry['insight'] = f"วิเคราะห์ (อัตโนมัติ): ขาดทุน (-${abs(profit):.2f}) สภาพตลาดอาจมีความผันผวนสูง หรือผิดทาง แนะนำให้คุมความเสี่ยงให้เคร่งครัด"
            else:
                entry['insight'] = "ปิดเสมอตัว ไม่มีกำไร/ขาดทุน"
                
    with open(journal_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=4)
    print("Fixed existing journal entries.")
else:
    print("No journal.json found.")
