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

from plots import RES, PAPER, db, load_sp, currents

RUNS = ["b2b_paper_B", "b2b_paper_B_stated", "b2b_paper_A_stated", "b2b_paper_B_stated_short", "b2b_improved",
        "single_paper_B_stated", "single_improved"]


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


def antenna(name, label):
    """Input match of a full antenna run: the lowest frequency from which
    |S11| stays below -10 dB up to 2.5 GHz, the bands between 2.5 and 15 GHz
    where it is not (with their peak), the share of 2.5 to 15 GHz (the band
    measured in the paper) below -10 dB and the worst |S11| there."""
    d = load_sp(name)
    if d is None:
        return None
    f, y = d.f_GHz.to_numpy(), db(d.s11.to_numpy())
    lo = lower_edge(f, d.s11.to_numpy(), fmax=2.5)
    p = (f >= 2.5) & (f <= 15)
    gaps, k = [], np.where(p)[0]
    bad = y[k] >= -10
    i = 0
    while i < len(k):
        if bad[i]:
            j = i
            while j + 1 < len(k) and bad[j + 1]:
                j += 1
            gaps.append(f"{f[k[i]]:.2f} to {f[k[j]]:.2f} GHz ({y[k[i]:k[j] + 1].max():.1f} dB)")
            i = j + 1
        else:
            i += 1
    return dict(balun=label, lo_GHz=round(lo, 2), gaps_2p5_15="; ".join(gaps) or "none",
                share_2p5_15=round(float((y[p] < -10).mean()), 3),
                worst_2p5_15=round(float(y[p].max()), 1))


def lobe(ang, g, c):
    """Peak of the lobe nearest the direction c (within 40 degrees) and its
    width 3 dB below that peak. ang is 0 to 359 in steps of 1 degree."""
    n = len(g)
    i0 = int(round(c)) % n
    ip = max(((i0 + k) % n for k in range(-40, 41)), key=lambda i: g[i])
    ref = g[ip] - 3
    lo = hi = 0
    while g[(ip + hi + 1) % n] > ref:
        hi += 1
    while g[(ip - lo - 1) % n] > ref:
        lo += 1
    # interpolate the two crossings
    a, b = g[(ip + hi) % n], g[(ip + hi + 1) % n]
    r = hi + (a - ref) / (a - b)
    a, b = g[(ip - lo) % n], g[(ip - lo - 1) % n]
    l = lo + (a - ref) / (a - b)
    return int(ang[ip]), round(float(g[ip]), 1), round(float(r + l), 1)


def fig11(name, label):
    """The 10 GHz cuts of a full antenna run against the simulated pattern
    of Fig. 11 of the paper: peak direction, level and -3 dB width of the
    front lobe (around theta = 0) and back lobe (around 180), and the rms
    difference in dB where both curves are above -15 dB. Fig. 11 counts the
    angle anticlockwise in its plot; it is taken here as our theta."""
    f = PAPER / "fig11_pattern_10GHz.csv"
    pat = RES / f"{name}_patterns.csv"
    if not f.exists() or not pat.exists():
        return []
    p = pd.read_csv(f)
    ang, gp = p.angle_deg.to_numpy(), p.paper_sim_dB.to_numpy()
    d = pd.read_csv(pat)
    d = d[np.isclose(d.f_GHz, 10)]
    rows = []
    for plane, g in [("paper Fig. 11", gp)] + [
            (pl, None) for pl in ("E", "H")]:
        if g is None:
            c = d[d.plane == plane]
            th = c.theta_deg.to_numpy() % 360
            k = np.argsort(th)
            g = np.interp(ang, th[k], c.E_dB.to_numpy()[k], period=360)
            g = g - g.max()
        m = (gp > -15) & (g > -15)
        fd, fl, fw = lobe(ang, g, 0)
        bd, bl, bw = lobe(ang, g, 180)
        rows.append(dict(run=label if plane != "paper Fig. 11" else "paper", plane=plane,
                         front_dir=fd, front_dB=fl, front_width=fw, back_dir=bd, back_dB=bl, back_width=bw,
                         rms_dB=round(float(np.sqrt(np.mean((g[m] - gp[m]) ** 2))), 2)))
    return rows


if __name__ == "__main__":
    f11 = fig11("spiral_full", "paper") + fig11("spiral_full_improved", "improved")[1:]
    if f11:
        pd.DataFrame(f11).to_csv(RES / "spiral_fig11.csv", index=False)
        print(pd.DataFrame(f11).to_string(index=False))
    ant = [r for r in (antenna("spiral_full", "paper"), antenna("spiral_full_improved", "improved")) if r]
    if ant:
        pd.DataFrame(ant).to_csv(RES / "spiral_numbers.csv", index=False)
        print(pd.DataFrame(ant).to_string(index=False))
    rows = [r for r in (row(n) for n in RUNS) if r]
    d = pd.DataFrame(rows)
    d.to_csv(RES / "summary.csv", index=False)
    print(d.to_string(index=False))
