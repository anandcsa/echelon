import bpy
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
p='/home/anand_inbasekaran/echelon-breakpoint/public/assets/road-barrier.glb'
bpy.ops.import_scene.gltf(filepath=p)
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o
  mod=o.modifiers.new('Browser LOD','DECIMATE');mod.ratio=.12;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.gltf(filepath=p,export_format='GLB')
