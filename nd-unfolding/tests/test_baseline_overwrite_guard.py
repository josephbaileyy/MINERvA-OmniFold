#!/usr/bin/env python3
"""The BASELINE OVERWRITE GUARD in `run_p4_unfold_std.sh`, tested in the direction it acts.

WHAT IT DEFENDS, and it is a live hazard rather than a hypothetical one. `validate_endpoint_receipt`
compares the producing driver's committed blob STRICTLY, and
`nd-unfolding/unfold_nd_omnifold_unbinned.py` changed after the ten adopted endpoint unfolds were
produced on 2026-08-08. Measured on the cluster at the deployed HEAD `32e403b8`:

    RECEIPT-REJECT :: receipt BeamAngleX_0 unfold_blob dc74c38f... != committed 662951e0...:
                      the unfold driver changed since this endpoint was produced

So all ten receipts of the adopted covariance `3d7465f6…`'s own inputs read STALE, and before this
guard the launcher fell straight through to the re-unfold and `mv -f`'d over them, exiting 0.

⚠ THE GUARD IS EXECUTED HERE, NOT DESCRIBED. The block is extracted VERBATIM from the launcher
between its markers and run by bash against the real `lib_member_resume.sh`. A test that re-typed
the condition would be a second implementation of the rule and could agree with itself while
disagreeing with the file that ships (the repo's own recurring finding). The extraction asserts it
found the block, so deleting or renaming the guard makes these tests fail loudly rather than
silently pass over an absent block.

FOUR DIRECTIONS, because a one-directional check waves the hazard through:
  * baseline + existing ROOT + stale receipt   -> REFUSE (rc 9)      <- fires
  * member namespace (offset declared)         -> allow             <- must NOT fire
  * baseline + no existing ROOT                -> allow             <- first production
  * baseline + explicit P4_ALLOW_BASELINE_REUNFOLD=1 -> allow       <- the named escape
"""
import os
import pathlib
import subprocess
import unittest

ND = pathlib.Path(__file__).resolve().parent.parent
LAUNCHER = ND / "run_p4_unfold_std.sh"
START = "# ⚠ BASELINE OVERWRITE GUARD"
# the first line after the block; the guard ends at the `fi` before it
END = "# REPAIR-6: the LEGACY-ATTEST path is DELETED"


def extract_guard():
    text = LAUNCHER.read_text()
    i = text.find(START)
    j = text.find(END, i + 1)
    assert i != -1, f"{START!r} not found in {LAUNCHER} -- the guard was removed or renamed"
    assert j != -1, f"{END!r} not found after the guard -- the extraction anchor has gone stale"
    block = text[i:j]
    assert "P4_ALLOW_BASELINE_REUNFOLD" in block, "extracted block does not contain the escape hatch"
    assert "mr_declared" in block, "extracted block does not consult the member axis"
    assert "return 9" in block, "extracted block does not refuse with the documented code"
    assert 'rm -f "${REC}"' in block, (
        "the extracted region no longer contains the stale-receipt removal -- either it moved back "
        "above the guard (the defect) or the END anchor has gone stale")
    assert block.index("return 9") < block.index('rm -f "${REC}"'), (
        "the stale-receipt removal precedes the refusal: a refused baseline run would delete the "
        "ten adopted receipts before being stopped, so the guard would prevent the overwrite and "
        "not the damage")
    return block


class TheGuardIsTheOneThatShips(unittest.TestCase):
    def test_the_block_is_extractable_and_is_the_real_one(self):
        """If this fails, every other test here is testing nothing."""
        b = extract_guard()
        self.assertIn('[[ -s "${OUT}" ]]', b)
        self.assertIn("3d7465f6", b, "the refusal must name the adopted digest it protects")


