"""Controls for fd_ct_closure (FD-CT-3B-DECLARATION.md section 3), on small synthetic lateral dumps. No real dump or
product is read.

* The truth-side check refuses each key it names, one at a time, and stays silent on two dumps that differ only in
  MCreco.
* With the zero dump as both inputs, the experiment is pvl_lib.closure_inputs at r = 1, array for array; with a
  shifted dump, only the observed rows change, and they are the shifted dump's own.
* main(), with the unfold stubbed: the product and its meta, and each refusal with nothing written.
* Where LightGBM is importable (the cluster's root_6_28, in the deploy tests), a real tiny unfold: the zero-on-zero
  product is bitwise the direct pv-ladder path on pvl_lib.closure_inputs."""
import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_ct_closure as C  # noqa: E402

L, PU = C.L, C.PU
try:
    import lightgbm  # noqa: F401
    HAVE_LGBM = True
except ImportError:  # pragma: no cover
    HAVE_LGBM = False

EDGES = [np.array([0.0, 0.5, 1.0]), np.array([1.5, 3.0, 6.0]), np.array([0.0, 0.4, 2.0]),
         np.array([0.0, 1.0, 3.0]), np.array([0.0, 1.4, 4.0])]


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(path: Path, seed=0, n=600, n_data=400, shift=0.0, **override):
    """A lateral-dump-shaped npz (nn_dump_inputs' keys). shift scales MCreco's hadronic columns only."""
    rng = np.random.default_rng(seed)
    lo = np.array([e[0] for e in EDGES]); hi = np.array([e[-1] for e in EDGES])
    gen = (lo + rng.uniform(0.02, 0.98, (n, 5)) * (hi - lo)).astype(np.float32)
    reco = (gen * (1 + rng.normal(0, 0.05, (n, 5)))).astype(np.float32)
    reco[:, 2:] *= np.float32(1 + shift)
    a = {"MCgen": gen, "MCreco": reco, "measured": gen[:n_data] * np.float32(1.01),
         "pass_reco": rng.uniform(size=n) > 0.1, "pass_truth": rng.uniform(size=n) > 0.05,
         "w_truth": rng.uniform(0.5, 1.5, n), "w_reco": rng.uniform(0.5, 1.5, n),
         "measured_weights": np.ones(n_data), "denom_nd": np.full([len(e) - 1 for e in EDGES], 50.0),
         "flux": np.full(len(EDGES[0]) - 1, 2.0), "data_pot": np.array(1.0), "n_nucleons": np.array(3.0),
         "nedges": np.array(5), "axes": np.array(["eavail", "q3", "W"], dtype=object)}
    a.update({f"edges_{i}": e for i, e in enumerate(EDGES)})
    a.update(override)
    np.savez(path, **a)
    return path


def zero_and_shifted(tmp: Path, shift=0.03, **override):
    """Two dumps of the same events at the same truth: the shifted one differs only in MCreco (and, as the real
    dumps do, in measured_weights)."""
    z = dump(tmp / "lat_zero.npz")
    s = dump(tmp / "lat_shift.npz", shift=shift, measured_weights=np.full(400, 0.9), **override)
    return z, s


