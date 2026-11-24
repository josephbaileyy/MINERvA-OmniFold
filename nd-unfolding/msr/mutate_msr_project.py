#!/usr/bin/env python3
"""Hand mutants of msr_project.py: each is one textual change, run in its own process against test_msr; a mutant is
killed if the suite fails. The source on disk is never modified (the mutated text is executed under the real path).

    python3 nd-unfolding/msr/mutate_msr_project.py      (exit 0 only if every mutant is killed)
"""
from __future__ import annotations

import concurrent.futures as cf
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "msr_project.py"

MUTANTS = [
    ("band_s poor edge", 'return "poor-dominated" if x >= 0.8', 'return "poor-dominated" if x > 0.8'),
    ("band_s well edge", '("well-dominated" if x <= 0.2 else "mixed")', '("well-dominated" if x < 0.2 else "mixed")'),
    ("band_z below edge", 'return "below" if x < 1 else', 'return "below" if x <= 1 else'),
    ("band_z resolvable edge", '("intermediate" if x < 2 else "resolvable")', '("intermediate" if x <= 2 else "resolvable")'),
    ("band_r most edge", "    if x >= 0.5:\n        return \"removes most\"", "    if x > 0.5:\n        return \"removes most\""),
    ("band_r no-change edge", "    if x > -0.2:\n        return \"no change\"", "    if x >= -0.2:\n        return \"no change\""),
    ("floor strict", "    if hi < FLOOR:", "    if hi <= FLOOR:"),
    ("Z per axis", "return float(np.sqrt(np.sum((w.T @ beta) ** 2 / np.maximum(s, 1e-300) ** 2)))",
     "return float(np.max(np.abs(w.T @ beta) / np.maximum(s, 1e-300)))"),
    ("U-infinity threshold", "    inf = rho > NULL_TOL", "    inf = rho > 0.5"),
    ("range cut", "    rng = lam > EIG_RTOL * lam.max()", "    rng = lam > 0"),
    ("combined order", '''    if z_lab == "resolvable":
        return "points at a resolvable component"
    if floor != "read":
        return floor''', '''    if floor != "read":
        return floor
    if z_lab == "resolvable":
        return "points at a resolvable component"'''),
    ("noise max lo>=", "        if lo > z_noise:", "        if lo >= z_noise:"),
    ("ddof 0", "np.std(np.asarray(f_splits, float), ddof=1)", "np.std(np.asarray(f_splits, float), ddof=0)"),
    ("r floor off", "P @ b_b0))\n        out[name] = None if den <= R_FLOOR else", "P @ b_b0))\n        out[name] = None if den < 0 else"),
    ("MC projector check off", "    ok = bool(same and d_ab <= MC_PROJ and d_fa <= MC_PROJ and d_fb <= MC_PROJ)", "    ok = bool(same)"),
    ("match bar off", "if ov[i, j] >= MC_MATCH}", "if ov[i, j] >= 0.0}"),
    ("s_poor complement", "    return 1.0 - float(beta @ dec[\"PW\"] @ beta) / nb if nb > 0", "    return float(beta @ dec[\"PW\"] @ beta) / nb if nb > 0"),
    ("C-RID tolerance", "ok = inf_ok and nan_ok and rel <= 1e-6", "ok = inf_ok and nan_ok and rel <= 1e-3"),
    ("info-limit and->or", 'if s_lab == "poor-dominated" and z_lab == "below":', 'if s_lab == "poor-dominated" or z_lab == "below":'),
    ("C-T3 tolerance", 'ctl(rec, "C-T3", worst <= 1e-12', 'ctl(rec, "C-T3", worst <= 1.0'),
    ("conversion drops P", 'return np.asarray(b, float) * np.asarray(z3[f"t3__P__s{s}"], float) / f0',
     'return np.asarray(b, float) / f0'),
    ("stop ignored", "    if stops:\n        (out / \"readout.json\")", "    if False:\n        (out / \"readout.json\")"),
    ("C-ROUTE ignored", '    ctl(rec, "C-ROUTE", route <= 0.0, max_excess=route)', '    ctl(rec, "C-ROUTE", True, max_excess=route)'),
    ("count space -> theta space J", "    J = (L[keep] / f0[keep, None])", "    J = (L[keep] / f0[keep, None]) * t0[None, :]"),
    ("dropped-cell check off", "    if not keeps_equal(decs):\n        return False, {\"dropped_cells_differ\": True}",
     "    if False:\n        return False, {\"dropped_cells_differ\": True}"),
    ("early stop off", "    if early:   # stop before", "    if False:   # stop before"),
    ("r N-PREC off", "            if not same_part or (v is None) != (ve is None) or (v is not None and abs(v - ve) > PREC_R):",
     "            if False:"),
    ("r route off", "                route_worst[0] = float(\"inf\") if (v is None) != (vi is None) else max(",
     "                route_worst[0] = 0.0 if True else max("),
    ("C-L id range off", "and int(ids.max()) < 224", "and True"),
    ("C-DID strict rule restored", "    ctl(rec, \"C-DID\", len(common) > 0 and len(common) == C_DID_COMMON_EXPECTED",
     "    ctl(rec, \"C-DID\", len(common) > 0 and len(common) == len(j5[\"t1_names\"])"),
    ("C-DID expected size off", "len(common) > 0 and len(common) == C_DID_COMMON_EXPECTED", "len(common) > 0"),
    ("C-2D exact M restored", "    m_ok = rel_ok(z2[\"d2_full__M\"], z2[\"d2__bank_ibu_response\"])",
     "    m_ok = bool(np.array_equal(z2[\"d2_full__M\"], z2[\"d2__bank_ibu_response\"]))"),
    ("C-D primary only restored", "    with_d = list(F0B_PRIMARY) + [t for t in F0B_SECONDARY_WITH_D]", "    with_d = list(F0B_PRIMARY)"),
    # Amendment E
    ("E: C's float64 formation restored (eigen route)",
     "        c, s, _ = svd(BQ.T @ G, driver)\n        s, w = s[::-1].copy(), (BQ @ c)[:, ::-1].copy()",
     "        s2, c = eigh(BQ.T @ (G @ G.T) @ BQ, driver)\n        s, w = np.sqrt(np.clip(s2, 0.0, None)), BQ @ c"),
    ("E: C's float64 formation restored (independent route)",
     "    rf = np.linalg.qr(dec[\"G\"].T @ Wb, mode=\"r\")\n    y = sla.solve_triangular(rf, a, trans=\"T\")\n    return sp, float(np.linalg.norm(y))",
     "    z2 = float(a @ np.linalg.solve(Wb.T @ (dec[\"G\"] @ dec[\"G\"].T) @ Wb, a))\n    return sp, float(np.sqrt(max(z2, 0.0)))"),
    ("E: well-block refinement off", "        if blk.any():   # the well-constrained block", "        if False:   # the well-constrained block"),
    ("E: production eigenbasis from eigh(F)", "    if A is None:\n        return eigh(F, driver)", "    if True:\n        return eigh(F, driver)"),
    ("E: root keeps mu <= 0 rows", "    keep = mu > 0\n    return np.asarray((sparse.diags", "    keep = mu != 0\n    return np.asarray((sparse.diags"),
    ("E: root null completion off", "    if V.shape[1] < n:   # fewer kept", "    if False:   # fewer kept"),
    ("E: re-sort after refinement off", "            s, w = s[o], w[:, o]\n", "            pass\n"),
    ("E: singular-Q refusal off", "        if BQ.shape[1] > G.shape[1]:\n", "        if False:\n"),
    ("E: G without the 1/sqrt(lambda) scale", "    G = (J @ V[:, rng]) / np.sqrt(lam[rng])[None, :]", "    G = (J @ V[:, rng]) / lam[rng][None, :]"),
    ("E: a production call drops the root", "                d = decompose(p[\"F\"], p[\"J\"], drv, A=p[\"A\"])", "                d = decompose(p[\"F\"], p[\"J\"], drv)"),
]

RUNNER = r'''
import sys, types, unittest
from pathlib import Path
here, target, old, new = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
src = target.read_text()
assert src.count(old) == 1, "mutant site not unique"
mod = types.ModuleType("msr_project"); mod.__file__ = str(target)
sys.modules["msr_project"] = mod
sys.path.insert(0, str(here))
exec(compile(src.replace(old, new), str(target), "exec"), mod.__dict__)
import test_msr
r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(unittest.defaultTestLoader.loadTestsFromModule(test_msr))
sys.exit(0 if r.wasSuccessful() else 1)
'''


def one(m):
    name, old, new = m
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    p = subprocess.run([sys.executable, "-c", RUNNER, str(HERE), str(TARGET), old, new], capture_output=True, text=True,
                       env=env, cwd=str(HERE))
    status = "SURVIVED" if p.returncode == 0 else ("ERROR" if "mutant site not unique" in p.stderr else "killed")
    return name, status


def main() -> int:
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(one, MUTANTS))
    for name, status in results:
        print(f"{status:9s} {name}")
    bad = [n for n, s in results if s != "killed"]
    print(f"mutants {len(results)}; killed {len(results) - len(bad)}; not killed {len(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
