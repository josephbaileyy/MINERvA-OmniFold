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
  * It attributes by ID BLOCK, not by authorship. A lane filing INSIDE another lane's range is
    confidently misattributed to the range's owner. NOTE, per Session D: BEN-089 was cited here as
    the example and DOES NOT DEMONSTRATE IT -- 89 is below every block, so the tool reports UNOWNED
    and refuses, which is the safe case. No current row demonstrates the real failure mode. Right
    claim, wrong evidence, in the paragraph written to prevent overstatement (BEN-096's shape).
  * VALIDATION_LEDGER.md rows CARRY `VL<n>` ids as of 2026-08-12 and are therefore nameable, but they
    are still UNOWNED: ownership is not derivable from a VL number, because ledger rows are written by
    whichever lane measured the number, in arrival order. A block table over VL could only be fiction.
    Until an owner side table keyed on the id exists, ledger conflicts report UNOWNED and are refused --
    which is the safe direction. It is the file with the second-most absorptions.
  * It sees rows, not prose. A conflict in a header paragraph is unattributable and reported as such.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent          # derived from __file__, never hardcoded (the p4_evidence.py lesson)

# `| D — verifier | `160-189` |`  /  `| A — orchestrator | `190-199` |`  /  `| repo infra | `200+` |`
# The `NNN+` alternative is REQUIRED, not decorative: the header's repo-infrastructure block is written
# `200+` and the closed-range-only pattern dropped it silently, so BEN-200/201/202 -- rows that already
# exist -- attributed as <unowned> and the gate told the operator to "route to its author: <unowned>".
BLOCK_ROW = re.compile(r"^>?\s*\|\s*([^|]+?)\s*\|\s*`(\d+)(?:-(\d+)|\+)`[^|]*\|", re.M)
OPEN_BLOCK_HI = 10 ** 9   # sentinel upper bound for an open-ended `NNN+` block
BEN_ROW = re.compile(r"^\|\s*BEN-(\d+)\s*\|")
CLM_ROW = re.compile(r"^\|\s*(CLM-\d+)\s*\|")
# VL ids added 2026-08-12 for ADDRESSABILITY, not ownership. A LEADING cell, deliberately: it is the
# only form matchable by one anchored pattern across VALIDATION_LEDGER.md's SEVEN distinct table
# widths (3,4,5,6,7,8,10 pipes). A trailing cell would need a per-width matcher, wrong for the eighth
# width someone adds. Ownership is NOT derivable from a VL number -- ledger rows are written by
# whichever lane measured the number, in arrival order, so a block table over VL could only be
# fiction. Owners come from a side table keyed on the id; until it exists these rows report UNOWNED
# and the gate refuses, which is the safe direction.
VL_ROW = re.compile(r"^\|\s*(VL\d+)\s*\|")
OI_ROW = re.compile(r"^\|\s*(OI-\d+)\s*\|\s*[^|]*\|\s*([^|]+?)\s*\|")
CONFLICT_START = re.compile(r"^<{7}")
CONFLICT_END = re.compile(r"^>{7}")

UNATTRIBUTABLE = "docs of no per-row id scheme"


def ben_blocks(findings: Path) -> list[tuple[int, int, str]]:
    """[(lo, hi, lane)] parsed from FINDINGS.md's header table. Raises if it cannot be found."""
    text = findings.read_text(encoding="utf-8", errors="replace")
    cut = text.find("## Long-form findings index")
    if cut < 0:
        # `text[:text.find(m)] or text[:8000]` was DEAD CODE: find() returns -1, so the slice is
        # text[:-1] -- the whole file -- and the `or` never fires because that slice is non-empty.
        # Measured by D: 2280 chars/5 blocks correct vs 38179 chars/5 blocks degraded. Fail loudly.
        raise SystemExit("FATAL: FINDINGS.md has no '## Long-form findings index' marker, so the "
                         "header cannot be delimited. Refusing to scan the whole file for block "
                         "rows -- a finding row shaped like a block row would become a lane.")
    head = text[:cut]
    out = []
    for lane, lo, hi in BLOCK_ROW.findall(head):
        lane = lane.strip().strip("*")
        if lane.lower().startswith(("lane", "---")) or not lane:
            continue
        out.append((int(lo), int(hi) if hi else OPEN_BLOCK_HI, lane))
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
    """Lines inside conflict markers. DEPTH-COUNTED, not a boolean.

    This was `inside = True/False`, so the FIRST `>>>>>>>` closed the region while an outer block was
    still open, and every row between an inner close and the outer close escaped attribution
    entirely. Session D demonstrated the consequence: a nested conflict made the gate report
    "OK :: every contested row is yours" and exit 0 on another lane's row -- a false pass in the gate
    whose entire purpose is preventing exactly that.

    It survived the substring false pass being fixed because I rebuilt the test for `lane_matches`
    and left this function's single well-formed-conflict case alone. D's rule, and it is the third
    instance in two days after BEN-084(B) and BEN-094(i): A REMEDY APPLIED TO THE SITE OF THE LAST
    FAILURE IS NOT APPLIED TO THE CLASS.

    An end marker with no start, and a start with no end, both scope to nothing -- which routes into
    NO ATTRIBUTABLE ROWS and refuses. That is the safe direction and it is deliberate.
    """
    depth, out = 0, set()
    for i, line in enumerate(text.splitlines(), 1):
        if CONFLICT_START.match(line):
            depth += 1
        if depth:
            out.add(i)
        if CONFLICT_END.match(line):
            depth = max(0, depth - 1)
    return out


def rows_in(path: Path, only_conflicts: bool, blocks, owners=None) -> list[tuple[int, str, str | None]]:
    """[(lineno, row_id, owner_or_None)]

    `owners` is the ROW-OWNERS.tsv mapping for id schemes that are not block-attributable
    (CLM, VL). Defaults to loading it, so a caller that forgets does not silently lose
    attribution -- the failure mode would be every CLM row reporting UNOWNED, which looks
    exactly like the pre-side-table world and would not be noticed.
    """
    if owners is None:
        owners = load_row_owners()
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
        # CLM and VL ids are SUBJECT-/ARRIVAL-allocated, so no arithmetic on the number yields
        # a lane. They are joined against the ROW-OWNERS.tsv side table instead. An id absent
        # from that table, or present with UNASSIGNED, resolves to None and the gate refuses.
        m = CLM_ROW.match(line)
        if m:
            out.append((i, m.group(1), owner_of_id(m.group(1), owners)))
            continue
        m = VL_ROW.match(line)
        if m:
            out.append((i, m.group(1), owner_of_id(m.group(1), owners)))
    return out


OWNERS_TSV = HERE / "ROW-OWNERS.tsv"
UNASSIGNED = "UNASSIGNED"


def load_row_owners(path: Path = OWNERS_TSV) -> dict[str, str]:
    """id -> owner, from the side table. Missing file is NOT an error: absent means every id
    reports UNOWNED, which is the pre-existing safe behaviour.

    `UNASSIGNED` is preserved as a VALUE rather than dropped, because the three states are
    genuinely different and collapsing two of them is how a vacuous pass gets built:
      * mapped to a lane  -> attributable; the gate can pass or refuse
      * UNASSIGNED        -> the id EXISTS in the table and nobody has decided. Gate exits 2.
      * absent            -> no mapping at all. Gate exits 2 as UNOWNED.
    If UNASSIGNED were dropped here it would become indistinguishable from `absent`, and both
    would read as "unowned" -- losing the fact that somebody deliberately listed the id and
    left the decision open. Same reason the audit script distinguishes "no digests" from
    "parser found none" (BEN-196).
    """
    owners: dict[str, str] = {}
    if not path.exists():
        return owners
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            continue
        rid, owner = parts[0].strip(), parts[1].strip()
        if not rid or rid.lower() == "id":      # skip the column header
            continue
        owners[rid] = owner
    return owners


def owner_of_id(rid: str, owners: dict[str, str]) -> str | None:
    """None means unattributable -- either absent from the table or explicitly UNASSIGNED.
    Callers must not treat None as permission; `lane_matches` already refuses on None."""
    o = owners.get(rid)
    if o is None or _lane_key(o) == UNASSIGNED:
        return None
    return o


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
    # The control that used to live here was `owner_of_ben(999999) is None`, and FIXING THE `200+`
    # PARSE MADE IT FALSE: an open-ended block owns every id above its floor, by design. Retaining it
    # would have been a test asserting a property the system deliberately does not have -- so it is
    # replaced rather than deleted, because "there exists an unowned id" is still the real invariant
    # and dropping the case entirely would leave the attributor free to answer everything again.
    open_blocks = [b for b in blocks if b[1] == OPEN_BLOCK_HI]
    if open_blocks:
        case("an open-ended block OWNS an arbitrarily high id (not unowned)",
             owner_of_ben(999999, blocks), open_blocks[0][2])
        case("...and the id below the lowest block is STILL unowned",
             owner_of_ben(lo0 - 1, blocks), None)
    else:
        case("absurdly high id is UNOWNED", owner_of_ben(999999, blocks), None)
    # PRESENCE, not just absence: the repo-infrastructure `200+` row must actually parse. Its absence
    # was invisible for exactly this reason -- every check here asked whether ids resolve, none asked
    # whether every documented block made it into the table.
    header_rows = (REPO / "docs/orchestration/FINDINGS.md").read_text(
        encoding="utf-8", errors="replace")
    header_rows = header_rows[: header_rows.find("## Long-form findings index")]
    documented = len([m for m in re.finditer(r"^>?\s*\|\s*[^|]+?\s*\|\s*`\d+(?:-\d+|\+)`", header_rows,
                                             re.M)])
    case("every documented block row is parsed (none silently dropped)", len(blocks), documented)
    # Blocks must not overlap, or an id has two owners and the rule cannot be enforced at all.
    spans = sorted((lo, hi) for lo, hi, _ in blocks)
    overlaps = [(a, b) for a, b in zip(spans, spans[1:]) if a[1] >= b[0]]
    case("no overlapping blocks", overlaps, [])
    # CONFLICT SCOPING: the form set, not one well-formed conflict. A single flat conflict is what
    # this suite had when D found that a NESTED one let another lane's row escape attribution
    # entirely -- the remedy for the substring false pass was applied to lane_matches and not to
    # the class, which is BEN-084(B)/BEN-094(i)'s shape a third time.
    nested = ("<<<<<<< A\n| BEN-171 | mine |\n<<<<<<< B\n| BEN-172 | mine |\n>>>>>>> B\n"
              "| BEN-131 | CONTESTED, C's row |\n>>>>>>> A\n")
    tmpn = REPO / "docs/orchestration/.whose_row_nested.tmp"
    try:
        tmpn.write_text(nested)
        got = sorted(r for _, r, _ in rows_in(tmpn, True, blocks))
        case("REGRESSION: nested conflict does not drop the row after the inner close",
             got, ["BEN-131", "BEN-171", "BEN-172"])
        tmpn.write_text(">>>>>>> orphan end\n| BEN-131 | x |\n")
        case("end marker with no start scopes to NOTHING (safe: refuses)",
             sorted(r for _, r, _ in rows_in(tmpn, True, blocks)), [])
        tmpn.write_text("<<<<<<< A\n| BEN-131 | x |\n")
        case("start with no end still scopes what follows it",
             sorted(r for _, r, _ in rows_in(tmpn, True, blocks)), ["BEN-131"])
    finally:
        tmpn.unlink(missing_ok=True)

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

    # END-TO-END EXIT CODES, run as a subprocess against a real conflicted file. `lane_matches` already
    # returned False for an empty lane above -- and the gate still exited 0, because the falsy `--lane`
    # short-circuited the accumulator before that answer was ever consulted. A unit check on the
    # predicate cannot see that; only the process's exit code can. This is A's own lesson from the
    # substring bug -- caught by an end-to-end merge, missed by the unit self-test -- applied here.
    probe = REPO / "docs/orchestration/.whose_row_exit_probe.tmp.md"
    try:
        probe.write_text("<<<<<<< HEAD\n| BEN-131 | a lane C row |\n=======\n>>>>>>> other\n")

        def run(*extra) -> int:
            return subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                   "--conflicts", *extra, str(probe)],
                                  capture_output=True, text=True).returncode

        case("EXIT: lane B on a lane C row REFUSES (1)", run("--lane", "B"), 1)
        case("EXIT: lane C on its own row passes (0)", run("--lane", "C"), 0)
        case("EXIT: --lane '' is FATAL (2), was a silent 0", run("--lane", ""), 2)
        case("EXIT: --lane '   ' is FATAL (2)", run("--lane", "   "), 2)
        case("EXIT: --lane omitted is attribution-only (0)", run(), 0)
    finally:
        probe.unlink(missing_ok=True)

    # ---- ROW-OWNERS side table. The three states must stay DISTINCT: collapsing UNASSIGNED
    # into "absent" loses the fact that someone listed the id and left the decision open, and
    # collapsing either into "owned" is a false pass on another lane's row.
    import tempfile as _tf, os as _os
    _fd, _tmp = _tf.mkstemp(suffix=".tsv"); _os.close(_fd)
    Path(_tmp).write_text(
        "# a comment line that must be ignored\n"
        "id\towner\tsource\tbasis\n"
        "CLM-900\tC\tdocs/orchestration/CLAIMS.md\tassigned to a real lane\n"
        "CLM-901\tUNASSIGNED\tdocs/orchestration/CLAIMS.md\tdeliberately undecided\n"
        "CLM-902\tB — uncertainty construction\tdocs/orchestration/CLAIMS.md\tfree text after the lane letter\n"
        "\n", encoding="utf-8")
    _own = load_row_owners(Path(_tmp))
    case("side table skips comments and the column header", sorted(_own), ["CLM-900", "CLM-901", "CLM-902"])
    case("an assigned id resolves to its lane", owner_of_id("CLM-900", _own), "C")
    case("UNASSIGNED resolves to None, NOT to a lane", owner_of_id("CLM-901", _own), None)
    case("an id absent from the table resolves to None", owner_of_id("CLM-999", _own), None)
    case("free text after the lane letter still resolves",
         _lane_key(owner_of_id("CLM-902", _own) or ""), "B")
    # The whole point: UNASSIGNED must never pass a gate, for ANY lane.
    for _ln in ("A", "B", "C", "D"):
        case(f"UNASSIGNED never matches lane {_ln}", lane_matches(owner_of_id("CLM-901", _own), _ln), False)
    case("an assigned row refuses a different lane", lane_matches(owner_of_id("CLM-900", _own), "B"), False)
    case("an assigned row passes its own lane", lane_matches(owner_of_id("CLM-900", _own), "C"), True)
    # A missing side table must degrade to "no mapping", not to an exception or a pass.
    case("a missing side table yields an empty mapping",
         load_row_owners(Path(_tmp + ".does-not-exist")), {})
    _os.unlink(_tmp)

    for label, ok, got, _ in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"  (got {got!r})"))
    print(f"  {len(blocks)} blocks parsed from FINDINGS.md's header, {len(checks)} checks")
    for f in failures:
        print(f"  FAIL {f}")

    print("SELF-TEST :: " + ("PASS" if not failures else "FAIL"))
    return 0 if not failures else 1


