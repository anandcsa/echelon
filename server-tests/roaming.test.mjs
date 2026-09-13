import {test} from 'node:test';
import assert from 'node:assert/strict';
import {advanceVehicle} from '../vehicles.js';
import {inWorld,restoreRoam,completeRoam} from '../shared/roaming.js';
import {newCampaign} from '../campaign.js';
test('driving accelerates, reverses, brakes and does not tunnel through walls',()=>{let s={x:0,z:80,heading:0,speed:0};for(let i=0;i<40;i++)s=advanceVehicle(s,{throttle:1},.1,()=>true);assert(s.z>120);assert(s.speed<=27);const moving=s.speed;for(let i=0;i<10;i++)s=advanceVehicle(s,{brake:true},.1,()=>true);assert(s.speed<moving*.01);for(let i=0;i<20;i++)s=advanceVehicle(s,{throttle:-1},.1,()=>true);assert(s.speed<0);s=advanceVehicle({x:0,z:0,heading:0,speed:27},{throttle:1},.35,(x,z)=>z<2);assert(s.hit);assert(s.z<2);assert.equal(s.speed,0);});
test('expanded saves reject the empty outside rim and malformed positions',()=>{assert(inWorld(150,310));assert(inWorld(0,-120));assert(!inWorld(150,20));assert(!inWorld(0,430));assert(!inWorld('0',100));assert.equal(restoreRoam({vehicle:{x:'0',z:100,yaw:0}}).vehicle,null);assert.deepEqual(restoreRoam({vehicle:{x:150,z:310,yaw:1},waypoint:'archive'}).vehicle,{x:150,z:310,yaw:1});});
test('story jobs persist consequences, change trust and cannot pay twice',()=>{const c=newCampaign(),old=c.story.cast.rook.trust;assert(completeRoam(c,'courier','private'));assert.equal(c.salvage,3);assert.equal(c.story.cast.rook.trust,old+1);assert.equal(completeRoam(c,'courier','public'),false);assert.equal(completeRoam(c,'fake','private'),false);assert.equal(c.salvage,3);assert.equal(restoreRoam(c.roam).choices.courier,'private');assert(c.story.events.at(-1).includes('Juno'));});

test('right steering follows the chase camera orientation',()=>{const s=advanceVehicle({x:0,z:100,heading:0,speed:10},{steer:1},.1,()=>true);assert(s.heading<0);assert(s.x<0);});
