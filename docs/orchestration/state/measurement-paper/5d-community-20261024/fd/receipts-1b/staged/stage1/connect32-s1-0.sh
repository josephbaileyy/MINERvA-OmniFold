# 1B staged, stage 1, connect 32 (FD-1B-STAGED-BINDING-2 rulings 2, 4-7; FD-1B-STAGED-AMENDMENT-1 section 4, step 1):
# the balance, a fresh clone at M2, the widened stat-before, stage-flux and receipt on the login node at nice 19 under
# /usr/bin/time -v, the bound generator's S1-0 tables, then S1-0's submission (1 node, 8 lanes, 1:00:00), each gated
# on the one before. Placed at $W1/logs and run detached on the login node (setsid nohup); not under set -u (the
# root_6_28 activation aborts under it).
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; W1=$W/stage1; DD1=$W1/deploy; V=$P/fd-1b-inv-20261101
M2=24c83ab839647dd5113847f3de11447eecd9c10e
BANK=$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware; DET=$P/s5p-20260926/bank_detector
NPZ=$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz; BKG=$P/s5c-20260924/runs/p2/bkg_dump.npz
PINS=$P/fd-1b-20261030/pins.json; PINS_SHA=5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248
FC=$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
ROOTF=$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
PREP=$P/fd-f1-20261027/f1b3/prep
GEN=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py
CAP_NODE_H=73.0
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; exit 2; }
[ -d $W ] || stop "$W (stage 0) is absent"
for d in $DD1 $W1/in $W1/unf $W1/lanes $W1/tables; do [ -e $d ] && stop "$d already exists"; done
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"

# 1. The balance (ruling 2): stop if the 73.0 node-h cap is above half of what remains.
echo "== iris"; iris 2>&1 | head -2; row=$(iris 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || stop "could not read the m3246 balance"
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') cap=$CAP_NODE_H"
awk -v b=$bal -v c=$CAP_NODE_H 'BEGIN{exit !(c <= b/2)}' || stop "the cap $CAP_NODE_H is above half the balance $bal: to Joseph"

# 2. The deploy: a fresh clone detached at M2, empty porcelain, the bound blobs (binding 2's table).
mkdir -p $W1/in $W1/unf $W1/lanes $W1/tables || stop mkdir
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $DD1 && git -C $DD1 checkout --quiet --detach $M2 || stop clone
n=$(git -C $DD1 status --porcelain | wc -l); h=$(git -C $DD1 rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M2" ] || stop "deploy not clean at M2"
S=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged
while read -r blob path; do
  got=$(git -C $DD1 hash-object "$path"); echo "blob $got $path"; [ "$got" = "$blob" ] || stop "$path is not the bound blob"
done <<BLOBS
74aa8daced207af0ea8e3b5e0d3136e5535f76a1 nd-unfolding/fd_1b_mc.py
0b08d17384642a6382f2c8069bd29fa2b0ef123f nd-unfolding/tests/test_fd_1b_mc.py
71ca615a67dfbd098852dd713677ad3179617ff6 $GEN
6ca37839374afa3fdf1c43c0ed6e13039409cad9 $S/mutation_mc.py
3004edbcf6112c6d9813459f6b51bc88b70a6d2f $S/mutation_mc.out
1810161d53c6b849d0dce7fb506d88d551d89900 nd-unfolding/fd_1b_null.py
31a88850a7999884150fef402fb0f22cba9005ed nd-unfolding/fd_1b_moded.py
BLOBS
s=$(sha256sum $DD1/nd-unfolding/fd_1b_mc.py | cut -d' ' -f1); echo "fd_1b_mc.py sha256 $s"
[ "$s" = "1a2f825fe4a7f31e800fab96d12fd97e210ea89f11cb0e395bd2bb99ef379a4a" ] || stop "fd_1b_mc.py sha256"

# 3. The environment the jobs use (s5c_array.sh), then the stat list, written before the first read.
source $DD1/setup_salloc_env.sh > $W1/logs/env.log 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
cd $DD1 || stop cd
# Every file a stage-1 job, stage-flux, receipt, null, readout or a control comparison reads that this lane did not
# make: the pinned weight files (pins.json, read through O_NOATIME: the bank's CV, Flux and interaction universes and
# the dump's detector bands), the inputs, background and pins, the flux constraint, the flux ROOT table, F1's two prep
# ratios, and every file under $V/i0/in and $V/i2/unf. The controls compare with S1's committed products in this
# deploy (fd/s1/readout/s1_assembly), which this connect cloned.
python3 -B - $PINS $NPZ $BKG $FC $ROOTF $PREP/bridged/genie_v3_g18.json $PREP/bridged/genie_v3_ar23.json > $W1/logs/stage1-sources.txt <<'PYL' || stop "source list"
import json, sys
sys.path.insert(0, "nd-unfolding")
import fd_1b_inv as inv
with inv.open_noatime(sys.argv[1]) as fh:
    pins = json.loads(fh.read().decode())
for p in sorted(set(pins["files"]) | set(sys.argv[1:])):
    print(p)
print(f"pinned={len(pins['files'])} named={len(set(sys.argv[1:]) - set(pins['files']))}", file=sys.stderr)
PYL
find $V/i0/in $V/i2/unf -type f | LC_ALL=C sort >> $W1/logs/stage1-sources.txt
echo "sources=$(wc -l < $W1/logs/stage1-sources.txt) i0_in=$(find $V/i0/in -type f | wc -l) i2_unf=$(find $V/i2/unf -type f | wc -l) unique=$(LC_ALL=C sort -u $W1/logs/stage1-sources.txt | wc -l)"
xargs -a $W1/logs/stage1-sources.txt stat -c '%X %Y %s %n' > $W1/logs/stat-before.txt || stop "a source is missing"
echo "stat-before lines=$(wc -l < $W1/logs/stat-before.txt)"

# 4. stage-flux, then receipt: login node, nice 19, /usr/bin/time -v (ruling 5). A kill by NERSC's login limits stops
#    here; the pre-authorized one-node fallback is a separate step.
nice -n 19 /usr/bin/time -v python3 nd-unfolding/fd_1b_mc.py stage-flux --root $ROOTF --out $W1/in/flux_universes.npz \
  > $W1/logs/stage-flux.out 2> $W1/logs/stage-flux.time; rc=$?
cat $W1/logs/stage-flux.out; grep -E 'Elapsed|Maximum resident|Exit status' $W1/logs/stage-flux.time
[ "$rc" = "0" ] || stop "stage-flux rc=$rc"
FSHA=$(sha256sum $W1/in/flux_universes.npz | cut -d' ' -f1); echo "flux_universes.npz sha256 $FSHA"
nice -n 19 /usr/bin/time -v python3 nd-unfolding/fd_1b_mc.py receipt --npz $NPZ --bkg $BKG --bank $BANK --detector-dir $DET \
  --pins $PINS --expect-pins-sha256 $PINS_SHA --flux-constraint $FC --flux-table $W1/in/flux_universes.npz \
  --expect-flux-table-sha256 $FSHA --out $W1/receipt.json > $W1/logs/receipt.out 2> $W1/logs/receipt.time; rc=$?
cat $W1/logs/receipt.out; grep -E 'Elapsed|Maximum resident|Exit status|signal' $W1/logs/receipt.time
[ "$rc" = "0" ] || { tail -5 $W1/logs/receipt.time; stop "receipt rc=$rc"; }
python3 -B - $W1/receipt.json <<'PYR' || stop "the receipt holds the bulk"
import json, sys
r = json.load(open(sys.argv[1]))
c = r["composite"]
print("receipt verdict", r["verdict"], "bound", r["n1_bound"], "n_draws", c["n_draws"], "cap", c["candidate_cap"])
print("single max_abs_ratio", r["max_abs_ratio"])
for k, v in c["arrays"].items():
    print("composite", k, "all_draws_max", v["all_draws_max"], "all_draws_rows_above", v["all_draws_rows_above"], "declared", v["declared"])
print("atime moved", r["atime"]["moved"], "opened", len(r["atime"]["files"]))
sys.exit(0 if r["verdict"] == "PASS" and not c["stop"] and not r["atime"]["moved"] else 1)
PYR
sha256sum $W1/receipt.json
xargs -a $W1/logs/stage1-sources.txt stat -c '%X %Y %s %n' > $W1/logs/stat-after-receipt.txt
if cmp -s $W1/logs/stat-before.txt $W1/logs/stat-after-receipt.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $W1/logs/stat-before.txt))"
else diff $W1/logs/stat-before.txt $W1/logs/stat-after-receipt.txt | head -20; stop "a source's stat moved (a deviation, not restored)"; fi

