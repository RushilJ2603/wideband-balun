# Wideband balun project: complete study guide

This guide covers the course project "Wideband BALUN circuit for L, S, C and X band Applications" from the first idea to the final demo. It is written so that a tutor can teach the whole project from it alone.

## 0. How to use this guide

1. Every number about the project in this guide was copied from the project's result files, the report or the base paper. Quote them as they are; do not round them differently or replace them with "typical" values.
2. General theory (transmission lines, S-parameters, FDTD and so on) is explained in Part B. Standard textbook explanations can be added, as long as they agree with the formulas given here.
3. Keep three kinds of statement apart and say which one is meant:
   - what the **base paper** claims (they used CST and measured real boards),
   - what **this project** found (openEMS simulations, a cross-section solver and a line model; nothing was built or measured),
   - **general theory**.
4. A question this guide does not answer (for example who in the team did which part, or a number that is not listed) is answered as "not in the guide", not guessed. Section 34 lists the known gaps.
5. Nothing in this project was fabricated or measured. Every result of "this project" is a simulation.
6. Read in order: Part B (background) before Part C (the paper) before Part D (what was done). Part B assumes no prior knowledge.

---

# Part A. The assignment

## 1. Course and team

- Course: EC301 RF Components and Circuits (RFCC), NITK Surathkal (National Institute of Technology Karnataka), Department of Electronics and Communication Engineering. Semester 5.
- Project number 12 of 36 in the course list: "Wideband BALUN circuit for L, S, C and X band Applications".
- Team: Rushil Jain (241EC148) and Jainam Sonigara (241EC155).
- Stated objective of course projects (from the instruction sheet): "To focus on learning a software tool to design, model/implement and analyse the RF components and circuits."

## 2. Rules and grading (from the instruction sheet, "Instructions to RFCC Course Projects")

- Groups of at most 2 students, same section, each group a different project. Topic cannot be changed once chosen. Group details were due on or before 8-11-2026.
- Rule 7: first find a simple research paper on the topic to get correct design specifications (design frequency, substrate, characteristic impedance, load impedance, permittivity, thickness, gain, bandwidth and so on).
- Rule 8, grading:
  - a) implement the project as per the base research paper, with **all its results validated**, and bring **some improvement** over the existing results: 10/10
  - b) only validate all the results of the paper: 8/10
  - c) confirm only 75 % of the paper's results: 6/10
  - d) 50 % of the results validated: 4/10
  - e) less than 50 %: 2/10
- Rule 9: the group divides the work equally.
- Rule 10: report in **.doc** format, including all results, on or before **27-11-2026 (Friday), 5 PM**.
- The team planned to present before 26-11-2026. The presentation focuses on the simulation, the graphs, and questions such as "what did you change and why did you change exactly this".

So the target was 10/10: reproduce every result of the base paper, then improve on it.

## 3. What was produced

| item | where | notes |
|---|---|---|
| Report, 21 pages | `report/Wideband_Balun_Report.docx`, `.pdf`; also `.doc` in the submission folder | built from `report/report.md` with pandoc by `report/build_report.py` |
| Slides, 13 slides | `slides/Wideband_Balun.pptx`, `.pdf` | built by `slides/build_deck.py` (python-pptx) |
| Submission copies | `RFCC/Project/submission/`: `Wideband_Balun_Report.doc`, `.docx`, `.pdf`, `Wideband_Balun_Slides.pptx`, `.pdf` | the `.doc` was made by saving the `.docx` from Word |
| Code, geometry, results | repository `wideband-balun` | public GitHub repository `RushilJ2603/wideband-balun`, branch `main` |
| Live demo | `run_demo.py` (opens MATLAB) and `src/balun_demo.m` (window of buttons) | Section 31 |
| This guide | `teaching.md` | in the repository |

The base paper is open access as the accepted version on QUT ePrints (eprints.qut.edu.au/48500). The PDF itself is not in the repository.

---

# Part B. Background from zero

## 4. Frequency, wavelength and the bands in the title

- Wavelength in free space: λ0 = c / f, with c = 2.998 × 10^8 m/s. At 1 GHz λ0 = 30 cm; at 10 GHz, 3 cm.
- In a material or on a printed line the wave is slower. On a line with effective permittivity εeff, the guided wavelength is λg = λ0 / √εeff.
- The radar band letters in the project title: L band 1 to 2 GHz, S band 2 to 4 GHz, C band 4 to 8 GHz, X band 8 to 12 GHz. Together they run from 1 GHz to 12 GHz, a 12 to 1 frequency range. The report states this as "The L, S, C and X bands together run from 1 GHz to 12 GHz, a twelve-to-one range."
- "Covering the L band" therefore means working from 1 GHz. This becomes the goal of the improvement.

## 5. Transmission lines

A transmission line is two conductors that guide a wave. Key properties:

