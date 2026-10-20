# 特別講義02：SQLインジェクションの「文字列」と「命令」の境界

> 文字列を**読むだけ**で違いを確認します。SQL送信やDB実行は不要です。

## ケース：書名で完全一致検索

```php
// 問題のある書き方
$sql = "SELECT id,title FROM books WHERE title = '$keyword'";
```

`$keyword` は本来「書名」という**データ**でしかありません。しかしSQL本文の途中で文字列連結すると、値に引用符が混じるケースで命令の境界が壊れ得ます。

```text
想定した問い合わせ：
  SELECT id,title FROM books WHERE title = '星空'

境界が壊れる入力を文字列連結した場合の例（実行不要）：
  SELECT id,title FROM books WHERE title = '' OR '1'='1'

                        ↑利用者の値がWHEREの条件に影響してしまう
```

## 修正の原理

```php
$stmt = $pdo->prepare('SELECT id,title FROM books WHERE title = :title');
$stmt->execute([':title' => $keyword]);
```

1. `prepare` に渡すSQLは一定の形。
2. `:title` は**値の位置**を示す名前付きプレースホルダー。
3. `execute` で値を与える。
4. 利用者の値に引用符があっても、SQLの意味として再解釈させない。

**注意：** プリペアドステートメントが正しく使用されていることが前提です。テーブル名・列名・並び順など、SQLの識別子や構文そのものを値のプレースホルダーでは安全化できません。必要な値は許可リストから選択します。

## ありがちな誤解

| 誤解 | 実際には |
|---|---|
| HTMLでエスケープしたからSQLも安全 | HTMLとSQLでは解釈のルールが違う |
| 変な文字を全部消せばよい | 正常なデータも壊す可能性。SQLと値を分けるのが基本 |
| prepareがあれば他人のデータも読める設計でよい | SQLi対策と認可は独立した問題 |
| バリデーションは不要 | 型や長さ、業務ルールの検証は依然重要 |

## 学習者への質問

`WHERE owner_id = :current_user_id` を削除しても、SQLi対策ができていれば安全ですか？ → **いいえ。** SQLを改変できなくても、そのSQL自体が他人のデータを返すよう作られていれば認可の不備です。

**一次資料：** [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php)
