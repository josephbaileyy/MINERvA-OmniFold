"""The stage 1 tables generator under A2.1's S2 and the director's ruling (A) of 2026-11-04: the "nature" bulk's graded
set is the declared set exactly, per truth; every generated step passes fd_1b_mc's real parser with the rule, the CV
tdw and (for the bulk) the gate pair it needs; and the bulk is written only on binding 3's committed pins file."""
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fd_1b_mc as mc  # noqa: E402
import s1_assemble as sa  # noqa: E402

GEN_PATH = (Path(__file__).resolve().parents[2] / "docs/orchestration/state/measurement-paper/5d-community-20261024"
            / "fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py")
_spec = importlib.util.spec_from_file_location("make_stage1_tables", GEN_PATH)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)
CLIP_SEED = str(mc.TOY_SEEDS["g18"][0])


class _Parsed(Exception):
    pass


def parsed(step_argv: list[str]):
    """The namespace fd_1b_mc's own parser makes of a generated step (the subcommand's function is stopped there)."""
    got = []

    def grab(a):
        got.append(a)
        raise _Parsed
    with mock.patch.object(mc, "run_unfold", grab), mock.patch.object(mc, "receipt", grab):
        try:
            mc.main(step_argv[1:])
        except _Parsed:
            pass
    assert len(got) == 1, step_argv[:8]
    return got[0]


def steps(path: Path) -> list[list[str]]:
    return [ln.split("\t")[2:] for ln in path.read_text().splitlines() if not ln.startswith("#")]


def declared(truth: str) -> set:
    """The declaration's graded set at one truth, from its own constants (not the generator's)."""
    out = {(truth, "central", "T"), (truth, "seed", "T")}
    out |= {(truth, "block", f"{b}_{i}") for b in sa.EXPECT for i in range(sa.EXPECT[b])}
    out |= {(truth, "stat", str(b)) for b in mc.STAT_REPLICAS} | {(truth, "toy", str(s)) for s in mc.TOY_SEEDS[truth]}
    return out


class Plan(unittest.TestCase):
    def test_the_graded_bulk_is_the_declared_set(self):
        for plugin, n, truths in ((False, 1054, ("g18", "ar23")), (True, 1581, ("g18", "ar23", "plugin"))):
            pilot, pilot_b, bulk = gen.plan(mc, sa, plugin, CLIP_SEED)
            self.assertEqual(len(bulk), len(set(bulk)))
            self.assertEqual(len(bulk), n)
            for t in truths:
                self.assertEqual({x for x in bulk if x[0] == t}, declared(t), (plugin, t))
                self.assertEqual(len(declared(t)), 527)
            self.assertEqual({x[0] for x in bulk}, set(truths))
            self.assertFalse({x for x in bulk if x[1] in ("clipmean", "control", "capture")})
            rerun = {x for x in pilot + pilot_b if x[1] in mc.BULK_ROLES}
            self.assertEqual(len(rerun), 5, rerun)                    # ruling (A): re-run under 'nature'
            self.assertLessEqual(rerun, set(bulk))

    def test_before_s1_0_there_is_no_bulk(self):
        _, pilot_b, bulk = gen.plan(mc, sa, False, None)
        self.assertEqual((pilot_b, bulk), ([], []))


