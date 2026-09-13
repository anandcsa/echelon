import {test,expect} from '@playwright/test';
test.use({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
const state=p=>p.evaluate(()=>window.echelon.getState());
async function load(page,save){if(save)await page.addInitScript(s=>localStorage.setItem('echelon-v2-save',JSON.stringify(s)),save);await page.goto('/');await page.waitForFunction(()=>window.echelon?.getState().ready,null,{timeout:90000});}
async function center(page,id){const r=await page.locator(id).boundingBox();return {x:r.x+r.width/2,y:r.y+r.height/2};}
test('portrait touch movement, simultaneous look/fire, release and pause',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await load(page);expect((await state(page)).touchMode).toBe(true);expect((await state(page)).quality).toBe('balanced');
 await page.screenshot({path:'mobile-portrait-menu.png'});await page.locator('#start').tap();await expect(page.locator('#touch-controls')).toBeVisible();expect(await page.evaluate(()=>!!document.pointerLockElement)).toBe(false);
 const client=await page.context().newCDPSession(page),m=await center(page,'#move-pad'),l=await center(page,'#look-pad'),f=await center(page,'#touch-fire');
 const send=(type,points)=>client.send('Input.dispatchTouchEvent',{type,touchPoints:points.map((p,i)=>({...p,id:i+1,radiusX:2,radiusY:2}))});
 const before=await state(page);await send('touchStart',[m]);await send('touchMove',[{x:m.x,y:m.y-35}]);await expect.poll(async()=>(await state(page)).position[2],{timeout:15000}).toBeLessThan(before.position[2]-.2);
 await send('touchStart',[{x:m.x,y:m.y-35},l]);await send('touchMove',[{x:m.x,y:m.y-35},{x:l.x+30,y:l.y}]);await expect.poll(async()=>(await state(page)).yaw).toBeLessThan(before.yaw-.05);
 await send('touchStart',[{x:m.x,y:m.y-35},{x:l.x+30,y:l.y},f]);await expect.poll(async()=>(await state(page)).ammo).toBeLessThan(18);await send('touchCancel',[]);
 const stopped=(await state(page)).position;await page.waitForTimeout(800);expect((await state(page)).position).toEqual(stopped);
 await page.locator('#touch-emp').tap();await expect.poll(async()=>(await state(page)).emp).toBeGreaterThan(0);await page.locator('#touch-reload').tap();await expect.poll(async()=>(await state(page)).ammo,{timeout:20000}).toBe(18);
 await page.screenshot({path:'mobile-portrait-game.png'});await page.locator('#pause-touch').tap();await expect(page.locator('#resume')).toBeVisible();await expect(page.locator('#touch-controls')).toBeHidden();await page.locator('#resume').tap();await expect(page.locator('#touch-controls')).toBeVisible();expect(errors).toEqual([]);
});
test('landscape touch hacking persists relay and controls fit screen',async({page})=>{
 await page.setViewportSize({width:844,height:390});await load(page,{position:[-14,1.85,20.4],relays:[false,false,false],health:85});await page.screenshot({path:'mobile-landscape-menu.png'});await page.locator('#continue').tap();
 const client=await page.context().newCDPSession(page),h=await center(page,'#touch-hack');await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...h,id:1}]});await expect.poll(async()=>(await state(page)).relays,{timeout:30000}).toBe(1);await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('echelon-v2-save')).relays[0])).toBe(true);
 for(const id of ['#move-pad','#touch-fire','#touch-hack','#touch-emp','#pause-touch']){const r=await page.locator(id).boundingBox();expect(r.x).toBeGreaterThanOrEqual(0);expect(r.y).toBeGreaterThanOrEqual(0);expect(r.x+r.width).toBeLessThanOrEqual(844);expect(r.y+r.height).toBeLessThanOrEqual(390);}
 await page.screenshot({path:'mobile-landscape-game.png'});await page.locator('#pause-touch').tap();await page.setViewportSize({width:390,height:844});await expect(page.locator('#resume')).toBeVisible();await page.locator('#resume').tap();await expect(page.locator('#touch-controls')).toBeVisible();
});
test('touch-only extraction finishes a completed checkpoint',async({page})=>{
 await load(page,{position:[0,1.85,-114],relays:[true,true,true],health:100});await page.locator('#continue').tap();await page.locator('#touch-hack').tap();await expect(page.locator('#result')).toBeVisible();await expect(page.locator('#touch-controls')).toBeHidden();await expect(page.locator('#ending-title')).toContainText('UNTRACEABLE');
});
