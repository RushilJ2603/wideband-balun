#!/usr/bin/env bash
# Runs openEMS on model folders written by build_all.m / build_spiral.m.
# Usage: run_sims.sh [name ...]     (default: every folder that has no results yet)
# Set OPENEMS_EXE to override the solver location and THREADS the thread count.

set -u
EXE="${OPENEMS_EXE:-/mnt/c/openEMS/openEMS.exe}"
THREADS="${THREADS:-16}"
SIMS="$(wslpath "$(cmd.exe /c echo %TEMP% 2>/dev/null | tr -d '\r')")/balun_sims"

if [ $# -gt 0 ]; then
    names=("$@")
else
    names=()
    for d in "$SIMS"/*/; do
        n="$(basename "$d")"
        [ -f "$d/model.xml" ] && [ ! -f "$d/run.log" ] && names+=("$n")
    done
fi

for n in "${names[@]}"; do
    echo "== $n  ($(date +%H:%M:%S))"
    start=$(date +%s)
    (cd "$SIMS/$n" && "$EXE" model.xml --numThreads="$THREADS" > run.log 2>&1)
    echo "   exit $?  after $(( ($(date +%s) - start) / 60 )) min"
done
