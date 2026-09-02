"""kit_util.py — mesh toolkit, collections, registry for the kitchen build.

Conventions:
- All builders return the created bpy object.
- `reg` (Registry) accumulates IR records as the scene is built; kit_ir serializes it.
- Articulated parts: mesh origin is placed ON the mechanical pivot so a single
  rotation_euler/translation change is the whole state model (deterministic reset).
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

import kit_params as P

TAU = math.tau


# ------------------------------------------------------------------ registry
class Registry:
    def __init__(self):
        self.objects = {}      # id -> ir record dict
        self.joints = {}       # joint_id -> dict
        self.lights = {}       # group -> [ids]
        self.cameras = {}      # cam name -> record
        self.proxies = {}      # proxy obj name -> owner id
        self.tasks = P.TASKS
        self.uncertainties = []
        self.name_by_id = {}   # id -> blender object name

    def add_object(self, oid, obj, category, role, dims, material, static=True,
                   mass=None, parent=None, support=None, collision="box_aabb",
                   extra=None):
        rec = dict(
            stable_id=oid, blender_name=obj.name, category=category,
            semantic_role=role, collection=obj.users_collection[0].name if obj.users_collection else "",
            dimensions=list(dims), material_class=material, static=static,
            mass_estimate_kg=mass, parent=parent, support=support,
            collision=collision,
        )
        if extra:
            rec.update(extra)
        self.objects[oid] = rec
        self.name_by_id[oid] = obj.name
        return rec

    def add_joint(self, jd, obj, pivot, axis_vec, handle_region, clearance,
                  allowed_contacts, collision_ids):
        jd = dict(jd)  # copy of seed
        jd.update(dict(
            blender_object=obj.name, pivot_world=list(pivot), axis_local=list(axis_vec),
            handle_grasp_region=handle_region, swept_volume_clearance=clearance,
            allowed_contacts=allowed_contacts, task_critical_collision=collision_ids,
            default_state=jd["states"].get("closed", 0),
        ))
        self.joints[jd["id"]] = jd
        # stamp persistent control metadata onto the object (survives save/load)
        import json as _json
        obj["joint_id"] = jd["id"]
        obj["joint_type"] = jd["type"]
        obj["joint_axis"] = jd["axis_local"]
        obj["joint_pivot"] = jd["pivot_world"]
        obj["joint_states_json"] = _json.dumps(jd["states"])
        obj["joint_default"] = jd.get("default_state", 0)
        obj["joint_limits"] = jd["limits"]
        return jd


REG = Registry()


# ---------------------------------------------------------------- collections
def make_collections():
    cols = {}
    for name in ("ARCH", "CABINETRY", "APPLIANCES", "FURNITURE", "PROPS",
                 "LIGHTING", "CAMERAS", "EXTERIOR", "PROXIES", "INTERACTION"):
        c = bpy.data.collections.get(name)
        if c is None:
            c = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(c)
        cols[name] = c
    return cols


COLS = {}


def link(obj, col_name):
    col = COLS.get(col_name)
    if col is None:
        col = bpy.context.scene.collection
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


# ---------------------------------------------------------------- primitives
def _finish(obj, smooth=False, edge_split_angle=0.44):
    if smooth:
        mesh_smooth(obj)
    else:
        add_edge_split(obj, edge_split_angle)
    return obj


def mesh_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


def bake_scale(obj):
    """Bake object scale into the mesh (keeps world size, resets scale to 1).

    Required for correct texture mapping (Object coords), correct bevel widths,
    and undistorted child objects. Call after any mesh-space hinge shifts."""
    if obj.type != "MESH":
        return obj
    sx, sy, sz = obj.scale
    if (abs(sx - 1) > 1e-9 or abs(sy - 1) > 1e-9 or abs(sz - 1) > 1e-9):
        obj.data.transform(Matrix.Diagonal((sx, sy, sz, 1.0)))
        obj.scale = (1.0, 1.0, 1.0)
    return obj


def add_edge_split(obj, angle=0.44):
    m = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    m.split_angle = angle
    m.use_edge_angle = True
    m.use_edge_sharp = False


def add_bevel(obj, width=0.0025, segments=2, angle=0.6):
    if width <= 0:
        return
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = angle
    m.harden_normals = False
    m.miter_outer = "MITER_ARC"


def box(name, size, loc, mat=None, col="PROPS", rot=(0, 0, 0), bevel=0.002,
        pivot="center", oid=None, category="prop", role="distractor",
        static=True, mass=None, smooth=False, parent=None, edge_angle=0.44):
    """Create a bevelled box. pivot: 'center' | 'min' (loc = min corner)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.scale = (size[0], size[1], size[2])
    if pivot == "min":
        off = Vector(size) * 0.5
    else:
        off = Vector((0, 0, 0))
    obj.location = Vector(loc) + Euler(rot).to_matrix() @ off
    obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    bake_scale(obj)
    if mat is not None:
        set_mat(obj, mat)
    if bevel:
        add_bevel(obj, min(bevel, 0.3 * min(size)))
    _finish(obj, smooth, edge_angle)
    if parent is not None:
        obj.parent = parent
    if oid:
        REG.add_object(oid, obj, category, role, size, mat_name(mat), static, mass)
    return obj


