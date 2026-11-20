"""Writes the balun outlines used by build_balun.m to geometry/*.csv.

Each file lists z (mm from the unbalanced end), top strip width w and
bottom conductor width wb for one balun.

paper_B   Table I of the paper, which the authors built as structure B.
paper_B_smooth
          Table I joined by a monotone cubic (PCHIP) instead of straight
          lines. The photograph of the built board, Fig. 7(b), shows curved
          edges, so this is the other reasonable reading of the table.
paper_A   Same top strip and length, with the bottom conductor narrowing
          linearly from 18 mm to 0.88 mm between z = 5 and z = 50 mm. The
          paper only shows structure A in a photograph, so this straight
          outline is an assumption based on Fig. 7(b).
"""

from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "geometry"

TABLE_I = np.array([
    [5.0, 4.80, 18.00],
    [12.7, 2.60, 16.00],
    [22.2, 1.76, 7.00],
    [29.8, 1.20, 2.00],
    [41.5, 1.10, 1.80],
    [46.2, 0.92, 0.98],
    [50.0, 0.88, 0.88],
    [70.0, 0.88, 0.88],
])


def write(name, z, w, wb):
    OUT.mkdir(exist_ok=True)
    data = np.column_stack([z, w, wb])
    np.savetxt(OUT / f"{name}.csv", data, delimiter=",", fmt="%.4f",
               header="z_mm,w_mm,wb_mm", comments="")


def paper_b():
    t = np.vstack([[0.0, 4.80, 18.00], TABLE_I])
    write("paper_B", t[:, 0], t[:, 1], t[:, 2])


def paper_b_smooth():
    t = np.vstack([[0.0, 4.80, 18.00], TABLE_I])
    knots = t[(t[:, 0] >= 5) & (t[:, 0] <= 50)]
    zs = np.arange(5.0, 50.0 + 1e-9, 0.5)
    w = PchipInterpolator(knots[:, 0], knots[:, 1])(zs)
    wb = PchipInterpolator(knots[:, 0], knots[:, 2])(zs)
    z = np.concatenate([[0.0], zs, [70.0]])
    write("paper_B_smooth", z, np.concatenate([[4.8], w, [0.88]]), np.concatenate([[18.0], wb, [0.88]]))


def paper_a():
    t = np.vstack([[0.0, 4.80, 18.00], TABLE_I])
    z = t[:, 0]
    wb = np.where(z <= 5, 18.0, np.where(z >= 50, 0.88, 18.0 + (0.88 - 18.0) * (z - 5) / 45))
    write("paper_A", z, t[:, 1], wb)


def short_middle(src, name, keep):
    """Copy of a balun with the parallel-strip end cut to `keep` mm, used
    for the common-mode check of Section II of the paper."""
    d = np.loadtxt(OUT / f"{src}.csv", delimiter=",", skiprows=1)
    zmax = d[d[:, 1] != d[-1, 1], 0].max()
    zmax = max(zmax, d[np.isclose(d[:, 1], d[-1, 1]) & np.isclose(d[:, 2], d[-1, 2]), 0].min())
    d = d[d[:, 0] <= zmax]
    d = np.vstack([d, [zmax + keep, d[-1, 1], d[-1, 2]]])
    write(name, d[:, 0], d[:, 1], d[:, 2])


if __name__ == "__main__":
    paper_b()
    paper_b_smooth()
    paper_a()
    short_middle("paper_B", "paper_B_short", 2.0)
    print("\n".join(sorted(f.name for f in OUT.glob("*.csv"))))
