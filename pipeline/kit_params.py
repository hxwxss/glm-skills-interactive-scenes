"""kit_params.py — single source of truth for the interactive kitchen scene.

All dimensions in meters, Blender Z-up. Interior room bounds: X [0, 9.8], Y [0, 7.4],
Z [0, 3.0]. Origin = interior SW floor corner. +X east, +Y north.
Every module builds from these constants; the scene IR is emitted from them.
"""

import math

SCHEMA_VERSION = "1.2.0"
BLENDER_TARGET_VERSION = "4.1.1"
UNITS = "meters"
COORD_CONVENTION = "Z-up, +X east, +Y north, origin at interior SW floor corner"

# ---------------------------------------------------------------- room shell
ROOM_X = 9.8
ROOM_Y = 7.4
ROOM_H = 3.0
WALL_T = 0.15          # walls extend OUTWARD from interior bounds
PART_T = 0.12          # interior partition thickness (pantry)
SLAB_T = 0.12          # floor / ceiling slab thickness (outward)

# ------------------------------------------------------------- west window W1
W1_Y0, W1_Y1 = 2.45, 3.35
W1_SILL, W1_HEAD = 1.15, 2.35

# ------------------------------------------------------------ north glazing
GLZ_X0, GLZ_X1 = 2.8, 8.6
GLZ_HEAD = 2.7          # sliding system head; transom above to ceiling
GLZ_MULLIONS = [2.8, 4.25, 5.7, 7.15, 8.6]

# ------------------------------------------------------------- terrace
TER_Y0, TER_Y1 = 7.55, 9.35     # outside north wall
TER_Z = -0.02                    # terrace floor top (below interior)
DRAIN_Y = 7.66
GUARD_Y = 9.30

# ------------------------------------------------------------- entry
ENTRY_Y0, ENTRY_Y1 = 3.35, 4.35  # opening in east wall
ENTRY_H = 2.15
HALL = {"x0": 9.95, "x1": 11.40, "y0": 2.85, "y1": 4.85, "h": 2.6}

# ------------------------------------------------------------- pantry
PAN = {
    "x0": 8.2, "x1": 9.8, "y0": 0.0, "y1": 2.4,
    "door_x0": 8.35, "door_x1": 9.25, "door_h": 2.10,
    "slide_open": 0.95, "panel_w": 1.06, "panel_h": 2.22, "panel_standoff": 0.06,
    "counter_z": 0.90, "shelf_zs": [0.55, 1.10, 1.65], "shelf_d": 0.30,
}

# ---------------------------------------------------- west preparation run
WRUN_D = 0.65                 # base depth, X 0..0.65
WRUN_TOP = 0.90               # worktop top surface
STONE_T = 0.03
CAR_H = WRUN_TOP - 0.10 - STONE_T     # carcass top (z) = 0.77
PLINTH_H = 0.10
PLINTH_SET = 0.05
UPPER_Z0, UPPER_Z1, UPPER_D = 1.45, 2.25, 0.35

# segments along Y: (id, y0, y1, kind)
WRUN_SEGS = [
    ("waste",   1.80, 2.40, "pullout"),
    ("sink",    2.45, 3.35, "sink"),
    ("dish",    3.35, 3.95, "dishwasher"),
    ("prep",    3.95, 4.95, "prep"),
    ("cook",    4.95, 5.75, "cooktop"),
    ("coffee",  5.75, 6.35, "counter"),
    ("ovencol", 6.35, 7.40, "ovencolumn"),
]
GAP_DOOR = 0.003               # door perimeter gap
GAP_DRAW = 0.003

# ------------------------------------------------------- south tall wall run
SRUN_D = 0.65
SRUN_H = 2.45
SRUN_SEGS = [
    ("fridge", 0.15, 1.35),
    ("tallcab", 1.35, 2.25),
    ("filler", 2.25, 2.35),
]
FRIDGE_SPLIT_Z = 1.27          # fridge door bottom / freezer top
FRIDGE_DOOR_TOP = 2.08
FRIDGE_ABOVE_TOP = 2.44        # top fixed panel
OVEN_NICHE = {                 # oven inside west-run north column
    "y0": 6.44, "y1": 7.02, "z0": 1.02, "z1": 1.49,   # door face region
    "cavity": {"y0": 6.50, "y1": 6.96, "z0": 1.10, "z1": 1.42, "x1": 0.52},
}

# ---------------------------------------------------------------- island
ISL = {
    "x0": 1.75, "x1": 2.85, "y0": 3.2, "y1": 5.6,
    "top": 0.90, "stone": 0.04, "plinth": 0.10, "plinth_set": 0.06,
    "east_panel": True,
}
ISL_WEST_STACKS = [            # (id, y0, y1, kind)
    ("drawer1", 3.24, 3.98, "drawer"),
    ("drawer2", 4.00, 4.74, "drawer"),
    ("door",    4.76, 5.56, "door"),
]

