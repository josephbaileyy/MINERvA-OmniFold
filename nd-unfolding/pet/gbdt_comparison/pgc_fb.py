"""One PET final-bank run's (prior, pseudodata) pair as a scalar unfolding problem.

A final-bank run directory (`s4f/S4F-<design>-FB<r>[-<case>]`, `s4s/S4S-...`) holds
`replicate_arrays.npz`: the prior (DEV-bank) and pseudodata (FB-bank) inventory rows, their pass
flags, truth `[pt, ppar, eavail, q3]`, engine-normalized `w_truth`/`w_reco`, reco E_avail (already
scaled for R cases), the pseudodata's truth distortion and the prior's oracle weights. Every design
of a (stage, draw, case) shares these bytes, so a GBDT trained on them sees exactly the PET runs'
events, weights and distortion.

The scalar recipe's other inputs are gathered at the same rows:

* reco p_T, p_par, q3 from the inventory's `reco_scalars` (signal-MC member; its column 2 must
  equal the run's unscaled reco E_avail on every row, or the gather is refused);
* stored-cluster count and energy sum and the truncated-cloud species counts from the study's
  `row_features.npz` (its pass flags must equal the run's).

The result is a `selection_data.Problem` (the matched study's container), so the estimator runs
unchanged. As there, the R factor scales the pseudodata's stored-cluster energy sum on reco-passing
rows; reco E_avail comes scaled from the run itself. For an R2 (muon momentum) case the PET path
scales the pseudodata's reco p_T and p_par and recomputes reco q3 on reco-passing rows
(`final_design/runner/design_inputs.apply_muon_scale` -> `r2_scalars`, cast to the inventory's
float32); the same function is applied here to the gathered `reco_scalars`, and the run's reco
E_avail must equal the unscaled inventory value. Simulation only.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ROW_FEATURE_COLUMNS = ("rc_n_valid", "rc_E_sum", "tr_n_p", "tr_n_n", "tr_n_pipm", "tr_n_pi0",
                       "tr_n_other", "pass_reco", "pass_truth")
R_FACTOR_RE = re.compile(r"^(R\d)_x([0-9.]+)(?:[+_]|$)")


def r_case(case: str) -> tuple[str, float] | None:
    """(family, factor) of a reco-response case ('R1_x1.05+D1_p0.350' -> ('R1', 1.05)), else
    None. Only R1 (hadronic energy scale) and R2 (muon momentum scale) exist on the PET path."""
    m = R_FACTOR_RE.match(case)
    if not m:
        return None
    if m.group(1) not in ("R1", "R2"):
        raise ValueError(f"{case}: reco response {m.group(1)} is not implemented on the PET path")
    return m.group(1), float(m.group(2))


def r_factor(case: str) -> float | None:
    """The R1 energy-scale factor of a case, else None."""
    rc = r_case(case)
    return rc[1] if rc is not None and rc[0] == "R1" else None


def load_arrays(run: Path | str) -> dict[str, np.ndarray]:
    with np.load(Path(run) / "replicate_arrays.npz", allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


class InventoryColumns:
    """`reco_scalars` (n_inventory x 4, float32) and the row-feature columns, indexed by row."""

    def __init__(self, reco_scalars: Path | str, row_features: Path | str) -> None:
        self.reco_scalars_path = Path(reco_scalars)
        self.row_features_path = Path(row_features)
        self.reco = np.load(self.reco_scalars_path, mmap_mode="r")
        with np.load(self.row_features_path, allow_pickle=False) as z:
            self.rf = {c: np.asarray(z[c]) for c in ROW_FEATURE_COLUMNS}
        n = self.reco.shape[0]
        if any(v.shape[0] != n for v in self.rf.values()):
            raise ValueError("reco_scalars and row_features disagree on the inventory length")

    def side(self, A: Mapping[str, np.ndarray], prefix: str) -> dict[str, np.ndarray]:
        rows = np.asarray(A[f"{prefix}_rows"], np.int64)
        reco = np.asarray(self.reco[rows], np.float64)
        inv_eav = reco[:, 2]
        if not np.array_equal(inv_eav, np.asarray(A[f"{prefix}_reco_eavail_unscaled"]),
                              equal_nan=True):
            raise ValueError(f"{prefix}: inventory reco E_avail differs from the run's")
        for flag in ("pass_reco", "pass_truth"):
            if not np.array_equal(self.rf[flag][rows].astype(bool),
                                  np.asarray(A[f"{prefix}_{flag}"], bool)):
                raise ValueError(f"{prefix}: row_features {flag} differs from the run's")
        out = {
            "rows": rows,
            "reco_scalars": reco,
            "truth_scalars": np.asarray(A[f"{prefix}_truth"], np.float64),
            "w_truth": np.asarray(A[f"{prefix}_w_truth"], np.float64),
            "w_reco": np.asarray(A[f"{prefix}_w_reco"], np.float64),
            "pass_reco": np.asarray(A[f"{prefix}_pass_reco"], bool),
            "pass_truth": np.asarray(A[f"{prefix}_pass_truth"], bool),
            "region": np.asarray(A[f"{prefix}_region"], np.int8),
            "rc_n_valid": self.rf["rc_n_valid"][rows].astype(np.float64),
            "rc_E_sum": self.rf["rc_E_sum"][rows].astype(np.float64),
            "reco_eavail": np.asarray(A[f"{prefix}_reco_eavail"], np.float64),
        }
        for k in ("p", "n", "pipm", "pi0", "other"):
            out[f"tr_n_{k}"] = self.rf[f"tr_n_{k}"][rows].astype(np.int64)
        return out


def build_problem(run: Path | str, cols: InventoryColumns, sd: Any,
                  r2_scalars: Any = None) -> Any:
    """The run's pair as `sd.Problem` (``sd`` is the imported `selection_data` module;
    ``r2_scalars`` the PET path's `design_inputs.r2_scalars`, required for an R2 case)."""
    run = Path(run)
    ident = json.loads((run / "run_identity.json").read_text())
    case = ident["distortion"]
    A = load_arrays(run)
    rc = r_case(case)
    factor = r_factor(case)
    A["prior_reco_eavail_unscaled"] = A["prior_reco_eavail"]
    if factor is None:
        A["pseudo_reco_eavail_unscaled"] = A["pseudo_reco_eavail"]
    else:
        # undo exactly what the PET path did: float32 multiply on reco-passing rows
        inv = np.asarray(cols.reco[np.asarray(A["pseudo_rows"], np.int64), 2], np.float64)
        expect = inv.astype(np.float32)
        hit = A["pseudo_pass_reco"].astype(bool)
        expect[hit] = expect[hit] * np.float32(factor)
        if not np.array_equal(expect.astype(np.float64), A["pseudo_reco_eavail"],
                              equal_nan=True):
            raise ValueError(f"{run.name}: pseudodata reco E_avail is not the inventory value "
                             f"x float32({factor}) on reco-passing rows")
        A["pseudo_reco_eavail_unscaled"] = inv
    prior, pseudo = cols.side(A, "prior"), cols.side(A, "pseudo")
    if rc is not None and rc[0] == "R2":
        if r2_scalars is None:
            raise ValueError(f"{run.name}: an R2 case needs the PET path's r2_scalars")
        hit = pseudo["pass_reco"]
        r = pseudo["reco_scalars"].astype(np.float32)
        pt2, ppar2, q32 = r2_scalars(r[hit, 0].astype(np.float64), r[hit, 1].astype(np.float64),
                                     r[hit, 3].astype(np.float64), rc[1])
        for col, v in ((0, pt2), (1, ppar2), (3, q32)):
            r[hit, col] = np.asarray(v).astype(np.float32)
        pseudo["reco_scalars"] = r.astype(np.float64)
    if factor is not None:
        hit = pseudo["pass_reco"]
        e = pseudo["rc_E_sum"].astype(np.float32)
        e[hit] = e[hit] * np.float32(factor)
        pseudo["rc_E_sum"] = e.astype(np.float64)
    distortion = np.asarray(A["pseudo_distortion"], np.float64)
    oracle = np.asarray(A["prior_oracle"], np.float64)
    pt = pseudo["pass_truth"]
    if not np.allclose(distortion[pt].mean(), 1.0, rtol=0, atol=1e-9) or \
            not np.all(distortion[~pt] == 1.0):
        raise ValueError(f"{run.name}: distortion is not unit-mean on truth-passing rows")
    if np.intersect1d(prior["rows"], pseudo["rows"]).size:
        raise ValueError(f"{run.name}: prior and pseudodata share rows")
    record = {"run": run.name, "case": case, "r_factor": factor,
              "reco_response": None if rc is None else {"family": rc[0], "factor": rc[1]},
              "n_prior": int(prior["rows"].size), "n_pseudo": int(pseudo["rows"].size)}
    prob = sd.Problem(run.name, case, prior, pseudo, distortion, oracle, factor, record)
    record.update({"prior_pass_truth": int(prob.pg_prior.sum()),
                   "prior_step1": int(prob.s1_prior.sum()),
                   "pseudo_step1": int(prob.s1_pseudo.sum())})
    return prob
