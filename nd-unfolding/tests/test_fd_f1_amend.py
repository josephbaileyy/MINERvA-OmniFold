"""Controls for F1's amendment 1 (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md
section 5): the re-pilot gate fd_f1_budget2.py on synthetic /usr/bin/time -v records, and the new scripts against
the gate's constants. No real product is read.

* parse_time_v reads GNU time -v's wall, maximum RSS and exit status, and refuses an incomplete record.
* the seeds: 48 per tune, distinct, disjoint from F1b's and the pseudo-experiments', and the batch script's.
* decide: GO, and a STOP for each rule on its own (an unphysical fit, memory, the wall, the priced total), with the
  per-event time, load, memory extrapolation, time limit and worst case recomputed here.
* load_runs refuses a missing, an undeclared and a failed run.
* the scripts: the re-pilot's event counts and concurrency are the gate's, F1b' never touches F1b's directory, the
  reused F1a products are exactly the five declared files, and every submission line is regular QOS with no GPU."""
import contextlib
import io
import json
import math
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_f1_budget2 as B2  # noqa: E402
import fd_f1_tasks as TASKS  # noqa: E402

FD = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024"
SUMS = FD / "fd/receipts-f1/amendment-1/f1a-SHA256SUMS"


def time_v(elapsed: str, rss: int, exit_status: int = 0) -> str:
    return (f'\tCommand being timed: "bash run_gevgen_v3.sh genie"\n\tUser time (seconds): 1.0\n'
            f"\tElapsed (wall clock) time (h:mm:ss or m:ss): {elapsed}\n\tMaximum resident set size (kbytes): {rss}\n"
            f"\tExit status: {exit_status}\n")


def mmss(s: float) -> str:
    return f"{int(s // 60)}:{s % 60:05.2f}"


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class TimeRecords(unittest.TestCase):
    def test_parse(self):
        r = B2.parse_time_v(time_v("1:02:03.5", 3_800_000))
        self.assertEqual(r, {"elapsed_s": 3723.5, "maxrss_kib": 3_800_000, "exit": 0})
        self.assertEqual(B2.parse_time_v(time_v("2:05.25", 10))["elapsed_s"], 125.25)
        for bad in ("", time_v("1:00", 5).replace("Exit status: 0", ""), time_v("1:00", 5).replace("Maximum", "Max")):
            with self.subTest(), self.assertRaises(ValueError):
                B2.parse_time_v(bad)
        with self.assertRaises(ValueError):
            B2.wall_seconds("12")


class Seeds(unittest.TestCase):
    def test_declared_seeds(self):
        f1b = {60000 + k for k in range(1, 65)} | {61000 + k for k in range(1, 65)}
        pe = set(range(806000, 806020)) | set(range(807000, 807020))
        seen = set()
        for tune in B2.TUNES:
            s = B2.seeds(tune)
            self.assertEqual((len(s["long"]), len(s["short"])), (B2.N_LONG, 2 * B2.N_SHORT))
            both = set(s["long"]) | set(s["short"])
            self.assertEqual(len(both), 48)
            self.assertFalse(both & f1b or both & pe or both & seen or both & {60000, 61000})
            seen |= both
        text = (ND / "sbatch_fd_f1a2.sh").read_text()
        base = dict(re.findall(r"\[(\w+)\]=(\d+)", re.search(r"BASE2=\((.*?)\)", text).group(1)))
        for tune in B2.TUNES:
            b = int(base[tune])
            self.assertEqual(B2.seeds(tune)["long"], list(range(b + 1, b + 17)))
            self.assertEqual(B2.seeds(tune)["short"], list(range(b + 17, b + 49)))


def runs(long_w=100.0, short_w=70.0, long_m=1_000_000, short_m=800_000, tune_scale=None):
    out = {}
    for tune in B2.TUNES:
        k = (tune_scale or {}).get(tune, 1.0)
        out[tune] = {"long": [{"elapsed_s": long_w * k - i * 0.1, "maxrss_kib": long_m - i, "exit": 0} for i in range(16)],
                     "short": [{"elapsed_s": short_w * k - i * 0.05, "maxrss_kib": short_m - i, "exit": 0} for i in range(32)]}
    return out


