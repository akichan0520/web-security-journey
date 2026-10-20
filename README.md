# Web Security Journey — READ & REASON Edition

**HTML → CSS → JavaScript → PHP → SQL / SQLite / MySQL / PostgreSQL / NoSQL → Web脆弱性 → 堅牢な設計**

> 🧠 **実行しない、読むハンズオン**です。実機への攻撃、ローカル環境の構築、脆弱なPHPアプリの起動、Docker、データベース接続は必要ありません。GitHub上のコードだけで、**何が起きる／なぜ危ない／どう直す／直した後も何に注意する**を学びます。

## 📚 大幅増補：DB・Cookieの「読む参考書」シリーズ

> **2026-10-20改訂：既存36章は残したまま、深掘り参考書を3冊追加。** 教材は完全に読解型。PHPやDBを起動する必要はありません。

| 参考書 | 学習範囲 | GitHubで読む | 音声付きWeb版 |
|---|---|---|---|
| **第1巻：データベース完全読本（18講義）** | DBMS、SQL、NULL、JOIN、制約、正規化、ACID、同時更新、隔離、MVCC、索引、EXPLAIN、PDO、SQLi、運用 | [Markdownで読む](textbooks/01-database-textbook.md) | [Web版](docs/database-book.html) |
| **第2巻：Cookie・セッション完全読本（20講義）** | HTTP Cookie、属性、SameSite、PHP、窃取の経路、MFA、失効、CSRF、SOC、DBSC | [Markdownで読む](textbooks/02-cookie-session-textbook.md) | [Web版](docs/cookie-book.html) |
| **総合編：Cookie×DBの設計レビュー** | ログイン済みの注文閲覧APIで認証・認可・SQL・ログを統合 | [Markdownで読む](textbooks/03-database-cookie-integration.md) | [Web版](docs/integration-book.html) |

全ての講義に**詳説・比較コード・紙上演習・理由付き解答・講師用ナレーション**があります。各巻末に参考文献（OWASP・MDN・IETF・NIST・PHP・SQLite・PostgreSQL・MySQL公式）を列挙しています。コードの実行、実ネットワークへのアクセス、DB接続はありません。Web版の読み上げはブラウザのローカル音声合成を使用します。

**おすすめの順序：** 第12〜15章を読んだらDB完全読本、第31〜36章を読んだらCookie完全読本、最後に総合編。正本はそれぞれの `textbooks/*.md` です。Web版の再生成は `tools/build_textbooks.py` で行います（任意、生成時にPython＋mistuneが必要。閲覧する人には不要）。

## 入口

- **教材ポータル：** [`docs/index.html`](docs/index.html) — 36章を検索・切替できる画面。ナレーション読み上げ、比較コード、理解度チェック付き
- **章ごとのMarkdown：** [`chapters/`](chapters/) — GitHubのプレビューで完結。各章に解答を折りたたんで掲載
- **学習ロードマップ：** [`guides/learning-path.md`](guides/learning-path.md)
- **通信・信頼境界図：** [`guides/system-map.md`](guides/system-map.md)
- **用語集：** [`guides/glossary.md`](guides/glossary.md)
- **講師向け進行台本：** [`guides/teacher-guide.md`](guides/teacher-guide.md)
- **特別講義01：** [HTML→JS→PHP→DBを通しで読む](guides/deep-dive-01-request-to-database.md)
- **特別講義02：** [SQLiの命令とデータの境界](guides/deep-dive-02-sqli.md)
- **特別講義03：** [XSSの3種類と出力文脈](guides/deep-dive-03-xss.md)
- **特別講義04：** [認証・認可・IDOR・CSRF](guides/deep-dive-04-authentication-authorization.md)
- **特別講義05：** [DB設計と製品比較・運用](guides/deep-dive-05-database-design.md)
- **特別講義06（新規・重要）：** [Cookie窃取・セッションハイジャックの完全講義（基礎〜応用・図解・公式根拠付き）](guides/deep-dive-06-cookie-session-hijacking.md)
- **Webで特別講義06を閲覧：** [`docs/cookie-session.html`](docs/cookie-session.html) — 日本語・音声読み上げ・章内目次付き

