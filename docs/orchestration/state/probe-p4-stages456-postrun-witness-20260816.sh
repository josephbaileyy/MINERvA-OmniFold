#!/bin/bash
# READ-ONLY post-run check: product digests + the R11-1 execution witness.
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
CAND=$REPO/nd-unfolding/active_universe_5d/standard/candidate
source "$REPO/setup_salloc_env.sh" >/dev/null 2>&1
echo "python : $(python3 -V 2>&1)"
echo
echo "=== products, post-run ==="
for f in std_final5_candidate.root std_component_manifest.json p4_standard_validation.json \
         std_proj4d_candidate.root std_proj4d_candidate_projmanifest.json; do
  printf '%14s  %s  %s\n' "$(stat -c '%s' "$CAND/$f")" "$(date -u -d @$(stat -c '%Y' "$CAND/$f") +%FT%TZ)" "$f"
done
echo
echo "=== sha256 of the two JSON manifests + proj4d ROOT (fast) ==="
sha256sum "$CAND/std_component_manifest.json" "$CAND/p4_standard_validation.json" \
          "$CAND/std_proj4d_candidate_projmanifest.json" "$CAND/std_proj4d_candidate.root" | sed 's#/pscratch.*/##'
echo
echo "=== R11-1 EXECUTION WITNESS ==="
python3 - <<'PY'
import json, os
cand = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/candidate"
pm = json.load(open(os.path.join(cand, "std_proj4d_candidate_projmanifest.json")))
man = json.load(open("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/evidence/p4_standard_manifest.json"))

ok = True
def check(label, cond, detail=""):
    global ok
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' -- ' + detail) if detail else ''}")
    ok = ok and bool(cond)

mstats = pm.get("projection_M_recipe_check")
check("projection_M_recipe_check present in the produced receipt", mstats is not None,
      "a commented-out call cannot populate this key")
if mstats:
    nnz  = mstats.get("projection_M_recipe_nnz")
    diff = mstats.get("projection_M_recipe_entries_differing")
    route= mstats.get("projection_M_recipe_route")
    print(f"        route = {route}")
    check("nnz > 0", isinstance(nnz, int) and nnz > 0, f"nnz={nnz}")
    check("entries_differing == 0", diff == 0, f"entries_differing={diff}")

    # INDEPENDENT RECOUNT, derived from recorded integers rather than read back from the same key.
    # M is the width-weighted marginalization 5D->4D, so every reported 5D bin contributes to
    # exactly ONE 4D bin => nnz must equal the number of reported 5D bins.
    n5 = man.get("mask5d_nreported")
    shape = pm.get("M_shape")
    n4eff = pm.get("mask4d_neffective")
    n4rep = pm.get("mask4d_nreported")
    unreach = pm.get("mask4d_unreachable_n")
    print(f"        mask5d_nreported={n5}  M_shape={shape}  mask4d_neffective={n4eff} "
          f"(reported {n4rep}, unreachable {unreach})")
    check("nnz == mask5d_nreported (one nonzero per 5D column: a marginalization map)", nnz == n5,
          f"{nnz} vs {n5}")
    check("M_shape == [mask4d_neffective, mask5d_nreported]", shape == [n4eff, n5],
          f"{shape} vs [{n4eff}, {n5}]")
    check("mask4d_neffective == mask4d_nreported - mask4d_unreachable_n",
          isinstance(n4eff, int) and n4eff == (n4rep or 0) - (unreach or 0),
          f"{n4eff} vs {n4rep} - {unreach}")

print(f"\n  projection_identity_relerr = {pm.get('projection_identity_relerr')}")
print(f"  projection_identity_gates_M = {pm.get('projection_identity_gates_M')}")
print(f"  M_content_sha256 = {pm.get('M_content_sha256')}")
print(f"  {os.path.basename('NON_ADOPTABLE')} marker keys: "
      f"{ {k: v for k, v in pm.items() if 'adopt' in k.lower()} }")
print(f"\nWITNESS: {'PASS' if ok else 'FAIL'}")
PY
echo
echo "=== stage 5 validation gates ==="
python3 -c "
import json
v=json.load(open('$CAND/p4_standard_validation.json'))
print('result       :', v.get('result'))
print('gates (n=%d) :' % len(v.get('gates',[])), ','.join(v.get('gates',[])))
print('candidate_sha256:', v.get('candidate_sha256'))
"
