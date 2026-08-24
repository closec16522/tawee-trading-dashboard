'use strict';
// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — To-Do List + Timer Skill  (v2 — visual popup flow)
// พูด "ทูดูลิส" → ป็อบอัพกรอกชื่องาน + เวลา → กด "เริ่มงาน" → นับถอยหลัง
// → หมดเวลาป็อบอัพถาม "สำเร็จไหม" → บันทึกเข้า Google Sheet อัตโนมัติ
// ไม่ต้องล็อกอิน Google เลย (ใช้ Apps Script Web App แบบ "Anyone" access)
// ─────────────────────────────────────────────────────────────
(function () {
  const LS_ACTIVE = 'tawee_todo_active_v1';   // { task, startedAt }               — text-flow (เริ่มงาน/จบงาน)
  const LS_COUNTDOWN = 'tawee_todo_cd_v1';    // { task, minutes, endAt }          — visual popup flow
  let tickInterval = null;

  // ── STORAGE ────────────────────────────────────────────────
  function getActive() {
    try { return JSON.parse(localStorage.getItem(LS_ACTIVE) || 'null'); } catch (e) { return null; }
  }
  function setActive(v) {
    try { v ? localStorage.setItem(LS_ACTIVE, JSON.stringify(v)) : localStorage.removeItem(LS_ACTIVE); } catch (e) {}
  }
  function getCountdown() {
    try { return JSON.parse(localStorage.getItem(LS_COUNTDOWN) || 'null'); } catch (e) { return null; }
  }
  function setCountdown(v) {
    try { v ? localStorage.setItem(LS_COUNTDOWN, JSON.stringify(v)) : localStorage.removeItem(LS_COUNTDOWN); } catch (e) {}
  }

  function formatDuration(ms) {
    const totalMin = Math.max(1, Math.round(ms / 60000));
    if (totalMin < 60) return `${totalMin} นาที`;
    const h = Math.floor(totalMin / 60), m = totalMin % 60;
    return m ? `${h} ชม. ${m} นาที` : `${h} ชม.`;
  }
  function pad2(n) { return String(n).padStart(2, '0'); }

  async function sendToSheet(cfg, { task, duration, status, user }) {
    if (!cfg.todoWebAppUrl) throw new Error('NO_WEBAPP_URL');
    // Apps Script Web Apps never send CORS headers to browser fetch() callers, so a normal
    // cross-origin request is blocked outright (confirmed: plain fetch() throws "Failed to
    // fetch" even though the same call succeeds fine from Node/curl, which don't enforce
    // CORS). mode:'no-cors' is the standard workaround — the request still reaches Google
    // and still writes the row, but the response comes back opaque (status 0, unreadable
    // body) by browser design, so we can only treat "fetch didn't throw" as success; we
    // cannot confirm the {ok:true} payload from here.
    await fetch(cfg.todoWebAppUrl, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ task, duration, status, user }),
    });
  }

  // ─────────────────────────────────────────────────────────
  // STYLES (matches TAWEE's glass-morphism design system, same
  // pattern as skills/links.js and skills/timer.js)
  // ─────────────────────────────────────────────────────────
  function injectStyles() {
    if (document.getElementById('tawee-todo-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-todo-style';
    s.textContent = `
      @keyframes taweeTodoIn { from{ opacity:0; transform:translateY(-12px) scale(.96); } to{ opacity:1; transform:translateY(0) scale(1); } }
      @keyframes taweeTodoPulse { 0%,100%{ box-shadow:0 10px 30px rgba(0,0,0,.5), 0 0 0 0 rgba(255,255,255,.18); } 50%{ box-shadow:0 10px 30px rgba(0,0,0,.5), 0 0 26px 3px rgba(255,255,255,.30); } }
      .tawee-todo-input { width:100%; padding:12px 14px; border-radius:12px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.12); color:#eef1f6; font-size:14px; font-family:inherit; box-sizing:border-box; }
      .tawee-todo-input:focus { outline:none; border-color:rgba(var(--accentRGB),.55); }
      .tawee-todo-btn-primary { padding:12px 18px; border-radius:12px; border:none; background:var(--accent); color:#04130c; font-weight:700; font-size:14px; cursor:pointer; width:100%; }
      .tawee-todo-btn-primary:hover { filter:brightness(1.08); }
      .tawee-todo-btn-secondary { padding:11px 16px; border-radius:12px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.04); color:#dfe3ea; font-size:13.5px; cursor:pointer; }
    `;
    document.head.appendChild(s);
  }

  function root() { return document.getElementById('tawee-root') || document.body; }

  function closeScrim(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // ─────────────────────────────────────────────────────────
  // STEP 1 — "ทูดูลิส" → modal: ชื่องาน / ภายในเวลา / เริ่มงาน
  // ─────────────────────────────────────────────────────────
  function showTaskModal(cfg) {
    injectStyles();
    closeScrim('tawee-todo-scrim');

    const scrim = document.createElement('div');
    scrim.id = 'tawee-todo-scrim';
    scrim.style.cssText = 'position:fixed;inset:0;z-index:70;background:rgba(2,3,8,.62);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;';
    scrim.onclick = (e) => { if (e.target === scrim) closeScrim('tawee-todo-scrim'); };

    const panel = document.createElement('div');
    panel.style.cssText = 'width:min(360px,90vw);border-radius:22px;background:rgba(10,12,20,.95);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(28px) saturate(160%);-webkit-backdrop-filter:blur(28px) saturate(160%);box-shadow:0 34px 90px rgba(0,0,0,.6),0 0 60px rgba(var(--accentRGB),.12);animation:taweeTodoIn .28s cubic-bezier(.22,1,.36,1);overflow:hidden;';

    panel.innerHTML = `
      <div style="height:2.5px;background:linear-gradient(90deg,var(--accent),var(--accent2));"></div>
      <div style="padding:22px 22px 24px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);">📋 To-Do List</span>
          <button id="tawee-todo-close" style="width:28px;height:28px;border-radius:9px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#9aa2b1;font-size:14px;cursor:pointer;">✕</button>
        </div>
        <div style="display:flex;flex-direction:column;gap:14px;">
          <div>
            <label style="display:block;font-size:12px;color:rgba(255,255,255,.5);margin-bottom:6px;">ชื่องาน</label>
            <input id="tawee-todo-name" class="tawee-todo-input" type="text" placeholder="เช่น ตอบลูกค้า A" autofocus>
          </div>
          <div>
            <label style="display:block;font-size:12px;color:rgba(255,255,255,.5);margin-bottom:6px;">ภายในเวลา (นาที)</label>
            <input id="tawee-todo-minutes" class="tawee-todo-input" type="number" min="1" max="480" placeholder="เช่น 25">
          </div>
          <div id="tawee-todo-err" style="display:none;color:#ff8a8a;font-size:12.5px;"></div>
          <button id="tawee-todo-start" class="tawee-todo-btn-primary" style="margin-top:4px;">▶️ เริ่มงาน</button>
        </div>
      </div>`;

    scrim.appendChild(panel);
    root().appendChild(scrim);

    document.getElementById('tawee-todo-close').onclick = () => closeScrim('tawee-todo-scrim');
    document.getElementById('tawee-todo-start').onclick = () => {
      const task = document.getElementById('tawee-todo-name').value.trim();
      const minutes = parseInt(document.getElementById('tawee-todo-minutes').value, 10);
      const errEl = document.getElementById('tawee-todo-err');
      if (!task) { errEl.textContent = 'กรุณากรอกชื่องานด้วยค่ะ'; errEl.style.display = ''; return; }
      if (!minutes || minutes <= 0) { errEl.textContent = 'กรุณากรอกเวลาเป็นตัวเลข (นาที) มากกว่า 0 ค่ะ'; errEl.style.display = ''; return; }
      closeScrim('tawee-todo-scrim');
      startCountdown(cfg, task, minutes);
    };
    setTimeout(() => document.getElementById('tawee-todo-name')?.focus(), 60);
  }

  // ─────────────────────────────────────────────────────────
  // STEP 2 — floating countdown widget
  // ─────────────────────────────────────────────────────────
  function ensureCountdownEl() {
    let el = document.getElementById('tawee-todo-countdown');
    if (!el) {
      injectStyles();
      el = document.createElement('div');
      el.id = 'tawee-todo-countdown';
      el.style.cssText = 'position:fixed;bottom:108px;right:24px;z-index:26;display:flex;flex-direction:column;gap:8px;padding:14px 18px;border-radius:18px;background:rgba(4,4,8,.85);border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:0 14px 40px rgba(0,0,0,.5);animation:taweeTodoIn .3s ease, taweeTodoPulse 2.6s ease-in-out infinite;min-width:180px;';
      root().appendChild(el);
    }
    return el;
  }

  function startCountdown(cfg, task, minutes) {
    const endAt = Date.now() + minutes * 60000;
    setCountdown({ task, minutes, endAt });
    renderCountdown(cfg);
  }

  function renderCountdown(cfg) {
    clearInterval(tickInterval);
    const cd = getCountdown();
    if (!cd) return;

    const el = ensureCountdownEl();
    const totalMs = cd.minutes * 60000;
    const tick = () => {
      const remain = Math.max(0, cd.endAt - Date.now());
      const mm = pad2(Math.floor(remain / 60000)), ss = pad2(Math.floor((remain % 60000) / 1000));
      const pct = Math.max(0, Math.min(100, (remain / totalMs) * 100));
      el.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
          <div style="display:flex;align-items:center;gap:7px;min-width:0;">
            <span style="width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent);flex-shrink:0;"></span>
            <span style="font-size:12.5px;color:#eef1f6;font-weight:500;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(cd.task)}</span>
          </div>
          <button id="tawee-todo-cancel" style="width:20px;height:20px;border-radius:50%;border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);color:#fff;font-size:10px;cursor:pointer;line-height:1;flex-shrink:0;">✕</button>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:var(--accent);letter-spacing:1.5px;text-align:center;line-height:1;">${mm}:${ss}</div>
        <div style="height:4px;border-radius:2px;background:rgba(255,255,255,.1);overflow:hidden;">
          <div style="height:100%;width:${pct}%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:2px;transition:width 1s linear;"></div>
        </div>`;
      const cancelBtn = document.getElementById('tawee-todo-cancel');
      if (cancelBtn) cancelBtn.onclick = () => { clearInterval(tickInterval); setCountdown(null); el.remove(); };

      if (remain <= 0) {
        clearInterval(tickInterval);
        el.remove();
        setCountdown(null);
        playChime();
        showResultPopup(cfg, cd.task, cd.minutes);
      }
    };
    tick();
    tickInterval = setInterval(tick, 1000);
  }

  function playChime() {
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      const ctx = new AC();
      [660, 880, 1100].forEach((freq, i) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sine'; o.frequency.value = freq;
        o.connect(g); g.connect(ctx.destination);
        const t0 = ctx.currentTime + i * 0.16;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(0.3, t0 + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.5);
        o.start(t0); o.stop(t0 + 0.5);
      });
      setTimeout(() => ctx.close?.(), 1200);
    } catch (e) {}
  }

  function escapeHtml(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  // ─────────────────────────────────────────────────────────
  // STEP 3 — หมดเวลา → ป็อบอัพถาม "สำเร็จไหม"
  // ─────────────────────────────────────────────────────────
  function showResultPopup(cfg, task, minutes) {
    injectStyles();
    closeScrim('tawee-todo-result-scrim');

    const scrim = document.createElement('div');
    scrim.id = 'tawee-todo-result-scrim';
    scrim.style.cssText = 'position:fixed;inset:0;z-index:71;background:rgba(2,3,8,.68);backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);display:flex;align-items:center;justify-content:center;';

    const panel = document.createElement('div');
    panel.style.cssText = 'width:min(340px,90vw);border-radius:22px;background:rgba(10,12,20,.96);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(28px) saturate(160%);-webkit-backdrop-filter:blur(28px) saturate(160%);box-shadow:0 34px 90px rgba(0,0,0,.6),0 0 60px rgba(var(--accentRGB),.14);animation:taweeTodoIn .3s cubic-bezier(.22,1,.36,1);overflow:hidden;text-align:center;';

    panel.innerHTML = `
      <div style="height:2.5px;background:linear-gradient(90deg,var(--accent),var(--accent2));"></div>
      <div style="padding:28px 22px 24px;">
        <div style="font-size:34px;margin-bottom:10px;">⏰</div>
        <div style="font-size:15px;color:#eef1f6;font-weight:600;margin-bottom:6px;">หมดเวลาแล้วค่ะ!</div>
        <div style="font-size:13.5px;color:rgba(255,255,255,.55);margin-bottom:22px;">งาน "${escapeHtml(task)}" (${minutes} นาที) — สำเร็จไหมคะ?</div>
        <div style="display:flex;gap:10px;">
          <button id="tawee-todo-fail" class="tawee-todo-btn-secondary" style="flex:1;">❌ ไม่สำเร็จ</button>
          <button id="tawee-todo-ok" class="tawee-todo-btn-primary" style="flex:1;">✅ สำเร็จ</button>
        </div>
      </div>`;

    scrim.appendChild(panel);
    root().appendChild(scrim);

    const finish = async (status) => {
      const user = cfg.userName || 'ไม่ระบุ';
      panel.style.opacity = '.6'; panel.style.pointerEvents = 'none';
      try {
        await sendToSheet(cfg, { task, duration: `${minutes} นาที`, status, user });
      } catch (e) {
        if (typeof TAWEE !== 'undefined') { TAWEE.pushMsg('system', `⚠ บันทึกงาน "${task}" ลงชีตไม่สำเร็จ: ${e.message}`); TAWEE.render(); }
        closeScrim('tawee-todo-result-scrim');
        return;
      }
      closeScrim('tawee-todo-result-scrim');
      if (typeof TAWEE !== 'undefined') {
        TAWEE.pushMsg('system', `✅ บันทึกงาน "${task}" (${minutes} นาที) — ${status} — ลงชีตแล้วค่ะ`);
        TAWEE.render();
      }
    };
    document.getElementById('tawee-todo-ok').onclick = () => finish('สำเร็จ');
    document.getElementById('tawee-todo-fail').onclick = () => finish('ไม่สำเร็จ');
  }

  // Resume an in-progress countdown if the page was reloaded mid-timer.
  function resumeOnLoad() {
    const cd = getCountdown();
    if (cd && cd.endAt > Date.now()) renderCountdown(typeof TAWEE !== 'undefined' ? TAWEE.cfg : {});
    else if (cd) setCountdown(null);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', resumeOnLoad);
  else resumeOnLoad();

  // ─────────────────────────────────────────────────────────
  // TEXT-COMMAND FLOW (kept for members who prefer typing/voice
  // without the popup — same Sheet, same endpoint)
  // ─────────────────────────────────────────────────────────
  const RE_OPEN_MODAL = /^(ทูดูลิส|to\s*-?\s*do\s*list|เปิดทูดูลิส|เปิด\s*to\s*-?\s*do\s*list|open\s*to\s*-?\s*do\s*list)\s*$/i;
  const RE_START      = /^(เริ่มงาน\s+(.+)|start\s*(?:task|working on)?\s*(.+))$/i;
  const RE_FINISH     = /^(จบงาน|เสร็จงาน|finish\s*task|done|task\s*done|finished)\s*$/i;
  const RE_DIRECT     = /^(บันทึกงาน\s+(.+?)\s*ใช้เวลา\s*(.+)|log\s*task\s+(.+?)\s*for\s*(.+))$/i;
  const RE_STATUS     = /^(กำลังทำอะไรอยู่|งานที่กำลังทำ|what\s*am\s*i\s*doing|current\s*task)\s*$/i;

  TAWEE.registerSkill('todo-timer', {
    match: (t) => RE_OPEN_MODAL.test(t) || RE_START.test(t) || RE_FINISH.test(t) || RE_DIRECT.test(t) || RE_STATUS.test(t),

    handle: async (t, raw, cfg) => {
      const user = cfg.userName || 'ไม่ระบุ';

      // ── เปิดป็อบอัพ To-Do List ───────────────────────────
      if (RE_OPEN_MODAL.test(raw)) {
        showTaskModal(cfg);
        return 'เปิดหน้าต่าง To-Do List ให้แล้วค่ะ กรอกชื่องานกับเวลา แล้วกด "เริ่มงาน" ได้เลย ✨';
      }

      // ── กำลังทำอะไรอยู่ ──────────────────────────────────
      if (RE_STATUS.test(raw)) {
        const cd = getCountdown();
        if (cd && cd.endAt > Date.now()) {
          const mm = Math.ceil((cd.endAt - Date.now()) / 60000);
          return `⏱ กำลังทำ "${cd.task}" เหลืออีกประมาณ ${mm} นาทีค่ะ`;
        }
        const active = getActive();
        if (!active) return 'ตอนนี้ไม่มีงานที่กำลังจับเวลาอยู่ค่ะ — พูดว่า "ทูดูลิส" เพื่อเริ่มได้เลย';
        const elapsed = formatDuration(Date.now() - active.startedAt);
        return `⏱ กำลังทำ "${active.task}" มาแล้ว ${elapsed} ค่ะ`;
      }

      // ── เริ่มงาน (text flow) ─────────────────────────────
      let m = raw.match(RE_START);
      if (m) {
        const task = (m[2] || m[3] || '').trim();
        if (!task) return 'บอกชื่องานด้วยนะคะ เช่น "เริ่มงาน ตอบลูกค้า" / "start task Reply to client"';
        const existing = getActive();
        if (existing) return `⚠ มีงาน "${existing.task}" ที่ยังไม่จบอยู่ค่ะ พูดว่า "จบงาน" ก่อน แล้วค่อยเริ่มงานใหม่`;
        setActive({ task, startedAt: Date.now() });
        return `▶️ เริ่มจับเวลา "${task}" แล้วค่ะ — พูดว่า "จบงาน" เมื่อทำเสร็จ`;
      }

      // ── จบงาน (text flow) ────────────────────────────────
      if (RE_FINISH.test(raw)) {
        const active = getActive();
        if (!active) return 'ไม่มีงานที่กำลังจับเวลาอยู่เลยค่ะ — ลองพูดว่า "เริ่มงาน [ชื่องาน]" ก่อนนะคะ';
        const durationMs = Date.now() - active.startedAt;
        const durationText = formatDuration(durationMs);
        try {
          await sendToSheet(cfg, { task: active.task, duration: durationText, status: 'บันทึกแล้ว', user });
        } catch (e) {
          return `⚠ จับเวลาเสร็จแล้ว (${durationText}) แต่บันทึกลงชีตไม่สำเร็จ: ${e.message} — ลองพูดว่า "จบงาน" อีกครั้งนะคะ`;
        }
        setActive(null);
        return `✅ บันทึกงาน "${active.task}" ใช้เวลา ${durationText} ลงชีตแล้วค่ะ`;
      }

      // ── บันทึกงาน [ชื่อ] ใช้เวลา [น.] (แบบไม่จับเวลาสด) ──
      m = raw.match(RE_DIRECT);
      if (m) {
        const task = (m[2] || m[4] || '').trim(), duration = (m[3] || m[5] || '').trim();
        if (!task || !duration) return 'บอกทั้งชื่องานและเวลาที่ใช้ด้วยนะคะ เช่น "บันทึกงาน ตอบลูกค้า ใช้เวลา 20 นาที" / "log task Reply to client for 20 minutes"';
        try {
          await sendToSheet(cfg, { task, duration, status: 'บันทึกแล้ว', user });
        } catch (e) {
          return `⚠ บันทึกไม่สำเร็จ: ${e.message} — ตรวจสอบอินเทอร์เน็ตแล้วลองอีกครั้งนะคะ`;
        }
        return `✅ บันทึกงาน "${task}" (${duration}) ลงชีตแล้วค่ะ`;
      }

      return null;
    },
  });
})();