LEDGER_SEP = re.compile(r"^\s*\|[\s:|-]+\|?\s*$")


def ledger_partition(lines):
    r"""(separators, headers, data rows) by STRUCTURE, never by keyword.

    header = the line immediately above a separator. This replaced a KEYWORD LIST
    (`ID|claim|item|quantity|arm|#`) that matched 7 of 22 real headers and yielded a data-row count of
    123 where the truth is 108 -- and two independent derivations AGREED because they SHARED THAT WRONG
    OPERAND, which is BEN-086's shape. Same family as `\btol\b` matching inside `psd_tol`, the `\dead{`
    regex disagreeing with TeX's parser, and `lane.lower() in owner.lower()`: WHEN THE ARTIFACT HAS A
    GRAMMAR, MATCH THE GRAMMAR, NOT WHAT ITS INSTANCES TEND TO SAY.

    The grammar is AMBIGUOUS rather than exact: a data row whose cells were literally dashes would match
    the separator pattern and would promote the row above it to header. Zero instances today -- latent,
    not occupied -- and the count assertion below is what would catch it.
    """
    sep = [i for i, l in enumerate(lines, 1) if LEDGER_SEP.match(l)]
    hdr = [i - 1 for i in sep if i - 2 >= 0 and lines[i - 2].lstrip().startswith("|")]
    tab = [i for i, l in enumerate(lines, 1) if l.lstrip().startswith("|")]
    s, h = set(sep), set(hdr)
    return sep, hdr, [i for i in tab if i not in s and i not in h]


