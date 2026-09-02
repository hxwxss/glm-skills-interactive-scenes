"""render_judgeset.py — render the fixed 12-camera judgeset.

  blender --background interactive_kitchen_final.blend --python scripts/render_judgeset.py -- --quality preview
  blender --background interactive_kitchen_final.blend --python scripts/render_judgeset.py -- --quality final

Uses Cycles GPU (OptiX/CUDA) when available, else CPU. Preview -> renders/previews,
final -> renders/final.
"""

import bpy
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import kit_params as P  # noqa: E402

FILENAMES = {
    "JUDGE_01_hero_entry": "01_hero_entry_reveal.png",
    "JUDGE_02_island_workflow": "02_island_workflow.png",
    "JUDGE_03_sink_dishwasher": "03_sink_dishwasher_zone.png",
    "JUDGE_04_cooking_oven": "04_cooking_oven_zone.png",
    "JUDGE_05_fridge_tall": "05_refrigerator_tall_storage.png",
    "JUDGE_06_pantry_interior": "06_pantry_interior.png",
    "JUDGE_07_breakfast_dining": "07_breakfast_dining.png",
    "JUDGE_08_robot_nav": "08_robot_height_navigation.png",
    "JUDGE_09_hinged_open": "09_hinged_interactions_open.png",
    "JUDGE_10_drawers_pullouts": "10_drawers_pullouts_open.png",
    "JUDGE_11_material_detail": "11_material_construction_detail.png",
    "JUDGE_12_reverse_audit": "12_reverse_coverage_audit.png",
}

# cameras whose default open-state composition requires articulation states
STATE_PRESETS = {
    "JUDGE_09_hinged_open": {"fridge_door": "half", "tall_door_a": "open",
                             "upper_door_a": "open"},
    "JUDGE_10_drawers_pullouts": {"drawer_island_1": "open", "drawer_prep_2": "open",
                                  "waste_pullout": "open"},
}


def parse_args():
    argv = sys.argv
    args = {"quality": "preview", "cameras": None, "outdir": None}
    if "--" in argv:
        rest = argv[argv.index("--") + 1:]
        i = 0
        while i < len(rest):
            if rest[i] == "--quality":
                args["quality"] = rest[i + 1]
                i += 2
            elif rest[i] == "--cameras":
                args["cameras"] = rest[i + 1]
                i += 2
            elif rest[i] == "--outdir":
                args["outdir"] = rest[i + 1]
                i += 2
            else:
                i += 1
    return args


def enable_gpu():
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dtype in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dtype
                prefs.get_devices()
                n = 0
                for d in prefs.devices:
                    d.use = d.type != "CPU"
                    n += 1 if d.use else 0
                if n:
                    bpy.context.scene.cycles.device = "GPU"
                    print(f"[render] GPU enabled via {dtype} ({n} devices)")
                    return True
            except Exception as e:
                print(f"[render] {dtype} unavailable: {e}")
    except Exception as e:
        print(f"[render] cycles prefs unavailable: {e}")
    print("[render] falling back to CPU")
    return False


def set_joint(jid, state_name):
    import kit_runtime as KR
    return KR.apply_joint_named(jid, state_name)


def main():
    args = parse_args()
    quality = args["quality"]
    sc = bpy.context.scene
    enable_gpu()
    if quality == "final":
        res = None  # per-camera
        samples = None
        outdir = args["outdir"] or os.path.join(PROJECT, "renders", "final")
    else:
        res = P.RENDER["preview_res"]
        samples = P.RENDER["preview_samples"]
        outdir = args["outdir"] or os.path.join(PROJECT, "renders", "previews")
    os.makedirs(outdir, exist_ok=True)
    cam_filter = args["cameras"].split(",") if args["cameras"] else None
    total = time.time()
    for name, loc, target, lens in P.CAMERAS:
        short = name.replace("JUDGE_", "").split("_", 1)[1]
        if cam_filter and not any(c in name for c in cam_filter):
            continue
        cam = bpy.data.objects.get(name)
        if cam is None:
            print(f"[render] MISSING camera {name}")
            continue
        sc.camera = cam
        if quality == "final":
            if name == "JUDGE_01_hero_entry":
                rx, ry = P.RENDER["final_res_hero"]
                sc.cycles.samples = P.RENDER["final_samples_hero"]
            else:
                rx, ry = P.RENDER["final_res"]
                sc.cycles.samples = P.RENDER["final_samples"]
            sc.render.resolution_x, sc.render.resolution_y = rx, ry
        else:
            sc.render.resolution_x, sc.render.resolution_y = res
            sc.cycles.samples = samples
        sc.cycles.adaptive_threshold = 0.01 if quality == "final" else 0.03
        # deterministic interaction state for the two evidence cameras
        if name in STATE_PRESETS:
            for jid, st in STATE_PRESETS[name].items():
                try:
                    set_joint(jid, st)
                except Exception as e:
                    print(f"[render] joint {jid} state failed: {e}")
        else:
            import kit_runtime as KR
            KR.reset_all_joints()
        bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(outdir, FILENAMES[name])
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"[render] {name} -> {sc.render.filepath} "
              f"({time.time()-t0:.1f}s, {sc.render.resolution_x}x"
              f"{sc.render.resolution_y}, s={sc.cycles.samples})")
    print(f"[render] judgeset complete in {time.time()-total:.1f}s -> {outdir}")
    print("RENDER_OK")


main()
