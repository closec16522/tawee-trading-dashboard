// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Notes Skill
// Save / list / search / delete notes in localStorage
// ─────────────────────────────────────────────────────────────
(function () {
  const LS_KEY = 'tawee_notes_v2';

  function getNotes() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch(e) { return []; }
  }
  function saveNotes(notes) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(notes)); } catch(e) {}
  }
  function now() {
    const d = new Date();
    return `${d.getDate()}/${d.getMonth()+1} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
  }

  TAWEE.registerSkill('notes', {
    match: (t) =>
      /บันทึก|โน้ต|จด|note|remind|จำ|รายการ|list.*note|show.*note|ลบโน้ต|ค้นหาโน้ต|โน้ตทั้งหมด|เพิ่มโน้ต|clear.*note/i.test(t),

    handle: async (t, raw) => {
      const notes = getNotes();

      // ── ADD ─────────────────────────────────────────────────
      if (/^(บันทึก|จด|เพิ่ม|add|save|note)\s+/i.test(raw)) {
        const content = raw.replace(/^(บันทึก|จด|เพิ่ม|add|save|note)\s+/i, '').trim();
        if (!content || content.length < 2) return 'จะให้บันทึกอะไรดีคะ? กรุณาระบุเนื้อหาหลังคำสั่งด้วยนะคะ';
        notes.push({ id: Date.now(), text: content, time: now() });
        saveNotes(notes);
        return `✅ บันทึกแล้วค่ะ: "${content}"\n(รวมทั้งหมด ${notes.length} โน้ต)`;
      }

      // ── LIST / SHOW ─────────────────────────────────────────
      if (/ดู|แสดง|list|show|ทั้งหมด|all/i.test(t)) {
        if (!notes.length) return 'ยังไม่มีโน้ตบันทึกไว้เลยค่ะ — ลองพูดว่า "บันทึก [ข้อความ]" เพื่อเพิ่มโน้ต';
        const lines = notes.map((n, i) => `${i+1}. ${n.text}  (${n.time})`).join('\n');
        return `📝 โน้ตทั้งหมด ${notes.length} รายการ:\n${lines}`;
      }

      // ── SEARCH ──────────────────────────────────────────────
      if (/ค้นหา|หา|search|find/i.test(t)) {
        const kw = raw.replace(/ค้นหา|หา|search|find/gi, '').trim();
        if (!kw) return 'กรุณาระบุคำที่ต้องการค้นหาค่ะ';
        const found = notes.filter(n => n.text.toLowerCase().includes(kw.toLowerCase()));
        if (!found.length) return `ไม่พบโน้ตที่มีคำว่า "${kw}" ค่ะ`;
        return `🔍 พบ ${found.length} รายการที่มี "${kw}":\n` + found.map((n,i) => `${i+1}. ${n.text}  (${n.time})`).join('\n');
      }

      // ── DELETE LAST ─────────────────────────────────────────
      if (/ลบ.*ล่าสุด|delete.*last|ลบอัน.*สุดท้าย/i.test(t)) {
        if (!notes.length) return 'ไม่มีโน้ตให้ลบค่ะ';
        const removed = notes.pop();
        saveNotes(notes);
        return `🗑 ลบโน้ตล่าสุดแล้ว: "${removed.text}" — เหลือ ${notes.length} รายการ`;
      }

      // ── CLEAR ALL ───────────────────────────────────────────
      if (/ลบทั้งหมด|clear|ล้าง/i.test(t)) {
        const count = notes.length;
        saveNotes([]);
        return `🗑 ลบโน้ตทั้งหมด ${count} รายการแล้วค่ะ`;
      }

      // ── DEFAULT: show count + help ───────────────────────────
      return notes.length
        ? `มีโน้ต ${notes.length} รายการค่ะ\n• "ดูโน้ต" → แสดงทั้งหมด\n• "บันทึก [ข้อความ]" → เพิ่มโน้ต\n• "ค้นหา [คำ]" → ค้นหาโน้ต\n• "ลบโน้ตล่าสุด" หรือ "ลบทั้งหมด"`
        : 'ยังไม่มีโน้ตค่ะ — ลองพูดว่า "บันทึก [ข้อความ]" เพื่อเริ่มต้นใช้งาน';
    },
  });
})();
