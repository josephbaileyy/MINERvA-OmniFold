#!/bin/bash
# The note figure's "rms" -> "SD" relabel (DECISION-20261116-joseph-paper-batch.md item 16; the methods-short
# FOLLOW-UP-DURING-BEN-REVIEW.md row 2): one login-node connect, no Slurm, 0 node-h, the restyle's method
# (fig-restyle-20261031/DECLARATION.md sections 3-4) for one figure. Three arms, each compare_to_paper_fullcov.py
# through boxes.py and the restyle's capture.py, with run-a2's argv (E_R and the published covariance) and only the
# output paths changed:
#   before  the installed figure's producer, git archive of db5276148 (fig-restyle's bound commit), --style restyle-2026-10
#   off     the package's producer at PKG, the same argv          after  the same, with --sd-label
# Each arm's working directory, TMPDIR and MPLCONFIGDIR are its own; nothing is written outside $W and $LOG (a file under
# the shared checkout's 2d-unfolding or docs, the deploy or the base tree newer than the marker is a STOP). E_R and the
# published covariance are hashed O_NOATIME before the arms and must be their pinned digests; the producers then read
# them plainly through ROOT, as run-a2 did, and capture.py hashes each file named in argv (plain reads, as in run-a2).
# The fence is RE-2-shapes rev 3's, verbatim, run at the start and again before the arms. The checks run on the laptop
# after the fetch (check_sd.py; README.md section 3). Not under set -u (conda).
# Run: setsid nohup bash /dev/shm/josephrb-pullsd.sh >/dev/null 2>&1 </dev/null &
PKG=__PKG__                                                                     # the package commit
BASE=db5276148d0097665800d3992f918d2f4e5e98b0                                   # fig-restyle-20261031's bound commit
P=/pscratch/sd/j/josephrb
W=$P/note-pullsd-20261117; DEP=$W/deploy
A=$P/MINERvA-OmniFold                         # the shared checkout: the producer's ANC_DIR; read, never written
X=$P/2d-closeout-re2-20261023/partb/out/ER/xsec.root
XSHA=a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef               # run-a2/after/logs/inputs.sha256
ANC=$A/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
ANCSHA=6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3             # run-a2/after/logs/inputs.sha256
PS=docs/orchestration/state/2d-closeout/stageF/methods/pull-sd-relabel-20261117
RT=docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/tools
SHA_CPF=__SHA_CPF__; SHA_BOXES=__SHA_BOXES__; SHA_CAPTURE=__SHA_CAPTURE__; SHA_ARTISTS=__SHA_ARTISTS__
SHA_OVERLAP=__SHA_OVERLAP__; SHA_RESTYLE=__SHA_RESTYLE__; SHA_TECHNOTE=__SHA_TECHNOTE__; SHA_RC=__SHA_RC__
SHA_CPF_BASE=1dd5ff52d0c140921a3bcc411bd4108337dbe756c43bffc2c707eb2a8f633314     # the installed figure's producer
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
URL=https://github.com/josephbaileyy/MINERvA-OmniFold
LOG=/dev/shm/josephrb-pullsd.log
stop() { echo "STOP $*"; echo "PULLSD INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; cp "$LOG" "$W/logs/connect.log" 2>/dev/null; echo DONE; exit 2; }
early() { printf 'STOP %s\nPULLSD INVALID (connect)\nDONE\n' "$*" >> "$LOG"; exit 2; }   # before the log is this script's stdout
[[ $PKG =~ ^[0-9a-f]{40}$ ]] || early "PKG is not filled"
for v in "$SHA_CPF" "$SHA_BOXES" "$SHA_CAPTURE" "$SHA_ARTISTS" "$SHA_OVERLAP" "$SHA_RESTYLE" "$SHA_TECHNOTE" "$SHA_RC"; do
  [[ $v =~ ^[0-9a-f]{64}$ ]] || early "a placeholder is not filled"; done
[ -e "$W" ] && early "$W exists"
exec >> "$LOG" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ PKG=$PKG BASE=$BASE nproc=$(nproc)"
# ---- the fence: at the start, and again before the arms
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
# ---- the deploy, the base producers, the code, the environment, the inputs
mkdir -p "$W/logs" "$W/tmp" || stop mkdir
git clone --quiet "$URL" "$DEP" && git -C "$DEP" checkout --quiet --detach "$PKG" || stop clone
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); h=$(git -C "$DEP" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$PKG" ] || stop "deploy not clean at PKG"
mkdir -p "$W/base" && git -C "$DEP" archive "$BASE" technote_style.py 2d-unfolding | tar -x -C "$W/base" || stop "base tree"
cat > "$W/code.sha256" <<SUMS
$SHA_CPF  $DEP/2d-unfolding/compare_to_paper_fullcov.py
$SHA_BOXES  $DEP/$PS/boxes.py
$SHA_CAPTURE  $DEP/$RT/capture.py
$SHA_ARTISTS  $DEP/$RT/artists.py
$SHA_OVERLAP  $DEP/$RT/overlap.py
$SHA_RESTYLE  $DEP/2d-unfolding/restyle_2026_10.py
$SHA_TECHNOTE  $DEP/technote_style.py
$SHA_RC  $DEP/2d-unfolding/uq/reported_cells.py
$SHA_CPF_BASE  $W/base/2d-unfolding/compare_to_paper_fullcov.py
$SHA_RESTYLE  $W/base/2d-unfolding/restyle_2026_10.py
$SHA_TECHNOTE  $W/base/technote_style.py
$SHA_RC  $W/base/2d-unfolding/uq/reported_cells.py
SUMS
sha256sum -c "$W/code.sha256" || stop "a code file is not its pinned sha256"
source "$DEP/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 MNV_REPO=$A OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset TECHNOTE_DARK
python3 -c "import sys, ROOT, matplotlib, numpy; print('python', sys.version.split()[0]); print('ROOT', ROOT.gROOT.GetVersion()); print('matplotlib', matplotlib.__version__); print('numpy', numpy.__version__)" > "$W/environment.txt" 2>&1 \
  || { cat "$W/environment.txt"; stop "environment did not activate (python, ROOT, matplotlib, numpy)"; }
hostname >> "$W/environment.txt"; cat "$W/environment.txt"
nsha() { python3 -c "
import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 22)
    if not b: break
    h.update(b)
os.close(fd); print(h.hexdigest())" "$1"; }
gx=$(nsha "$X"); ga=$(nsha "$ANC"); printf '%s  %s\n%s  %s\n' "$gx" "$X" "$ga" "$ANC" > "$W/inputs.sha256"; cat "$W/inputs.sha256"
[ "$gx" = "$XSHA" ] || stop "E_R is not its pinned digest"
[ "$ga" = "$ANCSHA" ] || stop "the published covariance is not its pinned digest"
# ---- the arms
fence arms
touch "$W/marker"
arm() {  # arm <name> <deploy> [extra producer args]
  local O=$W/$1 D=$2 rc t0; shift 2
  mkdir -p "$O"/{out,capture,tmp,mpl,logs}
  t0=$(date +%s)
  (cd "$O" && TMPDIR=$O/tmp MPLCONFIGDIR=$O/mpl XDG_CACHE_HOME=$O/tmp timeout 300 nice -n 19 python3 -I -B "$DEP/$PS/boxes.py" \
     "$O/capture/pull_full" "$D" "$D/2d-unfolding/compare_to_paper_fullcov.py" --ours "$X" --out-prefix "$O/out/MEFHC_5iter" \
     --style restyle-2026-10 "$@" > "$O/logs/pull_full.log" 2>&1); rc=$?
  printf 'step\trc\tseconds\tdeploy\targv\npull_full\t%s\t%s\t%s\t%s\n' "$rc" "$(( $(date +%s) - t0 ))" "$D" \
    "--ours $X --out-prefix $O/out/MEFHC_5iter --style restyle-2026-10 $*" > "$O/logs/steps.tsv"
  echo "arm $(basename "$O") rc=$rc"; tail -3 "$O/logs/pull_full.log"
  [ "$rc" = 0 ] || stop "arm $(basename "$O") rc=$rc (see $O/logs/pull_full.log)"
  [ -s "$O/out/MEFHC_5iter_pull_full.pdf" ] || stop "arm $(basename "$O") wrote no PDF"
}
arm before "$W/base"
arm off "$DEP"
arm after "$DEP" --sd-label
n=$(find "$A/2d-unfolding" "$A/docs" "$DEP" "$W/base" -newer "$W/marker" -type f 2>/dev/null | awk 'END {print NR}')
echo "files under the shared checkout's 2d-unfolding and docs, the deploy and the base tree newer than the marker: $n"
[ "$n" = 0 ] || stop "a stray write ($n file(s))"
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); echo "deploy porcelain after: $n"
[ "$n" = 0 ] || stop "the deploy is not clean after the arms"
(cd "$W" && find before off after -type f ! -name '*.png' ! -path '*/tmp/*' ! -path '*/mpl/*' -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS) || stop "SHA256SUMS"
echo "PULLSD CONNECT PASS: three arms drawn (rc 0), inputs as pinned, no stray write; the checks run on the laptop (check_sd.py)"
cp "$LOG" "$W/logs/connect.log" 2>/dev/null
echo "end=$(date -u +%FT%TZ)"; echo DONE
