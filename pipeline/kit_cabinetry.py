"""kit_cabinetry.py — cabinet family: carcasses, doors, drawers, plinths, worktops,
west preparation run, south tall wall, island, pantry fit-out, sideboard.

Coordinate conventions:
- West run: carcass front plane x=0.65, overlay fronts span x [0.65, 0.669].
- South run: carcass front plane y=0.65, fronts span y [0.65, 0.669].
- Island: west face front plane x=1.75, fronts span x [1.731, 1.750].
- Vertical-hinge doors: mesh origin ON the hinge line; opening rotation sign is
  determined by geometry (hinge S/W -> +, hinge N/E -> -, drop doors -> -Y local).
All articulated joints are registered in REG.joints with signed state values.
"""

import math
import bpy
from mathutils import Vector, Matrix

import kit_params as P
import kit_util as U
from kit_util import box, cyl, revolve, REG


CABS = ["cab_front_greige", "cab_body", "oak", "oak_dark", "stone_worktop",
        "bronze", "steel_brushed", "steel_dark", "ceramic_white", "linen"]


def carcass(name, x0, x1, y0, y1, z0, z1, mats, col="CABINETRY", t=0.018,
            back_t=0.012, oid=None, front="+Y"):
    """Carcass with real panel thickness, OPEN on the `front` side.
    Sides run perpendicular to the front; back panel opposite the front."""
    def B(nm, size, loc):
        return box(nm, size, loc, mats["cab_body"], col, bevel=0.0015)
    B(f"{name}_top", (x1 - x0, y1 - y0, t), ((x0 + x1) / 2, (y0 + y1) / 2, z1 - t / 2))
    B(f"{name}_bot", (x1 - x0, y1 - y0, t), ((x0 + x1) / 2, (y0 + y1) / 2, z0 + t / 2))
    if front in ("+X", "-X"):
        B(f"{name}_sideS", (x1 - x0, t, z1 - z0), ((x0 + x1) / 2, y0 + t / 2,
                                                   (z0 + z1) / 2))
        B(f"{name}_sideN", (x1 - x0, t, z1 - z0), ((x0 + x1) / 2, y1 - t / 2,
                                                   (z0 + z1) / 2))
        bx = x0 + back_t / 2 if front == "+X" else x1 - back_t / 2
        B(f"{name}_back", (back_t, y1 - y0, z1 - z0), (bx, (y0 + y1) / 2,
                                                       (z0 + z1) / 2))
    else:
        B(f"{name}_sideW", (t, y1 - y0, z1 - z0), (x0 + t / 2, (y0 + y1) / 2,
                                                   (z0 + z1) / 2))
        B(f"{name}_sideE", (t, y1 - y0, z1 - z0), (x1 - t / 2, (y0 + y1) / 2,
                                                   (z0 + z1) / 2))
        by = y0 + back_t / 2 if front == "+Y" else y1 - back_t / 2
        B(f"{name}_back", (x1 - x0, back_t, z1 - z0), ((x0 + x1) / 2, by,
                                                       (z0 + z1) / 2))
    if oid:
        REG.add_object(oid, bpy.data.objects[f"{name}_sideW" if front in ("+Y", "-Y")
                       else f"{name}_sideS"], "cabinetry", "container",
                       (x1 - x0, y1 - y0, z1 - z0), "cab_body", True)


def plinth(name, x0, x1, y0, y1, mats, col="CABINETRY", setback=0.05, h=0.10,
           axis="y"):
    if axis == "y":
        box(name, (x1 - x0 - setback, y1 - y0 - setback, h),
            ((x0 + x1) / 2, (y0 + y1) / 2 + setback / 2, h / 2),
            mats["cab_body"], col, bevel=0.002)
    else:
        box(name, (x1 - x0 - setback, y1 - y0 - setback, h),
            ((x0 + x1) / 2 + setback / 2, (y0 + y1) / 2, h / 2),
            mats["cab_body"], col, bevel=0.002)


def shelf(name, x0, x1, y0, y1, z, mats, t=0.018, col="CABINETRY"):
    return box(name, (x1 - x0 - 0.02, y1 - y0 - 0.02, t),
               ((x0 + x1) / 2, (y0 + y1) / 2, z), mats["cab_body"], col, bevel=0.001)


def vdoor(name, oid, hinge_xyz, width, z0, z1, t, extend, front, mats,
          joint=None, sign=None, col="CABINETRY", handle=True, handle_mat=None,
          z_handle=None):
    """Vertical-hinge door; mesh origin ON the hinge line.

    extend: '+X','-X','+Y','-Y' direction the door slab extends from the hinge.
    front:  '+X','-X','+Y','-Y' outward face normal (handle side).
    sign:   opening rotation sign about local Z (+ opens for hinge W/S edges,
            - for hinge E/N edges). Seed states are positive; stored signed.
    """
    h = z1 - z0
    cz = (z0 + z1) / 2
    hx, hy, hz = hinge_xyz
    ext_v = {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}[extend]
    frt_v = {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}[front]
    s = 1 if extend in ("+X", "+Y") else -1
    if extend in ("+X", "-X"):
        size = (width, t, h)
        obj = box(name, size, (0, 0, 0), mats["cab_front_greige"], col, bevel=0.002)
        # unit-cube mesh: shift by half UNIT so object scale carries the width
        obj.data.transform(Matrix.Translation((s * width / 2, 0, 0)))
    else:
        size = (t, width, h)
        obj = box(name, size, (0, 0, 0), mats["cab_front_greige"], col, bevel=0.002)
        obj.data.transform(Matrix.Translation((0, s * width / 2, 0)))
    obj.location = (hx, hy, cz)
    if oid:
        REG.add_object(oid, obj, "cabinetry", "container", size,
                       "cab_front_greige", static=False)
    if handle:
        hm = handle_mat or mats["bronze"]
        hl = min(0.30, h * 0.42)
        hzc = z_handle if z_handle is not None else cz
        # bar center: near free edge, standing off the front face
        # door-LOCAL coords: origin at the hinge line, z at the door center
        bx = ext_v[0] * (width - 0.05) + frt_v[0] * (t / 2 + 0.032)
        by = ext_v[1] * (width - 0.05) + frt_v[1] * (t / 2 + 0.032)
        sx0 = ext_v[0] * (width - 0.05) + frt_v[0] * (t / 2 + 0.016)
        sy0 = ext_v[1] * (width - 0.05) + frt_v[1] * (t / 2 + 0.016)
        rot_s = (0, math.pi / 2, 0) if frt_v[0] != 0 else (math.pi / 2, 0, 0)
        for dz in (-hl / 2, hl / 2):
            cyl(f"{name}_hst{dz:.2f}", 0.005, 0.032, (sx0, sy0, hzc - cz + dz), hm,
                col, rot=rot_s, verts=12, parent=obj)
        cyl(f"{name}_hbar", 0.008, hl, (bx, by, hzc - cz), hm, col,
            rot=(0, 0, 0), verts=14, parent=obj)
    if joint:
        jd = dict(joint)
        jd["states"] = {k: sign * v for k, v in joint["states"].items()}
        jd["limits"] = (min(sign * joint["limits"][0], sign * joint["limits"][1]),
                        max(sign * joint["limits"][0], sign * joint["limits"][1]))
        REG.add_joint(jd, obj, (hx, hy, cz), (0, 0, 1),
                      handle_region=f"bar handle near free edge, z~{hzc:.2f}",
                      clearance=f"sweeps radius {width:.2f} m about hinge",
                      allowed_contacts=["door edge vs carcass front 3mm gap (closed)"],
                      collision_ids=[oid or name])
    return obj


