import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.REVIEW_URL||'http://127.0.0.1:5190';
const browser=await chromium.launch({channel:'chrome',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1100,height:720}}),errors=[],models=new Map(),reports=[];
 page.setDefaultTimeout(120000);
 page.on('pageerror',error=>errors.push(error.message));
 page.on('response',response=>{if(/\/bs-[^/]+\.glb/.test(response.url()))models.set(new URL(response.url()).pathname,response.status());});
 await page.addInitScript(()=>{localStorage.setItem('echelon-controls-v2',JSON.stringify({profile:'remote'}));localStorage.setItem('echelon-v2-save',JSON.stringify({position:[-148,1.85,175],health:100,campaign:{roam:{jobs:{blackout:'complete'}}}}));});
 await page.goto(base+'?quality=balanced');
 await page.waitForFunction(()=>window.echelon?.getState().ready||document.querySelector('#loading.failed'));
 assert.ok(await page.evaluate(()=>window.echelon.getState().ready),'World loaded without asset errors');
 await page.locator('#continue').click();await page.keyboard.press('e');
 await page.waitForFunction(()=>window.echelon.getState().vehicles.driving);
 for(const quality of ['balanced','high']){
  if(quality==='high'){await page.keyboard.press('Escape');await page.locator('#quality').selectOption('high');await page.locator('#resume').click();}
  await page.waitForTimeout(1500);
  await page.screenshot({path:`blendswap-${quality}-driving.png`,timeout:120000});
  const state=await page.evaluate(()=>window.echelon.getState());
  assert.equal(state.assetEdition,'blendswap-2026-09');assert.ok(state.vehicles.driving);assert.equal(state.quality,quality);
  reports.push({quality,triangles:state.triangles,drawCalls:state.drawCalls,softwareFPS:state.fps,audio:state.audio});
 }
 assert.equal(models.size,6);assert.ok([...models.values()].every(status=>status===200));assert.deepEqual(errors,[]);
 const report={base,models:[...models],reports,errors,note:'Software-rendered visual review; not a hardware frame-rate benchmark.'};
 await writeFile('blendswap-visual-review.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
