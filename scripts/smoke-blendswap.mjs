import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.REVIEW_URL;
if(!base)throw new Error('Set REVIEW_URL to the deployed game URL.');
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:960,height:600}}),errors=[];
 page.setDefaultTimeout(120000);page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>localStorage.setItem('echelon-controls-v2',JSON.stringify({profile:'remote'})));
 await page.goto(base+'?quality=balanced');
 await page.waitForFunction(()=>window.echelon?.getState().ready||document.querySelector('#loading.failed'));
 assert.ok(await page.evaluate(()=>window.echelon.getState().ready));
 await page.locator('#start').click();await page.keyboard.press('e');
 await page.waitForFunction(()=>window.echelon.getState().vehicles.driving);
 const before=await page.evaluate(()=>window.echelon.getState().position[2]);
 await page.keyboard.down('w');
 await page.waitForFunction(z=>window.echelon.getState().position[2]>z+2,before,{timeout:30000});
 await page.keyboard.up('w');await page.keyboard.down('Space');
 await page.waitForFunction(()=>window.echelon.getState().vehicles.speed<3,null,{timeout:30000});
 await page.keyboard.up('Space');await page.screenshot({path:'blendswap-live-driving.png',timeout:120000});
 await page.keyboard.press('e');await page.waitForFunction(()=>!window.echelon.getState().vehicles.driving);
 const s=await page.evaluate(()=>window.echelon.getState());
 assert.equal(s.version,7);assert.equal(s.assetEdition,'blendswap-2026-09');assert.ok(s.audio.musicPlaying);assert.deepEqual(errors,[]);
 const report={base,version:s.version,assetEdition:s.assetEdition,ready:s.ready,drivingBrakeExit:true,music:s.audio,errors};
 await writeFile('blendswap-live-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
