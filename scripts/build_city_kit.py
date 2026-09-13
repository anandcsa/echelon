"""Original hard-surface props for Echelon; executed through Blender MCP."""
import bpy, math, os
from mathutils import Vector
ROOT='/home/anand_inbasekaran/echelon-breakpoint'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0,rough=.4,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
steel=mat('Brushed titanium',(.22,.28,.31),.7,.3);black=mat('Graphite ceramic',(.045,.065,.075),.35,.45);paint=mat('Patrol enamel',(.12,.23,.26),.65,.28);rubber=mat('Tire rubber',(.018,.022,.028),0,.8);glass=mat('Smoked sapphire glass',(.055,.16,.21),.7,.12);orange=mat('Safety amber',(1,.21,.025),0,.3,3);cyan=mat('Optical cyan',(.12,.8,1),0,.3,3);white=mat('Headlight',(1,.88,.6),0,.2,4);red=mat('Tail light',(1,.018,.012),0,.3,3);light=mat('Off-white polymer',(.6,.62,.55),.25,.45)
def box(n,p,s,m,b=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:
  mod=o.modifiers.new('Edge radii','BEVEL');mod.width=b;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(n,p,r,depth,m,rot=(0,0,0),vertices=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m)
 mod=o.modifiers.new('Edge radii','BEVEL');mod.width=.02;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 for f in o.data.polygons:f.use_smooth=True
 return o
def mesh(n,verts,faces,m):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def export(name):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=f'{ROOT}/public/assets/{name}.glb',export_format='GLB',use_selection=True)
 col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
 for o in list(bpy.context.scene.objects):
  if o.select_get():
   for c in list(o.users_collection):c.objects.unlink(o)
   col.objects.link(o);o.hide_set(True);o.hide_render=True
 bpy.ops.object.select_all(action='DESELECT')
# A low, broad autonomous sedan. Longitudinal axis Y, nose -Y.
box('Chassis',(0,0,.56),(2.05,4.6,.43),black,.13)
box('Armored body',(0,0,.85),(2.02,4.45,.55),paint,.18)
verts=[(-.86,-1,.99),(.86,-1,.99),(-.86,1.28,.99),(.86,1.28,.99),(-.69,-.55,1.65),(.69,-.55,1.65),(-.69,.92,1.65),(.69,.92,1.65)]
mesh('Cabin glazing',verts,[(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5),(4,5,7,6)],glass)
box('Roof',(0,.19,1.67),(1.46,1.6,.1),paint,.07)
box('Hood',(0,-1.55,1.14),(1.91,1.23,.1),paint,.04)
box('Rear deck',(0,1.65,1.14),(1.9,.9,.1),paint,.04)
for x in [-1.01,1.01]:
 box('Sill',(x,.05,.51),(.1,3.1,.19),steel)
 box('Door belt trim',(x,.05,1.02),(.055,2.3,.045),steel,.01)
 for y in [-.55,.66]:
  box('Flush door handle',(x*1.016,y,1),(.03,.23,.045),black,.01)
  box('Door seam',(x*1.015,y+.49,.82),(.01,.013,.34),black,.002)
 for y in [-1.37,1.39]:
  cyl('All terrain tire',(x,y,.49),.47,.28,rubber,(0,math.pi/2,0),32)
  cyl('Wheel hub',(x*1.15,y,.49),.31,.032,steel,(0,math.pi/2,0),24)
  cyl('Hub cap',(x*1.18,y,.49),.14,.04,black,(0,math.pi/2,0),16)
  for a in range(8):
   angle=a*math.pi/4;cyl('Wheel bolt',(x*1.2,y+math.cos(angle)*.22,.49+math.sin(angle)*.22),.025,.035,black,(0,math.pi/2,0),8)
 box('Wing mirror',(x*1.08,-.65,1.18),(.25,.3,.14),black)
