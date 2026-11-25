"""Tests of b5d_build.py (B5D-DECLARATION.md rev 1): the bias block, the per-band factor and its bootstrap, the trigger
in each direction, the fluctuation block, and the band rules. Run: python3 -B -m unittest nd-unfolding/b5d/test_b5d.py"""
import sys
import json
import types
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b5d_build as M  # noqa: E402

N = 16


def spd(seed, scale=1.0):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(N, N))
    return scale * (A @ A.T / N + 0.1 * np.eye(N))


class BiasBlock(unittest.TestCase):
    def test_debiased_sum_and_positive_part(self):
        rng = np.random.default_rng(0)
        beta = {t: rng.normal(0, 0.05, N) for t in M.FAMILY}
        Sigma = {t: np.diag(np.full(N, 1e-4)) for t in M.FAMILY}
        C, C0 = M.bias_block(beta, Sigma)
        raw = sum(np.outer(beta[t], beta[t]) - Sigma[t] for t in M.FAMILY)
        self.assertTrue(np.allclose(C0, sum(np.outer(beta[t], beta[t]) for t in M.FAMILY)))
        self.assertGreaterEqual(np.linalg.eigvalsh(C).min(), -1e-15)
        w, V = np.linalg.eigh(raw)
        self.assertTrue(np.allclose(C, (V * np.clip(w, 0, None)) @ V.T))
        self.assertLessEqual(int(np.sum(np.linalg.eigvalsh(C) > 1e-12)), 4)  # rank <= |F|

    def test_the_sum_not_the_mean(self):
        beta = {t: np.zeros(N) for t in M.FAMILY}
        beta["A7_gibuu"] = np.eye(N)[0] * 0.1
        C, _ = M.bias_block(beta, {t: np.zeros((N, N)) for t in M.FAMILY})
        self.assertAlmostEqual(C[0, 0], 0.01)  # one member's full outer product, not divided by 4

    def test_a_member_outside_the_family_does_not_enter(self):
        beta = {t: np.zeros(N) for t in M.FAMILY}
        beta["W1"] = np.ones(N)
        C, _ = M.bias_block(beta, {t: np.zeros((N, N)) for t in M.FAMILY})
        self.assertTrue(np.allclose(C, 0))

    def test_against(self):
        C = np.diag([4.0] + [0.0] * (N - 1))
        r = M.against(np.eye(N)[0] * 2.0, C)
        self.assertAlmostEqual(r["quad"], 1.0)
        self.assertAlmostEqual(r["fraction_outside_span"], 0.0)
        r = M.against(np.eye(N)[1], C)
        self.assertAlmostEqual(r["fraction_outside_span"], 1.0)


