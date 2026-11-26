"""Fit a shift of the MC charge decision in one training bin and test on both signs."""

import json

import numpy as np
import pandas as pd

from score import EVENTS, HERE, classify, periods, pot, prior_fit


def fit_threshold(qp: np.ndarray, weights: np.ndarray, target: float) -> float:
    """Return the threshold giving the nearest weighted negative count."""
    values, inverse = np.unique(qp, return_inverse=True)
    cumulative = np.r_[0.0, np.cumsum(np.bincount(inverse, weights=weights))]
    nearest = int(np.argmin(abs(cumulative - target)))
    if nearest == 0:
        return float(values[0])
    if nearest == len(values):
        return float(np.nextafter(values[-1], np.inf))
    return float((values[nearest] + values[nearest - 1]) / 2)


def main() -> None:
    records = []
    for period in periods:
        for sample in ("Data", "MC"):
            frame = classify(
                pd.read_csv(EVENTS / f"{period}_{sample}.csv.gz"), sample == "Data"
            )
            frame = frame.loc[
                frame.sign.isin(["-", "+"]), ["band", "qp", "fold"]
            ].copy()
            if sample == "MC":
                frame["fold"] *= pot[period][0] / pot[period][1]
            frame["sample"] = sample
            frame["playlist"] = period
            records.append(frame)
    events = pd.concat(records, ignore_index=True)
    training = events[events.playlist.isin(prior_fit["training"]) & (events.band == 1)]
    target = sum((training["sample"] == "Data") & (training.qp < 0))
    sim = training[training["sample"] == "MC"]
    threshold = fit_threshold(sim.qp.values, sim.fold.values, target)
    counts = []
    for split in ("training", "validation"):
        subset = events[events.playlist.isin(prior_fit[split])]
        for band, frame in subset.groupby("band"):
            mc = frame[frame["sample"] == "MC"]
            data = frame[frame["sample"] == "Data"]
            for sign in ("-", "+"):
                nominal = (mc.qp < 0) if sign == "-" else (mc.qp > 0)
                varied = (mc.qp < threshold) if sign == "-" else (mc.qp >= threshold)
                observed = (data.qp < 0) if sign == "-" else (data.qp > 0)
                w = mc.loc[varied, "fold"]
                counts.append(
                    {
                        "split": split,
                        "band": band,
                        "sign": sign,
                        "observed": observed.sum(),
                        "nominal": mc.loc[nominal, "fold"].sum(),
                        "shifted": w.sum(),
                        "shifted_sumw2": (w**2).sum(),
                    }
                )
    report = pd.DataFrame(counts)
    for _, cell in report.groupby(["split", "band"]):
        np.testing.assert_allclose(
            cell.nominal.sum(), cell.shifted.sum(), atol=1e-7, rtol=0
        )
    report.to_csv(HERE / "shifted-threshold.csv", index=False)
    (HERE / "shifted-threshold.json").write_text(
        json.dumps(
            {
                "mc_qp_threshold_inverse_GeV_c": threshold,
                "training_negative_40_60": int(target),
                "negative_nominal": float(sim.loc[sim.qp < 0, "fold"].sum()),
                "negative_at_threshold": float(
                    sim.loc[sim.qp < threshold, "fold"].sum()
                ),
                "training": prior_fit["training"],
                "validation": prior_fit["validation"],
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
