"""Opens the balun simulation demo in MATLAB.

    python run_demo.py

Works from Windows or from WSL and needs only the Python standard library.
Before opening MATLAB it checks that openEMS and every file the demo plots
are in place.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
MATLAB_ROOTS = (Path("/mnt/c/Program Files/MATLAB"), Path("C:/Program Files/MATLAB"))

NEEDED = [
    "src/balun_demo.m",
    "geometry/paper_B_stated.csv", "geometry/improved.csv",
    "geometry/step_exp60.csv", "geometry/step_klop45.csv",
    "results/run_info.csv", "results/live_improved.csv", "results/live_paper.csv",
    "results/b2b_paper_B_stated.csv", "results/b2b_paper_B_stated_fine.csv",
    "results/b2b_improved.csv", "results/b2b_step_exp60.csv", "results/b2b_step_klop45.csv",
    "results/single_paper_B_stated.csv", "results/single_improved.csv",
    "results/single_step_exp60.csv", "results/single_step_klop45.csv",
    "results/profile_paper_B_stated.csv", "results/profile_improved.csv",
    "results/movie_improved.mat", "results/spiral_full.csv", "results/spiral_full_improved.csv",
    "results/spiral_full_patterns.csv",
    "data/paper/fig7d_structure_B.csv", "data/paper/fig10_spiral.csv", "data/paper/fig11_pattern_10GHz.csv",
]


def find_matlab():
    for root in MATLAB_ROOTS:
        found = sorted(root.glob("R*/bin/matlab.exe")) if root.exists() else []
        if found:
            return str(found[-1])
    return shutil.which("matlab.exe") or shutil.which("matlab")


def openems_dir():
    d = os.environ.get("OPENEMS_DIR", "C:/openEMS")
    if Path("/mnt/c").exists() and d[1:2] == ":":
        d = "/mnt/" + d[0].lower() + d[2:].replace("\\", "/")
    return Path(d)


def windows_path(path):
    if str(path).startswith("/mnt/"):
        return subprocess.check_output(["wslpath", "-w", str(path)], text=True).strip()
    return str(path)


def check():
    missing = [f for f in NEEDED if not (ROOT / f).exists()]
    oe = openems_dir()
    for exe, use in (("openEMS.exe", "the Run simulation buttons"), ("AppCSXCAD.exe", "the openEMS viewer")):
        if not (oe / exe).exists():
            missing.append(f"{oe / exe} (needed for {use})")
    if not (oe / "matlab").is_dir():
        missing.append(f"{oe / 'matlab'} (openEMS MATLAB scripts)")
    if missing:
        print("Missing:")
        for m in missing:
            print("  " + m)
    else:
        print(f"Checked openEMS and {len(NEEDED)} files: all present.")
    return not missing


def main():
    matlab = find_matlab()
    if matlab is None:
        sys.exit("MATLAB was not found.")
    if not (SRC / "balun_demo.m").exists():
        sys.exit(f"balun_demo.m was not found in {SRC}")
    if not check():
        print("Opening the demo anyway. Buttons that use the missing files will fail.")
    subprocess.Popen([matlab, "-nosplash", "-sd", windows_path(SRC), "-r", "balun_demo"], cwd=SRC,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Opening MATLAB. The control window appears in about 30 seconds.")


if __name__ == "__main__":
    main()
