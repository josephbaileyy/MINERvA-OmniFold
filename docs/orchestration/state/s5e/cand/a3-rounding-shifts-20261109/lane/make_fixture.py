"""A synthetic assess/data tree (103 npz) and a receipt whose A3 summary is the producer's lines run the plain way."""
import glob, json, sys
from pathlib import Path
import numpy as np
D, T = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(D / "nd-unfolding"))
import s5e_analyze_candidate as AC
contract = D / "docs/orchestration/state/s5c/contract.json"
U, names = AC.sc.reported_functionals(json.loads(contract.read_text()))
n = U.shape[1]; rng = np.random.default_rng(7)
A = T / "assess"; (A / "data" / "boot").mkdir(parents=True)
base = rng.uniform(0.5, 2.0, n)
meta = json.dumps({"schema": "synthetic"})
def save(p, x): np.savez(p, xsec_flat=x.astype(np.float32) if "upcast" not in str(p) else x, meta=np.array(meta))
for i in range(1, 101): save(A / "data" / "boot" / f"boot_b{i}.npz", base * (1 + 0.01 * rng.standard_normal(n)))
save(A / "data" / "data_R.npz", base); save(A / "data" / "data_R_upcast.npz", base.astype(np.float32).astype(float))
for i in (1, 2): save(A / "data" / f"data_R_jitteredge{i}.npz", base * (1 + 0.003 * rng.standard_normal(n)))
load_fn = AC.load_fn
# the producer's lines :147-151, run the plain way
dsig = np.array([load_fn(f, U)["f"] for f in sorted(glob.glob(str(A / "data" / "boot" / "boot_b*.npz")))]).std(0, ddof=1)
up = load_fn(A / "data" / "data_R_upcast.npz", U)["f"]
jit = [np.abs(load_fn(f, U)["f"] - up) / dsig for f in sorted(glob.glob(str(A / "data" / "data_R_jitteredge*.npz")))]
jmax = np.max(np.array(jit), axis=0)
a3 = {"median": float(np.median(jmax)), "max": float(jmax.max()), "argmax": names[int(jmax.argmax())]}
(T / "receipt.json").write_text(json.dumps({"functional_names": names, "A3": {"data_rounding_probe_over_data_sigma": a3}}))
np.save(T / "jmax_plain.npy", jmax); print("plain", a3)
