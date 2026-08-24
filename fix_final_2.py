with open('index.html', 'rb') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if b'eqGrowthEl.innerText' in line and b'% ?????' in line:
        fixed = '                     eqGrowthEl.innerText = (data.account.equity_growth_30d >= 0 ? "+" : "") + data.account.equity_growth_30d.toFixed(2) + "% พอร์ต";\n'.encode('utf-8')
        new_lines.append(fixed)
    else:
        new_lines.append(line)

lines = new_lines

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
    clean_block = '''                   const meetingLog = document.getElementById('ai-meeting-log');
                   if (meetingLog) {
                       function translateCasual(agentId, text) {
                           let t = text.toLowerCase();
                           let r = text;
                           let id = agentId.toLowerCase();
                           if (t.includes("scanning") && t.includes("structure")) {
                               const pair = text.match(/Scanning (.*?) Structure/i);
                               const p = pair ? pair[1] : "กราฟ";
                               r = \เห้ยๆ ขอดูกราฟ \ แป๊บนะ ขอส่องโครงสร้างแป๊บ 👀\;
                           } else if (t.includes("waiting for market data")) {
                               r = \รอข้อมูลตลาดแป๊บนึงนะวัยรุ่น... เน็ตช้าหรือตลาดนิ่งเนี่ย 🥱\;
                           } else if (t.includes("bullish")) {
                               const pair = text.match(/\[(.*?)\]/);
                               const p = pair ? pair[1] : "";
                               r = \\ ทรงนี้กระทิงดุจัดๆ 🚀 ซื้อดิคร้าบบบรอไร!\;
                           } else if (t.includes("bearish")) {
                               const pair = text.match(/\[(.*?)\]/);
                               const p = pair ? pair[1] : "";
                               r = \\ หมีมาเต็มๆ เตรียมทุบเลยลูกพี่! 🐻📉\;
                           } else if (t.includes("evaluating")) {
                               const pair = text.match(/Evaluating (.*?)\\.\\.\\./i);
                               const p = pair ? pair[1] : "กราฟ";
                               r = \กำลังเพ่ง \ แบบละเอียดๆ อยู่ฮะ ขอใช้สมองแป๊บ 🧐\;
                           } else if (t.includes("จุดเข้าเทรดที่น่าสนใจ")) {
                               r = text.replace("จุดเข้าเทรดที่น่าสนใจคือเมื่อพิจารณาจาก", "เจอจุดเข้าสวยๆ ละพวก! ส่องจาก").replace("และ", "บวกกับ") + " เตรียมซิ่งเลยนะ 😎";
                           } else if (t.includes("trade rejected") || t.includes("volatility")) {
                               r = \โอ้ยยย กราฟเหวี่ยงเกิ๊นนน ยกเลิกออเดอร์ก่อน ไม่เสี่ยงดีกว่า 🛑\;
                           } else if (t.includes("calculating risk")) {
                               r = \กำลังดีดลูกคิดคำนวณความเสี่ยงแป๊บนะพี่น้อง 🧮💸\;
                           } else if (t.includes("executing")) {
                               r = \จัดไปชุดใหญ่ไฟกระพริบ! กำลังเคาะขวายิงออเดอร์ปิ้วๆ 🔫💥\;
                           } else if (t.includes("monitoring")) {
                               r = \เฝ้าพอร์ตให้แบบตาไม่กระพริบเลยครับเจ้านาย 👁️👁️\;
                           } else if (t.includes("ราคาจะถอยไปที่โซน")) {
                               r = text.replace("ราคาจะถอยไปที่โซน", "ระวังนะ ราคามันน่าจะย่อไปเทสแถวๆ โซน").replace("และสามารถเห็นการปิด", "แล้วถ้าปิดแบบ") + " ลองจับตาดูดีๆ วัยรุ่น! 🤓";
                           } else if (t.includes("ใกล้ๆ กับจุดนั้น")) {
                               r = text.replace("ใกล้ๆ กับจุดนั้น", "แถวๆ นั้นแหละ");
                           } else {
                               if (id === 'market_analyst') r = text + ' ว่าไงวัยรุ่น? 🕵️‍♂️';
                               else if (id === 'smc_strategist') r = text + ' ทรงนี้จัดมั้ยเซียน? 🧠';
                               else if (id === 'risk_manager') r = text + ' ใจร่มๆ ไว้ก่อนนะ 🛡️';
                               else if (id === 'trade_executor') r = text + ' พร้อมลุยเสมอ! ⚡';
                               else r = text;
                           }
                           return r;
                       }
                       
                       let meetingTxt = translateCasual(data.agent_id, txt);

                       const msgDiv = document.createElement('div');
                       msgDiv.className = 'ai-msg';
                       msgDiv.style.borderLeftColor = data.color || "#f59e0b";
                       msgDiv.innerHTML = \<strong style="color:\\">\</strong>: \\;
                       meetingLog.appendChild(msgDiv);
                       meetingLog.scrollTop = meetingLog.scrollHeight;
                   }\n'''.encode('utf-8')
    
    final_lines = lines[:target_start_idx] + [clean_block] + lines[target_end_idx:]
    with open('index.html', 'wb') as f:
        f.writelines(final_lines)
    print("Patched completely!")
else:
    print(f"Target not found: {target_start_idx}")