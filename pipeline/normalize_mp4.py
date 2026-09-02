"""Normalize the promo MP4 for universal browser playback (yuv420p + faststart)."""
import os
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
src = ("/mnt/c/Users/250010163/Desktop/Room_reconstruction/"
       "glm-skills-interactive-kitchen/videos/kitchen_promo.mp4")
tmp = src + ".tmp.mp4"

subprocess.run([FF, "-hide_banner", "-i", src], capture_output=True, text=True)
probe = subprocess.run([FF, "-hide_banner", "-i", src], capture_output=True,
                       text=True).stderr
for ln in probe.splitlines():
    if "Stream" in ln or "Duration" in ln:
        print("  ", ln.strip()[:100])

r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high",
                    "-preset", "medium", "-crf", "20",
                    "-movflags", "+faststart", "-an", tmp])
if r.returncode != 0:
    sys.exit("encode failed")
os.replace(tmp, src)
print("NORMALIZED", os.path.getsize(src), "bytes")
