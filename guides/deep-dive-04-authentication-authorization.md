# 特別講義04：ログインできることと、他人のデータが見えないことは違う

## 重要な2つの言葉

- **認証（Authentication）：** このリクエストの主体は誰か。
- **認可（Authorization）：** この主体はこの対象を読む・編集する・消す権限があるか。

## IDOR：IDを指定するだけでは認可したことにならない

```php
// 危険：IDだけでメモを探す
$stmt = $pdo->prepare('SELECT * FROM notes WHERE id = :id');
$stmt->execute([':id' => $requestedId]);
```

```php
// 改善：ログイン済み利用者に紐付くメモだけを探す
$stmt = $pdo->prepare('SELECT * FROM notes WHERE id = :id AND owner_id = :owner');
$stmt->execute([':id' => $requestedId, ':owner' => $sessionUserId]);
```

**紙上で考える：** Aliceがログイン中にBobのメモIDを指定すると、上は返す可能性があり、下は返さない。重要なのはIDが連番かUUIDかではなく、対象との権限関係です。

## CSRF：Cookieと「操作の意図」は違う

```php
// 危険な誤解
if (isset($_SESSION['user_id'])) {
    saveProfile($input);
}
```

```php
// 状態変更ではセッションと結び付けたトークンをサーバーで検証する
$expected = $_SESSION['csrf_token'] ?? '';
$received = $_POST['csrf_token'] ?? '';
if (!is_string($expected) || $expected === '' ||
    !is_string($received) || !hash_equals($expected, $received)) {
    http_response_code(403);
    exit;
}
// 検証済みの入力と認可の確認も必要
```

ブラウザはCookieを要求に自動送信することがあり、ログイン済みというだけでは利用者がその操作を意図した証拠になりません。SameSiteやOrigin検査、トークンなどを組み合わせます。

## 3問

1. ログイン済みなら全員のメモを読める？ → **いいえ。認可が別に必要。**
2. UUIDなら認可不要？ → **いいえ。推測困難性と権限確認は別。**
3. POSTならCSRFは成立しない？ → **いいえ。Cookie利用と状態変更の設計次第。**

**一次資料：** [OWASP IDOR](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)、[OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
