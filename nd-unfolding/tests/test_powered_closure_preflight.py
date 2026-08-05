"""Login-safe tests for the powered-closure submission-side gate and its launcher.

No GPU / no TF / no training / no submit / no 9.9 GB dump. The gate reads exactly three .npy members
(`w_truth`, `pass_truth`, `truth_scalars`), which is what makes it testable against a few-hundred-KB
synthetic npz instead of the real inventory.

What these lock down, and why each one is here rather than assumed:

  * The launcher's code pins must be DISCOVERABLE by verify_hash_bindings.collect_shell. Before
    2026-08-05 this launcher split its driver check across an assignment and a comparison, so the pin
    was enforced at runtime but invisible to the repo-wide verifier: an edit to the driver would have
    left the pin stale while the verifier went on printing ALL BINDINGS INTACT. Byte-identical
    behaviour, alarm disconnected -- exactly the failure mode test_hash_bindings.py exists for, one
    level further out.
  * The gate must have no bypass, must be able to FAIL, and must leave its receipt behind when it
    does. The reason the powered closure was submitted without knowing whether `gap` cleared its
    threshold is that the pre-flight smoke's report was discarded, and a gate whose evidence
    evaporates on failure reproduces that.
  * The gate's PASS is NOT the closure's PASS. It bounds two of three criteria; a collector that
    reads `verdict: PASS` out of a preflight receipt as the closure verdict would be claiming a
    recovery nobody measured.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ND)
PET = os.path.join(ND, "pet")
sys.path.insert(0, PET)

import closure_powered_truth_reweight as drv   # noqa: E402  (login-safe: TF imported inside main)
import fullevent_fps_dataloader as fe          # noqa: E402  (login-safe)
import preflight_powered_closure as pf         # noqa: E402  (login-safe)
from train_fullevent_nominal import NOMINAL_SEED_POLICY  # noqa: E402  (login-safe)

LAUNCHER = os.path.join(PET, "sbatch_powered_closure.sh")
GATE = os.path.join(PET, "preflight_powered_closure.py")
VERIFIER = os.path.join(REPO, "docs", "orchestration", "verify_hash_bindings.py")


def _load_verifier():
    spec = importlib.util.spec_from_file_location("vhb", VERIFIER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def synth_dump(path, *, n_rows, pt_values, ppar_values, all_truth=True, seed=1234):
    """A dump carrying ONLY the three members the gate reads.

    `pt_values`/`ppar_values` are sampled with replacement, so the number of OCCUPIED (pT,p||) cells
    -- not the 285 the grid has -- is what sets the A/B sampling floor. Concentrating the rows in a
    few cells is how a PASS becomes reachable at a few thousand rows instead of the real run's 2M:
    floor falls as sqrt(occupied_cells / n).
    """
    rng = np.random.default_rng(seed)
    scalars = np.zeros((n_rows, 4), np.float32)
    scalars[:, fe.SCALAR_COLS["pt"]] = rng.choice(np.asarray(pt_values, np.float32), n_rows)
    scalars[:, fe.SCALAR_COLS["pparallel"]] = rng.choice(np.asarray(ppar_values, np.float32), n_rows)
    pass_truth = (np.ones(n_rows, bool) if all_truth
                  else rng.random(n_rows) < 0.9)
    np.savez(path, w_truth=np.ones(n_rows, np.float32), pass_truth=pass_truth,
             truth_scalars=scalars)
    return path


def run_gate(inputs, receipt, *extra):
    r = subprocess.run([sys.executable, GATE, "--inputs", inputs, "--json", receipt] + list(extra),
                       capture_output=True, text=True)
    return r


class PreflightGateBehaviour(unittest.TestCase):
    # A handful of pT bins at ONE p|| bin: few occupied cells, so the floor is small at modest n.
    CONCENTRATED_PT = [0.03, 0.20, 0.36, 0.60, 0.90, 1.35]
    ONE_PPAR = [1.0]

    def test_passes_and_writes_a_receipt_when_the_criteria_are_met(self):
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=60000,
                             pt_values=self.CONCENTRATED_PT, ppar_values=self.ONE_PPAR)
            rec = os.path.join(td, "pf.json")
            r = run_gate(npz, rec, "--half-size", "20000", "--amplitude", "0.6")
            self.assertEqual(r.returncode, 0, f"expected PASS\n{r.stdout}\n{r.stderr}")
            d = json.load(open(rec))
            self.assertEqual(d["verdict"], "PASS")
            self.assertTrue(d["checks"]["gap_at_or_above_min"])
            self.assertTrue(d["checks"]["floor_over_gap_at_or_below_max"])
            self.assertGreaterEqual(d["metrics"]["gap"], drv.GAP_MIN)
            self.assertLessEqual(d["metrics"]["floor_over_gap"], drv.FLOOR_OVER_GAP_MAX)

    def test_fails_with_exit_3_when_the_injection_is_too_weak(self):
        """gap < GAP_MIN is the SIZE-INVARIANT failure: no half-size and no training recovers it."""
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=60000,
                             pt_values=self.CONCENTRATED_PT, ppar_values=self.ONE_PPAR)
            rec = os.path.join(td, "pf.json")
            r = run_gate(npz, rec, "--half-size", "20000", "--amplitude", "0.002")
            self.assertEqual(r.returncode, 3, f"expected the decided-FAIL code\n{r.stdout}")
            d = json.load(open(rec))
            self.assertEqual(d["verdict"], "FAIL")
            self.assertFalse(d["checks"]["gap_at_or_above_min"])
            self.assertIn("too weak", r.stderr)

    def test_fails_when_the_sampling_floor_eats_the_signal(self):
        """floor/gap is the noise-driven failure, and the one that scales away with a bigger half.

        This is the criterion the 20,000-row GPU smoke of 2026-08-04 actually failed (measured at the
        real dump: floor/gap 0.4040 at half 20,000 against 0.0459 at half 2,000,000). Distinguishing
        it from the gap failure above is the whole reason the gate reports which check tripped.
        """
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=4000,
                             pt_values=list(np.linspace(0.02, 3.0, 15)),
                             ppar_values=list(np.linspace(0.5, 30.0, 12)))
            rec = os.path.join(td, "pf.json")
            r = run_gate(npz, rec, "--half-size", "400", "--amplitude", "0.6")
            self.assertEqual(r.returncode, 3, f"expected the decided-FAIL code\n{r.stdout}")
            d = json.load(open(rec))
            self.assertFalse(d["checks"]["floor_over_gap_at_or_below_max"])
            self.assertIn("1/sqrt(n)", r.stderr)

    def test_receipt_survives_a_failure(self):
        """The discarded-smoke-report defect. A gate that fails without leaving its numbers behind
        is why nobody could tell whether the 08-04 smoke's FAIL was benign."""
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=4000,
                             pt_values=list(np.linspace(0.02, 3.0, 15)),
                             ppar_values=list(np.linspace(0.5, 30.0, 12)))
            rec = os.path.join(td, "pf.json")
            self.assertEqual(run_gate(npz, rec, "--half-size", "400").returncode, 3)
            d = json.load(open(rec))
            for k in ("gap", "floor", "floor_over_gap"):
                self.assertIsInstance(d["metrics"][k], float)
            self.assertEqual(len(d["spectra"]["h_prior"]), 285)

    def test_fails_closed_on_a_row_budget_it_cannot_meet(self):
        """Not enough rows for two disjoint halves -> exit 1, NOT a PASS and not a decided FAIL."""
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=100,
                             pt_values=self.CONCENTRATED_PT, ppar_values=self.ONE_PPAR)
            r = run_gate(npz, os.path.join(td, "pf.json"), "--half-size", "2000")
            self.assertEqual(r.returncode, 1)
            self.assertIn("disjoint halves", r.stdout + r.stderr)

    def test_fails_closed_on_a_dump_missing_a_member(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "d.npz")
            np.savez(p, w_truth=np.ones(500, np.float32))   # no pass_truth, no truth_scalars
            r = run_gate(p, os.path.join(td, "pf.json"), "--half-size", "100")
            self.assertEqual(r.returncode, 1)
            self.assertIn("pass_truth", r.stdout + r.stderr)

    def test_gate_pass_is_not_the_closure_verdict(self):
        """A collector must not be able to read this receipt as 'the powered closure passed'."""
        with tempfile.TemporaryDirectory() as td:
            npz = synth_dump(os.path.join(td, "d.npz"), n_rows=60000,
                             pt_values=self.CONCENTRATED_PT, ppar_values=self.ONE_PPAR)
            rec = os.path.join(td, "pf.json")
            self.assertEqual(run_gate(npz, rec, "--half-size", "20000",
                                      "--amplitude", "0.6").returncode, 0)
            d = json.load(open(rec))
            self.assertNotEqual(d["receipt_schema"], drv.REPORT_SCHEMA,
                                "the preflight must not share the closure report's schema string")
            self.assertTrue(d["not_evaluated_here"]["verdict_is_not_the_closure_verdict"])
            self.assertIn("residual", d["not_evaluated_here"])
            self.assertNotIn("residual", d["metrics"])
            self.assertNotIn("recovery", d["metrics"])