class Unit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct3b-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_two_dumps_that_differ_only_in_mcreco_pass(self):
        z, s = zero_and_shifted(self.tmp)
        resp, pseudo = C.s5c_unfold.load_inputs(z), C.s5c_unfold.load_inputs(s)
        self.assertFalse(np.array_equal(resp["MCreco"], pseudo["MCreco"]))
        self.assertEqual(C.truth_side_problems(resp, pseudo), [])

    def test_each_truth_side_key_is_checked(self):
        base = C.s5c_unfold.load_inputs(dump(self.tmp / "a.npz"))
        for k in C.SAME:
            other = dict(base)
            v = np.array(base[k], copy=True)
            v.flat[0] = (not v.flat[0]) if v.dtype == bool else v.flat[0] + 1   # one entry changed
            other[k] = v
            self.assertIn(k, C.truth_side_problems(base, other), k)
        other = dict(base, edges=[e.copy() for e in base["edges"]])
        other["edges"][2][1] += 0.01
        self.assertIn("edges", C.truth_side_problems(base, other))
        other = dict(base, MCreco=base["MCreco"][:-1])
        self.assertIn("MCreco shape", C.truth_side_problems(base, other))
        other = dict(base, w_truth=base["w_truth"].astype(np.float32))
        self.assertIn("w_truth", C.truth_side_problems(base, other))   # a dtype change alone

    def test_zero_on_zero_is_pvl_closure_at_unit_ratio(self):
        resp = C.s5c_unfold.load_inputs(dump(self.tmp / "z.npz"))
        exp, xt = C.mismatch_inputs(resp, resp)
        ref, xr = L.closure_inputs(resp, np.ones(resp["MCgen"].shape[0]))
        self.assertEqual(set(exp), set(ref))
        for k in ref:
            if k == "edges":
                self.assertTrue(all(np.array_equal(x, y) for x, y in zip(exp[k], ref[k])))
            else:
                np.testing.assert_array_equal(np.asarray(exp[k]), np.asarray(ref[k]), err_msg=k)
        np.testing.assert_array_equal(xt, xr)

    def test_a_shifted_pseudo_dump_changes_only_the_observed_rows(self):
        z, s = zero_and_shifted(self.tmp)
        resp, pseudo = C.s5c_unfold.load_inputs(z), C.s5c_unfold.load_inputs(s)
        exp, xt = C.mismatch_inputs(resp, pseudo)
        ref, xr = L.closure_inputs(resp, np.ones(resp["MCgen"].shape[0]))
        for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "tmpl", "tmpl_w"):
            np.testing.assert_array_equal(np.asarray(exp[k]), np.asarray(ref[k]), err_msg=k)   # the zero response
        np.testing.assert_array_equal(xt, xr)                                                 # the zero truth
        # the observed rows, rebuilt independently from the shifted dump
        reco = pseudo["MCreco"]
        keep = pseudo["pass_reco"] & pseudo["pass_truth"] & (pseudo["w_reco"] > 0)
        for k, e in enumerate(EDGES):
            keep &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
        np.testing.assert_array_equal(exp["obs"], reco[keep])
        np.testing.assert_array_equal(exp["obs_counts"], pseudo["w_reco"][keep])
        self.assertFalse(np.array_equal(exp["obs"], ref["obs"]) and exp["obs"].shape == ref["obs"].shape)
        self.assertEqual(exp["tmpl"].shape[0], 0)


