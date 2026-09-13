# Verification status — September 13, 2026

- Epic access is active. Unreal Engine 5.6.1 source and its Linux toolchain are installed outside this public repository. The first editor build is running; it is not yet a completed native build.
- The game C++ translation unit passes the bundled UE Clang 18 syntax check against the generated project headers and UE 5.6.1 headers. This check expanded the shared PCH header because the project PCH was still being built. It does not verify linking or gameplay.
- Blender exported nine original FBXs plus nine selected BlendSwap static derivatives. Three neutral Blender review renders are included with the BlendSwap credits. The FBX SDK check confirmed centimeter-scale bounds and material slot names on all nine BlendSwap meshes. The original car/drone CC BY 3.0 notices are retained; credentials, original scene archives and third-party source HDRIs are excluded.
- Source contracts pass: project/plugin setup, generated-header ordering, FBX signatures/sizes, bounded model complexity, texture presence, attribution and Python syntax.
- The direct GCP player and pinned Epic UE 5.6 signalling server build. Playwright passed desktop/mobile signalling connection, honest waiting-for-game state, disconnect, no horizontal overflow and no provider HTTP requests. There was no Unreal video in this test.
- GCP scripts passed shell/Python syntax and missing-package guards. Read-only preflight verified the L4 machine type and regional quota. No GPU VM has been created. Driver installation, TLS/TURN, native streaming and the four-hour VM limit remain untested.
- Native content import, shader compilation, cooking/packaging, rendered scale/orientation, collisions, audio, frame pacing and browser input still require a running Unreal executable. The importer contains checks for failed assets, unknown material slots and incorrect model dimensions.
- The native map now includes the BlendSwap fleet, tagged patrol drones, detailed skyline/equipment and a quiet music loop with a player toggle. These changes are prepared for import; the Blender renders are not in-game screenshots.
- The Gemini endpoint is verified in the existing browser edition. Native HTTP integration, campaign/combat parity, skeletal character animation and stream-reconnect checkpoint restoration remain incomplete.

The legacy provider player is retained under `Web/` for reference. Its mocked-provider tests are separate from the real Epic signalling checks under `GCP/player/` and do not establish an Unreal stream.
