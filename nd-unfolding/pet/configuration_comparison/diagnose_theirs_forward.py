"""Where does his arm become non-finite: at initialisation, or during training?

Three targeted repairs -- the feature conversion, the coordinate scaling and
the dE/dx sentinel -- were each a real defect and none of them cleared
`Last val loss nan`. Guessing a fourth is worse than measuring, and the
measurement that splits the space is cheap:

  * if the FORWARD is already non-finite on the real inputs at step 0, the
    problem is the inputs or the architecture;
  * if the forward is finite and the loss goes to nan over a few optimizer
    steps, the problem is the optimization -- learning rate, warmup, batch --
    and no amount of further input archaeology will find it.

Reports the first non-finite intermediate when there is one, and the per-step
loss when there is not.

NOT CITABLE FOR any performance claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--batch", type=int, default=512)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import sys
    for extra in (args.repo / "nd-unfolding" / "pet",
                  args.repo / "nd-unfolding" / "pet" / "configuration_comparison",
                  args.repo / "omnifold_nn"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    from keras_backend import configure_production_precision
    configure_production_precision(strict=True)

    import tensorflow as tf
    import frozen_design as fd
    import theirs_omnifold_arm as toa

    blob = np.load(args.cache, mmap_mode="r")
    packed = np.asarray(blob["prior_packed"][: args.batch], dtype=np.float32)
    globals_ = np.asarray(blob["prior_globals"][: args.batch], dtype=np.float32)

    report: dict[str, Any] = {
        "batch": int(packed.shape[0]),
        "inputs": {
            "packed_finite": bool(np.isfinite(packed).all()),
            "globals_finite": bool(np.isfinite(globals_).all()),
            "packed_absmax": float(np.abs(packed).max()),
            "globals_absmax": float(np.abs(globals_).max()),
            "all_zero_rows": int((np.abs(packed).sum(axis=(1, 2)) == 0).sum()),
        },
    }

    model = toa.TheirsCompleteArm(num_part=fd.THEIRS_COMPLETE["token_cap"])
    x = [tf.constant(packed), tf.constant(globals_)]
    out = model(x, training=False)
    out = np.asarray(out)
    report["forward_at_init"] = {
        "finite": bool(np.isfinite(out).all()),
        "non_finite": int((~np.isfinite(out)).sum()),
        "absmax": float(np.abs(out[np.isfinite(out)]).max()) if np.isfinite(out).any() else None,
        "reading": ("non-finite HERE means the inputs or the architecture; "
                    "finite here and nan later means the optimization"),
    }

    # A real training loop at the campaign's learning rate, loss per step.
    labels = np.zeros((packed.shape[0], 1), np.float32)
    labels[::2] = 1.0
    weights = np.ones((packed.shape[0],), np.float32)
    model.compile(optimizer=tf.keras.optimizers.Adam(args.learning_rate),
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True))
    losses = []
    first_bad = None
    for step in range(args.steps):
        history = model.fit(x, labels, sample_weight=weights, epochs=1,
                            batch_size=min(256, packed.shape[0]), verbose=0)
        loss = float(history.history["loss"][0])
        losses.append(loss)
        if not np.isfinite(loss) and first_bad is None:
            first_bad = step
            break
    report["training"] = {
        "learning_rate": args.learning_rate,
        "losses": losses,
        "first_non_finite_step": first_bad,
        "diverged": first_bad is not None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
