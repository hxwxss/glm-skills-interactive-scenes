# Iteration 01 Review — preview judgeset (1280×720, Cycles CPU, s=40, AgX)

Renders inspected: `renders/previews/01..12*.png` (this iteration's actual pixels),
plus two diagnostic renders (`diag_uppers.png`, fresh `02_check_fresh.png`).
Blender: 4.1.1 headless, factory startup. Builder regenerated `.blend` + IR before rendering.

## Critical / major defects (with pixel evidence)

| # | Severity | Camera (file) | Evidence | Subsystem | Root cause in source | Fix | vs prev |
|---|---|---|---|---|---|---|---|
| 1 | CRITICAL | all interior views | Wood floor renders as ~1.5 m pale tiles with wide grooves (12_reverse), not 0.19 m planks; oak grain stretched into giant waves on entry door leaf (12) | Materials/architecture | `box()` sets object SCALE on unit cube; `Object` texture coords are pre-scale unit coords → plank/brick mapping scaled by object size | Bake size into mesh (`bake_scale`), keep object scale 1.0 for all boxes/spheres | n/a (first) |
| 2 | CRITICAL | 07_breakfast | Chair backrests are huge floating banana arcs; chairs read as broken sculpture | Furniture | `build_chair` slat torus R=0.52 m (≈2× chair width) centered wrong | Rebuild backrest: R=0.34 arc≈1.1 rad centered north of posts, minor r 0.02 | n/a |
| 3 | MAJOR | 01,02,09 | Cabinet/bar handles invisible or squashed slivers | Cabinetry | Door objects carry non-uniform scale; child handle cylinders inherit it (r×0.019 → invisible) | Same `bake_scale` fix + parent after bake | n/a |
| 4 | MAJOR | 03,07,12 | West window and north glazing blow out to flat white; no readable city context; terrace pavement washed out | Lighting/exterior | World 0.55 + exterior_amb 1500 W + light facades (0.48) + distant buildings | Darker/closer facades, world 0.45, key 3600→2800, ext amb →900, more lit window cells, darker wet terrace | n/a |
| 5 | MAJOR | 04,09 (early batch) | Oven door and several doors appeared missing/open | Cabinetry articulation | Hinge shift applied in mesh units then multiplied by object scale (12 cm float) | Unit-space hinge shifts (fixed mid-iteration; verified via world bboxes) | fixed |
| 6 | MAJOR | 09 | South-west corner too dark to inspect comfortably; fridge interior near-black | Lighting | Downlights 14 W undersized for 3 m ceiling; no fridge interior light | Downlights →22 W, fridge cavity 3 W strip, pantry 8→12 W, hall 18→30 W | n/a |
| 7 | MINOR | 01,12 | Stool footrings render as messy intersecting loops | Furniture | Footring R 0.155 crosses splayed legs; splay rotation crude | Vertical legs, ring R 0.14 minor 0.007 | n/a |
| 8 | MINOR | 06,12 | oak_dark renders loud orange (pantry sliding panel); jars render almost black | Materials | Oak palette oversaturated; low-iron glass + dark interior | Desaturate oak family; jar glass lighter tint | n/a |
| 9 | MINOR | 07,12 | Dining pendants read as bare rods with tiny bells | Props/lighting | Shade too small (r 0.146) and cord too visible | Shades → r 0.17, cord r 0.003 dark | n/a |
| 10 | MINOR | 03 | Black vertical voids between adjacent carcass runs read harsh | Cabinetry | Double side panels + unlit reveals | Lighten cab_body to 0.5 albedo (accepted reveal) | n/a |

## What works (verified in pixels)
- Layout, zone relationships, clearances read correctly from hero/robot/reverse cameras.
- Articulation machinery works post-load: JUDGE_09/10 show fridge door + tall door +
  drawers + pull-out open with interiors visible (after kit_runtime fix).
- Sink zone credible: undermount bowl, gooseneck faucet, window, sill, herb pot (03).
- Pantry has real depth, shelving, jars, boxes, toaster, drawers (06).
- IR/joints/proxies: 104 objects, 19 joints, 65 proxies; all joint states 0 (closed) verified.

## Score estimate (rubric): 58/100 → proceed to iteration 2 repairs above.
