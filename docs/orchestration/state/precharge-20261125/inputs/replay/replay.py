"""Reconstruct the signed, ten-iteration IBU central value from playlist histograms."""

import csv
import json
from pathlib import Path

import numpy as np
import uproot
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parents[2] / "ibu-chi2-20261123"
archive = np.load(HERE / "playlists.npz")
feed = np.load(HERE / "feed.npz")
periods = sorted(key[:-4] for key in archive.files if key.endswith("_pot"))
f = uproot.open(HERE / "release.root")
e = uproot.open(HERE / "reference-run.root")
h = f["pt_pl_cross_section"]
pz, pt = (axis.edges() for axis in h.axes)
area = np.outer(np.diff(pt), np.diff(pz)).ravel()
nz, cells = len(pz) - 1, len(area)
published = h.values().T.ravel()
cov = f["TotalCovariance"].member("fElements").reshape(cells, cells)
mask = np.diag(cov) > 0
np.testing.assert_array_equal(mask, published > 0)
inverse = np.linalg.pinv(cov[np.ix_(mask, mask)])
col = np.arange(cells) % nz
archive_axes = json.loads((HERE / "axes.json").read_text())
for released, archived in zip((pz, pt), archive_axes):
    np.testing.assert_array_equal(released, archived)
flux = e["hFlux_pt"].values() / 1e4
nucleons = e["nNucleons"].member("fVal")


