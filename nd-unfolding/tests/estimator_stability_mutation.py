"""Mutation check of the estimator-stability probe's tests (FD-STAB-DECLARATION.md §8).

Each mutation plants one declared defect in a temporary copy of a module, runs the suite with that copy first on
sys.path, and must make the NAMED test fail (not merely some test). Exit 0 only if every mutation is killed by its
named test and the unmutated suite passes.

    python3 -B nd-unfolding/tests/estimator_stability_mutation.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_estimator_stability_probe.py"
P, A, S = "estimator_stability_probe.py", "estimator_stability_analyze.py", "sbatch_fd_stab.sh"
EXPECTED_TESTS = 93  # a script-mode run that stops early (unittest.main mid-file) exits 0 with fewer: refuse it
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
    ("bias criterion ignored", A, 'stab[c]["passes"] and bias_ok.get(c, False) is True]', 'stab[c]["passes"]]', "test_none_pass"),
    ("hypothesis pin unchecked", A, 'if (m.get("hypothesis") or {}).get("sha256") != expected_pin(hyp, repo):', "if False:",
     "test_the_product_checks_refuse"),
    # --- the #720 audit (coverage-5b-audit, 2026-11-03): each finding and test gap, with the test that must kill it
    ("overlapping pairs", A, "m = np.maximum(z[2 * p], z[2 * p + 1])", "m = np.maximum(z[p], z[p + 1])",
     "test_pairs_are_the_25_disjoint_ones"),
    ("passes from the worst pair", A, "maxs.mean() <= BOUND_MAX)}", "maxs.max() <= BOUND_MAX)}",
     "test_passes_reads_the_mean_over_pairs_not_the_worst_pair"),
    ("MAX noise from the noisiest cell", A, "return s_rms, float(s[kmax])", "return s_rms, float(s.max())",
     "test_max_noise_is_the_argmax_cells"),
    ("delta from the candidate alone", A, "d_max = FLOOR_K * SD_UPPER * math.hypot(nmc, nm0)",
     "d_max = FLOOR_K * SD_UPPER * math.hypot(nmc, 0.0)", "test_delta_combines_both_estimators_noise"),
    ("cell SD halved", A, "    return np.std(rel, axis=0, ddof=1)\n", "    return 0.5 * np.std(rel, axis=0, ddof=1)\n",
     "test_scale"),
    ("cell SD around the base (R3)", A, "    return np.std(rel, axis=0, ddof=1)\n",
     "    return np.sqrt(np.mean((rel[1:] - 1.0) ** 2, axis=0))\n", "test_sd_is_around_the_mean_with_ddof_one"),
    ("zero floor judged (R4)", A, "if not (d_rms > 0 and d_max > 0):", "if False:", "test_a_zero_floor_is_invalid_not_worse"),
    ("invalid floor ignored (R4)", A, "    if invalid:\n", "    if False:\n", "test_an_invalid_floor_makes_the_verdict_invalid"),
    ("expectation unchecked", A, 'if not (m.get("development") or {}).get("expectation"):', "if False:",
     "test_the_product_checks_refuse"),
    ("amplitude unchecked", A, 'or float(got_alt.get("amplitude")) != amp', "", "test_the_product_checks_refuse"),
    ("bootstrap replica admitted", A, 'if m.get("bootstrap_seed") is not None:', "if False:", "test_the_product_checks_refuse"),
    ("stability input unchecked", A, '"pseudo", probe.STABILITY_TRUTH["truth"], probe.STABILITY_TRUTH["ratio_sha256"], probe.STABILITY_PSEUDO_SEED):',
     '"pseudo", probe.STABILITY_TRUTH["truth"], probe.STABILITY_TRUTH["ratio_sha256"], probe.STABILITY_PSEUDO_SEED) and False:',
     "test_the_product_checks_refuse"),
    ("sigma pin unchecked", A, "if probe.sha256_path(Path(a.sigma_receipt)) != SIGMA_RECEIPT_SHA256:", "if False:",
     "test_the_sigma_pin_refuses_another_receipt"),
    ("closure split unchecked (R5)", A, 'if m.get("pseudo_seed") != probe.CLOSURE_SEED or', "if False and",
     "test_the_product_checks_refuse"),
    ("split not paired with the control (R5)", A, 'if splits[c] != splits["control"]:', "if False:",
     "test_the_product_checks_refuse"),
    ("determinism pair unchecked", A, "if not np.array_equal(x0, x1):", "if False:", "test_the_product_checks_refuse"),
    ("functionals not required", A, "if int(ok.sum()) != N_FUNCTIONALS:", "if False:",
     "test_every_candidate_must_use_all_the_functionals"),
    ("stability seed retyped", P, "STABILITY_PSEUDO_SEED = 990000", "STABILITY_PSEUDO_SEED = 990001", "test_constants"),
    ("closure seed retyped", P, "CLOSURE_SEED = 991000", "CLOSURE_SEED = 991001", "test_constants"),
    ("MC fraction dropped from the queue", P, '"--mc-fraction", CLOSURE_MC_FRACTION, ', "",
     "test_the_task_list_carries_them"),
    ("namespace: data admitted (R2)", P, 'if getattr(ns, "construction", None) != "pseudo":', "if False:",
     "test_the_namespace_check_refuses_what_the_runner_would_read"),
    ("product without the check (R2)", P, "if mode is not None and not state[\"checked\"]:", "if False:",
     "test_no_product_without_the_check"),
    ("repeats admitted (R2)", P, "            if name in seen:\n", "            if False:\n",
     "test_the_prescan_refuses_the_five_forms"),
    ("gate ignores the cap (R1)", P, 'if p["projected_node_h"] > cap:', 'if p["projected_node_h"] > cap + 100:',
     "test_stops_before_a_launch_past_the_cap"),
    ("gate ignores B2's ratio", P, 'elif p["b2_over_control"] is not None and p["b2_over_control"] > B2_STOP_RATIO:', "elif False:",
     "test_b2_above_twice_the_control_stops_and_below_does_not"),
    ("B2 assumed at 1x before measurement", P, 'ASSUMED_FACTOR = {"B2": 2.0}', 'ASSUMED_FACTOR = {"B2": 1.0}',
     "test_unmeasured_b2_at_twice_does_not_fit_the_cap"),
    ("running tasks counted in full", P, 'free.append(max(0.0, est - (now - r["start"])))', "free.append(est)",
     "test_running_tasks_count_their_remainder"),
    ("finished task rerun", P, '    if (log / f"{task}.end").exists():\n        return 4\n', "",
     "test_a_finished_task_is_skipped_not_rerun"),
    # --- the audit's second round (F1-F3) and its surviving mutants
    ("--pairs as two tokens (F1)", P, '"--pairs=" + ",".join(chunk),', '"--pairs", ",".join(chunk),',
     "test_every_queue_line_parses_and_passes_under_the_real_runners"),
    ("main without the guard's mode", P, "    with install(candidate, mode):", "    with install(candidate):",
     "test_every_queue_line_parses_and_passes_under_the_real_runners"),
    ("tail unpriced (F2)", P, "    wall_left = max(free) if free else 0.0", "    wall_left = sum(free) / lanes if free else 0.0",
     "test_the_tail_is_priced"),
    ("rates pooled over kinds", P, "        if (c, k) in per_ck:\n", "        if False:\n", "test_rates_are_per_kind"),
    ("B2 ratio pooled over kinds", P,
     'ratios = [per_ck[("B2", k)][0] / per_ck[("B2", k)][1] / (per_ck[("control", k)][0] / per_ck[("control", k)][1])\n'
     '              for k in ("stability", "closure") if ("B2", k) in per_ck and ("control", k) in per_ck]',
     'ratios = ([per_c["B2"][0] / per_c["B2"][1] / (per_c["control"][0] / per_c["control"][1])]\n'
     '              if "B2" in per_c and "control" in per_c else [])', "test_the_b2_ratio_is_like_for_like"),
    ("B2 rule at >=", P, 'p["b2_over_control"] > B2_STOP_RATIO:', 'p["b2_over_control"] >= B2_STOP_RATIO:',
     "test_b2_at_exactly_twice_is_admitted"),
    ("namespace: closure split unchecked", P, 'if getattr(ns, "mc_fraction", None) != CLOSURE_MC_FRACTION or \\\n',
     'if False and \\\n', "test_check_namespace_in_both_directions"),
    ("namespace: config unchecked", P, '    if getattr(ns, "config", None) != "R":', "    if False:",
     "test_check_namespace_in_both_directions"),
    ("namespace: closure noise-free unchecked", P,
     '        if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)):', "        if False:",
     "test_check_namespace_in_both_directions"),
    ("invalid only if every truth is", A, "return None if any(v is None for v in per_truth) else all(per_truth)",
     "return None if all(v is None for v in per_truth) else all(v for v in per_truth if v is not None)",
     "test_one_invalid_truth_makes_the_candidate_invalid"),
    ("zero floor needs both zero", A, "if not (d_rms > 0 and d_max > 0):", "if not (d_rms > 0 or d_max > 0):",
     "test_either_zero_floor_is_invalid"),
    ("split key may be absent", A, ' or m.get("split_key") is None:', ":", "test_the_product_checks_refuse"),
    ("full run without the DONE receipt (F3)", S, '    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] ||',
     '    [ ! -e "$OUT/log-dry/STOP" ] ||', "test_a_failed_task_stops_the_queue_and_the_full_run_refuses"),
    ("dry-run ends unchecked (F3)", S, '        [ -e "$OUT/log-dry/$id.end" ] ||', "        true ||",
     "test_a_dry_run_without_every_task_ended_is_refused"),
    ("a failed task does not stop the queue", S, '        > "$L/tasks/$id.log" 2>&1 || exit 255',
     '        > "$L/tasks/$id.log" 2>&1 || exit 0', "test_a_failed_task_in_the_full_run_stops_the_queue"),
    ("dirty deploy admitted", S, '[ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]', '[ "$head_sha" != "$PIN" ]',
     "test_a_dirty_deploy_refuses"),
    ("existing log admitted", S, '[ ! -e "$L" ] || {', "true || {", "test_an_existing_log_refuses"),
    ("environment check dropped", S, 'python3 -c "import lightgbm, scipy, numpy" >> "$L/env.log" 2>&1 ||', "true ||",
     "test_an_environment_without_lightgbm_refuses"),
    ("STOP not sticky", P, "    if stop.exists():\n        return 3\n", "", "test_stops_before_a_launch_past_the_cap"),
    # --- the audit's third round (G2, G3)
    ("B2 ratio from the cheaper kind (G3)", P, '"b2_over_control": max(ratios) if ratios', '"b2_over_control": min(ratios) if ratios',
     "test_b2_over_twice_in_one_kind_only_stops"),
    ("ended count unchecked (G3)", S, '[ "$n_end" -eq "$n_q" ] ||', "true ||",
     "test_an_end_lost_during_the_run_leaves_no_receipt"),
    ("a stopped run's products unpinned (G2)", S,
     "( cd \"$OUT\" && find runs -type f -name '*.npz' -print0 | sort -z | xargs -0 sha256sum ) > \"$L/SHA256SUMS\"\n", "",
     "test_a_reprice_stop_keeps_and_pins_the_products_and_is_not_resumed"),
    ("an incomplete run graded (G2)", A, "    why = incomplete(Path(a.receipt))\n", "    why = None\n",
     "test_an_incomplete_run_is_not_graded"),
    ("STOP or FAILED beside the receipt ignored (G2)", A, '    for name in ("STOP", "FAILED"):', "    for name in ():",
     "test_an_incomplete_run_is_not_graded"),
    ("the receipt's counts unchecked (G2)", A, 'd.get("tasks") != n or d.get("ended") != n', "False",
     "test_an_incomplete_run_is_not_graded"),
]


def run_suite(first: Path | None, script: Path | None = None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if script is not None:
        env["STAB_SBATCH"] = str(script)  # the job-script tests run this mutated copy
    p = subprocess.run([sys.executable, "-B", "-c", boot], capture_output=True, text=True, cwd=str(ND.parent), env=env)
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
            for f in (P, A, S):
                shutil.copy(ND / f, Path(d) / f)
            (Path(d) / fname).write_text(src.replace(old, new))
            rc, out = run_suite(Path(d), Path(d) / S if fname == S else None)
        fails = failing(out)
        killed = test in fails
        ok &= killed
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:35s} by {test}" + ("" if killed else f"  (failing: {sorted(fails)})"))
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
