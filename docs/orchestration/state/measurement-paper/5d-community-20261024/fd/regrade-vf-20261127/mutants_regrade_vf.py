"""Mutation runner for regrade_vf.py. It never edits the module in place: each mutant is a copy in a temporary directory,
beside a copy of the tests, with REGRADE_VF_REPO pointing at this checkout so the committed inputs resolve.

  python3 mutants_regrade_vf.py [--out mutation.txt]

The unmutated copy must pass first (exit 9 otherwise). A mutant whose replacement text does not occur exactly once is a
runner error (exit 8). Per mutant: NOT-COMPILED (excluded), KILLED (pytest exit 1), SURVIVED (exit 0), HARNESS (any
other exit; counted apart and named). Exit 0 only when every compiled mutant is KILLED.
"""
from __future__ import annotations

import argparse
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
SRC = HERE / "regrade_vf.py"
TESTS = HERE / "test_regrade_vf.py"

MUTANTS = [   # (name, old, new): old must occur exactly once in regrade_vf.py
    ("gap-min-off", "GAP_MIN = 1e-9", "GAP_MIN = -1.0"),
    ("debias-n-minus-1", "B = B_raw - F / n", "B = B_raw - F / (n - 1)"),
    ("no-debias", "B = B_raw - F / n", "B = B_raw"),
    ("F-divisor-n", "fn.chi2_nonnull(E - ebar, Cp)[0].sum() / (n - 1) / ndf", "fn.chi2_nonnull(E - ebar, Cp)[0].sum() / n / ndf"),
    ("F-uncentred", "fn.chi2_nonnull(E - ebar, Cp)", "fn.chi2_nonnull(E, Cp)"),
    ("identity-off", "abs(M - (B + F)) > ID_REL * M", "abs(M - (B + F)) > 1e9 * M"),
    ("tau-includes-dF", "r = rc.r_chi2(E, C_base, C_add)", "r = rc.r_chi2(E, 0 * C_base, C_base + C_add)"),
    ("rank-off", "if ndf != NDF or r[", "if False and r["),
    ("bvf-ge", 'if d > K_SE * se["B_minus_F"]:', 'if d >= K_SE * se["B_minus_F"]:'),
    ("bvf-fluct-sign", 'elif -d > K_SE * se["B_minus_F"]:', "elif d < 0:"),
    ("bias-ge", '"yes" if B > K_SE * se["B"]', '"yes" if B >= K_SE * se["B"]'),
    ("rchi2-no-minus-1", '"under-describes on average" if (M_full - 1.0) > K_SE * SE', '"under-describes on average" if M_full > K_SE * SE'),
    ("seed-moved", '"g18/minus2": 9_991_271', '"g18/minus2": 9_991_270'),
    ("n-boot-200", "N_BOOT = 2000", "N_BOOT = 200"),
    ("band-edge", '("R2", 4, 8), ("R3", 8, 16)', '("R2", 4, 9), ("R3", 9, 16)'),
    ("L-phi-not-sqrt", "(math.sqrt(phi[name]) - 1.0)", "(phi[name] - 1.0)"),
    ("eig-ascending", "order = np.argsort(lam)[::-1]", "order = np.argsort(lam)"),
    ("rule-ii-no-minus", "return L @ C_eT @ L.T - C_eT", "return L @ C_eT @ L.T"),
    ("rule-i-uncarried", 'dF = {"rule_i": rc.carry_frac(ops["DeltaC_e"], X_T, ops["f"])', 'dF = {"rule_i": ops["DeltaC_e"]'),
    ("c-add-pl-at-f", 'rc.carry_rel(ops["P_rel"], X_T)\n    r0', 'rc.carry_rel(ops["P_rel"], ops["f"])\n    r0'),
    ("a0-off", "if max(a0.values()) > A0_REL:", "if max(a0.values()) > 1.0:"),
    ("cf-capture-off", 'if frel > F_REL:\n        raise Stop(f"C-F: capture', 'if frel > 1.0:\n        raise Stop(f"C-F: capture'),
    ("cf-blocks-off", 'if frel > F_REL:\n        raise Stop(f"C-F: vf_block', 'if frel > 1.0:\n        raise Stop(f"C-F: vf_block'),
    ("psd-neg-off", "lmin_rel < -PSD_REL", "lmin_rel < -1.0"),
    ("psd-asym-off", "if asym > SYM_REL or", "if False or"),
    ("df-d1-off", "if d1 > DF_REL or d2 > DF_REL:", "if d2 > DF_REL:"),
    ("cl-l1-off", "if l1 > L_REL or l2 > L_REL:", "if l2 > L_REL:"),
    ("cl-l2-off", "if l1 > L_REL or l2 > L_REL:", "if l1 > L_REL:"),
    ("gap-T-off", 'c["C_GAP_T"] = gap_check(C_eT, f"C_e({e})")', 'c["C_GAP_T"] = {}'),
    ("active-off", "if not all(fl[\"trigger\"][name][\"active\"]", "if False and all(fl[\"trigger\"][name][\"active\"]"),
    ("main-overwrites", "if a.out.exists():", "if False:"),
    ("boot-B-no-debias", "Bb = np.sum(zbar ** 2, axis=1) / ndf - Fb / n", "Bb = np.sum(zbar ** 2, axis=1) / ndf"),
    ("boot-uncentred", "Fb = np.sum((Zb - zbar[:, None, :]) ** 2", "Fb = np.sum((Zb) ** 2"),
    ("boot-diff-plus", '"B_minus_F": float((Bb - Fb).std(ddof=1))', '"B_minus_F": float((Bb + Fb).std(ddof=1))'),
    ("sensitive-vs-before", 'carry_sensitive(rec["rule_i"], rec["rule_ii"])', 'carry_sensitive(rec["rule_i"], rec["before"])'),
    ("before-with-dF", 'rec["before"] = split(E, C_T, C_add, idx)', 'rec["before"] = split(E, C_T + dF["rule_i"], C_add, idx)'),
    ("pin-off", "if got != want:", "if False:"),
    ("pin-stop-scope", 'out["evaluations"] = {e: {"status": "STOP", "stop": str(ex)} for e in EVALS}', 'out["evaluations"] = {}'),
]


