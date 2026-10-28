"""Controls for F1's amendment 2 (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-2.md
section 5): the single-wave gate fd_f1_budget3.py, on synthetic records and on the committed re-pilot records; the
submission helper's f1b3 stage run with stub sbatch and sacct; and sbatch_fd_f1b3.sh's refusals, run against a
throwaway git deploy. No job runs and no cluster path is read.

* the seed rule: the first seven of F1b's declared ranges, in order, in the gate and the script alike; disjoint from
  the re-pilot's and the pseudo-experiments'.
* the single-wave plan: 14 tasks at concurrency 14, one wave, 1,120,000 events per tune as F1b declared.
* decide: GO with every number recomputed; a STOP from each rule with every other rule holding; the memory boundary
  counting the short runs; the timeout as 3 x the projected task.
* the committed records: they re-verify against the pinned sums, a planted change refuses, and their verdict.
* spent: the ledger's F1 rows.
* submit_fd_f1.sh f1b3 and sbatch_fd_f1b3.sh: refusal on a missing, non-GO or malformed gate file, on a re-pilot not
  in its gate's STOP state or over the memory rule, and on an existing output; F1b' never touches f1b/ or f1b2/."""
import contextlib
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_f1_budget2 as B2  # noqa: E402
import fd_f1_budget3 as B3  # noqa: E402
import fd_f1_tasks as TASKS  # noqa: E402

FD = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024"
GIB = 1024 * 1024
ARGS = dict(priced_node_h=2.0, ceiling_node_h=2.5)


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def runs(long_w=220.0, short_w=170.0, long_m=21 * GIB, short_m=22 * GIB, scale=None):
    """Synthetic re-pilot records in fd_f1_budget2.load_runs's form."""
    out = {}
    for tune in B2.TUNES:
        k = (scale or {}).get(tune, 1.0)
        out[tune] = {"long": [{"elapsed_s": long_w * k - i, "maxrss_kib": long_m - i, "exit": 0} for i in range(4)],
                     "short": [{"elapsed_s": short_w * k - i, "maxrss_kib": short_m - i, "exit": 0} for i in range(6)]}
    return out


class SeedsAndPlan(unittest.TestCase):
    def test_the_seed_rule(self):
        bound = (ND / "sbatch_fd_f1b.sh").read_text()        # F1b's declared ranges, as bound
        base = dict(re.findall(r"\[(\w+)\]=(\d+)", re.search(r"BASE=\((.*?)\)", bound).group(1)))
        nt = int(re.search(r"NT=(\d+)", bound).group(1))
        pe = {s0 + i for s0 in TASKS.SEEDS.values() for i in range(TASKS.N_PE)}
        repilot = {s for t in B2.TUNES for v in B2.seeds(t).values() for s in v}
        for tune in B3.TUNES:
            declared = list(range(int(base[tune]) + 1, int(base[tune]) + 1 + nt))
            self.assertEqual(B3.seeds(tune), declared[:7])
            self.assertFalse(set(B3.seeds(tune)) & (pe | repilot))
        s = (ND / "sbatch_fd_f1b3.sh").read_text()
        self.assertEqual(dict(re.findall(r"\[(\w+)\]=(\d+)", re.search(r"BASE=\((.*?)\)", s).group(1))),
                         {t: str(b) for t, b in B3.SEED_BASE.items()})
        self.assertIn('for k in $(seq 1 $NT); do echo "$T $(( ${BASE[$T]} + k ))"', s)

    def test_the_single_wave_plan(self):
        self.assertEqual((B3.P, B3.N_TASKS_PER_TUNE, B3.N_EVENTS, B3.WAVES), (14, 7, 160_000, 1))
        self.assertEqual(B3.P, len(B3.TUNES) * B3.N_TASKS_PER_TUNE)
        self.assertEqual(B3.N_TASKS_PER_TUNE * B3.N_EVENTS, 64 * 17_500)       # F1b's events per tune
        s = (ND / "sbatch_fd_f1b3.sh").read_text()
        self.assertIn(f"NT={B3.N_TASKS_PER_TUNE}; NEV={B3.N_EVENTS}", s)
        self.assertIn('[ "$P" = 14 ]', s)
        self.assertIn('xargs -P "$P"', s)
        self.assertIn("|| exit 255' < \"$F/queue.txt\"", s)


