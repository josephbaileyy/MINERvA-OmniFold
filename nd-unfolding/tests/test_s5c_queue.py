"""Controls for the unattended s5c lanes (s5c_queue.sh, s5c_launch.sh, s5c_futility_watch.sh): each
behaviour is exercised in the direction it acts and on its innocent neighbour, against stub
squeue/scancel on PATH. Run on the target interpreter (the login node's bash)."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
QUEUE, LAUNCH, WATCH = ND / "s5c_queue.sh", ND / "s5c_launch.sh", ND / "s5c_futility_watch.sh"


def _exe(path: Path, body: str) -> None:
    path.write_text("#!/bin/bash\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class Harness(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="s5c-queue-"))
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.tmp / "ns" / "runs").mkdir(parents=True)
        self.env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "S5C_NS": str(self.tmp / "ns"),
                    "S5C_QUEUE_POLL": "0.1", "S5C_QUEUE_RETRY": "0.1", "S5C_WATCH_POLL": "0.1"}
        # squeue: call k prints line k of squeue.seq ("FAIL" = exit 1); past the end, prints nothing
        (self.tmp / "squeue.seq").write_text("")
        _exe(self.bin / "squeue", f"""n=$(cat {self.tmp}/squeue.n 2>/dev/null || echo 0); echo $((n+1)) > {self.tmp}/squeue.n
