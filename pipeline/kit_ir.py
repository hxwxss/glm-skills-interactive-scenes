"""kit_ir.py — assembles and writes scene_ir/kitchen_scene_ir.json from the same
constants and registries the builder used (never parsed from the .blend)."""

import json
import math
import os
from datetime import datetime, timezone

import bpy
from mathutils import Vector

import kit_params as P
import kit_util as U


def _fmt_loc(obj):
    return [round(float(v), 5) for v in obj.location]


def _fmt_rot(obj):
    return [round(math.degrees(float(v)), 3) for v in obj.rotation_euler]


SPAWN_REGIONS = {
    "island_worktop": dict(box_min=[1.90, 3.40, 0.90], box_max=[2.70, 5.40, 0.96],
                           note="primary task-object spawn region"),
    "dining_table_top": dict(box_min=[5.0, 5.2, 0.75], box_max=[6.8, 6.0, 0.81]),
    "pantry_shelf_L2": dict(box_min=[8.36, 1.05, 1.11], box_max=[9.60, 1.97, 1.35]),
    "fridge_shelf_2": dict(box_min=[0.30, 0.10, 1.35], box_max=[1.20, 0.50, 1.50]),
    "dishwasher_upper_rack": dict(box_min=[0.10, 3.40, 0.55], box_max=[0.45, 3.90, 0.75]),
}

UNCERTAINTIES = [
    "Wood grain, stone speckle, plaster and brushed metal are procedural "
    "approximations, not scanned textures (visual-only).",
    "Appliance interiors are simplified but real cavities; rack wire density is "
    "a suggestion, not a full model.",
    "Collision proxies for curved props (faucet, plants, fruit) are conservative "
    "AABBs; visible meshes remain the truth for visual checks.",
    "Fruit is modeled as smooth supershapes with procedural bump skin; stem "
    "geometry simplified.",
    "Terrace puddles are thin water-film discs; drainage flow is implied by "
    "slope, not simulated.",
    "Cable paths for toaster (pantry, no outlet) are coiled behind the unit; "
    "documented as visual-only approximation.",
]


def build_ir():
    dg = bpy.context.evaluated_depsgraph_get()
    objects = {}
    for oid, rec in U.REG.objects.items():
        obj = bpy.data.objects.get(rec["blender_name"])
        r = dict(rec)
        if obj:
            r["location"] = _fmt_loc(obj)
            r["rotation_deg"] = _fmt_rot(obj)
        objects[oid] = r
    joints = {}
    for jid, jd in U.REG.joints.items():
        j = dict(jd)
        j["joint_order"] = jd.get("type")
        joints[jid] = j
    ir = {
        "schema_version": P.SCHEMA_VERSION,
        "generator": "interactive_kitchen_agent_project/scripts/build_scene.py",
        "blender_version": bpy.app.version_string,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "units": P.UNITS,
        "coordinate_convention": P.COORD_CONVENTION,
        "room": {
            "interior_dimensions": [P.ROOM_X, P.ROOM_Y, P.ROOM_H],
            "wall_thickness": P.WALL_T,
            "floor_level_z": 0.0,
            "openings": [
                dict(id="west_window", x=[0, 0], y=[P.W1_Y0, P.W1_Y1],
                     z=[P.W1_SILL, P.W1_HEAD], kind="window"),
                dict(id="terrace_glazing", x=[P.GLZ_X0, P.GLZ_X1], y=[7.4, 7.55],
                     z=[0.0, P.GLZ_HEAD], kind="sliding_glass_wall"),
                dict(id="entry_door", x=[9.8, 9.95], y=[P.ENTRY_Y0, P.ENTRY_Y1],
                     z=[0.0, P.ENTRY_H], kind="door"),
                dict(id="pantry_doorway", x=[P.PAN["door_x0"], P.PAN["door_x1"]],
                     y=[2.28, 2.4], z=[0.0, P.PAN["door_h"]], kind="sliding_panel"),
            ],
            "navigation_zones": P.NAV_ZONES,
        },
        "objects": objects,
        "joints": joints,
        "lights": {g: dict(desc=d["desc"], default=d["default"], lights=ids)
                   for g, d in P.LIGHT_GROUPS.items() for ids in [U.REG.lights.get(g, [])]},
        "cameras": U.REG.cameras,
        "collision_proxies": U.REG.proxies,
        "spawn_regions": SPAWN_REGIONS,
        "tasks": U.REG.tasks,
        "robot": dict(radius=P.ROBOT_RADIUS, route=[list(p) for p in P.ROBOT_ROUTE],
                      route_links=P.ROUTE_LINKS),
        "uncertainties": UNCERTAINTIES,
    }
    return ir


def write_ir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ir = build_ir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ir, f, indent=1)
    return ir
