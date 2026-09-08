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

    # ---- CLEAN-MERGE STATE, on real merges in throwaway repositories. See
    # _clean_merge_power_cases for why the newest pass-granting path is power-tested HERE and not
    # only in test_whose_row_clean_merge.py.
    for _label, _got, _want in _clean_merge_power_cases():
        case(_label, _got, _want)

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
#     parent commits alone, in a repository built for the purpose -- what is staged is byte-identical
#     to that recomputation, and the tracked working tree is byte-identical to what is staged.
#
# The recomputation reads only `HEAD` and `MERGE_HEAD`, so it is INDEPENDENT of anything the
# operator did to the index. Measured on a throwaway repository before this was written:
# `git merge-tree --write-tree HEAD MERGE_HEAD` still exits 1 after the conflict has been
# hand-resolved and staged, and `git diff --diff-filter=U` is empty at that same moment. That gap
# between the two facilities is what closes the laundering path, and it is why the reconstruction
# is not optional decoration on a cheaper check.
#
# THE SIXTH CONDITION, added 2026-09-08 in the same work, after two reviewers independently named
# the same line of this file's own receipt as the hole: it said the operand was the INDEX and that
# `git commit -a` would commit the working tree instead. That is a limit written down rather than
# closed, so an unstaged edit to a TRACKED file now refuses (`WORKTREE-DIFFERS-FROM-INDEX`).
# UNTRACKED files are ignored, deliberately and with no cost to the claim: `git commit -a` does not
# stage them either.
#
# ISOLATION, WHICH IS TWO CLAIMS AND NOT ONE.
#   (a) Nothing the operator owns is WRITTEN. `--write-tree` writes TREE OBJECTS (that is what the
#       flag means) and it now writes them into a throwaway repository, so unlike the first version
#       this one adds no loose objects to the operator's store either -- measured: their `objects/`
#       directory is byte-for-byte unchanged across a run. Every git invocation that could touch an
#       index is given a `GIT_INDEX_FILE` inside the throwaway directory, and the two index-derived
#       measurements (the staged tree, the working-tree comparison) run over BYTE COPIES.
#       `test_whose_row_clean_merge.py` digests the index and the working tree before and after a
#       run and requires them byte-identical, and digests the HOST repository's config and index
#       around the whole suite as well -- because on 2026-09-08 a fixture in this very work set
#       `core.bare=true` in a live `.git/config`, which is shared with every linked worktree, and
#       broke an unrelated checkout. "I touched nothing" is a measurement here, not a promise.
#   (b) Nothing the operator owns can DECIDE THE ANSWER. This is the claim the first version did not
#       have: `merge-tree` ran in the live repository, so `.git/info/attributes`, `~/.gitconfig` and
#       even an untracked working-tree `.gitattributes` could each turn the refusal below into a
#       pass. All three were reproduced. See the block above `_sanitized_env`.
#
# EVERY CONDITION FAILS CLOSED, and each returns its OWN reason token rather than a shared one.
# The ruling's section 2 is explicit that "the guard refused" withholds the field that determines
# what to do next; a single CANNOT-CHECK token for eleven different inabilities would rebuild that
# defect one level down.
# ==================================================================================================