class GateAndDriverAgreeOnTheProtocol(unittest.TestCase):
    def test_thresholds_come_from_the_driver_by_import(self):
        """One set of constants, not two. A gate holding its own copy of GAP_MIN would go on passing
        after the protocol was tightened."""
        for name in ("GAP_MIN", "FLOOR_OVER_GAP_MAX", "RESIDUAL_OVER_GAP_MAX", "HALF_SIZE",
                     "SPLIT_SEED", "TILT_AMPLITUDE", "TILT_CLIP_Z"):
            self.assertEqual(getattr(pf, name), getattr(drv, name), name)
        src = open(GATE).read()
        for name in ("GAP_MIN", "FLOOR_OVER_GAP_MAX", "RESIDUAL_OVER_GAP_MAX", "HALF_SIZE"):
            self.assertNotRegex(src, rf"(?m)^{name}\s*=",
                                f"{name} is redefined in the gate instead of imported")

    def test_shared_functions_are_the_driver_objects(self):
        for name in ("clipped_exponential_tilt", "deterministic_halves", "unit_spectrum", "l1"):
            self.assertIs(getattr(pf, name), getattr(drv, name), name)

    def test_gate_reproduces_the_loaders_subsample_draw(self):
        """The gate's one duplication (see its docstring). Pinned equal here, and re-measured against
        the driver's own gap/floor by the launcher's post-run cross-check on every real run."""
        n, need, seed = 49152885, 4_000_000, int(NOMINAL_SEED_POLICY["subsample_seed"])
        mine = np.sort(np.random.default_rng(seed).choice(n, min(need, n), replace=False))
        theirs = np.sort(np.random.default_rng(seed).choice(n, min(need, n), replace=False))
        self.assertTrue(np.array_equal(mine, theirs))
        self.assertEqual(mine.size, need)
        # The loader's line, read out of its source, so a change to it fails HERE rather than in a
        # 12-hour job's cross-check. fullevent_fps_dataloader.py is hash-pinned by the Gate-2
        # receipt, so this test cannot import a shared helper -- there is nowhere to put one.
        loader_src = open(os.path.join(PET, "fullevent_fps_dataloader.py")).read()
        self.assertIn("np.sort(np.random.default_rng(seed).choice(N, min(max_events, N), "
                      "replace=False))", loader_src,
                      "the loader's subsample draw moved; the gate's copy must move with it")


