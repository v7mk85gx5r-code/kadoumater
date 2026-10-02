import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# 転倒の切断：上部を完全に断ち、支点側の低い切り株だけ残す。その場で上部を塊にする（姿勢と回転を引き継ぐ）
p.rep('''  let k=0;
  const cut=Math.min(H-2, 2+((Math.random()*2)|0));
  for(let y=0;y<=cut;y++) for(let z=0;z<D;z++) for(let x=0;x<W;x++){
    const rel=(x-spx)*tx+(z-spz)*tz;           // 倒れる方向側の足元を抜く。反対側（支点）は残す
    if(rel < -Math.max(1.5, rx*0.25)) continue;
    k+=killVoxel(b,x,y,z,1);
  }
  b.dirty=true; b.mdirty=true;''',
'''  let k=0;
  const cut=Math.min(H-2, 2+((Math.random()*2)|0));
  for(let y=0;y<=cut;y++) for(let z=0;z<D;z++) for(let x=0;x<W;x++){
    const rel=(x-spx)*tx+(z-spz)*tz;
    if(y<cut-1 && rel < -Math.max(1.5, rx*0.6)) continue;   // 支点側の足元だけ切り株として残す。上2段は全面で断つ
    k+=killVoxel(b,x,y,z,1);
  }
  b.dirty=true; b.mdirty=true;
  // 断たれた上部をその場で塊にする（傾いた姿勢と回転の勢いを引き継ぐ）。予算を超えた分は次フレームに持ち越す
  { const _ps=KSRC; KSRC=(b.lastSrc==='nuke')?'nuke':'collapse';
    const comps=detachBuilding(b,false);
    _spawnMoved=0;
    for(let j=0;j<comps.length;j++) spawnChunk(b,comps[j],0,0,0);
    KSRC=_ps; }''')
# 塊化を優先するため、傾きの更新は剥離処理の前に（予算が新しい状態で）行う
p.rep("    if(b.pose){ b.pose.t-=dt; if(b.pose.t<=0) b.pose=null; } }\n  updToppling(dt);", "    if(b.pose){ b.pose.t-=dt; if(b.pose.t<=0) b.pose=null; } }")
p.rep("  PROF.bfs=0; PROF.mesh=0;\n  processDetach();", "  PROF.bfs=0; PROF.mesh=0;\n  updToppling(dt);\n  processDetach();")
# 傾いた姿勢は、上部の塊化が終わるまで（最大0.6秒）描画メッシュに残す＝直立に戻る一瞬の跳びを防ぐ
p.rep('''      b.pose={x:T.px,y:0,z:T.pz,q:[_tq.x,_tq.y,_tq.z,_tq.w],quat:_tq.clone(),w:[_ta.x*wmag,_ta.y*wmag,_ta.z*wmag],t:1.5};
      b.toppling=null; TOPPLING.splice(i,1);
      toppleCut(b);''',
'''      b.pose={x:T.px,y:0,z:T.pz,q:[_tq.x,_tq.y,_tq.z,_tq.w],quat:_tq.clone(),w:[_ta.x*wmag,_ta.y*wmag,_ta.z*wmag],t:1.5};
      T.hold=0.6; T.ang=T.maxAng;
      toppleCut(b);
      bldPose(b,T.ang);
    } else if(T.hold!==undefined){
      T.hold-=dt;
      if(T.hold<=0 || !b.dirty){ bldPoseReset(b); b.toppling=null; TOPPLING.splice(i,1); }''')
p.rep('''    T.t+=dt;
    const k=Math.min(1,T.t/T.dur);
    T.ang=T.maxAng*k*k*(3-2*k);
    bldPose(b,T.ang);
    if(chance(.5)) dustAt(T.px+rf(-4,4),1.5,T.pz+rf(-4,4),1,1.0);
    shake(.08+k*.25);
    if(k>=1){
      bldPoseReset(b);''',
'''    if(T.hold!==undefined){
      T.hold-=dt;
      if(T.hold<=0 || !b.dirty){ bldPoseReset(b); b.toppling=null; TOPPLING.splice(i,1); }
      continue;
    }
    T.t+=dt;
    const k=Math.min(1,T.t/T.dur);
    T.ang=T.maxAng*k*k*(3-2*k);
    bldPose(b,T.ang);
    if(chance(.5)) dustAt(T.px+rf(-4,4),1.5,T.pz+rf(-4,4),1,1.0);
    shake(.08+k*.25);
    if(k>=1){''')
