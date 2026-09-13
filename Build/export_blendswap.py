"""Blender CLI: export selected licensed BlendSwap geometry with portable PBR materials.
Run with --factory-startup --disable-autoexec. Original downloads stay outside the repo.
"""
import bpy, json, math, pathlib, sys
from mathutils import Matrix, Vector

root = pathlib.Path(__file__).resolve().parents[1]
staging = pathlib.Path(sys.argv[sys.argv.index('--') + 1])
out = root / 'SourceAssets/BlendSwap'
out.mkdir(parents=True, exist_ok=True)
recipes = [
    dict(id=8745, name='bs_interceptor', include=['Speed_car.007','Speed_car.000','Cube.044','Cube.045'], length=4.6, material='car'),
    dict(id=21029, name='bs_drone_ball', exclude=['Plane','71884j_large'], length=1.6, material='metal', center=True),
    dict(id=25188, name='bs_burt_drone', length=2.4, material='metal', center=True),
    dict(id=24947, name='bs_tower_a', include=['Highrise_14'], height=42, upright=True, material='tower'),
    dict(id=24947, name='bs_tower_b', include=['Highrise_15'], height=35, upright=True, material='tower'),
    dict(id=24947, name='bs_tower_c', include=['Highrise_19'], height=44, upright=True, material='tower'),
    dict(id=24058, name='bs_airlock', include=['AIRLOCK'], height=3.8, material='metal'),
    dict(id=24058, name='bs_antenna', include=['antenna2'], height=4, material='metal'),
    dict(id=24058, name='bs_relay', include=['crew_unit'], height=2.2, material='metal'),
]
manifest = []

