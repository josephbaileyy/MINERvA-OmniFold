#!/usr/bin/env python3
"""`z_null_bridge` -- it TRANSCRIBES the null's operands and refuses to manufacture them.

ROOT is not importable in this environment, so `read_throw_operands` (the only part that needs it)
is exercised through its OUTPUT CONTRACT: every test below drives `validate` and `bridge` over the
arrays and recorded scalars that function returns. That is stated rather than left implicit --
the ROOT read itself is covered by the campaign's own preflight, not here.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
if str(ND) not in sys.path:
    sys.path.insert(0, str(ND))

import z_contract as zc            # noqa: E402
import z_null_bridge as znb        # noqa: E402
import z_receipt as zrec           # noqa: E402

IDENT = {"revision": "abc123", "import_closure_digests": {"z_null_bridge.py": "d" * 64}}


def operands(n_grid=40, n_support=12, jitter=0.0, mask_override=None):
    x = np.zeros(n_grid)
    x[np.linspace(0, n_grid - 1, n_support).astype(int)] = np.linspace(1.0, 2.0, n_support)
    x2 = x.copy()
    if jitter:
        x2[x > 0] += jitter * x[x > 0]
    mask = (x > 0).astype(float) if mask_override is None else np.asarray(mask_override, float)
    arrays = {"x_cv": x, "x_cv2": x2, "producer_mask": mask}
    recorded = {"n_cv_executions": 2, "n_cv_bins_total": n_grid,
                "n_cv_support": int((x > 0).sum()),
                "n_cv_genuine_zero": int((x == 0).sum()),
                "cv_support_predicate": "x cv > 0".replace(" cv", "_cv")}
    return arrays, recorded


class ItValidatesRatherThanBelieves(unittest.TestCase):
    def test_honest_operands_validate(self):
        v = znb.validate(*operands())
        self.assertEqual(v["n_support"], 12)
        self.assertEqual(v["n_grid"], 40)
        self.assertTrue(np.array_equal(v["mask"], v["x_cv"] > 0))

    def test_ONE_execution_is_not_a_null(self):
        a, r = operands()
        r["n_cv_executions"] = 1
        with self.assertRaises(zc.ZContractError) as cm:
            znb.validate(a, r)
        self.assertIn("one is not a null", str(cm.exception))

    def test_a_DIFFERENT_predicate_is_refused(self):
        a, r = operands()
        r["cv_support_predicate"] = "x_cv >= 0"
        with self.assertRaises(zc.ZContractError):
            znb.validate(a, r)

    def test_the_support_is_RECONSTRUCTED_and_a_disagreement_refuses(self):
        """§3.3 condition 11b: the producer's mask is checked, not adopted."""
        a, r = operands()
        bad = (a["x_cv"] > 0).astype(float)
        idx = np.flatnonzero(bad)[0]
        bad[idx] = 0.0                       # producer drops one supported bin
        a["producer_mask"] = bad
        with self.assertRaises(zc.ZContractError) as cm:
            znb.validate(a, r)
        self.assertIn("11b exists to catch exactly this", str(cm.exception))

    def test_a_recorded_count_the_arrays_do_not_reproduce_refuses(self):
        for field in ("n_cv_bins_total", "n_cv_support", "n_cv_genuine_zero"):
            a, r = operands()
            r[field] = int(r[field]) + 1
            with self.assertRaises(zc.ZContractError) as cm:
                znb.validate(a, r)
            self.assertIn(field, str(cm.exception))

    def test_a_non_finite_execution_refuses(self):
        a, r = operands()
        a["x_cv2"] = a["x_cv2"].copy()
        a["x_cv2"][0] = np.nan
        with self.assertRaises(zc.ZContractError):
            znb.validate(a, r)

    def test_mismatched_shapes_refuse(self):
        a, r = operands()
        a["x_cv2"] = a["x_cv2"][:-1]
        with self.assertRaises(zc.ZContractError):
            znb.validate(a, r)


