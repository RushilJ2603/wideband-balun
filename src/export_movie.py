"""Converts the time-domain and cross-section field recordings of a finished
balun run to results/<name>.mat for balun_demo: Ez in the middle of the
substrate on a uniform grid over time (8-bit, normalised), and Ey, Ez at
5 GHz in three cross-sections, at the phase of largest field. Needs h5py.

    python3 export_movie.py movie_improved
"""

import sys

import h5py
import numpy as np
from scipy.interpolate import interp1d
from scipy.io import savemat

from export_fields import RES, sim_root


def resample(data, axis_values, new, axis):
    return interp1d(axis_values, data, axis=axis, bounds_error=False, fill_value=0.0)(new)


def movie(sim):
    with h5py.File(sim / "Et_mid.h5", "r") as f:
        x, y = f["Mesh/x"][()] * 1e3, f["Mesh/y"][()] * 1e3
        td = f["FieldData/TD"]
        keys = sorted(td, key=int)
        times = np.array([td[k].attrs["time"][0] for k in keys])
        peak = np.array([np.abs(td[k][2, :, :, 0]).max() for k in keys])
        # Frames from the start of the pulse until it has left the board.
        first = int(np.argmax(peak > 0.02 * peak.max()))
        last = min(first + 170, len(keys) - 1)
        use = keys[first:last + 1]
        xu = np.arange(x[0], x[-1] + 1e-9, 0.3)
        yu = np.arange(-9, 9 + 1e-9, 0.12)
        frames = np.empty((len(xu), len(yu), len(use)), dtype=np.float32)
        for n, k in enumerate(use):
            frames[:, :, n] = resample(resample(td[k][2, :, :, 0], x, xu, 0), y, yu, 1)
    scale = np.percentile(np.abs(frames), 99.8)
    Ez = np.clip(frames / scale, -1, 1)
    return dict(x=xu, y=yu, t_ns=times[first:last + 1] * 1e9, Ez=np.round(Ez * 127).astype(np.int8))


def section(sim, n):
    with h5py.File(sim / f"Ef_x{n}.h5", "r") as f:
        y, z = f["Mesh/y"][()] * 1e3, f["Mesh/z"][()] * 1e3
        E = f["FieldData/FD/f0"][()][:, 0, :, :]
    phase = 0.5 * np.angle((E[1] ** 2 + E[2] ** 2).sum())
    Ey, Ez = (E[1] * np.exp(-1j * phase)).real, (E[2] * np.exp(-1j * phase)).real
    yu = np.arange(-11.5, 11.5 + 1e-9, 0.06)
    zu = np.arange(-2.5, 4.0 + 1e-9, 0.06)
    a = resample(resample(Ey, y, yu, 0), z, zu, 1).astype(np.float32)
    b = resample(resample(Ez, y, yu, 0), z, zu, 1).astype(np.float32)
    return {f"y{n}": yu, f"z{n}": zu, f"Ey{n}": a, f"Ez{n}": b}


if __name__ == "__main__":
    for name in sys.argv[1:]:
        sim = sim_root() / name
        out = movie(sim)
        for n in (1, 2, 3):
            out.update(section(sim, n))
        savemat(RES / f"{name}.mat", out, do_compression=True)
        print("wrote", name, out["Ez"].shape, "frames from", out["t_ns"][0], "to", out["t_ns"][-1], "ns")
