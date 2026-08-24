'use strict';
// ═══════════════════════════════════════════════════════════
// TAWEE JARVIS — Core Application  |  app.js  |  v3.0
// ═══════════════════════════════════════════════════════════

// URL ของ Cloudflare Worker proxy + รหัสลับ — ไม่ฝังตายตัวในโค้ด แต่ละคนที่ใช้แอปนี้ deploy Worker
// ของตัวเองแล้วกรอกค่าเองในหน้าตั้งค่า (เก็บใน tawee_cfg_v3.proxyUrl / proxySecret คู่กับ apiKey)

// Deep jewel tones with a metallic edge — shared with the AI Agent Dashboard
// (same ids/hex/rgb via the 'tawee_cfg_v3' localStorage config) for a premium,
// non-neon look across both pages.
const PALETTES = {
  emerald:  { c1:'#0FAE7D', c2:'#065C40', rgb:'15,174,125'  },
  sapphire: { c1:'#3568D4', c2:'#122A63', rgb:'53,104,212'  },
  amethyst: { c1:'#7B4FE0', c2:'#3A1B6E', rgb:'123,79,224'  },
  bronze:   { c1:'#C97C3D', c2:'#7A431C', rgb:'201,124,61'  },
  wine:     { c1:'#B0304B', c2:'#5C1524', rgb:'176,48,75'   },
};

const THEMES = [
  { id:'emerald',  label:'มรกต'     },
  { id:'sapphire', label:'แซฟไฟร์'  },
  { id:'amethyst', label:'อเมทิสต์' },
  { id:'bronze',   label:'บรอนซ์'   },
  { id:'wine',     label:'ไวน์'     },
];

const BG_ANIM_STYLES = [
  { id:'none',   name:'ไม่มี',   desc:'พื้นหลังเรียบตามปกติ' },
  { id:'matrix', name:'Matrix', desc:'ตัวเลข 01 ตกแบบแฮกเกอร์' },
  { id:'fire',   name:'ไฟ',    desc:'เปลวไฟลุกโชนจากขอบจอ' },
  { id:'rain',   name:'ฝนตก',   desc:'สายฝนโปรยปรายทั่วจอ' },
  { id:'snow',   name:'หิมะตก', desc:'เกล็ดหิมะล่องลอยเบาๆ' },
];

const AVATAR_STYLES = [
  { id:'sphere',  name:'Sphere',  desc:'ทรงกลมอนุภาค'    },
  { id:'orb',     name:'Orb',     desc:'แสงกลมซ้อน'      },
  { id:'wave',    name:'Wave',    desc:'คลื่นความถี่'     },
  { id:'neural',  name:'Neural',  desc:'เครือข่ายประสาท'  },
  { id:'hex',     name:'Hex',     desc:'รูปหกเหลี่ยม'     },
  { id:'minimal', name:'Minimal', desc:'เรียบง่ายสง่า'    },
  { id:'crystal', name:'Crystal', desc:'คริสตัลหมุน 3 มิติ' },
  { id:'saturn',  name:'Saturn',  desc:'วงแหวนพลังงาน'    },
  { id:'helix',   name:'Helix',   desc:'เกลียวพลังงานคู่'  },
];

