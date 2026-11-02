# 1B investigation, step I0 (FD-1B-INV-BINDING ruling 7): login37, nice -n 19, 0 node-h, from a fresh clone at M.
P=/pscratch/sd/j/josephrb; V=$P/fd-1b-inv-20261101; DD=$V/deploy; M=b1c615f12fca5f8597d34750b2c074f1fd7b2cdd
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
R=$DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/stage2/run/score/gate-d.json
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $V ] && stop "$V already exists"
mkdir -p $V/logs $V/i0 || stop mkdir
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $DD && git -C $DD checkout --quiet --detach $M || stop clone
n=$(git -C $DD status --porcelain | wc -l); h=$(git -C $DD rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
echo "fd_1b_inv.py sha256 $(sha256sum $DD/nd-unfolding/fd_1b_inv.py | cut -c1-16)  gate-d $(sha256sum $R | cut -c1-16)"
# the staging spec, with the declared digests of the two pinned inputs taken from the bound code
nice -n 19 $PY - "$DD" "$V/i0/spec.json" <<'PYEOF' || stop spec
import glob, json, sys
dd, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, dd + "/nd-unfolding")
import fd_1b_score as fs, s1_assemble as sa
P = "/pscratch/sd/j/josephrb"
spec = [{"role": "derivation", "src": p, "dest": "derivation/" + p.rsplit("/", 1)[1]}
        for p in sorted(glob.glob(P + "/fd-1b-20261030/runs/derivation/fd1b_derivation_*.npz"))]
spec += [{"role": "s1-uni", "src": p, "dest": "uni/" + p.rsplit("/", 1)[1]}
         for p in sorted(glob.glob(P + "/s1-20261024/runs/uni/S1_*.npz"))]
spec += [{"role": "s1-assembly", "src": P + "/s1-20261024/s1_assembly.npz", "dest": "s1/s1_assembly.npz",
          "sha256": fs.S1_NPZ_SHA256},
         {"role": "flux-constraint", "src": P + "/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
          "dest": "flux_constraint.txt", "sha256": sa.CONSTRAINT_SHA256}]
num = P + "/s5p-20260926/runs/s2/num"
for role, sub, stem in (("jitter-data", "data", "data"), ("jitter-nom", "nom", "nom")):
    for j in ["-"] + [str(k) for k in range(1, 21)]:
        name = f"{stem}_b-_j{j}.npz"
        spec.append({"role": role, "src": f"{num}/{sub}/{name}", "dest": f"{role}/{name}"})
json.dump(spec, open(out, "w"), indent=1)
print(f"spec items={len(spec)}")
PYEOF
$PY -c "import json,sys; [print(x['src']) for x in json.load(open('$V/i0/spec.json'))]" > $V/i0/sources.txt
xargs -a $V/i0/sources.txt stat -c '%X %Y %s %n' > $V/logs/stat-before.txt; echo "stat-before lines=$(wc -l < $V/logs/stat-before.txt)"
t0=$(date +%s)
nice -n 19 $PY $DD/nd-unfolding/fd_1b_inv.py stage --spec $V/i0/spec.json --out $V/i0/in > $V/logs/stage.log 2>&1
echo "stage rc=$? wall_s=$(( $(date +%s) - t0 ))"; tail -2 $V/logs/stage.log
[ -f $V/i0/in/staged.json ] || stop "no staged.json"
t1=$(date +%s)
nice -n 19 $PY $DD/nd-unfolding/fd_1b_inv.py i0 --staged $V/i0/in \
  --definition $DD/nd-unfolding/pv-ladder/readouts/h2_definition.json --gate-d $R \
  --receipt $DD/docs/orchestration/state/s5p/stage2/stage2_receipt.json --out $V/i0/i0.json > $V/logs/i0.log 2>&1
echo "i0 rc=$? wall_s=$(( $(date +%s) - t1 ))"; grep -v "UserWarning\|warnings.warn" $V/logs/i0.log | tail -4
xargs -a $V/i0/sources.txt stat -c '%X %Y %s %n' > $V/logs/stat-after.txt
if cmp -s $V/logs/stat-before.txt $V/logs/stat-after.txt; then echo "atime/mtime/size: UNCHANGED on all $(wc -l < $V/logs/stat-after.txt) sources"
else echo "DEVIATION: stat changed:"; diff $V/logs/stat-before.txt $V/logs/stat-after.txt | head -20; fi
ls -l $V/i0/i0.json 2>&1; sha256sum $V/i0/i0.json $V/i0/in/staged.json 2>&1
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
