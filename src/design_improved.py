"""Synthesis of the improved balun.

The paper's taper follows an exponential impedance law over 45 mm and then
runs 20 mm of parallel strip. Here the same 70 mm is used differently:

  * the impedance follows a Klopfenstein profile, which for a given length
    gives the lowest reflection in the passband, and the taper is longer,
    ending 5 mm before the balanced end;
  * the ratio of bottom to top conductor width falls smoothly from 3.75
    (4.8 mm over 18 mm at the feed) to 1 at the balanced end, as
    r = 1 + 2.75 (1 - u)^p with u the normalised position;
  * at every point the top strip width is solved from the cross-section
    table so that the line has the profile impedance, which corrects the
    deviations found in Table I of the paper;
  * the parallel strip is sized for 188 ohm rather than 178 ohm.

The transmission-line model in taper.py ranks candidate designs; the chosen
one is then checked with the full-wave model.

Usage: python3 design_improved.py            sweep and write geometry
"""

import numpy as np
import pandas as pd

from make_geometry import OUT as GEO, write
from taper import back_to_back, cascade, klopfenstein, lower_edge
from ztable import ZTable

RES = GEO.parent / "results"
W50, WB0, FEED, LTOT, ZL = 4.8, 18.0, 5.0, 70.0, 188.0


def synthesize(T, Lt, gm, p=2.0, n=121):
    u, Zu, A = klopfenstein(50.0, ZL, gm, n)
    wend = T.square_for(ZL)
    r = 1 + (WB0 / W50 - 1) * (1 - u) ** p
    w = np.array([T.width_for_ratio(z, ri) for z, ri in zip(Zu, r)])
    wb = r * w
    z = FEED + u * Lt
    # The Klopfenstein profile has small steps at both ends; they are drawn
    # as 0.05 mm long transitions.
    rows = [[0.0, W50, WB0], [FEED - 0.05, W50, WB0]]
    rows += [[zi, wi, bi] for zi, wi, bi in zip(z, w, wb)]
    zend = FEED + Lt
    if zend + 0.05 < LTOT:
        rows += [[zend + 0.05, wend, wend], [LTOT, wend, wend]]
    g = np.array(rows)
    prof_z = np.concatenate([[0.0, FEED - 0.05], z, [zend + 0.05, LTOT]])
    prof_Z = np.concatenate([[T.z(W50, WB0)] * 2, Zu, [ZL, ZL]])
    prof_e = np.array([T.eeff(a, b) for a, b in zip(g[:, 1], g[:, 2])])
    return g, (prof_z[: len(g)], prof_Z[: len(g)], prof_e), A


def evaluate(prof, f):
    z, Z, e = prof
    zz = np.arange(0, z[-1] + 1e-9, 0.25)
    ZZ = np.exp(np.interp(zz, z, np.log(Z)))
    ee = np.interp(zz, z, e)
    s11, _ = cascade(zz, ZZ, ee, f, zload=ZL)
    zb, Zb, eb = back_to_back(zz, ZZ, ee)
    b11, _ = cascade(zb, Zb, eb, f)
    return s11, b11


def metrics(f, s11, b11):
    """Lower band edge (|S11| below -10 dB from there to 15 GHz) of the
    back-to-back pair and of one balun into 188 ohm, and the worst |S11|
    of each between 1 and 12 GHz."""
    sel = (f >= 1e9) & (f <= 12e9)
    return dict(b2b_lo_GHz=round(lower_edge(f, b11) / 1e9, 2),
                single_lo_GHz=round(lower_edge(f, s11) / 1e9, 2),
                b2b_worst_1_12=round(20 * np.log10(np.abs(b11[sel])).max(), 1),
                single_worst_1_12=round(20 * np.log10(np.abs(s11[sel])).max(), 1))


def sweep():
    T = ZTable()
    f = np.linspace(0.5e9, 16e9, 311)
    rows = []
    for Lt in (45.0, 55.0, 60.0):
        for gm in (0.08, 0.10, 0.12, 0.15):
            for p in (1.5, 2.0, 3.0):
                g, prof, A = synthesize(T, Lt, gm, p)
                s11, b11 = evaluate(prof, f)
                rows.append(dict(Lt=Lt, gm=gm, p=p, A=round(A, 3), **metrics(f, s11, b11),
                                 wmin=round(g[:, 1].min(), 3)))
    d = pd.DataFrame(rows)
    d.to_csv(RES / "improved_sweep.csv", index=False)
    print(d.to_string(index=False))
    return d


CHOSEN = dict(Lt=60.0, gm=0.12, p=2.0)


def write_chosen():
    T = ZTable()
    g, prof, A = synthesize(T, **CHOSEN)
    write("improved", g[:, 0], g[:, 1], g[:, 2])
    z, Z, e = prof
    pd.DataFrame(dict(z_mm=g[:, 0], w_mm=g[:, 1], wb_mm=g[:, 2], Z_ohm=np.round(Z, 2),
                      eeff=np.round(e, 4))).to_csv(RES / "profile_improved.csv", index=False)
    f = np.linspace(0.5e9, 16e9, 621)
    s11, b11 = evaluate(prof, f)
    pd.DataFrame(dict(f_GHz=f / 1e9, single_s11_dB=np.round(20 * np.log10(np.abs(s11)), 2),
                      b2b_s11_dB=np.round(20 * np.log10(np.abs(b11)), 2))).to_csv(
        RES / "linemodel_improved.csv", index=False)
    print("improved:", metrics(f, s11, b11))


if __name__ == "__main__":
    sweep()
    write_chosen()
