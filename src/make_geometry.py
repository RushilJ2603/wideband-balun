"""Writes the balun outlines used by build_balun.m to geometry/*.csv.

Each file lists z (mm from the unbalanced end), top strip width w and
bottom conductor width wb for one balun.

paper_B   Table I of the paper exactly as printed, widths joined by
          straight lines.

The outlines built to the impedances the table states (paper_B_stated,
paper_A_stated) and the improved balun need the cross-section table and
are written by design_improved.py.
"""

from pathlib import Path

import numpy as np

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
    print("\n".join(sorted(f.name for f in OUT.glob("*.csv"))))
