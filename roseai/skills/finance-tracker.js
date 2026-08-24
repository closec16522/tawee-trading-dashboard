'use strict';
// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — บันทึกรายรับ-รายจ่าย Skill  |  skills/finance-tracker.js
// พูด/พิมพ์ "บันทึกรายรับรายจ่าย" → ป็อบอัพเลือกรายรับ/รายจ่าย + หมวดหมู่ + จำนวนเงิน + รายการ
// → กด "บันทึก" → ส่งเข้า Google Sheet "TAWEE_Income_Expense_Dashboard" ชีตย่อย "รายการ"
// (Apps Script Web App แบบ "Anyone" access — โครงเดียวกับ skills/todo-timer.js)
// หมวดหมู่ต้องตรงกับ dropdown validation ใน sheet "รายการ" คอลัมน์ C เป๊ะ ไม่งั้น
// ตัวกรองหมวดหมู่ในหน้า Dashboard จะไม่นับแถวนั้น
// ─────────────────────────────────────────────────────────────
(function () {
  // ต้องตรงกับ data validation list ในชีต "รายการ" คอลัมน์ C เป๊ะ (ดูชีต "หมวดหมู่")
  const INCOME_CATEGORIES = ['เงินเดือน', 'รายได้ธุรกิจ', 'การลงทุน', 'โบนัส/คอมมิชชัน', 'ของขวัญ/คืนเงิน', 'รายรับอื่นๆ'];
  const EXPENSE_CATEGORIES = [
    'อาหารและเครื่องดื่ม', 'เดินทาง', 'ที่อยู่อาศัย', 'ค่าน้ำ/ไฟ/อินเทอร์เน็ต', 'สุขภาพ', 'การศึกษา',
    'ครอบครัว', 'ช้อปปิ้ง', 'ความบันเทิง', 'หนี้สิน', 'ภาษี/ค่าธรรมเนียม', 'ออม/ลงทุน', 'รายจ่ายธุรกิจ', 'บริจาค', 'รายจ่ายอื่นๆ',
  ];
  const DEFAULT_INCOME_CATEGORY = 'รายรับอื่นๆ';
  const DEFAULT_EXPENSE_CATEGORY = 'รายจ่ายอื่นๆ';

  function getCfg() {
    try { return JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}'); } catch (e) { return {}; }
  }

  // ── ส่งเข้า Google Sheet ────────────────────────────────────
  // payload ที่ส่งไป: { type: 'รายรับ' | 'รายจ่าย', category: string, amount: number, note: string, user: string }
  // ฝั่ง Apps Script อ่าน data.type / data.category / data.amount / data.note / data.user
  async function sendToSheet(cfg, { type, category, amount, note, user }) {
    if (!cfg.financeWebAppUrl) throw new Error('NO_WEBAPP_URL');
    // mode:'no-cors' จำเป็นเพราะ Apps Script Web App ไม่ส่ง CORS header กลับมาให้ browser fetch() อ่านได้
    await fetch(cfg.financeWebAppUrl, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ type, category, amount, note, user }),
    });
  }

  // ── STYLES ──────────────────────────────────────────────────
  function injectStyles() {
    if (document.getElementById('tawee-finance-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-finance-style';
    s.textContent = `
      @keyframes taweeFinanceIn { from{ opacity:0; transform:translateY(-12px) scale(.96); } to{ opacity:1; transform:translateY(0) scale(1); } }
      .tawee-finance-input { width:100%; padding:12px 14px; border-radius:12px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.12); color:#eef1f6; font-size:14px; font-family:inherit; box-sizing:border-box; }
      .tawee-finance-input:focus { outline:none; border-color:rgba(var(--accentRGB),.55); }
      select.tawee-finance-input { cursor:pointer; }
      select.tawee-finance-input option { background:#12141c; color:#eef1f6; }
      .tawee-finance-btn-primary { padding:12px 18px; border-radius:12px; border:none; background:var(--accent); color:#04130c; font-weight:700; font-size:14px; cursor:pointer; width:100%; }
      .tawee-finance-btn-primary:hover { filter:brightness(1.08); }
      .tawee-finance-toggle { flex:1; padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.04); color:#dfe3ea; font-size:14px; font-weight:600; cursor:pointer; transition:background .15s ease, border-color .15s ease; }
      .tawee-finance-toggle.active-income { background:rgba(74,222,128,.16); border-color:rgba(74,222,128,.55); color:#4ade80; }
      .tawee-finance-toggle.active-expense { background:rgba(239,68,68,.16); border-color:rgba(239,68,68,.55); color:#f87171; }
    `;
    document.head.appendChild(s);
  }

  function root() { return document.getElementById('tawee-root') || document.body; }
  function closeScrim(id) { const el = document.getElementById(id); if (el) el.remove(); }

  function categoryOptionsHtml(list) {
    return list.map((c) => `<option value="${c}">${c}</option>`).join('');
  }

  // ─────────────────────────────────────────────────────────
  // ป็อบอัพ: เลือกรายรับ/รายจ่าย + หมวดหมู่ + จำนวนเงิน + รายการ
  // ─────────────────────────────────────────────────────────
  function showFinanceModal(cfg) {
    injectStyles();
    closeScrim('tawee-finance-scrim');

    let selectedType = 'รายรับ'; // ค่าเริ่มต้น

    const scrim = document.createElement('div');
    scrim.id = 'tawee-finance-scrim';
    scrim.style.cssText = 'position:fixed;inset:0;z-index:70;background:rgba(2,3,8,.62);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;';
    scrim.onclick = (e) => { if (e.target === scrim) closeScrim('tawee-finance-scrim'); };

    const panel = document.createElement('div');
    panel.style.cssText = 'width:min(360px,90vw);border-radius:22px;background:rgba(10,12,20,.95);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(28px) saturate(160%);-webkit-backdrop-filter:blur(28px) saturate(160%);box-shadow:0 34px 90px rgba(0,0,0,.6),0 0 60px rgba(var(--accentRGB),.12);animation:taweeFinanceIn .28s cubic-bezier(.22,1,.36,1);overflow:hidden;';

    panel.innerHTML = `
      <div style="height:2.5px;background:linear-gradient(90deg,var(--accent),var(--accent2));"></div>
      <div style="padding:22px 22px 24px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);">💰 รายรับ-รายจ่าย</span>
          <button id="tawee-finance-close" style="width:28px;height:28px;border-radius:9px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#9aa2b1;font-size:14px;cursor:pointer;">✕</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:14px;">
          <div style="display:flex;gap:10px;">
            <button id="tawee-finance-income" class="tawee-finance-toggle active-income">📈 รายรับ</button>
            <button id="tawee-finance-expense" class="tawee-finance-toggle">📉 รายจ่าย</button>
          </div>
          <div>
            <label style="display:block;font-size:12px;color:rgba(255,255,255,.5);margin-bottom:6px;">หมวดหมู่</label>
            <select id="tawee-finance-category" class="tawee-finance-input">${categoryOptionsHtml(INCOME_CATEGORIES)}</select>
          </div>
          <div>
            <label style="display:block;font-size:12px;color:rgba(255,255,255,.5);margin-bottom:6px;">จำนวนเงิน (บาท)</label>
            <input id="tawee-finance-amount" class="tawee-finance-input" type="number" min="0" step="any" placeholder="เช่น 500" autofocus>
          </div>
          <div>
            <label style="display:block;font-size:12px;color:rgba(255,255,255,.5);margin-bottom:6px;">รายการ</label>
            <input id="tawee-finance-note" class="tawee-finance-input" type="text" placeholder="เช่น ค่าอาหาร / ขายของ">
          </div>
          <div id="tawee-finance-err" style="display:none;color:#ff8a8a;font-size:12.5px;"></div>
          <button id="tawee-finance-submit" class="tawee-finance-btn-primary" style="margin-top:4px;">✅ บันทึก</button>
        </div>
      </div>`;

    scrim.appendChild(panel);
    root().appendChild(scrim);

    const incomeBtn = document.getElementById('tawee-finance-income');
    const expenseBtn = document.getElementById('tawee-finance-expense');
    const categorySelect = document.getElementById('tawee-finance-category');
    incomeBtn.onclick = () => {
      selectedType = 'รายรับ'; incomeBtn.classList.add('active-income'); expenseBtn.classList.remove('active-expense');
      categorySelect.innerHTML = categoryOptionsHtml(INCOME_CATEGORIES);
    };
    expenseBtn.onclick = () => {
      selectedType = 'รายจ่าย'; expenseBtn.classList.add('active-expense'); incomeBtn.classList.remove('active-income');
      categorySelect.innerHTML = categoryOptionsHtml(EXPENSE_CATEGORIES);
    };

    document.getElementById('tawee-finance-close').onclick = () => closeScrim('tawee-finance-scrim');
    document.getElementById('tawee-finance-submit').onclick = async () => {
      const amountRaw = document.getElementById('tawee-finance-amount').value.trim();
      const note = document.getElementById('tawee-finance-note').value.trim();
      const category = categorySelect.value;
      const errEl = document.getElementById('tawee-finance-err');
      const amount = parseFloat(amountRaw);
      if (!amountRaw || isNaN(amount) || amount <= 0) { errEl.textContent = 'กรุณากรอกจำนวนเงินเป็นตัวเลขมากกว่า 0 ค่ะ'; errEl.style.display = ''; return; }

      const btn = document.getElementById('tawee-finance-submit');
      btn.disabled = true; btn.style.opacity = '.6';
      const user = cfg.userName || 'ไม่ระบุ';
      try {
        await sendToSheet(cfg, { type: selectedType, category, amount, note, user });
        closeScrim('tawee-finance-scrim');
        if (typeof TAWEE !== 'undefined') {
          TAWEE.pushMsg('system', `✅ บันทึก${selectedType} ${amount.toLocaleString()} บาท (${category})${note ? ' — ' + note : ''} ลงชีตแล้วค่ะ`);
          TAWEE.render();
        }
      } catch (e) {
        btn.disabled = false; btn.style.opacity = '1';
        errEl.textContent = 'บันทึกไม่สำเร็จ: ' + e.message;
        errEl.style.display = '';
      }
    };
    setTimeout(() => document.getElementById('tawee-finance-amount')?.focus(), 60);
  }

  // ─────────────────────────────────────────────────────────
  // TEXT-COMMAND FLOW — พิมพ์/พูดตรงๆ ไม่ต้องเปิดป็อบอัพก็ได้ (ใช้หมวดหมู่ "อื่นๆ" เป็นค่าเริ่มต้น)
  // เช่น "รายรับ 500 ขายของ" / "รายจ่าย 200 ค่าอาหาร"
  // ─────────────────────────────────────────────────────────
  const RE_OPEN_MODAL = /บันทึกรายรับรายจ่าย|เปิด.*รายรับ.*รายจ่าย|รายรับรายจ่าย/i;
  const RE_INCOME_DIRECT  = /^รายรับ\s+(\d+(?:\.\d+)?)\s*(.*)$/i;
  const RE_EXPENSE_DIRECT = /^รายจ่าย\s+(\d+(?:\.\d+)?)\s*(.*)$/i;

  TAWEE.registerSkill('finance-tracker', {
    match: (t) => RE_OPEN_MODAL.test(t) || RE_INCOME_DIRECT.test(t) || RE_EXPENSE_DIRECT.test(t),

    handle: async (t, raw, cfg) => {
      const user = cfg.userName || 'ไม่ระบุ';

      if (RE_OPEN_MODAL.test(raw)) {
        showFinanceModal(cfg);
        return 'เปิดหน้าต่างบันทึกรายรับ-รายจ่ายให้แล้วค่ะ เลือกหมวดหมู่ กรอกจำนวนเงินแล้วกด "บันทึก" ได้เลย ✨';
      }

      let m = raw.match(RE_INCOME_DIRECT);
      if (m) {
        const amount = parseFloat(m[1]);
        const note = (m[2] || '').trim();
        try {
          await sendToSheet(cfg, { type: 'รายรับ', category: DEFAULT_INCOME_CATEGORY, amount, note, user });
        } catch (e) {
          return `⚠ บันทึกรายรับไม่สำเร็จ: ${e.message}`;
        }
        return `✅ บันทึกรายรับ ${amount.toLocaleString()} บาท${note ? ' (' + note + ')' : ''} ลงชีตแล้วค่ะ (หมวด "${DEFAULT_INCOME_CATEGORY}" — แก้ไขในชีตได้ถ้าอยากระบุหมวดอื่น)`;
      }

      m = raw.match(RE_EXPENSE_DIRECT);
      if (m) {
        const amount = parseFloat(m[1]);
        const note = (m[2] || '').trim();
        try {
          await sendToSheet(cfg, { type: 'รายจ่าย', category: DEFAULT_EXPENSE_CATEGORY, amount, note, user });
        } catch (e) {
          return `⚠ บันทึกรายจ่ายไม่สำเร็จ: ${e.message}`;
        }
        return `✅ บันทึกรายจ่าย ${amount.toLocaleString()} บาท${note ? ' (' + note + ')' : ''} ลงชีตแล้วค่ะ (หมวด "${DEFAULT_EXPENSE_CATEGORY}" — แก้ไขในชีตได้ถ้าอยากระบุหมวดอื่น)`;
      }

      return null;
    },
  });
})();
