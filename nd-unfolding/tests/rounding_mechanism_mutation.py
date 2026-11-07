"""Mutation check of RS1's tests (RS1-DECLARATION.md §8; RS1-BINDING-1.md ruling 3: a REQUIRED mutant for every gate,
reading and refusal).

Each mutation plants one declared defect in a temporary copy of a module and runs the suite with that copy first on
sys.path (the job script's copy through RS1_SBATCH). The mutation must make its NAMED test fail, not merely some test.
Exit 0 only if every mutation is killed by its named test and the unmutated suite runs all EXPECTED_TESTS and passes.
The child runs with PYTHONDONTWRITEBYTECODE, so no stale bytecode of an earlier copy can stand in for the mutant.

    python3 -B nd-unfolding/tests/rounding_mechanism_mutation.py
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_rounding_mechanism.py"
P, A, S = "rounding_mechanism_probe.py", "rounding_mechanism_analyze.py", "sbatch_rs1.sh"
EXPECTED_TESTS = 50  # a script-mode run that stops early exits 0 with fewer: refuse it

# (label, file, old, new, the test that must fail). Every gate, reading and refusal has at least one.
MUTATIONS = [
    # --- arms and their rebindings (probe)
    ("seed 0 is a jitter (E2)", P, 'if seed == UNJITTERED_F64:\n            return o["jittered"](inputs, bkg, None)',
     'if seed == UNJITTERED_F64:\n            return o["jittered"](inputs, bkg, seed)',
     "test_seed_zero_is_the_upcast_and_a_jitter_differs_by_exactly_the_step"),
    ("V steps by the spacing above", P, "step[:, k] = u * 0.5 * ulp_toward_zero(x32[:, k])",
     "step[:, k] = u * 0.5 * np.spacing(np.abs(x32[:, k])).astype(np.float64)",
     "test_order_is_strictly_preserved_across_powers_of_two"),
    ("V keyed by row, not value", P, "h = _splitmix64(bits[:, k] ^ key)",
     "h = _splitmix64(np.arange(len(bits), dtype=np.uint64) ^ key)", "test_ties_are_kept_and_the_protocol_breaks_them"),
    ("V moves grid edges", P,
     "            step[np.isin(out[:, k], np.asarray(e, np.float32).astype(np.float64)), k] = 0.0\n    return out + step",
     "            pass\n    return out + step", "test_edges_unmoved_and_steps_within_half_the_spacing_toward_zero"),
    ("F_k leaks the other axes", P, "out[:, axis] = full[:, axis]", "out = full",
     "test_axis_k_carries_the_protocols_own_draws_and_the_others_none"),
    ("S-ref's loop jittered", P, 'loop_exp = exp if side in ("omni", "all") else exp_u', "loop_exp = exp",
     "test_s_ref_jitters_only_the_refinement_and_s_omni_only_the_loop"),
    ("S-omni's refinement jittered", P, 'ref_exp = exp if side in ("ref", "all") else exp_u', "ref_exp = exp",
     "test_s_ref_jitters_only_the_refinement_and_s_omni_only_the_loop"),
    ("S path drops the refined weights (G4)", P, "            unf_in = s5e_trace.unf_inputs(loop_exp, feat_l, w_ref)\n",
     "            unf_in = s5e_trace.unf_inputs(loop_exp, feat_l, np.abs(s5n_pseudo.signed_sample(loop_exp)[1]))\n",
     "test_G4_s_all_is_a0_bitwise"),
    ("alignment unchecked", P, "            check_aligned(exp, exp_u, xt, xt_u)\n", "            pass\n",
     "test_an_s_arm_whose_second_build_differs_stops_with_rc5"),
    ("alignment skips the counts", P, 'ALIGNED = ("obs_counts", "tmpl_w",', 'ALIGNED = ("tmpl_w",',
     "test_misaligned_experiments_are_refused_and_aligned_ones_pass"),
    ("alignment skips the truth", P,
     "if (xt_j is None) != (xt_u is None) or (xt_j is not None and not np.array_equal(xt_j, xt_u)):", "if False:",
     "test_misaligned_experiments_are_refused_and_aligned_ones_pass"),
    ("max_bin not added", P, '            out = {**out, "max_bin": int(cfg["max_bin"])}\n', "            pass\n",
     "test_b_arm_max_bin_reaches_the_loop_and_the_refinement"),
    ("refinement max_bin unverified", P, 'if "max_bin" in cfg and ev.get("ran") and', 'if False and ev.get("ran") and',
     "test_a_refinement_without_max_bin_is_refused"),
    ("P not permuted", P, 'return o["unfold"](s5c_unfold.permute(inputs, cfg["permute"]), config, seed, threads, iters)',
     'return o["unfold"](inputs, config, seed, threads, iters)', "test_p_arm_is_a_permutation_of_the_float64_base"),
    ("trace drops the per-iteration functionals", P, '                item["fn_push"] = rec.out["fn_push"].tolist()\n',
     "                pass\n", "test_trace_sidecars"),
    ("booster hidden from the bound probe", P, '        return getattr(self.base, "booster_", None)\n',
     "        return None\n", "test_the_bound_probes_leaf_counts_read_through_the_wrapper"),
    # --- refusals (probe)
    ("namespace check skipped", P, "            why = check_namespace(ns, arm)\n", "            why = None\n",
     "test_undeclared_pair_wrong_truth_and_wrong_threads_are_refused_and_the_declared_run_is_not"),
    ("undeclared pair allowed", P, "    if any(p not in allowed for p in pairs):", "    if False:",
     "test_undeclared_pair_wrong_truth_and_wrong_threads_are_refused_and_the_declared_run_is_not"),
    ("threads unchecked", P, 'for key in ("iters", "threads", "estimator_seed"):', 'for key in ("iters", "estimator_seed"):',
     "test_undeclared_pair_wrong_truth_and_wrong_threads_are_refused_and_the_declared_run_is_not"),
    ("truth unchecked", P, 'if getattr(ns, "truth", None) != want["truth"] or', "if False and",
     "test_undeclared_pair_wrong_truth_and_wrong_threads_are_refused_and_the_declared_run_is_not"),
    ("write without the check", P, '        if not st["checked"]:\n', "        if False:\n",
     "test_a_write_without_the_namespace_check_is_refused"),
    ("names not restored", P, '        s5p_numerics.jittered, s5p_numerics.unfold_one = saved["jittered"], saved["unfold_one"]\n',
     "        pass\n", "test_names_are_restored_after_an_error"),
    ("traced arm without U", P, '    if cfg.get("trace") and U is None:', "    if False:", "test_a_traced_arm_without_u_is_refused"),
    # --- the queue and declared constants (probe)
    ("pairs as two tokens", P, """f"--pairs={','.join(g)}", "--tag\"""", """"--pairs", ",".join(g), "--tag\"""",
     "test_every_queue_line_passes_the_real_parsers_and_rs1s_check"),
    ("tasks of five", P, "CHUNK = 4\n", "CHUNK = 5\n", "test_the_declared_counts"),
    ("S-all dropped from the dry run", P, ' ("S_all", "-:1"),', "", "test_the_declared_counts"),
    ("ten seeds", P, "SEEDS = tuple(range(1, 21))", "SEEDS = tuple(range(1, 11))", "test_constants_match_the_declaration"),
    ("S-all at twenty seeds", P, '"pairs": j[:3]}', '"pairs": j}', "test_constants_match_the_declaration"),
    # --- gates (analysis)
    ("no receipt graded", A, "    why = receipt_problem(a.runs)\n", "    why = None\n", "test_no_receipt_grades_nothing"),
    ("FAILED beside the receipt ignored", A, 'for bad in ("STOP", "FAILED"):', 'for bad in ("STOP",):',
     "test_no_receipt_grades_nothing"),
    ("G1 ignored", A, "    if not all(g1.values()):\n", "    if False:\n", "test_g1_failure_reads_nothing"),
    ("G1 references unpinned", A, "if name not in pinned or sha256_path(p) != pinned[name]:", "if name not in pinned:",
     "test_a_reference_that_is_not_fdstabs_pinned_product_is_refused"),
    ("G4 ignored", A, 'both(ratio["S_ref"], k5_rule) if g4 else', 'both(ratio["S_ref"], k5_rule) if True else',
     "test_g4_failure_leaves_k5_unread"),
    ("G2 / exclusion never invalidates", A, '"invalid": frac > EXCLUDE_MAX,', '"invalid": False,',
     "test_zero_spread_functionals_are_excluded_and_too_many_invalidate"),
    # --- readings (analysis)
    ("C band moved", A, '("C" if m >= C_MIN else "P")', '("C" if m >= 0.4 else "P")', "test_bands_read_in_each_direction"),
    ("R band moved", A, 'return "R" if m <= R_MAX else', 'return "R" if m <= 0.04 else', "test_bands_read_in_each_direction"),
    ("DEFINITE from the point alone", A, "(b_lo if b_lo == b_hi else", "(band(point) if True else",
     "test_an_interval_across_a_band_edge_is_inconclusive"),
    ("unpaired bootstrap", A, "        sba = rel_sd(Fa[i])[ok]\n", "        sba = rel_sd(Fa[rng.integers(0, n, n)])[ok]\n",
     "test_a_paired_identical_arm_reads_exactly_one"),
    ("sets need not agree", A, 'return vals.pop() if len(vals) == 1 else "INCONCLUSIVE"', "return sorted(vals)[0]",
     "test_rules"),
    ("K1 inverted", A, '{"R": "SUPPORTED", "P": "PARTIAL", "C": "NOT SUPPORTED"}', '{"R": "NOT SUPPORTED", "P": "PARTIAL", "C": "SUPPORTED"}',
     "test_rules"),
    ("K2 without its upper end", A, 'if r["M"] <= K2_POINT and hi <= K2_UPPER:', 'if r["M"] <= K2_POINT:', "test_rules"),
    ("K3 bitwise ignored", A, '    if bitwise_equal:\n        return "NOT SUPPORTED"', '    if False:\n        return "NOT SUPPORTED"',
     "test_rules"),
    ("K4 threshold strict", A, '"SUPPORTED" if v >= K4_SUPPORTED else', '"SUPPORTED" if v > K4_SUPPORTED else', "test_rules"),
    ("K5 inverted", A, '{"C": "SUPPORTED", "P": "PARTIAL", "R": "NOT SUPPORTED"}', '{"C": "NOT SUPPORTED", "P": "PARTIAL", "R": "SUPPORTED"}',
     "test_rules"),
    ("D over all functionals", A, "    ok = (s0 > 0) & (Fref != 0)\n", "    ok = Fref != 0\n", "test_base_difference"),
    ("bands retyped", A, "R_MAX, C_MIN = 0.10, 0.70", "R_MAX, C_MIN = 0.10, 0.60", "test_constants_match_the_declaration"),
    # --- product refusals (analysis)
    ("seed set unchecked", A, "    if set(out) != declared:\n", "    if False:\n", "test_product_refusals"),
    ("stability input unchecked", A, "        if want != (", "        if False and want != (", "test_product_refusals"),
    ("arm unchecked", A, 'if rm.get("schema") != rmp.SCHEMA or rm.get("arm") != arm:', 'if rm.get("schema") != rmp.SCHEMA:',
     "test_product_refusals"),
    # --- R0 (analysis)
    ("R0 cell order unchecked", A, 'if list(i0["cells"]) != cells or dp_cells != cells', 'if dp_cells != cells',
     "test_each_control_refuses"),
    ("R0 C_e identity unchecked", A, "    if not np.allclose(ce_dp, ce_s1, rtol=1e-12, atol=0):\n", "    if False:\n",
     "test_each_control_refuses"),
    ("R0 printed control unchecked", A, "    if got != I0_PRINTED:\n", "    if False:\n", "test_each_control_refuses"),
    ("R0 sigma_J read as relative", A, "    rel_j = sj / f\n", "    rel_j = sj\n",
     "test_r0_reads_with_its_controls_and_an_undefined_cell"),
    ("R0b defined everywhere", A, "    defined = stat > rel_j\n", "    defined = stat > 0\n",
     "test_r0_reads_with_its_controls_and_an_undefined_cell"),
    # --- the job script
    ("pin unchecked", S, 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', "if false; then",
     "test_a_dirty_deploy_is_refused"),
    ("existing log reused", S, '[ ! -e "$L" ] || {', "true || {", "test_an_existing_log_and_a_wrong_pin_are_refused"),
    ("full without a dry receipt", S, '[ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/FAILED" ] ||', "true ||",
     "test_full_refuses_without_a_dry_receipt"),
    ("a failed task still writes DONE", S, '[ "$rc" -eq 0 ] || {', "true || {", "test_a_failed_task_leaves_no_receipt"),
    ("dry tasks re-run in the full run", S, '[ -e "$L/$id.end" ] && exit 0', "false && exit 0",
     "test_dry_then_full_skips_the_dry_tasks_and_writes_done"),
    ("environment unchecked", S, '|| { echo "[rs1] refusing: the environment lacks lightgbm/scipy" >&2; exit 7; }', "|| true",
     "test_an_environment_without_lightgbm_is_refused"),
]


def run_suite(first: Path | None, script: Path | None = None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("RS1_SBATCH", None)
    if script is not None:
        env["RS1_SBATCH"] = str(script)
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
