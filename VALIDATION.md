# Neon City / Build 08 — September 14, 2026

- Production build and 22 Node unit/API tests passed.
- Selected Playwright regression suite: 20 passed on the first run. The mobile HUD test exhausted its original 120-second deadline at the final post-reload position check. It passed independently in 2.6 minutes with a targeted 180-second deadline, including an assertion that mobile starts in balanced mode. All 21 selected scenarios are now covered successfully; this is not a claim that the initial suite was entirely green.
- Coverage: mission signal and choices, upgrades, rooftop recovery and navigation, NPC evidence/memory/autonomy, desktop/remote controls, combat and EMP, relay saves/extraction, audio controls, touch HUD persistence, driving/braking/exiting, map navigation and all three side-story branches.
- Inspected actual high and balanced browser screenshots. New city placement count: 83 buildings. Validated 31 self-contained GLB exports, about 13.3 MB total, plus the generated billboard and primary asset manifest.
- All 33 new files matched deployed preview bytes. Live preview test passed real car movement, braking, exit, music playback, expected Build 08 identity and zero browser errors. Revision: `echelon-breakpoint-00015-moy`.
- The automated VM uses software rendering. The balanced live sample reported about 546k triangles and 199 draw calls; high adds reflection/shadow passes. No hardware GPU frame-rate or physical-phone performance claim is made. Software rendering remains slow.
- Editable Blender source and generation prompts are documented in `NEON-CITY.md`. The reference board is concept art; `neon-street.png`, `neon-driving.png`, `neon-high-final.png` and `neon-live-driving.png` are browser captures.

---

# Build 02 validation

- Production Vite build succeeded.
- Four browser scenarios passed: assets/exposure/movement/fire/recharge/EMP/pause; relay checkpoint; extraction; invalid save position and credits.
- Additional aimed-combat scenario passed: sentry fire reduces integrity, aimed disruptor fire disables a sentry, and at least three rounds are consumed.
- Final high and balanced visual passes completed with no page errors. Screenshots: review-v2-title.png and review-v2-gameplay.png (last run is balanced).
- Imported barrier reduced from 60,928 triangles to approximately 7,300 in Blender.
- Texture/billboard image encoding reduced source image bytes from 12,243,510 to 3,239,306. GLB and HDR data are additional.
- Automated Chrome uses software rendering on the VM: high mode was below 1 FPS and balanced approximately 2 FPS in these captures. This is not a hardware GPU benchmark. High mode requires a capable hardware-accelerated browser; software rendering remains a performance limitation.
- Approximate balanced render workload in the captured view: 235 draw calls / 375,317 triangles. High mode adds a reflected scene pass.

Build 03 (2026-09-12): six Playwright scenarios pass, covering movement, combat, EMP/reload, relay checkpoint persistence, extraction, invalid saves/credits, and real MP3 playback advancing after a user gesture with volume and mute controls. Blender preview inspected for smooth shells, wheel hub alignment and imported-material correctness. Final vehicle-only adjustment aligned aero hubs to actual tire bounds.. Vite production build passes. Personal skill validates and a generated isolated starter passes npm ci/build. Software-rendered browser remains slow; no hardware GPU frame rate claim is made.

Mobile update: six desktop scenarios passed before final touch refinements; all three focused mobile tests passed on the final input code (portrait multitouch movement/look/fire, cancellation, reload/EMP/pause; landscape hacking/save/rotation; touch-only extraction). Inspected portrait/landscape menu and game screenshots. Fixed the minimap ID rule overriding its mobile size after screenshot review. Browser emulation uses Chrome/SwiftShader; physical iOS/Android devices are not available for performance validation.

Final mobile screenshot confirms 86×108 minimap and portrait subtitles above the health display. The saved starter snapshot includes the mobile controls/layout and touch tests.

## Living City upgrade — September 12, 2026