ポータルの「読み上げ」はブラウザの日本語音声合成（Web Speech API）を使い、録音済み音声や外部TTS通信は利用しません。利用可否や音声の品質は端末・ブラウザに依存します。

## どんな読者を想定？

| 入門 | 中級 | 経験者・講師 |
|---|---|---|
| HTMLのタグや変数の意味から | ブラウザとPHPのデータの受け渡しから | 信頼境界、設計レビュー、認可の抜け・防御の限界まで |
| 用語と1行ごとの解説 | SQL・セッション・CRUDの設計 | 誤用例と対策を説明・教育できる |

## 1章の読み進め方

1. **基礎を読む**：この技術の役割を確認。
2. **危険な例を読む**：「利用者が変更できる値」に下線を引く。
3. **安全な例と比べる**：変わった行と変わらない行を特定。
4. **頭の中で追跡する**：入力→処理→結果の流れを予測。
5. **なぜ？を言語化する**：危険の根本原因と対策の限界を説明。
6. **解答を確認する**：知識チェックと一次資料を読む。

**「ハンズオン」の意味：** テキストの注釈、コードレビュー、紙上のデータフロー追跡、自己採点という能動学習です。実行・HTTP要求の送信・攻撃を意味しません。

## 全36章

- **01** [第01章：この教材の読み方・Webの役割分担](chapters/01-この教材の読み方-Webの役割分担.md) — ブラウザ、HTML、CSS、JavaScript、PHP、DBの責任範囲と、コードを読むだけで学ぶ方法を説明できる。
- **02** [第02章：HTTP・URL・DNS・リクエストの旅](chapters/02-HTTP-URL-DNS-リクエストの旅.md) — URLとHTTPの違い、DNS/TCP/TLS、メソッド、ステータス、ヘッダーと本文を区別する。
- **03** [第03章：HTMLの骨格と文書の意味](chapters/03-HTMLの骨格と文書の意味.md) — <!doctype html>、head、body、見出し、段落、リンク、画像を適切に書ける。
- **04** [第04章：セマンティックHTMLとアクセシビリティ](chapters/04-セマンティックHTMLとアクセシビリティ.md) — フォームラベル、代替テキスト、フォーカス、ランドマークを説明できる。
- **05** [第05章：フォーム・GET/POST・入力検証](chapters/05-フォーム-GET-POST-入力検証.md) — フォーム送信、name属性、入力制限、クライアント検証とサーバー検証の差を理解する。
- **06** [第06章：CSS・レイアウト・レスポンシブ](chapters/06-CSS-レイアウト-レスポンシブ.md) — セレクタ、ボックスモデル、Flex/Grid、メディアクエリ、フォーカス装飾を使える。
- **07** [第07章：JavaScriptの基本・変数・関数・イベント](chapters/07-JavaScriptの基本-変数-関数-イベント.md) — const/let、配列、オブジェクト、イベントリスナー、条件分岐を扱える。
- **08** [第08章：DOM操作と安全な文字列表示](chapters/08-DOM操作と安全な文字列表示.md) — querySelector、createElement、textContent、innerHTMLの違いを説明できる。
- **09** [第09章：非同期処理・Promise・fetchとJSON](chapters/09-非同期処理-Promise-fetchとJSON.md) — await/async、HTTPステータス、JSON、例外処理、URLエンコードを理解する。
- **10** [第10章：PHPの基本・変数・配列・関数](chapters/10-PHPの基本-変数-配列-関数.md) — PHPの実行場所、スーパーグローバル、型宣言、関数、JSON応答を理解する。
- **11** [第11章：HTTPヘッダー・Cookie・セッション](chapters/11-HTTPヘッダー-Cookie-セッション.md) — リクエスト/レスポンスヘッダー、Set-Cookie、HttpOnly、Secure、SameSiteとセッションの関係を説明する。
- **12** [第12章：RDBとSQLite：主キー・外部キー・制約](chapters/12-RDBとSQLite-主キー-外部キー-制約.md) — テーブル/行/列、主キー、外部キー、NULL、ユニーク制約と正規化の考え方を理解する。
- **13** [第13章：SQLの検索・JOIN・GROUP BY・集計](chapters/13-SQLの検索-JOIN-GROUP-BY-集計.md) — SELECT、WHERE、ORDER BY、JOIN、GROUP BY、HAVINGの用途を説明する。
- **14** [第14章：トランザクション・インデックス・マイグレーション](chapters/14-トランザクション-インデックス-マイグレーション.md) — ACIDの意味、BEGIN/COMMIT/ROLLBACK、インデックスとクエリ計画を知る。
- **15** [第15章：PDOとプレースホルダー・SQLインジェクション対策](chapters/15-PDOとプレースホルダー-SQLインジェクション対策.md) — SQL文字列連結が危険な理由と、PDO::prepareとexecuteの役割を説明する。
- **16** [第16章：認証・パスワード・セッション固定対策](chapters/16-認証-パスワード-セッション固定対策.md) — 認証と認可、password_hash/verify、セッション固定、ログアウトの仕組みを説明できる。
- **17** [第17章：XSS：反射・格納・DOMの3種類](chapters/17-XSS-反射-格納-DOMの3種類.md) — XSSの3つの典型形と表示コンテキスト、CSPの役割と限界を説明できる。
- **18** [第18章：CSRF：Cookieを使う状態変更の保護](chapters/18-CSRF-Cookieを使う状態変更の保護.md) — CSRFの成立条件、CSRFトークン、SameSiteの違いを理解する。
- **19** [第19章：IDOR・水平権限昇格・認可](chapters/19-IDOR-水平権限昇格-認可.md) — IDORの原因と認証/認可の違い、オブジェクト単位の権限検証を説明できる。
- **20** [第20章：ファイルアップロード・パス操作・SSRF](chapters/20-ファイルアップロード-パス操作-SSRF.md) — アップロードやパス/URL入力が危険になる条件を把握し、安全な設計を提案できる。
- **21** [第21章：セキュリティヘッダー・CSP・HTTPS](chapters/21-セキュリティヘッダー-CSP-HTTPS.md) — CSP、X-Content-Type-Options、Referrer-Policy、HTTPS/TLSの役割を説明できる。
- **22** [第22章：エラーハンドリング・ログ・監視](chapters/22-エラーハンドリング-ログ-監視.md) — エラー処理、HTTPステータス、ログの守り方、監査ログと個人情報の境界を理解する。
- **23** [第23章：テスト設計・回帰テスト・CI](chapters/23-テスト設計-回帰テスト-CI.md) — 正常系と異常系、境界値、回帰テスト、GitHub Actionsの位置づけを理解する。
- **24** [第24章：脅威モデリング・コードレビュー](chapters/24-脅威モデリング-コードレビュー.md) — 資産・攻撃者・入口・信頼境界、データフロー、優先順位付けを説明する。
- **25** [第25章：MySQL・MariaDBとSQLiteの違い](chapters/25-MySQL-MariaDBとSQLiteの違い.md) — SQL方言・クライアント/サーバー方式・InnoDB・インデックス・権限を比較する。
- **26** [第26章：PostgreSQL：JSONB・インデックス・隔離レベル](chapters/26-PostgreSQL-JSONB-インデックス-隔離レベル.md) — PostgreSQLのIDENTITY、JSONB、複数のインデックス型、トランザクションの概念を理解する。
- **27** [第27章：NoSQL・ドキュメントDB・入力型の安全性](chapters/27-NoSQL-ドキュメントDB-入力型の安全性.md) — RDBとドキュメント型DBの特徴・トレードオフ、NoSQLインジェクションを概念として理解する。
- **28** [第28章：DB運用：バックアップ・復元・マイグレーション](chapters/28-DB運用-バックアップ-復元-マイグレーション.md) — バックアップ、復元試験、スキーマ変更、秘密情報とテストデータの分離を設計できる。
- **29** [第29章：REST API設計・CORS・制限と本番化の判断](chapters/29-REST-API設計-CORS-制限と本番化の判断.md) — API設計とメソッド・ステータス、CORS、レート制限、運用段階で追加する対策を説明する。
- **30** [第30章：最終制作：脆弱なコードから堅牢な設計へ](chapters/30-最終制作-脆弱なコードから堅牢な設計へ.md) — 機能要件・認証・認可・入力検証・出力・DB・ログ・テストを一貫して説明する。


