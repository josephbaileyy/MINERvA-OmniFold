# s5p terminal run: CHECKLIST-20261001-s5p-terminal-and-claims.md sections 1-2, as one checked script.
# Usage (from the campaign worktree):
#   ssh saul.nersc.gov 'bash -s check'            < s5p_terminal_run.sh   read-only: is production terminal?
#   ssh saul.nersc.gov 'bash -s deploy <sha>'     < s5p_terminal_run.sh   new clean clone of origin/main at <sha>, verified
#   ssh saul.nersc.gov 'bash -s verify <sha>'     < s5p_terminal_run.sh   read-only: re-verify an existing deploy
#   ssh saul.nersc.gov 'bash -s evaluate <sha>'   < s5p_terminal_run.sh   evaluate, labels, seed states, sensitivity
# Exit codes: 0 = done/ready; 1 = a check failed (nothing written by check/deploy beyond the new deploy dir);
# 2 = a probe failed; 4 = sensitivity INCOMPLETE (outputs written and labelled).
# MEASURES: terminal readiness and the frozen evaluation outputs. CANNOT AUTHORIZE: recording the joint result
# before the independent recompute report (amendment 7 validation_and_assurance (v)).
set -o pipefail
NS=/pscratch/sd/j/josephrb/s5p-20260926
NULLS="MnvTune_v1 GENIE_2_12_10_CV GENIE_2_12_10_MEC NuWro_21_09 GiBUU_2019"
DESIGN_SHA=404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285
V=$NS/stage3/V/V-s3v.npz
V_SHA=35979ef75ca1b0fb019c07a20e11a4bf0fe3b230e7cea495930fb572fe8e1c84
METER_DEPLOY=$NS/deploy/e0d7b04a   # budget revision 7 (transition r3); older deploys are refused by the meter
RUNNER_PIDS="1047835 1047836 1047838 1047839 1047840 1047841"   # r3 runners (2026-10-04)
OUT=$NS/stage7/joint
cmd=${1:?check | deploy <sha> | verify <sha> | evaluate <sha>}
fail=0
say() { echo "$*"; }
bad() { echo "FAIL $*"; fail=1; }

check_terminal() {
  for n in $NULLS; do
    f=$NS/runs/prod/status/$n-final.json
    if [ -f "$f" ]; then say "PASS final $n: $(/usr/bin/python3.11 -c "import json,sys;d=json.load(open(sys.argv[1]));print('B',d['B'],'reason',d['reason'])" "$f")"
    else bad "no final status for $n"; fi
  done
  P=$NS/runs/queue-prod-r3-pow.log
  if grep -q "queue done" "$P"; then say "PASS power: 'queue done' in $(basename $P)"
  elif grep -qE "refused|--force-stop budget|\"reason\": \"budget\"|STOPPED the queue" "$P"; then bad "power: no 'queue done'; outcome lines: $(grep -E 'refused|--force-stop budget|"reason": "budget"|STOPPED the queue' "$P" | tail -2 | cut -c1-120)"
  else bad "power: queue not done"; fi
  Q=$(squeue -h -u josephrb -o "%j" 2>/dev/null); rc=$?
  if [ $rc != 0 ]; then echo "PROBE FAILED squeue rc=$rc"; exit 2; fi
  n=$(printf '%s\n' "$Q" | grep -c '^s5p-s5p_\(cal\|pow\)_')
  [ "$n" = 0 ] && say "PASS squeue rc 0, no s5p cal/pow job" || bad "squeue: $n s5p cal/pow jobs queued"
  M=$NS/measure/meter-measure-terminal-check-$(date -u +%Y%m%dT%H%M%SZ).json
  if (cd $METER_DEPLOY && /usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/s5p/budget.json \
        --ledger $NS/ledger/admissions.jsonl measure --out $M > /dev/null 2>&1); then
    oc=$(/usr/bin/python3.11 -c "import json,sys;s=json.load(open(sys.argv[1]))['summary'];print(s['cpu']['open_concurrency'],s['gpu']['open_concurrency'])" $M)
    [ "$oc" = "0.0 0.0" ] || [ "$oc" = "0 0" ] && say "PASS meter rc 0, open concurrency cpu/gpu $oc ($M)" || bad "meter open concurrency cpu/gpu $oc"
  else echo "PROBE FAILED meter measure"; exit 2; fi
  A=$(timeout 120 ssh -n -q -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout=30 login33 \
        "n=0; for p in $RUNNER_PIDS; do [ -r /proc/\$p/cmdline ] && n=\$((n+1)); done; echo \$n; timeout 60 ps -eo ppid,args 2>/dev/null | awk '\$1==1 && \$3 ~ /s5c_queue\\.sh\$/' | wc -l") || { echo "PROBE FAILED login33"; exit 2; }
  set -- $A
  [ "$1" = 0 ] && say "PASS no r3 runner process left" || bad "$1 r3 runner processes still alive"
  [ "${2:-0}" = 0 ] && say "PASS no queue-runner session leader on login33" || bad "${2} queue-runner session leaders on login33"
}

