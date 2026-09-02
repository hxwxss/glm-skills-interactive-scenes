"""render_promo_video.py — promotional video: overview + interactive-asset demo.

Loads interactive_kitchen_final.blend IN MEMORY ONLY (never saves), drives a
custom promo camera + joint/light states as a pure function of the frame number,
renders PNG frames, and (in --encode mode) assembles them into an H.264 MP4
via the Video Sequence Editor.

  blender --background interactive_kitchen_final.blend --python scripts/render_promo_video.py -- --frames 0 431
  blender --background interactive_kitchen_final.blend --python scripts/render_promo_video.py -- --encode

24 fps, 1280x720, 432 frames (~18 s). Deterministic: state = f(frame).
"""

import bpy
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import kit_runtime as KR  # noqa: E402

FPS = 24
RES = (1280, 720)
SAMPLES = 24
TOTAL = 432
FRAMES_DIR = os.path.join(PROJECT, "renders", "video", "frames")
MP4 = os.path.join(PROJECT, "renders", "video", "kitchen_promo.mp4")

# shot: (f0, f1, cam_pos0, cam_pos1, target0, target1, lens)
SHOTS = [
    (0,   71,  (9.00, 3.70, 1.60), (6.60, 3.40, 1.55), (2.80, 5.00, 1.00), (2.00, 4.80, 1.00), 24),
    (72,  119, (6.60, 3.40, 1.55), (4.30, 2.50, 1.95), (2.00, 4.80, 1.00), (5.90, 5.90, 0.90), 24),
    (120, 167, (3.30, 2.70, 1.50), (3.10, 2.45, 1.52), (0.70, 0.45, 1.20), (0.70, 0.55, 1.10), 30),
    (168, 215, (2.35, 5.75, 1.55), (2.30, 5.55, 1.50), (0.45, 6.55, 1.25), (0.50, 6.60, 1.20), 30),
    (216, 263, (2.75, 2.95, 1.40), (2.55, 2.65, 1.35), (0.45, 2.60, 0.55), (0.55, 2.40, 0.50), 28),
    (264, 311, (3.70, 4.30, 1.65), (3.45, 4.15, 1.60), (1.00, 4.25, 1.05), (0.90, 4.30, 1.00), 28),
    (312, 359, (8.40, 3.30, 1.55), (8.50, 3.10, 1.50), (8.90, 1.20, 1.10), (8.95, 1.10, 1.05), 26),
    (360, 431, (4.60, 3.00, 1.60), (8.90, 2.70, 1.70), (5.80, 5.40, 1.00), (3.40, 4.90, 1.05), 24),
]

# which joints open in which shot: joint -> (shot_index, t_start, t_end)
OPEN_ACTIONS = {
    "fridge_door":     (2, 0.05, 0.55),
    "freezer_drawer":  (2, 0.45, 0.95),
    "oven_door":       (3, 0.05, 0.55),
    "drawer_island_1": (3, 0.50, 0.95),
    "dishwasher_door": (4, 0.05, 0.50),
    "waste_pullout":   (4, 0.45, 0.95),
    "upper_door_a":    (5, 0.05, 0.45),
    "upper_door_b":    (5, 0.10, 0.50),
    "lower_door_a":    (5, 0.15, 0.55),
    "drawer_prep_1":   (5, 0.50, 0.95),
    "pantry_slide":    (6, 0.05, 0.60),
}
# named state each action drives to
OPEN_TARGET = {
    "fridge_door": "open", "freezer_drawer": "open", "oven_door": "open",
    "drawer_island_1": "open", "dishwasher_door": "open", "waste_pullout": "open",
    "upper_door_a": "open", "upper_door_b": "open", "lower_door_a": "open",
    "drawer_prep_1": "open", "pantry_slide": "open",
}
LIGHT_SWITCH_SHOT = 7


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def shot_at(f):
    for i, s in enumerate(SHOTS):
        if s[0] <= f <= s[1]:
            return i, (f - s[0]) / max(1, (s[1] - s[0]))
    return len(SHOTS) - 1, 1.0


