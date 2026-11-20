"""Input reflection at the 50 ohm connector of the spiral antenna fed by a
balun, from two full-wave results joined as networks:

  * the balun as a two-port, 50 ohm at port 1 and 188 ohm at port 2, from
    the runs single_<name> (port 1 driven) and single_<name>_p2 (port 2
    driven);
  * the spiral on its own, fed by a 188 ohm lumped port (spiral_lumped).

    Gamma_in = S11 + S12 S21 Gamma_L / (1 - S22 Gamma_L)

Writes results/spiral_<name>_cascade.csv and prints the reciprocity check
S12 = S21 of each balun.

    python3 cascade_spiral.py paper_B improved
"""

import sys

import numpy as np
import pandas as pd

from plots import RES, db, load_sp


def cascade(name):
    a, b = load_sp(f"single_{name}"), load_sp(f"single_{name}_p2")
    sp = load_sp("spiral_lumped")
    f = a.f_GHz.to_numpy()
    keep = (f >= sp.f_GHz.min()) & (f <= sp.f_GHz.max())
    f = f[keep]
    s11, s21 = a.s11.to_numpy()[keep], a.s21.to_numpy()[keep]
    s22, s12 = b.s11.to_numpy()[keep], b.s21.to_numpy()[keep]
    gl = np.interp(f, sp.f_GHz, sp.s11.to_numpy().real) + 1j * np.interp(f, sp.f_GHz, sp.s11.to_numpy().imag)
    gin = s11 + s12 * s21 * gl / (1 - s22 * gl)
    pd.DataFrame(dict(f_GHz=f, s11_re=gin.real, s11_im=gin.imag)).to_csv(RES / f"spiral_{name}_cascade.csv", index=False)
    rec = np.abs(db(s12) - db(s21))
    band = (f >= 2) & (f <= 15)
    print(f"{name}: |S12| and |S21| differ by at most {rec[band].max():.2f} dB from 2 to 15 GHz; "
          f"input |S11| worst {db(gin[band]).max():.1f} dB from 2 to 15 GHz, "
          f"{db(gin[(f >= 2.5) & (f <= 15)]).max():.1f} dB from 2.5 to 15 GHz")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        cascade(n)
