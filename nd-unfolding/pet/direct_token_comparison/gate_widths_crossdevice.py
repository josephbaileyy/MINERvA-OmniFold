"""Cross-device gate coverage for the bucket widths the experiment would train at.

**Why this exists rather than a call into the frozen preflight.** The intent was to
re-run `amended_preflight.py` unchanged on new fixtures, so the gate would stay the
single bound implementation. That is not possible. Its fixtures are hardcoded, and
`compatibility_preflight.main()` re-executes *itself in a fresh process* for its
reload check, so an in-process substitution cannot reach the child: job 58470936
failed there with ``CalledProcessError`` on the ``--reload-only`` phase. Editing the
bound file would break the manifest bindings the finished campaign is verified
against, and a ``sitecustomize`` injection would make a bound gate run under an
invisible global patch. Neither is acceptable.

So the **numerics stay bound** and only the scaffolding is new. The comparison itself
is `optimizer_equivalence.validate`, the trajectories are
`optimizer_diagnostic.trace`/`replay`/`float64_adam`, the tolerances are
`compatibility_preflight.compare`, and the reference implementation is the one the
campaign designated. What is *not* reproduced is the bundle verification, the
serialization round-trip and the packing checks: this instrument answers one narrower
question -- does CPU/GPU agreement hold at a uniform width -- and says nothing about
the rest.

A re-implementation that only ever passes proves nothing, so two controls bracket it
and both must land:

* the **nominal** geometry, one photon, one blob, two prongs, must **PASS**, matching
  the verdict the frozen campaign recorded for it;
* the frozen **variable** geometry must **FAIL**, matching the recorded stress
  failure. If it passes here, this instrument is not exercising the gate and its
  verdicts are void.

The receipt records both controls, and ``controls_ok`` is false if either misbehaves.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

import numpy as np

FAMILIES = ("photons", "blobs", "prongs")
NOMINAL_WIDTH = (1, 1, 2)
WEIGHT_COUNT = 42


def _install(checkout: Path) -> None:
    """Put the checkout's modules first."""
    for root in (
        checkout / "nd-unfolding" / "pet" / "direct_token_comparison",
        checkout / "nd-unfolding" / "pet",
    ):
        if not root.is_dir():
            raise ValueError(f"Not a directory: {root}")
        sys.path.insert(0, str(root))


def uniform_width_inputs(modules: dict[str, Any], width: tuple[int, ...], rows: int) -> Any:
    """Build one uniform-width case with the experiment's own producer."""
    fourarm = modules["fourarm"]
    typed = modules["typed"]
    adapter = modules["adapter"]
    counts = np.tile(np.asarray(width, dtype=np.int64), (rows, 1))
    batch = fourarm.build_variable_typed_batch(typed, counts, seed=2401)
    event = np.zeros((rows, 13), dtype=np.float32)
    inputs = dict(adapter.prepare_keras_inputs(batch, event))
    inputs.update(
        generic_values=np.zeros((rows, 12, 5), dtype=np.float32),
        generic_mask=np.ones((rows, 12), dtype=bool),
    )
    return batch, inputs


def gate_case(
    modules: dict[str, Any],
    inputs: dict[str, Any],
    norm: Any,
    routing: str,
    folder: Path,
) -> dict[str, Any]:
    """Run the bound cross-device comparison for one case and one routing.

    Mirrors the order `amended_preflight` uses, because the order is part of the
    check: the oracle parity and token-inventory comparisons happen *before*
    ``validate``, and ``instrumentation_exact`` is what tells ``validate`` the
    instrumented trajectory equalled an uninstrumented one.
    """
    tf = modules["tf"]
    original = modules["original"]
    candidate = modules["candidate"]
    reference = modules["reference"]
    diagnostic = modules["diagnostic"]
    equivalence = modules["equivalence"]

    folder.mkdir(parents=True, exist_ok=True)
    tf.keras.utils.set_random_seed(2401)
    with tf.device("/CPU:0"):
        old = reference.build_comparison(norm, routing=routing)
        old(inputs)
        weights = old.get_weights()
    with tf.device("/GPU:0"):
        new = candidate.build_comparison(norm, routing=routing)
        new(inputs)
        new.set_weights(weights)

    traces = []
    for label, model, device in (("cpu", old, "/CPU:0"), ("candidate", new, "/GPU:0")):
        captured = diagnostic.trace(tf, model, inputs, device, folder / label)
        model.set_weights(weights)
        with tf.device(device):
            tokens = model.route_tokens(inputs)
        diagnostic.save_arrays(
            folder / f"{label}-tokens.npz",
            {f"token_{i}": value for i, value in enumerate(tokens)},
        )
        oracle = original.exercise(tf, model, inputs, device)
        for index, value in enumerate(oracle["weights"]):
            original.compare(value, captured["states"][2][f"weight_{index}"], exact=True)
        original.compare(oracle["prediction"], captured["prediction"], exact=True)
        captured["instrumentation_exact"] = True
        captured["device"] = oracle["device"]
        traces.append(captured)

    replays = []
    for label, captured in zip(("cpu", "candidate"), traces):
        gradients = [
            [captured[phase][f"gradient_{i}"] for i in range(WEIGHT_COUNT)]
            for phase in ("initial", "second")
        ]
        cpu = diagnostic.replay(
            tf, weights, gradients, "/CPU:0", folder / f"replay-{label}-cpu"
        )
        gpu = diagnostic.replay(
            tf, weights, gradients, "/GPU:0", folder / f"replay-{label}-candidate"
        )
        high = [
            {f"weight_{i}": value for i, value in enumerate(values)}
            for values in diagnostic.float64_adam(weights, gradients)
        ]
        replays.append(
            {
                "initial": {
                    f"weight_{i}": value for i, value in enumerate(weights)
                },
                "gradients": [
                    {f"gradient_{i}": value for i, value in enumerate(step)}
                    for step in gradients
                ],
                "cpu": cpu,
                "candidate": gpu,
                "float64": high,
            }
        )

    left, right = (
        {
            key: value
            for key, value in np.load(folder / f"{label}-tokens.npz").items()
        }
        for label in ("cpu", "candidate")
    )
    if left.keys() != right.keys():
        raise ValueError("Token inventory differs")
    for index, key in enumerate(left):
        original.compare(left[key], right[key], exact=index > 0)
    return equivalence.validate(new, traces, replays, exact_cpu=False)