class Tables(unittest.TestCase):
    """main() on a scratch checkout: a git repository holding only the pins file at GATE_PIN's path (mc.GATE_PIN is
    redirected there; the modules are the ones already imported)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd1b-tables-"))
        self.co = self.tmp / "co"
        self.rel = mc.GATE_PIN.relative_to(mc._ND.parent)
        self.pin = self.co / self.rel
        self.pin.parent.mkdir(parents=True)
        self.git("init", "-q")
        self.gate = self.tmp / "gate.json"
        self.gate.write_text('{"schema": "fd-1b-c2-gate/1"}\n')
        self.sha = hashlib.sha256(self.gate.read_bytes()).hexdigest()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.co), "-c", "user.name=t", "-c", "user.email=t@t.invalid", *args],
                       check=True, capture_output=True)

    def commit_pin(self, text: str):
        self.pin.write_text(text)
        self.git("add", str(self.rel))
        self.git("commit", "-q", "-m", "pin")

    def run_gen(self, plugin="no", gate=True, sha=None, out="out"):
        o = self.tmp / out
        o.mkdir()
        argv = [str(self.co), str(o), "--plugin", plugin, "--flux-table-sha256", "f" * 64, "--estimator", "R",
                "--clip-seed", CLIP_SEED] + (["--push-sha256", "e" * 64] if plugin == "yes" else [])
        if gate:
            argv += ["--clip-gate", str(self.gate), "--expect-clip-gate-sha256", sha or self.sha]
        with mock.patch.object(mc, "GATE_PIN", self.pin):
            gen.main(argv)
        return o

    def test_every_step_passes_the_real_parser_with_its_rule(self):
        self.commit_pin(self.sha + "\n")
        for plugin, n, nodes in (("no", 1054, 6), ("yes", 1581, 9)):
            o = self.run_gen(plugin, out=f"out-{plugin}")
            bulk = steps(o / "s1-bulk-steps.tsv")
            self.assertEqual(len(bulk), n)
            self.assertEqual(len((o / "tasks-s1-bulk.tsv").read_text().splitlines()) - 1, 8 * nodes)
            lanes = [ln.split("\t")[0] for ln in (o / "s1-bulk-steps.tsv").read_text().splitlines()[1:]]
            self.assertLessEqual(max(lanes.count(x) for x in set(lanes)), 22)
            got = set()
            for s in bulk:
                a = parsed(s)
                self.assertEqual((a.clip_rule, str(a.clip_gate), a.expect_clip_gate_sha256), ("nature", str(self.gate), self.sha))
                self.assertEqual((str(a.cv_tdw), a.expect_cv_tdw_sha256), (gen.CV_TDW, gen.CV_TDW_SHA256))
                self.assertIn(a.role, mc.BULK_ROLES)
                got.add((a.truth, a.role, a.items))
            truths = ("g18", "ar23") + (("plugin",) if plugin == "yes" else ())
            self.assertEqual(got, set().union(*(declared(t) for t in truths)))
            for job in ("s1-0", "s1-0b"):
                for s in steps(o / f"{job}-steps.tsv"):
                    a = parsed(s)
                    self.assertEqual((a.clip_rule, a.clip_gate, a.expect_clip_gate_sha256), ("data", None, None))
                    self.assertEqual((str(a.cv_tdw), a.expect_cv_tdw_sha256), (gen.CV_TDW, gen.CV_TDW_SHA256))
            (r,) = steps(o / "receipt-steps.tsv")
            a = parsed(r)
            self.assertEqual((a.cmd, str(a.cv_tdw), a.expect_cv_tdw_sha256), ("receipt", gen.CV_TDW, gen.CV_TDW_SHA256))

    def test_no_product_path_is_shared_between_rules(self):
        """The audit's finding on ruling (A): over every generated table (s1-0, s1-0b, the bulk; with and without the
        plug-in), each step's product paths, as fd_1b_mc's own parser and product_name make them, are grouped by rule;
        no path appears under two rules, and each rule writes only to its own unfolds directory."""
        self.commit_pin(self.sha + "\n")
        for plugin in ("no", "yes"):
            o = self.run_gen(plugin, out=f"paths-{plugin}")
            by_rule = {"data": set(), "nature": set()}
            for job in ("s1-0", "s1-0b", "s1-bulk"):
                for st in steps(o / f"{job}-steps.tsv"):
                    a = parsed(st)
                    self.assertEqual((a.out.name, str(a.out.parent)),               # the ruled form, not the generator's
                                     (f"{a.clip_rule}-{a.estimator}", f"{gen.W}/stage1/unf"))
                    for it in a.items.split(","):
                        p = a.out / mc.product_name(a.tag, a.truth, a.role, it)
                        self.assertNotIn(p, by_rule[a.clip_rule], (job, p.name))   # one step per product
                        by_rule[a.clip_rule].add(p)
            self.assertFalse(by_rule["data"] & by_rule["nature"], plugin)
            self.assertEqual({p.parent for p in by_rule["data"]} & {p.parent for p in by_rule["nature"]}, set())
            names = {r: {p.name for p in ps} for r, ps in by_rule.items()}
            self.assertEqual(len(names["data"] & names["nature"]), 5, plugin)     # ruling (A)'s five re-runs

    def test_the_bulk_needs_binding_3s_committed_pins_file(self):
        with self.assertRaises(mc.Refusal):                                       # no pins file
            self.run_gen(out="o1")
        self.pin.write_text(self.sha + "\n")                                      # on disk, not committed
        with self.assertRaisesRegex(SystemExit, "not committed"):
            self.run_gen(out="o2")
        self.commit_pin(self.sha + "\n")
        self.pin.write_text("0" * 64 + "\n")                                      # committed, then changed on disk
        with self.assertRaisesRegex(SystemExit, "not committed"):
            self.run_gen(out="o3")
        self.pin.write_text(self.sha + "\n")
        with self.assertRaisesRegex(SystemExit, "not the record binding 3 commits"):
            self.run_gen(sha="1" * 64, out="o4")                                  # another record's digest
        o = self.run_gen(gate=False, out="o5")                                    # no gate given: no bulk table
        self.assertFalse((o / "s1-bulk-steps.tsv").exists())
        self.assertTrue((o / "s1-0b-steps.tsv").exists())
        o = self.run_gen(out="o6")                                                # the committed record
        self.assertTrue((o / "s1-bulk-steps.tsv").exists())


if __name__ == "__main__":
    unittest.main()