class CleanMergeVerdict(NamedTuple):
    """The measurement, not a boolean. `ok` is only true when all conditions held.

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
    worktree_drift: tuple[str, ...] = ()   # C6: tracked paths where the working tree != the index
    isolation: tuple[str, ...] = ()        # C2: what was MEASURED about the reconstruction's env


OID = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")   # sha1 or sha256, exactly


def _git(args: list[str], repo: Path, env_extra: dict[str, str] | None = None,
         env_full: dict[str, str] | None = None):
    """(rc, stdout, stderr), with rc None when git could not be EXECUTED at all.

    A separate helper rather than a refactor of the existing call sites, so their behaviour is
    untouched. `None` is deliberately not 0 and not 1: an inability must not be readable as either
    verdict, which is the distinction the CANNOT-CHECK code exists to preserve.

    `env_extra` ADDS to the inherited environment; `env_full` REPLACES it. The reconstruction needs
    the second kind, because the variables that would defeat it -- `GIT_CONFIG_*`, `GIT_ATTR_*`,
    `GIT_NO_REPLACE_OBJECTS`, `GIT_DIR`, `HOME` -- are ones it has to guarantee are ABSENT or
    exactly what it set, and absence is not something you can guarantee by adding keys to a
    dictionary you did not build.
    """
    env = None
    if env_full is not None:
        env = dict(env_full)
        if env_extra:
            env.update(env_extra)
    elif env_extra:
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


# --------------------------------------------------------------------------------------------------
# THE RECONSTRUCTION'S ENVIRONMENT. Added 2026-09-08 after a reviewer reproduced the hole below
# against the first version, in which `git merge-tree` ran in the OPERATOR'S repository and only the
# index was isolated.
#
# THREE ATTACK VECTORS, ALL MEASURED on throwaway repositories, all against the same hand-resolved
# foreign conflict that the gate correctly refuses:
#
#   1. `.git/info/attributes` = `shared.txt merge=ours`, plus `merge.ours.driver=true`
#      -> `git merge-tree --write-tree HEAD MERGE_HEAD` exits 0, and the refusal becomes
#         CLEAN-MERGE-VERIFIED. This is the reviewer's reproduction, confirmed here.
#   2. `~/.gitconfig` carrying the same driver and a `core.attributesFile` -> exits 0 as well, so
#      neutralising only the repo-local file would have left the global one open.
#   3. An UNTRACKED, UNSTAGED `.gitattributes` in the working tree -> exits 0 as well. This is the
#      sharpest of the three: in a non-bare repository git reads merge attributes from the
#      WORKING-TREE file, so the state that decided the merge semantics was neither committed nor
#      staged nor even known to git as content.
#
# So the reconstruction was governed by exactly the operator-writable state it exists to be
# independent of. It now runs in a repository this function builds, whose only config file it wrote
# itself, and it REFUSES when that cannot be shown (`RECONSTRUCTION-NOT-ISOLATED`) -- an unprovable
# environment is an inability, not a pass.
#
# BUILT BY HAND, with file writes, and `git init`/`git config` are not invoked anywhere. That is not
# stylistic. On 2026-09-08 an earlier fixture in this very piece of work set `core.bare=true` by
# running `git config` with a cwd inside a live repository; `.git/config` is SHARED with every
# linked worktree, so it broke an unrelated checkout ("this operation must be run in a work tree")
# and wiped a worktree's index. A git dir is a handful of files -- `HEAD`, `config`, `objects/`,
# `refs/`, `info/attributes` -- so writing those files directly removes the whole class: there is no
# git invocation that could resolve some repository other than the one named by `GIT_DIR`. The same
# incident is the direct evidence for the finding above: live-repo git operations from this code
# path demonstrably mutate shared, operator-visible state.
#
# THE OBJECT STORE IS SHARED READ-ONLY through `objects/info/alternates`, so the reconstruction sees
# the exact parent commits, trees and blobs and copies nothing. MEASURED: on a fresh fixture the
# operator's `objects/` directory is byte-for-byte unchanged across a reconstruction, and the tree
# `merge-tree` writes exists only in the throwaway store -- so unlike the first version, this one
# adds no loose objects to the operator's repository at all.
#
# `.gitattributes` COMMITTED INSIDE THE MERGED TREES: still not honoured, and no longer assumed
# harmless. Neutralising every attribute source was once defended with the claim that
#
#     "a merge whose real semantics WERE altered by an attribute, from any source, produces a tree
#      that differs from the reconstruction and is refused by condition 4 (TREE-MISMATCH)"
#
# which is TRUE for attributes that CHANGE MERGED CONTENT (`merge=union`, a custom driver: the real
# merge produces a different tree and C4 sees it) and FALSE for attributes that FORCE A CONFLICT
# (`-merge`, or `binary` on a TEXT file). A conflict produces NO TREE AT ALL, so there is nothing
# for C4 to differ from: the OPERATOR supplies the tree, and they can supply exactly the one the
# neutralised reconstruction computes. Measured twice, by an independent reviewer and again here --
# `.gitattributes` committing `shared.txt -merge`, `shared.txt` seven lines a..g, side edits line 1,
# main edits line 7: the real merge exits 1 ("Cannot merge binary files") leaving three unmerged
# stages, the operator hand-resolves to the obvious combined text, and the pre-C7 gate certified it.
#
# C7 is why that path is closed now, and it REFUSES rather than reproduces: real git reads the
# WORKING-TREE `.gitattributes`, which is operator-writable and need not match anything committed,
# so "faithful" and "independent" are not simultaneously available and independence is the purpose
# of the reconstruction. An unreconstructed semantics is therefore a refusal, not a pass. The
# refusal is narrow by construction -- see `_check_merge_semantics`: only the paths git had to
# CONTENT-MERGE (changed against the single merge base on both sides, plus rename destinations),
# only from COMMITTED trees read into an index outside this repository, and only when the value is
# something other than `unspecified`. `linguist-vendored` and an unchanged `*.pdf binary` do not
# refuse; both are pinned as controls, because "refuse whenever a merge attribute exists" would
# refuse every merge in this repository and unreachable green is the defect this state repairs.
# The reconstruction itself still runs with an empty index and no operator attribute source at all.
# --------------------------------------------------------------------------------------------------


def _sanitized_env(git_dir: Path, scratch: Path) -> dict[str, str]:
    """The environment the reconstruction runs in: every inherited `GIT_*` variable DROPPED, and
    then only the ones named here set. `HOME` and `XDG_CONFIG_HOME` are moved into the scratch
    directory too, so `~/.gitconfig` and `~/.config/git/attributes` are absent rather than merely
    masked -- vector 2 above went through exactly those.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "HOME": str(scratch),
        "XDG_CONFIG_HOME": str(scratch),
        "GIT_DIR": str(git_dir),          # this repository, and nothing DISCOVERED from a cwd
        "GIT_INDEX_FILE": str(scratch / "reconstruct.index"),   # never created; merge-tree needs none
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "LC_ALL": "C", "LANG": "C",
    })
    return env                            # GIT_WORK_TREE is absent by construction: the filter drops it


