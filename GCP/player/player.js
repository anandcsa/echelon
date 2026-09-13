import {Config, PixelStreaming} from '@epicgames-ps/lib-pixelstreamingfrontend-ue5.6';
const $=id=>document.getElementById(id);
let stream=null,config=null,ready=false,forward=0,right=0,brake=false,musicMuted=false;
const send=data=>{if(ready)stream?.emitUIInteraction(data);};
const input=()=>send({type:'echelon.input',forward,right,brake});
const neutral=()=>{forward=right=0;brake=false;input();};
function mode(on){document.body.classList.toggle('touch',on);$('input-mode').setAttribute('aria-pressed',String(on));neutral();}
$('input-mode').onclick=()=>mode(!document.body.classList.contains('touch'));
if(matchMedia('(pointer: coarse)').matches&&!matchMedia('(any-pointer: fine)').matches)mode(true);
function state(label,live=false){if(!live)neutral();ready=live;document.body.classList.toggle('playing',live);$('status').textContent=label;$('controls').classList.toggle('active',live);$('talk').hidden=!live;$('music').hidden=!live;}
$('start').onclick=()=>{
 $('welcome').hidden=true;$('stream').hidden=false;$('stop').hidden=false;state('CONNECTING');
 config=new Config({useUrlParams:false,initialSettings:{ss:(location.protocol==='https:'?'wss://':'ws://')+location.host,AutoConnect:false,AutoPlayVideo:true,StartVideoMuted:false,WaitForStreamer:true,HoveringMouse:true,TouchInput:false,KeyboardInput:true,MouseInput:true}});
 stream=new PixelStreaming(config,{videoElementParent:$('stream')});
 stream.addEventListener('webRtcConnected',()=>state('CONNECTED'));
 stream.addEventListener('playStream',()=>{state('LIVE',true);send({type:'echelon.music',muted:musicMuted});});
 stream.addEventListener('webRtcDisconnected',()=>state('DISCONNECTED'));
 stream.addEventListener('webRtcFailed',()=>state('CONNECTION FAILED'));
 stream.addEventListener('streamerListMessage',e=>{if(!e.data.messageStreamerList.ids?.length)state('WAITING FOR GAME');});
 stream.addEventListener('playStreamRejected',()=>{$('resume').hidden=false;state('PRESS PLAY AUDIO');});
 stream.addResponseEventListener('echelon',response=>{try{const d=JSON.parse(response);if(d.kind==='dialogue'&&typeof d.text==='string')$('reply').textContent=d.text.slice(0,500);}catch{}});
 stream.connect();
};
$('resume').onclick=()=>{stream?.play();$('resume').hidden=true;};
$('stop').onclick=()=>{neutral();stream?.disconnect();location.reload();};
// Avoid forwarding typed chat as movement keys to Unreal.
$('question').addEventListener('focus',()=>{neutral();config?.setFlagEnabled('KeyboardInput',false);});
$('question').addEventListener('blur',()=>config?.setFlagEnabled('KeyboardInput',true));
function hold(id,down,move,up){const el=$(id);let pointer=null;el.onpointerdown=e=>{if(!ready||pointer!==null)return;e.preventDefault();pointer=e.pointerId;el.setPointerCapture(pointer);down(e);};el.onpointermove=e=>{if(e.pointerId===pointer)move?.(e);};for(const name of ['pointerup','pointercancel','lostpointercapture'])el.addEventListener(name,e=>{if(e.pointerId!==pointer)return;pointer=null;up?.();});}
const move=e=>{const r=$('move').getBoundingClientRect();right=Math.max(-1,Math.min(1,(e.clientX-r.x-r.width/2)/(r.width*.35)));forward=Math.max(-1,Math.min(1,-(e.clientY-r.y-r.height/2)/(r.height*.35)));input();};
hold('move',move,move,()=>{forward=right=0;input();});let lookPoint=null;hold('look',e=>lookPoint=[e.clientX,e.clientY],e=>{send({type:'echelon.look',dx:e.clientX-lookPoint[0],dy:e.clientY-lookPoint[1]});lookPoint=[e.clientX,e.clientY];},()=>lookPoint=null);
hold('brake',()=>{brake=true;input();},null,()=>{brake=false;input();});$('interact').onclick=()=>{if(ready)send({type:'echelon.interact'});};
$('talk').onsubmit=e=>{e.preventDefault();const message=$('question').value.trim();if(!message||!ready)return;neutral();send({type:'echelon.talk',message:message.slice(0,400)});$('question').value='';$('stream').focus();};
setInterval(()=>{if(ready&&document.body.classList.contains('touch'))input();},100);
window.addEventListener('blur',neutral);document.addEventListener('visibilitychange',()=>{if(document.hidden)neutral();});

$('music').onclick=()=>{musicMuted=!musicMuted;$('music').setAttribute('aria-pressed',String(musicMuted));$('music').setAttribute('aria-label',musicMuted?'Enable background music':'Mute background music');$('music').textContent=musicMuted?'MUSIC OFF':'MUSIC';send({type:'echelon.music',muted:musicMuted});};
