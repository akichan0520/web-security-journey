# 参考書増補版 — 改訂内容

更新日：2026年10月20日。既存の全36章と特別講義は保持しています。

## 新しく収録した3冊

1. **DB完全読本（18講義）**：`textbooks/01-database-textbook.md` ／ Web: `docs/database-book.html`
2. **Cookie・セッション完全読本（20講義）**：`textbooks/02-cookie-session-textbook.md` ／ Web: `docs/cookie-book.html`
3. **Cookie×DB総合レビュー**：`textbooks/03-database-cookie-integration.md` ／ Web: `docs/integration-book.html`

どの講義も「原理 → 具体例 → コードの読み方 → 想定結果 → 原因 → 防御と限界 → 思考問題 → 詳解 → ナレーション」の流れを意識しました。一次資料へのリンクは各参考書末尾にあります。

## GitHub Pages の設定

リポジトリ直下に `README.md` / `docs/` / `textbooks/` / `chapters/` が並ぶ構成でアップロードします。その後 Settings → Pages → Deploy from a branch → main /docs を指定します。

- トップ：`https://<ユーザー名>.github.io/<リポジトリ名>/`
- DB読本：`https://<ユーザー名>.github.io/<リポジトリ名>/database-book.html`
- Cookie読本：`https://<ユーザー名>.github.io/<リポジトリ名>/cookie-book.html`
- 総合編：`https://<ユーザー名>.github.io/<リポジトリ名>/integration-book.html`

ここに掲載したURLは**一般形**で、公開済みを意味しません。

## 安全性と検証範囲

* 読者は**PHP・SQL・攻撃を実行しない**。コードはHTMLページ内のエスケープ済みコードブロックで表示。
* HTMLポータルと参考書Web版のブラウザ用JavaScriptは、目次検索・読み上げなど**表示用のみ**。
* 教材に本物の資格情報、Cookie、IPアドレスの個人データを入れない。
* `tools/build_textbooks.py` は編集者がMarkdownからHTMLを生成するためのツール。読者にPythonの用意は不要。
* 静的な構造テストと、JavaScript構文チェックを行う想定。掲載SQL/PHPの製品別実行検証はしていないため、性能値や実装差を「実測」と誤記しない。
