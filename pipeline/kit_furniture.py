"""kit_furniture.py — dining table, 6 chairs, 3 island stools."""

import math
import bpy
import bmesh

import kit_params as P
import kit_util as U
from kit_util import box, cyl, torus_seg, REG


def _m(name):
    return bpy.data.materials[name]


def _tapered_leg(name, top_xy, bottom_xy, w_top, w_bot, z_top, z_bot, mat, col):
    """Square tapered leg via 4-segment cone."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    cx = (top_xy[0] + bottom_xy[0]) / 2
    cy = (top_xy[1] + bottom_xy[1]) / 2
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4,
                          radius1=w_bot / 2 * 1.4142, radius2=w_top / 2 * 1.4142,
                          depth=z_top - z_bot)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (cx, cy, (z_top + z_bot) / 2)
    obj.rotation_euler = (0, 0, math.radians(45))
    bpy.context.scene.collection.objects.link(obj)
    U.link(obj, col)
    U.set_mat(obj, mat)
    U.mesh_smooth(obj)
    return obj


def build_table():
    cx, cy = P.DINING["cx"], P.DINING["cy"]
    w, d = P.DINING["w"], P.DINING["d"]
    top = P.DINING["top"]
    tt = P.DINING["top_t"]
    oak = _m("oak")
    box("dining_table_top", (w, d, tt), (cx, cy, top - tt / 2), oak, "FURNITURE",
        bevel=0.006, oid="dining_table", category="furniture", role="fixture",
        mass=42)
    # apron
    box("table_apron_a", (w - 0.16, 0.045, 0.07), (cx, cy - d / 2 + 0.06,
        top - tt - 0.035), oak, "FURNITURE", bevel=0.003)
    box("table_apron_b", (w - 0.16, 0.045, 0.07), (cx, cy + d / 2 - 0.06,
        top - tt - 0.035), oak, "FURNITURE", bevel=0.003)
    for i, (lx, ly) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        _tapered_leg(f"table_leg_{i}", (cx + lx * (w / 2 - 0.09), cy + ly * (d / 2 - 0.09)),
                     (cx + lx * (w / 2 - 0.13), cy + ly * (d / 2 - 0.13)),
                     0.062, 0.042, top - tt, 0.0, oak, "FURNITURE")


def build_chair(name, cx, cy, rot_deg, seat_mat, pulled=False):
    oak = _m("oak")
    textile = seat_mat
    root_loc = (cx, cy, 0)
    rot = math.radians(rot_deg)
    seat_z = 0.45
    # seat
    seat = box(f"{name}_seat", (0.44, 0.44, 0.045), (0, 0, seat_z), textile,
               "FURNITURE", bevel=0.012)
    # back: two posts + curved slat
    for sx in (-0.18, 0.18):
        cyl(f"{name}_post{sx}", 0.017, 0.44, (sx, 0.20, seat_z + 0.22 - 0.05),
            oak, "FURNITURE", verts=14)
        # tilt posts back slightly
        bpy.data.objects[f"{name}_post{sx}"].rotation_euler = (math.radians(-8), 0, 0)
    slat = torus_seg(f"{name}_slat", 0.34, 0.02, (0, 0.53, seat_z + 0.375),
                     rot=(-0.12, 0, math.radians(238)), arc=1.10,
                     mat=oak, col="FURNITURE", major=18, minor=8)
    slat.scale = (1.0, 1.0, 1.0)
    U.bake_scale(slat)
    # legs (back pair slightly angled)
    for i, (lx, ly) in enumerate(((-0.18, -0.18), (0.18, -0.18),
                                  (-0.18, 0.17), (0.18, 0.17))):
        l = cyl(f"{name}_leg{i}", 0.016, seat_z - 0.02, (lx, ly, (seat_z - 0.02) / 2),
                oak, "FURNITURE", verts=12)
    # stretcher ring
    torus_seg(f"{name}_stretcher", 0.24, 0.008, (0, 0, 0.16),
              rot=(0, 0, 0), arc=math.tau, mat=oak, col="FURNITURE",
              major=22, minor=6)
    # group under empty for placement rotation
    root = bpy.data.objects.new(name + "_root", None)
    root.location = root_loc
    root.rotation_euler = (0, 0, rot)
    bpy.context.scene.collection.objects.link(root)
    U.link(root, "FURNITURE")
    for obj in bpy.data.objects:
        if obj.name.startswith(name + "_") and obj is not root:
            obj.parent = root
    REG.add_object(name, seat, "furniture", "obstacle", (0.44, 0.44, 0.85),
                   "oak", True, parent=name + "_root")
    return root


def build_stool(i, cx, cy, rot_deg=0):
    oak = _m("oak")
    steel = _m("steel_dark")
    name = f"stool_{i}"
    seat_z = 0.65
    seat = cyl(f"{name}_seat", 0.175, 0.038, (0, 0, seat_z), oak, "FURNITURE",
               verts=28, oid=name, category="furniture", role="fixture")
    U.add_bevel(seat, 0.008)
    for k, (lx, ly) in enumerate(((-0.13, -0.13), (0.13, -0.13),
                                  (-0.13, 0.13), (0.13, 0.13))):
        leg = cyl(f"{name}_leg{k}", 0.013, seat_z - 0.02,
                  (lx, ly, (seat_z - 0.02) / 2), steel, "FURNITURE", verts=12)
    torus_seg(f"{name}_footring", 0.14, 0.007, (0, 0, 0.22),
              rot=(0, 0, 0), arc=math.tau, mat=steel, col="FURNITURE",
              major=24, minor=6)
    root = bpy.data.objects.new(name + "_root", None)
    root.location = (cx, cy, 0)
    root.rotation_euler = (0, 0, math.radians(rot_deg))
    bpy.context.scene.collection.objects.link(root)
    U.link(root, "FURNITURE")
    for obj in bpy.data.objects:
        if obj.name.startswith(name + "_") and obj is not root:
            obj.parent = root
    REG.add_object(name, bpy.data.objects[f"{name}_seat"], "furniture", "fixture",
                   (0.35, 0.35, seat_z), "oak", True, parent=name + "_root")
    return root


def build_all_furniture():
    build_table()
    seat_lin = _m("linen")
    seat_dark = _m("linen_dark")
    build_chair("chair_N1", 5.45, 6.34, 180, seat_lin)
    build_chair("chair_N2", 6.38, 6.34, 174, seat_dark)
    build_chair("chair_S1", 5.45, 4.90, 0, seat_dark)
    build_chair("chair_S2", 6.38, 4.62, 8, seat_lin, pulled=True)
    build_chair("chair_W", 4.62, 5.62, 90, seat_lin)
    build_chair("chair_E", 7.18, 5.62, 268, seat_dark)
    build_stool(0, 3.34, 3.72, 90)
    build_stool(1, 3.34, 4.42, 90)
    build_stool(2, 3.34, 5.12, 96)
