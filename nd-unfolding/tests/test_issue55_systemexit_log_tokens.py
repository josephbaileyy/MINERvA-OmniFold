"""ISSUE-55: the fatal-token scan must match what a SystemExit REALLY prints in these jobs' logs.

Both validators used to carry "SystemExit:" as their only token for a driver guard. A
`raise SystemExit("<msg>")` prints only `<msg>` to stderr, so that token could never match. These
tests use COMPLETE real Perlmutter logs (see fixtures/issue55_real_logs/PROVENANCE.tsv) and a real
child interpreter, never strings copied from the validators, and they test both directions:
  FIRES   on a real driver-guard failure's stderr, on the data-only path AND the replica/g1 path;
  SILENT  on a real healthy replica-family log pair, whose STDOUT does carry "[gate5-train]".
"""
import ast
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PET = HERE.parent / "pet"
REPO = HERE.parents[1]
FIX = HERE / "fixtures" / "issue55_real_logs"
WATCH_FIX = REPO / "docs" / "orchestration" / "test_fixtures_watch_report"
sys.path.insert(0, str(PET))

import cstat_data_only_readback as rb  # noqa: E402
import validate_gate5_training_artifacts as g1  # noqa: E402

OLD_TOKENS = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]

# Real driver-guard failures: (fixture path, what it is). The two watch-report fixtures are verbatim
# excerpts (final lines) of the real .err files; 57266000_0 is the complete file.
REAL_GUARD_ERRS = [
    FIX / "train_57266000_0.err.txt",
    WATCH_FIX / "train_57253127_0.err.txt",
    WATCH_FIX / "train_57256638_0.err.txt",
]
HEALTHY_G1_OUT = FIX / "train_56857233_0.out.txt"
HEALTHY_G1_ERR = FIX / "train_56857233_0.err.txt"


def g1_fatal_expression():
    """Compile the pinned g1 validator's OWN fatal-token expression (the 2nd argument of its
    `checks.eq("fatal_log_tokens", ...)`) so the test runs g1's code rather than a re-typed copy."""
    src = (PET / "validate_gate5_training_artifacts.py").read_text()
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate_member")
    assign = [n for n in ast.walk(fn) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == "fatal_tokens" for t in n.targets)]
    call = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == "eq"
            and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "fatal_log_tokens"]
    assert len(assign) == 1 and len(call) == 1, (len(assign), len(call))
    tokens = ast.literal_eval(assign[0].value)
    expr = compile(ast.Expression(call[0].args[1]), "<g1 fatal expr>", "eval")

    def run(out_text, err_text):
        return eval(expr, {"FATAL_STDERR_TOKENS": g1.FATAL_STDERR_TOKENS},
                    {"fatal_tokens": tokens, "out_text": out_text, "err_text": err_text})
    return run, tokens, call[0].lineno


class WhatASystemExitPrints(unittest.TestCase):
    def test_a_child_interpreter_prints_the_bare_message(self):
        msg = "[gate5-train] target receipt unreadable: x"
        r = subprocess.run([sys.executable, "-c", f"raise SystemExit({msg!r})"],
                           capture_output=True, text=True)
        self.assertEqual(1, r.returncode)
        self.assertEqual(msg + "\n", r.stderr)
        self.assertEqual("", r.stdout)

    def test_a_SystemExit_in_a_thread_prints_nothing(self):
        code = ("import threading\n"
                "def f():\n    raise SystemExit('[gate5-train] in a thread')\n"
                "t = threading.Thread(target=f); t.start(); t.join()\n")
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(0, r.returncode)
        self.assertNotIn("SystemExit", r.stderr + r.stdout)

    def test_real_guard_failures_end_in_a_bare_prefixed_message(self):
        for p in REAL_GUARD_ERRS:
            text = p.read_text(errors="replace")
            last = [ln for ln in text.splitlines() if ln.strip()][-1]
            self.assertNotIn("SystemExit", text, p.name)
            self.assertNotIn("Traceback", text, p.name)
            self.assertTrue(any(last.startswith(t) for t in rb.FATAL_STDERR_TOKENS), (p.name, last))


