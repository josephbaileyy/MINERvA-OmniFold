#!/bin/bash
# GENCMP E2, the login steps in order (binding #675 ruling 1): stage (O_NOATIME copies), vertices (V), ratios (R1).
# Each step's controls write its receipt; a stop ends the run (ruling 2: final). From $R/deploy at M''. Writes only
# under $R. No set -u (conda).
R=/pscratch/sd/j/josephrb/gencmp-e2-20261102
M=885e366ec46059b230352b08be5a47f13160768c
cd "$R/deploy" || exit 9
[ "$(git rev-parse HEAD)" = "$M" ] || { echo "HEAD not M''"; exit 9; }
[ -z "$(git status --porcelain)" ] || { echo "porcelain not empty"; exit 9; }
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > "$R/logs/env-login.log" 2>&1
export TMPDIR=$R/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
case "$(python -V 2>&1)" in *3.11*) ;; *) echo "STOP: environment did not activate"; exit 2 ;; esac
hostname
for step in stage vertices ratios; do
  date -u +%FT%TZ
  env -u PYTHONPATH python -B nd-unfolding/fd_gencmp_e2.py $step --run-dir "$R" > "$R/logs/$step.log" 2>&1
  rc=$?; echo "$step rc=$rc"; tail -3 "$R/logs/$step.log"
  [ $rc = 0 ] || { echo "STOP at $step (final)"; break; }
done
date -u +%FT%TZ
[ -z "$(git status --porcelain)" ] && echo "porcelain after: empty"
ls "$R/vertices/V.ok" "$R/prep_ch/R1.ok" 2>&1
