#!/bin/bash
# GENCMP amendment E addendum E2 (binding #677 (addendum E2-A1), ruling 1/5): a fresh clone at M''' into $R/deploy, the four bound blobs
# verified against the binding's list, the environment (RE-1's setup_salloc_env.sh, Python 3.11), the import closure
# (S7) and the bound tests. Writes only under $R. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-e2a1-20261102
M=372db7653ca16b34d033d076e609cb07b1fce0d2
[ -e "$R" ] && { echo "STOP: $R exists"; exit 2; }
mkdir -p "$R"/{receipts,logs,tmp} || exit 2
{ hostname; date -u +%FT%TZ; } > "$R/receipts/deploy-host.txt"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$R/deploy" > "$R/logs/clone.log" 2>&1 || { echo clone failed; exit 3; }
cd "$R/deploy" && git -c advice.detachedHead=false checkout -q --detach "$M" || exit 3
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'''"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
bad=0
while read -r h p; do g=$(git rev-parse "$M:$p"); echo "$g $p"; [ "$g" = "$h" ] || bad=1; done < /dev/shm/e2a1_want.txt > "$R/receipts/deploy-blobs.txt"; cp /dev/shm/e2a1_want.txt "$R/receipts/want-blobs.txt"
cut -c1-12 "$R/receipts/deploy-blobs.txt"
[ "$(wc -l < "$R/receipts/deploy-blobs.txt")" -eq 4 ] || { echo "STOP: not four blobs"; exit 9; }
[ $bad = 0 ] || { echo "STOP: a blob differs"; exit 9; }
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$R/logs/env-deploy.log" 2>&1
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1
python -V 2>&1; case "$(python -V 2>&1)" in *3.11*) ;; *) echo "STOP: environment did not activate"; exit 2 ;; esac
cd nd-unfolding
env -u PYTHONPATH python -B -c "
import sys; sys.path[:0] = ['.', 'pv-ladder']
import fd_gencmp_e2, fd_gencmp_e, fd_gencmp, fd_cpl_addition, fd_g_compare
import pvl_ratios, pvl_unfold, pvl_analyze, pvl_lib, build_cmodel5d, pv2d_lib, s5n_pseudo, lightgbm
print('import closure ok; lightgbm', lightgbm.__version__)" > "$R/logs/imports.log" 2>&1
rc=$?; cat "$R/logs/imports.log" | tail -2; [ $rc = 0 ] || { echo "STOP: import closure (S7)"; exit 9; }
cd tests && env -u PYTHONPATH python -B -m unittest test_fd_gencmp_e2 > "$R/logs/tests-e2.log" 2>&1
echo "tests rc=$? $(grep -E '^Ran|^OK|^FAILED' "$R/logs/tests-e2.log" | tr '\n' ' ')"
cd "$R/deploy" && [ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
echo "deploy ok at $M"