def cyl(name, r, depth, loc, mat=None, col="PROPS", rot=(0, 0, 0), verts=32,
        cap=True, smooth=True, oid=None, category="prop", role="distractor",
        static=True, mass=None, parent=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts,
                          radius1=r, radius2=r, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    if mat is not None:
        set_mat(obj, mat)
    _finish(obj, smooth)
    if parent is not None:
        obj.parent = parent
    if oid:
        REG.add_object(oid, obj, category, role, (2 * r, 2 * r, depth), mat_name(mat),
                       static, mass)
    return obj


def tube(name, r_out, r_in, depth, loc, mat=None, col="PROPS", rot=(0, 0, 0), verts=32,
         smooth=True, parent=None):
    """Hollow tube: circle profile + solidify (centered on loc, along local Z)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, segments=verts, radius=r_out)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    set_mat(obj, mat)
    sol = obj.modifiers.new("Solidify", "SOLIDIFY")
    sol.thickness = r_out - r_in
    sol.offset = 0.0
    if smooth:
        mesh_smooth(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def sphere(name, r, loc, mat=None, col="PROPS", scale=(1, 1, 1), segs=24, rings=16,
           oid=None, category="prop", role="distractor", static=True, parent=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.scale = scale
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    bake_scale(obj)
    if mat is not None:
        set_mat(obj, mat)
    mesh_smooth(obj)
    if parent is not None:
        obj.parent = parent
    if oid:
        REG.add_object(oid, obj, category, role, (2 * r * scale[0], 2 * r * scale[1],
                       2 * r * scale[2]), mat_name(mat), static, None)
    return obj


def torus_seg(name, R, r, loc, rot=(0, 0, 0), arc=math.pi, major=24, minor=10,
              mat=None, col="PROPS", parent=None):
    """Partial torus around local Z (arc starts at +X, sweeps CCW)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts_top, verts_bot = [], []
    for i in range(major + 1):
        a = arc * i / major
        ca, sa = math.cos(a), math.sin(a)
        for j in range(minor):
            b = TAU * j / minor
            rr = R + r * math.cos(b)
            z = r * math.sin(b)
            verts_top.append(bm.verts.new((rr * ca, rr * sa, z)))
    bm.verts.ensure_lookup_table()
    for i in range(major):
        for j in range(minor):
            j2 = (j + 1) % minor
            v1 = verts_top[i * minor + j]
            v2 = verts_top[i * minor + j2]
            v3 = verts_top[(i + 1) * minor + j2]
            v4 = verts_top[(i + 1) * minor + j]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    if mat is not None:
        set_mat(obj, mat)
    mesh_smooth(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def revolve(name, profile, loc, mat=None, col="PROPS", rot=(0, 0, 0), segs=40,
            oid=None, category="prop", role="distractor", static=True, parent=None,
            close_bottom=True, mass=None):
    """Revolve a (radius, z) profile polyline around the Z axis.

    profile: list of (r, z) from bottom to top. Produces a closed surface when the
    profile starts and ends at r=0, otherwise open ends (fine for hidden rims).
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    ring_verts = []
    n = len(profile)
    for i, (r, z) in enumerate(profile):
        ring = []
        for k in range(segs):
            a = TAU * k / segs
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        bm.verts.ensure_lookup_table()
        ring_verts.append(ring)
    for i in range(n - 1):
        r0, r1 = profile[i][0], profile[i + 1][0]
        for k in range(segs):
            k2 = (k + 1) % segs
            try:
                if r0 < 1e-6:
                    f = bm.faces.new((ring_verts[i][k], ring_verts[i + 1][k],
                                      ring_verts[i + 1][k2]))
                elif r1 < 1e-6:
                    f = bm.faces.new((ring_verts[i][k], ring_verts[i][k2],
                                      ring_verts[i + 1][k2]))
                else:
                    f = bm.faces.new((ring_verts[i][k], ring_verts[i][k2],
                                      ring_verts[i + 1][k2], ring_verts[i + 1][k]))
            except ValueError:
                pass
    if close_bottom and profile[0][0] > 1e-6:
        try:
            bm.faces.new(list(reversed(ring_verts[0])))
        except ValueError:
            pass
    if profile[-1][0] > 1e-6:
        try:
            bm.faces.new(ring_verts[-1])
        except ValueError:
            pass
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    if mat is not None:
        set_mat(obj, mat)
    mesh_smooth(obj)
    if parent is not None:
        obj.parent = parent
    if oid:
        rr = max(p[0] for p in profile)
        hh = profile[-1][1] - profile[0][1]
        REG.add_object(oid, obj, category, role, (2 * rr, 2 * rr, hh), mat_name(mat),
                       static, mass)
    return obj


def curve_tube(name, points, radius, loc=(0, 0, 0), mat=None, col="PROPS",
               res=6, bevel_res=3, parent=None):
    """Tube sweep through a polyline of world-space points (local to loc)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = bevel_res
    cu.resolution_u = res
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    obj = bpy.data.objects.new(name, cu)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    link(obj, col)
    if mat is not None:
        set_mat(obj, mat)
    if parent is not None:
        obj.parent = parent
    return obj


# ---------------------------------------------------------------- materials
def set_mat(obj, mat):
    if obj.data is None:
        return
    if isinstance(mat, str):
        m = bpy.data.materials.get(mat)
        if m is None:
            raise KeyError(f"material '{mat}' not created yet")
        mat = m
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def mat_name(mat):
    if mat is None:
        return "none"
    return mat if isinstance(mat, str) else mat.name


# ---------------------------------------------------------------- joint utils
def set_origin(obj, world_point):
    """Move obj's mesh origin to world_point (keeps world pose)."""
    inv = obj.matrix_world.inverted()
    local = inv @ Vector(world_point)
    obj.data.transform(Matrix.Translation(-local))
    obj.location = obj.matrix_world @ Vector(local)


def make_drawer(oid_prefix, name, front_w, front_h, box_w, box_d, box_h,
                front_world, slide_dir, mat_front, mat_box, col="CABINETRY",
                handle=True, handle_mat=None):
    """Drawer = front panel + real box (sides/bottom/back), assembly origin (empty
    root) at the center of the front panel.

    slide_dir: '+X','-X','+Y','-Y' = pull-out direction (also the front normal).
    front_world: world position of the front panel center (at closed state).
    Child parts are authored in root-local coordinates (strict parenting).
    Returns (root, front).
    """
    d = Vector((1, 0, 0)) if slide_dir == "+X" else Vector((-1, 0, 0)) if         slide_dir == "-X" else Vector((0, 1, 0)) if slide_dir == "+Y" else         Vector((0, -1, 0))
    lateral = Vector((0, 1, 0)) if d.x != 0 else Vector((1, 0, 0))
    root = bpy.data.objects.new(name + "_root", None)
    root.location = front_world
    bpy.context.scene.collection.objects.link(root)
    link(root, col)
    ft = 0.019
    bot_t = 0.012
    side_t = 0.014
    # front panel (thickness along slide dir, width along lateral)
    fsize = (ft, front_w, front_h) if d.x != 0 else (front_w, ft, front_h)
    front = box(name + "_front", fsize, (0, 0, 0), mat_front, col, bevel=0.0015,
                parent=root)
    # box behind front
    cx = -d.x * (ft / 2 + box_d / 2)
    cy = -d.y * (ft / 2 + box_d / 2)
    z0 = -front_h / 2
    if d.x != 0:
        side_size = (box_d, side_t, box_h)
        back_size = (side_t, box_w - 2 * side_t, box_h)
        bot_size = (box_d, box_w - 2 * side_t, bot_t)
        ly1, ly2 = cy, cy
    else:
        side_size = (side_t, box_d, box_h)
        back_size = (box_w - 2 * side_t, side_t, box_h)
        bot_size = (box_w - 2 * side_t, box_d, bot_t)
        ly1, ly2 = cx, cx
    zc = z0 + bot_t + box_h / 2
    sa = lateral * (box_w / 2 - side_t / 2)
    box(name + "_boxA", side_size,
        (cx + sa.x, cy + sa.y, zc), mat_box, col, bevel=0.001, parent=root)
    box(name + "_boxB", side_size,
        (cx - sa.x, cy - sa.y, zc), mat_box, col, bevel=0.001, parent=root)
    # back of box (away from pull direction)
    bx = cx - d.x * (box_d / 2 - side_t / 2)
    by = cy - d.y * (box_d / 2 - side_t / 2)
    box(name + "_boxBack", back_size, (bx if d.x else cx, by if d.y else cy, zc),
        mat_box, col, bevel=0.001, parent=root)
    box(name + "_boxBot", bot_size, (cx, cy, z0 + bot_t / 2), mat_box, col,
        bevel=0.0008, parent=root)
    if handle:
        hz = front_h / 2 - 0.045
        bar_len = min(0.32, front_w * 0.55)
        off_s = ft / 2 + 0.014
        off_b = ft / 2 + 0.042
        if d.x != 0:
            rot_s = (math.pi / 2, 0, 0)
            for sy in (-bar_len / 2, bar_len / 2):
                cyl(name + "_hstand", 0.005, 0.028,
                    (d.x * off_s, sy, hz), handle_mat or mat_front, col,
                    rot=rot_s, verts=10, parent=root)
            cyl(name + "_hbar", 0.008, bar_len, (d.x * off_b, 0, hz),
                handle_mat or mat_front, col, rot=rot_s, verts=14, parent=root)
        else:
            rot_s = (0, math.pi / 2, 0)
            for sx in (-bar_len / 2, bar_len / 2):
                cyl(name + "_hstand", 0.005, 0.028,
                    (sx, d.y * off_s, hz), handle_mat or mat_front, col,
                    rot=rot_s, verts=10, parent=root)
            cyl(name + "_hbar", 0.008, bar_len, (0, d.y * off_b, hz),
                handle_mat or mat_front, col, rot=rot_s, verts=14, parent=root)
    if oid_prefix:
        REG.add_object(oid_prefix + "_front", front, "cabinetry", "container",
                       fsize, mat_name(mat_front), static=False,
                       parent=name + "_root")
    return root, front


def make_proxy(oid, obj, margin=0.002):
    """Hidden collision proxy box tightly wrapping obj's local bbox."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    bb = [Vector(c) for c in ev.bound_box]
    mn = Vector((min(c.x for c in bb), min(c.y for c in bb), min(c.z for c in bb)))
    mx = Vector((max(c.x for c in bb), max(c.y for c in bb), max(c.z for c in bb)))
    size = mx - mn + Vector((margin * 2, margin * 2, margin * 2))
    ctr = obj.matrix_world @ ((mn + mx) / 2)
    if size.length < 1e-9:
        return None
    p = box(f"PROXY_{oid}", tuple(size), tuple(ctr), None, "PROXIES", bevel=0)
    p.hide_render = True
    p.hide_viewport = True
    REG.proxies[p.name] = oid
    return p


def scene_objects():
    return [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("PROXY_")]
