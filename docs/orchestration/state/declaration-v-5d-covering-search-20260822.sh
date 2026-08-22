#!/usr/bin/env bash
# Covering search for declaration (v) of app_statmethods.tex on the scalar-5D blocks.
#
# WHY THIS EXISTS. The record it backs makes two INVENTORY claims, and an inventory claim is
# falsified by exactly the work it authorizes. Both are stated here as runnable searches so a
# later reader can re-measure instead of trusting a date.
#
#   I1  No finite-ensemble debiasing factor and no shrinkage estimator is applied on any 5D
#       covariance construction path (`nd-unfolding/`).
#   I2  No 5D covariance ARTIFACT records the ensemble size of the C_stat or C_ML block.
#
# THREE DISCIPLINES, each of which the OI-137 harness had to learn the hard way:
#   * a null from a search is evidence about the SEARCH, so the file set is printed;
#   * a script that names every term it seeks WILL MATCH ITSELF, and so will the document that
#     documents it -- both are excluded, the exclusion is PRINTED, and a rename of either member
#     makes this script exit 1 rather than silently restoring the false hits;
#   * a null from a broken harness is indistinguishable from a null from a clean world, so two
#     positive controls must pass or every null below is void.
#
# Run from the repository root. Exits 0 only if both positive controls and the self-reference
# guard pass; the term results themselves never set the exit code.
set -uo pipefail

SELF="docs/orchestration/state/declaration-v-5d-covering-search-20260822.sh"
DOC="docs/orchestration/PROVENANCE-20260822-declaration-v-scalar5d-blocks.md"
SELF_REFERENCE_SET=("$SELF" "$DOC")

echo "=== declaration-(v) 5D covering search ==="
echo "HEAD            : $(git rev-parse HEAD)"
echo "run_at_utc      : $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo

# ---------------------------------------------------------------------------------------------
# Self-reference guard. Excluding a file is only legitimate when that file is ABOUT the search.
# If either member is renamed, the exclusion silently stops matching and the nulls below come
# back as false hits, so a missing member is a HARD FAILURE, not a warning.
# ---------------------------------------------------------------------------------------------
echo "--- self-reference exclusion set (printed so it is auditable) ---"
guard_ok=1
for m in "${SELF_REFERENCE_SET[@]}"; do
  if [ -f "$m" ]; then
    echo "  EXCLUDED  $m"
  else
    echo "  MISSING   $m   <-- the exclusion cannot match; results below would be self-hits"
    guard_ok=0
  fi
done
if [ "$guard_ok" -ne 1 ]; then
  echo "SELF-REFERENCE GUARD: FAIL -- stale exclusion set. Fix the paths before trusting any null."
  exit 1
fi
echo "SELF-REFERENCE GUARD: OK"
echo

# ---------------------------------------------------------------------------------------------
# File set. Tracked AND untracked (gitignored excluded). `.claude/worktrees/` is removed: a peer's
# live audit checkout there is another commit's content, not this tree's.
# ---------------------------------------------------------------------------------------------
FILELIST="$(mktemp)"; trap 'rm -f "$FILELIST"' EXIT
git ls-files -c -o --exclude-standard \
  | grep -E '\.(py|sh|json|tsv|md|tex|txt)$' \
  | grep -v '^\.claude/worktrees/' \
  | grep -vxF -e "$SELF" -e "$DOC" \
  > "$FILELIST"
echo "--- file set ---"
echo "  files after exclusions : $(wc -l < "$FILELIST" | tr -d ' ')"
echo "  by extension:"
sed 's/.*\.//' "$FILELIST" | sort | uniq -c | sort -rn | sed 's/^/    /'
echo "  NOT searched: binary .root payloads (a TNamed inside one is invisible to any text search --"
echo "                that is why I2 is answered from the ROOT-reading receipts, not from grep);"
echo "                .git internals; gitignored build products; the cluster checkout."
echo

