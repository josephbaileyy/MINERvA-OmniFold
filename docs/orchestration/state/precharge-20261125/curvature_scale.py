"""Check the relative curvature scale and rebin held-out data at fixed transverse acceptance."""

import numpy as np
import pandas as pd

from score import EVENTS, pot, prior_fit

EDGES = [20, 40, 60, 80, np.inf]
OFFSET = 0.036


def load_tracks(periods: list[str], sample: str) -> pd.DataFrame:
    frames = []
    for period in periods:
        frame = pd.read_csv(EVENTS / f"{period}_{sample}.csv.gz")
        if sample == "MC":
            frame["tune_weight"] *= pot[period][0] / pot[period][1]
        frames.append(frame[frame.qp.lt(0) & frame.curv.eq(1)])
    tracks = pd.concat(frames, ignore_index=True)
    tracks["curvature_p"] = 1 / abs(tracks.qp)
    tracks["total_p"] = np.hypot(tracks.pz, tracks.pt)
    return tracks


def weighted_median(values: pd.Series, weights: pd.Series) -> float:
    order = np.argsort(values.to_numpy())
    cumulative = np.cumsum(weights.to_numpy()[order])
    return float(
        values.to_numpy()[order][np.searchsorted(cumulative, cumulative[-1] / 2)]
    )


train = prior_fit["training"]
for lo, hi in [(35, 40), (55, 60)]:
    medians = []
    for sample in ("Data", "MC"):
        tracks = load_tracks(train, sample)
        selected = tracks[
            tracks.curvature_p.between(lo, hi, inclusive="left")
            & tracks.fracerr.abs().lt(0.30)
        ]
        medians.append(
            weighted_median(
                (selected.total_p - selected.curvature_p) / selected.curvature_p,
                selected.tune_weight,
            )
        )
    print(
        f"Curvature momentum {lo}–{hi}, difference of median fractional offsets "
        f"(data minus MC): {medians[0] - medians[1]:.4f}"
    )

data = load_tracks(prior_fit["validation"], "Data")
nominal = np.histogram(data.pz, EDGES)[0]
np.testing.assert_array_equal(nominal, prior_fit["data_totals"])
projected = data.pz * (1 - OFFSET * data.curvature_p / data.total_p)
varied = np.histogram(projected, EDGES)[0]
prediction = np.array(prior_fit["raw_prediction_totals"][0])
print("Held-out negative data nominal:", nominal)
print("Removing 3.6% of curvature momentum, projected along beam:", varied)
print("Nominal data minus fold:", np.round(nominal - prediction, 1))
print("Varied data minus fold:", np.round(varied - prediction, 1))
