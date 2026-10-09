"""Synthetic tests of the N2 harness: identity and split checks, the frozen plan, member records,
admission, and guarded synthetic campaigns. No ROOT, OmniFold, real input or job.

    python3 -m unittest discover -s 2d-unfolding/uq/coverage_fixed_truth/n2 -p 'test_*.py' -v
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
from n2 import design, execution as gx, identity, members as mb  # noqa: E402
import toy_design as td  # noqa: E402

SALT = "n2-synthetic-salt"
THRESH = {"development": 0.02, "reservoir": 0.5}
N2_FILES = ("__init__.py", "execution.py", "design.py", "identity.py", "members.py", "harness.py",
            "synthetic_producer.py")
N2_DIR = "2d-unfolding/uq/coverage_fixed_truth/n2"


def tables(n=6000, n_bkg=800, seed=3):
    """Signal rows (with truth-only misses), the same keys as truth denominators, distinct
    background keys; two playlists."""
    rng = np.random.default_rng(seed)
    src = np.where(rng.uniform(size=n) < 0.6, "P1", "P2")
    run, sub, nth = rng.integers(1, 50, n), rng.integers(1, 20, n), np.arange(n)
    w = rng.uniform(0.5, 1.5, n)
    sig = {"source": src, "mc_run": run, "mc_subrun": sub, "mc_nthEvtInFile": nth, "w_truth": w}
    den = {k: v.copy() for k, v in sig.items()}
    bsrc = np.where(rng.uniform(size=n_bkg) < 0.6, "P1", "P2")
    bkg = {"source": bsrc, "mc_run": rng.integers(1, 50, n_bkg),
           "mc_subrun": rng.integers(1, 20, n_bkg), "mc_nthEvtInFile": n + np.arange(n_bkg),
           "w_truth": rng.uniform(0.5, 1.5, n_bkg)}
    return {"mc_signal_reco": sig, "mc_truth_denom": den, "mc_background": bkg}


def move_row(fold_tables, tree, key_index, src, dst):
    """Move one row of ``tree`` from fold ``src`` to fold ``dst``."""
    out = copy.deepcopy(fold_tables)
    a, b = out[src][tree], out[dst][tree]
    for c in a:
        b[c] = np.concatenate([b[c], a[c][key_index:key_index + 1]])
        a[c] = np.delete(a[c], key_index)
    return out


class Identity(unittest.TestCase):
    def setUp(self):
        self.t = tables()
        self.ft = identity.materialize(self.t, SALT, THRESH)
        self.man = identity.manifest(identity.fold_keys(self.ft), SALT, THRESH)

    def test_positive_control_all_table_checks_hold(self):
        folds = identity.run_all(self.ft, self.man)
        self.assertEqual(sum(len(v) for v in folds["mc_signal_reco"].values()), 6000)

    def test_missing_ids_are_refused(self):
        for label, mutate in (
                ("column", lambda t: t["mc_signal_reco"].pop("mc_subrun")),
                ("negative", lambda t: t["mc_signal_reco"]["mc_run"].__setitem__(5, -1)),
                ("empty source", lambda t: t["mc_signal_reco"]["source"].__setitem__(5, ""))):
            with self.subTest(label):
                t = copy.deepcopy(self.t)
                mutate(t)
                with self.assertRaises(identity.IdentityError):
                    identity.materialize(t, SALT, THRESH)

    def test_a_repeated_identity_is_a_stop_condition(self):
        t = copy.deepcopy(self.t)
        t["mc_signal_reco"]["mc_nthEvtInFile"][7] = t["mc_signal_reco"]["mc_nthEvtInFile"][8]
        for c in ("source", "mc_run", "mc_subrun"):
            t["mc_signal_reco"][c][7] = t["mc_signal_reco"][c][8]
        with self.assertRaisesRegex(identity.IdentityError, "stop condition"):
            identity.materialize(t, SALT, THRESH)

    def test_c1_fires_when_a_reservoir_key_is_moved_into_training(self):
        moved = move_row(self.ft, "mc_signal_reco", 0, "reservoir", "training")
        with self.assertRaisesRegex(identity.IdentityError, "C1"):
            identity.check_c1_disjoint(identity.fold_keys(moved))
        with self.assertRaises(identity.IdentityError):
            identity.run_all(moved, self.man)

    def test_c2_fires_when_a_truth_denominator_row_is_dropped(self):
        ft = copy.deepcopy(self.ft)
        ft["training"]["mc_truth_denom"] = {c: v[1:] for c, v in
                                            ft["training"]["mc_truth_denom"].items()}
        with self.assertRaisesRegex(identity.IdentityError, "C2"):
            identity.check_c2_bijection(identity.fold_keys(ft))

    def test_c3_fires_on_a_key_in_signal_and_background(self):
        ft = copy.deepcopy(self.ft)
        b, s = ft["training"]["mc_background"], ft["training"]["mc_signal_reco"]
        for c in identity.KEY:
            b[c] = np.concatenate([b[c], s[c][:1]])
        b["w_truth"] = np.concatenate([b["w_truth"], [1.0]])
        with self.assertRaisesRegex(identity.IdentityError, "C3"):
            identity.check_c3_signal_background(identity.fold_keys(ft))

    def test_c4_fires_on_one_perturbed_value(self):
        prod = {"w_truth": self.t["mc_signal_reco"]["w_truth"]}
        rebuilt = {"w_truth": prod["w_truth"].copy()}
        identity.check_c4_rows_equal(prod, rebuilt, ["w_truth"])
        rebuilt["w_truth"][3] = np.nextafter(rebuilt["w_truth"][3], 9)
        with self.assertRaisesRegex(identity.IdentityError, "C4"):
            identity.check_c4_rows_equal(prod, rebuilt, ["w_truth"])

    def test_c5_fires_on_a_biased_threshold(self):
        biased = identity.materialize(self.t, SALT, {"development": 0.02, "reservoir": 0.56})
        with self.assertRaisesRegex(identity.IdentityError, "C5"):
            identity.check_c5_fractions(biased, THRESH)
        with self.assertRaises(identity.IdentityError):
            identity.check_rule(identity.fold_keys(biased), SALT, THRESH)

    def test_c6_fires_on_a_reservoir_row_in_the_bank(self):
        folds = identity.fold_keys(self.ft)
        ok = {"bank": sorted(folds["mc_signal_reco"]["training"]),
              "background_template": sorted(folds["mc_background"]["training"]),
              "pseudo_data": sorted(folds["mc_signal_reco"]["reservoir"])}
        identity.check_c6_sidecar(folds, ok, design.INTENDED_FOLDS)
        bad = dict(ok, bank=ok["bank"] + ok["pseudo_data"][:1])
        with self.assertRaisesRegex(identity.IdentityError, "C6"):
            identity.check_c6_sidecar(folds, bad, design.INTENDED_FOLDS)
        with self.assertRaisesRegex(identity.IdentityError, "C6"):
            identity.check_c6_sidecar(folds, {"bank": ok["bank"]}, design.INTENDED_FOLDS)

    def test_the_manifest_binds_the_materialized_folds(self):
        moved = move_row(self.ft, "mc_background", 0, "training", "development")
        with self.assertRaisesRegex(identity.IdentityError, "differ"):
            identity.verify_manifest(self.man, identity.fold_keys(moved))
        tampered = dict(self.man, salt="other")
        with self.assertRaisesRegex(identity.IdentityError, "digest"):
            identity.verify_manifest(tampered, identity.fold_keys(self.ft))


class Design(unittest.TestCase):
    def test_the_plan_streams_seeds_and_estimator(self):
        plan = design.validate_plan(design.members())
        T = [m for m in plan if m["arm"] == "T"]
        B = [m for m in plan if m["arm"] == "B"]
        self.assertEqual((len(T), len(B)), (50, 50))
        self.assertTrue(all(m["mc_stream"] == "held" for m in plan))
        self.assertTrue(all(m["boot_seed"] is None for m in T))
        self.assertEqual({m["base"] for m in B}, {"T001"})
        self.assertEqual({m["data_seed"] for m in B}, {T[0]["data_seed"]})
        self.assertEqual(T[0]["data_seed"], 20_261_008_000_001)
        self.assertEqual([m["boot_seed"] for m in B][:2], [20_261_008_201_001, 20_261_008_201_002])
        seeds = [m["data_seed"] for m in T] + [m["boot_seed"] for m in B]
        self.assertEqual(len(set(seeds)), 100)
        used = set(td.PRODUCTION_DATA_SEEDS) | set(td.PRODUCTION_MC_SEEDS) | \
            set(td.OLD_TOY_DATA_SEEDS) | set(td.OLD_TOY_MC_SEEDS)
        used |= {s for t in (1, td.MAX_TOY_INDEX) for s in td.toy_seeds(t)}
        used |= {td.bootstrap_seed(b) for b in (1, td.MAX_BOOT_INDEX)}
        self.assertFalse(set(seeds) & used)
        self.assertGreater(min(seeds), max(used))

    def test_any_departure_from_the_frozen_plan_is_refused(self):
        for label, edit in (
                ("estimator", lambda p: p[3].__setitem__("estimator",
                                                         dict(p[3]["estimator"], threads=128))),
                ("mc stream", lambda p: p[60].__setitem__("mc_stream", "bootstrap")),
                ("base", lambda p: p[70].__setitem__("base", "T002")),
                ("seed", lambda p: p[10].__setitem__("data_seed", 1)),
                ("dropped member", lambda p: p.pop())):
            with self.subTest(label):
                plan = design.members()
                edit(plan)
                with self.assertRaises(design.DesignError):
                    design.validate_plan(plan)

    def arms(self, b_over_t, seed=1):
        rng = np.random.default_rng(seed)
        m = rng.uniform(1, 3, design.N_REPORTED_BINS)
        XT = m * (1 + 0.01 * rng.standard_normal((50, m.size)))
        XB = XT[0] * (1 + b_over_t * 0.01 * rng.standard_normal((50, m.size)))
        return [{"spec": {"arm": "T"}, "values": v} for v in XT] + \
               [{"spec": {"arm": "B"}, "values": v} for v in XB]

    def test_the_statistic_recovers_the_known_ratio_and_the_rule(self):
        for b_over_t, verdict in ((1.0, "faithful"), (1.6, "over-scatter"),
                                  (0.6, "under-scatter")):
            with self.subTest(b_over_t):
                r = design.evaluate(self.arms(b_over_t))
                self.assertEqual(r["verdict"], verdict)
                self.assertAlmostEqual(r["M"], b_over_t, delta=0.08 * b_over_t)
        self.assertEqual(design.classify([0.9, 1.3]), "INCONCLUSIVE")
        self.assertEqual(design.classify([0.7, 0.9]), "INCONCLUSIVE")

    def test_records_need_the_frozen_estimator_and_finite_values(self):
        m = design.members()[0]
        good = {"estimator": design.FROZEN_ESTIMATOR, "values": [1.0] * design.N_REPORTED_BINS}
        design.check_record(m, good)
        for bad in (dict(good, estimator=dict(design.FROZEN_ESTIMATOR, seed=2)),
                    dict(good, values=[1.0] * 204), dict(good, values=[np.nan] * 205)):
            with self.assertRaises(design.DesignError):
                design.check_record(m, bad)


class Members(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_write_new_never_overwrites(self):
        p = mb.write_new(self.root / "a" / "x.json", "first")
        with self.assertRaisesRegex(mb.MemberError, "refusing to overwrite"):
            mb.write_new(p, "second")
        self.assertEqual(p.read_text(), "first")
        self.assertEqual(sorted(os.listdir(p.parent)), ["x.json"])

    def test_the_ledger_keeps_every_declared_member(self):
        plan = [{"id": f"M{i}"} for i in range(4)]
        d = mb.plan_digest(plan)
        mb.write_new(mb.result_path(self.root, "M0"),
                     json.dumps({"member": "M0", "plan_sha256": d, "spec": plan[0]}))
        mb.write_new(mb.result_path(self.root, "M1"),
                     json.dumps({"member": "M1", "plan_sha256": "other", "spec": plan[1]}))
        mb.record_failure(self.root, "M2", d, 1, "crashed")
        states = [s for _, s, _ in mb.ledger(plan, self.root, d)]
        self.assertEqual(states, ["ok", "failed", "failed", "missing"])
        with self.assertRaisesRegex(mb.MemberError, "3 of 4"):
            mb.require_complete(mb.ledger(plan, self.root, d))
        self.assertEqual(mb.summary(mb.ledger(plan, self.root, d))["counts"],
                         {"ok": 1, "failed": 2, "missing": 1})


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
                           "-c", "user.name=fixture", "-c", "user.email=fixture@invalid", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


class Harness(unittest.TestCase):
    """A throwaway checkout with the guard and the n2 package, committed, and synthetic folds."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name).resolve()
        cls.root = root = base / "checkout"
        (root / "nd-unfolding").mkdir(parents=True)
        (root / "VALIDATION_LEDGER.md").write_text("# fixture\n")
        shutil.copy2(REPO / "nd-unfolding/mnv_guarded_run.py", root / "nd-unfolding")
        shutil.copytree(REPO / "nd-unfolding/mnv_guard_shim", root / "nd-unfolding/mnv_guard_shim",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (root / N2_DIR).mkdir(parents=True)
        for f in N2_FILES:
            shutil.copy2(REPO / N2_DIR / f, root / N2_DIR / f)
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "fixture")
        cls.inputs = inputs = base / "inputs"
        ft = identity.materialize(tables(), SALT, THRESH)
        for fold, trees in ft.items():
            (inputs / "folds" / fold).mkdir(parents=True)
            for tree, cols in trees.items():
                np.savez(inputs / "folds" / fold / f"{tree}.npz", **cols)
        cls.split = inputs / "split.json"
        cls.split.write_text(json.dumps(identity.manifest(identity.fold_keys(ft), SALT, THRESH)))
        cls.harness = root / N2_DIR / "harness.py"
        cls.plan = base / "plan.json"
        cp = cls.run_harness("plan", "--out", cls.plan)
        assert cp.returncode == 0, cp.stderr
        cls.base = base

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def run_harness(cls, *args):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1")
        return subprocess.run([sys.executable, str(cls.harness), *map(str, args)],
                              capture_output=True, text=True, env=env)

    def admission(self, name, world, **override):
        code = {"commit": git(self.root, "rev-parse", "HEAD"),
                "modules": {f"{N2_DIR}/{f}": gx.sha256_hex((self.root / N2_DIR / f).read_bytes())
                            for f in N2_FILES}}
        wpath = self.base / f"{name}.world.json"
        wpath.write_text(json.dumps(world))
        adm = {"design": "N2", "design_sha256": design.design_digest(), "synthetic": True,
               "plan_sha256": json.loads(self.plan.read_text())["plan_sha256"],
               "producer": f"{N2_DIR}/synthetic_producer.py", "code": code,
               "inputs": {"split_manifest": {"path": str(self.split),
                                             "sha256": gx.sha256_hex(self.split.read_bytes())},
                          "fold_tables": {"path": str(self.inputs / "folds")},
                          "synthetic_world": {"path": str(wpath)}},
               "outroot": str(self.base / name)}
        adm.update(override)
        path = self.base / f"{name}.admission.json"
        path.write_text(json.dumps(adm))
        return path

    def auth(self):
        return {"path": "VALIDATION_LEDGER.md",
                "sha256": gx.sha256_hex((self.root / "VALIDATION_LEDGER.md").read_bytes())}

    def test_no_or_incomplete_admission_refuses_a_launch(self):
        cp = self.run_harness("run-member", "--admission", self.base / "absent.json",
                              "--plan", self.plan, "--member", "T001")
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT)
        self.assertIn("not admitted", cp.stderr)
        world = {"mean_seed": 1, "sigma_T": 0.01, "b_over_t": 1.0}
        for label, override, needle in (
                ("real, synthetic producer", {"synthetic": False, "authorization": {
                    "path": "VALIDATION_LEDGER.md", "sha256": "0"}}, "synthetic producer"),
                ("real, no authorization", {"synthetic": False, "producer": "x.py"},
                 "lacks ['authorization']"),
                ("real, no producer digest", {"synthetic": False, "producer": "x.py",
                                              "authorization": self.auth()},
                 "digest for its producer"),
                ("real, no rebuild", {"synthetic": False, "producer": "x.py",
                                      "authorization": self.auth(),
                                      "code": {"commit": git(self.root, "rev-parse", "HEAD"),
                                               "modules": {"x.py": "0" * 64}}},
                 "identity-carrying rebuild"),
                ("real, wrong authorization digest", {
                    "synthetic": False, "producer": "x.py",
                    "authorization": dict(self.auth(), sha256="0" * 64),
                    "code": {"commit": git(self.root, "rev-parse", "HEAD"),
                             "modules": {"x.py": "0" * 64}}}, "authorization record"),
                ("other design", {"design_sha256": "0" * 64}, "not this design.py"),
                ("other commit", {"code": {"commit": "0" * 40, "modules": {
                    f"{N2_DIR}/synthetic_producer.py": "x"}}}, "not this checkout's HEAD")):
            with self.subTest(label):
                adm = self.admission(f"refuse-{label.replace(' ', '_').replace(',', '')}",
                                     world, **override)
                cp = self.run_harness("run-member", "--admission", adm, "--plan", self.plan,
                                      "--member", "T001")
                self.assertEqual(cp.returncode, gx.REFUSAL_EXIT, cp.stderr)
                self.assertIn(needle, cp.stderr)
                self.assertFalse((self.base / json.loads(adm.read_text())["outroot"]).exists())

    def test_a_synthetic_campaign_runs_guarded_and_recovers_the_known_answer(self):
        """Positive control: 100 guarded members, strict provenance, verdict 'faithful'."""
        adm = self.admission("faithful", {"mean_seed": 1, "sigma_T": 0.01, "b_over_t": 1.0})
        self.assertEqual(self.run_harness("admit", "--admission", adm).returncode, 0)
        for m in design.members():
            cp = self.run_harness("run-member", "--admission", adm, "--plan", self.plan,
                                  "--member", m["id"])
            self.assertEqual(cp.returncode, 0, f"{m['id']}: {cp.stderr[-2000:]}")
        out = self.base / "faithful.result.json"
        cp = self.run_harness("aggregate", "--admission", adm, "--plan", self.plan, "--out", out)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        res = json.loads(out.read_text())
        self.assertEqual(res["verdict"], "faithful")
        self.assertEqual(res["ledger"]["counts"], {"ok": 100, "failed": 0, "missing": 0})
        self.assertAlmostEqual(res["M"], 1.0, delta=0.08)
        rec = json.loads(mb.result_path(self.base / "faithful", "B007").read_text())
        self.assertTrue(rec["provenance"]["strict"])
        self.assertEqual(rec["provenance"]["guard"]["expect_root"], str(self.root))
        inv = (self.base / "faithful" / "inventory" / "B007.jsonl").read_text()
        self.assertIn("N2 B007", inv)
        # the result is never overwritten
        cp = self.run_harness("aggregate", "--admission", adm, "--plan", self.plan, "--out", out)
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT)
        cp = self.run_harness("run-member", "--admission", adm, "--plan", self.plan,
                              "--member", "T001")
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT)
        self.assertIn("never overwritten", cp.stderr)

    def test_failed_contaminated_and_missing_members_are_reported_not_dropped(self):
        adm = self.admission("broken", {"mean_seed": 1, "sigma_T": 0.01, "b_over_t": 1.0,
                                        "contaminate": ["T003"], "fail": ["B007"]})
        ran = ["T001", "T002", "T003", "T004", "B001", "B007"]
        codes = {m: self.run_harness("run-member", "--admission", adm, "--plan", self.plan,
                                     "--member", m).returncode for m in ran}
        self.assertEqual(codes["B007"], 1)
        self.assertEqual({m: c for m, c in codes.items() if m != "B007"},
                         {m: 0 for m in ran if m != "B007"})
        out = self.base / "broken.result.json"
        cp = self.run_harness("aggregate", "--admission", adm, "--plan", self.plan, "--out", out)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        res = json.loads(out.read_text())
        self.assertEqual(res["verdict"], "INCONCLUSIVE")
        self.assertNotIn("M", res)
        self.assertEqual(res["ledger"]["counts"], {"ok": 4, "failed": 2, "missing": 94})
        by = {e["member"]: e for e in res["ledger"]["not_ok"]}
        self.assertIn("C6", by["T003"]["detail"]["reason"])
        self.assertEqual(by["B007"]["detail"]["status"], 1)
        self.assertEqual(by["T005"]["state"], "missing")

    def test_a_real_member_must_record_the_frozen_thread_count(self):
        from n2 import harness
        member = design.members()[0]
        head = git(self.root, "rev-parse", "HEAD")
        rec = {"estimator": design.FROZEN_ESTIMATOR, "values": [1.0] * design.N_REPORTED_BINS,
               "sidecar": {}, "provenance": {
                   "strict": True, "guard": {"expect_root": str(harness.REPO)},
                   "git": {"commit": head, "mismatched": []},
                   "environment": {"threads": {"OMP_NUM_THREADS": "32"}}}}
        check = harness.member_checker({"synthetic": False, "code": {"commit": head}}, {})
        with self.assertRaisesRegex(mb.MemberError, "OMP_NUM_THREADS"):
            check(member, rec)

    def test_an_edited_plan_is_refused(self):
        adm = self.admission("edited", {"mean_seed": 1, "sigma_T": 0.01, "b_over_t": 1.0})
        plan = json.loads(self.plan.read_text())
        plan["members"][0]["estimator"] = dict(plan["members"][0]["estimator"], iters=4)
        edited = self.base / "edited-plan.json"
        edited.write_text(json.dumps(plan))
        cp = self.run_harness("run-member", "--admission", adm, "--plan", edited, "--member",
                              "T001")
        self.assertEqual(cp.returncode, gx.REFUSAL_EXIT)
        self.assertIn("departs from the design", cp.stderr)


if __name__ == "__main__":
    unittest.main()