verify_deploy() {
  D=$1; sha=$2
  [ "$(git -C $D rev-parse HEAD)" = "$sha" ] && say "PASS deploy HEAD $sha" || bad "deploy HEAD $(git -C $D rev-parse HEAD)"
  [ -z "$(git -C $D status --porcelain --untracked-files=no)" ] && say "PASS deploy clean" || bad "deploy not clean"
  git -C $D diff --quiet 4f5a613f HEAD -- nd-unfolding/s5p_joint.py nd-unfolding/s5p_inference.py nd-unfolding/s5p_seqstop.py \
    && say "PASS frozen modules byte-identical to 4f5a613f" || bad "frozen modules differ from 4f5a613f"
  [ "$(sha256sum $D/docs/orchestration/state/s5p/prod/design.json | cut -d' ' -f1)" = $DESIGN_SHA ] && say "PASS design sha256 404446eb" || bad "design sha256"
  [ "$(sha256sum $V | cut -d' ' -f1)" = $V_SHA ] && say "PASS V sha256 35979ef7" || bad "V sha256"
  for f in nd-unfolding/s5p_robust_labels.py nd-unfolding/s5p_missing_sensitivity.py docs/orchestration/state/s5p/diag/s5p_lost_seed_runtime_diagnostic.py; do
    [ -f $D/$f ] && say "PASS present $f" || bad "missing $f"
  done
}

case "$cmd" in
  check)
    check_terminal
    [ $fail = 0 ] && { echo "TERMINAL: YES"; exit 0; } || { echo "TERMINAL: NO"; exit 1; } ;;
  deploy)
    sha=${2:?full sha}; D=$NS/deploy/${sha:0:8}
    [ -e $D ] && { echo "FAIL $D exists (never touch an existing deploy)"; exit 1; }
    git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout -q $sha || { echo "FAIL clone/checkout"; exit 1; }
    verify_deploy $D $sha
    [ $fail = 0 ] && { echo "DEPLOY: VALID $D"; exit 0; } || { echo "DEPLOY: INVALID"; exit 1; } ;;
  verify)
    sha=${2:?full sha}; verify_deploy $NS/deploy/${sha:0:8} $sha
    [ $fail = 0 ] && { echo "DEPLOY: VALID"; exit 0; } || { echo "DEPLOY: INVALID"; exit 1; } ;;
  evaluate)
    sha=${2:?full sha}; D=$NS/deploy/${sha:0:8}
    check_terminal; verify_deploy $D $sha
    [ $fail = 0 ] || { echo "EVALUATE: REFUSED (terminal or deploy check failed)"; exit 1; }
    mkdir -p $OUT
    for f in joint-evaluate.json robust-labels.json seed-states.json missing-sensitivity.json; do
      [ -e $OUT/$f ] && { echo "FAIL $OUT/$f exists (never overwrite)"; exit 1; }
    done
    cd $D && source ./setup_salloc_env.sh > /dev/null 2>&1
    export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
    PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_joint.py evaluate --design docs/orchestration/state/s5p/prod/design.json \
      --v $V --out $OUT/joint-evaluate.json > $OUT/joint-evaluate.stdout 2>&1 || { echo "FAIL evaluate rc=$?"; tail -5 $OUT/joint-evaluate.stdout; exit 1; }
    PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_robust_labels.py --evaluate $OUT/joint-evaluate.json \
      --design docs/orchestration/state/s5p/prod/design.json --out $OUT/robust-labels.json > $OUT/robust-labels.stdout 2>&1 || { echo "FAIL labels rc=$?"; exit 1; }
    PYTHONPATH=nd-unfolding python3 docs/orchestration/state/s5p/diag/s5p_lost_seed_runtime_diagnostic.py --logs $NS/runs/prod/logs \
      --v $V --out $OUT/seed-states.json > $OUT/seed-states.stdout 2>&1 || { echo "FAIL seed states rc=$?"; exit 1; }
    PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_missing_sensitivity.py --evaluate $OUT/joint-evaluate.json \
      --design docs/orchestration/state/s5p/prod/design.json --tables docs/orchestration/state/s5p/prod/tables \
      --ledger $NS/ledger/admissions.jsonl --seed-states $OUT/seed-states.json --out $OUT/missing-sensitivity.json > $OUT/missing-sensitivity.stdout 2>&1
    src=$?
    [ $src = 0 ] || [ $src = 4 ] || { echo "FAIL sensitivity rc=$src"; tail -5 $OUT/missing-sensitivity.stdout; exit 1; }
    echo "== packet for the recompute lane (CHECKLIST s2 step 6)"
    echo "deploy $sha ($D)"
    sha256sum $OUT/joint-evaluate.json $OUT/robust-labels.json $OUT/seed-states.json $OUT/missing-sensitivity.json
    echo "sensitivity status: $(/usr/bin/python3.11 -c "import json;print(json.load(open('$OUT/missing-sensitivity.json'))['status'])")"
    [ $src = 0 ] && exit 0 || exit 4 ;;
  *) echo "usage: check | deploy <sha> | evaluate <sha>"; exit 2 ;;
esac
