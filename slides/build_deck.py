"""Builds the presentation, Wideband_Balun.pptx, from the figures and
result tables in results/.

    python3 build_deck.py
"""

from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIG = ROOT / "results" / "figures"
RES = ROOT / "results"

INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x52, 0x51, 0x4E)
BLUE = RGBColor(0x2A, 0x78, 0xD6)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
RULE = RGBColor(0xD9, 0xD7, 0xD0)
PANEL = RGBColor(0xF5, 0xF4, 0xEF)
FONT = "Arial"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
count = 0


def text(slide, x, y, w, h, paras, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """paras: list of strings, or (string, dict) with keys size, bold,
    color, bullet, space."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, p in enumerate(paras):
        s, o = (p, {}) if isinstance(p, str) else p
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.space_after = Pt(o.get("space", 6))
        bullet = o.get("bullet", False)
        run = para.add_run()
        run.text = ("•  " if bullet else "") + s
        f = run.font
        f.name = FONT
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.color.rgb = o.get("color", color)
    return tb


def label(slide, x, y, s, color=BLUE):
    text(slide, x, y, 6, 0.3, [s.upper()], size=11, color=color, bold=True)


def new_slide(title, subtitle=""):
    global count
    count += 1
    s = prs.slides.add_slide(BLANK)
    text(s, 0.5, 0.3, 11.6, 0.6, [title], size=26, bold=True)
    if subtitle:
        text(s, 0.5, 0.88, 11.6, 0.4, [subtitle], size=14, color=MUTED)
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.32), Inches(12.33), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = BLUE
    line.line.fill.background()
    text(s, 12.2, 0.32, 0.6, 0.4, [str(count)], size=14, color=MUTED, align=PP_ALIGN.RIGHT)
    return s


def picture(slide, name, x, y, w=None, h=None):
    path = FIG / f"{name}.png"
    if not path.exists():
        return None
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def table(slide, x, y, w, rows, widths=None, size=11, header=True, row_h=0.3):
    nr, nc = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    t = shp.table
    if widths:
        for j, cw in enumerate(widths):
            t.columns[j].width = Inches(cw)
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.text = str(v)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.fill.solid()
            c.fill.fore_color.rgb = PANEL if (header and i == 0) else RGBColor(0xFF, 0xFF, 0xFF)
            for p in c.text_frame.paragraphs:
                for run in p.runs:
                    run.font.name = FONT
                    run.font.size = Pt(size)
                    run.font.bold = header and i == 0
                    run.font.color.rgb = INK
    return t


def panel(slide, x, y, w, h):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid()
    r.fill.fore_color.rgb = PANEL
    r.line.fill.background()
    r.shadow.inherit = False
    return r


summary = pd.read_csv(RES / "summary.csv").set_index("run")
B, P, I = summary.loc["b2b_paper_B_stated"], summary.loc["b2b_paper_B"], summary.loc["b2b_improved"]
A = summary.loc["b2b_paper_A_stated"]
SB, SI = summary.loc["single_paper_B_stated"], summary.loc["single_improved"]
SPI = pd.read_csv(RES / "spiral_numbers.csv").set_index("balun")
SHORT_BULLET = ("40 mm and 4 mm of parallel strip between the baluns: both matched over the band, |S11|² + |S21|² "
                "within 0.5 dB, so the balanced line adds no radiation (paper: no change).")
SPI_RANGE = f"{SPI.loc['paper', 'lo_GHz']:.2f} to 15 GHz"
if SPI.loc["paper", "gaps_2p5_15"] != "none":
    SPI_RANGE += f", except {SPI.loc['paper', 'gaps_2p5_15'].replace('(', '').replace(')', '').replace(' GHz ', ' GHz, ')}"
def spiral_match(balun):
    """Short form of the antenna match for a table cell."""
    r = SPI.loc[balun]
    out = f"from {r.lo_GHz:.2f} GHz"
    if r.gaps_2p5_15 != "none":
        out += ", except " + "; ".join(g.split(" (")[0] for g in r.gaps_2p5_15.split("; "))
    return out


SPIRAL_BULLET = f"With the paper's balun: below −10 dB from {SPI_RANGE} (paper, measured: 2.5 to 15 GHz)."
HP = pd.read_csv(RES / "spiral_full_hpbw.csv")
F11 = pd.read_csv(RES / "spiral_fig11.csv")
F11P = F11[F11.plane == "paper Fig. 11"].iloc[0]
F11H = F11[(F11.run == "paper") & (F11.plane == "H")].iloc[0]
A_SUMMARY = f"{100 * A.ok_p:.1f} % of the band against {100 * B.ok_p:.1f} % for B; first peak near 3.3 GHz"
SHORT_SUMMARY = "matched in both cases; power balance within 0.5 dB"
SPI_SUMMARY = SPI_RANGE

# 1. Title
count += 1
s = prs.slides.add_slide(BLANK)
text(s, 0.7, 1.2, 8.2, 1.6, ["Wideband microstrip to parallel strip balun for L, S, C and X band applications"],
     size=32, bold=True)
text(s, 0.7, 3.0, 8, 0.5, ["EC301 RF Components and Circuits, course project 12"], size=16, color=MUTED)
text(s, 0.7, 3.8, 8, 1.0, ["Rushil Jain (241EC148)", "Jainam Sonigara (241EC155)"], size=16)
text(s, 0.7, 4.9, 8, 0.8, ["Department of Electronics and Communication Engineering", "NITK Surathkal, November 2026"],
     size=13, color=MUTED)
panel(s, 9.3, 1.2, 3.5, 4.6)
text(s, 9.5, 1.35, 3.1, 4.4, [
    ("BASE PAPER", {"size": 11, "bold": True, "color": BLUE}),
    ("Vinayagamoorthy, Coetzee, Jayalath, IEEE VTC 2012: tapered balun, 50 to 188 Ω, RT/duroid 5880", {"size": 12, "space": 14}),
    ("THIS PROJECT", {"size": 11, "bold": True, "color": BLUE}),
    (f"Reproduced in openEMS: back to back below −10 dB from {B.lo_GHz:.2f} to 15 GHz (paper 1.75 to 15 GHz)", {"size": 12}),
    (f"Improved taper: back to back from {I.lo_GHz:.2f} GHz, one balun from {SI.lo_GHz:.2f} GHz", {"size": 12}),
], size=12)

# 2. Problem and base paper
s = new_slide("The problem and the base paper", "A balun from 1 GHz to 12 GHz on one board, from a published design")
label(s, 0.5, 1.6, "Why a wideband balun")
text(s, 0.5, 1.95, 5.9, 3.0, [
    ("Spirals, dipoles and balanced mixers need equal and opposite currents; test equipment and microstrip are unbalanced.", {"bullet": True}),
    ("Without a balun, current returns on the outside of the feed cable, radiates and distorts the pattern.", {"bullet": True}),
    ("L to X band is 12 to 1. Marchand and transformer baluns cover about an octave; a tapered transition has no resonant length, so its band is set by the taper length.", {"bullet": True}),
], size=14)
label(s, 0.5, 4.6, "Course requirement")
text(s, 0.5, 4.95, 5.9, 1.6, [
    ("Pick a published design, reproduce all its results with a software tool, then improve on them.", {"bullet": True}),
    ("Our target for the improvement: the full L band from 1 GHz in the same board size.", {"bullet": True}),
], size=14)
label(s, 6.9, 1.6, "Base paper [1]")
table(s, 6.9, 1.95, 5.9, [
    ["quantity", "value"],
    ["substrate", "RT/duroid 5880, εr 2.2, h 1.5748 mm"],
    ["ports", "50 Ω microstrip to 188 Ω parallel strip"],
    ["taper", "exponential impedance, 45 mm"],
    ["one balun", "70 mm × 18 mm"],
    ["tool", "CST Microwave Studio"],
    ["structure B, back to back", "|S11| < −10 dB, 1.75 to 15 GHz"],
    ["structure A, back to back", "2 to 14.3 GHz"],
    ["insertion loss", "below 3 dB"],
    ["application", "feeds an 8-turn Archimedean spiral"],
], widths=[2.3, 3.6], size=12)
text(s, 6.9, 5.4, 5.9, 0.8, ["[1] K. Vinayagamoorthy, J. Coetzee, D. Jayalath, \"Microstrip to parallel strip balun as spiral antenna feed\", IEEE VTC 2012 Spring, doi 10.1109/VETECS.2012.6240118"],
     size=10, color=MUTED)

# 3. How the balun works
s = new_slide("How the tapered balun works", "The ground narrows until both conductors are equal; the line changes mode and impedance together")
picture(s, "fig_layout_paper", 0.5, 1.6, w=6.6)
label(s, 7.4, 1.6, "Mode and impedance")
text(s, 7.4, 1.95, 5.4, 2.2, [
    ("50 Ω end: wide ground, microstrip field, unbalanced.", {"bullet": True}),
    ("188 Ω end: equal strips, parallel strip line, balanced. 188 Ω = η0/2, the input impedance of a self-complementary spiral.", {"bullet": True}),
    ("Every cross-section is a two-conductor line with its own Z(z), so the balun is a nonuniform line.", {"bullet": True}),
], size=13)
label(s, 7.4, 4.25, "Reflection of a taper")
text(s, 7.4, 4.6, 5.4, 2.6, [
    ("Γ = ½ ∫ e^(−2jφ(z)) d(ln Z)/dz dz", {"size": 15}),
    ("Exponential taper: |Γ| = ½ ln(ZL/Z0) |sin βL / βL|, below −10 dB once βL > 1.95, about 1.5 GHz for 45 mm.", {"bullet": True}),
    ("Back to back the two reflections can add: |S11| ≤ 2|Γ1|.", {"bullet": True}),
], size=13)

# 4. Tools and method
s = new_slide("Tools and method", "openEMS FDTD driven from MATLAB, with a cross-section solver and a line model in Python")
label(s, 0.5, 1.6, "Full-wave model, openEMS")
text(s, 0.5, 1.95, 6.0, 3.3, [
    ("Geometry, materials, mesh and ports written from MATLAB; one Gaussian pulse gives 0.5 to 16 GHz.", {"bullet": True}),
    ("35 µm copper sheets, tan δ 0.0009, mesh 0.08 mm at the strip edges, 0.4 mm along the line, PML boundaries.", {"bullet": True}),
    ("Microstrip ports de-embedded to the board edge; 188 Ω lumped port for a single balun.", {"bullet": True}),
    ("Strip currents and surface fields recorded for the balance and field maps.", {"bullet": True}),
    ("1.8 to 3.1 million cells, 3 to 10 minutes per run; the antenna with its balun 20 million cells, 1.7 hours.", {"bullet": True}),
], size=13)
label(s, 0.5, 5.15, "Check of the setup")
text(s, 0.5, 5.5, 6.0, 1.5, [
    ("Uniform 50 Ω line with the same settings: Z0 50.9 to 53.2 Ω, |S11| below −31.7 dB from 1 to 15 GHz.", {"bullet": True}),
], size=13)
label(s, 6.9, 1.6, "Cross-section solver, checked against closed form")
table(s, 6.9, 1.95, 5.9, [
    ["line", "solver (Ω)", "closed form (Ω)"],
    ["microstrip, w = 4.8 mm", "50.11", "50.42"],
    ["microstrip, w = 2.6 mm", "72.84", "73.45"],
    ["microstrip, w = 1.2 mm", "106.19", "107.33"],
    ["parallel strip, w = 0.88 mm", "178.08", "180.19"],
], widths=[3.1, 1.4, 1.4], size=12)
text(s, 6.9, 3.65, 5.9, 2.5, [
    ("Finite-difference Laplace solve of each cross-section gives Z0 and εeff; within 1.2 % of Hammerstad and Jensen.", {"bullet": True}),
    ("Line model: cascade of 0.25 to 0.5 mm uniform sections built from the solver, used to explore designs in seconds.", {"bullet": True}),
], size=13)

# 5. Table I check
t1 = pd.read_csv(RES / "table1_check.csv")
s = new_slide("Validation: the paper's dimension table", "Two rows of Table I do not give their stated impedance, so we built B to the stated impedances")
rows = [["z (mm)", "w (mm)", "w′ (mm)", "stated (Ω)", "computed (Ω)", "difference"]]
for _, r in t1.iterrows():
    rows.append([f"{r.z_mm:g}", f"{r.w_mm:g}", f"{r.wb_mm:g}", f"{r.Z_target:g}", f"{r.Z_solver:.1f}", f"{r.error_pct:+.1f} %"])
table(s, 0.5, 1.7, 5.9, rows, size=12)
text(s, 0.5, 4.75, 5.9, 2.2, [
    ("Four rows within 5 %; rows at 29.8 and 41.5 mm give 132.5 and 139.9 Ω (stated 110 and 150).", {"bullet": True}),
    ("Stated values follow Z = 50 (188/50)^(z/50) Ω exactly.", {"bullet": True}),
    ("Paper design: that law from 5 to 50 mm, widths solved every 0.5 mm with our solver, 0.786 mm (188 Ω) parallel strip.", {"bullet": True}),
], size=13)
picture(s, "fig_profile_paper_B", 6.7, 1.7, w=6.2)

# 6. Back to back B and root cause
s = new_slide("Validation: structure B back to back",
              f"Below −10 dB from {B.lo_GHz:.2f} to 15 GHz, against 1.75 to 15 GHz in the paper")
picture(s, "fig_b2b_paper_B", 0.4, 1.55, w=6.3)
picture(s, "fig_linemodel", 6.7, 1.55, w=6.2)
text(s, 0.5, 4.5, 6.1, 2.8, [
    (f"Paper design: |S11| below −10 dB from {B.lo_GHz:.2f} GHz to 15 GHz, same shape as the paper's CST curve.", {"bullet": True}),
    (f"|S21| never below {B.S21_min_p:.2f} dB (paper: within 3 dB).", {"bullet": True}),
], size=13)
text(s, 6.8, 4.5, 6.0, 2.8, [
    ("Widths as printed: two extra peaks, −6.7 dB at 5.4 to 6.1 GHz and −9.0 dB at 6.8 to 7.1 GHz.", {"bullet": True}),
    ("The line model predicts both: impedance rises near 30 and 45 mm, 18 mm apart, add in phase near c / (2 · 18 mm · √1.8) ≈ 6.2 GHz.", {"bullet": True}),
], size=13)

# 7. Balance, field map, balanced length
s = new_slide("Validation: balance, fields, balanced section, structure A",
              "Equal and opposite strip currents, symmetric surface current, no change with the balanced line length")
picture(s, "fig_fields_b2b_paper_B", 0.4, 1.55, w=6.4)
picture(s, "fig_long_short", 6.8, 1.55, w=6.1)
text(s, 0.5, 5.0, 6.2, 2.3, [
    (f"Strip currents within {B.dphi_max_p:.1f}° of 180° and {B.damp_max_p:.2f} dB of each other from 1.75 to 15 GHz; common mode at least {B.cmrr_min_p:.1f} dB down (paper: 180°).", {"bullet": True}),
    ("Field at 2.5 GHz symmetric about the centre line, moving from under the strip to the conductor edges as the ground narrows (paper Fig. 6).", {"bullet": True}),
], size=13)
text(s, 6.9, 4.2, 6.0, 3.0, [
    (SHORT_BULLET, {"bullet": True}),
    (f"Structure A (straight ground): below −10 dB on {100 * A.ok_p:.1f} % of 1.75 to 15 GHz against {100 * B.ok_p:.1f} % for B; B is better, as in the paper.", {"bullet": True}),
], size=13)

# 8. Spiral antenna, input match
paper_hp = {2: (94.6, 81.8), 2.5: (93.5, 78.5), 3: (86.4, 78.3), 4: (73.3, 70.2), 5: (64.9, 67.1),
            6: (61.0, 60.7), 10: (53.8, 47.3), 15: (42.6, 34.4)}
s = new_slide("Validation: spiral antenna fed by the balun",
              "Spiral and balun in one openEMS model, as in Fig. 9 of the paper: 20 million cells, 0.1 mm at the centre")
picture(s, "fig_spiral_s11", 0.4, 1.6, w=8.2)
text(s, 8.9, 1.7, 4.0, 5.2, [
    (SPIRAL_BULLET, {"bullet": True, "space": 10}),
    ("Follows the measured curve from 2 to 5 GHz, including the deep dip near 3.5 GHz.", {"bullet": True, "space": 10}),
    ("Spiral alone, 188 Ω feed: matched from 1.65 GHz; the paper puts the lower limit at 1.69 GHz from the arm size.", {"bullet": True}),
], size=13)

# 9. Spiral antenna, radiation
s = new_slide("Validation: radiation pattern and beamwidth",
              "Beamwidth as CST reports it: width of the strongest lobe of each cut, 3 dB below its peak")
picture(s, "fig_spiral_pattern_10GHz", 0.5, 1.5, h=5.7)
rows = [["f (GHz)", "paper E", "ours E", "paper H", "ours H"]]
for _, r in HP.iterrows():
    pe = paper_hp[round(r.f_GHz, 1) if r.f_GHz != 2.5 else 2.5]
    rows.append([f"{r.f_GHz:g}", f"{pe[0]:.1f}°", f"{r.hpbw_E_main_deg:.1f}°", f"{pe[1]:.1f}°", f"{r.hpbw_H_main_deg:.1f}°"])
label(s, 6.3, 1.55, "Half-power beamwidth, Table III of [1]")
table(s, 6.3, 1.9, 6.5, rows, widths=[1.3, 1.3, 1.3, 1.3, 1.3], size=11, row_h=0.27)
text(s, 6.3, 4.55, 6.5, 2.8, [
    ("E-plane within 3.7° from 2 to 6 GHz; H-plane within 6° from 3 to 6 GHz, 12° to 17° wider at 2 to 2.5 GHz.", {"bullet": True}),
    (f"10 GHz: our yz cut follows the paper's CST pattern (Fig. 11) within {F11H.rms_dB:.1f} dB rms; front lobe "
     f"{F11H.front_width:.1f}° against {F11P.front_width:.1f}°.", {"bullet": True}),
    (f"Table III at 10 GHz (53.8° / 47.3°) is narrower than both lobes of the paper's own Fig. 11 "
     f"({F11P.front_width:.1f}°, {F11P.back_width:.1f}°).", {"bullet": True}),
    ("15 GHz: strongest lobe along the balun, 24° wide; the paper shows no 15 GHz pattern.", {"bullet": True}),
], size=12)

# 9. Summary of validation
s = new_slide("Validation summary", "Each result of the paper and what our simulation gives")
table(s, 0.5, 1.6, 12.3, [
    ["result in [1]", "value in [1]", "this project"],
    ["structure B back to back, |S11| < −10 dB", "1.75 to 15 GHz", f"{B.lo_GHz:.2f} to 15 GHz"],
    ["insertion loss, back to back", "below 3 dB", f"below {abs(B.S21_min_p):.2f} dB"],
    ["structure A back to back", "2 to 14.3 GHz, worse than B", A_SUMMARY],
    ["phase of strip currents", "180°", f"180° ± {B.dphi_max_p:.1f}°, common mode {B.cmrr_min_p:.1f} dB down"],
    ["surface current at 2.5 GHz", "symmetric", "symmetric"],
    ["longer balanced section", "no change", SHORT_SUMMARY],
    ["spiral input match", "2.5 to 15 GHz, measured", SPI_SUMMARY],
    ["spiral pattern at 10 GHz", "Fig. 11 (CST)", f"front lobe {F11H.front_width:.1f}° against {F11P.front_width:.1f}°, {F11H.rms_dB:.1f} dB rms"],
    ["spiral beamwidths", "Table III", "E within 3.7° at 2 to 6 GHz, H within 6° at 3 to 6 GHz"],
    ["impedance of the table rows", "as stated", "two rows inconsistent; corrected design used"],
], widths=[3.6, 3.4, 5.3], size=12)

# 10. Improved design
sw = pd.read_csv(RES / "improved_sweep.csv")
s = new_slide("Improved design", "Klopfenstein taper over 60 of the 70 mm, every cross-section solved for its impedance")
picture(s, "fig_profiles", 0.4, 1.55, w=6.4)
picture(s, "fig_layout_improved", 0.4, 4.25, w=6.4)
label(s, 7.0, 1.6, "What changed")
text(s, 7.0, 1.95, 5.8, 3.0, [
    ("Taper 60 mm instead of 45 mm; the paper's 20 mm of parallel strip does nothing for matching, 5 mm kept.", {"bullet": True}),
    ("Klopfenstein profile, ripple Γm = 0.12 (−18.4 dB), A = 2.393: lowest passband reflection for the length.", {"bullet": True}),
    ("Width ratio w′/w = 1 + 2.75(1 − u)², from 3.75 at the feed to 1 at the end; top width solved at 121 points from a table of 780 cross-sections.", {"bullet": True}),
    ("188 Ω parallel strip is 0.786 mm (paper 0.88 mm, 178 Ω).", {"bullet": True}),
], size=13)
rows = [["taper", "Γm", "back to back from", "one balun from"]]
for _, r in sw[(sw.p == 2.0) & sw.Lt.isin([45, 60]) & sw.gm.isin([0.10, 0.12, 0.15])].iterrows():
    rows.append([f"{r.Lt:g} mm", f"{r.gm:.2f}", f"{r.b2b_lo_GHz:.2f} GHz", f"{r.single_lo_GHz:.2f} GHz"])
label(s, 7.0, 4.95, "Line-model sweep")
table(s, 7.0, 5.3, 5.8, rows, size=11, row_h=0.26)

# 11. Improved results
s = new_slide("Improved design: results", "Same board, same substrate, same settings in openEMS")
picture(s, "fig_compare", 0.4, 1.5, w=6.6)
table(s, 7.2, 1.6, 5.6, [
    ["", "paper design", "improved"],
    ["back to back below −10 dB from", f"{B.lo_GHz:.2f} GHz", f"{I.lo_GHz:.2f} GHz"],
    ["worst |S11|, 1.75 to 15 GHz", f"{B.worst_S11_p:.1f} dB", f"{I.worst_S11_p:.1f} dB"],
    ["lowest |S21|, 1.75 to 15 GHz", f"{B.S21_min_p:.2f} dB", f"{I.S21_min_p:.2f} dB"],
    ["one balun below −10 dB from", f"{SB.lo_GHz:.2f} GHz", f"{SI.lo_GHz:.2f} GHz"],
    ["one balun, worst |S11|, 1.75 to 15 GHz", f"{SB.worst_S11_p:.1f} dB", f"{SI.worst_S11_p:.1f} dB"],
    ["phase error of strip currents", f"{B.dphi_max_p:.1f}°", f"{I.dphi_max_p:.1f}°"],
    ["common mode below differential", f"{B.cmrr_min_p:.1f} dB", f"{I.cmrr_min_p:.1f} dB"],
    ["spiral, worst |S11|, 2.5 to 15 GHz", f"{SPI.loc['paper', 'worst_2p5_15']:.1f} dB", f"{SPI.loc['improved', 'worst_2p5_15']:.1f} dB"],
    ["spiral below −10 dB", spiral_match("paper"), spiral_match("improved")],
], widths=[2.65, 1.75, 1.2], size=11)
text(s, 7.2, 5.25, 5.6, 2.1, [
    (f"Back to back {I.lo_GHz:.2f} to beyond 15 GHz: {15 / I.lo_GHz:.1f} to 1, against {15 / 1.75:.1f} to 1 in the paper.", {"bullet": True}),
    (f"One balun into 188 Ω from {SI.lo_GHz:.2f} GHz: the whole L band.", {"bullet": True}),
    ("Better balance and lower loss over the whole band.", {"bullet": True}),
], size=13)

# 12. Conclusion
s = new_slide("Conclusion")
text(s, 0.5, 1.7, 12.2, 5.2, [
    (f"The balun of [1], built to its impedance profile, is matched back to back from {B.lo_GHz:.2f} to 15 GHz (paper 1.75 to 15 GHz); balance, surface current, structure A and the balanced section test agree with the paper.", {"bullet": True, "space": 12}),
    (f"The paper's spiral antenna with this balun under it is matched from {SPI_RANGE} (measured in the paper: 2.5 to 15 GHz); its 10 GHz pattern follows the paper's Fig. 11 and its E-plane beamwidth is within 3.7° of Table III up to 6 GHz.", {"bullet": True, "space": 12}),
    ("Our cross-section solver found two rows of Table I that do not give their stated impedance; built as printed they add two peaks near 6 GHz.", {"bullet": True, "space": 12}),
    (f"The improved Klopfenstein taper keeps the 70 mm × 18 mm board and is matched from {I.lo_GHz:.2f} GHz back to back and {SI.lo_GHz:.2f} GHz as a single balun, with better balance and lower loss: L, S, C and X bands.", {"bullet": True, "space": 12}),
], size=17)

cp = prs.core_properties
cp.title = "Wideband microstrip to parallel strip balun for L, S, C and X band applications"
cp.author = "Rushil Jain; Jainam Sonigara"
cp.last_modified_by = "Rushil Jain"
cp.comments = ""
cp.subject = "EC301 RF Components and Circuits, course project 12"
out = HERE / "Wideband_Balun.pptx"
prs.save(out)
print("wrote", out.name, len(prs.slides._sldIdLst), "slides")
