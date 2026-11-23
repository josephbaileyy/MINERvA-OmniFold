"""Hand mutants for covfix_core.py and covfix_p0.py: each must be killed (the unit tests fail).

  python3 -B covfix_mutation.py            prints one line per mutant and exits 0 only if all are killed

Each run copies the module and its tests into a fresh temp tree laid out like the repo (<tmp>/2d-unfolding/covfix/),
with nd-unfolding, 2d-unfolding/pv2d and docs linked read-only to the real checkout, so nothing beside this file is
touched. The unmutated copy must pass first.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FILES = ("covfix_core.py", "covfix_p0.py", "test_covfix_core.py", "test_covfix_p0.py")
C, P = "covfix_core.py", "covfix_p0.py"
MUTANTS = [
    ("rank-cut", C, "RANK_CUT = 1e-12 ", "RANK_CUT = 1e-11 "),
    ("well-cut", C, "WELL_CUT = 1e-6 ", "WELL_CUT = 1e-5 "),
    ("near-tie", C, "NEAR_TIE = 1e-9 ", "NEAR_TIE = 1e-8 "),
    ("psd-tol", C, "PSD_TOL = 1e-12 ", "PSD_TOL = 1e-11 "),
    ("residual-bar", C, "RESIDUAL_MAX = 0.1 ", "RESIDUAL_MAX = 0.2 "),
    ("label-lo", C, "LABEL_LO, LABEL_HI = 0.8, 1.25", "LABEL_LO, LABEL_HI = 0.75, 1.25"),
    ("label-hi", C, "LABEL_LO, LABEL_HI = 0.8, 1.25", "LABEL_LO, LABEL_HI = 0.8, 1.3"),
    ("band-min", C, "BAND_MIN = 10", "BAND_MIN = 11"),
    ("sym-dropped", C, "    return 0.5 * (C + C.T)\n", "    return C\n"),
    ("carry-zero-allowed", C, "bad = ~np.isfinite(d) | (d == 0)", "bad = ~np.isfinite(d)"),
    ("carry-one-sided", C, "return d[:, None] * np.asarray(V, np.float64) * d[None, :]",
     "return d[:, None] * np.asarray(V, np.float64)"),
    ("psd-zero-bar", C, 'rec["pass"] = bool(lam[0] >= -PSD_TOL * top)', 'rec["pass"] = bool(lam[0] >= 0)'),
    ("no-sign-fix", C, "    return U * s\n", "    return U\n"),
    ("ascending", C, 'order = np.argsort(lam, kind="stable")[::-1]', 'order = np.argsort(lam, kind="stable")'),
    ("no-tie-canon", C, "        if j - i > 1:\n", "        if j - i > 99:\n"),
    ("gs-null-skip", C, "        if nc > GS_NULL:\n", "        if nc >= 0:\n"),
    ("gs-tol-fixed", C, "GS_NULL = 100.0 * EPS ", "GS_NULL = 1e-10 "),
    ("evr-raw", C, '        lam, U = sl.eigh(S, driver="evr")\n',
     '        lam, U = sl.eigh(S, driver="evr")\n        return lam[::-1], U[:, ::-1]\n'),
    ("kept-nonstrict", C, "return np.asarray(lam) > RANK_CUT * float(lam1_F)",
     "return np.asarray(lam) >= RANK_CUT * float(lam1_F)"),
    ("band-edge-73", C, "band[rank <= 73] = 0", "band[rank <= 72] = 0"),
    ("band-edge-139", C, "band[rank <= 139] = 1", "band[rank <= 140] = 1"),
    ("cluster-goes-high", C, "band[start:i] = band[start]", "band[start:i] = band[i - 1]"),
    ("guard-ddof0", C, "se = float(psi.std(ddof=1) / math.sqrt(n))", "se = float(psi.std(ddof=0) / math.sqrt(n))"),
    ("guard-t95", C, "stats.t.ppf(0.975, n - 1)", "stats.t.ppf(0.95, n - 1)"),
    ("guard-zero-se-ok", C, "if not (math.isfinite(se) and se > 0):", "if not math.isfinite(se):"),
    ("label-lo-strict", C, "if lo >= LABEL_LO and hi <= LABEL_HI:", "if lo > LABEL_LO and hi <= LABEL_HI:"),
    ("label-over-nonstrict", C, "    if hi < LABEL_LO:\n", "    if hi <= LABEL_LO + 1e-15:\n"),
    ("no-kept-allowed", C, '    if ndf == 0:\n        raise Refusal("readings: no kept mode")\n', "    if False:\n        pass\n"),
    ("v-ddof1", C, "v = ((Z - m) ** 2).mean(axis=0)", "v = ((Z - m) ** 2).sum(axis=0) / (N - 1)"),
    ("cut-on-V", C, "    lamF1 = lambda_1(V_F)\n    keep = kept_mask(lam, lamF1)\n",
     "    lamF1 = lambda_1(V)\n    keep = kept_mask(lam, lamF1)\n"),
    ("band-psi-ndf", C, '"guard": guard(np.sum(Z[:, sel] ** 2, axis=1) / nb),', '"guard": guard(np.sum(Z[:, sel] ** 2, axis=1) / ndf),'),
    ("band-stats-for-dropped", C, "        if nb >= BAND_MIN:\n", "        if nb >= 0:\n"),
    ("evr-zero-den", C, "    ok = (den > 0) & ~differs\n", "    ok = (den >= 0) & ~differs\n"),
    ("well-on-V", C, "    lamF1 = lambda_1(F_ref)\n    well", "    lamF1 = lambda_1(V_ref)\n    well"),
    ("frobenius", C, "resid = float(np.linalg.norm(R, 2)) if", "resid = float(np.linalg.norm(R)) if"),
    ("undirected", C, "    Uw = U_r[:, well]\n    R = Uw - Uk @ (Uk.T @ Uw)\n",
     "    Uw = U_r[:, well]\n    R = Uk - Uw @ (Uw.T @ Uk)\n"),
    ("jsonable-nan", C, "return float(o) if math.isfinite(float(o)) else None", "return float(o)"),
    ("q-id-no-cpl", P, 'np.array_equal(Z["Q"], Z["s5_total"] + Z["C_PL"])', 'np.array_equal(Z["Q"], Z["s5_total"])'),
    ("s5-id-dropped", P, 'np.array_equal(Z["s5_total"],\n', 'True or np.array_equal(Z["s5_total"],\n'),
    ("a0-loose", P, 'rel <= t["tol"])', "rel <= 1.0)"),
    ("a0-no-ndf", P, 'rec["pass"] = bool(ndf == committed["ndf"] and', 'rec["pass"] = bool('),
    ("psd-no-stop", P, "    if bad:\n", "    if False:\n"),
    ("psd-reference-only", P, '            blocks |= {f"C_T({T})": B["C_T"],', '            blocks |= {} and {f"C_T({T})": B["C_T"],'),
    ("g2r-map-dropped", P, '"G2R x_T = blocks x_T": bool(np.array_equal(G["x_T"], B["x_T"]))', '"G2R x_T = blocks x_T": True'),
    ("g2r-rep-dropped", P, '"G2R rep = blocks rep": bool(np.array_equal(G["rep"], B["rep"])),', '"G2R rep = blocks rep": True,'),
    ("vf-uncarried", P, '"Q_T": cc.carry(Z["Q"], d),', '"Q_T": Z["Q"],'),
    ("pair-no-crun", P, 'args = (B["C_T"], dv["F_T"], B["C_T"] + dv["C_run"], dv["F_T"] + dv["C_run"])',
     'args = (B["C_T"], dv["F_T"], B["C_T"], dv["F_T"] + dv["C_run"])'),
    ("pair-fnew-no-crun", P, 'args = (B["C_T"], dv["F_T"], B["C_T"] + dv["C_run"], dv["F_T"] + dv["C_run"])',
     'args = (B["C_T"], dv["F_T"], B["C_T"] + dv["C_run"], dv["F_T"])'),
    ("fire-not-stop", P, "        if fired:\n", "        if False:\n"),
    ("ibukt-no-xR", P, 'b = np.asarray(rec[E_R_METHOD]["mean"], np.float64) * x_R',
     'b = np.asarray(rec[E_R_METHOD]["mean"], np.float64)'),
    ("ibukt-preflight-no-check", P, 'if [int(c) for c in rec["cells"]] != [int(c) for c in cells] or', "if False and"),
    ("residual-bar-nonstrict", C, '"fires": bool(resid > RESIDUAL_MAX)', '"fires": bool(resid >= RESIDUAL_MAX)'),
    ("well-angle-to-kept", C, "principal_angles_deg(Uw, U_n[:, well_n])", "principal_angles_deg(Uw, Uk)"),
    ("below-well-kept-only", C, "    tail = ~well\n", "    tail = kept_r & ~well\n"),
    ("evr-partition-ignored", C, "    for i, j in g1 ^ g2:\n", "    for i, j in set():\n"),
    ("spread-guard-mean-psi", C, "guard(infl.sum(axis=1) / ndf, X=float(v.mean()), labelled=False)",
     "guard(infl.sum(axis=1) / ndf, labelled=False)"),
    ("gs-null-n-scaled", C, "GS_NULL = 100.0 * EPS ", "GS_NULL = 10.0 * 205 * EPS "),
    ("gs-out-of-coords", C, "    return U @ np.column_stack(B)\n", "    return U @ np.column_stack(B) + 1e-9\n"),
    ("evr-refusal-raises", C, "    except Refusal as e:\n        rec |= {", "    except KeyError as e:\n        rec |= {"),
    ("a0-no-positive-ok", P, "    if not lam.max() > 0:\n        raise Stop(", "    if False:\n        raise Stop("),
    ("scoped-raises", P, "    except cc.Refusal as e:\n        return {\"refused\"", "    except KeyError as e:\n        return {\"refused\""),
    ("psd-no-rebuilt", P, '                       f"C_model_abs rebuilt({T})": dv["Cm_T_rebuilt"],\n', ""),
    ("out-not-exclusive", P, 'with open(a.out, "x") as f:', 'with open(a.out, "w") as f:'),
    ("c2-uncarried", P, '(("carried_to_tune", cc.carry(C_PL, d)),', '(("carried_to_tune", C_PL),'),
    ("c2-cut-drops-second", P, "zip(lam[:2], U[:, :2].T)", "zip(lam[lam > 1e-12 * lam[0]], U[:, lam > 1e-12 * lam[0]].T)"),
    ("c2-share-zero", P, '"share_of_ebar2": p * p / n2 if n2 > 0 else None', '"share_of_ebar2": p * p / n2 if n2 >= 0 else None'),
    ("g2r-unpinned", P, '"G": load_npz(pinned(gp, G2R_SHA[T])),', '"G": load_npz(gp),'),
    ("pin-oserror", P, '        raise Stop(f"C-PIN: {path} cannot be read ({e})") from e\n', "        raise\n"),
    ("rc-stop-0", P, 'return 0 if rec["status"] == "done (pre-W1 part)" else 3', "return 0"),
]


def tree(tmp: Path) -> Path:
    d = tmp / "2d-unfolding" / "covfix"
    d.mkdir(parents=True)
    for f in FILES:
        shutil.copy2(HERE / f, d / f)
    os.symlink(REPO / "nd-unfolding", tmp / "nd-unfolding")
    os.symlink(REPO / "2d-unfolding" / "pv2d", tmp / "2d-unfolding" / "pv2d")
    os.symlink(REPO / "docs", tmp / "docs")
    return d


def run_tests(d: Path) -> tuple[int, str]:
    """(rc, the first failing or erroring test's line, or the last stderr line if none is named)."""
    env = dict(os.environ, OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_covfix_core.py", "test_covfix_p0.py"], cwd=d,
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                       timeout=600, text=True)
    lines = r.stderr.splitlines()
    named = [ln for ln in lines if ln.startswith(("FAIL: ", "ERROR: ")) and "_FailedTest" not in ln]
    if r.returncode != 0 and not named:                   # an import, discovery or crash failure, not a detection
        return -1, "HARNESS: " + (lines[-1] if lines else "no stderr")
    return r.returncode, (named[0] if named else (lines[-1] if lines else ""))


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        base, why = run_tests(tree(Path(td)))
    print(f"baseline rc {base} {why}")
    if base != 0:
        return 2
    survived = []
    for mid, f, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as td:
            d = tree(Path(td))
            src = (d / f).read_text()
            if src.count(old) != 1:
                print(f"{mid}: NOT APPLIED (pattern occurs {src.count(old)} times)")
                survived.append(mid)
                continue
            (d / f).write_text(src.replace(old, new))
            rc, why = run_tests(d)
        status = "killed" if rc > 0 else ("HARNESS FAILURE" if rc < 0 else "SURVIVED")
        if rc <= 0:
            survived.append(mid)
        print(f"{mid}: {status} (rc {rc}) {why}")
    print(f"{len(MUTANTS) - len(survived)}/{len(MUTANTS)} killed; survived or not applied: {survived}")
    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
