# データベース完全読本 — SQLの最初の1行から設計・性能・障害対応まで

> Web Security Journey / **閲覧・紙上演習専用** / 2026-10-20確認  
> SQLとPHPは**教材の文字列**として表示しています。DB接続・コマンド実行・攻撃通信は不要です。例は架空の学習用書店データです。  
> 表記：**原理**＝仕様・公式説明に基づくこと、**設計判断**＝条件次第で変わる推奨、**反例**＝使用してはいけない説明用コード。

## この本で身に付けること

- 初心者：行・列・主キー、SELECT、JOIN、NULL、トランザクションを他人に説明できる。
- 中級者：データの重複を抑え、整合性・処理順・参照権限を設計できる。
- 上級者：隔離レベル、MVCC、ロック、実行計画、復旧目標、SQLインジェクションの根本原因まで評価できる。

**学習法：** 各章の「紙上演習」を先に解く→「解答」で照合→講師ナレーションを読み上げる。サンプルの実行結果は説明のための*推論*であり、特定製品・バージョンでの実測ではありません。

**学習用データ**（以後の例で共通）

| customers（顧客） | id | name |
|---|---:|---|
| | 1 | 葵 |
| | 2 | 海斗 |
| | 3 | 凛 |

| orders（注文） | id | customer_id | total_yen | status |
|---|---:|---:|---:|---|
| | 101 | 1 | 1500 | paid |
| | 102 | 1 | 900 | pending |
| | 103 | 2 | 2100 | paid |

顧客3にはまだ注文がありません。**データがないこと**もSQLの理解に欠かせません。

---

## DB-01｜そもそもデータベースとは何か

### 基礎：ファイルとDBMSの違い

CSVはデータを並べられるが、同時更新、参照関係の保証、障害時の原子性、権限管理をCSV自身は提供しません。DBMS（データベース管理システム）は、データを**保存するだけでなく、制約・検索・同時アクセス・回復を管理**します。RDB（関係データベース）は、情報を行と列を持つテーブルで表現し、関係をキーで結びます。

```text
ブラウザ
  │ HTTP: 「葵さんの注文を表示」
  ▼
PHPアプリ（認証・認可・入力検証）
  │ SQL: SELECT ... WHERE customer_id = ?
  ▼
DBMS（SQL解釈→実行計画→読み取り→結果）
  │
  ▼
テーブル customers ──（外部キー）── orders
```

**区別：** PHPは「誰が要求したか、何を許すか」を判断し、DBMSは「正しい制約でデータを保存・取り出す」ことを主に担います。DBの権限も重要ですが、アプリ側のユーザー単位の認可を代わりに実施してくれるとは限りません。

**紙上演習：** `orders.customer_id = 1` は何を意味する？注文数を計算するのはブラウザ・PHP・DBのどこが適切？

<details><summary>解答と解説</summary>`customers.id = 1` の顧客（葵）を参照する値です。通常はDBの `COUNT(*)` で集計し、PHPは認可後に結果を表示します。小規模データをPHPで集計する場合もありますが、通信量・整合性・性能を設計で検討します。</details>

**講師ナレーション：** 「DBは巨大なExcelではありません。『矛盾しないように記録する仕組み』です。『誰でも見られるか』はアプリとDBの両方で制御します。」

---

## DB-02｜テーブル・行・列・型・NULLを正しく読む