- Six campaign scenarios passed: signal checkpoint, rescue branch, capacitor/lockdown branch, upgrade purchase, rooftop recording and collision-map reachability of both interiors and rooftop ramp.
- Seven desktop/adaptive scenarios passed: generated sector contract reward, movement/combat/EMP, relay checkpoint, extraction, invalid-save handling/credits, enemy damage and aimed hits, and music playback/volume/mute. A subsequent final optic-coordinate combat check also passed.
- Nine Node unit/API cases passed, covering director constraints, campaign rules, optimistic storage writes, session isolation, checkpoint validation, request origin checks and audio ranges.
- Actual Cloud Run service-account requests successfully invoked Vertex Gemini and wrote/read Firestore checkpoints in the isolated `echelon-world` database. Final production evidence is in `deployment-status.json` and `backend-cloud-verification.json`.
- Blender-authored clinic/transit modules, props and vehicle distance LODs are retained with source scripts. Screenshots include desktop story choice, rooftop, generated sector and mobile story choice.
- The first mobile-story test used visible text instead of the button's accessible name (`Mission journal`); corrected the selector. This was a test lookup failure after the rescue action had succeeded.
- Physical Android/iPhone performance and a fixed ten-minute mission duration remain unmeasured. The map uses bounded modular areas, not unlimited generated meshes. Anonymous cloud sessions are tied to browser storage.
- Final mobile results: all three touch-control scenarios passed; corrected mobile rescue/journal scenario passed (22.4 seconds). Portrait gameplay, landscape menu and story-choice screenshots reviewed.
- Final desktop visual review loaded without page/HTTP errors. Balanced software-rendered sample: 298 draw calls and 302,750 triangles at the spawn view. The VM reported about 2 FPS under SwiftShader; this is not acceptable as a target device benchmark and is not presented as hardware-accelerated performance.
- Starter skill validation and isolated clone check passed, including unique save/session keys and configurable cloud identity.
- Production revision `echelon-breakpoint-00007-gmm` serves 100% of traffic. Live JS/CSS and changed Blender GLBs match the local build byte-for-byte. Production Gemini source and Firestore checkpoint round trip verified.
- Live Chrome gameplay review confirmed `ready=true`, `playing=true`, music advancing, `director.source=gemini`, an applied recovery contract and no page/HTTP errors. Temporary preview Cloud Run service deleted after production verification.

## Continuity / control redesign — September 12, 2026

Research: Activision's official COD Mobile control guide informed left movement/right swipe, separate aim, auxiliary fire and HUD customization. No external franchise assets or story characters were copied.

Passed checks so far:
- 15 server/unit scenarios including character validation, evidence/ending gates, concurrent cast/director/save requests and model fallback; a separate Blender asset check verifies all four models' dimensions and animation joints.
- Laptop hybrid-pointer regression, remote absolute-cursor aiming, firing/ADS and movement.
- Mara dialogue/evidence/trust/memory and autonomous following.
- Three mobile control regressions plus elevated/auxiliary fire, ADS and draggable HUD persistence.
- New accord ending, rescue/theft branches, core combat and mobile story/journal flow.

Corrections driven by evidence:
- Blender parenting needed a view-layer update before preserving transforms; corrected an oversized hair mesh. Export-safe joint names now match the runtime animation lookup.
- A completed checkpoint could be recreated by a late AI save. Completed runs now remove the local continue checkpoint on every save and ignore late world/character plans.
- Separated mobile health/ammo readouts from thumb action zones after screenshot review.

