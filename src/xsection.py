"""Quasi-static solver for the balun cross-section.

The cross-section has a top strip of width w on the upper face of the
substrate and a bottom strip of width wb on the lower face, both centred.
With wb much wider than w this is a microstrip line, and with wb equal to w
it is a parallel-strip line. Laplace's equation is solved by finite
differences on a graded grid, once with the substrate and once in air. The
line capacitance comes from the two-conductor capacitance matrix with equal
and opposite charge on the strips, then

    Z0 = 1 / (c * sqrt(C * C_air)),   eps_eff = C / C_air.

Lengths are in mm.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

C0 = 299792458.0
EPS0 = 8.854187817e-12


def _fill(a, b, fine, coarse, ratio):
    """Grid lines strictly between a and b. Cells start at `fine` next to
    both ends and grow by `ratio` towards the middle, capped at `coarse`."""
    sizes = []
    s = fine
    total = 0.0
    while total + s < (b - a) / 2:
        sizes.append(s)
        total += s
        s = min(s * ratio, coarse)
    left = a + np.cumsum(sizes)
    right = b - np.cumsum(sizes)
    mid = np.linspace(left[-1] if sizes else a, right[-1] if sizes else b,
                      max(2, int(np.ceil((right[-1] - left[-1]) / coarse)) + 1) if sizes else 2)
    return np.concatenate([left, mid, right])


def graded_axis(points, fine, coarse, ratio, lo, hi):
    """Grid lines through every given point, about `fine` apart next to each
    point and growing by `ratio` per cell up to `coarse` between them."""
    pts = np.unique(np.concatenate([np.atleast_1d(points), [lo, hi]]))
    pts = pts[(pts >= lo) & (pts <= hi)]
    lines = [pts]
    for a, b in zip(pts[:-1], pts[1:]):
        if b - a > 2 * fine:
            lines.append(_fill(a, b, fine, coarse, ratio))
    return np.unique(np.round(np.concatenate(lines), 9))


def solve(w, wb, h=1.5748, er=2.2, board=30.0, fine=None):
    """Return (Z0 in ohm, eps_eff) for top width w and bottom width wb."""
    if fine is None:
        fine = min(w, wb, h) / 40.0
    span = 25.0 * max(wb, w, h) + 40.0
    xs = graded_axis([-wb / 2, wb / 2, -w / 2, w / 2, -board / 2, board / 2, 0.0],
                     fine, span / 30.0, 1.15, -span, span)
    ys = graded_axis([0.0, h, h / 2], fine, span / 30.0, 1.15, -span, span + h)
    ys = np.unique(np.concatenate([ys, np.linspace(0, h, 9)]))

    caps = []
    for eps_sub in (er, 1.0):
        Cm = _cap_matrix(xs, ys, w, wb, h, eps_sub, board)
        e = np.array([1.0, -1.0])
        caps.append(1.0 / (e @ np.linalg.solve(Cm, e)))
    C, Ca = caps
    return 1.0 / (C0 * np.sqrt(C * Ca)), C / Ca


def _cap_matrix(xs, ys, w, wb, h, eps_sub, board):
    nx, ny = len(xs), len(ys)
    dx = np.diff(xs)
    dy = np.diff(ys)
    xc = 0.5 * (xs[:-1] + xs[1:])
    yc = 0.5 * (ys[:-1] + ys[1:])
    eps = np.ones((nx - 1, ny - 1))
    inside = (np.abs(xc)[:, None] < board / 2) & ((yc > 0) & (yc < h))[None, :]
    eps[inside] = eps_sub

    idx = np.arange(nx * ny).reshape(nx, ny)

    # Permittivity and cell sizes padded with zeros outside the grid, so a
    # node on the boundary simply has no cell on that side.
    ep = np.zeros((nx + 1, ny + 1))
    ep[1:-1, 1:-1] = eps
    dxp = np.concatenate([[0.0], dx, [0.0]])
    dyp = np.concatenate([[0.0], dy, [0.0]])

    # Finite-volume coupling between each node and its four neighbours.
    # Horizontal links join (i, j) and (i + 1, j); the flux face spans half
    # a cell above and below, each with its own permittivity.
    i, j = np.meshgrid(np.arange(nx - 1), np.arange(ny), indexing="ij")
    ax = (ep[i + 1, j + 1] * dyp[j + 1] + ep[i + 1, j] * dyp[j]) / 2 / dx[i]
    n1, n2 = idx[i, j].ravel(), idx[i + 1, j].ravel()
    i, j = np.meshgrid(np.arange(nx), np.arange(ny - 1), indexing="ij")
    ay = (ep[i + 1, j + 1] * dxp[i + 1] + ep[i, j + 1] * dxp[i]) / 2 / dy[j]
    m1, m2 = idx[i, j].ravel(), idx[i, j + 1].ravel()

    a = np.concatenate([ax.ravel(), ay.ravel()])
    p1 = np.concatenate([n1, m1])
    p2 = np.concatenate([n2, m2])
    rows = np.concatenate([p1, p1, p2, p2])
    cols = np.concatenate([p1, p2, p2, p1])
    vals = np.concatenate([a, -a, a, -a])
    A = sp.csr_matrix((vals, (rows, cols)), shape=(nx * ny, nx * ny))

    jt = int(np.argmin(np.abs(ys - h)))
    jb = int(np.argmin(np.abs(ys)))
    top = idx[np.abs(xs) <= w / 2 + 1e-9, jt]
    bot = idx[np.abs(xs) <= wb / 2 + 1e-9, jb]
    edge = np.unique(np.concatenate([idx[0, :], idx[-1, :], idx[:, 0], idx[:, -1]]))

    fixed = np.concatenate([top, bot, edge])
    free = np.setdiff1d(np.arange(nx * ny), fixed)
    Aff = A[free][:, free].tocsc()
    lu = spla.splu(Aff)

    Cm = np.zeros((2, 2))
    for k, cond in enumerate((top, bot)):
        phi = np.zeros(nx * ny)
        phi[cond] = 1.0
        rhs = -A[free][:, cond] @ phi[cond]
        phi[free] = lu.solve(rhs)
        q = A @ phi
        Cm[0, k] = q[top].sum()
        Cm[1, k] = q[bot].sum()
    return EPS0 * Cm  # per metre; the grid unit cancels in 2D


def microstrip_hammerstad(w, h, er):
    """Hammerstad and Jensen closed form for a microstrip on an infinite
    ground, used as a check on the solver."""
    u = w / h
    a = 1 + np.log((u**4 + (u / 52) ** 2) / (u**4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)
    f = 6 + (2 * np.pi - 6) * np.exp(-((30.666 / u) ** 0.7528))
    z01 = 60 * np.log(f / u + np.sqrt(1 + (2 / u) ** 2))
    return z01 / np.sqrt(ee), ee
