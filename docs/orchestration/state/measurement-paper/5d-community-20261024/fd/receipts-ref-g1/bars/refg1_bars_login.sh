#!/bin/bash
# REF-G1 reader, connect 1 of 2: the BARS only (REF-G1-BINDING-2.md rulings 3, 4 and 6; the director's ruling of
# 2026-11-05: bars, then a merge of bars.json to main, then the read). On a login node, 0 node-h. The batch must be
# DONE (job 60857388, 233 PASS) with its SHA256SUMS unchanged (6a4c1929...). A fresh clean clone at M into $R/deploy-M
# (porcelain --ignored 0 and the 5 bound blobs), then the bound reader's bars mode (ref_g1_read.py, blob e49ab974,
# docstring line 5: "bars --run DIR --out DIR/bars.json ... From the paired replica and universe differences alone,
# never the central Delta"):
#   /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -B nd-unfolding/ref_g1/ref_g1_read.py bars \
#       --run <batch>/units --out $R/bars.json
# in the root_6_28 environment, nice 19, idle I/O, 4 threads. No read mode runs here, so no central Delta is formed.
# Porcelain --ignored before and after. Writes only under a NEW $R (bars.json, bars.log, bars.done, the clone, this
# script's copy). No set -u. Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
B=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
R=/pscratch/sd/j/josephrb/ref-g1-20261105/read
D=$R/deploy-M
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$R" ] && [ -x "$PY" ] && [ -s "$B/DONE" ] || bail
mkdir -p "$R" || bail
exec > "$R/bars.log" 2>&1
finish() { echo "refg1 bars rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/bars.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "bars script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/refg1_bars_login.sh"
done_rec=$(dd if="$B/DONE" iflag=noatime status=none); sums=$(dd if="$B/SHA256SUMS" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "batch DONE: $done_rec; SHA256SUMS sha256 $sums"
[ "$done_rec" = '{"units": 233, "pass": 233, "job": "60857388", "porcelain_after": 0}' ] \
  && [ "$sums" = 6a4c192980bfa337a312381d5862d9598efa4df7ace00d80d587aa2858f47882 ] || { echo "STOP: the batch is not the accepted one"; finish 4; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
cfe089d466fa8cb1926d6665fbae65b5d269eaeb nd-unfolding/ref_g1/ref_g1.py
e49ab974598ea3d15663f61da538fad3c9c8f12a nd-unfolding/ref_g1/ref_g1_read.py
2a14b22f169b9a5e616a5498dcba79c682d6766b nd-unfolding/ref_g1/config.json
c68198177807a39d41114c8286edd3d23bc6ab18 nd-unfolding/ref_g1/test_ref_g1.py
4ad3b92570b2196737df57944f94300a90d9ecc5 nd-unfolding/ref_g1/ref_g1_mutation.py
BLOBS
echo "bound blobs: 5 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
  echo "interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))'); threads 4; nice 19; ionice idle"
  cd "$D" && nice -n 19 ionice -c3 /usr/bin/time -v -o "$R/bars.time" "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py bars \
      --run "$B/units" --out "$R/bars.json"
)
rc=$?
echo "bars rc=$rc"
grep -E 'Elapsed|Maximum resident' "$R/bars.time"
[ -s "$R/bars.json" ] && echo "bars.json sha256 $(sha256sum "$R/bars.json" | cut -d' ' -f1)"
[ -e "$R/readout.json" ] && echo "UNEXPECTED: a readout.json exists beside the bars"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
[ $rc = 0 ] && [ -s "$R/bars.json" ] || { echo "STOP: the bars step did not complete (to the director, unrepaired)"; finish 1; }
finish 0
