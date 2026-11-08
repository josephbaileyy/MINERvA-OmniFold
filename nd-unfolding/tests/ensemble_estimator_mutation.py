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
EXPECTED_TESTS = 76  # a script-mode run that stops early exits 0 with fewer: refuse it

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
    # "grid edges moved" (the bound design's exact-edge line) is retired under addendum A1: the edge zone contains it
    # (d = 0 and round32(e) are inside one spacing), so the line was removed and its mutant would be equivalent. The
    # zone's own mutants below (removed, 1/2 and 2 spacings, strict, the edge's spacing, the wrong edge sets) cover it.
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
    # --- the audit's ENS1-C1 sites (coverage-5b-audit, #899 comment 6712373597), its anchors verbatim
    ("X01 E2 across-k loop dropped", A, "    for s in seeds:\n        if len({digests[(s, k)] for k in range(1, N + 1)}) != N:", "    for s in ():\n        if len({digests[(s, k)] for k in range(1, N + 1)}) != N:", "test_e2_across_k"),
    ("X02 E1 jitter_seed unchecked", A, ' or m.get("jitter_seed") != s:', ":", "test_each_e1_sub_check_stops_the_read"),
    ("X03 E1 protocol_seed unchecked", A, 'eep.SCHEMA, "stability", k, eep.INTERNAL_BASE + k, s)', 'eep.SCHEMA, "stability", k, eep.INTERNAL_BASE + k, e.get("protocol_seed"))', "test_each_e1_sub_check_stops_the_read"),
    ("X04 E1 stability coords unchecked", A, '            if m.get("coords") != "float64":', '            if False:', "test_each_e1_sub_check_stops_the_read"),
    ("X05 E1 bootstrap unchecked", A, 'if m.get("bootstrap_seed") is not None:', "if False:", "test_each_e1_sub_check_stops_the_read"),
    ("X06 E1 input digests unchecked", A, 'if (m.get("input_npz_sha256"), m.get("bkg_dump_sha256")) != (st["npz_sha256"], st["bkg_sha256"]):', "if False:", "test_each_e1_sub_check_stops_the_read"),
    ("X07 E1 control path unchecked", A, 'if (m.get("stability_probe") or {}).get("candidate") != "control":', "if False:", "test_each_e1_sub_check_stops_the_read"),
    ("X08 E1 construction/truth/pseudo unchecked", A, '"pseudo", st["truth"], st["ratio_sha256"], st["pseudo_seed"]):', '"pseudo", st["truth"], st["ratio_sha256"], st["pseudo_seed"]) and False:', "test_each_e1_sub_check_stops_the_read"),
    ("X09 E3 F64 identity unchecked", A, 'if e.get("mode") != "base" or e.get("k") is not None or e.get("code_sha256") != code["ens1"]:', "if False:", "test_e3_f64_identity_meta_and_control_meta"),
    ("X10 E3 F64 meta unchecked", A, '    check_stability_meta(m, p.name)\n    if e.get("mode")', '    if e.get("mode")', "test_e3_f64_identity_meta_and_control_meta"),
    ("X11 E3 control-jitter meta unchecked", A, "        check_stability_meta(m, n)\n", "", "test_e3_f64_identity_meta_and_control_meta"),
    ("X12 usable count unchecked", A, "if int(ok.sum()) != esa.N_FUNCTIONALS:", "if False:", "test_every_functional_must_be_usable"),
    ("X13 stage2 product identity unchecked", A, 'if (e.get("mode"), e.get("truth"), e.get("k")) != ("closure", t, k):', "if False:", "test_the_stops"),
    ("X14 stage2 alternative digest unchecked", A, 'for key in ("hypothesis", "alternative"):', 'for key in ("hypothesis",):', "test_the_stops"),
    ("X15 G0 against E96(x) not F64(x)", A, "rel_F = Fj[:, :nf][:, ok0] / f64[:nf][ok0] - 1.0", "rel_F = Fj[:, :nf][:, ok0] / E[0, :nf][ok0] - 1.0", "test_g0_reads_against_f64_not_against_e96"),
    ("X16 stage1 no averaging (one fit)", A, "E = F.mean(axis=1)", "E = F[:, 0]", "test_the_mean_of_96_not_one_fit_is_read"),
    ("X17 stage2 no averaging (one fit)", A, "b_E = np.mean(xs, axis=0) / (M16 @ xt0) - 1.0", "b_E = xs[0] / (M16 @ xt0) - 1.0", "test_the_mean_of_96_closure_fits_not_one_is_read"),
    ("X18 receipt rc unchecked", A, 'if d.get("rc") != 0 or ', "if ", "test_each_receipt_field_is_checked"),
    ("X19 receipt tasks!=ended unchecked", A, ' or d.get("tasks") != d.get("ended")', "", "test_each_receipt_field_is_checked"),
    ("X20 receipt stage unchecked", A, ' or d.get("stage") != stage:', ":", "test_each_receipt_field_is_checked"),
    ("Y01 ratio sha unchecked", P, 'if ratio is None or rmp.sha256_path(Path(ratio)) != want["ratio_sha256"]:', "if False:", "test_each_stability_namespace_check_refuses"),
    ("Y02 stability expect digests unchecked", P, '    if getattr(ns, "expect_npz_sha256", None) != want["npz_sha256"] or \\\n            getattr(ns, "expect_bkg_sha256", None) != want["bkg_sha256"]:', "    if False:", "test_each_stability_namespace_check_refuses"),
    ("Y03 stability iters unchecked", P, '    for key in ("iters", "threads", "estimator_seed"):\n        if getattr(ns, key, None) != want[key]:', '    for key in ("threads", "estimator_seed"):\n        if getattr(ns, key, None) != want[key]:', "test_each_stability_namespace_check_refuses"),
    ("Y04 stability estimator_seed unchecked", P, '    for key in ("iters", "threads", "estimator_seed"):\n        if getattr(ns, key, None) != want[key]:', '    for key in ("iters", "threads"):\n        if getattr(ns, key, None) != want[key]:', "test_each_stability_namespace_check_refuses"),
    ("Y05 fixed-split/pseudo-seeds unchecked", P, 'if getattr(ns, "fixed_split_seed", None) is not None or getattr(ns, "pseudo_seeds", None) is not None:', "if False:", "test_each_stability_namespace_check_refuses"),
    ("Y06 closure namespace never enforced", P, "            why = check_closure_namespace(ns, truth)", "            why = None", "test_the_install_enforces_the_closure_namespace"),
    ("Y07 closure expect digests unchecked", P, '    if getattr(ns, "expect_npz_sha256", None) != STABILITY["npz_sha256"] or \\\n            getattr(ns, "expect_bkg_sha256", None) != STABILITY["bkg_sha256"]:', "    if False:", "test_each_closure_namespace_check_refuses"),
    ("Y08 closure iters/threads/seed unchecked", P, '    for key in ("iters", "threads", "estimator_seed"):\n        if getattr(ns, key, None) != STABILITY[key]:', '    for key in ():\n        if getattr(ns, key, None) != STABILITY[key]:', "test_each_closure_namespace_check_refuses"),
    ("Y09 closure split unchecked", P, ' or \\\n            getattr(ns, "pseudo_seeds", None) != f"{esp.CLOSURE_SEED}:{esp.CLOSURE_SEED}":', ":", "test_each_closure_namespace_check_refuses"),
    ("Y10 runner rc swallowed", P, "        if rc:\n            return rc\n    return 0", "        pass\n    return 0", "test_run_returns_the_first_non_zero_rc_and_stops"),
    ("Y11 closure tag without k", P, 'tag, out = f"ens1_{truth}_k{k:03d}", runs / "closure" / truth', 'tag, out = f"ens1_{truth}", runs / "closure" / truth', "test_every_closure_tag_carries_k"),
    ("Z01 ended-count check dropped", S, '[ "$n_end" -eq "$n_q" ] ||', "true ||", "test_a_task_without_its_end_record_leaves_no_receipt"),
    # --- A1's guard sites ported to ENS1's job script (audit #902 W04, W06, W09)
    ("W04 empty expect list read as all present", S, '[ "${#files[@]}" -gt 0 ] || all=0', "true", "test_a_task_whose_expect_fails_is_a_failure_not_a_teardown"),
    ("W06 xargs rc ignored", S, '[ -z "$failed" ] && [ "$rc" -eq 0 ] ||', '[ -z "$failed" ] ||', "test_xargs_rc_alone_stops_the_run"),
    ("W09 mv failure ignored", S, 'mv "$f" "$T/" || { echo "could not move $f aside" > "$L/$id.failed"; exit 1; }', 'mv "$f" "$T/" || true', "test_a_failed_move_aside_is_a_failure_and_the_crashed_products_are_not_used"),
    # --- ENS1 addendum A1: the edge zone (the director's terms: zone boundary, off by one spacing, the wrong edge set)
    ("REQ A1 zone removed", P, "        step[in_edge_zone(r32, edges)] = 0.0\n", "        pass\n", "test_the_bound_guard_passes_every_internal_seed"),
    ("REQ A1 zone half a spacing", P, "        zone[:, a] = d <= ulp[:, a]", "        zone[:, a] = d <= 0.5 * ulp[:, a]", "test_the_zone_is_one_spacing_inclusive_and_no_wider"),
    ("REQ A1 zone two spacings", P, "        zone[:, a] = d <= ulp[:, a]", "        zone[:, a] = d <= 2 * ulp[:, a]", "test_the_zone_is_one_spacing_inclusive_and_no_wider"),
    ("REQ A1 zone boundary strict", P, "        zone[:, a] = d <= ulp[:, a]", "        zone[:, a] = d < ulp[:, a]", "test_the_zone_is_one_spacing_inclusive_and_no_wider"),
    ("REQ A1 axis 0's edges for every axis", P, "    for a, e in enumerate(edges):\n        e = np.asarray(e, float)\n        j = np.clip", "    for a, e in enumerate([edges[0]] * len(edges)):\n        e = np.asarray(e, float)\n        j = np.clip", "test_the_zone_uses_each_axis_own_edges"),
    ("REQ A1 float32-rounded edges", P, "        e = np.asarray(e, float)\n        j = np.clip", "        e = np.asarray(e, np.float32).astype(float)\n        j = np.clip", "test_the_zone_compares_the_float64_edges_not_their_float32_rounding"),
    ("REQ A1 the edge's spacing, not the value's", P, "        zone[:, a] = d <= ulp[:, a]", "        near = np.where(np.abs(r64[:, a] - e[j - 1]) <= np.abs(e[j] - r64[:, a]), e[j - 1], e[j])\n        zone[:, a] = d <= np.spacing(np.abs(near.astype(np.float32))).astype(np.float64)", "test_the_zone_uses_the_values_own_spacing_on_the_narrow_side_of_a_binade"),
    ("A1 E5 moved-rows gate removed", A, '            if e.get("moved_rows") != {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}:\n                raise Stop(f"E5: {p.name} records moved rows {e.get(\'moved_rows\')} (A1', '            if False:\n                raise Stop(f"E5: {p.name} records moved rows {e.get(\'moved_rows\')} (A1', "test_every_product_must_record_zero_moved_rows"),
    ("A1 moved rows not recorded", P, '"moved_rows": item.get("moved_rows"),', '"moved_rows": None,', "test_every_product_records_zero_moved_rows"),
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
    from concurrent.futures import ThreadPoolExecutor

    def one(m):
        label, fname, old, new, test = m
        src = (ND / fname).read_text()
        if src.count(old) != 1:
            return f"MUTATION NOT APPLIED  {label}: anchor occurs {src.count(old)} times", False
        with tempfile.TemporaryDirectory() as d:
            for f in (P, A, S):
                shutil.copy(ND / f, Path(d) / f)
            (Path(d) / fname).write_text(src.replace(old, new))
            rc, out = run_suite(Path(d), Path(d) / S if fname == S else None)
        fails = failing(out)
        killed = test in fails
        return (f"{'KILLED' if killed else 'SURVIVED':8s}  {label:42s} by {test}"
                + ("" if killed else f"  (failing: {sorted(fails)})")), killed
    ok = True
    with ThreadPoolExecutor(int(os.environ.get("ENS1_MUTATION_WORKERS", "6"))) as ex:
        for text, killed in ex.map(one, MUTATIONS):   # results in MUTATIONS order
            ok &= killed
            print(text, flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
