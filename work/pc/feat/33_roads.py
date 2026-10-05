# 路面の精度（ENV-07）
#   buildRoad のキャンバス（2800px、最高・高では 3584px）は、マンホール 26 個・汚れ 220 個・「側溝と縁石の線」40 本を
#   街区も建物も関係なく一様乱数で散らしていた（建物の下にもマンホールがあった）。横断歩道は幅 ≥12 の交差点だけで、
#   停止線・「止まれ」・路側帯の白線は無く、異方性フィルタも無いので斜めに見る路面で白線がにじんでいた。
#   ・車道の帯（XL[i]±XW[i]/2、ZL[j]±ZW[j]/2）の中だけに、実物の規則で置く：
#       - 横断歩道：全交差点の 4 つの進入路（幅 11 の小路同士も）。0.5m の白 1.0m ピッチ、帯の幅は通りの幅で 3〜4.5m
#       - 停止線：各進入路の左側通行の進入側半分（幅 0.45m）。交差点の中のセンターラインは消す
#       - 「止まれ」：信号の無い交差点（どちらかが幅 <20）で細い方の通りに。縦に 1.8 倍に伸ばした 3 文字
#       - 右折矢印：幅 ≥20 の通りの中央線寄りの車線。幅 ≥28 は左車線に直進矢印も
#       - 側溝（縁石から 0.4m・幅 0.25m）と路側帯の白線（縁石から 1.0m・幅 0.15m）を全街区の縁に沿って。白線は横断歩道の手前で切る
#       - マンホール：車道の中心線 ±2m、20〜40m ピッチの千鳥。汚れは車道（長さ×幅で重み付け）とセンター街にだけ。幹線にはタイヤ跡の筋
#       - 一番街の突き当たり（建物）には何も描かず、セントラルロード（歩行者天国）・センター街には白線・停止線を描かない
#   ・路面テクスチャに anisotropy=min(8, maxAnisotropy)・ミップマップ・三線形フィルタを明示
#   ・縁石の立体化：街区の縁（車道の縁から 0〜0.3m 外側）に幅 0.3m・高さ 0.15m の箱を InstancedMesh（最大 256、1 ドローコール）で。
#     21_street_furniture.py の STF は縁石から 0.6m 以上内側に置くので重ならない。センター街の口と一番街の突き当たりは穴にする
#   ・WET（反射）の式は触らない。anchor は buildRoad のキャンバス描画と CanvasTexture の生成行だけ
#   負荷：キャンバスの描画は数千の fillRect（ノイズ付与ループに比べて無視できる）。3584px は最高・高のみ（生成時間 +60%）。
#         縁石は 12 三角形 × ≤256 で 1 ドローコール、毎フレームの処理は無い
TITLE='路面の精度（規則的なマンホール・側溝・路側帯・停止線・止まれ・全交差点の横断歩道・異方性・立体の縁石）'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)

    # ── 1. 定義：道路の帯・区間・歩行者域の照会、テクスチャ設定、縁石 ──
    rep("/*@DEFS*/", r"""/* ══════════ 路面の精度 ROADS（work/pc/feat/33_roads.py） ══════════
   車道の帯（XL/ZL）と、その片側の区間（交差点で切る）を照会する。buildRoad のキャンバス描画と縁石の InstancedMesh が共用する */
const ROADS={S:0, px:0, cross:0, stop:0, txt:0, arrow:0, man:0, dirt:0, seg:0, curb:0, aniso:0, ms:0, t0:0};
const CURB={mesh:null, MAX:256};
function roadBands(){                                                     // 車道の帯：{ax,i,c,hw,lo,hi}（ax=2：z 方向の通り）
  const RD=[];
  for(let i=0;i<XL.length;i++) RD.push({ax:2,i:i,c:XL[i],hw:XW[i]/2,lo:CITY.z0,hi:CITY.z1});
  for(let j=0;j<ZL.length;j++) RD.push({ax:0,i:j,c:ZL[j],hw:ZW[j]/2,lo:CITY.x0,hi:CITY.x1});
  return RD;
}
function roadDeadEnd(x,z){                                                // 一番街の突き当たり（花道通りまでの区画は建物）
  return MAPID===0&&Math.abs(x-XL[2])<XW[2]/2+.5&&z>ZL[2]+ZW[2]/2-.5&&z<ZL[3]-ZW[3]/2+.5;
}
function roadPedZone(x,z){                                                // 車の入らない所：突き当たり・セントラルロード・センター街
  if(roadDeadEnd(x,z)) return true;
  if(MAPID===0&&Math.abs(x-XL[2])<XW[2]/2+.5&&z>ZL[3]+ZW[3]/2-.5&&z<ZL[5]-ZW[5]/2+.5) return true;
  if(MAPID===1&&CGAI&&x>CGAI.x0-.5&&x<CGAI.x1+.5&&z>CGAI.z0-.5&&z<CGAI.z1+.5) return true;
  return false;
}
/* 通り R の片側 sd（-1/+1、0＝中心）の区間 [a,b] を交差点で切って列挙する。
   T 字路の突き当たり側は街区が続くので切らず、センター街の口は穴にする */
function roadSegs(R,sd){
  const cross=R.ax===2?ZL:XL, crossW=R.ax===2?ZW:XW, edge=R.c+sd*R.hw;
  const segs=[]; let a=R.lo;
  for(let k=0;k<cross.length;k++){
    if(MAPID===0&&R.ax===0&&k===2&&((R.i===2&&sd===1)||(R.i===3&&sd===-1))) continue;
    const c0=cross[k]-crossW[k]/2, c1=cross[k]+crossW[k]/2;
    if(c0-a>2) segs.push([a,c0]); a=c1;
  }
  if(R.hi-a>2) segs.push([a,R.hi]);
  const out=[];
  for(const s of segs){
    const m=(s[0]+s[1])/2;
    if(R.ax===2&&R.i===2&&roadDeadEnd(R.c,m)) continue;
    if(MAPID===1&&CGAI&&R.ax===0&&sd!==0&&(Math.abs(edge-CGAI.z0)<1||Math.abs(edge-CGAI.z1)<1)&&s[0]<CGAI.x0&&s[1]>CGAI.x1){
      out.push([s[0],CGAI.x0-.3]); out.push([CGAI.x1+.3,s[1]]);
    } else out.push(s);
  }
  return out;
}
function roadTexSetup(tex){                                               // 路面テクスチャ：三線形＋異方性（斜めに見る白線がにじまない）
  tex.generateMipmaps=true; tex.minFilter=THREE.LinearMipmapLinearFilter; tex.magFilter=THREE.LinearFilter;
  tex.wrapS=tex.wrapT=THREE.ClampToEdgeWrapping;
  let an=1; try{ an=Math.max(1,Math.min(8,renderer.capabilities.getMaxAnisotropy()|0)); }catch(e){}
  tex.anisotropy=an; ROADS.aniso=an;
  ROADS.ms=Math.round(performance.now()-ROADS.t0);
}
function initCurbs(){
  if(CURB.mesh) return;
  const g=new THREE.BoxGeometry(1,1,1).toNonIndexed();
  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(g.attributes.position.count*3).fill(1),3));
  const mat=new THREE.MeshBasicMaterial({vertexColors:true,fog:true}); setupLitMaterial(mat);
  const m=new THREE.InstancedMesh(g,mat,CURB.MAX);
  m.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(CURB.MAX*3),3);
  m.count=0; m.frustumCulled=false; scene.add(m); CURB.mesh=m;
}
function resetCurbs(){ if(CURB.mesh) CURB.mesh.count=0; ROADS.curb=0; }
/* 縁石：街区の縁に沿う幅 0.3m・高さ 0.15m の箱。z 方向の縁石は角まで、x 方向は角を 0.3m 譲る（面の重なりを避ける） */
function buildCurbs(){
  if(!CURB.mesh) return;
  const m=CURB.mesh, M=m.instanceMatrix.array, C=m.instanceColor.array; let n=0;
  for(const R of roadBands()) for(const sd of [-1,1]){
    const e=R.c+sd*(R.hw+.15);
    for(const s of roadSegs(R,sd)){
      if(n>=CURB.MAX) break;
      let a=s[0], b=s[1]; if(R.ax===0){ a+=.3; b-=.3; }
      const len=b-a; if(len<.5) continue;
      const o=n*16; M.fill(0,o,o+16); M[o+5]=.15; M[o+13]=.125; M[o+15]=1;
      if(R.ax===2){ M[o]=.3; M[o+10]=len; M[o+12]=e; M[o+14]=(a+b)/2; }
      else { M[o]=len; M[o+10]=.3; M[o+12]=(a+b)/2; M[o+14]=e; }
      const v=.40+rf(-.03,.03); C[n*3]=v; C[n*3+1]=v; C[n*3+2]=v*.96;
      n++;
    }
  }
  m.count=n; m.instanceMatrix.needsUpdate=true; m.instanceColor.needsUpdate=true; ROADS.curb=n;
}
HOOKS.init.push(initCurbs); HOOKS.build.push(buildCurbs); HOOKS.reset.push(resetCurbs);
/*@DEFS*/""")

    # ── 2. キャンバスの解像度：最高・高は 3584px（約 5px/m） ──
    rep("  const S=2800;\n  const spanX=CITY.x1-CITY.x0, spanZ=CITY.z1-CITY.z0;",
        "  const S=(QUAL.level<=1)?3584:2800;                                   // 最高・高は約 5px/m（work/pc/feat/33_roads.py）\n  ROADS.t0=performance.now(); ROADS.S=S;\n  const spanX=CITY.x1-CITY.x0, spanZ=CITY.z1-CITY.z0;")

    # ── 3. 横断歩道の置き換え：全交差点の 4 進入路に横断歩道・停止線・「止まれ」・矢印、全街区の縁に側溝と路側帯 ──
    rep("""  // 横断歩道
  g.fillStyle='rgba(216,226,236,.32)';
  for(let i=0;i<XL.length;i++) for(let j=0;j<ZL.length;j++){
    if(XW[i]<12||ZW[j]<12) continue;
    const zc=TZ(ZL[j]-ZW[j]/2-4), w=XW[i]*px;
    for(let k=0;k<6;k++) g.fillRect(TX(XL[i])-w/2+k*(w/6)+w/24, zc, w/12, 7*px);
  }""", r"""  // ── 路面標示（work/pc/feat/33_roads.py）：車道の帯の中だけに、実物の規則で置く ──
  ROADS.px=px; ROADS.cross=ROADS.stop=ROADS.txt=ROADS.arrow=ROADS.man=ROADS.dirt=ROADS.seg=0;
  const RD=roadBands();
  const MK='rgba(226,230,232,.50)';                                       // 白線（夜の路面標示。控えめ）
  const CWD=(hw)=>hw>=10?4.5:(hw>=7?4:3);                                // 横断歩道の帯の幅
  // 矢印（進入路の局所座標：x＝運転者の右、y＝交差点から離れる向き）。先端が交差点を向く
  const arrow=(u,t,right)=>{
    const x=u*px, y0=t*px, L=4.2*px, s=.36*px, hw2=.9*px, hl=1.2*px;
    g.fillStyle=MK; g.fillRect(x-s/2,y0+hl,s,L-hl);
    g.beginPath(); g.moveTo(x,y0); g.lineTo(x-hw2,y0+hl); g.lineTo(x+hw2,y0+hl); g.closePath(); g.fill();
    if(right){
      const bx=x+1.3*px, by=y0+L*.62-1.2*px;
      g.strokeStyle=MK; g.lineWidth=s; g.beginPath(); g.moveTo(x,y0+L*.62); g.lineTo(bx,by); g.stroke();
      g.beginPath(); g.moveTo(bx+.55*px,by-.7*px); g.lineTo(bx-.75*px,by-.15*px); g.lineTo(bx+.25*px,by+.75*px); g.closePath(); g.fill();
    }
  };
  for(let i=0;i<XL.length;i++) for(let j=0;j<ZL.length;j++){
    const X=XL[i], Z=ZL[j], hx=XW[i]/2, hz=ZW[j]/2, scr=(MAPID===1&&i===2&&j===2);
    if(!scr&&(XW[i]>=20||ZW[j]>=20)){ g.fillStyle='#0d1015'; g.fillRect(TX(X-hx),TZ(Z-hz),2*hx*px,2*hz*px); }   // 交差点の中のセンターラインを消す
    for(const ax of [2,0]) for(const sd of [-1,1]){
      // 進入路：口の中央 (ex,ez)、交差点から離れる向き A、運転者の右 R（左側通行：進入側は右の反対）
      const hw=ax===2?hx:hz, w=hw*2, wc=(ax===2?hz:hx)*2;
      const ex=ax===2?X:X+sd*hx, ez=ax===2?Z+sd*hz:Z;
      const Ax=ax===2?0:sd, Az=ax===2?sd:0, Rx=ax===2?sd:0, Rz=ax===2?0:-sd;
      const cw=CWD(hw), tStop=.6+cw+1.2;
      if(roadPedZone(ex+Ax*(.6+cw/2),ez+Az*(.6+cw/2))) continue;       // 突き当たり・歩行者天国・センター街には描かない
      g.save(); g.translate(TX(ex),TZ(ez)); g.rotate(Math.atan2(Rz,Rx));
      g.fillStyle=MK;
      for(let u=-hw+.6;u<hw-.9;u+=1.0) g.fillRect(u*px,.6*px,.5*px,cw*px);           // 横断歩道：0.5m の白、1.0m ピッチ
      ROADS.cross++;
      g.fillRect((-hw+.4)*px,tStop*px,(hw-.7)*px,.45*px); ROADS.stop++;              // 停止線：進入側（左半分）
      const sig=(w>=20&&wc>=20);                                                      // 信号機は幅 ≥20 同士の交差点
      if(!sig&&(w<wc||(w===wc&&ax===2))){                                             // 止まれ：細い方の通り
        g.font='bold '+(1.5*px).toFixed(1)+'px sans-serif'; g.textAlign='center'; g.textBaseline='middle';
        const u=-Math.min(hw*.5,2.6), f=1.8;                                          // 縦に 1.8 倍に伸ばす
        g.save(); g.scale(1,f);
        const ch=['止','ま','れ']; for(let k=0;k<3;k++) g.fillText(ch[k],u*px,(tStop+2.8+k*3.0)*px/f);   // 止が奥（交差点側）
        g.restore(); ROADS.txt++;
      }
      if(w>=20){ arrow(-2.3,tStop+2.5,true); ROADS.arrow++;                            // 右折矢印：中央線寄りの車線
        if(hw>=14){ arrow(-hw*.62,tStop+2.5,false); ROADS.arrow++; } }                 // 幅 ≥28：左車線に直進矢印
      g.restore();
    }
  }
  // 側溝（縁石から 0.4m・幅 0.25m）と路側帯の白線（縁石から 1.0m・幅 0.15m）：全街区の縁に沿う。幹線にはタイヤ跡の筋
  for(const R of RD){
    if(R.hw>=10){ g.fillStyle='rgba(0,0,0,.07)';
      for(const o of [-3.05,-1.55,1.55,3.05]){ const e=R.c+o;
        if(R.ax===2) g.fillRect(TX(e-.25),TZ(R.lo),.5*px,(R.hi-R.lo)*px); else g.fillRect(TX(R.lo),TZ(e-.25),(R.hi-R.lo)*px,.5*px); } }
    for(const sd of [-1,1]){
      const edge=R.c+sd*R.hw;
      const band=(off,wd,a,b,col)=>{ g.fillStyle=col; const e=edge-sd*off;             // off＝縁石から車道側へ
        if(R.ax===2) g.fillRect(TX(e-wd/2),TZ(a),wd*px,(b-a)*px); else g.fillRect(TX(a),TZ(e-wd/2),(b-a)*px,wd*px); };
      for(const s of roadSegs(R,sd)){
        ROADS.seg++;
        band(.4,.25,s[0],s[1],'rgba(0,0,0,.35)');
        const m=(s[0]+s[1])/2;
        if(roadPedZone(R.ax===2?R.c:m,R.ax===2?m:R.c)) continue;
        const tr=.6+CWD(R.hw)+1.65;                                                    // 横断歩道と停止線の分だけ切る
        band(1.0,.15,s[0]+(s[0]>R.lo+1?tr:0),s[1]-(s[1]<R.hi-1?tr:0),'rgba(220,220,210,.45)');
      }
    }
  }""")

    # ── 4. 汚れとマンホール：車道の帯の中だけ。マンホールは中心線 ±2m・20〜40m ピッチの千鳥 ──
    rep("""  // 汚れとマンホール
  for(let i=0;i<220;i++){
    const rx=Math.random()*S, rz=Math.random()*S, rr=6+Math.random()*34;
    g.fillStyle='rgba(0,0,0,'+(0.05+Math.random()*0.12)+')';
    g.beginPath(); g.ellipse(rx,rz,rr,rr*(.4+Math.random()*.8),Math.random()*3.14,0,6.283); g.fill();
  }
  for(let i=0;i<26;i++){
    const rx=Math.random()*S, rz=Math.random()*S;
    g.fillStyle='rgba(26,30,36,.9)';
    g.beginPath(); g.arc(rx,rz,3.4,0,6.283); g.fill();
    g.strokeStyle='rgba(60,66,74,.6)'; g.lineWidth=1;
    g.beginPath(); g.arc(rx,rz,3.4,0,6.283); g.stroke();
  }""", r"""  // 汚れとマンホール：車道の帯の中だけ（work/pc/feat/33_roads.py）
  { const totL=RD.reduce((a,R)=>a+(R.hi-R.lo)*R.hw,0);
    const roadPt=()=>{ let r=Math.random()*totL;                                       // 車道の点：長さ×幅で重み付け
      for(const R of RD){ const a=(R.hi-R.lo)*R.hw; if(r<a){ const t=R.lo+Math.random()*(R.hi-R.lo), u=(Math.random()*2-1)*(R.hw-.5);
        return R.ax===2?[R.c+u,t,2]:[t,R.c+u,0]; } r-=a; }
      return [RD[0].c,RD[0].lo,RD[0].ax]; };
    const dirt=(x,z,ax)=>{ const rr=(1.5+Math.random()*5.5)*px, k=.4+Math.random()*.5;   // 通りの向きに伸びた染み
      g.fillStyle='rgba(0,0,0,'+(0.05+Math.random()*0.12)+')';
      g.beginPath(); g.ellipse(TX(x),TZ(z),ax===2?rr*k:rr,ax===2?rr:rr*k,0,0,6.283); g.fill(); ROADS.dirt++; };
    for(let k=0;k<260;k++){ const p=roadPt(); if(!roadDeadEnd(p[0],p[1])) dirt(p[0],p[1],p[2]); }
    if(MAPID===1&&CGAI) for(let k=0;k<24;k++) dirt(rf(CGAI.x0+1,CGAI.x1-1),rf(CGAI.z0+2,CGAI.z1-2),2);
    for(const R of RD){ let side=1;
      for(const s of roadSegs(R,0)) for(let t=s[0]+rf(8,16);t<s[1]-8;t+=rf(20,40)){
        side=-side; const u=side*2.0, x=R.ax===2?R.c+u:t, z=R.ax===2?t:R.c+u;
        if(roadPedZone(x,z)&&!(MAPID===0&&R.ax===2&&R.i===2&&z>ZL[3])) continue;     // 歩行者天国にはマンホールだけ残す
        const qx=TX(x), qz=TZ(z), r=.5*px;
        g.fillStyle='rgba(26,30,36,.9)'; g.beginPath(); g.arc(qx,qz,r,0,6.283); g.fill();
        g.strokeStyle='rgba(60,66,74,.6)'; g.lineWidth=Math.max(1,.08*px); g.beginPath(); g.arc(qx,qz,r,0,6.283); g.stroke();
        ROADS.man++;
      }
    }
  }""")

    # ── 5. 乱雑な「側溝と縁石の線」40 本は廃止（側溝は上で全街区の縁に沿って描く） ──
    rep("""    // 側溝と縁石の線
    g.strokeStyle='rgba(0,0,0,.22)'; g.lineWidth=2;
    for(let i=0;i<40;i++){
      const rx=Math.random()*S, rz=Math.random()*S;
      g.beginPath(); g.moveTo(rx,rz);
      g.lineTo(rx+(Math.random()<.5?120:0), rz+(Math.random()<.5?0:120));
      g.stroke();
    }
""", "")

    # ── 6. テクスチャ：異方性・ミップマップ・三線形 ──
    rep("  const tex=new THREE.CanvasTexture(cv);\n", "  const tex=new THREE.CanvasTexture(cv);\n  roadTexSetup(tex);                                                     // 異方性 min(8,max)・三線形（work/pc/feat/33_roads.py）\n")

    # ── 7. 検証フック ──
    U("/*@PCDBG*/", "roads:()=>ROADS, CURB:()=>CURB, roadCanvas:()=>(roadMesh&&roadMesh.material.map)?roadMesh.material.map.image:null, /*@PCDBG*/")
