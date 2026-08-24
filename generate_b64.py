import base64

clean_block = '''                   const meetingLog = document.getElementById('ai-meeting-log');
                   if (meetingLog) {
                       function translateCasual(agentId, text) {
                           let t = text.toLowerCase();
                           let r = text;
                           let id = agentId.toLowerCase();
                           if (t.includes("scanning") && t.includes("structure")) {
                               const pair = text.match(/Scanning (.*?) Structure/i);
                               const p = pair ? pair[1] : "กราฟ";
                               r = `เห้ยๆ ขอดูกราฟ ${p} แป๊บนะ ขอส่องโครงสร้างแป๊บ 👀`;
                           } else if (t.includes("waiting for market data")) {
                               r = `รอข้อมูลตลาดแป๊บนึงนะวัยรุ่น... เน็ตช้าหรือตลาดนิ่งเนี่ย 🥱`;
                           } else if (t.includes("bullish")) {
                               const pair = text.match(/\[(.*?)\]/);
                               const p = pair ? pair[1] : "";
                               r = `${p} ทรงนี้กระทิงดุจัดๆ 🚀 ซื้อดิคร้าบบบรอไร!`;
                           } else if (t.includes("bearish")) {
                               const pair = text.match(/\[(.*?)\]/);
                               const p = pair ? pair[1] : "";
                               r = `${p} หมีมาเต็มๆ เตรียมทุบเลยลูกพี่! 🐻📉`;
                           } else if (t.includes("evaluating")) {
                               const pair = text.match(/Evaluating (.*?)\.\.\./i);
                               const p = pair ? pair[1] : "กราฟ";
                               r = `กำลังเพ่ง ${p} แบบละเอียดๆ อยู่ฮะ ขอใช้สมองแป๊บ 🧐`;
                           } else if (t.includes("จุดเข้าเทรดที่น่าสนใจ")) {
                               r = text.replace("จุดเข้าเทรดที่น่าสนใจคือเมื่อพิจารณาจาก", "เจอจุดเข้าสวยๆ ละพวก! ส่องจาก").replace("และ", "บวกกับ") + " เตรียมซิ่งเลยนะ 😎";
                           } else if (t.includes("trade rejected") || t.includes("volatility")) {
                               r = `โอ้ยยย กราฟเหวี่ยงเกิ๊นนน ยกเลิกออเดอร์ก่อน ไม่เสี่ยงดีกว่า 🛑`;
                           } else if (t.includes("calculating risk")) {
                               r = `กำลังดีดลูกคิดคำนวณความเสี่ยงแป๊บนะพี่น้อง 🧮💸`;
                           } else if (t.includes("executing")) {
                               r = `จัดไปชุดใหญ่ไฟกระพริบ! กำลังเคาะขวายิงออเดอร์ปิ้วๆ 🔫💥`;
                           } else if (t.includes("monitoring")) {
                               r = `เฝ้าพอร์ตให้แบบตาไม่กระพริบเลยครับเจ้านาย 👁️👁️`;
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
                       msgDiv.innerHTML = `<strong style="color:${data.color || "#f59e0b"}">${data.agent_id.toUpperCase()}</strong>: ${meetingTxt}`;
                       meetingLog.appendChild(msgDiv);
                       meetingLog.scrollTop = meetingLog.scrollHeight;
                   }\n'''

with open('base64_block.txt', 'w', encoding='utf-8') as f:
    f.write(base64.b64encode(clean_block.encode('utf-8')).decode('utf-8'))