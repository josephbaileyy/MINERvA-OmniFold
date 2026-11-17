#!/bin/bash
# D2 mu_max connect (the director's design rulings of 2026-11-16; lrows-g README:121-127's "not covered"): per truth
# (G18, AR23), mu_max of G = LL5D's band:GEANT_Neutron + band:GEANT_Proton rebuilt at T from that truth's products,
# against C_T (all; primary) and C_T^- (secondary), by fd/receipts-ll5d/mumax/ll5d_mumax.py, which reads only through
# LL5D's own functions (ll5d_b.setup, remade; products O_NOATIME) and lrows-g's geant_full.summarize. Controls in the
# script: made_from and the products' O_NOATIME digest equal LL5D's null records'; the removal control on the G used.
# The S1 reproduction control (geant_full's 0.081346592967004 and 0.04097223733043594) ran locally and is committed.
# Login node, setup_salloc_env (python 3.11, as LL5D's readout ran). Every input outside this connect's own deploy is
# read O_NOATIME (the deploy's definition and cmodel json are read plainly by LL5D's setup, made_from and cmodel_parts);
# atime-pre and atime-post over the watch list (`ll5d_mumax.py inputs`: the staged S1, the constraint, both truths'
# null-role products, plus the two null records; the pending bulk HPSS copy of $U) must show none moved, else a STOP.
# The fence is RE-2-shapes rev 3's, verbatim. Writes only under $W and $LOG. 0 node-h. Not under set -u (conda).
# Run: setsid nohup bash /dev/shm/josephrb-g2r-d2.sh >/dev/null 2>&1 </dev/null &
PKG=__PKG__                                  # the lane's package commit (branch lane/d2-mumax-20261116)
P=/pscratch/sd/j/josephrb
W=$P/cov2d-mumax-20261116; DEP=$W/deploy
U=$P/ll5d-unfolds-r2                         # LL5D's products (read O_NOATIME)
STAGED=$P/fd-1b-inv-20261101/i0/in
CONSTRAINT=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
NW=$P/ll5d-null-r1
NULLG18=73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2   # receipts-ll5d/null/node/null-g18.json
NULLAR23=a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933  # receipts-ll5d/null/node/null-ar23.json
MX=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ll5d/mumax
SHA_MUMAX=__SHA_MUMAX__; SHA_LL5DB=__SHA_LL5DB__; SHA_GF=__SHA_GF__
FIGMARK=$P/note-figstyle-20261114/RUNNING   # director-helper-2's group C figure connects hold this while they run
URL=https://github.com/josephbaileyy/MINERvA-OmniFold
LOG=/dev/shm/josephrb-g2r-d2.log
stop() { echo "STOP $*"; echo "D2 INVALID (connect)"; echo "end=$(date -u +%FT%TZ)"; cp "$LOG" "$W/logs/connect.log" 2>/dev/null; echo DONE; exit 2; }
[[ $PKG =~ ^[0-9a-f]{40}$ ]] || { echo "STOP PKG is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }
for v in "$SHA_MUMAX" "$SHA_LL5DB" "$SHA_GF"; do [[ $v =~ ^[0-9a-f]{64}$ ]] || { echo "STOP a placeholder is not filled" >> "$LOG"; echo DONE >> "$LOG"; exit 2; }; done
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
# ---- the deploy, the code, the environment, the null records
mkdir -p "$W/logs" "$W/tmp" || stop mkdir
git clone --quiet "$URL" "$DEP" && git -C "$DEP" checkout --quiet --detach "$PKG" || stop clone
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); h=$(git -C "$DEP" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$PKG" ] || stop "deploy not clean at PKG"
cat > "$W/code.sha256" <<SUMS
$SHA_MUMAX  $MX/ll5d_mumax.py
$SHA_LL5DB  nd-unfolding/ll5d_b.py
$SHA_GF  docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g/geant_full.py
SUMS
(cd "$DEP" && sha256sum -c "$W/code.sha256") || stop "a code file is not its pinned sha256"
source "$DEP/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1
{ python3 -c "import sys, numpy; print('python', sys.version.split()[0]); print('numpy', numpy.__version__)"; hostname; nproc; } > "$W/environment.txt"; cat "$W/environment.txt"
nsha() { python3 -c "
import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 22)
    if not b: break
    h.update(b)
os.close(fd); print(h.hexdigest())" "$1"; }
[ "$(nsha "$NW/null-g18.json")" = "$NULLG18" ] || stop "null-g18.json is not the committed record"
[ "$(nsha "$NW/null-ar23.json")" = "$NULLAR23" ] || stop "null-ar23.json is not the committed record"
echo "null records OK: g18 $NULLG18 ar23 $NULLAR23"
ARGS=(--staged "$STAGED" --definition "$DEP/nd-unfolding/pv-ladder/readouts/h2_definition.json" --unfolds "$U"
      --cmodel-json "$DEP/nd-unfolding/pv-ladder/readouts/cmodel_5d.json" --flux-constraint "$CONSTRAINT")
(cd "$DEP" && python3 -I -B "$MX/ll5d_mumax.py" inputs "${ARGS[@]}" --truth g18 --truth ar23) > "$W/inputs.txt" || stop "listing the declared inputs"
printf '%s\n%s\n' "$NW/null-g18.json" "$NW/null-ar23.json" >> "$W/inputs.txt"
echo "declared inputs: $(awk 'END {print NR}' "$W/inputs.txt")"
atimes() { python3 -c "
import os, sys
for p in open(sys.argv[1]).read().split():
    print(os.stat(p).st_atime_ns, p)" "$W/inputs.txt"; }
atimes > "$W/atime-pre.txt" || stop "atime-pre"
# ---- the run
echo "mumax start=$(date -u +%FT%TZ)"
(cd "$DEP" && /usr/bin/time -f "mumax wall %e s rss %M KB" python3 -I -B "$MX/ll5d_mumax.py" ll5d "${ARGS[@]}" \
   --null "$NW/null-g18.json" --null "$NW/null-ar23.json" --out "$W/mumax.json") > "$W/logs/mumax.log" 2>&1; rc=$?
echo "mumax rc=$rc end=$(date -u +%FT%TZ)"; cat "$W/logs/mumax.log"
atimes > "$W/atime-post.txt" || stop "atime-post"
moved=$(python3 -c "
import sys
a = dict(l.split(' ', 1)[::-1] for l in open(sys.argv[1]).read().splitlines())
b = dict(l.split(' ', 1)[::-1] for l in open(sys.argv[2]).read().splitlines())
print(sum(1 for k in a if a[k] != b.get(k)))" "$W/atime-pre.txt" "$W/atime-post.txt")
echo "atime: $(awk 'END {print NR}' "$W/atime-pre.txt") declared inputs, moved $moved"
n=$(git -C "$DEP" status --porcelain | awk 'END {print NR}'); echo "deploy porcelain after: $n"
(cd "$W" && sha256sum environment.txt code.sha256 inputs.txt atime-pre.txt atime-post.txt mumax.json logs/mumax.log) > "$W/out.sha256" 2>&1; cat "$W/out.sha256"
[ "$rc" = 0 ] || stop "mumax rc=$rc (see $W/logs/mumax.log)"
[ "$moved" = 0 ] || stop "an input's atime moved ($moved)"
[ "$n" = 0 ] || stop "the deploy is not clean after the run"
echo "D2 PASS: controls held, mu_max recorded for g18 and ar23, no atime moved"
cp "$LOG" "$W/logs/connect.log" 2>/dev/null
echo "end=$(date -u +%FT%TZ)"; echo DONE
