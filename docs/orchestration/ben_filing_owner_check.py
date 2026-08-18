#!/usr/bin/env python3
"""Every filed `BEN-*` id must resolve to a LANE, not to the `(unallocated)` span.

WHY (BEN-441). `FINDINGS.md`'s block table says, of its `*(unallocated)*` row:

    "The advance is not optional bookkeeping: `docs/orchestration/test_findings_ben_blocks.py`
     fails `no overlapping blocks` if a new row is added and this one is not narrowed, so the
     executable form of the rule catches the omission that `BEN-228` had to catch by attention."

THREE THINGS ARE WRONG WITH THAT SENTENCE AND THE THIRD IS THE DANGEROUS ONE.

1. `docs/orchestration/test_findings_ben_blocks.py` HAS NEVER EXISTED. Not in the worktree, not on
   `origin/main`, and not in any branch's history -- `git log --all --diff-filter=A` over the
   pathspec returns nothing. The named check is real but lives elsewhere, as the `no overlapping
   blocks` case inside `whose_row.py --self-test`. A citation to a path that has never existed
   (`BEN-380`), pointing at a guard.

2. IT DOES NOT RUN. `.githooks/pre-commit` invokes `findings_row_lint.py --longform` and not
   `whose_row.py`, so the guard fires only when a lane remembers to run it -- which is verbatim
   what the hook's own header at `:7` says went wrong before ("`whose_row.py` ... existed and none
   ran unless a lane remembered").

3. IT CANNOT CATCH THIS OMISSION EVEN WHEN IT DOES RUN, because it compares DECLARED spans against
   each other. A lane that files into the unallocated span WITHOUT adding a block row creates no
   second span, so there is nothing to overlap. Measured on `7e8bf844`: `BEN-430` and `BEN-431` are
   filed, no block row claims `430-439`, the `*(unallocated)*` row still advertises `430-439` as
   the next free block -- and `whose_row.py --self-test` returns `SELF-TEST :: PASS`, exit 0, with
   `owner_of_ben(430)` evaluating to the literal string `(unallocated)`.

So the free-list was stale, the row saying it could not go stale was the stale row, and the guard
cited as the reason was misnamed, unwired, and blind to this shape. The next lane to derive
freeness by reading that row takes `430-439` and collides -- `BEN-080`'s `B1` in its worst form,
where "BEN-430 is filed" is true of two different findings. This lane came one command from doing
exactly that.

THE MISSING PREDICATE, AND TWO WRONG ATTEMPTS AT IT BEFORE THE RIGHT ONE -- worth recording,
because both wrong ones were plausible and one of them is the repo's live parser:

  ATTEMPT 1, reuse `whose_row.ben_blocks`: reported 30 filed ids as having NO OWNING BLOCK. All 30
  are owned. That regex captures ONE span per row, and several lanes record continuations inside
  the row they already hold ("`190-199` (EXHAUSTED), then `210-219`, continued at `220-229`").
  A LIVE DEFECT, NOT MINE: `whose_row.owner_of_ben()` returns None for BEN-210..229 and
  BEN-240..249, and None reads as "unallocated" rather than as "this parser cannot see it".
  Routed to that script's owner; deliberately NOT patched here.

  ATTEMPT 2, capture every span in a row: reported 27 ids unowned, including this lane's own
  `390-399`. Block rows QUOTE other blocks in prose -- "NOT filed into `390-399`", "Advanced from
  `390-399`, then `400-409`" -- so a warning about a span became a claim to it.

  Narrow missed real spans; wide swallowed narrated ones. THE FIX WAS TO STOP PARSING OWNERSHIP
  FROM PROSE AT ALL. Ownership is narrated; OCCUPANCY is a fact about filed rows. The predicate
  below reads only the `*(unallocated)*` row -- the one thing that must be true of it -- and asks
  whether any id has ALREADY been filed into a span it is still advertising as free. No ownership
  map, nothing inferred from narration, and it cannot be fooled by a row that mentions a block.
  This repo's own rule, arrived at the hard way: derive it, do not narrate it.

NOT WIRED INTO THE HOOK, and not by oversight. It FAILS on `7e8bf844` -- so wiring it today would
red every lane's commit over two rows none of them filed, which is the admitting rule at
`.githooks/pre-commit:11` (lane D, `OI-64`) and precisely how a hook teaches a team `--no-verify`.
It becomes hook-eligible the moment `430-439` gets a block row. That is the mediator's to write:
`f0ad77f6` filed both ids and a block is claimed by the lane that files into it.

Usage:  python3 docs/orchestration/ben_filing_owner_check.py [--findings PATH] [--quiet]
Exit:   0 every filed id has an owning lane / 2 at least one does not / 3 usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import whose_row  # noqa: E402  -- reuse the block parser rather than write a second one

OK, UNOWNED, USAGE = 0, 2, 3

# A FILED id is one that heads a ledger row: `| BEN-NNN | ...`. Ids merely MENTIONED in prose
# (cross-references, block-table narration, this docstring) are not filings and must not be
# flagged -- the whole point of the id space is that mentioning is cheap and filing is not.
FILED = re.compile(r"^\| (BEN-(\d{3})) \|")
SPAN = re.compile(r"`(\d{3})-(\d{3})`")
UNALLOCATED_ROW = re.compile(r"^>?\s*\|\s*\*?\(unallocated\)\*?\s*\|(.*)$", re.M | re.I)


def filed_ids(findings: Path) -> list[tuple[int, int]]:
    """Ids that HEAD a ledger row. An id merely mentioned in prose is not a filing."""
    out = []
    for lineno, line in enumerate(findings.read_text(errors="replace").splitlines(), 1):
        m = FILED.match(line)
        if m:
            out.append((int(m.group(2)), lineno))
    return out


def advertised_free(findings: Path) -> list[tuple[int, int]]:
    """Spans the `*(unallocated)*` row still offers as the next free blocks."""
    text = findings.read_text(errors="replace")
    cut = text.find("## Long-form findings index")
    if cut < 0:
        raise SystemExit("FATAL: no '## Long-form findings index' marker to delimit the header.")
    rows = UNALLOCATED_ROW.findall(text[:cut])
    if not rows:
        raise SystemExit("FATAL: no *(unallocated)* row in FINDINGS.md's block table. Refusing to "
                         "pass by default -- a missing free-list is not an empty one.")
    # ATTEMPT 3, and the prose problem was INSIDE the row I had narrowed to. That cell reads
    #   "`430-439`, then `440-449`, ... -- ... *Advanced from `390-399`, then `400-409`, ...*"
    # so reading every span in it re-flagged four already-owned blocks including this lane's own.
    # The ADVERTISEMENT is the leading clause; everything after the em dash is commentary about
    # blocks that are no longer free. Cut there, and fail loudly if the cut leaves nothing --
    # a parse that silently finds no free block would pass every tree forever.
    spans: set[tuple[int, int]] = set()
    for row in rows:
        advert = row.split("\u2014")[0]
        spans.update((int(lo), int(hi)) for lo, hi in SPAN.findall(advert))
    if not spans:
        raise SystemExit("FATAL: the *(unallocated)* row names no span before its first em dash. "
                         "Refusing to report PASS from a parse that found nothing to check.")
    return sorted(spans)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="No id may be filed into an advertised-free block (BEN-441).")
    ap.add_argument("--findings", type=Path,
                    default=Path(__file__).resolve().parent / "FINDINGS.md")
    ap.add_argument("--quiet", action="store_true", help="print only failures")
    args = ap.parse_args(argv)

    if not args.findings.exists():
        print(f"[ben-owner] {args.findings} not found", file=sys.stderr)
        return USAGE

    free = advertised_free(args.findings)
    ids = filed_ids(args.findings)
    clash = [(n, ln, lo, hi) for n, ln in ids for lo, hi in free if lo <= n <= hi]

    if not args.quiet:
        spans = ", ".join(f"{lo}-{hi}" for lo, hi in free)
        print(f"[ben-owner] {len(ids)} filed ids; *(unallocated)* advertises {spans}")
    for n, ln, lo, hi in clash:
        print(f"[ben-owner] COLLISION  BEN-{n} is filed at {args.findings.name}:{ln} "
              f"but `{lo}-{hi}` is still advertised as free")
    if clash:
        taken = sorted({(lo, hi) for _, _, lo, hi in clash})
        print(f"[ben-owner] FAIL {len(clash)} id(s) already filed into "
              f"{len(taken)} advertised-free block(s). The next lane to derive freeness from that "
              f"row takes an occupied block -- `BEN-080`'s two-meanings-for-one-id.")
        print("[ben-owner]      FIX: give the block a table row naming its lane, and advance the "
              "*(unallocated)* row past it, in the same commit.")
        return UNOWNED
    if not args.quiet:
        print("[ben-owner] PASS no filed id falls inside an advertised-free block")
    return OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