def hinged_drop(name, oid, hinge_xyz, width, height, t, mats, joint, col="CABINETRY"):
    """Drop-down door (dishwasher/oven). Width along world Y, hangs from top
    hinge; opening rotates about local Y to negative angles (swings +X)."""
    hx, hy, hz = hinge_xyz
    obj = box(name, (t, width, height), (0, 0, 0), mats["steel_brushed"], col,
              bevel=0.002)
    obj.data.transform(Matrix.Translation((0, 0, -height / 2)))
    obj.location = (hx, hy, hz)
    REG.add_object(oid, obj, "appliances", "container", (t, width, height),
                   "steel_brushed", static=False)
    jd = dict(joint)
    jd["states"] = {k: -abs(v) for k, v in joint["states"].items()}
    span = max(abs(joint["limits"][0]), abs(joint["limits"][1]))
    jd["limits"] = (-span, 0)
    REG.add_joint(jd, obj, (hx, hy, hz), (0, 1, 0),
                  handle_region="recessed top-edge handle channel along width",
                  clearance=f"open reach {height:.2f} m toward +X at hinge height",
                  allowed_contacts=["door inner face vs body lip (intended, open)"],
                  collision_ids=[oid])
    return obj


def register_prismatic(jid, jd, root, axis_vec, handle_region, clearance,
                       allowed_contacts, collision_ids):
    jd = dict(jd)
    REG.add_joint(jd, root, tuple(root.location), list(axis_vec), handle_region,
                  clearance, allowed_contacts, collision_ids)


# ============================================================ west run
def build_west_run(mats):
    D = P.WRUN_D
    T = P.WRUN_TOP
    # worktop: segments with a real sink cutout (hole y 2.67..3.13, x 0.05..0.63)
    segs = [(1.80, 2.67), (3.13, 7.40)]
    for i, (a, b) in enumerate(segs):
        box(f"wr_worktop_{i}", (D + 0.015, b - a, P.STONE_T),
            (D / 2 + 0.0075, (a + b) / 2, T - P.STONE_T / 2), mats["stone_worktop"],
            "CABINETRY", bevel=0.003, oid=f"worktop_west_{i}", category="architecture",
            role="fixture")
    # hole reveal strips (x-wise)
    box("wr_worktop_ws", (0.05, 3.13 - 2.67, P.STONE_T),
        (0.025, (2.67 + 3.13) / 2, T - P.STONE_T / 2), mats["stone_worktop"],
        "CABINETRY", bevel=0.002)
    box("wr_worktop_we", (0.035, 3.13 - 2.67, P.STONE_T),
        (0.6475, (2.67 + 3.13) / 2, T - P.STONE_T / 2), mats["stone_worktop"],
        "CABINETRY", bevel=0.002)
    # backsplash
    box("wr_backsplash", (0.02, 7.40 - 1.80, 0.55), (0.01, (1.80 + 7.40) / 2, 1.175),
        mats["stone_worktop"], "CABINETRY", bevel=0.002, category="architecture",
        role="fixture")
    build_waste(mats)
    build_sink_base(mats)
    build_dishwasher(mats)
    build_prep_base(mats)
    build_cooktop(mats)
    build_coffee_counter(mats)
    build_oven_column(mats)
    build_uppers(mats)
    build_undercabinet_lights(mats)
    build_outlets_cables(mats)


