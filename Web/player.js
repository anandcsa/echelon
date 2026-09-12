'use strict';
const origin='https://share.streampixel.io',project='6aa5cbbe5c44891b8e2dcc3f',$=id=>document.getElementById(id);
let frame=null,ready=false,forward=0,right=0,brake=false;
const send=data=>{if(frame)frame.contentWindow.postMessage(data,origin);};
const input=()=>send({type:'echelon.input',forward,right,brake});
const neutral=()=>{forward=right=0;brake=false;input();};
const touch=()=>{document.body.classList.add('touch');$('input-mode').setAttribute('aria-pressed','true');};$('input-mode').onclick=()=>{const on=document.body.classList.toggle('touch');$('input-mode').setAttribute('aria-pressed',String(on));neutral();};
if(matchMedia('(pointer: coarse)').matches&&!matchMedia('(any-pointer: fine)').matches)touch();
window.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')touch();},{passive:true});
window.addEventListener('message',event=>{if(event.origin!==origin||event.source!==frame?.contentWindow)return;let data=event.data;if(typeof data==='string'){try{data=JSON.parse(data);}catch{return;}}if(!data||typeof data!=='object')return;if(data.type==='stream-state'){const labels={authenticating:'AUTHENTICATING',connecting:'FINDING SERVER',finalising:'STARTING',loadingComplete:'LIVE',reconnecting:'RECONNECTING',disconnected:'DISCONNECTED',restricted:'PROJECT UNAVAILABLE'};$('status').textContent=labels[data.value]||(String(data.value).startsWith('queue-')?'QUEUED':'CONNECTING');ready=data.value==='loadingComplete';$('controls').classList.toggle('active',ready);$('talk').hidden=!ready;if(!ready)neutral();}if(data.kind==='dialogue'&&typeof data.text==='string')$('reply').textContent=data.text.slice(0,500);});
$('start').onclick=()=>{$('welcome').hidden=true;$('stream').hidden=false;$('stop').hidden=false;$('status').textContent='CONNECTING';frame=document.createElement('iframe');frame.title='Echelon Unreal game';frame.allow='autoplay; fullscreen';frame.allowFullscreen=true;frame.src=origin+'/'+project;$('stream').append(frame);};
$('stop').onclick=()=>{neutral();send({message:'terminateSession'});frame?.remove();frame=null;ready=false;$('welcome').hidden=false;$('stream').hidden=true;$('stop').hidden=true;$('talk').hidden=true;$('controls').classList.remove('active');$('status').textContent='DISCONNECTED';};
function hold(id,down,move,up){const el=$(id);let pointer=null;el.onpointerdown=e=>{if(!ready||pointer!==null)return;e.preventDefault();pointer=e.pointerId;el.setPointerCapture(pointer);down(e);};el.onpointermove=e=>{if(e.pointerId===pointer)move?.(e);};for(const name of ['pointerup','pointercancel','lostpointercapture'])el.addEventListener(name,e=>{if(e.pointerId!==pointer)return;pointer=null;up?.();});}
const move=e=>{const r=$('move').getBoundingClientRect();right=Math.max(-1,Math.min(1,(e.clientX-r.x-r.width/2)/(r.width*.35)));forward=Math.max(-1,Math.min(1,-(e.clientY-r.y-r.height/2)/(r.height*.35)));input();};
hold('move',move,move,()=>{forward=right=0;input();});let lookPoint=null;hold('look',e=>lookPoint=[e.clientX,e.clientY],e=>{send({type:'echelon.look',dx:e.clientX-lookPoint[0],dy:e.clientY-lookPoint[1]});lookPoint=[e.clientX,e.clientY];},()=>lookPoint=null);
hold('brake',()=>{brake=true;input();},null,()=>{brake=false;input();});$('interact').onclick=()=>{if(ready)send({type:'echelon.interact'});};
$('talk').onsubmit=e=>{e.preventDefault();const message=$('question').value.trim();if(!message||!ready)return;neutral();send({type:'echelon.talk',message:message.slice(0,400)});$('question').value='';frame.focus();};
setInterval(()=>{if(ready&&document.body.classList.contains('touch'))input();},100);
window.addEventListener('blur',neutral);document.addEventListener('visibilitychange',()=>{if(document.hidden)neutral();});
