import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

// Original Blender kit. Main-road collision footprints remain aligned with mission access.
export async function buildNeonCity(scene, mats, obstacles, manager){
 const loader=new GLTFLoader(manager),models={},placements=[],batches=[],shared=new Map();
 const names=['tower-0','tower-1','tower-2','tower-3','tower-0-lod','tower-1-lod','tower-2-lod','tower-3-lod','planter','bench','shelter'];
 await Promise.all(names.map(async name=>{
  const gltf=await loader.loadAsync(`/assets/neon/${name}.glb`);gltf.scene.updateMatrixWorld(true);const parts=[];
  gltf.scene.traverse(m=>{if(!m.isMesh)return;const geometry=m.geometry.clone().applyMatrix4(m.matrixWorld);let material=shared.get(m.material.name);
   if(!material){material=m.material.clone();if(material.name==='NC mineral concrete'){material=mats.concrete.clone();material.name='NC mineral concrete';material.color.set('#a7a396');}if(material.name==='NC sapphire glazing'){material.envMapIntensity=1.5;material.roughness=.24;}shared.set(m.material.name,material);}
   if(material.map){const p=geometry.attributes.position,n=geometry.attributes.normal,uv=geometry.attributes.uv;for(let i=0;i<p.count;i++)uv.setXY(i,(Math.abs(n.getX(i))>.5?p.getZ(i):p.getX(i))/4,(Math.abs(n.getY(i))>.5?p.getZ(i):p.getY(i))/4);}
   parts.push({geometry,material});
  });models[name]=parts;
 }));
 const place=(name,x,z,scale=1,yaw=0,y=0,far=false)=>placements.push({name,x,z,scale,yaw,y,far});
 // Canyon blocks: gaps connect to the clinic, signal archive and rooftop route.
 for(const side of [-1,1])for(let i=0;i<6;i++){
  const z=55-i*30,x=side*29,variant=(i+(side>0?1:0))%4;
  place('tower-'+variant,x,z,1,side<0?Math.PI/2:-Math.PI/2);
  obstacles.push({x,z,w:10.9,d:10.9,minY:0,maxY:[43,58,72,91][variant]});
  place('planter',side*15.5,z+7,1,Math.PI/2);place('bench',side*15.5,z+3,1,side<0?Math.PI/2:-Math.PI/2);
 }
 // Outer city blocks: preserve all three longitudinal roads and four cross-streets.
 for(const x of [-205,-95,-48,48,95,205])for(const [i,z]of [135,230,265,350].entries()){
  const variant=(i+Math.abs(x))%4,scale=x===-48||x===48?1.05:1.18;
  place('tower-'+variant,x,z,scale,(i%4)*Math.PI/2);
  obstacles.push({x,z,w:10.5*scale+.45,d:10.5*scale+.45,minY:0,maxY:91*scale});
 }
 // Tiered distant skyline; different height, spacing and orientation avoid a uniform wall.
 let seed=861;const rand=()=>{seed=seed*16807%2147483647;return(seed-1)/2147483646;};
 for(let i=0;i<36;i++){const x=(i%2?1:-1)*(85+rand()*175),z=-145+rand()*220;place('tower-'+(i%4),x,z,.7+rand()*.75,Math.floor(rand()*4)*Math.PI/2,0,true);}
 for(let i=0;i<10;i++)place('tower-'+(i%4),-210+i*47,460+(i%2)*35,1.2+(i%3)*.25,0,0,true);
 place('tower-3',0,-166,1.35,0,0,true);
 for(const [x,z,a]of [[-15,66,Math.PI/2],[15,-16,-Math.PI/2],[-135,203,Math.PI/2],[135,285,-Math.PI/2]])place('shelter',x,z,.85,a);
 for(const x of [-165,-135,-15,15,135,165])for(const z of [117,155,190,285,330,408]){place('planter',x,z,1,Math.PI/2);if(z%2)place('bench',x,z+4,1,Math.PI/2);}
 const dummy=new T.Object3D();
 for(const name of names){const lod=name.endsWith('-lod'),items=placements.filter(p=>p.name===(lod?name.slice(0,-4):name));
  for(const part of models[name]){const mesh=new T.InstancedMesh(part.geometry,part.material,items.length);mesh.castShadow=mesh.receiveShadow=true;mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.frustumCulled=false;scene.add(mesh);batches.push({mesh,items,lod});}
 }
 let lastX=Infinity,lastZ=Infinity,lastQuality;
 function update(p,quality){if(Math.hypot(p.x-lastX,p.z-lastZ)<8&&quality===lastQuality)return;lastX=p.x;lastZ=p.z;lastQuality=quality;
  for(const {mesh,items,lod}of batches){let n=0;for(const item of items){const dist=Math.hypot(item.x-p.x,item.z-p.z),tower=item.name.startsWith('tower');if(tower&&lod!==(dist>(quality==='high'?105:65)))continue;if(dist>(tower?(quality==='high'?430:270):100))continue;
    dummy.position.set(item.x,item.y,item.z);dummy.rotation.set(0,item.yaw,0);dummy.scale.setScalar(item.scale);dummy.updateMatrix();mesh.setMatrixAt(n++,dummy.matrix);
   }mesh.count=n;mesh.instanceMatrix.needsUpdate=true;
  }
 }
 update(new T.Vector3(1.8,1.85,61),'high');
 return {update,placementCount:placements.length,buildingCount:placements.filter(p=>p.name.startsWith('tower')).length};
}
