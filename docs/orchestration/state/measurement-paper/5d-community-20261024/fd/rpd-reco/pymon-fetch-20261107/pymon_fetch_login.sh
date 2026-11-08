#!/bin/bash
# RPD-RECO #848, pymon fetch (the director's request, 2026-11-07): copy NERSC's pymon interpreter-start files, which
# #881's worker trace (run/prologue.strace, pid 1198232) shows executing, and the Python version under the sourced
# root_6_28 environment that #881 used. Login node, 0 node-h. It reads no analysis input and writes no file: everything
# goes to stdout. Launched from a /dev/shm copy of itself ($1), which it deletes.
# In order:
#   1. the COV2D fence: every job of josephrb's must be named rs1_* or ens1_*. A cov2d-* name, or any other name,
#      refuses (the director's rule for this fetch). squeue only.
#   2. a listing of /opt/nersc/pymon (names, types, sizes, modes, mtimes).
#   3. for each pymon file the trace shows opened: path, stat, sha256 and base64 of its full contents. The two the
#      director named come first: sitecustomize/__init__.py, then nersc_pymon/__init__.py. The rest are the other
#      pymon files the same trace shows the worker opening (log.py, _vendor/__init__.py, _vendor/nerscjson.py,
#      config/default.ini).
#   4. sys.version under the sourced environment: set +u; source setup_salloc_env.sh; set -u, as #881's wrapper does.
#      The wrapper's check-mat-setup step runs in a child process, so it cannot change this shell's environment, and
#      it is not run here. Both `python3` from PATH and MAT_PYTHON are recorded.
#   5. supplementary, data-free: NERSC_PYMON_UUID in that shell, then as seen inside two separate interpreter starts
#      and inside a child interpreter started by one of them.
SELF=$1
MAT_PYTHON=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MATENV=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
finish() { echo "== pymon-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== 1. COV2D fence (allowed names: rs1_* and ens1_*; anything else refuses)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc; rows:"
printf '%s\n' "$fence"
echo "-- end rows"
bad=$(printf '%s\n' "$fence" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 2. listing of /opt/nersc/pymon"
find /opt/nersc/pymon -printf '%y %m %s %TY-%Tm-%TdT%TH:%TM:%TS %P\n' 2>&1 | sort -k5
echo "== 3. files"
for f in /opt/nersc/pymon/sitecustomize/__init__.py /opt/nersc/pymon/nersc_pymon/__init__.py \
         /opt/nersc/pymon/nersc_pymon/log.py /opt/nersc/pymon/nersc_pymon/_vendor/__init__.py \
         /opt/nersc/pymon/nersc_pymon/_vendor/nerscjson.py /opt/nersc/pymon/nersc_pymon/config/default.ini; do
  echo "== FILE $f"
  stat "$f" 2>&1
  echo "sha256 $(sha256sum "$f" 2>&1 | cut -d' ' -f1)"
  echo "-- base64"
  base64 -w 76 "$f" 2>&1
  echo "-- end base64"
  echo "== END FILE $f"
done
echo "== 4 and 5. under the sourced environment"
bash -c '
set +u
source "$1" > /dev/null 2>&1
echo "setup source rc=$?"
set -u
echo "python3 on PATH: $(command -v python3)"
python3 -c "import sys; print(sys.version); print(sys.executable)"
echo "python3 rc=$?"
echo "MAT_PYTHON: $2"
"$2" -c "import sys; print(sys.version); print(sys.executable)"
echo "MAT_PYTHON rc=$?"
echo "== 5. NERSC_PYMON_UUID"
echo "shell: ${NERSC_PYMON_UUID-<unset>}"
echo "PYTHONPATH: ${PYTHONPATH-<unset>}"
for i in 1 2; do
  "$2" -c "import os; print(\"interpreter start $i:\", os.environ.get(\"NERSC_PYMON_UUID\", \"<unset>\"))"
done
"$2" -c "import os, subprocess, sys; print(\"parent:\", os.environ.get(\"NERSC_PYMON_UUID\", \"<unset>\")); sys.stdout.flush(); subprocess.run([sys.executable, \"-c\", \"import os; print(\\\"child:\\\", os.environ.get(\\\"NERSC_PYMON_UUID\\\", \\\"<unset>\\\"))\"], check=False)"
echo "shell after: ${NERSC_PYMON_UUID-<unset>}"
' pymon-env "$MATENV" "$MAT_PYTHON" 2>&1
echo "sourced-shell rc=$?"
finish 0
