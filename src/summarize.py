"""Collects the figures of merit of every finished balun run into
results/summary.csv, which is where the numbers quoted in the report come
from.

For each run:
  lo_GHz        lowest frequency above which |S11| stays below -10 dB up
                to 15 GHz
  worst_S11_*   largest |S11| between that edge and 15 GHz, and between 1
                and 12 GHz
  S21_min_*     smallest |S21| over the same ranges
  dphi_max      largest departure of the strip current phase difference
                from 180 degrees, above lo_GHz
  damp_max      largest strip current amplitude imbalance in dB, above
                lo_GHz
  cmrr_min      smallest ratio of differential to common-mode strip current
                in dB, above lo_GHz, with I_d = (I_top - I_bot) / 2 and
                I_c = (I_top + I_bot) / 2
  loss_max      largest fraction of power neither reflected nor
                transmitted, 1 - |S11|^2 - |S21|^2, above lo_GHz
  *_p           the same over the band the paper claims, 1.75 to 15 GHz;
                ok_p is the fraction of that band with |S11| below -10 dB
"""

import numpy as np
import pandas as pd

from plots import RES, db, load_sp, currents

RUNS = ["b2b_paper_B", "b2b_paper_A", "b2b_paper_B_smooth", "b2b_paper_B_short", "b2b_improved",
        "single_paper_B", "single_improved"]


def lower_edge(f, s11, level=-10.0, fmax=15.0):
    y = db(s11)
    sel = f <= fmax
    bad = np.where(y[sel] >= level)[0]
    if not bad.size:
        return f[0]
    k = bad[-1]
    if k + 1 >= sel.sum():
        return np.nan
    return float(np.interp(level, [y[k + 1], y[k]], [f[k + 1], f[k]]))


def row(name):
    d = load_sp(name)
    if d is None:
        return None
    f = d.f_GHz.to_numpy()
    s11, s21 = d.s11.to_numpy(), d.s21.to_numpy()
    it, ib = currents(d)
    lo = lower_edge(f, s11)
    band = (f >= lo) & (f <= 15)
    lx = (f >= 1) & (f <= 12)
    pb = (f >= 1.75) & (f <= 15)
    it, ib = it.to_numpy(), ib.to_numpy()
    dphi = np.degrees(np.angle(-it / ib))
    damp = db(it / ib)
    cmrr = db((it - ib) / (it + ib))
    loss = 1 - np.abs(s11) ** 2 - np.abs(s21) ** 2
    return dict(run=name, lo_GHz=round(lo, 2),
                worst_S11_band=round(db(s11[band]).max(), 1),
                worst_S11_1_12=round(db(s11[lx]).max(), 1),
                S21_min_band=round(db(s21[band]).min(), 2),
                S21_min_1_12=round(db(s21[lx]).min(), 2),
                S21_at_10=round(float(np.interp(10, f, db(s21))), 2),
                dphi_max=round(np.abs(dphi[band]).max(), 2),
                damp_max=round(np.abs(damp[band]).max(), 2),
                cmrr_min=round(cmrr[band].min(), 1),
                loss_max=round(loss[band].max(), 3),
                ok_p=round((db(s11[pb]) < -10).mean(), 3),
                worst_S11_p=round(db(s11[pb]).max(), 1),
                S21_min_p=round(db(s21[pb]).min(), 2),
                dphi_max_p=round(np.abs(dphi[pb]).max(), 2),
                damp_max_p=round(np.abs(damp[pb]).max(), 2),
                cmrr_min_p=round(cmrr[pb].min(), 1))


if __name__ == "__main__":
    rows = [r for r in (row(n) for n in RUNS) if r]
    d = pd.DataFrame(rows)
    d.to_csv(RES / "summary.csv", index=False)
    print(d.to_string(index=False))