box('Headlight strip',(0,-2.24,.98),(1.78,.03,.1),white,.01)
box('Tail strip',(0,2.24,1.02),(1.77,.03,.09),red,.01)
box('Front crash bar',(0,-2.28,.57),(1.8,.16,.15),steel)
for x in [-.7,-.5,-.3,-.1,.1,.3,.5,.7]:box('Intake grille',(x,-2.29,.75),(.04,.025,.14),black,.005)
cyl('Lidar sensor',(0,.2,1.84),.19,.22,black)
cyl('Lidar optical ring',(0,.2,1.89),.2,.04,cyan)
export('sentinel-sedan')
# Recon drone with armored center, ducted fans, gimbal and articulated pods.
box('Flight chassis',(0,0,0),(1.12,.9,.35),paint,.14)
box('Armor top',(0,0,.23),(.8,.72,.14),light,.09)
for x in [-.95,.95]:
 box('Outrigger',(x*.6,0,0),(.8,.16,.13),steel)
 for y in [-.55,.55]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.42,minor_radius=.065,major_segments=32,minor_segments=8,location=(x,y,0));bpy.context.object.data.materials.append(black)
  cyl('Motor',(x,y,0),.1,.15,steel)
  for a in [0,math.pi/2]:
   o=box('Rotor vane',(x,y,.025),(.73,.07,.03),black,.01);o.rotation_euler.z=a
  box('Navigation LED',(x,y,.1),(.13,.04,.025),cyan,.01)
cyl('Gimbal',(0,-.48,-.24),.19,.25,black,(math.pi/2,0,0))
cyl('Surveillance lens',(0,-.63,-.24),.12,.04,red,(math.pi/2,0,0))
for x in [-.4,.4]:box('Landing strut',(x,.1,-.28),(.06,.5,.4),steel,.02)
export('recon-drone')
# First-person electronic disruptor, nose -Y.
box('Receiver',(0,0,0),(.21,.53,.22),black,.035)
box('Upper rail',(0,-.06,.15),(.16,.7,.09),steel,.015)
box('Coil jacket',(0,-.48,.015),(.18,.42,.19),paint,.035)
cyl('Emitter barrel',(0,-.73,.035),.064,.12,black,(math.pi/2,0,0))
cyl('Emitter aperture',(0,-.798,.035),.037,.01,cyan,(math.pi/2,0,0))
for y in [-.32,-.4,-.48,-.56]:box('Coil winding',(0,y,.025),(.19,.025,.2),cyan,.008)
o=box('Grip',(0,.15,-.2),(.14,.18,.32),black);o.rotation_euler.x=-.2
box('Magazine',(0,-.09,-.22),(.12,.16,.25),steel)
box('Holographic sight',(0,.05,.23),(.11,.15,.12),black,.015)
box('Sight window',(0,-.031,.24),(.072,.01,.06),cyan,.005)
box('Status screen',(.112,.1,.035),(.01,.17,.09),cyan,.002)
export('pulse-carbine')
# Street vending unit with carefully modeled panel, louvers, keypad and dispenser.
box('Vending cabinet',(0,0,1.08),(1.08,.7,2.16),paint,.08)
box('Front inset',(0,-.36,1.2),(.92,.04,1.62),black)
box('Illuminated display',(-.12,-.39,1.5),(.57,.02,.9),cyan,.01)
box('Dispenser',(0,-.4,.38),(.65,.03,.28),black,.025)
box('Collection lip',(0,-.49,.24),(.72,.23,.04),steel)
for z in [.9,1.02,1.14]:
 for x in [.24,.34]:box('Keypad',(x,-.397,z),(.055,.015,.055),light,.009)
for z in [.12,.17]:box('Vent',(0,-.375,z),(.7,.01,.017),black,0)
export('vending-machine')
# Save editable kit, with each prop separated into a named collection.
for o in bpy.context.scene.objects:o.hide_set(False);o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=f'{ROOT}/echelon-city-kit.blend')
print('City kit exported')
