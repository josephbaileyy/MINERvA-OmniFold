#!/bin/bash
# T3: the submit connect (T3-CONNECT-PLAN.md section 6, under T3-BINDING-1 with addendum V1 and the director's standing
# go of 2026-11-21 relaying Joseph's authorization). Derived from FD-PRR's reviewed prr_dry_submit.sh (934c9c2f).
# On a Perlmutter login node, from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit.
#   usage: t3p_submit.sh <self> <dry|q3|floor> <window_end_epoch> <fence prefixes, comma-separated>
# In order, any failure a final stop before anything is submitted:
#   the window: now <= window_end (the epoch the launcher computed from date, never typed);
#   the fence: no job of this user whose name starts with a fenced prefix or t3p_ is in a non-terminal state, by sacct
#     (State classified in code; sacct, never squeue);
#   the balance from iris: the remaining cap at most half of m3246's remaining balance (cap 10.0 node-h overall);
#   dry: $OUT new; a fresh clone at M_V1, clean, the six bound T3 files, the declaration and addendum V1 at sha256;
#     test_t3p.py (69 OK) under root_6_28; the manifest (t3p_probe.py manifest) and its pins check (each source read
#     once through dd iflag=noatime into sha256sum, stat unmoved); the environment; the queues (dry 6, q3 6, floor 24);
#     $OUT/fence.txt, one prefix per line;
#   q3, floor: $OUT and its deploy exist, clean at M_V1, the bound files unchanged; log-dry/DONE present without STOP;
#     no log-<mode>;
#   the job's own limit from the bound code (`t3p_probe.py limit <mode>`) is the --time; one sbatch from the plain login
#     environment (FD-PRR's proven path); scontrol's TimeLimit must equal it, or scancel at once.
# Writes only under $OUT. No set -u (it kills setup_salloc_env.sh).
SELF=$1; MODE=$2; WEND=$3; FENCE=$4
M=8bb4e3b0e1028d960e39de0c202569a08a1218a0
OUT=/pscratch/sd/j/josephrb/t3p-20261121
D=$OUT/deploy
CAP_TOTAL=10.0
DECL_SHA=f96ed6f29a155e978bf449fdcb9810670202e0a3d74fb2f96afe48098b63cae1
V1_SHA=3998708a91dde4b01c3dcb1e87a7b7a45796de13da53880a0eb79a410ecc7986
bail() { echo "BAIL $*"; rm -f -- "$SELF"; exit 9; }
case "$MODE" in dry|q3|floor) ;; *) bail "mode '$MODE'";; esac
[[ "$WEND" =~ ^[0-9]{10}$ ]] || bail "window end '$WEND'"
now=$(date +%s); [ "$now" -le "$WEND" ] || bail "the window ended (now $now > $WEND)"
[[ "$FENCE" =~ ^[A-Za-z0-9_.-]+(,[A-Za-z0-9_.-]+)*$ ]] || bail "fence '$FENCE'"

# ---- the fence by sacct: non-terminal = any State outside the terminal set (CANCELLED by <uid> included as terminal)
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
if [ "$MODE" = dry ]; then
  [ ! -e "$OUT" ] || bail "$OUT exists"
  mkdir -p "$OUT/logs" || bail "mkdir"
else
  [ -d "$OUT/logs" ] && [ -d "$D" ] || bail "no $OUT or deploy"
  [ ! -e "$OUT/log-$MODE" ] || bail "log-$MODE exists"