class Fluctuation(unittest.TestCase):
    def sample(self, D, n, scale=1.0, seed=1):
        rng = np.random.default_rng(seed)
        return rng.multivariate_normal(np.zeros(N), scale * D, size=n)

    def test_eig_sorted_signs_and_order(self):
        w, V = M.eig_sorted(spd(2))
        self.assertTrue(np.all(np.diff(w) <= 0))
        for i in range(N):
            self.assertGreater(V[np.argmax(np.abs(V[:, i])), i], 0)

    def test_eig_sorted_canonical_on_an_exact_tie(self):
        d = np.array([1.0, 3.0, 3.0, 2.0] + [0.5] * (N - 4))
        rng = np.random.default_rng(5)
        for _ in range(5):
            w, V = M.eig_sorted(np.diag(d))
            np.testing.assert_allclose(V[:, :2], np.eye(N)[:, 1:3], atol=1e-12)  # e_2, e_3 in cell order
            self.assertEqual(list(w[:2]), [3.0, 3.0])
        Q = np.linalg.qr(rng.normal(size=(N, N)))[0]
        w1, V1 = M.eig_sorted(Q @ np.diag(d) @ Q.T)
        self.assertTrue(np.all(np.diff(w1) <= 0))
        # a solver that returns the tied space in a rotated basis: the canonical basis comes back
        from unittest import mock
        c, s_ = np.cos(0.7), np.sin(0.7)
        Vr = np.eye(N)
        Vr[:, 1], Vr[:, 2] = c * np.eye(N)[:, 1] + s_ * np.eye(N)[:, 2], -s_ * np.eye(N)[:, 1] + c * np.eye(N)[:, 2]
        with mock.patch.object(M.np.linalg, "eigh", lambda A: (d.copy(), Vr.copy())):
            w2, V2 = M.eig_sorted(np.diag(d))
        np.testing.assert_allclose(V2[:, :2], np.eye(N)[:, 1:3], atol=1e-12)

    def test_tie_rule_signs_and_a_small_first_projection(self):
        from unittest import mock
        d = np.array([3.0, 3.0] + [1.0] * (N - 2))
        u1 = np.zeros(N); u1[0], u1[2] = 0.1, -np.sqrt(0.99)
        A = np.column_stack([u1, np.eye(N)[:, 1]] + [np.eye(N)[:, k] for k in range(N) if k not in (1,)])
        Q = np.linalg.qr(A)[0]
        with mock.patch.object(M.np.linalg, "eigh", lambda X: (d.copy(), Q.copy())):
            w, V = M.eig_sorted(np.eye(N))
        for c in range(2):
            self.assertGreater(V[int(np.argmax(np.abs(V[:, c]))), c], 0)  # the sign rule after Gram-Schmidt
        a = np.zeros(N); a[0], a[7] = 1e-15, np.sqrt(1 - 1e-30)
        A = np.column_stack([a, np.eye(N)[:, 5]] + [np.eye(N)[:, k] for k in range(N) if k not in (5, 7)])
        Q = np.linalg.qr(A)[0]
        with mock.patch.object(M.np.linalg, "eigh", lambda X: (d.copy(), Q.copy())):
            w, V = M.eig_sorted(np.eye(N))
        self.assertAlmostEqual(abs(V[7, 0]), 1.0, places=10)  # e_1's 1e-15 projection is kept (relative test): a first
        Z = Q.copy()
        Z[:, :2] = 0.0  # a degenerate solver output: the tied space cannot be spanned
        with mock.patch.object(M.np.linalg, "eigh", lambda X: (d.copy(), Z.copy())):
            with self.assertRaisesRegex(M.Stop, "spanned 0 of 2"):
                M.eig_sorted(np.eye(N))

    def test_tie_rule_stays_orthonormal_on_near_parallel_projections(self):
        from unittest import mock
        rng = np.random.default_rng(2)
        A = rng.normal(size=(N, 3))
        A[0], A[1] = [1, 0, 0], [1, 1e-9, 0]  # e_1 and e_2 project almost parallel into the tied space
        U = np.linalg.qr(A)[0]
        Q = np.linalg.qr(np.column_stack([U, rng.normal(size=(N, N - 3))]))[0]
        d = np.array([3.0, 3.0, 3.0] + [1.0] * (N - 3))
        with mock.patch.object(M.np.linalg, "eigh", lambda X: (d.copy(), Q.copy())):
            w, V = M.eig_sorted(np.eye(N))
        np.testing.assert_allclose(V[:, :3].T @ V[:, :3], np.eye(3), atol=1e-13)  # COVFIX's two passes
        np.testing.assert_allclose(V[:, :3] @ V[:, :3].T, U @ U.T, atol=1e-12)  # the same space

    def test_against_a_zero_rank_block(self):
        r = M.against(np.ones(N), np.zeros((N, N)))
        self.assertIsNone(r["quad"])
        self.assertEqual(r["rank"], 0)
        self.assertEqual(r["fraction_outside_span"], 1.0)

    def test_fhat_averages_only_the_ensembles_that_keep_the_band(self):
        D = spd(31)
        w, V = M.eig_sorted(D)
        A, B2 = self.sample(D, 400, 1.0, 1), self.sample(D, 400, 4.0, 2)
        ens = {("g18", "minus2"): (A, w, V), ("ar23", "minus2"): (B2, w, V)}
        full, _ = M.bands_kept(w)
        bands = {("g18", "minus2"): full, ("ar23", "minus2"): [x for x in full if x[0] != M.BANDS[2][0]]}
        f = M.fhat(ens, bands)
        only = M.band_factor(M.mode_spreads(A, w, V), full[2][2], 400)
        self.assertAlmostEqual(f[2], only, places=12)
        self.assertGreater(f[0], 2.0)  # both enter R1
        f_none = M.fhat(ens, {k: [x for x in v if x[0] != 0] for k, v in bands.items()})
        self.assertIsNone(f_none[0])
        self.assertEqual(M.trigger(f_none, {0: None, 1: 0.1, 2: 0.1})[0]["phi"], 1.0)

    def test_l_acts_only_on_c_e_kept_modes(self):
        rng = np.random.default_rng(8)
        A = rng.normal(size=(N, 10))
        C = A @ A.T  # rank 10: modes 11-16 are not kept
        trig = {0: {"active": False, "phi": 1.0}, 1: {"active": False, "phi": 1.0}, 2: {"active": True, "phi": 4.0}}
        V_F, L = M.fluctuation_block(C, trig)
        w, V = M.eig_sorted(C)
        null = V[:, 10:]
        np.testing.assert_allclose(L @ null, null, atol=1e-10)
        np.testing.assert_allclose(V[:, 8:10].T @ L @ V[:, 8:10], 2 * np.eye(2), atol=1e-10)

    def test_a_correct_block_gives_fhat_near_one_and_an_inflated_one_more(self):
        D = spd(3)
        w, V = M.eig_sorted(D)
        bands, _ = M.bands_kept(w)
        ens = {("g18", "minus2"): (self.sample(D, 3000, 1.0, 4), w, V), ("ar23", "minus2"): (self.sample(D, 3000, 1.0, 5), w, V)}
        f = M.fhat(ens, {k: bands for k in ens})
        for r in f:
            self.assertAlmostEqual(f[r], 1.0, delta=0.08)
        ens2 = {k: (self.sample(D, 3000, 2.0, 6 + i), w, V) for i, k in enumerate(ens)}
        f2 = M.fhat(ens2, {k: bands for k in ens2})
        for r in f2:
            self.assertAlmostEqual(f2[r], 2.0, delta=0.2)


    def test_mode_spreads_are_centred(self):
        D = spd(15)
        w, V = M.eig_sorted(D)
        E = self.sample(D, 200, 1.0, 16)
        self.assertTrue(np.allclose(M.mode_spreads(E, w, V), M.mode_spreads(E + 5.0, w, V)))

    def test_band_factor_uses_n_minus_1_over_n(self):
        v = np.full(N, 0.9)
        self.assertAlmostEqual(M.band_factor(v, list(range(4)), 10), 1.0)

    def test_bootstrap_se_is_reproducible_and_positive(self):
        D = spd(7)
        w, V = M.eig_sorted(D)
        bands, _ = M.bands_kept(w)
        ens = {("g18", "minus2"): (self.sample(D, 300, 1.0, 8), w, V), ("ar23", "minus2"): (self.sample(D, 300, 1.0, 9), w, V)}
        b = {k: bands for k in ens}
        s1 = M.bootstrap_se(ens, b, n=200)
        s2 = M.bootstrap_se(ens, b, n=200)
        self.assertEqual(s1, s2)
        self.assertTrue(all(0.01 < s < 0.5 for s in s1.values()), s1)  # ~0.03 expected for N = 300, 4-mode bands

    def test_a2_band_states(self):
        f = {0: 30.0, 1: 1.2, 2: 2.0, 3: None}
        se = {0: 4.0, 1: 0.3, 2: 0.6, 3: None}
        t = M.trigger(f, se)
        self.assertEqual([t[r]["state"] for r in range(4)], ["ACTIVE", "RESOLVED-INACTIVE", "UNRESOLVED", "UNMEASURED"])
        self.assertEqual([t[r]["phi"] for r in range(4)], [30.0, 1.0, 1.0, 1.0])
        self.assertEqual(M.trigger({0: 1.1}, {0: 0.5})[0]["state"], "RESOLVED-INACTIVE")  # SE = 0.5 is resolved

    def test_trigger_in_each_direction(self):
        t = M.trigger({0: 1.31, 1: 1.30, 2: 0.8}, {0: 0.1, 1: 0.1, 2: 0.05})
        self.assertTrue(t[0]["active"])
        self.assertEqual(t[0]["phi"], 1.31)
        self.assertFalse(t[1]["active"])  # f - 1 = 3 SE exactly: not > 3 SE
        self.assertEqual(t[1]["phi"], 1.0)
        self.assertFalse(t[2]["active"])  # a factor below 1 is never applied
        self.assertEqual(t[2]["phi"], 1.0)
        self.assertEqual(M.trigger({0: None}, {0: None})[0]["phi"], 1.0)

    def test_fluctuation_block_changes_only_active_bands(self):
        C = spd(10)
        none = {r: {"active": False, "phi": 1.0} for r in range(3)}
        V0, L0 = M.fluctuation_block(C, none)
        self.assertTrue(np.allclose(V0, C))
        self.assertTrue(np.allclose(L0, np.eye(N)))
        one = dict(none)
        one[0] = {"active": True, "phi": 1.44}
        V1, L1 = M.fluctuation_block(C, one)
        w, U = M.eig_sorted(C)
        Vt = U.T @ V1 @ U
        self.assertTrue(np.allclose(np.diag(Vt)[:4], 1.44 * w[:4]))
        self.assertTrue(np.allclose(np.diag(Vt)[4:], w[4:]))

    def test_bands_kept_drops_a_thin_band(self):
        w = np.array([10.0] * 6 + [1e-14] * 10)
        kept, dropped = M.bands_kept(w)
        self.assertEqual([k[0] for k in kept], [0])  # ranks 5-8 hold 2 kept modes (<4): dropped; 9-16 hold none
        self.assertEqual(sorted(d[0] for d in dropped), [4, 8])

    def test_declared_constants(self):
        self.assertEqual(M.BANDS, ((0, 4), (4, 8), (8, 16)))
        self.assertEqual((M.BOOT_N, M.BOOT_SEED, M.TRIGGER_K, M.MIN_MODES, M.UNRESOLVED_SE), (2000, 9_991_000, 3.0, 4, 0.5))
        self.assertEqual(M.FAMILY, ("nominal", "A7_genie_mec", "A7_nuwro", "A7_gibuu"))
        self.assertEqual((M.PRIMARY, M.SECONDARY), ("minus2", "all"))


