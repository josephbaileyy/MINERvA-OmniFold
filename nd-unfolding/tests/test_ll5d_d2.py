"""ll5d_d2.py (the director's D2 request, 2026-11-12): mu_max of the rebuilt GEANT block against LL5D's ``all`` C_T.
Run over test_ll5d_b's synthetic products: the null, then the readout, then D2 on the same products. Every refusal is
tested in the direction it acts and the other.

    python3 -B nd-unfolding/tests/test_ll5d_d2.py
"""
from __future__ import annotations

import builtins
import importlib.util
import io
import json
import os
import subprocess
import sys
import traceback
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(Path(__file__).resolve().parent))

import fd_1b_inv as inv  # noqa: E402
import fd_1b_mc as mc  # noqa: E402
import ll5d_b as b  # noqa: E402
import ll5d_d2 as d2  # noqa: E402
import test_ll5d_b as tb  # noqa: E402
from test_ll5d import digest  # noqa: E402

GEANT_FULL = ND.parent / "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/lrows-g/geant_full.py"


def reference_mu(G: np.ndarray, M: np.ndarray) -> float:
    """An independent route: the largest eigenvalue of M^-1 G (real, since it is similar to a symmetric matrix)."""
    return float(np.max(np.linalg.eigvals(np.linalg.solve(M, G)).real))


