#!/bin/bash
# REGRADE's sixteen-cell capture connect (REGRADE-DECLARATION.md rev 2, section 5), on a Perlmutter login node, from a
# /dev/shm copy of itself whose path is $1; it deletes that copy at exit.
#   usage: capture_connect.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, any failure a final stop:
#   the window (now <= window_end, an epoch computed from date by the launcher); no Slurm job set; a login node;
#   the fence: no job of this user whose name starts with a fenced prefix is non-terminal, by sacct (never squeue);
#   $OUT new; a fresh clone; the deploy checked out at M_L, clean; the capture tool and the hpss list taken from the
#   pushed branch commit TOOLS_COMMIT by `git show`, each equal to its pinned sha256;
#   the capture under root_6_28's python3 (threads 1, nice 19): ll5d_regrade_capture.py, whose own checks are the
#   pins, the bound digests, the toy set and atime moved [] over every watched path.
# Writes only under $OUT. No Slurm job, 0 node-h. No set -u (it kills setup_salloc_env.sh).
SELF=$1; WEND=$2; FENCE=$3
M_L=4231b14de5ea693e92cb31b1358a816b5c2f6625
TOOLS_COMMIT=f6bb61858f8c87d75f85f3d24549127907c7ca40
CAP_SHA=fed8c9717cc786722181f7809dcfab62ae21a49b43d35de6adf64283f28ffe95
LIST_SHA=980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d
RD=docs/orchestration/state/measurement-paper/5d-community-20261024/fd
P=/pscratch/sd/j/josephrb
OUT=$P/regrade-capture-20261121
D=$OUT/deploy
STAGED=$P/fd-1b-inv-20261101/i0/in
U=$P/ll5d-unfolds-r2
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node";; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set"
fence_sacct() {
  local rows bad
  rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "sacct failed: $rows"; return 2; }
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      if (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }')
  [ -z "$bad" ] || { echo "fenced jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"
[ ! -e "$OUT" ] || bail "$OUT exists"
mkdir -p "$OUT/logs" "$OUT/tools" || bail "mkdir"
LOG=$OUT/logs/connect-capture.log
exec > "$LOG" 2>&1
finish() { echo "capture connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-capture.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/capture_connect.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M_L" || { echo "STOP: checkout M_L"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M_L" ] || { echo "STOP: HEAD is not M_L"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=all | wc -l); echo "HEAD $M_L; porcelain lines $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
git -C "$D" cat-file -e "$TOOLS_COMMIT^{commit}" || { echo "STOP: the tools commit $TOOLS_COMMIT is not in the clone"; finish 3; }
git -C "$D" show "$TOOLS_COMMIT:$RD/regrade-crep-20261121/ll5d_regrade_capture.py" > "$OUT/tools/ll5d_regrade_capture.py" || { echo "STOP: git show capture"; finish 3; }
git -C "$D" show "$TOOLS_COMMIT:$RD/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv" > "$OUT/tools/hpss_ll5d_u_list.tsv" || { echo "STOP: git show list"; finish 3; }
c=$(sha256sum "$OUT/tools/ll5d_regrade_capture.py" | cut -d' ' -f1); l=$(sha256sum "$OUT/tools/hpss_ll5d_u_list.tsv" | cut -d' ' -f1)
echo "capture tool sha256 $c (pinned $CAP_SHA); list sha256 $l (pinned $LIST_SHA)"
[ "$c" = "$CAP_SHA" ] && [ "$l" = "$LIST_SHA" ] || { echo "STOP: a tool is not the pinned one"; finish 9; }
now=$(date +%s); [ "$now" -le "$WEND" ] || { echo "STOP: the window ended before the capture"; finish 9; }
echo "== capture start $(date -u +%FT%TZ)"
# the environment LL5D's readout job used: the deploy's setup_salloc_env.sh at its bound digest, then root_6_28's python3
[ "$(sha256sum "$D/setup_salloc_env.sh" | cut -d' ' -f1)" = "ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48" ] \
  || { echo "STOP: setup_salloc_env.sh is not the bound one"; finish 9; }
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env.log" 2>&1; src=$?
  [ "$src" -eq 0 ] || { echo "STOP: setup_salloc_env.sh rc=$src"; exit 97; }
  [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "STOP: python3 is not root_6_28's"; exit 98; }
  echo "python3 $(command -v python3) $(python3 -V 2>&1)"
  cd "$OUT" && nice -n 19 env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 python3 -B "$OUT/tools/ll5d_regrade_capture.py" --deploy "$D" --staged "$STAGED" --unfolds "$U" \
    --constraint "$CONSTRAINT" --list "$OUT/tools/hpss_ll5d_u_list.tsv" --out "$OUT/capture" )
rc=$?
echo "== capture end $(date -u +%FT%TZ) rc=$rc"
ls -l "$OUT/capture"; (cd "$OUT/capture" && sha256sum ./*) 2>&1
n=$(git -C "$D" status --porcelain --untracked-files=all | wc -l); echo "deploy porcelain lines after $n"
[ "$rc" -eq 0 ] || finish "$rc"
(cd "$OUT" && tar czf post.tar.gz logs capture tools && sha256sum post.tar.gz)
finish 0
