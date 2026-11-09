import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/nd-unfolding/prior_retention")
import prr_probe as p
post = Path(sys.argv[2])
rec = p.read_log(post / "log-dry")
rates = p.measured_rates(rec)
out = {"unit_s": p.UNIT_S, "tasks": {}, "rates_s": rates, "jobs": {}}
dq = p.read_queue(post / "queues/dry.tsv")
for tid, lv, u in dq:
    r = rec[tid]; d = r["end"] - r["start"]
    out["tasks"][tid] = {"level": lv, "assumed_units": u, "wall_s": round(d, 1), "measured_units": round(d / p.UNIT_S, 3)}
t0 = min(r["start"] for r in rec.values())
out["dry_queue_span_s"] = round(max(r["end"] for r in rec.values()) - t0, 1)
for j in ("iter", "cap", "misc"):
    q = p.read_queue(post / f"queues/{j}.tsv")
    pr = p.project(1000.0, 1000.0, q, rec)
    lim = p.JOB_LIMIT_H[j]
    out["jobs"][j] = {"tasks": len(q), "already_ended_in_dry": sum(1 for t, _, _ in q if "end" in rec.get(t, {})),
                      "projected_h": round(pr["projected_h"], 4), "limit_h": lim, "gate_h": round(p.GATE_FRACTION * lim, 4),
                      "passes": pr["projected_h"] <= p.GATE_FRACTION * lim and not pr["unmeasured"], "unmeasured": pr["unmeasured"],
                      "levels": sorted({lv for _, lv, _ in q})}
print(json.dumps(out, indent=1))