class FiresOnRealFailure(unittest.TestCase):
    def test_g1_path_fires_on_every_real_guard_failure(self):
        run, _, _ = g1_fatal_expression()
        for p in REAL_GUARD_ERRS:
            self.assertNotEqual([], run("", p.read_text(errors="replace")), p.name)

    def test_MUTANT_the_old_list_misses_every_real_guard_failure(self):
        for p in REAL_GUARD_ERRS:
            text = p.read_text(errors="replace")
            self.assertEqual([], [t for t in OLD_TOKENS if t in text], p.name)

    def test_data_only_readback_fires_on_every_real_guard_failure(self):
        # A synthetic stdout with all five needles, so the ONLY thing that can raise is the token scan.
        idx, seed, job = 0, 50000, "57266000"
        out = "\n".join([
            f"{rb.LAUNCHER_LOG_PREFIX} index={idx} seed={seed} job={job}_{idx}",
            '"config_gate": "PASS"', rb.optimizer_proof_line(), '"status": "PASS"',
            f"{rb.LAUNCHER_LOG_PREFIX} DONE index={idx} seed={seed}"]) + "\n"
        for p in REAL_GUARD_ERRS:
            with tempfile.TemporaryDirectory() as tmp:
                d = Path(tmp)
                (d / f"train_{job}_{idx}.out").write_text(out)
                shutil.copyfile(p, d / f"train_{job}_{idx}.err")
                with self.assertRaises(SystemExit) as cm:
                    rb.assert_member_logs(d, array_job_id=job, replica_index=idx, bootstrap_seed=seed,
                                          where="issue55", launcher_log_prefix=rb.LAUNCHER_LOG_PREFIX)
                self.assertIn("fatal tokens present", str(cm.exception), p.name)


class SilentOnARealHealthyRun(unittest.TestCase):
    def test_g1_path_is_silent_on_the_real_healthy_pair(self):
        run, _, _ = g1_fatal_expression()
        out = HEALTHY_G1_OUT.read_text(errors="replace")
        err = HEALTHY_G1_ERR.read_text(errors="replace")
        self.assertIn("[gate5-train]", out, "the healthy stdout must carry the launcher prefix")
        self.assertIn("[gate4] WARNING", err, "the healthy stderr must carry the [gate4] warning")
        self.assertEqual([], run(out, err))

    def test_data_only_readback_passes_the_real_healthy_replica_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            shutil.copyfile(HEALTHY_G1_OUT, d / "train_56857233_0.out")
            shutil.copyfile(HEALTHY_G1_ERR, d / "train_56857233_0.err")
            res = rb.assert_member_logs(d, array_job_id="56857233", replica_index=0,
                                        bootstrap_seed=50000, where="issue55",
                                        launcher_log_prefix="[gate5-train]")
        self.assertEqual(8, res["checked"])

    def test_bare_gate4_would_false_alarm_so_it_is_not_a_token(self):
        err = HEALTHY_G1_ERR.read_text(errors="replace")
        self.assertIn("[gate4]", err)
        self.assertNotIn("[gate4]", rb.FATAL_STDERR_TOKENS)
        self.assertNotIn("[gate4]", g1.FATAL_STDERR_TOKENS)


class TheTwoPathsAgree(unittest.TestCase):
    def test_the_stderr_token_lists_are_equal(self):
        self.assertEqual(list(g1.FATAL_STDERR_TOKENS), list(rb.FATAL_STDERR_TOKENS))

    def test_no_list_still_carries_the_dead_token(self):
        _, g1_tokens, _ = g1_fatal_expression()
        self.assertNotIn("SystemExit:", g1_tokens)
        self.assertNotIn("SystemExit:", rb.FATAL_LOG_TOKENS)

    def test_the_g1_check_site_did_not_move_line(self):
        # The divergence manifest records site 345 as 'fatal_log_tokens'.
        _, _, line = g1_fatal_expression()
        self.assertEqual(345, line)

    def test_every_stderr_token_is_a_guard_prefix_in_the_driver_or_its_imports(self):
        srcs = "".join((PET / f).read_text() for f in (
            "train_fullevent_replica.py", "cstat_data_only.py", "train_fullevent_nominal.py"))
        for t in rb.FATAL_STDERR_TOKENS:
            self.assertIn(f'SystemExit(f"{t}', srcs.replace('SystemExit("', 'SystemExit(f"'), t)


if __name__ == "__main__":
    unittest.main()
