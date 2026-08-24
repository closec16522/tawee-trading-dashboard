'use strict';
// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Hub Panel (ฮับรวม)  |  skills/hub-panel.js
// รวม "แจ้งเตือนประจำวัน" + "to-do list" + "เพลง" ไว้เป็นเมนูเดียวที่พับ/กางได้
// กดปุ่มลอย 🔔 (#tawee-hub-fab) มุมขวาบนเพื่อเปิด/ปิดแผง แต่ละหมวดพับเก็บแยกกันได้
// เนื้อหาแต่ละหมวดวาดโดย TAWEE.dailyReminders.renderInto() / TAWEE.tasks.renderInto()
// ส่วนเพลงวาดเองในไฟล์นี้เพราะ music.js ไม่มี widget เป็นของตัวเองอยู่แล้ว
// ─────────────────────────────────────────────────────────────
(function () {
  'use strict';

  const COLLAPSE_KEY = 'tawee_hub_collapsed';
  let panelOpen = false;

  function loadCollapsed() {
    try { return JSON.parse(localStorage.getItem(COLLAPSE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function saveCollapsed(map) {
    try { localStorage.setItem(COLLAPSE_KEY, JSON.stringify(map)); } catch (e) {}
  }
  let collapsed = loadCollapsed();

  function musicRowHtml() {
    const st = (typeof TAWEE !== 'undefined' && TAWEE.music) ? TAWEE.music.getState() : { playing: false, trackName: '', hasTrack: false };
    return (
      '<div class="tawee-hub-music-row' + (st.playing ? ' playing' : '') + '" id="tawee-hub-music-row">' +
        '<button class="tawee-hub-music-btn" onclick="TAWEE.music.prev()" title="เพลงก่อนหน้า">⏮</button>' +
        '<button class="tawee-hub-music-btn tawee-hub-music-btn--main" onclick="TAWEE.music.toggle()" title="เล่น/หยุด">' + (st.playing ? '⏸' : '▶') + '</button>' +
        '<button class="tawee-hub-music-btn" onclick="TAWEE.music.next()" title="เพลงถัดไป">⏭</button>' +
        '<div class="tawee-hub-music-info">' +
          '<div class="tawee-hub-music-viz"><span></span><span></span><span></span><span></span></div>' +
          '<span class="tawee-hub-music-name">' + (st.trackName ? escapeHtml(st.trackName) : 'ยังไม่ได้เปิดเพลง') + '</span>' +
        '</div>' +
      '</div>'
    );
  }
  function escapeHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ไอคอนวาดเป็น SVG เส้น (ไม่ใช้ emoji) ให้ดูพรีเมี่ยม คมชัด สม่ำเสมอทุกแพลตฟอร์ม
  const ICONS = {
    reminders: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="13" r="7.5"/><path d="M12 9.5v4l2.6 2.2"/><path d="M5 3.5 3 5.5M19 3.5l2 2"/></svg>',
    tasks: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>',
    music: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
  };

  // แจ้งเตือนประจำวัน + To-do List เอาออกจากฮับก่อน (ตามคำขอ) — แจ้งเตือนยังทำงานจริงผ่าน LINE cron
  // อยู่แล้วไม่ต้องพึ่งแผงนี้ ส่วน to-do list พักไว้ก่อน จะเอากลับมาแค่ un-comment ในนี้
  const SECTIONS = [
    // {
    //   key: 'reminders', icon: ICONS.reminders, title: 'แจ้งเตือนประจำวัน',
    //   count: () => (typeof TAWEE !== 'undefined' && TAWEE.dailyReminders) ? TAWEE.dailyReminders.getAll().filter((r) => r.enabled).length : 0,
    //   render: (body) => { if (typeof TAWEE !== 'undefined' && TAWEE.dailyReminders) TAWEE.dailyReminders.renderInto(body); },
    // },
    // {
    //   key: 'tasks', icon: ICONS.tasks, title: 'To-do List',
    //   count: () => (typeof TAWEE !== 'undefined' && TAWEE.tasks) ? TAWEE.tasks.getAll().filter((t) => !t.done).length : 0,
    //   render: (body) => { if (typeof TAWEE !== 'undefined' && TAWEE.tasks) TAWEE.tasks.renderInto(body); },
    // },
    {
      key: 'music', icon: ICONS.music, title: 'เพลง',
      // โชว์เฉพาะตอนมีเพลงเล่นอยู่หรือเคยเปิดแล้ว (พูดสั่งเปิดเพลง) — ไม่โผล่ค้างตอนยังไม่ได้ใช้งาน
      visible: () => (typeof TAWEE !== 'undefined' && TAWEE.music) ? (TAWEE.music.isPlaying() || TAWEE.music.getState().hasTrack) : false,
      count: () => ((typeof TAWEE !== 'undefined' && TAWEE.music && TAWEE.music.isPlaying()) ? '►' : ''),
      render: (body) => { body.innerHTML = musicRowHtml(); },
    },
  ];

  function sectionShell(sec) {
    const isCollapsed = !!collapsed[sec.key];
    return (
      '<div class="tawee-hub-section' + (isCollapsed ? ' collapsed' : '') + '" data-key="' + sec.key + '">' +
        '<div class="tawee-hub-section-head" onclick="TAWEE.hub.toggleSection(\'' + sec.key + '\')">' +
          '<span class="tawee-hub-icon-badge ' + sec.key + '">' + sec.icon + '</span>' +
          '<span class="tawee-hub-section-title">' + sec.title + '</span>' +
          '<span class="tawee-hub-section-count" id="tawee-hub-count-' + sec.key + '"></span>' +
          '<span class="tawee-hub-chevron">▾</span>' +
        '</div>' +
        '<div class="tawee-hub-section-body"><div class="tawee-hub-section-body-inner" id="tawee-hub-body-' + sec.key + '"></div></div>' +
      '</div>'
    );
  }

  function ensurePanelSkeleton() {
    const panel = document.getElementById('tawee-hub-panel');
    if (!panel) return null;
    if (!panel.dataset.built) {
      panel.innerHTML = SECTIONS.map(sectionShell).join('');
      panel.dataset.built = '1';
    }
    return panel;
  }

  function refresh() {
    const panel = ensurePanelSkeleton();
    updateFab();
    if (!panel || !panelOpen) return; // ไม่ต้องวาดเนื้อหาถ้าแผงปิดอยู่ ประหยัดงาน
    let anyVisible = false;
    SECTIONS.forEach((sec) => {
      const el = panel.querySelector('.tawee-hub-section[data-key="' + sec.key + '"]');
      const isVisible = sec.visible ? sec.visible() : true;
      if (el) el.style.display = isVisible ? '' : 'none';
      if (!isVisible) return;
      anyVisible = true;
      const countEl = document.getElementById('tawee-hub-count-' + sec.key);
      const c = sec.count();
      if (countEl) countEl.textContent = c === '' ? '' : String(c);
      if (countEl) countEl.style.display = (c === '' || c === 0) ? 'none' : 'flex';
      const body = document.getElementById('tawee-hub-body-' + sec.key);
      if (body) sec.render(body);
    });
    let emptyEl = panel.querySelector('.tawee-hub-empty');
    if (!anyVisible) {
      if (!emptyEl) {
        emptyEl = document.createElement('div');
        emptyEl.className = 'tawee-hub-empty';
        emptyEl.style.cssText = 'padding:20px 6px;text-align:center;font-size:12.5px;color:rgba(255,255,255,.35);';
        emptyEl.textContent = 'ยังไม่มีอะไรให้แสดงตอนนี้ค่ะ';
        panel.appendChild(emptyEl);
      }
    } else if (emptyEl) {
      emptyEl.remove();
    }
  }

  function updateFab() {
    const fab = document.getElementById('tawee-hub-fab');
    if (!fab) return;
    fab.querySelectorAll('.tawee-hub-badge, .tawee-hub-dot').forEach((n) => n.remove());
    // แจ้งเตือน/to-do เอาออกจากฮับแล้ว เหลือแค่จุดเขียวบอกว่ากำลังเล่นเพลงอยู่
    if (typeof TAWEE !== 'undefined' && TAWEE.music && TAWEE.music.isPlaying()) {
      const d = document.createElement('span');
      d.className = 'tawee-hub-dot';
      fab.appendChild(d);
    }
  }

  function openPanel() {
    const panel = ensurePanelSkeleton();
    if (!panel) return;
    panelOpen = true;
    panel.classList.add('open');
    const fab = document.getElementById('tawee-hub-fab');
    if (fab) fab.classList.add('open');
    refresh();
  }
  function closePanel() {
    panelOpen = false;
    const panel = document.getElementById('tawee-hub-panel');
    if (panel) panel.classList.remove('open');
    const fab = document.getElementById('tawee-hub-fab');
    if (fab) fab.classList.remove('open');
  }
  function togglePanel() { panelOpen ? closePanel() : openPanel(); }

  function toggleSection(key) {
    collapsed[key] = !collapsed[key];
    saveCollapsed(collapsed);
    const panel = document.getElementById('tawee-hub-panel');
    const sec = panel && panel.querySelector('.tawee-hub-section[data-key="' + key + '"]');
    if (sec) sec.classList.toggle('collapsed', collapsed[key]);
  }

  // ปิดแผงเมื่อคลิกข้างนอก (เหมือนดรอปดาวน์เมนูบนสุด)
  document.addEventListener('click', (e) => {
    if (!panelOpen) return;
    const panel = document.getElementById('tawee-hub-panel');
    const fab = document.getElementById('tawee-hub-fab');
    if (panel && (panel.contains(e.target) || (fab && fab.contains(e.target)))) return;
    closePanel();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && panelOpen) closePanel(); });

  // ปุ่ม FAB เอียงตามตำแหน่งเมาส์แบบ "แม่เหล็ก" — ฟีดแบ็กพรีเมี่ยมที่ตัวปุ่มเองรู้สึกว่ามีมิติจริง
  // ข้ามตอนแผงเปิดอยู่ เพราะ .open ควบคุม transform ของตัวเองแล้ว ไม่อยากให้สองอย่างแย่งกัน
  function setupFabTilt() {
    const fab = document.getElementById('tawee-hub-fab');
    if (!fab || fab.dataset.tiltBound) return;
    fab.dataset.tiltBound = '1';
    fab.addEventListener('pointermove', (e) => {
      if (fab.classList.contains('open')) return;
      const r = fab.getBoundingClientRect();
      const dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
      const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
      const rotY = Math.max(-1, Math.min(1, dx)) * 14;
      const rotX = Math.max(-1, Math.min(1, dy)) * -14;
      fab.style.transform = `perspective(400px) scale(1.09) rotateX(${rotX}deg) rotateY(${rotY}deg)`;
    });
    fab.addEventListener('pointerleave', () => { fab.style.transform = ''; });
  }
  setupFabTilt();

  TAWEE.hub = { refresh, open: openPanel, close: closePanel, toggle: togglePanel, toggleSection };

  // อัปเดต badge/มินิเพลเยอร์ทันทีที่เพลงเปลี่ยนสถานะ แม้แผงจะปิดอยู่ (badge ต้องขึ้นเสมอ)
  (function waitForMusic() {
    if (typeof TAWEE === 'undefined' || !TAWEE.music) { setTimeout(waitForMusic, 50); return; }
    TAWEE.music.onChange(() => { updateFab(); if (panelOpen) refresh(); });
  })();

  document.addEventListener('DOMContentLoaded', refresh);
  if (document.readyState !== 'loading') refresh();
})();
