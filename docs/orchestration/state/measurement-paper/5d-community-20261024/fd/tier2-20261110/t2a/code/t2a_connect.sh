#!/bin/bash
# T2A's capture connect (T2A-COV2D-SPLIT-DECLARATION.md §2; T2-BINDING-1.md ruling 1), on one Perlmutter login node, in
# the foreground, 0 node-h, after cov2d's review of the tool commit, the director's go on this script's, the wrapper's
# and the launcher's sha256s, and cov2d_fence.sh CLEAR.
# For each tune, AR23 then G18, phase S is rerun unchanged through capture_e.py, in the template of the committed
# connect-s-<T>.sh (readout/AR23/phase-s/, readout/G18/phase-s-2/): the same /dev/shm path (score_<T>.json records the
# deploy's module paths), a fresh clone at the tune's score M, READOUT-SHA, the null-on-main check, the MAT pin and the
# MnvH1D preflight, nice 19, taskset -c 8-11, threads 1, porcelain and blobs before and after.
# Per tune, in order, each failure a stop for that tune (it is reported as not made; nothing is repaired):
#   $W absent; the 300 toys' xsec.root present and non-empty, by stat of each explicit path (no directory listed);
#   the clone at M clean with HEAD = M and cov2d_readout.py at its recorded sha256; origin/main's null_<T>.json at D;
#   the committed score_<T>.json from origin/main at its recorded sha256; capture_e.py from the tool commit at its
#   approved sha256; then the capture (its own A0: rc 0 OK, 8 STOP, 9 FAILED).
# Outputs are copied to $OUT/<T>/ on pscratch and checked by sha256, then $W is removed. Writes only under $OUT and $W.
# No set -u (it kills setup_salloc_env.sh). Launched from a /dev/shm copy of itself, whose path is $1; deleted at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/t2a-20261110
TOOLC=edd1bed05f32d7e2cc05d77f940b79a125b38a29
CAPTURE_SHA=dfee305eb95a64ab8033a1b44808b53cf778552f19b9f30402959003ed61ae7b
RUN_DIR=/pscratch/sd/j/josephrb/cov2d-run-20261104
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with the MAT build (setup_salloc_env.sh)
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
RUN="nice -n 19 taskset -c 8-11"
REC=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout
bail() { rm -f -- "$SELF"; exit 9; }                 # a precondition failed: nothing written
[ ! -e "$OUT" ] || bail
q=$(squeue --me -h -o '%i|%j|%T') || bail           # fails closed (the fence, again, at the connect)
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && bail
mkdir -p "$OUT/logs" || bail
exec > "$OUT/logs/connect.log" 2>&1
finish() { echo "t2a connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/t2a_connect.sh"
echo "squeue --me before:"; printf '%s\n' "$q" | sed '/^$/d; s/^/  /'

one() {   # one tune: T M D READOUT_SHA SCORE_SHA SEED0
  local T=$1 M=$2 D=$3 READOUT_SHA=$4 SCORE_SHA=$5 SEED0=$6
  local W=/dev/shm/josephrb-cov2d-s-$T; local DD=$W/deploy; local O=$OUT/$T
  echo "== $T: M=$M D=$D"
  [ -e "$W" ] && { echo "STOP $T: $W exists"; return 2; }
  # the toys, by stat of each explicit path (stat does not move atime)
  local n=0 bad=0 s p
  for ((i = 0; i < 300; i++)); do
    p="$RUN_DIR/out/T_${T}_$((SEED0 + i))/xsec.root"
    s=$(stat -c %s "$p" 2>/dev/null) && [ "$s" -gt 0 ] && n=$((n + 1)) || { bad=$((bad + 1)); [ $bad -le 5 ] && echo "missing or empty: $p"; }
  done
  echo "toys present and non-empty: $n of 300"
  [ "$n" = 300 ] || { echo "STOP $T: $bad toy products missing or empty"; return 2; }
  mkdir "$W" "$W/tmp" "$W/out" "$W/tool" "$W/ref" || { echo "STOP $T: mkdir"; return 2; }
  export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  local rcT=2
  (
    stop() { echo "STOP $T $*"; exit 2; }
    git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" -c advice.detachedHead=false checkout --quiet --detach "$M" || stop clone
    n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "porcelain_before_lines=$n head=$h"
    [ "$n" = 0 ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
    got=$(sha256sum "$DD/2d-unfolding/cov2d/cov2d_readout.py" | cut -c1-64)
    [ "$got" = "$READOUT_SHA" ] && echo "READOUT-SHA OK $got" || stop "cov2d_readout.py is $got"
    (cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.before"
    echo "origin/main=$(git -C "$DD" rev-parse origin/main)"
    g=$(git -C "$DD" show "origin/main:$REC/$T/null_$T.json" | sha256sum | cut -c1-64)
    [ "$g" = "$D" ] && echo "NULL-ON-MAIN OK $g" || stop "origin/main null_$T.json is $g, not $D"
    git -C "$DD" show "origin/main:$REC/$T/score_$T.json" > "$W/ref/score_$T.json" || stop "git show score_$T.json"
    g=$(sha256sum "$W/ref/score_$T.json" | cut -c1-64)
    [ "$g" = "$SCORE_SHA" ] && echo "SCORE-ON-MAIN OK $g" || stop "origin/main score_$T.json is $g, not $SCORE_SHA"
    git -C "$DD" cat-file -e "$TOOLC^{commit}" || stop "the tool commit is not in the clone"
    git -C "$DD" show "$TOOLC:2d-unfolding/cov2d/t2a/capture_e.py" > "$W/tool/capture_e.py" || stop "git show capture_e.py"
    g=$(sha256sum "$W/tool/capture_e.py" | cut -c1-64)
    [ "$g" = "$CAPTURE_SHA" ] && echo "CAPTURE-SHA OK $g" || stop "capture_e.py is $g, not $CAPTURE_SHA"
    (
      "$PY310" -B -c "import sys; sys.path.insert(0, '$DD/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" || exit 7
      source "$A/setup_salloc_env.sh" > /dev/null 2>&1 || exit 3
      export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
      echo "python=$(command -v python) TMPDIR=$TMPDIR"
      python -c "import sys, numpy, ROOT; print(sys.version.split()[0], 'numpy', numpy.__version__, 'ROOT', ROOT.gROOT.GetVersion())" || exit 4
      python - <<'PYEOF' || exit 5
import hashlib, os, ROOT
src = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_1A.root"
fd = os.open(src, os.O_RDONLY | os.O_NOATIME); data = b""
while True:
  b = os.read(fd, 1 << 24)
  if not b: break
  data += b
os.close(fd)
print("MAT preflight file:", src, "sha256", hashlib.sha256(data).hexdigest())
dst = os.path.join(os.environ["TMPDIR"], "mat_preflight.root"); open(dst, "wb").write(data)
f = ROOT.TFile.Open(dst); h = f.Get("pTmu_reweightedflux_integrated")
print("MAT preflight:", type(h).__name__, h.ClassName(), h.GetNbinsX(), "bins")
assert h.ClassName().startswith("PlotUtils::MnvH1D"), h.ClassName()
os.remove(dst)
PYEOF
      cd "$DD/2d-unfolding/cov2d" && $RUN /usr/bin/time -v python -B "$W/tool/capture_e.py" --cov2d-dir "$DD/2d-unfolding/cov2d" \
        --truth "$T" --null-digest "$D" --out "$W/out" --ref-score "$W/ref/score_$T.json" --ref-score-sha256 "$SCORE_SHA"
    ) > "$W/capture_$T.log" 2>&1; rc=$?
    grep -v '^Warning in <TInterpreter::ReadRootmapFile>' "$W/capture_$T.log" | tail -40
    echo "CAPTURE $T rc=$rc $(grep -E "^T2A-CAPTURE $T " "$W/capture_$T.log" | tail -1)"
    n=$(git -C "$DD" status --porcelain | wc -l); echo "porcelain_after_lines=$n head=$(git -C "$DD" rev-parse HEAD)"
    (cd "$DD" && git ls-tree -r HEAD 2d-unfolding/cov2d | grep -v __pycache__) > "$W/blobs.after"
    cmp -s "$W/blobs.before" "$W/blobs.after" && echo "blobs unchanged" || echo "blobs CHANGED"
    exit $rc
  ); rcT=$?
  # keep the records on pscratch, check them, then remove $W
  mkdir -p "$O" && cp -p "$W"/out/* "$W"/capture_$T.log "$W"/blobs.before "$W"/blobs.after "$W"/ref/score_$T.json "$O"/ 2>/dev/null
  (cd "$W/out" && sha256sum * 2>/dev/null) > "$O/out.sha256"
  if [ -s "$O/out.sha256" ]; then
    (cd "$O" && sha256sum -c --quiet out.sha256) && echo "COPY $T verified ($(wc -l < "$O/out.sha256") files)" || { echo "COPY $T NOT VERIFIED"; rcT=6; }
  else
    echo "COPY $T: phase S wrote no outputs"
  fi
  echo "removal: host=$(hostname) $(date -u +%FT%TZ) $(du -sh "$W" 2>/dev/null | cut -f1) $W"; rm -rf "$W"; echo "rm rc=$?"
  [ -e "$W" ] && echo "STILL PRESENT: $W"
  echo "TUNE $T rc=$rcT"
  return $rcT
}

one AR23 ac25b66533788ceb18b1d4e5add259c53b216669 80274e52c23365e5c6f84fad977576e54507bf186e1d04a8da8d596a75b0ac76 \
    d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297 fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1 5730000
rA=$?
one G18 b1d56e4f08e62983784e34b2278f38a09a68eca0 6bd5259d61b062af7b3a8b09af78fc544e3eba48e35a062a28fdcd923b90f6e0 \
    0c3ad137be128691cce7bbe3ec72493b76791e761e6cd897f75aaf0a4fc7444f 849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec 5720000
rG=$?
echo "SUMMARY AR23 rc=$rA G18 rc=$rG"
(cd "$OUT" && tar czf post.tar.gz logs/connect.log logs/t2a_connect.sh AR23 G18 2>/dev/null; sha256sum post.tar.gz)
[ "$rA" = 0 ] && [ "$rG" = 0 ] && finish 0
finish 1