### テーブルの定義

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
```

| 行 | 説明 | 気を付ける点 |
|---|---|---|
| `CREATE TABLE customers (` | 顧客テーブルの定義を開始 | 名称は業務上の概念を表す |
| `id INTEGER PRIMARY KEY` | 一意に行を識別する主キー | 主キーの採番方式はDB製品で異なる |
| `name TEXT NOT NULL` | 名前が `NULL` ではないと保証 | 空文字 `''` は別物。業務条件はさらに検証 |
| `email TEXT UNIQUE` | 重複を制限する | NULLとUNIQUEの扱いは製品ごとの仕様確認が必要 |

**NULLは空文字でも0でもありません。** 「値が不明・存在しない」などを表す特別なマーカーです。`WHERE email = NULL` は真にならないため、 `WHERE email IS NULL` と書きます。条件が真・偽だけでなくUNKNOWNにもなる**三値論理**を理解しましょう。

```sql
SELECT * FROM customers WHERE email IS NULL;   -- NULLを探す
SELECT * FROM customers WHERE email = NULL;     -- 判定できない：目的に合わない
```

**紙上演習：** `NOT NULL` と `CHECK (length(name) > 0)` は同じ？ `email = NULL` が検出に使えない理由は？

<details><summary>解答と解説</summary>違います。`NOT NULL` はNULLだけを禁止し、`''` は通常許します。`CHECK` は式の結果による制約で、SQLのNULL/UNKNOWNの扱いにも注意が必要です。NULLを探すには `IS NULL` を使います。</details>

**講師ナレーション：** 「データ型とNULLは検索結果を左右します。未入力と、数字のゼロを同じ意味にしないことが大切です。」

---

## DB-03｜主キー・外部キー・CHECK・UNIQUEで矛盾を防ぐ

```sql
-- SQLite型を中心にした読解例
PRAGMA foreign_keys = ON;        -- 接続ごとに明示。トランザクション開始前
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0)
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total_yen INTEGER NOT NULL CHECK (total_yen >= 0),
    status TEXT NOT NULL CHECK (status IN ('pending','paid','canceled')),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

**原理：** 主キーは1行を識別し、外部キーは「参照先が存在する」ことを守り、CHECKは業務上の条件の一部を保証します。`total_yen` は通貨を扱うために単純な浮動小数点より整数の最小通貨単位を使う例です。ただし為替・税・丸め・負数の業務要件は別途設計します。

**SQLite固有の注意：** 外部キーは各接続で `PRAGMA foreign_keys = ON` を明示し、トランザクション中の切替は効きません。MySQL/PostgreSQLでは同じPRAGMA構文は使用しません。[D1]

**紙上演習：** 顧客に存在しない `customer_id=999` の注文は、外部キーを有効にした場合どうなる？ 顧客を削除したとき何が起こる？

<details><summary>解答と解説</summary>不正な参照は制約違反です。削除時は `ON DELETE` 動作（RESTRICT、CASCADE、SET NULL等）や既定動作に依存します。履歴を消したくない業務ではCASCADEを安易に選ばず、削除禁止や匿名化などを設計します。</details>

**講師ナレーション：** 「PHPで入力チェックをしても、別の更新経路があれば整合性は壊れ得ます。DBにも最後の砦として制約を持たせます。」

---

## DB-04｜SQLの基本文法：SELECT・WHERE・ORDER BY・LIMIT

```sql
SELECT id, total_yen
FROM orders
WHERE status = 'paid' AND total_yen >= 1500
ORDER BY total_yen DESC, id ASC
LIMIT 10;
```

**上から読む説明：** `SELECT` は出す列、`FROM` は対象テーブル、`WHERE` は行を残す条件、`ORDER BY` は表示順、`LIMIT` は返す件数です。SQLは宣言的で、内部の物理的実行順はDBMSが決定します。「書いた順にレコードを1件ずつ実行している」と思わないこと。

**論理的な処理の理解用順序：** `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`。これは概念理解の順番であり、実際のクエリ実行プランの順序とは異なります。

**予想結果：** `id=103, total_yen=2100` と `id=101, total_yen=1500` の順。`ORDER BY` を省略すると行順の保証はありません。

**紙上演習：** `SELECT *` はなぜAPIには慎重に使うべき？ `ORDER BY` が同点の場合は？

<details><summary>解答と解説</summary>`*` は不要列や個人情報を増やし、列追加の影響・通信量も変わり得ます。同点の行順は不定なので `id` など安定したキーを第2ソート条件として書くと結果が再現しやすくなります。</details>

