"""Reads the S11 curves of Figs. 7(c), 7(d) and 10 of the paper and the
simulated 10 GHz pattern of Fig. 11 from page images, so our results can be
drawn over them.

    python3 digitize_paper.py <panel> <crop.png> <out.csv>

<panel> is fig7c, fig7d, fig10 or fig11 and <crop.png> a crop of that
panel; the pixel positions of the axis frame for each crop are in PANELS.
In the S11 panels the simulated curve is the light blue dashed line and the
measured one the dark blue solid line. Only the part of each curve below
-6.4 dB is read, which separates S11 from S21; frequencies where S11 lies
above that are left empty.

Fig. 11 is a polar plot from 0 dB at the outer circle to -40 dB at the
centre, with the angle counted anticlockwise from the top. In the page
image the circle is squashed into an ellipse, so the two radii are given
separately. The crop is page 6 at 600 dpi, 1690 x 1450 pixels from
(540, 2540). Only the simulated curve (solid blue) is read; the measured
points are 30 degrees apart.
"""

import sys

import numpy as np
import pandas as pd
from PIL import Image


# Pixel columns of the first and last frequency, pixel rows of 0 dB and of
# the bottom of the axis, the frequency and dB range, and the legend box as
# fractions of the crop (top, bottom, left, right).
PANELS = {
    "fig7c": dict(px=(124, 1294), py=(26, 790), f=(0, 15), db=-80, legend=(0.67, 0.88, 0.15, 0.52)),
    "fig7d": dict(px=(131, 1295), py=(27, 775), f=(0, 15), db=-80, legend=(0.67, 0.88, 0.15, 0.52)),
    "fig10": dict(px=(112, 1280), py=(34, 784), f=(1, 15), db=-40, legend=(0.08, 0.21, 0.65, 0.94)),
}


def read_panel(fn, px, py, f, db, legend):
    im = np.asarray(Image.open(fn).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    light = (b > 170) & (r < 140) & (g > 110) & (g < 200) & (b - r > 70)
    dark = (r < 70) & (g < 110) & (b > 80) & (b - r > 40) & ~light
    H, W = r.shape
    box = np.zeros_like(light)
    t, b, l, r = legend
    box[int(t * H):int(b * H), int(l * W):int(r * W)] = True
    x0, x1 = px
    y0, y1 = py
    cut = y0 + 6.4 / -db * (y1 - y0)
    curves = {}
    for name, mask in (("sim", light & ~box), ("meas", dark & ~box)):
        fs, vals = [], []
        for c in range(int(x0) + 2, int(x1) - 1):
            ys = np.where(mask[:, c])[0]
            ys = ys[(ys > cut) & (ys < y1 - 2)]
            if ys.size:
                y = ys.max() if name == "sim" else np.median(ys)
                fs.append(f[0] + (c - x0) / (x1 - x0) * (f[1] - f[0]))
                vals.append((y - y0) / (y1 - y0) * db)
        curves[name] = (np.array(fs), np.array(vals))
    return curves


FIG11 = dict(centre=(863.5, 716.0), radii=(707.0, 618.0), db=-40, legend=(0, 200, 1150, None))


def read_polar(fn, centre, radii, db, legend):
    """Simulated curve of a polar plot as normalised dB against angle, one
    value per degree (the median radius of the line pixels in that
    degree)."""
    im = np.asarray(Image.open(fn).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    blue = (b > 170) & (r < 100) & (g < 100)
    t, bt, l, rt = legend
    blue[t:bt, l:rt] = False
    ys, xs = np.nonzero(blue)
    dx = (xs - centre[0]) / radii[0]
    dy = (ys - centre[1]) / radii[1]
    ang = np.degrees(np.arctan2(-dx, -dy)) % 360
    val = -db * np.hypot(dx, dy) + db
    out = []
    for a in range(360):
        m = np.abs((ang - a + 180) % 360 - 180) < 0.5
        out.append(np.median(val[m]) if m.any() else np.nan)
    v = pd.Series(out).interpolate(limit_direction="both").to_numpy()
    return pd.DataFrame({"angle_deg": np.arange(360), "paper_sim_dB": (v - v.max()).round(2)})


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
    panel, fn, out = sys.argv[1:4]
    if panel == "fig11":
        read_polar(fn, **FIG11).to_csv(out, index=False)
        sys.exit()
    resample(read_panel(fn, **PANELS[panel]), np.linspace(1.0, 15.0, 561)).to_csv(out, index=False)