def check_ledger_ids(ledger):
    """TWO-SIDED completeness on the VL ids. 0 ok / 1 violated / 2 cannot check.

    One-sided cannot distinguish a half-finished re-id from rows having been deleted; two sides fail with
    OPPOSITE SIGNS, so the message names which. Per BEN-162 this covers the FORM SET rather than one
    variant: half-finished, deleted, duplicated, gapped, renumbered-from-2.
    """
    if not ledger.exists():
        print("CANNOT CHECK :: VALIDATION_LEDGER.md absent")
        return 2
    lines = ledger.read_text(encoding="utf-8", errors="replace").splitlines()
    sep, hdr, data = ledger_partition(lines)
    ids = [VL_ROW.match(lines[i - 1]).group(1) for i in data if VL_ROW.match(lines[i - 1])]
    nums = [int(v[2:]) for v in ids]
    print(f"  [{len(sep)} separators, {len(hdr)} headers, {len(data)} data rows, {len(ids)} VL ids]")
    fail = []
    if len(ids) != len(data):
        which = "HALF-FINISHED re-id" if len(ids) < len(data) else "ROWS DELETED after id assignment"
        fail.append(f"{which}: {len(ids)} ids against {len(data)} data rows")
    if len(set(nums)) != len(nums):
        fail.append(f"DUPLICATED ids: {sorted({n for n in nums if nums.count(n) > 1})[:5]}")
    if nums and sorted(nums) != list(range(1, len(nums) + 1)):
        if min(nums) != 1:
            fail.append(f"RENUMBERED-FROM-{min(nums)}: ids must be dense from 1")
        else:
            fail.append(f"GAPS: {sorted(set(range(1, max(nums) + 1)) - set(nums))[:5]}")
    for f in fail:
        print(f"  FAIL {f}")
    print("LEDGER-IDS :: " + ("PASS" if not fail else "FAIL"))
    return 0 if not fail else 1


# Duplicate `OI-*` ids that are DELIBERATELY tolerated, each with its reason. Read
# `FINDING-20260813-colliding-in-a-namespace-you-just-warned-about.md` before adding to this.
#
# WHY A WAIVER AND NOT A NARROWED CHECK: lane D's argument, adopted 2026-08-13 -- a waiver and a scope
# do the same job, except a waiver is reviewable in the source. Narrowing the check to "ids above 65"
# would hide the exception in a predicate; this names it.
#
# WHY THESE TWO ARE NOT RENUMBERED, which is the obvious alternative: lane A and lane C independently
# allocated BOTH ids by `max(existing)+1` on 2026-08-13 (BEN-223), and both are already cited in pushed
# commit messages and in sibling documents. Renumbering would silently break those references -- the
# BEN-216 / BEN-219 defect -- so they were resolved by ANNOTATION: each row leads with
# `⚠ ID COLLISION` naming the other's subject.
OI_ID_WAIVERS = {
    "OI-64": "A: verify_hash_bindings guarding nothing / C: deployment-parity check with no caller. "
             "BEN-223; annotated not renumbered, both cited in pushed commits.",
    "OI-65": "A: receipt-retirement liveness exposure / C: reconcile_gate5_family audit repair. "
             "BEN-223; annotated not renumbered, both cited in pushed commits.",
}


# The block table lives in docs/OPEN_ITEMS.md and is PARSED, not duplicated here. Hardcoding the ranges
# would make the document and the check able to disagree, which is BEN-201's shape (a retraction that
# landed in the index but not at the point of use). Requires the leading `>` so this cannot accidentally
# match a row of the main OI table or any other backticked range in the file.
OI_BLOCK_ROW = re.compile(r"^>\s*\|\s*([^|]+?)\s*\|\s*`(\d+)-(\d+)`", re.M)
OI_PRE_BLOCK_MAX = 69          # `1-69` is the closed pre-block era; see the table's own note
OI_FALLBACK_LANE = "Joseph / unattributed"


def oi_blocks(items) -> list[tuple[str, int, int]]:
    """[(lane, lo, hi)] from OPEN_ITEMS.md's own block table, in document order."""
    text = items.read_text(encoding="utf-8", errors="replace")
    return [(m.group(1), int(m.group(2)), int(m.group(3))) for m in OI_BLOCK_ROW.finditer(text)]


def _committer() -> str | None:
    """The identity this commit will carry. Reads `git config user.name`, which DOES see a
    `git -c user.name=...` override -- measured 2026-08-14 with a throwaway repo and a probe hook,
    because the whole check hangs off it and "config is inherited by hooks" was worth confirming
    rather than assuming."""
    try:
        r = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, cwd=REPO)
        return r.stdout.strip() or None
    except OSError:
        return None


def _identity_token(who: str) -> str:
    """Committer name -> the lane token the block table uses.

    `_lane_key` alone is NOT enough and the power test is what showed it: the lanes commit as
    `Lane A (Eavail)`, `Lane C (PET)`, and `_lane_key` yields `LANE A` for the first -- which matches no
    row, so EVERY lane silently fell through to the `Joseph / unattributed` block and would have been
    refused its own ids. Same family as the `lane.lower() in owner.lower()` bug this file's own
    `lane_matches` docstring records, except this one failed CLOSED (wrong and loud) rather than open.
    """
    return _lane_key(re.sub(r"^\s*lane\s+", "", who, flags=re.I))


