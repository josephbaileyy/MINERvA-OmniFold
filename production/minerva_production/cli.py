"""Consistent command boundaries; planning never trains or creates products."""

from __future__ import annotations

import argparse
import json
import subprocess
from importlib import import_module
from pathlib import Path
from typing import Any

from .storage import (
    ROOT,
    check_output,
    code_identity,
    digest,
    fingerprint,
    legacy_module,
    load_result,
    read_json,
    save_result,
)

DESCRIPTIONS = {
    "prepare_events": "Prepare a synthetic event fixture or plan per-playlist ROOT production with separate flux normalization.",
    "unfold_gbdt": "Unfold validated cached scalar arrays with the shared nominal/replica GBDT calculation.",
    "unfold_pet": "Run the guarded full-event PET diagnostic trainer in its TensorFlow environment.",
    "uncertainties": "Run statistical or ML split members and combine a declared, matched family; systematic paths require their governing construction.",
    "closure": "Construct strict signal-MC pseudo-data and reuse nominal unfolding; this does not measure coverage.",
    "project": "Project compatible cross sections and covariance without retraining, preserving widths and support.",
}


def parser(operation: str) -> argparse.ArgumentParser:
    """Build lightweight help with common config/input/output and plan arguments."""
    ap = argparse.ArgumentParser(description=DESCRIPTIONS[operation])
    ap.add_argument(
        "--config", required=True, type=Path, help="explicit JSON configuration"
    )
    ap.add_argument(
        "--input",
        type=Path,
        required=operation != "prepare_events",
        help="event NPZ, nominal result directory, or playlist inventory",
    )
    ap.add_argument(
        "--output",
        type=Path,
        required=True,
        help="fresh result directory (prepare_events synthetic: NPZ file)",
    )
    ap.add_argument(
        "--plan",
        action="store_true",
        help="resolve settings and prerequisites only; no dataset loading or output writes",
    )
    if operation in {"unfold_gbdt", "closure", "project", "uncertainties"}:
        ap.add_argument(
            "--resume",
            action="store_true",
            help="reuse only a complete output with matching input/config/code and payload digest",
        )
    if operation == "uncertainties":
        ap.add_argument("action", choices=["run", "combine"])
        ap.add_argument(
            "--source", choices=["statistical", "ml", "systematic"], required=True
        )
        ap.add_argument(
            "--mode",
            choices=["data-only", "data-plus-mc"],
            help="required for statistical members; never inferred",
        )
        ap.add_argument(
            "--seeds",
            type=int,
            nargs="+",
            required=True,
            help="exact nonnegative member seed inventory",
        )
        ap.add_argument(
            "--nominal",
            type=Path,
            required=True,
            help="complete nominal result with identical calculation identity",
        )
    return ap


