"""Shared pieces for tests A and B (DECLARATION.md). Reuses ../test1/events.py."""

import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "test1"))
from events import TRAINING, VALIDATION, load  # noqa: E402

FLOOR = 0.02
MIN_FOLD = 5.0
BANDS = [20, 40, 50, 60, 80, np.inf]


def frame():
    x = load()
    x["w0"] = np.where(x.is_data, 1.0, x.fold * x.own_scale)
    return x


def chi2(obs, mu, var_mc, var_par, floor=True):
    var = mu + var_mc + var_par + ((FLOOR * mu) ** 2 if floor else 0.0)
    return float(np.sum((obs - mu) ** 2 / var))


def pvalue(c, ndf):
    return float(stats.chi2.sf(c, ndf))


def directions():
    """Primary (fit training, score held out) and swap."""
    return [("primary", TRAINING, VALIDATION), ("swap", VALIDATION, TRAINING)]
