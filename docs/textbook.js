
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
