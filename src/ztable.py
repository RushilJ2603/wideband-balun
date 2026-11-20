"""Tabulates the cross-section solver over top width w and bottom width wb
and interpolates in that table, so taper synthesis does not have to call
the solver at every point. The table is stored in results/ztable.npz."""

from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq

from xsection import solve

TABLE = Path(__file__).resolve().parent.parent / "results" / "ztable.npz"
W = np.geomspace(0.4, 6.0, 26)
WB = np.geomspace(0.4, 24.0, 30)


def build():
    Z = np.full((len(W), len(WB)), np.nan)
    E = np.full_like(Z, np.nan)
    for i, w in enumerate(W):
        for j, wb in enumerate(WB):
            Z[i, j], E[i, j] = solve(w, wb)
        print(f"w = {w:.3f} done", flush=True)
    TABLE.parent.mkdir(exist_ok=True)
    np.savez(TABLE, w=W, wb=WB, Z=Z, E=E)


class ZTable:
    def __init__(self):
        d = np.load(TABLE)
        pts = (np.log(d["w"]), np.log(d["wb"]))
        self._lz = RegularGridInterpolator(pts, np.log(d["Z"]), method="cubic")
        self._e = RegularGridInterpolator(pts, d["E"], method="cubic")

    def z(self, w, wb):
        return float(np.exp(self._lz([[np.log(w), np.log(wb)]])[0]))

    def eeff(self, w, wb):
        return float(self._e([[np.log(w), np.log(wb)]])[0])

    def width_for(self, z_target, wb, lo=0.4, hi=6.0):
        """Top strip width giving z_target over a bottom conductor wb."""
        return brentq(lambda w: self.z(w, wb) - z_target, lo, hi, xtol=1e-5)

    def width_for_ratio(self, z_target, r):
        """Top strip width w giving z_target when the bottom conductor is
        r times as wide."""
        hi = min(6.0, 24.0 / r)
        return brentq(lambda w: self.z(w, r * w) - z_target, 0.4, hi, xtol=1e-5)

    def square_for(self, z_target):
        """Width of a symmetric parallel strip (w = wb) with z_target."""
        return brentq(lambda w: self.z(w, w) - z_target, 0.4, 6.0, xtol=1e-5)


if __name__ == "__main__":
    build()
