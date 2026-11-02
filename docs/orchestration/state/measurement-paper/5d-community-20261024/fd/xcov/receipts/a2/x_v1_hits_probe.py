"""X V1 defect sizing (read-only): for each of the 175 universes, how many pinned weight files carry the digest S1's
product recorded (fd_xcov_steps.weight_files' lookup without its exactly-one rule). From $R/deploy-a1 at M'; the
detector receipt is read through Inputs.bytes (O_NOATIME, pin-checked)."""
import json, sys, collections
from pathlib import Path
R = Path("/pscratch/sd/j/josephrb/gencmp-x-20261102")
sys.path.insert(0, str(R / "deploy-a1/nd-unfolding"))
import numpy as np, fd_xcov as X, fd_xcov_steps as XS
inp = X.Inputs()
sf1 = {p: h for h, p in (ln.split(None, 1) for ln in XS.SF1.read_text().splitlines() if ln.strip())}
sf1 = {p.strip(): h for p, h in sf1.items()}
det = {str(XS.DET_RECEIPT.parent / Path(p).name): h for p, h in json.loads(inp.bytes(XS.DET_RECEIPT))["files_sha256"].items()}
s1meta = json.loads(XS.S1_JSON.read_text())["meta"]["inputs_sha256"]
out, bands = {}, collections.defaultdict(lambda: collections.Counter())
for b, i in XS.universe_list():
    meta = json.loads(str(np.load(XS.S1DIR / f"S1_{b}_{i}.npz", allow_pickle=False)["meta"]))
    want = meta["bank_weight_sha256"]
    for k in ("wt", "wr"):
        hits = [p for p, h in {**sf1, **det}.items() if h == want[k] and p.endswith(f"_{k}.npy")]
        out[f"{b}:{i}:{k}"] = len(hits)
        bands[b][len(hits)] += 1
print(json.dumps({"universes": len(out) // 2, "hits_histogram": collections.Counter(out.values()),
                  "bands": {b: dict(c) for b, c in bands.items()},
                  "zero_hits": [k for k, v in out.items() if v == 0], "atime": inp.atime_deviations()}, default=str))
