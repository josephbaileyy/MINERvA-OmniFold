"""true_energies on the synthetic full-size sidecar, the staged copy outside the protected roots (as in the run)."""
import resource, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, sys.argv[1]); import fd_rpd_reco as R
work = Path(sys.argv[2]); N = 32846302
counts = np.full(12, N // 12); counts[-1] += N - counts.sum()
rows = dict(zip(R.PLAYLISTS, counts.tolist()))
side = work / "truthx_RDX_ALL.npz"
class Fake:
    config = {"true_energy": {"path": str(side), "sha256": "x" * 64, "npz_sha256": "6" * 64}}
    roots = [side]
    def copy(self, source, expected): return work / "staged" / "staged.npz"
rss0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
t = time.time()
try:
    energies, record = R.true_energies(Fake(), rows)
except Exception as e:
    print("ERROR", type(e).__name__, e); raise
te = time.time() - t
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f"true_energies: {te:.1f} s, status {record['status']}, rows {record['source']['rows']}, "
      f"spots {sum(len(v['rows']) for v in record['spots'].values())}; peak RSS {rss / 2**30:.2f} GiB "
      f"(before {rss0 / 2**30:.2f} GiB)")
