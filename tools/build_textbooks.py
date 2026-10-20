#!/usr/bin/env python3
"""Convert authored Markdown textbooks into dependency-free read-only HTML pages.
Does not execute any PHP/SQL/code examples. Requires mistune 3.x only for generation.
The generated HTML itself has no dependency on Python, PHP, databases or CDNs.
"""
from pathlib import Path
from html import escape, unescape
import re
import mistune

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs'
OUTPUT.mkdir(exist_ok=True)
MD = mistune.create_markdown(escape=False, plugins=['table','strikethrough'])
books = [
    ('01-database-textbook.md', 'database-book.html', 'DATABASE REFERENCE', 'データベース完全読本', '全18講義｜テーブル・SQL・JOIN・正規化・トランザクション・隔離・索引・SQLi・運用'),
    ('02-cookie-session-textbook.md', 'cookie-book.html', 'COOKIE & SESSION REFERENCE', 'Cookie・セッション完全読本', '全20講義｜Cookie属性・HTTP・PHPセッション・乗っ取り・MFA・監視・DBSC'),
    ('03-database-cookie-integration.md', 'integration-book.html', 'INTEGRATED DESIGN REVIEW', 'Cookie×DB 総合コードレビュー', '注文閲覧APIを題材にした認証・認可・DBの統合設計'),
]
css = r'''
:root{color-scheme:dark;--bg:#0b101b;--panel:#121b2c;--edge:#2a374e;--ink:#eff3fa;--muted:#b5c3d8;--accent:#81d9cc;--link:#a1bdff}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,system-ui,sans-serif;font-size:16px;line-height:1.92}
a{color:var(--link)}a:hover{color:#d3dfff}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--accent);outline-offset:4px}
.top{position:sticky;top:0;z-index:6;background:#0c1420f5;border-bottom:1px solid var(--edge);display:flex;gap:16px;align-items:center;justify-content:space-between;padding:13px 22px;flex-wrap:wrap}.brand{font-weight:800;letter-spacing:.08em;font-size:14px;color:var(--accent)}.toplinks{display:flex;flex-wrap:wrap;gap:12px;font-size:13px}
.layout{display:grid;grid-template-columns:minmax(235px,290px) minmax(0,1fr);max-width:1600px;margin:0 auto}.sidebar{position:sticky;top:57px;align-self:start;height:calc(100vh - 57px);overflow-y:auto;padding:24px 15px 24px 22px;border-right:1px solid var(--edge)}.eyebrow{letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-size:11px;font-weight:700}.sidebar h2{font-size:20px;margin:6px 0}.search{width:100%;border:1px solid #52617a;border-radius:9px;background:#1a2537;color:white;padding:11px;font-size:14px;margin:12px 0}.toc a{display:block;text-decoration:none;padding:10px 9px;border-radius:7px;font-size:13px;line-height:1.5;color:#dce6f3}.toc a:hover,.toc a.active{background:#1b2b3d;color:var(--accent)}.hint{font-size:12px;color:var(--muted);border-top:1px solid var(--edge);padding-top:16px}
main{min-width:0;max-width:1000px;padding:32px clamp(18px,4vw,65px) 90px}.intro{background:linear-gradient(145deg,#172b40,#131f30);border:1px solid #36536b;border-radius:15px;padding:24px 30px;margin-bottom:30px}.intro h1{font-size:clamp(24px,3vw,36px);line-height:1.4;margin:10px 0 18px}.intro p{color:var(--muted);margin:6px 0 0}
.chapter{padding:24px 0 34px;border-bottom:1px solid #39465d;scroll-margin-top:75px}.chapter h2{font-size:clamp(21px,2.3vw,27px);line-height:1.5;padding-bottom:14px;margin:0 0 20px;border-bottom:1px solid var(--edge)}h3{font-size:19px;color:#a6efe3;margin-top:28px}h4{font-size:17px;margin-top:20px}p,li{overflow-wrap:anywhere}ul,ol{padding-left:1.5em}strong{color:#fff}blockquote{border-left:4px solid var(--accent);padding:7px 18px;margin:20px 0;background:#19283a;color:#dde8f5}blockquote p{margin:7px 0}
pre{background:#070b13;border:1px solid #2a354b;border-radius:10px;padding:18px;overflow:auto;line-height:1.65;font-size:13px;color:#dfecff;white-space:pre}code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}p code,li code,td code{background:#243449;border-radius:4px;padding:2px 4px;font-size:.9em}
table{border-collapse:collapse;width:100%;display:block;overflow:auto;margin:20px 0;font-size:14px}th,td{border:1px solid #415067;padding:10px 12px;min-width:95px;text-align:left;vertical-align:top}th{background:#20334b;white-space:normal}tr:nth-child(even) td{background:#101c2a}
details{border:1px solid #3b5b63;background:#11282b;border-radius:9px;margin:15px 0 22px;padding:12px 16px}summary{cursor:pointer;color:#b0f2e8;font-weight:700}details[open] summary{padding-bottom:9px;margin-bottom:10px;border-bottom:1px solid #395964}
.controls{position:sticky;top:66px;z-index:5;display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:22px;padding:12px;background:#172334ea;border:1px solid var(--edge);border-radius:10px;backdrop-filter:blur(10px)}button{background:#1c3b49;color:#e8f8f4;border:1px solid #497b79;padding:8px 12px;border-radius:8px;cursor:pointer;font:inherit;font-size:12px}button:hover{background:#2d5c65}#voice-status{font-size:12px;color:var(--muted)}.small{font-size:12px;color:var(--muted)}footer{font-size:12px;color:#98acc4;margin-top:45px}.skip{position:absolute;left:-9999px;top:0}.skip:focus{left:16px;top:4px;z-index:99;background:#fff;color:#000}
@media(max-width:870px){.layout{display:block}.sidebar{position:relative;top:0;height:auto;border-right:0;border-bottom:1px solid var(--edge);padding:13px 18px}.toc{display:flex;gap:3px;overflow-x:auto;padding-bottom:3px}.toc a{flex:0 0 180px;min-width:180px}.hint{display:none}main{padding:18px 18px 65px}.controls{top:66px}.intro{padding:22px 18px}.chapter{scroll-margin-top:130px}}
@media print{body{color:#000;background:#fff}.top,.sidebar,.controls{display:none}.layout{display:block}main{max-width:100%;padding:0}.intro{background:none;border:0}a{color:#000}pre{white-space:pre-wrap;color:#000;background:#eee}details{break-inside:avoid}details:not([open]){display:none}}
'''

