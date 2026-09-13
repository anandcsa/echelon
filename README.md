# Echelon: Breakpoint — Continuity

A browser sci-fi action game built with Three.js/Vite and Blender assets. Play the Ghost Signal mission: trace Mara's transmission inside the transit station, decide whether to rescue Dr. Imani or take the life-support capacitor, sever three uplinks, and escape through the nexus. Explore a clinic, rooftop terrace, recordings and salvage; spend salvage at the clinic workbench.

The AI director uses Vertex Gemini through a same-origin Node backend on Cloud Run. It receives bounded gameplay statistics and proposes patrol, power, route, modular-sector and side-mission commands. Deterministic game code validates and applies them. Visited sector layouts persist. Side passages remain available during lockdown; gates warn before activation and cannot close through the player. Cameras sweep visible cones; drones investigate noise, telegraph attacks and react to EMP. Traffic turns away from closed gates. Relay shutdown disables the corresponding cameras and restores access.

## Run locally

`npm ci`, `npm run build`, then `npm start` (http://localhost:8080). Without GCP environment variables the server uses an in-memory development store and a deterministic director. Browser checkpoints also persist in localStorage. `npm run dev` starts Vite; backend calls fall back if no API server is connected.

`npm run test:unit` checks contracts, campaign rules, storage preconditions and API behavior. `npm test` runs Chrome browser scenarios, including mobile touch emulation. Tests require installed Chrome. Test files may be run separately on a software-rendering VM to avoid long combined runs.

## Controls

Desktop: WASD, Shift sprint, Space jump, mouse look/fire, R recharge, Q EMP, E interact/hold to hack, J journal, Escape pause. Mouse capture fallback: right-drag or arrow keys. Mobile: movement stick, drag-to-look/fire, on-screen actions and pause. Portrait and landscape work. Sensitivity, music volume, graphics and optional browser-spoken radio are in the menu. Existing pre-campaign saves retain their extraction eligibility.

## Backend and persistence

Node 22 serves compressed static assets and `/api/session`, `/api/save`, `/api/director`. Cloud Run uses a dedicated service account. Firestore database `echelon-world` stores anonymous session documents keyed by SHA-256 of a random 256-bit browser-held bearer token. The token is never sent to the model. Clearing site storage loses that anonymous session identity; this is not an account-based cross-device save system.

Configure `GCP_PROJECT`, `FIRESTORE_DATABASE`, `DIRECTOR_MODEL` (default gemini-2.5-flash-lite), and `AI_DAILY_LIMIT` (default 300). Cloud metadata provides credentials; never place API keys in browser code. Per-session leases cache director responses for 45 seconds. Shared Firestore budgets cap model calls globally; timeouts, offline use or exhausted budgets fall back to deterministic simulation. Cloud saves supplement local saves. `scripts/deploy.sh` updates the existing authorized service; `ECHELON_SERVICE` selects a separate preview service.

## World construction and limits

Blender source kits and build scripts are retained. New sectors use reserved, traversable pockets and three modular themes: medical relief, courier depots and resistance shelters. These are bounded procedural assemblies chosen by the director, not unconstrained AI-generated meshes or an infinite world. Preparation happens ahead of the player; existing sectors retain their theme. The simulation and graphics run locally and do not wait on an LLM.

City geometry uses material batching and spatial culling. Vehicles have Blender-generated distance LODs; optional sectors also have LODs. Balanced mode bypasses post-processing. High mode retains PBR, bloom and reflections. Physical iPhone/Android performance has not been measured; browser emulation is not a handset benchmark.

See `public/credits.html` and `public/assets/credits.json` for third-party licenses. The personal starter template is under `~/.codex/skills/aaa-game-template`.


## Continuity characters and controls

Four original Blender characters inhabit the city: Mara Vale, Rook Velez, Dr. Imani Sayegh and Echo / Instance Nine. Meet them in the street or clinic, press E / tap HACK, ask a typed question, collect authored evidence or share supplies. They retain trust and recent conversation memory. Their local navigation resolves the intentions selected by Gemini: follow, observe, cover, scavenge, assist or hide. Friendly aid needs trust and is limited by cooldowns. Imani is available only after rescue. The field journal contains dossiers and records. See STORY-BIBLE.md for the canon and ending conditions.

The `/api/cast` endpoint uses the existing server identity and shared model-call budget. Autonomous ensemble updates occur at most once per 75 seconds per session; direct conversation is throttled to one accepted interaction per eight seconds. World updates, character decisions and saves use optimistic Firestore writes. Model text does not grant evidence, trust, items or endings. When unavailable, characters continue with authored dialogue and local behavior. Dialogue can repeat; this is not an unlimited generative campaign.

Open CONTROLS / CUSTOM HUD from the menu. Laptop mode supports captured mouse look, LMB fire and RMB aim. Remote Desktop mode uses absolute cursor movement over the world without pointer capture, with continued turning at horizontal edges. Auto selects touch only when a coarse primary pointer has no fine pointer, and responds to actual touch/keyboard input; manual profiles are saved. Mouse, touch and ADS sensitivity are separate. Mobile uses left movement, broad right-side look, elevated fire/aim and a second left fire button. Drag HUD buttons in the editor, resize them and adjust opacity; settings persist on this browser. The normal hardware rendering path no longer enforces the previous 30 FPS cap. Actual handset performance remains unmeasured.

Control-layout research: [Activision's COD Mobile controls guide](https://blog.activision.com/call-of-duty/2019-10/Getting-a-Grip-on-the-Call-of-Duty-Mobile-Controls). The layout follows common FPS interaction principles and uses original game assets and styling.

## Open City / build 06

Five destinations connect through continuous roads: Kairos, Glass Harbor, Neon Exchange, Memory Depot and the Reservoir. Press M or MAP to set a waypoint. Three Sentinels can be entered with E / HACK; W/S accelerate/reverse, A/D steer, Space brakes, E exits when nearly stopped. Mobile buttons become GAS, BRAKE and EXIT; the movement stick also steers/reverses. Walking controls remain independent. Primary car location, story jobs, visited destinations and waypoint persist. Driving saves place the returning player beside the vehicle.

Rook's memory run leads from the Exchange to the Depot with private/public delivery choices. Harbor emergency power and Echo's divergent instance provide additional authored events. Their consequences alter persistent trust and enter the Gemini cast context. Ten ambient pedestrians use local routines; they are not individually LLM-controlled. Three additional sentries patrol new districts. This is a finite open city with arcade vehicle movement, not GTA-scale streaming, rigid-body vehicle physics, or an unlimited mission generator.

Realistic character candidates and exact download requirements are in ASSET-SHORTLIST.md and /asset-shortlist.html. These shortlisted models are not yet installed; current original Blender characters remain in use.

## BlendSwap visual upgrade / Build 07

The fleet uses Futuristic Car by DennisH2010 (3DHaupt), concept by Piotr Kupsc (CC BY 3.0). Spherical sentries use Drone Ball by CFilip (CC BY 3.0); Harbor and Archive patrols use BURT-VX-12 by THEREALDUSTIN (CC0). Full source URLs, changes and original notices are linked from `/credits.html`. Credentials and original downloaded archives are outside this repository.

Blender exports include near/far meshes: the car is approximately 12.7k/2.5k triangles, sentry 24k/4.8k, and warden 22k/4.4k. Car textures are 2K nearby and 512px at distance. Collider clearance matches the wider car. Visible drone optics retain the combat weak point and face the player. Existing movement profiles, quiet music, AI characters and open-city story remain in the browser edition.

`npm ci && npm run build` uses the included GLBs. Optional regeneration uses `scripts/import_blendswap.py` with inspected Blender review scenes generated by the native repository's `Build/export_blendswap.py` in sibling `echelon-unreal/Artifacts/AssetReview`. No account key is needed to build or play the checked-in browser app. The native Unreal migration and GCP GPU streaming setup remain on the repository's main branch.
