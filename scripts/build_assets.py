import bpy, math, os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0,emission=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=.32
 if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
 return m
dark=mat('Obsidian titanium',(.035,.055,.065),.85); glow=mat('Sentient amber',(1,.19,.025),0,6)
def box(name,loc,scale,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
 bevel=o.modifiers.new('Machined edges','BEVEL'); bevel.width=.08; bevel.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=bevel.name)
 return o
box('Foundation',(0,0,1),(15,15,2),dark)
for i in range(4):
 a=i*math.pi/2; x,y=5*math.cos(a),5*math.sin(a)
 box('Armored data spine',(x,y,18),(3,3,34),dark)
 box('Living conduit',(x*1.025,y*1.025,19),(.35,.35,33),glow)
box('Suspended intelligence',(0,0,25),(7,7,10),dark)
for z,r in [(10,7),(20,8),(32,6),(37,3)]:
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=.16,major_segments=64,minor_segments=8,location=(0,0,z)); bpy.context.object.data.materials.append(glow)
for z in range(3,35,4): box('Core',(0,0,z),(2,2,2),glow)
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'echelon-core.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(root,'public/assets/echelon-core.glb'),export_format='GLB')
