# コンパス帯（方位とランドマークの方角）と、M キーの大きな地図（ランドマーク名つき）
TITLE='コンパス帯と大きな地図（M）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    B('      <div id="modeTag">FREE PLAY</div>\n    </div>','      <div id="modeTag">FREE PLAY</div>\n      <canvas id="compass" width="1120" height="64"></canvas>\n    </div>')
    B('<div id="cutline"></div>','<div id="bigmap" class="ov"><div class="sheet" style="width:auto;text-align:center"><h3>MAP <span class="hk">M / Esc で閉じる</span><button id="bmClose" aria-label="閉じる">✕</button></h3><canvas id="bigmapCv" width="1400" height="1400"></canvas><div id="bmLegend"><i style="background:rgba(79,227,240,.6)"></i>健在　<i style="background:rgba(255,209,102,.95)"></i>ランドマーク　<i style="background:rgba(255,181,61,.85)"></i>損傷　<i style="background:rgba(255,61,127,.5)"></i>倒壊　<i style="background:rgba(255,120,30,.95);border-radius:50%"></i>火災</div></div></div>\n<div id="cutline"></div>')
    C('#scoreWrap{text-align:right;}', """#compass{display:block;width:560px;height:32px;margin:6px auto 0;opacity:.95;}
#scoreWrap{text-align:right;}
#bigmapCv{display:block;width:min(78vh,78vw);height:min(78vh,78vw);border-radius:14px;border:1px solid var(--edge);margin:0 auto;position:relative;inset:auto;}
#bmLegend{margin-top:10px;font-size:11px;color:var(--dim);letter-spacing:.06em;}
#bmLegend i{display:inline-block;width:12px;height:12px;vertical-align:-2px;margin:0 4px 0 10px;border-radius:2px;}""")
    # ミニマップ描画を共通化：任意の canvas に描く。大きな地図ではランドマーク名も
    U("function drawMinimap(){\n  if(!mmg||!CITY||!PCS.hud) return;\n  const W=mmCv.width, H=mmCv.height;",
      "function drawMinimap(){ if(!mmg||!CITY||!PCS.hud) return; drawMapTo(mmCv,mmg,false); }\nfunction drawMapTo(cv,mmg,big){\n  const W=cv.width, H=cv.height;")
    U("""  mmg.fillStyle='#fff'; mmg.strokeStyle='rgba(0,0,0,.8)'; mmg.lineWidth=2;
  mmg.beginPath(); mmg.moveTo(px+fx*11,pz+fz*11); mmg.lineTo(px-fx*7+fz*6,pz-fz*7-fx*6); mmg.lineTo(px-fx*7-fz*6,pz-fz*7+fx*6); mmg.closePath(); mmg.fill(); mmg.stroke();
}""","""  const S=big?2.6:1;
  mmg.fillStyle='#fff'; mmg.strokeStyle='rgba(0,0,0,.8)'; mmg.lineWidth=2;
  mmg.beginPath(); mmg.moveTo(px+fx*11*S,pz+fz*11*S); mmg.lineTo(px-fx*7*S+fz*6*S,pz-fz*7*S-fx*6*S); mmg.lineTo(px-fx*7*S-fz*6*S,pz-fz*7*S+fx*6*S); mmg.closePath(); mmg.fill(); mmg.stroke();
  if(big){
    // 道路（幹線）とランドマーク名
    mmg.font='bold 22px "Hiragino Sans","Noto Sans JP",sans-serif'; mmg.textAlign='center'; mmg.textBaseline='bottom';
    for(let i=0;i<LMS.length;i++){ const L=LMS[i]; let cx=0,cz=0,n=0; for(const k of L.ids){ const b=blds[k]; if(!b) continue; cx+=b.ox+b.W*VOX/2; cz+=b.oz+b.D*VOX/2; n++; } if(!n) continue; cx/=n; cz/=n;
      const tx=X(cx), tz=Z(cz)-8; mmg.lineWidth=5; mmg.strokeStyle='rgba(0,0,0,.85)'; mmg.strokeText(L.name,tx,tz); mmg.fillStyle=L.fell?'rgba(255,120,120,.9)':'rgba(255,220,140,1)'; mmg.fillText(L.name,tx,tz); }
    mmg.font='bold 20px sans-serif'; mmg.fillStyle='rgba(255,255,255,.55)'; mmg.textAlign='left'; mmg.textBaseline='top'; mmg.fillText('N ↑',14,12);
    mmg.textAlign='right'; mmg.fillText(MAPNAMES[MAPID]+'　SEED '+citySeed,W-14,12);
  }
}""")
    # コンパス帯
    U("/* 初回だけ短い操作ヒント */", """/* コンパス帯：方位の目盛りと、ランドマークの方角（金）。N＝-Z */
const cpCv=document.getElementById('compass'), cpg=cpCv?cpCv.getContext('2d'):null;
let cpT=0;
function drawCompass(dt){
  if(!cpg||!PCS.hud) return;
  cpT+=dt; if(cpT<.05) return; cpT=0;
  const W=cpCv.width, H=cpCv.height, cx=W/2;
  const hd=((-cam.yaw)%(Math.PI*2)+Math.PI*2)%(Math.PI*2);          // 向いている方位（0=N）
  const span=Math.PI*.75, pxPerRad=W/span;                              // 表示幅 135°
  cpg.clearRect(0,0,W,H);
  const grd=cpg.createLinearGradient(0,0,W,0); grd.addColorStop(0,'rgba(6,10,16,0)'); grd.addColorStop(.18,'rgba(6,10,16,.55)'); grd.addColorStop(.82,'rgba(6,10,16,.55)'); grd.addColorStop(1,'rgba(6,10,16,0)');
  cpg.fillStyle=grd; cpg.fillRect(0,0,W,H);
  const names={0:'N',90:'E',180:'S',270:'W'};
  cpg.textAlign='center'; cpg.textBaseline='middle';
  for(let d=0;d<360;d+=15){
    let rel=d*Math.PI/180-hd; rel=Math.atan2(Math.sin(rel),Math.cos(rel));
    if(Math.abs(rel)>span/2) continue;
    const x=cx+rel*pxPerRad, major=d%90===0, mid=d%45===0;
    const fade=1-Math.pow(Math.abs(rel)/(span/2),3);
    cpg.strokeStyle='rgba(232,239,246,'+(fade*(major?.95:.5)).toFixed(2)+')'; cpg.lineWidth=major?3:1.5;
    cpg.beginPath(); cpg.moveTo(x,H-6); cpg.lineTo(x,H-(major?26:(mid?18:12))); cpg.stroke();
    if(major){ cpg.fillStyle='rgba(232,239,246,'+fade.toFixed(2)+')'; cpg.font='bold 22px sans-serif'; cpg.fillText(names[d],x,18); }
    else if(mid){ cpg.fillStyle='rgba(141,162,180,'+fade.toFixed(2)+')'; cpg.font='bold 14px sans-serif'; cpg.fillText(String(d),x,20); }
  }
  // ランドマーク
  for(let i=0;i<LMS.length;i++){ const L=LMS[i]; if(L.fell) continue; let lx=0,lz=0,n=0; for(const k of L.ids){ const b=blds[k]; if(!b) continue; lx+=b.ox+b.W*VOX/2; lz+=b.oz+b.D*VOX/2; n++; } if(!n) continue; lx/=n; lz/=n;
    const dx=lx-camera.position.x, dz=lz-camera.position.z; const dist=Math.hypot(dx,dz);
    let rel=Math.atan2(dx,-dz)-hd; rel=Math.atan2(Math.sin(rel),Math.cos(rel)); if(Math.abs(rel)>span/2) continue;
    const x=cx+rel*pxPerRad;
    cpg.fillStyle='rgba(255,209,102,.95)'; cpg.beginPath(); cpg.moveTo(x,H-4); cpg.lineTo(x-7,H-16); cpg.lineTo(x+7,H-16); cpg.closePath(); cpg.fill();
    if(Math.abs(rel)<.35){ cpg.font='bold 15px "Hiragino Sans","Noto Sans JP",sans-serif'; cpg.fillStyle='rgba(255,209,102,.95)'; cpg.strokeStyle='rgba(0,0,0,.8)'; cpg.lineWidth=4; const t=L.name+' '+Math.round(dist)+'m'; cpg.strokeText(t,x,H-34); cpg.fillText(t,x,H-34); }
  }
  // 中央の指標
  cpg.fillStyle='var(--cyan)'; cpg.fillStyle='rgba(79,227,240,.95)'; cpg.beginPath(); cpg.moveTo(cx,H-2); cpg.lineTo(cx-6,H-12); cpg.lineTo(cx+6,H-12); cpg.closePath(); cpg.fill();
}
/* 大きな地図（M） */
const bigmapEl=document.getElementById('bigmap'), bmCv=document.getElementById('bigmapCv'), bmg=bmCv?bmCv.getContext('2d'):null;
let mapOn=false;
function openMap(){ if(mapOn) return; mapOn=true; bigmapEl.classList.add('on'); releasePointers(); if(bmg) drawMapTo(bmCv,bmg,true); knavOpen(bigmapEl,'bmClose'); }
function closeMap(){ if(!mapOn) return; mapOn=false; bigmapEl.classList.remove('on'); if(KNAV.root===bigmapEl) knavClose(); }
document.getElementById('bmClose').addEventListener('click',e=>{ e.stopPropagation(); closeMap(); });
bigmapEl.addEventListener('click',e=>{ if(e.target.id==='bigmap') closeMap(); });
/* 初回だけ短い操作ヒント */""")
    U("function uiBlocked(){ return booting || paused || resultOn || titleOn || menuOpen() || panelOpen() || keysOn; }",
      "function uiBlocked(){ return booting || paused || resultOn || titleOn || menuOpen() || panelOpen() || keysOn || mapOn; }")
    U("function topOverlay(){\n  if(keysOn) return keysEl;","function topOverlay(){\n  if(keysOn) return keysEl;\n  if(mapOn) return bigmapEl;")
    U("  if(ov===keysEl) closeKeys();\n  else if(ov===wpanel) closePanel();","  if(ov===keysEl) closeKeys();\n  else if(ov===bigmapEl) closeMap();\n  else if(ov===wpanel) closePanel();")
    U("    if(code==='Tab'){ if(ov===wpanel) closePanel(); e.preventDefault(); return; }",
      "    if(code==='Tab'){ if(ov===wpanel) closePanel(); e.preventDefault(); return; }\n    if(code==='KeyM' && ov===bigmapEl){ if(!rep) closeMap(); e.preventDefault(); return; }")
    U("    case 'KeyH': toggleHud(); break;","    case 'KeyH': toggleHud(); break;\n    case 'KeyM': openMap(); break;")
    U("const GAME_KEYS=new Set(['Space','Tab','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','F1','F2','Slash','KeyO',",
      "const GAME_KEYS=new Set(['Space','Tab','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','F1','F2','Slash','KeyO','KeyM',")
    U("function updHUD(dt){\n  updAimRings(dt); updHitMark(dt);","function updHUD(dt){\n  updAimRings(dt); updHitMark(dt); drawCompass(dt);")
    # 操作一覧・タイトル・キーヒントに M を追記
    B('<div class="k"><kbd>R</kbd> / <kbd>T</kbd></div><div class="v">視点を水平に ／ 俯瞰ポイントを順に移動</div>',
      '<div class="k"><kbd>R</kbd> / <kbd>T</kbd></div><div class="v">視点を水平に ／ 俯瞰ポイントを順に移動</div>\n      <div class="k"><kbd>M</kbd></div><div class="v">大きな地図（ランドマーク名・損傷・火災）</div>')
    B('<div class="k"><kbd>R</kbd><kbd>T</kbd></div><div class="v">視点を水平に戻す／俯瞰ポイントへ移動</div>',
      '<div class="k"><kbd>R</kbd><kbd>T</kbd><kbd>M</kbd></div><div class="v">視点を水平に戻す／俯瞰ポイントへ移動／大きな地図</div>')
    U("Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　Esc メニュー　/ 操作一覧'","Z/C 武器　Tab 一覧　V ズーム　T 俯瞰　M 地図　Esc メニュー　/ 操作一覧'")
    # パッド：Back は HUD 切替のまま、十字キー上（水平に）は維持。地図は Y 長押し…は複雑なので省略
    U("keysOn:()=>keysOn, knav:","keysOn:()=>keysOn, mapOn:()=>mapOn, openMap:openMap, closeMap:closeMap, drawCompass:drawCompass, knav:")
