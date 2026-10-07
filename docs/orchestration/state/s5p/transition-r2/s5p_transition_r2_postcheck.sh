# s5p transition r2: READ-ONLY post-start check of the restarted runners (E7). Run on saul:
#   ssh saul.nersc.gov 'bash -s' < s5p_transition_r2_postcheck.sh <DEPLOY_SHA_FULL> <EXPECTED_S5P_ARRAY_IDS_COMMA_SEPARATED>
# Exit 0 only if: exactly six queue-runner session leaders (PPID 1) exist on login33, one per queues-r2 lane, each
# running $NS/deploy/<sha>/nd-unfolding/s5c_queue.sh on its queues-r2 file; each r2 log records deploy=<deploy> and
# pin=<sha> and ends on the wait line of its expected label; squeue (rc 0) lists exactly the expected s5p cal/pow
# array ids (no new submission). Exit 1 otherwise, 2 if a probe failed. CANNOT AUTHORIZE: anything.
NS=/pscratch/sd/j/josephrb/s5p-20260926
SHA=${1:?deploy sha}; IDS=${2:?expected array ids}
D=$NS/deploy/${SHA:0:8}   # deploy directories are named by the 8-character short sha
fail=0
PS=$(ssh -n -q -o LogLevel=ERROR -o BatchMode=yes -o ConnectTimeout=30 login33 'ps -eo pid,pgid,ppid,args') || { echo "PROBE FAILED: login33 ps"; exit 2; }
total=$(printf '%s\n' "$PS" | awk '$3==1 && $5 ~ /s5c_queue\.sh$/' | grep -c .)
[ "$total" = 6 ] && echo "PASS six runner session leaders" || { echo "FAIL runner session leaders: $total"; fail=1; }
for spec in pow.q:s5p_pow_p3_a1p0:pow cal-MnvTune_v1.q:s5p_cal_mnvtune_v1_b2:MnvTune_v1 \
            cal-GENIE_2_12_10_CV.q:s5p_cal_genie_2_12_10_cv_b2:GENIE_2_12_10_CV cal-GENIE_2_12_10_MEC.q:s5p_cal_genie_2_12_10_mec_b2:GENIE_2_12_10_MEC \
            cal-NuWro_21_09.q:s5p_cal_nuwro_21_09_b2:NuWro_21_09 cal-GiBUU_2019.q:s5p_cal_gibuu_2019_b2:GiBUU_2019; do
  IFS=: read -r q lab lane <<< "$spec"
  want="$D/nd-unfolding/s5c_queue.sh $D/docs/orchestration/state/s5p/prod/queues-r2/$q $NS/runs/STOP-prod-r2-$lane"
  n=$(printf '%s\n' "$PS" | awk '$3==1' | grep -cF -- "$want")
  L=$NS/runs/queue-prod-r2-$lane.log
  started=$(grep -cF "deploy=$D pin=$SHA" "$L" 2>/dev/null)
  last=$(tail -1 "$L" 2>/dev/null)
  case "$last" in *"until out=\$(squeue -h --me -n s5p-$lab "*) onwait=yes ;; *) onwait=no ;; esac
  if [ "$n" = 1 ] && [ "$started" -ge 1 ] && [ $onwait = yes ]; then echo "PASS $lane: one runner, log pinned to $SHA, waiting on $lab"
  else echo "FAIL $lane: runners=$n pinned_start_lines=$started on_wait_line=$onwait last=${last:0:120}"; fail=1; fi
done
SQ=$(squeue -h -u josephrb -o "%F|%j" 2>/dev/null); rc=$?
[ $rc = 0 ] || { echo "PROBE FAILED: squeue rc=$rc"; exit 2; }
have=$(printf '%s\n' "$SQ" | awk -F'|' '$2 ~ /^s5p-s5p_(cal|pow)_/ {print $1}' | sort -u | paste -sd, -)
want=$(printf '%s\n' "$IDS" | tr ',' '\n' | sort -u | paste -sd, -)
[ "$have" = "$want" ] && echo "PASS s5p arrays in squeue == expected ($have)" || { echo "FAIL s5p arrays in squeue: have [$have] want [$want]"; fail=1; }
if [ $fail = 0 ]; then echo "POSTCHECK: PASS"; exit 0; else echo "POSTCHECK: FAIL"; exit 1; fi
