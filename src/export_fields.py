"""Converts the frequency-domain field dumps of finished balun runs to
results/<name>_fields.npz: the magnitude of H one cell above the top
conductor and one cell below the bottom one, with the mesh lines in mm.
Needs h5py.

    python3 export_fields.py name [name ...]
"""

import os
import sys
from pathlib import Path

import h5py
import numpy as np

RES = Path(__file__).resolve().parent.parent / "results"


def sim_root():
    tmp = os.environ.get("BALUN_SIMS")
    if tmp:
        return Path(tmp)
    return Path("/mnt/c/Users") / os.environ.get("WINUSER", "jishu") / "AppData/Local/Temp/balun_sims"


def export(name):
    out = {}
    for side in ("top", "bot"):
        fn = sim_root() / name / f"Hf_{side}.h5"
        with h5py.File(fn, "r") as f:
            # Mesh lines are stored in metres.
            out[f"{side}_x"] = f["Mesh/x"][()] * 1e3
            out[f"{side}_y"] = f["Mesh/y"][()] * 1e3
            fd = f["FieldData/FD"]
            out["freq"] = np.atleast_1d(fd.attrs["frequency"])
            for k in range(len(out["freq"])):
                H = fd[f"f{k}"][()]
                out[f"{side}_H{k}"] = np.sqrt((np.abs(H) ** 2).sum(axis=0))[..., 0].astype(np.float32)
    np.savez_compressed(RES / f"{name}_fields.npz", **out)
    print("wrote", name)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        export(n)
