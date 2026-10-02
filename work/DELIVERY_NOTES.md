# TOKYO TEARDOWN — iPhone 17 Enhanced 改修ノート（下書き）

納品物: `TOKYO_TEARDOWN_iPhone17_Enhanced.html`（単一HTML。three.js 0.128.0 を CDN から読み込む）

## 実行条件
- iPhone 17 標準モデル / iOS Safari を第一対象。縦持ち優先、横持ちも配置を最適化。
- 起動には通信が必要（three.js 0.128.0 を cdnjs → jsDelivr → unpkg の順に同一版で取得。失敗時は再試行ボタン）。完全オフラインでは動作しません。
- ファイルを Safari で開くだけで起動します（ビルド・APIキー・npm 不要）。`?debug` を付けると検証フック `window.__tt` と性能表示が使えます。

（テスト結果・未検証事項は最終版で追記）
