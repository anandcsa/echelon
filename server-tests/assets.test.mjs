import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('../public/assets/',import.meta.url);
test('BlendSwap GLBs keep mobile download budgets and package their mesh buffers',()=>{
 const manifest=JSON.parse(readFileSync(new URL('blendswap-browser-manifest.json',root)));
 assert.equal(manifest.length,6);
 for(const asset of manifest){
  const file=readFileSync(new URL(asset.name+'.glb',root));
  assert.equal(file.toString('ascii',0,4),'glTF');
  assert.equal(file.readUInt32LE(4),2);
  assert.equal(file.readUInt32LE(8),file.length);
  assert.equal(file.length,asset.bytes);
  assert.ok(file.length<(asset.name.endsWith('-lod')?500000:2500000),asset.name+' download budget');
  const gltf=JSON.parse(file.toString('utf8',20,20+file.readUInt32LE(12)));
  assert.ok(gltf.buffers.every(buffer=>!buffer.uri),'Self-contained GLB buffers');
  assert.ok((gltf.images||[]).every(image=>!image.uri),'Self-contained textures');
  assert.ok(gltf.meshes.flatMap(mesh=>mesh.primitives).every(p=>!('COLOR_0' in p.attributes)),'No unused legacy vertex-color modulation');
  const triangles=gltf.meshes.flatMap(mesh=>mesh.primitives).reduce((n,p)=>n+(gltf.accessors[p.indices].count/3),0);
  assert.ok(triangles<=(asset.name.endsWith('-lod')?6000:25000),asset.name+' geometry budget');
 }
 const credits=JSON.parse(readFileSync(new URL('blendswap-source-credits.json',root)));
 assert.deepEqual(credits.map(c=>c.source_id).sort((a,b)=>a-b),[8745,21029,25188]);
 assert.ok(credits.every(c=>c.attribution&&c.license.url&&c.source_url));
});
