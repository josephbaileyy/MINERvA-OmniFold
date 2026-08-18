#!/usr/bin/env python3
"""Tests for `ben_filing_owner_check.py` (BEN-441).

The check took three attempts and the first two both LOOKED right while being wrong in opposite
directions -- one under-parsed the block table, one over-parsed it. So these tests pin the exact
distinction that survived: an advertised span is the one in the row's LEADING clause; a span named
after the em dash is commentary about a block that is no longer free, and must not be treated as
either an advertisement or a claim.

Written in both directions per this repo's rule: the collision case fires, and the several
near-miss cases that must NOT fire are pinned too, because widening this later would look free.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ben_filing_owner_check as chk

HEADER = """# FINDINGS

> | lane | block |
> |---|---|
> | C - PET | `400-409` -- self-allocated. |
{unalloc}

## Long-form findings index

| id | row |
|---|---|
{rows}
"""

UNALLOC = "> | *(unallocated)* | `430-439`, then `440-449`, ... — *Advanced from `400-409`.* |"


def build(tmp: Path, rows: str, unalloc: str = UNALLOC) -> Path:
    p = tmp / "FINDINGS.md"
    p.write_text(HEADER.format(unalloc=unalloc, rows=rows))
    return p


class CheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())

    def test_clean_tree_passes(self) -> None:
        p = build(self.tmp, "| BEN-400 | a row |\n| BEN-401 | another |")
        self.assertEqual(chk.main(["--findings", str(p)]), chk.OK)

    def test_id_filed_into_advertised_block_fails(self) -> None:
        p = build(self.tmp, "| BEN-400 | a row |\n| BEN-430 | filed into the free span |")
        self.assertEqual(chk.main(["--findings", str(p)]), chk.UNOWNED)

    def test_second_advertised_block_is_also_protected(self) -> None:
        """`440-449` is advertised too; the check must not guard only the first span."""
        p = build(self.tmp, "| BEN-445 | filed into the SECOND advertised block |")
        self.assertEqual(chk.main(["--findings", str(p)]), chk.UNOWNED)

    def test_span_named_after_the_em_dash_is_not_an_advertisement(self) -> None:
        """REGRESSION (attempt 2 and 3): `400-409` is narrated as ALREADY TAKEN, not offered."""
        p = build(self.tmp, "| BEN-400 | owned by lane C, narrated in the unallocated row |")
        self.assertEqual(chk.main(["--findings", str(p)]), chk.OK)

    def test_annotation_BEFORE_the_em_dash_is_not_an_advertisement(self) -> None:
        """REGRESSION, and it accused another lane before it was caught.

        Lane B advanced the free-list correctly and put its annotation BEFORE the em dash:
        "`490-499`, then `500-509`, ... *Advanced from `480-489` ...* -- **closed ten-blocks only**".
        The em-dash-only cut read `480-489` as still advertised and reported a collision against a
        row that was entirely correct. An emphasis marker starts narration too, so cut at whichever
        comes first.
        """
        unalloc = ("> | *(unallocated)* | `490-499`, then `500-509`, ... *Advanced from `430-439` in "
                   "the same commit as `BEN-430`.* \u2014 **closed ten-blocks only** |")
        p = build(self.tmp, "| BEN-430 | filed, and its block IS properly rowed |", unalloc=unalloc)
        self.assertEqual(chk.main(["--findings", str(p)]), chk.OK)

    def test_still_fails_when_the_leading_clause_really_is_occupied(self) -> None:
        """The direction it must still act: narrowing the cut must not blind the check."""
        unalloc = ("> | *(unallocated)* | `430-439`, then `440-449`, ... *Advanced from `420-429`.* "
                   "\u2014 **closed ten-blocks only** |")
        p = build(self.tmp, "| BEN-430 | filed into a still-advertised block |", unalloc=unalloc)
        self.assertEqual(chk.main(["--findings", str(p)]), chk.UNOWNED)

    def test_a_mentioned_id_is_not_a_filed_id(self) -> None:
        """Prose may reference BEN-430 freely; only a row HEADED by the id is a filing."""
        p = build(self.tmp, "| BEN-400 | see BEN-430 and BEN-431 for the other half |")
        self.assertEqual(chk.main(["--findings", str(p)]), chk.OK)

    def test_missing_unallocated_row_is_fatal_not_pass(self) -> None:
        """A parse that finds no free-list must not report PASS -- absence is not emptiness."""
        p = build(self.tmp, "| BEN-400 | a row |", unalloc="> | D - verifier | `250-259` |")
        with self.assertRaises(SystemExit):
            chk.main(["--findings", str(p)])

    def test_advertised_row_with_no_span_before_the_dash_is_fatal(self) -> None:
        p = build(self.tmp, "| BEN-400 | a row |",
                  unalloc="> | *(unallocated)* | none right now — see `430-439` history. |")
        with self.assertRaises(SystemExit):
            chk.main(["--findings", str(p)])

    def test_missing_index_marker_is_fatal(self) -> None:
        p = self.tmp / "FINDINGS.md"
        p.write_text("> | *(unallocated)* | `430-439` |\n| BEN-430 | row |\n")
        with self.assertRaises(SystemExit):
            chk.main(["--findings", str(p)])

    def test_missing_file_is_a_usage_error(self) -> None:
        self.assertEqual(chk.main(["--findings", str(self.tmp / "nope.md")]), chk.USAGE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
