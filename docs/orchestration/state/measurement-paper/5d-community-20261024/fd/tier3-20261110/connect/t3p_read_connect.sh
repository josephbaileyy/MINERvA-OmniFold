#!/bin/bash
# T3: the read connect (T3-CONNECT-PLAN.md section 6 row c5; declaration section 7: after every job has completed, one
# reader run in a clean clone at the bound commit). Derived from FD-PRR's reviewed read connect prr_read.sh (42716ca4,
# committed at fd/receipts-prr/read/cluster/), with this lane's sacct fence (t3p_submit.sh 50e86da3) in place of squeue.
# On a Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit.
#   usage: t3p_read_connect.sh <self> <window_end_epoch> <fence prefixes, comma-separated>
# In order, each failure a final stop before the read:
#   the window: now <= window_end (the epoch the launcher computed from date, never typed);
#   the fence: no job of this user whose name starts with a fenced prefix or t3p_ is in a non-terminal state, by sacct;
#   sacct shows t3p_dry 61726250, t3p_q3 61728686 and t3p_floor 61731751 COMPLETED;
#   log-dry, log-q3 and log-floor each hold DONE and no STOP or FAILED; $OUT/read, $OUT/deploy-read, $OUT/fetch-read,
#     $OUT/fetch-read.tar, $OUT/fetch-read.sums and this connect's log and done are absent;
#   a fresh clone at M_V1 into $OUT/deploy-read, clean (porcelain --ignored 0), the six bound T3 files, the declaration
#     and addendum V1 at their bound sha256;
#   the 36 products against log-floor/SHA256SUMS (the floor job hashed every product under runs/ at its end), and
#     log-dry's and log-q3's SHA256SUMS still hold.
# Then the read: M_V1's t3p_read.main(["--run", $OUT, "--repo", $D, "--out", $OUT/read]), unchanged, under root_6_28's
# python with -I -B, nice 19, ionice idle, every thread cap at 1 and PYTHONHASHSEED=0, inside REF-G1's read guard
# (ref_g1.read_guards(ref_g1.PROTECTED, ($D, $OUT), root=False)): a plain Python read under /pscratch or /global/cfs
# outside the deploy and $OUT is refused. t3p_read's own stdout (its readout text) goes to /dev/null; this log prints the
# verdict only, so no reading is in the log. t3p_read writes only $OUT/read/ (readout.json and readout.txt).
# Then the records: every regular file under logs/, log-dry/, log-q3/, log-floor/, read/ and queues/, and manifest.json,
# stage.json and fence.txt (no .npz; this connect's own log, still open, is fetched beside the tar), copied through dd iflag=noatime into $OUT/fetch-read/, each copy's sha256 equal to
# its source's, then one tar of that copy at $OUT/fetch-read.tar, whose sha256 this log prints for the fetch.
# This connect writes only $OUT/deploy-read, $OUT/read, $OUT/fetch-read, $OUT/fetch-read.tar and its own log and done.
# No set -u. Any stop is final.
SELF=$1; WEND=$2; FENCE=$3
TAG=read
M=8bb4e3b0e1028d960e39de0c202569a08a1218a0
OUT=/pscratch/sd/j/josephrb/t3p-20261121
D=$OUT/deploy-$TAG
RO=$OUT/read
FR=$OUT/fetch-$TAG
PY=$HOME/.conda/envs/root_6_28/bin/python3
JOBS="dry:61726250 q3:61728686 floor:61731751"
DECL_SHA=f96ed6f29a155e978bf449fdcb9810670202e0a3d74fb2f96afe48098b63cae1
V1_SHA=3998708a91dde4b01c3dcb1e87a7b7a45796de13da53880a0eb79a410ecc7986
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }   # a precondition failed: nothing written
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"

