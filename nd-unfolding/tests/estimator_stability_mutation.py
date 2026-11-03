"""Mutation check of the estimator-stability probe's tests (FD-STAB-DECLARATION.md §8).

Each mutation plants one declared defect in a temporary copy of a module, runs the suite with that copy first on
sys.path, and must make the NAMED test fail (not merely some test). Exit 0 only if every mutation is killed by its
named test and the unmutated suite passes.

    python3 -B nd-unfolding/tests/estimator_stability_mutation.py
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_estimator_stability_probe.py"
P, A = "estimator_stability_probe.py", "estimator_stability_analyze.py"
EXPECTED_TESTS = 41  # a script-mode run that stops early (unittest.main mid-file) exits 0 with fewer: refuse it
MUTATIONS = [
    ("in-fold prediction", P, "rows = self.folds[:m] == f", "rows = self.folds[:m] != f",
     "test_every_evaluated_row_is_predicted_by_a_model_that_did_not_train_on_it"),
    ("step-2 copies split across folds", P, "            period = n // 2\n", "            period = None\n",
     "test_paired_copies_share_a_fold"),
    ("folds from values", P, "self.folds = fold_ids(n, self.k, self.key, period)",
     "self.folds = (np.abs(X[:, 0] * 1e9).astype(np.int64) % self.k)",
     "test_folds_unchanged_by_a_rounding_scale_perturbation"),
    ("B3 parameters dropped", P, 'if config == "deterministic" and est_params:', "if False:",
     "test_b3_parameters_reach_the_deterministic_configuration_only"),
    ("names not restored", P, "        s5c_unfold.config_params, onc.make_estimators, s5n_pseudo.write_product = orig_params, orig_make, orig_write\n",
     "        pass\n", "test_names_are_restored_on_exit_even_after_an_error"),
    ("data allowed", P, 'rest[rest.index("--construction") + 1] != "pseudo"', 'rest[rest.index("--construction") + 1] == "neither"',
     "test_refusals_fire"),
    ("q3 amplitude retyped", P, '"q3_given_eavail_w", 0.3)', '"q3_given_eavail_w", 0.4)', "test_amplitudes_and_kinds_are_f0s"),
    ("jitters pooled into one maximum", A, "m = np.maximum(z[2 * p], z[2 * p + 1])", "m = z.max(axis=0)",
     "test_a_single_extreme_jitter_does_not_set_the_statistic"),
    ("no noise floor", A, "FLOOR_K, SD_UPPER = 3.0, 1.20", "FLOOR_K, SD_UPPER = 0.0, 1.20", "test_within_the_floor_is_silent"),
    ("G0 inverted", A, 'return not control["passes"]', 'return control["passes"]', "test_g0"),
    ("co-winner tolerance dropped", A, '<= math.hypot(stab[c]["se_max"], stab[best]["se_max"]))', "<= 0)",
     "test_co_winners_within_one_combined_se"),
    ("bias criterion ignored", A, 'stab[c]["passes"] and bias_ok.get(c, False)]', 'stab[c]["passes"]]', "test_none_pass"),
    ("hypothesis pin unchecked", A, 'if (m.get("hypothesis") or {}).get("sha256") != expected_pin(hyp, repo):', "if False:",
     "test_the_product_checks_refuse"),
]


def run_suite(first: Path | None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    p = subprocess.run([sys.executable, "-B", "-c", boot], capture_output=True, text=True, cwd=str(ND.parent))
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main() -> int:
    rc, out = run_suite(None)
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-2000:])
        return 1
    ok = True
    for label, fname, old, new, test in MUTATIONS:
        src = (ND / fname).read_text()
        if src.count(old) != 1:
            print(f"MUTATION NOT APPLIED  {label}: anchor occurs {src.count(old)} times")
            ok = False
            continue
        with tempfile.TemporaryDirectory() as d:
            for f in (P, A):
                shutil.copy(ND / f, Path(d) / f)
            (Path(d) / fname).write_text(src.replace(old, new))
            rc, out = run_suite(Path(d))
        fails = failing(out)
        killed = test in fails
        ok &= killed
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:35s} by {test}" + ("" if killed else f"  (failing: {sorted(fails)})"))
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
