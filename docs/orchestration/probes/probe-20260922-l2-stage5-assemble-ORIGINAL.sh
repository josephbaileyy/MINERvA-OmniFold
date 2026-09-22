#!/bin/bash
# L2 stage 5: assemble the offset-1200 member's covariance with ITS OWN lateral block.
#
# ⚠ EXACTLY ONE ROW OF THE MANIFEST CHANGES. member_k001200's z-manifest is copied verbatim and
# only `active` is repointed at the member candidate built from the member's own ten endpoint
# unfolds at seed 1242. stat/ml/support/throw/null/central/parent are byte-for-byte the same
# objects member_k001200 was graded with. That is what makes the re-grade attributable to the five
# lateral bands and to nothing else.
#
# ⚠ WHY THIS BUILDS AT THE CURRENT REVISION AND NOT AT d64257c3, WHICH BUILT BOTH GRADED MEMBERS.
# I checked for the confound rather than assuming either way. The ONLY difference in z_build.py
# between d64257c3 and now is `--no-ext-diff` added to a `git show` that computes the receipt's
# code-identity block -- it touches no covariance arithmetic, and z_assembly.py, z_statistics.py
# and z_grade.py are unchanged between the two revisions. So the assembly math is identical.
# And the flag is not optional: its own comment records that mnv_guarded_run.py REFUSES
# `git show` without it, so a build at d64257c3 dies under the guard (job 58358282 is that
# failure). Forcing the old revision would trade an inert difference for a broken run.
#
# The consequence is a PROVENANCE difference between the two members' receipts -- member 0 records
# d64257c3, this one records its own revision -- and it is stated rather than hidden.
set -o pipefail
export HOME=/global/homes/j/josephrb
WT=/pscratch/sd/j/josephrb/MINERvA-OmniFold-l2-20260921
D=/pscratch/sd/j/josephrb/MINERvA-OmniFold
SRC=/pscratch/sd/j/josephrb/z2m-products/member_k001200
OUT=/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals
CAND="$WT/nd-unfolding/mii/member_k001200/active_universe_5d/standard/candidate/std_final5_candidate.root"

[[ -s "$CAND" ]] || { echo "[stage5] ABORT: no member candidate at $CAND"; exit 2; }
mkdir -p "$OUT"
source "$WT/setup_salloc_env.sh" >/dev/null 2>&1
cd "$WT/nd-unfolding"

python3 - "$SRC/z-manifest.json" "$CAND" "$OUT/z-manifest.json" <<'PYEOF'
import hashlib, json, sys
src, cand, dst = sys.argv[1], sys.argv[2], sys.argv[3]
m = json.load(open(src))
h = hashlib.sha256()
with open(cand, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""):
        h.update(b)
new = h.hexdigest()
old = m["sources"]["active"]["sha256"]
assert old != new, (
    "the member candidate has the SAME sha256 as the baseline candidate the graded members "
    "share. That means the member's own laterals never reached the build and this assembly "
    "would measure nothing: " + new)
m["sources"]["active"] = {"format": "root", "path": cand, "sha256": new}
m.setdefault("run", {})["id"] = "l2-laterals-k1200-20260921"
json.dump(m, open(dst, "w"), indent=2, sort_keys=True)
print("[stage5] active swapped")
print("  was:", old, "(shared baseline candidate)")
print("  now:", new, "(member k=1200 laterals at seed 1242)")
for k, v in sorted(m["sources"].items()):
    if k != "active":
        print(f"  unchanged {k:8s} {v['sha256'][:16]}")
PYEOF
[[ $? -eq 0 ]] || { echo "[stage5] ABORT: manifest construction refused"; exit 3; }

echo "[stage5] building..."
python3 z_build.py \
  --manifest "$OUT/z-manifest.json" \
  --out-cv "$OUT/z-cv.npz" --out-mean "$OUT/z-mean.npz" \
  --receipt-cv "$OUT/z-receipt-cv.json" --receipt-mean "$OUT/z-receipt-mean.json" \
  --out-null "$OUT/z-null.npz"
RC=$?
echo "[stage5] z_build rc=${RC}  (exit 2 = construction ran, science NON-PASSING -- expected here)"
ls -la "$OUT"
