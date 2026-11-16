"""Mutation check of LL5D amendment A1b.1's tests (the director's ruling of 2026-11-10: a bound bitwise comparison of the
four procedure controls, with a mutant in which one flipped ulp must read FAIL). Each mutation plants one defect in a
temporary copy of ll5d_ctl.py, placed first on sys.path, and runs the NAMED test, which must fail. Exit 0 only if every
mutation is killed and the unmutated suite runs all EXPECTED_TESTS and passes.

    python3 -B nd-unfolding/tests/ll5d_a1b1_mutation.py
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
TEST = TESTS / "test_ll5d_ctl.py"
SRC = ND / "ll5d_ctl.py"
EXPECTED_TESTS = 16

MUTATIONS = [
    # --- the bitwise rule (the director's REQUIRED mutant: one flipped ulp must FAIL)
    ("BW a tolerance in place of the bytes", "equal = bool(same_dtype and same_shape and a.tobytes() == b.tobytes())",
     "equal = bool(same_shape and np.allclose(np.asarray(a, np.float64), np.asarray(b, np.float64)))",
     "Bitwise.test_one_flipped_ulp_fails"),
    ("BW the dtype unchecked", "equal = bool(same_dtype and same_shape and a.tobytes() == b.tobytes())",
     "equal = bool(same_shape and np.array_equal(np.asarray(a, np.float64), np.asarray(b, np.float64)))",
     "Bitwise.test_a_dtype_change_fails_even_with_equal_values"),
    ("BW the shape unchecked", "equal = bool(same_dtype and same_shape and a.tobytes() == b.tobytes())",
     "equal = bool(same_dtype and a.tobytes() == b.tobytes())",
     "Bitwise.test_a_shape_change_fails_with_the_same_bytes"),
    ("BW one control enough", "    passes = all(r[\"equal\"] for r in rows.values())",
     "    passes = any(r[\"equal\"] for r in rows.values())", "Bitwise.test_one_flipped_ulp_fails"),
    ("BW the product compared with itself", "**compare(_array(prod_raw, prod_path), _array(ref_raw, ref_path))}",
     "**compare(_array(prod_raw, prod_path), _array(prod_raw, prod_path))}", "Bitwise.test_one_flipped_ulp_fails"),
    # --- the references
    ("RF the reference digest unchecked", "        if ref_sha != want:\n", "        if False:\n",
     "Refusals.test_a_reference_digest_mismatch_is_invalid"),
    ("RF the control list unchecked", "    if tuple(REFERENCES) != tuple(ll5d_b.CONTROLS):\n", "    if False:\n",
     "Refusals.test_the_references_must_be_exactly_the_declared_controls"),
    ("RF MaRES_0 against MaRES_1", "\"MaRES_0\": (f\"{S1_DIR}/S1_MaRES_0.npz\", \"aa3ed226",
     "\"MaRES_0\": (f\"{S1_DIR}/S1_MaRES_1.npz\", \"aa3ed226", "Pins.test_the_pins_are_the_committed_files_and_s1s_sha256sums"),
    ("RF set A at replica 2", "\"setA_b1\": (f\"{S1_DIR}/data_b1_j101.npz\"", "\"setA_b1\": (f\"{S1_DIR}/data_b2_j102.npz\"",
     "Pins.test_the_set_a_reference_is_replica_1_at_jitter_101"),
    # --- the exit codes and the reads
    ("EX FAIL exits 0", "    return (0 if rec[\"verdict\"] == \"PASS\" else RC_FAIL)", "    return (0 if rec[\"verdict\"] else RC_FAIL)",
     "ExitCodes.test_pass_fail_and_invalid_codes_and_records"),
    ("EX the atime move dropped", "    return (0 if rec[\"verdict\"] == \"PASS\" else RC_FAIL) | (ll5d_b.ll5d.ATIME_RC if rec[\"atime\"][\"moved\"] else 0)",
     "    return (0 if rec[\"verdict\"] == \"PASS\" else RC_FAIL)", "ExitCodes.test_an_atime_move_ors_in_8"),
    ("NA a plain read", "    with inv.open_noatime(path) as fh:\n        raw = fh.read()\n    return raw,",
     "    with open(path, \"rb\") as fh:\n        raw = fh.read()\n    return raw,", "NoAtime.test_every_read_goes_through_o_noatime"),
]

RUN = ("import runpy, sys; sys.path.insert(0, {tmp!r}); sys.argv = ['test_ll5d_ctl.py'] + {names!r}; "
       "runpy.run_path({test!r}, run_name='__main__')")


def run(tmp: str, names: list) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1")
    return subprocess.run([sys.executable, "-B", "-c", RUN.format(tmp=tmp, names=names, test=str(TEST))],
                          capture_output=True, text=True, env=env, cwd=str(TESTS))


def main() -> int:
    src = SRC.read_text()
    print(f"ll5d_ctl.py sha256 {hashlib.sha256(src.encode()).hexdigest()}")
    print(f"test_ll5d_ctl.py sha256 {hashlib.sha256(TEST.read_bytes()).hexdigest()}")
    ok = True
    with tempfile.TemporaryDirectory(prefix="ll5d-ctl-mut-") as tmp:
        shutil.copy(SRC, Path(tmp) / "ll5d_ctl.py")
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
            (Path(tmp) / "ll5d_ctl.py").write_text(mutated)
            p = run(tmp, [test])
            killed = p.returncode != 0
            print(f"MUTATION {'KILLED' if killed else 'SURVIVED'} {name} [{test}] "
                  f"sha256={hashlib.sha256(mutated.encode()).hexdigest()[:16]}")
            ok &= killed
    print("ALL-KILLED" if ok else "MUTATION-CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