js = r'''
(() => {
'use strict';
const chapters = [...document.querySelectorAll('.chapter')];
const links = [...document.querySelectorAll('.toc a')];
const search = document.querySelector('#toc-filter');
const status = document.querySelector('#voice-status');
const play = document.querySelector('#voice-play');
const stop = document.querySelector('#voice-stop');
const voiceRate = document.querySelector('#voice-rate');
let activeId = chapters[0]?.id || '';
let paused = false;
let currentChunks = [], cursor = 0;
const clearVoice = () => { paused=true; currentChunks=[]; cursor=0; if ('speechSynthesis' in window) speechSynthesis.cancel(); status.textContent='読み上げ停止'; };
function speakChunk() {
 if(paused || cursor>=currentChunks.length){if (!paused) status.textContent='読み上げ終了'; return;}
 const str=currentChunks[cursor++];
 const utterance=new SpeechSynthesisUtterance(str);utterance.lang='ja-JP';utterance.rate=Number(voiceRate.value);
 const ja=speechSynthesis.getVoices().find(v=>v.lang.toLowerCase().startsWith('ja'));if(ja)utterance.voice=ja;
 utterance.onend=()=>{if(!paused)speakChunk()};utterance.onerror=()=>{status.textContent='読み上げが中断されました';};
 status.textContent=`読み上げ中 (${cursor}/${currentChunks.length})`;
 speechSynthesis.speak(utterance);
}
function readChapter() {
 if(!('speechSynthesis' in window)){status.textContent='このブラウザでは読み上げできません';return;}
 clearVoice();paused=false;
 const chapter=document.getElementById(activeId);if(!chapter)return;
 const text=[...chapter.querySelectorAll('h2,h3,p,li,th,td')]
 .filter(el=>!el.closest('details') || el.closest('details').open)
 .map(el=>el.textContent.trim()).filter(Boolean).join('。');
 currentChunks=(text.match(/.{1,280}(?:[。！？\n]|$)/g)||text.match(/.{1,280}/g)||[]).map(x=>x.trim()).filter(Boolean);
 if(!currentChunks.length){status.textContent='読み上げる文章がありません';return;}speakChunk();
}
function mark(id){activeId=id;for(const a of links){const selected=a.getAttribute('href')==='#'+id;a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');} }
links.forEach(a=>a.addEventListener('click',()=>{clearVoice();mark(a.hash.slice(1));}));
search.addEventListener('input',()=>{const q=search.value.toLocaleLowerCase();links.forEach(a=>{a.hidden=!a.textContent.toLocaleLowerCase().includes(q);});});
play.addEventListener('click',readChapter);stop.addEventListener('click',clearVoice);
const hash=location.hash.slice(1);if(document.getElementById(hash))mark(hash);else mark(activeId);
window.addEventListener('hashchange',()=>{if(document.getElementById(location.hash.slice(1)))mark(location.hash.slice(1));});
})();
'''
(OUTPUT / 'textbook.css').write_text(css, encoding='utf-8')
(OUTPUT / 'textbook.js').write_text(js, encoding='utf-8')