def _scalar_context(
    args: argparse.Namespace, cfg: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    from .scalar import load_inputs

    before = args.input.stat()
    inputs, meta = load_inputs(args.input, cfg)
    input_digest = digest(args.input)
    after = args.input.stat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError("input changed while loading/hashing; use an immutable cache")
    classifiers = legacy_module("omnifold_nn_core").make_estimators(
        "lgbm", len(cfg["features"]), seed=cfg["estimator_seed"]
    )
    meta = {
        **meta,
        "normalization_values": {
            "flux": inputs["flux"].tolist(),
            "data_pot": float(inputs["data_pot"]),
            "n_nucleons": float(inputs["n_nucleons"]),
        },
    }
    identity = {
        "config": cfg,
        "input_sha256": input_digest,
        "code": code_identity(),
        "estimator_parameters": {
            name: model.get_params()
            for name, model in zip(
                ("classifier1", "classifier2", "regressor"), classifiers
            )
        },
    }
    return inputs, meta, identity


def _unfold(args: argparse.Namespace, cfg: dict[str, Any], operation: str) -> None:
    from .scalar import calculate, closure_inputs

    inputs, meta, identity = _scalar_context(args, cfg)
    identity = {**identity, "operation": operation}
    if check_output(args.output, identity, args.resume):
        return
    if operation == "closure":
        inputs, reference = closure_inputs(inputs, meta)
        arrays = calculate(inputs, meta, cfg)
        arrays.update(
            {
                "truth_xsec": reference["xsec"],
                "residual": arrays["xsec"] - reference["xsec"],
            }
        )
    else:
        arrays = calculate(inputs, meta, cfg)
    save_result(
        args.output,
        arrays,
        {
            "identity": identity,
            "output_contract": meta["output_contract"],
            "input_contract": meta,
        },
    )


def _uncertainties(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    from .scalar import calculate
    from .uncertainty import assemble, statistical_inputs, training_config

    nominal_arrays, nominal_record = load_result(args.nominal)
    nominal_identity = nominal_record["identity"]
    if (
        nominal_identity.get("operation") != "unfold_gbdt"
        or nominal_identity["config"] != cfg
    ):
        raise ValueError(
            "uncertainties require a matched nominal procedure and configuration"
        )
    if nominal_identity["code"] != code_identity():
        raise ValueError("nominal code/dependencies differ; use a matched nominal")
    perturbation = {"source": args.source, "mode": args.mode}
    if args.action == "run":
        inputs, meta, identity = _scalar_context(args, cfg)
        if {**identity, "operation": "unfold_gbdt"} != nominal_identity:
            raise ValueError("member input/config/code differs from identified nominal")
        for seed in args.seeds:
            member_identity = {
                **identity,
                "operation": "member",
                "nominal": fingerprint(nominal_record),
                "perturbation": {**perturbation, "seed": seed},
            }
            output = args.output / f"member_{seed}"
            if check_output(output, member_identity, args.resume):
                continue
            member_inputs, member_cfg = inputs, cfg
            if args.source == "statistical":
                member_inputs = statistical_inputs(inputs, seed=seed, mode=args.mode)
            else:
                member_cfg = training_config(cfg, seed)
            arrays = calculate(member_inputs, meta, member_cfg)
            save_result(
                output,
                arrays,
                {
                    "identity": member_identity,
                    "resolved_member_config": member_cfg,
                    "output_contract": meta["output_contract"],
                    "normalization_values": meta["normalization_values"],
                },
            )
        return
    members, bindings = [], {}
    for seed in args.seeds:
        arrays, record = load_result(args.input / f"member_{seed}")
        expected = {
            **nominal_identity,
            "operation": "member",
            "nominal": fingerprint(nominal_record),
            "perturbation": {**perturbation, "seed": seed},
        }
        if (
            record["identity"] != expected
            or record["output_contract"] != nominal_record["output_contract"]
        ):
            raise ValueError(
                f"member {seed}: nominal, perturbation, code or support mismatch"
            )
        members.append(arrays)
        bindings[str(seed)] = fingerprint(record)
    identity = {
        "operation": "combine",
        "nominal": fingerprint(nominal_record),
        "members": bindings,
        "perturbation": perturbation,
        "config": cfg,
        "code": code_identity(),
    }
    if check_output(args.output, identity, args.resume):
        return
    save_result(
        args.output,
        assemble(nominal_arrays, members),
        {
            "identity": identity,
            "output_contract": nominal_record["output_contract"],
            "covariance_contract": {
                "source": args.source,
                "centering": "ensemble-mean",
                "divisor": "N-1",
                "ensemble_size": len(members),
                "mean_shift": "reported separately",
                "combination": "single source only",
            },
        },
    )


def _project(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    from .projection import project

    arrays, record = load_result(args.input)
    identity = {
        "operation": "project",
        "config": cfg,
        "input_record": fingerprint(record),
        "code": code_identity(),
    }
    if check_output(args.output, identity, args.resume):
        return
    projected, contract = project(arrays, record["output_contract"], cfg["keep_axes"])
    metadata = {
        "identity": identity,
        "output_contract": contract,
        "source_contract": record["output_contract"],
    }
    if "covariance_contract" in record:
        metadata["covariance_contract"] = record["covariance_contract"]
    save_result(args.output, projected, metadata)


def main(operation: str, argv: list[str] | None = None) -> int:
    """Execute one public operation; report prerequisite failures as CLI errors."""
    ap = parser(operation)
    args = ap.parse_args(argv)
    try:
        cfg = read_json(args.config)
        args.output = args.output.expanduser().resolve()
        if args.input is not None:
            args.input = args.input.expanduser().resolve()
        if operation == "prepare_events":
            from .preparation import root_plan, synthetic

            if cfg.get("mode") == "root-plan":
                if args.input is None:
                    raise ValueError("root-plan requires --input playlist inventory")
                print(json.dumps(root_plan(cfg, args.input, args.output), indent=2))
            elif cfg.get("mode") == "synthetic":
                if args.input is not None:
                    raise ValueError(
                        "synthetic preparation generates events; omit --input"
                    )
                if args.plan:
                    print(
                        json.dumps(
                            {
                                "status": "plan-only",
                                "resolved_config": cfg,
                                "output": str(args.output),
                            }
                        )
                    )
                else:
                    synthetic(args.output, cfg)
            else:
                raise ValueError("prepare_events mode must be synthetic or root-plan")
            return 0
        if operation == "unfold_pet":
            from .pet import plan, run

            if args.input is None:
                raise ValueError("PET requires --input")
            resolved = plan(cfg, args.input, args.output)
            if args.plan:
                print(json.dumps(resolved, indent=2))
            else:
                run(resolved, args.output)
            return 0
        if operation == "project":
            if (
                set(cfg) != {"keep_axes"}
                or not isinstance(cfg["keep_axes"], list)
                or not cfg["keep_axes"]
            ):
                raise ValueError(
                    "projection config requires only a nonempty keep_axes list; normalized shape projection is unsupported"
                )
        else:
            from .scalar import resolve_config

            cfg = resolve_config(cfg)
        if operation == "uncertainties":
            from .uncertainty import require_systematic_path, training_config

            if len(set(args.seeds)) != len(args.seeds) or min(args.seeds) < 0:
                raise ValueError("seeds must be distinct nonnegative integers")
            if args.source == "statistical" and args.mode is None:
                raise ValueError(
                    "statistical source requires explicit --mode data-only or data-plus-mc"
                )
            if args.source != "statistical" and args.mode is not None:
                raise ValueError("--mode applies only to statistical perturbations")
            if args.source == "systematic":
                require_systematic_path()
            if args.source == "ml":
                training_config(cfg, args.seeds[0])
            if args.action == "combine" and len(args.seeds) < 2:
                raise ValueError("combination requires at least two declared seeds")
        if args.plan:
            if args.input is None:
                raise ValueError("operation requires --input")
            print(
                json.dumps(
                    {
                        "status": "plan-only",
                        "operation": operation,
                        "resolved_config": cfg,
                        "input": str(args.input),
                        "input_exists": args.input.exists(),
                        "output": str(args.output),
                        "requirements": "Execution validates arrays, alignment, normalization and supported backend dependencies.",
                    },
                    indent=2,
                )
            )
            return 0
        # The same import-origin guard protects local smoke and future compute.
        if operation in {"unfold_gbdt", "closure"} or (
            operation == "uncertainties" and args.action == "run"
        ):
            from joblib import cpu_count  # type: ignore[import-untyped]

            # Numerical packages perform read-only hardware discovery on first
            # import (including NumPy 1.x's lscpu probe). Fitting remains guarded.
            import_module("lightgbm")
            cpu_count(only_physical_cores=True)
        code_identity()
        legacy_module("mnv_guarded_run").install(str(ROOT))
        if operation in {"unfold_gbdt", "closure"}:
            _unfold(args, cfg, operation)
        elif operation == "uncertainties":
            _uncertainties(args, cfg)
        else:
            _project(args, cfg)
        print(
            f"{operation}: complete -> {args.output} (software execution; no scientific adoption)"
        )
        return 0
    except (
        ValueError,
        KeyError,
        OSError,
        ImportError,
        subprocess.CalledProcessError,
    ) as exc:
        ap.error(str(exc))
    return 2
