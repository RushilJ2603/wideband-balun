"""Impedance of each cross-section in Table I of the paper, and the
impedance profile along the tabulated outline of structure B. Writes
results/table1_check.csv and results/profile_<name>.csv."""

import numpy as np
import pandas as pd

from make_geometry import TABLE_I, OUT as GEO
from taper import profile
from xsection import solve, microstrip_hammerstad

RES = GEO.parent / "results"
STATED = [50, 70, 90, 110, 150, 170, 188, 188]


def table1():
    rows = []
    for (z, w, wb), zt in zip(TABLE_I, STATED):
        Z, ee = solve(w, wb)
        rows.append(dict(z_mm=z, w_mm=w, wb_mm=wb, Z_target=zt, Z_solver=round(Z, 1),
                         eeff=round(ee, 3), error_pct=round(100 * (Z - zt) / zt, 1),
                         Z_exp_law=round(50 * np.exp(np.log(188 / 50) * z / 50), 1) if z <= 50 else 188.0))
    d = pd.DataFrame(rows)
    d.to_csv(RES / "table1_check.csv", index=False)
    print(d.to_string(index=False))


def solver_check():
    rows = []
    for w in (4.8, 2.6, 1.2):
        Z, ee = solve(w, 150.0, board=300)
        zh, eh = microstrip_hammerstad(w, 1.5748, 2.2)
        rows.append(dict(case=f"microstrip w = {w} mm", Z_solver=round(Z, 2), Z_closed_form=round(zh, 2),
                         eeff_solver=round(ee, 3), eeff_closed_form=round(eh, 3)))
    Z, ee = solve(0.88, 0.88)
    zh, eh = microstrip_hammerstad(0.88, 1.5748 / 2, 2.2)
    rows.append(dict(case="parallel strip w = 0.88 mm", Z_solver=round(Z, 2), Z_closed_form=round(2 * zh, 2),
                     eeff_solver=round(ee, 3), eeff_closed_form=round(eh, 3)))
    d = pd.DataFrame(rows)
    d.to_csv(RES / "solver_check.csv", index=False)
    print(d.to_string(index=False))


def outline_profile(name):
    g = np.loadtxt(GEO / f"{name}.csv", delimiter=",", skiprows=1)
    z, Z, ee = profile(g, dz=0.5)
    w = np.interp(z, g[:, 0], g[:, 1])
    wb = np.interp(z, g[:, 0], g[:, 2])
    pd.DataFrame(dict(z_mm=z, w_mm=w, wb_mm=wb, Z_ohm=np.round(Z, 2), eeff=np.round(ee, 4))).to_csv(
        RES / f"profile_{name}.csv", index=False)


if __name__ == "__main__":
    solver_check()
    table1()
    outline_profile("paper_B")
    outline_profile("paper_A")
