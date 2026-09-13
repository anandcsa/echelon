import {chromium} from '@playwright/test';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const url=process.env.ECHELON_PREVIEW_URL;
const login=process.env.ECHELON_PREVIEW_LOGIN;
assert(url&&login,'Set ECHELON_PREVIEW_URL and ECHELON_PREVIEW_LOGIN (private file path)');
const text=fs.readFileSync(login,'utf8');
const username=text.match(/^Username: (.+)$/m)?.[1];
const password=text.match(/^Password: (.+)$/m)?.[1];
assert(username&&password,'Invalid login file');
const browser=await chromium.launch({channel:process.env.PLAYWRIGHT_CHANNEL||'chrome',headless:true,args:['--autoplay-policy=no-user-gesture-required']});
try{
 const touch=process.env.ECHELON_TOUCH==='1';
 const context=await browser.newContext({viewport:touch?{width:844,height:475}:{width:1440,height:900},hasTouch:touch,isMobile:touch,httpCredentials:{username,password,origin:new URL(url).origin}});
 await context.addInitScript(({relay})=>{window.__previewPeers=[];const Original=window.RTCPeerConnection;window.RTCPeerConnection=class extends Original{constructor(...args){if(relay)args[0]={...args[0],iceTransportPolicy:'relay'};super(...args);window.__previewPeers.push(this);}};},{relay:process.env.ECHELON_RELAY==='1'});
 const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url,{waitUntil:'networkidle'});
 await page.locator('#start').click();
 await page.waitForFunction(()=>{const v=document.querySelector('video');return v&&v.videoWidth>0&&v.readyState>=2&&v.currentTime>1;},{},{timeout:Number(process.env.ECHELON_STREAM_TIMEOUT_MS||120000)});
 const stats=async()=>page.evaluate(async()=>{
  const rows=[];for(const pc of window.__previewPeers){const report=await pc.getStats();for(const s of report.values())if(s.type==='inbound-rtp'&&s.kind==='video')rows.push({codec:report.get(s.codecId)?.mimeType,framesDecoded:s.framesDecoded,framesPerSecond:s.framesPerSecond,frameWidth:s.frameWidth,frameHeight:s.frameHeight,bytesReceived:s.bytesReceived,packetsLost:s.packetsLost});}return rows;
 });
 const before=await stats();assert(before.some(s=>s.framesDecoded>0),'No decoded WebRTC video');
 const shot=process.env.ECHELON_PREVIEW_SCREENSHOT||'../../Artifacts/unreal-live.png';
 await page.screenshot({path:shot});
 if(touch){
  if(process.env.ECHELON_ALREADY_DRIVING!=='1')await page.locator('#interact').click();await page.waitForTimeout(1000);
  const pad=await page.locator('#move').boundingBox();
  await page.mouse.move(pad.x+pad.width/2,pad.y+8);await page.mouse.down();await page.waitForTimeout(1200);await page.mouse.up();
  const brake=await page.locator('#brake').boundingBox();
  await page.mouse.move(brake.x+brake.width/2,brake.y+brake.height/2);await page.mouse.down();await page.waitForTimeout(1000);await page.mouse.up();
 }else{
  await page.locator('#stream').click({position:{x:720,y:380}});
  await page.keyboard.press('e');await page.waitForTimeout(1000);
  await page.keyboard.down('w');await page.waitForTimeout(1200);await page.keyboard.up('w');
  await page.keyboard.down('Space');await page.waitForTimeout(1000);await page.keyboard.up('Space');
 }
 await page.waitForTimeout(1000);
 const after=await stats();assert(after.some((s,i)=>s.framesDecoded>(before[i]?.framesDecoded||0)+5),'Stream did not continue decoding');
 await page.screenshot({path:shot.replace(/\.png$/,'-moved.png')});
 const audio=await page.evaluate(async()=>{const rows=[];for(const pc of window.__previewPeers)for(const s of (await pc.getStats()).values())if(s.type==='inbound-rtp'&&s.kind==='audio')rows.push({bytesReceived:s.bytesReceived,totalAudioEnergy:s.totalAudioEnergy});return rows;});
 const connections=await page.evaluate(async()=>{const rows=[];for(const pc of window.__previewPeers){const report=await pc.getStats();for(const s of report.values())if(s.type==='transport'&&s.selectedCandidatePairId){const pair=report.get(s.selectedCandidatePairId),local=report.get(pair.localCandidateId),remote=report.get(pair.remoteCandidateId);rows.push({local:local?.candidateType,remote:remote?.candidateType,protocol:local?.protocol});}}return rows;});
 if(process.env.ECHELON_RELAY==='1')assert(connections.some(s=>s.local==='relay'),'Forced relay test did not use a relay candidate');
 console.log(JSON.stringify({url,touch,relay:process.env.ECHELON_RELAY==='1',audio,connections,status:await page.locator('#status').innerText(),before,after,errors,screenshot:shot},null,2));
 assert.equal(errors.length,0,'Browser errors');
 if(touch)await page.locator('#interact').click();else await page.keyboard.press('e');
 await page.waitForTimeout(800);
 await page.screenshot({path:shot.replace(/\.png$/,'-exited.png')});
 await page.locator('#stop').click();
}finally{await browser.close();}
