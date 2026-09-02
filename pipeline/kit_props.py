"""kit_props.py — everyday task props, pantry goods, plants, art, narrative dressing."""

import math
import random
import bpy
from mathutils import Vector

import kit_params as P
import kit_util as U
from kit_util import box, cyl, revolve, torus_seg, REG

RNG = random.Random(7)


def _m(name):
    return bpy.data.materials[name]


ISL_TOP = P.ISL["top"]


def _on_island(x, y):
    return x, y, ISL_TOP


# ------------------------------------------------------------------ island story
def build_island_props():
    z = ISL_TOP
    # used cereal bowl + spoon
    revolve("bowl_cereal", [(0, 0), (0.062, 0.002), (0.070, 0.012), (0.095, 0.062),
                            (0.098, 0.070), (0.092, 0.072), (0.066, 0.020),
                            (0.052, 0.010), (0, 0.008)],
            (2.12, 4.58, z), _m("ceramic_white"), "PROPS", segs=36,
            oid="bowl_cereal", category="props", role="grasp_target", static=False,
            mass=0.35)
    revolve("bowl_cereal_milk", [(0, 0.012), (0.055, 0.014), (0.060, 0.020),
                                 (0, 0.022)],
            (2.12, 4.58, z), _m("ceramic_white"), "PROPS", segs=24)
    spoon("spoon", (2.26, 4.70, z + 0.004), math.radians(70))
    # coaster + mug
    cyl("coaster_a", 0.052, 0.007, (2.34, 3.78, z + 0.0035), _m("oak_dark"),
        "PROPS", verts=28, oid="coaster_a", category="props", role="grasp_target",
        static=False)
    build_mug("mug_coffee", 2.34, 3.78, z + 0.007, yaw=25)
    # open cereal box
    build_cereal_box("cereal_box", (2.56, 4.16, z), yaw=-14, open_flaps=True,
                     oid="cereal_box")
    # napkin
    box("napkin_1", (0.14, 0.14, 0.004), (2.44, 3.52, z + 0.002), _m("linen"),
        "PROPS", bevel=0.001, rot=(0, 0, math.radians(18)))
    # dish towel folded on island corner
    box("dish_towel", (0.20, 0.15, 0.025), (2.62, 5.38, z + 0.0125),
        _m("linen_dark"), "PROPS", bevel=0.008, oid="dish_towel", category="props",
        role="grasp_target", static=False)
    # fruit bowl + fruit
    revolve("fruit_bowl", [(0, 0), (0.11, 0.004), (0.135, 0.05), (0.14, 0.085),
                           (0.132, 0.088), (0.125, 0.055), (0.095, 0.012),
                           (0, 0.010)],
            (2.48, 5.10, z), _m("ceramic_putty"), "PROPS", segs=40,
            oid="fruit_bowl", category="props", role="grasp_target", static=False)
    for i, (fx, fy, fr, h) in enumerate(((2.44, 5.08, 0.038, 0.034),
                                         (2.52, 5.12, 0.036, 0.030),
                                         (2.47, 5.15, 0.034, 0.028))):
        apple = U.sphere(f"apple_{i+1}", 0.037, (fx, fy, z + 0.045 + h * 0.2),
                         _m("apple_skin"), "PROPS", scale=(1, 1, 0.92),
                         oid=f"apple_{i+1}", category="props", role="grasp_target",
                         static=False)
        cyl(f"apple_stem_{i+1}", 0.0025, 0.025, (fx, fy, z + 0.082), _m("bark"),
            "PROPS", verts=8)
    for i, (fx, fy) in enumerate(((2.53, 5.05), (2.44, 5.14))):
        U.sphere(f"orange_{i+1}", 0.034, (fx, fy, z + 0.105),
                 _m("orange_skin"), "PROPS",
                 oid=f"orange_{i+1}", category="props", role="grasp_target",
                 static=False)
    # banana on counter near board (west run) — gentle arc
    pts = []
    for i in range(13):
        t = i / 12
        a = math.pi * (0.25 + 0.5 * t)
        pts.append((0.33 + 0.09 * math.sin(a * 2 - 0.8), 4.38 + 0.16 * t,
                    P.WRUN_TOP + 0.030 + 0.022 * math.sin(math.pi * t)))
    U.curve_tube("banana", pts, 0.016, mat=_m("banana_skin"), col="PROPS")
    REG.add_object("banana", bpy.data.objects["banana"], "props", "grasp_target",
                   (0.2, 0.18, 0.05), "banana_skin", False)
    # cutting board leaning against backsplash + butter knife
    box("cutting_board", (0.014, 0.34, 0.26), (0.09, 4.42, P.WRUN_TOP + 0.13),
        _m("oak"), "PROPS", bevel=0.006, rot=(0, math.radians(-9), 0),
        oid="cutting_board", category="props", role="grasp_target", static=False,
        mass=1.2)
    box("butter_knife", (0.19, 0.022, 0.006), (0.30, 4.62, P.WRUN_TOP + 0.004),
        _m("steel_brushed"), "PROPS", bevel=0.002, rot=(0, 0, math.radians(-24)),
        oid="butter_knife", category="props", role="grasp_target", static=False)
    # recycling waiting on island: bottle + can
    revolve("bottle_recycling",
            [(0, 0), (0.032, 0.002), (0.035, 0.04), (0.033, 0.12), (0.016, 0.17),
             (0.013, 0.205), (0.017, 0.215), (0.013, 0.235), (0, 0.237)],
            (2.20, 3.42, z), _m("glass_low_iron"), "PROPS", segs=22,
            oid="bottle_recycling", category="props", role="grasp_target",
            static=False, mass=0.04)
    cyl("bottle_cap", 0.014, 0.014, (2.20, 3.42, z + 0.243), _m("plastic_blue"),
        "PROPS", verts=14)
    cyl("can_recycling", 0.033, 0.115, (2.66, 4.62, z + 0.0575),
        _m("steel_brushed"), "PROPS", verts=24, oid="can_recycling",
        category="props", role="grasp_target", static=False, mass=0.015)
    U.add_bevel(bpy.data.objects["can_recycling"], 0.006)


