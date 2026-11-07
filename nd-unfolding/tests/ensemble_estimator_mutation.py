"""Mutation check of ENS1's tests (ENS1-DECLARATION.md §2.2, §9; ENS1-BINDING-1.md ruling 4: REQUIRED mutants for every
gate, reading and refusal, including the three float32 traps).

Each mutation plants one declared defect in a temporary copy of a module and runs the suite with that copy first on
sys.path (the job script's copy through ENS1_SBATCH). The mutation must make its NAMED test fail, not merely some test.
Exit 0 only if every mutation is killed by its named test and the unmutated suite runs all EXPECTED_TESTS and passes.
The child runs with PYTHONDONTWRITEBYTECODE, so no stale bytecode of an earlier copy can stand in for the mutant.

    python3 -B nd-unfolding/tests/ensemble_estimator_mutation.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_ensemble_estimator.py"
P, A, S = "ensemble_estimator_probe.py", "ensemble_estimator_analyze.py", "sbatch_ens1.sh"
EXPECTED_TESTS = 49  # a script-mode run that stops early exits 0 with fewer: refuse it

# (label, file, old, new, the test that must fail)
MUTATIONS = [
    # --- REQUIRED: the three float32 traps and the scale (§2.1, §2.2; audit ENS-1, ENS-2)
    ("REQ internal jitter after a float32 cast", P,
     "        y = np.asarray(inputs[key], np.float64)\n        ji[key] = y + internal_step(y, rng, edges)",
     "        y = np.asarray(np.asarray(inputs[key], np.float32), np.float64)\n        ji[key] = y + internal_step(y, rng, edges)",
     "test_it_acts_on_y_at_full_precision_not_after_a_float32_cast"),
    ("REQ internal jitter at +-1/4 spacing", P, "step = rng.uniform(-0.5, 0.5, y.shape) * ulp",
     "step = rng.uniform(-0.5, 0.5, y.shape) * ulp * 0.5",
     "test_the_scale_is_plus_or_minus_half_the_float32_spacing_in_both_directions"),
    ("REQ closure unfolds in float32", P, 'return o["unfold_one"](exp, np.float64, *args, **kw)',
     'return o["unfold_one"](exp, dtype, *args, **kw)', "test_the_closure_unfolds_in_float64_whatever_the_runner_asks"),
    ("REQ G0 admits a float32 base", A,
     'if m.get("coords") != "float64" or m.get("jitter_seed") != eep.BASE_SEED:', "if False:",
     "test_g0_refuses_a_float32_base"),
    ("REQ seed 0 is a protocol jitter", P, 'ji, jb = o["jittered"](inputs, bkg, None if seed == BASE_SEED else seed)',
     'ji, jb = o["jittered"](inputs, bkg, seed)', "test_seed_zero_is_the_float64_copy_and_then_delta_k"),
    # --- the internal jitter
    ("grid edges moved", P,
     "            step[np.isin(r64[:, a], np.asarray(e, np.float32).astype(np.float64)), a] = 0.0", "            pass",
     "test_grid_edges_are_not_moved_and_other_values_are"),
    ("one stream for every k", P, "rng = np.random.default_rng(INTERNAL_BASE + k)", "rng = np.random.default_rng(INTERNAL_BASE)",
     "test_fixed_per_k_and_distinct_across_k"),
    ("undeclared k accepted", P, "    if k not in range(1, N_ENS + 1):\n        raise Refusal", "    if False:\n        raise Refusal",
     "test_an_undeclared_k_is_refused"),
    # --- refusals (probe)
    ("a write without the check", P, '        if not st["checked"]:\n            raise Refusal("refusing to write',
     '        if False:\n            raise Refusal("refusing to write', "test_a_write_without_the_namespace_check_is_refused"),
    ("any pair accepted", P, "    if len(pairs) != 1 or pairs[0] not in allowed:", "    if False:",
     "test_undeclared_pairs_and_inputs_are_refused_and_the_declared_call_is_not"),
    ("threads unchecked (stability)", P,
     '    for key in ("iters", "threads", "estimator_seed"):\n        if getattr(ns, key, None) != want[key]:',
     '    for key in ("iters", "estimator_seed"):\n        if getattr(ns, key, None) != want[key]:',
     "test_undeclared_pairs_and_inputs_are_refused_and_the_declared_call_is_not"),
    ("truth unchecked (stability)", P,
     'if getattr(ns, "truth", None) != want["truth"] or float(getattr(ns, "amplitude", -1)) != want["amplitude"]:',
     "if False:", "test_undeclared_pairs_and_inputs_are_refused_and_the_declared_call_is_not"),
    ("closure hypothesis unchecked", P,
     'if str(getattr(ns, "hypothesis", "")) != hyp and not str(getattr(ns, "hypothesis", "")).endswith("/" + hyp):',
     "if False:", "test_closure_namespace"),
    ("closure alternative unchecked", P,
     'if got_alt is None or not str(got_alt).endswith(tail) or float(getattr(ns, "alternative_amplitude", -1)) != amp:',
     "if False:", "test_closure_namespace"),
    ("closure noise allowed", P, 'if not (getattr(ns, "expectation", False) and getattr(ns, "no_nuisance", False)) or \\',
     "if False and \\", "test_closure_namespace"),
    ("closure grid move unchecked", P, "        if any(moved.values()):\n            raise Refusal",
     "        if False:\n            raise Refusal", "test_a_move_across_the_grid_is_refused_before_the_build"),
    ("closure build without delta_k", P, 'return o["build"](ji, jb, split, seed, expectation, mc_fraction)',
     'return o["build"](ui, ub, split, seed, expectation, mc_fraction)',
     "test_the_closure_inputs_carry_delta_k_and_differ_across_k"),
    ("CLI accepts an undeclared k", P, 'if mode != "base" and (len(set(ks)) != len(ks) or', 'if False and (len(set(ks)) != len(ks) or',
     "test_cli_refuses_an_undeclared_k"),
    ("queue runs A7 MnvTune at every k", P, "            if t == DETERMINISM[1]:\n                continue\n",
     "            if False:\n                continue\n", "test_the_declared_counts"),
    # --- gates and the stage-1 verdict (analysis)
    ("E1 two codes accepted", A, "    if len(codes) != 1:", "    if False:", "test_one_code_and_distinct_digests_are_required"),
    ("E2 identical inputs accepted", A, "        if len({digests[(s, k)] for s in seeds}) != len(seeds):", "        if False:",
     "test_one_code_and_distinct_digests_are_required"),
    ("E3 reference unpinned", A, "if n not in pinned or not p.is_file() or sha256_path(p) != pinned[n]:",
     "if not p.is_file():", "test_references_must_be_pinned_and_from_the_same_estimator_code"),
    ("LOW-2 other estimator code", A, "        if estimator_code(m) != want:", "        if False:",
     "test_references_must_be_pinned_and_from_the_same_estimator_code"),
    ("G0 always informative", A, 'g0 = not stab_F["passes"]', "g0 = True", "test_g0_reads_uninformative_when_the_control_passes"),
    ("bar ignored", A, 'verdict = "STAB_PASS" if stab_E["passes"] else "STAB_FAIL"', 'verdict = "STAB_PASS"',
     "test_a_small_ensemble_spread_passes_and_a_large_one_fails"),
    ("P = 9", A, "N, P = eep.N_ENS, 10", "N, P = eep.N_ENS, 9",
     "test_the_rebound_statistic_is_the_hand_computation_and_the_bound_one_at_25"),
    ("N_PAIRS not restored", A, "    finally:\n        esa.N_PAIRS = saved", "    finally:\n        pass",
     "test_n_pairs_is_restored_after_a_raise"),
    ("receipt pin unchecked", A, 'or d.get("pin") != pin or', "or", "test_an_incomplete_stage_grades_nothing"),
    ("receipt FAILED ignored", A, 'for bad in ("STOP", "FAILED"):', "for bad in ():", "test_an_incomplete_stage_grades_nothing"),
    ("receipt missing shard accepted", A, "        if not done.is_file():\n            return", "        if False:\n            return",
     "test_an_incomplete_stage_grades_nothing"),
    ("c_hat without the 1/(1+q)", A, "    return q / (1.0 + q)", "    return q", "test_c_hat_recovers_c"),
    ("c_hat reading at eps for c*", A, "    if top >= C_STAR:", "    if top >= EPS:", "test_the_c_hat_reading_in_each_direction"),
    ("stage 2 without STAB_PASS", A, '    if s1.get("verdict") != "STAB_PASS":', "    if False:",
     "test_stage2_refuses_without_stab_pass"),
    # --- stage 2
    ("s_E without its own factor", A, 's_E = np.asarray(s1["cell_sd_E96"], float) * (SD_UPPER_E / esa.SD_UPPER)',
     's_E = np.asarray(s1["cell_sd_E96"], float)', "test_s_e_carries_its_own_upper_factor"),
    ("s_F not reproduced", A, "    if not np.allclose(s_F, committed, rtol=0, atol=1e-8):", "    if False:", "test_the_stops"),
    ("determinism xsec unchecked", A, "    if not (np.array_equal(d0[0], d1[0]) and np.array_equal(d0[1], d1[1])):",
     "    if not np.array_equal(d0[1], d1[1]):", "test_the_stops"),
    ("determinism xtrue unchecked", A, "    if not (np.array_equal(d0[0], d1[0]) and np.array_equal(d0[1], d1[1])):",
     "    if not np.array_equal(d0[0], d1[0]):", "test_the_stops"),
    ("truth vector across k unchecked", A, "            elif not np.array_equal(xt, xt0):", "            elif False:", "test_the_stops"),
    ("closure digests unchecked", A, '            if got != {json.dumps((mF.get(key) or {}).get("sha256"))}:', "            if False:",
     "test_the_stops"),
    ("closure split unchecked", A, '        if {m.get("split_key") for m in metas} != {mF.get("split_key")}:', "        if False:",
     "test_the_stops"),
    ("zero floor read as a verdict", A, 'verdict = "INVALID" if status is None else ("PASS" if status else "BIAS_WORSE")',
     'verdict = "PASS" if status else "BIAS_WORSE"', "test_a_zero_floor_is_invalid"),
    ("worse read as a pass", A, 'verdict = "INVALID" if status is None else ("PASS" if status else "BIAS_WORSE")',
     'verdict = "INVALID" if status is None else "PASS"', "test_pass_and_bias_worse"),
    # --- the job script
    ("pin unchecked", S, 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', "if false; then",
     "test_refusals_existing_log_wrong_pin_bad_stage_or_shard_dirty_deploy"),
    ("existing log reused", S, '[ ! -e "$L" ] || {', "true || {", "test_refusals_existing_log_wrong_pin_bad_stage_or_shard_dirty_deploy"),
    ("any stage accepted", S, 'case "$STAGE" in 1|2) ;;', 'case "$STAGE" in *) ;;',
     "test_refusals_existing_log_wrong_pin_bad_stage_or_shard_dirty_deploy"),
    ("any shard accepted", S, 'case "$I" in [0-5]) ;;', 'case "$I" in *) ;;',
     "test_refusals_existing_log_wrong_pin_bad_stage_or_shard_dirty_deploy"),
    ("shard without the dry receipt", S, '[ -s "$SD/log-dry/DONE" ] && [ ! -e "$SD/log-dry/FAILED" ] ||', "true ||",
     "test_a_shard_refuses_without_the_dry_done_or_at_another_pin"),
    ("shard at another pin", S, '[ "$dry_pin" = "$PIN" ] ||', "true ||", "test_a_shard_refuses_without_the_dry_done_or_at_another_pin"),
    ("a failed task still writes DONE", S, '[ -z "$failed" ] && [ "$rc" -eq 0 ] || {', "true || {",
     "test_a_failed_task_leaves_no_receipt"),
    # --- REQUIRED: the teardown guard (RS1-BINDING-2 addendum A1; the director's ruling 5 for ENS1)
    ("REQ teardown crash read as a failure", S, 'if [ "$all" -ne 1 ]; then echo "rc=$rc before',
     'if true; then echo "rc=$rc before', "test_a_teardown_crash_is_recomputed_once_and_compared"),
    ("REQ pre-write failure read as a teardown", S, 'for f in "${files[@]}"; do [ -e "$f" ] || all=0; done', "true",
     "test_a_failure_before_writing_is_a_failure_and_the_queue_continues"),
    ("REQ a second crash accepted", S, 'if [ "$rc" -ne 0 ]; then echo "rc=$rc on the re-run',
     'if false; then echo "rc=$rc on the re-run', "test_a_second_crash_is_a_failure"),
    ("REQ xargs aborts on a failure", S, 'before every product was written" > "$L/$id.failed"; exit 1; fi',
     'before every product was written" > "$L/$id.failed"; exit 255; fi',
     "test_a_failure_before_writing_is_a_failure_and_the_queue_continues"),
    ("REQ crashed products kept, not recomputed", S, 'for f in "${files[@]}"; do mv "$f" "$T/" ||',
     'for f in; do mv "$f" "$T/" ||', "test_a_teardown_crash_is_recomputed_once_and_compared"),
    ("expect names another tag", P, 'product_name(f"ens1_k{k:03d}", b, j) for k in ks]',
     'product_name(f"ens1_k{k:02d}", b, j) for k in ks]', "test_expect_names_exactly_what_the_task_wrote"),
    ("environment unchecked", S, '|| { echo "[ens1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }', "|| true",
     "test_an_environment_without_lightgbm_is_refused"),
]


def run_suite(first: Path | None, script: Path | None = None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("ENS1_SBATCH", None)
    if script is not None:
        env["ENS1_SBATCH"] = str(script)
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
    print(f"UNMUTATED SUITE: {EXPECTED_TESTS} tests, rc 0")
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
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:42s} by {test}" + ("" if killed else f"  (failing: {sorted(fails)})"),
              flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
