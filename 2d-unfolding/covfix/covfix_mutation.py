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
    ("carry-zero-allowed", C, "bad = ~np.isfinite(d) | (d == 0)", "bad = ~np.isfinite(d)"),
    ("carry-one-sided", C, "return d[:, None] * np.asarray(V, np.float64) * d[None, :]",
     "return d[:, None] * np.asarray(V, np.float64)"),
    ("psd-zero-bar", C, 'rec["pass"] = bool(lam[0] >= -PSD_TOL * top)', 'rec["pass"] = bool(lam[0] >= 0)'),
    ("no-sign-fix", C, "    return U * s\n", "    return U\n"),
    ("ascending", C, 'order = np.argsort(lam, kind="stable")[::-1]', 'order = np.argsort(lam, kind="stable")'),
    ("no-tie-canon", C, "        if j - i > 1:\n", "        if j - i > 99:\n"),
    ("gs-null-skip", C, "        if nv > 1e-10:\n", "        if nv >= 0:\n"),
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
    ("v-ddof1", C, "v = ((Z - m) ** 2).mean(axis=0)", "v = ((Z - m) ** 2).sum(axis=0) / (N - 1)"),
    ("cut-on-V", C, "    lamF1 = float(np.linalg.eigvalsh(np.asarray(V_F, np.float64))[-1])\n    keep = kept_mask(lam, lamF1)\n",
     "    lamF1 = float(np.linalg.eigvalsh(np.asarray(V, np.float64))[-1])\n    keep = kept_mask(lam, lamF1)\n"),
    ("band-psi-ndf", C, 'rec["guard"] = guard(np.sum(Z[:, sel] ** 2, axis=1) / nb)',
     'rec["guard"] = guard(np.sum(Z[:, sel] ** 2, axis=1) / ndf)'),
    ("well-on-V", C, "    lamF1 = float(np.linalg.eigvalsh(np.asarray(F_ref, np.float64))[-1])\n    well",
     "    lamF1 = float(np.linalg.eigvalsh(np.asarray(V_ref, np.float64))[-1])\n    well"),
    ("frobenius", C, "resid = float(np.linalg.norm(R, 2)) if", "resid = float(np.linalg.norm(R)) if"),
    ("undirected", C, "    Uw = U_r[:, well]\n    R = Uw - Uk @ (Uk.T @ Uw)\n",
     "    Uw = U_r[:, well]\n    R = Uk - Uw @ (Uw.T @ Uk)\n"),
    ("q-id-no-cpl", P, 'np.array_equal(Z["Q"], Z["s5_total"] + Z["C_PL"])', 'np.array_equal(Z["Q"], Z["s5_total"])'),
    ("a0-loose", P, 'rel <= t["tol"])', "rel <= 1.0)"),
    ("a0-no-ndf", P, 'rec["pass"] = bool(ndf == committed["ndf"] and', 'rec["pass"] = bool('),
    ("psd-no-stop", P, "    if bad:\n        raise Stop(f\"C-PSD: {bad}\")\n", "    if False:\n        pass\n"),
    ("g2r-map-dropped", P, '"G2R x_T = blocks x_T": bool(np.array_equal(G["x_T"], B["x_T"]))', '"G2R x_T = blocks x_T": True'),
    ("vf-uncarried", P, "K0_T, Q_T = cc.carry(K0, d), cc.carry(Q, d)", "K0_T, Q_T = cc.carry(K0, d), Q"),
    ("pair-no-crun", P, 'rr = cc.residual_rule(B["C_T"], F_T, B["C_T"] + C_run, F_T + C_run)',
     'rr = cc.residual_rule(B["C_T"], F_T, B["C_T"], F_T + C_run)'),
    ("pair-fnew-no-crun", P, 'rr = cc.residual_rule(B["C_T"], F_T, B["C_T"] + C_run, F_T + C_run)',
     'rr = cc.residual_rule(B["C_T"], F_T, B["C_T"] + C_run, F_T)'),
    ("fire-not-stop", P, 'if rr["fires"] and stop is None:', "if False:"),
    ("ibukt-no-xR", P, 'b = np.asarray(rec[E_R_METHOD]["mean"], np.float64) * x_R',
     'b = np.asarray(rec[E_R_METHOD]["mean"], np.float64)'),
    ("ibukt-cells-unchecked", P, 'if [int(c) for c in rec["cells"]] != [int(c) for c in cells]:', "if False:"),
    ("c2-uncarried", P, '(("carried_to_tune", cc.carry(C_PL, d)),', '(("carried_to_tune", C_PL),'),
    ("g2r-unpinned", P, 'G = load_npz(pinned(g2r_dir / T / f"blocks_g2r_{T}.npz", G2R_SHA[T]))',
     'G = load_npz(g2r_dir / T / f"blocks_g2r_{T}.npz")'),
    ("rc-stop-0", P, 'return 0 if rec["status"] == "done" else 3', "return 0"),
    ("out-overwrite", P, "    if a.out.exists():\n", "    if False:\n"),
    ("xhat-ignored", P, "XR = load_npz(xhat_round) if xhat_round else None", "XR = None"),
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


def run_tests(d: Path) -> int:
    env = dict(os.environ, OMP_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_covfix_core.py", "test_covfix_p0.py"], cwd=d,
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                       timeout=600)
    return r.returncode


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        base = run_tests(tree(Path(td)))
    print(f"baseline rc {base}")
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
            rc = run_tests(d)
        status = "killed" if rc != 0 else "SURVIVED"
        if rc == 0:
            survived.append(mid)
        print(f"{mid}: {status} (rc {rc})")
    print(f"{len(MUTANTS) - len(survived)}/{len(MUTANTS)} killed; survived or not applied: {survived}")
    return 0 if not survived else 1


if __name__ == "__main__":
    sys.exit(main())