class Decide(unittest.TestCase):
    def test_go_with_every_number_recomputed(self):
        d = B3.decide(runs(scale={"AR23_20i_00_000": 1.05}), **ARGS)
        t = max((220.0 * k - 170.0 * k) / 16_500 for k in (1.0, 1.05))
        load = max(170.0 * k - 1_000 * (220.0 * k - 170.0 * k) / 16_500 for k in (1.0, 1.05))
        task = load + 160_000 * t
        wall = task + 900
        self.assertAlmostEqual(d["per_event_s_used"], t)
        self.assertAlmostEqual(d["load_s_used"], load)
        self.assertAlmostEqual(d["f1b3_projected_task_wall_s"], task)
        self.assertAlmostEqual(d["f1b3_projected_wall_s"], wall)
        self.assertEqual(d["f1b3_projected_mem_kib"], 14 * 22 * GIB)
        lim = math.ceil(wall * 1.25 / 60)
        self.assertEqual(d["f1b3_time_limit"], f"{lim // 60:02d}:{lim % 60:02d}:00")
        self.assertAlmostEqual(d["f1_projected_node_h"], 0.408333 + wall / 3600 + 0.75)
        self.assertAlmostEqual(d["worst_case_node_h"], 0.408333 + lim / 60 + 0.9)
        self.assertEqual(d["f1b3_task_timeout_s"], math.ceil(3.0 * task))
        self.assertEqual((d["concurrency"], d["waves"], d["decision"]), (14, 1, "GO"))

    def test_each_rule_stops_with_the_others_holding(self):
        rules = ("mem_ok", "f1b3_fits_its_limit", "within_priced", "within_ceiling")
        cases = {
            "mem_ok": (runs(short_m=26 * GIB), ARGS),
            "f1b3_fits_its_limit": (runs(long_w=350.0), dict(priced_node_h=9.0, ceiling_node_h=9.0)),
            "within_priced": (runs(), dict(ARGS, priced_node_h=1.5)),
            "within_ceiling": (runs(), dict(ARGS, ceiling_node_h=1.8)),
        }
        for rule, (r, kw) in cases.items():
            with self.subTest(rule):
                d = B3.decide(r, **kw)
                self.assertFalse(d[rule])
                self.assertTrue(all(d[o] for o in rules if o != rule), {o: d[o] for o in rules})
                self.assertEqual(d["decision"], "STOP")

    def test_memory_boundary_counts_the_short_runs_too(self):
        cap = int(0.75 * B3.NODE_MEM_KIB / 14)
        self.assertTrue(B3.decide(runs(long_m=cap, short_m=cap), **ARGS)["mem_ok"])
        self.assertFalse(B3.decide(runs(long_m=cap + 1, short_m=cap), **ARGS)["mem_ok"])
        self.assertFalse(B3.decide(runs(long_m=cap, short_m=cap + 1), **ARGS)["mem_ok"])

    def test_the_fit_uses_the_largest_per_event_time_and_load_across_tunes(self):
        # G18 has the larger per-event time and AR23 the larger load: the task takes both
        r = runs()
        for x in r["G18_10a_02_11b"]["long"]:
            x["elapsed_s"] += 100.0
        for x in r["AR23_20i_00_000"]["short"]:
            x["elapsed_s"] += 30.0
        s = B2.summary(r)
        d = B3.decide(r, **ARGS)
        self.assertEqual(d["per_event_s_used"], s["G18_10a_02_11b"]["per_event_s_descriptive"])
        self.assertEqual(d["load_s_used"], s["AR23_20i_00_000"]["load_s_descriptive"])
        own = max(v["load_s_descriptive"] + 160_000 * v["per_event_s_descriptive"] for v in s.values())
        self.assertGreater(d["f1b3_projected_task_wall_s"], own)

    def test_a_non_positive_fit_refuses(self):
        with self.assertRaises(SystemExit):
            B3.decide(runs(long_w=160.0, short_w=170.0), **ARGS)


