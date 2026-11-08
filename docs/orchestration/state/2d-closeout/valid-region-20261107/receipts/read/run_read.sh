#!/bin/bash
# Valid-region read (BINDING-1.md ruling 4): local, at M, 0 node-h, no cluster contact.
# Usage: bash run_read.sh <new workdir>. No set -e: every rc is read explicitly, unpiped.
M=0687d6f2776b3ad691568f701de3aff166d9ca2a
SRC=/Users/josephbailey/local-research/MINERvA-OmniFold
D=docs/orchestration/state/2d-closeout/valid-region-20261107
PINS="f46bb725607b0220c8fb85a8e572a63c7e5c587233496d2e7f27ecc7f0ca83a8  $D/DECLARATION.md
896201cc9d03754ddac5185f548b1b7e3a56183dbb0fe6503fcd75c5c59d5433  $D/valid_region.py
0df3207292ebd8c9e302f263eaa38e0012ef755940c95d311603d22916064580  $D/test_valid_region.py
53aae44cd2327509863a2c65180f6701e2f5c8860a7fe971f2d0097f1a45045a  $D/INPUTS.sha256"
W=${1:?usage: run_read.sh <workdir>}
[ -e "$W" ] && { echo "STOP: $W exists"; exit 2; }
mkdir -p "$W/R" || exit 2
LOG=$W/R/run.log
say() { echo "$*" | tee -a "$LOG"; }
say "== valid-region read $(date -u +%FT%TZ) M=$M host=$(hostname -s)"
git clone -q --no-checkout "$SRC" "$W/clone" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: clone rc $rc"; exit 3; }
git -C "$W/clone" checkout -q "$M" >>"$LOG" 2>&1; rc=$?
[ $rc -eq 0 ] || { say "STOP: checkout rc $rc"; exit 3; }
head=$(git -C "$W/clone" rev-parse HEAD)
[ "$head" = "$M" ] || { say "STOP: HEAD $head != M"; exit 3; }
porc=$(git -C "$W/clone" status --porcelain)
[ -z "$porc" ] || { say "STOP: porcelain not empty"; exit 3; }
say "clone at M; porcelain empty"
printf '%s\n' "$PINS" > "$W/R/binding-pins.sha256"
(cd "$W/clone" && shasum -a 256 -c "$W/R/binding-pins.sha256") > "$W/R/binding-pins.check" 2>&1; rc=$?
cat "$W/R/binding-pins.check" >> "$LOG"
[ $rc -eq 0 ] || { say "STOP: binding pins differ (rc $rc)"; exit 3; }
say "binding pins 4/4 equal"
(cd "$W/clone" && shasum -a 256 -c "$D/INPUTS.sha256") > "$W/R/inputs.check" 2>&1; rc=$?
cat "$W/R/inputs.check" >> "$LOG"
[ $rc -eq 0 ] || { say "STOP: inputs differ (rc $rc)"; exit 3; }
say "inputs 6/6 equal (shasum -a 256 -c INPUTS.sha256, rc 0)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=$(command -v python3)
"$PY" -c 'import sys, numpy; print("python", sys.version.split()[0], "numpy", numpy.__version__, "exe", sys.executable)' > "$W/R/environment.txt" 2>&1
cat "$W/R/environment.txt" >> "$LOG"
(cd "$W/clone/$D" && "$PY" -B -m unittest test_valid_region) > "$W/R/tests.log" 2>&1; rc=$?
say "tests rc $rc: $(grep -E '^Ran [0-9]+ tests' "$W/R/tests.log") $(tail -n 1 "$W/R/tests.log")"
[ $rc -eq 0 ] || { say "STOP: tests failed"; exit 3; }
(cd "$W/clone/$D" && "$PY" -B valid_region.py read --repo "$W/clone" --out "$W/out") > "$W/R/read.stdout" 2> "$W/R/read.stderr"; read_rc=$?
say "read rc $read_rc; stderr: $(cat "$W/R/read.stderr")"
cp "$W/out/readout.json" "$W/out/readout.txt" "$W/R/" 2>/dev/null
porc2=$(git -C "$W/clone" status --porcelain)
say "clone porcelain after the read: '${porc2}'"
(cd "$W/R" && shasum -a 256 $(ls | grep -v SHA256SUMS) > SHA256SUMS)
exit $read_rc
