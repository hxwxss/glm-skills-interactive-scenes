"""render_interaction_states.py — deterministic closed/intermediate/open evidence.

  blender --background interactive_kitchen_final.blend --python scripts/render_interaction_states.py

Renders a fixed evidence set (joint, state, camera) into renders/interaction_states/.
"""

import bpy
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import kit_params as P      # noqa: E402
import kit_runtime as KR    # noqa: E402

# (output name, camera, {joint: state}, description)
EVIDENCE = [
    ("fridge_door_closed", "JUDGE_05_fridge_tall", {"fridge_door": "closed"}),
    ("fridge_door_half", "JUDGE_05_fridge_tall", {"fridge_door": "half"}),
    ("fridge_door_open", "JUDGE_05_fridge_tall", {"fridge_door": "open"}),
    ("freezer_drawer_open", "JUDGE_05_fridge_tall", {"freezer_drawer": "open"}),
    ("oven_door_closed", "JUDGE_04_cooking_oven", {"oven_door": "closed"}),
    ("oven_door_half", "JUDGE_04_cooking_oven", {"oven_door": "half"}),
    ("oven_door_open", "JUDGE_04_cooking_oven", {"oven_door": "open"}),
    ("dishwasher_door_open", "JUDGE_03_sink_dishwasher", {"dishwasher_door": "open"}),
    ("dishwasher_door_half", "JUDGE_03_sink_dishwasher", {"dishwasher_door": "half"}),
    ("upper_doors_open", "JUDGE_02_island_workflow", {"upper_door_a": "open",
                                                      "upper_door_b": "open"}),
    ("lower_doors_drawer_open", "JUDGE_02_island_workflow", {"lower_door_b": "open",
                                                             "drawer_prep_1": "open"}),
    ("island_drawer_door_open", "JUDGE_10_drawers_pullouts", {"drawer_island_2": "open",
                                                              "island_door": "open"}),
    ("waste_pullout_open", "JUDGE_10_drawers_pullouts", {"waste_pullout": "open"}),
    ("pantry_slide_closed", "JUDGE_06_pantry_interior", {"pantry_slide": "closed"}),
    ("pantry_slide_open", "JUDGE_06_pantry_interior", {"pantry_slide": "open"}),
    ("dining_lighting_only", "JUDGE_07_breakfast_dining",
     {"__lights__": ("LIGHTING_GENERAL", 0.0, "LIGHTING_DINING", 1.0)}),
]


def enable_gpu():
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dtype in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dtype
                prefs.get_devices()
                n = sum(1 for d in prefs.devices if d.type != "CPU" and d.use)
                if n:
                    bpy.context.scene.cycles.device = "GPU"
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False


def main():
    sc = bpy.context.scene
    enable_gpu()
    outdir = os.path.join(PROJECT, "renders", "interaction_states")
    os.makedirs(outdir, exist_ok=True)
    rx, ry = P.RENDER["interaction_res"]
    total = time.time()
    for name, cam, states in EVIDENCE:
        KR.reset_all_joints()
        KR.set_light_group_state("LIGHTING_GENERAL",
                                 P.LIGHT_GROUPS["LIGHTING_GENERAL"]["default"])
        KR.set_light_group_state("LIGHTING_DINING",
                                 P.LIGHT_GROUPS["LIGHTING_DINING"]["default"])
        desc = ""
        for k, v in states.items():
            if k == "__lights__":
                g1, f1, g2, f2 = v
                KR.set_light_group_state(g1, f1)
                KR.set_light_group_state(g2, f2)
                desc = f"{g1}->{f1} {g2}->{f2}"
            else:
                KR.apply_joint_named(k, v)
                desc += f" {k}={v}"
        bpy.context.view_layer.update()
        sc.camera = bpy.data.objects[cam]
        sc.render.resolution_x, sc.render.resolution_y = rx, ry
        sc.cycles.samples = P.RENDER["interaction_samples"]
        sc.cycles.adaptive_threshold = 0.02
        sc.render.filepath = os.path.join(outdir, name + ".png")
        bpy.ops.render.render(write_still=True)
        print(f"[states] {name} ({cam}, {desc.strip()})")
    print(f"[states] complete in {time.time()-total:.1f}s")
    print("STATES_OK")


main()
