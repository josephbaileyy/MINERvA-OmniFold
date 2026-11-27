#!/bin/bash
# geanttw P2-P3 D1: which Perlmutter python3 has uproot? One fresh ssh, the director's GO of 2026-11-27 (option 1).
#   bash probe_uproot.sh > probe.out 2>&1
# On the login node it only runs `python3 -I -c 'import sys,uproot;...'` on each ~/.conda/envs/*/bin/python3 and on
# `module load python`'s python3. A FAIL line is printed for each interpreter lacking uproot. No data file, no stat of
# a /pscratch production path, no pip or conda install, and no write on the cluster.
SSH="ssh -o ControlMaster=no -o ControlPath=none -o BatchMode=yes -o ProxyJump=none -o ProxyCommand=none perlmutter.nersc.gov"
echo "mac_utc=$(date -u +%FT%TZ)"
${SSH} bash -s <<'EOF'; rc=$?
echo "host=$(hostname -s) utc=$(date -u +%FT%TZ)"
probe() {
  "$1" -I -c 'import sys,uproot;print(sys.executable,sys.version.split()[0],uproot.__version__)' 2>/dev/null \
    || echo "FAIL $1 (no uproot, or not runnable)"
}
for py in "$HOME"/.conda/envs/*/bin/python3; do
  [ -x "$py" ] && probe "$py"
done
mp=$(module load python >/dev/null 2>&1 && command -v python3)
if [ -n "$mp" ]; then probe "$mp"; else echo "FAIL module load python (no python3 found)"; fi
EOF
echo "== probe rc=${rc} $(date -u +%FT%TZ)"