**講師ナレーション：** 「SQLは何を取得するかを宣言し、どう取得するかの多くをDBMSに任せます。表示順は必要なら必ず明記します。」

---

## DB-05｜JOINの仕組みを「行の組み合わせ」で理解する

```sql
SELECT c.name, o.id AS order_id, o.total_yen
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
ORDER BY c.id, o.id;
```

| name | order_id | total_yen |
|---|---:|---:|
| 葵 | 101 | 1500 |
| 葵 | 102 | 900 |
| 海斗 | 103 | 2100 |
| 凛 | NULL | NULL |

`INNER JOIN` は一致する組だけ残します。`LEFT JOIN` は左側の各行を残し、右に相手がなければ右側の列をNULLにします。重要なのは**WHEREに右テーブルの条件を書くと、NULL行が取り除かれ、結果的にINNER JOINのような結果になる場合がある**ことです。

```sql
-- 注文がない顧客も残し、「paid」の注文だけ右側に結ぶ
SELECT c.name, o.id
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.id AND o.status = 'paid';
```

**紙上演習：** `WHERE o.status = 'paid'` と `ON ... AND o.status = 'paid'` の違いを、顧客3の行で説明する。

<details><summary>解答と解説</summary>`WHERE` に置くと右側がNULLの顧客3は条件が真にならず除外されます。`ON` に置くと右側の「結合可能な注文」だけ制限し、左側の顧客3はNULL付きで残ります。</details>

**講師ナレーション：** 「JOINの本質は2つの表を重ねることではなく、対応する行同士を条件で組み合わせることです。」

---

## DB-06｜集計・GROUP BY・HAVING・COUNTの落とし穴

```sql
SELECT c.id, c.name,
       COUNT(o.id) AS order_count,
       COALESCE(SUM(o.total_yen), 0) AS total
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id, c.name
HAVING COALESCE(SUM(o.total_yen), 0) >= 0
ORDER BY c.id;
```

`COUNT(*)` はグループ内の**行数**、`COUNT(o.id)` は指定列がNULLでない**値の数**です。LEFT JOINで注文がない顧客も1行として残ると、`COUNT(*)` は1、`COUNT(o.id)` は0になります。`SUM` は該当値がなければNULLになり得るため `COALESCE` で表示値を補います。

`WHERE` は**集約する前**の行、`HAVING` は**集約した後**のグループを絞るのが基本です。

**紙上演習：** 葵・海斗・凛の注文数と合計金額を予想する。

<details><summary>解答と解説</summary>葵：2件/2400円、海斗：1件/2100円、凛：0件/0円。`COUNT(o.id)` と `COALESCE` の効果に着目します。</details>

**講師ナレーション：** 「集計ではNULLをどう数えるかが、業務上の数字の正しさに直結します。COUNTの引数は重要です。」

---

## DB-07｜正規化とER図：なぜデータを分割するのか

**反例：** `orders` に `customer_name`、`customer_email`、`customer_address` を毎回コピーすると、住所変更時に過去注文との整合性が崩れる可能性があります。これが更新時異常（update anomaly）の典型例です。

```text
customers (1) ─────────── (N) orders
 id PK                         id PK
 name                          customer_id FK
 email                         total_yen
                               status
```

**第1正規形**では繰り返しグループ・非原子的な値を避ける方向で考えます。**第2正規形**は複合キーの一部だけへの従属、**第3正規形**は非キー項目を介した推移的従属を整理します（形式的な定義はキーと関数従属性に依存）。ただし、住所のように「注文時点の配送先」を履歴として保持したい場合は**あえて注文にコピーする**のが正しい場合もあります。重複の有無ではなく、**変更時に何を真実とみなすか**で判断します。

**紙上演習：** `orders` に顧客名を格納するのは常に間違い？

<details><summary>解答と解説</summary>常に間違いではありません。注文時点の請求先・配送先を不変のスナップショットとして残す要件もあります。参照マスタと取引時点の記録を区別し、更新規則を明記するのが重要です。</details>