# ------------------------------------------------------------- dining
DINING = {
    "cx": 5.90, "cy": 5.62, "w": 2.00, "d": 0.95, "top": 0.75, "top_t": 0.04,
}
PENDANT_DINING_XS = [5.45, 6.35]
PENDANT_ISLAND = [(2.30, 3.90), (2.30, 4.90)]
PEND_DROP = 1.85               # shade bottom z

# ------------------------------------------------------------ sideboard
SIDEBOARD = {"x0": 5.4, "x1": 7.4, "y1": 0.45, "h": 0.78}

# ------------------------------------------------------------- materials key
MAT = dict(
    plaster="plaster", ceiling="ceiling_white", oak_floor="oak_floor",
    stone_tile="stone_tile", wet_tile="wet_terrace_tile", oak="oak",
    oak_dark="oak_dark", cab_front="cab_front_greige", cab_body="cab_body",
    stone_work="stone_worktop", bronze="bronze", steel="steel_brushed",
    steel_dark="steel_dark", glass="glass_low_iron", glass_frosted="glass_frosted",
    ceramic_w="ceramic_white", ceramic_p="ceramic_putty", textile="linen",
    textile_dark="linen_dark", paper="paper", rubber="rubber_black",
    leaf="leaf", bark="bark", soil="soil", plastic_w="plastic_white",
    plastic_r="plastic_red", plastic_b="plastic_blue", plastic_g="plastic_green",
    card="cardboard", emissive_soft="emissive_soft", screen="appliance_screen",
    cooktop_glass="cooktop_glass", water="water_film", display_knob="display_knob",
    bin_grey="bin_grey", art_a="art_a", art_b="art_b", cereal="cereal_graphic",
    milk="milk_carton", chalk="chalkboard", brass_warm="brass_warm",
)

# ---------------------------------------------------------------- cameras
# (name, loc, target, lens_mm) — fixed judgeset
CAMERAS = [
    ("JUDGE_01_hero_entry",        (9.30, 3.35, 1.55), (2.10, 5.10, 1.00), 24),
    ("JUDGE_02_island_workflow",   (4.35, 1.95, 1.50), (0.70, 4.90, 0.95), 28),
    ("JUDGE_03_sink_dishwasher",   (2.75, 2.05, 1.50), (0.20, 3.40, 0.90), 28),
    ("JUDGE_04_cooking_oven",      (3.35, 3.05, 1.55), (0.35, 6.35, 1.00), 28),
    ("JUDGE_05_fridge_tall",       (3.60, 2.75, 1.50), (0.60, 0.35, 1.15), 28),
    ("JUDGE_06_pantry_interior",   (8.50, 2.15, 1.50), (9.35, 0.75, 1.10), 20),
    ("JUDGE_07_breakfast_dining",  (3.70, 3.30, 1.50), (6.30, 6.15, 0.80), 32),
    ("JUDGE_08_robot_nav",         (9.00, 3.85, 0.75), (1.40, 4.50, 0.85), 24),
    ("JUDGE_09_hinged_open",       (2.75, 3.10, 1.60), (0.55, 0.60, 1.00), 28),
    ("JUDGE_10_drawers_pullouts",  (2.60, 3.60, 1.40), (0.55, 2.00, 0.55), 28),
    ("JUDGE_11_material_detail",   (1.45, 4.45, 1.12), (0.55, 4.15, 0.90), 50),
    ("JUDGE_12_reverse_audit",     (0.55, 0.75, 2.40), (7.60, 6.30, 1.15), 20),
]

# ---------------------------------------------------------------- robot route
ROBOT_RADIUS = 0.35
ROBOT_ROUTE = [
    (9.30, 3.85), (7.60, 3.85), (4.55, 3.85), (4.20, 3.30), (2.30, 2.35),
    (2.00, 1.60), (0.90, 1.40), (1.20, 2.90), (1.20, 3.60), (1.20, 5.00),
    (1.20, 6.30), (1.45, 6.40), (5.60, 4.15), (9.00, 3.05), (9.06, 2.40),
    (9.06, 1.30),
]
ROUTE_LINKS = [  # index pairs traversable segments
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (5, 7), (7, 8),
    (8, 9), (9, 10), (10, 11), (2, 12), (1, 13), (13, 14), (14, 15),
]

# ---------------------------------------------------------------- render
RENDER = {
    "engine": "CYCLES",
    "preview_res": (1280, 720), "preview_samples": 40,
    "final_res_hero": (2560, 1440), "final_res": (1920, 1080),
    "final_samples_hero": 192, "final_samples": 112,
    "interaction_res": (1600, 900), "interaction_samples": 64,
    "denoise": True,
    "exposure": 0.35,
}

