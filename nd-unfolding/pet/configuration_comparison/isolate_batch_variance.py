"""Which operation makes the compiled graph disagree with itself across batch sizes?

The measured fact: the same XLA program, TF32 demonstrably off, gives different
answers at batch 2048 and batch 256 on the SAME rows -- median 2.37e-3 per row,
100% of rows -- while the same comparison on CPU gives exactly 0.0.

Two hypotheses were tested and REJECTED. k-NN tie resolution: the row profile
shows every row moving, not the handful a tie flip would move. TF32:
`NVIDIA_TF32_OVERRIDE=0` changed the deviation by nothing, to the digit.

This isolates the remaining candidates one operation at a time, each compiled
alone, each run at both batch sizes on the same input rows. An operation that is
batch-invariant in isolation is not the cause; one that is not, is a candidate.

The leading candidate is NOT a transcendental. A matmul's accumulation order
depends on how the kernel tiles the M dimension, and M is the batch -- so a
different batch can select a different kernel and sum the same products in a
different order. `erf` and `tanh` are elementwise: a batch-dependent result from
one of those would be far more surprising, which is exactly why they are worth
including rather than assuming.

CONTROLS both ways. An elementwise add must come back exactly 0.0, or the
harness is measuring something other than the operation. A deliberately
order-sensitive reduction must come back non-zero, or the harness cannot see the
effect it is looking for.

NOT CITABLE FOR any claim about the production model. It measures primitives.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from typing import Any

PRODUCTION_BATCH = 2048
REFERENCE_BATCH = 256
TOKENS = 33
WIDTH = 32


def _cases(tf: Any) -> dict[str, Any]:
    """Each case maps one input tensor to one output. Compiled one at a time."""
    rng = tf.random.Generator.from_seed(20260920)

    w = tf.Variable(rng.normal([WIDTH, WIDTH]), trainable=False)
    w2 = tf.Variable(rng.normal([WIDTH, WIDTH]), trainable=False)

    def add(x):
        return x + 1.0

    def mul(x):
        return x * 1.0000001

    def erf(x):
        return tf.math.erf(x)

    def gelu(x):
        return 0.5 * x * (1.0 + tf.math.erf(x / tf.sqrt(2.0)))

    def tanh_(x):
        return tf.tanh(x)

    def matmul(x):
        return tf.matmul(x, w)

    def matmul_deep(x):
        for _ in range(8):
            x = tf.matmul(x, w)
            x = x * 0.1
        return x

    def einsum(x):
        return tf.einsum("...i,oi->...o", x, w)

    def reduce_feature(x):
        return tf.reduce_sum(x, axis=-1, keepdims=True) + x

    def reduce_token(x):
        return tf.reduce_mean(x, axis=1, keepdims=True) + x

    def layernorm(x):
        mean = tf.reduce_mean(x, axis=-1, keepdims=True)
        var = tf.reduce_mean(tf.square(x - mean), axis=-1, keepdims=True)
        return (x - mean) * tf.math.rsqrt(var + 1e-6)

    def softmax(x):
        scores = tf.matmul(x, x, transpose_b=True) / tf.sqrt(float(WIDTH))
        return tf.matmul(tf.nn.softmax(scores, axis=-1), x)

    def sdpa(x):
        q = tf.matmul(x, w)
        k = tf.matmul(x, w2)
        scores = tf.matmul(q, k, transpose_b=True) / tf.sqrt(float(WIDTH))
        return tf.matmul(tf.nn.softmax(scores, axis=-1), x)

    def reduce_over_batch(x):
        """NEGATIVE CONTROL, expected to MOVE.

        A reduction over the batch axis genuinely depends on the batch: at 2048
        it sums 2048 rows and at 256 it sums 256. If this comes back 0.0 the
        harness is not comparing what it claims to.
        """
        return x + tf.reduce_mean(x, axis=0, keepdims=True)

    return {
        "add_control": add,
        "mul_control": mul,
        "erf": erf,
        "gelu": gelu,
        "tanh": tanh_,
        "matmul": matmul,
        "matmul_deep_8": matmul_deep,
        "einsum": einsum,
        "reduce_feature": reduce_feature,
        "reduce_token": reduce_token,
        "layernorm": layernorm,
        "softmax_selfattn": softmax,
        "sdpa": sdpa,
        "reduce_over_batch_NEGATIVE_CONTROL": reduce_over_batch,
    }


def measure(tf: Any, np: Any, name: str, fn: Any, x: Any) -> dict[str, Any]:
    compiled = tf.function(fn, jit_compile=True)
    big = compiled(x).numpy()
    small = compiled(x[:REFERENCE_BATCH]).numpy()
    diff = np.abs(big[:REFERENCE_BATCH] - small)
    scale = np.maximum(np.abs(big[:REFERENCE_BATCH]), 1e-30)
    per_row = diff.reshape(REFERENCE_BATCH, -1).max(axis=1)
    return {
        "op": name,
        "max_abs": float(diff.max()),
        "median_row_max_abs": float(np.median(per_row)),
        "rows_moved_fraction": float((per_row > 0).mean()),
        "max_rel": float((diff / scale).max()),
        "batch_invariant": bool(diff.max() == 0.0),
    }


def precision_witness(tf: Any, np: Any) -> dict[str, Any]:
    """Is the compiled matmul ACTUALLY float32, or TF32 wearing a float32 flag?

    "`NVIDIA_TF32_OVERRIDE=0` changed the deviation by nothing" is consistent
    with two different worlds: the override worked and TF32 was never the cause,
    or the override did not reach the compiled path at all. Neither is
    distinguished by comparing the path to itself.

    This compares it to the ANSWER. A float64 reference gives the true product;
    a genuine float32 matmul lands within about 1e-7 relative, and TF32 -- ten
    mantissa bits -- lands near 1e-3. The number says which arithmetic ran,
    without needing the flag to be honest.
    """
    rng = np.random.default_rng(11)
    a = rng.standard_normal((512, 512))
    b = rng.standard_normal((512, 512))
    exact = a @ b                                     # float64, on the host

    @tf.function(jit_compile=True)
    def compiled(x, y):
        return tf.matmul(x, y)

    got = compiled(tf.constant(a, tf.float32),
                   tf.constant(b, tf.float32)).numpy().astype(np.float64)

    # Normalised by the RMS of the exact product, NOT elementwise. An entrywise
    # relative error is meaningless wherever cancellation makes the true value
    # near zero -- the first version of this reported a max relative error of
    # 1.6 for a correct float32 matmul and labelled it TF32. The RMS-normalised
    # error is the quantity the error model actually predicts.
    k = a.shape[1]
    rms = float(np.sqrt(np.mean(exact ** 2)))
    normalised = float(np.max(np.abs(got - exact)) / rms)
    predicted_fp32 = np.sqrt(k) * np.finfo(np.float32).eps
    predicted_tf32 = np.sqrt(k) * 2.0 ** -11      # TF32 keeps 10 mantissa bits
    threshold = float(np.sqrt(predicted_fp32 * predicted_tf32))   # geometric mean
    return {
        "k": int(k),
        "error_over_rms": normalised,
        "predicted_if_float32": float(predicted_fp32),
        "predicted_if_tf32": float(predicted_tf32),
        "threshold": threshold,
        "verdict": ("looks like TF32" if normalised > threshold
                    else "looks like true float32"),
        "reference": "float64 host matmul",
        "reading": ("this compares the compiled path to the ANSWER, not to "
                    "itself, so it does not depend on any precision flag being "
                    "honest about what it set. The threshold is the geometric "
                    "mean of the two predicted error scales, fixed by the error "
                    "model rather than by the measurement"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()

    import sys
    for extra in (args.repo / "nd-unfolding" / "pet",
                  args.repo / "nd-unfolding" / "pet" / "configuration_comparison"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))

    from keras_backend import configure_production_precision, observed_precision_policy
    precision = configure_production_precision(strict=True)

    import numpy as np
    import tensorflow as tf

    gpus = tf.config.list_physical_devices("GPU")
    rng = tf.random.Generator.from_seed(7)
    x = rng.normal([PRODUCTION_BATCH, TOKENS, WIDTH])

    rows = [measure(tf, np, name, fn, x) for name, fn in _cases(tf).items()]
    witness = precision_witness(tf, np)

    controls = {r["op"]: r for r in rows}
    harness_ok = (
        controls["add_control"]["batch_invariant"]
        and controls["mul_control"]["batch_invariant"]
        and not controls["reduce_over_batch_NEGATIVE_CONTROL"]["batch_invariant"]
    )
    culprits = [r["op"] for r in rows
                if not r["batch_invariant"]
                and not r["op"].endswith("NEGATIVE_CONTROL")]

    report = {
        "scope": ("which primitive is not batch-invariant under XLA on this GPU. "
                  "Measures primitives; says nothing about the production model"),
        "production_batch": PRODUCTION_BATCH,
        "reference_batch": REFERENCE_BATCH,
        "precision": precision,
        "observed_precision": observed_precision_policy(),
        "gpu": [d.name for d in gpus],
        "gpu_details": [tf.config.experimental.get_device_details(d)
                        for d in gpus],
        "platform": platform.platform(),
        "tensorflow": tf.__version__,
        "rows": rows,
        "precision_witness": witness,
        "nvidia_tf32_override": __import__("os").environ.get(
            "NVIDIA_TF32_OVERRIDE", "<unset>"),
        "harness_controls_held": harness_ok,
        "harness_reading": (
            "an elementwise add and multiply must be exactly batch-invariant or "
            "the harness is measuring something other than the operation; the "
            "batch-axis reduction must MOVE or the harness cannot see the effect"
        ),
        "not_batch_invariant": culprits,
        "rejected_hypotheses": {
            "knn_ties": "the row profile shows every row moving, not a handful",
            "tf32": "NVIDIA_TF32_OVERRIDE=0 changed the deviation by nothing",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str))
    print(f"[isolate] controls held: {harness_ok}")
    for r in rows:
        flag = "OK " if r["batch_invariant"] else "MOVES"
        print(f"  {flag} {r['op']:<36} max={r['max_abs']:.3e} "
              f"med_row={r['median_row_max_abs']:.3e} "
              f"rows={100*r['rows_moved_fraction']:.1f}%")
    print(f"[isolate] precision witness: {witness['verdict']} "
          f"(err/rms {witness['error_over_rms']:.2e}, fp32 would be "
          f"{witness['predicted_if_float32']:.1e}, tf32 "
          f"{witness['predicted_if_tf32']:.1e})")
    print(f"[isolate] not batch-invariant: {culprits}")
    return 0 if harness_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
