"""build_scene.py — authoritative scene builder for the interactive kitchen.

Run:
  blender --background --factory-startup --python scripts/build_scene.py

Creates the full environment deterministically from kit_* modules, emits
scene_ir/kitchen_scene_ir.json from the same constants, and saves
interactive_kitchen_final.blend.
"""

import bpy
import os
import sys
import math
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import kit_params as P          # noqa: E402
import kit_util as U            # noqa: E402
import kit_materials as KM      # noqa: E402
import kit_architecture as KA   # noqa: E402
import kit_cabinetry as KC      # noqa: E402
import kit_appliances as KAp    # noqa: E402
import kit_furniture as KF      # noqa: E402
import kit_props as KP          # noqa: E402
import kit_lighting as KL       # noqa: E402
import kit_cameras as KCam      # noqa: E402
import kit_ir as KIR            # noqa: E402


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_scene():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.length_unit = "METERS"
    sc.render.engine = "CYCLES"
    sc.cycles.samples = P.RENDER["final_samples"]
    sc.cycles.use_denoising = P.RENDER["denoise"]
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 4
    sc.cycles.glossy_bounces = 4
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 12
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = 0.0
    sc.render.resolution_x, sc.render.resolution_y = P.RENDER["final_res"]
    sc.render.image_settings.file_format = "PNG"
    # performance
    sc.cycles.use_persistent_data = True
    sc.render.threads_mode = "AUTO"


def apply_default_states():
    """All joints to named 'closed'; light groups to documented defaults."""
    for jid, jd in U.REG.joints.items():
        set_joint_state(jid, jd.get("default_state", 0))
    for g, meta in P.LIGHT_GROUPS.items():
        KL.set_light_group_state(g, meta["default"])


def set_joint_state(jid, value):
    """Deterministic single entry point (delegates to kit_runtime, which reads
    the persistent custom properties stamped at build time)."""
    import kit_runtime as KR
    return KR.apply_joint_state(jid, value)


def build_everything():
    t0 = time.time()
    U.COLS.clear()
    U.COLS.update(U.make_collections())
    KM.build_all()
    print(f"[build] materials done t={time.time()-t0:.1f}s")
    KA.build_architecture()
    print(f"[build] architecture done t={time.time()-t0:.1f}s")
    KC.build_all_cabinetry()
    print(f"[build] cabinetry done t={time.time()-t0:.1f}s")
    KAp.build_all_appliances()
    KF.build_all_furniture()
    KP.build_all_props()
    KL.build_lighting()
    KCam.build_cameras()
    print(f"[build] contents done t={time.time()-t0:.1f}s")
    bpy.context.view_layer.update()
    make_proxies()
    apply_default_states()
    bpy.context.view_layer.update()
    print(f"[build] states+proxies done t={time.time()-t0:.1f}s")


def make_proxies():
    """Hidden, tightly aligned collision proxies for articulated + key objects."""
    proxy_targets = list(U.REG.joints.keys())
    for oid, rec in U.REG.objects.items():
        if rec.get("semantic_role") in ("grasp_target", "receptacle", "obstacle") or \
           oid in ("dining_table", "island_worktop", "sideboard", "console_table"):
            proxy_targets.append(oid)
    seen = set()
    for oid in proxy_targets:
        if oid in seen:
            continue
        seen.add(oid)
        nm = U.REG.name_by_id.get(oid)
        if not nm:
            continue
        obj = bpy.data.objects.get(nm)
        if obj and obj.type == "MESH":
            U.make_proxy(oid, obj)


def quick_audit():
    n_mesh = sum(1 for o in bpy.data.objects if o.type == "MESH")
    n_light = sum(1 for o in bpy.data.objects if o.type == "LIGHT")
    n_cam = sum(1 for o in bpy.data.objects if o.type == "CAMERA")
    missing_mats = [o.name for o in bpy.data.objects
                    if o.type == "MESH" and not o.data.materials]
    print(f"[audit] meshes={n_mesh} lights={n_light} cameras={n_cam} "
          f"joints={len(U.REG.joints)} ir_objects={len(U.REG.objects)} "
          f"proxies={len(U.REG.proxies)}")
    if missing_mats:
        print(f"[audit] WARNING {len(missing_mats)} objects without material: "
              f"{missing_mats[:8]}")
    return n_mesh


def main():
    clear_scene()
    setup_scene()
    build_everything()
    apply_default_states()
    quick_audit()
    ir_path = os.path.join(PROJECT, "scene_ir", "kitchen_scene_ir.json")
    ir = KIR.write_ir(ir_path)
    print(f"[build] IR written: {ir_path} ({len(ir['objects'])} objects, "
          f"{len(ir['joints'])} joints)")
    blend_path = os.path.join(PROJECT, "interactive_kitchen_final.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path, compress=True)
    print(f"[build] blend saved: {blend_path}")
    print("BUILD_OK")


if __name__ == "__main__":
    main()
