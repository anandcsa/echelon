import {test,expect} from '@playwright/test';
test.use({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
test('mobile story choice and journal return to touch gameplay',async({page})=>{
 await page.addInitScript(()=>localStorage.setItem('echelon-v2-save',JSON.stringify({position:[-49,1.85,40],health:100,relays:[false,false,false],campaign:{version:1,signal:true}})));
 await page.goto('/');await page.waitForFunction(()=>window.echelon?.getState().ready,null,{timeout:90000});await page.locator('#continue').tap();await page.locator('#touch-hack').tap();await expect(page.locator('#story-dialog')).toBeVisible();
 await page.screenshot({path:'mobile-story-choice.png'});await page.getByRole('button',{name:/RESCUE IMANI/}).tap();await expect.poll(()=>page.evaluate(()=>window.echelon.getState().campaign.choice)).toBe('rescue');await expect(page.locator('#touch-controls')).toBeVisible();
 await page.getByRole('button',{name:'Mission journal',exact:true}).tap();await expect(page.locator('#story-dialog')).toBeVisible();await page.getByRole('button',{name:'BACK TO CITY',exact:true}).tap();await expect(page.locator('#touch-controls')).toBeVisible();
});
