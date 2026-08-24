// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Email Check Skill  |  skills/email-check.js
// พูด/พิมพ์ "เช็คอีเมล" เพื่อดูหัวข้ออีเมลที่ยังไม่อ่านล่าสุด
// ข้อมูลมาจาก email-bridge/bridge.py ที่ต้องรันค้างไว้บนเครื่อง (เช็ค IMAP จริงทุก 60 วิ ส่งเข้า tawee-proxy)
// ─────────────────────────────────────────────────────────────
(function () {
  'use strict';

  function getProxyConfig() {
    try {
      const cfg = JSON.parse(localStorage.getItem('tawee_cfg_v3') || '{}');
      return { url: cfg.proxyUrl || '', secret: cfg.proxySecret || '' };
    } catch (e) { return { url: '', secret: '' }; }
  }

  async function fetchEmailStatus() {
    const { url, secret } = getProxyConfig();
    if (!url || !secret) throw new Error('ยังไม่ได้ตั้งค่า Cloudflare Worker Proxy ในหน้าตั้งค่า');
    const res = await fetch(`${url}/email-status`, {
      method: 'POST',
      headers: { 'x-tawee-secret': secret },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
    return data;
  }

  const MATCH_RE = /เช็ค.*(อีเมล|email|เมล)|(อีเมล|email|เมล).*(ใหม่|มา)ไหม|มี.*(อีเมล|email|เมล).*ใหม่/i;

  TAWEE.registerSkill('email-check', {
    match: (t) => MATCH_RE.test(t),
    handle: async () => {
      try {
        const data = await fetchEmailStatus();
        if (!data.connected) {
          return '⚠️ ยังไม่ได้เชื่อมต่ออีเมล — เปิด email-bridge/bridge.py ค้างไว้บนเครื่องก่อนนะคะ';
        }
        if (!data.unreadCount) {
          return '✅ ไม่มีอีเมลใหม่ค่ะ อ่านหมดแล้ว';
        }
        const lines = data.emails.slice(0, 8).map((e, i) => `${i + 1}. ${e.subject}${e.from ? ' — ' + e.from : ''}`);
        return `📬 มีอีเมลยังไม่อ่าน ${data.unreadCount} ฉบับค่ะ\n\n` + lines.join('\n');
      } catch (e) {
        return '❌ เช็คอีเมลไม่สำเร็จ: ' + e.message;
      }
    },
  });

  TAWEE.emailCheck = { checkNow: fetchEmailStatus };
})();