# --------------------------------------------------- joint registry (seed)
# filled at build time with real object names; limits in degrees / meters
JOINT_SEED = [
    dict(id="fridge_door", elem="Refrigerator main door", type="revolute",
         axis="Z", limits=(0, 95), states=dict(closed=0, half=45, open=92),
         handle_side="east", grasp="vertical bar handle, east edge"),
    dict(id="freezer_drawer", elem="Freezer drawer", type="prismatic",
         axis="+Y", limits=(0, 0.52), states=dict(closed=0, open=0.52)),
    dict(id="oven_door", elem="Oven drop-down door", type="revolute",
         axis="-Y_local_drop", limits=(-92, 0), states=dict(closed=0, half=-45, open=-90)),
    dict(id="dishwasher_door", elem="Dishwasher drop-down door", type="revolute",
         axis="-Y_local_drop", limits=(-92, 0), states=dict(closed=0, half=-45, open=-90)),
    dict(id="upper_door_a", elem="Prep upper door A", type="revolute",
         axis="Z", limits=(0, 80), states=dict(closed=0, open=78)),
    dict(id="upper_door_b", elem="Prep upper door B", type="revolute",
         axis="Z", limits=(0, 80), states=dict(closed=0, open=78)),
    dict(id="lower_door_a", elem="Prep base door A", type="revolute",
         axis="Z", limits=(0, 85), states=dict(closed=0, open=84)),
    dict(id="lower_door_b", elem="Prep base door B", type="revolute",
         axis="Z", limits=(0, 85), states=dict(closed=0, open=84)),
    dict(id="drawer_prep_1", elem="Prep drawer 1 (top)", type="prismatic",
         axis="+X", limits=(0, 0.45), states=dict(closed=0, open=0.45)),
    dict(id="drawer_prep_2", elem="Prep drawer 2 (mid)", type="prismatic",
         axis="+X", limits=(0, 0.45), states=dict(closed=0, open=0.45)),
    dict(id="drawer_island_1", elem="Island drawer 1", type="prismatic",
         axis="-X", limits=(0, 0.45), states=dict(closed=0, open=0.45)),
    dict(id="drawer_island_2", elem="Island drawer 2", type="prismatic",
         axis="-X", limits=(0, 0.45), states=dict(closed=0, open=0.45)),
    dict(id="island_door", elem="Island hinged door", type="revolute",
         axis="Z", limits=(0, 100), states=dict(closed=0, open=95)),
    dict(id="waste_pullout", elem="Waste/recycling pull-out", type="prismatic",
         axis="+X", limits=(0, 0.55), states=dict(closed=0, open=0.55)),
    dict(id="pantry_slide", elem="Pantry sliding panel", type="prismatic",
         axis="-X", limits=(0, 0.95), states=dict(closed=0, open=0.95)),
    dict(id="tall_door_a", elem="South tall cabinet door A", type="revolute",
         axis="Z", limits=(0, 92), states=dict(closed=0, open=90)),
    dict(id="tall_door_b", elem="South tall cabinet door B", type="revolute",
         axis="Z", limits=(0, 92), states=dict(closed=0, open=90)),
    dict(id="ovencol_top_door", elem="Oven column top cabinet door", type="revolute",
         axis="Z", limits=(0, 64), states=dict(closed=0, open=62)),
]

LIGHT_GROUPS = {
    "LIGHTING_GENERAL": dict(desc="general + task: downlights, under-cabinet, island pendants", default=1.0),
    "LIGHTING_DINING": dict(desc="dining pendants", default=0.0),
}