def spoon(name, loc, yaw):
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((-0.075 + 0.13 * t, 0, 0.004 if t < 0.6 else 0.004 + 0.006 * (t - 0.6) * 5))
    U.curve_tube(f"{name}_handle", pts, 0.005, loc=loc, mat=_m("steel_brushed"),
                 col="PROPS")
    bowl = U.sphere(f"{name}_bowl", 0.014, (0.065, 0, 0.006), _m("steel_brushed"),
                    "PROPS", scale=(1.5, 1, 0.45))
    bowl.parent = bpy.data.objects[f"{name}_handle"]
    bowl.location = (0.065, 0, 0.006)
    h = bpy.data.objects[f"{name}_handle"]
    h.rotation_euler = (0, 0, yaw)
    REG.add_object(name, h, "props", "grasp_target", (0.2, 0.03, 0.015),
                   "steel_brushed", False)


def build_mug(name, x, y, z, yaw=0):
    revolve(f"{name}_body", [(0, 0), (0.036, 0.002), (0.040, 0.018), (0.040, 0.088),
                             (0.037, 0.092), (0.034, 0.092), (0.034, 0.018),
                             (0, 0.010)],
            (x, y, z), _m("ceramic_putty"), "PROPS", segs=32,
            oid=name, category="props", role="grasp_target", static=False, mass=0.3)
    tor = torus_seg(f"{name}_handle", 0.030, 0.006, (x + 0.036, y, z + 0.05),
                    rot=(math.pi / 2, 0, 0), arc=math.pi * 1.1, mat=_m("ceramic_putty"),
                    col="PROPS", major=18, minor=8)
    tor.rotation_euler = (math.pi / 2, 0, math.radians(yaw))
    bpy.data.objects[f"{name}_body"].rotation_euler = (0, 0, math.radians(yaw))
    tor.location = (x + 0.036 * math.cos(math.radians(yaw)),
                    y + 0.036 * math.sin(math.radians(yaw)), z + 0.05)
    cyl(f"{name}_coffee", 0.031, 0.004, (x, y, z + 0.080), _m("cooktop_glass"),
        "PROPS", verts=24)


