'use strict';
// 利用者データをHTMLとして挿入しない方針。読み上げは端末のWeb Speech APIを使用。
const lessons = window.COURSE_LESSONS || [];
const byId = (id) => document.getElementById(id);
let active = 0;
const KEY = 'web-security-journey-reading-progress-v2';
let completed = new Set();
try { completed = new Set(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch { completed = new Set(); }
function renderMenu(term='') {
  const list = byId('lesson-list'); list.replaceChildren(); let lastGroup='';
  const groups = ['入門','基礎','中級','セキュリティ','応用','総合'];
  for (const l of lessons) {
    if (!`${l.title} ${l.level} ${l.goals}`.toLowerCase().includes(term.toLowerCase())) continue;
    if (l.level !== lastGroup) {
      const label=document.createElement('div'); label.className='group-label'; label.textContent=l.level;
      list.append(label); lastGroup=l.level;
    }
    const button = document.createElement('button'); button.type='button';
    button.className='lesson-button' + (active===l.id-1?' active':'') + (completed.has(l.id)?' done':'');
    button.setAttribute('aria-current',active===l.id-1?'step':'false');
    const span=document.createElement('span'); span.className='index'; span.textContent=completed.has(l.id)?'✓':String(l.id).padStart(2,'0');
    const name=document.createElement('span'); name.textContent=l.title;
    button.append(span,name);button.addEventListener('click',()=>choose(l.id-1));list.append(button);
  }
}
function updateProgress() {
  byId('progress-label').textContent=`${completed.size} / ${lessons.length} 章`;
  byId('progress-fill').style.width=`${100*completed.size/Math.max(1,lessons.length)}%`;
}
function fill(id,value) { byId(id).textContent=value; }
function choose(index, scroll=true) {
  active=Math.max(0,Math.min(index,lessons.length-1)); const l=lessons[active];
  if (!l) return;
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  const fieldMap={'number':`LESSON ${String(l.id).padStart(2,'0')}`,'level':l.level,'title':l.title,'goals':l.goals,
    'model':l.model,'narration':l.narration,'practice':l.practice,'observe':l.observe,'risky':l.risky,
    'why':l.why,'defense':l.defense,'verify':l.verify,'code':l.safe_code,'unsafe-code':l.unsafe_code,'code-reason':l.code_reason,
    'mental-trace':l.mental_trace,'reading-warning':l.reading_warning,'thought':l.thought_experiment,
    'question':l.question,'answer':l.answer};
  for (const [key,val] of Object.entries(fieldMap)) fill('lesson-'+key,val);
  const items=byId('line-notes');items.replaceChildren(); for (const line of l.line_notes) { const li=document.createElement('li');li.textContent=line;items.append(li); }
  byId('lesson-answer').hidden=true;byId('answer-toggle').setAttribute('aria-expanded','false');byId('answer-toggle').textContent='答えを確認';
  const ref=byId('reference-box'); ref.hidden=!l.ref;
  if (l.ref) { const a=byId('lesson-ref'); a.href=l.ref; a.textContent=l.ref; }
  byId('copy-code').textContent='安全側をコピー';byId('copy-unsafe').textContent='反例をコピー';
  byId('complete').textContent=completed.has(l.id)?'✓ 完了済み（クリックで取消）':'✓ この章を完了';
  byId('next').disabled=active===lessons.length-1;
  renderMenu(byId('search').value);
  if (location.hash!==`#lesson-${l.id}`) history.replaceState(null,'',`#lesson-${l.id}`);
  if (scroll) document.querySelector('.lesson').scrollIntoView({behavior:'smooth',block:'start'});
}
byId('search').addEventListener('input',(e)=>renderMenu(e.target.value));
byId('answer-toggle').addEventListener('click',()=>{
  const el=byId('lesson-answer'); el.hidden=!el.hidden;
  byId('answer-toggle').setAttribute('aria-expanded', String(!el.hidden));
  byId('answer-toggle').textContent=el.hidden?'答えを確認':'答えを隠す';
});
byId('complete').addEventListener('click',()=>{
  const l=lessons[active]; completed.has(l.id)?completed.delete(l.id):completed.add(l.id);
  try { localStorage.setItem(KEY,JSON.stringify([...completed])); } catch { /* private mode */ }
  updateProgress();choose(active);
});
byId('next').addEventListener('click',()=>choose(active+1));
byId('copy-unsafe').addEventListener('click',async()=>{
  try { await navigator.clipboard.writeText(lessons[active].unsafe_code);byId('copy-unsafe').textContent='コピーしました'; }
  catch { byId('copy-unsafe').textContent='選択してコピーしてください'; }
});
byId('copy-code').addEventListener('click',async()=>{
  try { await navigator.clipboard.writeText(lessons[active].code); byId('copy-code').textContent='コピーしました'; }
  catch { byId('copy-code').textContent='選択してコピーしてください'; }
});
byId('rate').addEventListener('input',(event)=>{ byId('rate-value').textContent=Number(event.target.value).toFixed(1)+'倍'; });
byId('play').addEventListener('click',()=>{
  if (!('speechSynthesis' in window)) { byId('voice-info').textContent='このブラウザは音声読み上げを利用できません。台本を読んで進めてください。'; return; }
  speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(lessons[active].narration);
  u.lang='ja-JP'; u.rate=Number(byId('rate').value);
  const voices=speechSynthesis.getVoices();const ja=voices.find(v=>v.lang.toLowerCase().startsWith('ja'));
  if (ja) u.voice=ja;
  speechSynthesis.speak(u);
});
byId('stop').addEventListener('click',()=>{ if ('speechSynthesis' in window) speechSynthesis.cancel(); });
window.addEventListener('hashchange',()=>{ const n=Number((location.hash.match(/^#lesson-(\d+)$/)||[])[1]); if (n>0&&n<=lessons.length&&active!==n-1) choose(n-1); });
const start=Number((location.hash.match(/^#lesson-(\d+)$/)||[])[1]);
updateProgress();choose(start>0&&start<=lessons.length?start-1:0,false);
