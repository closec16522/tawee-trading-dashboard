'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Dashboard Navigation Skill  |  skills/dashboard.js
// พูด/พิมพ์ "เปิด dashboard" หรือ "เปิดแดชบอร์ด" เพื่อไปที่ AI Agent Dashboard
// (agent โพสต์) หรือพูด "เปิดการเงิน" / "เปิด dashboard การเงิน" เพื่อไปที่
// Agent สายการเงิน (หน้านั้นจะอ่านสรุปข่าว 5 หัวข้อให้ฟังเองหลังเปิดขึ้นมา)
// หรือพูด "ไปหน้าโพสต์" / "เปิดหน้าโพสต์" เพื่อไปที่ agent โพสต์ (Facebook Post) โดยตรง
// ═══════════════════════════════════════════════════════════
(function () {
  const DASH_RE = /dashboard|แดชบอร์ด|แผงควบคุม/i;
  const FINANCE_RE = /การเงิน|finance|หุ้น|เทรด|ลงทุน/i;
  const OPEN_FINANCE_RE = /เปิด.*(การเงิน|finance|หุ้น|เทรด|ลงทุน)/i;
  const POST_RE = /โพสต์|โพส|เฟซบุ๊ก|facebook/i;
  const OPEN_POST_RE = /(ไป|เปิด).*(หน้า)?\s*(โพสต์|โพส|เฟซบุ๊ก|facebook)/i;
  const MATCH_RE = new RegExp(DASH_RE.source + '|' + OPEN_FINANCE_RE.source + '|' + OPEN_POST_RE.source, 'i');

  TAWEE.registerSkill('dashboard', {
    match: (t) => MATCH_RE.test(t),
    handle: async (t) => {
      if (FINANCE_RE.test(t)) {
        TAWEE.openDashboard('finance');
        return 'เปิด Dashboard สายการเงินให้แล้วค่ะ';
      }
      if (POST_RE.test(t)) {
        TAWEE.openDashboard('post', 'facebook');
        return 'เปิดหน้า Agent โพสต์ให้แล้วค่ะ';
      }
      TAWEE.openDashboard('post');
      return 'เปิด Dashboard ให้แล้วค่ะ';
    },
  });
})();
