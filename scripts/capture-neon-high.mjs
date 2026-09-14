import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:800}});page.setDefaultTimeout(180000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.REVIEW_URL||'http://127.0.0.1:5193')+'?quality=high',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.echelon?.getState().ready);
 await page.screenshot({path:'neon-high-final.png',timeout:180000});const state=await page.evaluate(()=>window.echelon.getState());
 await writeFile('neon-high-verification.json',JSON.stringify({quality:state.quality,edition:state.assetEdition,triangles:state.triangles,drawCalls:state.drawCalls,errors},null,2));if(errors.length)throw Error(errors.join('\n'));
}finally{await browser.close();}
