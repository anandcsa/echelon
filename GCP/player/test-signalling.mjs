import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
const infra=process.env.EPIC_INFRA_PATH;
if(!infra)throw new Error('Set EPIC_INFRA_PATH to the built, pinned Epic infrastructure checkout.');
const dir=mkdtempSync(path.join(tmpdir(),'echelon-signal-test-'));
const port=18780;
writeFileSync(path.join(dir,'config.json'),JSON.stringify({player_port:port,streamer_port:18788,sfu_port:18789,serve:true,http_root:path.resolve(import.meta.dirname,'dist'),homepage:'index.html',log_folder:dir,log_level_console:'warning',log_config:false,https_redirect:false}));
const server=spawn(process.execPath,[path.resolve(infra,'SignallingWebServer/dist/index.js'),'--config_file',path.join(dir,'config.json')],{stdio:['ignore','pipe','pipe']});
let output='';server.stdout.on('data',s=>output+=s);server.stderr.on('data',s=>output+=s);
let browser;
try{
 let started=false;
 for(let i=0;i<100;i++){
  if(server.exitCode!==null)throw new Error(output);
  try{if((await fetch(`http://127.0.0.1:${port}`)).ok){started=true;break;}}catch{}
  await new Promise(r=>setTimeout(r,100));
 }
 assert.ok(started,'Epic signalling starts');
 browser=await chromium.launch({...(process.env.PLAYWRIGHT_CHANNEL?{channel:process.env.PLAYWRIGHT_CHANNEL}:{}),args:['--no-sandbox']});
 for(const mobile of [false,true]){
  const context=await browser.newContext({viewport:mobile?{width:390,height:844}:{width:1440,height:900},hasTouch:mobile,isMobile:mobile});
  const page=await context.newPage(),errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(!r.url().startsWith(`http://127.0.0.1:${port}`))external.push(r.url());});
  await page.goto(`http://127.0.0.1:${port}`);
  assert.equal(await page.locator('#input-mode').getAttribute('aria-pressed'),String(mobile));
  await page.locator('#start').click();
  await page.waitForFunction(()=>document.getElementById('status').textContent==='WAITING FOR GAME');
  assert.equal(await page.locator('iframe').count(),0);
  assert.equal(await page.locator('video').count(),1);
  assert.equal(await page.locator('#talk').isVisible(),false);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.locator('#stop').click();
  await page.locator('#start').waitFor({state:'visible'});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  await context.close();
 }
 console.log('Passed: real Epic signalling connection, honest no-game status, desktop/mobile mode, disconnect, no provider requests. No Unreal video tested.');
}finally{
 await browser?.close();server.kill('SIGTERM');
 await new Promise(resolve=>server.exitCode!==null?resolve():server.once('exit',resolve));
 rmSync(dir,{recursive:true,force:true});
}
