"""Reads the far field of a spiral run (nf2ff.h5, written by the openEMS
far-field tool from the run folder) and writes

  results/<name>_patterns.csv   normalised |E| in the xz plane (phi = 0)
                                and the yz plane (phi = 90), theta from
                                -180 to 180 degrees, with the directivity
  results/<name>_hpbw.csv       half-power beamwidth in each plane around
                                broadside above the spiral (theta = 0)

The xz plane contains the balanced feed and is called the E-plane, the yz
plane the H-plane. Needs h5py.

    python3 far_field.py name [name ...]
"""

import sys

import h5py
import numpy as np
import pandas as pd

from export_fields import RES, sim_root


def read(name):
    with h5py.File(sim_root() / name / "nf2ff.h5", "r") as f:
        g = f["nf2ff"]
        freq = np.atleast_1d(g.attrs["Frequency"])
        dmax = np.atleast_1d(g.attrs["Dmax"])
        theta = np.degrees(f["Mesh/theta"][()])
        phi = np.degrees(f["Mesh/phi"][()])
        E = []
        for k in range(len(freq)):
            et = g[f"E_theta/FD/f{k}_real"][()] + 1j * g[f"E_theta/FD/f{k}_imag"][()]
            ep = g[f"E_phi/FD/f{k}_real"][()] + 1j * g[f"E_phi/FD/f{k}_imag"][()]
            E.append(np.sqrt(np.abs(et) ** 2 + np.abs(ep) ** 2))
    return freq, dmax, theta, phi, E


def cut(E, theta, phi, p0):
    """Full plane through phi = p0 and phi = p0 + 180, as theta from -180
    to 180 degrees. E is indexed [phi, theta] or [theta, phi]."""
    if E.shape[0] != len(phi):
        E = E.T
    i0 = int(np.argmin(np.abs(phi - p0)))
    i1 = int(np.argmin(np.abs(phi - (p0 + 180))))
    th = np.concatenate([-theta[::-1], theta[1:]])
    e = np.concatenate([E[i1][::-1], E[i0][1:]])
    return th, e


def hpbw(th, g_db):
    """Width of the -3 dB beam around theta = 0, from the level at 0."""
    i0 = int(np.argmin(np.abs(th)))
    ref = g_db[i0] - 3
    left = np.where(g_db[:i0] < ref)[0]
    right = np.where(g_db[i0:] < ref)[0]
    if not left.size or not right.size:
        return np.nan
    l, r = left[-1], i0 + right[0]
    tl = np.interp(ref, [g_db[l], g_db[l + 1]], [th[l], th[l + 1]])
    tr = np.interp(ref, [g_db[r], g_db[r - 1]], [th[r], th[r - 1]])
    return tr - tl


def process(name):
    freq, dmax, theta, phi, E = read(name)
    rows, bw = [], []
    for k, fr in enumerate(freq):
        widths = []
        for p0, plane in ((0, "E"), (90, "H")):
            th, e = cut(E[k], theta, phi, p0)
            g = 20 * np.log10(e / e.max())
            rows += [dict(f_GHz=fr / 1e9, plane=plane, theta_deg=t, E_dB=round(v, 2)) for t, v in zip(th, g)]
            widths.append(hpbw(th, g))
        bw.append(dict(f_GHz=fr / 1e9, hpbw_E_deg=round(widths[0], 1), hpbw_H_deg=round(widths[1], 1),
                       Dmax_dBi=round(10 * np.log10(dmax[k]), 2)))
    pd.DataFrame(rows).to_csv(RES / f"{name}_patterns.csv", index=False)
    d = pd.DataFrame(bw)
    d.to_csv(RES / f"{name}_hpbw.csv", index=False)
    print(name)
    print(d.to_string(index=False))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        process(n)
