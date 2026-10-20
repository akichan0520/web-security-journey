# 第09章：非同期処理・Promise・fetchとJSON

> **読解教材（実行不要）** — 以下のコードは比較のための断片です。危険版を実行・公開しないでください。

**難易度：** 基礎

## この章でできるようになる
await/async、HTTPステータス、JSON、例外処理、URLエンコードを理解する。

## 全体像
fetchはHTTPを送る道具。要求の成功とJSON解析の成功は別々の段階。

## 🎙 読み上げ可能な講師ナレーション
サーバーへの通信は時間がかかります。そのためasync/awaitで結果を待ちます。fetchは404や500でも通常はPromiseがrejectされないので、response.okの確認が必要です。通信エラー、認証エラー、入力エラーを分けて扱いましょう。

## 1. 危険なコードを読む
未信頼の値がどこから来て、どの命令や判断へ渡るかに注目してください。

```javascript
const data = await fetch('/api/items').then(r => r.json());
show(data); // 通信失敗でも成功扱いになる
```

## 2. 安全側のコードと比較する
これは設計上の考え方を伝える**抜粋**です。例外処理や周辺設定が省略されている場合があります。

```javascript
try {
  const response = await fetch('/api/items');
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  renderItems(data);
} catch (error) {
  showFriendlyError(); // 詳細は利用者に出さない
}
```

## 3. 一行ずつ意味を説明する
1. await fetch()でレスポンスを取得する。
2. response.okがfalseなら4xx/5xxを業務上の失敗として扱う。
3. response.json()は本文をJSONとして解析する。想定スキーマの検証も別に必要。

## 4. 頭の中で処理の流れを追う
① リクエスト→② HTTPステータスを判定→③ JSONを解析→④ 描画またはエラー処理。

### 根本原因
404や403のエラー本文まで成功データとして表示しうる。

### 修正の原理
fetchはHTTPの404/500で常に例外になるわけではない。Promiseの拒否とHTTPステータスエラーは分けて考える。

### 防御を重ねるとしたら
response.okを確認し、必要に応じて例外やユーザー向けメッセージを用意する。

## 5. 紙上ハンズオン（実行不要）
質問：fetchはHTTP 404で必ずrejectする？ まず答えを見ずに、危険版のどの部分が原因となるか一行で説明してください。

**確認課題：**
安全側のコードを読んで、上の問題をどう防ぐか説明する。実行・HTTP要求・入力操作は不要。

<details><summary>解答・理由を開く</summary>

**答え：** いいえ。HTTPエラーステータスでは通常rejectせず、res.okを見ます。

**着目点：** fetchはHTTPの404/500で常に例外になるわけではない。Promiseの拒否とHTTPステータスエラーは分けて考える。

</details>

## 6. 関連資料
- [用語集](../guides/glossary.md)
- [36章索引](../README.md)

---

**注意：** 危険なコードは説明用の反例です。実行する必要はなく、完成品へ流用しないでください。安全版も教材用の部分コードであり、単独で本番運用できる保証はありません。
