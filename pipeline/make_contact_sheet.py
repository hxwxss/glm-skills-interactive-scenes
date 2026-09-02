"""make_contact_sheet.py — compose renders into renders/contact_sheet.jpg.

  blender --background interactive_kitchen_final.blend --python scripts/make_contact_sheet.py -- --src final
"""

import bpy
import os
import sys
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(SCRIPT_DIR)


def parse_src():
    argv = sys.argv
    src = "final"
    if "--" in argv:
        rest = argv[argv.index("--") + 1:]
        if "--src" in rest:
            src = rest[rest.index("--src") + 1]
    return src


def load_px(path):
    img = bpy.data.images.load(path)
    w, h = img.size
    arr = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(img)
    return arr[::-1]  # flip to top-down


def save_grid(arr, path):
    h, w, _ = arr.shape
    out = bpy.data.images.new("contact", width=w, height=h, alpha=False)
    out.pixels = arr[::-1].ravel().tolist()
    out.filepath_raw = path
    out.file_format = "JPEG"
    out.save()
    print(f"[sheet] wrote {path} ({w}x{h})")


def resize(arr, tw, th):
    h, w, _ = arr.shape
    yi = (np.arange(th) * (h / th)).astype(int).clip(0, h - 1)
    xi = (np.arange(tw) * (w / tw)).astype(int).clip(0, w - 1)
    return arr[yi][:, xi]


def main():
    src = parse_src()
    srcdir = os.path.join(PROJECT, "renders", src)
    names = sorted(f for f in os.listdir(srcdir) if f.endswith(".png"))
    if not names:
        print("[sheet] no renders found in", srcdir)
        return
    cols = 4 if len(names) > 6 else 3
    rows = (len(names) + cols - 1) // cols
    tw, th = 960, 540
    pad = 8
    W = cols * tw + (cols + 1) * pad
    H = rows * th + (rows + 1) * pad
    grid = np.ones((H, W, 4), dtype=np.float32) * 0.08
    grid[:, :, 3] = 1.0
    for i, nm in enumerate(names):
        r, c = divmod(i, cols)
        arr = load_px(os.path.join(srcdir, nm))
        tile = resize(arr, tw, th)
        y = pad + r * (th + pad)
        x = pad + c * (tw + pad)
        grid[y:y + th, x:x + tw] = tile
    save_grid(grid, os.path.join(PROJECT, "renders", "contact_sheet.jpg"))


main()
