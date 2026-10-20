# 特別講義03：XSSを「HTMLパーサに渡すか」で理解する

> 危険な文字列はMarkdownの**コードブロックとして表示するだけ**で、ブラウザへHTMLとして挿入しません。

## 反射型・格納型・DOM型の見取り図

| 型 | データが来る場所 | どこで問題化するか |
|---|---|---|
| 反射型 | URLクエリなど | サーバーが直後の応答へ未処理で出力 |
| 格納型 | 投稿やコメントなど | 保存後、別の人の画面へ未処理で表示 |
| DOM型 | ブラウザ内のURLや入力 | JavaScriptが危険なDOM APIへ代入 |

## HTMLとして解釈する危険

```javascript
// 危険なDOM更新：入力値をHTMLとして扱う
result.innerHTML = userInput;
```

```javascript
// 文字表示が目的なら安全なAPIを使う
result.textContent = userInput;
```

入力文字列が次のようなタグ風の文字列だとします。

```text
<strong>お知らせ</strong>
```

- `innerHTML` は`strong`要素を生成し、太字で表示する。
- `textContent` はタグを**文字列として**表示する。
- 本当に危険な内容なら`innerHTML`経由でスクリプト実行につながるため、単なる装飾の違いではありません。

## PHPでHTML本文へ埋め込む場合

```php
// 危険：外部値をHTML本文へ直接渡す
echo '<p>' . $message . '</p>';

// 改善：HTML本文の文脈でエンコードする
echo '<p>' . htmlspecialchars($message, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
```

`htmlspecialchars` はHTML本文に適した方法の一つです。JavaScriptの文字列、CSS、URL、HTML属性の文脈で同じ処理を万能に流用しないでください。テンプレートの安全なエスケープ機能も選択肢です。

## CSPの役割

CSPは実行できるスクリプトの出所などを制限する**追加の防御層**です。CSPがあっても、未信頼値の直接出力を放置しないのが原則です。

## 問題

ユーザーのコメントをDBへ保存する前に`htmlspecialchars`する設計はいつも正しい？ → **いいえ。** 保存時に「データそのもの」を保持し、出力時に実際の表示文脈に応じて処理するのが一般的な設計です。

**一次資料：** [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)、[MDN DOM](https://developer.mozilla.org/ja/docs/Web/API/Document_Object_Model)
