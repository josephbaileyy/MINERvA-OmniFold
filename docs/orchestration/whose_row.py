#!/usr/bin/env python3
"""Attribute a ledger row to its owning lane, so "the author merges their own row" is a CHECK.

WHY THIS EXISTS
---------------
Joseph decided 2026-08-12: move to per-lane worktrees, and **no lane's ledger row is merged by anyone
but its author**. Worktrees eliminate the shared-index race (separate worktrees have separate indexes,
proven rather than assumed). What they do NOT eliminate is the contended document: five of the six
absorption events on 2026-08-11/12 landed in FINDINGS.md, VALIDATION_LEDGER.md or OPEN_ITEMS.md, and
under worktrees those become merge CONFLICTS instead of silent absorptions. Loud beats silent -- but a
conflict still has to be resolved by someone, and the someone resolving it is exactly the person least
likely to know what the other lane meant.

The rule alone would be another attentiveness remedy, and this campaign has a measured record of those:
BEN-105 counts four failures of BEN id attentiveness, twice while the failing agent was reading the
rule; six successive pre-commit staging remedies were each defeated in one night, the last one mine
twenty minutes after I relayed it. So the rule ships with a mechanism.

WHAT IT DOES
------------
Maps every row id in a conflicted (or merely changed) ledger file to its owning lane, and refuses the
merge if any contested row belongs to someone else.

    whose_row.py --lane C FINDINGS.md          # who owns each row; exit 1 if a row is not lane C's
    whose_row.py --conflicts --lane C           # only rows inside <<<<<<< conflict markers
    whose_row.py --self-test                    # power test, both directions

Attribution is DERIVED, never narrated: the BEN block table is parsed out of FINDINGS.md's own header,
because that header's own rule says the highest allocated id is derived and notes that the table which
used to state it "was wrong in three of five rows within a day of being written". If the table moves or
changes shape this script fails loudly rather than falling back to a stale copy -- a silent fallback
here would attribute rows to the wrong lane, which is worse than no attribution at all and is the exact
shape of the false confession BEN-160 records.

LIMITS, stated because an attributor that overstates its reach is the defect it exists to prevent:
  * It attributes by ID BLOCK, not by authorship. A lane that files in another lane's block is
    misattributed -- that has happened (BEN-089, max+1 from outside both documented ranges).
  * VALIDATION_LEDGER.md has no per-row id scheme, so it CANNOT be attributed by this tool. It is the
    file with the second-most absorptions. Named here rather than silently unhandled.
  * It sees rows, not prose. A conflict in a header paragraph is unattributable and reported as such.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent          # derived from __file__, never hardcoded (the p4_evidence.py lesson)

# `| D — verifier | `160-189` |`  /  `| A — orchestrator | `190-199` |`
BLOCK_ROW = re.compile(r"^>?\s*\|\s*([^|]+?)\s*\|\s*`(\d+)-(\d+)`[^|]*\|", re.M)
BEN_ROW = re.compile(r"^\|\s*BEN-(\d+)\s*\|")
CLM_ROW = re.compile(r"^\|\s*(CLM-\d+)\s*\|")
OI_ROW = re.compile(r"^\|\s*(OI-\d+)\s*\|\s*[^|]*\|\s*([^|]+?)\s*\|")
CONFLICT_START = re.compile(r"^<{7}")
CONFLICT_END = re.compile(r"^>{7}")

UNATTRIBUTABLE = "docs of no per-row id scheme"


def ben_blocks(findings: Path) -> list[tuple[int, int, str]]:
    """[(lo, hi, lane)] parsed from FINDINGS.md's header table. Raises if it cannot be found."""
    text = findings.read_text(encoding="utf-8", errors="replace")
    head = text[: text.find("## Long-form findings index")] or text[:8000]
    out = []
    for lane, lo, hi in BLOCK_ROW.findall(head):
        lane = lane.strip().strip("*")
        if lane.lower().startswith(("lane", "---")) or not lane:
            continue
        out.append((int(lo), int(hi), lane))
    if not out:
        raise SystemExit(
            "FATAL: no BEN block table found in FINDINGS.md's header. This script REFUSES to fall back "
            "to a hardcoded table -- a stale block map attributes rows to the wrong lane, which is "
            "worse than no attribution. Fix the header or fix this parser.")
    return sorted(out)


