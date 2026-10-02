/* ══════════ 音 ══════════
   役割：発射／着弾／素材ごとの破片／構造の軋み／崩落の胴鳴り／瓦礫の余韻／街の環境音。
   スマートフォンのスピーカーでも分かる中低域と短い立ち上がりを使い、マスター（コンプレッサー）で
   連鎖中の音割れを防ぐ。同時発音数と時間あたりの発音予算で鳴りっぱなしを抑える。
   距離で減衰し、カメラから見た左右で定位する */
const Snd=(()=>{
  let ac=null,nb=null,bud=0,hum=null,master=null,comp=null,voices=0;
  const MAXV=30;
  function A(){ if(!S.sound) return null;
    try{ if(!ac){ const C=window.AudioContext||window.webkitAudioContext; if(!C) return null;
      ac=new C(); const L=ac.sampleRate*2, b=ac.createBuffer(1,L,ac.sampleRate), d=b.getChannelData(0);
      for(let i=0;i<L;i++) d[i]=Math.random()*2-1; nb=b;
      comp=ac.createDynamicsCompressor(); comp.threshold.value=-14; comp.knee.value=18; comp.ratio.value=6; comp.attack.value=.004; comp.release.value=.18;
      master=ac.createGain(); master.gain.value=.85;
      master.connect(comp); comp.connect(ac.destination); }
      if(ac.state==='suspended') ac.resume(); return ac; }catch(e){ return null; } }
  const LAT=0.025;
  /* 距離減衰と左右の定位。位置が無ければそのまま */
  function sp(x,y,z){
    if(x===undefined||x===null||typeof camera==='undefined'||!camera) return {g:1,pan:0};
    const dx=x-camera.position.x, dy=y-camera.position.y, dz=z-camera.position.z;
    const d=Math.hypot(dx,dy,dz);
    const g=1/(1+d/150);
    const rx=Math.cos(cam.yaw), rz=-Math.sin(cam.yaw);          // カメラの右方向（水平）
    const pan=d>1?Math.max(-1,Math.min(1,(dx*rx+dz*rz)/d))*0.7:0;
    return {g:g,pan:pan};
  }
  function out(a,g,pos){
    const s=sp(pos&&pos[0],pos&&pos[1],pos&&pos[2]);
    let node=g;
    if(s.pan!==0 && a.createStereoPanner){ const pn=a.createStereoPanner(); pn.pan.value=s.pan; g.connect(pn); node=pn; }
    node.connect(master);
    return s.g;
  }
  function track(n){ voices++; n.onended=()=>{ voices--; }; }
  function N(dur,vol,ty,f0,f1,q,pos){ const a=A(); if(!a||bud<=0||voices>=MAXV) return; bud--;
    const t0=a.currentTime+LAT;
    const s=a.createBufferSource(); s.buffer=nb; s.playbackRate.value=.5+Math.random()*.8;
    const f=a.createBiquadFilter(); f.type=ty; f.Q.value=q||1;
    f.frequency.setValueAtTime(f0,t0);
    f.frequency.exponentialRampToValueAtTime(Math.max(28,f1),t0+dur);
    const g=a.createGain();
    const k=out(a,g,pos);
    g.gain.setValueAtTime(Math.max(.0009,vol*k),t0);
    g.gain.exponentialRampToValueAtTime(.0008,t0+dur);
    s.connect(f); f.connect(g); track(s); s.start(t0); s.stop(t0+dur); }
  function T(f0,f1,dur,vol,ty,pos){ const a=A(); if(!a||bud<=0||voices>=MAXV) return; bud--;
    const t0=a.currentTime+LAT;
    const o=a.createOscillator(); o.type=ty||'sine';
    o.frequency.setValueAtTime(f0,t0);
    o.frequency.exponentialRampToValueAtTime(Math.max(16,f1),t0+dur);
    const g=a.createGain();
    const k=out(a,g,pos);
    g.gain.setValueAtTime(Math.max(.0009,vol*k),t0);
    g.gain.exponentialRampToValueAtTime(.0008,t0+dur);
    o.connect(g); track(o); o.start(t0); o.stop(t0+dur); }
  /* 種類ごとの連打制限（破片音が重なって団子にならないように） */
  const lastAt={};
  function gate(key,ms){ const n=performance.now(); if(n-(lastAt[key]||0)<ms) return false; lastAt[key]=n; return true; }
  const P=(x,y,z)=>(x===undefined?null:[x,y,z]);
  return {
    f(dt){ bud=Math.min(12, bud+(dt||.016)*480); }, kick(){ A(); },
    pause(){ try{ this.humOff(); if(ac&&ac.state==='running') ac.suspend(); }catch(e){} },
    resume(){ try{ if(ac&&S.sound&&ac.state==='suspended') ac.resume(); }catch(e){} },
    voices(){ return voices; },
    blast(p,x,y,z){
      // 爆発音：①鋭い破裂音 ②胴鳴り ③低音 ④腹に来る超低音 ⑤遅れて降る瓦礫の音
      const pos=P(x,y,z);
      N(.10+p*.08,Math.min(.45,.20+p*.28),'highpass',2600,900,.7,pos);
      N(.6+p*.7,Math.min(.55,.22+p*.3),'lowpass',1700,45,1,pos);
      T(130-p*60,24,.7+p*.7,.45,'sine',pos);
      T(62,26,1.0+p*1.2,.28+p*.2,'sine',pos);
      if(p>.35) setTimeout(()=>N(.9+p,Math.min(.16,.07+p*.1),'bandpass',1800,600,1.4,pos),170+Math.random()*130);
    },
    rumble(){ N(2.2,.4,'lowpass',240,32,.7); T(46,18,2.4,.32,'sine'); },
    /* 低周波の地鳴り。大崩落や核のあと、数秒かけて減衰 */
    quake(v,sec){
      const a=A(); if(!a) return;
      const dur=sec||9, amp=Math.min(.5,(v||1)*.34);
      try{
        for(const f of [28,31.5]){
          const o=a.createOscillator(); o.type='sine'; o.frequency.value=f;
          const g=a.createGain();
          g.gain.setValueAtTime(0,a.currentTime);
          g.gain.linearRampToValueAtTime(amp, a.currentTime+.35);
          g.gain.exponentialRampToValueAtTime(.0008, a.currentTime+dur);
          o.connect(g); g.connect(master); track(o); o.start(); o.stop(a.currentTime+dur+.1);
        }
        const nz=a.createBufferSource(); nz.buffer=nb; nz.loop=true;
        const bp=a.createBiquadFilter(); bp.type='lowpass';
        bp.frequency.setValueAtTime(160,a.currentTime);
        bp.frequency.exponentialRampToValueAtTime(42,a.currentTime+dur);
        const ng=a.createGain();
        ng.gain.setValueAtTime(0,a.currentTime);
        ng.gain.linearRampToValueAtTime(amp*.5, a.currentTime+.4);
        ng.gain.exponentialRampToValueAtTime(.0006, a.currentTime+dur);
        nz.connect(bp); bp.connect(ng); ng.connect(master); track(nz);
        nz.start(); nz.stop(a.currentTime+dur+.1);
      }catch(e){}
    },
    thud(v,x,y,z){ const pos=P(x,y,z); N(.3,v,'lowpass',500,60,1,pos); T(90,36,.26,v*.7,'sine',pos); },
    crumble(v,x,y,z){ N(.16,Math.min(.24,v),'bandpass',2000,700,1.6,P(x,y,z)); },
    /* 構造が軋む：倒れ始めの数百ミリ秒。低いうなりと、金属が擦れる高い成分 */
    creak(x,y,z){ if(!gate('creak',300)) return; const pos=P(x,y,z);
      T(95,52,.62,.30,'sawtooth',pos); N(.55,.16,'bandpass',900,2600,6,pos); N(.5,.22,'lowpass',320,120,1,pos); },
    /* 崩落の胴鳴り：低い連続音＋瓦礫が降る音を時間差で */
    collapse(v,x,y,z){ const pos=P(x,y,z), k=Math.min(1,v||1);
      N(.9+k*.8,.30+k*.2,'lowpass',420,48,1,pos); T(56,30,1.1+k,.30,'sine',pos);
      for(let i=0;i<3+Math.round(k*4);i++) setTimeout(()=>N(.12+Math.random()*.1,.10+k*.08,'bandpass',900+Math.random()*1500,400,2,pos),120+i*90+Math.random()*120); },
    /* 瓦礫の余韻：細かな破片が時間差で落ちる */
    rubble(x,y,z,n){ const pos=P(x,y,z), c=Math.min(6,2+Math.round((n||10)/40));
      for(let i=0;i<c;i++) setTimeout(()=>N(.06+Math.random()*.06,.07+Math.random()*.05,'bandpass',1200+Math.random()*2400,500,3,pos),60+i*110+Math.random()*160); },
    /* 素材ごとの破片音：ガラスは高く細かく、金属は鳴り、木は乾いた割れ、コンクリートは低い欠け */
    glass(x,y,z){ if(!gate('glass',70)) return; const pos=P(x,y,z);
      for(let i=0;i<3;i++) setTimeout(()=>N(.05+Math.random()*.05,.09,'highpass',3800+Math.random()*2500,2500,2.5,pos),i*45+Math.random()*40); },
    metal(x,y,z){ if(!gate('metal',120)) return; const pos=P(x,y,z);
      T(900+Math.random()*900,300+Math.random()*200,.35,.12,'triangle',pos); N(.12,.10,'bandpass',2400,900,4,pos); },
    wood(x,y,z){ if(!gate('wood',90)) return; const pos=P(x,y,z);
      N(.09,.16,'bandpass',700,250,1.2,pos); N(.05,.08,'highpass',2200,1200,1.5,pos); },
    concrete(x,y,z){ if(!gate('conc',80)) return; const pos=P(x,y,z);
      N(.10,.14,'lowpass',900,180,1,pos); },
    mat(m,x,y,z){
      if(m===2||m===3||m===4||m===37||m===27||m===28||m===41) this.glass(x,y,z);
      else if(m===5||m===25||m===20||m===14||m===15||m===18||m===10||m===30||m===32) this.metal(x,y,z);
      else if(m===43||m===44) this.wood(x,y,z);
      else if(m===7||m===8||m===11||m===16||m===17||m===19||m===38||m===39) this.glass(x,y,z);
      else this.concrete(x,y,z);
    },
    rail(){ T(160,3000,.14,.24,'square'); N(.34,.2,'bandpass',900,3200,2.4); },
    cut(x,y,z){ const pos=P(x,y,z); T(3400,320,.26,.18,'sawtooth',pos); N(.2,.12,'highpass',3400,1200,1,pos); },
    beam(){ T(80,150,1.6,.22,'sawtooth'); N(1.6,.2,'bandpass',380,2000,3); },
    suck(){ T(60,1400,2.2,.16,'sine'); },
    woosh(){ N(.6,.14,'bandpass',300,1800,1.5); },
    jolt(v){ T(64,34,.09+(v||0)*.1,Math.min(.42,.14+(v||0)*.3),'sine'); },
    siren(v){
      const a=A(); if(!a) return;
      const amp=Math.min(.16,(v||1)*.12), dur=3.4;
      try{
        const o=a.createOscillator(); o.type='sine';
        const g=a.createGain();
        const lp=a.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=900;
        o.frequency.setValueAtTime(420,a.currentTime);
        for(let k=0;k<4;k++){
          o.frequency.linearRampToValueAtTime(740, a.currentTime+.42+k*.85);
          o.frequency.linearRampToValueAtTime(420, a.currentTime+.85+k*.85);
        }
        g.gain.setValueAtTime(0,a.currentTime);
        g.gain.linearRampToValueAtTime(amp,a.currentTime+.3);
        g.gain.setValueAtTime(amp,a.currentTime+dur-.8);
        g.gain.exponentialRampToValueAtTime(.0006,a.currentTime+dur);
        o.connect(lp); lp.connect(g); g.connect(master); track(o);
        o.start(); o.stop(a.currentTime+dur+.1);
      }catch(e){}
    },
    nuke(){ bud=8; T(200,16,3.6,.6,'sine'); N(3.8,.6,'lowpass',2800,28,.6);
            setTimeout(()=>{bud=4;N(2.8,.34,'lowpass',700,40,.8);},450); },
    humOn(){ const a=A(); if(!a||hum) return;
      try{
        const o=a.createOscillator(); o.type='sawtooth'; o.frequency.value=118;
        const nz=a.createBufferSource(); nz.buffer=nb; nz.loop=true;
        const f=a.createBiquadFilter(); f.type='bandpass'; f.frequency.value=1500; f.Q.value=2.2;
        const g=a.createGain(); g.gain.value=0;
        g.gain.linearRampToValueAtTime(.15,a.currentTime+.07);
        o.connect(g); nz.connect(f); f.connect(g); g.connect(master);
        o.start(); nz.start(); hum={o:o,nz:nz,g:g};
      }catch(e){} },
    humOff(){ if(!hum||!ac) return;
      try{ const t=ac.currentTime;
        hum.g.gain.cancelScheduledValues(t);
        hum.g.gain.setValueAtTime(hum.g.gain.value,t);
        hum.g.gain.linearRampToValueAtTime(0,t+.1);
        hum.o.stop(t+.14); hum.nz.stop(t+.14);
      }catch(e){}
      hum=null; },
  };
})();
