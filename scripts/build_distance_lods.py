from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]
for name in ['sentinel-sedan','recon-drone']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(root/'public/assets'/f'{name}.glb'))
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  bpy.context.view_layer.objects.active=o
  if len(o.data.polygons)>40:
   m=o.modifiers.new('Distance LOD','DECIMATE');m.ratio=.14;bpy.ops.object.modifier_apply(modifier=m.name)
 bpy.ops.export_scene.gltf(filepath=str(root/'public/assets'/f'{name}-lod.glb'),export_format='GLB')
