"""Mutation check of FD-PRR's tests (FD-PRR-DECLARATION.md §8).

Each mutation plants one declared defect in a copy of one FD-PRR file and must make the NAMED test fail, not merely
some test. The copy runs in a temporary tree that mirrors the repository: prior_retention/ holds real copies of the
FD-PRR files (the mutated one among them), and every other entry is a symlink to the real file, so the digest pins and
the imports resolve as they do in the checkout. Exit 0 only if the unmutated suite passes with the expected test count
and every mutation is killed by its named test.

    python3 -B nd-unfolding/prior_retention/prr_mutation.py [--only LABEL_SUBSTRING] [--jobs N]
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("prr_probe.py", "prr_ibu.py", "prr_read.py", "sbatch_prr.sh", "test_prr.py")
PB, IB, RD, SB = FILES[:4]
EXPECTED_TESTS = 104
MUTATIONS = [
    # --- the probe: the mask, the guard, the pins, the columns
    ("mask columns swapped", PB, "return orig(MCgen[:, gi], MCreco[:, ri], measured[:, ri], *args, **kwargs)",
     "return orig(MCgen[:, ri], MCreco[:, gi], measured[:, gi], *args, **kwargs)",
     "test_each_mask_hands_the_loop_its_columns_and_the_histogram_all_five"),
    ("measured side unmasked", PB, "return orig(MCgen[:, gi], MCreco[:, ri], measured[:, ri], *args, **kwargs)",
     "return orig(MCgen[:, gi], MCreco[:, ri], measured, *args, **kwargs)",
     "test_each_mask_hands_the_loop_its_columns_and_the_histogram_all_five"),
    ("O4r drops W everywhere", PB, '"O4r": (AXES, NO_W),', '"O4r": (NO_W, NO_W),', "test_the_masks"),
    ("iters unchecked", PB, 'if getattr(ns, "iters", None) != L["iters"]:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("capacity unchecked", PB, 'if s5e_trace.parse_pair(getattr(ns, "capacity", None)) != L["capacity"]:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("undeclared seed admitted", PB, "if (level, truth, s) not in set(all_tasks()):", "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("hypothesis unchecked", PB, 'if str(getattr(ns, "hypothesis", "")) != hyp:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("write without the check", PB, '        if not state["checked"]:\n', "        if False:\n",
     "test_no_product_without_the_check_or_with_a_missed_mask"),
    ("mask call count ignored", PB, 'if L["mask"] is not None and rec.get("calls") != 1:', "if False:",
     "test_no_product_without_the_check_or_with_a_missed_mask"),
    ("pins unchecked", PB, "if not p.is_file() or sha256_path(p) != want:", "if not p.is_file():",
     "test_a_changed_module_is_refused"),
    ("C-COLS order skipped", PB, "    if names != AXES:\n", "    if False:\n", "test_the_input_columns_are_checked_not_assumed"),
    ("loop not restored", PB, "        onc.omnifold_loop = orig\n", "        pass\n",
     "test_the_loop_is_restored_and_a_wrong_shape_refused"),
    # --- the probe: jobs, price, gate, staging, C-PAIR
    ("the 0.9 rule relaxed", PB, "GATE_FRACTION = 0.9", "GATE_FRACTION = 1.0", "test_the_0_9_rule_is_exact"),
    ("full job on assumed rates", PB, 'if mode == "full" and p["unmeasured"]:', "if False:",
     "test_a_full_job_refuses_an_unmeasured_level"),
    ("pack without its tail", PB, "    return max(free) if free else 0.0\n", "    return sum(free) / len(free) if free else 0.0\n",
     "test_pack_is_list_scheduling_with_its_tail"),
    ("measured rates ignored", PB, "        if lv in rates:\n", "        if False:\n", "test_a_full_job_runs_on_measured_rates"),
    ("cap's (1000, 63) not split", PB, 'if seed != PRIMARY_SEED or (level == "C1000" and truth in CAP_TO_MISC):',
     "if seed != PRIMARY_SEED:", "test_each_limit_passes_the_gate_at_the_conservative_unit"),
    ("a limit lowered", PB, '"cap": 6.5,', '"cap": 6.25,', "test_each_limit_passes_the_gate_at_the_conservative_unit"),
    ("floor seed on a refused value", PB, "FLOOR_SEEDS = (994001,", "FLOOR_SEEDS = (991001,",
     "test_the_floor_seeds_are_no_campaigns"),
    ("C-PAIR not complete in the dry run", PB, '(level == "B0" and truth == FLOOR_TRUTH)', "False",
     "test_the_dry_run_measures_every_level_and_completes_c_pair"),
    ("queue not longest first", PB, "key=lambda x: (-units(x[0]), task_id(*x))", "key=lambda x: task_id(*x)",
     "test_the_queue_is_longest_first"),
    ("stage atime unchecked", PB, "        if moved:\n", "        if False:\n", "test_a_moved_atime_is_refused"),
    ("stage pin unchecked", PB, '        if got != e["sha256"]:\n', "        if False:\n",
     "test_a_wrong_pin_or_a_used_destination_is_refused"),
    ("C-PAIR within a tolerance", PB, '"pass": bool(a.dtype == b.dtype and np.array_equal(a, b)), "cells"',
     '"pass": bool(np.allclose(a, b)), "cells"', "test_one_ulp_fails_c_pair"),
    ("C-MASK ignores the dtype", PB, 'out["C-MASK"]["nominal"] = {"pass": bool(a.dtype == b.dtype and np.array_equal(a, b))}',
     'out["C-MASK"]["nominal"] = {"pass": bool(np.array_equal(a, b))}', "test_a_mask_that_moves_b0_fails_c_mask"),
    # --- route 2
    ("capture writes into B0's directory", IB, '    argv[argv.index("--out") + 1] = str(scratch)\n', "",
     "test_the_capture_is_the_runners_experiment_and_writes_nothing"),
    ("R-SUP without the truth reweight", IB, "    w = half.w_truth * r[half.rows]\n", "    w = half.w_truth\n", "test_r_sup"),
    ("overlapping cells admitted", IB, "    if np.any(nz.sum(axis=0) > 1):\n", "    if False:\n",
     "test_fine_to_cell_refuses_an_overlap"),
    ("C-IBU tolerance widened", IB, '"pass": bool(rel <= cibu["tol"])', '"pass": bool(rel <= 1e-6)',
     "test_c_ibu_passes_on_the_committed_value_and_fails_off_it"),
    ("R-ID on the sub unfold", IB, '    pb = next(x for x in rec if "R" in x)\n', '    pb = [x for x in rec if "R" in x][-1]\n',
     "test_r_id_reads_the_fold_problem"),
    # --- the reader: quantities
    ("rho's sign", RD, "return float(-np.sum(b[S] * d[S]) / np.sum(d[S] ** 2)), int(S.sum())",
     "return float(np.sum(b[S] * d[S]) / np.sum(d[S] ** 2)), int(S.sum())", "test_the_prior_retains_one_and_the_truth_zero"),
    ("no |d| threshold", RD, "    S = np.abs(d) >= D_MIN\n", "    S = np.abs(d) >= 0\n", "test_undefined_below_two_cells"),
    ("P from the primary split", RD, '        p = X[("B0", P.PRIOR, s)][1]\n        r_, n_s = rho(xh, x, p)',
     '        p = X[("B0", P.PRIOR, P.PRIMARY_SEED)][1]\n        r_, n_s = rho(xh, x, p)', "test_planted_classes"),
    ("floor SD with ddof 0", RD, "return float(np.std(np.asarray(deltas, float), ddof=1))",
     "return float(np.std(np.asarray(deltas, float), ddof=0))", "test_floor_needs_five_defined_splits"),
    ("T_Q retyped", RD, "T_Q = 9.02936702750999", "T_Q = 9.03", "test_t_quantile"),
    ("no bar floor", RD, "    return max(BAR_FLOOR, T_Q * s)\n", "    return T_Q * s\n", "test_bar"),
    ("strict bar", RD, "lo = any(v <= rho0 - delta for v in rhos)", "lo = any(v < rho0 - delta for v in rhos)",
     "test_factor_class_both_directions"),
    ("information limit without F2", RD,
     'if pr1["F1"] in ("no effect", "increases") and pr1["F2"] in ("no effect", "increases") and pr2b in ("flat", "rises"):',
     'if pr1["F1"] in ("no effect", "increases") and pr2b in ("flat", "rises"):', "test_labels"),
    ("PR-3 ignores new flags", RD, '"without_new_flags": bool(c and not new)', '"without_new_flags": bool(c)', "test_clears"),
    ("Table II flag by p only", RD, '"flagged": bool(g["p_lt_0.01"] or g["cells_abs_z_gt_2"])',
     '"flagged": bool(g["p_lt_0.01"])', "test_table_ii_flags_by_p_and_by_z"),
    ("PR-2b without its bar", RD, 'return "falls" if r200 <= r5 - BAR_FLOOR', 'return "falls" if r200 <= r5',
     "test_ibu_classes"),
    ("own vertex dropped", RD, '        out[t] = (mats["C_total"] if own[t] is None else mats[f"minus_{own[t]}"]) + Cxr\n',
     '        out[t] = mats["C_total"] + Cxr\n', "test_the_own_vertex_is_f0s"),
    ("C-CT tolerance dropped", RD, 'ct["pass"] = bool(ct["f_same_in_block"] and all(ct[f"sigma_{k}"] <= CT_TOL for k in mats)',
     'ct["pass"] = bool(ct["f_same_in_block"] or all(ct[f"sigma_{k}"] <= CT_TOL for k in mats)', "test_a_moved_vertex_fails_c_ct"),
    # --- the reader: completeness and controls
    ("ended count unchecked", RD, '            if d.get("tasks") != n or d.get("ended") != n:\n', "            if False:\n",
     "test_incomplete_runs_read_nothing"),
    ("route 2 not required", RD, '    for job in (*P.JOBS, "ibu"):\n', "    for job in P.JOBS:\n", "test_incomplete_runs_read_nothing"),
    ("C-SPLIT unchecked", RD, "        if keys != {s5c_pseudo.split_key_for(s)}:\n", "        if False:\n",
     "test_a_split_off_its_seed_refuses"),
    ("C-CAP recorded unchecked", RD, 'if rec != {k: declared[k] for k in rec} or pr.get("recorded") != rec:', "if False:",
     "test_c_cap_on_the_recorded_iters"),
    ("mask record unchecked", RD, 'if m.get("calls") != 1 or m.get("gen_columns") != list(g) or m.get("reco_columns") != list(r):',
     "if False:", "test_a_missed_mask_refuses"),
    ("truth file unchecked", RD, '    if (meta.get("hypothesis") or {}).get("sha256") != want["hyp"]:\n', "    if False:\n",
     "test_a_wrong_truth_file_refuses"),
    ("product code digests unchecked", RD, "    if moved:\n        bad.append", "    if False:\n        bad.append",
     "test_a_product_made_by_other_code_refuses"),
    ("a noisy product admitted", RD, ' or (meta.get("nuisance_draw") is not None):', ":", "test_a_noisy_product_refuses"),
    ("C-IBU truths unchecked", RD, "    if worst > 1e-12:\n", "    if False:\n", "test_c_ibu_truths_must_be_es"),
    ("C-MASK not recomputed", RD, '    if not controls["C-MASK"]["pass"]:\n', "    if False:\n", "test_c_mask_on_the_products"),
    ("a cell value leaks", RD, '        out[(lv, t, s)] = {"rho": r_, "n_S": n_s, "b": b.tolist(),',
     '        out[(lv, t, s)] = {"x_hat": xh.tolist(), "rho": r_, "n_S": n_s, "b": b.tolist(),', "test_planted_classes"),
    # --- the job script
    ("pair does not gate", SB, '    [ "$pc" -eq 0 ] || {', '    [ "$pc" -eq "$pc" ] || {',
     "test_a_failed_pair_stops_the_dry_run_and_every_full_job"),
    ("TimeLimit unchecked", SB, "sys.exit(0 if sec(sys.argv[1]) <= sec(sys.argv[2]) else 1)", "sys.exit(0)",
     "test_a_limit_above_the_declared_is_refused"),
    ("full without the dry run's DONE", SB, '    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] ||',
     "    true ||", "test_a_failed_pair_stops_the_dry_run_and_every_full_job"),
    ("stage not re-verified", SB, 'python3 "$PY" verify-stage --stage "$OUT/stage.json" )', "true )",
     "test_a_full_job_refuses_a_changed_stage"),
    ("runs outside Slurm", SB, '    echo "[prr] refusing: not inside a Slurm job" >&2; exit 2', '    NAME="prr_$MODE"; TL="$LIMIT"',
     "test_outside_slurm_without_the_smoke_flag_it_refuses"),
    ("ens1 jobs not checked", SB, '    [ -z "$ens" ] || {', '    true || {',
     "test_an_ens1_job_queued_or_running_refuses_the_dry_run"),
    ("squeue failure admitted", SB, "2>/dev/null) || { echo \"[prr] refusing: squeue failed", "2>/dev/null) || true || { echo \"[prr] refusing: squeue failed",
     "test_an_ens1_job_queued_or_running_refuses_the_dry_run"),
    # --- Addendum A1 (REQUIRED): the environment is sourced before every python3 call
    ("limit above the source", SB, 'source "$D/setup_salloc_env.sh" > /dev/null 2>&1\n', "",
     "test_every_python3_call_runs_after_the_environment_is_sourced"),
    ("a failed task still DONE", SB, '[ "$rc" -eq 0 ] || { echo "rc=$rc" > "$L/FAILED"; echo "[prr] STOP: a task failed',
     'true || { echo "rc=$rc" > "$L/FAILED"; echo "[prr] STOP: a task failed',
     "test_a_failed_task_leaves_no_done"),
]


def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the FD-PRR files. Returns its prior_retention/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "prior_retention":
            (nd / e.name).symlink_to(e)
    pr = nd / "prior_retention"
    pr.mkdir()
    for f in FILES:
        (pr / f).write_bytes((HERE / f).read_bytes())
    return pr


def run_suite(pr: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PRR_SBATCH": str(pr / SB)}
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/prior_retention/test_prr.py"],
                       capture_output=True, text=True, cwd=str(pr.parents[1]), env=env)
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
            pr = mirror(Path(d))
            (pr / fname).write_text(src.replace(old, new))
            _, out = run_suite(pr)
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
            print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:40s} by {test}"
                  + ("" if killed else f"  (failing: {sorted(fails)})"), flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({n} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