def _build_isolated_gitdir(tmp: Path, objects_dir: Path, object_format: str) -> Path:
    """A minimal bare repository, written as files, sharing `objects_dir` read-only via alternates.

    `object_format` is mirrored rather than assumed: a sha256 repository's objects are unreadable
    through an alternate declared by a sha1 repository, and a reconstruction that silently could not
    read the parents would be reporting on nothing.
    """
    git_dir = tmp / "reconstruct.git"
    (git_dir / "objects" / "info").mkdir(parents=True)
    (git_dir / "refs" / "heads").mkdir(parents=True)
    (git_dir / "info").mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/isolated-reconstruction\n", encoding="utf-8")
    (git_dir / "info" / "attributes").write_text("", encoding="utf-8")
    cfg = ["[core]",
           "\trepositoryformatversion = " + ("1" if object_format == "sha256" else "0"),
           "\tbare = true",
           # A path that DOES NOT EXIST, so a hook cannot be found even if some future git grew one
           # here. `merge-tree` runs no hooks today; this is the belt beside the braces.
           f"\thooksPath = {tmp / 'no-hooks-and-none-created'}",
           f"\tattributesFile = {os.devnull}",
           "\tfsmonitor = false"]
    if object_format == "sha256":
        cfg += ["[extensions]", "\tobjectFormat = sha256"]
    (git_dir / "config").write_text("\n".join(cfg) + "\n", encoding="utf-8")
    (git_dir / "objects" / "info" / "alternates").write_text(f"{objects_dir}\n", encoding="utf-8")
    return git_dir


def _prove_isolation(git_dir: Path, env: dict[str, str], head: str,
                     merge_head: str) -> tuple[str | None, tuple[str, ...]]:
    """(why_not, facts). `why_not` is None only when the environment is DEMONSTRABLY free of
    operator influence; otherwise it is the sentence that says what could not be shown, and the
    caller refuses. `facts` are printed on the pass, so the isolation claim is a measurement in the
    receipt rather than a promise in a comment.

    THREE MEASUREMENTS, taken by asking git rather than by asserting:
      1. every config entry this git will read has scope `local` and origin the config file written
         above -- which covers global, system, per-worktree, command-line and `include.path` in one
         question, and would catch a future key of my own that came from somewhere unexpected;
      2. `refs/replace/` is empty here. Refs are NOT shared through `objects/info/alternates` -- only
         objects are -- so a replace ref in the operator's repository cannot reach this one, and
         `GIT_NO_REPLACE_OBJECTS=1` is set as well;
      3. both parents AND their trees resolve through the shared object store. Without this an
         alternate that did not work would surface as `RECONSTRUCTION-UNAVAILABLE` -- fail-closed,
         but naming the wrong cause and sending the operator to look at the wrong thing.
    """
    facts: list[str] = []
    cfg_origin = f"file:{git_dir / 'config'}"
    rc, out, err = _git(["config", "--list", "--show-scope", "--show-origin", "-z"], git_dir,
                        env_full=env)
    if rc is None or rc not in (0, 1):
        return (f"the isolated repository's config could not be enumerated (rc={rc}): "
                f"{err.strip()}", ())
    fields = out.split("\0")[:-1] if out else []
    if len(fields) % 3:
        return (f"`git config --show-scope --show-origin -z` returned {len(fields)} NUL-separated "
                f"fields, which is not a multiple of three, so the answer cannot be read", ())
    for i in range(0, len(fields), 3):
        scope, origin, key = fields[i], fields[i + 1], fields[i + 2].split("\n", 1)[0]
        if scope != "local" or origin != cfg_origin:
            return (f"the isolated repository would read {key!r} from scope {scope!r} at {origin!r}; "
                    f"only {git_dir / 'config'} may govern the reconstruction", ())
    facts.append(f"config:      {len(fields) // 3} entr(ies), every one scope=local from "
                 f"{git_dir / 'config'} (a file written by this process)")

    rc, out, err = _git(["for-each-ref", "--format=%(refname)", "refs/replace/"], git_dir,
                        env_full=env)
    if rc != 0:
        return f"refs/replace/ could not be checked (rc={rc}): {err.strip()}", ()
    if out.strip():
        return f"refs/replace/ is not empty in the isolated repository: {out.split()}", ()
    facts.append("replace:     refs/replace/ empty, refs are not shared through alternates, and "
                 "GIT_NO_REPLACE_OBJECTS=1")

    for label, oid in (("HEAD", head), ("MERGE_HEAD", merge_head)):
        for peel in ("commit", "tree"):
            rc, out, err = _git(["rev-parse", "--verify", "--quiet", f"{oid}^{{{peel}}}"], git_dir,
                                env_full=env)
            if rc != 0 or not OID.match(out.strip()):
                return (f"the shared object store does not deliver {label}'s {peel} ({oid[:12]}) to "
                        f"the isolated repository (rc={rc}): {err.strip()}", ())
    facts.append("objects:     both parents and both trees resolve through objects/info/alternates, "
                 "shared read-only")
    facts.append("attributes:  info/attributes empty, core.attributesFile=/dev/null, "
                 "GIT_ATTR_NOSYSTEM=1, and the")
    facts.append("             index is empty -- so merge semantics are git's BUILT-IN default and "
                 "an in-tree")
    facts.append("             .gitattributes is checked separately for unreconstructed merge semantics.")
    facts.append("hooks:       core.hooksPath points at a path that does not exist")
    return None, tuple(facts)


