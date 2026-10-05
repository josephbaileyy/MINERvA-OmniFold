"""Score a B2 (or A1-driver) PET run at every iteration, on the historical endpoint.

Every number comes from the historical scoring code through B1's `phase_b/scalar/scalar_common.py`
(bit-identical to `score_campaign.score_run`, blob-checked against `68cf9d29`) and B1's cached
populations (`populations.npz`, 31/31 checks against the report). Per iteration it records:

* `push`: the historical score of the step-2 output over half B -- aggregate, the three scored
  regions (+ `poor`, informational), signed per-bin residual vs the injected displacement, and
  the overshoot projection (`scalar_common.score_push`);
* `pull`: the same score for the pulled weights (step-1 weights carried to truth; misses carry the
  previous push), compact;
* weight tails and ESS: `push` on truth-passing rows (max, 99.9th pct, ESS/n) and the ESS
  `(sum w)^2 / sum w^2` of the final truth weights `w_truth x push`;
* `step1_detector`: experiment 3a -- how much of the REMAINING reco-level pseudo-data / prior
  difference (prior x previous push) this iteration's step-1 reweighting removed;
  `step1_detector_cumulative`: the same for the pulled weights against the ORIGINAL prior, on the same normalized-L1 scale, in reconstructed E_avail (the
  analysis definition, 7 endpoint bins), the muon (pT, p||) reporting cells, reco pT and p||
  alone, the stored-cluster energy sum (deciles of the prior) and the stored-cluster count;
* `pulled_vs_pushed`: experiment 3b -- truth E_avail recovery of the pull and of the push over
  the reco-passing events alone, and over the misses alone (targets: half A x tilt over the same
  class), i.e. where the correction is lost: at step 1, in the pull, or in extrapolation to misses.

Input: a run directory holding `iterations/iterNN.npz` (B2 driver) or the A1 driver's final
`weights_<arm>_<name>.npz` (then only the last iteration, push only).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
SCALAR = HERE.parent / "scalar"
if str(SCALAR) not in sys.path:
    sys.path.insert(0, str(SCALAR))

import binned_unfolding as bu  # noqa: E402
import run_ibu  # noqa: E402
import scalar_common as scm  # noqa: E402

SCHEMA = "phase-b2-run-scores/1"


def load_run(run: Path) -> tuple[list[tuple[int, np.ndarray, np.ndarray | None]], np.ndarray,
                                 dict[str, Any]]:
    """[(iteration, push, pull)], dump_rows_b, provenance."""
    it_dir = run / "iterations"
    files = sorted(it_dir.glob("iter*.npz")) if it_dir.is_dir() else []
    prov: dict[str, Any] = {"run": str(run)}
    receipt = run / "receipt.json"
    if receipt.exists():
        r = json.loads(receipt.read_text())
        prov.update({"receipt_sha256": scm.sha256_file(receipt), "config_hash": r.get("config_hash"),
                     "code_commit": r.get("code_commit"), "config_name": r["config"]["name"],
                     "feature_arm": r.get("b2_arm", r.get("feature_arm")),
                     "iterations_declared": r["config"]["iterations"],
                     "complete": r.get("complete", True)})
    if files:
        with np.load(run / "halves.npz") as h:
            rows_b = np.asarray(h["dump_rows_b"]).astype(np.int64)
        out = []
        for path in files:
            with np.load(path) as blob:
                out.append((int(path.stem[4:]), np.asarray(blob["push"], np.float64),
                            np.asarray(blob["pull"], np.float64)))
            prov.setdefault("iteration_files", {})[path.name] = scm.sha256_file(path)
        return out, rows_b, prov
    weights = sorted(run.glob("weights_*.npz"))
    if len(weights) != 1:
        raise SystemExit(f"[b2-score] {run}: no iterations/ and not exactly one weights file")
    with np.load(weights[0]) as blob:
        push = np.asarray(blob["weights"], np.float64)
        rows_b = np.asarray(blob["dump_rows_b"]).astype(np.int64)
    prov["weights_file"] = {weights[0].name: scm.sha256_file(weights[0])}
    k = int(prov.get("iterations_declared", 0)) - 1
    return [(k, push, None)], rows_b, prov


class Scorer:
    def __init__(self, populations: Path) -> None:
        self.sources = scm.verify_historical_sources()
        self.mods = scm.historical_modules()
        pop = scm.load_populations(populations)
        self.pop = pop
        self.populations = {"path": str(populations), "sha256": scm.sha256_file(populations)}
        self.endpoint = scm.endpoint_from_populations(pop)
        self.pga = pop["a_pass_truth"].astype(bool)
        self.pgb = pop["b_pass_truth"].astype(bool)
        self.s1a = self.pga & pop["a_pass_reco"].astype(bool)
        self.s1b = self.pgb & pop["b_pass_reco"].astype(bool)
        if not np.array_equal(pop["b_truth"][self.pgb, 2], pop["ep_eavail_b"]) or \
                not np.array_equal(pop["a_truth"][self.pga, 2], pop["ep_eavail_a"]):
            raise SystemExit("[b2-score] populations do not align with their Endpoint")
        self.w_data = (pop["a_w_reco"] * pop["a_tilt"])[self.s1a]
        self.bins = self._reco_bins()

    # ---- reco-level binnings (experiment 3a) -------------------------------------------- #
    def _reco_bins(self) -> dict[str, tuple[np.ndarray, np.ndarray, int]]:
        pop = self.pop
        ibu = run_ibu.build_bins(pop)
        out = {"reco_eavail_7": (ibu["b"]["reco_eavail7"], ibu["a"]["reco_eavail7"],
                                 run_ibu.N_EAV),
               "muon_cells": (ibu["b"]["muon"], ibu["a"]["muon"], ibu["n_reco"]["muon"])}
        for name, col, edges in (("reco_pt", 0, pop["edges_pt"]),
                                 ("reco_pparallel", 1, pop["edges_pz"])):
            out[name] = (np.digitize(pop["b_reco"][:, col], edges),
                         np.digitize(pop["a_reco"][:, col], edges), len(edges) + 1)
        deciles = np.quantile(pop["b_tok_sumE"][self.s1b], np.linspace(0.1, 0.9, 9))
        out["stored_sumE_deciles"] = (np.digitize(pop["b_tok_sumE"], deciles),
                                      np.digitize(pop["a_tok_sumE"], deciles), 10)
        out["stored_n"] = (pop["b_tok_n"].astype(np.int64), pop["a_tok_n"].astype(np.int64), 13)
        self.bin_definitions = {
            "reco_eavail_7": "endpoint E_avail edges on reco_scalars[:,2] (B1 run_ibu)",
            "muon_cells": "reco (pT, p||) reporting cells + off-grid (B1 run_ibu 'muon')",
            "reco_pt": "np.digitize on edges_pt (under/overflow bins included)",
            "reco_pparallel": "np.digitize on edges_pz (under/overflow bins included)",
            "stored_sumE_deciles": {"edges_GeV": deciles.tolist(),
                                    "from": "unweighted deciles over half-B step-1 rows"},
            "stored_n": "stored cluster count 0..12"}
        return out

    def step1_detector(self, before: np.ndarray, after: np.ndarray) -> dict[str, Any]:
        out = {}
        for name, (bb, ba, n) in self.bins.items():
            out[name] = bu.reco_level_recovery(bb, self.s1b, self.pop["b_w_reco"], before, after,
                                               ba[self.s1a], self.w_data, n)
        return out

    # ---- truth-level subsets (experiment 3b) --------------------------------------------- #
    def subset(self, weights_b: np.ndarray, mask_a: np.ndarray, mask_b: np.ndarray
               ) -> dict[str, Any]:
        sc, rae = self.mods["sc"], self.mods["rae"]
        ep, edges = self.endpoint, self.endpoint.edges
        w = np.asarray(weights_b, np.float64)[self.pgb]
        prior = sc._histogram(ep.eavail_b[mask_b], ep.w_truth_b[mask_b], edges)
        unfolded = sc._histogram(ep.eavail_b[mask_b], (ep.w_truth_b * w)[mask_b], edges)
        target = sc._histogram(ep.eavail_a[mask_a], (ep.w_truth_a * ep.tilt_a)[mask_a], edges)
        scored = rae.recovery(prior, unfolded, target)
        pn, un, tn = (np.asarray(a, float) / np.asarray(a, float).sum()
                      for a in (prior, unfolded, target))
        return {"recovery": scored["recovery"], "injected_l1": scored["injected_l1"],
                "residual_l1": scored["residual_l1"],
                "overshoot_projection": float(sc.overshoot_projection(prior, unfolded, target)),
                "signed_residual_per_bin": (un - tn).tolist(),
                "injected_per_bin": (tn - pn).tolist()}

    def pulled_vs_pushed(self, pull: np.ndarray, push: np.ndarray) -> dict[str, Any]:
        acc_a = self.pop["a_pass_reco"].astype(bool)[self.pga]
        acc_b = self.pop["b_pass_reco"].astype(bool)[self.pgb]
        region_a = np.asarray(self.endpoint.region_a)
        region_b = np.asarray(self.endpoint.region_b)
        out: dict[str, Any] = {}
        for cls, ma, mb in (("accepted", acc_a, acc_b), ("misses", ~acc_a, ~acc_b)):
            out[cls] = {"pull": self.subset(pull, ma, mb), "push": self.subset(push, ma, mb),
                        "regions": {}}
            for name in run_ibu.SCOREABLE:
                ra, rb = ma & (region_a == name), mb & (region_b == name)
                if ra.any() and rb.any():
                    out[cls]["regions"][name] = {
                        "pull": self.subset(pull, ra, rb)["recovery"],
                        "push": self.subset(push, ra, rb)["recovery"]}
        out["truth_mass_fraction_accepted_B"] = float(
            self.endpoint.w_truth_b[acc_b].sum() / self.endpoint.w_truth_b.sum())
        return out

    # ---- one run ------------------------------------------------------------------------- #
    def score_run(self, run: Path) -> dict[str, Any]:
        iterations, rows_b, prov = load_run(run)
        if not np.array_equal(rows_b, self.pop["b_rows"]):
            raise SystemExit(f"[b2-score] {run}: half-B rows differ from the populations'")
        records = []
        prev = np.ones(self.pgb.size)
        w_truth_b = self.pop["b_w_truth"]
        for k, push, pull in iterations:
            if not np.all(np.isfinite(push)) or (push < 0).any():
                raise SystemExit(f"[b2-score] iteration {k}: push not finite / non-negative")
            record: dict[str, Any] = {
                "iteration": k, "k": k + 1,
                "push": scm.score_push(self.endpoint, push, run_ibu.SCOREABLE,
                                       run_ibu.INFORMATIONAL),
                "push_weights_on_truth_passing": scm.weight_summary(push[self.pgb]),
                "final_truth_weights_ess": {
                    "ess": scm.ess(w_truth_b[self.pgb] * push[self.pgb]),
                    "n": int(self.pgb.sum()),
                    "ess_prior_only": scm.ess(w_truth_b[self.pgb])},
            }
            if pull is not None:
                record["pull"] = run_ibu.compact_score(
                    scm.score_push(self.endpoint, pull, run_ibu.SCOREABLE,
                                   run_ibu.INFORMATIONAL))
                ratio = pull[self.s1b] / np.where(prev[self.s1b] > 0, prev[self.s1b], 1.0)
                record["step1_ratio_on_step1_rows"] = scm.weight_summary(ratio)
                record["step1_detector"] = self.step1_detector(prev, pull)
                # cumulative: the pulled weights against the ORIGINAL prior (before any iteration)
                record["step1_detector_cumulative"] = self.step1_detector(
                    np.ones(self.pgb.size), pull)
                record["pulled_vs_pushed"] = self.pulled_vs_pushed(pull, push)
            records.append(record)
            prev = push
        return {"schema": SCHEMA, "provenance": prov, "populations": self.populations,
                "historical_sources": self.sources, "bin_definitions": self.bin_definitions,
                "commit": scm.repo_commit(), "iterations": records}


def brief(result: dict[str, Any]) -> str:
    lines = []
    for r in result["iterations"]:
        p = r["push"]
        reg = " ".join(f"{n}={v:.3f}" for n, v in p["recovery_by_region"].items())
        extra = ""
        if "pull" in r:
            extra = (f" pull={r['pull']['recovery']:.3f}"
                     f" reco7={r['step1_detector']['reco_eavail_7']['recovery']:.3f}")
        lines.append(f"k={r['k']:2d} R={p['recovery']:.4f} {reg}{extra}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, nargs="+", required=True)
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None,
                        help="default: <run>/scores.json for each run")
    args = parser.parse_args()
    t0 = time.perf_counter()
    scorer = Scorer(args.populations)
    for run in args.run:
        result = scorer.score_run(run)
        result["seconds"] = time.perf_counter() - t0
        out = args.output or (run / "scores.json")
        scm.write_json(out, result, compact=True)
        print(f"[b2-score] {run.name}\n{brief(result)}", flush=True)


if __name__ == "__main__":
    main()
