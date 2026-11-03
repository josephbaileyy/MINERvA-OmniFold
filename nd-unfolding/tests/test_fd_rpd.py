"""Controls for the run-period diagnosis (FD-RPD-DECLARATION.md part 1 revision 4; part 2): fd_rpd_inputs.py,
fd_rpd.py, the committed tables and the submit stages, on synthetic inputs and the committed H2 definition.

* Each refusing control refuses on a one-entry defect, with nothing written.
* Each deciding rule decides in both directions.
* R1's pattern rule returns exactly one outcome for every class assignment; FREE and CARRIES are disjoint for a
  resolved playlist; R2's partitions are counted and its statistic is recomputed by explicit loops.
* Nothing written carries f or an absolute cell value."""
import contextlib
import io
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
import fd_ct_period_inputs as pi  # noqa: E402
import fd_ct_readers as ct  # noqa: E402
import fd_rpd as rp  # noqa: E402
import fd_rpd_inputs as ri  # noqa: E402
import s1_assemble as sa  # noqa: E402
import test_fd_ct_readers as TR  # noqa: E402

REPO = ND.parent
DEFINITION = ND / "pv-ladder/readouts/h2_definition.json"
RELR = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd"
digest = TR.digest
PL = ri.PLAYLISTS
E_APPROX = np.array([.0847, .0176, .0405, .1359, .0972, .1575, .1311, .0127, .1507, .1001, .0280, .0439])
E_APPROX = E_APPROX / E_APPROX.sum()


def quiet(fn, *a, **k):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = fn(*a, **k)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue() + out.getvalue()


try:
    import ROOT  # noqa: F401
    HAVE_ROOT = True
except Exception:
    HAVE_ROOT = False


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="rpd-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


# ================================================================ definitions


class Definitions(unittest.TestCase):
    def test_replica_seeds_are_disjoint_and_not_5bs(self):
        allseeds = [s for X in PL for s in rp.REP[X]]
        self.assertEqual(len(allseeds), 360)
        self.assertEqual(len(set(allseeds)), 360)
        fiveb = {s for v in rp.cp.BOOT.values() for s in v}
        self.assertFalse(set(allseeds) & fiveb)
        self.assertEqual(rp.REP["1A"][:2], (4101, 4102))
        self.assertEqual(rp.REP["1P"][-1], 5230)

    def test_baseline_pins_are_stage_bs_records(self):
        import re
        s = (REPO / "docs/orchestration/state/2d-closeout/stageB/evidence/verify-c04/verify_c04.json").read_text()
        rec = {m.group(1): m.group(2) for m in re.finditer(
            r'"/pscratch[^"]*baseline_flux/(runEventLoop(?:MC|Data)_1[A-P]\.root)": "([0-9a-f]{64})"', s)}
        self.assertEqual(rec, ri.BASELINE)

    def test_the_production_flux_pin_is_the_2d_records(self):
        s = (REPO / "docs/orchestration/state/2d-closeout/period-unfold-20261014/scripts/periods.py").read_text()
        self.assertIn(ri.PROD_FLUX, s)

    def test_stage_sources_are_part_1s_table(self):
        src = ri.stage_sources()
        kinds = {}
        for name in src:
            kinds[name.split("/")[0]] = kinds.get(name.split("/")[0], 0) + 1
        self.assertEqual(kinds, {"zero": 12, "baseline": 25, "5b": 33 + 3 + 2, "mp1": 2, "s1": 1, "cresp": 1})
        inv = ri.inventory_pins()
        for name, (path, sha) in src.items():
            if name.startswith("5b/unf/") or name.startswith("5b/truth/"):
                self.assertEqual(inv[path], sha, name)
        self.assertEqual(src["mp1/lat_zero.npz"][1], pi.MP1_ZERO["lat_npz"])
        self.assertEqual(src["s1/s1_assembly.npz"][1], ct.PINS["s1_npz"])
        self.assertEqual(src["cresp/cresp.npz"][1], ct.PINS["cresp"])
        self.assertEqual(src["5b/unf/PC/5b_PC_b-_j-.npz"][1][:8], "e0594420")
        self.assertIn("5b/unf/PC/5b_PC_b3001_j-.npz", src)
        for pl in PL:
            self.assertEqual(src[f"zero/runEventLoopOmniFold_5D_{pl}_zero.root"][1], pi.ZERO_LOOPS[pl])
        self.assertTrue(all(p.startswith("/pscratch/") for p, _ in src.values()))

    def test_the_groupings(self):
        self.assertEqual(rp.FLUX_PI, (("PA", tuple(PL[:6])), ("PB", tuple(PL[6:9])), ("PC", tuple(PL[9:]))))
        self.assertEqual(sorted(m for _, ms in rp.ERA_PI for m in ms), sorted(PL))

    def test_n0_thresholds_are_t29_quantiles(self):
        from scipy import stats
        self.assertAlmostEqual(rp.N0_T_CELL, stats.t.ppf(1 - 0.01 / 16 / 2, 29), places=3)
        self.assertAlmostEqual(rp.N0_T_STEP, stats.t.ppf(1 - 0.01 / 2, 29), places=3)

    def test_nu_and_interval_reproduce_the_5d_label(self):
        nu = rp.nu_eff(np.array([0.5334, 0.2945, 0.1721]))
        self.assertAlmostEqual(nu, 1.8244, places=3)
        lo, hi = rp.sigma_interval(nu)
        self.assertEqual((round(lo, 2), round(hi, 2)), (0.73, 2.56))
        self.assertAlmostEqual(rp.nu_eff(E_APPROX), 7.98, places=1)

    def test_the_calibration_gate(self):
        self.assertAlmostEqual(rp.r2_gate_threshold(), 0.0646, places=4)


# ================================================================ fd_rpd_inputs: stage


class Stage(Tmp):
    def sources(self, n=3):
        src = {}
        for i in range(n):
            p = self.tmp / "src" / f"f{i}.bin"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(os.urandom(100 + i))
            src[f"d{i}/f{i}.bin"] = (str(p), digest(p))
        return src

    def run_stage(self, src):
        with mock.patch.object(ri, "stage_sources", lambda deploy=None: src):
            return quiet(ri.main, ["stage", "--r", str(self.tmp / "R"), "--allow-no-noatime"])

    def test_copies_each_file_at_its_pin_and_records_atime(self):
        src = self.sources()
        rc, _, err = self.run_stage(src)
        self.assertEqual(rc, 0, err)
        rec = json.loads((self.tmp / "R/staged/STAGED.json").read_text())
        self.assertEqual(rec["n_files"], 3)
        for name, (p, sha) in src.items():
            self.assertEqual(digest(self.tmp / "R/staged" / name), sha)
            self.assertIn("source_atime_before", rec["files"][name])

    def test_refuses_a_source_at_another_digest_and_keeps_no_copy(self):
        src = self.sources()
        name = sorted(src)[1]
        src[name] = (src[name][0], "0" * 64)
        rc, _, err = self.run_stage(src)
        self.assertEqual(rc, 4, err)
        self.assertFalse((self.tmp / "R/staged" / name).exists())
        self.assertFalse((self.tmp / "R/staged/STAGED.json").exists())

    def test_refuses_an_existing_staging_directory(self):
        (self.tmp / "R/staged").mkdir(parents=True)
        rc, _, _ = self.run_stage(self.sources())
        self.assertEqual(rc, 3)

    def test_refuses_a_missing_source_before_copying(self):
        src = self.sources()
        src["x/missing"] = (str(self.tmp / "nope"), "1" * 64)
        rc, _, err = self.run_stage(src)
        self.assertEqual(rc, 4)
        self.assertFalse((self.tmp / "R/staged").exists())

    def test_a_staged_copy_changed_afterwards_refuses(self):
        src = self.sources()
        self.run_stage(src)
        name = sorted(src)[0]
        p = self.tmp / "R/staged" / name
        p.chmod(0o640)
        p.write_bytes(b"changed")
        with self.assertRaises(ri.Refuse):
            ri.staged(self.tmp / "R", name)

    def test_the_copy_opens_with_o_noatime_where_the_platform_has_it(self):
        seen = []
        real = os.open

        def spy(path, flags, *a):
            seen.append(flags)
            return real(path, flags & ~getattr(os, "O_NOATIME", 0), *a)
        src = self.sources(1)
        with mock.patch.object(ri.os, "open", spy), mock.patch.object(ri.os, "O_NOATIME", 0o1000000, create=True):
            self.run_stage(src)
        self.assertTrue(seen and all(f & 0o1000000 for f in seen))


# ================================================================ fd_rpd_inputs: flux arithmetic and F1


def fake_flux(rng, pot_data, pot_mc, n=14, phi=None):
    phi = rng.uniform(5e-4, 7e-4) if phi is None else phi
    return {"edges": list(np.linspace(0, 4.5, n + 1)), "contents": [phi] * n,
            "errors": list(rng.uniform(1e-6, 2e-6, n)), "pot_data": pot_data, "pot_mc": pot_mc}


