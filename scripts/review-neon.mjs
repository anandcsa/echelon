import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.REVIEW_URL||'http://127.0.0.1:5193';
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:1100,height:720}}),errors=[],assets=new Map();page.setDefaultTimeout(120000);
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/assets/neon/'))assets.set(new URL(r.url()).pathname,r.status());});
 await page.addInitScript(()=>localStorage.setItem('echelon-controls-v2',JSON.stringify({profile:'remote'})));
 await page.goto(base+'?quality='+ (process.env.REVIEW_QUALITY||'balanced'),{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.echelon?.getState().ready||document.querySelector('#loading.failed'));
 assert.ok(await page.evaluate(()=>window.echelon?.getState().ready),JSON.stringify(errors));
 await page.waitForTimeout(1200);await page.screenshot({path:'neon-title.png',timeout:120000});
 await page.locator('#start').click();await page.waitForTimeout(1500);await page.screenshot({path:'neon-street.png',timeout:120000});
 console.log(JSON.stringify({state:await page.evaluate(()=>window.echelon.getState()),errors,assets:[...assets]},null,2));
 await page.keyboard.press('e');await page.waitForFunction(()=>window.echelon.getState().vehicles.driving);
 await page.waitForTimeout(1000);await page.screenshot({path:'neon-driving.png',timeout:120000});
 assert.deepEqual(errors,[]);await fs.writeFile('neon-visual-review.json',JSON.stringify({assets:[...assets],errors,state:await page.evaluate(()=>window.echelon.getState())},null,2));
}finally{await browser.close();}