class Decide(unittest.TestCase):
    def test_go_with_every_number_recomputed(self):
        r = runs(tune_scale={"AR23_20i_00_000": 1.1})
        d = B2.decide(r, 0.3075, 0.10, 2.0)
        t = (100.0 * 1.1 - 70.0 * 1.1) / 1500
        load = 70.0 * 1.1 - 1500 * t
        self.assertAlmostEqual(d["fit"]["AR23_20i_00_000"]["per_event_s"], t)
        self.assertAlmostEqual(d["fit"]["AR23_20i_00_000"]["load_s"], load)
        wall = 2 * (load + 17500 * t) + 900
        self.assertAlmostEqual(d["f1b2_projected_wall_s"], wall)
        slope = (1_000_000 - 800_000) / 1500
        self.assertAlmostEqual(d["f1b2_projected_mem_kib"], 64 * (1_000_000 + slope * (17500 - 3000)))
        lim = math.ceil(wall * 1.25 / 60)
        self.assertEqual(d["f1b2_time_limit"], f"{lim // 60:02d}:{lim % 60:02d}:00")
        self.assertAlmostEqual(d["worst_case_node_h"], 0.3075 + 0.10 + lim / 60 + 0.9)
        self.assertAlmostEqual(d["f1_projected_node_h"], 0.3075 + 0.10 + wall / 3600 + 0.75)
        self.assertEqual(d["decision"], "GO")
        self.assertEqual((d["concurrency"], d["waves"]), (64, 2))

    def test_each_rule_stops_on_its_own(self):
        base = dict(spent_node_h=0.3075, pilot_node_h=0.1, priced_node_h=2.0)
        cases = {
            "fit": (runs(long_w=80.0, short_w=90.0), "fit_ok"),                                   # t < 0
            "load": (runs(long_w=300.0, short_w=100.0), "fit_ok"),                               # load < 0
            "memory": (runs(long_m=5_000_000, short_m=2_000_000), "mem_ok"),                     # 64 x 34 GB
            "wall": (runs(long_w=400.0, short_w=250.0), "f1b2_fits_its_limit"),
        }
        for name, (r, key) in cases.items():
            with self.subTest(name):
                d = B2.decide(r, **base)
                self.assertFalse(d[key])
                self.assertEqual(d["decision"], "STOP")
        d = B2.decide(runs(), 0.3075, 0.1, 2.0, 1.5)                                             # the ceiling
        self.assertTrue(d["within_priced"])
        self.assertFalse(d["within_ceiling"])
        self.assertEqual(d["decision"], "STOP")
        self.assertTrue(B2.decide(runs(), 0.3075, 0.1, 2.0, 2.5)["within_ceiling"])
        d = B2.decide(runs(), 0.3075, 0.1, 1.25)                                                 # the priced total
        self.assertTrue(d["fit_ok"] and d["mem_ok"] and d["f1b2_fits_its_limit"])
        self.assertFalse(d["within_priced"])
        self.assertEqual(d["decision"], "STOP")

    def test_memory_boundary_and_no_negative_slope_credit(self):
        cap = 0.75 * B2.NODE_MEM_KIB / 64
        d = B2.decide(runs(long_m=int(cap) - 1, short_m=int(cap) - 1), 0.3, 0.1, 9.0)
        self.assertTrue(d["mem_ok"])
        d = B2.decide(runs(long_m=int(cap) + 1, short_m=int(cap) + 1), 0.3, 0.1, 9.0)
        self.assertFalse(d["mem_ok"])
        d = B2.decide(runs(long_m=1_000_000, short_m=2_000_000), 0.3, 0.1, 9.0)                 # shrinking RSS
        self.assertAlmostEqual(d["fit"]["G18_10a_02_11b"]["rss_at_task_kib"], 1_000_000)


class LoadRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f1-b2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for tune in B2.TUNES:
            (self.tmp / tune).mkdir()
            for role, ss in B2.seeds(tune).items():
                for s in ss:
                    (self.tmp / tune / f"{role}_s{s}.time").write_text(time_v(mmss(100 if role == "long" else 70), 900_000))

    def test_reads_every_declared_run_and_main_decides(self):
        r = B2.load_runs(self.tmp)
        self.assertEqual({t: (len(v["long"]), len(v["short"])) for t, v in r.items()}, {t: (16, 32) for t in B2.TUNES})
        out = self.tmp / "b.json"
        argv = ["--runs", str(self.tmp), "--spent-node-h", "0.3075", "--repilot-node-h", "0.1", "--priced-node-h",
                "2.0", "--ceiling-node-h", "2.5", "--out", str(out)]
        self.assertEqual(quiet(B2.main, argv), 0)
        self.assertEqual(json.loads(out.read_text())["decision"], "GO")
        with self.assertRaises(FileExistsError):
            quiet(B2.main, argv)
        argv[argv.index("2.0")] = "1.25"
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
                    p.write_text(time_v("2:30.00", 900_000, exit_status=137))
                else:
                    (self.tmp / t / "long_s99999.time").write_text(good)
                with self.assertRaises(SystemExit):
                    B2.load_runs(self.tmp)
                p.write_text(good)
                (self.tmp / t / "long_s99999.time").unlink(missing_ok=True)