- **Characteristic impedance Z0**: the ratio of voltage to current of a single travelling wave on the line. It depends only on the cross-section (conductor widths, spacing, material), not on length. For a lossless line Z0 = √(L'/C'), where L' and C' are inductance and capacitance per metre.
- **Effective permittivity εeff**: on a printed line part of the field is in the substrate and part in air, so the wave sees a permittivity between 1 and εr. Phase velocity v = c / √εeff.
- **Phase constant** β = 2π f √εeff / c (radians per metre). A length L of line delays the wave by βL radians.
- Formulas used in this project: Z0 = 1 / (c √(C · Ca)) and εeff = C / Ca, where C is the capacitance per metre of the real cross-section and Ca the capacitance per metre of the same conductors with the substrate replaced by air. (This works because the inductance does not depend on the dielectric: L' = 1 / (c² Ca).)

## 6. Reflection, matching and S-parameters

- When a wave on a line of impedance Z0 meets a load ZL, part of it reflects. The reflection coefficient is Γ = (ZL − Z0) / (ZL + Z0).
- Fraction of power reflected: |Γ|². Fraction delivered: 1 − |Γ|².
- **S-parameters** of a two-port: S11 is the reflected wave at port 1 divided by the incident wave at port 1 (with port 2 terminated in its reference impedance). S21 is the wave coming out of port 2 divided by the wave incident at port 1. They are complex numbers and functions of frequency.
- In decibels: |S11| (dB) = 20 log10 |S11|. **Return loss** is the same number with the sign flipped: |S11| = −10 dB means a return loss of 10 dB.
- The standard "matched" criterion, used by the paper and by this project, is |S11| < −10 dB. That is |Γ| < 0.316, 10 % of the power reflected, 90 % delivered, VSWR below about 1.92.
- **Insertion loss** is −20 log10 |S21|. "|S21| above −3 dB" means more than half the power gets through.
- **Power balance**: 1 − |S11|² − |S21|² is the fraction of power that is neither reflected nor transmitted, so it is lost to radiation, conductor loss and dielectric loss. The project reports its largest value as "largest share of power lost".
- Useful dB values: −3 dB is half power, −10 dB is one tenth, −20 dB one hundredth. For amplitudes (like |S11|) −10 dB is a factor 0.316, −20 dB is 0.1.

## 7. Microstrip line

- A microstrip line is a narrow copper strip on top of a dielectric substrate with a wide ground plane on the bottom. The field runs from the strip down into the ground, mostly inside the substrate.
- It is **unbalanced**: the ground is large and at "zero" potential; the strip carries the signal.
- Its impedance falls as the strip gets wider (more capacitance). On this project's substrate a 50 Ω microstrip is about 4.8 mm wide (4.85 mm by the Hammerstad and Jensen closed-form formula; the paper uses 4.8 mm).
- **Hammerstad and Jensen** (1980) is the standard closed-form formula for microstrip Z0 and εeff on an infinitely wide ground. The project uses it only to check its own solver. The formula as coded in `src/xsection.py` (function `microstrip_hammerstad`), with u = w/h:
  - a = 1 + ln((u⁴ + (u/52)²) / (u⁴ + 0.432)) / 49 + ln(1 + (u/18.1)³) / 18.7
  - b = 0.564 ((εr − 0.9) / (εr + 3))^0.053
  - εeff = (εr + 1)/2 + (εr − 1)/2 · (1 + 10/u)^(−a·b)
  - F = 6 + (2π − 6) exp(−(30.666/u)^0.7528)
  - Z01 = 60 ln(F/u + √(1 + (2/u)²)) (air-filled line), and Z0 = Z01 / √εeff.

## 8. Parallel strip line

- Two strips of equal width, one on the top face and one on the bottom face of the substrate, directly above each other.
- It is **balanced**: the two strips carry equal and opposite currents and sit at equal and opposite voltages.
- By symmetry the plane halfway between the strips is at zero potential, so the line behaves like two microstrips of half the substrate height in series: Zps(w, h) = 2 · Zms(w, h/2). This is how the closed-form check of the parallel strip was done.
- On this substrate a 0.88 mm parallel strip is about 178 to 180 Ω, and 188 Ω needs 0.786 mm (Section 21).

## 9. Balanced, unbalanced, and what a balun is

- **Unbalanced** line: one conductor is ground (coaxial cable, microstrip).
- **Balanced** load: two terminals with equal and opposite currents, neither one grounded (dipole, spiral antenna, parallel strip).
- Connecting them directly lets part of the current flow back on the outside of the feed (a "common mode" current). That current radiates by itself and distorts the antenna pattern.
- A **balun** (BALanced to UNbalanced) converts between the two. Often it also transforms impedance, here from 50 Ω (the cable and connector) to 188 Ω (the spiral).
- **Differential mode** current: Id = (Itop − Ibot) / 2, the wanted, equal and opposite current. **Common mode**: Ic = (Itop + Ibot) / 2, the unwanted part. A good balun has the two strip currents 180° apart and equal in size, so Ic is small. The project measures the "common mode rejection" as 20 log10 |Id / Ic| in dB (bigger is better).
- Types the report mentions: Marchand and transformer baluns cover about an octave (2 to 1). A **tapered** balun has no resonant length: its lowest frequency is set by how long the taper is, and its highest frequency only by how precisely the geometry is made. That is why a tapered balun was chosen for a 1 to 15 GHz range.

## 10. How the microstrip to parallel strip balun works

- Start with a 50 Ω microstrip: 4.8 mm strip over an 18 mm ground.
- Along the board, the ground (bottom conductor) is made narrower and narrower, and the top strip narrower as well, until both are the same width. At that point the line is a parallel strip.
- As the ground narrows, the field that went from the strip down into a wide ground becomes a field between two equal strips. So the taper does two jobs at once: **mode transformation** (unbalanced to balanced) and **impedance transformation** (50 Ω to 188 Ω).
- The narrowing must be gradual. A sudden change would reflect. How the impedance changes along the length is the "taper profile". The paper used an exponential profile; the improvement uses a Klopfenstein profile.

## 11. Reflection from a taper (theory of small reflections)

Treat each slice of the taper as a short piece of line with impedance Z(z). By the theory of small reflections (Pozar, Microwave Engineering, chapter 5):

Γ(f) = ½ ∫₀ᴸ e^(−2jφ(z)) · d/dz [ln Z(z)] dz, with φ(z) = ∫₀ᶻ (2πf/c) √εeff(z′) dz′.

In words: every place where ln Z changes reflects a little, and the reflections add with a phase set by how far they are from the input. At low frequency they all add in phase (large reflection); at high frequency they cancel (small reflection). That is why a taper is a **high-pass** match: matched above some frequency, set by its length.

**Exponential taper** (ln Z changes linearly with z, so Z = Z0 (ZL/Z0)^(z/L)):

|Γ| = ½ ln(ZL/Z0) · |sin βL / βL|.

For 50 Ω to 188 Ω, ½ ln(188/50) = 0.662, and |Γ| falls below 0.316 (−10 dB) once βL ≥ 1.95.

**Klopfenstein taper** (Klopfenstein, Proc. IRE, 1956): the profile with the lowest reflection in the passband for a given length. It is the limit of a Chebyshev multi-section transformer with infinitely many sections. Its definition:

ln Z(z) = ½ ln(Z0 ZL) + (Γ0 / cosh A) · A² · φ(2z/L − 1, A), with φ(x, A) = ∫₀ˣ I1(A√(1 − y²)) / (A√(1 − y²)) dy,

where Γ0 = ½ ln(ZL/Z0), cosh A = Γ0 / Γm, and I1 is the modified Bessel function of the first kind, order 1. Its reflection is

Γ(βL) = Γ0 e^(−jβL) cos(√((βL)² − A²)) / cosh A,

which stays at or below the ripple Γm for all βL ≥ A. So:

- Γm (the "ripple") is the reflection level you accept in the passband.
- A sets where the passband starts: βL = A.
- Choosing a bigger Γm makes A smaller, so the passband starts at a lower frequency, but the in-band reflection is higher.
- The Klopfenstein profile has small jumps (steps) of size Γm at both ends: it starts at Z0 · e^(Γm) instead of Z0 and ends at ZL · e^(−Γm) instead of ZL. With Γm = 0.12 these are 56.4 Ω (instead of 50) and 166.7 Ω (instead of 188).

Numbers for this project (all from the project files):

| Γm | A | Γm in dB | worst back-to-back, 2Γm |
|---:|---:|---:|---:|
| 0.08 | 2.803 | −21.9 dB | |
| 0.10 | 2.578 | −20.0 dB | |
| 0.12 (chosen) | 2.393 | −18.4 dB | 0.24 = −12.4 dB |
| 0.15 | 2.165 | −16.5 dB | 0.30 = −10.5 dB |

## 12. Back-to-back measurement

- A balun has one unbalanced port and one balanced port. A normal network analyser has unbalanced (coaxial) ports, so you cannot connect the balanced end directly.
- Solution used by the paper (and copied here): join two identical baluns at their balanced ends. The pair goes 50 Ω, 188 Ω balanced, 50 Ω, and can be measured as a normal two-port.
- The two baluns' reflections arrive with opposite sign and a delay, so |S11| ≈ |Γ1| · |1 − e^(−2jβd)| ≤ 2|Γ1|, where Γ1 is one balun's reflection. At some frequencies they cancel, at others they add up to twice one balun's reflection.
- So the back-to-back test is **stricter** than a single balun. In this project the "one balun into 188 Ω" result is also simulated (a lumped 188 Ω port at the balanced end), and it is the fairer measure of one balun.

## 13. Self-complementary spiral antenna

- A **self-complementary** antenna has metal and gaps of exactly the same shape (rotate the metal and you get the slot pattern). Mushiake showed its input impedance is η0 / 2 ≈ 188 Ω at all frequencies, where η0 ≈ 376.7 Ω is the impedance of free space. This is why the balun ends at 188 Ω.
- The paper's antenna is a **two-arm Archimedean spiral**: two arms that wind outward with radius growing linearly with angle. With arm width = gap = inner radius it is self-complementary.
- A spiral radiates from the "active region" where the arm circumference is about one wavelength. The outer radius sets the lowest frequency, and the fineness of the centre sets the highest. The paper puts the low end at fL = 1.69 GHz.

## 14. Antenna pattern terms

- **Far field**: the field far from the antenna, where it is a plane wave travelling outward. The pattern is |E| against direction.
- Spherical angles: θ from the z axis (here the axis of the spiral, θ = 0 is "above" the spiral, away from the balun), φ around it.
- **E-plane and H-plane**: two perpendicular cuts through the pattern. In this project the xz plane (φ = 0, which contains the balanced feed) is called the E-plane and the yz plane (φ = 90°) the H-plane.
- **HPBW (half-power beamwidth)**: the angular width of a lobe between the points 3 dB below its peak.
- **Directivity** (dBi): how much stronger the peak is than the average over all directions.
- **Near-field to far-field transformation (NF2FF)**: an FDTD simulation can only hold a box of space. The fields are recorded on a closed surface around the antenna and transformed mathematically to the far field. openEMS provides this as the `nf2ff` tool.

## 15. FDTD and openEMS

- **FDTD** (finite-difference time-domain): Maxwell's curl equations are written as differences on a grid and stepped forward in time. The electric and magnetic field components sit on a staggered grid (the **Yee grid**, Yee 1966) and are updated alternately (leapfrog).
- The **time step** is limited by the smallest cell (Courant stability limit): Δt ≤ 1 / (c √(1/Δx² + 1/Δy² + 1/Δz²)). Very small cells make the run slower.
- **Excitation**: a short Gaussian pulse contains a whole band of frequencies at once. Port voltages and currents are recorded over time; a Fourier transform gives the S-parameters over the whole band from one run.
- **Stopping**: the run stops when the total field energy has fallen far below its peak (here 50 dB, set as `EndCriteria 1e-5`), or at a maximum number of time steps.
- **Absorbing boundary**: the grid is finite, so its outer layer must absorb outgoing waves. openEMS offers a **PML** (perfectly matched layer, Bérenger 1994). This project uses 8-cell PML on all six sides (`PML_8`).
- **Mesh**: openEMS uses a rectilinear grid. Cells must be small near conductor edges (where fields change fast) and can grow away from them. A common rule is that cells should be a small fraction of the shortest wavelength.
- **openEMS**: a free, open-source FDTD solver by Thorsten Liebig, using the equivalent-circuit FDTD method (EC-FDTD). The project used version 0.37, the Windows build installed at `C:\openEMS`, scripted from MATLAB with the openEMS MATLAB interface (functions like `InitFDTD`, `InitCSX`, `AddPolygon`, `AddMSLPort`, `WriteOpenEMS`, `calcPort`). CSXCAD is its geometry library; AppCSXCAD is its 3D model viewer.
- **Losses in openEMS**: copper is modelled as a "conducting sheet" (a thin layer with a given conductivity and thickness). Dielectric loss is given as a conductivity κ = 2π f ε0 εr tan δ, evaluated at one frequency (10 GHz in this project, `src/add_substrate.m`).
- **Microstrip port** (`AddMSLPort`): a port built on a length of microstrip line, with voltage and current probes along it, so openEMS can separate the incident and reflected waves and also measure the line impedance. `FeedShift` places the source a distance into the line, `MeasPlaneShift` moves the reference plane.
- **Lumped port** (`AddLumpedPort`): a resistor with a source across a small gap, used where there is no line to put a microstrip port on.

## 16. Quasi-static cross-section solver (written for this project)

- For the impedance of a cross-section you only need a 2D electrostatic problem: put +1 V on one conductor and −1 V (or 0) on the other, solve Laplace's equation for the potential, and find the charge, hence the capacitance.
- `src/xsection.py` does this by finite differences (finite-volume form) on a graded 2D grid, with the substrate permittivity in the cells between the two faces, solved with a sparse LU factorisation (scipy). It computes the 2 × 2 capacitance matrix of the two strips, then the capacitance for equal and opposite charge.
- It solves twice, with the substrate and with air, and uses Z0 = 1 / (c √(C · Ca)) and εeff = C / Ca.
- The cross-section in the solver: a top strip of width w on the upper face and a bottom conductor of width w′ (called `wb` in the code) on the lower face, both centred, on a substrate of finite width (board width, default 30 mm in the function; the Table I check uses the default). With w′ much wider than w it is a microstrip; with w′ = w it is a parallel strip.
- "Quasi-static" means it ignores frequency dependence (dispersion). It gives one Z0 and εeff per cross-section.

## 17. Transmission-line (cascade) model (written for this project)

- `src/taper.py`. The balun is cut into short slices (0.5 mm, or 0.25 mm in the design sweep). Each slice is a uniform line with the mean Z and εeff of its two ends (from the cross-section solver).
- Each slice has an ABCD matrix [cos θ, jZ sin θ; j sin θ / Z, cos θ] with θ = β · length. Multiplying all of them gives the whole balun. The ABCD matrix is converted to S11 and S21 for chosen port impedances (50 Ω, or 50 Ω and 188 Ω for one balun).
- A back-to-back pair is made by mirroring the profile about the balanced end.
- It ignores radiation, coupling between distant parts and dispersion, but runs in a fraction of a second, so it was used to sweep many candidate designs. The chosen design was then checked with openEMS.

---

# Part C. The base paper

## 18. What the paper says

**Reference.** K. Vinayagamoorthy, J. Coetzee and D. Jayalath (Queensland University of Technology, Brisbane), "Microstrip to parallel strip balun as spiral antenna feed", Proceedings of the IEEE 75th Vehicular Technology Conference (VTC Spring), Yokohama, 2012, pp. 1 to 5, doi 10.1109/VETECS.2012.6240118. The copy used is the accepted version from QUT ePrints (eprints.qut.edu.au/48500). It was chosen because it is open access, it gives the substrate and a dimension table, and it reports results that can be checked numerically.

**Structure of the paper.** I Introduction, II Microstrip to parallel strip balun, III Configuration of the spiral antenna with balun, IV Conclusion, 10 references. Figures 1 to 11, Tables I to III.

**Section I (Introduction).** Spiral antennas are wideband, planar and circularly polarised, but have a high input impedance and need a balanced feed. Earlier microstrip to parallel strip baluns used a Chebyshev taper [their ref 5] and a Hecken taper [their ref 6]; the paper says those are long and limited in bandwidth. The paper proposes a compact design, simulated and optimised in CST Microwave Studio and tested with a vector network analyser.

**Section II (the balun).**
- Fig. 1: a single microstrip to parallel strip balun. Input 50 Ω (Z0), output 188 Ω (ZL), equal to the parallel strip impedance.
- Both the top strip and the ground are tapered to avoid step discontinuities.
- Design method in the paper: the 50 Ω width w1 from a characteristic impedance equation (Bahl and Trivedi); the **ground width found by a parameter sweep in CST**; repeated until the 188 Ω parallel strip. Positions z along the taper from an exponential taper equation (Kobayashi and Sawada). Example in the text: Z = 110 Ω is at z = 29.8 mm (Fig. 2(a)).
- Fig. 2(a): the impedance profile; Fig. 2(b): a graph of the widths.
- Fig. 3: the tapered line with an SMA connector; equation (1): zi = Σ tk (the position is the sum of the section lengths).
- Fig. 4: two baluns joined back to back at the balanced ends, with two H-field probes at the centre of the parallel strip, on the top and bottom conductors, to check current balance.
- **Table I** (dimensions of structure B; z from the 50 Ω end, w top strip width, w′ bottom conductor width):

| z (mm) | w (mm) | w′ (mm) | impedance (Ω) |
|---:|---:|---:|---:|
| 5 | 4.8 | 18 | 50 |
| 12.7 | 2.6 | 16 | 70 |
| 22.2 | 1.76 | 7 | 90 |
| 29.8 | 1.2 | 2 | 110 |
| 41.5 | 1.1 | 1.8 | 150 |
| 46.2 | 0.92 | 0.98 | 170 |
| 50 | 0.88 | 0.88 | 188 |
| 70 | 0.88 | 0.88 | 188 |

- Fig. 5: phase difference of the two H-field probes, 180° from 1.75 to 15 GHz.
- Common mode check: the paper inserted a long and a short balanced section in the middle of the back-to-back pair; "the S-parameter magnitude results for these both cases show no difference".
- Fig. 6: simulated surface current at 2.5 GHz, symmetric on the parallel strip.
- Substrate: RT/duroid 5880, εr = 2.2, h = 1.5748 mm.
- Fig. 7: two test boards with the same top strip and different ground shapes, structure A and structure B. (a) top view, (b) bottom view (photographs), (c) simulated and measured S-parameters of A, (d) of B. Measured on a Rohde & Schwarz ZVL analyser (300 kHz to 15 GHz). The paper blames differences between measurement and simulation on improper soldering and difficulty aligning the top and bottom conductors.
- Result: structure B was chosen. Back to back it works **from 1.75 to 15 GHz with insertion loss below 3 dB and return loss better than 10 dB**.
- **Table II** (comparison): Chebyshev tapered balun [5] 1 to 4 GHz, 90 × 24 mm²; Hecken tapered balun [6] 0.45 to 2 GHz, 115 × 8.6 mm²; balun A 2 to 14.3 GHz, 70 × 18 mm²; balun B 1.75 to 15 GHz, 70 × 18 mm².

**Section III (spiral antenna).**
- Self-complementary two-arm circular Archimedean spiral: arm spacing s = 0.86 mm, arm width w = 0.86 mm, inner radius r1 = 0.86 mm, outer radius r2 = 28.3 mm, N = 8 turns. Input impedance 188 Ω. Design parameters from Shively and Stutzman [their ref 10].
- Fig. 8: spiral geometry. Fig. 9: the spiral with the balun under it. Overall size 60 mm × 60 mm × 70 mm, or 0.34 λL × 0.34 λL × 0.39 λL, with λL the wavelength at the low frequency **fL = 1.69 GHz**.
- Fig. 10: measured and simulated S11 of the antenna. **The antenna works from 2.5 to 15 GHz** with return loss better than 10 dB.
- Fig. 11: measured and simulated radiation patterns at 10 GHz. Patterns measured with a horn receiver (1 to 18 GHz); the paper notes external reflections affected the measurement.
- **Table III** (HPBW of the spiral):

| f (GHz) | E-plane (°) | H-plane (°) |
|---:|---:|---:|
| 2 | 94.6 | 81.8 |
| 2.5 | 93.5 | 78.5 |
| 3 | 86.4 | 78.3 |
| 4 | 73.3 | 70.2 |
| 5 | 64.9 | 67.1 |
| 6 | 61 | 60.7 |
| 10 | 53.8 | 47.3 |
| 15 | 42.6 | 34.4 |

- The paper says the HPBW decreases as frequency increases, so the gain increases.

**What the paper does not give** (and this project had to fix itself): the loss tangent, the copper thickness, the exact shape of structure A's ground (only visible in the photograph of Fig. 7(b)), how the two baluns are joined in the back-to-back test, and the exact taper between the seven table rows. The board area 70 × 18 mm² comes from Table II.

**The results that had to be validated** (the checklist used by the project):

| item | paper's result | where in paper |
|---|---|---|
| V1 | structure B back to back, \|S11\| < −10 dB from 1.75 to 15 GHz | Fig. 7(d), text, Table II |
| V2 | insertion loss below 3 dB | text |
| V3 | structure A 2 to 14.3 GHz, worse than B | Fig. 7(c), Table II |
| V4 | strip currents 180° apart from 1.75 to 15 GHz | Fig. 5 |
| V5 | long and short balanced section give the same result | text |
| V6 | symmetric surface current at 2.5 GHz | Fig. 6 |
| V7 | Table I dimensions give the stated impedances | Table I, Fig. 2 |
| V8 | spiral antenna matched 2.5 to 15 GHz | Fig. 10 |
| V9 | 10 GHz radiation pattern | Fig. 11 |
| V10 | HPBW in E and H planes | Table III |

---

# Part D. What the project did

## 19. Tools

- **openEMS v0.37**, Windows build, installed at `C:\openEMS` (contains `openEMS.exe`, `nf2ff.exe`, `AppCSXCAD.exe`, and the MATLAB interface in `C:\openEMS\matlab`). The location can be changed with the environment variable `OPENEMS_DIR`.
- **MATLAB R2025b** (no RF toolboxes) writes the openEMS models and reads the port results.
- **Python 3** with numpy, scipy, pandas, matplotlib and h5py: cross-section solver, line model, taper synthesis, field and far-field reading, summary tables, figures.
- Report: pandoc and python-docx. Slides: python-pptx. The `.doc` copy was saved from Word.
- The computer: Windows with WSL (Linux) used for scripting; openEMS ran with 16 threads.
- Why openEMS and not CST, HFSS or ADS: none of those was available to the team; openEMS is a free, published FDTD solver. Its setup was checked on a plain 50 Ω line before the balun runs (Section 20).

How a run works (the flow used throughout):
1. A MATLAB `build_*` script writes `model.xml` (geometry, materials, mesh, ports, probes) into a folder `%TEMP%\balun_sims\<name>` (the Windows temporary folder). The function `sim_dir` empties that folder first.
2. `openEMS.exe model.xml --numThreads=16` is run in that folder (`src/run_sims.sh` does it for many runs).
3. A MATLAB `post_*` script reads the port files and writes a CSV into `results/`.
4. Python scripts make the summary tables and figures.

Practical problems met and how they were solved (good to know if asked "what went wrong"):
- MATLAB R2025b could not read the openEMS probe files with the original reader; `src/ReadUI.m` is a copy of the openEMS function that uses `load -ascii`.
- MATLAB's HDF5 reader cannot open the HDF5 2.x files that openEMS 0.37 writes, so field dumps and far fields are read in Python with h5py.
- Windows ran openEMS in "efficiency mode" when it was started from a terminal without a window, which made it about four times slower; `src/no_throttle.ps1` switches that off for running openEMS processes.
- The microstrip port's source must sit outside the 8-cell absorbing layer at the end of the line; with a coarser mesh the layer is deeper, so the feed position is computed as `max(4, 1.2·8·0.4/k)` mm (k is the mesh refinement factor) and the coarse demo model has a longer port line.

## 20. Values fixed by the project, and checks of the tools

Values the paper does not give, fixed for all runs (`src/balun_params.m`):

| quantity | value | source |
|---|---|---|
| εr, h | 2.2, 1.5748 mm | paper |
| loss tangent | 0.0009 | Rogers data sheet value at 10 GHz |
| copper | 35 µm (1 oz), σ = 5.8 × 10^7 S/m | standard |
| 50 Ω strip | 4.8 mm | paper (Table I) |
| board | 70 mm × 18 mm per balun | Table II area |
| back to back | two baluns joined at z = 70 mm, so 40 mm of parallel strip between the two taper ends in the paper design | project choice |
| ports | microstrip ports on 10 mm of 50 Ω line beyond each board edge, reference plane at the board edge, in place of SMA connectors | project choice |

**Check 1: uniform 50 Ω line** (`src/check_msl.m`). A 40 mm straight 4.8 mm line over an 18 mm ground, with the same ports, mesh rules and materials as the balun models. Result (`results/check_msl.csv`): line impedance 50.9 Ω to 53.2 Ω across the band, |S11| below −31.7 dB from 1 to 15 GHz. Meaning: the port, mesh and material setup does not itself create reflections.

**Check 2: cross-section solver against closed-form formulas** (`results/solver_check.csv`, report Table 4). Microstrips computed on a very wide ground (150 mm ground, 300 mm board) to compare with the infinite-ground formula; the parallel strip compared with 2 × microstrip at h/2:

| line | Z0 solver (Ω) | Z0 closed form (Ω) | εeff solver | εeff closed form |
|---|---:|---:|---:|---:|
| microstrip, w = 4.8 mm | 50.11 | 50.42 | 1.883 | 1.880 |
| microstrip, w = 2.6 mm | 72.84 | 73.45 | 1.818 | 1.816 |
| microstrip, w = 1.2 mm | 106.19 | 107.33 | 1.757 | 1.753 |
| parallel strip, w = 0.88 mm | 178.08 | 180.19 | 1.784 | 1.781 |

Agreement within 1.2 %.

## 21. Checking Table I of the paper

Each row of Table I was put through the cross-section solver (`src/check_table1.py`, `results/table1_check.csv`, report Table 5):

| z (mm) | w (mm) | w′ (mm) | stated (Ω) | computed (Ω) | difference |
|---:|---:|---:|---:|---:|---:|
| 5 | 4.8 | 18 | 50 | 50.6 | +1.2 % |
| 12.7 | 2.6 | 16 | 70 | 73.4 | +4.9 % |
| 22.2 | 1.76 | 7 | 90 | 92.3 | +2.5 % |
| 29.8 | 1.2 | 2 | 110 | 132.5 | +20.5 % |
| 41.5 | 1.1 | 1.8 | 150 | 139.9 | −6.7 % |
| 46.2 | 0.92 | 0.98 | 170 | 171.4 | +0.8 % |
| 50 and 70 | 0.88 | 0.88 | 188 | 178.1 | −5.3 % |

Findings:
1. The **stated impedances** follow the exponential law Z(z) = 50 (188/50)^(z/50) Ω exactly: it gives 70.0 Ω at 12.7 mm, 90.0 at 22.2, 110.1 at 29.8, 150.1 at 41.5, 170.0 at 46.2 and 188.0 at 50 mm. (At z = 5 mm the law gives 57.1 Ω, while the line there is 50 Ω, so the paper's profile has a small step at the feed.)
2. Four rows are within 5 % of the stated value.
3. Two rows are **inconsistent**: at z = 29.8 mm the printed widths give 132.5 Ω instead of 110 Ω (with a 1.2 mm top strip, 110 Ω needs a bottom conductor of about 6.3 mm, not 2 mm; a misprint of 6 as 2 is one possible explanation, but this is a guess and not confirmed), and at z = 41.5 mm they give 139.9 Ω instead of 150 Ω.
4. The **0.88 mm parallel strip is 178 Ω, not 188 Ω**. 188 Ω needs 0.786 mm.

Decision: build the "paper design" to the impedances the table **states**, not to the two inconsistent printed widths. The widths as printed were also simulated, to show what they do (Section 25).

## 22. The structures that were built

All outlines are CSV files in `geometry/` with columns z (mm from the 50 Ω end), w (top strip width), w′ (bottom conductor width), for one balun. Widths between rows are joined by straight lines.

| name | what it is | how it was made |
|---|---|---|
| `paper_B` | Table I exactly as printed, plus a row at z = 0 | `make_geometry.py` |
| `paper_B_stated` | **the "paper design"** used everywhere: structure B built to the stated impedances | `design_improved.py` |
| `paper_A_stated` | structure A: same top strip as `paper_B_stated`, ground narrowing linearly from 18 mm (at z = 5) to the strip width (at z = 50 mm), as seen in the photograph of Fig. 7(b) | `design_improved.py` |
| `paper_B_stated_short` | the paper design with 2 mm of parallel strip per balun, so 4 mm between the two tapers instead of 40 mm | `make_geometry.py` (`short_middle`) |
| `improved` | the improved design (Section 28) | `design_improved.py` |
| `step_exp60` | exponential profile over 60 mm (only the length changed) | `change_steps.py` |
| `step_klop45` | Klopfenstein profile over 45 mm (only the shape changed) | `change_steps.py` |

How the **paper design** (`paper_B_stated`) was built:
- 0 to 5 mm: 50 Ω microstrip, 4.8 mm strip over an 18 mm ground.
- 5 to 50 mm: 91 points where Z(z) = 50 (188/50)^(z/50). At each point the width ratio w′/w = 1 + 2.75 (1 − u)², with u = (z − 5)/45 going from 0 to 1, so the ground is 3.75 times the strip at the feed (18/4.8) and equal to it at the end. The top width w is then solved so that the cross-section has exactly Z(z).
- 50 to 70 mm: 20 mm of 188 Ω parallel strip, 0.786 mm wide.
- The widths come from a precomputed table of the cross-section solver (Section 28, `src/ztable.py`), interpolated.

So the paper design has the paper's impedance profile, the paper's length and the paper's board, with widths computed every 0.5 mm instead of joining seven points.

## 23. The openEMS balun model in detail (`src/build_balun.m`)

Coordinates: x runs along the balun. One balun goes from x = −70 mm (50 Ω end) to x = 0 (balanced end). In back-to-back mode the second balun is the mirror image from x = 0 to x = +70 mm.

- **Conductors**: the top strip is a polygon at z = h (top face), the bottom conductor a polygon at z = 0. Both are conducting sheets of copper (σ = 5.8 × 10^7 S/m, 35 µm). A lossless option (PEC, no dielectric loss) exists but was used only for diagnosis.
- **Substrate**: a box of εr = 2.2 with dielectric loss as a conductivity κ = 2π · 10 GHz · ε0 · εr · tan δ, from the left port end to the right port end, 18 mm wide (y from −9 to +9 mm), h thick.
- **Port lines**: 10 mm of 50 Ω microstrip (4.8 mm strip over the 18 mm ground) is added outside each end of the board (`ext` = 10 mm), so the model runs from x = −80 to +80 mm.
- **Ports**: microstrip ports (`AddMSLPort`) on those extensions. Port 1 is excited, with the source 4 mm into the line (`FeedShift`); the reference plane is moved to the board edge (`MeasPlaneShift` = 10 mm). Port 2 is the same at the other end (back to back). For a **single balun** (`mode = 'single'`), port 2 is a 188 Ω lumped port across the substrate at the balanced end, between the ends of the two strips. A variant drives the lumped port instead (`excite = 2`, run names ending `_p2`) to get the reflection seen from the balanced end.
- **Air and boundaries**: 20 mm of air above and below the board and beyond its sides; in x the grid ends at the ends of the port lines, where the lines run into the absorbing layer. 8-cell PML on all six faces.
- **Excitation**: Gaussian pulse with centre 8.25 GHz and half-width 7.75 GHz (`SetGaussExcite(FDTD, 8.25e9, 7.75e9)`), covering 0.5 to 16 GHz.
- **Stopping rule**: energy 50 dB below peak (`EndCriteria 1e-5`), at most 300 000 time steps.
- **Mesh** (`src/mesh_axis.m` places lines so that the cell size never exceeds a local limit, growing by at most 1.3 from cell to cell):
  - y (across): 0.08 mm within 1.4 mm of the centre line, 0.15 mm within 2.6 mm, 0.3 mm over the width of the ground, at most 2.0 mm in the air; fixed lines at the edges of the uniform sections (50 Ω strip, 18 mm ground, parallel strip) and the board edges.
  - x (along): 0.4 mm. For a single balun, 0.1 mm within 1 mm of the lumped port.
  - z (through): six cells through the substrate (h/6 ≈ 0.26 mm), at most 1.5 mm in the air.
  - The tapered edges are not on fixed lines; they are resolved by the fine grid near the centre line.
  - Result for the improved design back to back: 583 × 129 × 41 lines = **3.08 million cells**, smallest cell 0.079 mm. The paper design back to back has 2.84 million. Report: 1.8 to 3.1 million cells, 3 to 10 minutes per run on 16 threads.
- **Refinement option**: `refine = k` divides every cell size by k. k = 1.5 is the fine mesh check (6.73 million cells). k = 0.6 is the coarse demo copy (0.67 to 0.71 million cells).
- **Probes**: two current probes, boxes around the top strip and around the bottom strip, in the middle of the balanced section (x = 0 back to back; x = −5 mm for a single balun). They give Itop and Ibot.
- **Field dumps**: the magnetic field one cell above the top conductor and one cell below the bottom conductor, at 2.5 GHz (and also at 10 GHz for the improved design). The surface current on a conductor follows the tangential H just outside it, so these maps show the surface current.
- **Movie option** (`movie = true`, used only for the demo run `movie_improved`): Ez against time in the middle of the substrate (every second cell in x and y), and E at 5 GHz in three cross-sections at z = 2.5, 35 and 67.5 mm from the 50 Ω end.

## 24. From a finished run to numbers

`src/post_balun.m` (MATLAB):
- `calcPort` turns the port voltage and current probes into incident and reflected waves, referred to 50 Ω (and 188 Ω for the lumped port), at 621 frequencies from 0.5 to 16 GHz.
- S11 = reflected/incident at port 1; S21 = wave out of port 2 / wave into port 1, with the √Z factors when the reference impedances differ.
- The strip currents at the same frequencies from the current probes (`ReadUI`).
- Written to `results/<run>.csv`: f_GHz, s11_re, s11_im, s21_re, s21_im, itop_re, itop_im, ibot_re, ibot_im.

`src/summarize.py` (Python) makes `results/summary.csv`, the source of every balun number in the report. Definitions:
- **lo_GHz** (band edge): the lowest frequency above which |S11| stays below −10 dB all the way to 15 GHz (interpolated at the −10 dB crossing). This is the "matched from" number.
- **worst_S11**: the largest |S11| between the edge and 15 GHz, or (columns ending `_p`) between 1.75 and 15 GHz, the band the paper claims.
- **S21_min**: the smallest |S21| over the same range.
- **dphi_max**: the largest departure of the strip current phase difference from 180°.
- **damp_max**: the largest amplitude imbalance |Itop/Ibot| in dB.
- **cmrr_min**: the smallest differential to common mode ratio, 20 log10 |(Itop − Ibot)/(Itop + Ibot)|.
- **loss_max**: the largest value of 1 − |S11|² − |S21|².
- **ok_p**: the fraction of 1.75 to 15 GHz where |S11| < −10 dB.

The full `results/summary.csv`:

| run | lo_GHz | worst_S11_p | S21_min_p | dphi_max_p | damp_max_p | cmrr_min_p | ok_p | loss_max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| b2b_paper_B (as printed) | 7.13 | −6.7 | −1.9 | 14.44 | 1.73 | 17.3 | 0.906 | 0.094 |
| b2b_paper_B_stated (paper design) | 1.78 | −9.6 | −0.98 | 8.8 | 1.34 | 21.8 | 0.996 | 0.129 |
| b2b_paper_A_stated (structure A) | 5.81 | −6.9 | −1.8 | 11.36 | 1.89 | 17.8 | 0.927 | 0.114 |
| b2b_paper_B_stated_short | 1.56 | −10.9 | −0.78 | 9.13 | 1.4 | 20.4 | 1.0 | 0.11 |
| b2b_improved | 1.17 | −13.9 | −0.7 | 7.17 | 1.04 | 23.5 | 1.0 | 0.115 |
| single_paper_B_stated | 1.15 | −16.2 | −0.41 | 10.65 | 1.8 | 19.7 | 1.0 | 0.097 |
| single_improved | 0.95 | −18.0 | −0.32 | 8.01 | 1.52 | 21.1 | 1.0 | 0.066 |

(For single baluns S21 is the wave delivered into the 188 Ω port, so it is referred to 188 Ω. The edge "7.13" for the as-printed structure means its last failing frequency below 15 GHz is 7.13 GHz, because of the two extra peaks.)

## 25. Validation results, item by item

**V1 and V2: structure B back to back (paper design).**
- |S11| below −10 dB from **1.78 GHz to 15 GHz**, against 1.75 to 15 GHz in the paper. The curve follows the shape of the paper's CST curve.
- Worst |S11| inside 1.75 to 15 GHz: −9.6 dB, right at 1.75 GHz (the bottom edge). Above 2 GHz the highest ripple peak is −11.0 dB, at 3.15 GHz. Just below the edge there is a ripple peak of −8.84 dB at 1.625 GHz.
- |S21| never below **−0.98 dB** from 1.75 to 15 GHz, well inside the paper's 3 dB.
- Mesh check: with every cell 1.5 times smaller (6.7 million cells) the band starts at 1.77 GHz, |S21| changes by at most 0.12 dB and the phase error by 0.15°. A coarse copy (0.67 million cells) gives 1.78 GHz. So the mesh is fine enough.
- Figure: report Figure "Structure B back to back" (`results/figures/fig_b2b_paper_B.png`): our curve, the as-printed curve, and the paper's CST and measured curves digitised from Fig. 7(d).

**Table I as printed (part of V7).** With the widths exactly as printed, two extra peaks appear: −6.7 dB at 5.42 to 6.10 GHz and −9.0 dB at 6.78 to 7.13 GHz; only 90.6 % of 1.75 to 15 GHz is matched. The transmission-line model built from the same cross-sections predicts both peaks (`fig_linemodel.png`). Reason: the impedance rises quickly near z = 30 mm and near z = 45 mm, and these two rises, 18 mm apart, reflect in phase near c / (2 × 18 mm × √1.8) ≈ 6.2 GHz. The paper's own curves do not show these peaks, which supports the reading that the table has errors and the paper's real board followed the stated impedances.

**V3: structure A.** Same top strip, ground narrowing linearly. |S11| rises to −6.9 dB between 2.88 and 3.55 GHz and to −9.6 dB between 5.55 and 5.80 GHz. It meets −10 dB on 92.7 % of 1.75 to 15 GHz, against 99.6 % for structure B. So B is better, as in the paper, and A's first peak is at the frequency of the first peak in the paper's Fig. 7(c) (near 3.3 GHz). The paper quotes A as 2 to 14.3 GHz; ours is not matched over a single continuous band, so the agreement is in the ranking and in the peak position, not in the exact band. Structure A's ground shape is our reading of the photograph.

**V4: current balance.** From 1.75 to 15 GHz the strip currents stay within **8.8° of 180°** and within 1.34 dB of each other; the common mode current is at least **21.8 dB** below the differential current. The paper's Fig. 5 shows 180°.

**V6: surface current at 2.5 GHz.** The H-field maps above the top conductor and below the bottom conductor are symmetric about the centre line, as in Fig. 6 of the paper. On the wide ground the current flows under the strip; as the ground narrows it moves to the edges, until both faces carry the same distribution (`fig_fields_b2b_paper_B.png`).

**V5: length of the balanced section.** The paper design was simulated with 40 mm and with 4 mm of parallel strip between the two baluns. Both are matched across the band: from 1.78 GHz and from 1.56 GHz to 15 GHz. |S21| differs by at most 0.69 dB; the power balance |S11|² + |S21|² agrees within 0.43 dB; above 10 GHz the long version is 0.11 dB lower on average, which is the loss of the extra 36 mm of line. A longer balanced section adds no radiation of its own, as the paper reports (`fig_long_short.png`).

## 26. Spiral antenna model and results (V8, V9, V10)

**Model** (`src/build_spiral.m`, `src/build_antennas.m`):
- Spiral: two arms of 8 turns, arm width = gap = inner radius = 0.86 mm. Each arm runs from radius r1 + aφ to r1 + aφ + r1 with a = 4 r1 / (2π), so the radius grows by four arm widths per turn (arm, gap, other arm, gap); the second arm is the first turned by 180°. Copper conducting sheet on a 60 mm × 60 mm RT/duroid 5880 board. (With these formulas the inner edge of each arm ends at about 28.4 mm radius and the outer edge at about 29.2 mm; the paper gives r2 = 28.3 mm.)
- Balun board under the spiral, as in Fig. 9 of the paper: the 70 × 18 mm balun board stands vertically under the centre of the spiral board; its two strips continue up through the spiral board and short tabs on the top face join them to the inner ends of the two arms.
- Feed: a **50 Ω lumped port across the bottom edge** of the balun board (so the whole antenna fits inside the far-field box).
- Mesh graded towards the centre: 0.1 mm within 1.5 mm of the axis, 0.15 mm within 6 mm, 0.2 mm within 12 mm, 0.3 mm beyond; 40 mm of air on every side; about 20 million cells; 1.7 hours per run; energy fell 40 dB (`EndCriteria 1e-4`).
- Excitation: a sine-modulated Gaussian pulse from 1 to 16 GHz that has no DC content. The plain Gaussian has a little DC; with the balun feed that left a static charge in the structure that decayed very slowly, so the DC-free pulse was used.
- Far field: a near-field box 11 cells in from the outer boundary (so 3 cells clear of the 8-cell absorbing layer), recorded at 2, 2.5, 3, 4, 5, 6, 10 and 15 GHz; transformed with openEMS's `nf2ff.exe`, read with `src/far_field.py`.
- Three antenna runs: `spiral_lumped` (spiral alone, 188 Ω lumped port across the arm ends), `spiral_full` (with the paper design under it), `spiral_full_improved` (with the improved balun).

**Input match (V8).**
- Spiral alone: matched from **1.65 GHz**, close to the paper's fL = 1.69 GHz.
- With the paper design: |S11| < −10 dB from **1.75 GHz to 15 GHz, except 13.65 to 13.90 GHz where it reaches −9.4 dB**. 97.6 % of 2.5 to 15 GHz is matched. The paper measured 2.5 to 15 GHz. From 2 to 5 GHz our curve follows the paper's measured curve, including its deep minimum near 3.5 GHz.
- Why the bump at 13.8 GHz: above 10 GHz |S11| ripples with a period of about 1.5 GHz, which matches a round trip between the port and the spiral junction along the 70 mm balun; one ripple peak just touches −10 dB. The paper's measured curve also ripples there.
- With the improved balun: matched from **1.61 GHz to 15 GHz with no break**, worst −10.2 dB in 2.5 to 15 GHz.

**Patterns and beamwidth (V9, V10).**
- The spiral radiates on both sides of its board. Up to 10 GHz the lobes towards the front (away from the balun) and back (towards the balun) are within 1.2 dB of each other, as in Fig. 11 of the paper.
- Beamwidth was computed the way CST reports it: the width of the strongest lobe of each full cut, 3 dB below its peak. Table III must be simulated (CST) values, because the measured pattern in Fig. 11 has points only every 30°.

| f (GHz) | paper E | ours E | paper H | ours H | strongest lobe |
|---:|---:|---:|---:|---:|---|
| 2 | 94.6° | 97.3° | 81.8° | 93.8° | front |
| 2.5 | 93.5° | 94.4° | 78.5° | 95.2° | front |
| 3 | 86.4° | 85.8° | 78.3° | 81.9° | back |
| 4 | 73.3° | 73.3° | 70.2° | 76.1° | back |
| 5 | 64.9° | 62.2° | 67.1° | 64.9° | back |
| 6 | 61.0° | 57.3° | 60.7° | 59.2° | back |
| 10 | 53.8° | 64.5° | 47.3° | 76.3° | back |
| 15 | 42.6° | 24.2° | 34.4° | 22.5° | back |

- From 2 to 6 GHz the E-plane is within **3.7°** of Table III. From 3 to 6 GHz the H-plane is within **6°**. At 2 and 2.5 GHz our H-plane is 12° and 17° wider.
- **10 GHz**: the paper's simulated pattern of Fig. 11 was digitised (`src/digitize_paper.py`, `data/paper/fig11_pattern_10GHz.csv`): its front lobe is 66.8° wide and its back lobe 82.6°. Our yz cut follows it within **2.4 dB rms** (2.36), with a front lobe of **66.9°** and a back lobe of 76.3°, and like Fig. 11 it drops by more than 10 dB near the plane of the spiral. Table III gives 53.8° and 47.3° at 10 GHz, narrower than either lobe of the paper's own Fig. 11, so the 10 GHz row of Table III does not describe the pattern in Fig. 11. (Our xz cut against Fig. 11: front 52.1°, back 64.5°, 3.74 dB rms.)
- **15 GHz**: our strongest lobe points along the balun and is 24° wide, against 42.6° and 34.4° in Table III. The paper shows no 15 GHz pattern, so this difference is **not resolved**.
- Peak directivity with the paper design: 3.51 dBi at 2 GHz, 3.77 at 2.5, 4.45 at 3, 5.30 at 4, 5.83 at 5, 6.40 at 6, 6.64 at 10, 9.04 at 15 GHz. The beam narrows as frequency rises, as the paper says.
- With the improved balun the beamwidths differ by at most 2° up to 10 GHz.

## 27. Validation summary (report Table 7)

| result in the paper | value in the paper | this project | status |
|---|---|---|---|
| structure B back to back, \|S11\| < −10 dB | 1.75 to 15 GHz | 1.78 to 15 GHz | reproduced (0.03 GHz higher edge) |
| insertion loss back to back | below 3 dB | below 0.98 dB | reproduced |
| structure A | 2 to 14.3 GHz, worse than B | 92.7 % of band against 99.6 % for B; first peak near 3.3 GHz as in the paper | ranking and peak reproduced, exact band not |
| strip current phase | 180° | 180° ± 8.8°, common mode 21.8 dB down | reproduced |
| surface current at 2.5 GHz | symmetric | symmetric | reproduced |
| longer balanced section | no change | matched in both, power balance within 0.5 dB | reproduced |
| spiral antenna \|S11\| < −10 dB | 2.5 to 15 GHz, measured | 1.75 to 15 GHz, except −9.4 dB at 13.65 to 13.90 GHz | mostly reproduced, one small bump |
| spiral pattern at 10 GHz | Fig. 11 | front lobe 66.9° against 66.8°, 2.4 dB rms | reproduced |
| spiral beamwidths | Table III | E within 3.7° at 2 to 6 GHz; H within 6° at 3 to 6 GHz | reproduced up to 6 GHz; 10 GHz row inconsistent with Fig. 11; 15 GHz unresolved; H 12° to 17° wider at 2 to 2.5 GHz |
| Table I impedances | as stated | two rows inconsistent, 0.88 mm strip is 178 Ω | error found in the paper; corrected design used |

The "status" column is this guide's plain reading of the numbers, for teaching; the report itself shows the same numbers without such labels.

## 28. The improvement: design

**Aim.** The paper design starts at 1.78 GHz back to back (1.15 GHz as a single balun), so it misses most of the L band (1 to 2 GHz). Goal: cover 1 GHz to 15 GHz with the same substrate, the same 70 mm × 18 mm board per balun, the same 5 mm feed line and a 188 Ω balanced output. Since the board size is fixed, the only freedom is how the 70 mm are used.

**The ideas.**
1. **Longer taper.** A taper's lower edge scales roughly as 1/L (the band starts at a fixed value of βL). The paper spends 45 mm on the taper and 20 mm on parallel strip that does nothing for matching. The improved design uses 60 mm for the taper and keeps 5 mm of parallel strip: 5 mm feed + 60 mm taper + 5 mm parallel strip = 70 mm.
2. **Klopfenstein profile instead of exponential.** For a given length and ripple it has the lowest cutoff of any taper.
3. **Ripple Γm = 0.12**, so A = 2.393.
4. **Every cross-section solved for its impedance**, as for the paper design, which also removes the paper's table errors, and a **0.786 mm (188 Ω) parallel strip** instead of 0.88 mm (178 Ω).

**How the outline was synthesised** (`src/design_improved.py`, `src/ztable.py`):
1. The cross-section solver was tabulated over 26 top widths (0.4 to 6 mm, log spaced) × 30 bottom widths (0.4 to 24 mm, log spaced) = **780 combinations** (`results/ztable.npz`, about 25 minutes to build). Z and εeff are interpolated in this table (cubic, in log of the widths).
2. The Klopfenstein profile Z(u) from 50 Ω to 188 Ω with Γm = 0.12 is computed at 121 points, u = 0 to 1 (`klopfenstein()` in `src/taper.py`, numerical integral of the Bessel function expression).
3. The ground to strip width ratio at each point is r(u) = w′/w = 1 + 2.75 (1 − u)^p with p = 2: 3.75 at the feed, 1 at the end.
4. At each point the top width w is solved (root finding, `brentq`) so that the cross-section with w′ = r·w has the profile impedance.
5. Positions z = 5 mm + u × 60 mm. The Klopfenstein steps at the two ends are drawn as 0.05 mm long transitions (from the 50.6 Ω line to 56.4 Ω at z = 5 mm, and from 166.7 Ω to the 188 Ω strip at z = 65 mm).
6. The outline has 125 points (`geometry/improved.csv`; profile with Z and εeff in `results/profile_improved.csv`).

**How 60 mm and Γm = 0.12 were chosen.** With the transmission-line model, a sweep over taper length Lt = 45, 55, 60 mm, Γm = 0.08, 0.10, 0.12, 0.15 and ratio exponent p = 1.5, 2, 3 (36 designs, `results/improved_sweep.csv`). Results for p = 2 (report Table 8 shows a selection):

| Lt (mm) | Γm | A | back to back from | one balun into 188 Ω from |
|---:|---:|---:|---:|---:|
| 45 | 0.08 | 2.803 | 2.00 GHz | 1.55 GHz |
| 45 | 0.10 | 2.578 | 1.85 GHz | 1.45 GHz |
| 45 | 0.12 | 2.393 | 1.25 GHz | 1.40 GHz |
| 45 | 0.15 | 2.165 | 1.20 GHz | 1.35 GHz |
| 55 | 0.08 | 2.803 | 1.30 GHz | 1.25 GHz |
| 55 | 0.10 | 2.578 | 1.30 GHz | 1.20 GHz |
| 55 | 0.12 | 2.393 | 1.25 GHz | 1.15 GHz |
| 55 | 0.15 | 2.165 | 1.25 GHz | 1.10 GHz |
| 60 | 0.08 | 2.803 | 1.30 GHz | 1.15 GHz |
| 60 | 0.10 | 2.578 | 1.30 GHz | 1.10 GHz |
| **60** | **0.12** | **2.393** | **1.25 GHz** | **1.05 GHz** |
| 60 | 0.15 | 2.165 | 1.20 GHz | 1.00 GHz |

Reading the sweep:
- Longer is always better for the single balun (1.40 → 1.15 → 1.05 GHz at Γm = 0.12). 60 mm is the most the 70 mm board allows with a 5 mm feed and 5 mm of strip.
- Larger Γm lowers the edge but raises the in-band reflection. Back to back the two reflections can add to 2Γm: with Γm = 0.12 the worst case is −12.4 dB, which leaves margin under −10 dB; with 0.15 it is −10.5 dB, almost no margin, and the single-balun edge moves only 0.05 GHz (1.05 → 1.00 GHz). So 0.12 was chosen.
- The exponent p (how the width ratio falls) made almost no difference (the edges are identical for p = 1.5, 2, 3), because the impedance is solved to the target at every point anyway; p = 2 was kept.
- The line model is a ranking tool. Its edges (1.25 and 1.05 GHz for the chosen design) are a bit higher than openEMS gives (1.17 and 0.95 GHz).

**Dimensions of the improved balun** (report Table 9; full outline in `geometry/improved.csv`):

| z (mm) | w (mm) | w′ (mm) | impedance (Ω) |
|---:|---:|---:|---:|
| 0 to 5 | 4.80 | 18.00 | 50.6 |
| 5 | 4.08 | 15.29 | 56.4 |
| 15 | 3.32 | 9.67 | 64.9 |
| 25 | 2.57 | 5.72 | 78.3 |
| 35 | 2.00 | 3.37 | 97.0 |
| 45 | 1.58 | 2.06 | 120.1 |
| 55 | 1.26 | 1.35 | 144.8 |
| 65 | 1.01 | 1.01 | 166.7 |
| 65 to 70 | 0.786 | 0.786 | 188 |

## 29. The improvement: results

Simulated with exactly the same openEMS settings as the paper design, back to back and as a single balun into 188 Ω (report Table 10):

| quantity | paper, reported | paper design (ours) | improved |
|---|---|---|---|
| back to back, \|S11\| < −10 dB from | 1.75 GHz | 1.78 GHz | **1.17 GHz** |
| back to back, worst \|S11\| 1.75 to 15 GHz | | −9.6 dB | −13.9 dB |
| back to back, lowest \|S21\| 1.75 to 15 GHz | above −3 dB | −0.98 dB | −0.70 dB |
| one balun, \|S11\| < −10 dB from | | 1.15 GHz | **0.95 GHz** |
| one balun, worst \|S11\| 1.75 to 15 GHz | | −16.2 dB | −18.0 dB |
| phase error of strip currents | | 8.8° | 7.2° |
| common mode below differential mode | | 21.8 dB | 23.5 dB |
| largest share of power lost | | 12.9 % | 11.5 % |
| spiral antenna \|S11\| < −10 dB | 2.5 to 15 GHz | 1.75 to 15 GHz except 13.65 to 13.90 GHz | 1.61 to 15 GHz |
| spiral antenna, worst \|S11\| 2.5 to 15 GHz | below −10 dB | −9.4 dB | −10.2 dB |
| board per balun | 70 × 18 mm | 70 × 18 mm | 70 × 18 mm |

- Back to back the improved pair is matched from 1.17 to 15 GHz: a bandwidth ratio of 12.8 to 1 (15/1.17), against 8.6 to 1 in the paper (15/1.75).
- One improved balun into 188 Ω is matched from **0.95 GHz**, so it covers the whole L band. This is the claim "covers L, S, C and X bands" in the title.
- The strip currents are better balanced (7.2° and 1.04 dB, common mode 23.5 dB down) and less power is lost.
- Field map at 10 GHz for the improved design: `fig_fields_b2b_improved_10GHz.png`.
- With the improved balun the spiral antenna is matched from 1.61 GHz with no break; the −9.4 dB bump at 13.8 GHz disappears. The low end barely moves (1.75 → 1.61 GHz) because the spiral's own size sets it (the spiral alone starts at 1.65 GHz). A larger spiral could use the balun's lower edge. Beamwidths with the two baluns differ by at most 2° up to 10 GHz.

## 30. One change at a time (answers "what did each change do")

To separate the two main changes, two extra designs were simulated in openEMS with the same settings: only the length changed (`step_exp60`: exponential over 60 mm) and only the shape changed (`step_klop45`: Klopfenstein over 45 mm). Both use the same width ratio rule, 5 mm feed and 0.786 mm strip. Numbers recomputed from `results/b2b_*.csv` and `results/single_*.csv`:

| design | one balun, matched from | one balun, worst 1.75 to 15 GHz | back to back, matched from | back to back, worst 1.75 to 15 GHz |
|---|---:|---:|---:|---:|
| paper: exponential, 45 mm | 1.15 GHz | −16.2 dB | 1.78 GHz | −9.6 dB |
| longer only: exponential, 60 mm | 1.04 GHz | −17.6 dB | 1.24 GHz | −12.7 dB |
| shape only: Klopfenstein, 45 mm | 1.14 GHz | −18.0 dB | 1.15 GHz | −11.0 dB |
| both: Klopfenstein, 60 mm (improved) | **0.95 GHz** | −18.0 dB | 1.17 GHz | **−13.9 dB** |

How to read it:
- **Neither change alone gets the single balun below 1 GHz; together they do.**
- Length moves the edge most (1.15 → 1.04 GHz).
- The Klopfenstein shape alone barely moves the single-balun edge at 45 mm (1.15 → 1.14 GHz), but it lowers the reflection in the band (worst −18.0 dB). On the longer taper it takes the edge the rest of the way, to 0.95 GHz.
- **Why the single-balun edge is the fair measure, not the back-to-back edge.** The back-to-back edge is a threshold effect. The paper design has one ripple peak at −8.84 dB at 1.625 GHz, just above −10 dB, so its edge reads 1.78 GHz. Push that one peak under −10 dB and the edge jumps to about 1.1 GHz, where the curve first goes below −10 dB. That is why "shape only" reads 1.15 GHz back to back, slightly lower than the improved design's 1.17 GHz, although as a single balun it is much worse (1.14 against 0.95 GHz). So "1.78 → 1.17 GHz" back to back overstates the real gain; "1.15 → 0.95 GHz" for one balun is the honest measure.
- **"Longer only" is not purely a length change.** The paper's exponential law gives 57.1 Ω at z = 5 mm, where the line is 50.6 Ω, so the paper design has a small step at the feed. The 60 mm exponential starts at 50 Ω with no step, so that row also includes removing the step.
- **Check of the Klopfenstein formula.** With A = 2.393, L = 60 mm and εeff about 1.85, βL = A at 1.40 GHz. That is where |S11| should come down to the ripple level, 20 log10(0.12) = −18.4 dB. The simulated single improved balun reaches −18.4 dB at 1.32 GHz, about 6 % away. The −10 dB edge (0.95 GHz) is lower than this because the reflection is still rising below the passband and crosses −10 dB first.
- Demo button: "What each change did".

---

# Part E. Demo, files and how to run

## 31. The live demo

**Starting it.** From the project folder: `python3 run_demo.py` in WSL, or `python run_demo.py` in Windows. The script (standard library only):
1. Finds MATLAB (newest `R*/bin/matlab.exe` under Program Files).
2. Checks that openEMS (`openEMS.exe`, `AppCSXCAD.exe`, the `matlab` folder) and 29 files the demo plots are present, and prints "Checked openEMS and 29 files: all present." or a list of what is missing.
3. Starts MATLAB in `src/` running `balun_demo`. A window titled "Wideband balun" with buttons appears in about 15 to 30 seconds.

Alternative: open MATLAB in the `src` folder and type `balun_demo`.

**The buttons** (in window order) and what each shows:

*Simulation*
- **3D model**: both baluns drawn in 3D (paper design on top, improved below) on the 70 × 18 mm board: copper top strip narrowing from 4.8 mm, darker bottom conductor narrowing from 18 mm, labels "50 Ω, unbalanced" and "188 Ω, balanced". Can be rotated with the mouse.
- **Model and mesh in openEMS**: writes the full openEMS model of the improved balun back to back and opens it in openEMS's own viewer, AppCSXCAD (read-only "View Mode"). It shows the real solver geometry and the rectilinear grid: 583 × 129 × 41 lines, x from −80 to 80 mm, y from −29 to 29 mm, z from −20 to 21.57 mm. Use it when asked how the structure was meshed. The first press takes a few seconds.
- **Run simulation: improved (3 min)** and **Run simulation: paper design (3 min)**: build a coarse copy of that design back to back (every cell 1/0.6 times larger, 0.71 million cells for the improved, 0.67 million for the paper design, longer port lines so the source is outside the deeper absorbing layer), run openEMS in a console window titled "openEMS: improved design" that shows the time step, speed and field energy and closes itself when the energy is 50 dB down, then plot |S11| and |S21| of this run over the saved full-mesh run in grey. The title gives the cell count, the run time and both band edges. Measured: improved coarse 1.16 GHz against 1.17 GHz full (solved in 158 s), paper coarse 1.78 GHz against 1.78 GHz (191 s); worst |S11| within about 0.3 dB and |S21| within about 0.2 dB of the full run. Say openly that the live run is the coarse copy.
  - If openEMS is missing or fails, or its window is closed early, the graph of the saved copy of the same coarse run (in `results/live_improved.csv` or `live_paper.csv`) appears instead, with "saved coarse run" in the title.
  - The button worked end to end on 23-11-2026 (run started 23:43, finished about 23:46).
- **Show the last run again**: plots the last finished live run, or the saved coarse run if none is left in the temp folder.
- **Pulse moving through the balun**: Ez in the middle of the substrate of the improved balun back to back, recorded in time (171 frames from 0.07 to 1.36 ns, on a 534 × 151 grid over x −80 to 80 mm, y −9 to 9 mm). A slider and a Play button. The outlines of the top strip (solid) and ground (dashed) are drawn over it. The pulse squeezes into the narrow strip at the centre and spreads out again.
- **E field in the cross-section**: |E| (colour, dB) and its direction (arrows) at 5 GHz in three cross-sections of the improved balun: z = 2.5 mm (microstrip: field from the strip down to the wide ground), z = 35 mm (inside the taper), z = 67.5 mm (parallel strip: field symmetric between two equal strips). This is the mode change a balun performs.

*Validation*
- **Structure B against the paper**: the paper design back to back, our |S11| and |S21| over the paper's CST and measured |S11| digitised from Fig. 7(d). Title gives the band edge.
- **Mesh check**: the paper design back to back on three meshes: coarse (0.7 M cells, from 1.78 GHz), normal (2.8 M, from 1.78 GHz), fine (6.7 M, from 1.77 GHz). Left |S11|, right |S21|.
- **Table I as printed**: left, impedance along z: the law of the stated values, the stated values, and the values computed from the printed widths (two rows off); right, back-to-back |S11| of the printed widths against the paper design.
- **Current balance**: phase of Itop/Ibot (near 180°) and amplitude ratio in dB (near 0), paper design and improved, 1 to 15 GHz.
- **Spiral antenna, S11**: the spiral with the paper design and with the improved balun under it, with the paper's CST and measured curves from Fig. 10.
- **Spiral antenna, pattern**: polar plot of the normalised far field in the xz (E) and yz (H) planes, with a frequency menu (2, 2.5, 3, 4, 5, 6, 10, 15 GHz). At 10 GHz the paper's Fig. 11 CST curve is drawn too.

*Improvement*
- **Impedance along the taper**: impedance against position for the paper design (exponential) and the improved design (Klopfenstein), and the conductor widths on a log scale.
- **What each change did**: the four designs of Section 30, back to back and single, zoomed on 0.6 to 4 GHz.
- **Paper design against improved**: |S11| of both designs, back to back and single, with the L band shaded.

**Suggested order** (about 10 minutes): 3D model, Model and mesh in openEMS, press Run simulation: improved and keep talking while it runs, Pulse moving through the balun, E field in the cross-section, then the validation buttons, then the improvement buttons.

**Demo files.** `run_demo.py`; `src/balun_demo.m` (all views); `src/build_demo.m` (writes the coarse live models, the two one-change models and the movie model); `src/change_steps.py` (writes the two one-change outlines); `src/export_movie.py` (turns the time recording into `results/movie_improved.mat`); `results/run_info.csv` (cell counts and run times shown in titles).

## 32. Repository, scripts and how to run everything

**Layout of `wideband-balun/`:**

```
run_demo.py   opens the demo in MATLAB
src/          openEMS models (MATLAB), cross-section solver, line model, synthesis, figures (Python)
geometry/     outline of every simulated structure: z, top width, bottom width (mm)
data/paper/   curves digitised from the paper: Fig. 7(c), 7(d), 10, and the 10 GHz pattern of Fig. 11
results/      S-parameters, strip currents, field maps, summary.csv, figures/
report/       report source (report.md) and build script
slides/       presentation build script and the built deck
```

**Scripts in `src/`:**

| script | job |
|---|---|
| `balun_params.m` | substrate, copper, Table I, lengths |
| `build_balun.m` | writes one openEMS balun model (back to back or single) |
| `build_all.m` | writes every balun model of the report |
| `build_spiral.m`, `build_antennas.m` | write the spiral antenna models |
| `build_demo.m` | writes the demo models |
| `mesh_axis.m` | places mesh lines with local size limits and growth ratio 1.3 |
| `add_substrate.m` | substrate box with dielectric loss as conductivity |
| `sim_dir.m`, `setup_paths.m` | run folder in %TEMP%\balun_sims; openEMS MATLAB path |
| `check_msl.m` | uniform 50 Ω line check |
| `post_balun.m`, `post_all.m` | S-parameters and strip currents to results/ |
| `post_spiral.m` | antenna S11 and the input file for nf2ff.exe |
| `ReadUI.m` | copy of openEMS's probe reader that works in MATLAB R2025b |
| `run_sims.sh` | runs openEMS on model folders |
| `no_throttle.ps1` | turns off Windows efficiency mode for openEMS |
| `xsection.py` | quasi-static cross-section solver and the Hammerstad formula |
| `taper.py` | profile along an outline, cascade line model, Klopfenstein profile |
| `ztable.py` | the 780-point table of the solver and interpolation, width solving |
| `make_geometry.py` | Table I outline as printed; short balanced section |
| `check_table1.py` | Table I check, solver check, profile of the printed outline |
| `design_improved.py` | sweep, improved outline, paper design and structure A outlines |
| `change_steps.py` | the two one-change outlines |
| `export_fields.py`, `export_movie.py` | read field dumps (h5py) |
| `far_field.py` | patterns and beamwidths from nf2ff.h5 |
| `digitize_paper.py` | reads curves from page images of the paper |
| `summarize.py` | summary.csv, spiral_numbers.csv, spiral_fig11.csv |
| `plots.py` | all report figures |
| `balun_demo.m` | the demo window |

**Full run order** (from the README):

```
cd src
python3 make_geometry.py          # Table I outline as printed
python3 check_table1.py           # Table I check, solver check, impedance profile
python3 ztable.py                 # cross-section table (about 25 min)
python3 design_improved.py        # paper design, structure A, sweep, improved outline
matlab -batch "build_all"         # writes the openEMS models to %TEMP%\balun_sims
bash run_sims.sh                  # runs openEMS on every model
matlab -batch "post_all"          # S-parameters and strip currents to results/
python3 export_fields.py b2b_paper_B_stated b2b_improved
matlab -batch "build_antennas"    # spiral models
bash run_sims.sh spiral_lumped spiral_full spiral_full_improved
matlab -batch "post_spiral('spiral_full')"     # and the other two
python3 far_field.py spiral_full spiral_full_improved   # after nf2ff.exe nf2ff.xml in each run folder
python3 summarize.py
python3 plots.py
```

Demo runs: `python3 change_steps.py`, `matlab -batch "build_demo"`, run openEMS on those folders, then `post_balun` on the live runs and `python3 export_movie.py movie_improved`.

**Run sizes and times.** Balun models 1.8 to 3.1 million cells, 3 to 10 minutes each on 16 threads. Fine mesh check 6.7 million cells. Antenna models about 20 million cells, 1.7 hours each. Coarse demo copies 0.67 to 0.71 million cells, about 3 minutes.

**GitHub.** Public repository https://github.com/RushilJ2603/wideband-balun, branch `main`. Get it with `git clone https://github.com/RushilJ2603/wideband-balun.git`, or download it as a zip from the GitHub page. To run the demo on another computer it also needs MATLAB, openEMS 0.37 at `C:\openEMS` (or `OPENEMS_DIR` set), and Python 3. Without openEMS the saved-result buttons still work, and the Run buttons fall back to the saved coarse runs.

**The report** (21 pages, `report/report.md`): Abstract; 1 Introduction; 2 Base paper and design specification (Tables 1, 2); 3 Theory (microstrip and parallel strip lines, reflection from a taper, back-to-back measurement); 4 Tools and method (openEMS, Table 3 settings; cross-section solver and line model, Table 4); 5 Validation of the base paper (5.1 impedance of the published cross-sections, Table 5; 5.2 structure B back to back; 5.3 structure A; 5.4 current balance and surface current; 5.5 length of the balanced section; 5.6 spiral antenna, Table 6; 5.7 summary, Table 7); 6 Improved design (aim, design with Tables 8 and 9, results with Table 10); 7 Conclusion; 9 references; appendix of project files. 14 figures and 10 tables.

The 14 figures, in order: impedance and widths of Table I as printed; layout of structures A and B; structure B back to back against the paper; line model of the as-printed widths; structure A back to back; H-field map of structure B at 2.5 GHz; 40 mm against 4 mm balanced section; spiral S11; spiral pattern at 10 GHz; impedance profiles; layout of the paper and improved designs; |S11| comparison of paper and improved designs (back to back and single, L band shaded); current balance; H-field map of the improved design at 10 GHz.

References: [1] the base paper; [2] Pozar, Microwave Engineering, 4th ed.; [3] Klopfenstein 1956; [4] Hammerstad and Jensen 1980; [5] Liebig, openEMS 0.37; [6] Yee 1966; [7] Rogers RT/duroid 5880 data sheet; [8] Mushiake 1992, self-complementary antennas; [9] Bérenger 1994, PML.

**The slides** (13): 1 title; 2 why a wideband balun and why a tapered one, the paper's specification; 3 how it works, taper reflection, back-to-back |S11| ≤ 2|Γ1|; 4 tools (openEMS, the cross-section solver within 1.2 % of Hammerstad, the line model, the 50 Ω line check); 5 Table I check and how the paper design was built; 6 structure B back to back, mesh check, as-printed peaks and their cause; 7 balance, field map, long and short balanced section, structure A; 8 spiral model and S11; 9 pattern and beamwidth; 10 summary table; 11 improved design; 12 results table against the paper design; 13 conclusion.

---

# Part F. Viva preparation

## 33. Limitations and open discrepancies

Each is stated with the honest answer.

1. **Everything is simulation.** No board was made or measured. No SMA connector was modelled: microstrip ports at the board edges replace it. The paper's measured curves include connector and soldering effects that the model does not have. Next step would be fabrication and measurement.
2. **Paper design edge 1.78 GHz against the paper's 1.75 GHz.** A 0.03 GHz difference. The worst |S11| inside the paper's band is −9.6 dB, exactly at 1.75 GHz. The fine mesh gives 1.77 GHz, so this is not a mesh error.
3. **Structure A** is not reproduced as a continuous 2 to 14.3 GHz band; what matches is that B is better and the position of A's first peak. A's ground shape was taken from a photograph.
4. **Spiral antenna with the paper design**: one bump to −9.4 dB at 13.65 to 13.90 GHz (a ripple from the round trip along the balun). The paper's measured curve also ripples there.
5. **H-plane beamwidth at 2 and 2.5 GHz** is 12° and 17° wider than Table III.
6. **10 GHz beamwidth**: our numbers differ from Table III, but match the paper's own Fig. 11 pattern. The claim that Table III's 10 GHz row is inconsistent with Fig. 11 is our interpretation, based on reading the figure.
7. **15 GHz beamwidth**: 24° against 42.6° and 34.4°. Unresolved; the paper shows no 15 GHz pattern.
8. **Back-to-back improvement looks bigger than it is.** 1.78 → 1.17 GHz is inflated by the threshold effect (Section 30). The fair number is the single balun, 1.15 → 0.95 GHz.
9. **Back to back the improved design starts at 1.17 GHz**, so the full L band from 1 GHz is covered only by a single balun (0.95 GHz), which is what feeds an antenna.
10. **The antenna does not reach 1 GHz** with the improved balun (1.61 GHz), because the spiral's size sets its lower limit.
11. **Material data**: loss tangent and copper from the data sheet; dielectric loss is set as a conductivity at 10 GHz, so it is exact only at 10 GHz.
12. **The cross-section solver is quasi-static** (no dispersion), within 1.2 % of the closed-form formulas. The line model ignores radiation; it was only used to rank designs.
13. **"Longer only" in the one-change study** also removes the paper's 50.6 → 57.1 Ω feed step.
14. **The live demo run is a coarse copy** (0.7 million cells instead of 3.1 million). Its band edge agrees with the full run within 0.01 GHz.
15. **The Table I "misprint"** (2 mm possibly meant to be 6 mm) is a guess; only the inconsistency itself is proven.

## 34. What this guide does not know (do not invent answers)

- The questions that will be asked in the presentation.
- How the work was divided between Rushil Jain and Jainam Sonigara; the project files do not record it.
- Why exactly 5 mm of parallel strip was kept at the end of the improved design (rather than more or less). The files only state that it was kept.
- The paper's CST settings (mesh, ports, losses). The paper does not give them.
- Any measured data for this project's designs: none exist.
- What the paper's Table I was meant to say at the two inconsistent rows.
- The paper's 15 GHz pattern.
- The exact date and time of the presentation (planned before 26-11-2026).

## 35. Questions to expect, with short spoken answers

**Basics**

*What is a balun and why does a spiral need one?* It connects an unbalanced line (50 Ω coax or microstrip) to a balanced load whose two terminals carry equal and opposite currents. Without it, current flows back on the outside of the feed, radiates and spoils the pattern. The spiral is balanced and has 188 Ω input impedance, so the balun also transforms 50 Ω to 188 Ω.

*Why 188 Ω?* A self-complementary antenna (metal and gaps the same shape) has input impedance η0/2 ≈ 188 Ω at all frequencies (Mushiake). The spiral with arm width equal to arm spacing is self-complementary.

*How does this balun work?* It starts as a 50 Ω microstrip. Along 45 mm (paper) or 60 mm (improved), the ground narrows until it is as wide as the strip, so the microstrip mode turns into the balanced parallel strip mode and the impedance rises from 50 to 188 Ω.

*Why a tapered balun for 1 to 15 GHz?* A taper has no resonant length. Its lower edge is set by its length; its upper edge only by how precisely it is made. Marchand and transformer baluns cover about an octave.

*What does −10 dB |S11| mean?* 10 % of the power is reflected, 90 % goes in. Return loss 10 dB, VSWR under about 1.9.

*What is a back-to-back measurement and why is it stricter?* Two identical baluns joined at their balanced ends, so a normal two-port analyser can measure them. The two reflections can add, so the pair can reflect up to twice as much as one balun: |S11| ≤ 2|Γ1|.

**Tools**

*Why openEMS and not HFSS or CST?* None was available to us. openEMS is a free, published FDTD solver. We checked our setup on a plain 50 Ω line: line impedance 50.9 to 53.2 Ω, |S11| below −31.7 dB from 1 to 15 GHz.

*What is FDTD?* Maxwell's curl equations on a staggered (Yee) grid, stepped in time. One Gaussian pulse covers 0.5 to 16 GHz; port voltages and currents are recorded and a Fourier transform gives S-parameters over the whole band from one run. The smallest cell limits the time step.

*How did you mesh it?* 0.08 mm across the strips near the centre line, 0.4 mm along the line, six cells through the substrate, cells growing by at most 1.3 times, 20 mm of air and an 8-cell PML. The improved model has 3.08 million cells; smallest cell 0.079 mm. (Show "Model and mesh in openEMS".)

*How do you know the mesh is fine enough?* With every cell 1.5 times smaller (6.7 million cells) the band edge moves from 1.78 to 1.77 GHz and |S21| changes by at most 0.12 dB. A coarse mesh (0.67 million) still gives 1.78 GHz. (Show "Mesh check".)

*What losses are in the model?* 35 µm copper with σ = 5.8 × 10^7 S/m, and the substrate loss tangent 0.0009 as a conductivity at 10 GHz.

*What is your cross-section solver?* A 2D finite-difference Laplace solver written for the project. It finds the capacitance with and without the substrate, so Z0 = 1/(c√(C·Ca)) and εeff = C/Ca. It agrees with Hammerstad-Jensen within 1.2 %.

*What is the line model?* The balun cut into 0.5 mm slices, each a uniform line with the solver's Z and εeff, multiplied as ABCD matrices. It runs in a fraction of a second, so we used it to sweep designs.

**Validation**

*What exactly is "the paper design"?* The paper's impedance law Z = 50 (188/50)^(z/50) from 5 to 50 mm, which is exactly what Table I's stated impedances follow, with widths solved every 0.5 mm with our solver, then 20 mm of 188 Ω parallel strip. Same profile, same length, same board.

*Why not use the widths in Table I directly?* We did, as a separate run. Two rows give the wrong impedance: 132.5 Ω instead of 110 Ω at 29.8 mm, and 139.9 Ω instead of 150 Ω at 41.5 mm. Built as printed, the balun shows two peaks near 5.8 and 6.9 GHz that the paper's own curves do not show, and our line model predicts the same peaks from the impedance profile alone.

*Why 0.786 mm and not 0.88 mm for the parallel strip?* 0.88 mm is 178 Ω by our solver (180 Ω by the closed form). The paper wants 188 Ω, which needs 0.786 mm.

*Did you reproduce the main result?* Yes: back to back below −10 dB from 1.78 to 15 GHz against 1.75 to 15 GHz, |S21| never below −0.98 dB against the paper's 3 dB.

*How did you check the current balance?* Current probes around each strip in the middle of the balanced section. Phase within 8.8° of 180°, amplitude within 1.34 dB, common mode at least 21.8 dB below differential.

*What about the long and short balanced section?* 40 mm and 4 mm both matched; power balance agrees within 0.43 dB; the long one loses 0.11 dB more above 10 GHz, just the extra line loss. So no extra radiation, as the paper says.

*How did you simulate the antenna?* As one model like the paper's Fig. 9: the 60 × 60 mm spiral board, the 70 × 18 mm balun board standing under its centre, strips running up through the spiral board to the arm ends, a 50 Ω lumped port at the bottom edge of the balun. 20 million cells, 0.1 mm at the spiral centre, 40 mm of air, 1.7 hours. Far field with openEMS's nf2ff tool.

*Your antenna is matched from 1.75 GHz but the paper says 2.5 GHz. Why?* The paper's 2.5 GHz is measured; ours is simulated. From 2 to 5 GHz our curve follows the paper's measured curve, including its dip near 3.5 GHz. The spiral alone starts at 1.65 GHz, close to the paper's fL of 1.69 GHz.

*Why the −9.4 dB bump at 13.8 GHz?* A ripple with a period of about 1.5 GHz from the round trip along the 70 mm balun; one peak just touches −10 dB. The paper's measured curve ripples there too.

*Why don't your 10 and 15 GHz beamwidths match Table III?* At 10 GHz we matched the paper's own pattern in Fig. 11 instead: front lobe 66.9° against 66.8°, 2.4 dB rms. Table III's 10 GHz values are narrower than both lobes of that figure, so they don't describe it. At 15 GHz the paper shows no pattern, so that difference is unresolved.

*How did you compute the beamwidth?* Like CST: the width of the strongest lobe of each cut, 3 dB below its peak. The spiral radiates nearly equally to both sides, so the strongest lobe is in front at 2 and 2.5 GHz and on the balun side above that.

**Improvement: what and why**

*What did you change?* Four things: the taper is 60 mm instead of 45 mm (the 20 mm of parallel strip was mostly wasted), the profile is Klopfenstein instead of exponential, the ripple is Γm = 0.12, and every cross-section is solved for its impedance, with a 188 Ω (0.786 mm) parallel strip.

*Why longer?* A taper's lower edge scales as 1/L. The board is fixed at 70 mm, so we moved length from the useless parallel strip into the taper: 5 mm feed, 60 mm taper, 5 mm strip.

*Why Klopfenstein?* For a given length and passband ripple it has the lowest cutoff of any taper. It is the limit of a Chebyshev multi-section transformer with infinitely many sections.

*Why Γm = 0.12 and not 0.15?* Larger Γm lowers the edge but raises the in-band reflection. Back to back two reflections can add to 2Γm: 0.12 gives at worst −12.4 dB, safe margin; 0.15 gives −10.5 dB, almost none, and gains only 0.05 GHz in the line model (1.05 → 1.00 GHz).

*Where does A = 2.393 come from?* Γ0 = ½ ln(188/50) = 0.662, cosh A = Γ0/Γm = 0.662/0.12, so A = 2.393. The passband starts at βL = A.

*Does the formula match the simulation?* βL = A at 1.40 GHz for 60 mm and εeff ≈ 1.85. That is where |S11| should reach −18.4 dB. The simulated single balun reaches −18.4 dB at 1.32 GHz, 6 % away.

*How did you get the widths?* A table of our solver over 780 combinations of top and bottom width; the bottom-to-top ratio falls as 1 + 2.75(1 − u)² from 3.75 to 1; at each of 121 points the top width is solved for the target impedance.

*Which change did what?* Simulated one at a time. Single balun: paper 1.15 GHz, longer only 1.04, shape only 1.14, both 0.95 GHz. Neither alone gets below 1 GHz; together they do. Length moves the edge most; the Klopfenstein shape lowers the reflection and, on the longer taper, takes the edge the rest of the way.

*Why quote the single balun and not back to back?* The back-to-back edge is a threshold. The paper design has one ripple at −8.84 dB at 1.63 GHz; that single peak decides 1.78 GHz. So 1.78 → 1.17 GHz overstates the gain; 1.15 → 0.95 GHz is the fair number.

*Is the whole L band covered?* By one balun, yes, from 0.95 GHz. Back to back, from 1.17 GHz.

*Does the improved balun make the antenna work at 1 GHz?* No. The antenna starts at 1.61 GHz because the spiral's size sets that. What improves is the top end: the −9.4 dB bump at 13.8 GHz goes away. A larger spiral could use the balun's lower edge.

*What else got better?* Worst back-to-back reflection −13.9 dB against −9.6 dB, |S21| −0.70 against −0.98 dB, phase error 7.2° against 8.8°, common mode 23.5 against 21.8 dB down, power lost 11.5 % against 12.9 %.

*What would you do next?* Fabricate both designs and measure them.

## 36. Numbers cheat sheet

- Substrate RT/duroid 5880: εr 2.2, h 1.5748 mm, tan δ 0.0009; copper 35 µm, 5.8 × 10^7 S/m. Board 70 × 18 mm per balun.
- 50 Ω line: 4.8 mm strip over 18 mm ground. Parallel strip: 0.88 mm = 178 Ω, 0.786 mm = 188 Ω.
- Exponential law: Z = 50 (188/50)^(z/50); 57.1 Ω at z = 5 mm.
- Table I bad rows: 29.8 mm gives 132.5 Ω (stated 110); 41.5 mm gives 139.9 Ω (stated 150).
- Solver vs closed form: within 1.2 %. 50 Ω line check: 50.9 to 53.2 Ω, |S11| < −31.7 dB.
- Paper design back to back: 1.78 to 15 GHz; worst −9.6 dB at 1.75 GHz; −8.84 dB peak at 1.625 GHz; |S21| ≥ −0.98 dB; phase 8.8°; amplitude 1.34 dB; common mode 21.8 dB down; lost power up to 12.9 %.
- Mesh: 2.84 M cells (paper design), 3.08 M (improved); fine 6.73 M gives 1.77 GHz; coarse 0.67 M gives 1.78 GHz.
- As printed: peaks −6.7 dB (5.42 to 6.10 GHz) and −9.0 dB (6.78 to 7.13 GHz); 90.6 % of band; two rises 18 mm apart, ≈ 6.2 GHz.
- Structure A: 92.7 % against 99.6 %; peaks −6.9 dB (2.88 to 3.55) and −9.6 dB (5.55 to 5.80).
- Balanced section 40 mm vs 4 mm: edges 1.78 and 1.56 GHz; |S21| within 0.69 dB; power balance within 0.43 dB.
- Klopfenstein: Γ0 0.662, Γm 0.12 (−18.4 dB), A 2.393, 2Γm = −12.4 dB; steps 50 → 56.4 Ω and 166.7 → 188 Ω.
- Improved: 5 mm feed + 60 mm taper + 5 mm strip; 125-point outline; 780-point table; ratio 1 + 2.75(1 − u)².
- Improved back to back: 1.17 to 15 GHz, worst −13.9 dB, |S21| ≥ −0.70 dB, phase 7.2°, amplitude 1.04 dB, common mode 23.5 dB, lost power 11.5 %. Bandwidth ratio 12.8:1 against 8.6:1.
- Single balun: paper design 1.15 GHz (worst −16.2 dB), improved 0.95 GHz (worst −18.0 dB).
- One change at a time (single): 1.15, 1.04 (longer), 1.14 (shape), 0.95 GHz (both).
- βL = A at 1.40 GHz; simulated −18.4 dB at 1.32 GHz.
- Spiral: 8 turns, 0.86 mm arms; alone from 1.65 GHz (paper fL 1.69); with paper design 1.75 to 15 GHz except −9.4 dB at 13.65 to 13.90; with improved 1.61 to 15 GHz, worst −10.2 dB; 20 M cells, 1.7 h.
- Beamwidth: E within 3.7° (2 to 6 GHz), H within 6° (3 to 6 GHz); 10 GHz front lobe 66.9° vs 66.8°, 2.4 dB rms; directivity 3.5 dBi (2 GHz) to 6.6 dBi (10 GHz).
- Demo: coarse run 0.71 M cells, 158 s, edge 1.16 vs 1.17 GHz (improved); 0.67 M, 191 s, 1.78 vs 1.78 GHz (paper).

## 37. Glossary

- **A (Klopfenstein)**: constant with cosh A = Γ0/Γm; the passband starts at βL = A.
- **AppCSXCAD**: openEMS's 3D viewer for model files.
- **Back to back**: two baluns joined at their balanced ends and measured as a two-port.
- **Balanced / unbalanced**: two conductors with equal and opposite currents / one conductor grounded.
- **Band edge (lo_GHz)**: lowest frequency from which |S11| stays below −10 dB up to 15 GHz.
- **β**: phase constant, 2πf√εeff/c.
- **Common mode**: (Itop + Ibot)/2, the unwanted current; differential mode is (Itop − Ibot)/2.
- **Conducting sheet**: openEMS model of thin metal with finite conductivity and thickness.
- **CST Microwave Studio**: the commercial solver the paper used.
- **εeff**: effective permittivity of a printed line, between 1 and εr.
- **EndCriteria**: openEMS stopping rule, energy below a fraction of its peak (1e-5 = −50 dB).
- **FDTD**: finite-difference time-domain method.
- **Γ, Γ0, Γm**: reflection coefficient; ½ ln(ZL/Z0); Klopfenstein passband ripple.
- **HPBW**: half-power (−3 dB) beamwidth.
- **Klopfenstein taper**: optimum taper, lowest passband reflection for its length.
- **Lumped port**: a resistor and source across a gap, used as a port.
- **MSL port**: openEMS microstrip line port with voltage and current probes.
- **NF2FF**: near-field to far-field transformation.
- **Parallel strip line**: two equal strips on opposite faces of the substrate.
- **PML**: perfectly matched layer, absorbing boundary.
- **Quasi-static**: electrostatic approximation of a cross-section, no frequency dependence.
- **S11, S21**: reflection at port 1; transmission from port 1 to port 2.
- **Self-complementary**: metal and slots of identical shape; input impedance η0/2.
- **Structure A / B**: the paper's two test boards; same top strip, different ground shapes; B is the better one and the one used for the paper design.
- **Taper profile**: how the impedance changes along the transition.
- **tan δ**: loss tangent of the substrate.
- **Yee grid**: staggered grid of E and H components used by FDTD.
- **Z0**: characteristic impedance.
