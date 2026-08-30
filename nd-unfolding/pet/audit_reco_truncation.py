#!/usr/bin/env python3
"""Stream the predeclared reco-cloud rank-12 truncation audit from ROOT."""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


CONTRACT_ID = "PET-G6-GAP3-RECO-TRUNCATION-20260830"
SOURCE_RELATIVE_PATH = Path(
    "nd-unfolding/g2_fullevent/merged/"
    "runEventLoopOmniFold_G2_FPS_MEFHC.root"
)
MERGE_RECEIPT_RELATIVE_PATH = Path(
    "nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json"
)
EXPECTED_SOURCE_SHA256 = (
    "9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f"
)
EXPECTED_SOURCE_SIZE = 113_496_440_965
EXPECTED_MERGE_RECEIPT_SHA256 = (
    "26ea5561f47599987ebacbf594c606309146a5f23c82af8dd0e2ca299b31efa7"
)
CAP = 12
EXPECTED_SELECTED_ROWS = {
    "signal": 20_573_521,
    "data": 4_116_128,
    "background": 564_591,
}
PT_EDGES = (
    0.0,
    0.07,
    0.15,
    0.25,
    0.33,
    0.4,
    0.47,
    0.55,
    0.7,
    0.85,
    1.0,
    1.25,
    1.5,
    2.5,
    4.5,
    30.0,
)
PPARALLEL_EDGES = (
    0.0,
    0.75,
    1.5,
    2.0,
    2.5,
    3.0,
    3.5,
    4.0,
    4.5,
    5.0,
    6.0,
    7.0,
    8.0,
    9.0,
    10.0,
    15.0,
    20.0,
    40.0,
    60.0,
    120.0,
)
EAVAIL_EDGES = (0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0)
Q3_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0)
AXIS_EDGES = {
    "pt": PT_EDGES,
    "pparallel": PPARALLEL_EDGES,
    "eavail": EAVAIL_EDGES,
    "q3": Q3_EDGES,
}
INVENTORIES = {
    "signal": {
        "tree": "mc_signal_reco",
        "selection": (
            "sim_pass != 0 && std::isfinite(sim) && std::isfinite(sim_pz) "
            "&& sim >= 0.0 && sim <= 30.0 && sim_pz >= 0.0 && sim_pz <= 120.0"
        ),
        "axes": {
            "pt": "sim",
            "pparallel": "sim_pz",
            "eavail": "sim_eavail",
            "q3": "sim_q3",
        },
        "weight": "w_reco",
    },
    "data": {
        "tree": "data",
        "selection": (
            "measured_pass != 0 && std::isfinite(measured) "
            "&& std::isfinite(measured_pz) && measured >= 0.0 "
            "&& measured <= 30.0 && measured_pz >= 0.0 "
            "&& measured_pz <= 120.0"
        ),
        "axes": {
            "pt": "measured",
            "pparallel": "measured_pz",
            "eavail": "measured_eavail",
            "q3": "measured_q3",
        },
        "weight": "1.0",
    },
    "background": {
        "tree": "mc_background",
        "selection": (
            "sim_background_pass != 0 && std::isfinite(sim_background) "
            "&& std::isfinite(sim_background_pz) && sim_background >= 0.0 "
            "&& sim_background <= 30.0 && sim_background_pz >= 0.0 "
            "&& sim_background_pz <= 120.0"
        ),
        "axes": {
            "pt": "sim_background",
            "pparallel": "sim_background_pz",
            "eavail": "sim_background_eavail",
            "q3": "sim_background_q3",
        },
        "weight": "w_bkg",
    },
}
METRICS = (
    "events",
    "cap_events",
    "clusters_total",
    "clusters_discarded",
    "energy_total_mev",
    "energy_discarded_mev",
)
NON_AUTHORIZATION = (
    "do_not_change_representation_or_token_cap",
    "do_not_move_or_adopt_central_value",
    "do_not_construct_covariance_or_uncertainty",
    "do_not_select_gate6_member_or_start_leg2",
    "do_not_claim_equivalence_convergence_closure_or_coverage",
    "do_not_make_publication_claim",
    "do_not_authorize_further_compute",
)


