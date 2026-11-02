#!/bin/bash
# GENCMP E2 (addendum E2-A1, binding #677), the chi2 step on a login node after V.ok, R1.ok and U.ok: C1-C3, then
# e2.json. From $R/deploy at M'''. Writes only under $R. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-e2a1-20261102
M=372db7653ca16b34d033d076e609cb07b1fce0d2
cd "$R/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M'''"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$R/logs/env-chi2.log" 2>&1
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
case "$(python -V 2>&1)" in *3.11*) ;; *) echo "STOP: environment did not activate"; exit 2 ;; esac
hostname; date -u +%FT%TZ
env -u PYTHONPATH python -B nd-unfolding/fd_gencmp_e2.py chi2 --run-dir "$R" > "$R/logs/chi2.log" 2>&1
rc=$?; echo "chi2 rc=$rc"; date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
