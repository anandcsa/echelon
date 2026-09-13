"""Editable modular interiors, rescue pod and exploration props for the living district."""
from pathlib import Path
import bpy,math
ROOT=Path(__file__).resolve().parents[1]
helpers=(ROOT/'scripts/build_city_kit.py').read_text().split('# A low, broad')[0]
exec(helpers.replace("ROOT='/home/anand_inbasekaran/echelon-breakpoint'",'ROOT='+repr(str(ROOT))))
ROOT=Path(ROOT)
wall=mat('Architectural ceramic',(.38,.47,.5),.22,.48);floor=mat('Composite flooring',(.12,.19,.22),.35,.45);pearl=mat('Medical white',(.7,.8,.78),.35,.28)
def orb(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=p);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 return o
for name in ['clinic-module','transit-module']:
 box('Raised foundation',(0,0,.05),(12,12,.1),floor,.04)
 box('Rear structural wall',(0,5.9,2),(12,.2,4),wall,.06)
 for x in [-5.9,5.9]:
  box('Side wall',(x,0,2),(.2,12,4),wall,.06)
  box('Continuous wall light',(x*.975,0,2.8),(.04,11,.06),cyan,.01)
 for x in [-4,4]:
  box('Entry wall',(x,-5.9,2),(4,.2,4),wall,.08)
  box('Front inset',(x,-6.03,2),(2.9,.05,1.2),glass,.1)
 box('Entry lintel',(0,-5.9,3.8),(4,.25,.4),pearl,.06)
 box('Roof perimeter',(0,0,4.1),(12.3,12.3,.22),wall,.06)
 box('Skylight',(0,0,4.23),(6,7,.06),glass,.04)
 for y in [-3,0,3]:box('Ceiling light',(0,y,3.94),(3,.24,.06),white,.02)
 for x in [-4.5,4.5]:
  for y in [-2,2]:
   if name.startswith('clinic'):
    box('Treatment bed',(x,y,.65),(1.25,2,.25),pearl,.12);box('Bed pedestal',(x,y,.3),(.8,1.2,.6),black,.08)
   else:
    box('Station bench',(x,y,.55),(1.4,2,.2),steel,.1);box('Backrest',(x+.45,y,1),(.15,2,.9),paint,.06)
 box('Wall screen',(0,5.74,2.1),(3,.08,1.5),cyan,.08)
 export(name)
box('Stasis base',(0,0,.45),(1.35,2.6,.6),pearl,.22)
orb('Smoked capsule',(0,0,.95),(.59,1.2,.6),glass)
orb('Life support occupant',(0,0,.94),(.3,.72,.23),light)
orb('Helmet',(0,-.76,1.01),(.23,.27,.24),light)
for x in [-.64,.64]:box('Vitals rail',(x,0,.9),(.06,2.2,.06),cyan,.02)
box('Life support display',(0,1.22,1.05),(.65,.15,.4),cyan,.04)
export('survivor-pod')
box('Salvage case',(0,0,.35),(.7,.55,.7),black,.12)
box('Salvage top',(0,0,.75),(.65,.5,.12),steel,.08)
for x in [-.26,.26]:box('Status lock',(x,-.29,.4),(.07,.04,.35),orange,.02)
export('salvage-cache')
box('Terminal pedestal',(0,0,.5),(.5,.4,1),paint,.1)
o=box('Console',(0,-.08,1.08),(.85,.52,.15),steel,.08);o.rotation_euler.x=.25
box('Screen',(0,-.11,1.16),(.65,.35,.03),cyan,.02)
export('mission-console')
for o in bpy.context.scene.objects:o.hide_set(False);o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'echelon-district-kit.blend'))
