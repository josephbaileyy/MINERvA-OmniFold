"""Tests for v_half.py (DECLARATION.md section 8). Every rule clause, noise term, class precedence, control and
refusal is tested in both directions on synthetic fixtures with the inputs' schema. No real input is read.

Run from this directory: python3 -B -m unittest test_v_half
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import copy  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import contextlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v_half as vh  # noqa: E402

CELLS = vh.CELLS
LOW = CELLS[0:4] + CELLS[8:12]  # the eight p_par < 4.5 cells (Q1 and Q3)
TRUTHS = [  # name, row, group, own_vertex
    ("nominal", 1, "prior", None), ("W1", 1, "vertex-family", "nuwro"), ("W2", 1, "vertex-family", "genie_mec"),
    ("W3", 1, "vertex-family", "nuwro"), ("q3", 1, "non-vertex", None), ("stage0c_gibuu", 2, "vertex-family", "gibuu"),
    ("closure_nuwro", 3, "vertex-family", "nuwro"), ("A7_mnvtune", 4, "prior", None),
    ("A7_genie_cv", 4, "non-vertex", None), ("A7_genie_mec", 4, "vertex-family", "genie_mec"),
    ("A7_nuwro", 4, "vertex-family", "nuwro"), ("A7_gibuu", 4, "vertex-family", "gibuu"),
]
PRIORS = ("nominal", "A7_mnvtune")
H2_REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr/read/readout.json"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Fixture:
    """H1 (F0b's readout shape) and H2 (FD-PRR's readout shape) with every truth passing by a wide margin: d = 0.2
    (0 at the priors), r = 0.01, nu = 0.001, FD-PRR's own r = 0.02, and d at A7_gibuu jittered by 1e-4 over the five
    splits."""

    def __init__(self):
        self.d = {n: np.full(16, 0.0 if n in PRIORS else 0.2) for n, *_ in TRUTHS}
        self.r = {n: np.full(16, 0.01) for n, *_ in TRUTHS}
        self.nu = {n: np.full(16, 0.001) for n, *_ in TRUTHS}
        self.r_prr = {n: np.full(16, 0.02) for n, *_ in TRUTHS}
        self.jitter = 1e-4
        self.drop = set()      # truths with no H2 entry
        self.extra = []        # H1 edits applied last

    def h1(self):
        truths = []
        for n, row, group, own in TRUTHS:
            t = {"name": n, "row": row, "group": group, "own_vertex": own, "graded": True,
                 "bias": self.r[n].tolist(), "noise_sigma": self.nu[n].tolist()}
            if own == "gibuu":
                t["p_parallel_lt_4p5"] = {"cells": list(LOW)}
            truths.append(t)
        truths.append({"name": "P1r", "row": 6, "group": "vertex-family", "own_vertex": "nuwro", "graded": False,
                       "bias": [9.0] * 16, "noise_sigma": [0.0] * 16})
        h = {"cells": list(CELLS), "truths": truths}
        for fn in self.extra:
            fn(h)
        return h

    def entry(self, n, d):
        r = self.r_prr[n]
        return {"rho": None, "b": (r * (1.0 + d)).tolist(), "r": r.tolist(), "d": d.tolist()}

    def h2(self):
        table = {}
        for n, *_ in TRUTHS:
            if n not in self.drop:
                table[f"B0/{n}/s{vh.PRIMARY_SEED}"] = self.entry(n, self.d[n])
        for i, s in enumerate(vh.NOISE_SEEDS):
            if s != vh.PRIMARY_SEED:
                table[f"B0/A7_gibuu/s{s}"] = self.entry("A7_gibuu", self.d["A7_gibuu"] + self.jitter * (i - 2))
                table[f"B0/nominal/s{s}"] = self.entry("nominal", np.zeros(16))
        return {"verdict": "COMPLETE", "table": table}

    def write(self, root, h1=None, h2=None):
        root = Path(root)
        p1, p2 = root / vh.H1, root / H2_REL
        for p, obj in ((p1, h1 or self.h1()), (p2, h2 or self.h2())):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(obj))
        dd = root / vh.DECL_DIR
        dd.mkdir(parents=True, exist_ok=True)
        (dd / vh.PINS_H1).write_text(f"{sha(p1)}  {vh.H1}\n")
        (dd / vh.PINS_H2).write_text(f"{sha(p2)}  {H2_REL}\n")
        return root


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.fx = Fixture()

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, h1=None, h2=None):
        self.fx.write(self.root, h1, h2)
        out = Path(self.tmp.name) / f"out{len(list(Path(self.tmp.name).glob('out*')))}"
        with contextlib.redirect_stderr(io.StringIO()):
            rc = vh.main(["read", "--repo", str(self.root), "--out", str(out)])
        js = json.loads((out / "readout.json").read_text()) if (out / "readout.json").exists() else None
        return rc, js

    def cls(self, js, c):
        return js["readings"]["cells"][c]["class"]


class Rule(Case):
    def test_the_two_forms_agree(self):
        """REQUIRED (the director's ruling 1): |b| <= 0.5|d| with b = r(1 + d) iff |r| <= 0.5|d|/(1 + d)."""
        rng = np.random.default_rng(7)
        for r, d in zip(rng.uniform(-0.6, 0.6, 20000), rng.uniform(-0.9, 2.0, 20000)):
            p = vh.pair(float(r), 0.0, float(d), 0.0)
            if not p["applies"]:
                continue
            f2 = abs(r) <= 0.5 * abs(d) / (1.0 + d)
            self.assertEqual(p["class"] == vh.PASS, f2, (r, d))
        self.assertTrue(vh.ctl_form(self.fx_data())["pass"])

    def fx_data(self):
        return {"H1": self.fx.h1(), "H2": self.fx.h2()}

    def test_the_floor_is_inclusive_and_two_sided(self):
        self.assertTrue(vh.pair(0.0, 0.0, 0.01, 0.0)["applies"])
        self.assertTrue(vh.pair(0.0, 0.0, -0.01, 0.0)["applies"])
        self.assertFalse(vh.pair(0.0, 0.0, 0.00999, 0.0)["applies"])
        self.assertEqual(vh.pair(0.5, 0.0, 0.00999, 0.0)["class"], vh.NA)
        self.assertFalse(vh.pair(0.0, 0.0, 0.0199, 0.0, floor=0.02)["applies"])

    def test_half_is_inclusive_at_the_boundary(self):
        d = 0.2
        r = 0.5 * d / (1.0 + d)
        self.assertEqual(vh.pair(r * (1 - 1e-12), 0.0, d, 0.0)["class"], vh.PASS)
        self.assertEqual(vh.pair(r * (1 + 1e-9), 0.0, d, 0.0)["class"], vh.FAIL)
        self.assertEqual(vh.pair(0.4 * d / (1 + d), 0.0, d, 0.0)["class"], vh.PASS)
        self.assertEqual(vh.pair(0.6 * d / (1 + d), 0.0, d, 0.0)["class"], vh.FAIL)
        tie = vh.pair(0.25, 0.0, 1.0, 0.0)  # exact in binary: |b| = 0.5 = 0.5 |d|, the decision's "<=" passes
        self.assertEqual((tie["margin"], tie["sigma_m"], tie["class"]), (0.0, 0.0, vh.PASS))
        edge = vh.pair(0.125, 0.0625, 1.0, 0.0)  # m = 0.25 = 2 sigma_m exactly (sigma_m = 2 x 0.0625): lo = 0
        self.assertEqual((edge["lo"], edge["class"]), (0.0, vh.PASS))

    def test_b_carries_the_factor_one_plus_d(self):
        d, r = 1.0, 0.3  # |r| <= 0.5|d| but |r (1 + d)| = 0.6 > 0.5
        p = vh.pair(r, 0.0, d, 0.0)
        self.assertAlmostEqual(p["b"], 0.6)
        self.assertEqual(p["class"], vh.FAIL)
        self.assertEqual(vh.pair(0.2, 0.0, 1.0, 0.0)["class"], vh.PASS)

    def test_signs_enter_only_through_magnitudes(self):
        for r, d in ((0.04, 0.2), (-0.04, 0.2), (0.04, -0.2), (-0.04, -0.2)):
            self.assertEqual(vh.pair(r, 0.0, d, 0.0)["class"], vh.PASS, (r, d))
        for r, d in ((0.2, 0.2), (-0.2, 0.2), (0.2, -0.2), (-0.2, -0.2)):
            self.assertEqual(vh.pair(r, 0.0, d, 0.0)["class"], vh.FAIL, (r, d))


class Noise(Case):
    def test_a_pair_within_the_band_is_unresolved(self):
        d = 0.2
        r0 = 0.5 * d / (1.0 + d)
        self.assertEqual(vh.pair(r0 * 0.99, 0.01, d, 0.0)["class"], vh.UNRES)
        self.assertEqual(vh.pair(r0 * 1.01, 0.01, d, 0.0)["class"], vh.UNRES)
        self.assertEqual(vh.pair(r0 * 0.5, 0.001, d, 0.0)["class"], vh.PASS)
        self.assertEqual(vh.pair(r0 * 1.5, 0.001, d, 0.0)["class"], vh.FAIL)

    def test_the_band_is_k_sigma_inclusive_on_the_pass_side(self):
        d, nu = 0.2, 0.001
        sm = (1.0 + d) * nu
        r_edge = (0.5 * d - 2.0 * sm) / (1.0 + d)  # m = 2 sigma_m exactly: lo = 0, a pass
        self.assertEqual(vh.pair(r_edge * (1 - 1e-12), nu, d, 0.0)["class"], vh.PASS)
        self.assertEqual(vh.pair(r_edge * (1 + 1e-9), nu, d, 0.0)["class"], vh.UNRES)
        r_mid = (0.5 * d - 1.5 * sm) / (1.0 + d)    # 1.5 sigma: unresolved at K = 2, a pass at K = 1
        self.assertEqual(vh.pair(r_mid, nu, d, 0.0)["class"], vh.UNRES)
        self.assertEqual(vh.pair(r_mid, nu, d, 0.0, k=1.0)["class"], vh.PASS)
        self.assertEqual(vh.K, 2.0)

    def test_the_bias_noise_is_scaled_by_one_plus_d(self):
        d, nu = 1.0, 0.01  # sigma_b = (1 + d) nu = 0.02, not 0.01
        self.assertAlmostEqual(vh.pair(0.2, nu, d, 0.0)["sigma_m"], 0.02)
        r = 0.235          # m = 0.5 - 2 |r| = 0.03: inside 2 x 0.02, outside 2 x 0.01
        self.assertAlmostEqual(vh.pair(r, nu, d, 0.0)["margin"], 0.03)
        self.assertEqual(vh.pair(r, nu, d, 0.0)["class"], vh.UNRES)
        self.assertEqual(vh.pair(r, nu / 2, d, 0.0)["class"], vh.PASS)

    def test_the_departure_noise_enters_with_its_derivative(self):
        d, sd = 0.2, 0.01
        r = 0.02
        p = vh.pair(r, 0.0, d, sd)
        self.assertAlmostEqual(p["sigma_m"], abs(0.5 - abs(r)) * sd)
        r_close = (0.5 * d - 0.012) / (1.0 + d)  # m = 0.012, 2 sigma_m ~ 0.0096 at r~0.073 -> just a pass
        self.assertEqual(vh.pair(r_close, 0.0, d, sd)["class"], vh.PASS)
        self.assertEqual(vh.pair((0.5 * d - 0.005) / (1.0 + d), 0.0, d, sd)["class"], vh.UNRES)
        self.assertEqual(vh.pair((0.5 * d - 0.005) / (1.0 + d), 0.0, d, 0.0)["class"], vh.PASS)

    def test_sigma_d_is_the_five_split_sd(self):
        h2 = self.fx.h2()
        sd = vh.sigma_d(h2)
        rows = [np.asarray(h2["table"][f"B0/A7_gibuu/s{s}"]["d"]) for s in vh.NOISE_SEEDS]
        np.testing.assert_allclose(sd, np.std(np.vstack(rows), axis=0, ddof=1), rtol=1e-14)
        self.assertEqual(len(vh.NOISE_SEEDS), 5)
        self.assertIn(vh.PRIMARY_SEED, vh.NOISE_SEEDS)
        self.assertGreater(float(sd[0]), 0.0)
        self.assertAlmostEqual(float(sd[0]), float(np.std([0.2 + 1e-4 * (i - 2) if s != vh.PRIMARY_SEED else 0.2
                                                           for i, s in enumerate(vh.NOISE_SEEDS)], ddof=1)), places=15)


class Cells(Case):
    def test_all_pass_is_valid(self):
        rc, js = self.read()
        self.assertEqual(rc, 0)
        self.assertEqual({self.cls(js, c) for c in CELLS}, {vh.VALID})
        self.assertEqual(js["readings"]["counts"][vh.VALID], 16)

    def test_one_failing_truth_makes_the_cell_not_valid(self):
        self.fx.r["W2"][5] = 0.2
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R05"), vh.NOT_VALID)
        self.assertEqual(self.cls(js, "R04"), vh.VALID)

    def test_the_prior_truths_count_where_the_rule_applies(self):
        self.fx.d["A7_mnvtune"][3] = 0.05
        self.fx.r["A7_mnvtune"][3] = 0.2
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R03"), vh.NOT_VALID)
        self.assertEqual(js["readings"]["cells"]["R03"]["pairs"]["A7_mnvtune"]["class"], vh.FAIL)
        self.assertEqual(js["readings"]["cells"]["R03"]["pairs"]["nominal"]["class"], vh.NA)

    def test_a_cell_where_the_rule_applies_nowhere_is_not_valid(self):
        for n in self.fx.d:
            if n != "nominal":  # the prior's own d stays exactly 0 (C-PRR)
                self.fx.d[n][7] = 0.005
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R07"), vh.NOWHERE)
        self.assertNotEqual(self.cls(js, "R07"), vh.VALID)

    def test_a_truth_without_d_is_no_d_not_valid(self):
        self.fx.drop.add("W3")
        rc, js = self.read()
        self.assertEqual(rc, 0)
        self.assertEqual({self.cls(js, c) for c in CELLS}, {vh.NO_D})
        self.assertEqual(js["readings"]["cells"]["R00"]["pairs"]["W3"]["class"], vh.NOD)

    def test_precedence_fail_over_no_d_over_unresolved(self):
        self.fx.drop.add("W3")
        self.fx.r["W1"][0] = 0.2                       # R00: a fail and a no-d
        d = 0.2
        self.fx.r["W1"][1] = 0.5 * d / (1 + d)         # R01: an unresolved and a no-d
        self.fx.nu["W1"][1] = 0.01
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R00"), vh.NOT_VALID)
        self.assertEqual(self.cls(js, "R01"), vh.NO_D)
        self.fx.drop.clear()
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R01"), vh.UNRES)
        self.assertEqual(self.cls(js, "R00"), vh.NOT_VALID)

    def test_gibuu_is_graded_on_all_sixteen_cells_and_the_exclusion_is_print_only(self):
        self.fx.r["A7_gibuu"][6] = 0.2                 # R06 is a p_par >= 4.5 cell
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R06"), vh.NOT_VALID)
        po = js["readings"]["print_only"]
        self.assertEqual(po["gibuu_excluded_on_p_par_ge_4p5"]["R06"], vh.VALID)
        self.assertEqual(po["gibuu_excluded_on_p_par_ge_4p5"]["R00"], vh.VALID)

    def test_option_a_is_print_only_and_uses_the_prr_bias(self):
        self.fx.r_prr["q3"][9] = 0.2                   # FD-PRR's own B0 bias fails at R09; F0b's passes
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R09"), vh.VALID)
        self.assertEqual(js["readings"]["print_only"]["option_A_prr_b0_bias"]["R09"], vh.NOT_VALID)
        self.assertEqual(js["readings"]["print_only"]["option_A_prr_b0_bias"]["R08"], vh.VALID)

    def test_the_boundaries(self):
        self.fx.r["W1"][2] = 0.3 * 0.2 / 1.2           # q = 0.3 at |d| = 0.2
        self.fx.d["q3"][2] = 0.05
        self.fx.r["q3"][2] = 0.45 * 0.05 / 1.05        # q = 0.45 at |d| = 0.05
        rc, js = self.read()
        b = js["readings"]["print_only"]["boundaries"]["R02"]
        self.assertAlmostEqual(b["h_star_at_floor"], 0.45, places=12)
        self.assertTrue(b["valid_at_half_by_point"])
        floors = [s["floor_up_to"] for s in b["steps"]]
        self.assertIn(0.05, [round(f, 12) for f in floors])
        self.assertAlmostEqual(b["steps"][-1]["h_star"], 0.45, places=12)

    def test_k_sensitivity_is_print_only(self):
        d = 0.2
        self.fx.r["W2"][4] = (0.5 * d - 1.5 * 1.2 * 0.001) / (1 + d)  # 1.5 sigma_m from the boundary
        rc, js = self.read()
        self.assertEqual(self.cls(js, "R04"), vh.UNRES)
        self.assertEqual(js["readings"]["print_only"]["band_K"]["1.0"]["R04"], vh.VALID)
        self.assertEqual(js["readings"]["print_only"]["band_K"]["3.0"]["R04"], vh.UNRES)

    def test_the_licence_is_carried(self):
        rc, js = self.read()
        self.assertIn("coverage", js["licence"]["not_citable_for"])
        self.assertTrue(any("ATLAS" in s for s in js["licence"]["not_citable_for"]))


class Controls(Case):
    def stop(self, h1=None, h2=None, name=None):
        rc, js = self.read(h1, h2)
        self.assertEqual(rc, 3)
        self.assertNotIn("readings", js)
        if name:
            self.assertFalse(next(c for c in js["controls"] if c["control"] == name)["pass"], name)
        return js

    def test_clean_controls_pass(self):
        rc, js = self.read()
        self.assertEqual([c["pass"] for c in js["controls"]], [True] * 8)
        self.assertEqual([c["control"] for c in js["controls"]],
                         ["C-PIN", "C-CELLS", "C-TRUTHS", "C-PRR", "C-DOMAIN", "C-FINITE", "C-FORM", "C-HAND"])

    def test_c_pin(self):
        self.fx.write(self.root)
        p = self.root / vh.H1
        p.write_text(p.read_text() + " ")
        out = Path(self.tmp.name) / "o"
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(vh.main(["read", "--repo", str(self.root), "--out", str(out)]), 3)
        js = json.loads((out / "readout.json").read_text())
        self.assertFalse(js["controls"][0]["pass"])

    def test_c_cells(self):
        h1 = self.fx.h1()
        h1["cells"] = CELLS[::-1]
        self.stop(h1=h1, name="C-CELLS")
        h1 = self.fx.h1()
        h1["truths"][3]["noise_sigma"] = [0.0] * 15
        self.stop(h1=h1, name="C-CELLS")

    def test_c_truths(self):
        h1 = self.fx.h1()
        h1["truths"][2]["graded"] = False
        self.stop(h1=h1, name="C-TRUTHS")
        h2 = self.fx.h2()
        del h2["table"]["B0/A7_gibuu/s994003"]
        self.stop(h2=h2, name="C-TRUTHS")

    def test_c_prr(self):
        h2 = self.fx.h2()
        h2["verdict"] = "INCOMPLETE"
        self.stop(h2=h2, name="C-PRR")
        h2 = self.fx.h2()
        h2["table"][f"B0/q3/s{vh.PRIMARY_SEED}"]["d"][4] += 1e-6
        self.stop(h2=h2, name="C-PRR")
        h2 = self.fx.h2()
        h2["table"]["B0/nominal/s994002"]["d"][0] = 1e-17
        self.stop(h2=h2, name="C-PRR")

    def test_c_domain(self):
        h1 = self.fx.h1()
        next(t for t in h1["truths"] if t["name"] == "A7_gibuu")["p_parallel_lt_4p5"]["cells"] = CELLS[0:8]
        self.stop(h1=h1, name="C-DOMAIN")

    def test_c_finite(self):
        self.fx.r["W1"][0] = float("nan")
        self.stop(name="C-FINITE")
        self.fx = Fixture()
        self.fx.nu["W1"][0] = -0.001
        self.stop(name="C-FINITE")
        self.fx = Fixture()
        self.fx.d["W1"][0] = -1.0
        self.stop(name="C-FINITE")

    def test_c_hand(self):
        D = {"H1": self.fx.h1(), "H2": self.fx.h2()}
        self.assertTrue(vh.ctl_hand(D)["pass"])
        ci = CELLS.index(vh.HAND_CELL)
        D["H2"]["table"][f"B0/{vh.HAND_TRUTH}/s{vh.PRIMARY_SEED}"]["b"][ci] *= 1.01  # d no longer b/r - 1
        self.assertFalse(vh.ctl_hand(D)["pass"])
        self.assertEqual((vh.HAND_CELL, vh.HAND_TRUTH), ("R06", "A7_gibuu"))

    def test_c_form_on_the_fixture(self):
        D = {"H1": self.fx.h1(), "H2": self.fx.h2()}
        c = vh.ctl_form(D)
        self.assertTrue(c["pass"])
        self.assertEqual(c["detail"]["pairs_checked"], 10 * 16)


class Refusals(Case):
    def test_no_prr_pin_refuses(self):
        self.fx.write(self.root)
        (self.root / vh.DECL_DIR / vh.PINS_H2).unlink()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(vh.main(["read", "--repo", str(self.root), "--out", str(Path(self.tmp.name) / "o")]), 4)

    def test_an_existing_out_refuses(self):
        self.fx.write(self.root)
        o = Path(self.tmp.name) / "o"
        o.mkdir()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(vh.main(["read", "--repo", str(self.root), "--out", str(o)]), 4)

    def test_a_wrong_h1_path_refuses(self):
        self.fx.write(self.root)
        (self.root / vh.DECL_DIR / vh.PINS_H1).write_text(f"{'0' * 64}  some/other.json\n")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(vh.main(["read", "--repo", str(self.root), "--out", str(Path(self.tmp.name) / "o")]), 4)


if __name__ == "__main__":
    unittest.main()