### 新設：Cookie・セッション乗っ取り編（第31〜36章）

- **31** [第31章：Cookie・セッションの基本とBearer認証](chapters/31-Cookie-セッションの基本とBearer認証.md) — Cookieとログインを混同せず、Set-Cookie→Cookie→サーバー照合の順序を説明し、窃取時の危険を言語化できる。
- **32** [第32章：Cookie属性と安全なSet-Cookie設計](chapters/32-Cookie属性と安全なSet-Cookie設計.md) — HttpOnly、Secure、SameSite、Domain、Path、__Host-、Partitionedの目的と限界を理解する。
- **33** [第33章：Cookie窃取の経路：XSS・マルウェア・MFAの限界](chapters/33-Cookie窃取の経路-XSS-マルウェア-MFAの限界.md) — XSS、端末内の窃取、セッション固定、CSRFを分類でき、認証強化とセッション保護の違いを説明する。
- **34** [第34章：PHPで考えるセッション固定・再生成・期限・失効](chapters/34-PHPで考えるセッション固定-再生成-期限-失効.md) — 認証前後のID再生成、厳格モード、期限とログアウト時の失効の役割を説明できる。
- **35** [第35章：セッション乗っ取りの検知・ログ分析・対応](chapters/35-セッション乗っ取りの検知-ログ分析-対応.md) — IP/UA変化の偽陽性・偽陰性を理解し、資格情報をログに残さない監視・失効・再認証の流れを設計する。
- **36** [第36章：応用：DBSC・デバイス結合・セッション防御の将来](chapters/36-応用-DBSC-デバイス結合-セッション防御の将来.md) — 従来のBearer CookieとDBSCの違い、仕様と製品展開の違い、現在も残るリスクを説明できる。

