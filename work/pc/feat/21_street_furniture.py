# 歩道設備レイヤー STF（ENV-01）＋ 小物の破壊整合の最小部分（ENV-11：爆風で飛ぶ／倒れる・落下塊で倒れる・核で蒸発）
#   ・歩道＝通りの端（XL±XW/2 の外側 0.5〜2.5m）。幅 20m 以上の通りの縁に白いガードレール（3m ピッチ、所々に植栽）、
#     細い通りにはステンレスの車止め。交差点の角に案内標識とゴミ箱、長い幹線の中ほどにバス停（行灯が灯る）、
#     建物の壁沿いに駐輪自転車の列（歌舞伎町が最も多く、西新宿はほとんど無い）。建物（街路樹・電柱・設備を含む）とは bldAt で重ならない。
#   ・種類ごとに 1 つの InstancedMesh（計 7 ドローコール）。HOOKS.init でプールを 1 度だけ作り、HOOKS.build で配置、HOOKS.reset で空にする。
#     行列と色は dirty の時だけ詰め直す（通常フレームは 0）。
#   ・HOOKS.blast：半径内の設備は爆心から外へ 0.45 秒かけて倒れ（細長いもの）または飛び散り、素材に合った破片と火花になる。
#     核（KSRC==='nuke' の爆風／核の衝撃波 waves.nk）では破片も加点も無く、消えるだけ。落ちてくる塊に当たっても倒れる（車と同じ 1/15 秒間隔）。
TITLE='歩道設備（ガードレール・車止め・ゴミ箱・標識・バス停・植栽・駐輪）と爆風・落下塊・核への反応'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    # ── 本体の定義（/*@DEFS*/：resetWorld の直前）。登録はここで行う ──
    rep("/*@DEFS*/", r"""/* ══════════ 歩道設備 STF（work/pc/feat/21_street_furniture.py） ══════════
   歩道の縁に必ずあるもの：白いガードレール（幹線）・ステンレスの車止め（細い通り）・ゴミ箱・案内標識・バス停・植栽・駐輪自転車。
   種類ごとに 1 つの InstancedMesh（計 7 ドローコール）。行列と色は dirty の時だけ詰め直す。
   爆風で飛び（破片に変わる）、落ちてくる塊で倒れ、核では破片を出さずに消える */
const STF={kinds:{}, list:[], dirty:false, chk:0, fall:[], cells:new Map(), mat:null, hits:0};
const STF_MAX={rail:5000, bollard:1000, bin:360, sign:360, bus:80, planter:600, bike:1100};
const STF_SCORE={rail:40, bollard:30, bin:30, sign:60, bus:120, planter:40, bike:30};
const STF_TALL={rail:1, bollard:1, sign:1, bus:1};                      // 根元から倒れる種類（残りは飛び散る）
const STF_BIKE_COLS=[[.74,.75,.78],[.12,.14,.22],[.52,.10,.10],[.16,.18,.20],[.62,.58,.46],[.28,.38,.58],[.80,.80,.82]];
function stfCellKey(x,z){ return (((x/16)|0)+64)*256+(((z/16)|0)+64); }
function initStf(){
  if(STF.mat) return;
  // 箱を合成して 1 つのジオメトリに。局所座標：+x＝通りに沿う向き、+z＝車道の中心へ向く向き、原点＝地面。色は頂点色×インスタンス色
  // 発光する部品は頂点色の最小成分を 2〜4 にする（LIT_COLOR の区分 1＝控えめな発光）。その種類のインスタンス色は 1 に固定する
  const merge=(boxes)=>{
    const gs=boxes.map(b=>{ const g=new THREE.BoxGeometry(b[0],b[1],b[2]).toNonIndexed(); g.translate(b[3],b[4],b[5]);
      const n=g.attributes.position.count, c=new Float32Array(n*3);
      for(let i=0;i<n;i++){ c[i*3]=b[6]; c[i*3+1]=b[7]; c[i*3+2]=b[8]; }
      g.setAttribute('color',new THREE.BufferAttribute(c,3)); return g; });
    let n=0; for(const g of gs) n+=g.attributes.position.count;
    const P=new Float32Array(n*3), C=new Float32Array(n*3), V=new Float32Array(n*2); let o=0;
    for(const g of gs){ P.set(g.attributes.position.array,o*3); C.set(g.attributes.color.array,o*3); V.set(g.attributes.uv.array,o*2); o+=g.attributes.position.count; g.dispose(); }
    const m=new THREE.BufferGeometry();
    m.setAttribute('position',new THREE.BufferAttribute(P,3)); m.setAttribute('color',new THREE.BufferAttribute(C,3)); m.setAttribute('uv',new THREE.BufferAttribute(V,2));
    return m;
  };
  STF.mat=new THREE.MeshBasicMaterial({vertexColors:true,fog:true}); setupLitMaterial(STF.mat);
  const W=[.84,.85,.86], ST=[.56,.57,.60], DK=[.17,.18,.19];
  const G={
    // ガードレール：支柱 2 本＋横桟 3 本（白）。3m ピッチで連続する
    rail:[[.10,.86,.10,-1.42,.43,0,...ST],[.10,.86,.10,1.42,.43,0,...ST],
          [2.96,.11,.10,0,.80,0,...W],[2.96,.07,.08,0,.56,0,...W],[2.96,.07,.08,0,.32,0,...W]],
    // 車止め：ステンレスの角柱＋頭の黄色い反射帯（控えめな発光）
    bollard:[[.16,.88,.16,0,.44,0,...ST],[.19,.05,.19,0,.80,0,2.85,2.70,2.25]],
    // ゴミ箱：濃い緑の箱＋蓋＋投入口の表示
    bin:[[.52,.84,.52,0,.42,0,.22,.27,.24],[.58,.10,.58,0,.89,0,.30,.31,.32],[.30,.26,.03,0,.60,.27,.60,.58,.50]],
    // 案内標識：細い柱＋青い反射板（通りに沿って車の方を向く）
    sign:[[.08,3.2,.08,0,1.6,0,...ST],[.03,.62,.62,-.02,2.65,0,.32,.33,.35],[.03,.62,.62,.02,2.65,0,2.30,2.42,2.74]],
    // バス停：柱＋行灯（灯っている）＋ベンチ（歩道の奥側）
    bus:[[.10,3.0,.10,-1.0,1.5,0,...ST],[.06,.82,.50,-1.0,2.62,0,2.92,2.88,2.74],[.14,.08,.56,-1.0,2.18,0,...DK],
         [1.6,.07,.42,.3,.46,-.7,.42,.33,.23],[.06,.46,.36,-.4,.23,-.7,...DK],[.06,.46,.36,1.0,.23,-.7,...DK],[1.6,.30,.05,.3,.72,-.90,.42,.33,.23]],
    // 植栽：コンクリートの升に低木
    planter:[[1.2,.50,.50,0,.25,0,.36,.35,.33],[1.1,.14,.42,0,.56,0,.17,.27,.13],[.42,.26,.34,-.28,.72,0,.19,.31,.15],[.36,.22,.30,.26,.70,.02,.21,.33,.16]],
    // 自転車：車輪 2 枚＋フレーム（インスタンス色）＋ハンドル・サドル・前かご
    bike:[[.66,.66,.05,-.52,.33,0,.10,.10,.11],[.66,.66,.05,.52,.33,0,.10,.10,.11],
          [.90,.05,.05,0,.72,0,1,1,1],[.05,.44,.05,-.18,.52,0,1,1,1],[.52,.05,.05,.28,.52,0,1,1,1],
          [.05,.05,.46,.50,.96,0,.14,.14,.15],[.05,.30,.05,.50,.82,0,1,1,1],[.22,.06,.11,-.18,.88,0,.12,.12,.12],[.30,.22,.30,.66,.78,0,.50,.50,.52]],
  };
  for(const k in G){
    const m=new THREE.InstancedMesh(merge(G[k]),STF.mat,STF_MAX[k]);
    m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    m.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(STF_MAX[k]*3),3);
    m.count=0; m.frustumCulled=false; scene.add(m); STF.kinds[k]=m;
  }
}
function resetStf(){
  STF.list.length=0; STF.fall.length=0; STF.cells.clear(); STF.dirty=false; STF.chk=0; STF.hits=0;
  for(const k in STF.kinds) STF.kinds[k].count=0;
}
function buildStf(){
  resetStf();
  if(!STF.mat) return;
  const cnt={}; for(const k in STF_MAX) cnt[k]=0;
  const dens=QUAL.level>=3?0.5:1;                                        // 低画質では自転車と植栽を半分に
  const put=(k,x,z,rot,col)=>{
    if(cnt[k]>=STF_MAX[k]||bldAt(x,.5,z)||bldAt(x,2.0,z)) return null;   // 建物・街路樹・電柱・設備と重ねない
    const q={k:k,x:x,z:z,rot:rot,col:col,dead:false,gone:false,fall:-1,fx:0,fz:0};
    STF.list.push(q); cnt[k]++;
    const key=stfCellKey(x,z); let c=STF.cells.get(key); if(!c){ c=[]; STF.cells.set(key,c); } c.push(q);
    return q;
  };
  const gray=(a,b)=>{ const v=rf(a,b); return [v,v,v]; };
  const ONE=[1,1,1];
  // 通りの片側ごとの区間（交差点の ±6m は空ける）を列挙する。ax=2：XL の通り（z 方向）、ax=0：ZL の通り（x 方向）
  const roads=[];
  for(let i=0;i<XL.length;i++){
    const segs=[]; const lo=CITY.z0+6, hi=CITY.z1-6;
    const cuts=[]; for(let j=0;j<ZL.length;j++) cuts.push([ZL[j]-ZW[j]/2-6, ZL[j]+ZW[j]/2+6]);
    let a=lo; for(let j=0;j<cuts.length;j++){ if(cuts[j][0]-a>14) segs.push([a,cuts[j][0],j-1]); a=cuts[j][1]; }
    if(hi-a>14) segs.push([a,hi,cuts.length-1]);
    roads.push({ax:2,c:XL[i],hw:XW[i]/2,segs:segs,i:i});
  }
  for(let j=0;j<ZL.length;j++){
    const segs=[]; const lo=CITY.x0+6, hi=CITY.x1-6;
    const cuts=[]; for(let i=0;i<XL.length;i++) cuts.push([XL[i]-XW[i]/2-6, XL[i]+XW[i]/2+6]);
    let a=lo; for(let i=0;i<cuts.length;i++){ if(cuts[i][0]-a>14) segs.push([a,cuts[i][0],i-1]); a=cuts[i][1]; }
    if(hi-a>14) segs.push([a,hi,cuts.length-1]);
    roads.push({ax:0,c:ZL[j],hw:ZW[j]/2,segs:segs,i:j});
  }
  for(const R of roads) for(const sd of [-1,1]){
    const wide=R.hw>=10;
    const rot=R.ax===2?-sd*Math.PI/2:(sd<0?0:Math.PI);                  // 局所 +z が車道の中心を向く回転
    const P=(t,off)=>R.ax===2?[R.c+sd*(R.hw+off),t]:[t,R.c+sd*(R.hw+off)];   // off＝縁石から歩道側へ（0.5〜2.5m）
    const wall=(t)=>{ const p=P(t,3.4); return !!bldAt(p[0],2,p[1]); };   // 歩道の奥に建物の壁があるか
    for(const seg of R.segs){
      const a=seg[0], b=seg[1], len=b-a;
      if(MAPID===0&&R.ax===2&&R.i===2&&seg[2]===2) continue;            // 一番街の突き当たりの先は建物
      // 標識とゴミ箱は区間の両端（交差点の角の少し手前）
      for(const [t,end] of [[a+1.2,0],[b-1.2,1]]){
        if(Math.random()<.55){ const p=P(t,.7); put('sign',p[0],p[1],rot,ONE); }
        if(Math.random()<.5){ const p=P(t+(end?-3.2:3.2),1.0); put('bin',p[0],p[1],rot+rf(-.1,.1),gray(.85,1)); }
      }
      let busT=-1e9;
      if(wide){
        // バス停：長い区間の中ほど（行灯が灯る）
        if(len>70&&Math.random()<.6){ busT=(a+b)/2+rf(-10,10); const p=P(busT,1.2); put('bus',p[0],p[1],rot,ONE); }
        // ガードレール：縁石のすぐ内側 0.7m を 3m ピッチで。所々に車の出入口の切れ目。渋谷・西新宿は 4 本に 1 本が植栽
        let gap=0, n=0;
        for(let t=a+1.6;t<b-1.4;t+=3.0,n++){
          if(Math.abs(t-busT)<4.5) continue;
          if(gap>0){ gap--; continue; }
          if(Math.random()<.05){ gap=1; continue; }
          if(MAPID!==0&&(n%4)===2){ if(Math.random()<dens){ const p=P(t,2.2); put('planter',p[0],p[1],rot,gray(.9,1.05)); } }
          else { const p=P(t,.7); put('rail',p[0],p[1],rot,gray(.86,1.0)); }
        }
      } else if(Math.random()<.42){
        // 車止め：細い通りの縁に 3.2m ピッチ
        for(let t=a+2;t<b-1.5;t+=3.2){ const p=P(t,.6); put('bollard',p[0],p[1],rot,ONE); }
      }
      // 駐輪：建物の壁に沿って 0.62m ピッチの列。歌舞伎町が最も多く、西新宿はほとんど無い
      const pb=(MAPID===0?.55:(MAPID===1?.28:.08))*(wide?.5:1)*dens;
      for(let t=a+4;t<b-6;t+=rf(9,16)){
        if(Math.random()>pb||!wall(t)) continue;
        const nb=3+((Math.random()*7)|0), col=STF_BIKE_COLS[(Math.random()*STF_BIKE_COLS.length)|0];
        for(let k=0;k<nb&&t+k*.62<b-4;k++){
          const p=P(t+k*.62,2.0);
          put('bike',p[0],p[1],rot+rf(-.22,.22)+(Math.random()<.5?Math.PI:0),Math.random()<.7?col:STF_BIKE_COLS[(Math.random()*STF_BIKE_COLS.length)|0]);
        }
        t+=nb*.62;
      }
    }
  }
  STF.dirty=true;
}
/* 設備 1 個が壊れる。src は SRCMUL の分岐（核は破片も加点もなし）。細長い種類は 0.45 秒だけ根元から傾いて消える */
function stfHit(q,src,ox,oz){
  if(q.dead) return;
  q.dead=true; STF.dirty=true; STF.hits++;
  src=src||KSRC;
  if(src==='nuke'){ q.gone=true; return; }
  if(STF_TALL[q.k]){ let dx=q.x-(ox===undefined?q.x+Math.cos(q.rot):ox), dz=q.z-(oz===undefined?q.z+Math.sin(q.rot):oz); const l=Math.hypot(dx,dz)||1;
    q.fx=dx/l; q.fz=dz/l; q.fall=0; STF.fall.push(q); }
  else q.gone=true;
  const k=q.k, c=q.col, y=.8;
  const ST={n:'鉄骨',r:.56,g:.57,b:.60,emis:0}, WH={n:'鉄骨',r:.80,g:.81,b:.82,emis:0}, PN={n:'金属パネル',r:.30,g:.33,b:.46,emis:0};
  if(k==='rail'){ spawnDebris(q.x,y,q.z,WH,.9); spawnDebris(q.x,y,q.z,WH,.9); }
  else if(k==='bollard'){ spawnDebris(q.x,y,q.z,ST,.8); }
  else if(k==='bin'){ spawnDebris(q.x,y,q.z,{n:'金属パネル',r:.24,g:.28,b:.25,emis:0},.8); vfxSmoke(q.x,1.2,q.z,rf(2.5,4),rf(2,3),rf(-.5,.5),rf(2,3),rf(-.5,.5),.6); }
  else if(k==='sign'){ spawnDebris(q.x,2.2,q.z,ST,.9); spawnDebris(q.x,2.6,q.z,PN,1.0); }
  else if(k==='bus'){ spawnDebris(q.x,2.2,q.z,ST,.9); spawnDebris(q.x,2.6,q.z,{n:'金属パネル',r:.70,g:.68,b:.60,emis:1},1.0); spawnDebris(q.x,.6,q.z,{n:'幹',r:.42,g:.33,b:.23,emis:0},.8); }
  else if(k==='planter'){ spawnDebris(q.x,.5,q.z,{n:'コンクリート',r:.36,g:.35,b:.33,emis:0},.7); spawnDebris(q.x,.8,q.z,{n:'樹木',r:.19,g:.31,b:.15,emis:0},.8); spawnDebris(q.x,.8,q.z,{n:'樹木',r:.19,g:.31,b:.15,emis:0},.8); }
  else if(k==='bike'){ const M={n:'手すり',r:c[0],g:c[1],b:c[2],emis:0}; spawnDebris(q.x,y,q.z,M,.9); spawnDebris(q.x,y,q.z,M,.9); spawnDebris(q.x,.5,q.z,{n:'金属パネル',r:.12,g:.12,b:.13,emis:0},.8); }
  if(k!=='planter') for(let i=0;i<4;i++) spark(q.x,y,q.z,rf(-6,6),rf(2,8),rf(-6,6),rf(.2,.4),1,.6,.3);
  if(Math.random()<.25) Snd.mat(k==='planter'?1:5,q.x,y,q.z);
  if((SRCMUL[src]||0)>0) S.score+=Math.round((STF_SCORE[k]||30)*S.combo);  // 核・破壊球では加点しない
}
/* 爆風（HOOKS.blast）：半径内の設備は爆心から外へ倒れ、破片になる。16m 格子で引くので走査は近傍だけ */
function stfBlast(x,y,z,R){
  if(!STF.list.length) return;
  const r=R*1.1, src=KSRC, rr=r*r, yy=y*y*.25;
  const cx0=((x-r)/16)|0, cx1=((x+r)/16)|0, cz0=((z-r)/16)|0, cz1=((z+r)/16)|0;
  for(let cx=cx0;cx<=cx1;cx++) for(let cz=cz0;cz<=cz1;cz++){
    const cell=STF.cells.get((cx+64)*256+(cz+64)); if(!cell) continue;
    for(let i=0;i<cell.length;i++){ const q=cell[i]; if(q.dead) continue;
      const dx=q.x-x, dz=q.z-z; if(dx*dx+dz*dz+yy<rr) stfHit(q,src,x,z); }
  }
}
/* 核の衝撃波：半径内の設備は破片を出さずに消える（waves の nk は毎フレーム半径が広がる） */
function stfNuke(x,z,r){
  if(!STF.list.length) return;
  const rr=r*r;
  for(let i=0;i<STF.list.length;i++){ const q=STF.list[i]; if(q.dead) continue;
    const dx=q.x-x, dz=q.z-z; if(dx*dx+dz*dz<rr){ q.dead=true; q.gone=true; STF.dirty=true; STF.hits++; } }
}
function updStf(dt){
  if(!STF.mat) return;
  if(STF.list.length){
    // 核の衝撃波が届いた範囲は蒸発
    for(let i=0;i<waves.length;i++){ const Wv=waves[i]; if(Wv.nk) stfNuke(Wv.x,Wv.z,Wv.r); }
    // 落ちてくる塊に当たると倒れる（車と同じく 1/15 秒ごと）。塊の足元の範囲を 16m 格子で引く
    STF.chk+=dt;
    if(STF.chk>=1/15){ STF.chk=0;
      for(let k=0;k<chunks.length;k++){ const c=chunks[k];
        if(c.sleep||c.p[1]-c.h[1]>3.0) continue;
        const hx=c.h[0]+.8, hz=c.h[2]+.8;
        const cx0=((c.p[0]-hx)/16)|0, cx1=((c.p[0]+hx)/16)|0, cz0=((c.p[2]-hz)/16)|0, cz1=((c.p[2]+hz)/16)|0;
        const src=c.src==='nuke'?'nuke':'domino';
        for(let cx=cx0;cx<=cx1;cx++) for(let cz=cz0;cz<=cz1;cz++){
          const cell=STF.cells.get((cx+64)*256+(cz+64)); if(!cell) continue;
          for(let i=0;i<cell.length;i++){ const q=cell[i]; if(q.dead) continue;
            if(Math.abs(q.x-c.p[0])<hx&&Math.abs(q.z-c.p[2])<hz) stfHit(q,src,c.p[0],c.p[2]); }
        }
      }
    }
  }
  // 倒れる途中の設備（0.45 秒で消える）
  if(STF.fall.length){ STF.dirty=true;
    for(let i=STF.fall.length-1;i>=0;i--){ const q=STF.fall[i]; q.fall+=dt;
      if(q.fall>=.45){ q.gone=true; STF.fall.splice(i,1); } }
  }
  if(!STF.dirty) return;
  STF.dirty=false;
  let w=0; const L=STF.list;                                             // 消えたものを詰める（格子の参照は dead で読み飛ばす）
  for(let i=0;i<L.length;i++){ const q=L[i]; if(!q.gone) L[w++]=q; }
  L.length=w;
  const n={}; for(const k in STF.kinds) n[k]=0;
  for(let i=0;i<L.length;i++){ const q=L[i], m=STF.kinds[q.k], j=n[q.k]++, o=j*16;
    const M=m.instanceMatrix.array, C=m.instanceColor.array;
    const cs=Math.cos(q.rot), sn=Math.sin(q.rot);
    if(q.fall>=0){                                                      // 根元を軸に、爆心から遠ざかる向きへ倒れる
      const t=Math.min(1,q.fall/.45), ph=1.35*t*t, c=Math.cos(ph), s=Math.sin(ph), ax=q.fz, az=-q.fx, k1=1-c;
      const R00=c+k1*ax*ax, R01=-s*az, R02=k1*ax*az, R10=s*az, R11=c, R12=-s*ax, R20=k1*ax*az, R21=s*ax, R22=c+k1*az*az;
      M[o]=R00*cs-R02*sn; M[o+1]=R10*cs-R12*sn; M[o+2]=R20*cs-R22*sn; M[o+3]=0;
      M[o+4]=R01; M[o+5]=R11; M[o+6]=R21; M[o+7]=0;
      M[o+8]=R00*sn+R02*cs; M[o+9]=R10*sn+R12*cs; M[o+10]=R20*sn+R22*cs; M[o+11]=0;
    } else {
      M[o]=cs;M[o+1]=0;M[o+2]=-sn;M[o+3]=0; M[o+4]=0;M[o+5]=1;M[o+6]=0;M[o+7]=0; M[o+8]=sn;M[o+9]=0;M[o+10]=cs;M[o+11]=0;
    }
    M[o+12]=q.x;M[o+13]=0;M[o+14]=q.z;M[o+15]=1;
    C[j*3]=q.col[0]; C[j*3+1]=q.col[1]; C[j*3+2]=q.col[2];
  }
  for(const k in STF.kinds){ const m=STF.kinds[k]; m.count=n[k]; m.instanceMatrix.needsUpdate=true; m.instanceColor.needsUpdate=true; }
}
HOOKS.init.push(initStf); HOOKS.build.push(buildStf); HOOKS.reset.push(resetStf); HOOKS.update.push(updStf); HOOKS.blast.push(stfBlast);
/*@DEFS*/""")
    # ── 検証フック（__tt.pc.STF() など） ──
    U("/*@PCDBG*/", "STF:()=>STF, stfBlast:stfBlast, stfHit:stfHit, stfNuke:stfNuke, /*@PCDBG*/")
