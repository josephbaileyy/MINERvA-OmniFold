#!/usr/bin/env python3
"""RATCHET, not a functional test -- and the distinction is the point.

`p4_project_4d.py` gained an OI-129 readback (reopen the closed product, read `hRowIndex4D` back
out, require it to equal the array it was written from, digest the readback, digest the output
file). That code is **not exercised by any test here**, because `main()` needs ROOT, a parent
component manifest, real 5D/4D central products and a candidate path, and no interpreter available
in this environment has ROOT. Its companion `project_cov_nd.py` IS functionally tested, including
both failure directions, in `test_project_cov_nd_receipt.py`.

So this file does the one thing that is honest at this cost: it **ratchets** the readback against
silent removal or reversion to the in-memory digest. A ratchet proves the code is PRESENT and
SHAPED correctly. It does NOT prove the code WORKS -- only an execution with ROOT does that, and
OI-129 already assigns the owning re-verification to the standard-P4 lane. Recording the limit
here rather than letting a green suite imply coverage it does not have.

⚠ What would make this a real test: run `main()` on the cluster against a candidate and confirm the
readback FIRES when the stored histogram is perturbed. Until then the functional direction is
UNTESTED, not passing.
"""
import re
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "p4_project_4d.py"


class P4ReadbackRatchet(unittest.TestCase):
    def setUp(self):
        self.s = SRC.read_text()

    def test_output_file_is_digested(self):
        """OI-129's first half: nothing digested the covariance this script had just written."""
        self.assertIn("proj4d_sha256", self.s)
        self.assertRegex(self.s, r'"proj4d_sha256":\s*P\.sha256_file\(a\.out\)',
                         "the product digest must be of the FILE, via sha256_file(a.out)")

    def test_row_index_is_read_back_out_of_the_closed_file(self):
        """OI-129's second half: the old digest hashed the in-memory array it wrote from."""
        self.assertIn("_rows_readback", self.s)
        self.assertRegex(self.s, r'_rows_readback\s*=\s*_flat\(a\.out,\s*"hRowIndex4D"\)',
                         "the readback must come from the written FILE, not from memory")

    def test_readback_equality_is_REQUIRED_not_merely_recorded(self):
        """A digest recorded beside another digest is not a check; something must refuse."""
        self.assertRegex(self.s, r"P\.require\(\s*bool\(np\.array_equal\(_rows_readback,\s*_rows_written\)\)",
                         "equality must go through P.require, so a mismatch REFUSES")
        self.assertRegex(self.s, r"P\.require\(\s*_rows_readback\.size\s*==\s*_rows_written\.size",
                         "length must be asserted separately -- array_equal on a short read is "
                         "False but says nothing about which failure occurred")

    def test_the_readback_happens_AFTER_the_file_is_closed(self):
        """Reading before Close() would read the in-memory buffer and prove nothing."""
        close = self.s.index("fo.Close()")
        readback = self.s.index("_rows_readback")
        self.assertLess(close, readback, "the readback must follow fo.Close()")

    def test_the_old_in_memory_field_is_RETAINED(self):
        """Additive by design: consumers reading the old manifest key must not break."""
        self.assertRegex(self.s, r'"row_index_sha256":\s*P\.hashlib\.sha256\(',
                         "the pre-existing in-memory digest must survive beside the readback")

    def test_this_file_states_that_it_is_not_functional_coverage(self):
        """Guard against a future reader taking a green ratchet for a tested code path."""
        doc = sys.modules[__name__].__doc__ or ""
        self.assertIn("RATCHET", doc)
        self.assertIn("UNTESTED", doc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
