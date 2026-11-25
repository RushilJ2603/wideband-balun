---
title: "Wideband balun: formulas, choices and results"
subtitle: "EC301 course project 12. Rushil Jain (241EC148), Jainam Sonigara (241EC155)"
---

**Base paper.** K. Vinayagamoorthy, J. Coetzee, D. Jayalath, "Microstrip to parallel strip balun as spiral antenna feed", IEEE VTC Spring 2012. Tapered microstrip to parallel strip balun, 50 Ω to 188 Ω, back to back $|S_{11}| < -10$ dB from 1.75 to 15 GHz.

**Where to look.** File names are in the project folder (`results/`, `src/`). "Report" means `report/Wideband_Balun_Report.pdf`. "Demo" means the button of that name in the window opened by `run_demo.py`.

# 1. Values we used and where they come from

| quantity | value | source |
|------|-------------|-----------|
| substrate | RT/duroid 5880, $\varepsilon_r = 2.2$, $h = 1.5748$ mm | paper, Section II |
| loss tangent | $\tan\delta = 0.0009$ | Rogers RT/duroid 5880 data sheet, value at 10 GHz (not in the paper); `src/balun_params.m` |
| loss in openEMS | conductivity $\kappa = 2\pi f \varepsilon_0 \varepsilon_r \tan\delta$ at $f$ = 10 GHz $= 1.1 \times 10^{-3}$ S/m | `src/add_substrate.m` |
| copper | 35 µm thick (1 oz), $\sigma = 5.8 \times 10^7$ S/m | standard values (not in the paper); `src/balun_params.m` |
| 50 Ω line | 4.8 mm strip on an 18 mm ground, 5 mm long | paper, Table I |
| board | 70 mm × 18 mm per balun | paper, Table II |
| balanced load | 188 Ω $= \eta_0/2$ (self-complementary spiral) | paper, Section II |
| spiral | 2 arms, 8 turns; arm width = gap = inner radius = 0.86 mm; outer radius 28.3 mm; 60 mm × 60 mm board | paper, Section III |
| ports (our choice) | balun: microstrip ports on 10 mm of 50 Ω line, reference plane at the board edge; one balun: 188 Ω lumped port at the balanced end; antenna: 50 Ω lumped port at the balun edge | `src/build_balun.m`, `src/build_spiral.m` |

# 2. Taper formulas

Paper, exponential taper:

$$ Z(z) = 50 \left(\frac{188}{50}\right)^{z/50} \Omega, \qquad |\Gamma| = \frac{1}{2}\ln\frac{Z_L}{Z_0}\left|\frac{\sin\beta L}{\beta L}\right| $$

Improved, Klopfenstein taper:

$$ \ln Z(z) = \frac{1}{2}\ln(Z_0 Z_L) + \frac{\Gamma_0}{\cosh A}\,A^2\,\varphi\!\left(\frac{2z}{L}-1,\,A\right), \qquad \varphi(x, A) = \int_0^x \frac{I_1\!\left(A\sqrt{1-y^2}\right)}{A\sqrt{1-y^2}}\,dy $$

$$ \Gamma_0 = \frac{1}{2}\ln\frac{Z_L}{Z_0}, \qquad \cosh A = \frac{\Gamma_0}{\Gamma_m} $$

$$ \Gamma(\beta L) = \Gamma_0\,e^{-j\beta L}\,\frac{\cos\sqrt{(\beta L)^2 - A^2}}{\cosh A}, \qquad |\Gamma| \le \Gamma_m \ \text{for}\ \beta L \ge A $$

with $\beta = 2\pi f\sqrt{\varepsilon_{\text{eff}}}/c$. Back to back the two reflections can add: $|S_{11}| \le 2|\Gamma_1|$. Line impedance from our 2D solver: $Z_0 = 1/(c\sqrt{C\,C_a})$, $\varepsilon_{\text{eff}} = C/C_a$.

# 3. What we chose

| quantity | paper | improved design |
|---------|---------|------------|
| taper profile | exponential | Klopfenstein |
| taper length $L$ | 45 mm | 60 mm |
| use of the 70 mm | 5 feed + 45 taper + 20 parallel strip | 5 feed + 60 taper + 5 parallel strip |
| $\Gamma_0 = \frac{1}{2}\ln(188/50)$ | 0.662 | 0.662 |
| ripple $\Gamma_m$ | | **0.12** ($-18.4$ dB) |
| $A$ | | 2.393 |
| parallel strip width | 0.88 mm (178 Ω) | 0.786 mm (188 Ω) |
| ground to strip width ratio | 7 table points | $w'/w = 1 + 2.75\,(1-u)^2$, $u = (z - 5\ \text{mm})/60\ \text{mm}$ |
| widths | 7 table points | solved at 121 points for the target impedance |

