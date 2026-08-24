// ไมโครโฟน/STT กลางใช้ร่วมกันทุกหน้าในโปรเจกต์ TAWEE AI (นอก app.js หลัก — หน้าพวกนี้เป็น standalone ไม่ได้โหลด app.js)
// พอร์ตมาจาก pattern เดียวกับหน้าหลัก: MediaRecorder + POST /transcribe (ElevenLabs ผ่าน Worker) — ไม่ใช้ browser SpeechRecognition
// เหตุผล: SpeechRecognition ขึ้นกับการเชื่อมต่อเซิร์ฟเวอร์เสียงของ Google ฝั่งเบราว์เซอร์ ถ้าเชื่อมไม่ได้จะค้างเงียบๆ ไม่มี event ใดๆ เลย
//
// วิธีใช้:
//   window.TAWEE_TTS_PAGE = 'finance-dashboard'; // ตั้งไว้ก่อนโหลดสคริปต์นี้ เพื่อให้ log แยกหน้าได้ (ใช้ค่าเดียวกับ soniox-tts.js ก็ได้)
//   const voice = new TaweeVoiceInput();
//   voice.start({
//     onStateChange(state) {},  // 'requesting_permission' | 'listening' | 'processing_stt' | 'executing_command' | 'idle'
//     onTranscript(text, requestId) {},  // เรียกฟังก์ชันจัดการคำสั่งของหน้านั้นเอง (เช่น handleVoiceCommand)
//     onError(err) {},  // { message, name? }
//   });
//   voice.stop(); // กดไมค์ซ้ำเพื่อหยุดฟังเอง
(function (global) {
  'use strict';
  var LS_KEY = 'tawee_cfg_v3';

  function getCfg() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch (e) { return {}; }
  }

  function log(event, details) {
    var payload = { page: global.TAWEE_TTS_PAGE || 'unknown' };
    for (var k in details) if (details.hasOwnProperty(k)) payload[k] = details[k];
    console.error('[voice:' + event + ']', payload);
  }

  function TaweeVoiceInput() {
    this._recorder = null;
    this._stream = null;
    this._audioContext = null;
    this._raf = null;
    this._maxTimer = null;
    this._starting = false;
    this._listening = false;
    this._discard = false;
    this._callbacks = {};
  }

  TaweeVoiceInput.prototype._setState = function (state) {
    if (this._callbacks.onStateChange) this._callbacks.onStateChange(state);
  };

  TaweeVoiceInput.prototype._cleanup = function () {
    clearTimeout(this._maxTimer);
    if (this._raf) cancelAnimationFrame(this._raf);
    if (this._audioContext && this._audioContext.state !== 'closed') { try { this._audioContext.close(); } catch (e) {} }
    if (this._stream) this._stream.getTracks().forEach(function (t) { t.stop(); });
    this._maxTimer = null; this._raf = null; this._audioContext = null; this._stream = null; this._recorder = null;
  };

  // กดไมค์ซ้ำเพื่อหยุดเอง (discard=true คือทิ้งเสียงที่อัดมาไม่ต้องส่งไปแปลง เช่นตอน error)
  TaweeVoiceInput.prototype.stop = function (discard) {
    if (discard) this._discard = true;
    clearTimeout(this._maxTimer);
    if (this._raf) cancelAnimationFrame(this._raf);
    var recorder = this._recorder;
    if (recorder && recorder.state !== 'inactive') {
      try { recorder.stop(); } catch (e) { this._cleanup(); }
    } else {
      this._cleanup();
    }
  };

  TaweeVoiceInput.prototype._startSilenceMonitor = function (stream, recorder, startedAt) {
    var self = this;
    var AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    try {
      var ctx = new AudioCtx();
      var analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      ctx.createMediaStreamSource(stream).connect(analyser);
      var samples = new Uint8Array(analyser.fftSize);
      var heardSpeech = false, quietSince = 0;
      self._audioContext = ctx;
      function tick() {
        if (self._recorder !== recorder || recorder.state !== 'recording') return;
        analyser.getByteTimeDomainData(samples);
        var sum = 0;
        for (var i = 0; i < samples.length; i++) { var v = (samples[i] - 128) / 128; sum += v * v; }
        var rms = Math.sqrt(sum / samples.length);
        var now = performance.now();
        if (now - startedAt > 350 && rms > 0.025) { heardSpeech = true; quietSince = 0; }
        else if (heardSpeech) {
          if (!quietSince) quietSince = now;
          if (now - quietSince >= 1000) { self.stop(false); return; }
        }
        self._raf = requestAnimationFrame(tick);
      }
      tick();
    } catch (e) {}
  };

  // เริ่มฟัง — กันกดซ้ำด้วย _starting/_listening, ตั้ง timeout สูงสุด 12 วิ (ตัดจริงด้วยตัวจับความเงียบก่อนถึงเวลานี้ตามปกติ)
  TaweeVoiceInput.prototype.start = function (callbacks) {
    var self = this;
    if (this._starting || this._listening) return;
    this._callbacks = callbacks || {};
    var cfg = getCfg();
    if (!cfg.proxyUrl || !cfg.proxySecret) {
      if (this._callbacks.onError) this._callbacks.onError({ message: 'ยังไม่ได้ตั้งค่า Worker Proxy (ตั้งค่าที่หน้าหลัก TAWEE ก่อน)' });
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      if (this._callbacks.onError) this._callbacks.onError({ message: 'เบราว์เซอร์นี้ไม่รองรับการอัดเสียง' });
      return;
    }
    this._starting = true;
    this._discard = false;
    this._setState('requesting_permission');

    navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } })
      .then(function (stream) {
        self._stream = stream;
        var mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'];
        var mimeType = mimeTypes.find(function (type) { return !MediaRecorder.isTypeSupported || MediaRecorder.isTypeSupported(type); });
        var recorder = new MediaRecorder(stream, mimeType ? { mimeType: mimeType } : undefined);
        var chunks = [];
        var startedAt = performance.now();
        self._recorder = recorder;

        recorder.ondataavailable = function (e) { if (e.data && e.data.size) chunks.push(e.data); };
        recorder.onerror = function () {
          self._discard = true;
          log('recorder_error', {});
          if (self._callbacks.onError) self._callbacks.onError({ message: 'อัดเสียงไม่สำเร็จ กรุณาลองใหม่' });
          self.stop(true);
        };
        recorder.onstop = function () {
          var discard = self._discard;
          var blob = new Blob(chunks, { type: recorder.mimeType || mimeType || 'audio/webm' });
          self._cleanup();
          self._listening = false;
          if (discard) { self._setState('idle'); return; }
          if (blob.size < 500) {
            self._setState('idle');
            if (self._callbacks.onError) self._callbacks.onError({ message: 'ไม่ได้ยินเสียงพูด กรุณาลองใหม่' });
            return;
          }
          self._setState('processing_stt');
          self._transcribe(blob);
        };

        recorder.start(250);
        self._listening = true;
        self._setState('listening');
        self._startSilenceMonitor(stream, recorder, startedAt);
        self._maxTimer = setTimeout(function () { self.stop(false); }, 12000);
      })
      .catch(function (e) {
        self._cleanup();
        self._listening = false;
        self._setState('idle');
        var msg = 'เปิดไมค์ไม่สำเร็จ: ' + (e && e.message ? e.message : 'unknown error');
        if (e && (e.name === 'NotAllowedError' || e.name === 'SecurityError')) msg = 'ไม่ได้รับสิทธิ์ใช้ไมค์ — อนุญาตไมค์ให้เว็บไซต์นี้แล้วลองใหม่';
        else if (e && e.name === 'NotFoundError') msg = 'ไม่พบไมโครโฟนในเครื่อง';
        log('getusermedia_failed', { name: e && e.name, message: e && e.message });
        if (self._callbacks.onError) self._callbacks.onError({ message: msg, name: e && e.name });
      })
      .then(function () { self._starting = false; }, function () { self._starting = false; });
  };

  TaweeVoiceInput.prototype._transcribe = function (blob) {
    var self = this;
    var cfg = getCfg();
    var controller = new AbortController();
    var timeoutId = setTimeout(function () { controller.abort(); }, 30000); // STT timeout แยกจาก TTS
    var requestId = 'req_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    var form = new FormData();
    var ext = blob.type.indexOf('mp4') >= 0 ? 'm4a' : 'webm';
    form.append('audio', blob, 'tawee-' + Date.now() + '.' + ext);
    var baseUrl = cfg.proxyUrl.replace(/\/+$/, '');

    fetch(baseUrl + '/transcribe', {
      method: 'POST',
      headers: { 'x-tawee-secret': cfg.proxySecret },
      body: form,
      signal: controller.signal,
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (!res.ok) { var err = new Error(data.error || ('HTTP ' + res.status)); err.code = data.code; throw err; }
        return data;
      });
    }).then(function (data) {
      clearTimeout(timeoutId);
      var text = String(data.text || '').trim();
      if (!text || text === 'ว่างเปล่า') {
        self._setState('idle');
        if (self._callbacks.onError) self._callbacks.onError({ message: 'ไม่ได้ยินคำพูดชัดเจน กรุณาลองใหม่' });
        return;
      }
      self._setState('executing_command');
      if (self._callbacks.onTranscript) self._callbacks.onTranscript(text, requestId);
      self._setState('idle');
    }).catch(function (e) {
      clearTimeout(timeoutId);
      self._setState('idle');
      var msg = e && e.name === 'AbortError' ? 'หมดเวลารอระบบแปลงเสียง' : (e && e.message ? e.message : 'unknown error');
      log('stt_failed', { requestId: requestId, name: e && e.name, message: e && e.message, code: e && e.code });
      if (self._callbacks.onError) self._callbacks.onError({ message: 'แปลงเสียงไม่สำเร็จ: ' + msg });
    });
  };

  global.TaweeVoiceInput = TaweeVoiceInput;
})(window);
