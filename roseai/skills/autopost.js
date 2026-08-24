'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Auto Post Skill  |  skills/autopost.js
// พูด/พิมพ์ "สร้างโพสต์ <หัวข้อ>" — TAWEE จะเขียนบทความด้วย Claude แล้วโพสต์
// ขึ้น Facebook Page ให้อัตโนมัติ ใช้ Facebook Page Access Token ที่บันทึกไว้
// จากหน้า AI Agent Dashboard > API Settings (localStorage: tawee_fb_t) — โพสต์
// ผ่าน /me/feed เพราะ Page token เองก็บอกอยู่แล้วว่าเป็นเพจไหน ไม่ต้องใช้ Page ID
// และ Claude API key ที่ตั้งไว้ในหน้า TAWEE เอง
// ═══════════════════════════════════════════════════════════
(function () {
  const MATCH_RE = /^(?:ช่วย)?(?:สร้าง|เขียน)?(?:บทความ)?โพสต์(?:เรื่อง|ให้หน่อย|เกี่ยวกับ)?\s*[:\-]?\s*(.+)/i;

  function extractTopic(text) {
    const m = text.match(MATCH_RE);
    if (!m || !m[1]) return '';
    return m[1].trim().replace(/^["'“”]+|["'“”]+$/g, '').trim();
  }

  async function writeArticle(topic, cfg) {
    const target = TAWEE._apiTarget();
    const res = await fetch(target.url, {
      method: 'POST',
      headers: { 'content-type': 'application/json', ...target.headers },
      body: JSON.stringify({
        model: cfg.model,
        max_tokens: 800,
        messages: [{
          role: 'user',
          content: 'เขียนบทความโพสต์โซเชียลมีเดียภาษาไทยสำหรับหัวข้อ: ' + topic +
            '\nให้สั้น กระชับ น่าสนใจ เหมาะกับ Facebook ห้ามใช้เครื่องหมาย * หรือ # และห้ามใช้อิโมจิเด็ดขาด ใช้ได้แค่ตัวอักษรและตัวเลขเท่านั้น',
        }],
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error((data.error && data.error.message) || 'HTTP ' + res.status);
    return (data.content?.[0]?.text || '').trim();
  }

  async function postToFacebook(message, token) {
    const res = await fetch('https://graph.facebook.com/me/feed', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ access_token: token, message }),
    });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error((data.error && data.error.message) || 'HTTP ' + res.status);
    return data.id;
  }

  TAWEE.registerSkill('autopost', {
    match: (t) => MATCH_RE.test(t),
    handle: async (t, text, cfg) => {
      const topic = extractTopic(text);
      if (!topic) return 'บอกหัวข้อที่จะให้เขียนโพสต์ด้วยนะคะ เช่น สร้างโพสต์ โปรโมชั่นสิ้นปี';
      if (!TAWEE.hasApiAccess()) return 'กรุณาใส่ Claude API key ในหน้าตั้งค่าของ TAWEE ก่อนนะคะ';

      const fbToken = localStorage.getItem('tawee_fb_t');
      if (!fbToken) return 'กรุณาตั้งค่า Facebook Page Access Token ที่หน้า Dashboard เมนู API Settings ก่อนนะคะ';

      let article;
      try {
        article = await writeArticle(topic, cfg);
      } catch (e) {
        return 'เขียนบทความไม่สำเร็จค่ะ: ' + e.message;
      }
      if (!article) return 'เขียนบทความไม่สำเร็จค่ะ ลองใหม่อีกครั้งนะคะ';

      try {
        await postToFacebook(article, fbToken);
      } catch (e) {
        return 'เขียนบทความเสร็จแล้ว แต่โพสต์ขึ้น Facebook ไม่สำเร็จค่ะ ' + e.message + '\n\nบทความที่เขียนไว้:\n' + article;
      }
      return 'โพสต์เรื่อง ' + topic + ' ขึ้น Facebook ให้เรียบร้อยแล้วค่ะ\n\n' + article;
    },
  });
})();