class ItWritesASlabThatZBuildCanRead(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)

    def _bridge(self, tag="a", **kw):
        a, r = operands(**kw)
        with mock.patch.object(znb, "read_throw_operands", return_value=(a, r)):
            src = self.d / f"throw-{tag}.root"
            src.write_bytes(b"synthetic stand-in; the ROOT read is mocked")
            return znb.bridge(src, self.d / f"null-{tag}.npz", code_identity=IDENT)

    def test_the_slab_round_trips_through_the_production_loader(self):
        rec = self._bridge(tag="rt", jitter=1e-13)
        x1, x2, mask = zrec.load_null_operands(self.d / "null-rt.npz")
        self.assertEqual(int(mask.sum()), 12)
        self.assertTrue(np.all(np.isfinite(x1)) and np.all(np.isfinite(x2)))

    def test_it_reports_r_null_as_a_MEASUREMENT_and_grades_nothing(self):
        rec = self._bridge(jitter=1e-13)
        r = rec["reconstructed_null"]["r_null"]
        self.assertGreater(r, 0.0)
        self.assertAlmostEqual(r / 1e-13, 1.0, places=3,
                               msg="a proportional jitter of j gives r_null ~ j")
        self.assertIn("grades_nothing", rec)
        self.assertNotIn("verdict", rec)
        self.assertNotIn("scientific_acceptance", rec)

    def test_r_null_SCALES_with_the_perturbation(self):
        """The ratio is the jitter ratio -- and the jitters are chosen ABOVE the float64 floor.

        At `1e-13` the ratio comes out `10.0017`, not `10`, because `x + 1e-13*x` is only ~450
        eps from `x` and the difference loses its low bits. That is a property of the arithmetic,
        not of this function, so the scaling is asserted where it is clean rather than with a
        tolerance wide enough to hide a real error.
        """
        a = self._bridge(tag="s1", jitter=1e-6)["reconstructed_null"]["r_null"]
        b = self._bridge(tag="s2", jitter=1e-5)["reconstructed_null"]["r_null"]
        self.assertGreater(a, 0.0)
        self.assertAlmostEqual(b / a, 10.0, places=6)

    def test_an_IDENTICAL_pair_gives_exactly_zero_and_is_still_recorded(self):
        rec = self._bridge(jitter=0.0)
        self.assertEqual(rec["reconstructed_null"]["r_null"], 0.0)

    def test_it_refuses_to_overwrite_an_existing_slab(self):
        self._bridge(tag="dup")
        with self.assertRaises(zc.ZContractError) as cm:
            self._bridge(tag="dup")
        self.assertIn("written once", str(cm.exception))

    def test_the_record_binds_the_source_by_digest(self):
        rec = self._bridge(tag="dig")
        self.assertEqual(rec["source"]["sha256"],
                         zrec.sha256_file(self.d / "throw-dig.root"))
        self.assertEqual(rec["bridge_status"], "TRANSCRIBED")

    def test_it_never_recomputes_a_CV(self):
        """SPEC 3.6d item 5: a separately produced denominator presumes what the null tests."""
        src = (ND / "z_null_bridge.py").read_text(encoding="utf-8")
        code = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
        for forbidden in ("_xsec_for_weights", "unfold", "estimator_seed"):
            self.assertNotIn(forbidden, code,
                             f"{forbidden!r} in the bridge would mean it PRODUCES an operand")


class TheROOTReadIsTheOnlyPartThatNeedsROOT(unittest.TestCase):
    def test_the_import_is_function_local(self):
        """A module-level `import ROOT` would make every guard above unreachable off-cluster --
        the campaign's own catalogued defect, seven instances."""
        src = (ND / "z_null_bridge.py").read_text(encoding="utf-8")
        head = src.split("def read_throw_operands", 1)[0]
        self.assertNotIn("import ROOT", head)
        self.assertIn("    import ROOT", src)


if __name__ == "__main__":
    unittest.main()