def apply_frame(f):
    """Deterministic scene + camera state for frame f (in-memory only)."""
    sc = bpy.context.scene
    si, t = shot_at(f)
    sh = SHOTS[si]
    e = ease(t)
    pos = tuple(a + (b - a) * e for a, b in zip(sh[2], sh[3]))
    tgt = tuple(a + (b - a) * e for a, b in zip(sh[4], sh[5]))
    cam = bpy.data.objects.get("PROMO_CAM")
    if cam is None:
        cd = bpy.data.cameras.new("PROMO_CAM")
        cam = bpy.data.objects.new("PROMO_CAM", cd)
        sc.collection.objects.link(cam)
    cam.location = pos
    d = __import__("mathutils").Vector(tgt) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = sh[6]
    cam.data.clip_start = 0.03
    sc.camera = cam

    # joint states
    for jid, (sj, t0, t1) in OPEN_ACTIONS.items():
        info = KR.joint_info(jid)
        target = info["states"][OPEN_TARGET[jid]]
        if si < sj:
            v = info["default"]
        elif si > sj:
            v = target
        else:
            v = info["default"] + (target - info["default"]) * ease((t - t0) / (t1 - t0))
        KR.apply_joint_state(jid, v)
    # shot 8: everything eases back to closed
    if si == 7:
        close_t = ease(t / 0.7) if t < 0.7 else 1.0
        for jid in OPEN_ACTIONS:
            info = KR.joint_info(jid)
            v = info["states"].get(OPEN_TARGET.get(jid, "open"), info["limits"][1])
            KR.apply_joint_state(jid, v * (1 - close_t))
    # lighting switch
    g, dn = 1.0, 0.0
    if si == LIGHT_SWITCH_SHOT:
        g = 1.0 - 0.75 * ease((t - 0.15) / 0.4)
        dn = ease((t - 0.25) / 0.4)
    KR.set_light_group_state("LIGHTING_GENERAL", max(g, 0.25))
    KR.set_light_group_state("LIGHTING_DINING", dn)
    bpy.context.view_layer.update()


def setup_render():
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.image_settings.file_format = "PNG"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.1
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 6
    sc.cycles.use_denoising = True
    # GPU if available (falls back to CPU silently)
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dtype in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dtype
                prefs.get_devices()
                if any(d.use for d in prefs.devices if d.type != "CPU"):
                    sc.cycles.device = "GPU"
                    break
            except Exception:
                pass
    except Exception:
        pass


def render_frames(f0, f1):
    os.makedirs(FRAMES_DIR, exist_ok=True)
    setup_render()
    sc = bpy.context.scene
    for f in range(f0, f1 + 1):
        apply_frame(f)
        sc.frame_set(f)
        sc.render.filepath = os.path.join(FRAMES_DIR, f"f_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[promo] frame {f}/{f1}", flush=True)


def encode():
    sc = bpy.context.scene
    files = sorted(x for x in os.listdir(FRAMES_DIR) if x.endswith(".png"))
    if not files:
        print("[promo] no frames to encode")
        return
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.fps = FPS
    sc.sequence_editor_create()
    se = sc.sequence_editor
    for s in list(se.sequences):
        se.sequences.remove(s)
    strip = se.sequences.new_image("promo", os.path.join(FRAMES_DIR, files[0]),
                                   channel=1, frame_start=1)
    for fn in files[1:]:
        strip.elements.append(fn)
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.ffmpeg.gopsize = FPS
    sc.render.use_sequencer = True
    sc.frame_start = 1
    sc.frame_end = len(files)
    sc.render.filepath = MP4
    bpy.ops.render.render(animation=True)
    print(f"[promo] wrote {MP4} ({len(files)} frames)")


def main():
    argv = sys.argv
    rest = argv[argv.index("--") + 1:] if "--" in argv else []
    if "--encode" in rest:
        encode()
    else:
        f0, f1 = 0, TOTAL - 1
        if "--frames" in rest:
            i = rest.index("--frames")
            f0, f1 = int(rest[i + 1]), int(rest[i + 2])
        render_frames(f0, f1)
    print("PROMO_OK")


if __name__ == "__main__":
    main()
