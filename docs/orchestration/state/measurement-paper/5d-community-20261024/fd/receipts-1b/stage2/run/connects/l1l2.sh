P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030; M=b43d9f23e54d633c19ba7480094fe29874834d35; DP=$B/deploy/stage2-pins
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ -e "$DP" ] || [ -e "$B/pins.json" ]; then echo "REFUSE: $DP or pins.json already exists"; exit 3; fi
mkdir -p $B/deploy $B/logs $B/runs $B/score
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DP" && git -C "$DP" checkout --quiet --detach $M
echo "clone_rc=$?"
n=$(git -C "$DP" status --porcelain | wc -l); h=$(git -C "$DP" rev-parse HEAD)
echo "L1 porcelain_lines=$n head=$h"
if [ "$n" != "0" ] || [ "$h" != "$M" ]; then echo "L1 STOP"; exit 2; fi
S=$DP/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt
cd $B && nohup setsid bash -c "nice -n 19 $PY $DP/nd-unfolding/fd_1b_toys.py pins --bank $P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware --detector-dir $P/s5p-20260926/bank_detector --manifest $S --detector-receipt $P/s5p-20260926/bank_detector/detector-dump.json --out $B/pins.json > $B/logs/l2-pins.log 2>&1; echo rc=\$? >> $B/logs/l2-pins.log; date -u +%Y-%m-%dT%H:%M:%SZ >> $B/logs/l2-pins.log" > /dev/null 2>&1 < /dev/null &
echo "L2 started pid=$! at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
