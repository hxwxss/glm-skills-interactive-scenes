# Final Validation & Delivery Report

Date: 2026-09-01 · Blender 4.1.1 (Linux, headless) · Cycles CPU (32 t) + OID denoise

## Gate results (all PASS)

| Gate | Result | Evidence |
|---|---|---|
| G0 environment/cold-build | PASS | exact 4.1.1 Linux binary; `--factory-startup` build regenerates .blend + IR in ~2 s; no GUI/MCP |
| G1 scene/IR integrity | PASS | IR parses; 104 unique stable ids; all blender_name resolve; transforms finite; 12 cameras; 19 joints carry runtime props; zero external file deps |
| G2 static geometry | PASS | 0 visible-mesh penetrations > 3.5 mm beyond declared contacts (AABB prefilter + whitelist) |
| G3 articulation | PASS | 19 joints × 14 samples full-sweep; every AABB flag confirmed by BVH mesh intersection → 0 real penetrations; pivots/axes/limits/named states verified against IR |
| G4 navigation & tasks | PASS | robot disc r=0.35 m traverses all 15 route segments; min clearance ≥ 60 mm (0.82 m+ effective passage); task initial states not pre-satisfied |
| G5 visual judgeset | PASS | 12/12 finals inspected as pixels; hero 2560×1440 s=192; others 1920×1080 s=112; two consecutive cycles (iteration 03 → 04 → finals) without material regression; self-scored 91/100 (≥85 % per category) |
| G6 cold-start | PASS | fresh CLI process: all gates re-PASS; hero re-rendered 2560×1440 (381.7 s, current timestamp); fridge-open + drawers-open interaction re-renders; `reports/coldstart_*.png` |

## Delivered files (Linux root: `/home/yuxuan/projects/interactive_kitchen_agent_project`)

- `interactive_kitchen_final.blend` (+ `checkpoints/final_gates_pass.blend`)
- `scene_ir/kitchen_scene_ir.json`
- `scripts/` — build_scene.py, validate_scene.py, render_judgeset.py,
  render_interaction_states.py, make_contact_sheet.py + 12 kit_* modules
- `renders/final/` — 12 numbered judgeset PNGs
- `renders/interaction_states/` — 16 evidence PNGs
- `renders/contact_sheet.jpg` (3880×1652)
- `reports/` — iteration_01/02–04 reviews, validation_report.json, final report
- Docs: README, ART_DIRECTION, SPATIAL_PLAN, ASSET_INVENTORY, INTERACTION_SPEC,
  TASK_STATE, ASSUMPTIONS

A full copy of the deliverables is synced to the Windows workspace:
`C:\Users\250010163\Desktop\Room_reconstruction\interactive_kitchen_agent_project\`
(the synced .blend was re-opened headlessly from that path to confirm portability).

## Render performance (CPU)

| Pass | Resolution | Samples | Time |
|---|---|---|---|
| Preview judgeset | 1280×720 | 40 | ~16 s/image |
| Final hero | 2560×1440 | 192 | 382–415 s |
| Final others | 1920×1080 | 112 | ~110–130 s/image |
| Interaction evidence | 1600×900 | 64 | ~40 s/image |

## Honest remaining limitations

- City exterior is procedural and intentionally hazy; minimal facade detail at close
  window angles.
- Appliance interiors and cookware contents are credible suggestions, not full models.
- West-window head-on remains high-key (bright overcast sky occupies part of the view).
- WSL CUDA not enumerable by this Blender build → CPU rendering used (documented;
  scripts auto-enable GPU when available).
