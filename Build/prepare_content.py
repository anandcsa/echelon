"""Unreal Editor commandlet: import licensed source assets and build the first map."""
import json, os, random
from pathlib import Path
import unreal as u

root = Path(__file__).resolve().parents[1]
assets = u.AssetToolsHelpers.get_asset_tools()
material_api = u.MaterialEditingLibrary

def import_file(path, folder, name, options=None):
    task = u.AssetImportTask()
    task.set_editor_property('filename', str(path))
    task.set_editor_property('destination_path', folder)
    task.set_editor_property('destination_name', name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    if options:
        task.set_editor_property('options', options)
        task.set_editor_property('factory', u.FbxFactory())
    assets.import_asset_tasks([task])
    result = u.load_asset(folder + '/' + name)
    if result is None:
        raise RuntimeError('Asset was not imported at expected path: ' + folder + '/' + name)
    return result

for fbx in sorted((root / 'SourceAssets').glob('*.fbx')):
    opts = u.FbxImportUI()
    opts.set_editor_property('automated_import_should_detect_type', False)
    opts.set_editor_property('mesh_type_to_import', u.FBXImportType.FBXIT_STATIC_MESH)
    opts.set_editor_property('import_as_skeletal', False)
    opts.set_editor_property('import_materials', True)
    opts.set_editor_property('import_textures', True)
    opts.static_mesh_import_data.set_editor_property('combine_meshes', True)
    opts.static_mesh_import_data.set_editor_property('auto_generate_collision', True)
    import_file(fbx, '/Game/Echelon', fbx.stem.replace('-', '_'), opts)

textures = {}
for path in sorted((root / 'SourceAssets' / 'Textures').glob('*.jpg')):
    name = path.stem.replace('-', '_')
    tex = import_file(path, '/Game/Echelon/Textures', name)
    if path.stem.endswith('-normal'):
        tex.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
    elif path.stem.endswith('-rough'):
        tex.set_editor_property('srgb', False)
    u.EditorAssetLibrary.save_loaded_asset(tex)
    textures[name] = tex

def material(name, rgb, rough=.65, metal=0, glow=0, texture=None, ground=False):
    folder = '/Game/Echelon/Materials'
    path = folder + '/' + name
    existing = u.load_asset(path)
    if existing:
        u.EditorAssetLibrary.delete_asset(path)
    m = assets.create_asset(name, folder, u.Material, u.MaterialFactoryNew())
    def expr(cls):
        return material_api.create_material_expression(m, cls)
    def number(value, prop):
        e = expr(u.MaterialExpressionConstant)
        e.set_editor_property('r', value)
        material_api.connect_material_property(e, '', prop)
    color = expr(u.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant', u.LinearColor(*rgb, 1))
    material_api.connect_material_property(color, '', u.MaterialProperty.MP_BASE_COLOR)
    number(rough, u.MaterialProperty.MP_ROUGHNESS)
    number(metal, u.MaterialProperty.MP_METALLIC)
    if glow:
        emissive = expr(u.MaterialExpressionConstant3Vector)
        emissive.set_editor_property('constant', u.LinearColor(*(v * glow for v in rgb), 1))
        material_api.connect_material_property(emissive, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
    if texture:
        if ground:
            pos = expr(u.MaterialExpressionWorldPosition)
            mask = expr(u.MaterialExpressionComponentMask)
            mask.set_editor_property('r', True); mask.set_editor_property('g', True)
            mask.set_editor_property('b', False); mask.set_editor_property('a', False)
            scale = expr(u.MaterialExpressionDivide); scale.set_editor_property('const_b', 600)
            material_api.connect_material_expressions(pos, '', mask, 'Input')
            material_api.connect_material_expressions(mask, '', scale, 'A')
            uv = scale
        else:
            uv = expr(u.MaterialExpressionTextureCoordinate)
            uv.set_editor_property('u_tiling', 4); uv.set_editor_property('v_tiling', 4)
        for suffix, prop in [('color', u.MaterialProperty.MP_BASE_COLOR), ('normal', u.MaterialProperty.MP_NORMAL), ('rough', u.MaterialProperty.MP_ROUGHNESS)]:
            sample = expr(u.MaterialExpressionTextureSample)
            sample.set_editor_property('texture', textures[texture + '_' + suffix])
            if suffix == 'normal': sample.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            elif suffix == 'rough': sample.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
            material_api.connect_material_expressions(uv, '', sample, 'UVs')
            material_api.connect_material_property(sample, 'RGB' if suffix != 'rough' else 'R', prop)
    material_api.recompile_material(m)
    u.EditorAssetLibrary.save_loaded_asset(m)
    return m

def add_facade_windows(m):
    """World-space facade glazing avoids thousands of extra window actors/draw calls."""
    custom = material_api.create_material_expression(m, u.MaterialExpressionCustom)
    custom.set_editor_property('description', 'Seeded Kairos facade windows')
    custom.set_editor_property('output_type', u.CustomMaterialOutputType.CMOT_FLOAT4)
    custom.set_editor_property('inputs', [u.CustomInput(input_name='P'), u.CustomInput(input_name='N')])
    custom.set_editor_property('code', """
float2 uv = float2(abs(N.x) > 0.5 ? P.y : P.x, P.z) / float2(280.0, 360.0);
float2 cell = frac(uv);
float frame = step(0.12,cell.x) * (1-step(0.88,cell.x)) * step(0.18,cell.y) * (1-step(0.78,cell.y));
frame *= step(0.6,abs(N.x)+abs(N.y)) * step(300.0,P.z);
float seed = frac(sin(dot(floor(uv),float2(12.9898,78.233))) * 43758.5453);
float lit = frame * step(0.66,seed);
float3 base = lerp(float3(0.18,0.23,0.27),float3(0.025,0.085,0.12),frame);
return float4(base,lit);
""")
    pos = material_api.create_material_expression(m, u.MaterialExpressionWorldPosition)
    normal = material_api.create_material_expression(m, u.MaterialExpressionPixelNormalWS)
    material_api.connect_material_expressions(pos,'',custom,'P')
    material_api.connect_material_expressions(normal,'',custom,'N')
    mask = material_api.create_material_expression(m, u.MaterialExpressionComponentMask)
    for channel in ['r','g','b']: mask.set_editor_property(channel,True)
    mask.set_editor_property('a',False)
    material_api.connect_material_expressions(custom,'',mask,'Input')
    material_api.connect_material_property(mask,'',u.MaterialProperty.MP_BASE_COLOR)
    alpha = material_api.create_material_expression(m, u.MaterialExpressionComponentMask)
    for channel in ['r','g','b']: alpha.set_editor_property(channel,False)
    alpha.set_editor_property('a',True)
    material_api.connect_material_expressions(custom,'',alpha,'Input')
    tint = material_api.create_material_expression(m, u.MaterialExpressionConstant3Vector)
    tint.set_editor_property('constant',u.LinearColor(2.4,1.45,.65,1))
    glow = material_api.create_material_expression(m,u.MaterialExpressionMultiply)
    material_api.connect_material_expressions(alpha,'',glow,'A')
    material_api.connect_material_expressions(tint,'',glow,'B')
    material_api.connect_material_property(glow,'',u.MaterialProperty.MP_EMISSIVE_COLOR)

# Explicit portable materials avoid importing unsupported legacy Blender shaders.
blend_models = {}
blend_manifest = json.loads((root / 'SourceAssets/BlendSwap/manifest.json').read_text())
for entry in blend_manifest:
    folder = '/Game/Echelon/BlendSwap'
    opts = u.FbxImportUI()
    opts.set_editor_property('automated_import_should_detect_type', False)
    opts.set_editor_property('mesh_type_to_import', u.FBXImportType.FBXIT_STATIC_MESH)
    opts.set_editor_property('import_as_skeletal', False)
    opts.set_editor_property('import_materials', False)
    opts.set_editor_property('import_textures', False)
    opts.static_mesh_import_data.set_editor_property('combine_meshes', True)
    opts.static_mesh_import_data.set_editor_property('auto_generate_collision', True)
    opts.static_mesh_import_data.set_editor_property('normal_import_method', u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    mesh = import_file(root / 'SourceAssets/BlendSwap' / (entry['name'] + '.fbx'), folder, entry['name'], opts)
    mats = {}
    for desc in entry['materials']:
        m = material(desc['name'], desc['color'][:3], desc['roughness'], desc['metallic'])
        if entry['name'].startswith('bs_tower_'): add_facade_windows(m)
        if 'emission' in desc:
            e = material_api.create_material_expression(m, u.MaterialExpressionConstant3Vector)
            e.set_editor_property('constant', u.LinearColor(*(v * desc['strength'] for v in desc['emission'][:3]), 1))
            material_api.connect_material_property(e, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
        for channel, prop in [('color', u.MaterialProperty.MP_BASE_COLOR), ('normal', u.MaterialProperty.MP_NORMAL)]:
            filename = desc.get(channel + '_map')
            if not filename: continue
            path = root / 'SourceAssets/BlendSwap' / filename
            tex = import_file(path, folder + '/Textures', path.stem)
            if channel == 'normal':
                tex.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_NORMALMAP)
                tex.set_editor_property('srgb', False)
                # Blender uses OpenGL normal maps; Unreal expects DirectX green orientation.
                tex.set_editor_property('flip_green_channel', True)
            u.EditorAssetLibrary.save_loaded_asset(tex)
            sample = material_api.create_material_expression(m, u.MaterialExpressionTextureSample)
            sample.set_editor_property('texture', tex)
            if channel == 'normal': sample.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            material_api.connect_material_property(sample, 'RGB', prop)
        material_api.recompile_material(m)
        u.EditorAssetLibrary.save_loaded_asset(m)
        mats[desc['name']] = m
    for index, slot in enumerate(mesh.get_editor_property('static_materials')):
        name = str(slot.get_editor_property('imported_material_slot_name'))
        if name not in mats:
            raise RuntimeError(f'Unexpected material slot on {entry["name"]}: {name}')
        mesh.set_material(index, mats[name])
    # Catch incorrect FBX units before baking a city full of misplaced models.
    extent = mesh.get_bounds().box_extent
    actual = sorted([extent.x * .02, extent.y * .02, extent.z * .02])
    expected = sorted(entry['dimensions_m'])
    if any(abs(a-b) > max(.05, b * .03) for a,b in zip(actual, expected)):
        raise RuntimeError(f'Incorrect imported scale for {entry["name"]}: {actual} versus {expected}')
    u.EditorAssetLibrary.save_loaded_asset(mesh)
    blend_models[entry['name']] = mesh

road = material('M_Road', (.15,.18,.21), .4, .1, texture='asphalt_02', ground=True)
pavement = material('M_Pavement', (.4,.46,.5), texture='concrete_pavement', ground=True)
wall = material('M_Concrete', (.3,.4,.46), texture='concrete_wall_009')
metal = material('M_Metal', (.2,.32,.4), .4, .55, texture='blue_metal_plate')
glass = material('M_Glass', (.035,.12,.16), .2, .65)
cyan = material('M_Cyan', (.08,.75,.8), glow=4)
warm = material('M_Warm', (1,.6,.22), glow=2)
paint = material('M_Paint', (.8,.7,.3))

world = u.EditorLoadingAndSavingUtils.new_blank_map(False)
cube = u.load_asset('/Engine/BasicShapes/Cube.Cube')
actor_system = u.get_editor_subsystem(u.EditorActorSubsystem)

def cube_actor(x, y, z, sx, sy, sz, mat, collision=True):
    actor = actor_system.spawn_actor_from_class(u.StaticMeshActor, u.Vector(x,y,z))
    component = actor.static_mesh_component
    component.set_static_mesh(cube)
    component.set_material(0, mat)
    component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if collision else u.CollisionEnabled.NO_COLLISION)
    actor.set_actor_scale3d(u.Vector(sx/100,sy/100,sz/100))
    return actor

def box(x,z,y,w,d,h,mat,collision=True):
    return cube_actor(z*100,x*100,y*100,d*100,w*100,h*100,mat,collision)

box(0,145,-.2,470,560,.4,pavement)
box(0,-30,.015,24,210,.03,road)
for x in [-150,0,150]: box(x,250,.015,24,350,.03,road)
for z in [100,170,300,395]: box(0,z,.035,450,24,.03,road)
for z in range(-120,420,10): box(0,z,.06,.2,5,.03,paint,False)
rng = random.Random(9102)
for x in [-205,-95,-48,48,95,205]:
    for z in [135,230,265,350]:
        height = rng.uniform(14,38)
        box(x,z,height/2,26,25,height,wall if x<0 else metal)
        box(x,z,height,28,27,.8,metal)
        for y in range(4,int(height),4):
            for dx in range(-10,11,5):
                box(x+dx,z-12.6,y,2,.12,1.8,glass if rng.random()>.15 else warm,False)
                box(x+dx,z+12.6,y,2,.12,1.8,glass,False)
        for dx in [-13,13]: box(x+dx,z-12.7,3,.2,.2,6,cyan,False)
for side in [-1,1]:
    for z in [35,5,-25,-55,-85]:
        box(side*27,z,14,23,23,28,wall)
        for y in [4,8,12,16,20,24]:
            box(side*15.4,z,y,.12,19,2,glass,False)
for x in [-150,0,150]:
    for z in range(85,420,28):
        for side in [-1,1]:
            box(x+side*14,z,2.8,.15,.15,5.6,metal)
            box(x+side*13,z,5.6,2,.4,.12,warm,False)
for x in [-174,-126]: box(x,218,5,2,2,10,metal)
box(-150,218,10,50,3,1,metal)

for name,x,z in [('clinic_module',-43,36),('transit_module',43,-35)]:
    actor = actor_system.spawn_actor_from_class(u.StaticMeshActor,u.Vector(z*100,x*100,0))
    actor.static_mesh_component.set_static_mesh(u.load_asset('/Game/Echelon/'+name))

def detail(name, x, z, height=0, yaw=0, scale=1, collision=True, label=None):
    actor = actor_system.spawn_actor_from_class(u.StaticMeshActor, u.Vector(z*100,x*100,height*100))
    actor.set_actor_label(label or name)
    component = actor.static_mesh_component
    component.set_static_mesh(blend_models[name])
    component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if collision else u.CollisionEnabled.NO_COLLISION)
    actor.set_actor_rotation(u.Rotator(0,yaw,0),False)
    actor.set_actor_scale3d(u.Vector(scale,scale,scale))
    return actor

# Detailed skyline occupies spare lots; roads and the playable arrival area stay clear.
for name,x,z in [('bs_tower_a',-98,200),('bs_tower_b',48,200),('bs_tower_c',98,325),
                 ('bs_tower_b',-205,325),('bs_tower_c',205,200)]:
    detail(name,x,z)
    detail('bs_antenna',x,z,{'bs_tower_a':42,'bs_tower_b':35,'bs_tower_c':44}[name],collision=False)
for x,z,yaw in [(-13,60,0),(13,25,180),(-164,194,90),(164,324,270)]:
    detail('bs_relay',x,z,yaw=yaw)
# An airlock and uplink give Mara's meeting point an identifiable landmark.
detail('bs_airlock',-26,51,yaw=90)
detail('bs_antenna',-26,51,4,collision=False)
# Tagged mobile meshes are animated by the native game mode; no physics collisions in flight.
for index,(name,x,z,height) in enumerate([('bs_drone_ball',-6,43,7),('bs_drone_ball',6,76,8),
                                         ('bs_burt_drone',-149,200,11),('bs_burt_drone',149,340,12)]):
    drone=detail(name,x,z,height,collision=False,label='Echelon patrol '+str(index+1))
    drone.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
    drone.set_editor_property('tags',[u.Name('EchelonPatrol')])

music = import_file(root/'SourceAssets/Audio/floating_in_space.wav','/Game/Echelon/Audio','floating_in_space')
music.set_editor_property('looping',True)
u.EditorAssetLibrary.save_loaded_asset(music)
ambient = actor_system.spawn_actor_from_class(u.AmbientSound,u.Vector(0,0,200))
ambient.set_actor_label('Quiet Kairos soundtrack')
ambient.set_editor_property('tags',[u.Name('EchelonMusic')])
audio = ambient.get_component_by_class(u.AudioComponent)
audio.set_sound(music)
audio.set_editor_property('allow_spatialization',False)
audio.set_editor_property('auto_activate',True)
audio.set_volume_multiplier(.12)

start = actor_system.spawn_actor_from_class(u.PlayerStart,u.Vector(6100,180,96))
sun = actor_system.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,6000))
sun.set_actor_rotation(u.Rotator(-22,-35,0),False)
light = sun.get_component_by_class(u.DirectionalLightComponent)
light.set_mobility(u.ComponentMobility.MOVABLE)
light.set_editor_property('atmosphere_sun_light',True)
light.set_intensity(10000)
actor_system.spawn_actor_from_class(u.SkyAtmosphere,u.Vector(0,0,0))
sky = actor_system.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,1000))
sky_light=sky.get_component_by_class(u.SkyLightComponent)
sky_light.set_mobility(u.ComponentMobility.MOVABLE)
sky_light.set_editor_property('real_time_capture',True)
fog = actor_system.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,0))
fog.get_component_by_class(u.ExponentialHeightFogComponent).set_editor_property('fog_density',.008)
if not u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/Kairos'):
    raise RuntimeError('Map could not be saved')
u.EditorAssetLibrary.save_directory('/Game/Echelon',only_if_is_dirty=False,recursive=True)
marker = root/'Content'/'Echelon'/'import-complete.json'
marker.parent.mkdir(parents=True,exist_ok=True)
marker.write_text(json.dumps({'fingerprint':os.environ.get('ECHELON_IMPORT_FINGERPRINT','manual'),'map':'/Game/Maps/Kairos'}))
u.log('ECHELON_CONTENT_READY')
