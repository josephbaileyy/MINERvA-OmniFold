"""Tests of RE-2 part B's layout (re2_partb_layout.py), its committed tables, and the charge gate (re2b_gate.py).

    python3 -m unittest 2d-unfolding/re2/tests/test_re2b.py
"""
import csv
import hashlib
import json
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import re2_partb_layout as layout  # noqa: E402
import re2b_gate as gate  # noqa: E402

try:
    import ROOT  # noqa: F401
    import re2_k1 as K
    from test_re2_readouts import root_xsec
    HAVE_ROOT = True
except Exception:  # pragma: no cover
    HAVE_ROOT = False

RE2 = layout.ST / "stageF/methods/re2/run"
J0_VARS = {"$LATBAX0": "$ACT/runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root",
           "$PUPA": "$P/inputs/runEventLoopOmniFold_PA.root", "$PUFPA": "$P/flux/runEventLoopMC_PA.root",
           "$PUALL": "$P/inputs/runEventLoopOmniFold_ALL.root", "$PUFALL": "$P/flux/runEventLoopMC_ALL.root"}
# J0 run -> the part-B run that repeats its argv (the J0 run timed that class)
SAME_ARGV = {"F_MaCCQE0": "U_MaCCQE_0", "F_Flux23": "U_Flux_23", "F_MaRES0": "U_MaRES_0",
             "F_NormDISCC0": "U_NormDISCC_0", "FL_BAX0": "S3_BeamAngleX0", "D_cv": "C0_cv", "D_unit": "C0_unit",
             "RF_PA": "pu_PA_s42", "RPR_PA_b01": "pu_PA_b01", **{f"RB_{i:03d}": f"S1_{i:03d}" for i in range(1, 9)}}


def options(args: str) -> dict:
    """argv as {option: value}; a flag maps to True. Order does not matter to argparse."""
    toks, out, i = shlex.split(args, posix=False), {}, 0
    while i < len(toks):
        if i + 1 < len(toks) and not toks[i + 1].startswith("--"):
            out[toks[i]] = toks[i + 1]
            i += 2
        else:
            out[toks[i]] = True
            i += 1
    return out


