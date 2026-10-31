"""Controls for F1's new code (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 5), on
synthetic inputs and the committed records. No real product, event or data value is read, and nothing needs ROOT.

* fd_f1_prep: the config replaces the vertices only; the bridge carries r unchanged, and through s5e_deform's
  ratio_nd truth it reweights every truth row exactly as pvl_lib.row_weight does, up to ratio_nd's one constant.
* fd_f1_tasks: the lane plan covers each truth's 20 seeds once with one closure each; every pseudo-experiment step
  is the committed W2 line with only the declared fields changed; the seeds appear in no committed task table.
* fd_f1_lane: steps in order, stop at the first failure, refuse an entrypoint outside nd-unfolding.
* fd_f1_budget: GO and STOP on each side of both rules.
* gen5d_v3: the flux contents, the spline-header check on synthetic spline files, the refusal rules.
* fd_f0_regrade's F1 option: on F0's synthetic tree, the F1 truths are graded by hand-recomputed statistics in their
  own group, control 9 holds, and each F1 input refuses on a one-entry defect.
* the batch scripts agree with the budget's constants, and run_gevgen_v3.sh's spline filter is reduce_splines.sh's."""
import contextlib
import gzip
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
# F1c's own step table: committed after F1c ran (fd/receipts-f1/run/s10.out:9 records these bytes), so the no-reuse scan
# below excludes exactly this file at exactly this digest.
F1C_STEPS = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/f1c/f1c-steps.tsv"
F1C_STEPS_SHA256 = "70b287c372855e2bd10eaeab6febd4fe56c106a9ebea03ff437a65d0a2e88679"
GENIE = REPO / "3d-unfolding" / "genie"
for p in (str(ND), str(ND / "pv-ladder"), str(GENIE), str(Path(__file__).resolve().parent)):
    if p not in sys.path:
        sys.path.insert(1, p)
import fd_f1_budget as BUD  # noqa: E402
import fd_f1_lane as LANE  # noqa: E402
import fd_f1_prep as PREP  # noqa: E402
import fd_f1_tasks as TASKS  # noqa: E402
import gen5d_v3 as V3  # noqa: E402
import pvl_lib as L  # noqa: E402
import s5e_deform  # noqa: E402
import fd_f0_regrade as F  # noqa: E402
import test_fd_f0_regrade as T0  # noqa: E402

STATE = REPO / "docs/orchestration/state"
N5 = int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5]))


def digest(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)



def seed_hits(root: Path) -> tuple[list[str], int, list[str]]:
    """--pseudo-seed(s) in every .tsv and .sh under root that overlap F1's seeds: (hits, matches seen, files skipped)."""
    pat = re.compile(r"--pseudo-seeds?\s+(\d+)(?::(\d+))?")
    lo, hi = min(TASKS.SEEDS.values()), max(TASKS.SEEDS.values()) + TASKS.N_PE - 1
    hits, n, skipped = [], 0, []
    for p in sorted([*root.rglob("*.tsv"), *root.rglob("*.sh")]):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        if rel == F1C_STEPS and hashlib.sha256(p.read_bytes()).hexdigest() == F1C_STEPS_SHA256:
            skipped.append(rel)
            continue
        for m in pat.finditer(p.read_text(errors="ignore")):
            n += 1
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a <= hi and b >= lo:
                hits.append(f"{rel}: {m.group(0)}")
    return hits, n, skipped

