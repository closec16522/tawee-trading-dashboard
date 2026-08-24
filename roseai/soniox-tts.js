// Soniox TTS ใช้ร่วมกันทุกหน้าในโปรเจกต์ TAWEE AI (นอก app.js หลัก — หน้าพวกนี้เป็น standalone ไม่ได้โหลด app.js)
// อ่าน proxyUrl/proxySecret จาก localStorage key เดียวกับหน้าอื่น (tawee_cfg_v3) — ไม่มี fallback ไปเสียงเบราว์เซอร์เด็ดขาด
// ตั้งค่า window.TAWEE_TTS_PAGE = 'ชื่อหน้า' ก่อนโหลดสคริปต์นี้ เพื่อให้ log แยกหน้าได้
(function (global) {
  'use strict';
  var LS_KEY = 'tawee_cfg_v3';
  var ttsToken = 0;
  var ttsChain = Promise.resolve();
  var currentAudio = null;
  var currentAudioUrl = null;
  var lastFailedText = null;
  var toastHideTimer = null;

  function getCfg() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch (e) { return {}; }
  }

  // log โครงสร้าง เก็บแค่ requestId/error name-message/code — ห้ามมีข้อความสนทนาเต็มหรือคีย์ใดๆ
  function log(event, details) {
    var payload = { page: global.TAWEE_TTS_PAGE || 'unknown' };
    for (var k in details) if (details.hasOwnProperty(k)) payload[k] = details[k];
    console.error('[tts:' + event + ']', payload);
  }

  function showFailToast(text) {
    lastFailedText = text;
    var toast = document.getElementById('tawee-tts-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'tawee-tts-toast';
      toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);' +
        'background:#3a1020;color:#fff;padding:10px 18px;border-radius:8px;font-size:14px;' +
        'cursor:pointer;z-index:99999;box-shadow:0 4px 16px rgba(0,0,0,.3);max-width:80vw;text-align:center';
      document.body.appendChild(toast);
    }
    toast.textContent = 'ระบบเสียงขัดข้อง กรุณาลองใหม่ (แตะเพื่อลองเล่นเสียงอีกครั้ง)';
    toast.style.display = '';
    toast.onclick = function () {
      toast.style.display = 'none';
      if (lastFailedText) speak(lastFailedText);
    };
    clearTimeout(toastHideTimer);
    toastHideTimer = setTimeout(function () { toast.style.display = 'none'; }, 6000);
  }

  // ยกเลิกเสียงที่กำลังพูด/ค้างคิวอยู่ (ผู้ใช้พูดแทรก/สั่งใหม่) แล้วคืน token รอบใหม่
  function resetBargeIn() {
    if (currentAudio) {
      try { currentAudio.pause(); } catch (e) {}
      try { currentAudio.removeAttribute('src'); currentAudio.load(); } catch (e) {}
      currentAudio = null;
    }
    if (currentAudioUrl) { try { URL.revokeObjectURL(currentAudioUrl); } catch (e) {} currentAudioUrl = null; }
    ttsToken++;
    ttsChain = Promise.resolve();
    return ttsToken;
  }

  // ดึงเสียงจาก Soniox ล่วงหน้า (prefetch) — ไม่รอคิวก่อนหน้าเล่นจบก่อน กันช่วงเงียบคั่นระหว่างประโยค
  function fetchBlob(text, myToken, requestId) {
    var cfg = getCfg();
    if (myToken !== ttsToken || !cfg.proxyUrl || !cfg.proxySecret) return Promise.resolve(null);
    var controller = new AbortController();
    var timeoutId = setTimeout(function () { controller.abort(); }, 15000); // TTS timeout
    var baseUrl = cfg.proxyUrl.replace(/\/+$/, '');
    return fetch(baseUrl + '/tts', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-tawee-secret': cfg.proxySecret },
      body: JSON.stringify({ text: text }),
      signal: controller.signal,
    }).then(function (res) {
      clearTimeout(timeoutId);
      if (myToken !== ttsToken) return null;
      if (!res.ok) {
        return res.json().catch(function () { return {}; }).then(function (errData) {
          log('tts_error', { requestId: requestId, code: errData.code || res.status });
          return { error: true };
        });
      }
      return res.blob().then(function (blob) {
        if (myToken !== ttsToken) return null;
        return { blob: blob };
      });
    }).catch(function (e) {
      clearTimeout(timeoutId);
      if (myToken !== ttsToken) return null;
      log('tts_request_failed', { requestId: requestId, name: e.name, message: e.message });
      return { error: true };
    });
  }

  // เล่นเสียงที่ดึงมาเตรียมไว้แล้ว — เรียงตามคิวเสมอ (ttsChain) ไม่มีทางเล่นซ้อน/สลับลำดับ
  function playBlob(fetchPromise, text, myToken, requestId) {
    return fetchPromise.then(function (result) {
      if (!result || myToken !== ttsToken) return;
      if (result.error || !result.blob) { showFailToast(text); return; }
      var url = URL.createObjectURL(result.blob);
      var audio = new Audio(url);
      currentAudio = audio; currentAudioUrl = url;
      return new Promise(function (resolve) {
        function cleanupUrl() {
          try { URL.revokeObjectURL(url); } catch (e) {}
          if (currentAudioUrl === url) currentAudioUrl = null;
        }
        audio.onended = function () { log('audio_ended', { requestId: requestId }); cleanupUrl(); resolve(); };
        audio.onerror = function () {
          var err = audio.error;
          log('audio_playback_error', { requestId: requestId, code: err ? err.code : 'unknown' });
          cleanupUrl();
          if (myToken === ttsToken) showFailToast(text);
          resolve();
        };
        audio.play().catch(function (e) {
          log('audio_play_rejected', { requestId: requestId, name: e.name, message: e.message });
          cleanupUrl();
          if (myToken === ttsToken) showFailToast(text);
          resolve();
        });
      });
    });
  }

  // ทางเข้าเดียว — ใช้แทนของเดิม (window.speechSynthesis) เสียง Soniox Maya เท่านั้น ไม่มี fallback ไปเสียงอื่น
  function speak(text) {
    if (!text) return Promise.resolve();
    var cfg = getCfg();
    if (cfg.speak === false) return Promise.resolve(); // เคารพสวิตช์ปิดเสียงถ้าหน้านั้นมี ไม่มีก็ไม่บล็อก
    var myToken = resetBargeIn();
    var requestId = 'req_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    var fetchPromise = fetchBlob(text, myToken, requestId);
    ttsChain = ttsChain.then(function () { return playBlob(fetchPromise, text, myToken, requestId); });
    return ttsChain;
  }

  global.speakSoniox = speak;
  global.SonioxTTS = { speak: speak, resetBargeIn: resetBargeIn };
})(window);
