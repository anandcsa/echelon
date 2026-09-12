param([Parameter(Mandatory=$true)][string]$EngineDir,[Parameter(Mandatory=$true)][string]$ProjectDir)
$ErrorActionPreference = 'Stop'
$ProjectDir = [System.IO.Path]::GetFullPath($ProjectDir)
$marker = Join-Path $ProjectDir 'Content/Echelon/import-complete.json'
$files = @(Get-ChildItem (Join-Path $ProjectDir 'SourceAssets') -File -Recurse | Sort-Object Name) + @(Get-Item (Join-Path $ProjectDir 'Build/prepare_content.py'))
$fingerprint = ($files | ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash }) -join ''
if ((Test-Path $marker) -and ((Get-Content $marker -Raw | ConvertFrom-Json).fingerprint -eq $fingerprint)) { Write-Output 'Echelon content already prepared.'; exit 0 }
# An asset-only sibling project avoids loading an uncompiled game module during import.
$prepProject = Join-Path $ProjectDir 'EchelonAssetPrep.uproject'
@{ FileVersion=3; EngineAssociation='5.6'; Plugins=@(@{Name='PythonScriptPlugin';Enabled=$true},@{Name='EditorScriptingUtilities';Enabled=$true}) } | ConvertTo-Json -Depth 5 | Set-Content $prepProject -Encoding UTF8
$env:ECHELON_IMPORT_FINGERPRINT = $fingerprint
$editor = Join-Path $EngineDir 'Binaries/Win64/UnrealEditor-Cmd.exe'
if (!(Test-Path $editor)) { throw "Unreal editor commandlet not found at $editor" }
try {
 & $editor $prepProject -run=pythonscript "-script=$ProjectDir/Build/prepare_content.py" -unattended -nop4 -nullrhi -nosplash '-ExecCmds=Interchange.FeatureFlags.Import.FBX 0' "-abslog=$ProjectDir/AssetImport.log"
 if ($LASTEXITCODE -ne 0) { throw 'Unreal asset import failed. See AssetImport.log.' }
 if (!(Test-Path $marker)) { throw 'Import did not produce its completion marker.' }
} finally { Remove-Item $prepProject -ErrorAction SilentlyContinue }
