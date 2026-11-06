#!/bin/bash
# REF-G1 A1 connect 2: the READ (REF-G1-BINDING-2-A1.md ruling 4.3; A1 section 5 step 4; code at M' = 0bb9a1bf), on a
# login node, 0 node-h, under the binding's fixed conditional sequence. It refuses unless connect 1's PASS record is on
# main: in a fresh clone, `git fetch origin main`, the committed bars.json and gibu1-product.tsv (fd/receipts-ref-g1/
# a1-connect1/) hash equal to the files on pscratch, and the pin they carry is this connect's. Then, from that clone
# checked out at M' (porcelain --ignored 0, the binding's 5 blobs), the bound reader's read mode in the read directory
# beside its bars:
#   ref_g1_read.py read --run <batch>/units --bars $R/bars.json --bars-sha256 ba4b6985... --out $R/readout.json
#       --gibu1-product <gibu1 re-run>/gibu1.npz --gibu1-sha256 683b4936...
# in root_6_28, nice 19, idle I/O, 4 threads. The reader stages every declared input through O_NOATIME into
# $R/inputs-read (which must not exist). The stat (no read) of `ref_g1_read.py reads`' set plus the gibu1 product is
# taken before and after: a moved atime is a STOP. The reader's stdout (it prints R1's reading) goes to read.stdout, not
# to read.log, so the log carries no reading. Porcelain --ignored before and after. The COV2D fence refuses before
# anything is written. Writes only under $R (readout.json or STOP.json, inputs-read/, read.*, logs) and $O/deploy-read.
# No set -u. Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-g1-20261106
R=$O/read
D=$O/deploy-read
B=/pscratch/sd/j/josephrb/ref-g1-20261105/batch
M=0bb9a1bfcb462ebd171d337ae1c8b2e2d0905e93
BARS_SHA=ba4b698500d6fd3b897d172a003936f6b89c9c3add63bfd79a84b231e3745497
G1=$O/gibu1/gibu1.npz
G1_SHA=683b493652d4a1e651e8af1684de4e170f79a636761454dd219d0ffc140dace6
RC=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-g1/a1-connect1
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -s "$R/bars.json" ] && [ -s "$G1" ] && [ -x "$PY" ] && [ -s "$B/DONE" ] || bail
for x in readout.json STOP.json inputs-read read.log read.stdout read.done read.time logs-read; do [ ! -e "$R/$x" ] || bail; done
[ ! -e "$D" ] || bail
fence=$(squeue -u josephrb -h -o '%i|%j|%T') || bail                  # the COV2D fence (#798)
printf '%s\n' "$fence" | awk -F'|' '$2 ~ /^cov2d-/ {f=1} END {exit f}' || bail
LR=$R/logs-read
mkdir -p "$LR" || bail
exec > "$R/read.log" 2>&1
finish() { echo "refg1 a1 read rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/read.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "read script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$LR/refg1a1_c2_read_login.sh"
echo "COV2D fence: no cov2d-* job in squeue at $(date -u +%FT%TZ)"
done_rec=$(dd if="$B/DONE" iflag=noatime status=none); sums=$(dd if="$B/SHA256SUMS" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "batch DONE: $done_rec; SHA256SUMS sha256 $sums"
[ "$done_rec" = '{"units": 233, "pass": 233, "job": "60857388", "porcelain_after": 0}' ] \
  && [ "$sums" = 6a4c192980bfa337a312381d5862d9598efa4df7ace00d80d587aa2858f47882 ] || { echo "STOP: the batch is not the accepted one"; finish 4; }
lb=$(dd if="$R/bars.json" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
lg=$(dd if="$G1" iflag=noatime status=none | sha256sum | cut -d' ' -f1)
echo "pscratch: bars.json $lb (expected $BARS_SHA); gibu1.npz $lg (expected $G1_SHA)"
[ "$lb" = "$BARS_SHA" ] && [ "$lg" = "$G1_SHA" ] || { echo "STOP: the bars or the gibu1 product is not connect 1's"; finish 4; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$LR/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" fetch -q origin main >> "$LR/clone.log" 2>&1 || { echo "STOP: fetch origin main"; finish 3; }
mb=$(git -C "$D" show "origin/main:$RC/bars.json" 2>/dev/null | sha256sum | cut -d' ' -f1)
mp=$(git -C "$D" show "origin/main:$RC/gibu1-product.tsv" 2>/dev/null)
echo "origin/main $(git -C "$D" rev-parse origin/main): bars.json $mb; gibu1-product.tsv: $mp"
[ "$mb" = "$lb" ] || { echo "STOP: connect 1's bars.json is not on main (the read waits for the merge)"; finish 4; }
[ "$mp" = "$(printf '%s\t%s' "$G1" "$G1_SHA")" ] || { echo "STOP: the committed gibu1 pin is not this connect's"; finish 4; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M'"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
d015a352e0e1789f88f4bd45c088850453850c7f nd-unfolding/ref_g1/ref_g1.py
e045d96215ab266a8b16347ed9b03561a23658d5 nd-unfolding/ref_g1/ref_g1_read.py
245697523a76b7f2a6839f0f70569df73898886e nd-unfolding/ref_g1/config.json
820d4afdede7bf49bd4e19df3d36af1554452f36 nd-unfolding/ref_g1/test_ref_g1.py
2d29a9151d27a85f2ba3d65a48a8a744cf95302a nd-unfolding/ref_g1/ref_g1_mutation.py
BLOBS
echo "bound blobs: 5 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1
  cd "$D" && "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py reads > "$LR/reads.tsv" 2> "$LR/reads.err"
)
[ -s "$LR/reads.tsv" ] || { echo "STOP: reads failed"; cat "$LR/reads.err"; finish 4; }
{ cut -f2 "$LR/reads.tsv"; echo "$G1"; } > "$LR/watch.txt"
xargs -d '\n' stat -c '%U %a %X %s %n' < "$LR/watch.txt" > "$LR/watch-before.txt" 2>&1
echo "stat set: $(wc -l < "$LR/watch-before.txt") paths (reads' $(wc -l < "$LR/reads.tsv") and the gibu1 product); not owned by josephrb: $(awk '$1 != "josephrb"' "$LR/watch-before.txt" | wc -l)"
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
  echo "interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))'); threads 4; nice 19; ionice idle"
  cd "$D" && nice -n 19 ionice -c3 /usr/bin/time -v -o "$R/read.time" "$PY" -B nd-unfolding/ref_g1/ref_g1_read.py read \
      --run "$B/units" --bars "$R/bars.json" --bars-sha256 "$lb" --out "$R/readout.json" \
      --gibu1-product "$G1" --gibu1-sha256 "$G1_SHA" > "$R/read.stdout"
)
rc=$?
echo "read rc=$rc"
grep -E 'Elapsed|Maximum resident' "$R/read.time"
[ -s "$R/readout.json" ] && echo "readout.json sha256 $(sha256sum "$R/readout.json" | cut -d' ' -f1)"
[ -e "$R/STOP.json" ] && echo "STOP.json written: sha256 $(sha256sum "$R/STOP.json" | cut -d' ' -f1)"
echo "reader stdout (the reading; not echoed here) is $R/read.stdout"
xargs -d '\n' stat -c '%U %a %X %s %n' < "$LR/watch.txt" > "$LR/watch-after.txt" 2>&1
if cmp -s "$LR/watch-before.txt" "$LR/watch-after.txt"; then echo "stat set: no atime moved"; else echo "STOP: the stat set changed:"; diff "$LR/watch-before.txt" "$LR/watch-after.txt" | head -20; fi
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
cmp -s "$LR/watch-before.txt" "$LR/watch-after.txt" || finish 8
finish $rc
