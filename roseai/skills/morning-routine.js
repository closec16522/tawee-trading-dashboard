'use strict';
// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Morning Routine  |  skills/morning-routine.js
// พูด/พิมพ์ "Morning Routine" หรือ "มอร์นิ่ง รูทีน" เพื่อเริ่มกิจวัตรตอนเช้า (จับเวลาไล่ทีละขั้นอัตโนมัติ)
// พูด/พิมพ์ "ยกเลิก Morning Routine" เพื่อหยุดกลางคัน
// ทุกการแจ้งเตือนพูดด้วยน้ำเสียงบวก ให้กำลังใจ — ไม่ส่งแจ้งเตือนผ่าน LINE
// วางรูปกระดานวิสัยทัศน์ไว้ที่ data/vision-board.jpg (ใช้ตอนขั้นตอน "วิสัยทัศน์ชีวิต")
// ─────────────────────────────────────────────────────────────
(function () {
  const VISION_IMAGE  = 'data/vision-board.jpg';
  const LS_STATE_KEY  = 'tawee_morning_routine_state';

  // ── บันทึกลง Google Sheet "Routine Log" (Apps Script Web App — โครงเดียวกับ todo-timer.js) ──
  // โปรโตคอลตรงกับที่ออกแบบไว้ในชีต "Tawee Connect": session_start → task_start → task_complete → session_complete
  // task_start เพิ่มแถวใหม่ (สถานะ "กำลังทำ"), task_complete หาแถวเดิมด้วย session_id+activity แล้วอัปเดตเวลาจบ+สถานะ
  function getCfg() {
    try { return JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}'); } catch (e) { return {}; }
  }
  function sendRoutineEvent(payload) {
    const cfg = getCfg();
    if (!cfg.morningRoutineWebAppUrl) return; // ยังไม่ได้ตั้งค่า — ปล่อยผ่านเงียบๆ ไม่ให้กิจวัตรสะดุด
    fetch(cfg.morningRoutineWebAppUrl, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(payload),
    }).catch((e) => console.error('[morning-routine] บันทึกลงชีตไม่สำเร็จ:', e.message));
  }
  function newSessionId() {
    const d = new Date();
    const p2 = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}${p2(d.getMonth()+1)}${p2(d.getDate())}-${p2(d.getHours())}${p2(d.getMinutes())}${p2(d.getSeconds())}`;
  }
  let sessionId = null;

  const STAGES = [
    {
      key: 'gratitude', minutes: 5, title: 'เขียนขอบคุณ', icon: '🙏',
      startMsg: 'เริ่มกิจวัตรตอนเช้าค่ะ 5 นาทีแรกนี้ เขียนสิ่งที่รู้สึกขอบคุณลงไปนะคะ แค่นี้ใจก็จะเบาและสดใสขึ้นทันที',
      doneMsg:  'เก่งมากค่ะ เขียนขอบคุณครบแล้ว หัวใจดวงนี้เต็มไปด้วยความสุขแล้วนะคะ',
    },
      {
      key: 'vision', minutes: 10, title: 'วิสัยทัศน์ชีวิต', icon: '🎯', lockImage: true,
      startMsg: 'อีก 10 นาทีนี้ มองภาพวิสัยทัศน์ชีวิตให้ชัดเจนเลยนะคะ จดจำเป้าหมายที่ตั้งใจไว้ แล้วเดินไปให้ถึงค่ะ',
      doneMsg:  'เป้าหมายชัดเจนอยู่ในใจแล้วค่ะ วันนี้ทุกก้าวคือก้าวที่พาไปถึงฝันนั้นเลยค่ะ',
    },
    {
      key: 'affirm', minutes: 5, title: 'พูดตอกย้ำตัวเอง', icon: '💬',
      startMsg: 'ต่อไปอีก 5 นาที พูดตอกย้ำตัวเองด้วยคำพูดดีๆ ออกมาดังๆ เลยนะคะ ให้ใจเชื่อว่าวันนี้ทำได้แน่นอน',
      doneMsg:  'สุดยอดค่ะ พลังใจเต็มร้อยแล้ว วันนี้พร้อมลุยทุกอย่างแน่นอนค่ะ',
    },
    {
      key: 'exercise', minutes: 10, title: 'ออกกำลังกาย', icon: '🏃',
      startMsg: 'ถึงเวลาออกกำลังกาย 10 นาทีแล้วค่ะ ขยับร่างกายให้เลือดสูบฉีด ร่างกายแข็งแรง ใจก็แข็งแกร่งตามไปด้วยนะคะ',
      doneMsg:  'เยี่ยมมากค่ะ ออกกำลังกายครบแล้ว ร่างกายสดชื่นพร้อมสู้ทั้งวันเลยค่ะ',
    },
    {
      key: 'meditate', minutes: 10, title: 'นั่งสมาธิ', icon: '🧘',
      startMsg: 'ตอนนี้เวลานั่งสมาธิ 10 นาทีค่ะ หายใจเข้าลึกๆ ปล่อยวาง ให้ใจสงบและมีสติเต็มเปี่ยม',
      doneMsg:  'จิตใจสงบและมีสติเต็มเปี่ยมแล้วค่ะ พร้อมเผชิญวันนี้ด้วยความมั่นคง',
    },
  
    {
      key: 'shower', minutes: 20, title: 'อาบน้ำ กินข้าว', icon: '🚿',
      startMsg: 'อีก 20 นาทีสุดท้าย อาบน้ำและทานข้าวเช้าให้อิ่มนะคะ เติมพลังให้ร่างกายพร้อมออกไปสู้โลกกว้างค่ะ',
      doneMsg:  'ครบกิจวัตรตอนเช้าทั้งหมดแล้วค่ะ วันนี้ประธานโยพร้อมที่สุดแล้ว ไปทำให้วันนี้เป็นวันที่ดีที่สุดกันนะคะ',
    },
  ];

  let stageIndex = -1;
  let stageTimerId = null;
  let tickId = null;
  let stageEndAt = 0;
  let stageStartAt = 0;
  let weEnteredFullscreen = false;

  // ── state persistence (กันเผื่อรีเฟรชหน้าเว็บระหว่างทำกิจวัตร) ──
  function saveState() {
    try {
      if (stageIndex < 0) { localStorage.removeItem(LS_STATE_KEY); return; }
      localStorage.setItem(LS_STATE_KEY, JSON.stringify({ stageIndex, endAt: stageEndAt, startAt: stageStartAt, sessionId }));
    } catch (e) {}
  }
  function loadState() {
    try {
      const raw = localStorage.getItem(LS_STATE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }
  function clearState() { try { localStorage.removeItem(LS_STATE_KEY); } catch (e) {} }

  function pad2(n) { return String(n).padStart(2, '0'); }
  function fmtRemain(ms) {
    const s = Math.max(0, Math.round(ms / 1000));
    return pad2(Math.floor(s / 60)) + ':' + pad2(s % 60);
  }

  function injectStyles() {
    if (document.getElementById('tawee-routine-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-routine-style';
    s.textContent = `
      @keyframes taweeRoutineGlow {
        0%,100%{ box-shadow:0 8px 26px rgba(0,0,0,.5), 0 0 0 0 rgba(var(--accentRGB),.25); }
        50%{ box-shadow:0 8px 26px rgba(0,0,0,.5), 0 0 18px 1px rgba(var(--accentRGB),.35); }
      }
      .tawee-routine-row.current { animation: taweeRoutineGlow 3s ease-in-out infinite; }
    `;
    document.head.appendChild(s);
  }

  // ── widget แถบไทม์ไลน์ลอยกลางซ้ายจอ แสดงทุกขั้นตอนพร้อมกัน (เห็นภาพรวมทั้งหมด) ──
  function ensureWidget() {
    injectStyles();
    let el = document.getElementById('tawee-routine-widget');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'tawee-routine-widget';
    el.style.cssText = 'position:fixed;top:50%;left:24px;transform:translateY(-50%);z-index:23;display:flex;flex-direction:column;gap:8px;animation:taweeFade .3s ease;';
    const root = document.getElementById('tawee-root') || document.body;
    root.appendChild(el);
    return el;
  }
  function removeWidget() {
    const el = document.getElementById('tawee-routine-widget');
    if (el) el.remove();
  }
  function rowHtml(idx) {
    const stage = STAGES[idx];
    const isDone = idx < stageIndex;
    const isCurrent = idx === stageIndex;
    const opacity = isDone ? '.5' : (isCurrent ? '1' : '.42');
    const borderRGB = isCurrent ? 'rgba(var(--accentRGB),.4)' : 'rgba(255,255,255,.1)';
    let ringBg = 'rgba(255,255,255,.12)';
    let iconHtml = stage.icon;
    let timeHtml;
    if (isDone) {
      ringBg = 'var(--accent)';
      iconHtml = '✓';
      timeHtml = 'เสร็จแล้ว';
    } else if (isCurrent) {
      const remain = stageEndAt - Date.now();
      const total = Math.max(1, stageEndAt - stageStartAt);
      const pct = Math.max(0, Math.min(1, 1 - remain / total));
      ringBg = 'conic-gradient(var(--accent) ' + (pct * 360).toFixed(1) + 'deg, rgba(255,255,255,.12) 0deg)';
      timeHtml = fmtRemain(remain);
    } else {
      timeHtml = stage.minutes + ' นาที';
    }
    return (
      '<div class="tawee-routine-row' + (isCurrent ? ' current' : '') + '" style="display:flex;align-items:center;gap:10px;padding:7px 14px 7px 7px;border-radius:14px;background:rgba(6,8,14,.82);border:1px solid ' + borderRGB + ';backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);opacity:' + opacity + ';transition:opacity .3s;min-width:188px;">' +
        '<div style="position:relative;width:32px;height:32px;border-radius:50%;flex-shrink:0;background:' + ringBg + ';">' +
          '<div style="position:absolute;inset:3px;border-radius:50%;background:#05060b;display:flex;align-items:center;justify-content:center;font-size:13.5px;color:' + (isDone ? 'var(--accent)' : '#fff') + ';">' + iconHtml + '</div>' +
        '</div>' +
        '<div style="display:flex;flex-direction:column;gap:2px;min-width:0;">' +
          '<span style="font-size:11.5px;font-weight:600;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px;">' + stage.title + '</span>' +
          '<span style="font-size:10px;font-family:\'JetBrains Mono\',monospace;color:' + (isCurrent ? 'var(--accent)' : 'rgba(255,255,255,.45)') + ';font-weight:' + (isCurrent ? '700' : '400') + ';">' + timeHtml + '</span>' +
        '</div>' +
      '</div>'
    );
  }
  function renderWidget() {
    if (stageIndex < 0) return;
    const el = ensureWidget();
    let html = '';
    for (let i = 0; i < STAGES.length; i++) html += rowHtml(i);
    html +=
      '<button onclick="TAWEE.morningRoutine.cancel()" style="margin-top:2px;padding:7px 10px;border-radius:12px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.04);color:rgba(255,255,255,.6);font-size:11px;cursor:pointer;">✕ ยกเลิก Morning Routine</button>';
    el.innerHTML = html;
  }
  function ensureTick() {
    if (tickId) return;
    tickId = setInterval(() => {
      if (stageIndex < 0) { clearInterval(tickId); tickId = null; return; }
      renderWidget();
    }, 1000);
  }

  // ── overlay ล็อกจอด้วยภาพวิสัยทัศน์เต็มจอ (มีปุ่มปิด) ──
  function showVisionOverlay() {
    if (document.getElementById('tawee-vision-overlay')) return;
    const ov = document.createElement('div');
    ov.id = 'tawee-vision-overlay';
    ov.style.cssText = 'position:fixed;inset:0;z-index:200;background:#04050a;animation:taweeFade .35s ease;';
    ov.innerHTML =
      '<img src="' + VISION_IMAGE + '" alt="วิสัยทัศน์ชีวิต" ' +
        'style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain;" ' +
        'onerror="this.style.display=\'none\';document.getElementById(\'tawee-vision-fallback\').style.display=\'flex\';">' +
      '<div id="tawee-vision-fallback" style="display:none;position:absolute;inset:0;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:rgba(255,255,255,.7);font-size:14px;text-align:center;padding:0 10vw;">' +
        '<span style="font-size:34px;">🖼️</span>' +
        '<span>ยังไม่พบรูปกระดานวิสัยทัศน์ค่ะ<br>วางไฟล์ไว้ที่ data/vision-board.jpg แล้วลองใหม่นะคะ</span>' +
      '</div>' +
      '<div style="position:absolute;bottom:0;left:0;right:0;padding:28px 20px;text-align:center;color:rgba(255,255,255,.7);font-size:13px;letter-spacing:.3px;background:linear-gradient(transparent,rgba(0,0,0,.55));">มองภาพนี้ให้ชัดเจน แล้วจดจำเป้าหมายของวันนี้ไว้ค่ะ</div>' +
      '<button onclick="TAWEE.morningRoutine.closeVision()" title="ปิด" style="position:absolute;top:24px;right:24px;width:42px;height:42px;border-radius:50%;border:1px solid rgba(255,255,255,.3);background:rgba(0,0,0,.35);color:#fff;font-size:16px;cursor:pointer;line-height:1;backdrop-filter:blur(10px);">✕</button>';
    const root = document.getElementById('tawee-root') || document.body;
    root.appendChild(ov);
    // เข้าโหมดเต็มจอจริงถ้าเบราว์เซอร์อนุญาต (ไม่บังคับ ถ้าไม่ได้ก็ยังบังหน้าจอด้วย overlay ตามปกติ)
    try {
      const target = document.getElementById('tawee-root') || document.documentElement;
      if (!document.fullscreenElement && target.requestFullscreen) {
        target.requestFullscreen().then(() => { weEnteredFullscreen = true; }).catch(() => {});
      }
    } catch (e) {}
  }
  function removeVisionOverlay() {
    const el = document.getElementById('tawee-vision-overlay');
    if (el) el.remove();
    if (weEnteredFullscreen) {
      weEnteredFullscreen = false;
      try { if (document.fullscreenElement) document.exitFullscreen?.(); } catch (e) {}
    }
  }

  function announce(text) {
    TAWEE.pushMsg('assistant', text);
    TAWEE.speakText(text);
    TAWEE.render();
  }

  function startStage(i) {
    if (i >= STAGES.length) {
      sendRoutineEvent({ event: 'session_complete', session_id: sessionId, ended_at: new Date().toISOString(), status: 'เสร็จแล้ว' });
      finishRoutine();
      return;
    }
    stageIndex = i;
    const stage = STAGES[i];
    stageStartAt = Date.now();
    stageEndAt = stageStartAt + stage.minutes * 60 * 1000;
    saveState();
    sendRoutineEvent({
      event: 'task_start', session_id: sessionId, activity: stage.title, order: i + 1,
      planned_minutes: stage.minutes, started_at: new Date(stageStartAt).toISOString(), status: 'กำลังทำ',
    });
    announce(stage.startMsg);
    if (stage.lockImage) showVisionOverlay();
    renderWidget();
    ensureTick();
    stageTimerId = setTimeout(() => advanceStage(i), stage.minutes * 60 * 1000);
  }

  function advanceStage(i) {
    const stage = STAGES[i];
    if (stage.lockImage) removeVisionOverlay();
    if (stage) {
      sendRoutineEvent({ event: 'task_complete', session_id: sessionId, activity: stage.title, ended_at: new Date().toISOString(), status: 'เสร็จแล้ว' });
      announce(stage.doneMsg);
    }
    startStage(i + 1);
  }

  function finishRoutine() {
    stageIndex = -1;
    stageTimerId = null;
    if (tickId) { clearInterval(tickId); tickId = null; }
    removeWidget();
    removeVisionOverlay();
    clearState();
    sessionId = null;
    if (TAWEE.music) TAWEE.music.stop();
  }

  function startRoutine() {
    if (stageIndex >= 0) return 'Morning Routine กำลังดำเนินอยู่แล้วค่ะ ขั้นตอนตอนนี้คือ "' + STAGES[stageIndex].title + '"';
    sessionId = newSessionId();
    sendRoutineEvent({ event: 'session_start', session_id: sessionId, started_at: new Date().toISOString(), status: 'กำลังทำ' });
    startStage(0);
    if (TAWEE.music) TAWEE.music.play(); // เปิดเพลงคลอไปตลอดกิจวัตร หยุดเองตอนจบ/ยกเลิก
    return '🌅 เริ่ม Morning Routine แล้วค่ะ วันนี้จะเป็นวันที่ดีมากแน่นอน ไปเริ่มกันเลยค่ะ';
  }

  function cancelRoutine() {
    const wasRunning = stageIndex >= 0;
    if (stageTimerId) { clearTimeout(stageTimerId); stageTimerId = null; }
    finishRoutine();
    if (!wasRunning) return 'ตอนนี้ไม่มี Morning Routine ที่กำลังทำงานอยู่ค่ะ';
    announce('หยุด Morning Routine แล้วค่ะ ไม่เป็นไรเลยนะคะ พร้อมเมื่อไหร่ก็พูดว่า Morning Routine ได้ใหม่เสมอค่ะ');
    return null;
  }

  // ปิดขั้นตอนภาพวิสัยทัศน์ก่อนเวลา — ถือว่าขั้นนี้จบแล้ว ไปขั้นถัดไปเลย
  function closeVision() {
    if (stageIndex < 0 || !STAGES[stageIndex] || !STAGES[stageIndex].lockImage) { removeVisionOverlay(); return; }
    if (stageTimerId) { clearTimeout(stageTimerId); stageTimerId = null; }
    advanceStage(stageIndex);
  }

  TAWEE.morningRoutine = {
    start: startRoutine,
    cancel: cancelRoutine,
    closeVision,
    isRunning: () => stageIndex >= 0,
  };

  // ── resume หลังรีเฟรชหน้า ถ้ายังไม่หมดเวลาขั้นตอนเดิม ──
  (function resume() {
    const s = loadState();
    if (!s || s.stageIndex == null || !STAGES[s.stageIndex]) return;
    const remain = s.endAt - Date.now();
    if (remain <= 0) { clearState(); return; }
    stageIndex = s.stageIndex;
    stageEndAt = s.endAt;
    stageStartAt = s.startAt || (s.endAt - STAGES[s.stageIndex].minutes * 60 * 1000);
    sessionId = s.sessionId || newSessionId(); // เผื่อ state เก่าก่อนอัปเดตนี้ไม่มี sessionId
    const stage = STAGES[stageIndex];
    if (stage.lockImage) showVisionOverlay();
    renderWidget();
    ensureTick();
    stageTimerId = setTimeout(() => advanceStage(stageIndex), remain);
  })();

  // ── ลงทะเบียน Skill ── (รองรับ "Morning Routine" และคำไทยที่ STT อาจถอดเสียงต่างกัน
  // เช่น "มอร์นิ่ง รูทีน" / "มอนิ่งลูทีน" / "มอนิ่ง รูทีน" ฯลฯ — เลยเขียนแบบยืดหยุ่น
  // แทนที่จะ match สตริงตายตัว)
  const START_RE  = /morning\s*routine|มอ(ร์)?นิ่?ง\s*[รล]ูทีน/i;
  const CANCEL_RE = /(ยกเลิก|หยุด|ปิด).*(morning\s*routine|มอ(ร์)?นิ่?ง\s*[รล]ูทีน)/i;
  const MATCH_RE  = new RegExp(CANCEL_RE.source + '|' + START_RE.source, 'i');

  TAWEE.registerSkill('morning-routine', {
    match: (t) => MATCH_RE.test(t),
    handle: async (t) => {
      if (CANCEL_RE.test(t)) return cancelRoutine();
      return startRoutine();
    },
  });
})();
