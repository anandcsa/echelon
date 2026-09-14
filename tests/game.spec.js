import {test,expect} from '@playwright/test';
const state=p=>p.evaluate(()=>window.echelon.getState());
async function open(page,save){if(save)await page.addInitScript(s=>localStorage.setItem('echelon-v2-save',JSON.stringify(s)),save);await page.goto('/?quality=balanced');await page.waitForFunction(()=>window.echelon?.getState().ready,null,{timeout:90000});}
test('world assets load, exposure works, movement, shooting, recharge and EMP respond',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await open(page);expect((await state(page)).version).toBe(8);await page.locator('#brightness').fill('1.3');await expect(page.locator('#brightness-value')).toHaveText('130%');await page.locator('#start').click();await expect(page.locator('#hud')).toBeVisible();const before=(await state(page)).position;await page.keyboard.down('w');await expect.poll(async()=>(await state(page)).position[2],{timeout:15000}).toBeLessThan(before[2]-.2);await page.keyboard.up('w');await page.mouse.click(450,300);await expect.poll(async()=>(await state(page)).ammo,{timeout:10000}).toBeLessThan(18);await page.keyboard.press('r');await expect.poll(async()=>(await state(page)).ammo,{timeout:20000}).toBe(18);await page.keyboard.press('q');await expect.poll(async()=>(await state(page)).emp).toBeGreaterThan(0);await page.keyboard.press('Escape');await expect(page.locator('#resume')).toBeVisible();expect(errors).toEqual([]);
});
test('relay hacking completes and persists a checkpoint',async({page})=>{
 await open(page,{position:[-14,1.85,20.4],relays:[false,false,false],health:85});await page.locator('#continue').click();await expect(page.locator('#prompt')).toContainText('MARKET UPLINK');await page.keyboard.down('e');await expect(page.locator('#progress')).toHaveText('1 / 3 RELAYS OFFLINE',{timeout:30000});await page.keyboard.up('e');expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('echelon-v2-save')).relays[0])).toBe(true);expect((await state(page)).health).toBeGreaterThan(85);
});
test('completed checkpoints resume and extraction wins',async({page})=>{
 await open(page,{position:[0,1.85,-114],relays:[true,true,true],health:100});await page.locator('#continue').click();await expect(page.locator('#progress')).toHaveText('3 / 3 RELAYS OFFLINE');await page.keyboard.press('e');await expect(page.locator('#result')).toBeVisible();await expect(page.locator('#ending-title')).toContainText('UNTRACEABLE');expect(await page.evaluate(()=>localStorage.getItem('echelon-v2-save'))).toBeNull();
});
test('invalid saved positions are rejected and credits are accessible',async({page})=>{
 await open(page,{position:[9000,1.85,9000],relays:[false,false,false],health:100});await page.locator('#continue').click();expect((await state(page)).position[0]).toBeLessThan(70);const response=await page.request.get('/credits.html');expect(response.ok()).toBe(true);expect(await response.text()).toContain('CC0');
});
test('sentry fire causes damage and aimed disruptor fire disables a drone',async({page})=>{
 await open(page,{position:[-5,1.85,-7],relays:[false,false,false],health:100});await page.locator('#continue').click();await expect.poll(async()=>(await state(page)).health,{timeout:15000}).toBeLessThan(100);await page.keyboard.press('q');await page.evaluate(()=>{const s=window.echelon.getState(),a=s.position,b=s.droneStates[0].position,dx=b[0]-a[0],dz=b[2]-a[2],dy=b[1]-a[1];const yaw=Math.atan2(-dx,-dz),pitch=Math.atan2(dy,Math.hypot(dx,dz));const scale=.0017*s.controlSettings.mouse,mx=(s.yaw-yaw)/scale,my=(s.pitch-pitch)/scale,steps=Math.ceil(Math.max(Math.abs(mx),Math.abs(my))/150)||1;for(let i=0;i<steps;i++)window.dispatchEvent(new MouseEvent('mousemove',{movementX:mx/steps,movementY:my/steps}));});
 await page.mouse.down();await expect.poll(async()=>(await state(page)).kills,{timeout:15000}).toBeGreaterThan(0);await page.mouse.up();expect((await state(page)).droneStates[0].hp).toBe(0);expect((await state(page)).ammo).toBeLessThan(18);
});

test('ambient music starts after entry, advances, responds to volume and mute',async({page})=>{
 await open(page);expect((await state(page)).audio.musicPlaying).toBe(false);
 await page.locator('#music-volume').fill('0.12');await expect(page.locator('#music-value')).toHaveText('12%');
 await page.locator('#start').click();await expect.poll(async()=>(await state(page)).audio.musicTime,{timeout:20000}).toBeGreaterThan(.3);
 expect((await state(page)).audio.musicVolume).toBe(.12);
 await page.keyboard.press('Escape');await page.locator('#sound').click();expect((await state(page)).audio.musicPlaying).toBe(false);
 await page.locator('#sound').click();await expect.poll(async()=>(await state(page)).audio.musicPlaying).toBe(true);
});
