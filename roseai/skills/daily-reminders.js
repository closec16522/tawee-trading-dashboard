// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Daily LINE Reminders  |  skills/daily-reminders.js
// ควบคุมเปิด/ปิด + แก้เวลา/ข้อความได้จากหน้าตั้งค่า (tawee-reminders-list)
// และจากแผงลอยบนหน้าจอหลักโดยตรง (เพิ่ม/ลบ/เปิดปิดได้ทันทีไม่ต้องเข้าตั้งค่า)
// หมายเหตุ: การแจ้งเตือนรายวันหลัก (09:00/12:00/13:00/17:00) ทำงานผ่าน
// Cron Triggers บน tawee-proxy Worker แล้ว (ทำงาน 24 ชม. ไม่ต้องเปิดแท็บค้าง)
// ไฟล์นี้ยังมีไว้เผื่อผู้ใช้อยากเพิ่ม/แก้ reminder เองแบบ ad-hoc ระหว่างเปิดแท็บอยู่
// ─────────────────────────────────────────────────────────────
(function () {
  'use strict';

  // URL/secret ของ Worker ไม่ฝังตายตัว — อ่านจากค่าที่ผู้ใช้กรอกไว้ในหน้าตั้งค่า (tawee_cfg_v3.proxyUrl/proxySecret)
  function getProxyConfig() {
    try {
      const cfg = JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}');
      return { url: cfg.proxyUrl || '', secret: cfg.proxySecret || '' };
    } catch (e) { return { url: '', secret: '' }; }
  }
  const LS_KEY         = 'tawee_daily_reminders';
  const LS_ENABLED_KEY = 'tawee_daily_reminders_enabled';
  const CHECK_EVERY_MS = 20 * 1000;

  const DEFAULTS = [
    { time: '09:00', message: 'ประธานโยคะ ☀️ ถึงเวลาเข้างานแล้วนะคะ ขอให้วันนี้เป็นวันที่ดีและราบรื่นค่ะ สู้ๆ นะคะ!' },
    { time: '12:00', message: 'ประธานโยคะ 🍽️ ถึงเวลาพักเที่ยงแล้วนะคะ ทำงานมาเก่งมากช่วงเช้า พักผ่อน ทานข้าวให้อร่อยนะคะ' },
    { time: '13:00', message: 'ประธานโยคะ 💪 ถึงเวลาทำงานต่อแล้วนะคะ ช่วงบ่ายนี้ลุยกันต่อเลยค่ะ เป็นกำลังใจให้นะคะ' },
    { time: '17:00', message: 'เลิกงานแล้วนะคะ 🎉 วันนี้ประธานโยสุดยอดมากค่ะ เหนื่อยมาทั้งวัน พักผ่อนเยอะๆ นะคะ พรุ่งนี้สู้ต่อกันใหม่ค่ะ' },
  ];

  let idCounter = 0;
  let tickId = null;

  function load() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return null;
      const list = JSON.parse(raw);
      idCounter = list.reduce((m, r) => Math.max(m, r.id), 0);
      return list;
    } catch (e) { return null; }
  }

  function save(list) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(list)); } catch (e) {}
    renderList();
    renderWidget();
  }

  let reminders = load();
  if (!reminders) {
    reminders = DEFAULTS.map((d) => ({ id: ++idCounter, time: d.time, message: d.message, enabled: true, lastFiredDate: null }));
    save(reminders);
  }

  function isEnabled() {
    try { return localStorage.getItem(LS_ENABLED_KEY) !== '0'; } catch (e) { return true; } // เปิดเป็นค่าเริ่มต้น
  }
  function setEnabled(v) {
    try { localStorage.setItem(LS_ENABLED_KEY, v ? '1' : '0'); } catch (e) {}
  }

  async function sendLine(message) {
    const { url, secret } = getProxyConfig();
    if (!url || !secret) throw new Error('ยังไม่ได้ตั้งค่า Worker URL/secret ในหน้าตั้งค่า');
    return fetch(`${url}/line-push`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-tawee-secret': secret },
      body: JSON.stringify({ message }),
    });
  }

  async function checkTick() {
    if (!isEnabled()) return;
    const now = new Date();
    const nowMinutes = now.getHours() * 60 + now.getMinutes();
    const todayStr = now.toDateString();
    let changed = false;
    for (const r of reminders) {
      if (!r.enabled) continue;
      if (r.lastFiredDate === todayStr) continue;
      const [rh, rm] = r.time.split(':').map(Number);
      // เช็คแบบ "ถึงเวลาหรือเลยมาแล้ว" แทนการเทียบเวลาตรงเป๊ะ เพราะถ้าแท็บถูกเบราว์เซอร์
      // หน่วงไทม์เมอร์ตอนอยู่ background (พบบ่อยเวลาสลับไปทำงานอื่น) checkTick อาจไม่ได้รันตรง
      // นาทีนั้นพอดี ถ้าเทียบตรงเป๊ะจะพลาดแจ้งเตือนไปทั้งวัน — วิธีนี้ยิงทันทีที่รอบถัดไปมาถึงแทน
      if (nowMinutes >= rh * 60 + rm) {
        r.lastFiredDate = todayStr;
        changed = true;
        try { await sendLine(r.message); } catch (e) { console.error('[daily-reminders] ส่งไม่สำเร็จ:', e.message); }
      }
    }
    if (changed) save(reminders);
  }

  function startChecker() {
    if (tickId) return;
    tickId = setInterval(checkTick, CHECK_EVERY_MS);
    checkTick();
  }
  function stopChecker() {
    if (tickId) { clearInterval(tickId); tickId = null; }
  }

  function escapeAttr(s) {
    return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ── รายการแบบละเอียด ในหน้าตั้งค่า (เดิม) ────────────────
  function renderList() {
    const el = document.getElementById('tawee-reminders-list');
    if (!el) return;

    const rowsHtml = reminders.map((r) => `
      <div style="display:flex;align-items:center;gap:7px;padding:9px 10px;border-radius:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);margin-bottom:8px;">
        <input type="checkbox" ${r.enabled ? 'checked' : ''} onchange="TAWEE.dailyReminders.toggle(${r.id})" style="flex-shrink:0;width:16px;height:16px;cursor:pointer;">
        <input type="time" value="${escapeAttr(r.time)}" onchange="TAWEE.dailyReminders.updateTime(${r.id},this.value)" style="flex-shrink:0;width:92px;padding:7px 8px;border-radius:8px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);color:#eef1f6;font-size:12px;font-family:'JetBrains Mono',monospace;">
        <input type="text" value="${escapeAttr(r.message)}" onchange="TAWEE.dailyReminders.updateMessage(${r.id},this.value)" style="flex:1;min-width:0;padding:7px 9px;border-radius:8px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);color:#eef1f6;font-size:11.5px;">
        <button onclick="TAWEE.dailyReminders.remove(${r.id})" style="flex-shrink:0;width:24px;height:24px;border-radius:7px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#c2c8d4;font-size:12px;cursor:pointer;">✕</button>
      </div>`).join('');

    el.innerHTML = rowsHtml + `
      <button onclick="TAWEE.dailyReminders.add()" style="width:100%;padding:9px;border-radius:10px;border:1px dashed rgba(255,255,255,.18);background:transparent;color:rgba(255,255,255,.5);font-size:12px;cursor:pointer;margin-top:2px;">+ เพิ่มการแจ้งเตือน</button>`;

    const tog = document.getElementById('tawee-reminders-toggle');
    if (tog) {
      const on = isEnabled();
      const trk = tog.querySelector('span:last-child'); if (trk) trk.style.background = on ? 'var(--accent)' : 'rgba(255,255,255,.18)';
      const knob = tog.querySelector('.knob'); if (knob) knob.style.left = on ? '21px' : '3px';
    }
  }

  // ── เนื้อหาส่วน "แจ้งเตือน" ในแผงฮับรวม (skills/hub-panel.js) ──
  function rowHtmlWidget(r) {
    const on = r.enabled;
    return (
      '<div class="tawee-reminder-row" style="display:flex;align-items:center;gap:8px;padding:7px 8px 7px 10px;border-radius:14px;background:rgba(6,8,14,.84);border:1px solid ' + (on ? 'rgba(var(--accentRGB),.3)' : 'rgba(255,255,255,.1)') + ';backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);box-shadow:0 8px 22px rgba(0,0,0,.45);opacity:' + (on ? '1' : '.5') + ';">' +
        '<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;font-weight:700;color:' + (on ? 'var(--accent)' : 'rgba(255,255,255,.5)') + ';flex-shrink:0;">' + escapeHtml(r.time) + '</span>' +
        '<span style="font-size:11px;color:rgba(255,255,255,.7);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0;">' + escapeHtml(r.message) + '</span>' +
        '<button class="tawee-reminder-toggle-mini" onclick="TAWEE.dailyReminders.toggle(' + r.id + ')" title="เปิด/ปิด" style="flex-shrink:0;width:30px;height:17px;border-radius:9px;border:none;position:relative;cursor:pointer;background:' + (on ? 'var(--accent)' : 'rgba(255,255,255,.18)') + ';padding:0;">' +
          '<span class="knob-mini" style="position:absolute;top:2px;left:' + (on ? '15px' : '2px') + ';width:13px;height:13px;border-radius:50%;background:#fff;"></span>' +
        '</button>' +
        '<button onclick="TAWEE.dailyReminders.remove(' + r.id + ')" title="ลบ" style="flex-shrink:0;width:18px;height:18px;border-radius:50%;border:none;background:transparent;color:rgba(255,255,255,.32);cursor:pointer;font-size:11px;">✕</button>' +
      '</div>'
    );
  }

  // เรียกโดย TAWEE.hub (hub-panel.js) เพื่อวาดเนื้อหาลงในกล่องที่ฮับเตรียมไว้
  function renderInto(container) {
    if (!container) return;
    container.innerHTML = reminders.map(rowHtmlWidget).join('') +
      '<button class="tawee-reminder-add-btn" onclick="TAWEE.dailyReminders.add()" style="width:100%;padding:8px;border-radius:12px;border:1px dashed rgba(255,255,255,.22);background:rgba(255,255,255,.03);color:rgba(255,255,255,.5);font-size:11.5px;cursor:pointer;transition:all .15s;">+ เพิ่มการแจ้งเตือน</button>';
  }

  // แจ้งฮับให้วาดใหม่ทุกครั้งที่ข้อมูลเปลี่ยน (ฮับจะเรียก renderInto เองถ้าแผงเปิดอยู่)
  function renderWidget() {
    if (typeof TAWEE !== 'undefined' && TAWEE.hub) TAWEE.hub.refresh();
  }

  TAWEE.dailyReminders = {
    toggleEnabled() { setEnabled(!isEnabled()); if (isEnabled()) startChecker(); else stopChecker(); renderList(); renderWidget(); },
    isEnabled,
    getAll: () => reminders.slice(),
    add() {
      reminders.push({ id: ++idCounter, time: '09:00', message: 'ข้อความแจ้งเตือนใหม่', enabled: true, lastFiredDate: null });
      save(reminders);
    },
    remove(id) {
      reminders = reminders.filter((r) => r.id !== id);
      save(reminders);
    },
    toggle(id) {
      const r = reminders.find((x) => x.id === id); if (!r) return;
      r.enabled = !r.enabled; save(reminders);
    },
    updateTime(id, val) {
      const r = reminders.find((x) => x.id === id); if (!r) return;
      r.time = val; r.lastFiredDate = null; save(reminders);
    },
    updateMessage(id, val) {
      const r = reminders.find((x) => x.id === id); if (!r) return;
      r.message = val; save(reminders);
    },
    renderList,
    renderWidget,
    renderInto,
  };

  if (isEnabled()) startChecker();
  document.addEventListener('DOMContentLoaded', () => { renderList(); renderWidget(); });
  if (document.readyState !== 'loading') { renderList(); renderWidget(); }
})();