// ═══════════════════════════════════════════════════════════
const TAWEE = {
  // ── Config (defaults; overridden by config.json / localStorage)
  cfg: {
    apiKey:'', proxyUrl:'', proxySecret:'', model:'claude-sonnet-5',
    theme:'emerald', avatar:'sphere', speak:true,
    bgAnim:'none', bgAnimOpacity:0.5, bgAnimSpeed:1,
    userName:'คุณ', weatherLat:13.7563, weatherLon:100.5018, weatherCity:'กรุงเทพฯ',
  },
  // ── UI State
  st: {
    status:'standby', messages:[], panel:null,
    input:'', listening:false, error:'', keySaved:false, proxySaved:false, voiceName:'กำลังโหลด…',
  },
  // ── Avatar canvas
  av: { amp:0.06, micLevel:0, W:0, H:0, ctx:null, pts:[], neuralPts:[], hexPts:[] },
  // ── Audio nodes
  aud: { stream:null, analyser:null, buf:null, ctx:null },
  // ── Camera
  cam: { stream:null, active:false },
  // ── Registry
  skills:{}, voices:[], thVoice:null, recog:null,
  LS: { cfg:'tawee_cfg_v3', hist:'tawee_hist_v3' },

  // ─────────────────────────────────────────────────────────
  // INIT
  // ─────────────────────────────────────────────────────────
  async init() {
    await this.loadCfg();
    this.applyTheme(this.cfg.theme, false);
    this.initHistory();
    this.st.keySaved = !!this.cfg.apiKey;
    this.st.proxySaved = !!(this.cfg.proxyUrl && this.cfg.proxySecret);
    if (!this.hasApiAccess()) this.st.panel = 'settings';
    this.loadVoices();
    this.initCanvas();
    this.initBgAnimCanvas();
    this._startBgAnim();
    this.setStatus('standby');
    this.render();
    this._drawDashIcons();
  },

  async loadCfg() {
    // 1. config.json supplies bootstrap defaults (works when served from local HTTP server)
    let bootstrap = {};
    try {
      const r = await fetch('./config.json');
      if (r.ok) bootstrap = await r.json();
    } catch(e) {}
    Object.assign(this.cfg, bootstrap);
    // 2. localStorage holds the user's latest saved settings — wins over the defaults
    //    ยกเว้นค่าว่าง: saveCfg() เซฟ cfg ทั้งก้อนรวม field ที่ยังว่างอยู่ด้วย ถ้าปล่อยให้ค่าว่างทับ
    //    ค่าที่ config.json ตั้งมาให้ จะกลายเป็นว่าเปิดเว็บมาแล้ว proxyUrl/proxySecret หายทุกครั้ง
    //    (นี่คือสาเหตุที่ไมค์หล่นไปใช้ SpeechRecognition ของเบราว์เซอร์แล้วขึ้น "aborted")
    try {
      const s = localStorage.getItem(this.LS.cfg);
      if (s) {
        const saved = JSON.parse(s);
        for (const k of Object.keys(saved)) {
          const v = saved[k];
          const isBlank = (v === '' || v === null || v === undefined);
          if (isBlank && bootstrap[k]) continue;   // ค่าว่างไม่ทับค่าที่ config.json ให้มา
          this.cfg[k] = v;
        }
      }
    } catch(e) {}
  },

  saveCfg() {
    try { localStorage.setItem(this.LS.cfg, JSON.stringify(this.cfg)); } catch(e) {}
  },

  initHistory() {
    try {
      const h = localStorage.getItem(this.LS.hist);
      if (h) this.st.messages = JSON.parse(h);
    } catch(e) {}
    if (!this.st.messages.length) {
      this.pushMsg('system', 'สวัสดีค่ะ ฉันคือ TAWEE พร้อมให้บริการแล้ว\nกด "ตั้งค่า" เพื่อใส่ Claude API key แล้วเริ่มคุยได้เลย ✨');
    }
  },

  // ─────────────────────────────────────────────────────────
  // THEME
  // ─────────────────────────────────────────────────────────
  applyTheme(name, save = true) {
    if (!PALETTES[name]) return;
    this.cfg.theme = name;
    const p = PALETTES[name];
    const root = document.getElementById('tawee-root');
    if (root) {
      root.style.setProperty('--accent',    p.c1);
      root.style.setProperty('--accent2',   p.c2);
      root.style.setProperty('--accentRGB', p.rgb);
    }
    if (save) this.saveCfg();
    this.render();
  },

  setAvatar(id) {
    this.cfg.avatar = id;
    this.saveCfg();
    this._renderAvatarPanel();   // redraw grid without closing
  },

  // ─────────────────────────────────────────────────────────
  // CANVAS / AVATAR ENGINE
  // ─────────────────────────────────────────────────────────
  initCanvas() {
    const cv = document.getElementById('tawee-canvas');
    if (!cv) return;
    this._genSphere();
    this._genNeural();
    this._genHex();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      const r = cv.getBoundingClientRect();
      this.av.W = r.width; this.av.H = r.height;
      cv.width  = Math.round(r.width  * dpr);
      cv.height = Math.round(r.height * dpr);
      this.av.ctx = cv.getContext('2d');
      this.av.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);
    const loop = (now) => { requestAnimationFrame(loop); this._tickAv(now); };
    requestAnimationFrame(loop);
    this._initMiniOrb();
  },

  // Tiny glowing-orb preview that sits in the top bar as the Dashboard nav button
  _initMiniOrb() {
    const cv = document.getElementById('tawee-dash-mini');
    if (!cv) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const size = 40;
    cv.width = size * dpr; cv.height = size * dpr;
    const ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    const cx = size / 2, cy = size / 2;
    const draw = (now) => {
      requestAnimationFrame(draw);
      const rgb = (PALETTES[this.cfg.theme] || PALETTES.emerald).rgb;
      const pulse = 0.5 + 0.5 * Math.sin(now * 0.0022);
      ctx.clearRect(0, 0, size, size);
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 15);
      g.addColorStop(0,   `rgba(255,255,255,${0.55 + pulse * 0.25})`);
      g.addColorStop(0.4, `rgba(${rgb},${0.55 + pulse * 0.25})`);
      g.addColorStop(1,   'transparent');
      ctx.beginPath(); ctx.arc(cx, cy, 15, 0, 6.283); ctx.fillStyle = g; ctx.fill();
      for (let i = 0; i < 10; i++) {
        const a = (i / 10) * Math.PI * 2 + now * 0.0006;
        const r = 12 + Math.sin(now * 0.002 + i) * 2;
        ctx.beginPath();
        ctx.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 1.1, 0, 6.283);
        ctx.fillStyle = `rgba(${rgb},${0.5 + 0.4 * Math.sin(now * 0.003 + i)})`;
        ctx.fill();
      }
    };
    requestAnimationFrame(draw);
  },

  _genSphere() {
    const N = 460, pts = [];
    for (let i = 0; i < N; i++) {
      const y = 1 - (i / (N-1)) * 2;
      const r = Math.sqrt(Math.max(0, 1 - y*y));
      const phi = i * 2.399963;
      pts.push([Math.cos(phi)*r, y, Math.sin(phi)*r]);
    }
    this.av.pts = pts;
  },

  _genNeural() {
    const pts = [];
    for (let i = 0; i < 22; i++) {
      const a = (i / 22) * Math.PI * 2;
      const r = 0.28 + Math.random() * 0.42;
      pts.push({ x:Math.cos(a)*r, y:Math.sin(a)*r*0.7, vx:(Math.random()-.5)*.0009, vy:(Math.random()-.5)*.0009 });
    }
    pts.push({ x:0, y:0, vx:0, vy:0 });   // center node
    this.av.neuralPts = pts;
  },

  _genHex() {
    const pts = [], size = 0.14;
    for (let q = -4; q <= 4; q++) {
      for (let rr = -4; rr <= 4; rr++) {
        const x = size * (1.5 * q);
        const y = size * (Math.sqrt(3)/2 * q + Math.sqrt(3) * rr);
        if (Math.sqrt(x*x + y*y) < 0.9) pts.push({ x, y, q, r:rr });
      }
    }
    this.av.hexPts = pts;
  },

  _tickAv(now) {
    const { ctx, W, H } = this.av;
    if (!ctx || !W) return;
    // Amplitude target
    let target = 0.05 + 0.022 * Math.sin(now * 0.0016);
    const st = this.st.status;
    if      (st === 'listening') target = Math.max(target, this._readMic());
    else if (st === 'speaking')  target = 0.36 + .20*Math.abs(Math.sin(now*.011)) + .12*Math.abs(Math.sin(now*.029));
    else if (st === 'thinking')  target = 0.18 + .09*Math.abs(Math.sin(now*.007));
    this.av.amp += (target - this.av.amp) * 0.12;
    ctx.clearRect(0, 0, W, H);
    const pal = PALETTES[this.cfg.theme] || PALETTES.emerald;
    switch (this.cfg.avatar) {
      case 'sphere':  this._drawSphere (ctx,W,H,now,this.av.amp,pal); break;
      case 'orb':     this._drawOrb    (ctx,W,H,now,this.av.amp,pal); break;
      case 'wave':    this._drawWave   (ctx,W,H,now,this.av.amp,pal); break;
      case 'neural':  this._drawNeural (ctx,W,H,now,this.av.amp,pal); break;
      case 'hex':     this._drawHex    (ctx,W,H,now,this.av.amp,pal); break;
      case 'minimal': this._drawMinimal(ctx,W,H,now,this.av.amp,pal); break;
      case 'crystal': this._drawCrystal(ctx,W,H,now,this.av.amp,pal); break;
      case 'saturn':  this._drawSaturn (ctx,W,H,now,this.av.amp,pal); break;
      case 'helix':   this._drawHelix  (ctx,W,H,now,this.av.amp,pal); break;
      default:        this._drawSphere (ctx,W,H,now,this.av.amp,pal);
    }
  },

  // ── 1. Sphere — rotating particle globe ──────────────────
  _drawSphere(ctx, W, H, t, amp, pal) {
    const cx=W/2, cy=H/2, rgb=pal.rgb;
    const scale = Math.min(W,H) * 0.30 * (1 + amp*0.18);
    ctx.save(); ctx.translate(cx, cy);
    // Outer glow
    const g = ctx.createRadialGradient(0,0,0, 0,0,scale*1.2);
    g.addColorStop(0,   `rgba(${rgb},${.28+amp*.50})`);
    g.addColorStop(0.5, `rgba(${rgb},${.06+amp*.12})`);
    g.addColorStop(1,   'transparent');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(0,0,scale*1.2,0,6.283); ctx.fill();
    // Rotating points
    const ry=t*.00026, rx=Math.sin(t*.00018)*.45;
    const cY=Math.cos(ry),sY=Math.sin(ry),cX=Math.cos(rx),sX=Math.sin(rx);
    for (const p of this.av.pts) {
      const x1=p[0]*cY-p[2]*sY, z1=p[0]*sY+p[2]*cY, y1=p[1];
      const y2=y1*cX-z1*sX,     z2=y1*sX+z1*cX;
      const d=(z2+1)/2;
      ctx.fillStyle=`rgba(${rgb},${.12+d*.72})`;
      ctx.beginPath(); ctx.arc(x1*scale,y2*scale,.5+d*1.9,0,6.283); ctx.fill();
    }
    // Bright core
    const cg=ctx.createRadialGradient(0,0,0,0,0,scale*.40);
    cg.addColorStop(0,   `rgba(255,255,255,${.50+amp*.40})`);
    cg.addColorStop(0.5, `rgba(${rgb},${.35+amp*.30})`);
    cg.addColorStop(1,   'transparent');
    ctx.fillStyle=cg; ctx.beginPath(); ctx.arc(0,0,scale*.40,0,6.283); ctx.fill();
    // Reactive wave ring
    ctx.lineWidth=1.6; ctx.strokeStyle=`rgba(${rgb},${.50+amp*.45})`;
    ctx.shadowColor=`rgba(${rgb},.90)`; ctx.shadowBlur=10+amp*50;
    ctx.beginPath();
    for(let i=0;i<=128;i++){
      const a=i/128*6.283, w=Math.sin(a*5+t*.004)*.5+Math.sin(a*9-t*.0065)*.5;
      const rr=scale*1.22+(6+amp*80)*w;
      i?ctx.lineTo(Math.cos(a)*rr,Math.sin(a)*rr):ctx.moveTo(Math.cos(a)*rr,Math.sin(a)*rr);
    }
    ctx.closePath(); ctx.stroke(); ctx.shadowBlur=0;
    // Orbiting dots
    for(let k=0;k<3;k++){
      const a=t*.0006*(k+1)+k*2.1, orb=scale*(1.42+.05*Math.sin(t*.002+k));
      ctx.fillStyle=`rgba(${rgb},.90)`; ctx.shadowColor=`rgba(${rgb},1)`; ctx.shadowBlur=14;
      ctx.beginPath(); ctx.arc(Math.cos(a)*orb,Math.sin(a)*orb*.42,2.2,0,6.283); ctx.fill();
      ctx.shadowBlur=0;
    }
    ctx.restore();
  },

  // ── 2. Orb — layered glowing orb ─────────────────────────
  _drawOrb(ctx, W, H, t, amp, pal) {
    const cx=W/2,cy=H/2,rgb=pal.rgb,base=Math.min(W,H)*.28;
    ctx.save(); ctx.translate(cx,cy);
    for(let i=3;i>=1;i--){
      const ph=Math.sin(t*.0012+i)*.5+.5, r=base*(.9+i*.28+amp*.3*i), a=(.06+ph*.08)*(1+amp*.5);
      ctx.beginPath(); ctx.arc(0,0,r,0,6.283);
      ctx.strokeStyle=`rgba(${rgb},${a})`; ctx.lineWidth=1.5+i; ctx.stroke();
    }
    const ripR=base*(1.1+((t%3000)/3000)*(1+amp)), ripA=Math.max(0,.6-ripR/(base*2.5));
    ctx.beginPath(); ctx.arc(0,0,ripR,0,6.283);
    ctx.strokeStyle=`rgba(${rgb},${ripA})`; ctx.lineWidth=2.5; ctx.stroke();
    const ig=ctx.createRadialGradient(0,0,0,0,0,base*1.1);
    ig.addColorStop(0,   `rgba(255,255,255,${.60+amp*.40})`);
    ig.addColorStop(0.35,`rgba(${rgb},${.50+amp*.40})`);
    ig.addColorStop(0.7, `rgba(${rgb},${.15+amp*.20})`);
    ig.addColorStop(1,   'transparent');
    ctx.fillStyle=ig; ctx.beginPath(); ctx.arc(0,0,base*1.1,0,6.283); ctx.fill();
    const a1=t*.0009, a2=a1+Math.PI*(1.5+amp*.5);
    ctx.beginPath(); ctx.arc(0,0,base*(1.2+amp*.12),a1,a2);
    ctx.strokeStyle=`rgba(${rgb},${.70+amp*.30})`; ctx.lineWidth=2.5;
    ctx.shadowColor=`rgba(${rgb},1)`; ctx.shadowBlur=18+amp*30;
    ctx.stroke(); ctx.shadowBlur=0;
    ctx.restore();
  },

  // ── 3. Wave — circular frequency bars ────────────────────
  _drawWave(ctx, W, H, t, amp, pal) {
    const cx=W/2,cy=H/2,rgb=pal.rgb,base=Math.min(W,H)*.30;
    ctx.save(); ctx.translate(cx,cy);
    const g=ctx.createRadialGradient(0,0,0,0,0,base*1.5);
    g.addColorStop(0,`rgba(${rgb},${.12+amp*.18})`); g.addColorStop(1,'transparent');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(0,0,base*1.5,0,6.283); ctx.fill();
    for(let i=0;i<64;i++){
      const a=i/64*6.283-Math.PI/2;
      const f=Math.abs(Math.sin(i*.4+t*.004)*.5+Math.sin(i*.8-t*.007)*.5+Math.sin(i*1.6+t*.003)*.3);
      const bl=base*(.1+f*(.5+amp*.8));
      const x1=Math.cos(a)*base*.6, y1=Math.sin(a)*base*.6;
      const x2=Math.cos(a)*(base*.6+bl), y2=Math.sin(a)*(base*.6+bl);
      ctx.strokeStyle=`rgba(${rgb},${.40+f*.50})`; ctx.lineWidth=2.5;
      ctx.shadowColor=`rgba(${rgb},${.40+f*.50})`; ctx.shadowBlur=6+f*20;
      ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    }
    ctx.shadowBlur=0;
    const cg=ctx.createRadialGradient(0,0,0,0,0,base*.5);
    cg.addColorStop(0,`rgba(255,255,255,${.60+amp*.40})`); cg.addColorStop(.6,`rgba(${rgb},${.30+amp*.40})`); cg.addColorStop(1,'transparent');
    ctx.fillStyle=cg; ctx.beginPath(); ctx.arc(0,0,base*.5,0,6.283); ctx.fill();
    ctx.restore();
  },

  // ── 4. Neural — animated neural network ──────────────────
  _drawNeural(ctx, W, H, t, amp, pal) {
    const cx=W/2,cy=H/2,rgb=pal.rgb,scale=Math.min(W,H)*.38;
    ctx.save(); ctx.translate(cx,cy);
    const pts=this.av.neuralPts;
    for(const p of pts){ p.x+=p.vx*(1+amp*2); p.y+=p.vy*(1+amp*2); if(Math.abs(p.x)>.9)p.vx*=-1; if(Math.abs(p.y)>.6)p.vy*=-1; }
    for(let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
      const dx=(pts[j].x-pts[i].x)*scale, dy=(pts[j].y-pts[i].y)*scale;
      const dist=Math.sqrt(dx*dx+dy*dy);
      if(dist<scale*.55){
        const a=(1-dist/(scale*.55))*(.25+amp*.35);
        ctx.strokeStyle=`rgba(${rgb},${a})`; ctx.lineWidth=.8+a*2;
        ctx.beginPath(); ctx.moveTo(pts[i].x*scale,pts[i].y*scale); ctx.lineTo(pts[j].x*scale,pts[j].y*scale); ctx.stroke();
      }
    }
    for(let i=0;i<pts.length;i++){
      const p=pts[i], isC=i===pts.length-1;
      const r2=isC?6+amp*10:2.5+amp*3, a=isC?.90+amp*.10:.50+amp*.40;
      ctx.shadowColor=`rgba(${rgb},.9)`; ctx.shadowBlur=isC?20+amp*40:8+amp*12;
      ctx.fillStyle=`rgba(${rgb},${a})`;
      ctx.beginPath(); ctx.arc(p.x*scale,p.y*scale,r2,0,6.283); ctx.fill();
    }
    ctx.shadowBlur=0;
    ctx.beginPath(); ctx.arc(0,0,scale*.85,0,6.283);
    ctx.strokeStyle=`rgba(${rgb},${.10+amp*.15})`; ctx.lineWidth=1; ctx.stroke();
    ctx.restore();
  },

  // ── 5. Hex — hexagonal grid ───────────────────────────────
  _drawHex(ctx, W, H, t, amp, pal) {
    const cx=W/2,cy=H/2,rgb=pal.rgb,scale=Math.min(W,H)*.42;
    ctx.save(); ctx.translate(cx,cy);
    const g=ctx.createRadialGradient(0,0,0,0,0,scale*.9);
    g.addColorStop(0,`rgba(${rgb},${.12+amp*.18})`); g.addColorStop(1,'transparent');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(0,0,scale*.9,0,6.283); ctx.fill();
    const size=scale*.11;
    for(const h of this.av.hexPts){
      const x=h.x*scale, y=h.y*scale;
      const dist=Math.sqrt(h.x*h.x+h.y*h.y);
      const wave=Math.sin(dist*5-t*.003+h.q*.5)*.5+.5;
      const a=.08+wave*(.15+amp*.35), sz=size*(.85+wave*.20);
      ctx.beginPath();
      for(let k=0;k<6;k++){ const a2=k/6*6.283; k?ctx.lineTo(x+Math.cos(a2)*sz,y+Math.sin(a2)*sz):ctx.moveTo(x+Math.cos(a2)*sz,y+Math.sin(a2)*sz); }
      ctx.closePath();
      ctx.strokeStyle=`rgba(${rgb},${a})`; ctx.lineWidth=1;
      ctx.fillStyle=`rgba(${rgb},${a*.20})`;
      ctx.shadowColor=`rgba(${rgb},${a})`; ctx.shadowBlur=4+wave*10*amp;
      ctx.fill(); ctx.stroke();
    }
    ctx.shadowBlur=0;
    const cg=ctx.createRadialGradient(0,0,0,0,0,scale*.22);
    cg.addColorStop(0,`rgba(255,255,255,${.50+amp*.40})`); cg.addColorStop(.7,`rgba(${rgb},${.30+amp*.30})`); cg.addColorStop(1,'transparent');
    ctx.fillStyle=cg; ctx.beginPath(); ctx.arc(0,0,scale*.22,0,6.283); ctx.fill();
    ctx.restore();
  },

  // ── 6. Minimal — elegant line + pulse ────────────────────
  _drawMinimal(ctx, W, H, t, amp, pal) {
    const cx=W/2,cy=H/2,rgb=pal.rgb,base=Math.min(W,H)*.30;
    ctx.save(); ctx.translate(cx,cy);
    ctx.beginPath(); ctx.arc(0,0,base,0,6.283);
    ctx.strokeStyle=`rgba(${rgb},${.15+amp*.20})`; ctx.lineWidth=1; ctx.stroke();
    const pr=base*(.65+amp*.25);
    ctx.beginPath(); ctx.arc(0,0,pr,0,6.283);
    ctx.strokeStyle=`rgba(${rgb},${.40+amp*.50})`; ctx.lineWidth=1.5;
    ctx.shadowColor=`rgba(${rgb},.80)`; ctx.shadowBlur=15+amp*35; ctx.stroke(); ctx.shadowBlur=0;
    const sy=Math.sin(t*.002)*base*.55, sa=.15+amp*.50;
    ctx.beginPath(); ctx.moveTo(-base*.55,sy); ctx.lineTo(base*.55,sy);
    ctx.strokeStyle=`rgba(${rgb},${sa})`; ctx.lineWidth=1;
    ctx.shadowColor=`rgba(${rgb},${sa})`; ctx.shadowBlur=8+amp*20; ctx.stroke(); ctx.shadowBlur=0;
    const vA=Math.sin(t*.0015)*.5+.5, vL=base*(.3+vA*.4+amp*.2);
    ctx.beginPath(); ctx.moveTo(0,-vL); ctx.lineTo(0,vL);
    ctx.strokeStyle=`rgba(${rgb},${.20+vA*.40+amp*.20})`; ctx.lineWidth=1.5; ctx.stroke();
    ctx.fillStyle=`rgba(${rgb},${.80+amp*.20})`; ctx.shadowColor=`rgba(${rgb},1)`; ctx.shadowBlur=12+amp*28;
    ctx.beginPath(); ctx.arc(0,0,3.5+amp*5,0,6.283); ctx.fill(); ctx.shadowBlur=0;
    for(const [dx,dy] of [[1,0],[0,1],[-1,0],[0,-1]]){
      const bx=dx*base*.78, by=dy*base*.78, tl=8;
      ctx.beginPath(); ctx.moveTo(bx-dy*tl,by+dx*tl); ctx.lineTo(bx+dy*tl,by-dx*tl);
      ctx.strokeStyle=`rgba(${rgb},${.40+amp*.40})`; ctx.lineWidth=1.5; ctx.stroke();
    }
    ctx.restore();
  },

  // ── 7. Crystal — rotating 3D wireframe octahedron ─────────
  _drawCrystal(ctx, W, H, t, amp, pal) {
    const cx=W/2, cy=H/2, rgb=pal.rgb, scale=Math.min(W,H)*.32*(1+amp*.15);
    const ax=t*.0006, ay=t*.0009;
    const verts=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
    const edges=[[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,4],[2,5],[3,4],[3,5]];
    const proj=verts.map(([x,y,z])=>{
      const x1=x*Math.cos(ay)+z*Math.sin(ay), z1=-x*Math.sin(ay)+z*Math.cos(ay);
      const y1=y*Math.cos(ax)-z1*Math.sin(ax), z2=y*Math.sin(ax)+z1*Math.cos(ax);
      const f=2.6, persp=f/(f+z2);
      return { x:cx+x1*scale*persp, y:cy+y1*scale*persp, z:z2, persp };
    });
    ctx.save();
    const g=ctx.createRadialGradient(cx,cy,0,cx,cy,scale*1.1);
    g.addColorStop(0,`rgba(${rgb},${.10+amp*.15})`); g.addColorStop(1,'transparent');
    ctx.fillStyle=g; ctx.beginPath(); ctx.arc(cx,cy,scale*1.1,0,6.283); ctx.fill();
    const sorted=[...edges].sort((a,b)=>(proj[a[0]].z+proj[a[1]].z)-(proj[b[0]].z+proj[b[1]].z));
    for (const [i,j] of sorted) {
      const p1=proj[i], p2=proj[j], depth=(p1.z+p2.z)/2;
      const a=Math.max(.15,Math.min(1,.35+amp*.4+depth*.15));
      ctx.strokeStyle=`rgba(${rgb},${a})`; ctx.lineWidth=1.2+p1.persp*.8;
      ctx.beginPath(); ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y); ctx.stroke();
    }
    for (const p of proj) {
      ctx.shadowColor=`rgba(${rgb},.9)`; ctx.shadowBlur=10+amp*20;
      ctx.fillStyle=`rgba(${rgb},${.7+amp*.3})`;
      ctx.beginPath(); ctx.arc(p.x,p.y,2.5*p.persp,0,6.283); ctx.fill();
    }
    ctx.shadowBlur=0; ctx.restore();
  },

  // ── 8. Saturn — glowing core with tilted energy rings ─────
  _drawSaturn(ctx, W, H, t, amp, pal) {
    const cx=W/2, cy=H/2, rgb=pal.rgb, scale=Math.min(W,H)*.30*(1+amp*.15);
    ctx.save(); ctx.translate(cx,cy);
    const core=ctx.createRadialGradient(0,0,0,0,0,scale*.42);
    core.addColorStop(0,'rgba(255,255,255,.9)'); core.addColorStop(.5,`rgba(${rgb},.7)`); core.addColorStop(1,'transparent');
    ctx.fillStyle=core; ctx.beginPath(); ctx.arc(0,0,scale*.42,0,6.283); ctx.fill();
    const rings=[
      { rx:scale*.95, ry:scale*.28, rot:t*.0004 },
      { rx:scale*.78, ry:scale*.20, rot:-t*.0006+1.4 },
      { rx:scale*1.12,ry:scale*.34, rot:t*.0003+2.6 },
    ];
    for (const r of rings) {
      ctx.save(); ctx.rotate(r.rot);
      ctx.beginPath(); ctx.ellipse(0,0,r.rx,r.ry,0,0,6.283);
      ctx.strokeStyle=`rgba(${rgb},${.35+amp*.35})`; ctx.lineWidth=1.6;
      ctx.shadowColor=`rgba(${rgb},.6)`; ctx.shadowBlur=8+amp*14;
      ctx.stroke(); ctx.restore();
    }
    ctx.shadowBlur=0; ctx.restore();
  },

  // ── 9. Helix — rotating double energy helix ───────────────
  _drawHelix(ctx, W, H, t, amp, pal) {
    const cx=W/2, cy=H/2, rgb=pal.rgb, scale=Math.min(W,H)*.34;
    ctx.save(); ctx.translate(cx,cy);
    const N=26, speed=t*.0025, strand1=[], strand2=[];
    for (let i=0;i<N;i++) {
      const phase=(i/N)*Math.PI*4+speed, y=(i/N-.5)*scale*1.7;
      strand1.push({ x:Math.cos(phase)*scale*.42*(1+amp*.2), y, z:Math.sin(phase) });
      strand2.push({ x:Math.cos(phase+Math.PI)*scale*.42*(1+amp*.2), y, z:Math.sin(phase+Math.PI) });
    }
    for (let i=0;i<N;i+=2) {
      const p1=strand1[i], p2=strand2[i], a=.15+amp*.25+(p1.z+1)/2*.15;
      ctx.strokeStyle=`rgba(${rgb},${a})`; ctx.lineWidth=1;
      ctx.beginPath(); ctx.moveTo(p1.x,p1.y); ctx.lineTo(p2.x,p2.y); ctx.stroke();
    }
    for (const strand of [strand1,strand2]) {
      for (const p of strand) {
        const depthA=(p.z+1)/2;
        ctx.shadowColor=`rgba(${rgb},.8)`; ctx.shadowBlur=6+amp*14*depthA;
        ctx.fillStyle=`rgba(${rgb},${.35+depthA*.55+amp*.2})`;
        ctx.beginPath(); ctx.arc(p.x,p.y,2+depthA*2.2,0,6.283); ctx.fill();
      }
    }
    ctx.shadowBlur=0; ctx.restore();
  },

  // ─────────────────────────────────────────────────────────
  // CAMERA + VISION
  // ─────────────────────────────────────────────────────────
  async toggleCamera() {
    this.cam.active ? this.stopCamera() : await this.startCamera();
  },

  async startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode:'user', width:{ ideal:640 }, height:{ ideal:480 } },
      });
      this.cam.stream  = stream;
      this.cam.active  = true;
      const vid = document.getElementById('tawee-video');
      if (vid) { vid.srcObject = stream; }
      const panel = document.getElementById('tawee-cam-panel');
      if (panel) panel.style.display = '';
      this._styleCamBtn(true);
      this.pushMsg('system', '📷 กล้องเปิดแล้วค่ะ — กด "ส่งให้ TAWEE ดู" เพื่อให้ TAWEE วิเคราะห์ภาพ หรือถามว่า "เห็นอะไรบ้าง" ก็ได้ค่ะ');
      this.render();
    } catch(e) {
      this.showErr('ไม่สามารถเปิดกล้องได้: ' + (e.message || e.name));
    }
  },

  stopCamera() {
    if (this.cam.stream) { this.cam.stream.getTracks().forEach(t => t.stop()); this.cam.stream = null; }
    this.cam.active = false;
    const panel = document.getElementById('tawee-cam-panel');
    if (panel) panel.style.display = 'none';
    this._styleCamBtn(false);
    this.render();
  },

  _styleCamBtn(active) {
    const btn = document.getElementById('tawee-cam-btn');
    if (!btn) return;
    btn.style.borderColor = active ? 'var(--accent)'              : 'rgba(255,255,255,.14)';
    btn.style.background  = active ? 'rgba(var(--accentRGB),.18)' : 'rgba(255,255,255,.05)';
    btn.style.boxShadow   = active ? '0 0 22px rgba(var(--accentRGB),.5)' : '';
    btn.textContent = active ? '🎥' : '📷';
  },

  captureFrame() {
    const vid = document.getElementById('tawee-video');
    if (!vid || !this.cam.active || !vid.videoWidth) return null;
    const canvas = document.createElement('canvas');
    canvas.width  = vid.videoWidth;
    canvas.height = vid.videoHeight;
    const ctx = canvas.getContext('2d');
    // un-mirror for Claude (draw normal)
    ctx.scale(-1, 1);
    ctx.drawImage(vid, -canvas.width, 0);
    return canvas.toDataURL('image/jpeg', 0.75).split(',')[1];
  },

  // Send current camera frame (with optional prompt) to Claude Vision
  async sendCameraFrame(prompt) {
    if (!this.cam.active) { this.showErr('กรุณาเปิดกล้องก่อนค่ะ'); return; }
    if (!this.hasApiAccess()) { this.st.panel='settings'; this.showErr('กรุณาใส่ Claude API key ก่อน'); this.render(); return; }
    const base64 = this.captureFrame();
    if (!base64) { this.showErr('ไม่สามารถจับภาพได้ กรุณารอให้กล้องโหลดเสร็จ'); return; }
    const userText = prompt || 'คุณเห็นอะไรในภาพนี้? ช่วยบอกสิ่งที่เห็นให้ละเอียดหน่อยค่ะ';
    this.pushMsg('user', '📷 ' + userText);
    this.st.input = '';
    this.setStatus('thinking'); this.render();
    await this._callVision(base64, userText);
  },

  // "ถามพร้อมภาพ" — take current input text + frame together
  async snapAndAsk() {
    const txt = (document.getElementById('tawee-input')?.value || '').trim();
    await this.sendCameraFrame(txt || 'มีอะไรน่าสนใจในภาพนี้บ้างคะ?');
  },

  async _callVision(base64, text) {
    try {
      const target = this._apiTarget();
      
        if (this.cfg.model.startsWith('gemini')) {
            const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${this.cfg.model}:generateContent?key=${this.cfg.geminiKey}`;
            
            // Format history for Gemini
            let geminiContents = history.map(m => ({
                role: m.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: m.content }]
            }));
            
            const geminiBody = {
                systemInstruction: { parts: [{ text: this._sysPrompt() }] },
                contents: geminiContents,
                generationConfig: { maxOutputTokens: 1024, temperature: 0.7 }
            };
            
            const gRes = await fetch(geminiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(geminiBody)
            });
            const gData = await gRes.json();
            
            if (gData.error) throw new Error(gData.error.message);
            if (!gData.candidates || !gData.candidates[0].content) throw new Error("Invalid Gemini response");
            
            const botMsg = gData.candidates[0].content.parts[0].text;
            this.pushMsg('assistant', botMsg);
            this.setStatus('standby');
            this.speakText(botMsg);
            this.render();
            return;
        }

        
        if (this.cfg.model.startsWith('gemini')) {
            const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${this.cfg.model}:generateContent?key=${this.cfg.geminiKey}`;
            let geminiContents = history.map(m => ({
                role: m.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: m.content }]
            }));
            const geminiBody = {
                systemInstruction: { parts: [{ text: this._sysPrompt() }] },
                contents: geminiContents,
                generationConfig: { maxOutputTokens: 1024, temperature: 0.7 }
            };
            const gRes = await fetch(geminiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(geminiBody)
            });
            const gData = await gRes.json();
            if (gData.error) throw new Error(gData.error.message);
            if (!gData.candidates || !gData.candidates[0].content) throw new Error("Invalid Gemini response");
            const botMsg = gData.candidates[0].content.parts[0].text;
            this.pushMsg('assistant', botMsg);
            this.setStatus('standby');
            this.speakText(botMsg);
            this.render();
            return;
        }

        const res = await fetch(target.url, {
        method: 'POST',
        headers: { 'content-type': 'application/json', ...target.headers },
        body: JSON.stringify({
          model: this.cfg.model,
          max_tokens: 600,
          system: this._sysPrompt(),
          messages: [{
            role: 'user',
            content: [
              { type: 'image', source: { type:'base64', media_type:'image/jpeg', data:base64 } },
              { type: 'text',  text },
            ],
          }],
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error((data.error && data.error.message) || 'HTTP ' + res.status);
      const reply = data.content?.[0]?.text || '(ไม่มีคำตอบ)';
      this.pushMsg('assistant', reply); this.setStatus('standby'); this.speakText(reply);
    } catch(e) {
      this.pushMsg('system', '⚠ Vision error: ' + e.message);
      this.setStatus('standby'); this.showErr(e.message);
    }
    this.render();
  },

  // ─────────────────────────────────────────────────────────
  // MICROPHONE CAPTURE
  // ─────────────────────────────────────────────────────────
  async startMicCap() {
    try {
      this.aud.stream = await navigator.mediaDevices.getUserMedia({ audio:true });
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!this.aud.ctx) this.aud.ctx = new AC();
      if (this.aud.ctx.state === 'suspended') await this.aud.ctx.resume();
      const src = this.aud.ctx.createMediaStreamSource(this.aud.stream);
      const an  = this.aud.ctx.createAnalyser(); an.fftSize = 256;
      src.connect(an); this.aud.analyser = an; this.aud.buf = new Uint8Array(an.fftSize);
    } catch(e) {}
  },

  stopMicCap() {
    if (this.aud.stream) { this.aud.stream.getTracks().forEach(t => t.stop()); this.aud.stream = null; }
    this.aud.analyser = null; this.av.micLevel = 0;
  },

  _readMic() {
    if (!this.aud.analyser) return this.av.micLevel;
    this.aud.analyser.getByteTimeDomainData(this.aud.buf);
    let sum = 0;
    for (const v of this.aud.buf) { const d=(v-128)/128; sum+=d*d; }
    this.av.micLevel = Math.min(1, Math.sqrt(sum / this.aud.buf.length) * 3.5);
    return this.av.micLevel;
  },

  // ─────────────────────────────────────────────────────────
  // TEXT-TO-SPEECH — เลือกทางเดียวตายตัวตามค่าที่ตั้งไว้ ไม่มีการสลับไปมาระหว่างสองเสียงกลางคัน (กันปัญหาเสียงเปลี่ยนไม่คงที่)
  // ตั้งค่า Worker/Soniox ไว้ → ใช้ Soniox (เสียง Maya) ตลอด | ไม่ได้ตั้งค่า → ใช้เสียงในตัวบราวเซอร์ตลอด (ใช้ได้ทันที ไม่ต้องสมัคร API เสียงเพิ่ม)
  // ทุกช่องทาง (พิมพ์/ไมค์/กล้อง/Local Skills) เดินผ่าน pipeline เดียวกันนี้ทั้งหมด (speakText = ตัวห่อสั้นๆ เรียก enqueue เหมือนกัน)
  // ─────────────────────────────────────────────────────────
  loadVoices() {
    this.st.voiceName = (this.cfg.proxyUrl && this.cfg.proxySecret) ? 'Soniox Maya' : 'เสียงในตัวบราวเซอร์';
    const el = document.getElementById('tawee-tts-name'); if (el) el.textContent = this.st.voiceName;
  },

  // ทางเข้าเดียวสำหรับพูดข้อความก้อนเดียว (พิมพ์/Local Skills/กล้อง) — ใช้ pipeline เดียวกับโหมดเสียงทุกจุด
  async speakText(text) {
    if (!this.cfg.speak) return;
    const myToken = this._resetTtsBargeIn();
    this._enqueueSpeech(text, myToken, null, true, 0);
  },

  // ยกเลิกเสียงที่กำลังพูด/ค้างคิวอยู่ (ตอบใหม่ทับของเก่า หรือผู้ใช้พูดขัดจังหวะ) แล้วคืน token รอบใหม่
  _resetTtsBargeIn() {
    if (this._ttsAudio) {
      try { this._ttsAudio.pause(); } catch (e) {}
      try { this._ttsAudio.removeAttribute('src'); this._ttsAudio.load(); } catch (e) {} // ยกเลิก network request เดิมจริงๆ ไม่ใช่แค่หยุดเล่น
      this._ttsAudio = null;
    }
    if (this._ttsAudioUrl) { try { URL.revokeObjectURL(this._ttsAudioUrl); } catch (e) {} this._ttsAudioUrl = null; }
    if (window.speechSynthesis) { try { window.speechSynthesis.cancel(); } catch (e) {} }
    this._ttsToken = (this._ttsToken || 0) + 1;
    this._ttsChain = Promise.resolve();
    return this._ttsToken;
  },

  // ต่อคิวพูดทีละท่อนตามลำดับ
  // จุดสำคัญ: เริ่ม "ดึงเสียง" (fetch) ท่อนนี้ทันทีตอนเรียก ไม่รอคิวก่อนหน้าเล่นจบก่อน (prefetch) — ป้องกันช่วงเงียบคั่นระหว่างประโยค
  // ส่วนการ "เล่น" ยังคงเรียงตามคิว (_ttsChain) เสมอ ไม่มีทางเล่นสองท่อนซ้อนกันหรือสลับลำดับ
  // เลือกทาง Soniox หรือเสียงในตัวบราวเซอร์ตั้งแต่ตรงนี้ทางเดียว ไม่ใช่ fallback หลังลองยิงจริงแล้วพัง (กันเสียงสลับไปมาไม่คงที่)
  _enqueueSpeech(text, myToken, requestId, isFirstChunk, chunkIndex) {
    if (!this._ttsChain) this._ttsChain = Promise.resolve();
    if (!(this.cfg.proxyUrl && this.cfg.proxySecret)) {
      this._ttsChain = this._ttsChain.then(() => this._playBrowserTts(text, myToken, requestId, isFirstChunk));
      return;
    }
    const fetchPromise = this._fetchTtsBlob(text, myToken, requestId, isFirstChunk, chunkIndex);
    this._ttsChain = this._ttsChain.then(() => this._playTtsBlob(fetchPromise, text, myToken, requestId, isFirstChunk, chunkIndex));
  },

  // พูดผ่านเสียงในตัวบราวเซอร์ (Web Speech API) — ใช้ตอนยังไม่ได้ตั้งค่า Worker/Soniox เพื่อให้สมาชิกใช้เสียงได้ทันทีโดยไม่ต้องสมัคร API เสียงเพิ่ม
  async _playBrowserTts(text, myToken, requestId, isFirstChunk) {
    if (myToken !== this._ttsToken || !window.speechSynthesis) return;
    this.setStatus('speaking');
    if (isFirstChunk && requestId) this._traceMark(requestId, 'audio_playback_started');
    await new Promise((resolve) => {
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'th-TH';
      utter.onend = resolve;
      utter.onerror = resolve;
      window.speechSynthesis.speak(utter);
    });
    if (isFirstChunk && requestId) this._traceReport(requestId);
    if (myToken === this._ttsToken && this.st.status === 'speaking') this.setStatus('standby');
  },

  // ดึงเสียงท่อนนี้จาก Soniox (POST /tts) ล่วงหน้า — ไม่มี fallback ไปเสียงอื่นเด็ดขาด
  // คืน {blob} เมื่อสำเร็จ, {error:true} เมื่อ Soniox ใช้ไม่ได้จริง (network/timeout/error), null เมื่อถูกยกเลิกก่อนเสร็จ (token เปลี่ยน)
  async _fetchTtsBlob(text, myToken, requestId, isFirstChunk, chunkIndex) {
    if (myToken !== this._ttsToken || !this.cfg.speak) return null;
    if (!(this.cfg.proxyUrl && this.cfg.proxySecret)) return null;
    if (isFirstChunk && requestId) this._traceMark(requestId, 'tts_started');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // TTS timeout แยกจาก STT/LLM
    try {
      const res = await fetch(`${this.cfg.proxyUrl}/tts`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-tawee-secret': this.cfg.proxySecret },
        body: JSON.stringify({ text }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (myToken !== this._ttsToken) return null;
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        this._ttsLog('tts_error', { requestId, chunkIndex, code: errData.code || res.status });
        return { error: true };
      }
      const blob = await res.blob();
      if (myToken !== this._ttsToken) return null;
      if (isFirstChunk && requestId) { this._traceMark(requestId, 'tts_first_audio_chunk'); this._traceMark(requestId, 'tts_completed'); }
      return { blob };
    } catch (e) {
      clearTimeout(timeoutId);
      if (myToken !== this._ttsToken) return null;
      this._ttsLog('tts_request_failed', { requestId, chunkIndex, name: e.name, message: e.message });
      return { error: true };
    }
  },

  // เล่นเสียงท่อนที่ดึงมาเตรียมไว้แล้ว (รอให้ fetch เสร็จก่อนถ้ายังไม่เสร็จ) — เรียงตามคิวเสมอ ไม่เล่นซ้อน
  async _playTtsBlob(fetchPromise, text, myToken, requestId, isFirstChunk, chunkIndex) {
    const result = await fetchPromise;
    if (!result || myToken !== this._ttsToken) return;
    if (result.error || !result.blob) {
      this._ttsFailed(text, myToken, requestId, isFirstChunk);
      return;
    }

    const url = URL.createObjectURL(result.blob);
    const audio = new Audio(url);
    this._ttsAudio = audio;
    this._ttsAudioUrl = url;
    this.setStatus('speaking');
    if (isFirstChunk && requestId) this._traceMark(requestId, 'audio_playback_started');

    await new Promise((resolve) => {
      const cleanupUrl = () => { try { URL.revokeObjectURL(url); } catch (e) {} if (this._ttsAudioUrl === url) this._ttsAudioUrl = null; };
      audio.onended = () => { this._ttsLog('audio_ended', { requestId, chunkIndex }); cleanupUrl(); resolve(); };
      audio.onerror = () => {
        const mediaErr = audio.error;
        this._ttsLog('audio_playback_error', { requestId, chunkIndex, code: mediaErr ? mediaErr.code : 'unknown', message: mediaErr ? mediaErr.message : '' });
        cleanupUrl();
        if (myToken === this._ttsToken) this._ttsFailed(text, myToken, requestId, isFirstChunk);
        resolve();
      };
      audio.play().catch((e) => {
        this._ttsLog('audio_play_rejected', { requestId, chunkIndex, name: e.name, message: e.message });
        cleanupUrl();
        if (myToken === this._ttsToken) this._ttsFailed(text, myToken, requestId, isFirstChunk);
        resolve();
      });
    });

    if (isFirstChunk && requestId) this._traceReport(requestId);
    if (myToken === this._ttsToken && this.st.status === 'speaking') this.setStatus('standby');
  },

  // log โครงสร้าง เก็บแค่ requestId/chunkIndex/error name-message — ห้ามมีข้อความสนทนาเต็มหรือคีย์ใดๆ
  _ttsLog(event, details) {
    console.error('[tts:' + event + ']', { page: 'main', ...details });
  },

  // Soniox ใช้ไม่ได้จริงๆ — ไม่เปลี่ยนไปเสียงอื่นเด็ดขาด แค่แจ้งเตือน + ให้แตะข้อความแจ้งเตือนเพื่อลองเล่นเสียงซ้ำ
  _ttsFailed(text, myToken, requestId, isFirstChunk) {
    if (isFirstChunk && requestId) this._traceReport(requestId);
    if (myToken === this._ttsToken && this.st.status === 'speaking') this.setStatus('standby');
    this._lastFailedTts = text;
    this.showErr('ระบบเสียงขัดข้อง กรุณาลองใหม่ (แตะข้อความนี้เพื่อลองเล่นเสียงอีกครั้ง)');
    const toast = document.getElementById('tawee-toast');
    if (toast) { toast.style.cursor = 'pointer'; toast.onclick = () => this.retryLastTts(); }
  },

  // ปุ่ม "ลองเล่นเสียงอีกครั้ง" — เรียกจากการแตะข้อความแจ้งเตือนตอน TTS ล้มเหลว
  retryLastTts() {
    if (!this._lastFailedTts) return;
    const text = this._lastFailedTts;
    this._lastFailedTts = null;
    const myToken = this._resetTtsBargeIn();
    this._enqueueSpeech(text, myToken, null, true, 0);
  },

  // ─────────────────────────────────────────────────────────
  // CONVERSATION
  // ─────────────────────────────────────────────────────────
  // ถ้าใส่ apiKey ไว้ในหน้าตั้งค่า → ยิงตรงหา Anthropic (สะดวกตอน dev/ทดสอบ local)
  // ถ้าไม่ใส่แต่ตั้งค่า Worker proxy ของตัวเองไว้ → ใช้ Worker แทน (เก็บ key ไว้ฝั่ง server ปลอดภัยกว่า)
  _apiTarget() {
    if (this.cfg.apiKey) {
      return {
        url: 'https://api.anthropic.com/v1/messages',
        headers: {
          'x-api-key': this.cfg.apiKey,
          'anthropic-version': '2023-06-01',
          'anthropic-dangerous-direct-browser-access': 'true',
        },
      };
    }
    return { url: this.cfg.proxyUrl, headers: { 'x-tawee-secret': this.cfg.proxySecret } };
  },

  hasApiAccess() { return !!(this.cfg.apiKey || this.cfg.geminiKey || (this.cfg.proxyUrl && this.cfg.proxySecret)); },

  async send(rawText, opts) {
    const text = (rawText != null ? rawText : this.st.input).trim();
    if (!text) return;
    if (!this.hasApiAccess()) {
      this.st.panel='settings'; this.showErr('กรุณาใส่ Claude API key ก่อนใช้งานค่ะ'); this.render(); return;
    }

    // Auto vision: if camera is on + query contains visual keywords → include frame
    const VISION_KW = /เห็น|ดูหน่อย|มองดู|ในภาพ|ในกล้อง|หน้าตา|ที่เห็น|look|see|what.*see|in.*camera/i;
    if (this.cam.active && VISION_KW.test(text)) {
      await this.sendCameraFrame(text); return;
    }

    this.pushMsg('user', text);
    this.st.input=''; this.setStatus('thinking'); this.render();

    // ── Try local skills first
    const skillRes = await this.dispatchSkill(text);
    if (skillRes) {
      this.pushMsg('assistant', skillRes); this.setStatus('standby'); this.speakText(skillRes); this.render(); return;
    }

    // ── ไม่มี skill ไหนจับคำสั่งได้จาก regex ตรงๆ → ให้ Claude ลองแปลประโยคธรรมชาติเป็นคำสั่งมาตรฐานก่อน
    // (เช่น "อีกสิบนาทีเตือนหน่อยนะ" → "ตั้งเวลา 10 นาที") แล้วค่อยยิงเข้า skill เดิมตามปกติ
    // ถ้าแปลไม่ได้/ไม่ใช่คำสั่ง จะคืน null แล้วไหลไปคุยกับ Claude แบบปกติ ไม่ขวางทาง
    if (TAWEE.nlu) {
      const canonical = await TAWEE.nlu.translate(text, this.cfg);
      if (canonical) {
        const nluRes = await this.dispatchSkill(canonical);
        if (nluRes) {
          this.pushMsg('assistant', nluRes); this.setStatus('standby'); this.speakText(nluRes); this.render(); return;
        }
      }
    }

    // ── Claude API
    // ข้อความเก่าที่ .text เพี้ยน (ไม่ใช่ string) ต้องกันไว้ตรงนี้ด้วย — ไม่งั้น content จะหลุดเป็น undefined
    // ทำให้ Claude API reject ทั้ง request ด้วย error "content: Input should be a valid array"
    const history = this.st.messages
      .filter(m => m.role==='user' || m.role==='assistant')
      .map(m => ({ role: m.role, content: String(m.text ?? '').trim() }))
      .filter(m => m.content)
      .slice(-20);

    // โหมดเสียง (fast) ใช้ path แบบ stream — พูดทีละประโยคทันทีที่ Claude สร้างเสร็จ ไม่ต้องรอทั้งก้อน
    // (เดิมรอ Claude ตอบจบ + TTS สร้างเสียงทั้งไฟล์ก่อนถึงพูดได้ ทำให้เห็นข้อความแล้วแต่เงียบอีกหลายวิ)
    if (opts && opts.fast) {
      await this._sendStreaming(history, opts.requestId);
      this.render();
      return;
    }

    try {
      const target = this._apiTarget();
      
        if (this.cfg.model.startsWith('gemini')) {
            const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${this.cfg.model}:generateContent?key=${this.cfg.geminiKey}`;
            
            // Format history for Gemini
            let geminiContents = history.map(m => ({
                role: m.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: m.content }]
            }));
            
            const geminiBody = {
                systemInstruction: { parts: [{ text: this._sysPrompt() }] },
                contents: geminiContents,
                generationConfig: { maxOutputTokens: 1024, temperature: 0.7 }
            };
            
            const gRes = await fetch(geminiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(geminiBody)
            });
            const gData = await gRes.json();
            
            if (gData.error) throw new Error(gData.error.message);
            if (!gData.candidates || !gData.candidates[0].content) throw new Error("Invalid Gemini response");
            
            const botMsg = gData.candidates[0].content.parts[0].text;
            this.pushMsg('assistant', botMsg);
            this.setStatus('standby');
            this.speakText(botMsg);
            this.render();
            return;
        }

        
        if (this.cfg.model.startsWith('gemini')) {
            const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${this.cfg.model}:generateContent?key=${this.cfg.geminiKey}`;
            let geminiContents = history.map(m => ({
                role: m.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: m.content }]
            }));
            const geminiBody = {
                systemInstruction: { parts: [{ text: this._sysPrompt() }] },
                contents: geminiContents,
                generationConfig: { maxOutputTokens: 1024, temperature: 0.7 }
            };
            const gRes = await fetch(geminiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(geminiBody)
            });
            const gData = await gRes.json();
            if (gData.error) throw new Error(gData.error.message);
            if (!gData.candidates || !gData.candidates[0].content) throw new Error("Invalid Gemini response");
            const botMsg = gData.candidates[0].content.parts[0].text;
            this.pushMsg('assistant', botMsg);
            this.setStatus('standby');
            this.speakText(botMsg);
            this.render();
            return;
        }

        const res = await fetch(target.url, {
        method:'POST',
        headers:{ 'content-type':'application/json', ...target.headers },
        body: JSON.stringify({
          model: this.cfg.model,
          max_tokens: 1024,
          system: this._sysPrompt(),
          messages: history,
          // เปิด Web Search ให้ Claude ค้นข้อมูลจริงตอนตอบได้ (ข่าว/ราคา/เหตุการณ์ปัจจุบัน) — เฉพาะ path คุยทั่วไปนี้ ไม่กระทบ voice/skill ที่เร็วอยู่แล้ว
          tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 3 }],
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error((data.error&&data.error.message)||'HTTP '+res.status);
      // content อาจมีหลาย block ปนกัน (server_tool_use/web_search_tool_result/text) เมื่อ Claude เรียกค้นเว็บ — เอาเฉพาะ text มาต่อกัน
      const reply = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n\n').trim() || '(ไม่มีคำตอบ)';
      this.pushMsg('assistant', reply); this.setStatus('standby'); this.speakText(reply);
    } catch(e) {
      this.pushMsg('system', '⚠ เกิดข้อผิดพลาด: ' + e.message);
      this.setStatus('standby'); this.showErr(e.message);
    }
    this.render();
  },

  // ─── Performance Tracing ───
  // วัดเวลาแต่ละช่วงของ pipeline เสียง (ฟัง→คิด→พูด) ด้วย requestId เดียวกันตลอดสาย
  // เก็บแค่ timestamp ตัวเลข ไม่ log ข้อความ/คีย์ใดๆ ทั้งสิ้น
  _traceStart(requestId) {
    this._traces = this._traces || {};
    this._traces[requestId] = { t0: performance.now(), marks: {} };
  },
  _traceMark(requestId, stage) {
    const t = this._traces && this._traces[requestId];
    if (!t || t.marks[stage] != null) return; // มาร์กซ้ำไม่ทับของเดิม (เอาเวลาที่เกิดครั้งแรกจริง)
    t.marks[stage] = performance.now() - t.t0;
  },
  // แสดง timestamp ดิบทุก stage (ms นับจาก speech_end) แยกชัดเจน 3 จุดที่มักปนกัน:
  // tts_first_audio_chunk (ไบต์แรกมาถึง) vs audio_playback_started (เริ่มเล่นจริง) vs tts_completed (สร้าง/โหลดเสียงเสร็จทั้งไฟล์)
  _traceReport(requestId) {
    const t = this._traces && this._traces[requestId];
    if (!t) return;
    const m = t.marks;
    const val = (stage) => m[stage] != null ? Math.round(m[stage]) : null;
    console.table({
      [requestId]: {
        request_id: requestId,
        speech_end: 0,
        stt_started: val('stt_started'),
        stt_completed: val('stt_completed'),
        llm_started: val('llm_started'),
        llm_first_token: val('llm_first_token'),
        llm_completed: val('llm_completed'),
        tts_started: val('tts_started'),
        tts_response_headers: val('tts_response_headers'),
        tts_first_audio_chunk: val('tts_first_audio_chunk'),
        audio_playback_started: val('audio_playback_started'),
        tts_completed: val('tts_completed'),
        total_time_to_first_audio: val('audio_playback_started'),
      },
    });
    delete this._traces[requestId];
  },

  // โมเดลเร็วสุด (Haiku) + คำตอบสั้น (300 token พอสำหรับคุยด้วยเสียง) + stream:true
  // อ่านคำตอบทีละท่อนจาก Claude แล้วส่งพูดทันทีที่ครบประโยค ไม่รอคำตอบจบทั้งหมด
  async _sendStreaming(history, requestId) {
    let res;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // LLM timeout แยกจาก STT/TTS
    if (requestId) this._traceMark(requestId, 'llm_started');
    try {
      const target = this._apiTarget();
      res = await fetch(target.url, {
        method: 'POST',
        headers: { 'content-type': 'application/json', ...target.headers },
        body: JSON.stringify({
          model: 'claude-haiku-4-5-20251001',
          max_tokens: 300,
          system: this._sysPrompt(),
          messages: history,
          stream: true,
        }),
        signal: controller.signal,
      });
    } catch (e) {
      clearTimeout(timeoutId);
      const msg = e.name === 'AbortError' ? 'Claude ตอบช้าเกินไป (timeout)' : e.message;
      this.pushMsg('system', '⚠ เกิดข้อผิดพลาด: ' + msg);
      this.setStatus('standby'); this.showErr(msg);
      return;
    }
    if (!res.ok || !res.body) {
      clearTimeout(timeoutId);
      const data = await res.json().catch(() => ({}));
      const msg = (data.error && data.error.message) || ('HTTP ' + res.status);
      this.pushMsg('system', '⚠ เกิดข้อผิดพลาด: ' + msg);
      this.setStatus('standby'); this.showErr(msg);
      return;
    }

    this.pushMsg('assistant', '');
    const msgObj = this.st.messages[this.st.messages.length - 1];
    const myToken = this._resetTtsBargeIn();

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let sseBuffer = '';
    let fullText = '';
    let speakBuffer = '';
    let isFirstChunk = true;
    let chunkIndex = 0;
    // ตัดที่จบประโยคเป็นหลักเสมอ — ความยาวเป็นแค่ตัวช่วยตัดสินว่า "พอตัดได้หรือยัง" (ไม่ถึง MIN ไม่ตัดแม้เจอจุด)
    // และเป็นเพดานกันข้อความยาวเกินไปไม่มีจุดจบเลย (บังคับตัดที่ MAX โดยหาช่องว่างล่าสุดกันตัดกลางคำ)
    const SENTENCE_END = /[.!?\n]|[ๆฯ](?=\s|$)/;
    const MIN_CHUNK = 80, MAX_CHUNK = 240;

    const flush = (force) => {
      if (!speakBuffer.trim()) return;
      let chunk;
      if (force) {
        chunk = speakBuffer; speakBuffer = '';
      } else if (speakBuffer.length >= MAX_CHUNK) {
        // ยาวเกิน max แต่ยังไม่เจอจุดจบประโยคเลย — ตัดที่ช่องว่างล่าสุดก่อนตำแหน่ง max กันตัดกลางคำ
        let cut = speakBuffer.lastIndexOf(' ', MAX_CHUNK);
        if (cut < MIN_CHUNK) cut = MAX_CHUNK; // ไม่มีช่องว่างให้ตัดเลยจริงๆ (ข้อความยาวติดกัน) ตัดตรงนั้นไปเลย
        chunk = speakBuffer.slice(0, cut).trim();
        speakBuffer = speakBuffer.slice(cut);
      } else if (speakBuffer.length >= MIN_CHUNK && SENTENCE_END.test(speakBuffer)) {
        chunk = speakBuffer; speakBuffer = '';
      } else {
        return; // ยังสั้นไปหรือยังไม่จบประโยค รอสะสมต่อ
      }
      if (!chunk) return;
      this._enqueueSpeech(chunk, myToken, requestId, isFirstChunk, chunkIndex);
      isFirstChunk = false; chunkIndex++;
    };

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        sseBuffer += decoder.decode(value, { stream: true });
        const lines = sseBuffer.split('\n');
        sseBuffer = lines.pop(); // บรรทัดสุดท้ายอาจยังมาไม่ครบ เก็บไว้ต่อรอบหน้า
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr || jsonStr === '[DONE]') continue;
          let evt;
          try { evt = JSON.parse(jsonStr); } catch (e) { continue; }
          if (evt.type === 'content_block_delta' && evt.delta && evt.delta.type === 'text_delta') {
            if (requestId && !fullText) this._traceMark(requestId, 'llm_first_token');
            const piece = evt.delta.text || '';
            fullText += piece; speakBuffer += piece;
            msgObj.text = fullText; this.render();
            flush(false);
          }
        }
      }
    } catch (e) {
      // เน็ตหลุดกลางทาง/timeout — พูดเท่าที่ได้มาต่อ ไม่ทำให้ทั้งข้อความหาย
    } finally {
      clearTimeout(timeoutId);
      if (requestId) this._traceMark(requestId, 'llm_completed');
    }
    flush(true);
    if (!fullText.trim()) msgObj.text = '(ไม่มีคำตอบ)';
    try { localStorage.setItem(this.LS.hist, JSON.stringify(this.st.messages.slice(-60))); } catch (e) {}
  },

  _sysPrompt() {
    let p = 'คุณคือ TAWEE ผู้ช่วยส่วนตัวอัจฉริยะ อบอุ่น สุภาพ เป็นกันเอง ตอบเป็นภาษาไทยเสมอ ใช้คำลงท้ายที่เป็นมิตร ตอบกระชับ ชัดเจน เป็นธรรมชาติเหมือนคุยกับเพื่อนที่ฉลาด ห้ามใช้เครื่องหมาย * หรือ # และห้ามใช้อิโมจิเด็ดขาดในทุกคำตอบ ใช้ได้แค่ตัวอักษรและตัวเลขเท่านั้น';
    const profile = localStorage.getItem('tawee_profile');
    if (profile) p += '\n\nข้อมูลเจ้าของ:\n' + profile;
    return p;
  },

  pushMsg(role, text) {
    const time = new Date().toTimeString().slice(0,8);
    this.st.messages.push({ role, text, time });
    try { localStorage.setItem(this.LS.hist, JSON.stringify(this.st.messages.slice(-60))); } catch(e) {}
    setTimeout(() => { const f=document.getElementById('tawee-feed'); if(f) f.scrollTop=f.scrollHeight; }, 40);
  },

  clearChat() {
    try { localStorage.removeItem(this.LS.hist); } catch(e) {}
    this.st.messages = [{ role:'system', text:'ล้างบทสนทนาแล้ว — เริ่มคุยใหม่ได้เลยค่ะ', time:new Date().toTimeString().slice(0,8) }];
    this.render();
  },

  // ─────────────────────────────────────────────────────────
  // SKILL DISPATCH
  // ─────────────────────────────────────────────────────────
  registerSkill(name, skill) { this.skills[name] = skill; },

  async dispatchSkill(text) {
    const t = text.toLowerCase();
    for (const [, skill] of Object.entries(this.skills)) {
      if (skill.match && skill.match(t)) {
        try { return await skill.handle(t, text, this.cfg); } catch(e) { return null; }
      }
    }
    return null;
  },

  // ─────────────────────────────────────────────────────────
  // STATE HELPERS
  // ─────────────────────────────────────────────────────────
  setStatus(s) {
    this.st.status = s;
    const colors = { standby:'var(--accent)', listening:'var(--accent)', thinking:'#ffd166', speaking:'var(--accent)' };
    const labels = { standby:'พร้อมใช้งาน', listening:'กำลังฟัง…', thinking:'กำลังคิด…', speaking:'กำลังพูด…' };
    const dot = document.getElementById('tawee-status-dot');
    const lbl = document.getElementById('tawee-status');
    if (dot) { dot.style.background=colors[s]; dot.style.boxShadow=`0 0 12px ${colors[s]}`; }
    if (lbl) lbl.textContent = labels[s]||s;
    const ripple = document.getElementById('tawee-mic-ripple');
    if (ripple) ripple.style.display = s==='listening' ? '' : 'none';
  },

  showErr(msg) {
    this.st.error = msg;
    const toast = document.getElementById('tawee-toast');
    if (toast) { toast.textContent=msg; toast.style.display=msg?'':'none'; }
    clearTimeout(this._errT);
    if (msg) this._errT = setTimeout(() => {
      this.st.error='';
      const t=document.getElementById('tawee-toast'); if(t) t.style.display='none';
    }, 4500);
  },

  // ─────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────
  // แต่ละฟังก์ชันแยก try/catch กันเอง — ถ้าตัวใดตัวหนึ่ง throw (เช่นข้อมูลเก่าที่รูปแบบผิดจาก localStorage)
  // ฟังก์ชันที่เหลือยังต้องทำงานต่อ ไม่งั้นแผงตั้งค่า/แชท/อวตารจะไม่อัปเดตเลยทั้งที่ไม่เกี่ยวกับจุดที่พัง
  render() {
    const steps = [
      this._renderTopBar, this._renderCaption, this._renderInput, this._renderScrim,
      this._renderSettingsPanel, this._renderFeedPanel, this._renderAvatarPanel, this._renderBgPanel,
    ];
    for (const fn of steps) {
      try { fn.call(this); } catch (e) { console.error('[render] ' + fn.name + ' failed:', e); }
    }
  },

  _renderTopBar() {
    // Theme dots
    const dotsEl = document.getElementById('tawee-theme-dots');
    if (dotsEl) {
      dotsEl.innerHTML = Object.keys(PALETTES).map(id => {
        const p = PALETTES[id], active = id===this.cfg.theme;
        return `<button onclick="TAWEE.applyTheme('${id}')" title="${id}" style="width:13px;height:13px;border-radius:50%;border:none;cursor:pointer;padding:0;background:${p.c1};box-shadow:${active?'0 0 0 2px #fff,0 0 10px '+p.c1:'0 0 0 1px rgba(255,255,255,.22)'};transition:all .2s;"></button>`;
      }).join('');
    }
    // Message count
    const badge = document.getElementById('tawee-msg-count');
    if (badge) badge.textContent = this.st.messages.filter(m=>m.role!=='system').length || '';
  },

  _renderCaption() {
    const el = document.getElementById('tawee-caption'); if(!el) return;
    const lastA = [...this.st.messages].reverse().find(m=>m.role==='assistant');
    const lastU = [...this.st.messages].reverse().find(m=>m.role==='user');
    // ข้อความเก่าใน localStorage บางรายการ .text อาจไม่ใช่ string (ข้อมูลค้างจากบั๊กเก่า) — กันด้วย String() เสมอ
    // ไม่งั้น .slice() throw ตรงนี้จะทำให้ render() หยุดกลางคัน ฟังก์ชัน render ย่อยที่เรียงไว้หลังจากนี้ทั้งหมดจะไม่ทำงานเลย
    const uText = lastU ? String(lastU.text ?? '') : '';
    const aText = lastA ? String(lastA.text ?? '') : '';
    let cap = '';
    if (this.st.status==='thinking' && lastU) cap = '"' + uText.slice(0,90) + (uText.length>90?'…':'"');
    else if (lastA) cap = aText.slice(0,160) + (aText.length>160?'…':'');
    else cap = 'สวัสดีค่ะ ฉันคือ TAWEE — พิมพ์ข้อความหรือกดไมค์เพื่อเริ่มคุย';
    el.textContent = cap;
  },

  _renderInput() {
    const inp = document.getElementById('tawee-input');
    if (inp && document.activeElement!==inp) inp.value = this.st.input;
    const mic = document.getElementById('tawee-mic');
    if (mic) {
      const a = this.st.listening;
      mic.style.borderColor = a?'var(--accent)':'rgba(255,255,255,.14)';
      mic.style.background  = a?'rgba(var(--accentRGB),.16)':'rgba(255,255,255,.05)';
      mic.style.boxShadow   = a?'0 0 28px rgba(var(--accentRGB),.55)':'0 10px 30px rgba(0,0,0,.4)';
    }
    this._styleCamBtn(this.cam.active);
  },

  _renderScrim() {
    const s = document.getElementById('tawee-scrim'); if(s) s.style.display=this.st.panel?'':'none';
  },

  _renderSettingsPanel() {
    const panel = document.getElementById('tawee-settings'); if(!panel) return;
    const open = this.st.panel==='settings';
    panel.style.transform = open?'translateX(0)':'translateX(-105%)';
    if (!open) return;
    // Fields
    const ki = document.getElementById('tawee-key-input'); if(ki&&!ki.value&&this.cfg.apiKey) ki.value=this.cfg.apiKey;
    const ks = document.getElementById('tawee-key-saved'); if(ks) ks.style.display=this.st.keySaved?'':'none';
    const pu = document.getElementById('tawee-proxy-url-input'); if(pu&&!pu.value&&this.cfg.proxyUrl) pu.value=this.cfg.proxyUrl;
    const psec = document.getElementById('tawee-proxy-secret-input'); if(psec&&!psec.value&&this.cfg.proxySecret) psec.value=this.cfg.proxySecret;
    const ps = document.getElementById('tawee-proxy-saved'); if(ps) ps.style.display=this.st.proxySaved?'':'none';
    const mdl= document.getElementById('tawee-model-select'); if(mdl) mdl.value=this.cfg.model;
    const tts= document.getElementById('tawee-tts-name'); if(tts) tts.textContent=this.st.voiceName;
    const wc = document.getElementById('tawee-weather-city'); if(wc&&!wc.value) wc.value=this.cfg.weatherCity||'';
    // Speak toggle
    const tog = document.getElementById('tawee-speak-toggle');
    if (tog) {
      const on=this.cfg.speak;
      const trk=tog.querySelector('span:last-child'); if(trk) trk.style.background=on?'var(--accent)':'rgba(255,255,255,.18)';
      const knob=tog.querySelector('.knob'); if(knob) knob.style.left=on?'21px':'3px';
    }
    // Profile
    const pr = document.getElementById('tawee-profile');
    if (pr && !pr.dataset.loaded) { pr.value=localStorage.getItem('tawee_profile')||''; pr.dataset.loaded='1'; }
    // Theme list
    const tl = document.getElementById('tawee-theme-list');
    if (tl) tl.innerHTML = THEMES.map(th => {
      const p=PALETTES[th.id], active=th.id===this.cfg.theme;
      return `<button onclick="TAWEE.applyTheme('${th.id}')" style="display:flex;align-items:center;gap:12px;padding:11px 13px;border-radius:12px;border:1px solid ${active?'rgba(255,255,255,.35)':'rgba(255,255,255,.08)'};background:${active?'rgba(255,255,255,.06)':'rgba(255,255,255,.02)'};color:#dfe3ea;font-size:13px;cursor:pointer;width:100%;text-align:left;transition:all .2s;"><span style="width:22px;height:22px;border-radius:7px;flex-shrink:0;background:linear-gradient(135deg,${p.c1},${p.c2});box-shadow:0 0 12px ${p.c1}80;"></span><span style="flex:1;">${th.label}</span>${active?'<span style="color:var(--accent);">✓</span>':''}</button>`;
    }).join('');
  },

  _renderFeedPanel() {
    const panel = document.getElementById('tawee-feed-panel'); if(!panel) return;
    const open = this.st.panel==='feed';
    panel.style.transform = open?'translateX(0)':'translateX(105%)';
    if (!open) return;
    // Messages
    const feed = document.getElementById('tawee-feed');
    if (feed) {
      const lc={system:'#7c8598',user:'#aeb6c4',assistant:'var(--accent)'};
      const tc={system:'rgba(255,255,255,.42)',user:'rgba(255,255,255,.82)',assistant:'rgba(255,255,255,.88)'};
      const lb={system:'SYS',user:'YOU',assistant:'TAWEE'};
      feed.innerHTML = this.st.messages.map(m =>
        `<div style="display:flex;flex-direction:column;gap:3px;animation:taweeFade .3s ease;">` +
        `<div style="display:flex;align-items:center;gap:8px;">` +
        `<span style="font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1.5px;color:${lc[m.role]||'#7c8598'};">${lb[m.role]||m.role}</span>` +
        `<span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,255,255,.28);">${m.time||''}</span></div>` +
        `<div style="font-size:13.5px;line-height:1.65;color:${tc[m.role]||'rgba(255,255,255,.7)'};font-weight:300;">${this._esc(m.text)}</div></div>`
      ).join('') + (this.st.status==='thinking'
        ? '<div style="display:flex;gap:5px;align-items:center;padding-top:2px;"><span style="width:6px;height:6px;border-radius:50%;background:var(--accent);animation:taweeDots 1.2s infinite;display:inline-block;"></span><span style="width:6px;height:6px;border-radius:50%;background:var(--accent);animation:taweeDots 1.2s infinite .2s;display:inline-block;"></span><span style="width:6px;height:6px;border-radius:50%;background:var(--accent);animation:taweeDots 1.2s infinite .4s;display:inline-block;"></span></div>'
        : '');
      feed.scrollTop = feed.scrollHeight;
    }
    const apiEl=document.getElementById('tawee-api-status'); if(apiEl){apiEl.textContent=this.cfg.apiKey?'เชื่อมต่อแล้ว':'ยังไม่ได้ใส่ key';apiEl.style.color=this.cfg.apiKey?'var(--accent)':'#ff7a8a';}
    const memEl=document.getElementById('tawee-mem-count'); if(memEl) memEl.textContent=this.st.messages.filter(m=>m.role!=='system').length+' ข้อความ';
    const sttEl=document.getElementById('tawee-stt-status'); if(sttEl){
      const workerOk=this._canUseServerStt();
      const browserOk=!!(window.SpeechRecognition || window.webkitSpeechRecognition);
      sttEl.textContent=workerOk?'พร้อม (Worker STT)':(browserOk?'พร้อม (Browser)':'ไม่รองรับ');
      sttEl.style.color=(workerOk||browserOk)?'var(--accent)':'#ff7a8a';
    }
  },

  _renderAvatarPanel() {
    const panel = document.getElementById('tawee-avatar-panel'); if(!panel) return;
    const open = this.st.panel==='avatars';
    panel.style.transform = open?'translateX(0)':'translateX(105%)';
    if (!open) return;
    const grid = document.getElementById('tawee-avatar-grid');
    if (grid) {
      grid.innerHTML = AVATAR_STYLES.map(s => {
        const active = s.id===this.cfg.avatar;
        return `<button onclick="TAWEE.setAvatar('${s.id}')" style="display:flex;flex-direction:column;align-items:center;gap:9px;padding:16px 10px;border-radius:14px;border:1px solid ${active?'rgba(255,255,255,.40)':'rgba(255,255,255,.08)'};background:${active?'rgba(255,255,255,.07)':'rgba(255,255,255,.02)'};cursor:pointer;transition:all .2s;width:100%;">
          <canvas id="av-tb-${s.id}" width="74" height="74" style="border-radius:10px;background:rgba(0,0,0,.35);display:block;"></canvas>
          <span style="font-size:12.5px;font-weight:600;color:${active?'var(--accent)':'#b9c0cd'};">${s.name}</span>
          <span style="font-size:10.5px;color:rgba(255,255,255,.38);text-align:center;line-height:1.4;">${s.desc}</span>
          ${active?'<span style="font-size:10px;color:var(--accent);">✓ ใช้งานอยู่</span>':''}
        </button>`;
      }).join('');
      setTimeout(() => { if(this.st.panel==='avatars') this._drawThumbs(); }, 60);
    }
  },

  _drawThumbs() {
    const rgb = (PALETTES[this.cfg.theme]||PALETTES.emerald).rgb;
    for (const s of AVATAR_STYLES) {
      const cv = document.getElementById('av-tb-'+s.id); if(!cv) continue;
      const ctx=cv.getContext('2d'); const W=74,H=74;
      ctx.clearRect(0,0,W,H); ctx.save(); ctx.translate(W/2,H/2);
      switch(s.id) {
        case 'sphere': {
          const g=ctx.createRadialGradient(0,0,0,0,0,28);g.addColorStop(0,'rgba(255,255,255,.8)');g.addColorStop(.5,`rgba(${rgb},.6)`);g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,28,0,6.283);ctx.fill();
          for(let i=0;i<20;i++){const a=i/20*6.283,r2=16+Math.sin(i*1.5)*5;ctx.fillStyle=`rgba(${rgb},.75)`;ctx.beginPath();ctx.arc(Math.cos(a)*r2,Math.sin(a)*r2,1.7,0,6.283);ctx.fill();}
          break; }
        case 'orb': {
          for(let i=3;i>=1;i--){ctx.beginPath();ctx.arc(0,0,i*9,0,6.283);ctx.strokeStyle=`rgba(${rgb},${.12*i})`;ctx.lineWidth=2+i;ctx.stroke();}
          const g=ctx.createRadialGradient(0,0,0,0,0,16);g.addColorStop(0,'rgba(255,255,255,.9)');g.addColorStop(.6,`rgba(${rgb},.7)`);g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,16,0,6.283);ctx.fill();
          break; }
        case 'wave': {
          for(let i=0;i<24;i++){const a=i/24*6.283,f=Math.abs(Math.sin(i*.6));const x1=Math.cos(a)*10,y1=Math.sin(a)*10,x2=Math.cos(a)*(10+f*16),y2=Math.sin(a)*(10+f*16);ctx.strokeStyle=`rgba(${rgb},${.4+f*.6})`;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
          ctx.fillStyle=`rgba(${rgb},.85)`;ctx.beginPath();ctx.arc(0,0,5,0,6.283);ctx.fill();
          break; }
        case 'neural': {
          const np=[[0,0],[12,-8],[-12,-6],[8,12],[-10,10],[0,-18],[18,0],[-18,2],[6,-14],[-6,14]];
          for(let i=0;i<np.length;i++)for(let j=i+1;j<np.length;j++){const dx=np[j][0]-np[i][0],dy=np[j][1]-np[i][1],d=Math.sqrt(dx*dx+dy*dy);if(d<22){ctx.strokeStyle=`rgba(${rgb},${.15+(1-d/22)*.55})`;ctx.lineWidth=.8;ctx.beginPath();ctx.moveTo(np[i][0],np[i][1]);ctx.lineTo(np[j][0],np[j][1]);ctx.stroke();}}
          for(const p of np){ctx.fillStyle=`rgba(${rgb},.9)`;ctx.beginPath();ctx.arc(p[0],p[1],p[0]===0&&p[1]===0?4.5:2.2,0,6.283);ctx.fill();}
          break; }
        case 'hex': {
          const hs=12,angles=[0,Math.PI/3,2*Math.PI/3,Math.PI,4*Math.PI/3,5*Math.PI/3];
          for(const a of [...angles,null]){const hx=a!=null?Math.cos(a)*hs*1.55:0,hy=a!=null?Math.sin(a)*hs*1.55:0;ctx.beginPath();for(let k=0;k<6;k++){const ka=k/6*6.283;ctx.lineTo(hx+Math.cos(ka)*hs*.52,hy+Math.sin(ka)*hs*.52);}ctx.closePath();ctx.strokeStyle=`rgba(${rgb},.5)`;ctx.lineWidth=1;ctx.fillStyle=`rgba(${rgb},.08)`;ctx.fill();ctx.stroke();}
          break; }
        case 'minimal': {
          ctx.beginPath();ctx.arc(0,0,27,0,6.283);ctx.strokeStyle=`rgba(${rgb},.2)`;ctx.lineWidth=1;ctx.stroke();
          ctx.beginPath();ctx.arc(0,0,17,0,6.283);ctx.strokeStyle=`rgba(${rgb},.7)`;ctx.lineWidth=1.5;ctx.shadowColor=`rgba(${rgb},.8)`;ctx.shadowBlur=8;ctx.stroke();ctx.shadowBlur=0;
          ctx.beginPath();ctx.moveTo(-20,0);ctx.lineTo(20,0);ctx.strokeStyle=`rgba(${rgb},.45)`;ctx.lineWidth=1;ctx.stroke();
          ctx.beginPath();ctx.moveTo(0,-20);ctx.lineTo(0,20);ctx.stroke();
          ctx.fillStyle=`rgba(${rgb},1)`;ctx.beginPath();ctx.arc(0,0,3.2,0,6.283);ctx.fill();
          break; }
        case 'crystal': {
          const cv2=[[1,0],[-1,0],[0,1],[0,-1]], sz=20;
          for(const [x,y] of cv2){ ctx.beginPath(); ctx.moveTo(0,-sz*.9); ctx.lineTo(x*sz,y*sz*.5); ctx.strokeStyle=`rgba(${rgb},.55)`; ctx.lineWidth=1; ctx.stroke();
            ctx.beginPath(); ctx.moveTo(0,sz*.9); ctx.lineTo(x*sz,y*sz*.5); ctx.stroke(); }
          ctx.fillStyle=`rgba(${rgb},.9)`;
          for(const [x,y] of [[0,-sz*.9],[0,sz*.9],[sz,0],[-sz,0],[0,sz*.5],[0,-sz*.5]]){ ctx.beginPath(); ctx.arc(x,y,2,0,6.283); ctx.fill(); }
          break; }
        case 'saturn': {
          const g2=ctx.createRadialGradient(0,0,0,0,0,12); g2.addColorStop(0,'rgba(255,255,255,.9)'); g2.addColorStop(.6,`rgba(${rgb},.7)`); g2.addColorStop(1,'transparent');
          ctx.fillStyle=g2; ctx.beginPath(); ctx.arc(0,0,12,0,6.283); ctx.fill();
          ctx.save(); ctx.rotate(-.35); ctx.beginPath(); ctx.ellipse(0,0,27,8,0,0,6.283); ctx.strokeStyle=`rgba(${rgb},.7)`; ctx.lineWidth=1.4; ctx.stroke(); ctx.restore();
          break; }
        case 'helix': {
          for(let i=0;i<12;i++){ const ph=i/12*Math.PI*4;
            const x1=Math.cos(ph)*13, y1=(i/12-.5)*44, x2=Math.cos(ph+Math.PI)*13;
            if(i%2===0){ ctx.strokeStyle=`rgba(${rgb},.3)`; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y1); ctx.stroke(); }
            ctx.fillStyle=`rgba(${rgb},.85)`; ctx.beginPath(); ctx.arc(x1,y1,1.8,0,6.283); ctx.fill();
            ctx.beginPath(); ctx.arc(x2,y1,1.8,0,6.283); ctx.fill(); }
          break; }
      }
      ctx.restore();
    }
  },

  _renderBgPanel() {
    const panel = document.getElementById('tawee-bg-panel'); if(!panel) return;
    const open = this.st.panel==='background';
    panel.style.transform = open?'translateX(0)':'translateX(105%)';
    if (!open) return;
    const grid = document.getElementById('tawee-bg-grid');
    if (grid) {
      grid.innerHTML = BG_ANIM_STYLES.map(s => {
        const active = s.id===this.cfg.bgAnim;
        return `<button onclick="TAWEE.setBgAnim('${s.id}')" style="display:flex;flex-direction:column;align-items:flex-start;gap:5px;padding:14px;border-radius:14px;border:1px solid ${active?'rgba(255,255,255,.40)':'rgba(255,255,255,.08)'};background:${active?'rgba(255,255,255,.07)':'rgba(255,255,255,.02)'};cursor:pointer;transition:all .2s;text-align:left;">
          <span style="font-size:13px;font-weight:600;color:${active?'var(--accent)':'#b9c0cd'};">${s.name}${active?' ✓':''}</span>
          <span style="font-size:10.5px;color:rgba(255,255,255,.4);line-height:1.4;">${s.desc}</span>
        </button>`;
      }).join('');
    }
    const opVal = Math.round((this.cfg.bgAnimOpacity ?? 0.5)*100);
    const spVal = Math.round((this.cfg.bgAnimSpeed ?? 1)*100);
    const opSlider = document.getElementById('tawee-bg-opacity-slider'); if(opSlider) opSlider.value = opVal;
    const opLbl = document.getElementById('tawee-bg-opacity-val'); if(opLbl) opLbl.textContent = opVal+'%';
    const spSlider = document.getElementById('tawee-bg-speed-slider'); if(spSlider) spSlider.value = spVal;
    const spLbl = document.getElementById('tawee-bg-speed-val'); if(spLbl) spLbl.textContent = (spVal/100).toFixed(1)+'x';
  },

  // ─────────────────────────────────────────────────────────
  // BACKGROUND ANIMATION ENGINE — matrix / fire / rain / snow
  // ใช้สี theme ปัจจุบัน (PALETTES[cfg.theme].rgb) วาดด้วย canvas ชั้นล่างสุด
  // ปรับความเข้ม (bgAnimOpacity) และความเร็ว (bgAnimSpeed) ได้จากแผงตั้งค่า
  // ─────────────────────────────────────────────────────────
  initBgAnimCanvas() {
    const cv = document.getElementById('tawee-bg-anim-canvas');
    if (!cv) return;
    this._bgCv = cv;
    this._bgCtx = cv.getContext('2d');
    const resize = () => {
      cv.width = window.innerWidth;
      cv.height = window.innerHeight;
      this._bgParticles = null; // บังคับ re-seed ตามขนาดจอใหม่
    };
    resize();
    window.addEventListener('resize', resize);
  },

  setBgAnim(id) {
    this.cfg.bgAnim = id;
    this.saveCfg();
    this._startBgAnim();
    this._renderBgPanel();
  },
  setBgAnimOpacity(val) {
    this.cfg.bgAnimOpacity = Number(val)/100;
    this.saveCfg();
    const el = document.getElementById('tawee-bg-opacity-val'); if (el) el.textContent = val+'%';
  },
  setBgAnimSpeed(val) {
    this.cfg.bgAnimSpeed = Number(val)/100;
    this.saveCfg();
    const el = document.getElementById('tawee-bg-speed-val'); if (el) el.textContent = (Number(val)/100).toFixed(1)+'x';
  },

  _startBgAnim() {
    if (this._bgRAF) cancelAnimationFrame(this._bgRAF);
    this._bgParticles = null;
    const ctx = this._bgCtx;
    if (!ctx) return;
    ctx.clearRect(0,0,this._bgCv.width,this._bgCv.height);
    if (this.cfg.bgAnim === 'none') { this._bgRAF = null; return; }
    const loop = () => {
      this._bgDrawFrame();
      this._bgRAF = requestAnimationFrame(loop);
    };
    this._bgRAF = requestAnimationFrame(loop);
  },

  _bgDrawFrame() {
    const ctx = this._bgCtx, cv = this._bgCv;
    if (!ctx || !cv) return;
    const W = cv.width, H = cv.height;
    const rgb = (PALETTES[this.cfg.theme]||PALETTES.emerald).rgb;
    const speed = this.cfg.bgAnimSpeed ?? 1;
    const opacity = this.cfg.bgAnimOpacity ?? 0.5;
    ctx.clearRect(0,0,W,H);
    switch (this.cfg.bgAnim) {
      case 'matrix': this._bgFrameMatrix(ctx,W,H,rgb,speed,opacity); break;
      case 'fire':   this._bgFrameFire(ctx,W,H,rgb,speed,opacity); break;
      case 'rain':   this._bgFrameRain(ctx,W,H,rgb,speed,opacity); break;
      case 'snow':   this._bgFrameSnow(ctx,W,H,rgb,speed,opacity); break;
    }
  },

  _bgFrameMatrix(ctx,W,H,rgb,speed,opacity) {
    const fontSize = 16;
    const cols = Math.max(1, Math.floor(W/fontSize));
    if (!this._bgParticles || this._bgParticles.length !== cols) {
      this._bgParticles = Array.from({length:cols}, () => ({ y: Math.random()*H/fontSize, len: 8+Math.floor(Math.random()*10) }));
    }
    ctx.font = fontSize+'px monospace';
    ctx.textBaseline = 'top';
    this._bgParticles.forEach((col,i) => {
      for (let t=0; t<col.len; t++) {
        const yPix = (col.y - t) * fontSize;
        if (yPix < 0 || yPix > H) continue;
        const a = (1 - t/col.len) * opacity;
        ctx.fillStyle = t===0 ? `rgba(255,255,255,${Math.min(1,a+0.3)})` : `rgba(${rgb},${a})`;
        ctx.fillText(Math.random()>0.5?'1':'0', i*fontSize, yPix);
      }
      col.y += 0.15 * speed;
      if ((col.y - col.len) * fontSize > H) col.y = -Math.random()*20;
    });
  },

  _bgSpawnFire(W,H) {
    return { x: Math.random()*W, y: H+Math.random()*20, vx:(Math.random()-0.5)*0.6, vy:-(1+Math.random()*2), r:6+Math.random()*14, life:60+Math.random()*60, maxLife:120 };
  },
  _bgFrameFire(ctx,W,H,rgb,speed,opacity) {
    if (!this._bgParticles) this._bgParticles = Array.from({length:140}, () => this._bgSpawnFire(W,H));
    this._bgParticles.forEach((p) => {
      const a = Math.max(0,(p.life/p.maxLife)) * opacity;
      const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,Math.max(p.r,0.1));
      g.addColorStop(0, `rgba(255,240,220,${a})`);
      g.addColorStop(0.4, `rgba(${rgb},${a*0.85})`);
      g.addColorStop(1, `rgba(${rgb},0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(p.x,p.y,Math.max(p.r,0.1),0,6.283); ctx.fill();
      p.x += p.vx * speed;
      p.y += p.vy * speed;
      p.vx += (Math.random()-0.5)*0.15;
      p.r *= 0.985;
      p.life--;
      if (p.life <= 0 || p.r < 0.5) Object.assign(p, this._bgSpawnFire(W,H));
    });
  },

  _bgSpawnRain(W,H,rand) {
    return { x: Math.random()*W, y: rand?Math.random()*H:-20, vy:8+Math.random()*8, len:14+Math.random()*10 };
  },
  _bgFrameRain(ctx,W,H,rgb,speed,opacity) {
    if (!this._bgParticles) this._bgParticles = Array.from({length:150}, () => this._bgSpawnRain(W,H,true));
    ctx.strokeStyle = `rgba(${rgb},${opacity*0.6})`;
    ctx.lineWidth = 1;
    this._bgParticles.forEach((p) => {
      ctx.beginPath();
      ctx.moveTo(p.x,p.y);
      ctx.lineTo(p.x-2, p.y+p.len);
      ctx.stroke();
      p.x -= 1.5*speed;
      p.y += p.vy*speed;
      if (p.y > H) Object.assign(p, this._bgSpawnRain(W,H,false));
    });
  },

  _bgSpawnSnow(W,H,rand) {
    return { x: Math.random()*W, y: rand?Math.random()*H:-10, vy:0.4+Math.random()*1, r:1.5+Math.random()*2.5, phase:Math.random()*6.283, a:0.4+Math.random()*0.6 };
  },
  _bgFrameSnow(ctx,W,H,rgb,speed,opacity) {
    if (!this._bgParticles) this._bgParticles = Array.from({length:90}, () => this._bgSpawnSnow(W,H,true));
    this._bgParticles.forEach((p) => {
      ctx.beginPath();
      ctx.fillStyle = `rgba(${rgb},${opacity*p.a})`;
      ctx.arc(p.x,p.y,p.r,0,6.283);
      ctx.fill();
      p.phase += 0.02*speed;
      p.x += Math.sin(p.phase)*0.6;
      p.y += p.vy*speed;
      if (p.y > H) Object.assign(p, this._bgSpawnSnow(W,H,false));
    });
  },

  _drawSphereIcon(id, rgb) {
    const cv = document.getElementById(id); if (!cv) return;
    const ctx = cv.getContext('2d'); const W=26,H=26;
    ctx.clearRect(0,0,W,H); ctx.save(); ctx.translate(W/2,H/2);
    const g=ctx.createRadialGradient(0,0,0,0,0,10);g.addColorStop(0,'rgba(255,255,255,.8)');g.addColorStop(.5,`rgba(${rgb},.6)`);g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(0,0,10,0,6.283);ctx.fill();
    for(let i=0;i<14;i++){const a=i/14*6.283,r2=6+Math.sin(i*1.5)*2;ctx.fillStyle=`rgba(${rgb},.75)`;ctx.beginPath();ctx.arc(Math.cos(a)*r2,Math.sin(a)*r2,.8,0,6.283);ctx.fill();}
    ctx.restore();
  },

  _drawDashIcons() {
    this._drawSphereIcon('tawee-dash-icon-post', '63,214,255');
    this._drawSphereIcon('tawee-dash-icon-finance', '255,180,84');
    this._drawSphereIcon('tawee-dash-icon-mt5', '129,140,248');
  },

  _esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>'); },

  // ─────────────────────────────────────────────────────────
  // PUBLIC ACTIONS  (called from HTML onclick)
  // ─────────────────────────────────────────────────────────
  openPanel(name)  { this.st.panel=name; this.render(); },
  closePanel()     { this.st.panel=null; this.render(); },

  toggleFullscreen() {
    if (!document.fullscreenElement) (document.getElementById('tawee-root')||document.documentElement).requestFullscreen?.();
    else document.exitFullscreen?.();
  },

  DASHBOARD_PATHS: {
    post:    './AI Agent Dashboard ออกแบบ/TAWEE Dashboard.dc.html',
    finance: './finance/Finance AI Dashboard.dc.html',
    mt5:     './mt5/MT5 Dashboard.html',
  },

  openDashboard(kind, nav) {
    const path = this.DASHBOARD_PATHS[kind] || this.DASHBOARD_PATHS.post;
    const url = nav ? `${path}?nav=${encodeURIComponent(nav)}` : path;
    window.location.href = encodeURI(url);
  },

  onKeyInput(val)  { this.st.keyInput=val; },

  
  onGeminiKeyInput(val) { this._tmpGemini = val; },
  saveGeminiKey() {
    if (this._tmpGemini) {
      this.cfg.geminiKey = this._tmpGemini;
      this.saveCfg();
      const s = document.getElementById('tawee-gemini-saved');
      if(s) { s.style.display='block'; setTimeout(()=>s.style.display='none', 2500); }
    }
  },
  clearGeminiKey() {
    this.cfg.geminiKey = '';
    this.saveCfg();
    const inp = document.getElementById('tawee-gemini-input');
    if(inp) inp.value = '';
    this._tmpGemini = '';
  },

  saveApiKey() {
    const k = (document.getElementById('tawee-key-input')?.value||'').trim();
    if (!k) { this.showErr('กรุณากรอก API key'); return; }
    this.cfg.apiKey=k; this.st.keySaved=true; this.saveCfg(); this.render();
  },

  clearApiKey() {
    this.cfg.apiKey=''; this.st.keySaved=false;
    const ki=document.getElementById('tawee-key-input'); if(ki) ki.value='';
    this.saveCfg(); this.render();
  },

  onProxyUrlInput(val)    { this.st.proxyUrlInput=val; },
  onProxySecretInput(val) { this.st.proxySecretInput=val; },

  saveProxyConfig() {
    const url = (document.getElementById('tawee-proxy-url-input')?.value||'').trim();
    const secret = (document.getElementById('tawee-proxy-secret-input')?.value||'').trim();
    if (!url || !secret) { this.showErr('กรุณากรอกทั้ง Worker URL และรหัสลับ'); return; }
    this.cfg.proxyUrl=url; this.cfg.proxySecret=secret; this.st.proxySaved=true;
    this.saveCfg(); this.loadVoices(); this.render();
  },

  clearProxyConfig() {
    this.cfg.proxyUrl=''; this.cfg.proxySecret=''; this.st.proxySaved=false;
    const pu=document.getElementById('tawee-proxy-url-input'); if(pu) pu.value='';
    const psec=document.getElementById('tawee-proxy-secret-input'); if(psec) psec.value='';
    this.saveCfg(); this.loadVoices(); this.render();
  },

  setModel(val)  { this.cfg.model=val; this.saveCfg(); },

  toggleSpeak()  {
    this.cfg.speak=!this.cfg.speak;
    if (!this.cfg.speak) this._resetTtsBargeIn();
    this.saveCfg(); this._renderSettingsPanel();
  },

  setInput(val)  { this.st.input=val; },
  onKeyDown(e)   { if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();this.send();} },

  setWeatherCity(val) {
    this.cfg.weatherCity=val;
    // Try to geocode (Open-Meteo geocoding)
    clearTimeout(this._geoT);
    this._geoT = setTimeout(async () => {
      try {
        const r = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(val)}&count=1&language=th&format=json`);
        const d = await r.json();
        if (d.results && d.results[0]) {
          this.cfg.weatherLat = d.results[0].latitude;
          this.cfg.weatherLon = d.results[0].longitude;
          this.cfg.weatherCity= val;
          this.saveCfg();
        }
      } catch(e) {}
    }, 1200);
  },

  saveProfile(text) { try { localStorage.setItem('tawee_profile', text); } catch(e) {} },

  // ใช้ Worker STT เป็นทางหลักเมื่อมี proxy config เพื่อไม่ต้องพึ่ง Google Web Speech ของเบราว์เซอร์
  // ตัวตรวจจับความเงียบจะหยุดอัดอัตโนมัติหลังพูดจบ และกดไมค์ซ้ำเพื่อหยุดเองได้
  _canUseServerStt() {
    return !!(
      this.cfg.proxyUrl && this.cfg.proxySecret &&
      navigator.mediaDevices && navigator.mediaDevices.getUserMedia &&
      window.MediaRecorder
    );
  },

  _stopPlaybackForListening() {
    this._resetTtsBargeIn();
  },

  async _startServerRecognition() {
    if (this._sttStarting || this.st.listening) return;
    this._sttStarting = true;
    this._sttDiscard = false;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation:true, noiseSuppression:true, autoGainControl:true },
      });
      this._sttStream = stream;
      const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'];
      const mimeType = mimeTypes.find(type => !MediaRecorder.isTypeSupported || MediaRecorder.isTypeSupported(type));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      const chunks = [];
      const startedAt = performance.now();

      this._sttRecorder = recorder;
      this._sttChunks = chunks;
      recorder.ondataavailable = event => { if (event.data && event.data.size) chunks.push(event.data); };
      recorder.onerror = () => {
        this._sttDiscard = true;
        this.showErr('อัดเสียงไม่สำเร็จ กรุณาลองใหม่');
        this._stopServerRecording(true);
      };
      recorder.onstop = async () => {
        const discard = this._sttDiscard;
        const blob = new Blob(chunks, { type: recorder.mimeType || mimeType || 'audio/webm' });
        this._cleanupServerRecording();
        this.st.listening = false;
        if (this.st.status === 'listening') this.setStatus(discard ? 'standby' : 'thinking');
        this.render();
        if (discard) return;
        if (blob.size < 500) {
          this.setStatus('standby');
          this.showErr('ไม่ได้ยินเสียงพูด กรุณาลองใหม่');
          return;
        }
        // requestId เดียวกันนี้จะเดินทางผ่าน STT → LLM → TTS → เล่นเสียง เพื่อวัดเวลารวมทั้ง pipeline
        const requestId = 'req_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
        this._traceStart(requestId);
        this._traceMark(requestId, 'speech_end');
        await this._transcribeServerAudio(blob, requestId);
      };

      recorder.start(250);
      this.st.listening = true;
      this.setStatus('listening');
      this.render();
      this._startSilenceMonitor(stream, recorder, startedAt);
      this._sttMaxTimer = setTimeout(() => this._stopServerRecording(false), 12000);
    } catch (e) {
      this._cleanupServerRecording();
      this.st.listening = false;
      this.setStatus('standby');
      if (e && (e.name === 'NotAllowedError' || e.name === 'SecurityError')) {
        this.showErr('ไม่ได้รับสิทธิ์ใช้ไมค์ — อนุญาตไมค์ให้เว็บไซต์นี้แล้วลองใหม่');
      } else if (e && e.name === 'NotFoundError') {
        this.showErr('ไม่พบไมโครโฟนในเครื่อง');
      } else {
        this.showErr('เปิดไมค์ไม่สำเร็จ: ' + (e && e.message ? e.message : 'unknown error'));
      }
      this.render();
    } finally {
      this._sttStarting = false;
    }
  },

  _startSilenceMonitor(stream, recorder, startedAt) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    try {
      const ctx = new AudioCtx();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const samples = new Uint8Array(analyser.fftSize);
      let heardSpeech = false;
      let quietSince = 0;
      this._sttAudioContext = ctx;
      const tick = () => {
        if (this._sttRecorder !== recorder || recorder.state !== 'recording') return;
        analyser.getByteTimeDomainData(samples);
        let sum = 0;
        for (let i = 0; i < samples.length; i++) {
          const value = (samples[i] - 128) / 128;
          sum += value * value;
        }
        const rms = Math.sqrt(sum / samples.length);
        const now = performance.now();
        if (now - startedAt > 350 && rms > 0.025) {
          heardSpeech = true;
          quietSince = 0;
        } else if (heardSpeech) {
          if (!quietSince) quietSince = now;
          if (now - quietSince >= 1000) {
            this._stopServerRecording(false);
            return;
          }
        }
        this._sttRaf = requestAnimationFrame(tick);
      };
      tick();
    } catch (e) {
      // ถ้า AudioContext ใช้ไม่ได้ ยังหยุดได้ด้วยการกดไมค์ซ้ำหรือ timeout 12 วินาที
    }
  },

  _stopServerRecording(discard) {
    if (discard) this._sttDiscard = true;
    clearTimeout(this._sttMaxTimer);
    if (this._sttRaf) cancelAnimationFrame(this._sttRaf);
    const recorder = this._sttRecorder;
    if (recorder && recorder.state !== 'inactive') {
      try { recorder.stop(); } catch(e) { this._cleanupServerRecording(); }
    }
  },

  _cleanupServerRecording() {
    clearTimeout(this._sttMaxTimer);
    if (this._sttRaf) cancelAnimationFrame(this._sttRaf);
    if (this._sttAudioContext && this._sttAudioContext.state !== 'closed') {
      this._sttAudioContext.close().catch(() => {});
    }
    if (this._sttStream) this._sttStream.getTracks().forEach(track => track.stop());
    this._sttMaxTimer = null;
    this._sttRaf = null;
    this._sttAudioContext = null;
    this._sttStream = null;
    this._sttRecorder = null;
    this._sttChunks = null;
  },

  async _transcribeServerAudio(blob, requestId) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000); // STT timeout แยกจาก LLM/TTS
    try {
      if (requestId) this._traceMark(requestId, 'stt_started');
      const form = new FormData();
      const ext = blob.type.includes('mp4') ? 'm4a' : 'webm';
      form.append('audio', blob, `tawee-${Date.now()}.${ext}`);
      const baseUrl = this.cfg.proxyUrl.replace(/\/+$/, '');
      const res = await fetch(`${baseUrl}/transcribe`, {
        method: 'POST',
        headers: { 'x-tawee-secret': this.cfg.proxySecret },
        body: form,
        signal: controller.signal,
      });
      let data = {};
      try { data = await res.json(); } catch(e) {}
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      if (requestId) this._traceMark(requestId, 'stt_completed');
      const text = String(data.text || '').trim();
      if (!text || text === 'ว่างเปล่า') {
        this.setStatus('standby');
        this.showErr('ไม่ได้ยินคำพูดชัดเจน กรุณาลองใหม่');
        return;
      }
      await this.send(text, { fast: true, requestId });
    } catch (e) {
      this.setStatus('standby');
      const reason = e && e.name === 'AbortError' ? 'หมดเวลารอระบบแปลงเสียง' : (e && e.message ? e.message : 'unknown error');
      this.showErr('แปลงเสียงไม่สำเร็จ: ' + reason);
    } finally {
      clearTimeout(timeout);
      this.render();
    }
  },

  // ใช้ Browser Web Speech เป็น fallback เฉพาะเมื่อยังไม่ได้ตั้งค่า Worker
  micClick() {
    if (this.st.listening) {
      if (this._sttRecorder && this._sttRecorder.state !== 'inactive') {
        this._stopServerRecording(false);
        return;
      }
      if (this.recog) { try { this.recog.stop(); } catch(e){} }
      return;
    }
    this._stopPlaybackForListening();
    if (this._canUseServerStt()) {
      this._startServerRecognition();
      return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      this.showErr('เบราว์เซอร์นี้ไม่รองรับการฟังเสียงพูด ลองใช้ Chrome หรือ Edge');
      return;
    }
    const recog = new SR();
    recog.lang = 'th-TH';
    recog.continuous = false;
    recog.interimResults = false;
    recog.maxAlternatives = 1;
    // เบราว์เซอร์บางกรณีเชื่อมต่อเซิร์ฟเวอร์แปลงเสียงของ Google ไม่ได้ (เน็ต/ภูมิภาค) แล้ว onend ยิงเฉยๆ
    // โดยไม่ผ่าน onresult หรือ onerror เลย — เดิมกรณีนี้จะเงียบสนิทไม่มีอะไรขึ้น ต้องกันด้วย flag นี้
    let handled = false;
    recog.onstart = () => { this.st.listening = true; this.setStatus('listening'); this.render(); };
    recog.onresult = (e) => {
      handled = true;
      const text = (e.results[0] && e.results[0][0] && e.results[0][0].transcript || '').trim();
      if (text) this.send(text, { fast: true });
      else this.showErr('ไม่ได้ยินเสียงพูดเลยค่ะ ลองพูดดัง ๆ ชัด ๆ อีกครั้ง');
    };
    recog.onerror = (e) => {
      handled = true;
      if (e.error === 'no-speech') this.showErr('ไม่ได้ยินเสียงพูดเลยค่ะ ลองพูดดัง ๆ ชัด ๆ อีกครั้ง');
      else if (e.error === 'not-allowed') this.showErr('ไม่ได้รับสิทธิ์ใช้ไมค์ — ไปที่ตั้งค่าเบราว์เซอร์อนุญาตไมค์ให้เว็บนี้ แล้วลองใหม่');
      else if (e.error === 'network') this.showErr('เชื่อมต่อระบบแปลงเสียงไม่ได้ — เช็คอินเทอร์เน็ตแล้วลองใหม่');
      else this.showErr('ฟังเสียงไม่สำเร็จ: ' + e.error);
    };
    recog.onend = () => {
      clearTimeout(this._recogTimeout);
      this.st.listening = false;
      if (this.st.status === 'listening') this.setStatus('standby');
      if (!handled) this.showErr('ฟังไม่สำเร็จค่ะ (ไม่มีการตอบกลับจากระบบแปลงเสียง) ลองใหม่อีกครั้ง');
      this.render();
    };
    this.recog = recog;
    try {
      recog.start();
      // เคสร้ายสุด: เบราว์เซอร์เชื่อมเซิร์ฟเวอร์แปลงเสียงของ Google ไม่ได้แล้ว "ค้าง" เฉยๆ
      // ไม่ยิง onresult/onerror/onend อะไรเลยสักตัว (เจอจริงจากการดูล็อกสด — ไม่มี request เข้ามาที่ฝั่งเราเลย)
      // ต้องบังคับตัดเองหลัง 10 วิ ไม่งั้นจะค้างสถานะ "กำลังฟัง..." ตลอดไป
      clearTimeout(this._recogTimeout);
      this._recogTimeout = setTimeout(() => {
        if (!handled && this.st.listening) {
          try { recog.abort(); } catch (e) {}
          this.st.listening = false;
          this.setStatus('standby');
          this.showErr('เชื่อมต่อระบบฟังเสียงไม่ได้ (รอนานเกินไป) — เช็คอินเทอร์เน็ตแล้วลองใหม่ หรือพิมพ์แทนได้');
          this.render();
        }
      }, 10000);
    } catch (e) { this.showErr('เริ่มฟังเสียงไม่สำเร็จ: ' + e.message); }
  },
};