CPP_HELPERS = r"""
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <vector>
#include "ROOT/RVec.hxx"

namespace gap3 {
struct TruncationStats {
  double events;
  double cap_events;
  double clusters_total;
  double clusters_discarded;
  double energy_total_mev;
  double energy_discarded_mev;
  double nonfinite_energy_count;
  double negative_energy_count;
  double zero_energy_count;
};

TruncationStats summarize(const ROOT::VecOps::RVec<double>& energies) {
  TruncationStats result{1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  result.clusters_total = static_cast<double>(energies.size());
  result.clusters_discarded =
      energies.size() > 12 ? static_cast<double>(energies.size() - 12) : 0.0;
  result.cap_events = energies.size() > 12 ? 1.0 : 0.0;

  std::vector<double> ranked;
  ranked.reserve(energies.size());
  for (const double energy : energies) {
    if (!std::isfinite(energy)) {
      result.nonfinite_energy_count += 1.0;
      ranked.push_back(0.0);
      continue;
    }
    if (energy < 0.0) result.negative_energy_count += 1.0;
    if (energy == 0.0) result.zero_energy_count += 1.0;
    result.energy_total_mev += energy;
    ranked.push_back(energy);
  }
  std::stable_sort(ranked.begin(), ranked.end(), std::greater<double>());
  if (ranked.size() > 12) {
    for (std::size_t index = 12; index < ranked.size(); ++index) {
      result.energy_discarded_mev += ranked[index];
    }
  }
  return result;
}
}  // namespace gap3
"""


