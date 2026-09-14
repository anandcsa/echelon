import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.REVIEW_URL||'http://127.0.0.1:5193';
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:960,height:600}}),errors=[],assets=new Map();page.setDefaultTimeout(180000);
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/assets/neon/'))assets.set(new URL(r.url()).pathname,r.status());});
 await page.addInitScript(()=>localStorage.setItem('echelon-controls-v2',JSON.stringify({profile:'remote'})));
 await page.goto(base+'?quality=balanced',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.echelon?.getState().ready||document.querySelector('#loading.failed'));
 assert.ok(await page.evaluate(()=>window.echelon?.getState().ready),'World ready');
 await page.locator('#start').click();await page.keyboard.press('e');await page.waitForFunction(()=>window.echelon.getState().vehicles.driving);
 const before=await page.evaluate(()=>window.echelon.getState().position[2]);await page.keyboard.down('w');
 await page.waitForFunction(z=>window.echelon.getState().position[2]>z+2,before,{timeout:45000});await page.keyboard.up('w');await page.keyboard.down('Space');
 await page.waitForFunction(()=>window.echelon.getState().vehicles.speed<3,null,{timeout:45000});await page.keyboard.up('Space');
 await page.screenshot({path:'neon-live-driving.png',timeout:120000});await page.keyboard.press('e');await page.waitForFunction(()=>!window.echelon.getState().vehicles.driving);
 const s=await page.evaluate(()=>window.echelon.getState());assert.equal(s.version,8);assert.equal(s.assetEdition,'neon-city-2026-09');assert.equal(s.cityBuildings,83);assert.ok(s.audio.musicPlaying);assert.ok(assets.size>=30);assert.ok([...assets.values()].every(x=>x===200));assert.deepEqual(errors,[]);
 const report={base,version:s.version,edition:s.assetEdition,cityBuildings:s.cityBuildings,triangles:s.triangles,drawCalls:s.drawCalls,drivingBrakeExit:true,audio:s.audio,assets:[...assets],errors};await writeFile('neon-live-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
