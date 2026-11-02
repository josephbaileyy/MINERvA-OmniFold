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

    def assert_records(self, inputs, got, k, labels):
        """Every quoted field, recomputed from _single on the fixture (the audit's review of connect 34)."""
        cv = mc._cv_arrays(inputs, self.bkg)[k]
        single = {x: mc._single(inputs, self.bkg, self.bank_cv, x, self.weights(x), self.flux)[0][k] for x in self.SMALL}

        def r(x, row):
            return abs(single[x][row] / cv[row]) if cv[row] != 0 else abs(single[x][row])

        v = got["arrays"][k]
        recs = v["rows"]
        self.assertTrue(recs)
        first, second, pairs, truths, band_r = {}, {}, {}, {}, {}
        for rec in recs:
            row = rec["row"]
            self.assertEqual(rec["a_cv"], float(cv[row]))
            want = sorted(((r(x, row), x) for x in self.draws[rec["draw_index"]]), reverse=True)
            self.assertEqual([x for _, x in want[:na.TOP]], [x for x, _ in rec["top"]], row)
            for (wr, _), (_, gr) in zip(want, rec["top"]):
                self.assertAlmostEqual(gr, wr, places=12)
            self.assertEqual(rec["n_universes_r_gt_1"], sum(y > 1 for y, _ in want))
            self.assertEqual((rec["truth"], rec["seed"]), labels[rec["draw_index"]])
            b1, b2 = na.band(want[0][1]), na.band(want[1][1])
            first[b1] = first.get(b1, 0) + 1
            second[b2] = second.get(b2, 0) + 1
            pairs[f"{b1}+{b2}"] = pairs.get(f"{b1}+{b2}", 0) + 1
            truths[rec["truth"]] = truths.get(rec["truth"], 0) + 1
            for x in self.SMALL:
                band_r.setdefault(na.band(x), []).append(r(x, row))
        self.assertEqual(v["largest_r_band"], first)
        self.assertEqual(v["second_r_band"], second)
        self.assertLessEqual(len(pairs), 10)                # so the top 10 is every pair
        self.assertEqual(v["top_pairs"], pairs)
        self.assertEqual(v["worst_truth"], truths)
        a = np.abs(np.array([rec["a_cv"] for rec in recs]))
        self.assertEqual(v["a_cv_abs_rows_above"], na.quantiles(a[a > 0]))
        self.assertEqual(v["rows_above_cv_zero"], int(np.sum(a == 0)))
        want_b = {b: {"max": max(x), "rows_gt_10": sum(y > 10 for y in x), "rows_gt_2": sum(y > 2 for y in x)}
                  for b, x in sorted(band_r.items()) if max(x) > 1}
        self.assertEqual(set(v["band_max_r_on_rows_above"]), set(want_b))
        for b, w in want_b.items():
            g = v["band_max_r_on_rows_above"][b]
            self.assertAlmostEqual(g["max"], w["max"], places=12)
            self.assertEqual((g["rows_gt_10"], g["rows_gt_2"]), (w["rows_gt_10"], w["rows_gt_2"]), b)
        nzv = cv[cv != 0]
        self.assertEqual(v["a_cv_abs_all_nonzero_rows"], na.quantiles(np.abs(nzv)))

    def test_every_record_field_recomputed(self):
        _, got = self.both(self.inputs, 0.5)
        labels = [(None, d) for d in range(len(self.draws))]
        for k, v in got["arrays"].items():
            if v.get("rows"):
                self.assert_records(self.inputs, got, k, labels)

    def test_every_record_field_recomputed_cv_zero(self):
        wt = np.array(self.inputs["w_truth"], float)
        wt[100:110] = 0.0
        inputs = dict(self.inputs, w_truth=wt)
        _, got = self.both(inputs, 2.5)
        self.assert_records(inputs, got, "wt", [(None, d) for d in range(len(self.draws))])

    def test_declared_draws_a_strict_subset(self):
        """The fixture's 12 draws are every combination, so every candidate row is a row above. With fewer declared
        draws some candidates fall below the bound, and the quoted |a_CV| and band fields must cover the rows above
        only."""
        self.draws = self.draws[:3]
        _, got = self.both(self.inputs, 1.05)              # near the fixture's composites, so the subset matters
        fewer = [k for k, v in got["arrays"].items()
                 if v.get("rows") and v["declared"]["rows_above"] < v["all_draws_rows_above"]]
        self.assertTrue(fewer)
        for k in fewer:
            self.assert_records(self.inputs, got, k, [(None, d) for d in range(len(self.draws))])

    def test_900_draws_carry_the_declared_labels(self):
        """With 900 draws the records are labelled by draw_labels(). The first 600 repeat one draw and the last 300
        cycle the fixture's 12, so a row whose worst draw is another one is labelled with the plug-in's seeds."""
        self.draws = [self.draws[0]] * 600 + [self.draws[d % len(self.draws)] for d in range(300)]
        _, got = self.both(self.inputs, 0.5)
        labels = na.draw_labels()
        seen = set()
        for k, v in got["arrays"].items():
            if v.get("rows"):
                self.assert_records(self.inputs, got, k, labels)
                seen |= {rec["truth"] for rec in v["rows"]}
        self.assertEqual(seen, {"g18", "plugin"})

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