def run_case(
    modules: dict[str, Any],
    label: str,
    inputs: dict[str, Any],
    norm: Any,
    workspace: Path,
) -> dict[str, Any]:
    """Gate both routings for one case, recording a verdict rather than raising."""
    record: dict[str, Any] = {"case": label, "routings": {}}
    for routing in ("pooled", "direct"):
        folder = workspace / f"{label}-{routing}"
        try:
            gate = gate_case(modules, inputs, norm, routing, folder)
            record["routings"][routing] = {
                "verdict": "PASS",
                "raw_bias_errors": [
                    float(value) for value in gate.get("raw_bias_errors", [])
                ]
                if isinstance(gate, dict)
                else [],
            }
        except (AssertionError, ValueError) as failure:
            record["routings"][routing] = {
                "verdict": "FAIL",
                "error": f"{type(failure).__name__}: {failure}",
            }
    record["verdict"] = (
        "PASS"
        if all(r["verdict"] == "PASS" for r in record["routings"].values())
        else "FAIL"
    )
    return record


def main() -> None:
    """Gate the nominal control, the variable control, then every width."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--widths", required=True, help="JSON list of width triples")
    parser.add_argument("--rows", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _install(args.checkout)
    import compatibility_preflight as original
    import four_arm_representation as fourarm
    import optimizer_diagnostic as diagnostic
    import optimizer_equivalence as equivalence
    import typed_descriptor_keras as adapter
    import typed_descriptors as typed
    import typed_token_comparison as candidate

    import run_typed_token_comparison as runner

    tf = adapter.require_tensorflow()
    policy = runner.configure_precision()
    devices = [device.name for device in tf.config.list_logical_devices("GPU")]
    if not devices:
        raise RuntimeError("No GPU is visible; this gate is a cross-device comparison")
    modules = {
        "tf": tf,
        "fourarm": fourarm,
        "typed": typed,
        "adapter": adapter,
        "runner": runner,
        "candidate": candidate,
        "original": original,
        "reference": original.original_module(),
        "diagnostic": diagnostic,
        "equivalence": equivalence,
    }

    widths = [tuple(int(v) for v in width) for width in json.loads(args.widths)]
    frozen_norm, frozen_cases = original.fixtures()

    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as scratch:
        workspace = Path(scratch)
        # Negative control first: if the nominal geometry does not reproduce the
        # campaign's recorded PASS, nothing below is worth reading.
        nominal = run_case(
            modules, "control-nominal", frozen_cases["nominal"], frozen_norm, workspace
        )
        records.append(nominal)
        print(f"control-nominal: {nominal['verdict']}", flush=True)
        # Positive control: the recorded stress failure must still fail here.
        variable = run_case(
            modules,
            "control-variable",
            frozen_cases["variable"],
            frozen_norm,
            workspace,
        )
        records.append(variable)
        print(f"control-variable: {variable['verdict']}", flush=True)

        for width in widths:
            batch, inputs = uniform_width_inputs(modules, width, args.rows)
            norm = typed.fit_frozen_normalization_for_smoke(
                batch,
                fit_inventory_row_selection_digest=runner.digest_arrays(
                    [np.zeros((args.rows, 2), dtype=np.float32)]
                ),
            )
            label = "w" + "-".join(str(value) for value in width)
            record = run_case(modules, label, inputs, norm, workspace)
            record["width"] = list(width)
            records.append(record)
            print(f"{label}: {record['verdict']}", flush=True)

    controls_ok = nominal["verdict"] == "PASS" and variable["verdict"] == "FAIL"
    by_width = {
        tuple(record["width"]): record["verdict"]
        for record in records
        if "width" in record
    }
    validated = sorted(w for w, verdict in by_width.items() if verdict == "PASS")
    failed = sorted(w for w, verdict in by_width.items() if verdict != "PASS")
    receipt = {
        "scope": (
            "cross-device agreement at uniform bucket widths. Bound numerics, new "
            "scaffolding, two controls. Not a substitute for the full preflight: no "
            "bundle verification, no serialization round-trip, no packing checks."
        ),
        "authorization": "A3, Joseph, 2026-09-18",
        "precision_policy": policy,
        "gpu_devices": devices,
        "controls": {
            "nominal_expected": "PASS",
            "nominal_measured": nominal["verdict"],
            "variable_expected": "FAIL",
            "variable_measured": variable["verdict"],
            "controls_ok": controls_ok,
        },
        "records": records,
        "validated_widths": [list(width) for width in validated],
        "failed_widths": [list(width) for width in failed],
        "gate_complete": controls_ok and bool(validated) and not failed,
        "non_claim": (
            "A validated width means CPU and GPU agreed there under the campaign's "
            "own tolerances. It is not a statement about closure, and if controls_ok "
            "is false every verdict here is void."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        f"controls_ok={controls_ok} validated={len(validated)} failed={len(failed)} "
        f"gate_complete={receipt['gate_complete']}"
    )


if __name__ == "__main__":
    main()
