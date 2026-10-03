/* ══════════ SSAO（深度プリパス → 半球サンプル → 深度を見て平滑化）と異方性ストリーク ══════════ */
const AO_STRENGTH=0.85, STREAK_STRENGTH=0.32;
const AO_FRAG=`#include <packing>
uniform sampler2D tDepth; uniform vec2 uTexel; uniform float uNear, uFar, uRadius, uBias, uTime; uniform mat4 uProj, uInvProj;
varying vec2 vUv;
float h12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*0.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float rd(vec2 uv){ return unpackRGBAToDepth(texture2D(tDepth,uv)); }
vec3 vp(vec2 uv,float d){ vec4 n=vec4(uv*2.0-1.0,d*2.0-1.0,1.0); vec4 v=uInvProj*n; return v.xyz/v.w; }
void main(){
  float d=rd(vUv);
  // 何も描かれていない画素（クリア値 (0,0,0,1) は 255/256 に復号される）と、ほぼ遠方面は遮蔽なし
  if(abs(d-0.99609375)<2e-6 || d>0.99995){ gl_FragColor=vec4(1.0,1.0,1.0,1.0); return; }
  vec3 P=vp(vUv,d);
  vec2 tx=vec2(uTexel.x,0.0), ty=vec2(0.0,uTexel.y);
  vec3 Pr=vp(vUv+tx,rd(vUv+tx)), Pl=vp(vUv-tx,rd(vUv-tx)), Pu=vp(vUv+ty,rd(vUv+ty)), Pd=vp(vUv-ty,rd(vUv-ty));
  vec3 dx=(abs(Pr.z-P.z)<abs(Pl.z-P.z))?(Pr-P):(P-Pl);
  vec3 dy=(abs(Pu.z-P.z)<abs(Pd.z-P.z))?(Pu-P):(P-Pd);
  vec3 N=normalize(cross(dx,dy));
  vec3 T=normalize(cross(N, abs(N.y)<0.9?vec3(0.0,1.0,0.0):vec3(1.0,0.0,0.0)));
  vec3 B=cross(N,T);
  float rnd=h12(gl_FragCoord.xy+vec2(fract(uTime*0.37)*53.0));
  float R=uRadius*(1.0+(-P.z)*0.0035);
  float occ=0.0;
  for(int i=0;i<12;i++){
    float fi=float(i)+0.5;
    float ang=fi*2.39996+rnd*6.2832;
    float rr=sqrt(fi/12.0)*R;
    float e=0.18+0.82*h12(vec2(fi,rnd*91.0));
    float cs=sqrt(1.0-e*e);
    vec3 S=P+(T*cos(ang)+B*sin(ang))*rr*cs+N*rr*e;
    vec4 pc=uProj*vec4(S,1.0);
    vec2 suv=pc.xy/pc.w*0.5+0.5;
    if(suv.x<0.0||suv.x>1.0||suv.y<0.0||suv.y>1.0) continue;
    float sd=rd(suv);
    if(abs(sd-0.99609375)<2e-6) continue;          // 空：遮らない
    float sz=vp(suv,sd).z;
    float dz=sz-S.z;
    float rk=smoothstep(0.0,1.0,R/max(0.001,abs(P.z-sz)));
    occ+=step(uBias,dz)*rk;
  }
  float ao=pow(clamp(1.0-occ/12.0,0.0,1.0),1.5);
  float zl=clamp(-P.z/uFar,0.0,1.0);
  gl_FragColor=vec4(ao, floor(zl*255.0)/255.0, fract(zl*255.0), 1.0);
}`;
const AOBLUR_FRAG=`uniform sampler2D tSrc; uniform vec2 uDir; varying vec2 vUv;
float dp(vec4 c){ return c.g+c.b/255.0; }
void main(){
  vec4 c0=texture2D(tSrc,vUv); float z0=dp(c0);
  float sum=c0.r, ws=1.0;
  for(int i=1;i<=4;i++){
    float fi=float(i); float w0=exp(-fi*fi*0.16);
    vec4 a=texture2D(tSrc,vUv+uDir*fi), b=texture2D(tSrc,vUv-uDir*fi);
    float k=60.0/(0.02+z0);
    float wa=w0*exp(-pow(abs(dp(a)-z0)*k,2.0)), wb=w0*exp(-pow(abs(dp(b)-z0)*k,2.0));
    sum+=a.r*wa+b.r*wb; ws+=wa+wb;
  }
  gl_FragColor=vec4(sum/ws, c0.g, c0.b, 1.0);
}`;
const STREAK_FRAG=`uniform sampler2D tSrc; uniform vec2 uTexel; uniform float uStride; uniform vec3 uTint; varying vec2 vUv;
void main(){ vec3 c=vec3(0.0); float ws=0.0;
  for(int i=-5;i<=5;i++){ float fi=float(i); float w=1.0/(1.0+abs(fi)*0.55); c+=texture2D(tSrc,vUv+vec2(uTexel.x*uStride*fi,0.0)).rgb*w; ws+=w; }
  gl_FragColor=vec4(c/ws*uTint,1.0); }`;
