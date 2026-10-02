import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# 粉塵：主役（倒れる建物）を隠し切らない量と色に。接触点から出て、沈む
p.rep("  const nd=Math.min(16,4+Math.round(n*.003));\n  for(let i=0;i<nd;i++){ const a=Math.random()*6.283, r=rf(4,30);\n    vfxSmoke(x+Math.cos(a)*r,rf(2,12),z+Math.sin(a)*r,rf(16,34),rf(8,16),Math.cos(a)*rf(10,26),rf(1,5),Math.sin(a)*rf(10,26),-1); }",
      "  const nd=Math.min(10,3+Math.round(n*.002));\n  for(let i=0;i<nd;i++){ const a=Math.random()*6.283, r=rf(4,26);\n    vfxSmoke(x+Math.cos(a)*r,rf(1,8),z+Math.sin(a)*r,rf(10,22),rf(5,10),Math.cos(a)*rf(10,24),rf(.5,3),Math.sin(a)*rf(10,24),-1); }")
p.rep("  vec3 base=dust?mix(vec3(0.62,0.60,0.56),vec3(0.86,0.84,0.80),vN):mix(vec3(0.15,0.14,0.135),vec3(0.30,0.28,0.26),vN);   // 粉塵は砕けたコンクリートと石膏の灰白色",
      "  vec3 base=dust?mix(vec3(0.44,0.42,0.39),vec3(0.64,0.61,0.57),vN):mix(vec3(0.15,0.14,0.135),vec3(0.30,0.28,0.26),vN);   // 粉塵は砕けたコンクリートと石膏の灰色（白く飛ばない）")
p.save()
