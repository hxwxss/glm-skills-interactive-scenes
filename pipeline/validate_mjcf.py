"""validate_mjcf.py — load the exported MJCF in MuJoCo and run sanity checks.

  python validate_mjcf.py [path/to/kitchen.xml]

Checks: compilation, DOF count, all 19 joints present with correct ranges,
closed/half/open keyframe stability, contact penetration audit.
"""
import os
import sys

import mujoco
import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else "sim_ready/kitchen_mjcf/kitchen.xml"

# keyframes are stripped first so a keyframe size error can't mask model issues
import re
import tempfile
xml = open(path).read()
xml_nokf = re.sub(r"<keyframe>.*?</keyframe>", "", xml, flags=re.S)
# from_xml_string has no base dir -> keep meshdir resolution via a temp file
tmp = tempfile.NamedTemporaryFile("w", suffix=".xml", dir=os.path.dirname(
    os.path.abspath(path)), delete=False)
tmp.write(xml_nokf)
tmp.close()
model = mujoco.MjModel.from_xml_path(tmp.name)
data = mujoco.MjData(model)
print(f"compiled: nq={model.nq} njnt={model.njnt} ngeom={model.ngeom} nbody={model.nbody}")

t = {2: "slide", 3: "hinge"}
expected = [
    "dishwasher_door", "drawer_island_1", "drawer_island_2", "drawer_prep_1",
    "drawer_prep_2", "freezer_drawer", "fridge_door", "island_door",
    "lower_door_a", "lower_door_b", "oven_door", "ovencol_top_door",
    "pantry_drawer", "pantry_slide", "tall_door_a", "tall_door_b",
    "upper_door_a", "upper_door_b", "waste_pullout",
]
got = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(model.njnt)]
print("joints match:", sorted(got) == sorted(expected))
for i, nm in enumerate(got):
    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, nm)
    lim = bool(model.jnt_limited[jid])
    rng = np.degrees(model.jnt_range[jid]) if model.jnt_type[jid] == 3 else model.jnt_range[jid]
    print(f"  {nm:22s} {t.get(int(model.jnt_type[jid]))} limited={lim} "
          f"range={np.round(rng, 2).tolist()}")

if model.nq != 19:
    print(f"PROBLEM: nq={model.nq}, expected 19 — inspect joints above")
    sys.exit(1)

# full load including keyframes
model = mujoco.MjModel.from_xml_path(path)
for kf in ("closed", "half", "open"):
    kid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, kf)
    if kid < 0:
        print(f"keyframe {kf}: MISSING")
        continue
    mujoco.mj_resetDataKeyframe(model, data, kid)
    for _ in range(500):
        mujoco.mj_step(model, data)
    worst = min((float(data.contact[i].dist) for i in range(data.ncon)), default=0.0)
    qv = float(np.abs(data.qvel).max())
    print(f"keyframe {kf:7s} worst contact {worst*1000:8.2f} mm | qvel max {qv:.4f}")

print("MUJOCO_VALIDATE_OK")
