# ズームを 3 段階に（V で巡回：×2.3 → ×5 → 解除。右ボタン/LT は押している間 ×2.3）、倍率表示、メニュー操作音
TITLE='3 段階ズームと倍率表示、メニュー操作音'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    B('  <div id="xhRing"></div>','  <div id="xhRing"></div>\n  <div id="zoomLbl"></div>')
    C('#xhCd{', "#zoomLbl{position:absolute;left:50%;top:calc(50% + 74px);transform:translateX(-50%);font-size:11px;letter-spacing:.2em;color:var(--cyan);font-weight:900;opacity:0;pointer-events:none;text-shadow:0 1px 0 #000;}\n#zoomLbl.on{opacity:.9;}\n#xhCd{")
    U("let fireHeld=false, fireSrc=null, zoomHeld=false, zoomToggle=false;","let fireHeld=false, fireSrc=null, zoomHeld=false, zoomToggle=false, zoomStage=0;\nconst ZOOM_STAGES=[0,1,1.43];   // fovBase の係数：0=等倍、1=×2.3、1.43=×5")
    U("    case 'KeyV': zoomToggle=!zoomToggle; break;","    case 'KeyV': zoomStage=(zoomStage+1)%ZOOM_STAGES.length; zoomToggle=zoomStage>0; break;")
    U("  if(edge(11)) zoomToggle=!zoomToggle;","  if(edge(11)){ zoomStage=(zoomStage+1)%ZOOM_STAGES.length; zoomToggle=zoomStage>0; }")
    U("""  const zt=(zoomHeld||zoomToggle||PAD.zoom)?1:0;
  zoomK+=(zt-zoomK)*Math.min(1,dt*11); if(Math.abs(zoomK-zt)<.003) zoomK=zt;
  el.xh.classList.toggle('zoom',zoomK>.5);""","""  const zt=Math.max((zoomHeld||PAD.zoom)?1:0, zoomToggle?ZOOM_STAGES[zoomStage]:0);
  zoomK+=(zt-zoomK)*Math.min(1,dt*11); if(Math.abs(zoomK-zt)<.003) zoomK=zt;
  el.xh.classList.toggle('zoom',zoomK>.5);
  const zl=document.getElementById('zoomLbl'); if(zl){ if(zoomK>.5){ const mag=Math.tan(fovUser*Math.PI/360)/Math.tan(fovBase()*Math.PI/360); zl.textContent='×'+mag.toFixed(1)+' ZOOM'; zl.classList.add('on'); } else zl.classList.remove('on'); }""")
    U("  PTR.clear(); zoomHeld=false;","  PTR.clear(); zoomHeld=false; zoomToggle=false; zoomStage=0;")
    B('<div class="k"><kbd>V</kbd></div><div class="v">ズーム切替（マウス右ボタン／LT は押している間）</div>','<div class="k"><kbd>V</kbd></div><div class="v">ズーム ×2.6 → ×5.8 → 解除（マウス右ボタン／LT は押している間 ×2.6）</div>')
    B('<div class="k"><kbd>V</kbd></div><div class="v">ズーム切替</div>','<div class="k"><kbd>V</kbd></div><div class="v">ズーム ×2.6 → ×5.8 → 解除</div>')
    # メニュー操作音（合成）
    rep("    gun(){ if(!gate('gun',40)) return;","    ui(k){ if(k==='move'){ T(1400,1100,.045,.035,'sine'); } else if(k==='ok'){ T(880,1320,.08,.06,'triangle'); } else if(k==='back'){ T(640,420,.08,.05,'triangle'); } else if(k==='sel'){ T(1000,1500,.06,.045,'sine'); } },\n    gun(){ if(!gate('gun',40)) return;")
    U("  if(best>=0){ knavSet(best); Snd.kick(); }","  if(best>=0){ knavSet(best); Snd.ui('move'); }")
    U("function knavActivate(){ const it=knavItems(); const b=it[KNAV.idx]; if(b) b.click(); }","function knavActivate(){ const it=knavItems(); const b=it[KNAV.idx]; if(b){ Snd.ui('ok'); b.click(); } }")
    U("function closeTop(){\n  const ov=topOverlay();","function closeTop(){\n  const ov=topOverlay(); if(ov) Snd.ui('back');")
    U("  wpn=id; cd=Math.min(cd,.2);\n  const W=curW();","  wpn=id; cd=Math.min(cd,.2);\n  if(fromUser) Snd.ui('sel');\n  const W=curW();")
