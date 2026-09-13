import {chromium} from '@playwright/test';
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try {
 const page=await browser.newPage({viewport:{width:1100,height:760}});page.setDefaultTimeout(90000);const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGE ERROR',e.message)});page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))console.log('HTTP ERROR',r.status(),r.url())});
 await page.goto(process.env.REVIEW_URL||'http://127.0.0.1:5189?quality=balanced',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.echelon?.getState().ready,null,{timeout:120000});await page.waitForTimeout(1000);await page.screenshot({path:'review-v3-title.png',timeout:120000});console.log('TITLE',await page.evaluate(()=>window.echelon.getState()));await page.locator('#start').click();await page.waitForTimeout(800);await page.screenshot({path:'review-v3-gameplay.png',timeout:120000});console.log('GAME',await page.evaluate(()=>window.echelon.getState()));console.log('ERRORS',errors);
} finally {await browser.close();}