class Flux(unittest.TestCase):
    def test_combine_is_the_combiners_arithmetic(self):
        rng = np.random.default_rng(1)
        per = [{"contents": rng.random(14), "errors": rng.random(14), "pot_data": rng.random() * 1e20,
                "pot_mc": rng.random() * 1e21} for _ in range(6)]
        c = ri.combine(per)
        w = np.array([p["pot_data"] for p in per])
        want = sum(p["contents"] * p["pot_data"] for p in per) / w.sum()
        werr = np.sqrt(sum((p["errors"] * p["pot_data"]) ** 2 for p in per)) / w.sum()
        np.testing.assert_allclose(c["contents"], want, rtol=1e-15)
        np.testing.assert_allclose(c["errors"], werr, rtol=1e-15)
        self.assertAlmostEqual(c["pot_mc"], sum(p["pot_mc"] for p in per), delta=1e6)

    def build(self, rng):
        per = {pl: fake_flux(rng, rng.uniform(1e19, 2e20), rng.uniform(1e20, 1e21)) for pl in PL}
        periods = {}
        for k, pls in ri.PERIODS.items():
            c = ri.combine([{**per[p], "contents": np.asarray(per[p]["contents"]),
                             "errors": np.asarray(per[p]["errors"])} for p in pls])
            periods[k] = {"edges": per[pls[0]]["edges"], "contents": list(c["contents"]),
                          "errors": list(c["errors"]), "pot_data": c["pot_data"], "pot_mc": c["pot_mc"]}
        c = ri.combine([{**per[p], "contents": np.asarray(per[p]["contents"]), "errors": np.asarray(per[p]["errors"])}
                        for p in PL])
        prod = {"edges": per["1A"]["edges"], "contents": list(c["contents"]), "errors": list(c["errors"]),
                "pot_data": c["pot_data"], "pot_mc": c["pot_mc"]}
        return per, periods, prod

    def test_f1_passes_consistent_files_and_fails_a_one_bin_defect_in_each(self):
        per, periods, prod = self.build(np.random.default_rng(2))
        self.assertTrue(all(v["pass"] for v in ri.f1_decide(per, periods, prod).values()))
        for target in ("PB", "ALL"):
            bad_periods = json.loads(json.dumps(periods))
            bad_prod = json.loads(json.dumps(prod))
            ref = bad_prod if target == "ALL" else bad_periods[target]
            ref["contents"][3] *= 1 + 1e-11
            out = ri.f1_decide(per, bad_periods, bad_prod)
            self.assertFalse(out[target]["pass"], target)
        bad = json.loads(json.dumps(periods))
        bad["PA"]["pot_data"] *= 1 + 1e-11
        self.assertFalse(ri.f1_decide(per, bad, prod)["PA"]["pass"])

    def test_f1_passes_within_its_tolerance(self):
        per, periods, prod = self.build(np.random.default_rng(3))
        periods["PC"]["contents"][0] *= 1 + 5e-13
        self.assertTrue(ri.f1_decide(per, periods, prod)["PC"]["pass"])

    def test_exposure_shares_are_pot_times_flux(self):
        rng = np.random.default_rng(4)
        per = {pl: fake_flux(rng, rng.uniform(1e19, 2e20), 1e21) for pl in PL}
        e, spread = ri.exposure_shares(per)
        raw = {pl: per[pl]["pot_data"] * per[pl]["contents"][0] for pl in PL}
        for pl in PL:
            self.assertAlmostEqual(e[pl], raw[pl] / sum(raw.values()), places=14)
        self.assertLessEqual(spread, 1e-15)

    @unittest.skipUnless(HAVE_ROOT, "needs ROOT")
    def test_the_combiner_is_loaded_unchanged_with_its_base_pointed_at_the_staged_copies(self):
        cf = ri.load_combiner(REPO, Path("/staged/baseline"))
        self.assertEqual(cf.BASE, "/staged/baseline")


# ================================================================ fd_rpd_inputs: check


def nn_npz(path: Path, seed=0, n=50, **over):
    rng = np.random.default_rng(seed)
    arr = {"axes": np.array(["eavail", "q3", "W"], dtype=object),
           "MCgen": rng.normal(size=(n, 5)).astype(np.float32), "MCreco": rng.normal(size=(n, 5)).astype(np.float32),
           "measured": rng.normal(size=(20, 5)).astype(np.float32), "pass_reco": rng.random(n) > 0.2,
           "pass_truth": rng.random(n) > 0.1, "w_truth": rng.random(n), "w_reco": rng.random(n),
           "measured_weights": rng.random(20), "denom_nd": rng.random((2, 2, 2, 2, 2)),
           "flux": np.full(14, 6.2e-4), "data_pot": 1.0e20, "n_nucleons": 3.2e30,
           **{f"edges_{i}": np.linspace(-3, 3, 3) for i in range(5)}, "nedges": 5}
    arr.update(over)
    np.savez_compressed(path, **arr)
    return path


def write_staged(R: Path, files: dict):
    """A staging record over files already under R/staged: name -> path."""
    rec = {"schema": "fd-rpd-staged/1", "n_files": len(files),
           "files": {n: {"sha256": digest(p)} for n, p in files.items()}}
    (R / "staged").mkdir(parents=True, exist_ok=True)
    (R / "staged/STAGED.json").write_text(json.dumps(rec))


class Check(Tmp):
    X = "1G"

    def build(self, lat_over=None, bkg_meta=None, flux_contents=None, f_pot=1.0e20):
        R = self.R = self.tmp / "R"
        X = self.X
        loop = R / f"staged/zero/runEventLoopOmniFold_5D_{X}_zero.root"
        loop.parent.mkdir(parents=True)
        loop.write_bytes(b"loop " + X.encode())
        write_staged(R, {f"zero/runEventLoopOmniFold_5D_{X}_zero.root": loop})
        self.loop = loop
        p = {k: R / v for k, v in ri.playlist_paths(X).items()}
        for d in ("flux", "dumps"):
            (R / d).mkdir(exist_ok=True)
        p["flux"].write_bytes(b"flux " + X.encode())
        F1 = {"schema": "fd-rpd-flux/1", "verdict": "PASS",
              "files": {X: [str(p["flux"]), digest(p["flux"])]},
              "per_playlist": {X: {"contents": flux_contents or [6.2e-4] * 14, "pot_data": f_pot}},
              "exposure_share": {}}
        (R / "flux/F1.json").write_text(json.dumps(F1))
        nn_npz(p["nn"])
        nn_npz(p["lat"], **(lat_over or {}))
        meta = bkg_meta or {"npz_sha256": digest(p["lat"]), "omnifile": str(loop)}
        np.savez_compressed(p["bkg"], bkg_reco=np.zeros((3, 5)), bkg_w=np.ones(3), bkg_nd=np.zeros((2,) * 5),
                            meta=json.dumps(meta))
        self.p = p
        return ["check", "--r", str(R), "--playlist", X]

    def patches(self, pots=(1.0e20, 4.0e20)):
        def run(cmd, *a, **k):
            self.truth_cmd = cmd
            Path(cmd[cmd.index("--out") + 1]).write_bytes(b"truth")
            return subprocess.CompletedProcess(cmd, 0)
        return [mock.patch.dict(pi.ZERO_LOOPS, {self.X: digest(self.loop)}),
                mock.patch.object(ri, "loop_pots", lambda p: pots), mock.patch.object(ri.subprocess, "run", run)]

    def go(self, argv, patches):
        with contextlib.ExitStack() as st:
            for q in patches:
                st.enter_context(q)
            return quiet(ri.main, argv)

    def refuses(self, argv, msg, rc=5, patches=None):
        r, _, err = self.go(argv, patches or self.patches())
        self.assertEqual(r, rc, err)
        self.assertIn(msg, err)
        self.assertFalse(self.p["receipt"].exists())

    def test_a_consistent_playlist_passes_records_mc_pot_and_writes_its_truth(self):
        argv = self.build()
        rc, _, err = self.go(argv, self.patches())
        self.assertEqual(rc, 0, err)
        rec = json.loads(self.p["receipt"].read_text())
        self.assertEqual((rec["data_pot"], rec["mc_pot"]), (1.0e20, 4.0e20))
        self.assertEqual(rec["pot_scale"], 0.25)
        self.assertEqual(rec["files"]["loop"], [str(self.loop), digest(self.loop)])
        self.assertEqual(Path(self.truth_cmd[1]).name, "s5p_mc_truth_pred.py")

    def test_refuses_a_loop_that_is_not_the_pinned_one(self):
        argv = self.build()
        ps = self.patches()
        ps[0] = mock.patch.dict(pi.ZERO_LOOPS, {self.X: "0" * 64})
        self.refuses(argv, "not its pinned zero loop", rc=4, patches=ps)

    def test_refuses_a_flux_file_that_is_not_f1s(self):
        argv = self.build()
        self.p["flux"].write_bytes(b"another")
        self.refuses(argv, f"{self.X} flux file", rc=4)

    def test_refuses_a_lateral_npz_that_is_not_the_nn_dump(self):
        argv = self.build(lat_over={"w_reco": np.zeros(50)})
        self.refuses(argv, "'w_reco'")

    def test_refuses_a_background_dump_of_another_npz_or_loop(self):
        argv = self.build(bkg_meta={"npz_sha256": "0" * 64, "omnifile": "x"})
        self.refuses(argv, "background dump does not name")

    def test_refuses_an_npz_flux_that_is_not_the_playlists_flux(self):
        argv = self.build(flux_contents=[6.2e-4 * (1 + 1e-11)] * 14)
        self.refuses(argv, "flux key")

    def test_refuses_data_pots_that_disagree(self):
        argv = self.build(f_pot=1.0e20 * (1 + 1e-11))
        self.refuses(argv, "data POT")
        argv = self.build_again()
        self.refuses(argv, "data POT", patches=self.patches(pots=(1.0e20 * (1 + 1e-11), 4e20)))

    def build_again(self):
        shutil.rmtree(self.tmp / "R")
        return self.build()

    def test_refuses_without_f1s_pass(self):
        argv = self.build()
        rec = json.loads((self.R / "flux/F1.json").read_text())
        rec["verdict"] = "FAIL"
        (self.R / "flux/F1.json").write_text(json.dumps(rec))
        self.refuses(argv, "F1 did not record a PASS")

    def test_refuses_to_overwrite(self):
        argv = self.build()
        self.p["receipt"].parent.mkdir(parents=True, exist_ok=True)
        self.p["receipt"].write_text("{}")
        r, _, _ = self.go(argv, self.patches())
        self.assertEqual(r, 3)


# ================================================================ fd_rpd_inputs: N0


def lat_all(rng, n_sig=4000, n_data=3000, n_bkg=800):
    edges = [np.linspace(-3, 3, 4) for _ in range(5)]
    mc = rng.normal(size=(n_sig, 5)).astype(np.float32)
    z = {"axes": np.array(["eavail", "q3", "W"], dtype=object), "MCgen": mc,
         "MCreco": (mc + rng.normal(0, .3, mc.shape)).astype(np.float32),
         "measured": rng.normal(size=(n_data, 5)).astype(np.float32), "pass_reco": rng.random(n_sig) > 0.2,
         "pass_truth": rng.random(n_sig) > 0.1, "w_truth": rng.uniform(0.5, 1.5, n_sig) * 0.3,
         "w_reco": rng.uniform(0.5, 1.5, n_sig) * 0.3, "measured_weights": rng.random(n_data),
         "flux": np.full(14, 6.2e-4), "data_pot": 1.0e21, "n_nucleons": 3.2e30,
         **{f"edges_{i}": e for i, e in enumerate(edges)}, "nedges": 5}
    o = ri.truth_sum(z["MCgen"], z["pass_truth"], z["w_truth"], edges)
    z["denom_nd"] = o * 1.4 + 0.5
    b = {"bkg_reco": rng.normal(size=(n_bkg, 5)), "bkg_w": rng.uniform(0.1, 0.3, n_bkg)}
    b["bkg_nd"] = ri.histnd_counts([b["bkg_reco"][:, i] for i in range(5)], b["bkg_w"], edges)
    return z, b


