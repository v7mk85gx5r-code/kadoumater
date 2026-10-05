# 遠景の密度（L11）
#   ・街の外周（CITY 矩形＋45m 〜 半径 1500m）にシルエットの街（約 1,400〜1,700 棟の箱ビル）と、マップごとの方角に遠い超高層群を敷く。
#     1 本の BufferGeometry（側面 4＋屋上 1＝20 頂点／棟、頂点は起動時に最大数ぶん確保し genCity ごとに書き換える）＋ 1 ドローコール。
#     窓は専用の ShaderMaterial が頂点属性（面に沿った距離・高さ・種・点灯率）から手続きで描く。遠くで窓が 1 画素を切ると平均の明るさに溶かす（ちらつかない）。
#     霧（1100〜3400m）に沈み、核の閃光（uFlash）で白く焼ける。濡れた路面の反射パス（uFlip<0）では描かない。
#   ・高さ 60m 超の棟の屋上に航空障害灯（Points、1 ドローコール）。街じゅうの障害灯と同じ 0.75Hz の同期点滅。
#   ・方角：北＝-z、西＝-x。歌舞伎町からは西南西に西新宿の超高層群、渋谷からは北北東に新宿（霧の中）と東に六本木、西新宿では周囲 450〜750m に超高層。
#   ・破壊の対象ではない（blds ではなく aimRay/rayCast にも当たらない）。HOOKS.init で確保、HOOKS.build で書き換え、HOOKS.update で点滅。
TITLE='遠景の密度：外周のシルエット街と遠い超高層群・航空障害灯'
def apply(rep, between, src):
    U=lambda a,b,c=1: src.rep('ui',a,b,c)
    rep("/*@DEFS*/", r"""/* ══════════ 遠景：外周のシルエット街と遠い超高層群（work/pc/feat/24_far_city.py） ══════════
   CITY の外は平らな地面しか無く、街の端や俯瞰で「舞台の縁」が見えていた。外周リングに箱ビルを敷き、
   方角に合わせた超高層群で地平線を「東京」にする。1 本の BufferGeometry（最大 FAR_MAX 棟、起動時に確保）＋障害灯の Points */
const FAR_MAX=2200, FAR_PMAX=480;
const FAR={mesh:null, pts:null, mat:null, pmat:null, n:0, np:0, top:0, blink:-1};
const FAR_VERT=`
attribute vec4 aF;
varying vec4 vF; varying vec3 vC;
uniform float uFlip;
#include <fog_pars_vertex>
void main(){
  vF=aF; vC=color;
  vec4 mvPosition=modelViewMatrix*vec4(position,1.0);
  gl_Position=projectionMatrix*mvPosition;
  if(uFlip<0.0) gl_Position=vec4(2.0,2.0,2.0,1.0);          // 反射パスでは描かない（遠景の反射は距離で消えている）
#include <fog_vertex>
}`;
const FAR_FRAG=`
uniform float uFlash;
uniform vec3 uStreetCol;
varying vec4 vF; varying vec3 vC;
#include <fog_pars_fragment>
float fh21(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
void main(){
  vec3 c=vC;
  float lo=exp(-vF.y/13.0);
  c=c*(1.0+0.55*lo)+uStreetCol*(0.035*lo);                    // 足元は路面の光でわずかに明るい
  if(vF.w>=0.0){
    // 窓：面に沿った距離 vF.x と高さ vF.y を 3.0×3.4m の格子に切る。種 vF.z（整数部＝寒色の割合×8、小数部＝棟ごとの乱数）
    float seed=fract(vF.z), coolK=floor(vF.z)*0.125;
    vec2 q=vF.xy/vec2(3.0,3.4);
    vec2 id=floor(q), f=fract(q);
    float px=max(fwidth(q.x),fwidth(q.y));                     // 1 画素あたりの格子数
    float on=step(fh21(id+seed*97.0),vF.w);
    float aa=min(0.12,px*0.9);
    float win=smoothstep(0.24-aa,0.24+aa,f.x)*smoothstep(0.78+aa,0.78-aa,f.x)
             *smoothstep(0.30-aa,0.30+aa,f.y)*smoothstep(0.80+aa,0.80-aa,f.y);
    float floorOff=step(0.93,fh21(vec2(id.y,seed*53.0)));        // 消灯した階
    vec3 warm=vec3(1.0,0.76,0.50), cool=vec3(0.66,0.78,1.0);
    vec3 wc=mix(warm,cool,step(fh21(id*1.7+seed*31.0),coolK))*(0.50+0.50*fh21(id*3.1+seed));
    float cov=clamp((1.0/max(px,1e-4)-1.5)/2.5,0.0,1.0);          // 格子が 4 画素以上なら窓を描き、1.5 画素以下なら平均に溶かす
    vec3 avg=mix(warm,cool,coolK)*(0.27*0.75*vF.w);
    c+=mix(avg,wc*win*on,cov)*(1.0-floorOff)*0.78;
  }
  c+=vec3(1.0,0.92,0.80)*uFlash*0.9;                            // 核の閃光
  gl_FragColor=vec4(c,1.0);
#include <fog_fragment>
}`;
function initFar(){
  if(FAR.mesh) return;
  const g=new THREE.BufferGeometry();
  const NV=FAR_MAX*20;
  g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(NV*3),3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(NV*3),3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute('aF',new THREE.BufferAttribute(new Float32Array(NV*4),4).setUsage(THREE.DynamicDrawUsage));
  const idx=new Uint32Array(FAR_MAX*30);                       // 5 面×2 三角形。並びは一定なので 1 度だけ作る
  for(let b=0;b<FAR_MAX*5;b++){ const v=b*4, o=b*6; idx[o]=v; idx[o+1]=v+1; idx[o+2]=v+2; idx[o+3]=v; idx[o+4]=v+2; idx[o+5]=v+3; }
  g.setIndex(new THREE.BufferAttribute(idx,1));
  g.setDrawRange(0,0);
  FAR.mat=new THREE.ShaderMaterial({
    uniforms:THREE.UniformsUtils.merge([THREE.UniformsLib.fog,{uFlash:{value:0},uFlip:{value:1},uStreetCol:{value:new THREE.Color(1,.6,.33)}}]),
    vertexShader:FAR_VERT, fragmentShader:FAR_FRAG, vertexColors:true, fog:true, side:THREE.DoubleSide,
  });
  FAR.mat.extensions=FAR.mat.extensions||{}; FAR.mat.extensions.derivatives=true;
  FAR.mat.uniforms.uFlash=SKYU.uFlash; FAR.mat.uniforms.uFlip=LITU.uFlip; FAR.mat.uniforms.uStreetCol=LITU.uStreetCol;   // 既存の uniform を共有
  FAR.mesh=new THREE.Mesh(g,FAR.mat);
  FAR.mesh.frustumCulled=false; FAR.mesh.renderOrder=-900;      // 空の直後・街より先に描く
  scene.add(FAR.mesh);
  // 航空障害灯
  const pg=new THREE.BufferGeometry();
  pg.setAttribute('position',new THREE.BufferAttribute(new Float32Array(FAR_PMAX*3),3).setUsage(THREE.DynamicDrawUsage));
  pg.setDrawRange(0,0);
  FAR.pmat=new THREE.PointsMaterial({size:6, map:radialTex('255,70,40',false), color:new THREE.Color(1,.22,.10),
    transparent:true, opacity:1, depthWrite:false, blending:THREE.AdditiveBlending, sizeAttenuation:true, fog:true});
  FAR.pts=new THREE.Points(pg,FAR.pmat);
  FAR.pts.frustumCulled=false;
  scene.add(FAR.pts);
}
/* 外周の街を書き換える（genCity の seed 付き乱数の中で呼ばれる） */
function buildFar(){
  if(!FAR.mesh) return;
  const R=Math.random;
  const P=FAR.mesh.geometry.attributes.position.array, C=FAR.mesh.geometry.attributes.color.array, A=FAR.mesh.geometry.attributes.aF.array;
  const L=FAR.pts.geometry.attributes.position.array;
  let n=0, np=0, top=0;
  const ccx=(CITY.x0+CITY.x1)/2, ccz=(CITY.z0+CITY.z1)/2;
  const put=(cx,cz,w,d,h,rot,lit,coolK,tr,tg,tb)=>{
    if(n>=FAR_MAX) return;
    const s=Math.sin(rot), c=Math.cos(rot), hw=w/2, hd=d/2;
    const X=[cx+(-hw*c+hd*s), cx+(hw*c+hd*s), cx+(hw*c-hd*s), cx+(-hw*c-hd*s)];
    const Z=[cz+(-hw*s-hd*c), cz+(hw*s-hd*c), cz+(hw*s+hd*c), cz+(-hw*s+hd*c)];
    const seed=Math.floor(coolK*8)+R()*0.999;
    let v=n*20;
    const vert=(x,y,z,u,hh,lt)=>{ const p=v*3, a=v*4; P[p]=x; P[p+1]=y; P[p+2]=z; C[p]=tr; C[p+1]=tg; C[p+2]=tb; A[a]=u; A[a+1]=hh; A[a+2]=seed; A[a+3]=lt; v++; };
    for(let i=0;i<4;i++){ const j=(i+1)&3, len=(i&1)?d:w, uo=R()*7;
      vert(X[i],0,Z[i],uo,0,lit); vert(X[j],0,Z[j],uo+len,0,lit); vert(X[j],h,Z[j],uo+len,h,lit); vert(X[i],h,Z[i],uo,h,lit); }
    for(let i=0;i<4;i++) vert(X[i],h,Z[i],0,h,-1);              // 屋上（窓なし）
    n++;
    if(h>top) top=h;
    if(h>60&&np<FAR_PMAX){ L[np*3]=cx; L[np*3+1]=h+1.2; L[np*3+2]=cz; np++;
      if(h>=120&&np<FAR_PMAX){ L[np*3]=X[2]; L[np*3+1]=h+1.2; L[np*3+2]=Z[2]; np++; } }
  };
  const tint=(k,blue)=>{ const m=.055*k; return [m*(1.0+.08*blue), m*(0.96+.10*blue), m*(1.08+.30*blue)]; };
  // ── 1. 外周の一般の街：42m の格子に揺らぎを入れて撒く。CITY 矩形＋45m を空け、半径 1500m で薄れて終わる ──
  const CELL=42, NC=37;
  for(let ix=-NC;ix<=NC;ix++) for(let iz=-NC;iz<=NC;iz++){
    const cx=ccx+ix*CELL+(R()-.5)*14, cz=ccz+iz*CELL+(R()-.5)*14;
    const dx=Math.max(CITY.x0-45-cx,0,cx-CITY.x1-45), dz=Math.max(CITY.z0-45-cz,0,cz-CITY.z1-45);
    const rd=Math.hypot(dx,dz); if(rd<=0) continue;            // 街の中
    const rc=Math.hypot(cx-ccx,cz-ccz); if(rc>1520) continue;
    let p=rd<250?.60:(rd<650?.48:(rd<1000?.40:.34));
    p*=Math.min(1,(1520-rc)/170);
    if(R()>p) continue;
    const w=12+R()*22, d=12+R()*22;
    const u=R();
    let h=u<.62?10+R()*18:(u<.90?28+R()*32:60+R()*60);
    h*=1+.40*Math.min(1,Math.max(0,(rd-300)/1100));            // 遠いほど高く：地平線を持ち上げる
    if(rd<200) h=Math.min(h,58);                                // 街の縁では眺めを塞がない
    const office=u>.84;
    put(cx,cz,w,d,h,(R()-.5)*.10, office?.26+R()*.22:.10+R()*.22, office?.6+R()*.3:.08+R()*.25, ...tint(.75+R()*.5,office?1:0));
  }
  // ── 2. マップごとの超高層群（北＝-z、西＝-x）──
  const tower=(x,z,h,w,rot)=>put(x,z,w||(34+R()*18),w?w*(0.8+R()*.4):(34+R()*18),h,rot||(R()-.5)*.3,.30+R()*.22,.75+R()*.25,...tint(.9+R()*.3,1));
  if(MAPID===0){
    // 歌舞伎町：西南西 700〜950m に西新宿の超高層群（都庁・住友・三井・損保…）。南 1.2km に新宿駅南口の高層（ドコモタワー）
    for(let i=0;i<9;i++){ const a=Math.PI*(1.02+.30*(i/8))+(R()-.5)*.08, r=700+R()*250; tower(ccx+Math.cos(a)*r,ccz-Math.sin(a)*r,150+R()*90); }
    tower(ccx+170,ccz+1230,240,40); tower(ccx+60,ccz+1180,160,44);
  } else if(MAPID===1){
    // 渋谷：北北東 1.2〜1.45km に新宿の超高層（霧の中の影）、東南東 1.1km に六本木ヒルズ、南 1km に恵比寿ガーデンプレイス、南西 450m にセルリアンタワー
    for(let i=0;i<6;i++){ const a=Math.PI*(.62+.10*(i/5))+(R()-.5)*.05, r=1200+R()*250; tower(ccx+Math.cos(a)*r,ccz-Math.sin(a)*r,170+R()*70); }
    tower(ccx+1000,ccz+450,230,52); tower(ccx+1060,ccz+520,150,40);
    tower(ccx+150,ccz+1000,165,42);
    tower(ccx-310,ccz+470,180,40,.2);
  } else {
    // 西新宿：周囲 450〜750m に超高層が散らばる（北・東に多い）。南西 750m にオペラシティ、南東 1km にドコモタワー
    for(let i=0;i<12;i++){ const a=(i<8?Math.PI*(1.45+.75*(i/7)):Math.PI*(0.25+.9*((i-8)/3)))+(R()-.5)*.12, r=450+R()*300;
      tower(ccx+Math.cos(a)*r,ccz-Math.sin(a)*r,120+R()*80); }
    tower(ccx-720,ccz+420,234,46,.1); tower(ccx+480,ccz+960,240,40);
  }
  FAR.n=n; FAR.np=np; FAR.top=top;
  const g=FAR.mesh.geometry;
  g.attributes.position.needsUpdate=true; g.attributes.color.needsUpdate=true; g.attributes.aF.needsUpdate=true;
  g.setDrawRange(0,n*30);
  FAR.pts.geometry.attributes.position.needsUpdate=true; FAR.pts.geometry.setDrawRange(0,np);
}
/* 障害灯：街じゅうの障害灯（LIT_MAIN）と同じ 0.75Hz の同期点滅 */
function updFar(dt){
  if(!FAR.pmat) return;
  const fl=(SKYU.uTime.value*0.75)%1, ss=(a,b,x)=>{ const t=Math.min(1,Math.max(0,(x-a)/(b-a))); return t*t*(3-2*t); };
  const op=Math.min(1,0.06+1.9*ss(0,0.06,fl)*ss(0.50,0.36,fl));
  if(Math.abs(op-FAR.blink)>0.01){ FAR.blink=op; FAR.pmat.opacity=op; }
}
HOOKS.init.push(initFar);
HOOKS.build.push(buildFar);
HOOKS.update.push(updFar);
/*@DEFS*/""")
    U("/*@PCDBG*/", "far:()=>({n:FAR.n, pts:FAR.np, tris:FAR.n*10, top:Math.round(FAR.top), blink:FAR.blink, visible:!!(FAR.mesh&&FAR.mesh.visible)}), /*@PCDBG*/")