line=$(sed -n "$((n+1))p" {self.tmp}/squeue.seq)
[ "$line" = FAIL ] && exit 1
[ -n "$line" ] && printf '%b\\n' "$line"
exit 0
""")
        _exe(self.bin / "scancel", f'echo "$@" >> {self.tmp}/scancel.log\n')

    def queue(self, lines: list[str], stop: bool = False) -> subprocess.CompletedProcess:
        q = self.tmp / "q.txt"
        q.write_text("\n".join(lines) + "\n")
        stopf = self.tmp / "STOP"
        if stop:
            stopf.write_text("x")
        return subprocess.run(["bash", str(QUEUE), str(q), str(stopf)], env=self.env, capture_output=True,
                              text=True, timeout=60)

    def mark(self, name: str) -> str:
        return f"touch {self.tmp}/{name}"


class QueueTests(Harness):
    def test_follows_a_launched_job_until_it_leaves_then_runs_the_next_line(self) -> None:
        (self.tmp / "squeue.seq").write_text("11\n11\\n99\n")
        r = self.queue(["echo LAUNCHED job=11", self.mark("second")])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("job 11 left the queue", r.stdout)
        self.assertEqual((self.tmp / "squeue.n").read_text().strip(), "3")  # seen twice, then gone
        self.assertTrue((self.tmp / "second").exists())

    def test_an_squeue_failure_is_not_read_as_the_job_having_left(self) -> None:
        (self.tmp / "squeue.seq").write_text("FAIL\n11\n")
        r = self.queue(["echo LAUNCHED job=11", self.mark("second")])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.tmp / "squeue.n").read_text().strip(), "3")

    def test_concurrency_refusal_is_retried(self) -> None:
        c = self.tmp / "c"
        line = f'n=$(cat {c} 2>/dev/null || echo 0); echo $((n+1)) > {c}; [ $n -ge 2 ] && echo LAUNCHED job=12 || exit 4'
        r = self.queue([line, self.mark("second")])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(c.read_text().strip(), "3")
        self.assertTrue((self.tmp / "second").exists())

    def test_a_cap_refusal_stops_the_queue(self) -> None:
        r = self.queue(["exit 3", self.mark("second")])
        self.assertEqual(r.returncode, 1)
        self.assertIn("STOPPED the queue (exit 3)", r.stdout)
        self.assertFalse((self.tmp / "second").exists())

    def test_not_granted_is_retried_a_bounded_number_of_times(self) -> None:
        c = self.tmp / "c"
        r = self.queue([f'echo x >> {c}; exit 7'])
        self.assertEqual(r.returncode, 1)
        self.assertEqual(len(c.read_text().split()), 13)

    def test_stop_file_skips_validation_lines_only(self) -> None:
        r = self.queue([self.mark("valid") + " # s5c_valid_launch.sh", self.mark("construct")], stop=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.tmp / "valid").exists())
        self.assertTrue((self.tmp / "construct").exists())

    def test_without_stop_file_validation_lines_run(self) -> None:
        r = self.queue([self.mark("valid") + " # s5c_valid_launch.sh"])
        self.assertEqual(r.returncode, 0)
        self.assertTrue((self.tmp / "valid").exists())


class QueueDeployTests(Harness):
    def repo_queue(self, dirty: bool) -> subprocess.CompletedProcess:
        repo = self.tmp / "repo"
        (repo / "q").mkdir(parents=True)
        (repo / "q" / "lane.q").write_text(f'echo "$S5C_DEPLOY $S5C_PIN" > {self.tmp}/seen\n')
        g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(g[:3] + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "q/lane.q"], check=True)
        subprocess.run(g + ["commit", "-q", "-m", "q"], check=True)
        if dirty:
            (repo / "q" / "lane.q").write_text("touch x\n")
        return subprocess.run(["bash", str(QUEUE), str(repo / "q" / "lane.q"), str(self.tmp / "STOP")],
                              env=self.env, capture_output=True, text=True, timeout=60)

    def test_a_committed_queue_exports_its_clean_checkout_and_head(self) -> None:
        r = self.repo_queue(dirty=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        head = subprocess.run(["git", "-C", str(self.tmp / "repo"), "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
        deploy, pin = (self.tmp / "seen").read_text().split()
        self.assertEqual((Path(deploy).resolve(), pin), ((self.tmp / "repo").resolve(), head))

    def test_a_dirty_checkout_is_refused(self) -> None:
        r = self.repo_queue(dirty=True)
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.tmp / "seen").exists())


class LaunchTests(Harness):
    def setUp(self) -> None:
        super().setUp()
        self.deploy = self.tmp / "deploy"
        t = self.deploy / "docs/orchestration/state/s5c"
        t.mkdir(parents=True)
        (t / "a.tsv").write_text("x\n")
        (t / "b.tsv").write_text("x\n")

    def launch(self, *tracks: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(LAUNCH), str(self.deploy), "sha", "gpu", "st", "1", "lab", "8G", "m",
                               *tracks], env={**self.env, "S5C_LAUNCH_DRYRUN": "1"}, capture_output=True,
                              text=True)

    def test_relative_tracks_become_committed_table_and_namespace_paths(self) -> None:
        r = self.launch("a.tsv:o1:1:5:7", "a.tsv:o1:1:8:8,b.tsv:o2:2")
        self.assertEqual(r.returncode, 0, r.stderr)
        t, ns = self.deploy / "docs/orchestration/state/s5c", self.tmp / "ns" / "runs"
        self.assertEqual(r.stdout.splitlines(), [
            f"track {t}/a.tsv:{ns}/o1:1:5:7",
            f"track {t}/a.tsv:{ns}/o1:1:8:8,{t}/b.tsv:{ns}/o2:2"])

    def test_an_uncommitted_table_is_refused(self) -> None:
        r = self.launch("missing.tsv:o:1")
        self.assertEqual(r.returncode, 2)
        self.assertIn("no committed table", r.stderr)


class FutilityWatchTests(Harness):
    def setUp(self) -> None:
        super().setUp()
        self.deploy = self.tmp / "deploy"
        c = self.deploy / "docs/orchestration/state/s5c"
        (c / "d1").mkdir(parents=True)
        (self.deploy / "nd-unfolding").mkdir()
        c.joinpath("contract.json").write_text(json.dumps({"coverage": {"grid": [
            {"truth": "nominal", "amplitude": 0, "validation_seeds": [100, 199]},
            {"truth": "tilt", "amplitude": 0.2, "validation_seeds": [200, 299]}]}}))
        self.sv = self.tmp / "ns" / "runs" / "s_valid"
        self.sv.mkdir()
        for s in range(100, 103):
            (self.sv / f"nominal_a0_s{s}.npz").write_text("")
        for s in range(200, 203):
            (self.sv / f"tilt_a0.2_s{s}.npz").write_text("")
        (self.tmp / "squeue.seq").write_text("21 s5c-tier_s_valid_cpu_0\\n22 s5c-f2_construction_2\n")

    def watch(self, verdict: str, n: int = 3) -> subprocess.CompletedProcess:
        py = self.tmp / "bin" / "fakepy"
        _exe(py, f"""out=""; while [ $# -gt 0 ]; do [ "$1" = --out ] && out=$2; shift; done
echo '{{"verdict": "{verdict}"}}' > "$out"
""")
        return subprocess.run(["bash", str(WATCH), str(self.deploy), str(n), str(self.tmp / "STOP")],
                              env={**self.env, "S5C_PY": str(py)}, capture_output=True, text=True, timeout=60)

    def test_futility_fail_writes_the_stop_file_and_cancels_validation_only(self) -> None:
        r = self.watch("FUTILITY-FAIL")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("present 6 of 6", r.stdout)
        self.assertTrue((self.tmp / "STOP").exists())
        self.assertEqual((self.tmp / "scancel.log").read_text().split(), ["21"])

    def test_continue_changes_nothing(self) -> None:
        r = self.watch("CONTINUE")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.tmp / "STOP").exists())
        self.assertFalse((self.tmp / "scancel.log").exists())

    def test_it_waits_while_a_declared_seed_is_missing(self) -> None:
        (self.sv / "tilt_a0.2_s202.npz").unlink()
        p = subprocess.Popen(["bash", str(WATCH), str(self.deploy), "3", str(self.tmp / "STOP")],
                             env={**self.env, "S5C_PY": "/bin/false"}, stdout=subprocess.PIPE, text=True)
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                p.wait(timeout=1.5)
        finally:
            p.kill()
        out = p.stdout.read()
        self.assertIn("present 5 of 6", out)
        self.assertNotIn("verdict", out)


if __name__ == "__main__":
    unittest.main()
