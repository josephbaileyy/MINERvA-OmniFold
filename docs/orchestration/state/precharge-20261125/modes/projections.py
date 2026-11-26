"""Reproject both cross sections in one published covariance eigenbasis."""

import csv
import json
from pathlib import Path

import numpy as np
import uproot

here = Path(__file__).resolve().parent
replay = here.parent / "inputs" / "replay"
receipt = here.parents[1] / "ibu-chi2-20261123" / "regenA5" / "out"
with uproot.open(replay / "release.root") as release:
    published = release["pt_pl_cross_section"].values().T.ravel()

    def matrix(key):
        return release[key].member("fElements").reshape(224, 224)

    mask = np.diag(matrix("StatOnlyCovariance")) > 0
    covariance = matrix("TotalCovariance")[np.ix_(mask, mask)]
assert mask.sum() == 205
lam, directions = np.linalg.eigh(covariance)
keep = lam > lam.max() * 1e-15
assert keep.all()
paths = [here / "before.root", replay / "reference-run.root"]
spectra = []
for path in paths:
    with uproot.open(path) as root:
        spectra.append(root["hXSec2D"].values().ravel())
residuals = (np.array(spectra) - published)[:, mask]
z = residuals @ directions / np.sqrt(lam)
after = json.loads((receipt / "readout_e.json").read_text())
before = json.loads((receipt / "readout_old.json").read_text())
# Orient the reported eigenvectors to the signs in the A5 readout. Both
# spectra and every additional diagnostic use the same oriented vectors.
for row in after["modes"]:
    k = row["lam_rank"]
    directions[:, k] *= np.sign(row["eigpull"] * z[1, k])
raw = residuals @ directions
z = raw / np.sqrt(lam)
modes = np.argsort(z[1] ** 2)[::-1][:6]
q = z * z
for i, control in enumerate([before, after]):
    np.testing.assert_allclose(q[i].sum(), control["chi2_modes"], rtol=5e-6)
    np.testing.assert_allclose(
        q[i, :10].sum() / q[i].sum(), control["share10_smallest"], rtol=5e-6
    )
    for k in modes:
        r = next(r for r in control["modes"] if r["lam_rank"] == k)
        np.testing.assert_allclose(z[i, k], r["eigpull"], rtol=5e-6)
np.testing.assert_array_equal(modes, [m["lam_rank"] for m in after["modes"][:6]])
jz = np.arange(224)[mask] % 16
# Replay the separate all-selected K=10 IBU convention on the published axes.
bins = np.genfromtxt(replay / "cross-section.csv", delimiter=",", names=True)
in_any = np.divide(
    bins["selected_in_grid"],
    bins["selected_anywhere"],
    out=np.ones(224),
    where=bins["selected_anywhere"] > 0,
)
ibu = bins["xsec_cm2_per_nucleon_per_GeVc_squared"]
ibu_z = ((np.array([ibu, ibu * in_any]) - published)[:, mask] @ directions) / np.sqrt(
    lam
)
print("K10 check chi2 / 205", np.sum(ibu_z**2, axis=1) / 205)
out = []
for i, k in enumerate(modes):
    direction = directions[:, k]
    tail = jz == 15
    tailz = residuals[:, tail] @ direction[tail] / np.sqrt(lam[k])
    row = dict(
        panel="abcdef"[i],
        ascending_eigenvalue_rank_zero_based=int(k),
        before_contribution_rank=int(np.argsort(np.argsort(-q[0]))[k] + 1),
        after_contribution_rank=i + 1,
        relative_eigenvalue=lam[k] / lam[-1],
        norm2_in_20_40=sum(direction[jz == 14] ** 2),
        norm2_in_40_60=sum(direction[tail] ** 2),
        c_before=raw[0, k],
        c_after=raw[1, k],
        z_before=z[0, k],
        z_after=z[1, k],
        z_change=z[1, k] - z[0, k],
        chi2_change=q[1, k] - q[0, k],
        z_from_40_60_before=tailz[0],
        z_from_40_60_after=tailz[1],
        ibu10_in_grid_z=ibu_z[0, k],
        ibu10_all_selected_z=ibu_z[1, k],
    )
    out.append(row)
with (here / "six-modes.csv").open("w") as f:
    writer = csv.DictWriter(f, fieldnames=out[0], lineterminator="\n")
    writer.writeheader()
    writer.writerows(out)
print("Total, ten smallest, fixed six, five high, lower mode")
for v in q:
    print(
        v.sum(),
        v[:10].sum(),
        v[modes].sum(),
        v[modes[[0, 2, 3, 4, 5]]].sum(),
        v[modes[1]],
    )
for r in out:
    print(
        r["panel"],
        *[
            f"{r[key]:.5g}"
            for key in (
                "c_before",
                "c_after",
                "z_before",
                "z_after",
                "z_change",
                "norm2_in_20_40",
                "norm2_in_40_60",
                "z_from_40_60_before",
                "z_from_40_60_after",
                "ibu10_in_grid_z",
                "ibu10_all_selected_z",
            )
        ],
    )
