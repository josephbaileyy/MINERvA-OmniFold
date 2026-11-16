"""Mutation check of ll5d_d2.py's tests (the director's D2 request, 2026-11-12: mu_max of the rebuilt GEANT block
against LL5D's all C_T, descriptive). Each mutation plants one defect in a temporary copy of ll5d_d2.py, placed first
on sys.path, and runs the NAMED test, which must fail. Exit 0 only if every mutation is killed and the unmutated suite
runs all EXPECTED_TESTS and passes.

    python3 -B nd-unfolding/tests/ll5d_d2_mutation.py
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
TESTS = ND / "tests"
TEST = TESTS / "test_ll5d_d2.py"
SRC = ND / "ll5d_d2.py"
EXPECTED_TESTS = 11

MUTATIONS = [
    # --- the quantity
    ("MU the Pion band in G", 'GEANT = ("band:GEANT_Neutron", "band:GEANT_Proton")',
     'GEANT = ("band:GEANT_Pion", "band:GEANT_Proton")', "D2.test_mu_max_is_g_neutron_plus_proton_against_c_t_all"),
    ("MU against C_e alone", '    M = rm["C_T"]\n', '    M = rm["C_e"]\n',
     "D2.test_mu_max_is_g_neutron_plus_proton_against_c_t_all"),
    ("MU the minus2 reading", 'rm = ll5d_b.remade(a.unfolds, a.truth, s1, U, w, frac, "all")',
     'rm = ll5d_b.remade(a.unfolds, a.truth, s1, U, w, frac, "minus2")', "D2.test_mu_max_is_g_neutron_plus_proton_against_c_t_all"),
    ("MU the smallest eigenvalue", "    order = np.argsort(w)[::-1]\n", "    order = np.argsort(w)\n",
     "D2.test_gen_eig_is_geant_full_s"),
    ("MU the bound as 1 + mu", '"chi2_ratio_bound": float(1 / (1 - mu[0])),', '"chi2_ratio_bound": float(1 + mu[0]),',
     "D2.test_the_chi2_bound_holds_for_every_bias"),
    # --- the pins and the control
    ("PN the null digest unchecked", '    if inv.sha256_noatime(path) != want_sha256:\n', '    if False:\n',
     "D2.test_refusals"),
    ("PN the products unchecked",
     '    if nl.get("products_sha256") != ll5d_b.products_digest(a.unfolds, a.truth, ll5d_b.BLOCK_ROLES):\n',
     '    if False:\n', "D2.test_refusals"),
    ("PN the readout's null unchecked",
     '    if ro.get("truth") != a.truth or ro.get("null_sha256") != a.expect_null_sha256:\n',
     '    if ro.get("truth") != a.truth:\n', "D2.test_refusals"),
    ("PN made_from unchecked", '    if nl.get("made_from") != mc.made_from(a, U):\n', '    if False:\n', "D2.test_refusals"),
    ("CT the diagonal control only (the audit's M1)",
     "    passes = g is not None and all(v <= CONTROL_TOL for v in rel.values()) and all(exact.values())\n",
     "    passes = rel[\"realization_check\"] <= CONTROL_TOL\n", "D2.test_off_diagonals_changed_alone_fail_the_control"),
    ("CT a refused grade passes", "    passes = g is not None and all(", "    passes = all(",
     "D2.test_off_diagonals_changed_alone_fail_the_control"),
    ("CT the control's tolerance ignored", "all(v <= CONTROL_TOL for v in rel.values())", "True",
     "D2.test_a_readout_record_that_differs_fails_the_control"),
    ("CT the grade recomputed under another matrix", 'g, chk, _rule = ll5d_b.graded(E, rm["C_T"],',
     'g, chk, _rule = ll5d_b.graded(E, np.diag(np.diag(rm["C_T"])),', "D2.test_the_control_reproduces_the_readouts_full_matrix_statistics"),
    ("PN the S1 assembly unchecked", '(a.staged / "s1" / "s1_assembly.npz", a.expect_staged_s1_sha256, "staged S1 assembly"),\n                             ', '',
     "D2.test_refusals"),
    ("CT a failed control still graded", '    if not ctl["passes"]:\n        out["verdict"] = "INVALID"\n        return out\n',
     '', "D2.test_a_readout_record_that_differs_fails_the_control"),
    ("CT a missing check passes", '        raise Refusal(f"the readout\'s {truth}/all evaluation has no realization_check',
     '        return {"passes": True, "max_rel_diff": 0.0}\n        raise Refusal(f"the readout\'s {truth}/all evaluation has no realization_check',
     "D2.test_refusals"),
    # --- reads and exits
    ("NA a plain read of a record", "    with inv.open_noatime(path) as fh:\n        return json.loads(fh.read().decode())",
     "    with open(path, \"rb\") as fh:\n        return json.loads(fh.read().decode())",
     "D2.test_records_and_arrays_are_read_with_o_noatime_and_only_the_digest_reads_plainly"),
    ("EX the atime move dropped", '    return rc | (ll5d.ATIME_RC if rec["atime"]["moved"] else 0)', '    return rc',
     "D2.test_main_writes_the_record_once_and_a_refusal_is_invalid"),
    ("EX a refusal exits 0", "        return 5 | (ll5d.ATIME_RC if bad[\"atime\"][\"moved\"] else 0)", "        return 0",
     "D2.test_main_writes_the_record_once_and_a_refusal_is_invalid"),
    ("EX the record overwritten", '    if a.out.exists() or a.out.with_suffix(".invalid.json").exists():\n', '    if False:\n',
     "D2.test_main_writes_the_record_once_and_a_refusal_is_invalid"),
]

RUN = ("import runpy, sys; sys.path.insert(0, {tmp!r}); sys.argv = ['test_ll5d_d2.py'] + {names!r}; "
       "runpy.run_path({test!r}, run_name='__main__')")


def run(tmp: str, names: list) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(tmp=tmp, names=names, test=str(TEST))],
                          capture_output=True, text=True, env=env, cwd=str(TESTS))


def main() -> int:
    src = SRC.read_text()
    print(f"ll5d_d2.py sha256 {hashlib.sha256(src.encode()).hexdigest()}")
    print(f"test_ll5d_d2.py sha256 {hashlib.sha256(TEST.read_bytes()).hexdigest()}")
    ok = True
    with tempfile.TemporaryDirectory(prefix="ll5d-d2-mut-") as tmp:
        shutil.copy(SRC, Path(tmp) / "ll5d_d2.py")
        base = run(tmp, [])
        m = re.search(r"Ran (\d+) tests", base.stderr)
        n = int(m.group(1)) if m else -1
        skipped = "skipped" in base.stderr
        base_ok = base.returncode == 0 and n == EXPECTED_TESTS and not skipped
        print(f"UNMUTATED {'PASS' if base_ok else 'FAIL'} tests={n} expected={EXPECTED_TESTS} skipped={skipped} "
              f"rc={base.returncode}")
        ok &= base_ok
        for name, old, new, test in MUTATIONS:
            if src.count(old) != 1:
                print(f"MUTATION NOT-APPLICABLE {name}: the anchor occurs {src.count(old)} times")
                ok = False
                continue
            mutated = src.replace(old, new)
            (Path(tmp) / "ll5d_d2.py").write_text(mutated)
            p = run(tmp, [test])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{test}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
