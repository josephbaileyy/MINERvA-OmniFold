"""Controls for s5p_robust_labels (A7 and A7-VS rulings): the kappa = 3 family keeps the process-shift variants and
replaces F +- 2 delta_M1 by F +- 3 delta_M1; a primary rejection is 'robust' only if the full kappa = 3 Holm re-run
also rejects it, 'not robust' otherwise; every non-rejection 'not applicable'; the leaves must reproduce the frozen
evaluator's decisions before they are used; the frozen boolean and the keep-both labels are kept as diagnostics; the
label file never overwrites and never touches the evaluator output. One test runs the real evaluator."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402
import s5p_robust_labels as rl  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
STAGE1 = REPO / "docs/orchestration/state/s5p/stage1/stage1_inspect.json"
S5C = REPO / "docs/orchestration/state/s5c/contract.json"
B = 1999


def leaf(k):
    return {"p": (k + 1) / (B + 1), "k": k, "B": B}


def var(kt, ks):
    return {"total": leaf(kt), "shape": leaf(ks)}


def null_entry(shift_k, m1_k=None, k3=None):
    """shift_k: {c-name: (kt, ks)}; m1_k / k3: {'+': (kt, ks), '-': ...} or None (no M1)."""
    e = {"variants": {n: var(*k) for n, k in shift_k.items()}, "robustness_variants": {}}
    if m1_k is not None:
        e["m1_shift"] = {"kappa": 2, "kappa_robust": 3, "path": "x"}
        e["variants"].update({f"m1{s}2": var(*k) for s, k in m1_k.items()})
        e["robustness_variants"] = {f"m1{s}3": var(*k) for s, k in k3.items()}
    for s in rl.SIDES:  # as s5p_joint.test_null writes them
        e[s] = max(e["variants"].values(), key=lambda v: v[s]["p"])[s]
        e[s + "_robust"] = max([e[s]] + [r[s] for r in e["robustness_variants"].values()], key=lambda v: v["p"])
    return e


def evaluator_like(tests):
    """A result with the frozen evaluator's own decision fields computed from the entries (s5p_joint.main)."""
    res = {"tests": tests}
    claims, robust = {}, {}
    for n, e in tests.items():
        for s in rl.SIDES:
            one = {"p": 1.0, "k": 0, "B": 0}
            claims[f"{n}:{s}"] = one if "not_calibrated" in e else {kk: e[s][kk] for kk in ("p", "k", "B")}
            robust[f"{n}:{s}"] = one if "not_calibrated" in e else {kk: e[s + "_robust"][kk] for kk in ("p", "k", "B")}
    res["decisions"] = si.holm_determined(claims, 0.05)
    res["decisions_robust_kappa"] = si.holm_determined(robust, 0.05)
    res["robust_to_the_sub_fine_residual"] = {t: res["decisions"][t]["decision"] == res["decisions_robust_kappa"][t]["decision"]
                                              for t in res["decisions"]}
    return res


C = {"0.0": (0, 900), "0.5": (0, 900), "1.0": (0, 900)}


class Labels(unittest.TestCase):
    def test_each_branch(self):
        d = lambda **kw: {k: {"decision": v} for k, v in kw.items()}  # noqa: E731
        out = rl.labels(d(a="rejected", b="rejected", c="rejected", e="undetermined", f="not rejected"),
                        d(a="rejected", b="undetermined", c="not rejected", e="rejected", f="rejected"))
        self.assertEqual(out, {"a": rl.ROBUST, "b": rl.NOT_ROBUST, "c": rl.NOT_ROBUST, "e": rl.NA, "f": rl.NA})

    def test_mismatched_test_sets_are_refused(self):
        with self.assertRaises(SystemExit):
            rl.labels({"a": {"decision": "rejected"}}, {"b": {"decision": "rejected"}})


