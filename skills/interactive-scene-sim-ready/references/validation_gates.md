# Validation Gates G0–G6

Gates are the contract between "it renders" and "it is deliverable". Implement
them in `scripts/validate_scene.py` (geometry) and `scripts/validate_mjcf.py`
(physics export). A gate PASSes only with machine-readable evidence in
`reports/validation_report.json`.

## G0 — Runtime & cold build
- exact Blender version confirmed on Linux, headless
- `--factory-startup` build regenerates `.blend` + IR with zero manual steps
- no MCP, no GUI, no missing add-ons

## G1 — Scene/IR integrity
- IR parses as JSON; `schema_version`, blender version, timestamp present
- stable ids unique; every `blender_name` resolves to a live object
- dimensions/locations finite
- every joint has runtime custom properties (`joint_id` … `joint_limits`)
- zero unpacked external file dependencies

## G2 — Static geometry
- pairwise AABB overlap prefilter across all visible meshes
- whitelist only *declared* contacts: layered slabs, parent↔child parts,
  attached hardware (handles/stands/stems), joinery (aprons/legs/posts),
  intended seals
- penetration depth > 3.5 mm outside the whitelist → FAIL

## G3 — Articulation sweep
- for each joint: N ≥ 13 samples across the signed range
- moving assembly = registered object + `children_recursive`
- for each sample: `view_layer.update()`, AABB prefilter vs static context,
  **BVH mesh-intersection confirmation** for any flag deeper than 6 mm
  (AABBs of rotated slabs throw corner ghosts; only faces count)
- contacts that are *by design* (runner rails, roller-in-track, rack lips) are
  declared per joint in the IR `allowed_contacts`
- restore default state after each joint

## G4 — Navigation & task access
- robot footprint disc (r = 0.35 m) sampled every 10 cm along each route
  segment; clearance = min distance to any obstacle AABB (height band
  0.04–1.6 m) minus radius; threshold ≥ 60 mm at every sample
- access machinery with task preconditions (e.g. the closed pantry slider) is
  excluded and its precondition is documented in the IR task table
- task initial states must NOT already satisfy their success conditions
  (mug not already in the dishwasher…)

## G5 — Visual judgeset
- 12 fixed cameras rendered at final quality (hero ≥ 2560×1440)
- inspected as pixels; no open-through walls, no untextured defaults, no blown
  windows, reverse angles clean
- two consecutive complete cycles without material regression

## G6 — Cold-start delivery
- fresh CLI process reopens the final `.blend`, re-runs G1–G4 (PASS)
- re-renders hero + ≥2 interaction views at final quality with current
  timestamps; dimensions verified
- deliverables synced; contact sheet regenerated

## Physics-export gates (validate_mjcf.py)
- MJCF compiles: `nq == njnt == number of joints` (a mismatch means a joint tag
  was corrupted or a range degenerated)
- every joint limited, ranges match the IR (degrees for hinges, meters for slides)
- keyframes for every named state; each simulates ≥ 500 steps with
  `|qvel|max` small (stability) and worst contact depth bounded (≥ −5 mm)
- intended contacts (runner rails, roller tracks) excluded via
  `<contact><exclude>` at body level
