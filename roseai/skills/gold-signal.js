// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Gold Trading Signal Skill  |  skills/gold-signal.js
// พูด/พิมพ์ "สัญญาณทองคำ" หรือ "เช็คสัญญาณเทรด" เพื่อคำนวณ MACD ของทองคำ (XAU/USD) ตอนนี้ทันที
// แล้วส่งเข้า LINE เสมอ (ต่างจาก cron อัตโนมัติทุก 15 นาทีที่ส่งเฉพาะตอนตัดกันจริง)
// คำนวณจริงฝั่ง tawee-proxy (Worker) เพราะ Kraken/Binance บาง endpoint บล็อก CORS จาก browser
// ─────────────────────────────────────────────────────────────
(function () {
  'use strict';

  function getProxyConfig() {
    try {
      const cfg = JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}');
      return { url: cfg.proxyUrl || '', secret: cfg.proxySecret || '' };
    } catch (e) { return { url: '', secret: '' }; }
  }

  async function checkGoldSignalNow() {
    const { url, secret } = getProxyConfig();
    if (!url || !secret) throw new Error('ยังไม่ได้ตั้งค่า Cloudflare Worker Proxy ในหน้าตั้งค่า');
    const res = await fetch(`${url}/check-gold-signal`, {
      method: 'POST',
      headers: { 'x-tawee-secret': secret },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data; // { trend, price, signal }
  }

  const MATCH_RE = /สัญญาณ.*(ทอง|เทรด|xau|gold)|(ทอง|เทรด|xau|gold).*สัญญาณ|เช็ค.*สัญญาณ/i;

  TAWEE.registerSkill('gold-signal', {
    match: (t) => MATCH_RE.test(t),
    handle: async () => {
      try {
        const { trend, price, signal } = await checkGoldSignalNow();
        const label = trend === 'bullish' ? 'BUY 🟢 (ขาขึ้น)' : 'SELL 🔴 (ขาลง)';
        return `✅ เช็คสัญญาณทองคำแล้ว ส่งเข้าไลน์ให้ด้วยค่ะ\n\nสัญญาณ: ${label}\nราคา: $${price.toFixed(2)}`;
      } catch (e) {
        return '❌ เช็คสัญญาณทองคำไม่สำเร็จ: ' + e.message;
      }
    },
  });

  TAWEE.goldSignal = { checkNow: checkGoldSignalNow };
})();
