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
EXPECTED_TESTS = 18
MUTATIONS = [
    ("NC-X not checked", RD, '    if not np.array_equal(prod["X0"][1], prod["X0_lat"][1]):\n', "    if False:\n",
     "test_nc_x_refuses_and_reads_nothing"),
    ("sha not compared with the job's", RD, "        if got[task] != shas[task]:\n", "        if False:\n",
     "test_a_sha_that_is_not_the_jobs_refuses"),
    ("a missing log line allowed", RD, "    if missing:\n", "    if False:\n",
     "test_the_logs_must_print_each_task_exactly_once"),
    ("a duplicated log line allowed", RD, "            if task in seen:\n", "            if False:\n",
     "test_the_logs_must_print_each_task_exactly_once"),
    ("an undeclared product allowed", RD, "            if task not in names:\n", "            if False:\n",
     "test_the_logs_must_print_each_task_exactly_once"),
    ("identity not enforced", RD, '        if bad:\n            fail(f"{task}: ', '        if False:\n            fail(f"{task}: ',
     "test_a_product_that_is_not_its_declared_task_refuses"),
    ("background pin of X0_lat taken from RDX's", RD, '"bkg_dump_sha256": pins["lat_zero_bkg.npz" if lat else "lat_RDX_ALL_bkg.npz"]',
     '"bkg_dump_sha256": pins["lat_RDX_ALL_bkg.npz"]', "test_a_product_that_is_not_its_declared_task_refuses"),
    ("estimator parameters not compared", RD, '        if meta.get("estimator_params") != ref.get("estimator_params"):\n',
     "        if False:\n", "test_parameters_must_be_x0s"),
    ("transfer record count unchecked", RD, '    if spec["transfer"] and len(r.get("transfer_records") or []) != ITERS:\n',
     "    if False:\n", "test_a_transfer_step_needs_five_records"),
    ("the null not subtracted in R1", RD, "    e = np.abs(d1) - np.abs(dp)\n", "    e = np.abs(d1)\n",
     "test_the_excess_is_beyond_the_null"),
    ("half sigma read as one sigma", RD, "e > RR.HALF_SIGMA * sigma", "e > sigma",
     "test_an_excess_beyond_half_sigma_is_a_named_sensitivity"),
    ("refit null W2 not decisive", RD, '    if c1p == "W2":\n', '    if c1p == "W9":\n',
     "test_the_refit_null_at_w2_makes_r1_unattributable"),
    ("R4 read against X0's truth", RD, "        return rel(X[t], integ(xt))\n",
     '        return rel(X[t], integ(prod["X0c"][2]))\n', "test_r4_reads_each_closure_against_its_own_truth"),
    ("R4 prior without the null", RD, "    a_prior = np.abs(D1) - np.abs(Dp)\n", "    a_prior = np.abs(D1)\n",
     "test_r4_at_the_prior_subtracts_the_refit_null"),
    ("R4 q3 left out of the outcome", RD, 'for t in ("prior", "gibuu", "q3")}', 'for t in ("prior", "gibuu")}',
     "test_r4_q3_and_the_weight_at_the_prior"),
    ("the weight made an outcome change", RD, 'for t in ("prior", "gibuu", "q3")}',
     'for t in ("prior", "gibuu", "q3", "weight_at_prior")}', "test_r4_q3_and_the_weight_at_the_prior"),
    ("R2 against X0", RD, '    d2 = rel(X["X1w"], X["X1"])\n', '    d2 = rel(X["X1w"], X["X0"]) * 0 + 1.0\n',
     "test_r2_classes_x1w_against_x1"),
    ("R3 reads the first iteration", RD, '["transfer_records"][-1]["cell_bias"]\n    t0', '["transfer_records"][0]["cell_bias"]\n    t0',
     "test_r3_reads_the_last_iteration_and_the_difference"),
    ("R3 difference drops a missing cell", RD, "    td = [None if a is None or b is None else a - b for a, b in zip(t1, t0)]\n",
     "    td = [0.0 if a is None or b is None else a - b for a, b in zip(t1, t0)]\n",
     "test_r3_reads_the_last_iteration_and_the_difference"),
    ("loop-untouched always true", RD, '"X1t_equals_X1": bool(np.array_equal(prod["X1t"][1], prod["X1"][1]))',
     '"X1t_equals_X1": True', "test_r3_reports_whether_the_probe_left_the_loop_untouched"),
    ("a nonpositive reference allowed", RD, "    if np.any(b <= 0) or", "    if False and np.any(b <= 0) or",
     "test_a_nonpositive_reference_refuses"),
    ("sigma unchecked", RD, " or np.any(phi <= 0) or np.any(sigma <= 0):", ":",
     "test_phi_and_sigma_come_from_the_committed_records"),
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
