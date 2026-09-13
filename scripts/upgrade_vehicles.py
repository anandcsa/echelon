"""Adapt CC BY Car Concept and author a smooth surveillance drone in Blender."""
from pathlib import Path
import bpy, math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# Import shared modeling helpers without rebuilding the original kit.
helpers=(ROOT/'scripts/build_city_kit.py').read_text().split('# A low, broad')[0]
exec(helpers.replace("ROOT='/home/anand_inbasekaran/echelon-breakpoint'",'ROOT='+repr(str(ROOT))))
ROOT=Path(ROOT)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'reference/car-concept-CarConcept.glb'))
pearl=mat('Pearlescent glacier enamel',(.48,.66,.7),.65,.23)
pearl.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.7
# Remove hidden cabin machinery, logos and costly tiny fittings. Replace branded textures.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 if o.name.startswith('Interior') or any(s in o.name for s in ['Wiper','License','BrakePad','BrakeDisc','HoodInterior']):
  bpy.data.objects.remove(o,do_unlink=True);continue
 mw=o.matrix_world.copy();o.parent=None;o.matrix_world=mw
 if hasattr(o.data,'gltf2_variant_default_materials'):o.data.gltf2_variant_default_materials.clear()
 if hasattr(o.data,'gltf2_variant_mesh_data'):o.data.gltf2_variant_mesh_data.clear()
 for i,m in enumerate(o.data.materials):
  n=m.name.lower()
  o.data.materials[i]=pearl if 'paint 1' in n else glass if 'glass' in n or 'mirror' in n else white if 'headlight' in n else red if 'brakelight' in n else orange if 'signallight' in n else rubber if 'tire' in n else steel if 'rim' in n else black
 if len(o.data.polygons)>450:
  bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Street LOD','DECIMATE');mod.ratio=.16 if 'Rim' in o.name else .28;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box]
lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);center=(lo+hi)/2
for o in objs:
 o.data.transform(o.matrix_world);o.matrix_world.identity()
 for v in o.data.vertices:
  v.co.x=(v.co.x-center.x)*2.25/(hi.x-lo.x);v.co.y=(v.co.y-center.y)*4.6/(hi.y-lo.y);v.co.z=(v.co.z-lo.z)*1.08
# Enclosed luminous aero hubs and sensor strip make autonomous fleet identity clear.
for o in objs:
 if not any('Tire rubber' in m.name for m in o.data.materials):continue
 lo=Vector([min(v.co[i] for v in o.data.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in o.data.vertices) for i in range(3)]);c=(lo+hi)/2
 x=hi.x+.018 if c.x>0 else lo.x-.018
 cyl('Aero hub',(x,c.y,c.z),(hi.z-lo.z)*.33,.024,steel,(0,math.pi/2,0),32)
 cyl('Hub light',(x+(.016 if x>0 else -.016),c.y,c.z),.07,.026,cyan,(0,math.pi/2,0),24)
export('sentinel-sedan')
def orb(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
orb('Seamless ceramic shell',(0,0,0),(.64,.77,.3),pearl)
orb('Underbody sensor band',(0,0,-.12),(.59,.71,.22),black)
orb('Dorsal armor',(0,.06,.17),(.47,.57,.2),pearl)
for x in [-.89,.89]:
 orb('Swept fan pylon',(x*.64,0,0),(.55,.25,.12),steel)
 for y in [-.46,.46]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.32,minor_radius=.095,major_segments=40,minor_segments=10,location=(x,y,0));o=bpy.context.object;o.name='Polished enclosed fan';o.data.materials.append(pearl)
  for f in o.data.polygons:f.use_smooth=True
  cyl('Duct motor',(x,y,0),.09,.12,black)
  for a in [0,math.pi/2]:
   o=orb('Rotor blade',(x,y,0),(.27,.035,.018),black);o.rotation_euler.z=a
  orb('Running light',(x,y,.095),(.06,.14,.025),cyan)
orb('Gimbal housing',(0,-.55,-.22),(.24,.23,.22),steel)
orb('Obsidian optical visor',(0,-.73,-.2),(.3,.10,.14),glass)
orb('Tracking eye',(0,-.825,-.2),(.105,.025,.065),red)
export('recon-drone')
for o in bpy.context.scene.objects:o.hide_set(False);o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'echelon-future-vehicles.blend'))
