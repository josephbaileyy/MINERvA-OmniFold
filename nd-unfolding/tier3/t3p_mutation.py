"""Mutation check of T3's tests (T3-PIPELINE-TESTS-DECLARATION.md rev 2, §8).

Each mutation plants one declared defect in a copy of one T3 file and must make the NAMED test fail, not merely some
test. The copy runs in a temporary tree that mirrors the repository: tier3/ holds real copies of the T3 files (the
mutated one among them), and every other entry is a symlink to the real file, so the pins and imports resolve as in the
checkout (FD-PRR's harness, prr_mutation.py, the same way). Exit 0 only if the unmutated suite passes with the expected
test count and every mutation is killed by its named test. Mutations marked REQUIRED are the director's ruling 5.

    python3 -B nd-unfolding/tier3/t3p_mutation.py [--only LABEL_SUBSTRING] [--jobs N]
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
FILES = ("t3p_arms.py", "t3p_probe.py", "t3p_read.py", "sbatch_t3p.sh", "test_t3p.py")
AR, PB, RD, SB = FILES[:4]
EXPECTED_TESTS = 69
MUTATIONS = [
    # --- REQUIRED: C-PAIR fails on a one-ulp change, and the trace at k is the plain unfold at k
    ("REQUIRED C-PAIR compares within a tolerance", PB,
     '"pass": bool(a.tobytes() == b.tobytes())', '"pass": bool(np.allclose(a, b))', "test_one_ulp_in_our_trace_fails_c_pair"),
    ("REQUIRED C-PAIR compares within a tolerance (reference side)", PB,
     '"pass": bool(a.tobytes() == b.tobytes())', '"pass": bool(np.allclose(a, b))', "test_one_ulp_in_the_reference_fails_c_pair"),
    ("REQUIRED stored k unfold from w_pull", AR,
     'self.xs_at[k] = xs_from_push(self.unf_in, w_push).ravel(order="C")',
     'self.xs_at[k] = xs_from_push(self.unf_in, w_pull).ravel(order="C")',
     "test_b0_trace_at_k_equals_the_plain_unfold_at_k"),
    # --- the probe: the namespace check
    ("iters unchecked", PB, 'if getattr(ns, "iters", None) != A.ITERS[arm]:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("capacity unchecked", PB, 'if s5e_trace.parse_pair(getattr(ns, "capacity", None)) is not None:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("mc fraction unchecked", PB, 'if getattr(ns, "mc_fraction", None) != "half":', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("undeclared task admitted", PB, "if (arm, truth, int(a)) not in set(all_tasks()):", "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("tag unchecked", PB, 'if getattr(ns, "tag", None) != f"t3p_{arm}_{truth}":', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("hypothesis unchecked", PB, 'if str(getattr(ns, "hypothesis", "")) != hyp:', "if False:",
     "test_the_refusals_fire_on_the_runners_parse"),
    ("iterations not set on the line", PB, '_set(argv, "--iters", str(A.ITERS[arm]))', "pass",
     "test_lines_are_fd_prrs_k50_line_but_for_three_fields"),
    ("jobs swapped", PB, 'return "dry" if truth == FLOOR_TRUTH else "q3"', 'return "q3" if truth == FLOOR_TRUTH else "dry"',
     "test_tasks_and_jobs"),
    ("floor limit too low", PB, 'JOB_LIMIT_H = {"dry": 2.25, "q3": 2.0, "floor": 5.75}',
     'JOB_LIMIT_H = {"dry": 2.25, "q3": 2.0, "floor": 5.5}', "test_price_limits_and_cap"),
    ("trace unit changed", PB, "TASK_S = {50: 6000.0, 2: 600.0}", "TASK_S = {50: 5000.0, 2: 600.0}",
     "test_price_limits_and_cap"),
    ("pairing levels shifted", PB, 'PRR_LEVEL_AT_K = {5: "B0", 10: "K10", 20: "K20", 50: "K50"}',
     'PRR_LEVEL_AT_K = {5: "K10", 10: "B0", 20: "K20", 50: "K50"}', "test_sources"),
    # --- the probe: the install
    ("SO keeps the background", PB, 'kw = dict(kw, no_background=(arm == "SO"))', "kw = dict(kw, no_background=False)",
     "test_so_builds_signal_only_and_r_is_captured"),
    ("r from the pseudo-data half", PB, 'state["r_A"] = r[~is_b]', 'state["r_A"] = r[is_b]',
     "test_so_builds_signal_only_and_r_is_captured"),
    ("runner's development option admitted", PB, 'if kw.get("no_background") or kw.get("prior_matches_truth"):',
     "if False:", "test_a_development_option_from_the_runner_is_refused"),
    ("write without the check", PB, 'if not state["checked"]:', "if False:",
     "test_no_product_without_the_check_or_the_steps"),
    ("write without the steps", PB, 'if state["builds"] != 1 or state["unfolds"] != 1 or state["trace"] is None:',
     "if False:", "test_no_product_without_the_check_or_the_steps"),
    ("rho read in place", PB, "if not rho or sha not in rho:", "if False:",
     "test_the_rho_loader_reads_only_a_staged_copy"),
    ("substitute unfold admitted", PB, "if unfold_fn is not None:", "if False:",
     "test_unfold_one_refuses_a_missing_r_a_mismatched_r_or_a_substitute"),
    ("r length unchecked", PB, 'if state["r_A"] is None or len(state["r_A"]) != len(exp["MCgen"]):',
     'if state["r_A"] is None:', "test_unfold_one_refuses_a_missing_r_a_mismatched_r_or_a_substitute"),
    # --- the probe: C-PAIR, C-X and the gate
    ("C-PAIR dtype ignored", PB, "if a.dtype != b.dtype or a.shape != b.shape:", "if a.shape != b.shape:",
     "test_a_dtype_change_fails"),
    ("C-PAIR by value", PB, '"pass": bool(a.tobytes() == b.tobytes())', '"pass": bool(np.array_equal(a, b))',
     "test_a_signed_zero_fails_c_pair"),
    ("C-PAIR pin unchecked", PB,
     'if ref is None or sha256_path(ref) != pin:\n            out["C-PAIR"][key]',
     'if ref is None:\n            out["C-PAIR"][key]', "test_a_reference_that_is_not_its_pin_fails"),
    ("C-X not in the verdict", PB, 'for blk in ("C-PAIR", "C-X") for v in out[blk].values())',
     'for blk in ("C-PAIR",) for v in out[blk].values())', "test_one_ulp_in_an_arms_truth_fails_c_x"),
    ("full job starts unmeasured", PB, 'if mode == "full" and p["unmeasured"]:', "if False:",
     "test_a_full_job_refuses_an_unmeasured_arm_and_uses_a_measured_one"),
    ("projection ignored", PB, 'elif p["projected_h"] > GATE_FRACTION * limit_h:', "elif False:",
     "test_a_projection_above_the_limit_stops"),
    ("rates from FD-PRR's ids", PB, 'tid.startswith("t3p_") and arm_of(tid) in A.ARMS',
     'tid.startswith("prr_") and arm_of(tid) in A.ARMS', "test_a_full_job_refuses_an_unmeasured_arm_and_uses_a_measured_one"),
    # --- the arms
    ("MW weight not passed on", AR, "self._inner.fit(X, y, sample_weight=sample_weight)",
     "self._inner.fit(X, y, sample_weight=None)", "test_mw_weights_reach_the_regressor"),
    ("MW weight on the reco population", AR, "return self.w_push[self.pr] * self.w_truth[self.pr]",
     "return self.w_push[self.pr] * self.w_reco[self.pr]", "test_mw_weights_reach_the_regressor"),
    ("MW check disabled", AR, "if self.mw_given is None or not np.array_equal(self.mw_given, want):", "if False:",
     "test_mw_refuses_a_wrong_weight"),
    ("MO oracle on the wrong side", AR, "out = self.oracle_new_w(pass_side=False)",
     "out = self.oracle_new_w(pass_side=True)", "test_mo_gives_misses_the_true_weight"),
    ("oracle check disabled", AR, "if not dev <= ORACLE_RTOL:", "if False:", "test_mo_and_op_refuse_a_wrong_oracle"),
    ("OP leaves step 1 alone", AR, 'if self._role == "step1" and t.arm == "OP":', "if False:",
     "test_op_gives_every_event_the_true_weight_and_records_the_repeat"),
    ("clip edges swapped", AR, "self.clip[role].append((int(np.sum(p <= CLIP)), int(np.sum(p >= 1.0 - CLIP))))",
     "self.clip[role].append((int(np.sum(p >= 1.0 - CLIP)), int(np.sum(p <= CLIP))))", "test_the_clip_is_counted"),
    ("push and pull swapped", AR, '"X16_push": o["fn_push"], "X16_pull": o["fn_pull"]',
     '"X16_push": o["fn_pull"], "X16_pull": o["fn_push"]', "test_the_trace_records_r00_r15_from_the_production_extraction"),
    # --- the reader
    ("crossing never classed", RD, "if min(rhos) <= -delta:", "if False:", "test_trajectory_classes"),
    ("tail bar halved", RD, "if r25 - r50 >= dt:", "if r25 - r50 >= dt / 2:", "test_the_tail_bar_is_delta_t"),
    ("reco overshoot ignored", RD, "if abs(r1) >= DELTA_R:", "if r1 >= DELTA_R:", "test_location_classes"),
    ("TR-1 boundary open", RD, "if delta <= -bar:", "if delta < -bar:", "test_tr1_and_tr2"),
    ("TR-2 sign", RD, 'return "step 2 carries the truth" if abs(rho_op) < bar else',
     'return "step 2 carries the truth" if rho_op < bar else', "test_tr1_and_tr2"),
    ("bounded by step 2 dropped", RD,
     'if arm in STEP2_BOUNDED and tr1[arm] == "no effect" and headroom is not None and headroom < bars[arm]:',
     "if False:", "test_mo_bounded_by_step_2"),
    ("bounded by step 2 from TR-2's class", RD,
     'if arm in STEP2_BOUNDED and tr1[arm] == "no effect" and headroom is not None and headroom < bars[arm]:',
     'if arm == "MO" and tr1[arm] == "no effect" and tr2 == "step 2 does not carry the truth":',
     "test_bounded_by_step_2_is_decided_from_the_numbers"),
    ("bounded by step 2 ignores the headroom", RD, "headroom is not None and headroom < bars[arm]:",
     "headroom is not None:", "test_no_effect_with_headroom_stands_whatever_tr2"),
    ("v1: the bound includes equality", RD, "headroom is not None and headroom < bars[arm]:",
     "headroom is not None and headroom <= bars[arm]:", "test_the_bound_is_strict_at_equality"),
    ("SO bounded by OP", RD, 'STEP2_BOUNDED = ("MU", "MW", "MO")', "STEP2_BOUNDED = TR1_ARMS",
     "test_mo_bounded_by_step_2"),
    ("resolution not printed", RD, '"bar_over_rho_B0_50": None if not b50 else bars[arm] / b50,',
     '"bar_over_rho_B0_50": None,', "test_bounded_by_step_2_is_decided_from_the_numbers"),
    ("R1a: the bound rewrites a lowers", RD, 'tr1[arm] == "no effect" and headroom',
     'tr1[arm] in ("no effect", "lowers the limit") and headroom', "test_a_lowers_is_never_rewritten_to_bounded"),
    ("R1b: the headroom takes OP at k = 1", RD, 'op = rho_at(q[("OP", t, S0)], 2)', 'op = rho_at(q[("OP", t, S0)], 1)',
     "test_the_headroom_operands_are_rho_op_at_2_and_rho_b0_at_50"),
    ("R1c: the headroom takes B0 at k = 5", RD, "headroom = None if op is None or b50 is None else b50 - op",
     "headroom = None if op is None or b50 is None else b5 - op",
     "test_the_headroom_operands_are_rho_op_at_2_and_rho_b0_at_50"),
    ("resolution Delta dropped", RD, 'res[arm] = {"Delta": d50,', 'res[arm] = {"Delta": None,',
     "test_a_lowers_is_never_rewritten_to_bounded"),
    ("crossing boundary open", RD, "if min(rhos) <= -delta:", "if min(rhos) < -delta:", "test_trajectory_classes"),
    ("crosses keeps rho(50) = delta", RD, 'return "crosses" if r50 < delta else', 'return "crosses" if r50 <= delta else',
     "test_trajectory_classes"),
    ("C-PAIR shape ignored", PB, "if a.dtype != b.dtype or a.shape != b.shape:", "if a.dtype != b.dtype:",
     "test_a_dtype_change_fails"),
    ("crosses and returns folded", RD, 'return "crosses" if r50 < delta else "crosses and returns"',
     'return "crosses"', "test_trajectory_classes"),
    ("unattributed dropped", RD, 'return out or ["unattributed"]', "return out", "test_labels"),
    ("b_par outside S", RD, "par = np.where(S, -rho * d, 0.0)", "par = -rho * d", "test_bias_split_is_exact"),
    ("bar floor dropped", RD, "bars[arm] = max(BAR_FLOOR, T_Q * s[arm])", "bars[arm] = T_Q * s[arm]",
     "test_planted_classes"),
    ("a failed pair record read", RD, 'if not pr.is_file() or json.loads(pr.read_text()).get("pass") is not True:',
     "if not pr.is_file():", "test_incomplete_when_a_pair_record_failed"),
    ("SO evidence unchecked", RD,
     'if not (ref.get("ran") is False and so.get("template_rows") == 0 and so.get("pseudo_background_events") == 0',
     'if False and (ref.get("ran") is False and so.get("template_rows") == 0 and so.get("pseudo_background_events") == 0',
     "test_so_with_the_refinement_running_stops"),
    ("oracle evidence unchecked", RD, "if len(dev) != it or not all(d <= A.ORACLE_RTOL for d in dev):",
     "if len(dev) != it:", "test_a_product_check_stops"),
    ("C-TRACE disabled", RD, 'if not np.allclose(arrays["X16_push"][k - 1], ref, rtol=1e-12, atol=0):', "if False:",
     "test_c_trace_stops"),
    ("C-RECO disabled", RD, "if not np.isclose(ric[i], float(np.sum(arrays[key])), rtol=1e-12, atol=0):", "if False:",
     "test_c_reco_stops"),
    ("C-P pin unchecked", RD, "if path is None or T.sha256_path(path) != pin:", "if path is None:",
     "test_a_prior_not_its_pin_stops"),
    ("T_Q from FD-PRR's family", RD, "T_Q = 8.610301581379899", "T_Q = 9.02936702750999", "test_t_quantile"),
    # --- the job script
    ("deploy pin unchecked", SB, 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', "if false; then",
     "test_a_deploy_not_at_its_pin_refuses"),
    ("job name unchecked", SB, '[ "$NAME" = "t3p_$MODE" ] ||', "true ||", "test_a_wrong_job_name_refuses"),
    ("limit above admitted", SB, '[ "$trc" -ne 4 ] ||', "true ||",
     "test_a_limit_above_the_declared_refuses_and_an_unreadable_one_says_so"),
    ("no fence admitted", SB, '[ -s "$OUT/fence.txt" ] ||', "true ||",
     "test_the_dry_run_refuses_without_a_fence_and_on_a_fenced_job"),
    ("fence prefix anywhere", SB, "'index($1, p) == 1'", "'index($1, p) > 0'",
     "test_a_fence_prefix_matches_only_at_the_start"),
    ("squeue failure tolerated", SB, "sq=$(squeue -h -u \"${USER:-josephrb}\" -o '%j|%T' 2>/dev/null) ||",
     "sq=$(squeue -h -u \"${USER:-josephrb}\" -o '%j|%T' 2>/dev/null) ; true ||",
     "test_the_dry_run_refuses_without_a_fence_and_on_a_fenced_job"),
    ("fence in the dry job only", SB, "fi\nfence_check\n", 'fi\n[ "$MODE" != dry ] || fence_check\n',
     "test_a_full_job_checks_the_fence_too"),
    ("full job without the dry DONE", SB, '[ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/STOP" ] ||', "true ||",
     "test_a_full_job_refuses_without_the_dry_runs_done_and_an_existing_log"),
]


def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the T3 files. Returns its tier3/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "tier3":
            (nd / e.name).symlink_to(e)
    t3 = nd / "tier3"
    t3.mkdir()
    for f in FILES:
        (t3 / f).write_bytes((HERE / f).read_bytes())
    (t3 / SB).chmod(0o755)
    return t3


def run_suite(t3: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/tier3/test_t3p.py"], cwd=t3.parents[1],
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
            t3 = mirror(Path(d))
            (t3 / fname).write_text(src.replace(old, new))
            _, out = run_suite(t3)
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
