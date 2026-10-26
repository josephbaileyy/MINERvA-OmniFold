"""Controls for build_cresp (C-RESP-SPEC.md section 5), on synthetic products, a synthetic S1 assembly and the
committed H2 definition: the half-span block and its invariances, the primary sum without cross-talk, the PSD,
symmetry and rank checks, every refusal (each checked by its message) beside a run that passes, an end-to-end
build recomputed by hand, and the module as invoked. No real data are read."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import build_cresp as bc  # noqa: E402
import s1_assemble as sa  # noqa: E402

ND = Path(__file__).resolve().parents[1]
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
N = 65856
SHIFT = {"proton": 0.010, "meson": 0.015, "em": 0.005, "other": 0.006, "xtalk": 0.004}


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fake(variant: str, kind: str) -> str:
    return hashlib.sha256(f"{variant}/{kind}".encode()).hexdigest()


def meta(variant: str, **extra):
    m = {"schema": "s5p-numerics/1", "config": "R", "capacity": None, "iters": 5, "estimator_seed": 42,
         "estimator_params": [{"n_estimators": 100, "num_leaves": 8, "random_state": 42}] * 3,
         "refinement": {"classifier_params": {"n_estimators": 400, "num_leaves": 31, "random_state": 45}},
         "construction": "data", "truth": "nominal", "bootstrap_seed": None, "jitter_seed": None,
         "coords": "float32", "input_npz_sha256": fake(variant, "npz"), "bkg_dump_sha256": fake(variant, "bkg")}
    m.update(extra)
    return m


def base_x(rng):
    return rng.uniform(0.5, 1.5, N) * 1e-40


def shifted(x0, rng_s, sign, scale):
    """A smooth, species-specific response: a fixed per-fine-cell pattern times the sign."""
    return x0 * (1.0 + sign * scale * rng_s)


class Fixture:
    """Eleven products and an S1 assembly in a temporary tree, with the module's pins patched to them."""

    def __init__(self, tmp: Path, nonlinear: float = 0.0):
        self.tmp, rng = tmp, np.random.default_rng(7)
        self.products = tmp / "unf"
        self.products.mkdir()
        self.x0 = base_x(rng)
        self.pattern = {s: rng.uniform(-1, 1, N) for s in SHIFT}
        self.x = {"zero": self.x0}
        for s, k in SHIFT.items():
            for tag, sign in (("m1", -1), ("p1", +1)):
                self.x[f"{s}_{tag}"] = shifted(self.x0, self.pattern[s], sign, k) + nonlinear * self.x0
        self.U = sa.functional_matrix(sa.fine_map(DEFINITION))
        self.pins = {}
        for v, x in self.x.items():
            self.write_product(v, x)
        self.f = self.U @ self.x0
        C_e = np.diag((0.06 * self.f) ** 2) + np.outer(0.01 * self.f, 0.01 * self.f)
        C_m = np.outer(0.03 * self.f, 0.03 * self.f)
        self.s1 = {"f": self.f, "U": self.U.astype(np.float32), "C_e": C_e, "C_model_abs": C_m, "C_total": C_e + C_m}
        self.s1_path = tmp / "s1_assembly.npz"
        self.write_s1()

    def write_product(self, v, x, **meta_extra):
        p = bc.product_path(self.products, v)
        np.savez_compressed(p, xsec_flat=np.asarray(x, float), shape=np.array(sa.s1.fine_shape()),
                            meta=json.dumps(meta(v, **meta_extra)))
        self.pins[v] = (digest(p), fake(v, "npz"), fake(v, "bkg"))

    def write_s1(self, **override):
        s = {**self.s1, **override}
        self.s1_path.unlink(missing_ok=True)
        np.savez_compressed(self.s1_path, **s, meta=json.dumps({"schema": "s1-assembly/1"}))
        self.s1_sha = digest(self.s1_path)

    def patches(self):
        return (mock.patch.dict(bc.PRODUCTS, self.pins, clear=True),
                mock.patch.object(bc, "S1_ASSEMBLY_SHA256", self.s1_sha))

    def argv(self, out="cresp.npz"):
        return ["--definition", str(DEFINITION), "--products-dir", str(self.products), "--s1-assembly",
                str(self.s1_path), "--out", str(self.tmp / out)]

    def run(self, out="cresp.npz"):
        p1, p2 = self.patches()
        with p1, p2, mock.patch("sys.stdout"):
            return bc.main(self.argv(out))


