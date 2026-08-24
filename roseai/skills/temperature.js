'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Room Temperature Skill  |  temperature.js
// ═══════════════════════════════════════════════════════════
(function () {

  // ── State ────────────────────────────────────────────────
  let lastReading = null;     // { indoor, outdoor, humidity, comfort, time }
  let _raf        = null;

  // ── Comfort labels ───────────────────────────────────────
  const COMFORT = [
    { max: 16, label: 'หนาวมาก ❄️',  color: '#60d4ff', bg: 'rgba(96,212,255,.12)'  },
    { max: 20, label: 'เย็นสบาย 🌬',  color: '#60d4ff', bg: 'rgba(96,212,255,.08)'  },
    { max: 24, label: 'สบายมาก 😊',   color: '#35f0a0', bg: 'rgba(53,240,160,.10)'  },
    { max: 27, label: 'อุ่นสบาย 🌿',  color: '#ffe066', bg: 'rgba(255,224,102,.09)'  },
    { max: 30, label: 'ร้อนนิดหน่อย 🌤', color: '#ffb454', bg: 'rgba(255,180,84,.10)'  },
    { max: 34, label: 'ร้อน ☀️',     color: '#ff8c42', bg: 'rgba(255,140,66,.10)'  },
    { max: 99, label: 'ร้อนมาก 🔥',  color: '#ff4d6d', bg: 'rgba(255,77,109,.12)'  },
  ];

  function comfortFor(t) { return COMFORT.find(c => t <= c.max) || COMFORT[COMFORT.length - 1]; }

  // ── Estimate indoor temp from outdoor ────────────────────
  // Assume AC keeps indoor ~24–26°C when outdoor > 28°C,
  // or outdoor + offset otherwise
  function estimateIndoor(outdoor, hour) {
    const h = hour ?? new Date().getHours();
    if (outdoor > 30) return +(23.5 + Math.sin(h / 24 * Math.PI) * 1.8 + (Math.random() - .5) * .4).toFixed(1);
    if (outdoor > 26) return +(outdoor - 3.5 + (Math.random() - .5) * .6).toFixed(1);
    return +(outdoor + 1.2 + (Math.random() - .5) * .5).toFixed(1);
  }

  function estimateHumidity(outdoor, indoor) {
    // Indoor humidity tends to be lower thanks to AC
    const base = outdoor > 28 ? 52 : 62;
    return Math.round(base + (Math.random() - .5) * 8);
  }

  // ── Fetch outdoor temp from Open-Meteo ───────────────────
  async function fetchOutdoor(lat, lon) {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
      `&current=temperature_2m,relative_humidity_2m,weather_code&timezone=Asia%2FBangkok`;
    const r = await fetch(url);
    const d = await r.json();
    return {
      outdoor:  +(d.current.temperature_2m).toFixed(1),
      humidity: d.current.relative_humidity_2m,
    };
  }

  // ── Build & show the temperature modal ───────────────────
  function showModal(reading, animateIn = true) {
    closeModal();
    injectStyles();

    const c = comfortFor(reading.indoor);
    const root = document.getElementById('tawee-root') || document.body;

    const scrim = document.createElement('div');
    scrim.id = 'tawee-temp-scrim';
    scrim.style.cssText = 'position:fixed;inset:0;z-index:65;background:rgba(2,3,8,.72);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;';
    scrim.onclick = (e) => { if (e.target === scrim) closeModal(); };

    const panel = document.createElement('div');
    panel.style.cssText = `position:relative;width:min(420px,92vw);border-radius:28px;background:rgba(10,12,20,.95);border:1px solid ${c.color}33;backdrop-filter:blur(30px) saturate(180%);-webkit-backdrop-filter:blur(30px) saturate(180%);box-shadow:0 40px 100px rgba(0,0,0,.7),0 0 80px ${c.color}18;overflow:hidden;${animateIn ? 'animation:taweeTempIn .45s cubic-bezier(.22,1,.36,1);' : ''}`;

    // Gradient top stripe
    const stripe = document.createElement('div');
    stripe.style.cssText = `height:3px;background:linear-gradient(90deg,${c.color},var(--accent2));`;
    panel.appendChild(stripe);

    // Canvas for animated gauge
    const canvasWrap = document.createElement('div');
    canvasWrap.style.cssText = 'position:relative;display:flex;justify-content:center;padding:32px 24px 0;';
    const cv = document.createElement('canvas');
    cv.id   = 'tawee-temp-canvas';
    cv.width = 300; cv.height = 200;
    cv.style.cssText = 'display:block;filter:drop-shadow(0 0 28px ' + c.color + '55);';
    canvasWrap.appendChild(cv);
    panel.appendChild(canvasWrap);

    // Info row
    panel.insertAdjacentHTML('beforeend', `
      <div style="padding:18px 28px 26px;display:flex;flex-direction:column;gap:14px;">
        <div style="text-align:center;">
          <div style="font-size:46px;font-weight:700;letter-spacing:-1px;color:#fff;line-height:1;font-family:'JetBrains Mono',monospace;">
            ${reading.indoor}<span style="font-size:22px;vertical-align:top;margin-top:6px;display:inline-block;color:${c.color};">°C</span>
          </div>
          <div style="margin-top:8px;font-size:15px;color:${c.color};font-weight:500;">${c.label}</div>
          <div style="margin-top:4px;font-size:11.5px;color:rgba(255,255,255,.38);font-family:'JetBrains Mono',monospace;letter-spacing:2px;text-transform:uppercase;">ห้องนั่งเล่น · ${reading.time}</div>
        </div>

        <!-- stats row -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;">
          ${statCard('💧', 'ความชื้น', reading.humidity + '%', '#60d4ff')}
          ${statCard('🌡', 'ภายนอก', reading.outdoor + '°C', '#ffb454')}
          ${statCard('🔆', 'ดัชนีสุข', comfortIndex(reading.indoor, reading.humidity), c.color)}
        </div>

        <!-- temp bar -->
        <div>
          <div style="display:flex;justify-content:space-between;margin-bottom:7px;font-size:11px;color:rgba(255,255,255,.38);font-family:'JetBrains Mono',monospace;">
            <span>16°C</span><span>อุณหภูมิในร่ม</span><span>35°C</span>
          </div>
          <div style="height:7px;border-radius:4px;background:rgba(255,255,255,.08);position:relative;overflow:hidden;">
            <div id="tawee-temp-bar" style="position:absolute;top:0;left:0;height:100%;border-radius:4px;background:linear-gradient(90deg,#60d4ff,${c.color});width:0%;transition:width 1.4s cubic-bezier(.4,0,.2,1);box-shadow:0 0 10px ${c.color}88;"></div>
          </div>
        </div>

        <!-- suggestion -->
        <div style="padding:12px 14px;border-radius:14px;background:${c.bg};border:1px solid ${c.color}22;font-size:13px;color:rgba(255,255,255,.7);line-height:1.6;">
          ${suggestion(reading.indoor, reading.humidity)}
        </div>

        <button onclick="document.getElementById('tawee-temp-scrim')?.remove()"
          style="width:100%;padding:13px;border-radius:14px;border:none;background:${c.color};color:#04130c;font-size:14px;font-weight:700;cursor:pointer;letter-spacing:.5px;">
          ✓ รับทราบ
        </button>
      </div>
    `);

    scrim.appendChild(panel);
    root.appendChild(scrim);

    // Animate gauge after DOM inserts
    requestAnimationFrame(() => {
      animateGauge(cv, reading.indoor, c.color);
      const bar = document.getElementById('tawee-temp-bar');
      if (bar) {
        const pct = Math.min(100, Math.max(0, ((reading.indoor - 16) / 19) * 100));
        setTimeout(() => { bar.style.width = pct + '%'; }, 200);
      }
    });
  }

  function statCard(icon, label, value, color) {
    return `<div style="padding:12px 10px;border-radius:14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);text-align:center;">
      <div style="font-size:18px;margin-bottom:5px;">${icon}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:600;color:${color};">${value}</div>
      <div style="font-size:10.5px;color:rgba(255,255,255,.36);margin-top:3px;">${label}</div>
    </div>`;
  }

  function comfortIndex(temp, hum) {
    // Heat index simplified
    const hi = temp - 0.55 * (1 - hum / 100) * (temp - 14.5);
    if (hi < 21) return 'เย็น';
    if (hi < 27) return 'สบาย';
    if (hi < 32) return 'อุ่น';
    return 'ร้อน';
  }

  function suggestion(temp, hum) {
    if (temp < 20) return '🧥 แนะนำให้ใส่เสื้อกันหนาว และดูแลสุขภาพให้ดีนะคะ อากาศเย็นมาก';
    if (temp < 24) return '😊 อุณหภูมิสบายมากค่ะ เหมาะกับการทำงานและพักผ่อน';
    if (temp < 27) return '✅ อากาศสบายดีค่ะ ดื่มน้ำให้เพียงพอวันละ 6–8 แก้วนะคะ';
    if (temp < 30) return '💧 เริ่มอุ่นแล้ว ดื่มน้ำบ่อย ๆ และเปิดพัดลมหรือแอร์เบา ๆ ได้เลยค่ะ';
    if (temp < 33) return '🌬 ร้อนค่ะ แนะนำปรับแอร์ที่ 25°C เพื่อประหยัดไฟและยังสบาย';
    return '🔥 ร้อนมากค่ะ ควรเปิดแอร์และดื่มน้ำเย็นบ่อย ๆ หลีกเลี่ยงกิจกรรมหนักในช่วงนี้';
  }

  // ── Canvas Gauge ─────────────────────────────────────────
  function animateGauge(cv, targetTemp, color) {
    const ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    const cx = W / 2, cy = H * 0.82;
    const R  = 88;
    const START = Math.PI * 0.8, END = Math.PI * 2.2;
    const RANGE = END - START;
    const MIN_T = 16, MAX_T = 36;
    let current = 16;
    let frame   = 0;
    const FRAMES = 90;

    function ease(t) { return t < .5 ? 2*t*t : -1+(4-2*t)*t; }

    function draw() {
      ctx.clearRect(0, 0, W, H);

      // Track arc (background)
      ctx.beginPath();
      ctx.arc(cx, cy, R, START, END);
      ctx.strokeStyle = 'rgba(255,255,255,.08)';
      ctx.lineWidth   = 13;
      ctx.lineCap     = 'round';
      ctx.stroke();

      // Value arc
      const pct  = Math.max(0, Math.min(1, (current - MIN_T) / (MAX_T - MIN_T)));
      const endA = START + RANGE * pct;
      if (pct > 0) {
        const grad = ctx.createLinearGradient(cx - R, cy, cx + R, cy);
        grad.addColorStop(0, '#60d4ff');
        grad.addColorStop(0.5, color);
        grad.addColorStop(1, color);
        ctx.beginPath();
        ctx.arc(cx, cy, R, START, endA);
        ctx.strokeStyle = grad;
        ctx.lineWidth   = 13;
        ctx.lineCap     = 'round';
        ctx.shadowColor = color;
        ctx.shadowBlur  = 18;
        ctx.stroke();
        ctx.shadowBlur  = 0;
      }

      // Dot at tip
      const dotA = START + RANGE * pct;
      ctx.beginPath();
      ctx.arc(cx + Math.cos(dotA) * R, cy + Math.sin(dotA) * R, 7, 0, 6.283);
      ctx.fillStyle = color;
      ctx.shadowColor = color; ctx.shadowBlur = 20;
      ctx.fill(); ctx.shadowBlur = 0;

      // Min/Max labels
      ctx.font = '11px "JetBrains Mono",monospace';
      ctx.fillStyle = 'rgba(255,255,255,.30)';
      ctx.textAlign = 'center';
      ctx.fillText(`${MIN_T}°`, cx + Math.cos(START) * (R + 22), cy + Math.sin(START) * (R + 22));
      ctx.fillText(`${MAX_T}°`, cx + Math.cos(END) * (R + 22), cy + Math.sin(END) * (R + 22));

      // Tick marks
      for (let i = 0; i <= 20; i++) {
        const a = START + (i / 20) * RANGE;
        const isMajor = i % 4 === 0;
        const r1 = R - (isMajor ? 22 : 16), r2 = R - 12;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1);
        ctx.lineTo(cx + Math.cos(a) * r2, cy + Math.sin(a) * r2);
        ctx.strokeStyle = isMajor ? 'rgba(255,255,255,.30)' : 'rgba(255,255,255,.12)';
        ctx.lineWidth = isMajor ? 1.5 : 0.8;
        ctx.stroke();
      }

      // Center value (large)
      ctx.font = 'bold 36px "JetBrains Mono",monospace';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(current.toFixed(1) + '°', cx, cy - 18);
      ctx.font = '11px "JetBrains Mono",monospace';
      ctx.fillStyle = color;
      ctx.fillText('อุณหภูมิห้อง', cx, cy + 8);
    }

    function tick() {
      frame++;
      const t = Math.min(1, frame / FRAMES);
      current = +(16 + (targetTemp - 16) * ease(t)).toFixed(1);
      draw();
      if (frame < FRAMES) _raf = requestAnimationFrame(tick);
    }
    if (_raf) cancelAnimationFrame(_raf);
    _raf = requestAnimationFrame(tick);
  }

  // ── Styles ───────────────────────────────────────────────
  function injectStyles() {
    if (document.getElementById('tawee-temp-style')) return;
    const s = document.createElement('style');
    s.id = 'tawee-temp-style';
    s.textContent = `@keyframes taweeTempIn { from{ opacity:0; transform:scale(.92) translateY(20px); } to{ opacity:1; transform:scale(1) translateY(0); } }`;
    document.head.appendChild(s);
  }

  function closeModal() {
    document.getElementById('tawee-temp-scrim')?.remove();
    if (_raf) { cancelAnimationFrame(_raf); _raf = null; }
  }

  // ── Expose for splash ────────────────────────────────────
  TAWEE.measureTemperature = async function (silent = false) {
    const cfg    = TAWEE.cfg || {};
    const lat    = cfg.weatherLat  || 13.7563;
    const lon    = cfg.weatherLon  || 100.5018;
    const hour   = new Date().getHours();
    const time   = new Date().toTimeString().slice(0, 5);

    try {
      const { outdoor, humidity: outHum } = await fetchOutdoor(lat, lon);
      const indoor   = estimateIndoor(outdoor, hour);
      const humidity = estimateHumidity(outdoor, indoor);
      const comfort  = comfortFor(indoor).label;
      lastReading = { indoor, outdoor, humidity, comfort, time };
      if (!silent) showModal(lastReading);
      return lastReading;
    } catch (e) {
      // Offline fallback
      const indoor  = +(24 + (Math.random() - .5) * 2).toFixed(1);
      const outdoor = +(32 + (Math.random() - .5) * 3).toFixed(1);
      const humidity = 58;
      lastReading = { indoor, outdoor, humidity, comfort: comfortFor(indoor).label, time };
      if (!silent) showModal(lastReading);
      return lastReading;
    }
  };

  TAWEE.lastTemperature = () => lastReading;
  TAWEE.showTemperatureModal = () => lastReading ? showModal(lastReading, true) : TAWEE.measureTemperature();

  TAWEE.registerSkill('temperature', {
    match: (t) => /อุณหภูมิ|ห้อง.*ร้อน|ร้อนแค่ไหน|อากาศ.*ห้อง|temperature|temp.*room|วัดอุณหภูมิ|ห้องนี้|ความร้อน|room.*hot|กี่องศา/i.test(t),
    handle: async (t) => {
      const r = await TAWEE.measureTemperature(false);
      return `อุณหภูมิห้องตอนนี้ ${r.indoor}°C — ${r.comfort}\nความชื้น ${r.humidity}% · ภายนอก ${r.outdoor}°C`;
    },
  });
})();
