"""Original articulated character models: tailored clothing, readable faces and joint pivots."""
from pathlib import Path
import bpy,math
ROOT=Path(__file__).resolve().parents[1]
helpers=(ROOT/'scripts/build_city_kit.py').read_text().split('# A low, broad')[0]
exec(helpers.replace("ROOT='/home/anand_inbasekaran/echelon-breakpoint'",'ROOT='+repr(str(ROOT))))
ROOT=Path(ROOT)
def sphere(name,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=p);o=bpy.context.object;o.name=name;o.scale=s;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def pivot(name,p):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p;return o
def child(o,parent):
 bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
for id,c,skin in [('mara',(.06,.35,.32),(.57,.32,.21)),('rook',(.43,.2,.06),(.31,.16,.08)),('imani',(.62,.72,.67),(.23,.105,.05)),('echo',(.23,.31,.51),(.36,.44,.49))]:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 cloth=mat(id+' tailored coat',c,.22,.52);dark=mat('Graphite technical fabric',(.035,.055,.065),.2,.6);skinmat=mat(id+' skin',skin,.05,.52);trim=mat('Ceramic seam',(.46,.63,.64),.5,.32);eye=mat('Eyes',(.018,.025,.027),.15,.18);iris=mat('Iris',(.12,.42,.38),.25,.3);hair=mat('Hair',(.04,.025,.02),.05,.7);glow=mat('Personal signal',(.15,.8,.73),.25,.3,1.1)
 # Local Blender -Y is the face direction. GLTF export rotates into +Z.
 sphere('Coat torso',(0,0,1.15),(.27,.155,.34),cloth);box('Coat hem',(0,0,.89),(.48,.29,.23),cloth,.06);box('Belt',(0,0,.93),(.47,.31,.045),dark,.015)
 for x in [-.12,.12]:box('Lapel',(x,-.15,1.32),(.12,.035,.23),dark,.015)
 box('Signal badge',(.15,-.175,1.25),(.06,.02,.04),glow,.007);sphere('Neck',(0,0,1.51),(.073,.07,.10),skinmat)
 head=pivot('Head',(0,0,1.66));parts=[sphere('Face',(0,-.012,1.69),(.128,.112,.166),skinmat),sphere('Jaw',(0,-.015,1.61),(.099,.088,.09),skinmat),sphere('Nose',(0,-.119,1.681),(.025,.031,.039),skinmat)]
 for x in [-.056,.056]:
  parts.append(sphere('Eye white',(x,-.110,1.718),(.027,.010,.012),trim));parts.append(sphere('Pupil',(x,-.12,1.718),(.012,.006,.01),eye));parts.append(box('Brow',(x,-.11,1.751),(.062,.015,.011),hair,.004));parts.append(sphere('Ear',(x*2.35,0,1.69),(.021,.028,.04),skinmat))
 parts.append(box('Mouth',(0,-.112,1.627),(.047,.008,.007),dark,.003))
 if id=='echo':
  parts.append(box('Visor',(0,-.118,1.72),(.22,.027,.04),dark,.012));parts.append(box('Visor filament',(0,-.136,1.72),(.16,.008,.009),glow,.003))
 else:
  parts.append(sphere('Hair cap',(0,.025,1.793),(.133,.1,.091),hair))
  if id in ['mara','imani']:parts.append(sphere('Tied hair',(0,.108,1.71),(.085,.073,.11),hair))
 for o in parts:child(o,head)
 for side,x in [('L',-.29),('R',.29)]:
  arm=pivot('Arm_'+side,(x,0,1.36));parts=[sphere('Shoulder',(x,0,1.34),(.096,.12,.12),cloth),sphere('Sleeve',(x,0,1.12),(.075,.09,.23),cloth),sphere('Glove',(x,-.005,.875),(.056,.059,.085),dark),box('Cuff',(x,0,.945),(.13,.16,.044),trim,.02)]
  for o in parts:child(o,arm)
 for side,x in [('L',-.125),('R',.125)]:
  leg=pivot('Leg_'+side,(x,0,.85));parts=[sphere('Trouser',(x,0,.51),(.099,.114,.34),dark),box('Boot',(x,-.046,.095),(.185,.32,.19),dark,.04),box('Knee plate',(x,-.108,.48),(.13,.04,.14),cloth,.025)]
  for o in parts:child(o,leg)
 if id=='rook':
  box('Courier satchel',(.17,.17,1.03),(.25,.13,.28),dark,.03);box('Respirator',(0,-.12,1.59),(.11,.07,.075),trim,.02)
 if id=='imani':
  box('Medical cross vertical',(-.15,-.17,1.24),(.015,.012,.062),glow,.003);box('Medical cross horizontal',(-.15,-.17,1.24),(.051,.013,.014),glow,.003)
 if id=='echo':
  for x in [-.21,.21]:box('Cognitive filament',(x,-.135,1.14),(.012,.018,.27),glow,.003)
 bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets'/f'npc-{id}.glb'),export_format='GLB',export_yup=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'echelon-characters.blend'))