class Main(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ct3b-main-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.z, self.s = zero_and_shifted(self.tmp)

    def argv(self, pseudo=None, out="closure.npz", rsha=None, psha=None, variant="proton_p1"):
        pseudo = pseudo or self.s
        return ["--variant", variant, "--response-npz", str(self.z), "--expect-response-sha256", rsha or digest(self.z),
                "--pseudo-npz", str(pseudo), "--expect-pseudo-sha256", psha or digest(pseudo),
                "--out", str(self.tmp / out)]

    def run_main(self, argv):
        """main() with the unfold stubbed: the measured side returns the observed rows and counts, and the unfold
        returns a fixed cross section, recording what it was given."""
        seen = {}

        def measured(exp, cols, seed, threads):
            seen["obs"] = exp["obs"].copy()
            return exp["obs"], exp["obs_counts"], {"ran": False, "reason": "no negative weights (signal-only reference)"}

        def unfold(d, cols, seed, threads, iters):
            seen["unf"] = {k: d[k] for k in ("MCgen", "MCreco", "measured")}
            return np.full([len(e) - 1 for e in EDGES], 7.0), [{"n_estimators": 100, "num_leaves": 8, "random_state": 42}] * 3

        err, out = io.StringIO(), io.StringIO()
        with mock.patch.object(PU, "measured_negweight", measured), mock.patch.object(PU, "unfold", unfold), \
                mock.patch("s5e_candidate.install"), contextlib.redirect_stderr(err), contextlib.redirect_stdout(out), \
                mock.patch.dict(sys.modules, {"lightgbm": mock.MagicMock(__version__="stub")}):
            rc = C.main(argv)
        self.err = err.getvalue()
        return rc, seen

    def test_the_product_and_its_meta(self):
        rc, seen = self.run_main(self.argv())
        self.assertEqual(rc, 0, self.err)
        with np.load(self.tmp / "closure.npz", allow_pickle=False) as z:
            m = json.loads(str(z["meta"]))
            self.assertEqual(z["xsec_flat"].shape, (32,))
            resp = C.s5c_unfold.load_inputs(self.z)
            np.testing.assert_array_equal(z["xtrue_flat"],
                                          L.closure_inputs(resp, np.ones(resp["MCgen"].shape[0]))[1].ravel())
        self.assertEqual((m["schema"], m["variant"], m["construction"], m["truth"], m["arm"]),
                         ("fd-ct-closure/1", "proton_p1", "mismatch-closure", "nominal", "e"))
        self.assertEqual((m["response_npz_sha256"], m["pseudo_npz_sha256"]), (digest(self.z), digest(self.s)))
        self.assertEqual(m["experiment"]["pseudo_reco_identical"], False)
        self.assertEqual((m["refinement"]["ran"], m["estimator_seed"], m["iters"]), (False, 42, 5))
        self.assertIn("fd_ct_closure.py", m["code_sha256"])
        np.testing.assert_array_equal(seen["unf"]["MCreco"], resp["MCreco"])   # the zero response is unfolded

    def test_zero_on_zero_records_identical_reco(self):
        rc, _ = self.run_main(self.argv(pseudo=self.z, variant="zero"))
        self.assertEqual(rc, 0, self.err)
        with np.load(self.tmp / "closure.npz", allow_pickle=False) as z:
            self.assertTrue(json.loads(str(z["meta"]))["experiment"]["pseudo_reco_identical"])

    def test_refuses_to_overwrite(self):
        (self.tmp / "closure.npz").write_text("x")
        rc, _ = self.run_main(self.argv())
        self.assertEqual(rc, 3)
        self.assertIn("refusing to overwrite", self.err)

    def test_refuses_a_digest_that_is_not_expected(self):
        rc, _ = self.run_main(self.argv(psha="0" * 64))
        self.assertEqual(rc, 4)
        self.assertIn("input digests", self.err)
        self.assertFalse((self.tmp / "closure.npz").exists())

    def test_refuses_dumps_of_another_truth(self):
        other = dump(self.tmp / "lat_other.npz", shift=0.03, w_truth=np.full(600, 1.1))
        rc, _ = self.run_main(self.argv(pseudo=other))
        self.assertEqual(rc, 4)
        self.assertIn("refusing: the two dumps differ in ['w_truth']", self.err)
        self.assertFalse((self.tmp / "closure.npz").exists())

    def test_refuses_another_axis_set(self):
        other = dump(self.tmp / "lat_axes.npz", shift=0.03, axes=np.array(["eavail", "W", "q3"], dtype=object))
        rc, _ = self.run_main(self.argv(pseudo=other))
        self.assertEqual(rc, 4)
        self.assertIn("axes", self.err)
        self.assertFalse((self.tmp / "closure.npz").exists())


@unittest.skipUnless(HAVE_LGBM, "LightGBM is not importable here; this runs in the cluster deploy tests")
class RealUnfold(unittest.TestCase):
    def test_zero_on_zero_is_bitwise_the_direct_pv_ladder_path(self):
        tmp = Path(tempfile.mkdtemp(prefix="ct3b-real-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        z = dump(tmp / "lat_zero.npz", n=3000, n_data=2000)
        argv = ["--variant", "zero", "--response-npz", str(z), "--expect-response-sha256", digest(z),
                "--pseudo-npz", str(z), "--expect-pseudo-sha256", digest(z), "--threads", "2", "--out",
                str(tmp / "closure_zero.npz")]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(C.main(argv), 0)
        import s5e_candidate

        s5e_candidate.install("R")
        resp = C.s5c_unfold.load_inputs(z)
        exp, _ = L.closure_inputs(resp, np.ones(resp["MCgen"].shape[0]))
        feat, w_ref, _ = PU.measured_negweight(exp, None, 42, 2)
        unf_in = {k: exp[k] for k in PU.EXP_KEYS}
        unf_in["measured"], unf_in["measured_weights"] = feat, w_ref
        xs, _ = PU.unfold(unf_in, None, 42, 2, 5)
        with np.load(tmp / "closure_zero.npz", allow_pickle=False) as p:
            np.testing.assert_array_equal(p["xsec_flat"], xs.ravel())


if __name__ == "__main__":
    unittest.main()
