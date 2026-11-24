"""Outlines used to separate the two changes of the improved design, the
taper length and the taper profile:

    step_exp60    exponential impedance over 60 mm (only the length changed)
    step_klop45   Klopfenstein impedance over 45 mm (only the profile changed)

Both use the same width ratio rule, feed and 188 ohm parallel strip as the
improved balun.

Usage: python3 change_steps.py
"""

import numpy as np

from design_improved import FEED, LTOT, W50, WB0, ZL, synthesize
from make_geometry import write
from ztable import ZTable


def exponential(T, Lt, p=2.0, n=121):
    u = np.linspace(0, 1, n)
    Zu = 50.0 * (ZL / 50.0) ** u
    r = 1 + (WB0 / W50 - 1) * (1 - u) ** p
    w = np.array([T.width_for_ratio(a, b) for a, b in zip(Zu, r)])
    wend = T.square_for(ZL)
    z = FEED + u * Lt
    rows = [[0.0, W50, WB0], [FEED - 0.05, W50, WB0]]
    rows += [[a, b, c * b] for a, b, c in zip(z, w, r)]
    rows += [[FEED + Lt + 0.05, wend, wend], [LTOT, wend, wend]]
    return np.array(rows)


if __name__ == "__main__":
    T = ZTable()
    g = exponential(T, 60.0)
    write("step_exp60", g[:, 0], g[:, 1], g[:, 2])
    g = synthesize(T, 45.0, 0.12)[0]
    write("step_klop45", g[:, 0], g[:, 1], g[:, 2])
    print("wrote step_exp60, step_klop45")
