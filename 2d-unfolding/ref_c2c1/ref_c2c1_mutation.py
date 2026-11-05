#!/usr/bin/env python3
"""Mutation check of REF-C2C1's tests (REF-C2C1-DECLARATION.md §4: "a mutation harness with a mutant per control, bar
and pairing key"; REF-C2C1-BINDING-1.md ruling 3).

Each mutation plants one defect in ``ref_c2c1.py`` or ``ref_c2c1_read.py`` and must make its NAMED test fail or
error. The modules locate the repository from their own path, so a mutation is written in place and the original
restored after it; the harness refuses to finish unless every file's sha256 is back to what it was. Run it in the
tests' environment (PyROOT, LightGBM, scikit-learn, scipy, matplotlib), pinned as RE-2's suite says.

    python3 -B 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST = HERE / "test_ref_c2c1.py"
D, R = "ref_c2c1.py", "ref_c2c1_read.py"
EXPECTED_TESTS = 17  # a run that stops early exits 0 with fewer: refuse it (one C-ROO test skips without RooUnfold)
MUTATIONS = [
    # the IBU seam and the driver
    ("IBU's per-event factor not unfolded/prior", D, "    factor = np.divide(u, T, out=np.ones_like(u), where=T > 0)",
     "    factor = np.ones_like(u)", "Driver.test_c2_is_e_rs_pipeline_with_ibu_in_the_omnifold_seam"),
    ("the measured histogram not E_R's refined weights", D,
     "y = np.bincount(rm[rm >= 0], weights=np.asarray(w_meas, float)[rm >= 0], minlength=n)",
     "y = np.bincount(rm[rm >= 0], minlength=n).astype(float)",
     "Driver.test_c2_is_e_rs_pipeline_with_ibu_in_the_omnifold_seam"),
    ("C-SIM's tolerance loosened", D, "    return {\"max_rel\": worst, \"pass\": bool(worst <= rtol and",
     "    return {\"max_rel\": worst, \"pass\": bool(worst <= 1.0 and", "Ibu.test_c_sim_fires_on_a_chain_defect"),
    ("c1's keys not merged", D, "                params = {**params, **(extra or {})}", "                params = dict(params)",
     "Driver.test_c1_differs_from_e_r_by_exactly_the_four_keys"),
    ("a unit skipped whatever its verdict", D, '        if verdict == "PASS":\n            return 0',
     "        if True:\n            return 0", "Driver.test_a_unit_without_a_pass_marker_is_never_done"),
    ("the replica set not bound", D, '    if rs["choice"] not in rs["options"]:', "    if False:",
     "Units.test_the_replica_set_is_bound_at_step_two"),
    # pairing keys
    ("a replica's bootstrap seed not E_R's", D, '        argv += [x.format(b=b) for x in e["replica_argv_extra"]]',
     '        argv += [x.format(b=b + 1) for x in e["replica_argv_extra"]]',
     "Units.test_the_argv_is_e_rs_and_a_replica_adds_its_streams"),
    # the rank rule and the null
    ("the rank rule not N / 4", R, '    return n // int(cfg["readings"]["rank_divisor"])', "    return n // 2",
     "Readings.test_the_rank_rule"),
    ("the null in-sample, not leave-one-out", R, "        rest = np.delete(D, i, axis=0)\n", "        rest = D\n",
     "Readings.test_the_leave_one_out_null_on_a_known_answer"),
    # per reading bar
    ("C2-R2's input side one-sided", R, "    if a <= lo and hi <= b:", "    if a <= lo:",
     "Readings.test_the_rho_classes_at_their_bars"),
    ("C2-R2's algorithm side without C2-R1 differ", R, '    if hi <= alg and c2r1 == "differ":', "    if hi <= alg:",
     "Readings.test_the_rho_classes_at_their_bars"),
    ("C2-R2's interval read as a point", R,
     "        lo, hi = float(np.quantile(rho_r, q)), float(np.quantile(rho_r, 1 - q))",
     "        lo = hi = float(np.median(rho_r))", "Readings.test_the_readings_on_known_products"),
    # per control
    ("a failed control flagged and the read continued", R, "    if failed:\n        stop", "    if False:\n        stop",
     "Controls.test_each_control_stops_the_read"),
    ("C-CV's tolerance loosened", R, '"pass": bool(rel(x_er_run, x_er) <= rd["e_r_rtol"])}',
     '"pass": bool(rel(x_er_run, x_er) <= 1e-3)}', "Controls.test_each_control_stops_the_read"),
    ("C-PUB's tolerance loosened", R, 'abs(d_er * ndf / c_pub["chi2"] - 1) <= c_pub["rtol"]',
     'abs(d_er * ndf / c_pub["chi2"] - 1) <= 1e-2', "Controls.test_each_control_stops_the_read"),
    ("C-SET passes anything", R, '    return {"pass": all(r["differ"] == sorted(keys) for r in rows), "constructions": rows}',
     '    return {"pass": True, "constructions": rows}', "Controls.test_each_control_stops_the_read"),
    ("C-REF's deterministic part dropped", R, 'for k in ("params", "signed_sum"))', 'for k in ("params",))',
     "Controls.test_each_control_stops_the_read"),
    ("C-SIM not carried into the read", R, '    for name in ("C-SIM", "C-ROO"):', '    for name in ("C-ROO",):',
     "Controls.test_each_control_stops_the_read"),
    ("a unit without a PASS marker read", R, '    controls["done"] = {"pass": not not_done,',
     '    controls["done"] = {"pass": True,', "Controls.test_each_control_stops_the_read"),
    ("C-IN unchecked", R, '    controls["C-IN"] = {"pass": C.sha256(e_r) == cfg["e_r"]["central_sha256"]}',
     '    controls["C-IN"] = {"pass": True}', "Controls.test_each_control_stops_the_read"),
    ("C-CELLS passes a different set", R, '        controls["C-CELLS"] = {"pass": False, "why": str(e)[:300]}',
     '        controls["C-CELLS"] = {"pass": True, "why": str(e)[:300]}',
     "Controls.test_the_cells_are_bound_index_by_index"),
    ("the cells' sha256 unchecked", R, "    if C.sha256(cells) != cells_sha:", "    if False:",
     "Controls.test_the_cells_are_bound_index_by_index"),
]


def digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def run(tests: list[str]) -> tuple[int, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "1"}
    p = subprocess.run([sys.executable, "-B", str(TEST), *tests], capture_output=True, text=True, cwd=str(HERE.parent),
                       env=env)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return {f"{c}.{t}" for t, c in re.findall(r"^(?:FAIL|ERROR): (\w+) \(\w+\.(\w+)\.\w+\)", out, re.M)}


def mutate(fname: str, old: str, new: str, tests: list[str]) -> tuple[int, str] | None:
    path = HERE / fname
    src = path.read_text()
    if src.count(old) != 1:
        return None
    try:
        path.write_text(src.replace(old, new))
        return run(tests)
    finally:
        path.write_text(src)


def main() -> int:
    before = {f: digest(f) for f in (D, R)}
    rc, out = run([])
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-2000:])
        return 1
    ok = True
    for label, fname, old, new, test in MUTATIONS:
        res = mutate(fname, old, new, [test])
        if res is None:
            print(f"MUTATION NOT APPLIED  {label}: anchor does not occur exactly once")
            ok = False
            continue
        killed = test in failing(res[1])
        ok &= killed
        print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:48s} by {test}")
    after = {f: digest(f) for f in (D, R)}
    if after != before:
        print("MODULES NOT RESTORED:", {f for f in before if before[f] != after[f]})
        return 1
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({len(MUTATIONS)} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
