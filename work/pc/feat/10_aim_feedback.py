# 照準のフィードバック：兵装ごとの着弾予告（地面に置く輪）、絨毯爆撃の 9 点、機関砲の散布円、ヒットマーク
TITLE='着弾予告リング・散布円・ヒットマーク'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    C=lambda a,b,c=1: src.rep('css',a,b,c)
    B=lambda a,b,c=1: src.rep('body',a,b,c)
    # ── HUD 要素 ──
    B('<div id="xhCd"></div>','<div id="xhCd"></div>\n  <div id="xhSp"></div>\n  <div id="xhHit"></div>')
    C('#xhCd{', """#xhSp{position:absolute;left:50%;top:50%;width:0;height:0;transform:translate(-50%,-50%);border:1.5px solid rgba(255,181,61,.75);border-radius:50%;opacity:0;pointer-events:none;
  box-shadow:0 0 6px rgba(0,0,0,.6);transition:opacity .15s;}
#xhSp.on{opacity:1;}
#xhHit{position:absolute;left:50%;top:50%;width:26px;height:26px;transform:translate(-50%,-50%) rotate(45deg);opacity:0;pointer-events:none;}
#xhHit::before,#xhHit::after{content:"";position:absolute;background:#fff;box-shadow:0 0 6px rgba(255,120,60,.9);}
#xhHit::before{left:0;top:12px;width:26px;height:2px;} #xhHit::after{left:12px;top:0;width:2px;height:26px;}
#xhCd{""")
    # ── 兵装ごとの着弾予告（3D の輪）と散布円・ヒットマーク ──
    U("let hudT=0, mmT=0;", """let hudT=0, mmT=0;
/* 着弾予告：照準の先（建物なら屋上、地面なら路面）に兵装の効果半径の輪を置く。絨毯爆撃は 9 点、焼夷弾は火の海の広さ */
const AIMR={mesh:null, n:0, t:0, mat:null};
const AIM_RADIUS={missile:30, carpet:30, incend:24, grav:100, orbit:26, demo:34, meteor:118, nuke:190, orb:0, ball:0, rail:0, gun:0, cutter:0};
function aimRingsInit(){
  if(AIMR.mesh||typeof scene==='undefined'||!scene) return;
  const g=new THREE.RingGeometry(.955,1.0,72); g.rotateX(-Math.PI/2);
  AIMR.mat=new THREE.MeshBasicMaterial({color:0xffb53d,transparent:true,opacity:.55,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false});
  AIMR.mesh=new THREE.InstancedMesh(g,AIMR.mat,9); AIMR.mesh.frustumCulled=false; AIMR.mesh.renderOrder=3; AIMR.mesh.count=0; scene.add(AIMR.mesh);
}
/* その地点の「上面」の高さ：上空から下へ走査して最初の固体の上。何も無ければ路面 */
function topAt(x,z){
  const y0=Math.min(cityTop+4, 420);
  for(let y=y0;y>0;y-=VOX*.5){ if(solidAt(x,y,z)) return y+VOX*.6; }
  return .6;
}
const _am=new THREE.Matrix4(), _ap=new THREE.Vector3(), _aq=new THREE.Quaternion(), _as=new THREE.Vector3();
function updAimRings(dt){
  aimRingsInit(); if(!AIMR.mesh) return;
  AIMR.t+=dt;
  const W=curW(); let n=0;
  const show=!uiBlocked() && !CUT.on && (AIM_RADIUS[W.id]>0 || W.id==='carpet');
  if(show){
    const h=aimRay();
    if(!h.miss){
      const pulse=1+Math.sin(AIMR.t*4.5)*.04;
      const put=(x,z,r,y)=>{ if(n>=9) return; _ap.set(x,(y!==undefined?y:topAt(x,z))+.15,z); _as.set(r*pulse,1,r*pulse); _am.compose(_ap,_aq,_as); AIMR.mesh.setMatrixAt(n++,_am); };
      if(W.id==='carpet'){
        const o=camera.position; let fx0=o.x-h.x, fz0=o.z-h.z; const fl=Math.hypot(fx0,fz0)||1; fx0/=-fl; fz0/=-fl;   // 照準の向き（水平）
        const gap=26; for(let i=0;i<9;i++) put(h.x+fx0*gap*(i-4), h.z+fz0*gap*(i-4), 9);
        AIMR.mat.color.setHex(0xffb53d); AIMR.mat.opacity=.4;
      } else {
        const r=AIM_RADIUS[W.id];
        put(h.x,h.z,r, h.ground?.6:undefined);
        if(W.id==='nuke'||W.id==='meteor'){ put(h.x,h.z,r*.45,h.ground?.6:undefined); }            // 内側＝確実に消える範囲
        AIMR.mat.color.setHex(W.id==='nuke'?0xff3d7f:(W.id==='incend'?0xff7a30:0xffb53d)); AIMR.mat.opacity=.34;
      }
    }
  }
  AIMR.mesh.count=n; if(n) AIMR.mesh.instanceMatrix.needsUpdate=true;
  // 機関砲の散布円：熱で広がる。画面上の半径 = tan(散り角)×焦点距離
  const sp=document.getElementById('xhSp');
  if(sp){
    if(W.id==='gun' && !uiBlocked()){
      const ang=.005+(typeof gunHeat==='number'?gunHeat:0)*.013;
      const f=(window.innerHeight/2)/Math.tan(camera.fov*Math.PI/360);
      const px=Math.max(14,Math.tan(ang)*f*2);
      sp.style.width=px+'px'; sp.style.height=px+'px'; sp.classList.add('on');
    } else sp.classList.remove('on');
  }
}
let hitFlash=0;
function updHitMark(dt){
  const h=document.getElementById('xhHit'); if(!h) return;
  if(hitFlash>0){ hitFlash-=dt*5; h.style.opacity=Math.max(0,Math.min(1,hitFlash)); h.style.transform='translate(-50%,-50%) rotate(45deg) scale('+(1.2-hitFlash*.2).toFixed(2)+')'; }
  else if(h.style.opacity!=='0') h.style.opacity='0';
}""")
    U("function pushVox(n){ if(n>0) popVox+=n; }","function pushVox(n){ if(n>0){ popVox+=n; if(n>=6) hitFlash=1; } }")
    U("function updHUD(dt){\n  mmT+=dt; if(mmT>.15){ mmT=0; drawMinimap(); }",
      "function updHUD(dt){\n  updAimRings(dt); updHitMark(dt);\n  mmT+=dt; if(mmT>.15){ mmT=0; drawMinimap(); }")
    # ズーム時は散布円も見やすく：既存の .zoom と干渉しない（独立要素）
