"""kit_cameras.py — fixed judgeset cameras (JUDGE_*), transforms + purposes."""

import math
import bpy
from mathutils import Vector

import kit_params as P
import kit_util as U

PURPOSE = {
    "JUDGE_01_hero_entry": "complete spatial hero view from entry",
    "JUDGE_02_island_workflow": "island + preparation wall + working clearances",
    "JUDGE_03_sink_dishwasher": "sink, dishwasher, waste system, service logic",
    "JUDGE_04_cooking_oven": "cooktop, extraction, oven column, safe clearances",
    "JUDGE_05_fridge_tall": "refrigerator enclosure and tall cabinetry",
    "JUDGE_06_pantry_interior": "pantry depth, shelving, drawers, sliding entry",
    "JUDGE_07_breakfast_dining": "dining furniture, daylight, lived-in story",
    "JUDGE_08_robot_nav": "robot-height 0.75 m route width + obstacle complexity",
    "JUDGE_09_hinged_open": "open door states with pivots and interiors visible",
    "JUDGE_10_drawers_pullouts": "drawer boxes, waste pull-out, internals",
    "JUDGE_11_material_detail": "cabinet gaps, worktop edge, seals, grain, contact",
    "JUDGE_12_reverse_audit": "high reverse angle: backs, ceiling, entry, terrace",
}


def _aim(cam_obj, target):
    d = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def build_cameras():
    for name, loc, target, lens in P.CAMERAS:
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.sensor_width = 36
        cd.clip_start = 0.03
        cd.clip_end = 220
        if name == "JUDGE_11_material_detail":
            cd.dof.use_dof = True
            cd.dof.focus_distance = 0.95
            cd.dof.aperture_fstop = 5.6
        ob = bpy.data.objects.new(name, cd)
        ob.location = loc
        _aim(ob, target)
        bpy.context.scene.collection.objects.link(ob)
        U.link(ob, "CAMERAS")
        U.REG.cameras[name] = dict(
            name=name, location=list(loc), target=list(target), lens_mm=lens,
            purpose=PURPOSE[name], blender_name=ob.name)
    bpy.context.scene.camera = bpy.data.objects["JUDGE_01_hero_entry"]