# ---- the fence by sacct (t3p_submit.sh's, unchanged): non-terminal = any State outside the terminal set
fence_sacct() {
  local rows bad
  rows=$(sacct -X -n -P -S now-14days -o JobID,JobName,State 2>&1) || { echo "sacct failed: $rows"; return 2; }
  bad=$(printf '%s\n' "$rows" | awk -F'|' -v pre="$FENCE,t3p_" '
    BEGIN { n = split(pre, P, ",") }
    NF >= 3 {
      st = $3; sub(/ by [0-9]+$/, "", st)
      term = (st ~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)$/)
      if (term) next
      for (i = 1; i <= n; i++) if (P[i] != "" && index($2, P[i]) == 1) { print; break }
    }')
  [ -z "$bad" ] || { echo "fenced or t3p_ jobs not terminal: $bad"; return 1; }
  return 0
}
fence_sacct > /dev/null 2>&1 || bail "fence (sacct) not clear"
[ -d "$OUT/logs" ] && [ -x "$PY" ] || bail "no $OUT/logs or no $PY"
for jj in $JOBS; do
  j=${jj%%:*}; id=${jj##*:}
  [ -s "$OUT/log-$j/DONE" ] && [ ! -e "$OUT/log-$j/STOP" ] && [ ! -e "$OUT/log-$j/FAILED" ] || bail "log-$j"
  st=$(sacct -j "$id" -X -n -P -o State 2>/dev/null | head -1)
  [ "$st" = COMPLETED ] || bail "job $id is '$st', not COMPLETED"
done
for p in "$RO" "$D" "$FR" "$FR.tar" "$FR.sums" "$OUT/logs/connect-$TAG.log" "$OUT/logs/connect-$TAG.done"; do
  [ ! -e "$p" ] || bail "$p exists"
done
LOG=$OUT/logs/connect-$TAG.log
exec > "$LOG" 2>&1
finish() { echo "t3p $TAG rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$TAG.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/t3p_${TAG}.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"
echo "== the three jobs (sacct)"
for jj in $JOBS; do sacct -j "${jj##*:}" -X -n -P -o JobID,JobName,State,ExitCode,Start,End,ElapsedRaw,NNodes | head -1; done
for jj in $JOBS; do j=${jj%%:*}; echo "log-$j/DONE: $(dd if="$OUT/log-$j/DONE" iflag=noatime status=none)"; done

# ---- the deploy: a fresh clone at M_V1, clean, the bound bytes
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-$TAG.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_V1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
( cd "$D/nd-unfolding/tier3" && sha256sum -c ) <<SUMS || { echo "STOP: the T3 files are not the bound ones"; finish 9; }
4a685bde238dcc6dc25e9b1121029994f33becafab486cbec1a7bf846206bf84  t3p_arms.py
e27bf07a3e2c60320a749355eaedceed5a36574d2d8fa83675bd4b4721985bd2  t3p_probe.py
f4c221dda95fbbdf2318f7fcdde57b9e1b7fb265e85b13e1dea15341cf069295  t3p_read.py
a21ad29f35a71e46c1b286ca6ae96128f01c482cbd30aac5133d3e4729d2de3c  sbatch_t3p.sh
4879178f4f9783f011f8a5992273e0b34a3d022bb822edf688051f038e642aa8  test_t3p.py
ae9667bc71819f092a7f61ae6d58ed4e7659ea4b0fea08de299c10462d738001  t3p_mutation.py
SUMS
T3DIR="$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier3-20261110"
decl=$(sha256sum "$T3DIR/T3-PIPELINE-TESTS-DECLARATION.md" | cut -d' ' -f1); echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }
v1=$(sha256sum "$T3DIR/T3-ADDENDUM-V1.md" | cut -d' ' -f1); echo "addendum V1 sha256 $v1"
[ "$v1" = "$V1_SHA" ] || { echo "STOP: addendum V1 is not the bound one"; finish 9; }

# ---- the products at the jobs' own records
np=$(grep -c '\.npz$' "$OUT/log-floor/SHA256SUMS"); echo "log-floor/SHA256SUMS: $np products"
[ "$np" -eq 36 ] || { echo "STOP: log-floor/SHA256SUMS does not list 36 products"; finish 9; }
for j in dry q3 floor; do
  ( cd "$OUT" && sha256sum --quiet -c "log-$j/SHA256SUMS" ) || { echo "STOP: the products are not log-$j/SHA256SUMS's"; finish 9; }
  echo "log-$j/SHA256SUMS: OK ($(grep -c '\.npz$' "$OUT/log-$j/SHA256SUMS") lines)"
done
na=$(find "$OUT/runs" -type f -name '*.npz' | wc -l); echo "npz files under runs/: $na"
[ "$na" -eq 36 ] || { echo "STOP: runs/ does not hold exactly 36 products"; finish 9; }

# ---- the read: M_V1's t3p_read.main, unchanged, inside REF-G1's read guard; its stdout to /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONHASHSEED=0
echo "threads: OMP=1 OPENBLAS=1 MKL=1 NUMEXPR=1 VECLIB=1; nice 19; ionice idle; python $("$PY" -c 'import sys; print(sys.version.split()[0])')"
( cd "$D" && nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B -c '
import contextlib, json, os, sys
from pathlib import Path
D, OUT, RO = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for p in ("nd-unfolding/tier3", "nd-unfolding/prior_retention", "nd-unfolding", "nd-unfolding/ref_g1"):
    sys.path.insert(0, str(D / p))
import t3p_read, ref_g1
assert Path(t3p_read.__file__).resolve().is_relative_to(D.resolve()), t3p_read.__file__
with ref_g1.read_guards(ref_g1.PROTECTED, (D, OUT), root=False):
    with open(os.devnull, "w") as null, contextlib.redirect_stdout(null):
        rc = t3p_read.main(["--run", str(OUT), "--repo", str(D), "--out", str(RO)])
print(json.dumps({"verdict": json.loads((RO / "readout.json").read_text())["verdict"]}), flush=True)
print("t3p_read rc", rc, flush=True)
sys.exit(rc)
' "$D" "$OUT" "$RO" )
rc=$?
echo "read rc=$rc"
ls -la "$RO" 2>&1
for f in readout.json readout.txt; do
  [ -e "$RO/$f" ] && echo "$f sha256 $(dd if="$RO/$f" iflag=noatime status=none | sha256sum | cut -d' ' -f1) bytes $(stat -c %s "$RO/$f")"
done
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }

# ---- the records for the fetch: dd iflag=noatime copies, each checked, then one tar
echo "== records"
date -u +%FT%TZ
mkdir "$FR" || { echo "STOP: mkdir $FR"; finish 9; }
fail=0; nf=0
while IFS= read -r -d '' src; do
  rel=${src#"$OUT"/}
  mkdir -p "$FR/$(dirname "$rel")"
  dd if="$src" of="$FR/$rel" iflag=noatime status=none || { echo "copy failed: $rel"; fail=1; continue; }
  a=$(dd if="$src" iflag=noatime status=none | sha256sum | cut -d' ' -f1); b=$(sha256sum "$FR/$rel" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "copy differs: $rel"; fail=1; }
  echo "$b  $rel" >> "$FR.sums"; nf=$((nf + 1))
done < <(cd "$OUT" && find logs log-dry log-q3 log-floor read queues manifest.json stage.json fence.txt \
           -type f ! -name '*.npz' ! -name "connect-$TAG.log" -print0 2>/dev/null | sort -z | sed -z "s|^|$OUT/|")
[ "$fail" -eq 0 ] || { echo "STOP: a record copy failed or differs"; finish 4; }
mv "$FR.sums" "$FR/RECORDS.SHA256SUMS" || finish 4
echo "records copied: $nf files, $(du -sb "$FR" | cut -f1) bytes"
tar -C "$OUT" -cf "$FR.tar" "fetch-$TAG" || { echo "STOP: tar"; finish 4; }
echo "fetch-$TAG.tar sha256 $(sha256sum "$FR.tar" | cut -d' ' -f1) bytes $(stat -c %s "$FR.tar")"
finish $rc
