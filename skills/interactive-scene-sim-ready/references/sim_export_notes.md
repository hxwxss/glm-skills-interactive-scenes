# MuJoCo Export Notes

`scripts/export_mjcf.py` (Blender side) + `scripts/validate_mjcf.py`
(pure-python side). Target: MuJoCo ≥ 3.12 (`pip install mujoco`).

## Structure emitted

```
sim_ready/kitchen_mjcf/
  kitchen.xml
  meshes/            # statics_<material>.obj + <joint_id>.obj per moving part
```

- **Statics** → collision boxes (from world AABBs, `group="3"`, `contype=1
  conaffinity=1`) + ONE visual mesh per material bucket (`group="1"`,
  `contype=0 conaffinity=0`), each with a flat rgba from a keyword palette.
- **Articulated parts** → body at the pivot (`pos = pivot`), joint on the real
  axis, visual mesh geom + per-part collision boxes; slides get
  `frictionloss="0.8"` so unactuated drawers hold position (real runners do).
- **Keyframes** for every named state (`closed/half/open`) — this is what makes
  `mj_resetDataKeyframe` a task-reset API.
- Intended contacts (sliding panel ↔ its track) are silenced with
  `<contact><exclude body1="..." body2="world"/>` — declared, not hidden.

## The three traps (each verified empirically)

### 1. Keyframe qpos is ALWAYS radians
`<compiler angle="degree">` converts *attribute* values (joint `range`,
`axisangle`…) but **not** keyframe `qpos`. Writing `qpos="92"` for a 92° hinge
puts the door at 92 rad ≡ 232° — through the wall, 15 cm of penetration, while
the printed qpos still "looks right" in degrees. Export hinges with
`math.radians(v)`; slides in meters.

### 2. OBJ axes are imported IDENTITY in MuJoCo 3.12
MuJoCo 3.12 loads OBJ vertices **as-is** (x→x, y→y, z→z) and then re-centers the
mesh (`mesh_pos` = old center, verts become center-relative). Y-up conversion
folklore does not apply. Proven with an asymmetric probe box: file x[10,12]
y[30,32] z[50,53] → model bounds centered with the same axis assignment. Export
plain Z-up world coords; any (x,z,−y) "conversion" scatters the scene.

### 3. Resolve meshes via from_xml_path
`MjModel.from_xml_string(xml)` has no base directory, so `meshdir="meshes"`
resolves against CWD and fails with `meshes/meshes/...`. Strip keyframes to a
temp file **in the same directory** and load with `from_xml_path`.

## Validation recipe

```
python scripts/validate_mjcf.py [kitchen.xml]
```
checks: compile, `nq == njnt == expected`, every joint limited with IR ranges,
every keyframe simulates 500 steps (stability `|qvel|max`, worst contact depth),
plus per-pair contact dumps when deep. Keep the worst steady-state contact above
−5 mm; investigate anything deeper by name (exporter names geoms after their
Blender objects).

## Viewing interactively (WSLg works)

```bash
DISPLAY=:0 python -m mujoco.viewer --mjcf kitchen.xml
```
Drag the joint sliders, switch keyframes from the panel. Offscreen stills:
`mujoco.Renderer` + `MjvCamera` (needs `DISPLAY=:0` via WSLg, or EGL where a GPU
is available; set `<visual><global offwidth offheight>` ≥ render size).

## Known v1 limits (honest)

- Collision proxies are AABBs; no convex decomposition for curved parts.
- Visual meshes carry flat rgba, not baked PBR textures.
- Masses come from geom density defaults, not measured weights.
- Visual mesh + collision box pairs are independent geoms — keep
  `contype=0/conaffinity=0` on visuals so they never generate contacts.
