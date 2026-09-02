"""kit_architecture.py — room shell, openings, glazing, terrace, exterior context."""

import math
import bpy
from mathutils import Vector

import kit_params as P
import kit_util as U
from kit_util import box, cyl, link


def _m(name):
    return bpy.data.materials[name]


def build_architecture():
    M = {k: bpy.data.materials[k] for k in (
        "plaster", "ceiling_white", "oak_floor", "stone_tile", "wet_terrace_tile",
        "glass_low_iron", "glass_frosted", "bronze", "steel_dark", "oak",
        "steel_brushed", "stone_threshold", "facade", "facade_b", "window_glow",
        "sky_haze", "rubber_black", "linen", "water_film", "ceramic_white",
        "soil", "leaf", "doormat", "emissive_soft")}
    build_room_shell(M)
    build_west_window(M)
    build_terrace_glazing(M)
    build_terrace(M)
    build_entry(M)
    build_exterior(M)


def build_room_shell(M):
    X, Y, H, T = P.ROOM_X, P.ROOM_Y, P.ROOM_H, P.WALL_T
    plaster, ceil = M["plaster"], M["ceiling_white"]
    # floor slab (top at z=0)
    box("floor_slab", (X + 2 * T, Y + 2 * T, P.SLAB_T), (X / 2, Y / 2, -P.SLAB_T / 2),
        M["oak_floor"], "ARCH", oid="floor_slab", category="architecture",
        role="fixture", mass=8000)
    # ceiling slab
    box("ceiling_slab", (X + 2 * T, Y + 2 * T, P.SLAB_T),
        (X / 2, Y / 2, H + P.SLAB_T / 2), ceil, "ARCH", oid="ceiling_slab",
        category="architecture", role="fixture")
    # north wall (with glazing opening X 2.8..8.6, head 2.7 + transom band)
    segs = [(-T, P.GLZ_X0), (P.GLZ_X1, X + T)]
    for i, (a, b) in enumerate(segs):
        box(f"wall_N_{i}", (b - a, T, H), ((a + b) / 2, Y + T / 2, H / 2),
            plaster, "ARCH", category="architecture", role="fixture")
    box("wall_N_head", (P.GLZ_X1 - P.GLZ_X0, T, H - P.GLZ_HEAD),
        ((P.GLZ_X0 + P.GLZ_X1) / 2, Y + T / 2, (H + P.GLZ_HEAD) / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    # south wall
    box("wall_S", (X + 2 * T, T, H), (X / 2, -T / 2, H / 2), plaster, "ARCH",
        category="architecture", role="fixture")
    # west wall with window opening (W1)
    box("wall_W_s", (T, P.W1_Y0 + T, H), (-T / 2, (P.W1_Y0 - T) / 2, H / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    box("wall_W_n", (T, Y - P.W1_Y1 + T, H),
        (-T / 2, (P.W1_Y1 + Y + T) / 2, H / 2), plaster, "ARCH",
        category="architecture", role="fixture")
    box("wall_W_sill", (T, P.W1_Y1 - P.W1_Y0, P.W1_SILL),
        (-T / 2, (P.W1_Y0 + P.W1_Y1) / 2, P.W1_SILL / 2), plaster, "ARCH",
        category="architecture", role="fixture")
    box("wall_W_head", (T, P.W1_Y1 - P.W1_Y0, H - P.W1_HEAD),
        (-T / 2, (P.W1_Y0 + P.W1_Y1) / 2, (P.W1_HEAD + H) / 2), plaster, "ARCH",
        category="architecture", role="fixture")
    # east wall with entry opening
    box("wall_E_s", (T, P.ENTRY_Y0 + T, H), (X + T / 2, (P.ENTRY_Y0 - T) / 2, H / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    box("wall_E_n", (T, Y - P.ENTRY_Y1 + T, H),
        (X + T / 2, (P.ENTRY_Y1 + Y + T) / 2, H / 2), plaster, "ARCH",
        category="architecture", role="fixture")
    box("wall_E_head", (T, P.ENTRY_Y1 - P.ENTRY_Y0, H - P.ENTRY_H),
        (X + T / 2, (P.ENTRY_Y0 + P.ENTRY_Y1) / 2, (P.ENTRY_H + H) / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    # ---- pantry partitions
    pt = P.PART_T
    box("part_pantry_W", (pt, P.PAN["y1"] - P.PAN["y0"], H),
        (P.PAN["x0"] + pt / 2, (P.PAN["y0"] + P.PAN["y1"]) / 2, H / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    y0, y1 = P.PAN["y1"] - pt, P.PAN["y1"]
    box("part_pantry_S_seg", (P.PAN["door_x0"] - P.PAN["x0"], pt, H),
        ((P.PAN["x0"] + P.PAN["door_x0"]) / 2, (y0 + y1) / 2, H / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    box("part_pantry_N_seg", (P.PAN["x1"] - P.PAN["door_x1"], pt, H),
        ((P.PAN["door_x1"] + P.PAN["x1"]) / 2, (y0 + y1) / 2, H / 2),
        plaster, "ARCH", category="architecture", role="fixture")
    box("part_pantry_head", (P.PAN["door_x1"] - P.PAN["door_x0"], pt, H - P.PAN["door_h"]),
        ((P.PAN["door_x0"] + P.PAN["door_x1"]) / 2, (y0 + y1) / 2,
         (P.PAN["door_h"] + H) / 2), plaster, "ARCH", category="architecture",
        role="fixture")
    # ---- skirting (exposed wall stretches only)
    sk_h, sk_t = 0.06, 0.014
    def skirt(name, size, loc):
        box(name, size, loc, M["ceramic_white"], "ARCH", bevel=0.002,
            category="architecture", role="fixture")
    skirt("skirt_W_n", (sk_t, Y - P.W1_Y1, sk_h),
          (sk_t / 2, (P.W1_Y1 + Y) / 2, sk_h / 2))
    skirt("skirt_E_n", (sk_t, Y - P.ENTRY_Y1, sk_h),
          (X - sk_t / 2, (P.ENTRY_Y1 + Y) / 2, sk_h / 2))
    skirt("skirt_E_s", (sk_t, P.ENTRY_Y0, sk_h), (X - sk_t / 2, P.ENTRY_Y0 / 2, sk_h / 2))
    skirt("skirt_S_open", (P.SIDEBOARD["x1"] - P.SIDEBOARD["x0"], sk_t, sk_h),
          ((P.SIDEBOARD["x0"] + P.SIDEBOARD["x1"]) / 2, sk_t / 2, sk_h / 2))
    # north solid segments
    skirt("skirt_N_w", (P.GLZ_X0, sk_t, sk_h), (P.GLZ_X0 / 2, Y - sk_t / 2, sk_h / 2))
    skirt("skirt_N_e", (X - P.GLZ_X1, sk_t, sk_h),
          ((P.GLZ_X1 + X) / 2, Y - sk_t / 2, sk_h / 2))


def build_west_window(M):
    """West kitchen window: frame, sill, glazing, reveal."""
    y0, y1 = P.W1_Y0, P.W1_Y1
    z0, z1 = P.W1_SILL, P.W1_HEAD
    fd = 0.07          # frame depth
    ft = 0.06          # frame width
    cx = -P.WALL_T / 2
    # frame: 4 members
    box("w1_frame_b", (fd, y1 - y0, ft), (cx, (y0 + y1) / 2, z0 + ft / 2),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    box("w1_frame_t", (fd, y1 - y0, ft), (cx, (y0 + y1) / 2, z1 - ft / 2),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    box("w1_frame_l", (fd, ft, z1 - z0), (cx, y0 + ft / 2, (z0 + z1) / 2),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    box("w1_frame_r", (fd, ft, z1 - z0), (cx, y1 - ft / 2, (z0 + z1) / 2),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    box("w1_frame_m", (fd - 0.02, 0.035, z1 - z0), (cx, (y0 + y1) / 2, (z0 + z1) / 2),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    # glazing
    box("w1_glass", (0.008, y1 - y0 - 2 * ft + 0.01, z1 - z0 - 2 * ft + 0.01),
        (cx, (y0 + y1) / 2, (z0 + z1) / 2), M["glass_low_iron"], "ARCH", bevel=0,
        category="architecture", role="visual_only")
    # interior sill board
    box("w1_sill", (0.16, y1 - y0 + 0.10, 0.03), (0.02, (y0 + y1) / 2, z0 - 0.015),
        M["stone_threshold"], "ARCH", bevel=0.003, category="architecture",
        role="fixture")
    # herb pot sits on sill (props module)
    # exterior head drip + reveal trim
    box("w1_reveal_ext", (0.02, y1 - y0 + 0.06, 0.05),
        (-P.WALL_T - 0.01, (y0 + y1) / 2, z1 + 0.025), M["steel_dark"], "ARCH",
        category="architecture", role="fixture")


def build_terrace_glazing(M):
    """North full-height sliding system: bottom track, head, mullions, 4 leaves."""
    x0, x1 = P.GLZ_X0, P.GLZ_X1
    yw = P.ROOM_Y                      # wall inner face
    head = P.GLZ_HEAD
    # bottom track (recessed channel + threshold)
    box("glz_track", (x1 - x0, 0.16, 0.024), ((x0 + x1) / 2, yw + 0.08, 0.012),
        M["steel_brushed"], "ARCH", bevel=0.002, category="architecture", role="fixture")
    box("glz_threshold", (x1 - x0, 0.05, 0.006), ((x0 + x1) / 2, yw + 0.155, 0.003),
        M["stone_threshold"], "ARCH", bevel=0.001, category="architecture",
        role="fixture")
    # head track
    box("glz_head", (x1 - x0, 0.14, 0.08), ((x0 + x1) / 2, yw + 0.07, head - 0.04),
        M["steel_dark"], "ARCH", category="architecture", role="fixture")
    # vertical frame members at ends + mullions
    for i, mx in enumerate(P.GLZ_MULLIONS):
        box(f"glz_mull_{i}", (0.07, 0.10, head - 0.06), (mx, yw + 0.05, head / 2),
            M["steel_dark"], "ARCH", bevel=0.002, category="architecture",
            role="fixture")
    # 4 leaves: leaves 1,4 fixed; leaves 2,3 sliding (interlocked on 2 tracks)
    leaf_w = (x1 - x0) / 4
    ys = [yw + 0.045, yw + 0.115]      # outer/inner track plane centers
    for li in range(4):
        lx = x0 + leaf_w * (li + 0.5)
        track = ys[0] if li in (0, 3) else ys[1]
        gl = box(f"glz_leaf_{li}", (leaf_w - 0.085, 0.024, head - 0.10),
                 (lx, track, head / 2), M["glass_low_iron"], "ARCH", bevel=0,
                 category="architecture", role="visual_only")
        # leaf frame stiles
        for sx in (-1, 1):
            box(f"glz_leaf_{li}_stile_{sx}", (0.045, 0.034, head - 0.10),
                (lx + sx * (leaf_w - 0.085) / 2, track, head / 2),
                M["steel_dark"], "ARCH", bevel=0.002, category="architecture",
                role="fixture")
        box(f"glz_leaf_{li}_rail_b", (leaf_w - 0.085, 0.034, 0.045),
            (lx, track, 0.10), M["steel_dark"], "ARCH", bevel=0.002,
            category="architecture", role="fixture")
        box(f"glz_leaf_{li}_rail_t", (leaf_w - 0.085, 0.034, 0.045),
            (lx, track, head - 0.10), M["steel_dark"], "ARCH", bevel=0.002,
            category="architecture", role="fixture")
        if li in (1, 2):
            # vertical pull handle on sliding leaves
            hx = lx + (0.05 if li == 1 else -0.05)
            h = cyl(f"glz_handle_{li}", 0.011, 1.05, (hx, track - 0.045, head / 2),
                    M["bronze"], "ARCH", verts=16)
            for hz in (-0.42, 0.42):
                cyl(f"glz_handle_{li}_st{hz}", 0.006, 0.045, (hx, track - 0.024, head / 2 + hz),
                    M["bronze"], "ARCH", rot=(math.pi / 2, 0, 0), verts=12)


def build_terrace(M):
    X, Y = P.ROOM_X, P.ROOM_Y
    ty0, ty1 = P.TER_Y0, P.TER_Y1
    tx0, tx1 = P.GLZ_X0, P.GLZ_X1
    # terrace slab
    box("terrace_slab", (tx1 - tx0 + 1.2, ty1 - ty0 + 0.6, 0.12),
        ((tx0 + tx1) / 2, (ty0 + ty1) / 2 - 0.1, P.TER_Z - 0.06),
        M["wet_terrace_tile"], "EXTERIOR", category="architecture", role="fixture")
    # linear drain slot + grate at door line
    box("terrace_drain_slot", (tx1 - tx0, 0.06, 0.05),
        ((tx0 + tx1) / 2, P.DRAIN_Y, P.TER_Z - 0.028), M["rubber_black"], "EXTERIOR",
        bevel=0, category="architecture", role="fixture")
    grate = box("terrace_drain_grate", (tx1 - tx0, 0.045, 0.012),
                ((tx0 + tx1) / 2, P.DRAIN_Y, P.TER_Z - 0.004), M["steel_brushed"],
                "EXTERIOR", bevel=0.001, category="architecture", role="fixture")
    # puddle films (thin water)
    for i, (px, py, pr) in enumerate([(4.4, 8.4, 0.5), (6.6, 8.9, 0.35), (3.6, 8.0, 0.28)]):
        c = cyl(f"puddle_{i}", pr, 0.004, (px, py, P.TER_Z + 0.001),
                M["water_film"], "EXTERIOR", verts=24)
    # glass balustrade + bronze posts
    gy = P.GUARD_Y
    n_post = 7
    for i in range(n_post):
        px = tx0 - 0.4 + (tx1 - tx0 + 0.8) * i / (n_post - 1)
        box(f"guard_post_{i}", (0.05, 0.05, 1.10), (px, gy, P.TER_Z + 0.55),
            M["bronze"], "EXTERIOR", category="architecture", role="fixture")
    box("guard_glass", (tx1 - tx0 + 0.8, 0.02, 1.02),
        ((tx0 + tx1) / 2, gy, P.TER_Z + 0.60), M["glass_low_iron"], "EXTERIOR",
        bevel=0, category="architecture", role="visual_only")
    box("guard_rail", (tx1 - tx0 + 0.8, 0.06, 0.04),
        ((tx0 + tx1) / 2, gy, P.TER_Z + 1.12), M["bronze"], "EXTERIOR",
        category="architecture", role="fixture")
    # planters along guard
    for i, px in enumerate((4.1, 6.9)):
        box(f"terrace_planter_{i}", (1.1, 0.42, 0.45), (px, ty1 - 0.45, P.TER_Z + 0.225),
            M["ceramic_white"], "EXTERIOR", bevel=0.01, category="architecture",
            role="fixture")
        box(f"terrace_planter_{i}_soil", (1.0, 0.34, 0.05),
            (px, ty1 - 0.45, P.TER_Z + 0.44), M["soil"], "EXTERIOR", bevel=0,
            category="architecture", role="fixture")


def build_entry(M):
    """Entry door (ajar into hall), frame, hallway stub, floor transition."""
    X = P.ROOM_X
    y0, y1 = P.ENTRY_Y0, P.ENTRY_Y1
    h = P.ENTRY_H
    fd, ft = 0.09, 0.055
    cxE = X + P.WALL_T / 2
    for nm, sy, sz, size in (
            ("entry_frame_l", y0 + ft / 2, h / 2, (fd, ft, h)),
            ("entry_frame_r", y1 - ft / 2, h / 2, (fd, ft, h)),
            ("entry_frame_t", (y0 + y1) / 2, h - ft / 2, (fd, y1 - y0, ft))):
        box(nm, size, (cxE, sy, sz), M["oak"], "ARCH", category="architecture",
            role="fixture")
    # door leaf, hinged at north jamb, ajar 24 deg into hallway
    hinge = (cxE, y1 - 0.02, h / 2)
    leaf = box("entry_door_leaf", (0.045, y1 - y0 - 0.04 - 0.006, h - 0.02),
               (0, 0, 0), M["oak"], "ARCH", bevel=0.003,
               oid="entry_door", category="architecture", role="container",
               static=False)
    leaf.data.transform(__import__("mathutils").Matrix.Translation(
        (0, -(y1 - y0 - 0.04 - 0.006) / 2, 0)))
    leaf.location = hinge
    leaf.rotation_euler = (0, 0, math.radians(-24))
    bar = cyl("entry_door_handle", 0.010, 0.14, (0.06, -0.07, 0.05), M["bronze"],
              "ARCH", rot=(0, math.pi / 2, 0), verts=14)
    bar.parent = leaf
    # hallway stub
    hx0, hx1 = P.HALL["x0"], P.HALL["x1"]
    hy0, hy1 = P.HALL["y0"], P.HALL["y1"]
    hh = P.HALL["h"]
    box("hall_floor", (hx1 - hx0 + 0.3, hy1 - hy0, 0.05),
        ((hx0 + hx1) / 2, (hy0 + hy1) / 2, -0.025), M["stone_tile"], "ARCH",
        category="architecture", role="fixture")
    box("hall_ceil", (hx1 - hx0 + 0.3, hy1 - hy0, 0.08),
        ((hx0 + hx1) / 2, (hy0 + hy1) / 2, hh + 0.04), M["ceiling_white"], "ARCH",
        category="architecture", role="fixture")
    box("hall_wall_S", (hx1 - hx0 + 0.3, 0.1, hh), ((hx0 + hx1) / 2, hy0 - 0.05, hh / 2),
        M["plaster"], "ARCH", category="architecture", role="fixture")
    box("hall_wall_N", (hx1 - hx0 + 0.3, 0.1, hh), ((hx0 + hx1) / 2, hy1 + 0.05, hh / 2),
        M["plaster"], "ARCH", category="architecture", role="fixture")
    box("hall_wall_E", (0.1, hy1 - hy0, hh), (hx1 + 0.05, (hy0 + hy1) / 2, hh / 2),
        M["plaster"], "ARCH", category="architecture", role="fixture")
    # coat hooks + console mirror hint
    for i in range(3):
        cyl(f"hall_hook_{i}", 0.012, 0.06, (hx0 + 0.35 + 0.18 * i, hy0 + 0.06, 1.6),
            M["bronze"], "ARCH", rot=(math.pi / 2, 0, 0), verts=10)
    # floor transition: stone tile patch at entry zone (sits 1mm above oak)
    box("entry_tile_zone", (P.ROOM_X - 7.9, 5.2 - 2.4, 0.002),
        ((7.9 + X) / 2, (2.4 + 5.2) / 2, 0.001), M["stone_tile"], "ARCH", bevel=0,
        oid="entry_tile_zone", category="architecture", role="fixture")
    box("entry_transition_strip", (0.035, 5.2 - 2.4, 0.006),
        (7.9, (2.4 + 5.2) / 2, 0.003), M["bronze"], "ARCH", bevel=0.001,
        category="architecture", role="fixture")
    # doormat
    box("doormat", (0.75, 0.5, 0.012), (9.05, 3.85, 0.008), M["doormat"], "ARCH",
        bevel=0.004, oid="doormat", category="props", role="visual_only")


def build_exterior(M):
    """Layered city context: neighbor facades, window grids, distant hazy blocks."""
    X, Y = P.ROOM_X, P.ROOM_Y
    # north neighbor building (behind terrace)
    box("city_bldg_N", (30.0, 7.0, 17.0), (5.0, 15.6, 8.5 - 0.02), M["facade"],
        "EXTERIOR", bevel=0, category="architecture", role="visual_only")
    # window grid on its south facade (facing us), recessed boxes + occasional glow
    for row in range(4):
        for col in range(11):
            wx = -5.4 + col * 1.9
            wz = 2.4 + row * 3.2
            lit = (row * 11 + col) % 5 in (2, 4)
            box(f"city_win_N_{row}_{col}", (1.15, 0.10, 1.6), (wx, 12.10, wz),
                M["window_glow"] if lit else M["glass_frosted"], "EXTERIOR",
                bevel=0, category="architecture", role="visual_only")
    # west neighbor (seen through W1)
    box("city_bldg_W", (6.0, 18.0, 14.0), (-6.4, 3.0, 7.0 - 0.02), M["facade_b"],
        "EXTERIOR", bevel=0, category="architecture", role="visual_only")
    for row in range(3):
        for col in range(6):
            wy = -4.0 + col * 2.6
            wz = 2.2 + row * 3.4
            lit = (row * 6 + col) % 4 in (1, 3)
            box(f"city_win_W_{row}_{col}", (0.10, 1.5, 1.7), (-3.40, wy, wz),
                M["window_glow"] if lit else M["glass_frosted"], "EXTERIOR",
                bevel=0, category="architecture", role="visual_only")
    # distant hazy blocks
    rnd = __import__("random").Random(11)
    for i in range(26):
        bx = rnd.uniform(-45, 55)
        by = rnd.uniform(34, 75)
        bw = rnd.uniform(6, 16)
        bd = rnd.uniform(6, 14)
        bh = rnd.uniform(9, 42)
        box(f"city_far_{i}", (bw, bd, bh), (bx, by, bh / 2 - 0.02), M["sky_haze"],
            "EXTERIOR", bevel=0, category="architecture", role="visual_only")
    # ground plane far below terrace level to avoid void
    box("city_ground", (220, 220, 0.2), (5, 20, -3.5), M["facade_b"], "EXTERIOR",
        bevel=0, category="architecture", role="visual_only")
