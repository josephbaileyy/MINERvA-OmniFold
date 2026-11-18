#!/usr/bin/env python3
"""Tests of rdx_read.py (RDX-DECLARATION.md §4), on synthetic products; each guard in the direction it acts and in
the other. The cell integrals are the identity on 16-cell arrays (the fine grid is 16 cells here), so every reading is
set by hand."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rdx_read as R  # noqa: E402

SPEC = R.tasks()
PINS = dict(R.sums(R.SUMS))
PINS["ratio"] = R.sums(R.PVL_SUMS)[R.RATIO_KEY]
PHI = np.full(16, 0.001)
SIGMA = np.full(16, 0.02)
IDENT = lambda x: np.asarray(x, float)  # noqa: E731
BASE = np.linspace(1.0, 2.5, 16)
FINE = (16,)
PRODUCER = json.loads((HERE.parents[1] / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e2/receipts/sweep-a1/e2a1_probe.out.json").read_text())["metas"]["tune_v1"]
EST_PARAMS = PRODUCER["estimator_params"]          # the committed pvl-unfold record: the same producer, rung and seed
REFINE_PARAMS = PRODUCER["refinement"]["classifier_params"]
DECL = HERE.parents[1] / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/redump-f12i-20261112/RDX-DECLARATION.md"


def record(k: int, cell_bias=None) -> dict:
    return {"iteration": k, "n_masked": 100, "rel_bias": 0.0, "rel_rms": 0.05,
            "cell_bias": [0.0] * 16 if cell_bias is None else cell_bias,
            "acceptance_edges": [i / 10 for i in range(11)], "acceptance_decile_rel_bias": [0.0] * 10}


def meta_for(task: str) -> dict:
    s = SPEC[task]
    lat = s["inputs"] == "lat_zero"
    wide = s["features"] == "wide"
    instrumented = wide or s["weight"] != "none" or s["transfer"]
    rdx = {"regressor_features": s["features"], "regressor_weight": s["weight"], "truth": s["truth"],
           "transfer": s["transfer"], "truthx_permute": s["permute"],
           "truthx_sidecar_sha256": PINS["truthx_RDX_ALL.npz"] if wide else None, "fit_calls": None}
    if instrumented:
        rdx.update(fit_calls=R.ITERS, predict_calls=R.ITERS, rows=1000,
                   weight_sums=[10.0] * R.ITERS if s["weight"] != "none" else None)
    if s["transfer"]:
        rdx["transfer_records"] = [record(k) for k in range(R.ITERS)]
    if s["truth"] == "a7_gibuu":
        rdx["a7_hypothesis_sha256"] = R.A7_HYPOTHESIS_SHA256
    return {"schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "features": list(R.AXES5), "closure": s["closure"],
            "ratio_sha256": PINS["ratio"], "estimator_seed": 42, "iters": 5, "threads": 32,
            "input_npz_sha256": PINS["lat_zero.npz" if lat else "lat_RDX_ALL.npz"],
            "bkg_dump_sha256": PINS["lat_zero_bkg.npz" if lat else "lat_RDX_ALL_bkg.npz"],
            "estimator_params": json.loads(json.dumps(EST_PARAMS)),
            "refinement": {"ran": not s["closure"], "classifier_params": json.loads(json.dumps(REFINE_PARAMS))}, "rdx": rdx}


def truth_for(task):
    """The family's common truth: the prior's is BASE, the A7 GiBUU hybrid's and the q3 tilt's differ from it."""
    if task in R.FAMILIES["gibuu"]:
        return BASE * 1.1
    if task in R.FAMILIES["q3"]:
        return BASE * 0.9
    return BASE.copy()


def clean_prod() -> dict:
    """Every product equal to its own truth (closures) or BASE (data), so every difference is 0."""
    out = {}
    for t in SPEC:
        xt = truth_for(t) if SPEC[t]["closure"] else None
        out[t] = (meta_for(t), xt.copy() if xt is not None else BASE.copy(), xt, np.array(FINE))
    return out


def setx(prod, task, x):
    m, _, xt, shp = prod[task]
    prod[task] = (m, np.asarray(x, float), xt, shp)


def bump(x, cells, by):
    y = np.array(x, float)
    y[list(cells)] *= 1.0 + by
    return y


def write_all(d: Path, prod: dict) -> dict:
    lines = {"S3a": ["[rdx-arms] start"], "S3b": ["[rdx-arms] start"]}
    for t, (meta, x, xt, shp) in prod.items():
        arrays = {"meta": np.array(json.dumps(meta)), "xsec_flat": x, "shape": shp}
        if xt is not None:
            arrays["xtrue_flat"] = xt
        np.savez(d / f"{t}.npz", **arrays)
        lines[SPEC[t]["job"]].append(f"{R.sha256(d / f'{t}.npz')}  /pscratch/sd/j/josephrb/rdx-20261112b/out/products/{t}.npz")
    logs = {}
    for job, ls in lines.items():
        logs[job] = d / f"rdx_{job}.out"
        logs[job].write_text("\n".join(ls) + "\n")
    return logs


def check(d: Path, logs: dict):
    return R.checked_products(d, logs, SPEC, PINS, 16, FINE)


class Guards(unittest.TestCase):
    def test_a_clean_set_is_checked_and_read(self):
        with tempfile.TemporaryDirectory() as d:
            prod, _ = check(Path(d), write_all(Path(d), clean_prod()))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")
        self.assertEqual(out["outcome"]["statement"], R.SENTENCE)

    def test_the_licensed_and_outcome_sentences_are_section_4s_characters(self):
        decl = re.sub(r"\s+", " ", DECL.read_text())
        self.assertIn(f'the licensed sentence is "{R.SENTENCE}". {R.SILENT}', decl)
        self.assertIn("E_ν", R.SENTENCE)
        self.assertIn("σ", R.SENTENCE)
        self.assertIn(R.REFIT_W2, decl)
        self.assertIn(R.SENSITIVITY, decl)

    def test_a_sha_that_is_not_the_jobs_refuses(self):
        prod = clean_prod()
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), prod)
            np.savez(Path(d) / "X1.npz", meta=np.array(json.dumps(prod["X1"][0])), xsec_flat=BASE * 1.01,
                     shape=np.array(FINE))
            with self.assertRaisesRegex(SystemExit, "X1: sha256 .* is not the .* its job printed"):
                check(Path(d), logs)

    def test_the_logs_print_each_task_once_in_its_own_jobs_log(self):
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), clean_prod())
            text = logs["S3b"].read_text().splitlines()
            logs["S3b"].write_text("\n".join(text[:1] + text[2:]) + "\n")
            with self.assertRaisesRegex(SystemExit, "print no sha256 for"):
                R.log_shas(logs, SPEC)
            logs["S3b"].write_text("\n".join(text + [text[1]]) + "\n")
            with self.assertRaisesRegex(SystemExit, "more than once"):
                R.log_shas(logs, SPEC)
            logs["S3b"].write_text("\n".join(text + ["0" * 64 + "  /x/products/extra-task.npz"]) + "\n")
            with self.assertRaisesRegex(SystemExit, "not a declared task"):
                R.log_shas(logs, SPEC)
            a = logs["S3a"].read_text().splitlines()
            logs["S3b"].write_text("\n".join(text + [a[1]]) + "\n")
            logs["S3a"].write_text("\n".join(a[:1] + a[2:]) + "\n")
            with self.assertRaisesRegex(SystemExit, "printed in S3b's log"):
                R.log_shas(logs, SPEC)

    def test_a_malformed_product_line_refuses_and_chatter_does_not(self):
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), clean_prod())
            text = logs["S3b"].read_text()
            logs["S3b"].write_text(text + "[rdx-arms] task X0t failed; see /x/logs/X0t.log\n")
            self.assertEqual(sorted(R.log_shas(logs, SPEC)), sorted(SPEC))
            logs["S3b"].write_text(text + "A" * 64 + "  /x/products/X1q.npz\n")
            with self.assertRaisesRegex(SystemExit, "malformed product line"):
                R.log_shas(logs, SPEC)

    def test_the_directory_must_hold_exactly_the_fifteen(self):
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), clean_prod())
            np.savez(Path(d) / "X9.npz", xsec_flat=BASE)
            with self.assertRaisesRegex(SystemExit, "not exactly the fifteen"):
                check(Path(d), logs)
            (Path(d) / "X9.npz").unlink()
            (Path(d) / "X1q.npz").unlink()
            with self.assertRaisesRegex(SystemExit, "not exactly the fifteen"):
                check(Path(d), logs)

    def test_the_task_table_and_manifests_are_bound_and_unique(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.tsv"
            text = R.TASKS.read_text()
            p.write_text(text)
            with self.assertRaisesRegex(SystemExit, "not the bound task table"):
                R.tasks(p, "0" * 64)
            first = next(ln for ln in text.splitlines() if ln.startswith("X0\t"))
            p.write_text(text + first + "\n")
            with self.assertRaisesRegex(SystemExit, "appears twice"):
                R.tasks(p, None)
            p.write_text(text.replace("X1q\tS3b", "X1q\tS3c"))
            with self.assertRaisesRegex(SystemExit, "is not one of"):
                R.tasks(p, None)
            p.write_text("\n".join(ln for ln in text.splitlines() if not ln.startswith("X1q\t")) + "\n")
            with self.assertRaisesRegex(SystemExit, "not §4's fifteen"):
                R.tasks(p, None)
            s = Path(d) / "sums"
            s.write_text(f"{'a' * 64}  ./x.npz\n{'b' * 64}  ./x.npz\n")
            with self.assertRaisesRegex(SystemExit, "appears twice"):
                R.sums(s)
            for text, why in ((f"{'a' * 64}  ./x.npz\n{'b' * 64}  ./sub/../x.npz\n", "not a normal relative path"),
                              (f"{'a' * 64}  ./x.npz\n{'b' * 64}  x.npz\n", "malformed manifest line"),
                              (f"{'A' * 64}  ./x.npz\n", "malformed manifest line"),
                              (f"{'a' * 63}  ./x.npz\n", "malformed manifest line"),
                              (f"{'a' * 64}  ./../x.npz\n", "not a normal relative path"),
                              (f"{'a' * 64}  ./x.npz extra\n", "malformed manifest line")):
                s.write_text(text)
                with self.assertRaisesRegex(SystemExit, why, msg=text):
                    R.sums(s)
            self.assertIn("lat_RDX_ALL.npz", R.sums(R.SUMS))
            self.assertIn(R.RATIO_KEY, R.sums(R.PVL_SUMS))
        self.assertEqual(R.sha256(R.TASKS), R.TASKS_SHA256)

    def test_a_product_that_is_not_its_declared_task_refuses(self):
        for task, key, value in (("X1w", ("rdx", "regressor_weight"), "none"), ("X1p", ("rdx", "truthx_permute"), None),
                                 ("X0_lat", ("bkg_dump_sha256",), PINS["lat_RDX_ALL_bkg.npz"]),
                                 ("X1c", ("closure",), False), ("X1", ("rdx", "truthx_sidecar_sha256"), None),
                                 ("X0t", ("rdx", "fit_calls"), None), ("X1", ("estimator_seed",), 7),
                                 ("X1q", ("rdx", "truth"), "a7_gibuu"), ("X0g", ("ratio_sha256",), "0" * 64),
                                 ("X0t", ("rdx", "predict_calls"), 0), ("X1", ("rung",), "L-4D"),
                                 ("X1", ("iters",), 4), ("X1", ("threads",), 8), ("X1", ("input_npz_sha256",), "0" * 64),
                                 ("X0g", ("rdx", "a7_hypothesis_sha256"), "0" * 64), ("X1w", ("rdx", "weight_sums"), None),
                                 ("X0", ("rdx", "fit_calls"), 5)):
            prod = clean_prod()
            m = prod[task][0]
            tgt = m["rdx"] if key[0] == "rdx" else m
            tgt[key[-1]] = value
            with tempfile.TemporaryDirectory() as d:
                logs = write_all(Path(d), prod)
                with self.assertRaisesRegex(SystemExit, f"{task}: ", msg=f"{task} {key}"):
                    check(Path(d), logs)

    def test_parameters_must_be_present_and_x0s(self):
        prod = clean_prod()
        prod["X1"][0]["estimator_params"][0]["min_child_samples"] = 21
        self.assertIn("estimator_params differ from X0's",
                      R.identity_problems(prod["X1"][0], SPEC["X1"], PINS, prod["X0"][0]))
        self.assertFalse(R.identity_problems(prod["X1p"][0], SPEC["X1p"], PINS, prod["X0"][0]))
        prod["X0"][0]["estimator_params"] = None
        self.assertIn("estimator_params are not the loop's three estimators' records",
                      R.identity_problems(prod["X0"][0], SPEC["X0"], PINS, None))
        prod = clean_prod()
        prod["X0"][0]["refinement"]["classifier_params"] = None
        self.assertIn("refinement.classifier_params is not a parameter record",
                      R.identity_problems(prod["X0"][0], SPEC["X0"], PINS, None))
        prod = clean_prod()
        prod["X1"][0]["refinement"]["classifier_params"]["min_child_samples"] = 21
        self.assertIn("refinement parameters differ from X0's",
                      R.identity_problems(prod["X1"][0], SPEC["X1"], PINS, prod["X0"][0]))

    def test_the_producers_committed_parameters_pass(self):
        for name, p in zip(("clf1", "clf2", "reg"), EST_PARAMS):
            self.assertEqual(R.params_problems(p, R.EST_FIXED, R.EST_ONLY, name), [])
        self.assertEqual(R.params_problems(REFINE_PARAMS, R.REFINE_FIXED, {}, "refine"), [])

    def test_parameters_outside_the_producers_domain_refuse(self):
        def est(k, v, which="est"):
            p = json.loads(json.dumps(EST_PARAMS[0] if which == "est" else REFINE_PARAMS))
            if v is KeyError:
                p.pop(k)
            else:
                p[k] = v
            return R.params_problems(p, R.EST_FIXED if which == "est" else R.REFINE_FIXED,
                                     R.EST_ONLY if which == "est" else {}, "p")
        for k, v in (("n_estimators", -1), ("n_estimators", 100.0), ("n_estimators", True), ("learning_rate", "0.1"),
                     ("deterministic", 1), ("num_threads", 8), ("random_state", 43), ("subsample", 1.5),
                     ("min_child_samples", -3), ("max_depth", 0), ("boosting_type", "dart"), ("reg_alpha", -0.1),
                     ("objective", "binary"), ("min_split_gain", KeyError), ("surprise", 1)):
            self.assertTrue(est(k, v), f"{k}={v!r} must refuse")
        self.assertTrue(est("n_estimators", -1, "refine"))
        self.assertTrue(est("random_state", 42, "refine"), "the refinement's seed is the estimator seed + 3")
        prod = clean_prod()
        for t in SPEC:
            for p in prod[t][0]["estimator_params"]:
                p["n_estimators"] = -1
        self.assertTrue(R.identity_problems(prod["X0"][0], SPEC["X0"], PINS, None),
                        "an invalid configuration shared by all fifteen still refuses")

    def test_scalars_have_the_producers_json_types(self):
        for task, key, value in (("X1", ("iters",), 5.0), ("X1c", ("closure",), 1), ("X1", ("estimator_seed",), 42.0),
                                 ("X1t", ("rdx", "transfer"), 1), ("X1", ("rdx", "rows"), True),
                                 ("X1", ("rdx", "fit_calls"), 5.0), ("X1p", ("rdx", "truthx_permute"), 20261113.0),
                                 ("X1w", ("rdx", "weight_sums"), [10] * 5)):
            prod = clean_prod()
            m = prod[task][0]
            (m["rdx"] if key[0] == "rdx" else m)[key[-1]] = value
            self.assertTrue(R.identity_problems(m, SPEC[task], PINS, None if task == "X0" else prod["X0"][0]),
                            f"{task} {key}={value!r} must refuse")

    def test_the_transfer_records_are_the_producers(self):
        def problems(recs, task="X1t"):
            prod = clean_prod()
            prod[task][0]["rdx"]["transfer_records"] = recs
            return R.identity_problems(prod[task][0], SPEC[task], PINS, prod["X0"][0])

        good = [record(k) for k in range(5)]
        self.assertEqual(problems(good), [])
        self.assertIn("a transfer step must carry one transfer record per iteration", problems(good[:4]))
        self.assertIn("the transfer records' iterations are not the integers 0..4 in order", problems([record(0)] * 5))
        self.assertIn("the transfer records' iterations are not the integers 0..4 in order", problems(good[::-1]))
        bad = [record(k) for k in range(5)]
        bad[4]["cell_bias"] = [0.0]
        self.assertTrue(any("cell_bias" in p for p in problems(bad)))
        bad[4]["cell_bias"] = [float("nan")] * 16
        self.assertTrue(any("cell_bias" in p for p in problems(bad)))
        bad[4]["cell_bias"] = [None] + [0.0] * 15
        self.assertEqual(problems(bad), [])
        bad[4].pop("rel_rms")
        self.assertIn("a transfer record does not have summarize's fields", problems(bad))
        floats = [record(k) for k in range(5)]
        floats[4]["iteration"] = 4.0
        self.assertIn("the transfer records' iterations are not the integers 0..4 in order", problems(floats))
        for field, value, why in (("n_masked", True, "n_masked"), ("rel_rms", -1.0, "rel_rms"),
                                  ("acceptance_edges", [1.0 - i / 10 for i in range(11)], "not increasing"),
                                  ("acceptance_edges", [0.5] * 11, "not increasing")):
            recs = [record(k) for k in range(5)]
            recs[2][field] = value
            self.assertTrue(any(why in p for p in problems(recs)), f"{field}={value!r}")
        lone = [record(k) for k in range(5)]
        lone[2].update(n_masked=True, cell_bias=[0.0] + [None] * 15, acceptance_decile_rel_bias=[None] * 10)
        self.assertIn("iteration 2: n_masked, rel_bias or rel_rms is not valid", problems(lone),
                      "a bool n_masked refuses even where one masked row would populate what is reported")
        tied = [record(k) for k in range(5)]
        tied[2]["acceptance_edges"] = [0.0, 0.1, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.assertEqual(problems(tied), [], "numpy.quantile can repeat an edge on tied acceptances")
        prod = clean_prod()
        prod["X1"][0]["rdx"]["transfer_records"] = good
        self.assertIn("a step without the transfer diagnostic carries transfer records",
                      R.identity_problems(prod["X1"][0], SPEC["X1"], PINS, prod["X0"][0]))

    def test_a_repeated_archive_member_or_json_key_refuses(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "X1.npz"
            meta = meta_for("X1")
            np.savez(p, meta=np.array(json.dumps(meta)), xsec_flat=BASE, shape=np.array(FINE))
            self.assertEqual(len(R.load(p)), 4)
            q = Path(d) / "extra.npy"
            np.save(q, np.full(16, np.nan))
            with zipfile.ZipFile(p, "a") as zf, self.assertWarns(UserWarning):
                zf.write(q, "xsec_flat.npy")
            with self.assertRaisesRegex(SystemExit, "repeats a member"):
                R.load(p)
            text = json.dumps(meta)
            dup = text[:-1] + ', "iters": -1}'
            np.savez(p, meta=np.array(dup), xsec_flat=BASE, shape=np.array(FINE))
            with self.assertRaisesRegex(SystemExit, "repeats the key 'iters'"):
                R.load(p)
            nested = text.replace('"rdx": {', '"rdx": {"truth": "q3", ', 1)
            np.savez(p, meta=np.array(nested), xsec_flat=BASE, shape=np.array(FINE))
            with self.assertRaisesRegex(SystemExit, "repeats the key 'truth'"):
                R.load(p)

    def test_the_transfer_counts_are_consistent(self):
        prod = clean_prod()
        m1 = prod["X1t"][0]
        self.assertEqual(R.identity_problems(m1, SPEC["X1t"], PINS, prod["X0"][0]), [])
        self.assertEqual(R.transfer_cross_problems(m1["rdx"], prod["X0t"][0]["rdx"]), [])
        m1["rdx"]["transfer_records"][-1]["n_masked"] = 1001
        self.assertTrue(any("exceeds rdx.rows" in p for p in R.identity_problems(m1, SPEC["X1t"], PINS, prod["X0"][0])))
        m1["rdx"]["transfer_records"][-1]["n_masked"] = 1
        self.assertTrue(any("cannot populate" in p for p in R.identity_problems(m1, SPEC["X1t"], PINS, prod["X0"][0])))
        m1["rdx"]["transfer_records"][-1]["n_masked"] = 101
        self.assertEqual(R.identity_problems(m1, SPEC["X1t"], PINS, prod["X0"][0]), [])
        self.assertTrue(any("under the same mask" in p for p in R.transfer_cross_problems(m1["rdx"], prod["X0t"][0]["rdx"])))
        m1["rdx"]["transfer_records"][-1]["n_masked"] = 100
        m1["rdx"]["rows"] = 999
        self.assertTrue(any("rdx.rows" in p for p in R.transfer_cross_problems(m1["rdx"], prod["X0t"][0]["rdx"])))
        prod = clean_prod()
        prod["X1t"][0]["rdx"]["transfer_records"][2]["n_masked"] = 101
        with tempfile.TemporaryDirectory() as d:
            logs = write_all(Path(d), prod)
            with self.assertRaisesRegex(SystemExit, "X1t/X0t: .*under the same mask"):
                check(Path(d), logs)

    def test_product_arrays_must_be_the_fine_grids(self):
        for mutate, why in ((lambda p: setx(p, "X1", BASE[:15]), "xsec_flat is"),
                            (lambda p: setx(p, "X1", np.where(np.arange(16) == 3, np.nan, BASE)), "non-finite"),
                            (lambda p: p.__setitem__("X1", (p["X1"][0], BASE.astype(np.float32), None, p["X1"][3])),
                             "xsec_flat is"),
                            (lambda p: p.__setitem__("X1", (p["X1"][0], BASE, None, np.array([4, 4]))), "shape"),
                            (lambda p: p.__setitem__("X1", (p["X1"][0], BASE, None, np.array([FINE]))), "shape"),
                            (lambda p: p.__setitem__("X1", (p["X1"][0], BASE, BASE.copy(), p["X1"][3])), "exactly by the closures"),
                            (lambda p: p.__setitem__("X1c", (p["X1c"][0], BASE, None, p["X1c"][3])), "exactly by the closures")):
            prod = clean_prod()
            mutate(prod)
            with tempfile.TemporaryDirectory() as d:
                logs = write_all(Path(d), prod)
                with self.assertRaisesRegex(SystemExit, why):
                    check(Path(d), logs)

    def test_nc_x_is_bitwise_on_xsec_flat_and_shape(self):
        prod = clean_prod()
        setx(prod, "X0_lat", np.nextafter(BASE, 3.0))
        with self.assertRaisesRegex(SystemExit, "NC-X"):
            R.read(prod, IDENT, PHI, SIGMA)
        z = BASE.copy()
        z[0] = 0.0
        prod = clean_prod()
        setx(prod, "X0", z)
        setx(prod, "X0_lat", np.where(np.arange(16) == 0, -0.0, z))
        with self.assertRaisesRegex(SystemExit, "NC-X"):
            R.read(prod, IDENT, PHI, SIGMA)
        prod = clean_prod()
        prod["X0_lat"] = (prod["X0_lat"][0], prod["X0_lat"][1], None, np.array(FINE, dtype=np.int32))
        prod["X0"] = (prod["X0"][0], prod["X0"][1], None, np.array(FINE, dtype=np.int64))
        with self.assertRaisesRegex(SystemExit, "NC-X"):
            R.read(prod, IDENT, PHI, SIGMA)

    def test_a_closure_familys_truths_must_agree(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1g"]
        prod["X1g"] = (m, x, bump(xt, [9], 0.02), shp)
        with self.assertRaisesRegex(SystemExit, "gibuu closure family's truth references differ"):
            R.read(prod, IDENT, PHI, SIGMA)
        prod = clean_prod()
        m, x, xt, shp = prod["X1pc"]
        prod["X1pc"] = (m, x, np.nextafter(xt, 9.0), shp)
        with self.assertRaisesRegex(SystemExit, "prior closure family's truth references differ"):
            R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(R.read(clean_prod(), IDENT, PHI, SIGMA)["outcome"]["outcome"], "LICENSED",
                         "different truths BETWEEN families are the declared design")

    def test_phi_and_sigma_are_committed_finite_and_positive(self):
        self.assertEqual(R.RR.I0.name, "i0.json")
        self.assertEqual(R.RR.F1_READOUT.name, "fd_f1_readout.json")
        self.assertEqual(R.RR.CMODEL_JSON.name, "cmodel_5d.json")
        src = Path(R.__file__).read_text()
        self.assertNotIn("--i0", src)
        self.assertNotIn("--f1-readout", src)
        for bad in (np.zeros(16), np.where(np.arange(16) == 5, np.nan, SIGMA), np.where(np.arange(16) == 5, np.inf, SIGMA),
                    np.full(1, 0.02)):
            with self.assertRaisesRegex(SystemExit, "sigma_c must be 16 finite positive values"):
                R.read(clean_prod(), IDENT, PHI, bad)
        with self.assertRaisesRegex(SystemExit, "phi_c must be 16 finite positive values"):
            R.read(clean_prod(), IDENT, np.where(np.arange(16) == 2, np.nan, PHI), SIGMA)

    def test_a_cell_integral_must_be_sixteen_finite_values(self):
        with self.assertRaisesRegex(SystemExit, "cell integral"):
            R.read(clean_prod(), lambda x: np.asarray(x, float)[:1], PHI, SIGMA)
        with self.assertRaisesRegex(SystemExit, "cell integral"):
            R.read(clean_prod(), lambda x: np.where(np.arange(16) == 0, np.inf, np.asarray(x, float)), PHI, SIGMA)

    def test_a_transfer_cell_bias_read_must_be_sixteen_values(self):
        prod = clean_prod()
        prod["X1t"][0]["rdx"]["transfer_records"][-1]["cell_bias"] = [0.0]
        with self.assertRaisesRegex(SystemExit, "cell_bias is not 16"):
            R.read(prod, IDENT, PHI, SIGMA)
        prod["X1t"][0]["rdx"]["transfer_records"][-1]["cell_bias"] = [float("nan")] * 16
        with self.assertRaisesRegex(SystemExit, "cell_bias is not 16"):
            R.read(prod, IDENT, PHI, SIGMA)


class Readings(unittest.TestCase):
    def test_the_refit_null_at_w2_makes_r1_unattributable(self):
        prod = clean_prod()
        setx(prod, "X1p", bump(BASE, [3], 0.02))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1p"]["class"], "W2")
        self.assertEqual((out["outcome"]["outcome"], out["outcome"]["cells"]), ("REFIT NULL W2", ["R03"]))

    def test_the_refit_null_takes_precedence_over_a_sensitivity(self):
        prod = clean_prod()
        setx(prod, "X1p", bump(BASE, [3], 0.02))
        setx(prod, "X1", bump(BASE, [5], 0.05))
        m, x, xt, shp = prod["X1g"]
        prod["X1g"] = (m, bump(x, [9], 0.02), xt, shp)
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["outcome"]["outcome"], "REFIT NULL W2")

    def test_an_excess_beyond_half_sigma_is_a_named_sensitivity(self):
        prod = clean_prod()
        setx(prod, "X1", bump(BASE, [5], 0.012))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1"]["cells_excess_beyond_half_sigma"], ["R05"])
        self.assertEqual(out["outcome"]["outcome"], "STATED SENSITIVITY")
        setx(prod, "X1", bump(BASE, [5], 0.009))
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["outcome"]["outcome"], "LICENSED")

    def test_an_excess_exactly_at_half_sigma_is_licensed(self):
        prod = clean_prod()
        two = np.full(16, 2.0)
        for t in ("X0", "X0_lat", "X1p", "X1w", "X1t", "X0t"):
            setx(prod, t, two)
        setx(prod, "X1", bump(two, [5], 0.125))
        sigma = np.full(16, 0.25)
        out = R.read(prod, IDENT, PHI, sigma)
        self.assertEqual(out["R1"]["excess"][5], 0.125)
        self.assertEqual(out["R1"]["cells_excess_beyond_half_sigma"], [])
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_the_excess_is_beyond_the_null(self):
        prod = clean_prod()
        setx(prod, "X1", bump(BASE, [5], 0.012))
        setx(prod, "X1p", bump(BASE, [5], 0.008))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R1p"]["class"], "W1")
        self.assertEqual(out["R1"]["cells_excess_beyond_half_sigma"], [])
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r4_reads_each_closure_against_its_familys_truth(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1g"]
        prod["X1g"] = (m, bump(x, [9], 0.02), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["gibuu"]["class"], "W2")
        self.assertEqual(out["outcome"]["cells"]["R4_gibuu"], ["R09"])
        self.assertAlmostEqual(out["R4"]["bias"]["X1g"][9], 0.02, places=12)
        self.assertEqual(out["R4"]["bias"]["X0g"][9], 0.0, "the family truth normalizes each bias")

    def test_r4_in_w1_still_licenses(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1q"]
        prod["X1q"] = (m, bump(x, [9], 0.004), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["q3"]["class"], "W1")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r4_at_the_prior_subtracts_the_refit_null(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1c"]
        prod["X1c"] = (m, bump(x, [2], 0.02), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["prior"]["class"], "W2")
        m, x, xt, shp = prod["X1pc"]
        prod["X1pc"] = (m, bump(x, [2], 0.02), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["prior"]["class"], "W0")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r4_prior_is_the_signed_residual_and_a_larger_null_flags(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1pc"]
        prod["X1pc"] = (m, bump(x, [2], 0.02), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertAlmostEqual(out["R4"]["prior"]["attributable"][2], -0.02, places=12,
                               msg="a null larger than the change leaves a signed residual")
        self.assertEqual((out["R4"]["prior"]["class"], out["R4"]["prior"]["cells"]), ("W2", ["R02"]))
        self.assertEqual(out["outcome"]["outcome"], "STATED SENSITIVITY", "conservative against licensing (J7)")
        self.assertEqual(out["outcome"]["cells"]["R4_prior"], ["R02"])
        self.assertEqual(R.RR.wr_class(out["R4"]["prior"]["attributable"], PHI, SIGMA)[0], out["R4"]["prior"]["class"],
                         "re-classing the stored vector gives the stored class")
        prod = clean_prod()
        for t, by in (("X1c", 0.012), ("X1pc", -0.012)):
            m, x, xt, shp = prod[t]
            prod[t] = (m, bump(x, [6], by), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["prior"]["class"], "W2", "a change equal and opposite to the null is flagged")

    def test_r4_q3_and_the_weight_at_the_prior(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1q"]
        prod["X1q"] = (m, bump(x, [0], 0.02), xt, shp)
        self.assertEqual(R.read(prod, IDENT, PHI, SIGMA)["outcome"]["cells"]["R4_q3"], ["R00"])
        prod = clean_prod()
        m, x, xt, shp = prod["X1wc"]
        prod["X1wc"] = (m, bump(x, [1], 0.02), xt, shp)
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R4"]["weight_at_prior"]["class"], "W2")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED", "the weight qualifies; it is not an outcome change")

    def test_the_weight_at_the_prior_is_never_silent(self):
        prod = clean_prod()
        m, x, xt, shp = prod["X1wc"]
        prod["X1wc"] = (m, bump(x, [1], 0.02), xt, shp)
        o = R.read(prod, IDENT, PHI, SIGMA)["outcome"]
        self.assertEqual(o["outcome"], "LICENSED")
        self.assertEqual(o["weight_at_prior"]["class"], "W2")
        self.assertAlmostEqual(o["weight_at_prior"]["max_abs_change_over_sigma"], 1.0, places=9)
        self.assertEqual(o["qualifier"], R.WEIGHT_CROSSES.format(cells="R01"))
        self.assertIn("more than half the reported σ in R01", o["qualifier"])
        prod = clean_prod()
        m, x, xt, shp = prod["X1wc"]
        prod["X1wc"] = (m, bump(x, [1], 0.004), xt, shp)
        o = R.read(prod, IDENT, PHI, SIGMA)["outcome"]
        self.assertEqual(o["weight_at_prior"]["class"], "W1")
        self.assertNotIn("qualifier", o, "below R2's threshold it is printed, not stated")
        setx(prod, "X1p", bump(BASE, [3], 0.02))
        m, x, xt, shp = prod["X1wc"]
        prod["X1wc"] = (m, bump(xt, [1], 0.02), xt, shp)
        o = R.read(prod, IDENT, PHI, SIGMA)["outcome"]
        self.assertEqual((o["outcome"], o["weight_at_prior"]["class"]), ("REFIT NULL W2", "W2"))
        self.assertIn("qualifier", o, "it is stated whatever the outcome")

    def test_r2_classes_x1w_against_x1_and_only_qualifies(self):
        prod = clean_prod()
        setx(prod, "X1", bump(BASE, [4], 0.009))
        setx(prod, "X1w", bump(BASE, [4], 0.009) * np.where(np.arange(16) == 4, 1.003, 1.0))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R2"]["class"], "W1", "against X1; against X0 it would be W2")
        setx(prod, "X1w", bump(BASE, [4], 0.05))
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual(out["R2"]["class"], "W2")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED")

    def test_r3_reads_the_last_iteration_and_the_difference(self):
        prod = clean_prod()
        recs = prod["X1t"][0]["rdx"]["transfer_records"]
        recs[0]["cell_bias"] = [0.5] * 16
        recs[-1]["cell_bias"] = [0.0] * 15 + [0.03]
        out = R.read(prod, IDENT, PHI, SIGMA)
        self.assertEqual((out["R3"]["X1t"]["class"], out["R3"]["X1t"]["cells_beyond_half_sigma"]), ("T2", ["R15"]))
        self.assertEqual(out["R3"]["X0t"]["class"], "T0")
        self.assertEqual(out["R3"]["difference"]["class"], "T2")
        self.assertEqual(out["outcome"]["outcome"], "LICENSED", "R3 qualifies only")
        recs[-1]["cell_bias"] = [None] + [0.0] * 15
        diff = R.read(prod, IDENT, PHI, SIGMA)["R3"]["difference"]
        self.assertEqual((diff["class"], diff["cells_beyond_half_sigma"]), ("T2", ["R00"]))

    def test_r3_reports_bitwise_whether_the_probe_left_the_loop_untouched(self):
        prod = clean_prod()
        self.assertTrue(R.read(prod, IDENT, PHI, SIGMA)["R3"]["loop_untouched"]["X1t_equals_X1_bitwise"])
        setx(prod, "X1t", np.nextafter(BASE, 3.0))
        self.assertFalse(R.read(prod, IDENT, PHI, SIGMA)["R3"]["loop_untouched"]["X1t_equals_X1_bitwise"])

    def test_a_nonpositive_reference_refuses(self):
        prod = clean_prod()
        z = BASE.copy()
        z[7] = 0.0
        setx(prod, "X0", z)
        setx(prod, "X0_lat", z.copy())
        with self.assertRaisesRegex(SystemExit, "positive reference"):
            R.read(prod, IDENT, PHI, SIGMA)


if __name__ == "__main__":
    unittest.main()
