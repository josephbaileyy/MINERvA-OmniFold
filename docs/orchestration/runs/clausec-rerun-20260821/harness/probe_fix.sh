#!/bin/bash
# ==================================================================================================
# FORWARD-LOOKING PROBE OF A PROPOSED REMEDY. **NOT PART OF THE CLAUSE (c) CERTIFICATION.**
#
# Everything here runs PATCHED COPIES of modules that are NOT in any commit. It measures what a
# proposed fix would do; it says nothing about 00be534f, and no arm result may be quoted from it.
# The worktree is untouched: the patched files are copies in the sandbox, symlinked alongside the
# real ones.
#
# TWO CANDIDATES, because the first is the one that looks obviously right and I want it measured
# rather than endorsed:
#   A: add hDiagCombinedOld / hDiagCombinedOldRaw to EXPECTED_ELEMENTS at REPORTED_NBINS.
#   B: A, plus make the m_mx completeness check assert EQUALITY (n == expected) instead of
#      partiality (frac < 1.0), with a distinct message for an OVER-LENGTH array.
# ==================================================================================================
set -uo pipefail
WT="${WT:?}"; SB="${SB:?}"
MEMBER="$SB/m_A3d.root"; ARCHIVE="$SB/archive_pos.root"
[[ -f "$MEMBER" && -f "$ARCHIVE" ]] || { echo "[FAIL] need $MEMBER and $ARCHIVE from the main run"; exit 1; }

mkprobe() {   # mkprobe <dir> <patch-classes> <patch-comparator>
  local d="$1"
  rm -rf "$d"; mkdir -p "$d/nd-unfolding"
  ln -sfn "$WT/docs" "$d/docs"
  for e in "$WT"/nd-unfolding/*; do
    b="$(basename "$e")"; case "$b" in products|uq_5d) continue;; esac
    ln -sfn "$e" "$d/nd-unfolding/$b"
  done
  rm -f "$d/nd-unfolding/mii_root_payload_classes.py" "$d/nd-unfolding/mii_anchor_comparator.py"
  cp "$WT/nd-unfolding/mii_root_payload_classes.py" "$d/nd-unfolding/"
  cp "$WT/nd-unfolding/mii_anchor_comparator.py"   "$d/nd-unfolding/"
  python3 - "$d" "$2" "$3" <<'PY'
import sys, pathlib
d, pc, pcmp = sys.argv[1], sys.argv[2] == "1", sys.argv[3] == "1"
if pc:
    p = pathlib.Path(d, "nd-unfolding/mii_root_payload_classes.py"); s = p.read_text()
    old = '    "hCov_combined5d_total_uthrow": REPORTED_NBINS ** 2,\n}'
    new = ('    "hCov_combined5d_total_uthrow": REPORTED_NBINS ** 2,\n'
           '    "hDiagCombinedOld": REPORTED_NBINS,\n'
           '    "hDiagCombinedOldRaw": REPORTED_NBINS,\n}')
    assert old in s, "EXPECTED_ELEMENTS anchor not found"
    p.write_text(s.replace(old, new, 1)); print("  patched: EXPECTED_ELEMENTS + 2 diagonal rows")
if pcmp:
    p = pathlib.Path(d, "nd-unfolding/mii_anchor_comparator.py"); s = p.read_text()
    old = "        if frac < 1.0:"
    new = ("        if n > expected:\n"
           "            lines.append(\n"
           "                f\"{name}: WRONG LENGTH -- {n} elements where the writer's own \"\n"
           "                f\"construction gives {expected}. An OVER-LENGTH array is not a partial \"\n"
           "                \"comparison and must not borrow that word: every element compared equal \"\n"
           "                \"and the array is still not the one the writer emits.\")\n"
           "            class_failed = True\n"
           "        if frac < 1.0:")
    assert old in s, "coverage branch anchor not found"
    p.write_text(s.replace(old, new, 1)); print("  patched: m_mx completeness now asserts EQUALITY")
PY
}

run() {  # run <dir> <label>
  echo "--- $2 ---"
  ( cd "$1/nd-unfolding" && python3 mii_anchor_comparator.py --artifact adopted_uthrow.root \
      --archive "$ARCHIVE" --member "$MEMBER" --offset 0 --archive-date 2026-07-14 ) \
      > "$SB/logs/probe_$2.log" 2>&1
  local rc=$?
  grep -E "VERDICT|coverage\] hDiag|WRONG LENGTH|PARTIAL COMPARISON" "$SB/logs/probe_$2.log" | sed 's/^/    /'
  echo "    EXIT = $rc   (0=PASS 2=FAIL)"
}

echo "=== BASELINE: 00be534f as committed (already measured as arm A3d) ==="
mkprobe "$SB/probe_base" 0 0; run "$SB/probe_base" base
echo "=== CANDIDATE A: the two EXPECTED_ELEMENTS entries ONLY ==="
mkprobe "$SB/probe_a" 1 0; run "$SB/probe_a" A
echo "=== CANDIDATE B: A + completeness asserts EQUALITY ==="
mkprobe "$SB/probe_b" 1 1; run "$SB/probe_b" B
echo
echo "=== CONTROL: candidate B must still PASS the GOOD product (no false positive) ==="
MEMBER="$SB/mirror/nd-unfolding/uq_5d/A1/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root"
run "$SB/probe_b" B_on_good
