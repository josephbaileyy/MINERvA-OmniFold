"""Audit check: evaluate the article's kappa-scan bracket endpoints from RC4 tarball inputs, using the committed
scan class (publication/kappa/kappa_breakdown.py) with the RC4 copy of replay_inference.py (digest-checked)."""
import hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
rc, kb = Path(sys.argv[1]), Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("kb", kb); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rp = rc / "code/replay_inference.py"
assert hashlib.sha256(rp.read_bytes()).hexdigest() == m.REPLAY_SHA256
sys.path.insert(0, str(rp.parent)); import replay_inference as ri
for reading, npz, ks in (("frozen", "data/frozen/inference_sufficient.npz", [5.25, 5.2546875, 5.25625]),
                         ("union", "data/recovery-union/inference_sufficient.npz", [5.16875, 5.1703125])):
    z = np.load(rc / npz); man = json.loads((rc / (npz + ".manifest.json")).read_text())
    sc = m.Scan(ri, z, man)
    for k in ks:
        d = sc.family(k, "A")
        nonrej = {t: (v["decision"], v["k"], v["own_interval_vs_threshold"]) for t, v in d.items() if v["decision"] != "rejected"}
        mec = d["GENIE_2_12_10_MEC:shape"]
        print(f"{reading} kappa={k}: all rejected={not nonrej}; non-rejected={nonrej}; MEC shape k={mec['k']} own={mec['own_interval_vs_threshold']}", flush=True)