# 5. The bound generator's tables (plug-in yes; the bulk table waits for the push digest).
python3 -B $DD1/$GEN $DD1 $W1/tables yes $FSHA || stop tables
cd $W1/tables && sha256sum s1-0-steps.tsv tasks-s1-0.tsv > SHA256SUMS && cat SHA256SUMS
[ "$(grep -vc '^#' s1-0-steps.tsv)" = "8" ] && [ "$(grep -vc '^#' tasks-s1-0.tsv)" = "8" ] || stop "S1-0 is not 8 lanes"
[ -e s1-bulk-steps.tsv ] && stop "a bulk table was made before the push digest"
cut -f1-6 s1-0-steps.tsv

# 6. S1-0's submission (binding 2 ruling 2: 1 node, 1:00:00, 1.0 node-h).
[ "$(squeue --me -h -o %j | grep -c '^fd1b')" = "0" ] || stop "an fd1b job is queued"
cat > $W1/logs/submit-s1-0.txt <<SUB
sbatch -A m3246 -q regular -C cpu -t 01:00:00 -J fd1b_mc_s1_0 -o $W1/logs/%x_%j.out $DD1/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh $DD1 $M2 $W1/tables/tasks-s1-0.tsv $W1/lanes 32 56G 0 7 inherit
SUB
cat $W1/logs/submit-s1-0.txt
bash $W1/logs/submit-s1-0.txt > $W1/logs/submit-s1-0.out 2>&1; echo "rc=$?" >> $W1/logs/submit-s1-0.out
cat $W1/logs/submit-s1-0.out
squeue --me -h -o "%i %j %T %l %D %R"
echo "== hpssquota (read only; the tars wait for maintenance to clear)"; timeout 60 hpssquota 2>&1 | tail -3
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
