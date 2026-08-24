'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Quick Links Skill  (v2 — polished glass menu)
// Opens configured external links by voice/text command
// พูด/พิมพ์ "open menu" หรือ "เปิดเมนู" เพื่อเปิดป็อบอับรายการลิงก์
// ═══════════════════════════════════════════════════════════
(function () {
  // ── ไอคอน SVG แบบ line-icon (คมชัดทุกเครื่อง ไม่พึ่ง emoji font) ─
  const ICONS = {
    social:  '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="12" r="2.4"/><circle cx="17" cy="6" r="2.4"/><circle cx="17" cy="18" r="2.4"/><path d="M8.2 10.6l6.6-3.3M8.2 13.4l6.6 3.3"/></svg>',
    play:    '<svg viewBox="0 0 24 24" fill="white"><path d="M8 5.2v13.6c0 .8.9 1.3 1.6.9l10.9-6.8c.7-.4.7-1.4 0-1.8L9.6 4.3C8.9 3.9 8 4.4 8 5.2z"/></svg>',
    spark:   '<svg viewBox="0 0 24 24" fill="white"><path d="M12 2l1.9 6.1L20 10l-6.1 1.9L12 18l-1.9-6.1L4 10l6.1-1.9L12 2z"/></svg>',
    trend:   '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 16.5l6-6 4 4 8-8"/><path d="M15 6.5h6v6"/></svg>',
    chat:    '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.4 8.4 8.3 8.3 0 0 1-3.8-.9L3 21l1.9-5.7a8.3 8.3 0 0 1-.9-3.8A8.4 8.4 0 0 1 12.5 3 8.4 8.4 0 0 1 21 11.5z"/></svg>',
    grid:    '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3.2" y="3.2" width="17.6" height="17.6" rx="2.6"/><path d="M3.2 9h17.6M3.2 15h17.6M9 3.2v17.6M15 3.2v17.6"/></svg>',
  };

  const LINKS = [
    { match: /open facebook|facebook/i,           name: 'Facebook',       url: 'https://web.facebook.com/optionsociety', icon: ICONS.social, c1: '#3fa9ff', c2: '#2f6fed' },
    { match: /open youtube|youtube/i,             name: 'YouTube',        url: 'https://www.youtube.com/watch?v=bf3XNXT6QVk&list=RDbf3XNXT6QVk&start_radio=1&t=218s', icon: ICONS.play, c1: '#ff5f6d', c2: '#e02121' },
    { match: /open claude|claude/i,               name: 'Claude',         url: 'https://claude.ai/new', icon: ICONS.spark, c1: '#c96bff', c2: '#ff5fae' },
    { match: /open trading ?view|trading ?view/i, name: 'TradingView',    url: 'https://www.tradingview.com/', icon: ICONS.trend, c1: '#22d3ee', c2: '#2563eb' },
    { match: /open chat ?gpt|chat ?gpt/i,         name: 'ChatGPT',        url: 'https://chatgpt.com/', icon: ICONS.chat, c1: '#34d399', c2: '#059669' },
    { match: /open sheet ?1|เปิดชีท ?1|ชีทที่ ?1|open google sheet ?1/i,
      name: 'Google Sheet 1', url: 'https://docs.google.com/spreadsheets/d/1qQ4qvn1I7utyFEAy9ffWivXUwHUNBAnXh7uS1JXWyho/edit?gid=1801131835#gid=1801131835', icon: ICONS.grid, c1: '#4ade80', c2: '#16a34a' },
    { match: /open sheet ?2|เปิดชีท ?2|ชีทที่ ?2|open google sheet ?2/i,
      name: 'Google Sheet 2', url: 'https://docs.google.com/spreadsheets/d/1xrnPwIfO0T6sz1sMy1PfGr6gZoREaRW0QGIB0YvkpBo/edit?gid=1399373158#gid=1399373158', icon: ICONS.grid, c1: '#ffb454', c2: '#ff7a3d' },
  ];

  const MENU_RE = /open\s*menu|เปิดเมนู|เมนูลิงก์|แสดงเมนู|list\s*links|show\s*links/i;

  // ── ป็อบอับเมนูลิงก์ (glass card เข้าธีม TAWEE) ───────────
  function injectMenuStyles() {
    if (document.getElementById('tawee-linkmenu-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-linkmenu-style';
    s.textContent = `
      @keyframes taweeLinkMenuIn { from{ opacity:0; transform:translateY(-12px) scale(.96); } to{ opacity:1; transform:translateY(0) scale(1); } }
      @keyframes taweeLinkItemIn { from{ opacity:0; transform:translateY(6px); } to{ opacity:1; transform:translateY(0); } }
      .tawee-linkmenu-item:hover { background:rgba(255,255,255,.07) !important; border-color:rgba(var(--accentRGB),.5) !important; transform:translateX(3px); box-shadow:0 6px 20px rgba(0,0,0,.35); }
      .tawee-linkmenu-item:hover .tawee-linkmenu-arrow { color:var(--accent) !important; transform:translate(2px,-2px); }
      .tawee-linkmenu-item:hover .tawee-linkmenu-badge { filter:brightness(1.15); transform:scale(1.05); }
    `;
    document.head.appendChild(s);
  }

  function closeLinksMenu() {
    const wrap = document.getElementById('tawee-linkmenu-scrim');
    if (wrap) wrap.remove();
    document.removeEventListener('keydown', onEscKey);
  }

  function onEscKey(e) { if (e.key === 'Escape') closeLinksMenu(); }

  function hostnameOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch (e) { return ''; }
  }

  function showLinksMenu() {
    injectMenuStyles();
    closeLinksMenu();
    // แขวนไว้ใน #tawee-root เพื่อให้ยังโชว์ตอนอยู่ในโหมดเต็มจอด้วย
    const root = document.getElementById('tawee-root') || document.body;

    const scrim = document.createElement('div');
    scrim.id = 'tawee-linkmenu-scrim';
    scrim.style.cssText = 'position:fixed;inset:0;z-index:60;background:rgba(2,3,8,.6);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);display:flex;align-items:flex-start;justify-content:center;padding-top:100px;';
    scrim.onclick = (e) => { if (e.target === scrim) closeLinksMenu(); };

    const panel = document.createElement('div');
    panel.style.cssText = 'position:relative;width:min(360px,88vw);max-height:min(74vh,640px);border-radius:22px;background:rgba(10,12,20,.94);border:1px solid rgba(255,255,255,.09);backdrop-filter:blur(28px) saturate(160%);-webkit-backdrop-filter:blur(28px) saturate(160%);box-shadow:0 34px 90px rgba(0,0,0,.6),0 0 60px rgba(var(--accentRGB),.10);animation:taweeLinkMenuIn .28s cubic-bezier(.22,1,.36,1);overflow:hidden;display:flex;flex-direction:column;';

    // แถบไล่สีบนสุด
    const topBar = document.createElement('div');
    topBar.style.cssText = 'height:2.5px;flex-shrink:0;background:linear-gradient(90deg,var(--accent),var(--accent2));';
    panel.appendChild(topBar);

    const header = document.createElement('div');
    header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:17px 18px 14px;border-bottom:1px solid rgba(255,255,255,.07);flex-shrink:0;';
    header.innerHTML = `<div style="display:flex;align-items:center;gap:9px;">
        <span style="width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent);animation:taweePulse 2.2s ease-in-out infinite;"></span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);">เมนูลัด</span>
      </div>`;
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '✕';
    closeBtn.style.cssText = 'width:27px;height:27px;border-radius:9px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#9aa2b1;font-size:13px;cursor:pointer;transition:all .18s;flex-shrink:0;';
    closeBtn.onmouseenter = () => { closeBtn.style.borderColor = 'rgba(var(--accentRGB),.5)'; closeBtn.style.color = 'var(--accent)'; };
    closeBtn.onmouseleave = () => { closeBtn.style.borderColor = 'rgba(255,255,255,.1)'; closeBtn.style.color = '#9aa2b1'; };
    closeBtn.onclick = closeLinksMenu;
    header.appendChild(closeBtn);
    panel.appendChild(header);

    const list = document.createElement('div');
    list.style.cssText = 'display:flex;flex-direction:column;gap:8px;padding:14px;overflow-y:auto;';

    // เรียงตามลำดับใน LINKS จากบนลงล่าง พร้อม stagger animation
    LINKS.forEach((link, i) => {
      const item = document.createElement('button');
      item.className = 'tawee-linkmenu-item';
      item.style.cssText = `display:flex;align-items:center;gap:13px;padding:11px 13px;border-radius:14px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#eef1f6;font-size:13.5px;cursor:pointer;text-align:left;transition:all .18s;width:100%;flex-shrink:0;animation:taweeLinkItemIn .3s ease both;animation-delay:${i * 45}ms;`;
      item.innerHTML = `
        <span class="tawee-linkmenu-badge" style="width:34px;height:34px;border-radius:11px;flex-shrink:0;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,${link.c1},${link.c2});box-shadow:0 0 14px ${link.c1}55;transition:all .2s;">
          <span style="width:16px;height:16px;display:block;">${link.icon}</span>
        </span>
        <span style="flex:1;min-width:0;display:flex;flex-direction:column;gap:1px;">
          <span style="font-weight:600;color:#f3f5f9;">${link.name}</span>
          <span style="font-size:10.5px;color:rgba(255,255,255,.36);font-family:'JetBrains Mono',monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${hostnameOf(link.url)}</span>
        </span>
        <span class="tawee-linkmenu-arrow" style="color:rgba(255,255,255,.32);font-size:13px;transition:all .18s;flex-shrink:0;">↗</span>
      `;
      item.onclick = () => { window.open(link.url, '_blank', 'noopener,noreferrer'); closeLinksMenu(); };
      list.appendChild(item);
    });

    panel.appendChild(list);
    scrim.appendChild(panel);
    root.appendChild(scrim);
    document.addEventListener('keydown', onEscKey);
  }

  TAWEE.registerSkill('links', {
    match: (t) => MENU_RE.test(t) || LINKS.some(l => l.match.test(t)),
    handle: async (t) => {
      if (MENU_RE.test(t)) {
        showLinksMenu();
        return 'เปิดเมนูลิงก์ให้แล้วค่ะ เลือกได้เลย ✨';
      }
      const link = LINKS.find(l => l.match.test(t));
      if (!link) return null;
      const win = window.open(link.url, '_blank', 'noopener,noreferrer');
      if (!win) {
        // Browser blocked the auto-open (common when triggered by voice, since there's
        // no direct click for the browser to treat as user activation). Fall back to a
        // clickable button in the chat — a real click in the chat always bypasses popup blocking.
        return {
          html: true,
          speak: `I couldn't open ${link.name} automatically. Tap the button in the chat to open it.`,
          text: `⚠ Auto-open was blocked for ${link.name}. ` +
            `<a href="${link.url}" target="_blank" rel="noopener noreferrer" ` +
            `style="display:inline-block;margin-top:8px;padding:9px 16px;border-radius:10px;background:var(--accent);color:#04130c;font-weight:600;text-decoration:none;">` +
            `Open ${link.name}</a>`,
        };
      }
      return `Opening ${link.name} for you.`;
    },
  });
})();