# ------------------------------------------------------------ embodied tasks
TASKS = [
    dict(id="place_mug_in_dishwasher",
         instruction="Pick up the coffee mug from the island worktop and place it upright in the dishwasher upper rack.",
         objects=["mug_coffee", "dishwasher_door", "dishwasher_rack"],
         init="mug on island worktop near west edge; dishwasher door closed",
         precondition="dishwasher_door.state == 'open'",
         target="dishwasher upper rack region (x 0.10-0.45, y 3.40-3.90, z 0.55-0.75)",
         success="mug supported inside rack region, upright, door may close",
         fail="mug penetrates rack/door/floor or rests on floor",
         approach="from island west aisle, face +X toward dishwasher front",
         interact_point=(0.60, 3.65, 0.90),
         rand=dict(mug_xy=[0.10, 0.35], mug_yaw=[-30, 30])),
    dict(id="retrieve_cereal_from_pantry",
         instruction="Fetch the cereal box from the pantry shelf and bring it to the island.",
         objects=["cereal_box_pantry", "pantry_slide", "cereal_box"],
         init="backup cereal box on pantry shelf level 2; decoy box already on island",
         precondition="pantry_slide.state == 'open'",
         target="island worktop region near east stools",
         success="pantry cereal box supported on island worktop region",
         fail="box left pantry region but never reaches island; box dropped",
         approach="through pantry doorway, frontal shelf approach, reach height 1.10 m",
         interact_point=(8.85, 1.10, 1.10),
         rand=dict(yaw=[-20, 20])),
    dict(id="move_fruit_to_dining_table",
         instruction="Move one piece of fruit from the fruit bowl to the dining table.",
         objects=["apple_1", "apple_2", "orange_1", "fruit_bowl", "dining_table"],
         init="fruit in bowl on island worktop",
         precondition="none",
         target="dining table top region",
         success="at least one fruit supported on table top",
         fail="fruit on floor or penetrating tableware",
         approach="island east side, then dining table south edge",
         interact_point=(2.85, 4.40, 0.90),
         rand=dict(which_fruit="any of apples/oranges")),
    dict(id="put_recycling_in_pullout_bin",
         instruction="Put the plastic bottle and the tin can into the recycling pull-out bins.",
         objects=["bottle_recycling", "can_recycling", "waste_pullout"],
         init="bottle and can on island worktop; pull-out closed",
         precondition="waste_pullout.state == 'open'",
         target="pull-out bin volumes (plastic lane / metal lane)",
         success="both items inside their bin volumes, supported",
         fail="item on floor, item in wrong lane when task requires sorting",
         approach="island west, then waste pull-out front (face -X)",
         interact_point=(1.10, 2.10, 0.60),
         rand=dict(n_items=[1, 2])),
    dict(id="open_refrigerator_and_retrieve_item",
         instruction="Open the refrigerator and take out the milk carton.",
         objects=["fridge_door", "milk_carton"],
         init="fridge door closed; milk on fridge shelf 2",
         precondition="none",
         target="front clear zone outside fridge",
         success="fridge door >= half-open AND milk carton retrieved to front zone",
         fail="door forced beyond limit; carton dropped",
         approach="frontal, hinge west so swing moves away from approach line",
         interact_point=(0.70, 1.55, 1.55),
         rand=dict(door_state=["half", "open"])),
    dict(id="place_bowl_in_upper_cabinet",
         instruction="Put the cereal bowl into the prep upper cabinet B.",
         objects=["bowl_cereal", "upper_door_b"],
         init="bowl on island worktop; upper_door_b closed",
         precondition="upper_door_b.state == 'open'",
         target="upper cabinet B shelf region (z 1.50-1.70)",
         success="bowl supported on cabinet shelf inside cavity",
         fail="bowl penetrates shelf/door; door closed onto bowl",
         approach="island west aisle, reach up to 1.65 m",
         interact_point=(0.45, 4.70, 1.60),
         rand=dict(yaw=[-25, 25])),
    dict(id="close_all_open_storage",
         instruction="Close every open door, drawer and pull-out in the kitchen.",
         objects=["fridge_door", "dishwasher_door", "upper_door_a", "drawer_prep_1",
                  "waste_pullout", "pantry_slide"],
         init="reset sets fridge door open, dishwasher open, one upper open, one drawer open, pull-out open, pantry open",
         precondition="none",
         target="all joints at named state 'closed'",
         success="every joint within 0.5 deg / 5 mm of closed",
         fail="any joint left open",
         approach="per-fixture approach points",
         interact_point=None,
         rand=dict(open_set="deterministic fixed set")),
    dict(id="switch_from_task_lighting_to_dining_lighting",
         instruction="Switch off the task lighting group and switch on the dining pendants.",
         objects=["LIGHTING_GENERAL", "LIGHTING_DINING"],
         init="GENERAL on, DINING off",
         precondition="none",
         target="light group states",
         success="GENERAL off AND DINING on",
         fail="both on or both off",
         approach="switch actuation at wall keypad (2.95, 0.10, 1.10) or API",
         interact_point=(2.95, 0.10, 1.10),
         rand=dict()),
]

NAV_ZONES = [
    dict(id="zone_kitchen_aisle", poly=[(0.65, 1.8), (1.75, 1.8), (1.75, 5.6), (0.65, 5.6)]),
    dict(id="zone_south_spine", poly=[(0.3, 0.8), (8.1, 0.8), (8.1, 3.2), (0.3, 3.2)]),
    dict(id="zone_central", poly=[(2.85, 3.2), (4.9, 3.2), (4.9, 5.15), (2.85, 5.15)]),
    dict(id="zone_dining", poly=[(4.4, 4.2), (7.6, 4.2), (7.6, 7.3), (4.4, 7.3)]),
    dict(id="zone_entry", poly=[(7.9, 2.5), (9.7, 2.5), (9.7, 5.2), (7.9, 5.2)]),
    dict(id="zone_pantry", poly=[(8.32, 0.12), (9.68, 0.12), (9.68, 2.28), (8.32, 2.28)]),
]
