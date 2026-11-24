# Presentation and viva notes

## The project in one minute

A balun joins an unbalanced 50 Ω line to a balanced 188 Ω load (a self-complementary spiral antenna, η0/2). We took the tapered microstrip to parallel strip balun of Vinayagamoorthy et al. (IEEE VTC 2012), rebuilt it in the open-source FDTD solver openEMS driven from MATLAB, and checked every result of the paper. Built to the impedance profile the paper states, it is matched back to back from 1.78 GHz to 15 GHz (paper: 1.75 to 15 GHz), and the balance, field map, structure A comparison, balanced section test and spiral antenna all agree. Along the way our cross-section solver found two rows of the paper's Table I whose widths do not give the stated impedance. We then redesigned the taper (Klopfenstein, solved point by point) in the same 70 × 18 mm board: back to back from 1.17 GHz, single balun from 0.95 GHz, so the whole L band is covered.

## D-day: 5-minute presentation

**Before your turn:** laptop on the charger. Run `python3 run_demo.py` in the project folder (WSL) or `python run_demo.py` (Windows). The "Wideband balun" window appears in 15 to 30 s. Press **Model and mesh in openEMS** once and close it, so it opens fast later.

No live solving in the 5 minutes. Every button below opens at once, from finished openEMS runs. Do not press the two "Run simulation" buttons unless he asks to see the solver run (they take about 3 minutes).

| time | press | what to say |
|---|---|---|
| 0:00 to 0:40 | **3D model** | A balun joins the unbalanced 50 Ω line to the balanced 188 Ω spiral antenna. Base paper: Vinayagamoorthy et al., IEEE VTC 2012, tapered microstrip to parallel strip, 1.75 to 15 GHz. The ground narrows until it is as wide as the strip. |
| 0:40 to 1:15 | **Model and mesh in openEMS** | This is the model the solver ran: 3.08 million cells, 0.08 mm cells at the strip edges, copper and substrate losses, absorbing boundaries. |
| 1:15 to 1:50 | **Pulse moving through the balun**, press Play | openEMS result: the pulse enters as microstrip, squeezes into the narrow strips, comes out balanced. |
| 1:50 to 2:20 | **E field in the cross-section** | Left: field from strip down to a wide ground. Right: symmetric between two equal strips. That is the balun's job. |
| 2:20 to 3:10 | **Structure B against the paper**, then **Table I as printed** | 1.78 to 15 GHz against the paper's 1.75, \|S21\| never below −0.98 dB. Two rows of the paper's Table I give the wrong impedance; built as printed they add two peaks near 6 GHz, so we built to the impedances the paper states. |
| 3:10 to 4:30 | **What each change did**, then **Paper design against improved** | Goal: the whole L band from 1 GHz on the same 70 × 18 mm board. Taper 45 to 60 mm, because the paper wasted 20 mm on parallel strip. Exponential to Klopfenstein, the lowest cutoff for a given length. Alone: 1.04 and 1.14 GHz. Together: one balun from 0.95 GHz, back to back from 1.17 GHz. |
| 4:30 to 5:00 | say it | Every paper result reproduced in openEMS, an error found in its Table I, and an improved balun covering L, S, C and X bands with better balance and lower loss. Simulation only; fabrication is next. |

If he asks about the mesh: **Mesh check** (0.7, 2.8 and 6.7 million cells all give 1.77 to 1.78 GHz). Balance: **Current balance**. Antenna: **Spiral antenna, S11** and **pattern**. A possible split: one speaker up to 2:20, the other from 2:20.

## Live demo

Before he arrives: in the project folder run `python3 run_demo.py` (WSL) or `python run_demo.py` (Windows). It prints "all present" and the button window appears in about 15 to 30 seconds. Close other heavy programs, because the solver uses 16 threads. Keep the laptop plugged in. Press **Model and mesh in openEMS** once beforehand so the first press is not slow.

Order, about 10 minutes:

