"""kit_appliances.py — small appliances + appliance interior items.

Major appliances (fridge, oven, dishwasher, cooktop, hood) live in kit_cabinetry.
"""

import math
import bpy
from mathutils import Vector

import kit_params as P
import kit_util as U
from kit_util import box, cyl, revolve, torus_seg, REG

M = None


def _m(name):
    return bpy.data.materials[name]


def build_kettle():
    z0 = P.WRUN_TOP
    x, y = 0.36, 6.23
    body = revolve("kettle_body", [(0, 0), (0.085, 0.004), (0.098, 0.02),
                                   (0.104, 0.10), (0.096, 0.185), (0.088, 0.20),
                                   (0.082, 0.20), (0.088, 0.185), (0.096, 0.10),
                                   (0.090, 0.02), (0, 0.016)],
                   (x, y, z0), _m("steel_brushed"), "APPLIANCES", segs=36,
                   oid="kettle", category="appliances", role="tool")
    cyl("kettle_lid", 0.086, 0.014, (x, y, z0 + 0.207), _m("steel_dark"),
        "APPLIANCES", verts=32)
    cyl("kettle_knob", 0.018, 0.02, (x, y, z0 + 0.224), _m("steel_dark"),
        "APPLIANCES", verts=16)
    torus_seg("kettle_handle", 0.075, 0.011, (x + 0.085, y, z0 + 0.19),
              rot=(math.pi / 2, 0, 0), arc=math.pi * 0.9, mat=_m("plastic_black")
              if bpy.data.materials.get("plastic_black") else _m("rubber_black"),
              col="APPLIANCES", major=20, minor=8)
    cyl("kettle_spout", 0.016, 0.09, (x - 0.09, y, z0 + 0.15), _m("steel_brushed"),
        "APPLIANCES", rot=(0, math.radians(35), 0), verts=14)
    cable_to("kettle_cable", (x, y, z0 + 0.01), (0.021, 6.10, 1.12), r=0.0035)


def build_coffee_machine():
    z0 = P.WRUN_TOP
    x, y = 0.34, 5.92
    box("coffee_body", (0.24, 0.38, 0.36), (x, y, z0 + 0.19), _m("steel_dark"),
        "APPLIANCES", bevel=0.025, oid="coffee_machine", category="appliances",
        role="fixture", mass=9)
    box("coffee_top", (0.22, 0.30, 0.06), (x, y + 0.02, z0 + 0.395),
        _m("steel_brushed"), "APPLIANCES", bevel=0.015)
    box("coffee_drip", (0.20, 0.12, 0.03), (x, y - 0.09, z0 + 0.045),
        _m("steel_brushed"), "APPLIANCES", bevel=0.004)
    cyl("coffee_portafilter", 0.036, 0.05, (x, y - 0.09, z0 + 0.13),
        _m("steel_brushed"), "APPLIANCES", verts=24)
    cyl("coffee_pf_handle", 0.014, 0.11, (x + 0.10, y - 0.09, z0 + 0.125),
        _m("plastic_black") if bpy.data.materials.get("plastic_black")
        else _m("rubber_black"), "APPLIANCES", rot=(0, math.pi / 2, 0), verts=12)
    cyl("coffee_gauge", 0.028, 0.012, (x - 0.115, y + 0.10, z0 + 0.28),
        _m("display_knob"), "APPLIANCES", rot=(0, math.pi / 2, 0), verts=20)
    cable_to("coffee_cable", (x, y + 0.15, z0 + 0.01), (0.021, 6.10, 1.12), r=0.004)


def build_toaster():
    z0 = P.PAN["counter_z"]
    x, y = 9.10, 0.50
    box("toaster_body", (0.20, 0.30, 0.19), (x, y, z0 + 0.095),
        _m("steel_brushed"), "APPLIANCES", bevel=0.035, oid="toaster",
        category="appliances", role="fixture", mass=2)
    for i, dy in enumerate((-0.06, 0.06)):
        box(f"toaster_slot_{i}", (0.14, 0.03, 0.02), (x, y + dy, z0 + 0.19),
            _m("rubber_black"), "APPLIANCES", bevel=0.003)
    cyl("toaster_lever", 0.008, 0.05, (x + 0.10, y - 0.12, z0 + 0.12),
        _m("steel_dark"), "APPLIANCES", verts=10)
    # coiled cable behind (no outlet in pantry — honest detail)
    for i in range(3):
        torus_seg(f"toaster_cable_{i}", 0.045, 0.0035, (x + 0.02, y - 0.22, z0 + 0.008 + i * 0.012),
                  rot=(0, 0, 0.4 * i), arc=math.tau * 0.8, mat=_m("rubber_black"),
                  col="APPLIANCES", major=18, minor=6)


def build_fridge_contents():
    # milk carton on shelf 1 (z 0.98)
    mx, my = 0.52, 0.28
    box("milk_carton", (0.085, 0.085, 0.22), (mx, my, 1.477), _m("milk_carton"),
        "APPLIANCES", bevel=0.006, oid="milk_carton", category="props",
        role="grasp_target", static=False, mass=1.0)
    box("milk_carton_roof", (0.085, 0.085, 0.05), (mx, my, 1.602),
        _m("milk_carton"), "APPLIANCES", bevel=0.004, rot=(0, 0.0, 0))
    # water bottles on shelf 0 (z 0.62)
    for i in range(2):
        revolve(f"fridge_bottle_{i}",
                [(0, 0), (0.033, 0.002), (0.036, 0.03), (0.036, 0.16),
                 (0.020, 0.20), (0.014, 0.225), (0, 0.227)],
                (0.30 + i * 0.10, 0.30, 1.377), _m("glass_low_iron"), "APPLIANCES",
                segs=20, oid=f"fridge_bottle_{i}", category="props",
                role="grasp_target", static=False)
        cyl(f"fridge_bottle_cap_{i}", 0.015, 0.02, (0.30 + i * 0.10, 0.30, 1.612),
            _m("plastic_blue"), "APPLIANCES", verts=14)


def cable_to(name, start, end, r=0.004, sag=0.25):
    """Drooping power cable from appliance to outlet (bezier-ish polyline)."""
    pts = []
    n = 10
    for i in range(n + 1):
        t = i / n
        p = Vector(start) * (1 - t) + Vector(end) * t
        p.z -= sag * math.sin(math.pi * t) ** 1.5
        pts.append(tuple(p))
    cu = U.curve_tube(name, pts, r, mat=_m("rubber_black"), col="APPLIANCES")


def build_all_appliances():
    build_kettle()
    build_coffee_machine()
    build_toaster()
    build_fridge_contents()
