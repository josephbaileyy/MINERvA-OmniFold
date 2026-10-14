"""Read-only: reuse of the overlaid data gate (ev_run, ev_subrun, ev_gate) across MC events, within and across files."""
import sys, json, ROOT
import numpy as np
ROOT.gROOT.SetBatch(True)
keys = {}
res = {"files": []}
for p in sys.argv[1:]:
    a = ROOT.RDataFrame("Truth", p).AsNumpy(["ev_run", "ev_subrun", "ev_gate", "mc_run", "mc_subrun", "mc_nthEvtInFile"])
    a = {k: np.asarray(v).astype(np.int64) for k, v in a.items()}
    ov = (a["ev_run"] << 32) | (a["ev_subrun"] << 16) | a["ev_gate"]
    mck = (a["mc_run"] << 40) | (a["mc_subrun"] << 24) | a["mc_nthEvtInFile"]
    # dedupe exact MC duplicate keys first (known double-filled subrun)
    _, first = np.unique(mck, return_index=True)
    ov = ov[np.sort(first)]; sub = ((a["mc_run"] << 16) | a["mc_subrun"])[np.sort(first)]
    u, c = np.unique(ov, return_counts=True)
    # gates reused across different MC subruns (generator jobs)
    pairs = np.unique(np.stack([ov, sub]), axis=1)
    ug, cg = np.unique(pairs[0], return_counts=True)
    r = {"path": p.split("/")[-1], "mc_events": int(ov.size), "distinct_overlay_gates": int(u.size),
         "max_events_per_gate": int(c.max()), "events_on_shared_gates": int(c[c > 1].sum()),
         "gates_in_more_than_one_mc_subrun": int((cg > 1).sum()), "max_subruns_per_gate": int(cg.max()),
         "ev_run_range": [int(a["ev_run"].min()), int(a["ev_run"].max())]}
    keys[p] = set(u.tolist())
    res["files"].append(r)
    print(json.dumps(r), flush=True)
ps = list(keys)
res["cross_file_shared_gates"] = {f"{ps[i].split('/')[-1]}|{ps[j].split('/')[-1]}": len(keys[ps[i]] & keys[ps[j]]) for i in range(len(ps)) for j in range(i + 1, len(ps))}
print(json.dumps(res["cross_file_shared_gates"]))
