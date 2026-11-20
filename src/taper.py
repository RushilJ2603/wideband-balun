"""Impedance profile and transmission-line model of a balun taper.

profile()     Z(z) and eps_eff(z) along a balun outline, from the
              cross-section solver.
cascade()     S-parameters of a chain of short uniform line sections, used
              for a single balun or for two baluns back to back.
klopfenstein()  The Klopfenstein impedance profile.

Lengths in mm, frequencies in Hz.
"""

import numpy as np
from scipy.integrate import quad
from scipy.special import i1

from xsection import solve, C0


def outline(geom, dz=0.5):
    """Sample a balun outline (rows of z, w, wb) every dz mm."""
    z = np.arange(geom[0, 0], geom[-1, 0] + dz / 2, dz)
    w = np.interp(z, geom[:, 0], geom[:, 1])
    wb = np.interp(z, geom[:, 0], geom[:, 2])
    return z, w, wb


def profile(geom, dz=0.5, cache=None):
    """Z and eps_eff at each sample of the outline. Repeated cross-sections
    are solved once."""
    z, w, wb = outline(geom, dz)
    cache = {} if cache is None else cache
    Z = np.empty_like(z)
    ee = np.empty_like(z)
    for k, (a, b) in enumerate(zip(w, wb)):
        key = (round(a, 4), round(b, 4))
        if key not in cache:
            cache[key] = solve(a, b)
        Z[k], ee[k] = cache[key]
    return z, Z, ee


def cascade(z, Z, ee, f, zref=50.0, zload=None):
    """S11 and S21 of the line sections between the samples. Each section
    takes the mean impedance and permittivity of its two end samples. The
    output port is referred to zload (default zref)."""
    zload = zref if zload is None else zload
    dz = np.diff(z) * 1e-3
    Zs = 0.5 * (Z[1:] + Z[:-1])
    es = 0.5 * (ee[1:] + ee[:-1])
    s11 = np.empty(len(f), complex)
    s21 = np.empty(len(f), complex)
    for n, fr in enumerate(f):
        bl = 2 * np.pi * fr * np.sqrt(es) / C0 * dz
        A, B, C, D = 1.0 + 0j, 0j, 0j, 1.0 + 0j
        for zs, t in zip(Zs, bl):
            a, b, c, d = np.cos(t), 1j * zs * np.sin(t), 1j * np.sin(t) / zs, np.cos(t)
            A, B, C, D = A * a + B * c, A * b + B * d, C * a + D * c, C * b + D * d
        z1, z2 = zref, zload
        den = A * z2 + B + C * z1 * z2 + D * z1
        s11[n] = (A * z2 + B - C * z1 * z2 - D * z1) / den
        s21[n] = 2 * np.sqrt(z1 * z2) / den
    return s11, s21


def back_to_back(z, Z, ee):
    """Mirror a single-balun profile about its balanced end."""
    L = z[-1]
    z2 = np.concatenate([z, 2 * L - z[-2::-1]])
    return z2, np.concatenate([Z, Z[-2::-1]]), np.concatenate([ee, ee[-2::-1]])


def klopfenstein(z0, zl, gm, n=201):
    """Klopfenstein profile from z0 to zl with passband reflection gm.
    Returns normalised position u in [0, 1] and Z(u), and the constant A
    that sets the lower band edge (beta * L = A)."""
    g0 = 0.5 * np.log(zl / z0)
    A = np.arccosh(g0 / gm)
    u = np.linspace(0, 1, n)

    def phi(x):
        f = lambda y: i1(A * np.sqrt(1 - y * y)) / (A * np.sqrt(1 - y * y)) if y * y < 1 else 0.5
        return quad(f, 0, x, limit=200)[0]

    lnz = np.array([0.5 * np.log(z0 * zl) + g0 / np.cosh(A) * A**2 * phi(2 * x - 1) for x in u])
    return u, np.exp(lnz), A


def band(f, s11, level=-10.0):
    """First continuous band from the low end where |S11| is below level."""
    ok = 20 * np.log10(np.abs(s11)) < level
    if not ok.any():
        return np.nan, np.nan
    i0 = int(np.argmax(ok))
    rest = np.where(~ok[i0:])[0]
    i1_ = i0 + rest[0] - 1 if rest.size else len(f) - 1
    return f[i0], f[i1_]


def lower_edge(f, s11, level=-10.0, fmax=15e9):
    """Lowest frequency above which |S11| stays below level up to fmax."""
    sel = f <= fmax
    bad = np.where(20 * np.log10(np.abs(s11[sel])) >= level)[0]
    if not bad.size:
        return f[0]
    k = bad[-1]
    return f[k + 1] if k + 1 < sel.sum() else np.nan