def build_waste(mats):
    y0, y1 = 1.80, 2.40
    carcass("wr_waste_cab", 0.0, P.WRUN_D, y0, y1, 0.10, P.WRUN_TOP - P.STONE_T,
            mats, front="+X")
    root = bpy.data.objects.new("waste_pullout_root", None)
    root.location = (P.WRUN_D + 0.0095, (y0 + y1) / 2, 0.486)
    bpy.context.scene.collection.objects.link(root)
    U.link(root, "CABINETRY")
    door = box("waste_pullout_door", (0.019, y1 - y0 - 0.006, 0.745),
               (0, 0, 0), mats["cab_front_greige"], "CABINETRY", bevel=0.002,
               parent=root)
    cyl("waste_handle_bar", 0.008, 0.25, (0.042, 0, 0.22), mats["bronze"],
        "CABINETRY", rot=(math.pi / 2, 0, 0), verts=14, parent=root)
    for sy in (-0.125, 0.125):
        cyl(f"waste_handle_st{sy}", 0.005, 0.032, (0.024, sy, 0.22), mats["bronze"],
            "CABINETRY", rot=(math.pi / 2, 0, 0), verts=10, parent=root)
    # bin frame + 2 bins (root-local, behind door)
    fx = -0.28
    box("waste_frame_b", (0.52, 0.55, 0.015), (fx, 0, -0.31), mats["bin_grey"],
        "CABINETRY", bevel=0.002, parent=root)
    for sy, lane in ((-0.14, "bin_paper"), (0.14, "bin_plastic")):
        box(f"{lane}_L", (0.50, 0.008, 0.42), (fx, sy - 0.13, -0.09), mats["bin_grey"],
            "CABINETRY", bevel=0.002, parent=root)
        box(f"{lane}_R", (0.50, 0.008, 0.42), (fx, sy + 0.13, -0.09), mats["bin_grey"],
            "CABINETRY", bevel=0.002, parent=root)
        box(f"{lane}_B", (0.008, 0.26, 0.42), (fx - 0.25, sy, -0.09), mats["bin_grey"],
            "CABINETRY", bevel=0.002, parent=root)
        box(f"{lane}_F", (0.008, 0.26, 0.42), (fx + 0.25, sy, -0.09), mats["bin_grey"],
            "CABINETRY", bevel=0.002, parent=root)
        REG.add_object(lane, bpy.data.objects[f"{lane}_B"], "cabinetry", "receptacle",
                       (0.5, 0.25, 0.42), "bin_grey", True, parent="waste_pullout_root")
    # contents hint: paper stack in paper bin
    box("bin_paper_contents", (0.28, 0.20, 0.10), (fx, -0.14, -0.13), mats["paper"],
        "PROPS", bevel=0.002, parent=root)
    jd = next(j for j in P.JOINT_SEED if j["id"] == "waste_pullout")
    register_prismatic("waste_pullout", jd, root, (1, 0, 0),
                       "bar handle center of door", "slides 0.55 m +X out of cabinet",
                       ["runner carriage vs carcass rails (intended)"],
                       ["waste_pullout_door", "bin_paper", "bin_plastic"])
    REG.add_object("waste_pullout_door", door, "cabinetry", "container",
                   (0.019, y1 - y0 - 0.006, 0.745), "cab_front_greige", False,
                   parent="waste_pullout_root")


def build_sink_base(mats):
    y0, y1 = 2.45, 3.35
    carcass("wr_sink_cab", 0.0, P.WRUN_D, y0, y1, 0.10, P.WRUN_TOP - P.STONE_T,
            mats, front="+X")
    box("wr_sink_front", (0.019, y1 - y0 - 0.006, 0.745),
        (P.WRUN_D + 0.0095, (y0 + y1) / 2, 0.486), mats["cab_front_greige"],
        "CABINETRY", bevel=0.002)
    # undermount stainless bowl
    bw, bd, bdepth = 0.58, 0.42, 0.19
    bx, by = 0.34, (y0 + y1) / 2
    ztop = P.WRUN_TOP - P.STONE_T
    st = 0.012
    for nm, size, loc in (
            ("bowl_B", (bw, bd, st), (bx, by, ztop - bdepth)),
            ("bowl_S", (bw, st, bdepth), (bx, by - bd / 2 + st / 2, ztop - bdepth / 2)),
            ("bowl_N", (bw, st, bdepth), (bx, by + bd / 2 - st / 2, ztop - bdepth / 2)),
            ("bowl_W", (st, bd - 2 * st, bdepth), (bx - bw / 2 + st / 2, by, ztop - bdepth / 2)),
            ("bowl_E", (st, bd - 2 * st, bdepth), (bx + bw / 2 - st / 2, by, ztop - bdepth / 2))):
        box(f"sink_{nm}", size, loc, mats["steel_brushed"], "CABINETRY", bevel=0.004)
    cyl("sink_drain", 0.045, 0.01, (bx + 0.14, by, ztop - bdepth + 0.008),
        mats["steel_brushed"], "CABINETRY", verts=20)
    # faucet
    fx, fy = 0.10, (y0 + y1) / 2
    cyl("faucet_base", 0.028, 0.03, (fx, fy, ztop + 0.015), mats["faucet_steel"],
        "CABINETRY", verts=24)
    cyl("faucet_riser", 0.019, 0.28, (fx, fy, ztop + 0.17), mats["faucet_steel"],
        "CABINETRY", verts=20)
    U.torus_seg("faucet_gooseneck", 0.11, 0.017, (fx, fy, ztop + 0.31),
                rot=(math.pi / 2, 0, 0), arc=math.pi, mat=mats["faucet_steel"],
                col="CABINETRY", major=28, minor=12)
    cyl("faucet_spout", 0.017, 0.10, (fx + 0.11, fy, ztop + 0.26),
        mats["faucet_steel"], "CABINETRY", verts=16)
    cyl("faucet_lever", 0.011, 0.11, (fx - 0.03, fy + 0.03, ztop + 0.335),
        mats["faucet_steel"], "CABINETRY", rot=(0, math.radians(25), 0), verts=12)
    REG.add_object("sink_bowl", bpy.data.objects["sink_bowl_B"], "fixtures",
                   "receptacle", (bw, bd, bdepth), "steel_brushed", True)
    REG.add_object("faucet", bpy.data.objects["faucet_riser"], "fixtures", "fixture",
                   (0.06, 0.06, 0.35), "faucet_steel", True)


def build_dishwasher(mats):
    y0, y1 = 3.35, 3.95
    box("dw_body", (0.60, y1 - y0, 0.72), (0.32, (y0 + y1) / 2, 0.46),
        mats["steel_dark"], "CABINETRY", bevel=0.002, oid="dishwasher_body",
        category="appliances", role="fixture")
    box("dw_cavity", (0.55, y1 - y0 - 0.10, 0.60), (0.33, (y0 + y1) / 2, 0.46),
        mats["steel_dark"], "CABINETRY", bevel=0.002)
    for i, rz in enumerate((0.62, 0.30)):
        box(f"dw_rack_{i}", (0.48, y1 - y0 - 0.16, 0.015), (0.30, (y0 + y1) / 2, rz),
            mats["steel_brushed"], "CABINETRY", bevel=0.002,
            oid=f"dishwasher_rack_{i}" if i == 0 else None,
            category="appliances", role="container")
        for k in range(5):
            box(f"dw_rack_{i}_wire_{k}", (0.48, 0.006, 0.05),
                (0.30, y0 + 0.09 + k * 0.09, rz + 0.03), mats["steel_brushed"],
                "CABINETRY", bevel=0)
    jd = next(j for j in P.JOINT_SEED if j["id"] == "dishwasher_door")
    door = hinged_drop("dishwasher_door", "dishwasher_door",
                       (0.66, (y0 + y1) / 2, P.WRUN_TOP - P.STONE_T - 0.006),
                       y1 - y0 - 0.006, 0.58, 0.020, mats, jd)
    box("dw_control_strip", (0.006, y1 - y0 - 0.05, 0.035),
        (0.014, 0, -0.03), mats["steel_brushed"], "CABINETRY", bevel=0.001,
        parent=door)
    plinth("dw_plinth", 0.0, P.WRUN_D, y0, y1, mats, setback=P.PLINTH_SET, axis="y")


