"""Single-site mutants of regrade_crep.py and ll5d_regrade_capture.py; each must make the test suite fail.

    python3 -B regrade_mutation.py      (prints one line per mutant and 'killed k of n'; exit 0 only if all killed)
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MUTANTS = [
    ("regrade_crep.py", "    M_full = M + tau\n", "    M_full = M\n"),
    ("regrade_crep.py", "    under = read_rule(M_full, se)", "    under = read_rule(M, se)"),
    ("regrade_crep.py", "    return (M_full - 1.0) > READING_SE * se", "    return (M_full - 1.0) >= READING_SE * se"),
    ("regrade_crep.py", "    return (M_full - 1.0) > READING_SE * se", "    return abs(M_full - 1.0) > READING_SE * se"),
    ("regrade_crep.py", "READING_SE = 3.0", "READING_SE = 2.0"),
    ("regrade_crep.py", "se = float(chi2.std(ddof=1) / math.sqrt(n) / ndf)", "se = float(chi2.std(ddof=0) / math.sqrt(n) / ndf)"),
    ("regrade_crep.py", "tau = float(fn.chi2_nonnull(U.T, Cp)[0] @ mu / ndf)", "tau = float(np.trace(C_add) / ndf)"),
    ("regrade_crep.py", '"spread_part": M - mean_err', '"spread_part": M'),
    ("regrade_crep.py", "    r = np.asarray(x_num, np.float64) / np.asarray(x_den, np.float64)\n", "    r = np.asarray(x_num, np.float64) / np.asarray(x_num, np.float64)\n"),
    ("regrade_crep.py", "    return X[:, None] * np.asarray(P_rel, np.float64) * X[None, :]", "    return np.asarray(P_rel, np.float64)"),
    ("regrade_crep.py", '    b = {k: v for k, v in B.items() if k != "C_T_minus"}', "    b = dict(B)"),
    ("regrade_crep.py", '    b["C08"] = B["C08"] + C_run', '    b["C08"] = B["C08"]'),
    ("regrade_crep.py", "A0_CHI2_REL = 1e-9", "A0_CHI2_REL = 1e-3"),
    ("regrade_crep.py", '    a = {k: (g[k], committed[k], g[k] == committed[k]) for k in ("ndf", "joint_count", "counts")}', '    a = {k: (g[k], committed[k], g[k] == committed[k]) for k in ("ndf", "counts")}'),
    ("regrade_crep.py", '    out["c_reading"] = "equal" if all(out["c"].values()) else "null redraw differs"', '    out["c_reading"] = "equal"'),
    ("regrade_crep.py", "    if asym > SYM_TOL or lam[0] < -PSD_TOL * lam[-1]:", "    if asym > SYM_TOL:"),
    ("regrade_crep.py", '            warnings.simplefilter("error", RuntimeWarning)', '            warnings.simplefilter("ignore", RuntimeWarning)'),
    ("regrade_crep.py", '    out["verdict"] = "descriptive-" + g["verdict"]', '    out["verdict"] = g["verdict"]'),
    ("ll5d_regrade_capture.py", "    bad = [r[2] for r in rows if inv.sha256_noatime(Path(r[2])) != r[1]]", "    bad = []"),
    ("ll5d_regrade_capture.py", '    if inv.sha256_noatime(s1_path) != S1_SHA:', '    if False:'),
    ("ll5d_regrade_capture.py", "    if have != want:", "    if not have <= want:"),
    ("ll5d_regrade_capture.py", "    if moved or changed:", "    if changed:"),
    ("ll5d_regrade_capture.py", "            if E.shape != (N_TOYS, N_CELLS) or not np.all(np.isfinite(E)):", "            if not np.all(np.isfinite(E)):"),
    ("ll5d_regrade_capture.py", "        for p in a.out.glob(\"capture_*.npz\"):\n            p.unlink()\n", "        pass\n"),
]

def main():
    killed = 0
    for i, (f, old, new) in enumerate(MUTANTS):
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            for name in ("regrade_crep.py", "ll5d_regrade_capture.py", "test_regrade_crep.py", "test_ll5d_regrade_capture.py"):
                shutil.copy(HERE / name, t / name)
            s = (t / f).read_text()
            assert s.count(old) == 1, (i, f, old)
            (t / f).write_text(s.replace(old, new))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_regrade_crep.py", "test_ll5d_regrade_capture.py"],
                               cwd=t, capture_output=True, text=True,
                               env={"PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": "1",
                                    "PYTHONPATH": str(HERE.parents[6] / "nd-unfolding") + ":" + str(HERE.parents[6] / "2d-unfolding" / "cov2d")})
            ok = r.returncode != 0
            killed += ok
            print(f"m{i:02d} {'KILLED' if ok else 'SURVIVED'} {f}: {old.strip()[:70]!r}")
    print(f"killed {killed} of {len(MUTANTS)}")
    return 0 if killed == len(MUTANTS) else 1

if __name__ == "__main__":
    sys.exit(main())
