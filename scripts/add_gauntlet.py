import bpy,math
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
p='/home/anand_inbasekaran/echelon-breakpoint/public/assets/pulse-carbine.glb'
bpy.ops.import_scene.gltf(filepath=p)
def material(n,c,metal=.2):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=.55;return m
rubber=material('Tactical glove',(.035,.055,.06));armor=material('Wrist armor',(.23,.29,.31),.6)
def box(n,p,s,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('Softened edges','BEVEL');b.width=.025;b.segments=3;bpy.ops.object.modifier_apply(modifier=b.name)
box('Gloved palm',(.035,.2,-.25),(.19,.16,.2),rubber)
for i in range(4):box('Curled finger',(.085,.115,-.16-i*.044),(.12,.085,.037),rubber)
box('Thumb',(-.065,.11,-.13),(.07,.14,.06),rubber)
a=Vector((.035,.28,-.28));b=Vector((.11,.63,-.5));v=b-a
bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.09,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.name='Sleeve';o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(rubber)
box('Armored cuff',(.07,.4,-.35),(.21,.14,.18),armor)
bpy.ops.export_scene.gltf(filepath=p,export_format='GLB')
bpy.ops.wm.save_as_mainfile(filepath='/home/anand_inbasekaran/echelon-breakpoint/echelon-first-person.blend')
