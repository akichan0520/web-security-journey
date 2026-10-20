# 第11章：HTTPヘッダー・Cookie・セッション

> **読解教材（実行不要）** — 以下のコードは比較のための断片です。危険版を実行・公開しないでください。

**難易度：** 中級

## この章でできるようになる
リクエスト/レスポンスヘッダー、Set-Cookie、HttpOnly、Secure、SameSiteとセッションの関係を説明する。

## 全体像
Cookieはブラウザが保持して毎回送る識別情報。セッションの中身はサーバー側。

## 🎙 読み上げ可能な講師ナレーション
ログイン後に毎回パスワードを送り直さなくてもよいのはセッションの仕組みがあるからです。ただしCookieは盗まれるリスクがあります。HttpOnlyはJavaScriptからのCookie読取りを抑え、SecureはHTTPS送信に制限します。SameSiteはCSRFリスクを下げますが万能ではありません。

## 1. 危険なコードを読む
未信頼の値がどこから来て、どの命令や判断へ渡るかに注目してください。

```php
// 危険: セッションIDをURLに混ぜる
$link = '/account?sid=' . session_id();
```

## 2. 安全側のコードと比較する
これは設計上の考え方を伝える**抜粋**です。例外処理や周辺設定が省略されている場合があります。

```php
session_set_cookie_params([
  'httponly' => true,
  'secure' => true,  // HTTPS前提
  'samesite' => 'Lax',
]);
session_start();
// 認証成功時に session_regenerate_id(true);
```

## 3. 一行ずつ意味を説明する
1. httponlyはJSからのCookie読取りを制限する（すべてのXSS被害を防ぐわけではない）。
2. secureはHTTPS接続での送信を求める。本番でHTTPSを前提に設定する。
3. session_regenerate_idは権限変化後のセッション固定攻撃リスクを低減する。

## 4. 頭の中で処理の流れを追う
① Cookieで識別子送信→② サーバー側の状態参照→③ 権限確認→④ 応答生成。

### 根本原因
URLが履歴、ログ、共有リンクに残り、識別子が漏れる。

### 修正の原理
セッションIDはログイン状態を識別するための機密値。URLに含めると履歴やログに残る。Cookie属性だけで全リスクは解消せず、CSRFやXSSの対策も必要。

### 防御を重ねるとしたら
CookieはHttpOnly、SameSite、HTTPS本番時はSecureを設定。権限上昇時はID再生成。

## 5. 紙上ハンズオン（実行不要）
質問：SameSite=LaxだけでCSRFトークンは不要？ まず答えを見ずに、危険版のどの部分が原因となるか一行で説明してください。

**確認課題：**
安全側のコードを読んで、上の問題をどう防ぐか説明する。実行・HTTP要求・入力操作は不要。

<details><summary>解答・理由を開く</summary>

**答え：** いいえ。防御を重ね、状態変更操作ではCSRF対策を実装します。

**着目点：** セッションIDはログイン状態を識別するための機密値。URLに含めると履歴やログに残る。Cookie属性だけで全リスクは解消せず、CSRFやXSSの対策も必要。

</details>

## 6. 関連資料
- [一次資料を読む](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [特別講義06：Cookie窃取とセッションハイジャック（初級～上級）](../guides/deep-dive-06-cookie-session-hijacking.md)
- [用語集](../guides/glossary.md)
- [36章索引](../README.md)

---

**注意：** 危険なコードは説明用の反例です。実行する必要はなく、完成品へ流用しないでください。安全版も教材用の部分コードであり、単独で本番運用できる保証はありません。