def _check_merge_semantics(
    repo: Path, iso: Path, env: dict[str, str], head: str, merge_head: str
) -> tuple[str | None, str, tuple[str, ...]]:
    """Check ancestry agreement and committed attributes before reconstruction."""
    if any(name in os.environ for name in
           ("GIT_SHALLOW_FILE", "GIT_GRAFT_FILE", "GIT_REPLACE_REF_BASE")):
        return "MERGE-GRAPH-UNVERIFIABLE", "inherited graph override", ()
    # Alternates share objects, but not shallow boundaries, grafts or replace refs.
    for graph_file in ("shallow", "info/grafts"):
        rc, out, err = _git(["rev-parse", "--git-path", graph_file], repo)
        if rc != 0 or not out.strip():
            return "MERGE-GRAPH-UNVERIFIABLE", err.strip(), ()
        path = Path(out.strip())
        if not path.is_absolute():
            path = repo / path
        try:
            if path.exists() and path.stat().st_size:
                return "MERGE-GRAPH-UNVERIFIABLE", f"local graph boundary: {graph_file}", ()
        except OSError as exc:
            return "MERGE-GRAPH-UNVERIFIABLE", str(exc), ()
    rc, out, err = _git(["for-each-ref", "--format=%(refname)", "refs/replace/"], repo)
    if rc != 0 or out.strip():
        return "MERGE-GRAPH-UNVERIFIABLE", "replace refs are present or unreadable", ()
    rc, out, err = _git(["merge-base", "-a", head, merge_head], iso, env_full=env)
    bases = tuple(out.split())
    if rc != 0 or not bases or any(not OID.fullmatch(base) for base in bases):
        return "MERGE-BASE-UNREADABLE", err.strip(), ()
    rc, out, err = _git(["merge-base", "-a", head, merge_head], repo)
    if rc != 0 or len(bases) != 1 or tuple(out.split()) != bases:
        return "MERGE-GRAPH-UNVERIFIABLE", "a single matching merge base is required", bases

    # ---- THE SCOPE: the paths git had to CONTENT-MERGE, which is the both-sides INTERSECTION ----
    # NOT the union of the two sides, and the difference is load-bearing rather than cosmetic. git
    # consults a `merge` attribute only where it runs a content merge, and it runs one only for a
    # path whose content differs from the merge base on BOTH sides; a path changed on one side alone
    # is taken from that side verbatim, so no attribute on it can alter the result or force a
    # conflict. MEASURED against the union form on 2026-09-08: this repository commits
    # `*.pdf binary` over 59 tracked PDFs, so a genuinely clean merge in which one side had rebuilt
    # a deliverable refused with UNRECONSTRUCTED-MERGE-ATTRIBUTES while the intersection was EMPTY
    # -- the unreachable green this branch exists to repair, walked back in through C7.
    #
    # RENAME DESTINATIONS ARE ADDED BACK IN, because a rename moves the content merge to the
    # destination path and git looks the attribute up THERE. MEASURED: `.gitattributes` carrying
    # `new.txt -merge`, side renames old.txt -> new.txt and edits it, main edits old.txt -> a
    # genuine conflict at new.txt, whose SOURCE path carries no attribute at all. A scope of
    # intersecting paths alone would have certified the hand resolution of that conflict, so the
    # narrowing is done with rename detection ON rather than by dropping `--no-renames`.
    #
    # `-l0` because rename detection can be skipped SILENTLY: measured, `-M -l1` over three inexact
    # renames exits 0, reports six D/A records where there are three R records, and says so only in
    # a warning on stderr. A skipped detection would drop the destination from this scope, so any
    # diagnostic at all from these two enumerations refuses instead of narrowing the scope.
    sides: list[set[str]] = []
    renames: dict[str, set[str]] = {}
    for parent in (head, merge_head):
        rc, out, err = _git(
            ["diff-tree", "-r", "-z", "-M", "-l0", "--no-commit-id", "--name-status",
             bases[0], parent], iso, env_full=env
        )
        if rc != 0 or err.strip():
            return "SCOPE-UNENUMERABLE", err.strip() or f"rc={rc}", bases
        fields = out.split("\0")[:-1] if out else []
        side: set[str] = set()
        cursor = 0
        while cursor < len(fields):
            status = fields[cursor]
            width = 3 if status[:1] in ("R", "C") else 2
            if not status or cursor + width > len(fields):
                return ("SCOPE-UNENUMERABLE",
                        f"a `diff-tree --name-status -z` record ({status!r}) is truncated, so the "
                        f"changed scope cannot be read", bases)
            if width == 3:
                source, destination = fields[cursor + 1], fields[cursor + 2]
                side.update((source, destination))
                renames.setdefault(source, set()).add(destination)
            else:
                side.add(fields[cursor + 1])
            cursor += width
        sides.append(side)
    content_merged = sides[0] & sides[1]
    content_merged |= {dst for src in tuple(content_merged) for dst in renames.get(src, ())}
    if not content_merged:
        return None, "", bases
    attr_env = dict(env, GIT_INDEX_FILE=str(iso.parent / "attributes.index"))
    for tree in (*bases, head, merge_head):
        rc, out, err = _git(["read-tree", tree], iso, env_full=attr_env)
        if rc != 0:
            return "MERGE-ATTRIBUTES-UNREADABLE", err.strip(), bases
        # Batches bound argv size while Git handles patterns, macros and nested files.
        paths = sorted(content_merged)
        for offset in range(0, len(paths), 64):
            batch = paths[offset:offset + 64]
            attrs = ("merge", "conflict-marker-size", "filter", "working-tree-encoding")
            rc, out, err = _git(
                ["check-attr", "--cached", "-z", *attrs, "--", *batch],
                iso, env_full=attr_env
            )
            fields = out.split("\0")[:-1]
            if rc != 0 or not out.endswith("\0") or len(fields) != len(batch) * len(attrs) * 3:
                return "MERGE-ATTRIBUTES-UNREADABLE", err.strip(), bases
            for index in range(0, len(fields), 3):
                path, attribute, value = fields[index:index + 3]
                if value != "unspecified":
                    return (
                        "UNRECONSTRUCTED-MERGE-ATTRIBUTES",
                        f"{path}: {attribute}={value} in committed tree {tree}", bases
                    )
    return None, "", bases


