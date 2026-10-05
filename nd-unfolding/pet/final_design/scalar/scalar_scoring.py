"""Scores of a truth-level push on one (selection, case) problem, against the replicate's OWN
pseudodata truth.

* **Primary: the historical seven-bin E_avail recovery**, built exactly as the predecessor's
  `confirm/score_replicate.RunScorer` builds it -- a historical `score_campaign.Endpoint` whose
  target is the pseudodata's truth-passing rows at `w_truth x distortion` and whose prior is the
  prior's truth-passing rows at `w_truth`, scored by `scalar_common.score_push` (blob-checked
  historical code). "Moves away" = `residual_l1 > injected_l1` (R < 0), the predecessor's
  definition.
* **Joint topology:** truth E_avail (endpoint bins) x proton class (0/1/2/3+) and x neutron class
  (0/1/2/3+) of the truncated truth cloud, plus the two class marginals, with the recovery form of
  `final_design/diagnostics/posthoc_iterations.py` (`1 - L1(norm(h_w) - norm(h_t)) /
  L1(norm(h_prior) - norm(h_t))`, `null` below an injected L1 of 1e-3) -- but with the target the
  pseudodata truth instead of the oracle-weighted prior.
* **Oracle anchor:** the same scores for the exact distortion evaluated on the prior
  (`prior_oracle`), i.e. what a perfect estimator reaches on this finite pair of samples.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))

import selection_data as sd  # noqa: E402
import common as cm  # noqa: E402  (phase_e, on the path via selection_data)
import scalar_common as scm  # noqa: E402

CODE_TO_REGION = {v: k for k, v in cm.REGION_CODES.items()}
SCOREABLE = cm.SCOREABLE
INFORMATIONAL = cm.INFORMATIONAL
EAVAIL_EDGES = cm.ENDPOINT_EDGES
SPECIES_TOP = {"p": 3, "n": 3}
SMALL_INJECTION_L1 = 1e-3


def _eavail_bin(e: np.ndarray) -> np.ndarray:
    """posthoc_iterations.eavail_bin."""
    return np.clip(np.digitize(e, EAVAIL_EDGES) - 1, 0, len(EAVAIL_EDGES) - 2)


def _norm(h: np.ndarray) -> np.ndarray:
    s = h.sum()
    return h / s if s > 0 else h


def posthoc_recovery(h_w: np.ndarray, h_prior: np.ndarray, h_target: np.ndarray
                     ) -> dict[str, Any]:
    """posthoc_iterations.recovery, with the target in place of the oracle."""
    a, p, t = _norm(h_w), _norm(h_prior), _norm(h_target)
    inj = float(np.abs(p - t).sum())
    res = float(np.abs(a - t).sum())
    return {"injected_l1": inj, "residual_l1": res,
            "recovery": (1.0 - res / inj) if inj > SMALL_INJECTION_L1 else None,
            "moves_away": bool(res > inj),
            "signed_residual": np.round(a - t, 6).tolist()}


class Scorer:
    def __init__(self, prob: sd.Problem) -> None:
        cm.historical()                                       # blob check before any number
        self.prob = prob
        sc = cm.historical()["sc"]
        P, D = prob.prior, prob.pseudo
        eav_a, eav_b = D["truth_scalars"][:, 2], P["truth_scalars"][:, 2]
        self.keep_a = D["pass_truth"] & np.isfinite(eav_a)
        self.keep_b = P["pass_truth"] & np.isfinite(eav_b)
        ka, kb = self.keep_a, self.keep_b
        self.endpoint = sc.Endpoint(
            eavail_a=eav_a[ka], w_truth_a=D["w_truth"][ka], tilt_a=prob.distortion[ka],
            region_a=np.array([CODE_TO_REGION[c] for c in D["region"][ka]], "<U32"),
            eavail_b=eav_b[kb], w_truth_b=P["w_truth"][kb],
            region_b=np.array([CODE_TO_REGION[c] for c in P["region"][kb]], "<U32"),
            prior_selector=kb)
        # topology codes
        eb_b, eb_a = _eavail_bin(eav_b), _eavail_bin(eav_a)
        nb = len(EAVAIL_EDGES) - 1
        self.codes: dict[str, tuple[np.ndarray, np.ndarray, int]] = {}
        for k, top in SPECIES_TOP.items():
            cb = np.minimum(P[f"tr_n_{k}"], top)
            ca = np.minimum(D[f"tr_n_{k}"], top)
            self.codes[f"class_{k}"] = (cb, ca, top + 1)
            self.codes[f"joint_eavail_{k}"] = (eb_b * (top + 1) + cb, eb_a * (top + 1) + ca,
                                               nb * (top + 1))
        wt = (D["w_truth"] * prob.distortion) * ka
        self.targets = {name: np.bincount(ca, weights=wt, minlength=n)[:n]
                        for name, (_cb, ca, n) in self.codes.items()}
        w0 = P["w_truth"] * kb
        self.priors = {name: np.bincount(cb, weights=w0, minlength=n)[:n]
                       for name, (cb, _ca, n) in self.codes.items()}
        self.oracle = self.score(prob.oracle, full=True)

    def eavail(self, push: np.ndarray, full: bool = False) -> dict[str, Any]:
        res = scm.score_push(self.endpoint, np.asarray(push, np.float64), SCOREABLE,
                             INFORMATIONAL)
        agg = res["aggregate"]
        out = {"recovery": res["recovery"], "recovery_by_region": res["recovery_by_region"],
               "injected_l1": agg["injected_l1"], "residual_l1": agg["residual_l1"],
               "moves_away": bool(agg["residual_l1"] > agg["injected_l1"]),
               "signed_residual_per_bin": agg["signed_residual_per_bin"],
               "moves_away_by_region": {k: bool(v["residual_l1"] > v["injected_l1"])
                                        for k, v in res["regions"].items()}}
        if full:
            out["injected_per_bin"] = agg["injected_per_bin"]
            out["overshoot_projection"] = agg["overshoot_projection"]
        return out

    def topology(self, push: np.ndarray) -> dict[str, Any]:
        w = self.prob.prior["w_truth"] * np.asarray(push, np.float64) * self.keep_b
        out = {}
        for name, (cb, _ca, n) in self.codes.items():
            h = np.bincount(cb, weights=w, minlength=n)[:n]
            r = posthoc_recovery(h, self.priors[name], self.targets[name])
            if not name.startswith("joint"):
                r.pop("signed_residual")
            out[name] = r
        return out

    def score(self, push: np.ndarray, full: bool = False) -> dict[str, Any]:
        push = np.asarray(push, np.float64)
        if push.shape != self.prob.prior["rows"].shape:
            raise ValueError("push must be aligned to all prior rows")
        return {"eavail": self.eavail(push, full=full), "topology": self.topology(push)}

    def constants(self) -> dict[str, Any]:
        return {"n_prior_scored": int(self.keep_b.sum()), "n_target": int(self.keep_a.sum()),
                "oracle": self.oracle,
                "target_eavail_hist": np.asarray(
                    cm.historical()["sc"]._histogram(self.endpoint.eavail_a,
                                                     self.endpoint.w_truth_a
                                                     * self.endpoint.tilt_a,
                                                     EAVAIL_EDGES)).tolist()}
