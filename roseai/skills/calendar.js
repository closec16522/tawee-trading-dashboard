// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Calendar & DateTime Skill
// ─────────────────────────────────────────────────────────────
(function () {
  const DAYS   = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const MONTHS = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];
  const MON_S  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const pad    = (n) => String(n).padStart(2, '0');

  function thaiDateTime(d) {
    return `${DAYS[d.getDay()]}, ${MONTHS[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  }

  function thaiTime(d) {
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  function nextHoliday() {
    const now = new Date();
    const yr  = now.getFullYear();
    const holidays = [
      { month:1,  day:1,  name:'New Year\'s Day' },
      { month:4,  day:6,  name:'Chakri Memorial Day' },
      { month:4,  day:13, name:'Songkran Festival' },
      { month:4,  day:14, name:'Songkran Festival (continued)' },
      { month:4,  day:15, name:'Songkran Festival (continued)' },
      { month:5,  day:1,  name:'National Labour Day' },
      { month:5,  day:4,  name:'Coronation Day' },
      { month:5,  day:13, name:'Royal Ploughing Ceremony Day' },
      { month:6,  day:3,  name:'Queen Suthida\'s Birthday' },
      { month:7,  day:28, name:'King Vajiralongkorn\'s Birthday' },
      { month:8,  day:12, name:'National Mother\'s Day' },
      { month:10, day:13, name:'King Bhumibol Memorial Day' },
      { month:10, day:23, name:'Chulalongkorn Day' },
      { month:12, day:5,  name:'National Father\'s Day' },
      { month:12, day:10, name:'Constitution Day' },
      { month:12, day:31, name:'New Year\'s Eve' },
    ];
    for (const h of holidays) {
      let d = new Date(yr, h.month - 1, h.day);
      if (d < now) d = new Date(yr + 1, h.month - 1, h.day);
      h._date = d;
      h._diff = Math.ceil((d - now) / 86400000);
    }
    const next = holidays.sort((a,b) => a._diff - b._diff)[0];
    return next ? `${next.name} — ${next._date.getDate()} ${MON_S[next._date.getMonth()]} (in ${next._diff} days)` : '';
  }

  TAWEE.registerSkill('calendar', {
    // FIX: ตัด countdown ออก เพราะ timer.js จัดการแทนแล้ว
    match: (t) => /\btoday\b|\bdate\b|\btime\b|\bclock\b|\bholiday\b/i.test(t),
    handle: async (t) => {
      const now = new Date();

      if (/\btime\b|\bclock\b/i.test(t)) {
        return `It's ${thaiTime(now)} right now (${thaiDateTime(now)})`;
      }

      if (/holiday/i.test(t)) {
        const next = nextHoliday();
        return next ? `The nearest holiday is ${next}` : 'No holiday information found.';
      }

      if (/countdown/i.test(t)) {
        const endOfYear = new Date(now.getFullYear(), 11, 31);
        const diff = Math.ceil((endOfYear - now) / 86400000);
        return `There are ${diff} days left until the end of ${now.getFullYear()}.`;
      }

      return `${thaiDateTime(now)}\nTime: ${thaiTime(now)}`;
    },
  });
})();