**講師ナレーション：** 「正規化は『とにかく分割』ではありません。何が変わって何が残るかを決める設計作業です。」

---

## DB-08｜トランザクションとACIDを実務で理解する

送金や在庫引当のように複数の変更をひとまとまりに扱うのがトランザクションです。

```sql
BEGIN;
UPDATE stock SET quantity = quantity - 1
 WHERE item_id = 7 AND quantity >= 1;
-- 更新した行数が1なら注文を追加し、0ならROLLBACKする（アプリ側の判断）
INSERT INTO reservations(item_id, customer_id) VALUES (7, 1);
COMMIT;
```

**重要：** 上記は手順を説明する断片で、実際には更新件数の判定・例外処理・重複注文防止・制約・後続失敗時のROLLBACKが必要です。これらがないままコピーしても安全な在庫処理にはなりません。

- **Atomicity（原子性）**：まとめて成立／取り消し。
- **Consistency（一貫性）**：定義した制約を保つ。業務の意味まで自動保証するわけではない。
- **Isolation（隔離性）**：同時実行での見え方を規定する。設定・DBに依存。
- **Durability（永続性）**：コミットした変更の保持。ハードウェアや設定、障害モデルに依存。

**紙上演習：** 在庫を1減らした直後に注文INSERTで失敗。トランザクションを使わない場合と使う場合は？

<details><summary>解答と解説</summary>使わないと在庫だけ減った不整合が残る可能性があります。トランザクション内で失敗時にROLLBACKすれば一連の変更を取り消せます。ただし外部メールの送信などは通常DBのROLLBACKで元に戻せません。</details>

**講師ナレーション：** 「ACIDは魔法の保証ではなく、適切なトランザクション境界とDBの設定で成立する性質です。」

---

## DB-09｜同時更新・ロストアップデート・ロックを図で追う

```text
在庫 quantity = 1
時刻   担当A                  担当B
 t1    SELECT → 1
 t2                           SELECT → 1
 t3    アプリ計算 → 0
 t4                           アプリ計算 → 0
 t5    UPDATE quantity=0
 t6                           UPDATE quantity=0
結果   2回売ったのに0（競合が隠れた）
```

これは**読み取り→アプリ計算→書き戻し**で起きる代表例です。`UPDATE stock SET quantity=quantity-1 WHERE ... AND quantity>=1` のように条件付きの単一更新に寄せ、更新行数を判定する、あるいはDBに応じて行ロック・バージョン列による楽観ロックを検討します。

```sql
-- 楽観ロックの設計例（製品やDBの実装に応じて調整）
UPDATE profile
SET display_name = :name, version = version + 1
WHERE id = :id AND version = :expected_version;
-- 影響行数0なら競合。再取得・再試行や利用者への通知が必要
```

**トランザクションがあるだけで自動的に全競合が解消するわけではありません。** 隔離レベルやSQLの書き方を含めて設計します。

**紙上演習：** `WHERE version = ...` を入れると、2件目の更新はどうなる？

<details><summary>解答と解説</summary>先に成功した更新がversionを増やすため、古いversionを前提とする後続更新は通常0行になり、競合を検出できます。アプリは0行を「成功」と誤認してはいけません。</details>

**講師ナレーション：** 「二人が正しい操作をしても、同時に行うと間違った結果になり得ます。競合を『起こさない』だけでなく『検出する』設計が必要です。」

---

## DB-10｜隔離レベル・MVCC・ファントムリード

| 現象 | 例 | 説明 |
|---|---|---|
| ダーティリード | Aが未コミットの値をBが読む | 取り消されるかもしれない値が見える |
| ノンリピータブルリード | 同じ行を再読すると値が変わる | 別トランザクションのコミットが影響 |
| ファントム | 同じ条件で検索すると行数が増減 | 条件を満たす行の追加・削除が影響 |
| 直列化異常 | 取引全体の組み合わせに矛盾 | 個々のSQLは正しくても全体は危険 |

