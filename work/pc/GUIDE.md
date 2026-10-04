# TOKYO TEARDOWN PC — コード案内（作業エージェント向け）

## 何のプロジェクトか
東京（歌舞伎町／渋谷スクランブル／西新宿高層ビル街）をボクセルで再現し、13種の兵装で解体する単一 HTML のゲーム。
three.js r128（UMD、HTML に同梱・通信不要）＋自作の剛体／支持判定／グリーディメッシュ／ポストプロセス。
**納品物は `TOKYO_TEARDOWN_PC.html` 1 ファイル。** npm・ビルドツール・外部リソース・ネットワークは使わない（フォント・画像・音すべて手続き生成）。

## 対象環境（今回）
ユーザーの **M5 MacBook Pro（2026, 32GB）**: 14インチ Liquid Retina XDR 3024×1964・devicePixelRatio 2・ProMotion 120Hz、Safari 26 / Chrome。
WebGL2・HalfFloat RT・MSAA が使える前提で画質を上げてよい（ネイティブ解像度 ≈ 5.9MP）。ただし自動画質の段階は残す。
キーボードだけで遊べること（マウス・トラックパッド・ゲームパッドは任意）は必須。MacBook の F1/F2 は輝度キーなので頼らない。

## ファイル構成
- `work/TOKYO_TEARDOWN_iPhone17_Enhanced.html` … ベース（iPhone 版）。**直接編集しない。**
- `work/pc/build.py` … ベースに PC 版の差分を当てて `work/TOKYO_TEARDOWN_PC.html`（と `TOKYO_TEARDOWN_PC.html`）を生成する。
  `rep(old,new,count=1)`＝完全一致の置換（件数が違えば exit 1）、`between(a,b,new)`＝a から b の直前までを差し替え。
  差し込むソース: `style_pc.css`（CSS 全体）、`body_pc.html`（本文 HTML 全体）、`ui_pc.js`（HUD・入力・メニュー）、`post_pc.js`（SSAO/ストリーク）、`weapons_pc.js`（新兵装）。
- 生成物 `work/TOKYO_TEARDOWN_PC.html` の構造: `<style>`（7〜）→ `<body>` の HTML → `<script>` three.js → `<script>` ゲーム本体（`(function(){'use strict'; … })();` の中、約 10,000 行）。
- `work/pc/SYMBOLS.txt` … 生成物の関数・定数の一覧（行番号つき）。`grep -n` で場所を探すのに使う。

## 生成物（ゲーム本体）の主な区画（行番号は work/TOKYO_TEARDOWN_PC.html）
| 行 | 内容 |
|---|---|
| 521 | 定数（VOX=1.4m, MAXCHUNK, FOG など） |
| 558 | 空シェーダー（光害・雲・月・星） |
| 628〜1157 | 動的ライティング：`setupLitMaterial`（onBeforeCompile で MeshBasicMaterial に独自ライティングを注入。LIT_PRE/LIT_MAIN）、点光源 `addLight`/`updLights`（NLIT=16）、赤熱 `addHot`、看板 `SIGNS` |
| 1158 | 看板の照り返し（光の地図 buildLightMap） |
| 1241〜1429 | ランドマークの特殊形状（歌舞伎町タワー、QFRONT、センター街アーチ） |
| 1430 | 走る車 `TRF`（InstancedMesh、車線、ヘッドライト）、`PARKED` 駐車車両 |
| 1560 | 歩行者 `PED`、赤提灯 `LAN` |
| 1697 | 信号機 `SIG` |
| 1767 | 濡れた路面の反射 `WET`（平面反射 RT） |
| 1847 | VFX（火球・煙 InstancedMesh、火花、歪み） |
| 2057 | 画質プリセット `QLV`（5 段階）、`applyLevel`、`setQuality`、`updPerf`（自動画質） |
| 2123〜2583 | ポストプロセス（MSAA RT → ブルーム → SSAO → ストリーク → 合成 COMP_FRAG） |
| 2584 | グリーディメッシュ `greedy`/`buildGeo`（頂点属性 aM＝素材＋損傷段階） |
| 2755〜4640 | 街の生成：`MATS`（素材表）、建物生成 `mkBld` 系（zakkyo/shop/apart/office/tower…）、ボクセル文字、各マップ（歌舞伎町 `buildKabukicho`、渋谷、西新宿）、ランドマーク `regLM`、路上の車・設備 `placeCars`/`placeStreetTrees`/`placeUtils` |
| 4751 | マップ切替 `genCity(mapId,seed)`、`spawnOverview`、`VIEWS` |
| 5119 | 空間グリッド `cellAt`/`bldAt`/`solidAt` |
| 5152〜6149 | 破壊 `damageSphere` 等、支持判定→剥離、塊（剛体）`spawnChunk` |
| 6294〜6937 | 粒子 `fx`/`gxA`、破片 `DEB`、火災 `fires`/`spreadFire`、効果プール `efx` |
| 6938 | 音 `Snd`（Web Audio、全て合成） |
| 7119 | 兵装表 `WPN`、`fireWeapon`、`aimRay`/`rayCast` |
| 7398 | 機関砲 `gunTick`、絨毯爆撃 `fireCarpet`、焼夷弾 `fireIncend` |
| 8019 | カメラ `cam`/`inp`/`updCam`（`fovBase()`＝設定視野角×ズーム） |
| 8137 | 毎フレーム `step(dt)`（物理・兵装・粒子・火災・塊・メッシュ再生成の予算） |
| 8164 | モード／結果 `MODES`, `updRun`, `showResult` |
| 9145〜9857 | **UI ブロック（`work/pc/ui_pc.js` と同じ内容）**：HUD、スコア演出、武器バー、設定 `PCS`、入力（キーボード・マウス・パッド）、キーナビ `KNAV`、タイトル、メニュー、ミニマップ |
| 9858 | 初期化 `initScene`、`resize`、起動列、`setPaused`、`loop`、検証フック `window.__tt`（`__tt.pc` が PC 固有） |

