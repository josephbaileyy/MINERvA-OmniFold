#!/bin/bash
# Stand-in run of s2r_submit.sh or s2r_fetch.sh inside a Debian container (Dockerfile.txt). Stubs: sacct, iris, sbatch,
# scontrol, scancel (each logs its call), git's clone URL only (a --shared clone of the read-only host object store),
# the conda hook (activation = PATH), and sha256sum on stdin only for planted inputs: a planted /pscratch input holds
# the text "STANDIN-PIN:<its pin>" and the stub prints that pin (every other sha256sum call is the real tool). The real
# 3.7 GB inputs cannot be planted; everything else is the real script and the real tools.
# Usage (in the container): standin.sh <submit|fetch> <variant>
#   submit: ok | fence_running | s2r_pending | out_exists | low_balance | pin_bad | timelimit_bad | window_ended
#   fetch:  ok | not_completed | stop_present | sums_bad | extra_product | no_readout
WHICH=${1:?}; V=${2:?}
M=4017c0825444c4e88742801653bf088075c197ed
OUT=/pscratch/sd/j/josephrb/s2r-20261124
git config --global --add safe.directory '*'
export HOME=/root
# the image's lightgbm needs libgomp.so.1; scikit-learn's wheel ships one (the Docker VM disk is too full to apt it)
mkdir -p /global/standin-lib && ln -sf /usr/local/lib/python3.11/site-packages/scikit_learn.libs/libgomp-a49a47f9.so.1.0.0 /global/standin-lib/libgomp.so.1
export LD_LIBRARY_PATH=/global/standin-lib
mkdir -p /stub /root/.conda/envs/root_6_28/bin /global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin
ln -sf /usr/local/bin/python3 /root/.conda/envs/root_6_28/bin/python3
cat > /global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda <<'EOF'
#!/bin/bash
[ "$1" = shell.bash ] && echo 'conda() { if [ "$1" = activate ]; then export PATH="$2/bin:$PATH"; fi; }'
EOF
chmod +x /global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda
cat > /stub/git <<'EOF'
#!/bin/bash
if [ "$1" = clone ]; then dest=${@: -1}; exec /usr/bin/git clone -q --shared /hostgit "$dest"; fi
exec /usr/bin/git "$@"
EOF
cat > /stub/sha256sum <<'EOF'
#!/bin/bash
if [ "$#" -eq 0 ]; then
  t=$(mktemp); cat > "$t"
  if head -c 12 "$t" | grep -q '^STANDIN-PIN:'; then echo "$(sed -n 's/^STANDIN-PIN:\([0-9a-f]\{64\}\).*/\1/p' "$t")  -"; rm -f "$t"; exit 0; fi
  /usr/bin/sha256sum < "$t"; r=$?; rm -f "$t"; exit $r
fi
exec /usr/bin/sha256sum "$@"
EOF
FENCE_ROWS="99|cov2d_x|COMPLETED"
[ "$V" = fence_running ] && FENCE_ROWS="99|rpd_reco_p1|RUNNING"
[ "$V" = s2r_pending ] && FENCE_ROWS="98|s2r_run|PENDING"
JOB_STATE=COMPLETED; [ "$V" = not_completed ] && JOB_STATE=RUNNING
cat > /stub/sacct <<EOF
#!/bin/bash
echo "sacct \$*" >> /tmp/calls.log
if [[ " \$* " == *" -j "* ]]; then
  if [[ " \$* " == *"JobName,State"* ]] && [[ " \$* " != *"JobID,JobName"* ]]; then echo "s2r_run|$JOB_STATE"
  else echo "7000001|s2r_run|$JOB_STATE|0:0|2026-11-24T20:00:00|2026-11-24T20:40:00|2400|1|01:00:00|1|regular|m3246"; fi