class N0(Tmp):
    def test_a_partition_is_a_partition_with_weights_unchanged_and_completeness_kept(self):
        rng = np.random.default_rng(5)
        z, b = lat_all(rng)
        npzs, bkgs, asg = ri.n0_partition(z, b, E_APPROX, 123)
        edges = [z[f"edges_{i}"] for i in range(5)]
        o_all = ri.truth_sum(z["MCgen"], z["pass_truth"], z["w_truth"], edges)
        for key, tree in (("MCgen", "signal"), ("w_truth", "signal"), ("measured", "data")):
            back = np.empty_like(z[key])
            for k in range(12):
                back[asg[tree] == k] = npzs[k][key]
            self.assertTrue(np.array_equal(back, z[key]), key)
        self.assertAlmostEqual(sum(x["data_pot"] for x in npzs) / z["data_pot"], 1.0, places=12)
        np.testing.assert_allclose(sum(x["denom_nd"] for x in npzs), z["denom_nd"], rtol=1e-9)
        np.testing.assert_allclose(sum(x["bkg_nd"] for x in bkgs), b["bkg_nd"], rtol=1e-9)
        for k in range(12):
            o_k = ri.truth_sum(npzs[k]["MCgen"], npzs[k]["pass_truth"], npzs[k]["w_truth"], edges)
            pos = o_k > 0
            np.testing.assert_allclose((o_k / npzs[k]["denom_nd"])[pos], (o_all / z["denom_nd"])[pos], rtol=1e-12)
            for g in ri.GLOBAL_KEYS:
                self.assertTrue(np.array_equal(npzs[k][g], z[g]))

    def test_the_draw_is_fixed_by_the_seed(self):
        rng = np.random.default_rng(6)
        z, b = lat_all(rng)
        a1 = ri.n0_partition(z, b, E_APPROX, 7)[2]
        a2 = ri.n0_partition(z, b, E_APPROX, 7)[2]
        a3 = ri.n0_partition(z, b, E_APPROX, 8)[2]
        self.assertTrue(all(np.array_equal(a1[k], a2[k]) for k in a1))
        self.assertFalse(np.array_equal(a1["data"], a3["data"]))

    def test_a_scaled_denominator_would_break_the_completeness_that_the_ratio_keeps(self):
        rng = np.random.default_rng(9)
        z, b = lat_all(rng, n_sig=600)
        npzs, _, _ = ri.n0_partition(z, b, E_APPROX, 3)
        edges = [z[f"edges_{i}"] for i in range(5)]
        k = 7   # the 1L analogue
        o_k = ri.truth_sum(npzs[k]["MCgen"], npzs[k]["pass_truth"], npzs[k]["w_truth"], edges)
        o_all = ri.truth_sum(z["MCgen"], z["pass_truth"], z["w_truth"], edges)
        pos = o_k > 0
        scaled = (o_k / (E_APPROX[k] * z["denom_nd"]))[pos]
        self.assertFalse(np.allclose(scaled, (o_all / z["denom_nd"])[pos], rtol=1e-6))


# ================================================================ fd_rpd_inputs: unfold


class Unfold(Tmp):
    def receipt_playlist(self, X="1A", schema="fd-rpd-inputs/1"):
        R = self.tmp / "R"
        lat, bkg = R / "dumps/lat.npz", R / "dumps/bkg.npz"
        lat.parent.mkdir(parents=True)
        lat.write_bytes(b"lat")
        bkg.write_bytes(b"bkg")
        rp_ = R / ri.playlist_paths(X)["receipt"]
        rp_.parent.mkdir(parents=True)
        rp_.write_text(json.dumps({"schema": schema, "playlist": X,
                                   "files": {"lat_npz": [str(lat), digest(lat)], "lat_bkg": [str(bkg), digest(bkg)]}}))
        return R, lat, bkg

    def fake(self, write=True):
        calls = []

        def run(cmd, *a, **k):
            calls.append(cmd)
            if write:
                out = Path(cmd[cmd.index("--out") + 1])
                out.mkdir(parents=True, exist_ok=True)
                pairs = [x for x in cmd if x.startswith("--pairs=")][0].split("=")[1]
                b = pairs.split(":")[0]
                (out / f"{cmd[cmd.index('--tag') + 1]}_b{b}_j-.npz").write_bytes(b"u")
            return subprocess.CompletedProcess(cmd, 0)
        return calls, mock.patch.object(ri.subprocess, "run", run)

    def test_a_playlist_unfold_runs_s5p_numerics_as_declared(self):
        R, lat, bkg = self.receipt_playlist()
        calls, p = self.fake()
        with p:
            rc, _, err = quiet(ri.main, ["unfold", "--r", str(R), "--what", "playlist", "--playlist", "1A",
                                         "--pairs=4101:-"])
        self.assertEqual(rc, 0, err)
        c = calls[0]
        for flag, v in (("--expect-npz-sha256", digest(lat)), ("--expect-bkg-sha256", digest(bkg)),
                        ("--config", "R"), ("--iters", "5"), ("--construction", "data"),
                        ("--estimator-seed", "42"), ("--threads", "32"), ("--tag", "rpd_1A")):
            self.assertEqual(c[c.index(flag) + 1], v, flag)

    def test_refuses_an_existing_product_another_receipt_or_a_missing_product(self):
        R, lat, bkg = self.receipt_playlist()
        out = R / "unf/1A"
        out.mkdir(parents=True)
        (out / "rpd_1A_b4101_j-.npz").write_bytes(b"old")
        calls, p = self.fake()
        with p:
            self.assertEqual(quiet(ri.main, ["unfold", "--r", str(R), "--what", "playlist", "--playlist", "1A",
                                             "--pairs=4101:-"])[0], 3)
        shutil.rmtree(self.tmp / "R")
        R, lat, bkg = self.receipt_playlist(schema="fd-ct-5b-inputs/1")
        with p:
            self.assertEqual(quiet(ri.main, ["unfold", "--r", str(R), "--what", "playlist", "--playlist", "1A",
                                             "--pairs=4101:-"])[0], 4)
        self.assertEqual(calls, [])
        shutil.rmtree(self.tmp / "R")
        R, lat, bkg = self.receipt_playlist()
        calls, p = self.fake(write=False)
        with p:
            rc, _, err = quiet(ri.main, ["unfold", "--r", str(R), "--what", "playlist", "--playlist", "1A",
                                         "--pairs=4101:-"])
        self.assertEqual(rc, 6)

    def test_what_takes_exactly_its_own_arguments(self):
        for argv in (["--what", "k2", "--playlist", "1A"], ["--what", "n0", "--partition", "1"],
                     ["--what", "playlist"]):
            rc, _, _ = quiet(ri.main, ["unfold", "--r", str(self.tmp), "--pairs=-:-", *argv])
            self.assertEqual(rc, 2, argv)


# ================================================================ fd_rpd: arithmetic