def owner_of_ben(n: int, blocks: list[tuple[int, int, str]]) -> str | None:
    for lo, hi, lane in blocks:
        if lo <= n <= hi:
            return lane
    return None


def conflicted_line_numbers(text: str) -> set[int]:
    inside, out = False, set()
    for i, line in enumerate(text.splitlines(), 1):
        if CONFLICT_START.match(line):
            inside = True
        if inside:
            out.add(i)
        if CONFLICT_END.match(line):
            inside = False
    return out


def rows_in(path: Path, only_conflicts: bool, blocks) -> list[tuple[int, str, str | None]]:
    """[(lineno, row_id, owner_or_None)]"""
    text = path.read_text(encoding="utf-8", errors="replace")
    keep = conflicted_line_numbers(text) if only_conflicts else None
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if keep is not None and i not in keep:
            continue
        m = BEN_ROW.match(line)
        if m:
            n = int(m.group(1))
            out.append((i, f"BEN-{m.group(1)}", owner_of_ben(n, blocks)))
            continue
        m = OI_ROW.match(line)
        if m:
            out.append((i, m.group(1), m.group(2).strip() or None))
            continue
        m = CLM_ROW.match(line)
        if m:
            out.append((i, m.group(1), None))
    return out


def _lane_key(s: str) -> str:
    """The lane's identifying token: 'C - PET' -> 'C', 'B — uncertainty construction' -> 'B'."""
    head = re.split(r"[—\-/(]", s.strip(), maxsplit=1)[0]
    return head.strip().strip("*.").upper()


def lane_matches(owner: str | None, lane: str) -> bool:
    """Whole-token comparison. NEVER substring.

    The first version of this function was `lane.lower() in owner.lower()`, and it returned TRUE for
    lane "C" against owner "B — uncertainty construction" -- because "constru(c)tion" contains a "c".
    A single-letter substring test matches almost everything, so the gate PASSED lane C on lane B's
    row: a false pass, in the only direction that matters, in the check written to prevent exactly
    that. Caught by an end-to-end merge between two real worktrees, NOT by the self-test, whose one
    negative control (`"C — PET"` vs `"B"`) happened to be a case where the bug does not fire.
    That is D's rule earned twice in one night: THE BATTERY IS THE FORM SET, NOT ONE VARIANT.
    The self-test now runs the full lane x owner cross-product and requires the diagonal exactly.
    """
    if owner is None:
        return False
    want = _lane_key(lane)
    if not want:
        return False
    if _lane_key(owner) == want:
        return True
    # OPEN_ITEMS owner cells are free text ("PET / cause 5 owner", "standard P4 / Joseph"). Allow a
    # whole-word match on a multi-character lane name, never on a bare letter.
    if len(want) > 1 and re.search(rf"(?<![A-Za-z]){re.escape(want)}(?![A-Za-z])", owner.upper()):
        return True
    return False


