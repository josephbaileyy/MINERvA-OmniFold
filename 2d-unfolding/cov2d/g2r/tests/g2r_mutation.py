"""Mutation check of COV2D-G2R's tests (COV2D-G2R-DECLARATION.md §9's required mutants, and one per control). Each
mutation plants one defect in one source file, runs the NAMED test, which must fail, and restores the file's exact
bytes. Exit 0 only if every mutation is killed, every anchor occurs once, the unmutated suites run all EXPECTED tests
and pass, and every source file is byte-identical to HEAD at the end.

    python3 -B 2d-unfolding/cov2d/g2r/tests/g2r_mutation.py

It mutates in place, so it refuses unless the three source files are clean against HEAD (run it in a clean checkout).
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
G2R = REPO / "2d-unfolding/cov2d/g2r/g2r.py"
READOUT = REPO / "2d-unfolding/cov2d/g2r/g2r_readout.py"
DRIVER = REPO / "2d-unfolding/re2/re2_driver.py"
T_G2R = REPO / "2d-unfolding/cov2d/g2r/tests/test_g2r.py"
T_DRV = REPO / "2d-unfolding/re2/tests/test_re2_miss_map.py"
EXPECTED = {T_G2R: 24, T_DRV: 8}

MUTATIONS = [
    # --- §9's required mutants
    ("the flag silently ignored (an all-NaN override)", DRIVER,
     "    override[miss] = col[truth]\n", "    pass\n", T_DRV, "MissMapLoader.test_the_override_from_the_map"),
    ("the override applied to a passing row", DRIVER,
     "                if passed:  # G2R\n", "                if False:  # G2R\n", T_DRV, "MissMapLoader.test_loader_guards"),
    ("a universe's override from another column (the CV w_truth)", DRIVER,
     "    branch = _universe_truth_branch(universe_branch)\n    if not t_truth_denom.GetBranch(branch):",
     "    branch = \"w_truth\"\n    if not t_truth_denom.GetBranch(branch):", T_DRV,
     "MissMapLoader.test_the_override_from_the_map"),
    ("eps on the full space, not the retained eigensystem", G2R,
     "    keep = lam > rel * lam.max()\n", "    keep = lam > -np.inf\n", T_G2R,
     "Readings.test_a_null_direction_does_not_enter_eps_and_coupling_sees_it"),
    ("the regrade reading the old C_T", READOUT,
     "    g = cs.score(E, new[\"C_T\"], null, truth, flat, weak, list(controls_failed), chol_tol=chol[\"tol\"])",
     "    g = cs.score(E, B[\"C_T\"], null, truth, flat, weak, list(controls_failed), chol_tol=chol[\"tol\"])", T_G2R,
     "RegradeCore.test_the_grade_reads_the_errors_against_c_t_prime"),
    ("the null left at the old laws", READOUT,
     "    res = cn.null_at_T(new, new[\"bands\"], B[\"minos_x\"], B[\"w_flux\"], **kw)",
     "    res = cn.null_at_T(new, {k[6:]: B[k] for k in B if k.startswith(\"band__\")}, B[\"minos_x\"], B[\"w_flux\"], **kw)",
     T_G2R, "RegradeCore.test_the_null_is_from_the_corrected_bands_and_c_t_prime"),
    # --- the alignment checks (G4)
    ("the subsequence order unchecked", G2R,
     "        check(f\"{name}_subsequence_order\", bool(np.all(np.diff(tidx) > 0)))",
     "        check(f\"{name}_subsequence_order\", True)", T_G2R, "Map.test_each_alignment_check_refuses"),
    ("the complement unchecked", G2R,
     "        check(f\"{name}_complement_eq_reco_rows_cv\", sorted_equal(",
     "        check(f\"{name}_complement_eq_reco_rows_cv\", True or sorted_equal(", T_G2R,
     "Map.test_each_alignment_check_refuses"),
    ("a miss row's proxy unchecked per universe", G2R,
     "    if not (np.array_equal(wt_s[miss_rows], w[miss_rows]) and np.array_equal(wr_s[miss_rows], w[miss_rows])):",
     "    if False:", T_G2R, "Map.test_universe_check_refuses_a_non_proxy_miss_and_a_complement_mismatch"),
    ("the override at the wrong truth rows", G2R,
     "np.asarray(wt_truth_u, np.float64)[np.asarray(truth_rows, np.int64)]",
     "np.asarray(wt_truth_u, np.float64)[np.asarray(miss_rows, np.int64)]", T_G2R,
     "Map.test_override_equals_p5_builder_semantics"),
    # --- G6 and G7
    ("C_T' with the lateral check dropped", G2R,
     "    if not (np.array_equal(C_lat, B[\"C_lat\"]) and np.array_equal(C_norm, B[\"C_norm\"])):",
     "    if False:", T_G2R, "CTPrime.test_a_tampered_lateral_block_refuses"),
    ("G7 ignoring the integer fields", READOUT,
     "    diff = [k for k in GRADE_EXACT if g_new.get(k) != g_old.get(k)]",
     "    diff = []", T_G2R, "ReadoutCores.test_grade_reproduction"),
    # --- the director's conditions on amendment 1 §2
    ("state carried between universes (a cached override)", DRIVER,
     "    return override, prov\n",
     "    if getattr(g2r_miss_override, \"_memo\", None) is None:\n        g2r_miss_override._memo = (override, prov)\n"
     "    return g2r_miss_override._memo\n",
     T_DRV, "MissMapLoader.test_no_state_is_carried_between_universes"),
    ("G11 comparing the override with itself", G2R,
     "        b = p5_override(S, T, blocks, col)\n", "        b = a\n", T_G2R, "Map.test_the_spot_check_passes_and_refuses"),
    ("part (a) not subtracting the old universe block", READOUT,
     "\"C_new\": np.asarray(Q, np.float64) - old + new}", "\"C_new\": np.asarray(Q, np.float64) + new}", T_G2R,
     "ReadoutCores.test_data_core_replaces_only_the_universe_bands"),
]

RUN = ("import runpy, sys; sys.argv = [{test!r}] + {names!r}; runpy.run_path({test!r}, run_name='__main__')")


def run(test: Path, names: list) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(test=str(test), names=names)], capture_output=True,
                          text=True, env=env, cwd=str(REPO))


def head_bytes(path: Path) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{path.relative_to(REPO)}"], check=True,
                          capture_output=True).stdout


def main() -> int:
    sources = (G2R, READOUT, DRIVER)
    for p in sources:
        if p.read_bytes() != head_bytes(p):
            print(f"REFUSED: {p.relative_to(REPO)} differs from HEAD; run in a clean checkout")
            return 2
    orig = {p: p.read_bytes() for p in sources}
    for p in sources:
        print(f"{p.relative_to(REPO)} sha256 {hashlib.sha256(orig[p]).hexdigest()}")
    ok = True
    for test, n_want in EXPECTED.items():
        base = run(test, [])
        m = re.search(r"Ran (\d+) tests", base.stderr)
        n = int(m.group(1)) if m else -1
        skipped = "skipped" in base.stderr
        good = base.returncode == 0 and n == n_want and not skipped
        print(f"UNMUTATED {'PASS' if good else 'FAIL'} {test.name} tests={n} expected={n_want} skipped={skipped} "
              f"rc={base.returncode}")
        ok &= good
    try:
        for name, path, old, new, test, case in MUTATIONS:
            src = orig[path].decode()
            if src.count(old) != 1:
                print(f"MUTATION NOT-APPLICABLE {name}: the anchor occurs {src.count(old)} times")
                ok = False
                continue
            mutated = src.replace(old, new)
            path.write_text(mutated)
            try:
                p = run(test, [case])
            finally:
                path.write_bytes(orig[path])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{case}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
    finally:
        for p in sources:
            p.write_bytes(orig[p])
    restored = all(p.read_bytes() == head_bytes(p) for p in sources)
    print(f"SOURCES RESTORED {'OK' if restored else 'FAIL'}")
    ok &= restored
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
