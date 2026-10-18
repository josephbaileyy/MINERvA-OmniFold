#!/usr/bin/env python3
"""Stage F rebuild phase 1: the STOP comparisons that span runs (SPEC §4 equivalence, §5 KI-90 pass lines, §6 fig. 6/7
projections). Reads only files under <NS>; writes <NS>/checks.json. Exit 0 only if every check passes.

  python3 -I check_rebuild.py <NS>
"""
import json
import re
import sys
from pathlib import Path

NS = Path(sys.argv[1])
res = {}


def check(name, ok, detail=None):
    res[name] = {"ok": bool(ok), "detail": detail}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail is not None else ""))


def norm(text):
    # absolute paths differ between the two archives and output prefixes; strip them, and the run's sys.path line
    out = []
    for ln in text.splitlines():
        if ln.startswith("sys.path "):
            continue
        out.append(re.sub(r"/pscratch/\S+", "<path>", ln))
    return out


PASS_LINE = "cell identity OK"
WARN_LINE = "no stored reported set; count only"
expect_added = {  # SPEC §4 (amended from the code review's measurement)
    "adopted": {"pass": 1, "warn": 1},
    "control": {"pass": 2, "warn": 0},
    "repaired": {"pass": 2, "warn": 0},
}
for tag, want in expect_added.items():
    for mode in ("std", "lognormal", "substat"):
        a = norm((NS / "eq/a1" / f"{tag}_{mode}.txt").read_text())
        b = norm((NS / "eq/a2" / f"{tag}_{mode}.txt").read_text())
        added = [ln for ln in b if PASS_LINE in ln or WARN_LINE in ln]
        rest = [ln for ln in b if not (PASS_LINE in ln or WARN_LINE in ln)]
        n_pass = sum(PASS_LINE in ln for ln in added)
        n_warn = sum(WARN_LINE in ln for ln in added)
        check(f"B_equiv_{tag}_{mode}_identical_after_removing_added_lines", rest == a,
              None if rest == a else [x for x in rest if x not in a][:3])
        check(f"B_equiv_{tag}_{mode}_added_lines", (n_pass, n_warn) == (want["pass"], want["warn"]),
              {"pass": n_pass, "warn": n_warn})
for pre in ("control_EC_adopted", "EU_adopted", "EU_repaired"):
    a = (NS / "eq/a1" / f"{pre}_summary.txt").read_text()
    b = (NS / "eq/a2" / f"{pre}_summary.txt").read_text()
    check(f"B_equiv_fig67_{pre}_summary_identical", a == b)
    for sfx in ("pt", "pz"):
        pa, pb = NS / "eq/a1" / f"{pre}_{sfx}.png", NS / "eq/a2" / f"{pre}_{sfx}.png"
        check(f"B_equiv_fig67_{pre}_{sfx}_png_identical", pa.read_bytes() == pb.read_bytes())

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
print(f"check_rebuild: {len(res) - len(bad)}/{len(res)} passed")
sys.exit(1 if bad else 0)