Limits: SwiftShader is software rendering, not a laptop GPU or phone benchmark. No physical handset or the user's remote-desktop path was available for latency testing. NPC dialogue is variable, not guaranteed never to repeat. Canonical evidence, trust changes and ending eligibility remain authored and validated.
- Corrected completed-save regression passed; Mara conversation/following scenario passed again with final character assets.
- Final Escape-from-typed-dialogue test passed and confirmed WASD movement returns to the game canvas.
- Final desktop and both mobile orientations reviewed without page errors; mobile review also exercised ADS and auxiliary fire. Character models now have correct proportions and named animated limb joints. Traffic yields to nearby cast members.
- Total this update: 16 unit/API/asset checks and 15 distinct browser scenarios passed across focused runs. Physical phone and actual remote-session latency remain unmeasured.
- Live revision `echelon-breakpoint-00008-2cp` serves 100% of traffic. Published JS/CSS and all four character GLBs match local hashes. Live browser reports a Gemini-driven cast with no page/HTTP errors. A typed question to Mara returned a Gemini response and the saved conversation memory survived a Firestore round trip.

## Open City / build 06 — September 12, 2026

- Production build passed; 21 unit/API tests passed, including substep vehicle collision, steering direction, bounded expanded saves and one-time story rewards.
- 17 distinct browser checks passed across controls-v2, game, mobile, cast and roaming suites. The final 8-check run verified NPC dialogue/memory, portrait movement/fire/pause, landscape hacking/layout, touch extraction, connected-road reachability, driving beyond the previous district boundary, map marker selection, persistent delivery/Harbor/Echo choices and touch gas/brake/exit.
- Initial test failures exposed a conflicting-traffic starter position (fixed), an overwriting save fixture (fixed), and an assertion that failed to account for autonomous NPC salvage (fixture isolated from that reward). Corrected checks passed.
- Inspected desktop driving/map/Harbor and phone screenshots. Corrected stretched road UVs. High graphics review entered the Harbor car with no page errors: 147 draw calls and 86,015 triangles in the sampled scene. Software renderer reported 3 FPS; this is not a physical-device benchmark.
- Cloud Run revision `echelon-breakpoint-00009-rul` now receives 100% of service traffic. Verified production JS/CSS and model hashes, new-district Firestore checkpoint restoration, real Gemini director/character responses, persistent NPC memory and the asset shortlist page.
- Realistic shortlisted character models remain uninstalled pending their licensed GLB/FBX downloads. Current cast remains the original Blender models.
- Separate StreamPixel preparation: API authentication succeeded and identified the inactive Echelon project; 3 local tooling contract tests passed. No Unreal build or StreamPixel gameplay session has been tested.

- Blender exported nine FBX assets for Unreal migration (4,578,332 bytes total); manifest confirms no skinned armatures. The separate ZIP includes source credits and canon data. Unreal import/animation and native compilation remain unverified.

## BlendSwap upgrade — September 13, 2026

- 22 Node tests pass, including binary GLB validation, near/far download and geometry budgets, bundled texture checks, and attribution.
- 13 selected Playwright checks pass across laptop/remote controls, movement/combat, checkpoints, soundtrack, driving, city navigation and story outcomes. After removing unused legacy vertex colors from the final GLBs, the mobile gas/brake/exit check passed again.
- Final production-build screenshots were inspected in balanced and high graphics modes. All six new model files loaded with HTTP 200 and no page errors. The optimized GLBs were also imported and inspected through the connected Blender addon in a separate review scene.
- The car has approximately 12.7k/2.5k triangles and downloads at 1.54 MB/270 KB for near/far meshes. Sentry and Warden assets use reduced near/far geometry as recorded in `public/assets/blendswap-browser-manifest.json`.
- The VM uses software rendering for browser checks. These results are functional/visual validation, not a claimed hardware frame rate or a physical-phone benchmark.
- This is the Three.js browser edition. The Unreal engine build and GCP GPU streaming migration are separate work on the main branch.

- Live release: `echelon-breakpoint-00010-8h5` serves 100% of Cloud Run traffic. Eleven production pages/bundles/model files match the local build byte-for-byte. Playwright verified Build 07 on the canonical URL, including car movement, brake, exit, advancing music and zero page errors.
- Deployment now explicitly advances traffic to the revision returned by the build, fixing the previous service pin that kept successful deployments on an older revision.