class Arithmetic(unittest.TestCase):
    def test_the_regions_are_the_reported_fine_cells_between_the_declared_edges(self):
        g = rp.Grid(DEFINITION)
        self.assertTrue(np.all((g.wL > 0) <= (g.fm >= 0)) and np.all((g.wH > 0) <= (g.fm >= 0)))
        self.assertFalse(np.any((g.wL > 0) & (g.wH > 0)))
        self.assertTrue(g.wL.sum() > 0 and g.wH.sum() > 0)
        shape = sa.s1.fine_shape()
        ipz = np.unravel_index(np.arange(g.fm.size), shape)[1]
        e = np.asarray(sa.s1.FINE["pz"])
        self.assertTrue(np.all(e[ipz][g.wH > 0] >= 8.0) and np.all(e[ipz + 1][g.wH > 0] <= 15.0))
        self.assertTrue(np.all(e[ipz][g.wL > 0] >= 1.5) and np.all(e[ipz + 1][g.wL > 0] <= 8.0))
        vol = sa.s1.fine_volume()
        np.testing.assert_allclose(g.wL[g.wL > 0], vol[g.wL > 0])

    def test_the_step_is_the_2d_tests_form(self):
        Xn, Tn, Xd, Td = np.array([2.0, 3.3]), np.array([1.9, 3.0]), np.array([4.0, 6.0]), np.array([4.1, 6.1])
        want = ((3.3 / 3.0) / (6.0 / 6.1)) / ((2.0 / 1.9) / (4.0 / 4.1)) - 1
        self.assertAlmostEqual(rp.step(Xn / Tn, Xd / Td), want, places=14)

    def test_the_reference_leaves_x_out_and_is_the_exposure_weighted_mean(self):
        self.assertNotIn("1D", rp.ref_set("1D"))
        self.assertEqual(rp.ref_set("1G"), rp.A_SET)
        D = {X: np.array([1.0 + i, 2.0 + i]) for i, X in enumerate(PL)}
        e = dict(zip(PL, E_APPROX))
        w = np.array([e[m] for m in rp.A_SET])
        want = sum(e[m] * D[m] for m in rp.A_SET) / w.sum()
        np.testing.assert_allclose(rp.combo(D, e, rp.A_SET), want)

    def test_the_patterns_give_exactly_one_outcome_for_every_class_assignment(self):
        classes = ("UNRESOLVED", "CARRIES", "FREE", "PARTIAL")
        counts = {"PERIOD-WIDE": 0, "SUBSET": 0, "OTHER": 0}
        for combo in itertools.product(classes, repeat=9):
            cls = dict(zip(PL[:9], combo))
            cls.update({X: "FREE" for X in PL[9:]})
            counts[rp.pattern(cls)] += 1
        self.assertEqual(sum(counts.values()), 4 ** 9)
        self.assertEqual(counts["PERIOD-WIDE"], 252)     # audit 2's enumeration count
        self.assertEqual(counts["SUBSET"], 756)

    def test_the_pattern_semantics(self):
        base = {X: "FREE" for X in PL}
        pw = {**base, "1G": "CARRIES", "1L": "UNRESOLVED", "1M": "CARRIES"}
        self.assertEqual(rp.pattern(pw), "PERIOD-WIDE")
        self.assertEqual(rp.pattern({**pw, "1D": "PARTIAL"}), "OTHER")
        self.assertEqual(rp.pattern({**pw, **{X: "UNRESOLVED" for X in rp.A_SET}}), "OTHER")
        sub = {**base, "1G": "CARRIES", "1L": "UNRESOLVED", "1M": "FREE"}
        self.assertEqual(rp.pattern(sub), "SUBSET")
        self.assertEqual(rp.pattern({**sub, "1L": "PARTIAL"}), "OTHER")
        self.assertEqual(rp.pattern({**base, "1G": "CARRIES", "1L": "UNRESOLVED", "1M": "UNRESOLVED"}), "OTHER")
        self.assertEqual(rp.pattern({**pw, "1N": "PARTIAL"}), "PERIOD-WIDE")

    def test_free_and_carries_are_disjoint_for_a_resolved_playlist(self):
        rng = np.random.default_rng(10)
        for _ in range(20000):
            tbar = rng.uniform(0.001, 0.1)
            s = rng.uniform(0, tbar / 4 * 0.999)
            sh = rng.uniform(0, 2 * s)
            t = rng.normal(tbar / 4, tbar)
            rp.classify(t, s, t - tbar / 2, sh, tbar)     # raises if both held

    def test_classes_in_both_directions(self):
        tbar = 0.07
        self.assertEqual(rp.classify(0.0, 0.01, -0.035, 0.01, tbar), "FREE")
        self.assertEqual(rp.classify(0.07, 0.01, 0.035, 0.01, tbar), "CARRIES")
        self.assertEqual(rp.classify(0.07, 0.0176, 0.035, 0.0176, tbar), "UNRESOLVED")   # sigma >= tbar/4
        self.assertEqual(rp.classify(0.07, 0.0174, 0.035, 0.0174, tbar), "CARRIES")
        self.assertEqual(rp.classify(0.045, 0.01, 0.01, 0.01, tbar), "PARTIAL")
        self.assertEqual(rp.classify(0.0, 0.001, -0.035, 0.001, tbar, unres_forced=True), "UNRESOLVED")
        # a single carrier, well above the group mean, is CARRIES (audit 3, A1)
        self.assertEqual(rp.classify(0.157, 0.01, 0.157 - 0.035, 0.01, tbar), "CARRIES")

    def test_the_partitions(self):
        A = rp.partitions((6, 3, 3))
        self.assertEqual(len(A), 9240)
        self.assertTrue(np.all(A.sum(axis=1) == 1))
        keys = {tuple(sorted(tuple(np.flatnonzero(g)) for g in p)) for p in A}
        self.assertEqual(len(keys), 9240)
        B = rp.partitions((5, 3, 2, 2))
        self.assertEqual(len(B), 83160)
        keysB = {tuple(sorted(tuple(np.flatnonzero(g)) for g in p)) for p in B}
        self.assertEqual(len(keysB), 83160)
        self.assertEqual(rp.find(A, rp.membership(rp.FLUX_PI)) >= 0, True)

    def test_f_is_the_between_share_by_explicit_loops(self):
        rng = np.random.default_rng(11)
        g = rp.offsets(1 + rng.normal(0, .02, (12, 16)), E_APPROX)
        M = np.cov(rng.normal(size=(40, 16)), rowvar=False) + np.eye(16)
        Mi = np.linalg.inv(M)
        A = rp.partitions((6, 3, 3))
        F = rp.F_all(rp.gram(g, E_APPROX, Mi), E_APPROX, A.astype(float))
        for n in (0, 17, 9239):
            qb = 0.0
            for grp in A[n]:
                idx = np.flatnonzero(grp)
                Eg = E_APPROX[idx].sum()
                G = sum(E_APPROX[i] * g[i] for i in idx) / Eg
                qb += Eg * G @ Mi @ G
            qt = sum(E_APPROX[i] * g[i] @ Mi @ g[i] for i in range(12))
            self.assertAlmostEqual(F[n], qb / qt, places=12)
        self.assertAlmostEqual(float(np.max(np.abs((E_APPROX[:, None] * g).sum(axis=0)))), 0.0, places=14)

    def test_the_p_value_counts_ties_and_the_observed_partition(self):
        F = np.array([0.1, 0.5, 0.5, 0.2])
        self.assertEqual(rp.p_value(F, 1), 0.5)
        self.assertEqual(rp.p_value(F, 0), 1.0)

    def test_sigma_delta_is_unbiased_for_iid_offsets(self):
        rng = np.random.default_rng(12)
        S = np.diag(np.linspace(1, 2, 16)) * 1e-4
        L = np.linalg.cholesky(S)
        est = np.mean([rp.sigma_delta(rp.offsets(1 + rng.standard_normal((12, 16)) @ L.T, E_APPROX), E_APPROX)
                       for _ in range(3000)], axis=0)
        np.testing.assert_allclose(np.diag(est), np.diag(S), rtol=0.08)

    def test_r2s_outcomes_are_an_ordered_partition(self):
        ok = {str(a): 0.05 for a in rp.R2_SCALES}
        bad = {**ok, "2.0": 0.07}
        self.assertEqual(rp.r2_outcome(0.01, ok, 0.9, False), "CLUSTERED")
        self.assertEqual(rp.r2_outcome(0.2, ok, 0.9, False), "EXCHANGEABLE-COMPATIBLE")
        self.assertEqual(rp.r2_outcome(0.2, ok, 0.79, False), "INCONCLUSIVE")
        self.assertEqual(rp.r2_outcome(0.01, bad, 0.9, False), "INCONCLUSIVE")
        self.assertEqual(rp.r2_outcome(0.01, ok, 0.9, True), "INCONCLUSIVE")
        self.assertEqual(rp.r2_outcome(0.2, {}, 0.9, False, gate=False), "EXCHANGEABLE-COMPATIBLE")

    def test_stage_0s_branches(self):
        self.assertEqual(rp.stage0_branch(0.07, 0.005), "SEES")
        self.assertEqual(rp.stage0_branch(0.0346, 0.0069), "OTHER")       # below half of 2D's step
        self.assertEqual(rp.stage0_branch(0.0348, 0.00696), "SEES")
        self.assertEqual(rp.stage0_branch(0.07, 0.0141), "OTHER")         # z < 5
        self.assertEqual(rp.stage0_branch(0.001, 0.005), "ABSENT")
        self.assertEqual(rp.stage0_branch(-0.07, 0.005), "OTHER")         # a significant negative step

    def test_the_oc_model_reproduces_sigma0_and_its_truths(self):
        s0, sig0 = 0.06, 0.004
        keys, A, su2, sig, E = rp.oc_model(E_APPROX, s0, sig0)
        mPB = np.zeros(12)
        mPA = np.zeros(12)
        for X in rp.B_SET:
            mPB[PL.index(X)] = E_APPROX[PL.index(X)] / E["PB"]
        for X in rp.A_SET:
            mPA[PL.index(X)] = E_APPROX[PL.index(X)] / E["PA"]
        v = mPB - mPA
        self.assertAlmostEqual(math.sqrt(v @ np.diag(su2 / E_APPROX) @ v), sig0, places=12)
        tr = rp.oc_truths(E_APPROX, s0, E)
        ed = dict(zip(PL, E_APPROX))
        for name in ("PW", "S-1G", "S-1M", "S-1G1M"):
            mean = sum(ed[X] * tr[name][X] for X in rp.B_SET) / E["PB"]
            self.assertAlmostEqual(mean, s0, places=12, msg=name)

    def test_the_oc_table_finds_each_pattern_at_low_noise(self):
        oc = rp.oc_table(E_APPROX, 0.07, 0.0005, 2000, 1)
        self.assertGreater(oc["PW"]["PERIOD-WIDE"], 0.6)
        self.assertGreater(oc["S-1G"]["SUBSET"], 0.6)
        self.assertGreater(oc["S-1G1M"]["SUBSET"], 0.6)
        noisy = rp.oc_table(E_APPROX, 0.035, 0.007, 2000, 1)
        self.assertLess(noisy["PW"]["PERIOD-WIDE"], 0.5)

    def test_s1_is_the_observed_period_structure_shrunk_by_its_noise_share(self):
        r2 = rp.R2(E_APPROX, np.eye(16))
        sd = 0.0016 / np.sqrt(E_APPROX)

        def noise(rng):
            return rng.standard_normal((12, 16)) * sd[:, None]
        rng = np.random.default_rng(14)
        G = {per: rng.standard_normal(16) * 0.004 for per, _ in rp.FLUX_PI}
        g = r2.g_of(np.vstack([G[rp.GROUP[X]] for X in PL]), noise(rng))
        sim = r2.run(g, noise, rng, 40, gate=False)
        self.assertAlmostEqual(sim["c"], math.sqrt(max(0.0, 1.0 - sim["q_noise_mean"] / sim["q_obs"])), places=12)
        self.assertLess(sim["c"], 1.0)
        g0 = r2.g_of(0.0, noise(rng))
        self.assertLess(r2.run(g0, noise, rng, 40, gate=False)["c"], 0.8)

    def test_scaled_equal_needs_exact_zeros_where_the_reference_is_zero(self):
        self.assertTrue(rp.scaled_equal(np.array([0.0, 2.0]), np.array([0.0, 1.0]), 2.0))
        self.assertFalse(rp.scaled_equal(np.array([1e-300, 2.0]), np.array([0.0, 1.0]), 2.0))
        self.assertFalse(rp.scaled_equal(np.array([0.0, 2.0 * (1 + 1e-11)]), np.array([0.0, 1.0]), 2.0))

    def test_r2_reaches_ec_on_exchangeable_offsets_and_clustered_on_clustered_ones(self):
        r2 = rp.R2(E_APPROX, np.eye(16))
        sd = 0.0016 / np.sqrt(E_APPROX)

        def noise(rng):
            return rng.standard_normal((12, 16)) * sd[:, None]
        rng = np.random.default_rng(13)
        out = {"ex": [], "cl": []}
        for _ in range(6):
            g = r2.g_of(rng.standard_normal((12, 16)) * 0.011, noise(rng))
            p = r2.test(g)[1]
            out["ex"].append(rp.r2_outcome(p, {}, r2.run(g, noise, rng, 60, gate=False)["beta1"], False, gate=False))
            G = {per: rng.standard_normal(16) * 0.01 for per, _ in rp.FLUX_PI}
            g = r2.g_of(np.vstack([G[rp.GROUP[X]] for X in PL]), noise(rng))
            p = r2.test(g)[1]
            out["cl"].append(rp.r2_outcome(p, {}, r2.run(g, noise, rng, 60, gate=False)["beta1"], False, gate=False))
        self.assertGreaterEqual(out["ex"].count("EXCHANGEABLE-COMPATIBLE"), 4, out)
        self.assertEqual(out["cl"].count("CLUSTERED"), 6, out)