class D2(tb.Pipeline):
    """D2 after the null and the readout, on test_ll5d_b's synthetic g18 products."""

    def readout_file(self) -> Path:
        rf = self.tmp / "readout.json"
        if not rf.exists():
            rf.write_text(json.dumps(self.readout(), sort_keys=True))
        return rf

    def d2_args(self, **kw):
        nf, rf = self.null(), self.readout_file()
        base = dict(null=nf, expect_null_sha256=digest(nf), readout=rf, expect_readout_sha256=digest(rf),
                    out=self.tmp / "d2" / "d2.json")
        base.update(kw)
        return self.args(**base)

    def run_d2(self, **kw):
        return self.with_patches(d2.d2, self.d2_args(**kw))

    def remade_all(self):
        s1, U, frac, _m, w = self.with_patches(b.setup, self.args())
        return self.with_patches(b.remade, self.unf, "g18", s1, U, w, frac, "all")

    # --- the quantity

    def test_mu_max_is_g_neutron_plus_proton_against_c_t_all(self):
        rec = self.run_d2()
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["verdict_role"], "none (descriptive)")
        rm = self.remade_all()
        G = rm["blocks"]["band:GEANT_Neutron"] + rm["blocks"]["band:GEANT_Proton"]
        mu = rec["C_T_all"]["mu_max"]
        self.assertAlmostEqual(mu, reference_mu(G, rm["C_T"]), delta=1e-10 * abs(mu))
        self.assertGreater(mu, 0.0)
        self.assertLess(mu, 1.0)
        # not the Pion band, and not against C_e alone: each gives another number
        Gp = rm["blocks"]["band:GEANT_Pion"] + rm["blocks"]["band:GEANT_Proton"]
        self.assertGreater(abs(reference_mu(Gp, rm["C_T"]) - mu), 1e-6 * mu)
        self.assertGreater(abs(reference_mu(G, rm["C_e"]) - mu), 1e-6 * mu)
        self.assertAlmostEqual(rec["C_T_all"]["chi2_ratio_bound"], 1 / (1 - mu), places=12)
        self.assertEqual(len(rec["C_T_all"]["eigenmode_shares_smallest_first"]), 16)

    def test_the_chi2_bound_holds_for_every_bias(self):
        rec = self.run_d2()
        rm = self.remade_all()
        G = rm["blocks"]["band:GEANT_Neutron"] + rm["blocks"]["band:GEANT_Proton"]
        M, bound = rm["C_T"], rec["C_T_all"]["chi2_ratio_bound"]
        rng = np.random.default_rng(5)
        for _ in range(200):
            v = rng.normal(size=16) * np.sqrt(np.diag(M))
            r = (v @ np.linalg.solve(M - G, v)) / (v @ np.linalg.solve(M, v))
            self.assertGreaterEqual(r, 1 - 1e-12)
            self.assertLessEqual(r, bound * (1 + 1e-9))
        a0 = d2.gen_eig(G, M)[1][:, 0]            # the bound is attained at b = M a0: it is the supremum, not loose
        v = M @ a0
        r = (v @ np.linalg.solve(M - G, v)) / (v @ np.linalg.solve(M, v))
        self.assertAlmostEqual(r, bound, delta=1e-9 * bound)

    def test_gen_eig_is_geant_full_s(self):
        spec = importlib.util.spec_from_file_location("geant_full_ref", GEANT_FULL)
        gf = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules):
            spec.loader.exec_module(gf)
        rng = np.random.default_rng(11)
        for _ in range(5):
            X, Y = rng.normal(size=(16, 40)), rng.normal(size=(16, 3))
            M, G = X @ X.T / 40 + 1e-3 * np.eye(16), Y @ Y.T
            w1, v1 = d2.gen_eig(G, M)
            w2, v2 = gf.gen_eig(G, M)
            np.testing.assert_array_equal(w1, w2)
            np.testing.assert_array_equal(v1, v2)
            self.assertAlmostEqual(w1[0], reference_mu(G, M), delta=1e-10 * abs(w1[0]))

    # --- the pins and the control

    def test_the_control_reproduces_the_readouts_realization_check(self):
        rec = self.run_d2()
        self.assertTrue(rec["control"]["passes"])
        self.assertLessEqual(rec["control"]["max_rel_diff"], d2.CONTROL_TOL)

    def test_a_readout_from_another_matrix_fails_the_control(self):
        ro = json.loads(self.readout_file().read_text())
        for scale, passes in ((1 + 1e-6, False), (1 + 1e-12, True)):
            r2 = json.loads(json.dumps(ro))
            pc = r2["evaluations"]["g18/all"]["readouts"]["realization_check"]["per_cell_sigma"]
            r2["evaluations"]["g18/all"]["readouts"]["realization_check"]["per_cell_sigma"] = [x * scale for x in pc]
            f = self.tmp / f"readout-{scale!r}.json"
            f.write_text(json.dumps(r2, sort_keys=True))
            rec = self.run_d2(readout=f, expect_readout_sha256=digest(f))
            self.assertEqual(rec["control"]["passes"], passes, scale)
            self.assertEqual(rec["verdict"], "PASS" if passes else "INVALID", scale)
            self.assertEqual("C_T_all" in rec, passes, scale)

    def test_refusals(self):
        nf, rf = self.null(), self.readout_file()
        with self.assertRaisesRegex(d2.Refusal, "null's digest"):
            self.run_d2(expect_null_sha256="0" * 64)
        with self.assertRaisesRegex(d2.Refusal, "readout's digest"):
            self.run_d2(expect_readout_sha256="0" * 64)
        with mock.patch.object(b, "products_digest", lambda u, t, r: "other"):
            with self.assertRaisesRegex(d2.Refusal, "not made from these products"):
                self.run_d2()
        nl = json.loads(nf.read_text())
        for change, msg in (({"verdict": "INVALID"}, "not a PASS"), ({"truth": "ar23"}, "not a PASS")):
            f = self.tmp / f"null-{list(change.values())[0]}.json"
            f.write_text(json.dumps(dict(nl, **change), sort_keys=True))
            with self.assertRaisesRegex(d2.Refusal, msg):
                self.run_d2(null=f, expect_null_sha256=digest(f))
        ro = json.loads(rf.read_text())
        f = self.tmp / "readout-other-null.json"
        f.write_text(json.dumps(dict(ro, null_sha256="1" * 64), sort_keys=True))
        with self.assertRaisesRegex(d2.Refusal, "not made with this null"):
            self.run_d2(readout=f, expect_readout_sha256=digest(f))
        r2 = json.loads(rf.read_text())
        del r2["evaluations"]["g18/all"]["readouts"]["realization_check"]
        f = self.tmp / "readout-no-check.json"
        f.write_text(json.dumps(r2, sort_keys=True))
        with self.assertRaisesRegex(d2.Refusal, "no realization_check"):
            self.run_d2(readout=f, expect_readout_sha256=digest(f))
        ps = self.common()
        for p in ps:
            p.start()
        try:
            with mock.patch.object(mc, "made_from", lambda a, U: {"definition_sha256": "other"}):
                with self.assertRaisesRegex(d2.Refusal, "made from"):
                    d2.d2(self.d2_args())
        finally:
            for p in reversed(ps):
                p.stop()

    # --- reads, exits and the record

    def test_records_and_arrays_are_read_with_o_noatime_and_only_the_digest_reads_plainly(self):
        nf, rf = self.null(), self.readout_file()
        real_open, real_io_open = builtins.open, io.open
        plain = []

        def refuse(real):
            def opener(file, *a, **k):
                if isinstance(file, (str, Path)):
                    f = str(file)
                    if f in (str(nf), str(rf)):
                        raise AssertionError(f"plain open of the record {f}")
                    if f.startswith(str(self.unf)):
                        stack = [fr.name for fr in traceback.extract_stack()]
                        if "products_digest" not in stack:
                            raise AssertionError(f"plain open of the product {f} outside products_digest")
                        plain.append(f)
                return real(file, *a, **k)
            return opener
        args = self.d2_args()                     # the test's own digests are taken before the guard
        inv.OPENED.clear()
        with mock.patch.object(builtins, "open", refuse(real_open)), mock.patch.object(io, "open", refuse(real_io_open)):
            rec = self.with_patches(d2.d2, args)
        self.assertEqual(rec["verdict"], "PASS")
        self.assertIn(str(nf), inv.OPENED)
        self.assertIn(str(rf), inv.OPENED)
        self.assertTrue(any(p.startswith(str(self.unf)) for p in inv.OPENED))
        self.assertTrue(plain, "products_digest read the products (the call LL5D's null and readout make)")

    def test_main_writes_the_record_once_and_a_refusal_is_invalid(self):
        out = self.tmp / "main" / "d2-g18.json"
        argv = lambda o, **kw: [  # noqa: E731
            "--staged", str(self.tmp), "--definition", str(self.tmp / "definition.json"), "--unfolds", str(self.unf),
            "--cmodel-json", str(self.tmp / "cmodel.json"), "--flux-constraint", str(self.w.constraint),
            "--truth", "g18", "--null", str(self.null()),
            "--expect-null-sha256", kw.get("nsha", digest(self.null())), "--readout", str(self.readout_file()),
            "--expect-readout-sha256", digest(self.readout_file()), "--out", str(o)]
        self.assertEqual(self.with_patches(d2.main, argv(out)), 0)
        rec = json.loads(out.read_text())
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["atime"]["moved"], [])
        self.assertFalse(any(k.endswith("_sha256") and k[:-7] in rec for k in rec), "a path + _sha256 key pair")
        with self.assertRaises(SystemExit):
            self.with_patches(d2.main, argv(out))
        bad = self.tmp / "main" / "d2-bad.json"
        self.assertEqual(self.with_patches(d2.main, argv(bad, nsha="0" * 64)), 5)
        self.assertFalse(bad.exists())
        self.assertEqual(json.loads(bad.with_suffix(".invalid.json").read_text())["verdict"], "INVALID")
        moved = self.tmp / "main" / "d2-moved.json"
        with mock.patch.object(inv, "atime_check", lambda: {"files": {}, "moved": ["x"]}):
            self.assertEqual(self.with_patches(d2.main, argv(moved)), 0 | 8)

    def test_the_remaining_guards_and_the_entry_point(self):
        rng = np.random.default_rng(2)
        X = rng.normal(size=(16, 40))
        M, G = X @ X.T / 40 + np.eye(16), np.eye(16) * 0.1
        real = d2.gen_eig
        with mock.patch.object(d2, "gen_eig", lambda g, m: (real(g, m)[0] * 1.01, real(g, m)[1])):
            with self.assertRaisesRegex(d2.Refusal, "top direction"):
                d2.summarize(G, M, [f"R{c:02d}" for c in range(16)])
        r2 = json.loads(self.readout_file().read_text())
        pc = r2["evaluations"]["g18/all"]["readouts"]["realization_check"]["per_cell_sigma"]
        r2["evaluations"]["g18/all"]["readouts"]["realization_check"]["per_cell_sigma"] = pc[:15]
        f = self.tmp / "readout-short.json"
        f.write_text(json.dumps(r2, sort_keys=True))
        with self.assertRaisesRegex(d2.Refusal, "shape"):
            self.run_d2(readout=f, expect_readout_sha256=digest(f))
        mod = Path(d2.__file__).resolve()          # under the mutation runner, a temporary copy beside no siblings
        env = dict(os.environ, PYTHONPATH=str(ND))
        p = subprocess.run([sys.executable, "-B", str(mod), "--help"], capture_output=True, text=True,
                           cwd=str(self.tmp), env=env)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("--expect-readout-sha256", p.stdout)
        # loaded by path from elsewhere (its directory not on sys.path): the module puts its own directory first
        code = ("import importlib.util, sys; d = sys.argv[2]; b = d in sys.path; sys.path.append(sys.argv[3]); "
                "s = importlib.util.spec_from_file_location('m', sys.argv[1]); "
                "m = importlib.util.module_from_spec(s); s.loader.exec_module(m); print(not b and d in sys.path)")
        p = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(mod), str(mod.parent), str(ND)],
                           capture_output=True, text=True, cwd=str(self.tmp))
        self.assertEqual((p.returncode, p.stdout.strip()), (0, "True"), p.stderr)

    def test_nothing_in_ll5d_b_is_redefined(self):
        src = Path(d2.__file__).read_text()
        for name in ("def remade(", "def setup(", "def products_digest(", "def _x(", "def mat_cov("):
            self.assertNotIn(name, src)


for _name in [n for n in dir(tb.Pipeline) if n.startswith("test")]:
    setattr(D2, _name, None)          # test_ll5d_b runs its own Pipeline tests; only D2's run here


if __name__ == "__main__":
    unittest.main()
