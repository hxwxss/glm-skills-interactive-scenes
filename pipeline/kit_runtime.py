"""kit_runtime.py — post-load articulation + light-group control.

Joint metadata is stamped onto objects as custom properties at build time
(persists inside the .blend), so state control works in ANY later Blender
process without re-running the builder.
"""

import json
import math
import bpy
from mathutils import Vector

_JOINT_MAP = None


def joint_map():
    """joint_id -> object (built once per process from custom properties)."""
    global _JOINT_MAP
    if _JOINT_MAP is None:
        m = {}
        for obj in bpy.data.objects:
            if obj.get("joint_id"):
                m[obj["joint_id"]] = obj
        _JOINT_MAP = m
    return _JOINT_MAP


def joint_info(jid):
    obj = joint_map().get(jid)
    if obj is None:
        raise KeyError(f"unknown joint {jid}")
    return dict(
        id=obj["joint_id"],
        type=obj["joint_type"],
        axis=tuple(obj["joint_axis"]),
        pivot=Vector(obj["joint_pivot"]),
        states=json.loads(obj["joint_states_json"]),
        default=float(obj.get("joint_default", 0.0)),
        limits=tuple(obj.get("joint_limits", (0.0, 0.0))),
    )


def apply_joint_state(jid, value):
    """Set a joint to a numeric state (degrees for revolute, meters prismatic)."""
    obj = joint_map().get(jid)
    if obj is None:
        raise KeyError(f"unknown joint {jid}")
    jd = joint_info(jid)
    axis = jd["axis"]
    if jd["type"] == "revolute":
        idx = axis.index(max(axis, key=abs))
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.rotation_euler[idx] = math.radians(float(value))
    else:
        obj.location = jd["pivot"] + Vector(axis) * float(value)
    obj["joint_state"] = float(value)
    return obj


def apply_joint_named(jid, state_name):
    jd = joint_info(jid)
    return apply_joint_state(jid, jd["states"][state_name])


def reset_all_joints():
    for jid, obj in joint_map().items():
        apply_joint_state(jid, float(obj.get("joint_default", 0.0)))


def set_light_group_state(group, factor):
    n = 0
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.get("light_group") == group:
            ob.data.energy = float(ob.get("base_energy", ob.data.energy)) * float(factor)
            n += 1
    return n


def get_light_group_state(group):
    tot, base = 0.0, 0.0
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.get("light_group") == group:
            tot += ob.data.energy
            base += float(ob.get("base_energy", 1.0))
    return tot / base if base > 0 else 0.0