def material(recipe, original, index):
    label = original.name if original else 'metal'
    name = recipe['name'] + '_m' + str(index)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    d = dict(name=name, source_material=label, color=[.22,.28,.32,1], metallic=.65, roughness=.34)
    lower = label.lower()
    if any(s in lower for s in ['black','kevlar','rubber','dark']): d.update(color=[.025,.04,.055,1],metallic=.4,roughness=.4)
    elif any(s in lower for s in ['alum','steel','metal','chrome']): d.update(color=[.38,.44,.49,1],metallic=.85,roughness=.25)
    if 'soap' in lower or 'paint' in lower: d.update(color=[.63,.7,.71,1],metallic=.35,roughness=.26)
    if any(s in lower for s in ['emission','glow','laser']): d.update(color=[.04,.55,.8,1],emission=[.04,.7,1,1],strength=5)
    if 'glass' in lower or 'lens' in lower: d.update(color=[.025,.08,.11,1],metallic=.65,roughness=.08)
    if recipe['material']=='tower': d.update(color=[.12,.18,.22,1],metallic=.5,roughness=.32)
    p.inputs['Base Color'].default_value=d['color'];p.inputs['Metallic'].default_value=d['metallic'];p.inputs['Roughness'].default_value=d['roughness']
    if 'emission' in d:
        p.inputs['Emission Color'].default_value=d['emission'];p.inputs['Emission Strength'].default_value=d['strength']
    if recipe['material']=='car' and label=='Futuristic_Car':
        for image_name, channel in [('Futuristic_Car_C.jpg','color'),('Futuristic_Car_N.jpg','normal')]:
            image = bpy.data.images.get(image_name)
            if not image or not image.packed_file: continue
            filename=recipe['name']+'_'+channel+'.jpg';(out/filename).write_bytes(bytes(image.packed_file.data));image.filepath_raw=str(out/filename);image.file_format='JPEG'
            node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;d[channel+'_map']=filename
            if channel=='normal':
                image.colorspace_settings.name='Non-Color';normal=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(node.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
            else:m.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
    m.diffuse_color=d['color']
    return m,d

for recipe in recipes:
    folder=staging/str(recipe['id'])
    source=next(folder.rglob('*.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    bpy.context.scene.frame_set(1)
    bpy.context.scene.unit_settings.system='METRIC'
    bpy.context.scene.unit_settings.scale_length=1.0
    selected=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'} and not o.hide_render
              and o.name not in recipe.get('exclude',[]) and ('include' not in recipe or o.name in recipe['include'])]
    if not selected: raise RuntimeError('Empty model selection: '+recipe['name'])
    # Keep bevel detail but cap subdivision before evaluating to control game mesh density.
    for obj in selected:
        obj.hide_set(False)
        for mod in obj.modifiers:
            if mod.type=='SUBSURF':mod.levels=min(mod.levels,1);mod.render_levels=mod.levels
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();copies=[]
    for obj in selected:
        evaluated=obj.evaluated_get(deps)
        mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
        if not mesh.vertices:continue
        clone=bpy.data.objects.new(recipe['name']+'_'+obj.name,mesh);bpy.context.scene.collection.objects.link(clone)
        mesh.transform(obj.matrix_world);clone.matrix_world=Matrix.Identity(4);copies.append(clone)
    for obj in list(bpy.context.scene.objects):
        if obj not in copies:bpy.data.objects.remove(obj,do_unlink=True)
    if recipe.get('upright'):
        points=[v.co for obj in copies for v in obj.data.vertices]
        extents=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
        axis=max(range(3), key=lambda i:extents[i])
        rotation=Matrix.Rotation(-math.pi/2,4,'Y') if axis==0 else Matrix.Rotation(math.pi/2,4,'X') if axis==1 else Matrix.Identity(4)
        for obj in copies: obj.data.transform(rotation)
    points=[v.co for obj in copies for v in obj.data.vertices]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    size=hi-lo
    factor=recipe['height']/size.z if 'height' in recipe else recipe['length']/max(size)
    center=(lo+hi)*.5
    if not recipe.get('center'):center.z=lo.z
    remap={};materials=[];canonical={}
    for obj in copies:
        for v in obj.data.vertices:v.co=(v.co-center)*factor
        if not obj.data.materials:obj.data.materials.append(None)
        for i,original in enumerate(obj.data.materials):
            key=original.name if original else '__default'
            if key not in remap:
                new,desc=material(recipe,original,len(materials))
                signature=json.dumps({k:v for k,v in desc.items() if k not in {'name','source_material'}},sort_keys=True)
                if signature in canonical:
                    bpy.data.materials.remove(new);new=canonical[signature]
                else:
                    canonical[signature]=new;materials.append(desc)
                remap[key]=new
            obj.data.materials[i]=remap[key]
        # Preserve authored hard edges and smooth curved surfaces.
        obj.select_set(True)
    bpy.context.view_layer.objects.active=copies[0]
    bpy.ops.object.join();obj=bpy.context.object;obj.name=recipe['name']
    unique=list(canonical.values());indices={m.name:i for i,m in enumerate(unique)}
    faces=[indices[obj.data.materials[p.material_index].name] for p in obj.data.polygons]
    obj.data.materials.clear()
    for m in unique:obj.data.materials.append(m)
    for poly,index in zip(obj.data.polygons,faces):poly.material_index=index
    # Shared materials reduce draw calls without changing face assignment.
    tri_count=sum(len(p.vertices)-2 for p in obj.data.polygons)
    fbx=out/(recipe['name']+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},axis_forward='-X',axis_up='Z',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
    # Review scenes contain only the selected model and its new materials, not source HDRIs/scripts.
    for world in list(bpy.data.worlds): bpy.data.worlds.remove(world)
    for old in list(bpy.data.materials):
        if old not in remap.values(): bpy.data.materials.remove(old)
    used_images={n.image for m in remap.values() for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for image in list(bpy.data.images):
        if image not in used_images: bpy.data.images.remove(image)
    for text in list(bpy.data.texts): bpy.data.texts.remove(text)
    if bpy.data.use_autopack: bpy.ops.file.autopack_toggle()
    review=root/'Artifacts/AssetReview';review.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(review/(recipe['name']+'.blend')))
    metadata=json.loads((staging/(str(recipe['id'])+'-metadata.json')).read_text())
    metadata=metadata.get('data',metadata)
    license=dict(metadata['license'])
    if recipe['id'] in {8745,21029}:
        license.update(name='Creative Commons Attribution 3.0',url='https://creativecommons.org/licenses/by/3.0/',license_source='bundled_original_license')
    attribution='DennisH2010 (3DHaupt); vehicle concept by Piotr Kupsc' if recipe['id']==8745 else metadata['author']['username']
    manifest.append(dict(attribution=attribution,name=recipe['name'],source_id=recipe['id'],source_url=metadata['url'],author=metadata['author'],license=license,source_downloads=metadata['counts']['downloads'],triangles=tri_count,dimensions_m=list(size*factor),materials=materials,fbx_bytes=fbx.stat().st_size,changes='Selected geometry, applied modifiers, normalized scale/origin, rebuilt portable PBR materials. Scene backgrounds and reference images omitted.'))
    print('EXPORTED',recipe['name'],tri_count,'triangles',flush=True)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
