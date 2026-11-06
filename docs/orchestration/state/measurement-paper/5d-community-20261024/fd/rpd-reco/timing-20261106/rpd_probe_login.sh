#!/bin/bash
# RPD-RECO login measurements (the director's request of 2026-11-06), 0 node-h: stages rpd_probe.py, fd_rpd_reco.py
# (10731ed3), h2_definition.json (10731ed3) and the repository's committed runEventLoopMC_PB.root (receipts-ct/5b/flux/,
# from git, no pscratch read), all shipped with this wrapper into /dev/shm/josephrb-rpd-probe by the launching ssh; copies ONE non-input MAT flux file by an
# O_NOATIME read, stat'ing its atime before and after; runs the probe in omnifold_py310 at OMP/MKL/OPENBLAS 1 and nice 19.
# The flux file is the antineutrino (pdg -14) gen2thin 1M flux: not among the nine C-N candidates (all pdg 14), not a
# declared RPD-RECO input, and not read by the numu COV2D analysis. Removes its /dev/shm directory by literal path.
B=/dev/shm/josephrb-rpd-probe
F=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/data/flux/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3
[ "$0" = /dev/shm/josephrb-rpd-probe/rpd_probe_login.sh ] || { echo "refusing: run from the staged directory"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
echo "probe sha256 $(sha256sum "$0" | cut -d' ' -f1) (this wrapper)"; (cd "$B" && sha256sum rpd_probe.py fd_rpd_reco.py h2_definition.json runEventLoopMC_PB.root)
echo "flux file before: $(stat -c '%U %a %s %X %n' "$F")"
dd if="$F" iflag=noatime status=none of="$B/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root" || { echo "copy failed"; rm -rf /dev/shm/josephrb-rpd-probe; exit 4; }
echo "flux file after:  $(stat -c '%U %a %s %X %n' "$F")"
echo "copy sha256 $(sha256sum "$B/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root" | cut -d' ' -f1)"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
nice -n 19 "$PY" -I -B "$B/rpd_probe.py" "$B" > "$B/probe.json" 2> "$B/probe.err"; rc=$?
echo "probe rc=$rc $(date -u +%FT%TZ)"; tail -5 "$B/probe.err"
echo "==JSON=="; cat "$B/probe.json"
rm -rf /dev/shm/josephrb-rpd-probe