- **Why 60 mm:** the lower edge scales as $1/L$, and the paper's 20 mm of parallel strip does no matching, so that length went into the taper. 60 mm is the most the 70 mm board allows with the 5 mm feed and 5 mm of parallel strip.

- **Paper design (for validation):** the paper's law $Z = 50\,(188/50)^{z/50}$ from 5 to 50 mm, widths solved every 0.5 mm, 0.786 mm strip.

**Why $\Gamma_m = 0.12$.** $\Gamma_m$ is the reflection we accept inside the passband. It sets $A$ through $\cosh A = \Gamma_0/\Gamma_m$, and the passband starts at $\beta L = A$. So a larger $\Gamma_m$ gives a smaller $A$ and a lower cutoff, but more reflection in the band. In the back-to-back pair the two reflections can add up to $2\Gamma_m$, and that pair still has to stay below $-10$ dB. We compared four values on the 60 mm taper with the line model:

| $\Gamma_m$ | $A$ | in-band ripple $\Gamma_m$ | worst back to back $2\Gamma_m$ | margin under $-10$ dB | line model: one balun from | line model: back to back from |
|---:|---:|---:|---:|---:|---:|---:|
| 0.08 | 2.803 | $-21.9$ dB | $-15.9$ dB | 5.9 dB | 1.15 GHz | 1.30 GHz |
| 0.10 | 2.578 | $-20.0$ dB | $-14.0$ dB | 4.0 dB | 1.10 GHz | 1.30 GHz |
| **0.12** | **2.393** | $-18.4$ dB | $-12.4$ dB | **2.4 dB** | **1.05 GHz** | 1.25 GHz |
| 0.15 | 2.165 | $-16.5$ dB | $-10.5$ dB | 0.5 dB | 1.00 GHz | 1.20 GHz |

- Going from 0.08 to 0.12 lowers the one-balun edge from 1.15 to 1.05 GHz, close to the 1 GHz goal.

- 0.12 still leaves a 2.4 dB margin for the back-to-back pair.

- 0.15 would leave only 0.5 dB of margin and gain just 0.05 GHz (1.05 to 1.00 GHz), so 0.12 is the best trade.

- Source: `results/improved_sweep.csv` (rows with Lt = 60, p = 2); report Table 8.

# 4. Simulation settings (openEMS v0.37, FDTD)

| item | setting |
|----|----------------|
| excitation | Gaussian pulse, 0.5 to 16 GHz |
| mesh | 0.08 mm at the strips, 0.4 mm along the line, 6 cells through the substrate |
| boundaries | 8-cell PML, 20 mm of air |
| stop | field energy 50 dB below its peak |
| size and time | paper design 2.84 M cells, improved 3.08 M cells, 3 to 10 min per run on 16 threads; antenna 20 M cells, 1.7 h |

# 5. Every frequency: what it is and where to find it

"Matched from $f$" means $|S_{11}|$ stays below $-10$ dB from $f$ up to 15 GHz. "Back to back" is two baluns joined at the balanced ends (50 Ω to 50 Ω). "One balun" is a single balun into a 188 Ω load.

**From the paper**

| frequency | what it is | where |
|------|-----------|------------|
| 1.75 to 15 GHz | structure B back to back, $\lvert S_{11}\rvert < -10$ dB, CST and measured | paper Fig. 7(d), Table II |
| 2 to 14.3 GHz | structure A back to back | paper Table II |
| 2.5 to 15 GHz | spiral antenna with balun, measured | paper Fig. 10 |
| 1.69 GHz | lowest frequency of the spiral ($f_L$) | paper Section III |
| 1 to 12 GHz | L (1 to 2), S (2 to 4), C (4 to 8), X (8 to 12 GHz): the bands in the project title | |

**Our balun results**

