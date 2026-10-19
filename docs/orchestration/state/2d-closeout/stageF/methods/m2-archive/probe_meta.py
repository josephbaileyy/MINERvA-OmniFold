import json, sys, numpy as np
for p in sys.argv[1:]:
    z = np.load(p, allow_pickle=False)
    m = json.loads(str(z["meta"]))
    d = m.get("nuisance_draw") or {}
    print(p.split('/')[-1], list(z.files), {k: np.shape(z[k]) for k in z.files if k != "meta"})
    print("  detector_bands", m.get("detector_bands"), "n_model", len(m.get("model_bands") or []), "dev", m.get("development"), "cfg", m.get("config"), m.get("capacity"), m.get("iters"))
    print("  draw keys", sorted(d.keys()), "lat", d.get("lateral_z"), "norm", d.get("normalization_z"))
    print("  det draw", {k: d[k] for k in d if 'det' in k.lower()})
    print("  code", json.dumps(m.get("code_sha256"))[:300], "hyp", m.get("hypothesis"))
