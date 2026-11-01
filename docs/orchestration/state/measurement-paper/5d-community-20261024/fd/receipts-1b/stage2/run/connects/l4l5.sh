# 1B stage 2, L4 (the run deploy at R) and L5 (preflight), FD-1B-STAGE2-DECLARATION.md section 3. Login node only.
P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030
M=b43d9f23e54d633c19ba7480094fe29874834d35; R=664c38dbffdca4fe3873a5ebf61cb2f949005b59
PINS=5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248
D=$B/deploy/stage2
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
R1B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware; DET=$P/s5p-20260926/bank_detector
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }

# L4
[ -e "$D" ] && stop "$D already exists"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D" && git -C "$D" checkout --quiet --detach $R || stop "clone"
n=$(git -C "$D" status --porcelain | wc -l); h=$(git -C "$D" rev-parse HEAD)
echo "L4 porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$R" ] || stop "L4 deploy not clean at R"
extra=$(git -C "$D" diff --name-only $M $R | grep -v -e "^$R1B/tables/" -e "^$R1B/stage2/" -e '^docs/orchestration/MANIFEST.tsv$')
echo "L4 diff_M_R_outside_L3=[$extra]"
[ -z "$extra" ] || stop "M..R touches paths outside L3"

# L5: submit lines (nodes and limits from section 4)
for spec in 2a-0:1:01:00:00 2a:3:02:40:00 2b:2:02:30:00 2c:3:03:00:00; do
  J=${spec%%:*}; rest=${spec#*:}; N=${rest%%:*}; T=${rest#*:}
  $PY $D/nd-unfolding/fd_1b_tasks.py submit --job $J --deploy $D --pin $R > $B/logs/l5-submit-$J.txt 2>&1 || stop "submit $J rc"
  lines=$(grep -c '^sbatch ' $B/logs/l5-submit-$J.txt); tlim=$(grep -c -- " -t $T " $B/logs/l5-submit-$J.txt)
  tab=$(awk '{for(i=1;i<=NF;i++) if($i ~ /tasks-fd1b-.*\.tsv$/) print $i}' $B/logs/l5-submit-$J.txt | sort -u)
  echo "L5 submit $J lines=$lines want=$N limit_ok=$tlim table=$( [ -f "$tab" ] && echo present || echo MISSING ) pin_ok=$(grep -c " $R " $B/logs/l5-submit-$J.txt)"
  [ "$lines" = "$N" ] && [ "$tlim" = "$N" ] && [ -f "$tab" ] || stop "submit lines for $J"
done

# L5: the pins file
got=$(sha256sum $B/pins.json | cut -d' ' -f1); echo "L5 pins_sha256=$got"
[ "$got" = "$PINS" ] || stop "pins.json changed"
$PY -c "import json, sys; from pathlib import Path; sys.path.insert(0, '$D/nd-unfolding'); import fd_1b_toys as t; t.check_pins(json.load(open('$B/pins.json')), Path('$BANK'), Path('$DET')); print('pins unchanged')" > $B/logs/l5-pins.log 2>&1
rc=$?; echo "rc=$rc" >> $B/logs/l5-pins.log; echo "L5 check_pins rc=$rc: $(head -1 $B/logs/l5-pins.log)"
[ "$rc" = "0" ] || stop "check_pins"

# L5: the derivation check against its committed output
$PY $D/$R1B/stage1/derivation_check.py --deploy $D > $B/logs/l5-derivation-check.json 2> $B/logs/l5-derivation-check.err
rc=$?; echo "L5 derivation_check rc=$rc"
[ "$rc" = "0" ] || stop "derivation check"
diff <(sed '1,3d;$d' $D/$R1B/stage1/derivation-check.out) $B/logs/l5-derivation-check.json > $B/logs/l5-derivation-check.diff
rc=$?; echo "L5 derivation_check diff rc=$rc lines=$(wc -l < $B/logs/l5-derivation-check.diff)"
[ "$rc" = "0" ] || stop "derivation check differs from the committed output"

# L5: the queue and the balance
squeue --me -h -o %j > $B/logs/l5-squeue.txt 2>&1
echo "L5 squeue jobs=$(wc -l < $B/logs/l5-squeue.txt) fd1b=$(grep -c '^fd1b' $B/logs/l5-squeue.txt)"
[ "$(grep -c '^fd1b' $B/logs/l5-squeue.txt)" = "0" ] || stop "an fd1b job is already queued"
iris > $B/logs/l5-iris.txt 2>&1
echo "L5 iris rc=$? at $(date -u +%Y-%m-%dT%H:%M:%SZ):"; head -12 $B/logs/l5-iris.txt
echo "L5 done"
