"""Walk a finished campaign directory and write the report. One command.

This is the continuation command named in the handoff: given the campaign
directory and the closure inputs, it scores every run, applies the frozen rule
and writes `campaign_report.json`. It computes nothing that `score_campaign`
does not; it exists so the path from weights to verdict is one invocation whose
inputs are all recorded, rather than a sequence somebody reassembles later.

It FAILS rather than reports when the campaign is incomplete. A partial campaign
scored as if it were whole is the single most available way to get a decision
out of this comparison early, and the rule is that the sample is the frozen one.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

import frozen_design as fd
import score_campaign as sc


def _digest(path: Path | str, chunk: int = 1 << 24) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            h.update(block)
    return h.hexdigest()


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return "unknown"


def discover(campaign: Path, stage: str) -> list[sc.Run]:
    """Every weights file under `campaign/<stage>`, loaded through its receipt."""
    folder = campaign / stage
    if not folder.is_dir():
        raise FileNotFoundError(
            f"no {stage} directory under {campaign}. The comparison is not "
            "complete and scoring it would report a sample nobody planned"
        )
    runs = [sc.load_run(p) for p in sorted(folder.rglob("weights_*.npz"))]
    if not runs:
        raise FileNotFoundError(f"{folder} holds no weights files")
    return runs


def build_endpoint(closure_npz: Path | str, weights_npz: Path | str
                   ) -> tuple[sc.Endpoint, dict[str, Any]]:
    """The frozen endpoint over the TWO HALVES a run actually used.

    The halves come from the run's own weights file -- `dump_rows_a`,
    `dump_rows_b`, `tilt_a` -- not from replaying the subsample and split
    logic here. A second implementation of the split is a second thing that
    can disagree with the first, and it would disagree silently: the spectra
    would still compute.
    """
    import characterize_regions as cr

    closure_npz, weights_npz = Path(closure_npz), Path(weights_npz)
    with np.load(weights_npz) as run:
        rows_a = np.asarray(run["dump_rows_a"]).astype(np.int64)
        rows_b = np.asarray(run["dump_rows_b"]).astype(np.int64)
        tilt_a = np.asarray(run["tilt_a"]).astype(np.float64)

    with np.load(closure_npz, allow_pickle=False) as handle:
        truth_scalars = np.asarray(handle["truth_scalars"], dtype=np.float64)
        pass_truth = np.asarray(handle["pass_truth"], dtype=bool)
        pass_reco = np.asarray(handle["pass_reco"], dtype=bool)
        w_truth = np.asarray(handle["w_truth"], dtype=np.float64)
        edges_pt = np.asarray(handle["edges_0"], dtype=np.float64)
        edges_pz = np.asarray(handle["edges_1"], dtype=np.float64)

    pt, pz = truth_scalars[:, 0], truth_scalars[:, 1]
    eavail = truth_scalars[:, 2]

    # The acceptance map and the regional references come from the WHOLE
    # truth-passing population, not from either half: a reference built from
    # half B would move with the split.
    keep = pass_truth & np.isfinite(eavail)
    both = keep & pass_reco
    denom, _, _ = np.histogram2d(pt[keep], pz[keep], bins=[edges_pt, edges_pz],
                                 weights=w_truth[keep])
    numer, _, _ = np.histogram2d(pt[both], pz[both], bins=[edges_pt, edges_pz],
                                 weights=w_truth[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acceptance = np.where(denom > 0, numer / denom, 0.0)
    prior_f = (denom / denom.sum()).ravel()
    tilt_all, _spec = _tilt(eavail[keep])
    target, _, _ = np.histogram2d(pt[keep], pz[keep], bins=[edges_pt, edges_pz],
                                  weights=w_truth[keep] * tilt_all)
    displacement = np.abs((target / target.sum()).ravel() - prior_f)

    census = cr.region_census(acceptance.ravel(), prior_f, displacement)
    regional_ref = cr.regional_reference(acceptance.ravel(), displacement)

    # Score on each half's TRUTH-PASSING rows: the injection is a truth-level
    # reweighting and is undefined elsewhere.
    keep_a = pass_truth[rows_a] & np.isfinite(eavail[rows_a])
    keep_b = pass_truth[rows_b] & np.isfinite(eavail[rows_b])
    sel_a, sel_b = rows_a[keep_a], rows_b[keep_b]

    labels_a, _ = cr.region_labels_for_events(pt[sel_a], pz[sel_a], edges_pt,
                                              edges_pz, acceptance.ravel())
    labels_b, _ = cr.region_labels_for_events(pt[sel_b], pz[sel_b], edges_pt,
                                              edges_pz, acceptance.ravel())

    endpoint = sc.Endpoint(
        eavail_a=eavail[sel_a], w_truth_a=w_truth[sel_a],
        tilt_a=tilt_a[keep_a], region_a=labels_a,
        eavail_b=eavail[sel_b], w_truth_b=w_truth[sel_b], region_b=labels_b,
        # The push spans all of half B; this says which of those rows the
        # endpoint scores.
        prior_selector=keep_b)
    context = {
        "closure_npz": {"path": str(closure_npz), "sha256": _digest(closure_npz)},
        "half_a_rows": int(sel_a.size), "half_b_rows": int(sel_b.size),
        "half_b_rows_dropped_not_truth_passing": int(rows_b.size - sel_b.size),
        "halves_disjoint": bool(np.intersect1d(rows_a, rows_b).size == 0),
        "census": census,
        "regional_reference": regional_ref,
        "scoreable_regions": census["scoreable_regions"],
        "off_grid_truth_fraction": endpoint.unassigned_fraction,
    }
    if not context["halves_disjoint"]:
        raise SystemExit(
            "[report] the run's two halves overlap. The estimator saw events it "
            "had to reweight, so the closure has no power and the number it "
            "produced is not a recovery")
    return endpoint, context


def _tilt(eavail: np.ndarray):
    import closure_powered_truth_reweight as cp
    return cp.clipped_exponential_tilt(
        np.asarray(eavail, dtype=np.float64),
        amplitude=float(fd.ENDPOINT["amplitude"]),
        clip_z=float(fd.ENDPOINT["clip"]))


def _halves_of(weights_npz: Path) -> tuple[str, str]:
    """A cheap fingerprint of a run's two halves, to prove they are the same."""
    with np.load(weights_npz) as run:
        return (hashlib.sha256(np.asarray(run["dump_rows_a"]).tobytes()).hexdigest(),
                hashlib.sha256(np.asarray(run["dump_rows_b"]).tobytes()).hexdigest())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True,
                        help="directory holding final/ and pilot/")
    parser.add_argument("--closure-npz", type=Path, required=True)
    parser.add_argument("--reference", type=float, required=True,
                        help="the applicable aggregate reference ceiling")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    first = sorted((args.campaign / "final").rglob("weights_*.npz"))
    if not first:
        raise FileNotFoundError(
            f"no final-stage weights under {args.campaign}; the comparison is "
            "not complete and scoring it would report a sample nobody planned")
    endpoint, context = build_endpoint(args.closure_npz, first[0])
    scoreable = context["scoreable_regions"]
    reference_halves = _halves_of(first[0])

    def score_all(stage: str) -> list[dict[str, Any]]:
        scored = []
        for run in discover(args.campaign, stage):
            if _halves_of(Path(run.source)) != reference_halves:
                raise SystemExit(
                    f"[report] {run.source} used different halves from "
                    f"{first[0]}. Every run must be scored against the same "
                    "split or the paired difference is not paired")
            scored.append(sc.score_run(run, endpoint, scoreable_regions=scoreable))
        return scored

    final = score_all("final")
    pilot = score_all("pilot") if (args.campaign / "pilot").is_dir() else None

    report = sc.score_campaign(
        final, reference=args.reference,
        regional_reference=context["regional_reference"],
        scoreable_regions=scoreable, region_census=context["census"],
        pilot_scores=pilot)
    report["provenance"] = {
        "commit": _commit(),
        "campaign_dir": str(args.campaign),
        "aggregate_reference": args.reference,
        **context,
    }
    report["per_run"] = final
    report["scope_note"] = (
        "PET is diagnostic method development. This report is not a publication "
        "adoption, a covariance, a systematic or a central-value change."
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str))
    print(f"[report] {report['verdict']} / {report['recommendation']}")
    print(f"[report] mean d = {report['interval']['mean']:+.4f} "
          f"[{report['interval']['ci_low']:+.4f}, "
          f"{report['interval']['ci_high']:+.4f}] "
          f"over {report['interval']['n_pairs']} pairs")
    print(f"[report] written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
