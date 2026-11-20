"""Reads the S11 curves of Fig. 7(c) and 7(d) of the paper from a page
image, so the simulated results can be drawn over them.

    python3 digitize_fig7.py <page5.png> <x0> <x15> <y0> <y80> <out.csv>

The image is a crop of one panel. x0 and x15 are the pixel columns of 0
and 15 GHz, y0 and y80 the pixel rows of 0 dB and -80 dB. The simulated
curve is the light blue dashed line and the measured one the dark blue
solid line. Only the part of each curve below -6.4 dB is read, which
separates S11 from S21; frequencies where S11 lies above that are left
empty.
"""

import sys

import numpy as np
import pandas as pd
from PIL import Image


def read_panel(fn, x0, x15, y0, y80):
    im = np.asarray(Image.open(fn).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    light = (b > 170) & (r < 140) & (g > 110) & (g < 200) & (b - r > 70)
    dark = (r < 70) & (g < 110) & (b > 80) & (b - r > 40) & ~light
    H, W = r.shape
    legend = np.zeros_like(light)
    legend[int(0.67 * H):int(0.88 * H), int(0.15 * W):int(0.52 * W)] = True
    curves = {}
    for name, mask in (("sim", light & ~legend), ("meas", dark & ~legend)):
        fs, vals = [], []
        for c in range(int(x0) + 2, int(x15) - 1):
            ys = np.where(mask[:, c])[0]
            ys = ys[ys > y0 + 0.08 * (y80 - y0)]
            if ys.size:
                y = ys.max() if name == "sim" else np.median(ys)
                fs.append((c - x0) / (x15 - x0) * 15)
                vals.append(-(y - y0) / (y80 - y0) * 80)
        curves[name] = (np.array(fs), np.array(vals))
    return curves


def resample(curves, f):
    out = {"f_GHz": f}
    for name, (fs, v) in curves.items():
        y = np.interp(f, fs, v)
        y[(f < fs.min()) | (f > fs.max())] = np.nan
        # Values close to the -6.4 dB cut come from the edge of the curve
        # where it crosses the cut, not from the curve itself.
        y[y > -7.0] = np.nan
        out[f"paper_{name}_s11_dB"] = y
    return pd.DataFrame(out).round(2)


if __name__ == "__main__":
    fn, x0, x15, y0, y80, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
    resample(read_panel(fn, x0, x15, y0, y80), np.linspace(1.0, 15.0, 561)).to_csv(out, index=False)