def _ratio(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.divide(
        x, y, out=np.zeros(np.broadcast_shapes(x.shape, y.shape)), where=y > 0
    )


def _ibu(m: np.ndarray, t: np.ndarray, y: np.ndarray, iterations: int) -> np.ndarray:
    response = _ratio(m, t)
    eff = response.sum(0)
    u = t.copy()
    for _ in range(iterations):
        u = _ratio(u * (response.T @ _ratio(y, response @ u)), eff)
    return u


def _pool(names: list[str], per_period_exposure: bool) -> dict:
    pot = sum(archive[pl + "_pot"] for pl in names)
    group = {}
    for key in ("N", "B", "M", "T", "S", "Sw", "feed"):
        vals = []
        for pl in names:
            pd, pm = archive[pl + "_pot"] if per_period_exposure else pot
            values = feed[pl] if key == "feed" else archive[pl + "_" + key]
            vals.append(values if key == "N" else values * (pd / pm))
        group[key] = sum(vals)
    group["pot"] = pot
    return group


def _bands(x: np.ndarray) -> np.ndarray:
    return np.r_[x[:cells][col == 14].sum(), x[:cells][col == 15].sum(), x[cells:]]


def _distance(x: np.ndarray) -> float:
    delta = (x - published)[mask]
    return float(delta @ inverse @ delta / mask.sum())


g = _pool(periods, False)
m, t, n, b, s, sw = [g[k] for k in ("M", "T", "N", "B", "S", "Sw")]
exposure = np.repeat(flux, nz) * g["pot"][0] * nucleons
unit = 1 / (exposure * area)
np.testing.assert_array_equal(n[:cells], e["hDataReco2D"].values().ravel())
np.testing.assert_allclose(
    b[:cells], e["hBkgReco2D"].values().ravel(), atol=1e-8, rtol=1e-11
)
np.testing.assert_allclose(t, e["hEffDen"].values().ravel(), atol=1e-7, rtol=1e-11)
np.testing.assert_allclose(
    m[:cells].sum(0), e["hEffNum"].values().ravel(), atol=1e-8, rtol=1e-11
)
u = _ibu(m[:cells], t, (n - b)[:cells], 10)
xsec = u * unit
reference = np.load(HERE / "signed-reference.npz")
refined = _ibu(m[:cells], t, reference["refined_y"], 10) * unit
for result, name in ((xsec, "signed_xsec"), (refined, "refined_xsec")):
    row = np.where(reference["ks"] == 10)[0].item()
    np.testing.assert_allclose(result, reference[name][row], rtol=1e-10, atol=1e-58)
np.testing.assert_allclose(
    (n - b)[:cells], reference["signed_y"], rtol=1e-10, atol=1e-8
)
# Below the reporting threshold the input to the fold is our own estimate.
pub_counts = np.where(mask, published / unit, u)
fold = m @ _ratio(pub_counts, t) + b
any_fold = (
    m @ _ratio(pub_counts * np.where(mask, _ratio(s, m[:cells].sum(0)), 1), t) + b
)

tune = np.zeros(cells)
for row in csv.DictReader((HERE / "tune-v1.csv").open()):
    tune[(int(row["Ptbin"]) - 1) * nz + int(row["P||bin"]) - 1] = float(
        row["model_cross_section"]
    )


def _shape_gap(prior: np.ndarray) -> list:
    pub_truth = tune / unit
    scale = pub_truth[mask].sum() / prior[mask].sum()
    return [
        pub_truth[col == j].sum() / prior[col == j].sum() / scale - 1 for j in (14, 15)
    ]


z = np.load(HERE / "flux.npz")
scale = g["pot"][0] / g["pot"][1]
np.testing.assert_allclose(z["T"][0] * scale, t, rtol=1e-10, atol=1e-7)
np.testing.assert_allclose(z["M"][0] * scale, m, rtol=1e-10, atol=1e-7)
tf, mf = z["T"][1] * scale, z["M"][1] * scale
flux_fold = mf @ _ratio(pub_counts, tf) + b
fig5 = np.zeros(cells)
for row in csv.DictReader((FIGURES / "resp/extract" / "fig5.csv").open()):
    fig5[int(row["ipt"]) * nz + int(row["ipz"])] = float(row["value"])
points = {}
for row in csv.DictReader((FIGURES / "fig2" / "fig2_points.csv").open()):
    k = int(row["g"]), row["kind"]
    step = float(row["quantum_count"]) * area[k[0]] / float(row["area"])
    if k not in points or step < points[k][0]:
        points[k] = step, float(row["ydisp"]) / float(row["factor"]) * 1e5 * area[k[0]]
fig2 = {
    kind: sum(v[1] for (i, k), v in points.items() if col[i] == 15 and k == kind)
    for kind in ("data", "mc")
}
print(
    "axes",
    pz,
    pt,
    "reported cells",
    mask.sum(),
    "POT(data,MC)",
    g["pot"],
    "flux /cm2/POT",
    flux[0],
    "nucleons",
    nucleons,
)
print(
    "signed measurable minimum",
    min(n[:cells] - b[:cells]),
    "selected total",
    n[:cells].sum(),
)
print(
    "reported-cell integrals signed 10 / paper:",
    (xsec * area)[mask].sum(),
    (published * area)[mask].sum(),
)
print(
    "chi2/205 signed K5,K10, refined K10:",
    _distance(_ibu(m[:cells], t, (n - b)[:cells], 5) * unit),
    _distance(xsec),
    _distance(refined),
)
print(
    "literal rounded published POT, flux, targets; signed K10 chi2/205:",
    _distance(u / (area * 1.061e21 * 6.32e-8 * 3.23e30)),
)
print(
    "20-40,40-60,60-80,>=80 rows: data, nominal MC, B, published fold, Valencia fold, all-selected interpretation, own K10 fold"
)
print(
    np.array(
        [
            _bands(v)
            for v in (
                n,
                m.sum(1) + b,
                b,
                fold,
                flux_fold,
                any_fold,
                m @ _ratio(u, t) + b,
            )
        ]
    ).T
)
print("fig2 exact-area fine-copy counts", fig2)
print(
    "Tune v1 shape gap at true 20-40 and 40-60 nominal/Valencia",
    _shape_gap(t),
    _shape_gap(tf),
)
print(
    "true 40–60: generated / selected (truth weights) / selected (reco weights) / selected in-grid / Fig5 weighted efficiency"
)
j = col == 15
print(
    t[j].sum(),
    sw[j].sum(),
    s[j].sum(),
    m[:cells, j].sum(),
    (t[j] * fig5[j]).sum() / t[j].sum(),
)
print("unfolded high column / paper", sum(u[j]) / sum(pub_counts[j]))
with (HERE / "cross-section.csv").open("w") as stream:
    w = csv.writer(stream, lineterminator="\n")
    w.writerow(
        [
            "pt_low",
            "pt_high",
            "ppar_low",
            "ppar_high",
            "reported",
            "data",
            "background",
            "truth_generated",
            "selected_in_grid",
            "selected_anywhere",
            "unfolded_signed_K10",
            "xsec_cm2_per_nucleon_per_GeVc_squared",
            "published_xsec",
        ]
    )
    for i in range(cells):
        ix, iz = divmod(i, nz)
        w.writerow(
            [
                pt[ix],
                pt[ix + 1],
                pz[iz],
                pz[iz + 1],
                int(mask[i]),
                int(n[i]),
                b[i],
                t[i],
                m[:cells, i].sum(),
                s[i],
                u[i],
                xsec[i],
                published[i],
            ]
        )
train = _pool(periods[::2], True)
control = _pool(periods[1::2], True)


def _predict(k: float, target: dict) -> np.ndarray:
    varied = train["B"] + (k - 1) * train["feed"]
    unfolded = _ibu(train["M"][:cells], train["T"], (train["N"] - varied)[:cells], 10)
    # Apply the training truth/MC ratio to an exposure-weighted, distinct MC sample.
    return (
        target["M"] @ _ratio(unfolded, train["T"])
        + target["B"]
        + (k - 1) * target["feed"]
    )


def _train_overflow(k: float) -> float:
    return float((_predict(k, train) - train["N"])[cells:].sum())


fitted = brentq(_train_overflow, 0, 10)
print(
    "training",
    periods[::2],
    "validation",
    periods[1::2],
    "fitted true >=60 factor",
    fitted,
)
print(
    "independent validation: data / nominal / fitted / (data minus nominal) / (data minus fitted)"
)
a, bb, cc = (
    _bands(v) for v in (control["N"], _predict(1, control), _predict(fitted, control))
)
print(np.array([a, bb, cc, a - bb, a - cc]).T)

print(
    "Nominal with in-domain flux reweighting, fixed backgrounds", _bands(mf.sum(1) + b)
)
print(
    "Raw in-grid totals signal, background, generated",
    m[:cells].sum(),
    b[:cells].sum(),
    t.sum(),
)
tail = _bands(g["feed"])
print("True >=60 contribution to the four reco bands", tail)
remaining = _bands(n - any_fold)
for idx in ([1], [2, 3]):
    extra = remaining[idx].sum() / tail[idx].sum()
    print(
        "Single true-tail multiplier, anchor band indices, residuals",
        1 + extra,
        idx,
        remaining - extra * tail,
    )
weighted_counts = pub_counts * np.where(mask, _ratio(s, m[:cells].sum(0)), 1)
fig5_factor = np.ones(cells)
assert (s[j & mask] > 0).all()
fig5_factor[j & mask] = (fig5 * t)[j & mask] / s[j & mask]
imposed = m @ _ratio(weighted_counts * fig5_factor, t) + b
print(
    "Impose true 40-60 Fig 5 per pT bin, data minus fold in four bands",
    _bands(n - imposed),
)
print(
    "True 40-60 selected in grid, pz overflow within pT acceptance, all other reco destinations",
    m[:cells, j].sum() / s[j].sum(),
    m[cells:, j].sum() / s[j].sum(),
    1 - m[:, j].sum() / s[j].sum(),
)
drawn = {
    (int(row["true_bin"]), int(row["reco_bin"])): float(row["value"])
    for row in csv.DictReader((FIGURES / "resp/extract" / "fig3.csv").open())
}
for true_bin, reco_bin in ((15, 15), (15, 14), (14, 15)):
    selected_column = m[:cells, col == true_bin].sum(1)
    print(
        "Truth, reco bin; in-grid conditional probability; PDF color estimate",
        true_bin,
        reco_bin,
        selected_column[col == reco_bin].sum() / selected_column.sum(),
        drawn[true_bin, reco_bin],
    )
with (HERE / "reco-bands.csv").open("w") as stream:
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        [
            "ppar_low",
            "ppar_high",
            "selected_data",
            "nominal_mc",
            "nominal_bkg",
            "fold_published",
            "fold_published_flux_swap",
            "fold_all_selected",
            "fold_imposed_fig5_true40",
            "fold_own_k10",
            "true_ge60_feed",
            "validation_data",
            "validation_nominal",
            "validation_scaled_tail",
        ]
    )
    writer.writerows(
        zip(
            (20, 40, 60, 80),
            (40, 60, 80, "inf"),
            *[
                _bands(v)
                for v in (
                    n,
                    m.sum(1) + b,
                    b,
                    fold,
                    flux_fold,
                    any_fold,
                    imposed,
                    m @ _ratio(u, t) + b,
                )
            ],
            tail,
            a,
            bb,
            cc,
        )
    )