class CommittedRecords(unittest.TestCase):
    def test_they_reverify_and_give_the_declared_verdict(self):
        d = B3.decide(B3.verify_records(B3.RECORDS), **ARGS)
        self.assertEqual(d["decision"], "GO")
        self.assertEqual(d["f1b3_projected_mem_kib"], 14 * 22_015_472)
        self.assertAlmostEqual(d["per_event_s_used"], 0.00958969696969697, places=15)    # G18, seed 60103 included
        self.assertAlmostEqual(d["load_s_used"], 170.36636363636364, places=9)          # AR23
        self.assertEqual(d["f1b3_time_limit"], "00:55:00")
        self.assertEqual(d["f1b3_task_timeout_s"], 5115)

    def test_a_planted_change_refuses(self):
        tmp = Path(tempfile.mkdtemp(prefix="f1-b3-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        root = tmp / "f1a2"
        shutil.copytree(B3.RECORDS, root)
        quiet(B3.verify_records, root)
        rec = sorted((root / "runs").glob("*/long_*.time"))[0]
        good = rec.read_bytes()
        for plant in ("record", "extra", "missing", "sums"):
            with self.subTest(plant):
                if plant == "record":
                    rec.write_bytes(good.replace(b"Exit status: 0", b"Exit status: 0 "))
                elif plant == "extra":
                    (rec.parent / "long_s99999.time").write_bytes(good)
                elif plant == "missing":
                    rec.unlink()
                else:
                    (root / "f1a2-SHA256SUMS").write_bytes((B3.RECORDS / "f1a2-SHA256SUMS").read_bytes() + b"\n")
                with self.assertRaises(SystemExit):
                    B3.verify_records(root)
                rec.write_bytes(good)
                (rec.parent / "long_s99999.time").unlink(missing_ok=True)
                shutil.copy(B3.RECORDS / "f1a2-SHA256SUMS", root / "f1a2-SHA256SUMS")

    def test_main_writes_once_and_exits_3_on_stop(self):
        tmp = Path(tempfile.mkdtemp(prefix="f1-b3m-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        argv = ["--priced-node-h", "2.0", "--ceiling-node-h", "2.5", "--out", str(tmp / "b.json")]
        self.assertEqual(quiet(B3.main, argv), 0)
        self.assertEqual(json.loads((tmp / "b.json").read_text())["decision"], "GO")
        with self.assertRaises(FileExistsError):
            quiet(B3.main, argv)
        self.assertEqual(quiet(B3.main, ["--priced-node-h", "1.0", "--ceiling-node-h", "2.5", "--out",
                                         str(tmp / "c.json")]), 3)

    def test_spent_is_the_ledgers_f1_rows(self):
        # F1's charged jobs before F1b': F1a, F1b and the re-pilot (later F1 rows are F1b' and after)
        rows = [l.split("\t") for l in (FD / "fd/LEDGER.tsv").read_text().splitlines()[1:]]
        jobs = {"60415571": "F1 S4.2", "60417614": "F1 S4.3", B3.REPILOT_JOB_ID: "F1 S4.5"}
        charged = [r for r in rows if r[6] in jobs]
        self.assertEqual(sorted(r[0][:7] for r in charged), sorted(jobs.values()))
        self.assertAlmostEqual(sum(float(r[7]) for r in charged), B3.SPENT_NODE_H, places=6)
        self.assertLessEqual(B3.SPENT_NODE_H + B3.F1B_MAX_S / 3600 + B3.F1C_LIMIT_H, 2.5)   # Joseph's ceiling


class SubmitF1b3(unittest.TestCase):
    """submit_fd_f1.sh f1b3 with stub sbatch and sacct, the deploy being this checkout."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-sub3-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.bin / "sbatch").write_text('#!/bin/bash\necho "SBATCH $*" > "$STUB_LOG"\necho "Submitted batch job 1"\n')
        (self.bin / "sacct").write_text('#!/bin/bash\ncase "$*" in *State*) echo "$STUB_STATE" ;; *) echo "$STUB_MAXRSS" ;; esac\n')
        for f in ("sbatch", "sacct"):
            (self.bin / f).chmod(0o755)

    def submit(self, priced="2.0", ceiling="2.5", state="FAILED|3:0", maxrss="287876772K", pre=None):
        out = self.tmp / "OUT"
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir()
        if pre:
            (out / pre).mkdir()
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", STUB_LOG=str(self.tmp / "sbatch.log"),
                   STUB_STATE=state, STUB_MAXRSS=maxrss, F1_PY=sys.executable)
        (self.tmp / "sbatch.log").unlink(missing_ok=True)
        p = subprocess.run(["bash", str(ND / "submit_fd_f1.sh"), "f1b3", str(ND.parent), "PIN", str(out), priced, ceiling],
                           env=env, capture_output=True, text=True)
        return p, out

    def test_go_submits_with_the_gates_limit(self):
        p, out = self.submit()
        self.assertEqual(p.returncode, 0, p.stderr)
        line = (self.tmp / "sbatch.log").read_text()
        for x in ("--qos=regular", "--constraint=cpu", "--exclusive", "--no-requeue", "--time=00:55:00",
                  "--job-name=fd_f1b3", "sbatch_fd_f1b3.sh"):
            self.assertIn(x, line)
        self.assertEqual(json.loads((out / "gate3/budget3.json").read_text())["decision"], "GO")

    def test_refusals(self):
        limit_k = 487802 * 1024 * 3 // 4
        for kw in (dict(priced="1.0"), dict(ceiling="2.0"), dict(state="COMPLETED|0:0"), dict(state="FAILED|1:0"),
                   dict(state="RUNNING|0:0"), dict(maxrss=f"{limit_k + 1}K"), dict(maxrss="400G"), dict(maxrss=""),
                   dict(pre="gate3"), dict(pre="f1b3")):
            with self.subTest(**kw):
                p, _ = self.submit(**kw)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((self.tmp / "sbatch.log").exists())
        self.assertEqual(self.submit(maxrss=f"{limit_k}K")[0].returncode, 0)


class LauncherRefusals(unittest.TestCase):
    """sbatch_fd_f1b3.sh run against a throwaway git deploy: every guard before generation refuses with exit 2."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-l3-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.d = self.tmp / "deploy"
        self.d.mkdir()
        g = ["git", "-C", str(self.d), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.hooksPath=/dev/null"]
        subprocess.run(["git", "init", "-q", str(self.d)], check=True)
        (self.d / "x").write_text("x\n")
        subprocess.run(g + ["add", "x"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)
        self.pin = subprocess.run(["git", "-C", str(self.d), "rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
        self.out = self.tmp / "OUT"
        (self.out / "gate3").mkdir(parents=True)
        (self.out / "f1a").mkdir()
        (self.out / "f1a2").mkdir()
        # a valid one-line checksum file, so the products check passes on GNU and BSD sha256sum alike and each
        # refusal below is the guard it names
        (self.out / "f1a/p.txt").write_text("p\n")
        h = hashlib.sha256(b"p\n").hexdigest()
        (self.out / "f1a2/reused.sha256").write_text(f"{h}  ./p.txt\n")

    def launch(self, budget=None, pin=None):
        if budget is not None:
            (self.out / "gate3/budget3.json").write_text(json.dumps(budget, indent=1))
        return subprocess.run(["bash", str(ND / "sbatch_fd_f1b3.sh"), str(self.d), pin or self.pin, str(self.out)],
                              capture_output=True, text=True)

    def test_refusals(self):
        good = {"decision": "GO", "concurrency": 14, "f1b3_task_timeout_s": 5115}
        cases = {"wrong pin": (good, "0" * 40, "deploy HEAD="), "missing gate file": (None, None, "is not GO"),
                 "STOP": (dict(good, decision="STOP"), None, "is not GO"),
                 "concurrency 16": (dict(good, concurrency=16), None, "concurrency 16 is not the declared 14"),
                 "no timeout": ({k: v for k, v in good.items() if k != "f1b3_task_timeout_s"}, None,
                                "no per-task timeout"),
                 "zero timeout": (dict(good, f1b3_task_timeout_s=0), None, "no per-task timeout")}
        for name, (budget, pin, why) in cases.items():
            with self.subTest(name):
                (self.out / "gate3/budget3.json").unlink(missing_ok=True)
                p = self.launch(budget, pin)
                self.assertEqual(p.returncode, 2, p.stderr)
                self.assertIn(why, p.stderr)
                self.assertFalse((self.out / "f1b3").exists())
        reused = (self.out / "f1a2/reused.sha256").read_text()
        (self.out / "f1a2/reused.sha256").write_text("0" * 64 + "  ./p.txt\n")
        p = self.launch(good)
        self.assertEqual(p.returncode, 2)
        self.assertIn("F1a's products changed", p.stderr)
        (self.out / "f1a2/reused.sha256").write_text(reused)
        (self.out / "f1b3").mkdir()
        p = self.launch(good)
        self.assertEqual(p.returncode, 2)
        self.assertIn("exists", p.stderr)

    def test_never_touches_f1b_or_f1b2_and_times_every_task(self):
        s = (ND / "sbatch_fd_f1b3.sh").read_text()
        self.assertNotRegex(s, r"\$OUT/f1b(?!3)")
        self.assertIn('F="$OUT/f1b3"', s)
        self.assertIn('task_s$1.time" timeout "$TO"', s)
        self.assertIn('"f1b3_task_timeout_s"', s)
        self.assertIn('B3="$OUT/gate3/budget3.json"', s)
        self.assertIn('sha256sum -c "$A2/reused.sha256"', s)
        self.assertIn('> "$F/f1b3-SHA256SUMS"\nneed $? "the sums file"', s)


if __name__ == "__main__":
    unittest.main()
