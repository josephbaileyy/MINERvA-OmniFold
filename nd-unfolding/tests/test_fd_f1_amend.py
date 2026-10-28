"""Controls for F1's amendment 1 (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md
section 5): the re-pilot gate fd_f1_budget2.py on synthetic /usr/bin/time -v records, the submission helper run with
stub sbatch and sacct, and the new scripts against the gate's constants. No real product is read.

* parse_time_v reads GNU time -v's wall, maximum RSS and exit status, and refuses an incomplete record.
* the seeds: 12 per tune, distinct, disjoint from F1a's, F1b''s (60001-60064, 61001-61064) and the pseudo-experiments'
  (fd_f1_tasks.SEEDS), and the batch script's arithmetic.
* decide: GO with every number recomputed, and a STOP from each rule with every other rule holding.
* load_runs refuses a missing, an undeclared and a failed run.
* submit_fd_f1.sh f1b2 refuses a STOP budget, a budget without the re-pilot's job, and a re-pilot whose sacct batch
  MaxRSS exceeds 75 % of the node, and submits with the gate's time limit otherwise.
* the scripts: the re-pilot is the gate's design, F1b' never touches F1b's directory, xargs stops on a failure, the
  reused F1a products are exactly the five declared files, and every submission line is regular QOS with no GPU."""
import contextlib
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
import fd_f1_tasks as TASKS  # noqa: E402

FD = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024"
SUMS = FD / "fd/receipts-f1/amendment-1/f1a-SHA256SUMS"
GIB = 1024 * 1024


def time_v(elapsed: str, rss: int, exit_status: int = 0) -> str:
    return (f'\tCommand being timed: "bash run_gevgen_v3.sh genie"\n\tUser time (seconds): 1.0\n'
            f"\tElapsed (wall clock) time (h:mm:ss or m:ss): {elapsed}\n\tMaximum resident set size (kbytes): {rss}\n"
            f"\tExit status: {exit_status}\n")


def mmss(s: float) -> str:
    return f"{int(s // 60)}:{s % 60:05.2f}"


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def runs(long_w=120.0, short_w=60.0, long_m=20 * GIB, short_m=19 * GIB, scale=None):
    out = {}
    for tune in B2.TUNES:
        k = (scale or {}).get(tune, 1.0)
        out[tune] = {"long": [{"elapsed_s": long_w * k - i, "maxrss_kib": long_m - i, "exit": 0} for i in range(4)],
                     "short": [{"elapsed_s": short_w * k - i, "maxrss_kib": short_m - i, "exit": 0} for i in range(8)]}
    return out