class Families(unittest.TestCase):
    def test_replace_drops_the_kappa2_members_and_keeps_the_shift_variants(self):
        # m1+2 is the claim argmax (k = 5); the kappa = 3 members are k = 1; replace = max(c S k = 0, m1+-3 k = 1) = 1
        e = null_entry(C, {"+": (5, 900), "-": (0, 900)}, {"+": (1, 900), "-": (0, 900)})
        fam = rl.families(evaluator_like({"G": e}))
        self.assertEqual(fam["G:total"]["primary"]["k"], 5)
        self.assertEqual(fam["G:total"]["keep_both"]["k"], 5)  # the frozen set keeps m1+2
        self.assertEqual(fam["G:total"]["replace"]["k"], 1)
        self.assertEqual(fam["G:total"]["members"], ["0.0", "0.5", "1.0", "m1+3", "m1-3"])

    def test_a_shift_variant_can_be_the_replace_argmax(self):
        e = null_entry({"0.0": (0, 900), "0.5": (7, 900), "1.0": (3, 900)}, {"+": (2, 900), "-": (0, 900)},
                       {"+": (4, 900), "-": (0, 900)})
        self.assertEqual(rl.families(evaluator_like({"G": e}))["G:total"]["replace"]["k"], 7)

    def test_no_m1_null_replace_equals_the_claim(self):
        fam = rl.families(evaluator_like({"MnvTune_v1": null_entry(C)}))
        self.assertEqual(fam["MnvTune_v1:shape"]["replace"], fam["MnvTune_v1:shape"]["primary"])

    def test_keep_both_and_replace_labels_differ(self):
        # X: claim k = 0 (rejected at kappa 2), kappa = 3 leaf k = 20 (95% CP [0.0061, 0.0154]).
        # Y: claim argmax is its m1+2 leaf (k = 40: undetermined at kappa 2); its kappa = 3 leaves are k = 0.
        # keep-both keeps Y at k = 40, so X is first in the step-down at 0.05/4 = 0.0125: undetermined -> not robust.
        # replace drops Y to k = 0, so X moves to step 3 at 0.025: rejected -> robust.
        tests = {"X": null_entry({"0.0": (0, 0)}, {"+": (0, 0), "-": (0, 0)}, {"+": (20, 20), "-": (0, 0)}),
                 "Y": null_entry({"0.0": (0, 0)}, {"+": (40, 40), "-": (0, 0)}, {"+": (0, 0), "-": (0, 0)})}
        res = evaluator_like(tests)
        self.assertEqual(res["decisions"]["X:total"]["decision"], "rejected")
        out = rl.derive(res, 0.05)
        self.assertEqual(out["labels"]["X:total"], rl.ROBUST)
        self.assertEqual(out["diagnostics"]["keep_both"]["labels"]["X:total"], rl.NOT_ROBUST)
        self.assertEqual(out["labels"]["Y:total"], rl.NA)  # a primary non-rejection, even though rejected at kappa 3
        self.assertFalse(out["diagnostics"]["frozen_boolean_robust_to_the_sub_fine_residual"]["X:total"])

    def test_step_down_difference_between_keep_both_and_replace(self):
        # X is rejected at kappa 2. Y's claim argmax is its m1+2 leaf (k = 40, not rejected at kappa 2); under
        # keep-both Y stays at k = 40, under replace Y drops to its kappa = 3 leaves (k = 0). The ordering of the
        # step-down changes, so X's threshold changes between the two kappa = 3 runs.
        tests = {"X": null_entry({"0.0": (0, 0)}, {"+": (0, 0), "-": (0, 0)}, {"+": (3, 3), "-": (0, 0)}),
                 "Y": null_entry({"0.0": (0, 0)}, {"+": (40, 40), "-": (0, 0)}, {"+": (0, 0), "-": (0, 0)})}
        res = evaluator_like(tests)
        out = rl.derive(res, 0.05)
        keep, rep = res["decisions_robust_kappa"], out["decisions_kappa3_replace"]
        self.assertNotEqual(keep["X:total"]["threshold"], rep["X:total"]["threshold"])
        self.assertEqual(rep["Y:total"]["k"], 0)
        self.assertEqual(keep["Y:total"]["k"], 40)

    def test_budget_b0_null_is_not_applicable_and_p_one(self):
        res = evaluator_like({"G": null_entry(C), "N": {"not_calibrated": "B = 0 at the stop"}})
        out = rl.derive(res, 0.05)
        self.assertEqual(out["labels"]["N:total"], rl.NA)
        self.assertEqual(out["decisions_kappa3_replace"]["N:total"]["B"], 0)


