# Direct GCP Pixel Streaming

Hosting choice: user's Google Cloud account; Epic's upstream streaming stack. This is a single-player preview deployment, not a multi-user game service. The dedicated `echelon-stream` L4 VM is provisioned. See `VALIDATION.md` for the current runtime verification status.

## Verified account preflight

- Project: `gen-lang-client-0773193027`.
- Zone: `us-central1-a`.
- `g2-standard-8`: 8 vCPUs, 32 GB RAM, one NVIDIA L4.
- Regional L4 quota: 32 at preflight. Quota does not guarantee physical capacity.
- Separate `echelon-stream` VPC/VM names; existing workloads are not modified.
- Epic engine repository: invitation accepted; access active. UE 5.6.1 tag checked out locally at engine commit `6978b63c8951e57d97048d8424a0bebd637dde1d`.

Epic source access setup (already completed for `anandcsa`):
https://www.unrealengine.com/en-US/ue-on-github

## Build before provisioning

Install/build licensed Unreal Engine 5.6 on the development machine. Epic engine source and binaries must not be committed to this public repository. Follow the engine's setup instructions, then:

```bash
python3 Build/build_linux.py --engine-root /path/to/UnrealEngine --output Artifacts/Linux
npm ci --prefix GCP/player
npm run build --prefix GCP/player
```

The Linux helper validates the engine version, builds the editor and shader worker, runs the asset import commandlet, checks its fingerprint and invokes Unreal Automation Tool to compile/cook/package the game. Editor compilation, asset import and editor game-mode startup have passed; standalone cooking/packaging remains pending. Asset/source contracts and JavaScript checks cannot substitute for native compilation.

## First GPU preview

For an early native preview, the already compiled Unreal editor can run the game in `-game` mode. This is actual Unreal rendering, but is a larger deployment than a cooked game:

```bash
python3 Build/build_linux.py --engine-root /path/to/UnrealEngine --import-only
python3 Build/stage_editor_preview.py --engine-root /path/to/UnrealEngine
./GCP/provision.sh "$PWD/Artifacts/EditorPreview"
```

The staging helper includes the engine binaries, shader sources, program configurations, plugin runtime files and imported project. Keep `Artifacts/` private: it contains licensed Epic binaries. Do not run the staged copy while archiving it. First launch compiles a local shader cache and can take several minutes before streaming starts.

Alternatively, after successful standalone packaging, pass the directory containing `Echelon.sh`:

```bash
./GCP/provision.sh "$PWD/Artifacts/Linux/Linux"
```

The script refuses to allocate a VM without a game launcher/native binary directory and built player. It creates a dedicated network, IAP-only SSH ingress and one L4 VM, uploads the staged game or editor preview plus player, then installs the runtime. It does not copy Epic C++ source, GitHub tokens or GCP service-account credentials.

- Ubuntu 22.04, NVIDIA 570-or-newer server driver with NVENC/Vulkan libraries (UE 5.6.1 rejects older Linux drivers).
- UE 5.6 Epic infrastructure pinned to `771b83692a0bd464a6c3b80a0b207aafd7825162`.
- HTTPS via Caddy from its official signed package repository, authenticated preview access, coturn relay. The headless SDL dummy audio device keeps the mixer running for Pixel Streaming.
- Streamer/signalling ports 8888/8080 are not open in the cloud firewall. Public ports are HTTPS/ACME, authenticated TURN and restricted-range WebRTC media.
- TURN and preview passwords are generated on the VM. Preview login: `/root/echelon-preview-login`, mode 0600. Do not paste it into GitHub or logs.
- At most one player subscribes to the game. There is no session allocator or per-player isolation yet.
- A **four-hour VM run limit** stops the instance. It is a run-duration limit, not an idle detector or hard spending cap. Disk/IP costs may persist when stopped.

Default preview hostname: `<VM-IP>.sslip.io`. This external DNS service maps the hostname to the VM address; it is not a Google-owned domain. Prefer a domain you control for production. An optional second argument selects that hostname; its DNS A record must point to the VM before Caddy can issue a certificate. Ephemeral IP changes after stop/start require updating DNS, TURN `external-ip`, and the Caddy hostname/configuration. The first preview is intentionally not an always-on service.

After installation, reboot the VM to load the driver:

```bash
gcloud compute ssh echelon-stream --project gen-lang-client-0773193027 --zone us-central1-a --tunnel-through-iap --command='sudo reboot'
```

Then inspect `nvidia-smi`, `journalctl -u echelon-game`, `journalctl -u echelon-signalling`, and Caddy/coturn logs through IAP. Verify a real rendered frame, audio, laptop and touch input, driving, Gemini dialogue and relay connectivity before sharing a play URL. The runtime is not validated until these checks pass. Networks that block UDP may require additional TURN/TLS deployment work.

Stop the preview:

```bash
gcloud compute instances stop echelon-stream --project gen-lang-client-0773193027 --zone us-central1-a
```

## Player and signalling verification

The player connects directly to the same-origin Epic signalling WebSocket. It does not accept a signalling URL through query parameters and does not load a third-party iframe. Touch movement/look and typed Mara dialogue use Unreal UI-interaction messages; laptop keyboard input is disabled while typing chat. Disconnect closes the stream and reloads the page to remove input listeners.

`test-signalling.mjs` exercises the actual Epic signalling server with no Unreal process. It must display **WAITING FOR GAME**, never imply a playable stream. Build the pinned infrastructure's Common, Signalling and SignallingWebServer workspaces first, then:

```bash
EPIC_INFRA_PATH=/path/to/PixelStreamingInfrastructure node GCP/player/test-signalling.mjs
```

Official references:
https://github.com/EpicGames/PixelStreamingInfrastructure
https://docs.cloud.google.com/compute/docs/gpus
https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime


## Live video check

Fetch the generated preview login over IAP into a private local file, then run:

```bash
cd GCP/player
ECHELON_PREVIEW_URL=https://your-preview-host \
ECHELON_PREVIEW_LOGIN=/absolute/path/to/private-login-file \
node test-live-stream.mjs
```

This waits for decoded WebRTC video, records codec/resolution/frame statistics and audio energy, exercises entering/driving/braking, and captures screenshots. Inspect those screenshots to confirm the expected scene and movement. `ECHELON_TOUCH=1` checks touch controls; `ECHELON_RELAY=1` forces TURN. Increase `ECHELON_STREAM_TIMEOUT_MS` during first shader initialization. Do not treat the waiting page as proof that Unreal is streaming.
