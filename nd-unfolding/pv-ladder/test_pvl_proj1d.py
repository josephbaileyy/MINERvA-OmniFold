"""Controls for the post-hoc 1D-projection addendum: run with `python3 -m unittest test_pvl_proj1d -v` from this
directory. Each check is run silent on the committed readout and then against a planted defect."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import pvl_lib as L
import pvl_proj1d as P

HERE = Path(__file__).resolve().parent
READOUT = json.loads((HERE / "readouts" / "proj1d.json").read_text())
NPZ_SHA = L.load_json(HERE / "config.json")["rungs"]["L-5D-PV"]["npz"]["sha256"]


def failing(rungs):
    return {r: [k for k, v in c["max_abs_deviation"].items() if v > c["bound"][k]] for r, c in P.checks(rungs).items()}


class Checks(unittest.TestCase):
    def setUp(self):
        self.rungs = copy.deepcopy(READOUT["rungs"])

    def test_silent_on_the_committed_readout(self):
        self.assertEqual(failing(self.rungs), {"L-EW": [], "L-5D-PV": []})
        self.assertEqual(P.checks(self.rungs), READOUT["checks"])

    def test_closure_truth_against_npz_departure(self):
        self.rungs["L-5D-PV"]["W"]["closure_nuwro"]["dc"][0] += 1e-5
        self.assertEqual(failing(self.rungs)["L-5D-PV"], ["closure_truth_equals_npz_departure"])

    def test_tune_v1_closure_within_the_recorded_floor(self):
        floor = L.load_json(HERE / "readouts" / "L-EW_e.json")["controls"]["PC"]["closure_floor"]["max"]
        self.rungs["L-EW"]["pz"]["closure_nuwro"]["control_b_tune_v1"][3] = 2 * floor
        self.assertEqual(failing(self.rungs)["L-EW"], ["tune_v1_closure_bias"])

    def test_ew_shift_reproduces_the_readout(self):
        self.rungs["L-5D-PV"]["EW"]["vertices"]["gibuu"]["s"][7] += 1e-9
        self.assertEqual(failing(self.rungs)["L-5D-PV"], ["ew_shift_reproduces_readout"])

    def test_ew_departure_reproduces_departure_json(self):
        self.rungs["L-EW"]["EW"]["vertices"]["genie_mec"]["d"][0] += 1e-9
        self.assertEqual(failing(self.rungs)["L-EW"], ["ew_departure_reproduces_departure_json"])

    def test_cell_list_mismatch_refuses(self):
        self.rungs["L-EW"]["EW"]["cells"] = self.rungs["L-EW"]["EW"]["cells"][::-1]
        with self.assertRaises(SystemExit):
            P.checks(self.rungs)


class Summary(unittest.TestCase):
    def test_committed_summary_is_its_rungs(self):
        """To 1e-12 relative: the readout was written on another host, whose BLAS sums in another order."""
        for rung, rec in READOUT["rungs"].items():
            got, want = P.summary(rec), READOUT["summary"][rung]
            self.assertEqual(got.keys(), want.keys())
            for axis in want:
                for k in want[axis]:
                    for m, x in want[axis][k].items():
                        self.assertAlmostEqual(got[axis][k][m], x, delta=1e-12 * max(1.0, abs(x)))

    def test_leak_is_the_slope(self):
        rng = np.random.default_rng(3)
        d = rng.normal(0, 0.1, 30)
        self.assertAlmostEqual(P.leak(0.3 * d, d), 0.3)
        self.assertAlmostEqual(P.leak(d, d), 1.0)
        self.assertAlmostEqual(P.leak(np.zeros(30), d), 0.0)

    def test_closure_leak_sign(self):
        dc = np.array([0.1, -0.2, 0.05])
        rec = {"a": {"vertices": {v: {"s": [0.0] * 3, "d": dc.tolist()} for v in P.VERTICES},
                     "closure_nuwro": {"b": (-0.25 * dc).tolist(), "dc": dc.tolist()}}}
        self.assertAlmostEqual(P.summary(rec)["a"]["closure_nuwro"]["leak"], 0.25)

    def test_projection_keeps_the_total(self):
        x = np.random.default_rng(4).uniform(size=int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5])))
        for axis in L.AXES5 + ("EW",):
            self.assertAlmostEqual(P.project(x, axis).sum(), x.sum(), places=6)
        self.assertEqual(P.project(x, "W").shape, (len(L.FINE["W"]) - 1,))


class InputPins(unittest.TestCase):
    """verify_inputs on a planted tree: silent when every digest matches, refusing on a changed byte."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.products, self.ratios = self.tmp / "products", self.tmp / "ratios"
        self.products.mkdir()
        rec, prep = [], []
        for rung in P.RUNGS:
            for t in P.TASKS:
                f = self.products / f"{rung}_e_{t}.npz"
                f.write_bytes(f"{rung}{t}".encode())
                rec.append(f"{L.sha256_path(f)}  products/{f.name}")
            (self.ratios / rung).mkdir(parents=True)
            for v in P.VERTICES:
                f = self.ratios / rung / f"{v}.json"
                f.write_text(json.dumps({"rung": rung, "v": v}))
                prep.append(f"{L.sha256_path(f)}  ./ratios/{rung}/{v}.json")
        self.receipts, self.prep = self.tmp / "SHA256SUMS", self.tmp / "prep-SHA256SUMS"
        self.receipts.write_text("\n".join(rec) + "\n")
        self.prep.write_text("\n".join(prep) + "\n")

    def run_verify(self, expect=NPZ_SHA):
        P.verify_inputs(self.products, self.ratios, None, expect, receipts=self.receipts, prep_sums=self.prep)

    def test_silent_when_pinned(self):
        self.run_verify()

    def test_refuses_a_perturbed_product(self):
        f = self.products / "L-5D-PV_e_closure_nuwro.npz"
        f.write_bytes(f.read_bytes() + b"\0")
        with self.assertRaises(SystemExit):
            self.run_verify()

    def test_refuses_a_perturbed_ratio(self):
        (self.ratios / "L-EW" / "gibuu.json").write_text("{}")
        with self.assertRaises(SystemExit):
            self.run_verify()

    def test_refuses_another_npz(self):
        with self.assertRaises(SystemExit):
            self.run_verify(expect="0" * 64)

    def test_committed_receipts_list_every_product(self):
        sums = P.read_sums(P.RECEIPTS)
        for rung in P.RUNGS:
            for t in P.TASKS:
                self.assertIn(f"products/{rung}_e_{t}.npz", sums)


if __name__ == "__main__":
    unittest.main()
