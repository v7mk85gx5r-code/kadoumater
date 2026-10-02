import sys; sys.path.insert(0,'/home/user/kadoumater/work/patches')
from lib import P
p=P()
# set() の範囲判定を NaN に強くする（短い建物で lv[1] が undefined → y=NaN の書き込みが live だけ増やしていた）
p.rep("    if(!m||x<0||y<0||z<0||x>=W||y>=HH||z>=D) return;\n    const i=at(x,y,z); if(!vox[i]) live++;",
      "    if(!m||!(x>=0&&y>=0&&z>=0&&x<W&&y<HH&&z<D)) return;\n    const i=at(x,y,z); if(!vox[i]) live++;")
p.rep("  const set=(x,y,z,m)=>{ if(!m||x<0||y<0||z<0||x>=W||y>=HH||z>=D) return;", "  const set=(x,y,z,m)=>{ if(!m||!(x>=0&&y>=0&&z>=0&&x<W&&y<HH&&z<D)) return;", 3)
p.rep("      const y=lv[RI(1,Math.max(1,nlv-1))]+1;", "      const y=(nlv>1?lv[RI(1,nlv-1)]:RI(1,Math.max(1,H-3)))+1;")
# 特異点の最終崩壊：引き剥がしが機能するようになったので、仕上げの爆発は少し控えめに（半径175→120）
p.rep("      detonate(A.x,A.y,A.z,175,700,3.0);", "      detonate(A.x,A.y,A.z,120,620,2.6);")
p.save()
