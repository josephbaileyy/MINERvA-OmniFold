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
# POPULATION, stated once and used for every count in this block: *.jsonl directly under
# <run>/inv/.
# CORRECTED 2026-08-25, defect found by an independent grader. This block used to count the run
# with `find $RUN/inv -type f` and each sibling with a RECURSIVE search of the whole sibling
# directory for *.jsonl. Two different populations, printed adjacent as though they were one.
# That is how it reported "298 jsonl" against a sibling: those 298 live in
# k0-a54038b2-20260823T205254Z/guard-inventories/, a directory name no glob in this script
# reads. So the claim "a runs/*/inv glob would pool them" was FALSE, and the arithmetic resting
# on it -- that such a glob would inflate 374 by 80% -- was correct arithmetic over the wrong
# operand. The exclusion-by-name prevented nothing. The 374 itself was and is correct.
echo "  population: *.jsonl directly under <run>/inv/ -- the SAME glob shape for run and siblings"
echo "  records : $(ls -1 $RUN/inv/*.jsonl 2>/dev/null | wc -l)  -- one per guarded process, this run only"
echo "  sibling run dirs in that same population (a 0 here is a MEASURED 0, so say which kind):"
ls -d /pscratch/sd/j/josephrb/k0r2/runs/*/ 2>/dev/null | while read d; do
  [ "$(basename $d)" = "$(basename $RUN)" ] && continue
  n=$(ls -1 "$d/inv"/*.jsonl 2>/dev/null | wc -l)
  # `ls | wc -l` returns 0 for an empty directory AND for an absent one. Name which this is,
  # because "excluded 0 records" and "there was no directory to exclude" are different claims.
  if [ -d "$d/inv" ]; then shape="inv/ exists and is empty-or-counted"; else shape="NO inv/ DIRECTORY AT ALL"; fi
  echo "    $(basename $d): $n in population  ($shape)"
done
echo "  covering control -- the glob the old justification named, actually run:"
echo "    runs/*/inv/*.jsonl = $(ls -1 /pscratch/sd/j/josephrb/k0r2/runs/*/inv/*.jsonl 2>/dev/null | wc -l)"
echo "    it equals the count above, so no sibling contributes and the exclusion is DEFENSIVE,"
echo "    not load-bearing. It would start mattering the moment a sibling populated its own inv/."

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
PRESERVER="$TOOLS_ROOT/docs/orchestration/preserve_f17b_record.py"
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the canonical checkout, per :621
OUT="${TMPDIR:-/tmp}/f17b.$$"
DURABLE_RECORD="${MNV_F17B_RECORD_PATH:-/global/u2/j/josephrb/mnv-work/MINERvA-OmniFold/docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json}"
mkdir -p "$OUT"

# Digests are deliberately NOT printed here. A digest printed BEFORE the invocation asserts
# something about a file that can still be swapped before it executes -- measured 2026-08-25,
# I made exactly that swap by hand between this print and the call, and the log's digest line
# was false while every other line stayed true. Each tool is now digested immediately before
# AND immediately after its own invocation, and a mismatch is a refusal, not a footnote.
echo "  ruler    : $MEASURER"
echo "  comparator: $COMPARATOR"
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
if [ ! -f "$COMPARATOR" ] || [ ! -f "$EXPECTED" ] || [ ! -f "$PRESERVER" ]; then
  echo "  REFUSE: the comparator, expected-list, or durable-record helper is absent under TOOLS_ROOT=$TOOLS_ROOT."
  echo "          Set MNV_TOOLS_ROOT to a checkout that carries docs/orchestration/compare_m1_m6.py."
  echo "          F-17(b) is NOT discharged by skipping the comparison: a step that silently does"
  echo "          nothing is the failure mode this whole file exists to avoid."
  rm -rf "$OUT"; exit 11
fi

EXPECTED_PRESERVER_SHA256=ea2dea540e24c38abf8d63669f8d06989a05172b95f6b2e31afc7d79358fefd9

MEASURER_PRE=$(sha256sum "$MEASURER" 2>/dev/null | cut -d' ' -f1)

for pair in "deploy:$CODE_ROOT" "canonical:$CANON"; do
  lbl="${pair%%:*}"; tree="${pair#*:}"
  "$PY" "$MEASURER" --tree "$tree" --label "$lbl" --json > "$OUT/$lbl.json" 2>"$OUT/$lbl.err"
  rc=$?
  echo "  measured $lbl ($tree) rc=$rc  bytes=$(wc -c < "$OUT/$lbl.json" 2>/dev/null)"
  if [ "$rc" -ne 0 ]; then
    sed 's/^/      /' "$OUT/$lbl.err" | tail -3
    echo "  REFUSE: measurer failed on $lbl. Cannot compare incomplete inputs."
    exit "$rc"
  fi
done
MEASURER_POST=$(sha256sum "$MEASURER" 2>/dev/null | cut -d' ' -f1)

echo "  comparing the two trees (exit 0 none / 10 all-expected / 20 some-unexpected / 4,5 refusal):"
# These two PRE digests are read HERE, on the line before the call -- not up beside the ruler's.
# Corrected 2026-08-25 after an independent grader measured the gap: they used to be read before
# the two ruler passes, which on this run was 44 min 48 s of wall clock, and a second copy of
# this script was executing out of a mutation worktree inside that window. A loose PRE does not
# merely weaken the bracket, it CHANGES WHAT IT CATCHES: a file swapped, used, and reverted
# before POST is caught by an adjacent PRE and missed by an early one, because the early PRE and
# the POST both read the reverted bytes and agree with each other. A tight bracket strictly
# dominates a loose one, so there is no trade-off here to weigh.
COMPARATOR_PRE=$(sha256sum "$COMPARATOR" 2>/dev/null | cut -d' ' -f1)
EXPECTED_PRE=$(sha256sum "$EXPECTED" 2>/dev/null | cut -d' ' -f1)
"$PY" "$COMPARATOR" --input "$OUT/deploy.json" --input "$OUT/canonical.json" \
      --expected "$EXPECTED" --repo "$TOOLS_ROOT" --record "$OUT/f17b-record.json" > "$OUT/cmp.txt" 2>&1
crc=$?
COMPARATOR_POST=$(sha256sum "$COMPARATOR" 2>/dev/null | cut -d' ' -f1)
EXPECTED_POST=$(sha256sum "$EXPECTED" 2>/dev/null | cut -d' ' -f1)
sed 's/^/    /' "$OUT/cmp.txt" | tail -18
echo "  COMPARATOR EXIT = $crc"
echo "  ruler      sha256 pre=${MEASURER_PRE:0:12}   post=${MEASURER_POST:0:12}"
echo "  comparator sha256 pre=${COMPARATOR_PRE:0:12}   post=${COMPARATOR_POST:0:12}"
echo "  expected   sha256 pre=${EXPECTED_PRE:0:12}   post=${EXPECTED_POST:0:12}"
if [ "$MEASURER_PRE" != "$MEASURER_POST" ] \
   || [ "$COMPARATOR_PRE" != "$COMPARATOR_POST" ] \
   || [ "$EXPECTED_PRE" != "$EXPECTED_POST" ]; then
  echo "  REFUSE: a tool changed on disk across its own invocation, so this comparison cannot be"
  echo "          attributed to any single revision. Nothing published; scratch kept at $OUT."
  exit 13
fi
if [ "$MODE" = "--measure" ]; then
  case "$crc" in
    0|10|20) ;;
    *)
      echo "  REFUSE: comparator exit $crc is not a completed comparison; no durable record published."
      echo "          scratch output remains at $OUT for diagnosis."
      exit "$crc"
      ;;
  esac
  echo "  publishing the completed record atomically, without clobber: $DURABLE_RECORD"
  PRESERVER_PRE=$(sha256sum "$PRESERVER" 2>/dev/null | cut -d' ' -f1)
  if [ "$PRESERVER_PRE" != "$EXPECTED_PRESERVER_SHA256" ]; then
    echo "  REFUSE: preserver changed on disk BEFORE invocation. Nothing published."
    exit 13
  fi

  [ -e "$DURABLE_RECORD" ] && RECORD_EXISTED=1 || RECORD_EXISTED=0

  "$PY" "$PRESERVER" --source "$OUT/f17b-record.json" --destination "$DURABLE_RECORD"
  prc=$?
  PRESERVER_POST=$(sha256sum "$PRESERVER" 2>/dev/null | cut -d' ' -f1)
  echo "  preserver  sha256 pre=${PRESERVER_PRE:0:12}   post=${PRESERVER_POST:0:12}"
  if [ "$PRESERVER_PRE" != "$PRESERVER_POST" ]; then
    echo "  REFUSE: a tool changed on disk across its own invocation, so this comparison cannot be"
    echo "          attributed to any single revision. Nothing published; scratch kept at $OUT."
    if [ "$RECORD_EXISTED" -eq 0 ] && [ -e "$DURABLE_RECORD" ]; then
      rm -f "$DURABLE_RECORD"
    fi
    exit 13
  fi
  if [ "$prc" -ne 0 ]; then
    echo "  REFUSE: durable publication failed; scratch output remains at $OUT for diagnosis."
    exit "$prc"
  fi
  echo "  durable record published; commit it beside the F-17(b) filing"
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