def build_cereal_box(name, loc, yaw=0, open_flaps=False, oid=None):
    w, d, h = 0.16, 0.07, 0.30
    root = bpy.data.objects.new(name + "_root", None)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw))
    bpy.context.scene.collection.objects.link(root)
    U.link(root, "PROPS")
    body = box(f"{name}_body", (w, d, h * 0.92), (0, 0, h * 0.46),
               _m("cereal_graphic"), "PROPS", bevel=0.004, parent=root)
    if open_flaps:
        for i, (rx, off) in enumerate(((-1.0, -w / 2), (1.25, w / 2))):
            fl = box(f"{name}_flap{i}", (w * 0.98, d, 0.004), (0, 0, 0),
                     _m("cereal_graphic"), "PROPS", bevel=0.001, parent=root)
            fl.data.transform(__import__("mathutils").Matrix.Translation(
                ((w * 0.98) / 2 if off > 0 else -(w * 0.98) / 2, 0, 0)))
            fl.location = (0, 0, h * 0.92)
            fl.rotation_euler = (rx, 0, 0)
    if oid:
        REG.add_object(oid, body, "props", "grasp_target", (w, d, h),
                       "cereal_graphic", False, mass=0.5, parent=name + "_root")
    return root


# ------------------------------------------------------------------ sink zone
def build_sink_props():
    z = P.WRUN_TOP
    box("sponge", (0.09, 0.06, 0.028), (0.30, 2.58, z + 0.014), _m("ceramic_putty")
        if False else _m("linen_dark"), "PROPS", bevel=0.008, oid="sponge",
        category="props", role="grasp_target", static=False)
    revolve("soap_dispenser", [(0, 0), (0.035, 0.002), (0.042, 0.06),
                               (0.038, 0.14), (0.020, 0.155), (0.014, 0.16),
                               (0, 0.162)],
            (0.16, 2.55, z), _m("ceramic_white"), "PROPS", segs=28,
            oid="soap_dispenser", category="props", role="grasp_target",
            static=False, mass=0.4)
    cyl("soap_pump", 0.008, 0.05, (0.16, 2.55, z + 0.185), _m("steel_dark"),
        "PROPS", verts=12)
    # drying rack with plates + glass (prep counter, near sink)
    rx, ry = 0.34, 4.02
    box("drying_rack_base", (0.36, 0.26, 0.012), (rx, ry, z + 0.006),
        _m("steel_brushed"), "PROPS", bevel=0.003)
    for i in range(6):
        box(f"drying_rack_wire_{i}", (0.006, 0.26, 0.05),
            (rx - 0.15 + i * 0.06, ry, z + 0.035), _m("steel_brushed"), "PROPS",
            bevel=0.001)
    for i in range(2):
        revolve(f"plate_drying_{i+1}",
                [(0, 0.002), (0.10, 0.006), (0.118, 0.014), (0.10, 0.018),
                 (0, 0.020)],
                (rx - 0.06 + i * 0.09, ry, z + 0.072 + i * 0.022),
                _m("ceramic_white"), "PROPS", segs=32,
                oid=f"plate_drying_{i+1}" if i == 0 else None, category="props",
                role="grasp_target", static=False)
    revolve("glass_drying", [(0, 0), (0.031, 0.002), (0.034, 0.10), (0.031, 0.102),
                             (0.028, 0.015), (0, 0.012)],
            (rx + 0.13, ry + 0.02, z + 0.052), _m("glass_low_iron"), "PROPS", segs=28,
            oid="glass_drying", category="props", role="grasp_target", static=False)


