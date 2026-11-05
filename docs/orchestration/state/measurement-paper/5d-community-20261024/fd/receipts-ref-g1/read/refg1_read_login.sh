#!/bin/bash
# REF-G1 reader, connect 2 of 2: the READ (REF-G1-BINDING-2.md rulings 3, 4 and 6; the director's ruling of 2026-11-05:
# bars, then the merge of bars.json to main (#791), then this read). On a login node, 0 node-h. It refuses unless:
#   the batch is the accepted one (DONE 233/233, SHA256SUMS 6a4c1929...);
#   $R/bars.json is present, no readout.json beside it, and its sha256 is de12c674...;
#   in a fresh clean clone at M (porcelain --ignored 0, the 5 bound blobs), `git fetch origin main` and
#   `git show origin/main:<the committed bars.json> | sha256sum` equals the local file's sha256 (bars.json on main
#   before Delta, by construction).
# Then the bound reader's read mode (ref_g1_read.py, blob e49ab974):
#   /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -B nd-unfolding/ref_g1/ref_g1_read.py read \
#       --run <batch>/units --bars $R/bars.json --bars-sha256 <that sha> --out $R/readout.json
# in the root_6_28 environment, nice 19, idle I/O, 4 threads. Porcelain --ignored before and after. Writes only
# readout.json (or STOP.json), read.log, read.stdout, read.done, read.time, clone-read.log and this script's copy under $R;
# the reader's stdout (it prints R1's reading) goes to read.stdout, not to read.log, so the log carries no reading; the clone is $R/deploy-read. No set -u.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
B=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
R=/pscratch/sd/j/josephrb/ref-g1-20261105/read
D=$R/deploy-read
BARS_SHA=de12c6745b4f5353a83ae8573c7cc75d986617f7a21d8b4ea4c5e275d8607780
BARS_PATH=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-g1/bars/bars.json
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -s "$R/bars.json" ] && [ -x "$PY" ] && [ -s "$B/DONE" ] || bail
for x in readout.json STOP.json read.log read.stdout read.done read.time clone-read.log deploy-read; do [ ! -e "$R/$x" ] || bail; done
exec > "$R/read.log" 2>&1
finish() { echo "refg1 read rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/read.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "read script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/refg1_read_login.sh"
done_rec=$(dd if="$B/DONE" iflag=noatime status=none); sums=$(dd if="$B/SHA256SUMS" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "batch DONE: $done_rec; SHA256SUMS sha256 $sums"
[ "$done_rec" = '{"units": 233, "pass": 233, "job": "60857388", "porcelain_after": 0}' ] \
  && [ "$sums" = 6a4c192980bfa337a312381d5862d9598efa4df7ace00d80d587aa2858f47882 ] || { echo "STOP: the batch is not the accepted one"; finish 4; }
loc=$(dd if="$R/bars.json" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "local bars.json sha256 $loc (expected $BARS_SHA)"
[ "$loc" = "$BARS_SHA" ] || { echo "STOP: the local bars.json is not de12c674"; finish 4; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/clone-read.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin main >> "$R/clone-read.log" 2>&1 || { echo "STOP: fetch origin main"; finish 3; }
onmain=$(git -C "$D" show "origin/main:$BARS_PATH" 2>/dev/null | sha256sum | cut -d' ' -f1)
echo "origin/main $(git -C "$D" rev-parse origin/main): $BARS_PATH sha256 $onmain"
[ "$onmain" = "$loc" ] || { echo "STOP: bars.json on origin/main is not the local file (or is not on main): the read waits for the merge"; finish 4; }
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
  cd "$D" && nice -n 19 ionice -c3 /usr/bin/time -v -o "$R/read.time" "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py read \
      --run "$B/units" --bars "$R/bars.json" --bars-sha256 "$loc" --out "$R/readout.json" > "$R/read.stdout"
)
rc=$?
echo "read rc=$rc"
grep -E 'Elapsed|Maximum resident' "$R/read.time"
[ -s "$R/readout.json" ] && echo "readout.json sha256 $(sha256sum "$R/readout.json" | cut -d' ' -f1)"
[ -e "$R/STOP.json" ] && echo "STOP.json written: sha256 $(sha256sum "$R/STOP.json" | cut -d' ' -f1)"
echo "reader stdout (the reading; not echoed here) is $R/read.stdout"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish $rc