| frequency | what it is | where |
|------|-----------|------------|
| **1.78 GHz** | paper design, back to back, matched from (paper: 1.75) | `results/summary.csv` row `b2b_paper_B_stated`; report Table 10; demo "Structure B against the paper" |
| **1.17 GHz** | improved design, back to back, matched from | `summary.csv` row `b2b_improved`; report Table 10; demo "Paper design against improved" (top) |
| **1.15 GHz** | paper design, one balun into 188 Ω, matched from | `summary.csv` row `single_paper_B_stated`; report Table 10; same demo (bottom) |
| **0.95 GHz** | improved design, one balun into 188 Ω, matched from | `summary.csv` row `single_improved`; report Table 10; same demo (bottom) |
| 1.625 GHz | the one ripple peak ($-8.84$ dB) that puts the paper design's back-to-back edge at 1.78 GHz | `results/b2b_paper_B_stated.csv` |
| 3.15 GHz | paper design back to back: highest ripple above 2 GHz, $-11.0$ dB | report Section 5.2 |
| 1.56 GHz | paper design back to back with 4 mm instead of 40 mm of parallel strip in the middle | `summary.csv` row `b2b_paper_B_stated_short`; report Section 5.5 |

**One change at a time**

| design | one balun, matched from | back to back, matched from | where |
|---------|-----|-----|---------|
| paper: exponential, 45 mm | 1.15 GHz | 1.78 GHz | `single_`/`b2b_paper_B_stated.csv` |
| longer only: exponential, 60 mm | 1.04 GHz | 1.24 GHz | `single_`/`b2b_step_exp60.csv` |
| shape only: Klopfenstein, 45 mm | 1.14 GHz | 1.15 GHz | `single_`/`b2b_step_klop45.csv` |
| both: Klopfenstein, 60 mm | **0.95 GHz** | 1.17 GHz | `single_`/`b2b_improved.csv` |

All in `results/`, shown together in demo "What each change did". The back-to-back edge depends on single ripple peaks, so the one-balun column is the fair comparison.

**Design predictions (line model and formula)**

| frequency | what it is | where |
|------|-----------|------------|
| 1.25 / 1.05 GHz | line model of the chosen design: back to back / one balun | `results/improved_sweep.csv`; report Table 8 |
| 1.40 GHz | $\beta L = A$ for $L$ = 60 mm, $\varepsilon_{\text{eff}} \approx 1.85$: where $\lvert S_{11}\rvert$ should reach $\Gamma_m$ ($-18.4$ dB) | formula above |
| 1.32 GHz | where the simulated improved single balun reaches $-18.4$ dB (6 % from 1.40) | `results/single_improved.csv` |

**Spiral antenna**

| frequency | what it is | where |
|------|-----------|------------|
| 1.65 GHz | spiral alone (188 Ω feed), matched from | `results/spiral_lumped.csv`; report Section 5.6 |
| 1.75 to 15 GHz, except 13.65 to 13.90 GHz ($-9.4$ dB) | antenna with the paper design | `results/spiral_numbers.csv`; report Table 10; demo "Spiral antenna, S11" |
| 1.61 to 15 GHz, no gap | antenna with the improved balun | `results/spiral_numbers.csv`; report Table 10; same demo |
| 2, 2.5, 3, 4, 5, 6, 10, 15 GHz | pattern and beamwidth frequencies (as in paper Table III) | `results/spiral_full_hpbw.csv`; report Table 6; demo "Spiral antenna, pattern" |

**Checks and the frequencies used in the setup**

| frequency | what it is | where |
|------|-----------|------------|
| 1.77 GHz | paper design back to back with every cell 1.5 times smaller (6.73 M cells) | `results/b2b_paper_B_stated_fine.csv`; report Section 5.2; demo "Mesh check" |
| 1.78 GHz | the same on the coarse demo mesh (0.67 M cells) | `results/live_paper.csv`; demo "Mesh check" |
| 1.16 GHz | improved design on the coarse demo mesh (0.71 M cells; full mesh 1.17) | `results/live_improved.csv`; demo "Show the last run again" |
| 0.5 to 16 GHz | excitation band of every balun run | `src/build_balun.m`; report Table 3 |
| 10 GHz | frequency at which the loss tangent is set | `src/add_substrate.m` |
| 2.5 GHz, 10 GHz | surface current (H-field) maps | report figures in Sections 5.4 and 6.3 |
| 5 GHz | field in three cross-sections | demo "E field in the cross-section" |

# 6. Other results

