"""Drive the real `MultiFold` loop with the ported backbone on both step schemas.

The port checks establish that the network is his. They say nothing about whether
it can be TRAINED by our estimator, and the two failure modes are different: a
shape that only appears when step 2's 8-column truth cloud meets a model built for
step 1's 5, an optimizer the engine silently replaces, a pad mask that is fine in a
forward pass and wrong once `pass_reco` gates the loss.

So this runs the vendored `MultiFold.Unfold()` itself -- not a stand-in -- for a
small number of iterations on synthetic arrays at the production schemas, with the
`OI-125` fold-forward recorder attached, and checks the things that would be
silently wrong rather than loudly broken:

* both steps built, trained and reweighted at their OWN widths (5/13 and 8/2);
* the optimizer the engine actually used is his, not the hardcoded Adam;
* push weights are finite, positive, and exactly 1 where `pass_gen` is False;
* an event with no tokens at all produces a finite logit;
* the fold-forward recorder produced an end-of-run row, which is the row the
  `RunStep1`-hooked instrumentation could never produce.

Synthetic only. No real source is read, nothing is adopted, and the loss values
here are not a result.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import keras_backend
import pet2_omnifold_adapter as adapter
from fold_forward_recorder import FoldForwardRecorder
from torch_adamw import TorchAdamW

keras_backend.select_keras_backend()

import tensorflow as tf  # noqa: E402


def load_multifold(repo: Path) -> Any:
    root = repo / "omnifold_nn"
    if not root.is_dir():
        raise SystemExit(f"[exercise] no omnifold_nn under {repo}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from omnifold import MultiFold

    return MultiFold


def run(repo: Path, rows: int, niter: int, epochs: int, num_part: int,
        size: str) -> dict[str, Any]:
    multifold_class = load_multifold(repo)
    ported_class = adapter.make_ported_multifold(multifold_class)
    mc, data = adapter.synthetic_loaders(rows, num_part=num_part)

    model_reco = adapter.build_step_model("step1_reco", num_part=num_part, size=size)
    model_gen = adapter.build_step_model("step2_gen", num_part=num_part, size=size)

    with tempfile.TemporaryDirectory() as scratch:
        unfolder = ported_class(
            name="ported_exercise", model_reco=model_reco, model_gen=model_gen,
            data=data, mc=mc, weights_folder=scratch, log_folder=scratch,
            niter=niter, batch_size=32, epochs=epochs, lr=1e-4, early_stop=epochs,
            verbose=False,
        )
        # Confirm the override is live BEFORE running, so a silent fallback to the
        # engine's Adam cannot be discovered only by reading loss curves later.
        probe = unfolder.get_optimizer(10, fixed=False)
        optimizer_is_his = isinstance(probe, TorchAdamW)

        recorder = FoldForwardRecorder(unfolder, mc.weight_reco, mc.pass_reco,
                                       label="ported-exercise")
        with recorder:
            unfolder.Unfold()
        push = np.asarray(unfolder.weights_push, dtype=np.float64)

    # Step-wise evidence that each model really saw its own schema.
    reco_logits = model_reco([tf.constant(mc.reco), tf.constant(mc.reco_evt)],
                             training=False).numpy()
    gen_logits = model_gen([tf.constant(mc.gen), tf.constant(mc.gen_evt)],
                           training=False).numpy()

    empty_event = int(np.argmin(np.abs(mc.reco).max(axis=(1, 2))))
    checks = {
        "E1_both_steps_built_at_own_width": {
            "held": bool(model_reco.num_feat == 5 and model_reco.num_evt == 13
                         and model_gen.num_feat == 8 and model_gen.num_evt == 2),
            "step1": {"num_feat": model_reco.num_feat, "num_evt": model_reco.num_evt,
                      "coord_idx": list(model_reco.coord_idx)},
            "step2": {"num_feat": model_gen.num_feat, "num_evt": model_gen.num_evt,
                      "coord_idx": list(model_gen.coord_idx)},
        },
        "E2_engine_used_his_optimizer": {
            "held": optimizer_is_his,
            "optimizer": type(probe).__name__,
            "note": ("MultiFold.get_optimizer hardcodes tf.keras.optimizers.Adam; "
                     "without the subclass his architecture would train under our "
                     "optimizer and the arm would not be his configuration"),
        },
        "E3_push_weights_sane": {
            "held": bool(np.isfinite(push).all() and (push > 0).all()
                         and np.allclose(push[~mc.pass_gen], 1.0)),
            "finite": bool(np.isfinite(push).all()),
            "all_positive": bool((push > 0).all()),
            "min": float(push.min()), "max": float(push.max()),
            "mean": float(push.mean()),
            "rows_not_pass_gen": int((~mc.pass_gen).sum()),
        },
        "E4_empty_event_finite": {
            "held": bool(np.isfinite(reco_logits[empty_event]).all()),
            "row": empty_event,
            "tokens_in_row": int((np.abs(mc.reco[empty_event]).max(axis=-1) != 0).sum()),
            "logit": float(reco_logits[empty_event][0]),
            "note": ("a real production state: an event with no recoil tokens. The "
                     "upstream's -1e9 additive mask keeps this finite where -inf "
                     "would give NaN"),
        },
        "E5_fold_forward_end_of_run_recorded": {
            "held": bool(recorder.summary()["end_of_run_is_recorded_not_reconstructed"]),
            **recorder.summary(),
        },
        "E6_logits_finite_both_steps": {
            "held": bool(np.isfinite(reco_logits).all() and np.isfinite(gen_logits).all()),
            "reco_logit_range": [float(reco_logits.min()), float(reco_logits.max())],
            "gen_logit_range": [float(gen_logits.min()), float(gen_logits.max())],
        },
    }
    return {
        "scope": ("exercises the vendored MultiFold loop with the ported PET2 on both "
                  "step schemas, on SYNTHETIC arrays. No result, no adoption."),
        "rows": rows, "niter": niter, "epochs": epochs, "num_part": num_part,
        "size": size,
        "schemas": adapter.STEP_SCHEMAS,
        "pad_column": adapter.PAD_COLUMN,
        "backend": keras_backend.select_keras_backend(),
        "versions": keras_backend.record_versions(),
        "checks": checks,
        "all_held": all(v["held"] for v in checks.values()),
        "not_implemented": [
            "his cosine schedule over max_steps: max_steps must be derived from the "
            "agreed fair budget (proposal §7.3), which is not ratified",
            "gradient clipping, if his recipe uses it, is not yet transcribed",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=512)
    parser.add_argument("--niter", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--num-part", type=int, default=12)
    parser.add_argument("--size", default="small")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    receipt = run(args.repo, args.rows, args.niter, args.epochs, args.num_part, args.size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    for name, value in receipt["checks"].items():
        print(f"{name}: {'PASS' if value['held'] else 'FAIL'}")
    print(f"all_held: {receipt['all_held']}")
    if not receipt["all_held"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
