#!/bin/bash
# GENCMP E-A2, attempt 2 (the director's option (a), 2026-11-02): the same $R and its verified clone at M''''; the
# first attempt's pre-run gate stopped on uproot's absence in root_6_28 (logs/tests.log, kept). Gate on
# test_fd_gencmp_ea2 and test_fd_g_figures only, then fd_gencmp_ea2.py as bound. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-ea2-20261102
M=e1c0af3b0e5367369540e27a25b372f92e49f871
[ "$(hostname)" = login37 ] || { echo "STOP: not login37"; exit 2; }
[ -e "$R/figures-a2" ] && { echo "STOP: figures-a2 exists"; exit 2; }
cd "$R/deploy" || exit 2
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M''''"; exit 9; }
[ -z "$(git status --porcelain --ignored)" ] || { echo "porcelain not empty"; exit 9; }
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done < "$R/receipts/want-blobs.txt" > "$R/receipts/deploy-blobs-2.txt"
[ $bad = 0 ] || { echo "STOP: a blob differs"; exit 9; }
{ hostname; date -u +%FT%TZ; echo attempt 2; } >> "$R/receipts/host.txt"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1
env -u PYTHONPATH python3 -c 'import sys, matplotlib, numpy; print(sys.version.split()[0], "matplotlib", matplotlib.__version__, "numpy", numpy.__version__)' > "$R/receipts/env-2.txt" 2>&1
grep -q "matplotlib 3.10.8" "$R/receipts/env-2.txt" || { echo "STOP: not matplotlib 3.10.8"; exit 9; }
cd "$R/deploy/nd-unfolding/tests" && env -u PYTHONPATH python3 -B -m unittest test_fd_gencmp_ea2 test_fd_g_figures > "$R/logs/tests-2.log" 2>&1
trc=$?; echo "tests rc=$trc $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests-2.log" | tr '\n' ' ')" | tee "$R/logs/tests-2.summary"
[ $trc = 0 ] || { echo "STOP: tests"; exit 9; }
cd "$R/deploy" && env -u PYTHONPATH python3 -I -B nd-unfolding/fd_gencmp_ea2.py --out-dir "$R/figures-a2" > "$R/logs/ea2.out" 2> "$R/logs/ea2.err"
rc=$?; echo "rc=$rc" >> "$R/logs/ea2.out"; echo "ea2 rc=$rc"; grep -E 'OK:|FAIL|control D' "$R/logs/ea2.out"
(cd "$R/figures-a2" 2>/dev/null && sha256sum * > "$R/receipts/figures-a2.sha256")
cd "$R/deploy" && echo "porcelain after: $(git status --porcelain --ignored | wc -l)" | tee "$R/logs/porcelain-after.txt"
date -u +%FT%TZ >> "$R/receipts/host.txt"
exit $rc
