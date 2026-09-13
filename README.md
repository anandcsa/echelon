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
- `GCP/player/` contains the active Epic Pixel Streaming player. `Web/` preserves the earlier provider player with typed Mara chat, explicit touch controls, movement/look gestures, brake/interact and neutral-input release handling. It has not yet been tested against an Unreal stream.
- Pixel Streaming enabled. Pixel Streaming 2 deliberately disabled to retain the current UE 5.6 integration while moving hosts.
- Windows pre-build content preparation, plus a GitHub Actions source-validation workflow.

The initial character assets are articulated static geometry, not skinned human rigs. Photorealistic character replacement, animation retargeting, full campaign/combat parity, robust NPC navigation, mobile input validation and persistent identity across streaming reconnects remain migration work. Native saves currently write checkpoints under a process-local anonymous session; they do not yet restore across fresh stream instances. The existing browser edition retains its established saved progress and gameplay.

## GCP streaming — active hosting direction

The user selected direct hosting in their Google Cloud account on September 13, 2026. No StreamPixel account, key, GitHub app or cloud build is required for this path.

See [GCP/README.md](GCP/README.md) for the build, provisioning and validation steps. The intended first preview uses one Compute Engine `g2-standard-8` VM with an NVIDIA L4, Epic's UE 5.6 signalling server, the custom browser player and authenticated TURN. The existing Cloud Run service retains the browser game and Gemini/save backend.

**Current blocker:** the authenticated GitHub account cannot read `EpicGames/UnrealEngine` (HTTP 404), and no Unreal Engine installation is present on this development VM. Link the GitHub account through Epic and accept the repository invitation:
https://www.unrealengine.com/en-US/ue-on-github

No GPU VM has been started, and there is no verified Unreal play URL yet. The native code, imported materials, packaging and GPU/WebRTC path still need to run on a licensed UE 5.6 toolchain. The previous StreamPixel configuration is historical; its queued build is not controlled by these scripts.

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
