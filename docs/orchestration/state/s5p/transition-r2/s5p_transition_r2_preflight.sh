# s5p transition r2 (budget revision 6 + coordinated six-runner transition): READ-ONLY preflight.
# Run from the campaign worktree:  ssh saul.nersc.gov 'bash -s' < s5p_transition_r2_preflight.sh [NEW_DEPLOY_SHA]
# MEASURES: whether every lane can be stopped safely now (one runner, on its wait line, its array with pending
# tasks), the ledger's budget binding, the meter, and (given a sha) the candidate new deploy. It writes only the
# meter's --out receipt under $NS/diag-20260929/transition-dry/. CANNOT AUTHORIZE: the transition (owner approval).
NS=/pscratch/sd/j/josephrb/s5p-20260926
NEW=${1:-}
T=$NS/diag-20260929/transition-dry
mkdir -p "$T"
echo "preflight $(date -u +%FT%TZ)"
fail=0
PS=$(ssh -n -q -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout=30 login33 'ps -eo pid,pgid,ppid,args') || { echo "NOT READY: login33 ps failed"; exit 2; }
SQ=$(squeue -h -r -u josephrb -o "%j|%T" 2>/dev/null); sq_rc=$?
[ $sq_rc = 0 ] || { echo "NOT READY: squeue rc=$sq_rc"; exit 2; }
for spec in pow:queues-r1/pow.q:queue-prod-r1-pow.log \
            MnvTune_v1:queues-r1/cal-MnvTune_v1.q:queue-prod-r1-MnvTune_v1.log \
            GENIE_2_12_10_CV:queues-r1/cal-GENIE_2_12_10_CV.q:queue-prod-r1-GENIE_2_12_10_CV.log \
            GENIE_2_12_10_MEC:queues-r1/cal-GENIE_2_12_10_MEC.q:queue-prod-r1-GENIE_2_12_10_MEC.log \
            NuWro_21_09:queues/cal-NuWro_21_09.q:queue-prod-NuWro_21_09.log \
            GiBUU_2019:queues/cal-GiBUU_2019.q:queue-prod-GiBUU_2019.log; do
  IFS=: read -r lane q log <<< "$spec"
  leaders=$(printf '%s\n' "$PS" | awk -v q="$q" '$3==1 && $5 ~ /s5c_queue\.sh$/ && index($6, q) {print $2}')
  n=$(printf '%s\n' "$leaders" | grep -c .)
  last=$(tail -1 "$NS/runs/$log")
  label=$(printf '%s\n' "$last" | sed -n 's/.*until out=$(squeue -h --me -n s5p-\([a-z0-9_]*\) .*/\1/p')
  pend=$(printf '%s\n' "$SQ" | grep -c "^s5p-$label|PENDING"); run=$(printf '%s\n' "$SQ" | grep -c "^s5p-$label|RUNNING")
  done_q=$(grep -c "queue done" "$NS/runs/$log")
  if [ "$done_q" -gt 0 ]; then state="TERMINAL (queue done): nothing to move"
  elif [ "$n" != 1 ]; then state="NOT READY: $n runner session leaders"; fail=1
  elif [ -z "$label" ]; then state="NOT READY: runner not on a wait line: ${last:0:140}"; fail=1
  elif [ "$pend" -lt 1 ]; then state="NOT READY: array s5p-$label has no pending task (may leave the scheduler soon)"; fail=1
  else state="READY"; fi
  echo "$lane pgid=$(echo $leaders | tr '\n' ' ') label=${label:-?} pending=$pend running=$run :: $state"
done
echo "status files: $(ls $NS/runs/prod/status | wc -l), finals: $(ls $NS/runs/prod/status | grep -c final)"
last_bind=$(grep '"kind": "budget"' $NS/ledger/admissions.jsonl | tail -1 | sed -n 's/.*"budget_sha256": "\([0-9a-f]*\)".*/\1/p')
rev5=$(sha256sum $NS/deploy/55a41765/docs/orchestration/state/s5p/budget.json | cut -d' ' -f1)
echo "ledger last budget binding ${last_bind:0:12}; deploy 55a41765 budget ${rev5:0:12} :: $([ "$last_bind" = "$rev5" ] && echo OK || { fail=1; echo MISMATCH; })"
( cd $NS/deploy/55a41765 && /usr/bin/python3.11 nd-unfolding/s5c_meter.py --budget docs/orchestration/state/s5p/budget.json \
    --ledger $NS/ledger/admissions.jsonl measure --out $T/preflight-meter-$(date -u +%Y%m%dT%H%MZ).json > /dev/null 2>&1 ) \
  && echo "meter measure (rev 5) rc=0" || { echo "NOT READY: meter measure failed"; fail=1; }
if [ -n "$NEW" ]; then
  D=$NS/deploy/$NEW
  if [ ! -d "$D/.git" ]; then echo "NOT READY: no deploy $D"; fail=1
  else
    head=$(git -C "$D" rev-parse --short=8 HEAD); dirty=$(git -C "$D" status --porcelain --untracked-files=no | wc -l)
    extra=$(git -C "$D" diff --name-only 55a41765 HEAD -- nd-unfolding | grep -vE '^nd-unfolding/(s5p_robust_labels\.py|tests/test_s5p_robust_labels\.py)$' | wc -l)
    frozen=$(git -C "$D" diff --quiet 4f5a613f HEAD -- nd-unfolding/s5p_joint.py nd-unfolding/s5p_inference.py nd-unfolding/s5p_seqstop.py && echo identical || echo CHANGED)
    rev=$(/usr/bin/python3.11 -c "import json;b=json.load(open('$D/docs/orchestration/state/s5p/budget.json'));s=b['pools']['cpu']['stages'];print(b['revision'],s['production'],round(sum(s.values()),3),b['pools']['cpu']['campaign_cap_node_hours'],s['verification_repair'])")
    nq=$(ls $D/docs/orchestration/state/s5p/prod/queues-r2/*.q 2>/dev/null | wc -l)
    echo "new deploy $NEW: HEAD $head, tracked changes $dirty, extra nd-unfolding changes vs 55a41765 $extra, frozen modules $frozen, budget [rev prod sum cap vr] $rev, queues-r2 $nq"
    [ "$head" = "${NEW:0:8}" ] && [ "$dirty" = 0 ] && [ "$extra" = 0 ] && [ "$frozen" = identical ] && [ "$nq" -ge 1 ] || { echo "NOT READY: new deploy check"; fail=1; }
  fi
fi
[ $fail = 0 ] && echo "PREFLIGHT: READY" || echo "PREFLIGHT: NOT READY"
