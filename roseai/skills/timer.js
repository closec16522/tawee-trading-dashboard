'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Countdown Timer  |  skills/timer.js  (v4)
// ═══════════════════════════════════════════════════════════
(function () {
  const activeTimers = {};
  const widgetEls = {};
  let timerIdCounter = 0;
  let rafId = null;

  const SOUNDS = {
    beep:  { label: 'Beep',       fn: () => _playTone(880,  'sine',     3, 0.35) },
    bell:  { label: 'Deep Bell',  fn: () => _playTone(220,  'sine',     2, 0.80) },
    high:  { label: 'High Alert', fn: () => _playTone(1320, 'sine',     4, 0.25) },
    chime: { label: 'Soft Chime', fn: () => _playTone(528,  'triangle', 2, 0.60) },
    pulse: { label: 'Pulse',      fn: () => _playTone(660,  'square',   3, 0.30) },
    sweep: { label: 'Alarm',      fn: _playSweep },
  };

  TAWEE.timerSound = TAWEE.timerSound || 'beep';

  const WAKE_MSG = 'ขี้เกียจวันนี้ ก็อย่าเสียใจทีหลังแล้วกัน 1 ชีวิตมี 80 ปี ตอนนี้ประธานโยเหลือกี่วัน ลงมือทำทันที 5 4 3 2 1 ลงมือทำทันที 5 4 3 2 1';

  function _playTone(freq, type, times, interval) {
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      const ctx = new AC();
      const now = ctx.currentTime;
      for (let i = 0; i < times; i++) {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = type; o.frequency.value = freq;
        o.connect(g); g.connect(ctx.destination);
        const t0 = now + i * interval;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(0.35, t0 + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + (interval * 0.85));
        o.start(t0); o.stop(t0 + interval);
      }
      setTimeout(() => ctx.close?.(), (times * interval + 0.5) * 1000);
    } catch (e) {}
  }

  function _playSweep() {
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      const ctx = new AC();
      for (let i = 0; i < 3; i++) {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sawtooth';
        o.frequency.setValueAtTime(440, ctx.currentTime + i * 0.5);
        o.frequency.linearRampToValueAtTime(880, ctx.currentTime + i * 0.5 + 0.4);
        g.gain.setValueAtTime(0.0001, ctx.currentTime + i * 0.5);
        g.gain.exponentialRampToValueAtTime(0.3, ctx.currentTime + i * 0.5 + 0.05);
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + i * 0.5 + 0.45);
        o.connect(g); g.connect(ctx.destination);
        o.start(ctx.currentTime + i * 0.5);
        o.stop(ctx.currentTime + i * 0.5 + 0.46);
      }
      setTimeout(() => ctx.close?.(), 2000);
    } catch (e) {}
  }

  function playAlert() {
    const s = SOUNDS[TAWEE.timerSound] || SOUNDS.beep;
    s.fn();
  }

  const THAI_NUM = {
    'หนึ่ง':1,'สอง':2,'สาม':3,'สี่':4,'ห้า':5,'หก':6,'เจ็ด':7,'แปด':8,'เก้า':9,'สิบ':10,
    'สิบเอ็ด':11,'สิบสอง':12,'สิบสาม':13,'สิบสี่':14,'สิบห้า':15,'สิบหก':16,'สิบเจ็ด':17,'สิบแปด':18,'สิบเก้า':19,
    'ยี่สิบ':20,'สามสิบ':30,'สี่สิบ':40,'ห้าสิบ':50,'หกสิบ':60,
  };

  function parseNumber(str) {
    str = (str || '').trim();
    if (/^\d+(\.\d+)?$/.test(str)) return parseFloat(str);
    if (THAI_NUM[str] != null) return THAI_NUM[str];
    return null;
  }

  function toSeconds(amount, unitWord) {
    const u = (unitWord || '').toLowerCase();
    // เช็ค "วินาที" ก่อน "นาที" เสมอ เพราะ "วินาที" มีคำว่า "นาที" ซ้อนอยู่ข้างใน
    // (เช่น .test("วินาที") ของ /นาที/ จะ true ด้วย ถ้าเช็คนาทีก่อนจะตีความ "วินาที" เป็นนาทีผิดๆ)
    if (/ชั่วโมง|hour|hr/.test(u))  return amount * 3600;
    if (/วินาที|วิ|sec/.test(u))     return amount;
    if (/นาที|min/.test(u))          return amount * 60;
    return amount;
  }

  function formatDuration(sec) {
    sec = Math.round(sec);
    const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    const parts = [];
    if (h) parts.push(h + ' ชั่วโมง');
    if (m) parts.push(m + ' นาที');
    if (s || !parts.length) parts.push(s + ' วินาที');
    return parts.join(' ');
  }

  function injectStyles() {
    if (document.getElementById('tawee-timer-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-timer-style';
    s.textContent = `
      @keyframes taweeTimerPulse {
        0%,100%{ box-shadow:0 10px 30px rgba(0,0,0,.5), 0 0 0 0 rgba(255,255,255,.18); }
        50%{ box-shadow:0 10px 30px rgba(0,0,0,.5), 0 0 26px 3px rgba(255,255,255,.30); }
      }
      @keyframes taweeTimerFlash { 0%,100%{ opacity:1; } 50%{ opacity:.5; } }
      .tawee-timer-card { animation: taweeFade .3s ease, taweeTimerPulse 2.6s ease-in-out infinite; transition: opacity .2s; }
      .tawee-timer-card.critical { animation: taweeFade .3s ease, taweeTimerFlash .45s ease-in-out infinite; }
    `;
    document.head.appendChild(s);
  }

  function escapeHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function ensureWidgetEl() {
    injectStyles();
    let el = document.getElementById('tawee-timer-widget');
    if (!el) {
      el = document.createElement('div');
      el.id = 'tawee-timer-widget';
      el.style.cssText = 'position:fixed;top:70px;left:24px;z-index:22;display:flex;flex-direction:column;gap:10px;align-items:flex-start;pointer-events:none;';
      const root = document.getElementById('tawee-root') || document.body;
      root.appendChild(el);
    }
    return el;
  }

  function createCard(id, t) {
    const card = document.createElement('div');
    card.className = 'tawee-timer-card';
    card.style.cssText = 'pointer-events:auto;display:flex;align-items:center;gap:12px;padding:9px 14px 9px 9px;border-radius:18px;background:rgba(4,4,8,.82);border:1px solid rgba(255,255,255,.16);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);';
    card.innerHTML = `
      <div class="tawee-timer-ring" style="position:relative;width:54px;height:54px;border-radius:50%;flex-shrink:0;">
        <div style="position:absolute;inset:5px;border-radius:50%;background:#050508;display:flex;align-items:center;justify-content:center;">
          <span class="tawee-timer-time" style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600;color:#fff;letter-spacing:.3px;"></span>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:2px;min-width:0;">
        ${t.label ? `<span style="font-size:12.5px;color:#fff;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:130px;">${escapeHtml(t.label)}</span>` : ''}
        <span style="font-size:9.5px;color:rgba(255,255,255,.45);font-family:'JetBrains Mono',monospace;letter-spacing:1.5px;text-transform:uppercase;">countdown</span>
      </div>
      <button onclick="TAWEE._cancelTimerId(${id})" style="margin-left:2px;width:22px;height:22px;border-radius:50%;border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.08);color:#fff;font-size:11px;cursor:pointer;line-height:1;flex-shrink:0;">✕</button>
    `;
    return { card, ring: card.querySelector('.tawee-timer-ring'), timeEl: card.querySelector('.tawee-timer-time') };
  }

  function renderWidget() {
    const el = ensureWidgetEl();
    const now = Date.now();
    const ids = Object.keys(activeTimers);
    for (const id in widgetEls) {
      if (!activeTimers[id]) { widgetEls[id].card.remove(); delete widgetEls[id]; }
    }
    for (const id of ids) {
      const t = activeTimers[id];
      if (!widgetEls[id]) {
        widgetEls[id] = createCard(id, t);
        el.appendChild(widgetEls[id].card);
      }
      const w = widgetEls[id];
      const remain = Math.max(0, t.endAt - now);
      const mm = String(Math.floor(remain / 60000)).padStart(2, '0');
      const ss = String(Math.floor((remain % 60000) / 1000)).padStart(2, '0');
      const totalMs = Math.max(1, t.seconds * 1000);
      const pct = Math.max(0, Math.min(1, remain / totalMs));
      const deg = (pct * 360).toFixed(1);
      w.ring.style.background = `conic-gradient(#fff ${deg}deg, rgba(255,255,255,.14) 0deg)`;
      w.timeEl.textContent = `${mm}:${ss}`;
      const critical = remain > 0 && remain <= 5000;
      w.card.classList.toggle('critical', critical);
    }
  }

  function ensureTick() {
    if (rafId) return;
    const loop = () => {
      renderWidget();
      if (Object.keys(activeTimers).length) rafId = requestAnimationFrame(loop);
      else rafId = null;
    };
    rafId = requestAnimationFrame(loop);
  }

  function startTimer(seconds, label) {
    const id = ++timerIdCounter;
    const endAt = Date.now() + seconds * 1000;
    const handle = setTimeout(() => {
      delete activeTimers[id];
      playAlert();
      const feedMsg = (label ? `⏰ "${label}" ครบเวลาแล้วค่ะ!\n` : '⏰ ครบเวลาแล้วค่ะ!\n') + WAKE_MSG;
      TAWEE.pushMsg('system', feedMsg);
      TAWEE.speakText(WAKE_MSG);
      TAWEE.render();
      renderWidget();
    }, seconds * 1000);
    activeTimers[id] = { handle, endAt, seconds, label };
    renderWidget();
    ensureTick();
    return id;
  }

  function cancelOne(id) {
    if (!activeTimers[id]) return;
    clearTimeout(activeTimers[id].handle);
    delete activeTimers[id];
    renderWidget();
  }

  function cancelAll() {
    const n = Object.keys(activeTimers).length;
    for (const id in activeTimers) cancelOne(id);
    return n;
  }

  function listRemaining() {
    const now = Date.now();
    return Object.values(activeTimers).map(t => ({
      label: t.label, remaining: Math.max(0, (t.endAt - now) / 1000),
    }));
  }

  TAWEE._cancelTimerId = function (id) { cancelOne(id); };

  TAWEE.setTimerSound = function (name) {
    if (!SOUNDS[name]) return false;
    TAWEE.timerSound = name;
    return true;
  };

  TAWEE.listTimerSounds = function () {
    return Object.entries(SOUNDS).map(([id, s]) => `${id} — ${s.label}`).join('\n');
  };

  // ── FIX: เพิ่ม วิ และ ชม รองรับคำย่อภาษาไทย ────────────────
  // บั๊กเดิม: [ก-๙]+ กว้างเกินไป (จับได้ทุกตัวอักษรไทย) ภาษาไทยไม่มีช่องว่างคั่นคำ ทำให้ regex โลภกลืนทั้งประโยคก่อนหน้าตัวเลข
  // (เช่น "ตั้งเวลานับถอยหลังสิบนาที" จับ "ตั้งเวลานับถอยหลังสิบ" ทั้งดุ้นมาเป็น "ตัวเลข" แล้วเทียบกับ dictionary ไม่เจอ เลยพัง)
  // แก้โดยระบุเฉพาะคำเลขไทยที่รู้จักจริงจาก THAI_NUM เท่านั้น เรียงยาวไปสั้นกันคำสั้นแย่งจับก่อนคำยาว (เช่น "สิบเอ็ด" ต้องมาก่อน "สิบ")
  const THAI_NUM_ALT = Object.keys(THAI_NUM).sort((a, b) => b.length - a.length).join('|');
  const NUM_UNIT_RE = new RegExp('(\\d+(?:\\.\\d+)?|' + THAI_NUM_ALT + ')\\s*(ชั่วโมง|ชม\\.?|นาที|นท\\.?|วินาที|วิ\\.?|hours?|hrs?|minutes?|mins?|seconds?|secs?)', 'i');
  const SET_TH      = /ตั้ง(?:เวลา|นาฬิกา(?:ปลุก)?|ปลุก|ไทม์เมอร์)|นับถอยหลัง|จับเวลา|ตั้งเวลา/;
  const SET_EN      = /\b(start|set|begin|countdown|timer|alarm)\b/i;
  const CANCEL_RE   = /(?:ยกเลิก|หยุด|ปิด)(?:ตั้งเวลา|นาฬิกาปลุก|ไทม์เมอร์|timer|countdown)|(?:cancel|stop)\s*(?:the\s*)?(?:timer|countdown|alarm)/i;
  const CHECK_RE    = /(?:เหลือเวลา|เวลาที่เหลือ|ไทม์เมอร์.*เท่าไหร่|เหลืออีกกี่)|how\s*(?:much|long).*(?:left|remain)|time\s*left/i;
  const SOUND_RE    = /timer\s*sound\s*(\w+)/i;

  TAWEE.registerSkill('timer', {
    match(t) {
      if (CANCEL_RE.test(t) || CHECK_RE.test(t) || SOUND_RE.test(t)) return true;
      if (NUM_UNIT_RE.test(t) && (SET_TH.test(t) || SET_EN.test(t))) return true;
      // คำสั่งภาษาไทยชัดเจนอยู่แล้ว (เช่น "ตั้งเวลานับถอยหลัง" เฉยๆ ไม่บอกจำนวน) — จับไว้ก่อนเสมอ
      // ให้ handle() ถามกลับว่ากี่นาที แทนที่จะหลุดไปให้ Claude ตอบเลื่อนลอยแล้วไม่ได้ตั้งอะไรจริง
      // (ไม่รวม SET_EN เพราะคำอังกฤษ เช่น start/set/timer กว้างเกินไป เสี่ยงจับประโยคอื่นที่ไม่เกี่ยวโดยไม่ตั้งใจ)
      if (SET_TH.test(t)) return true;
      return false;
    },

    async handle(t, original) {
      const sm = original.match(SOUND_RE);
      if (sm) {
        const ok = TAWEE.setTimerSound(sm[1].toLowerCase());
        if (ok) {
          playAlert();
          return `เปลี่ยนเสียงเตือนเป็น "${SOUNDS[TAWEE.timerSound].label}" แล้วค่ะ`;
        }
        return `ไม่พบเสียงนั้นค่ะ มีให้เลือก:\n${TAWEE.listTimerSounds()}`;
      }

      if (CANCEL_RE.test(t)) {
        const n = cancelAll();
        return n > 0
          ? `ยกเลิกตั้งเวลาทั้งหมด ${n} รายการแล้วค่ะ`
          : 'ตอนนี้ไม่มีตั้งเวลาที่กำลังทำงานอยู่ค่ะ';
      }

      if (CHECK_RE.test(t)) {
        const list = listRemaining();
        if (!list.length) return 'ไม่มีตั้งเวลาที่กำลังนับถอยหลังอยู่ค่ะ';
        return list.map(x => `${x.label ? x.label + ': ' : ''}เหลือ ${formatDuration(x.remaining)}`).join('\n');
      }

      // ลอง match จาก original ก่อน ถ้าไม่ได้ค่อย match จาก t
      const m = original.match(NUM_UNIT_RE) || t.match(NUM_UNIT_RE);
      // ไม่มีตัวเลข/หน่วยเวลาเลย (เช่นพูดแค่ "ตั้งเวลานับถอยหลัง" เฉยๆ) — ถามกลับ ไม่ใช่เงียบไปเฉยๆ
      if (!m) return 'บอกจำนวนเวลาชัดๆ ด้วยนะคะ เช่น "ตั้งเวลา 5 นาที" หรือ "นับถอยหลัง 30 วินาที"';

      const amount = parseNumber(m[1]);
      if (amount == null || amount <= 0)
        return 'บอกจำนวนเวลาชัดๆ อีกครั้งนะคะ เช่น "ตั้งเวลา 5 นาที" หรือ "start 5 minutes"';

      const seconds = toSeconds(amount, m[2] || 'วินาที');
      if (seconds > 24 * 3600) return 'ตั้งเวลาได้สูงสุด 24 ชั่วโมงค่ะ';

      const labelTH = original.match(/(?:เพื่อ|สำหรับ)\s*(.+)$/);
      const labelEN = original.match(/\bfor\s+([a-zA-Zก-๙].+)$/i);
      const label   = ((labelTH ? labelTH[1] : (labelEN ? labelEN[1] : '')) || '').trim();

      startTimer(seconds, label);
      return `ตั้งเวลา ${formatDuration(seconds)} แล้วค่ะ${label ? ' สำหรับ "' + label + '"' : ''} — จะแจ้งเตือนเมื่อครบกำหนด ⏳`;
    },
  });
})();