# Pipeline Stages — commands and discipline

Companion to SKILL.md. All paths relative to the project root
(`<linux>/~/projects/<scene>_project/`). Reference implementation:
`../assets/reference_impl/`.

## Stage 0 — Runtime (30 min, do not skip)

```bash
# inside WSL/Linux
mkdir -p ~/projects/<scene>_project/{scripts,scene_ir,checkpoints,reports,
                                   renders/{previews,final,interaction_states,video}}
curl -sL -o /tmp/bl.tar.xz https://download.blender.org/release/Blender4.1/blender-4.1.1-linux-x64.tar.xz
tar -xf /tmp/bl.tar.xz -C ~/ && mv ~/blender-4.1.1-linux-x64 ~/blender-4.1.1
~/blender-4.1.1/blender --version | head -1      # must print: Blender 4.1.1
```

GPU probe (2 min budget): `blender --background --factory-startup --python-expr`
setting `prefs.compute_device_type` to OPTIX/CUDA and counting devices; else CPU.

## Stage 1 — Planning docs

Write in this order: SPATIAL_PLAN (coordinates!) → ART_DIRECTION →
INTERACTION_SPEC → ASSET_INVENTORY → ASSUMPTIONS. Then `kit_params.py`.
Test: every constant used later must exist here; grep for magic numbers in
stage 2 code reviews.

## Stage 2 — Build

```bash
~/blender-4.1.1/blender --background --factory-startup \
  --python scripts/build_scene.py        # → .blend + scene_ir/*.json, ~2 s
```

The build prints an audit line (meshes/lights/cameras/joints/proxies). A build
crash is *good* at this stage — fix source, never patch the .blend.

## Stage 3 — Render-review-repair

```bash
# preview judgeset (~16 s/frame CPU)
~/blender-4.1.1/blender --background interactive_kitchen_final.blend \
  --python scripts/render_judgeset.py -- --quality preview
```

- READ every PNG. Diagnose with: straight-on diagnostic renders of suspect
  regions, `scene.ray_cast` from the camera, world-AABB dumps.
- One `reports/iteration_NN_review.md` per cycle: table of
  severity/evidence/camera/subsystem/root-cause/fix/vs-previous.
- Fix classes in expected order: layout > construction > articulation >
  materials > lighting > composition. Never decorate a broken build.

## Stage 4 — Gates

```bash
~/blender-4.1.1/blender --background interactive_kitchen_final.blend \
  --python scripts/validate_scene.py     # prints [G1..G4] PASS/FAIL
```

Iterate: validation failures name the exact pair (joint @ value ↔ object, mm
depth). Fix source, rebuild, revalidate. Then re-render the judgeset — gates
passing while pixels regress is a critical failure of process.

## Stage 5 — Sim export

```bash
# in Blender: writes sim_ready/kitchen_mjcf/kitchen.xml + meshes/*.obj
~/blender-4.1.1/blender --background interactive_kitchen_final.blend \
  --python scripts/export_mjcf.py
# outside Blender:
pip install mujoco                        # 3.12 used by the reference impl
python scripts/validate_mjcf.py           # compile + keyframes + contacts
```

Acceptance: nq == njnt == joint count; all limited; all keyframes stable;
worst contact > −5 mm; a MuJoCo-rendered still (`mujoco_view.png`) showing the
real scene (hide collision-only ceiling for the interior view).

## Stage 6 — Delivery

```bash
# finals (chunked: hero alone ~7 min CPU)
... --python scripts/render_judgeset.py -- --quality final --cameras 01,02,03
# interaction evidence
... --python scripts/render_interaction_states.py
# promo (background job, ~1 h for 432 frames + encode)
... --python scripts/render_promo_video.py -- --frames 0 431
... --python scripts/render_promo_video.py -- --encode
# contact sheet + cold start
... --python scripts/make_contact_sheet.py -- --src final
```

Cold start: new CLI process → reopen .blend → revalidate → re-render hero + 2
interaction views → verify dimensions/timestamps → sync deliverables.

## Timing reference (32-core CPU, Cycles + OIDenoise)

| pass | res | samples | s/frame |
|---|---|---|---|
| preview | 1280×720 | 40 | ~16 |
| final hero | 2560×1440 | 192 | ~400 |
| final others | 1920×1080 | 112 | ~110–130 |
| interaction | 1600×900 | 64 | ~40 |
| promo frame | 1280×720 | 24 | ~8–12 |

## Session discipline

- Keep a `TASK_STATE.md` updated after every stable stage: done, worst defects,
  next source-level actions, latest commands, latest render paths, rubric score.
- Long renders run as background jobs with chunked camera ranges; a 12-camera
  final batch exceeds any single command timeout.
- Deliverables live in the Linux filesystem; sync to the user-visible Windows
  folder at milestones (renders are small; the .blend is one file).
