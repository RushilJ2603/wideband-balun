# Wideband microstrip to parallel strip balun, 1 to 15 GHz

Course project, EC301 RF Components and Circuits, NITK Surathkal (project 12, "Wideband BALUN circuit for L, S, C and X band applications").
Rushil Jain (241EC148) and Jainam Sonigara (241EC155).

A balun joins an unbalanced 50 Ω line to a balanced load. This project reproduces the tapered microstrip to parallel strip balun of Vinayagamoorthy, Coetzee and Jayalath (IEEE VTC 2012 Spring, doi 10.1109/VETECS.2012.6240118) in the FDTD solver [openEMS](https://www.openems.de), checks each result of the paper, and redesigns the taper so that the balun covers the whole L band on the same 70 mm × 18 mm board. The substrate is RT/duroid 5880 (εr = 2.2, h = 1.5748 mm) and the balun transforms 50 Ω to 188 Ω, the input impedance of a self-complementary spiral antenna.

## Results

Back to back, the paper design and the improved design, both in openEMS with the same settings:

| | paper, reported | paper design | improved |
|---|---|---|---|
| \|S11\| < −10 dB | 1.75 to 15 GHz | 1.77 to 15 GHz | 1.17 to 15 GHz |
| worst \|S11\|, 1.75 to 15 GHz | | −9.7 dB | −13.9 dB |
| lowest \|S21\|, 1.75 to 15 GHz | above −3 dB | −0.98 dB | −0.72 dB |
| strip current phase error | | 11.9° | 8.4° |
| common mode below differential mode | | 19.2 dB | 22.0 dB |

One balun into 188 Ω is matched (|S11| < −10 dB) from 1.15 GHz with the paper design and from 0.95 GHz with the improved taper. The paper's spiral antenna fed through the paper design is below −10 dB from 1.59 GHz to 15 GHz (2.5 to 15 GHz measured in the paper).

![Back to back and single-balun |S11|](results/figures/fig_compare.png)

The paper design follows the impedances stated in Table I of the paper, Z = 50 (188/50)^(z/50) Ω from z = 5 mm to 50 mm, with the widths solved at every 0.5 mm by a quasi-static cross-section solver (`src/xsection.py`). The solver shows that two rows of Table I, at z = 29.8 mm and 41.5 mm, give 132 Ω and 140 Ω instead of the stated 110 Ω and 150 Ω; built exactly as printed, the balun has two extra reflection peaks near 5.8 and 6.9 GHz, which a transmission-line model built from the same solver also predicts.

![Structure B back to back](results/figures/fig_b2b_paper_B.png)

The improved balun uses 60 of its 70 mm for a Klopfenstein taper (ripple 0.12, A = 2.393) and ends in 5 mm of 188 Ω parallel strip (0.786 mm strips). At each of 121 points the top strip width is solved from a table of the cross-section solver so that the line has the profile impedance, with the ground to strip width ratio falling as 1 + 2.75(1 − u)².

![Impedance profiles](results/figures/fig_profiles.png)

## Reproducing

Requirements: openEMS 0.37 (Windows build, in `C:\openEMS` or at `OPENEMS_DIR`), MATLAB, Python 3 with numpy, scipy, pandas, matplotlib, and h5py for the field and far-field files.

```
cd src
python3 make_geometry.py          # Table I outline as printed
python3 check_table1.py           # Table I check, solver check, impedance profile
python3 ztable.py                 # cross-section table for the synthesis (about 25 min)
python3 design_improved.py        # paper design, structure A, taper sweep, improved outline
matlab -batch "build_all"         # writes the openEMS models to %TEMP%\balun_sims
bash run_sims.sh                  # runs openEMS on every model
matlab -batch "post_all"          # S-parameters and strip currents to results/
python3 export_fields.py b2b_paper_B_stated b2b_improved
python3 cascade_spiral.py paper_B_stated improved
python3 summarize.py              # results/summary.csv
python3 plots.py                  # results/figures/
```

The spiral antenna: `build_spiral('spiral_lumped', ..., struct('feed', 'lumped'))` in MATLAB, run openEMS, `post_spiral('spiral_lumped')`, run `nf2ff.exe nf2ff.xml` in the run folder, then `python3 far_field.py spiral_lumped`. `cascade_spiral.py` joins it to the two-port of each balun.

Windows runs processes started from a terminal without a window in efficiency mode, which slowed openEMS by a factor of four here; `src/no_throttle.ps1` turns that off for running openEMS processes.

A uniform 50 Ω line with the same port and mesh settings (`check_msl.m`) gives a line impedance of 50.9 to 53.2 Ω and |S11| below −31.7 dB from 1 to 15 GHz.

MATLAB R2025b reads the openEMS probe files only with `load -ascii`, so `src/ReadUI.m` is a copy of the openEMS function with that change. MATLAB's HDF5 reader cannot open the HDF5 2.x files that openEMS 0.37 writes, so field dumps and far fields are read in Python.

## Layout

```
src/        openEMS models (MATLAB), cross-section solver, line model, synthesis, figures (Python)
geometry/   outline of every simulated structure: z, top width, bottom width (mm)
data/paper/ S11 curves digitised from Figs. 7 and 10 of the paper
results/    S-parameters, strip currents, field maps, summary.csv, figures/
report/     report source (Markdown) and build script
slides/     presentation build script
```