# ------------------------------------------------------------------ pantry goods
def build_pantry_props():
    rng = RNG
    jar_cols = ("ceramic_white", "plastic_blue", "plastic_green", "linen_dark",
                "ceramic_putty")
    z0 = P.PAN["counter_z"]
    # jars on west shelves + east shelves
    spots = []
    for sz in (P.PAN["shelf_zs"][0], P.PAN["shelf_zs"][1]):
        for k in range(3):
            spots.append((8.47, 1.15 + k * 0.28, sz + 0.014))
            spots.append((9.62, 1.15 + k * 0.28, sz + 0.014))
    for i, (jx, jy, jz) in enumerate(spots[:8]):
        jr = rng.uniform(0.042, 0.055)
        jh = rng.uniform(0.13, 0.19)
        revolve(f"jar_{i+1}", [(0, 0), (jr, 0.003), (jr, jh), (jr - 0.006, jh),
                               (jr - 0.006, 0.012), (0, 0.010)],
                (jx, jy, jz), _m("glass_low_iron"), "PROPS", segs=24,
                oid=f"jar_{i+1}", category="props", role="grasp_target",
                static=False)
        cyl(f"jar_{i+1}_content", jr - 0.008, jh * rng.uniform(0.5, 0.8),
            (jx, jy, jz + jh * 0.35), _m(jar_cols[i % len(jar_cols)]), "PROPS",
            verts=20)
        cyl(f"jar_{i+1}_lid", jr + 0.004, 0.016, (jx, jy, jz + jh + 0.008),
            _m("steel_dark"), "PROPS", verts=22)
    # dry-goods boxes on shelves
    for i in range(4):
        bx = 9.64 if i % 2 == 0 else 8.45
        by = 1.05 + (i // 2) * 0.45
        bz = P.PAN["shelf_zs"][2] + 0.014 if i < 2 else P.PAN["shelf_zs"][1] + 0.014
        build_cereal_box(f"pantry_box_{i+1}", (bx, by, bz),
                         yaw=0 if bx > 9.5 else rng.uniform(-15, 15),
                         oid=f"pantry_box_{i+1}")
    # backup cereal box on shelf level 2 (task object)
    build_cereal_box("cereal_box_pantry", (8.47, 1.75, P.PAN["shelf_zs"][1] + 0.014),
                     yaw=8, oid="cereal_box_pantry")
    # snack boxes in pantry drawer (visible when open)
    for i in range(3):
        box(f"pantry_snack_{i}", (0.16, 0.11, 0.05),
            (9.0 - 0.3 + i * 0.3, P.PAN["y0"] + 0.40, 0.60), _m("cardboard"),
            "PROPS", bevel=0.004)


# ------------------------------------------------------------------ entry zone
def build_entry_props():
    # console on pantry partition north face
    x0, x1 = 9.46, 9.76
    yc = 2.90
    h = 0.80
    box("console_top", (x1 - x0, 0.60, 0.03), ((x0 + x1) / 2, yc, h),
        _m("oak"), "PROPS", bevel=0.004, oid="console_table", category="furniture",
        role="fixture")
    for ly in (yc - 0.24, yc + 0.24):
        box(f"console_leg_{ly}", (0.26, 0.03, h - 0.03), ((x0 + x1) / 2, ly,
            (h - 0.03) / 2), _m("oak_dark"), "PROPS", bevel=0.002)
    # key tray + keys
    revolve("key_tray", [(0, 0), (0.10, 0.004), (0.115, 0.024), (0.112, 0.026),
                         (0.098, 0.008), (0, 0.006)],
            (9.58, 3.06, h + 0.015), _m("steel_dark"), "PROPS", segs=28,
            oid="key_tray", category="props", role="grasp_target", static=False)
    torus_seg("keys_ring", 0.022, 0.003, (9.58, 3.06, h + 0.055),
              rot=(math.pi / 2, 0, 0.4), arc=math.tau, mat=_m("bronze"), col="PROPS",
              major=16, minor=5)
    box("keys_fob", (0.035, 0.012, 0.006), (9.58, 3.06, h + 0.050), _m("rubber_black"),
        "PROPS", bevel=0.002, rot=(0, 0, 0.7), oid="keys", category="props",
        role="grasp_target", static=False)
    # notebook + phone
    box("notebook", (0.22, 0.16, 0.022), (9.60, 2.76, h + 0.026), _m("linen_dark"),
        "PROPS", bevel=0.003, rot=(0, 0, math.radians(82)), oid="notebook",
        category="props", role="grasp_target", static=False)
    box("notebook_pages", (0.20, 0.145, 0.014), (9.60, 2.76, h + 0.022),
        _m("paper"), "PROPS", bevel=0.001)
    box("phone", (0.142, 0.068, 0.008), (9.60, 3.20, h + 0.019),
        _m("steel_dark"), "PROPS", bevel=0.002, rot=(0, 0, math.radians(68)),
        oid="phone", category="props", role="grasp_target", static=False)
    # framed art on south wall + sideboard books
    for i, (ax, aw, ah, mat) in enumerate(((3.55, 0.55, 0.70, "art_a"),
                                           (4.45, 0.42, 0.55, "art_b"))):
        box(f"art_frame_{i}", (aw, 0.035, ah), (ax, 0.0175 + 0.0, 1.55),
            _m("oak_dark"), "PROPS", bevel=0.004)
        box(f"art_canvas_{i}", (aw - 0.06, 0.012, ah - 0.06), (ax, 0.040, 1.55),
            _m(mat), "PROPS", bevel=0)
    for i in range(3):
        box(f"cookbook_{i}", (0.20 - i * 0.015, 0.15 - i * 0.012, 0.030),
            (2.30, 3.38, 0.435 + 0.03 + i * 0.031 + 0.015),
            _m(["art_a", "linen_dark", "plastic_red"][i]), "PROPS", bevel=0.003,
            rot=(0, 0, math.radians(i * 5 - 5)))
    box("sideboard_book", (0.035, 0.22, 0.30), (6.55, 0.23, 0.78 + 0.15 + 0.01),
        _m("art_b"), "PROPS", bevel=0.004, rot=(math.radians(9), 0, 0))
    # wall keypad near south tall run (light control interact point)
    box("keypad_plate", (0.09, 0.012, 0.12), (2.95, 0.016, 1.10),
        _m("ceramic_white"), "PROPS", bevel=0.003)
    for i in range(2):
        box(f"keypad_btn_{i}", (0.03, 0.006, 0.03), (2.95, 0.026, 1.12 - i * 0.045),
            _m("display_knob"), "PROPS", bevel=0.001)


# ------------------------------------------------------------------ plants
def build_plants():
    rng = RNG
    # olive tree near glazing
    px, py = 4.35, 6.95
    revolve("olive_pot", [(0, 0), (0.16, 0.004), (0.19, 0.10), (0.21, 0.34),
                          (0.195, 0.35), (0.175, 0.10), (0, 0.06)],
            (px, py, 0.0), _m("ceramic_putty"), "PROPS", segs=32,
            oid="plant_olive", category="props", role="visual_only")
    cyl("olive_soil", 0.175, 0.02, (px, py, 0.345), _m("soil"), "PROPS", verts=28)
    trunk_pts = [(px, py, 0.35), (px + 0.02, py + 0.01, 0.55), (px - 0.01, py, 0.85),
                 (px + 0.01, py - 0.02, 1.15)]
    U.curve_tube("olive_trunk", trunk_pts, 0.028, mat=_m("bark"), col="PROPS")
    for i in range(7):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.03, 0.12)
        s = rng.uniform(0.12, 0.15)
        U.sphere(f"olive_crown_{i}", s,
                 (px + 0.10 + r * math.cos(a), py + 0.08 + r * math.sin(a),
                  1.62 + rng.uniform(0.0, 0.30)),
                 _m("leaf"), "PROPS", scale=(1, 1, 0.8))
    # herb pot on west windowsill
    hx, hy = 0.0, 2.70
    revolve("herb_pot", [(0, 0), (0.05, 0.002), (0.062, 0.05), (0.070, 0.10),
                         (0.064, 0.105), (0.056, 0.05), (0, 0.03)],
            (hx, hy, P.W1_SILL + 0.015), _m("ceramic_white"), "PROPS", segs=24)
    for i in range(6):
        a = rng.uniform(0, math.tau)
        U.sphere(f"herb_leaf_{i}", 0.035,
                 (hx + 0.02 * math.cos(a), hy + 0.02 * math.sin(a),
                  P.W1_SILL + 0.16 + rng.uniform(0, 0.06)),
                 _m("leaf"), "PROPS", scale=(0.6, 0.6, 1.4))
    # terrace shrubs
    for i, sx in enumerate((4.1, 6.9)):
        for k in range(4):
            U.sphere(f"terrace_shrub_{i}_{k}", rng.uniform(0.14, 0.22),
                     (sx + rng.uniform(-0.3, 0.3), 8.9 + rng.uniform(-0.1, 0.1),
                      P.TER_Z + 0.48 + rng.uniform(0, 0.18)),
                     _m("leaf"), "EXTERIOR", scale=(1.1, 1.1, 0.9))
    # smoke detector
    cyl("smoke_detector", 0.055, 0.03, (4.9, 3.7, 2.975), _m("ceramic_white"),
        "ARCH", verts=20)


