# 1B stage 2, amendment 1: A3 (the deploy at R2), A4 (preflight), A5 (the quarantine). Login node only.
P=/pscratch/sd/j/josephrb; B=$P/fd-1b-20261030
M2=833288c4dffc22a3aa795cfc72c1ace82fef58f6; R2=e3c91978bced44ad85b97f50c17acd21429bfbcc
PINS=5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248
D2=$B/deploy/stage2-r
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
R1B=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware; DET=$P/s5p-20260926/bank_detector
Q0=d7b6d0207c05e1c81eee316cffa66ac570ae56ce5a96b918fae835022a46ac14
Q4=a19f14db359b15949789f21515dca0cda7c4038b0d5c66c79fa87cfbbaaff0af
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }

# A3
[ -e "$D2" ] && stop "$D2 already exists"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D2" && git -C "$D2" checkout --quiet --detach $R2 || stop "clone"
n=$(git -C "$D2" status --porcelain | wc -l); h=$(git -C "$D2" rev-parse HEAD)
echo "A3 porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$R2" ] || stop "A3 deploy not clean at R2"
extra=$(git -C "$D2" diff --name-only $M2 $R2 | grep -v -e "^$R1B/tables/fd1b-2a-r-steps.tsv$" -e "^$R1B/tables/tasks-fd1b-2a-r.tsv$" -e '^docs/orchestration/MANIFEST.tsv$')
echo "A3 diff_M2_R2_outside=[$extra]"
[ -z "$extra" ] || stop "M2..R2 touches other paths"

# A4: preflight
$PY $D2/nd-unfolding/fd_1b_tasks.py submit --job 2a-r --deploy $D2 --pin $R2 > $B/logs/a4-submit-2a-r.txt 2>&1 || { cat $B/logs/a4-submit-2a-r.txt; stop "submit 2a-r rc"; }
lines=$(grep -c '^sbatch ' $B/logs/a4-submit-2a-r.txt); tl=$(grep -c -- " -t 01:00:00 " $B/logs/a4-submit-2a-r.txt)
tab=$(awk '{for(i=1;i<=NF;i++) if($i ~ /tasks-fd1b-.*\.tsv$/) print $i}' $B/logs/a4-submit-2a-r.txt | sort -u)
echo "A4 submit 2a-r lines=$lines limit_ok=$tl table=$( [ -f "$tab" ] && echo present || echo MISSING ) pin_ok=$(grep -c " $R2 " $B/logs/a4-submit-2a-r.txt)"
[ "$lines" = "1" ] && [ "$tl" = "1" ] && [ -f "$tab" ] || stop "submit line for 2a-r"
got=$(sha256sum $B/pins.json | cut -d' ' -f1); echo "A4 pins_sha256=$got"
[ "$got" = "$PINS" ] || stop "pins.json changed"
$PY -c "import json, sys; from pathlib import Path; sys.path.insert(0, '$D2/nd-unfolding'); import fd_1b_toys as t; t.check_pins(json.load(open('$B/pins.json')), Path('$BANK'), Path('$DET')); print('pins unchanged')" > $B/logs/a4-pins.log 2>&1
rc=$?; echo "rc=$rc" >> $B/logs/a4-pins.log; echo "A4 check_pins rc=$rc: $(head -1 $B/logs/a4-pins.log)"
[ "$rc" = "0" ] || stop "check_pins"
$PY $D2/$R1B/stage1/derivation_check.py --deploy $D2 > $B/logs/a4-derivation-check.json 2> $B/logs/a4-derivation-check.err
rc=$?; echo "A4 derivation_check rc=$rc"; [ "$rc" = "0" ] || stop "derivation check"
diff <(sed '1,3d;$d' $D2/$R1B/stage1/derivation-check.out) $B/logs/a4-derivation-check.json > $B/logs/a4-derivation-check.diff
rc=$?; echo "A4 derivation_check diff rc=$rc lines=$(wc -l < $B/logs/a4-derivation-check.diff)"
[ "$rc" = "0" ] || stop "derivation check differs from the committed output"
squeue --me -h -o %j > $B/logs/a4-squeue.txt 2>&1
echo "A4 squeue jobs=$(wc -l < $B/logs/a4-squeue.txt) fd1b=$(grep -c '^fd1b' $B/logs/a4-squeue.txt)"
[ "$(grep -c '^fd1b' $B/logs/a4-squeue.txt)" = "0" ] || stop "an fd1b job is queued"
iris > $B/logs/a4-iris.txt 2>&1
echo "A4 iris rc=$? at $(date -u +%Y-%m-%dT%H:%M:%SZ):"; grep -E "^Project|^m3246 " $B/logs/a4-iris.txt
rem=$(awk '$1=="m3246" {print $5 - $4}' $B/logs/a4-iris.txt)
echo "A4 m3246 remaining=$rem half=$(awk -v r=$rem 'BEGIN{print r/2}')"
awk -v r="$rem" 'BEGIN{exit !(r/2 >= 3.0)}' || stop "half of the remaining balance is under 3.0 node-h"
echo "A4 the 10 unmade products are absent:"
for f in pilot-half/fd1b_pilot_half_s260000{1,2,3,5,6,7}.npz derivation/fd1b_derivation_{2p2h_0,2p2h_1,2p2h_2,AGKYxF1pi_0}.npz; do
  [ -e "$B/runs/$f" ] && stop "$f already exists"; done; echo "  yes"

# A5: the quarantine (moved, not deleted)
mkdir -p $B/quarantine
[ -e $B/quarantine/fd1b_pilot_half_s2600000.npz ] || [ -e $B/quarantine/fd1b_pilot_half_s2600004.npz ] && stop "quarantine already holds them"
mv $B/runs/pilot-half/fd1b_pilot_half_s2600000.npz $B/runs/pilot-half/fd1b_pilot_half_s2600004.npz $B/quarantine/ || stop "mv"
sha256sum $B/quarantine/*.npz > $B/logs/a5-quarantine.sha256; cat $B/logs/a5-quarantine.sha256
q0=$(sha256sum $B/quarantine/fd1b_pilot_half_s2600000.npz | cut -d' ' -f1); q4=$(sha256sum $B/quarantine/fd1b_pilot_half_s2600004.npz | cut -d' ' -f1)
[ "$q0" = "$Q0" ] && [ "$q4" = "$Q4" ] || stop "quarantined digests differ from the amendment's"
left=$(ls $B/runs/pilot-half/*.npz 2>/dev/null | wc -l); echo "A5 pilot-half npz left=$left"
[ "$left" = "0" ] || stop "pilot-half still holds products"
echo "A5 done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
