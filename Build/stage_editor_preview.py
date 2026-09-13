#!/usr/bin/env python3
"""Stage an already compiled UE editor in game mode for a private GPU preview.
This contains licensed Epic binaries; never publish the staged directory.
"""
import argparse, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--engine-root',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];engine=a.engine_root.resolve();out=root/'Artifacts/EditorPreview';out.mkdir(parents=True,exist_ok=True)
if not (engine/'Engine/Binaries/Linux/UnrealEditor').exists():raise SystemExit('Compile editor first')
for folder in ['Binaries','Content','Config','Shaders','Plugins','Build','Programs']:
 source=engine/'Engine'/folder
 subprocess.run(['rsync','-a','--exclude=Intermediate/','--exclude=Source/','--exclude=Win64/','--exclude=Win32/','--exclude=Mac/','--exclude=Android/','--exclude=IOS/','--exclude=*.debug','--exclude=*.sym','--exclude=DotNet/','--exclude=UnrealBuildTool/','--exclude=AutomationTool/',str(source),str(out/'Engine')+'/'],check=True)
if not (root/'Content/Echelon/import-complete.json').exists():raise SystemExit('Engine staged; complete asset import before staging the project')
for folder in ['Binaries','Content','Config']:
 subprocess.run(['rsync','-a',str(root/folder),str(out/'Echelon')+'/'],check=True)
shutil.copy2(root/'Echelon.uproject',out/'Echelon/Echelon.uproject')
launcher=out/'Echelon.sh';launcher.write_text('''#!/usr/bin/env bash
set -euo pipefail
PREVIEW_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec "$PREVIEW_ROOT/Engine/Binaries/Linux/UnrealEditor" "$PREVIEW_ROOT/Echelon/Echelon.uproject" /Game/Maps/Kairos -game -nosplash "$@"
''');launcher.chmod(0o755)
print(out)
