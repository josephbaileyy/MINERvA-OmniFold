"""COV2D-BINDING-2 addendum A5 mutants: one guard or declared rule per mutant, over the A5 change in 1B's
fd_1b_mc.grade, cov2d_score.score, cov2d_readouts.leave_out_mec and cov2d_readout (the tolerance, its passthroughs, the
grade-refusal record). Run from a scratchpad with an interpreter that has PyROOT and numpy:
    TMPDIR=<dir> PYTHONDONTWRITEBYTECODE=1 python -B mutation_a5.py <worktree> [<mutant name> ...]
As mutation_a4.py: each mutant rewrites one text of one file (it must occur once, or it counts as not killed), runs the
test sets, and restores it; a kill counts only on a test failure (rc != 0). The test sets are the classes the A5 change
touches, named so that environment-only errors elsewhere in a module (numpy-2 reprs, absent uproot) cannot count as
kills; the unmutated tree must pass them first (BASELINE), or the run stops. Exits 1 unless every mutant is killed, and
names any REQUIRED mutant that was not."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
F = "nd-unfolding/fd_1b_mc.py"
S = "2d-unfolding/cov2d/cov2d_score.py"
O = "2d-unfolding/cov2d/cov2d_readouts.py"
R = "2d-unfolding/cov2d/cov2d_readout.py"
SETS = [("nd-unfolding/tests", ["test_fd_1b_mc.CholeskyTolerance", "test_fd_1b_mc.Grading"]),
        ("2d-unfolding/cov2d/tests", ["test_cov2d_readout.CholeskyTolPure", "test_cov2d_readout.CholeskyA5",
                                      "test_cov2d_readout.PhaseS", "test_cov2d_score", "test_cov2d_readouts.LeaveOutMEC"])]
M = [
    # 1B's grade: the tolerance argument, its default and message, the compared values
    (F, "grade ignores chol_tol (1e-9 hard)", 'if compared["max_rel_diff"] > chol_tol:',
     'if compared["max_rel_diff"] > 1e-9:'),
    (F, "1B default changed to 1e-3", "null: dict, chol_tol: float = 1e-9,", "null: dict, chol_tol: float = 1e-3,"),
    (F, "1B refusal message changed", 'e = Refusal("the non-null chi2 and the Cholesky chi2 differ")',
     'e = Refusal("the chi2s differ")'),
    (F, "full-rank cross-check skipped", "    if ndf == C.shape[0]:\n        L = np.linalg.cholesky(C)",
     "    if False:\n        L = np.linalg.cholesky(C)"),
    (F, "refusal carries no compared values", "            e.compared = compared\n", ""),
    (F, "chol_out not filled at full rank", "        if chol_out is not None:\n            chol_out.update(compared)\n", ""),
    # the passthroughs
    (S, "cov2d_score drops the C_T passthrough", "g = mc.grade(E, C_T, null, chol_tol=chol_tol, chol_out=chol_out)",
     "g = mc.grade(E, C_T, null, chol_out=chol_out)"),
    (O, "leave_out_mec drops the C_T- passthrough",
     'g = mc.grade(E, blocks["C_T_minus"], null_minus, chol_tol=chol_tol, chol_out=chol_out)',
     'g = mc.grade(E, blocks["C_T_minus"], null_minus, chol_out=chol_out)'),
    # the driver: the tolerance from each matrix, passed and recorded
    (R, "tol without the factor 10", '"tol": max(1e-9, 10 * kappa * eps)}', '"tol": max(1e-9, kappa * eps)}'),
    (R, "tol without the 1e-9 floor", '"tol": max(1e-9, 10 * kappa * eps)}', '"tol": 10 * kappa * eps}'),
    (R, "kappa from the second-smallest eigenvalue", 'kappa = float(lam[-1] / lam[0]) if lam[0] > 0',
     'kappa = float(lam[-1] / lam[1]) if lam[0] > 0'),
    (R, "C_T- tolerance taken from C_T", 'rec["cholesky_check_minus"] = cholesky_tol(B["C_T_minus"])',
     'rec["cholesky_check_minus"] = cholesky_tol(B["C_T"])'),
    (R, "driver does not pass C_T's tolerance", 'chol_tol=rec["cholesky_check"]["tol"], chol_out=compared)',
     'chol_out=compared)'),
    (R, "driver does not pass C_T-'s tolerance", 'chol_tol=rec["cholesky_check_minus"]["tol"], chol_out=compared_minus)',
     'chol_out=compared_minus)'),
    (R, "compared values not recorded on a pass", '        rec["cholesky_check"]["compared"] = compared\n', ""),
    # the grade-refusal record (ruling 2, extended to both grades)
    (R, "grade refusal not caught", "        except mc.Refusal as e:      # addendum A5",
     "        except ZeroDivisionError as e:      # addendum A5"),
    (R, "a refusal does not finish Run", '            return run.finish(out, f"score_{truth}.invalid.json")',
     "            raise"),
    (R, "invalid record written as score_<T>.json", 'f"score_{truth}.invalid.json"', 'f"score_{truth}.json"'),
    (R, "a refusal's verdict is not INVALID",
     '            rec["verdict"] = "INVALID"\n            return run.finish(out, f"score_{truth}.invalid.json")',
     '            rec["verdict"] = "COVERS"\n            return run.finish(out, f"score_{truth}.invalid.json")'),
    (R, "the refusing grade is not named", '            which = "C_T_minus"\n', ""),
    (R, "compared values not recorded on a refusal", '            rec[key]["compared"] = getattr(e, "compared", None)\n', ""),
    (R, "no distinct INVALID line", '    if rec.get("grade_refusal"):', "    if False:"),
]
REQUIRED = {"grade ignores chol_tol (1e-9 hard)", "1B default changed to 1e-3", "1B refusal message changed",
            "full-rank cross-check skipped", "cov2d_score drops the C_T passthrough",
            "leave_out_mec drops the C_T- passthrough", "tol without the factor 10", "tol without the 1e-9 floor",
            "C_T- tolerance taken from C_T", "driver does not pass C_T's tolerance",
            "driver does not pass C_T-'s tolerance", "grade refusal not caught", "a refusal does not finish Run",
            "invalid record written as score_<T>.json", "no distinct INVALID line"}
assert REQUIRED <= {m[1] for m in M}
if sys.argv[2:]:
    unknown = set(sys.argv[2:]) - {m[1] for m in M}
    assert not unknown, f"no such mutant: {sorted(unknown)}"
    M = [m for m in M if m[1] in sys.argv[2:]]


def run_sets() -> int:
    rc = 0
    for cwd, ids in SETS:
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *ids], cwd=WT / cwd, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        rc |= r.returncode
        if rc:
            break
    return rc


if run_sets():
    print("BASELINE FAILED: the unmutated tree does not pass the test sets; nothing mutated")
    sys.exit(2)
print("BASELINE ok", flush=True)
bak = Path(os.environ["TMPDIR"])
files = sorted({m[0] for m in M})
for f in files:
    (bak / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(WT / f, bak / f)
killed, alive = 0, []
try:
    for f, name, a, b in M:
        src = (bak / f).read_text()
        if src.count(a) != 1:
            print(f"NOMATCH {f}: {name}", flush=True)
            alive.append(name)
            continue
        (WT / f).write_text(src.replace(a, b))
        rc = run_sets()
        killed += bool(rc)
        if not rc:
            alive.append(name)
        print(f"{'KILLED ' if rc else 'SURVIVED'} {Path(f).name}: {name}", flush=True)
        shutil.copy(bak / f, WT / f)
finally:
    for f in files:
        shutil.copy(bak / f, WT / f)
print(f"killed {killed} of {len(M)}")
if REQUIRED & set(alive):
    print(f"REQUIRED NOT KILLED: {sorted(REQUIRED & set(alive))}")
sys.exit(1 if alive else 0)
