#!/usr/bin/env python3
"""RE-2 part C: check_rebuild.py's same-run checks on re2c_run.sh's output (RE2-DECLARATION-C.md §3.7; CR-02, CR-03).

    python3 -I re2c_check_rebuild.py <outdir>

Copied from stageF/rebuild/scripts/check_rebuild.py (its steps C and D: lines 58-77). Its step-B equivalence (CR-01)
compared two archives of the purity code and has no counterpart here. Both checks stop:
  CR-02  each chi2_Q_<mode>.txt and the Fig. 6/7 log carry the cell-identity pass lines and no count-only warning;
  CR-03  the Fig. 6/7 projections equal budget_Q.json's Q, c08 and C_PL projections to 1e-12 (the same run's x: E_U in
         the purity arm, E_R in the refined arm).
Writes <outdir>/checks.json; exit 0 only if every check passes.
"""
import json
import sys
from pathlib import Path

NS = Path(sys.argv[1])
res = {}
PASS_LINE = "cell identity OK"
WARN_LINE = "no stored reported set; count only"


def check(name, ok, detail=None):
    res[name] = {"ok": bool(ok), "detail": detail}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail is not None else ""))


for mode in ("std", "lognormal", "substat"):
    t = (NS / "chi2" / f"chi2_Q_{mode}.txt").read_text()
    check(f"C_chi2_Q_{mode}_cell_identity_pass_line", PASS_LINE in t and "hReportedCells" in t and WARN_LINE not in t)
f67log = (NS / "logs/fig67_Q.log").read_text()
check("D_fig67_Q_cell_identity_four_pass_lines", f67log.count("identity OK") == 4 and WARN_LINE not in f67log,
      f67log.count("identity OK"))

b = json.loads((NS / "outA/budget_Q.json").read_text())
pj = json.loads((NS / "fig67/fig67_projections.json").read_text())
worst = 0.0
for axis, key in (("pt", "pt_sigma_pct"), ("pz", "pz_sigma_pct")):
    for curve, mat in (("Total", "Q"), ("Training seed", "c08"), ("Run period", "C_PL")):
        ref = b[mat][key]
        got = [100.0 * v for v in pj[axis][curve]]
        if len(ref) != len(got):
            check(f"D_fig67_{axis}_{curve}_length", False, (len(ref), len(got)))
            continue
        worst = max(worst, max(abs(g - r) / abs(r) for g, r in zip(got, ref)))
check("D_fig67_projections_eq_budget_Q_le_1e-12", worst <= 1e-12, worst)

(NS / "checks.json").write_text(json.dumps(res, indent=1) + "\n")
bad = [k for k, v in res.items() if not v["ok"]]
print(f"re2c_check_rebuild: {len(res) - len(bad)}/{len(res)} passed")
sys.exit(1 if bad else 0)