def build_prep_base(mats):
    y0, y1 = 3.95, 4.95
    carcass("wr_prep_cab", 0.0, P.WRUN_D, y0, y1, 0.10, P.WRUN_TOP - P.STONE_T,
            mats, front="+X")
    plinth("wr_prep_plinth", 0.0, P.WRUN_D, y0, y1, mats, setback=P.PLINTH_SET,
           axis="y")
    fa_x = P.WRUN_D + 0.0095
    root1, f1 = U.make_drawer("drawer_prep_1", "drawer_prep_1", 0.494, 0.136, 0.46,
                              0.50, 0.11, (fa_x, 4.20, 0.796), "+X",
                              mats["cab_front_greige"], mats["cab_body"],
                              handle_mat=mats["bronze"])
    root2, f2 = U.make_drawer("drawer_prep_2", "drawer_prep_2", 0.494, 0.290, 0.46,
                              0.50, 0.24, (fa_x, 4.20, 0.585), "+X",
                              mats["cab_front_greige"], mats["cab_body"],
                              handle_mat=mats["bronze"])
    vdoor("wr_prep_door_a", "lower_door_a", (fa_x, y0 + 0.003, 0.4425), 0.494,
          0.113, 0.439, 0.019, "+Y", "+X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "lower_door_a"), sign=-1)
    vdoor("wr_prep_door_b", "lower_door_b", (fa_x, y1 - 0.003, 0.49), 0.494,
          0.113, 0.864, 0.019, "-Y", "+X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "lower_door_b"), sign=+1)
    shelf("wr_prep_shelfB", 0.0, P.WRUN_D, 4.45, y1, 0.44, mats)
    for i in range(4):
        revolve(f"wr_plate_{i}", [(0, 0), (0.10, 0.004), (0.115, 0.012),
                                  (0.10, 0.016), (0, 0.018)],
                (0.30, 4.70, 0.459 + i * 0.02), mats["ceramic_white"], "CABINETRY",
                segs=28)
    for pid in ("drawer_prep_1", "drawer_prep_2"):
        jd = next(j for j in P.JOINT_SEED if j["id"] == pid)
        register_prismatic(pid, jd, bpy.data.objects[pid + "_root"], (1, 0, 0),
                           "bar handle front center", "slides 0.45 m +X",
                           ["drawer box vs carcass walls (runner clearance)"],
                           [pid + "_front"])


def build_cooktop(mats):
    y0, y1 = 4.95, 5.75
    carcass("wr_cook_cab", 0.0, P.WRUN_D, y0, y1, 0.10, P.WRUN_TOP - P.STONE_T,
            mats, front="+X")
    plinth("wr_cook_plinth", 0.0, P.WRUN_D, y0, y1, mats, setback=P.PLINTH_SET,
           axis="y")
    box("wr_cook_door", (0.019, y1 - y0 - 0.006, 0.751),
        (P.WRUN_D + 0.0095, (y0 + y1) / 2, 0.4885), mats["cab_front_greige"],
        "CABINETRY", bevel=0.002)
    box("cooktop_glass", (P.WRUN_D - 0.06, y1 - y0 - 0.08, 0.008),
        (P.WRUN_D / 2, (y0 + y1) / 2, P.WRUN_TOP + 0.001), mats["cooktop_glass"],
        "CABINETRY", bevel=0.001, oid="cooktop", category="appliances", role="fixture")
    for i, (zx, zy, r) in enumerate(((0.24, 5.20, 0.085), (0.24, 5.50, 0.085),
                                     (0.44, 5.20, 0.065), (0.44, 5.50, 0.065))):
        U.tube(f"cooktop_zone_{i}", r, r - 0.004, 0.002,
               (zx, zy, P.WRUN_TOP + 0.0055), mats["steel_brushed"], "CABINETRY",
               verts=24)
    box("cooktop_controls", (0.05, y1 - y0 - 0.30, 0.004),
        (0.075, (y0 + y1) / 2, P.WRUN_TOP + 0.004), mats["steel_dark"], "CABINETRY",
        bevel=0)
    box("hood_box", (0.50, 0.78, 0.42), (0.25, (y0 + y1) / 2 + 0.11, 1.78),
        mats["steel_brushed"], "CABINETRY", bevel=0.004, oid="hood",
        category="appliances", role="fixture")
    box("hood_filter_strip", (0.03, 0.64, 0.24), (0.475, (y0 + y1) / 2 + 0.11, 1.70),
        mats["steel_dark"], "CABINETRY", bevel=0.002)
    box("hood_duct", (0.24, 0.24, P.ROOM_H - 2.0),
        (0.25, (y0 + y1) / 2, 2.0 + (P.ROOM_H - 2.0) / 2), mats["steel_brushed"],
        "CABINETRY", bevel=0.002)
    REG.add_object("hood", bpy.data.objects["hood_box"], "appliances", "fixture",
                   (0.5, 1.0, 0.42), "steel_brushed", True)


def build_coffee_counter(mats):
    y0, y1 = 5.75, 6.35
    carcass("wr_coffee_cab", 0.0, P.WRUN_D, y0, y1, 0.10, P.WRUN_TOP - P.STONE_T,
            mats, front="+X")
    plinth("wr_coffee_plinth", 0.0, P.WRUN_D, y0, y1, mats, setback=P.PLINTH_SET,
           axis="y")
    vdoor("wr_coffee_door", None, (P.WRUN_D + 0.0095, y1 - 0.003, 0.49), 0.594,
          0.113, 0.864, 0.019, "-Y", "+X", mats)


def build_oven_column(mats):
    y0, y1 = 6.35, 7.40
    carcass("wr_oven_cab", 0.0, P.WRUN_D, y0, y1, 0.10, 2.45, mats, front="+X")
    plinth("wr_oven_plinth", 0.0, P.WRUN_D, y0, y1, mats, setback=P.PLINTH_SET,
           axis="y")
    cav = P.OVEN_NICHE["cavity"]
    box("oven_cavity", (0.55, cav["y1"] - cav["y0"], cav["z1"] - cav["z0"]),
        (0.28, (cav["y0"] + cav["y1"]) / 2, (cav["z0"] + cav["z1"]) / 2),
        mats["steel_dark"], "APPLIANCES", bevel=0.002, oid="oven_cavity",
        category="appliances", role="fixture")
    for i, rz in enumerate((1.18, 1.32)):
        box(f"oven_rack_{i}", (0.42, 0.40, 0.012),
            (0.26, (cav["y0"] + cav["y1"]) / 2, rz), mats["steel_brushed"],
            "APPLIANCES", bevel=0.002)
    niche = P.OVEN_NICHE
    jd = next(j for j in P.JOINT_SEED if j["id"] == "oven_door")
    door = hinged_drop("oven_door", "oven_door",
                       (0.66, (niche["y0"] + niche["y1"]) / 2, niche["z1"]),
                       niche["y1"] - niche["y0"], niche["z1"] - niche["z0"], 0.024,
                       mats, jd)
    box("oven_door_glass", (0.006, niche["y1"] - niche["y0"] - 0.09,
                            niche["z1"] - niche["z0"] - 0.09),
        (0.014, 0, -(niche["z1"] - niche["z0"]) / 2 + 0.006),
        mats["glass_low_iron"], "APPLIANCES", bevel=0, parent=door)
    box("oven_control", (0.018, niche["y1"] - niche["y0"], 0.09),
        (P.WRUN_D + 0.009, (niche["y0"] + niche["y1"]) / 2, niche["z1"] + 0.045),
        mats["steel_dark"], "APPLIANCES", bevel=0.002)
    box("oven_display", (0.004, 0.16, 0.03),
        (P.WRUN_D + 0.019, (niche["y0"] + niche["y1"]) / 2, niche["z1"] + 0.055),
        bpy.data.materials["appliance_screen"], "APPLIANCES", bevel=0)
    for k in range(2):
        cyl(f"oven_knob_{k}", 0.016, 0.012,
            (P.WRUN_D + 0.019, 6.62 + k * 0.24, niche["z1"] + 0.028),
            bpy.data.materials["display_knob"], "APPLIANCES",
            rot=(0, math.pi / 2, 0), verts=16)
    vdoor("wr_ovencol_top_door", "ovencol_top_door",
          (P.WRUN_D + 0.0095, y1 - 0.003, 2.1325), 0.60, 1.845, 2.42, 0.019, "-Y",
          "+X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "ovencol_top_door"),
          sign=+1, handle_mat=mats["bronze"])
    box("oven_warming_front", (0.019, niche["y1"] - niche["y0"], 0.57),
        (P.WRUN_D + 0.0095, (niche["y0"] + niche["y1"]) / 2, 0.735),
        mats["steel_brushed"], "APPLIANCES", bevel=0.002)
    box("oven_col_filler_hi", (0.019, 0.41, 0.855),
        (P.WRUN_D + 0.0095, 6.585, 2.0125),
        mats["cab_front_greige"], "CABINETRY", bevel=0.002)
    shelf("wr_oven_shelf_top", 0.02, P.WRUN_D - 0.02, y0 + 0.02, y1 - 0.02, 2.10,
          mats)


def build_uppers(mats):
    D = P.UPPER_D
    z0, z1 = P.UPPER_Z0, P.UPPER_Z1
    carcass("up_a", 0.0, D, 3.95, 4.95, z0, z1, mats, front="+X")
    shelf("up_a_shelf", 0.0, D, 3.95, 4.95, z0 + (z1 - z0) * 0.45, mats)
    shelf("up_a_shelf2", 0.0, D, 3.95, 4.95, z0 + (z1 - z0) * 0.78, mats)
    vdoor("up_door_a", "upper_door_a", (D + 0.0095, 3.953, (z0 + z1) / 2), 0.494,
          z0 + 0.003, z1 - 0.003, 0.019, "+Y", "+X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "upper_door_a"), sign=-1,
          handle_mat=mats["bronze"])
    vdoor("up_door_b", "upper_door_b", (D + 0.0095, 4.947, (z0 + z1) / 2), 0.494,
          z0 + 0.003, z1 - 0.003, 0.019, "-Y", "+X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "upper_door_b"), sign=+1,
          handle_mat=mats["bronze"])
    for i in range(3):
        revolve(f"up_bowl_{i}", [(0, 0), (0.07, 0.01), (0.09, 0.05), (0.085, 0.055),
                                 (0, 0.06)],
                (0.16, 4.68, z0 + 0.03 + i * 0.065), mats["ceramic_putty"],
                "CABINETRY", segs=26)
    carcass("up_b", 0.0, D, 5.75, 6.35, z0, z1, mats, front="+X")
    vdoor("up_door_c", None, (D + 0.0095, 6.347, (z0 + z1) / 2), 0.594,
          z0 + 0.003, z1 - 0.003, 0.019, "-Y", "+X", mats)
    # open oak shelves over waste zone
    box("up_open_shelf", (0.24, 0.70, 0.035), (0.14, 2.15, z0 + 0.28), mats["oak"],
        "CABINETRY", bevel=0.003, oid="up_open_shelf", category="cabinetry",
        role="fixture")
    box("up_open_shelf2", (0.24, 0.70, 0.035), (0.14, 2.15, z0 + 0.62), mats["oak"],
        "CABINETRY", bevel=0.003)
    # fixed filler panel between window and uppers
    box("up_filler_win", (D - 0.02, 0.019, z1 - z0), (D / 2 - 0.01, 3.65,
        (z0 + z1) / 2), mats["cab_front_greige"], "CABINETRY", bevel=0.001)


def build_undercabinet_lights(mats):
    em = bpy.data.materials["emissive_strip"]
    box("uc_strip_a", (0.05, 0.95, 0.012), (0.06, 4.45, P.UPPER_Z0 - 0.008), em,
        "LIGHTING", bevel=0)
    box("uc_strip_b", (0.05, 0.55, 0.012), (0.06, 6.05, P.UPPER_Z0 - 0.008), em,
        "LIGHTING", bevel=0)


def build_outlets_cables(mats):
    for nm, oy in (("outlet_a", 4.20), ("outlet_b", 6.10)):
        box(nm, (0.012, 0.086, 0.086), (0.021, oy, 1.12), mats["ceramic_white"],
            "ARCH", bevel=0.002)
        REG.add_object(nm, bpy.data.objects[nm], "fixtures", "fixture",
                       (0.086, 0.086, 0.012), "ceramic_white", True)


# ============================================================ south tall wall
def build_south_tall(mats):
    D = P.SRUN_D
    H = P.SRUN_H
    z0 = 0.10
    carcass("fridge_enc", 0.15, 1.35, 0.0, D, z0, H, mats, front="+Y")
    box("fridge_enc_side_l", (0.02, D, H - z0), (0.14, D / 2, (z0 + H) / 2),
        mats["cab_front_greige"], "CABINETRY", bevel=0.002)
    plinth("srun_plinth", 0.15, 2.25, 0.0, D, mats, setback=P.PLINTH_SET, axis="y")
    ld = bpy.data.lights.new("fridge_light", "AREA")
    ld.energy = 3
    ld.size = 0.5
    ld.size_y = 0.06
    ld.color = (1.0, 0.97, 0.92)
    flo = bpy.data.objects.new("fridge_light", ld)
    flo.location = (0.75, 0.34, 2.06)
    bpy.context.scene.collection.objects.link(flo)
    U.link(flo, "APPLIANCES")
    # real open-front interiors: fridge zone above, freezer zone below (z 1.21)
    bt = 0.012
    box("fridge_int_back", (1.08, bt, 0.87), (0.75, 0.036, 1.655),
        mats["steel_dark"], "APPLIANCES", bevel=0.001)
    for i, sx in enumerate((0.226, 1.274)):
        box(f"fridge_int_side_{i}", (bt, 0.55, 0.87), (sx, 0.32, 1.655),
            mats["steel_dark"], "APPLIANCES", bevel=0.001)
    box("fridge_int_top", (1.08, 0.58, bt), (0.75, 0.32, 2.084),
        mats["steel_dark"], "APPLIANCES", bevel=0.001)
    box("fridge_int_mid", (1.08, 0.58, bt), (0.75, 0.32, 1.216),
        mats["steel_dark"], "APPLIANCES", bevel=0.001)
    box("fridge_int_bot", (1.08, 0.58, bt), (0.75, 0.32, 0.114),
        mats["steel_dark"], "APPLIANCES", bevel=0.001)
    REG.add_object("fridge_cavity", bpy.data.objects["fridge_int_back"],
                   "appliances", "fixture", (1.08, 0.58, 1.95), "steel_dark", True)
    for i, sz in enumerate((1.36, 1.64, 1.92)):
        box(f"fridge_shelf_{i}", (1.02, 0.52, 0.014), (0.75, 0.30, sz),
            mats["glass_low_iron"], "APPLIANCES", bevel=0.002,
            oid=f"fridge_shelf_{i}" if i == 1 else None, category="appliances",
            role="container")
    for i in range(2):
        box(f"fridge_bin_{i}", (0.48, 0.40, 0.16), (0.52 + i * 0.44, 0.28, 1.40),
            bpy.data.materials["plastic_white"], "APPLIANCES", bevel=0.004)
    jd = next(j for j in P.JOINT_SEED if j["id"] == "fridge_door")
    door = vdoor("fridge_door", "fridge_door", (0.19, D + 0.012, 1.675), 1.05,
                 P.FRIDGE_SPLIT_Z + 0.01, P.FRIDGE_DOOR_TOP, 0.045, "+X", "+Y",
                 mats, joint=jd, sign=+1, handle_mat=mats["bronze"], z_handle=1.68)
    box("fridge_door_face", (0.98, 0.008, P.FRIDGE_DOOR_TOP - P.FRIDGE_SPLIT_Z - 0.04),
        (0.52, 0.028, 0), mats["steel_brushed"], "APPLIANCES", bevel=0.002,
        parent=door)
    # freezer drawer (front normal +Y)
    fz0, fz1 = 0.12, P.FRIDGE_SPLIT_Z
    root, _ = U.make_drawer("freezer_drawer", "freezer_drawer", 1.05,
                            fz1 - fz0 - 0.01, 1.0, 0.52, (fz1 - fz0) - 0.08,
                            (0.675, D + 0.0095, (fz0 + fz1) / 2), "+Y",
                            mats["steel_brushed"], mats["cab_body"],
                            handle_mat=mats["steel_dark"])
    jd2 = next(j for j in P.JOINT_SEED if j["id"] == "freezer_drawer")
    register_prismatic("freezer_drawer", jd2, root, (0, 1, 0),
                       "horizontal bar handle", "slides 0.52 m +Y",
                       ["drawer box vs enclosure walls (runner clearance)"],
                       ["freezer_drawer_front"])
    box("fridge_top_panel", (1.14, 0.019, P.FRIDGE_ABOVE_TOP - P.FRIDGE_DOOR_TOP - 0.01),
        (0.75, D + 0.0095, (P.FRIDGE_DOOR_TOP + P.FRIDGE_ABOVE_TOP) / 2),
        mats["cab_front_greige"], "CABINETRY", bevel=0.002)
    box("fridge_vent_grille", (0.60, 0.012, 0.02), (0.75, D + 0.020, H - 0.12),
        mats["steel_dark"], "APPLIANCES", bevel=0.001)
    carcass("tall_cab", 1.35, 2.25, 0.0, D, z0, H, mats, front="+Y")
    for i, sz in enumerate((0.55, 1.05, 1.55, 2.05)):
        shelf(f"tall_shelf_{i}", 1.35, 2.25, 0.02, D - 0.02, sz, mats)
    vdoor("tall_door_a", "tall_door_a", (1.353, D + 0.0095, 1.275), 0.441,
          0.113, 2.44, 0.019, "+X", "+Y", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "tall_door_a"), sign=+1,
          handle_mat=mats["bronze"])
    vdoor("tall_door_b", "tall_door_b", (2.247, D + 0.0095, 1.275), 0.441,
          0.113, 2.44, 0.019, "-X", "+Y", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "tall_door_b"), sign=-1,
          handle_mat=mats["bronze"])
    # tall cabinet contents: baskets and dry-goods boxes on shelves
    for i, sz in enumerate((0.55, 1.05, 1.55)):
        box(f"tall_basket_{i}", (0.30, 0.36, 0.22), (1.62, 0.33, sz + 0.11),
            bpy.data.materials["bin_grey"], "CABINETRY", bevel=0.012)
    box("tall_goods_1", (0.26, 0.30, 0.20), (2.02, 0.33, 0.66),
        bpy.data.materials["cardboard"], "CABINETRY", bevel=0.006)
    box("tall_goods_2", (0.22, 0.26, 0.16), (2.04, 0.33, 2.14),
        bpy.data.materials["cereal_graphic"], "CABINETRY", bevel=0.006)
    box("srun_filler", (0.06, 0.019, H - z0), (2.32, D + 0.0095, (z0 + H) / 2),
        mats["cab_front_greige"], "CABINETRY", bevel=0.001)


