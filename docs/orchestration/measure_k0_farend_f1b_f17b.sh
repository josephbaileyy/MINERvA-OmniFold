#!/bin/bash
# ============================================================================================
# PRESERVED 2026-08-25 from a session-scoped job directory, which is deleted with its session.
# The METHOD is pre-committed on build-k0-execution-integrity in
#   docs/orchestration/RECEIPT-20260824-k0-f8a-f9-f12-f17a-filings.md
# so the knowledge was never at risk. THIS FILE is the tested IMPLEMENTATION, and that is the
# part worth keeping: its refusal arm has been exercised, and a rewrite from the receipt would be
# written from a summary -- which is the naive reading of its own rule. Retyping a guard is a
# second implementation of it.
#
# RUN-SPECIFIC. Hardcoded to run k0-aa67c426-20260824T145751Z and its seven job ids. It is a
# record of how F-1(b)/F-17(b) were measured for THAT run, not a general instrument.
#
# --------------------------------------------------------------------------------------------
# DEFERRED DEFECTS, colocated here because this is the file a lane opens when F-1(b) comes due,
# which is exactly when they become actionable. All four are on the CANDIDATE branch, all four
# were deliberately not fixed while the rehearsal was in flight (every one touches a tracked
# .py or .sh, and the deployment is frozen at aa67c426 until F-1(b) is filed).
#
#   1. CORRECTED 2026-08-25 by re-deriving it instead of re-quoting it. I first wrote this as
#      "measure_m1_m6.py computes M-1 non-transitively". That is wrong, and wrong in a way worth
#      recording: the tool has NO cross-tree comparison surface at all. --tree is required with no
#      default, one tree per invocation, and its own docstring at :11 says "the defect is measuring
#      one tree and reporting about another." So there is no comparison in the instrument to be
#      non-transitive. The real defect is larger: F-17(b) obliges M-1..M-6 "on BOTH trees", and the
#      comparison of those two column sets is UNINSTRUMENTED -- done by eye into a receipt, as
#      F-17(a) did at 30ec0707. Transitivity does not even arise at n=2; it bites only at n>=3.
#      I filed this under a cause-name that sort-of fit, and the cause-name displaced the finding.
#   2. Three stale ratchet docstrings: "Eight files remain", "15 <- what this test counts", and
#      the overcount gloss. Each was true when written; none was re-derived after the count moved.
#   3. omnifold.py is coupled to a .gitignore re-include. The coupling is undocumented, so a
#      later .gitignore edit can untrack it silently.
#   4. F-7(b) has no exclusion instrument -- nothing mechanically enforces the exclusion the
#      clause asserts, so it is satisfied by convention only.
#
# These are NOT filed as OPEN_ITEMS rows: this lane block (120-139) is exhausted, and a new doc
# without an override row is born archival and invisible to the router. Whoever picks them up
# should claim a fresh ten-block and file them properly.
# ============================================================================================
# F-1(b) and F-17(b): the far-end measurement. DRY-RUN CAPABLE.
#   --dry-run  : exercise every instrument read-only and print what it WOULD assert. Takes nothing.
#   --measure  : take the measurement. ONLY valid once all seven jobs are terminal.
# Method pre-committed at candidate 511b5d02 BEFORE measuring, so the comparison cannot be chosen
# to flatter the result. NO set -u.
MODE="${1:---dry-run}"
CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
WANT_SHA=aa67c426afaa9b6ca91c9996637a6bade950da9a
PY=/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
BASELINE=/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json   # NOT the run's copy
RUN=/pscratch/sd/j/josephrb/k0r2/runs/k0-aa67c426-20260824T145751Z
JOBS=57527866,57527869,57527870,57527872,57527873,57527874,57527875

echo "### MODE = $MODE"
echo "### 0. PRECONDITION -- F-1(b) is only valid AFTER the last leg"
r=$(sacct -j $JOBS -X -P -n --format=State | grep -c RUNNING)
p=$(sacct -j $JOBS -X -P -n --format=State | grep -c PENDING)
f=$(sacct -j $JOBS -X -P -n --format=State | grep -cE 'FAILED|CANCELLED|TIMEOUT|NODE_FAIL')
echo "  running=$r pending=$p failed=$f"
if [ "$MODE" = "--measure" ] && { [ "$r" -ne 0 ] || [ "$p" -ne 0 ]; }; then
  echo "  REFUSE: not all seven are terminal. F-1(b) taken now would not be the far end."; exit 10; fi
