#!/usr/bin/env python3
"""Mutation check of RSN's tests (RSN-DECLARATION.md §8).

Each mutation plants one declared defect in a copy of one RSN file and must make the NAMED test fail, not merely some
test. The copy runs in a temporary tree that mirrors the repository: rsn/ holds real copies of the RSN files (the
mutated one among them), and every other entry is a symlink to the real file, so the pins and imports resolve as in
the checkout (tier3/t3p_mutation.py's harness). Exit 0 only if the unmutated suite passes with the expected test count
and every mutation is killed by its named test.

    python3 -B nd-unfolding/rsn/rsn_mutation.py [--only LABEL_SUBSTRING] [--jobs N]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("rsn_prep.py", "rsn_unfold.py", "rsn_cmodel.py", "rsn_regrade.py", "rsn_read.py", "sbatch_rsn.sh",
         "rsn_tasks.tsv", "test_rsn.py")
PR, UF, CM, RG, RD, SB = FILES[:6]
EXPECTED_TESTS = 50
MUTATIONS = [
    # --- prep: the smoothing, G6, the step share, the manipulation check and the controls
    ("box radius one short", PR, "hi = np.minimum(np.arange(n) + radius + 1, n)", "hi = np.minimum(np.arange(n) + radius, n)",
     "test_box_sum_matches_a_brute_force_box"),
    ("smoothing averages over off cells", PR, "w = np.where(region, p, 0.0)", "w = p",
     "test_smoothing_is_the_weighted_box_mean_renormalized"),
    ("smoothing not renormalized", PR, "    return L.normalize(raw, assigned, p)\n", "    return raw, 1.0\n",
     "test_smoothing_a_constant_reweight_gives_one"),
    ("G6 cut at 10 GeV/c", PR, "G6_PZ = 6.0", "G6_PZ = 10.0",
     "test_g6_is_off_above_6_and_the_frozen_rho_rescaled_below"),
    ("G6 keeps the labels above 6", PR, 'lab[pz_hi > G6_PZ] = "off"', "lab[pz_hi > G6_PZ] = lab[pz_hi > G6_PZ]",
     "test_g6_is_off_above_6_and_the_frozen_rho_rescaled_below"),
    ("step threshold doubled", PR, "big = np.abs(a[tuple(lo)] - a[tuple(hi)]) > L.STEP",
     "big = np.abs(a[tuple(lo)] - a[tuple(hi)]) > 2 * L.STEP", "test_a_step_marks_both_neighbours_and_a_small_one_marks_none"),
    ("step marks one side", PR, "        near[tuple(hi)] |= big\n", "        near[tuple(hi)] |= False\n",
     "test_a_step_marks_both_neighbours_and_a_small_one_marks_none"),
    ("manipulation check: median rule only", PR,
     "ok = med <= MEDIAN_FRACTION * med0 and not_raised >= MIN_CELLS_NOT_RAISED", "ok = med <= MEDIAN_FRACTION * med0",
     "test_the_manipulation_check_boundaries"),
    ("manipulation check: 11 cells", PR, "MIN_CELLS_NOT_RAISED = 12", "MIN_CELLS_NOT_RAISED = 11",
     "test_the_manipulation_check_boundaries"),
    ("manipulation check: 0.6 of the median", PR, "MEDIAN_FRACTION = 0.5", "MEDIAN_FRACTION = 0.6",
     "test_the_manipulation_check_boundaries"),
    ("no radius 2", PR, "    for rad in RADII:\n", "    for rad in RADII[:1]:\n", "test_the_radius_ladder"),
    ("describe control skipped", PR, "if got.shape != want.shape or not np.allclose(got, want, rtol=TOL, atol=1e-15):",
     "if False:", "test_the_prep_refuses_on_each_control"),
    ("domain k control skipped", PR, 'if abs(k6 - float(domain["k"]["ii"])) > TOL * k6:', "if False:",
     "test_the_prep_refuses_on_each_control"),
    ("domain departure control skipped", PR,
     'if not np.allclose(d6, np.asarray(domain["departure"]["ii"], float), rtol=0, atol=TOL):', "if False:",
     "test_the_prep_refuses_on_each_control"),
    ("frozen reweight control skipped", PR,
     'if not np.allclose(r, f["r"], rtol=TOL, atol=0) or abs(k - f["k"]) > TOL * f["k"]:', "if False:",
     "test_a_frozen_reweight_that_normalize_does_not_reproduce_refuses"),
    # --- the instrumented regressor, the declared truths and the transfer diagnostic
    ("regressor weight w_reco", UF, 'w = np.asarray(d["w_truth"], float)[m][pr]', 'w = np.asarray(d["w_reco"], float)[m][pr]',
     "test_the_regressor_is_fitted_on_w_push_times_w_truth_of_the_reco_passing_truth_rows"),
    ("regressor rows not reco-filtered", UF, 'w = np.asarray(d["w_truth"], float)[m][pr]', 'w = np.asarray(d["w_truth"], float)[m]',
     "test_the_regressor_is_fitted_on_w_push_times_w_truth_of_the_reco_passing_truth_rows"),
    ("push not tracked", UF, 'if clf is st["clf2"]:', "if False:",
     "test_the_regressor_is_fitted_on_w_push_times_w_truth_of_the_reco_passing_truth_rows"),
    ("weight without push", UF, 'sw = wt * np.asarray(st["push"], float)[pr] if weighted else None',
     "sw = wt if weighted else None", "test_the_regressor_is_fitted_on_w_push_times_w_truth_of_the_reco_passing_truth_rows"),
    ("sample_weight not passed", UF, "return inner(X, y, sample_weight=sw)", "return inner(X, y)",
     "test_unit_weights_and_no_push_reproduce_nothing_but_the_weighting_changes_the_loop"),
    ("fit count unchecked", UF, "if calls != [wt.size] * int(iters):", "if False:",
     "test_the_wrapper_refuses_extra_arguments_wrong_rows_missing_fits_and_bad_weights"),
    ("factory not restored", UF, "            onc.make_estimators, onc._reweight = true_make, true_rw\n",
     "            onc._reweight = true_rw\n", "test_the_wrapper_refuses_extra_arguments_wrong_rows_missing_fits_and_bad_weights"),
    ("extra fit arguments accepted", UF, "if args or kw:", "if False:",
     "test_the_wrapper_refuses_extra_arguments_wrong_rows_missing_fits_and_bad_weights"),
    ("non-positive weights accepted", UF, "if w.size == 0 or not np.all(np.isfinite(w)) or np.any(w <= 0):",
     "if w.size == 0:", "test_the_wrapper_refuses_extra_arguments_wrong_rows_missing_fits_and_bad_weights"),
    ("main never weights", UF, 'instrument(orig[0], evidence, a.regressor_weight == "w_push_w_truth", a.transfer)',
     "instrument(orig[0], evidence, False, a.transfer)", "test_main_records_the_options_and_restores_every_patch"),
    ("load_inputs not restored", UF, "PU.unfold, s5n_pseudo.write_product, L.row_weight, s5c_unfold.load_inputs = orig\n",
     "PU.unfold, s5n_pseudo.write_product, L.row_weight = orig[:3]\n", "test_a_declared_truth_replaces_the_identity_reweight"),
    ("write without the regressor", UF,
     'if (a.regressor_weight != "none" or a.transfer) and evidence.get("fit_calls") is None:', "if False:",
     "test_an_instrumented_step_refuses_to_write_when_the_regressor_never_ran"),
    ("transfer probe on every row", UF, "probe.fit(X_[~mk], y_[~mk])\n", "probe.fit(X_, y_)\n",
     "test_the_transfer_diagnostic_leaves_the_loop_untouched_and_records_every_iteration"),
    ("transfer probe unweighted in a weighted step", UF, "probe.fit(X_[~mk], y_[~mk], sample_weight=sw[~mk])",
     "probe.fit(X_[~mk], y_[~mk])", "test_the_transfer_diagnostic_leaves_the_loop_untouched_and_records_every_iteration"),
    ("one mask for every iteration", UF, "np.random.default_rng([TRANSFER_SEED, k])", "np.random.default_rng(TRANSFER_SEED)",
     "test_the_transfer_diagnostic_leaves_the_loop_untouched_and_records_every_iteration"),
    ("transfer fraction 0.3", UF, "TRANSFER_SEED, TRANSFER_FRACTION = 20261111, 0.2", "TRANSFER_SEED, TRANSFER_FRACTION = 20261111, 0.3",
     "test_the_transfer_diagnostic_leaves_the_loop_untouched_and_records_every_iteration"),
    ("cell bias not relative", UF, 'cb.append(float((w[s] * pred[s]).sum() / den - 1.0) if den > 0 else None)',
     'cb.append(float((w[s] * pred[s]).sum() / den) if den > 0 else None)', "test_the_transfer_summary"),
    ("q3 amplitude 0.2", UF, "Q3_AMPLITUDE = 0.3", "Q3_AMPLITUDE = 0.2", "test_a_declared_truth_replaces_the_identity_reweight"),
    ("A7 hypothesis pin unchecked", UF, "if L.sha256_path(A7_HYPOTHESIS) != A7_HYPOTHESIS_SHA256:", "if False:",
     "test_a_declared_truth_refuses_off_a_closure_a_non_identity_ratio_and_a_changed_hypothesis"),
    ("a truth off a closure accepted", UF, 'if a.truth != "ratio" and "--closure" not in rest:', "if False:",
     "test_a_declared_truth_refuses_off_a_closure_a_non_identity_ratio_and_a_changed_hypothesis"),
    ("a non-identity ratio replaced", UF, 'if not ratio.get("identity") or not np.all(r == 1.0):', "if False:",
     "test_a_declared_truth_refuses_off_a_closure_a_non_identity_ratio_and_a_changed_hypothesis"),
    # --- C_model variants
    ("G6 replaces NuWro's row", CM, 'np.vstack([S0[0], S0[1], P.rel_shift(X("G6_gibuu"), X0)])',
     'np.vstack([S0[0], P.rel_shift(X("G6_gibuu"), X0), S0[2]])', "test_the_arms_are_built_from_the_declared_rows"),
    ("WR closure against X0", CM, "b_w = P.rel_shift(X(task), B5.integrals(got[task][1], rmap, n))",
     "b_w = P.rel_shift(X(task), X0)", "test_the_arms_are_built_from_the_declared_rows"),
    ("SM never built", CM, 'sm_built = any(k.startswith("./SM/") for k in rsn_sums)', "sm_built = False",
     "test_the_arms_are_built_from_the_declared_rows"),
    ("NC skipped", CM, "    rec, _ = B5.nominal_control(x_nc, p5, rmap, n)\n", "    rec = {}\n",
     "test_the_nc_and_nc_s_refuse"),
    ("NC-S skipped", CM, 'if not np.array_equal(S0, np.asarray(committed["S"], float)):', "if False:",
     "test_the_nc_and_nc_s_refuse"),
    ("equal-weight reference is the weighted closure", CM, '"gibuu": ("WR_closure_gibuu", "rsn:WU_closure_gibuu")',
     '"gibuu": ("WR_closure_gibuu", "rsn:WR_closure_gibuu")', "test_the_arms_are_built_from_the_declared_rows"),
    ("TR_data control skipped", CM, 'if not np.array_equal(got["TR_data"][0], got["rsn_nc"][0]):', "if False:",
     "test_a_transfer_step_that_moved_the_loop_refuses"),
    ("transfer records unchecked", CM, 'if spec["transfer"] and len(rsn.get("transfer_records") or []) != ITERS:', "if False:",
     "test_each_wrong_meta_field_refuses"),
    ("truth unchecked in meta", CM, 'for k in ("regressor_weight", "truth", "transfer"):', 'for k in ("regressor_weight", "transfer"):',
     "test_each_wrong_meta_field_refuses"),
    ("ratio sha unchecked", CM, '"ratio_sha256": want_ratio, ', "", "test_each_wrong_meta_field_refuses"),
    ("fit count in meta unchecked", CM, 'if rsn.get("fit_calls") != want_calls:', "if False:",
     "test_each_wrong_meta_field_refuses"),
    ("closure refinement unchecked", CM, 'if refine.get("ran") is not False:', "if False:",
     "test_each_wrong_meta_field_refuses"),
    # --- the regrade
    ("own vertex not left out", RG,
     'C = (mats["C_total"] if t["own"] is None else mats[f"minus_{t[\'own\']}"]) + Cx_rel', 'C = mats["C_total"] + Cx_rel',
     "test_each_grade_uses_the_arm_s_rows_with_the_own_vertex_left_out"),
    ("model-only on C_e", RG, 'R.grade(b, N, R.leave_out(Cstat_rel, S, t["own"]))', 'R.grade(b, N, R.leave_out(Ce_rel, S, t["own"]))',
     "test_each_grade_uses_the_arm_s_rows_with_the_own_vertex_left_out"),
    ("row-6 offset not subtracted", RG, 'est[t["name"]] = (bw - o["O"], Nw + o["N_O"], Beff, "offset-corrected", bw)',
     'est[t["name"]] = (bw, Nw + o["N_O"], Beff, "offset-corrected", bw)', "test_the_estimates_are_fd_f0_regrade_s"),
    ("NC-R bias unchecked", RG, 'if not np.allclose(rec["bias"], o["bias"], rtol=1e-12, atol=1e-15):', "if False:",
     "test_nc_r_reproduces_and_refuses_on_any_differing_field"),
    ("NC-R grades unchecked", RG, "def same_grade(a: dict, b: dict) -> bool:\n    return (",
     "def same_grade(a: dict, b: dict) -> bool:\n    return True or (", "test_nc_r_reproduces_and_refuses_on_any_differing_field"),
    ("NC-R groups unchecked", RG,
     'if any(mine.get(k) != g[k] for k in ("truths", "cells", "cells_abs_z_gt_2", "truths_p_lt_0.01")):', "if False:",
     "test_nc_r_reproduces_and_refuses_on_any_differing_field"),
    ("NC-R control 7 unchecked", RG, 'if offset_pass != bool(readout["controls"]["offset_control_7"]["pass"]):', "if False:",
     "test_nc_r_reproduces_and_refuses_on_any_differing_field"),
    ("NC-R order unchecked", RG, 'if [r["name"] for r in nom["records"]] != [r["name"] for r in readout["truths"]]:',
     "if False:", "test_nc_r_reproduces_and_refuses_on_any_differing_field"),
    ("C-INV skipped", RG, 'if a["own_vertex"] == "gibuu" and a["grade"] != b["grade"]:', "if False:",
     "test_c_inv_holds_for_a_gibuu_only_change_and_catches_any_other"),
    ("nominal S unchecked", RG, 'if "nominal" not in arms or not np.array_equal(arms["nominal"], S0):',
     'if "nominal" not in arms:', "test_the_regrade_runs_end_to_end_and_refuses_a_wrong_pin_or_nominal_s"),
    ("WR matrix without the leave-out", RG, "        M = matrix(WR_OWN[t])\n", "        M = matrix(None)\n",
     "test_wr_directions_grade_each_vector_against_its_truth_s_matrix"),
    ("GiBUU closure graded with GiBUU's shift", RG,
     'WR_OWN = {"data": None, "tune_v1": None, "nuwro": "nuwro", "gibuu": "gibuu", "q3": None}',
     'WR_OWN = {"data": None, "tune_v1": None, "nuwro": "nuwro", "gibuu": None, "q3": None}',
     "test_wr_directions_grade_each_vector_against_its_truth_s_matrix"),
    ("components not whitened", RG, "comp = ((E.T @ v) / np.sqrt(lam))[order]", "comp = (E.T @ v)[order]",
     "test_wr_directions_grade_each_vector_against_its_truth_s_matrix"),
    ("along unnormalized", RG, "return float(yd @ yb / np.sqrt(yb @ yb))", "return float(yd @ yb)",
     "test_wr_directions_grade_each_vector_against_its_truth_s_matrix"),
    ("rsn_cmodel.json's S unchecked", RG, 'if not np.array_equal(np.asarray(cm["arms"]["nominal"]["S"], float), S0):',
     "if False:", "test_the_regrade_runs_end_to_end_and_refuses_a_wrong_pin_or_nominal_s"),
    # --- the readings
    ("q smaller below 0.79", RD, "Q_SMALLER, Q_LARGER, Q_CELL = 0.8, 1.25, (0.5, 2.0)",
     "Q_SMALLER, Q_LARGER, Q_CELL = 0.79, 1.25, (0.5, 2.0)", "test_the_sigma_classes_and_their_boundaries"),
    ("q cell bound 0.4", RD, "Q_SMALLER, Q_LARGER, Q_CELL = 0.8, 1.25, (0.5, 2.0)",
     "Q_SMALLER, Q_LARGER, Q_CELL = 0.8, 1.25, (0.4, 2.0)", "test_the_sigma_classes_and_their_boundaries"),
    ("floor multiple 3", RD, "FLOOR_MULT, HALF_SIGMA = 2.0, 0.5", "FLOOR_MULT, HALF_SIGMA = 3.0, 0.5",
     "test_the_wr_classes_and_their_boundaries"),
    ("half sigma 0.6", RD, "FLOOR_MULT, HALF_SIGMA = 2.0, 0.5", "FLOOR_MULT, HALF_SIGMA = 2.0, 0.6",
     "test_the_wr_classes_and_their_boundaries"),
    ("signed delta", RD, "d, fl, sg = (np.abs(np.asarray(x, float)) for x in (delta, floor, sigma))",
     "d, fl, sg = (np.asarray(x, float) for x in (delta, floor, sigma))", "test_the_wr_classes_and_their_boundaries"),
    ("rms lower bound 0.89", RD, "RMS_LOWER, RMS_HIGHER = 0.9, 1.1", "RMS_LOWER, RMS_HIGHER = 0.89, 1.1",
     "test_the_closure_classes"),
    ("held-out count unchecked", RD, 'return g["truths"] == 4 and g["cells_abs_z_gt_2"] == 0',
     'return g["cells_abs_z_gt_2"] == 0', "test_the_held_out_reading"),
    ("fewer and more swapped", RD, "    if b < a:\n", "    if b > a:\n", "test_the_listed_classes"),
    ("verdict ignores the held-out records", RD, 'if lc == "unchanged" and ho', 'if lc == "unchanged"',
     "test_the_readout_applies_the_tables"),
    ("floor closure bound 1e-3", RD, "FLOOR_CLOSURE_MAX = 1e-4", "FLOOR_CLOSURE_MAX = 1e-3",
     "test_the_readout_applies_the_tables"),
    ("rounding floor unchecked", RD, "if got != FLOOR_PRINTED:", "if False:",
     "test_the_rounding_floor_reproduces_the_printed_figures_and_refuses_otherwise"),
    ("nominal sigma unchecked", RD,
     'if not np.allclose(nom["reported_relative_sigma"], sigma_rep, rtol=1e-12, atol=0):', "if False:",
     "test_the_readout_refuses_a_nominal_that_is_not_the_committed_one"),
    ("nominal C_model unchecked", RD,
     'if not np.allclose(cm["arms"]["nominal"]["sqrt_diag"], cmodel["sqrt_diag"], rtol=1e-12, atol=0):', "if False:",
     "test_the_readout_refuses_a_nominal_that_is_not_the_committed_one"),
    ("chi2 fraction 0.3", RD, "CHI2_FRACTION = 0.25", "CHI2_FRACTION = 0.3", "test_the_deformed_truth_classes"),
    ("flag change ignored", RD, 'if flagged(w) != flagged(u) or abs(w["chi2"] - u["chi2"]) > CHI2_FRACTION * u["chi2"]:',
     'if abs(w["chi2"] - u["chi2"]) > CHI2_FRACTION * u["chi2"]:', "test_the_deformed_truth_classes"),
    ("transfer floor multiple 3", RD, "if np.all(t <= FLOOR_MULT * np.asarray(floor, float)):",
     "if np.all(t <= 3 * np.asarray(floor, float)):", "test_the_transfer_classes"),
    ("an empty cell passes the transfer", RD, "t = np.array([np.inf if v is None else abs(v) for v in cell_bias])",
     "t = np.array([0.0 if v is None else abs(v) for v in cell_bias])", "test_the_transfer_classes"),
    ("WR verdict ignores the data", RD, 'if not material and wc in ("W0", "W1") else', "if not material else",
     "test_the_readout_applies_the_tables"),
    ("transfer read at the first iteration", RD, 'last = cm["transfer"][pt][-1]', 'last = cm["transfer"][pt][0]',
     "test_the_readout_applies_the_tables"),
    # --- the launcher
    ("job name unchecked", SB, '[ "$NAME" = "rsn_$JOB" ] ||', "true ||", "test_the_deploy_name_and_limit_checks"),
    ("J1 limit 0:20", SB, "J1|J3) LIMIT=0:19:00 ;;", "J1|J3) LIMIT=0:20:00 ;;", "test_the_deploy_name_and_limit_checks"),
    ("J2 limit 0:23", SB, "J2|J2n) LIMIT=0:22:00 ;;", "J2|J2n) LIMIT=0:23:00 ;;", "test_the_deploy_name_and_limit_checks"),
    ("J3 runs without its gate", SB, 'if [ "$JOB" != J1 ]; then\n    G=', 'if [ "$JOB" = J2 ] || [ "$JOB" = J2n ]; then\n    G=',
     "test_j3_runs_the_four_f1_closures_after_the_nc"),
    ("transfer flag dropped", SB, '[ "$transfer" = yes ] && extra+=(--transfer)', ":",
     "test_j2_runs_the_eight_declared_steps"),
    ("truth dropped", SB, '--truth "$truth"', "--truth ratio", "test_j3_runs_the_four_f1_closures_after_the_nc"),
    ("untracked files ignored", SB,
     'stray=$(git -C "$D" status --porcelain --untracked-files=all -- nd-unfolding 2>/dev/null | wc -l)', "stray=0",
     "test_the_deploy_name_and_limit_checks"),
    ("no fence file accepted", SB, '[ -s "$OUT/fence.txt" ] ||', "true ||",
     "test_the_fence_fails_closed_and_matches_at_the_start_only"),
    ("fence matches anywhere", SB, "'index($1, p) == 1'", "'index($1, p) >= 1'",
     "test_the_fence_fails_closed_and_matches_at_the_start_only"),
    ("squeue failure ignored", SB, '|| { say "refusing: squeue failed"; exit 2; }', "|| true",
     "test_the_fence_fails_closed_and_matches_at_the_start_only"),
    ("J2 gate unchecked", SB, '[ -f "$G" ] && grep -qx "pin=$PIN" "$G" ||', "true ||",
     "test_j2_needs_its_gate_the_nc_pass_and_the_committed_reweights"),
    ("NC PASS unchecked", SB, "grep -q '\"verdict\": \"PASS\"' \"$OUT/nc.json\" 2>/dev/null ||", "true ||",
     "test_j2_needs_its_gate_the_nc_pass_and_the_committed_reweights"),
    ("J2 without the SM reweights", SB, 'if [ "$JOB" = J2 ] && [ "$n_sm" -ne 3 ]; then', "if false; then",
     "test_j2_needs_its_gate_the_nc_pass_and_the_committed_reweights"),
    ("reweight sha unchecked", SB, '[ -n "$SHA" ] && [ -f "$RF" ] && [ "$(sha256sum "$RF" | cut -d\' \' -f1)" = "$SHA" ]',
     '[ -n "$SHA" ] && [ -f "$RF" ]', "test_a_changed_reweight_or_an_existing_product_refuses"),
    ("existing product overwritten", SB, '[ ! -e "$OUT/products/$task.npz" ] ||', "true ||",
     "test_a_changed_reweight_or_an_existing_product_refuses"),
    ("every step unweighted", SB, '--regressor-weight "$weight"', "--regressor-weight none",
     "test_j2_runs_the_eight_declared_steps"),
    ("closure flag inverted", SB, 'extra=(); [ "$closure" = yes ] && extra=(--closure)',
     'extra=(); [ "$closure" = no ] && extra=(--closure)', "test_j2_runs_the_eight_declared_steps"),
    ("a WR step dropped from the task table", "rsn_tasks.tsv",
     "WR_closure_tune_v1\tJ2\tWR\tfrozen:tune_v1\tyes\tw_push_w_truth", "WR_closure_tune_v1\tJ9\tWR\tfrozen:tune_v1\tyes\tw_push_w_truth",
     "test_the_task_table"),
    ("a WU transfer dropped from the task table", "rsn_tasks.tsv", "WU_closure_q3\tJ3\tWU\tfrozen:tune_v1\tyes\tnone\tq3\tyes",
     "WU_closure_q3\tJ3\tWU\tfrozen:tune_v1\tyes\tnone\tq3\tno", "test_the_task_table"),
]


def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the RSN files. Returns its rsn/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "rsn":
            (nd / e.name).symlink_to(e)
    rs = nd / "rsn"
    rs.mkdir()
    for f in FILES:
        (rs / f).write_bytes((HERE / f).read_bytes())
    (rs / SB).chmod(0o755)
    return rs


def run_suite(rs: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/rsn/test_rsn.py"], cwd=rs.parents[1],
                       capture_output=True, text=True, timeout=3600)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1, help="mutants run at once (each in its own mirrored tree)")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_suite(mirror(Path(d)))
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-3000:])
        return 1
    print(f"unmutated suite: {ran.group(1)} tests OK, in the mirrored tree")
    todo = [m for m in MUTATIONS if not a.only or a.only in m[0]]
    ok, n = True, len(todo)

    def one(m):
        label, fname, old, new, test = m
        src = (HERE / fname).read_text()
        if src.count(old) != 1:
            return label, test, None, f"anchor occurs {src.count(old)} times"
        with tempfile.TemporaryDirectory() as d:
            rs = mirror(Path(d))
            (rs / fname).write_text(src.replace(old, new))
            _, out = run_suite(rs)
        return label, test, failing(out), ""

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for label, test, fails, why in ex.map(one, todo):
            if fails is None:
                print(f"MUTATION NOT APPLIED  {label}: {why}", flush=True)
                ok = False
                continue
            killed = test in fails
            ok &= killed
            print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:48s} by {test}"
                  + ("" if killed else f"  (failing: {sorted(fails)})"), flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({n} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