**MVCC（Multi-Version Concurrency Control）**：行の複数のバージョンを扱い、読み書きの衝突を減らす仕組み。『MVCCならロック不要』は誤解です。更新時の衝突や制約、直列化には別の制御が必要です。

製品ごとの差：PostgreSQLは通常 `READ COMMITTED` が既定、MySQL InnoDBは通常 `REPEATABLE READ` が既定。SQLiteは独自の並行性・スナップショットモデルです。同じ隔離レベル名でも挙動の詳細が異なります。[D2][D3]

**紙上演習：** 直列化（SERIALIZABLE）に設定すればアプリの再試行は不要？

<details><summary>解答と解説</summary>不要にはなりません。直列化違反によってトランザクションが中断され得るため、再試行可能な業務処理にすることが重要です。外部副作用を重複させない設計も必要です。</details>

**講師ナレーション：** 「トランザクション同士がお互いの変更をどう見るか。そこに性能と正しさのトレードオフがあります。」

---

## DB-11｜インデックスの正体：検索を速くする代償

インデックスは本の索引に似ています。インデックスがあれば必ず速いわけではなく、対象件数・選択度・統計・更新頻度によります。作成すると更新・削除・挿入で索引の維持が必要です。

```sql
CREATE INDEX idx_orders_customer_status
ON orders(customer_id, status);
```

**複合インデックス**では先頭列からの利用が重要になる場合が多く、`WHERE customer_id=? AND status=?` のようなクエリに適する可能性があります。ただしDBMS・統計・実行計画に依存するため無条件の断言は避けましょう。

**読解例**

```text
Index Scan / Index Seek ：索引を使って候補を絞る
Seq Scan / Table Scan  ：表を走査する
Nested Loop            ：外側の行ごとに内側を探す
Hash Join              ：ハッシュ表で結合する（対応DBで）
```

**紙上演習：** テーブル3行のサンプルでテーブルスキャンになるのはDBの故障？

<details><summary>解答と解説</summary>故障ではありません。少数行なら全走査の方が低コストと推定される場合があります。データ量・分布・クエリに基づいて評価します。</details>

**講師ナレーション：** 「速さは索引の本数で決まりません。実行計画を読んで、なぜその方法を選んだかを考えます。」

---

## DB-12｜EXPLAIN・統計・遅いSQLの原因調査

```sql
-- PostgreSQLにおける実行計画の読解例（説明用）
EXPLAIN SELECT * FROM orders WHERE customer_id = 1;
```

- **推定コスト**：所要時間のミリ秒と同義ではありません。
- **rows**：予測した行数。実際の行数と差が大きければ統計や条件を検討。
- **ANALYZE**：実際に実行して計測する機能。UPDATE/DELETEなどでは**データを変更し得る**ため、本書では実行しません。
- **最適化の順序**：目的とSQLの正しさ→絞り込み→インデックス→統計→必要なら設計変更。やみくもな索引追加は逆効果です。[D4]

**紙上演習：** `EXPLAIN ANALYZE DELETE FROM ...` を読み取りだけの安全な操作として扱える？

<details><summary>解答と解説</summary>扱えません。PostgreSQLで `EXPLAIN ANALYZE` は対象ステートメントを実行します。変更系では副作用があるため実DBでの扱いは慎重にします。</details>

**講師ナレーション：** 「EXPLAINを知るとSQLの裏側が見えてきます。ただし、説明する機能と実際に処理する機能を混同しないでください。」

---

## DB-13｜PHPからDBを扱う：PDOと型・例外

**説明用の安全側断片：** 接続や認証情報は省略。ここではクエリの構造と値の分離だけに注目します。

```php
<?php
// $pdo は事前に安全に初期化されている想定
$sql = 'SELECT id, total_yen FROM orders WHERE customer_id = :customer_id';
$stmt = $pdo->prepare($sql);
$stmt->bindValue(':customer_id', $authorizedCustomerId, PDO::PARAM_INT);
$stmt->execute();
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
// 次に表示する際はHTML文脈に応じて出力エスケープを行う
```

