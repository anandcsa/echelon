# Verification status

- Source contract validation: checks `.uproject`, exactly one enabled Pixel Streaming plugin, required modules, FBX signatures/sizes, PBR texture inputs and Python syntax.
- Blender export: nine FBXs, source manifest and attribution retained.
- Native Unreal compilation: **not run**. No Unreal Editor/toolchain is installed on the development VM.
- Windows content-import commandlet: **not run in Unreal**; must be verified on the StreamPixel build worker or a Windows editor installation.
- Packaged game/stream, collision, material scale, car orientation, frame pacing and touch input: **not yet verified**.
- Gemini endpoint was verified in the existing browser edition. The new native HTTP integration has not yet been exercised by an Unreal executable.
- Current scope is a first migration slice. Browser campaign/combat parity, skeletal character animation and stream-reconnect save restoration remain incomplete.
