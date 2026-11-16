#!/bin/bash
# cr connect (the director's XCOV ruling: fd_gencmp cmd_overlap re-run under C_new, after the RE-2-shapes production):
# GENCMP amendment E step C-R's own command (fd/gencmp-e/c-r/e_cr.sh: fd_gencmp.py overlap --arm refined, on a login
# node in omnifold_py310, which has uproot), run twice on one fresh deploy at PKG (fd_gencmp.py unchanged since step
# C-R's M 6cd095d6):
#   control  exactly e_cr.sh's arguments (--q2d partc-r2's Q_R): its overlap_refined.json must reproduce the committed
#            fd/gencmp-e/c-r/overlap_refined.json (cr_compare.py: equal after dropping argv and the deploy prefix).
#            A STOP here leaves the g2r arm unrun.
#   g2r      --q2d route A's Q_R (RE2SHAPES PASS, #1167: cov2d-re2shapes-20261115/g2r/combination/s5_plus_playlist.npz,
#            81fdd16f), pinned by fd/receipts-cov2d/g2r/cr/INPUTS-g2r.sha256 beside step C-R's two INPUTS files.
#            Everything else is step C-R's (--playlist partc-r2's playlist_term.npz, identical to the g2r tree's).
# The fence is RE-2-shapes rev 3's, verbatim (fails closed, refuses every job, helper-2's marker), at the start and
# again before the g2r arm. Writes only under $W and $LOG. Login node, 0 node-h. Not under set -u.
# Run: setsid nohup bash /dev/shm/josephrb-g2r-cr.sh >/dev/null 2>&1 </dev/null &
PKG=__PKG__                                  # the lane's package commit (branch lane/cr-g2r-20261116)
P=/pscratch/sd/j/josephrb
W=$P/cov2d-cr-g2r-20261116; DEP=$W/deploy
R=$P/2d-closeout-re2-20261023
G2RQ=$P/cov2d-re2shapes-20261115/g2r/combination/s5_plus_playlist.npz
FD=docs/orchestration/state/measurement-paper/5d-community-20261024
GENCMP=__SHA_GENCMP__                        # nd-unfolding/fd_gencmp.py at PKG (= at 6cd095d6)
CMPSHA=__SHA_CMP__                           # cr_compare.py at PKG
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
URL=https://github.com/josephbaileyy/MINERvA-OmniFold
LOG=/dev/shm/josephrb-g2r-cr.log
stop() { echo "STOP $*"; echo "CR INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; cp "$LOG" "$W/logs/connect.log" 2>/dev/null; echo DONE; exit 2; }
[[ $PKG =~ ^[0-9a-f]{40}$ ]] || { echo "STOP PKG is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }
for v in "$GENCMP" "$CMPSHA"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }; done
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
# ---- the deploy and the environment (e_cr.sh's)
mkdir -p "$W/logs" "$W/control" "$W/g2r" "$W/tmp" || stop mkdir
git clone --quiet "$URL" "$DEP" && git -C "$DEP" checkout --quiet --detach "$PKG" || stop clone
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); h=$(git -C "$DEP" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$PKG" ] || stop "deploy not clean at PKG"
[ "$(sha256sum "$DEP/nd-unfolding/fd_gencmp.py" | cut -d' ' -f1)" = "$GENCMP" ] || stop "fd_gencmp.py is not the pinned one"
[ "$(sha256sum "$DEP/$FD/fd/receipts-cov2d/g2r/cr/cr_compare.py" | cut -d' ' -f1)" = "$CMPSHA" ] || stop "cr_compare.py is not the pinned one"
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/omnifold_py310" || stop "conda activate"
export TMPDIR=$W/tmp
env -u PYTHONPATH python -B -c "import sys,numpy,uproot;print('python',sys.version.split()[0]);print('numpy',numpy.__version__);print('uproot',uproot.__version__);print('executable',sys.executable)" > "$W/environment.txt" || stop "environment"
cat "$W/environment.txt"
ov() {  # ov <arm dir> <q2d> <extra --inputs ...>
  local out=$1 q=$2; shift 2
  (cd "$DEP" && env -u PYTHONPATH python -B nd-unfolding/fd_gencmp.py overlap --arm refined \
    --inputs $FD/fd/gencmp/INPUTS.sha256 --inputs $FD/fd/gencmp-e/INPUTS.sha256 "$@" \
    --p5 $P/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz --mnvtune $P/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz \
    --cv2d $R/partb/out/ER/xsec.root --q2d "$q" \
    --playlist $R/partc-r2/playlist/playlist_term.npz \
    --cv3d $P/MINERvA-OmniFold/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root \
    --proj3d $P/z2m-products/PROJ3D/cov_5d_to_ptpzeavail_from_adopted_trunk.root \
    --out "$out/overlap_refined.json") > "$out/overlap.out" 2> "$out/overlap.err"
}
# ---- control: step C-R exactly, then the comparison with its committed readout
echo "control start=$(date -u +%FT%TZ)"
ov "$W/control" "$R/partc-r2/combination/s5_plus_playlist.npz"; rc=$?
echo "control rc=$rc end=$(date -u +%FT%TZ)"; tail -6 "$W/control/overlap.out"
[ "$rc" = 0 ] || stop "control rc=$rc (see $W/control/overlap.err)"
env -u PYTHONPATH python -B "$DEP/$FD/fd/receipts-cov2d/g2r/cr/cr_compare.py" --rerun "$W/control/overlap_refined.json" \
  --committed "$DEP/$FD/fd/gencmp-e/c-r/overlap_refined.json" --rerun-deploy "$DEP" > "$W/control/compare.out" 2>&1; crc=$?
cat "$W/control/compare.out"
[ "$crc" = 0 ] && grep -q '^CR-CONTROL PASS' "$W/control/compare.out" || stop "the control did not reproduce step C-R's committed readout"
# ---- g2r: route A's Q_R
fence "before the g2r arm"
echo "g2r start=$(date -u +%FT%TZ)"
ov "$W/g2r" "$G2RQ" --inputs $FD/fd/receipts-cov2d/g2r/cr/INPUTS-g2r.sha256; rc=$?
echo "g2r rc=$rc end=$(date -u +%FT%TZ)"; tail -6 "$W/g2r/overlap.out"
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); echo "deploy porcelain after: $n"
(cd "$W" && sha256sum environment.txt control/overlap_refined.json control/compare.out g2r/overlap_refined.json) > "$W/out.sha256" 2>&1; cat "$W/out.sha256"
[ "$rc" = 0 ] || stop "g2r rc=$rc (see $W/g2r/overlap.err)"
[ "$n" = 0 ] || stop "the deploy is not clean after the runs"
echo "CR PASS: control reproduced step C-R; g2r arm rc 0"
cp "$LOG" "$W/logs/connect.log" 2>/dev/null
echo "end=$(date -u +%FT%TZ)"; echo DONE
