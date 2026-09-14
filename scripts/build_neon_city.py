"""Original Echelon city kit, guided by reference/neon-rebuild/city-reference.png.
Run with Blender 4.5 --background --python scripts/build_neon_city.py.
All dimensions are meters; Blender -Y exports to glTF +Z. No purchased meshes.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'public/assets/neon'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(2078)
manifest=[]
def mat(n,c,metal=0,rough=.5,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
concrete=mat('NC mineral concrete',(.48,.44,.36),.05,.8);ivory=mat('NC ceramic ivory',(.72,.73,.68),.35,.32);steel=mat('NC brushed titanium',(.24,.29,.31),.75,.35);black=mat('NC graphite',(.026,.04,.05),.3,.46);glass=mat('NC sapphire glazing',(.055,.15,.20),.75,.18);copper=mat('NC oxidized copper',(.34,.14,.072),.65,.44);rubber=mat('NC tire',(.015,.019,.021),0,.92);cyan=mat('NC cyan',(.08,.68,.75),.2,.3,1.4);amber=mat('NC amber',(1,.42,.12),.2,.35,1.5);red=mat('NC vermilion',(.8,.075,.026),.3,.4);tail=mat('NC tail',(1,.03,.018),.2,.3,2);white=mat('NC headlamp',(.8,.95,1),.2,.2,2);leaf=mat('NC foliage',(.13,.22,.065),0,.9);soil=mat('NC earth',(.065,.05,.027),0,1)
def box(n,p,s,m,b=0.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  mod=o.modifiers.new('Manufactured edge','BEVEL');mod.width=min(b,min(s)*.4);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Weighted corners','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def orb(n,p,s,m,seg=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def cyl(n,p,r,d,m,rot=(0,0,0),v=20):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 mod=o.modifiers.new('Machined edge','BEVEL');mod.width=min(.035,r*.15);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 for f in o.data.polygons:f.use_smooth=True
 return o
def tube(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=6;cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);o.data.materials.append(m);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def export(n,articulated=False):
 objects=[o for o in bpy.context.scene.objects if not o.hide_render]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 # Join static pieces by material offline: small primitive count per GLB and shared buffers.
 if not articulated:
  groups={}
  for o in objects:
   if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
  for name,items in groups.items():
   bpy.ops.object.select_all(action='DESELECT')
   for o in items:o.select_set(True)
   bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();items[0].name=name
  objects=[o for o in bpy.context.scene.objects if not o.hide_render]
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/(n+'.glb')),export_format='GLB',use_selection=True,export_yup=True)
 tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects if o.type=='MESH')
 manifest.append({'name':n,'triangles':tris,'bytes':(OUT/(n+'.glb')).stat().st_size})
 col=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(col)
 for o in objects:
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.hide_render=True;o.hide_set(True)
 print('EXPORTED',n,tris,flush=True)
def facade(width,depth,height,variant):
 # Sculpted podium and three stepped upper masses, rather than one slab with painted windows.
 box('Podium',(0,0,3),(width,depth,6),concrete,.5)
 for level,(frac,scale) in enumerate([(0.38,1),(.72,.86),(1,.68)]):
  bottom=6 if level==0 else 6+(height-6)*([.38,.72][level-1]);top=6+(height-6)*frac;w=(width-1.8)*scale;d=(depth-1.8)*scale
  box('Setback glazing',(0,0,(bottom+top)/2),(w,d,top-bottom),glass,.45)
  for z in range(int(bottom),int(top),4):
   box('Spandrel',(0,0,z),(w+.35,d+.35,.38),concrete,.08)
   for face in range(4):
    # Slim mullions and warm occupied windows on all four faces.
    count=int((w if face<2 else d)/3)
    for k in range(count):
     t=(k-(count-1)/2)*3
     if face<2:p=(t,(-1 if face==0 else 1)*(d/2+.025),z+1.6);s=(.12,.12,2.85)
     else:p=((-1 if face==2 else 1)*(w/2+.025),t,z+1.6);s=(.12,.12,2.85)
     box('Mullion',p,s,steel,0)
     if random.random()<.23:
      if face<2:p=(t+1, p[1],z+1.4);s=(1.4,.035,1.7)
      else:p=(p[0],t+1,z+1.4);s=(.035,1.4,1.7)
      box('Occupied office',p,s,amber,0)
  # Broad load-bearing panels break up the curtain wall; alternating bays make each tower distinct.
  for face in range(4):
   before=set(bpy.context.scene.objects)
   for x in [-w*.30,w*.30]:
    panel_width=2.5 if variant%2 else 3.5
    box('Facade pier',(x,-d/2-.20,(bottom+top)/2),(panel_width,.55,top-bottom-.5),concrete,.12)
    box('Inset copper rail',(x+panel_width*.35,-d/2-.5,(bottom+top)/2),(.11,.06,top-bottom-1),copper,.015)
    for zz in range(int(bottom)+1,int(top),4):box('Panel joint',(x,-d/2-.49,zz),(panel_width-.2,.015,.045),black,0)
   if variant in [1,3] and level==0:
    box('Vertical identity panel',(0,-d/2-.22,(bottom+top)/2),(2,.38,top-bottom-2),red,.1)
   for o in set(bpy.context.scene.objects)-before:
    xx,yy=o.location.x,o.location.y;a=face*math.pi/2;o.location.x=xx*math.cos(a)-yy*math.sin(a);o.location.y=xx*math.sin(a)+yy*math.cos(a);o.rotation_euler.z+=a
  for x in [-w/2,w/2]:
   for y in [-d/2,d/2]:box('Deep structural corner',(x,y,(bottom+top)/2),(.7,.7,top-bottom+.6),ivory,.18)
  box('Terrace coping',(0,0,top),(w+.9,d+.9,.65),concrete,.2)
  if level<2:
   for x in [-w*.35,w*.35]:
    box('Terrace planter',(x,-d/2+.5,top+.5),(4,1.3,.65),black,.15)
    for j in range(5):orb('Terrace shrub',(x-1.6+j*.8,-d/2+.5,top+.95),(.65,.55,.5),leaf,8,6)
 # Recessed shop fronts with separated windows, awnings, handles and plinths.
 for face in range(4):
  before=set(bpy.context.scene.objects)
  for x in [-6.4,0,6.4]:
   box('Store glazing',(x,-depth/2-.04,2.5),(5.4,.08,3.5),glass,.06)
   box('Shop light box',(x,-depth/2-.13,4.6),(5.7,.22,.72),red if variant%2 else black,.1)
   box('Shop sign accent',(x,-depth/2-.26,4.65),(4.6,.02,.08),amber if variant%2 else cyan,0)
   box('Deep awning',(x,-depth/2-.7,5.3),(6.1,1.65,.38),steel,.12)
   box('Awning underside',(x,-depth/2-.8,5.08),(5.6,1.25,.06),ivory,0)
   for dx in [-2.7,0,2.7]:box('Store upright',(x+dx,-depth/2-.14,2.5),(.11,.2,3.5),steel,.025)
   box('Door handle',(x+.35,-depth/2-.22,2),(.04,.06,.6),ivory,.01)
   box('Store sill',(x,-depth/2-.12,.8),(5.5,.25,.22),concrete,.04)
  # Rotate one facade around origin onto each side. Square building footprint.
  for o in set(bpy.context.scene.objects)-before:
   x,y=o.location.x,o.location.y;a=face*math.pi/2;o.location.x=x*math.cos(a)-y*math.sin(a);o.location.y=x*math.sin(a)+y*math.cos(a);o.rotation_euler.z+=a
 for x in [-width/2+.8,width/2-.8]:
  tube('Copper riser',[(x,depth/2+.2,1),(x,depth/2+.2,height*.7),(x-1,depth/2+.2,height*.7)],.12,copper)
 for z in range(9,int(height*.7),8):
  box('AC compressor',(width/2+.45,2,z),(.85,2,1.3),ivory,.13)
  for k in range(5):box('AC louvers',(width/2+.89,2,z-.45+k*.22),(.02,1.6,.06),black,0)
 for x in [-3,3]:
  box('Rooftop plant',(x,0,height+1.1),(3,4,1.6),steel,.2)
  cyl('Cooling fan',(x,0,height+1.96),1,.1,black,v=16)
 cyl('Communications mast',(0,0,height+4),.14,8,steel)
 cyl('Navigation beacon',(0,0,height+8),.25,.4,tail)
 for z in [height*.35,height*.65]:box('Service outrigger',(0,depth*.45,z),(width*.7,3,.5),concrete,.1)
for i,h in enumerate([43,58,72,91]):facade(21,21,h,i);export('tower-'+str(i))
# Spherical patrol robot: optically readable face, layered shell, thrust pods.
for name,scale in [('recon-drone',1),('warden-drone',1.25)]:
 orb('Ceramic flight shell',(0,0,0),(.62,.5,.42),ivory,32,20)
 orb('Equatorial insert',(0,0,-.03),(.635,.51,.23),black)
 orb('Ceramic upper shell',(0,0,.1),(.61,.48,.35),ivory)
 cyl('Optic collar',(0,-.48,-.12),.24,.17,steel,(math.pi/2,0,0),32)
 cyl('Lens',(0,-.58,-.12),.17,.04,glass,(math.pi/2,0,0),32)
 cyl('Reticle',(0,-.605,-.12),.06,.02,tail,(math.pi/2,0,0),20)
 for x in [-.75,.75]:
  orb('Thrust pod',(x,0,0),(.23,.36,.22),steel)
  cyl('Duct',(x,0,-.17),.17,.08,black)
  cyl('Ion ring',(x,0,-.22),.12,.025,cyan)
 for x in [-.35,.35]:tube('Shell seam',[(x,-.34,.25),(x,-.1,.4),(x,.2,.35)],.013,steel)
 box('Telemetry',(0,-.43,.23),(.38,.05,.055),cyan,.02)
 export(name)
# Smooth coupe body built from section rings; nose points -Y, glTF +Z.
def loft(n,sections,m):
 verts=[];faces=[];N=20
 for y,width,bottom,top in sections:
  for j in range(N):
   a=j*math.tau/N;verts.append((width*math.cos(a),y,(top+bottom)/2+(top-bottom)/2*math.sin(a)))
 for i in range(len(sections)-1):
  for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
 faces.extend([tuple(range(N-1,-1,-1)),tuple((len(sections)-1)*N+j for j in range(N))])
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m)
 for f in me.polygons:f.use_smooth=True
 return o
loft('Monocoque',[( -2.35,.74,.48,.83),(-2.12,.99,.35,1.02),(-1.45,1.05,.34,1.12),(-.5,1,.34,1.12),(.7,1.04,.34,1.17),(1.65,1.08,.38,1.15),(2.22,.92,.48,.94)],ivory)
loft('Continuous canopy',[(-1.25,.70,.9,1.05),(-.65,.78,.99,1.62),(.15,.77,1.04,1.72),(.9,.73,1.03,1.61),(1.5,.66,.98,1.16)],glass)
loft('Roof spine',[(-.65,.06,1.58,1.65),(.15,.065,1.67,1.74),(.9,.06,1.56,1.65),(1.5,.04,1.13,1.2)],black)
for x in [-1.0,1.0]:
 for y in [-1.45,1.43]:
  cyl('Performance tire',(x,y,.48),.455,.28,rubber,(0,math.pi/2,0),40)
  cyl('Wheel face',(x*1.145,y,.48),.34,.035,steel,(0,math.pi/2,0),32)
  cyl('Wheel center',(x*1.17,y,.48),.12,.05,black,(0,math.pi/2,0),20)
  for a in range(5):
   ang=a*math.tau/5;o=box('Turbine spoke',(x*1.17,y+math.sin(ang)*.2,.48+math.cos(ang)*.2),(.03,.075,.29),black,.02);o.rotation_euler.x=-ang
 tube('Shoulder crease',[(x*.94,-1.9,.98),(x*1.01,-.8,1.05),(x*1.02,.6,1.09),(x*1.02,1.8,1.04)],.016,steel)
 box('Aero sill',(x,0,.4),(.13,2.55,.16),black,.05)
 box('Flush handle',(x*1.02,.28,1.03),(.025,.28,.035),steel,.01)
 orb('Camera mirror',(x*1.08,-.75,1.19),(.16,.22,.085),black)
 for y in [-.9,-.4,.1,.6]:box('Intake blade',(x*1.01,y,.63),(.025,.18,.065),black,.01)
tube('Front running light',[(-.87,-2.08,.91),(-.55,-2.29,.9),(0,-2.38,.88),(.55,-2.29,.9),(.87,-2.08,.91)],.035,white)
tube('Continuous taillight',[(-.89,2.15,.87),(-.6,2.26,.87),(.6,2.26,.87),(.89,2.15,.87)],.034,tail)
box('Front diffuser',(0,-2.23,.55),(1.53,.18,.18),black,.06)
for x in [-.65,0,.65]:box('Rear aero fin',(x,2.15,.45),(.055,.28,.24),black,.015)
box('Rear registration',(0,2.245,.65),(.45,.015,.14),steel,.015)
export('sentinel-sedan')
# Street service kit: kiosks, bollards, planters, benches, terminals and road barriers.
for name in ['utility-box','vending-machine','mission-console']:
 h=1.6 if name=='mission-console' else 2.15;w=1 if name=='utility-box' else 1.35
 box('Rounded enclosure',(0,0,h/2),(w,.8,h),ivory,.18)
 box('Front graphite inset',(0,-.412,h*.55),(w*.85,.035,h*.74),black,.07)
 box('Information screen',(0,-.435,h*.64),(w*.65,.02,h*.36),glass,.04)
 for z in [h*.58,h*.68,h*.75]:box('Screen data',(0,-.45,z),(w*.48,.008,.027),cyan,.002)
 box('Canopy',(0,-.08,h+.1),(w+.22,1,.22),steel,.09)
 box('Canopy light',(0,-.55,h+.04),(w*.8,.04,.045),amber,.01)
 box('Dispenser',(0,-.45,.5),(w*.6,.08,.2),black,.04)
 for x in [-w*.3,w*.3]:cyl('Fixing',(x,-.455,.8),.027,.018,steel,(math.pi/2,0,0),12)
 for z in [.15,.23,.31]:box('Vent',(0,-.41,z),(w*.7,.03,.025),black,.005)
 export(name)
box('Crash barrier',(0,0,.53),(2.8,.75,.95),concrete,.2)
for x in [-.9,0,.9]:
 o=box('Safety stripe',(x,-.39,.62),(.25,.035,.58),red,.01);o.rotation_euler.y=-.3
box('Barrier cap',(0,0,1.06),(2.5,.65,.12),steel,.04);export('road-barrier')
box('Planter vessel',(0,0,.45),(3.4,1.4,.9),concrete,.16);box('Soil',(0,0,.9),(3.1,1.1,.05),soil,0)
for j in range(14):orb('Plant',((random.random()-.5)*2.8,(random.random()-.5)*.8,1+random.random()*.45),(.35,.32,.3),leaf,8,6)
export('planter')
box('Bench seat',(0,0,.55),(2.2,.62,.16),copper,.07)
for x in [-.8,.8]:box('Bench legs',(x,0,.27),(.13,.55,.55),steel,.04)
box('Bench back',(0,.26,.95),(2.2,.12,.65),steel,.07);export('bench')
# Integrated transport stop with rounded roof and enclosed ad panel.
for x in [-2.8,2.8]:box('Shelter column',(x,.5,1.8),(.24,.3,3.6),steel,.07)
box('Shelter back',(0,.65,1.9),(5.7,.08,2.6),glass,.05)
box('Shelter roof',(0,0,3.55),(6.4,3,.42),ivory,.2)
box('Strip light',(0,-1.35,3.35),(5.8,.05,.045),white,.01)
box('Timetable kiosk',(2.6,-.2,1.65),(.4,1.55,3),black,.14)
box('Display',(2.82,-.2,1.8),(.02,1.25,2.3),cyan,.01)
box('Shelter bench',(-.8,.25,.6),(3.2,.7,.16),copper,.06);export('shelter')
# New pulse carbine and central machine silhouette.
box('Weapon shell',(0,0,0),(.22,.62,.22),ivory,.07);box('Receiver',(0,-.37,.01),(.16,.4,.16),black,.05)
cyl('Emitter',(0,-.65,.01),.07,.24,steel,(math.pi/2,0,0));cyl('Emitter lens',(0,-.78,.01),.046,.02,cyan,(math.pi/2,0,0))
for y in [-.2,-.3,-.4]:box('Coil',(0,y,.11),(.17,.04,.025),cyan,.008)
o=box('Grip',(0,.17,-.2),(.14,.19,.29),black,.04);o.rotation_euler.x=-.2
box('Sight',(0,.03,.17),(.1,.18,.1),steel,.02);export('pulse-carbine')
for z,r in [(0,2.2),(1,1.9),(2,1.6),(3,1.3),(4,1)]:
 cyl('Core armor',(0,0,z),r,.55,steel,v=32);cyl('Core filament',(0,0,z+.3),r*.97,.055,cyan,v=32)
orb('Intelligence',(0,0,5),(1.25,1.25,1.5),glass,32,20)
for a in range(6):
 t=a*math.tau/6;tube('Core spine',[(math.cos(t)*2,math.sin(t)*2,0),(math.cos(t)*1.7,math.sin(t)*1.7,4),(math.cos(t)*.5,math.sin(t)*.5,6)],.13,ivory)
export('echelon-core')
# Keep editable collections in one source scene; visibility can be toggled per asset.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'echelon-neon-city.blend'))
(OUT/'manifest.json').write_text(json.dumps({'edition':'neon-city-2026-09','author':'Original Echelon procedural Blender models','reference':'reference/neon-rebuild/city-reference.png','assets':manifest},indent=2))
print('COMPLETE',len(manifest),'assets',flush=True)
