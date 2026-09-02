"""export_mjcf.py — export the kitchen scene to MuJoCo MJCF (sim-ready layer).

Run inside Blender:
  blender --background interactive_kitchen_final.blend --python scripts/export_mjcf.py

Outputs sim_ready/kitchen_mjcf/:
  kitchen.xml      — collision boxes (group 3, sim-only) + visual meshes (group 1)
  meshes/*.obj     — static structure per material class + one file per moving part

Articulated part OBJs are written with vertices offset by -pivot (body frame) and
Vertices stay in Blender world axes (MuJoCo 3.12 imports OBJ as-is).

The .blend is never modified.
"""

import bpy
import json
import os
import sys
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

OUT_DIR = os.path.join(PROJECT, "sim_ready", "kitchen_mjcf")
MESH_DIR = os.path.join(OUT_DIR, "meshes")

STATIC_COLLECTIONS = ("ARCH", "CABINETRY", "APPLIANCES", "FURNITURE", "PROPS")
EXCLUDE_PREFIX = ("PROXY", "city_", "guard_", "terrace_shrub", "puddle")
MIN_VOLUME = 0.0008
MIN_DIM = 0.01

# material-name keyword -> (asset key, rgba)
PALETTE = [
    ("oak_floor", (0.45, 0.31, 0.19, 1)),
    ("oak", (0.52, 0.38, 0.24, 1)),
    ("stone_worktop", (0.20, 0.20, 0.21, 1)),
    ("stone", (0.62, 0.60, 0.57, 1)),
    ("cab_front", (0.72, 0.70, 0.64, 1)),
    ("cab_body", (0.50, 0.49, 0.46, 1)),
    ("steel_brushed", (0.58, 0.58, 0.60, 1)),
    ("steel_dark", (0.12, 0.12, 0.13, 1)),
    ("steel", (0.58, 0.58, 0.60, 1)),
    ("bronze", (0.45, 0.28, 0.15, 1)),
    ("brass", (0.62, 0.48, 0.28, 1)),
    ("glass", (0.75, 0.85, 0.85, 0.35)),
    ("ceramic", (0.86, 0.85, 0.82, 1)),
    ("linen", (0.72, 0.68, 0.60, 1)),
    ("leaf", (0.25, 0.40, 0.16, 1)),
    ("plastic", (0.5, 0.5, 0.5, 1)),
    ("cardboard", (0.55, 0.42, 0.28, 1)),
    ("cereal", (0.86, 0.55, 0.25, 1)),
    ("paper", (0.88, 0.86, 0.80, 1)),
    ("rubber", (0.08, 0.08, 0.08, 1)),
    ("cooktop", (0.05, 0.05, 0.06, 1)),
    ("plaster", (0.84, 0.82, 0.78, 1)),
    ("bin", (0.35, 0.36, 0.37, 1)),
    ("wet", (0.30, 0.31, 0.32, 1)),
    ("doormat", (0.35, 0.32, 0.28, 1)),
    ("chalk", (0.08, 0.09, 0.085, 1)),
    ("milk", (0.90, 0.90, 0.88, 1)),
    ("art", (0.55, 0.52, 0.45, 1)),
]


def mat_bucket(obj):
    if obj.data is None or not obj.data.materials or obj.data.materials[0] is None:
        return "misc", (0.6, 0.5, 0.4, 1)
    name = obj.data.materials[0].name
    for key, rgba in PALETTE:
        if key in name:
            return key, rgba
    return "misc", (0.6, 0.5, 0.4, 1)


