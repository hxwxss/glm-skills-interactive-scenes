---
name: interactive-scene-sim-ready
description: >-
  Build a validated, interactive, sim-ready 3D interior scene in Blender from a
  one-line prompt (e.g. "an interactive kitchen with a fridge, dishwasher, and
  walk-in pantry"), run a render-review-repair loop with geometric validation
  gates, export it to MuJoCo MJCF with real articulated joints and collision
  proxies, and render a promotional video. Use when the user asks to create,
  validate, or make sim-ready any interactive Blender environment (kitchen,
  living room, lab, bedroom...), export Blender scenes to MuJoCo, or produce
  demo videos of 3D scenes.
---

# Interactive Scene → Sim-Ready Pipeline

Turn a one-line prompt into a **physically-validated, MuJoCo-ready, interactive
Blender scene** plus a judgeset, a promo video, and a full audit trail.

Authoritative reference implementation: `assets/reference_impl/` (a complete
interactive kitchen — 813 meshes, 19 articulated joints, all gates passing,
validated MJCF). Copy it and swap `kit_params.py` to adapt to any new scene.

## Pipeline overview

```
one-line prompt
  → STAGE 0  runtime contract (Linux, exact Blender, headless)
  → STAGE 1  planning docs (params are the contract, not prose)
  → STAGE 2  parametric builder (kit modules, registry, joint stamping)
  → STAGE 3  render-review-repair loop  ←—— the core discipline
  → STAGE 4  validation gates G1–G4 (geometry, articulation, navigation)
  → STAGE 5  sim export: MJCF + OBJ meshes + keyframes → MuJoCo-validated
  → STAGE 6  promo video + cold-start delivery
```

Work **autonomously through every stage**. Never stop at "the script runs" —
the deliverable is validated pixels and a validated physics model.

## STAGE 0 — Runtime contract

Discover and lock the environment first:

```bash
uname -a                 # need Linux (WSL2 Ubuntu ok); Git Bash alone is NOT enough
blender --version        # need one EXACT version; 4.1.1 LTS recommended
```

- If Blender is missing: download the exact official build
  (`https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-x64.tar.xz`)
  into the Linux filesystem (`~/blender-4.1.1/`), never run the Windows exe.
- Headless only: `blender --background --factory-startup --python ...`
- GPU: try Cycles GPU (OptiX/CUDA); if enumeration fails, CPU with OpenImageDenoise
  is fine (a 32-core box renders a 720p preview frame in ~8 s). WSL2 often cannot
  enumerate devices — do not burn time on it.
- Record every successful command in the project README.

## STAGE 1 — Planning docs from the one-line prompt

Expand the prompt into **five markdown docs** *before* writing geometry code:
`ART_DIRECTION.md` (palette, mood, light), `SPATIAL_PLAN.md` (a measured table of
every zone/segment with coordinates), `ASSET_INVENTORY.md`, `INTERACTION_SPEC.md`
(every door/drawer/dispenser with axis, pivot, limits, named states), and
`ASSUMPTIONS.md`. Then encode everything as **named constants in
`scripts/kit_params.py`** — the params file is the single source of truth;
docs summarize it. If a doc and the params disagree, the params win.

## STAGE 2 — Parametric builder

Split the builder into kit modules (see `assets/reference_impl/scripts/`):

| module | role |
|---|---|
| `kit_params.py` | ALL dimensions, segment tables, camera list, joint seeds, tasks, robot route |
| `kit_util.py` | mesh toolkit (`box/cyl/revolve/tube/curve_tube`), Registry, drawers, `bake_scale`, collision proxies |
| `kit_materials.py` | procedural PBR library keyed by name |
| `kit_architecture.py` | shell, openings, glazing, exterior context |
| `kit_cabinetry.py` | carcass/door/drawer/joint system |
| `kit_appliances.py`, `kit_furniture.py`, `kit_props.py` | contents |
| `kit_lighting.py` | world + light groups |
| `kit_cameras.py` | fixed judgeset cameras |
| `kit_ir.py` | scene IR (JSON) written from the same constants |
| `build_scene.py` | orchestrator: clear factory scene → build → proxies → states → IR → save |

Non-negotiable rules (violations cost a full debug day each — see
`references/blender_pitfalls.md`):

1. **Bake scale into meshes** (`bake_scale`) — never leave object scale ≠ 1 on
   anything that has children, textures, or bevels.
2. **Origin-at-hinge for every moving part**: mesh verts shifted by ±half-size in
   the *baked* mesh, so one rotation = the whole state model.
3. **Parent-local authoring**: children are positioned in parent-local coords,
   `matrix_parent_inverse` untouched.
4. **Stamp joint metadata as custom properties** (`joint_id`, `joint_type`,
   `joint_axis`, `joint_pivot`, `joint_states_json`, `joint_limits`,
   `joint_default`) so any later process can drive joints without re-building.
5. Emit the scene IR from the build registries in the same run — never parse the
   .blend to reconstruct it.
6. Carcasses are open-fronted: sides perpendicular to the front, back opposite;
   the front plane hosts overlay fronts with 3 mm gaps.

## STAGE 3 — Render-review-repair loop (≥4 iterations)

This is where quality actually comes from. Cycle:

```
rebuild (factory startup) → render fixed judgeset at preview res
→ LOOK AT THE PIXELS (Read the PNGs; code review is not a substitute)
→ write reports/iteration_NN_review.md (severity, pixel evidence, root cause, fix)
→ repair the authoritative source → repeat
```

Fixed 12-camera judgeset via `scripts/render_judgeset.py` (hero 24 mm, zone
studies 28–35 mm, robot-height 0.75 m, interaction states, 50 mm material
close-up, high reverse audit). Issues are found by *looking*: doors that render
open, floors scaled wrong, handles crushed, windows blown white, scattered
furniture. Expect the first build to score ~60/100 and the loop to bring it past 90.

## STAGE 4 — Validation gates

`scripts/validate_scene.py` must implement and PASS:

- **G1** scene/IR integrity: unique stable ids, every name resolves, finite
  transforms, no unpacked external files, joints carry runtime props.
- **G2** static geometry: pairwise AABB prefilter + whitelist of *declared*
  contacts; 0 unexplained penetrations.
- **G3** articulation sweep: every joint sampled through its full range (≥13
  steps); every AABB flag confirmed by **BVH mesh intersection** (AABB corner
  ghosts are false positives); moving assemblies vs static context → 0 hits.
- **G4** navigation & tasks: robot-footprint disc (e.g. r=0.35 m) sampled along a
  declared polyline route with min clearance ≥ threshold; task initial states not
  pre-satisfied; appliance sweeps and opposing doors never collide.

Write `reports/validation_report.json` and iterate the pipeline until PASS —
see `references/validation_gates.md`.

## STAGE 5 — MuJoCo sim export

`scripts/export_mjcf.py` (runs in Blender) emits `sim_ready/kitchen_mjcf/`:
`kitchen.xml` + `meshes/*.obj` — static collision boxes (group 3, hidden),
per-material visual meshes (group 1), one articulated body per joint with
`frictionloss` on slides, and **keyframes for every named state**.
`scripts/validate_mjcf.py` (plain python, `pip install mujoco`) then verifies:
compiles, nq == njnt == 19, all limited with correct ranges, keyframes simulate
stably, worst contact depth bounded. See `references/sim_export_notes.md` for the
three unit/axis traps that will otherwise cost hours.

## STAGE 6 — Promo video + cold-start delivery

- `scripts/render_promo_video.py`: camera dolly + joint states as a **pure
  function of the frame number** (deterministic), PNG frames then H.264 via the
  Video Sequence Editor. 720p/24 fps ≈ 8–12 s per CPU frame — budget ~1 h.
- G6 cold-start: close everything, reopen the final .blend in a fresh CLI
  process, re-run validation, re-render hero + 2 interaction views, confirm
  dimensions/timestamps, sync deliverables.

## Deliverables checklist

`.blend` · `scene_ir/*.json` · `scripts/` · `renders/final|previews|
interaction_states/` · `renders/contact_sheet.jpg` · `renders/video/*.mp4` ·
`sim_ready/kitchen_mjcf/` · `reports/` (per-iteration + validation) · 7 planning
docs · `checkpoints/`.

## Adapting to a new scene

1. Copy `assets/reference_impl/` wholesale.
2. Rewrite `kit_params.py` (room dims, segment tables, joint seeds, cameras,
   tasks, route) — everything else reads from it.
3. Rewrite `kit_architecture.py` / `kit_cabinetry.py` geometry to the new plan;
   keep the utility and joint conventions untouched.
4. Adjust the 12 cameras, the palette in `kit_materials.py`, and the route.
5. Run the pipeline end to end; the validation gates transfer unchanged.
