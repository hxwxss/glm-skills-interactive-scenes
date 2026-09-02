"""kit_lighting.py — world, daylight, interior fixtures, controllable light groups."""

import math
import bpy

import kit_params as P
import kit_util as U
from kit_util import box, cyl, REG


def _m(name):
    return bpy.data.materials[name]


def _light(name, type_, loc, energy, color=(1, 1, 1), size=0.1, size_y=None,
           rot=(0, 0, 0), group=None, spot_size=None, col="LIGHTING"):
    ld = bpy.data.lights.new(name, type_)
    ld.energy = energy
    ld.color = color
    if type_ == "AREA":
        ld.size = size
        if size_y:
            ld.shape = "RECTANGLE"
            ld.size_y = size_y
    elif type_ == "POINT":
        ld.shadow_soft_size = size
    elif type_ == "SPOT" and spot_size:
        ld.spot_size = spot_size
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    U.link(ob, col)
    if group:
        ob["light_group"] = group
        ob["base_energy"] = energy
        REG.lights.setdefault(group, []).append(name)
    return ob


def build_world():
    w = bpy.data.worlds.new("kitchen_world")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    # overcast sky gradient: zenith cool, horizon bright
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = -0.15
    mp.inputs["From Max"].default_value = 0.7
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mp.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.86, 0.88, 0.90, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.52, 0.62, 0.76, 1)
    nt.links.new(mp.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.45
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def build_lighting():
    build_world()
    cool = (0.93, 0.96, 1.0)
    warm = (1.0, 0.86, 0.68)
    # key soft daylight bank outside terrace glazing (overcast)
    _light("daylight_key", "AREA", (5.7, 11.6, 5.2), 2800, cool, size=8.0,
           size_y=3.2, rot=(math.radians(-58), 0, 0))
    # softer fill lower, angles into room
    _light("daylight_fill", "AREA", (4.0, 10.2, 2.2), 900, cool, size=6.0,
           size_y=2.0, rot=(math.radians(-75), 0, 0))
    # west window fill
    _light("window_fill_W", "AREA", (-2.2, 2.9, 2.1), 220, cool, size=2.4,
           size_y=1.6, rot=(0, math.radians(-72), 0))
    # exterior ambient so terrace/city read
    _light("exterior_amb", "AREA", (5.7, 14.5, 9.0), 900, (0.88, 0.92, 0.98),
           size=12.0, size_y=8.0, rot=(math.radians(-32), 0, 0), col="EXTERIOR")
    _light("hall_light", "POINT", (10.7, 3.85, 2.35), 30, (1.0, 0.80, 0.58),
           size=0.06, col="ARCH")
    # recessed downlights (GENERAL)
    spots = [(1.30, 2.60), (1.30, 5.90), (3.60, 2.20), (3.60, 6.60),
             (5.20, 3.40), (7.30, 3.40), (8.60, 5.00), (7.90, 6.70)]
    for i, (sx, sy) in enumerate(spots):
        _light(f"downlight_{i}", "POINT", (sx, sy, 2.90), 22, warm, size=0.05,
               group="LIGHTING_GENERAL")
        cyl(f"downlight_trim_{i}", 0.045, 0.012, (sx, sy, 2.994),
            _m("steel_dark"), "LIGHTING", verts=20)
        cyl(f"downlight_lens_{i}", 0.034, 0.004, (sx, sy, 2.988),
            _m("emissive_soft"), "LIGHTING", verts=20)
    # under-cabinet strips (GENERAL)
    _light("uc_light_a", "AREA", (0.09, 4.45, 1.435), 7, warm, size=0.95,
           size_y=0.04, rot=(math.radians(-90), 0, math.radians(90)),
           group="LIGHTING_GENERAL")
    _light("uc_light_b", "AREA", (0.09, 6.05, 1.435), 5, warm, size=0.55,
           size_y=0.04, rot=(math.radians(-90), 0, math.radians(90)),
           group="LIGHTING_GENERAL")
    # island pendants (GENERAL task)
    for i, (px, py) in enumerate(P.PENDANT_ISLAND):
        _light(f"pendant_island_{i}_light", "POINT", (px, py, P.PEND_DROP + 0.04),
               10, warm, size=0.05, group="LIGHTING_GENERAL")
    # dining pendants (DINING) — default off
    for i, px in enumerate(P.PENDANT_DINING_XS):
        _light(f"pendant_dining_{i}_light", "POINT", (px, P.DINING["cy"],
               P.PEND_DROP + 0.06), 0, warm, size=0.05, group="LIGHTING_DINING")
    # pantry ceiling light (GENERAL)
    _light("pantry_light_src", "AREA", (9.0, 1.2, 2.83), 12, warm, size=0.5,
           size_y=0.12, rot=(math.radians(-90), 0, 0), group="LIGHTING_GENERAL")


def set_light_group_state(group, factor):
    """Deterministic control entry point; also used by validation/renders."""
    names = REG.lights.get(group, [])
    for nm in names:
        ob = bpy.data.objects.get(nm)
        if ob and ob.type == "LIGHT":
            ob.data.energy = ob.get("base_energy", ob.data.energy) * factor
    return len(names)