| 行 | 読み解き |
|---|---|
| `$sql` | SQL構造は固定し、動的な値は`:customer_id`に渡す |
| `prepare` | SQLの構造と値を分離する準備。DB/PDO設定によりネイティブ/エミュレート差がある |
| `bindValue` | 型を明示して値を渡す。ユーザー入力そのままではなく**認可されたID**を使う |
| `execute` | SQLを実行する段階。例外処理・タイムアウト等は省略 |
| `fetchAll` | 結果を配列にする。大量件数はメモリ使用を考える |

**重要：** パラメータ化はSQLインジェクション対策であり、行の持ち主チェック（IDOR対策）でもXSS対策でもありません。**PDOを使っただけで堅牢**とは言えません。[D5]

**紙上演習：** `$authorizedCustomerId` をリクエストの `customer_id` に置き換えるだけで何のリスクが残る？

<details><summary>解答と解説</summary>他人のIDを指定できると権限外参照が起こり得ます（IDOR/BOLA）。パラメータ化でSQLiを防いでも、対象レコードの認可は別途必要です。</details>

**講師ナレーション：** 「SQLの安全性と、誰がどのデータを読む権利を持つかは別問題です。」

---

## DB-14｜SQLインジェクション：命令とデータの境界

### 反例（レビュー用・実行しない）

```php
<?php
// NG：値とSQL命令を文字列で結合する
$sql = "SELECT id FROM customers WHERE name = '" . $name . "'";
```

ユーザーに変更できる `$name` が、SQLリテラルを組み立てる操作に混ざります。任意の入力によって**コードとして解釈される領域**に入り込む設計が根本原因です。特定の攻撃文字列を試さなくても危険性を説明できます。

### 改善例（説明用断片）

```php
<?php
$sql = 'SELECT id FROM customers WHERE name = :name';
$stmt = $pdo->prepare($sql);
$stmt->execute([':name' => $name]);
```

**違い：** `'... :name'` はクエリ構造、`$name` はデータとして渡されます。なお、**テーブル名・列名・ORDER BYの方向**は一般にプレースホルダーで置換できないため、固定候補へのホワイトリストで扱います。エスケープのみを主たる防御策にしないこと。[D5]

**紙上演習：** `ORDER BY $_GET['sort']` を `:sort` にすれば並び替え列を動的に選べる？

<details><summary>解答と解説</summary>通常はできません。パラメータはSQLの「値」のためで、識別子やキーワードに置き換わるものではありません。`name` または `created_at` など許可した列名にサーバー側でマッピングします。</details>

**講師ナレーション：** 「インジェクション対策の核心は危険な文字を消すことではなく、SQLの命令部分と値部分を混ぜないことです。」

---

## DB-15｜DB製品ごとの違い：SQLite・MySQL・PostgreSQL・NoSQL

| 観点 | SQLite | MySQL（InnoDB） | PostgreSQL | ドキュメント型DB |
|---|---|---|---|---|
| 主な用途 | 組込み・ローカル・小規模サービス等 | 汎用Web・業務システム | 複雑なSQL・多機能な業務システム | 柔軟な文書構造・用途特化 |
| 接続 | 原則ライブラリでDBファイル操作 | サーバー型 | サーバー型 | 製品依存、多くはサーバー型 |
| 外部キー | PRAGMAで明示有効化が必要な構成 | InnoDBで利用可能 | 利用可能 | RDBの参照整合性と同等の機能とは限らない |
| 同時処理 | 書き込み競合モデルに留意 | MVCC/ロック | MVCC/ロック | 製品の整合性モデルに依存 |
| SQL方言 | SQLite方言 | MySQL方言 | PostgreSQL方言 | クエリAPI・言語が製品依存 |

**NoSQLは『セキュリティが弱いDB』でも『SQLiが存在しないから安全なDB』でもありません。** ユーザー入力の型を信用せず、固定したクエリ構造で扱い、権限を絞る原則は共通です。