class Guards(unittest.TestCase):
    def test_a_tampered_leaf_is_refused(self):
        res = evaluator_like({"G": null_entry(C, {"+": (0, 900), "-": (0, 900)}, {"+": (1, 900), "-": (0, 900)})})
        bad = copy.deepcopy(res)
        bad["tests"]["G"]["variants"]["m1+2"]["total"] = leaf(600)  # the claim would no longer reproduce decisions
        with self.assertRaises(SystemExit):
            rl.derive(bad, 0.05)
        bad = copy.deepcopy(res)
        bad["tests"]["G"]["robustness_variants"]["m1+3"]["total"] = leaf(600)  # keep-both no longer reproduces
        with self.assertRaises(SystemExit):
            rl.derive(bad, 0.05)
        rl.derive(res, 0.05)  # and silent on the untampered result

    def test_variants_not_matching_the_declared_m1_are_refused(self):
        res = evaluator_like({"G": null_entry(C, {"+": (0, 0), "-": (0, 0)}, {"+": (0, 0), "-": (0, 0)})})
        res["tests"]["G"]["m1_shift"]["kappa_robust"] = 4
        with self.assertRaises(SystemExit):
            rl.families(res)

    def test_cli_design_check_separate_file_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            design = t / "design.json"
            design.write_text(json.dumps({"alpha_family": 0.05}))
            res = evaluator_like({"G": null_entry(C, {"+": (0, 0), "-": (0, 0)}, {"+": (0, 0), "-": (0, 0)})})
            res["design_sha256"] = hashlib.sha256(design.read_bytes()).hexdigest()
            ev = t / "joint-evaluate.json"
            ev.write_text(json.dumps(res))
            before = ev.read_bytes()
            out = t / "labels.json"
            self.assertEqual(rl.main(["--evaluate", str(ev), "--design", str(design), "--out", str(out)]), 0)
            self.assertEqual(ev.read_bytes(), before)
            got = json.loads(out.read_text())
            self.assertEqual(got["schema"], "s5p-robust-labels/2")
            self.assertEqual(got["diagnostics"]["frozen_boolean_robust_to_the_sub_fine_residual"],
                             res["robust_to_the_sub_fine_residual"])
            with self.assertRaises(SystemExit):
                rl.main(["--evaluate", str(ev), "--design", str(design), "--out", str(out)])
            other = t / "other.json"
            other.write_text(json.dumps({"alpha_family": 0.05, "x": 1}))
            with self.assertRaises(SystemExit):
                rl.main(["--evaluate", str(ev), "--design", str(other), "--out", str(t / "o2.json")])


def product(path, x, seed=None):
    np.savez_compressed(path, xsec_flat=x, meta=json.dumps({"pseudo_seed": seed, "nuisance_draw": None}))