def sha256_file(path: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    """Return the SHA-256 digest of a file using bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def safe_fraction(numerator: float, denominator: float) -> float | None:
    """Return a finite fraction, or ``None`` for a non-positive denominator."""
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return None
    if denominator <= 0.0:
        return None
    return numerator / denominator


def add_metric_payloads(
    first: dict[str, float], second: dict[str, float]
) -> dict[str, float]:
    """Add persisted metric operands from two disjoint populations."""
    return {metric: float(first[metric]) + float(second[metric]) for metric in METRICS}


def derive_fractions(operands: dict[str, float]) -> dict[str, Any]:
    """Attach the three predeclared fractions to their persisted operands."""
    payload: dict[str, Any] = {metric: float(operands[metric]) for metric in METRICS}
    payload["cap_event_fraction"] = safe_fraction(
        payload["cap_events"], payload["events"]
    )
    payload["discarded_cluster_fraction"] = safe_fraction(
        payload["clusters_discarded"], payload["clusters_total"]
    )
    payload["discarded_energy_fraction"] = safe_fraction(
        payload["energy_discarded_mev"], payload["energy_total_mev"]
    )
    return payload


def _git_output(code_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(code_root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def verify_static_inputs(args: argparse.Namespace) -> dict[str, Any]:
    """Verify source, receipt, code hashes, and checkout identity before ROOT I/O."""
    code_root = args.code_root.resolve()
    data_root = args.data_root.resolve()
    source = data_root / SOURCE_RELATIVE_PATH
    merge_receipt = data_root / MERGE_RECEIPT_RELATIVE_PATH
    predeclaration = code_root / args.predeclaration_relative_path
    script = Path(__file__).resolve()

    if _git_output(code_root, "rev-parse", "HEAD") != args.expected_head:
        raise RuntimeError("code checkout HEAD does not match --expected-head")
    if _git_output(code_root, "status", "--porcelain"):
        raise RuntimeError("code checkout is not clean")

    fixed_hashes = {
        "audit": (
            script,
            args.expected_audit_sha256,
            "nd-unfolding/pet/audit_reco_truncation.py",
        ),
        "predeclaration": (
            predeclaration,
            args.expected_predeclaration_sha256,
            str(args.predeclaration_relative_path),
        ),
        "guard": (
            code_root / "nd-unfolding/mnv_guarded_run.py",
            args.expected_guard_sha256,
            "nd-unfolding/mnv_guarded_run.py",
        ),
        "merge_receipt": (
            merge_receipt,
            EXPECTED_MERGE_RECEIPT_SHA256,
            str(MERGE_RECEIPT_RELATIVE_PATH),
        ),
    }
    verified_hashes = {}
    for label, (path, expected, receipt_path) in fixed_hashes.items():
        if not path.is_file():
            raise FileNotFoundError(f"missing {label}: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"{label} SHA-256 mismatch: {actual} != {expected}")
        verified_hashes[label] = {"path": receipt_path, "sha256": actual}

    if not source.is_file():
        raise FileNotFoundError(f"missing source ROOT: {source}")
    if source.stat().st_size != EXPECTED_SOURCE_SIZE:
        raise RuntimeError(
            f"source size mismatch: {source.stat().st_size} != {EXPECTED_SOURCE_SIZE}"
        )
    source_sha256 = sha256_file(source)
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"source SHA-256 mismatch: {source_sha256} != {EXPECTED_SOURCE_SHA256}"
        )

    receipt = json.loads(merge_receipt.read_text())
    recorded_source = receipt.get("merged_root", {})
    if receipt.get("status") != "PASS":
        raise RuntimeError("merge receipt status is not PASS")
    if recorded_source.get("sha256") != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("merge receipt source SHA-256 mismatch")
    if int(recorded_source.get("size_bytes", -1)) != EXPECTED_SOURCE_SIZE:
        raise RuntimeError("merge receipt source size mismatch")

    return {
        "_source_runtime": str(source),
        "source": str(SOURCE_RELATIVE_PATH),
        "source_size_bytes": EXPECTED_SOURCE_SIZE,
        "source_sha256": source_sha256,
        "expected_head": args.expected_head,
        "verified_hashes": verified_hashes,
    }


def verify_root_schema(source: str) -> None:
    """Fail closed unless the exact G2 schema, trees, and branches are present."""
    import ROOT

    root_file = ROOT.TFile.Open(source, "READ")
    if not root_file or root_file.IsZombie():
        raise RuntimeError(f"cannot open source ROOT: {source}")
    try:
        schema = root_file.Get("petSchemaVersion")
        full_schema = root_file.Get("hasFullEventSchema")
        full_phase_space = root_file.Get("fullPhaseSpace")
        if not schema or str(schema.GetTitle()) != "g2-fullevent-v1":
            raise RuntimeError("source petSchemaVersion is not g2-fullevent-v1")
        if not full_schema or int(full_schema.GetVal()) != 1:
            raise RuntimeError("source hasFullEventSchema is not 1")
        if not full_phase_space or int(full_phase_space.GetVal()) != 1:
            raise RuntimeError("source fullPhaseSpace is not 1")
        for config in INVENTORIES.values():
            tree = root_file.Get(config["tree"])
            if not tree:
                raise RuntimeError(f"missing tree {config['tree']}")
            branches = {branch.GetName() for branch in tree.GetListOfBranches()}
            required = {"part_reco_E", *config["axes"].values()}
            if config["weight"] != "1.0":
                required.add(config["weight"])
            pass_branch = config["selection"].split()[0]
            required.add(pass_branch)
            missing = sorted(required - branches)
            if missing:
                raise RuntimeError(
                    f"tree {config['tree']} missing required branches: {missing}"
                )
    finally:
        root_file.Close()


def _book_histograms(
    node: Any,
    *,
    prefix: str,
    axis_columns: dict[str, str],
) -> dict[str, Any]:
    actions: dict[str, Any] = {}
    for weighted in (False, True):
        family = "weighted" if weighted else "unweighted"
        suffix = "_weighted" if weighted else ""
        for axis_name, axis_column in axis_columns.items():
            edges = AXIS_EDGES[axis_name]
            model_edges = array("d", edges)
            for metric in METRICS:
                model = (
                    f"{prefix}_{family}_{axis_name}_{metric}",
                    "",
                    len(edges) - 1,
                    model_edges,
                )
                actions[f"{family}:{axis_name}:{metric}"] = node.Histo1D(
                    model, axis_column, f"gap3_{metric}{suffix}"
                )

        pt_edges = array("d", PT_EDGES)
        pparallel_edges = array("d", PPARALLEL_EDGES)
        for metric in METRICS:
            model = (
                f"{prefix}_{family}_pt_pparallel_{metric}",
                "",
                len(PT_EDGES) - 1,
                pt_edges,
                len(PPARALLEL_EDGES) - 1,
                pparallel_edges,
            )
            actions[f"{family}:pt_pparallel:{metric}"] = node.Histo2D(
                model,
                axis_columns["pt"],
                axis_columns["pparallel"],
                f"gap3_{metric}{suffix}",
            )
    return actions


def _book_inventory(source: str, name: str, config: dict[str, Any]) -> dict[str, Any]:
    import ROOT

    node = ROOT.RDataFrame(config["tree"], source).Filter(config["selection"])
    node = node.Define("gap3_stats", "gap3::summarize(part_reco_E)")
    for metric in METRICS:
        node = node.Define(f"gap3_{metric}", f"gap3_stats.{metric}")
    node = node.Define("gap3_nonfinite_energy_count", "gap3_stats.nonfinite_energy_count")
    node = node.Define("gap3_negative_energy_count", "gap3_stats.negative_energy_count")
    node = node.Define("gap3_zero_energy_count", "gap3_stats.zero_energy_count")
    node = node.Define("gap3_raw_weight", config["weight"])
    node = node.Define(
        "gap3_invalid_weight",
        "(!std::isfinite(gap3_raw_weight) || gap3_raw_weight < 0.0) ? 1.0 : 0.0",
    )
    node = node.Define(
        "gap3_analysis_weight",
        "std::isfinite(gap3_raw_weight) && gap3_raw_weight >= 0.0 "
        "? gap3_raw_weight : 0.0",
    )
    for metric in METRICS:
        node = node.Define(
            f"gap3_{metric}_weighted",
            f"gap3_{metric} * gap3_analysis_weight",
        )

    actions: dict[str, Any] = {
        "selected_rows": node.Count(),
        "nonfinite_energy_count": node.Sum("gap3_nonfinite_energy_count"),
        "negative_energy_count": node.Sum("gap3_negative_energy_count"),
        "zero_energy_count": node.Sum("gap3_zero_energy_count"),
        "invalid_weight_count": node.Sum("gap3_invalid_weight"),
    }
    for family, suffix in (("unweighted", ""), ("weighted", "_weighted")):
        for metric in METRICS:
            actions[f"aggregate:{family}:{metric}"] = node.Sum(
                f"gap3_{metric}{suffix}"
            )
    actions.update(
        _book_histograms(node, prefix=name, axis_columns=config["axes"])
    )
    return actions


def _run_actions(actions: dict[str, Any]) -> None:
    import ROOT

    ROOT.RDF.RunGraphs(list(actions.values()))


def _histogram_operands_1d(
    actions: dict[str, Any], family: str, axis_name: str
) -> list[dict[str, float]]:
    histograms = {
        metric: actions[f"{family}:{axis_name}:{metric}"].GetValue()
        for metric in METRICS
    }
    edges = AXIS_EDGES[axis_name]
    bins = []
    for index in range(1, len(edges)):
        operands = {
            metric: float(histograms[metric].GetBinContent(index))
            for metric in METRICS
        }
        bins.append(
            {
                "low": edges[index - 1],
                "high": edges[index],
                **derive_fractions(operands),
            }
        )
    return bins


def _histogram_operands_2d(
    actions: dict[str, Any], family: str
) -> list[dict[str, float]]:
    histograms = {
        metric: actions[f"{family}:pt_pparallel:{metric}"].GetValue()
        for metric in METRICS
    }
    bins = []
    for pt_index in range(1, len(PT_EDGES)):
        for pparallel_index in range(1, len(PPARALLEL_EDGES)):
            operands = {
                metric: float(
                    histograms[metric].GetBinContent(pt_index, pparallel_index)
                )
                for metric in METRICS
            }
            bins.append(
                {
                    "pt_low": PT_EDGES[pt_index - 1],
                    "pt_high": PT_EDGES[pt_index],
                    "pparallel_low": PPARALLEL_EDGES[pparallel_index - 1],
                    "pparallel_high": PPARALLEL_EDGES[pparallel_index],
                    **derive_fractions(operands),
                }
            )
    return bins


def _extract_inventory(actions: dict[str, Any]) -> dict[str, Any]:
    aggregates = {}
    kinematics = {}
    for family in ("unweighted", "weighted"):
        operands = {
            metric: float(actions[f"aggregate:{family}:{metric}"].GetValue())
            for metric in METRICS
        }
        aggregates[family] = derive_fractions(operands)
        kinematics[family] = {
            axis_name: _histogram_operands_1d(actions, family, axis_name)
            for axis_name in AXIS_EDGES
        }
        kinematics[family]["pt_pparallel"] = _histogram_operands_2d(
            actions, family
        )
    return {
        "selected_rows": int(actions["selected_rows"].GetValue()),
        "quality": {
            "nonfinite_energy_count": int(
                round(actions["nonfinite_energy_count"].GetValue())
            ),
            "negative_energy_count": int(
                round(actions["negative_energy_count"].GetValue())
            ),
            "zero_energy_count": int(round(actions["zero_energy_count"].GetValue())),
            "invalid_weight_count": int(
                round(actions["invalid_weight_count"].GetValue())
            ),
        },
        "aggregate": aggregates,
        "kinematics": kinematics,
    }


def _combine_bin_lists(
    first: list[dict[str, Any]], second: list[dict[str, Any]], coordinate_keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    combined = []
    for first_bin, second_bin in zip(first, second, strict=True):
        for key in coordinate_keys:
            if first_bin[key] != second_bin[key]:
                raise RuntimeError(f"combined-MC bin coordinate mismatch for {key}")
        operands = add_metric_payloads(first_bin, second_bin)
        combined.append(
            {key: first_bin[key] for key in coordinate_keys}
            | derive_fractions(operands)
        )
    return combined


def combine_mc(signal: dict[str, Any], background: dict[str, Any]) -> dict[str, Any]:
    """Combine disjoint signal and background operands without averaging fractions."""
    payload: dict[str, Any] = {
        "selected_rows": signal["selected_rows"] + background["selected_rows"],
        "quality": {
            key: signal["quality"][key] + background["quality"][key]
            for key in signal["quality"]
        },
        "aggregate": {},
        "kinematics": {},
    }
    for family in ("unweighted", "weighted"):
        payload["aggregate"][family] = derive_fractions(
            add_metric_payloads(
                signal["aggregate"][family], background["aggregate"][family]
            )
        )
        payload["kinematics"][family] = {}
        for axis_name in AXIS_EDGES:
            payload["kinematics"][family][axis_name] = _combine_bin_lists(
                signal["kinematics"][family][axis_name],
                background["kinematics"][family][axis_name],
                ("low", "high"),
            )
        payload["kinematics"][family]["pt_pparallel"] = _combine_bin_lists(
            signal["kinematics"][family]["pt_pparallel"],
            background["kinematics"][family]["pt_pparallel"],
            ("pt_low", "pt_high", "pparallel_low", "pparallel_high"),
        )
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def run(args: argparse.Namespace) -> int:
    """Run the hash-bound streaming audit and persist its terminal receipt."""
    provenance = verify_static_inputs(args)
    source = provenance.pop("_source_runtime")

    import ROOT

    ROOT.EnableImplicitMT(args.threads)
    ROOT.gInterpreter.Declare(CPP_HELPERS)
    verify_root_schema(source)

    inventories = {}
    for name, config in INVENTORIES.items():
        print(f"[gap3] scanning {name} tree={config['tree']}", flush=True)
        actions = _book_inventory(source, name, config)
        _run_actions(actions)
        inventories[name] = _extract_inventory(actions)
        print(
            f"[gap3] {name} selected_rows={inventories[name]['selected_rows']}",
            flush=True,
        )

    inventories["mc_combined"] = combine_mc(
        inventories["signal"], inventories["background"]
    )

    row_checks = {
        name: inventories[name]["selected_rows"] == expected
        for name, expected in EXPECTED_SELECTED_ROWS.items()
    }
    quality_checks = {
        f"{name}:{key}": value == 0
        for name in EXPECTED_SELECTED_ROWS
        for key, value in inventories[name]["quality"].items()
        if key != "zero_energy_count"
    }
    denominator_checks = {
        f"{name}:{family}:positive_cluster_denominator": (
            inventories[name]["aggregate"][family]["clusters_total"] > 0.0
        )
        for name in EXPECTED_SELECTED_ROWS
        for family in ("unweighted", "weighted")
    }
    denominator_checks.update(
        {
            f"{name}:{family}:positive_energy_denominator": (
                inventories[name]["aggregate"][family]["energy_total_mev"] > 0.0
            )
            for name in EXPECTED_SELECTED_ROWS
            for family in ("unweighted", "weighted")
        }
    )
    all_checks = row_checks | quality_checks | denominator_checks
    status = "PASS" if all(all_checks.values()) else "INVALID_OR_INCOMPLETE"
    payload = {
        "schema_version": 1,
        "contract_id": CONTRACT_ID,
        "status": status,
        "provenance": provenance,
        "runtime": {
            "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
            "slurm_cpus_per_task": os.environ.get("SLURM_CPUS_PER_TASK"),
            "threads": args.threads,
            "python": sys.version,
            "root_version": str(ROOT.gROOT.GetVersion()),
        },
        "contract": {
            "cap": CAP,
            "expected_selected_rows": EXPECTED_SELECTED_ROWS,
            "axis_edges": {key: list(value) for key, value in AXIS_EDGES.items()},
            "primary": "unweighted micro-fractions",
            "secondary": "analysis-weighted micro-fractions",
            "non_authorization": NON_AUTHORIZATION,
        },
        "checks": all_checks,
        "inventories": inventories,
    }
    _write_json_atomic(args.output.resolve(), payload)
    print(json.dumps({"status": status, "output": str(args.output)}, sort_keys=True))
    return 0 if status == "PASS" else 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--expected-predeclaration-sha256", required=True)
    parser.add_argument("--expected-guard-sha256", required=True)
    parser.add_argument(
        "--predeclaration-relative-path",
        type=Path,
        default=Path(
            "docs/orchestration/"
            "PREDECLARATION-20260830-gate6-gap3-reco-truncation-audit.md"
        ),
    )
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    if args.threads != 8:
        parser.error("the predeclared scan requires exactly 8 threads")
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