class LauncherWiring(unittest.TestCase):
    def setUp(self):
        self.src = open(LAUNCHER).read()

    def test_bash_syntax(self):
        r = subprocess.run(["bash", "-n", LAUNCHER], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_gate_byte_compiles(self):
        r = subprocess.run([sys.executable, "-m", "py_compile", GATE],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_code_pins_are_discoverable_by_the_repo_verifier(self):
        """THE regression test. collect_shell pairs a pin to a file only from a single line naming
        exactly one `sha_of "$VAR"` and exactly one `$EXPECTED_*_SHA`; a two-line check enforces the
        pin at runtime and is invisible to the verifier."""
        m = _load_verifier()
        found = []
        m.collect_shell(self.src, os.path.relpath(LAUNCHER, REPO), found)
        resolved = {}
        for target, want, _src in found:
            lp = m.localize(target, REPO)
            if lp:
                resolved[os.path.relpath(lp, REPO)] = want
        for expect in ("nd-unfolding/pet/closure_powered_truth_reweight.py",
                       "nd-unfolding/pet/preflight_powered_closure.py"):
            self.assertIn(expect, resolved, f"{expect} pin is not verifier-discoverable")
            self.assertEqual(resolved[expect], m.sha256(os.path.join(REPO, expect)),
                             f"{expect} pin is stale")

    def test_pin_floor_covers_these_pins(self):
        """SHELL_PIN_FLOOR must count pins on TRACKED files only -- this checkout resolves more,
        because it also holds the 9.9 GB dump and a compiled binary that no clone is guaranteed."""
        m = _load_verifier()
        import glob
        found = []
        for f in (glob.glob(os.path.join(REPO, "docs/**/*.sh"), recursive=True)
                  + glob.glob(os.path.join(REPO, "nd-unfolding/**/*.sh"), recursive=True)
                  + glob.glob(os.path.join(REPO, "2d-unfolding/**/*.sh"), recursive=True)):
            m.collect_shell(open(f).read(), os.path.relpath(f, REPO), found)
        tracked = set(subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True,
                                     text=True).stdout.split())
        n_tracked = sum(1 for p, _, _ in found
                        if (lp := m.localize(p, REPO)) and os.path.relpath(lp, REPO) in tracked)
        self.assertGreaterEqual(n_tracked, m.SHELL_PIN_FLOOR,
                                "fewer tracked shell pins than the floor demands")
        self.assertEqual(n_tracked, m.SHELL_PIN_FLOOR,
                         "tracked shell pins changed; raise SHELL_PIN_FLOOR to match (never lower "
                         "it to make this pass)")

    def test_launcher_runs_the_gate_before_the_training(self):
        i_gate = self.src.index('python3 "$PREFLIGHT"')
        i_train = self.src.index('srun -n 1 -c 32 --gpus=1 python3 "$DRIVER"')
        self.assertLess(i_gate, i_train, "the gate must run before the GPU is spent")

    def test_launcher_aborts_when_the_gate_fails(self):
        self.assertRegex(self.src, r"if \[\[ \$pf_rc -ne 0 \]\]; then")
        self.assertRegex(self.src, r"(?s)if \[\[ \$pf_rc -ne 0 \]\]; then.*?exit \$pf_rc")

    def test_no_bypass_switch(self):
        """An env var that skips a gate is the vacuous pass, shipped."""
        for bad in ("SKIP_PREFLIGHT", "NO_PREFLIGHT", "FORCE_RUN", "POWERED_SKIP"):
            self.assertNotIn(bad, self.src)

    def test_launcher_overrides_no_protocol_constants(self):
        """The gate and the driver must both run at the predeclared configuration.

        Comment lines are stripped first: the header says in prose that it overrides none of these,
        and a raw substring search reads that promise as the violation it forbids.
        """
        code = "\n".join(ln for ln in self.src.splitlines() if not ln.lstrip().startswith("#"))
        for flag in ("--half-size", "--amplitude", "--clip-z", "--split-seed", "--max-events"):
            self.assertNotIn(flag, code, f"launcher passes {flag}; that moves the goalposts")

    def test_cross_check_is_wired_and_can_fail_the_run(self):
        self.assertIn("PREFLIGHT_XCHECK_RTOL", self.src)
        self.assertIn("DIVERGED", self.src)
        self.assertRegex(self.src, r"if \[\[ \$xrc -ne 0 && \$rc -eq 0 \]\]; then\s*\n\s*rc=\$xrc")

    def test_log_directory_is_tracked(self):
        """slurmstepd opens --output before this script's mkdir runs, so the directory has to exist
        at submit time. Job 56355818 was submitted without it."""
        keep = os.path.join(PET, "powered_closure", "logs", ".gitkeep")
        self.assertTrue(os.path.isfile(keep))
        tracked = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch",
                                  os.path.relpath(keep, REPO)], capture_output=True, text=True)
        self.assertEqual(tracked.returncode, 0, "the log directory marker is not tracked")


if __name__ == "__main__":
    unittest.main()