SQLiteのWAL（Write-Ahead Logging）は読み取りと書き込みの並行性に利点がありますが、書き込みの同時性・チェックポイント・運用上の制限を理解する必要があります。製品の仕様書を優先してください。[D1][D2][D3]

**紙上演習：** PHPからMySQLに変更したら、SQLiteのSQL・テーブル定義が必ずそのまま使える？

<details><summary>解答と解説</summary>使えるとは限りません。採番・型・関数・DDL・UPSERT・隔離レベルなどに差があります。移行計画とテストが必要です。</details>

**講師ナレーション：** 「『SQL』は共通語ですが、方言や内部の動作まで完全に同一ではありません。」

---

## DB-16｜バックアップ・復元・移行の考え方

**バックアップがある＝復旧できる、ではありません。** 設計上の問いは次の4つです。

1. **RPO（Recovery Point Objective）**：何分前までのデータ喪失を許容できるか。
2. **RTO（Recovery Time Objective）**：何分で業務再開すべきか。
3. **整合したバックアップ**：更新途中やトランザクション、WAL・バイナリログも含めてどう一貫性を取るか。
4. **復元テスト**：秘密情報を保護した別環境で復元し、機能・制約・件数を確認したか。

**SQLiteの注意：** 稼働中のDBファイルを単にコピーしても一貫したバックアップを保証できません。SQLite公式のオンラインバックアップAPI等を参照します。[D6]

**マイグレーション**は変更履歴を明示し、既存データの移行、ロールバック可能性、サービス停止要否を事前確認します。列名を変えるだけでもアプリの旧バージョンとの互換性に影響します。

**紙上演習：** 1日1回のバックアップなら、最大どれほどのデータ損失があり得る？

<details><summary>解答と解説</summary>障害時刻によっては約1日分です。これは単純化した例で、追加のログ保存・スナップショット等があれば変わります。業務要件に合わせたRPO/RTOが必要です。</details>

**講師ナレーション：** 「バックアップの価値は作成した回数でなく、必要な時に整合して戻せるかで決まります。」

---

## DB-17｜最小権限、監査ログ、個人情報と暗号化

**最小権限**：WebアプリのDB接続アカウントに、スキーマ変更や全DB管理権限を日常的に与えない。読み取り専用APIと更新系APIは権限分割も検討します。SQLインジェクションが残っても被害を小さくする多層防御です。

**監査ログ**：誰が、いつ、どの操作・テーブル・レコード種別にアクセスしたかを追跡。原文SQL、パスワード、認証トークン、個人情報を無条件に保存すると、ログ自体が情報漏えい源となります。

**暗号化の区別**：TLS（通信中）、DB/ストレージ暗号化（保存中）、アプリによる特定列の暗号化（利用上の制約あり）を区別します。暗号化だけでは権限外参照やアプリ侵害を防げません。

**紙上演習：** Web APIが `SELECT` しかしないのにDB管理者権限で接続する設計の問題は？

<details><summary>解答と解説</summary>誤実装・権限乗っ取り・SQLiなどが起きたときに不必要に広い操作が可能になります。必要な表・操作へ権限を絞る設計が重要です。</details>

**講師ナレーション：** 「安全なSQLだけで守るのではなく、もし突破されたときの権限と記録を設計します。」

---

## DB-18｜総合設計レビュー：誰のどのデータをどこで守るか

架空の注文閲覧機能を対象に、以下を**実行せずにレビュー**します。

```text
利用者入力 customer_id
      ↓ ① 認証済みセッションか？
PHPアプリ ② この利用者がcustomer_idを閲覧できるか？
      ↓ ③ SQL構造と値が分離しているか？
DBMS     ④ 参照先・制約・トランザクションの範囲は適切か？
      ↓ ⑤ 個人情報を取得しすぎていないか？
PHP       ⑥ HTML表示時に文脈別エスケープしたか？
      ↓ ⑦ 操作証跡は残るが秘密は残さないか？
ブラウザ
```