## 検証の仕方（ヘッドレス Chromium・SwiftShader・GPU なし）
- 構文: `python3 work/pc/build.py` が「applied N patches」と出れば差分は当たっている。構文は
  `node -e "const fs=require('fs');const t=fs.readFileSync('work/TOKYO_TEARDOWN_PC.html','utf8');const s=t.split('<script>')[2].split('</script>')[0];new Function(s);console.log('ok')"`
- 起動して式を評価: `cd work/test && node probe_pc.mjs ../TOKYO_TEARDOWN_PC.html "<JS式>" [待ちms] [shot.png] [quality]`（約 2〜4 分。`window.__tt` のフックが使える。`VW=1920 VH=1080` 環境変数で解像度）
- 一式: `node work/test/suite_pc.mjs work/TOKYO_TEARDOWN_PC.html`（約 8 分、25 項目）。`--shots` で最高画質のスクリーンショット。
- `__tt` の主なフック: `genCity(m,seed)`, `step(dt)`, `selW(id)`, `setCd(0)`, `fireWeapon()`, `aimRay()`, `cam`, `updCam(dt)`, `blds`, `killedVox()`, `S`, `setQuality('ultra'|'high'|'mid'|'low')`, `renderFrame(dt)`, `POST()`, `pc.*`（`start`, `key(code,down)`, `look(dx,dy)`, `openMenu`, `PCS`…）

## 作法
- UI 文言は日本語。既存のトーン（簡潔・体言止め）に合わせる。
- 時間依存の処理は `dt` に比例させる（`dtK`, `chance(p)`, `nK(n)`, `dampK(k)` を使う）。毎フレームの固定確率や固定減衰を書かない。
- 新しい GPU 資源はプールにし、`genCity` の再生成で解放／再利用する（`disposeBld`、`removeChunk` の流儀）。
- 1 フレームの予算を意識する（`step` の `geoBudget`/`scanBudget`/`TB`）。重い処理は複数フレームに分ける。
- 変更は **`work/pc/feat/<名前>.py`** という「機能モジュール」で書く（`build.py` が `feat/` のモジュールを名前順に適用する）。
  形式:
  ```python
  # work/pc/feat/10_example.py
  TITLE='例：…'
  def apply(rep, between, src):
      # src['ui'], src['css'], src['body'] は差し込み前のソース文字列を書き換えるための辞書（rep と同じ完全一致置換を行う関数 src.rep('ui', old, new)）
      rep("既存の一意な文字列", "置換後")
  ```
  完全一致で置換すること。曖昧な短い文字列を anchor にしない（他の機能モジュールと衝突する）。

## 共通フックとマーカー（work/pc/feat/19_hooks.py が用意。**新しい機能は必ずこれを使う**）
同じ行を複数の機能が置換すると 2 つ目以降が失敗するため、共有の行は直接触らず、フック配列に push するかマーカーを置換する。
- フック配列 `HOOKS`（本体スコープ、どこからでも参照可）: `HOOKS.init.push(fn)`（initScene の空の生成直後。プールを 1 度だけ作る）、`HOOKS.build.push(fn)`（genCity の最後、seed 付き乱数の中）、`HOOKS.reset.push(fn)`（resetWorld）、`HOOKS.update.push(fn(dt))`（step の毎フレーム）、`HOOKS.blast.push(fn(x,y,z,R))`（detonate の爆風）、`HOOKS.lights.push(fn(cand,dt))`（updLights の候補。`cand.push({x,y,z,r,c:[r,g,b],i,tau:1,s:0})`）、`HOOKS.hud.push(fn(dt))`（updHUD）。
  登録は定義置き場で `HOOKS.build.push(myBuild);` のように書く（モジュール評価時に実行される。genCity は起動列の最後で呼ばれるので間に合う）。
- マーカー（`rep(marker, 自分のコード + '\n' + marker)` のように、**置換後も同じマーカーを残す**）:
  `/*@MATS*/`（MATS 素材表の末尾。新しい素材 ID は 46〜63 を使う。`M_*` 配列は 64 枠）、`/*@DEFS*/`（本体の関数・定数の定義置き場。resetWorld の直前）、`/*@UI_DEFS*/`（UI ブロックの定義置き場）、`/*@CSS*/`（CSS 末尾。`src.rep('css',...)`）、`<!--@BODY-->`（本文 HTML。`src.rep('body',...)`）、`<!--@MENU_ROWS-->`（設定メニューの行を足す）、`/*@MENU_RENDER*/`（renderMenu の中で行を描く）、`/*@PCS_DEF*/`（設定の既定値。`, foo:1 /*@PCS_DEF*/` のように）、`/*@PCS_APPLY*/`（applyPCS の正規化）、`/*@KEYS*/`（keydown の switch に `case 'KeyX': ...; break;` を足す）、`/*@GAME_KEYS*/`（preventDefault するキー。`'KeyX',/*@GAME_KEYS*/`）、`/*@PCDBG*/`（`__tt.pc` の検証フック。`foo:()=>..., /*@PCDBG*/`）、`<!--@KEYS_LEGEND-->`（操作一覧の末尾に行を足す）。
- シェーダの cacheKey は文字列長から自動で変わるので触らない（LIT_PRE/LIT_MAIN/LIT_COLOR、WET_PRE/WET_MAIN を置換すれば鍵も変わる）。
- 既存の機能モジュール 00〜20 が置換した行は、生成物の文面が変わっている。anchor は **生成物（work/TOKYO_TEARDOWN_PC.html）の現在の文面**から取ること。
