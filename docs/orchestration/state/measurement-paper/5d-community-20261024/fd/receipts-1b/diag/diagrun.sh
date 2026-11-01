P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030; M3=ea2977613cd051dc3c2b321c7fad44f7a6d3ef2c; DD=$B/deploy/diag
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
CON=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
for x in $DD $B/score/diag.json $B/logs/diag.log; do [ -e "$x" ] && stop "$x already exists"; done
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $DD && git -C $DD checkout --quiet --detach $M3 || stop clone
n=$(git -C $DD status --porcelain | wc -l); h=$(git -C $DD rev-parse HEAD); echo "D1 porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M3" ] || stop "D1 deploy not clean at M3"
echo "D1 fd_1b_diag.py sha256 $(sha256sum $DD/nd-unfolding/fd_1b_diag.py | cut -c1-16)  gate-d $(sha256sum $DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/stage2/run/score/gate-d.json | cut -c1-16)"
echo "D1 derivation products: $(ls $B/runs/derivation/*.npz | wc -l)"
t0=$(date +%s)
nice -n 19 $PY $DD/nd-unfolding/fd_1b_diag.py --derivation $B/runs/derivation --tag fd1b_derivation \
  --s1-npz $P/s1-20261024/s1_assembly.npz --flux-constraint $CON \
  --gate-d $DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/stage2/run/score/gate-d.json \
  --out $B/score/diag.json > $B/logs/diag.log 2>&1; echo rc=$? >> $B/logs/diag.log
echo "D2 wall_s=$(( $(date +%s) - t0 ))"; grep -v "UserWarning\|warnings.warn" $B/logs/diag.log | tail -5
ls -l $B/score/diag.json 2>&1; sha256sum $B/score/diag.json 2>&1
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