class Scripts(unittest.TestCase):
    def test_the_repilot_is_the_gates(self):
        a = (ND / "sbatch_fd_f1a2.sh").read_text()
        self.assertIn(f'run "$T" long {B2.N2} "$s"', a)
        self.assertIn(f'run "$T" short {B2.N1} "${{S[$k]}}" && run "$T" short {B2.N1}', a)
        self.assertEqual(a.count("/usr/bin/time -v -o"), 1)
        self.assertIn("flux-check", a)
        self.assertIn('[ ! -e "$F" ]', a)
        spent = float(re.search(r"SPENT=([0-9.]+)", a).group(1))
        self.assertAlmostEqual(spent, 0.104722 + 0.202778, places=6)
        led = (FD / "fd/LEDGER.tsv").read_text() if (FD / "fd/LEDGER.tsv").exists() else ""
        if "60417614" in led:     # on the report branch the ledger carries both charges
            self.assertIn("0.202778", led)
            self.assertIn("0.104722", led)

    def test_f1b2_never_touches_f1b_and_runs_at_the_declared_concurrency(self):
        b = (ND / "sbatch_fd_f1b2.sh").read_text()
        self.assertNotRegex(b, r'"\$OUT/f1b"|\$OUT/f1b/')
        self.assertIn('F="$OUT/f1b2"', b)
        self.assertIn(f'[ "$P" = {B2.P} ]', b)
        self.assertIn('xargs -P "$P"', b)
        self.assertIn("NT=64; NEV=17500", b)
        self.assertEqual((B2.N_TASK, B2.N_TASKS), (17500, 128))
        self.assertIn("declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)", b)
        self.assertIn('"decision": "GO"', b)
        self.assertIn("reused.sha256", b)

    def test_the_reused_products_are_exactly_five(self):
        a = (ND / "sbatch_fd_f1a2.sh").read_text()
        pat = re.search(r"grep -E '(.*?)' \"\$SUMS\"", a).group(1)
        lines = [l for l in SUMS.read_text().splitlines() if re.search(pat, l)]
        self.assertEqual(sorted(l.split("  ./")[1] for l in lines),
                         ["flux_phi_t_0_100.root", "graphs_AR23_20i_00_000.root", "graphs_G18_10a_02_11b.root",
                          "splines/AR23_20i_00_000_CH.xml.gz", "splines/G18_10a_02_11b_CH.xml.gz"])
        rec = {l.split("  ./")[1]: l.split()[0] for l in lines}
        self.assertEqual(rec["splines/G18_10a_02_11b_CH.xml.gz"], "dbd305df75dcd731a25dd0b20064ba52c20f095196ea21694997169831788c82")
        self.assertEqual(rec["splines/AR23_20i_00_000_CH.xml.gz"], "f3a763e5e22e7f0246a838d6d2e8b94287f6f7137f71882dad5582cbab5439ba")

    def test_submission_lines(self):
        sub = (ND / "submit_fd_f1.sh").read_text()
        self.assertIn('--time=00:20:00 --job-name=fd_f1a2 "$D/nd-unfolding/sbatch_fd_f1a2.sh" "$D" "$PIN" "$OUT" "$PRICED" "$CEIL"', sub)
        self.assertIn('--time="$T" --job-name=fd_f1b2', sub)
        self.assertIn("f1b2_time_limit", sub)
        for x in ("--account=m3246", "--qos=regular", "--constraint=cpu", "--exclusive", "--no-requeue"):
            self.assertIn(x, sub)
        self.assertNotRegex(sub, r"(--qos[= ]|-q )\S*premium")
        self.assertNotRegex(sub, r"--(gpus|gpus-per-node|gres)[= ](?!none)|-G ")

    def test_mem_limit_is_the_nodes(self):
        self.assertEqual(B2.NODE_MEM_KIB, 487_802 * 1024)
        self.assertEqual(B2.MEM_FRACTION, 0.75)
        self.assertEqual(B2.WAVES, 2)


if __name__ == "__main__":
    unittest.main()
