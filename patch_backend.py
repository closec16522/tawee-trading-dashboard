import re
import os

file_path = os.path.join('mt5_backend', 'agent_orchestrator.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

fallback_logic = """                        if profit > 0:
                            insight = f"วิเคราะห์ (อัตโนมัติ): เทรดทำกำไรได้สำเร็จ (+${profit:.2f}) ระบบประเมินว่าจุดออกเหมาะสมตามแผน"
                        elif profit < 0:
                            insight = f"วิเคราะห์ (อัตโนมัติ): ขาดทุน (-${abs(profit):.2f}) สภาพตลาดอาจมีความผันผวนสูง หรือผิดทาง แนะนำให้คุมความเสี่ยงให้เคร่งครัด"
                        else:
                            insight = "วิเคราะห์ (อัตโนมัติ): ปิดเสมอตัว ไม่มีกำไร/ขาดทุน"
"""

content = content.replace('insight = "ไม่สามารถวิเคราะห์ได้ในขณะนี้"', fallback_logic.strip())

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Backend fallback logic patched.")