def self_test() -> int:
    blocks = ben_blocks(REPO / "docs/orchestration/FINDINGS.md")
    checks, failures = [], []

    def case(label, got, want):
        checks.append((label, got == want, got, want))
        if got != want:
            failures.append(f"{label}: got {got!r} want {want!r}")

    # Positive: every documented block maps its own endpoints to itself.
    for lo, hi, lane in blocks:
        case(f"{lo} -> {lane}", owner_of_ben(lo, blocks), lane)
        case(f"{hi} -> {lane}", owner_of_ben(hi, blocks), lane)

    # NEGATIVE CONTROLS, both directions -- an attributor that answers everything is useless.
    lo0 = min(b[0] for b in blocks)
    case("below every block is UNOWNED", owner_of_ben(lo0 - 1, blocks), None)
    case("absurdly high id is UNOWNED", owner_of_ben(999999, blocks), None)
    # Blocks must not overlap, or an id has two owners and the rule cannot be enforced at all.
    spans = sorted((lo, hi) for lo, hi, _ in blocks)
    overlaps = [(a, b) for a, b in zip(spans, spans[1:]) if a[1] >= b[0]]
    case("no overlapping blocks", overlaps, [])
    # Conflict-marker scoping must actually scope.
    sample = "| BEN-101 | x |\n<<<<<<< HEAD\n| BEN-131 | y |\n=======\n>>>>>>> other\n"
    tmp = REPO / "docs/orchestration/.whose_row_selftest.tmp"
    try:
        tmp.write_text(sample)
        allr = {r for _, r, _ in rows_in(tmp, False, blocks)}
        conf = {r for _, r, _ in rows_in(tmp, True, blocks)}
        case("unscoped sees both rows", allr, {"BEN-101", "BEN-131"})
        case("conflict scoping sees ONLY the conflicted row", conf, {"BEN-131"})
    finally:
        tmp.unlink(missing_ok=True)
    # LANE MATCHING: the FULL CROSS-PRODUCT, not one variant. A single negative control here passed
    # by luck while the gate false-passed lane C on lane B's row -- see lane_matches' docstring.
    owners = [lane for _, _, lane in blocks]
    for owner in owners:
        for probe in ("A", "B", "C", "D"):
            want = _lane_key(owner) == probe
            case(f"{probe!r} vs {owner!r}", lane_matches(owner, probe), want)
    # The specific historical false pass, pinned by name so it cannot regress silently.
    case("REGRESSION: 'C' must NOT match 'B — uncertainty construction' (substring 'construction')",
         lane_matches("B — uncertainty construction", "C"), False)
    case("REGRESSION: 'D' must NOT match 'A — orchestrator' (substring 'orchestrator')",
         lane_matches("A — orchestrator", "D"), False)
    case("full lane string accepts", lane_matches("C — PET", "C - PET"), True)
    case("free-text OI owner, whole word", lane_matches("PET / cause 5 owner", "PET"), True)
    case("free-text OI owner, bare letter must NOT match", lane_matches("PET / cause 5 owner", "P"),
         False)
    case("unowned row is never matchable", lane_matches(None, "C"), False)
    case("empty lane never matches", lane_matches("C — PET", ""), False)

    for label, ok, got, _ in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"  (got {got!r})"))
    print(f"  {len(blocks)} blocks parsed from FINDINGS.md's header, {len(checks)} checks")
    for f in failures:
        print(f"  FAIL {f}")
    print("SELF-TEST :: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="ledger files to attribute (default: the conflicted set)")
    ap.add_argument("--lane", help='your lane, e.g. "C" or "C - PET". Exit 1 if a row is not yours.')
    ap.add_argument("--conflicts", action="store_true", help="only rows inside conflict markers")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    blocks = ben_blocks(REPO / "docs/orchestration/FINDINGS.md")
    files = [Path(f) for f in args.files]
    if not files:
        try:
            out = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", "--diff-filter=U"],
                                 capture_output=True, text=True, check=True).stdout
            files = [REPO / p for p in out.split()]
        except (subprocess.CalledProcessError, OSError):
            files = []
        if not files:
            print("no unmerged files; nothing to attribute")
            return 0

    foreign, unattributable = [], []
    for path in files:
        if not path.exists():
            print(f"  skip {path} (absent)")
            continue
        rows = rows_in(path, args.conflicts, blocks)
        rel = path.relative_to(REPO) if REPO in path.parents else path
        if not rows:
            print(f"  {rel}: NO ATTRIBUTABLE ROWS -- resolve by hand and route to the author. "
                  f"(VALIDATION_LEDGER.md has no per-row id scheme; a prose conflict has no row.)")
            unattributable.append(str(rel))
            continue
        for lineno, rid, owner in rows:
            mine = args.lane and lane_matches(owner, args.lane)
            tag = "YOURS" if mine else ("OTHER" if owner else "UNOWNED")
            print(f"  {tag:8} {rel}:{lineno}  {rid:9} owner={owner or '<unowned>'}")
            if args.lane and not mine:
                foreign.append(f"{rel}:{lineno} {rid} -> {owner or '<unowned>'}")

    if args.lane and (foreign or unattributable):
        print()
        print("REFUSED :: you are not the author of every contested row.")
        for f in foreign:
            print(f"  route to its author: {f}")
        for u in unattributable:
            print(f"  unattributable, route by hand: {u}")
        print("Joseph's rule, 2026-08-12: no lane's ledger row is merged by anyone but its author.")
        return 1
    print("OK :: every contested row is yours" if args.lane else "attribution complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