1. **3D model.** Top strip narrows from 4.8 mm, ground narrows from 18 mm, both meet at equal width. Drag to rotate.
   **Model and mesh in openEMS** opens the actual solver model in openEMS's own viewer (AppCSXCAD): 583 × 129 × 41 grid lines, 3.08 million cells, smallest cell 0.079 mm across the strip edges. Use it when he asks how the structure was meshed.
2. **Run simulation: improved (3 min).** Press it first, then keep talking. A console opens with the timestep, speed and field energy; the run stops when the energy is 50 dB below its peak. The window closes itself and the graph appears. The live run uses a coarser mesh (0.7 million cells instead of 3.1 million). Its graph draws the saved full run in grey behind it. Measured difference: band edge 1.16 GHz against 1.17 GHz (both shown in the title), worst |S11| within 0.3 dB, |S21| within 0.21 dB. Say openly that it is the coarse copy.
3. **Pulse moving through the balun.** Drag the slider and stop in the taper. The pulse squeezes into the narrow strip at the centre and spreads out again.
4. **E field in the cross-section.** Left: field goes from strip down to a wide ground (microstrip). Right: symmetric between two equal strips (balanced). This picture is what a balun does.
5. **Structure B against the paper**, **Mesh check** (coarse 0.7 M, normal 2.8 M, fine 6.7 M cells: band edge 1.78, 1.78, 1.77 GHz), **Table I as printed**, **Current balance**, **Spiral S11**, **Pattern** (use the frequency menu; 10 GHz has the paper's curve on it).
6. **Impedance along the taper**, **What each change did**, **Paper design against improved**.

If the solver fails or you close its window, the graph of the saved coarse run comes up by itself, with "saved coarse run" in the title. **Show the last run again** does the same at any time.

## What we changed and why

There are two groups of changes. The first group was needed to reproduce the paper. The second is our improvement.

### To reproduce the paper

**1. Built to the impedances in Table I and did not use two of its printed widths.** With w = 1.2 mm and a 2 mm ground, the row at 29.8 mm gives 132.5 Ω, and the table says 110 Ω. The row at 41.5 mm gives 139.9 Ω, and the table says 150 Ω. We simulated both versions. The printed widths give two extra peaks (−6.7 dB at 5.42 to 6.10 GHz, −9.0 dB at 6.78 to 7.13 GHz) that the paper's own curve does not have. Button: Table I as printed.

**2. Parallel strip 0.786 mm instead of 0.88 mm.** Our solver gives 178 Ω for 0.88 mm, and the closed form gives 180 Ω. The paper wants 188 Ω, which needs 0.786 mm.

**3. Widths solved every 0.5 mm instead of joining 7 table rows.** The paper found its points by a CST sweep and gives only seven. We solve the top width at each point for the target impedance, with the ground to strip ratio falling smoothly from 3.75 to 1.

### The improvement

The aim was the full L band from 1 GHz on the same 70 × 18 mm board, so the only freedom was how the 70 mm is used.

**4. Taper from 45 mm to 60 mm.** A taper's lower edge scales as 1/L. The paper spends 20 mm on parallel strip that does nothing for matching, so we moved that length into the taper and kept 5 mm of strip.

**5. Exponential to Klopfenstein.** For a fixed length and fixed ripple, Klopfenstein has the lowest cutoff of any taper. It is the limit of a Chebyshev multisection transformer.

**6. Ripple Γm = 0.12.** Γ0 = ½ ln(188/50) = 0.662, so cosh A = 0.662 / 0.12 and A = 2.393. Smaller ripple raises the edge, larger ripple lowers it. Back to back the two reflections can add to 2Γm: 0.12 gives at worst −12.4 dB, which leaves margin, while 0.15 gives −10.5 dB, almost no margin, and moves the line-model edge by only 0.05 GHz (1.05 to 1.00 GHz).

**Which change did what.** We simulated each one separately in openEMS (button: What each change did):

| design | one balun, below −10 dB from | back to back, worst \|S11\| 1.75 to 15 GHz |
|---|---|---|
| paper: exponential, 45 mm | 1.15 GHz | −9.6 dB |
| longer: exponential, 60 mm | 1.04 GHz | −12.7 dB |
| new shape: Klopfenstein, 45 mm | 1.14 GHz | −11.0 dB |
| both: Klopfenstein, 60 mm | **0.95 GHz** | **−13.9 dB** |

The short answer: **neither change alone gets below 1 GHz; together they do.** Length moves the edge most (1.15 to 1.04 GHz). The Klopfenstein shape alone barely moves the edge at 45 mm, but it lowers the reflection, and on the longer taper it takes the edge the rest of the way to 0.95 GHz.

### Follow-up questions on the changes

**Why compare with one balun and not back to back?** The back-to-back edge is a threshold effect. The paper design has one ripple peak at −8.84 dB near 1.63 GHz, so its edge reads 1.78 GHz. Pull that peak under −10 dB and the edge jumps to about 1.1 GHz, where the curve first drops below −10 dB. So 1.78 to 1.17 GHz overstates the real gain. The one-balun edge, 1.15 to 0.95 GHz, is the fair measure.

**Was "longer" really only a length change?** Almost. The paper's law gives 57.1 Ω at z = 5 mm, where the line is 50 Ω, so it has a small step at the feed. Our 60 mm exponential runs from 50 Ω with no step, so that row includes removing the step too.

**Your formula says the band starts at βL = A. Does the simulation agree?** With A = 2.393, L = 60 mm and εeff about 1.85, βL = A at 1.40 GHz. That is where |S11| should reach the ripple level of −18.4 dB. The simulated single balun reaches −18.4 dB at 1.32 GHz, about 6 % away. The −10 dB edge is lower, at 0.95 GHz, because the reflection is still rising below the passband.

**Does the improved balun make the antenna work at 1 GHz?** No. With it the antenna is matched from 1.61 GHz, because the spiral's size sets that limit (the spiral alone starts at 1.65 GHz). What improves is the top of the band: the −9.4 dB bump at 13.8 GHz goes away. A larger spiral could use the balun's lower edge.

**Is the whole L band covered back to back?** No. Back to back the improved design starts at 1.17 GHz. The single balun, which is what feeds an antenna, starts at 0.95 GHz.

**What would you do next?** Fabricate it and measure it. Everything here is simulation.

## Slide by slide

1. Title. Base paper, what we did, headline numbers.
2. Why a wideband balun; why a tapered one (no resonant length, band set by taper length); the paper's specification.
3. How it works: ground narrows until both conductors are equal, which turns the microstrip mode into the balanced parallel-strip mode and 50 Ω into 188 Ω. Taper reflection formula; back to back the two reflections can add, |S11| ≤ 2|Γ1|.
4. Tools: openEMS (FDTD, Yee grid, one pulse covers 0.5 to 16 GHz), our 2D cross-section solver (within 1.2 % of Hammerstad), the line model. Setup check on a plain 50 Ω line.
5. Table I check: the stated impedances follow Z = 50 (188/50)^(z/50) exactly. Rows at 29.8 mm (132.5 Ω vs 110) and 41.5 mm (139.9 vs 150) don't. So we built B to the stated impedances: widths solved every 0.5 mm with our solver, ground/strip ratio falling smoothly, 0.786 mm (188 Ω) parallel strip.
6. Structure B back to back: 1.78 to 15 GHz (1.77 with every cell 1.5 times smaller), same shape as the paper's CST curve, |S21| ≥ −0.98 dB. With the widths as printed: two extra peaks near 5.8 and 6.9 GHz, predicted by the line model (two impedance rises 18 mm apart add in phase at c / (2 · 18 mm · √1.8) ≈ 6.2 GHz).
7. Balance (180° ± 8.8°, common mode 21.8 dB down), field map at 2.5 GHz (symmetric), 40 mm vs 4 mm balanced section (both matched, power balance within 0.5 dB), structure A (92.7 % vs 99.6 % of the band, B better as in the paper).
8. Spiral: spiral board and balun board in one openEMS model (Fig. 9 of the paper), 20 million cells, 1.7 hours. Below −10 dB from 1.75 to 15 GHz except −9.4 dB at 13.65 to 13.90 GHz (paper measured 2.5 to 15), follows the measured curve 2 to 5 GHz including the dip near 3.5 GHz.
9. Pattern and beamwidth: E-plane within 3.7° of Table III at 2 to 6 GHz, H-plane within 6° at 3 to 6 GHz. At 10 GHz our yz cut sits on the paper's Fig. 11 CST curve (front lobe 66.9° vs 66.8°); Table III's 10 GHz numbers are narrower than both lobes of that figure.
10. Summary table.
11. Improved design: 60 mm Klopfenstein taper (ripple 0.12, A = 2.393), width ratio rule, 0.786 mm strips.
12. Results table against the paper design.
13. Conclusion.

## Questions to expect

Why openEMS and not HFSS/CST/ADS? None was available to us; openEMS is a free, published FDTD solver (Liebig) used in research. We checked it on a uniform 50 Ω line (Z0 50.9 to 53.2 Ω, |S11| below −31.7 dB) and checked our cross-section solver against Hammerstad-Jensen.

What is FDTD? Maxwell's curl equations discretised on a staggered (Yee) grid and stepped in time. A broadband Gaussian pulse is injected, port voltages and currents are recorded, and a Fourier transform gives S-parameters over the whole band from one run. The time step is limited by the smallest cell (Courant limit).

What is a back-to-back measurement and why is it stricter? Two identical baluns joined at the balanced ends, measured with an ordinary two-port analyser. The two reflections arrive with opposite sign and a delay, so the pair can reflect up to twice as much as one balun.

Why 188 Ω? A self-complementary antenna (metal and slot shapes identical) has input impedance η0/2 ≈ 188 Ω, independent of frequency (Mushiake). The spiral with arm width equal to spacing is self-complementary.

What exactly is the "paper design"? The paper says the impedance follows an exponential law (its Fig. 2(a)) and lists impedances in Table I: 70 Ω at 12.7 mm, 90 at 22.2, 110 at 29.8, 150 at 41.5, 170 at 46.2, 188 at 50. These are exactly Z = 50 (188/50)^(z/50). The paper found the widths by a CST parameter sweep; we found them with our cross-section solver, at every 0.5 mm instead of 7 points. Same impedance profile, same length, same board.

Why not just use the widths in Table I? We did that too. Two rows give the wrong impedance (with w = 1.2 mm, a 2 mm ground gives 132.5 Ω; 110 Ω needs about 6.3 mm, so possibly a misprint of 6). Built as printed, the balun has two peaks the paper's own curves don't show. The line model predicts the same peaks from the impedance profile alone, so they come from the table, not from our modelling.

Why 0.786 mm and not 0.88 mm for the parallel strip? Our solver gives 178 Ω for 0.88 mm (the closed form gives 180 Ω). The paper says 188 Ω, which needs 0.786 mm.

What is the Klopfenstein taper? The impedance profile with the smallest passband reflection for a given length; the limit of a Chebyshev multisection transformer as the number of sections goes to infinity. Small steps of Γm at both ends; passband starts at βL = A, with cosh A = Γ0 / Γm.

How did you choose 60 mm and Γm = 0.12? Line-model sweep (Table 8): longer is always better; larger Γm lowers the edge but raises the in-band reflection. 60 mm keeps the 70 mm board (5 mm feed + 60 mm taper + 5 mm parallel strip). 0.12 gives a single-balun edge near 1 GHz.

How did you get the widths at every point? We tabulated the cross-section solver over 780 combinations of top and bottom width, set the bottom-to-top ratio to fall as 1 + 2.75(1 − u)², and at each point solved for the top width that gives the target impedance. Same method for the paper design (exponential target) and the improved design (Klopfenstein target).

Why is the back-to-back edge (1.17 GHz) higher than the single-balun edge (0.95 GHz)? The two reflections add in the pair (up to 2|Γ1|).

How did you simulate the antenna? As one model, like Fig. 9: the 60 × 60 mm spiral board with the copper on top, the 70 × 18 mm balun board standing under its centre, the two strips running up through the spiral board and joining the inner arm ends on the top face, and a 50 Ω lumped port at the bottom edge of the balun. 20 million cells, 0.1 mm at the spiral centre, 40 mm of air, near-field box around everything, energy down 40 dB. The far field comes from openEMS's nf2ff tool.

Why is there a −9.4 dB bump at 13.8 GHz? The input |S11| ripples above 10 GHz with a period of about 1.5 GHz, the round trip between the port and the spiral junction along the 70 mm balun. One ripple peak just touches −10 dB. The paper's measured curve also ripples there.

Does the improved balun help the antenna? Yes, at the top end: with it the antenna is below −10 dB from 1.61 to 15 GHz with no break (worst −10.2 dB above 2.5 GHz); with the paper's balun there is −9.4 dB at 13.65 to 13.90 GHz. The lower limit (about 1.6 GHz) is set by the spiral's size, so it barely moves. The balun itself now reaches 0.95 GHz, so a larger spiral could use the full L band. Patterns with the two baluns differ by under about 2° up to 10 GHz.

Beamwidths: Table III must be CST output (the measured pattern in Fig. 11 has points only every 30°). CST gives the width of the strongest lobe of a cut, 3 dB below its peak; we computed it the same way. The spiral radiates almost equally to both sides (within 1.2 dB up to 10 GHz), so the strongest lobe is in front at 2 to 2.5 GHz and behind (balun side) above that. E-plane within 3.7° at 2 to 6 GHz; H-plane within 6° at 3 to 6 GHz, 12° to 17° wider at 2 to 2.5 GHz.

Why don't 10 and 15 GHz match Table III? At 10 GHz we compared with the paper's own simulated pattern (Fig. 11), read from the figure: lobes 66.8° and 82.6° wide. Ours: 66.9° and 76.3°, 2.4 dB rms. Table III says 53.8° and 47.3°, narrower than both lobes of its own figure, so that row doesn't describe Fig. 11. At 15 GHz our strongest lobe points along the balun and is 24° wide (paper 42.6° and 34.4°); the paper shows no pattern there to compare with.

Limitations if asked: simulation only (no connectors, soldering, layer alignment); loss tangent and copper from the data sheet; structure A ground outline taken from the photograph.

## Numbers worth remembering

* Substrate RT/duroid 5880, εr 2.2, h 1.5748 mm; 50 Ω line 4.8 mm; parallel strip 0.88 mm = 178 Ω, 0.786 mm = 188 Ω.
* Paper design back to back: 1.78 to 15 GHz, worst −9.6 dB at 1.75 GHz, |S21| ≥ −0.98 dB, phase within 8.8°, common mode 21.8 dB down.
* Mesh check: every cell 1.5 times smaller (6.7 million cells): band from 1.77 GHz, |S21| within 0.12 dB, phase within 0.15°.
* Widths as printed: 90.6 % of 1.75 to 15 GHz, peaks −6.7 dB (5.42 to 6.10) and −9.0 dB (6.78 to 7.13).
* Structure A: 92.7 % of the band, peaks −6.9 dB (2.88 to 3.55) and −9.6 dB (5.55 to 5.80).
* Improved back to back: 1.17 to 15 GHz, worst −13.9 dB, |S21| ≥ −0.70 dB, phase 7.2°, common mode 23.5 dB down, max lost power 11.5 % (paper design 12.9 %).
* Single balun into 188 Ω: paper design from 1.15 GHz (worst −16.2 dB), improved from 0.95 GHz (worst −18.0 dB).
* Spiral: alone from 1.65 GHz; with the paper's balun (full model) 1.75 to 15 GHz except −9.4 dB at 13.65 to 13.90 GHz; directivity 3.5 dBi at 2 GHz, 6.6 dBi at 10 GHz; with the improved balun 1.61 to 15 GHz, no break, worst −10.2 dB above 2.5 GHz.
