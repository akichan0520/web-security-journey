# Contribution Guide

初心者に伝わる説明、技術的な正確さ、出典を重視します。問題箇所の原因と対策をセットで提案してください。

章データの正本は `curriculum.json`。以下のキーを維持してください：`unsafe_code`、`safe_code`、`line_notes`、`mental_trace`、`code_reason`、`narration`、`question`、`answer`。

```sh
python3 tools/build_reading.py
```

このコマンドはMarkdownと表示用JavaScriptの文字列データを生成するだけです。PHP・SQLの実行はありません。Issue / PRには学習対象と根拠（公式仕様・一次資料）を含めてください。コードを動かす操作手順は不要です。
