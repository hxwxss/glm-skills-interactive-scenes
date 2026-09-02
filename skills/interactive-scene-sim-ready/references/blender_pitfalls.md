# Blender Pitfalls — hard-won, each one cost a real debug cycle

These are the failure modes that produced *wrong renders while the code looked
correct*. All are fixed in `assets/reference_impl/scripts/`, but any new
hand-written geometry code must respect them.

## 1. Object scale leaks into everything

`box()` used to create a unit cube and set `obj.scale = size`. Consequences:

- `Object` texture coordinates are pre-scale → wood planks rendered 10× too big.
- Bevel modifier widths distorted (non-uniform scale).
- **Child objects inherit scale** → 8 mm handle cylinders on a 19 mm-thick door
  rendered as invisible slivers.
- Mesh-space "origin at hinge" shifts got multiplied by the scale → oven door
  floating 12 cm too high, vertical doors displaced up to 12 cm sideways, looking
  like open cabinets in renders while bounding boxes looked plausible.

**Fix**: `bake_scale(obj)` — `obj.data.transform(Matrix.Diagonal((sx,sy,sz,1)))`,
then `obj.scale = (1,1,1)`. Called inside `box()`/`sphere()` at creation time.
Every hinge shift must therefore be in **real meters** (`±width/2`, `−height/2`),
applied *after* the bake.

## 2. Parenting is parent-local — and world coords are a trap

`obj.parent = parent` leaves `matrix_parent_inverse` at identity, so the child's
`location` is interpreted **in the parent's local frame**. Any child position
computed from world coordinates (e.g. "hinge + offset" for a door handle) must be
converted to parent-local first. Symptom when wrong: handles orbit the room at
4.5 m radius when the door swings. Rule: children are authored in parent-local
coordinates, always (`vdoor()` in `kit_cabinetry.py` is the reference).

## 3. Carcasses must be open-fronted

A naive "box with sides on all four corners" puts a panel across the cabinet
front. Overlay doors look fine closed, but drawers and pull-outs collide with
the phantom panel the moment they move (G3 found 700+ penetrations from this).
`carcass(..., front="+X"|"+Y"|"-X"|"-Y")` builds sides perpendicular to the
front, back opposite, nothing on the front.

## 4. Hinge rotation signs are geometric, not configurable

For a vertical hinge at a door edge, the opening direction is fully determined:
hinge on the S or W edge → positive rotation opens into the room; hinge on the
N or E edge → negative. Seed states in `kit_params.JOINT_SEED` are stored
**positive**; `vdoor(..., sign=±1)` applies the sign at registration so the IR
carries correct signed values. Drop-down doors (dishwasher/oven) rotate about
local Y to negative angles. Getting this wrong swings doors into walls — and the
error only shows at intermediate sweep samples, not at the endpoints.

## 5. Joint limits must respect neighbors

Limits are not free: a fridge door at 110° swings 15° past the adjacent wall; an
upper cabinet door at 90° sweeps into the range hood face; a base door at 100°
hits the neighboring front. Run the G3 sweep and shrink limits until the sweep is
clean (typical final values: fridge 95°, uppers 78–80°, base doors 88–90°, top
hatch 64–70°). Real cabinetry uses soft-close stops at these angles anyway.

## 6. Floating-point / IDProperty gotchas

- `obj["prop"] = tuple` stores an IDProperty array; it reads back fine via
  `obj.get(...)` but is **falsy in some contexts** — never write
  `x = obj.get("k") or default`; use explicit `list(...)` + emptiness checks.
- Accessing `matrix_world` right after moving an object can return a stale
  matrix in scripts that never call `bpy.context.view_layer.update()`. The
  validators call it after every state change.
- `bpy.data.objects.new(...)` objects are not fully "live" until linked to a
  collection; `link()` right after creation (the toolkit does it for you).

## 7. Look at pixels, not at bounding boxes

Bounding boxes said "doors closed, correct position" while renders showed open
cabinets — the actual defect was elsewhere in frame (an exposed carcass slot in
the oven column). Renders are ground truth; diagnostics (straight-on renders,
`scene.ray_cast` from the camera, world-AABB dumps) resolve disagreements
between data and pixels in minutes.
