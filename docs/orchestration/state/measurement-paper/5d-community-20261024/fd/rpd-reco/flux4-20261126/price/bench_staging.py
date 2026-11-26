"""flux4's added work, measured: a synthetic sidecar of the real schema and row count, custody-style staging
(two full reads with sha256 plus one copy), then fd_rpd_reco.true_energies itself; wall time and peak RSS."""
import hashlib, json, resource, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, sys.argv[1]); import fd_rpd_reco as R
work = Path(sys.argv[2]); N = 32846302
PL = R.PLAYLISTS
counts = np.full(12, N // 12); counts[-1] += N - counts.sum()
rows = dict(zip(PL, counts.tolist()))
side = work / "truthx_RDX_ALL.npz"
t0 = time.time()
rng = np.random.default_rng(1)
tx = np.empty((N, 5)); tx[:, 0] = rng.uniform(1500, 20000, N); tx[:, 1:] = rng.normal(size=(N, 4))
pi = np.repeat(np.arange(12), counts)
ids = np.column_stack([pi, rng.integers(1, 10**5, N), rng.integers(1, 100, N), np.arange(N)]).astype(np.int64)
meta = {"schema": R.SIDECAR_SCHEMA, "npz_sha256": "6" * 64, "rows": N, "playlists": [[p, f"/x/{p}"] for p in PL]}
np.savez(side, truthx=tx, truthx_names=np.array(R.SIDECAR_TRUTHX), mc_id=ids, mc_id_names=np.array(R.SIDECAR_IDS),
         meta=json.dumps(meta))
del tx, ids, pi
print(f"synthetic sidecar {side.stat().st_size} bytes, written in {time.time() - t0:.1f} s", flush=True)
def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(1 << 24): h.update(b)
    return h.hexdigest()
t1 = time.time(); d = digest(side); shutil.copyfile(side, work / "staged.npz"); d2 = digest(work / "staged.npz")
stage = time.time() - t1
print(f"staging (read+sha256, copy, read+sha256): {stage:.1f} s", flush=True)
class Fake:
    config = {"true_energy": {"path": str(side), "sha256": d, "npz_sha256": "6" * 64}}
    roots = [work]
    def copy(self, source, expected): return work / "staged.npz"
rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
t2 = time.time(); energies, record = R.true_energies(Fake(), rows); te = time.time() - t2
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f"true_energies: {te:.1f} s, status {record['status']}, rows {record['source']['rows']}; "
      f"peak RSS {rss / 2**30:.2f} GiB (before the call {rss0 / 2**30:.2f} GiB; macOS ru_maxrss is bytes)", flush=True)
