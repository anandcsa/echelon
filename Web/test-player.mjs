import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const browser=await chromium.launch({...(process.env.PLAYWRIGHT_CHANNEL?{channel:process.env.PLAYWRIGHT_CHANNEL}:{}),args:['--no-sandbox']});
try {
 const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://echelon.preview/**',r=>{const script=r.request().url().endsWith('player.js');return r.fulfill({contentType:script?'text/javascript':'text/html',body:fs.readFileSync(new URL(script?'player.js':'index.html',import.meta.url),'utf8')});});
 // Intercept every provider request. Tests never create a paid/native stream.
 await page.route('https://share.streampixel.io/**',r=>r.fulfill({contentType:'text/html',body:`<html><body>Mock stream<script>window.received=[];addEventListener('message',e=>received.push(e.data));parent.postMessage({type:'stream-state',value:'loadingComplete'},'http://echelon.preview');</script></body></html>`}));
 await page.goto('http://echelon.preview/');await page.locator('#start').tap();await page.waitForFunction(()=>document.getElementById('status').textContent==='LIVE');
 const frame=page.frames().find(f=>f.url().startsWith('https://share.streampixel.io'));
 await page.locator('#question').fill('What happened to Iona?');await page.locator('#talk button').tap();await frame.waitForFunction(()=>received.some(x=>x.type==='echelon.talk'&&x.message.includes('Iona')));
 await page.evaluate(()=>dispatchEvent(new MessageEvent('message',{origin:'https://share.streampixel.io',source:window,data:{kind:'dialogue',text:'FORGED'}})));assert.equal(await page.locator('#reply').textContent(),'');
 await frame.evaluate(()=>parent.postMessage(JSON.stringify({kind:'dialogue',text:'Mara: I signed the override.'}),'http://echelon.preview'));await page.waitForFunction(()=>document.getElementById('reply').textContent.includes('override'));
 const client=await context.newCDPSession(page),r=await page.locator('#move').boundingBox(),p={x:r.x+r.width/2,y:r.y+r.height/2,id:1};
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[p]});await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{...p,y:p.y-30}]});await frame.waitForFunction(()=>received.some(x=>x.type==='echelon.input'&&x.forward>.5));await client.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});await frame.waitForFunction(()=>received.filter(x=>x.type==='echelon.input').at(-1)?.forward===0);
 await page.locator('#input-mode').tap();assert.equal(await page.locator('body').evaluate(el=>el.classList.contains('touch')),false);
 await page.locator('#stop').tap();assert.equal(page.frames().length,1);assert.deepEqual(errors,[]);
 console.log('Player checks passed: states, typed chat, origin/source filtering, touch move/cancel, manual touch toggle, disconnect. Provider stream mocked.');
} finally {await browser.close();}
