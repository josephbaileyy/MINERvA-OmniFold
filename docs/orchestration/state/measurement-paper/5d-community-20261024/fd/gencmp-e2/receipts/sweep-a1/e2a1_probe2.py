"""E2-A1 sweep probe, B2's code leg: the code record a seed-42 arm-e rerun at M'' would write in this environment
(pvl_unfold.py:156-160 installs candidate R before :186-188 reads s5n_pseudo.code_digests), against the committed
L-5D-PV_e_nuwro meta. Read-only."""
import io, json, sys, hashlib
from pathlib import Path
R = Path("/pscratch/sd/j/josephrb/gencmp-e2-20261102")
sys.path[:0] = [str(R / "deploy/nd-unfolding"), str(R / "deploy/nd-unfolding/pv-ladder")]
import numpy as np
import fd_gencmp as gc, fd_gencmp_e2 as E2, pvl_lib as L, s5n_pseudo, s5e_candidate, s5e_trace, pvl_unfold, lightgbm
pins = gc.load_pins(E2.INPUTS)
rel = f"{E2.PRODUCTS}/L-5D-PV_e_nuwro.npz"
data, _ = gc.read_noatime(R / "inputs" / rel)
assert hashlib.sha256(data).hexdigest() == pins[str(E2.SCRATCH / rel)]
old = json.loads(str(np.load(io.BytesIO(data), allow_pickle=True)["meta"]))["code_sha256"]
s5e_candidate.install("R")
now = {**s5n_pseudo.code_digests(), "pvl_unfold.py": L.sha256_path(Path(pvl_unfold.__file__)),
       "pvl_lib.py": L.sha256_path(L.__file__), "s5e_trace.py": L.sha256_path(Path(s5e_trace.__file__)),
       "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "lightgbm": lightgbm.__version__}}
differ = sorted(k for k in set(old) | set(now) if old.get(k) != now.get(k))
print(json.dumps({"differ": differ, "subset_of_allowed": set(differ) <= E2.CODE_ALLOWED_TO_DIFFER, "code_now": now}, default=str))
