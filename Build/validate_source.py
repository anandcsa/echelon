"""Source contract checks only; this does not replace Unreal compilation."""
import ast, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
project=json.loads((root/'Echelon.uproject').read_text())
assert project['EngineAssociation']=='5.6'
plugins={p['Name']:p['Enabled'] for p in project['Plugins']}
assert plugins['PixelStreaming'] and not plugins['PixelStreaming2']
assert project['Modules'][0]['Name']=='Echelon'
for name in ['Echelon.Target.cs','EchelonEditor.Target.cs','Echelon/Echelon.Build.cs','Echelon/Echelon.cpp','Echelon/EchelonGame.h','Echelon/EchelonGame.cpp']:
    assert (root/'Source'/name).is_file(), name
for file in (root/'Build').glob('*.py'): ast.parse(file.read_text())
assets=json.loads((root/'SourceAssets/manifest.json').read_text())
assert len(assets)==9
for asset in assets:
    path=root/'SourceAssets'/(asset['name']+'.fbx')
    assert path.stat().st_size==asset['fbx_bytes'],path
    assert path.read_bytes().startswith(b'Kaydara FBX Binary'),path
for name in ['asphalt_02','concrete_wall_009','concrete_pavement','blue_metal_plate']:
    for channel in ['color','normal','rough']:
        assert (root/'SourceAssets/Textures'/(name+'-'+channel+'.jpg')).is_file()
engine=(root/'Config/DefaultEngine.ini').read_text()
assert '/Game/Maps/Kairos' in engine and '/Script/Echelon.EchelonGameMode' in engine
assert 'PrepareAssets.ps1' in (root/'Source/Echelon.Target.cs').read_text()
assert (root/'SourceAssets/car-concept-LICENSE.md').is_file()
print('Source contracts passed: project, single streaming plugin, import scripts, 9 FBXs, 12 textures, game/map configuration. Unreal compilation NOT performed.')
