"""n1_attrib against fd_1b_mc.composite_n1 on test_fd_1b_mc's synthetic world (run from the checkout's root):
  python3 -B -m pytest -q docs/.../stage1/attrib/test_n1_attrib.py
The repetition reproduces composite_n1's numbers exactly, ``check`` fires on a receipt that differs and is silent on
one that agrees, and each attributed row's worst composite is compose's own per-row record for that draw."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "nd-unfolding" / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import n1_attrib as na  # noqa: E402
import test_fd_1b_mc as t  # noqa: E402

mc, toys = t.mc, t.toys


class Attribution(t.Case):
    SMALL = t.N1Composite.SMALL

    def setUp(self):
        super().setUp()
        p = mock.patch.object(toys, "s1_universes", lambda: list(self.SMALL))
        p.start()
        self.addCleanup(p.stop)
        self.draws = [[a, b, c] for a in self.SMALL[:3] for b in self.SMALL[3:5] for c in self.SMALL[5:]]

    def both(self, inputs, bound):
        with mock.patch.object(mc, "N1_BOUND", bound):
            ref = mc.composite_n1(inputs, self.bkg, self.bank_cv, self.weights, self.flux, self.draws)
            got = na.attribute(inputs, self.bkg, self.bank_cv, self.weights, self.flux, self.draws)
        return ref, got

    def per_row(self, inputs, k, tags):
        """compose's |a_D| / max_j |a_uj| per row for one draw (the record composite_n1's exact pass equals)."""
        ui, ub, _ = mc.compose(inputs, self.bkg, self.bank_cv, tags, self.weights, self.flux)
        comp = {"wt": ui["w_truth"], "wr": ui["w_reco"], "bkgw": ub["bkg_w"]}[k]
        s = np.array([mc._single(inputs, self.bkg, self.bank_cv, x, self.weights(x), self.flux)[0][k] for x in tags])
        return np.abs(comp) / np.max(np.abs(s), axis=0)

    def assert_rows(self, inputs, got, k, bound):
        v = got["arrays"][k]
        self.assertEqual(len(v["rows"]), v["declared"]["rows_above"])
        for rec in v["rows"]:
            r = self.per_row(inputs, k, self.draws[rec["draw_index"]])
            self.assertAlmostEqual(rec["worst"], float(r[rec["row"]]), places=10, msg=(k, rec["row"]))
            best = max(float(self.per_row(inputs, k, d)[rec["row"]]) for d in self.draws)
            self.assertAlmostEqual(rec["worst"], best, places=10)
            self.assertGreater(rec["worst"], bound)
        self.assertEqual(sum(v["largest_r_band"].values()), v["declared"]["rows_above"])

    def test_reproduces_composite_n1_and_attributes_each_row(self):
        ref, got = self.both(self.inputs, 0.5)
        self.assertEqual(na.check(got, {"composite": ref}), [])
        fired = [k for k, v in ref["arrays"].items() if v["declared"]["rows_above"]]
        self.assertTrue(fired)
        for k in fired:
            self.assert_rows(self.inputs, got, k, 0.5)

    def test_cv_zero_rows(self):
        wt = np.array(self.inputs["w_truth"], float)
        wt[100:110] = 0.0
        inputs = dict(self.inputs, w_truth=wt)
        ref, got = self.both(inputs, 2.5)
        self.assertEqual(na.check(got, {"composite": ref}), [])
        v = got["arrays"]["wt"]
        self.assertGreater(v["declared"]["rows_above"], 0)
        self.assertEqual(v["rows_above_cv_zero"], v["declared"]["rows_above"])
        self.assertTrue(all(r["cv_zero"] and r["a_cv"] == 0.0 for r in v["rows"]))
        self.assert_rows(inputs, got, "wt", 2.5)

    def test_check_fires_on_a_differing_receipt(self):
        ref, got = self.both(self.inputs, 0.5)
        k = next(k for k, v in ref["arrays"].items() if v["declared"]["rows_above"])
        for path, val in ((("declared", "rows_above"), 10 ** 6), (("declared", "max"), 1e9),
                          (("all_draws_rows_above",), -1), (("all_draws_max",), -1.0)):
            bad = {"composite": {**ref, "arrays": {**ref["arrays"], k: {**ref["arrays"][k],
                                                                         "declared": dict(ref["arrays"][k]["declared"])}}}}
            node = bad["composite"]["arrays"][k]
            for p in path[:-1]:
                node = node[p]
            node[path[-1]] = val
            self.assertTrue(na.check(got, bad), path)
        self.assertTrue(na.check(got, {"composite": {**ref, "n_draws": 901}}))

    def test_the_declared_draw_labels(self):
        labels = na.draw_labels()
        self.assertEqual(len(labels), 900)
        self.assertEqual((labels[0], labels[299], labels[300], labels[899]),
                         (("g18", 3620000), ("g18", 3620299), ("ar23", 3630000), ("plugin", 3640299)))


if __name__ == "__main__":
    unittest.main()
