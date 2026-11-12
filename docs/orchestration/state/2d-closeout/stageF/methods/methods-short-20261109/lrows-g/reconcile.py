"""L-row G5 (referee6 minor 6): where the two period steps (6.94 +- 0.41 % and 6.89 +- 0.46 %) and the two lower
endpoints (9 % and 16 %) of the three shape changes' largest residuals come from. Read-only. Run from the repository
root: python3 -I <this file>. Each input is recorded with its sha256 under "digest", a record rather than a
binding (a path key beside a "sha256" key would join the receipt-binding inventory). The recovery readout and the paper's sources are on #977's branch, read by `git show`
at BRANCH."""
import hashlib
import json
import subprocess
from pathlib import Path

BRANCH = "60d144395f68ae16bd7b569a4571d178a3af0211"
P_PURITY = Path("docs/orchestration/state/2d-closeout/period-unfold-20261014/outputs/analysis.json")
P_REFINED = Path("docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/periods/analysis.json")
VT = Path("docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/values_table.tsv")
S5E = "docs/orchestration/state/s5e/cand/assess_receipt.json"
RECOV = "docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-figure-deformation-20261112/check-a/a_recovery.json"


def show(path):
    return subprocess.run(["git", "show", f"{BRANCH}:{path}"], check=True, capture_output=True).stdout


sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
steps = {}
for name, p in (("purity", P_PURITY), ("refined", P_REFINED)):
    b = p.read_bytes()
    s = json.loads(b)["comparisons"]["dr_PB/PA"]["step"]
    steps[name] = {"file": str(p), "digest": sha(b), "key": "comparisons/dr_PB/PA/step",
                   "value_pct": 100 * s["value"], "noise_sigma_pct": 100 * s["noise_sigma"]}
rows = [ln.split("\t") for ln in VT.read_text().splitlines()]
hdr = rows[0]
vt = {r[0]: dict(zip(hdr, r)) for r in rows[1:] if r[0] in ("pl-step", "pl-step-sigma")}
assert abs(float(vt["pl-step"]["purity_value"]) - steps["purity"]["value_pct"] / 100) < 1e-15
assert abs(float(vt["pl-step"]["refined_value"]) - steps["refined"]["value_pct"] / 100) < 1e-15
s5e_b, rec_b = show(S5E), show(RECOV)
a, r = json.loads(s5e_b)["points"], json.loads(rec_b)["shapes"]
shapes = {k: {"all_cells_max_pct": a[k]["ew_max_abs_pct"], "all_cells_argmax": a[k]["ew_argmax"],
              "supported_max_pct": 100 * r[k]["max_abs_residual_supported"],
              "supported_argmax": r[k]["max_abs_residual_supported_cell"]} for k in ("W1", "W2", "W3")}
out = {"schema": "lrows-g5-reconcile/1", "branch": BRANCH,
       "period_step": {**steps, "values_table": {"file": str(VT), "digest": sha(VT.read_bytes()),
                                                 "rows": {k: {x: v[x] for x in ("where", "printed", "refined_rendered", "source")}
                                                          for k, v in vt.items()}}},
       "residual_endpoints": {"s5e_assess": {"file": S5E, "digest": sha(s5e_b), "key": "points/<W>/ew_max_abs_pct"},
                              "recovery_check_a": {"file": RECOV, "digest": sha(rec_b),
                                                   "key": "shapes/<W>/max_abs_residual_supported"},
                              "shapes": shapes,
                              "all_cells_range_pct": [min(s["all_cells_max_pct"] for s in shapes.values()),
                                                      max(s["all_cells_max_pct"] for s in shapes.values())],
                              "supported_range_pct": [min(s["supported_max_pct"] for s in shapes.values()),
                                                      max(s["supported_max_pct"] for s in shapes.values())]}}
Path(__file__).with_name("reconcile.json").write_text(json.dumps(out, indent=1) + "\n")
for k, v in steps.items():
    print(f"step {k}: {v['value_pct']:.4f} +- {v['noise_sigma_pct']:.4f} %  ({v['file']}, {v['digest'][:8]})")
for k, v in shapes.items():
    print(f"{k}: all cells {v['all_cells_max_pct']:.2f} % at {v['all_cells_argmax']}; supported {v['supported_max_pct']:.2f} % at {v['supported_argmax']}")
print("ranges:", out["residual_endpoints"]["all_cells_range_pct"], out["residual_endpoints"]["supported_range_pct"])
