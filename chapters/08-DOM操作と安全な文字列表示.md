# 第08章：DOM操作と安全な文字列表示

> **読解教材（実行不要）** — 以下のコードは比較のための断片です。危険版を実行・公開しないでください。

**難易度：** 基礎

## この章でできるようになる
querySelector、createElement、textContent、innerHTMLの違いを説明できる。

## 全体像
DOMは画面上の要素のオブジェクト表現。文字列をHTMLとして解釈するか否かがXSSの鍵。

## 🎙 読み上げ可能な講師ナレーション
ユーザーが入力した文字を表示するとき、textContentは文字列として扱います。一方innerHTMLはHTMLを組み立てます。見た目が似ていても、危険性は大きく違います。今回は「HTMLのタグを書いてもタグにならない」という動作を確認します。

## 1. 危険なコードを読む
未信頼の値がどこから来て、どの命令や判断へ渡るかに注目してください。

```javascript
const value = location.search.slice(1);
document.querySelector('#result').innerHTML = value;
```

## 2. 安全側のコードと比較する
これは設計上の考え方を伝える**抜粋**です。例外処理や周辺設定が省略されている場合があります。

```javascript
const value = new URLSearchParams(location.search).get('q') ?? '';
document.querySelector('#result').textContent = value;
```

## 3. 一行ずつ意味を説明する
1. URLSearchParamsはURLクエリ文字列からqを取得する。
2. ?? は値がnull/undefinedなら空文字へ置き換える。
3. textContentはHTMLパーサへ入力文字列を渡さない。

## 4. 頭の中で処理の流れを追う
① URLクエリを取得→② 入力文字列を保持→③ textContentで文字として表示。

### 根本原因
HTMLパーサが入力内容をコードやDOM構造として解釈しうる。

### 修正の原理
innerHTMLは入力をHTMLとして解析する。textContentは文字列として扱う。文字列をHTML・属性・URL・JavaScriptのどこに入れるかで必要な対策が変わる。

### 防御を重ねるとしたら
プレーンテキストはtextContent。HTMLが必要なら信頼できるテンプレートや適切なサニタイズを使う。

## 5. 紙上ハンズオン（実行不要）
質問：HTMLを表示しないコメント欄に使うべきAPIは？ まず答えを見ずに、危険版のどの部分が原因となるか一行で説明してください。

**確認課題：**
安全側のコードを読んで、上の問題をどう防ぐか説明する。実行・HTTP要求・入力操作は不要。

<details><summary>解答・理由を開く</summary>

**答え：** textContentなど、文字列として扱うAPIです。

**着目点：** innerHTMLは入力をHTMLとして解析する。textContentは文字列として扱う。文字列をHTML・属性・URL・JavaScriptのどこに入れるかで必要な対策が変わる。

</details>

## 6. 関連資料
- [一次資料を読む](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [用語集](../guides/glossary.md)
- [36章索引](../README.md)

---

**注意：** 危険なコードは説明用の反例です。実行する必要はなく、完成品へ流用しないでください。安全版も教材用の部分コードであり、単独で本番運用できる保証はありません。