# ================================================================ fd_rpd: readers on a synthetic run directory


def check5b(per):
    return json.loads((REPO / rp.CHECK_REL / f"check_{per}.json").read_text())["files"]


class RTree:
    """A synthetic run directory R: staged S1/C_resp and 5B products, F1's record, the playlists' receipts, unfolds and
    truths, N0's partitions, from planted cell integrals over the readers' synthetic S1 assembly."""

    def __init__(self, root: Path, seed=3, step_pb=0.0, noise=0.002, n_rep=3, n_part=2):
        self.root, self.R = root, root / "R"
        self.t = TR.Tree(root / "s1", seed=seed).write_common()
        self.rng = np.random.default_rng(seed + 50)
        self.grid = rp.Grid(DEFINITION)
        self.step_pb, self.noise, self.n_rep, self.n_part = step_pb, noise, n_rep, n_part
        self.rep = {X: tuple(4000 + 100 * (i + 1) + k for k in range(1, n_rep + 1)) for i, X in enumerate(PL)}
        self.staged = {}
        self.code_num = sa.sha256(ND / "s5p_numerics.py")
        self.code_truth = sa.sha256(ND / "s5p_mc_truth_pred.py")

    def fine(self, X_cells, h_factor=1.0):
        x = self.t.cellwise(X_cells)
        return np.where(self.grid.wH > 0, x * h_factor, x)

    def put(self, name, writer):
        p = self.R / "staged" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        writer(p)
        self.staged[name] = p
        return p

    def unfold_file(self, p, x, lat_sha, bkg_sha, b):
        m = TR.data_meta(lat_sha, bkg_sha, bootstrap_seed=b, code_sha256={"s5p_numerics.py": self.code_num})
        np.savez(p, xsec_flat=x, meta=json.dumps(m))

    def truth_file(self, p, t, lat_sha, var_rel=1e-6):
        np.savez(p, xsec_flat=t, sumw2_flat=(t * math.sqrt(var_rel)) ** 2,
                 meta_json=json.dumps({"schema": "s5p-mc-truth-pred/1", "npz_sha256": lat_sha,
                                       "code_sha256": self.code_truth}))

    def write_5b(self, pers=("PA", "PB", "PC")):
        f = self.t.f
        for per in pers:
            files = check5b(per)
            ls, bs = files["lat_npz"][1], files["lat_bkg"][1]
            T = f * self.rng.uniform(0.9, 1.1, 16)
            h = 1.0 + (self.step_pb if per == "PB" else 0.0)
            for b in (None, *rp.cp.BOOT[per]):
                X = T * (1.0 + (0 if b is None else 1) * self.rng.normal(0, self.noise, 16))
                name = f"5b/unf/{per}/5b_{per}_b{'-' if b is None else b}_j-.npz"
                self.put(name, lambda p, X=X, b=b: self.unfold_file(p, self.fine(X, h), ls, bs, b))
            self.put(f"5b/truth/truth_{per}.npz", lambda p, T=T: self.truth_file(p, self.fine(T), ls))
        return self

    def write_common(self):
        self.put("s1/s1_assembly.npz", lambda p: shutil.copy(self.t.s1, p))
        self.put("cresp/cresp.npz", lambda p: shutil.copy(self.t.cresp, p))
        return self

    def write_staged_record(self):
        write_staged(self.R, self.staged)
        return self

    def write_f1(self, e=E_APPROX):
        (self.R / "flux").mkdir(parents=True, exist_ok=True)
        rec = {"schema": "fd-rpd-flux/1", "verdict": "PASS", "exposure_share": dict(zip(PL, e.tolist())),
               "files": {}, "per_playlist": {X: {"contents": [6.2e-4] * 14, "pot_data": 1e20} for X in PL}}
        (self.R / "flux/F1.json").write_text(json.dumps(rec))
        return self

    def patches(self):
        return [mock.patch.dict(ct.PINS, {"s1_npz": digest(self.t.s1), "cresp": digest(self.t.cresp)}),
                mock.patch.object(rp, "REP", self.rep), mock.patch.object(rp, "N_REP", self.n_rep),
                mock.patch.object(ri, "N_PART", self.n_part)]

    def argv(self, reader, out):
        return [reader, "--r", str(self.R), "--definition", str(DEFINITION), "--out-json", str(out),
                "--deploy", str(REPO)]


class ReadersBase(Tmp):
    def run_rp(self, tree, argv, extra=()):
        with contextlib.ExitStack() as st:
            for p in [*tree.patches(), *extra]:
                st.enter_context(p)
            rc, self.stdout, self.stderr = quiet(rp.main, argv)
        return rc


class Stage0(ReadersBase):
    def tree(self, step):
        return RTree(self.tmp, step_pb=step).write_common().write_5b(("PA", "PB")).write_staged_record()

    def test_sees_a_planted_step_and_writes_nothing_absolute(self):
        t = self.tree(0.07)
        out = self.tmp / "stage0.json"
        rc = self.run_rp(t, t.argv("stage0", out))
        self.assertEqual(rc, 0, self.stderr)
        rec = json.loads(out.read_text())
        self.assertEqual(rec["branch"], "SEES")
        self.assertAlmostEqual(rec["s0"], 0.07, places=6)
        self.assertEqual(len(rec["replica_pair_steps"]), 10)
        pairs = np.array(rec["replica_pair_steps"])
        self.assertAlmostEqual(rec["sigma0"], math.sqrt(np.mean((pairs - rec["s0"]) ** 2)), places=14)   # about s0
        text = out.read_text()
        for v in t.t.f:
            self.assertNotIn(repr(float(v)), text)

    def test_a_flat_ratio_is_absent(self):
        t = self.tree(0.0)
        out = self.tmp / "stage0.json"
        self.assertEqual(self.run_rp(t, t.argv("stage0", out)), 0, self.stderr)
        self.assertEqual(json.loads(out.read_text())["branch"], "ABSENT")

    def test_refuses_a_5b_unfold_not_made_from_5bs_dumps(self):
        t = RTree(self.tmp, step_pb=0.07).write_common().write_5b(("PA", "PB"))
        name = "5b/unf/PB/5b_PB_b2003_j-.npz"
        p = t.staged[name]
        t.unfold_file(p, sa.xs(p), "0" * 64, check5b("PB")["lat_bkg"][1], 2003)
        t.write_staged_record()
        out = self.tmp / "stage0.json"
        self.assertEqual(self.run_rp(t, t.argv("stage0", out)), 1)
        self.assertFalse(out.exists())

    def test_refuses_a_staged_copy_changed_after_staging(self):
        t = self.tree(0.07)
        t.staged["5b/truth/truth_PA.npz"].write_bytes(b"changed")
        out = self.tmp / "stage0.json"
        self.assertEqual(self.run_rp(t, t.argv("stage0", out)), 1)
        self.assertIn("staged 5b/truth/truth_PA.npz", self.stderr)

    def test_the_guard_refuses_a_planted_ratio_to_f(self):
        t = self.tree(0.07)
        out = self.tmp / "stage0.json"
        real = rp.stage0_branch
        with mock.patch.object(rp, "stage0_branch", lambda s0, s: real(s0, s) if s0 != 99 else "x"):
            pass
        leak = float(t.t.f[3])
        with mock.patch.object(rp, "staged_digests", lambda R, p: {"leak": leak}):
            rc = self.run_rp(t, t.argv("stage0", out))
        self.assertNotEqual(rc, 0)
        self.assertFalse(out.exists())


class StageD(ReadersBase):
    def test_writes_both_rules_and_respects_its_budget(self):
        t = RTree(self.tmp).write_common().write_staged_record().write_f1()
        (t.R / "control").mkdir(parents=True)
        (t.R / "control/stage0.json").write_text(json.dumps({"schema": "fd-rpd-stage0/1", "branch": "SEES",
                                                             "s0": 0.06, "sigma0": 0.004}))
        ro = {"C_PL5D": {"C_PL5D_rel": (np.diag(np.full(16, 0.02 ** 2))).tolist()},
              "g_vs_5A": {"periods": {p: {"g_5b": list(v * np.linspace(-1, 1, 16)), "g_5b_noise_sigma": [0.003] * 16}
                                      for p, v in (("PA", 0.0), ("PB", -0.03), ("PC", 0.05))}}}
        out = self.tmp / "stageD.json"
        with mock.patch.object(rp, "five_b_readout", lambda d: ro), mock.patch.object(rp, "STAGE_D_R1_DRAWS", 500):
            rc = self.run_rp(t, t.argv("staged", out) + ["--outer", "3", "--inner", "20"])
        self.assertEqual(rc, 0, self.stderr)
        rec = json.loads(out.read_text())
        r1 = rec["R1_rules"]
        self.assertEqual(r1["drop_PERIOD_WIDE"], r1["P_PW_given_PW"] < 0.5)
        self.assertEqual(r1["drop_SUBSET"], r1["best_P_SUBSET_given_subset_truth"] < 0.5)
        self.assertEqual(r1["P_PW_given_PW"], rec["R1_operating_characteristics"]["at_s0"]["PW"]["PERIOD-WIDE"])
        self.assertIsNotNone(rec["R2_reachability"]["alpha_at_inner_descriptive"]["T1"])
        self.assertIsNone(rec["R2_rule"]["flag_12_playlist_wording_not_expected"])   # fewer than 200 outer
        self.assertEqual(rec["R2_reachability"]["probabilities"]["T2"]["n"], 3)
        # T2 is strongly clustered: every dataset is CLUSTERED
        self.assertEqual(rec["R2_reachability"]["probabilities"]["T2"]["CLUSTERED"], 1.0)
        out2 = self.tmp / "stageD2.json"
        with mock.patch.object(rp, "five_b_readout", lambda d: ro), mock.patch.object(rp, "STAGE_D_R1_DRAWS", 500):
            rc = self.run_rp(t, t.argv("staged", out2) + ["--outer", "50", "--inner", "20", "--budget", "0"])
        self.assertEqual(rc, 0, self.stderr)
        r2 = json.loads(out2.read_text())["R2_reachability"]
        self.assertTrue(r2["stopped_at_budget"])
        self.assertEqual(r2["probabilities"]["T1"]["n"], 0)

    def test_refuses_without_stage_0(self):
        t = RTree(self.tmp).write_common().write_staged_record().write_f1()
        out = self.tmp / "stageD.json"
        rc = self.run_rp(t, t.argv("staged", out))
        self.assertNotEqual(rc, 0)
        self.assertFalse(out.exists())


