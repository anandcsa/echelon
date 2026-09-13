# Kairos visual rebuild

## Diagnosis from the v1 browser screenshots

- Near-black materials without image-based lighting obliterated surface detail.
- Flat box buildings and randomly lit window dots lacked believable floor scale and architecture.
- Empty streets had almost no storefronts, signage, street furniture or narrative details.
- Hovering primitive drones and block cars looked like placeholders.
- There was no visible equipment or active combat feedback.

## Research and direction

CD Projekt RED's GDC talk, [Bringing Light to Night City](https://www.gdcvault.com/play/1027959/Advanced-Graphics-Summit-Cyberpunk-2077), describes cinematic, physically accurate lighting and the challenges of dense urban light sources. The practical direction taken here is readable blue-hour illumination, consistent human scale, distinct light colors, believable local detail and material response.

Poly Haven's [FAQ](https://docs.polyhaven.com/en/faq) and [license](https://polyhaven.com/license) confirm commercial reuse of CC0 assets. Eight asset sets were downloaded; source URLs and authors are preserved in `public/assets/credits.json` and the in-game credits page. The utility box and concrete barrier were downloaded/imported via Blender MCP and exported as self-contained GLBs. Road, concrete, metal and paving surfaces use color, normal and roughness maps. The environment uses a real evening HDRI.

## Implementation

A new assembled boulevard replaces the random grid. Mid-rise buildings have shop glazing, structural ribs, floor bands, signs, awnings, air conditioners, ladders, rooftop plant and overhead cables. An elevated transit bridge and the civic nexus define the route. A fictional AI-generated AURA portrait advertisement adds a visual focal point. Blender-authored hard-surface props replace primitive vehicles/drones and supply first-person equipment.

Rendering uses image-based lighting, hemisphere fill, a shadowed directional key, limited point lights, planar road reflections under textured asphalt, restrained bloom, fog and sky separation. Exposure and balanced graphics are accessible from the menu. Static geometry is merged by material, window lights are instanced, and imported static models are merged per material to reduce draw calls.

The game adds a pulse carbine, rechargeable magazine, hit feedback, three-hit drone disabling, line-of-sight checks, timed hostile fire, EMP disruption, world-space relay markers, jump, sprint, and checkpoint saves. It remains a finite browser prototype, not a production AAA open-world RPG.

## Build 03 assets
- Car Concept: https://github.com/KhronosGroup/glTF-Sample-Assets/tree/main/Models/CarConcept — Eric Chadwick / Darmstadt Graphics Group GmbH, CC BY 4.0, original source Unity Fan. Downloaded actual GLB and reference rendering. Blender adaptation removes unused interior, replaces branded materials, simplifies geometry and adds aero hubs. Imported variant metadata must be cleared or Blender restores original materials at export.
- Floating in Space: https://opengameart.org/content/floating-in-space — Umplix, CC0. Downloaded MP3 preview for self-hosted ambient music.
- New surveillance drone is original Blender geometry with smooth ceramic shells and enclosed fans. It is not represented as a downloaded model.
