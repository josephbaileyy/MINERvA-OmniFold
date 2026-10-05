"""The scalar input sets, by name, built from the cached populations. One definition, used by every
runner, so a table's input label always means the same columns.

Reco side (step 1) reads ONLY reconstructed quantities; `assert_reco_only` refuses a truth column.
Truth side (step 2) reads the four truth scalars.

Non-finite entries on the rows a step actually uses are filled with the column median over the
finite used rows and COUNTED (`fill_nonfinite`); measured on the historical halves this touches
only true q3 (15 of 600,130 truth-passing rows in half A, 21 of 600,111 in half B;
`populations.json` census). Rows a step does not use are never inspected (the reco side carries
the -9999 sentinel there, which is finite and must not drive a fill).
"""
from __future__ import annotations

from typing import Mapping

import numpy as np

# name -> list of (population key, column or None, label)
RECO_SETS = {
    "muon": [("reco", 0, "reco_pt"), ("reco", 1, "reco_pparallel")],
    # the single controlled addition: the analysis's reconstructed available energy
    "muon_eavail": [("reco", 0, "reco_pt"), ("reco", 1, "reco_pparallel"),
                    ("reco", 2, "reco_eavail")],
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


def fill_nonfinite(X: np.ndarray, used: np.ndarray, names: list[str]
                   ) -> tuple[np.ndarray, dict[str, dict[str, float]]]:
    """Median-fill non-finite entries on the USED rows; returns the matrix and a per-column record."""
    X = np.array(X, dtype=np.float64)
    used = np.asarray(used, dtype=bool)
    record = {}
    for i, name in enumerate(names):
        col = X[:, i]
        bad = used & ~np.isfinite(col)
        if bad.any():
            fill = float(np.median(col[used & np.isfinite(col)]))
            col[bad] = fill
            record[name] = {"filled_rows": int(bad.sum()), "used_rows": int(used.sum()),
                            "fill_value": fill, "rule": "median over finite used rows"}
    return X, record


def reco_matrix(pop: Mapping[str, np.ndarray], side: str, name: str,
                used: np.ndarray | None = None) -> np.ndarray | tuple[np.ndarray, dict]:
    assert_reco_only(name)
    X = build(pop, side, RECO_SETS[name])
    return X if used is None else fill_nonfinite(X, used, labels(name, reco=True))


def truth_matrix(pop: Mapping[str, np.ndarray], side: str, name: str,
                 used: np.ndarray | None = None) -> np.ndarray | tuple[np.ndarray, dict]:
    X = build(pop, side, TRUTH_SETS[name])
    return X if used is None else fill_nonfinite(X, used, labels(name, reco=False))


def labels(spec_name: str, reco: bool) -> list[str]:
    table = RECO_SETS if reco else TRUTH_SETS
    return [label for _k, _c, label in table[spec_name]]