def _block_for(who: str | None, blocks: list[tuple[str, int, int]]) -> list[tuple[str, int, int]]:
    """The blocks `who` may allocate from; the declared fallback when nothing matches, never everything."""
    if who:
        tok = _identity_token(who)
        owned = [b for b in blocks if tok and _lane_key(b[0]) == tok]
        if owned:
            return owned
    return [b for b in blocks if b[0] == OI_FALLBACK_LANE]


def _ids_at_head(rel: str) -> set[str] | None:
    """OI ids in HEAD's copy of `rel`, or None if that cannot be read.

    None is propagated as CANNOT-CHECK for the block arm rather than treated as "no ids", which would
    make every existing id look newly added and fail the commit for the wrong reason.
    """
    try:
        r = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=REPO)
        if r.returncode != 0:
            return None
    except OSError:
        return None
    return {m.group(1) for m in (OI_ROW.match(l) for l in r.stdout.splitlines()) if m}


def check_oi_ids(items) -> int:
    """No duplicate `OI-*` id in OPEN_ITEMS.md. 0 ok / 1 violated / 2 cannot check.

    Added 2026-08-13 on BEN-223: `OI-*` has no block table and no addressing convention (OI-62(b), still
    Joseph's call), so `max(existing)+1` is the only available algorithm and TWO CONCURRENT LANES RUNNING
    IT COLLIDE BY CONSTRUCTION. Lane A filed that warning in the morning and collided with lane C the
    same day, on two ids, surfaced only by a rebase. Writing the rule down did not work; this is the
    executable form, per CLAUDE.md's own preference for one.

    IT DOES NOT PREVENT THE COLLISION -- nothing local can, since the other lane's row is not in your
    tree until you pull. It makes it LOUD AT THE NEXT COMMIT rather than at a rebase days later, which is
    the difference between a conflict you resolve and a cross-reference someone acts on.

    THREE-SIDED, per BEN-162's form set, because a one-sided duplicate check passes on an empty file:
      * ids fewer than data rows -> a half-finished re-id, or a row whose id cell was damaged;
      * a duplicate that is not waived -> the collision this exists for;
      * A WAIVER THAT IS NO LONGER NEEDED -> also a failure. A stale waiver silently authorizes the next
        genuine collision on that same id forever, so a guard that outlives its reason becomes a hole.
        This is the direction that gets left out, and it is the one that turns a fix into a trap.

    A KNOWN ASYMMETRY IN THE BLOCK ARM, raised by lane D 2026-08-14 and left OPEN deliberately, with the
    reason, because an undocumented asymmetry is the BEN-173 / BEN-180 shape (a control on one side and
    none on its mirror):

        reject direction  -- a lane that forgets `git -c` and files OUTSIDE the fallback block fails
                             LOUDLY, and now gets a NOTE naming the `git -c` form.
        accept direction  -- a lane that forgets `git -c` and files INSIDE the fallback block
                             (120-129) is ACCEPTED SILENTLY, attributed to the fallback, not to itself.

    Why it is not closed here rather than being overlooked:

      1. COLLISION SAFETY IS ALREADY COVERED. Two parties both defaulting to the fallback and both
         running max+1 would collide, and the DUPLICATE arm catches that. What the accept case loses is
         ATTRIBUTION, not collision-safety, and attribution is OI-62(c) -- three parties sharing one git
         identity -- which is WAITING-USER.
      2. "ACCEPT BUT WARN" IS NOT IMPLEMENTABLE IN A HOOK. `.githooks/pre-commit`'s `run()` captures each
         check's output and `cat`s it ONLY on non-zero exit, so a passing check's output is discarded
         (BEN-226, measured with a control). The only available behaviours are fail or nothing.
         A third branch -- RECORD, write the observation and have something else surface it -- was raised
         and collapses: into the tree mid-commit it touches unstaged files and would corrupt this arm's own
         HEAD-vs-staged diff; outside the tree it is a channel nobody watches; and to a destination that IS
         watched it is simply the "put it in a test" remedy, not a third option.
      3. FAILING WOULD BLOCK A LEGITIMATE COMMITTER. Joseph filing in his own block is correct, and
         D's admitting rule -- a committer who did nothing wrong can always make it pass -- forbids it.

    THE TRIGGER THAT UNLOCKS THE FIX, so this is a conditional TODO and not a vague someday: if OI-62(c)
    is resolved such that every committer carries a lane identity, then NOBODY legitimately files into the
    fallback block, and an id arriving there becomes free to detect as an error. Revisit then, not before.
    """
    if not items.exists():
        print("CANNOT CHECK :: docs/OPEN_ITEMS.md absent")
        return 2
    lines = items.read_text(encoding="utf-8", errors="replace").splitlines()
    sep, hdr, data = ledger_partition(lines)
    ids = [OI_ROW.match(lines[i - 1]).group(1) for i in data if OI_ROW.match(lines[i - 1])]
    # A discoverer that matches nothing reports success -- the failure mode verify_hash_bindings.py's
    # SHELL_PIN_FLOOR and test_hash_bindings.py's launch-code floor both exist to catch. Zero is
    # CANNOT CHECK, never PASS.
    if not data or not ids:
        print(f"CANNOT CHECK :: {len(data)} data rows, {len(ids)} OI ids -- the row grammar no longer "
              f"matches, so this check would pass vacuously")
        return 2
    counts = {i: ids.count(i) for i in dict.fromkeys(ids)}
    dupes = {i: n for i, n in counts.items() if n > 1}
    print(f"  [{len(data)} data rows, {len(ids)} OI ids, {len(dupes)} duplicated, "
          f"{len(OI_ID_WAIVERS)} waived]")
    fail = []
    if len(ids) != len(data):
        fail.append(f"HALF-FINISHED re-id or damaged id cell: {len(ids)} ids against {len(data)} data rows")
    for i, n in sorted(dupes.items()):
        if i not in OI_ID_WAIVERS:
            fail.append(f"DUPLICATE {i} x{n} -- two lanes allocated it. Do NOT renumber a row that is "
                        f"already cited elsewhere; annotate both and add a waiver with the reason")
    for i in sorted(OI_ID_WAIVERS):
        if i not in dupes:
            fail.append(f"STALE WAIVER {i} is waived but is no longer duplicated -- remove it, or it "
                        f"silently permits the next real collision on that id")

    # BLOCK ARM (OI-62(b), added 2026-08-14). Applies ONLY to ids this commit adds: 65 ids predate the
    # table and are grandfathered by the `1-69` pre-block row. Without the HEAD diff every existing id
    # would look new and the check would fail every commit -- correct-looking and useless.
    blocks = oi_blocks(items)
    head_ids = _ids_at_head("docs/OPEN_ITEMS.md")
    if not blocks:
        print("  block arm CANNOT CHECK :: no block table found in OPEN_ITEMS.md -- allocation is "
              "unenforced, which is the state OI-62(b) describes")
    elif head_ids is None:
        print("  block arm CANNOT CHECK :: HEAD:docs/OPEN_ITEMS.md unreadable, so 'newly added' is "
              "undefined (every id would look new)")
    else:
        who = _committer()
        owned = _block_for(who, blocks)
        added = sorted(int(i[3:]) for i in set(ids) - head_ids)
        span = ", ".join(f"{lo}-{hi}" for _, lo, hi in owned) or "NONE"
        print(f"  [committer {who!r} -> block {span}; {len(added)} id(s) added vs HEAD: "
              f"{added or '-'}]")
        # A MANUAL run reads the repo's default identity, while the hook reads the `git -c user.name=`
        # override the lane commits with -- so pre-flighting this by hand can report a FAIL on an id that
        # is correctly inside your own block. Said here because the failure text otherwise reads as "your
        # id is wrong" when the real answer is "this process is not your commit".
        if added and owned and owned[0][0] == OI_FALLBACK_LANE:
            print(f"  NOTE :: {who!r} matched no lane block, so the fallback applies. If you are a lane "
                  f"pre-flighting by hand, re-run as `git -c user.name=\"Lane X (...)\" ...` or just "
                  f"commit -- the hook sees your per-commit identity, this process sees the repo default.")
        for n in added:
            if n <= OI_PRE_BLOCK_MAX:
                fail.append(f"OI-{n} BACKFILLS the closed pre-block range 1-{OI_PRE_BLOCK_MAX} -- a new "
                            f"item must not sort among items filed weeks earlier. Take your lane's block")
            elif not any(lo <= n <= hi for _, lo, hi in owned):
                fail.append(f"OI-{n} IS OUTSIDE {who!r}'s block ({span}) -- this is the max(existing)+1 "
                            f"habit that produced two collisions on 2026-08-13. Renumber it into your "
                            f"block, or if the block is exhausted take the next free closed ten-block and "
                            f"write it into OPEN_ITEMS.md's table in this same commit")
    for f in fail:
        print(f"  FAIL {f}")
    if dupes and not fail:
        for i in sorted(dupes):
            print(f"  waived {i} x{dupes[i]} :: {OI_ID_WAIVERS[i]}")
    print("OI-IDS :: " + ("PASS" if not fail else "FAIL"))
    return 0 if not fail else 1


