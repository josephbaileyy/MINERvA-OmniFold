"""Measure key-bias invariance on preserved diagnostic weights, on CPU only."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
from typing import Any

import numpy as np

import compatibility_preflight as preflight
import run_typed_token_comparison as runner
import typed_descriptor_keras as adapter
import typed_token_comparison as candidate
from optimizer_diagnostic import metrics


def main() -> None:
    """Compare saved trained predictions after changing only attention key bias."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    tf = adapter.require_tensorflow()
    tf.config.set_visible_devices([], "GPU")
    runner.configure_precision()
    tf.config.threading.set_intra_op_parallelism_threads(7)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    norm, _ = preflight.fixtures()
    rows = []
    with tarfile.open(args.archive) as archive:

        def read_arrays(name: str) -> dict[str, Any]:
            stream = archive.extractfile("capture/" + name)
            assert stream is not None
            with np.load(io.BytesIO(stream.read()), allow_pickle=False) as source:
                return dict(source)

        for case in preflight.CASES:
            inputs = read_arrays(f"{case}.npz")
            for route in ("pooled", "direct"):
                stem = f"{case}-{route}"
                metadata_stream = archive.extractfile(
                    f"capture/{stem}/cpu/variables.json"
                )
                assert metadata_stream is not None
                metadata = json.load(metadata_stream)["weights"]
                indices = [
                    i for i, v in enumerate(metadata) if v["path"].endswith("/key/bias")
                ]
                if len(indices) != 1:
                    raise AssertionError("One attention key bias is required")
                index = indices[0]
                model = candidate.build_comparison(norm, routing=route)
                model(inputs)
                for origin in ("cpu", "candidate"):
                    state = read_arrays(f"{stem}/{origin}/state-2.npz")
                    weights = [state[f"weight_{i}"] for i in range(len(metadata))]
                    model.set_weights(weights)
                    baseline = np.asarray(model(inputs)).copy()
                    for label, bias in (
                        ("zero", np.zeros_like(weights[index])),
                        ("constant_0.125", np.full_like(weights[index], 0.125)),
                    ):
                        changed = [value.copy() for value in weights]
                        changed[index] = bias
                        model.set_weights(changed)
                        prediction = np.asarray(model(inputs)).copy()
                        rows.append(
                            {
                                "case": case,
                                "routing": route,
                                "weight_origin": origin,
                                "replacement": label,
                                "prediction": metrics(baseline, prediction),
                            }
                        )
    args.output.write_text(
        json.dumps(
            {
                "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                "device": "CPU",
                "precision": runner.precision_settings(),
                "rows": rows,
                "training_authorized": False,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