fi
LOG=$OUT/logs/connect-$MODE.log
[ ! -e "$LOG" ] || bail "$LOG exists"
exec > "$LOG" 2>&1
finish() { echo "t3p $MODE submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-$MODE.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ; echo "window_end_epoch $WEND (now $now); fence prefixes $FENCE"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/t3p_submit.$MODE.sh"
echo "== fence (sacct)"; fence_sacct || { echo "STOP: fence"; finish 9; }; echo "fence clear"

# ---- the balance: iris's m3246 row, Allocated - Charged; the remaining cap = 10.0 minus the limits already submitted
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap_total=$CAP_TOTAL"
awk -v b=$bal -v c=$CAP_TOTAL 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap $CAP_TOTAL is above half the balance $bal"; finish 9; }

PYENV() { ( eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
            conda activate "$HOME/.conda/envs/root_6_28" && cd "$D" && \
            nice -n 19 env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 python3 -B "$@" ); }
bound_check() {
  ( cd "$D/nd-unfolding/tier3" && sha256sum -c ) <<SUMS
4a685bde238dcc6dc25e9b1121029994f33becafab486cbec1a7bf846206bf84  t3p_arms.py
e27bf07a3e2c60320a749355eaedceed5a36574d2d8fa83675bd4b4721985bd2  t3p_probe.py
f4c221dda95fbbdf2318f7fcdde57b9e1b7fb265e85b13e1dea15341cf069295  t3p_read.py
a21ad29f35a71e46c1b286ca6ae96128f01c482cbd30aac5133d3e4729d2de3c  sbatch_t3p.sh
4879178f4f9783f011f8a5992273e0b34a3d022bb822edf688051f038e642aa8  test_t3p.py
ae9667bc71819f092a7f61ae6d58ed4e7659ea4b0fea08de299c10462d738001  t3p_mutation.py
SUMS
}
T3DIR="$D/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier3-20261110"
# rev 2 (2026-11-21, after dry connect 1's rc 8): python3 without -B (this connect's limit call at rev 1, and the bound
# job's own calls) writes ignored __pycache__/ directories into the deploy; those are tolerated, nothing else is
clean_check() {
  local n bad
  n=$(git -C "$D" status --porcelain --untracked-files=all | wc -l)
  bad=$(git -C "$D" status --porcelain --ignored --untracked-files=all | grep '^!! ' | grep -vc '__pycache__/')
  echo "porcelain lines (tracked+untracked) $n; ignored entries other than __pycache__/ $bad"
  [ "$n" -eq 0 ] && [ "$bad" -eq 0 ]
}

if [ "$MODE" = dry ]; then
  # ---- the deploy: a fresh clone at M, clean, the bound bytes
  git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
  git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
fi
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
echo "HEAD $M"; clean_check || { echo "STOP: the deploy is not clean"; finish 9; }
bound_check || { echo "STOP: the T3 files are not the bound ones"; finish 9; }
decl=$(sha256sum "$T3DIR/T3-PIPELINE-TESTS-DECLARATION.md" | cut -d' ' -f1); echo "declaration sha256 $decl"
[ "$decl" = "$DECL_SHA" ] || { echo "STOP: the declaration is not the bound one"; finish 9; }
v1=$(sha256sum "$T3DIR/T3-ADDENDUM-V1.md" | cut -d' ' -f1); echo "addendum V1 sha256 $v1"
[ "$v1" = "$V1_SHA" ] || { echo "STOP: addendum V1 is not the bound one"; finish 9; }

if [ "$MODE" = dry ]; then
  # ---- the tests (binding addendum V1: every connect checks the two new test digests; 69 OK)
  PYENV -m unittest nd-unfolding/tier3/test_t3p.py > "$OUT/logs/tests.log" 2>&1; trc=$?
  tail -3 "$OUT/logs/tests.log"
  [ "$trc" -eq 0 ] && grep -q '^Ran 69 tests' "$OUT/logs/tests.log" && tail -1 "$OUT/logs/tests.log" | grep -q '^OK' \
    || { echo "STOP: test_t3p.py did not run 69 OK (rc $trc)"; finish 5; }
  clean_check || { echo "STOP: the tests left files in the deploy"; git -C "$D" status --porcelain --ignored | head; finish 5; }

  # ---- the manifest, from the bound code, then the pins check of every source
  PYENV nd-unfolding/tier3/t3p_probe.py manifest --out "$OUT/manifest.json" || { echo "STOP: manifest"; finish 5; }
  sha256sum "$OUT/manifest.json"
  PYENV - "$OUT/manifest.json" > "$OUT/logs/pins.tsv" <<'EOF' || { echo "STOP: the pins check did not pass (logs/pins.tsv)"; cat "$OUT/logs/pins.tsv"; finish 4; }
import json, os, subprocess, sys
ok = True
print("role\tsha256_ok\tstat_unmoved\tsize\tatime_before_ns\tatime_after_ns\tsrc")
for e in json.load(open(sys.argv[1])):
    st = lambda: (lambda s: (s.st_size, s.st_mtime_ns, s.st_atime_ns, s.st_ino))(os.stat(e["src"]))
    before = st()
    dd = subprocess.Popen(["dd", f"if={e['src']}", "iflag=noatime", "bs=16M", "status=none"], stdout=subprocess.PIPE)
    got = subprocess.run(["sha256sum"], stdin=dd.stdout, capture_output=True, text=True).stdout.split()[0]
    rc = dd.wait()
    after = st()
    good, still = rc == 0 and got == e["sha256"], before == after
    ok &= good and still
    print(f"{e['role']}\t{good}\t{still}\t{before[0]}\t{before[2]}\t{after[2]}\t{e['src']}")
sys.exit(0 if ok else 1)
EOF
  cat "$OUT/logs/pins.tsv"

  # ---- the environment the job will source
  ( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck.log" 2>&1
    python3 -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
    || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

  # ---- the queues, from the probe's own tasks command
  PYENV nd-unfolding/tier3/t3p_probe.py tasks --out "$OUT/queues" --stage-dir "$OUT/stage" --runs "$OUT/runs" \
    --stage-json "$OUT/stage.json" || { echo "STOP: tasks"; finish 5; }
  for j in dry:6 q3:6 floor:24; do
    n=$(grep -vc '^#' "$OUT/queues/${j%%:*}.tsv"); echo "queue ${j%%:*}: $n tasks"
    [ "$n" -eq "${j##*:}" ] || { echo "STOP: queue ${j%%:*} is not ${j##*:} tasks"; finish 5; }
  done
  sha256sum "$OUT"/queues/*.tsv

  # ---- the fence file the job reads (sbatch_t3p.sh:76-83), one prefix per line
  printf '%s\n' "${FENCE//,/$'\n'}" > "$OUT/fence.txt"; echo "fence.txt:"; cat "$OUT/fence.txt"
else
  [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] || { echo "STOP: no clean dry-run DONE"; finish 9; }
  cat "$OUT/log-dry/DONE"
  [ -s "$OUT/fence.txt" ] || { echo "STOP: no fence.txt"; finish 9; }
fi

# ---- the job's first python call after sourcing: the declared limit is the --time submitted
lim=$( source "$D/setup_salloc_env.sh" > "$OUT/logs/connect-source-$MODE.log" 2>&1; rc=$?
       [ "$rc" -eq 0 ] || { echo "SOURCE_RC=$rc" >&2; exit 97; }
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo "NOT_ROOT628" >&2; exit 98; }
       python3 -B "$D/nd-unfolding/tier3/t3p_probe.py" limit "$MODE" ) 2> "$OUT/logs/sourced-python-$MODE.err"
lrc=$?
cat "$OUT/logs/sourced-python-$MODE.err"
case "$MODE" in dry) want=2:15:00;; q3) want=2:00:00;; floor) want=5:45:00;; esac
echo "t3p_probe.py limit $MODE -> '$lim' (rc $lrc), declared $want"
[ "$lrc" -eq 0 ] && [ "$lim" = "$want" ] || { echo "STOP: the limit is not the declared $want"; finish 7; }
TLIMIT=$(echo "$lim" | awk -F: '{printf "%02d:%02d:%02d", $1, $2, $3}')

# ---- the submission, from the plain login environment, as FD-PRR's, ENS1's and E96D's connects submitted (the job
# script is --export=ALL with HOME set and sources setup_salloc_env.sh itself; every conda call above ran in a subshell)
echo "== fence again (sacct)"; fence_sacct || { echo "STOP: fence at submission"; finish 9; }
now=$(date +%s); [ "$now" -le "$WEND" ] || { echo "STOP: the window ended before sbatch"; finish 9; }
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=t3p_$MODE --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/tier3/sbatch_t3p.sh" "$MODE" "$D" "$M" "$OUT" > "$OUT/logs/submit-$MODE.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-$MODE.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-$MODE.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "t3p_$MODE job $job"; echo "$job" > "$OUT/logs/$MODE.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
sacct -j "$job" -X -n -P -o JobID,JobName,State,Timelimit,NNodes,QOS,Account
clean_check || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
