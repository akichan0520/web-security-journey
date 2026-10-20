# 特別講義05：DB設計を基礎から運用まで読む

**深く学びたい方：** [データベース完全読本（18講義）](../textbooks/01-database-textbook.md)／[Web版](../docs/database-book.html) へ進んでください。


## テーブルの関係

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE notes (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES users(id),
  body TEXT NOT NULL
);
```

- **PRIMARY KEY：** 行を識別する。
- **FOREIGN KEY：** 関係を保つ。DB設定によっては外部キー機能の有効化が必要。
- **NOT NULL：** NULLを許可しない。
- **UNIQUE：** 同じ値の重複を制限する。
- **owner_id：** アプリの認可の判断材料になり得るが、外部キーだけでは認可されない。

## SELECT・JOIN・GROUP BY

```sql
SELECT u.name, COUNT(n.id) AS note_count
FROM users u
LEFT JOIN notes n ON n.owner_id = u.id
GROUP BY u.id, u.name;
```

**紙上の想定：** Aliceにメモ2件、Bobに0件あれば、LEFT JOIN + COUNT(n.id)でAlice=2、Bob=0を数えられます。COUNT(*)を使うとJOINの不一致行の扱いが違うため要注意。

## DB製品による考え方の違い

| 分類 | 得意分野 | 読む際の着眼点 |
|---|---|---|
| SQLite | 組み込み・単一ファイル | 外部キーの有効化、型、同時書込み |
| MySQL/MariaDB | サーバー型RDB | DBユーザー権限、トランザクションエンジン、文字セット |
| PostgreSQL | サーバー型RDB | データ型、JSONB、トランザクション分離、拡張性 |
| ドキュメント型NoSQL | 柔軟な文書データ | 入力型・検索オブジェクト、インデックス、整合性 |

## トランザクションは万能ではない

```sql
BEGIN;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
UPDATE accounts SET balance = balance + 10 WHERE id = 2;
COMMIT;
```

上記は構造を読むための例であり、そのまま送金システムに使えません。残高不足、二重実行、競合による更新ロスト、例外時のROLLBACK、監査や権限が別途必要です。

## インデックス・バックアップの考え方

1. 検索パターンからインデックスを選び、更新コストも考える。
2. 保存するデータの機密性と権限を設計する。
3. バックアップは暗号化・保管期間・復元検証までを1セットで考える。
4. DBの制約とアプリの権限チェックは役割が違うと理解する。

**一次資料：** [SQLite docs](https://www.sqlite.org/docs.html)、[PostgreSQL docs](https://www.postgresql.org/docs/)、[MySQL docs](https://dev.mysql.com/doc/)