function mkRT8(w,h,depth){
  return new THREE.WebGLRenderTarget(w,h,{type:THREE.UnsignedByteType,format:THREE.RGBAFormat,
    minFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter,depthBuffer:!!depth,stencilBuffer:false});
}
const _aoHide=[], _cc=new THREE.Color();
function renderAO(){
  const A=POST.ao, M=POST.mats;
  if(!POST.aoOn||!A.rt||!POST.depthMat){ M.comp.uniforms.uAOk.value=0; return; }
  // 深度プリパス：半透明・加算・深度を書かないものは除く（煙・火球・光線・空など）
  _aoHide.length=0;
  scene.traverse(o=>{
    if(!o.visible||!o.material) return;
    const m=Array.isArray(o.material)?o.material[0]:o.material;
    if(!m) return;
    if(o===skyMesh) return;                                   // 空のドームは深度に残す（遠方として扱われる）
    if(m.transparent||m.depthWrite===false||m.depthTest===false||o.isPoints||o.isLine||o.isSprite){ _aoHide.push(o); o.visible=false; }
  });
  const ca=renderer.getClearAlpha(); renderer.getClearColor(_cc);
  const fogPrev=scene.fog; scene.fog=null;
  scene.overrideMaterial=POST.depthMat;
  try{
    renderer.setClearColor(0x000000,1);
    renderer.setRenderTarget(A.depth);
    renderer.render(scene,camera);
  }catch(e){}
  scene.overrideMaterial=null; scene.fog=fogPrev;
  renderer.setClearColor(_cc,ca);
  for(let i=0;i<_aoHide.length;i++) _aoHide[i].visible=true;
  _aoHide.length=0;
  const U=M.ao.uniforms;
  U.tDepth.value=A.depth.texture; U.uTexel.value.set(1/A.w,1/A.h);
  U.uProj.value.copy(camera.projectionMatrix); U.uInvProj.value.copy(camera.projectionMatrixInverse);
  U.uNear.value=camera.near; U.uFar.value=camera.far; U.uTime.value=SKYU.uTime.value;
  fsPass(M.ao,A.rt);
  M.aoBlur.uniforms.tSrc.value=A.rt.texture; M.aoBlur.uniforms.uDir.value.set(1/A.w,0); fsPass(M.aoBlur,A.blur);
  M.aoBlur.uniforms.tSrc.value=A.blur.texture; M.aoBlur.uniforms.uDir.value.set(0,1/A.h); fsPass(M.aoBlur,A.rt);
  M.comp.uniforms.tAO.value=A.rt.texture; M.comp.uniforms.uAOk.value=AO_STRENGTH;
}
function renderStreak(){
  const Sk=POST.streak, M=POST.mats;
  if(!POST.streakOn||!Sk.a||POST.mips.length<2){ M.comp.uniforms.uStreak.value=0; return; }
  const src=POST.mips[1];
  let tex=src.texture;
  const strides=[1,3,9];
  let dst=Sk.a, other=Sk.b;
  for(let i=0;i<3;i++){
    M.streak.uniforms.tSrc.value=tex; M.streak.uniforms.uTexel.value.set(1/src.width,1/src.height); M.streak.uniforms.uStride.value=strides[i];
    fsPass(M.streak,dst); tex=dst.texture; const t=dst; dst=other; other=t;
  }
  M.comp.uniforms.tStreak.value=tex; M.comp.uniforms.uStreak.value=STREAK_STRENGTH;
}