# ------------------------------------------------------------------ pendants
def build_pendants():
    em = _m("emissive_soft")
    bronze = _m("bronze")
    # island pendants (task group)
    cord_m = bpy.data.materials["steel_dark"]
    for i, (px, py) in enumerate(P.PENDANT_ISLAND):
        cyl(f"pendant_island_{i}_cord", 0.003, 1.15, (px, py, 2.425), cord_m,
            "LIGHTING", verts=8)
        revolve(f"pendant_island_{i}_shade",
                [(0, 0), (0.06, 0.012), (0.12, 0.10), (0.15, 0.21), (0.155, 0.22),
                 (0.148, 0.22), (0.11, 0.11), (0.052, 0.016), (0, 0.006)],
                (px, py, P.PEND_DROP), em, "LIGHTING", segs=36)
        cyl(f"pendant_island_{i}_bulb", 0.022, 0.012, (px, py, P.PEND_DROP + 0.025),
            em, "LIGHTING", verts=14)
    # dining pendants (dining group)
    for i, px in enumerate(P.PENDANT_DINING_XS):
        py = P.DINING["cy"]
        cyl(f"pendant_dining_{i}_cord", 0.003, 1.05, (px, py, 2.475), cord_m,
            "LIGHTING", verts=8)
        revolve(f"pendant_dining_{i}_shade",
                [(0, 0), (0.07, 0.014), (0.13, 0.11), (0.165, 0.23), (0.17, 0.24),
                 (0.162, 0.24), (0.12, 0.12), (0.06, 0.018), (0, 0.007)],
                (px, py, P.PEND_DROP + 0.02), em, "LIGHTING", segs=36)
        cyl(f"pendant_dining_{i}_bulb", 0.024, 0.014, (px, py, P.PEND_DROP + 0.05),
            em, "LIGHTING", verts=14)
    # runner on dining table
    box("table_runner", (1.6, 0.32, 0.006), (P.DINING["cx"], P.DINING["cy"] - 0.12,
        P.DINING["top"] + 0.003), _m("linen"), "PROPS", bevel=0.002)
    # used breakfast setting on table: plate + mug + napkin (south side)
    revolve("plate_table", [(0, 0.002), (0.10, 0.006), (0.118, 0.014),
                            (0.10, 0.018), (0, 0.020)],
            (6.38, 5.28, P.DINING["top"] + 0.005), _m("ceramic_white"), "PROPS",
            segs=32, oid="plate_table", category="props", role="grasp_target",
            static=False)
    build_mug("mug_table", 6.62, 5.24, P.DINING["top"] + 0.006, yaw=-40)
    box("napkin_2", (0.14, 0.14, 0.004), (6.16, 5.32, P.DINING["top"] + 0.004),
        _m("linen_dark"), "PROPS", bevel=0.001, rot=(0, 0, math.radians(-24)))


def build_all_props():
    build_island_props()
    build_sink_props()
    build_pantry_props()
    build_entry_props()
    build_plants()
    build_pendants()
