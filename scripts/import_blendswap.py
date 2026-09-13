"""Export inspected BlendSwap derivatives for the browser with bounded near/far LODs."""
import bpy, json, math
from mathutils import Matrix
from pathlib import Path
root=Path(__file__).resolve().parents[1]
review=root.parent/'echelon-unreal/Artifacts/AssetReview'
manifest=[]
for source,name,target in [('bs_interceptor','bs-interceptor',13000),('bs_drone_ball','bs-sentry',24000),('bs_burt_drone','bs-warden',22000)]:
 bpy.ops.wm.open_mainfile(filepath=str(review/(source+'.blend')),load_ui=False,use_scripts=False)
 obj=bpy.data.objects[source]
 # Legacy paint layers are not used by the rebuilt shaders and must not modulate glTF materials.
 for attribute in list(obj.data.color_attributes):obj.data.color_attributes.remove(attribute)
 bpy.context.view_layer.objects.active=obj;obj.select_set(True)
 if source=='bs_interceptor':obj.data.transform(Matrix.Rotation(math.pi/2,4,'Z'))
 original=sum(len(p.vertices)-2 for p in obj.data.polygons)
 if original>target:
  mod=obj.modifiers.new('Browser triangle budget','DECIMATE');mod.ratio=target/original
  bpy.ops.object.modifier_apply(modifier=mod.name)
 for image in bpy.data.images:
  if image.size[0]>2048 or image.size[1]>2048:image.scale(2048,2048)
 for suffix,ratio in [('',1),('-lod',.2)]:
  if ratio<1:
   for image in bpy.data.images:
    if image.size[0]>512 or image.size[1]>512:image.scale(512,512)
   mod=obj.modifiers.new('Distant silhouette','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name)
  path=root/'public/assets'/(name+suffix+'.glb')
  bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_image_format='JPEG',export_jpeg_quality=92,use_selection=True,export_animations=False,export_cameras=False,export_lights=False)
  triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
  manifest.append(dict(name=name+suffix,source_derivative=source,triangles=triangles,bytes=path.stat().st_size,materials=len(obj.data.materials)))
(root/'public/assets/blendswap-browser-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('BROWSER ASSETS',manifest)
