"""Figures for the report. Run `python3 plots.py` from src/ after the
simulations; each figure is skipped if its input file is missing.
Figures go to results/figures/."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
GEO = ROOT / "geometry"
PAPER = ROOT / "data" / "paper"
FIG = RES / "figures"

BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
GREY, INK, MUTED = "#8a8985", "#0b0b0b", "#52514e"
COPPER, BOARD = "#c8874b", "#e9e6dc"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.6,
    "axes.grid": True,
    "grid.color": "#dddcd7",
    "grid.linewidth": 0.5,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "lines.linewidth": 1.5,
    "legend.frameon": False,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)
    print("wrote", name)


def load_geom(name):
    return np.loadtxt(GEO / f"{name}.csv", delimiter=",", skiprows=1)


def load_sp(name):
    f = RES / f"{name}.csv"
    if not f.exists():
        return None
    d = pd.read_csv(f)
    d["s11"] = d.s11_re + 1j * d.s11_im
    if "s21_re" in d:
        d["s21"] = d.s21_re + 1j * d.s21_im
    return d


def db(x):
    return 20 * np.log10(np.abs(x))


def band_edges(f, s11, level=-10.0):
    """First band from the low end where |S11| stays below level, with the
    edges interpolated between samples."""
    y = db(s11) - level
    ok = y < 0
    if not ok.any():
        return np.nan, np.nan
    i0 = int(np.argmax(ok))
    lo = f[i0] if i0 == 0 else np.interp(0, [y[i0], y[i0 - 1]], [f[i0], f[i0 - 1]])
    rest = np.where(~ok[i0:])[0]
    if not rest.size:
        return lo, f[-1]
    i1 = i0 + rest[0]
    hi = np.interp(0, [y[i1 - 1], y[i1]], [f[i1 - 1], f[i1]])
    return lo, hi


# Layout of the back-to-back boards (cf. Fig. 7(a), 7(b) of the paper).
def fig_layout(names, labels, out, board=18.0, ext=0.0):
    fig, axes = plt.subplots(len(names), 2, figsize=(7.2, 1.25 * len(names) + 0.4))
    axes = np.atleast_2d(axes)
    for r, (name, lab) in enumerate(zip(names, labels)):
        g = load_geom(name)
        z, w, wb = g[:, 0], g[:, 1], g[:, 2]
        L = z[-1]
        x = np.concatenate([z - L, (L - z)[::-1][1:]])
        for c, (width, side) in enumerate(((w, "top"), (wb, "bottom"))):
            ww = np.concatenate([width, width[::-1][1:]])
            ax = axes[r, c]
            ax.add_patch(plt.Rectangle((-L, -board / 2), 2 * L, board, color=BOARD, lw=0))
            ax.add_patch(Polygon(np.column_stack([np.r_[x, x[::-1]], np.r_[ww / 2, -ww[::-1] / 2]]),
                                 color=COPPER, lw=0))
            ax.set_xlim(-L - 2, L + 2)
            ax.set_ylim(-board / 2 - 1, board / 2 + 1)
            ax.set_aspect("equal")
            ax.grid(False)
            ax.set_yticks([-9, 0, 9])
            ax.set_title(f"{lab}, {side} face", fontsize=8, color=INK, loc="left")
            if r == len(names) - 1:
                ax.set_xlabel("x (mm)")
    fig.tight_layout()
    save(fig, out)


# Impedance profile of the as-tabulated structure B (cf. Fig. 2 of the paper).
def fig_profile(prof_csv="profile_paper_B.csv"):
    f = RES / prof_csv
    if not f.exists():
        return
    d = pd.read_csv(f)
    t = pd.read_csv(RES / "table1_check.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.7))
    zz = np.linspace(0, 50, 200)
    a1.plot(zz, 50 * np.exp(np.log(188 / 50) * zz / 50), color=GREY, ls="--", label="exponential law, 50 to 188 Ω")
    a1.plot(d.z_mm, d.Z_ohm, color=BLUE, label="Table I widths, 2D solver")
    a1.plot(t.z_mm, t.Z_target, "o", ms=4, color=GREY, label="Table I stated value")
    a1.plot(t.z_mm, t.Z_solver, "o", ms=4, mfc="white", color=BLUE)
    a1.set_xlabel("distance z (mm)")
    a1.set_ylabel("characteristic impedance (Ω)")
    a1.legend(fontsize=7, loc="lower right")
    a2.plot(d.z_mm, d.wb_mm, color=ORANGE, label="bottom conductor w′")
    a2.plot(d.z_mm, d.w_mm, color=BLUE, label="top strip w")
    a2.set_yscale("log")
    a2.set_yticks([0.5, 1, 2, 5, 10, 20])
    a2.set_yticklabels(["0.5", "1", "2", "5", "10", "20"])
    a2.set_xlabel("distance z (mm)")
    a2.set_ylabel("width (mm)")
    a2.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig_profile_paper_B")


def load_paper(panel):
    f = ROOT / "data" / "paper" / f"{panel}.csv"
    return pd.read_csv(f) if f.exists() else None


# Back-to-back S-parameters against the paper's Fig. 7 (c) or (d), with an
# optional second openEMS curve.
def fig_b2b(name, panel, title, out, label="this work (openEMS)", extra=None, extra_label=""):
    d = load_sp(name)
    if d is None:
        return
    p = load_paper(panel)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    if p is not None:
        ax.plot(p.f_GHz, p.paper_sim_s11_dB, color=GREY, lw=1.2, ls="--", label="|S11| paper, simulated (CST)")
        ax.plot(p.f_GHz, p.paper_meas_s11_dB, color=GREY, lw=0.9, label="|S11| paper, measured")
    e = load_sp(extra) if extra else None
    if e is not None:
        ax.plot(e.f_GHz, db(e.s11), color=VIOLET, lw=1.0, label=f"|S11| {extra_label}")
    ax.plot(d.f_GHz, db(d.s11), color=BLUE, label=f"|S11| {label}")
    ax.plot(d.f_GHz, db(d.s21), color=ORANGE, label=f"|S21| {label}")
    ax.axhline(-10, color=MUTED, lw=0.7, ls=":")
    ax.set_xlim(0.5, 15)
    ax.set_ylim(-50, 2)
    ax.set_xlabel("frequency (GHz)")
    ax.set_ylabel("magnitude (dB)")
    ax.set_title(title, fontsize=9, loc="left", color=INK)
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    save(fig, out)


def currents(d):
    it = d.itop_re + 1j * d.itop_im
    ib = d.ibot_re + 1j * d.ibot_im
    return it, ib


# Phase and amplitude balance of the strip currents (cf. Fig. 5 of the paper).
def fig_balance(names, labels, out, fmin=1.0, colors=(ORANGE, BLUE, AQUA)):
    ds = [load_sp(n) for n in names]
    if any(d is None for d in ds):
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.8))
    for d, lab, col in zip(ds, labels, colors):
        it, ib = currents(d)
        sel = d.f_GHz >= fmin
        dphi = np.degrees(np.angle(it / ib))
        dphi = np.where(dphi < 0, dphi + 360, dphi)
        a1.plot(d.f_GHz[sel], dphi[sel], color=col, label=lab)
        a2.plot(d.f_GHz[sel], db(it[sel] / ib[sel]), color=col, label=lab)
    a1.axhline(180, color=GREY, lw=0.8, ls="--")
    a1.set_ylim(160, 200)
    a1.set_xlabel("frequency (GHz)")
    a1.set_ylabel("phase of I_top / I_bottom (deg)")
    a2.axhline(0, color=GREY, lw=0.8, ls="--")
    a2.set_ylim(-3, 3)
    a2.set_xlabel("frequency (GHz)")
    a2.set_ylabel("|I_top / I_bottom| (dB)")
    for a in (a1, a2):
        a.set_xlim(fmin, 15)
    a1.legend(fontsize=7)
    fig.tight_layout()
    save(fig, out)


def load_fields(name):
    f = RES / f"{name}_fields.npz"
    return np.load(f) if f.exists() else None


# Magnetic field magnitude just outside each conductor, which follows the
# surface current on it (cf. Fig. 6 of the paper).
def fig_fields(name, out, k=0, title=""):
    F = load_fields(name)
    if F is None:
        return
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 2.7), sharex=True)
    hmax = max(F[f"top_H{k}"].max(), F[f"bot_H{k}"].max())
    for ax, side, lab in zip(axes, ("top", "bot"), ("top face", "bottom face")):
        x, y, H = F[f"{side}_x"], F[f"{side}_y"], F[f"{side}_H{k}"]
        Hn = 20 * np.log10(H / hmax + 1e-12)
        im = ax.pcolormesh(x, y, Hn.T, cmap="viridis", vmin=-30, vmax=0, shading="nearest")
        ax.set_aspect("equal")
        ax.set_ylim(-9.5, 9.5)
        ax.grid(False)
        ax.set_ylabel("y (mm)")
        ax.set_title(f"{title}{lab}, |H| at {F['freq'][k] / 1e9:g} GHz", fontsize=8, loc="left", color=INK)
    axes[-1].set_xlabel("x (mm)")
    cb = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.02)
    cb.set_label("|H| re maximum (dB)")
    save(fig, out)


# Improved design against the paper: back to back, with the paper's own
# simulated curve, and as a single balun into 188 ohm.
def fig_compare(out):
    pb, ib = load_sp("b2b_paper_B_stated"), load_sp("b2b_improved")
    ps, is_ = load_sp("single_paper_B_stated"), load_sp("single_improved")
    if any(d is None for d in (pb, ib, ps, is_)):
        return
    p = load_paper("fig7d_structure_B")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True)
    if p is not None:
        a1.plot(p.f_GHz, p.paper_sim_s11_dB, color=GREY, lw=1.2, ls="--", label="paper, CST (Fig. 7d)")
    a1.plot(pb.f_GHz, db(pb.s11), color=ORANGE, label="paper design, openEMS")
    a1.plot(ib.f_GHz, db(ib.s11), color=BLUE, label="improved, openEMS")
    a1.set_title("Back to back, |S11|", fontsize=9, loc="left", color=INK)
    a2.plot(ps.f_GHz, db(ps.s11), color=ORANGE, label="paper design")
    a2.plot(is_.f_GHz, db(is_.s11), color=BLUE, label="improved")
    a2.set_title("One balun into 188 Ω, |S11|", fontsize=9, loc="left", color=INK)
    for a in (a1, a2):
        a.axhline(-10, color=MUTED, lw=0.7, ls=":")
        a.axvspan(1, 2, color="#f1efe8", lw=0, zorder=0)
        a.set_ylim(-45, 0)
        a.set_ylabel("|S11| (dB)")
        a.legend(fontsize=7, loc="lower right", bbox_to_anchor=(1, 1), ncol=3, borderaxespad=0.2)
    a1.text(1.5, -3, "L band", ha="center", fontsize=7, color=MUTED)
    a2.set_xlim(0.5, 15)
    a2.set_xlabel("frequency (GHz)")
    fig.tight_layout()
    save(fig, out)


# Impedance along the balun: the paper's design (Table I impedances), the
# widths printed in Table I, and the improved Klopfenstein profile.
def fig_profiles(out):
    files = [RES / f"profile_{n}.csv" for n in ("paper_B_stated", "paper_B", "improved")]
    if not all(f.exists() for f in files):
        return
    st, pb, im = (pd.read_csv(f) for f in files)
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(st.z_mm, st.Z_ohm, color=ORANGE, label="paper design, Table I impedances")
    ax.plot(pb.z_mm, pb.Z_ohm, color=GREY, ls="--", lw=1.0, label="widths as printed in Table I")
    ax.plot(im.z_mm, im.Z_ohm, color=BLUE, label="improved, Klopfenstein")
    ax.set_xlabel("distance from the 50 Ω end, z (mm)")
    ax.set_ylabel("line impedance (Ω)")
    ax.set_xlim(0, 70)
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    save(fig, out)


# Transmission-line model against the full-wave result for the published
# outline, back to back.
def fig_linemodel(out):
    from taper import profile, cascade, back_to_back
    d = load_sp("b2b_paper_B")
    if d is None:
        return
    g = load_geom("paper_B")
    z, Z, e = profile(g, dz=0.5)
    zb, Zb, eb = back_to_back(z, Z, e)
    f = d.f_GHz.to_numpy()
    s11, _ = cascade(zb, Zb, eb, f * 1e9)
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(f, db(s11), color=GREY, ls="--", label="line model (2D solver + cascade)")
    ax.plot(f, db(d.s11), color=ORANGE, label="openEMS")
    ax.axhline(-10, color=MUTED, lw=0.7, ls=":")
    ax.set_xlim(0.5, 15)
    ax.set_ylim(-45, 0)
    ax.set_xlabel("frequency (GHz)")
    ax.set_ylabel("|S11| (dB)")
    ax.set_title("Widths as printed in Table I, back to back", fontsize=9, loc="left", color=INK)
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    save(fig, out)


# Long and short balanced section between the two baluns.
def fig_long_short(out):
    a, b = load_sp("b2b_paper_B_stated"), load_sp("b2b_paper_B_stated_short")
    if a is None or b is None:
        return
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    ax.plot(a.f_GHz, db(a.s21), color=ORANGE, label="|S21|, 40 mm balanced section")
    ax.plot(b.f_GHz, db(b.s21), color=BLUE, label="|S21|, 4 mm balanced section")
    ax.plot(a.f_GHz, 10 * np.log10(np.abs(a.s11) ** 2 + np.abs(a.s21) ** 2), color=ORANGE, ls="--", lw=1,
            label="|S11|² + |S21|², 40 mm")
    ax.plot(b.f_GHz, 10 * np.log10(np.abs(b.s11) ** 2 + np.abs(b.s21) ** 2), color=BLUE, ls="--", lw=1,
            label="|S11|² + |S21|², 4 mm")
    ax.set_xlim(1.5, 15)
    ax.set_ylim(-1.8, 0.1)
    ax.set_xlabel("frequency (GHz)")
    ax.set_ylabel("dB")
    ax.legend(fontsize=7, loc="lower center", ncol=2)
    fig.tight_layout()
    save(fig, out)


# Spiral antenna fed by the balun: input reflection against Fig. 10 of the
# paper.
def fig_spiral_s11(names, labels, out, alone=None):
    ds = [load_sp(n) for n in names]
    if any(d is None for d in ds):
        return
    p = load_paper("fig10_spiral")
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    if p is not None:
        ax.plot(p.f_GHz, p.paper_sim_s11_dB, color=GREY, lw=1.2, ls="--", label="paper, CST (Fig. 10)")
        ax.plot(p.f_GHz, p.paper_meas_s11_dB, color=GREY, lw=0.9, label="paper, measured")
    for d, lab, col in zip(ds, labels, (ORANGE, BLUE)):
        ax.plot(d.f_GHz, db(d.s11), color=col, label=lab)
    if alone is not None and load_sp(alone) is not None:
        d = load_sp(alone)
        ax.plot(d.f_GHz, db(d.s11), color=AQUA, lw=1.0, label="spiral alone, re 188 Ω")
    ax.axhline(-10, color=MUTED, lw=0.7, ls=":")
    ax.set_xlim(1, 15)
    ax.set_ylim(-40, 0)
    ax.set_xlabel("frequency (GHz)")
    ax.set_ylabel("|S11| (dB)")
    ax.legend(fontsize=7, loc="lower right", ncol=2)
    fig.tight_layout()
    save(fig, out)


# Normalised far field in the two principal planes at one frequency.
def fig_spiral_pattern(name, out, f_ghz=10.0):
    """Both cuts at f_ghz over the simulated pattern of Fig. 11 of the
    paper, with the angle counted anticlockwise as in that figure."""
    f = RES / f"{name}_patterns.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    d = d[np.isclose(d.f_GHz, f_ghz)]
    fig, ax = plt.subplots(figsize=(4.4, 4.6), subplot_kw={"projection": "polar"})
    p = PAPER / "fig11_pattern_10GHz.csv"
    if p.exists() and np.isclose(f_ghz, 10):
        q = pd.read_csv(p)
        ax.plot(np.radians(q.angle_deg), np.clip(q.paper_sim_dB, -30, 0), color=GREY, lw=2.2,
                label="paper, Fig. 11 (CST)")
    for plane, col, lab in (("E", BLUE, "xz plane (E)"), ("H", ORANGE, "yz plane (H)")):
        c = d[d.plane == plane]
        ax.plot(np.radians(c.theta_deg), np.clip(c.E_dB, -30, 0), color=col, lw=1.3, label=lab)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(1)
    ax.set_rlim(-30, 0)
    ax.set_rticks([-30, -20, -10, 0])
    ax.set_title(f"{f_ghz:g} GHz, normalised |E| (dB)", fontsize=9, color=INK)
    ax.legend(fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.22), ncol=3)
    fig.tight_layout()
    save(fig, out)


if __name__ == "__main__":
    fig_layout(["paper_A_stated", "paper_B_stated"], ["Structure A", "Structure B"], "fig_layout_paper")
    fig_layout(["paper_B_stated", "improved"], ["Paper design", "Improved"], "fig_layout_improved")
    fig_profile()
    fig_fields("b2b_paper_B_stated", "fig_fields_b2b_paper_B", title="Structure B back to back, ")
    fig_fields("b2b_improved", "fig_fields_b2b_improved_10GHz", k=1, title="Improved back to back, ")
    fig_balance(["b2b_paper_B_stated", "b2b_improved"], ["paper design", "improved"], "fig_balance")
    fig_compare("fig_compare")
    fig_profiles("fig_profiles")
    fig_linemodel("fig_linemodel")
    fig_long_short("fig_long_short")
    fig_spiral_s11(["spiral_full", "spiral_full_improved"],
                   ["antenna with the paper's balun", "antenna with the improved balun"], "fig_spiral_s11")
    fig_spiral_pattern("spiral_full", "fig_spiral_pattern_10GHz")
    fig_b2b("b2b_paper_B_stated", "fig7d_structure_B", "Structure B, back to back", "fig_b2b_paper_B",
            extra="b2b_paper_B", extra_label="widths as printed in Table I")
    fig_b2b("b2b_paper_A_stated", "fig7c_structure_A", "Structure A, back to back", "fig_b2b_paper_A")