class RealEvaluator(unittest.TestCase):
    def test_on_s5p_joint_evaluate_output(self):
        """The leaves and field names are those the frozen evaluator writes (process shift and M1 on one null)."""
        rng = np.random.default_rng(5)
        U, names, _ = sj.j_matrix(json.loads(STAGE1.read_text()),
                                  json.loads(S5C.read_text())["measurement"]["partition_J"]["supported_cells"])
        n = U.shape[1]
        x0 = rng.uniform(0.5, 1.5, n) * 1e-39
        noise = lambda: x0 * (1 + 0.03 * rng.normal(size=n))  # noqa: E731
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for sub in ("v", "cal_ok", "cal_bad", "none", "lat"):
                (d / sub).mkdir()
            for i in range(40):
                product(d / "v" / f"v_s{i:04d}.npz", noise(), seed=1000 + i)
            for i in range(60):
                product(d / "cal_ok" / f"c_s{i:04d}.npz", noise(), seed=2000 + i)
                product(d / "cal_bad" / f"c_s{i:04d}.npz", 1.1 * noise(), seed=3000 + i)
            product(d / "lat" / "b0.npz", x0 * 0.999)
            product(d / "lat" / "b1.npz", x0 * 1.001)
            for i in range(3):
                product(d / "lat" / f"j{i}.npz", x0 * (1 + 1e-4 * rng.normal(size=n)))
            product(d / "data.npz", noise())
            np.savez(d / "pred0.npz", xsec_flat=x0, sumw2_flat=(0.001 * x0) ** 2)
            np.savez(d / "pred1.npz", xsec_flat=x0 * 1.1, sumw2_flat=(0.001 * x0) ** 2)
            np.savez(d / "D.npz", D_J=0.02 * (U @ x0), d_pairs=np.array([0.02 * (U @ x0)] * 4))
            np.savez(d / "M1.npz", D_J=0.03 * (U @ x0))
            dg = lambda p: {"path": str(p), "sha256": sj.sha256(p)}  # noqa: E731
            design = {"stage1": str(STAGE1), "s5c_contract": str(S5C), "alpha_family": 0.05,
                      "lateral_endpoints": {"B": [str(d / "lat/b0.npz"), str(d / "lat/b1.npz")]},
                      "data_jitters": [str(d / f"lat/j{i}.npz") for i in range(3)], "data_central": str(d / "data.npz"),
                      "v_ensemble_glob": str(d / "v/*.npz"), "v_ensemble_n": 40, "shift_coefficients": [0.0, 0.5, 1.0],
                      "process_shift": {"MnvTune_v1": {**dg(d / "D.npz"), "mode": "raw"}, "G": {**dg(d / "D.npz"), "mode": "raw"},
                                        "N": {"none": "fixture"}},
                      "m1_shift": {"MnvTune_v1": {"none": "rho = 1"}, "G": {**dg(d / "M1.npz"), "kappa": 2, "kappa_robust": 3},
                                   "N": {"none": "fixture"}},
                      "nulls": {"MnvTune_v1": {"prediction": str(d / "pred0.npz"), "calibration_glob": str(d / "cal_ok/*.npz"),
                                               "calibration_n": 60, "surrogate_seed0": 10},
                                "G": {"prediction": str(d / "pred1.npz"), "calibration_glob": str(d / "cal_bad/*.npz"),
                                      "calibration_n": 60, "surrogate_seed0": 20},
                                "N": {"prediction": str(d / "pred0.npz"), "calibration_glob": str(d / "none/*.npz"),
                                      "calibration_n": 0, "surrogate_seed0": 30}}}
            (d / "design.json").write_text(json.dumps(design))
            self.assertEqual(sj.main(["build-v", "--design", str(d / "design.json"), "--out", str(d / "V.npz")]), 0)
            self.assertEqual(sj.main(["evaluate", "--design", str(d / "design.json"), "--v", str(d / "V.npz"),
                                      "--out", str(d / "res.json")]), 0)
            self.assertEqual(rl.main(["--evaluate", str(d / "res.json"), "--design", str(d / "design.json"),
                                      "--out", str(d / "labels.json")]), 0)  # the leaves reproduce the evaluator
            res = json.loads((d / "res.json").read_text())
            got = json.loads((d / "labels.json").read_text())
        self.assertEqual(set(got["labels"]), set(res["decisions"]))
        self.assertEqual(got["family_members"]["G:total"], ["0.0", "0.5", "1.0", "m1+3", "m1-3"])
        self.assertEqual(got["family_members"]["MnvTune_v1:total"], ["0.0", "0.5", "1.0"])
        self.assertEqual(got["family_members"]["N:total"], [])
        for t, d_ in res["decisions"].items():
            if d_["decision"] != "rejected":
                self.assertEqual(got["labels"][t], rl.NA)
        rep = {t: max([res["tests"]["G"]["variants"][m][t.split(":")[1]]["p"] for m in ("0.0", "0.5", "1.0")] +
                      [res["tests"]["G"]["robustness_variants"][m][t.split(":")[1]]["p"] for m in ("m1+3", "m1-3")])
               for t in ("G:total", "G:shape")}
        for t, p in rep.items():
            self.assertEqual(got["decisions_kappa3_replace"][t]["p"], p)


if __name__ == "__main__":
    unittest.main()
