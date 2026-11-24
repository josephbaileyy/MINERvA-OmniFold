"""Peak RSS of p0's read pattern at full scale: fd_rpd_reco.py's Inputs.key loads one NPZ key at a time and keeps
no array; p0 reads pass_reco per playlist and, through pinned_flux_factors (fd_rpd_reco.py:2060-2097, called at :2189),
loads each playlist's four factor arrays together and checks them (isfinite, >= 0); runtime_estimate reads w_reco and
bkg_w per playlist and draws 262,144 Poisson numbers.

usage: python3 -I -B probe.py FIXTURE_DIR   (12 playlists, each at the largest playlist's size: an upper bound)
"""

import resource
import sys

import numpy as np

d = sys.argv[1]


def key(name, k):
    with np.load(f"{d}/{name}", allow_pickle=True) as archive:
        return np.asarray(archive[k])


rows = 0
for _ in range(12):
    with np.load(f"{d}/factors_big.npz", allow_pickle=False) as archive:
        arrays = {k: archive[k] for k in ("factor_1D", "factor_1M", "outside_1D", "outside_1M")}
    assert all(np.all(np.isfinite(arrays[f"factor_{g}"])) and np.all(arrays[f"factor_{g}"] >= 0) for g in ("1D", "1M"))
    del arrays
    rows += len(key("lat_big.npz", "pass_reco"))
    rows += len(key("lat_big.npz", "w_reco"))
    rows += len(key("lat_big_bkg.npz", "bkg_w"))
np.random.default_rng(20261104).poisson(1, 262_144)
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
scale = 1 if sys.platform == "darwin" else 1024  # ru_maxrss: bytes on macOS, KiB on Linux
print("rows touched", rows, "peak RSS bytes", peak * scale, "=", round(peak * scale / 1e9, 3), "GB")