class TheGuardFiresAndStaysSilentInTheRightPlaces(unittest.TestCase):
    """Runs the extracted block as the body of a function, exactly as the launcher does."""

    def _run(self, *, out_exists, offset=None, allow=None):
        guard = extract_guard()
        tmp = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / f"bog_{os.getpid()}"
        tmp.mkdir(parents=True, exist_ok=True)
        out = tmp / ("endpoint.root" if out_exists else "absent.root")
        rec = pathlib.Path(str(out) + ".done")
        rec.unlink(missing_ok=True)
        if out_exists:
            out.write_text("not empty")            # `-s` requires nonempty, not merely present
            rec.write_text('{"tag":"BeamAngleX_0"}')   # the stale receipt the guard must preserve
        script = tmp / "drive.sh"
        script.write_text(
            "#!/bin/bash\n"
            f'source "{ND}/lib_member_resume.sh"\n'
            "mr_require_valid_offset\n"
            f'OUT="{out}"\n'
            'REC="${OUT}.done"\n'
            'tag="BeamAngleX_0"\n'
            'RCHK="receipt BeamAngleX_0 unfold_blob dc74c38f != committed 662951e0"\n'
            "guarded(){\n" + guard + "\n  echo ALLOWED\n  return 0\n}\n"
            "guarded\n"
        )
        env = dict(os.environ)
        env.pop("MNV_EST_SEED_OFFSET", None)
        env.pop("P4_ALLOW_BASELINE_REUNFOLD", None)
        if offset is not None:
            env["MNV_EST_SEED_OFFSET"] = str(offset)
        if allow is not None:
            env["P4_ALLOW_BASELINE_REUNFOLD"] = str(allow)
        r = subprocess.run(["bash", str(script)], capture_output=True, text=True, env=env)
        r.receipt_survived = rec.exists()          # type: ignore[attr-defined]
        return r

    def test_BASELINE_with_an_existing_ROOT_is_REFUSED(self):
        r = self._run(out_exists=True)
        self.assertEqual(r.returncode, 9, f"expected refusal rc=9; got {r.returncode}\n{r.stderr}")
        self.assertNotIn("ALLOWED", r.stdout)
        self.assertIn("would OVERWRITE", r.stderr)
        self.assertIn("3d7465f6", r.stderr, "the refusal must say which product it is protecting")
        self.assertIn("dc74c38f", r.stderr, "the refusal must quote why the receipt was rejected")
        self.assertTrue(r.receipt_survived,
                        "the refusal deleted the receipt: a run that is stopped must leave the "
                        "baseline exactly as it found it, ROOTs AND receipts")

    def test_a_MEMBER_run_is_NOT_refused(self):
        """The whole point of the member axis: a member writes to its own namespace, where
        nothing is adopted, so re-unfolding there is the normal case and must not be blocked."""
        r = self._run(out_exists=True, offset=1200)
        self.assertEqual(r.returncode, 0, f"member run was refused: {r.stderr}")
        self.assertIn("ALLOWED", r.stdout)
        # and the stale receipt IS cleared once production is allowed -- D2's rule is preserved,
        # only reordered, so this asserts the move did not quietly drop it
        self.assertFalse(r.receipt_survived,
                         "an allowed re-production left the stale receipt in place; D2 requires "
                         "never leaving a stale ROOT/receipt pair behind")

    def test_a_FIRST_production_with_no_existing_ROOT_is_NOT_refused(self):
        r = self._run(out_exists=False)
        self.assertEqual(r.returncode, 0, f"first production was refused: {r.stderr}")
        self.assertIn("ALLOWED", r.stdout)

    def test_the_named_escape_hatch_works_and_ONLY_on_the_exact_value(self):
        r = self._run(out_exists=True, allow=1)
        self.assertEqual(r.returncode, 0, f"escape hatch did not release the guard: {r.stderr}")
        self.assertIn("ALLOWED", r.stdout)
        # A near-miss must NOT release it: an escape that accepts "yes"/"true"/"0" is one a
        # careless export can trip, which is the property that makes it useless as a deliberate act.
        for near in ("0", "yes", "true", "", "2"):
            with self.subTest(value=near):
                rr = self._run(out_exists=True, allow=near)
                self.assertEqual(rr.returncode, 9,
                                 f"P4_ALLOW_BASELINE_REUNFOLD={near!r} released the guard")


if __name__ == "__main__":
    unittest.main()
