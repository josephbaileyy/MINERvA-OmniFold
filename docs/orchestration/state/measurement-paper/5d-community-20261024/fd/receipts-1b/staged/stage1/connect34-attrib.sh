# 1B staged, stage 1, connect 34 (the director's ruling on connect 32's STOP, item 2): N1's rows above on the declared
# draws, attributed by band and |a_CV|. DESCRIPTIVE ONLY. On the login node at nice 19 under /usr/bin/time -v, from
# connect 32's deploy at M2 (re-checked clean) with attrib/n1_attrib.py placed beside it (its sha256 checked against
# the committed one); every input through O_NOATIME, connect 32's 1,513-path list stat'ed before and after. Writes only
# under $W1/attrib. Placed there and run detached (setsid nohup), as connect 32. No HPSS, no submission.
P=/pscratch/sd/j/josephrb; W1=$P/fd-1b-staged-20261102/stage1; DD1=$W1/deploy; A=$W1/attrib
M2=24c83ab839647dd5113847f3de11447eecd9c10e
ATTRIB_SHA=954b44c89b3b7a2acb69956664e6a07ebea7de4b2a4afd3350f99fec5978f2f4
RECEIPT_SHA=c8fcd7f97b95ae39824d3cea476782f46dcef5fdcdde54f325d8906607b2abed
FLUX_SHA=cdc3da788c385da72826b2a74b1987320bbe399af212722826914df4d2fe15a5
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware; DET=$P/s5p-20260926/bank_detector
NPZ=$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz; BKG=$P/s5c-20260924/runs/p2/bkg_dump.npz
PINS=$P/fd-1b-20261030/pins.json; PINS_SHA=5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248
FC=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; exit 2; }
[ -e $A/n1_attrib.json ] && stop "n1_attrib.json already exists"
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
n=$(git -C $DD1 status --porcelain | wc -l); h=$(git -C $DD1 rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M2" ] || stop "deploy not clean at M2"
s=$(sha256sum $DD1/nd-unfolding/fd_1b_mc.py | cut -d' ' -f1); echo "fd_1b_mc.py sha256 $s"
[ "$s" = "1a2f825fe4a7f31e800fab96d12fd97e210ea89f11cb0e395bd2bb99ef379a4a" ] || stop "fd_1b_mc.py sha256"
s=$(sha256sum $A/n1_attrib.py | cut -d' ' -f1); echo "n1_attrib.py sha256 $s"; [ "$s" = "$ATTRIB_SHA" ] || stop "n1_attrib.py sha256"
for f in "$W1/receipt.json $RECEIPT_SHA" "$W1/in/flux_universes.npz $FLUX_SHA"; do
  set -- $f; got=$(sha256sum $1 | cut -d' ' -f1); echo "$1 sha256 $got"; [ "$got" = "$2" ] || stop "$1 digest"
done
source $DD1/setup_salloc_env.sh > $A/env.log 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
cd $DD1 || stop cd
xargs -a $W1/logs/stage1-sources.txt stat -c '%X %Y %s %n' > $A/stat-before.txt || stop "a source is missing"
echo "stat-before lines=$(wc -l < $A/stat-before.txt)"
nice -n 19 /usr/bin/time -v python3 $A/n1_attrib.py --npz $NPZ --bkg $BKG --bank $BANK --detector-dir $DET \
  --pins $PINS --expect-pins-sha256 $PINS_SHA --flux-constraint $FC --flux-table $W1/in/flux_universes.npz \
  --expect-flux-table-sha256 $FLUX_SHA --receipt $W1/receipt.json --expect-receipt-sha256 $RECEIPT_SHA \
  --out $A/n1_attrib.json > $A/n1_attrib.out 2> $A/n1_attrib.time; rc=$?
cat $A/n1_attrib.out; grep -E 'Elapsed|Maximum resident|File system inputs|Exit status|signal' $A/n1_attrib.time
echo "n1_attrib rc=$rc"; [ "$rc" = "0" ] || tail -5 $A/n1_attrib.time
[ -e $A/n1_attrib.json ] && sha256sum $A/n1_attrib.json
xargs -a $W1/logs/stage1-sources.txt stat -c '%X %Y %s %n' > $A/stat-after.txt
if cmp -s $A/stat-before.txt $A/stat-after.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $A/stat-before.txt))"
else echo "sources CHANGED (a deviation, not restored):"; diff $A/stat-before.txt $A/stat-after.txt | head -40; fi
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
