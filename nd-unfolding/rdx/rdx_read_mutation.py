#!/usr/bin/env python3
"""Mutation check of rdx_read.py's tests (test_rdx_read.py), with rdx_mutation_stages.py's harness pattern.

Each mutation plants one defect in a copy of rdx_read.py and must make the NAMED test fail. Exit 0 only if the unmutated
suite passes with the expected test count and every mutation is killed by its named test.

    python3 -B nd-unfolding/rdx/rdx_read_mutation.py [--only LABEL_SUBSTRING] [--jobs N]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("rdx_read.py", "test_rdx_read.py")
RD = FILES[0]
EXPECTED_TESTS = 30
MUTATIONS = [
    # NC-X and the families
    ("NC-X not checked", RD, '    if not (same_bits(x0[1], xl[1]) and same_bits(x0[3], xl[3])):\n', "    if False:\n",
     "test_nc_x_is_bitwise_on_xsec_flat_and_shape"),
    ("NC-X by value, not bits", RD, "    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()\n",
     "    return a.shape == b.shape and bool(np.array_equal(a, b))\n", "test_nc_x_is_bitwise_on_xsec_flat_and_shape"),
    ("NC-X skips shape", RD, "same_bits(x0[1], xl[1]) and same_bits(x0[3], xl[3])", "same_bits(x0[1], xl[1])",
     "test_nc_x_is_bitwise_on_xsec_flat_and_shape"),
    ("family truths unchecked", RD, "            if prod[t][2] is None or not same_bits(prod[t][2], t0):\n",
     "            if prod[t][2] is None:\n", "test_a_closure_familys_truths_must_agree"),
    # logs, tasks, directory
    ("sha not compared with the job's", RD, "        if got[task] != shas[task]:\n", "        if False:\n",
     "test_a_sha_that_is_not_the_jobs_refuses"),
    ("a missing log line allowed", RD, "    if missing:\n", "    if False:\n",
     "test_the_logs_print_each_task_once_in_its_own_jobs_log"),
    ("a duplicated log line allowed", RD, "            if task in seen:\n", "            if False:\n",
     "test_the_logs_print_each_task_once_in_its_own_jobs_log"),
    ("an undeclared product allowed", RD, "            if task not in spec:\n", "            if False:\n",
     "test_the_logs_print_each_task_once_in_its_own_jobs_log"),
    ("the other job's log allowed", RD, '            if spec[task]["job"] != job:\n', "            if False:\n",
     "test_the_logs_print_each_task_once_in_its_own_jobs_log"),
    ("malformed product lines ignored", RD, '                if "/products/" in s:\n', "                if False:\n",
     "test_a_malformed_product_line_refuses_and_chatter_does_not"),
    ("extra products allowed", RD, "    if found != sorted(spec):\n", "    if not set(spec) <= set(found):\n",
     "test_the_directory_must_hold_exactly_the_fifteen"),
    ("task table sha unchecked", RD, "    if expect_sha is not None and sha256(path) != expect_sha:\n", "    if False:\n",
     "test_the_task_table_and_manifests_are_bound_and_unique"),
    ("duplicate task rows allowed", RD, "        if task in out:\n            fail(f\"{path}: the task {task} appears twice\")\n",
     "        if False:\n            pass\n", "test_the_task_table_and_manifests_are_bound_and_unique"),
    ("duplicate manifest keys allowed", RD, "        if name in out:\n", "        if False:\n",
     "test_the_task_table_and_manifests_are_bound_and_unique"),
    # arrays and identity
    ("identity not enforced", RD, '        bad = identity_problems(prod[task][0], s, pins, None if task == "X0" else ref)\n        if bad:\n',
     '        bad = identity_problems(prod[task][0], s, pins, None if task == "X0" else ref)\n        if False:\n',
     "test_a_product_that_is_not_its_declared_task_refuses"),
    ("arrays not checked", RD, '        bad = array_problems(prod[task][1], prod[task][2], prod[task][3], spec[task]["closure"], n_fine, fine_shape)\n        if bad:\n',
     '        bad = array_problems(prod[task][1], prod[task][2], prod[task][3], spec[task]["closure"], n_fine, fine_shape)\n        if False:\n',
     "test_product_arrays_must_be_the_fine_grids"),
    ("non-finite arrays allowed", RD, "        elif not np.all(np.isfinite(a)):\n", "        elif False:\n",
     "test_product_arrays_must_be_the_fine_grids"),
    ("background pin of X0_lat taken from RDX's", RD, '"bkg_dump_sha256": pins["lat_zero_bkg.npz" if lat else "lat_RDX_ALL_bkg.npz"]',
     '"bkg_dump_sha256": pins["lat_RDX_ALL_bkg.npz"]', "test_a_product_that_is_not_its_declared_task_refuses"),
    ("estimator parameters not compared", RD, '        if params != ref.get("estimator_params"):\n', "        if False:\n",
     "test_parameters_must_be_present_and_x0s"),
    ("absent estimator parameters allowed", RD, "    if not params or not isinstance(params, (dict, list)):\n", "    if False:\n",
     "test_parameters_must_be_present_and_x0s"),
    ("predict count unchecked", RD, ' or r.get("predict_calls") != ITERS:', ":",
     "test_a_product_that_is_not_its_declared_task_refuses"),
    ("A7 pin unchecked", RD, '        if r.get("a7_hypothesis_sha256") != A7_HYPOTHESIS_SHA256:\n', "        if False:\n",
     "test_a_product_that_is_not_its_declared_task_refuses"),
    ("transfer iterations unchecked", RD, "    if [r.get(\"iteration\") if isinstance(r, dict) else None for r in recs] != list(range(ITERS)):\n",
     "    if False:\n", "test_the_transfer_records_are_the_producers"),
    ("transfer cell_bias schema unchecked", RD, "        if not isinstance(cb, list) or len(cb) != 16 or not all(v is None or finite(v) for v in cb):\n",
     "        if False:\n", "test_the_transfer_records_are_the_producers"),
    ("transfer records on a plain arm allowed", RD, '    elif "transfer_records" in r:\n', "    elif False:\n",
     "test_the_transfer_records_are_the_producers"),
    # phi, sigma, integrals, references
    ("sigma finiteness unchecked", RD, "        if v.shape != (16,) or not np.all(np.isfinite(v)) or np.any(v <= 0):\n",
     "        if v.shape != (16,) or np.any(v <= 0):\n", "test_phi_and_sigma_are_committed_finite_and_positive"),
    ("cell integrals unchecked", RD, '        if c.shape != (16,) or not np.all(np.isfinite(c)):\n', "        if False:\n",
     "test_a_cell_integral_must_be_sixteen_finite_values"),
    ("transfer cell_bias read unchecked", RD, "        if len(t) != 16 or not all(v is None or finite(v) for v in t):\n",
     "        if False:\n", "test_a_transfer_cell_bias_read_must_be_sixteen_values"),
    ("a nonpositive reference allowed", RD, "    if np.any(b <= 0) or", "    if False and np.any(b <= 0) or",
     "test_a_nonpositive_reference_refuses"),
    # the readings
    ("the null not subtracted in R1", RD, "    e = np.abs(d1) - np.abs(dp)\n", "    e = np.abs(d1)\n",
     "test_the_excess_is_beyond_the_null"),
    ("half sigma read as one sigma", RD, "e > RR.HALF_SIGMA * sigma", "e > sigma",
     "test_an_excess_beyond_half_sigma_is_a_named_sensitivity"),
    ("equality named", RD, "e > RR.HALF_SIGMA * sigma", "e >= RR.HALF_SIGMA * sigma",
     "test_an_excess_exactly_at_half_sigma_is_licensed"),
    ("refit null W2 not decisive", RD, '    if c1p == "W2":\n', '    if c1p == "W9":\n',
     "test_the_refit_null_takes_precedence_over_a_sensitivity"),
    ("R4 read against X0c's truth", RD, "        return rel(X[t], cells(prod[t][2]))\n",
     '        return rel(X[t], cells(prod["X0c"][2]))\n', "test_r4_reads_each_closure_against_its_familys_truth"),
    ("R4 prior without the null", RD, "    a_prior = np.maximum(np.abs(D1) - np.abs(Dp), 0.0)\n",
     "    a_prior = np.abs(D1)\n", "test_r4_at_the_prior_subtracts_the_refit_null"),
    ("R4 prior unclipped", RD, "    a_prior = np.maximum(np.abs(D1) - np.abs(Dp), 0.0)\n",
     "    a_prior = np.abs(D1) - np.abs(Dp)\n", "test_r4_prior_stores_the_clipped_excess_it_classes"),
    ("only W0 licenses", RD, 'all(v in ("W0", "W1") for v in attributable.values())', 'all(v == "W0" for v in attributable.values())',
     "test_r4_in_w1_still_licenses"),
    ("R4 q3 left out of the outcome", RD, 'for t in ("prior", "gibuu", "q3")}', 'for t in ("prior", "gibuu")}',
     "test_r4_q3_and_the_weight_at_the_prior"),
    ("the weight made an outcome change", RD, 'for t in ("prior", "gibuu", "q3")}',
     'for t in ("prior", "gibuu", "q3", "weight_at_prior")}', "test_r4_q3_and_the_weight_at_the_prior"),
    ("R2 against X0", RD, '    d2 = rel(X["X1w"], X["X1"])\n', '    d2 = rel(X["X1w"], X["X0"])\n',
     "test_r2_classes_x1w_against_x1_and_only_qualifies"),
    ("R3 reads the first iteration", RD, '["transfer_records"][-1]["cell_bias"]\n    t0', '["transfer_records"][0]["cell_bias"]\n    t0',
     "test_r3_reads_the_last_iteration_and_the_difference"),
    ("R3 difference drops a missing cell", RD, "    td = [None if a is None or b is None else a - b for a, b in zip(t1, t0)]\n",
     "    td = [0.0 if a is None or b is None else a - b for a, b in zip(t1, t0)]\n",
     "test_r3_reads_the_last_iteration_and_the_difference"),
    ("loop-untouched always true", RD, '"X1t_equals_X1_bitwise": same_bits(prod["X1t"][1], prod["X1"][1])',
     '"X1t_equals_X1_bitwise": True', "test_r3_reports_bitwise_whether_the_probe_left_the_loop_untouched"),
    ("the sentence transliterated", RD, "adding E_ν, the true vertex", "adding E_nu, the true vertex",
     "test_the_licensed_and_outcome_sentences_are_section_4s_characters"),
]


def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the files under test. Returns its rdx/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "rdx":
            (nd / e.name).symlink_to(e)
    rd = nd / "rdx"
    rd.mkdir()
    for e in HERE.iterdir():
        if e.name not in FILES:
            (rd / e.name).symlink_to(e)
    for f in FILES:
        (rd / f).write_bytes((HERE / f).read_bytes())
    return rd


def run_suite(rd: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/rdx/test_rdx_read.py"], cwd=rd.parents[1],
                       capture_output=True, text=True, timeout=1800)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_suite(mirror(Path(d)))
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-3000:])
        return 1
    print(f"unmutated suite: {ran.group(1)} tests OK, in the mirrored tree")
    todo = [m for m in MUTATIONS if not a.only or a.only in m[0]]
    ok = True

    def one(m):
        label, fname, old, new, test = m
        src = (HERE / fname).read_text()
        if src.count(old) != 1:
            return label, test, None, f"anchor occurs {src.count(old)} times"
        with tempfile.TemporaryDirectory() as d:
            rd = mirror(Path(d))
            (rd / fname).write_text(src.replace(old, new))
            _, out = run_suite(rd)
        return label, test, failing(out), ""

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
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(todo)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
