"""Regenerate the articulated cast and mission interior assets for the new city palette."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
# Existing pivot names and door openings are a gameplay contract, not visual constraints.
s=(ROOT/'scripts/build_npc_cast.py').read_text()
s=s.replace("segments=16,ring_count=10", "segments=24,ring_count=16")
s=s.replace("(.06,.35,.32)","(.14,.24,.25)").replace("(.43,.2,.06)","(.46,.11,.04)").replace("(.62,.72,.67)","(.76,.73,.65)")
s=s.replace("# Local Blender -Y", """# Tailored technical clothing and equipment, with readable layered silhouettes.
 box('Back armor',(0,.13,1.23),(.40,.12,.41),dark,.07)
 for x in [-.2,.2]:
  box('Shoulder harness',(x,-.13,1.34),(.065,.07,.34),trim,.018)
  box('Hip pouch',(x,-.16,.94),(.13,.10,.17),dark,.025)
  box('Pocket clasp',(x,-.22,.98),(.055,.015,.035),trim,.006)
 for z in [1.02,1.07,1.12,1.17]:box('Front zip',(0,-.165,z),(.013,.02,.03),trim,.002)
 box('Utility belt buckle',(0,-.18,.94),(.10,.03,.06),trim,.012)
 # Local Blender -Y""")
s=s.replace("parts.append(box('Mouth'", "parts.append(box('Mouth'")
s=s.replace("if id=='echo':\n  parts.append", """if id=='rook':
  parts.append(sphere('Protective helmet',(0,.01,1.78),(.151,.13,.13),cloth))
  parts.append(box('Visor',(0,-.131,1.735),(.245,.028,.067),glass,.018))
 if id=='echo':
  parts.append""")
s=s.replace("ROOT/'public/assets'/f'npc-", "ROOT/'public/assets/neon'/f'npc-")
exec(compile(s,str(ROOT/'scripts/build_npc_cast.py'),'exec'))
# Interior kit has the same 4m doors and collision dimensions, new surface and furnishings.
s=(ROOT/'scripts/build_district_kit.py').read_text()
s=s.replace("exec(helpers.replace", "helpers=helpers.replace(\"public/assets/{name}.glb\",\"public/assets/neon/{name}.glb\")\nexec(helpers.replace")
s=s.replace("(.38,.47,.5)","(.61,.57,.48)").replace("(.12,.19,.22)","(.16,.19,.19)")
s=s.replace("box('Wall screen'", """for y in [-4,-2,0,2,4]:
  for x in [-5.72,5.72]:
   box('Wall rib',(x,y,2),(.16,.18,3.7),steel,.04)
   box('Service inset',(x*.99,y,1.4),(.04,1.45,.8),black,.035)
 for x in [-3,3]:
  box('Roof HVAC',(x,3,4.6),(2.2,2.7,.65),steel,.12)
  for y in [2.2,2.6,3,3.4,3.8]:box('Vent louvre',(x,y,4.95),(1.8,.12,.06),black,.02)
 box('Wall screen'""")
exec(compile(s,str(ROOT/'scripts/build_district_kit.py'),'exec'))
