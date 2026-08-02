"""J33 regression: the ND reader must FAIL CLOSED on a branch it cannot bind.

AUDIT-FINDINGS-20260731 J33, all three sub-claims confirmed and latent-not-live. The defects were
silent by construction, which is why they need a test rather than a comment:

  1. `_addr` allocated `array("d", [0.0])` and DISCARDED `TTree::SetBranchAddress`'s return code,
     so a missing branch left the buffer at its initial value -- a column of zeros. At the CV
     `w_truth` site the initial value is 1.0, which silently reproduces KNOWN_ISSUES #1 (unit MC
     weights, globally low by pot_scale).
  2. `t_td` was absent from the axis-branch validation list even though `collect_truth_denom_nd`
     binds `ax["truth"]` on it. Zeroed truth-denominator coordinates do NOT trip the
     finite-support closure gate, which compares COUNTS -- and counts are unaffected by zeroed
     coordinates. The truth denominator is the cross section's denominator.
  3. A missing SHIFTED branch in a kinematic universe silently retained the CV branch name,
     understating the lateral band rather than failing.

WHY A STUBBED ROOT. The module imports ROOT at line 45 and this suite runs off-cluster. The stub
is installed only for the import; every assertion below is about this repo's own logic, not
ROOT's. `_addr` is deliberately probed through the module attribute rather than re-implemented, so
deleting or weakening it fails here instead of silently passing.
"""
import os
import sys
import types
import unittest

_ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(_ND)


def _load_module():
    if "ROOT" not in sys.modules:
        stub = types.ModuleType("ROOT")
        stub.gROOT = types.SimpleNamespace(SetBatch=lambda *a, **k: None)
        sys.modules["ROOT"] = stub
    for p in (os.path.join(_ROOT_DIR, "2d-unfolding"), _ND):
        if p not in sys.path:
            sys.path.insert(0, p)
    import unfold_nd_omnifold_unbinned as m
    return m


m = _load_module()


class FakeTree:
    """Minimal TTree stand-in: knows which branches exist and what SetBranchAddress returns."""

    def __init__(self, branches, rc=0, name="mc_truth_denom"):
        self._branches = set(branches)
        self._rc = rc
        self._name = name
        self.bound = []

    def GetName(self):
        return self._name

    def GetBranch(self, n):
        return object() if n in self._branches else None

    def SetBranchAddress(self, n, buf):
        self.bound.append(n)
        return self._rc


class AddrFailsClosed(unittest.TestCase):
    def test_present_branch_binds(self):
        t = FakeTree({"mc_pt"})
        a = m._addr(t, "mc_pt")
        self.assertEqual(len(a), 1)
        self.assertEqual(t.bound, ["mc_pt"])

    def test_missing_branch_raises_and_names_it(self):
        t = FakeTree({"mc_pt"})
        with self.assertRaises(RuntimeError) as cm:
            m._addr(t, "MC_q3")
        msg = str(cm.exception)
        self.assertIn("MC_q3", msg)
        self.assertIn("mc_truth_denom", msg)

    def test_missing_branch_does_not_bind_a_zero_column(self):
        """The defect's actual signature: it used to RETURN a buffer of 0.0 and carry on."""
        t = FakeTree(set())
        with self.assertRaises(RuntimeError):
            m._addr(t, "anything")
        self.assertEqual(t.bound, [], "SetBranchAddress was called on a branch that is absent")

    def test_negative_setbranchaddress_status_raises(self):
        """ROOT returns negative ESetBranchAddressStatus for kMissingBranch/kMismatch. A branch can
        exist and still fail to bind on a type mismatch, which GetBranch alone cannot see."""
        t = FakeTree({"MC_q3"}, rc=-2)          # kMismatch
        with self.assertRaises(RuntimeError) as cm:
            m._addr(t, "MC_q3")
        self.assertIn("-2", str(cm.exception))

    def test_nonnegative_status_is_accepted(self):
        for rc in (0, 1, 4, 5):                  # kMatch, kMatchConversion, kVoidPtr, kNoCheck
            with self.subTest(rc=rc):
                self.assertIsNotNone(m._addr(FakeTree({"b"}, rc=rc), "b"))

    def test_none_status_is_tolerated(self):
        """Some PyROOT builds return None rather than an int; that must not be read as negative."""
        self.assertIsNotNone(m._addr(FakeTree({"b"}, rc=None), "b"))


class WeightBindingFailsClosed(unittest.TestCase):
    """The 1.0-initialized buffer is the dangerous one: a missing weight branch is KNOWN_ISSUES #1."""

    def test_missing_weight_branch_raises(self):
        from array import array
        t = FakeTree(set(), name="mc_signal_reco")
        with self.assertRaises(RuntimeError) as cm:
            m._addr_weight(t, "w_truth", array("d", [1.0]))
        msg = str(cm.exception)
        self.assertIn("w_truth", msg)
        self.assertIn("KNOWN_ISSUES #1", msg,
                      "the message must name the defect it prevents; that is why it exists")

    def test_present_weight_branch_binds_the_supplied_buffer(self):
        from array import array
        buf = array("d", [1.0])
        t = FakeTree({"w_truth"})
        self.assertIs(m._addr_weight(t, "w_truth", buf), buf)

    def test_negative_status_raises(self):
        from array import array
        with self.assertRaises(RuntimeError):
            m._addr_weight(FakeTree({"w_truth"}, rc=-5), "w_truth", array("d", [1.0]))


class SourceLevelInvariants(unittest.TestCase):
    """J33.2 and J33.3 live inside functions that need a real ROOT file to reach, so they are
    pinned at the source level. Weaker than execution, and better than nothing -- the failure mode
    is a future edit quietly restoring the silent fallback."""

    @classmethod
    def setUpClass(cls):
        cls.src = open(os.path.join(_ND, "unfold_nd_omnifold_unbinned.py")).read()

    def test_truth_denominator_tree_is_axis_validated(self):
        """J33.2: `t_td` was absent from the validation list while collect_truth_denom_nd bound
        ax["truth"] on it unchecked."""
        self.assertIn('(t_td, ax["truth"])', self.src,
                      "the truth-denominator tree is no longer axis-validated; zeroed coordinates "
                      "there rescale every reported bin and the closure gate compares only counts")

    def test_no_silent_cv_fallback_on_a_missing_shifted_branch(self):
        """J33.3: the three swap sites must not reduce to `if GetBranch(x): use(x)`, which keeps
        the CV branch and understates the lateral band."""
        for bad in ('if t.GetBranch(nm):\n                        ax_truth[k] = nm',
                    'if t.GetBranch(nm):\n                        ax_bkg[k] = nm',
                    'if t.GetBranch(nt):\n                        ax_truth[k] = nt',
                    'if t.GetBranch(nr):\n                        ax_reco[k] = nr'):
                self.assertNotIn(bad, self.src,
                                 "a silent CV fallback on a missing shifted branch is back")

    def test_shifted_branch_sites_fail_closed(self):
        """All three swap sites -- truth-denominator, signal (truth+reco), background -- must
        refuse. Counted by the phrase that states the CONSEQUENCE rather than by "Re-run the event
        loop", which is line-wrapped at one site and so is not a countable literal."""
        self.assertEqual(
            self.src.count("understate this lateral band"), 3,
            "expected exactly one fail-closed message per shifted-branch swap site "
            "(mc_truth_denom, signal, background)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