class Units(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(3)

    def test_block_is_the_half_span_outer_product(self):
        lo, hi = self.rng.uniform(1, 2, 16), self.rng.uniform(1, 2, 16)
        d = (hi - lo) / 2
        np.testing.assert_allclose(bc.species_block(lo, hi), np.outer(d, d), rtol=1e-14)

    def test_block_is_s1_assembles_lateral_convention(self):
        lo, hi = self.rng.uniform(1, 2, 16), self.rng.uniform(1, 2, 16)
        np.testing.assert_array_equal(bc.species_block(lo, hi), sa.mat_cov(np.array([lo, hi])))

    def test_a_common_offset_cancels_and_endpoint_order_does_not_matter(self):
        lo, hi, c = (self.rng.uniform(1, 2, 16) for _ in range(3))
        ref = bc.species_block(lo, hi)
        np.testing.assert_allclose(bc.species_block(lo + c, hi + c), ref, rtol=1e-12)
        np.testing.assert_allclose(bc.species_block(hi, lo), ref, rtol=1e-12)

    def test_curvature_ratio_is_zero_for_a_linear_response_and_measures_a_quadratic(self):
        z, d = self.rng.uniform(1, 2, 16), self.rng.uniform(0.01, 0.02, 16)
        self.assertAlmostEqual(bc.curvature_ratio(z - d, z, z + d), 0.0, places=12)
        q = 0.1 * d
        self.assertAlmostEqual(bc.curvature_ratio(z - d + q, z, z + d + q), np.linalg.norm(2 * q) / np.linalg.norm(2 * d))

    def test_psd_check_fires_on_a_negative_direction_and_on_asymmetry_and_is_silent_on_psd(self):
        A = self.rng.normal(size=(16, 16))
        bc.require_psd(A @ A.T, "psd")
        with self.assertRaisesRegex(SystemExit, "not positive semidefinite"):
            bc.require_psd(A @ A.T - 10 * np.eye(16) * np.abs(A @ A.T).max(), "neg")
        B = A @ A.T
        B[0, 1] += 1e-3 * np.abs(B).max()
        with self.assertRaisesRegex(SystemExit, "not symmetric"):
            bc.require_psd(B, "asym")

    def test_rank_counts_independent_directions(self):
        vs = self.rng.normal(size=(4, 16))
        self.assertEqual(bc.rank(sum(np.outer(v, v) for v in vs)), 4)
        self.assertEqual(bc.rank(np.zeros((16, 16))), 0)

    def test_the_pins_cover_the_eleven_products_and_the_species(self):
        self.assertEqual(len(bc.PRODUCTS), 11)
        want = {"zero"} | {f"{s}_{t}" for s in bc.PRIMARY + bc.VARIANT for t in ("m1", "p1")}
        self.assertEqual(set(bc.PRODUCTS), want)
        self.assertEqual(bc.PRIMARY, ("proton", "meson", "em", "other"))
        self.assertEqual(bc.VARIANT, ("xtalk",))
        for v, shas in bc.PRODUCTS.items():
            self.assertTrue(all(len(s) == 64 and int(s, 16) >= 0 for s in shas), v)


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cresp-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.fx = Fixture(self.tmp)

    def test_the_build_recomputed_by_hand(self):
        self.assertEqual(self.fx.run(), 0)
        z = np.load(self.tmp / "cresp.npz", allow_pickle=False)
        U, x = self.fx.U, self.fx.x
        hand = {}
        for s in bc.PRIMARY + bc.VARIANT:
            d = (U @ x[f"{s}_p1"] - U @ x[f"{s}_m1"]) / 2
            hand[s] = np.outer(d, d)
            np.testing.assert_allclose(z[f"C_resp_{s}"], hand[s], rtol=1e-12)
        C_resp = sum(hand[s] for s in bc.PRIMARY)
        np.testing.assert_allclose(z["C_resp"], C_resp, rtol=1e-12)
        np.testing.assert_allclose(z["C_total_resp"], self.fx.s1["C_total"] + C_resp, rtol=1e-12)
        self.assertFalse(np.allclose(z["C_resp"], C_resp + hand["xtalk"], rtol=1e-6, atol=0.0))   # cross-talk is not summed
        r = json.loads((self.tmp / "cresp.json").read_text())
        self.assertEqual(r["assembly_sha256"], digest(self.tmp / "cresp.npz"))
        np.testing.assert_allclose(r["relative_sigma"]["C_resp"], np.sqrt(np.diag(C_resp)) / self.fx.f, rtol=1e-12)
        self.assertEqual(r["eigen"]["C_resp"]["rank_rel_1e-12"], 4)
        self.assertEqual(r["eigen"]["C_total_resp"]["rank_rel_1e-12"], 16)
        for s in bc.PRIMARY + bc.VARIANT:
            self.assertEqual(r["eigen"][f"C_resp_{s}"]["rank_rel_1e-12"], 1)
            self.assertAlmostEqual(r["curvature_ratio_descriptive"][s], 0.0, places=10)
        self.assertAlmostEqual(sum(r["trace_share_of_C_total_resp"].values()), 1.0, places=12)
        self.assertEqual(r["meta"]["inputs_sha256"]["zero"], self.fx.pins["zero"][0])
        self.assertEqual(set(r["meta"]["labels"]), {"component", "not_varied", "xtalk", "curvature"})

    def test_the_readout_carries_no_absolute_value(self):
        self.fx.run()
        text = (self.tmp / "cresp.json").read_text()
        for v in np.concatenate([self.fx.f, np.diag(self.fx.s1["C_total"])]):
            self.assertNotIn(repr(float(v)), text)

    def test_a_nonlinear_response_shows_in_the_descriptive_ratio_only(self):
        tmp = self.tmp / "nl"
        tmp.mkdir()
        fx = Fixture(tmp, nonlinear=0.001)
        self.assertEqual(fx.run(), 0)
        r = json.loads((tmp / "cresp.json").read_text())
        self.assertGreater(min(r["curvature_ratio_descriptive"].values()), 0.01)

    def test_refuses_to_overwrite(self):
        self.fx.run()
        with self.assertRaisesRegex(SystemExit, "refusing to overwrite"):
            self.fx.run()

    def test_refuses_a_product_whose_digest_differs(self):
        self.fx.pins["em_p1"] = ("0" * 64,) + self.fx.pins["em_p1"][1:]
        with self.assertRaisesRegex(SystemExit, "em_p1 .*sha256"):
            self.fx.run()

    def test_refuses_a_missing_product(self):
        bc.product_path(self.fx.products, "other_m1").unlink()
        with self.assertRaisesRegex(SystemExit, "other_m1: .* is missing"):
            self.fx.run()

    def test_refuses_a_jittered_or_bootstrap_product(self):
        self.fx.write_product("meson_p1", self.fx.x["meson_p1"], jitter_seed=3)
        with self.assertRaisesRegex(SystemExit, "jitter_seed 3 != None"):
            self.fx.run()

    def test_refuses_another_estimator(self):
        self.fx.write_product("proton_m1", self.fx.x["proton_m1"], config="B0")
        with self.assertRaisesRegex(SystemExit, "config/capacity/iters/seed"):
            self.fx.run()

    def test_refuses_a_product_made_from_another_dump(self):
        self.fx.write_product("xtalk_m1", self.fx.x["xtalk_m1"], bkg_dump_sha256="f" * 64)
        with self.assertRaisesRegex(SystemExit, "bkg_dump_sha256"):
            self.fx.run()

    def test_refuses_non_finite_cross_sections(self):
        x = self.fx.x["em_m1"].copy()
        x[5] = np.nan
        self.fx.write_product("em_m1", x)
        with self.assertRaisesRegex(SystemExit, "non-finite"):
            self.fx.run()

    def test_refuses_another_s1_assembly(self):
        p1, p2 = self.fx.patches()
        with p1, mock.patch.object(bc, "S1_ASSEMBLY_SHA256", "1" * 64), self.assertRaisesRegex(SystemExit, "S1 assembly"):
            bc.main(self.fx.argv())

    def test_refuses_an_s1_assembly_on_other_cells(self):
        U = self.fx.s1["U"].copy()
        U[[0, 1]] = U[[1, 0]]
        self.fx.write_s1(U=U)
        with self.assertRaisesRegex(SystemExit, "U is not this definition"):
            self.fx.run()

    def test_refuses_an_s1_total_that_is_not_its_sum(self):
        self.fx.write_s1(C_total=self.fx.s1["C_total"] * 1.01)
        with self.assertRaisesRegex(SystemExit, "C_total is not C_e \\+ C_model_abs"):
            self.fx.run()

    def test_refuses_a_singular_total(self):
        v = self.fx.f
        self.fx.write_s1(C_e=np.outer(v, v) * 1e-4, C_model_abs=np.zeros((16, 16)), C_total=np.outer(v, v) * 1e-4)
        with self.assertRaisesRegex(SystemExit, "C_total_resp rank"):
            self.fx.run()


class AsInvoked(unittest.TestCase):
    """The module run as the spec's argv runs it (-I -B, cwd outside nd-unfolding), with only the pins set by a
    wrapper, since the pins are constants."""

    def test_the_module_as_invoked(self):
        tmp = Path(tempfile.mkdtemp(prefix="cresp-cli-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        fx = Fixture(tmp)
        wrapper = tmp / "wrap.py"
        wrapper.write_text(
            "import json, sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import build_cresp as bc\n"
            f"bc.PRODUCTS.clear(); bc.PRODUCTS.update({{k: tuple(v) for k, v in json.loads({json.dumps(json.dumps(fx.pins))}).items()}})\n"
            f"bc.S1_ASSEMBLY_SHA256 = {fx.s1_sha!r}\n"
            "raise SystemExit(bc.main(sys.argv[1:]))\n")
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, "-I", "-B", str(wrapper), *fx.argv()], cwd=tmp, env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["sha256"], digest(tmp / "cresp.npz"))
        r2 = subprocess.run([sys.executable, "-I", "-B", str(wrapper), *fx.argv()], cwd=tmp, env=env,
                            capture_output=True, text=True)
        self.assertNotEqual(r2.returncode, 0)
        self.assertIn("refusing to overwrite", r2.stderr)


if __name__ == "__main__":
    unittest.main()
