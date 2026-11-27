"""Tabulate the declared me1A true 40–60 GeV/c column per 10²⁰ MC POT."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    """Write the selected-anywhere and generated counts in the released true p_T bins."""
    folder = Path(__file__).resolve().parent
    inputs = folder.parent / "inputs"
    pz, pt = map(np.array, json.loads((inputs / "replay/axes.json").read_text()))
    assert tuple(pz[-2:]) == (40.0, 60.0)
    with np.load(inputs / "replay/playlists.npz") as archive:
        generated = archive["1A_T"].reshape(len(pt) - 1, len(pz) - 1)[:, -1]
        selected = archive["1A_S"].reshape(len(pt) - 1, len(pz) - 1)[:, -1]
        _, mc_pot = archive["1A_pot"]
    events = pd.read_csv(inputs / "events/1A_MC.csv.gz")
    assert (events.pz >= 20).all() and events.pt.between(0, 4.5, inclusive="left").all()
    tracks = events.loc[
        (events.qp < 0)
        & (events.pdg == 14)
        & (events.current == 1)
        & (events.fid == 0)
        & events.true_pz.between(40, 60, inclusive="left")
        & events.true_pt.between(pt[0], pt[-1], inclusive="left")
    ]
    added, _ = np.histogram(tracks.true_pt, bins=pt, weights=tracks.tune_weight)
    np.testing.assert_allclose(added.sum(), tracks.tune_weight.sum())
    scale = 1e20 / mc_pot
    counts = pd.DataFrame(
        {
            "true_pt_low_GeVc": pt[:-1],
            "true_pt_high_GeVc": pt[1:],
            "selected_anywhere_per_1e20_MC_POT": selected * scale,
            "saved_nonfid_addition_per_1e20_MC_POT": added * scale,
            "partial_selected_numerator_per_1e20_MC_POT": (selected + added) * scale,
            "generated_denominator_per_1e20_MC_POT": generated * scale,
        }
    )
    counts.to_csv(folder / "me1a-counts.csv", index=False)
    print(f"me1A MC POT {mc_pot:.12g}; bins {len(counts)}")
    print(counts.iloc[:, 2:].sum().to_string())


if __name__ == "__main__":
    main()