def outlier(E):
    """One toy 300x the rest: f-hat in the hundreds with an SE as large, so every measured band is UNRESOLVED."""
    E = E.copy()
    E[0] *= 300.0
    return E


class EndToEnd(unittest.TestCase):
    """build() on a tiny synthetic world: stand-in modules for s1_assemble, ll5d, ll5d_b and bsel_select with the same
    names and conventions, 16-entry products, an identity functional; the module's pins re-pointed to the fixture."""

    def setUp(self):
        import json
        import tempfile
        import types
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.repo, self.ll5d = d / "repo", d / "ll5d"
        self.ll5d.mkdir()
        rng = np.random.default_rng(11)
        bands = {"Flux": 4, "MaRES": 2, "GEANT_Neutron": 2}
        stat_reps = tuple(range(1, 6))
        seeds = {"g18": range(100, 140), "ar23": range(200, 240)}
        D = spd(12, 1e-4)
        pins = []
        X_T = np.full(N, 1.0)

        def save(name, xs, xt):
            np.savez(self.ll5d / name, xsec_flat=xs, xtrue_flat=xt)
            pins.append(("toys" if "_toy_" in name else "null_roles", name))
        for t in seeds:
            save(f"ll5d_{t}_central_T.npz", X_T, X_T)
            save(f"ll5d_{t}_seed_T.npz", X_T, X_T)
            for b, n in bands.items():
                for i in range(n):
                    save(f"ll5d_{t}_block_{b}_{i}.npz", X_T + rng.normal(0, 0.01, N), X_T)
            for r in stat_reps:
                save(f"ll5d_{t}_stat_{r}.npz", X_T + rng.normal(0, 0.005, N), X_T)
            for rd in ("minus2", "all"):
                for s in seeds[t]:
                    e = rng.multivariate_normal(np.zeros(N), D)
                    save(f"ll5d_{t}_toy_{rd}_{s}.npz", X_T + e, X_T)
        (self.ll5d / M.CONSTRAINT_NAME).write_text("Flux 0 1.0\nFlux 1 2.0\nFlux 2 1.0\nFlux 3 1.0\n")
        w = np.array([1.0, 2.0, 1.0, 1.0])
        fdir = self.repo / M.FD
        lst = "\n".join(f"{g}\t{M.sha256_path(self.ll5d / n)}\t/pscratch/x/{n}" for g, n in pins) + "\n"
        files = {
            f"{M.FD}/with-cpl/data-product/fd_data_product_cpl_C_e.csv":
                "cell," + ",".join(f"R{c:02d}" for c in range(N)) + "\n" + "\n".join(
                    f"R{c:02d}," + ",".join(repr(x) for x in spd(13)[c]) for c in range(N)) + "\n",
            "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json":
                json.dumps({"meta": {"flux_weights": {"sum": float(w.sum()), "n_eff": float(w.sum() ** 2 / (w ** 2).sum())}},
                            "relative_sigma": {"flux": [0.03] * N, "stat": [0.002] * N}}),
            f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv": lst,
        }
        for rel, txt in files.items():
            p = self.repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(txt)
        roles = ("central", "seed", "block", "stat")

        def products_digest(unfolds, truth, rl):
            import hashlib
            h = hashlib.sha256()
            for q in sorted(Path(unfolds).glob(f"ll5d_{truth}_*.npz")):
                if q.name.split("_")[2] in rl:
                    h.update(q.name.encode())
                    h.update(M.sha256_path(q).encode())
            return h.hexdigest()
        for t in seeds:
            p = self.repo / f"{M.FD}/receipts-ll5d/null/node/null-{t}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"products_sha256": products_digest(self.ll5d, t, roles)}))
        self.saved = dict(M.COMMITTED)
        M.COMMITTED.clear()
        M.COMMITTED.update({rel: M.sha256_path(self.repo / rel) for rel in list(files) + [
            f"{M.FD}/receipts-ll5d/null/node/null-g18.json", f"{M.FD}/receipts-ll5d/null/node/null-ar23.json"]})
        self.saved_manifest_n = None
        self.sa = types.SimpleNamespace(
            CONSTRAINT_SHA256=M.sha256_path(self.ll5d / M.CONSTRAINT_NAME), EXPECT=bands, FLUX="Flux",
            mat_cov=lambda X, w=None: __import__("s1_assemble_stub").mat_cov(X, w),
            functional_matrix=lambda fm: np.eye(N), fine_map=lambda p: None,
            flux_weights=lambda p: w.copy())
        self.ll5d_mod = types.SimpleNamespace(TOY_SEEDS=seeds)
        self.ll5d_b = types.SimpleNamespace(
            bands_of=lambda rd: [b for b in bands if not (rd == "minus2" and b == "GEANT_Neutron")],
            product_name=lambda t, role, item: f"ll5d_{t}_{role}_{item}.npz", STAT_REPLICAS=stat_reps,
            BLOCK_ROLES=roles, products_digest=products_digest)
        beta_rng = np.random.default_rng(14)
        truths = ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune", "A7_genie_cv",
                  "A7_genie_mec", "A7_nuwro", "A7_gibuu", "F1_genie_v3_g18", "F1_genie_v3_ar23")
        tabs = {t: 0.01 + beta_rng.normal(0, 0.002, (16 if t.startswith("A7") else 40, N)) for t in M.FAMILY}
        sel = self.repo / M.SELECTION_INPUTS
        sel.mkdir(parents=True)
        np.savez(sel / "fd_f0b_experiments.npz", **{f"r_{t}": v for t, v in tabs.items()},
                 r_cal_A7_nuwro=np.array([object()], dtype=object))  # unreadable with allow_pickle=False: never read
        b = {t: (tabs[t].mean(0) if t in tabs else np.full(N, 0.01)) for t in truths}
        sig = {t: (np.sqrt(np.diag(np.cov(tabs[t], rowvar=False, ddof=1)) / tabs[t].shape[0]) if t in tabs else np.full(N, 1e-3)) for t in truths}
        self.B = types.SimpleNamespace(TRUTHS=truths, check_pins=lambda repo, sel: None,
                                       prepare=lambda repo, sel, M16: (b, sig, {t: np.ones(N) for t in truths}, {}, {"mnvtune_v1": [2e-39] * N}))
        sys.modules["estimator_stability_analyze"] = types.SimpleNamespace(cell_matrix=lambda p: np.eye(N))
        stub = types.ModuleType("s1_assemble_stub")

        def mat_cov(X, w=None):
            w = np.ones(X.shape[0]) if w is None else np.asarray(w, float)
            mu = (w[:, None] * X).sum(0) / w.sum()
            Z = X - mu
            return (Z.T * w) @ Z / w.sum()
        stub.mat_cov = mat_cov
        sys.modules["s1_assemble_stub"] = stub
        self.orig_pins = M.manifest_pins
        M.manifest_pins = lambda repo: {Path(l.split("\t")[2]).name: l.split("\t")[1]
                                        for l in (repo / f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv").read_text().splitlines() if l.strip()}
        self.orig_check = M.check_ll5d_pins

        def check(repo, d, sa):  # the real check with the fixture's file count
            pins = M.manifest_pins(repo)
            have = {q.name for q in d.glob("ll5d_*.npz")}
            if have != set(pins):
                raise M.Stop("C-PIN", "set")
            for n, pin in pins.items():
                if M.sha256_path(d / n) != pin:
                    raise M.Stop("C-PIN", f"{n} is not its pin")
            if M.sha256_path(d / M.CONSTRAINT_NAME) != sa.CONSTRAINT_SHA256:
                raise M.Stop("C-PIN", "constraint")
        M.check_ll5d_pins = check

    def tearDown(self):
        M.COMMITTED.clear()
        M.COMMITTED.update(self.saved)
        M.manifest_pins = self.orig_pins
        M.check_ll5d_pins = self.orig_check
        for k in ("estimator_stability_analyze", "s1_assemble_stub"):
            sys.modules.pop(k, None)
        self.tmp.cleanup()

    def build(self):
        return M.build(self.repo, self.ll5d, self.sa, self.ll5d_mod, self.ll5d_b, self.B)

    def test_build_runs_and_reports(self):
        rec = self.build()
        self.assertEqual(rec["schema"], M.SCHEMA)
        self.assertEqual(len(rec["bias_block"]["C_b_tune_v1_units"]), N)
        self.assertEqual(set(rec["fluctuation"]["f_hat"]), {"R1", "R2", "R3"})
        self.assertNotIn("cal_cross_check_sd_over_s1_flux_stat", rec)  # A1 item 1: the cal cross-check is dropped
        me = rec["bias_block"]["ll5d_toy_mean_error_tune_v1_units"]
        self.assertEqual(set(me), {"g18/minus2", "g18/all", "ar23/minus2", "ar23/all"})
        self.assertTrue({"quad", "fraction_outside_span", "rank", "beta"} <= set(me["g18/minus2"]))
        M.check_leak(rec)
        self.assertEqual(set(rec["fluctuation"]["per_ensemble"]), {"g18/minus2", "g18/all", "ar23/minus2", "ar23/all"})


    def test_band_traces_are_printed_for_every_band_and_reading(self):
        rec = self.build()
        tr = rec["fluctuation"]["band_traces_relative_to_T"]
        self.assertEqual(set(tr), {"g18/minus2", "g18/all", "ar23/minus2", "ar23/all"})
        for d in tr.values():
            self.assertEqual(set(d), {"R1", "R2", "R3"})
        D = spd(31)
        w, V = M.eig_sorted(D)
        E = np.random.default_rng(3).multivariate_normal(np.zeros(N), 2 * D, 400)
        kept, dropped = M.bands_kept(w)
        X = np.full(N, 2.0)
        t = M.band_traces(E, D, V, X, kept, dropped)
        Xn = np.linspace(0.5, 3.0, N)  # nonuniform: W does not commute with P
        tn = M.band_traces(E, D, V, Xn, kept, dropped)
        W = np.diag(1 / Xn)
        P = V[:, kept[0][2]] @ V[:, kept[0][2]].T
        S = np.cov(E, rowvar=False, ddof=1)
        self.assertAlmostEqual(tn["R1"]["toy"], np.trace(W @ P @ S @ P @ W), places=12)
        self.assertAlmostEqual(tn["R1"]["reference"], np.trace(W @ P @ D @ P @ W), places=12)
        self.assertNotAlmostEqual(tn["R1"]["reference"], np.trace(P @ W @ D @ W @ P), places=6)
        v = M.mode_spreads(E, w, V)
        idx = kept[0][2]
        self.assertAlmostEqual(t["R1"]["reference"], w[idx].sum() / 4, places=12)  # W = I/2
        self.assertAlmostEqual(t["R1"]["toy"], (w[idx] * v[idx]).sum() * 400 / 399 / 4, places=12)
        self.assertTrue(t["R1"]["kept"])

    def test_an_unresolved_build_still_prints_the_size(self):
        import tempfile
        orig = M.toy_errors
        M.toy_errors = lambda d, U, t, rd, *a: outlier(orig(d, U, t, rd, *a))  # noise, not a resolved excess
        try:
            rec = self.build()
        finally:
            M.toy_errors = orig
        fl = rec["fluctuation"]
        self.assertTrue(fl["unresolved_stop"])
        self.assertIsNone(fl["V_F"])
        self.assertTrue(all(v is not None for r, v in fl["f_hat"].items() if r != "R3"))
        self.assertEqual({r: v["state"] for r, v in fl["trigger"].items()}, {"R1": "UNRESOLVED", "R2": "UNRESOLVED", "R3": "UNMEASURED"})
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "o"
            M.write_record(d, rec)
            txt = (Path(d) / "blocks5d.txt").read_text()
        self.assertIn("unresolved stop: True", txt)
        self.assertIn("g18/minus2 traces (relative to T): R1 toy", txt)

    def test_a2_all_resolved_inactive_builds_v_f_equal_to_c_e(self):
        orig = M.toy_errors
        M.toy_errors = lambda d, U, t, rd, *a: 0.5 * orig(d, U, t, rd, *a)  # spread below the block: nothing active
        try:
            rec = self.build()
        finally:
            M.toy_errors = orig
        fl = rec["fluctuation"]
        self.assertEqual({r: v["state"] for r, v in fl["trigger"].items()},
                         {"R1": "RESOLVED-INACTIVE", "R2": "RESOLVED-INACTIVE", "R3": "UNMEASURED"})
        self.assertFalse(fl["unresolved_stop"])
        np.testing.assert_allclose(np.asarray(fl["V_F"]), spd(13), rtol=1e-12)  # L = I

    def test_a2_a_resolved_large_excess_builds_v_f(self):
        orig = M.toy_errors
        M.toy_errors = lambda d, U, t, rd, *a: 30.0 * orig(d, U, t, rd, *a)  # f-hat ~ 900 with SE > 0.5, resolved
        try:
            rec = self.build()
        finally:
            M.toy_errors = orig
        fl = rec["fluctuation"]
        self.assertTrue(all(fl["se"][r] > 0.5 for r in ("R1", "R2")))
        self.assertEqual(fl["trigger"]["R1"]["state"], "ACTIVE")
        self.assertFalse(fl["unresolved_stop"])
        self.assertIsNotNone(fl["V_F"])

    def test_an_active_trigger_inside_build(self):
        orig = M.toy_errors
        M.toy_errors = lambda d, U, t, rd, *a: 3.0 * orig(d, U, t, rd, *a)  # spread 9x: R1 and R2 active
        try:
            rec = self.build()
        finally:
            M.toy_errors = orig
        fl = rec["fluctuation"]
        measured = [r for r, v in fl["f_hat"].items() if v is not None]
        self.assertTrue(measured)
        for r in measured:
            self.assertTrue(fl["trigger"][r]["active"])
            self.assertEqual(fl["trigger"][r]["phi"], fl["f_hat"][r])
            self.assertGreater(fl["trigger"][r]["phi"], 1.0)
        C_e = spd(13)  # the fixture's C_e
        V_F, L = np.asarray(fl["V_F"]), np.asarray(fl["L"])
        np.testing.assert_allclose(V_F, L @ C_e @ L.T, rtol=1e-10, atol=0)
        self.assertGreater(np.trace(V_F), np.trace(C_e))

    def test_a_rank_deficient_block_drops_modes_not_the_build(self):
        rec = self.build()  # the fixture's D has 6 universes + 5 replicas: fewer than 16 positive modes
        dropped = rec["fluctuation"]["dropped"]
        self.assertTrue(any(dropped.values()))
        self.assertIsNotNone(rec["fluctuation"]["f_hat"]["R1"])


    def test_c_seed_fires_when_the_digest_would_pass(self):
        q = self.ll5d / "ll5d_g18_seed_T.npz"
        np.savez(q, xsec_flat=np.full(N, 1.5), xtrue_flat=np.ones(N))
        lst = self.repo / f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"
        lst.write_text("\n".join(l if not l.endswith("/ll5d_g18_seed_T.npz") else
                                 "\t".join([l.split("\t")[0], M.sha256_path(q), l.split("\t")[2]])
                                 for l in lst.read_text().splitlines()) + "\n")
        M.COMMITTED[f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"] = M.sha256_path(lst)
        self.ll5d_b.products_digest = lambda *a: __import__("json").loads(
            (self.repo / f"{M.FD}/receipts-ll5d/null/node/null-{a[1]}.json").read_text())["products_sha256"]
        with self.assertRaisesRegex(M.Stop, "C-SEED"):
            self.build()

    def test_a_committed_input_not_its_pin_stops(self):
        M.COMMITTED[f"{M.FD}/with-cpl/data-product/fd_data_product_cpl_C_e.csv"] = "0" * 64
        with self.assertRaisesRegex(M.Stop, "C-PIN"):
            self.build()

    def test_a_table_noise_mismatch_stops(self):
        b, sig, R, sr, g = self.B.prepare(None, None, None)
        sig = dict(sig)
        sig["A7_nuwro"] = sig["A7_nuwro"] * 1.01
        self.B.prepare = lambda *a: (b, sig, R, sr, g)
        with self.assertRaisesRegex(M.Stop, "C-TAB"):
            self.build()

    def test_a_block_with_no_positive_mode_stops(self):
        for q in self.ll5d.glob("ll5d_g18_block_*.npz"):
            np.savez(q, xsec_flat=np.ones(N), xtrue_flat=np.ones(N))
        for q in self.ll5d.glob("ll5d_g18_stat_*.npz"):
            np.savez(q, xsec_flat=np.ones(N), xtrue_flat=np.ones(N))
        lst = self.repo / f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"
        lst.write_text("\n".join("\t".join([l.split("\t")[0], M.sha256_path(self.ll5d / Path(l.split("\t")[2]).name), l.split("\t")[2]])
                                 for l in lst.read_text().splitlines() if l.strip()) + "\n")
        M.COMMITTED[f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"] = M.sha256_path(lst)
        self.ll5d_b.products_digest = lambda *a: __import__("json").loads(
            (self.repo / f"{M.FD}/receipts-ll5d/null/node/null-{a[1]}.json").read_text())["products_sha256"]
        with self.assertRaisesRegex(M.Stop, "C-PSD"):
            self.build()

    def test_the_record_files(self):
        import tempfile
        rec = self.build()
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "o"
            M.write_record(d, rec)
            names = sorted(p.name for p in Path(d).iterdir())
            self.assertEqual(names, ["C_b_abs.csv", "C_b_tune_v1_units.csv", "V_F.csv", "blocks5d.json", "blocks5d.txt"])
            rows = (Path(d) / "C_b_abs.csv").read_text().splitlines()
            self.assertEqual(len(rows), 17)
            self.assertIn("B5D blocks:", (Path(d) / "blocks5d.txt").read_text())
            j = json.loads((Path(d) / "blocks5d.json").read_text())
            self.assertEqual(j["matrices_sha256"], {n: M.sha256_path(Path(d) / n) for n in names if n.endswith(".csv")})
        bad = json.loads(json.dumps(rec))
        bad["fluctuation"]["f_hat"]["R1"] = float("inf")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                M.write_record(Path(d) / "o", bad)
            self.assertEqual(list(Path(d).iterdir()), [])  # nothing written, not even the CSVs
        bad = json.loads(json.dumps(rec))
        bad["bias_block"]["C_b_abs"][0][0] = float("inf")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                M.write_record(Path(d) / "o", bad)
            self.assertEqual(list(Path(d).iterdir()), [])
        z = json.loads(json.dumps(rec))
        for v in z["bias_block"]["printed_against_C_b"].values():
            v["quad"] = None  # a rank-0 C_b: null, never Infinity
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "o"
            M.write_record(d, z)
            self.assertIn("n/a (C_b rank 0)", (Path(d) / "blocks5d.txt").read_text())
            rec2 = dict(rec)
            rec2["fluctuation"] = dict(rec["fluctuation"], V_F=None)
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "o"
            M.write_record(d, rec2)
            self.assertNotIn("V_F.csv", [p.name for p in Path(d).iterdir()])


    def test_the_mean_error_is_in_tune_v1_units_through_r(self):
        base = self.build()["bias_block"]["ll5d_toy_mean_error_tune_v1_units"]["g18/minus2"]["beta"]
        b, sig, R, sr, g = self.B.prepare(None, None, None)
        R = dict(R, F1_genie_v3_g18=np.full(N, 2.0))
        self.B.prepare = lambda *a: (b, sig, R, sr, g)
        rec = self.build()["bias_block"]["ll5d_toy_mean_error_tune_v1_units"]
        np.testing.assert_allclose(rec["g18/minus2"]["beta"], 2 * np.asarray(base), rtol=1e-12)
        orig = M.cells
        M.cells = lambda d, U, name, key="xsec_flat": orig(d, U, name, key) * (2.0 if key == "xtrue_flat" and "_central_" in name else 1.0)
        try:
            half = self.build()["bias_block"]["ll5d_toy_mean_error_tune_v1_units"]["ar23/all"]["beta"]
        finally:
            M.cells = orig
        np.testing.assert_allclose(half, np.asarray(rec["ar23/all"]["beta"]) / 2, rtol=1e-12)

    def test_a_truth_with_a_zero_cell_stops(self):
        orig = M.cells
        M.cells = lambda d, U, name, key="xsec_flat": orig(d, U, name, key) * (0.0 if key == "xtrue_flat" and "_central_" in name else 1.0)
        try:
            with self.assertRaisesRegex(M.Stop, "C-FIN.*cell integrals are not all positive"):
                self.build()
        finally:
            M.cells = orig

    def test_an_indefinite_d_stops(self):
        orig = M.drawn_block
        M.drawn_block = lambda *a: np.diag([2.0] * (N - 1) + [-1.0])
        try:
            with self.assertRaisesRegex(M.Stop, "C-PSD.*indefinite"):
                self.build()
        finally:
            M.drawn_block = orig

    def test_a_nan_bias_block_stops(self):
        orig = M.bias_block
        M.bias_block = lambda beta, Sigma: (np.full((N, N), np.nan), np.eye(N))
        try:
            with self.assertRaisesRegex(M.Stop, "C-PSD"):
                self.build()
        finally:
            M.bias_block = orig

    def test_a_nonfinite_secondary_factor_stops(self):
        orig_te, orig_ms = M.toy_errors, M.mode_spreads
        secondary = set()

        def te(d, U, t, rd, *a):
            E = orig_te(d, U, t, rd, *a)
            if rd == M.SECONDARY:
                secondary.add(id(E))
            return E
        M.toy_errors = te
        M.mode_spreads = lambda E, w, V: np.full(len(w), np.nan) if id(E) in secondary else orig_ms(E, w, V)
        try:
            with self.assertRaisesRegex(M.Stop, "C-FIN.*/all R1: the band factor"):
                self.build()
        finally:
            M.toy_errors, M.mode_spreads = orig_te, orig_ms

    def test_the_remaining_stops(self):
        for name, fake, pat in (
                ("bias_block", lambda beta, Sigma: (-np.eye(N), np.eye(N)), "C-PSD.*C_b is not positive semidefinite"),
                ("fhat", lambda ens, bands: {0: float("inf"), 1: 1.0, 2: 1.0}, "C-FIN.*band 1: f-hat"),
                ("against", lambda beta, C: {"quad": float("nan"), "fraction_outside_span": 0.0, "rank": 1}, "C-FIN.*quad is not finite"),
                ("band_traces", lambda *a: {"R1": {"toy": float("nan"), "reference": 1.0, "kept_modes": 4, "kept": True}},
                 "C-FIN.*band trace")):
            orig = getattr(M, name)
            setattr(M, name, fake)
            try:
                with self.assertRaisesRegex(M.Stop, pat):
                    self.build()
            finally:
                setattr(M, name, orig)

    def test_main_writes_the_record_and_says_so(self):
        import tempfile, io, contextlib
        rec = self.build()
        mods = {"s1_assemble": types.SimpleNamespace(), "ll5d": types.SimpleNamespace(),
                "ll5d_b": types.SimpleNamespace(Refusal=RuntimeError), "bsel_select": types.SimpleNamespace(Stop=RuntimeError)}
        saved = {k: sys.modules.get(k) for k in mods}
        sys.modules.update(mods)
        orig = M.build
        try:
            te = M.toy_errors
            M.toy_errors = lambda d, U, t, rd, *a: outlier(te(d, U, t, rd, *a))
            try:
                unres = orig(self.repo, self.ll5d, self.sa, self.ll5d_mod, self.ll5d_b, self.B)  # a real unresolved build
            finally:
                M.toy_errors = te
            self.assertTrue(unres["fluctuation"]["unresolved_stop"])
            for r, verdict, has_vf in ((rec, "COMPLETE", True), (unres, "UNRESOLVED: no V_F", False)):
                M.build = lambda *a, r=r: r
                with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(M.main(["--repo", d, "--ll5d", d, "--out", str(Path(d) / "o")]), 0)
                    self.assertEqual(json.loads(out.getvalue())["verdict"], verdict)
                    self.assertTrue((Path(d) / "o" / "blocks5d.json").exists())
                    self.assertEqual((Path(d) / "o" / "V_F.csv").exists(), has_vf)
                    self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ["o"])  # no partial directory left
        finally:
            M.build = orig
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    def test_c_leak_judges_arrays_by_size_and_numeric_strings(self):
        rec = self.build()
        ok = json.loads(json.dumps(rec))
        ok["bias_block"]["C_b_tune_v1_units"][0][1] = 1e-32  # roundoff in a relative matrix is not a leak
        ok["fluctuation"]["rows"] = [{"ok": 0.5}, {"n": 3}]
        ok["fluctuation"]["nested"] = [[{"a": 0.5}], [[0.1, 1e-35]]]  # deeper nesting is walked; a matrix by its max
        M.check_leak(ok)
        bad = json.loads(json.dumps(ok))
        bad["fluctuation"]["nested"] = [[{"a": 2e-39}]]
        with self.assertRaisesRegex(M.Stop, "C-LEAK.*nested/a"):
            M.check_leak(bad)
        bad = json.loads(json.dumps(rec))
        bad["bias_block"]["members"]["nominal"]["note"] = "2e-39"
        with self.assertRaisesRegex(M.Stop, "C-LEAK"):
            M.check_leak(bad)
        bad = json.loads(json.dumps(rec))
        bad["fluctuation"]["xs"] = {"g18": [3e-39, 1e-39]}
        with self.assertRaisesRegex(M.Stop, "C-LEAK"):
            M.check_leak(bad)
        bad = json.loads(json.dumps(rec))
        bad["fluctuation"]["rows"] = [{"ok": 0.5}, {"x": 2e-39}]  # a list of records is walked record by record
        with self.assertRaisesRegex(M.Stop, "C-LEAK.*rows/x"):
            M.check_leak(bad)
        bad = json.loads(json.dumps(rec))
        bad["bias_block"]["printed_against_C_b"]["W1"]["beta"] = [2e-39] + [0.01] * (N - 1)  # one absolute entry
        with self.assertRaisesRegex(M.Stop, "C-LEAK.*W1/beta"):
            M.check_leak(bad)

    def test_dimensional_invariance(self):
        """Scale every absolute input (U*xsec, U*xtrue, g_TuneV1 by k; C_e by k^2): every non-exempt number is unchanged
        and C_b,abs and V_F scale by k^2. Any absolute quantity in the record would move."""
        k = 7.0
        rec = self.build()
        oc, orr = M.cells, M.read_csv_matrix
        b, sig, R, sr, g = self.B.prepare(None, None, None)
        op = self.B.prepare
        M.cells = lambda d, U, name, key="xsec_flat": k * oc(d, U, name, key)
        M.read_csv_matrix = lambda q: k * k * orr(q)
        self.B.prepare = lambda *a: (b, sig, R, sr, {"mnvtune_v1": [k * x for x in g["mnvtune_v1"]]})
        try:
            rk = self.build()
        finally:
            M.cells, M.read_csv_matrix, self.B.prepare = oc, orr, op

        def cmp(x, y, path):
            if path in M.LEAK_EXEMPT:
                np.testing.assert_allclose(np.asarray(y, float), k * k * np.asarray(x, float), rtol=1e-9, atol=0)
            elif isinstance(x, dict):
                self.assertEqual(set(x), set(y))
                for key in x:
                    cmp(x[key], y[key], path + (key,))
            elif isinstance(x, (list, tuple)) and x and isinstance(x[0], (dict, list, tuple)):
                for u, v in zip(x, y):
                    cmp(u, v, path)
            elif isinstance(x, (list, tuple)) and any(isinstance(u, str) for u in x):
                self.assertEqual(x, y, "/".join(map(str, path)))
            elif isinstance(x, (list, tuple, float, int)) and not isinstance(x, bool):
                np.testing.assert_allclose(np.asarray(y, float), np.asarray(x, float), rtol=1e-9, atol=1e-300,
                                           err_msg="/".join(map(str, path)))
            else:
                self.assertEqual(x, y, "/".join(map(str, path)))
        cmp(rec, rk, ())

    def test_a_nan_d_stops_before_the_solver(self):
        orig = M.drawn_block
        M.drawn_block = lambda *a: np.full((N, N), np.nan)
        try:
            with self.assertRaisesRegex(M.Stop, "C-PSD.*not finite"):
                self.build()
        finally:
            M.drawn_block = orig

    def test_a_zero_spread_is_a_result_not_a_stop(self):
        orig = M.toy_errors
        M.toy_errors = lambda d, U, t, rd, *a: np.zeros_like(orig(d, U, t, rd, *a)) if rd == M.SECONDARY else orig(d, U, t, rd, *a)
        try:
            rec = self.build()
        finally:
            M.toy_errors = orig
        self.assertEqual(rec["fluctuation"]["per_ensemble"]["g18/all"]["R1"], 0.0)

    def test_a_nonfinite_c_b_abs_stops(self):
        b, sig, R, sr, g = self.B.prepare(None, None, None)
        self.B.prepare = lambda *a: (b, sig, R, sr, {"mnvtune_v1": [np.inf] * N})
        with self.assertRaisesRegex(M.Stop, "C-FIN.*C_b_abs"):
            self.build()

    def test_the_writer_never_replaces_or_creates_parents(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "o").mkdir()  # an empty directory that appeared after main's check
            with self.assertRaises(FileExistsError):
                M.write_files(Path(d) / "o", {"a.txt": b"x"})
            self.assertEqual(list((Path(d) / "o").iterdir()), [])
            with self.assertRaises(FileNotFoundError):
                M.write_files(Path(d) / "p" / "o", {"a.txt": b"x"})
            self.assertEqual(sorted(q.name for q in Path(d).iterdir()), ["o"])

    def test_a_failed_write_leaves_nothing(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(OSError):
                M.write_files(Path(d) / "o", {"a.txt": b"x", "missing/b.txt": b"y"})
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_a_nonfinite_v_f_stops(self):
        orig = M.fluctuation_block
        M.fluctuation_block = lambda C_e, trig: (np.full((N, N), np.nan), np.eye(N))
        try:
            with self.assertRaisesRegex(M.Stop, "C-FIN.*V_F"):
                self.build()
        finally:
            M.fluctuation_block = orig

    def test_all_bands_dropped_gives_no_v_f(self):
        orig = M.bands_kept
        M.bands_kept = lambda w: ([], [(a, b, []) for a, b in M.BANDS])
        try:
            rec = self.build()
        finally:
            M.bands_kept = orig
        fl = rec["fluctuation"]
        self.assertTrue(fl["unresolved_stop"])
        self.assertIsNone(fl["V_F"])
        self.assertEqual(set(fl["f_hat"].values()), {None})

    def test_c_leak(self):
        rec = self.build()
        M.check_leak(rec)  # C_b_abs (absolute) is exempt
        self.assertLess(abs(np.asarray(rec["bias_block"]["C_b_abs"])).max(), 1e-60)
        bad = json.loads(json.dumps(rec))
        bad["bias_block"]["printed_against_C_b"]["W1"]["x_T"] = [2e-39] * N
        with self.assertRaisesRegex(M.Stop, "C-LEAK"):
            M.check_leak(bad)
        bad = json.loads(json.dumps(rec))
        bad["fluctuation"]["L"] = [[3e-39] * N] * N  # only V_F and C_b_abs are exempt
        with self.assertRaisesRegex(M.Stop, "C-LEAK"):
            M.check_leak(bad)
        ok = json.loads(json.dumps(rec))
        ok["fluctuation"]["V_F"] = [[3e-79] * N] * N
        M.check_leak(ok)

    def test_main_maps_every_refusal_to_stop_5(self):
        import tempfile, io, contextlib

        class BStop(RuntimeError):
            pass

        class Refusal(RuntimeError):
            pass
        mods = {"s1_assemble": types.SimpleNamespace(), "ll5d": types.SimpleNamespace(),
                "ll5d_b": types.SimpleNamespace(Refusal=Refusal), "bsel_select": types.SimpleNamespace(Stop=BStop)}
        saved = {k: sys.modules.get(k) for k in mods}
        sys.modules.update(mods)
        orig = M.build
        try:
            mods["ll5d"].Refusal = type("LL5DRefusal", (RuntimeError,), {})
            for exc in (M.Stop("C-X", "y"), BStop("b"), Refusal("r"), mods["ll5d"].Refusal("l"), OSError("o"), SystemExit(3),
                        np.linalg.LinAlgError("e"), ValueError("v")):
                def raiser(*a, exc=exc):
                    raise exc
                M.build = raiser
                with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(M.main(["--repo", d, "--ll5d", d, "--out", str(Path(d) / "o")]), 5)
                    self.assertFalse((Path(d) / "o").exists())
                    self.assertIn("STOP", err.getvalue())

            def boom(*a):
                raise TypeError("a bug is not a STOP")
            M.build = boom
            with tempfile.TemporaryDirectory() as d, self.assertRaises(TypeError):
                M.main(["--repo", d, "--ll5d", d, "--out", str(Path(d) / "o")])
            rec = orig(self.repo, self.ll5d, self.sa, self.ll5d_mod, self.ll5d_b, self.B)
            rec["bias_block"]["members"]["nominal"]["leak"] = 1e-39
            M.build = lambda *a: rec
            with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(M.main(["--repo", d, "--ll5d", d, "--out", str(Path(d) / "o")]), 5)
                self.assertFalse((Path(d) / "o").exists())
        finally:
            M.build = orig
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    def test_toy_errors_refuses_an_incomplete_seed_set(self):
        (self.ll5d / "ll5d_g18_toy_all_101.npz").unlink()
        with self.assertRaisesRegex(M.Stop, "C-LL5D"):
            M.toy_errors(self.ll5d, np.eye(N), "g18", "all", self.ll5d_mod, self.ll5d_b)
        E = M.toy_errors(self.ll5d, np.eye(N), "ar23", "minus2", self.ll5d_mod, self.ll5d_b)
        self.assertEqual(E.shape, (40, N))


    def test_a_wrong_n_eff_with_the_right_sum_stops(self):
        self.sa.flux_weights = lambda p: np.array([1.25, 1.25, 1.25, 1.25])  # sum 5 as S1's, n_eff 4 not 25/7
        with self.assertRaisesRegex(M.Stop, "C-FLUX"):
            self.build()

    def test_drawn_block_is_flux_weighted_bands_plus_stat(self):
        U = np.eye(N)
        w = np.array([1.0, 2.0, 1.0, 1.0])
        D = M.drawn_block(self.ll5d, U, "g18", "all", w, self.sa, self.ll5d_b)

        def load(n):
            with np.load(self.ll5d / n) as z:
                return np.asarray(z["xsec_flat"], float)
        want = np.zeros((N, N))
        for band, n in self.sa.EXPECT.items():
            X = np.array([load(f"ll5d_g18_block_{band}_{i}.npz") for i in range(n)])
            ww = w if band == "Flux" else np.ones(n)
            mu = (ww[:, None] * X).sum(0) / ww.sum()
            want += ((X - mu).T * ww) @ (X - mu) / ww.sum()
        Rr = np.array([load(f"ll5d_g18_stat_{r}.npz") for r in self.ll5d_b.STAT_REPLICAS])
        want += np.cov(Rr, rowvar=False, ddof=1)
        self.assertTrue(np.allclose(D, want, rtol=1e-12, atol=0))

    def test_toy_errors_are_unfold_minus_truth(self):
        E = M.toy_errors(self.ll5d, np.eye(N), "g18", "minus2", self.ll5d_mod, self.ll5d_b)
        with np.load(self.ll5d / "ll5d_g18_toy_minus2_100.npz") as z:
            self.assertTrue(np.allclose(E[0], z["xsec_flat"] - z["xtrue_flat"], rtol=0, atol=0))

    def test_sigma_and_beta_are_in_tune_v1_units(self):
        b, sig, R, sr, g = self.B.prepare(None, None, None)
        R = {t: np.full(N, 1.5) for t in R}
        self.B.prepare = lambda *a: (b, sig, R, sr, g)
        rec = self.build()
        with np.load(self.repo / M.SELECTION_INPUTS / "fd_f0b_experiments.npz") as z:
            raw = sum(np.outer(b[t] * 1.5, b[t] * 1.5) - 2.25 * np.cov(z[f"r_{t}"], rowvar=False, ddof=1) / z[f"r_{t}"].shape[0]
                      for t in M.FAMILY)
        self.assertTrue(np.allclose(rec["bias_block"]["C_b_tune_v1_units"], M.positive_part(raw), rtol=1e-10, atol=1e-18))

    def test_a_changed_product_stops(self):
        q = self.ll5d / "ll5d_g18_block_MaRES_0.npz"
        np.savez(q, xsec_flat=np.zeros(N), xtrue_flat=np.ones(N))
        with self.assertRaisesRegex(M.Stop, "C-PIN"):
            self.build()

    def test_a_missing_toy_stops(self):
        (self.ll5d / "ll5d_ar23_toy_minus2_205.npz").unlink()
        with self.assertRaises(M.Stop):
            self.build()

    def test_a_wrong_flux_weight_stops(self):
        self.sa.flux_weights = lambda p: np.array([1.0, 2.0, 1.0, 1.1])
        with self.assertRaisesRegex(M.Stop, "C-FLUX"):
            self.build()

    def test_a_seed_mismatch_stops(self):
        q = self.ll5d / "ll5d_ar23_seed_T.npz"
        np.savez(q, xsec_flat=np.full(N, 1.0 + 1e-12), xtrue_flat=np.ones(N))
        lst = self.repo / f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"
        lst.write_text("\n".join(l if not l.endswith("/ll5d_ar23_seed_T.npz") else
                                 "\t".join([l.split("\t")[0], M.sha256_path(q), l.split("\t")[2]])
                                 for l in lst.read_text().splitlines()) + "\n")
        M.COMMITTED[f"{M.FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"] = M.sha256_path(lst)
        with self.assertRaises(M.Stop):  # C-LL5D (the digest moves) or C-SEED
            self.build()


class Pins(unittest.TestCase):
    def test_manifest_groups_and_the_1654_count(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            p = repo / M.FD / "receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"
            p.parent.mkdir(parents=True)
            p.write_text("toys\t" + "a" * 64 + "\t/x/ll5d_g18_toy_minus2_1.npz\nsidecars\t" + "b" * 64 + "\t/x/s.json\n"
                         "extras\t" + "c" * 64 + "\t/x/ll5d_data_control_Flux_0.npz\nnull_roles\t" + "d" * 64 + "\t/x/ll5d_g18_central_T.npz\n\n")
            pins = M.manifest_pins(repo)
            self.assertEqual(pins, {"ll5d_g18_toy_minus2_1.npz": "a" * 64, "ll5d_g18_central_T.npz": "d" * 64})
            with self.assertRaisesRegex(M.Stop, "not 1654"):
                M.check_ll5d_pins(repo, repo, None)

    def test_the_real_manifest_gives_1654(self):
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual(len(M.manifest_pins(repo)), 1654)

    def test_check_ll5d_pins_on_a_full_tiny_set(self):
        import tempfile, types
        with tempfile.TemporaryDirectory() as d:
            repo, ll = Path(d) / "r", Path(d) / "l"
            ll.mkdir()
            rows = []
            for i in range(1654):
                q = ll / f"ll5d_g18_toy_minus2_{i}.npz"
                q.write_bytes(str(i).encode())
                rows.append(f"toys\t{M.sha256_path(q)}\t/x/{q.name}")
            (ll / M.CONSTRAINT_NAME).write_text("Flux 0 1.0\n")
            p = repo / M.FD / "receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv"
            p.parent.mkdir(parents=True)
            p.write_text("\n".join(rows) + "\n")
            sa = types.SimpleNamespace(CONSTRAINT_SHA256=M.sha256_path(ll / M.CONSTRAINT_NAME))
            M.check_ll5d_pins(repo, ll, sa)
            (ll / "ll5d_g18_toy_minus2_7.npz").write_bytes(b"x")
            with self.assertRaisesRegex(M.Stop, "is not its pin"):
                M.check_ll5d_pins(repo, ll, sa)
            (ll / "ll5d_g18_toy_minus2_7.npz").write_bytes(b"7")
            sa.CONSTRAINT_SHA256 = "0" * 64
            with self.assertRaisesRegex(M.Stop, "constraint"):
                M.check_ll5d_pins(repo, ll, sa)
            (ll / "ll5d_extra.npz").write_bytes(b"e")
            with self.assertRaisesRegex(M.Stop, "differs"):
                M.check_ll5d_pins(repo, ll, sa)

    def test_main_refuses_an_existing_output(self):
        import tempfile, io, contextlib
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(M.main(["--repo", d, "--ll5d", d, "--out", d]), 5)

    def test_read_csv_matrix_shape(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            q = Path(d) / "m.csv"
            q.write_text("cell,R00\nR00,1.0\n")
            with self.assertRaisesRegex(M.Stop, "16 x 16"):
                M.read_csv_matrix(q)


if __name__ == "__main__":
    unittest.main()
