"""Replay a truth-fiducial bookkeeping change using the frozen high-momentum tables.

Run with the path to the receipt checkout. Writes a per-cell CSV beside this file.
Only recorded, negative, reconstructed tracks with an in-grid true muon move.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import uproot


def divide(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return zero in empty cells, matching the archived IBU replay."""
    return np.divide(
        a, b, out=np.zeros(np.broadcast_shapes(a.shape, b.shape)), where=b > 0
    )


def unfold_selected(migration: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Unfold to selected events in ten iterations with the selected MC prior."""
    prior = migration.sum(axis=0)
    response = divide(migration, prior)
    for _ in range(10):
        prior = prior * (response.T @ divide(target, response @ prior))
    return prior


def compare(checkout: Path) -> None:
    """Compare efficiency numerators and rerun signed IBU on the original grid."""
    state = checkout / "docs/orchestration/state"
    root = state / "precharge-20261125"
    replay = root / "inputs/replay"
    pz, pt = map(np.array, json.loads((replay / "axes.json").read_text()))
    cells = (len(pt) - 1) * (len(pz) - 1)
    cross = pd.read_csv(replay / "cross-section.csv")
    rows = np.arange(cells) % (len(pz) - 1)
    high = rows == len(pz) - 2
    assert np.array_equal(cross.ppar_low, pz[rows])
    assert np.array_equal(cross.pt_low, pt[np.arange(cells) // (len(pz) - 1)])
    efficiency = pd.read_csv(state / "ibu-chi2-20261123/resp/extract/fig5.csv")
    figure = np.full(cells, np.nan)
    figure[efficiency.ipt * (len(pz) - 1) + efficiency.ipz] = efficiency.value
    archive = np.load(replay / "playlists.npz")
    periods = sorted(k[:-4] for k in archive if k.endswith("_pot"))
    assert len(periods) == 12
    data_pot, mc_pot = sum(archive[k + "_pot"] for k in periods)
    scale = data_pot / mc_pot
    migration = scale * sum(archive[k + "_M"] for k in periods)
    background = scale * sum(archive[k + "_B"] for k in periods)
    observed = sum(archive[k + "_N"] for k in periods)
    gen = cross.truth_generated.to_numpy()
    selected = cross.selected_anywhere.to_numpy()
    delta = np.zeros_like(migration)
    for period in periods:
        events = pd.read_csv(root / "inputs/events" / f"{period}_MC.csv.gz")
        selected_cc = events.loc[
            (events.qp < 0)
            & (events.pdg == 14)
            & (events.current == 1)
            & (events.fid == 0)
            & events.true_pt.between(pt[0], pt[-1], inclusive="left")
            & events.true_pz.between(pz[0], pz[-1], inclusive="left")
        ]
        truth = (
            (np.searchsorted(pt, selected_cc.true_pt, side="right") - 1) * (len(pz) - 1)
            + np.searchsorted(pz, selected_cc.true_pz, side="right")
            - 1
        )
        reco = (
            (np.searchsorted(pt, selected_cc.pt, side="right") - 1) * (len(pz) - 1)
            + np.searchsorted(pz, selected_cc.pz, side="right")
            - 1
        )
        reco = np.where(
            selected_cc.pz < 60, reco, cells + (selected_cc.pz >= 80).astype(int)
        )
        increment = np.zeros_like(delta)
        np.add.at(increment, (reco, truth), selected_cc.tune_weight * scale)
        assert np.all(increment.sum(axis=1) <= archive[period + "_B"] * scale + 1e-7)
        delta += increment
    in_grid = migration[:cells].sum(axis=0)
    np.testing.assert_allclose(in_grid, cross.selected_in_grid, atol=1e-7)
    baseline = divide(
        unfold_selected(migration[:cells], (observed - background)[:cells]),
        divide(in_grid, gen),
    )
    np.testing.assert_allclose(baseline, cross.unfolded_signed_K10, atol=1e-7)
    area = (cross.pt_high - cross.pt_low) * (cross.ppar_high - cross.ppar_low)
    reported = cross.reported.astype(bool).to_numpy()
    weight = divide(cross.xsec_cm2_per_nucleon_per_GeVc_squared.to_numpy(), baseline)
    published = np.where(
        reported, divide(cross.published_xsec.to_numpy(), weight), baseline
    )
    with uproot.open(replay / "release.root") as release:
        covariance = (
            release["TotalCovariance"].member("fElements").reshape(cells, cells)
        )
        released_xsec = release["pt_pl_cross_section"].values().T.ravel()
    np.testing.assert_allclose(released_xsec, cross.published_xsec, rtol=1e-12, atol=0)
    np.testing.assert_array_equal(covariance.diagonal() > 0, reported)
    inverse_covariance = np.linalg.pinv(covariance[np.ix_(reported, reported)])
    high_area = area.to_numpy()[high]
    reference = sum(high_area * cross.published_xsec.to_numpy()[high])
    results = cross.loc[high, ["pt_low", "pt_high"]].copy()
    results["generated"] = gen[high]
    results["selected_anywhere"] = selected[high]
    results["nonfid_in_saved_acceptance"] = delta.sum(axis=0)[high]
    results["figure5_efficiency"] = figure[high]
    results["figure5_times_our_generated"] = (figure * gen)[high]
    for name, change in (
        ("unchanged", np.zeros_like(delta)),
        ("true40_60_only", delta * high),
        ("all_in_grid_true_muons", delta),
    ):
        mat = migration + change
        bkg = background - change.sum(axis=1)
        assert min(bkg) > -1e-6
        np.testing.assert_allclose(
            mat.sum(axis=1) + bkg, migration.sum(axis=1) + background
        )
        accepted = selected + change.sum(axis=0)
        counted = mat[:cells].sum(axis=0)
        signal = unfold_selected(mat[:cells], (observed - bkg)[:cells])
        for convention, numerator in (("in_grid", counted), ("anywhere", accepted)):
            counts = divide(signal, divide(numerator, gen))
            xsec = counts * weight
            ratio = xsec[high] / cross.published_xsec.to_numpy()[high]
            results[name + "_" + convention + "_ratio"] = ratio
            folded = (
                mat
                @ divide(
                    published * np.where(reported, divide(numerator, counted), 1), gen
                )
                + bkg
            )
            residual = observed - folded
            difference = (xsec - released_xsec)[reported]
            distance = difference @ inverse_covariance @ difference / reported.sum()
            print(
                name,
                convention,
                "chi2/205",
                distance,
                "column ratio",
                np.dot(high_area, xsec[high]) / reference,
                "cell range",
                ratio.min(),
                ratio.max(),
                "data-fold 40-60, 60-80, >=80",
                [residual[:cells][high].sum(), *residual[cells:]],
            )
    figure_ratio = (
        divide(in_grid[high], gen[high])
        / figure[high]
        * cross.xsec_cm2_per_nucleon_per_GeVc_squared.to_numpy()[high]
        / cross.published_xsec.to_numpy()[high]
    )
    results["figure5_substitution_only_ratio"] = figure_ratio
    columns = results.sum(numeric_only=True)
    print(
        "generated",
        columns.generated,
        "selected",
        columns.selected_anywhere,
        "known addition",
        columns.nonfid_in_saved_acceptance,
        "figure5 target",
        columns.figure5_times_our_generated,
    )
    results.to_csv(Path(__file__).with_name("true_40_60.csv"), index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    compare(parser.parse_args().checkout)
