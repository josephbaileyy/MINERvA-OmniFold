"""Compare guarded cached-bootstrap entry points on identical synthetic rows.

Run with the audit's Python environment, two isolated checkout paths, and a fresh
scratch output directory. This measures local process wall time, including IO
and provenance; it does not benchmark ROOT preparation or production training.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


def _run(argv: list[str], cwd: Path, environment: dict[str, str]) -> float:
    start = time.perf_counter()
    subprocess.run(
        argv, cwd=cwd, env=environment, check=True, capture_output=True, timeout=60
    )
    return time.perf_counter() - start


def main() -> None:
    """Write samples, numerical comparisons and runtime identity to results.json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--feature", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    main_root, feature = args.main.resolve(), args.feature.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(feature))
    import numpy as np

    from production.minerva_production.preparation import synthetic
    from production.minerva_production.scalar import load_inputs, resolve_config

    environment = dict(os.environ)
    environment.pop("GIT_SSH_COMMAND", None)
    environment.update(
        OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", LOKY_MAX_CPU_COUNT="1"
    )
    raw_config = {
        "backend": "cached-lgbm-v1",
        "features": ["pt", "pparallel"],
        "selection": "synthetic-cuts-v1",
        "background": "signal-only",
        "iterations": 2,
        "estimator_seed": 42,
    }
    config = resolve_config(raw_config)
    fixture = output / "original.npz"
    synthetic(fixture, {"mode": "synthetic", "events": 800, "seed": 17})
    arrays, metadata = load_inputs(fixture, config)
    selected = arrays["meas_pass_reco"]
    for key in ("measured", "measured_weights", "data_id"):
        arrays[key] = arrays[key][selected]
    arrays["meas_pass_reco"] = np.ones(int(selected.sum()), dtype=bool)
    events = output / "events.npz"
    np.savez_compressed(events, **arrays, metadata=json.dumps(metadata))
    legacy_events = output / "legacy.npz"
    axes = metadata["output_contract"]["axes"]
    np.savez_compressed(
        legacy_events,
        **arrays,
        nedges=2,
        edges_0=axes[0]["edges"],
        edges_1=axes[1]["edges"],
    )
    config_path = output / "config.json"
    config_path.write_text(json.dumps(raw_config))
    nominal = output / "nominal"
    _run(
        [
            sys.executable,
            "production/unfold_gbdt.py",
            "--config",
            str(config_path),
            "--input",
            str(events),
            "--output",
            str(nominal),
        ],
        feature,
        environment,
    )
    samples: dict[str, list[float]] = {"retained": [], "interface": []}
    warmups: dict[str, float] = {}
    differences = []
    product_bytes: dict[str, int] = {}
    for iteration in range(6):
        retained = output / f"retained-{iteration}.npz"
        members = output / f"interface-{iteration}"
        commands = {
            "retained": [
                sys.executable,
                str(main_root / "nd-unfolding/mnv_guarded_run.py"),
                "--expect-root",
                str(main_root),
                "--",
                str(main_root / "nd-unfolding/bootstrap_nd.py"),
                "--npz",
                str(legacy_events),
                "--seed",
                "7",
                "--iters",
                "2",
                "--estimator-seed",
                "42",
                "--out",
                str(retained),
            ],
            "interface": [
                sys.executable,
                "production/uncertainties.py",
                "run",
                "--source",
                "statistical",
                "--mode",
                "data-plus-mc",
                "--seeds",
                "7",
                "--config",
                str(config_path),
                "--input",
                str(events),
                "--nominal",
                str(nominal),
                "--output",
                str(members),
            ],
        }
        order = (
            ("retained", "interface")
            if iteration % 2 == 0
            else ("interface", "retained")
        )
        for name in order:
            elapsed = _run(
                commands[name],
                main_root if name == "retained" else feature,
                environment,
            )
            if iteration == 0:
                warmups[name] = elapsed
            else:
                samples[name].append(elapsed)
        with np.load(retained) as old, np.load(members / "member_7/result.npz") as new:
            np.testing.assert_allclose(
                new["xsec"], old["xsec_flat"], rtol=1e-12, atol=0
            )
            widths = np.outer(
                np.diff(axes[0]["edges"]), np.diff(axes[1]["edges"])
            ).ravel()
            np.testing.assert_allclose(
                new["xsec"] @ widths, old["total_xsec"], rtol=1e-12, atol=0
            )
            differences.append(float(np.max(np.abs(new["xsec"] - old["xsec_flat"]))))
        product_bytes = {
            "retained": retained.stat().st_size,
            "interface": sum(
                path.stat().st_size for path in (members / "member_7").iterdir()
            ),
        }
    report: dict[str, Any] = {
        "main_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=main_root, text=True
        ).strip(),
        "feature_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=feature, text=True
        ).strip(),
        "python": sys.version.split()[0],
        "versions": {
            name: importlib.metadata.version(name)
            for name in (
                "numpy",
                "lightgbm",
                "scikit-learn",
                "scipy",
                "joblib",
                "threadpoolctl",
            )
        },
        "environment": {
            name: environment[name]
            for name in (
                "OPENBLAS_NUM_THREADS",
                "OMP_NUM_THREADS",
                "LOKY_MAX_CPU_COUNT",
            )
        },
        "config": config,
        "fixture_seed": 17,
        "mc_rows": len(arrays["MCgen"]),
        "data_rows": len(arrays["measured"]),
        "bootstrap_seed": 7,
        "array_sha256": {
            name: hashlib.sha256(value.tobytes()).hexdigest()
            for name, value in arrays.items()
        },
        "warmups_seconds": warmups,
        "samples_seconds": samples,
        "median_seconds": {
            name: statistics.median(values) for name, values in samples.items()
        },
        "range_seconds": {
            name: [min(values), max(values)] for name, values in samples.items()
        },
        "maximum_absolute_xsec_difference_each_pair": differences,
        "comparison": {"rtol": 1e-12, "atol": 0, "pairs_passed": 6},
        "member_output_bytes": product_bytes,
        "limitations": "Synthetic two-dimensional cached backend; warm filesystem, fresh processes; nominal setup excluded; outputs differ in provenance and intermediates; no production throughput or peak-memory claim.",
    }
    (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
