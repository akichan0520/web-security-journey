# 総合編：Cookieとデータベースはどうつながっているか？ — 認証済み注文閲覧APIをコードレビュー

> **読解専用。** 脆弱なアプリは起動せず、実際の通信も送信しません。データは架空。ここではDB読本とCookie読本の知識を統合します。実用コードの完成品ではなく、安全設計の判断点を明らかにする抜粋です。

## 1. 概観：CookieをDBに直接送るわけではない

```text
ブラウザ
 │ GET /orders
 │ Cookie: __Host-session=[架空ID]
 ▼
Webサーバー / PHP
 │ ① HTTPSを受理しCookieを読む
 │ ② セッション保存先からIDを照合（期限・失効も見る）
 │ ③ ログイン済み利用者のuser_idを得る
 │ ④ 対象の注文を見る権限を判定
 │ ⑤ 固定したSQL文に認可済みuser_idを束縛
 ▼
データベース（orders.customer_idで絞り込む）
 │ ⑥ 最小限の列を返す
 ▼
PHP
 │ ⑦ JSON応答の構造と機密情報を確認
 ▼
ブラウザ（HTMLへ表示する場合は文字列として安全に扱う）
```

**DBにはログイン用のセッション保存先と、業務データ保存先の2種類の役割がある**ことに注目します。セッション保存先はRedisなどDB以外の場合もあり、説明を簡潔にするため同じ図に示しています。HTTP CookieをブラウザからSQLとしてそのままDBへ送るのではありません。

## 2. 反例：SQLはパラメータ化済みでも危険

```php
<?php
session_start();
$requestedId = (int)($_GET['customer_id'] ?? 0);
$stmt = $pdo->prepare('SELECT id, total_yen FROM orders WHERE customer_id = :id');
$stmt->execute([':id' => $requestedId]);
$orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
```

**このコードはSQLインジェクションに対しては値の束縛がある**一方、要求元利用者と `$requestedId` の関係を確認していません。ログイン済みなら自由に顧客IDを指定して注文閲覧できる設計なら、オブジェクト単位の認可不足です。

## 3. 安全側の設計断片：認証・認可・パラメータ化を分離

```php
<?php
// session_start()やCookie属性・期限・失効チェックは前段ですでに完了した想定
$userId = $_SESSION['user_id'] ?? null;
if (!is_int($userId)) {
    // 401 応答を返して終了する（関数・出力処理は省略）
    return;
}

// 顧客個人の注文閲覧では要求パラメータで所有者を選ばせない例
$stmt = $pdo->prepare(
    'SELECT id, total_yen, status FROM orders WHERE customer_id = :owner ORDER BY id DESC'
);
$stmt->bindValue(':owner', $userId, PDO::PARAM_INT);
$stmt->execute();
$orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
```

**解説：** `$_SESSION['user_id']` は事前に安全に発行・照合されたセッションを前提とし、利用者が渡した `customer_id` を所有者IDとして採用していません。`prepare` はSQL構造と値を分離します。API応答ではJSONの型と適切なContent-Typeを扱い、HTML表示時は`textContent`等で文字列として表示します。

**限界：** 管理者が他人の注文を見るユースケース、委任権限、所属部署の権限、複数テナント、注文キャンセルなどでは追加の認可ポリシーが必要です。これをコピペしても本番で安全な認証システムは完成しません。

## 4. セッションの保存先と失効を設計する

| 格納項目 | 役割 | 気を付ける点 |
|---|---|---|
| `session_id_hash` | セッション秘密の照合識別子 | 生IDのログ・DB流出を避けるための設計例 |
| `user_id` | 認証主体 | 最小限のアカウント情報と関連付け |
| `created_at` | 発行時刻 | 認証時点・絶対期限の判断 |
| `last_seen_at` | 最終利用 | アイドル期限をサーバー側で判定 |
| `expires_at` | 絶対失効時刻 | Cookie期限だけに頼らない |
| `revoked_at` | 明示失効の印 | 存在する場合は以後の利用を拒否 |
| `risk_state` | リスク評価状態 | 指標の誤検知・保存期間・プライバシーを検討 |

**セッションDBと業務DBの違い：** 業務DBの `orders.customer_id` は*顧客*を表し、セッション保存先の `user_id` は*認証された主体*を表します。両者の紐付けが正しいかが認可の核心です。

## 5. 読むだけの時系列：認証と失効を見比べる

| 時刻 | イベント | セッション状態 | 結果 |
|---|---|---|---|
| 10:00 | ログイン成功 | 新しいIDが発行される | 利用可能 |
| 10:03 | 注文参照 | 所有者の注文だけ返す | 正常 |
| 10:05 | 不審な操作の兆候 | 高リスクとして評価 | 調査・追加認証 |
| 10:06 | 管理者側で失効 | `revoked_at` に記録 | 以後IDを拒否 |
| 10:07 | 同じIDで再要求 | 失効を検出 | 401等で拒否 |

**要点：** クライアントがCookieを持っていても、サーバーが失効を確認すれば拒否できます。逆にブラウザからCookieを消すだけでは、第三者が持つコピーを拒否できるとは限りません。

## 6. レビュー演習：10個の安全設計を説明する

次の項目を見ながら、**誰が／どのコードで／何を保証するか**を答えてください。

1. HTTPSを強制する理由は？
2. `HttpOnly` の目的と限界は？
3. ログイン成功時にIDを更新する理由は？
4. セッションIDが失効していることをどこで判断する？
5. SQLのプレースホルダーで防げない脆弱性は？
6. 外部キーを付けても不要になるわけではない対策は？
7. 注文一覧に `SELECT *` を使わない理由は？
8. なぜ `orders.customer_id` と `user_id` の関係を確認する？
9. Cookie値の生ログが危険なのは？
10. 端末感染が疑われる場合の対応はCookie削除だけでよいか？

<details><summary>解答と補足</summary>

1. 通信経路での盗聴・改ざんを防ぐため。端末内部の侵害は防げない。
2. JSからのCookie読取を制限する。XSSによる同一ブラウザ上の不正操作は別問題。
3. 認証前に把握されたIDを認証後の権限と結び付けないため。
4. サーバー側のセッション保存先で期限・失効フラグを確認する。
5. IDOR、XSS、CSRF、認可不足などは別の対策が必要。
6. APIのユーザー単位の認可、入力・出力処理、最小権限など。
7. 機密列の混入や列追加の影響、不要な通信量を防ぐため。
8. 「ログインしている」だけで「他人の注文が見られる」わけではないから。
9. セッションIDは持参人型の秘密になり得るため、ログ流出が乗っ取りに直結する可能性がある。
10. 不十分。サーバー側失効・端末調査・安全な端末での再認証などが必要。

</details>

## 7. 参照の順序

はじめに[データベース完全読本](01-database-textbook.md)のDB-01〜06、続いて[Cookie・セッション完全読本](02-cookie-session-textbook.md)のCK-01〜05、最後に両書の応用編と本章を読むと理解しやすくなります。

一次資料： [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) ／ [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) ／ [OWASP API Security](https://owasp.org/API-Security/) ／ [PHP Manual](https://www.php.net/manual/en/book.session.php)。
