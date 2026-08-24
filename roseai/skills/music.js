'use strict';
// ─────────────────────────────────────────────────────────────
// TAWEE JARVIS — Music Player  |  skills/music.js
// พูด/พิมพ์ "เปิดเพลง" หรือ "เล่นเพลง" เพื่อเริ่มเล่นเพลง
// พูด/พิมพ์ "หยุดเพลง" หรือ "ปิดเพลง" เพื่อหยุด
// พูด/พิมพ์ "เพลงต่อไป" หรือ "เปลี่ยนเพลง" เพื่อข้ามไปเพลงถัดไป
// มีปุ่มควบคุมลอย (เล่น/หยุด/ก่อนหน้า/ถัดไป) โผล่ขึ้นอัตโนมัติตอนเล่นเพลงด้วย
// ─────────────────────────────────────────────────────────────
(function () {
  'use strict';

  // เพลงที่วางไว้ในโฟลเดอร์ data/ — เพิ่ม/ลบไฟล์ในลิสต์นี้ได้ตามต้องการ
  const PLAYLIST = ['data/song2.mp3', 'data/song3.mp3', 'data/song4.mp3'];

  let audio = null;
  let currentIndex = -1;
  let listeners = [];

  function notify() { listeners.forEach((fn) => { try { fn(getState()); } catch (e) {} }); }

  function getState() {
    return {
      playing: isPlaying(),
      trackName: currentIndex >= 0 ? PLAYLIST[currentIndex].split('/').pop().replace(/\.[^.]+$/, '') : '',
      hasTrack: currentIndex >= 0,
    };
  }

  function getAudio() {
    if (!audio) {
      audio = document.createElement('audio');
      audio.id = 'tawee-music-audio';
      audio.style.display = 'none';
      document.body.appendChild(audio);
      audio.addEventListener('ended', playNext);
      audio.addEventListener('play', notify);
      audio.addEventListener('pause', notify);
    }
    return audio;
  }

  function playTrack(index) {
    if (!PLAYLIST.length) return;
    currentIndex = ((index % PLAYLIST.length) + PLAYLIST.length) % PLAYLIST.length;
    const a = getAudio();
    a.src = PLAYLIST[currentIndex];
    notify(); // แสดงชื่อเพลง/แผงควบคุมทันที ไม่ต้องรอ play() สำเร็จก่อน
    a.play().then(notify).catch((e) => {
      console.error('[music] เล่นเพลงไม่สำเร็จ:', e.message);
      notify();
      if (typeof TAWEE !== 'undefined' && TAWEE.showErr) TAWEE.showErr('เล่นเพลงไม่ได้: ' + e.message);
    });
  }

  function playNext() { playTrack(currentIndex + 1); }
  function playPrev() { playTrack(currentIndex <= 0 ? PLAYLIST.length - 1 : currentIndex - 1); }

  function pause() {
    if (audio) audio.pause();
    notify();
  }

  function resume() {
    if (audio && audio.src) { audio.play().catch(() => {}); }
    else { playTrack(0); }
    notify();
  }

  function toggle() { isPlaying() ? pause() : resume(); }

  function stop() {
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    notify();
  }

  function isPlaying() {
    return !!audio && !audio.paused;
  }

  // หมายเหตุ: "เปิดเพลง" มีคำว่า "ปิดเพลง" ซ้อนอยู่ข้างในพอดี (เ+ปิดเพลง) ต้องกันด้วย (?<!เ)
  // ไม่งั้น STOP_RE จะ match มั่วเข้าไปในคำว่า "เปิดเพลง" ทำให้สั่งเปิดเพลงแล้วกลายเป็นหยุดแทน
  const PLAY_RE  = /เปิดเพลง|เล่นเพลง/i;
  const STOP_RE  = /หยุดเพลง|(?<!เ)ปิดเพลง/i;
  const NEXT_RE  = /เพลงต่อไป|เปลี่ยนเพลง|ข้ามเพลง/i;
  const MATCH_RE = new RegExp(PLAY_RE.source + '|' + STOP_RE.source + '|' + NEXT_RE.source, 'i');

  TAWEE.registerSkill('music', {
    match: (t) => MATCH_RE.test(t),
    handle: async (t) => {
      if (STOP_RE.test(t)) { stop(); return '⏸️ หยุดเพลงแล้วค่ะ'; }
      if (NEXT_RE.test(t)) { playNext(); return '⏭️ เปลี่ยนเป็นเพลงถัดไปแล้วค่ะ'; }
      playTrack(currentIndex === -1 ? 0 : currentIndex);
      return '🎵 เปิดเพลงให้แล้วค่ะ ฟังเพลิน ๆ ได้เลยนะคะ';
    },
  });

  // เผื่อสคริปต์อื่น (เช่น morning-routine.js) หรือปุ่มควบคุมลอยอยากสั่งเล่น/หยุดเพลงเอง
  TAWEE.music = {
    play: () => playTrack(0), playTrack, next: playNext, prev: playPrev,
    pause, resume, toggle, stop, isPlaying, getState,
    onChange: (fn) => { listeners.push(fn); },
  };
})();
