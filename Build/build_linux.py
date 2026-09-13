#!/usr/bin/env python3
"""Import, compile and package using a locally installed, licensed UE 5.6 toolchain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine-root', required=True, type=Path, help='Directory containing Engine/')
    parser.add_argument('--output', type=Path, default=Path('Artifacts/Linux'))
    parser.add_argument('--jobs', type=int, default=8, help='Maximum parallel C++ actions')
    parser.add_argument('--import-only', action='store_true', help='Use the existing compiled editor to prepare a GPU editor preview')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    engine = args.engine_root.resolve() / 'Engine'
    editor = engine / 'Binaries/Linux/UnrealEditor-Cmd'
    uat = engine / 'Build/BatchFiles/RunUAT.sh'
    build = engine / 'Build/BatchFiles/Linux/Build.sh'
    for tool in (uat, build):
        if not tool.is_file():
            parser.error(f'Missing Unreal tool: {tool}. Install/build licensed Unreal Engine 5.6 first.')
    version = json.loads((engine / 'Build/Build.version').read_text())
    if (version['MajorVersion'], version['MinorVersion']) != (5, 6):
        parser.error('This project targets Unreal Engine 5.6.')
    if not 1 <= args.jobs <= 64:
        parser.error('--jobs must be between 1 and 64')
    project = str(root / 'Echelon.uproject')
    flags = ['-NoUBA', '-NoDebugInfo', f'-MaxParallelActions={args.jobs}']
    if not args.import_only:
        if not (engine / 'Build/InstalledBuild.txt').exists():
            # UE's BuildUBT helper also publishes the DLL to the path Build.sh executes.
            subprocess.run([str(engine / 'Build/BatchFiles/BuildUBT.sh')], check=True)
        # A source checkout has no editor executable yet. Build it before importing assets.
        subprocess.run([str(build), 'EchelonEditor', 'Linux', 'Development',
            f'-Project={project}', '-WaitMutex', *flags], check=True)
        subprocess.run([str(build), 'ShaderCompileWorker', 'Linux', 'Development', *flags], check=True)
    if not editor.is_file():
        editor = engine / 'Binaries/Linux/UnrealEditor'
    if not editor.is_file():
        parser.error(f'Editor build did not produce {editor}')
    digest = hashlib.sha256()
    inputs = sorted((root / 'SourceAssets').rglob('*')) + [root / 'Build/prepare_content.py', engine / 'Build/Build.version']
    for path in inputs:
        if path.is_file() and not any(part.endswith('.fbm') for part in path.parts):
            digest.update(str(path.relative_to(root) if path.is_relative_to(root) else path.name).encode())
            digest.update(path.read_bytes())
    prep = root / 'EchelonAssetPrep.uproject'
    if prep.exists():
        parser.error(f'{prep} already exists; inspect it before retrying.')
    marker = root / 'Content/Echelon/import-complete.json'
    env = dict(os.environ, ECHELON_IMPORT_FINGERPRINT=digest.hexdigest())
    try:
        prep.write_text(json.dumps({'FileVersion': 3, 'EngineAssociation': '5.6', 'Plugins': [
            {'Name': 'PythonScriptPlugin', 'Enabled': True},
            {'Name': 'EditorScriptingUtilities', 'Enabled': True}]}))
        subprocess.run([str(editor), str(prep), '-run=pythonscript', f'-script={root}/Build/prepare_content.py',
            '-unattended', '-nop4', '-nullrhi', '-nosplash', '-AllowCommandletAudio',
            '-ExecCmds=Interchange.FeatureFlags.Import.FBX 0', f'-abslog={root}/AssetImport.log'], env=env, check=True)
        if not marker.is_file() or json.loads(marker.read_text()).get('fingerprint') != digest.hexdigest():
            raise RuntimeError('Content import did not finish successfully; inspect AssetImport.log.')
    finally:
        prep.unlink(missing_ok=True)
    if args.import_only:
        print('Unreal content imported; compiled editor preview can now be staged.')
        return
    subprocess.run([str(uat), 'BuildCookRun', f'-project={project}', '-noP4', '-platform=Linux',
        '-clientconfig=Development', '-build', '-cook', '-stage', '-pak', '-package', '-archive',
        f'-archivedirectory={args.output.resolve()}', '-unattended', '-utf8output',
        '-nodebuginfo', '-ubtargs=' + ' '.join(flags)], check=True)
    if not list(args.output.resolve().rglob('Echelon.sh')):
        raise RuntimeError('Packaging returned without an Echelon.sh launcher.')
    print(f'Linux package created at {args.output.resolve()}. GPU and browser validation still required.')

if __name__ == '__main__':
    main()
