"""Generalized loaders: one (selection, case) of the predecessor's PET STRESS/FINAL library as a
scalar unfolding problem.

A *selection* is one replicate draw of family `confirm-historical-size-v1` -- pool T replicate 0
or 1 (`T0`, `T1`; the PET STRESS runs) or pool F replicate 0 or 1 (`F0`, `F1`; the PET FINAL
runs) -- extracted on the cluster by `extract_selections.py` into `selection_<S>.npz`. A *case* is
the truth distortion (and, for R1, the pseudodata reco scaling) applied to it:

* `F0`/`F1`: `dev` (the historical development tilt);
* `T0`/`T1`: `D1_m0.350`, `D2_bump_c0.3`, `D4c_p_up`, `D4d_n_up`, `D5_nuwro`,
  `R1_x1.05_D1_p0.350`, and the derived control `D1_p0.350` -- the R1 case's own truth weights with
  the reco scaling NOT applied (PROTOCOL-20260925 section 7 asks for this matched unscaled control;
  the predecessor has no PET run of it, so it is labelled derived).

R1, as on the PET path (`confirm/replicate_inputs._r1_distortion`): the PSEUDODATA's reco E_avail
and stored-cluster energies are multiplied by the float32 factor on reco-passing rows; muon
quantities, reco q3, the cluster count, the prior and the selection are unchanged. Here the
stored-cluster energy SUM (`rc_E_sum`) is scaled, which equals the sum of the scaled energies up to
float32 rounding.

Inputs (detector-only at step 1, the information the PET compact hybrid H2 receives as summaries):
reco p_T, p_par, reco E_avail, reco q3, stored-cluster energy sum and count. Truth inputs: true
E_avail, p_T, p_par, q3 (`truth4`, the predecessor's order) and optionally the truncated-cloud
species counts (`truth4_species`: + protons, neutrons, charged pions, neutral pions, other -- counts
over the stored 12-token truth cloud, not full final-state multiplicities).

Selections as the engine sees them: the step-1 prior rows are `pass_reco & pass_truth`, the
pseudodata rows `pass_reco & pass_truth` at weight `w_reco x distortion`; step 2 acts on the
prior's `pass_truth` rows. Simulation only.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent.parent / "improvement_campaign"
for _p in (CAMPAIGN / "phase_e", CAMPAIGN / "phase_b" / "scalar", CAMPAIGN / "phase_f"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))

import features as b1_features  # noqa: E402  (phase_b/scalar: median fill of non-finite inputs)

SELECTIONS = ("T0", "T1", "F0", "F1")
STRESS_CASES = ("D1_m0.350", "D2_bump_c0.3", "D4c_p_up", "D4d_n_up", "D5_nuwro",
                "R1_x1.05_D1_p0.350")
DERIVED_CONTROL = {"D1_p0.350": "R1_x1.05_D1_p0.350"}   # control -> the case whose weights it uses
R1_FACTOR = {"R1_x1.05_D1_p0.350": 1.05}
DEV_CASE = "dev"

RECO_LABELS = ("reco_pt", "reco_pparallel", "reco_eavail", "reco_q3", "stored_cluster_Esum",
               "stored_cluster_n")
TRUTH_SETS = {
    "truth4": ("true_eavail", "true_pt", "true_pparallel", "true_q3"),
    "truth4_species": ("true_eavail", "true_pt", "true_pparallel", "true_q3",
                       "trunc_cloud_n_p", "trunc_cloud_n_n", "trunc_cloud_n_pipm",
                       "trunc_cloud_n_pi0", "trunc_cloud_n_other"),
}
SPECIES = ("p", "n", "pipm", "pi0", "other")
GRID = json.loads((HERE / "reporting_grid.json").read_text())


def cases_for(selection: str) -> tuple[str, ...]:
    if selection not in SELECTIONS:
        raise ValueError(f"unknown selection {selection!r}")
    return (DEV_CASE,) if selection.startswith("F") else STRESS_CASES + tuple(DERIVED_CONTROL)


def library() -> list[tuple[str, str]]:
    """Every (selection, case) unit of the comparison, in a fixed order."""
    return [(s, c) for s in SELECTIONS for c in cases_for(s)]


def load_selection(path: Path | str) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


@dataclass
class Problem:
    """One (selection, case): per-row arrays for the prior (all prior rows) and the pseudodata."""
    selection: str
    case: str
    prior: dict[str, np.ndarray]
    pseudo: dict[str, np.ndarray]
    distortion: np.ndarray           # per pseudodata row (1 off pass_truth), unit mean on pass_truth
    oracle: np.ndarray               # per prior row: the exact distortion on the prior's truth
    r1_factor: float | None
    record: dict[str, Any] = field(default_factory=dict)

    # --- selections --------------------------------------------------------------------- #
    @property
    def pg_prior(self) -> np.ndarray:
        return self.prior["pass_truth"]

    @property
    def s1_prior(self) -> np.ndarray:
        return self.prior["pass_reco"] & self.prior["pass_truth"]

    @property
    def s1_pseudo(self) -> np.ndarray:
        return self.pseudo["pass_reco"] & self.pseudo["pass_truth"]

    @property
    def w_data(self) -> np.ndarray:
        """Pseudodata weight on its step-1 rows: w_reco x distortion (engine closure)."""
        return (self.pseudo["w_reco"] * self.distortion)[self.s1_pseudo]

    # --- feature matrices ---------------------------------------------------------------- #
    def reco_matrix(self, side: str) -> tuple[np.ndarray, dict[str, Any]]:
        """The six reco inputs on ALL rows of ``side``; non-finite entries on the step-1 rows
        median-filled and counted (phase_b `features.fill_nonfinite`)."""
        d = self.prior if side == "prior" else self.pseudo
        r = d["reco_scalars"]
        X = np.stack([r[:, 0], r[:, 1], d["reco_eavail"], r[:, 3], d["rc_E_sum"],
                      d["rc_n_valid"]], axis=1).astype(np.float64)
        used = self.s1_prior if side == "prior" else self.s1_pseudo
        return b1_features.fill_nonfinite(X, used, list(RECO_LABELS))

    def truth_matrix(self, truth_set: str) -> tuple[np.ndarray, dict[str, Any]]:
        """Truth inputs on ALL prior rows (median-filled on the pass_truth rows)."""
        if truth_set not in TRUTH_SETS:
            raise ValueError(f"unknown truth set {truth_set!r}")
        t = self.prior["truth_scalars"]
        cols = [t[:, 2], t[:, 0], t[:, 1], t[:, 3]]
        if truth_set == "truth4_species":
            cols += [self.prior[f"tr_n_{k}"] for k in SPECIES]
        X = np.stack(cols, axis=1).astype(np.float64)
        return b1_features.fill_nonfinite(X, self.pg_prior, list(TRUTH_SETS[truth_set]))


def _side(sel: Mapping[str, np.ndarray], side: str) -> dict[str, np.ndarray]:
    out = {
        "rows": sel[f"{side}_rows"].astype(np.int64),
        "reco_scalars": sel[f"{side}_reco_scalars"].astype(np.float64),
        "truth_scalars": sel[f"{side}_truth_scalars"].astype(np.float64),
        "w_truth": sel[f"{side}_w_truth"].astype(np.float64),
        "w_reco": sel[f"{side}_w_reco"].astype(np.float64),
        "pass_reco": sel[f"{side}_pass_reco"].astype(bool),
        "pass_truth": sel[f"{side}_pass_truth"].astype(bool),
        "region": sel[f"{side}_region"].astype(np.int8),
        "rc_n_valid": sel[f"{side}_rc_n_valid"].astype(np.float64),
        "rc_E_sum": sel[f"{side}_rc_E_sum"].astype(np.float32),
    }
    for k in SPECIES:
        out[f"tr_n_{k}"] = sel[f"{side}_tr_n_{k}"].astype(np.int64)
    out["reco_eavail"] = sel[f"{side}_reco_scalars"][:, 2].astype(np.float32)
    return out


def build_problem(sel: Mapping[str, np.ndarray], selection: str, case: str) -> Problem:
    """The (selection, case) problem from an extracted selection npz (``load_selection``)."""
    if case not in cases_for(selection):
        raise ValueError(f"case {case!r} is not in selection {selection}'s library")
    source = DERIVED_CONTROL.get(case, case)
    key = f"case__{source}__pseudo_distortion"
    if key not in sel:
        raise KeyError(f"{key} not in the selection file")
    prior, pseudo = _side(sel, "prior"), _side(sel, "pseudo")
    factor = R1_FACTOR.get(case)                  # the derived control is NOT scaled
    if factor is not None:
        hit = pseudo["pass_reco"]
        f32 = np.float32(factor)
        pseudo["reco_eavail"] = pseudo["reco_eavail"].copy()
        pseudo["reco_eavail"][hit] = pseudo["reco_eavail"][hit] * f32
        pseudo["rc_E_sum"] = pseudo["rc_E_sum"].copy()
        pseudo["rc_E_sum"][hit] = pseudo["rc_E_sum"][hit] * f32
    for d in (prior, pseudo):
        d["reco_eavail"] = d["reco_eavail"].astype(np.float64)
        d["rc_E_sum"] = d["rc_E_sum"].astype(np.float64)
    distortion = np.asarray(sel[key], np.float64)
    oracle = np.asarray(sel[f"case__{source}__prior_oracle"], np.float64)
    if distortion.shape != pseudo["rows"].shape or oracle.shape != prior["rows"].shape:
        raise ValueError("distortion/oracle not aligned to the selection rows")
    pt = pseudo["pass_truth"]
    if not np.allclose(distortion[pt].mean(), 1.0, rtol=0, atol=1e-9) or \
            not np.all(distortion[~pt] == 1.0):
        raise ValueError("distortion is not unit-mean on the pseudodata's truth-passing rows")
    if np.intersect1d(prior["rows"], pseudo["rows"]).size:
        raise ValueError("prior and pseudodata share rows")
    record = {"selection": selection, "case": case, "weights_from_case": source,
              "derived_control": case in DERIVED_CONTROL, "r1_factor": factor,
              "n_prior": int(prior["rows"].size), "n_pseudo": int(pseudo["rows"].size)}
    prob = Problem(selection, case, prior, pseudo, distortion, oracle, factor, record)
    record.update({"prior_pass_truth": int(prob.pg_prior.sum()),
                   "prior_step1": int(prob.s1_prior.sum()),
                   "pseudo_step1": int(prob.s1_pseudo.sum())})
    return prob


def truth_cell(pt: np.ndarray, ppar: np.ndarray) -> np.ndarray:
    """Flat historical reporting cell (-1 off grid), by the historical function."""
    import common as cm            # phase_e (blob-checked historical import)
    cr = cm.historical()["cr"]
    return cr.cell_index_of_events(pt, ppar, np.asarray(GRID["edges_pt"]),
                                   np.asarray(GRID["edges_pz"]))