[ "$MODE" = "--dry-run" ] && echo "  (dry run: proceeding regardless, asserting nothing)"

echo
echo "### 1. F-1(b) -- A-2(a)-(g) at the FAR END, against the DECLARED baseline"
echo "  baseline : $BASELINE"
echo "    exists=$([ -f "$BASELINE" ] && echo yes || echo NO)  file sha256=$(sha256sum "$BASELINE" 2>/dev/null | cut -c1-12)  (expect 622ddc0a)"
echo "  the run's own manifest, deliberately NOT used as the baseline:"
echo "    $RUN/source-manifest.json  sha256=$(sha256sum $RUN/source-manifest.json 2>/dev/null | cut -c1-12)  (b46e4f57; built 9s pre-submission)"
H=$(git -C "$CODE_ROOT" rev-parse HEAD)
echo "  a) HEAD=$H  $([ "$H" = "$WANT_SHA" ] && echo MATCHES || echo '*** DIFFERS ***')"
git -C "$CODE_ROOT" symbolic-ref -q HEAD >/dev/null && echo "     ON BRANCH -- would violate the 7.0.19 freeze" || echo "     DETACHED (7.0.19 intact)"
git -C "$CODE_ROOT" status --porcelain > /tmp/fe_porc.$$
echo "  b) porcelain=$(wc -l < /tmp/fe_porc.$$)"
for fl in require-checkout require-no-nested-checkout require-not-nested require-readonly; do
  "$PY" "$CODE_ROOT/nd-unfolding/mnv_source_manifest.py" --repo "$CODE_ROOT" --compare "$BASELINE" --"$fl" >/dev/null 2>&1
  echo "  --$fl rc=$?"
done
"$PY" "$CODE_ROOT/nd-unfolding/mnv_source_manifest.py" --repo "$CODE_ROOT" --compare "$BASELINE" --require-clean > /tmp/fe_f.$$ 2>&1
echo "  f) --compare --require-clean rc=$?"
grep -o 'SOURCE MANIFEST IDENTICAL.*' /tmp/fe_f.$$ | sed 's/^/     /'
echo "     THE FIELD IS listing_sha256, not the file digest:"
"$PY" - <<PY 2>/dev/null
import json
d=json.load(open("$BASELINE"))
print("       baseline listing_sha256 =", d.get("listing_sha256"))
print("       baseline file_count     =", d.get("file_count"))
PY
rm -f /tmp/fe_porc.$$ /tmp/fe_f.$$

