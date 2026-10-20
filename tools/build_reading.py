from pathlib import Path
import json, re, html
ROOT=Path(__file__).resolve().parents[1]
J=json.loads((ROOT/'curriculum.json').read_text())
assert len(J)==36 and [x['id'] for x in J]==list(range(1,37))
for f in (ROOT/'chapters').glob('*.md'): f.unlink()
for l in J:
    t=l['title']
    suffix=re.sub(r'[^0-9A-Za-z一-龥ぁ-んァ-ンー]+','-',t).strip('-')
    name=f"{l['id']:02d}-{suffix}.md"
    code_lang='text' if l['id'] in [1,2,23,24,28,29,32,36] else ('html' if l['id'] in [3,4,5] else 'css' if l['id']==6 else 'javascript' if l['id'] in [7,8,9,27,33] else 'sql' if l['id'] in [12,13,25,26,30] else 'php')
    lines=[f'# 第{l["id"]:02d}章：{t}', '', '> **読解教材（実行不要）** — 以下のコードは比較のための断片です。危険版を実行・公開しないでください。','','**難易度：** '+l['level'],'','## この章でできるようになる',l['goals'],'','## 全体像',l['model'],'','## 🎙 読み上げ可能な講師ナレーション',l['narration'],'','## 1. 危険なコードを読む','未信頼の値がどこから来て、どの命令や判断へ渡るかに注目してください。','','```'+code_lang,l['unsafe_code'],'```','','## 2. 安全側のコードと比較する','これは設計上の考え方を伝える**抜粋**です。例外処理や周辺設定が省略されている場合があります。','','```'+code_lang,l['safe_code'],'```','','## 3. 一行ずつ意味を説明する']
    for idx,n in enumerate(l['line_notes'],1): lines += [f'{idx}. {n}']
    lines+=['','## 4. 頭の中で処理の流れを追う',l['mental_trace'],'','### 根本原因',l['why'],'','### 修正の原理',l['code_reason'],'','### 防御を重ねるとしたら',l['defense'],'','## 5. 紙上ハンズオン（実行不要）',l['thought_experiment'],'','**確認課題：**',l['verify'],'','<details><summary>解答・理由を開く</summary>','','**答え：** '+l['answer'],'','**着目点：** '+l['code_reason'],'','</details>','','## 6. 関連資料']
    if l['ref']: lines+=['- [一次資料を読む]('+l['ref']+')']
    if l['id'] in [11,16,17,18,31,32,33,34,35,36]:
        lines += ['- [特別講義06：Cookie窃取とセッションハイジャック（初級～上級）](../guides/deep-dive-06-cookie-session-hijacking.md)']
    lines+=['- [用語集](../guides/glossary.md)','- [36章索引](../README.md)','','---','','**注意：** '+l['reading_warning'],'']
    (ROOT/'chapters'/name).write_text('\n'.join(lines),encoding='utf-8')
(ROOT/'docs'/'lessons.js').write_text('/* 教材データのみ。サンプルコードは実行しません。 */\nwindow.COURSE_LESSONS = '+json.dumps(J,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('Generated',len(J),'lessons and',len(list((ROOT/'chapters').glob('*.md'))),'chapter files')
