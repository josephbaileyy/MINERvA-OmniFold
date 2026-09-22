"""The scalar input sets, by name, built from the cached populations. One definition, used by every
runner, so a table's input label always means the same columns.

Reco side (step 1) reads ONLY reconstructed quantities; `assert_reco_only` refuses a truth column.
Truth side (step 2) reads the four truth scalars.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np

# name -> list of (population key, column or None, label)
RECO_SETS = {
    "muon": [("reco", 0, "reco_pt"), ("reco", 1, "reco_pparallel")],
    "muon_had": [("reco", 0, "reco_pt"), ("reco", 1, "reco_pparallel"),
                 ("reco", 2, "reco_eavail"), ("reco", 3, "reco_q3"),
                 ("tok_sumE", None, "stored_token_sumE"), ("tok_n", None, "stored_token_n")],
}
TRUTH_SETS = {
    "truth4": [("truth", 2, "true_eavail"), ("truth", 0, "true_pt"),
               ("truth", 1, "true_pparallel"), ("truth", 3, "true_q3")],
    "eavail": [("truth", 2, "true_eavail")],
    "muon_truth": [("truth", 0, "true_pt"), ("truth", 1, "true_pparallel")],
}
TRUTH_KEYS = {"truth"}


def assert_reco_only(name: str) -> None:
    bad = [label for key, _c, label in RECO_SETS[name] if key in TRUTH_KEYS]
    if bad:
        raise SystemExit(f"[features] reco set {name!r} reads truth columns {bad}")


def build(pop: Mapping[str, np.ndarray], side: str, spec: list) -> np.ndarray:
    """Feature matrix for half ``side`` ('a' or 'b'), all rows of that half, float64."""
    cols = []
    for key, col, _label in spec:
        arr = np.asarray(pop[f"{side}_{key}"], dtype=np.float64)
        cols.append(arr[:, col] if col is not None else arr)
    return np.stack(cols, axis=1)


def reco_matrix(pop: Mapping[str, np.ndarray], side: str, name: str) -> np.ndarray:
    assert_reco_only(name)
    return build(pop, side, RECO_SETS[name])


def truth_matrix(pop: Mapping[str, np.ndarray], side: str, name: str) -> np.ndarray:
    return build(pop, side, TRUTH_SETS[name])


def labels(spec_name: str, reco: bool) -> list[str]:
    table = RECO_SETS if reco else TRUTH_SETS
    return [label for _k, _c, label in table[spec_name]]