def run_tests(d: Path) -> int:
    env = {**os.environ, "REGRADE_VF_REPO": str(REPO), "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("PYTHONPATH", None)
    p = subprocess.run([sys.executable, "-I", "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                        str(d / "test_regrade_vf.py")], cwd=d, env=env, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    return p.returncode


def trial(source: str) -> str:
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "regrade_vf.py").write_text(source)
        shutil.copy2(TESTS, d / "test_regrade_vf.py")
        try:
            py_compile.compile(str(d / "regrade_vf.py"), cfile=str(d / "c.pyc"), doraise=True)
        except py_compile.PyCompileError:
            return "NOT-COMPILED"
        rc = run_tests(d)
    return {0: "SURVIVED", 1: "KILLED"}.get(rc, f"HARNESS (exit {rc})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    src = SRC.read_text()
    lines = []
    for name, old, _ in MUTANTS:
        if src.count(old) != 1:
            print(f"runner error: mutant {name}: its text occurs {src.count(old)} times", file=sys.stderr)
            return 8
    base = trial(src)
    lines.append(f"baseline (unmutated copy): {'tests pass' if base == 'SURVIVED' else base}")
    if base != "SURVIVED":
        print("\n".join(lines))
        return 9
    counts: dict = {}
    for name, old, new in MUTANTS:
        r = trial(src.replace(old, new))
        counts[r.split(" ")[0]] = counts.get(r.split(" ")[0], 0) + 1
        lines.append(f"{name}: {r}")
    compiled = sum(v for k, v in counts.items() if k != "NOT-COMPILED")
    lines.append(f"summary: {counts.get('KILLED', 0)}/{compiled} compiled mutants KILLED; {counts}")
    text = "\n".join(lines) + "\n"
    print(text, end="")
    if a.out:
        a.out.write_text(text)
    return 0 if counts.get("KILLED", 0) == compiled else 1


if __name__ == "__main__":
    sys.exit(main())