# ---------------------------------------------------------------------------------------------
# Positive controls. Both must pass or every null is void.
#   PC1 finds the one REAL shrinkage estimator in the repository. The original OI-137 grep missed
#       it because `hartlap`/`N-p-2`/`(N - p` cannot match a shrinkage implementation; a harness
#       that cannot find it is not measuring I1.
#   PC2 finds a real ensemble-size stamp inside a ROOT-reading receipt, proving the search reaches
#       the receipt layer that I2 is about.
# ---------------------------------------------------------------------------------------------
pc_fail=0
pc () {  # pc <label> <pattern> <expected-path>
  local n
  n=$(grep -ril -- "$2" $(cat "$FILELIST") 2>/dev/null | grep -cxF "$3")
  if [ "$n" -eq 1 ]; then echo "  PC OK    $1: '$2' found in $3"
  else echo "  PC FAIL  $1: '$2' NOT found in $3 (matches=$n)"; pc_fail=1; fi
}
echo "--- positive controls ---"
pc PC1 'ledoit'            '2d-unfolding/uq/analyze_universes.py'
pc PC2 'upstream_n_throws' 'nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json'
if [ "$pc_fail" -ne 0 ]; then
  echo "POSITIVE CONTROLS: FAIL -- every null below is void."
  exit 1
fi
echo "POSITIVE CONTROLS: OK"
echo

# ---------------------------------------------------------------------------------------------
# I1 -- finite-ensemble treatment on the 5D construction path.
# Scoped to nd-unfolding/*.py, which is where every 5D covariance block is built. The wider
# repository-scale version of this null is BRIEF-20260822-oi137's job and is not repeated here.
# ---------------------------------------------------------------------------------------------
echo "--- I1: finite-ensemble treatment in nd-unfolding/*.py (the 5D construction path) ---"
ND_PY="$(grep -E '^nd-unfolding/.*\.py$' "$FILELIST" | grep -v '/tests\?/')"
echo "  scope: $(echo "$ND_PY" | grep -c . ) non-test .py files under nd-unfolding/"
for t in hartlap ledoit shrink 'n-p-2' 'n - p - 2' debias sellentin percival kaufman wishart; do
  hits=$(grep -ril -- "$t" $ND_PY 2>/dev/null | sort -u)
  n=$(echo "$hits" | grep -c .)
  printf '  %-14s hits=%s' "$t" "$n"
  [ "$n" -gt 0 ] && printf '  -> %s' "$(echo "$hits" | tr '\n' ' ')"
  printf '\n'
done
echo

# ---------------------------------------------------------------------------------------------
# I2 -- ensemble-size keys actually present in the 5D artifacts, read from the ROOT-reading
# receipts. `combine_cov_nd.py` writes ONE TH2D and no scalar, so C_stat/C_ML carry no N; this
# prints the receipt evidence for that rather than asserting it.
# ---------------------------------------------------------------------------------------------
echo "--- I2: ensemble-size keys in the 5D covariance receipts ---"
python3 - <<'PY'
import json, os
recs = {
  "construction contract (6 adopted roots + 2 throw roots)":
      "nd-unfolding/uq_5d/receipt_construction_contract_5d.json",
  "candidate stamps (2026-08-12 stamped arms)":
      "nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json",
}
KEYS = ("n_throws", "upstream_n_throws", "n_universes", "n_replicas")
for label, p in recs.items():
    print(f"  {label}\n    {p}")
    if not os.path.exists(p):
        print("    ABSENT -- cannot answer"); continue
    d = json.load(open(p))
    for group in ("adopted_roots", "throw_roots", "files"):
        for name, v in (d.get(group) or {}).items():
            params = v.get("parameters", {})
            got = {k: params[k].get("value") for k in KEYS
                   if k in params and params[k].get("present")}
            print(f"      [{group}] {name}: " + (str(got) if got else "NO ensemble-size key"))
print("  C_stat / C_ML 5D artifacts (uq_cov_stat_5d.root, uq_cov_mlsplit_5d.root):")
print("    covered by NO receipt in this tree; combine_cov_nd.py writes one TH2D and no scalar,")
print("    so no ensemble-size key can exist on them. Recount route: the --expected-ids range.")
PY
echo
echo "=== end. Term results above are NOT the exit code; the guard and the controls are. ==="
exit 0
