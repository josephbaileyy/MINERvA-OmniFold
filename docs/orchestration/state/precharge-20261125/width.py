"""Test inverse-momentum resolution against the digitized Fig. 3 migration cell."""

import csv
from pathlib import Path

import numpy as np

from score import published_weights, merged_pot, period_mc, periods

here = Path(__file__).resolve().parent
scan = np.load(here / "inputs/control/width.npz")
scale = merged_pot[0] / merged_pot[1]
counts = scan["counts"] * scale
high = np.arange(224) % 16 >= 14
nominal = sum(period_mc[p + "_M"] for p in periods) * scale
rows = np.vstack([nominal[:224].reshape(14, 16, 224).sum(0), nominal[224:].sum(0)])
np.testing.assert_allclose(counts[0], rows[:, high], atol=1e-7)
fig3 = here.parent / "ibu-chi2-20261123/resp/extract/fig3.csv"
with fig3.open() as stream:
    cell = next(
        r
        for r in csv.DictReader(stream)
        if (r["true_bin"], r["reco_bin"]) == ("14", "15")
    )
outcomes = counts[:, :, ::2].sum(axis=2)
delta = (counts - counts[0]) @ published_weights()[high]
for bins in [16, 17]:
    probability = outcomes[:, 15] / outcomes[:, :bins].sum(axis=1)
    closest = np.argmin(abs(probability - float(cell["value"])))
    print(
        "Normalization rows, width, migration probability:",
        bins,
        scan["factors"][closest],
        probability[closest],
    )
    print("Change at reco 20–40, 40–60, ≥60:", np.round(delta[closest, 14:], 1))