def verify_clean_merge(repo: Path = REPO) -> CleanMergeVerdict:
    """Was the in-progress merge of the exact parents independently reconstructible as conflict-free,
    is that reconstruction what is staged, and is the staged state what would actually be committed?
    All conditions required; any doubt refuses.

        C1  a merge is in progress and its EXACT parents are readable (HEAD, MERGE_HEAD)
        C2  the merge of those two commits is INDEPENDENTLY reconstructible, in a repository this
            function BUILDS, whose freedom from operator influence is measured and not assumed
        C3  that reconstruction was conflict-FREE
        C4  the staged result's tree is IDENTICAL to the reconstruction
        C5  (i)   the unmerged set enumerated successfully  -- established by the caller, which
                  returns 2 when `git diff --diff-filter=U` fails, and is why this function is only
                  reached on a successful enumeration;
            (ii)  zero unmerged entries, RE-MEASURED here with a second facility;
            (iii) the inspected scope is enumerable, so the pass can print what it looked at.
        C6  the TRACKED working tree matches the index, so `git commit -a` would record the same
            tree that C4 verified. Untracked files are ignored, deliberately.
        C7  the merge semantics are the ones that were reconstructed: no committed merge attribute
            on any path git had to CONTENT-MERGE (both sides changed it against the base, or it is
            the destination of a rename of such a path), and both repositories agree on a SINGLE
            merge base with no local graph override (grafts, shallow boundary, replace refs).

    C5(ii) is defence in depth and its exit-code effect is masked: an index carrying unmerged
    entries cannot produce a tree at all, so C4 would refuse anyway. It is kept, and kept FIRST,
    because it is the only one of the two that can NAME the cause -- `git write-tree` reports an
    inability, not "you are mid-conflict". Recorded here rather than discovered by the next reader,
    because a condition whose removal changes no verdict is exactly the kind of thing a mutation
    table quietly passes over.

    C2 AND C6 ARE ISOLATED IN OPPOSITE DIRECTIONS, and that asymmetry is the design, not an
    oversight. C2 asks WHAT THE MERGE MEANS, which must not depend on operator-local state, so it
    runs in a repository with a config file this function wrote and every attribute source
    neutralised. C6 asks WHAT THE OPERATOR'S NEXT COMMAND WOULD DO, which must depend on exactly
    that state, so it runs in the operator's own repository under the operator's own config: C6 is
    the prediction "`git add -u` would be a no-op", and a prediction about `git commit -a` has to be
    made with the settings `git commit -a` will use. A clean filter or an `assume-unchanged` bit
    that hides a working-tree edit from C6 hides it from `git commit -a` identically, so the two
    agree by construction, which is the property C6 needs.

    C6's OPERAND is a REFRESHED COPY of the index. `git diff-files` on an unrefreshed index reports
    any file whose stat data merely changed -- measured: `touch` alone is enough -- so the naive
    form would refuse a perfectly clean merge after any command that rewrote an mtime. The copy is
    refreshed in the throwaway directory; the operator's index is never written.
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

        # ---- C2: independent reconstruction, in an ISOLATED REPOSITORY --------------------------
        # Not merely an isolated index, which is all the first version had. See the block above
        # `_sanitized_env` for the three measured attack vectors this closes, and for why the
        # repository is built with file writes instead of `git init`.
        rc, out, err = _git(["rev-parse", "--git-path", "objects"], repo)
        if rc != 0 or not out.strip():
            return CleanMergeVerdict(False, "RECONSTRUCTION-NOT-ISOLATED",
                                     f"the object store to share read-only could not be located "
                                     f"(rc={rc}): {err.strip()}", head, merge_head)
        objects_dir = Path(out.strip())
        if not objects_dir.is_absolute():
            objects_dir = repo / objects_dir
        rc, out, err = _git(["rev-parse", "--show-object-format"], repo)
        object_format = out.strip() if rc == 0 else ""
        if object_format not in ("sha1", "sha256"):
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-NOT-ISOLATED",
                f"the repository reports object format {object_format!r} (rc={rc}). The isolated "
                f"repository has to declare the SAME one to read the parents through an alternate, "
                f"and it will not guess.", head, merge_head)
        try:
            iso = _build_isolated_gitdir(tmp, objects_dir.resolve(), object_format)
        except OSError as exc:
            return CleanMergeVerdict(False, "RECONSTRUCTION-NOT-ISOLATED",
                                     f"the isolated repository could not be built: {exc}",
                                     head, merge_head)
        iso_env = _sanitized_env(iso, tmp)
        why_not, isolation = _prove_isolation(iso, iso_env, head, merge_head)
        if why_not:
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-NOT-ISOLATED",
                f"the reconstruction environment could not be SHOWN free of operator influence, so "
                f"nothing computed in it would mean anything: {why_not}. An unprovable environment "
                f"is an inability, not a pass.", head, merge_head)
        reason, detail, bases = _check_merge_semantics(repo, iso, iso_env, head, merge_head)
        if reason:
            return CleanMergeVerdict(False, reason, detail, head, merge_head, bases,
                                     isolation=isolation)
        rc, out, err = _git(["merge-tree", "--write-tree", head, merge_head], iso,
                            env_full=iso_env)
        if rc is None or rc not in (0, 1):
            # 129 is what git < 2.38 returns for `--write-tree` (measured: "unknown option"), 128
            # covers refusing unrelated histories and every other fatal. All of them mean THE
            # RECONSTRUCTION DID NOT HAPPEN, which is an inability, never a pass.
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-UNAVAILABLE",
                f"`git merge-tree --write-tree` did not run (rc={rc}): "
                f"{(err.strip() or out.strip())[:400]}. git >= 2.38 is required, and unrelated "
                f"histories are not reconstructed here.", head, merge_head, isolation=isolation)
        first = out.splitlines()[0].strip() if out.strip() else ""
        if not OID.match(first):
            return CleanMergeVerdict(False, "RECONSTRUCTION-UNAVAILABLE",
                                     f"`git merge-tree --write-tree` exited {rc} but its first line "
                                     f"is not a tree id: {first!r}", head, merge_head,
                                     isolation=isolation)
        # ---- C3: and it was conflict-FREE --------------------------------------------------------
        if rc == 1:
            paths = _conflicted_paths(out)
            return CleanMergeVerdict(
                False, "RECONSTRUCTION-CONFLICTED",
                f"the merge of these exact parents CONFLICTS on {len(paths)} path(s): "
                f"{', '.join(paths[:8])}{' ...' if len(paths) > 8 else ''}. A clean index does not "
                f"change that: if those conflicts have been resolved by hand, the resolution is "
                f"exactly what this gate refuses to certify.",
                head, merge_head, reconstructed_tree=first, unmerged=0, isolation=isolation)
        # Asked of the ISOLATED repository, because that is where `--write-tree` wrote: the tree is
        # deliberately NOT added to the operator's object store (measured: their objects/ directory
        # is byte-for-byte unchanged across a reconstruction). Tree ids are content addresses, so
        # comparing this one to a tree hashed in the operator's repository at C4 is still exact.
        rc2, out2, err2 = _git(["rev-parse", "--verify", "--quiet", first + "^{tree}"], iso,
                               env_full=iso_env)
        if rc2 != 0 or out2.strip() != first:
            return CleanMergeVerdict(False, "RECONSTRUCTION-UNAVAILABLE",
                                     f"the reconstructed id {first} is not a tree in the isolated "
                                     f"repository", head, merge_head, isolation=isolation)
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

        # ---- C6: the TRACKED WORKING TREE matches the index --------------------------------------
        # C4 verified what `git commit` would record. `git commit -a`, `git add -u`, and every
        # editor's "commit all" button record the WORKING TREE instead, and the first version of
        # this function said so in its own receipt and stopped there. Two reviewers independently
        # named that line as the hole; a limit you can write down is a limit you can close.
        #
        # ON A REFRESHED COPY. `git diff-files` against an unrefreshed index reports every file
        # whose stat data merely changed -- measured: a bare `touch` is enough -- so the naive form
        # would refuse a genuinely clean merge after any command that rewrote an mtime. Refreshing
        # updates cached stat data only, never object ids, so it cannot hide a real edit, and it
        # happens on a COPY in the throwaway directory: the operator's index stays byte-identical.
        #
        # UNTRACKED FILES ARE IGNORED, on purpose, and `diff-files` is the facility that ignores
        # them by construction rather than by a filter I wrote. An operator carrying unrelated
        # scratch files must still be able to merge, and the boundary costs the claim nothing:
        # `git commit -a` does not stage untracked files either.
        refreshed = tmp / "worktree-check.index"
        try:
            shutil.copyfile(real_index, refreshed)
        except OSError as exc:
            return CleanMergeVerdict(False, "WORKTREE-STATE-UNREADABLE",
                                     f"the index could not be copied to compare against the "
                                     f"working tree: {real_index}: {exc}", head, merge_head,
                                     reconstructed_tree=reconstructed, staged_tree=staged,
                                     isolation=isolation)
        rc, out, err = _git(["update-index", "-q", "--refresh"], repo,
                            {"GIT_INDEX_FILE": str(refreshed)})
        if rc is None or rc not in (0, 1):
            # rc 1 is `--refresh`'s ordinary "some entries need updating", which is the very state
            # being measured and is reported by `diff-files` below. Anything else -- 128, or git not
            # running at all -- means the comparison did not happen, and that is a refusal.
            return CleanMergeVerdict(False, "WORKTREE-STATE-UNREADABLE",
                                     f"`git update-index --refresh` over a copy of the index did "
                                     f"not run (rc={rc}): {err.strip()}", head, merge_head,
                                     reconstructed_tree=reconstructed, staged_tree=staged,
                                     isolation=isolation)
        rc, out, err = _git(["diff-files", "--name-only", "-z"], repo,
                            {"GIT_INDEX_FILE": str(refreshed)})
        if rc != 0:
            return CleanMergeVerdict(False, "WORKTREE-STATE-UNREADABLE",
                                     f"`git diff-files` over a refreshed copy of the index failed "
                                     f"(rc={rc}): {err.strip()}, so whether the working tree "
                                     f"matches what was verified is UNKNOWN", head, merge_head,
                                     reconstructed_tree=reconstructed, staged_tree=staged,
                                     isolation=isolation)
        drift = tuple(p for p in out.split("\0") if p)
        if drift:
            return CleanMergeVerdict(
                False, "WORKTREE-DIFFERS-FROM-INDEX",
                f"{len(drift)} TRACKED file(s) differ between the working tree and the index: "
                f"{', '.join(drift[:8])}{' ...' if len(drift) > 8 else ''}. What was verified above "
                f"is the index, so `git commit` would record the reconstruction -- but `git commit "
                f"-a` would record these working-tree contents instead, and those have not been "
                f"verified against anything. Stage them and re-run if they belong in this merge, or "
                f"restore them. Untracked files are not counted here and never block a pass.",
                head, merge_head, reconstructed_tree=reconstructed, staged_tree=staged, unmerged=0,
                worktree_drift=drift, isolation=isolation)

        # The reconstructed tree exists only in the isolated object store.
        rc, out, err = _git(["diff-tree", "-r", "-z", "--no-commit-id", "--name-only",
                             head + "^{tree}", reconstructed], iso, env_full=iso_env)
        if rc != 0:
            return CleanMergeVerdict(False, "SCOPE-UNENUMERABLE",
                                     f"could not enumerate what this merge changes (rc={rc}): "
                                     f"{err.strip()}", head, merge_head, bases,
                                     reconstructed_tree=reconstructed, staged_tree=staged,
                                     isolation=isolation)
        scope = tuple(p for p in out.split("\0") if p)
        return CleanMergeVerdict(True, "CLEAN-MERGE-VERIFIED",
                                 "the merge of these exact parents was reconstructed independently, "
                                 "in an isolated repository, conflict-free; the staged tree is "
                                 "byte-identical to it; and the tracked working tree matches the "
                                 "index",
                                 head, merge_head, bases, reconstructed, staged, 0, scope,
                                 worktree_drift=(), isolation=isolation)
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
                 f"(exit 0, conflict-free)")
    lines.append("  reconstructed in:  a git dir this check BUILT, sharing the object store "
                 "read-only through alternates,")
    lines.append("                     so no operator-writable state could decide the merge. "
                 "MEASURED, not asserted:")
    for fact in v.isolation:
        lines.append(f"    {fact}")
    lines.append(f"  staged tree:       {v.staged_tree}  == the reconstruction")
    lines.append(f"  unmerged entries:  {v.unmerged} (git ls-files --unmerged)")
    lines.append("  worktree vs index: IDENTICAL for every TRACKED file -- git diff-files over a "
                 "REFRESHED COPY of the")
    lines.append("                     index, so a stale mtime cannot fake drift and the real index "
                 "is not written.")
    # The OPERAND, named in the same breath as the verdict. It is now the index AND the tracked
    # working tree: two reviewers named the `git commit -a` caveat the previous version printed here
    # as a hole to close rather than a limit to document, and condition 6 closes it.
    lines.append("  operand:           the INDEX *and* the tracked working tree, so `git commit` "
                 "and `git commit -a`")
    lines.append("                     would record the SAME tree -- the one verified above. NOT "
                 "covered: untracked")
    lines.append("                     files. `git commit -a` does not stage those either, so the "
                 "boundary costs")
    lines.append("                     this claim nothing.")
    lines.append(f"  scope inspected:   {len(v.scope)} path(s) this merge changes against HEAD")
    for p in v.scope[:limit]:
        lines.append(f"    {p}")
    if len(v.scope) > limit:
        lines.append(f"    ... and {len(v.scope) - limit} more")
    return lines



# The identity and config isolation the throwaway fixtures below need. `core.hooksPath` in this
# repository is an ABSOLUTE path (EnterWorktree normalises it for every lane), and a GLOBAL
# hooksPath would make a throwaway repo run this campaign's pre-commit hook -- which runs this
# self-test, which would build another throwaway repo. Identity comes from the environment so no
# fixture depends on a `git config` write having landed first.
_FIXTURE_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "whose_row self-test", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
    "GIT_COMMITTER_NAME": "whose_row self-test", "GIT_COMMITTER_EMAIL": "selftest@example.invalid",
    "GIT_AUTHOR_DATE": "2026-09-08T00:00:00 +0000",
    "GIT_COMMITTER_DATE": "2026-09-08T00:00:00 +0000",
}


def _fixture_git(repo: Path, *args: str, allow_fail: bool = False) -> str:
    rc, out, err = _git(list(args), repo, _FIXTURE_ENV)
    if rc != 0 and not allow_fail:
        raise SystemExit(f"FATAL: the clean-merge power test could not build its fixture: "
                         f"`git {' '.join(args)}` returned {rc} in {repo}\n{err}\n"
                         f"A power test that cannot run must not report PASS, so this is fatal "
                         f"rather than skipped.")
    return out


def _clean_merge_power_cases() -> list[tuple[str, object, object]]:
    """[(label, got, want)] for the clean-merge state, on REAL merges in throwaway repositories.

    WHY IT IS IN THE SELF-TEST and not only in test_whose_row_clean_merge.py: merge_guard.sh runs
    `--self-test` FIRST, so that a broken gate fails the merge instead of passing everything. The
    clean-merge state is the one that can hand out a 0, so leaving it out of the power test would
    put the newest pass-granting path outside the check whose whole job is guarding pass-granting
    paths -- and `lane_matches`' own docstring records that this file's one false pass was caught
    end-to-end and NOT by this self-test.

    NOTHING HERE MEASURES THE REAL REPOSITORY, deliberately. During a real merge the operator's
    tree is the object under test; a power test that read it would be reporting the answer instead
    of testing the instrument.

    Both directions, and the negative is the laundering path: a hand-resolved, staged conflict.
    """
    out: list[tuple[str, object, object]] = []
    tmp = Path(tempfile.mkdtemp(prefix="whose_row-selftest-merges-"))
    try:
        # ---- A: a genuine conflict-FREE merge, then two ways of spoiling it --------------------
        a = tmp / "clean"
        a.mkdir()
        _fixture_git(a, "init", "-q", "-b", "main", ".")
        (a / "base.md").write_text("base\n")
        _fixture_git(a, "add", "-A"); _fixture_git(a, "commit", "-q", "-m", "base")
        _fixture_git(a, "checkout", "-q", "-b", "side")
        (a / "side-only.md").write_text("side\n")
        _fixture_git(a, "add", "-A"); _fixture_git(a, "commit", "-q", "-m", "side")
        _fixture_git(a, "checkout", "-q", "main")
        (a / "main-only.md").write_text("main\n")
        _fixture_git(a, "add", "-A"); _fixture_git(a, "commit", "-q", "-m", "main")
        _fixture_git(a, "merge", "--no-ff", "--no-commit", "side")
        v = verify_clean_merge(a)
        out.append(("CLEAN MERGE: a real conflict-free merge VERIFIES", (v.ok, v.reason),
                    (True, "CLEAN-MERGE-VERIFIED")))
        out.append(("CLEAN MERGE: and its two trees are identical, not merely both present",
                    v.staged_tree == v.reconstructed_tree and bool(v.staged_tree), True))
        out.append(("CLEAN MERGE: the scope is MEASURED, not empty",
                    v.scope, ("side-only.md",)))
        # STAGED DRIFT on top of that same clean merge -- nothing about the merge changed, but what
        # would be committed did.
        (a / "base.md").write_text("base, edited while merging\n")
        _fixture_git(a, "add", "base.md")
        out.append(("CLEAN MERGE: one extra staged edit is NOT a verified merge",
                    verify_clean_merge(a).reason, "TREE-MISMATCH"))
        _fixture_git(a, "merge", "--abort", allow_fail=True)
        out.append(("CLEAN MERGE: with no merge in progress there is nothing to verify",
                    verify_clean_merge(a).reason, "NO-MERGE-IN-PROGRESS"))

        # ---- B: THE LAUNDERING PATH. A real conflict, resolved by hand and STAGED. -------------
        b = tmp / "laundered"
        b.mkdir()
        _fixture_git(b, "init", "-q", "-b", "main", ".")
        (b / "rows.md").write_text("| BEN-131 | base |\n")
        _fixture_git(b, "add", "-A"); _fixture_git(b, "commit", "-q", "-m", "base")
        _fixture_git(b, "checkout", "-q", "-b", "side")
        (b / "rows.md").write_text("| BEN-131 | SIDE |\n")
        _fixture_git(b, "add", "-A"); _fixture_git(b, "commit", "-q", "-m", "side")
        _fixture_git(b, "checkout", "-q", "main")
        (b / "rows.md").write_text("| BEN-131 | MAIN |\n")
        _fixture_git(b, "add", "-A"); _fixture_git(b, "commit", "-q", "-m", "main")
        _fixture_git(b, "merge", "--no-ff", "--no-commit", "side", allow_fail=True)
        out.append(("LAUNDERING: while unresolved, the cause named is the unmerged index",
                    verify_clean_merge(b).reason, "UNMERGED-ENTRIES-PRESENT"))
        (b / "rows.md").write_text("| BEN-131 | HAND-RESOLVED |\n")
        _fixture_git(b, "add", "rows.md")
        out.append(("LAUNDERING: git itself now reports NO unmerged files (the premise)",
                    _fixture_git(b, "diff", "--name-only", "--diff-filter=U"), ""))
        v = verify_clean_merge(b)
        out.append(("LAUNDERING: a hand-resolved, STAGED conflict is still REFUSED",
                    (v.ok, v.reason), (False, "RECONSTRUCTION-CONFLICTED")))
        out.append(("LAUNDERING: and it is refused while the index is clean, not because it is not",
                    v.unmerged, 0))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


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
            print("CANNOT CHECK :: this merge COULD NOT BE VERIFIED as a clean merge -- the "
                  "reason above names the condition that did not hold, and an INABILITY to check "
                  "is one of them.")
            print("  Remove the cause and re-run the guard. A clean index or an authorization "
                  "does not convert this refusal into a pass.")
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