else printf '%s\n' "$FENCE_ROWS" "100|ibub_run|RUNNING"; fi
EOF
BAL="1328.8"; [ "$V" = low_balance ] && BAL="1.5"
cat > /stub/iris <<EOF
#!/bin/bash
echo "Project Allocation"; echo "m3246 cpu x 0.0 $BAL"
EOF
cat > /stub/sbatch <<'EOF'
#!/bin/bash
echo "sbatch $*" >> /tmp/calls.log; echo "Submitted batch job 7000001"
EOF
TL=01:00:00; [ "$V" = timelimit_bad ] && TL=01:30:00
cat > /stub/scontrol <<EOF
#!/bin/bash
echo "scontrol \$*" >> /tmp/calls.log; echo "JobId=7000001 JobName=s2r_run TimeLimit=$TL TimeMin=N/A"
EOF
cat > /stub/scancel <<'EOF'
#!/bin/bash
echo "scancel $*" >> /tmp/calls.log
EOF
printf '#!/bin/bash\necho "squeue was called" >> /tmp/calls.log; exit 99\n' > /stub/squeue
chmod +x /stub/*
export PATH=/stub:$PATH
: > /tmp/calls.log
WEND=$(( $(date +%s) + 900 )); [ "$V" = window_ended ] && WEND=$(( $(date +%s) - 1 ))
FENCE=cov2d,rpd_,d2s0,covfix

if [ "$WHICH" = submit ]; then
  # the planted inputs: the bound manifest from a source clone at M, each source holding its pin's text
  /usr/bin/git clone -q --shared /hostgit /tmp/src && /usr/bin/git -C /tmp/src -c advice.detachedHead=false checkout -q $M || exit 50
  ( cd /tmp/src && python3 -B nd-unfolding/s2r/s2r_probe.py manifest --out /tmp/manifest.json ) || exit 51
  python3 - /tmp/manifest.json "$V" <<'EOF' || exit 52
import json, os, sys
for i, e in enumerate(json.load(open(sys.argv[1]))):
    os.makedirs(os.path.dirname(e["src"]), exist_ok=True)
    pin = e["sha256"] if not (sys.argv[2] == "pin_bad" and i == 1) else "0" * 64
    open(e["src"], "w").write(f"STANDIN-PIN:{pin}\n")
EOF
  [ "$V" = out_exists ] && mkdir -p $OUT
  sleep 1; touch /tmp/after-plant   # the outside-OUT check below counts files newer than this
  cp /connect/s2r_submit.sh /dev/shm/s2rc.1.sh
  bash /dev/shm/s2rc.1.sh /dev/shm/s2rc.1.sh $WEND $FENCE; rc=$?
  echo "=== script rc=$rc; /dev/shm copy left: $([ -e /dev/shm/s2rc.1.sh ] && echo yes || echo no)"
  echo "=== $OUT/logs/connect-submit.log"; cat $OUT/logs/connect-submit.log 2>/dev/null | grep -v '^  ' | head -120
  echo "=== tests.log tail"; tail -3 $OUT/logs/tests.log 2>/dev/null
else
  # a finished run's tree, as sbatch_s2r.sh leaves it (stand-in products and records)
  mkdir -p $OUT/logs $OUT/log $OUT/read $OUT/queues
  echo 7000001 > $OUT/logs/run.jobid
  for a in B0 S2R; do for t in nominal A7_gibuu q3; do
    mkdir -p $OUT/runs/$a/$t; echo "stand-in $a $t" > $OUT/runs/$a/$t/s2r_${a}_${t}_s991000.npz; done; done
  ( cd $OUT && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum ) > $OUT/log/SHA256SUMS
  echo '{"tasks": 6, "ended": 6, "rc": 0}' > $OUT/log/DONE
  echo '{"pass": true}' > $OUT/log/pair.json
  echo '{"verdict": "FAIL"}' > $OUT/read/readout.json; echo "S2R readout: FAIL" > $OUT/read/readout.txt
  echo "# q" > $OUT/queues/run.tsv; echo '[]' > $OUT/manifest.json; echo '{}' > $OUT/stage.json; echo cov2d > $OUT/fence.txt
  echo "stand-in" > $OUT/logs/connect-submit.log
  [ "$V" = stop_present ] && echo "pair rc=1" > $OUT/log/STOP
  [ "$V" = sums_bad ] && echo "changed" >> $OUT/runs/S2R/q3/s2r_S2R_q3_s991000.npz
  [ "$V" = extra_product ] && echo x > $OUT/runs/S2R/q3/extra.npz
  [ "$V" = no_readout ] && rm -f $OUT/read/readout.txt
  sleep 1; touch /tmp/after-plant
  cp /connect/s2r_fetch.sh /dev/shm/s2rc.2.sh
  bash /dev/shm/s2rc.2.sh /dev/shm/s2rc.2.sh $WEND $FENCE; rc=$?
  echo "=== script rc=$rc; /dev/shm copy left: $([ -e /dev/shm/s2rc.2.sh ] && echo yes || echo no)"
  echo "=== $OUT/logs/connect-records.log"; cat $OUT/logs/connect-records.log 2>/dev/null | head -60
  [ -f $OUT/fetch-records.tar ] && { mkdir /tmp/x && tar -C /tmp/x -xf $OUT/fetch-records.tar && ( cd /tmp/x/fetch-records && sha256sum -c --quiet RECORDS.SHA256SUMS ) && echo "=== tar RECORDS.SHA256SUMS: OK ($(grep -c . /tmp/x/fetch-records/RECORDS.SHA256SUMS) files)"; }
fi
echo "=== stub calls"; cat /tmp/calls.log
echo "=== files written under /pscratch outside $OUT (newer than the planting):"; find /pscratch -newer /tmp/after-plant ! -path "$OUT" ! -path "$OUT/*" | head