def world_aabb(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def xml_vec(v):
    return " ".join(f"{x:.5f}" for x in v)


def joint_meta():
    out = {}
    for obj in bpy.data.objects:
        if obj.get("joint_id"):
            out[obj["joint_id"]] = dict(
                obj=obj, jid=obj["joint_id"], jtype=obj["joint_type"],
                axis=tuple(obj["joint_axis"]), pivot=Vector(obj["joint_pivot"]),
                states=json.loads(obj["joint_states_json"]),
                default=float(obj.get("joint_default", 0.0)),
                limits=tuple(obj.get("joint_limits", (0.0, 0.0))),
            )
    return out


def collect_articulated(joints):
    moving = set()
    for jd in joints.values():
        moving.add(jd["obj"].name)
        for ch in jd["obj"].children_recursive:
            moving.add(ch.name)
    return moving


def export_objs(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.wm.obj_export(
        filepath=path, export_selected_objects=True, apply_modifiers=True,
        export_materials=False, export_uv=False, export_normals=False,
        forward_axis="Y", up_axis="Z")


def shift_obj_yup(path, offset=None):
    """Post-process OBJ: subtract offset (body frame) and convert Z-up -> Y-up.

    Blender (x, y, z) -> file (x, z, -y); MuJoCo loads Y-up OBJ back to Z-up.
    """
    lines = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("v "):
                parts = ln.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                if offset is not None:
                    x, y, z = x - offset[0], y - offset[1], z - offset[2]
                # MuJoCo 3.12 imports OBJ vertices as-is (identity axes)
                lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")
            else:
                lines.append(ln.rstrip("\n"))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    os.makedirs(MESH_DIR, exist_ok=True)
    joints = joint_meta()
    moving = collect_articulated(joints)

    static_geoms = []
    mesh_assets = []
    visual_geoms = []
    keyframes = {}

    # -------- statics: one visual mesh per material bucket + collision boxes ----
    buckets = {}
    for cname in STATIC_COLLECTIONS:
        col = bpy.data.collections.get(cname)
        if not col:
            continue
        for obj in col.objects:
            if obj.type != "MESH" or obj.name.startswith(EXCLUDE_PREFIX):
                continue
            if obj.name in moving:
                continue
            mn, mx = world_aabb(obj)
            size = mx - mn
            if min(size) < MIN_DIM or size.x * size.y * size.z < MIN_VOLUME:
                continue
            key, rgba = mat_bucket(obj)
            if obj.name == "ceiling_slab":
                key = None      # collision-only: keep the interior visible
            if key is None:
                continue
            buckets.setdefault(key, {"objs": [], "rgba": rgba})
            buckets[key]["objs"].append(obj)
            ctr = (mn + mx) / 2
            static_geoms.append(
                f'      <geom name="c_{key}_{len(static_geoms)}" type="box" '
                f'pos="{xml_vec(ctr)}" size="{xml_vec(size / 2)}" '
                f'contype="1" conaffinity="1" group="3" rgba="0 0 0 0"/>')
    for key, b in sorted(buckets.items()):
        path = os.path.join(MESH_DIR, f"statics_{key}.obj")
        export_objs(b["objs"], path)
        shift_obj_yup(path)
        mesh_assets.append(
            f'    <mesh name="statics_{key}" file="statics_{key}.obj"/>')
        r, g, bl, a = b["rgba"]
        visual_geoms.append(
            f'      <geom name="v_statics_{key}" type="mesh" mesh="statics_{key}" '
            f'contype="0" conaffinity="0" group="1" rgba="{r} {g} {bl} {a}"/>')

    # ---------------- articulated bodies ----------------
    joint_elems = []
    for jid, jd in sorted(joints.items()):
        pivot = jd["pivot"]
        parts = [jd["obj"]] + [ch for ch in jd["obj"].children_recursive
                               if ch.type == "MESH"]
        path = os.path.join(MESH_DIR, f"{jid}.obj")
        export_objs(parts, path)
        shift_obj_yup(path, offset=pivot)
        mesh_assets.append(f'    <mesh name="m_{jid}" file="{jid}.obj"/>')

        mrgba = mat_bucket(jd["obj"])[1]
        r, g, bl, a = mrgba
        vgeom = (f'      <geom name="v_{jid}" type="mesh" mesh="m_{jid}" '
                 f'contype="0" conaffinity="0" group="1" rgba="{r} {g} {bl} {a}"/>')

        geom_lines = []
        gi = 0
        for p in parts:
            mn, mx = world_aabb(p)
            size = mx - mn
            if min(size) < 0.002 or size.x * size.y * size.z < 1e-5:
                continue
            ctr = (mn + mx) / 2 - pivot
            geom_lines.append(
                f'      <geom name="c_{jid}_{gi}" type="box" pos="{xml_vec(ctr)}" '
                f'size="{xml_vec(size / 2)}" contype="1" conaffinity="1" '
                f'group="3" rgba="0 0 0 0"/>')
            gi += 1

        jtype = "hinge" if jd["jtype"] == "revolute" else "slide"
        fl = ' frictionloss="0.8"' if jtype == "slide" else ""
        lo, hi = sorted((float(jd["limits"][0]), float(jd["limits"][1])))
        joint_elems.append(
            f'    <body name="{jid}" pos="{xml_vec(pivot)}">\n'
            f'      <joint name="{jid}" type="{jtype}" axis="{xml_vec(jd["axis"])}" '
            f'range="{lo:.4f} {hi:.4f}" damping="0.5"{fl}/>\n'
            + vgeom + "\n" + "\n".join(geom_lines) + "\n    </body>")

        for state_name, val in jd["states"].items():
            keyframes.setdefault(state_name, {})[jid] = float(val)

    # ---------------- keyframes (qpos flat, radians for hinges) ----------------
    import math as _m
    all_jids = sorted(joints.keys())
    kf_lines = []
    for kname in ("closed", "half", "open"):
        vals = []
        for jid in all_jids:
            v = keyframes.get(kname, {}).get(jid, joints[jid]["default"])
            if joints[jid]["jtype"] == "revolute":
                v = _m.radians(v)
            vals.append(v)
        kf_lines.append(f'    <key name="{kname}" qpos="'
                        + " ".join(f"{v:.6f}" for v in vals) + '"/>')

    xml = f"""<mujoco model="interactive_kitchen">
  <compiler angle="degree" coordinate="local" meshdir="meshes"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <visual>
    <global offwidth="1920" offheight="1080"/>
  </visual>
  <asset>
{chr(10).join(mesh_assets)}
  </asset>
  <contact>
    <exclude body1="pantry_slide" body2="world"/>
  </contact>
  <worldbody>
    <geom name="floor" type="plane" size="30 30 0.1" rgba="0.45 0.38 0.30 1" pos="0 0 0"/>
{chr(10).join(visual_geoms)}
{chr(10).join(static_geoms)}
{chr(10).join(joint_elems)}
  </worldbody>
  <actuator/>
  <keyframe>
{chr(10).join(kf_lines)}
  </keyframe>
</mujoco>
"""
    out_path = os.path.join(OUT_DIR, "kitchen.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml)
    n_obj = len([x for x in os.listdir(MESH_DIR) if x.endswith(".obj")])
    print(f"[mjcf] static geoms: {len(static_geoms)}, joints: {len(joints)}, "
          f"mesh assets: {n_obj}")
    print(f"[mjcf] wrote {out_path}")
    print("MJCF_OK")


main()