class TimeRecords(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(B2.parse_time_v(time_v("1:02:03.5", 3_800_000)),
                         {"elapsed_s": 3723.5, "maxrss_kib": 3_800_000, "exit": 0})
        self.assertEqual(B2.parse_time_v(time_v("2:05.25", 10))["elapsed_s"], 125.25)
        for bad in ("", time_v("1:00", 5).replace("Exit status: 0", ""), time_v("1:00", 5).replace("Maximum", "Max")):
            with self.subTest(), self.assertRaises(ValueError):
                B2.parse_time_v(bad)
        with self.assertRaises(ValueError):
            B2.wall_seconds("12")


class Seeds(unittest.TestCase):
    def test_declared_seeds(self):
        f1b = {60000 + k for k in range(1, 65)} | {61000 + k for k in range(1, 65)}
        pe = {s0 + i for s0 in TASKS.SEEDS.values() for i in range(TASKS.N_PE)}
        seen = set()
        for tune in B2.TUNES:
            s = B2.seeds(tune)
            self.assertEqual((len(s["long"]), len(s["short"])), (B2.N_LONG, 2 * B2.N_SHORT))
            both = set(s["long"]) | set(s["short"])
            self.assertEqual(len(both), 12)
            self.assertFalse(both & f1b or both & pe or both & seen or both & {60000, 61000})
            seen |= both
        text = (ND / "sbatch_fd_f1a2.sh").read_text()
        base = dict(re.findall(r"\[(\w+)\]=(\d+)", re.search(r"BASE2=\((.*?)\)", text).group(1)))
        for tune in B2.TUNES:
            b = int(base[tune])
            self.assertEqual(B2.seeds(tune)["long"], list(range(b + 1, b + 5)))
            self.assertEqual(B2.seeds(tune)["short"], list(range(b + 5, b + 13)))


class Decide(unittest.TestCase):
    ARGS = dict(spent_node_h=0.3075, pilot_node_h=0.08, priced_node_h=2.5, ceiling_node_h=2.5)

    def test_go_with_every_number_recomputed(self):
        d = B2.decide(runs(scale={"AR23_20i_00_000": 1.1}), **self.ARGS)
        wall = 8 * 120.0 * 1.1 + 900
        self.assertAlmostEqual(d["f1b2_projected_wall_s"], wall)
        self.assertEqual(d["f1b2_projected_mem_kib"], 16 * 20 * GIB)
        lim = math.ceil(wall * 1.25 / 60)
        self.assertEqual(d["f1b2_time_limit"], f"{lim // 60:02d}:{lim % 60:02d}:00")
        self.assertAlmostEqual(d["worst_case_node_h"], 0.3075 + 0.08 + lim / 60 + 0.9)
        self.assertAlmostEqual(d["f1_projected_node_h"], 0.3075 + 0.08 + wall / 3600 + 0.75)
        t = (120.0 * 1.1 - 60.0 * 1.1) / (17500 - 1000)
        self.assertAlmostEqual(d["runs"]["AR23_20i_00_000"]["per_event_s_descriptive"], t)
        self.assertEqual((d["concurrency"], d["waves"], d["decision"]), (16, 8, "GO"))

    def test_each_rule_stops_with_the_others_holding(self):
        cases = {
            "mem_ok": (runs(long_m=24 * GIB), self.ARGS),
            "f1b2_fits_its_limit": (runs(long_w=260.0), dict(self.ARGS, priced_node_h=9.0, ceiling_node_h=9.0)),
            "within_priced": (runs(), dict(self.ARGS, priced_node_h=1.2)),
            "within_ceiling": (runs(), dict(self.ARGS, ceiling_node_h=1.5)),
        }
        rules = ("mem_ok", "f1b2_fits_its_limit", "within_priced", "within_ceiling")
        for rule, (r, kw) in cases.items():
            with self.subTest(rule):
                d = B2.decide(r, **kw)
                self.assertFalse(d[rule])
                self.assertTrue(all(d[o] for o in rules if o != rule), {o: d[o] for o in rules})
                self.assertEqual(d["decision"], "STOP")

    def test_memory_boundary_counts_the_short_runs_too(self):
        cap = int(0.75 * B2.NODE_MEM_KIB / 16)
        self.assertTrue(B2.decide(runs(long_m=cap, short_m=cap), **self.ARGS)["mem_ok"])
        self.assertFalse(B2.decide(runs(long_m=cap + 1, short_m=cap), **self.ARGS)["mem_ok"])
        self.assertFalse(B2.decide(runs(long_m=cap, short_m=cap + 1), **self.ARGS)["mem_ok"])   # the start-up peak


class LoadRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-b2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for tune in B2.TUNES:
            (self.tmp / tune).mkdir()
            for role, ss in B2.seeds(tune).items():
                for s in ss:
                    (self.tmp / tune / f"{role}_s{s}.time").write_text(time_v(mmss(120 if role == "long" else 60), 20 * GIB))

    def test_reads_every_declared_run_and_main_decides(self):
        r = B2.load_runs(self.tmp)
        self.assertEqual({t: (len(v["long"]), len(v["short"])) for t, v in r.items()}, {t: (4, 8) for t in B2.TUNES})
        out = self.tmp / "b.json"
        argv = ["--runs", str(self.tmp), "--spent-node-h", "0.3075", "--repilot-node-h", "0.08", "--priced-node-h",
                "2.5", "--ceiling-node-h", "2.5", "--job-id", "123", "--out", str(out)]
        self.assertEqual(quiet(B2.main, argv), 0)
        d = json.loads(out.read_text())
        self.assertEqual((d["decision"], d["repilot_job_id"]), ("GO", "123"))
        with self.assertRaises(FileExistsError):
            quiet(B2.main, argv)
        argv[argv.index("--priced-node-h") + 1] = "1.0"
        argv[-1] = str(self.tmp / "c.json")
        self.assertEqual(quiet(B2.main, argv), 3)

    def test_refusals(self):
        t, s = B2.TUNES[0], B2.seeds(B2.TUNES[0])["long"][0]
        p = self.tmp / t / f"long_s{s}.time"
        good = p.read_text()
        for plant in ("missing", "failed", "undeclared"):
            with self.subTest(plant):
                if plant == "missing":
                    p.unlink()
                elif plant == "failed":
                    p.write_text(time_v("2:00.00", 20 * GIB, exit_status=137))
                else:
                    (self.tmp / t / "long_s99999.time").write_text(good)
                with self.assertRaises(SystemExit):
                    B2.load_runs(self.tmp)
                p.write_text(good)
                (self.tmp / t / "long_s99999.time").unlink(missing_ok=True)


class SubmitHelper(unittest.TestCase):
    """submit_fd_f1.sh f1b2 with stub sbatch and sacct on PATH."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-sub-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.bin / "sbatch").write_text('#!/bin/bash\necho "SBATCH $*" > "$STUB_LOG"\necho "Submitted batch job 1"\n')
        (self.bin / "sacct").write_text('#!/bin/bash\necho "$STUB_MAXRSS"\n')
        for f in ("sbatch", "sacct"):
            (self.bin / f).chmod(0o755)
        self.out = self.tmp / "OUT"
        (self.out / "f1a2").mkdir(parents=True)

    def submit(self, decision="GO", job="777", maxrss="300000000K"):
        b = {"decision": decision, "f1b2_time_limit": "00:41:00"}
        if job:
            b["repilot_job_id"] = job
        (self.out / "f1a2/budget2.json").write_text(json.dumps(b, indent=1))
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", STUB_LOG=str(self.tmp / "sbatch.log"),
                   STUB_MAXRSS=maxrss)
        (self.tmp / "sbatch.log").unlink(missing_ok=True)
        return subprocess.run(["bash", str(ND / "submit_fd_f1.sh"), "f1b2", "/D", "PIN", str(self.out)], env=env,
                              capture_output=True, text=True)

    def test_go_submits_with_the_gates_limit(self):
        p = self.submit()
        self.assertEqual(p.returncode, 0, p.stderr)
        line = (self.tmp / "sbatch.log").read_text()
        for x in ("--qos=regular", "--constraint=cpu", "--no-requeue", "--time=00:41:00", "--job-name=fd_f1b2"):
            self.assertIn(x, line)

    def test_refusals(self):
        limit_k = 487802 * 1024 * 3 // 4
        for kw in (dict(decision="STOP"), dict(job=None), dict(maxrss=f"{limit_k + 1}K"), dict(maxrss="400G"),
                   dict(maxrss="")):
            with self.subTest(**kw):
                p = self.submit(**kw)
                self.assertNotEqual(p.returncode, 0)
                self.assertFalse((self.tmp / "sbatch.log").exists())
        self.assertEqual(self.submit(maxrss=f"{limit_k}K").returncode, 0)
        self.assertEqual(self.submit(maxrss="350000M").returncode, 0)


class Scripts(unittest.TestCase):
    def test_the_repilot_is_the_gates(self):
        a = (ND / "sbatch_fd_f1a2.sh").read_text()
        self.assertIn(f'run "$T" long {B2.N_TASK} "$s"', a)
        self.assertIn(f'run "$T" short {B2.N1} "${{S[$k]}}" && run "$T" short {B2.N1}', a)
        self.assertIn("for k in $(seq 0 2 6)", a)
        self.assertEqual(a.count("/usr/bin/time -v -o"), 1)
        self.assertIn('--job-id "$SLURM_JOB_ID"', a)
        self.assertIn("flux-check", a)
        self.assertIn('[ ! -e "$F" ]', a)
        self.assertAlmostEqual(float(re.search(r"SPENT=([0-9.]+)", a).group(1)), 0.104722 + 0.202778, places=6)

    def test_f1b2_never_touches_f1b_and_stops_on_a_failure(self):
        b = (ND / "sbatch_fd_f1b2.sh").read_text()
        self.assertNotRegex(b, r'"\$OUT/f1b"|\$OUT/f1b/')
        self.assertIn('F="$OUT/f1b2"', b)
        self.assertIn(f'[ "$P" = {B2.P} ]', b)
        self.assertIn('xargs -P "$P"', b)
        self.assertIn("|| exit 255' < \"$F/queue.txt\"", b)
        self.assertIn("NT=64; NEV=17500", b)
        self.assertEqual((B2.N_TASK, B2.N_TASKS, B2.WAVES), (17500, 128, 8))
        self.assertIn("declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)", b)
        self.assertIn("reused.sha256", b)

    def test_the_reused_products_are_exactly_five(self):
        a = (ND / "sbatch_fd_f1a2.sh").read_text()
        pat = re.search(r"grep -E '(.*?)' \"\$SUMS\"", a).group(1)
        lines = [l for l in SUMS.read_text().splitlines() if re.search(pat, l)]
        self.assertEqual(sorted(l.split("  ./")[1] for l in lines),
                         ["flux_phi_t_0_100.root", "graphs_AR23_20i_00_000.root", "graphs_G18_10a_02_11b.root",
                          "splines/AR23_20i_00_000_CH.xml.gz", "splines/G18_10a_02_11b_CH.xml.gz"])

    def test_submission_lines_and_caps(self):
        sub = (ND / "submit_fd_f1.sh").read_text()
        self.assertIn('--time=00:20:00 --job-name=fd_f1a2 "$D/nd-unfolding/sbatch_fd_f1a2.sh" "$D" "$PIN" "$OUT" "$PRICED" "$CEIL"', sub)
        for x in ("--account=m3246", "--qos=regular", "--constraint=cpu", "--exclusive", "--no-requeue"):
            self.assertIn(x, sub)
        self.assertNotRegex(sub, r"(--qos[= ]|-q )\S*premium")
        self.assertNotRegex(sub, r"--(gpus|gpus-per-node|gres)[= ](?!none)|-G ")
        self.assertLessEqual(0.3075 + 20 / 60 + B2.F1B_MAX_S / 3600 + B2.F1C_LIMIT_H, 2.5)     # Joseph's ceiling
        self.assertEqual((B2.NODE_MEM_KIB, B2.MEM_FRACTION), (487_802 * 1024, 0.75))


if __name__ == "__main__":
    unittest.main()