# 塊の分割：予算切れでも破片を消さない。最大の成分は元の塊に残し、分け切れない成分も元の塊に残して次フレームへ
p.rex(r"  if\(comps\.length<=1\)\{ if\(c\.dirty\) chunkRemesh\(c\); return; \}\n  comps\.sort\(\(a,b\)=>b\.length-a\.length\);   // 大きい破片を優先して実体化\n.*?\n  \}\n\}\n\n/\* ══════════ 剛体演算 ══════════ \*/",
'''  if(comps.length<=1){ if(c.dirty) chunkRemesh(c); return; }
  comps.sort((a,b)=>b.length-a.length);   // 大きい破片を優先して実体化
  const q=[c.q[0],c.q[1],c.q[2],c.q[3]], qq=new THREE.Quaternion(q[0],q[1],q[2],q[3]);
  const P=c.p, V=c.v, Wv=c.w, gen=c.gen;
  const _csrc=c.src||'collapse', _cbid=c.bid;
  chunkSrc=_csrc;
  let left=false;
  // 最大の成分（comps[0]）は元の塊に残す。他の成分を新しい塊へ移す
  for(let k=1;k<comps.length;k++){
    const list=comps[k];
    if(list.length<3){                       // ごく小さな欠片は粉砕
      let _sp=0;
      for(let j=0;j<list.length;j++){ const i=list[j]; killedVox++; _sp+=MATS[c.vox[i]].sc*6; c.vox[i]=0; c.code[i]=0; c.live--; }
      tallyKill(list.length,_sp,_csrc,-1,false); pushVox(list.length);
      continue;
    }
    if(chunks.length>=MAXCHUNK || geoBudget<=0 || spawnBudget<=0){ left=true; continue; }   // 予算切れ：元の塊に残して次フレームへ
    let x0=1e9,y0=1e9,z0=1e9,x1=-1e9,y1=-1e9,z1=-1e9;
    for(let j=0;j<list.length;j++){
      const i=list[j], x=i%W, y=((i/W)|0)%H, z=(i/(W*H))|0;
      if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; if(z<z0)z0=z; if(z>z1)z1=z;
    }
    const nW=x1-x0+1,nH=y1-y0+1,nD=z1-z0+1;
    const nv=new Uint8Array(nW*nH*nD), nh=new Uint16Array(nW*nH*nD);
    for(let j=0;j<list.length;j++){
      const i=list[j], x=i%W, y=((i/W)|0)%H, z=(i/(W*H))|0;
      const t=(x-x0)+nW*((y-y0)+nH*(z-z0));
      nv[t]=c.vox[i]; nh[t]=c.hp[i];
    }
    // 元の塊のローカル中心 → 新しい塊の中心（ワールド）
    const lcx=(x0+nW/2)*VOX-c.h[0], lcy=(y0+nH/2)*VOX-c.h[1], lcz=(z0+nD/2)*VOX-c.h[2];
    const wr=qRot(q,lcx,lcy,lcz);
    const nc=addChunk(nv,nh,nW,nH,nD,P[0]+wr[0],P[1]+wr[1],P[2]+wr[2],
      V[0]+(Math.random()-.5)*5, V[1]+(Math.random()-.5)*3, V[2]+(Math.random()-.5)*5, gen+1, qq, c.tint);
    for(let j=0;j<list.length;j++){ const i=list[j]; if(c.vox[i]){ c.vox[i]=0; c.code[i]=0; c.live--; } }   // 移した分を元から抜く（粉砕された場合も集計済み）
    if(nc){ nc.w=[Wv[0]+(Math.random()-.5)*.6, Wv[1]+(Math.random()-.5)*.6, Wv[2]+(Math.random()-.5)*.6]; nc.bid=_cbid; }
  }
  c.split=left;                             // 残った成分があれば次フレームにもう一度割る
  c.dirty=true;
  if(geoBudget>0) chunkRemesh(c); else c.dirty=true;
}

/* ══════════ 剛体演算 ══════════ */''')
p.save()
