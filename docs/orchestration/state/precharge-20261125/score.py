"""Compare both signs of reconstructed MINOS q/p before imposing the sign cut."""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
EVENTS = Path(os.environ.get("PRECHARGE_EVENTS", HERE))
REPLAY = HERE / "inputs" / "replay"
CONTROL = HERE / "inputs" / "control"
PZ, PT = map(np.array, json.loads((REPLAY / "axes.json").read_text()))
EDGES = [20, 40, 60, 80, np.inf]
Q_EDGES = [
    -np.inf,
    -0.05,
    -0.025,
    -1 / 60,
    -0.0125,
    -0.01,
    -0.005,
    0,
    0.005,
    0.01,
    0.0125,
    1 / 60,
    0.025,
    0.05,
    np.inf,
]
period_mc = np.load(REPLAY / "playlists.npz")
prior_quality = np.load(CONTROL / "quality.npz")
prior_fit = json.loads((CONTROL / "results.json").read_text())
periods = sorted(prior_quality.files)
pot = {pl: period_mc[pl + "_pot"] for pl in periods}
merged_pot = sum(pot.values())
bands = np.arange(224) % 16
published = pd.read_csv(REPLAY / "cross-section.csv")


def ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.divide(a, b, out=np.zeros_like(a, dtype=float), where=b > 0)


def published_weights() -> np.ndarray:
    """Convert the in-domain nominal generated template to the all-selected fold."""
    r = published
    weights = ratio(r.unfolded_signed_K10.values, r.truth_generated.values)
    ok = r.reported == 1
    weights[ok] *= (
        r.published_xsec[ok] / r.xsec_cm2_per_nucleon_per_GeVc_squared[ok]
    ) * (r.selected_anywhere[ok] / r.selected_in_grid[ok])
    return weights


def classify(frame: pd.DataFrame, data: bool) -> pd.DataFrame:
    r = frame
    r["sign"] = np.where(r.qp == 0, "zero", np.where(r.qp < 0, "-", "+"))
    bad = (~np.isfinite(r.qp)) | (r.qp <= -999) | (r.qp >= 999)
    r.loc[bad, "sign"] = "invalid"
    r["band"] = np.searchsorted(EDGES[1:], r.pz, side="right")
    assert r.band.max() <= 3 and r.band.min() >= 0
    r["precision"] = np.where(
        (r.curv == 1) & np.isfinite(r.fracerr) & (r.fracerr.abs() < 9999),
        np.where(r.fracerr.abs() < 0.3, "good", "poor"),
        "other",
    )
    r["origin"] = np.select(
        [
            np.full(len(r), data, dtype=bool),
            (r.current == 1) & (r.pdg == -14),
            (r.current == 1) & (r.pdg == 14),
        ],
        ["data", "antinu_mu_CC", "nu_mu_CC"],
        default="other",
    )
    r["fold"] = r.tune_weight.copy()
    r["tail"] = 0.0
    r["migration"] = 0.0
    if not data:
        fidcc = (r.origin == "nu_mu_CC") & (r.fid == 1)
        in_ps = (
            fidcc
            & (r.true_pz >= 1.5)
            & (r.true_pz < 60.0)
            & (r.true_pt >= 0.0)
            & (r.true_pt < 4.5)
            & (np.arctan2(r.true_pt, r.true_pz) < np.deg2rad(20))
        )
        idx = (
            (np.searchsorted(PT, r.true_pt[in_ps], side="right") - 1) * 16
            + np.searchsorted(PZ, r.true_pz[in_ps], side="right")
            - 1
        )
        r.loc[in_ps, "fold"] *= published_weights()[idx]
        r.loc[fidcc & (r.true_pz >= 60), "tail"] = r.tune_weight
        up = (
            in_ps
            & (r.true_pz >= 20)
            & (((r.band == 1) & (r.true_pz < 40)) | (r.band >= 2))
        )
        r.loc[up, "migration"] = r.fold
    return r


def projected(x: np.ndarray) -> np.ndarray:
    return np.r_[x[:224][bands == 14].sum(), x[:224][bands == 15].sum(), x[224:]]


def group(frame: pd.DataFrame, by: list[str], sample: str, pl: str) -> pd.DataFrame:
    fields = ["tune_weight", "fold", "fold_w2", "tune_w2", "tail", "migration"]
    sums = frame.groupby(by, observed=True)[fields].sum().reset_index()
    sums["sample"] = sample
    sums["playlist"] = pl
    return sums