full_rows = [
    json.loads(line)
    for line in (HERE / "full-phase-generated.jsonl").read_text().splitlines()
]
split_rows = [
    json.loads(line)
    for line in (HERE / "full-phase-playlists.jsonl").read_text().splitlines()
]
assert (
    [row["playlist"] for row in full_rows]
    == [row["pl"] for row in split_rows]
    == periods
)
for row in split_rows:
    np.testing.assert_allclose(row["pot"], archive[row["pl"] + "_pot"], rtol=1e-12)


def _project_full(key: str) -> np.ndarray:
    counts = scale * np.sum([row["groups"][key] for row in split_rows], axis=0)
    return np.array(
        [counts[1:4].sum(), counts[4:6].sum(), counts[6:8].sum(), counts[8:].sum()]
    )


np.testing.assert_allclose(_project_full("in_grid"), _bands(m.sum(1)), rtol=1e-11)
np.testing.assert_allclose(
    _project_full("true_60_80") + _project_full("true_80plus"), tail, rtol=1e-11
)
den = scale * np.sum(
    [[band["truth_w"] for band in row["stats"]] for row in full_rows], axis=0
)
dest = scale * np.sum(
    [[band["reco"] for band in row["stats"]] for row in full_rows], axis=0
)
np.testing.assert_allclose(dest[:, 1:4, 2].sum(0), tail[1:], rtol=1e-11)
print(
    "All truth pT, true 60-80 and >=80: generated",
    den,
    "reco 40-60/60-80/>=80",
    dest[:, 1:4, 2],
)
print(
    "Fixed weights with efficiency up to unity: maximum extra events in reco >=40 from true >=60",
    den.sum() - tail[1:].sum(),
    "combined all-selected residual",
    remaining[1:].sum(),
)
np.testing.assert_allclose(z["S"][0] * scale, s, rtol=1e-10, atol=1e-7)
print(
    "True 40-60 after Valencia reweight, in-grid / anywhere / Fig 5 with varied truth mix",
    mf[:cells, j].sum() / tf[j].sum(),
    z["S"][1, j].sum() * scale / tf[j].sum(),
    (tf[j] * fig5[j]).sum() / tf[j].sum(),
)