def read(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


class Layout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        t = Path(cls.tmp.name)
        cls.argv = ["--units", str(RE2 / "j0_readout/units.json"), "--runs-out", str(t / "runs.tsv"),
                    "--jobs-out", str(t / "jobs.tsv"), "--checks-out", str(t / "checks.tsv")]
        layout.main(cls.argv)
        cls.runs, cls.jobs, cls.checks = read(t / "runs.tsv"), read(t / "jobs.tsv"), read(t / "checks.tsv")

    def test_committed_tables_are_the_generators_output(self):
        for name, mine in (("partb_runs.tsv", "runs.tsv"), ("partb_jobs.tsv", "jobs.tsv"),
                           ("partb_checks.tsv", "checks.tsv")):
            self.assertEqual((RE2 / name).read_text(), (Path(self.tmp.name) / mine).read_text(), name)

    def test_counts(self):
        count = {}
        for r in self.runs:
            count[r["job"][:2]] = count.get(r["job"][:2], 0) + 1
        self.assertEqual(count, {"J1": 3, "J2": 175, "J3": 10, "J4": 300, "J6": 80, "J7": 39, "J8": 37})
        self.assertEqual(len({r["label"] for r in self.runs}), len(self.runs))

    def test_every_run_is_refined_400_31(self):
        for r in self.runs:
            o = options(r["args"])
            self.assertEqual((o["--bkg-mode"], o["--refine-n-estimators"], o["--refine-num-leaves"]),
                             ("negweight-refined", "400", "31"), r["label"])
            self.assertNotIn("purity", r["args"])

    def test_part_b_repeats_the_argv_j0_timed(self):
        j0 = {r["label"]: r for r in read(RE2 / "j0_runs.tsv")}
        b = {r["label"]: r for r in self.runs}
        for j0_label, b_label in SAME_ARGV.items():
            a = j0[j0_label]["args"]
            for k, v in J0_VARS.items():
                a = a.replace(k, v)
            self.assertEqual(options(a), options(b[b_label]["args"]), b_label)
            self.assertEqual(j0[j0_label]["cpus"], b[b_label]["cpus"], b_label)

    def test_er_repeats_c0_cv(self):
        b = {r["label"]: options(r["args"]) for r in self.runs}
        self.assertEqual(b["ER"], b["C0_cv"])

    def test_panel_seed42_equals_its_july_universe(self):
        # Muon_Energy_MINOS:0 is a panel universe but its band is a lateral, replaced by S3 in the rollup
        b = {r["label"]: options(r["args"]) for r in self.runs}
        in_j2 = [u for u in layout.PANEL_U if f"U_{u.replace(':', '_')}" in b]
        self.assertEqual([u for u in layout.PANEL_U if u not in in_j2], ["Muon_Energy_MINOS:0"])
        for u in in_j2:
            self.assertEqual(b[f"S4U_{u.replace(':', '')}_s42"], b[f"U_{u.replace(':', '_')}"], u)

    def test_universes_are_the_rollups(self):
        u = [options(r["args"])["--universe"] for r in self.runs if r["job"].startswith("J2")]
        self.assertEqual(sorted(u), sorted(layout.universes()))
        bands = {x.split(":")[0] for x in u}
        self.assertFalse(bands & {"Rvp1pi", "CV", "BeamAngleX", "Muon_Energy_MINOS"})
        self.assertEqual(sum(1 for x in u if x.startswith("Flux:")), 100)

    def test_limits_and_caps(self):
        for j in self.jobs:
            self.assertLess(gate.hours(j["limit"]), 12)
            self.assertGreaterEqual(gate.hours(j["limit"]), 1.25 * float(j["wall_s"]) / 3600)
            self.assertAlmostEqual(float(j["cap_node_h"]), gate.hours(j["limit"]), places=3)
        self.assertLessEqual(sum(float(j["cap_node_h"]) for j in self.jobs), 84.5245)

    def test_lanes_hold_the_declared_cpus(self):
        for j in self.jobs:
            lanes = {r["lane"] for r in self.runs if r["job"] == j["job"]}
            self.assertLessEqual(len(lanes), 256 // int(j["lane_cpus"]))
            for r in self.runs:
                if r["job"] == j["job"]:
                    self.assertLessEqual(int(r["cpus"]), int(j["lane_cpus"]))


    def test_checks_cover_what_is_declared(self):
        ids = [c["id"] for c in self.checks]
        self.assertEqual(len(ids), len(set(ids)))
        kinds = {k: [c for c in self.checks if c["kind"] == k] for k in ("le", "stream", "differs")}
        self.assertEqual(sum(map(len, kinds.values())), len(self.checks))
        boot = {r["label"] for r in self.runs if r["label"].startswith(("S1_", "S4B_"))}
        self.assertEqual({c["test"] for c in kinds["stream"]}, boot)
        self.assertEqual(len(boot), 380)
        for c in kinds["stream"]:
            self.assertTrue(c["ref"].endswith(f"/2dc_P_{c['test']}/xsec.root") and len(c["ref_sha256"]) == 64)
        powered = {c["test"] for c in kinds["differs"]}
        unis = {r["label"] for r in self.runs if r["label"].startswith("U_")}
        self.assertEqual(unis - powered, {"U_NormDISCC_0", "U_NormDISCC_1", "U_EtaNCEL_0", "U_EtaNCEL_1"})
        self.assertTrue({r["label"] for r in self.runs if r["label"].startswith("S3_")} <= powered)
        nulls = {c["test"] for c in kinds["le"] if c["id"].startswith("PB-null-")}
        self.assertEqual(nulls, {"U_NormDISCC_0", "U_NormDISCC_1"})
        for c in self.checks:
            if not c["ref"].startswith("run:"):
                self.assertEqual(len(c["ref_sha256"]), 64, c["id"])


def seed_of(args: str) -> int:
    return int(re.search(r"--seed\s+(\d+)", args).group(1))


@unittest.skipUnless(HAVE_ROOT, "needs PyROOT")
class DeclaredTables(unittest.TestCase):
    """re2_k1.py over the DECLARED part-B tables, with a synthetic output for each of the 644 runs: the verdict can
    be PASS, every health row uses its own seed + 3, and a wrong seed, a dead universe or a wrong stream fails
    exactly its own row."""

    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        d = cls.d = Path(cls.td.name)
        cls.runs = read(RE2 / "partb_runs.tsv")
        cls.checks = read(RE2 / "partb_checks.tsv")
        rng = np.random.default_rng(7)
        cls.eu = rng.uniform(1, 2, (14, 16))
        cls.eu.ravel()[:19] = 0.0
        root_xsec(d / "eu.root", cls.eu)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def factor(self, label: str) -> float:
        if label in ("ER", "C0_cv", "C0_unit", "U_NormDISCC_0", "U_NormDISCC_1") or \
                label.startswith(("pu_CTRL", "S4U_NormDISCC")):   # NormDISCC is a null band at every seed
            return 1.0
        if label.startswith(("U_", "S4U_")):
            u = label[2:] if label.startswith("U_") else label[4:].rsplit("_s", 1)[0]
            return 1.0 + 0.01 * (1 + sum(map(ord, u.replace("_", ""))) % 50)
        for prefix, f in (("S3_", 1.02), ("S1_", 1.03), ("S4B_", 1.04), ("S4CV_", 1.05), ("pu_PA_s42", 1.06),
                          ("pu_PA_b", 1.07), ("pu_PA_s43", 1.08), ("pu_", 1.09)):
            if label.startswith(prefix):
                return f
        raise KeyError(label)

    def build(self, bad_seed=None, dead=None, bad_stream=None):
        d = self.d
        shutil.rmtree(d / "partb", ignore_errors=True)
        out = d / "partb" / "out"
        for r in self.runs:
            lab = r["label"]
            ref = {"params": {"random_state": seed_of(r["args"]) + 3 - (3 if lab == bad_seed else 0),
                              "n_estimators": 400, "num_leaves": 31},
                   "clipped_fraction": 0.0, "refined_over_signed": 1.0, "background_stream": True,
                   "signed_sum": 89.0 if lab == bad_stream else 90.0}
            x = self.eu * (1.0 if lab == dead else self.factor(lab))
            root_xsec(out / lab / "xsec.root", x, ref, {"hEff2D": self.eu * 0.5},
                      {"p1Streams": {"sum": {"data": 100.0}}})
        for job in sorted({r["job"] for r in self.runs}):
            lines = [f"{hashlib.sha256((out / r['label'] / 'xsec.root').read_bytes()).hexdigest()}  "
                     f"{r['label']}/xsec.root" for r in self.runs if r["job"] == job]
            (d / "partb" / f"SHA256SUMS.{job}").write_text("\n".join(lines) + "\n")
        rows, n = ["id\tkind\ttest\tref\tref_sha256\thist\tmin_shift"], 0
        for c in self.checks:
            ref, sha = c["ref"], c["ref_sha256"]
            if not ref.startswith("run:"):
                p, n = d / "refs" / f"r{n}.root", n + 1
                if c["kind"] == "stream":   # Stage C's purity replica: its resampled background integrates to 10
                    b = np.zeros((14, 16)); b[0, 0] = 10.0
                    root_xsec(p, self.eu, None, {"hBkgRecoStar2D": b})
                else:                       # an external reference equal to the run it is compared with
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(out / c["test"] / "xsec.root", p)
                ref, sha = str(p), K.sha256_path(p)
            rows.append("\t".join([c["id"], c["kind"], c["test"], ref, sha, c["hist"], c["min_shift"]]))
        (d / "checks.tsv").write_text("\n".join(rows) + "\n")
        K.main(["--runs", str(RE2 / "partb_runs.tsv"), "--checks", str(d / "checks.tsv"), "--out-dir", str(out),
                "--eu", str(d / "eu.root"), "--expect-eu-sha256", K.sha256_path(d / "eu.root"),
                "--result", str(d / "k1.json"), "--sums-glob", "SHA256SUMS.J[1-8]*"])
        return json.loads((d / "k1.json").read_text())

    def failed(self, r):
        return ([x["id"] for x in r["checks"] if x["verdict"] != "PASS"],
                [x["label"] for x in r["health"] if x["verdict"] != "PASS"])

    def test_declared_tables_can_pass(self):
        r = self.build()
        self.assertEqual(self.failed(r), ([], []))
        self.assertEqual(len(r["health"]), 644)
        self.assertEqual(r["sums"]["n_listed"], 644)
        self.assertEqual(r["verdict"], "PASS")

    def test_each_defect_fails_its_own_row(self):
        r = self.build(bad_seed="S4B_s48_07", dead="U_MaCCQE_1", bad_stream="S1_150")
        self.assertEqual(self.failed(r), (["PB-stream-S1_150", "PB-pow-U_MaCCQE_1"], ["S4B_s48_07"]))
        self.assertEqual(r["verdict"], "FAIL")


class Gate(unittest.TestCase):
    JOBS = {"J2a": {"cap": 8.9, "projected": 7.1, "gated": False},
            "J4a": {"cap": 8.1, "projected": 6.5, "gated": False},
            "J7": {"cap": 7.8, "projected": 6.2, "gated": True}}

    def row(self, state, elapsed, billing=256):
        return {"State": state, "ElapsedRaw": str(elapsed), "AllocTRES": f"billing={billing},cpu=256,node=1"}

    def test_pass_when_caps_fit(self):
        out = gate.decide(self.JOBS, 5.4755, {}, {}, ["J2a", "J4a", "J7"])
        self.assertEqual(out["verdict"], "PASS")
        self.assertAlmostEqual(out["wanted"][-1]["used_after"], 8.9 + 8.1 + 7.8)

    def test_refuse_when_a_cap_would_cross_room(self):
        out = gate.decide(self.JOBS, 75.0, {}, {}, ["J2a", "J4a"])  # room 15: 8.9 fits, 8.9 + 8.1 does not
        self.assertEqual([w["verdict"] for w in out["wanted"]], ["PASS", "REFUSE"])
        self.assertEqual(out["verdict"], "REFUSE")

    def test_running_job_reserves_its_cap_and_ended_job_its_charge(self):
        sub = {"J2a": "1", "J4a": "2"}
        sacct = {"1": self.row("RUNNING", 100), "2": self.row("COMPLETED", 3600 * 6)}
        out = gate.decide(self.JOBS, 5.4755, sub, sacct, ["J7"])
        self.assertAlmostEqual(out["used_before"], 8.9 + 6.0)
        self.assertEqual(out["wanted"][0]["director_form"], {"ledgered": 6.0, "projected": 6.2, "ok": True})

    def test_missing_from_sacct_counts_its_cap(self):
        out = gate.decide(self.JOBS, 5.4755, {"J2a": "9"}, {}, ["J7"])
        self.assertAlmostEqual(out["used_before"], 8.9)

    def test_cancelled_counts_its_charge(self):
        out = gate.decide(self.JOBS, 5.4755, {"J2a": "1"}, {"1": self.row("CANCELLED by 1", 1800)}, ["J7"])
        self.assertAlmostEqual(out["used_before"], 0.5)

    def test_already_submitted_is_refused(self):
        out = gate.decide(self.JOBS, 5.4755, {"J7": "3"}, {"3": self.row("COMPLETED", 60)}, ["J7"])
        self.assertEqual(out["wanted"][0]["reason"], "already submitted")

    def test_main_reads_files_and_refuses_a_bad_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "jobs.tsv").write_text("job\tgated\tprojected_node_h\tcap_node_h\nJ7\tyes\t6.2\t7.8\n")
            (d / "led.tsv").write_text("jobid\tcharge_node_h\n1\t4.0386\n2\t1.4369\n")
            (d / "sub.log").write_text("")
            (d / "s.psv").write_text("")
            argv = ["--jobs", str(d / "jobs.tsv"), "--j0-ledger", str(d / "led.tsv"), "--submissions",
                    str(d / "sub.log"), "--sacct", str(d / "s.psv"), "--want", "J7"]
            self.assertEqual(gate.main(argv), 0)
            (d / "led.tsv").write_text("jobid\tcharge_node_h\n1\t4.0386\n")
            with self.assertRaises(SystemExit):
                gate.main(argv)


if __name__ == "__main__":
    unittest.main()