> **重要：** この章は実行不要の読解教材です。実在のCookieやアカウント、攻撃用通信、マルウェアは一切使いません。根拠は[NIST/OWASP/MDN等](guides/deep-dive-06-cookie-session-hijacking.md#14根拠資料一次資料公式文書)を参照。

## コードの使い方に関する重要な注意

- **危険版はアンチパターン**です。仕組みを理解するための比較用で、実行・公開・転用は不要です。
- **改善版も機能の全体を実装した完成品ではありません。** 教材の焦点に必要な行だけを抜粋し、周辺の実装が省略されている場合があります。
- コピーできるボタンは学習メモ用です。危険なコードを貼り付けて試すことを推奨しません。
- 実データ、パスワード、秘密鍵、組織の構成情報を教材の例に含めないでください。
- GitHub Pagesは静的なHTML/CSS/JSの表示用です。PHP・SQLのサンプルはコード表示としてのみ含まれます。

## GitHubで公開する場合

空の新規リポジトリを作り、このフォルダの中身をコミットするだけで、すべてのMarkdownがブラウザから閲覧できます。サイト風の学習ポータルを公開する場合は、**Settings → Pages → Deploy from a branch → main /docs** を設定してください。

```sh
# GitHub登録操作の例。教材の「危険なコード」は実行されません。
git init
git branch -M main
git add .
git commit -m "Publish read-only Web Security Journey"
git remote add origin https://github.com/YOUR_USERNAME/web-security-journey.git
git push -u origin main
```

GitHubの操作に使うコマンド以外、教材中のサンプルを実行する必要はありません。GitHub Pages公開を望まない場合でも、Markdownの閲覧のみで全課程を受講できます。

## 内容の修正・追補

**正本は `curriculum.json`** です。36章の各項目を変更したら、`tools/build_reading.py` を実行するとMarkdownとWeb表示用データが同期されます。生成ツールは教材のテキストファイルを作るためのものです。教材のPHP/SQLサンプルは実行しません。

出典の確認には [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)、[MDN Web Docs](https://developer.mozilla.org/ja/)、[PHP公式マニュアル](https://www.php.net/manual/ja/) などを利用しています。章ごとに参照資料を掲載しています。

## ライセンス

[MIT](LICENSE)（コード・構成）。説明文や例示の再利用にあたっては出典・ライセンスを確認してください。
