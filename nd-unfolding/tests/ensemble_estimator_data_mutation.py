"""Mutation check of E96-DATA's tests (fd/e96-data-20261110/E96D-DECLARATION.md, draft): REQUIRED mutants for every gate,
refusal and the analysis's controls, in ENS1's harness pattern (tests/ensemble_estimator_mutation.py).

Each mutation plants one declared defect in a temporary copy of ``ensemble_estimator_data.py`` and runs the suite with
that copy first on sys.path. The mutation must make its NAMED test fail, not merely some test. Exit 0 only if every
mutation is killed by its named test and the unmutated suite runs all EXPECTED_TESTS and passes.

    python3 -B nd-unfolding/tests/ensemble_estimator_data_mutation.py
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TEST = ND / "tests" / "test_ensemble_estimator_data.py"
M = "ensemble_estimator_data.py"
S = "sbatch_e96data.sh"
EXPECTED_TESTS = 30

# (label, old, new, the test that must fail[, file]); the file is the module unless named
MUTATIONS = [
    # --- the job script (the test runs the copy through E96D_SBATCH)
    ("REQ the full run without the dry DONE", '    [ -s "$OUT/log-dry/DONE" ] && [ ! -e "$OUT/log-dry/FAILED" ] ||', "    true ||",
     "test_full_needs_the_dry_done_at_this_pin_and_dry_then_full_run", S),
    ("the deploy pin unchecked", 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', "if false; then",
     "test_it_refuses_a_deploy_off_the_pin_and_a_bad_mode", S),
    ("an existing log resumed", '[ ! -e "$L" ] || { echo "[e96data] refusing: $L exists" >&2; exit 2; }', "true",
     "test_full_needs_the_dry_done_at_this_pin_and_dry_then_full_run", S),
    # --- REQUIRED: the data role's own refusals and the float64 base
    ("REQ a pseudo construction admitted", '    if getattr(ns, "construction", None) != "data":',
     "    if False:", "test_a_pseudo_construction_is_refused"),
    ("REQ the base takes a protocol jitter at seed 0", 'ji, jb = o["jittered"](inputs, bkg, None)',
     'ji, jb = o["jittered"](inputs, bkg, seed)', "test_the_base_is_the_float64_copy"),
    ("REQ a write without the check", '        if not st["checked"]:\n            raise Refusal("refusing to write',
     '        if False:\n            raise Refusal("refusing to write', "test_a_write_without_the_namespace_check_is_refused"),
    ("REQ the control passes when one ulp differs", "        same_array(raw_xsec(pc), x_e) and not probs,",
     "        bool(np.allclose(np.asarray(raw_xsec(pc), float), np.asarray(x_e, float), rtol=1e-12, atol=0)) and not probs,",
     "test_a_control_one_ulp_off_stops"),
    ("REQ the control runs the float64 path", '        if mode == "control":\n            raise Refusal("the control is',
     '        if False:\n            raise Refusal("the control is', "test_the_control_takes_no_jitter_and_the_base_no_protocol_seed"),
    # --- the namespace
    ("any pair accepted", "    if pairs != [PAIR[mode]]:", "    if False:",
     "test_undeclared_pairs_are_refused_and_the_declared_ones_are_not"),
    ("threads unchecked", '    for key in ("iters", "threads", "estimator_seed"):', '    for key in ("iters", "estimator_seed"):',
     "test_each_namespace_check_refuses"),
    ("capacity admitted", '    if getattr(ns, "capacity", None) is not None:', "    if False:", "test_each_namespace_check_refuses"),
    ("eavail ratio admitted", '    for key in ("pseudo_seed", "pseudo_seeds", "fixed_split_seed", "eavail_ratio"):',
     '    for key in ("pseudo_seed", "pseudo_seeds", "fixed_split_seed"):', "test_each_namespace_check_refuses"),
    ("truth unchecked", '    if getattr(ns, "truth", None) != "nominal" or float(getattr(ns, "amplitude", -1)) != 0.0:',
     "    if False:", "test_each_namespace_check_refuses"),
    ("inputs unchecked", '    if getattr(ns, "expect_npz_sha256", None) != DATA["npz_sha256"] or \\\n            getattr(ns, "expect_bkg_sha256", None) != DATA["bkg_sha256"]:',
     "    if False:", "test_each_namespace_check_refuses"),
    # --- the rebinding
    ("protocol seed admitted", "        if seed != BASE_SEED:\n            raise Refusal", "        if False:\n            raise Refusal",
     "test_the_control_takes_no_jitter_and_the_base_no_protocol_seed"),
    ("the ensemble without delta_k", "        if k is not None:\n            ji, jb, item", "        if False:\n            ji, jb, item",
     "test_the_ensemble_fits_carry_delta_k_and_differ_across_k"),
    ("moved rows not recorded", '"moved_rows": item.get("moved_rows"),', '"moved_rows": None,',
     "test_the_ensemble_fits_carry_delta_k_and_differ_across_k"),
    ("install takes any k", '    if (mode in ("ensemble", "repeat")) != (k is not None) or', "    if False or", "test_install_arguments"),
    ("CLI accepts an undeclared k", 'if mode == "ensemble" and (len(set(ks)) != len(ks) or',
     'if False and (len(set(ks)) != len(ks) or', "test_cli_refuses_an_undeclared_k_before_any_runner"),
    # --- the queue
    ("queue misses the last pair", "    for i in range(0, len(ks), CHUNK):", "    for i in range(0, len(ks) - CHUNK, CHUNK):",
     "test_the_queue"),
    ("the full run repeats the dry k", "    ks = [k for k in range(1, N_ENS + 1) if k not in DRY_KS]",
     "    ks = list(range(1, N_ENS + 1))", "test_the_queue"),
    # --- the dry run's gate and the repeat (audit E1, E2), REQUIRED
    ("REQ the full run without a passing gate", '    [ "$gate_ok" = yes ] ||', "    true ||",
     "test_full_refuses_a_failing_or_missing_gate", S),
    ("the gate's queue sha unchecked", '    [ "$q_sha" = "$g_sha" ] ||', "    true ||", "test_full_refuses_a_queue_other_than_the_gated_one", S),
    ("the projection without the load time", "    return float(lo) + float(un) if", "    return float(un) if",
     "test_the_gate_passes_the_declared_dry_run_and_records_the_pin"),
    ("REQ the gate's projection removed", "        proj is not None and proj <= 0.9 * FULL_TIME_S,", "        True,",
     "test_the_gate_fails_on_a_control_defect_a_slow_unfold_or_a_missing_k1"),
    ("REQ the gate skips the control", "        m_c = check_control(a.runs, x_e, chk)\n        p1 = product_path(a.runs, \"ensemble\", 1)",
     "        m_c = None\n        p1 = product_path(a.runs, \"ensemble\", 1)",
     "test_the_gate_fails_on_a_control_defect_a_slow_unfold_or_a_missing_k1"),
    ("REQ the repeat not compared", "            p1.is_file() and same_array(raw_xsec(pr), raw_xsec(p1)) and not r_probs,",
     "            not r_probs,", "test_the_repeat_must_equal_k1_bitwise"),
    ("the repeat takes any k", 'or (mode == "repeat" and k != REPEAT_K):', ":", "test_install_arguments"),
    # --- the post-hoc meta checks (audit E3, e1, e4)
    ("REQ seed/threads/iters unchecked post hoc", '    if (meta.get("estimator_seed"), meta.get("threads"), meta.get("iters")) != \\\n            (DATA["estimator_seed"], DATA["threads"], DATA["iters"]):',
     "    if False:", "test_each_post_hoc_meta_check_stops"),
    ("REQ the control's meta ignored", "        same_array(raw_xsec(pc), x_e) and not probs, {\"problems\": probs})",
     "        same_array(raw_xsec(pc), x_e), {\"problems\": probs})", "test_each_post_hoc_meta_check_stops"),
    ("REQ the base's meta ignored", '    probs = product_problems(m_b, "base", None)\n    codes', "    probs = []\n    codes",
     "test_each_post_hoc_meta_check_stops"),
    ("REQ one code unchecked", "        not missing and not probs and len(codes) == 1 and len(digests) == N_ENS,",
     "        not missing and not probs and len(digests) == N_ENS,", "test_each_post_hoc_meta_check_stops"),
    ("REQ coords unchecked", '    if meta.get("coords") != ("float32" if mode == "control" else "float64"):', "    if False:",
     "test_each_post_hoc_meta_check_stops"),
    ("the control's code outside the set", "    codes = {code_of(m_b)} | ({code_of(m_c)} if m_c is not None else set())",
     "    codes = {code_of(m_b)}", "test_each_post_hoc_meta_check_stops"),
    ("dtype ignored in the bitwise comparison", "    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()",
     "    return np.array_equal(np.asarray(a, np.float64), np.asarray(b, np.float64))", "test_a_missing_control_dtype_or_e_sha_is_a_stop_record"),
    ("A-D0's digest unchecked", "a.e_product.is_file() and sha256_path(a.e_product) == e_sha", "a.e_product.is_file()",
     "test_a_missing_control_dtype_or_e_sha_is_a_stop_record"),
    # --- the analysis
    ("A-D0 f unchecked", 'bool(np.allclose(f_e, f_dp, rtol=1e-12, atol=0))', "True", "test_an_f_that_is_not_es_stops"),
    ("A-D2 a missing fit accepted", "        not missing and not probs and len(codes) == 1 and len(digests) == N_ENS,",
     "        not probs and len(codes) == 1,", "test_each_a_d2_defect_stops"),
    ("A-D2 moved rows accepted", '    if mode != "control" and any((blk.get("moved_rows") or {"_": 1}).values()):',
     "    if False:", "test_each_a_d2_defect_stops"),
    ("E96 is the first fit, not the mean", "    x_E = X.mean(axis=0)", "    x_E = X[0]",
     "test_the_result_is_the_hand_computation"),
    ("the sd of the mean without sqrt(96)", "    sd_mean = F.std(axis=0, ddof=1) / np.sqrt(N_ENS)",
     "    sd_mean = F.std(axis=0, ddof=1)", "test_the_result_is_the_hand_computation"),
]


def run_suite(first: Path | None, script: Path | None = None) -> tuple[int, str]:
    boot = ("import sys, runpy; sys.argv = ['t']; " + (f"sys.path.insert(0, {str(first)!r}); " if first else "")
            + f"runpy.run_path({str(TEST)!r}, run_name='__main__')")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("E96D_SBATCH", None)
    if script is not None:
        env["E96D_SBATCH"] = str(script)
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
        label, old, new, test = m[:4]
        fname = m[4] if len(m) > 4 else M
        src = (ND / fname).read_text()
        if src.count(old) != 1:
            return f"MUTATION NOT APPLIED  {label}: anchor occurs {src.count(old)} times", False
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / fname).write_text(src.replace(old, new))
            if fname == S:
                rc, out = run_suite(None, Path(d) / S)
            else:
                rc, out = run_suite(Path(d))
        fails = failing(out)
        killed = test in fails
        return (f"{'KILLED' if killed else 'SURVIVED':8s}  {label:46s} by {test}"
                + ("" if killed else f"  (failing: {sorted(fails)})")), killed
    ok = True
    with ThreadPoolExecutor(int(os.environ.get("E96D_MUTATION_WORKERS", "6"))) as ex:
        for text, killed in ex.map(one, MUTATIONS):
            ok &= killed
            print(text, flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