for name, outfile, serial, title, subtitle in books:
    md_text=(ROOT/'textbooks'/name).read_text(encoding='utf-8')
    if outfile=='integration-book.html':
        md_text=md_text.replace('(01-database-textbook.md)','(database-book.html)').replace('(02-cookie-session-textbook.md)','(cookie-book.html)')
    content=MD(md_text)
    chunks=re.split(r'(?=<h2>.*?</h2>)', content, flags=re.DOTALL)
    preamble=chunks.pop(0) if not chunks[0].startswith('<h2>') else ''
    navigation=[]; parts=[]
    for idx, ch in enumerate(chunks, start=1):
        if not ch.strip():continue
        head=re.search(r'<h2>(.*?)</h2>',ch,re.DOTALL)
        if not head:parts.append(ch);continue
        chaptext=unescape(re.sub(r'<[^>]+>', '', head.group(1))).strip()
        tag=re.match(r'\s*(?:DB|CK)-([0-9]{2})',chaptext)
        sect_id=('db-' if outfile.startswith('database') else 'ck-')+tag.group(1) if tag else f'appendix-{idx}'
        navigation.append((sect_id,chaptext))
        parts.append(f'<section class="chapter" id="{escape(sect_id)}">{ch}</section>')
    nav='\n'.join(f'<a href="#{escape(i)}">{escape(h)}</a>' for i,h in navigation)
    external_links=' '.join(f'<a href="{escape(other)}">{escape(short)}</a>' for other,short in [('index.html','全36章'),('database-book.html','DB読本'),('cookie-book.html','Cookie読本'),('integration-book.html','総合編')] if other!=outfile)
    page=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(subtitle)}。実行せずに読める日本語の技術参考書。"><title>{escape(title)} | Web Security Journey</title><link rel="stylesheet" href="textbook.css"></head>
<body><a href="#main" class="skip">本文へ移動</a><header class="top"><div class="brand">&lt;/&gt; WEB SECURITY JOURNEY — REFERENCE LIBRARY</div><nav class="toplinks" aria-label="ほかの教材">{external_links}</nav></header>
<div class="layout"><aside class="sidebar" aria-label="章ナビゲーション"><div class="eyebrow">{escape(serial)}</div><h2>{escape(title)}</h2><label for="toc-filter" class="small">目次を検索</label><input id="toc-filter" type="search" class="search" placeholder="キーワードで章を絞り込む"><nav class="toc">{nav}</nav><p class="hint">本文はすべて学習用の静的な文章とコードブロックです。PHPやSQLのサンプルは実行されません。音声読み上げはブラウザ端末内の機能です。</p></aside>
<main id="main"><div class="intro"><div class="eyebrow">{escape(serial)} · READ ONLY</div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div><div class="controls" aria-label="読み上げ操作"><button type="button" id="voice-play">▶ 選択中の章を読み上げ</button><button type="button" id="voice-stop">■ 停止</button><label class="small" for="voice-rate">速度</label><select id="voice-rate"><option value="0.85">ゆっくり</option><option value="1" selected>標準</option><option value="1.15">速め</option></select><span id="voice-status" role="status" aria-live="polite">左の目次で章を選んでください</span></div>
<div class="content">{preamble}{''.join(parts)}</div><footer>この教材は閲覧・思考・コードレビュー用です。反例を実サービスに使わないでください。仕様と製品実装の差は一次資料で確認してください。</footer></main></div><script src="textbook.js" defer></script></body></html>'''
    (OUTPUT/outfile).write_text(page,encoding='utf-8')
    print(outfile, 'chapters',sum(1 for i,_ in navigation if i.startswith(('db-','ck-'))), 'bytes',len(page.encode()),'sections',len(navigation))
