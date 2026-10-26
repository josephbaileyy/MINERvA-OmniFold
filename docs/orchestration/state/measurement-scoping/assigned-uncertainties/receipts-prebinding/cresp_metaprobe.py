"""Meta-only probe of the 11 MP-1 S1 unfold products: reads each npz's `meta` key and no other array.

Prints the provenance fields C-RESP-SPEC's builder checks; computes nothing from xsec_flat."""
import json
import sys
from pathlib import Path

import numpy as np

KEYS = ("schema", "config", "capacity", "iters", "construction", "truth", "amplitude", "pseudo_seed",
        "bootstrap_seed", "jitter_seed", "jitter_mode", "coords", "estimator_seed", "input_npz_sha256",
        "bkg_dump_sha256", "eavail_ratio_sha256")
for p in sorted(Path(sys.argv[1]).glob("mp1s1_*_b-_j-.npz")):
    with np.load(p, allow_pickle=False) as z:
        m = json.loads(str(z["meta"]))
        files = sorted(z.files)
    cp = (m.get("refinement") or {}).get("classifier_params") or {}
    est = [(e.get("n_estimators"), e.get("num_leaves"), e.get("random_state")) for e in m.get("estimator_params", [])]
    row = {k: m.get(k) for k in KEYS}
    row.update({"npz_keys": files, "estimators": est, "refinement_ran": (m.get("refinement") or {}).get("ran"),
                "refinement": (cp.get("n_estimators"), cp.get("num_leaves"), cp.get("random_state"),
                               cp.get("deterministic"), cp.get("bin_construct_sample_cnt"))})
    print(p.name, json.dumps(row, sort_keys=True))
