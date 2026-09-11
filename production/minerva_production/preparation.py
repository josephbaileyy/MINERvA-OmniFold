"""Synthetic event fixtures and per-playlist ROOT preparation plans."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def root_plan(config: dict[str, Any], input_path: Path, output: Path) -> dict[str, Any]:
    """Plan per-playlist event loops and require a separate normalization product.

    Parameters
    ----------
    config : dict
        Paths to the built event loop and the independently prepared flux file.
    input_path : Path
        JSON with one data/MC manifest pair per playlist.
    output : Path
        Fresh parent directory for per-playlist products.

    Returns
    -------
    dict
        Commands and prerequisites only. No jobs or products are created.
    """
    from .storage import ROOT, read_json

    if set(config) != {"mode", "event_loop", "flux_file", "n_nucleons"}:
        raise ValueError(
            "root-plan config requires exactly mode, event_loop, flux_file, n_nucleons"
        )
    if not config["flux_file"] or config["n_nucleons"] <= 0:
        raise ValueError(
            "separate POT-weighted flux_file and positive geometry n_nucleons are required"
        )
    inventory = read_json(input_path)["playlists"]
    names = [entry["name"] for entry in inventory]
    if (
        not names
        or len(set(names)) != len(names)
        or any(not name.replace("_", "").replace("-", "").isalnum() for name in names)
    ):
        raise ValueError("playlists require distinct simple names")
    executable = str(Path(config["event_loop"]).expanduser().resolve())
    commands = []
    prerequisites = [executable, str(Path(config["flux_file"]).expanduser().resolve())]
    for entry in inventory:
        manifests = [
            str((input_path.parent / entry[key]).resolve())
            for key in ("data_manifest", "mc_manifest")
        ]
        prerequisites.extend(manifests)
        commands.append(
            {"cwd": str(output / entry["name"]), "argv": [executable, *manifests]}
        )
    merged = output / "events.root"
    return {
        "status": "plan-only",
        "commands": commands,
        "merge": [
            "python",
            str(ROOT / "2d-unfolding/uq/hadd_universes_full.py"),
            str(merged),
            *[str(output / name / "runEventLoopOmniFold.root") for name in names],
        ],
        "normalization": {
            "flux_file": config["flux_file"],
            "n_nucleons": config["n_nucleons"],
            "flux_histogram": "pTmu_reweightedflux_integrated",
            "flux_units": "m^-2/POT",
        },
        "missing_paths": [path for path in prerequisites if not Path(path).is_file()],
        "requirements": [
            "Each manifest must contain exactly its declared playlist; inspect run identities before execution.",
            "Prepare baseline flux separately per playlist and combine with combine_flux_MEFHC.py.",
            "Use the governing event-loop launcher/environment and authorization; this plan does not authorize execution.",
            "Do not use summed nucleon metadata from merged files.",
        ],
    }


def synthetic(path: Path, config: dict[str, Any]) -> None:
    """Write a deterministic, weighted, aligned fixture with misses and truth cuts."""
    import numpy as np

    if set(config) != {"mode", "seed", "events"} or config["mode"] != "synthetic":
        raise ValueError("synthetic config requires exactly mode, seed, events")
    if (
        type(config["events"]) is not int
        or config["events"] < 400
        or type(config["seed"]) is not int
        or config["seed"] < 0
    ):
        raise ValueError(
            "synthetic fixture requires events >= 400 and a nonnegative integer seed"
        )
    if path.exists():
        raise FileExistsError(path)
    rng = np.random.default_rng(config["seed"])
    count = config["events"]
    truth = rng.uniform([0, 0], [3, 5], (count, 2))
    reco = np.clip(
        truth + rng.normal(0, 0.18, truth.shape), [0.001, 0.001], [2.999, 4.999]
    )
    measured = rng.uniform([0, 0], [3, 5], (count, 2))
    weights = rng.uniform(0.8, 1.2, count)
    pass_truth = rng.random(count) > 0.04
    pass_reco = rng.random(count) > 0.12
    edges = [[0, 1, 3], [0, 2, 5]]
    denominator = (
        np.histogramdd(truth[pass_truth], bins=edges, weights=weights[pass_truth])[0]
        / 0.9
    )
    meta = {
        "selection": "synthetic-cuts-v1",
        "background": "signal-only",
        "feature_names": ["pt", "pparallel"],
        "feature_units": {"pt": "GeV", "pparallel": "GeV"},
        "flux_axis": 0,
        "normalization_units": {
            "flux": "m^-2/POT",
            "data_pot": "POT",
            "n_nucleons": "nucleons",
        },
        "normalization_source": "synthetic fixture, not experimental normalization",
        "denominator_policy": "fixed-under-bootstrap",
        "fixture_config": config,
        "output_contract": {
            "axes": [
                {"name": name, "unit": "GeV", "edges": edge}
                for name, edge in zip(["pt", "pparallel"], edges)
            ],
            "ordering": "C",
            "meaning": "density",
            "value_unit": "cm^2/nucleon",
            "support": [True] * 4,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents two fixture producers from replacing each other.
    with path.open("xb") as stream:
        np.savez_compressed(
            stream,
            MCgen=truth,
            MCreco=reco,
            measured=measured,
            w_truth=weights,
            w_reco=weights.copy(),
            measured_weights=np.ones(count),
            pass_truth=pass_truth,
            pass_reco=pass_reco,
            meas_pass_reco=rng.random(count) > 0.03,
            truth_id=np.arange(count),
            reco_id=np.arange(count),
            data_id=np.arange(count),
            denom_nd=denominator,
            flux=np.array([0.0005, 0.0007]),
            data_pot=1.0e20,
            n_nucleons=3.2353e30,
            metadata=json.dumps(meta),
        )