**レビュー課題（ケーススタディ）**：注文履歴を表示するAPIが `customer_id` を自由に受け取る。SQLはプレースホルダーを使っている。注文の金額は `REAL` 型で管理し、更新時のトランザクションがない。閲覧ログにはセッションIDが書かれている。**4つ以上の改善点**を挙げ、各対策が防げないものも説明する。

<details><summary>模範解答と理由</summary>

1. `customer_id` とログイン利用者・権限の関係をサーバー側で照合：IDOR対策（SQLi対策とは別）。
2. 金額は業務に合う整数最小単位または正確なNUMERIC/DECIMAL等を検討：丸めの問題（型はDB製品に依存）。
3. 複数更新のトランザクション化・制約・競合検出：途中失敗と同時更新の問題。
4. セッションIDをログに書かない：ログ漏えいがセッション侵害に連鎖するリスク。
5. 出力時のエスケープ、最小取得列、最小DB権限、復元試験、監査手順を検討。

</details>

**講師ナレーション：** 「本当に強い設計は『セキュリティの関数を一つ呼ぶこと』ではありません。通信、認証、SQL、DB制約、ログと復元の境界をつなげて考えます。」

---

## 重要用語・早見表

| 用語 | ひとことで | よくある誤解 |
|---|---|---|
| RDBMS | 行・列・関係を管理するDBMS | Excelと同じ |
| 主キー | 行の一意な識別子 | 常に連番でなければならない |
| 外部キー | 表間の参照関係を強制 | アプリの認可も代行する |
| NULL | 値の不在・不明を示す | 0や空文字と同じ |
| JOIN | 条件に沿って行を組み合わせる | 単純に表を連結するだけ |
| トランザクション | 複数操作を一組で扱う単位 | 競合が全自動でなくなる |
| インデックス | 検索を補助するデータ構造 | 多いほど常に速い |
| MVCC | 同時アクセスのため複数版を管理 | ロックが不要になる |
| SQLi | データがSQL命令として混入する不具合 | 危険文字を消せば万全 |
| IDOR | オブジェクト単位の認可不足 | SQLのパラメータ化で防げる |
| RPO/RTO | 許容損失時点・復旧目標時間 | バックアップを取れば同じ |

## 根拠資料（一次資料・公式）

この本は説明の根拠となる**仕様と公式マニュアル**を示すものです。製品の版・導入形態が異なる場合は該当版の公式資料で再確認してください。

- **[D1] SQLite — Foreign Key Support**：https://www.sqlite.org/foreignkeys.html （第3章・第15章）
- **[D2] SQLite — Transactions**：https://www.sqlite.org/lang_transaction.html （第8〜10章）
- **[D3] MySQL 8.4 — InnoDB Transaction Model**：https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html （第10章・第15章）
- **[D4] PostgreSQL — Using EXPLAIN**：https://www.postgresql.org/docs/current/using-explain.html （第11〜12章）
- **[D5] OWASP — SQL Injection Prevention Cheat Sheet**：https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html （第13〜14章）
- **[D6] SQLite — Online Backup API**：https://www.sqlite.org/backup.html （第16章）
- **[D7] SQLite — PRAGMA statements**：https://www.sqlite.org/pragma.html （第3章）
- **[D8] PostgreSQL — Transaction Isolation**：https://www.postgresql.org/docs/current/transaction-iso.html （第10章）
- **[D9] SQLite — Write-Ahead Logging**：https://www.sqlite.org/wal.html （第15〜16章）
- **[D10] MySQL 8.4 — Server Options**：https://dev.mysql.com/doc/refman/8.4/en/server-options.html （第10章）

### 発展的な読み方

この本のSQLコードは**SQLの挙動を考えるための静的な断片**です。DBエンジン・インデックス・設定・データ量によって性能と分離性は変わります。「正確な結果」「計測で得た結果」「推奨設計」を区別してレビューすると、実務でも通用する読み方になります。
