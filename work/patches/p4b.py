import sys, re; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# 歌舞伎町：自前の巨大ボクセル車の配置を、共通の駐車車両（実寸）に置き換える
p.rex(r"  // ── 路上の車と設備 ──\n  for\(let i=0;i<XL\.length;i\+\+\)\n    for\(let j=0;j<ZL\.length-1;j\+\+\)\{\n      const z0=ZL\[j\]\+ZW\[j\]/2\+8, z1=ZL\[j\+1\]-ZW\[j\+1\]/2-16;.*?        x\+=RI2\(18,38\);\n      \}\n    \}\n",
      "  // ── 路上の車と設備 ──\n  placeCars(0.95);\n")
p.rep("  gm.userData.wetK=0.45;", "  gm.userData.wetK=0.30;")
p.rep("  ()=>({x:XL[2]+1.0, y:27, z:ZL[5]+80, yaw:0, pitch:-0.085}),", "  ()=>({x:XL[2]+1.0, y:33, z:ZL[5]+74, yaw:0, pitch:-0.045}),")
p.rep("  ()=>({x:XL[2]+XW[2]/2+70, y:36, z:ZL[2]+ZW[2]/2+66, yaw:Math.PI*0.74, pitch:-0.17}),       // 渋谷：交差点の南東上空から。QFRONT・109・スクランブルスクエア",
      "  ()=>({x:XL[2]+2.0, y:40, z:ZL[2]+ZW[2]/2+178, yaw:0, pitch:-0.15}),                        // 渋谷：南の大通りの上空から交差点へ。QFRONT・大型ビジョン・スクランブルスクエア")
p.save()