# ============================================================ island
def build_island(mats):
    x0, x1 = P.ISL["x0"], P.ISL["x1"]
    y0, y1 = P.ISL["y0"], P.ISL["y1"]
    top = P.ISL["top"]
    st = P.ISL["stone"]
    zc1 = top - st
    carcass("island_cab", x0, x1, y0, y1, 0.10, zc1, mats, front="-X")
    plinth("island_plinth", x0, x1, y0, y1, mats, setback=P.ISL["plinth_set"],
           axis="y")
    box("island_worktop", (x1 - x0 + 0.02, y1 - y0, st),
        ((x0 + x1) / 2, (y0 + y1) / 2, top - st / 2), mats["stone_worktop"],
        "CABINETRY", bevel=0.004, oid="island_worktop", category="cabinetry",
        role="fixture")
    box("island_east_panel", (0.022, y1 - y0, top), (x1 - 0.011, (y0 + y1) / 2,
        top / 2), mats["oak"], "CABINETRY", bevel=0.003, oid="island_east_panel",
        category="cabinetry", role="fixture")
    box("island_south_panel", (x1 - x0 - 0.04, 0.018, zc1 - 0.10),
        ((x0 + x1) / 2, y0 + 0.028, (0.10 + zc1) / 2), mats["oak"], "CABINETRY",
        bevel=0.002)
    box("island_south_shelf", (x1 - x0 - 0.04, 0.30, 0.03),
        ((x0 + x1) / 2, y0 + 0.17, 0.42), mats["oak"], "CABINETRY", bevel=0.003,
        oid="island_niche_shelf", category="cabinetry", role="fixture")
    fa_x = x0 - 0.0095
    U.make_drawer("drawer_island_1", "drawer_island_1", 0.734, 0.140, 0.70, 0.52,
                  0.11, (fa_x, 3.61, 0.786), "-X", mats["cab_front_greige"],
                  mats["cab_body"], handle_mat=mats["bronze"])
    U.make_drawer("drawer_island_2", "drawer_island_2", 0.734, 0.290, 0.70, 0.52,
                  0.24, (fa_x, 4.37, 0.571), "-X", mats["cab_front_greige"],
                  mats["cab_body"], handle_mat=mats["bronze"])
    vdoor("island_door", "island_door", (fa_x, 4.763, 0.275), 0.78, 0.122, 0.423,
          0.019, "+Y", "-X", mats,
          joint=next(j for j in P.JOINT_SEED if j["id"] == "island_door"), sign=-1,
          handle_mat=mats["bronze"])
    for pid in ("drawer_island_1", "drawer_island_2"):
        jd = next(j for j in P.JOINT_SEED if j["id"] == pid)
        register_prismatic(pid, jd, bpy.data.objects[pid + "_root"], (-1, 0, 0),
                           "bar handle front center", "slides 0.45 m -X into aisle",
                           ["drawer box vs carcass walls (runner clearance)"],
                           [pid + "_front"])
    shelf("island_shelf", x0 + 0.02, x1 - 0.02, 4.76, y1 - 0.02, 0.44, mats)


