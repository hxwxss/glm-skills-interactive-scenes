"""kit_materials.py — self-contained procedural material library (Principled BSDF).

No external textures. Every material distinguishes itself via base color, roughness
(variation), normal detail, metallic/transmission/sheen response.
"""

import bpy


def _new(name):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf, out


def _noise_bump(nt, bsdf, scale=8.0, detail=6.0, strength=0.05, distortion=0.0,
                roughness_in=None, coord="Generated"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-700, 0)
    nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.location = (-500, 0)
    no.inputs["Scale"].default_value = scale
    no.inputs["Detail"].default_value = detail
    no.inputs["Distortion"].default_value = distortion
    nt.links.new(mp.outputs["Vector"], no.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.location = (-200, -200)
    bp.inputs["Strength"].default_value = strength
    nt.links.new(no.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    if roughness_in is not None:
        rr = nt.nodes.new("ShaderNodeMapRange")
        rr.location = (-200, 100)
        rr.inputs["From Min"].default_value = 0.0
        rr.inputs["From Max"].default_value = 1.0
        rr.inputs["To Min"].default_value = roughness_in[0]
        rr.inputs["To Max"].default_value = roughness_in[1]
        nt.links.new(no.outputs["Fac"], rr.inputs["Value"])
        nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    return no, mp, tc


def simple(name, base, rough, metal=0.0, transmission=0.0, ior=1.45,
           bump_scale=0.0, bump_strength=0.05, rough_var=None, sheen=0.0,
           specular=0.5, coord="Generated", alpha=1.0, emit=0.0, emit_color=None):
    m, nt, bsdf, out = _new(name)
    bsdf.inputs["Base Color"].default_value = (*base, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    if transmission > 0:
        bsdf.inputs["Transmission Weight"].default_value = transmission
        bsdf.inputs["IOR"].default_value = ior
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    if emit > 0:
        bsdf.inputs["Emission Color"].default_value = (*(emit_color or base), 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    if bump_scale > 0:
        _noise_bump(nt, bsdf, scale=bump_scale, strength=bump_strength,
                    roughness_in=rough_var, coord=coord)
    elif rough_var is not None:
        no, mp, tc = _noise_bump(nt, bsdf, scale=4, strength=0, roughness_in=rough_var,
                                 coord=coord)
        nt.links.remove(bsdf.inputs["Normal"].links[0])
    return m


def wood_floor():
    name = "oak_floor"
    m, nt, bsdf, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 1, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    # plank layout: object coords, planks run along X, width 0.19
    sc = nt.nodes.new("ShaderNodeTexBrick")
    sc.offset = 0.5
    sc.inputs["Scale"].default_value = 1.0
    sc.inputs["Color1"].default_value = (1, 1, 1, 1)
    sc.inputs["Color2"].default_value = (1, 1, 1, 1)
    sc.inputs["Mortar"].default_value = (0, 0, 0, 1)
    sc.inputs["Mortar Size"].default_value = 0.004
    sc.inputs["Bias"].default_value = 0.0
    sc.inputs["Brick Width"].default_value = 1.6
    sc.inputs["Row Height"].default_value = 0.19
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = (1, 1, 1)
    nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
    nt.links.new(mp2.outputs["Vector"], sc.inputs["Vector"])
    # grain: stretched noise + wave
    mp3 = nt.nodes.new("ShaderNodeMapping")
    mp3.inputs["Scale"].default_value = (1.2, 60.0, 6.0)
    nt.links.new(tc.outputs["Object"], mp3.inputs["Vector"])
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = 9.0
    no.inputs["Detail"].default_value = 8.0
    no.inputs["Distortion"].default_value = 0.4
    nt.links.new(mp3.outputs["Vector"], no.inputs["Vector"])
    wav = nt.nodes.new("ShaderNodeTexWave")
    wav.inputs["Scale"].default_value = 1.1
    wav.inputs["Distortion"].default_value = 6.0
    wav.inputs["Detail"].default_value = 2.0
    wav.bands_direction = "Y"
    nt.links.new(mp3.outputs["Vector"], wav.inputs["Vector"])
    mixg = nt.nodes.new("ShaderNodeMix")
    mixg.data_type = "FLOAT"
    mixg.inputs[0].default_value = 0.55
    nt.links.new(no.outputs["Fac"], mixg.inputs[2])
    nt.links.new(wav.outputs["Fac"], mixg.inputs[3])
    # plank index color variation
    ramp_idx = nt.nodes.new("ShaderNodeMapRange")
    ramp_idx.inputs["To Min"].default_value = 0.0
    ramp_idx.inputs["To Max"].default_value = 1.0
    # color ramp oak
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (0.36, 0.25, 0.15, 1)
    cr.color_ramp.elements[1].color = (0.52, 0.38, 0.24, 1)
    e = cr.color_ramp.elements.new(0.5)
    e.color = (0.44, 0.31, 0.19, 1)
    mortar_dark = nt.nodes.new("ShaderNodeRGB")
    mortar_dark.outputs[0].default_value = (0.16, 0.11, 0.07, 1)
    seam_mix = nt.nodes.new("ShaderNodeMix")
    seam_mix.data_type = "RGBA"
    nt.links.new(sc.outputs["Fac"], seam_mix.inputs[0])
    nt.links.new(cr.outputs["Color"], seam_mix.inputs[6])
    nt.links.new(mortar_dark.outputs[0], seam_mix.inputs[7])
    nt.links.new(seam_mix.outputs[2], bsdf.inputs["Base Color"])
    # roughness varies with grain
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.30
    rr.inputs["To Max"].default_value = 0.55
    nt.links.new(mixg.outputs[0], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    # bump from grain + plank seams
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    nt.links.new(mixg.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def oak(name="oak", c0=(0.52, 0.35, 0.20), c1=(0.68, 0.50, 0.30), scale=(1.0, 14.0, 2.0),
        rough=0.4, coord="Object", axis_stretch=(1.2, 60.0, 3.0)):
    m, nt, bsdf, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = 6.0
    no.inputs["Detail"].default_value = 8.0
    no.inputs["Distortion"].default_value = 0.5
    nt.links.new(mp.outputs["Vector"], no.inputs["Vector"])
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = axis_stretch
    nt.links.new(tc.outputs[coord], mp2.inputs["Vector"])
    wav = nt.nodes.new("ShaderNodeTexWave")
    wav.inputs["Scale"].default_value = 2.2
    wav.inputs["Distortion"].default_value = 8.0
    wav.inputs["Detail"].default_value = 3.0
    wav.bands_direction = "Z"
    nt.links.new(mp2.outputs["Vector"], wav.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs[0].default_value = 0.6
    nt.links.new(no.outputs["Fac"], mix.inputs[2])
    nt.links.new(wav.outputs["Fac"], mix.inputs[3])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*c0, 1)
    cr.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    nt.links.new(mix.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def stone(name, c0, c1, speck=0.02, rough=0.4, bump=0.03, scale=18.0):
    m, nt, bsdf, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = scale
    no.inputs["Detail"].default_value = 10.0
    nt.links.new(tc.outputs["Generated"], no.inputs["Vector"])
    no2 = nt.nodes.new("ShaderNodeTexNoise")   # fine speckle carrier
    no2.inputs["Scale"].default_value = scale * 9.0
    no2.inputs["Detail"].default_value = 3.0
    nt.links.new(tc.outputs["Generated"], no2.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*c0, 1)
    cr.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(no.outputs["Fac"], cr.inputs["Fac"])
    dark = nt.nodes.new("ShaderNodeRGB")
    dark.outputs[0].default_value = (0.16, 0.16, 0.17, 1)
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = speck * 0.25
    mr.inputs["To Max"].default_value = min(speck * 1.6, 0.85)
    nt.links.new(no2.outputs["Fac"], mr.inputs["Value"])
    mixsp = nt.nodes.new("ShaderNodeMix")
    mixsp.data_type = "RGBA"
    mixsp.blend_type = "MIX"
    nt.links.new(cr.outputs["Color"], mixsp.inputs[6])
    nt.links.new(dark.outputs[0], mixsp.inputs[7])
    nt.links.new(mr.outputs["Result"], mixsp.inputs[0])
    nt.links.new(mixsp.outputs[2], bsdf.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = max(rough - 0.06, 0.02)
    rr.inputs["To Max"].default_value = rough + 0.06
    nt.links.new(no.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    nt.links.new(no.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def plaster(name="plaster", base=(0.845, 0.822, 0.782)):
    return simple(name, base, 0.85, bump_scale=14.0, bump_strength=0.035,
                  rough_var=(0.78, 0.92))


def brushed_metal(name, base=(0.42, 0.42, 0.44), rough=0.3, stretch=(1.0, 60.0, 60.0)):
    m, nt, bsdf, out = _new(name)
    bsdf.inputs["Base Color"].default_value = (*base, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = stretch
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = 40.0
    no.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], no.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = rough - 0.1
    rr.inputs["To Max"].default_value = rough + 0.12
    nt.links.new(no.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], bsdf.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.04
    nt.links.new(no.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def glass(name="glass_low_iron", rough=0.008, color=(0.92, 0.95, 0.94)):
    m, nt, bsdf, out = _new(name)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["IOR"].default_value = 1.5
    return m


def emissive(name, color, strength, base=None):
    m, nt, bsdf, out = _new(name)
    bsdf.inputs["Base Color"].default_value = (*(base or color), 1)
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.4
    return m


def cereal_box_mat():
    name = "cereal_graphic"
    m, nt, bsdf, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # horizontal color bands = invented generic packaging
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "LINEAR"
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, -1.5708, 0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    rmp = nt.nodes.new("ShaderNodeValToRGB")
    rmp.color_ramp.interpolation = "CONSTANT"
    rmp.color_ramp.elements[0].position = 0.0
    rmp.color_ramp.elements[0].color = (0.86, 0.42, 0.12, 1)
    rmp.color_ramp.elements[1].position = 1.0
    rmp.color_ramp.elements[1].color = (0.94, 0.86, 0.70, 1)
    e = rmp.color_ramp.elements.new(0.55)
    e.color = (0.35, 0.16, 0.10, 1)
    nt.links.new(gr.outputs["Fac"], rmp.inputs["Fac"])
    nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.42
    return m


def art_canvas(name, c_a, c_b, c_c):
    m, nt, bsdf, out = _new(name)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    no = nt.nodes.new("ShaderNodeTexNoise")
    no.inputs["Scale"].default_value = 2.2
    no.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs["Generated"], no.inputs["Vector"])
    rmp = nt.nodes.new("ShaderNodeValToRGB")
    rmp.color_ramp.interpolation = "CONSTANT"
    rmp.color_ramp.elements[0].color = (*c_a, 1)
    rmp.color_ramp.elements[1].color = (*c_b, 1)
    e = rmp.color_ramp.elements.new(0.62)
    e.color = (*c_c, 1)
    nt.links.new(no.outputs["Fac"], rmp.inputs["Fac"])
    nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.65
    return m


def build_all():
    mats = {}
    mats["plaster"] = plaster()
    mats["ceiling_white"] = simple("ceiling_white", (0.90, 0.90, 0.89), 0.9,
                                   bump_scale=20, bump_strength=0.02)
    mats["oak_floor"] = wood_floor()
    mats["stone_tile"] = stone("stone_tile", (0.62, 0.60, 0.575), (0.72, 0.70, 0.67),
                               speck=0.05, rough=0.5, bump=0.04, scale=8)
    mats["wet_terrace_tile"] = stone("wet_terrace_tile", (0.22, 0.23, 0.24),
                                     (0.32, 0.33, 0.34), speck=0.06, rough=0.22,
                                     bump=0.05, scale=8)
    mats["oak"] = oak("oak", c0=(0.42, 0.30, 0.19), c1=(0.56, 0.43, 0.28),
                      rough=0.42)
    mats["oak_dark"] = oak("oak_dark", c0=(0.26, 0.18, 0.12), c1=(0.38, 0.27, 0.18),
                           rough=0.48)
    mats["cab_front_greige"] = simple("cab_front_greige", (0.512, 0.502, 0.458), 0.44,
                                      bump_scale=30, bump_strength=0.015)
    mats["cab_body"] = simple("cab_body", (0.50, 0.49, 0.46), 0.6)
    mats["stone_worktop"] = stone("stone_worktop", (0.165, 0.165, 0.17),
                                  (0.23, 0.23, 0.24), speck=0.18, rough=0.38,
                                  bump=0.035, scale=30)
    mats["bronze"] = simple("bronze", (0.30, 0.19, 0.11), 0.34, metal=1.0)
    mats["steel_brushed"] = brushed_metal("steel_brushed")
    mats["steel_dark"] = simple("steel_dark", (0.09, 0.09, 0.10), 0.42, metal=1.0)
    mats["glass_low_iron"] = glass()
    mats["glass_frosted"] = glass("glass_frosted", rough=0.28, color=(0.92, 0.94, 0.94))
    mats["ceramic_white"] = simple("ceramic_white", (0.86, 0.85, 0.82), 0.28,
                                   bump_scale=60, bump_strength=0.01)
    mats["ceramic_putty"] = simple("ceramic_putty", (0.62, 0.58, 0.52), 0.4)
    mats["linen"] = simple("linen", (0.72, 0.68, 0.60), 0.85, sheen=0.4,
                           bump_scale=80, bump_strength=0.05)
    mats["linen_dark"] = simple("linen_dark", (0.32, 0.33, 0.32), 0.85, sheen=0.4,
                                bump_scale=80, bump_strength=0.05)
    mats["paper"] = simple("paper", (0.88, 0.86, 0.80), 0.7)
    mats["rubber_black"] = simple("rubber_black", (0.03, 0.03, 0.032), 0.75)
    mats["plastic_black"] = simple("plastic_black", (0.045, 0.045, 0.048), 0.4)
    mats["apple_skin"] = simple("apple_skin", (0.48, 0.06, 0.045), 0.35,
                                bump_scale=45, bump_strength=0.02)
    mats["orange_skin"] = simple("orange_skin", (0.80, 0.38, 0.07), 0.55,
                                 bump_scale=90, bump_strength=0.06)
    mats["banana_skin"] = simple("banana_skin", (0.72, 0.60, 0.16), 0.5)
    mats["leaf"] = simple("leaf", (0.20, 0.34, 0.14), 0.5,
                          bump_scale=30, bump_strength=0.08, rough_var=(0.4, 0.6))
    mats["bark"] = simple("bark", (0.28, 0.22, 0.16), 0.8, bump_scale=25,
                          bump_strength=0.2)
    mats["soil"] = simple("soil", (0.09, 0.07, 0.055), 0.9, bump_scale=40,
                          bump_strength=0.15)
    mats["plastic_white"] = simple("plastic_white", (0.88, 0.88, 0.86), 0.32)
    mats["plastic_red"] = simple("plastic_red", (0.55, 0.10, 0.08), 0.34)
    mats["plastic_blue"] = simple("plastic_blue", (0.13, 0.22, 0.42), 0.34)
    mats["plastic_green"] = simple("plastic_green", (0.16, 0.36, 0.18), 0.34)
    mats["cardboard"] = simple("cardboard", (0.52, 0.38, 0.24), 0.75,
                               bump_scale=35, bump_strength=0.05)
    mats["emissive_soft"] = emissive("emissive_soft", (1.0, 0.93, 0.82), 8.0,
                                     base=(0.95, 0.95, 0.93))
    mats["emissive_strip"] = emissive("emissive_strip", (1.0, 0.88, 0.72), 14.0)
    mats["appliance_screen"] = emissive("appliance_screen", (0.35, 0.75, 0.85), 3.0)
    mats["display_knob"] = simple("display_knob", (0.85, 0.85, 0.84), 0.35)
    mats["cooktop_glass"] = simple("cooktop_glass", (0.028, 0.028, 0.030), 0.12,
                                   bump_scale=0, bump_strength=0)
    mats["water_film"] = simple("water_film", (0.9, 0.93, 0.95), 0.03, transmission=0.9,
                                ior=1.33)
    mats["bin_grey"] = simple("bin_grey", (0.30, 0.31, 0.32), 0.45)
    mats["art_a"] = art_canvas("art_a", (0.55, 0.52, 0.45), (0.22, 0.26, 0.28),
                               (0.72, 0.66, 0.55))
    mats["art_b"] = art_canvas("art_b", (0.72, 0.70, 0.65), (0.35, 0.30, 0.24),
                               (0.20, 0.24, 0.30))
    mats["cereal_graphic"] = cereal_box_mat()
    mats["milk_carton"] = simple("milk_carton", (0.90, 0.90, 0.88), 0.5)
    mats["chalkboard"] = simple("chalkboard", (0.06, 0.07, 0.065), 0.55)
    mats["brass_warm"] = simple("brass_warm", (0.62, 0.48, 0.28), 0.32, metal=1.0)
    mats["faucet_steel"] = brushed_metal("faucet_steel", base=(0.55, 0.55, 0.56),
                                         rough=0.24, stretch=(1.0, 1.0, 60.0))
    mats["sky_haze"] = simple("sky_haze", (0.78, 0.83, 0.90), 1.0, alpha=0.32)
    mats["facade"] = simple("facade", (0.48, 0.45, 0.42), 0.8)
    mats["facade_b"] = simple("facade_b", (0.44, 0.42, 0.39), 0.8)
    mats["window_glow"] = emissive("window_glow", (1.0, 0.85, 0.6), 2.2,
                                   base=(0.8, 0.8, 0.8))
    mats["curtain"] = simple("curtain", (0.80, 0.78, 0.72), 0.9, sheen=0.5,
                             bump_scale=25, bump_strength=0.1)
    mats["doormat"] = simple("doormat", (0.35, 0.32, 0.28), 0.95, bump_scale=60,
                             bump_strength=0.2)
    mats["stone_threshold"] = stone("stone_threshold", (0.55, 0.54, 0.52),
                                    (0.60, 0.59, 0.57), rough=0.5, scale=10)
    return mats


def get(name):
    m = bpy.data.materials.get(name)
    return m
