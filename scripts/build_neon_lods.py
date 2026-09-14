"""Generate lower-detail distant tower and vehicle meshes from original Blender exports."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'public/assets/neon'
for name in ['tower-0','tower-1','tower-2','tower-3','sentinel-sedan','recon-drone','warden-drone']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(OUT/(name+'.glb')))
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('Distance simplification','DECIMATE');mod.ratio=.2 if name.startswith('tower') else .4;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'-lod.glb')),export_format='GLB',export_yup=True)
 print('LOD',name,flush=True)
