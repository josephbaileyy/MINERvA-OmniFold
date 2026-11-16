#!/bin/bash
# RSN J2/J3 connect (RSN-BINDING-1 ruling 3; RSN-DECLARATION.md rev 3 §6 step 4), on one Perlmutter login node, at
# 0 node-h for itself. Two steps, each run only on the director's go for this script's sha256 and the launcher's:
#   nc      after J1 (61168780) has ended:
#     1 refusals before anything is written: the host is not loginNN; a Slurm job is set; an rsn_ or fenced job is
#       queued or running; sacct does not show J1 as rsn_J1 COMPLETED 0:0; J1's log lacks its rc=0 line or its
#       product's sha256 line, or the product on disk differs from that line; $OUT/nc.json, $OUT/gates or $D exists;
#     2 a fresh clone at M_P1 into $D (the deploy J2 and J3 name): HEAD = M_P1, no modified or untracked file, the nine
#       §7 files at their bound sha256s, the committed nd-unfolding/rsn/rsn-prep-SHA256SUMS byte-equal to
#       $OUT/rsn-prep-SHA256SUMS (connect 1's), and P5 at its pin;
#     3 rsn_cmodel.py nc (§6 step 4) on J1's product, the frozen L-5D-PV products and P5 -> $OUT/nc.json; it must
#       record schema rsn-nc/1, PASS, J1's product sha256 and the bound rsn_cmodel.py sha256;
#     4 the gate files $OUT/gates/J2.ok and J3.ok, each the one line pin=M_P1;
#     5 everything is printed in full for the receipt PR, which is committed before step submit.
#   submit  after the receipt (nc.json, the gate files) is committed and the director's go:
#     1 refusals before anything is submitted: host, Slurm job; $OUT/nc.json records no rsn-nc/1 PASS; a gate file is
#       not exactly pin=M_P1; the deploy $D is not clean at M_P1 or sbatch_rsn.sh is not the bound one; fence.txt is
#       not the pinned bytes; an rsn_ or fenced job is queued or running;
#     2 the bound launcher's smoke mode (RSN_SMOKE=1, outside Slurm) for J2 (8 steps) and J3 (4 steps);
#     3 J2 and J3 are submitted back to back:
#       sbatch --parsable --job-name=rsn_J2 --time=0:22:00 --output=$OUT/logs/%x_%j.out sbatch_rsn.sh $D M_P1 $OUT J2
#       sbatch --parsable --job-name=rsn_J3 --time=0:19:00 --output=$OUT/logs/%x_%j.out sbatch_rsn.sh $D M_P1 $OUT J3
#       J3 is not submitted if J2's sbatch fails. It does not wait for the jobs.
# Any failure is a STOP: nothing is repaired or retried. Launched from a /dev/shm copy of itself ($1), deleted at exit.
# Threads 1, nice 19 for the NC. No set -u.
SELF=$1; STEP=$2
PIN=5e43e509d08d9b294594988f2c21e50e281e7ad8
P=/pscratch/sd/j/josephrb
B=$P/rsn-20261112
D=$B/deploy-p1
OUT=$B/out
J1_JOB=61168780
PVL_PRODUCTS=$P/pv-ladder-20261024/products
P5_REL=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/f1b3/prep/k1_p5_rerun.npz
P5_SHA=e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
REPO=https://github.com/josephbaileyy/MINERvA-OmniFold.git
CMODEL_SHA=ab63292122bffbc30e5d85efc2a5ae3f96c7f917891a856c48e2d26414848a48
LAUNCHER_SHA=f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6
FENCE_SHA=5934e32776a9142661188f2239bb91c1fb3f276f50afdbd666f1030d4cfa5894
FENCED='^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)'
BOUND="7b0fc567776d2016897173b1f8ab723fd99daedd34454537b36cd42bd03194be nd-unfolding/rsn/rsn_prep.py
5796bb6043a0ff646043206ef3ef623cbaf19d003875331da54a5642454e3690 nd-unfolding/rsn/rsn_unfold.py
ab63292122bffbc30e5d85efc2a5ae3f96c7f917891a856c48e2d26414848a48 nd-unfolding/rsn/rsn_cmodel.py
661608d81ccf7ca0ab08aee853f5934d4c0dab89677e82f8292239fee60b7652 nd-unfolding/rsn/rsn_regrade.py
4dd37197f6aa6c7f013b3ffea5558fd8d8fd1bc124047f761269adafce87e484 nd-unfolding/rsn/rsn_read.py
f889a0cf4de4a78aa7096bc01341ab6f3e6cdb41438267918519da7a527051d6 nd-unfolding/rsn/sbatch_rsn.sh
354bd16dd4d8b9dd5462f1daf6114e7beb467be3ab80e28b8ff212f51ea55616 nd-unfolding/rsn/rsn_tasks.tsv
887dbccd648e8648c03810e8d7ef335e09e5dfc7d97d4098c608db8de7bcaf29 nd-unfolding/rsn/test_rsn.py
8075fe8c9befed9184924fbab614ed81bf8c46bcfa112c7420a8c1a34d33f483 nd-unfolding/rsn/rsn_mutation.py"

