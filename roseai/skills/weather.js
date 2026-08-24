// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Weather Skill
// Uses Open-Meteo (free, no API key required)
// ─────────────────────────────────────────────────────────────
(function () {
  const WMO = {
    0:'แจ่มใส ☀️', 1:'มีเมฆบางส่วน 🌤', 2:'เมฆครึ้ม 🌥', 3:'มีเมฆมาก ☁️',
    45:'หมอกลง 🌫', 48:'หมอกน้ำแข็ง 🌫',
    51:'ฝนละอองเบา 🌦', 53:'ฝนละออง 🌦', 55:'ฝนละอองหนัก 🌧',
    61:'ฝนเบา 🌧', 63:'ฝนปานกลาง 🌧', 65:'ฝนหนัก 🌧',
    71:'หิมะเบา 🌨', 73:'หิมะ 🌨', 75:'หิมะหนัก ❄️',
    80:'ฝนฝนหน้า 🌦', 81:'ฝน 🌧', 82:'ฝนหนักมาก ⛈',
    95:'พายุฝนฟ้าคะนอง ⛈', 96:'พายุลูกเห็บ 🌩', 99:'พายุรุนแรง 🌩',
  };

  const HUMIDITY_LABEL = (h) => h < 40 ? 'แห้ง' : h < 60 ? 'สบาย' : h < 80 ? 'ชื้น' : 'ชื้นมาก';
  const WIND_LABEL     = (w) => w < 10 ? 'สงบ' : w < 30 ? 'ลมเบา' : w < 60 ? 'ลมแรง' : 'ลมกระโชก';

  TAWEE.registerSkill('weather', {
    match: (t) => /อากาศ|ฝน|ร้อน|หนาว|ลม|พยากรณ์|weather|forecast|temp|degree|องศา|ความชื้น|humidity/i.test(t),
    handle: async (t, raw, cfg) => {
      const lat  = cfg.weatherLat  || 13.7563;
      const lon  = cfg.weatherLon  || 100.5018;
      const city = cfg.weatherCity || 'กรุงเทพฯ';

      const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}`
        + `&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,precipitation`
        + `&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code`
        + `&wind_speed_unit=kmh&temperature_unit=celsius&timezone=Asia%2FBangkok&forecast_days=3`;

      const res  = await fetch(url);
      const data = await res.json();
      const cur  = data.current;
      const day  = data.daily;

      const cond = WMO[cur.weather_code] || 'ไม่ทราบ';

      let reply =
        `🌍 อากาศ${city} ตอนนี้\n` +
        `━━━━━━━━━━━━━━━━\n` +
        `${cond}\n` +
        `🌡 ${cur.temperature_2m}°C (รู้สึกเหมือน ${cur.apparent_temperature}°C)\n` +
        `💧 ความชื้น ${cur.relative_humidity_2m}% — ${HUMIDITY_LABEL(cur.relative_humidity_2m)}\n` +
        `💨 ลม ${cur.wind_speed_10m} กม./ชม. — ${WIND_LABEL(cur.wind_speed_10m)}\n`;

      if (cur.precipitation > 0) reply += `🌧 ปริมาณฝน ${cur.precipitation} มม.\n`;

      // 3-day forecast
      if (day && day.time) {
        reply += `\n📅 พยากรณ์ 3 วัน\n`;
        const dayNames = ['อา','จ','อ','พ','พฤ','ศ','ส'];
        for (let i = 0; i < Math.min(3, day.time.length); i++) {
          const d = new Date(day.time[i]);
          const name = i === 0 ? 'วันนี้' : i === 1 ? 'พรุ่งนี้' : dayNames[d.getDay()] + '. ' + d.getDate();
          const cnd  = WMO[day.weather_code[i]] || '—';
          reply += `• ${name}: ${day.temperature_2m_min[i]}–${day.temperature_2m_max[i]}°C ${cnd}`;
          if (day.precipitation_sum[i] > 0) reply += ` ฝน ${day.precipitation_sum[i]} มม.`;
          reply += '\n';
        }
      }
      return reply.trim();
    },
  });
})();
