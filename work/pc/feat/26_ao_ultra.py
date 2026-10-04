# M5 向け：最高画質では SSAO をフル解像度（DPR2 でも細部の接触影が潰れない）、ブルーム段数と反射解像度はそのまま
TITLE='最高画質の SSAO をフル解像度に'
def apply(rep, between, src):
    rep("  {mp:99,   refl:1, smoke:260, ped:1.0,  mips:6, msaa:true,  ao:1, streak:1},   // 最高：ネイティブ解像度・SSAO・反射を毎フレーム",
        "  {mp:99,   refl:1, smoke:260, ped:1.0,  mips:6, msaa:true,  ao:2, streak:1},   // 最高：ネイティブ解像度・SSAO（フル解像度）・反射を毎フレーム")
    rep("  if(POST.aoOn){                               // SSAO は半分の解像度で計算する\n    const aw=Math.max(1,w>>1), ah=Math.max(1,h>>1);",
        "  if(POST.aoOn){                               // SSAO は半分の解像度で計算する（最高画質ではフル解像度）\n    const full=QLV[POST.level]&&QLV[POST.level].ao>=2;\n    const aw=full?w:Math.max(1,w>>1), ah=full?h:Math.max(1,h>>1);")