def check_row_owners() -> int:
    """Validate ROW-OWNERS.tsv against the files it claims to describe. 0 ok / 1 drift / 2 cannot-check.

    TWO-SIDED, for the reason the ledger id check is: a one-sided check passes on an empty
    table. Both directions are failures worth naming:
      * an id in the table that does NOT exist in its source file -> a typo or a deleted row,
        and it will silently never match anything;
      * an id in a source file that is NOT in the table -> unattributable, which is safe but
        must be COUNTED, because "0 unmapped" and "we never looked" print the same otherwise.
    """
    owners = load_row_owners()
    if not owners:
        print("ROW-OWNERS :: CANNOT CHECK -- side table is missing or empty, so nothing was validated.")
        print("  Every CLM/VL row will report UNOWNED and the gate will refuse. That is safe, not verified.")
        return 2

    problems, assigned, unassigned = [], 0, 0
    # Which source file each id claims to live in, from column 3 when present.
    sources: dict[str, str] = {}
    for raw in OWNERS_TSV.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) >= 3 and parts[0].strip() and parts[0].strip().lower() != "id":
            sources[parts[0].strip()] = parts[2].strip()

    for rid, owner in sorted(owners.items()):
        if _lane_key(owner) == UNASSIGNED:
            unassigned += 1
        else:
            assigned += 1
        src = sources.get(rid)
        if not src:
            problems.append(f"{rid}: no source file column, so its existence cannot be checked")
            continue
        p = REPO / src
        if not p.exists():
            problems.append(f"{rid}: source file {src} does not exist")
            continue
        if not re.search(rf"^\|\s*{re.escape(rid)}\s*\|", p.read_text(encoding='utf-8', errors='replace'), re.M):
            problems.append(f"{rid}: listed here but NO leading-cell row in {src}")

    # Reverse direction: ids present in the sources but absent from the table.
    unmapped: list[str] = []
    for src in sorted(set(sources.values())):
        p = REPO / src
        if not p.exists():
            continue
        for m in re.finditer(r"^\|\s*((?:CLM-\d+|VL\d+))\s*\|", p.read_text(encoding='utf-8', errors='replace'), re.M):
            if m.group(1) not in owners:
                unmapped.append(f"{src}:{m.group(1)}")

    print(f"ROW-OWNERS :: {len(owners)} ids -- {assigned} assigned, {unassigned} UNASSIGNED; "
          f"{len(unmapped)} id(s) in the sources with no table entry")
    if unassigned:
        print(f"  {unassigned} UNASSIGNED means NOBODY HAS DECIDED, not 'anyone may edit'. The gate exits 2 on these.")
    if unmapped:
        print("  unmapped (report UNOWNED, gate refuses): " + ", ".join(unmapped[:12])
              + (" ..." if len(unmapped) > 12 else ""))
    for pr in problems:
        print(f"  DRIFT {pr}")
    print("ROW-OWNERS :: " + ("PASS" if not problems else "FAIL"))
    return 1 if problems else 0


# ==================================================================================================
# CLEAN-MERGE VERIFICATION, added 2026-09-08.
#
# WHY. A merge that AUTO-RESOLVES has no unmerged files, so everything above examined nothing and
# `main` returned 2 -- which meant a green exit was UNREACHABLE for every clean merge. Three
# independent observations (a resolved prose conflict, a pristine single-file branch, a clean
# evidence merge) all landed on the same 2, and five branches sat blocked behind it. Joseph's
# ruling of 2026-09-08 makes a refusal terminal and names exactly two legal exits: remove the
# cause and re-run to green, or FIX THE GATE. Green was not reachable, so this is the second exit.
# The refusing paths are untouched: no code below maps an existing 2 onto 0.
#
# THE HOLE IN THE OBVIOUS FIX, which is the whole reason this is 150 lines and not three.
# "MERGE_HEAD present + zero unmerged entries -> 0" is WRONG, and wrong in the one direction that
# matters. An operator who hits a REFUSED foreign conflict, resolves it by hand and `git add`s it
# has zero unmerged entries too -- so that version hands a 0 to the exact act this gate exists to
# refuse, through the door being opened for clean merges. A refusal would become launderable by
# `git add`, and the gate would be worse than the one that refused everything.
#
# SO THE CLAIM IS NOT "the index looks clean now". It is:
#
#     the ORIGINAL merge of THESE EXACT PARENTS was conflict-free -- recomputed here, from the two
#     parent commits alone -- and what is staged is byte-identical to that recomputation.
#
# The recomputation reads only `HEAD` and `MERGE_HEAD`, so it is INDEPENDENT of anything the
# operator did to the index. Measured on a throwaway repository before this was written:
# `git merge-tree --write-tree HEAD MERGE_HEAD` still exits 1 after the conflict has been
# hand-resolved and staged, and `git diff --diff-filter=U` is empty at that same moment. That gap
# between the two facilities is what closes the laundering path, and it is why the reconstruction
# is not optional decoration on a cheaper check.
#
# ISOLATION. `--write-tree` writes TREE OBJECTS (that is what the flag means, and they are
# unreferenced until something points at them), and every git invocation here that could touch an
# index is given a `GIT_INDEX_FILE` inside a throwaway directory: the reconstruction gets a
# never-created index path, and the staged tree is computed from a BYTE COPY of the real index.
# The real index and the working tree are never written. `test_whose_row_clean_merge.py` digests
# both before and after a run and requires them byte-identical, because "I touched nothing" is a
# measurement here and not a promise.
#
# EVERY CONDITION FAILS CLOSED, and each returns its OWN reason token rather than a shared one.
# The ruling's section 2 is explicit that "the guard refused" withholds the field that determines
# what to do next; a single CANNOT-CHECK token for eleven different inabilities would rebuild that
# defect one level down.
# ==================================================================================================


