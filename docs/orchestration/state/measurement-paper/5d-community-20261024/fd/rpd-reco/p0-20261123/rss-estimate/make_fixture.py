"""Write a synthetic dump the size of the largest playlist (5,916,895 MC rows, job A's logs) and its background file.

usage: python3 -I -B make_fixture.py OUTDIR
The members mirror a real dump's: an MCreco block p0 never reads, w_reco (float64), pass_reco and pass_truth (bool);
the background file holds bkg_reco and bkg_w (114,278 rows, the largest bkg_rows), compressed as the dumps are; and a
factor product with pinned_flux_factors' four keys, uncompressed (the real flux-factors-1M.npz is 106,505,136 bytes).
"""

import os
import sys

import numpy as np

out = sys.argv[1]
rng = np.random.default_rng(1)
n = 5_916_895
np.savez_compressed(
    os.path.join(out, "lat_big.npz"),
    MCreco=rng.normal(size=(n, 6)),
    w_reco=rng.random(n),
    pass_reco=rng.random(n) < 0.6,
    pass_truth=np.ones(n, bool),
)
np.savez_compressed(os.path.join(out, "lat_big_bkg.npz"), bkg_reco=rng.normal(size=(114_278, 6)), bkg_w=rng.random(114_278))
np.savez(  # flux-factors-<PL>.npz: uncompressed, 4 full-row arrays (pinned_flux_factors' keys), about 106 MB at this size
    os.path.join(out, "factors_big.npz"),
    factor_1D=rng.random(n),
    factor_1M=rng.random(n),
    outside_1D=rng.random(n) < 0.01,
    outside_1M=rng.random(n) < 0.01,
)
print({f: os.path.getsize(os.path.join(out, f)) for f in sorted(os.listdir(out))})
