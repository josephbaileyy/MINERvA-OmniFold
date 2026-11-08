#!/bin/bash
# coverage-5b-audit: RS1 dry-run tie-invariance read (RS1-BINDING-2 ruling 2), run only after ENS1's binding merges.
# Login node, 0 node-h. Reads four RS1 dry-run files through dd iflag=noatime copies; compares on the copies only.
set -eo pipefail
date -u +%FT%TZ; hostname
# 1. the COV2D fence (the embedded logic of cov2d_fence.sh)
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l') || { echo "FENCE: squeue failed; treat as RUNNING"; exit 3; }
hits=$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^cov2d-/')
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present:"; printf '%s\n' "$hits"; exit 3; fi
echo "FENCE: no cov2d-* job queued or running"
R=/pscratch/sd/j/josephrb/rs1-20261106
W=/pscratch/sd/j/josephrb/c5b-tieread-20261107
[ ! -e "$W" ] || { echo "REFUSE: $W exists"; exit 4; }
mkdir "$W"
FILES="runs/A0/rs1_A0_b-_j0.npz runs/A0/rs1_A0_b-_j0.trace.json.gz runs/V/rs1_V_b-_j1.npz runs/V/rs1_V_b-_j1.trace.json.gz"
# 2. stat before, noatime copies, stat after (atime must not move)
for f in $FILES; do stat -c "BEFORE %X %Y %s %n" "$R/$f"; done
for f in $FILES; do dd if="$R/$f" of="$W/$(basename "$f")" iflag=noatime bs=4M status=none; done
for f in $FILES; do stat -c "AFTER  %X %Y %s %n" "$R/$f"; done
# 3. digests compared against #891's SHA256SUMS, as a separate step
cat > "$W/expected.sha256" <<'SUMS'
73ed3bd01bcd852754f7d0443d86a806f41d39268b12974eefce16dfffea25cd  rs1_A0_b-_j0.npz
640cfb8f4d4d3fed41974966fd796c342a34a2ca006037448afb959fc025fd36  rs1_A0_b-_j0.trace.json.gz
d0c0782940ee923a1687af5b03b19f380242d12ea6ad7747196fee23ed452284  rs1_V_b-_j1.npz
f1a8c2f9618293ddc6909f9765e87a236adecf92e68fd928bd7b4ff49b8b8b28  rs1_V_b-_j1.trace.json.gz
SUMS
( cd "$W" && sha256sum -c expected.sha256 ) || { echo "STOP: a copy is off its pin"; rm -rf -- /pscratch/sd/j/josephrb/c5b-tieread-20261107; exit 5; }
echo "DIGESTS: 4 of 4 match #891"
# 4. the comparison, on the copies only
rc=0
/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python -I - "$W" <<'PY' || rc=$?
import gzip, json, sys
import numpy as np
W = sys.argv[1]
def prod(n):
    z = np.load(f"{W}/{n}.npz", allow_pickle=False)
    return np.asarray(z["xsec_flat"], float), json.loads(str(z["meta"]))
def side(n):
    with gzip.open(f"{W}/{n}.trace.json.gz", "rt") as fh:
        return json.load(fh)
xb, mb = prod("rs1_A0_b-_j0"); xv, mv = prod("rs1_V_b-_j1")
tb, tv = side("rs1_A0_b-_j0"), side("rs1_V_b-_j1")
out = {"base": {"arm": mb["rounding_mechanism"]["arm"], "jitter_seed": mb["rounding_mechanism"]["jitter_seed"]},
       "V": {"arm": mv["rounding_mechanism"]["arm"], "jitter_seed": mv["rounding_mechanism"]["jitter_seed"]}}
eq = bool(np.array_equal(xb, xv))
nz = xb != 0
rel = np.abs(xv[nz] / xb[nz] - 1) if nz.any() else np.array([0.0])
out["xsec_flat"] = {"bitwise_equal": eq, "n": int(xb.size), "n_differ": int((xb != xv).sum()),
                    "max_rel_diff": float(rel.max()), "median_rel_diff_of_differing":
                    float(np.median(rel[rel > 0])) if (rel > 0).any() else 0.0}
def struct(tree):   # everything but the split thresholds
    return [n[:2] + n[3:] if n[0] == "s" else list(n) for n in tree]
def compare_fits(fa, fb):
    res = {"n_fits": [len(fa), len(fb)], "identical": 0, "threshold_only": 0, "structure_differs": 0, "first": None}
    for i, (a, b) in enumerate(zip(fa, fb)):
        if a["role"] != b["role"]:
            res["first"] = res["first"] or {"fit": i, "what": f"role {a['role']} vs {b['role']}"}
            res["structure_differs"] += 1; continue
        if a["trees"] == b["trees"]:
            res["identical"] += 1; continue
        same_struct = len(a["trees"]) == len(b["trees"]) and all(struct(x) == struct(y) for x, y in zip(a["trees"], b["trees"]))
        if same_struct:
            res["threshold_only"] += 1; continue
        res["structure_differs"] += 1
        if res["first"] is None:
            for t, (x, y) in enumerate(zip(a["trees"], b["trees"])):
                if struct(x) != struct(y):
                    k = next((j for j, (p, q) in enumerate(zip(struct(x), struct(y))) if p != q), min(len(x), len(y)))
                    res["first"] = {"fit": i, "role": a["role"], "tree": t, "node": k,
                                    "base": x[k] if k < len(x) else None, "V": y[k] if k < len(y) else None}
                    break
            else:
                res["first"] = {"fit": i, "role": a["role"], "what": f"tree count {len(a['trees'])} vs {len(b['trees'])}"}
    return res
out["fits"] = compare_fits(tb.get("fits", []), tv.get("fits", []))
rb, rv = tb.get("refinement_tree"), tv.get("refinement_tree")
out["refinement_tree"] = (None if rb is None or rv is None else
                          compare_fits([{"role": "refine", "trees": rb}], [{"role": "refine", "trees": rv}]))
print("TIEREAD " + json.dumps(out, sort_keys=True))
PY
echo "compare rc=$rc"
# 5. remove the scratch by its literal path
rm -rf -- /pscratch/sd/j/josephrb/c5b-tieread-20261107 && echo "REMOVED /pscratch/sd/j/josephrb/c5b-tieread-20261107"
exit $rc