class Prep(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-prep-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def ratio(self, seed=0, **extra):
        r = np.random.default_rng(seed).uniform(0.7, 1.3, N5)
        return {"schema": L.RATIO_SCHEMA, "vertex": "genie_v3_g18", "label": "x", "axes": list(L.AXES5),
                "edges": {a: list(L.FINE[a]) for a in L.AXES5}, "r": r.tolist(), "k": 0.98, **extra}

    def test_config_replaces_the_vertices_only(self):
        base = json.loads((ND / "pv-ladder/config.json").read_text())
        cfg = PREP.f1_config(base, {"genie_v3_g18": ("/p/g.npz", "a" * 64), "genie_v3_ar23": ("/p/a.npz", "b" * 64)})
        for k in ("schema", "ratio", "rungs", "reference", "declaration"):
            self.assertEqual(cfg[k], base[k], k)
        self.assertEqual(sorted(cfg["vertices"]), ["genie_v3_ar23", "genie_v3_g18"])
        self.assertEqual(cfg["vertices"]["genie_v3_g18"]["sha256"], "a" * 64)
        self.assertNotIn("pz_max", cfg["vertices"]["genie_v3_g18"])
        with self.assertRaises(SystemExit):
            PREP.f1_config(base, {"genie_v3_g18": ("/p", "a" * 64)})

    def test_bridge_carries_r_unchanged(self):
        src = self.tmp / "g.json"
        rat = self.ratio()
        src.write_text(json.dumps(rat))
        b = PREP.bridge(rat, src)
        self.assertEqual((b["schema"], b["axes"], b["kind"]), ("s5e-shape-ratio/1", [0, 1, 2, 3, 4], "pvl-ratio-5d"))
        self.assertEqual(b["shape_ratio"], rat["r"])
        self.assertEqual(b["edges"], [list(L.FINE[a]) for a in L.AXES5])
        self.assertEqual(b["source"]["sha256"], digest(src))

    def test_bridge_refusals(self):
        src = self.tmp / "g.json"
        src.write_text("{}")
        for bad in (dict(self.ratio(), schema="other"), dict(self.ratio(), axes=["pt", "pz"]),
                    dict(self.ratio(), r=[1.0] * 10), dict(self.ratio(), r=[0.0] + [1.0] * (N5 - 1)),
                    self.ratio(truth_cut={"axis": "pz", "below": 10.0})):
            with self.subTest(keys=sorted(bad)), self.assertRaises(SystemExit):
                PREP.bridge(bad, src)

    def test_ratio_nd_reweights_as_row_weight_up_to_one_constant(self):
        rng = np.random.default_rng(3)
        n = 4000
        cols = [rng.uniform(L.FINE[a][0], L.FINE[a][-1] * (0.2 if a in ("eavail", "q3", "W") else 1.0), n)
                for a in L.AXES5]
        gen = np.column_stack(cols)
        gen[:5, 0] = L.FINE["pt"][-1]                       # the last edge belongs to the last bin in both
        pass_truth = np.ones(n, bool)
        pass_truth[-300:] = False
        gen[-300:] = -9999.0                                # rows outside the truth selection carry a sentinel
        w = rng.uniform(0.5, 1.5, n)
        rat = self.ratio(seed=5)
        r_pvl = L.row_weight(gen, L.AXES5, rat, pass_truth)
        src = self.tmp / "g.json"
        src.write_text(json.dumps(rat))
        r_nd = s5e_deform.ratio_weight(gen, [np.asarray(L.FINE[a]) for a in L.AXES5], w, PREP.bridge(rat, src), 1.0)
        c = r_nd[:-300] / r_pvl[:-300]
        np.testing.assert_allclose(c, c[0], rtol=1e-12)
        np.testing.assert_array_equal(r_nd[-300:], 1.0)
        np.testing.assert_array_equal(r_pvl[-300:], 1.0)
        self.assertAlmostEqual(float((w * r_nd).sum()), float(w.sum()), delta=1e-9 * w.sum())

    def test_main_end_to_end_with_the_ratio_step_stubbed(self):
        preds = {}
        for k in PREP.TRUTHS:
            p = self.tmp / f"{k}.npz"
            p.write_bytes(k.encode())
            preds[k] = p

        def fake_ratios(argv):
            out = Path(argv[argv.index("--out") + 1]) / PREP.RUNG
            out.mkdir(parents=True)
            cfg = json.loads(Path(argv[argv.index("--config") + 1]).read_text())
            for k in cfg["vertices"]:
                (out / f"{k}.json").write_text(json.dumps(self.ratio()))
            return 0
        argv = [x for k, p in preds.items() for x in ("--pred", f"{k}={p}={digest(p)}")] + ["--out", str(self.tmp / "o")]
        with mock.patch.object(PREP.pvl_ratios, "main", fake_ratios):
            self.assertEqual(quiet(PREP.main, argv), 0)
        sums = TASKS.load_sums(self.tmp / "o/f1-prep-SHA256SUMS")
        for k in PREP.TRUTHS:
            self.assertEqual(sums[f"bridged/{k}.json"], digest(self.tmp / f"o/bridged/{k}.json"))
            self.assertIn(f"ratios/L-5D-PV/{k}.json", sums)
        self.assertIn("config-f1.json", sums)
        with self.assertRaises(SystemExit):                              # refuses an existing --out
            quiet(PREP.main, argv)
        bad = list(argv)
        bad[1] = bad[1][:-1] + ("0" if bad[1][-1] != "0" else "1")
        with self.assertRaises(SystemExit):                              # refuses a prediction off its sha256
            quiet(PREP.main, bad[:-1] + [str(self.tmp / "o2")])


class Tasks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-tasks-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.sums = self.tmp / "f1-prep-SHA256SUMS"
        self.sums.write_text("".join(f"{c * 64}  ./{rel}\n" for c, rel in (
            ("1", "ratios/L-5D-PV/genie_v3_g18.json"), ("2", "bridged/genie_v3_g18.json"),
            ("3", "ratios/L-5D-PV/genie_v3_ar23.json"), ("4", "bridged/genie_v3_ar23.json"))))

    def test_plan(self):
        TASKS.check_plan()
        for bad in (TASKS.LANES[:-1], TASKS.LANES[:2] + ((2, "genie_v3_g18", False, 3, 7),) + TASKS.LANES[3:],
                    ((0, "genie_v3_g18", True, 0, 4), (1, "genie_v3_ar23", False, 0, 4)) + TASKS.LANES[2:]):
            with self.subTest(), mock.patch.object(TASKS, "LANES", bad), self.assertRaises(SystemExit):
                TASKS.check_plan()

    def test_steps_are_the_committed_lines_with_only_the_declared_fields_changed(self):
        rows = TASKS.steps(self.sums, "/P/prep", "/P/runs")
        w2 = next(l for l in (STATE / "s5e/cand-assess-tasks.tsv").read_text().splitlines()
                  if l.startswith("aW2_s804000\t")).split("\t")
        changed = {"--eavail-ratio", "--pseudo-seeds", "--out"}
        seen = {}
        for row in rows:
            lane, name, entry, args = int(row[0]), row[1], row[2], row[3:]
            if entry == "s5e_candidate.py":
                self.assertEqual(len(args), len(w2) - 2)
                for i, (x, y) in enumerate(zip(args, w2[2:])):
                    if i == 0 or args[i - 1] not in changed:
                        self.assertEqual(x, y, (name, i))
                truth = name.split("_s")[0][len("f1_pe_"):]
                self.assertEqual(args[args.index("--eavail-ratio") + 1], f"/P/prep/bridged/{truth}.json")
                self.assertEqual(args[args.index("--out") + 1], f"/P/runs/pe/{truth}")
                a, b = map(int, args[args.index("--pseudo-seeds") + 1].split(":"))
                seen.setdefault(truth, []).extend(range(a, b + 1))
            else:
                self.assertEqual(entry, "pv-ladder/pvl_unfold.py")
                truth = name[len("f1_closure_"):]
                cfg = json.loads((ND / "pv-ladder/config.json").read_text())["rungs"]["L-5D-PV"]
                kv = dict(zip(args[::1], args[1:] + [""]))
                self.assertEqual((kv["--npz"], kv["--expect-npz-sha256"]), (cfg["npz"]["path"], cfg["npz"]["sha256"]))
                self.assertEqual((kv["--bkg"], kv["--expect-bkg-sha256"]), (cfg["bkg"]["path"], cfg["bkg"]["sha256"]))
                for k, v in (("--rung", "L-5D-PV"), ("--arm", "e"), ("--features", "all"), ("--estimator-seed", "42"),
                             ("--threads", "32"), ("--iters", "5")):
                    self.assertEqual(kv[k], v, k)
                self.assertIn("--closure", args)
                self.assertEqual(kv["--ratio"], f"/P/prep/ratios/L-5D-PV/{truth}.json")
                self.assertEqual(kv["--expect-ratio-sha256"], ("1" if truth == "genie_v3_g18" else "3") * 64)
                self.assertIn(lane, (0, 1))
                self.assertEqual(rows.index(row), [r[1] for r in rows].index(name))
        for truth, s0 in TASKS.SEEDS.items():
            self.assertEqual(sorted(seen[truth]), list(range(s0, s0 + 20)))
        for lane in (0, 1):                                              # the closure runs first in its lane
            self.assertTrue([r for r in rows if r[0] == str(lane)][0][1].startswith("f1_closure_"))

    def test_the_seeds_appear_in_no_committed_task_table(self):
        """Every --pseudo-seed(s) in a committed .tsv or .sh, against 806000-807019, except F1c's own step table at
        the bytes its run recorded (it was committed after the run, and it is where these seeds belong)."""
        hits, n, skipped = seed_hits(REPO)
        self.assertGreater(n, 100)                                      # the scan found the existing tables
        self.assertEqual(hits, [])
        self.assertEqual(skipped, [F1C_STEPS])                          # the one exclusion is live, not vacuous

    def test_the_seed_scan_still_fires_on_a_planted_table(self):
        """A planted table with an F1 seed is a hit, beside F1c's excluded table; a changed F1c table is not excluded."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / F1C_STEPS).parent.mkdir(parents=True)
            shutil.copy2(REPO / F1C_STEPS, root / F1C_STEPS)
            (root / "other").mkdir()
            (root / "other/tasks-planted.tsv").write_text("t0\ts5e_candidate.py\t--pseudo-seeds\t806005:806010\n")
            (root / "other/ok.tsv").write_text("t0\ts5e_candidate.py\t--pseudo-seeds\t805000:805019\n")
            hits, n, skipped = seed_hits(root)
            self.assertEqual(skipped, [F1C_STEPS])
            self.assertEqual(len(hits), 1)
            self.assertIn("tasks-planted.tsv", hits[0])
            with open(root / F1C_STEPS, "a") as fh:                    # an edit to F1c's table voids its exclusion
                fh.write("9\tx\ts5e_candidate.py\t--pseudo-seeds\t806000:806000\n")
            hits, n, skipped = seed_hits(root)
            self.assertEqual(skipped, [])
            self.assertTrue(any(F1C_STEPS in h for h in hits))

    def test_main_writes_both_tables_and_refuses_to_overwrite(self):
        argv = ["tables", "--sums", str(self.sums), "--prep", "/P/prep", "--runs", "/P/runs", "--table-dir", "/D/t",
                "--out-dir", str(self.tmp)]
        self.assertEqual(quiet(TASKS.main, argv), 0)
        lanes = [l.split("\t") for l in (self.tmp / "tasks-f1c.tsv").read_text().splitlines() if not l.startswith("#")]
        self.assertEqual([l[:2] for l in lanes], [[f"f1c_lane{k}", "fd_f1_lane.py"] for k in range(8)])
        self.assertTrue(all(l[2:] == ["--steps", "/D/t/f1c-steps.tsv", "--lane", str(k)] for k, l in enumerate(lanes)))
        self.assertIn(digest(self.sums), (self.tmp / "f1c-steps.tsv").read_text().splitlines()[0])
        with self.assertRaises(SystemExit):
            quiet(TASKS.main, argv)

    def products(self, root: Path):
        for rel in TASKS.expected_products():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(rel.encode())

    def test_manifest_lists_exactly_the_declared_products(self):
        runs = self.tmp / "runs"
        self.products(runs)
        out = self.tmp / "m.txt"
        self.assertEqual(quiet(TASKS.main, ["manifest", "--runs", str(runs), "--out", str(out)]), 0)
        lines = out.read_text().splitlines()
        self.assertEqual(len(lines), 2 + 2 * TASKS.N_PE)
        for line in lines:
            sha, rel = line.split("  ")
            self.assertEqual(sha, digest(runs / rel[2:]))
        with self.assertRaises(FileExistsError):
            quiet(TASKS.main, ["manifest", "--runs", str(runs), "--out", str(out)])
        for plant in ("pe/genie_v3_g18/ratio_nd_a1_s806000.npz.partial.npz", "closure/x.npz", "pe/other/a.npz"):
            with self.subTest(plant=plant):
                (runs / plant).parent.mkdir(parents=True, exist_ok=True)
                (runs / plant).write_bytes(b"x")
                with self.assertRaises(SystemExit):
                    TASKS.manifest(runs)
                (runs / plant).unlink()
        (runs / "pe/genie_v3_ar23/ratio_nd_a1_s807019.npz").unlink()
        with self.assertRaises(SystemExit):
            TASKS.manifest(runs)

    def test_the_grader_and_the_tables_name_the_same_truths_and_seeds(self):
        self.assertEqual(F.F1_TRUTHS, TASKS.SEEDS)
        self.assertEqual(F.F1_N, TASKS.N_PE)
        self.assertEqual(set(PREP.TRUTHS), set(TASKS.SEEDS))

    def test_a_missing_ratio_refuses(self):
        self.sums.write_text("1" * 64 + "  ./ratios/L-5D-PV/genie_v3_g18.json\n")
        with self.assertRaises(SystemExit):
            TASKS.steps(self.sums, "/P", "/R")


class Lane(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-lane-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.scripts = []
        for name, body in (("ok", "open(sys.argv[1], 'a').write(sys.argv[2] + '\\n')"),
                           ("bad", "sys.exit(3)")):
            p = Path(__file__).resolve().parent / f"_f1lane_{name}_{id(self)}.py"
            p.write_text(f"import sys\n{body}\n")
            self.addCleanup(p.unlink)
            self.scripts.append(f"tests/{p.name}")

    def table(self, lines):
        t = self.tmp / "steps.tsv"
        t.write_text("# header\n" + "".join("\t".join(x) + "\n" for x in lines))
        return t

    def test_runs_in_order_and_stops_at_the_first_failure(self):
        log = self.tmp / "log.txt"
        ok, bad = self.scripts
        t = self.table([["0", "a", ok, str(log), "a"], ["1", "x", ok, str(log), "x"], ["0", "b", ok, str(log), "b"],
                        ["0", "c", bad], ["0", "d", ok, str(log), "d"]])
        self.assertEqual(quiet(LANE.main, ["--steps", str(t), "--lane", "0"]), 3)
        self.assertEqual(log.read_text().split(), ["a", "b"])
        log.unlink()
        self.assertEqual(quiet(LANE.main, ["--steps", str(t), "--lane", "1"]), 0)
        self.assertEqual(log.read_text().split(), ["x"])

    def test_refusals(self):
        ok = self.scripts[0]
        for lines, lane in (([["0", "a", "../setup_salloc_env.sh"]], 0), ([["0", "a", "/bin/true.py"]], 0),
                            ([["0", "a", "tests/nonexistent.py"]], 0), ([["0", "a", ok, "x", "y"]], 1), ([["0", "a"]], 0)):
            with self.subTest(lines=lines), self.assertRaises(SystemExit):
                LANE.lane_steps(self.table(lines), lane)


class Budget(unittest.TestCase):
    def test_go_and_stop(self):
        d = BUD.decide({"G18_10a_02_11b": 30.0, "AR23_20i_00_000": 40.0}, 0.10)
        self.assertEqual(d["f1b_projected_wall_s"], 1.25 * (40.0 * 1.75 + 40.0) + BUD.FIXED_S)
        self.assertAlmostEqual(d["f1_projected_node_h"], 0.10 + d["f1b_projected_wall_s"] / 3600 + 0.75)
        self.assertEqual(d["decision"], "GO")
        lim = -(-(d["f1b_projected_wall_s"] * 1.25) // 60)
        self.assertEqual(d["f1b_time_limit"], f"{int(lim) // 60:02d}:{int(lim) % 60:02d}:00")
        self.assertAlmostEqual(d["worst_case_node_h"], 0.10 + lim / 60 + 0.9)
        self.assertEqual(d["f1c_time_limit"], "00:54:00")
        # the priced total: wall w with 0.1 + (1.25 x 2.75 w + 900)/3600 + 0.75 = 1.25 -> w = 157.1 s
        w = (1.25 - 0.85) * 3600
        w = (w - BUD.FIXED_S) / (1.25 * 2.75)
        self.assertEqual(BUD.decide({"t": w - 0.5}, 0.10)["decision"], "GO")
        self.assertEqual(BUD.decide({"t": w + 0.5}, 0.10)["decision"], "STOP")
        self.assertFalse(BUD.decide({"t": w + 0.5}, 0.10)["within_priced"])
        # the wall rule alone: 1.25 x (1.25 x 2.75 w + 900) > 2700 at w > 366.5 s
        with mock.patch.object(BUD, "PRICED_NODE_H", 99.0):
            self.assertEqual(BUD.decide({"t": 366.0}, 0.0)["decision"], "GO")
            self.assertEqual(BUD.decide({"t": 367.0}, 0.0)["decision"], "STOP")
        for bad in ({}, {"t": 0.0}, {"t": -1.0}):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                BUD.decide(bad, 0.1)

    def test_main_exit_codes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "b.json"
            self.assertEqual(quiet(BUD.main, ["--wall", "t=30", "--f1a-node-h", "0.1", "--out", str(out)]), 0)
            with self.assertRaises(FileExistsError):
                quiet(BUD.main, ["--wall", "t=30", "--f1a-node-h", "0.1", "--out", str(out)])
            out2 = Path(d) / "c.json"
            self.assertEqual(quiet(BUD.main, ["--wall", "t=900", "--f1a-node-h", "0.1", "--out", str(out2)]), 3)
            self.assertEqual(json.loads(out2.read_text())["decision"], "STOP")


SPL = """<?xml version="1.0" encoding="ISO-8859-1"?>

<!-- generated by genie::XSecSplineList::SaveSplineList() -->

<genie_xsec_spline_list version="3.00" uselog="1">

  <genie_tune name="{tune}">

{body}
  </genie_tune>
</genie_xsec_spline_list>
"""


def spline(tgt, k):
    return (f'    <spline name="genie::X/Default/nu:14;tgt:{tgt};N:2112;proc:Weak[CC],QES;{k}" nknots="2">\n'
            f'\t<knot> <E> 0.1 </E> <xsec> 1.0 </xsec> </knot>\n    </spline>\n')


class Gen5dV3(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-v3-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def files(self, tune="G18_10a_02_11b", rtune=None, drop=0, version_lines=1, extra=False, fmt="3.00"):
        ch = [spline("1000060120", i) for i in range(3)] + [spline("1000010010", i) for i in range(2)]
        other = [spline("1000080160", i) for i in range(2)]
        src = self.tmp / "src.xml"
        src.write_text(SPL.format(tune=tune, body="".join(ch[:2] + other + ch[2:])))
        red = self.tmp / "red.xml.gz"
        body = "".join(ch[drop:] + (other[:1] if extra else []))
        red.write_bytes(gzip.compress(SPL.format(tune=rtune or tune, body=body).replace('version="3.00"', f'version="{fmt}"').encode()))
        readme = self.tmp / "README"
        readme.write_text("GENIE XML Cross Section Spline files for\n" + "   version v3_02_00 qualifier X\n" * version_lines)
        return ["--tune", "G18_10a_02_11b", "--source", str(src), "--reduced", str(red), "--readme", str(readme),
                "--out", str(self.tmp / "check.json")]

    def pins(self, line="version v3_02_00 qualifier X"):
        src, readme = self.tmp / "src.xml", self.tmp / "README"
        return mock.patch.dict(V3.SPLINE_PINS, {"G18_10a_02_11b": (digest(src), digest(readme), line)})

    def check(self, *, line="version v3_02_00 qualifier X", **kw):
        argv = ["spline-check"] + self.files(**kw)
        with self.pins(line):
            return quiet(V3.main, argv)

    def test_spline_check(self):
        self.assertEqual(self.check(), 0)
        rec = json.loads((self.tmp / "check.json").read_text())
        self.assertEqual((rec["header"]["tune"], rec["header"]["format"], rec["header"]["n_splines"]),
                         ("G18_10a_02_11b", "3.00", 5))
        self.assertEqual(rec["readme_version_line"], "version v3_02_00 qualifier X")
        for kw in (dict(tune="AR23_20i_00_000"), dict(rtune="AR23_20i_00_000"), dict(drop=1), dict(version_lines=2),
                   dict(tune="AR23_20i_00_000", rtune="G18_10a_02_11b"),     # the source alone names another tune
                   dict(extra=True), dict(fmt="2.00"),                        # an extra spline; another list format
                   dict(line="version v3_04_00 qualifier X")):                # the README names another version
            with self.subTest(**kw):
                self.assertEqual(self.check(**kw), 1)
        argv = ["spline-check"] + self.files()
        with mock.patch.dict(V3.SPLINE_PINS, {"G18_10a_02_11b": ("0" * 64, digest(self.tmp / "README"),
                                                                 "version v3_02_00 qualifier X")}):
            self.assertEqual(quiet(V3.main, argv), 1)                         # the source is not the pinned file

    def test_the_committed_pins(self):
        self.assertEqual(V3.SPLINE_PINS["G18_10a_02_11b"][2], "version v3_02_00 qualifier G1810a0211b:k250:e1000")
        self.assertEqual(V3.SPLINE_PINS["AR23_20i_00_000"][2], "version v3_04_00 qualifier AR2320i00000:k250:e1000")
        decl = (STATE / "measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md").read_text()
        for t, (a, b, line) in V3.SPLINE_PINS.items():
            self.assertIn(a, decl)
            self.assertIn(b, decl)
        self.assertIn(V3.HFLUXCV_SHA256, decl)
        self.assertIn(V3.PHI_T_SHA256, decl)

    def test_phi_t_and_integral_checks(self):
        good = {"schema": "gen5d-fluxfix-phi-t/v1", "npz_sha256": V3.PHI_T_SHA256,
                "definition": "phi_t = ... FluxReweighter(minervame<p>, nu_pdg 14, nuE constraint true, 100 universes)"}
        V3.check_phi_t(V3.PHI_T_SHA256, good)
        for sha, meta in (("0" * 64, dict(good, npz_sha256="0" * 64)), (V3.PHI_T_SHA256, dict(good, schema="x")),
                          (V3.PHI_T_SHA256, dict(good, npz_sha256="1" * 64)),
                          (V3.PHI_T_SHA256, dict(good, definition="FluxReweighter(..., nuE constraint false)"))):
            with self.subTest(meta=meta), self.assertRaises(SystemExit):
                V3.check_phi_t(sha, meta)
        c = np.array([1.0, 2.0, 3.0])
        self.assertEqual(V3.check_integral(c, 6.0), 0.0)
        V3.check_integral(c, 6.0 * (1 + 5e-13))
        for h in (6.0 * (1 + 2e-12), float("nan")):
            with self.subTest(h=h), self.assertRaises(SystemExit):
                V3.check_integral(c, h)

    def test_same_spectrum(self):
        e, c = np.array([0.0, 1.0, 3.0]), np.array([2.0, 4.0])
        self.assertTrue(V3.same_spectrum(e, c, e.copy(), c.copy()))
        self.assertFalse(V3.same_spectrum(e, c, e, c * np.diff(e)))            # what gevgen samples without NOWIDTH
        self.assertFalse(V3.same_spectrum(e, c, np.array([0.0, 1.5, 3.0]), c))

    def test_flux_contents(self):
        e = np.array([0.0, 0.5, 2.0, 100.0])
        np.testing.assert_array_equal(V3.flux_contents(e, [2.0, 1.0, 0.5]), [1.0, 1.5, 49.0])
        for bad in ((np.array([0.5, 2.0, 100.0]), [1.0, 1.0]), (np.array([0.0, 2.0, 50.0]), [1.0, 1.0]),
                    (e, [1.0, 1.0])):
            with self.subTest(), self.assertRaises(SystemExit):
                V3.flux_contents(*bad)

    def test_refusal_rules(self):
        rng = {a: {"n_nonfinite": 0} for a in L.AXES5}
        good = {"reader_parity": {"n_checked": 20000, "n_mismatch": 0}}
        self.assertEqual(V3.problems(rng, good, {"pass": True}), [])
        self.assertTrue(V3.problems(dict(rng, q3={"n_nonfinite": 1}), good, {"pass": True}))
        self.assertTrue(V3.problems(rng, {"reader_parity": {"n_checked": 0, "n_mismatch": 0}}, {"pass": True}))
        self.assertTrue(V3.problems(rng, {"reader_parity": {"n_checked": 9, "n_mismatch": 1}}, {"pass": True}))
        self.assertTrue(V3.problems(rng, good, {"pass": False}))

    def test_pins(self):
        rec = json.loads((REPO / "nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json").read_text())
        self.assertIn(V3.PHI_T_SHA256, [i["sha256"] for i in rec["inputs"] if i["role"] == "phi_t"])


class Scripts(unittest.TestCase):
    def test_batch_scripts_agree_with_the_budget(self):
        a = (ND / "sbatch_fd_f1a.sh").read_text()
        b = (ND / "sbatch_fd_f1b.sh").read_text()
        sub = (ND / "submit_fd_f1.sh").read_text()
        self.assertIn("--time=00:20:00 --job-name=fd_f1a", sub)
        self.assertIn('--time="$T" --job-name=fd_f1b', sub)
        self.assertIn(f"--time={BUD.F1C_LIMIT} --job-name=fd_f1c", sub)
        self.assertIn('"$D" "$PIN" "$TABLE" "$OUT/f1c" 32 56G 0 7 none', sub)
        for x in ("--account=m3246", "--qos=regular", "--constraint=cpu", "--exclusive", "--no-requeue"):
            self.assertIn(x, sub)
        self.assertNotRegex(sub, r"(--qos[= ]|-q )\S*premium")
        self.assertNotRegex(sub, r"--(gpus|gpus-per-node|gres)[= ](?!none)|-G ")
        self.assertIn("f1b_time_limit", sub)
        self.assertIn("flux-check", a)
        self.assertIn("flux-check", b)
        self.assertIn(f"NT=64; NEV={BUD.N_TASK}", b)
        self.assertIn(f'"$F/splines" {BUD.N_PILOT} ', a)
        self.assertIn("[G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000", a)
        self.assertIn("declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)", b)
        self.assertIn('"decision": "GO"', b)
        for s in (a, b):
            self.assertNotRegex(s, r"(--qos[= ]|-q )\S*premium")
            self.assertNotRegex(s, r"--(gpus|gpus-per-node|gres)[= ](?!none)|-G ")
            self.assertIn("--no-requeue", s)

    def test_spline_filter_is_reduce_splines_verbatim(self):
        prog = lambda text: re.search(r"awk '\n(.*?)\n\s*' ", text, re.S).group(1)  # noqa: E731
        norm = lambda s: [ln.strip() for ln in s.splitlines() if ln.strip()]   # noqa: E731
        self.assertEqual(norm(prog((GENIE / "run_gevgen_v3.sh").read_text())),
                         norm(prog((GENIE / "reduce_splines.sh").read_text())))

    def test_generation_settings(self):
        s = (GENIE / "run_gevgen_v3.sh").read_text()
        for x in ("-e 0,100", "-p 14", "-t '1000060120[0.9225],1000010010[0.0775]'", '--tune "$TUNE"',
                  '-f "${FLUX},flux_numu,NOWIDTH"',
                  '--seed "$SEED"', '-r "$SEED"', "Messenger_laconic.xml"):
            self.assertIn(x, s)
        self.assertNotIn("event-generator-list", s.split("genie)")[1].split(";;")[0])


# ------------------------------------------------------------------------------------------------ the grader's F1 option


class GraderF1(T0.Base):
    """F0b's synthetic tree plus the F1 products; F0b first, then F1 against its readout."""

    def setUp(self):
        super().setUp()
        self.tr = self.tree(seed=21)
        self.Cx = T0.ExtraBlockF0b.resp(self.tr)
        self.blk = T0.ExtraBlockF0b.block(self.tr, self.Cx)
        argv, out = T0.ExtraBlockF0b.argv_to(self.tr, self.blk, "f0b")
        self.go(argv)
        self.f0b = out / "readout.json"
        self.build_f1()

    def go(self, argv):
        with self.tr.patches()[0], self.tr.patches()[1], self.tr.patches()[2], mock.patch.object(F, "F1_N", T0.SMALL):
            return quiet(F.run, F.build_args(argv), self.tr.pins)

    def build_f1(self):
        t, rng = self.tr, np.random.default_rng(4)
        self.f1root = t.root / "f1"
        self.prep = t.root / "f1-prep-SHA256SUMS"
        self.sha = {n: (hashlib.sha256(f"r{n}".encode()).hexdigest(), hashlib.sha256(f"b{n}".encode()).hexdigest())
                    for n in F.F1_TRUTHS}
        self.prep.write_text("".join(f"{r}  ./ratios/L-5D-PV/{n}.json\n{b}  ./bridged/{n}.json\n"
                                     for n, (r, b) in self.sha.items()))
        self.items = {}
        for n, s0 in F.F1_TRUTHS.items():
            Tt = t.T0 * (1 + rng.normal(0, 0.05, F.N_CELLS))
            b = rng.normal(0, 0.02, F.N_CELLS)
            pe = []
            for s in range(s0, s0 + T0.SMALL):
                m = {**T0.base_meta(), "schema": "s5n-unfold/1", "config": "deterministic", "bkg_mode": "negweight-refined",
                     "no_background": False, "truth": "ratio_nd", "amplitude": 1.0,
                     "eavail_ratio_sha256": self.sha[n][1], "pseudo_seed": s}
                pe.append([self.f1root / "pe" / n / f"ratio_nd_a1_s{s}.npz", m, Tt * (1 + rng.normal(0, 1e-3, F.N_CELLS)),
                           b + rng.normal(0, 0.004, F.N_CELLS)])
            mc = {**T0.base_meta(), "refinement": {"ran": False, "reason": "no negative weights (signal-only reference)"},
                  "schema": "pvl-unfold/1", "rung": "L-5D-PV", "arm": "e", "closure": True,
                  "features": ["pt", "pz", "eavail", "q3", "W"], "ratio_sha256": self.sha[n][0]}
            cl = [[self.f1root / "closure" / f"f1_closure_{n}.npz", mc, Tt, rng.normal(0, 0.02, F.N_CELLS)]]
            self.items[f"F1_{n}"], self.items[f"F1_closure_{n}"] = pe, cl
        self.write_f1()

    def write_f1(self):
        for items in self.items.values():
            for path, meta, Xt, r in items:
                path.parent.mkdir(parents=True, exist_ok=True)
                xs, xt = self.tr.arrays(Xt, r)
                np.savez_compressed(path, xsec_flat=xs, xtrue_flat=xt, meta=json.dumps(meta))
        self.psums = self.tr.root / "f1-products-SHA256SUMS"
        self.psums.write_text("".join(f"{digest(p)}  ./{p.relative_to(self.f1root)}\n"
                                      for items in self.items.values() for p, *_ in items))

    def f1argv(self, sub, f0b=None, prep_sha=None):
        extra = self.blk + ["--f1-prep-sums", str(self.prep), "--f1-prep-sums-sha256", prep_sha or digest(self.prep),
                            "--f1-products-sums", str(self.psums), "--f1-products-sums-sha256", digest(self.psums),
                            "--f1-root", str(self.f1root), "--f0b-readout", str(f0b or self.f0b),
                            "--f0b-readout-sha256", digest(f0b or self.f0b)]
        return T0.ExtraBlockF0b.argv_to(self.tr, extra, sub)

    def stops(self, argv, out, control):
        with self.assertRaises(SystemExit) as cm:
            self.go(argv)
        self.assertIn(f"FAIL control {control}:", str(cm.exception.code))
        self.assertFalse(any(out.iterdir()))

    def test_f1_truths_graded_by_hand_and_control_9(self):
        argv, out = self.f1argv("out_f1")
        self.assertEqual(self.go(argv), 0)
        r = json.loads((out / "readout.json").read_text())
        old = json.loads(self.f0b.read_text())
        self.assertEqual(r["schema"], "fd-f1-readout/1")
        self.assertIn(9, r["controls"]["passed"])
        self.assertTrue(r["labels"]["f1"].startswith("a bias test at two held-out GENIE v3 truths, not a coverage test"))
        self.assertEqual(r["inputs_sha256"]["f0b_readout"], digest(self.f0b))
        self.assertEqual([x for x in r["truths"] if x["row"] <= 6], old["truths"])
        ff = np.outer(self.tr.f, self.tr.f)
        C = self.tr.Ce / ff + self.tr.S.T @ self.tr.S + self.Cx / ff
        Cs = self.tr.Ce / ff + self.tr.S[1:].T @ self.tr.S[1:] + self.Cx / ff        # minus genie_mec
        got = {x["name"]: x for x in r["truths"] if x["row"] >= 7}
        self.assertEqual(sorted(got), sorted([f"F1_{n}" for n in F.F1_TRUTHS] + [f"F1_closure_{n}" for n in F.F1_TRUTHS]))
        for name, items in self.items.items():
            x = got[name]
            R = np.array([self.tr.rel(it) for it in items])
            if len(items) > 1:
                b, N = R.mean(axis=0), np.cov(R, rowvar=False, ddof=1) / len(items)
            else:
                b, N = R[0], np.zeros((F.N_CELLS, F.N_CELLS))
            self.assertEqual((x["group"], x["own_vertex"], x["grade_matrix"]), ("held-out", None, "C_total + C_resp"))
            np.testing.assert_allclose(x["bias"], b, rtol=1e-12, atol=1e-15)
            for key, M in (("grade", C), ("sensitivity", Cs)):
                chi2 = float(b @ np.linalg.solve(M + N, b))
                self.assertAlmostEqual(x[key]["chi2"], chi2, delta=1e-8 * chi2, msg=(name, key))
                np.testing.assert_allclose(x[key]["z"], b / np.sqrt(np.diag(M + N)), rtol=1e-10)
            self.assertNotIn("in_sample", x)
        self.assertIn("held-out", r["triggers"]["by_group"])
        self.assertEqual(r["triggers"]["by_group"]["held-out"]["truths"], 4)
        self.assertEqual(r["triggers"]["all_graded"], old["triggers"]["all_graded"])   # held-out is never pooled
        self.assertIn("the two F1 truths are, in their own group held-out", r["labels"]["not"])

    def test_control_9_refuses_a_readout_that_differs(self):
        bad = json.loads(self.f0b.read_text())
        bad["truths"][3]["grade"]["chi2"] += 1e-9
        p = self.tr.root / "f0b_changed.json"
        p.write_text(json.dumps(bad, indent=1) + "\n")
        argv, out = self.f1argv("out_f1x", f0b=p)
        self.stops(argv, out, 9)

    def test_control_9_compares_every_field(self):
        bad = json.loads(self.f0b.read_text())
        bad["truths"][0]["estimator"] = "something else"
        p = self.tr.root / "f0b_label.json"
        p.write_text(json.dumps(bad, indent=1) + "\n")
        argv, out = self.f1argv("out_f1y", f0b=p)
        self.stops(argv, out, 9)

    def test_f1_input_refusals(self):
        argv, out = self.f1argv("a", prep_sha="0" * 64)
        self.stops(argv, out, 1)
        stray = self.f1root / "pe" / "genie_v3_g18" / "ratio_nd_a1_s806099.npz"
        shutil.copy(self.items["F1_genie_v3_g18"][0][0], stray)
        argv, out = self.f1argv("b")
        self.stops(argv, out, 1)
        stray.unlink()
        for name, key, val, control in (("F1_genie_v3_ar23", "eavail_ratio_sha256", "f" * 64, 2),
                                        ("F1_closure_genie_v3_g18", "ratio_sha256", "f" * 64, 2),
                                        ("F1_genie_v3_g18", "amplitude", 0.5, 2)):
            with self.subTest(name=name, key=key):
                keep = self.items[name][0][1][key]
                self.items[name][0][1][key] = val
                self.write_f1()
                argv, out = self.f1argv(f"c_{name}_{key}")
                self.stops(argv, out, control)
                self.items[name][0][1][key] = keep
                self.write_f1()

    def test_options_go_together(self):
        argv, _ = self.f1argv("d")
        i = argv.index("--f1-root")
        for drop in (argv[:i] + argv[i + 2:], [x for x in argv if x not in self.blk]):
            with self.subTest(), self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                F.build_args(drop)


if __name__ == "__main__":
    unittest.main()
