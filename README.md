# Echelon: Breakpoint — Unreal streaming edition

An Unreal Engine 5.6 migration prototype for the existing Echelon browser game. **Native compilation and streaming have not yet been verified.** This repository is the first buildable-source candidate, not a claim of AAA completion or feature parity with the browser edition.

Current playable browser edition:
https://echelon-breakpoint-50221095849.us-central1.run.app

Character shortlist:
https://echelon-breakpoint-50221095849.us-central1.run.app/asset-shortlist.html

## Source included

- First-person movement with collision; Sentinel entry, arcade driving, braking and exit.
- A Mara character with local movement and bounded Gemini dialogue/intentions through the existing Node backend. E near Mara asks an authored question; the web bridge accepts typed questions.
- Nine FBX models exported in Blender, attributed PBR source textures, and original character canon.
- A Python content generator that imports the assets, creates PBR materials and builds the connected street map.
- `Web/` contains a provider player with typed Mara chat, explicit touch controls, movement/look gestures, brake/interact and neutral-input release handling. It has not yet been tested against an Unreal stream.
- Pixel Streaming enabled. Pixel Streaming 2 deliberately disabled because the provider requires exactly one plugin.
- Windows pre-build content preparation, plus a GitHub Actions source-validation workflow.

The initial character assets are articulated static geometry, not skinned human rigs. Photorealistic character replacement, animation retargeting, full campaign/combat parity, robust NPC navigation, mobile input validation and persistent identity across streaming reconnects remain migration work. Native saves currently write checkpoints under a process-local anonymous session; they do not yet restore across fresh stream instances. The existing browser edition retains its established saved progress and gameplay.

## StreamPixel cloud build

Project dashboard:
https://dashboard.streampixel.io/projectdetail/6aa5cbbe5c44891b8e2dcc3f

1. Open **Builds → Connect Repository → GitHub**.
2. Authorize the StreamPixel GitHub App for **anandcsa/echelon**, then select this repository.
3. Add a **Win64 / Development / main / Manual** build configuration, with auto-deploy off for the first verification.
4. Run the build. Inspect compilation, content import and cook/package logs. `AssetImport.log` records the automatic FBX/material/map generation.
5. Once the build succeeds, test its preview, then deploy it for streaming.

Provider docs:
https://docs.streampixel.io/resources/cloud-builds/connect-your-repository
https://docs.streampixel.io/resources/cloud-builds/build-configurations

The `.uproject` declares UE 5.6. Confirm that version is available in the selected build fleet. The Windows target invokes `Build/PrepareAssets.ps1`, which launches the installed Unreal Editor commandlet against a temporary asset-only sibling project, avoiding a dependency on a not-yet-compiled game module. It writes the real project's Content directory, then the normal C++ build/cook can proceed. This hook requires validation on the provider's actual build worker; a restricted runner may require the documented manual import step instead.

## Local Windows build

With UE 5.6 installed, run PowerShell:

```powershell
./Build/PrepareAssets.ps1 -EngineDir 'C:/Program Files/Epic Games/UE_5.6/Engine' -ProjectDir $PWD.Path
```

Open `Echelon.uproject`, compile the Editor target if prompted, inspect `/Game/Maps/Kairos`, then package Win64 Development. Assets are generated and ignored by Git; source FBX/JPG files are tracked. Imported material scale, vehicle orientation, camera framing and native input must be checked in-engine.

## Security and validation

No StreamPixel API key, GitHub token or cloud credential belongs in this repository. Provider credentials are not needed in the game or browser player. The native client uses a new anonymous bearer token for the existing game API; Vertex credentials stay on its server.

Run `python3 Build/validate_source.py` for source-layout, import-input and configuration checks. These do not compile Unreal C++ or validate visuals. See `VALIDATION.md` for the exact verification state.

See `SourceAssets/README.md`, `SourceAssets/source-credits.json` and the included original Car Concept license for asset attribution and limitations.