# ---------------------------------------------------------------- controls


def split_lat(z, b, s_ratio):
    """Per-playlist dumps from a synthetic lat_zero, as a correct run would make them: rows partitioned in production
    order, weights and histograms rescaled by s_X / s_ALL."""
    n_sig, n_dat, n_bkg = len(z["MCgen"]), len(z["measured"]), len(b["bkg_reco"])
    cut = {k: np.linspace(0, n, 13).astype(int) for k, n in (("s", n_sig), ("d", n_dat), ("b", n_bkg))}
    out = []
    edges = [z[f"edges_{i}"] for i in range(5)]
    for i, X in enumerate(PL):
        ss, sd, sb = (slice(cut[k][i], cut[k][i + 1]) for k in ("s", "d", "b"))
        r = s_ratio[X]
        zz = {k: z[k] for k in ri.GLOBAL_KEYS}
        zz.update({k: z[k][ss] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth")})
        zz["w_truth"], zz["w_reco"] = z["w_truth"][ss] * r, z["w_reco"][ss] * r
        zz["measured"] = z["measured"][sd]
        zz["data_pot"] = float(z["data_pot"]) * (cut["d"][i + 1] - cut["d"][i]) / n_dat
        bb = {"bkg_reco": b["bkg_reco"][sb], "bkg_w": b["bkg_w"][sb] * r}
        bb["bkg_nd"] = ri.histnd_counts([bb["bkg_reco"][:, j] for j in range(5)], bb["bkg_w"], edges)
        zz["denom_nd"] = None
        out.append((zz, bb))
    # the denominators: split the truth histogram as the rows, rescaled, so that the sum rule holds exactly
    tot = np.zeros_like(z["denom_nd"])
    for i, (zz, bb) in enumerate(out):
        part = ri.truth_sum(zz["MCgen"], zz["pass_truth"], zz["w_truth"] / s_ratio[PL[i]], edges)
        zz["denom_nd"] = part * 1.4 * s_ratio[PL[i]]
        tot += part * 1.4
    z["denom_nd"] = tot
    for zz, bb in out:
        meas = zz["measured"].astype(float)
        dn = ri.histnd_counts([meas[:, j] for j in range(5)], np.ones(len(meas)), edges)
        target = np.maximum(0.0, dn - bb["bkg_nd"])
        idx = [np.digitize(meas[:, j], e) - 1 for j, e in enumerate(edges)]
        w = np.zeros(len(meas))
        for n in range(len(meas)):
            c = tuple(int(ix[n]) for ix in idx)
            if all(0 <= c[a] < dn.shape[a] for a in range(5)) and dn[c] > 0:
                w[n] = target[c] / dn[c]
        zz["measured_weights"] = w
    return out


class Controls(ReadersBase):
    def build(self):
        t = RTree(self.tmp).write_common()
        rng = np.random.default_rng(21)
        z, b = lat_all(rng, n_sig=2400, n_data=1200, n_bkg=480)
        self.mc_pot = {X: 1e21 * (1 + 0.1 * i) for i, X in enumerate(PL)}
        self.data_pot = {}
        recs = {}
        sr = {}
        # data POTs follow the data rows' split; s_X = data_pot / mc_pot
        n_dat = len(z["measured"])
        cut = np.linspace(0, n_dat, 13).astype(int)
        for i, X in enumerate(PL):
            self.data_pot[X] = float(z["data_pot"]) * (cut[i + 1] - cut[i]) / n_dat
        s = {X: self.data_pot[X] / self.mc_pot[X] for X in PL}
        s_all = sum(self.data_pot.values()) / sum(self.mc_pot.values())
        sr = {X: s[X] / s_all for X in PL}
        parts = split_lat(z, b, sr)
        lat0 = t.put("mp1/lat_zero.npz", lambda p: np.savez(p, **z))
        bkg0 = t.put("mp1/lat_zero_bkg.npz", lambda p: np.savez(p, **b, meta="{}"))
        code = sa.sha256(Path(ri.__file__).resolve())
        for i, X in enumerate(PL):
            zz, bb = parts[i]
            q = {k: t.R / v for k, v in ri.playlist_paths(X).items()}
            for d in ("dumps", "truth", "inputs", "flux"):
                (t.R / d).mkdir(exist_ok=True)
            np.savez(q["lat"], **zz)
            np.savez(q["bkg"], **bb, meta=json.dumps({"npz_sha256": digest(q["lat"])}))
            q["truth"].write_bytes(b"t")
            q["flux"].write_bytes(b"f")
            loop = t.put(f"zero/runEventLoopOmniFold_5D_{X}_zero.root", lambda p: p.write_bytes(X.encode()))
            recs[X] = {"schema": "fd-rpd-inputs/1", "playlist": X, "data_pot": self.data_pot[X],
                       "mc_pot": self.mc_pot[X], "code_sha256": {"fd_rpd_inputs.py": code},
                       "files": {k: [str(p), digest(p)] for k, p in (("lat_npz", q["lat"]), ("lat_bkg", q["bkg"]),
                                                                      ("truth", q["truth"]), ("flux", q["flux"]),
                                                                      ("loop", loop))}}
            q["receipt"].write_text(json.dumps(recs[X]))
        t.write_staged_record().write_f1()
        self.t, self.z, self.b = t, z, b
        return t, recs

    def test_c1_passes_a_correct_split_and_fails_each_one_entry_defect(self):
        t, recs = self.build()
        fr = json.loads((t.R / "flux/F1.json").read_text())
        res = rp.c1(t.R, recs, fr)
        self.assertTrue(res["pass"], res["keys"])
        for key, tamper in (("w_truth", lambda z: z["w_truth"].__setitem__(0, z["w_truth"][0] * (1 + 1e-10))),
                            ("MCgen", lambda z: z["MCgen"].__setitem__((0, 0), z["MCgen"][0, 0] + 1)),
                            ("data_pot", lambda z: z.__setitem__("data_pot", z["data_pot"] * 1.001)),
                            ("flux", lambda z: z.__setitem__("flux", z["flux"] * (1 + 1e-10)))):
            with self.subTest(key=key):
                p = Path(recs["1L"]["files"]["lat_npz"][0])
                with np.load(p, allow_pickle=True) as zz:
                    d = {k: np.array(zz[k]) for k in zz.files}
                orig = {k: np.array(v) for k, v in d.items()}
                tamper(d)
                np.savez(p, **d)
                self.assertFalse(rp.c1(t.R, recs, fr)["keys"][key])
                np.savez(p, **orig)
        p = Path(recs["1G"]["files"]["lat_bkg"][0])
        with np.load(p, allow_pickle=True) as bb:
            d = {k: np.array(bb[k]) for k in bb.files}
        d["bkg_nd"] = d["bkg_nd"] * 1.001
        np.savez(p, **d)
        self.assertFalse(rp.c1(t.R, recs, fr)["keys"]["bkg_nd"])

    def test_c1s_hadd_additivity_is_tested_by_the_weights(self):
        t, recs = self.build()
        fr = json.loads((t.R / "flux/F1.json").read_text())
        recs["1D"]["mc_pot"] *= 1.0001                    # a merge whose mcPOTUsed is not the sum
        self.assertFalse(rp.c1(t.R, recs, fr)["keys"]["w_truth"])

    def test_the_vectorized_measured_weights_are_the_dumps_rule(self):
        t, recs = self.build()
        z = rp.load_all(Path(recs["1A"]["files"]["lat_npz"][0]))
        b = rp.load_all(Path(recs["1A"]["files"]["lat_bkg"][0]))
        self.assertEqual(rp.measured_weights_agreement(z, b, [z[f"edges_{i}"] for i in range(5)]), 1.0)
        z["measured_weights"] = z["measured_weights"] * 1.01
        self.assertLess(rp.measured_weights_agreement(z, b, [z[f"edges_{i}"] for i in range(5)]), 0.999)

    def test_n0p_passes_a_true_partition_and_fails_each_defect(self):
        t, recs = self.build()
        fr = json.loads((t.R / "flux/F1.json").read_text())
        z = rp.load_all(t.staged["mp1/lat_zero.npz"])
        b = rp.load_all(t.staged["mp1/lat_zero_bkg.npz"])
        e = np.array([fr["exposure_share"][X] for X in PL])
        for part in (1, 2):
            npzs, bkgs, asg = ri.n0_partition(z, {k: v for k, v in b.items() if k != "meta"}, e, ri.N0_SEED0 + part)
            rp_ = t.R / ri.n0_paths(part, 0)["receipt"]
            rp_.parent.mkdir(parents=True, exist_ok=True)
            ap = t.R / ri.n0_paths(part, 0)["assign"]
            np.savez(ap, **asg)
            pseudo = []
            for k in range(12):
                q = {kk: t.R / v for kk, v in ri.n0_paths(part, k).items()}
                np.savez(q["npz"], **npzs[k])
                np.savez(q["bkg"], **bkgs[k], meta=json.dumps({"npz_sha256": digest(q["npz"])}))
                pseudo.append({"k": k, "npz": [str(q["npz"]), digest(q["npz"])], "bkg": [str(q["bkg"]), digest(q["bkg"])]})
            rp_.write_text(json.dumps({"schema": "fd-rpd-n0/1", "partition": part, "assign": [str(ap), digest(ap)],
                                       "pseudo": pseudo}))
        with mock.patch.object(ri, "N_PART", 2):
            res = rp.n0p(t.R, fr)
            self.assertTrue(res["pass"], res)
            q = ri.n0_paths(2, 4)
            zz = rp.load_all(t.R / q["npz"])
            zz["denom_nd"] = zz["denom_nd"] * 1.001
            np.savez(t.R / q["npz"], **zz)
            rec = json.loads((t.R / ri.n0_paths(2, 0)["receipt"]).read_text())
            rec["pseudo"][4]["npz"][1] = digest(t.R / q["npz"])
            (t.R / ri.n0_paths(2, 0)["receipt"]).write_text(json.dumps(rec))
            res = rp.n0p(t.R, fr)
        self.assertFalse(res["partitions"]["2"]["checks"]["completeness_equal"])
        self.assertTrue(res["partitions"]["1"]["pass"])

    def test_k2_is_bitwise_on_xsec_flat(self):
        t = RTree(self.tmp).write_common()
        pc = check5b("PC")
        lat = t.put("5b/dumps/lat_PC.npz", lambda p: p.write_bytes(b"lat"))
        bkg = t.put("5b/dumps/lat_PC_bkg.npz", lambda p: p.write_bytes(b"bkg"))
        x = t.fine(t.t.f)
        (t.R / "unf-k2").mkdir(parents=True)
        for b in rp.K2_SEEDS:
            tag = f"b{'-' if b is None else b}_j-"
            t.put(f"5b/unf/PC/5b_PC_{tag}.npz", lambda p: np.savez(p, xsec_flat=x, meta="{}"))
            t.unfold_file(t.R / "unf-k2" / f"rpd_k2_PC_{tag}.npz", x, digest(lat), digest(bkg), b)
        t.write_staged_record()
        self.assertTrue(rp.k2(t.R)["pass"])
        y = x.copy()
        y[100] = np.nextafter(y[100], 1.0)
        t.unfold_file(t.R / "unf-k2" / "rpd_k2_PC_b3001_j-.npz", y, digest(lat), digest(bkg), 3001)
        res = rp.k2(t.R)
        self.assertEqual(res["by_seed"], {"None": True, "3001": False})
        self.assertNotEqual(pc["lat_npz"][1], digest(lat))   # K2 checks against the staged copies' own digests


class FiveB(ReadersBase):
    def test_the_rebuilt_5d_block_must_be_the_committed_one(self):
        t = RTree(self.tmp, step_pb=0.03).write_common().write_5b().write_staged_record()
        grid = t.grid
        e5 = {"PA": 0.5334, "PB": 0.2945, "PC": 0.1721}
        fb = {}
        for per in ("PA", "PB", "PC"):
            T = grid.cells(sa.xs(t.staged[f"5b/truth/truth_{per}.npz"]))
            X = grid.cells(sa.xs(t.staged[f"5b/unf/{per}/5b_{per}_b-_j-.npz"]))
            fb[per] = X / T
        m = sum(e5[P] * fb[P] for P in fb)
        V2 = sum(v * v for v in e5.values())
        C = V2 / (1 - V2) * sum(e5[P] * np.outer(fb[P] / m - 1, fb[P] / m - 1) for P in fb)
        a = argparse_ns(t)
        for ref, ok in ((C, True), (C * 1.01, False)):
            ro = {"constants": {"exposure_share": e5}, "C_PL5D": {"C_PL5D_rel": ref.tolist()}}
            with contextlib.ExitStack() as st:
                for p in [*t.patches(), mock.patch.object(rp, "five_b_readout", lambda d, ro=ro: ro)]:
                    st.enter_context(p)
                if ok:
                    C5, Cn = rp.five_b_block(a, grid)
                    np.testing.assert_allclose(C5, C, rtol=1e-12)
                    self.assertEqual(Cn.shape, (16, 16))
                else:
                    with self.assertRaises(rp.f0.Stop):
                        rp.five_b_block(a, grid)


def argparse_ns(t):
    import argparse
    return argparse.Namespace(r=t.R, deploy=REPO)


class Gate(ReadersBase):
    def test_job_a_needs_f1_and_the_stage_0_and_d_records(self):
        t = RTree(self.tmp)
        (t.R / "control").mkdir(parents=True)
        g = ["gate", "--r", str(t.R), "--stage", "a"]
        self.assertEqual(self.run_rp(t, g), 1)
        t.write_f1()
        self.assertEqual(self.run_rp(t, g), 1)
        (t.R / "control/stage0.json").write_text(json.dumps({"schema": "fd-rpd-stage0/1"}))
        self.assertEqual(self.run_rp(t, g), 1)
        (t.R / "control/stageD.json").write_text(json.dumps({"schema": "fd-rpd-stageD/1"}))
        self.assertEqual(self.run_rp(t, g), 0, self.stderr)

    def test_job_b_needs_this_deploys_controls_pass_on_the_receipts_now_on_disk(self):
        t = RTree(self.tmp)
        (t.R / "control").mkdir(parents=True)
        (t.R / "inputs").mkdir(parents=True)
        for X in PL:
            (t.R / ri.playlist_paths(X)["receipt"]).write_text(X)
        rec = {"schema": "fd-rpd-controls/1", "verdict": "PASS",
               "code_sha256": {"fd_rpd.py": sa.sha256(Path(rp.__file__).resolve())},
               "inputs_sha256": {"receipts": {X: digest(t.R / ri.playlist_paths(X)["receipt"]) for X in PL}}}
        g = ["gate", "--r", str(t.R), "--stage", "b"]
        for bad in ({"verdict": "FAIL"}, {"code_sha256": {"fd_rpd.py": "0"}}):
            (t.R / "control/controls.json").write_text(json.dumps({**rec, **bad}))
            self.assertEqual(self.run_rp(t, g), 1, bad)
        (t.R / "control/controls.json").write_text(json.dumps(rec))
        self.assertEqual(self.run_rp(t, g), 0, self.stderr)
        (t.R / ri.playlist_paths("1M")["receipt"]).write_text("changed")
        self.assertEqual(self.run_rp(t, g), 1)


# ---------------------------------------------------------------- readout


class Readout(ReadersBase):
    """The readout end to end, on 12 synthetic playlists (3 replicas each), 2 N0 partitions and 400 null datasets."""

    def build(self, branch="SEES", pb_step=0.07, carriers=("1G", "1L", "1M"), size_bias=0.0):
        # 10 replicas: with 3, the replica-resampled null is a 3^12-point mixture whose size depends on the draw, and
        # the calibration gate rightly refuses it (alpha(0) = 0.17 at seed 31; part 2 section 4)
        t = RTree(self.tmp, noise=0.002, n_rep=10).write_common()
        f = t.t.f
        rng = np.random.default_rng(31)
        code = sa.sha256(Path(ri.__file__).resolve())
        T0 = f * rng.uniform(0.9, 1.1, 16)
        for i, X in enumerate(PL):
            q = {k: t.R / v for k, v in ri.playlist_paths(X).items()}
            for d in ("dumps", "truth", "inputs", "flux", "unf"):
                (t.R / d).mkdir(exist_ok=True)
            q["lat"].write_bytes(X.encode() + b"lat")
            q["bkg"].write_bytes(X.encode() + b"bkg")
            q["flux"].write_bytes(b"f")
            ls, bs = digest(q["lat"]), digest(q["bkg"])
            T = T0 * E_APPROX[i]
            t.truth_file(q["truth"], t.fine(T), ls)
            h = 1.0 + (pb_step * (0.295 / sum(E_APPROX[PL.index(c)] for c in carriers)) if X in carriers else 0.0)
            # an offset uniform in p_parallel (so it moves no step): a normalization per playlist, and a p_T shape
            # shared by 1G/1L/1M, so the 16-cell offsets cluster by flux-file group
            pt_shape = np.array([(-1.0 if c in rp.cp.PZ_LO else 1.0) for c in range(16)])
            off = 1.0 + rng.normal(0, 0.002) + (0.03 * (1 + 0.5 * np.sin(np.arange(16))) if X in rp.B_SET else 0.0)
            q["unf"].mkdir()
            for b in (None, *t.rep[X]):
                X_ = T * off * (1.0 + (0 if b is None else 1) * rng.normal(0, 0.002 / math.sqrt(E_APPROX[i]), 16))
                t.unfold_file(q["unf"] / f"rpd_{X}_b{'-' if b is None else b}_j-.npz", t.fine(X_, h), ls, bs, b)
            loop = t.put(f"zero/runEventLoopOmniFold_5D_{X}_zero.root", lambda p, X=X: p.write_bytes(X.encode()))
            q["receipt"].write_text(json.dumps({
                "schema": "fd-rpd-inputs/1", "playlist": X, "code_sha256": {"fd_rpd_inputs.py": code},
                "files": {k: [str(p), digest(p)] for k, p in (("lat_npz", q["lat"]), ("lat_bkg", q["bkg"]),
                                                               ("truth", q["truth"]), ("flux", q["flux"]),
                                                               ("loop", loop))}}))
        for part in range(1, t.n_part + 1):
            rp_ = t.R / ri.n0_paths(part, 0)["receipt"]
            rp_.parent.mkdir(parents=True, exist_ok=True)
            pseudo = []
            for k, X in enumerate(PL):
                q = {kk: t.R / v for kk, v in ri.n0_paths(part, k).items()}
                q["npz"].write_bytes(f"n0 {part} {k}".encode())
                q["bkg"].write_bytes(f"n0b {part} {k}".encode())
                ls, bs = digest(q["npz"]), digest(q["bkg"])
                T = T0 * E_APPROX[k]
                t.truth_file(q["truth"], t.fine(T), ls)
                bias = size_bias if E_APPROX[k] < 0.03 else 0.0
                X_ = T * (1 + bias + rng.normal(0, 0.002 / math.sqrt(E_APPROX[k]), 16))
                q["unf"].mkdir(parents=True)
                t.unfold_file(q["unf"] / f"rpd_n0_p{part:02d}_k{k:02d}_b-_j-.npz", t.fine(X_), ls, bs, None)
                pseudo.append({"k": k, "npz": [str(q["npz"]), ls], "bkg": [str(q["bkg"]), bs],
                               "truth": [str(q["truth"]), digest(q["truth"])]})
            rp_.write_text(json.dumps({"schema": "fd-rpd-n0/1", "partition": part, "pseudo": pseudo}))
        t.write_staged_record().write_f1()
        (t.R / "control").mkdir(exist_ok=True)
        (t.R / "control/controls.json").write_text(json.dumps({"schema": "fd-rpd-controls/1", "verdict": "PASS"}))
        (t.R / "control/stage0.json").write_text(json.dumps({"schema": "fd-rpd-stage0/1", "branch": branch,
                                                             "s0": 0.07, "sigma0": 0.004}))
        (t.R / "control/stageD.json").write_text(json.dumps({
            "schema": "fd-rpd-stageD/1", "R1_rules": {"drop_PERIOD_WIDE": False, "drop_SUBSET": False},
            "R2_rule": {"flag_12_playlist_wording_not_expected": False}}))
        self.c5 = np.diag(np.full(16, 0.02 ** 2))
        return t

    def run_readout(self, t):
        out = self.tmp / "readout.json"
        extra = [mock.patch.object(rp, "R2_GATE_N", 400),
                 mock.patch.object(rp, "five_b_block", lambda a, g: (self.c5, self.c5 * 0.05))]
        rc = self.run_rp(t, t.argv("readout", out), extra)
        return rc, (json.loads(out.read_text()) if out.exists() else None)

    def test_the_readout_end_to_end(self):
        t = self.build()
        rc, rec = self.run_readout(t)
        self.assertEqual(rc, 0, self.stderr)
        self.assertEqual(rec["R1"]["outcome"], "PERIOD-WIDE", rec["R1"].get("classes"))
        self.assertEqual(rec["R2"]["outcome"], "CLUSTERED", {k: rec["R2"][k] for k in ("p_flux", "alpha", "beta1", "c")})
        self.assertEqual(rec["R2"]["n_partitions"], {"flux": 9240, "era": 83160})
        self.assertFalse(rec["N0"]["SIZE_BIAS_g"])
        self.assertAlmostEqual(rec["R3"]["nu12"], rp.nu_eff(E_APPROX), places=12)
        text = json.dumps(rec)
        for v in t.t.f:
            self.assertNotIn(repr(float(v)), text)

    def test_r1_is_not_computed_unless_stage_0_sees(self):
        t = self.build(branch="ABSENT")
        rc, rec = self.run_readout(t)
        self.assertEqual(rc, 0, self.stderr)
        self.assertEqual(rec["R1"]["outcome"], "NOT COMPUTED")

    def test_r1_is_not_computed_without_a_step(self):
        t = self.build(pb_step=0.0)
        rc, rec = self.run_readout(t)
        self.assertEqual(rc, 0, self.stderr)
        self.assertEqual(rec["R1"]["outcome"], "NOT COMPUTED", rec["R1"].get("tbar"))
        self.assertLess(rec["R1"]["tbar"] / rec["R1"]["sigma_tbar"], 3)

    def test_a_single_carrier_is_a_subset(self):
        t = self.build(carriers=("1G",))
        rc, rec = self.run_readout(t)
        self.assertEqual(rc, 0, self.stderr)
        self.assertEqual(rec["R1"]["classes"]["1G"], "CARRIES", rec["R1"])
        self.assertIn(rec["R1"]["classes"]["1M"], ("FREE",))
        self.assertEqual(rec["R1"]["outcome"], "SUBSET")

    def test_a_planted_size_bias_fires_n0_and_makes_r2_inconclusive(self):
        t = self.build(size_bias=0.05)
        rc, rec = self.run_readout(t)
        self.assertEqual(rc, 0, self.stderr)
        self.assertTrue(rec["N0"]["SIZE_BIAS_g"])
        self.assertEqual(rec["R2"]["outcome"], "INCONCLUSIVE")
        self.assertIn("effect", rec["N0"])

    def test_refuses_without_the_controls_pass(self):
        t = self.build()
        (t.R / "control/controls.json").write_text(json.dumps({"schema": "fd-rpd-controls/1", "verdict": "FAIL"}))
        rc, rec = self.run_readout(t)
        self.assertEqual((rc, rec), (1, None))


# ================================================================ tables and submit stages


class Tables(Tmp):
    def test_the_committed_tables_are_the_generators(self):
        r = subprocess.run([sys.executable, "-I", "-B", str(REPO / RELR / "make_rpd_tables.py"), str(REPO),
                            str(self.tmp)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for n in ("rpd-a-steps.tsv", "tasks-rpd-a.tsv", "rpd-b-steps.tsv", "tasks-rpd-b.tsv", "packing.json"):
            self.assertEqual((self.tmp / n).read_text(), (REPO / RELR / n).read_text(), n)

    def steps(self, name):
        return [ln.split("\t") for ln in (REPO / RELR / name).read_text().splitlines() if ln and not ln.startswith("#")]

    def test_job_b_is_every_declared_unfold_once(self):
        rows = self.steps("rpd-b-steps.tsv")
        self.assertEqual(len(rows), 12 * 31 + 120)
        seen = set()
        for r in rows:
            a = r[3:]
            if a[a.index("--what") + 1] == "playlist":
                X = a[a.index("--playlist") + 1]
                b = [x for x in a if x.startswith("--pairs=")][0][8:].split(":")[0]
                seen.add((X, None if b == "-" else int(b)))
        want = {(X, b) for X in PL for b in (None, *rp.REP[X])}
        self.assertEqual(seen, want)
        self.assertEqual(sorted({int(r[0]) for r in rows}), list(range(8)))

    def test_job_a_passes_mcfile_explicitly_to_every_dump(self):
        rows = self.steps("rpd-a-steps.tsv")
        self.assertEqual(len(rows), 12 * 3 + 2 + 10)
        dumps = [r for r in rows if r[2] in ("nn_dump_inputs.py", "s5p_input_dumps.py")]
        self.assertEqual(len(dumps), 24)
        for r in dumps:
            a = r[3:]
            X = r[1].split("_")[-1]
            self.assertEqual(a[a.index("--mcfile") + 1], f"/pscratch/sd/j/josephrb/fd-rpd-20261103/flux/runEventLoopMC_{X}.root")
            self.assertEqual(a[a.index("--omnifile") + 1],
                             f"/pscratch/sd/j/josephrb/fd-rpd-20261103/staged/zero/runEventLoopOmniFold_5D_{X}_zero.root")

    def test_the_lanes_fit_their_limits(self):
        load = json.loads((REPO / RELR / "packing.json").read_text())["lane_load_s"]
        self.assertLess(max(load["A"]), 3600)
        self.assertLess(max(load["B"]), 7200)


class Submit(Tmp):
    def setUp(self):
        super().setUp()
        self.B, self.D = self.tmp / "R", self.tmp / "deploy"
        (self.D / RELR).mkdir(parents=True)
        real = "/pscratch/sd/j/josephrb/fd-rpd-20261103"
        for n in ("rpd-a-steps.tsv", "tasks-rpd-a.tsv", "rpd-b-steps.tsv", "tasks-rpd-b.tsv"):
            (self.D / RELR / n).write_text((REPO / RELR / n).read_text().replace(real, str(self.B)))
        run = lambda *a: subprocess.run(["git", "-C", str(self.D), *a], check=True, capture_output=True)  # noqa: E731
        run("init", "-q")
        run("add", "-A")
        run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "t")
        self.pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()
        b = self.tmp / "bin"
        b.mkdir()
        (b / "sbatch").write_text(f"#!/bin/bash\nprintf '%s\\n' \"$@\" > {self.tmp}/sbatch.args\necho Submitted\n")
        (b / "py").write_text("#!/bin/bash\n"
                              f"if [ \"$2\" = gate ]; then echo \"$@\" >> {self.tmp}/gate.args; "
                              "[ -e \"$6/control/gate-ok-$4\" ]; exit; fi\nexit 9\n")
        for x in ("sbatch", "py"):
            (b / x).chmod(0o755)
        self.env = {**os.environ, "PATH": f"{b}:{os.environ['PATH']}", "FD_CT_PY": str(b / "py")}

    def submit(self, *args):
        return subprocess.run(["bash", str(ND / "submit_fd_ct.sh"), *args], capture_output=True, text=True, env=self.env)

    def ready_a(self):
        for d in ("staged", "flux", "control"):
            (self.B / d).mkdir(parents=True, exist_ok=True)
        (self.B / "control/gate-ok-a").write_text("")

    def args(self):
        return (self.tmp / "sbatch.args").read_text().splitlines()

    def test_the_job_a_submission(self):
        self.ready_a()
        r = self.submit("rpd-a", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 0, r.stderr)
        a = self.args()
        for want in ("--account=m3246", "--qos=regular", "--constraint=cpu", "--nodes=1", "--exclusive",
                     "--no-requeue", "--time=01:00:00", "--job-name=fd_rpd_a", "32", "56G", "0", "7", "none",
                     str(self.B / "lanes-a")):
            self.assertIn(want, a)
        self.assertIn(f"gate --stage a --r {self.B}", (self.tmp / "gate.args").read_text())
        for d in ("dumps", "truth", "inputs", "n0"):
            self.assertTrue((self.B / d).is_dir(), d)

    def test_the_job_b_submission(self):
        (self.B / "control").mkdir(parents=True)
        (self.B / "control/gate-ok-b").write_text("")
        r = self.submit("rpd-b", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--time=02:00:00", self.args())
        self.assertIn("--job-name=fd_rpd_b", self.args())

    def test_job_a_refuses_before_stage_s_or_without_the_gate(self):
        r = self.submit("rpd-a", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("is missing", r.stderr)
        for d in ("staged", "flux", "control"):
            (self.B / d).mkdir(parents=True, exist_ok=True)
        r = self.submit("rpd-a", str(self.D), self.pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("the gate did not pass", r.stderr)
        self.assertFalse((self.tmp / "sbatch.args").exists() or (self.B / "dumps").exists())

    def test_job_a_refuses_an_existing_product_directory(self):
        for d in ("dumps", "n0", "unf-k2", "lanes-a"):
            with self.subTest(d=d):
                self.ready_a()
                (self.B / d).mkdir()
                r = self.submit("rpd-a", str(self.D), self.pin, str(self.B))
                self.assertEqual(r.returncode, 2)
                self.assertIn(f"{self.B}/{d} exists", r.stderr)
                shutil.rmtree(self.B)

    def test_job_a_refuses_a_dump_step_without_its_mcfile(self):
        self.ready_a()
        p = self.D / RELR / "rpd-a-steps.tsv"
        lines = p.read_text().splitlines()
        i = next(n for n, ln in enumerate(lines) if "\tnn_dump_inputs.py\t" in ln)
        f = lines[i].split("\t")
        j = f.index("--mcfile")
        lines[i] = "\t".join(f[:j] + f[j + 2:])
        p.write_text("\n".join(lines) + "\n")
        subprocess.run(["git", "-C", str(self.D), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "m"],
                       check=True, capture_output=True)
        pin = subprocess.run(["git", "-C", str(self.D), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        r = self.submit("rpd-a", str(self.D), pin, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("dump steps", r.stderr)

    def test_refuses_a_deploy_not_at_the_pin(self):
        self.ready_a()
        r = self.submit("rpd-a", str(self.D), "0" * 40, str(self.B))
        self.assertEqual(r.returncode, 2)
        self.assertIn("is not at", r.stderr)


if __name__ == "__main__":
    unittest.main()
