"""Diff the RHC branch lists against the FHC ones (per tree: names only in one, and type or leaf-count changes)."""
import json, sys
D = sys.argv[1]
out = {}
for kind in ("mc", "data"):
    r = json.load(open(f"{D}/branches_rhc_{kind}_5A.json")); f = json.load(open(f"{D}/branches_fhc_{kind}_1B.json"))
    o = {"rhc_file": r["file"], "fhc_file": f["file"], "trees": {}}
    for t in sorted(set(r["trees"]) | set(f["trees"])):
        rb = {b[0]: (b[1], b[2]) for b in r["trees"].get(t, {}).get("branches", [])}
        fb = {b[0]: (b[1], b[2]) for b in f["trees"].get(t, {}).get("branches", [])}
        o["trees"][t] = {"n_rhc": len(rb), "n_fhc": len(fb), "only_rhc": sorted(set(rb) - set(fb)), "only_fhc": sorted(set(fb) - set(rb)),
                         "type_changed": sorted([n, fb[n], rb[n]] for n in set(rb) & set(fb) if rb[n] != fb[n]),
                         "same_order": [b[0] for b in r["trees"].get(t, {}).get("branches", [])] == [b[0] for b in f["trees"].get(t, {}).get("branches", [])]}
    out[kind] = o
json.dump(out, open(f"{D}/branch_diff.json", "w"), indent=1)
for k, o in out.items():
    for t, v in o["trees"].items():
        print(k, t, "rhc", v["n_rhc"], "fhc", v["n_fhc"], "only_rhc", v["only_rhc"][:10], "only_fhc", v["only_fhc"][:10], "type_changed", v["type_changed"][:5], "same_order", v["same_order"])
