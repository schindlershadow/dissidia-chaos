#!/usr/bin/env python3
"""In-battle portrait for Chaos from the boss' own picture.

    make_hud.py <dissidia tools dir> <p_org200_normal.gim> <out.png>

The retail HUD portrait is a small cut-out. The boss' picture fills the whole 128x128 texture and would cover the HP bar, so it is
cropped to the horns, spikes and collar and fitted into the free part of the HUD (texture x 41..100, y 38..101: left of it the purple
EX gauge, to the right the HP bar), downscaled from 4x bicubic with Lanczos, with a soft bottom and right edge."""
import sys

tools, gim, out = sys.argv[1:4]
sys.path.insert(0, tools)
import gim_encode as ge  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402

src = ge.decode(open(gim, "rb").read()).convert("RGBA")
crop, box = (8, 10, 128, 120), (41, 38, 100, 101)
c = src.crop(crop)
bw, bh = box[2] - box[0], box[3] - box[1]
s = min(bw / c.width, bh / c.height)
nw, nh = round(c.width * s), round(c.height * s)
big = c.resize((c.width * 4, c.height * 4), Image.BICUBIC).resize((nw, nh), Image.LANCZOS)
rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(radius=0.7, percent=70, threshold=2))
pic = rgb.convert("RGBA")
pic.putalpha(big.getchannel("A"))
img = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
x, y = box[0], box[3] - nh
img.paste(pic, (x, y))
al = np.array(img.getchannel("A"), dtype=float)
for k in range(8):
    al[box[3] - 1 - k, :] *= (k + 1) / 9.0
al[box[3]:, :] = 0
for k in range(8):
    al[:, x + nw - 1 - k] *= (k + 1) / 9.0
img.putalpha(Image.fromarray(al.astype("uint8")))
img.save(out)
print("wrote", out)
