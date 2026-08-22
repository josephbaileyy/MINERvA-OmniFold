#!/usr/bin/env bash
# OI-137 covering search for a finite-N precision-bias correction.
# Re-runnable falsification harness for BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md.
# Measured at HEAD 57d9f3fbdb72282f8da1ca70192de0d7566c3f8c on 2026-08-22.
#
# WHY THIS EXISTS: the claim on file in OI-137 rested on a grep over `.py` and `.tex`
# only, for three terms only. A null grep is evidence about the search, not the world.
# This widens BOTH axes -- file set and term set -- and prints the file inventory so a
# reader can see what was NOT searched.
#
# Run from the repository root. Requires bash 3.2+ (macOS) or 4.x (Perlmutter).
# NOTE the options line is part of the harness: an extracted tail would lose it and
# would then swallow refusals and exit 0.
set -eo pipefail

TMP="${TMPDIR:-/tmp}/oi137-search.$$"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

# ---- SEARCH SET -------------------------------------------------------------
# Tracked AND untracked (--exclude-standard drops gitignored), minus the
# worktree tree: a peer's live audit checkout under .claude/worktrees/ would
# otherwise be counted as repository content and inflate every hit count.
# SELF-EXCLUSION, and it is not cosmetic: the first run of this harness reported
# `kaufman hits=1`, `sellentin hits=1`, `percival hits=1`, `wishart hits=1` -- every
# one of them THIS FILE matching its own term list. An absence test that names the
# thing it is looking for cannot find its own null. The true count for those terms
# is 0. Same failure shape as the OI-147 docstring exclusion.
SELF='docs/orchestration/state/oi137-covering-search-20260822.sh'

git ls-files -c -o --exclude-standard \
  | grep -E '\.(py|tex|md|ipynb|json|tsv|sh|cxx|C|h|txt|yaml|yml|cfg|toml)$' \
  | grep -v '^\.claude/worktrees/' \
  | grep -vxF "$SELF" > "$TMP/searchset.txt"

echo "HEAD: $(git rev-parse HEAD)"
echo "search set: $(wc -l < "$TMP/searchset.txt" | tr -d ' ') files"
echo "--- by extension ---"
sed 's/.*\.//' "$TMP/searchset.txt" | sort | uniq -c | sort -rn
echo
echo "NOT IN THE SEARCH SET (stated so the null can be falsified):"
echo "  * binary ROOT payloads -- a correction applied inside a .root TNamed"
echo "    would not be found here. Checked separately: the adopted 5D roots"
echo "    carry no n_throws at all (receipt_construction_contract_5d.json)."
echo "  * .git internals, gitignored build products, PDFs."
echo "  * the cluster checkout: this measures THIS tree only."
echo

# ---- TERMS ------------------------------------------------------------------
# All case-insensitive. Column 1 is a label, column 2 an ERE.
run() {
  local label="$1" pat="$2" n
  tr '\n' '\0' < "$TMP/searchset.txt" | xargs -0 grep -EnI -i -- "$pat" \
    > "$TMP/hits.txt" 2>/dev/null || true
  n=$(wc -l < "$TMP/hits.txt" | tr -d ' ')
  printf '%-40s hits=%-6s files=%s\n' "$label" "$n" \
    "$(cut -d: -f1 "$TMP/hits.txt" | sort -u | tr '\n' ' ')"
}

# ---- POSITIVE CONTROL -------------------------------------------------------
# A null from a broken harness looks exactly like a null from a clean world.
# `hartlap` MUST hit in docs/OPEN_ITEMS.md (OI-93 and OI-137 both spell it).
# If this arm fails, every null below is uninterpretable and the script exits 1.
if ! tr '\n' '\0' < "$TMP/searchset.txt" \
     | xargs -0 grep -lI -i -- 'hartlap' 2>/dev/null \
     | grep -qxF 'docs/OPEN_ITEMS.md'; then
  echo "POSITIVE CONTROL FAILED: 'hartlap' did not match docs/OPEN_ITEMS.md." >&2
  echo "The harness is broken (search set, quoting, or locale). Nulls below are void." >&2
  exit 1
fi
echo "positive control: OK ('hartlap' matches docs/OPEN_ITEMS.md as required)"
echo

echo "=== the three terms the filed claim used (its scope was .py + .tex only) ==="
run "hartlap"                     'hartlap'
# The separator class carries BOTH the ASCII hyphen and the U+2212 minus sign:
# OPEN_ITEMS.md and the note write this factor with a real minus, and an
# ASCII-only pattern silently misses every prose occurrence.
run "N-p-2 family"                '\(?N[[:space:]]*[-−][[:space:]]*p[[:space:]]*[-−][[:space:]]*2'
run "(N - p"                      '\([[:space:]]*N[[:space:]]*[-−][[:space:]]*p'
echo
echo "=== terms the filed claim did not use ==="
run "kaufman"                     'kaufman'
run "shrinkage"                   'shrink'
run "ledoit / wolf"               'ledoit|wolf'
run "dof (word)"                  '\bdof\b'
run "debias / de-bias"            'de-?bias'
run "sellentin / heavens"         'sellentin|heavens'
run "dodelson / schneider"        'dodelson|schneider'
run "percival"                    'percival'
run "wishart / anderson-hartlap"  'wishart|anderson-hartlap'
run "finite-N / finite ensemble"  'finite[- ](n|ensemble|sample)'
run "precision matrix"            'precision matrix'
run "effective ndf / dof"         'effective (ndf|dof|degrees)'
run "unbiased inverse"            'unbiased.{0,25}invers|invers.{0,25}unbiased'
run "ddof"                        'ddof'
