# Verification status

- GCP migration (September 13, 2026): direct Epic UE 5.6 player and pinned signalling server compile. Real signalling integration passed on desktop/mobile: waiting-for-game status, local video element, disconnect, no horizontal overflow and no provider HTTP requests. No Unreal streamer/video was present in this check.
- GCP scripts: shell syntax, Python compile and missing-engine fail-fast checked. Cloud read-only preflight verified the L4 machine type and regional quota. Provisioning, driver installation, TLS/TURN, native game and the four-hour VM limit have **not been exercised**. No GPU resources have been created.
- Engine access: Epic organization invitation accepted; UE 5.6.1 source downloaded. Native toolchain setup/build is now in progress.

- Source contract validation: checks `.uproject`, exactly one enabled Pixel Streaming plugin, required modules, FBX signatures/sizes, PBR texture inputs and Python syntax.
- Blender export: nine FBXs, source manifest and attribution retained.
- Browser player: Playwright passed connection state, typed dialogue, message origin/source filtering, touch movement/cancellation, manual touch-mode toggle and disconnect. The provider iframe was mocked; this does not verify an Unreal stream. Reproduce with `cd Web && npm ci && npx playwright install chromium && npm test`.
- Native Unreal compilation: **not run**. No Unreal Editor/toolchain is installed on the development VM.
- Windows content-import commandlet: **not run in Unreal**; must be verified on the StreamPixel build worker or a Windows editor installation.
- Packaged game/stream, collision, material scale, car orientation, frame pacing and touch input: **not yet verified**.
- Gemini endpoint was verified in the existing browser edition. The new native HTTP integration has not yet been exercised by an Unreal executable.
- Current scope is a first migration slice. Browser campaign/combat parity, skeletal character animation and stream-reconnect save restoration remain incomplete.
