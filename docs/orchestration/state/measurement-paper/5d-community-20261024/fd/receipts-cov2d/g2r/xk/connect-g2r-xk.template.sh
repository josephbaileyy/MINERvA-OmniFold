#!/bin/bash
# xk connect (the director's XCOV ruling and xk design rulings of 2026-11-16): GENCMP X's step K (fd_xcov.py k, on a
# login node in omnifold_py310, as fd/xcov/run/receipts/x_k.sh ran it: 11.27 s, 1.5 GB RSS, login37) run twice on one
# fresh deploy at PKG:
#   control  `k --products re2` (K as it ran) on $W/ctl: must reproduce the committed fd/xcov/run/k/k.json exactly
#            (xk_compare.py: parsed equality; the readout names no deploy or run-directory path). A STOP leaves g2r unrun.
#   g2r      `k --products g2r` on $W/run: Q_R and S5_R are RE-2-shapes route A's (S5_R's band blocks are G2R's rebuilt
#            band blocks, K1's 2D reference), the 2D band vectors are G2R's A_<b>_<i> products, C-R is cr's readout and
#            cmodel_R is route A's (fd_xcov_steps.PRODUCTS; pins fd/receipts-cov2d/g2r/xk/INPUTS-g2r.sha256).
# Both run directories hold digest-checked copies (xk_copy.py) of the original X run's V0, V1 and BOOT records and its
# staged of_inputs_5d.npz, which K reads from its run directory: V0, V1 and BOOT read no 2D covariance product, so they
# are reused, not rerun (ruling 1). The original run directory /pscratch/sd/j/josephrb/gencmp-x-20261102 is only read.
# Ruling 2: V1's pairing holds for G2R's products only if the MEFHC universes file is at X's pin (220c479e, also
# cov2d.UNI_SHA256, under which G2R's unfolds read it); a different digest is a STOP.
# The fence is RE-2-shapes rev 3's, verbatim, at the start and again before the g2r arm. Writes only under $W and $LOG.
# Login node, 0 node-h. Not under set -u (conda).
# Run: setsid nohup bash /dev/shm/josephrb-g2r-xk.sh >/dev/null 2>&1 </dev/null &
PKG=__PKG__                                  # the lane's package commit (branch lane/xk-g2r-20261116)
P=/pscratch/sd/j/josephrb
W=$P/cov2d-xk-g2r-20261116; DEP=$W/deploy
R0=$P/gencmp-x-20261102                      # the original X run directory (read only)
UNI=$P/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
UNISHA=220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418   # fd/xcov INPUTS pin = cov2d.UNI_SHA256
FD=docs/orchestration/state/measurement-paper/5d-community-20261024
XK=$FD/fd/receipts-cov2d/g2r/xk
SHA_XCOV=__SHA_XCOV__; SHA_STEPS=__SHA_STEPS__; SHA_COPY=__SHA_COPY__; SHA_CMP=__SHA_CMP__
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
URL=https://github.com/josephbaileyy/MINERvA-OmniFold
LOG=/dev/shm/josephrb-g2r-xk.log
stop() { echo "STOP $*"; echo "XK INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; cp "$LOG" "$W/logs/connect.log" 2>/dev/null; echo DONE; exit 2; }
[[ $PKG =~ ^[0-9a-f]{40}$ ]] || { echo "STOP PKG is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }
for v in "$SHA_XCOV" "$SHA_STEPS" "$SHA_COPY" "$SHA_CMP"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }; done
[ -e "$W" ] && { echo "STOP $W exists" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ PKG=$PKG nproc=$(nproc) OMP_NUM_THREADS=${OMP_NUM_THREADS:-unset}"
# ---- the fence: at the start, and again before the g2r arm (coverage-5b-audit low: not start-time only)
fence() {
  TERM_RE='^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)'
  sq=$(squeue --me -o '%i|%j|%T|%l|%D'); sqrc=$?
  echo "squeue rc=$sqrc: [$(printf '%s' "$sq" | tr '\n' ';')]"
  [ "$sqrc" = 0 ] || stop "squeue failed (rc $sqrc): the fence is not clear"
  [ "$(printf '%s\n' "$sq" | head -1)" = "JOBID|NAME|STATE|TIME_LIMIT|NODES" ] || stop "squeue's reply has no header (empty or malformed): the fence is not clear"
  [ "$(printf '%s\n' "$sq" | awk 'END {print NR}')" = 1 ] || stop "a job of josephrb is queued or running (the fence refuses every job)"
  s1=$(sacct -X -n -P -S 2026-11-01 -u josephrb --name rdx_s1_1A -o JobID,JobName,State,End); s1rc=$?
  echo "sacct rdx_s1_1A rc=$s1rc: [$(printf '%s' "$s1" | tr '\n' ';')]"
  [ "$s1rc" = 0 ] || stop "sacct (rdx_s1_1A) failed (rc $s1rc): the fence is not clear"
  [ -n "$s1" ] || stop "sacct shows no rdx_s1_1A job (an empty reply): the fence is not clear"
  printf '%s\n' "$s1" | awk -F'|' -v t="$TERM_RE" '$3 !~ t {bad = 1} END {exit bad}' || stop "rdx_s1_1A has not ended"
  al=$(sacct -X -n -P -S 2026-11-01 -u josephrb -o JobID,JobName,State); alrc=$?
  echo "sacct all since 2026-11-01 rc=$alrc: $(printf '%s\n' "$al" | awk 'END {print NR}') rows"
  [ "$alrc" = 0 ] || stop "sacct (all jobs) failed (rc $alrc): the fence is not clear"
  [ -n "$al" ] || stop "sacct lists no job since 2026-11-01 (an empty reply; rdx_s1_1A at least is expected): the fence is not clear"
  un=$(printf '%s\n' "$al" | awk -F'|' -v t="$TERM_RE" '$3 !~ t')
  [ -z "$un" ] || stop "a job of josephrb is unended (the fence refuses every job): $(printf '%s' "$un" | tr '\n' ';')"
  [ -e "$FIGMARK" ] && stop "a group C figure connect is running (or left its marker): $(head -c 300 "$FIGMARK")"
  echo "fence ($1) clear: every query rc 0, rdx_s1_1A ended, no job queued, running or unended, group C marker absent"
}
fence start
# ---- the deploy, the pins, the universes file, the environment
mkdir -p "$W/logs" "$W/tmp" || stop mkdir
git clone --quiet "$URL" "$DEP" && git -C "$DEP" checkout --quiet --detach "$PKG" || stop clone
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); h=$(git -C "$DEP" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$PKG" ] || stop "deploy not clean at PKG"
cat > "$W/code.sha256" <<SUMS
$SHA_XCOV  nd-unfolding/fd_xcov.py
$SHA_STEPS  nd-unfolding/fd_xcov_steps.py
$SHA_COPY  $XK/xk_copy.py
$SHA_CMP  $XK/xk_compare.py
SUMS
(cd "$DEP" && sha256sum -c "$W/code.sha256") || stop "a code file is not its pinned sha256"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310" || stop "conda activate"
export TMPDIR=$W/tmp
{ env -u PYTHONPATH python -B -c "import sys,numpy,uproot;print('python',sys.version.split()[0]);print('numpy',numpy.__version__);print('uproot',uproot.__version__);print('executable',sys.executable)"; hostname; nproc; } > "$W/environment.txt" || stop "environment"
cat "$W/environment.txt"
got=$(env -u PYTHONPATH python -B -c "
import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 24)
    if not b: break
    h.update(b)
os.close(fd); print(h.hexdigest())" "$UNI") || stop "hashing the universes file"
echo "universes file sha256 $got (X's pin $UNISHA)"
[ "$got" = "$UNISHA" ] || stop "the MEFHC universes file is not at X's pin: V1's pairing does not carry to G2R's products"
env -u PYTHONPATH python -B "$DEP/$XK/xk_copy.py" --source "$R0" --hpss-list "$DEP/$FD/fd/xcov/run/hpss/files.sha256" \
  --dest "$W/ctl" --dest "$W/run" > "$W/logs/copy.out" 2>&1; crc=$?
cat "$W/logs/copy.out"
[ "$crc" = 0 ] && grep -q '^XK-COPY OK' "$W/logs/copy.out" || stop "the copies did not complete"
kstep() {  # kstep <run dir> <log> <products>
  (cd "$DEP" && /usr/bin/time -f "k wall %e s rss %M KB" env -u PYTHONPATH python -B nd-unfolding/fd_xcov.py k --run-dir "$1" --products "$3") > "$2" 2>&1
}
# ---- control: K as it ran
echo "control start=$(date -u +%FT%TZ)"
kstep "$W/ctl" "$W/logs/ctl-k.log" re2; rc=$?
echo "control rc=$rc end=$(date -u +%FT%TZ)"; tail -3 "$W/logs/ctl-k.log"
[ "$rc" = 0 ] || stop "control rc=$rc (see $W/logs/ctl-k.log)"
env -u PYTHONPATH python -B "$DEP/$XK/xk_compare.py" --rerun "$W/ctl/k/k.json" --committed "$DEP/$FD/fd/xcov/run/k/k.json" \
  > "$W/logs/ctl-compare.out" 2>&1; crc=$?
cat "$W/logs/ctl-compare.out"
[ "$crc" = 0 ] && grep -q '^XK-CONTROL PASS' "$W/logs/ctl-compare.out" || stop "the control did not reproduce the committed k.json"
# ---- g2r
fence "before the g2r arm"
echo "g2r start=$(date -u +%FT%TZ)"
kstep "$W/run" "$W/logs/g2r-k.log" g2r; rc=$?
echo "g2r rc=$rc end=$(date -u +%FT%TZ)"; tail -3 "$W/logs/g2r-k.log"
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); echo "deploy porcelain after: $n"
(cd "$W" && sha256sum environment.txt code.sha256 ctl/k/k.json run/k/k.json logs/ctl-k.log logs/g2r-k.log logs/ctl-compare.out logs/copy.out) > "$W/out.sha256" 2>&1; cat "$W/out.sha256"
[ "$rc" = 0 ] || stop "g2r rc=$rc (see $W/logs/g2r-k.log)"
[ "$n" = 0 ] || stop "the deploy is not clean after the runs"
echo "XK PASS: control reproduced the committed k.json; g2r arm rc 0"
cp "$LOG" "$W/logs/connect.log" 2>/dev/null
echo "end=$(date -u +%FT%TZ)"; echo DONE