# ============================================================ pantry fit-out
def build_pantry(mats):
    px0, px1 = P.PAN["x0"] + P.PART_T, P.PAN["x1"]
    py0, py1 = P.PAN["y0"] + P.PART_T, P.PAN["y1"] - P.PART_T
    cz = P.PAN["counter_z"]
    box("pantry_counter", (px1 - px0 - 0.04, 0.62, 0.04),
        ((px0 + px1) / 2, py0 + 0.31, cz - 0.02), mats["stone_worktop"],
        "CABINETRY", bevel=0.003, oid="pantry_counter", category="cabinetry",
        role="fixture")
    carcass("pantry_base", px0 + 0.02, px1 - 0.02, py0, py0 + 0.62, 0.10, cz - 0.04,
            mats, front="+Y")
    plinth("pantry_plinth", px0 + 0.02, px1 - 0.02, py0, py0 + 0.62, mats,
           setback=0.05, axis="x")
    U.make_drawer("pantry_drawer", "pantry_drawer", 0.85, 0.20, 0.80, 0.52, 0.16,
                  ((px0 + px1) / 2, py0 + 0.6295, cz - 0.16), "+Y",
                  mats["cab_front_greige"], mats["cab_body"],
                  handle_mat=mats["bronze"])
    box("pantry_drawer_front_b", (0.85, 0.019, 0.20),
        ((px0 + px1) / 2, py0 + 0.6295, cz - 0.38), mats["cab_front_greige"],
        "CABINETRY", bevel=0.002)
    box("pantry_door_front", (1.40, 0.019, 0.40),
        ((px0 + px1) / 2, py0 + 0.6295, 0.30), mats["cab_front_greige"],
        "CABINETRY", bevel=0.002)
    jd = dict(id="pantry_drawer", elem="Pantry lower drawer", type="prismatic",
              axis="+Y", limits=(0, 0.40), states=dict(closed=0, open=0.40),
              blender_object="", pivot_world=[], axis_local=[], handle_grasp_region="",
              swept_volume_clearance="", allowed_contacts=[], task_critical_collision=[])
    register_prismatic("pantry_drawer", jd, bpy.data.objects["pantry_drawer_root"],
                       (0, 1, 0), "bar handle front", "slides 0.40 m +Y",
                       ["drawer box vs carcass (runner clearance)"],
                       ["pantry_drawer_front"])
    for i, sz in enumerate(P.PAN["shelf_zs"]):
        box(f"pantry_shelf_E_{i}", (P.PAN["shelf_d"] - 0.05, py1 - py0 - 0.66, 0.028),
            (px1 - (P.PAN["shelf_d"] - 0.05) / 2, (py0 + 0.62 + py1) / 2, sz), mats["oak"],
            "CABINETRY", bevel=0.003, oid=f"pantry_shelf_{i}" if i == 1 else None,
            category="cabinetry", role="fixture")
        box(f"pantry_shelf_W_{i}", (P.PAN["shelf_d"], py1 - py0 - 0.66, 0.028),
            (px0 + P.PAN["shelf_d"] / 2, (py0 + 0.62 + py1) / 2, sz), mats["oak"],
            "CABINETRY", bevel=0.003)
    box("pantry_shelf_S_top", (px1 - px0 - 2 * P.PAN["shelf_d"] - 0.04, 0.30, 0.028),
        ((px0 + px1) / 2, py1 - P.PAN["shelf_d"] / 2 - 0.04, P.PAN["shelf_zs"][-1]),
        mats["oak"], "CABINETRY", bevel=0.003)
    for i, sy in enumerate((1.05, 1.55)):
        box(f"pantry_divider_E_{i}", (P.PAN["shelf_d"] - 0.02, 0.015, 0.55),
            (px1 - P.PAN["shelf_d"] / 2, sy, 1.375), mats["oak"], "CABINETRY",
            bevel=0.002)
    # sliding panel + track (room side of north partition)
    panel_w = P.PAN["panel_w"]
    py_wall = P.PAN["y1"] + P.PAN["panel_standoff"]
    panel = box("pantry_slide_panel", (panel_w, 0.04, P.PAN["panel_h"]),
                (P.PAN["door_x0"] + panel_w / 2 - 0.03, py_wall,
                 P.PAN["panel_h"] / 2 + 0.04), mats["oak_dark"], "CABINETRY",
                bevel=0.003, oid="pantry_slide_panel", category="cabinetry",
                role="container", static=False)
    box("pantry_slide_inset", (panel_w - 0.3, 0.008, P.PAN["panel_h"] - 0.3),
        (0, -0.024, 0), bpy.data.materials["chalkboard"], "CABINETRY", bevel=0.001,
        parent=panel)
    box("pantry_track", (2.4, 0.05, 0.05), (8.45, py_wall, P.PAN["panel_h"] + 0.10),
        mats["bronze"], "CABINETRY", bevel=0.003)
    for sx in (-0.35, 0.35):
        cyl(f"pantry_roller{sx}", 0.022, 0.03,
            (sx, 0, P.PAN["panel_h"] / 2 + 0.075), mats["bronze"], "CABINETRY",
            rot=(0, math.pi / 2, 0), verts=14, parent=panel)
    cyl("pantry_handle_bar", 0.011, 0.5, (panel_w / 2 - 0.06, -0.045, 0.0),
        mats["bronze"], "CABINETRY", verts=14, parent=panel)
    jd = next(j for j in P.JOINT_SEED if j["id"] == "pantry_slide")
    REG.add_joint(jd, panel, tuple(panel.location), (-1, 0, 0),
                  "vertical bar handle east edge", "slides 0.95 m -X along track",
                  ["rollers vs track channel (intended)"], ["pantry_slide_panel"])
    box("pantry_light", (0.5, 0.12, 0.05), ((px0 + px1) / 2, 1.2, 2.86),
        bpy.data.materials["emissive_soft"], "LIGHTING", bevel=0.003)