def summarize(names: list[str], destination: Path) -> None:
    """Save global and held-out counts and check the earlier negative-sign marginals."""
    slices, qhist, closure = [], [], []
    for pl in names:
        for sample in ("Data", "MC"):
            is_data = sample == "Data"
            r = classify(pd.read_csv(EVENTS / f"{pl}_{sample}.csv.gz"), is_data)
            assert np.isfinite(r.tune_weight).all() and (r.tune_weight >= 0).all()
            r["fold_w2"] = r.fold**2
            r["tune_w2"] = r.tune_weight**2
            negative = r[r.sign == "-"]
            weighted = np.bincount(
                negative.band, weights=negative.tune_weight, minlength=4
            )
            expected = (
                period_mc[pl + "_N"]
                if is_data
                else period_mc[pl + "_M"].sum(1) + period_mc[pl + "_B"]
            )
            truth_check = projected(expected)
            np.testing.assert_allclose(weighted, truth_check, rtol=2e-9, atol=1e-7)
            closure.append([pl, sample, float(np.max(np.abs(weighted - truth_check)))])
            if not is_data:
                h = prior_quality[pl]
                folded = (
                    h[..., :224] @ published_weights() + h[..., 224:226].sum(-1)
                ).sum((1, 2))
                rebuilt = np.bincount(negative.band, weights=negative.fold, minlength=4)
                np.testing.assert_allclose(rebuilt, folded, rtol=2e-9, atol=1e-7)
                np.testing.assert_allclose(
                    np.bincount(negative.band, weights=negative["tail"], minlength=4),
                    h[..., 225].sum((1, 2)),
                    rtol=2e-9,
                    atol=1e-7,
                )
            slices.append(group(r, ["band", "sign", "precision", "origin"], sample, pl))
            signed = r[r.sign.isin(["-", "+"])].copy()
            signed["qbin"] = np.searchsorted(Q_EDGES, signed.qp, side="right") - 1
            qhist.append(group(signed, ["band", "qbin", "sign"], sample, pl))
    records = pd.concat(slices)
    records.to_csv(destination / "playlist-counts.csv", index=False)
    pd.DataFrame(closure, columns=["playlist", "sample", "max_abs_difference"]).to_csv(
        destination / "negative-closure.csv", index=False
    )
    factors = np.array(prior_fit["excess_factors"])
    reports = {}
    for label, chosen, individual in [
        ("merged", names, False),
        ("validation", [p for p in names if p in prior_fit["validation"]], True),
    ]:
        if not chosen:
            continue
        x = records[records.playlist.isin(chosen)].copy()
        for key in ["tune_weight", "fold", "tail", "migration", "fold_w2", "tune_w2"]:
            scale = [
                1
                if s == "Data"
                else pot[p][0] / pot[p][1]
                if individual
                else merged_pot[0] / merged_pot[1]
                for p, s in zip(x.playlist, x["sample"])
            ]
            x[key] *= np.array(scale) ** (2 if key.endswith("w2") else 1)
        x["extra_true_tail"] = x.fold + x["tail"] * (factors[0, x.band] - 1)
        x["extra_upward_migrants"] = x.fold + x.migration * (factors[1, x.band] - 1)
        fields = [
            "tune_weight",
            "fold",
            "tail",
            "migration",
            "tune_w2",
            "fold_w2",
            "extra_true_tail",
            "extra_upward_migrants",
        ]
        for category, extra in [
            ("all", []),
            ("quality", ["precision"]),
            ("origin", ["origin"]),
        ]:
            table = (
                x.groupby(["band", "sign", "sample"] + extra)[fields]
                .sum()
                .reset_index()
            )
            if (
                label == "validation"
                and category == "all"
                and set(chosen) == set(prior_fit["validation"])
            ):
                negative = table[table.sign == "-"].sort_values("band")
                mc = negative[negative["sample"] == "MC"]
                indices = ["fold", "extra_true_tail", "extra_upward_migrants"]
                np.testing.assert_allclose(
                    mc[indices].to_numpy().T,
                    prior_fit["raw_prediction_totals"],
                    rtol=1e-9,
                    atol=1e-7,
                )
                np.testing.assert_array_equal(
                    negative.loc[negative["sample"] == "Data", "fold"],
                    prior_fit["data_totals"],
                )
            table.to_csv(destination / f"{label}-{category}.csv", index=False)
        reports[label] = chosen
    q = pd.concat(qhist)
    for field in ("tune_weight", "fold", "tail", "migration", "tune_w2", "fold_w2"):
        q.loc[q["sample"] == "MC", field] *= (merged_pot[0] / merged_pot[1]) ** (
            2 if field.endswith("w2") else 1
        )
    q = (
        q.groupby(["band", "qbin", "sign", "sample"])[
            ["tune_weight", "fold", "tune_w2", "fold_w2"]
        ]
        .sum()
        .reset_index()
    )
    q["qp_low"] = [Q_EDGES[i] for i in q.qbin]
    q["qp_high"] = [Q_EDGES[i + 1] for i in q.qbin]
    q.to_csv(destination / "signed-qp.csv", index=False)
    (destination / "scope.json").write_text(
        json.dumps(
            {
                "groups": reports,
                "fit_factors": factors.tolist(),
                "pz_edges": [20, 40, 60, 80, "inf"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("playlists", nargs="*", default=periods)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True)
    summarize(args.playlists, args.output)
