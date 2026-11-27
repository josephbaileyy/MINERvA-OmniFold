"""Load the saved event tables with the all-selected fold weight of ../score.py."""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
os.environ.setdefault("PRECHARGE_EVENTS", str(HERE.parent / "inputs" / "events"))
from score import EVENTS, classify, merged_pot, periods, pot, prior_fit  # noqa: E402

CACHE = HERE / ".events-cache.pkl"


def load() -> pd.DataFrame:
    """All tracks in all 12 playlists; MC weights carry both POT scalings."""
    if CACHE.exists():
        return pd.read_pickle(CACHE)
    frames = []
    for pl in periods:
        for sample in ("Data", "MC"):
            r = classify(pd.read_csv(EVENTS / f"{pl}_{sample}.csv.gz"), sample == "Data")
            r["playlist"] = pl
            r["is_data"] = sample == "Data"
            merged = 1.0 if sample == "Data" else merged_pot[0] / merged_pot[1]
            own = 1.0 if sample == "Data" else pot[pl][0] / pot[pl][1]
            r["merged_scale"] = merged
            r["own_scale"] = own
            frames.append(r)
    x = pd.concat(frames, ignore_index=True)
    x["evis"] = x.pz + x.energy
    x["pcurv"] = np.where(x.qp != 0, 1 / x.qp.abs().where(x.qp != 0, np.nan), np.nan)
    x.to_pickle(CACHE)
    return x


TRAINING = prior_fit["training"]
VALIDATION = prior_fit["validation"]
