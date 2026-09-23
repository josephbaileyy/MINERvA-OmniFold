"""Score a confirmatory run (`run_replicate.py`) at every iteration, like-for-like with the
historical score.

**Primary (like-for-like).** The historical seven-bin E_avail recovery computed by the historical
code: a `score_campaign.Endpoint` whose target is the replicate's OWN pseudodata truth weighted by
the injected distortion, and whose prior/unfolded spectra are the replicate's prior (the
historical design, with the replicate in place of the halves), scored by
`scalar_common.score_push` (bit-identical to `score_campaign.score_run`, blob-checked against the
comparison's code commit). Regions: the historical (pT, p||)-cell regions under the historical
acceptance map. With the historical halves forced in, this IS the historical endpoint.

Beside it, per iteration: the same score against the POPULATION target (the distorted spectrum
over the whole pool, `population_target.py`), the signed per-bin residuals, the pull's score,
truth-weight tails (max, 99.9th percentile) and ESS `(sum w)^2 / sum w^2`, and the reco-level
closure of step 1 in reconstructed E_avail (seven endpoint bins; the pulled weights against the
original prior, and this iteration's step against the previous push).

Per run: the ORACLE anchor -- the exact distortion function applied to the prior (unit mean over
its truth-passing rows) and scored like a push against both targets -- i.e. the recovery a
perfect estimator reaches on this finite sample; and the distance between the replicate's target
and the population target.

    score_replicate.py --run <run dir> [--population-target <json>] [--reference-run <B2 run dir>]

`--reference-run` (the positive control on the historical halves): compares every common
iteration's pull/push arrays byte for byte with a B2 run and the scores with its `scores.json`.
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
CAMPAIGN = HERE.parent
for _p in (HERE, CAMPAIGN / "phase_e", CAMPAIGN / "phase_b" / "scalar"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import binned_unfolding as bu  # noqa: E402
import common as cm  # noqa: E402
import run_ibu  # noqa: E402
import scalar_common as scm  # noqa: E402

SCHEMA = "pet-improvement-confirm-run-scores/1"
CODE_TO_REGION = {v: k for k, v in cm.REGION_CODES.items()}
N_EAV = len(cm.ENDPOINT_EDGES) - 1


def load_iterations(run: Path) -> list[tuple[int, np.ndarray, np.ndarray, str]]:
    out = []
    for path in sorted((run / "iterations").glob("iter*.npz")):
        with np.load(path) as blob:
            out.append((int(path.stem[4:]), np.asarray(blob["push"], np.float64),
                        np.asarray(blob["pull"], np.float64), scm.sha256_file(path)))
    return out


def l1_normalized(a: Any, b: Any) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.abs(a / a.sum() - b / b.sum()).sum())


class RunScorer:
    def __init__(self, run: Path, population_target: Path | None = None) -> None:
        self.run = Path(run)
        self.sources = scm.verify_historical_sources()
        self.mods = scm.historical_modules()
        receipt_path = self.run / "receipt.json"
        self.receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        with np.load(self.run / "replicate_arrays.npz") as blob:
            a = {k: np.asarray(blob[k]) for k in blob.files}
        with np.load(self.run / "halves.npz") as h:
            if not (np.array_equal(h["dump_rows_b"], a["prior_rows"])
                    and np.array_equal(h["dump_rows_a"], a["pseudo_rows"])):
                raise SystemExit("[confirm-score] halves.npz and replicate_arrays.npz disagree")
        self.a = a
        eav_a, eav_b = a["pseudo_truth"][:, 2], a["prior_truth"][:, 2]
        self.keep_a = a["pseudo_pass_truth"].astype(bool) & np.isfinite(eav_a)
        self.keep_b = a["prior_pass_truth"].astype(bool) & np.isfinite(eav_b)
        ka, kb = self.keep_a, self.keep_b
        self.region_b_code = a["prior_region"][kb]
        sc = self.mods["sc"]
        self.endpoint = sc.Endpoint(
            eavail_a=eav_a[ka], w_truth_a=a["pseudo_w_truth"][ka],
            tilt_a=a["pseudo_distortion"][ka],
            region_a=np.array([CODE_TO_REGION[c] for c in a["pseudo_region"][ka]], "<U32"),
            eavail_b=eav_b[kb], w_truth_b=a["prior_w_truth"][kb],
            region_b=np.array([CODE_TO_REGION[c] for c in self.region_b_code], "<U32"),
            prior_selector=kb)
        self.population = None
        if population_target is not None:
            self.population = self._load_population(Path(population_target))
        # reco-level closure of step 1 (reconstructed E_avail, endpoint bins)
        self.s1a = a["pseudo_pass_reco"].astype(bool) & a["pseudo_pass_truth"].astype(bool)
        self.s1b = a["prior_pass_reco"].astype(bool) & a["prior_pass_truth"].astype(bool)
        self.reco_bin_b = run_ibu.eavail_bin(a["prior_reco_eavail"], cm.ENDPOINT_EDGES)
        self.reco_bin_a = run_ibu.eavail_bin(a["pseudo_reco_eavail"], cm.ENDPOINT_EDGES)
        self.w_data = (a["pseudo_w_reco"] * a["pseudo_distortion"])[self.s1a]

    def _load_population(self, path: Path) -> dict[str, Any]:
        doc = json.loads(path.read_text())
        sel = self.receipt.get("selection", {})
        pool = sel.get("replicate", {}).get("design", {}).get("pool")
        want = self.receipt.get("run_identity", {}).get("distortion_hash")
        if doc["pool"] != pool or (want is not None and doc["distortion_hash"] != want):
            raise SystemExit(f"[confirm-score] population target {path} is for "
                             f"{doc['pool']}/{doc['distortion']}, not this run's {pool}")
        t = doc["targets"]
        targets = {"aggregate": np.asarray(t["aggregate"], float)}
        targets.update({k: np.asarray(v, float) for k, v in t["regions"].items()})
        return {"path": str(path), "sha256": scm.sha256_file(path), "targets": targets,
                "pool": doc["pool"], "distortion": doc["distortion"]}

    # ---- pieces ------------------------------------------------------------------------ #
    def replicate_score(self, push: np.ndarray) -> dict[str, Any]:
        return scm.score_push(self.endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)

    def population_score(self, push: np.ndarray) -> dict[str, Any] | None:
        if self.population is None:
            return None
        kb = self.keep_b
        return cm.score(self.endpoint.eavail_b, self.endpoint.w_truth_b,
                        np.asarray(push, np.float64)[kb], self.region_b_code,
                        self.population["targets"], compact=True)

    def reco_closure(self, before: np.ndarray, after: np.ndarray) -> dict[str, Any]:
        return bu.reco_level_recovery(self.reco_bin_b, self.s1b, self.a["prior_w_reco"],
                                      before, after, self.reco_bin_a[self.s1a], self.w_data,
                                      N_EAV)

    def constants(self) -> dict[str, Any]:
        oracle = self.a["prior_oracle"]
        ep = self.endpoint
        sc = self.mods["sc"]
        rep_target = sc._histogram(ep.eavail_a, ep.w_truth_a * ep.tilt_a, ep.edges)
        prior = sc._histogram(ep.eavail_b, ep.w_truth_b, ep.edges)
        out: dict[str, Any] = {
            "oracle_vs_replicate_target": run_ibu.compact_score(self.replicate_score(oracle)),
            "replicate_target_hist": rep_target.tolist(), "prior_hist": prior.tolist(),
            "injected_l1_replicate": l1_normalized(rep_target, prior),
            "n_prior_scored": int(self.keep_b.sum()), "n_pseudo_scored": int(self.keep_a.sum()),
            "prior_rows_not_scored": int((~self.keep_b).sum()),
        }
        if self.population is not None:
            pop = self.population["targets"]["aggregate"]
            out.update({"oracle_vs_population_target": self.population_score(oracle),
                        "population_target_hist": pop.tolist(),
                        "injected_l1_population": l1_normalized(pop, prior),
                        "replicate_target_minus_population_l1": l1_normalized(rep_target, pop)})
        return out

    def score(self) -> dict[str, Any]:
        its = load_iterations(self.run)
        wb = self.a["prior_w_truth"]
        kb = self.keep_b
        records = []
        prev = np.ones(kb.size)
        for k, push, pull, sha in its:
            if not np.all(np.isfinite(push)) or (push < 0).any():
                raise SystemExit(f"[confirm-score] iteration {k}: push not finite/non-negative")
            records.append({
                "iteration": k, "k": k + 1, "file_sha256": sha,
                "push": self.replicate_score(push),
                "push_vs_population": self.population_score(push),
                "pull": run_ibu.compact_score(self.replicate_score(pull)),
                "pull_vs_population": self.population_score(pull),
                "push_weights_on_truth_passing": scm.weight_summary(push[kb]),
                "final_truth_weights_ess": {"ess": scm.ess(wb[kb] * push[kb]),
                                            "n": int(kb.sum()),
                                            "ess_prior_only": scm.ess(wb[kb])},
                "step1_reco_eavail_7": self.reco_closure(prev, pull),
                "step1_reco_eavail_7_cumulative": self.reco_closure(np.ones(kb.size), pull),
            })
            prev = push
        prov = {k: self.receipt.get(k) for k in ("config_hash", "code_commit", "step2_miss_mode",
                                                  "b2_arm", "complete")}
        prov.update({"run": str(self.run), "run_identity": self.receipt.get("run_identity"),
                     "selection_record_rows": {
                         k: self.receipt.get("selection", {}).get(k)
                         for k in ("prior_rows_sha256", "pseudo_rows_sha256")},
                     "receipt_sha256": (scm.sha256_file(self.run / "receipt.json")
                                        if (self.run / "receipt.json").exists() else None),
                     "replicate_arrays_sha256": scm.sha256_file(self.run /
                                                                "replicate_arrays.npz")})
        return {"schema": SCHEMA, "provenance": prov, "historical_sources": self.sources,
                "population_target": (None if self.population is None else
                                      {k: self.population[k] for k in
                                       ("path", "sha256", "pool", "distortion")}),
                "commit": scm.repo_commit(), "constants": self.constants(),
                "iterations": records}


def compare_to_reference(run: Path, reference: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Byte comparison of every common iteration with a B2 run, and of the scores."""
    ours = {k: (push, pull) for k, push, pull, _ in load_iterations(run)}
    theirs = {k: (push, pull) for k, push, pull, _ in load_iterations(reference)}
    ref_scores = {}
    if (reference / "scores.json").exists():
        ref_scores = {r["iteration"]: r for r in
                      json.loads((reference / "scores.json").read_text())["iterations"]}
    with np.load(run / "halves.npz") as a, np.load(reference / "halves.npz") as b:
        halves_equal = {k: bool(np.array_equal(a[k], b[k])) for k in a.files if k in b.files}
    out: dict[str, Any] = {"reference": str(reference), "halves_equal": halves_equal,
                           "iterations": {}}
    mine = {r["iteration"]: r for r in result["iterations"]}
    for k in sorted(set(ours) & set(theirs)):
        (p1, q1), (p2, q2) = ours[k], theirs[k]
        rec = {"push_bit_identical": bool(p1.tobytes() == p2.tobytes()),
               "pull_bit_identical": bool(q1.tobytes() == q2.tobytes()),
               "push_max_abs_diff": float(np.max(np.abs(p1 - p2))),
               "pull_max_abs_diff": float(np.max(np.abs(q1 - q2)))}
        if k in ref_scores:
            r1, r2 = mine[k]["push"], ref_scores[k]["push"]
            rec.update({"recovery_ours": r1["recovery"], "recovery_reference": r2["recovery"],
                        "recovery_equal": r1["recovery"] == r2["recovery"],
                        "regions_equal": r1["recovery_by_region"] == r2["recovery_by_region"]})
        out["iterations"][str(k)] = rec
    out["all_iterations_bit_identical"] = bool(out["iterations"]) and all(
        v["push_bit_identical"] and v["pull_bit_identical"] for v in out["iterations"].values())
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--population-target", type=Path, default=None)
    ap.add_argument("--reference-run", type=Path, default=None)
    ap.add_argument("--output", type=Path, default=None, help="default: <run>/scores.json")
    args = ap.parse_args()
    t0 = time.perf_counter()
    result = RunScorer(args.run, args.population_target).score()
    if args.reference_run is not None:
        result["reference_comparison"] = compare_to_reference(args.run, args.reference_run,
                                                              result)
    result["seconds"] = time.perf_counter() - t0
    out = scm.refuse_historical_output(args.output or (args.run / "scores.json"))
    scm.write_json(out, result, compact=True)
    for r in result["iterations"]:
        p = r["push"]
        reg = " ".join(f"{n}={v:.3f}" for n, v in p["recovery_by_region"].items())
        pop = r["push_vs_population"]
        extra = "" if pop is None else f" pop={pop['recovery']:.4f}"
        print(f"k={r['k']:2d} R={p['recovery']:.4f} {reg}{extra}", flush=True)


if __name__ == "__main__":
    main()
