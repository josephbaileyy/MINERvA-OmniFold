#!/bin/bash
# GENCMP amendment E addendum E-A2 (binding #710, ruling 1): on login37, root_6_28, 0 node-h. A fresh clone at M'''' into
# $R/deploy, the four bound blobs verified, the bound tests, then fd_gencmp_ea2.py (the chain's figure entry,
# fd_g_figures_check, control D) into $R/figures-a2. Reads only committed files in the clone. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-ea2-20261102
M=e1c0af3b0e5367369540e27a25b372f92e49f871
[ "$(hostname)" = login37 ] || { echo "STOP: not login37"; exit 2; }
[ -e "$R" ] && { echo "STOP: $R exists"; exit 2; }
mkdir -p "$R"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$R/receipts/host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$R/deploy" > "$R/logs/clone.log" 2>&1 || { echo clone failed; exit 3; }
cd "$R/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M''''"; exit 9; }
[ -z "$(git status --porcelain --ignored)" ] || { echo "porcelain not empty"; exit 9; }
cat > "$R/receipts/want-blobs.txt" <<'W'
76d1c5b8b41da48d93f60775c63a1411faa334c4 nd-unfolding/fd_g_figures.py
943bb2f2294614569e0efa343bfbc2fe20829ded nd-unfolding/fd_g_figures_check.py
16e4e20f6cd671f0d3744d02dfeceb543e56e648 nd-unfolding/fd_gencmp_ea2.py
955db2d9db1115b54849f8be9c14312ff58c4af4 nd-unfolding/tests/test_fd_gencmp_ea2.py
W
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done < "$R/receipts/want-blobs.txt" > "$R/receipts/deploy-blobs.txt"
[ $bad = 0 ] && [ "$(wc -l < "$R/receipts/deploy-blobs.txt")" -eq 4 ] || { echo "STOP: a blob differs"; exit 9; }
echo "blobs ok"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1
env -u PYTHONPATH python3 -c 'import sys, matplotlib, numpy; print(sys.version.split()[0], "matplotlib", matplotlib.__version__, "numpy", numpy.__version__)' > "$R/receipts/env.txt" 2>&1
cat "$R/receipts/env.txt"
grep -q "matplotlib 3.10.8" "$R/receipts/env.txt" || { echo "STOP: not matplotlib 3.10.8"; exit 9; }
cd "$R/deploy/nd-unfolding/tests" && env -u PYTHONPATH python3 -B -m unittest test_fd_gencmp_ea2 test_fd_gencmp_e test_fd_g_figures > "$R/logs/tests.log" 2>&1
trc=$?; echo "tests rc=$trc $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests.log" | tr '\n' ' ')"
[ $trc = 0 ] || { echo "STOP: tests"; exit 9; }
cd "$R/deploy" && env -u PYTHONPATH python3 -I -B nd-unfolding/fd_gencmp_ea2.py --out-dir "$R/figures-a2" > "$R/logs/ea2.out" 2> "$R/logs/ea2.err"
rc=$?; echo "rc=$rc" >> "$R/logs/ea2.out"; echo "ea2 rc=$rc"; grep -E 'OK:|control D' "$R/logs/ea2.out"
(cd "$R/figures-a2" 2>/dev/null && sha256sum * > "$R/receipts/figures-a2.sha256")
cd "$R/deploy" && echo "porcelain after: $(git status --porcelain --ignored | wc -l)"
date -u +%FT%TZ >> "$R/receipts/host.txt"
exit $rc
