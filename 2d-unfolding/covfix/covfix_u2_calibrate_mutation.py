"""Hand mutants for covfix_u2_calibrate.py: each must be killed by test_covfix_u2_calibrate.py.

  python3 -B covfix_u2_calibrate_mutation.py     one line per mutant; exit 0 only if all are killed

Each mutant runs in a fresh temp dir with copies of the module and its test. A failure that names no test, or an
import or discovery failure, is a HARNESS FAILURE, not a kill.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("covfix_u2_calibrate.py", "test_covfix_u2_calibrate.py")
L = "covfix_u2_calibrate.py"
MUTANTS = [
    ('d2-no-subtract', '(rg - rr)[both] ** 2 - var_g[both] - var_ref[both]', '(rg - rr)[both] ** 2'),
    ('d2-ref-var-dropped', ' - var_g[both] - var_ref[both])', ' - var_g[both])'),
    ('d2-no-floor-at-zero', 'd2 = np.maximum(0.0, (rg - rr)[both] ** 2 - var_g[both] - var_ref[both])', 'd2 = np.abs((rg - rr)[both] ** 2 - var_g[both] - var_ref[both])'),
    ('debiased-unweighted', '"D_debiased": float((w * np.sqrt(d2)).sum() / w.sum())', '"D_debiased": float(np.sqrt(d2).mean())'),
    ('var-ddof0', 'axis=0, ddof=1)', 'axis=0, ddof=0)'),
    ('var-min-reps-ignored', '    return np.where(n >= 2, var, np.inf)', '    return var'),
    ('floor-branch-inverted', 'branch = "floor" if min(d_deb) < floor else "min"', 'branch = "floor" if min(d_deb) > floor else "min"'),
    ('floor-fraction-off', 'floor = FLOOR_FRACTION * t_hi', 'floor = FLOOR_FRACTION * min(d_deb)'),
    ('t-hi-from-raw', 't_hi = max(d_deb)', 't_hi = max(d_raw)'),
    ('nontrivial-wrong', '"nontrivial_threshold": NONTRIVIAL_FRACTION * t_lo', '"nontrivial_threshold": NONTRIVIAL_FRACTION * t_hi'),
    ('zero-spread-allowed', '    if t_hi <= 0.0:\n        raise Refusal("every debiased D is zero', '    if False:\n        raise Refusal("every debiased D is zero'),
    ('a-lo-from-raw', 'a_lo, a_hi = _match(w, scan, t_lo), _match(w, scan, t_hi)', 'a_lo, a_hi = _match(w, scan, r1["t_lo"]), _match(w, scan, t_hi)'),
    ('map-noise-no-resample', '        we = resample(w, sd, rng)', '        we = w'),
    ('zero-count-wrong', '"cells_debiased_to_zero": int(np.sum(d2 == 0.0))', '"cells_debiased_to_zero": int(np.sum(d2 > 0.0))'),
    ('noise-scale-unweighted', '"noise_scale": float((w[fin] * noise[fin]).sum() / w[fin].sum())', '"noise_scale": float(noise[fin].mean())'),
    ('ipf-joint-skipped', '        r *= ratio(t_joint, (w * r).sum(axis=(3, 4)))[..., None, None]\n', ''),
    ('ipf-tol-ignored', '        if dev <= RAKE_TOL:', '        if True:'),
    ('corr-not-normalized', '        rho = (s * xi * eta).sum(axis=(3, 4)) / tot', '        rho = (s * xi * eta).sum(axis=(3, 4))'),
    ('validity-ignored', '    valid = (tot > 0) & (vq > 1e-12) & (vw > 1e-12)', '    valid = tot > 0'),
    ('scan-monotone-unchecked', '    if As[1] <= As[0] or any(b <= a for a, b in zip(As[1:], As[2:])):', '    if False:'),
    ('sha-unchecked', '            if got != pin:', '            if False:'),
    ('overwrite-ok', '    if a.out.exists():', '    if False:'),
]


def run_tests(d: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_covfix_u2_calibrate.py"], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=300,
                       text=True, env=dict(os.environ))
    lines = r.stderr.splitlines()
    named = [ln for ln in lines if ln.startswith(("FAIL: ", "ERROR: "))]
    if r.returncode != 0 and (not named or any("_FailedTest" in ln for ln in named)):
        return -1, "HARNESS: " + (lines[-1] if lines else "no stderr")
    return r.returncode, (named[0] if named else (lines[-1] if lines else ""))


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        for f in FILES:
            shutil.copy2(HERE / f, Path(td) / f)
        base, why = run_tests(Path(td))
    print(f"baseline rc {base} {why}")
    if base != 0:
        return 2
    bad = []
    for mid, old, new in MUTANTS:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            for f in FILES:
                shutil.copy2(HERE / f, d / f)
            src = (d / L).read_text()
            if src.count(old) != 1:
                print(f"{mid}: NOT APPLIED (pattern occurs {src.count(old)} times)")
                bad.append(mid)
                continue
            (d / L).write_text(src.replace(old, new))
            rc, why = run_tests(d)
        status = "killed" if rc > 0 else ("HARNESS FAILURE" if rc < 0 else "SURVIVED")
        if rc <= 0:
            bad.append(mid)
        print(f"{mid}: {status} {why}")
    print(f"{len(MUTANTS) - len(bad)}/{len(MUTANTS)} killed; survived, harness or not applied: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