| result | paper design | improved | where |
|----------|----|----|-----------|
| back to back, worst $\lvert S_{11}\rvert$, 1.75 to 15 GHz | $-9.6$ dB | $-13.9$ dB | `summary.csv` column `worst_S11_p`; report Table 10 |
| back to back, lowest $\lvert S_{21}\rvert$, 1.75 to 15 GHz (paper: above $-3$ dB) | $-0.98$ dB | $-0.70$ dB | column `S21_min_p`; report Table 10 |
| one balun, worst $\lvert S_{11}\rvert$, 1.75 to 15 GHz | $-16.2$ dB | $-18.0$ dB | `summary.csv`; report Table 10 |
| strip current phase difference (paper: 180°) | 180° ± 8.8° | 180° ± 7.2° | column `dphi_max_p`; demo "Current balance" |
| strip current amplitude difference | 1.34 dB | 1.04 dB | column `damp_max_p` |
| common mode below differential mode | 21.8 dB | 23.5 dB | column `cmrr_min_p` |
| largest share of power lost | 12.9 % | 11.5 % | column `loss_max`; report Table 10 |

| check | result | where |
|-------|-----------|---------|
| structure A against structure B | A matched on 92.7 % of 1.75 to 15 GHz, B on 99.6 %; B better, as in the paper | `summary.csv` column `ok_p`; report Section 5.3 |
| 40 mm against 4 mm of parallel strip in the middle | both matched; $\lvert S_{11}\rvert^2 + \lvert S_{21}\rvert^2$ within 0.43 dB | report Section 5.5 |
| our 2D solver against Hammerstad-Jensen | within 1.2 % | `results/solver_check.csv`; report Table 4 |
| plain 50 Ω line, same setup | line impedance 50.9 to 53.2 Ω, $\lvert S_{11}\rvert < -31.7$ dB from 1 to 15 GHz | `results/check_msl.csv` |

# 7. Spiral antenna: half-power beamwidth and directivity

Beamwidth is measured as CST reports it: the width of the strongest lobe of each full cut, 3 dB below its peak. E-plane is the xz cut (it contains the balanced feed), H-plane the yz cut. "Front" is away from the balun, "back" is towards it. The paper's values are from its Table III.

| f (GHz) | E-plane: paper | E-plane: ours, paper design | E-plane: ours, improved | H-plane: paper | H-plane: ours, paper design | H-plane: ours, improved | strongest lobe |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 94.6° | 97.3° | 96.9° | 81.8° | 93.8° | 92.2° | front |
| 2.5 | 93.5° | 94.4° | 94.1° | 78.5° | 95.2° | 94.4° | front |
| 3 | 86.4° | 85.8° | 86.7° | 78.3° | 81.9° | 83.4° | back |
| 4 | 73.3° | 73.3° | 72.6° | 70.2° | 76.1° | 76.2° | back |
| 5 | 64.9° | 62.2° | 63.1° | 67.1° | 64.9° | 64.9° | back |
| 6 | 61.0° | 57.3° | 57.6° | 60.7° | 59.2° | 58.9° | back |
| 10 | 53.8° | 64.5° | 64.3° | 47.3° | 76.3° | 78.3° | back |
| 15 | 42.6° | 24.2° | 27.0° | 34.4° | 22.5° | 24.2° | back |

- E-plane within 3.7° of the paper from 2 to 6 GHz. H-plane within 6° from 3 to 6 GHz (12° and 17° wider at 2 and 2.5 GHz).

- With the two baluns the beamwidths differ by at most 2° up to 10 GHz.

- **At 10 GHz, against the paper's simulated pattern (Fig. 11):** front lobe 66.9° against 66.8°, back lobe 76.3° against 82.6°, 2.4 dB rms difference (our yz cut). Source: `results/spiral_fig11.csv`.

- The front and back lobes are within 1.2 dB of each other up to 10 GHz: the spiral radiates on both sides of its board.

**Peak directivity** (the paper gives no value; it says only that the gain rises with frequency):

| f (GHz) | 2 | 2.5 | 3 | 4 | 5 | 6 | 10 | 15 |
|------------------------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| paper design under the spiral (dBi) | 3.51 | 3.77 | 4.45 | 5.30 | 5.83 | 6.40 | 6.64 | 9.04 |
| improved balun under the spiral (dBi) | 3.62 | 3.82 | 4.44 | 5.31 | 5.82 | 6.49 | 6.59 | 9.78 |

Sources: `results/spiral_full_hpbw.csv` and `results/spiral_full_improved_hpbw.csv` (columns `hpbw_E_main_deg`, `hpbw_H_main_deg`, `Dmax_dBi`); report Table 6; demo "Spiral antenna, pattern" (frequency menu).
