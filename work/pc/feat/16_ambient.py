# 街の環境音：交通の低い唸り・雑踏のざわめき・遠くのクラクション・空気のヒス。高度と街の明かり、破壊の進み具合で変わる
TITLE='街の環境音（交通・雑踏・遠くの音）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    rep("    f(dt){ bud=Math.min(12, bud+(dt||.016)*480); }, kick(){ A(); },",
"""    f(dt){ bud=Math.min(12, bud+(dt||.016)*480); }, kick(){ A(); },
    /* 環境音：ノイズをフィルタで整形した 3 層（交通の唸り／雑踏／空気）＋ときどき遠くのクラクション。
       ユーザー操作で AudioContext が起きてから鳴り始め、ポーズ（suspend）で止まる。音量は設定と状況で決まる */
    amb(dt){
      if(!ambOn||!S.sound){ if(amb){ try{ amb.g.gain.setTargetAtTime(0,ac.currentTime,.2); }catch(e){} } return; }
      const a=A(); if(!a) return;
      if(!amb){
        try{
          const g=a.createGain(); g.gain.value=0; g.connect(master);
          const mk=(type,f,q,vol)=>{ const s=a.createBufferSource(); s.buffer=nb; s.loop=true; s.playbackRate.value=.5+Math.random()*.2;
            const fl=a.createBiquadFilter(); fl.type=type; fl.frequency.value=f; fl.Q.value=q; const gg=a.createGain(); gg.gain.value=vol;
            s.connect(fl); fl.connect(gg); gg.connect(g); s.start(); return {s:s,f:fl,g:gg}; };
          amb={g:g, traffic:mk('lowpass',180,.8,.9), crowd:mk('bandpass',700,.9,.22), air:mk('highpass',3200,.6,.035), t:0, horn:2+Math.random()*4};
        }catch(e){ ambOn=false; return; }
      }
      amb.t+=dt;
      // 状況：高度が上がると雑踏が遠のき、停電で静まり、壊れるほど街の生活音が減る
      const y=camera?camera.position.y:50;
      const alt=1-Math.min(1,Math.max(0,(y-40)/320))*.7;
      const life=1-Math.min(1,(typeof killedVox==='number'&&totalVox?killedVox/totalVox:0))*.65;
      const pw=(typeof cityPower==='number')?cityPower:1;
      const base=.16*ambVol;
      const t=a.currentTime;
      amb.g.gain.setTargetAtTime(base*(.55+.45*pw), t, .4);
      amb.traffic.g.gain.setTargetAtTime(.9*(.6+.4*alt)*(.5+.5*life)*(.9+.1*Math.sin(amb.t*.23)), t, .5);
      amb.crowd.g.gain.setTargetAtTime(.22*alt*life*(MAPID===1?1.5:(MAPID===0?1.1:.5))*(.85+.15*Math.sin(amb.t*.37+1)), t, .5);
      amb.air.g.gain.setTargetAtTime(.035*(1.2-alt*.4), t, .5);
      amb.traffic.f.frequency.setTargetAtTime(150+alt*90, t, .5);
      // 遠くのクラクション・警笛（まれに）
      amb.horn-=dt;
      if(amb.horn<=0){ amb.horn=6+Math.random()*14; if(bud>2 && life>.3){ const f0=380+Math.random()*180; T(f0,f0*.98,.25+Math.random()*.3,.035*alt*ambVol,'square'); if(Math.random()<.35) setTimeout(()=>T(f0*1.26,f0*1.24,.3,.03*alt*ambVol,'square'),220); } }
    },
    setAmb(on,vol){ ambOn=!!on; if(vol!==undefined) ambVol=Math.max(0,Math.min(1,vol)); },""")
    rep("  let ac=null,nb=null,bud=0,hum=null,master=null,comp=null,voices=0;","  let ac=null,nb=null,bud=0,hum=null,master=null,comp=null,voices=0;\n  let amb=null, ambOn=true, ambVol=1;")
    rep("  Snd.f(realDt);","  Snd.f(realDt); Snd.amb(realDt);")
    # 設定：環境音の音量（切／小／標準）
    U("const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock',fps:0};",
      "const PCS={q:'auto',scale:1,fov:75,sens:5,invY:false,ao:true,snd:true,fx:1,hud:true,mlook:'lock',fps:0,amb:1};   // amb: 環境音 0/0.5/1")
    U("  fpsCap=[0,60,30].includes(+PCS.fps)?+PCS.fps:0;","  fpsCap=[0,60,30].includes(+PCS.fps)?+PCS.fps:0;\n  if(![0,.5,1].includes(+PCS.amb)) PCS.amb=1; Snd.setAmb(+PCS.amb>0, +PCS.amb);")
    B('<button class="pb" id="bInvY">Y軸反転</button><button class="pb" id="bSnd">音</button></div>',
      '<button class="pb" id="bInvY">Y軸反転</button><button class="pb" id="bSnd">音</button></div>\n  <div class="row"><span class="lb">環境音</span><div class="row" id="pmAmbRow" style="margin:0;flex:1"></div></div>')
    U("  const fr=document.getElementById('pmFpsRow'); fr.innerHTML='';","""  const ar=document.getElementById('pmAmbRow'); ar.innerHTML='';
  [[0,'切'],[.5,'小'],[1,'標準']].forEach(([v,n])=>{ ar.appendChild(mkPB(n,+PCS.amb===v,()=>{ PCS.amb=v; Snd.setAmb(v>0,v); savePCS(); renderMenu(); },'pmAmb_'+Math.round(v*10))); });
  const fr=document.getElementById('pmFpsRow'); fr.innerHTML='';""")