echo
echo "### 2. F-4(b) -- inventory count, POPULATION NAMED, single RUN_ID only"
echo "  run root: $RUN"
echo "  records : $(find $RUN/inv -type f 2>/dev/null | wc -l)  -- one per guarded process, this run only"
echo "  sibling run dirs deliberately EXCLUDED (a runs/*/inv glob would pool them):"
ls -d /pscratch/sd/j/josephrb/k0r2/runs/*/ 2>/dev/null | while read d; do
  [ "$(basename $d)" = "$(basename $RUN)" ] && continue
  echo "    EXCLUDED $(basename $d): $(find $d -name '*.jsonl' 2>/dev/null | wc -l) jsonl"
done

echo
echo "### 3. F-17(b) -- M-1..M-6 on BOTH trees; the canonical run takes 42-47 min"
echo "  clause text is pinned by digest, NOT 'the contract':"
echo "    the deployed rubric has 7.0 x$(grep -c '7\.0' $CODE_ROOT/docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md) and F-1(b) x$(grep -cF 'F-1(b)' $CODE_ROOT/docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md)"
echo "    so the obligations are quoted from main's copy by sha256, with the tree named"

# The RULER. measure_m1_m6.py is byte-identical in the frozen deploy and on main (measured
# 2026-08-25: sha256 0fcd90f7...), so which copy is used does not change the numbers -- but it is
# recorded anyway, because "identical today" is a measurement and not a property.
MEASURER="$CODE_ROOT/docs/orchestration/measure_m1_m6.py"
# THE COMPARATOR IS NOT IN THE FROZEN TREE. It was built after aa67c426, so it cannot be, and it
# must be invoked from a live checkout. That is sound rather than a compromise: the comparator
# measures no tree -- it forbids itself from importing subprocess, ast, glob and os -- so running
# it from outside the freeze cannot perturb what is being compared.
TOOLS_ROOT="${MNV_TOOLS_ROOT:-$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)}"
COMPARATOR="$TOOLS_ROOT/docs/orchestration/compare_m1_m6.py"
EXPECTED="$TOOLS_ROOT/docs/orchestration/m1m6_expected_differences.json"
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the canonical checkout, per :621
OUT="${TMPDIR:-/tmp}/f17b.$$"
mkdir -p "$OUT"

echo "  ruler    : $MEASURER  sha256=$(sha256sum "$MEASURER" 2>/dev/null | cut -c1-12)"
echo "  comparator: $COMPARATOR  sha256=$(sha256sum "$COMPARATOR" 2>/dev/null | cut -c1-12)"
# TOOLS_ROOT must be a REAL CHECKOUT, not a staging directory holding just these two files.
# Measured 2026-08-25: a partial TOOLS_ROOT passes a two-file existence check and then the
# comparator refuses at exit 5, because the expected-list's CITATIONS resolve relative to --repo
# and the cited document was not there. A precondition check that is narrower than the thing it
# gates just moves the failure later and makes it read as a finding instead of a misconfiguration.
if [ ! -d "$TOOLS_ROOT/.git" ] && ! git -C "$TOOLS_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "  REFUSE: TOOLS_ROOT=$TOOLS_ROOT is not a git checkout, so the expected-list's citations"
  echo "          cannot resolve under --repo. Point MNV_TOOLS_ROOT at a real checkout."
  rm -rf "$OUT"; exit 12
fi
if [ ! -f "$COMPARATOR" ] || [ ! -f "$EXPECTED" ]; then
  echo "  REFUSE: the comparator or its expected-list is absent under TOOLS_ROOT=$TOOLS_ROOT."
  echo "          Set MNV_TOOLS_ROOT to a checkout that carries docs/orchestration/compare_m1_m6.py."
  echo "          F-17(b) is NOT discharged by skipping the comparison: a step that silently does"
  echo "          nothing is the failure mode this whole file exists to avoid."
  rm -rf "$OUT"; exit 11
fi

for pair in "deploy:$CODE_ROOT" "canonical:$CANON"; do
  lbl="${pair%%:*}"; tree="${pair#*:}"
  "$PY" "$MEASURER" --tree "$tree" --label "$lbl" --json > "$OUT/$lbl.json" 2>"$OUT/$lbl.err"
  rc=$?
  echo "  measured $lbl ($tree) rc=$rc  bytes=$(wc -c < "$OUT/$lbl.json" 2>/dev/null)"
  [ "$rc" -ne 0 ] && sed 's/^/      /' "$OUT/$lbl.err" | tail -3
done

echo "  comparing the two trees (exit 0 none / 10 all-expected / 20 some-unexpected / 4,5 refusal):"
"$PY" "$COMPARATOR" --input "$OUT/deploy.json" --input "$OUT/canonical.json" \
      --expected "$EXPECTED" --repo "$TOOLS_ROOT" --record "$OUT/f17b-record.json" > "$OUT/cmp.txt" 2>&1
crc=$?
sed 's/^/    /' "$OUT/cmp.txt" | tail -18
echo "  COMPARATOR EXIT = $crc"
if [ "$MODE" = "--measure" ]; then
  echo "  record kept at $OUT/f17b-record.json -- commit it beside the F-17(b) filing"
else
  rm -rf "$OUT"
fi

echo
echo "### THE HALF THIS FILE STILL CANNOT DISCHARGE, stated rather than left to be discovered."
echo "  :621's two-tree comparison is now instrumented, above. :1471 separately obliges that 'any"
echo "  difference from THIS DOCUMENT is reported as a finding', and that document"
echo "  (MEASUREMENT-20260822-m1-m6-at-pinned-sha.md) is markdown prose. The comparator consumes"
echo "  --json and there is no --json column filed pre-submission, so it CANNOT perform that"
echo "  comparison. Manufacturing a column that was never taken would be worse than saying so."
echo "  Found by an independent grader lane, 2026-08-25; see"
echo "  GRADE-20260825-f17b-comparison-instrument-fitness.md."
[ "$MODE" = "--dry-run" ] && echo "### DRY RUN COMPLETE -- nothing asserted, nothing filed"