class CleanMergeVerdict(NamedTuple):
    """The measurement, not a boolean. `ok` is only true when all five conditions held.

    `reason` is a stable token, asserted by name in the tests: a message-only distinction would let
    the causes drift into each other, and the mutation battery needs to see WHICH condition spoke.
    """
    ok: bool
    reason: str
    detail: str
    head: str | None = None
    merge_head: str | None = None
    bases: tuple[str, ...] = ()
    reconstructed_tree: str | None = None
    staged_tree: str | None = None
    unmerged: int | None = None
    scope: tuple[str, ...] = ()


OID = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")   # sha1 or sha256, exactly


def _git(args: list[str], repo: Path, env_extra: dict[str, str] | None = None):
    """(rc, stdout, stderr), with rc None when git could not be EXECUTED at all.

    A separate helper rather than a refactor of the existing call sites, so their behaviour is
    untouched. `None` is deliberately not 0 and not 1: an inability must not be readable as either
    verdict, which is the distinction the CANNOT-CHECK code exists to preserve.
    """
    env = None
    if env_extra:
        env = dict(os.environ)
        env.update(env_extra)
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=str(repo), env=env)
    except OSError as exc:
        return None, "", f"{type(exc).__name__}: {exc}"
    return r.returncode, r.stdout, r.stderr


def _conflicted_paths(merge_tree_output: str) -> list[str]:
    """Paths from `merge-tree --write-tree`'s conflict block: `<mode> <oid> <stage>\\tpath`.

    Best-effort and used ONLY in a message. The VERDICT comes from the exit status, never from
    parsing this text -- a parser that found no paths must not be able to turn a conflicted
    reconstruction into a clean one.
    """
    out = []
    for line in merge_tree_output.splitlines()[1:]:
        if "\t" in line:
            out.append(line.split("\t", 1)[1])
    return sorted(set(out))


def verify_clean_merge(repo: Path = REPO) -> CleanMergeVerdict:
    """Was the in-progress merge of the exact parents independently reconstructible as conflict-free,
    and is that reconstruction what is staged? All five conditions required; any doubt refuses.

        C1  a merge is in progress and its EXACT parents are readable (HEAD, MERGE_HEAD)
        C2  the merge of those two commits is INDEPENDENTLY reconstructible here
        C3  that reconstruction was conflict-FREE
        C4  the staged result's tree is IDENTICAL to the reconstruction
        C5  (i)   the unmerged set enumerated successfully  -- established by the caller, which
                  returns 2 when `git diff --diff-filter=U` fails, and is why this function is only
                  reached on a successful enumeration;
            (ii)  zero unmerged entries, RE-MEASURED here with a second facility;
            (iii) the inspected scope is enumerable, so the pass can print what it looked at.

    C5(ii) is defence in depth and its exit-code effect is masked: an index carrying unmerged
    entries cannot produce a tree at all, so C4 would refuse anyway. It is kept, and kept FIRST,
    because it is the only one of the two that can NAME the cause -- `git write-tree` reports an
    inability, not "you are mid-conflict". Recorded here rather than discovered by the next reader,
    because a condition whose removal changes no verdict is exactly the kind of thing a mutation
    table quietly passes over.
    """
    tmp = Path(tempfile.mkdtemp(prefix="whose_row-mergecheck-"))
    try:
        # ---- C1: a merge is in progress, and the parents are the EXACT ones -----------------------
        # `--git-path`, not `.git/MERGE_HEAD`: in a linked worktree the merge state lives in the
        # worktree's own git dir, and every lane here runs in a linked worktree
        # (CONVENTION-lane-worktrees.md), so the hardcoded path would find nothing and this would
        # report NO-MERGE-IN-PROGRESS for every lane -- fail-closed, but permanently.
        rc, out, err = _git(["rev-parse", "--git-path", "MERGE_HEAD"], repo)
        if rc != 0 or not out.strip():
            return CleanMergeVerdict(False, "GIT-FAILURE",
                                     f"could not locate MERGE_HEAD (rc={rc}): {err.strip()}")
        mh_path = Path(out.strip())
        if not mh_path.is_absolute():
            mh_path = repo / mh_path
        if not mh_path.exists():
            return CleanMergeVerdict(
                False, "NO-MERGE-IN-PROGRESS",
                f"{mh_path} does not exist, so there is no merge whose parents could be "
                f"reconstructed. A FAST-FORWARD and an ALREADY-COMMITTED merge both land here: "
                f"neither has an in-progress merge to measure. If you need a gated record of a "
                f"fast-forward, re-run the merge with --no-ff --no-commit.")
        try:
            heads = [l.strip() for l in mh_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        except OSError as exc:
            return CleanMergeVerdict(False, "MERGE-HEAD-UNREADABLE", f"{mh_path}: {exc}")
        if len(heads) != 1:
            return CleanMergeVerdict(
                False, "NOT-A-TWO-PARENT-MERGE",
                f"MERGE_HEAD names {len(heads)} head(s). The reconstruction below merges TWO "
                f"commits; an octopus merge is not recomputable by it, so its parents cannot be "
                f"independently checked and this is not a pass.")
        rc, out, err = _git(["rev-parse", "--verify", "--quiet", "HEAD^{commit}"], repo)
        if rc != 0 or not OID.match(out.strip()):
            return CleanMergeVerdict(False, "PARENT-UNRESOLVABLE",
                                     f"HEAD does not resolve to a commit (rc={rc}): {err.strip()}")
        head = out.strip()
        rc, out, err = _git(["rev-parse", "--verify", "--quiet", heads[0] + "^{commit}"], repo)
        if rc != 0 or not OID.match(out.strip()):
            return CleanMergeVerdict(False, "PARENT-UNRESOLVABLE",
                                     f"MERGE_HEAD {heads[0]!r} does not resolve to a commit "
                                     f"(rc={rc}): {err.strip()}")
        merge_head = out.strip()

        # ---- C5(ii): zero unmerged entries, by a DIFFERENT facility than the caller used ----------
        rc, out, err = _git(["ls-files", "--unmerged", "-z"], repo)
        if rc != 0:
            return CleanMergeVerdict(False, "GIT-FAILURE", f"git ls-files --unmerged failed "
                                     f"(rc={rc}): {err.strip()}", head, merge_head)
        entries = [e for e in out.split("\0") if e]
        if entries:
            return CleanMergeVerdict(False, "UNMERGED-ENTRIES-PRESENT",
                                     f"{len(entries)} unmerged index entr(ies) remain, so this merge "
                                     f"is still being resolved", head, merge_head,
                                     unmerged=len(entries))

        # ---- C2: independent reconstruction, in an isolated index -------------------------------
        # The index path handed to merge-tree is inside the throwaway directory and is never
        # created; merge-tree does not use an index, and pinning it anyway means a git that DID
        # would write to the throwaway rather than to the operator's merge.
        rc, out, err = _git(["merge-tree", "--write-tree", head, merge_head], repo,
                            {"GIT_INDEX_FILE": str(tmp / "reconstruct.index")})
        if rc is None or rc not in (0, 1):
            # 129 is what git < 2.38 returns for `--write-tree` (measured: "unknown option"), 128
            # covers refusing unrelated histories and every other fatal. All of them mean THE
            # RECONSTRUCTION DID NOT HAPPEN, which is an inability, never a pass.
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-UNAVAILABLE",
                f"`git merge-tree --write-tree` did not run (rc={rc}): "
                f"{(err.strip() or out.strip())[:400]}. git >= 2.38 is required, and unrelated "
                f"histories are not reconstructed here.", head, merge_head)
        first = out.splitlines()[0].strip() if out.strip() else ""
        if not OID.match(first):
            return CleanMergeVerdict(False, "RECONSTRUCTION-UNAVAILABLE",
                                     f"`git merge-tree --write-tree` exited {rc} but its first line "
                                     f"is not a tree id: {first!r}", head, merge_head)
        # ---- C3: and it was conflict-FREE --------------------------------------------------------
        if rc == 1:
            paths = _conflicted_paths(out)
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-CONFLICTED",
                f"the merge of these exact parents CONFLICTS on {len(paths)} path(s): "
                f"{', '.join(paths[:8])}{' ...' if len(paths) > 8 else ''}. A clean index does not "
                f"change that: if those conflicts have been resolved by hand, the resolution is "
                f"exactly what this gate refuses to certify.",
                head, merge_head, reconstructed_tree=first, unmerged=0)
        rc2, out2, err2 = _git(["rev-parse", "--verify", "--quiet", first + "^{tree}"], repo)
        if rc2 != 0 or out2.strip() != first:
            return CleanMergeVerdict(False, "RECONSTRUCTION-UNAVAILABLE",
                                     f"the reconstructed id {first} is not a tree in this repository",
                                     head, merge_head)
        reconstructed = first

        # ---- C4: what is STAGED is byte-identical to the reconstruction ---------------------------
        # Computed from a COPY of the index, because `git write-tree` may rewrite the index's
        # cache-tree extension, and this function's contract is that it writes neither the index nor
        # the working tree.
        rc, out, err = _git(["rev-parse", "--git-path", "index"], repo)
        if rc != 0 or not out.strip():
            return CleanMergeVerdict(False, "STAGED-TREE-UNREADABLE",
                                     f"could not locate the index (rc={rc}): {err.strip()}",
                                     head, merge_head, reconstructed_tree=reconstructed)
        real_index = Path(out.strip())
        if not real_index.is_absolute():
            real_index = repo / real_index
        copied = tmp / "staged.index"
        try:
            shutil.copyfile(real_index, copied)
        except OSError as exc:
            return CleanMergeVerdict(False, "STAGED-TREE-UNREADABLE", f"{real_index}: {exc}",
                                     head, merge_head, reconstructed_tree=reconstructed)
        rc, out, err = _git(["write-tree"], repo, {"GIT_INDEX_FILE": str(copied)})
        if rc != 0 or not OID.match(out.strip()):
            return CleanMergeVerdict(False, "STAGED-TREE-UNREADABLE",
                                     f"`git write-tree` over a copy of the index failed (rc={rc}): "
                                     f"{err.strip()}", head, merge_head,
                                     reconstructed_tree=reconstructed)
        staged = out.strip()
        if staged != reconstructed:
            return CleanMergeVerdict(
                False, "TREE-MISMATCH",
                f"the staged tree {staged} is NOT the reconstruction {reconstructed}. Something was "
                f"changed on top of the automatic merge -- a hand resolution, a staged unrelated "
                f"edit, a different merge strategy or `-X` option, or renormalisation. Whatever it "
                f"was, it is a resolution this gate has not verified and will not certify.",
                head, merge_head, reconstructed_tree=reconstructed, staged_tree=staged, unmerged=0)

        # ---- C5(iii): name the inputs and enumerate the scope, so the pass is a MEASUREMENT -------
        rc, out, err = _git(["merge-base", "-a", head, merge_head], repo)
        if rc != 0 or not out.split():
            return CleanMergeVerdict(False, "MERGE-BASE-UNREADABLE",
                                     f"the parents' merge base could not be named (rc={rc}): "
                                     f"{err.strip()}", head, merge_head,
                                     reconstructed_tree=reconstructed, staged_tree=staged)
        bases = tuple(out.split())
        rc, out, err = _git(["diff-tree", "-r", "-z", "--no-commit-id", "--name-only",
                             head + "^{tree}", reconstructed], repo)
        if rc != 0:
            return CleanMergeVerdict(False, "SCOPE-UNENUMERABLE",
                                     f"could not enumerate what this merge changes (rc={rc}): "
                                     f"{err.strip()}", head, merge_head, bases,
                                     reconstructed_tree=reconstructed, staged_tree=staged)
        scope = tuple(p for p in out.split("\0") if p)
        return CleanMergeVerdict(True, "CLEAN-MERGE-VERIFIED",
                                 "the merge of these exact parents was reconstructed independently, "
                                 "conflict-free, and the staged tree is byte-identical to it",
                                 head, merge_head, bases, reconstructed, staged, 0, scope)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SCOPE_PRINT_LIMIT = 25


