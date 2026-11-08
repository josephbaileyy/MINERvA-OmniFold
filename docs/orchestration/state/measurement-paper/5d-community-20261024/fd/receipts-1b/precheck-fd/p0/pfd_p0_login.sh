#!/bin/bash
# 1B pre-check Part 1, P0: the stat-only connect (FD-1B-PRECHECK-FD-BINDING-1.md ruling 3; declaration section 6), on a
# login node at 0 node-h, from a fresh clone at M = ed8f328f with empty porcelain. It stats every source the run reads
# (staged and in-place) and reads no file content. The COV2D fence is recorded. The universe list comes from the
# bound code's own fd_1b_toys.s1_universes(). Everything local is under the literal root /dev/shm/limres-pfd-p0-20261107
# (refused if it exists), removed by its literal path at exit. Launched from a /dev/shm copy of itself ($1), which it
# deletes.
SELF=$1
M=ed8f328fab52122112f54850d0078d79e81834c5
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
P=/pscratch/sd/j/josephrb
finish() { echo "== pfd-p0 rc=$1 $(date -u +%FT%TZ)"; rm -rf -- /dev/shm/limres-pfd-p0-20261107; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node"; rm -f -- "$SELF"; exit 9 ;; esac
[ ! -e /dev/shm/limres-pfd-p0-20261107 ] || { echo "STOP: /dev/shm/limres-pfd-p0-20261107 exists"; rm -f -- "$SELF"; exit 9; }
mkdir /dev/shm/limres-pfd-p0-20261107 || { rm -f -- "$SELF"; exit 9; }
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== COV2D fence (recorded; P0 reads no content)"
fence=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
echo "squeue rc=$frc; cov2d-* rows: [$(printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/')]"
git clone --quiet --filter=blob:none --no-checkout https://github.com/josephbaileyy/MINERvA-OmniFold.git \
  /dev/shm/limres-pfd-p0-20261107/repo || { echo "STOP: clone failed"; finish 5; }
git -C /dev/shm/limres-pfd-p0-20261107/repo -c advice.detachedHead=false checkout --quiet "$M" || { echo "STOP: checkout"; finish 5; }
head=$(git -C /dev/shm/limres-pfd-p0-20261107/repo rev-parse HEAD); porc=$(git -C /dev/shm/limres-pfd-p0-20261107/repo status --porcelain | wc -l)
echo "HEAD $head; porcelain lines $porc"; [ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: clone not M clean"; finish 5; }
cd /dev/shm/limres-pfd-p0-20261107/repo/nd-unfolding || finish 5
env -u PYTHONPATH "$PY" -B -c 'import fd_1b_toys as t; print("\n".join(t.s1_universes()))' > /dev/shm/limres-pfd-p0-20261107/universes.txt \
  || { echo "STOP: universe list"; finish 5; }
env -u PYTHONPATH "$PY" -B -c 'import fd_1b_precheck_fd as p; print("\n".join(p.universes()))' > /dev/shm/limres-pfd-p0-20261107/fd-universes.txt \
  || { echo "STOP: Part 1 universe list"; finish 5; }
echo "S1 universes $(wc -l < /dev/shm/limres-pfd-p0-20261107/universes.txt); Part 1 universes $(wc -l < /dev/shm/limres-pfd-p0-20261107/fd-universes.txt)"
L=/dev/shm/limres-pfd-p0-20261107/paths.txt
{ echo "staged|$P/fd-1b-20261030/runs/derivation/fd1b_derivation_CV.npz"
  while read -r u; do echo "staged|$P/fd-1b-20261030/runs/derivation/fd1b_derivation_$u.npz"; done < /dev/shm/limres-pfd-p0-20261107/universes.txt
  echo "staged|$P/s1-20261024/runs/uni/S1_CV.npz"
  while read -r u; do echo "staged|$P/s1-20261024/runs/uni/S1_$u.npz"; done < /dev/shm/limres-pfd-p0-20261107/universes.txt
  echo "staged|$P/s1-20261024/s1_assembly.npz"
  echo "staged|$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
  echo "staged|$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root"
  echo "inplace|$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
  echo "inplace|$P/s5c-20260924/runs/p2/bkg_dump.npz"
  echo "inplace|$P/fd-1b-20261030/pins.json"
  echo "inplace|$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz"
  while read -r u; do
    case "$u" in
      Flux_*) for k in wt wr tdw bkgw; do echo "inplace|$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/${u}_$k.npy"; done ;;
      *) for k in wt wr denom_nd bkgw; do echo "inplace|$P/s5p-20260926/bank_detector/${u}_$k.npy"; done ;;
    esac
  done < /dev/shm/limres-pfd-p0-20261107/fd-universes.txt; } > "$L"
echo "== stat of $(wc -l < "$L") sources (name|size|mtime|atime), no content read"
n_missing=0; now=$(date +%s); oldest=$now
while IFS='|' read -r kind path; do
  if s=$(stat -c '%s|%Y|%X' "$path" 2>/dev/null); then
    echo "$kind|$path|$s"; a=${s##*|}; [ "$a" -lt "$oldest" ] && oldest=$a
  else echo "$kind|$path|MISSING"; n_missing=$((n_missing + 1)); fi
done < "$L"
echo "== summary: sources $(wc -l < "$L"); missing $n_missing"
echo "oldest atime $(date -u -d @"$oldest" +%FT%TZ); exposed from (oldest atime + 8 weeks, arithmetic) $(date -u -d @"$((oldest + 56 * 86400))" +%FT%TZ)"
[ "$n_missing" -eq 0 ] || { echo "STOP: a source is missing; nothing staged; to the director"; finish 4; }
finish 0
