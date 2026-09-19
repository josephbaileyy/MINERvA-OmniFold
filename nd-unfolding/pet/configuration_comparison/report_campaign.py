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


def _digest(path: Path, chunk: int = 1 << 24) -> str:
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


def build_endpoint(closure_npz: Path) -> tuple[sc.Endpoint, dict[str, Any]]:
    """The frozen endpoint over the truth leg, with per-event regions from the cells."""
    import characterize_regions as cr

    with np.load(closure_npz, allow_pickle=False) as handle:
        truth_scalars = np.asarray(handle["truth_scalars"], dtype=np.float64)
        pass_truth = np.asarray(handle["pass_truth"], dtype=bool)
        pass_reco = np.asarray(handle["pass_reco"], dtype=bool)
        w_truth = np.asarray(handle["w_truth"], dtype=np.float64)
        edges_pt = np.asarray(handle["edges_0"], dtype=np.float64)
        edges_pz = np.asarray(handle["edges_1"], dtype=np.float64)

    pt, pz, eavail = truth_scalars[:, 0], truth_scalars[:, 1], truth_scalars[:, 2]
    keep = pass_truth & np.isfinite(eavail)
    both = keep & pass_reco
    denom, _, _ = np.histogram2d(pt[keep], pz[keep], bins=[edges_pt, edges_pz],
                                 weights=w_truth[keep])
    numer, _, _ = np.histogram2d(pt[both], pz[both], bins=[edges_pt, edges_pz],
                                 weights=w_truth[both])
    with np.errstate(divide="ignore", invalid="ignore"):
        acceptance = np.where(denom > 0, numer / denom, 0.0)

    prior_f = (denom / denom.sum()).ravel()
    tilt = sc.injected_truth_weights(eavail[keep], fd.ENDPOINT["amplitude"],
                                     fd.ENDPOINT["clip"])
    target, _, _ = np.histogram2d(pt[keep], pz[keep], bins=[edges_pt, edges_pz],
                                  weights=w_truth[keep] * tilt)
    displacement = np.abs((target / target.sum()).ravel() - prior_f)

    census = cr.region_census(acceptance.ravel(), prior_f, displacement)
    regional_ref = cr.regional_reference(acceptance.ravel(), displacement)
    labels, _flat = cr.region_labels_for_events(pt[keep], pz[keep], edges_pt,
                                                edges_pz, acceptance.ravel())
    endpoint = sc.Endpoint(truth_eavail=eavail[keep], region_of_event=labels,
                           base_weights=w_truth[keep])
    context = {
        "closure_npz": {"path": str(closure_npz), "sha256": _digest(closure_npz)},
        "truth_rows_scored": int(keep.sum()),
        "census": census,
        "regional_reference": regional_ref,
        "scoreable_regions": census["scoreable_regions"],
        "off_grid_truth_fraction": endpoint.unassigned_fraction,
    }
    return endpoint, context


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True,
                        help="directory holding final/ and pilot/")
    parser.add_argument("--closure-npz", type=Path, required=True)
    parser.add_argument("--reference", type=float, required=True,
                        help="the applicable aggregate reference ceiling")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    endpoint, context = build_endpoint(args.closure_npz)
    scoreable = context["scoreable_regions"]

    def score_all(stage: str) -> list[dict[str, Any]]:
        return [sc.score_run(run, endpoint, scoreable_regions=scoreable)
                for run in discover(args.campaign, stage)]

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