bail() { echo "REFUSED (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
stop() { echo "STOP: $*"; rm -rf -- "$B/tmp-j23"; echo "== rsn connect j23 $STEP rc=8 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit 8; }
case "$STEP" in nc|submit) ;; *) bail "step '$STEP' is not nc or submit" ;; esac
case "$(hostname -s)" in login[0-9][0-9]) ;; *) bail "host $(hostname -s) is not a login node" ;; esac
[ -z "$SLURM_JOB_ID" ] || bail "a Slurm job is set ($SLURM_JOB_ID)"
q=$(squeue --me -h -o '%i|%j|%T') || bail "squeue failed"
hit=$(printf '%s\n' "$q" | awk -F'|' -v re="$FENCED" '$2 ~ re')
[ -z "$hit" ] || bail "fenced or rsn_ jobs are queued or running: $hit"
echo "node $(hostname) $(date -u +%FT%TZ) step $STEP slurm_job='$SLURM_JOB_ID'; connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "squeue --me:"; printf '%s\n' "$q"

if [ "$STEP" = nc ]; then
  [ -x "$PY" ] || bail "no $PY"
  [ ! -e "$OUT/nc.json" ] || bail "$OUT/nc.json exists"
  [ ! -e "$OUT/gates" ] || bail "$OUT/gates exists"
  [ ! -e "$D" ] || bail "$D exists"
  [ -s "$OUT/rsn-prep-SHA256SUMS" ] || bail "no $OUT/rsn-prep-SHA256SUMS (connect 1's)"
  acct=$(sacct -X -n -P -j "$J1_JOB" -o JobID,JobName,State,ExitCode,Elapsed) || bail "sacct failed"
  echo "sacct J1: $acct"
  printf '%s\n' "$acct" | awk -F'|' -v j="$J1_JOB" '$1 == j && $2 == "rsn_J1" && $3 == "COMPLETED" && $4 == "0:0" {f=1} END {exit !f}' \
    || bail "J1 $J1_JOB is not rsn_J1 COMPLETED 0:0"
  LOG="$OUT/logs/rsn_J1_$J1_JOB.out"
  grep -q '^\[rsn\] job=J1 rc=0 ' "$LOG" 2>/dev/null || bail "$LOG has no '[rsn] job=J1 rc=0' line"
  psha=$(awk -v f="$OUT/products/rsn_nc.npz" '$2 == f && $1 ~ /^[0-9a-f]{64}$/ {print $1}' "$LOG")
  [ -n "$psha" ] || bail "$LOG has no sha256 line for $OUT/products/rsn_nc.npz"
  got=$(sha256sum "$OUT/products/rsn_nc.npz" 2>/dev/null | cut -d' ' -f1)
  [ "$got" = "$psha" ] || bail "rsn_nc.npz on disk ($got) is not J1's logged $psha"
  echo "J1 log $LOG: rc=0; rsn_nc.npz sha256 $got (logged = on disk)"
  sed -n '/^\[rsn\] job=J1 slurm=/p; /^\[rsn\] job=J1 rc=/p' "$LOG"

  mkdir -p "$B/tmp-j23" || bail "mkdir $B/tmp-j23"
  export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  export TMPDIR="$B/tmp-j23" PYTHONDONTWRITEBYTECODE=1
  echo "python $("$PY" -V 2>&1); numpy $(env -u PYTHONPATH "$PY" -I -B -c 'import numpy; print(numpy.__version__)')"

  echo "== 2 clone at M_P1 $PIN into $D"
  git clone --quiet --filter=blob:none --no-checkout "$REPO" "$D" || stop "clone failed"
  git -C "$D" -c advice.detachedHead=false checkout --quiet "$PIN" || stop "checkout failed"
  head=$(git -C "$D" rev-parse HEAD)
  porc=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
  echo "HEAD $head; porcelain lines (untracked included) $porc"
  [ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || stop "the deploy is not $PIN clean"
  while read -r want rel; do
    got=$(sha256sum "$D/$rel" | cut -d' ' -f1); echo "sha256 $got $rel"
    [ "$got" = "$want" ] || stop "$rel is not at its bound sha256 $want"
  done <<< "$BOUND"
  cmp -s "$D/nd-unfolding/rsn/rsn-prep-SHA256SUMS" "$OUT/rsn-prep-SHA256SUMS" \
    || stop "the committed rsn-prep-SHA256SUMS is not connect 1's $OUT/rsn-prep-SHA256SUMS"
  echo "rsn-prep-SHA256SUMS committed = connect 1's: $(sha256sum "$OUT/rsn-prep-SHA256SUMS" | cut -d' ' -f1)"
  p5=$(sha256sum "$D/$P5_REL" | cut -d' ' -f1); echo "P5 sha256 $p5"
  [ "$p5" = "$P5_SHA" ] || stop "P5 is not at its pin $P5_SHA"

  echo "== 3 rsn_cmodel.py nc"
  ( cd "$B" && timeout 900 env -u PYTHONPATH nice -n 19 "$PY" -I -B "$D/nd-unfolding/rsn/rsn_cmodel.py" nc \
      --product "$OUT/products/rsn_nc.npz" --products "$PVL_PRODUCTS" --p5 "$D/$P5_REL" --out "$OUT/nc.json" \
      > "$OUT/logs/nc.out" 2> "$OUT/logs/nc.err" )
  r=$?; echo "rsn_cmodel.py nc rc=$r"; cat "$OUT/logs/nc.out" "$OUT/logs/nc.err"
  [ $r = 0 ] || stop "rsn_cmodel.py nc rc=$r"
  [ -f "$OUT/nc.json" ] || stop "no $OUT/nc.json"
  echo "== FILE nc.json sha256 $(sha256sum "$OUT/nc.json" | cut -d' ' -f1)"
  cat "$OUT/nc.json"; echo "== END nc.json"
  chk=$(env -u PYTHONPATH "$PY" -I -B -c 'import json,sys
d = json.load(open(sys.argv[1]))
ok = (d.get("schema") == "rsn-nc/1" and d.get("verdict") == "PASS" and d.get("product_sha256") == sys.argv[2]
      and d.get("code_sha256", {}).get("rsn_cmodel.py") == sys.argv[3])
print("OK" if ok else "BAD")' "$OUT/nc.json" "$psha" "$CMODEL_SHA")
  [ "$chk" = OK ] || stop "nc.json is not an rsn-nc/1 PASS on J1's product by the bound rsn_cmodel.py"
  echo "NC PASS: schema rsn-nc/1, product $psha, rsn_cmodel.py $CMODEL_SHA"

  echo "== 4 the gate files"
  mkdir "$OUT/gates" || stop "mkdir $OUT/gates"
  for j in J2 J3; do
    printf 'pin=%s\n' "$PIN" > "$OUT/gates/$j.ok" || stop "write $OUT/gates/$j.ok"
    echo "== FILE gates/$j.ok sha256 $(sha256sum "$OUT/gates/$j.ok" | cut -d' ' -f1)"; cat "$OUT/gates/$j.ok"
  done
  porc=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
  echo "deploy porcelain after (untracked included) $porc"
  [ "$porc" -eq 0 ] || stop "the deploy is no longer clean"
  rm -rf -- "$B/tmp-j23"
  echo "NC STEP PASS: J1 COMPLETED; NC PASS; deploy clean at $PIN; gates name it. J2 and J3 wait for the receipt and the director's go."
  echo "== rsn connect j23 nc rc=0 $(date -u +%FT%TZ)"
  rm -f -- "$SELF"; exit 0
fi

# step submit
grep -q '"schema": "rsn-nc/1"' "$OUT/nc.json" 2>/dev/null && grep -q '"verdict": "PASS"' "$OUT/nc.json" \
  || bail "$OUT/nc.json records no rsn-nc/1 PASS"
for j in J2 J3; do
  [ "$(cat "$OUT/gates/$j.ok" 2>/dev/null)" = "pin=$PIN" ] || bail "$OUT/gates/$j.ok is not exactly pin=$PIN"
done
head=$(git -C "$D" rev-parse HEAD 2>/dev/null)
porc=$(git -C "$D" status --porcelain --untracked-files=all 2>/dev/null | wc -l)
[ "$head" = "$PIN" ] && [ "$porc" -eq 0 ] || bail "the deploy is not $PIN clean (HEAD=$head, $porc porcelain lines)"
[ "$(sha256sum "$D/nd-unfolding/rsn/sbatch_rsn.sh" | cut -d' ' -f1)" = "$LAUNCHER_SHA" ] || bail "sbatch_rsn.sh is not the bound one"
[ "$(sha256sum "$OUT/fence.txt" 2>/dev/null | cut -d' ' -f1)" = "$FENCE_SHA" ] || bail "fence.txt is not the pinned bytes"
echo "deploy HEAD $head, porcelain $porc; sbatch_rsn.sh $LAUNCHER_SHA; fence.txt $FENCE_SHA; nc.json PASS; gates pin=$PIN"
mkdir -p "$OUT/logs" || stop "mkdir $OUT/logs"
for jn in "J2 8" "J3 4"; do
  set -- $jn
  echo "== the bound launcher's smoke mode for $1 (no npz read)"
  RSN_SMOKE=1 bash "$D/nd-unfolding/rsn/sbatch_rsn.sh" "$D" "$PIN" "$OUT" "$1" > "$OUT/logs/$1-smoke.txt" 2>&1; r=$?
  cat "$OUT/logs/$1-smoke.txt"; echo "smoke $1 rc=$r"
  [ $r = 0 ] && grep -q "^\[rsn\] smoke: checks passed, $2 steps" "$OUT/logs/$1-smoke.txt" \
    || stop "the launcher's smoke did not pass for $1 with $2 steps"
done
q2=$(squeue --me -h -o '%i|%j|%T') || stop "squeue failed"
hit=$(printf '%s\n' "$q2" | awk -F'|' -v re="$FENCED" '$2 ~ re')
[ -z "$hit" ] && echo "squeue again: none fenced" || stop "fenced or rsn_ jobs appeared: $hit"
echo "== submit J2 $(date -u +%FT%TZ)"
j2=$(sbatch --parsable --job-name=rsn_J2 --time=0:22:00 --output="$OUT/logs/%x_%j.out" \
     "$D/nd-unfolding/rsn/sbatch_rsn.sh" "$D" "$PIN" "$OUT" J2); r=$?
echo "sbatch J2 rc=$r jobid=$j2"
[ $r = 0 ] && [ -n "$j2" ] || stop "sbatch J2 failed; J3 not submitted"
echo "== submit J3 $(date -u +%FT%TZ)"
j3=$(sbatch --parsable --job-name=rsn_J3 --time=0:19:00 --output="$OUT/logs/%x_%j.out" \
     "$D/nd-unfolding/rsn/sbatch_rsn.sh" "$D" "$PIN" "$OUT" J3); r=$?
echo "sbatch J3 rc=$r jobid=$j3"
[ $r = 0 ] && [ -n "$j3" ] || stop "sbatch J3 failed; J2 $j2 IS submitted"
squeue -j "$j2,$j3" -o '%i|%j|%T|%l|%P|%q|%D' 2>&1
echo "J2 J3 SUBMITTED: J2 $j2 (0:22:00), J3 $j3 (0:19:00), deploy $D at $PIN, out $OUT"
echo "== rsn connect j23 submit rc=0 $(date -u +%FT%TZ)"
rm -f -- "$SELF"; exit 0