def clean_merge_report(v: CleanMergeVerdict, limit: int = SCOPE_PRINT_LIMIT) -> list[str]:
    """The lines a caller prints for `v`. Both directions print the parents when they are known:
    a refusal that does not say WHICH merge it was measuring is as underspecified as the bare
    "the guard refused" the 2026-09-08 ruling is about."""
    lines = []
    if not v.ok:
        lines.append(f"  clean-merge check :: {v.reason} -- {v.detail}")
        if v.head:
            lines.append(f"    parents inspected: HEAD={v.head[:12]} MERGE_HEAD="
                         f"{(v.merge_head or '?')[:12]}")
        return lines
    lines.append(f"CLEAN MERGE VERIFIED :: HEAD={v.head} + MERGE_HEAD={v.merge_head}")
    lines.append(f"  merge base(s):     {', '.join(v.bases)}")
    lines.append(f"  reconstruction:    git merge-tree --write-tree -> {v.reconstructed_tree} "
                 f"(exit 0, conflict-free, isolated index)")
    lines.append(f"  staged tree:       {v.staged_tree}  == the reconstruction")
    lines.append(f"  unmerged entries:  {v.unmerged} (git ls-files --unmerged)")
    lines.append(f"  scope inspected:   {len(v.scope)} path(s) this merge changes against HEAD")
    for p in v.scope[:limit]:
        lines.append(f"    {p}")
    if len(v.scope) > limit:
        lines.append(f"    ... and {len(v.scope) - limit} more")
    return lines



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="ledger files to attribute (default: the conflicted set)")
    ap.add_argument("--lane", help='your lane, e.g. "C" or "C - PET". Exit 1 if a row is not yours.')
    ap.add_argument("--conflicts", action="store_true", help="only rows inside conflict markers")
    ap.add_argument("--check-ledger-ids", action="store_true",
                    help="two-sided completeness on VALIDATION_LEDGER.md's VL ids; 0 ok / 1 "
                         "violated / 2 cannot check. A half-finished re-id and deleted rows fail "
                         "with opposite signs, so the message names which.")
    ap.add_argument("--check-owners", action="store_true",
                    help="validate ROW-OWNERS.tsv against the files it describes; 0 ok / 1 drift "
                         "/ 2 cannot check. Two-sided: a listed id missing from its source, and a "
                         "source id missing from the table, are different failures and both print.")
    ap.add_argument("--check-oi-ids", action="store_true",
                    help="no duplicate OI-* id in docs/OPEN_ITEMS.md; 0 ok / 1 violated / 2 cannot "
                         "check. Three-sided: a half-finished re-id, an unwaived duplicate, and a "
                         "WAIVER THAT IS NO LONGER NEEDED are three different failures and all print.")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.check_oi_ids:
        return check_oi_ids(REPO / "docs" / "OPEN_ITEMS.md")
    if args.check_owners:
        return check_row_owners()
    if args.check_ledger_ids:
        return check_ledger_ids(REPO / "VALIDATION_LEDGER.md")
    if args.self_test:
        return self_test()

    # A GATE THAT CANNOT FAIL, found 2026-08-12 by Lane B probing this script rather than using it.
    # `--lane ""` -- what `--lane "$LANE"` expands to when LANE is unset, which is how any wrapper or
    # hook will invoke this -- printed `OTHER` for every foreign row and then exited 0. The falsy
    # `args.lane` short-circuited BOTH the `if args.lane and not mine` accumulator and the final
    # `if args.lane and (foreign or unattributable)` check, so the tool identified the rows as somebody
    # else's and passed them anyway. Same direction and same class as the `lane.lower() in owner.lower()`
    # substring bug this file's own docstring records: a false pass inside the check written to prevent
    # false passes. Omitting `--lane` entirely stays legal -- that is the documented attribution-only
    # mode and it reports rather than gates -- but PRESENT-AND-EMPTY is now fatal, because the caller
    # asked to be gated and would have been told it passed.
    if args.lane is not None and not args.lane.strip():
        print("FATAL: --lane was given but is empty (an unset shell variable?). Refusing to run: an "
              "empty lane silently passed every foreign row before 2026-08-12. Pass your lane, or omit "
              "--lane entirely for attribution-only output.", file=sys.stderr)
        return 2

    blocks = ben_blocks(REPO / "docs/orchestration/FINDINGS.md")
    files = [Path(f) for f in args.files]
    if not files:
        try:
            out = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", "--diff-filter=U"],
                                 capture_output=True, text=True, check=True).stdout
            files = [REPO / p for p in out.split()]
        except (subprocess.CalledProcessError, OSError) as exc:
            # A gate that cannot run must not report that it ran. Distinguishing "git failed" from
            # "no conflicts" matters: the first is an inability, the second is a state.
            print(f"CANNOT CHECK :: could not enumerate unmerged files ({exc}).")
            return 2

    # VACUOUS PASS, closed. This previously printed "nothing to attribute" and returned 0, so
    # `whose_row.py --conflicts --lane C && git commit` passed when the tool had examined NOTHING.
    # That is the same shape as check_dead_containment.py's `pdf_text` returning "" -- Session D found
    # that one two commits earlier -- and as this repo's whole gates-that-cannot-fail class: a stage
    # that did not run reporting as a stage that passed.
    # The asymmetry is deliberate and matches --source-only's: the PERMISSIVE reading has to be asked
    # for. With --lane you are using this as a GATE, and a gate over zero files is not a pass; without
    # --lane you are using it as a QUERY, and an empty answer is a fine answer.
    if not files:
        if args.lane:
            # ZERO UNMERGED FILES IS NOW TWO STATES, NOT ONE. Until 2026-09-08 both landed on the 2
            # below, so no clean merge could reach a green exit and five branches were stuck behind a
            # refusal the ruling of that date makes terminal. The split is a MEASUREMENT and never an
            # absence: `verify_clean_merge` recomputes the merge of these exact parents from the two
            # parent commits alone, and passes only if that reconstruction was conflict-free AND is
            # byte-identical to what is staged. Reaching here at all establishes C5(i) -- the
            # enumeration above succeeded, because its failure returns 2 before this point.
            #
            # WHAT THIS DOES NOT DO, said here because it is the plausible misreading: it does not
            # map 2 onto 0. A hand-resolved conflict has zero unmerged files too, and it stays at 2
            # -- the reconstruction still conflicts, which is measured, not assumed. Nothing in the
            # refusal paths below was changed.
            verdict = verify_clean_merge(REPO)
            for line in clean_merge_report(verdict):
                print(line)
            if verdict.ok:
                print(f"OK [examined 0 unmerged file(s), 0 attributable row(s); "
                      f"{len(verdict.scope)} path(s) in the reconstructed merge] :: this merge "
                      f"auto-resolved and the reconstruction PROVES it -- so no contested row "
                      f"exists, and nobody resolved anyone else's row. You may commit this merge.")
                return 0
            print("CANNOT CHECK :: no unmerged files, so there is nothing to attribute and NOTHING "
                  "WAS CHECKED.")
            print("  If you are gating a merge, you are gating an empty set -- resolve the conflict "
                  "first, or name the files explicitly.")
            print("  If you only wanted to ask who owns what, omit --lane; a query may legitimately "
                  "return nothing, a gate may not.")
            print("  A CLEAN merge can pass here as of 2026-09-08, but only on an independent "
                  "reconstruction of its exact parents; the line above says which condition failed.")
            return 2
        print("no unmerged files; nothing to attribute  (query mode: 0 files, 0 rows)")
        return 0

    foreign, unattributable = [], []
    examined_files = examined_rows = 0
    for path in files:
        if not path.exists():
            # An absent file used to `continue` and fall through to "OK :: every contested row is
            # yours" -- a message asserting the opposite of what happened, over zero rows. Found by D.
            print(f"  ABSENT {path}")
            unattributable.append(f"{path} (absent)")
            continue
        examined_files += 1
        rows = rows_in(path, args.conflicts, blocks)
        examined_rows += len(rows)
        rel = path.relative_to(REPO) if REPO in path.parents else path
        if not rows:
            print(f"  {rel}: NO ATTRIBUTABLE ROWS -- resolve by hand and route to the author. "
                  f"(a prose conflict has no row; VALIDATION_LEDGER.md rows carry VL ids but are "
                  f"UNOWNED until the owner side table exists.)")
            unattributable.append(str(rel))
            continue
        for lineno, rid, owner in rows:
            mine = args.lane and lane_matches(owner, args.lane)
            tag = "YOURS" if mine else ("OTHER" if owner else "UNOWNED")
            print(f"  {tag:8} {rel}:{lineno}  {rid:9} owner={owner or '<unowned>'}")
            if args.lane and not mine:
                foreign.append(f"{rel}:{lineno} {rid} -> {owner or '<unowned>'}")

    # EVERY EXIT PRINTS ITS DENOMINATOR. This is the systematic form of the three false passes in
    # this file (vacuous file set, nested scoping, absent file): each printed a verdict without
    # saying what it had examined, and "0 rows, PASS" is indistinguishable from "40 rows, PASS" when
    # only the verdict is printed. BEN-077's receipt-ingredients convention applied to a gate.
    scope = f"[examined {examined_files} file(s), {examined_rows} attributable row(s)]"
    if args.lane and examined_rows == 0 and not foreign and not unattributable:
        print(f"CANNOT CHECK :: {scope} -- nothing was examined, so nothing was verified.")
        return 2
    if args.lane and (foreign or unattributable):
        print()
        print(f"REFUSED {scope} :: you are not the author of every contested row.")
        for f in foreign:
            print(f"  route to its author: {f}")
        for u in unattributable:
            print(f"  unattributable, route by hand: {u}")
        print("Joseph's rule, 2026-08-12: no lane's ledger row is merged by anyone but its author.")
        return 1
    print(f"OK {scope} :: every contested row is yours" if args.lane
          else f"attribution complete {scope}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
