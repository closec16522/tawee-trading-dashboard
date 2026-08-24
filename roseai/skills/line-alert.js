// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — LINE Price Alert Skill  |  skills/line-alert.js
// พูด/พิมพ์ "เปิดแจ้งเตือนราคาไลน์" เพื่อเริ่มเช็คราคาทุก 1 ชม. แล้วส่งเข้า LINE
// พูด/พิมพ์ "ปิดแจ้งเตือนราคาไลน์" เพื่อหยุด
// พูด/พิมพ์ "เช็คราคาคริปโต" เพื่อทดสอบยิงทันที 1 ครั้ง
//
// ══════════════════════════════════════════════════════════════
// ⚠️ Worker URL/secret ไม่ฝังตายตัวในไฟล์นี้ — อ่านจากค่าที่ผู้ใช้กรอกไว้ในหน้าตั้งค่า
//    (tawee_cfg_v3.proxyUrl / proxySecret) หลัง deploy tawee-proxy (Cloudflare Worker) ของตัวเองแล้ว
//    ถ้ายังไม่ตั้งค่า จะ fallback ไปยิงตรงจาก browser ด้วย LINE_TOKEN/LINE_USER_ID ด้านล่าง
//    (ใช้ไม่ได้จริงเพราะ LINE ปิด CORS — เว้นไว้เผื่อทดสอบผ่าน proxy อื่นเอง)
// ══════════════════════════════════════════════════════════════
(function () {
  'use strict';

  // ═══ โหมดสำรอง: ยิงตรงจาก browser (ปกติใช้ไม่ได้จริงเพราะ LINE ปิด CORS) ═══
  const LINE_TOKEN     = '';
  const LINE_USER_ID   = '';

  // URL/secret ของ Worker ไม่ฝังตายตัว — อ่านจากค่าที่ผู้ใช้กรอกไว้ในหน้าตั้งค่า (tawee_cfg_v3.proxyUrl/proxySecret)
  function getProxyConfig() {
    try {
      const cfg = JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}');
      return { url: cfg.proxyUrl || '', secret: cfg.proxySecret || '' };
    } catch (e) { return { url: '', secret: '' }; }
  }

  const CHECK_INTERVAL_MS = 60 * 60 * 1000; // 1 ชั่วโมง
  const LS_ENABLED_KEY = 'tawee_line_alert_enabled';
  const LS_ASSETS_KEY  = 'tawee_line_alert_assets';

  // ═══ สินทรัพย์ที่ติดตาม ═══
  // ตอนนี้มีแหล่งราคาฟรีที่ยิงตรงจาก browser ได้ชัวร์แค่ BTC (Binance public API)
  // หุ้น/ทอง/SET ยังไม่มี API ฟรีที่เปิด CORS ให้ browser เรียกตรงได้ — ต้องรอ
  // ต่อผ่าน tawee-proxy (ฝั่ง server เรียก API ที่มี key แล้วส่งกลับมาแทน)
  const ASSETS = [
    { id: 'BTC', label: 'Bitcoin', fetcher: fetchBinancePrice('BTCUSDT'), unit: 'USD' },
    // เพิ่มได้เมื่อมี API ฝั่ง proxy พร้อม เช่น:
    // { id: 'XAU', label: 'ทองคำ',  fetcher: fetchViaProxy('XAU'), unit: 'USD' },
    // { id: 'NVDA',label: 'Nvidia', fetcher: fetchViaProxy('NVDA'), unit: 'USD' },
  ];

  let timerId = null;
  let lastPrices = {}; // เก็บราคาครั้งก่อนไว้เทียบ ขึ้น/ลง

  // ─────────────────────────────────────────────────────────
  // ราคา — Binance public API (ไม่ต้องมี key, เปิด CORS ให้ browser เรียกตรงได้)
  // ─────────────────────────────────────────────────────────
  function fetchBinancePrice(symbol) {
    return async function () {
      const res  = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}`);
      if (!res.ok) throw new Error('Binance API error ' + res.status);
      const data = await res.json();
      return parseFloat(data.price);
    };
  }

  // เผื่ออนาคตย้ายไปดึงผ่าน proxy (รองรับหุ้น/ทอง/SET ที่ต้องมี API key)
  function fetchViaProxy(assetId) {
    return async function () {
      const { url } = getProxyConfig();
      if (!url) throw new Error('ยังไม่ได้ตั้งค่า Worker URL ในหน้าตั้งค่า');
      const res  = await fetch(`${url}/price?asset=${assetId}`);
      if (!res.ok) throw new Error('Proxy price error ' + res.status);
      const data = await res.json();
      return parseFloat(data.price);
    };
  }

  // ─────────────────────────────────────────────────────────
  // แนวรับ/แนวต้าน จาก Bitcoin Options Open Interest (Deribit public API)
  // โลจิกเดียวกับ _computeOIWalls ใน Finance AI Dashboard.dc.html
  // ─────────────────────────────────────────────────────────
  async function fetchBTCOIWalls(price) {
    const res = await fetch('https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option');
    if (!res.ok) throw new Error('Deribit API error ' + res.status);
    const data = await res.json();
    const byStrike = {};
    (data.result || []).forEach(o => {
      const parts  = o.instrument_name.split('-'); // BTC-12JUL26-59000-C
      const strike = +parts[2];
      if (!strike) return;
      const isCall = parts[3] === 'C';
      const oi = o.open_interest || 0;
      if (!byStrike[strike]) byStrike[strike] = { strike, call: 0, put: 0 };
      byStrike[strike][isCall ? 'call' : 'put'] += oi;
    });
    const strikes = Object.values(byStrike);
    const resistances = strikes.filter(s => s.strike > price).sort((a, b) => b.call - a.call).slice(0, 2);
    const supports    = strikes.filter(s => s.strike < price).sort((a, b) => b.put - a.put).slice(0, 2);
    return { resistances, supports };
  }

  // ─────────────────────────────────────────────────────────
  // แท่งเทียน BTC (Binance) ไว้วาดรูปกราฟส่งแนบเข้า LINE
  // ─────────────────────────────────────────────────────────
  async function fetchBTCCandles(limit) {
    const res = await fetch(`https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=4h&limit=${limit}`);
    if (!res.ok) throw new Error('Binance klines error ' + res.status);
    const raw = await res.json();
    return raw.map(k => ({ o: +k[1], h: +k[2], l: +k[3], c: +k[4] }));
  }

  // วาดกราฟแท่งเทียน + เส้นแนวรับ/แนวต้าน OI ลงบน canvas แล้วคืนเป็น PNG base64 (ไม่มี prefix data:)
  function renderBTCChartImage(candles, walls, price) {
    const W = 800, H = 450, PAD = 46;
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#0b0f17';
    ctx.fillRect(0, 0, W, H);

    const wallVals = [...walls.resistances, ...walls.supports].map(w => w.strike);
    const allVals  = candles.flatMap(c => [c.h, c.l]).concat(wallVals, [price]);
    const lo = Math.min(...allVals), hi = Math.max(...allVals);
    const range = (hi - lo) || 1;
    const y = (v) => PAD + (H - PAD * 2) * (1 - (v - lo) / range);

    const n = candles.length;
    const cw = (W - PAD * 2) / n;
    candles.forEach((c, i) => {
      const x = PAD + i * cw + cw / 2;
      const up = c.c >= c.o;
      ctx.strokeStyle = ctx.fillStyle = up ? '#22c55e' : '#ef4444';
      ctx.beginPath();
      ctx.moveTo(x, y(c.h));
      ctx.lineTo(x, y(c.l));
      ctx.stroke();
      const bodyTop = y(Math.max(c.o, c.c));
      const bodyBot = y(Math.min(c.o, c.c));
      ctx.fillRect(x - cw * 0.3, bodyTop, cw * 0.6, Math.max(1, bodyBot - bodyTop));
    });

    function drawLevel(v, color, label) {
      const yy = y(v);
      ctx.strokeStyle = color;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(PAD, yy);
      ctx.lineTo(W - PAD, yy);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = color;
      ctx.font = '12px sans-serif';
      ctx.fillText(`${label} ${v.toLocaleString()}`, W - PAD - 150, yy - 4);
    }
    walls.resistances.forEach((w, i) => drawLevel(w.strike, '#f87171', `R${i + 1}`));
    walls.supports.forEach((w, i) => drawLevel(w.strike, '#4ade80', `S${i + 1}`));

    ctx.strokeStyle = '#60a5fa';
    ctx.setLineDash([2, 3]);
    ctx.beginPath();
    ctx.moveTo(PAD, y(price));
    ctx.lineTo(W - PAD, y(price));
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#e5e7eb';
    ctx.font = 'bold 16px sans-serif';
    ctx.fillText(`BTC/USD  ${price.toLocaleString()}`, PAD, 26);

    return canvas.toDataURL('image/png').split(',')[1];
  }

  // ─────────────────────────────────────────────────────────
  // อัพโหลดรูปผ่าน local-proxy (proxy ไปฝากที่ catbox.moe แล้วคืน public URL กลับมา)
  // ─────────────────────────────────────────────────────────
  async function uploadChartImage(imageBase64) {
    const { url } = getProxyConfig();
    if (!url) throw new Error('ยังไม่ได้ตั้งค่า Worker URL ในหน้าตั้งค่า');
    const res = await fetch(`${url}/upload-image`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ imageBase64 }),
    });
    const data = await res.json();
    if (!res.ok || !data.url) throw new Error(data.error || 'upload failed');
    return data.url;
  }

  // ─────────────────────────────────────────────────────────
  // ยิงเข้า LINE
  // ─────────────────────────────────────────────────────────
  async function sendLineAlert(message, imageUrl) {
    const { url, secret } = getProxyConfig();
    if (url && secret) {
      // โหมดปลอดภัย — ผ่าน tawee-proxy (token ซ่อนอยู่ฝั่ง server)
      return fetch(`${url}/line-push`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-tawee-secret': secret },
        body: JSON.stringify({ message, imageUrl }),
      });
    }
    // โหมดทดสอบ — ยิงตรงจาก browser
    if (!LINE_TOKEN || !LINE_USER_ID) {
      throw new Error('ยังไม่ได้ตั้งค่า LINE_TOKEN / LINE_USER_ID ในไฟล์ line-alert.js');
    }
    const messages = [{ type: 'text', text: message }];
    if (imageUrl) messages.push({ type: 'image', originalContentUrl: imageUrl, previewImageUrl: imageUrl });
    return fetch('https://api.line.me/v2/bot/message/push', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'Authorization': 'Bearer ' + LINE_TOKEN,
      },
      body: JSON.stringify({ to: LINE_USER_ID, messages }),
    });
  }

  // ─────────────────────────────────────────────────────────
  // เช็คราคาทุกตัว แล้วประกอบข้อความส่งเข้า LINE
  // ─────────────────────────────────────────────────────────
  async function checkAndAlert() {
    const lines = [];
    let chartImageBase64 = null;

    for (const asset of ASSETS) {
      try {
        const price = await asset.fetcher();
        const prev  = lastPrices[asset.id];
        let trend = '';
        if (prev != null) {
          if (price > prev) trend = ' 🔺';
          else if (price < prev) trend = ' 🔻';
          else trend = ' ➖';
        }
        lastPrices[asset.id] = price;
        lines.push(`${asset.label}: ${price.toLocaleString()} ${asset.unit}${trend}`);

        if (asset.id === 'BTC') {
          try {
            const walls = await fetchBTCOIWalls(price);
            const fmt = (s) => s ? `${s.strike.toLocaleString()} USD` : 'ไม่มีข้อมูล';
            lines.push(`แนวต้าน OI 1 : ${fmt(walls.resistances[0])}`);
            lines.push(`แนวต้าน OI 2 : ${fmt(walls.resistances[1])}`);
            lines.push(`แนวรับ OI 1 : ${fmt(walls.supports[0])}`);
            lines.push(`แนวรับ OI 2 : ${fmt(walls.supports[1])}`);

            try {
              const candles = await fetchBTCCandles(60);
              chartImageBase64 = renderBTCChartImage(candles, walls, price);
            } catch (e) {
              console.error('[line-alert] วาดกราฟไม่สำเร็จ:', e.message);
            }
          } catch (e) {
            lines.push(`แนวรับ/แนวต้าน OI: ดึงข้อมูลไม่สำเร็จ (${e.message})`);
          }
        }
      } catch (e) {
        lines.push(`${asset.label}: ดึงราคาไม่สำเร็จ (${e.message})`);
      }
    }

    const now = new Date();
    const timeStr = now.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
    const message =
      `📊 อัปเดตราคาสินทรัพย์ (${timeStr})\n` +
      `━━━━━━━━━━━━━━━━\n` +
      lines.join('\n');

    try {
      let imageUrl = null;
      if (chartImageBase64) {
        try {
          imageUrl = await uploadChartImage(chartImageBase64);
        } catch (e) {
          console.error('[line-alert] อัพโหลดรูปไม่สำเร็จ:', e.message);
        }
      }
      await sendLineAlert(message, imageUrl);
    } catch (e) {
      console.error('[line-alert] ส่งเข้า LINE ไม่สำเร็จ:', e.message);
    }
    return message;
  }

  // ─────────────────────────────────────────────────────────
  // เปิด / ปิด การเช็คอัตโนมัติทุก 1 ชม.
  // ─────────────────────────────────────────────────────────
  function startAutoCheck() {
    if (timerId) return; // ทำงานอยู่แล้ว
    timerId = setInterval(checkAndAlert, CHECK_INTERVAL_MS);
    try { localStorage.setItem(LS_ENABLED_KEY, '1'); } catch (e) {}
  }

  function stopAutoCheck() {
    if (timerId) { clearInterval(timerId); timerId = null; }
    try { localStorage.setItem(LS_ENABLED_KEY, '0'); } catch (e) {}
  }

  function isEnabled() {
    try { return localStorage.getItem(LS_ENABLED_KEY) === '1'; } catch (e) { return false; }
  }

  // โหลดหน้าเว็บใหม่ (F5) แล้วยังจำสถานะเดิมไว้ — ถ้าเคยเปิดไว้ ให้เริ่มเช็คต่ออัตโนมัติ
  if (isEnabled()) startAutoCheck();

  // ─────────────────────────────────────────────────────────
  // ลงทะเบียน Skill
  // ─────────────────────────────────────────────────────────
  const ON_RE    = /เปิด.*(แจ้งเตือน|เตือน).*(ไลน์|line)|(ไลน์|line).*(แจ้งเตือน|เตือน).*เปิด/i;
  const OFF_RE   = /ปิด.*(แจ้งเตือน|เตือน).*(ไลน์|line)|(ไลน์|line).*(แจ้งเตือน|เตือน).*ปิด/i;
  const NOW_RE   = /เช็คราคา.*(เดี๋ยวนี้|ตอนนี้)|ทดสอบ.*(ไลน์|line)|ส่งราคา.*(ไลน์|line)/i;
  const MATCH_RE = new RegExp(ON_RE.source + '|' + OFF_RE.source + '|' + NOW_RE.source, 'i');

  TAWEE.registerSkill('line-alert', {
    match: (t) => MATCH_RE.test(t),
    handle: async (t) => {
      if (OFF_RE.test(t)) {
        stopAutoCheck();
        return '❌ ปิดแจ้งเตือนราคาผ่านไลน์แล้วค่ะ';
      }
      if (NOW_RE.test(t)) {
        const msg = await checkAndAlert();
        return '✅ ส่งราคาเข้าไลน์ให้แล้วค่ะ\n\n' + msg;
      }
      // default: เปิด
      if (timerId) return 'แจ้งเตือนราคาเปิดอยู่แล้วค่ะ (เช็คทุก 1 ชั่วโมง)';
      startAutoCheck();
      checkAndAlert(); // ยิงทันที 1 ครั้งแรกให้เห็นผลเลย ไม่ต้องรอครบชั่วโมง
      return '✅ เปิดแจ้งเตือนราคาผ่านไลน์แล้วค่ะ จะอัปเดตให้ทุก 1 ชั่วโมง';
    },
  });

  // เผื่ออยากเรียกจากที่อื่นในโค้ด (เช่นปุ่มในหน้า settings)
  TAWEE.lineAlert = { start: startAutoCheck, stop: stopAutoCheck, checkNow: checkAndAlert, isEnabled };
})();