# ============================================================ sideboard
def build_sideboard(mats):
    x0, x1 = P.SIDEBOARD["x0"], P.SIDEBOARD["x1"]
    y1 = P.SIDEBOARD["y1"]
    h = P.SIDEBOARD["h"]
    carcass("sideboard", x0, x1, 0.02, y1, 0.08, h - 0.02, mats, front="+Y")
    box("sideboard_top", (x1 - x0 + 0.03, y1 - 0.005, 0.025),
        ((x0 + x1) / 2, (0.02 + y1) / 2, h), mats["oak"], "CABINETRY", bevel=0.003)
    dw = (x1 - x0) / 3 - 0.006
    for i in range(3):
        box(f"sideboard_door_{i}", (dw, 0.019, h - 0.16),
            (x0 + (i + 0.5) * (x1 - x0) / 3, y1 + 0.0095, (0.08 + h) / 2 - 0.01),
            mats["oak"], "CABINETRY", bevel=0.002)
    REG.add_object("sideboard", bpy.data.objects["sideboard_top"], "furniture",
                   "fixture", (x1 - x0, y1, h), "oak", True)


class MatSet:
    """Lazy material accessor — any material in bpy.data by name."""
    def __getitem__(self, k):
        m = bpy.data.materials.get(k)
        if m is None:
            raise KeyError(k)
        return m


def build_all_cabinetry():
    mats = MatSet()
    build_west_run(mats)
    build_south_tall(mats)
    build_island(mats)
    build_pantry(mats)
    build_sideboard(mats)
